using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R23: once a Kasada token exists, the identity it was minted under is pinned. These are
/// pure unit tests — no network, no browser.
/// </summary>
public class KasadaIdentityPinTests
{
    private static FlowContext Ctx()
    {
        using var http = new NetClient();
        return new FlowContext
        {
            Http = http,
            Url = "https://www.nike.com/",
            Product = new Product { Name = "x", Url = "https://www.nike.com/" },
        };
    }

    [Fact]
    public void WithoutATokenTheSessionUserAgentIsUsedAsIs()
    {
        var ctx = Ctx();
        ctx.Session.UserAgent = "UA-A";

        var options = ctx.Options("t");

        Assert.Equal("UA-A", options.Headers["User-Agent"]);
        Assert.False(ctx.HasKasadaToken);
    }

    [Fact]
    public void WithATokenThePinnedUserAgentWins()
    {
        var ctx = Ctx();
        ctx.Session.UserAgent = "UA-A";
        ctx.Session.AntiBotTokens["x-kpsdk-ct"] = "token-abc";
        ctx.Session.Vars["kasada.ua"] = "UA-PINNED";

        var options = ctx.Options("t");

        Assert.True(ctx.HasKasadaToken);
        Assert.Equal("UA-PINNED", options.Headers["User-Agent"]);
    }

    [Fact]
    public void ASwappedUserAgentIsCorrectedAndRecorded()
    {
        var ctx = Ctx();
        ctx.Session.UserAgent = "UA-WRONG";
        ctx.Session.AntiBotTokens["x-kpsdk-ct"] = "token-abc";
        ctx.Session.Vars["kasada.ua"] = "UA-PINNED";

        var options = ctx.Options("t");

        Assert.Equal("UA-PINNED", options.Headers["User-Agent"]);
        Assert.Equal("UA-PINNED", ctx.Session.UserAgent);

        // the fact that it had drifted is preserved for diagnostics
        Assert.Equal("UA-WRONG", ctx.Session.Vars["kasada.uaCorrection"]);
    }

    [Fact]
    public void ATokenWithoutARecordedUserAgentLeavesThingsAlone()
    {
        var ctx = Ctx();
        ctx.Session.UserAgent = "UA-A";
        ctx.Session.AntiBotTokens["x-kpsdk-ct"] = "token-abc";

        var options = ctx.Options("t");

        Assert.True(ctx.HasKasadaToken);
        Assert.Null(ctx.KasadaUserAgent);
        Assert.Equal("UA-A", options.Headers["User-Agent"]);
    }

    [Fact]
    public void KasadaTokensAreCarriedAsRequestHeaders()
    {
        var ctx = Ctx();
        ctx.Session.AntiBotTokens["x-kpsdk-ct"] = "ct-value";
        ctx.Session.AntiBotTokens["x-kpsdk-dt"] = "dt-value";
        ctx.Session.AntiBotTokens["x-kpsdk-im"] = "im-value";

        var options = ctx.Options("t");

        Assert.Equal("ct-value", options.Headers["x-kpsdk-ct"]);
        Assert.Equal("dt-value", options.Headers["x-kpsdk-dt"]);
        Assert.Equal("im-value", options.Headers["x-kpsdk-im"]);
    }

    [Fact]
    public void EveryOptionBagSeesTheSamePinnedIdentity()
    {
        var ctx = Ctx();
        ctx.Session.UserAgent = "UA-A";
        ctx.Session.AntiBotTokens["x-kpsdk-ct"] = "token";
        ctx.Session.Vars["kasada.ua"] = "UA-PINNED";

        var first = ctx.Options("one");
        var second = ctx.Options("two");

        Assert.Equal(first.Headers["User-Agent"], second.Headers["User-Agent"]);
        Assert.Equal("UA-PINNED", second.Headers["User-Agent"]);
    }
}
