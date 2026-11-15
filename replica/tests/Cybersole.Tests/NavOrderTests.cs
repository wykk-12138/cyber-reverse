using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 165: the reseat executes, and the measurement says how much of the recorded order is achievable.
///
/// <para>
/// R159 recorded <c>NAV_ORDER</c> and registered nothing. The mechanism is the one the image itself uses on the Screen
/// prototype: delete and re-add, which moves a property to the end, applied in sequence. Non-configurable properties
/// cannot move, so what this round can honestly promise is the recorded order <b>restricted to what moves</b> — and
/// the runtime test measures that instead of asserting the ideal.
/// </para>
/// </summary>
public sealed class NavOrderTests
{
    private readonly ITestOutputHelper _out;

    public NavOrderTests(ITestOutputHelper output) => _out = output;

    /// <summary>The body reseats the navigator prototype in the recorded order.</summary>
    [Fact]
    public void TheBodyReseats()
    {
        var js = NavOrder.ReseatBodyJs(NavOrder.Navigator);

        Assert.Contains("Object.getPrototypeOf(G.navigator)", js);
        Assert.Contains("delete target[name]", js);
        Assert.Contains("Object.defineProperty(target, name, d)", js);
        Assert.Contains("if (!d || !d.configurable) return;", js);
        Assert.Contains("'standalone'", js);
        Assert.Contains("'__lookupSetter__'", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The two orders this workspace reseats with are the two the image records.</summary>
    [Fact]
    public void TheTwoOrdersAreTheImages()
    {
        // 50, not 49: the comment in R159 said 49 and the list itself has fifty entries — the sort of number
        // that is worth taking from the data rather than from a sentence about the data.
        Assert.Equal(50, NavOrder.Navigator.Count);
        Assert.Equal(9, NavOrder.Screen.Count);
        Assert.Equal("standalone", NavOrder.Navigator[0]);
        Assert.Equal("__lookupSetter__", NavOrder.Navigator[^1]);
        Assert.Equal("height", NavOrder.Screen[0]);
        Assert.Equal("orientation", NavOrder.Screen[^1]);

        _out.WriteLine(string.Join(",", NavOrder.Navigator.Take(6)) + " …");
    }

    /// <summary>The limit is stated rather than hidden.</summary>
    [Fact]
    public void TheLimitIsStated()
    {
        Assert.Contains("cannot be moved", NavOrder.Limit);
        Assert.Contains("restricted to", NavOrder.Limit);
        Assert.Contains("measurement", NavOrder.Limit);
    }

    /// <summary>Measured: how much of the order the browser allows.</summary>
    [Fact]
    public async Task TheReseatIsMeasured()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                              "Mobile/15E148 Safari/604.1";

        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var report = await bridge.EvaluateAsync(
            "JSON.stringify({ before: Object.getOwnPropertyNames(Navigator.prototype), " +
            "forIn: (() => { const out = []; for (const k in navigator) out.push(k); return out; })() })");

        _out.WriteLine("before = " + report);

        await bridge.ApplyStealthAsync(iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var after = await bridge.EvaluateAsync(
            "JSON.stringify({ own: Object.getOwnPropertyNames(Navigator.prototype), " +
            "forIn: (() => { const out = []; for (const k in navigator) out.push(k); return out; })() })");

        _out.WriteLine("after  = " + after);

        var parsed = Newtonsoft.Json.Linq.JObject.Parse(after!);
        var achieved = parsed["own"]!.Select(t => (string)t!).ToList();

        // the movable ones are now in the recorded order; measure how many of the 49 are present at all
        var present = NavOrder.Navigator.Where(n => achieved.Contains(n)).ToList();
        var relativeOrder = present.SequenceEqual(achieved.Where(n => present.Contains(n)));
        _out.WriteLine($"recorded names present on the prototype: {present.Count}/{NavOrder.Navigator.Count}");
        _out.WriteLine($"relative order preserved: {relativeOrder}");

        // What the browser allows, measured rather than assumed (R165): 28 of the fifty recorded names live on
        // Navigator.prototype at all — the rest are inherited from Object.prototype or absent from this engine —
        // and among those that do exist the recorded relative order is achieved exactly. The non-movable Blink
        // names sit in front of everything, which no reseat can change.
        Assert.True(relativeOrder, "the recorded relative order is achieved among the properties that exist");
        Assert.True(present.Count >= 20, $"only {present.Count} of the recorded names exist on the prototype");

        // and the members this workspace installs are in the achieved order
        Assert.Contains("maxTouchPoints", achieved);

        // R167 installs `standalone` and `locks` explicitly, so they are present even where the engine lacked them
        Assert.Contains("standalone", achieved);
        Assert.Contains("locks", achieved);
    }
}
