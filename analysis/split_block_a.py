"""R1349: block A is a region, not a family — the variables say which is which.

Last round treated block A as one thing because its fifteen operations share an address range. Reading their
documents breaks that up:

    cartApiObjectCreate      $input + six include flags + country + metafieldsIdentifiers   Shopify Storefront
    createCart               $lines, $buyerIdentity, $attributes, $country, $language       Shopify Storefront
    removeLineItemFromCart   $cartId, $lineItemId, $version, $quantity, $locale             Shopify Storefront
    setBillingAddress        $action: SetCartBillingAddress!, $locale, $preferredLocale      the Highsnobiety family
    createCheckout           $variantId, $location, $attributes, $recaptchaToken            something else again

setBillingAddress declares exactly the shape setCustomerEmail declares — an action object, a locale and a
preferredLocale — which is the tm-api family, not Shopify. And createCheckout carries a recaptcha token, so it is
a third thing.

So three of the five join the storefront class as its own operations, and setBillingAddress becomes the billing step
of the store it actually belongs to. An address cluster is a lead; the variable signature is the evidence.

Usage: python analysis/split_block_a.py
"""
import io
import json
import os

DOCS = 'analysis/.shopify_storefront_docs.json'
OLD = 'replica/src/Cybersole.Stores/Flows/ShopifyCartCreate.cs'
NEW = 'replica/src/Cybersole.Stores/Flows/ShopifyStorefrontQueries.cs'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

documents = json.loads(io.open(DOCS, encoding='utf-8').read())


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
/// The Shopify Storefront mutations the image carries.
///
/// <para>
/// <b>Observed</b> (R1348, R1349): three documents whose variable signatures are Storefront's own —
/// <c>cartApiObjectCreate</c> (5876 characters, 0x1470EF5FC), <c>createCart</c> (1622, 0x1470F260C) and
/// <c>removeLineItemFromCart</c> (1553, 0x1470F4C84) — posted to <c>api/&lt;version&gt;/graphql.json</c> with a
/// Storefront access token header.
/// </para>
///
/// <para>
/// <b>Why only three:</b> the other documents in that address range are not Storefront. <c>setBillingAddress</c>
/// declares an action object plus two locales, which is the shape the Highsnobiety family uses, and
/// <c>createCheckout</c> carries a recaptcha token. An address cluster is a lead; the variable signature is the
/// evidence.
/// </para>
///
/// <para>
/// <b>Not reproduced:</b> the Storefront access token the image holds as a literal. A credential copied into source
/// is a credential that leaks, so the caller supplies its own.
/// </para>
/// </summary>
public static class ShopifyStorefrontQueries
{
    /// <summary>The API version the senders address.</summary>
    public const string ApiVersion = "2025-04";

    /// <summary>cartApiObjectCreate, 5876 characters from 0x1470EF5FC.</summary>
    public const string CartApiObjectCreate = "__CART_OBJECT__";

    /// <summary>createCart, 1622 characters from 0x1470F260C.</summary>
    public const string CreateCart = "__CREATE_CART__";

    /// <summary>removeLineItemFromCart, 1553 characters from 0x1470F4C84.</summary>
    public const string RemoveLineItemFromCart = "__REMOVE_LINE__";

    /// <summary>The variables each document declares.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> Declared = new Dictionary<string, string[]>
    {
        ["cartApiObjectCreate"] = new[]
        {
            "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
            "includeProductTags", "includeCustomerTags", "country", "metafieldsIdentifiers",
        },
        ["createCart"] = new[] { "lines", "buyerIdentity", "attributes", "country", "language" },
        ["removeLineItemFromCart"] = new[] { "cartId", "lineItemId", "version", "quantity", "locale" },
    };

    /// <summary>The variables each sender fills. <c>metafieldsIdentifiers</c> is declared and left out.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> SenderFills = new Dictionary<string, string[]>
    {
        ["cartApiObjectCreate"] = new[]
        {
            "input", "includeInventory", "includeStoreAvailability", "includeSellingPlans",
            "includeProductTags", "includeCustomerTags", "country",
        },
        ["createCart"] = new[] { "lines", "buyerIdentity", "attributes", "country", "language" },
        ["removeLineItemFromCart"] = new[] { "cartId", "lineItemId", "version", "quantity", "locale" },
    };

    /// <summary>The document for an operation, or null when it is not one of the three.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "cartApiObjectCreate" => CartApiObjectCreate,
        "createCart" => CreateCart,
        "removeLineItemFromCart" => RemoveLineItemFromCart,
        _ => null,
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(string operation, JObject variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = DocumentFor(operation) ?? throw new ArgumentOutOfRangeException(nameof(operation)),
        ["variables"] = variables,
    };

    /// <summary>
    /// Post one Storefront operation. <paramref name="host"/> and <paramref name="token"/> are the caller's — the
    /// image's own token is a credential rather than a fact to copy.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? host, string? token, string operation, JObject variables,
        CancellationToken ct, string? version = null)
    {
        if (string.IsNullOrWhiteSpace(host)) return (null, "shopify-storefront: no store host");
        if (string.IsNullOrWhiteSpace(token)) return (null, "shopify-storefront: no storefront access token");

        var document = DocumentFor(operation);
        if (document is null) return (null, "shopify-storefront: unknown operation " + operation);

        foreach (var property in variables.Properties())
        {
            if (Array.IndexOf(Declared[operation], property.Name) >= 0) continue;
            return (null, "shopify-storefront: " + operation + " does not declare $" + property.Name);
        }

        var url = ShopifyGraphQl.Endpoint(host!, version ?? ApiVersion);
        c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token!;

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, variables), "shopify-" + operation, ct)
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
          .replace('__CART_OBJECT__', escape_literal(documents['cart_api_object_create']))
          .replace('__CREATE_CART__', escape_literal(documents['create_cart']))
          .replace('__REMOVE_LINE__', escape_literal(documents['remove_line_item_from_cart'])))

io.open(NEW, 'w', encoding='utf-8', newline='').write(source)
if os.path.exists(OLD):
    os.remove(OLD)
print('wrote %s and removed the single-operation class' % NEW)

# setBillingAddress belongs to the Highsnobiety family: an action object plus two locales.
flows = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'SetBillingAddressDocument' not in flows:
    anchor = "    /// <summary>The order confirmation query, 4825 characters from 0x14713E1FC.</summary>"
    if flows.count(anchor) != 1:
        raise SystemExit('constant anchor found %d times' % flows.count(anchor))

    constants = '''    /// <summary>
    /// The billing mutation, 4989 characters from 0x1470F5B24. It declares an action object and two locales —
    /// the shape this family uses, not Shopify Storefront's, which is how it was attributed (R1349).
    /// </summary>
    public const string SetBillingAddressDocument =
        "%s";

''' % escape_literal(documents['set_billing_address'])

    flows = flows.replace(anchor, constants + anchor)

    step_anchor = '''    /// <summary>
    /// Read the order confirmation. The query is keyed by the Stripe payment-intent id the image's own sender at
    /// 0x140B574F0 passes, with the two locale fields beside it.
    /// </summary>'''
    if flows.count(step_anchor) != 1:
        raise SystemExit('step anchor found %d times' % flows.count(step_anchor))

    step = '''    /// <summary>
    /// Submit billing through the observed mutation; the payload is the caller's SetCartBillingAddress object,
    /// which the image never spells out.
    /// </summary>
    public override async Task<StepOutcome> SubmitBillingAsync(FlowContext c, CancellationToken ct)
    {
        var action = ActionFrom(c, "highsnobiety.billingAction", "submit billing", out var failure);
        if (action is null) return failure!.Value;

        var locale = Locale(c);
        var variables = new JObject
        {
            ["action"] = action,
            ["locale"] = locale,
            ["preferredLocale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.preferredLocale") ?? locale,
        };

        var host = c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;
        var body = new JObject
        {
            ["operationName"] = "setBillingAddress",
            ["query"] = SetBillingAddressDocument,
            ["variables"] = variables,
        };

        var res = await PostJsonAsync(c, host, body.ToString(Newtonsoft.Json.Formatting.None),
            "hs-billing", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("highsnobiety billing failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"highsnobiety billing HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["billing"] = res.Body;
        return StepOutcome.Success();
    }

'''

    flows = flows.replace(step_anchor, step + step_anchor)
    io.open(FLOWS, 'w', encoding='utf-8', newline='').write(flows)
    print('added setBillingAddress to the Highsnobiety family')
