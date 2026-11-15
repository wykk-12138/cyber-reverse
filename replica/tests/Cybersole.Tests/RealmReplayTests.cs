using System.Reflection;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The stealth script must patch every realm, not just the top window.
///
/// Round 136: the live build records each patch as a realm-independent path and replays it into
/// child frames, with this reason in its own comment —
///
///   "An iframe gets its own constructors, so a same-origin child is otherwise completely
///    unspoofed — read iframe.contentWindow.navigator and the real Blink values come straight
///    back."
///
/// The replica's script used bare `navigator` / `window` throughout, which makes realm replay
/// impossible in principle: the same code cannot be pointed at a different global. These tests
/// hold the rewrite in place.
/// </summary>
public class RealmReplayTests
{
    private readonly ITestOutputHelper _out;
    public RealmReplayTests(ITestOutputHelper output) => _out = output;

    private static readonly Lazy<string> Script = new(() =>
    {
        var type = typeof(Cybersole.Stores.Scripts.ChromiumBridge);
        var field = type.GetField("StealthScript",
            BindingFlags.NonPublic | BindingFlags.Static);
        Assert.NotNull(field);
        return (string)field!.GetRawConstantValue()!;
    });

    [Fact]
    public void ScriptPatchesAFreshRealmThroughAParameter()
    {
        var script = Script.Value;

        // the patch body must be a function of the global, not statements against the current one
        Assert.Contains("const apply = (W) =>", script);
        Assert.Contains("replay(globalThis)", script);

        _out.WriteLine($"{script.Length} chars");
        _out.WriteLine("has apply(W): " + script.Contains("const apply = (W) =>"));
    }

    [Fact]
    public void NoPatchReadsABareNavigatorOrWindow()
    {
        var script = Script.Value;

        // strip the comments before looking, since they legitimately mention both words
        var code = Regex.Replace(script, @"//[^\n]*", "");
        code = Regex.Replace(code, @"/\*.*?\*/", "", RegexOptions.Singleline);

        // `navigator` / `window` may appear only as property reads on the realm object (W.navigator)
        // or inside string literals; a bare identifier would bind to the top window.
        var bareNavigator = Regex.Matches(code, @"(?<![.\w'""])navigator\b");
        var bareWindow = Regex.Matches(code, @"(?<![.\w'""])window\b");

        _out.WriteLine($"bare 'navigator' references: {bareNavigator.Count}");
        _out.WriteLine($"bare 'window' references:    {bareWindow.Count}");
        foreach (Match m in bareWindow.Take(3))
        {
            var line = code[Math.Max(0, m.Index - 40)..Math.Min(code.Length, m.Index + 40)];
            _out.WriteLine("  ..." + line.Replace("\n", " ") + "...");
        }

        // `W.Notification` is fine; `window.Notification` would not be
        Assert.Empty(bareNavigator);
        Assert.Empty(bareWindow);
    }

    [Fact]
    public void BothIframeRoutesAreHooked()
    {
        var script = Script.Value;

        // Round 143: these assertions used to check that a name appeared somewhere, and a name
        // appears in two places here — the assignment and the saved original. Mutating the saved
        // original to null left every assertion green while the hook was dead. Each check below
        // now pins the exact statement that does the work, not the word it contains.
        Assert.Contains("const createElement = Document.prototype.createElement;", script);
        Assert.Contains("Document.prototype.createElement = function (tag)", script);
        Assert.Contains("const descriptor = Object.getOwnPropertyDescriptor(proto, 'contentWindow');", script);
        Assert.Contains("Object.defineProperty(proto, 'contentWindow', {", script);
        Assert.Contains("el.addEventListener('load', () => replay(el.contentWindow));", script);

        _out.WriteLine("createElement: saves the original, then replaces it");
        _out.WriteLine("contentWindow: reads the descriptor, then replaces the getter");
    }

    [Fact]
    public void RealmSetIsAWeakSetBecauseAGlobalCanBeReplaced()
    {
        var script = Script.Value;

        // a flag on the window would survive navigation, and a navigated frame has a new global
        // that still needs patching
        Assert.Contains("new WeakSet()", script);
        Assert.Contains("PATCHED.has(win)", script);
        Assert.Contains("PATCHED.add(win)", script);

        _out.WriteLine("uses WeakSet: " + script.Contains("new WeakSet()"));
    }

    [Fact]
    public void EveryPatchSurvivesAMissingApiInTheChildRealm()
    {
        var script = Script.Value;

        // a child frame can be sandboxed, or be about:blank, and then WebGLRenderingContext or
        // Notification is simply absent; an unguarded reference would abort the whole replay and
        // leave the realm half-patched, which is worse than unpatched
        Assert.Contains("const N = W.navigator;", script);
        Assert.Contains("if (!N) return;", script);
        Assert.Contains("W.Notification ?", script);
        Assert.Contains("if (ctx && ctx.prototype)", script);

        var guards = Regex.Matches(script, @"try \{").Count;
        _out.WriteLine($"try blocks: {guards}");
        Assert.True(guards >= 8, $"only {guards} try blocks — each patch needs its own");
    }

    [Fact]
    public void TheOriginalPatchesAreAllStillThere()
    {
        var script = Script.Value;

        string[] markers =
        {
            "'webdriver'",              // 1
            "W.chrome",                 // 2
                        "'languages'",              // 3
            "permissions.query",        // 4
            "getParameter",             // 5
            "'hardwareConcurrency'",    // 6
            "'outerWidth'",             // 7
        };

        foreach (var marker in markers)
        {
            Assert.Contains(marker, script);
            _out.WriteLine($"present: {marker}");
        }
    }

    [Fact]
    public void SpeechSynthesisReturnsAVoiceList()
    {
        var script = Script.Value;

        // a headless Chrome reports zero voices, and `getVoices().length === 0` on its own is
        // enough to reject a session — no real browser on any platform ships an empty list
        Assert.Contains("getVoices", script);
        Assert.Contains("voices.slice()", script);

        // R199: the list is the device's 68 Apple voices, substituted from VoiceTable at assembly time — the six
        // Windows/Google entries that used to live inline were a louder tell than no list at all. The template carries
        // a PLACEHOLDER, so this test checks the shape and VoiceListTests checks the answer in a real browser.
        Assert.Contains("__VOICES__", script);
        Assert.True(Cybersole.Stores.Scripts.VoiceTable.Count >= 60,
            $"only {Cybersole.Stores.Scripts.VoiceTable.Count} voices in the table");
        Assert.Contains("voiceURI", Cybersole.Stores.Scripts.VoiceTable.VoicesJs);
        Assert.DoesNotContain("Microsoft David", script);

        // the patch must land on the prototype when it exists, and on the instance otherwise;
        // Chrome exposes it on SpeechSynthesis.prototype and a page may read either
        Assert.Contains("W.SpeechSynthesis.prototype", script);
        Assert.Contains(": W.speechSynthesis", script);
    }

    [Fact]
    public void SrcLessIframesArePatchedWithoutWaitingForLoad()
    {
        var script = Script.Value;

        // "a frame created with createElement/appendChild never navigates, so there is no
        //  document-start for the host to hook"
        // — an about:blank frame never fires load, so a load-only hook misses the common case
        var createHook = script[script.IndexOf("Document.prototype.createElement", StringComparison.Ordinal)..];
        createHook = createHook[..Math.Min(700, createHook.Length)];

        Assert.Contains("replay(el.contentWindow)", createHook);
        _out.WriteLine("replay at creation: " + createHook.Contains("replay(el.contentWindow)"));

        // the getter hook remains the one that covers a frame that already exists
        Assert.Contains("Object.getOwnPropertyDescriptor(proto, 'contentWindow')", script);
    }
}
