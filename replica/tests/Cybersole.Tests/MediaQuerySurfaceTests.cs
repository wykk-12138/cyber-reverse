using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>R197: matchMedia, measured against the raw engine and against the table the target ships.</summary>
public sealed class MediaQuerySurfaceTests
{
    private readonly ITestOutputHelper _out;
    public MediaQuerySurfaceTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const m = (q) => { try { return matchMedia(q); } catch (e) { return null; } }; " +
        "const coarse = m('(pointer:coarse)'), spaced = m('(pointer: coarse)'); " +
        "const built = m('(device-width: 402px) and (device-height: 874px)'); " +
        "const wrong = m('(device-width: 1200px)'); " +
        "return JSON.stringify([" +
        "coarse ? coarse.matches : null, spaced ? spaced.matches : null, spaced ? spaced.media : null, " +
        "built ? built.matches : null, wrong ? wrong.matches : null, " +
        "m('(prefers-reduced-transparency: reduce)').matches, " +
        "m('(prefers-reduced-transparency: no-preference)').matches, " +
        "m('(min-resolution: 2dppx)').matches, m('(monochrome)').matches, " +
        "m('screen and (min-width: 100px)').media]); })()";

    private static async Task<string?> MeasureAsync(bool stealth)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        if (stealth) await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return await bridge.EvaluateAsync(Probe);
    }

    [Fact]
    public async Task TheQueriesAnswerTheDevice()
    {
        var raw = await MeasureAsync(stealth: false);
        var patched = await MeasureAsync(stealth: true);
        _out.WriteLine("raw     = " + raw);
        _out.WriteLine("patched = " + patched);

        using var doc = System.Text.Json.JsonDocument.Parse(patched!);
        var r = doc.RootElement;

        // both spellings of the same query, and the re-serialised .media
        Assert.True(r[0].GetBoolean(), "(pointer:coarse) did not match");
        Assert.True(r[1].GetBoolean(), "(pointer: coarse) did not match the same table entry");
        Assert.Equal("(pointer: coarse)", r[2].GetString());

        // the query hsw BUILDS from screen.* — it must confirm itself
        Assert.True(r[3].GetBoolean(), "the 402x874 query denied the screen this page reports");
        Assert.False(r[4].GetBoolean(), "a wrong device-width matched");

        // prefers-reduced-transparency is a Blink feature: WebKit answers NEITHER half
        Assert.False(r[5].GetBoolean());
        Assert.False(r[6].GetBoolean());

        // the geometry-derived ones
        Assert.True(r[7].GetBoolean(), "min-resolution: 2dppx did not match a 3dppx device");

        // a media type is left to the engine, and .media keeps the caller's spacing
        Assert.Equal("screen and (min-width: 100px)", r[9].GetString());
    }

    [Fact]
    public async Task TheRawEngineDisagrees()
    {
        var raw = await MeasureAsync(stealth: false);
        using var doc = System.Text.Json.JsonDocument.Parse(raw!);
        var r = doc.RootElement;

        _out.WriteLine("raw coarse=" + r[0] + " built=" + r[3]);

        // on the host display the self-confirming query is false — that is the hole this layer closes
        Assert.False(r[3].GetBoolean());
    }

    [Fact]
    public void TheTablesAreVerbatim()
    {
        Assert.Equal(44, MediaQueryTable.QueryCount);
        Assert.Equal(9, MediaQueryTable.GeometryCount);
        Assert.Contains("(pointer:coarse)", MediaQueryTable.QueriesJs);
        Assert.Contains("\"device-width\": 402", MediaQueryTable.GeometryJs);
        Assert.Contains("both halves", MediaQuerySurface.Rule);
        Assert.Contains("402x874", MediaQuerySurface.GeometryRule);
    }
}
