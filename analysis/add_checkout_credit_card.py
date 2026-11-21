"""R1368: CreditCard posts to a relative finalize path, and its other handler is Nike's.

The name has five referencers. The handler at sub_140AAE300 builds
api/checkout/v1/orders/ + <order id> + /finalize with the card fields (cardNumber, cardCvv, cardExpiryMonth,
cardExpiryYear, cardName) and the label "Submit order" — a relative path, so the origin is the caller's, and the
order id is a path segment rather than a variable.

The handler at sub_140B29DA7 also names CreditCard and carries https://www.nike.com/nl/checkout/confirmation?cid= with
"Submit payment" and the SHIP/ASTLA tokens: that is the Nike checkout variant, and Nike already has a home in this
replica, so the variant is recorded rather than folded in.

getShippingMethods, meanwhile, has two handlers of its own: one reads carrier_code/carrier_title/method_code/
method_title (Magento's rate shape), the other names onepanini and Panini with city/countryId/postcode — the PANINI
family again. Both recorded.

Usage: python analysis/add_checkout_credit_card.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470CF934
OUT = 'replica/src/Cybersole.Stores/Flows/CheckoutCreditCard.cs'
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
print('CreditCard: %d chars' % len(document))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['credit_card'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The card submission that finalises an order — <c>CreditCard</c>.
///
/// <para>
/// <b>Observed</b> (R1368): <c>sub_140AAE300</c> builds <c>api/checkout/v1/orders/</c> plus the order id plus
/// <c>/finalize</c>, with the card fields <c>cardNumber</c>, <c>cardCvv</c>, <c>cardExpiryMonth</c>,
/// <c>cardExpiryYear</c>, <c>cardName</c> and the label "Submit order". The path is relative, so the origin is the
/// caller's and the order id is a path segment rather than a variable in the document.
/// </para>
///
/// <para>
/// <b>Recorded, not implemented:</b> a second handler carries <c>https://www.nike.com/nl/checkout/confirmation?cid=</c>
/// with "Submit payment" and the SHIP/ASTLA tokens — the Nike variant, which belongs with that store's own steps
/// rather than with this generic path.
/// </para>
/// </summary>
public static class CheckoutCreditCard
{
    /// <summary>The operation name.</summary>
    public const string OperationName = "CreditCard";

    /// <summary>The relative path prefix the sender builds.</summary>
    public const string OrderPathPrefix = "api/checkout/v1/orders/";

    /// <summary>The suffix the sender appends after the order id.</summary>
    public const string FinalizeSuffix = "/finalize";

    /// <summary>The document, 2867 characters from 0x1470CF934.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The card fields the handler names.</summary>
    public static readonly string[] CardFields =
    {
        "cardNumber", "cardCvv", "cardExpiryMonth", "cardExpiryYear", "cardName",
    };

    /// <summary>The handler's words for this step.</summary>
    public const string SubmitOrderMessage = "Submit order";

    /// <summary>The url for one order: origin + the relative path + the id + the suffix.</summary>
    public static string UrlFor(string origin, string orderId) =>
        origin.TrimEnd('/') + "/" + OrderPathPrefix + orderId + FinalizeSuffix;

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Submit the card. The card object is the caller's; nothing about a card belongs in source.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SubmitAsync(
        FlowContext c, string? origin, string? orderId, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "checkout-card: no origin");
        if (string.IsNullOrWhiteSpace(orderId))
            return (null, "checkout-card: no order id — it is a path segment, not a variable");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, UrlFor(origin!, orderId!), Envelope(variables ?? new JObject()),
                    "checkout-card", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, SubmitOrderMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, topLevel[0]?["message"]?.ToString() ?? SubmitOrderMessage);

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "checkout-card: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
