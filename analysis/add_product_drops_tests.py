"""R1351 tests plus a caller: the product-drops query, reached from the product step."""

import io

TESTS = 'replica/tests/Cybersole.Tests/ShopifyProductDropsTests.cs'
FLOW = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'

tests = '''using System.Threading.Tasks;
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
        Assert.StartsWith("query getProductDetails($handle: String!)", ShopifyProductDrops.Document);
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
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"product\\":{\\"id\\":\\"1\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyProductDrops.FetchAsync(
            ctx, server.BaseUrl, new JObject { ["handle"] = "tee" }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        Assert.Contains("apps/product-drops", server.Requests[0].Path);
        Assert.Contains("operation=getProductDetails", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopifyProductDrops.Document, sent["query"]!.ToObject<string>());
    }

    /// <summary>The product step takes it when the run names a drops origin.</summary>
    [Fact]
    public async Task TheProductStepTakesTheProductDropsBranch()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"product\\":{\\"id\\":\\"p-3\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/drop-tee" };
        ctx.Session.Vars["productdrops.origin"] = server.BaseUrl;

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Contains("apps/product-drops", server.Requests[0].Path);
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)

flow = io.open(FLOW, encoding='utf-8', newline='').read()
if 'ShopifyProductDrops' not in flow:
    anchor = '        var searchKey = c.Session.Vars.GetValueOrDefault("shopapp.searchKey");'
    if flow.count(anchor) != 1:
        raise SystemExit('flow anchor found %d times' % flow.count(anchor))

    branch = '''        // R1351: the product-drops app query. Its path is relative with the operation in the query string, so
        // the origin comes from the run; the handle is the one this step already resolved from the url.
        var dropsOrigin = c.Session.Vars.GetValueOrDefault("productdrops.origin");
        if (!string.IsNullOrEmpty(dropsOrigin))
        {
            var dropsHandle = c.Session.Vars.GetValueOrDefault("productdrops.handle") ?? ProductHandle(c.Url);
            if (string.IsNullOrEmpty(dropsHandle))
                return StepOutcome.Fail("shopify: product-drops needs a handle and the url has none");

            var (dropsData, dropsError) = await ShopifyProductDrops.FetchAsync(c, dropsOrigin,
                new JObject { ["handle"] = dropsHandle }, ct).ConfigureAwait(false);
            if (dropsData is null) return StepOutcome.Fail(dropsError);

            c.Session.Vars["product"] = dropsData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

'''
    flow = flow.replace(anchor, branch + anchor)
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
    print('added the product-drops branch')
