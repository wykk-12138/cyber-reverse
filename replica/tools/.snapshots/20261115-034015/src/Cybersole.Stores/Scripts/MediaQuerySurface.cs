namespace Cybersole.Stores.Scripts;

/// <summary>
/// <c>matchMedia</c>: the recorded answers, plus the dimension features evaluated against this persona's own geometry (R197).
///
/// <para>
/// Two halves have to be right, not one — the target's own note:
/// </para>
///
/// <code>
/// WebKit re-serializes the query text with a space after the colon; Blink echoes the input verbatim. hCaptcha reads
/// .media, so both halves have to be right, not just .matches.
/// </code>
///
/// <para>
/// <b>The table cannot hold what hsw builds.</b> It reads <c>screen.width</c>/<c>screen.height</c> — answered 402/874
/// here — and then asks the media engine to confirm:
/// <c>matchMedia("(device-width: 402px) and (device-height: 874px)")</c>. No key for that can be captured ahead of
/// time, so it used to fall through to Blink, which evaluated it against the HOST display and said false: "a payload
/// claiming a 402x874 screen and denying it two reads later". The dimension features are therefore computed from the
/// same geometry this persona reports everywhere else, so the answers agree with <c>screen.*</c>, <c>innerWidth</c> and
/// <c>devicePixelRatio</c> by construction rather than by coincidence.
/// </para>
///
/// <para>
/// <b>And the lookup must be normalised.</b> Media queries are whitespace- and case-insensitive, so
/// <c>(pointer:coarse)</c> and <c>(pointer: coarse)</c> are the same question; keying on the raw string made the
/// conventional spacing miss the table and fall through to Blink — <c>true</c> for one spelling and <c>false</c> for
/// the other in the same document, "something no real browser does".
/// </para>
/// </summary>
public static class MediaQuerySurface
{
    /// <summary>The two-halves rule, in the target's words.</summary>
    public const string Rule =
        "hCaptcha reads .media, so both halves have to be right, not just .matches";

    /// <summary>The construction rule.</summary>
    public const string GeometryRule =
        "a payload claiming a 402x874 screen and denying it two reads later";

    /// <summary>The layer.</summary>
    public static string BodyJs() => """
        // ---- matchMedia (R197) ---------------------------------------------------------------------
        // Two halves, not one: .matches AND .media (WebKit re-serializes with a space after the colon). And the table
        // cannot hold what hsw BUILDS -- it asks the media engine to confirm the screen.* it just read.
        (() => {
        try {
          if (typeof G.matchMedia !== 'function') return;
          const M = G.__nativeMask || {};
          const asNative = M.asNative || ((fn) => fn);

          const QUERIES = __QUERIES__;
          const GEOMETRY = __GEOMETRY__;

          // Media queries are whitespace- and case-insensitive: `(pointer: coarse)` and `(pointer:coarse)` are the
          // same query. Keying on the raw string made the conventional spacing miss the table entirely.
          const canonical = (q) => q.toLowerCase().replace(/\s+/g, '');

          const lengthOf = (feature, raw) => {
            let m;
            if (feature === 'resolution' || feature === '-webkit-device-pixel-ratio') {
              if ((m = /^([0-9.]+)(dppx|x)?$/.exec(raw))) return parseFloat(m[1]);
              if ((m = /^([0-9.]+)dpi$/.exec(raw))) return parseFloat(m[1]) / 96;
              if ((m = /^([0-9.]+)dpcm$/.exec(raw))) return parseFloat(m[1]) * 2.54 / 96;
              return null;
            }
            if (feature === 'aspect-ratio' || feature === 'device-aspect-ratio') {
              if ((m = /^([0-9.]+)\/([0-9.]+)$/.exec(raw))) return parseFloat(m[1]) / parseFloat(m[2]);
              if ((m = /^([0-9.]+)$/.exec(raw))) return parseFloat(m[1]);
            }
            if (feature === 'monochrome') return /^[0-9]+$/.test(raw) ? parseInt(raw, 10) : null;
            if ((m = /^(-?[0-9.]+)px$/.exec(raw))) return parseFloat(m[1]);
            return raw === '0' ? 0 : null;
          };

          // One parenthesised condition, already canonical. undefined means "cannot say": the caller then leaves the
          // engine's own answer in place, exactly as before.
          const condition = (cond) => {
            if (Object.prototype.hasOwnProperty.call(QUERIES, cond)) return QUERIES[cond];
            const m = /^\((min-|max-)?([a-z-]+)(?::([^()]+))?\)$/.exec(cond);
            if (!m) return undefined;
            let bound = m[1] || '', feature = m[2];
            const prefixed = /^-webkit-(min-|max-)device-pixel-ratio$/.exec(feature);
            if (prefixed) { bound = prefixed[1]; feature = '-webkit-device-pixel-ratio'; }
            // Gecko-only features are unknown to WebKit, and an unknown feature never matches.
            if (feature.indexOf('-moz-') === 0) return false;
            if (!Object.prototype.hasOwnProperty.call(GEOMETRY, feature)) return undefined;
            const actual = GEOMETRY[feature];
            if (m[3] === undefined) return bound ? undefined : actual !== 0;
            const wanted = lengthOf(feature, m[3]);
            if (wanted === null || isNaN(wanted)) return undefined;
            if (bound === 'min-') return actual >= wanted - 1e-9;
            if (bound === 'max-') return actual <= wanted + 1e-9;
            return Math.abs(actual - wanted) < 1e-6;
          };

          // Only a plain conjunction of parenthesised conditions -- "(a) and (b) and (c)". A media type, `not`, `only`,
          // a comma list or range syntax is left to the engine.
          const evaluate = (key) => {
            if (key.charAt(0) !== '(' || key.charAt(key.length - 1) !== ')') return undefined;
            const parts = key.slice(1, -1).split(')and(');
            let result = true;
            for (let i = 0; i < parts.length; i++) {
              const answer = condition('(' + parts[i] + ')');
              if (answer === undefined) return undefined;
              result = result && answer;
            }
            return result;
          };

          const original = G.matchMedia;
          const patched = { m() {
            const list = original.apply(this, arguments);
            const asked = String(arguments[0]);
            const key = canonical(asked);
            const answer = Object.prototype.hasOwnProperty.call(QUERIES, key) ? QUERIES[key] : evaluate(key);
            try {
              if (answer !== undefined) {
                Object.defineProperty(list, 'matches',
                  { value: answer, writable: true, enumerable: true, configurable: true });
              }
            } catch (e) {}
            // `.media` keeps the caller's own text re-serialised the way WebKit does it: collapsing whitespace there
            // would mangle multi-condition queries ('screen and (min-width: 100px)').
            try {
              Object.defineProperty(list, 'media',
                { value: asked.replace(/:\s*/g, ': '), writable: true, enumerable: true, configurable: true });
            } catch (e) {}
            return list;
          } }.m;

          asNative(patched, 'matchMedia', original.length);
          Object.defineProperty(G, 'matchMedia',
            { value: patched, writable: true, enumerable: false, configurable: true });
        } catch (e) {}
        })();
        """.Replace("__QUERIES__", MediaQueryTable.QueriesJs)
           .Replace("__GEOMETRY__", MediaQueryTable.GeometryJs);
}
