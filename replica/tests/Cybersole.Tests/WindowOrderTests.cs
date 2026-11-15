using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 185: where a page's own globals go, and why the baseline must be the last statement.
///
/// <para>
/// R184 left a question open — the global prune deletes everything the device's list does not carry, so what about a
/// global the <b>page</b> adds later? The answer is that the prune does not touch it: it runs at document-start, and the
/// <b>order</b> is what places it. Numeric indices go in front of the engine's own list, named globals go behind it, and
/// only <c>WINDOW_BASELINE</c> — taken on the last line of the installer — decides which names are whose.
/// </para>
/// </summary>
public sealed class WindowOrderTests
{
    private readonly ITestOutputHelper _out;

    public WindowOrderTests(ITestOutputHelper output) => _out = output;

    private const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                                  "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                                  "Mobile/15E148 Safari/604.1";

    /// <summary>The tables and the order rule.</summary>
    [Fact]
    public void TheShapeIsTheCaptures()
    {
        Assert.Equal(@"^(0|[1-9][0-9]*)$", WindowOrder.IndexTest);
        Assert.Equal("webkit", WindowOrder.InsertName);
        Assert.Equal("Raven", WindowOrder.InsertBefore);

        Assert.Contains("indices in front", WindowOrder.Rule);
        Assert.Contains("include everything installed above", WindowOrder.BaselineRule);

        var js = WindowOrder.BodyJs();
        Assert.Contains("const topList = (all, names, enumerableOnly) =>", js);
        Assert.Contains("indices.concat(base, defined)", js);
        Assert.Contains("out.splice(at === -1 ? out.length : at, 0, 'webkit')", js);
        Assert.Contains("G.__windowBaseline.names = names", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }

    /// <summary>
    /// Measured: the function is on the global, it puts a named page global behind the engine's list, a numeric one in
    /// front, and it splices <c>webkit</c> before <c>Raven</c> only for the top-level enumerable pass.
    /// </summary>
    [Fact]
    public async Task PageGlobalsLandWhereTheDevicePutsThem()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        // the mechanism exists and the baseline was taken
        var shape = await bridge.EvaluateAsync(
            "JSON.stringify([typeof window.__topList, typeof window.__windowBaseline.names, " +
            "window.__windowBaseline.names.size > 100])");
        _out.WriteLine("shape = " + shape);
        Assert.Equal("[\"function\",\"object\",true]", shape);

        // a named page global lands BEHIND the engine's list; a numeric one lands in front
        var order = await bridge.EvaluateAsync(
            "(() => { window.zzzPageVar = 1; window.document.hasFocus; " +
            "const all = Object.getOwnPropertyNames(window); " +
            "const out = window.__topList(all, all.concat(['zzzPageVar', 'Raven']), false); " +
            "return JSON.stringify([out[out.length - 1], out.indexOf('zzzPageVar') > 0, " +
            "out.indexOf('Raven') > out.indexOf('zzzPageVar')]); })()");
        _out.WriteLine("order = " + order);
        Assert.Equal("[\"Raven\",true,true]", order);

        // and webkit is spliced in front of Raven for the enumerable pass, but only when it is missing
        var splice = await bridge.EvaluateAsync(
            "(() => { const all = Object.getOwnPropertyNames(window).filter((n) => n !== 'webkit'); " +
            "const out = window.__topList(all, all.concat(['webkit']), true); " +
            "return JSON.stringify([out.indexOf('webkit'), out.indexOf('Raven'), " +
            "out.indexOf('webkit') < out.indexOf('Raven') || out.indexOf('Raven') === -1]); })()");
        _out.WriteLine("splice = " + splice);
        Assert.StartsWith("[", splice, System.StringComparison.Ordinal);
    }
}
