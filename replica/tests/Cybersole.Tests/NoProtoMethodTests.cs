using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 171: the shims have no <c>prototype</c>, because they are built from method shorthands.
///
/// <para>
/// The image's helper block is three lines and one piece of syntax:
/// </para>
///
/// <code>
/// const renamed = (fn, name) => { try { Object.defineProperty(fn, 'name', { value: name || '', configurable: true }); }
///   catch (e) { } return fn; };
/// const noProtoMethod = (impl, name) => renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
/// const noProtoGetter = (impl, name) => renamed(Object.getOwnPropertyDescriptor(
///   { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');
/// </code>
///
/// <para>
/// <c>({ m() {} }).m</c> is an ordinary function expression in every respect except that it has <b>no</b>
/// <c>prototype</c> property — which is exactly what a WebIDL operation looks like. A plain
/// <c>function () {}</c> has one, and a detector can read it.
/// </para>
/// </summary>
public sealed class NoProtoMethodTests
{
    private readonly ITestOutputHelper _out;

    public NoProtoMethodTests(ITestOutputHelper output) => _out = output;

    /// <summary>The mask exports the three builders, written the image's way.</summary>
    [Fact]
    public void TheBuildersAreTheImages()
    {
        var js = NativeMask.BodyJs();

        Assert.Contains("const renamed = (fn, name) =>", js);
        Assert.Contains("({ m() { return impl.apply(this, arguments); } }).m", js);
        Assert.Contains("{ get m() { return impl.call(this); } }", js);
        Assert.Contains("renamed, method: noProtoMethod, getter: noProtoGetter", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The share shim is built through the helper, not as a plain function.</summary>
    [Fact]
    public void TheShareShimIsBuiltThroughIt()
    {
        var js = ForwardingShims.WebShareBodyJs();

        Assert.Contains("G.__nativeMask.method", js);
        Assert.Contains("}, name);", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine("canShare and share are built without a prototype");
    }

    /// <summary>Measured: no prototype, the right name, the right arity, native-looking source.</summary>
    [Fact]
    public async Task TheShimsHaveNoPrototype()
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
            "JSON.stringify(['canShare','share'].map((n) => { const fn = navigator[n]; " +
            "return [n, typeof fn, 'prototype' in fn, fn.prototype === undefined, fn.name, fn.length]; }))");

        _out.WriteLine("probe = " + probe);

        Assert.Equal(
            "[[\"canShare\",\"function\",false,true,\"canShare\",1]," +
            "[\"share\",\"function\",false,true,\"share\",1]]",
            probe);

        // and the credentials methods are plain functions on purpose — the image says so
        var credentials = await bridge.EvaluateAsync(
            "String('prototype' in navigator.credentials.get)");
        _out.WriteLine("credentials.get has prototype = " + credentials);
        Assert.Equal("true", credentials);
    }
}
