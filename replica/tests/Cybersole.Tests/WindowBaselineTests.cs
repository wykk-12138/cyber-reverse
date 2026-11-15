using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 181: what the recorded window list proves, and the baseline mechanism that keeps it honest.
///
/// <para>
/// The top-level list has <b>1290</b> names, and eleven of them are Chrome-for-iOS's own injected hooks —
/// <c>_injected_clipboard</c>, <c>_injected_passkey_controller</c>, <c>__gCrWeb</c> and the rest. A desktop Chromium with a
/// rewritten navigator has none of them, which is a device-specific tell no navigator value can offset.
/// </para>
///
/// <para>
/// The list cannot be a constant either: <c>api.js</c> sends <c>Object.keys(window).sort().join(',')</c> to the wasm as
/// <c>wdata</c> and the proof grows with it, so the answer has to be the <b>live</b> key list with a baseline taken on the
/// last line of the file.
/// </para>
/// </summary>
public sealed class WindowBaselineTests
{
    private readonly ITestOutputHelper _out;

    public WindowBaselineTests(ITestOutputHelper output) => _out = output;

    /// <summary>Twelve injected names, two of them main-frame-only, against a recorded 1062.</summary>
    [Fact]
    public void TheRecordedListIsCounted()
    {
        // R183 corrected this: the list is 1062, and 1290 was a regex artefact
        Assert.Equal(1062, WindowBaseline.RecordedNameCount);
        Assert.Equal(228, WindowBaseline.RecordedEnumCount);
        Assert.Equal(12, WindowBaseline.InjectedCount);

        Assert.Contains("__gCrWeb", WindowBaseline.InjectedNames);
        Assert.Contains("gcrweb", WindowBaseline.InjectedNames);
        Assert.Contains("_injected_passkey_controller", WindowBaseline.InjectedNames);

        // ten of the twelve are `_injected_*`, the other two are the gcrweb pair
        Assert.Equal(10, WindowBaseline.InjectedNames.Count(n => n.StartsWith("_injected_", System.StringComparison.Ordinal)));

        // and the two a frame must not advertise are among them
        Assert.All(WindowBaseline.MainFrameOnly, n => Assert.Contains(n, WindowBaseline.InjectedNames));

        _out.WriteLine($"{WindowBaseline.InjectedCount} injected names of {WindowBaseline.RecordedNameCount}");
    }

    /// <summary>The mechanism: FRAMED by identity, a live baseline, the two names dropped from frames.</summary>
    [Fact]
    public void TheBaselineIsLive()
    {
        var js = WindowBaseline.BodyJs();

        Assert.Contains("G.top !== G", js);
        Assert.Contains("G.__windowBaseline = { framed: FRAMED", js);
        Assert.Contains("const INJECTED = [", js);

        // R193: this body no longer CREATES the twelve injected names — it used to define all of them as `{}`, and the
        // device says ten are booleans. GlobalSurfaceTable owns the kinds now.
        Assert.DoesNotContain("value: {}", js);

        Assert.Contains("LIVE key list", WindowBaseline.Rule);
        Assert.Contains("wdata", WindowBaseline.Rule);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters; gap: {WindowBaseline.Gap}");
    }
}
