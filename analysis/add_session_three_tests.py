"""Tests for the three new session operations."""

import io

TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheThreeHostLessOperationsJoined' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1367: the rest of the host-less group, landed the way R1359 landed four of them — envelope-only handlers,
    /// same block, origin from the caller. createMyPayment is deliberately absent: R1364 showed it belongs with the
    /// Cybersource family.
    /// </summary>
    [Fact]
    public void TheThreeHostLessOperationsJoined()
    {
        Assert.Equal(421, StoreSessionQueries.CreateCartByStoreDocument.Length);
        Assert.Equal(251, StoreSessionQueries.InitiateCheckoutDocument.Length);
        Assert.Equal(223, StoreSessionQueries.MaintainShippingGroupsDocument.Length);

        Assert.Equal(new[] { "country", "currency", "locale", "storeKey", "taxMode" },
            StoreSessionQueries.Declared["createCartByStore"]);
        Assert.Empty(StoreSessionQueries.Declared["initiateCheckout"]);
        Assert.Equal(new[] { "cartId" }, StoreSessionQueries.Declared["maintainShippingGroups"]);

        foreach (var name in new[] { "createCartByStore", "initiateCheckout", "maintainShippingGroups" })
            Assert.NotNull(StoreSessionQueries.DocumentFor(name));
    }

    /// <summary>createMyPayment stays out of this family, on R1364's evidence.</summary>
    [Fact]
    public void ThePaymentCreationIsNotInTheSessionFamily()
    {
        Assert.Null(StoreSessionQueries.DocumentFor("createMyPayment"));
    }

    [Fact]
    public async Task TheCheckoutInitiationPostsItsEmptyVariableSet()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"initiateCheckout\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "initiateCheckout", new JObject(), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.InitiateCheckoutDocument, sent["query"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended three tests')
