"""R1360: TokenizeCreditCard names Braintree's payments host outright.

The nest's five operations split immediately. TokenizeCreditCard's handler, sub_140B632B0, holds

    https://payments.braintree-api.com/graphql

with client, clientSdkMetadata, creditCard, cvv, expirationMonth, expirationYear, billingAddress, input and dropin2 —
Braintree's public payments API and its Drop-in v2 SDK marker. That both confirms R1358's Braintree reading and gives
this operation a host, so it needs no caller-supplied origin.

SignInAsGuest's handler (sub_140CFF770) holds only accessToken, authPayload, data and the operation name, so it stays
in the host-less group.

Usage: python analysis/add_braintree_tokenize.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470E33B4
OUT = 'replica/src/Cybersole.Stores/Payments/BraintreeTokenizeCard.cs'
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
print('TokenizeCreditCard: %d chars  %s' % (len(document),
                                            document[:64].replace('\n', ' ').replace('\r', '')))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['tokenize_credit_card'] = document
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
/// Braintree's card tokenisation, at the payments host its handler names.
///
/// <para>
/// <b>Observed</b> (R1360): <c>sub_140B632B0</c> holds <c>https://payments.braintree-api.com/graphql</c> together
/// with <c>client</c>, <c>clientSdkMetadata</c>, <c>creditCard</c>, <c>cvv</c>, <c>expirationMonth</c>,
/// <c>expirationYear</c>, <c>billingAddress</c> and <c>dropin2</c> — Braintree's payments API and its Drop-in v2
/// marker. The document is 505 characters at 0x1470E33B4.
/// </para>
///
/// <para>
/// <b>Observed:</b> the same module also fetches a client token (R1358), so the two belong to one Braintree
/// integration rather than to a store's own checkout.
/// </para>
/// </summary>
public static class BraintreeTokenizeCard
{
    /// <summary>The host the handler names.</summary>
    public const string Url = "https://payments.braintree-api.com/graphql";

    /// <summary>The operation name.</summary>
    public const string OperationName = "TokenizeCreditCard";

    /// <summary>The document, 505 characters from 0x1470E33B4.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The SDK marker the handler carries — Drop-in v2.</summary>
    public const string ClientSdkName = "dropin2";

    /// <summary>The field names the handler names beside the operation.</summary>
    public static readonly string[] ObservedFields =
    {
        "client", "clientSdkMetadata", "creditCard", "cvv", "expirationMonth", "expirationYear",
        "billingAddress", "input",
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Tokenise a card. The credit-card object, the client token and the SDK metadata are the caller's — copying
    /// card fields into source would be copying credentials, the same rule the storefront token goes by.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> TokenizeAsync(
        FlowContext c, JObject variables, CancellationToken ct)
    {
        if (variables?["creditCard"] is null)
            return (null, "braintree: no creditCard — the mutation is keyed by it");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, Url, Envelope(variables), "braintree-tokenize", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "braintree: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "braintree: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "braintree: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "braintree: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
