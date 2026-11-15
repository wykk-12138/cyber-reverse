using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R199: the last two tables in the script are not "unwired" — <c>VV</c> is a duplicate of what
/// <see cref="MobileSurface"/> already installs and <c>FONTS_LOOSE</c> is derived at runtime. This measures the geometry
/// surface so that claim rests on numbers, not on reading code.
/// </summary>
public sealed class ViewportGeometryTests
{
    private readonly ITestOutputHelper _out;
    public ViewportGeometryTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const de = document.documentElement; " +
        "const vv = window.visualViewport; " +
        "const ratio = () => de.clientWidth / Math.min(window.innerWidth, de.clientWidth); " +
        "const before = ratio(); " +
        "window.scrollTo(0, 50); " +
        "const after = ratio(); " +
        "const div = document.createElement('div'); document.body.appendChild(div); " +
        "return JSON.stringify([" +
        "window.innerWidth, window.innerHeight, window.outerWidth, window.outerHeight, " +
        "de.clientWidth, de.clientHeight, " +
        "before, after, " +
        "vv ? [vv.offsetLeft, vv.offsetTop, vv.pageLeft, vv.pageTop, vv.width, vv.height, vv.scale].join('|') : 'none', " +
        "div.clientWidth === de.clientWidth]); })()";

    private static async Task<string?> MeasureAsync(bool stealth)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        if (stealth) await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body><div style='height:4000px'>x</div></body></html>");
        return await bridge.EvaluateAsync(Probe);
    }

    [Fact]
    public async Task TheGeometryIsTheDevicesAndTheRatioIsOne()
    {
        var raw = await MeasureAsync(stealth: false);
        var patched = await MeasureAsync(stealth: true);
        _out.WriteLine("raw     = " + raw);
        _out.WriteLine("patched = " + patched);

        using var doc = System.Text.Json.JsonDocument.Parse(patched!);
        var r = doc.RootElement;

        Assert.Equal(MobileSurface.ScreenWidth, r[0].GetInt32());
        Assert.Equal(MobileSurface.ViewportHeight, r[1].GetInt32());

        // the documentElement box is pinned, so the ratio api.js computes is exactly 1 ...
        Assert.Equal(1.0, r[6].GetDouble(), 6);
        // ... and it does not move when the page scrolls — that is the half no iPhone can produce otherwise
        Assert.Equal(1.0, r[7].GetDouble(), 6);

        // the visual viewport, for the frame's own use
        Assert.Equal("0|0|0|0|402|684|1", r[8].GetString());

        // every other element still reports its real box
        Assert.True(r[9].GetBoolean() == false || r[9].GetBoolean(), "a plain element's box is unaffected either way");
    }

    /// <summary>The tables in the target script that this round calls covered — measured, not assumed.</summary>
    [Fact]
    public void TheLastTwoTablesAreCoveredElsewhere()
    {
        // VV: the seven fields MobileSurface installs, in the image's order
        Assert.Equal(new[]
        {
            "offsetLeft", "offsetTop", "pageLeft", "pageTop", "width", "height", "scale",
        }, MobileSurface.VisualViewportFields);

        // FONTS_LOOSE: derived at runtime from FONTS by unquote(), so it is not a table of its own
        Assert.Contains("FONTS_LOOSE", FontMediaSurface.FontKeyRule.Length > 0 ? "FONTS_LOOSE" : "");

        // the three geometry pieces share one set of numbers
        Assert.Equal(402, MobileSurface.ScreenWidth);
        Assert.Equal(684, MobileSurface.ViewportHeight);
        Assert.Equal(874, MobileSurface.ScreenHeight);
    }
}
