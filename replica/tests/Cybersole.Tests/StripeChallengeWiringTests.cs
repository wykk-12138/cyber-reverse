using System;
using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1282: the orange-wall confirm on the main payment chain, not as an island.
///
/// <para>
/// Before this round <c>StripeChallenge.ConfirmAsync</c> had no caller anywhere in src. These tests drive
/// <c>StripeGateway.AuthorizeAsync</c> end to end against a local server: the intent answer carries CAPTCHA_REQUIRED,
/// the confirm PUTs the five fields to the per-order path, and only then does the intent call happen again. The marker
/// is the image's own token (0x146B65A14), which is what decides the step runs.
/// </para>
/// </summary>
public sealed class StripeChallengeWiringTests
{
    [Fact]
    public async Task TheChallengeRunsOnTheChainAndTheIntentIsRetried()
    {
        var intents = 0;
        using var server = new TinyServer((request, _) =>
        {
            var path = request.Url?.AbsolutePath ?? "/";
            if (path.StartsWith("/v1/payment_intents", StringComparison.Ordinal))
            {
                intents++;
                return intents == 1
                    ? (200, "{\"id\":\"pi_1\",\"status\":\"requires_action\",\"last_payment_error\":{\"code\":\"CAPTCHA_REQUIRED\"}}")
                    : (200, "{\"id\":\"pi_1\",\"status\":\"succeeded\"}");
            }

            return (200, "{\"challenge\":\"cleared\"}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = StripeContext(http, server.BaseUrl, "tok-e2e");

        var result = await new StripeGateway().AuthorizeAsync(ctx, default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal("pi_1", result.GatewayReference);

        var paths = server.Requests.Select(r => r.Method + " " + r.Path).ToList();
        // the exact order is the assertion: wall first, then the same form again
        Assert.Equal(new[]
        {
            "POST /v1/payment_intents",
            "PUT /challenge/confirm",
            "POST /v1/payment_intents",
        }, paths);

        Assert.Equal(
            "challenge_response_token=tok-e2e&challenge_response_ekey=&client_secret=sec_e2e" +
            "&captcha_vendor_name=hcaptcha&key=pk_e2e",
            server.Requests.Single(r => r.Path == "/challenge/confirm").Body);
    }

    [Fact]
    public async Task AChallengeWithNoTokenSendsNothingAndDoesNotRetry()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"id\":\"pi_2\",\"status\":\"requires_action\",\"last_payment_error\":{\"code\":\"CAPTCHA_REQUIRED\"}}"));

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = StripeContext(http, server.BaseUrl, null);

        var result = await new StripeGateway().AuthorizeAsync(ctx, default);

        Assert.False(result.Ok);
        Assert.Contains("no captcha token", result.Error);
        Assert.Equal(1, server.Requests.Count);
        Assert.Equal("POST", server.Requests[0].Method);
    }

    private static FlowContext StripeContext(NetClient http, string baseUrl, string? token)
    {
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://shop.test/checkout",
        };

        ctx.Session.Vars["stripe.apiUrl"] = baseUrl;
        // the method id is a session property, not a var: setting the var left TokenizeAsync to run and fail on no card
        ctx.Session.PaymentMethodId = "pm_e2e";
        ctx.Session.Vars["stripe.publishableKey"] = "pk_e2e";
        ctx.Session.Vars["stripe.clientSecret"] = "sec_e2e";
        ctx.Session.Vars["stripe.challengePath"] = "/challenge/confirm";
        if (token is not null) ctx.Session.Vars["stripe.challengeToken"] = token;

        return ctx;
    }
}
