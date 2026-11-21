"""R1354: setShippingAddress completes Highsnobiety — the signature and the sender both say so.

setShippingAddress is 4992 characters and declares $action: SetCartShippingAddress! plus $locale and
$preferredLocale — the same shape the store's billing and email mutations use. Its one code reference is 0x140B59CF7,
inside sub_140B59790, which is the function R1339's sweep of the Highsnobiety host already listed as its shipping
sender. Two independent facts, same answer, so this is the third address step of that store rather than a guess from
a matching length.

With it, Highsnobiety has cart, email, product, billing, payment, shipping and order — its whole checkout.

Usage: python analysis/add_hs_shipping.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470FA944
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
DOCS = 'analysis/.block_a_docs.json'


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


document = read_string(SOURCE)
print('setShippingAddress: %d chars' % len(document))

try:
    docs = json.loads(io.open(DOCS, encoding='utf-8').read())
except FileNotFoundError:
    docs = {}
docs['set_shipping_address'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'SetShippingAddressDocument' in text:
    raise SystemExit('already present')

anchor = "    /// <summary>\n    /// The payment mutation, 222 characters from 0x1470F3BEC."
if text.count(anchor) != 1:
    raise SystemExit('constant anchor found %d times' % text.count(anchor))

constants = '''    /// <summary>
    /// The shipping mutation, 4992 characters from 0x1470FA944. Declares an action object and two locales — this
    /// family's shape — and its one reference sits in the sender R1339's host sweep listed as shipping (R1354).
    /// </summary>
    public const string SetShippingAddressDocument =
        "%s";

''' % escape_literal(document)

text = text.replace(anchor, constants + anchor)

step_anchor = "    /// <summary>\n    /// Start the payment."
if text.count(step_anchor) != 1:
    raise SystemExit('step anchor found %d times' % text.count(step_anchor))

step = '''    /// <summary>
    /// Submit shipping through the observed mutation. The payload is the caller's SetCartShippingAddress object,
    /// which the image never spells out — the same arrangement billing uses.
    /// </summary>
    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)
    {
        var action = ActionFrom(c, "highsnobiety.shippingAction", "submit shipping", out var failure);
        if (action is null) return failure!.Value;

        var locale = Locale(c);
        var variables = new JObject
        {
            ["action"] = action,
            ["locale"] = locale,
            ["preferredLocale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.preferredLocale") ?? locale,
        };

        var host = c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;
        var body = new JObject
        {
            ["operationName"] = "setShippingAddress",
            ["query"] = SetShippingAddressDocument,
            ["variables"] = variables,
        };

        var res = await PostJsonAsync(c, host, body.ToString(Newtonsoft.Json.Formatting.None),
            "hs-shipping", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("highsnobiety shipping failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"highsnobiety shipping HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["shipping"] = res.Body;
        return StepOutcome.Success();
    }

'''

text = text.replace(step_anchor, step + step_anchor)
io.open(FLOWS, 'w', encoding='utf-8', newline='').write(text)
print('added SubmitShippingAsync with the 4992-character document')
