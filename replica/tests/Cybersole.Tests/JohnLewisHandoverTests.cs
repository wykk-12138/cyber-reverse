using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1130: John Lewis's hand-over — a PUT to <c>v2/sessions/web/handover</c>.
///
/// The image names this one endpoint twice (step ordinals 23 and 24, <c>WebHandOver</c> and
/// <c>SessionHandover</c>), so both names have to reach it. The body's nesting is read off
/// <c>sub_140A410E0</c>: the three <c>time*</c> keys land on the inner object that <c>timestamps</c>
/// then points at, while <c>express</c>, <c>basketId</c> and <c>discountsInBasketUIEnabled</c> sit on
/// the root.
/// </summary>
public sealed class JohnLewisHandoverTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.handoverUrl"] = server.BaseUrl + "/bff/v2/sessions/web/handover";
        c.Session.Vars["jl.basketId"] = "b-77";
        c.Session.Vars["jl.express"] = "true";
        c.Session.Vars["jl.discountsInBasketUIEnabled"] = "false";
        c.Session.Vars["jl.timeReactLoaded"] = "125";
        c.Session.Vars["jl.timeToReactLoaded"] = "125";
        c.Session.Vars["jl.timeToCheckoutSpinner"] = "40";
        c.Session.Vars["jl.timeContinueToCheckoutClicked"] = "90";
        return c;
    }

    [Fact]
    public async Task TheHandoverPutsTheTimestampsNestedUnderTheRoot()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " " + body);
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().WebHandOverAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v2/sessions/web/handover", request);

        // the three stamps are nested, not siblings of express/basketId
        Assert.Contains("\"timestamps\":{", request);
        Assert.Contains("\"timeToReactLoaded\":125", request);
        Assert.Contains("\"timeToCheckoutSpinner\":40", request);
        Assert.Contains("\"timeContinueToCheckoutClicked\":90", request);
        Assert.Contains("\"basketId\":\"b-77\"", request);
        Assert.Contains("\"express\":true", request);
        Assert.Contains("\"discountsInBasketUIEnabled\":false", request);
    }

    /// <summary>Both image step names reach the same endpoint.</summary>
    [Fact]
    public async Task TheSecondStepNameReachesTheSameEndpoint()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod);
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().SessionHandoverAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Contains("/bff/v2/sessions/web/handover", Assert.Single(seen));
    }

    /// <summary>
    /// The two names are dispatchable by name, which is the whole reason the virtuals exist: the
    /// runner builds its table from StoreFlow's public *Async methods, so a name nobody declares would
    /// fail as "unknown step".
    /// </summary>
    [Fact]
    public void BothStepNamesAreKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("WebHandOver"));
        Assert.True(StepActionRunner.Knows("SessionHandover"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (502, "bad gateway"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().WebHandOverAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>The default URL is the image's own literal: 0x14705d830.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v2/sessions/web/handover",
            RetailApiFamilies.JohnLewisBff.SessionHandoverV2);
    }
}
