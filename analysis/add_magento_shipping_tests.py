"""Tests for the Magento shipping-methods query."""

import io

TESTS = 'replica/tests/Cybersole.Tests/MagentoCartTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheShippingMethodsQueryIsMagentos' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1369: getShippingMethods is Magento 2's shipping query — carrier_code/method_code with prices and an address
    /// argument in Magento's snake_case shape. It references twelve variables and declares none, which is how the
    /// image carries it; a replica that declared them would send a different request.
    /// </summary>
    [Fact]
    public void TheShippingMethodsQueryIsMagentos()
    {
        var document = MagentoCart.ShippingMethodsDocument;

        Assert.Equal(531, document.Length);
        Assert.StartsWith("query getShippingMethods {", document);
        foreach (var field in new[] { "carrier_code", "method_code", "carrier_title", "method_title",
                                      "price_excl_tax", "price_incl_tax", "save_in_address_book" })
            Assert.Contains(field, document);
        Assert.Contains("$region", document);
        Assert.DoesNotContain("$region:", document);
    }

    /// <summary>No endpoint, no request — the store's own host is never guessed.</summary>
    [Fact]
    public async Task TheShippingQueryNeedsTheStoresEndpoint()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await MagentoCart.GetShippingMethodsAsync(ctx, null, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no endpoint", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheShippingQueryPostsItsDocument()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"getShippingMethods\\":[]}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await MagentoCart.GetShippingMethodsAsync(
            ctx, server.BaseUrl + "/graphql", new JObject(), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(MagentoCart.ShippingMethodsDocument, sent["query"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended three tests')
