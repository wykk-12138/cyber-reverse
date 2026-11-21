"""The checkout document needs a production caller, the same rule every document here follows."""

import io

PATH = 'replica/src/Cybersole.Stores/Flows/ShopifyProductDrops.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'CreateCheckoutAsync' in text:
    raise SystemExit('already wired')

anchor = '''    /// <summary>
    /// Ask for a product by handle. <paramref name="origin"/> is the store's, because the path is relative.
    /// </summary>'''
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

step = '''    /// <summary>
    /// Start a checkout through the same app. The document declares $variantId, $location, $attributes and
    /// $recaptchaToken; all four are the caller's, because what fills them is not in the sender.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> CreateCheckoutAsync(
        FlowContext c, string? origin, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "product-drops: no origin");

        var url = origin!.TrimEnd('/') + "/" + CheckoutPath;
        var body = new JObject
        {
            ["operationName"] = "createCheckout",
            ["query"] = CreateCheckoutDocument,
            ["variables"] = variables,
        };

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, body, "product-drops-checkout", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "product-drops: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "product-drops: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "product-drops: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "product-drops: " + ex.GetType().Name);
        }
    }

'''

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(anchor, step + anchor))
print('added CreateCheckoutAsync')

TESTS = 'replica/tests/Cybersole.Tests/ShopifyProductDropsTests.cs'
tests = io.open(TESTS, encoding='utf-8', newline='').read()
if 'TheCheckoutPostsToItsOwnPath' not in tests:
    block = '''
    [Fact]
    public async Task TheCheckoutPostsToItsOwnPath()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"createCheckout\\":{\\"id\\":\\"c-1\\"}}}"));
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
'''
    tests = tests.rstrip()
    tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
    print('appended the checkout call test')
