namespace Cybersole.Stores.Flows;

/// <summary>
/// Vans's REST endpoints, recovered from the image's string table in R898 and corrected in R899.
///
/// <para>
/// <b>What is observed.</b> The image holds five complete URLs, each carrying the host and the path in one literal:
/// <c>https://www.vans.com/api/cart/v1/cartWithItem?locale=</c>, <c>.../api/cart/v2/cart/</c>,
/// <c>.../api/cart/v2/checkout/order/</c>, <c>.../api/cart/v2/checkout/order?locale=</c> and
/// <c>.../api/products/v2/products/</c>. Because the host and the path share a literal, the paths' ownership is
/// observed rather than inferred — which is the opposite of what R898 recorded.
/// </para>
///
/// <para>
/// <b>What R898 got wrong.</b> It recovered the same paths without the <c>/api</c> prefix, because it scanned for
/// <c>/(cart|products)/vN/</c> and that pattern starts the match at the segment after <c>/api</c>. The constants were
/// therefore paths no Vans server answers. The prefix is part of every one of them and is now in the literals below.
/// </para>
///
/// <para>
/// <b>What is still absent.</b> The request bodies and the response shapes, so no step calls these. A constant
/// without an evidenced body would be an endpoint the flow appears to reach and cannot use (R850).
/// </para>
/// </summary>
public static class VansEndpoints
{
    /// <summary>Cart read on v1, with an item. The locale is a query parameter rather than a path segment.</summary>
    public const string CartWithItemV1 = "/api/cart/v1/cartWithItem?locale=";

    /// <summary>Cart read on v2. Both versions exist in the image; which one a given step uses is unknown.</summary>
    public const string CartV2 = "/api/cart/v2/cart/";

    /// <summary>Order submission on v2, path form.</summary>
    public const string OrderV2 = "/api/cart/v2/checkout/order/";

    /// <summary>Order submission on v2, query form — the same endpoint reached with a locale.</summary>
    public const string OrderV2WithLocale = "/api/cart/v2/checkout/order?locale=";

    /// <summary>The product list. Note the doubled word, which is in the image rather than a typo here.</summary>
    public const string ProductsV2 = "/api/products/v2/products/";

    /// <summary>
    /// The fifth URL, <c>.../api/cart/v1/cart/</c>, kept as a constant of its own: v1 has both a bare cart read and
    /// the withItem form, exactly as v2 does.
    /// </summary>
    public const string CartV1 = "/api/cart/v1/cart/";

    /// <summary>Every path above, for tests and for a coverage check that needs to enumerate them.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CartV1, CartWithItemV1, CartV2, OrderV2, OrderV2WithLocale, ProductsV2,
    };

    /// <summary>The host, which shares a literal with each path and is therefore observed rather than assigned.</summary>
    public const string FamilyHost = "www.vans.com";

    /// <summary>
    /// False, and it was true one round earlier.
    ///
    /// <para>
    /// R898 set this because the six paths it recovered had no host in their own literals. That was an artefact of the
    /// pattern it used: scanning for <c>/(cart|products)/vN/</c> matched the bare segment and never saw the
    /// <c>https://www.vans.com</c> in front of it. Searching for the host and the path together found five literals
    /// holding both, so the ownership question this flag was recording is settled.
    /// </para>
    /// </summary>
    public const bool OwnershipIsInference = false;
}
