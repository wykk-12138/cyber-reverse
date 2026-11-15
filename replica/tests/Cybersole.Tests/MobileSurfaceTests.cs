using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 147: the rest of the image's injected script — the iPhone surface, with the reasons the original
/// wrote down for each piece of it.
///
/// <para>
/// Every rule here was learned by the original the hard way, and each comment names the detector that
/// caught the previous attempt: a TouchEvent factory that threw, a <c>performance.memory</c> that WebKit
/// never had, a Screen with ten keys where a phone has eight, an <c>innerWidth &gt; outerWidth</c> that no
/// browser produces, and a page-zoom ratio that moved on scroll.
/// </para>
/// </summary>
public sealed class MobileSurfaceTests
{
    private readonly ITestOutputHelper _out;

    public MobileSurfaceTests(ITestOutputHelper output) => _out = output;

    /// <summary>The device: 402×874, minus 190px of Safari chrome for the top-level viewport.</summary>
    [Fact]
    public void TheDeviceGeometryIsRecorded()
    {
        Assert.Equal(402, MobileSurface.ScreenWidth);
        Assert.Equal(874, MobileSurface.ScreenHeight);
        Assert.Equal(190, MobileSurface.ChromeHeight);
        Assert.Equal(684, MobileSurface.ViewportHeight);
        Assert.Equal(3, MobileSurface.DevicePixelRatio);

        _out.WriteLine($"{MobileSurface.ScreenWidth}x{MobileSurface.ScreenHeight} screen, " +
                       $"{MobileSurface.ScreenWidth}x{MobileSurface.ViewportHeight} viewport");
    }

    /// <summary>The Screen shape is nine keys, and Blink's two extra are named for deletion.</summary>
    [Fact]
    public void TheScreenShapeIsNineKeys()
    {
        Assert.Equal(9, MobileSurface.ScreenOrder.Count);
        Assert.Equal(2, MobileSurface.BlinkOnlyScreenMembers.Count);
        Assert.Contains("isExtended", MobileSurface.BlinkOnlyScreenMembers);
        Assert.Contains("onchange", MobileSurface.BlinkOnlyScreenMembers);

        // neither of Blink's extras is part of the shape a phone reports
        Assert.DoesNotContain("isExtended", MobileSurface.ScreenOrder);
        Assert.DoesNotContain("onchange", MobileSurface.ScreenOrder);
    }

    /// <summary>Both impossible geometries are rejected by the same predicate.</summary>
    [Fact]
    public void TheImpossibleGeometryIsRecognised()
    {
        // patching outer without inner manufactures this
        Assert.True(MobileSurface.IsImpossibleGeometry(innerWidth: 700, outerWidth: 402, screenWidth: 402));
        Assert.True(MobileSurface.IsImpossibleGeometry(innerWidth: 500, outerWidth: 500, screenWidth: 402));

        // the device figures are coherent
        Assert.False(MobileSurface.IsImpossibleGeometry(MobileSurface.ScreenWidth,
            MobileSurface.ScreenWidth, MobileSurface.ScreenWidth));
    }

    /// <summary>The scrollbar tell is the ratio moving, not the ratio itself.</summary>
    [Fact]
    public void TheScrollbarTellIsTheChangingRatio()
    {
        // real layout viewport with a Windows scrollbar, against a spoofed innerWidth
        var before = MobileSurface.ZoomRatio(clientWidth: 500, innerWidth: 402);
        var after = MobileSurface.ZoomRatio(clientWidth: 485, innerWidth: 402);

        _out.WriteLine($"{MobileSurface.Format(before)} then {MobileSurface.Format(after)}");

        Assert.NotEqual(MobileSurface.Format(before), MobileSurface.Format(after));
        // The comment quotes 1.2437 and 1.2065. 485/402 really is 1.2065, but 500/402 is 1.24378…,
        // which rounds to 1.2438 — so the original truncated there rather than rounded. Comparing at
        // three places keeps the test about the tell (the ratio moves) and not about the author's
        // rounding habit.
        Assert.Equal("1.244", before.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
        Assert.Equal("1.206", after.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
        Assert.True(before > after, "the ratio must fall when a scrollbar takes layout width");

        // pinning clientWidth makes it exactly one, and independent of what the host did
        Assert.Equal("1", MobileSurface.Format(MobileSurface.ZoomRatio(402, 402)));
        Assert.Contains("overlays", MobileSurface.ScrollbarTell);
    }

    /// <summary>The frame rule: the device figures belong to the top-level window.</summary>
    [Fact]
    public void TheFrameRuleIsRecorded()
    {
        Assert.Contains("top-level window only", MobileSurface.FrameRule);
        Assert.Contains("honest", MobileSurface.FrameRule);

        // and the two boxes that get pinned are named
        Assert.Equal(new[] { "clientWidth", "clientHeight" }, MobileSurface.PinnedBoxes);
    }

    /// <summary>Both removed APIs are recorded with the probe that finds them.</summary>
    [Fact]
    public void TheRemovedApisCarryTheirProbes()
    {
        Assert.Equal(2, MobileSurface.Removed.Count);

        foreach (var (api, probe) in MobileSurface.Removed)
            _out.WriteLine($"{api,-34} {probe}");

        Assert.Contains("\"memory\" in performance", MobileSurface.Removed["Performance.prototype.memory"]);
        Assert.Contains("NotSupportedError",
            MobileSurface.Removed["TouchEvent from createEvent"]);
    }

    /// <summary>The touch factory is the uninitialised constructor call, not a throw.</summary>
    [Fact]
    public void TheTouchFactoryReturnsAnEvent()
    {
        Assert.Equal("new TouchEvent('')", MobileSurface.TouchEventFactory);
        Assert.DoesNotContain("throw", MobileSurface.TouchEventFactory);
        Assert.Single(MobileSurface.WebKitAliases);
        Assert.Equal("webkitIndexedDB", MobileSurface.WebKitAliases[0]);
    }
}
