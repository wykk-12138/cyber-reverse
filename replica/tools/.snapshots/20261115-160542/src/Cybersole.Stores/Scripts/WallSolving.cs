using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The original's wall-solving surface, read from its own state-machine names in R143 — and the
/// correction that follows from it.
///
/// <code>
/// DetectAsync        the detection step, named exactly as the replica names it
/// SolveWafAsync      one WAF, one call — the generic solve step
/// RemoteSolve        the service road, named as its own method
/// SolveBotD          DataDome's BotD challenge
/// SolveCptChallenge  the interstitial ("captcha-token") challenge
/// SolveRecaptcha     reCAPTCHA specifically
/// SubmitCaptcha      the submit half, separate from the fetch
/// PollCaptchaAsync   polling, which means at least one road is asynchronous
/// GetCheckoutCaptcha the checkout-time captcha (Adyen's 3DS captcha)
/// Solve3DS / Solve3DSRedirect / Solve3DSToken / Solve3DSChallenge / SolvePayPal3DS
/// </code>
///
/// <para>
/// <b>R141's DataDome row was wrong.</b> The audit said DataDome had "a host, no protocol" and left it
/// at that. <c>SolveBotD</c> is DataDome's own challenge script, and the original has a method named
/// after it — so the original solves DataDome, and what was missing was <b>this workspace's</b> knowledge
/// of the protocol, not the original's implementation. That is the same distinction R127 drew about
/// missing controllers, and it deserves the same wording: <i>the gap is in my notes</i>.
/// </para>
///
/// <para>
/// <c>PollCaptchaAsync</c> answers the other question this round asked: at least one road is
/// <b>polled</b>, not awaited inline. So detection may dispatch and poll rather than block — the replica
/// runs its ladder synchronously, which is correct for a local browser solve and wrong for a service
/// that answers later.
/// </para>
/// </summary>
public static class WallSolving
{
    /// <summary>The detection step's name, which the replica shares.</summary>
    public const string DetectStep = "DetectAsync";

    /// <summary>Every solve-shaped method the image names.</summary>
    public static readonly IReadOnlyList<string> SolveMethods = new[]
    {
        "SolveWafAsync", "RemoteSolve", "SolveBotD", "SolveCptChallenge", "SolveRecaptcha",
        "SubmitCaptcha", "PollCaptchaAsync", "GetCheckoutCaptcha",
        "Solve3DS", "Solve3DSRedirect", "Solve3DSToken", "SolvePayPal3DS",
    };

    /// <summary>Which vendor each solve method belongs to, where the name says it.</summary>
    public static readonly IReadOnlyDictionary<string, string> MethodVendor =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["SolveWafAsync"] = "generic",
            ["RemoteSolve"] = "service",
            ["SolveBotD"] = "datadome",
            ["SolveRecaptcha"] = "recaptcha",
            ["GetCheckoutCaptcha"] = "checkout",
            ["Solve3DS"] = "three-d-secure",
            ["Solve3DSRedirect"] = "three-d-secure",
            ["Solve3DSToken"] = "three-d-secure",
            ["SolvePayPal3DS"] = "three-d-secure",
        };

    /// <summary>
    /// The vendored methods that prove a wall the audit called a gap is in fact solved:
    /// DataDome by name, and the checkout captcha as its own concern.
    /// </summary>
    public static readonly IReadOnlyList<string> VendoredSolves = new[]
    {
        "SolveBotD", "SolveRecaptcha", "GetCheckoutCaptcha",
    };

    /// <summary>Methods whose names imply waiting rather than blocking.</summary>
    public static readonly IReadOnlyList<string> Polling = new[] { "PollCaptchaAsync" };

    /// <summary>True when the image names a solve method for this vendor.</summary>
    public static bool HasSolveFor(string? vendor) =>
        !string.IsNullOrEmpty(vendor)
        && MethodVendor.Any(kv => string.Equals(kv.Value, vendor, System.StringComparison.OrdinalIgnoreCase));

    /// <summary>The correction to R141's audit, in one sentence a test can hold.</summary>
    public const string DataDomeCorrection =
        "SolveBotD exists, so the original does solve DataDome — the missing protocol is this " +
        "workspace's gap, not the original's";

    /// <summary>What polling implies about the dispatch the replica runs synchronously.</summary>
    public const string PollingConsequence =
        "PollCaptchaAsync means at least one road answers later; an inline await fits a local browser " +
        "solve and does not fit a service";
}
