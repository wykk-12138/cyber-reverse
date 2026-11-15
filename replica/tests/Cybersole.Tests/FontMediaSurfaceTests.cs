using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>R198: text metrics and the media-type verdicts, measured against the tables the target ships.</summary>
public sealed class FontMediaSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public FontMediaSurfaceTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const c = document.createElement('canvas'); const x = c.getContext('2d'); " +
        "x.font = '16px monospace'; const exact = x.measureText('mmmmmmmmmmlli').width; " +
        "x.font = '16px   monospace'; const loose = x.measureText('mmmmmmmmmmlli').width; " +
        "const audio = document.createElement('audio'); const video = document.createElement('video'); " +
        "return JSON.stringify([exact, loose, " +
        "audio.canPlayType('audio/mpeg'), video.canPlayType('audio/mpeg'), " +
        "audio.canPlayType('audio/ogg; codecs=\"vorbis\"'), " +
        "typeof window.MediaSource, typeof window.SourceBuffer, " +
        "typeof window.ManagedMediaSource, " +
        "window.ManagedMediaSource ? window.ManagedMediaSource.isTypeSupported('audio/mpeg') : null, " +
        "window.ManagedMediaSource ? window.ManagedMediaSource.isTypeSupported('nonsense/x') : null, " +
        "typeof window.MediaRecorder === 'function' ? MediaRecorder.isTypeSupported('audio/mpeg') : null]); })()";

    private static async Task<string?> MeasureAsync(bool stealth)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        if (stealth) await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return await bridge.EvaluateAsync(Probe);
    }

    [Fact]
    public async Task TheMetricsAreTheDevices()
    {
        var probe = await MeasureAsync(stealth: true);
        _out.WriteLine("fonts = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        var table = System.Text.Json.JsonDocument.Parse(FontMediaTable.FontsJs);
        var expected = table.RootElement.GetProperty("16px monospace|mmmmmmmmmmlli").GetProperty("width").GetDouble();

        Assert.Equal(expected, r[0].GetDouble(), 5);

        // the lookup is normalised on BOTH sides, so extra whitespace in the caller's font still hits the table
        Assert.Equal(r[0].GetDouble(), r[1].GetDouble(), 5);
    }

    [Fact]
    public async Task TheMediaVerdictsAreTheDevices()
    {
        var probe = await MeasureAsync(stealth: true);
        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        var media = System.Text.Json.JsonDocument.Parse(FontMediaTable.MediaJs).RootElement
            .GetProperty("audio/mpeg");
        Assert.Equal(media.GetProperty("audio").GetString(), r[2].GetString());
        Assert.Equal(media.GetProperty("video").GetString(), r[3].GetString());

        // the row that used to be "" — a missing row is louder than a wrong verdict
        Assert.False(string.IsNullOrEmpty(r[4].GetString()), "audio/ogg answered empty and drops out of the list");

        // WebKit has no MediaSource, and does have ManagedMediaSource
        Assert.Equal("undefined", r[5].GetString());
        Assert.Equal("undefined", r[6].GetString());
        Assert.Equal("function", r[7].GetString());
        Assert.True(r[8].GetBoolean());
        Assert.False(r[9].GetBoolean());
    }

    [Fact]
    public async Task TheRawEngineDisagrees()
    {
        var raw = await MeasureAsync(stealth: false);
        using var doc = System.Text.Json.JsonDocument.Parse(raw!);
        var r = doc.RootElement;

        _out.WriteLine("raw MediaSource=" + r[5] + " ManagedMediaSource=" + r[7]);
        Assert.Equal("function", r[5].GetString());      // Blink has MediaSource, WebKit does not
        Assert.Equal("undefined", r[7].GetString());     // and has no ManagedMediaSource
    }

    [Fact]
    public void TheTablesAreVerbatim()
    {
        Assert.Equal(221, FontMediaTable.FontCount);
        Assert.Equal(18, FontMediaTable.MediaCount);
        Assert.Contains("16px monospace|mmmmmmmmmmlli", FontMediaTable.FontsJs);
        Assert.Contains("\"managed\": true", FontMediaTable.MediaJs);
        Assert.Equal(2, FontMediaSurface.Absent.Length);
        Assert.Contains("louder signal", FontMediaSurface.MediaRule);
    }
}
