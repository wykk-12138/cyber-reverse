namespace Cybersole.Stores.Scripts;

/// <summary>
/// The window baseline, re-taken as the very last thing the surface does (R192).
///
/// <para>
/// In the target the snapshot is literally the last statement of the injecting IIFE
/// (<c>0x03d99162</c>), after every install and after the prunes. The replica took it during the window-order step,
/// which is fine for everything installed above it — and wrong for everything installed below: the
/// <c>CSSStyleProperties</c> synthesis and the css prototype are added afterwards, so a live enumeration would report
/// them as "something the page defined" and push them to the END of <c>Object.keys(window)</c>. That is exactly the
/// region hsw reads.
/// </para>
///
/// <para>
/// The list is read through the reference captured at the top (<see cref="NativeRefs"/>) so the key-order wrapper
/// cannot filter what the snapshot records.
/// </para>
/// </summary>
public static class WindowBaselineSnapshot
{
    /// <summary>The re-snapshot, last in the surface.</summary>
    public static string BodyJs() => """
        // ---- the window baseline, re-taken at the end (R192) -------------------------------
        // Everything the surface installs is in place now, including the CSSStyleProperties synthesis: a snapshot
        // taken earlier would report this script's own late globals as names the page defined, and they would land at
        // the end of Object.keys(window) — the slice hsw sweeps.
        (() => {
        try {
          const base = G.__windowBaseline;
          if (!base) return;
          const own = G.__nativeOwnNames || Object.getOwnPropertyNames;
          base.names = new Set(own(G));
        } catch (e) {}
        })();
        """;

    /// <summary>Why it is the last step.</summary>
    public const string Rule =
        "the snapshot has to include everything installed above, or the slots this script added itself would later be "
        + "reported as something the page defined";
}
