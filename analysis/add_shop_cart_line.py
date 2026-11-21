"""R1355: the cartLineItemSet sender carries the Shop app's whole failure vocabulary.

The document's own function has no literals — it is a state machine. The operation name does have a referencer, and
that function, sub_140D11730 (1049 bytes), is where the interesting part is:

    Password page up
    StatusInfo
    The product in the cart does not exist.
    The product in the cart is out of stock.
    The shopify shop of this cart is not eligible
    cannot be fulfilled
    tries exhausted on cart
    cart / data / id / white

So this is the Shop app's add-to-cart handler, and those are the outcomes it distinguishes: a password-protected
storefront, a product that no longer exists, one out of stock, a shop that is not eligible for the app, an
unfulfillable cart, and an exhaustion message. Copying the document without them would reproduce the request and
none of the behaviour.

The variables are $brokerId, $variantId, $quantity and $attribution — brokerId again, which is what ties this to the
Shop app family rather than to a storefront.

Usage: python analysis/add_shop_cart_line.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470CE874
OUT = 'replica/src/Cybersole.Stores/Flows/ShopAppCart.cs'
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
print('cartLineItemSet: %d chars' % len(document))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['cart_line_item_set'] = document
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
/// The Shop app's add-to-cart — <c>cartLineItemSet</c> — and the outcomes its handler distinguishes.
///
/// <para>
/// <b>Observed</b> (R1355): the document is 1255 characters at 0x1470CE874 and declares <c>$brokerId</c>,
/// <c>$variantId</c>, <c>$quantity</c> and <c>$attribution</c>; <c>brokerId</c> is what ties it to the Shop app.
/// </para>
///
/// <para>
/// <b>Observed:</b> the function that references the operation name — <c>sub_140D11730</c>, 1049 bytes — carries
/// the messages this class publishes: "Password page up", "The product in the cart does not exist.",
/// "The product in the cart is out of stock.", "The shopify shop of this cart is not eligible",
/// "cannot be fulfilled" and "tries exhausted on cart". They are the behaviour that belongs with the request;
/// copying the document alone would reproduce the call and none of the reaction.
/// </para>
/// </summary>
public static class ShopAppCart
{
    /// <summary>The operation name, 0x146FC1A38.</summary>
    public const string OperationName = "cartLineItemSet";

    /// <summary>The document, 1255 characters from 0x1470CE874.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The four variables the document declares.</summary>
    public static readonly string[] DeclaredVariables = { "brokerId", "variantId", "quantity", "attribution" };

    /// <summary>A storefront behind a password page — the cart cannot be touched.</summary>
    public const string PasswordPageMessage = "Password page up";

    /// <summary>The product is gone from the shop.</summary>
    public const string ProductMissingMessage = "The product in the cart does not exist.";

    /// <summary>The product is out of stock.</summary>
    public const string ProductOutOfStockMessage = "The product in the cart is out of stock.";

    /// <summary>The Shopify shop is not eligible for the app's cart.</summary>
    public const string ShopNotEligibleMessage = "The shopify shop of this cart is not eligible";

    /// <summary>Part of the cart cannot be fulfilled.</summary>
    public const string CannotBeFulfilledMessage = "cannot be fulfilled";

    /// <summary>The handler gave up after its attempts.</summary>
    public const string TriesExhaustedMessage = "tries exhausted on cart";

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Add a line to the Shop app's cart. Every message the handler distinguishes becomes a failed step with the
    /// same words, so a run reads the same way here as in the image.
    /// </summary>
    public static async Task<(JObject? Cart, string Error)> AddLineAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables is null || variables["brokerId"] is null || string.IsNullOrEmpty(variables["brokerId"]!.ToString()))
            return (null, "shop-app-cart: no brokerId — the operation is keyed by it");
        if (variables["variantId"] is null || string.IsNullOrEmpty(variables["variantId"]!.ToString()))
            return (null, "shop-app-cart: no variantId to add");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? ShopAppProduct.Url, Envelope(variables), "shop-app-cart", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "shop-app-cart: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "shop-app-cart: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var cart = reply["data"]?["cartLineItemSet"]?["cart"] as JObject ?? reply["data"]?["cart"] as JObject;
            if (cart is null) return (null, "shop-app-cart: no cart in reply");

            var status = cart["statusInfo"]?.ToString() ?? reply["data"]?["statusInfo"]?.ToString();
            if (!string.IsNullOrEmpty(status) && status!.Contains("PASSWORD", StringComparison.OrdinalIgnoreCase))
                return (null, PasswordPageMessage);

            var errors = cart["errors"] as JArray ?? reply["data"]?["errors"] as JArray;
            if (errors is not null)
            {
                foreach (var error in errors)
                {
                    var message = error?["message"]?.ToString() ?? string.Empty;
                    if (message.Length == 0) continue;
                    if (message.Contains("out of stock", StringComparison.OrdinalIgnoreCase))
                        return (null, ProductOutOfStockMessage);
                    if (message.Contains("does not exist", StringComparison.OrdinalIgnoreCase))
                        return (null, ProductMissingMessage);
                    if (message.Contains("not eligible", StringComparison.OrdinalIgnoreCase))
                        return (null, ShopNotEligibleMessage);
                    if (message.Contains("fulfil", StringComparison.OrdinalIgnoreCase))
                        return (null, CannotBeFulfilledMessage);
                    return (null, message);
                }
            }

            return (cart, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "shop-app-cart: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
