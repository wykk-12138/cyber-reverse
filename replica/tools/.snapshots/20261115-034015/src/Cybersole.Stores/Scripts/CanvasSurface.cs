namespace Cybersole.Stores.Scripts;

/// <summary>
/// Canvas read-back: the pixels this device actually produces, answered only for the program that produced them (R194).
///
/// <para>
/// The target's reasoning, kept because it is the design:
/// </para>
///
/// <code>
/// // A baked PNG is a picture of one draw program, so it may only answer for that program. The same hsw build ships a
/// // second 20x20 canvas painted with radial gradients and a 300x150 WebGL one — handing either of those the emoji
/// // picture contradicts what the caller itself just drew, which is louder than any engine tell.
/// // hsw's 96x48 program is fixed per BUILD ... so a picture may only answer for the exact program it is a picture of.
/// </code>
///
/// <para>
/// So the layer traces the draw calls and keys the answer on <c>geometry#signature</c> first, falling back to a
/// geometry-only table when the picture is "replayable" — text drawn, no gradient or pattern, which is the shape both
/// read-back programs have. Anything unknown falls through to the host's own pixels, which is honest.
/// </para>
///
/// <para>
/// <b>The 2x2 program</b> is the anti-aliased arc edge: Skia and CoreGraphics shade it differently and the device reads
/// <c>185/229/47</c> where Blink reads <c>192/244/53</c>. Keyed on the <c>arc(0,0,2,0,1,true)</c> CALL, not on pixels,
/// so the random-grey canary — a bare <c>fillRect</c> — passes through untouched.
/// </para>
/// </summary>
public static class CanvasSurface
{
    /// <summary>The draw calls whose arguments identify a program.</summary>
    public static readonly string[] Traced = { "fillText", "strokeText", "fillRect", "arc" };

    /// <summary>The calls that make a picture unreplayable: their output depends on the gradient itself.</summary>
    public static readonly string[] Complex = { "createLinearGradient", "createRadialGradient", "createConicGradient", "createPattern" };

    /// <summary>The 2x2 program's identifying call.</summary>
    public const string ArcProgram = "arc(0,0,2,0,1,true)";

    /// <summary>The layer.</summary>
    public static string BodyJs()
    {
        var traced = string.Join(", ", Traced.Select(n => "'" + n + "'"));
        var complex = string.Join(", ", Complex.Select(n => "'" + n + "'"));

        return """
               // ---- canvas read-back (R194) --------------------------------------------------------
               // A baked PNG is a picture of ONE draw program, so it answers only for that program: geometry AND the
               // exact call signature. Anything else falls through to the host's own pixels, which is honest.
               (() => {
               try {
                 if (typeof HTMLCanvasElement === 'undefined') return;
                 if (typeof CanvasRenderingContext2D === 'undefined') return;

                 const M = G.__nativeMask || {};
                 // R194: `M.method` is a FACTORY (it returns a proto-less function); the target''s `method()` is an
                 // INSTALLER. Using the factory as if it installed left every canvas patch uninstalled — measured: the
                 // 2x2 arc still read Blink''s 192/244/53. So the installer is spelled out here.
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

                 const CANVAS = __CANVAS__;
                 const PROGRAMS = __PROGRAMS__;
                 const BLINK_2X2 = __BLINK__;
                 const DEVICE_2X2 = __DEVICE__;

                 // Keyed on the exact canvas geometry. Answering for a canvas we did not measure is how a previous
                 // build returned a 20x20 PNG for a 300x150 canvas.
                 const shapeKey = (canvas) => canvas.width + 'x' + canvas.height + '|'
                   + (canvas.getAttribute('style') ? 1 : 0);

                 const DRAWN = new WeakMap();
                 const stateOf = (canvas) => {
                   let state = DRAWN.get(canvas);
                   if (!state) { state = { text: 0, complex: 0, arc2: 0, calls: 0, sig: '' }; DRAWN.set(canvas, state); }
                   return state;
                 };

                 const mark = (ctx, flag) => {
                   try {
                     const canvas = ctx && ctx.canvas;
                     if (!canvas) return;
                     stateOf(canvas)[flag] += 1;
                   } catch (e) {}
                 };

                 // The draw calls, in order, with their arguments: a program's identity.
                 const trace = (ctx, name, args) => {
                   try {
                     mark(ctx, 'calls');
                     const canvas = ctx && ctx.canvas;
                     if (!canvas) return;
                     stateOf(canvas).sig += name + '(' + Array.prototype.join.call(args, ',') + ')';
                   } catch (e) {}
                 };

                 ['fillText', 'strokeText'].forEach((name) => {
                   try {
                     install(CanvasRenderingContext2D.prototype, name, function (original, args) {
                       mark(this, 'text');
                       trace(this, name, args);
                       return original.apply(this, args);
                     });
                   } catch (e) {}
                 });

                 try {
                   install(CanvasRenderingContext2D.prototype, 'fillRect', function (original, args) {
                     // A fill over the whole canvas starts a new picture. hsw reuses one 2x2 canvas for the fixed arc
                     // program and then for the random-grey canary (a bare full fillRect); without this the arc mark
                     // outlived the arc and the canary was answered with the arc's pixels instead of its uniform grey.
                     try {
                       const c = this.canvas, state = c && DRAWN.get(c);
                       if (state && Number(args[0]) <= 0 && Number(args[1]) <= 0 &&
                           Number(args[0]) + Number(args[2]) >= c.width &&
                           Number(args[1]) + Number(args[3]) >= c.height) state.arc2 = 0;
                     } catch (e) {}
                     trace(this, 'fillRect', args);
                     return original.apply(this, args);
                   });
                 } catch (e) {}

                 __COMPLEX__.forEach((name) => {
                   try {
                     install(CanvasRenderingContext2D.prototype, name, function (original, args) {
                       mark(this, 'complex');
                       return original.apply(this, args);
                     });
                   } catch (e) {}
                 });

                 // hsw's fixed 2x2 program ends in arc(0, 0, 2, 0, 1, true); recognised by the CALL, not by the
                 // pixels the host produced, since those depend on whether the host rasterises on a GPU.
                 try {
                   install(CanvasRenderingContext2D.prototype, 'arc', function (original, args) {
                     try {
                       const c = this.canvas;
                       if (c && c.width === 2 && c.height === 2 && Number(args[0]) === 0 && Number(args[1]) === 0
                           && Number(args[2]) === 2) mark(this, 'arc2');
                     } catch (e) {}
                     trace(this, 'arc', args);
                     return original.apply(this, args);
                   });
                 } catch (e) {}

                 const replayable = (canvas) => {
                   const state = canvas && DRAWN.get(canvas);
                   return !!state && state.text > 0 && state.complex === 0;
                 };

                 try {
                   install(HTMLCanvasElement.prototype, 'toDataURL', function (original, args) {
                     const key = shapeKey(this);
                     const state = DRAWN.get(this);
                     const program = state && state.sig ? key + '#' + state.sig : null;
                     if (program && Object.prototype.hasOwnProperty.call(PROGRAMS, program)) return PROGRAMS[program];
                     return replayable(this) && Object.prototype.hasOwnProperty.call(CANVAS, key)
                       ? CANVAS[key] : original.apply(this, args);
                   });
                 } catch (e) {}

                 // getImageData has to agree with toDataURL or the pair contradicts itself. The capture stores a hash
                 // rather than pixels, so decode the PNG we are already returning and read it back -- same source, so
                 // the two can never disagree. Decoding is async and getImageData is not, hence the warm-up: probes
                 // that land before it completes fall through to the real pixels.
                 const PIXELS = new Map();
                 Object.keys(CANVAS).forEach((key) => {
                   try {
                     const image = new Image();
                     image.onload = function () {
                       try {
                         const scratch = document.createElement('canvas');
                         scratch.width = image.width;
                         scratch.height = image.height;
                         const ctx = scratch.getContext('2d');
                         ctx.drawImage(image, 0, 0);
                         PIXELS.set(key, ctx.getImageData(0, 0, image.width, image.height));
                       } catch (e) {}
                     };
                     image.src = CANVAS[key];
                   } catch (e) {}
                 });

                 try {
                   install(CanvasRenderingContext2D.prototype, 'getImageData', function (original, args) {
                     const canvas = this.canvas;
                     const cached = replayable(canvas) ? PIXELS.get(shapeKey(canvas)) : null;
                     // Only answer for a full-canvas read; a sub-rect would need cropping we cannot verify.
                     if (cached && Number(args[0]) === 0 && Number(args[1]) === 0
                         && Number(args[2]) === cached.width && Number(args[3]) === cached.height) {
                       try { return new ImageData(new Uint8ClampedArray(cached.data), cached.width, cached.height); }
                       catch (e) {}
                     }

                     const real = original.apply(this, args);
                     // Only the arc's anti-aliased edge varies: every iPhone run reads 185/229/47 where Blink reads
                     // 192/244/53 on a GPU desktop. Keyed on the arc call, so the grey canary passes untouched.
                     try {
                       const d = real && real.data;
                       const state = canvas && DRAWN.get(canvas);
                       if (d && d.length === 16 && real.width === 2 && real.height === 2 &&
                           ((state && state.arc2 > 0) || BLINK_2X2.every((v, i) => d[i] === v))) {
                         DEVICE_2X2.forEach((v, i) => { d[i] = v; });
                       }
                     } catch (e) {}
                     return real;
                   });
                 } catch (e) {}
               } catch (e) {}
               })();
               """
            .Replace("__CANVAS__", CanvasTable.CanvasJs)
            .Replace("__PROGRAMS__", CanvasTable.ProgramsJs)
            .Replace("__BLINK__", CanvasTable.Blink2x2Js)
            .Replace("__DEVICE__", CanvasTable.Device2x2Js)
            .Replace("__COMPLEX__", "[" + complex + "]")
            .Replace("__TRACED__", "[" + traced + "]");
    }

    /// <summary>Why the answer is keyed on the program.</summary>
    public const string Rule =
        "a baked PNG is a picture of one draw program, so it may only answer for that program";

    /// <summary>The 2x2 program in one sentence.</summary>
    public const string ArcRule =
        "every iPhone run reads 185/229/47 where Blink reads 192/244/53 on a GPU desktop";
}
