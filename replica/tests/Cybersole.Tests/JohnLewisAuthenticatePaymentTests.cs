using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1139: John Lewis's <c>AuthenticatePayment</c> — the body-less PUT on the payment page.
///
/// <c>sub_140A3FEC0</c> issues two verbs against <c>v2/orderforms/payment-page</c>: a GET on one state
/// and a PUT whose body argument is the literal 0 on another (R1132). GetPaymentPage owns the read;
/// this step owns the touch. The assignment is an inference from that shape and the name — the
/// endpoint, the verb and the absent body are observed.
/// </summary>
public sealed class JohnLewisAuthenticatePaymentTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.authenticatePaymentUrl"] =
            server.BaseUrl + "/bff/v2/orderforms/payment-page";
        return c;
    }

    [Fact]
    public async Task ThePaymentPageIsTouchedWithABodylessPut()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " [" + body + "]");
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().AuthenticatePaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v2/orderforms/payment-page", request);
        Assert.EndsWith("[]", request);   // no body at all, not an empty object
    }

    /// <summary>The read and the touch are separate steps against the same URL.</summary>
    [Fact]
    public void ThePairMapGivesTheTwoVerbsToTwoSteps()
    {
        var pairs = JohnLewisStepMap.Pairs;
        Assert.Equal(RetailApiFamilies.JohnLewisBff.PaymentPageV2, pairs["GetPaymentPage"]);
        Assert.Equal(RetailApiFamilies.JohnLewisBff.PaymentPageV2, pairs["AuthenticatePayment"]);
    }

    [Fact]
    public void TheStepNameIsKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("AuthenticatePayment"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (502, "bad gateway"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().AuthenticatePaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }
}
