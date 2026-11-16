namespace Cybersole.Stores.Flows;

/// <summary>
/// Every Nike API base URL the binary contains, read out of the 5.18.32 image with
/// <c>find_regex "api\.nike\.com"</c> in R87. Twenty strings, verbatim, in address order.
///
/// <para>
/// This exists because the replica's Nike flow was calling <b>two URL families the binary does not
/// contain at all</b> — <c>buy/carts/v2/…</c> and <c>buy/orders/v2/…</c> — while the real checkout
/// surface is a single <c>buy/checkouts/v3/</c> resource that each step writes to. The list below is
/// the ground truth for what exists; the per-step mapping is still open (see docs/NIKE_PARITY.md).
/// </para>
///
/// <para>
/// Two endpoints are jobs: the API answers <c>202</c> with a job id and the client polls
/// <c>&lt;name&gt;_jobs/</c> for the result. Both halves are listed because both are real.
/// </para>
/// </summary>
public static class NikeEndpoints
{
    /// <summary>Checkout preview (no order placed) — POST creates, later steps write to the id.</summary>
    public const string CheckoutPreviews = "https://api.nike.com/buy/checkout_previews/v3/";

    /// <summary>The polling half of the preview above.</summary>
    public const string CheckoutPreviewsJobs = "https://api.nike.com/buy/checkout_previews_jobs/v3/";

    /// <summary>A real checkout — this is the resource every checkout step writes to.</summary>
    public const string Checkouts = "https://api.nike.com/buy/checkouts/v3/";

    /// <summary>The polling half of the checkout above.</summary>
    public const string CheckoutsJobs = "https://api.nike.com/buy/checkouts_jobs/v3/";

    /// <summary>Shipping-rate offerings, as a job.</summary>
    public const string FulfillmentOfferingsJobs =
        "https://api.nike.com/buy/fulfillment_offerings_jobs/v2/";

    /// <summary>Partner pre-order cart (the basket path).</summary>
    public const string PartnerCartPreorder = "https://api.nike.com/buy/partner_cart_preorder/v2/";

    /// <summary>The polling half of the partner cart above.</summary>
    public const string PartnerCartPreorderJobs =
        "https://api.nike.com/buy/partner_cart_preorder_jobs/v2/";

    /// <summary>Stock check by GTIN — the inventory step.</summary>
    public const string AvailableGtins = "https://api.nike.com/deliver/available_gtins/v3";

    /// <summary>3-D Secure: start an authentication.</summary>
    public const string ThreeDsAuthentications = "https://api.nike.com/payment/3ds_authentications/v3";

    /// <summary>3-D Secure: report the challenge result.</summary>
    public const string ThreeDsResults = "https://api.nike.com/payment/3ds_results/v3";

    /// <summary>Deferred payment forms (Klarna and friends).</summary>
    public const string DeferredPaymentForms =
        "https://api.nike.com/payment/deferred_payment_forms/v1";

    /// <summary>The polling half of the deferred forms above.</summary>
    public const string DeferredPaymentFormsJobs =
        "https://api.nike.com/payment/deferred_payment_forms/v1/jobs/";

    /// <summary>PayPal: the payment details step.</summary>
    public const string PayPalDetails = "https://api.nike.com/payment/paypal_details/v2";

    /// <summary>The polling half of the PayPal details above.</summary>
    public const string PayPalDetailsJobs = "https://api.nike.com/payment/paypal_details/v2/jobs/";

    /// <summary>PayPal: mark the funding source.</summary>
    public const string PayPalMark = "https://api.nike.com/payment/paypal_mark/v2";

    /// <summary>The polling half of the PayPal mark above.</summary>
    public const string PayPalMarkJobs = "https://api.nike.com/payment/paypal_mark/v2/jobs/";

    /// <summary>Payment preview — validates a payment instrument against a checkout.</summary>
    public const string PaymentPreview = "https://api.nike.com/payment/preview/v3";

    /// <summary>The polling half of the payment preview above.</summary>
    public const string PaymentPreviewJobs = "https://api.nike.com/payment/preview/v3/jobs/";

    /// <summary>The product feed — how the monitor and the variant scrape both start.</summary>
    public const string ProductFeedThreads = "https://api.nike.com/product_feed/threads/v2?fields=";

    /// <summary>All twenty, in the order the image lists them.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CheckoutPreviews,
        CheckoutPreviewsJobs,
        Checkouts,
        CheckoutsJobs,
        FulfillmentOfferingsJobs,
        PartnerCartPreorder,
        PartnerCartPreorderJobs,
        AvailableGtins,
        ThreeDsAuthentications,
        ThreeDsResults,
        DeferredPaymentForms,
        DeferredPaymentFormsJobs,
        PayPalDetails,
        PayPalDetailsJobs,
        PayPalMark,
        PayPalMarkJobs,
        PaymentPreview,
        PaymentPreviewJobs,
        ProductFeedThreads,
    };

    /// <summary>True when <paramref name="url"/> starts with one of the twenty.</summary>
    public static bool IsKnown(string? url) =>
        !string.IsNullOrEmpty(url) && All.Any(e => url.StartsWith(e, StringComparison.Ordinal));

    /// <summary>
    /// The order endpoint — <c>https://www.nike.com/gs/checkout-api/api/v5/Order/</c>.
    ///
    /// <para>
    /// Found in R127 while checking a <c>v5/Order/</c> path that had been wrongly attributed to
    /// Scheels. It is Nike's, and it is the answer to a question this session asked repeatedly
    /// (R87: where does an order go?). The host is not <c>api.nike.com</c> but
    /// <c>www.nike.com/gs/checkout-api/api</c> — the guest-checkout proxy — which is why the endpoint
    /// never turned up in the <c>api.nike.com</c> family.
    /// </para>
    /// </summary>
    public const string OrderV5 = "https://www.nike.com/gs/checkout-api/api/v5/Order/";
}
