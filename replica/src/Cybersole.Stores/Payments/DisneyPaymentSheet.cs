using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Disney's payment sheet — a card tokenised before a checkout, on a host separate from the guest account.
///
/// <para>
/// R924. Four paths across two hosts:
/// </para>
///
/// <code>
/// paymentsheet-ent.wdprapps.disney.com/api/v1/card/token   a card, tokenised
/// paymentsheet-ent.wdprapps.disney.com/api/v1/checkout     the checkout that token pays for
/// paymentsheet-ent.wdprapps.disney.com/api/v3/process      the processing step, a version later
/// registerdisney.go.com/jgc/v8/client                      the guest account client
/// </code>
///
/// <para>
/// <b>Why tokenise first.</b> The card endpoint is separate from checkout, and its name says token rather than pay, so
/// the flow's card never reaches the checkout call. That is a security property worth implementing rather than a
/// cosmetic one: a card number that appears in two request bodies is exposed twice, and the original appears to keep it
/// to one. <see cref="TokeniseCardAsync"/> therefore takes a card and returns a token, and nothing else in this class
/// accepts a card.
/// </para>
///
/// <para>
/// Two API versions sit side by side — v1 for checkout and v3 for process — which is normal for a service where the
/// processing step outlives the checkout that started it. They are recorded separately rather than unified, because
/// collapsing them to one version would silently change one of the two calls.
/// </para>
///
/// <para>
/// <b>What is inference.</b> Every request body and every response. The endpoints' names give an order — token, then
/// checkout, then process — and that order is the whole of the evidence; the field names sent below are the least the
/// names imply. The guest client is recorded and not called: nothing says what <c>jgc/v8/client</c> returns or whether a
/// purchase needs it, and a call made on a guess would be a request the original might never send.
/// </para>
/// </summary>
public static class DisneyPaymentSheet
{
    internal const string SheetHost = "https://paymentsheet-ent.wdprapps.disney.com";
    internal const string GuestHost = "https://registerdisney.go.com";

    internal const string CardToken = "/api/v1/card/token";
    internal const string Checkout = "/api/v1/checkout";
    internal const string Process = "/api/v3/process";
    internal const string GuestClient = "/jgc/v8/client";

    internal const int RecoveredAddressCount = 4;

    /// <summary>
    /// Tokenises a card and leaves the token in <c>disney.cardToken</c>.
    ///
    /// <para>
    /// The card number goes into this one request and nowhere else. That is the point of the endpoint and the reason
    /// this class exposes no method that takes a card for checkout.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> TokeniseCardAsync(FlowSession session, string cardNumber, string expiry,
        CancellationToken ct, Func<string, string, string, CancellationToken, Task<NetResponse?>> post)
    {
        if (string.IsNullOrWhiteSpace(cardNumber))
            return StepOutcome.Fail("disney tokenise needs a card number");

        var body = "{\"cardNumber\":\"" + cardNumber.Replace("\"", "") + "\",\"expiry\":\"" + (expiry ?? string.Empty).Replace("\"", "") + "\"}";

        var res = await post(SheetHost + CardToken, body, "disney-card-token", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("disney payment sheet unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"disney card token HTTP {res.StatusCode}", retryable: true);

        var m = Regex.Match(res.Body, "\"(?:token|cardToken|paymentToken)\"\\s*:\\s*\"([^\"]+)\"");
        if (!m.Success)
            return StepOutcome.Fail("disney card token answered in a shape this does not recognise");

        session.Vars["disney.cardToken"] = m.Groups[1].Value;
        // the body is kept for the same reason as everywhere else: its shape is unknown and dropping it loses evidence
        session.Vars["disney.cardTokenBody"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The checkout, paid for by the token rather than by a card. Refuses when no token was obtained, since a checkout
    /// without one would have to carry the card and that is what the split exists to avoid.
    /// </summary>
    public static async Task<StepOutcome> CheckoutAsync(FlowSession session, CancellationToken ct,
        Func<string, string, string, CancellationToken, Task<NetResponse?>> post)
    {
        if (!session.Vars.TryGetValue("disney.cardToken", out var token) || string.IsNullOrEmpty(token))
            return StepOutcome.Fail("disney checkout has no card token; tokenise first");

        var body = "{\"paymentToken\":\"" + token.Replace("\"", "") + "\"}";
        var res = await post(SheetHost + Checkout, body, "disney-checkout", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("disney checkout unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"disney checkout HTTP {res.StatusCode}", retryable: true);

        session.Vars["disney.checkout"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The processing step, which is v3 while checkout is v1. Kept separate because they are separate calls in the
    /// image, and a flow that merged them would be sending one request where the original sends two.
    /// </summary>
    public static async Task<StepOutcome> ProcessAsync(FlowSession session, CancellationToken ct,
        Func<string, string, string, CancellationToken, Task<NetResponse?>> post)
    {
        if (!session.Vars.TryGetValue("disney.checkout", out var checkout) || string.IsNullOrEmpty(checkout))
            return StepOutcome.Fail("disney process has no checkout in the session");

        var res = await post(SheetHost + Process, checkout, "disney-process", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("disney process unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"disney process HTTP {res.StatusCode}", retryable: true);

        session.Vars["disney.process"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The three step names in the order the endpoint names imply. Recorded so a runner can be told the sequence without
    /// this class calling anything on its own.
    /// </summary>
    internal static readonly string[] StepOrder = { "TokeniseCard", "Checkout", "Process" };

    /// <summary>True when the guest client is named but not called, which is the honest state of that endpoint.</summary>
    internal const string GuestClientNote =
        "jgc/v8/client is recorded and never called: nothing says what it returns or whether a purchase needs it";
}