using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Ask a real Chrome the questions a detector asks, and print the answers.
///
/// Rounds 136-138 fixed three things the source said were wrong. This is the other direction: it
/// launches the actual browser and reports what the session looks like from the inside, so the
/// next round of guesses is grounded in measurement rather than in reading.
///
/// Trait Speed=Slow: it starts a browser. Run with `dotnet test --filter Speed=Slow` or the
/// verifier's -Full switch.
/// </summary>
[Trait("Speed", "Slow")]
public class LiveBrowserProbeTests
{
    private readonly ITestOutputHelper _out;
    public LiveBrowserProbeTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task ProbeTheRealBrowserSurface()
    {
        if (ChromiumBridge.FindBrowser() is null)
        {
            _out.WriteLine("no browser on this machine — probe skipped");
            return;
        }

        // Round 142: this navigated to a data: URL, which is not a secure context, so a dozen
        // APIs reported absent for a reason that had nothing to do with the replica. Loopback is
        // a secure context, and is what a real https:// store looks like to these APIs.
        using var server = new LocalPageServer();
        await using var bridge = await ChromiumBridge.LaunchAsync();
        await bridge.ApplyStealthAsync();
        await bridge.NavigateAsync(server.Url);

        var probes = new (string Label, string Expression)[]
        {
            ("isSecureContext", "String(window.isSecureContext)"),
            ("UA", "navigator.userAgent"),
            ("uaData.fullVersion", "navigator.userAgentData ? navigator.userAgentData.fullVersion : 'absent'"),
            ("uaData.brands", "navigator.userAgentData ? JSON.stringify(navigator.userAgentData.brands) : 'absent'"),
            ("webdriver", "'webdriver' in navigator ? String(navigator.webdriver) : 'absent'"),
            ("ontouchstart in window", "'ontouchstart' in window"),
            ("ontouchstart shape", @"(() => {
                const d = Object.getOwnPropertyDescriptor(window, 'ontouchstart');
                if (!d) return 'no descriptor';
                const kinds = [];
                if ('value' in d) kinds.push('value=' + String(d.value));
                if (d.get) kinds.push('getter:' + d.get.name);
                if (d.set) kinds.push('setter:' + d.set.name);
                return kinds.join(' | ') || 'empty descriptor';
            })()"),
            ("getVoices length", "speechSynthesis.getVoices().length"),
            ("getVoices first", "speechSynthesis.getVoices().length ? speechSynthesis.getVoices()[0].name : 'none'"),
            ("plugins length", "navigator.plugins.length"),
            ("hardwareConcurrency", "String(navigator.hardwareConcurrency)"),
            ("document own props (first 8)",
                "Object.getOwnPropertyNames(document).slice(0, 8).join(',')"),
            ("document has featurePolicy",
                "'featurePolicy' in document ? 'present' : 'absent'"),
            ("document has browsingTopics",
                "'browsingTopics' in document ? 'present' : 'absent'"),
            ("navigator own props count", "String(Object.getOwnPropertyNames(Object.getPrototypeOf(navigator)).length)"),
            ("navigator has userAgentData",
                "'userAgentData' in navigator ? 'present' : 'absent'"),
            ("webkit in window", "'webkit' in window"),
            ("chrome in window", "'chrome' in window"),
            ("iframe navigator.webdriver",
                @"(() => {
                    const f = document.createElement('iframe');
                    document.body.appendChild(f);
                    const v = f.contentWindow.navigator;
                    const wd = 'webdriver' in v ? String(v.webdriver) : 'absent';
                    const voices = f.contentWindow.speechSynthesis
                        ? f.contentWindow.speechSynthesis.getVoices().length : -1;
                    return 'webdriver=' + wd + ' voices=' + voices;
                })()"),
        };

        var results = new Dictionary<string, string>();
        foreach (var (label, expression) in probes)
        {
            try
            {
                var value = await bridge.EvaluateAsync(expression);
                results[label] = value ?? "(null)";
            }
            catch (Exception ex)
            {
                results[label] = "ERROR: " + ex.Message;
            }
        }

        _out.WriteLine("=== live browser surface ===");
        foreach (var (label, value) in results)
            _out.WriteLine($"{label,-32} {value}");

        // The three properties rounds 136-138 changed must hold in a real session, not just in
        // the source. These are the assertions worth keeping.
        var ua = results.GetValueOrDefault("UA", "");
        var full = results.GetValueOrDefault("uaData.fullVersion", "");
        var brands = results.GetValueOrDefault("uaData.brands", "");
        var secure = results.GetValueOrDefault("isSecureContext", "false");

        _out.WriteLine("");
        _out.WriteLine("=== consistency ===");
        _out.WriteLine($"secure context: {secure}");
        _out.WriteLine($"UA token:       {Extract(ua, @"Chrome/([\d.]+)")}");
        _out.WriteLine($"fullVersion:    {full}");

        var uaToken = Extract(ua, @"Chrome/([\d.]+)");
        Assert.False(string.IsNullOrEmpty(uaToken), "UA has no Chrome token");

        // navigator.userAgentData only exists in a secure context. The probe now navigates to
        // loopback, so it does exist here — which is the point of reporting isSecureContext
        // alongside it.
        if (secure == "true")
        {
            var brandVersion = Extract(brands, @"""version"":""(\d+)""");
            Assert.Equal(uaToken!.Split('.')[0], brandVersion);

            // fullVersion is not settable through setUserAgentOverride on Chrome 157: the engine
            // downgrades fullVersionList to the major and getHighEntropyValues omits the field.
            // Round 141 measured that; asserting it here would just re-fail for a CDP reason.
            _out.WriteLine($"fullVersion from the default surface: {full} (CDP does not expose it)");
        }
        else
        {
            _out.WriteLine("not a secure context — userAgentData comparison skipped");
        }

        // browsingTopics and featurePolicy are both secure-context-gated, and both are the kind
        // of thing a fingerprint walks. Recorded because round 139 read them on a data: URL and
        // concluded browsingTopics was absent — it was, on that page.
        _out.WriteLine("");
        _out.WriteLine("=== secure-context-gated document members ===");
        foreach (var label in new[] { "document has featurePolicy", "document has browsingTopics" })
            _out.WriteLine($"{label,-32} {results.GetValueOrDefault(label, "?")}");

        // round 137: a headless Chrome reports zero voices, which alone rejects a session
        var voices = results.GetValueOrDefault("getVoices length", "0");
        _out.WriteLine($"voices: {voices}");
        Assert.NotEqual("0", voices);

        // round 136/137: the child realm must answer the same as the parent
        var child = results.GetValueOrDefault("iframe navigator.webdriver", "");
        _out.WriteLine($"iframe: {child}");
        Assert.DoesNotContain("webdriver=true", child);
        Assert.DoesNotContain("voices=0", child);

        // The probe measured these on a desktop with no touchscreen, so their absence is the
        // honest answer rather than a gap. Recorded here because the live build's HANDLERS table
        // exists for the opposite platform, and a future reader needs to know why the replica
        // does not carry it:
        //
        //   aK_ = ('ontouchstart' in window);  lK = uS && aK_ && <ua not Safari-shaped>
        //   — the gate that decides whether to spawn a worker, and it is iOS-shaped.
        _out.WriteLine("");
        _out.WriteLine("=== platform facts (not gaps) ===");
        _out.WriteLine($"ontouchstart in window: {results.GetValueOrDefault("ontouchstart in window", "?")}");
        _out.WriteLine($"ontouchstart descriptor: {results.GetValueOrDefault("ontouchstart shape", "?")}");
        _out.WriteLine($"webkit in window:       {results.GetValueOrDefault("webkit in window", "?")}");
        _out.WriteLine($"chrome in window:       {results.GetValueOrDefault("chrome in window", "?")}");
    }

    private static string? Extract(string text, string pattern)
    {
        var m = System.Text.RegularExpressions.Regex.Match(text, pattern);
        return m.Success ? m.Groups[1].Value : null;
    }
}
