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

    /// <summary>The fingerprint gate: only the decoded type stages the frozen account.</summary>
    [Fact]
    public async Task TheFingerprintGateStagesTheFrozenAccount()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, card: null);
        ctx.Session.Vars["jl.paymentsBody"] =
            "{\"next_action\":{\"use_stripe_sdk\":{\"type\":\"stripe_3ds2_fingerprint\"," +
            "\"three_d_secure_2_source\":\"src_3ds_secret_ABC123\"}}}";
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
