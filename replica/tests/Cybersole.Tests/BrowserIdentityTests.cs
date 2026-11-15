using System.IO;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 134: closing the loop — something now <b>writes</b> the browser identity the payment layer
/// reads.
///
/// <para>
/// R133 taught the gateway to read <c>browser.fingerprintKey</c> and
/// <c>browser.timezoneOffsetMinutes</c>, but nothing in the workspace ever set them: the read side
/// existed and the write side did not, so every payment fell back to the User-Agent.
/// <see cref="BrowserIdentity"/> is the single writer, and the keys are spelled once.
/// </para>
///
/// <para>
/// The important property is that the browser launcher and the payment gateway derive from the
/// <b>same key</b>. A profile that picks one screen while the payment reports another is the failure
/// this whole chain exists to prevent.
/// </para>
/// </summary>
public sealed class BrowserIdentityTests
{
    private readonly ITestOutputHelper _out;

    public BrowserIdentityTests(ITestOutputHelper output) => _out = output;

    /// <summary>Recording writes all three keys; reading returns them.</summary>
    [Fact]
    public void RecordWritesThreeKeysAndReadsThemBack()
    {
        var session = new FlowSession();
        Assert.Null(BrowserIdentity.FingerprintKey(session));

        BrowserIdentity.Record(session, "task-9/profile-2", utcOffsetMinutes: 60);

        Assert.Equal("task-9/profile-2", BrowserIdentity.FingerprintKey(session));
        Assert.Equal(60, BrowserIdentity.TimeZoneOffset(session));
        Assert.Equal("fingerprint-v1", BrowserIdentity.Payload(session));
        Assert.False(BrowserIdentity.IsSansUserAgent(session));

        Assert.Equal(3, BrowserIdentity.Keys.Count);
        foreach (var key in BrowserIdentity.Keys) _out.WriteLine(key);
    }

    /// <summary>The variant is decided once, at record time.</summary>
    [Fact]
    public void TheVariantIsDecidedOnce()
    {
        var session = new FlowSession();
        BrowserIdentity.Record(session, "p", 0, userAgentAlreadySent: true);

        Assert.Equal("fingerprint-v1-sans-ua", BrowserIdentity.Payload(session));
        Assert.True(BrowserIdentity.IsSansUserAgent(session));
    }

    /// <summary>
    /// The launcher and the payment layer derive from the same key — the property the whole chain is
    /// for.
    /// </summary>
    [Fact]
    public void LauncherAndPaymentAgree()
    {
        var session = new FlowSession { UserAgent = "Mozilla/5.0 Chrome/157" };

        var profilePath = "/tmp/cyb-chromium-abc12345";
        var launcherFingerprint = BrowserFingerprint.ForProfile(profilePath);

        BrowserIdentity.RecordProfile(session, profilePath, utcOffsetMinutes: -300);

        var paymentFingerprint = BrowserIdentity.Fingerprint(session);
        var dlpa = DlpaProfile.From(paymentFingerprint, BrowserIdentity.TimeZoneOffset(session),
            session.UserAgent);

        Assert.Equal(launcherFingerprint, paymentFingerprint);
        Assert.True(dlpa.AgreesWith(launcherFingerprint));
        Assert.Equal("-300", dlpa.BrowserTz);

        _out.WriteLine($"{paymentFingerprint.ScreenWidth}x{paymentFingerprint.ScreenHeight} tz {dlpa.BrowserTz}");
    }

    /// <summary>No browser means a stable fallback, never a random one.</summary>
    [Fact]
    public void WithoutABrowserTheFallbackIsStable()
    {
        var session = new FlowSession { UserAgent = "Mozilla/5.0 Chrome/157" };

        var first = BrowserIdentity.Fingerprint(session);
        var second = BrowserIdentity.Fingerprint(session);

        Assert.Equal(first, second);
        Assert.Equal(0, BrowserIdentity.TimeZoneOffset(session));
        Assert.Equal("fingerprint-v1", BrowserIdentity.Payload(session));
    }

    /// <summary>The gateway reads through the same class, so there is one spelling of each key.</summary>
    [Fact]
    public void TheGatewayUsesTheSingleWriter()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var gateway = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Payments", "AdyenGateway.cs"));

        Assert.Contains("BrowserIdentity.Fingerprint(c.Session)", gateway);
        Assert.Contains("BrowserIdentity.TimeZoneOffset(c.Session)", gateway);

        // no second spelling of the key strings anywhere in the gateway
        Assert.DoesNotContain("\"browser.fingerprintKey\"", gateway);
        Assert.DoesNotContain("\"browser.timezoneOffsetMinutes\"", gateway);
    }
}
