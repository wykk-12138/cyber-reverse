namespace Cybersole.Stores.Scripts;

/// <summary>
/// Cart priming: what "Dummy" means, and why it is not a dry run.
///
/// <para>
/// R941. R940 recorded AddToCartDummy as the one gap that need not wait on endpoint evidence, on the reasoning that its
/// name says it does not talk to a shop. The neighbours say otherwise. Four consecutive state machines:
/// </para>
///
/// <code>
/// &lt;GetProduct&gt;d__45 · &lt;AddToCartDummy&gt;d__46 · &lt;AddToCartMulti&gt;d__47 · &lt;RemoveDummy&gt;d__48
/// </code>
///
/// <para>
/// An add followed immediately by a remove, which is not a dry run and not a test: it is the priming pattern. A shop that
/// creates a cart on first add costs a round trip and a session mutation at the worst possible moment, so adding a cheap
/// item early and removing it later leaves a cart in place for the real add to reuse. The name is about the item being a
/// placeholder, not about the call being fake.
/// </para>
///
/// <para>
/// <b>What surrounds it, and what that says about the store.</b> The other descriptors in the same file name
/// <c>Login</c>, <c>LoginVerify2FA</c>, <c>EnableTwoFactor</c>, <c>Register</c>, <c>FetchBalance</c>,
/// <c>CheckFanRewardStat</c> and <c>EnterSweepStakesRaffle</c>. A balance, a fan reward statistic and a sweepstakes raffle
/// are a loyalty-programme store's surface, which is why the dummy item can be cheap: the shop has one. That is inference
/// from names and is labelled as such — it narrows which shop this belongs to without identifying it.
/// </para>
///
/// <para>
/// <b>What follows for the replica.</b> The step is now implementable without endpoint evidence in the way the other four
/// are blocked: what it needs is a product to prime with and a remove to follow, and its shape is add-then-remove rather
/// than a request whose address must be recovered. What is still unknown is which item a given shop tolerates as a dummy,
/// which is per-shop data rather than per-framework code.
/// </para>
/// </summary>
public static class CartPriming
{
    /// <summary>The four consecutive state machines, in ordinal order — an add followed by its remove.</summary>
    internal static readonly string[] PrimingSequence =
    {
        "GetProduct", "AddToCartDummy", "AddToCartMulti", "RemoveDummy",
    };

    /// <summary>
    /// Names from the same file that characterise the store: account handling and a loyalty programme.
    /// </summary>
    internal static readonly string[] LoyaltySurface =
    {
        "Login", "LoginVerify2FA", "EnableTwoFactor", "Register", "FetchBalance",
        "CheckFanRewardStat", "EnterSweepStakesRaffle",
    };

    /// <summary>The per-shop datum the priming step needs, which no name in the image supplies.</summary>
    internal const string UnknownForPriming =
        "which item a given shop tolerates as a placeholder; that is per-shop data, not per-framework code";

    /// <summary>
    /// What the pattern is. Priming, not a dry run: a cart is created early so the real add does not have to create one at
    /// the moment it matters.
    /// </summary>
    internal const string Meaning =
        "a placeholder item added early and removed later, so the real add reuses a cart that already exists";

    /// <summary>True when a name belongs to the priming pair rather than to the transport or parser axes.</summary>
    public static bool IsPriming(string? name) =>
        name == "AddToCartDummy" || name == "RemoveDummy";

    /// <summary>
    /// The two calls a priming step makes, in order, so a caller cannot add without removing — which would leave a stray
    /// item in the cart and is the failure the pair exists to avoid.
    /// </summary>
    public static IReadOnlyList<string> CallsFor(string productReference) =>
        new[] { "add:" + (productReference ?? string.Empty), "remove:" + (productReference ?? string.Empty) };
}