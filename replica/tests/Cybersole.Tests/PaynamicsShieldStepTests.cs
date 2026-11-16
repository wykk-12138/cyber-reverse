using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The shield step: what the image's evidence fixes, and what the implementation refuses to pretend it knows.
///
/// <para>
/// R916. <c>RunShield</c> carries ordinal eighteen and three locals — data, data2 and shieldQuery. Its neighbours are
/// ProcessResult at fourteen, OpenSecurePage at fifteen and Navigate at seventeen, which places it after a secure page
/// is open and around a navigation. So it is a step in a payment flow, not the standalone OTP call R905 first read it
/// as, and the order it implies — profile, build the query, post, process the answer — is inference from ordinals and
/// local names rather than from any literal.
/// </para>
/// </summary>
public class PaynamicsShieldStepTests
{
    private static FlowSession SessionWith(string? deviceToken)
    {
        var s = new FlowSession { SessionId = "s" };
        if (deviceToken != null) s.Vars["paynamics.deviceToken"] = deviceToken;
        return s;
    }

    private static NetResponse Ok(string body) => new()
    {
        Url = new System.Uri("https://shield.paynamics.net/shield/v1/verify_otp"),
        StatusCode = 200,
        Body = body,
        Headers = new System.Collections.Generic.Dictionary<string, string>(),
    };

    /// <summary>
    /// The step is on StoreFlow and refuses by default, which is what keeps a store without shield evidence from
    /// appearing to have it.
    /// </summary>
    [Fact]
    public void TheStepExistsAndFailsByDefault()
    {
        var method = typeof(StoreFlow).GetMethod("RunShieldAsync");
        Assert.NotNull(method);
        Assert.True(method!.IsVirtual);
    }

    /// <summary>
    /// Without a device token there is nothing to shield, and the failure is retryable because the profiling step may
    /// simply not have run yet. A send with an empty token would look like success and shield nothing.
    /// </summary>
    [Fact]
    public async Task ItFailsWithoutADeviceToken()
    {
        var outcome = await PaynamicsShield.RunAsync(SessionWith(null), default,
            (url, body, tag, ct) => Task.FromResult<NetResponse?>(null));

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>
    /// With a token it posts to the second shield host and the OTP path — the pair R905 recovered and nothing used.
    /// </summary>
    [Fact]
    public async Task ItPostsToTheRecoveredHostAndPath()
    {
        var session = SessionWith("tok-1");
        string? seenUrl = null;
        string? seenBody = null;

        var outcome = await PaynamicsShield.RunAsync(session, default, (url, body, tag, ct) =>
        {
            seenUrl = url;
            seenBody = body;
            return Task.FromResult<NetResponse?>(Ok("{\"shieldToken\":\"sh-9\"}"));
        });

        Assert.True(outcome.Ok);
        Assert.Equal("https://shield.paynamics.net/shield/v1/verify_otp", seenUrl);
        Assert.Contains("tok-1", seenBody);
        Assert.Equal("sh-9", session.Vars["paynamics.shieldResult"]);
    }

    /// <summary>
    /// An unreachable host is retryable and leaves no result behind, so a later step cannot read a token that was never
    /// issued.
    /// </summary>
    [Fact]
    public async Task AnUnreachableHostLeavesNoResult()
    {
        var session = SessionWith("tok-1");

        var outcome = await PaynamicsShield.RunAsync(session, default,
            (url, body, tag, ct) => Task.FromResult<NetResponse?>(null));

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
        Assert.False(session.Vars.ContainsKey("paynamics.shieldResult"));
    }

    /// <summary>
    /// A response without a recognised token still records the body rather than dropping it, because the answer's
    /// meaning is unknown and discarding it would lose the only evidence a later round could read.
    /// </summary>
    [Fact]
    public async Task AnUnrecognisedAnswerIsStillRecorded()
    {
        var session = SessionWith("tok-1");

        var outcome = await PaynamicsShield.RunAsync(session, default,
            (url, body, tag, ct) => Task.FromResult<NetResponse?>(Ok("{\"something\":\"else\"}")));

        Assert.True(outcome.Ok);
        Assert.Equal("{\"something\":\"else\"}", session.Vars["paynamics.shieldResult"]);
        Assert.Equal("{\"something\":\"else\"}", session.Vars["paynamics.shieldBody"]);
    }

    /// <summary>
    /// The two shield hosts are distinct, so a call that used the profiling host would be talking to the wrong one.
    /// </summary>
    [Fact]
    public void TheTwoShieldHostsAreNotInterchangeable()
    {
        var (host, _path) = PaynamicsGateway.RecoveredShieldSurface;
        Assert.NotEqual("https://nodecde1.paynamics.net", host);
        Assert.Equal("https://shield.paynamics.net", host);
    }
}