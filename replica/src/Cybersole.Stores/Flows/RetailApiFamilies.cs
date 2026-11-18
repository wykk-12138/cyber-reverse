using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Two more store APIs from the 5.18.32 image, dumped in R103 — John Lewis's BFF and Scheels's
/// Frontastic action hub.
///
/// <para>
/// <b>John Lewis</b> is the interesting shape: the twelve endpoints are spread across <b>four</b>
/// API versions (v1, v2, v3, v4). There is no single base URL — the billing address lives on v1, the
/// payment page on v2, the delivery page on v3 and the delivery address on v4. A flow that pins one
/// version gets three of the four steps wrong.
/// </para>
///
/// <para>
/// <b>Scheels</b> is a Frontastic action hub: every call is
/// <c>apihub.scheels.com/frontastic/action/{area}/{action}</c>. The cart area carries the whole
/// checkout, including two steps a plain cart never has — <c>completeSignifydStepUpCheckout</c> and
/// <c>sendSignifydStepUpCode</c>. Signifyd is a fraud step-up: the order cannot complete until a
/// code is sent and accepted.
/// </para>
/// </summary>
public static class RetailApiFamilies
{
    /// <summary>John Lewis BFF, grouped by the version each step lives on.</summary>
    public static class JohnLewisBff
    {
        public const string Base = "https://checkout.johnlewis.com/bff/";

        public const string BillingAddressV1 = Base + "v1/orderforms/payments/billing-address";
        public const string PaymentPageV2 = Base + "v2/orderforms/payment-page";
        public const string PaymentsV2 = Base + "v2/orderforms/payments";
        public const string OrdersV2 = Base + "v2/orders";
        public const string SessionHandoverV2 = Base + "v2/sessions/web/handover";
        public const string DeliveryDetailsV3 = Base + "v3/orderforms/deliveries/details";
        public const string DeliveryPageV3 = Base + "v3/orderforms/delivery-page";
        public const string PaymentsV3 = Base + "v3/orderforms/payments/";
        public const string GuestCallbackV4 = Base + "v4/callback/guest";

        /// <summary>
        /// The guest login callback the census found outside this table in R127:
        /// <c>https://checkout.johnlewis.com/callback/login/guest?email=</c>. It sits beside the BFF
        /// rather than under it — a different first segment — which is why a scan keyed on
        /// <c>bff/</c> missed it.
        /// </summary>
        public const string GuestLoginCallback = "https://checkout.johnlewis.com/callback/login/guest?email=";
        public const string DeliveriesV4 = Base + "v4/orderforms/deliveries";
        public const string DeliveriesSlashV4 = Base + "v4/orderforms/deliveries/";
        public const string DeliveryAddressV4 = Base + "v4/orderforms/deliveries/delivery-address";

        /// <summary>
        /// The delivery methods, which the image never writes as one literal.
        ///
        /// <para>
        /// R1132: <c>sub_140A3FB10</c> builds it at run time —
        /// <c>sub_141CF62D0(&amp;off_14705DB98, v2, &amp;off_146AB5DD0)</c> — where the first argument is
        /// <c>…/bff/v4/orderforms/deliveries/</c> (0x14705db98) and the third is the suffix
        /// <c>/methods</c> (0x146ab5dd0), and the joined value is what the GET call receives. So the
        /// endpoint is <c>…/deliveries/methods</c>: a census keyed on single literals can never see it,
        /// and the trailing slash on the base is what makes the join come out right.
        /// </para>
        /// </summary>
        public const string DeliveryMethodsV4 = DeliveriesSlashV4 + "methods";
        // R1137: listed in All as well -- the pair map requires every paired target to be a
        // member, and a derived endpoint is still an endpoint of this family.

        /// <summary>
        /// The checkout walk, in the order the image's own steps run: hand over the session, the guest
        /// callback, the delivery page, the address, the confirm, the methods read, the method submit,
        /// the payment page, the payment, the billing address, the order.
        ///
        /// <para>
        /// R1141 reordered this. It had listed the body-less confirm (step 28) before the address that
        /// it confirms (step 27), put the delivery page (step 26) after both, and left the methods read
        /// (step 29) out altogether. The ordinals come from the image's state-machine enumeration
        /// (d__20 ... d__39, R1135) and the pairings from R1136-R1140, so this is the same ordering the
        /// image executes rather than a plausible sequence.
        /// </para>
        /// </summary>
        public static readonly IReadOnlyList<string> Chain = new[]
        {
            SessionHandoverV2, GuestCallbackV4, DeliveryPageV3, DeliveryAddressV4, DeliveriesV4,
            DeliveryMethodsV4, DeliveryDetailsV3, PaymentPageV2, PaymentsV2, BillingAddressV1, OrdersV2,
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            BillingAddressV1, PaymentPageV2, PaymentsV2, OrdersV2, SessionHandoverV2,
            DeliveryDetailsV3, DeliveryPageV3, PaymentsV3,
            GuestCallbackV4, GuestLoginCallback, DeliveriesV4, DeliveriesSlashV4,
        DeliveryAddressV4,
        DeliveryMethodsV4,   // R1137: derived (.../deliveries/ + methods); listed so the pair map holds
        };

        /// <summary>How many steps live on each version — the fact a single-base-URL flow gets wrong.</summary>
        public static IReadOnlyDictionary<string, int> StepsPerVersion() => new Dictionary<string, int>
        {
            ["v1"] = All.Count(a => a.Contains("/v1/", System.StringComparison.Ordinal)),
            ["v2"] = All.Count(a => a.Contains("/v2/", System.StringComparison.Ordinal)),
            ["v3"] = All.Count(a => a.Contains("/v3/", System.StringComparison.Ordinal)),
            ["v4"] = All.Count(a => a.Contains("/v4/", System.StringComparison.Ordinal)),
        };
    }

    /// <summary>Scheels Frontastic action hub.</summary>
    public static class ScheelsFrontastic
    {
        public const string Base = "https://apihub.scheels.com/frontastic/action/";

        public const string GetAccount = Base + "account/getAccount";
        public const string Login = Base + "account/login";
        public const string Register = Base + "account/register";
        public const string RequestReset = Base + "account/requestReset";
        public const string Reset = Base + "account/reset";

        public const string GetProduct = Base + "product/getProduct";

        public const string AddToCart = Base + "cart/addToCart";
        public const string UpdateCart = Base + "cart/updateCart";
        public const string RemoveLineItem = Base + "cart/removeLineItem";
        public const string CleanCart = Base + "cart/clean";
        public const string Checkout = Base + "cart/checkout";
        public const string CompleteDetailsCheckout = Base + "cart/completeDetailsCheckout";
        public const string SignifydStepUpCode = Base + "cart/sendSignifydStepUpCode";
        public const string CompleteSignifydStepUp = Base + "cart/completeSignifydStepUpCheckout";
        public const string SetAdyenCreditCard = Base + "cart/setAdyenCreditCard";

        public const string BeginPayPal = Base + "adyen/beginPayPal";
        public const string CompletePayPal = Base + "adyen/completePayPal";

        /// <summary>Purchase walk, including the two Signifyd step-up calls.</summary>
        public static readonly IReadOnlyList<string> Chain = new[]
        {
            Login, GetProduct, AddToCart, UpdateCart, Checkout, CompleteDetailsCheckout,
            SignifydStepUpCode, CompleteSignifydStepUp, SetAdyenCreditCard,
        };

        public static readonly IReadOnlyList<string> PayPal = new[] { BeginPayPal, CompletePayPal };

        public static readonly IReadOnlyList<string> All = new[]
        {
            GetAccount, Login, Register, RequestReset, Reset,
            BeginPayPal, CompletePayPal,
            AddToCart, Checkout, CleanCart, CompleteDetailsCheckout, CompleteSignifydStepUp,
            RemoveLineItem, SignifydStepUpCode, SetAdyenCreditCard, UpdateCart,
            GetProduct,
        };
    }

    /// <summary>Every endpoint in both families.</summary>
    public static readonly IReadOnlyList<string> All = JohnLewisBff.All
        .Concat(ScheelsFrontastic.All)
        .ToList();

    /// <summary>True when the URL belongs to either family, exactly.</summary>
    public static bool IsKnown(string? url) =>
        !string.IsNullOrEmpty(url) && All.Contains(url, System.StringComparer.Ordinal);
}
