using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 176: the accessor's wording, its brand check, and its stack — three things this workspace had slightly wrong.
///
/// <code>
/// // The message follows WebKit's wording rather than Blink's "Illegal invocation", since WebKit is the engine being
/// // presented.
/// throw new TypeError('The ' + label + '.' + name + ' getter can only be used on instances of ' + label);
///
/// // The brand is checked with Object.prototype.toString, NOT instanceof. Child realms are patched by copying this
/// // descriptor into them, so the closure keeps the PARENT's constructor, and instanceof is realm-scoped.
///
/// // Armed with an EMPTY head on purpose. Eliding our own frames is measured and safe; the native frame a real engine
/// // would show here is not — WebKit adds no JS frame for an IDL brand check at all.
/// ELIDE = [getter, ''];
/// </code>
/// </summary>
public sealed class AccessorWordingTests
{
    private readonly ITestOutputHelper _out;

    public AccessorWordingTests(ITestOutputHelper output) => _out = output;

    /// <summary>The message is WebKit's, built from the target's own label.</summary>
    [Fact]
    public void TheMessageIsWebKits()
    {
        Assert.Equal("The Navigator.platform getter can only be used on instances of Navigator",
            AccessorBrandCheck.MessageFor("Navigator", "platform"));
        Assert.Equal("The Screen.width getter can only be used on instances of Screen",
            AccessorBrandCheck.MessageFor("Screen", "width"));

        var js = AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded);
        Assert.Contains("+ ' getter can only be used on instances of ' + label", js);

        // Blink's wording must not appear as a THROWN message. The comment above the code names Blink's phrasing on
        // purpose — that is the sentence this file exists to not produce — so the assertion looks for the quote form.
        Assert.DoesNotContain("'Illegal invocation'", js, System.StringComparison.Ordinal);
    }

    /// <summary>The brand is captured from the target at install time, and the stack is elided without invention.</summary>
    [Fact]
    public void TheBrandIsCapturedAndTheStackIsNotInvented()
    {
        var js = AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded);

        Assert.Contains("brand = Object.prototype.toString.call(target)", js);
        Assert.Contains("Object.prototype.toString.call(this) !== brand", js);
        Assert.DoesNotContain("instanceof G.Navigator", js, System.StringComparison.Ordinal);

        // armed with an EMPTY head, cleared in a finally
        Assert.Contains("ELIDE = [getter, '']", js);
        Assert.Contains("finally { ELIDE = null; }", js);

        // and no invented native frame
        Assert.DoesNotContain("(native)'", js, System.StringComparison.Ordinal);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }

    /// <summary>Measured: the message, the throw, and a stack with no frame of ours and no invented one.</summary>
    [Fact]
    public async Task TheThrowSaysWhatWebKitSays()
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

        var report = await bridge.EvaluateAsync(
            "(() => { const d = Object.getOwnPropertyDescriptor(Navigator.prototype, 'platform'); " +
            "try { d.get.call({}); return 'no-throw'; } catch (e) { " +
            "return JSON.stringify([e.name, e.message, String(e.stack).split('\\n')[0], " +
            "String(e.stack).indexOf('(native)'), String(e.stack).indexOf('illegalInvocation')]); } })()");

        _out.WriteLine("report = " + report);

        // the name, the WebKit sentence, and a stack whose first line is the message
        Assert.StartsWith("[\"TypeError\",\"The Navigator.platform getter can only be used on instances of Navigator\",",
            report, System.StringComparison.Ordinal);

        // no invented native frame (-1), and no frame of the helper (-1)
        Assert.EndsWith(",-1,-1]", report, System.StringComparison.Ordinal);

        // a real receiver still answers
        Assert.Equal("\"iPhone\"", await bridge.EvaluateAsync("JSON.stringify(navigator.platform)"));
    }
}
