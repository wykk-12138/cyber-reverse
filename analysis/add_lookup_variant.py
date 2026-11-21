"""R1324: add the short look-up dialect and let the flag cover both operations that have two.

Measured before writing (analysis/measure_three_ds_docs.py):
  lookup_b (0x1470E2CCC, 871) is the replica's LookUpDocument, byte-identical
  authenticate (0x1470E1FAC, 813) is the replica's AuthenticateDocument, byte-identical
  lookup_a (0x1470E261C, 844) is lookup_b minus 27 characters at offset 827: "authenticationProvider\n    "

So the two dialects differ by the same field the resolve pair differed by, and the resolve flag from R1323 was
too narrow: it named one operation when the property belongs to two. That also makes the test written last
round — "the flag does not affect the look-up" — wrong, and it is corrected here rather than deleted.

Usage: python analysis/add_lookup_variant.py
"""
import io
import json

SOURCE = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
TEST = 'replica/tests/Cybersole.Tests/PayPalThreeDsTests.cs'
DOCS = 'analysis/.three_ds_docs.json'

text = io.open(SOURCE, encoding='utf-8').read()
docs = json.loads(io.open(DOCS, encoding='utf-8').read())
short = docs['lookup_a']

if 'LookUpDocumentWithoutProviderFields' in text:
    raise SystemExit('look-up variant already present')

anchor = '    /// <summary>The four state-machine names the image carries for the 3DS challenge.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

block = (
    '    /// <summary>\n'
    '    /// The other live variant of the look-up mutation — 844 characters from 0x1470E261C. It is\n'
    '    /// <see cref="LookUpDocument"/> minus the same <c>authenticationProvider</c> field block the resolve pair\n'
    '    /// differs by (27 characters at offset 827), which is what makes the two pairs one dialect question\n'
    '    /// rather than two coincidences.\n'
    '    /// </summary>\n'
    '    public const string LookUpDocumentWithoutProviderFields = @"' + short.replace('"', '""') + '";\n'
    '\n'
)
text = text.replace(anchor, block + anchor)

old = '            LookUpOperation => LookUpDocument,'
new = ('            // R1324: the look-up has the same pair, so the flag means the same thing here.\n'
       '            LookUpOperation => providerFields ? LookUpDocument : LookUpDocumentWithoutProviderFields,')
if text.count(old) != 1:
    raise SystemExit('look-up selector line found %d times' % text.count(old))
text = text.replace(old, new)

# The selector's own wording still says "the longer one", which is now true of two operations.
text = text.replace(
    '    public static string DocumentFor(string operationName, bool providerFields = true) =>',
    '    /// <summary>\n'
    '    /// The document for an operation. <paramref name="providerFields"/> selects the dialect: the image\n'
    '    /// sends both a resolve and a look-up that include <c>authenticationProvider</c> and one of each that\n'
    '    /// does not. The default is the longer text, which is what this method returned before the pairs were\n'
    '    /// known.\n'
    '    /// </summary>\n'
    '    public static string DocumentFor(string operationName, bool providerFields = true) =>')

io.open(SOURCE, 'w', encoding='utf-8', newline='').write(text)
print('added LookUpDocumentWithoutProviderFields (%d chars) and widened the flag' % len(short))

# Correct the assertion written in R1323: the flag now covers the look-up because the look-up has a pair too.
tests = io.open(TEST, encoding='utf-8').read()
stale = (
    '        // The flag only applies to the resolve operation; the other three are unaffected.\n'
    '        Assert.Equal(PayPalThreeDs.LookUpDocument,\n'
    '            PayPalThreeDs.DocumentFor(PayPalThreeDs.LookUpOperation, providerFields: false));'
)
if tests.count(stale) != 1:
    raise SystemExit('stale assertion not found once')
fresh = (
    '        // R1324: this assertion used to say the flag did not affect the look-up. It does: the image sends\n'
    '        // two look-up dialects too, differing by the same authenticationProvider block as the resolve pair.\n'
    '        Assert.Equal(PayPalThreeDs.LookUpDocumentWithoutProviderFields,\n'
    '            PayPalThreeDs.DocumentFor(PayPalThreeDs.LookUpOperation, providerFields: false));\n'
    '        // The two operations without a pair are still unaffected.\n'
    '        Assert.Equal(PayPalThreeDs.AuthenticateDocument,\n'
    '            PayPalThreeDs.DocumentFor(PayPalThreeDs.AuthenticateOperation, providerFields: false));'
)
tests = tests.replace(stale, fresh)

extra = '''
    /// <summary>
    /// R1324: the look-up pair differs by the same field as the resolve pair — 27 characters at offset 827 —
    /// which is what turns two coincidences into one dialect question. Both operations are live in the image,
    /// so both texts have to be present and selectable.
    /// </summary>
    [Fact]
    public void TheLookUpPairDiffersByTheSameProviderField()
    {
        Assert.Equal(871, PayPalThreeDs.LookUpDocument.Length);
        Assert.Equal(844, PayPalThreeDs.LookUpDocumentWithoutProviderFields.Length);

        var shortText = PayPalThreeDs.LookUpDocumentWithoutProviderFields;
        var longText = PayPalThreeDs.LookUpDocument;

        Assert.Equal(shortText[..827], longText[..827]);
        Assert.Equal(shortText[827..], longText[854..]);
        Assert.Equal("authenticationProvider", longText[827..854].Trim());
        Assert.DoesNotContain("authenticationProvider", shortText);
        Assert.Equal(813, PayPalThreeDs.AuthenticateDocument.Length);
        Assert.DoesNotContain("authenticationProvider", PayPalThreeDs.AuthenticateDocument);
    }
}
'''
tests = tests.rstrip()
tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + extra
io.open(TEST, 'w', encoding='utf-8', newline='').write(tests)
print('corrected the R1323 assertion and added the look-up pair test')
