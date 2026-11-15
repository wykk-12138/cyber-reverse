using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 158, the slow half: every generated body is handed to a real JavaScript parser.
///
/// <para>
/// <c>new Function('G', body)</c> compiles the body without running it, which is exactly the check that was
/// missing three times. A static guard can spot a doubled escape or an extra brace; only a parser can say whether
/// the result is a program. Both halves exist because they fail differently: the static one runs in milliseconds and
/// catches the shapes already known, and this one catches what nobody has written a rule for yet.
/// </para>
/// </summary>
[Trait("Speed", "Slow")]
public class JsParseTests
{
    private readonly ITestOutputHelper _out;

    public JsParseTests(ITestOutputHelper output) => _out = output;

    /// <summary>Each body compiles, and a deliberately broken one does not.</summary>
    [Fact]
    public async Task EveryBodyParses()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

        foreach (var (name, body) in JsGuard.AllBodies())
        {
            var result = await CompileAsync(bridge, body);
            _out.WriteLine($"{name,-22} {result}");

            Assert.Equal("ok", result);
        }

        // the control: the shape R157 produced must be refused, or this test proves nothing
        var broken = await CompileAsync(bridge, "  try {\n    x();\n  } catch (e) {}\n  ['a']\n    .forEach(y);} ");
        Assert.StartsWith("SyntaxError", broken, System.StringComparison.Ordinal);
        _out.WriteLine("control  " + broken);
    }

    /// <summary>And the composed surface the bridge actually installs parses too.</summary>
    [Fact]
    public async Task TheComposedSurfaceParses()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";

        var composed = "const applySurface = (realm) => {\n  const G = realm;\n" +
                       MobileSurface.EngineBodyJs() +
                       WebAssemblySurface.BodyJs() +
                       MobileSurface.BodyJs() +
                       MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"]) +
                       "\n}; applySurface(window);";

        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

        var result = await CompileAsync(bridge, composed);
        _out.WriteLine("composed = " + result);
        Assert.Equal("ok", result);

        // and the real thing reaches the page: the phone's touch surface is there
        await bridge.ApplyStealthAsync(iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        Assert.Equal("5", await bridge.EvaluateAsync("String(navigator.maxTouchPoints)"));
    }

    /// <summary>Compile without executing, and report the parser's verdict.</summary>
    private static async Task<string> CompileAsync(ChromiumBridge bridge, string body)
    {
        var expression =
            "(function () { try { new Function('G', " + Quote(body) + "); return 'ok'; }" +
            " catch (e) { return e.name + ': ' + e.message; } })()";

        return await bridge.EvaluateAsync(expression) ?? "(null)";
    }

    /// <summary>A JSON string literal is a valid JS string literal for these bodies.</summary>
    private static string Quote(string text) =>
        Newtonsoft.Json.JsonConvert.ToString(text);
}
