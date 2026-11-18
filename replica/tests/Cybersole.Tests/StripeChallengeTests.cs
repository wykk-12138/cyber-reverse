using System.Linq;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1080: Stripe's checkout challenge, pinned to the decompiled <c>sub_140BE31F0</c> — the orange
/// wall, the hCaptcha confession form, and the PUT to the frozen <c>https://api.stripe.com</c>
/// literal (0x147054DD8) with the per-checkout path riding the context.
/// </summary>
public sealed class StripeChallengeTests
{
    private static StripeChallenge.ChallengeInput Sample() => new()
    {
        CaptchaToken = "tok-1234",
        ClientSecret = "sec_iy7",
        PublishableKey = "pk_live_xx",
        Path = "/v1/payment_intents/pi_9/confirm",
    };

    private static FlowContext Context(NetClient http) => new()
    {
        Http = http,
        Url = "https://checkout.example.test/pay",
    };

    /// <summary>The frozen literals: host, statuses, wall kind, colour, vendor.</summary>
    [Fact]
    public void TheConstantsMatchTheFrozenLiterals()
    {
        Assert.Equal("https://api.stripe.com", StripeChallenge.ApiHost);
        Assert.Equal("Solving Stripe challenge", StripeChallenge.SolvingStatus);
        Assert.Equal("orange", StripeChallenge.WallKind);       // not PayPal's white
        Assert.Equal("Waiting for captcha", StripeChallenge.WaitingForCaptcha);
        Assert.Equal("Stripe challenge captcha failed", StripeChallenge.CaptchaFailedStatus);
        Assert.Equal("#FB4961", StripeChallenge.CaptchaFailedColour);   // the image's own colour code
        Assert.Equal("hcaptcha", StripeChallenge.CaptchaVendor);
    }

    /// <summary>The five-field form, in the encoder's own order, with the empty ekey sentinel.</summary>
    [Fact]
    public void TheFormMatchesTheDecompiledContract()
    {
        var f = StripeChallenge.Form(Sample());

        Assert.Equal(5, f.Count);
        Assert.Equal(new[]
        {
            "challenge_response_token", "challenge_response_ekey", "client_secret",
            "captcha_vendor_name", "key",
        }, f.Keys.ToArray());
        Assert.Equal("tok-1234", f["challenge_response_token"]);
        Assert.Equal(string.Empty, f["challenge_response_ekey"]);   // the empty-string sentinel
        Assert.Equal("sec_iy7", f["client_secret"]);
        Assert.Equal("hcaptcha", f["captcha_vendor_name"]);
        Assert.Equal("pk_live_xx", f["key"]);
    }

    /// <summary>
    /// The confirm step PUTs the urlencoded form to the stripe host plus the context's path, and
    /// hangs the orange wall plus the captcha-wait label before it.
    /// </summary>
    [Fact]
    public async Task TheConfirmPutsTheFormToTheStripeHost()
    {
        using var server = new TinyServer((_, _) => (200, "{\"ok\":true}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await StripeChallenge.ConfirmAsync(ctx, Sample(), default, server.BaseUrl);

        Assert.True(outcome.Ok);
        Assert.Equal(200, outcome.Status);
        Assert.Equal("{\"ok\":true}", outcome.Body);

        Assert.Equal("PUT", server.Requests.Single().Method);
        Assert.Equal("/", server.Requests.Single().Path);
        Assert.Equal(
            "challenge_response_token=tok-1234&challenge_response_ekey=&client_secret=sec_iy7" +
            "&captcha_vendor_name=hcaptcha&key=pk_live_xx",
            server.Requests.Single().Body);

        Assert.Equal(StripeChallenge.SolvingStatus, ctx.Events[0].Name);
        Assert.Equal("StatusInfo", ctx.Events[0].Type);
        Assert.Equal(StripeChallenge.WaitingForCaptcha, ctx.Events[1].Name);
    }

    /// <summary>
    /// Without a captcha token the step reports the failed status with its colour and sends nothing —
    /// the original's failure branch, not a silent success.
    /// </summary>
    [Fact]
    public async Task NoTokenReportsTheFailedStatusAndSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await StripeChallenge.ConfirmAsync(ctx,
            new StripeChallenge.ChallengeInput { ClientSecret = "s", PublishableKey = "k", Path = "/x" },
            default, server.BaseUrl);

        Assert.False(outcome.Ok);
        Assert.Empty(server.Requests);
        Assert.Contains(ctx.Events, e => e.Name == StripeChallenge.CaptchaFailedStatus
                                         && e.Type == StripeChallenge.CaptchaFailedColour);
    }
}
