"""R1352 tests: the two new Storefront operations, the second drops operation, and the version split."""

import io

TESTS = 'replica/tests/Cybersole.Tests/ShopifyStorefrontQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheTwoApiVersionsStayApart' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1352: the Storefront operations do not share one API version — cartCreate's sender pins 2021-10 while
    /// customerAccessTokenCreate's pins 2025-04 — so the version travels with the call.
    /// </summary>
    [Fact]
    public void TheTwoApiVersionsStayApart()
    {
        Assert.Equal("2025-04", ShopifyStorefrontQueries.ApiVersion);
        Assert.Equal("2021-10", ShopifyStorefrontQueries.CartCreateApiVersion);
        Assert.NotEqual(ShopifyStorefrontQueries.ApiVersion, ShopifyStorefrontQueries.CartCreateApiVersion);
    }

    [Fact]
    public void TheTwoNewDocumentsAreTheMeasuredOnes()
    {
        Assert.Equal(91, ShopifyStorefrontQueries.CartCreate.Length);
        Assert.StartsWith("mutation cartCreate {", ShopifyStorefrontQueries.CartCreate);
        Assert.Equal(250, ShopifyStorefrontQueries.CustomerAccessTokenCreate.Length);
        Assert.StartsWith("mutation customerAccessTokenCreate($input: CustomerAccessTok",
            ShopifyStorefrontQueries.CustomerAccessTokenCreate);

        Assert.Equal(new[] { "input", "buyerIdentity", "country", "language" },
            ShopifyStorefrontQueries.Declared["cartCreate"]);
        Assert.Equal(new[] { "input" }, ShopifyStorefrontQueries.Declared["customerAccessTokenCreate"]);
    }

    [Fact]
    public void TheTwoNewOperationsResolveTheirDocuments()
    {
        Assert.Same(ShopifyStorefrontQueries.CartCreate,
            ShopifyStorefrontQueries.DocumentFor("cartCreate"));
        Assert.Same(ShopifyStorefrontQueries.CustomerAccessTokenCreate,
            ShopifyStorefrontQueries.DocumentFor("customerAccessTokenCreate"));
        Assert.Null(ShopifyStorefrontQueries.DocumentFor("createCartByStore"));
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended three storefront tests')

DROPS = 'replica/tests/Cybersole.Tests/ShopifyProductDropsTests.cs'
drops = io.open(DROPS, encoding='utf-8').read()
if 'TheCheckoutUsesTheSameAppWithItsOwnOperation' not in drops:
    block = '''
    /// <summary>R1352: createCheckout is the same product-drops app with its own operation in the path.</summary>
    [Fact]
    public void TheCheckoutUsesTheSameAppWithItsOwnOperation()
    {
        Assert.Equal("apps/product-drops?kind=mutation&operation=createCheckout",
            ShopifyProductDrops.CheckoutPath);
        Assert.Equal(720, ShopifyProductDrops.CreateCheckoutDocument.Length);
        Assert.StartsWith("mutation createCheckout($variantId: String", ShopifyProductDrops.CreateCheckoutDocument);
        Assert.NotEqual(ShopifyProductDrops.Path, ShopifyProductDrops.CheckoutPath);
        Assert.Contains("product-drops", ShopifyProductDrops.CheckoutPath);
    }
}
'''
    drops = drops.rstrip()
    drops = drops[:drops.rfind('}')].rstrip('\n') + '\n' + block
    io.open(DROPS, 'w', encoding='utf-8', newline='').write(drops)
    print('appended the drops checkout test')
