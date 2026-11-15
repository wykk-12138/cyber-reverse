using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

public sealed class WindowOrderWrapTests
{
    private readonly ITestOutputHelper _out;
    public WindowOrderWrapTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    [Fact]
    public void TheSliceIsNarrow()
    {
        var js = WindowOrderWrap.BodyJs();

        // R187: three entry points, read off the target at 0x03d1efd4 — Object.getOwnPropertyNames, Object.keys
        // and Reflect.ownKeys, the third one wrapping through the symbol split.
        Assert.Equal(new[] { "getOwnPropertyNames", "keys", "ownKeys" },
            WindowOrderWrap.EntryPoints.Select(p => p.Name).ToArray());
        Assert.Equal(new[] { "Object", "Object", "Reflect" },
            WindowOrderWrap.EntryPoints.Select(p => p.Owner).ToArray());
        Assert.Contains("const CSS_DECL = ", js);
        Assert.Contains("install('Reflect', 'ownKeys', false);", js);
        Assert.Contains("const owner = G[host] || (host === 'Object' ? Object : Reflect);", js);

        // R188: the whole dispatch, not just the window branch
        Assert.Contains("if (target === G && G.__topList) {", js);
        Assert.Contains("const recorded = G.__windowNames", js);
        Assert.Contains("return G.__topList(recorded, names, enumerableOnly);", js);
        Assert.Contains("&& target === CSSStyleDeclaration.prototype) {", js);
        Assert.Contains("return names.filter((n) => INDEX.test(n));", js);
        Assert.Contains("for (let i = 0; i < ORDER.length; i++) {", js);
        Assert.Contains("return wanted.concat(extra);", js);
        Assert.Contains("return reorder(target, strings, false).concat(rest);", js);

        Assert.Equal(11, KeyOrderRules.RuleCount);
        Assert.Contains("[object Location]", KeyOrderRules.OrderRulesJs);
        Assert.Contains("\"getPropertyCSSValue\"", KeyOrderRules.CssDeclarationJs);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }

    [Fact]
    public async Task TheWindowIsOrderedAndOtherObjectsAreNot()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var probe = await bridge.EvaluateAsync(
            "(() => { window.zzzPageVar = 1; " +
            "const win = Object.getOwnPropertyNames(window); " +
            "const obj = Object.getOwnPropertyNames({ b: 1, a: 2 }); " +
            "const keys = Object.keys({ b: 1, a: 2 }); " +
            "return JSON.stringify([win[win.length - 1] === 'zzzPageVar', obj.join(','), keys.join(','), " +
            "Function.prototype.toString.call(Object.keys).split('\\n').length]); })()");

        _out.WriteLine("probe = " + probe);
        Assert.Equal("[true,\"b,a\",\"b,a\",3]", probe);
    }

    /// <summary>
    /// R187: <c>Reflect.ownKeys</c> is the third entry point, and the wrapper follows the patch into a child realm.
    /// </summary>
    [Fact]
    public async Task TheOwnKeysEntryPointAndTheChildRealm()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var before = await bridge.EvaluateAsync(
            "(() => { window.__p0 = Object.keys; window.__p0t = Function.prototype.toString; " +
            "return JSON.stringify([Function.prototype.toString.call(Object.keys).split('\\n').length, " +
            "Function.prototype.toString.call(Object.keys).slice(0, 24)]); })()");

        var probe = await bridge.EvaluateAsync(
            "(() => { window.zzzPageVar = 1; " +
            "const own = Reflect.ownKeys(window); " +
            "const sym = own.filter(k => typeof k !== 'string').length; " +
            "const obj = Reflect.ownKeys({ b: 1, a: 2 }).join(','); " +
            "const f = document.createElement('iframe'); f.id = 'probe-frame'; document.body.appendChild(f); " +
            "return JSON.stringify([own[own.length - 1] === 'zzzPageVar', sym === 0, obj]); })()");

        // the journal's hook and the realm replay are both asynchronous: poll until the child has been patched,
        // with a deadline, instead of guessing a fixed wait (a fixed 400 ms failed under a full-suite load).
        for (var i = 0; i < 60; i++)
        {
            var ready = await bridge.EvaluateAsync(
                "String(!!(document.getElementById('probe-frame') && " +
                "document.getElementById('probe-frame').contentWindow.CSSStyleProperties))");
            if (ready == "true") break;
            await System.Threading.Tasks.Task.Delay(100);
        }

        var child = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('probe-frame').contentWindow; " +
            "w.zzzChildVar = 1; " +
            "const own = Object.getOwnPropertyNames(w); " +
            "const same = w.Object.keys === Object.keys && w.Reflect.ownKeys === Reflect.ownKeys; " +
            "const sameToString = w.Function.prototype.toString === Function.prototype.toString; " +
            "const cloaked = Function.prototype.toString.call(w.Object.keys).split('\\n').length; " +
            "const top = Function.prototype.toString.call(Object.keys).split('\\n').length; " +
            "const replaced = Object.keys !== window.__p0; " +
            "const p0 = window.__p0t.call(window.__p0).split('\\n').length; " +
            "const toStringReplaced = Function.prototype.toString !== window.__p0t; " +
            "const sharedObject = w.Object === Object; " +
            "const childMask = typeof w.__nativeMask; " +
            "const childPatch = typeof w.__patchJournal; " +
            "const len = Object.keys.length; " +
            "return JSON.stringify([same, own[own.length - 1] === 'zzzChildVar', cloaked, sameToString, top, " +
            "replaced, p0, toStringReplaced, sharedObject, childMask, childPatch, len]); })()");

        _out.WriteLine("before = " + before + "  probe = " + probe + "  child = " + child);
        Assert.Equal("[true,true,\"b,a\"]", probe);

        using var doc = System.Text.Json.JsonDocument.Parse(child);
        var row = doc.RootElement;
        // [same, childOrdered, cloaked, sameToString, top, replaced, p0, toStringReplaced, ...]
        Assert.True(row[1].GetBoolean(), "the child's own window enumeration is not ordered");
        Assert.False(row[5].GetBoolean(), "a child-realm replay replaced the parent's Object.keys");
        Assert.Equal(3, row[6].GetInt32());   // the parent's wrapper is still cloaked
        Assert.True(row[8].GetBoolean() == false, "the child unexpectedly shares the parent's Object");
    }
}
