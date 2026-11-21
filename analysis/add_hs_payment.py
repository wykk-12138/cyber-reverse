"""R1350: createCheckoutPayment is Highsnobiety's payment step — proven by its sender's address, not its signature.

The signature pass could not place it: $storefront and $withoutShippingAddressSet match no family I had written
down. What places it is where its sender lives. The document's one code reference is 0x140B56EA4, inside
sub_140B56CC0 — the very function R1339's sweep of the Highsnobiety host listed as "Create payment" with the
variables storefront and App. Same block, same host, same operation.

So the family detector in signature_clusters.py only recognises families already written into it. When it says
"none", the next question is not "what is this" but "who sends it" — and the sender's address is the answer that
does not depend on my list.

Usage: python analysis/add_hs_payment.py
"""
import io
import json

DOCS = 'analysis/.block_a_docs.json'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

document = json.loads(io.open(DOCS, encoding='utf-8').read())['createCheckoutPayment']
print('createCheckoutPayment: %d chars  head: %s' % (len(document),
                                                     document[:80].replace('\n', ' ').replace('\r', '')))


def escape_literal(text):
    out = []
    for character in text:
        if character == '\\':
            out.append('\\\\')
        elif character == '"':
            out.append('\\"')
        elif character == '\r':
            out.append('\\r')
        elif character == '\n':
            out.append('\\n')
        elif character == '\t':
            out.append('\\t')
        else:
            out.append(character)
    return ''.join(out)


text = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'CreateCheckoutPaymentDocument' in text:
    raise SystemExit('already present')

anchor = "    /// <summary>\n    /// The billing mutation, 4989 characters from 0x1470F5B24."
if text.count(anchor) != 1:
    raise SystemExit('constant anchor found %d times' % text.count(anchor))

constants = '''    /// <summary>
    /// The payment mutation, 222 characters from 0x1470F3BEC. Its one code reference is 0x140B56EA4, inside this
    /// store's own payment sender (sub_140B56CC0), which is what placed it here (R1350).
    /// </summary>
    public const string CreateCheckoutPaymentDocument =
        "%s";

''' % escape_literal(document)

text = text.replace(anchor, constants + anchor)

step_anchor = "    /// <summary>\n    /// Read the order confirmation."
if text.count(step_anchor) != 1:
    raise SystemExit('step anchor found %d times' % text.count(step_anchor))

step = '''    /// <summary>
    /// Start the payment. The document declares two variables — <c>$storefront</c> and
    /// <c>$withoutShippingAddressSet</c> — and both are the caller's, because the image never shows what fills them.
    /// </summary>
    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var storefront = c.Session.Vars.GetValueOrDefault("highsnobiety.storefront")
                         ?? c.Session.Vars.GetValueOrDefault("storeId");
        if (string.IsNullOrEmpty(storefront))
            return StepOutcome.Fail("highsnobiety: no $storefront — the payment mutation is keyed by it");

        var variables = new JObject
        {
            ["storefront"] = storefront,
            ["withoutShippingAddressSet"] = string.Equals(
                c.Session.Vars.GetValueOrDefault("highsnobiety.withoutShipping"),
                "true", StringComparison.OrdinalIgnoreCase),
        };

        var body = new JObject
        {
            ["operationName"] = "createCheckoutPayment",
            ["query"] = CreateCheckoutPaymentDocument,
            ["variables"] = variables,
        };

        var host = c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;
        var res = await PostJsonAsync(c, host, body.ToString(Newtonsoft.Json.Formatting.None),
            "hs-payment", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("highsnobiety payment failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"highsnobiety payment HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["payment"] = res.Body;
        return StepOutcome.Success();
    }

'''

text = text.replace(step_anchor, step + step_anchor)
io.open(FLOWS, 'w', encoding='utf-8', newline='').write(text)
print('added SubmitPaymentAsync with the 222-character document')
