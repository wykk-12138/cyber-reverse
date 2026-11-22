"""R1377b: addToCart and buynow are Magento, not session-shaped — move them where the vocabulary points.

addToCart declares $sku, $qty, $type and $info; buynow's own body carries item {sku, qty, quote_id, type: "Simple",
bundleOptions} and isNormalBuyFlow, and answers with cart_id and session_id. quote_id and "Simple" are Magento's
vocabulary, and MagentoCart already holds this platform's documents — so both belong there, not with the session
family I first put them in. SignInAsGuest stays: its $medium / SignInMediumTypeEnum is a different shape.

This moves them and keeps the tests honest about which class owns what.
"""
import io
import re

SESSION = 'replica/src/Cybersole.Stores/Flows/StoreSessionQueries.cs'
MAGENTO = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'
TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'
MAGENTO_TESTS = 'replica/tests/Cybersole.Tests/MagentoCartTests.cs'

session = io.open(SESSION, encoding='utf-8', newline='').read()

# Pull the two documents out of the session class.
documents = {}
for name in ('addToCart', 'buynow'):
    pattern = '    public const string %sDocument = "' % name
    start = session.find(pattern)
    if start < 0:
        raise SystemExit('%s constant not found' % name)
    end = session.find('";', start) + 2

    summary_start = session.rfind('    /// <summary>', 0, start)
    literal = session[start:end]
    value_start = literal.find('"') + 1
    documents[name] = literal[value_start:-2]
    session = session[:summary_start] + session[end + 1:]

for name in ('addToCart', 'buynow'):
    session = re.sub(r'\n        \["%s"\] = [^\n]*' % name, '', session, count=1)
    session = re.sub(r'\n        "%s" => %sDocument,' % (name, name), '', session, count=1)

io.open(SESSION, 'w', encoding='utf-8', newline='').write(session)
print('removed from the session family: %s' % ', '.join(documents))

magento = io.open(MAGENTO, encoding='utf-8', newline='').read()
if 'BuyNowDocument' in magento:
    raise SystemExit('already present in MagentoCart')

anchor = '    public const string CustomerCartDocument ='
if magento.count(anchor) != 1:
    raise SystemExit('Magento anchor matched %d times' % magento.count(anchor))

blocks = []
for name, constant, note in (
        ('addToCart', 'AddToCartDocument', 'declares $sku, $qty, $type and $info'),
        ('buynow', 'BuyNowDocument', 'a query: item {sku, qty, quote_id, type: "Simple"} and isNormalBuyFlow')):
    escaped = documents[name].replace('"', '""')
    blocks.append('''    /// <summary>
    /// %s, from the image's own document. Magento's vocabulary — %s.
    /// </summary>
    public const string %s = @"%s";

''' % (name, note, constant, escaped))

magento = magento.replace(anchor, ''.join(blocks) + anchor, 1)
io.open(MAGENTO, 'w', encoding='utf-8', newline='').write(magento)
print('added to MagentoCart')

tests = io.open(TESTS, encoding='utf-8').read()
tests = re.sub(r'\n        Assert\.Equal\(232, StoreSessionQueries\.addToCartDocument\.Length\);', '', tests)
tests = re.sub(r'\n        Assert\.Equal\(216, StoreSessionQueries\.buynowDocument\.Length\);', '', tests)
tests = re.sub(r'\n        Assert\.Equal\(new\[\] \{ "info", "qty", "sku", "type" \}, StoreSessionQueries\.Declared\["addToCart"\]\);', '', tests)
tests = re.sub(r'\n        Assert\.Empty\(StoreSessionQueries\.Declared\["buynow"\]\);', '', tests)
tests = re.sub(r'\n        Assert\.NotNull\(StoreSessionQueries\.DocumentFor\("addToCart"\)\);', '', tests)
tests = re.sub(r'\n        Assert\.NotNull\(StoreSessionQueries\.DocumentFor\("buynow"\)\);', '', tests)
tests = tests.replace('public void TheLastThreeOperationsLanded()', 'public void TheGuestSignInLanded()')
tests = tests.replace('/// R1377: the three that were still absent. Nineteen of twenty-three session operations had already landed here;\n    /// these finish the inventory, and their declared sets are the documents\' own — buynow declares nothing.',
                      '/// R1377: SignInAsGuest was the last absent operation shaped like this family. addToCart and buynow turned\n    /// out to be Magento\'s and live in MagentoCart.')
io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('session tests trimmed')

magento_tests = io.open(MAGENTO_TESTS, encoding='utf-8').read()
if 'TheCartAndBuyNowDocumentsAreMagentos' not in magento_tests:
    block = '''
    /// <summary>
    /// R1377: addToCart and buynow carry Magento's vocabulary — sku/qty/quote_id/"Simple" — so they belong with this
    /// platform's documents rather than with the session family they were first filed under.
    /// </summary>
    [Fact]
    public void TheCartAndBuyNowDocumentsAreMagentos()
    {
        Assert.Contains("$sku", MagentoCart.AddToCartDocument);
        Assert.Contains("$qty", MagentoCart.AddToCartDocument);
        Assert.Contains("$type", MagentoCart.AddToCartDocument);

        Assert.StartsWith("query buynow", MagentoCart.BuyNowDocument);
        Assert.Contains("quote_id", MagentoCart.BuyNowDocument);
        Assert.Contains("isNormalBuyFlow", MagentoCart.BuyNowDocument);
        Assert.Contains("cart_id", MagentoCart.BuyNowDocument);
    }
}
'''
    magento_tests = magento_tests.rstrip()
    magento_tests = magento_tests[:magento_tests.rfind('}')].rstrip('\n') + '\n' + block
    io.open(MAGENTO_TESTS, 'w', encoding='utf-8', newline='').write(magento_tests)
    print('magento test appended')
