namespace Cybersole.Stores.Flows;

/// <summary>
/// The checkout route shapes the image carries, as opposed to the two the replica had assumed.
///
/// <para>
/// <b>Observed</b> (R1255, from the full string dump): the image holds a large checkout family, of which these are the
/// same-origin page and action shapes — <c>/checkout/</c>, <c>/checkout/?stage=shipping</c>,
/// <c>/checkout/?stage=payment</c>, <c>/checkout/?stage=placeOrder</c>, <c>/checkout/?step=payment</c>,
/// <c>/checkout/cart/</c>, <c>/checkout/cart/addcoupon/?couponCode=</c>, <c>/checkout/cart/couponPost/</c>,
/// <c>/checkout/confirmation</c>, <c>/checkout/success</c>, <c>/checkout/onepage/success/</c>,
/// <c>/checkout/return</c>, <c>/checkout/services/placeorder/</c>,
/// <c>/checkout/shippingservices/submitshipping/</c> and <c>/checkout/sidebar/removeItem/</c>.
/// </para>
///
/// <para>
/// <b>Not observed</b>: <c>/checkout/complete</c> and <c>/checkout/#payment</c>, the two the replica had used. The
/// image expresses the same ideas as <c>/checkout/success</c> and <c>/checkout/?stage=payment</c>, but with a query
/// stage rather than a fragment — a fragment is resolved client-side and never reaches the server, so a storefront
/// whose page is keyed by <c>?stage=</c> cannot be reached by <c>#payment</c>.
/// </para>
///
/// <para>
/// <b>Unknown</b>: which storefront uses which of these, and whether a given flow's page step belongs to the
/// <c>?stage=</c> family or the <c>?step=</c> one. Dispatch is not observable (R1219), so the shapes are exposed and
/// the existing call sites keep their own paths, annotated instead of rewritten.
/// </para>
/// </summary>
public static class CheckoutRoutes
{
    public const string Root = "/checkout/";

    /// <summary>The three page stages the image keys by query, plus the sibling spelling with <c>step</c>.</summary>
    public const string StageShipping = "/checkout/?stage=shipping";

    public const string StagePayment = "/checkout/?stage=payment";

    public const string StagePlaceOrder = "/checkout/?stage=placeOrder";

    public const string StepPayment = "/checkout/?step=payment";

    /// <summary>Cart-scoped actions.</summary>
    public const string Cart = "/checkout/cart/";

    public const string CartAddCoupon = "/checkout/cart/addcoupon/?couponCode=";

    public const string CartCouponPost = "/checkout/cart/couponPost/";

    public const string CartRemoveItem = "/checkout/sidebar/removeItem/";

    /// <summary>Terminal pages — the image's spelling of what the replica called <c>/checkout/complete</c>.</summary>
    public const string Confirmation = "/checkout/confirmation";

    public const string Success = "/checkout/success";

    public const string OnePageSuccess = "/checkout/onepage/success/";

    public const string Return = "/checkout/return";

    /// <summary>The Demandware-style controller pair, which the same dump carries beside the rest.</summary>
    public const string ServicesPlaceOrder = "/checkout/services/placeorder/";

    public const string ShippingServicesSubmitShipping = "/checkout/shippingservices/submitshipping/";
}
