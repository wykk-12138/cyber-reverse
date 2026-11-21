"""R1323: append the two-variant tests to PayPalThreeDsTests."""

import io

PATH = 'replica/tests/Cybersole.Tests/PayPalThreeDsTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'ResolveDocumentWithoutProviderFields' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1323: the image sends two variants of the resolve mutation from two different functions, both
    /// referenced once — so both paths are live and the replica has to be able to send either.
    /// <c>sub_141113680</c> (15615 bytes) sends the 10370-character document; <c>sub_14110FDB0</c> (14458
    /// bytes) sends the 10262-character one at 0x1470D7974, which is the same text minus one field block.
    /// </summary>
    [Fact]
    public void BothResolveVariantsAreTheStringsTheImageHolds()
    {
        Assert.Equal(10370, PayPalThreeDs.ResolveDocument.Length);
        Assert.Equal(10262, PayPalThreeDs.ResolveDocumentWithoutProviderFields.Length);
        Assert.True(PayPalThreeDs.ResolveDocument.Length - PayPalThreeDs.ResolveDocumentWithoutProviderFields.Length == 108);
    }

    /// <summary>
    /// The difference is one insertion, not a rewrite: the longer document is the shorter one with a block of
    /// provider and device-data fields added at offset 2890. Asserting the insertion point is what stops a
    /// future edit from "tidying" the two into one text with the fields moved somewhere else.
    /// </summary>
    [Fact]
    public void TheLongerVariantIsTheShorterOnePlusOneBlock()
    {
        var shortText = PayPalThreeDs.ResolveDocumentWithoutProviderFields;
        var longText = PayPalThreeDs.ResolveDocument;

        Assert.Equal(shortText[..2890], longText[..2890]);
        Assert.Equal(shortText[2890..], longText[2998..]);
        Assert.Contains("authenticationProvider", longText[2890..2998]);
        Assert.Contains("cardBrandProcessed", longText[2890..2998]);
        Assert.DoesNotContain("authenticationProvider", shortText);
    }

    [Fact]
    public void TheSelectorDefaultsToTheLongerVariantAndCanAskForTheShorter()
    {
        Assert.Equal(PayPalThreeDs.ResolveDocument, PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation));
        Assert.Equal(PayPalThreeDs.ResolveDocument,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation, providerFields: true));
        Assert.Equal(PayPalThreeDs.ResolveDocumentWithoutProviderFields,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation, providerFields: false));

        // The flag only applies to the resolve operation; the other three are unaffected.
        Assert.Equal(PayPalThreeDs.LookUpDocument,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.LookUpOperation, providerFields: false));
    }
}
'''

# The file ends with the class close; put the tests before it and keep one close.
assert text.rstrip().endswith('}')
text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended 3 tests to PayPalThreeDsTests')
