using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 151: the geometry the replica had left alone — <c>VisualViewport</c> — plus the field the image
/// deliberately does <b>not</b> patch.
///
/// <para>
/// The image's comment names the failure precisely: "innerWidth/innerHeight and visualViewport were the only
/// geometry left unpatched, so they reported the real host window while outerWidth/outerHeight reported the
/// device." The replica had exactly the same gap one round after fixing the same sentence's first half.
/// </para>
///
/// <para>
/// <c>orientation</c> is the opposite kind of fact: it is in <c>SCREEN_ORDER</c> but not in the image's
/// <c>SCREEN</c> object, so its native value stays. Patching it would be a claim with nothing to correct.
/// </para>
/// </summary>
public sealed class VisualViewportTests
{
    private readonly ITestOutputHelper _out;

    public VisualViewportTests(ITestOutputHelper output) => _out = output;

    /// <summary>Seven fields, in the order the image writes them.</summary>
    [Fact]
    public void TheSevenFieldsAreRecorded()
    {
        Assert.Equal(7, MobileSurface.VisualViewportFields.Count);
        Assert.Equal(new[]
        {
            "offsetLeft", "offsetTop", "pageLeft", "pageTop", "width", "height", "scale",
        }, MobileSurface.VisualViewportFields);

        _out.WriteLine(string.Join(", ", MobileSurface.VisualViewportFields));
    }

    /// <summary>Orientation is in the shape and not in the values.</summary>
    [Fact]
    public void OrientationStaysNative()
    {
        Assert.Contains(MobileSurface.OrientationIsNative, MobileSurface.ScreenOrder);
        Assert.DoesNotContain(MobileSurface.OrientationIsNative, MobileSurface.VisualViewportFields);

        _out.WriteLine("orientation is in SCREEN_ORDER and absent from SCREEN — the image leaves it alone");
    }

    /// <summary>The body installs the viewport at the top level and nowhere else.</summary>
    [Fact]
    public void TheViewportIsTopLevelOnly()
    {
        var js = MobileSurface.BodyJs();

        Assert.Contains("G.VisualViewport && G.VisualViewport.prototype", js);
        Assert.Contains("scale: 1", js);
        Assert.Contains("offsetLeft: 0", js);

        // it sits inside an isTop block
        var vv = js.IndexOf("G.VisualViewport", System.StringComparison.Ordinal);
        var lastIsTop = js.LastIndexOf("if (isTop) {", vv, System.StringComparison.Ordinal);
        Assert.True(lastIsTop > 0 && lastIsTop < vv, "the viewport patch is inside an isTop block");

        // and the clientWidth pin, which is per-realm, comes after it
        var pin = js.IndexOf("clientWidth", System.StringComparison.Ordinal);
        Assert.True(pin > vv);
    }

    /// <summary>The values are the phone's, and the scale is exactly one.</summary>
    [Fact]
    public void TheValuesAreThePhones()
    {
        var js = MobileSurface.BodyJs();

        Assert.Contains("width: " + MobileSurface.ScreenWidth, js);
        Assert.Contains("height: " + MobileSurface.ViewportHeight, js);

        // no throw anywhere in the block
        var start = js.IndexOf("G.VisualViewport", System.StringComparison.Ordinal);
        var end = js.IndexOf("clientWidth", System.StringComparison.Ordinal);
        Assert.DoesNotContain("throw ", js[start..end]);
    }
}
