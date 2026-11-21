"""R1347: ShopProductSearch belongs to the Shop app — same host, and it names its variables.

The clustering pass sorted the absent operations by address and found three blocks. The smallest held
ShopProductSearch, addToCart and buynow; the first two turned out to be different animals. ShopProductSearch's
sender (0x140D26050, 1264 bytes) carries https://server.shop.app/graphql — the host ProductDetails uses — and
names brokerId, filter, first, inStock, includeProductFilters, key and searchKind with the label
SHOP_STORE_PRODUCT_SEARCH. The other sender has no host at all, only a store's cart vocabulary, so it stays out.

Address proximity got me to the block; the host is what decides membership. That distinction is the point: a
neighbour is a lead, not evidence.

Usage: python analysis/add_shop_search.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x14713AB24
CLASS = 'replica/src/Cybersole.Stores/Flows/ShopAppProduct.cs'
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
print('ShopProductSearch: %d chars' % len(document))

documents = json.loads(io.open(DOCS, encoding='utf-8').read())
documents['product_search'] = document
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


text = io.open(CLASS, encoding='utf-8', newline='').read()
if 'SearchDocument' in text:
    raise SystemExit('search already present')

anchor = '    /// <summary>The eight variable keys the sender fills, in its own spelling.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

constants = '''    /// <summary>The search operation name, 0x146...; the sender labels it SHOP_STORE_PRODUCT_SEARCH.</summary>
    public const string SearchOperation = "ShopProductSearch";

    /// <summary>The search document, %d characters from 0x14713AB24.</summary>
    public const string SearchDocument =
        "%s";

    /// <summary>The seven variable keys the search sender fills.</summary>
    public static readonly string[] SearchVariableNames =
    {
        "brokerId", "filter", "first", "inStock", "includeProductFilters", "key", "searchKind",
    };

''' % (len(document), escape_literal(document))

text = text.replace(anchor, constants + anchor)

# The search call goes after FetchAsync, which it sits beside in the image.
method_anchor = '''    /// <summary>
    /// Ask for a product. Returns the <c>product</c> node or null with the reason in <paramref name="error"/>.
    /// </summary>'''
if text.count(method_anchor) != 1:
    raise SystemExit('method anchor found %d times' % text.count(method_anchor))

search = '''    /// <summary>
    /// Search the Shop app's catalogue. Same host and envelope as the product query; the variables are the ones its
    /// own sender fills. Null with a reason when the reply carries no results node.
    /// </summary>
    public static async Task<(JObject? Results, string Error)> SearchAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables is null || variables["key"] is null || string.IsNullOrEmpty(variables["key"]!.ToString()))
            return (null, "shop-app: no search key — the query is keyed by it");

        var body = new JObject
        {
            ["operationName"] = SearchOperation,
            ["query"] = SearchDocument,
            ["variables"] = variables,
        };

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, body, "shop-app-search", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "shop-app: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "shop-app: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "shop-app: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "shop-app: " + ex.GetType().Name);
        }
    }

'''

text = text.replace(method_anchor, search + method_anchor)
io.open(CLASS, 'w', encoding='utf-8', newline='').write(text)
print('added SearchDocument, SearchVariableNames and SearchAsync')
