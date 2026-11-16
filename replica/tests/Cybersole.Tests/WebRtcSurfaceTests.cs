using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The WebRTC surface, which covers a different kind of leak from its four siblings.
///
/// <para>
/// R914. Canvas, WebGL, font and media surfaces make the browser report values that must agree with the persona. WebRTC
/// does not report a value — it opens channels that answer with network addresses, so the requirement is the opposite:
/// report nothing the persona did not claim. The image names a SubmitWebRtc step; whether the original blocks, spoofs
/// or records is not established, and this surface implements the guard a proxied browser needs while saying so.
/// </para>
/// </summary>
public class WebRtcSurfaceTests
{
    /// <summary>
    /// Both candidate kinds are named. Suppressing one and not the other leaves the other to leak, and which one
    /// matters depends on the network, so a caller needs to see both to make a choice.
    /// </summary>
    [Fact]
    public void BothCandidateKindsAreNamed()
    {
        Assert.Contains("host", WebRtcSurface.CandidateLeaks);
        Assert.Contains("srflx", WebRtcSurface.CandidateLeaks);
        Assert.Contains("mDNS", WebRtcSurface.CandidateLeaks);
    }

    /// <summary>
    /// The script suppresses candidates in the event handler, which is the obvious half. The other half — stripping
    /// the same candidates from localDescription — is the one a page reading the SDP directly would exploit, so its
    /// presence is asserted separately rather than assumed from the first.
    /// </summary>
    [Fact]
    public void BothHalvesOfTheLeakAreClosed()
    {
        var js = WebRtcSurface.BodyJs();

        Assert.Contains("icecandidate", js);
        Assert.Contains("localDescription", js);
        Assert.Contains("stripSdp", js);
    }

    /// <summary>
    /// The connection stays constructible. A surface that made RTCPeerConnection throw would be detectable as surely
    /// as a leak, and a page that feature-detects it would fall back to something this guard does not cover.
    /// </summary>
    [Fact]
    public void TheConnectionRemainsConstructible()
    {
        var js = WebRtcSurface.BodyJs();

        Assert.Contains("window.RTCPeerConnection = Wrapped", js);
        Assert.Contains("Wrapped.prototype = PC.prototype", js);
        Assert.DoesNotContain("delete window.RTCPeerConnection", js);
        Assert.DoesNotContain("RTCPeerConnection = undefined", js);
    }

    /// <summary>A browser without the API is left alone rather than patched into an error.</summary>
    [Fact]
    public void ItDoesNothingWhenTheApiIsAbsent()
    {
        Assert.Contains("if (!PC) return;", WebRtcSurface.BodyJs());
    }

    /// <summary>
    /// The condition is data, not a comment: a session without a proxy has no address to protect, and installing the
    /// guard anyway would be a behaviour the original may not have.
    /// </summary>
    [Fact]
    public void TheGuardIsOnlyRequiredBehindAProxy()
    {
        Assert.True(WebRtcSurface.RequiredFor(behindProxy: true));
        Assert.False(WebRtcSurface.RequiredFor(behindProxy: false));
    }

    /// <summary>
    /// The surface says what it is not: the original's policy is unknown, and the Rule line records the reasoning
    /// rather than claiming parity.
    /// </summary>
    [Fact]
    public void TheRuleStatesTheReasoningRatherThanAClaim()
    {
        Assert.Contains("must not let WebRTC report an address the proxy hides", WebRtcSurface.Rule);
        Assert.DoesNotContain("as the original does", WebRtcSurface.Rule);
    }
}