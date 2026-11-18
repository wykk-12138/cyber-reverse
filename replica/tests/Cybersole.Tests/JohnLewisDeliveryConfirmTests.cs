using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1133: the v4 <c>deliveries</c> PUT carries <b>no body</b>.
///
/// In <c>sub_140A3F590</c> the verb call is <c>sub_1408B6310(v2, v3, 0, v4)</c> — the third argument,
/// which every other BFF call uses for its body object, is the literal <c>0</c>. So these facts pin
/// three things that a copied-and-pasted implementation gets wrong: the URL, the verb, and that the
/// request body is empty rather than <c>{}</c>.
/// </summary>
public sealed class JohnLewisDeliveryConfirmTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.deliveriesUrl"] = server.BaseUrl + "/bff/v4/orderforms/deliveries";
        return c;
    }

    [Fact]
    public async Task TheConfirmPutsWithNoBody()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " [" + body + "]");
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v4/orderforms/deliveries", request);
        // an empty body, not "{}" -- the machine passes a literal 0 for it
        Assert.EndsWith("[]", request);
    }

    [Fact]
    public async Task TheSecondStepNameHitsTheSameEndpoint()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod);
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().CreateDeliveryAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Contains("/bff/v4/orderforms/deliveries", Assert.Single(seen));
    }

    [Fact]
    public void BothStepNamesAreKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("SubmitShipping"));
        Assert.True(StepActionRunner.Knows("CreateDelivery"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (500, "boom"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().SubmitShippingAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>The default URL is the image's own literal: 0x14705db08.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v4/orderforms/deliveries",
            RetailApiFamilies.JohnLewisBff.DeliveriesV4);
    }
}
