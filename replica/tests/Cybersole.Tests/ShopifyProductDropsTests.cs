using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1351: the product-drops app query. Its sender builds a relative path with the operation in the query string,
/// and the document declares a single variable.
/// </summary>
public sealed class ShopifyProductDropsTests
{
    [Fact]
    public void ThePathCarriesTheOperationAsAParameter()
    {
        Assert.Equal("apps/product-drops?kind=mutation&operation=getProductDetails",
            ShopifyProductDrops.Path);
        Assert.Contains(ShopifyProductDrops.OperationName, ShopifyProductDrops.Path);
        Assert.DoesNotContain("://", ShopifyProductDrops.Path);
    }

    [Fact]
    public void TheDocumentAndItsOneVariable()
    {
        Assert.Equal(499, ShopifyProductDrops.Document.Length);
        Assert.StartsWith("mutation getProductDetails($handle: String)", ShopifyProductDrops.Document);
        Assert.Equal(new[] { "handle" }, ShopifyProductDrops.DeclaredVariables);
    }

    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyProductDrops.FetchAsync(
            ctx, null, new JObject { ["handle"] = "tee" }, default);

        Assert.Null(data);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task WithoutAHandleNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyProductDrops.FetchAsync(
            ctx, server.BaseUrl, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no handle", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheQueryPostsToThePathWithItsQueryString()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"product\":{\"id\":\"1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyProductDrops.FetchAsync(
            ctx, server.BaseUrl, new JObject { ["handle"] = "tee" }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        // TinyServer reports the path without its query string, so the query string is checked on the constant
        // and the path here.
        Assert.Contains("product-drops", server.Requests[0].Path);
        Assert.Contains("kind=mutation", ShopifyProductDrops.Path);
        Assert.Contains("operation=getProductDetails", ShopifyProductDrops.Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopifyProductDrops.Document, sent["query"]!.ToObject<string>());
    }

    /// <summary>The product step takes it when the run names a drops origin.</summary>
    [Fact]
    public async Task TheProductStepTakesTheProductDropsBranch()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"product\":{\"id\":\"p-3\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/drop-tee" };
        ctx.Session.Vars["productdrops.origin"] = server.BaseUrl;

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Contains("product-drops", server.Requests[0].Path);
    }

    /// <summary>R1352: createCheckout is the same product-drops app with its own operation in the path.</summary>
    [Fact]
    public void TheCheckoutUsesTheSameAppWithItsOwnOperation()
    {
        Assert.Equal("apps/product-drops?kind=mutation&operation=createCheckout",
            ShopifyProductDrops.CheckoutPath);
        Assert.Equal(720, ShopifyProductDrops.CreateCheckoutDocument.Length);
        Assert.StartsWith("mutation createCheckout($variantId: String", ShopifyProductDrops.CreateCheckoutDocument);
        Assert.NotEqual(ShopifyProductDrops.Path, ShopifyProductDrops.CheckoutPath);
        Assert.Contains("product-drops", ShopifyProductDrops.CheckoutPath);
    }

    [Fact]
    public async Task TheCheckoutPostsToItsOwnPath()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"createCheckout\":{\"id\":\"c-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyProductDrops.CreateCheckoutAsync(
            ctx, server.BaseUrl, new JObject { ["variantId"] = "gid://shop/1" }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        Assert.Contains("product-drops", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("createCheckout", sent["operationName"]!.ToObject<string>());
        Assert.Equal(ShopifyProductDrops.CreateCheckoutDocument, sent["query"]!.ToObject<string>());
    }
}
