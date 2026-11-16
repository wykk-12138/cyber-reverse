namespace Cybersole.Stores.Payments;

/// <summary>
/// The three payment hosts the coverage table could not match to anything, and what they actually carry.
///
/// <para>
/// R948. Criterion (f) asks for a coverage table the original's hosts can be checked against item by item. The vendor side
/// is clean -- all twelve hosts are named in source -- but the store side reported three hosts with no registration
/// behind them: api.braintreegateway.com, api.vipps.no and payments.bigcommerce.com. All three are payment hosts rather
/// than shops, which is why no store flow claimed them, and all three carry concrete paths in the image.
/// </para>
///
/// <code>
/// Braintree   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account
///             /merchants/rfbkw27jcwmw2xgp/client_api/v1/paypal_hermes/create_payment_resource
///             assets.braintreegateway.com
/// Vipps       /adyen-card-enrollment/initiate · /commit
///             /checkout-frontend/session/
/// BigCommerce /api/public/v1/orders/payments
/// </code>
///
/// <para>
/// <b>What is recorded and what is not.</b> The paths and the merchant id are the image's, verbatim. Which shop each one
/// serves is not: nothing in these strings names a store, so a caller supplies it. And the Vipps strings sit beside
/// "VippsNo" and "3DS Unsupported (VippsNo)", which read as a locale's display name and a status message -- recorded as
/// wording rather than interpreted, since "No" could be Norway and could be the word no.
/// </para>
/// </summary>
public static class PaymentHostGaps
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

        /// <summary>Full URLs, in the order the image lists the two enrollment paths.</summary>
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

    /// <summary>
    /// The three hosts, so a coverage report can name what it could not match rather than leaving it as a count.
    /// </summary>
    internal static readonly string[] Hosts =
    {
        "api.braintreegateway.com", "api.vipps.no", "payments.bigcommerce.com",
    };

    /// <summary>True when a host is one of the three payment hosts rather than a shop.</summary>
    public static bool IsPaymentHost(string? host) =>
        !string.IsNullOrEmpty(host) && Hosts.Contains(host, StringComparer.OrdinalIgnoreCase);
}