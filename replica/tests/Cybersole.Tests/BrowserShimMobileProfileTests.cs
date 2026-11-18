using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the original ships a mobile Kasada path (IsMobile / MfcEnabled / MobileDv /
/// SpoofMobile / GenRandomIos / VersionHandler -- addresses in docs/KASADA/11 5.69). The payload itself is
/// device-agnostic: its literal table contains no iPhone/Android/Platform/maxTouchPoints strings at all
/// (5.70), so the mobile path is the same sensor presented with a mobile identity rather than a second
/// script. These cases pin that the shim can actually present one -- a profile that lies about the
/// user agent while reporting maxTouchPoints = 0 is self-contradictory and sites detect it.
/// </summary>
public sealed class BrowserShimMobileProfileTests
{
    [Fact]
    public void TheIosProfileReportsATouchDeviceConsistently()
    {
        using var runtime = new ScriptRuntime(BrowserShim.Ios());

        Assert.Contains("iPhone", runtime.TryString("navigator.userAgent")!, StringComparison.Ordinal);
        Assert.Equal("iPhone", runtime.TryString("navigator.platform"));
        Assert.Equal("Apple Computer, Inc.", runtime.TryString("navigator.vendor"));
        Assert.Equal("5", runtime.TryString("String(navigator.maxTouchPoints)"));
        Assert.Equal("true", runtime.TryString("String(/iPhone/.test(navigator.userAgent) && navigator.maxTouchPoints > 0)"));
    }

    [Fact]
    public void TheDesktopDefaultStillReportsNoTouch()
    {
        using var runtime = new ScriptRuntime(new BrowserShim());

        // The regression this guards: every sandbox run before this change reported 0 touch points, which
        // is correct for a desktop and must not drift when a mobile profile is added alongside it.
        Assert.Equal("0", runtime.TryString("String(navigator.maxTouchPoints)"));
        Assert.Equal("Google Inc.", runtime.TryString("navigator.vendor"));
    }

    [Fact]
    public void AProfileCanOverrideEveryFieldSitesRead()
    {
        using var runtime = new ScriptRuntime(new BrowserShim
        {
            UserAgent = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36",
            Platform = "Linux armv8l",
            Vendor = "Google Inc.",
            MaxTouchPoints = 5,
            HardwareConcurrency = 8,
            DeviceMemory = 8,
        });

        Assert.Contains("Android", runtime.TryString("navigator.userAgent")!, StringComparison.Ordinal);
        Assert.Equal("Linux armv8l", runtime.TryString("navigator.platform"));
        Assert.Equal("5", runtime.TryString("String(navigator.maxTouchPoints)"));
        Assert.Equal("8", runtime.TryString("String(navigator.hardwareConcurrency)"));
        Assert.Equal("8", runtime.TryString("String(navigator.deviceMemory)"));
    }
}
