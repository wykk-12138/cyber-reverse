"""Tests for the session family's new member."""

import io

TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheChannelAddJoinsTheSameFamily' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1362: addToCartByChannel belongs here because its handler carries key/locale like getCart and no host.
    /// Its document declares five variables — the sender named a couple more fields than the document takes.
    /// </summary>
    [Fact]
    public void TheChannelAddJoinsTheSameFamily()
    {
        Assert.Equal(2271, StoreSessionQueries.AddToCartByChannelDocument.Length);
        Assert.StartsWith("mutation addToCartByChannel", StoreSessionQueries.AddToCartByChannelDocument);
        Assert.Equal(new[] { "cartId", "locale", "productId", "quantity", "version" },
            StoreSessionQueries.Declared["addToCartByChannel"]);
        Assert.Same(StoreSessionQueries.AddToCartByChannelDocument,
            StoreSessionQueries.DocumentFor("addToCartByChannel"));
    }

    [Fact]
    public async Task TheChannelAddPostsToTheFamilyOrigin()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"addToCartByChannel\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl, "addToCartByChannel",
            new JObject { ["cartId"] = "c-1", ["productId"] = "p-1", ["quantity"] = 1 }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.AddToCartByChannelDocument, sent["query"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two tests')
