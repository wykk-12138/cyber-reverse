using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The two prunes the replica never had: the global object and the document (R184).
///
/// <para>
/// <b>The global prune.</b> Every name on the window that the device's own list does not carry is deleted — which is
/// how <c>window.chrome</c> stops answering. The capture's reason for making it a function is the whole point:
/// </para>
///
/// <code>
/// // Exposed as a function, not a one-shot loop, because a child realm arrives with a fresh global carrying the full
/// // Blink surface again. Deleting only in this realm left `'chrome' in window` false at the top and TRUE inside an
/// // iframe -- and the challenge runs in an iframe, so the frame that matters was answering honestly.
/// </code>
///
/// <para>
/// <b>The document prune.</b> Eight Blink-only members are deleted, and the reason is the first request of the whole flow:
/// hCaptcha's <c>checksiteconfig</c> carries <c>spst</c>, computed from <c>document.hasPrivateToken</c> and
/// <c>document.featurePolicy</c>. "Private State Tokens and featurePolicy are Blink-only; WebKit has never shipped
/// either, so a real Chrome-on-iOS can only ever answer 0. We answered 1. Verified against a device capture on the SAME
/// sitekey AND the same api.js build (d865efcccaf8): device spst=0, bot spst=1 — the only apples-to-apples comparison in
/// the whole artifact set, and we were losing it on request one."
/// </para>
/// </summary>
public static class GlobalPrune
{
    /// <summary>
    /// Names that survive the global prune although the device's list does not carry them: this script's own hooks, and
    /// the eight hCaptcha names the capture keeps.
    /// </summary>
    public static readonly IReadOnlyList<string> Keep = new[]
    {
        // the capture's own keep list, verbatim
        "hsw", "Raven", "_sharedLibs", "webkit", "__wdata", "__hcLoggerInstalled",
        "__hcWorkerProbeInstalled", "__hcWorker", "__hcCollector", "__hcLogCalls", "__hcSweepDelay",

        // this replica's internals — a prune that deleted them would disable the mask mid-flight
        "__nativeMask", "__nativeMaskInstalled", "__patchJournal", "__windowBaseline", "__topList",
        "__globalPrune", "__documentPrune", "__nativeOwnNames", "__cssProto", "__windowNames",
        "__brandCheckRan", "__engineParityInstalled",
    };

    /// <summary>The eight Blink-only document members WebKit has never shipped.</summary>
    public static readonly IReadOnlyList<string> DocumentBlinkOnly = new[]
    {
        "featurePolicy", "hasPrivateToken", "hasRedemptionRecord", "hasTrustToken",
        "browsingTopics", "requestStorageAccessFor", "prerendering", "startViewTransition",
    };

    /// <summary>The two members whose presence makes <c>spst</c> answer 1.</summary>
    public static readonly IReadOnlyList<string> SpstMembers = new[] { "hasPrivateToken", "featurePolicy" };

    /// <summary>
    /// Names Chromium puts BACK after a delete. Measured in R206: one suite run in about six ended with
    /// <c>extra[chrome]</c> — <c>'chrome' in window</c> true again, minutes after the prune had removed it. A single
    /// delete cannot win a race against a renderer that re-installs the object later, so the same deletion is
    /// re-asserted at the moments a renderer can do that.
    /// </summary>
    public static readonly IReadOnlyList<string> ReCreated = new[] { "chrome" };

    /// <summary>The value a real Chrome-on-iOS can only ever report.</summary>
    public const int DeviceSpst = 0;

    /// <summary>The value the capture's bot was reporting.</summary>
    public const int BotSpst = 1;

    /// <summary>The global prune, as a function of a realm so a child frame gets it too.</summary>
    public static string GlobalBodyJs()
    {
        var device = string.Join(", ", WindowNameTable.All.Select(n => "'" + n.Replace("'", "\\'") + "'"));
        var keep = string.Join(", ", Keep.Select(n => "'" + n + "'").Concat(new[] { "'__globalPruneReassert'" }));

        return """
               // ---- the global prune (R184) ------------------------------------------------------
               // A child realm arrives with a fresh global carrying the full Blink surface again, so this is a
               // function of a realm, not a one-shot loop: deleting only in this realm leaves `'chrome' in window`
               // false at the top and TRUE inside an iframe — and the challenge runs in an iframe.
               try {
                 const DEVICE_GLOBALS = new Set([__DEVICE__]);
                 const KEEP = new Set([__KEEP__]);

                 const globalPrune = (realm) => {
                   if (!realm) return;
                   // R187: `nativeOwnNames` (0x03d27321 in the target) rather than the live builtin. The key-order
                   // wrapper is installed above this prune, and the target can only afford that because it holds the
                   // reference taken before the wrapper existed.
                   const own = G.__nativeOwnNames || Object.getOwnPropertyNames;
                   own(realm).forEach((key) => {
                     if (!DEVICE_GLOBALS.has(key) && !KEEP.has(key)) {
                       try { delete realm[key]; } catch (e) {}
                     }
                   });
                 };

                 // R206: Chromium re-installs `chrome` after this runs. Re-assert the deletion of the names that come
                 // back, at every moment a renderer can put them there again -- the current task, DOMContentLoaded,
                 // load, one rAF and three short timers. Only the ReCreated list is touched, so this cannot delete
                 // anything this script added later in the load.
                 const reassert = (realm) => {
                   if (!realm) return;
                   [__RECREATED__].forEach((name) => { try { delete realm[name]; } catch (e) {} });
                 };
                 const scheduleReassert = (realm) => {
                   if (!realm) return;
                   reassert(realm);
                   try { realm.setTimeout(() => reassert(realm), 0); } catch (e) {}
                   try { realm.setTimeout(() => reassert(realm), 60); } catch (e) {}
                   try { realm.setTimeout(() => reassert(realm), 300); } catch (e) {}
                   try { if (realm.document && realm.document.addEventListener)
                     realm.document.addEventListener('DOMContentLoaded', () => reassert(realm), true); } catch (e) {}
                   try { if (realm.addEventListener)
                     realm.addEventListener('load', () => reassert(realm), true); } catch (e) {}
                   try { if (realm.requestAnimationFrame) realm.requestAnimationFrame(() => reassert(realm)); } catch (e) {}
                 };

                 G.__globalPrune = globalPrune;
                 G.__globalPruneReassert = scheduleReassert;
                 globalPrune(G);
                 scheduleReassert(G);
               } catch (e) {}
               """
            .Replace("__DEVICE__", device)
            .Replace("__KEEP__", keep)
            .Replace("__RECREATED__", string.Join(", ", ReCreated.Select(n => "'" + n + "'")));
    }

    /// <summary>The document prune: eight members, then <c>spst</c> can only answer 0.</summary>
    public static string DocumentBodyJs()
    {
        var names = string.Join(", ", DocumentBlinkOnly.Select(n => "'" + n + "'"));

        return """
               // ---- the document prune (R184) ----------------------------------------------------
               // hCaptcha's checksiteconfig — the FIRST request of the flow, in plaintext, before a single sensor
               // byte — carries `spst`, computed from document.hasPrivateToken and document.featurePolicy. Both are
               // Blink-only; WebKit has never shipped either, so a real Chrome-on-iOS can only answer 0.
               try {
                 const prune = (realm) => {
                   const proto = realm && realm.Document && realm.Document.prototype;
                   if (!proto) return;
                   [__NAMES__].forEach((name) => {
                     try { delete proto[name]; } catch (e) {}
                     try { if (realm.document) delete realm.document[name]; } catch (e) {}
                   });
                 };

                 G.__documentPrune = prune;
                 prune(G);
               } catch (e) {}
               """.Replace("__NAMES__", names);
    }

    /// <summary>What the prune is for, in the capture's words.</summary>
    public const string Rule =
        "the challenge runs in an iframe, so the frame that matters was answering honestly";

    /// <summary>The first-request consequence.</summary>
    public const string SpstStory =
        "device spst=0, bot spst=1 — the only apples-to-apples comparison in the whole artifact set, and we were "
        + "losing it on request one";
}
