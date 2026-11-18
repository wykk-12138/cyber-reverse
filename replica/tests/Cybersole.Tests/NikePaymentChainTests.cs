using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1086: Nike's payment chain, pinned to the decompiled <c>sub_140B35420</c> — the two GETs the
/// machine runs: <c>/InitiatePayment?singleStep=true&amp;deliveryCountryIso={country}</c> on the
/// guest-checkout Order host, then the eshopworld panel's <c>PaymentMethods?paymentId={id}</c>,
/// whose answer feeds the checkout POST's <c>paymentToken</c> (ctx field 29).
/// </summary>
public sealed class NikePaymentChainTests
{
    private static FlowContext Context(NetClient http)
    {
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://www.nike.com/launch/t/air-max-1",
            Shipping = new Address { Country = "US" },
            Card = new Card { Number = "4111111111111111", Month = "12", Year = "2030", Cvv = "123" },
        };
        ctx.Session.CartId = "ord-1";
        return ctx;
    }

    /// <summary>
    /// The first GET: the frozen composition — the OrderV5 prefix, the order id, the inline
    /// InitiatePayment segment, and the two decoded query parameters.
    /// </summary>
    [Fact]
    public async Task TheInitiateGetCarriesTheDecodedQuery()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            var path = req.Url?.AbsolutePath ?? "";
            if (path.EndsWith("/InitiatePayment")) return (200, "{\"paymentId\":\"pay-77\"}");
            return (404, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["nike.initiatePaymentUrl"] = server.BaseUrl + "/gs/checkout-api/api/v5/Order";

        var outcome = await new NikeFlow().GetPaymentMethodsAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var req = server.Requests.Single();
        Assert.Equal("GET", req.Method);
        var url = seen.Single();

        // The decoded machine's progress label went out first.
        Assert.Contains(ctx.Events, e => e.Name == "Initialize payment");
        // The query the builder assembles: singleStep=true (0x14715d7e8/0x147173de8) and
        // deliveryCountryIso (0x147001c30) ← the profile's shipping country.
        // The frozen composition: the OrderV5 prefix, the order id, the inline segment, the two
        // decoded parameters — the query follows the segment, so the segment sits inside the URL.
        Assert.Contains("/gs/checkout-api/api/v5/Order/ord-1/InitiatePayment", url);
        Assert.Contains("singleStep=true", url);
        Assert.Contains("deliveryCountryIso=US", url);
        Assert.Equal("pay-77", ctx.Session.Vars["nike.paymentId"]);
    }

    /// <summary>
    /// The second GET and the chain's purpose: the payment-methods answer's token lands on the
    /// session's PaymentToken — the field the checkout POST's paymentToken variable reads.
    /// </summary>
    [Fact]
    public async Task TheMethodsGetFeedsTheCheckoutToken()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            var path = req.Url?.PathAndQuery ?? "";
            if (path.Contains("InitiatePayment")) return (200, "{\"paymentId\":\"pay-77\"}");
            if (path.Contains("PaymentMethods")) return (200, "{\"paymentToken\":\"tok-pay-77\"}");
            return (404, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["nike.initiatePaymentUrl"] = server.BaseUrl + "/gs/checkout-api/api/v5/Order";
        ctx.Session.Vars["nike.paymentMethodsUrl"] = server.BaseUrl + "/api/v2/PaymentMethods";

        var flow = new NikeFlow();
        var outcome = await flow.SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);

        // The machine's own order: the initiate GET ran first (the step re-runs the chain's first
        // half when it has not run), then the methods GET keyed on the payment id.
        Assert.Equal(2, server.Requests.Count);
        Assert.Contains("paymentId=pay-77", seen[1]);

        // The chain's contract: ctx field 29's replica home carries the token.
        Assert.Equal("tok-pay-77", ctx.Session.PaymentToken);
    }

    /// <summary>The step reports, not guesses, when the methods answer carries no token.</summary>
    [Fact]
    public async Task AnAnswerWithoutATokenIsAFailureNotASuccess()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["nike.initiatePaymentUrl"] = server.BaseUrl + "/gs/checkout-api/api/v5/Order";
        ctx.Session.Vars["nike.paymentMethodsUrl"] = server.BaseUrl + "/api/v2/PaymentMethods";

        var outcome = await new NikeFlow().SubmitPaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("no token", outcome.Error);
        Assert.Null(ctx.Session.PaymentToken);
    }
}
