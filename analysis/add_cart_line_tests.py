"""R1331: append the cart-line edit tests to the Shopify GraphQL test class."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheLineEditTakesTheStructuredPath' in text:
    raise SystemExit('tests already present')

if 'using Cybersole.Http;' not in text:
    text = text.replace('using Cybersole.Stores.Flows;', 'using Cybersole.Http;\nusing Cybersole.Stores.Flows;', 1)
if 'using Cybersole.Tests.Support;' not in text:
    text = text.replace('using Cybersole.Stores.Flows;', 'using Cybersole.Stores.Flows;\nusing Cybersole.Tests.Support;', 1)

block = '''
    /// <summary>
    /// R1331: cartLinesUpdate had no caller since it was declared. With a cart id, a line id and a storefront
    /// token — all three of which the GraphQL cart read now supplies — the edit takes the structured path and
    /// sends the observed mutation.
    /// </summary>
    [Fact]
    public async Task TheLineEditTakesTheStructuredPath()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"cartLinesUpdate\\":{\\"cart\\":{\\"checkoutUrl\\":\\"https://shop.test/checkout\\"}}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Quantity = 3;
        ctx.Session.Vars[ShopifyFlow.GraphQlTokenVar] = "tok";
        ctx.Session.Vars[ShopifyFlow.GraphQlCartVar] = "gid://shopify/Cart/1";
        ctx.Session.Vars["shopify.lineId"] = "gid://shopify/CartLine/9";
        ctx.Session.Vars["shopify.apiVersion"] = "2025-04";

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.EditLineAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        var sent = Newtonsoft.Json.Linq.JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopifyGraphQl.CartLinesUpdate, sent["query"]!.ToObject<string>());
        Assert.Equal("gid://shopify/Cart/1", sent["variables"]!["cartId"]!.ToObject<string>());
        Assert.Equal("gid://shopify/CartLine/9", sent["variables"]!["lines"]![0]!["id"]!.ToObject<string>());
        Assert.Equal(3, sent["variables"]!["lines"]![0]!["quantity"]!.ToObject<int>());
    }

    /// <summary>
    /// Without a line id there is nothing for cartLinesUpdate to address, so the REST call this step has always
    /// made stays — the structured path is an addition, not a replacement.
    /// </summary>
    [Fact]
    public async Task WithoutALineIdTheRestCallRemains()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Quantity = 2;

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.EditLineAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.EndsWith("/cart/update.js", server.Requests[0].Path);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the cart-line edit tests')
