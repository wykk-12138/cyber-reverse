using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// <c>measureText</c> and the media-type verdicts — two tables that look like data and are actually answers to
/// questions about this device (R198).
///
/// <para>
/// <b>Why the font key is normalised twice.</b> The target's note:
/// </para>
///
/// <code>
/// The capture keys on the font string as *asked for*; ctx.font gives it back *serialized*, and the engines disagree --
/// the device turned '16px "Roboto"' into '16px Roboto'. Index both ways or every quoted family misses and falls
/// through to the real Windows metrics.
/// Whitespace is normalised as well as quotes. hsw asks in fallback-stack form -- "16px 'Segoe UI', monospace" -- and
/// the engine serializes that back with different quoting AND different spacing, so quote-stripping alone still missed
/// and fell through to the host's real metrics.
/// </code>
///
/// <para>
/// <b>Why the media table carries every verdict, including the empty ones.</b>
/// </para>
///
/// <code>
/// audio/ogg; codecs="vorbis" was "" here, which is what Safari used to answer ... iOS 26 answers "probably" for both
/// audio and video -- re-measured on the device. An empty string drops the row out of hsw's codec list entirely, so the
/// payload carried 9 rows where the device sends 10; a missing row is a louder signal than a wrong verdict in one.
/// </code>
///
/// <para>
/// The rest of that block follows from WebKit's surface: <c>MediaSource</c>/<c>SourceBuffer</c> are deleted (Chromium has
/// them, WebKit does not), <c>ManagedMediaSource</c> is synthesized for iOS 17+, and both <c>isTypeSupported</c>
/// variants answer from the same table.
/// </para>
/// </summary>
public static class FontMediaSurface
{
    /// <summary>The normalisation both sides of the font lookup run through.</summary>
    public const string FontKeyRule =
        "quote-stripping alone still missed and fell through to the host's real metrics";

    /// <summary>Why a missing row is worse than a wrong one.</summary>
    public const string MediaRule =
        "a missing row is a louder signal than a wrong verdict in one";

    /// <summary>The interface WebKit has and Chromium does not.</summary>
    public const string ManagedInterface = "ManagedMediaSource";

    /// <summary>The two interfaces WebKit does not have.</summary>
    public static readonly string[] Absent = { "MediaSource", "SourceBuffer" };

    /// <summary>The layer.</summary>
    public static string BodyJs()
    {
        var absent = string.Join(", ", Absent.Select(n => "'" + n + "'"));

        return """
               // ---- measureText + media types (R198) ------------------------------------------------------
               // Two tables that look like data and are answers about this device. The font key is normalised on both
               // sides (quotes AND whitespace), because the capture keys the font as ASKED FOR and ctx.font returns it
               // SERIALIZED, and the two engines serialize differently.
               (() => {
               try {
                 const M = G.__nativeMask || {};
                 const asNative = M.asNative || ((fn) => fn);
                 const install = (proto, name, build) => {
                   try {
                     if (!proto) return;
                     const original = proto[name];
                     if (typeof original !== 'function') return;
                     const wrapped = { m() { return build.call(this, original, arguments); } }.m;
                     if (M.asNative) M.asNative(wrapped, name, original.length);
                     Object.defineProperty(proto, name,
                       { value: wrapped, writable: true, enumerable: false, configurable: true });
                   } catch (e) {}
                 };

                 const FONTS = __FONTS__;
                 const MEDIA = __MEDIA__;

                 const unquote = (s) => String(s).replace(/["']/g, '').replace(/\s+/g, '');
                 const FONTS_LOOSE = {};
                 Object.keys(FONTS).forEach((key) => { FONTS_LOOSE[unquote(key)] = FONTS[key]; });

                 if (typeof CanvasRenderingContext2D !== 'undefined') {
                   install(CanvasRenderingContext2D.prototype, 'measureText', function (original, args) {
                     const metrics = original.apply(this, args);
                     const text = String(args[0]);
                     const row = FONTS[this.font + '|' + text] || FONTS_LOOSE[unquote(this.font + '|' + text)];
                     if (row) {
                       Object.keys(row).forEach((key) => {
                         try {
                           Object.defineProperty(metrics, key,
                             { value: row[key], writable: true, enumerable: true, configurable: true });
                         } catch (e) {}
                       });
                     }
                     return metrics;
                   });
                 }

                 if (typeof HTMLAudioElement !== 'undefined') {
                   install(HTMLAudioElement.prototype, 'canPlayType', function (original, args) {
                     const row = MEDIA[String(args[0])];
                     return row && row.audio !== undefined ? row.audio : original.apply(this, args);
                   });
                 }
                 if (typeof HTMLVideoElement !== 'undefined') {
                   install(HTMLVideoElement.prototype, 'canPlayType', function (original, args) {
                     const row = MEDIA[String(args[0])];
                     return row && row.video !== undefined ? row.video : original.apply(this, args);
                   });
                 }
                 if (typeof G.MediaRecorder === 'function') {
                   install(G.MediaRecorder, 'isTypeSupported', function (original, args) {
                     const row = MEDIA[String(args[0])];
                     return row ? !!row.recorder : original.apply(this, args);
                   });
                 }

                 // WebKit has no MediaSource at all; Chromium does.
                 [__ABSENT__].forEach((name) => { try { delete G[name]; } catch (e) {} });

                 // iOS 17+ exposes ManagedMediaSource. Chromium has no such interface, so install one whose
                 // isTypeSupported answers from the captured table.
                 // The global-surface pass runs BEFORE this one and already creates a bare `ManagedMediaSource`
                 // constructor (the name is in the device window list), so the interface usually exists without
                 // isTypeSupported on it. Measured: the first version skipped the whole block and the page threw
                 // "window.ManagedMediaSource.isTypeSupported is not a function".
                 try {
                   if (!G.ManagedMediaSource) {
                     const ManagedMediaSource = function ManagedMediaSource() {
                       throw new TypeError('Illegal constructor');
                     };
                     asNative(ManagedMediaSource, 'ManagedMediaSource', 0);
                     Object.defineProperty(G, 'ManagedMediaSource',
                       { value: ManagedMediaSource, writable: true, configurable: true });
                   }
                   const iface = G.ManagedMediaSource;
                   if (iface && typeof iface.isTypeSupported !== 'function') {
                     const isTypeSupported = function isTypeSupported(type) {
                       const row = MEDIA[String(type)];
                       return row ? !!row.managed : false;
                     };
                     asNative(isTypeSupported, 'isTypeSupported', 1);
                     Object.defineProperty(iface, 'isTypeSupported',
                       { value: isTypeSupported, writable: true, configurable: true });
                   }
                 } catch (e) {}
               } catch (e) {}
               })();
               """
            .Replace("__FONTS__", FontMediaTable.FontsJs)
            .Replace("__MEDIA__", FontMediaTable.MediaJs)
            .Replace("__ABSENT__", "[" + absent + "]");
    }
}
