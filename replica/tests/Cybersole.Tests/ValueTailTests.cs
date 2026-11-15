using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 177: the tail of <c>value()</c>, and the two shapes beside it that had never been read.
///
/// <code>
/// Object.defineProperty(target, name, {
///   get: getter,
///   configurable: true,
///   enumerable: enumerable !== false,
/// });
/// record(target, name);
/// </code>
///
/// <para>
/// The interesting part is one expression: <c>enumerable !== false</c> — true by default, false where a call site says
/// so. The replica wrote <c>true</c> unconditionally, which is right for every member this workspace installs and wrong
/// as a shape.
/// </para>
///
/// <para>
/// The other two shapes in the same block are <c>method()</c> — a replacement whose arity comes from the <b>original</b>,
/// handed to the builder as its first argument — and <c>reseat()</c>, which R165 implemented and which matches the
/// capture line for line.
/// </para>
/// </summary>
public sealed class ValueTailTests
{
    private readonly ITestOutputHelper _out;

    public ValueTailTests(ITestOutputHelper output) => _out = output;

    /// <summary>The descriptor is the image's expression, not a constant.</summary>
    [Fact]
    public void TheDescriptorFollowsTheExpression()
    {
        var js = AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded);

        Assert.Contains("enumerable: !MUST_HIDE.has(name)", js);
        Assert.Contains("const MUST_HIDE = new Set([])", js);
        Assert.DoesNotContain("enumerable: true });", js, System.StringComparison.Ordinal);

        Assert.Contains("enumerable: enumerable !== false", AccessorBrandCheck.ValueTail);
        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The other two shapes are recorded with what makes them shapes.</summary>
    [Fact]
    public void TheNeighbouringShapesAreRecorded()
    {
        Assert.Contains("ORIGINAL", AccessorBrandCheck.MethodShape);
        Assert.Contains("first argument", AccessorBrandCheck.MethodShape);

        Assert.Contains("carried across untouched", AccessorBrandCheck.ReseatShape);
        Assert.Contains("non-configurable", AccessorBrandCheck.ReseatShape);
        Assert.Contains("relative order at the end", AccessorBrandCheck.ReseatShape);

        _out.WriteLine(AccessorBrandCheck.ValueTail);
        _out.WriteLine(AccessorBrandCheck.MethodShape);
        _out.WriteLine(AccessorBrandCheck.ReseatShape);
    }

    /// <summary>Measured: the members are enumerable, so for-in sees them, as the device's list does.</summary>
    [Fact]
    public async Task TheInstalledAccessorsAreEnumerable()
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

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify(['platform','userAgent','vendor','appVersion'].map((n) => { " +
            "const d = Object.getOwnPropertyDescriptor(Navigator.prototype, n); " +
            "return [n, !!d.get, d.enumerable, d.configurable, 'value' in d]; }))");

        _out.WriteLine("descriptors = " + probe);

        // accessor, enumerable, configurable, no value — for all four
        Assert.Equal(
            "[[\"platform\",true,true,true,false],[\"userAgent\",true,true,true,false]," +
            "[\"vendor\",true,true,true,false],[\"appVersion\",true,true,true,false]]",
            probe);

        // and for-in sees them, which is the reason the expression defaults to true
        var forIn = await bridge.EvaluateAsync(
            "(() => { const k = []; for (const n in navigator) k.push(n); " +
            "return String(k.indexOf('platform') >= 0); })()");
        Assert.Equal("true", forIn);
    }
}
