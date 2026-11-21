using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1359: four session-shaped operations whose handlers name no host, so the origin is the caller's. The declared
/// sets are the documents' own — three of them take no variables at all.
/// </summary>
public sealed class StoreSessionQueriesTests
{
    [Fact]
    public void TheFourDocumentsAreTheMeasuredOnes()
    {
        Assert.Equal(197, StoreSessionQueries.GetCustomerInformationDocument.Length);
        Assert.StartsWith("query getCustomerInformation {", StoreSessionQueries.GetCustomerInformationDocument);
        Assert.Equal(3067, StoreSessionQueries.GetPaymentdMethodsDocument.Length);
        Assert.Equal(67, StoreSessionQueries.ItemDocument.Length);
        Assert.Equal(3234, StoreSessionQueries.GetCartDocument.Length);
        Assert.StartsWith("query getCart", StoreSessionQueries.GetCartDocument);
    }

    /// <summary>getPaymentdMethods keeps the image's own spelling of "methods".</summary>
    [Fact]
    public void TheOperationNameKeepsItsMisspelling()
    {
        Assert.NotNull(StoreSessionQueries.DocumentFor("getPaymentdMethods"));
        Assert.StartsWith("query getPaymentdMethods", StoreSessionQueries.GetPaymentdMethodsDocument);
    }

    [Fact]
    public void ThreeOfTheFourDeclareNoVariables()
    {
        Assert.Empty(StoreSessionQueries.Declared["getCustomerInformation"]);
        Assert.Empty(StoreSessionQueries.Declared["getPaymentdMethods"]);
        Assert.Empty(StoreSessionQueries.Declared["item"]);
        Assert.Equal(new[] { "key", "locale" }, StoreSessionQueries.Declared["getCart"]);
    }

    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, null, "getCart", new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>A variable the document does not declare is refused before the request.</summary>
    [Fact]
    public async Task AnUndeclaredVariableIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl, "getCustomerInformation", new JObject { ["key"] = "x" }, default);

        Assert.Null(data);
        Assert.Contains("does not declare $key", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheQueryPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"me\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl, "getCustomerInformation", new JObject(), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("getCustomerInformation", sent["operationName"]!.ToObject<string>());
        Assert.Equal(StoreSessionQueries.GetCustomerInformationDocument, sent["query"]!.ToObject<string>());
    }

    /// <summary>
    /// R1362: addToCartByChannel belongs here because its handler carries key/locale like getCart and no host.
    /// Its document declares five variables — the sender named a couple more fields than the document takes.
    /// </summary>
    [Fact]
    public void TheChannelAddJoinsTheSameFamily()
    {
        Assert.Equal(2271, StoreSessionQueries.AddToCartByChannelDocument.Length);
        Assert.StartsWith("mutation addToCartByChannel", StoreSessionQueries.AddToCartByChannelDocument);
        Assert.Equal(new[] { "cartId", "locale", "productId", "quantity", "version" },
            StoreSessionQueries.Declared["addToCartByChannel"]);
        Assert.Same(StoreSessionQueries.AddToCartByChannelDocument,
            StoreSessionQueries.DocumentFor("addToCartByChannel"));
    }

    [Fact]
    public async Task TheChannelAddPostsToTheFamilyOrigin()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"addToCartByChannel\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl, "addToCartByChannel",
            new JObject { ["cartId"] = "c-1", ["productId"] = "p-1", ["quantity"] = 1 }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.AddToCartByChannelDocument, sent["query"]!.ToObject<string>());
    }
}
