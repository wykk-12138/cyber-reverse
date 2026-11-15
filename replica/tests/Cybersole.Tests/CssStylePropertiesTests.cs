using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R189: the acceptance table from <c>docs\CSS_PROPERTIES_PLAN.md</c>, measured in a real Chromium.
/// </summary>
public sealed class CssStylePropertiesTests
{
    private readonly ITestOutputHelper _out;
    public CssStylePropertiesTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const el = document.body; el.style.color = 'rgb(255, 0, 0)'; const cs = getComputedStyle(el); " +
        "const proto = window.CSSStyleProperties && window.CSSStyleProperties.prototype; " +
        "const own = Object.getOwnPropertyNames(cs); " +
        "return JSON.stringify([" +
        "cs.constructor.name, " +
        "Object.prototype.toString.call(cs), " +
        "('appRegion' in cs), " +
        "cs.hasOwnProperty('appRegion'), " +
        "Object.getPrototypeOf(cs) === proto, " +
        "(cs instanceof CSSStyleDeclaration), " +
        "cs.getPropertyValue('color'), " +
        "proto ? Object.getOwnPropertyNames(proto).length : -1, " +
        "own.every((n) => /^[0-9]+$/.test(n)) ? 1 : 0, " +
        "Object.getOwnPropertyNames(CSSStyleDeclaration.prototype).length, " +
        "typeof window.CSSStyleProperties, " +
        "Function.prototype.toString.call(window.getComputedStyle).split('\\n').length]); })()";

    private static async Task<(string Patched, bool Ok)> MeasureAsync()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }
        var text = await bridge.EvaluateAsync(Probe);
        return (text ?? "", text is not null);
    }

    [Fact]
    public async Task TheComputedStyleIsACssStyleProperties()
    {
        var (probe, ok) = await MeasureAsync();
        _out.WriteLine("probe = " + probe);
        Assert.True(ok && probe.StartsWith('['), probe);

        using var doc = System.Text.Json.JsonDocument.Parse(probe);
        var r = doc.RootElement;

        // [constructor.name, toString tag, 'appRegion' in cs, hasOwnProperty, proto identity, instanceof,
        //  getPropertyValue, proto name count, numeric-only, CSD.prototype count, typeof, source lines]
        Assert.Equal("CSSStyleProperties", r[0].GetString());
        Assert.Equal("[object CSSStyleProperties]", r[1].GetString());

        // the two channels R188 could not fix
        Assert.False(r[2].GetBoolean(), "'appRegion' is still in the computed style");
        Assert.False(r[3].GetBoolean(), "hasOwnProperty('appRegion') is still true");

        Assert.True(r[4].GetBoolean(), "getPrototypeOf(cs) is not CSSStyleProperties.prototype");
        Assert.True(r[5].GetBoolean(), "cs is no longer an instance of CSSStyleDeclaration");

        // the declaration must still work
        Assert.Equal("rgb(255, 0, 0)", r[6].GetString());

        Assert.Equal(CssProperties.PropertyCount, r[7].GetInt32());
        Assert.Equal(1, r[8].GetInt32());
        Assert.Equal(11, r[9].GetInt32());
        Assert.Equal("function", r[10].GetString());
        Assert.Equal(3, r[11].GetInt32());
    }

    [Fact]
    public void TheVocabularyIsTheDevices()
    {
        Assert.Equal(1468, CssProperties.PropertyCount);
        Assert.StartsWith("[\"constructor\"", CssProperties.PropsJs.TrimStart());
        Assert.Contains("\"backgroundColor\"", CssProperties.PropsJs);
        Assert.Contains("\"webkitTransform\"", CssProperties.PropsJs);

        // a Blink-only name must NOT be in the device's vocabulary -- that is the whole point of the proxy
        Assert.DoesNotContain("\"appRegion\"", CssProperties.PropsJs);

        Assert.Equal("CSSStyleProperties", CssStyleProperties.InterfaceName);
        Assert.Equal("appRegion", CssStyleProperties.BlinkOnlyProbe);
        Assert.Contains("IDL named-property interceptor", CssStyleProperties.Rule);
    }
}
