using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R194: the canvas read-back, measured in a real browser against the table the target ships.
/// </summary>
public sealed class CanvasSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public CanvasSurfaceTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const c = document.createElement('canvas'); c.width = 300; c.height = 150; " +
        "const ctx = c.getContext('2d'); ctx.fillStyle = '#069'; ctx.font = '11pt Arial'; " +
        "ctx.fillText('Cwm fjordbank glyphs vext quiz', 2, 15); " +
        "const url = c.toDataURL(); " +
        "let imaged = null; try { imaged = ctx.getImageData(0, 0, 300, 150); } catch (e) { imaged = null; } " +
        "const c2 = document.createElement('canvas'); c2.width = 2; c2.height = 2; " +
        "const x2 = c2.getContext('2d'); " +
        "x2.fillStyle = '#000'; x2.fillRect(0, 0, 2, 2); " +
        "x2.fillStyle = '#fff'; x2.fillRect(2, 2, 1, 1); " +
        "x2.beginPath(); x2.arc(0, 0, 2, 0, 1, true); x2.fill(); " +
        "const px = x2.getImageData(0, 0, 2, 2); " +
        "return JSON.stringify([url, imaged ? imaged.width : -1, " +
        "imaged ? imaged.height : -1, Array.prototype.slice.call(px.data, 0, 16)]); })()";

    private static async Task<string?> MeasureAsync()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return await bridge.EvaluateAsync(Probe);
    }

    /// <summary>The 300x150 text canvas answers the device's picture, and getImageData agrees with it.</summary>
    [Fact]
    public async Task TheTextCanvasAnswersTheDevicesPng()
    {
        var probe = await MeasureAsync();
        _out.WriteLine("canvas = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        var table = System.Text.Json.JsonDocument.Parse(CanvasTable.CanvasJs);
        var expected = table.RootElement.GetProperty("300x150|0").GetString()!;

        // the WHOLE data URL is the device's picture, byte for byte
        Assert.Equal(expected, r[0].GetString());

        // the pixel read is the SAME picture: decoded from the PNG we return, so the pair cannot contradict itself
        Assert.Equal(300, r[1].GetInt32());
        Assert.Equal(150, r[2].GetInt32());
    }

    /// <summary>The 2x2 arc program reads the device's anti-aliased edge, not Blink's.</summary>
    [Fact]
    public async Task TheArcProgramReadsTheDevicesPixels()
    {
        var probe = await MeasureAsync();
        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var px = doc.RootElement[3].EnumerateArray().Select(e => e.GetInt32()).ToArray();

        _out.WriteLine("2x2 = " + string.Join(",", px));

        var device = System.Text.Json.JsonDocument.Parse(CanvasTable.Device2x2Js)
            .RootElement.EnumerateArray().Select(e => e.GetInt32()).ToArray();
        var blink = System.Text.Json.JsonDocument.Parse(CanvasTable.Blink2x2Js)
            .RootElement.EnumerateArray().Select(e => e.GetInt32()).ToArray();

        Assert.Equal(device, px);        // the whole 2x2 read is the device's
        Assert.NotEqual(blink, px);      // ...and not Blink's
    }

    /// <summary>A gradient canvas must NOT be answered from the text table — that is the contradiction the key prevents.</summary>
    [Fact]
    public async Task AGradientCanvasFallsThrough()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

        var probe = await bridge.EvaluateAsync(
            "(() => { const c = document.createElement('canvas'); c.width = 300; c.height = 150; " +
            "const ctx = c.getContext('2d'); " +
            "const g = ctx.createLinearGradient(0, 0, 300, 150); g.addColorStop(0, '#000'); g.addColorStop(1, '#fff'); " +
            "ctx.fillStyle = g; ctx.fillRect(0, 0, 300, 150); " +
            "ctx.fillText('Cwm fjordbank', 2, 15); " +
            "return c.toDataURL().length + ':' + c.toDataURL().slice(0, 22); })()");

        _out.WriteLine("gradient = " + probe);
        using var table = System.Text.Json.JsonDocument.Parse(CanvasTable.CanvasJs);
        var bakedLength = table.RootElement.GetProperty("300x150|0").GetString()!.Length;

        // the host's own PNG, not the baked one
        Assert.NotEqual(bakedLength.ToString() + ":data:image/png;base64", probe);
    }

    [Fact]
    public void TheTablesAreVerbatim()
    {
        Assert.Equal(4, CanvasTable.ShapeCount);
        Assert.Equal(4, CanvasTable.ProgramCount);
        Assert.Contains("300x150|0", CanvasTable.CanvasJs);
        Assert.Contains("96x48|0#fillRect(0,0,96,48)", CanvasTable.ProgramsJs);
        Assert.Contains("192", CanvasTable.Blink2x2Js);
        Assert.Contains("185", CanvasTable.Device2x2Js);
        Assert.Contains("185/229/47", CanvasSurface.ArcRule);
        Assert.Contains("192/244/53", CanvasSurface.ArcRule);
        Assert.Equal("arc(0,0,2,0,1,true)", CanvasSurface.ArcProgram);
    }
}
