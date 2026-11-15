using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 175: a brand-check throw carries no frame from this script.
///
/// <code>
/// // A native IDL brand check throws from inside the engine, so the error's stack has no JS frame for the check at
/// // all: in JSC the top frame is the accessor itself, rendered 'get userAgent@[native code]', and the next frame is
/// // the caller. Ours is built in JS, so the stack carried the override's own frame — at this script's URL, with a
/// // line and column — and the Error wrapper's frame on top of it. Both are pure artifacts of this file.
/// </code>
///
/// <para>
/// The fix is <c>Error.captureStackTrace</c> taken <b>once</b>, at bootstrap — reading it at throw time would call
/// whatever the page installed on it, announcing every throw and handing the probe a live reference to the getter.
/// </para>
/// </summary>
public sealed class StackElisionTests
{
    private readonly ITestOutputHelper _out;

    public StackElisionTests(ITestOutputHelper output) => _out = output;

    /// <summary>The body captures the helper once and arms it before constructing the error.</summary>
    [Fact]
    public void TheHelperIsCapturedOnce()
    {
        var js = AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded);

        Assert.Contains("const nativeCapture = typeof Error.captureStackTrace === 'function'", js);
        Assert.Contains("ELIDE = [getter, '']", js);
        Assert.Contains("finally { ELIDE = null; }", js);
        Assert.Contains("throw new TypeError('The ' + label + '.' + name", js);

        // captured at bootstrap, not read at throw time
        var captureIndex = js.IndexOf("const nativeCapture", System.StringComparison.Ordinal);
        var throwIndex = js.IndexOf("throw new TypeError('The '", System.StringComparison.Ordinal);
        Assert.True(captureIndex >= 0 && captureIndex < throwIndex);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>Measured: the stack names the accessor as native and carries no frame of ours.</summary>
    [Fact]
    public async Task TheStackNamesAnAccessor()
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

        // R179 changed the shape as well as the format: JSC's `stack` carries FRAMES ONLY — the message lives on
        // e.message — so both are read here.
        var stack = await bridge.EvaluateAsync(
            "(() => { const d = Object.getOwnPropertyDescriptor(Navigator.prototype, 'platform'); " +
            "try { d.get.call({}); return 'no-throw'; } catch (e) { " +
            "return String(e.message) + ' || ' + String(e.stack); } })()");

        _out.WriteLine("stack = " + stack);

        // R176: WebKit's sentence, not Blink's, and NO invented frame — the capture says inventing one is a guess
        Assert.Contains("getter can only be used on instances of Navigator", stack!, System.StringComparison.Ordinal);
        Assert.DoesNotContain("(native)", stack, System.StringComparison.Ordinal);

        // R179 changed the FORMAT: JSC renders frames as `fn@url:line:col`, not `    at fn (url)`
        Assert.DoesNotContain("    at ", stack, System.StringComparison.Ordinal);

        // No frame of OURS: not the helper, and not the injected script's URL. The frame below the native one is the
        // CALLER — here that is the harness's own evaluate, which renders as `<anonymous>:` and is exactly what the
        // device shows for a page's own code, so it is not a tell and is not asserted against.
        Assert.DoesNotContain("at illegalInvocation", stack, System.StringComparison.Ordinal);
        Assert.DoesNotContain("blob:", stack, System.StringComparison.Ordinal);
        Assert.DoesNotContain("__nativeMask", stack, System.StringComparison.Ordinal);

        // and the native frame sits immediately under the message
        var parts = stack!.Split(" || ");
        Assert.Contains("getter can only be used on instances of Navigator", parts[0],
            System.StringComparison.Ordinal);

        // and the first frame names the accessor, in JSC's `name@location` form
        var firstFrame = parts[1].Split('\n')[0];
        Assert.Contains("get platform@", firstFrame, System.StringComparison.Ordinal);
    }

    /// <summary>And the value still answers for a real receiver.</summary>
    [Fact]
    public async Task ARealReceiverStillAnswers()
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

        Assert.Equal("\"iPhone\"", await bridge.EvaluateAsync("JSON.stringify(navigator.platform)"));
        Assert.Equal("\"Apple Computer, Inc.\"",
            await bridge.EvaluateAsync("JSON.stringify(navigator.vendor)"));
    }
}
