using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Candidate steps found by scanning ordinals instead of reading one contiguous literal — and the
/// reason they are only <b>candidates</b>.
///
/// <para>
/// R112 read each flow from a single adjacent run of the string pool, which is the reliable unit:
/// that run is one class's own step list. R119 showed a run can skip ordinals that are real steps
/// (John Lewis 21/22), and the fix was to read the <b>same class's lambda literal</b>, which names
/// them.
/// </para>
///
/// <para>
/// R120 tried the cheaper route — scan every literal for <c>&lt;Name&gt;d__N</c> and collect the names
/// per ordinal — and it does not work, for a reason worth writing down: <b>ordinals are per class</b>.
/// Ordinal 126 contains <c>CompletePayPalGuestPayment</c>, <c>Register</c> and
/// <c>SubmitKlaviyoSubscription</c> from three different classes, so a bare ordinal cannot say which
/// class owns a name. The scan is therefore recorded as a candidate list, not merged into
/// <see cref="StoreFlowSteps"/>.
/// </para>
///
/// <code>
/// 104 GetAccessToken / CartApiObjectCreate / GetOrders        (three classes collide)
/// 106 AddToCartGraphQL         107 AddToCartPreloadGraphQL   108 CreateCartGraphql
/// 109 GetCartAvailabilityGraphql                              ← a GraphQL cart family
/// 125 CompletePayPalPayment    126 CompletePayPalGuestPayment 127 CompleteForwardPayment
/// 128 AddToCartStoreFront      130 AddToCartPreload
/// </code>
///
/// <para>
/// Two of these families are worth chasing with the <b>literal</b> method rather than the ordinal
/// method: the four GraphQL cart steps (106–109) line up with R101's persisted queries, and the
/// PayPal steps (125–127) line up with R118's finding that one store reaches Stripe directly.
/// </para>
/// </summary>
public static class CandidateSteps
{
    /// <summary>One candidate: the name, the ordinal it was seen at, and what else shares it.</summary>
    public sealed record Candidate(string Name, int Ordinal, string Collision);

    /// <summary>
    /// The GraphQL cart family — the strongest candidates, because they agree with R101's six
    /// persisted operations and with R96's finding that the replica had no GraphQL cart at all.
    /// </summary>
    public static readonly IReadOnlyList<Candidate> GraphQlCart = new[]
    {
        new Candidate("AddToCartGraphQL", 106, "CartApiObjectCreate"),
        new Candidate("AddToCartPreloadGraphQL", 107, "GetUnzerCallback"),
        new Candidate("CreateCartGraphql", 108, "FetchTokensFromBrokerAsync"),
        new Candidate("GetCartAvailabilityGraphql", 109, "GetCartAvailabilityGraphql"),
    };

    /// <summary>The PayPal/forward-payment family seen at 125–127.</summary>
    public static readonly IReadOnlyList<Candidate> PaymentCompletion = new[]
    {
        new Candidate("CompletePayPalPayment", 125, "none"),
        new Candidate("CompletePayPalGuestPayment", 126, "Register, SubmitKlaviyoSubscription"),
        new Candidate("CompleteForwardPayment", 127, "WriteAttributeTextBlockAsync"),
    };

    /// <summary>The storefront cart steps seen at 128 and 130.</summary>
    public static readonly IReadOnlyList<Candidate> StorefrontCart = new[]
    {
        new Candidate("AddToCartStoreFront", 128, "none"),
        new Candidate("AddToCartPreload", 130, "WriteRawWithCharCheckingAsync"),
    };

    /// <summary>All candidates.</summary>
    public static readonly IReadOnlyList<Candidate> All = GraphQlCart
        .Concat(PaymentCompletion)
        .Concat(StorefrontCart)
        .ToList();

    /// <summary>
    /// Why none of these is asserted as a step. Asserted by a test so the caveat cannot be lost.
    /// </summary>
    public const string Evidence =
        "ordinal scan; ordinals are per class, so a name seen at an ordinal may belong to another " +
        "class; ownership unproven; not merged into StoreFlowSteps";

    /// <summary>True when the name is a candidate (and therefore not a confirmed step unless it also
    /// appears in <see cref="StoreFlowSteps"/>).</summary>
    public static bool IsCandidate(string? name) =>
        !string.IsNullOrEmpty(name) && All.Any(c => c.Name == name);

    /// <summary>The candidate with this name, or null.</summary>
    public static Candidate? For(string? name) =>
        string.IsNullOrEmpty(name) ? null : All.FirstOrDefault(c => c.Name == name);
}
