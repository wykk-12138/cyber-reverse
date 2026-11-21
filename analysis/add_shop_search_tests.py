"""R1347 tests: the Shop app search, and the branch that reaches it."""

import io

TESTS = 'replica/tests/Cybersole.Tests/ShopAppProductTests.cs'
FLOW = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'

text = io.open(TESTS, encoding='utf-8').read()
if 'TheSearchCarriesSevenVariables' not in text:
    block = '''
    /// <summary>
    /// R1347: the search shares the product query's host and envelope, and its seven variables are the ones its own
    /// sender fills. The document is 6537 characters at 0x14713AB24.
    /// </summary>
    [Fact]
    public void TheSearchCarriesSevenVariables()
    {
        Assert.Equal("ShopProductSearch", ShopAppProduct.SearchOperation);
        Assert.Equal(6537, ShopAppProduct.SearchDocument.Length);
        Assert.StartsWith("query ShopProductSearch", ShopAppProduct.SearchDocument);
        Assert.Equal(new[] { "brokerId", "filter", "first", "inStock", "includeProductFilters", "key", "searchKind" },
            ShopAppProduct.SearchVariableNames);
    }

    [Fact]
    public async Task ASearchWithoutAKeyIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (results, error) = await ShopAppProduct.SearchAsync(ctx, new JObject(), default);

        Assert.Null(results);
        Assert.Contains("no search key", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheSearchPostsTheObservedEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"products\\":[]}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (results, error) = await ShopAppProduct.SearchAsync(
            ctx, new JObject { ["key"] = "tee", ["first"] = 10 }, default, server.BaseUrl + "/graphql");

        Assert.NotNull(results);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("ShopProductSearch", sent["operationName"]!.ToObject<string>());
        Assert.Equal(ShopAppProduct.SearchDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("tee", sent["variables"]!["key"]!.ToObject<string>());
    }
}
'''
    text = text.rstrip()
    text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
    print('appended three search tests')

flow = io.open(FLOW, encoding='utf-8', newline='').read()
if 'ShopAppProduct.SearchAsync' not in flow:
    anchor = '        var brokerId = c.Session.Vars.GetValueOrDefault("shopapp.brokerId");'
    if flow.count(anchor) != 1:
        raise SystemExit('flow anchor found %d times' % flow.count(anchor))

    branch = '''        // R1347: the catalogue search, when a run carries a key for it. Same host and envelope as the product
        // query, so it sits in the same branch above the store's own lookup.
        var searchKey = c.Session.Vars.GetValueOrDefault("shopapp.searchKey");
        if (!string.IsNullOrEmpty(searchKey))
        {
            var searchVariables = new JObject
            {
                ["key"] = searchKey,
                ["brokerId"] = c.Session.Vars.GetValueOrDefault("shopapp.brokerId"),
                ["first"] = int.TryParse(c.Session.Vars.GetValueOrDefault("shopapp.first"), out var first) ? first : 10,
                ["searchKind"] = c.Session.Vars.GetValueOrDefault("shopapp.searchKind") ?? "SHOP_STORE_PRODUCT_SEARCH",
            };

            var (results, searchError) = await ShopAppProduct
                .SearchAsync(c, searchVariables, ct, c.Session.Vars.GetValueOrDefault("shopapp.url"))
                .ConfigureAwait(false);
            if (results is null) return StepOutcome.Fail(searchError);

            c.Session.Vars["search"] = results.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

'''
    flow = flow.replace(anchor, branch + anchor)
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
    print('added the search branch')
