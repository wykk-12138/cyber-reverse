using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Payments;

/// <summary>
/// eShopWorld — a hosted payment panel with two polling loops, on two hosts.
///
/// <para>
/// R923. Five paths, and their arrangement is the interesting part:
/// </para>
///
/// <code>
/// payments-panel.production.eshopworld.com/api/v2/PaymentMethods/url        where the panel lives
/// payments-panel.production.eshopworld.com/api/v2/PaymentMethods?paymentId= what a payment is
/// payments-panel.production.eshopworld.com/api/v2/WebComponent/state       how the panel is doing
/// retailer-shopifypayments-api.production.eshopworld.com
///     /api/v1/payment/apm/session/status                                   how an alternative payment is doing
///     /api/v1/payment/apm/session/post_pay_status                           ...and just after it is paid
/// </code>
///
/// <para>
/// Two of those are state endpoints, which means this vendor is not a single call but a wait: ask for a panel, let the
/// buyer complete it, and poll until the state settles. The panel's own state and an alternative payment's session are
/// separate loops on separate hosts, so a flow that has both must not poll one and assume the other.
/// </para>
///
/// <para>
/// <b>Why a shared poller rather than two loops.</b> Both endpoints answer the shape "not yet / done / failed" and both
/// need a deadline, an interval and a terminal condition. Writing that twice invites the two copies to disagree about
/// what counts as done, which is how a checkout completes on one path and hangs on the other.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The states themselves. No response body survives, so the terminal words below are a guess
/// drawn from what a payment state machine usually says. The poller therefore treats anything it does not recognise as
/// "keep waiting until the deadline" rather than as failure -- a wrong guess at a failure word would abandon a payment
/// that was about to succeed, which is worse than waiting out the clock.
/// </para>
/// </summary>
public static class EshopWorldPanel
{
    internal const string PanelHost = "https://payments-panel.production.eshopworld.com";
    internal const string ApmpHost = "https://retailer-shopifypayments-api.production.eshopworld.com";

    internal const string MethodsUrl = "/api/v2/PaymentMethods/url";
    internal const string MethodsByPayment = "/api/v2/PaymentMethods?paymentId=";
    internal const string WebComponentState = "/api/v2/WebComponent/state";
    internal const string ApmpStatus = "/api/v1/payment/apm/session/status";
    internal const string ApmpPostPayStatus = "/api/v1/payment/apm/session/post_pay_status";

    internal const int RecoveredAddressCount = 5;

    /// <summary>The words that end a poll. Everything else keeps waiting.</summary>
    internal static readonly string[] TerminalStates =
    {
        "completed", "complete", "succeeded", "success", "approved", "authorised", "authorized", "captured",
        "failed", "declined", "cancelled", "canceled", "rejected", "expired", "error",
    };

    private static readonly string[] SuccessWords =
    {
        "completed", "complete", "succeeded", "success", "approved", "authorised", "authorized", "captured",
    };

    /// <summary>Which of the two state endpoints a poll talks to.</summary>
    public enum Loop
    {
        /// <summary>The hosted panel's own state, on the panel host.</summary>
        WebComponent,

        /// <summary>An alternative payment's session, on the APM host.</summary>
        Apmp,
    }

    /// <summary>The URL a poll would call for a loop, given whatever identifier that loop needs.</summary>
    public static string StateUrl(Loop loop, string id) => loop switch
    {
        Loop.WebComponent => PanelHost + WebComponentState + "?paymentId=" + Uri.EscapeDataString(id ?? string.Empty),
        Loop.Apmp => ApmpHost + ApmpStatus + "?paymentId=" + Uri.EscapeDataString(id ?? string.Empty),
        _ => throw new ArgumentOutOfRangeException(nameof(loop)),
    };

    /// <summary>
    /// The panel URL for a payment, which is where a buyer is sent rather than something the flow reads.
    /// </summary>
    public static string MethodsUrlFor(string paymentId) =>
        PanelHost + MethodsByPayment + Uri.EscapeDataString(paymentId ?? string.Empty);

    /// <summary>
    /// Polls a state endpoint until a terminal word appears or the deadline passes.
    ///
    /// <para>
    /// Returns three outcomes and keeps them distinct: done, failed, and still-unsettled. The third is not a failure --
    /// a payment that has not settled by the deadline may still settle, and calling it failed would make a slow gateway
    /// look like a declined card.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> PollAsync(FlowSession session, Loop loop, string id, CancellationToken ct,
        Func<string, CancellationToken, Task<NetResponse?>> get,
        int attempts = 20, int intervalMs = 1500)
    {
        if (string.IsNullOrWhiteSpace(id))
            return StepOutcome.Fail("eShopWorld poll needs an id and none was given");

        var url = StateUrl(loop, id);
        string? last = null;

        for (var i = 0; i < attempts; i++)
        {
            if (ct.IsCancellationRequested) break;

            var res = await get(url, ct).ConfigureAwait(false);
            if (res is null || !res.IsSuccess)
            {
                // an unreachable poll is not a failed payment; keep trying until the deadline
                if (i < attempts - 1) { await Delay(intervalMs, ct).ConfigureAwait(false); continue; }
                return StepOutcome.Fail("eshopworld state endpoint unreachable through the whole window", retryable: true);
            }

            last = res.Body;
            session.Vars["eshopworld.state"] = last;

            var word = StateWord(last);
            if (word != null)
            {
                if (SuccessWords.Contains(word, StringComparer.OrdinalIgnoreCase))
                {
                    session.Vars["eshopworld.settled"] = "done";
                    return StepOutcome.Success();
                }
                session.Vars["eshopworld.settled"] = "failed";
                return StepOutcome.Fail($"eshopworld payment {word}");
            }

            if (i < attempts - 1) await Delay(intervalMs, ct).ConfigureAwait(false);
        }

        // unsettled, and said so rather than guessed in either direction
        session.Vars["eshopworld.settled"] = "unknown";
        return StepOutcome.Fail("eshopworld state did not settle before the deadline", retryable: true);
    }

    /// <summary>
    /// The first terminal word in a body, or null. Recognition is deliberately narrow: only an exact word from the list
    /// counts, so a body mentioning "completed" inside an unrelated field is still a hit while an unknown word is not.
    /// </summary>
    internal static string? StateWord(string? body)
    {
        if (string.IsNullOrEmpty(body)) return null;

        foreach (var word in TerminalStates)
        {
            if (Regex.IsMatch(body, "\"\\s*(?:state|status|paymentStatus|result)\\s*\"\\s*:\\s*\"" + Regex.Escape(word) + "\"",
                    RegexOptions.IgnoreCase))
                return word;
        }
        return null;
    }

    private static Task Delay(int ms, CancellationToken ct) =>
        ms <= 0 ? Task.CompletedTask : Task.Delay(ms, ct);
}