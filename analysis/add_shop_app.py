"""R1342: ProductDetails belongs to the Shop app, and landing it tests a 26 KB document in source.

The largest absent operation, ProductDetails at 26206 characters (0x14712CE54), has one code reference —
0x140D26DDB in sub_140D26A20 (1266 bytes) — and that sender says which surface it belongs to:

    https://server.shop.app/graphql     31 characters, 0x147080990
    operationName ProductDetails        0x146E4BF60
    productId, productInput, brokerId, imageWidth, sampleReviews, sortReviewsBy,
    userHasEntryPointsV2, variantsLimit
    RECOMMENDED                         0x146E59A08

So this is not a store flow at all: it is Shopify's Shop app API, which the replica has never carried —
`where_is.py "shop.app"` finds nothing. That makes it a surface of its own, and the document is big enough that
landing it also answers a mechanical question the project has never asked: does a 26 KB string constant survive
source, compiler and AOT intact?

Usage: python analysis/add_shop_app.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x14712CE54
OUT = 'replica/src/Cybersole.Stores/Flows/ShopAppProduct.cs'
DOCS = 'analysis/.shop_app_docs.json'


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
print('ProductDetails: %d chars' % len(document))
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps({'product_details': document}, ensure_ascii=False, indent=1, sort_keys=True))


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
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Shopify's Shop app product query — the surface behind <c>https://server.shop.app/graphql</c>.
///
/// <para>
/// <b>Observed</b> (R1342): the sender at <c>sub_140D26A20</c> (1266 bytes) composes that host (0x147080990,
/// 31 characters), sets <c>operationName</c> to <c>ProductDetails</c> (0x146E4BF60), and fills eight variables —
/// <c>productId</c>, <c>productInput</c>, <c>brokerId</c>, <c>imageWidth</c>, <c>sampleReviews</c>,
/// <c>sortReviewsBy</c>, <c>userHasEntryPointsV2</c>, <c>variantsLimit</c> — with <c>RECOMMENDED</c>
/// (0x146E59A08) beside them. The document is 26206 characters at 0x14712CE54.
/// </para>
///
/// <para>
/// The replica has never carried this surface: it is Shopify's app API, not any one store's. So it lives here as a
/// standalone query rather than as a store flow, and a caller supplies the product identifiers the document asks
/// for — the image never says where they come from.
/// </para>
/// </summary>
public static class ShopAppProduct
{
    /// <summary>The Shop app GraphQL endpoint, 0x147080990.</summary>
    public const string Url = "https://server.shop.app/graphql";

    /// <summary>The operation name, 0x146E4BF60.</summary>
    public const string OperationName = "ProductDetails";

    /// <summary>The review sort the sender names, 0x146E59A08.</summary>
    public const string SortRecommended = "RECOMMENDED";

    /// <summary>The document, 26206 characters from 0x14712CE54.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The eight variable keys the sender fills, in its own spelling.</summary>
    public static readonly string[] VariableNames =
    {
        "productId", "productInput", "brokerId", "imageWidth", "sampleReviews",
        "sortReviewsBy", "userHasEntryPointsV2", "variantsLimit",
    };

    /// <summary>
    /// The request body. <paramref name="variables"/> is the caller's: the image never shows where the product
    /// identifiers come from, and inventing them would send a query about a product nobody asked for.
    /// </summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for a product. Returns the <c>product</c> node or null with the reason in <paramref name="error"/>.
    /// </summary>
    public static async Task<(JObject? Product, string Error)> FetchAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables is null || variables.Count == 0)
            return (null, "shop-app: no variables — the document needs the product identifiers to say anything");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, Envelope(variables), "shop-app-product", ct)
                .ConfigureAwait(false);

            if (reply is null) return (null, "shop-app: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "shop-app: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var product = reply["data"]?["product"] as JObject;
            return product is null ? (null, "shop-app: no product in reply") : (product, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "shop-app: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s (%d bytes of source)' % (OUT, len(source)))
