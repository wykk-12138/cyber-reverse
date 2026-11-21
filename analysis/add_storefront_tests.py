"""R1345 tests: the storefront-API product query and its branch."""

import io

PATH = 'replica/tests/Cybersole.Tests/StorefrontApiProductTests.cs'
source = '''using System.Threading.Tasks;
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
public sealed class StorefrontApiProductTests
{
    [Fact]
    public void TheOperationAndPathAreTheObservedOnes()
    {
        Assert.Equal("Product", StorefrontApiProduct.OperationName);
        Assert.Equal("api/graphql", StorefrontApiProduct.Path);
        Assert.DoesNotContain("://", StorefrontApiProduct.Path);
    }

    [Fact]
    public void TheDocumentIsTheWholeStringAndDeclaresFourVariables()
    {
        Assert.Equal(10620, StorefrontApiProduct.Document.Length);
        Assert.StartsWith("query Product($id: ID!", StorefrontApiProduct.Document);
        Assert.Equal(new[] { "id", "isDraft", "variationId", "src" }, StorefrontApiProduct.DeclaredVariables);
        Assert.Equal(new[] { "id", "variationId" }, StorefrontApiProduct.SenderVariables);
        foreach (var name in StorefrontApiProduct.DeclaredVariables)
            Assert.Contains("$" + name, StorefrontApiProduct.Document);
    }

    /// <summary>A relative path with no origin would be a request to nowhere, so it is refused.</summary>
    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await StorefrontApiProduct.FetchAsync(
            ctx, null, new JObject { ["id"] = "1" }, default);

        Assert.Null(product);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task WithoutAnIdNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await StorefrontApiProduct.FetchAsync(
            ctx, server.BaseUrl, new JObject(), default);

        Assert.Null(product);
        Assert.Contains("no id", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheQueryPostsToTheRelativePathOnTheGivenOrigin()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"product\\":{\\"id\\":\\"p-1\\",\\"title\\":\\"Tee\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await StorefrontApiProduct.FetchAsync(
            ctx, server.BaseUrl + "/", new JObject { ["id"] = "p-1", ["variationId"] = "v-1" }, default);

        Assert.NotNull(product);
        Assert.Equal(string.Empty, error);
        Assert.EndsWith("/api/graphql", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("Product", sent["operationName"]!.ToObject<string>());
        Assert.Equal(StorefrontApiProduct.Document, sent["query"]!.ToObject<string>());
        Assert.Equal("v-1", sent["variables"]!["variationId"]!.ToObject<string>());
    }

    /// <summary>The flow's product step takes the branch when the run supplies an origin.</summary>
    [Fact]
    public async Task TheProductStepTakesTheStorefrontApiBranch()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"product\\":{\\"id\\":\\"p-9\\"}}}"));
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
}
'''

io.open(PATH, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % PATH)
