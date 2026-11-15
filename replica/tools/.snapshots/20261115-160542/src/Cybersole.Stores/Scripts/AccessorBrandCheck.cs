using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Two mechanisms from the image's injection framework, both about being believed under a probe (R173).
///
/// <para>
/// <b>1. A native accessor throws for a foreign receiver.</b> The image says it exactly:
/// </para>
///
/// <code>
/// // A native accessor is bound to its interface and throws when handed a foreign receiver. A getter that just
/// // closes over a constant answers anyone, and that difference needs no reference device to see: pull the
/// // descriptor off Navigator.prototype, call .get on {}, and a real browser throws where a naive override
/// // returns the user agent.
/// </code>
///
/// <para>
/// The replica installed data properties, which answer anyone. One line — a brand check at the top of the getter —
/// makes the descriptor behave like the platform's.
/// </para>
///
/// <para>
/// <b>2. Patches are recorded with a realm-independent path.</b> <c>pathOf</c> maps a patched object back to a name
/// like <c>['Navigator', 'prototype']</c> or <c>['Intl', 'DateTimeFormat', 'prototype']</c>, and <c>record</c> pushes
/// <c>{ path, key, from }</c> so a child realm can be patched by resolving the path there. The image's <c>KNOWN</c>
/// list is the set of constructors that can appear in such a path.
/// </para>
/// </summary>
public static class AccessorBrandCheck
{
    /// <summary>The constructors that can appear in a replay path, in the image's order.</summary>
    public static readonly IReadOnlyList<string> Known = new[]
    {
        "Navigator", "Screen", "CanvasRenderingContext2D", "HTMLCanvasElement",
        "WebGLRenderingContext", "WebGL2RenderingContext", "AudioBuffer", "DynamicsCompressorNode",
        "AudioContext", "OfflineAudioContext", "HTMLAudioElement", "HTMLVideoElement", "MediaSource",
        "MediaRecorder", "ManagedMediaSource", "Function", "Object", "Reflect", "Error",
        "HTMLIFrameElement", "Date", "SpeechSynthesis", "speechSynthesis",
    };

    /// <summary>The Intl names, which need a three-step path because they hang off <c>Intl</c>.</summary>
    public static readonly IReadOnlyList<string> IntlNames = new[]
    {
        "DateTimeFormat", "NumberFormat", "Collator", "PluralRules", "RelativeTimeFormat",
        "ListFormat", "DisplayNames", "Segmenter", "DurationFormat",
    };

    /// <summary>The members installed as brand-checked accessors rather than data properties.</summary>
    public static readonly IReadOnlyList<string> Guarded = new[]
    {
        "userAgent", "platform", "vendor", "appVersion",
    };

    /// <summary>
    /// Statements that replace the listed members with accessors whose getter throws for a foreign receiver, the way a
    /// real accessor does.
    /// </summary>
    public static string BodyJs(IReadOnlyList<string> names)
    {
        var list = string.Join(", ", names.Select(n => "'" + n + "'"));

        return """
               // ---- brand-checked accessors (R173, corrected in R176) ---------------------------
               // A native accessor is bound to its interface and throws when handed a foreign receiver. A getter that
               // just closes over a constant answers anyone, and that difference needs no reference device to see:
               // pull the descriptor off Navigator.prototype, call .get on {}, and a real browser throws where a naive
               // override returns the user agent.
               //
               // Two things are easy to get wrong, and the capture says so:
               //
               //   - the message is WEBKIT's, not Blink's "Illegal invocation", because WebKit is the engine being
               //     presented: 'The Navigator.platform getter can only be used on instances of Navigator'
               //   - the brand is checked with Object.prototype.toString, NOT instanceof. Child realms are patched by
               //     copying this descriptor into them, so the closure keeps the PARENT's constructor, and instanceof
               //     is realm-scoped — `this instanceof Navigator` is false for a perfectly good navigator inside an
               //     iframe. The toStringTag survives the realm boundary.
               //
               // And the stack: eliding our own frames is measured and safe, but inventing a native frame is a guess.
               // WebKit adds NO JS frame for an IDL brand check at all, so caller-frames-only is the faithful answer.
               try {
                 const P = G.Navigator && G.Navigator.prototype;

                 // Captured ONCE, here: reading Error.captureStackTrace at throw time would call whatever the page
                 // has installed on it, announcing every brand-check throw and handing the probe a live reference to
                 // the installed getter as its second argument.
                 const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
                 let ELIDE = null;

                 // the names a call site installs non-enumerable; empty here, because every member this workspace
                 // installs on Navigator.prototype is one the device reports in its for-in walk
                 const MUST_HIDE = new Set([]);

                 if (P) {
                   const install = (target, name, v, enumerable) => {
                     let brand = null;
                     try { brand = Object.prototype.toString.call(target); } catch (e) { brand = null; }
                     const label = (target && target.constructor && target.constructor.name) || '';

                     const getter = Object.getOwnPropertyDescriptor({
                       get x() {
                         if (brand && brand !== '[object Object]'
                             && Object.prototype.toString.call(this) !== brand) {
                           // Armed with an EMPTY head on purpose: our own frames are dropped, and no native frame is
                           // invented for a check that, in WebKit, never had one.
                           ELIDE = [getter, ''];
                           try {
                             throw new TypeError('The ' + label + '.' + name
                               + ' getter can only be used on instances of ' + label);
                           } finally { ELIDE = null; }
                         }
                         return v;
                       },
                     }, 'x').get;

                     // NOTE: the mask may rename this getter, but it must not rebuild it — MaskTargets' helper wraps
                     // the implementation, and a rebuilt getter has no brand check (measured: the first version of
                     // this function returned `M.getter(...)`, and the throw disappeared).
                     return getter;
                   };

                   [__NAMES__].forEach((name) => {
                     try {
                       let current;
                       try { current = G.navigator[name]; } catch (e) { current = undefined; }
                       if (current === undefined) return;

                       const getter = install(P, name, current, true);
                       try {
                         const M = G.__nativeMask;
                         if (M && M.asNative) M.asNative(getter, 'get ' + name, 0);
                       } catch (e) {}
                       try { Object.defineProperty(getter, 'name', { value: 'get ' + name, configurable: true }); }
                       catch (e) {}

                       // `enumerable: enumerable !== false` — true by default, false when a call site says so. The
                       // image's value() takes the parameter and passes it straight through (R177).
                       Object.defineProperty(P, name,
                         { get: getter, configurable: true, enumerable: !MUST_HIDE.has(name) });
                     } catch (e) {}
                   });
                 }
               } catch (e) {}
               """.Replace("__NAMES__", list);
    }

    /// <summary>
    /// The error a foreign receiver earns, in WebKit's wording rather than Blink's: the engine being presented is the
    /// one whose sentence has to be produced.
    /// </summary>
    public static string MessageFor(string label, string name) =>
        "The " + label + "." + name + " getter can only be used on instances of " + label;

    /// <summary>
    /// The image's <c>value()</c> tail, recorded because it is the part that has to be copied exactly (R177):
    /// </summary>
    /// <code>
    /// Object.defineProperty(getter, 'name', { value: 'get ' + name, configurable: true });
    /// Object.defineProperty(target, name, {
    ///   get: getter,
    ///   configurable: true,
    ///   enumerable: enumerable !== false,
    /// });
    /// record(target, name);
    /// </code>
    public const string ValueTail =
        "get: getter, configurable: true, enumerable: enumerable !== false — then record(target, name)";

    /// <summary>
    /// The image's <c>method()</c>: a replacement whose <c>length</c> comes from the ORIGINAL, whose name is the same,
    /// and which keeps the original as its first argument.
    /// </summary>
    public const string MethodShape =
        "the arity of a patched method comes from the ORIGINAL, and the original is handed to the builder as its "
        + "first argument";

    /// <summary>
    /// The image's <c>reseat</c>, which this workspace implements as <see cref="NavOrder.ReseatBodyJs"/> — recorded here
    /// because R177 measured that the two agree: descriptors carried across untouched, non-configurable members left
    /// alone, and anything the device did not list keeping its relative order at the end.
    /// </summary>
    public const string ReseatShape =
        "delete then define appends: kept descriptors are carried across untouched, unlisted members keep their "
        + "relative order at the end, and non-configurable members are left alone";

    /// <summary>Why a data property is not enough.</summary>
    public const string Rule =
        "a getter that closes over a constant answers anyone; a native accessor is bound to its interface and throws "
        + "for a foreign receiver — and that difference needs no reference device to see";
}
