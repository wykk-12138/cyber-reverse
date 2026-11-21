"""R1323: add the second live ResolveThreeDsContingency variant the image carries.

The replica's ResolveDocument is byte-identical to variant B (10370 characters, verified by
analysis/compare_resolve.py), which is what sub_141113680 at 0x141117103 sends. The image has a second
document of the same family at 0x1470D7974 (10262 characters), sent by a different function
(sub_14110FDB0, 14458 bytes) whose body is 108 characters shorter: B inserts one block of extra fields at
offset 2890 --

    authenticationProvider
    cardBrandProcessed
    dataOnlyIndicator
    deviceDataCollectionBin...

So the image has two dialects of the same mutation, both referenced, and the replica had only one. This adds
the other verbatim and makes the choice explicit at DocumentFor, defaulting to the one that was already there
so no existing caller changes behaviour.

Usage: python analysis/add_resolve_variant.py
"""
import io

SOURCE = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
VARIANT = 'analysis/.three_ds_a.txt'

text = io.open(SOURCE, encoding='utf-8').read()
document = io.open(VARIANT, encoding='utf-8').read()

if 'ResolveDocumentWithoutProviderFields' in text:
    raise SystemExit('variant already present')

literal = document.replace('"', '""')

anchor = '    /// <summary>The four state-machine names the image carries for the 3DS challenge.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

block = (
    '    /// <summary>\n'
    '    /// The other live variant of the same mutation — 10262 characters from 0x1470D7974, sent by\n'
    '    /// <c>sub_14110FDB0</c> (14458 bytes). It is <see cref="ResolveDocument"/> with one field block missing:\n'
    '    /// the longer document inserts <c>authenticationProvider</c>, <c>cardBrandProcessed</c>,\n'
    '    /// <c>dataOnlyIndicator</c> and the device-data collection fields at offset 2890. Both documents are\n'
    '    /// referenced exactly once in the image, so both code paths are live and the choice belongs to the\n'
    '    /// caller rather than to this class.\n'
    '    /// </summary>\n'
    '    public const string ResolveDocumentWithoutProviderFields = @"' + literal + '";\n'
    '\n'
)

text = text.replace(anchor, block + anchor)

# The selector: default keeps the behaviour every existing caller already has.
old_selector = (
    '    public static string DocumentFor(string operationName) => operationName switch\n'
    '    {\n'
    '        JwtQueryOperation => JwtQueryDocument,\n'
    '        AuthenticateOperation => AuthenticateDocument,\n'
    '        LookUpOperation => LookUpDocument,\n'
    '        ResolveOperation => ResolveDocument,\n'
    '        _ => string.Empty,\n'
    '    };'
)
new_selector = (
    '    public static string DocumentFor(string operationName, bool providerFields = true) =>\n'
    '        operationName switch\n'
    '        {\n'
    '            JwtQueryOperation => JwtQueryDocument,\n'
    '            AuthenticateOperation => AuthenticateDocument,\n'
    '            LookUpOperation => LookUpDocument,\n'
    '            // R1323: the image sends two variants of the resolve mutation from two functions. The default is\n'
    '            // the longer one, which is what this method returned before the variant was known.\n'
    '            ResolveOperation => providerFields ? ResolveDocument : ResolveDocumentWithoutProviderFields,\n'
    '            _ => string.Empty,\n'
    '        };'
)
if text.count('    public static string DocumentFor(string operationName) => operationName switch') != 1:
    raise SystemExit('selector anchor not found once')
text = text.replace(old_selector, new_selector)

io.open(SOURCE, 'w', encoding='utf-8', newline='').write(text)
print('added ResolveDocumentWithoutProviderFields (%d chars) and the selector' % len(document))
