"""R1351: three senders, and only one of them says where it goes.

Every one of the three carries no host, which on its own would put all three in the unattributed pile. What
separates them is the path: getProductDetails's sender builds

    apps/product-drops?kind=mutation&operation=getProductDetails

— Shopify's product-drops app endpoint, with the operation passed as a query parameter rather than in the body,
which is the same shape as the PayPal partner family. saveAddress and maintainShippingGroups build no path at all,
only the envelope keys, so they join getCart in the pile that cannot be attributed yet.

Usage: python analysis/add_product_drops.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470F43C4
OUT = 'replica/src/Cybersole.Stores/Flows/ShopifyProductDrops.cs'
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


document = read_string(SOURCE)
print('getProductDetails: %d chars' % len(document))


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


source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Shopify product-drops app query — <c>getProductDetails</c>.
///
/// <para>
/// <b>Observed</b> (R1351): the sender at <c>sub_140C81880</c> (1010 bytes) builds the relative path
/// <c>apps/product-drops?kind=mutation&amp;operation=getProductDetails</c> — the operation travels as a query
/// parameter, and the only document variable is <c>$handle</c>. The document is 499 characters at 0x1470F43C4.
/// </para>
///
/// <para>
/// <b>Inference:</b> that the parameter name <c>kind</c> means the same thing here as in the partner family, where
/// its values are operational words. Nothing in this sender sets it to anything but <c>mutation</c>, so no other
/// value is offered here.
/// </para>
/// </summary>
public static class ShopifyProductDrops
{
    /// <summary>The relative path the sender builds, including its query string.</summary>
    public const string Path = "apps/product-drops?kind=mutation&operation=getProductDetails";

    /// <summary>The operation name, which also appears inside <see cref="Path"/>.</summary>
    public const string OperationName = "getProductDetails";

    /// <summary>The document, 499 characters from 0x1470F43C4.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The one variable the document declares.</summary>
    public static readonly string[] DeclaredVariables = { "handle" };

    /// <summary>The request body the sender builds.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for a product by handle. <paramref name="origin"/> is the store's, because the path is relative.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> FetchAsync(
        FlowContext c, string? origin, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "product-drops: no origin");
        if (variables?["handle"] is null || string.IsNullOrEmpty(variables["handle"]!.ToString()))
            return (null, "product-drops: no handle — the only variable the document declares");

        var url = origin!.TrimEnd('/') + "/" + Path;
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(variables), "product-drops", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "product-drops: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "product-drops: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "product-drops: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "product-drops: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)

# Record the two that cannot be attributed yet.
notes = 'analysis/.unattributed_operations.json'
try:
    existing = json.loads(io.open(notes, encoding='utf-8').read())
except FileNotFoundError:
    existing = {}
existing.update({
    'saveAddress': 'no host, no path — only the envelope keys; same pile as getCart',
    'maintainShippingGroups': 'no host, no path — only the envelope keys; same pile as getCart',
    'getCart': 'no host, no path — only getCart/key/locale',
})
io.open(notes, 'w', encoding='utf-8', newline='').write(
    json.dumps(existing, ensure_ascii=False, indent=1, sort_keys=True))
print('recorded %d unattributed operations' % len(existing))
