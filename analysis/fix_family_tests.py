"""Replace the id-premise test with the variable-set rule the family actually enforces."""

import io

PATH = 'replica/tests/Cybersole.Tests/StorefrontApiProductTests.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

start = text.find('    /// <summary>\n    /// A relative path with no origin')
end = text.find('    [Fact]\n    public async Task TheQueryPostsToTheRelativePathOnTheGivenOrigin')
if start < 0 or end < 0:
    raise SystemExit('region not found (start=%s end=%s)' % (start, end))

replacement = '''    /// <summary>A relative path with no origin would be a request to nowhere, so it is refused.</summary>
    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, null, "Product", new JObject { ["id"] = "1" }, default);

        Assert.Null(data);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// R1346: a variable the document does not declare cannot be passed — the server would reject the request, so
    /// the family refuses it here instead of letting a run fail later with a GraphQL error nobody expected.
    /// </summary>
    [Fact]
    public async Task AUndeclaredVariableIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl, "getSession", new JObject { ["id"] = "1" }, default);

        Assert.Null(data);
        Assert.Contains("does not declare $id", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>The five documents are all present, with the sizes their addresses measured.</summary>
    [Fact]
    public void AllFiveOperationsCarryTheirDocuments()
    {
        Assert.Equal(2108, StorefrontApiQueries.AddItemToCart.Length);
        Assert.Equal(865, StorefrontApiQueries.CreateInitialCart.Length);
        Assert.Equal(10620, StorefrontApiQueries.Product.Length);
        Assert.Equal(4102, StorefrontApiQueries.CheckoutCart.Length);
        Assert.Equal(133, StorefrontApiQueries.Session.Length);

        Assert.StartsWith("mutation AddItemToCart($input: AddItemToCartInput!)", StorefrontApiQueries.AddItemToCart);
        Assert.StartsWith("mutation CreateInitialCart {", StorefrontApiQueries.CreateInitialCart);
        Assert.StartsWith("query CheckoutCart($id: ID!)", StorefrontApiQueries.CheckoutCart);
        Assert.StartsWith("query getSession {", StorefrontApiQueries.Session);
    }

    /// <summary>Each operation's declared set is the document's own, and the sender's fills are recorded beside it.</summary>
    [Fact]
    public void TheDeclaredSetsAreTheDocumentsOwn()
    {
        Assert.Equal(new[] { "input" }, StorefrontApiQueries.Declared["AddItemToCart"]);
        Assert.Empty(StorefrontApiQueries.Declared["CreateInitialCart"]);
        Assert.Equal(new[] { "id" }, StorefrontApiQueries.Declared["CheckoutCart"]);
        Assert.Empty(StorefrontApiQueries.Declared["getSession"]);

        Assert.Equal(new[] { "id", "input", "productId" }, StorefrontApiQueries.SenderFills["AddItemToCart"]);
        Assert.Equal(new[] { "id" }, StorefrontApiQueries.SenderFills["CheckoutCart"]);
    }

    [Fact]
    public async Task TheCheckoutCartQueryPostsItsOwnDocument()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"cart\\":{\\"id\\":\\"c-1\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl, "CheckoutCart", new JObject { ["id"] = "c-1" }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("CheckoutCart", sent["operationName"]!.ToObject<string>());
        Assert.Equal(StorefrontApiQueries.CheckoutCart, sent["query"]!.ToObject<string>());
    }

'''

text = text[:start] + replacement + text[end:]
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('rewrote the test region')
