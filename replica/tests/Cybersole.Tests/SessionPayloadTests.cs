using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 152: the session payload the image actually posts, read off a captured sample.
///
/// <para>
/// This is the first time this session has the original's own telemetry schema in hand rather than inferring
/// it from a class name. It settles R151's open question in passing: the sample reports
/// <c>screen.orientation.type = "landscape-primary"</c> with <c>angle 0</c>, under a Windows UA — so leaving
/// orientation native is not an incoherence this replica introduced, it is what the original reports.
/// </para>
/// </summary>
public sealed class SessionPayloadTests
{
    private readonly ITestOutputHelper _out;

    public SessionPayloadTests(ITestOutputHelper output) => _out = output;

    /// <summary>Sixteen head keys, in the sample's order.</summary>
    [Fact]
    public void TheHeadHasSixteenKeys()
    {
        Assert.Equal(16, SessionPayload.HeadKeys.Count);
        Assert.Equal(SessionPayload.HeadKeys.Count, SessionPayload.HeadKeys.Distinct().Count());

        Assert.Equal(new[] { "sid", "tid", "_t", "cf_flags", "fresh-cookie", "cookie-_cc" },
            SessionPayload.HeadKeys.Take(6));

        _out.WriteLine(string.Join(", ", SessionPayload.HeadKeys));
    }

    /// <summary>The cookie tag is a truncation of the token, not an independent value.</summary>
    [Fact]
    public void TheCookieTagIsATruncation()
    {
        const string token = "ASaMBHzL7WoRfLL6ekqt4MuLNpqk5pjk";
        Assert.Equal("ASaMBHzL7WoRfLL6ekqt4MuL", SessionPayload.CookieTagFor(token));
        Assert.Equal(24, SessionPayload.CookieTagLength);

        // short tokens pass through untouched rather than being padded
        Assert.Equal("abc", SessionPayload.CookieTagFor("abc"));
    }

    /// <summary>getTimezoneOffset is minutes behind UTC, and DST is a state, not a number.</summary>
    [Fact]
    public void TheTimezoneFlagsCorroborateEachOther()
    {
        // central European summer time is +02:00 east, which JS reports as -120
        Assert.Equal(-120, SessionPayload.GetTimezoneOffsetMinutes(120));

        // the sample has offset == stdOffset (-120) yet says DST is active; that is what a host in CEST
        // reports when the standard offset is also taken from the same zone
        Assert.False(SessionPayload.IsDaylightActive(-120, -120));
        Assert.True(SessionPayload.IsDaylightActive(-120, -60));

        Assert.Equal("6-3-2014, 07:58:39", SessionPayload.FixedLocaleSample);
        Assert.Equal(new System.DateTime(2014, 3, 6, 7, 58, 39), SessionPayload.FixedLocaleDate);
    }

    /// <summary>The computed keys are the original's findings, not DOM readings.</summary>
    [Fact]
    public void TheComputedKeysAreFindings()
    {
        Assert.Equal(4, SessionPayload.ComputedKeys.Count);
        Assert.Contains("navigator.automationEnabled", SessionPayload.ComputedKeys);
        Assert.Contains("webdriver_detect", SessionPayload.ComputedKeys);
        Assert.Contains("canvas_spoofing", SessionPayload.ComputedKeys);
        Assert.Contains("js-errors", SessionPayload.ComputedKeys);

        // and none of them is a real navigator member, which is why they cannot be read back
        Assert.DoesNotContain("navigator.userAgent", SessionPayload.ComputedKeys);

        _out.WriteLine(string.Join(", ", SessionPayload.ComputedKeys));
    }

    /// <summary>Five plugin entries, all reporting the same internal filename.</summary>
    [Fact]
    public void TheFivePluginsShareOneFilename()
    {
        Assert.Equal(5, SessionPayload.PluginNames.Count);
        Assert.Equal(5, SessionPayload.PluginNames.Distinct().Count());
        Assert.Equal("internal-pdf-viewer", SessionPayload.PluginFilename);
        Assert.Equal("Portable Document Format", SessionPayload.PluginDescription);

        _out.WriteLine(string.Join(" | ", SessionPayload.PluginNames));
    }

    /// <summary>The non-standard dark-mode member and the connection quartet are recorded.</summary>
    [Fact]
    public void TheExtraMembersAreRecorded()
    {
        Assert.Equal("screen.darkMode.enabled", SessionPayload.DarkModeKey);
        Assert.False(SessionPayload.DarkModeSample);

        Assert.Equal(4, SessionPayload.ConnectionKeys.Count);
        Assert.Contains("navigator.connection.effectiveType", SessionPayload.ConnectionKeys);

        Assert.Equal(1006579, SessionPayload.CfFlagsSample);
        Assert.Equal("1006579", SessionPayload.CfFlags(SessionPayload.CfFlagsSample));
    }

    /// <summary>The sample's orientation settles R151: the original reports landscape too.</summary>
    [Fact]
    public void TheSampleSettlesTheOrientationQuestion()
    {
        // R151 left orientation native and called it a known incoherence. The sample says the original
        // reports "landscape-primary" with angle 0 under a Windows UA, so native is what it does too.
        Assert.Contains("orientation", MobileSurface.ScreenOrder);
        Assert.DoesNotContain("portrait-primary", MobileSurface.BodyJs(),
            System.StringComparison.OrdinalIgnoreCase);

        _out.WriteLine("orientation is native in the image as well — R151's 'incoherence' is its normal state");
    }
}
