using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// John Lewis's nineteen steps against its twelve BFF endpoints, paired in R118/R119.
///
/// <para>
/// This is the first map in the session with <b>more steps than endpoints</b> — fourteen steps share
/// nine endpoints, three steps have none, and three endpoints are named by no step. That shape is
/// itself a reading: a BFF endpoint is not a step. <c>v2/sessions/web/handover</c> serves
/// <c>WebHandOver</c> and <c>SessionHandover</c> both, and <c>v4/orderforms/deliveries</c> serves
/// <c>SubmitShipping</c> and <c>CreateDelivery</c>, because the step list is the client's phases and
/// the endpoints are the server's resources.
/// </para>
///
/// <code>
/// WebHandOver          → v2/sessions/web/handover        GuestCallback        → v4/callback/guest
/// SessionHandover      → v2/sessions/web/handover        DeliveryPage         → v3/orderforms/delivery-page
/// SubmitShipping       → v4/orderforms/deliveries        CreateDelivery       → v4/orderforms/deliveries
/// GetDeliveryMethods   → v4/orderforms/deliveries/methods (derived, R1137)
/// SubmitDeliveryMethod → v3/orderforms/deliveries/details
/// GetPaymentPage       → v2/orderforms/payment-page      SubmitOrderStripe    → v2/orderforms/payments
/// SubmitOrder          → v2/orders                       AuthenticatePayment  → v2/orderforms/payments
/// SubmitBillingAddress → v1/orderforms/payments/billing-address
/// PlaceOrder           → v2/orders
/// </code>
///
/// <para>
/// The three unmapped steps are unmapped for a reason worth recording: <c>GetHome</c> is a page load,
/// and <c>HandleRequiresAction</c> / <c>GetStripePaymentIntent</c> are <b>Stripe's</b> calls, made
/// against Stripe's host rather than the BFF. That is the mirror image of R117's finding: Demandware
/// has Stripe <i>steps</i> and no Stripe <i>controller</i>; John Lewis has Stripe steps and reaches
/// Stripe directly, which is why no BFF endpoint names them.
/// </para>
/// </summary>
public static class JohnLewisStepMap
{
    /// <summary>Step → BFF endpoint, where the names settle it.</summary>
    public static readonly IReadOnlyDictionary<string, string> Pairs =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            // R119: FindProduct(21) and AddToCart(22) are steps of this flow, and neither has a BFF
            // endpoint — the BFF starts at the handover. They stay unmapped by construction.
            ["WebHandOver"] = RetailApiFamilies.JohnLewisBff.SessionHandoverV2,
            ["SessionHandover"] = RetailApiFamilies.JohnLewisBff.SessionHandoverV2,
            ["GuestCallback"] = RetailApiFamilies.JohnLewisBff.GuestCallbackV4,
            ["DeliveryPage"] = RetailApiFamilies.JohnLewisBff.DeliveryPageV3,
            // R1136: SubmitShipping carries the address (delivery-address, eleven-key body);
        // CreateDelivery below is the body-less confirm. The map had both on DeliveriesV4.
        ["SubmitShipping"] = RetailApiFamilies.JohnLewisBff.DeliveryAddressV4,
            ["CreateDelivery"] = RetailApiFamilies.JohnLewisBff.DeliveriesV4,
            // R1137: this step reads, and reads the derived URL the image builds by joining
        // "…/deliveries/" with "/methods" (0x14705db98 + 0x146ab5dd0, GET at sub_140A3FB10).
        // R118/R119 paired it with the POST details by name correlation alone, which left that
        // GET with no step and gave one endpoint two names; the submit just below keeps the POST.
        ["GetDeliveryMethods"] = RetailApiFamilies.JohnLewisBff.DeliveryMethodsV4,
            ["SubmitDeliveryMethod"] = RetailApiFamilies.JohnLewisBff.DeliveryDetailsV3,
            ["GetPaymentPage"] = RetailApiFamilies.JohnLewisBff.PaymentPageV2,
            ["SubmitOrderStripe"] = RetailApiFamilies.JohnLewisBff.PaymentsV2,
            ["AuthenticatePayment"] = RetailApiFamilies.JohnLewisBff.PaymentsV2,
            ["SubmitOrder"] = RetailApiFamilies.JohnLewisBff.OrdersV2,
            ["PlaceOrder"] = RetailApiFamilies.JohnLewisBff.OrdersV2,
            ["SubmitBillingAddress"] = RetailApiFamilies.JohnLewisBff.BillingAddressV1,
        };

    /// <summary>Steps with no BFF endpoint — a page load and two Stripe calls.</summary>
    public static readonly IReadOnlyList<string> UnmappedSteps =
        StoreFlowSteps.JohnLewis.Names.Where(n => !Pairs.ContainsKey(n)).ToList();

    /// <summary>Endpoints no step names, including the trailing-slash duplicate.</summary>
    public static readonly IReadOnlyList<string> UnusedEndpoints =
        RetailApiFamilies.JohnLewisBff.All.Where(e => !Pairs.Values.Contains(e)).ToList();

    /// <summary>
    /// The contrast with R117, recorded next to the map so the two findings stay together.
    /// </summary>
    public const string StripeContrast =
        "John Lewis reaches Stripe directly (no BFF endpoint names its Stripe steps); " +
        "Demandware has Stripe steps and no Stripe controller";

    /// <summary>How the map was drawn.</summary>
    public const string Evidence =
        "name correlation between the 19 John Lewis steps and the 12 BFF endpoints; " +
        "no request capture; unmapped steps and unused endpoints recorded";

    /// <summary>The endpoint a step pairs with, or null.</summary>
    public static string? EndpointFor(string? step) =>
        string.IsNullOrEmpty(step) ? null
            : Pairs.TryGetValue(step, out var endpoint) ? endpoint : null;

    /// <summary>Distinct endpoints the fourteen mapped steps reach.</summary>
    public static IReadOnlyList<string> Targets => Pairs.Values.Distinct().ToList();

    /// <summary>The steps that pair, in flow order.</summary>
    public static IReadOnlyList<string> MappedSteps =>
        StoreFlowSteps.JohnLewis.Names.Where(Pairs.ContainsKey).ToList();
}
