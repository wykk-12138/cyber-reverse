using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 174: patches are recorded as paths and replayed into a child realm.
///
/// <para>
/// The image's reason is one sentence: <i>an iframe gets its own constructors, so a same-origin child is otherwise
/// completely unspoofed — read <c>iframe.contentWindow.navigator</c> and the real Blink values come straight back.</i>
/// </para>
///
/// <para>
/// The replica replayed by re-running the whole body with another realm; a journal records <b>which key on which
/// object</b> instead, and can name objects the body cannot reach generically — <c>Intl.DateTimeFormat.prototype</c>,
/// which needs a three-step path.
/// </para>
/// </summary>
public sealed class PatchJournalTests
{
    private readonly ITestOutputHelper _out;

    public PatchJournalTests(ITestOutputHelper output) => _out = output;

    /// <summary>The journal covers the installers, and records the Intl paths it cannot install.</summary>
    [Fact]
    public void TheEntriesCoverTheInstallers()
    {
        var entries = PatchJournal.Entries;

        // every guarded accessor, both locks members, audioSession and the Web Share pair
        foreach (var name in AccessorBrandCheck.Guarded) Assert.Contains(entries, e => e.Key == name);
        foreach (var name in NavigatorLocks.Installed) Assert.Contains(entries, e => e.Key == name);
        Assert.Contains(entries, e => e.Key == "audioSession");
        foreach (var (name, _) in ForwardingShims.WebShare) Assert.Contains(entries, e => e.Key == name);

        // and the Intl paths, which the body cannot reach generically
        Assert.Contains(entries, e => e.Path.SequenceEqual(new[] { "Intl", "DateTimeFormat", "prototype" }));
        Assert.Contains(entries, e => e.Path.SequenceEqual(new[] { "Intl", "NumberFormat", "prototype" }));

        _out.WriteLine($"{entries.Count} entries, {entries.Select(e => e.Path.Length).Distinct().Count()} path shapes");
    }

    /// <summary>The body carries pathOf, record, replay and the frame hook.</summary>
    [Fact]
    public void TheBodyCarriesTheMachinery()
    {
        var js = PatchJournal.BodyJs();

        Assert.Contains("const pathOf = (target) =>", js);
        Assert.Contains("const record = (target, key) =>", js);
        Assert.Contains("const replay = (realm) =>", js);
        Assert.Contains("G.__patchJournal =", js);
        Assert.Contains("MutationObserver", js);
        Assert.Contains("'Intl'", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }

    /// <summary>Measured: a same-origin iframe answers like its parent.</summary>
    [Fact]
    public async Task AChildRealmIsPatched()
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

        // The child document is created asynchronously, so the wait happens HERE and the read is synchronous: an
        // async IIFE returns a promise, and the bridge answers the promise object rather than its value (R167's trap).
        await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); f.id = 'probe'; " +
            "document.body.appendChild(f); return 'appended'; })()");

        for (var i = 0; i < 100; i++)
        {
            var ready = await bridge.EvaluateAsync(
                "(() => { const f = document.getElementById('probe'); " +
                "return String(!!(f && f.contentDocument && f.contentDocument.readyState === 'complete')); })()");
            if (ready == "true") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        // and the members live on `w.navigator`, not on `w` — the first version of this probe asked the wrong object
        var probe = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('probe').contentWindow; " +
            "return JSON.stringify([navigator.platform, w.navigator.platform, " +
            "navigator.maxTouchPoints, w.navigator.maxTouchPoints, " +
            "typeof w.navigator.canShare, " +
            "Function.prototype.toString.call(w.navigator.canShare).indexOf('[native code]') > 0]); })()");

        _out.WriteLine("child = " + probe);
        Assert.Contains("[\"iPhone\",\"iPhone\",5,5,\"function\",true]", probe!, System.StringComparison.Ordinal);
    }
}
