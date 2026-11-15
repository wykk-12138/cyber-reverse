using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 164: two details the capture states in code rather than prose.
///
/// <code>
/// Object.keys(NAV).forEach((key) => value(Navigator.prototype, key, NAV[key]));
/// value(Navigator.prototype, 'languages', Object.freeze([NAV.language]));
/// </code>
///
/// <para>
/// The first line says <b>where</b>: the prototype, not the instance. A detector can read
/// <c>Object.getOwnPropertyNames(navigator)</c> and see whether the properties are its own. The second says
/// <b>how many</b>: one language, frozen — a phone that reports a single element where a desktop reports two is a
/// coherent phone, and a phone reporting <c>["nl-NL","en-US"]</c> is a desktop wearing a phone's user agent.
/// </para>
/// </summary>
public sealed class NavigatorPlacementTests
{
    private readonly ITestOutputHelper _out;

    public NavigatorPlacementTests(ITestOutputHelper output) => _out = output;

    /// <summary>The body targets the prototype and freezes a single-element language list.</summary>
    [Fact]
    public void TheBodyUsesThePrototype()
    {
        var js = MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"]);

        Assert.Contains("Object.getPrototypeOf(N)", js);

        // R164: the first attempt defined on the prototype only, and a defineProperty that the browser accepts
        // and then overrides left `platform` at Win32. The body now tries both targets and verifies by reading
        // back through the instance, which is the only test that cannot be fooled.
        Assert.Contains("const targets = [P, N];", js);
        Assert.Contains("if (N[name] === v) return;", js);
        Assert.Contains("Object.freeze(['nl-NL'])", js);
        Assert.Contains("writable: false", js);

        // one element, not two: the literal must not carry a second language
        Assert.DoesNotContain("'en-US'", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The captured language is the one installed.</summary>
    [Fact]
    public void TheLanguageIsTheCaptures()
    {
        Assert.Equal("nl-NL", MobileNavigator.Captured["language"]);

        var js = MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"]);
        Assert.Contains("put('language', 'nl-NL')", js);
    }

    /// <summary>The nine members the capture installs are all still installed.</summary>
    [Fact]
    public void TheMembersAreStillAllThere()
    {
        var js = MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"]);

        foreach (var name in new[]
                 {
                     "maxTouchPoints", "standalone", "cookieEnabled", "appCodeName", "appName",
                     "platform", "product", "productSub", "vendor", "vendorSub", "onLine",
                     "pdfViewerEnabled", "language", "appVersion",
                 })
        {
            Assert.Contains("put('" + name + "'", js);
        }

        _out.WriteLine("fourteen members, one languages list, one appVersion derived from the agent");
    }

    /// <summary>Measured: navigator.languages is exactly one element.</summary>
    [Fact]
    public async Task TheLanguagesListHasOneElement()
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

        // One expression, no embedded newlines: an escaped newline inside a C# string becomes a real
        // newline in the JavaScript, and a newline inside a quoted literal is a SyntaxError.
        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.language, navigator.languages.length, " +
            "navigator.languages.join('" + "|" + "'), Object.isFrozen(navigator.languages), " +
            "navigator.platform, navigator.vendor, navigator.productSub])");

        _out.WriteLine("probe = " + probe);

        Assert.Equal("[\"nl-NL\",1,\"nl-NL\",true,\"iPhone\",\"Apple Computer, Inc.\",\"20030107\"]", probe);
    }
}
