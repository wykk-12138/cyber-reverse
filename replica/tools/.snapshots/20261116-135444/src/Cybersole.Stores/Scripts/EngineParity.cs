using System.Collections.Generic;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The engine-parity layer: V8 and JavaScriptCore word the same failures differently, and a profile claiming WebKit has
/// to produce WebKit's words (R179).
///
/// <para>
/// The capture's <c>MESSAGES</c> table is four strings, and each one is a place where Blink's sentence would give the
/// claim away:
/// </para>
///
/// <code>
/// const MESSAGES = {
///   "nullProp": "null is not an object (evaluating 'null.x')",
///   "notFunction": "(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
///   "badArrayLength": "Array length must be a positive integer of safe magnitude.",
///   "jsonCircular": "JSON.stringify cannot serialize cyclic structures."
/// };
/// </code>
///
/// <para>
/// Three patches follow from it, plus two that are not messages at all:
/// </para>
///
/// <list type="number">
/// <item><b>Stacks.</b> V8 renders <c>    at fn (url:line:col)</c>; JSC renders <c>fn@url:line:col</c>. One regex
/// rewrites the first into the second, and it runs over every constructed error.</item>
/// <item><b>The <c>stack</c> descriptor.</b> V8 installs <c>stack</c> as an own ACCESSOR on the error; JSC leaves a
/// writable data property. <c>Error.prepareStackTrace</c> would reformat too, but assigning it makes
/// <c>typeof Error.prepareStackTrace</c> report <c>'function'</c> where the device says <c>'undefined'</c> — trading
/// one tell for another. Wrapping construction avoids that.</item>
/// <item><b>Array length.</b> <c>new Array(-1)</c> and friends produce a WebKit sentence about "safe magnitude".</item>
/// <item><b>Bound functions.</b> V8 names them <c>"function bound () {…}"</c>; JSC does not. One line to match.</item>
/// <item><b><c>Error.stackTraceLimit</c></b> — V8 defaults to 10, JSC to 100. One assignment.</item>
/// </list>
///
/// <para>
/// The capture is explicit that this trades completeness for shape: <i>Errors the engine throws itself (null.x) never
/// pass through here, so they keep V8's accessor. A probe that compares a thrown error against a constructed one can
/// still tell — but hCaptcha's own probe constructs.</i>
/// </para>
/// </summary>
public static class EngineParity
{
    /// <summary>The four messages, verbatim.</summary>
    public static readonly IReadOnlyDictionary<string, string> Messages = new Dictionary<string, string>
    {
        ["nullProp"] = "null is not an object (evaluating 'null.x')",
        ["notFunction"] = "(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
        ["badArrayLength"] = "Array length must be a positive integer of safe magnitude.",
        ["jsonCircular"] = "JSON.stringify cannot serialize cyclic structures.",
    };

    /// <summary>The error constructors the capture wraps, in its order.</summary>
    public static readonly IReadOnlyList<string> Wrapped = new[]
    {
        "Error", "TypeError", "RangeError", "SyntaxError", "ReferenceError", "EvalError", "URIError",
    };

    /// <summary>The stack frame shape V8 produces, and the one JSC produces.</summary>
    public const string V8Frame = @"^\s*at (?:(.+?) \()?(.+?)\)?$";

    /// <inheritdoc cref="V8Frame"/>
    public const string JscFrame = "fn@url:line:col";

    /// <summary>The default V8 limit, and the device's.</summary>
    public const int V8StackTraceLimit = 10;

    /// <inheritdoc cref="V8StackTraceLimit"/>
    public const int DeviceStackTraceLimit = 100;

    /// <summary>The whole layer: messages, stack rewrite, error wrappers, Array length, JSON cyclic, bind, limit.</summary>
    public static string BodyJs()
    {
        return """
               // ---- engine parity (R179) ---------------------------------------------------------
               // V8 and JavaScriptCore word the same failures differently. A profile claiming WebKit has to produce
               // WebKit's words, its stack format, and its `stack` descriptor.
               (() => {
                 try {
                   const MESSAGES = {
                     nullProp: "null is not an object (evaluating 'null.x')",
                     notFunction: "(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
                     badArrayLength: "Array length must be a positive integer of safe magnitude.",
                     jsonCircular: "JSON.stringify cannot serialize cyclic structures.",
                   };

                   const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
                   let ELIDE = null;

                   // V8: "    at fn (url:line:col)"   JSC: "fn@url:line:col"
                   const toJscStack = (raw) => {
                     const out = [];
                     String(raw).split('\n').forEach((line) => {
                       const match = /^\s*at (?:(.+?) \()?(.+?)\)?$/.exec(line);
                       if (match) out.push((match[1] || '') + '@' + match[2]);
                     });
                     return out.join('\n');
                   };

                   // One assignment each: JSC's default limit, and the bound-function naming V8 adds and JSC does not.
                   try { Error.stackTraceLimit = 100; } catch (e) {}

                   try {
                     const protoBind = Function.prototype.bind;
                     if (typeof protoBind === 'function') {
                       const bound = {
                         bind() {
                           const fn = protoBind.apply(this, arguments);
                           try {
                             const M = G.__nativeMask;
                             if (M && M.asNative) M.asNative(fn, '');
                           } catch (e) {}
                           return fn;
                         },
                       }.bind;
                       try {
                         const M = G.__nativeMask;
                         if (M && M.asNative) M.asNative(bound, 'bind', protoBind.length);
                       } catch (e) {}
                       Function.prototype.bind = bound;
                     }
                   } catch (e) {}

                   // Array length: the sentence belongs to WebKit, and the wrapper keeps identity intact.
                   try {
                     const RealArray = Array;
                     // constructible, for the same reason the error wrappers are
                     const ArrayWrapped = function Array(...args) {
                       if (args.length === 1 && typeof args[0] === 'number'
                           && (args[0] < 0 || args[0] > 4294967295 || args[0] % 1 !== 0)) {
                         throw new RangeError(MESSAGES.badArrayLength);
                       }
                       return Reflect.construct(RealArray, args, new.target || RealArray);
                     };

                     ArrayWrapped.prototype = RealArray.prototype;
                     Object.getOwnPropertyNames(RealArray).forEach((key) => {
                       if (key === 'prototype' || key === 'name' || key === 'length') return;
                       try { ArrayWrapped[key] = RealArray[key]; } catch (e) {}
                     });
                     Object.defineProperty(ArrayWrapped, 'name', { value: 'Array', configurable: true });
                     Object.defineProperty(ArrayWrapped, 'length', { value: 1, configurable: true });
                     try {
                       const M = G.__nativeMask;
                       if (M && M.asNative) M.asNative(ArrayWrapped, 'Array');
                     } catch (e) {}
                     try {
                       Object.defineProperty(RealArray.prototype, 'constructor',
                         { value: ArrayWrapped, writable: true, configurable: true });
                     } catch (e) {}
                     G.Array = ArrayWrapped;
                   } catch (e) {}

                   // JSON.stringify: only the cyclic-structure case is reworded; every other failure keeps its error.
                   try {
                     const original = JSON.stringify;
                     if (typeof original === 'function') {
                       const wrapped = {
                         stringify() {
                           try {
                             return original.apply(this, arguments);
                           } catch (error) {
                             if (error instanceof TypeError && /circular|cyclic/i.test(String(error.message))) {
                               throw new TypeError(MESSAGES.jsonCircular);
                             }
                             throw error;
                           }
                         },
                       }.stringify;
                       try {
                         const M = G.__nativeMask;
                         if (M && M.asNative) M.asNative(wrapped, 'stringify', original.length);
                       } catch (e) {}
                       JSON.stringify = wrapped;
                     }
                   } catch (e) {}

                   // The error constructors: `stack` becomes a writable data property in JSC's format, and the ELIDE
                   // hook from the brand check is honoured here rather than by inventing a frame.
                   ['Error', 'TypeError', 'RangeError', 'SyntaxError', 'ReferenceError', 'EvalError', 'URIError']
                     .forEach((name) => {
                       try {
                         const Original = G[name];
                         if (typeof Original !== 'function') return;

                         // a function EXPRESSION, not a method shorthand: an error constructor must be
                         // constructible, and a shorthand has no [[Construct]] (measured: 'Error is not a
                         // constructor')
                         const Wrapped = function (...args) {
                           const error = new.target
                             ? Reflect.construct(Original, args, new.target)
                             : Original(...args);
                           try {
                             const elide = ELIDE;
                             ELIDE = null;
                             let head = '';
                             if (elide && nativeCapture) {
                               try {
                                 nativeCapture(error, elide[0]);
                                 head = elide[1];
                               } catch (e) {}
                             }
                             const body = toJscStack(error.stack);
                             Object.defineProperty(error, 'stack', {
                               value: head ? (body ? head + '\n' + body : head) : body,
                               writable: true, configurable: true, enumerable: false,
                             });
                           } catch (e) {}
                           return error;
                         };

                         // identity survives: instanceof, .constructor and the statics all still work
                         Wrapped.prototype = Original.prototype;
                         Object.getOwnPropertyNames(Original).forEach((key) => {
                           try { Wrapped[key] = Original[key]; } catch (e) {}
                         });
                         Object.defineProperty(Wrapped, 'name', { value: name, configurable: true });
                         Object.defineProperty(Wrapped, 'length',
                           { value: Original.length, configurable: true });
                         try {
                           const M = G.__nativeMask;
                           if (M && M.asNative) M.asNative(Wrapped, name, Original.length);
                         } catch (e) {}
                         G[name] = Wrapped;
                       } catch (e) {}
                     });
                 } catch (e) {}
               })();
               """;
    }

    /// <summary>What the layer buys, and what it deliberately does not.</summary>
    public const string Rule =
        "errors the engine throws itself never pass through the wrapper, so they keep V8's accessor — a probe that "
        + "compares a thrown error against a constructed one can still tell, but hCaptcha's own probe constructs";
}
