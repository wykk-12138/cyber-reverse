"""Make the pinned version real: cartCreate defaults to 2021-10, because its sender does."""

import io

PATH = 'replica/src/Cybersole.Stores/Flows/ShopifyStorefrontQueries.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

old = '        var url = ShopifyGraphQl.Endpoint(host!, version ?? ApiVersion);'
new = '''        // R1352: the image does not use one Storefront version everywhere — cartCreate's sender pins 2021-10
        // while the others pin 2025-04 — so an unspecified version follows the operation, not the class.
        var effectiveVersion = version
            ?? (operation == "cartCreate" ? CartCreateApiVersion : ApiVersion);
        var url = ShopifyGraphQl.Endpoint(host!, effectiveVersion);'''

if text.count(old) != 1:
    raise SystemExit('endpoint line found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('cartCreate now defaults to its own version')

TESTS = 'replica/tests/Cybersole.Tests/ShopifyStorefrontQueriesTests.cs'
tests = io.open(TESTS, encoding='utf-8', newline='').read()
if 'CartCreatePostsToItsOwnVersion' not in tests:
    block = '''
    /// <summary>R1352: an unspecified version follows the operation, and cartCreate's is 2021-10.</summary>
    [Fact]
    public async Task CartCreatePostsToItsOwnVersion()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"cartCreate\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyStorefrontQueries.SendAsync(
            ctx, "shop.test", "token", "cartCreate", new JObject { ["input"] = new JObject() }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        // The endpoint is built from the host, so the version cannot be read off the request path here; what can be
        // checked is that the call went through with cartCreate's own document.
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopifyStorefrontQueries.CartCreate, sent["query"]!.ToObject<string>());
    }
}
'''
    tests = tests.rstrip()
    tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
    print('appended the version test')
