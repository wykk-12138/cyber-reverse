using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 132: layer 3 in code — the 3-D Secure profile derived from the browser fingerprint.
///
/// <para>
/// The rule this enforces is the one that costs money when broken: a payment profile that disagrees
/// with the browser it came from is rejected by the scheme's risk engine, and the rejection looks
/// exactly like a declined card. So the profile is <b>derived</b>, never assembled from separate
/// sources, and <see cref="DlpaProfile.AgreesWith"/> is the check.
/// </para>
///
/// <para>
/// The payload variant decides the User-Agent: with <c>fingerprint-v1-sans-ua</c> the caller sends it
/// elsewhere, so the profile leaves it out.
/// </para>
/// </summary>
public sealed class DlpaProfileTests
{
    private readonly ITestOutputHelper _out;

    public DlpaProfileTests(ITestOutputHelper output) => _out = output;

    /// <summary>Every derived field agrees with the browser it came from.</summary>
    [Fact]
    public void TheProfileAgreesWithItsBrowser()
    {
        var fp = BrowserFingerprint.ForProfile("pay-1");
        var dlpa = DlpaProfile.From(fp, utcOffsetMinutes: 60, userAgent: "Mozilla/5.0 … Chrome/157");

        _out.WriteLine($"{dlpa.BrowserScreenWidth}x{dlpa.BrowserScreenHeight} depth {dlpa.BrowserColorDepth} tz {dlpa.BrowserTz}");

        Assert.True(dlpa.AgreesWith(fp));
        Assert.Equal(fp.ScreenWidth.ToString(), dlpa.BrowserScreenWidth);
        Assert.Equal(fp.ScreenHeight.ToString(), dlpa.BrowserScreenHeight);
        Assert.Equal(fp.ColorDepth.ToString(), dlpa.BrowserColorDepth);
    }

    /// <summary>Every value is a string, because the scheme wants strings.</summary>
    [Fact]
    public void EveryValueIsAString()
    {
        var dlpa = DlpaProfile.From(BrowserFingerprint.ForProfile("pay-2"), 0, "ua");

        foreach (var (name, value) in dlpa.ToFields())
        {
            _out.WriteLine($"{name} = {value ?? "(null)"}");
            if (value is not null) Assert.IsType<string>(value);
        }
    }

    /// <summary>The field order matches the literal the image emits.</summary>
    [Fact]
    public void TheFieldOrderMatchesTheImage()
    {
        Assert.Equal(new[]
        {
            "fingerprintAttempted", "fingerprintData", "challengeWindowSize", "threeDSCompInd",
            "browserJavaEnabled", "browserJavascriptEnabled", "browserLanguage",
            "browserColorDepth", "browserScreenHeight", "browserScreenWidth", "browserTZ",
            "browserUserAgent",
        }, DlpaProfile.FieldOrder);
    }

    /// <summary>The sans-ua payload drops the User-Agent and nothing else.</summary>
    [Fact]
    public void TheSansUaPayloadDropsOnlyTheUserAgent()
    {
        var dlpa = DlpaProfile.From(BrowserFingerprint.ForProfile("pay-3"), 0, "Mozilla/5.0 UA");

        var with = dlpa.ToFields(sansUserAgent: false);
        var without = dlpa.ToFields(sansUserAgent: true);

        Assert.Equal("Mozilla/5.0 UA", with["browserUserAgent"]);
        Assert.False(without.ContainsKey("browserUserAgent"));

        // everything else is identical
        foreach (var key in without.Keys)
            Assert.Equal(with[key], without[key]);

        Assert.Equal(with.Count - 1, without.Count);
    }

    /// <summary>The time zone is minutes east of UTC, spelled as the scheme spells it.</summary>
    [Fact]
    public void TheTimeZoneIsMinutesEastOfUtc()
    {
        var fp = BrowserFingerprint.ForProfile("pay-4");

        Assert.Equal("60", DlpaProfile.From(fp, 60).BrowserTz);
        Assert.Equal("-300", DlpaProfile.From(fp, -300).BrowserTz);
        Assert.Equal("0", DlpaProfile.From(fp, 0).BrowserTz);
    }

    /// <summary>A profile cannot be made to disagree with its browser.</summary>
    [Fact]
    public void AProfileCannotDisagree()
    {
        var fp = BrowserFingerprint.ForProfile("pay-5");
        var wrong = DlpaProfile.From(fp, 0) with { BrowserScreenWidth = "5120" };

        Assert.False(wrong.AgreesWith(fp));
        Assert.True(DlpaProfile.From(fp, 0).AgreesWith(fp));
    }

    /// <summary>The two layers stay separate: DLPA carries no pixel ratio or hardware.</summary>
    [Fact]
    public void TheLayersDoNotBleed()
    {
        var fields = DlpaProfile.From(BrowserFingerprint.ForProfile("pay-6"), 0, "ua").ToFields();

        Assert.DoesNotContain("HardwareConcurrency", fields.Keys);
        Assert.DoesNotContain("DeviceMemory", fields.Keys);
        Assert.DoesNotContain("PixelRatio", fields.Keys);
        Assert.DoesNotContain("browserPixelRatio", fields.Keys);
    }
}
