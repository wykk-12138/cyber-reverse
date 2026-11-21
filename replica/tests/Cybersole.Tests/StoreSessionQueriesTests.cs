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

    /// <summary>
    /// R1363: UpdateContactDetails' one handler builds https:// + host + /graphql, so it takes the caller's origin
    /// like the rest of this family. Its other handler sends the same operation by hash; which a run picks is not
    /// established, so only this one is wired.
    /// </summary>
    [Fact]
    public void TheContactDetailsJoinTheSameFamily()
    {
        Assert.Equal(244, StoreSessionQueries.UpdateContactDetailsDocument.Length);
        Assert.StartsWith("mutation UpdateContactDetails", StoreSessionQueries.UpdateContactDetailsDocument);
        Assert.Equal(new[] { "email", "emailOptIn", "phone" },
            StoreSessionQueries.Declared["UpdateContactDetails"]);
        Assert.Same(StoreSessionQueries.UpdateContactDetailsDocument,
            StoreSessionQueries.DocumentFor("UpdateContactDetails"));
    }

    [Fact]
    public async Task TheContactDetailsPostTheirThreeVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"updateContactDetails\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "UpdateContactDetails",
            new JObject { ["email"] = "a@b.test", ["emailOptIn"] = false, ["phone"] = "010" }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.UpdateContactDetailsDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("a@b.test", sent["variables"]!["email"]!.ToObject<string>());
    }

    /// <summary>
    /// R1366: saveAddress belongs here — four declared variables, no host, and the image's own async tail names a
    /// SaveAddress step, which is what makes it a store step rather than a helper.
    /// </summary>
    [Fact]
    public void TheAddressSaveJoinsTheSameFamily()
    {
        Assert.Equal(296, StoreSessionQueries.SaveAddressDocument.Length);
        Assert.StartsWith("mutation saveAddress(", StoreSessionQueries.SaveAddressDocument);
        Assert.Equal(new[] { "address", "editAddress", "saveAddress", "setDefault" },
            StoreSessionQueries.Declared["saveAddress"]);
        Assert.Same(StoreSessionQueries.SaveAddressDocument, StoreSessionQueries.DocumentFor("saveAddress"));
    }

    [Fact]
    public async Task TheAddressSavePostsItsFourVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"saveAddress\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "saveAddress",
            new JObject
            {
                ["address"] = new JObject { ["city"] = "Seoul" },
                ["editAddress"] = false,
                ["saveAddress"] = true,
                ["setDefault"] = false,
            }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.SaveAddressDocument, sent["query"]!.ToObject<string>());
    }

    /// <summary>
    /// R1367: the rest of the host-less group, landed the way R1359 landed four of them — envelope-only handlers,
    /// same block, origin from the caller. createMyPayment is deliberately absent: R1364 showed it belongs with the
    /// Cybersource family.
    /// </summary>
    [Fact]
    public void TheThreeHostLessOperationsJoined()
    {
        Assert.Equal(421, StoreSessionQueries.CreateCartByStoreDocument.Length);
        Assert.Equal(251, StoreSessionQueries.InitiateCheckoutDocument.Length);
        Assert.Equal(223, StoreSessionQueries.MaintainShippingGroupsDocument.Length);

        Assert.Equal(new[] { "country", "currency", "locale", "storeKey", "taxMode" },
            StoreSessionQueries.Declared["createCartByStore"]);
        Assert.Empty(StoreSessionQueries.Declared["initiateCheckout"]);
        Assert.Equal(new[] { "cartId" }, StoreSessionQueries.Declared["maintainShippingGroups"]);

        foreach (var name in new[] { "createCartByStore", "initiateCheckout", "maintainShippingGroups" })
            Assert.NotNull(StoreSessionQueries.DocumentFor(name));
    }

    /// <summary>createMyPayment stays out of this family, on R1364's evidence.</summary>
    [Fact]
    public void ThePaymentCreationIsNotInTheSessionFamily()
    {
        Assert.Null(StoreSessionQueries.DocumentFor("createMyPayment"));
    }

    [Fact]
    public async Task TheCheckoutInitiationPostsItsEmptyVariableSet()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"initiateCheckout\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "initiateCheckout", new JObject(), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.InitiateCheckoutDocument, sent["query"]!.ToObject<string>());
    }
}
