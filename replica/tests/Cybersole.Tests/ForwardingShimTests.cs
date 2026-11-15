using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 170: the credentials question closes — not with a virtual authenticator, but with a forwarder.
///
/// <para>
/// The image's note says Chrome for iOS hides WebKit's <c>CredentialsContainer</c>, and its own passkey script puts a
/// plain object of four script functions on the navigator <b>instance</b>, non-enumerable. Two consequences follow and the
/// replica had both wrong: <c>for (k in navigator)</c> skips an own non-enumerable property (the device sends 32 keys,
/// an engine with a stray <c>credentials: {}</c> sends 33), and the value prints script source rather than
/// <c>[native code]</c>.
/// </para>
///
/// <para>
/// So the original does not implement WebAuthn at all — it forwards to whatever container the engine has and cloaks the
/// source. Smaller and more faithful than an authenticator, which is what this round builds.
/// </para>
/// </summary>
public sealed class ForwardingShimTests
{
    private readonly ITestOutputHelper _out;

    public ForwardingShimTests(ITestOutputHelper output) => _out = output;

    /// <summary>The credentials shim is an own non-enumerable property that forwards.</summary>
    [Fact]
    public void TheCredentialsShimForwards()
    {
        var js = ForwardingShims.CredentialsBodyJs();

        Assert.Contains("Object.prototype.hasOwnProperty.call(nav, 'credentials')", js);
        Assert.Contains("target.apply(native, arguments)", js);
        Assert.Contains("Object.defineProperty(nav, 'credentials', { value: shim });", js);

        // the descriptor deliberately omits writable/configurable/enumerable — the defaults are false
        Assert.DoesNotContain("Object.defineProperty(nav, 'credentials',\n                     { value: shim, writable", js);

        Assert.Equal(4, ForwardingShims.Credentials.Count);
        Assert.Equal(new[] { "get", "create", "preventSilentAccess", "store" },
            ForwardingShims.Credentials.Select(c => c.Name));

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The Web Share pair are data properties with the arities the capture lists.</summary>
    [Fact]
    public void TheWebSharePairAreDataProperties()
    {
        var js = ForwardingShims.WebShareBodyJs();

        Assert.Contains("[['canShare', 1], ['share', 1]]", js);
        Assert.Contains("{ value: fn, writable: true, configurable: true, enumerable: true }", js);
        Assert.Contains("NotAllowedError", js);
        Assert.Contains(ForwardingShims.ShareRejection, js);

        Assert.Equal(2, ForwardingShims.WebShare.Count);
        Assert.Equal((1, 1), (ForwardingShims.WebShare[0].Length, ForwardingShims.WebShare[1].Length));

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The key counts and the reason are recorded.</summary>
    [Fact]
    public void TheKeyCountsAreRecorded()
    {
        Assert.Equal(32, ForwardingShims.DeviceForInKeys);
        Assert.Contains("32 keys, not 33", ForwardingShims.OwnPropertyReason);
        Assert.Contains("for-in skips it", ForwardingShims.OwnPropertyReason);

        _out.WriteLine(ForwardingShims.OwnPropertyReason);
    }

    /// <summary>Measured: credentials is an own property, skipped by for-in, and its methods look native.</summary>
    [Fact]
    public async Task TheCredentialsShimIsSkippedByForIn()
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
            "JSON.stringify((() => { const d = Object.getOwnPropertyDescriptor(navigator, 'credentials'); " +
            "const keys = []; for (const k in navigator) keys.push(k); " +
            "return [!!d, d ? d.enumerable : null, d ? d.writable : null, d ? d.configurable : null, " +
            "keys.indexOf('credentials'), typeof navigator.credentials.get, " +
            "navigator.credentials.get.length, " +
            "Function.prototype.toString.call(navigator.credentials.get)]; })())");

        _out.WriteLine("probe = " + probe);

        // own, non-enumerable, non-writable, non-configurable; for-in does not see it; the method looks native
        Assert.StartsWith("[true,false,false,false,-1,\"function\",1,", probe, System.StringComparison.Ordinal);
        Assert.Contains("[native code]", probe, System.StringComparison.Ordinal);

        // and the prototype still carries the member, as the device's does
        var onProto = await bridge.EvaluateAsync(
            "String('credentials' in Object.getPrototypeOf(navigator))");
        Assert.Equal("true", onProto);
    }

    /// <summary>Measured: canShare answers, share rejects with WebKit's message.</summary>
    [Fact]
    public async Task TheWebSharePairAnswers()
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
            "JSON.stringify([typeof navigator.canShare, navigator.canShare.length, " +
            "navigator.canShare({ title: 'x' }), navigator.canShare({}), navigator.share.length, " +
            "Function.prototype.toString.call(navigator.canShare)])");

        _out.WriteLine("share = " + probe);
        Assert.StartsWith("[\"function\",1,true,false,1,", probe, System.StringComparison.Ordinal);
        Assert.Contains("[native code]", probe, System.StringComparison.Ordinal);
    }
}
