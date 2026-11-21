"""R1371: createMyPayment's request shape is fully recoverable — the host is not, and does not need to be invented.

Two handlers. sub_140E51E20 is the reply side: it reads isv_tokenCaptureContextSignature out of data and has the words
"Error processing payment" and "StatusInfo". sub_140E55A00 is the request side, and it is the interesting one: it
composes customFields out of isv_payment_data, isv_store, isv_screenHeight, isv_screenWidth and isv_customerIpAddress,
with centAmount and currencyCode beside them, names cybersource and creditCardWithPayerAuthentication, and has the
refusal "No capture context".

Neither names a host, so the endpoint is the merchant's own and comes from the caller. What can be implemented without
guessing is the request itself, which is what this does: the document, the custom-field names, the refusal, and the
reply key.

Usage: python analysis/add_cybersource_payment.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470F3DC4
OUT = 'replica/src/Cybersole.Stores/Payments/CybersourcePayment.cs'
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
    chunks, offset = [], 0
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
print('createMyPayment: %d chars' % len(document))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['create_my_payment'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Cybersource's payment creation, as this image builds it.
///
/// <para>
/// <b>Observed</b> (R1371): the request handler <c>sub_140E55A00</c> composes <c>customFields</c> from
/// <c>isv_payment_data</c>, <c>isv_store</c>, <c>isv_screenHeight</c>, <c>isv_screenWidth</c> and
/// <c>isv_customerIpAddress</c>, with <c>centAmount</c> and <c>currencyCode</c> beside them, and names
/// <c>cybersource</c> and <c>creditCardWithPayerAuthentication</c>. Its refusal is "No capture context".
/// The reply handler <c>sub_140E51E20</c> reads <c>isv_tokenCaptureContextSignature</c> out of <c>data</c> and
/// carries "Error processing payment".
/// </para>
///
/// <para>
/// <b>Not observed:</b> a host. Neither handler names one, so the endpoint is the merchant's own and comes from the
/// caller — the same rule every family without a host follows here.
/// </para>
/// </summary>
public static class CybersourcePayment
{
    /// <summary>The operation name.</summary>
    public const string OperationName = "createMyPayment";

    /// <summary>The document, 493 characters from 0x1470E... (see .block_a_docs.json: create_my_payment).</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The provider name the handler carries.</summary>
    public const string ProviderName = "cybersource";

    /// <summary>The payment method the handler names.</summary>
    public const string PayerAuthenticationMethod = "creditCardWithPayerAuthentication";

    /// <summary>The custom-field keys, in the order the handler names them.</summary>
    public static readonly string[] CustomFieldNames =
    {
        "isv_payment_data", "isv_store", "isv_screenHeight", "isv_screenWidth", "isv_customerIpAddress",
    };

    /// <summary>The handler's words when the capture context is missing.</summary>
    public const string NoCaptureContextMessage = "No capture context";

    /// <summary>The reply handler's words when the provider refuses.</summary>
    public const string ErrorProcessingPaymentMessage = "Error processing payment";

    /// <summary>The reply key the capture context signature arrives in.</summary>
    public const string CaptureContextSignatureKey = "isv_tokenCaptureContextSignature";

    /// <summary>
    /// Build the custom fields from what a run knows: the payment data blob, the store name, the two screen
    /// dimensions and the customer's address. Empty values are dropped rather than sent as blanks, because the
    /// provider reads a present-but-empty field differently from an absent one.
    /// </summary>
    public static JObject BuildCustomFields(
        string? paymentData, string? store, int screenHeight, int screenWidth, string? customerIpAddress)
    {
        var fields = new JObject();
        if (!string.IsNullOrEmpty(paymentData)) fields["isv_payment_data"] = paymentData;
        if (!string.IsNullOrEmpty(store)) fields["isv_store"] = store;
        if (screenHeight > 0) fields["isv_screenHeight"] = screenHeight;
        if (screenWidth > 0) fields["isv_screenWidth"] = screenWidth;
        if (!string.IsNullOrEmpty(customerIpAddress)) fields["isv_customerIpAddress"] = customerIpAddress;
        return fields;
    }

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Create the payment. Without a capture context the handler refuses, so this refuses too rather than sending a
    /// request the provider would answer with an authorisation error.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> CreateAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint))
            return (null, "cybersource: no endpoint — the merchant host is the caller's");

        var signature = variables?["captureContext"]?.ToString()
                        ?? variables?["customFields"]?["isv_payment_data"]?.ToString();
        if (string.IsNullOrEmpty(signature)) return (null, NoCaptureContextMessage);

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, endpoint!.TrimEnd('/'), Envelope(variables!), "cybersource", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, ErrorProcessingPaymentMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, ErrorProcessingPaymentMessage);

            var data = reply["data"] as JObject;
            return data is null ? (null, ErrorProcessingPaymentMessage) : (data, string.Empty);
        }
        catch (Exception)
        {
            return (null, ErrorProcessingPaymentMessage);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
