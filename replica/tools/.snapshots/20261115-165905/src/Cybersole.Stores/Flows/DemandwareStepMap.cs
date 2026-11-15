using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Demandware's classic twelve steps against the controllers, paired in R117 — and the first map in
/// this session where the pairing **closed a real gap in the code**: three of the twelve steps had no
/// controller in the table because R94 read a window of the pool instead of the whole list.
///
/// <code>
/// AddToCart              → Cart-AddProduct
/// InitiateCheckout       → Checkout-Begin
/// GenerateCSRF           → CSRF-Generate
/// GetCheckout            → CheckoutServices-FetchOrderModel
/// SubmitBillingAddress   → CheckoutServices-SubmitBilling          (new in R117)
/// SubmitConsignment      → CheckoutShippingServices-SubmitShipping
/// SubmitShippingOption   → CheckoutShippingServices-UpdateShippingMethod  (new in R117)
/// CreateOrder            → CheckoutServices-PlaceOrder
/// SubmitPayment          → CheckoutServices-SubmitPayment
/// ConfirmPayment         → CheckoutServices-PaymentAuthorization   (new in R117)
/// </code>
///
/// <para>
/// Two steps stay unmapped, and one of them is a finding in itself:
/// </para>
///
/// <list type="bullet">
/// <item><c>GetPaymentMethod</c> — the only payment read the image has is
/// <c>CheckoutServices-FetchOrderModel</c>, which is already carrying <c>GetCheckout</c>. Whether this
/// step re-reads the model or asks something else is not settled by the names.</item>
/// <item><c>CreateStripePaymentMethod</c> — <b>there is no <c>Stripe-*</c> controller anywhere in the
/// image.</b> The payment controllers are Adyen's (<c>AdyenUpgrade-Authorize</c>,
/// <c>Adyen-Adyen3DS2</c>, <c>Adyen-PaymentsDetails</c>, <c>AdyenComponents-Payment*</c>). So this step
/// goes through the generic submit with a Stripe form, or the image has a gap of its own — either way
/// the step name is not backed by a Stripe controller, and saying so is more useful than inventing
/// one.</item>
/// </list>
/// </summary>
public static class DemandwareStepMap
{
    /// <summary>Step → controller, where the two names settle it.</summary>
    public static readonly IReadOnlyDictionary<string, string> Pairs =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["AddToCart"] = DemandwareControllers.CartAddProduct,
            ["InitiateCheckout"] = DemandwareControllers.CheckoutBegin,
            ["GenerateCSRF"] = DemandwareControllers.CsrfGenerate,
            ["GetCheckout"] = DemandwareControllers.FetchOrderModel,
            ["SubmitBillingAddress"] = DemandwareControllers.SubmitBilling,
            ["SubmitConsignment"] = DemandwareControllers.SubmitShipping,
            ["SubmitShippingOption"] = DemandwareControllers.UpdateShippingMethod,
            ["CreateOrder"] = DemandwareControllers.PlaceOrder,
            ["SubmitPayment"] = DemandwareControllers.SubmitPayment,
            ["ConfirmPayment"] = DemandwareControllers.PaymentAuthorization,
        };

    /// <summary>Steps whose controller the names do not settle.</summary>
    public static readonly IReadOnlyList<string> UnmappedSteps =
        StoreFlowSteps.DemandwareClassic.Names.Where(n => !Pairs.ContainsKey(n)).ToList();

    /// <summary>
    /// The finding behind the biggest gap: no <c>Stripe-*</c> controller exists in the image, while
    /// the payment controllers that do exist are all Adyen's.
    /// </summary>
    public const string StripeFinding =
        "no Stripe-* controller exists in the image; payment controllers are Adyen's";

    /// <summary>How the map was drawn.</summary>
    public const string Evidence =
        "name correlation between the 12 classic steps and the controller list; no request capture; " +
        "unmapped steps recorded";

    /// <summary>The controller a step pairs with, or null.</summary>
    public static string? ControllerFor(string? step) =>
        string.IsNullOrEmpty(step) ? null
            : Pairs.TryGetValue(step, out var controller) ? controller : null;

    /// <summary>The steps that pair, in flow order.</summary>
    public static IReadOnlyList<string> MappedSteps =>
        StoreFlowSteps.DemandwareClassic.Names.Where(Pairs.ContainsKey).ToList();
}
