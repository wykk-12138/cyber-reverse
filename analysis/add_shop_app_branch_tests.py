"""R1344 tests: the Shop app branch inside the Shopify product step."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheProductStepTakesTheShopAppBranch' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1344: the Shop app query had no consumer, so the type existed only for its tests. ShopifyFlow's product
    /// step now takes it when a run supplies the identifiers — a separate API (server.shop.app) reached through a
    /// branch, not a replacement for the store's own /products/&lt;handle&gt;.js lookup.
    /// </summary>
    [Fact]
    public async Task TheProductStepTakesTheShopAppBranch()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"product\\":{\\"id\\":\\"gid://shop/1\\",\\"title\\":\\"Tee\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["shopapp.brokerId"] = "broker-1";
        ctx.Session.Vars["shopapp.url"] = server.BaseUrl + "/graphql";

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        var sent = Newtonsoft.Json.Linq.JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopAppProduct.OperationName, sent["operationName"]!.ToObject<string>());
        Assert.Equal("broker-1", sent["variables"]!["brokerId"]!.ToObject<string>());
        Assert.Equal("RECOMMENDED", sent["variables"]!["sortReviewsBy"]!.ToObject<string>());
        Assert.Equal("gid://shop/1", ctx.Session.Vars["productId"]);
    }

    /// <summary>Without the identifiers the step keeps doing what it always did.</summary>
    [Fact]
    public async Task WithoutTheBrokerIdTheStorefrontLookupStays()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"product\\":{\\"id\\":1,\\"title\\":\\"Tee\\"}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/some-handle" };

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.EndsWith("/products/some-handle.js", server.Requests[0].Path);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended two branch tests')
