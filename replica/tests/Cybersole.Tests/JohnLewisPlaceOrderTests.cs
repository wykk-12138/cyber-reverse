using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1140: John Lewis's <c>PlaceOrder</c> — the body-less PUT to <c>v2/orders</c>.
///
/// The orders literal has exactly one data reference in the image (<c>sub_140A40F20</c>), and that
/// function sets no keys and passes a literal 0 where a body would go, so the request carries nothing:
/// everything the order needs is already on the server. Only one of the two step names can own that
/// single call, so this pins the behaviour and not the naming question.
/// </summary>
public sealed class JohnLewisPlaceOrderTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.ordersUrl"] = server.BaseUrl + "/bff/v2/orders";
        return c;
    }

    [Fact]
    public async Task TheOrderIsPlacedWithABodylessPut()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " [" + body + "]");
            return (200, "{\"orderNumber\":\"A1\"}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().PlaceOrderAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v2/orders", request);
        Assert.EndsWith("[]", request);   // no body at all
        Assert.Equal("{\"orderNumber\":\"A1\"}", ctx.Session.Vars["jl.ordersBody"]);
    }

    [Fact]
    public void TheStepNameIsKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("PlaceOrder"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (409, "already placed"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().PlaceOrderAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>
    /// SubmitOrder is deliberately not landed: only one function in the image issues the orders URL, so
    /// wiring both names would issue the PUT twice. This fact records that decision rather than a guess.
    /// </summary>
    [Fact]
    public void SubmitOrderIsLeftUnlandedSoThePutIsNotIssuedTwice()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        // the base virtual refuses rather than delegating into PlaceOrder
        var outcome = new JohnLewisFlow().SubmitOrderAsync(ctx, default).GetAwaiter().GetResult();
        Assert.False(outcome.Ok);
    }

    /// <summary>The default URL is the image's own literal: 0x14705d7cc.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v2/orders",
            RetailApiFamilies.JohnLewisBff.OrdersV2);
    }
}
