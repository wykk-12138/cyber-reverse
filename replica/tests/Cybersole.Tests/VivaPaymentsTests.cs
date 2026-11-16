using System.Collections.Generic;
using System.Reflection;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Viva, the last vendor, and the only one whose three calls form a complete cycle.
///
/// <para>
/// R925. Tokenise, read the outcome by reference, then a listing. The <c>ref=</c> on the second call is what makes it a
/// cycle: the token answer carries a reference and the status read is addressed by it. So the case that matters is a
/// token answer without a recognisable reference — a token nobody can ask about is worth nothing to the next step, and
/// the step fails rather than inventing one.
/// </para>
/// </summary>
public class VivaPaymentsTests
{
    private static string Const(string name) =>
        (string)typeof(VivaPayments)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!;

    private static NetResponse Ok(string body) => new()
    {
        Url = new System.Uri("https://www.vivapayments.com/web2/checkout/v2/chargetokens"),
        StatusCode = 200,
        Body = body,
        Headers = new Dictionary<string, string>(),
    };

    /// <summary>Three addresses, one version, one host.</summary>
    [Fact]
    public void TheThreeAddressesShareOneVersionAndHost()
    {
        Assert.Equal("https://www.vivapayments.com", Const("Host"));
        Assert.Equal("/web2/checkout/v2/chargetokens", Const("ChargeTokens"));
        Assert.Equal("/web2/checkout/v2/paymentdetails?ref=", Const("PaymentDetails"));
        Assert.Equal("/web2/checkout/v2/transactions", Const("Transactions"));

        Assert.Equal(3, (int)typeof(VivaPayments)
            .GetField("RecoveredAddressCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);

        // all three carry the same version segment, unlike Disney's split
        foreach (var name in new[] { "ChargeTokens", "PaymentDetails", "Transactions" })
            Assert.Contains("/v2/", Const(name));
    }

    /// <summary>A reference is found whichever of the candidate fields carries it, and the field is recorded.</summary>
    [Theory]
    [InlineData("{\"chargeToken\":\"ct-1\"}", "ct-1", "chargeToken")]
    [InlineData("{\"transactionId\":\"tx-9\"}", "tx-9", "transactionId")]
    [InlineData("{\"orderCode\":\"oc-3\"}", "oc-3", "orderCode")]
    public async Task AReferenceIsFoundAndRecorded(string body, string expected, string field)
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await VivaPayments.ChargeTokenAsync(session, "4111111111111111", "12/29", default,
            (url, b, tag, ct) => Task.FromResult<NetResponse?>(Ok(body)));

        Assert.True(outcome.Ok);
        Assert.Equal(expected, session.Vars["viva.ref"]);
        Assert.Equal(field, session.Vars["viva.refField"]);
    }

    /// <summary>
    /// The case the class exists to get right: no recognisable reference is a failure, not a half-success. A token
    /// nobody can ask about is worth nothing to the next step.
    /// </summary>
    [Fact]
    public async Task AnAnswerWithoutAReferenceFails()
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await VivaPayments.ChargeTokenAsync(session, "4111111111111111", "12/29", default,
            (url, b, tag, ct) => Task.FromResult<NetResponse?>(Ok("{\"ok\":true}")));

        Assert.False(outcome.Ok);
        Assert.False(session.Vars.ContainsKey("viva.ref"));

        // the body is still kept, so the shape can be judged later
        Assert.Equal("{\"ok\":true}", session.Vars["viva.chargeTokenBody"]);
    }

    /// <summary>The card goes to one endpoint; the status read is addressed by reference and carries no card.</summary>
    [Fact]
    public async Task TheStatusReadCarriesTheReferenceAndNoCard()
    {
        var session = new FlowSession { SessionId = "s" };
        session.Vars["viva.ref"] = "ct-1";

        string? seenUrl = null;
        var outcome = await VivaPayments.PaymentDetailsAsync(session, default, (url, ct) =>
        {
            seenUrl = url;
            return Task.FromResult<NetResponse?>(Ok("{\"status\":\"ok\"}"));
        });

        Assert.True(outcome.Ok);
        Assert.Equal("https://www.vivapayments.com/web2/checkout/v2/paymentdetails?ref=ct-1", seenUrl);
        Assert.DoesNotContain("4111", seenUrl);
    }

    /// <summary>A status read without a reference is refused before any request.</summary>
    [Fact]
    public async Task AStatusReadWithoutAReferenceIsRefused()
    {
        var called = false;
        var outcome = await VivaPayments.PaymentDetailsAsync(new FlowSession { SessionId = "s" }, default, (url, ct) =>
        {
            called = true;
            return Task.FromResult<NetResponse?>(null);
        });

        Assert.False(outcome.Ok);
        Assert.False(called);
    }

    /// <summary>The three calls are recorded in order.</summary>
    [Fact]
    public void TheStepOrderIsRecorded()
    {
        var order = (string[])typeof(VivaPayments)
            .GetField("StepOrder", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(new[] { "ChargeToken", "PaymentDetails", "Transactions" }, order);
    }
}