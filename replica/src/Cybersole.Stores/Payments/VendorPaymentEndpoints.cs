namespace Cybersole.Stores.Payments;

/// <summary>
/// The three vendor payment endpoints whose strings the image carries but which no store flow claims.
///
/// <para>
/// <b>History.</b> This was <c>PaymentHostGaps</c> (R948), and the name said "gaps" because the coverage table had three
/// hosts it could not match to a registration. R1269 renamed it: the paths, hosts and merchant id are runtime protocol
/// facts that a payment step would actually use, while the two coverage-report helpers it also carried
/// (<c>Hosts</c> and <c>IsPaymentHost</c>) were ledger logic, and the product-code rule keeps ledgers out of
/// <c>src</c>. The helpers are gone; the facts stayed, under a name that describes what they are.
/// </para>
///
/// <para>
/// <b>Observed</b>: every string below is the image's, verbatim — the Braintree merchant id
/// <c>rfbkw27jcwmw2xgp</c> with its two client-side paths, the Vipps enrolment pair plus its checkout session path,
/// and BigCommerce's single order-payment path. <b>Unknown</b>: which shop each one serves. Nothing in these strings
/// names a store, so a caller supplies it; the Vipps strings <c>VippsNo</c> and <c>3DS Unsupported (VippsNo)</c> sit
/// beside the paths and are recorded as wording rather than interpreted, since "No" could be Norway or the word no.
/// </para>
/// </summary>
public static class VendorPaymentEndpoints
{
    /// <summary>Braintree, including the merchant id the image hard-codes.</summary>
    public static class Braintree
    {
        /// <summary>The merchant id, as the image spells it. Per-merchant rather than per-vendor, so it belongs to one shop.</summary>
        public const string MerchantId = "rfbkw27jcwmw2xgp";

        /// <summary>The two client-side endpoints, both under that merchant.</summary>
        public static readonly IReadOnlyList<string> Paths = new[]
        {
            "/merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account",
            "/merchants/rfbkw27jcwmw2xgp/client_api/v1/paypal_hermes/create_payment_resource",
        };

        /// <summary>The asset host, which is a second host for the same vendor and needs no path.</summary>
        public const string AssetHost = "https://assets.braintreegateway.com";

        /// <summary>The API host the paths hang off.</summary>
        public const string ApiHost = "https://api.braintreegateway.com";

        /// <summary>The full URL for a path, so a caller does not concatenate by hand.</summary>
        public static string UrlFor(string path) => ApiHost + path;
    }

    /// <summary>Vipps, whose strings suggest a Norwegian locale but do not say so.</summary>
    public static class Vipps
    {
        /// <summary>The three paths, verbatim.</summary>
        public static readonly IReadOnlyList<string> Paths = new[]
        {
            "/adyen-card-enrollment/initiate",
            "/adyen-card-enrollment/commit",
            "/checkout-frontend/session/",
        };

        /// <summary>The API host.</summary>
        public const string ApiHost = "https://api.vipps.no";

        /// <summary>A second host, for the checkout frontend.</summary>
        public const string CheckoutHost = "checkout.vipps.no";

        /// <summary>The two other strings, recorded as the image's wording.</summary>
        public static readonly IReadOnlyList<string> Messages = new[]
        {
            "VippsNo", "3DS Unsupported (VippsNo)",
        };

        /// <summary>Full URLs, in the order the image lists the two enrolment paths.</summary>
        public static IReadOnlyList<string> Urls() => new[]
        {
            ApiHost + "/adyen-card-enrollment/initiate",
            ApiHost + "/adyen-card-enrollment/commit",
        };
    }

    /// <summary>BigCommerce, one endpoint for recording a payment against an order.</summary>
    public static class BigCommerce
    {
        /// <summary>The single path the image carries.</summary>
        public const string PaymentsPath = "/api/public/v1/orders/payments";

        /// <summary>The host.</summary>
        public const string Host = "https://payments.bigcommerce.com";

        /// <summary>The full URL.</summary>
        public static string Url() => Host + PaymentsPath;
    }
}
