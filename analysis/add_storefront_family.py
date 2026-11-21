"""R1346: the whole api/graphql family, in one class instead of a class per document.

R1345 landed Product and found the four siblings. This finishes the family. Each sender's variables were read
from its function; each document's declared variables from the document itself, and they are not the same set:

  AddItemToCart        mutation, declares $input          sender fills id, input, productId
  CreateInitialCart    mutation, declares nothing         sender fills nothing
  Product              query,    declares four            sender fills id, variationId
  CheckoutCart         query,    declares $id             sender fills id
  getSession           query,    declares nothing         sender fills nothing

The document wins on what may be sent: a variable the document does not declare cannot be passed, and a variable it
declares but the sender leaves out is optional. The class therefore exposes the declared set and lets the caller
fill it.

StorefrontApiProduct becomes StorefrontApiQueries with all five operations. One family, one class — five classes
for one relative path would be five places to keep the same origin rule.

Usage: python analysis/add_storefront_family.py
"""
import io
import json
import os

DOCS = 'analysis/.storefront_api_docs.json'
OLD = 'replica/src/Cybersole.Stores/Flows/StorefrontApiProduct.cs'
NEW = 'replica/src/Cybersole.Stores/Flows/StorefrontApiQueries.cs'

documents = json.loads(io.open(DOCS, encoding='utf-8').read())
documents['product'] = json.loads(io.open(DOCS, encoding='utf-8').read()).get('product') or \
    json.loads(io.open('analysis/.storefront_api_docs.json', encoding='utf-8').read()).get('product')

if 'product' not in documents or not documents['product']:
    # Product was saved by R1345's script separately; rebuild it from the same reader.
    import sys
    sys.path.insert(0, 'analysis')
    from ida import call  # noqa: E402

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

    documents['product'] = read_string(0x147127B44)

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


template = '''using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The five operations of a storefront API that posts a relative <c>api/graphql</c>.
///
/// <para>
/// <b>Observed</b> (R1345, R1346): five senders in one block of address space —
/// <c>sub_140E1B1D0</c> (AddItemToCart), <c>sub_140E1B700</c> (CreateInitialCart), <c>sub_140E1BAB0</c>
/// (Product), <c>sub_140E1BF40</c> (CheckoutCart) and <c>sub_140E1C390</c> (a session query). Each builds the
/// same relative path, none carries a host, and each posts <c>operationName</c>, <c>query</c> and
/// <c>variables</c> as <c>application/json</c>.
/// </para>
///
/// <para>
/// <b>Observed:</b> the sender's variable set and the document's declared set differ. The document wins on what
/// may be sent — a variable it does not declare cannot be passed — so each operation publishes its declared set
/// and takes the values from the caller.
/// </para>
/// </summary>
public static class StorefrontApiQueries
{
    /// <summary>The relative path every sender in this family appends.</summary>
    public const string Path = "api/graphql";

    /// <summary>AddItemToCart, 0x146CB0F40's document at 0x1470CB3F4.</summary>
    public const string AddItemToCart = "__ADD_ITEM__";

    /// <summary>CreateInitialCart, 865 characters at 0x1470CF25C.</summary>
    public const string CreateInitialCart = "__CREATE_CART__";

    /// <summary>Product, 10620 characters at 0x147127B44.</summary>
    public const string Product = "__PRODUCT__";

    /// <summary>CheckoutCart, 4102 characters at 0x14711CF9C.</summary>
    public const string CheckoutCart = "__CHECKOUT__";

    /// <summary>The session query, 133 characters at 0x147146994.</summary>
    public const string Session = "__SESSION__";

    /// <summary>The variables each document declares, which is what a caller may fill.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> Declared = new Dictionary<string, string[]>
    {
        ["AddItemToCart"] = new[] { "input" },
        ["CreateInitialCart"] = Array.Empty<string>(),
        ["Product"] = new[] { "id", "isDraft", "variationId", "src" },
        ["CheckoutCart"] = new[] { "id" },
        ["getSession"] = Array.Empty<string>(),
    };

    /// <summary>The variables the sender of each operation actually fills.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> SenderFills = new Dictionary<string, string[]>
    {
        ["AddItemToCart"] = new[] { "id", "input", "productId" },
        ["CreateInitialCart"] = Array.Empty<string>(),
        ["Product"] = new[] { "id", "variationId" },
        ["CheckoutCart"] = new[] { "id" },
        ["getSession"] = Array.Empty<string>(),
    };

    /// <summary>The document for an operation name, or null when the name is not one of the five.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "AddItemToCart" => AddItemToCart,
        "CreateInitialCart" => CreateInitialCart,
        "Product" => Product,
        "CheckoutCart" => CheckoutCart,
        "getSession" => Session,
        _ => null,
    };

    /// <summary>The request body every sender builds.</summary>
    public static JObject Envelope(string operation, JObject? variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = DocumentFor(operation) ?? throw new ArgumentOutOfRangeException(nameof(operation)),
        ["variables"] = variables ?? new JObject(),
    };

    /// <summary>
    /// Post one operation. <paramref name="origin"/> is the store's origin — the family never carries it — and a
    /// run without one is told so rather than being sent to a guessed host.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, string operation, JObject? variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin))
            return (null, "storefront-api: no origin — this family posts a relative api/graphql and the image " +
                          "keeps the host above the senders");

        var document = DocumentFor(operation);
        if (document is null) return (null, "storefront-api: unknown operation " + operation);

        var declared = Declared[operation];
        if (variables is not null)
        {
            foreach (var property in variables.Properties())
            {
                if (Array.IndexOf(declared, property.Name) >= 0) continue;
                return (null, "storefront-api: " + operation + " does not declare $" + property.Name +
                              " — the document would reject it");
            }
        }

        var url = origin!.TrimEnd('/') + "/" + Path;
        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, variables), "storefront-" + operation, ct)
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
'''

source = (template
          .replace('__ADD_ITEM__', escape_literal(documents['add_item_to_cart']))
          .replace('__CREATE_CART__', escape_literal(documents['create_initial_cart']))
          .replace('__PRODUCT__', escape_literal(documents['product']))
          .replace('__CHECKOUT__', escape_literal(documents['checkout_cart']))
          .replace('__SESSION__', escape_literal(documents['get_session'])))

io.open(NEW, 'w', encoding='utf-8', newline='').write(source)
if os.path.exists(OLD):
    os.remove(OLD)
print('wrote %s (%d bytes) and removed the single-operation class' % (NEW, len(source)))
