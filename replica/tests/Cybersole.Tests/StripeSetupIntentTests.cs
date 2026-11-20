using System.Collections.Generic;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1214: the setup-intent confirm form, decoded from <c>sub_140BE0F80</c> (2,844 bytes).
///
/// <para>
/// The replica had no <c>payment_method_data[...]</c> keys at all before this — the payment-method create uses
/// its own <c>card[...]</c> family and the 3DS2 forms use browser/fingerprint keys, so this surface is a distinct
/// one. Every assertion below names the frozen literal it comes from, so a future round can re-check the decode
/// rather than trust it.
/// </para>
/// </summary>
public sealed class StripeSetupIntentTests
{
    private static readonly StripeGateway.CardDetails Card =
        new("4242424242424242", "737", "12", "2030");

    [Fact]
    public void ConfirmUrlIsTheFrozenPrefixPlusIdPlusConfirm()
    {
        // 0x147054fe0 + 0x146ab3a08
        Assert.Equal("https://api.stripe.com/v1/setup_intents/setup_intent_123/confirm",
            StripeGateway.SetupConfirmUrl("setup_intent_123"));
    }

    [Fact]
    public void ConfirmUrlEscapesTheId()
    {
        Assert.EndsWith("/set%2F..%2Fx/confirm", StripeGateway.SetupConfirmUrl("set/../x"));
    }

    [Fact]
    public void RetrieveUrlIsTheIntentPlusTheThreeFrozenFragments()
    {
        // 0x147054fe0 + 0x146b28808 + 0x146a84588 + 0x146a7afd8, the whole constant set of sub_141145DB0
        Assert.Equal(
            "https://api.stripe.com/v1/setup_intents/si_1?is_stripe_sdk=true&client_secret=sec&key=pk&_stripe_account=acct",
            StripeGateway.SetupIntentRetrieveUrl("si_1", "sec", "pk", "acct"));
    }

    [Fact]
    public void RetrieveUrlKeepsTheAccountSlotEvenWhenEmpty()
    {
        // the image appends the fragment unconditionally; dropping it would change the request shape
        Assert.EndsWith("&_stripe_account=", StripeGateway.SetupIntentRetrieveUrl("si_1", "sec", "pk"));
    }

    [Fact]
    public void RetrieveUrlEscapesEveryPart()
    {
        var url = StripeGateway.SetupIntentRetrieveUrl("a/b", "s+c", "p k", "x&y");
        Assert.Contains("/a%2Fb?", url);
        Assert.Contains("client_secret=s%2Bc", url);
        Assert.Contains("key=p%20k", url);
        Assert.Contains("_stripe_account=x%26y", url);
    }

    [Fact]
    public void ThePaymentIntentRetrieveIsTheOtherShapeFromTheJohnLewisConfirm()
    {
        // sub_140A40170 vs sub_1411458f0: false and a pinned version, against true and none
        var url = StripeGateway.PaymentIntentRetrieveUrl("pi_1", "sec", "pk", "acct");
        Assert.StartsWith("https://api.stripe.com/v1/payment_intents/pi_1?is_stripe_sdk=false&client_secret=", url);
        Assert.Contains("&_stripe_version=2025-09-30.clover", url);
        Assert.Contains("&key=pk", url);
        Assert.Contains("&_stripe_account=acct", url);
        Assert.DoesNotContain("is_stripe_sdk=true", url);
    }

    [Fact]
    public void ThePaymentIntentRetrieveHasTwoVersionPinsThatDifferOnlyInTheVersion()
    {
        // sub_140A40170 pins clover (0x146ADFC98); sub_14095B6C0 pins basil (0x146ADFC60) on the same five literals
        var clover = StripeGateway.PaymentIntentRetrieveUrl("pi_1", "sec", "pk");
        var basil = StripeGateway.PaymentIntentRetrieveUrlBasil("pi_1", "sec", "pk");

        Assert.Contains("_stripe_version=" + StripeGateway.IntentVersion, clover);
        Assert.Contains("_stripe_version=" + StripeGateway.ChallengeVersion, basil);
        Assert.Equal(clover.Replace(StripeGateway.IntentVersion, "X"),
            basil.Replace(StripeGateway.ChallengeVersion, "X"));
    }

    [Fact]
    public void TheTwoPinsAreTheImagesOwnValues()
    {
        Assert.Equal("2025-09-30.clover", StripeGateway.IntentVersion);
        Assert.Equal("2025-08-27.basil", StripeGateway.ChallengeVersion);
        Assert.NotEqual(StripeGateway.IntentVersion, StripeGateway.ChallengeVersion);
    }

    [Fact]
    public void TheImageCarriesThreeDistinctStripeApiVersions()
    {
        // acacia (form, 0x146adfbe0) · basil (challenge, 0x146adfc60) · clover (intent retrieve, 0x146adfc98)
        Assert.Equal("2025-01-27.acacia", StripeGateway.FormVersion);
        Assert.Equal("2025-09-30.clover", StripeGateway.IntentVersion);
        Assert.NotEqual(StripeGateway.FormVersion, StripeGateway.IntentVersion);
    }

    [Fact]
    public void ThePayPalConfirmCarriesTheMandateFamily()
    {
        // 0x1470be0c0 / 0x1471085e8 / 0x1470be030 — none of these existed in the replica before R1217
        var f = StripeGateway.PayPalConfirmForm("pm_1", "sec", "pk", "https://shop/thanks", "true");
        Assert.Equal("paypal", f["payment_method_data[type]"]);
        Assert.Equal("paypal", f["expected_payment_method_type"]);
        Assert.Equal("online", f["mandate_data[customer_acceptance][type]"]);
        Assert.Equal("true", f["mandate_data[customer_acceptance][online][infer_from_client]"]);
        Assert.Equal("https://shop/thanks", f["return_url"]);
        Assert.Equal("pm_1", f["payment_method"]);
    }

    [Fact]
    public void TheInferFlagIsAParameterBecauseThePairingIsNotObservable()
    {
        // the function holds a bare `true` at 0x147173de8 but the decompiler does not tie it to the slot
        var no = StripeGateway.PayPalConfirmForm("pm_1", "sec", "pk", "https://shop/thanks", "false");
        Assert.Equal("false", no["mandate_data[customer_acceptance][online][infer_from_client]"]);
    }

    [Fact]
    public void ThereAreThreeDifferentStripeUserAgentsAndTheyMustStayDifferent()
    {
        // 0x1471655c8 (payment-element/autopm) · 0x1471654a0 (card-element) · 0x1471659d8 (paypal, d6356e1526)
        var agents = new[]
        {
            StripeGateway.PaymentUserAgent,
            StripeGateway.CardElementUserAgent,
            StripeGateway.PayPalConfirmUserAgent,
        };
        Assert.Equal(3, System.Linq.Enumerable.Count(System.Linq.Enumerable.Distinct(agents)));
        Assert.Contains("d6356e1526", StripeGateway.PayPalConfirmUserAgent);
    }

    [Fact]
    public void TheCardElementUserAgentIsTheOtherSurfaceNotThePaymentElementOne()
    {
        // 0x1471654a0 vs the payment-method create's 0x1471655c8
        Assert.Equal("stripe.js/035decdc6c; stripe-js-v3/035decdc6c; card-element",
            StripeGateway.CardElementUserAgent);
        Assert.NotEqual(StripeGateway.PaymentUserAgent, StripeGateway.CardElementUserAgent);
    }

    [Fact]
    public void TheFormCarriesThePaymentMethodDataFamily()
    {
        var f = StripeGateway.SetupConfirmForm("si_1", "secret_1", "pk_1", Card);

        // every key below is a frozen literal in sub_140BE0F80
        Assert.Equal("card", f["payment_method_data[type]"]);
        Assert.Equal("4242424242424242", f["payment_method_data[card][number]"]);
        Assert.Equal("737", f["payment_method_data[card][cvc]"]);
        Assert.Equal("12", f["payment_method_data[card][exp_month]"]);
        Assert.Equal("2030", f["payment_method_data[card][exp_year]"]);
        Assert.Equal(StripeGateway.CardElementUserAgent, f["payment_method_data[payment_user_agent]"]);
        Assert.Equal(StripeGateway.TimeOnPage, f["payment_method_data[time_on_page]"]);
    }

    [Fact]
    public void TheFormCarriesTheSdkFlagsAndTheSecret()
    {
        // 0x147179510 / 0x147173de8 / 0x146fcb508 / 0x1470ae940 / 0x147020f28
        var f = StripeGateway.SetupConfirmForm("si_1", "secret_1", "pk_1", Card);
        Assert.Equal("true", f["use_stripe_sdk"]);
        Assert.Equal("secret_1", f["client_secret"]);
        Assert.Equal("pk_1", f["key"]);
        Assert.Equal("card", f["expected_payment_method_type"]);
    }

    [Fact]
    public void TheAttributionMetadataAppearsBothNestedAndTopLevel()
    {
        var f = StripeGateway.SetupConfirmForm("si_1", "secret_1", "pk_1", Card,
            integrationSource: "elements", integrationVersion: "2017");
        Assert.Equal("elements", f["client_attribution_metadata[merchant_integration_source]"]);
        Assert.Equal("2017", f["client_attribution_metadata[merchant_integration_version]"]);
        Assert.Equal("elements",
            f["payment_method_data[client_attribution_metadata][merchant_integration_source]"]);
        Assert.Equal("2017",
            f["payment_method_data[client_attribution_metadata][merchant_integration_version]"]);
    }

    [Fact]
    public void TheRadarCaptchaTokenIsOnlySentWhenThereIsOne()
    {
        // 0x147148170 — the wall hands over an hCaptcha token or the key is absent
        var without = StripeGateway.SetupConfirmForm("si_1", "secret_1", "pk_1", Card);
        Assert.False(without.ContainsKey("radar_options[hcaptcha_token]"));

        var with = StripeGateway.SetupConfirmForm("si_1", "secret_1", "pk_1", Card, hcaptchaToken: "tok");
        Assert.Equal("tok", with["radar_options[hcaptcha_token]"]);
    }

    private static FlowContext Context(NetClient http, string baseUrl)
    {
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://www.casio.com/checkout",
            Shipping = new Address { Country = "GB" },
            Card = new Card { Number = Card.Number, Cvv = Card.Cvc, Month = Card.ExpMonth, Year = Card.ExpYear },
        };
        ctx.Session.Vars["stripe.apiUrl"] = baseUrl;
        return ctx;
    }

    [Fact]
    public async Task RetrieveAndConfirmRuntimeMethodsHitExpectedStripeEndpoints()
    {
        var seenQueries = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seenQueries.Add(req.Url?.PathAndQuery ?? "");
            var path = req.Url?.AbsolutePath ?? "";
            if (req.HttpMethod == "GET" && path == "/v1/payment_intents/pi_basil")
                return (200, "{\"id\":\"pi_basil\",\"status\":\"requires_action\",\"client_secret\":\"sec_b\",\"next_action\":{\"source\":\"src_casio\",\"redirect_to_url\":{\"url\":\"https://hooks.stripe.com/3ds\"}}}");
            if (req.HttpMethod == "GET" && path == "/v1/setup_intents/si_1")
                return (200, "{\"id\":\"si_1\",\"status\":\"succeeded\"}");
            if (req.HttpMethod == "POST" && path == "/v1/setup_intents/si_1/confirm")
                return (200, "{\"id\":\"si_1\",\"status\":\"succeeded\"}");
            if (req.HttpMethod == "POST" && path == "/v1/payment_intents/pi_pp/confirm")
                return (200, "{\"id\":\"pi_pp\",\"status\":\"succeeded\"}");
            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);
        var gw = new StripeGateway();

        // 1. PaymentIntent retrieve with basil pin (Casio sub_14095B6C0)
        var piRes = await gw.RetrievePaymentIntentAsync(
            ctx, "pi_basil", "sec_b", "pk_1", "acct_1", StripeGateway.ChallengeVersion);
        Assert.False(piRes.Ok);
        Assert.Equal("src_casio", ctx.Session.Vars["stripe.threeDs2Source"]);
        Assert.Equal("pi_basil", ctx.Session.Vars["stripe.intentId"]);
        Assert.Contains("_stripe_version=2025-08-27.basil", seenQueries[0]);

        // 2. SetupIntent retrieve (sub_141145DB0)
        var siGet = await gw.RetrieveSetupIntentAsync(ctx, "si_1", "sec_s", "pk_1", "acct_1");
        Assert.True(siGet.Ok, siGet.Error);
        Assert.Contains("is_stripe_sdk=true", seenQueries[1]);

        // 3. SetupIntent confirm (Above The Clouds sub_140BE0F80)
        var siPost = await gw.ConfirmSetupIntentAsync(ctx, "si_1", "sec_s", "pk_1", Card, hcaptchaToken: "hc_1");
        Assert.True(siPost.Ok, siPost.Error);
        Assert.Contains("payment_method_data%5Btype%5D=card", server.Requests[2].Body);
        Assert.Contains("radar_options%5Bhcaptcha_token%5D=hc_1", server.Requests[2].Body);

        // 4. PayPal-on-Stripe confirm (Highsnobiety sub_140B58D60)
        var ppPost = await gw.ConfirmPayPalIntentAsync(
            ctx, "pi_pp", "pm_pp", "sec_p", "pk_1", "https://highsnobiety.com/thanks", "true");
        Assert.True(ppPost.Ok, ppPost.Error);
        Assert.Contains("expected_payment_method_type=paypal", server.Requests[3].Body);
        Assert.Contains("payment_method=pm_pp", server.Requests[3].Body);
    }
}
