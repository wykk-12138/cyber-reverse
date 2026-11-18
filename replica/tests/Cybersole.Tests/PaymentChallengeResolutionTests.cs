using Cybersole.Http;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1153: who resolves a waiting PayPal challenge.
///
/// R1152 moved the resolution into <c>ProcessPayment</c>, because the flow's own ordinals put that step
/// straight after <c>SubmitPayPal</c> (SubmitPayment 44, GetPayPalToken 45, SubmitPayPal 46,
/// ProcessPayment 47) while <c>Process3DS</c> belongs to the Adyen action alone. The edge reached
/// <c>PayPalGateway.CompleteActionAsync</c>, which had no caller at all.
///
/// These facts pin the decision rather than the network: with a challenge waiting and no gateway to run
/// it, the step must say so instead of falling through to the generic classifier and reporting
/// "payment requires action" — the message that hides the fact that nothing was even attempted.
/// </summary>
public sealed class PaymentChallengeResolutionTests
{
    /// <summary>The base class is abstract; this double adds nothing, so every assertion is about the base.</summary>
    private sealed class BareFlow : StoreFlow
    {
        public override string Id => "bare";
        public override string Name => "bare";
        public override System.Collections.Generic.IReadOnlyList<string> Domains { get; } =
            new[] { "shop.example" };
    }

    private static FlowContext Context() => new()
    {
        Http = new NetClient { Transport = TransportMode.SChannel },
        Url = "https://shop.example/checkout",
    };

    [Fact]
    public async Task AWaitingChallengeWithoutAGatewayIsReportedRatherThanClassified()
    {
        var ctx = Context();
        ctx.Session.Vars["paymentStatus"] = "requires_action";
        ctx.Session.Vars["paypal3ds.state"] = "Waiting3DS";

        var outcome = await new BareFlow().ProcessPaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("no gateway", outcome.Error);
        Assert.DoesNotContain("payment requires action", outcome.Error);
    }

    /// <summary>Without the machine waiting, the classifier still owns the answer.</summary>
    [Fact]
    public async Task AClassifiedPaymentStillGoesThroughTheClassifier()
    {
        var ctx = Context();
        ctx.Session.Vars["paymentStatus"] = "requires_action";

        var outcome = await new BareFlow().ProcessPaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Equal("payment requires action", outcome.Error);
    }

    [Fact]
    public async Task AnAuthorisedPaymentSucceeds()
    {
        var ctx = Context();
        ctx.Session.Vars["paymentStatus"] = "authorised";

        var outcome = await new BareFlow().ProcessPaymentAsync(ctx, default);

        Assert.True(outcome.Ok);
    }
}
