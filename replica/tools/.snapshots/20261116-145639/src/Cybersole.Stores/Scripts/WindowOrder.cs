using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// How the window's own list is ordered, and where the page's later globals go (R185).
///
/// <code>
/// const topList = (all, names, enumerableOnly) => {
///   const base = FRAMED ? all.filter((n) => !MAIN_FRAME_ONLY.has(n)) : all;
///   if (!WINDOW_BASELINE) return base.slice();
///   const known = new Set(base);
///   const indices = [], defined = [];
///   names.forEach((name) => {
///     if (WINDOW_BASELINE.has(name) || known.has(name)) return;
///     (/^(0|[1-9][0-9]*)$/.test(name) ? indices : defined).push(name);
///   });
///   const out = indices.concat(base, defined);
///   if (enumerableOnly &amp;&amp; !FRAMED &amp;&amp; names.indexOf('webkit') !== -1 &amp;&amp; out.indexOf('webkit') === -1) {
///     const at = out.indexOf('Raven');
///     out.splice(at === -1 ? out.length : at, 0, 'webkit');
///   }
///   return out;
/// };
/// </code>
///
/// <para>
/// This is the answer to the question R184 left open: the prune does not delete a page's own globals. The <b>order</b>
/// places them — numeric indices in front, named ones behind — and only the baseline decides which is which:
/// </para>
///
/// <code>
/// // MUST stay the last statement. The snapshot has to include everything installed above, or the slots this script
/// // added itself would later be reported as something the page defined.
/// if (isWindow) { try { WINDOW_BASELINE = new Set(nativeOwnNames(G)); } catch (e) { } }
/// </code>
///
/// <para>
/// The last two lines of <c>topList</c> are the capture's own correction: the iPhone reported
/// <c>["__gCrWeb","hsw","__wdata","webkit"]</c> with <c>webkit</c> last, and <c>webkit</c> is not in the enumerable list —
/// so it is spliced in explicitly, in front of <c>Raven</c>, and only for the top-level enumerable pass.
/// </para>
/// </summary>
public static class WindowOrder
{
    /// <summary>The numeric-index test the capture uses (no <c>+</c>, no <c>e</c>, no leading zeros).</summary>
    public const string IndexTest = @"^(0|[1-9][0-9]*)$";

    /// <summary>The name the enumerable pass inserts, and the name it is inserted before.</summary>
    public const string InsertName = "webkit";

    /// <inheritdoc cref="InsertName"/>
    public const string InsertBefore = "Raven";

    /// <summary>
    /// The mechanism, installed as a function on the global so a test can drive it with synthetic input. Wiring it into
    /// <c>Object.keys</c> / <c>getOwnPropertyNames</c> is deliberately separate: R180 measured that wrapping those makes a
    /// mutated run hang, so the function is proved first and the wrapper is a later decision.
    /// </summary>
    public static string BodyJs()
    {
        var mainFrame = string.Join(", ", KeyOrderTable.MainFrameOnly.Select(n => "'" + n + "'"));
        var all = string.Join(", ", WindowNameTable.All.Select(Quote));
        var enm = string.Join(", ", WindowNameTable.Enum.Select(Quote));

        return """
               // ---- window order (R185, constants since R192) ------------------------------------
               // Where the page's later globals go: numeric indices in front, named ones behind. The prune does not
               // delete them; only the baseline decides which names are the script's and which are the page's.
               //
               // The BASE is the device's own recorded list, not this realm's live enumeration. The target does the
               // same — it passes WINDOW_ENUM / WINDOW_ALL (0x03d0f9d0 / 0x03d14741) into topList — and the difference
               // is measurable: hsw sweeps `Object.keys(window).slice(-25)`, so which names sit at the end is the
               // answer, and Blink's order is not the device's.
               try {
                 const MAIN_FRAME_ONLY = new Set([__MAIN_FRAME__]);
                 const WINDOW_ALL = [__WINDOW_ALL__];
                 const WINDOW_ENUM = [__WINDOW_ENUM__];
                 G.__windowNames = { all: WINDOW_ALL, enum: WINDOW_ENUM };

                 const topList = (all, names, enumerableOnly) => {
                   const base = G.__windowBaseline && G.__windowBaseline.framed
                     ? all.filter((n) => !MAIN_FRAME_ONLY.has(n))
                     : all;

                   const baseline = G.__windowBaseline && G.__windowBaseline.names;
                   if (!baseline) return base.slice();

                   const known = new Set(base);
                   const indices = [], defined = [];
                   (names || []).forEach((name) => {
                     if (baseline.has(name) || known.has(name)) return;
                     (/^(0|[1-9][0-9]*)$/.test(name) ? indices : defined).push(name);
                   });

                   const out = indices.concat(base, defined);

                   // `webkit` is in the own-names list and NOT in the enumerable one, so it has to be spliced in
                   // explicitly — in front of `Raven`, and only for the top-level enumerable pass.
                   if (enumerableOnly && !(G.__windowBaseline && G.__windowBaseline.framed)
                       && (names || []).indexOf('webkit') !== -1 && out.indexOf('webkit') === -1) {
                     const at = out.indexOf('Raven');
                     out.splice(at === -1 ? out.length : at, 0, 'webkit');
                   }

                   return out;
                 };

                 G.__topList = topList;

                 // MUST be the last statement of the installer: the snapshot has to include everything installed
                 // above, or the slots this script added itself would be reported as the page's.
                 // R187: read through the reference captured at the top (0x03d05776 in the target), not through the
                 // live builtin — the key-order wrapper is installed above this point in the target's own script.
                 try {
                   const names = new Set((G.__nativeOwnNames || Object.getOwnPropertyNames)(G));
                   G.__windowBaseline.names = names;
                 } catch (e) {}
               } catch (e) {}
               """
            .Replace("__MAIN_FRAME__", mainFrame)
            .Replace("__WINDOW_ALL__", all)
            .Replace("__WINDOW_ENUM__", enm);
    }

    private static string Quote(string name) => "'" + name.Replace("\\", "\\\\").Replace("'", "\\'") + "'";

    /// <summary>Why the baseline is taken last.</summary>
    public const string BaselineRule =
        "the snapshot has to include everything installed above, or the slots this script added itself would later be "
        + "reported as something the page defined";

    /// <summary>The order in one sentence.</summary>
    public const string Rule =
        "indices in front, base in the middle, the page's named globals behind — and webkit spliced in before Raven";
}
