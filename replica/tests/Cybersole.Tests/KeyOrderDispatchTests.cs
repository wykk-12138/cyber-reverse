using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R188: the key-order dispatch is measured against the raw engine, not asserted from the source. Every number below
/// is what Chromium answered with the script applied and what it answers without it.
/// </summary>
public sealed class KeyOrderDispatchTests
{
    private readonly ITestOutputHelper _out;
    public KeyOrderDispatchTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const cs = getComputedStyle(document.body); " +
        "const proto = Object.getOwnPropertyNames(CSSStyleDeclaration.prototype); " +
        "const inst = Object.getOwnPropertyNames(cs); " +
        "const allIndex = inst.every((n) => /^[0-9]+$/.test(n)); " +
        "const instKeys = Object.keys(cs); " +
        "const loc = Object.getOwnPropertyNames(document.location); " +
        "const op = Object.getOwnPropertyNames(Object.prototype); " +
        "const plain = Object.getOwnPropertyNames({ b: 1, a: 2 }).join(','); " +
        "return JSON.stringify([proto.length, inst.length, instKeys.length, allIndex, loc.slice(0, 4).join('|'), " +
        "op.slice(0, 3).join('|'), plain]); })()";

    private static async Task<string> MeasureAsync(bool stealth)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        if (stealth) await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }
        return await bridge.EvaluateAsync(Probe);
    }

    [Fact]
    public async Task TheDispatchChangesWhatTheBrowserAnswers()
    {
        var raw = await MeasureAsync(stealth: false);
        var patched = await MeasureAsync(stealth: true);

        _out.WriteLine("raw     = " + raw);
        _out.WriteLine("patched = " + patched);

        using var rawDoc = System.Text.Json.JsonDocument.Parse(raw);
        using var patchedDoc = System.Text.Json.JsonDocument.Parse(patched);
        var r = rawDoc.RootElement;
        var p = patchedDoc.RootElement;

        // [proto.length, inst.length, instKeys.length, allIndex, loc4, op3, plain]
        // the engine's own answers, for the record
        Assert.Equal(10, r[0].GetInt32());
        Assert.False(r[3].GetBoolean());          // a raw computed style is not numeric-only

        // CSSStyleDeclaration.prototype now answers the device's eleven names (CSS_DECL, 0x03d15574)
        Assert.Equal(11, p[0].GetInt32());

        // the instance answers its numeric indices alone -- "no engine enumerates a property twice"
        Assert.True(p[3].GetBoolean());
        Assert.True(p[1].GetInt32() < r[1].GetInt32(), $"instance went {r[1]} -> {p[1]}");

        // location and Object.prototype follow their ORDER rules
        Assert.Equal("href|protocol|host|hostname", p[4].GetString());
        Assert.Equal("toString|toLocaleString|valueOf", p[5].GetString());

        // the dispatch must not touch an ordinary object
        Assert.Equal("b,a", p[6].GetString());
    }

    [Fact]
    public void TheTablesAreVerbatim()
    {
        // 17.7 KB of rules and no placeholder left behind (the tables legitimately contain `__proto__`)
        Assert.True(KeyOrderRules.OrderRulesJs.Length > 17_000);
        Assert.DoesNotContain("__RULES__", KeyOrderRules.OrderRulesJs);
        Assert.DoesNotContain("__CSS__", KeyOrderRules.CssDeclarationJs);

        var lines = KeyOrderRules.OrderRulesJs.Split('\n');
        Assert.Equal(KeyOrderRules.RuleCount, lines.Length);
        foreach (var line in lines) Assert.Contains("match:", line, System.StringComparison.Ordinal);
    }

    /// <summary>Which branch answers a computed style, and what it hands back.</summary>
    [Fact]
    public async Task TheComputedStyleInstanceIsDiagnosed()
    {
        var probe =
            "(() => { const cs = getComputedStyle(document.body); " +
            "const own = Object.getOwnPropertyNames(cs); " +
            "return JSON.stringify([cs instanceof CSSStyleDeclaration, own.length, own.slice(0, 4).join('|'), " +
            "Object.keys(cs).length, Object.getOwnPropertyNames(CSSStyleDeclaration.prototype).length]); })()";

        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }

        var raw = await bridge.EvaluateAsync(probe);
        _out.WriteLine("instance = " + raw);
        Assert.False(string.IsNullOrWhiteSpace(raw));
    }
}
