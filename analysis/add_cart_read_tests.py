"""R1329 tests: the cart read has a caller, and it says what the store said."""

import io

PATH = 'replica/tests/Cybersole.Tests/MagentoCartTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheCartReadUsesTheImageQuery' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1329: CustomerCartDocument was declared in R1320 and had no caller — a document the replica could not
    /// send. The step reads the cart through it, and this pins the query that goes out.
    /// </summary>
    [Fact]
    public async Task TheCartReadUsesTheImageQuery()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"customerCart\\":{\\"id\\":\\"masked-9\\",\\"total_quantity\\":2," +
                 "\\"items\\":[{\\"uid\\":\\"a\\",\\"quantity\\":2}]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().GetCartAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("masked-9", ctx.Session.Vars["cart"]);
        Assert.Equal("2", ctx.Session.Vars["casio.cartTotal"]);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(MagentoCart.CustomerCartDocument, sent["query"]!.Value<string>());
    }

    /// <summary>
    /// A store that keys carts by masked id answers no customerCart. That is a failure to report, not an empty
    /// cart — the difference decides whether the run continues with a cart it does not have.
    /// </summary>
    [Fact]
    public async Task ACartReplyWithoutCustomerCartIsAFailure()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().GetCartAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("customerCart", outcome.Error);
        Assert.False(ctx.Session.Vars.ContainsKey("cart"));
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the cart-read tests')
