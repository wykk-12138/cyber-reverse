using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The Shopify identifier block the image carries, with addresses (R203).
///
/// <para>
/// The eight literals sit in two clusters in the string pool, which is why they are recorded in two groups rather than
/// as one header list:
/// </para>
///
/// <code>
/// 0x06f2caf4  X-Shopify-Generated-Cart-Token
/// 0x06f2cb4c  X-Shopify-Storefront-Access-Token
/// 0x07187b04  x-shopify-storefront-access-token      ← the same header, second spelling
///
/// 0x0715a984  shopify-cart
/// 0x0715a9b4  shopify-checkout-client
/// 0x0715a9fc  shopify-checkout-source
/// 0x0715aa44  shopify-identification-signature
/// 0x0715aa9c  shopify-pay.tappaysdk.com
/// </code>
///
/// <para>
/// The second cluster is written in lower case and at even spacing, and three of its entries are what this replica
/// already uses as <b>request trace tags</b> — the short labels that appear in the session log next to each call. That
/// reading is the only one the image supports on its own: a header name would be spelled like the first cluster. It is
/// recorded as an inference, and the two entries whose role is genuinely unresolved
/// (<see cref="IdentificationSignature"/>, and the TapPay host) are not sent anywhere.
/// </para>
/// </summary>
public static class ShopifyHeaders
{
    /// <summary>One literal with the address it was read at.</summary>
    public sealed record Literal(string Value, string Address, string What);

    // ---- the header cluster ----------------------------------------------------------------------------

    /// <summary>Carries the cart token Shopify generates for a cart it created.</summary>
    public const string GeneratedCartToken = "X-Shopify-Generated-Cart-Token";

    /// <summary>The Storefront API token; the flow already sends this one.</summary>
    public const string StorefrontAccessToken = "X-Shopify-Storefront-Access-Token";

    /// <summary>The same header in the image's second spelling (HTTP header names are case-insensitive).</summary>
    public const string StorefrontAccessTokenLower = "x-shopify-storefront-access-token";

    /// <summary>The header cluster, in address order.</summary>
    public static readonly IReadOnlyList<Literal> Headers = new[]
    {
        new Literal(GeneratedCartToken, "0x06f2caf4", "generated cart token"),
        new Literal(StorefrontAccessToken, "0x06f2cb4c", "storefront access token"),
        new Literal(StorefrontAccessTokenLower, "0x07187b04", "the same header, lower-case spelling"),
    };

    // ---- the tag cluster -------------------------------------------------------------------------------

    /// <summary>The cart tag, which the replica already uses verbatim.</summary>
    public const string CartTag = "shopify-cart";

    /// <summary>The checkout client tag.</summary>
    public const string CheckoutClientTag = "shopify-checkout-client";

    /// <summary>The checkout source tag.</summary>
    public const string CheckoutSourceTag = "shopify-checkout-source";

    /// <summary>The identification signature — a field name; the direction is not established by the image.</summary>
    public const string IdentificationSignature = "shopify-identification-signature";

    /// <summary>The TapPay host the image also carries in this cluster.</summary>
    public const string TapPayHost = "shopify-pay.tappaysdk.com";

    /// <summary>The tag cluster, in address order.</summary>
    public static readonly IReadOnlyList<Literal> Tags = new[]
    {
        new Literal(CartTag, "0x0715a984", "cart request tag"),
        new Literal(CheckoutClientTag, "0x0715a9b4", "checkout client tag"),
        new Literal(CheckoutSourceTag, "0x0715a9fc", "checkout source tag"),
        new Literal(IdentificationSignature, "0x0715aa44", "identification signature name (role unresolved)"),
        new Literal(TapPayHost, "0x0715aa9c", "TapPay payment host"),
    };

    /// <summary>Everything above, for a provenance walk.</summary>
    public static IEnumerable<Literal> All => Headers.Concat(Tags);

    /// <summary>
    /// The JS-side field the identification signature belongs to, from the image's own string blob: the checkout form
    /// names its payment fields <c>_paymentToken0_identificationSignature</c> and friends.
    /// </summary>
    public const string SignatureFieldInJs = "_paymentToken0_identificationSignature";

    /// <summary>The three tags the flow may write into its request log.</summary>
    public static readonly IReadOnlyList<string> TraceTags = new[]
    {
        CartTag, CheckoutClientTag, CheckoutSourceTag,
    };
}
