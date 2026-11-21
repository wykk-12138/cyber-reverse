"""R1341: the operation inventory, the approveMemberPayment dialect, and Highsnobiety's order step.

Three findings, in increasing order of usefulness.

1. `ida.py str` reports seven GraphQL operations; the document region holds sixty-five. Searching for strings is
   not an enumeration of the document pool, and a set difference built on it would have been confidently wrong.
   Walking 0x1470C0000..0x147150000 and testing every four-byte boundary for a frozen header finds them all.

2. `approveMemberPayment` exists twice: 5407 characters at 0x1470E9FA4 — the one R1335 landed — and 5620 at
   0x1470EC9FC. A dialect pair, like the 3DS ones. Which is used when is not established, so this round records
   the pair rather than guessing.

3. The replica carries 18 of the 65 and is missing 47. The largest of those with a known sender is Highsnobiety's
   fetchOrderConfirmation (4825 characters at 0x14713E1FC), whose sender R1339 already identified at 0x140B574F0
   with variables stripePaymentIntentId, locale and preferredLocale. That becomes the store's order step.

Usage: python analysis/add_order_step.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

DOCS = 'analysis/.highsnobiety_docs.json'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
SITE = 0x14713E1FC
SHORT_VARIANT = 0x1470E9FA4
LONG_VARIANT = 0x1470EC9FC


def bytes_at(address, size):
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except json.JSONDecodeError:
            reply = json.loads(reply.splitlines()[0])
    if isinstance(reply, dict):
        reply = reply.get('result', reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def read_string(chars_va):
    length = int.from_bytes(bytes_at(chars_va - 12, 12)[8:12], 'little')
    chunks = []
    offset = 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


documents = json.loads(io.open(DOCS, encoding='utf-8').read())
documents['fetch_order_confirmation'] = read_string(SITE)
print('fetchOrderConfirmation: %d chars' % len(documents['fetch_order_confirmation']))

short = read_string(SHORT_VARIANT)
long_variant = read_string(LONG_VARIANT)
print('approveMemberPayment: %d vs %d chars' % (len(short), len(long_variant)))
print('  short tail: %s' % short[-90:].replace('\r', '').replace('\n', ' '))
print('  long  tail: %s' % long_variant[-90:].replace('\r', '').replace('\n', ' '))

io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(documents, ensure_ascii=False, indent=1, sort_keys=True))


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


source = io.open(FLOWS, encoding='utf-8', newline='').read()

if 'FetchOrderConfirmationDocument' in source:
    raise SystemExit('order step already present')

# Constants go beside the other documents, inside the class.
anchor = '    /// <summary>The three variable keys the add-to-cart document declares.</summary>'
if source.count(anchor) != 1:
    raise SystemExit('constant anchor found %d times' % source.count(anchor))

constants = '''    /// <summary>The order confirmation query, 4825 characters from 0x14713E1FC.</summary>
    public const string FetchOrderConfirmationDocument =
        "__ORDER__";

    /// <summary>The three variable keys the confirmation query declares.</summary>
    public static readonly string[] FetchOrderConfirmationVariables = { "stripePaymentIntentId", "locale", "preferredLocale" };

'''.replace('__ORDER__', escape_literal(documents['fetch_order_confirmation']))

source = source.replace(anchor, constants + anchor)

# The step goes after SubmitEmailAsync, which is the step before it in the image's own ordering.
step_anchor = '''    /// <summary>Apply a discount code through the observed operation and its two variables.</summary>'''
if source.count(step_anchor) != 1:
    raise SystemExit('step anchor found %d times' % source.count(step_anchor))

step = '''    /// <summary>
    /// Read the order confirmation. The query is keyed by the Stripe payment-intent id the image's own sender at
    /// 0x140B574F0 passes, with the two locale fields beside it.
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var intent = c.Session.Vars.GetValueOrDefault("stripePaymentIntentId")
                     ?? c.Session.Vars.GetValueOrDefault("paymentIntentId");
        if (string.IsNullOrEmpty(intent))
            return StepOutcome.Fail("highsnobiety: no stripePaymentIntentId to confirm the order with");

        var locale = Locale(c);
        var variables = new JObject
        {
            ["stripePaymentIntentId"] = intent,
            ["locale"] = locale,
            ["preferredLocale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.preferredLocale") ?? locale,
        };

        return await PostOperationAsync(c, FetchOrderConfirmationOperation, FetchOrderConfirmationDocument,
            variables, "hs-order", "order", ct).ConfigureAwait(false);
    }

'''

source = source.replace(step_anchor, step + step_anchor)

# The operation name constant, beside its siblings.
name_anchor = '    /// <summary>The email mutation\'s operation name, 0x147158FF0.</summary>'
if source.count(name_anchor) != 1:
    raise SystemExit('operation-name anchor found %d times' % source.count(name_anchor))
source = source.replace(
    name_anchor,
    "    /// <summary>The order confirmation query's operation name.</summary>\n"
    '    public const string FetchOrderConfirmationOperation = "fetchOrderConfirmation";\n\n' + name_anchor)

io.open(FLOWS, 'w', encoding='utf-8', newline='').write(source)
print('added SubmitOrderAsync with the 4825-character query')
