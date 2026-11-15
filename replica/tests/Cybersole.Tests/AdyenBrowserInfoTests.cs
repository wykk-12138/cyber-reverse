using System.IO;
using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 133: the 3-D Secure browser profile is derived from the fingerprint, in the gateway that
/// actually sends it.
///
/// <para>
/// The gateway used to send <c>colorDepth 24</c>, <c>screenHeight 1080</c>, <c>screenWidth 1920</c>,
/// <c>timeZoneOffset 0</c> for every payment. A scheme risk engine compares those four against the
/// browser that made the request; when they disagree it rejects, and the rejection arrives as a
/// decline — indistinguishable from a bad card, so it never looks like a bug in this code.
/// </para>
///
/// <para>
/// The test reads the gateway source the way this repository's other parity tests do, because the
/// defect being prevented is precisely "a literal appears where a derived value belongs".
/// </para>
/// </summary>
public sealed class AdyenBrowserInfoTests
{
    private readonly ITestOutputHelper _out;

    public AdyenBrowserInfoTests(ITestOutputHelper output) => _out = output;

    private static string Source()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Payments", "AdyenGateway.cs"));
    }

    /// <summary>The browser info is built from the fingerprint, not from literals.</summary>
    [Fact]
    public void TheBrowserInfoIsDerived()
    {
        var text = Source();

        Assert.Contains("[\"browserInfo\"] = BrowserInfo(c)", text);
        Assert.Contains("private static JObject BrowserInfo(FlowContext c)", text);
        Assert.Contains("BrowserIdentity.Fingerprint(c.Session)", text);
        Assert.Contains("DlpaProfile.From(fingerprint", text);
    }

    /// <summary>None of the four hardcoded values survives in the payload.</summary>
    [Fact]
    public void TheHardcodedScreenValuesAreGone()
    {
        var text = Source();

        // the literal 1080/1920 pair was the fingerprint of the bug
        Assert.DoesNotContain("[\"screenHeight\"] = 1080", text);
        Assert.DoesNotContain("[\"screenWidth\"] = 1920", text);
        Assert.DoesNotContain("[\"colorDepth\"] = 24", text);
        Assert.DoesNotContain("[\"timeZoneOffset\"] = 0,", text);

        // they are now read from the fingerprint
        Assert.Contains("[\"screenHeight\"] = fingerprint.ScreenHeight", text);
        Assert.Contains("[\"screenWidth\"] = fingerprint.ScreenWidth", text);
        Assert.Contains("[\"colorDepth\"] = fingerprint.ColorDepth", text);
        Assert.Contains("[\"timeZoneOffset\"] = TimeZoneOffset(c)", text);
    }

    /// <summary>The session can carry the browser's own profile key and time zone.</summary>
    [Fact]
    public void TheSessionSuppliesTheProfileKeyAndOffset()
    {
        var text = Source();

        // R134: the key spellings live in BrowserIdentity now, so the gateway names the class instead
        // of the strings — one spelling of each key, in one file.
        Assert.Contains("BrowserIdentity.Fingerprint", text);
        Assert.Contains("BrowserIdentity.TimeZoneOffset", text);
        Assert.DoesNotContain("\"browser.fingerprintKey\"", text);

        foreach (var key in BrowserIdentity.Keys) _out.WriteLine(key);
    }

    /// <summary>
    /// A fingerprint and its DLPA profile describe the same device, so the pair the gateway builds
    /// cannot disagree.
    /// </summary>
    [Fact]
    public void ThePairAgreesForEveryProfile()
    {
        foreach (var key in new[] { "a", "b", "profile-1", "profile-9" })
        {
            var fp = BrowserFingerprint.ForProfile(key);
            var dlpa = DlpaProfile.From(fp, 60, "Mozilla/5.0");

            Assert.True(dlpa.AgreesWith(fp), key);
            Assert.Equal(fp.ScreenWidth.ToString(), dlpa.BrowserScreenWidth);
            _out.WriteLine($"{key}: {fp.ScreenWidth}x{fp.ScreenHeight} tz {dlpa.BrowserTz}");
        }
    }

    /// <summary>Both payload variants exist and differ only in the UA field.</summary>
    [Fact]
    public void ThePayloadVariantIsSelectable()
    {
        Assert.Equal("fingerprint-v1", FingerprintLayers.PayloadFor(userAgentAlreadySent: false));
        Assert.Equal("fingerprint-v1-sans-ua", FingerprintLayers.PayloadFor(userAgentAlreadySent: true));

        var dlpa = DlpaProfile.From(BrowserFingerprint.ForProfile("x"), 0, "UA");
        Assert.True(dlpa.ToFields(sansUserAgent: true).Count < dlpa.ToFields().Count);
    }
}
