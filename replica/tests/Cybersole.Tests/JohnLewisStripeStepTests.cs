using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1089: John Lewis's <c>SubmitOrderStripe</c>, pinned to the decoded payments machine
/// (<c>sub_140a42bc0</c>) — a PUT to the BFF's <c>v2/orderforms/payments</c> with the two
/// parameters the machine assembles, gated by the method the context selected.
/// </summary>
public sealed class JohnLewisStripeStepTests
{
    private static FlowContext Context(NetClient http, Card? card) => new()
    {
        Http = http,
        Url = "https://www.johnlewis.com/ourshop/product",
        Shipping = new Address { Country = "GB" },
        Card = card,
    };

    /// <summary>
    /// The request contract: a PUT carrying <c>methodId</c> (0x1470c29a0) and
    /// <c>setupFutureUsage</c> (0x147159a48) on the payments endpoint.
    /// </summary>
    [Fact]
    public async Task ThePaymentsPutCarriesTheDecodedParameters()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod);
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, new Card { Number = "4242424242424242", Month = "12", Year = "2030", Cvv = "737" });
        ctx.Session.Vars["jl.paymentsUrl"] = server.BaseUrl + "/bff/v2/orderforms/payments";
        ctx.Session.Vars["jl.methodId"] = "m-41";

        var outcome = await new JohnLewisFlow().SubmitOrderStripeAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = seen.Single();
        Assert.EndsWith("PUT", request);
        Assert.Contains("/bff/v2/orderforms/payments", request);
        Assert.Contains("methodId=m-41", request);
        Assert.Contains("setupFutureUsage=false", request);   // the decoded flag's off state
        Assert.Equal("{\"ok\":true}", ctx.Session.Vars["jl.paymentsBody"]);
    }

    /// <summary>
    /// The machine's CREDITCARD gate: the method the context selected decides the continuation —
    /// a credit-card method with no card loaded stops the step instead of driving the chain.
    /// </summary>
    [Fact]
    public async Task TheCreditCardGateStopsWhenNoCardIsLoaded()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsUrl"] = server.BaseUrl + "/bff/v2/orderforms/payments";
        ctx.Session.Vars["jl.methodId"] = "m-41";
        ctx.Session.Vars["jl.paymentMethod"] = "CREDITCARD";

        var outcome = await new JohnLewisFlow().SubmitOrderStripeAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("no card", outcome.Error);
    }

    /// <summary>No method id to submit with is a retryable stop, not a guessed request.</summary>
    [Fact]
    public async Task NoMethodIdIsARetryableStop()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, new Card { Number = "4242424242424242" });
        ctx.Session.Vars["jl.paymentsUrl"] = server.BaseUrl + "/bff/v2/orderforms/payments";

        var outcome = await new JohnLewisFlow().SubmitOrderStripeAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
        Assert.Contains("no payment method id", outcome.Error);
        Assert.Empty(server.Requests);   // nothing went out on the wire
    }

    /// <summary>
    /// R1090: the intent read's needle chain — next_action.use_stripe_sdk.type gated on
    /// stripe_3ds2_fingerprint, the three_d_secure_2_source staged, the '_secret_' split.
    /// </summary>
    [Fact]
    public async Task TheIntentReadPullsTheDecodedNeedleChain()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";

        var outcome = await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("stripe_3ds2_fingerprint", ctx.Session.Vars["jl.stripeSdkType"]);
        Assert.Equal("src_3ds_secret_ABC123", ctx.Session.Vars["jl.threeDs2Source"]);
        Assert.Equal("ABC123", ctx.Session.Vars["jl.stripeSecret"]);   // the '_secret_' needle split
    }

    /// <summary>
    /// R1091: the process wall — the STRIPE channel's opening line carries the intent, the frozen
    /// merchant account, and the staged source, verbatim from the decoded machine.
    /// </summary>
    [Fact]
    public async Task TheProcessWallOpensOnTheStripeChannel()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"id\":\"pi_77\",\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
        ctx.Session.Vars["stripe.hooksUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        var outcome = await new JohnLewisFlow().HandleRequiresActionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Contains(ctx.Events, e =>
            e.Name == "Process start: payment_intent=pi_77 merchant=acct_1S0JRiIiwyy5Cf6X " +
                     "source=src_3ds_secret_ABC123"
            && e.Type == "STRIPE");
    }

    /// <summary>
    /// R1092: the chain's first request — a GET of the hosted challenge page on Stripe's hooks
    /// surface, the five composed segments verbatim, with the return URL reported back.
    /// </summary>
    [Fact]
    public async Task TheHostedGetCarriesTheFiveComposedSegments()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            return (200, "{\"returnUrl\":\"https://checkout.johnlewis.com/back\"}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"id\":\"pi_77\",\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
        ctx.Session.Vars["stripe.hooksUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.publishableKey"] = "pk_jl";
        await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        var outcome = await new JohnLewisFlow().HandleRequiresActionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        // R1093 added the intent confirm after the hosted page; this pin is about the hosted GET.
        var url = seen.First(u => u.Contains("3d_secure_2/hosted"));
        Assert.Contains("/3d_secure_2/hosted", url);
        Assert.Contains("merchant=acct_1S0JRiIiwyy5Cf6X", url);
        Assert.Contains("payment_intent=pi_77", url);
        Assert.Contains("payment_intent_client_secret=ABC123", url);
        Assert.Contains("publishable_key=pk_jl", url);
        Assert.Contains("source=src_3ds_secret_ABC123", url);

        // The machine's report line, on the STRIPE channel with the answer's return URL.
        Assert.Contains(ctx.Events, e =>
            e.Name == "GetHostedPage: returnUrl=https://checkout.johnlewis.com/back"
            && e.Type == "STRIPE");
        Assert.Equal("https://checkout.johnlewis.com/back", ctx.Session.Vars["jl.hostedReturnUrl"]);
    }

    /// <summary>
    /// R1093: the chain's second request — the intent confirm as a GET on the v1 surface with
    /// the JL variant's own segments (is_stripe_sdk, client_secret, key, _stripe_account), and
    /// the chain's closing line on the STRIPE channel.
    /// </summary>
    [Fact]
    public async Task TheIntentConfirmGetCarriesTheJlSegmentsAndClosesTheChain()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            if ((req.Url?.AbsolutePath ?? "").Contains("3d_secure_2/hosted"))
                return (200, "{\"returnUrl\":\"https://checkout.johnlewis.com/back\"}");
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"id\":\"pi_77\",\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
        ctx.Session.Vars["stripe.hooksUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.publishableKey"] = "pk_jl";
        await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        var outcome = await new JohnLewisFlow().HandleRequiresActionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        // R1094 put the 3DS2 pair after the confirm; this pin is about the intent confirm itself.
        var confirm = seen.First(u => u.Contains("/v1/payment_intents/"));

        // The confirm is the /v1 intent URL with the four JL segments, in the machine's order.
        Assert.Contains("/v1/payment_intents/pi_77", confirm);
        Assert.Contains("is_stripe_sdk=true", confirm);
        Assert.Contains("client_secret=ABC123", confirm);
        Assert.Contains("key=pk_jl", confirm);
        Assert.Contains("_stripe_account=acct_1S0JRiIiwyy5Cf6X", confirm);

        // The chain's closing line, verbatim, on the same channel.
        Assert.Contains(ctx.Events, e => e.Name == "Process complete" && e.Type == "STRIPE");
    }

    /// <summary>
    /// R1094: the chain's tail — the fingerprint submit to 3ds2/authenticate (twelve-key browser
    /// object, the one_click family driven by the has-form flag, key and _stripe_account), then
    /// the notify hop and the challenge_complete PUT with final_cres.
    /// </summary>
    [Fact]
    public async Task TheFingerprintSubmitAndCompletionRunInMachineOrder()
    {
        var seen = new System.Collections.Generic.List<string>();
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.PathAndQuery ?? "";
            seen.Add(path);
            bodies.Add(body);
            if (path.Contains("3d_secure_2/hosted"))
                return (200, "{\"returnUrl\":\"https://checkout.johnlewis.com/back\"}");
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"id\":\"pi_77\",\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
        ctx.Session.Vars["stripe.hooksUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.publishableKey"] = "pk_jl";
        ctx.Session.Vars["jl.finalCres"] = "cres-answer";              // the window answered
        ctx.Session.Vars["jl.threeDsServerTransId"] = "txn-9";
        await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        var outcome = await new JohnLewisFlow().HandleRequiresActionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);

        // The machine's own order across the whole chain.
        Assert.Equal(5, seen.Count);
        Assert.Contains("3d_secure_2/hosted", seen[0]);
        Assert.Contains("/v1/payment_intents/pi_77", seen[1]);
        Assert.Equal("/v1/3ds2/authenticate", seen[2]);
        Assert.Contains("/3d_secure_2/notify/", seen[3]);
        Assert.Equal("/v1/3ds2/challenge_complete", seen[4]);

        // The fingerprint form: twelve browser keys, the one_click family, key, account.
        var auth = bodies[2];
        Assert.Contains("source=src_3ds_secret_ABC123", auth);
        Assert.Contains("one_click_authn_device_support%5Bhosted%5D=true", auth);
        Assert.Contains("one_click_authn_device_support%5Bwebauthn_eligible%5D=true", auth);
        Assert.Contains("one_click_authn_device_support%5Bspc_eligible%5D=true", auth);  // has-form → true
        Assert.Contains("key=pk_jl", auth);
        Assert.Contains("_stripe_account=acct_1S0JRiIiwyy5Cf6X", auth);
        Assert.Contains("browserScreenWidth", auth);
        Assert.Contains("browserTZ", auth);

        // The completion carries final_cres.
        Assert.Contains("final_cres=cres-answer", bodies[4]);

        // The machine's report lines, in order.
        Assert.Contains(ctx.Events, e => e.Name.StartsWith("SubmitFingerprint: methodUrl='") &&
                                         e.Name.Contains("fingerprintAvailable=true") && e.Type == "STRIPE");
        Assert.Contains(ctx.Events, e =>
            e.Name == "CompletePayment: notify serverTransactionId=txn-9" && e.Type == "STRIPE");
    }

    /// <summary>
    /// Without a challenge form the fingerprint block reports its own not_supported outcome and
    /// the one_click family flips to false where the has-form flag drives it.
    /// </summary>
    [Fact]
    public async Task TheNoFormFingerprintReportsNotSupported()
    {
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, body) =>
        {
            bodies.Add(body);
            var path = req.Url?.PathAndQuery ?? "";
            if (path.Contains("3d_secure_2/hosted")) return (200, "{\"returnUrl\":\"x\"}");
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"id\":\"pi_77\",\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
        ctx.Session.Vars["stripe.hooksUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.publishableKey"] = "pk_jl";
        await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        var outcome = await new JohnLewisFlow().HandleRequiresActionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var auth = bodies[2];
        Assert.Contains("fingerprintOutcome=not_supported", auth);
        Assert.Contains("one_click_authn_device_support%5Bspc_eligible%5D=false", auth);   // !has-form
        Assert.Contains("one_click_authn_device_support%5Bhosted%5D=true", auth);          // always true

        Assert.Contains(ctx.Events, e => e.Name.Contains("fingerprintAvailable=false") &&
                                         e.Type == "STRIPE");
    }

    /// <summary>The no-3DS stop line is the machine's own message, on the same channel.</summary>
    [Fact]
    public async Task TheNoSourceAnswerSpeaksTheMachinesStopLine()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] = "{\"next_action\":{}}";

        var outcome = await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Contains(ctx.Events, e =>
            e.Name == "Process: no 3DS source after GetPaymentIntent - no authentication required"
            && e.Type == "STRIPE");
    }

    /// <summary>The fingerprint gate: only the decoded type stages the frozen account.</summary>
    [Fact]
    public async Task TheFingerprintGateStagesTheFrozenAccount()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
        ctx.Session.Vars["stripe.hooksUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        var outcome = await new JohnLewisFlow().HandleRequiresActionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(JohnLewisFlow.StripeAccount, ctx.Session.Vars["jl.stripeAccount"]);
        Assert.Equal("acct_1S0JRiIiwyy5Cf6X", JohnLewisFlow.StripeAccount);   // the frozen literal

        // Any other action type leaves the account unstaged.
        var other = Context(new NetClient { Transport = TransportMode.SChannel }, card: null);
        other.Session.Vars["jl.paymentsBody"] =
            "{\"next_action\":{\"use_stripe_sdk\":{\"type\":\"redirect_to_url\"," +
            "\"three_d_secure_2_source\":\"src_9\"}}}";
        await new JohnLewisFlow().GetStripePaymentIntentAsync(other, default);
        await new JohnLewisFlow().HandleRequiresActionAsync(other, default);
        Assert.False(other.Session.Vars.ContainsKey("jl.stripeAccount"));
    }

    /// <summary>No payments answer to read from is a retryable stop, not a guessed request.</summary>
    [Fact]
    public async Task NoPaymentsAnswerIsARetryableStop()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);

        var outcome = await new JohnLewisFlow().GetStripePaymentIntentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
        Assert.Contains("no payments answer", outcome.Error);
    }
}
