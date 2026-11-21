"""R1345: the Product query belongs to a five-sender family that all post to a relative api/graphql.

Following Product to its sender gives 0x140E1BAB0 (1076 bytes), and that function builds its URL by hand — the
constant at 0x145E99C50 turns out to be the characters "api/grap", so the path is *relative* and the host lives
somewhere above. Looking at the neighbours finds the rest of the family:

    0x140E1B1D0  Add to cart      AddItemToCart      id, input, productId
    0x140E1B700  —                CreateInitialCart
    0x140E1BAB0  Find product     Product            id, variationId
    0x140E1BF40  Generate checkout CheckoutCart      id
    0x140E1C390  Get session      (query + variables)

Five operations, one relative path, no host in any of them. Three of those names are already in the absent list
(R1341): AddItemToCart, CreateInitialCart, CheckoutCart, and Product is the one this round took. That makes the
family a store's storefront API whose host the image keeps out of the senders — the same shape as /cartApi/checkout,
and the same reason it cannot be attributed to a store yet.

So the document is landed with its operation and variables, and reached through a branch on a session-supplied
endpoint, which is the only honest way to send a relative path: the caller knows the origin.

Usage: python analysis/add_storefront_product.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x147127B44
OUT = 'replica/src/Cybersole.Stores/Flows/StorefrontApiProduct.cs'
DOCS = 'analysis/.storefront_api_docs.json'


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
print('Product: %d chars  head: %s' % (len(document), document[:70].replace('\n', ' ').replace('\r', '')))
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps({'product': document}, ensure_ascii=False, indent=1, sort_keys=True))


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
/// The <c>Product</c> query of a storefront API that posts to a relative <c>api/graphql</c>.
///
/// <para>
/// <b>Observed</b> (R1345): the sender at <c>sub_140E1BAB0</c> (1076 bytes) sets <c>operationName</c> to
/// <c>Product</c> (0x146E4BB30), fills <c>id</c> and <c>variationId</c>, and appends the path <c>api/graphql</c>
/// — built character by character, which is why the constant at 0x145E99C50 reads "api/grap" rather than a URL.
/// The document is 10620 characters at 0x147127B44.
/// </para>
///
/// <para>
/// <b>Observed:</b> four neighbours post to the same relative path with their own operations —
/// <c>AddItemToCart</c> (0x140E1B1D0), <c>CreateInitialCart</c> (0x140E1B700), <c>CheckoutCart</c> (0x140E1BF40)
/// and a session query (0x140E1C390). Together they are one store's storefront API, and none of the five carries
/// the host, so the origin has to come from the caller. That is why the endpoint is a parameter here rather than a
/// constant: a relative path with an invented host would send a real request to the wrong server.
/// </para>
/// </summary>
public static class StorefrontApiProduct
{
    /// <summary>The operation name, 0x146E4BB30.</summary>
    public const string OperationName = "Product";

    /// <summary>The relative path every sender in this family appends.</summary>
    public const string Path = "api/graphql";

    /// <summary>The document, 10620 characters from 0x147127B44.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The two variable keys the sender fills.</summary>
    public static readonly string[] VariableNames = { "id", "variationId" };

    /// <summary>The request body the sender builds.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for a product. <paramref name="origin"/> is the store's origin — the family never carries it — and the
    /// step refuses rather than guessing, because a guess here is a real request to a real server.
    /// </summary>
    public static async Task<(JObject? Product, string Error)> FetchAsync(
        FlowContext c, string? origin, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin))
            return (null, "storefront-api: no origin — this family posts a relative api/graphql and the image " +
                          "keeps the host above the senders");

        if (variables is null || variables["id"] is null || string.IsNullOrEmpty(variables["id"]!.ToString()))
            return (null, "storefront-api: no id to ask about");

        var url = origin!.TrimEnd('/') + "/" + Path;
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(variables), "storefront-product", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "storefront-api: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "storefront-api: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var product = reply["data"]?["product"] as JObject ?? reply["data"] as JObject;
            return product is null ? (null, "storefront-api: no product in reply") : (product, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "storefront-api: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
