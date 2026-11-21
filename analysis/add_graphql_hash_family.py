"""R1357: the cart block does not send documents — it sends GraphQL hashes.

Two 64-hex constants in sub_14088BB80 (the function that references GetCartCookie's name) turn out to be values for
headers that the same function also names:

    x-graphql-hash          83c4b10c99a6f6c89abf7e84f83d5dc6360f8627eb2b70c7eb4b12590c6f1950
                            b613893783ae3da73f38b5f93a9a59ccbaa7f131a209cac92634a93d06f06866
    x-graphql-query-name
    x-header-id

with "Getting session", "StatusInfo" and the full browser header set beside them. So this family posts persisted
queries identified by hash and name, which is why their senders held no host and no path to find — and why the
documents exist at all: they are what the hash stands for.

Two hashes for three operations (GetCartCookie, GetCart, GetProductInventory) does not establish which belongs to
which, so the pairing stays unknown and only the mechanism is implemented.

Usage: python analysis/add_graphql_hash_family.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

DOCUMENTS = {
    'get_cart_cookie': 0x147120B5C,
    'get_product_inventory': 0x147120C0C,
    'get_cart': 0x14711EFC4,
}
OUT = 'replica/src/Cybersole.Stores/Flows/GraphQlHashQueries.cs'
DOCS = 'analysis/.hash_family_docs.json'


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


documents = {}
for name, address in DOCUMENTS.items():
    documents[name] = read_string(address)
    print('%-22s %5d chars  %s' % (name, len(documents[name]),
                                   documents[name][:60].replace('\n', ' ').replace('\r', '')))

io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(documents, ensure_ascii=False, indent=1, sort_keys=True))

source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The family that posts persisted GraphQL queries by hash rather than by document.
///
/// <para>
/// <b>Observed</b> (R1357): <c>sub_14088BB80</c> — the function that references <c>GetCartCookie</c>'s name — names
/// the headers <c>x-graphql-hash</c>, <c>x-graphql-query-name</c> and <c>x-header-id</c>, and holds two 64-hex
/// constants that fit the first of those:
/// <c>83c4b10c…f1950</c> and <c>b6138937…06866</c>. It also carries "Getting session" and "StatusInfo".
/// </para>
///
/// <para>
/// <b>Unknown:</b> which hash belongs to which operation. Two values and three operations do not settle it, so the
/// class takes the hash from the caller and never picks one itself. The documents are still sent when a caller has
/// no hash — a server that accepts persisted queries generally accepts the query too, and sending the wrong hash
/// would be worse than sending none.
/// </para>
/// </summary>
public static class GraphQlHashQueries
{
    /// <summary>The hash header.</summary>
    public const string HashHeader = "x-graphql-hash";

    /// <summary>The query-name header.</summary>
    public const string QueryNameHeader = "x-graphql-query-name";

    /// <summary>The header the same function also names.</summary>
    public const string HeaderIdHeader = "x-header-id";

    /// <summary>The two 64-hex values the handler holds, in the order they appear.</summary>
    public static readonly string[] ObservedHashes =
    {
        "83c4b10c99a6f6c89abf7e84f83d5dc6360f8627eb2b70c7eb4b12590c6f1950",
        "b613893783ae3da73f38b5f93a9a59ccbaa7f131a209cac92634a93d06f06866",
    };

    /// <summary>GetCartCookie, 74 characters from 0x147120B5C.</summary>
    public const string GetCartCookieDocument = "__COOKIE__";

    /// <summary>GetProductInventory, 490 characters from 0x147120C0C.</summary>
    public const string GetProductInventoryDocument = "__INVENTORY__";

    /// <summary>GetCart, 3520 characters from 0x14711EFC4.</summary>
    public const string GetCartDocument = "__CART__";

    /// <summary>The document for an operation, or null when it is not one of the three.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "GetCartCookie" => GetCartCookieDocument,
        "GetProductInventory" => GetProductInventoryDocument,
        "GetCart" => GetCartDocument,
        _ => null,
    };

    /// <summary>The body: variables always, the query only when there is no hash to identify it.</summary>
    public static JObject Envelope(string operation, JObject variables, bool includeDocument)
    {
        var body = new JObject
        {
            ["operationName"] = operation,
            ["variables"] = variables,
        };
        if (includeDocument) body["query"] = DocumentFor(operation);
        return body;
    }

    /// <summary>
    /// Post one operation. With a hash the query travels as a header and the body carries variables alone; without
    /// one the document is sent, which is the same request in the long form.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, string operation, JObject variables, string? hash,
        CancellationToken ct, string? headerId = null)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "graphql-hash: no origin");
        if (DocumentFor(operation) is null) return (null, "graphql-hash: unknown operation " + operation);

        var byHash = !string.IsNullOrWhiteSpace(hash);
        if (byHash)
        {
            c.Session.Headers[HashHeader] = hash!;
            c.Session.Headers[QueryNameHeader] = operation;
            if (!string.IsNullOrEmpty(headerId)) c.Session.Headers[HeaderIdHeader] = headerId!;
        }

        var url = origin!.TrimEnd('/');
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, variables, !byHash), "graphql-hash", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, operation + ": no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, operation + ": " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, operation + ": no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, operation + ": " + ex.GetType().Name);
        }
    }
}
'''.replace('__COOKIE__', escape_literal(documents['get_cart_cookie'])) \
   .replace('__INVENTORY__', escape_literal(documents['get_product_inventory'])) \
   .replace('__CART__', escape_literal(documents['get_cart']))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
