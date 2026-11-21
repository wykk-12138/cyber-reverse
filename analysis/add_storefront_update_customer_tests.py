"""Tests for the new member."""

import io

TESTS = 'replica/tests/Cybersole.Tests/StorefrontApiProductTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheCustomerUpdateJoinsTheSameFamily' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>R1362: UpdateCustomerForCart is the sixth member of this family, same relative path.</summary>
    [Fact]
    public void TheCustomerUpdateJoinsTheSameFamily()
    {
        Assert.Equal(382, StorefrontApiQueries.UpdateCustomerForCart.Length);
        Assert.StartsWith("mutation UpdateCustomerForCart($input:", StorefrontApiQueries.UpdateCustomerForCart);
        Assert.Equal(new[] { "input" }, StorefrontApiQueries.Declared["UpdateCustomerForCart"]);
        Assert.Same(StorefrontApiQueries.UpdateCustomerForCart,
            StorefrontApiQueries.DocumentFor("UpdateCustomerForCart"));
    }

    /// <summary>Six operations now answer to the one relative path, and each keeps its own document.</summary>
    [Fact]
    public void TheFamilyHasSixDistinctDocuments()
    {
        var names = new[] { "AddItemToCart", "CreateInitialCart", "Product", "CheckoutCart", "getSession",
                            "UpdateShippingAddress", "UpdateCustomerForCart" };
        foreach (var name in names) Assert.NotNull(StorefrontApiQueries.DocumentFor(name));

        var documents = names.Select(StorefrontApiQueries.DocumentFor).ToArray();
        Assert.Equal(documents.Length, documents.Distinct().Count());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
if 'using System.Linq;' not in text:
    text = 'using System.Linq;\n' + text
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two tests')
