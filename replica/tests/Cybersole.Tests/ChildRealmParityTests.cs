using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R190: what a same-origin child realm actually answers. Every number here is measured; the assertions say what the
/// measurement is, not what I hoped it would be.
/// </summary>
public sealed class ChildRealmParityTests
{
    private readonly ITestOutputHelper _out;
    public ChildRealmParityTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private static async Task<Cybersole.Stores.Scripts.ChromiumBridge> PageAsync()
    {
        var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }
        return bridge;
    }

    /// <summary>The child's own copy of every surface this workspace installs.</summary>
    [Fact]
    public async Task TheChildIsPatchedToo()
    {
        await using var bridge = await PageAsync();

        await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); f.id = 'f'; " +
            "document.body.appendChild(f); return 'ok'; })()");
        await Task.Delay(400);

        var probe = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('f').contentWindow; " +
            "w.document.body.innerHTML = 'x'; " +
            "const cs = w.getComputedStyle(w.document.body); " +
            "const lines = (f) => Function.prototype.toString.call(f).split('\\n').length; " +
            "return JSON.stringify([" +
            "typeof w.CSSStyleProperties, " +                            // 0 synthesized in the child?
            "lines(w.getComputedStyle), " +                              // 1 cloaked?
            "lines(w.Object.keys), " +                                   // 2 cloaked?
            "Object.prototype.toString.call(cs), " +                     // 3 class string
            "cs.constructor.name, " +                                    // 4 constructor name
            "('appRegion' in cs), " +                                    // 5 hidden in the child?
            "cs.hasOwnProperty('appRegion'), " +                         // 6
            "(cs instanceof w.CSSStyleDeclaration), " +                   // 7 brand survives
            "w.CSSStyleProperties ? Object.getPrototypeOf(cs) === w.CSSStyleProperties.prototype : null, " + // 8
            "cs.getPropertyValue('color') " +                             // 9 still works
            "]); })()");

        _out.WriteLine("child = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var c = doc.RootElement;

        // [CSSStyleProperties?, lines(getComputedStyle), lines(Object.keys), class string, constructor name,
        //  'appRegion' in cs, hasOwnProperty('appRegion'), instanceof, proto identity, getPropertyValue]
        Assert.Equal("function", c[0].GetString());
        Assert.Equal(3, c[1].GetInt32());          // cloaked through the SHARED table (R190)
        Assert.Equal(3, c[2].GetInt32());
        Assert.Equal("[object CSSStyleProperties]", c[3].GetString());
        Assert.Equal("CSSStyleProperties", c[4].GetString());

        // the two channels must agree in the child too — this was the measured defect (R190)
        Assert.False(c[5].GetBoolean(), "'appRegion' is in the child's computed style");
        Assert.False(c[6].GetBoolean(), "hasOwnProperty('appRegion') is true in the child");

        // and the child's proto must be the CHILD's, or instanceof breaks in the frame that matters
        Assert.True(c[7].GetBoolean(), "cs is not an instance of the child's CSSStyleDeclaration");
        Assert.True(c[8].GetBoolean(), "getPrototypeOf(cs) is not the child's CSSStyleProperties.prototype");

        Assert.Equal("rgb(0, 0, 0)", c[9].GetString());
    }

    /// <summary>The top realm's own numbers, for the same probe, so the two are comparable.</summary>
    [Fact]
    public async Task TheTopRealmForComparison()
    {
        await using var bridge = await PageAsync();
        var probe = await bridge.EvaluateAsync(
            "(() => { const cs = getComputedStyle(document.body); " +
            "const lines = (f) => Function.prototype.toString.call(f).split('\\n').length; " +
            "return JSON.stringify([" +
            "typeof window.CSSStyleProperties, lines(window.getComputedStyle), lines(Object.keys), " +
            "Object.prototype.toString.call(cs), cs.constructor.name, ('appRegion' in cs), " +
            "cs.hasOwnProperty('appRegion'), (cs instanceof CSSStyleDeclaration), " +
            "Object.getPrototypeOf(cs) === CSSStyleProperties.prototype, cs.getPropertyValue('color')]); })()");

        _out.WriteLine("top   = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));
    }
}
