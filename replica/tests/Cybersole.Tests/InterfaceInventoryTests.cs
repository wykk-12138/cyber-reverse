using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Inventory the browser's own interfaces, so "is this the right count?" has an answer.
///
/// Round 139 measured `Object.getOwnPropertyNames(Navigator.prototype).length === 36` and left the
/// question open: the live build's iOS capture has far fewer, but a Windows Chrome legitimately
/// has more. This dump settles it against the engine actually installed rather than against a
/// remembered number.
///
/// Trait Speed=Slow — it starts a browser.
/// </summary>
[Trait("Speed", "Slow")]
public class InterfaceInventoryTests
{
    private readonly ITestOutputHelper _out;
    public InterfaceInventoryTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task DumpTheInstalledInterfaces()
    {
        if (ChromiumBridge.FindBrowser() is null)
        {
            _out.WriteLine("no browser on this machine — inventory skipped");
            return;
        }

        // Round 140: this used to navigate to a data: URL, which is not a secure context, so
        // every API gated behind one reported absent — bluetooth, usb, hid, serial, mediaDevices,
        // clipboard, gpu, locks, storage, serviceWorker, userAgentData. That reads as twelve
        // missing features when it is one wrong page. 127.0.0.1 is a secure context, which is
        // what a real session sees on any https:// store.
        using var server = new LocalPageServer();
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync(server.Url);

        async Task<string> Ask(string expression)
        {
            try { return await bridge.EvaluateAsync(expression) ?? "(null)"; }
            catch (Exception ex) { return "ERROR: " + ex.Message; }
        }

        _out.WriteLine($"page: {server.Url}");
        _out.WriteLine($"isSecureContext: {await Ask("String(window.isSecureContext)")}");

        // the four surfaces an anti-bot script walks, in the order it walks them
        var surfaces = new (string Name, string Expression)[]
        {
            ("Navigator.prototype", "Object.getOwnPropertyNames(Navigator.prototype)"),
            ("Document.prototype", "Object.getOwnPropertyNames(Document.prototype)"),
            ("Screen.prototype", "Object.getOwnPropertyNames(Screen.prototype)"),
            ("WebGLRenderingContext.prototype",
                "Object.getOwnPropertyNames(WebGLRenderingContext.prototype)"),
        };

        foreach (var (name, expression) in surfaces)
        {
            var json = await Ask($"JSON.stringify({expression})");
            if (json.StartsWith("ERROR") || json == "(null)")
            {
                _out.WriteLine($"{name}: {json}");
                continue;
            }

            var props = JsonSerializer.Deserialize<List<string>>(json) ?? new List<string>();
            _out.WriteLine("");
            _out.WriteLine($"=== {name} — {props.Count} own properties ===");
            foreach (var chunk in props.Chunk(6))
                _out.WriteLine("  " + string.Join(" ", chunk.Select(p => p.PadRight(14))));
        }

        // the counts that matter for the comparison in round 139
        _out.WriteLine("");
        _out.WriteLine("=== counts ===");
        foreach (var (label, expression) in new (string, string)[]
        {
            ("Navigator.prototype", "Object.getOwnPropertyNames(Navigator.prototype).length"),
            ("Document.prototype", "Object.getOwnPropertyNames(Document.prototype).length"),
            ("window own", "Object.getOwnPropertyNames(window).length"),
            ("window enumerable", "Object.keys(window).length"),
            ("document own", "Object.getOwnPropertyNames(document).length"),
            ("navigator own (instance)", "Object.getOwnPropertyNames(navigator).length"),
        })
        {
            _out.WriteLine($"{label,-28} {await Ask(expression)}");
        }

        // the properties WebKit never shipped, which the live build deletes on iOS but a Windows
        // Chrome must keep — this is the check that says the replica is right not to prune
        _out.WriteLine("");
        _out.WriteLine("=== Blink-only navigator members (must be present on Windows) ===");
        foreach (var member in new[]
        {
            "userAgentData", "connection", "bluetooth", "usb", "hid", "serial", "xr",
            "deviceMemory", "getBattery", "mediaDevices", "clipboard", "gpu", "locks",
            "storage", "wakeLock", "presentation", "scheduling", "serviceWorker",
        })
        {
            var present = await Ask($"String('{member}' in navigator)");
            _out.WriteLine($"{member,-16} {present}");
        }

        // the reverse: members WebKit has that Blink must not claim
        _out.WriteLine("");
        _out.WriteLine("=== WebKit-only navigator members (must be absent on Windows) ===");
        foreach (var member in new[] { "standalone", "audioSession" })
        {
            var present = await Ask($"String('{member}' in navigator)");
            _out.WriteLine($"{member,-16} {present}");
            Assert.Equal("false", present);
        }

        // --- the assertions worth keeping ------------------------------------------------
        // A secure context is what any real session sees on an https:// store, so these are the
        // numbers that describe the product. Asserting them means a future ApplyStealthAsync edit
        // that deletes a Blink member — copying the live build's iOS prune wholesale, say — is
        // caught here instead of on a live drop.
        Assert.Equal("true", await Ask("String(window.isSecureContext)"));

        var blinkOnly = new[]
        {
            "userAgentData", "connection", "bluetooth", "usb", "hid", "serial", "xr",
            "deviceMemory", "getBattery", "mediaDevices", "clipboard", "gpu", "locks",
            "storage", "wakeLock", "presentation", "scheduling", "serviceWorker",
        };
        foreach (var member in blinkOnly)
            Assert.Equal("true", await Ask($"String('{member}' in navigator)"));

        // Blink's surface is far larger than WebKit's; a Windows Chrome below 60 members would
        // mean half of it went missing
        var navigatorCount = int.Parse(await Ask("String(Object.getOwnPropertyNames(Navigator.prototype).length)"));
        _out.WriteLine("");
        _out.WriteLine($"Navigator.prototype on a secure context: {navigatorCount}");
        Assert.True(navigatorCount >= 60,
            $"only {navigatorCount} members — a Windows Chrome exposes ~71, so something is deleting them");

        // the UA and userAgentData must agree here, where userAgentData actually exists.
        //
        // fullVersion is NOT a property of userAgentData — only brands, mobile and platform are.
        // The exact build comes from getHighEntropyValues(), which returns a promise, so the
        // evaluation has to await it. Round 138 wrote fullVersion into the override and this is
        // where that value would become readable; asking for it as a plain property returns
        // undefined on any Chrome, which is what the first attempt measured.
        //
        // fullVersion is also NOT returned by getHighEntropyValues on this build even when the
        // override supplies a four-part fullVersionList — the engine downgrades every entry to
        // the major. So the assertions below cover what the override can actually control:
        //
        //   brands[].version  ← settable, and the part a detector compares against the UA
        //   fullVersion       ← not settable through CDP on this build
        //
        // Recording the limit rather than asserting it away: the day a build does return
        // fullVersion, this test prints it and the comment above is what needs revising.
        var uaToken = await Ask("navigator.userAgent.match(/Chrome\\/([\\d.]+)/)[1]");
        var brand = await Ask(
            "navigator.userAgentData.brands.find(b => b.brand === 'Google Chrome').version");
        var entropy = await bridge.EvaluateAsync(
            "navigator.userAgentData.getHighEntropyValues(['fullVersion']).then(v => JSON.stringify(v))",
            awaitPromise: true) ?? "(null)";
        var fullVersion = await bridge.EvaluateAsync(
            "navigator.userAgentData.getHighEntropyValues(['fullVersion']).then(v => v.fullVersion || '(absent)')",
            awaitPromise: true) ?? "(null)";

        _out.WriteLine("");
        _out.WriteLine("UA token      " + uaToken);
        _out.WriteLine("brand version " + brand);
        _out.WriteLine("fullVersion   " + fullVersion);
        _out.WriteLine("entropy all   " + entropy);

        // the reduced UA token must be <major>.0.0.0
        Assert.Equal(uaToken!.Split('.')[0] + ".0.0.0", uaToken);
        // and userAgentData must report the same major
        Assert.Equal(uaToken.Split('.')[0], brand);

        if (fullVersion == "(absent)")
            _out.WriteLine("CDP limitation: setUserAgentOverride.fullVersionList is downgraded to the major on this build");
        else
            Assert.Equal(uaToken.Split('.')[0], fullVersion.Split('.')[0]);
    }
}
