using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The masking half of a shim, read from the image's <c>CRED_SHIM</c> in R160.
///
/// <para>
/// The capture carries entries like
/// </para>
///
/// <code>
/// {"name": "get", "length": 1, "src": "function(e){if(!e?.publicKey){return O.get(e)}…"}
/// </code>
///
/// <para>
/// A shim is two things: what it does, and what it <b>says it is</b>. <c>Function.prototype.toString</c> reads the
/// second, so a patched <c>navigator.credentials.get</c> or a patched <c>plugins</c> getter that answers
/// <c>function () { … }</c> is a shim announcing itself. That is why the capture records a <c>length</c> and a
/// <c>src</c> next to every fake: both fields are readable, and both are read.
/// </para>
///
/// <para>
/// The replica patched <c>getVoices</c>, <c>createEvent</c> and several getters and never masked any of them. This
/// class supplies the mechanism — a registry of fakes and one override of <c>Function.prototype.toString</c> — so a
/// patch and its mask are written together or not at all.
/// </para>
/// </summary>
public static class NativeMask
{
    /// <summary>
    /// The shape V8 prints for a native: one line, <c>{ [native code] }</c>. Captured from the image (R172) as
    /// <c>/^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$/</c>.
    /// </summary>
    public const string V8Native = @"^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$";

    /// <summary>
    /// V8 writes an accessor's role into its source — <c>function get navigation() { … }</c> — and the device does not.
    /// Captured as <c>/^function (?:get|set) (?=[^\s(])/</c>; the lookahead is what leaves a function genuinely named
    /// <c>get</c> (<c>Map.prototype.get</c>) alone.
    /// </summary>
    public const string V8Accessor = @"^function (?:get|set) (?=[^\s(])";

    /// <summary>
    /// The text WebKit answers with: the same name, then a newline and four spaces. R172's finding is that the cloak
    /// <b>reformats</b> V8's one-line form into this one, because the profile claims a WebKit engine.
    /// </summary>
    public static string WebKitText(string name) => "function " + name + "() {\n    [native code]\n}";

    /// <summary>The text a native function answers with, per name, in the engine the profile claims.</summary>
    public static string NativeText(string name) => WebKitText(name);

    /// <summary>
    /// The statements that install the registry and the override.
    ///
    /// <para>
    /// <c>asNative(fn, name)</c> records the fake and fixes its <c>name</c> and <c>length</c>;
    /// <c>maskGetter(target, prop, name)</c> does the same for a property getter, which is how a patched
    /// <c>navigator.plugins</c> stops announcing itself.
    /// </para>
    /// </summary>
    public static string BodyJs()
    {
        return """
               // ---- native masking (R160) -------------------------------------------------------
               // A patch is two things: behaviour, and what Function.prototype.toString reports. The image's
               // CRED_SHIM records { name, length, src } next to every fake, which is only worth recording because
               // a detector reads all three.
               (() => {
                 if (!G || G.__nativeMaskInstalled) return;
                 try { Object.defineProperty(G, '__nativeMaskInstalled', { value: true }); } catch (e) { return; }

                 // R190: ONE cloak table per page, not one per realm. A child realm re-runs this body and would
                 // otherwise keep its own WeakMap — measured: the child's own `getComputedStyle` came back as one
                 // line of real source when read through the parent's (cloaked) toString, because the parent's map
                 // had never heard of the child's function. Sharing the top realm's map is what the target's single
                 // closure does.
                 const FAKES = (() => {
                   try {
                     const top = G.top;
                     if (top && top !== G && top.__nativeMask && top.__nativeMask.fakes) return top.__nativeMask.fakes;
                   } catch (e) {}
                   return new WeakMap();
                 })();
                 const protoToString = Function.prototype.toString;

                 const asNative = (fn, name, length) => {
                   if (typeof fn !== 'function') return fn;
                   try {
                     Object.defineProperty(fn, 'name', { value: name, configurable: true });
                     Object.defineProperty(fn, 'length', { value: length === undefined ? 0 : length, configurable: true });
                     // the device does not write an accessor's role into its source, so `get userAgent` is cloaked as
                     // `function userAgent() { … }` — the same rewrite the real cloak applies to untouched natives (R172/R173)
                     const base = name.indexOf('get ') === 0 ? name.slice(4)
                       : (name.indexOf('set ') === 0 ? name.slice(4) : name);
                     FAKES.set(fn, 'function ' + base + '() {\n    [native code]\n}');
                   } catch (e) {}
                   return fn;
                 };

                 // R171: the image builds its shims from METHOD SHORTHANDS, not from plain functions:
                 //
                 //   const renamed = (fn, name) => { try { Object.defineProperty(fn, 'name', { value: name || '',
                 //     configurable: true }); } catch (e) { } return fn; };
                 //   const noProtoMethod = (impl, name) => renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
                 //   const noProtoGetter = (impl, name) => renamed(Object.getOwnPropertyDescriptor(
                 //     { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');
                 //
                 // The trick is in the syntax: `{ m() {} }.m` is an ordinary function expression in every respect except
                 // that it has NO `prototype` property, which is exactly what a WebIDL operation looks like. `delete
                 // fn.prototype` also works, but a shorthand never creates one.
                 const renamed = (fn, name) => {
                   try { Object.defineProperty(fn, 'name', { value: name || '', configurable: true }); } catch (e) {}
                   return fn;
                 };
                 const noProtoMethod = (impl, name) =>
                   renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
                 const noProtoGetter = (impl, name) =>
                   renamed(Object.getOwnPropertyDescriptor(
                     { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');

                                // R172: the cloak REFORMATS rather than answering from a table. V8 prints
                 //   function get userAgent() { [native code] }
                 // and the device prints
                 //   function userAgent() {
                 //       [native code]
                 //   }
                 // so a source that matches V8's native shape is rewritten into WebKit's, and an accessor's role
                 // (the `get `/`set ` word) is dropped. Anything else passes through untouched, which is what keeps a
                 // page's own functions printing their own code.
                 const V8_NATIVE = /^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$/;
                 const V8_ACCESSOR = /^function (?:get|set) (?=[^\s(])/;

                 // a METHOD SHORTHAND, so `'prototype' in Function.prototype.toString` answers false, as the real one
                 // does — hsw's [ctor, prop] sweep records exactly that predicate, ~110 reads per solve
                 const masked = {
                   toString() {
                     const fake = FAKES.get(this);
                     if (fake !== undefined) return fake;

                     const real = protoToString.call(this);
                     const match = V8_NATIVE.exec(real);
                     return match
                       ? match[1].replace(V8_ACCESSOR, 'function ') + ' {\n    [native code]\n}'
                       : real;
                   },
                 }.toString;

                 renamed(masked, 'toString');
                 try { Object.defineProperty(masked, 'length',
                   { value: protoToString.length, configurable: true }); } catch (e) {}
                 FAKES.set(masked, 'function toString() {\n    [native code]\n}');
                 try {
                   Object.defineProperty(Function.prototype, 'toString',
                     { value: masked, writable: true, configurable: true, enumerable: false });
                 } catch (e) {}

                 const maskGetter = (target, prop, name) => {
                   try {
                     const d = Object.getOwnPropertyDescriptor(target, prop);
                     if (!d || !d.get) return;
                     asNative(d.get, name || ('get ' + prop), 0);
                   } catch (e) {}
                 };

                 const maskProps = (target, names) => {
                   (names || []).forEach((n) => maskGetter(target, n));
                 };


                 // exported last: everything above must exist first — the same temporal-dead-zone rule the
                 // image's own note states, and the rule this round broke twice.
                 G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter, fakes: FAKES };

               })();
               """;
    }

    /// <summary>The functions the replica patches and must therefore mask, by name.</summary>
    public static readonly IReadOnlyList<string> MaskedFunctions = new[]
    {
        "getVoices", "createEvent", "getParameter",
    };

    /// <summary>The getters the replica installs and must therefore mask.</summary>
    public static readonly IReadOnlyList<string> MaskedGetters = new[]
    {
        "plugins", "mimeTypes", "connection", "maxTouchPoints", "hardwareConcurrency",
        "deviceMemory", "outerWidth", "outerHeight", "innerWidth", "innerHeight",
        "clientWidth", "clientHeight", "devicePixelRatio",
    };

    /// <summary>The rule: a patch and its mask are written together or not at all.</summary>
    public const string Rule =
        "a shim that does not mask its toString is a shim announcing itself; the image records name, length "
        + "and src next to every fake because all three are readable";

    /// <summary>True when a patched name has to be masked.</summary>
    public static bool NeedsMask(string? name) =>
        !string.IsNullOrEmpty(name)
        && (MaskedFunctions.Contains(name) || MaskedGetters.Contains(name));
}
