using System.Collections.Generic;
using Cybersole.Stores.Payments;
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
    public void TheImageCarriesThreeDistinctStripeApiVersions()
    {
        // acacia (form, 0x146adfbe0) · basil (challenge, 0x146adfc60) · clover (intent retrieve, 0x146adfc98)
        Assert.Equal("2025-01-27.acacia", StripeGateway.FormVersion);
        Assert.Equal("2025-09-30.clover", StripeGateway.IntentVersion);
        Assert.NotEqual(StripeGateway.FormVersion, StripeGateway.IntentVersion);
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
}
