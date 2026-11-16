using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// A sixth store flow the image carries: <b>Adyen/PayPal express checkout</b>, found in R125 while
/// checking whether the SCAPI family was complete.
///
/// <code>
/// 33 AdyenSession                        34 SubmitPaymentPayPal
/// 35 AdyenPayPalPatchOrder               36 GetPayPalAccessToken
/// 37 AdyenSaveExpressShopperDetails      38 ShowConfirmationPaymentFromComponent
/// </code>
///
/// <para>
/// Read the way R119 taught: the literal's first token (<c>&lt;PlaceOrder&gt;d__32</c>) is the tail of
/// the <i>previous</i> string in the pool, so the flow's own ordinals are 33–38 and the count is six.
/// Trusting the literal as-is would have produced seven steps and an ordinal list that cannot ascend.
/// </para>
///
/// <para>
/// Every step here has a controller or is a client-side confirmation, which is the opposite of the
/// Demandware app path in R124 — the payment path <b>does</b> run to completion on one side:
/// </para>
///
/// <list type="bullet">
/// <item><c>AdyenSession</c> → the Adyen session the page opens, matching
/// <c>Adyen-Adyen3DS2</c> and <c>Adyen-PaymentsDetails</c>.</item>
/// <item><c>AdyenSaveExpressShopperDetails</c> → <c>Adyen-SaveExpressShopperDetails?ajax=true</c>, a
/// controller this session's table did not have before R125.</item>
/// <item><c>ShowConfirmationPaymentFromComponent</c> → the component's confirmation page, the client
/// half of the component-based flow (<c>AdyenComponents-Payment*</c>).</item>
/// </list>
/// </summary>
public static class AdyenPayPalFlow
{
    /// <summary>One step: name and ordinal.</summary>
    public sealed record Step(string Name, int Ordinal);

    public static readonly IReadOnlyList<Step> All = new[]
    {
        new Step("AdyenSession", 33),
        new Step("SubmitPaymentPayPal", 34),
        new Step("AdyenPayPalPatchOrder", 35),
        new Step("GetPayPalAccessToken", 36),
        new Step("AdyenSaveExpressShopperDetails", 37),
        new Step("ShowConfirmationPaymentFromComponent", 38),
    };

    /// <summary>Names in order.</summary>
    public static IReadOnlyList<string> Names => All.Select(s => s.Name).ToList();

    /// <summary>
    /// The token that made the literal look like seven steps, and the reason it is not:
    /// it belongs to the string before it.
    /// </summary>
    public const string TailToken = "<PlaceOrder>d__32 is the previous literal's tail";

    /// <summary>How the flow was read.</summary>
    public const string Evidence =
        "one adjacent run with a foreign tail token; ordinals 33..38; no request capture";

    /// <summary>True when the name is a step of this flow.</summary>
    public static bool IsStep(string? name) =>
        !string.IsNullOrEmpty(name) && Names.Contains(name);

    /// <summary>The ordinal of a step, or null.</summary>
    public static int? OrdinalOf(string? name) =>
        string.IsNullOrEmpty(name) ? null : All.FirstOrDefault(s => s.Name == name)?.Ordinal;

    /// <summary>
    /// The controllers this flow pins, both of which the table gained in R125.
    /// </summary>
    public static readonly IReadOnlyList<string> Controllers = new[]
    {
        DemandwareControllers.AdyenSaveExpressShopperDetails,
        DemandwareControllers.ShopperInfoIp,
        DemandwareControllers.Adyen3Ds2,
        DemandwareControllers.AdyenPaymentsDetails,
    };
}
