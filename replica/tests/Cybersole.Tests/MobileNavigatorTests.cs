using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 157: the phone's navigator and the one gate that makes it matter.
///
/// <para>
/// Two captures settle this round. <c>const NAV</c> is the iPhone profile the image installs —
/// iOS 27.0.1, four cores, five touch points, <c>webdriver</c> false, <c>cookieEnabled</c> true. And the
/// comment at 0x03d27ea7 records a wall gating its worker path on <c>'ontouchstart' in window</c>, paired
/// with the agent's shape. The replica installed a phone's screen and never a phone's touch surface, which is
/// the same class of miss as R151's viewport.
/// </para>
///
/// <para>
/// The negative half is worth as much: <c>history.length</c> is read by the payload and the pool contains no
/// <c>pushState</c> or <c>replaceState</c> at all, so the sample's 9 is the browser's own number and nothing
/// installs it.
/// </para>
/// </summary>
public sealed class MobileNavigatorTests
{
    private readonly ITestOutputHelper _out;

    public MobileNavigatorTests(ITestOutputHelper output) => _out = output;

    /// <summary>The captured navigator, verbatim.</summary>
    [Fact]
    public void TheCaptureIsRecorded()
    {
        Assert.Equal(5, MobileNavigator.MaxTouchPoints);
        Assert.Equal(4, MobileNavigator.HardwareConcurrency);
        Assert.Equal("27.0.1", MobileNavigator.IosVersion);

        // sixteen: the capture fixes all but userAgent (which is the agent the bridge sends) and languages
        Assert.Equal(16, MobileNavigator.Captured.Count);
        Assert.Equal("5", MobileNavigator.Captured["maxTouchPoints"]);
        Assert.Equal("false", MobileNavigator.Captured["standalone"]);
        Assert.Equal("true", MobileNavigator.Captured["cookieEnabled"]);

        _out.WriteLine(string.Join(", ", MobileNavigator.Captured.Select(kv => kv.Key + "=" + kv.Value)));
    }

    /// <summary>Five touch handlers, and the gate's own wording.</summary>
    [Fact]
    public void TheTouchGateIsRecorded()
    {
        Assert.Equal(5, MobileNavigator.TouchHandlers.Count);
        Assert.Contains("ontouchstart", MobileNavigator.TouchHandlers);

        Assert.Contains("aK_ = ('ontouchstart' in window)", MobileNavigator.HswGate);
        Assert.Contains("QW = nW || lK", MobileNavigator.HswGate);
        Assert.Equal("with aK_ false the gate opens", MobileNavigator.HswConsequence);

        _out.WriteLine(MobileNavigator.HswGate);
    }

    /// <summary>The body installs the counts and the handlers, and never throws.</summary>
    [Fact]
    public void TheBodyInstallsTouches()
    {
        var js = MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"]);

        // the body passes the count through a placeholder, so the literal to look for is the call's argument
        Assert.Contains("put('maxTouchPoints', " + MobileNavigator.MaxTouchPoints + ")", js);
        Assert.Contains("put('standalone', false)", js);
        Assert.Contains("put('vendor', 'Apple Computer, Inc.')", js);

        // appVersion is derived from the agent, not hard-coded
        Assert.Contains("ua.slice(8)", js);

        // R196: the five touch handlers moved to HandlerSurface, which installs them as ACCESSOR pairs — a null data
        // slot is "a shape no engine gives a handler" (hsw reads .value AND .get of each descriptor). This body keeps
        // only the navigator figures, and must not install a data slot behind the accessor layer's back.
        Assert.DoesNotContain("Object.defineProperty(G, name,", js);
        foreach (var handler in MobileNavigator.TouchHandlers)
        {
            Assert.Contains(handler, HandlerTable.HandlersJs);
            Assert.Contains(handler, HandlerTable.Touch);
        }

        Assert.DoesNotContain("throw ", js);
        Assert.Equal(js.Count(c => c == '{'), js.Count(c => c == '}'));
    }

    /// <summary>Only an Apple agent installs them.</summary>
    [Fact]
    public void OnlyAnAppleAgentGetsTouches()
    {
        Assert.True(MobileNavigator.ShouldInstallTouches(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15"));
        Assert.False(MobileNavigator.ShouldInstallTouches(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/157.0.0.0 Safari/537.36"));
        Assert.False(MobileNavigator.ShouldInstallTouches(null));
    }

    /// <summary>The gate is measured in a real browser: present for the phone, absent for the desktop.</summary>
    [Fact]
    public async Task TheGateAnswersDifferentlyForAPhoneAndADesktop()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";
        const string chrome = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                              "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36";

        await using (var bridge = await ChromiumBridge.LaunchAsync(userAgent: iphone))
        {
            await bridge.ApplyStealthAsync(iphone);
            await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

            var gate = await bridge.EvaluateAsync(
                "JSON.stringify([('ontouchstart' in window), navigator.maxTouchPoints," +
                " ('ontouchmove' in window)])");
            _out.WriteLine($"phone gate = {gate}");
            Assert.Equal("[true,5,true]", gate);
        }

        await using (var bridge = await ChromiumBridge.LaunchAsync(userAgent: chrome))
        {
            await bridge.ApplyStealthAsync(chrome);
            await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");

            var gate = await bridge.EvaluateAsync("String('ontouchstart' in window)");
            _out.WriteLine($"desktop gate = {gate}");
            Assert.Equal("false", gate);
        }
    }

    /// <summary>Nothing installs history.length, because the pool has no history writer at all.</summary>
    [Fact]
    public void HistoryLengthIsNeverWritten()
    {
        Assert.Equal("window.history.length", MobileNavigator.HistoryLength);

        var bodies = MobileSurface.BodyJs() + MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"]) + MobileSurface.EngineBodyJs();
        Assert.DoesNotContain("pushState", bodies);
        Assert.DoesNotContain("replaceState", bodies);
        Assert.DoesNotContain("history.length", bodies);

        _out.WriteLine("the sample's 9 is the browser's own number");
    }
}
