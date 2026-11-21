"""Replace the network-dependent version test with one that checks the composed endpoint."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyStorefrontQueriesTests.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

start = text.find('    /// <summary>R1352: an unspecified version follows the operation, and cartCreate\'s is 2021-10.</summary>')
if start < 0:
    raise SystemExit('test not found')
end = text.rfind('}')
block = '''    /// <summary>
    /// R1352: an unspecified version follows the operation. Checked on the composed endpoint rather than by
    /// sending, because a fake host would be a real DNS lookup.
    /// </summary>
    [Fact]
    public void TheVersionRuleBuildsTwoDifferentEndpoints()
    {
        var forCart = ShopifyGraphQl.Endpoint("shop.test", ShopifyStorefrontQueries.CartCreateApiVersion);
        var forOthers = ShopifyGraphQl.Endpoint("shop.test", ShopifyStorefrontQueries.ApiVersion);

        Assert.Contains("/api/2021-10/graphql.json", forCart);
        Assert.Contains("/api/2025-04/graphql.json", forOthers);
        Assert.NotEqual(forCart, forOthers);
        Assert.Equal(ShopifyStorefrontQueries.CartCreate,
            ShopifyStorefrontQueries.DocumentFor("cartCreate"));
    }
}
'''

text = text[:start] + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('replaced the network test')
