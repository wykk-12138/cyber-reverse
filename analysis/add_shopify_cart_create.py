"""R1348: block A is the Shopify Storefront API, and its largest mutation is cartApiObjectCreate.

One sender from each block answers the question the cluster could not.

Block A — sub_140D1B380 (2258 bytes) — carries api/2025-04/graphql.json, buyerIdentity, customerAccessToken,
gid://shopify/ProductVariant/, includeCustomerTags, includeSellingPlans, includeStoreAvailability and a storefront
access token written out as a literal. That is the Shopify Storefront API, and the replica already composes exactly
that path in ShopifyGraphQl.Endpoint, so the fifteen operations of block A belong beside the storefront machinery
rather than in a class of their own.

Block B — sub_140E55F90 (960 bytes) — has no host at all: application/json, getCart, key, locale, operationName,
query, variables. Same shape as the api/graphql family, still unattributed.

The document declares eight variables — the seven flags its sender sets, plus metafieldsIdentifiers.

Usage: python analysis/add_shopify_cart_create.py
"""
import io
import json

DOCS = 'analysis/.shopify_storefront_docs.json'
OUT = 'replica/src/Cybersole.Stores/Flows/ShopifyCartCreate.cs'

document = json.loads(io.open(DOCS, encoding='utf-8').read())['cart_api_object_create']


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
/// The Shopify Storefront cart creation — <c>cartApiObjectCreate</c>.
///
/// <para>
/// <b>Observed</b> (R1348): the sender at <c>sub_140D1B380</c> (2258 bytes) posts to
/// <c>api/2025-04/graphql.json</c> with <c>buyerIdentity</c>, <c>customerAccessToken</c>,
/// <c>gid://shopify/ProductVariant/</c> and the five <c>include*</c> flags — the Storefront API the replica already
/// addresses through <see cref="ShopifyGraphQl.Endpoint"/>. The document is 5876 characters at 0x1470EF5FC and
/// declares <c>$input</c> plus seven flags; the sender sets all but <c>metafieldsIdentifiers</c>.
/// </para>
///
/// <para>
/// <b>Not reproduced:</b> the storefront access token that sits in the image as a literal
/// (<c>e927ea99…</c>). It is a credential, and a credential copied into source is a credential that leaks; the
/// caller supplies its own.
/// </para>
/// </summary>
public static class ShopifyCartCreate
{
    /// <summary>The operation name, from the document's own header.</summary>
    public const string OperationName = "cartApiObjectCreate";

    /// <summary>The API version the sender addresses.</summary>
    public const string ApiVersion = "2025-04";

    /// <summary>The document, 5876 characters from 0x1470EF5FC.</summary>
    public const string Document =
        "__DOCUMENT__";

    /// <summary>The eight variables the document declares.</summary>
    public static readonly string[] DeclaredVariables =
    {
        "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
        "includeProductTags", "includeCustomerTags", "country", "metafieldsIdentifiers",
    };

    /// <summary>
    /// The variables the sender fills. <c>metafieldsIdentifiers</c> is declared and left out, so it stays the
    /// caller's to add when a store asks for metafields.
    /// </summary>
    public static readonly string[] SenderVariables =
    {
        "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
        "includeProductTags", "includeCustomerTags", "country",
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Create a cart. <paramref name="host"/> is the store's hostname and <paramref name="token"/> its Storefront
    /// access token — both are the caller's, because the image's own copy is a credential rather than a fact.
    /// </summary>
    public static async Task<(string? CartId, string Error)> CreateAsync(
        FlowContext c, string? host, string? token, JObject variables, CancellationToken ct, string? version = null)
    {
        if (string.IsNullOrWhiteSpace(host)) return (null, "shopify-cart: no store host");
        if (string.IsNullOrWhiteSpace(token)) return (null, "shopify-cart: no storefront access token");
        if (variables is null || variables["input"] is null)
            return (null, "shopify-cart: no $input — the document requires a CartInput");

        var url = ShopifyGraphQl.Endpoint(host!, version ?? ApiVersion);
        c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token!;

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(variables), "shopify-cart-create", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "shopify-cart: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "shopify-cart: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var cart = reply["data"]?["cartCreate"]?["cart"];
            var cartId = cart?["id"]?.ToString();
            return string.IsNullOrEmpty(cartId)
                ? (null, "shopify-cart: no cart in reply")
                : (cartId, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "shopify-cart: " + ex.GetType().Name);
        }
    }
}
'''.replace('__DOCUMENT__', escape_literal(document))

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s (%d bytes)' % (OUT, len(source)))
