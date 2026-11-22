"""Tests for the last three operations, and the corrected coverage figure."""

import io

TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheLastThreeOperationsLanded' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1377: the three that were still absent. Nineteen of twenty-three session operations had already landed here;
    /// these finish the inventory, and their declared sets are the documents' own — buynow declares nothing.
    /// </summary>
    [Fact]
    public void TheLastThreeOperationsLanded()
    {
        Assert.Equal(453, StoreSessionQueries.SignInAsGuestDocument.Length);
        Assert.Equal(232, StoreSessionQueries.addToCartDocument.Length);
        Assert.Equal(216, StoreSessionQueries.buynowDocument.Length);

        Assert.Equal(new[] { "medium" }, StoreSessionQueries.Declared["SignInAsGuest"]);
        Assert.Equal(new[] { "info", "qty", "sku", "type" }, StoreSessionQueries.Declared["addToCart"]);
        Assert.Empty(StoreSessionQueries.Declared["buynow"]);

        Assert.NotNull(StoreSessionQueries.DocumentFor("SignInAsGuest"));
        Assert.NotNull(StoreSessionQueries.DocumentFor("addToCart"));
        Assert.NotNull(StoreSessionQueries.DocumentFor("buynow"));
    }

    /// <summary>The sign-in mutation names its medium, which is the only variable it takes.</summary>
    [Fact]
    public void TheGuestSignInCarriesItsMedium()
    {
        Assert.StartsWith("mutation SignInAsGuest($medium:", StoreSessionQueries.SignInAsGuestDocument);
        Assert.Contains("SignInMediumTypeEnum", StoreSessionQueries.SignInAsGuestDocument);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two tests')
