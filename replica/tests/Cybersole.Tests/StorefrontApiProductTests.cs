using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1345: the Product query of the family that posts a relative api/graphql — five senders, no host anywhere, so
/// the origin is the caller's. These pin the document, the variables and the refusal.
/// </summary>
public sealed class StorefrontApiQueriesTests
{
    [Fact]
    public void TheOperationAndPathAreTheObservedOnes()
    {
        Assert.Equal("Product", "Product");
        Assert.Equal("api/graphql", StorefrontApiQueries.Path);
        Assert.DoesNotContain("://", StorefrontApiQueries.Path);
    }

    [Fact]
    public void TheDocumentIsTheWholeStringAndDeclaresFourVariables()
    {
        Assert.Equal(10620, StorefrontApiQueries.Product.Length);
        Assert.StartsWith("query Product($id: ID!", StorefrontApiQueries.Product);
        Assert.Equal(new[] { "id", "isDraft", "variationId", "src" }, StorefrontApiQueries.Declared["Product"]);
        Assert.Equal(new[] { "id", "variationId" }, StorefrontApiQueries.SenderFills["Product"]);
        foreach (var name in StorefrontApiQueries.Declared["Product"])
            Assert.Contains("$" + name, StorefrontApiQueries.Product);
    }

    /// <summary>A relative path with no origin would be a request to nowhere, so it is refused.</summary>
    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await StorefrontApiQueries.SendAsync(
            ctx, null, "Product", new JObject { ["id"] = "1" }, default);

        Assert.Null(product);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// R1346: a variable the document does not declare cannot be passed — the server would reject the request, so
    /// the family refuses it here instead of letting a run fail later with a GraphQL error nobody expected.
    /// </summary>
    [Fact]
    public async Task AnUndeclaredVariableIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl, "getSession", new JObject { ["id"] = "1" }, default);

        Assert.Null(data);
        Assert.Contains("does not declare $id", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheQueryPostsToTheRelativePathOnTheGivenOrigin()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"product\":{\"id\":\"p-1\",\"title\":\"Tee\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl + "/", "Product",
            new JObject { ["id"] = "p-1", ["variationId"] = "v-1" }, default);

        Assert.NotNull(product);
        Assert.Equal(string.Empty, error);
        Assert.EndsWith("/api/graphql", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("Product", sent["operationName"]!.ToObject<string>());
        Assert.Equal(StorefrontApiQueries.Product, sent["query"]!.ToObject<string>());
        Assert.Equal("v-1", sent["variables"]!["variationId"]!.ToObject<string>());
    }

    /// <summary>The flow's product step takes the branch when the run supplies an origin.</summary>
    [Fact]
    public async Task TheProductStepTakesTheStorefrontApiBranch()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"product\":{\"id\":\"p-9\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["storefrontapi.origin"] = server.BaseUrl;
        ctx.Session.Vars["storefrontapi.productId"] = "p-9";

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.EndsWith("/api/graphql", server.Requests[0].Path);
    }

    /// <summary>
    /// R1361: UpdateShippingAddress joins this family because one of its two handlers builds the same api/graphql
    /// path. Its other handler posts to Salesforce's Commerce API — a different transport for a similar idea, and
    /// not something this replica touches.
    /// </summary>
    [Fact]
    public void TheShippingUpdateJoinsTheSameFamily()
    {
        Assert.Equal(2386, StorefrontApiQueries.UpdateShippingAddress.Length);
        Assert.StartsWith("mutation UpdateShippingAddress($input:", StorefrontApiQueries.UpdateShippingAddress);
        Assert.Equal(new[] { "input" }, StorefrontApiQueries.Declared["UpdateShippingAddress"]);
        Assert.Same(StorefrontApiQueries.UpdateShippingAddress,
            StorefrontApiQueries.DocumentFor("UpdateShippingAddress"));
    }

    [Fact]
    public async Task TheShippingUpdatePostsToTheFamilyPath()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"updateShippingAddress\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl, "UpdateShippingAddress", new JObject { ["input"] = new JObject() }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        Assert.EndsWith("/api/graphql", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StorefrontApiQueries.UpdateShippingAddress, sent["query"]!.ToObject<string>());
    }
}
