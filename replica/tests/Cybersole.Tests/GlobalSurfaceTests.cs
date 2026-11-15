using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R193: the device-only globals. The measurement that matters is the phantom count — names the enumeration
/// advertises and the window does not actually carry.
/// </summary>
public sealed class GlobalSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public GlobalSurfaceTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private static async Task<string?> ProbeAsync(string js)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        // R206: readyState alone was not enough -- Chromium puts `chrome` back after the prune, and how late depends on
        // load. Wait for the name count to stop moving before measuring.
        await Support.BrowserProbe.ReadyAsync(bridge);
        // R304: the count can be stable while the set is not, so settle on the names themselves before measuring.
        await Support.BrowserProbe.SettleNamesAsync(bridge);
        return await bridge.EvaluateAsync(js);
    }

    [Fact]
    public async Task NoNameIsAdvertisedWithoutAProperty()
    {
        // R206: the probe now returns the NAMES, not just a count. The count alone said "1062 expected, 1063
        // measured" under load and nothing else, which is not enough to act on — this lists the extra ones.
        var probe = await ProbeAsync(
            "(() => { const names = Object.getOwnPropertyNames(window); " +
            "const phantom = names.filter((n) => !(n in window)); " +
            "const noDescriptor = names.filter((n) => Object.getOwnPropertyDescriptor(window, n) === undefined); " +
            "return JSON.stringify([names, phantom, noDescriptor]); })()");

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        var names = r[0].EnumerateArray().Select(e => e.GetString()!).ToList();
        var phantom = r[1].EnumerateArray().Select(e => e.GetString()!).ToList();
        var noDescriptor = r[2].EnumerateArray().Select(e => e.GetString()!).ToList();

        var expected = WindowNameTable.All.ToHashSet(System.StringComparer.Ordinal);
        var extra = names.Where(n => !expected.Contains(n)).ToList();
        var missing = expected.Where(n => !names.Contains(n, System.StringComparer.Ordinal)).ToList();

        _out.WriteLine($"own names = {names.Count}, expected = {WindowNameTable.AllCount}");
        _out.WriteLine("extra  = " + string.Join(", ", extra));
        _out.WriteLine("missing= " + string.Join(", ", missing));

        Assert.True(extra.Count == 0 && missing.Count == 0,
            $"window names differ from the table (+{extra.Count} / -{missing.Count}): "
            + "extra[" + string.Join(",", extra) + "] missing[" + string.Join(",", missing) + "]");

        Assert.Equal(0, phantom.Count);      // every advertised name is actually in the window
        Assert.Equal(0, noDescriptor.Count); // and has a descriptor
    }

    [Fact]
    public async Task TheInjectedNamesAnswerLikeTheDevice()
    {
        var probe = await ProbeAsync(
            "(() => { const d = Object.getOwnPropertyDescriptor(window, 'webkit'); " +
            "return JSON.stringify([" +
            "('webkit' in window), typeof window.webkit, " +
            "d ? (('get' in d) ? 'accessor' : 'data') : 'none', " +
            "window.webkit ? Object.prototype.toString.call(window.webkit) : 'nil', " +
            "window.webkit && window.webkit.constructor ? window.webkit.constructor.name : 'nil', " +
            "('openDatabase' in window), typeof window.openDatabase, " +
            "('_injected_clipboard' in window), typeof window._injected_clipboard, " +
            "typeof window.CSS, typeof window.CSS.supports]); })()");

        _out.WriteLine("injected = " + probe);
        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        Assert.True(r[0].GetBoolean(), "'webkit' is not in the window");
        Assert.Equal("object", r[1].GetString());
        // a DATA property, or hsw's sweep keeps it and it never appears in the suspicious-globals list
        Assert.Equal("data", r[2].GetString());
        Assert.Equal("[object WebKitNamespace]", r[3].GetString());
        Assert.Equal("WebKitNamespace", r[4].GetString());

        // the "u" row: present, but typeof undefined, exactly like the device
        Assert.True(r[5].GetBoolean(), "'openDatabase' is not in the window");
        Assert.Equal("undefined", r[6].GetString());

        // the "b" rows are booleans on the device
        Assert.True(r[7].GetBoolean(), "'_injected_clipboard' is not in the window");
        Assert.Equal("boolean", r[8].GetString());

        // and a platform object exists without its constructor being exposed under the interface name
        Assert.Equal("object", r[9].GetString());
        Assert.Equal("function", r[10].GetString());
    }

    [Fact]
    public async Task ThePhantomNamesAreOnesBlinkNeverHad()
    {
        const string js =
            "JSON.stringify([('oncopy' in window), typeof window.oncopy, ('ongesturestart' in window), " +
            "('onpaste' in window), typeof window.onpaste])";

        await using var raw = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await raw.NavigateAsync("data:text/html,<html><body>x</body></html>");
        var before = await raw.EvaluateAsync(js);

        var after = await ProbeAsync(js);

        _out.WriteLine("raw     = " + before);
        _out.WriteLine("patched = " + after);
        Assert.False(string.IsNullOrWhiteSpace(before));
        Assert.False(string.IsNullOrWhiteSpace(after));
    }

    [Fact]
    public void TheTablesAreVerbatim()
    {
        Assert.Equal(67, GlobalSurfaceTable.KindCount);
        Assert.Equal(219, GlobalSurfaceTable.NotFunctionCount);
        Assert.Contains("\"gcrweb\"", GlobalSurfaceTable.KindsJs);
        Assert.Contains("\"openDatabase\": \"u\"", GlobalSurfaceTable.KindsJs);
        Assert.Contains("_injected_clipboard\": \"b\"", GlobalSurfaceTable.KindsJs);
        Assert.Contains("\"Atomics\"", GlobalSurfaceTable.NotFunctionJs);
        Assert.Equal("['webkit']", GlobalSurfaceTable.InjectedGlobalsJs.Trim());
    }
}
