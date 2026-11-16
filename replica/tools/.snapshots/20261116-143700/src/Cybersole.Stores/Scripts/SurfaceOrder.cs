using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The composition order, as a contract instead of a thing to rediscover each round (R168).
///
/// <para>
/// Three separate rounds were spent learning that position is semantics:
/// </para>
///
/// <list type="number">
/// <item>R161: the mask pass has to run <b>last</b>, or the getters it masks have not been installed yet.</item>
/// <item>R156: an engine block running before the older navigator patch lost its five plugins to three.</item>
/// <item>R167: installing <c>locks</c> after the reseat appended it to the end of the prototype and broke the
/// recorded order — 29/50 with the order <c>False</c> instead of true.</item>
/// </list>
///
/// <para>
/// The order below is what the bridge does, written down so a new body spliced in the wrong place fails a test instead
/// of a runtime measurement. Each row carries the reason it cannot move.
/// </para>
/// </summary>
public static class SurfaceOrder
{
    /// <summary>One step of the composition.</summary>
    public sealed record Step(int Position, string Name, string Marker, string Why);

    /// <summary>The order, first to last.</summary>
    public static readonly IReadOnlyList<Step> Steps = new[]
    {
        new Step(1, "capture", "NativeRefs.BodyJs()",
            "first: every enumerating pass below reads the reference taken here, before anything is replaced"),

        new Step(2, "mask", "NativeMask.BodyJs()",
            "before every patch after it: each one registers itself as native"),

        new Step(3, "parity", "EngineParity.BodyJs()",
            "before every other patch: the error wrappers are what a brand check's ELIDE hook talks to"),

        new Step(4, "engine", "MobileSurface.EngineBodyJs()",
            "unconditional: it is what a real Chromium reports, so it is true for every profile"),

        new Step(5, "webassembly", "WebAssemblySurface.BodyJs()",
            "gated on an Apple claim: the counts are Blink's own numbers"),

        new Step(6, "mobile", "MobileSurface.BodyJs()",
            "gated on an Apple claim: the figures describe a 402x874 phone"),

        new Step(7, "touches", "MobileNavigator.BodyJs(userAgent)",
            "after the mobile figures, because it installs on the same prototype"),

        new Step(8, "prune", "NavPrune.BodyJs()",
            "after the engine block, because it deletes members the engine block installed"),

        new Step(9, "locks", "NavigatorLocks.BodyJs()",
            "before the reseat, because every install appends to the prototype"),

        new Step(10, "reseat", "NavOrder.ReseatBodyJs(NavOrder.Navigator)",
            "after every install, because a reseat orders what already exists"),

        new Step(11, "window-names", "WindowBaseline.BodyJs()",
            "after every other install: it adds globals, and the baseline it reports is taken once the script is done"),

        new Step(12, "window-order", "WindowOrder.BodyJs()",
            "before the key-order wrap: the wrap calls the function this installs, and the baseline it takes"),

        new Step(13, "window-order-wrap", "WindowOrderWrap.BodyJs()",
            "above the prunes, as in the target (0x03d1efd4 before 0x03d272d4): safe only because they hold a "
            + "captured enumerator"),

        new Step(14, "global-prune", "GlobalPrune.GlobalBodyJs()",
            "after every install: it deletes what the device's list does not carry, so it must run last of the adders"),

        new Step(15, "document-prune", "GlobalPrune.DocumentBodyJs()",
            "with the global prune: hCaptcha's first request reads document.featurePolicy"),

        new Step(16, "css-properties", "CssStyleProperties.BodyJs()",
            "after the global prune: window.CSSStyleProperties is a name the device's list does not carry"),

        new Step(17, "canvas", "CanvasSurface.BodyJs()",
            "with the other device bodies: the baked pictures are this device's own renderings"),

        new Step(18, "webgl", "WebGlSurface.BodyJs()",
            "with the other device bodies: the parameters name an Apple GPU"),

        new Step(19, "global-surface", "GlobalSurface.BodyJs()",
            "after the prunes and the CSS synthesis: it builds back the names the device list advertises"),

        new Step(20, "handlers", "HandlerSurface.BodyJs()",
            "after the globals: it skips names that already exist, and hsw reads their descriptors"),

        new Step(21, "match-media", "MediaQuerySurface.BodyJs()",
            "after the geometry bodies: it answers the queries built from screen.* and innerWidth"),

        new Step(22, "fonts-media", "FontMediaSurface.BodyJs()",
            "after matchMedia: both answer questions built from this device's own figures"),

        new Step(23, "mask-pass", "MaskTargets.ApplyJs()",
            "after every patch: a getter that has not been installed yet cannot be masked"),

        new Step(24, "baseline-snapshot", "WindowBaselineSnapshot.BodyJs()",
            "last of all: the target re-snapshots at 0x03d99162, so its own late globals are not reported as the page's"),
    };

    /// <summary>The names in order.</summary>
    public static IReadOnlyList<string> Names => Steps.Select(s => s.Name).ToList();

    /// <summary>
    /// Check a composition source for the order. Returns one message per violation, empty when it holds.
    /// </summary>
    public static IReadOnlyList<string> Check(string bridgeSource)
    {
        var problems = new List<string>();
        var positions = new List<(Step Step, int Index)>();

        foreach (var step in Steps)
        {
            // the first mention is the composition; later mentions are comments or call sites
            var index = bridgeSource.IndexOf(step.Marker, System.StringComparison.Ordinal);
            if (index < 0)
            {
                problems.Add($"{step.Name}: marker not found ({step.Marker})");
                continue;
            }

            positions.Add((step, index));
        }

        if (problems.Count > 0) return problems;

        foreach (var (step, index) in positions)
        {
            var earlier = positions.Where(p => p.Step.Position < step.Position && p.Index > index).ToList();
            foreach (var wrong in earlier)
                problems.Add($"{step.Name} appears before {wrong.Step.Name}, but {wrong.Step.Name} must come first " +
                             $"({wrong.Step.Why})");
        }

        return problems;
    }

    /// <summary>The rule three rounds produced.</summary>
    public const string Rule =
        "position is semantics: a body that installs, orders, deletes or masks must sit where its verb allows";
}
