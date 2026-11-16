namespace Cybersole.Stores.Flows;

/// <summary>
/// Vans's REST endpoints, recovered from the image's string table in R898.
///
/// <para>
/// <b>What is observed.</b> Six path literals exist in the image under the three families <c>cart/v1</c>,
/// <c>cart/v2</c> and <c>products/v2</c>: the two cart reads, the two order submissions, and the product list. They
/// are listed verbatim below and each appears exactly as written.
/// </para>
///
/// <para>
/// <b>What is inference.</b> That these six belong to Vans. The association is at <i>family</i> level: R893 found
/// <c>/cart/v1/</c>, <c>/cart/v2/</c> and <c>/products/v2/</c> sharing a literal with <c>www.vans.com</c>, so the
/// families are Vans's. But none of these six paths has a host in its own literal — which is why this file separates
/// the two claims. A different store on the same platform could use the same paths, and nothing recovered says it
/// does not.
/// </para>
///
/// <para>
/// <b>What is absent.</b> The request bodies and the response shapes. Nothing here is called by a step, because a
/// constant without an evidenced body would be an endpoint the flow appears to reach and cannot actually use
/// (R850's rule, applied again in R890 for the two store_ticket paths).
/// </para>
///
/// <para>
/// Reproof: the paths come from scanning the image's strings for <c>/(?:cart|products)/v\d+/...</c> and reading back
/// every match. The families' hosts come from R893's co-occurrence scan.
/// </para>
/// </summary>
public static class VansEndpoints
{
    /// <summary>Cart read on v1. Trailing slash is part of the literal.</summary>
    public const string CartV1 = "/cart/v1/cart/";

    /// <summary>
    /// The v1 cart with an item already in it. The locale is a query parameter here rather than a path segment,
    /// unlike the Demandware controllers in <see cref="DemandwareControllers"/>.
    /// </summary>
    public const string CartWithItemV1 = "/cart/v1/cartWithItem?locale=";

    /// <summary>Cart read on v2. Both versions exist in the image; which one a given step uses is unknown.</summary>
    public const string CartV2 = "/cart/v2/cart/";

    /// <summary>Order submission on v2, path form.</summary>
    public const string OrderV2 = "/cart/v2/checkout/order/";

    /// <summary>Order submission on v2, query form — the same endpoint reached with a locale.</summary>
    public const string OrderV2WithLocale = "/cart/v2/checkout/order?locale=";

    /// <summary>The product list. Note the doubled word, which is in the image rather than a typo here.</summary>
    public const string ProductsV2 = "/products/v2/products/";

    /// <summary>Every path above, for tests and for a coverage check that needs to enumerate them.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CartV1, CartWithItemV1, CartV2, OrderV2, OrderV2WithLocale, ProductsV2,
    };

    /// <summary>
    /// The host the families are associated with. Recorded here because the association is family-level, so this is
    /// the reason the paths are filed under Vans and also the limit of that claim.
    /// </summary>
    public const string FamilyHost = "www.vans.com";

    /// <summary>
    /// True for every path in <see cref="All"/>. Named so a caller has to read the class comment before using the
    /// paths as though their ownership were established.
    /// </summary>
    public const bool OwnershipIsInference = true;
}
