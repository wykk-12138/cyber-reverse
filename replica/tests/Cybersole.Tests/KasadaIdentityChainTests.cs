using System.IO;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 135: the Kasada solver is now the place a browser identity is born, so a token and the
/// payment that follows it belong to the same machine.
///
/// <para>
/// The chain reads: <c>ChromiumBridge.LaunchAsync</c> creates the profile folder and derives the
/// fingerprint from it; the solver records that same key in the session; the payment gateway reads it
/// back. Before this round the first step was invisible to the other two, so the identity a token was
/// solved on and the identity a payment described could differ — and nothing would report it.
/// </para>
///
/// <para>
/// The solver's contract is checked at the source level because the real path launches a browser;
/// the identity arithmetic itself is covered by <see cref="BrowserIdentityTests"/>.
/// </para>
/// </summary>
public sealed class KasadaIdentityChainTests
{
    private readonly ITestOutputHelper _out;

    public KasadaIdentityChainTests(ITestOutputHelper output) => _out = output;

    private static string Source(params string[] parts)
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(new[] { dir!.FullName }.Concat(parts).ToArray()));
    }

    /// <summary>The solver accepts a session and records the identity before touching the page.</summary>
    [Fact]
    public void TheSolverRecordsTheIdentity()
    {
        var text = Source("src", "Cybersole.Stores", "Scripts", "ChromiumKasadaSolver.cs");

        Assert.Contains("FlowSession? session = null", text);
        Assert.Contains("BrowserIdentity.RecordProfile(session, bridge.ProfilePath", text);

        // recording happens right after launch, before navigation
        var record = text.IndexOf("BrowserIdentity.RecordProfile", System.StringComparison.Ordinal);
        var navigate = text.IndexOf("NavigateAsync(pageUrl", System.StringComparison.Ordinal);
        Assert.True(record > 0 && navigate > record, "identity is recorded before the page is opened");
    }

    /// <summary>The bridge publishes what the identity is derived from.</summary>
    [Fact]
    public void TheBridgePublishesItsIdentity()
    {
        var text = Source("src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs");

        Assert.Contains("public string ProfilePath { get; private set; }", text);
        Assert.Contains("public BrowserFingerprint Fingerprint { get; private set; }", text);
        Assert.Contains("bridge.ProfilePath = profile;", text);
        Assert.Contains("bridge.Fingerprint = fingerprint;", text);
    }

    /// <summary>The result carries the key, so a caller without a session can still align.</summary>
    [Fact]
    public void TheResultCarriesTheKey()
    {
        var text = Source("src", "Cybersole.Stores", "Scripts", "ChromiumKasadaSolver.cs");

        Assert.Contains("public string ProfileKey { get; private set; }", text);
        Assert.Contains("ProfileKey = bridge.ProfilePath;", text);
    }

    /// <summary>
    /// End to end at the value level: one key produces one fingerprint, and the payment profile built
    /// from it agrees.
    /// </summary>
    [Fact]
    public void OneKeyOneFingerprintOneProfile()
    {
        var session = new FlowSession { UserAgent = "Mozilla/5.0 Chrome/157" };
        var profilePath = "/tmp/cyb-chromium-1a2b3c4d";

        // what the bridge derives
        var bridgeFingerprint = BrowserFingerprint.ForProfile(profilePath);

        // what the solver records (userAgentAlreadySent: true — the solver sends the UA itself)
        BrowserIdentity.RecordProfile(session, profilePath, utcOffsetMinutes: 60,
            userAgentAlreadySent: true);

        var sessionFingerprint = BrowserIdentity.Fingerprint(session);
        var dlpa = DlpaProfile.From(sessionFingerprint, BrowserIdentity.TimeZoneOffset(session),
            session.UserAgent);

        Assert.Equal(bridgeFingerprint, sessionFingerprint);
        Assert.True(dlpa.AgreesWith(bridgeFingerprint));
        Assert.True(BrowserIdentity.IsSansUserAgent(session));
        Assert.Equal("60", dlpa.BrowserTz);

        _out.WriteLine($"{sessionFingerprint.ScreenWidth}x{sessionFingerprint.ScreenHeight}, " +
                       $"tz {dlpa.BrowserTz}, payload {BrowserIdentity.Payload(session)}");
    }
}
