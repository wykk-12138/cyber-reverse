using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Viva — the last vendor in the inventory, and the one whose three calls form a complete payment cycle.
///
/// <para>
/// R925. Three paths, all under one version and one host:
/// </para>
///
/// <code>
/// /web2/checkout/v2/chargetokens        a card becomes a charge token
/// /web2/checkout/v2/paymentdetails?ref= what happened to that charge
/// /web2/checkout/v2/transactions        the transaction list
/// </code>
///
/// <para>
/// Unlike the others this is a full cycle rather than one step of one: tokenise, then read the outcome by reference,
/// then a listing. The <c>ref=</c> parameter on the second is what makes it a cycle — the token call's answer carries a
/// reference, and the status read is addressed by it rather than by a session identifier. That is the same shape as a
/// payment gateway's authorise-then-query and it is why the three sit together.
/// </para>
///
/// <para>
/// <b>The card reaches one endpoint.</b> As with Disney, <c>chargetokens</c> names a token rather than a payment, and
/// nothing else here takes a card. <see cref="ChargeTokenAsync"/> takes one; the other two accept a reference and a
/// window. That is enforced by the signatures rather than by a note.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The bodies, the responses, and the reference's field name. <c>ref=</c> is the only clue to
/// the shape of the token answer, so <see cref="ChargeTokenAsync"/> looks for a field whose name suggests a reference
/// and fails when it finds none rather than inventing one — a reference invented from nothing produces a status read
/// that answers about a charge that does not exist.
/// </para>
/// </summary>
public static class VivaPayments
{
    internal const string Host = "https://www.vivapayments.com";

    internal const string ChargeTokens = "/web2/checkout/v2/chargetokens";
    internal const string PaymentDetails = "/web2/checkout/v2/paymentdetails?ref=";
    internal const string Transactions = "/web2/checkout/v2/transactions";

    internal const int RecoveredAddressCount = 3;

    /// <summary>Field names that could carry the reference the status read is addressed by. Guesses, and labelled so.</summary>
    internal static readonly string[] ReferenceFields =
    {
        "chargeToken", "token", "transactionId", "transactionRef", "paymentRef", "orderCode",
    };

    /// <summary>
    /// Turns a card into a charge token and leaves the reference in <c>viva.ref</c>.
    ///
    /// <para>
    /// The reference is the thing the second call needs, so failing to find one is a failure and not a partial success:
    /// a token nobody can ask about is worth nothing to the next step.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> ChargeTokenAsync(FlowSession session, string cardNumber, string expiry,
        CancellationToken ct, Func<string, string, string, CancellationToken, Task<NetResponse?>> post)
    {
        if (string.IsNullOrWhiteSpace(cardNumber))
            return StepOutcome.Fail("viva charge-token needs a card number");

        var body = "{\"cardNumber\":\"" + cardNumber.Replace("\"", "") + "\",\"expiry\":\"" +
                   (expiry ?? string.Empty).Replace("\"", "") + "\"}";

        var res = await post(Host + ChargeTokens, body, "viva-chargetokens", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("vivapayments unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"viva charge-token HTTP {res.StatusCode}", retryable: true);

        session.Vars["viva.chargeTokenBody"] = res.Body;

        foreach (var field in ReferenceFields)
        {
            var m = Regex.Match(res.Body, "\"" + Regex.Escape(field) + "\"\\s*:\\s*\"([^\"]+)\"");
            if (m.Success)
            {
                session.Vars["viva.ref"] = m.Groups[1].Value;
                session.Vars["viva.refField"] = field;
                return StepOutcome.Success();
            }
        }

        // no reference, so no status read is possible -- said plainly instead of leaving a half-result
        return StepOutcome.Fail("viva charge-token answered without a recognisable reference; the status read cannot be addressed");
    }

    /// <summary>
    /// Reads a charge's outcome by reference. Succeeds when the answer arrives, whatever it says; whether the charge
    /// itself succeeded is a separate question the caller asks of the body.
    /// </summary>
    public static async Task<StepOutcome> PaymentDetailsAsync(FlowSession session, CancellationToken ct,
        Func<string, CancellationToken, Task<NetResponse?>> get)
    {
        if (!session.Vars.TryGetValue("viva.ref", out var reference) || string.IsNullOrEmpty(reference))
            return StepOutcome.Fail("viva payment-details has no reference; the charge-token step did not produce one");

        var res = await get(Host + PaymentDetails + Uri.EscapeDataString(reference), ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("vivapayments unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"viva payment-details HTTP {res.StatusCode}", retryable: true);

        session.Vars["viva.paymentDetails"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The transaction listing. Recorded as a call the original can make; what a purchase needs from it is unknown, so it
    /// is exposed and not invoked by anything else here.
    /// </summary>
    public static async Task<StepOutcome> TransactionsAsync(FlowSession session, CancellationToken ct,
        Func<string, CancellationToken, Task<NetResponse?>> get)
    {
        var res = await get(Host + Transactions, ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("vivapayments unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"viva transactions HTTP {res.StatusCode}", retryable: true);

        session.Vars["viva.transactions"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>The three calls in order, as the names imply.</summary>
    internal static readonly string[] StepOrder = { "ChargeToken", "PaymentDetails", "Transactions" };
}