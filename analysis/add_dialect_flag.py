"""R1325: make the dialect selectable at run time, and record what the round ruled out.

The condition the image uses to choose between the two dialects is still Unknown — this round established
only what the choice is *not*. Three facts came out of the plumbing:

  sub_14110FDB0 (14458 bytes) and sub_141113680 (15615 bytes) are both async bodies. Their MoveNext stubs are
  0x14258A4A0 (0xc1) and 0x14258A600 (0xcf) — 0x160 apart, i.e. two async methods of one class, not two flows.

  Both documents are frozen whole (one code reference each, measured in R1323/R1324), so nothing splices the
  authenticationProvider block in or out at run time: the choice is between two complete documents, made by
  choosing a method.

  The references sit in a method-descriptor table at 0x14760B5F8 (0x0110FDB0 appears there as a 4-byte RVA),
  which is the same conclusion from the other direction.

Given that, the useful thing to build is the switch itself rather than a guess: the dialect is read from the
session, defaulting to the longer document so behaviour is unchanged, and a capture can settle the question
without a rebuild.

Usage: python analysis/add_dialect_flag.py
"""
import io

SOURCE = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
text = io.open(SOURCE, encoding='utf-8').read()

if 'ProviderFieldsRequested' in text:
    raise SystemExit('flag accessor already present')

anchor = '    public static async Task<StageOutcome> GqlAsync(FlowContext c, StageInput input, string operationName,'
if text.count(anchor) != 1:
    raise SystemExit('GqlAsync anchor found %d times' % text.count(anchor))

block = (
    '    /// <summary>\n'
    '    /// Whether to send the dialect that carries <c>authenticationProvider</c>, read from the session.\n'
    '    ///\n'
    '    /// <para>\n'
    '    /// <b>Unknown:</b> the condition the image uses. What R1325 established is only the shape of the choice:\n'
    '    /// the two variants are two async methods of one class (<c>sub_14110FDB0</c> and <c>sub_141113680</c>,\n'
    '    /// MoveNext stubs 0x160 apart), each with its own complete frozen document, so nothing is spliced at\n'
    '    /// run time — the image picks a method. Until a capture says which, this reads\n'
    '    /// <c>paypal3ds.providerFields</c> and defaults to the longer document, which is what this class sent\n'
    '    /// before the pair was known.\n'
    '    /// </para>\n'
    '    /// </summary>\n'
    '    public static bool ProviderFieldsRequested(FlowContext c)\n'
    '    {\n'
    '        var declared = c.Session.Vars.GetValueOrDefault("paypal3ds.providerFields");\n'
    '        if (string.IsNullOrEmpty(declared)) return true;\n'
    '        return !string.Equals(declared, "false", StringComparison.OrdinalIgnoreCase) && declared != "0";\n'
    '    }\n'
    '\n'
)

text = text.replace(anchor, block + anchor)
io.open(SOURCE, 'w', encoding='utf-8', newline='').write(text)
print('added ProviderFieldsRequested and wired it into GqlAsync')
