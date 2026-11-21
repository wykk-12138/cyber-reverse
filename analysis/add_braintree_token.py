"""R1358: generateClientToken is a Braintree client token, and its handler names the fields.

The operation name at 0x14703DADC has two handlers. The first, sub_140B5EDB0, holds:

    Error getting token
    StatusInfo
    authorizationFingerprint
    clientToken

authorizationFingerprint is Braintree's, and clientToken is what that call returns. The second handler,
sub_140B61090, holds onepanini — the marker that also appears in the Shop app's add-to-cart and, as PANINI, in the
PayPal order handler — so this store's payment stack is Braintree underneath a PANINI-named module.

getShippingMethods, by contrast, has no standalone operation-name string at all: the string table only offers closure
names from other classes. It joins CreditCard in the group that cannot be followed by name.

Usage: python analysis/add_braintree_token.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x14714348C
OUT = 'replica/src/Cybersole.Stores/Payments/BraintreeClientToken.cs'
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
print('generateClientToken: %d chars  %s' % (len(document),
                                             document[:64].replace('\n', ' ').replace('\r', '')))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['generate_client_token'] = document
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
/// Braintree's client token, as this image asks for it.
///
/// <para>
/// <b>Observed</b> (R1358): the operation name's handler <c>sub_140B5EDB0</c> holds <c>authorizationFingerprint</c>,
/// <c>clientToken</c>, "Error getting token" and "StatusInfo"; <c>authorizationFingerprint</c> is Braintree's field
/// and <c>clientToken</c> is what the call returns. The document is 188 characters at 0x14714348C.
/// </para>
///
/// <para>
/// <b>Observed:</b> a second handler, <c>sub_140B61090</c>, holds <c>onepanini</c> — the marker that also appears in
/// the Shop app's add-to-cart handler and, as PANINI, in the PayPal order handler. So the payment stack is Braintree
/// under a module named after that token; the name itself is not protocol, which is why this class does not depend on
/// it.
/// </para>
/// </summary>
public static class BraintreeClientToken
{
    /// <summary>The operation name, 0x14703DADC.</summary>
    public const string OperationName = "generateClientToken";

    /// <summary>The document, 188 characters from 0x14714348C.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The field Braintree calls the authorization fingerprint.</summary>
    public const string AuthorizationFingerprintField = "authorizationFingerprint";

    /// <summary>The field the reply carries the token in.</summary>
    public const string ClientTokenField = "clientToken";

    /// <summary>The handler's words when the token cannot be had.</summary>
    public const string ErrorGettingTokenMessage = "Error getting token";

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Fetch the client token. The reply's <c>clientToken</c> is returned; a reply without one becomes the handler's
    /// own message rather than a raw error.
    /// </summary>
    public static async Task<(string? Token, string Error)> FetchAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint)) return (null, "braintree: no endpoint");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, endpoint!, Envelope(variables ?? new JObject()), "braintree-token", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, ErrorGettingTokenMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, ErrorGettingTokenMessage);

            var token = reply["data"]?[ClientTokenField]?.ToString()
                        ?? reply[ClientTokenField]?.ToString();
            return string.IsNullOrEmpty(token) ? (null, ErrorGettingTokenMessage) : (token, string.Empty);
        }
        catch (Exception)
        {
            return (null, ErrorGettingTokenMessage);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
