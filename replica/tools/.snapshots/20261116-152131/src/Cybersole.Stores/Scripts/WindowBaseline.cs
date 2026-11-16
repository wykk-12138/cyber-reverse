using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// What the recorded window name list says, and the baseline mechanism that keeps it honest (R181).
///
/// <para>
/// The capture's top-level list has <b>1290</b> names. Eleven of them are Chrome-for-iOS's own injected hooks — names no
/// other browser has, and names this replica's window does not carry:
/// </para>
///
/// <code>
/// _injected_programmatic_form_submission_handler   _injected_clipboard
/// _injected_setup_frame                            _injected_passkey_controller
/// _injected_autofill_form_features                 _injected_scroll_helper
/// _injected_navigation                             _injected_gcrweb
/// _injected_choose_file                            _injected_print
/// gcrweb                                           __gCrWeb
/// </code>
///
/// <para>
/// Two of them — <c>_injected_scroll_helper</c> and <c>_injected_navigation</c> — are removed from every frame but the
/// top one, because "a frame advertised two names its real counterpart lacks". The rest are part of what makes the
/// window look like a phone running Chrome rather than a desktop Chromium with a rewritten navigator.
/// </para>
///
/// <para>
/// The list cannot be a constant at the top level, and the capture explains why: <c>api.js</c> hands the host page's
/// globals to hCaptcha — <c>function sr(){ return Object.keys(window).sort().join(",") }</c>, called from
/// <c>initChallenge</c> — which goes into the create-challenge message as <c>wdata</c>, the frame stores it as
/// <c>window.__wdata</c>, and the wasm reads it back. So the answer has to be the <b>live</b> key list, with this script's
/// own additions ordered deliberately and the page's later additions appended after them.
/// </para>
///
/// <para>
/// <c>WINDOW_BASELINE</c> is that mechanism: every own name the engine reported once this script had finished
/// installing — assigned on the <b>last line of the file</b>, at document-start, before any page script. "Whatever the
/// engine reports later that is not in here, the page put there."
/// </para>
/// </summary>
public static class WindowBaseline
{
    /// <summary>The eleven Chrome-for-iOS names, verbatim from the recorded list.</summary>
    public static readonly IReadOnlyList<string> InjectedNames = new[]
    {
        "_injected_programmatic_form_submission_handler", "_injected_clipboard",
        "_injected_setup_frame", "_injected_passkey_controller",
        "_injected_autofill_form_features", "_injected_scroll_helper",
        "_injected_navigation", "_injected_gcrweb",
        "_injected_choose_file", "_injected_print",
        "gcrweb", "__gCrWeb",
    };

    /// <summary>The two names a child frame must not advertise.</summary>
    public static IReadOnlyList<string> MainFrameOnly => KeyOrderTable.MainFrameOnly;

    /// <summary>
    /// How many names the recorded top-level list has. R183 corrected this from 1290: the list is 1062, and the earlier
    /// number came from a regex that also caught quoted strings around the array.
    /// </summary>
    public const int RecordedNameCount = 1062;

    /// <summary>How many of them the enumerable pass reports.</summary>
    public const int RecordedEnumCount = 228;

    /// <summary>How many of them are this engine's own injected hooks.</summary>
    public static int InjectedCount => InjectedNames.Count;

    /// <summary>
    /// The mechanism: <c>FRAMED</c> by identity, the baseline assigned last, and the page's later names appended after
    /// this script's own.
    /// </summary>
    public static string BodyJs()
    {
        var injected = string.Join(", ", InjectedNames.Select(n => "'" + n + "'"));
        var mainFrame = string.Join(", ", MainFrameOnly.Select(n => "'" + n + "'"));

        return """
               // ---- window baseline (R181) ------------------------------------------------------
               // hCaptcha's api.js hands `Object.keys(window).sort().join(",")` to the wasm as `wdata`, and the proof
               // grows with it — so the answer has to be the LIVE key list, not a frozen array. The baseline is every
               // own name the engine reported once this script had finished installing; whatever appears later is the
               // page's own.
               try {
                 // `top` is readable across origins and only identity is compared
                 const FRAMED = (() => { try { return G.top !== G; } catch (e) { return true; } })();
                 const MAIN_FRAME_ONLY = new Set([__MAIN_FRAME__]);

                 // the names Chrome for iOS puts on its own window. R193: this body no longer CREATES them — it used
                 // to define all twelve as `{}`, and the device says ten of them are booleans (`_injected_clipboard`
                 // measured 'object' where the capture records `"b"`). The kinds live in GlobalSurfaceTable, so that
                 // is where they are built; this list stays as the record of which names are Chrome-for-iOS's own.
                 const INJECTED = [__INJECTED__];

                 G.__windowBaseline = { framed: FRAMED, mainFrameOnly: MAIN_FRAME_ONLY, injected: INJECTED };
               } catch (e) {}
               """.Replace("__MAIN_FRAME__", mainFrame).Replace("__INJECTED__", injected);
    }

    /// <summary>The rule the baseline exists for.</summary>
    public const string Rule =
        "the answer has to be the LIVE key list: api.js sends Object.keys(window).sort().join(',') to the wasm as "
        + "wdata, and the proof grows with it";

    /// <summary>What the recorded list proves about this replica.</summary>
    public const string Gap =
        "eleven names in the recorded list are Chrome-for-iOS's own injected hooks; a desktop Chromium with a rewritten "
        + "navigator has none of them, which is a device-specific tell no navigator value can offset";
}
