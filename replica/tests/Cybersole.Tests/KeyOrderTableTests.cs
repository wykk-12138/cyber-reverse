using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 180: one <c>reorder</c>, three entry points, and five kinds of rule.
///
/// <para>
/// The sharpest measurement in the block is the <c>CSSStyleDeclaration</c> instance: filtering it to the device's own
/// vocabulary still produced <b>1505</b> names — the correct 881 followed by 624 duplicates in Blink's order — because
/// Blink hangs the camelCase properties off the instance while WebKit hangs them off <c>CSSStyleProperties.prototype</c>.
/// The answer that matches is the numeric indices alone.
/// </para>
///
/// <para>
/// And the symbol half: bailing out of any symbol-bearing object made <c>getOwnPropertyNames</c> and
/// <c>Reflect.ownKeys</c> disagree about the same object, since every interface prototype carries
/// <c>Symbol.toStringTag</c>.
/// </para>
/// </summary>
public sealed class KeyOrderTableTests
{
    private readonly ITestOutputHelper _out;

    public KeyOrderTableTests(ITestOutputHelper output) => _out = output;

    /// <summary>The tables are the capture's.</summary>
    [Fact]
    public void TheTablesAreTheCaptures()
    {
        Assert.Equal(2, KeyOrderTable.MainFrameOnly.Count);
        Assert.Contains("_injected_scroll_helper", KeyOrderTable.MainFrameOnly);
        Assert.Contains("_injected_navigation", KeyOrderTable.MainFrameOnly);

        Assert.Equal(3, KeyOrderTable.EntryPoints.Count);
        Assert.Contains("Reflect.ownKeys", KeyOrderTable.EntryPoints);

        Assert.Equal(2, KeyOrderTable.Rules.Count);
        Assert.Equal("Navigator.prototype", KeyOrderTable.Rules[0].Matches);
        Assert.Equal("Screen.prototype", KeyOrderTable.Rules[1].Matches);

        Assert.Equal(881, KeyOrderTable.DeviceNameCount);
        Assert.Equal(1505, KeyOrderTable.MeasuredWithoutFilter);
        Assert.Equal(1505 - 881, KeyOrderTable.MeasuredWithoutFilter - KeyOrderTable.DeviceNameCount);
        Assert.Equal("^[0-9]+$", KeyOrderTable.CssInstanceFilter);

        _out.WriteLine(KeyOrderTable.DuplicateRule);
    }

    /// <summary>The dispatch that used to live here is now in WindowOrderWrap, and this class says so.</summary>
    [Fact]
    public void TheBodyMovedToTheDispatch()
    {
        var bridge = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs"));

        Assert.Contains("WindowOrderWrap.BodyJs()", bridge);
        Assert.DoesNotContain("KeyOrderTable.BodyJs()", bridge);
        Assert.Contains("WindowOrderWrap", KeyOrderTable.SupersededBy);
        Assert.Contains("KeyOrderRules", KeyOrderTable.SupersededBy);

        // the live dispatch carries the same four answers this class records
        var js = WindowOrderWrap.BodyJs();
        Assert.Contains("target instanceof CSSStyleDeclaration", js);
        Assert.Contains("INDEX.test(n)", js);
        Assert.Contains("rule.drop", js);
        Assert.Contains("for (let i = 0; i < ORDER.length; i++) {", js);
        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }
    /// <summary>Measured on a bare page: symbols stay last, and a CSS instance owns numeric indices only.</summary>
    [Fact]
    public async Task TheEngineAlreadyPutsSymbolsLast()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                              "Mobile/15E148 Safari/604.1";

        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: iphone);
        await bridge.ApplyStealthAsync(iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        // Unwired, the entry points are the engine's own functions — and the cloak (R172) reformats every native source
        // into WebKit's three-line form, so three lines each is the correct baseline, not one.
        var sources = await bridge.EvaluateAsync(
            "JSON.stringify([Function.prototype.toString.call(Object.getOwnPropertyNames)," +
            "Function.prototype.toString.call(Reflect.ownKeys)].map((s) => s.split('\\n').length))");
        _out.WriteLine("sources = " + sources);
        Assert.Equal("[3,3]", sources);

        // symbols stay last on a symbol-bearing object
        var symbols = await bridge.EvaluateAsync(
            "JSON.stringify((() => { const k = Reflect.ownKeys(Navigator.prototype); " +
            "let seenSymbol = false, bad = 0; k.forEach((x) => { " +
            "if (typeof x === 'symbol') seenSymbol = true; else if (seenSymbol) bad++; }); return bad; })())");
        Assert.Equal("0", symbols);

        // a CSS declaration instance answers numeric indices only
        var css = await bridge.EvaluateAsync(
            "(() => { const el = document.body; el.style.color = 'red'; " +
            "const names = Object.getOwnPropertyNames(el.style); " +
            "return String(names.filter((n) => !/^[0-9]+$/.test(n)).length) + ':' + String(names.length); })()");
        _out.WriteLine("css non-numeric:total = " + css);

        // WIRED since R188: the dispatch answers a declaration instance with its numeric indices alone, so the gap this
        // test was written to record is closed and the number is the proof -- measured 1230 -> 480, all numeric.
        var nonNumeric = int.Parse(css!.Split(':')[0]);
        Assert.Equal(0, nonNumeric);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
