using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1134: John Lewis's <c>DeliveryPage</c> step — a body-less PUT to the v3 delivery page.
///
/// <c>sub_140A3F750</c> references only its own URL and passes the literal 0 where a body would go, so
/// the request has no body. The address itself goes to a different endpoint
/// (<c>v4/orderforms/deliveries/delivery-address</c>), which is why this one is a touch rather than a
/// submission.
/// </summary>
public sealed class JohnLewisDeliveryPageTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.deliveryPageUrl"] = server.BaseUrl + "/bff/v3/orderforms/delivery-page";
        return c;
    }

    [Fact]
    public async Task ThePageIsTouchedWithABodylessPut()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " [" + body + "]");
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().DeliveryPageAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v3/orderforms/delivery-page", request);
        Assert.EndsWith("[]", request);   // empty body, not an empty object
    }

    [Fact]
    public void TheStepNameIsKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("DeliveryPage"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (503, "busy"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().DeliveryPageAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>The default URL is the image's own literal: 0x14705d960.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v3/orderforms/delivery-page",
            RetailApiFamilies.JohnLewisBff.DeliveryPageV3);
    }
}
