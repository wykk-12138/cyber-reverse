using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1131: John Lewis's guest callback — a PUT to the BFF's <c>v4/callback/guest</c> carrying one
/// <c>email</c> key.
///
/// The containing function <c>sub_140A407A0</c> touches two URLs and they are not interchangeable:
/// <c>…/callback/login/guest?email=</c> goes to <c>sub_141CF6230</c>, while the PUT's URL argument is
/// the BFF one. These facts pin the PUT's URL, its verb, and that the body is exactly one key.
/// </summary>
public sealed class JohnLewisGuestCallbackTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.guestCallbackUrl"] = server.BaseUrl + "/bff/v4/callback/guest";
        return c;
    }

    [Fact]
    public async Task TheCallbackPutsOneEmailKeyToTheBff()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " " + body);
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);
        ctx.Session.Vars["jl.email"] = "ada@example.com";

        var outcome = await new JohnLewisFlow().GuestCallbackAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v4/callback/guest", request);
        Assert.Contains("\"email\":\"ada@example.com\"", request);
        // one key only: the body is not the whole profile
        Assert.DoesNotContain("firstName", request);
    }

    [Fact]
    public async Task TheSharedEmailKeyIsAcceptedAsAFallback()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);
        ctx.Session.Vars["email"] = "shared@example.com";

        var outcome = await new JohnLewisFlow().GuestCallbackAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
    }

    [Fact]
    public async Task NoEmailStopsTheStep()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().GuestCallbackAsync(ctx, default);

        Assert.False(outcome.Ok);
    }

    /// <summary>The step name is dispatchable, which is what makes the virtual worth declaring.</summary>
    [Fact]
    public void TheStepNameIsKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("GuestCallback"));
    }

    /// <summary>The default URL is the image's own literal: 0x14705da88.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v4/callback/guest",
            RetailApiFamilies.JohnLewisBff.GuestCallbackV4);
    }
}
