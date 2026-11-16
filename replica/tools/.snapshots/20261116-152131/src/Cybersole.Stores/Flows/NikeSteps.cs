namespace Cybersole.Stores.Flows;

/// <summary>
/// Nike's checkout step list, read out of the 5.18.32 image in R111 — <b>sixteen</b> steps in
/// compiler order, with the state-machine ordinals the compiler assigned.
///
/// <para>
/// The literals are one adjacent run in the string pool, which is why the ordinals are consecutive
/// where they exist:
/// </para>
///
/// <code>
/// &lt;StartEcomSession&gt;d__41   &lt;Authorize&gt;d__42        &lt;GetAccessToken&gt;d__43
/// &lt;FindVariant&gt;d__44        &lt;CreateBasket&gt;d__46      &lt;SubmitCustomer&gt;d__48
/// &lt;ValidateAddress&gt;d__49    &lt;SubmitShippingAddress&gt;d__50
/// &lt;GetShippingMethods&gt;d__51 &lt;SubmitShippingMethod&gt;d__52
/// &lt;SubmitBillingAddress&gt;d__53 &lt;BeginCheckout&gt;d__54
/// &lt;CheckInventory&gt;d__55      &lt;GetShopperIp&gt;d__56
/// &lt;GetPaymentMethods&gt;d__57   &lt;SubmitOrder&gt;d__58
/// </code>
///
/// <para>
/// This replaces an inherited "fourteen steps" count that came from a partial reading. Sixteen is
/// what the binary says, and the names are the compiler's, not a paraphrase — <c>StartEcomSession</c>
/// at 41 and <c>BeginCheckout</c> at 54 are two different steps, and treating them as one is exactly
/// the kind of merge a hand-written list makes.
/// </para>
///
/// <para>
/// The ordinals skip 45 and 47: those are the <c>MoveNext</c> helpers the compiler emitted between
/// steps, not steps themselves. Gaps are expected and are not evidence of a missing step.
/// </para>
/// </summary>
public static class NikeSteps
{
    /// <summary>One step: the compiler's method name and the ordinal it carries.</summary>
    public sealed record Step(string Name, int Ordinal);

    /// <summary>The sixteen steps, in the order the pool lists them.</summary>
    public static readonly IReadOnlyList<Step> All = new[]
    {
        new Step("StartEcomSession", 41),
        new Step("Authorize", 42),
        new Step("GetAccessToken", 43),
        new Step("FindVariant", 44),
        new Step("CreateBasket", 46),
        new Step("SubmitCustomer", 48),
        new Step("ValidateAddress", 49),
        new Step("SubmitShippingAddress", 50),
        new Step("GetShippingMethods", 51),
        new Step("SubmitShippingMethod", 52),
        new Step("SubmitBillingAddress", 53),
        new Step("BeginCheckout", 54),
        new Step("CheckInventory", 55),
        new Step("GetShopperIp", 56),
        new Step("GetPaymentMethods", 57),
        new Step("SubmitOrder", 58),
    };

    /// <summary>The step names alone, in order.</summary>
    public static IReadOnlyList<string> Names => All.Select(s => s.Name).ToList();

    /// <summary>The ordinals, ascending — the pool's order is the compiler's order.</summary>
    public static IReadOnlyList<int> Ordinals => All.Select(s => s.Ordinal).ToList();

    /// <summary>True when the image names this step.</summary>
    public static bool IsStep(string? name) =>
        !string.IsNullOrEmpty(name) && All.Any(s => s.Name == name);

    /// <summary>Where a step sits in the flow, 1-based; null when it is not one of the sixteen.</summary>
    public static int? Position(string? name)
    {
        if (string.IsNullOrEmpty(name)) return null;

        for (var i = 0; i < All.Count; i++)
            if (All[i].Name == name) return i + 1;

        return null;
    }
}
