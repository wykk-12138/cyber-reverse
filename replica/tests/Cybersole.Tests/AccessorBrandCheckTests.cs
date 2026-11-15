using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 173: a native accessor throws for a foreign receiver, and a data property does not.
///
/// <code>
/// // A native accessor is bound to its interface and throws when handed a foreign receiver. A getter that just
/// // closes over a constant answers anyone, and that difference needs no reference device to see: pull the
/// // descriptor off Navigator.prototype, call .get on {}, and a real browser throws where a naive override
/// // returns the user agent.
/// </code>
///
/// <para>
/// The replica's members were data properties, so <c>.get.call({})</c> answered the value — a one-line rejection no
/// reference device is needed for. This round installs the four most-probed strings as guarded accessors instead.
/// </para>
///
/// <para>
/// The second mechanism recorded here is the replay path: <c>pathOf</c> maps a patched object back to
/// <c>['Navigator','prototype']</c> or <c>['Intl','DateTimeFormat','prototype']</c> so a child realm can be patched by
/// resolving the path there, over the <c>KNOWN</c> list of constructors that can appear in one.
/// </para>
/// </summary>
public sealed class AccessorBrandCheckTests
{
    private readonly ITestOutputHelper _out;

    public AccessorBrandCheckTests(ITestOutputHelper output) => _out = output;

    /// <summary>The recorded tables are the image's.</summary>
    [Fact]
    public void TheTablesAreTheImages()
    {
        Assert.Equal(23, AccessorBrandCheck.Known.Count);
        Assert.Contains("Navigator", AccessorBrandCheck.Known);
        Assert.Contains("speechSynthesis", AccessorBrandCheck.Known);
        Assert.Contains("HTMLIFrameElement", AccessorBrandCheck.Known);

        // Intl needs a three-step path, so it has its own list
        Assert.Equal(9, AccessorBrandCheck.IntlNames.Count);
        Assert.Contains("DateTimeFormat", AccessorBrandCheck.IntlNames);

        Assert.Equal(new[] { "userAgent", "platform", "vendor", "appVersion" }, AccessorBrandCheck.Guarded);
    }

    /// <summary>The body guards a foreign receiver and installs an accessor.</summary>
    [Fact]
    public void TheBodyGuardsTheReceiver()
    {
        var js = AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded);

        // realm-independent, and captured from the TARGET rather than hard-coded (R176): `instanceof` is realm-scoped,
        // so `this instanceof Navigator` is false for a perfectly good navigator inside an iframe
        Assert.Contains("Object.prototype.toString.call(this) !== brand", js);
        Assert.Contains("brand = Object.prototype.toString.call(target)", js);
        // R176: WebKit's sentence, with the label taken from the target rather than hard-coded
        Assert.Contains("+ ' getter can only be used on instances of ' + label", js);
        Assert.DoesNotContain("'Illegal invocation'", js);
        // R176 renamed the local: the getter is built by `install()` and installed by name
        // R177: `enumerable !== false`, not a constant
        Assert.Contains("enumerable: !MUST_HIDE.has(name)", js);
        Assert.Contains("'get ' + name", js);

        // a getter shorthand, taken through its descriptor so reading it does not call it
        Assert.Contains("get x() {", js);
        Assert.Contains("Object.getOwnPropertyDescriptor({", js);
        Assert.Contains("}, 'x').get;", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>Measured: the values still answer, and a foreign receiver now throws.</summary>
    [Fact]
    public async Task AForeignReceiverThrows()
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

        var values = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.platform, navigator.vendor, navigator.appVersion.slice(0, 7), " +
            "typeof navigator.userAgent])");
        _out.WriteLine("values = " + values);
        Assert.Equal("[\"iPhone\",\"Apple Computer, Inc.\",\"5.0 (iP\",\"string\"]", values);

        var foreign = await bridge.EvaluateAsync(
            "JSON.stringify(['platform','userAgent'].map((n) => { " +
            "const d = Object.getOwnPropertyDescriptor(Navigator.prototype, n); " +
            "try { d.get.call({}); return n + ':answered'; } " +
            "catch (e) { return n + ':' + e.name; } }))");
        _out.WriteLine("foreign = " + foreign);
        Assert.Equal("[\"platform:TypeError\",\"userAgent:TypeError\"]", foreign);

        // and the getter still looks like an accessor
        var shape = await bridge.EvaluateAsync(
            "JSON.stringify((() => { const d = Object.getOwnPropertyDescriptor(Navigator.prototype, 'platform'); " +
            "return [d.get.name, d.get.length, 'prototype' in d.get, " +
            "Function.prototype.toString.call(d.get)]; })())");
        _out.WriteLine("shape = " + shape);
        Assert.Contains("\"get platform\",0,false", shape, System.StringComparison.Ordinal);
    }
}
