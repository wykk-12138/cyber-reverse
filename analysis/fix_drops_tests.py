"""Meaure before asserting: fix the two assertions that came from memory."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyProductDropsTests.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

text = text.replace(
    'Assert.StartsWith("query getProductDetails($handle: String!)", ShopifyProductDrops.Document);',
    'Assert.StartsWith("mutation getProductDetails($handle: String)", ShopifyProductDrops.Document);')

text = text.replace(
    '''        Assert.Contains("apps/product-drops", server.Requests[0].Path);
        Assert.Contains("operation=getProductDetails", server.Requests[0].Path);''',
    '''        // TinyServer reports the path without its query string, so the query string is checked on the constant
        // and the path here.
        Assert.Contains("product-drops", server.Requests[0].Path);
        Assert.Contains("kind=mutation", ShopifyProductDrops.Path);
        Assert.Contains("operation=getProductDetails", ShopifyProductDrops.Path);''')

text = text.replace(
    'Assert.Contains("apps/product-drops", server.Requests[0].Path);',
    'Assert.Contains("product-drops", server.Requests[0].Path);')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('assertions now match the measured text')
