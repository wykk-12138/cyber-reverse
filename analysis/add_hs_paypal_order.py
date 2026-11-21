"""R1356: placeOrderWithPaypal is Highsnobiety's PayPal order path, and its handler states the outcomes.

The operation name has one standalone string, 0x147113B8C, and both of its references sit inside sub_140B5F250 —
the same address block as the store's other senders. That function carries:

    Error submitting order
    Payment Declined
    Your payment could not be processed
    StatusInfo
    PANINI

PANINI is the marker that turned up in the Shop app's add-to-cart handler too, spelled into a key there; here it is a
standalone token. The document is 843 characters.

Usage: python analysis/add_hs_paypal_order.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x147146F94
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
print('placeOrderWithPaypal: %d chars  %s' % (len(document),
                                              document[:70].replace('\n', ' ').replace('\r', '')))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['place_order_with_paypal'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'PlaceOrderWithPaypalDocument' in text:
    raise SystemExit('already present')

anchor = "    /// <summary>\n    /// The shipping mutation, 4992 characters from 0x1470FA944."
if text.count(anchor) != 1:
    raise SystemExit('constant anchor found %d times' % text.count(anchor))

constants = '''    /// <summary>
    /// The PayPal order mutation, 843 characters from 0x147146F94. Its handler (sub_140B5F250) distinguishes three
    /// outcomes, and they are the messages this class reports (R1356).
    /// </summary>
    public const string PlaceOrderWithPaypalDocument =
        "%s";

    /// <summary>The handler's words for a rejected order.</summary>
    public const string ErrorSubmittingOrderMessage = "Error submitting order";

    /// <summary>The handler's words for a declined payment.</summary>
    public const string PaymentDeclinedMessage = "Payment Declined";

    /// <summary>The handler's words when the payment could not be processed at all.</summary>
    public const string PaymentNotProcessedMessage = "Your payment could not be processed";

''' % escape_literal(document)

text = text.replace(anchor, constants + anchor)

step_anchor = "    /// <summary>\n    /// Submit shipping through the observed mutation."
if text.count(step_anchor) != 1:
    raise SystemExit('step anchor found %d times' % text.count(step_anchor))

step = '''    /// <summary>
    /// Place the order through PayPal. The mutation's variable is the caller's; the three outcomes the handler
    /// distinguishes become the failure messages, in its own words.
    /// </summary>
    public override async Task<StepOutcome> SubmitPayPalOrderAsync(FlowContext c, CancellationToken ct)
    {
        var action = ActionFrom(c, "highsnobiety.paypalOrder", "place the paypal order", out var failure);
        if (action is null) return failure!.Value;

        var body = new JObject
        {
            ["operationName"] = "placeOrderWithPaypal",
            ["query"] = PlaceOrderWithPaypalDocument,
            ["variables"] = new JObject { ["input"] = action },
        };

        var host = c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;
        var res = await PostJsonAsync(c, host, body.ToString(Newtonsoft.Json.Formatting.None),
            "hs-paypal-order", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail(ErrorSubmittingOrderMessage, retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail(ErrorSubmittingOrderMessage, retryable: true);

        if (res.Body is not null && res.Body.Contains("PAYMENT_DECLINED", StringComparison.OrdinalIgnoreCase))
            return StepOutcome.Fail(PaymentDeclinedMessage);
        if (res.Body is not null && res.Body.Contains("\\"errors\\"", StringComparison.Ordinal))
            return StepOutcome.Fail(PaymentNotProcessedMessage);

        c.Session.Vars["order"] = res.Body ?? string.Empty;
        return StepOutcome.Success();
    }

'''

text = text.replace(step_anchor, step + step_anchor)
io.open(FLOWS, 'w', encoding='utf-8', newline='').write(text)
print('added SubmitPayPalOrderAsync with the 843-character document and three messages')
