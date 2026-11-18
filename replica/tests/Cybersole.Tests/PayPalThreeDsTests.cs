using System.Linq;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1078: PayPal 3-D Secure, pinned to the decompiled stage-1 builders — sub_141102970 (normal)
/// and sub_141105A80 (hosted), with the send step sub_14110D670 (PUT to the frozen
/// https://www.paypal.com/graphql/ literal 0x147097e78).
///
/// <para>
/// Every value asserted here is a decoded frozen constant; the header casing differences between
/// the two dialects (Accept-Encoding vs accept-encoding, en-GB vs en-US) are the image's own and
/// are pinned as-is rather than normalised.
/// </para>
/// </summary>
public sealed class PayPalThreeDsTests
{
    private static PayPalThreeDs.StageInput Sample(bool hosted = false) => new()
    {
        ChallengeActive = hosted,   // the normal sample reports 'Solving', the hosted one 'Proccesing'
        Hosted = hosted,
        Euat = "euat-7",
        MetadataId = "meta-7",
        Country = "US",
        HostedAppName = "ctx-app",
        HostedReferer = "https://www.paypal.com/checkout",
        UserAgent = "UA/1",
        SecChUa = @"""Ch"";v=""1""",
        SecChUaPlatform = @"""Windows""",
        Payload = "{\"query\":\"{}\"}",
    };

    private static FlowContext Context(NetClient http) => new()
    {
        Http = http,
        Url = "https://www.paypal.com/checkout",
    };

    /// <summary>The normal dialect's wall, exactly as sub_141102970 assembles it.</summary>
    [Fact]
    public void TheNormalWallMatchesTheDecompiledContract()
    {
        var h = PayPalThreeDs.NormalHeaders(Sample());

        Assert.Equal(16, h.Count);
        Assert.Equal("euat-7", h["x-paypal-internal-euat"]);
        Assert.Equal("meta-7", h["paypal-client-metadata-id"]);
        Assert.Equal("?0", h["sec-ch-ua-mobile"]);
        Assert.Equal(PayPalThreeDs.AppName, h["x-app-name"]);
        Assert.Equal("application/json", h["content-type"]);
        Assert.Equal("*/*", h["accept"]);
        Assert.Equal("https://www.paypal.com", h["origin"]);
        Assert.Equal("https://www.paypal.com", h["referer"]);
        Assert.Equal("same-origin", h["sec-fetch-site"]);
        Assert.Equal("cors", h["sec-fetch-mode"]);
        Assert.Equal("empty", h["sec-fetch-dest"]);
        Assert.Equal("gzip, deflate", h["Accept-Encoding"]);
        Assert.Equal("en-GB", h["Accept-Language"]);
        Assert.Equal("UA/1", h["user-agent"]);

        // The sec-fetch family is the normal dialect's; the hosted-only headers are absent.
        Assert.False(h.ContainsKey("x-requested-with"));
        Assert.False(h.ContainsKey("x-locale"));
        Assert.False(h.ContainsKey("priority"));
        Assert.False(h.ContainsKey("x-country"));
    }

    /// <summary>
    /// The hosted dialect's wall (sub_141105A80): its own headers, its own casing, and the app
    /// name / referer / country taken from the context instead of literals.
    /// </summary>
    [Fact]
    public void TheHostedDialectCarriesItsOwnHeadersAndCasing()
    {
        var h = PayPalThreeDs.HostedHeaders(Sample(hosted: true));

        Assert.Equal(17, h.Count);
        Assert.Equal("fetch", h["x-requested-with"]);
        Assert.Equal("en_US", h["x-locale"]);
        Assert.Equal("meta-7", h["paypal-client-context"]);
        Assert.Equal("ctx-app", h["x-app-name"]);
        Assert.Equal("US", h["x-country"]);
        Assert.Equal("https://www.paypal.com/checkout", h["referer"]);
        Assert.Equal("gzip, deflate, br, zstd", h["accept-encoding"]);
        Assert.Equal("en-US,en;q=0.9", h["accept-language"]);
        Assert.Equal("u=1, i", h["priority"]);

        // The hosted wall does not send the sec-fetch family the normal one does.
        Assert.False(h.ContainsKey("sec-fetch-site"));
        Assert.False(h.ContainsKey("sec-fetch-mode"));
        Assert.False(h.ContainsKey("sec-fetch-dest"));
    }

    /// <summary>The stage texts, including the image's own spelling of "Proccesing".</summary>
    [Fact]
    public void TheStatusTextsKeepTheImageSpelling()
    {
        Assert.Equal("Solving PayPal 3DS", PayPalThreeDs.SolvingStatus);
        Assert.Equal("Proccesing 3D Secure", PayPalThreeDs.ProcessingStatus);   // the typo is the image's
        Assert.Equal(PayPalThreeDs.SolvingStatus, PayPalThreeDs.StatusText(challengeActive: false));
        Assert.Equal(PayPalThreeDs.ProcessingStatus, PayPalThreeDs.StatusText(challengeActive: true));
    }

    /// <summary>The target URL, the app name and the thirty-second budget, as frozen constants.</summary>
    [Fact]
    public void TheStageConstantsMatchTheFrozenLiterals()
    {
        Assert.Equal("https://www.paypal.com/graphql/", PayPalThreeDs.GraphqlUrl);
        Assert.Equal("checkoutuinodeweb_hermione", PayPalThreeDs.AppName);
        Assert.Equal(30000, PayPalThreeDs.StageTimeoutMs);
        Assert.Equal(new[] { "Submit3DS", "Process3DS", "Waiting3DS", "Complete3DS" },
            System.Enum.GetNames<PayPalThreeDs.ThreeDsState>());
    }

    /// <summary>
    /// The dispatch the builders register: 200 reaches the success continuation, 403 and 429 share
    /// the retry closure, and the machine stops with the located stages named.
    /// </summary>
    [Theory]
    [InlineData(200, true, false)]
    [InlineData(403, false, true)]
    [InlineData(429, false, true)]
    [InlineData(500, false, false)]
    public async Task TheStatusDispatchMirrorsTheRegisteredHandlers(int status, bool ok, bool retry)
    {
        using var server = new TinyServer((_, _) => (status, status == 200 ? "{\"done\":true}" : "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await PayPalThreeDs.SubmitAsync(ctx, Sample(), default, server.BaseUrl + "/graphql/");

        Assert.Equal(status, outcome.Status);
        Assert.Equal(ok, outcome.Ok);
        Assert.Equal(retry, outcome.Retryable);
        if (ok) Assert.Equal("{\"done\":true}", outcome.Body);

        // The white StatusInfo wall went out with the stage text before the request.
        Assert.Contains(ctx.Events, e => e.Name == PayPalThreeDs.SolvingStatus && e.Type == "StatusInfo");

        // And the request itself was the PUT the send step performs.
        Assert.Equal("PUT", server.Requests.Single().Method);
        Assert.Equal("/graphql/", server.Requests.Single().Path);
        Assert.Equal("{\"query\":\"{}\"}", server.Requests.Single().Body);
    }

    /// <summary>
    /// The four-state machine advances past a decoded Submit and stops where the decoded stages
    /// end — naming the eight located bodies rather than reporting a completion nothing performed.
    /// </summary>
    [Fact]
    public async Task TheMachineStopsWhereTheDecodedStagesEnd()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var solver = new PayPalThreeDs();
        var outcome = await solver.RunAsync(ctx, Sample(), default, server.BaseUrl + "/graphql/");

        Assert.False(outcome.Ok);
        Assert.False(outcome.Retryable);
        Assert.NotNull(outcome.Error);
        Assert.Contains("not decoded", outcome.Error);
        Assert.Equal(nameof(PayPalThreeDs.ThreeDsState.Process3DS), ctx.Session.Vars["paypal3ds.state"]);
        foreach (var fn in new[] { "sub_141103410", "sub_141103800", "sub_141103BF0", "sub_1411090C0",
                     "sub_141109550", "sub_141109910", "sub_14110A080", "sub_141106360" })
            Assert.Contains(fn, outcome.Error);
    }
}
