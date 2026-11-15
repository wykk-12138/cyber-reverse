using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 172: the cloak reformats rather than answering from a table.
///
/// <code>
/// const V8_NATIVE = /^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$/;
/// const V8_ACCESSOR = /^function (?:get|set) (?=[^\s(])/;
///
/// const real = nativeToString.call(this);
/// const match = V8_NATIVE.exec(real);
/// return match ? match[1].replace(V8_ACCESSOR, 'function ') + ' {\n    [native code]\n}' : real;
/// </code>
///
/// <para>
/// Two facts are in that snippet. V8 writes an accessor's role into its source — <c>function get userAgent() { … }</c> —
/// and the device does not, so the role word is dropped. And the device prints natives on <b>three lines</b>, where V8
/// prints one, so every native source is reformatted. A replica that answers a stored one-line string is V8-shaped, which
/// on an iOS profile is a tell in itself.
/// </para>
/// </summary>
public sealed class CloakRegexTests
{
    private readonly ITestOutputHelper _out;

    public CloakRegexTests(ITestOutputHelper output) => _out = output;

    /// <summary>The two patterns are the image's, and the text is three lines.</summary>
    [Fact]
    public void ThePatternsAreTheImages()
    {
        Assert.Equal(@"^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$", NativeMask.V8Native);
        Assert.Equal(@"^function (?:get|set) (?=[^\s(])", NativeMask.V8Accessor);

        var text = NativeMask.WebKitText("canShare");
        Assert.Equal("function canShare() {\n    [native code]\n}", text);
        Assert.Equal(3, text.Split('\n').Length);

        _out.WriteLine(text.Replace("\n", "\\n"));
    }

    /// <summary>The generated cloak carries both regexes and the reformatting.</summary>
    [Fact]
    public void TheCloakReformats()
    {
        var js = NativeMask.BodyJs();

        Assert.Contains("const V8_NATIVE = /^(function [^(]*\\(\\)|class [^ ]*) \\{ \\[native code\\] \\}$/;", js);
        Assert.Contains("const V8_ACCESSOR = /^function (?:get|set) (?=[^\\s(])/;", js);
        Assert.Contains("match[1].replace(V8_ACCESSOR, 'function ')", js);
        Assert.Contains("' {\\n    [native code]\\n}'", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>
    /// Measured: a patched method reports WebKit's three-line form, an untouched native is reformatted the same
    /// way, and a page's own function still prints its own source.
    /// </summary>
    [Fact]
    public async Task TheFormattingIsWebKits()
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

        // our own patch
        var patched = await bridge.EvaluateAsync(
            "JSON.stringify(Function.prototype.toString.call(navigator.canShare))");
        _out.WriteLine("patched = " + patched);
        Assert.Equal("\"function canShare() {\\n    [native code]\\n}\"", patched);

        // an untouched native, reformatted by the cloak
        var untouched = await bridge.EvaluateAsync(
            "JSON.stringify(Function.prototype.toString.call(Map))");
        _out.WriteLine("untouched = " + untouched);
        Assert.Contains("[native code]", untouched, System.StringComparison.Ordinal);
        Assert.Contains("\\n", untouched, System.StringComparison.Ordinal);

        // an accessor's role word is dropped
        var accessor = await bridge.EvaluateAsync(
            "JSON.stringify((() => { const d = Object.getOwnPropertyDescriptor(Navigator.prototype, " +
            "'userAgent'); return d && d.get ? Function.prototype.toString.call(d.get) : 'none'; })())");
        _out.WriteLine("accessor = " + accessor);
        Assert.DoesNotContain("get userAgent", accessor!, System.StringComparison.Ordinal);

        // and a page's own function is untouched
        var user = await bridge.EvaluateAsync(
            "Function.prototype.toString.call(function named(x) { return x + 1; })");
        Assert.Contains("return x + 1", user, System.StringComparison.Ordinal);

        // the override itself has no prototype, as the real one does not
        var proto = await bridge.EvaluateAsync(
            "String('prototype' in Function.prototype.toString)");
        Assert.Equal("false", proto);
    }
}
