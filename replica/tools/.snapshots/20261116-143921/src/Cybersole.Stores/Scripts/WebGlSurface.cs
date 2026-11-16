using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// WebGL: every parameter the device answered, and the four questions hsw asks around them (R195).
///
/// <para>
/// The target's reason for carrying the whole table rather than a sample:
/// </para>
///
/// <code>
/// // All 135/85 parameters, not a hand-picked 18. A miss here falls through to the real GPU.
/// // The sweep records only enums that answered, so a constant that is missing from the table is one the device
/// // answered null for. Falling through there hands the question to the real GPU -- and the call log shows hCaptcha
/// // probing 552 distinct enums against a table of ~130, so that fall-through was the single largest hole in the
/// // whole spoof.
/// </code>
///
/// <para>
/// The four patches, in the same order: <c>getParameter</c> (table → value, a known enum with no value → <c>null</c>,
/// anything that is not a constant → the real implementation), <c>getSupportedExtensions</c>,
/// <c>getContextAttributes</c> (drop the keys the device does not report, then set the ones it does — "an extra key is
/// as much of a tell as a wrong value"), and <c>getShaderPrecisionFormat</c>. Plus the GPU-tier retry on
/// <c>getContext</c>: a host without a GPU refuses <c>failIfMajorPerformanceCaveat: true</c> and has to be retried
/// without it, because "the iPhone succeeds with true".
/// </para>
/// </summary>
public static class WebGlSurface
{
    /// <summary>The two context kinds, in the target's order.</summary>
    public static readonly string[] Kinds = { "webgl", "webgl2" };

    /// <summary>The four methods patched on each context prototype.</summary>
    public static readonly string[] Patched =
    {
        "getParameter", "getSupportedExtensions", "getContextAttributes", "getShaderPrecisionFormat",
    };

    /// <summary>The retry flag, and what it means.</summary>
    public const string CaveatFlag = "failIfMajorPerformanceCaveat";

    /// <summary>The layer.</summary>
    public static string BodyJs()
    {
        var kinds = string.Join(", ", Kinds.Select(k => "'" + k + "'"));

        return """
               // ---- webgl (R195) -----------------------------------------------------------------------
               // Every parameter the device answered, not a sample: a miss falls through to the real GPU, and that
               // fall-through was the largest hole in the whole spoof (552 distinct enums probed against a table of
               // ~130). Each patch below is the target's, in the target's order.
               (() => {
               try {
                 if (typeof WebGLRenderingContext === 'undefined') return;

                 const M = G.__nativeMask || {};
                 const install = (proto, name, build) => {
                   try {
                     const original = proto[name];
                     if (typeof original !== 'function') return;
                     const wrapped = { m() { return build.call(this, original, arguments); } }.m;
                     if (M.asNative) M.asNative(wrapped, name, original.length);
                     Object.defineProperty(proto, name,
                       { value: wrapped, writable: true, enumerable: false, configurable: true });
                   } catch (e) {}
                 };

                 const GL_PARAMS = __PARAMS__;
                 const GL_META = __META__;
                 const rebuild = (v) => (v && v.__typed) ? new (G[v.__typed] || Array)(v.values) : v;

                 [['webgl', G.WebGLRenderingContext], ['webgl2', G.WebGL2RenderingContext]].forEach(([kind, ctor]) => {
                   try {
                     if (!ctor || !GL_PARAMS[kind]) return;
                     const table = GL_PARAMS[kind];
                     const meta = GL_META[kind] || {};

                     // The sweep records only enums that answered, so a constant missing from the table is one the
                     // device answered null for. Collect the real constants so the two cases stay distinguishable.
                     const known = new Set();
                     Object.getOwnPropertyNames(ctor).forEach((name) => {
                       const enumValue = ctor[name];
                       if (typeof enumValue === 'number' && /^[A-Z][A-Z0-9_]*$/.test(name)) known.add(String(enumValue));
                     });

                     install(ctor.prototype, 'getParameter', function (original, args) {
                       const key = String(args[0]);
                       if (Object.prototype.hasOwnProperty.call(table, key)) return rebuild(table[key]);
                       // Anything that is not a constant at all (hCaptcha probes 0, 1, 2 to see how errors behave) is
                       // left to the real implementation, which returns null for an unknown enum just as WebKit does.
                       return known.has(key) ? null : original.apply(this, args);
                     });

                     install(ctor.prototype, 'getSupportedExtensions', function () {
                       return (meta.extensions || []).slice();
                     });

                     install(ctor.prototype, 'getContextAttributes', function (original, args) {
                       const real = original.apply(this, args) || {};
                       const wanted = meta.attributes || {};
                       // Blink exposes attributes WebKit does not (desynchronized, xrCompatible); an extra key is as
                       // much of a tell as a wrong value, so drop what the device does not report.
                       Object.keys(real).forEach((k) => { if (!(k in wanted)) { try { delete real[k]; } catch (e) {} } });
                       Object.keys(wanted).forEach((k) => { try { real[k] = wanted[k]; } catch (e) {} });
                       return real;
                     });

                     install(ctor.prototype, 'getShaderPrecisionFormat', function (original, args) {
                       const real = original.apply(this, args);
                       // The target's body validates against the table and returns the real object either way; the
                       // table's job here is to make a wrong answer visible, not to replace it.
                       const names = Object.keys(meta.precisions || {});
                       for (let i = 0; i < names.length; i++) {
                         const spec = meta.precisions[names[i]];
                         if (real && real.rangeMin === spec.rangeMin && real.rangeMax === spec.rangeMax) return real;
                       }
                       return real;
                     });
                   } catch (e) {}
                 });

                 // GPU tier: hsw asks with failIfMajorPerformanceCaveat: true first, falls back to false, and records
                 // which one worked. A real GPU -- and the iPhone -- succeed with true; a GPU-less host only with
                 // false. So a refused caveat request is retried without the flag.
                 [
                   typeof HTMLCanvasElement !== 'undefined' ? HTMLCanvasElement.prototype : null,
                   typeof OffscreenCanvas !== 'undefined' ? OffscreenCanvas.prototype : null,
                 ].forEach((proto) => {
                   if (!proto) return;
                   install(proto, 'getContext', function (original, args) {
                     const ctx = original.apply(this, args);
                     const opts = args[1];
                     if (ctx === null && /^(?:experimental-)?webgl2?$/.test(String(args[0]))
                         && opts && typeof opts === 'object' && opts.__CAVEAT__) {
                       return original.call(this, args[0],
                         Object.assign({}, opts, { __CAVEAT__: false }));
                     }
                     return ctx;
                   });
                 });
               } catch (e) {}
               })();
               """
            .Replace("__PARAMS__", WebGlTable.ParamsJs)
            .Replace("__META__", WebGlTable.MetaJs)
            .Replace("__CAVEAT__", CaveatFlag)
            .Replace("__KINDS__", "[" + kinds + "]");
    }

    /// <summary>The hole the full table closes.</summary>
    public const string Rule =
        "a miss here falls through to the real GPU ... that fall-through was the single largest hole in the whole spoof";

    /// <summary>Why the attributes are rebuilt rather than merged.</summary>
    public const string AttributeRule =
        "an extra key is as much of a tell as a wrong value, so drop what the device does not report";
}
