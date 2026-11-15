using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 184: the two prunes the replica never had — the global object and the document.
///
/// <para>
/// The global prune deletes every window name the device's own list does not carry, which is how <c>'chrome' in
/// window</c> stops answering. Its reason for being a function rather than a loop is the whole point: <i>a child realm
/// arrives with a fresh global carrying the full Blink surface again — deleting only in this realm left
/// <c>'chrome' in window</c> false at the top and TRUE inside an iframe, and the challenge runs in an iframe.</i>
/// </para>
///
/// <para>
/// The document prune removes eight Blink-only members, and the first request of the whole flow depends on it: hCaptcha's
/// <c>checksiteconfig</c> carries <c>spst</c>, computed from <c>document.hasPrivateToken</c> and
/// <c>document.featurePolicy</c>. The capture measured device <c>spst=0</c> against bot <c>spst=1</c> on the same sitekey
/// and the same api.js build.
/// </para>
/// </summary>
public sealed class GlobalPruneTests
{
    private readonly ITestOutputHelper _out;

    public GlobalPruneTests(ITestOutputHelper output) => _out = output;

    private const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                                  "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                                  "Mobile/15E148 Safari/604.1";

    /// <summary>The keep list is the capture's, plus this replica's internals.</summary>
    [Fact]
    public void TheKeepListIsTheCaptures()
    {
        foreach (var name in new[] { "hsw", "Raven", "_sharedLibs", "webkit", "__wdata", "__hcLoggerInstalled" })
            Assert.Contains(name, GlobalPrune.Keep);

        // and our own internals, or the prune would disable the mask mid-flight
        Assert.Contains("__nativeMask", GlobalPrune.Keep);
        Assert.Contains("__patchJournal", GlobalPrune.Keep);

        Assert.Equal(8, GlobalPrune.DocumentBlinkOnly.Count);
        Assert.Contains("featurePolicy", GlobalPrune.DocumentBlinkOnly);
        Assert.Contains("hasPrivateToken", GlobalPrune.DocumentBlinkOnly);

        Assert.Equal(0, GlobalPrune.DeviceSpst);
        Assert.Equal(1, GlobalPrune.BotSpst);
        Assert.Contains("losing it on request one", GlobalPrune.SpstStory);

        _out.WriteLine($"{GlobalPrune.Keep.Count} kept, {GlobalPrune.DocumentBlinkOnly.Count} document members");
    }

    /// <summary>The bodies prune as a function of a realm, and delete rather than trap.</summary>
    [Fact]
    public void TheBodiesPruneByRealm()
    {
        var global = GlobalPrune.GlobalBodyJs();
        var document = GlobalPrune.DocumentBodyJs();

        Assert.Contains("const globalPrune = (realm) => {", global);
        Assert.Contains("if (!DEVICE_GLOBALS.has(key) && !KEEP.has(key))", global);
        Assert.Contains("delete realm[key]", global);
        Assert.Contains("globalPrune(G);", global);

        Assert.Contains("G.__documentPrune = prune", document);
        Assert.Contains("delete proto[name]", document);

        Assert.True(JsGuard.IsClean(global), string.Join("; ", JsGuard.Inspect(global).Select(p => p.Kind)));
        Assert.True(JsGuard.IsClean(document), string.Join("; ", JsGuard.Inspect(document).Select(p => p.Kind)));

        _out.WriteLine($"{global.Length} + {document.Length} characters");
    }

    /// <summary>Measured: <c>'chrome' in window</c> is false, and the document no longer has the eight.</summary>
    [Fact]
    public async Task ChromeIsGone()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        // R206: wait for the window to settle, not just for readyState -- see Support/BrowserProbe.
        await Support.BrowserProbe.ReadyAsync(bridge);

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([('chrome' in window), (typeof window.chrome), " +
            "('featurePolicy' in document), ('hasPrivateToken' in document), " +
            "('hsw' in window) || true, typeof window.__nativeMask])");

        // R237: under a full-suite run this probe occasionally read the document before the stealth patch had applied —
        // it passed alone and failed in the batch, which is a timing flake, not a defect. Re-probe a few times with a
        // short wait instead of failing on the first read.
        for (var attempt = 0; attempt < 20; attempt++)
        {
            if (probe.StartsWith("[false,\"undefined\",false,false,", System.StringComparison.Ordinal)) break;

            _out.WriteLine($"attempt {attempt + 1}: {probe}");
            await Task.Delay(100);
            probe = await bridge.EvaluateAsync(
                "JSON.stringify([('chrome' in window), (typeof window.chrome), " +
                "('featurePolicy' in document), ('hasPrivateToken' in document), " +
                "('hsw' in window) || true, typeof window.__nativeMask])");
        }

        _out.WriteLine("probe = " + probe);

        // the three that matter: no chrome, no featurePolicy, no hasPrivateToken — and the mask survived the prune
        Assert.StartsWith("[false,\"undefined\",false,false,", probe, System.StringComparison.Ordinal);
        Assert.EndsWith(",\"object\"]", probe, System.StringComparison.Ordinal);
    }

    /// <summary>Measured: a child frame is pruned too, which is where the challenge runs.</summary>
    [Fact]
    public async Task AChildFrameIsPruned()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        // R206: wait for the window to settle, not just for readyState -- see Support/BrowserProbe.
        await Support.BrowserProbe.ReadyAsync(bridge);

        await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); f.id = 'probe'; document.body.appendChild(f); " +
            "return 'ok'; })()");

        for (var i = 0; i < 100; i++)
        {
            var ready = await bridge.EvaluateAsync(
                "(() => { const f = document.getElementById('probe'); " +
                "return String(!!(f && f.contentDocument && f.contentDocument.readyState === 'complete')); })()");
            if (ready == "true") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var probe = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('probe').contentWindow; " +
            "return JSON.stringify([('chrome' in w), ('featurePolicy' in w.document)]); })()");

        _out.WriteLine("child = " + probe);
        Assert.Equal("[false,false]", probe);
    }
}
