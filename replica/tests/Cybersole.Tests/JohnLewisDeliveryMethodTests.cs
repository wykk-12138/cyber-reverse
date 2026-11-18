using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1135: John Lewis's <c>SubmitDeliveryMethod</c> — a POST to the v3 <c>deliveries/details</c>.
///
/// The body is read off <c>sub_140A428D0</c>: <c>deliveryId</c> plus an inner object holding
/// <c>fulfilmentOfferId</c> under <c>fulfilment</c>, and that pair goes into a <b>single-element
/// array</b> stored under <c>deliveries</c>. The array is the part a flat reading gets wrong, so these
/// facts pin it rather than only the keys.
/// </summary>
public sealed class JohnLewisDeliveryMethodTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.deliveryDetailsUrl"] = server.BaseUrl + "/bff/v3/orderforms/deliveries/details";
        c.Session.Vars["jl.deliveryId"] = "d-9";
        c.Session.Vars["jl.fulfilmentOfferId"] = "f-31";
        return c;
    }

    [Fact]
    public async Task TheBodyWrapsOneDeliveryInAnArray()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " " + body);
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().SubmitDeliveryMethodAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("POST", request.Split(' ')[1]);
        Assert.Contains("/bff/v3/orderforms/deliveries/details", request);

        // the array wrapper and the nested fulfilment object, in the order the machine builds them
        Assert.Contains(
            "\"deliveries\":[{\"deliveryId\":\"d-9\",\"fulfilment\":{\"fulfilmentOfferId\":\"f-31\"}}]",
            request);
    }

    [Fact]
    public async Task NoDeliveryIdStopsTheStep()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);
        ctx.Session.Vars.Remove("jl.deliveryId");

        var outcome = await new JohnLewisFlow().SubmitDeliveryMethodAsync(ctx, default);

        Assert.False(outcome.Ok);
    }

    [Fact]
    public void TheStepNameIsKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("SubmitDeliveryMethod"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (409, "gone"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().SubmitDeliveryMethodAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>The default URL is the image's own literal: 0x14705d8c0.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v3/orderforms/deliveries/details",
            RetailApiFamilies.JohnLewisBff.DeliveryDetailsV3);
    }
}
