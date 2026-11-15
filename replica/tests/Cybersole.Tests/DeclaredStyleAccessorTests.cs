using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R191: two suspicions from the last round, measured. (1) <c>dashed('cssFloat')</c> produces <c>css-float</c>, which
/// is not a CSS property. (2) the ORDER rules match constructors by identity, so a child realm may fall through.
/// </summary>
public sealed class DeclaredStyleAccessorTests
{
    private readonly ITestOutputHelper _out;
    public DeclaredStyleAccessorTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private static async Task<Cybersole.Stores.Scripts.ChromiumBridge> PageAsync(bool stealth = true)
    {
        var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        if (stealth) await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body><div id='d' style='float:left;color:red'>x</div></body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }
        return bridge;
    }

    private const string Probe =
        "(() => { const d = document.getElementById('d'); const cs = getComputedStyle(d); " +
        "return JSON.stringify([" +
        "cs.cssFloat, " +                                  // 0 the suspect
        "cs.getPropertyValue('float'), " +                 // 1 the correct name
        "cs.getPropertyValue('css-float'), " +             // 2 the name the accessor builds
        "cs.color, " +                                     // 3 a mapping that should work
        "cs.webkitTransform, " +                           // 4 the -webkit- prefix rule
        "typeof cs.length + ':' + cs.length, " +           // 5 not shadowed by the synthesis
        "typeof cs.item, " +                               // 6 still a method
        "typeof cs.cssText, " +                            // 7 still the declaration's own
        "cs.getPropertyValue('color')]); })()";            // 8 still works

    [Fact]
    public async Task WhatTheAccessorsAnswer()
    {
        var raw = await Measured(false);
        var patched = await Measured(true);
        _out.WriteLine("raw     = " + raw);
        _out.WriteLine("patched = " + patched);

        using var doc = System.Text.Json.JsonDocument.Parse(patched!);
        var p = doc.RootElement;

        // the declaration must still behave like one
        Assert.StartsWith("number:", p[5].GetString());
        Assert.Equal("function", p[6].GetString());
        Assert.Equal("string", p[7].GetString());
        Assert.Equal("rgb(255, 0, 0)", p[8].GetString());

        // a camelCase name that maps cleanly
        Assert.Equal("rgb(255, 0, 0)", p[3].GetString());
    }

    /// <summary>Which realm's constructors the ORDER rules see.</summary>
    [Fact]
    public async Task TheOrderRulesInsideAChild()
    {
        await using var bridge = await PageAsync();
        await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); f.id = 'f'; document.body.appendChild(f); return 'ok'; })()");
        await Task.Delay(400);

        var probe = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('f').contentWindow; " +
            "const own = w.Object.getOwnPropertyNames(w.CSSStyleDeclaration.prototype); " +
            "return JSON.stringify({" +
            "sharedObject: w.Object === Object, " +
            "sameEntryPoint: w.Object.getOwnPropertyNames === Object.getOwnPropertyNames, " +
            "lines: Function.prototype.toString.call(w.Object.getOwnPropertyNames).split('\\n').length, " +
            "topList: typeof w.__topList, " +
            "cssProto: typeof w.__cssProto, " +
            "iface: typeof w.CSSStyleProperties, " +
            "count: own.length, " +
            "names: own.join('|'), " +
            "webgl: w.Object.getOwnPropertyNames(w.WebGL2RenderingContext).slice(0, 3).join('|'), " +
            "parentObjectPatches: window.__patchJournal ? window.__patchJournal.patches.filter(" +
            "  (r) => r.path && r.path[0] === 'Object').map((r) => r.path.join('.') + '#' + r.key).join(',') : 'none', " +
            "known: window.__patchJournal ? window.__patchJournal.known.join(',') : 'none' }); })()");

        _out.WriteLine("order = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        // the child must own its entry points, or its wrapper's identity checks fire against the parent's constructors
        Assert.False(r.GetProperty("sameEntryPoint").GetBoolean(), "the child shares the parent's Object.getOwnPropertyNames");

        // ...and then CSS_DECL answers, in the device's order. Measured before the fix: 12 raw Blink names.
        Assert.Equal(11, r.GetProperty("count").GetInt32());
        Assert.Equal(
            "constructor|cssText|cssRules|length|parentRule|item|getPropertyValue|getPropertyPriority|setProperty|"
            + "removeProperty|getPropertyCSSValue",
            r.GetProperty("names").GetString());

        // the ORDER table fires in the child too, on the child's own constructors
        Assert.Equal("length|name|prototype", r.GetProperty("webgl").GetString());

        // and the interface itself is reachable there
        Assert.Equal("object", r.GetProperty("cssProto").GetString());
        Assert.Equal("function", r.GetProperty("iface").GetString());
    }

    private static async Task<string?> Measured(bool stealth)
    {
        await using var bridge = await PageAsync(stealth);
        return await bridge.EvaluateAsync(Probe);
    }
}
