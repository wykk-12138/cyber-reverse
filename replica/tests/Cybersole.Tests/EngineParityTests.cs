using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 179: the engine-parity layer — V8's words replaced by JavaScriptCore's.
///
/// <code>
/// const MESSAGES = {
///   "nullProp": "null is not an object (evaluating 'null.x')",
///   "notFunction": "(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
///   "badArrayLength": "Array length must be a positive integer of safe magnitude.",
///   "jsonCircular": "JSON.stringify cannot serialize cyclic structures."
/// };
/// </code>
///
/// <para>
/// Five patches follow: the four messages, the stack format (<c>at fn (url)</c> → <c>fn@url</c>), the <c>stack</c>
/// descriptor (V8 installs an accessor, JSC a writable data property), <c>Error.stackTraceLimit</c> (10 → 100), and the
/// bound-function naming V8 adds and JSC does not.
/// </para>
/// </summary>
public sealed class EngineParityTests
{
    private readonly ITestOutputHelper _out;

    public EngineParityTests(ITestOutputHelper output) => _out = output;

    /// <summary>The four messages are verbatim, and the frame regex is the capture's.</summary>
    [Fact]
    public void TheMessagesAreVerbatim()
    {
        Assert.Equal("null is not an object (evaluating 'null.x')", EngineParity.Messages["nullProp"]);
        Assert.Equal("(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
            EngineParity.Messages["notFunction"]);
        Assert.Equal("Array length must be a positive integer of safe magnitude.",
            EngineParity.Messages["badArrayLength"]);
        Assert.Equal("JSON.stringify cannot serialize cyclic structures.", EngineParity.Messages["jsonCircular"]);

        Assert.Equal(@"^\s*at (?:(.+?) \()?(.+?)\)?$", EngineParity.V8Frame);
        Assert.Equal(7, EngineParity.Wrapped.Count);
        Assert.Equal(10, EngineParity.V8StackTraceLimit);
        Assert.Equal(100, EngineParity.DeviceStackTraceLimit);

        var js = EngineParity.BodyJs();
        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }

    /// <summary>The body carries all five patches.</summary>
    [Fact]
    public void TheBodyCarriesTheFivePatches()
    {
        var js = EngineParity.BodyJs();

        Assert.Contains("const toJscStack = (raw) =>", js);
        Assert.Contains("Error.stackTraceLimit = 100", js);
        Assert.Contains("Function.prototype.bind = bound", js);
        Assert.Contains("G.Array = ArrayWrapped", js);
        Assert.Contains("JSON.stringify = wrapped", js);
        Assert.Contains("Object.defineProperty(error, 'stack', {", js);
        Assert.Contains("head ? (body ? head +", js);
        Assert.Contains("writable: true, configurable: true, enumerable: false", js);

        // The reason prepareStackTrace is not used lives in the C# documentation, not in the generated code — the
        // body must NOT assign it, because doing so makes `typeof Error.prepareStackTrace` report 'function'.
        Assert.DoesNotContain("prepareStackTrace =", js, System.StringComparison.Ordinal);

        // and the trade-off is stated where the next reader will find it: in the class documentation
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "EngineParity.cs"));
        Assert.Contains("prepareStackTrace", source);
    }

    /// <summary>Measured: V8's wording and format are gone from a constructed error.</summary>
    [Fact]
    public async Task AConstructedErrorSpeaksJsc()
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

        // the stack format
        var stack = await bridge.EvaluateAsync(
            "(() => { function outer() { return new Error('x'); } const e = outer(); " +
            "return JSON.stringify([String(e.stack).split('\\n').slice(1, 3), " +
            "Object.getOwnPropertyDescriptor(e, 'stack') ? " +
            "!!Object.getOwnPropertyDescriptor(e, 'stack').get : null]); })()");
        _out.WriteLine("stack = " + stack);
        Assert.Contains("@", stack!, System.StringComparison.Ordinal);
        Assert.DoesNotContain("    at ", stack, System.StringComparison.Ordinal);
        Assert.EndsWith(",false]", stack, System.StringComparison.Ordinal);   // data property, not an accessor

        // the limit
        Assert.Equal("100", await bridge.EvaluateAsync("String(Error.stackTraceLimit)"));

        // prepareStackTrace must stay undefined
        Assert.Equal("undefined", await bridge.EvaluateAsync("typeof Error.prepareStackTrace"));

        // the Array length sentence
        var arrayMessage = await bridge.EvaluateAsync(
            "(() => { try { new Array(-1); return 'no-throw'; } catch (e) { return e.name + ': ' + e.message; } })()");
        _out.WriteLine("array = " + arrayMessage);
        Assert.Equal("RangeError: Array length must be a positive integer of safe magnitude.", arrayMessage);

        // the cyclic JSON sentence
        var jsonMessage = await bridge.EvaluateAsync(
            "(() => { const a = {}; a.self = a; try { JSON.stringify(a); return 'no-throw'; } " +
            "catch (e) { return e.name + ': ' + e.message; } })()");
        _out.WriteLine("json = " + jsonMessage);
        Assert.Equal("TypeError: JSON.stringify cannot serialize cyclic structures.", jsonMessage);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
