using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Two shims the image builds by <b>forwarding</b> rather than simulating (R170).
///
/// <para>
/// The note that settles the credentials question is longer than most and says three things the replica had wrong:
/// </para>
///
/// <code>
/// // Chrome for iOS does not expose WebKit's CredentialsContainer to the page. Its passkey script
/// // (components/webauthn/ios/resources/passkey_controller.ts, injected into every frame) caches the native one and
/// // then runs Object.defineProperty(navigator, 'credentials', {value: credentialsContainer}) — an OWN property of
/// // the navigator INSTANCE, non-enumerable, non-writable and non-configurable, holding a plain object of four script
/// // functions. Two things follow on the device and both were wrong here:
/// //   - for (k in navigator) SKIPS credentials, because a non-enumerable own property shadows the enumerable one on
/// //     the prototype. hCaptcha ships that loop verbatim as topLevel.nv: the device sends 32 keys, this engine sent
/// //     33 with credentials: {} after audioSession.
/// //   - the value is a plain Object whose methods print script source, not an [object CredentialsContainer] whose
/// //     methods print [native code].
/// </code>
///
/// <para>
/// So the original does <b>not</b> implement WebAuthn at all: it takes the engine's own container, wraps each of four
/// methods in a function that forwards to it, and cloaks the source. That is a smaller and more faithful answer than a
/// virtual authenticator, and it is the one this round builds.
/// </para>
///
/// <para>
/// <c>canShare</c> and <c>share</c> are the same idea in a different place: Web Share is not exposed in this build, so
/// they are appended as <b>data properties</b> (WebIDL operations are data properties; an accessor would be wrong),
/// <c>canShare</c> answers a predicate, and <c>share</c> rejects with the message WebKit actually produces outside a
/// transient activation.
/// </para>
/// </summary>
public static class ForwardingShims
{
    /// <summary>The four credentials entries, name and arity, from the image's <c>CRED_SHIM</c>.</summary>
    public static readonly IReadOnlyList<(string Name, int Length)> Credentials = new[]
    {
        ("get", 1), ("create", 1), ("preventSilentAccess", 0), ("store", 1),
    };

    /// <summary>The two Web Share operations, name and arity.</summary>
    public static readonly IReadOnlyList<(string Name, int Length)> WebShare = new[]
    {
        ("canShare", 1), ("share", 1),
    };

    /// <summary>
    /// The credentials shim: an own, non-enumerable property of the instance, holding four plain functions that forward
    /// to whatever container the engine already has.
    /// </summary>
    public static string CredentialsBodyJs()
    {
        var rows = string.Join(", ",
            Credentials.Select(c => "{ name: '" + c.Name + "', length: " + c.Length + " }"));

        return """
               // ---- credentials (R170) ---------------------------------------------------------
               // An own property of the INSTANCE: non-enumerable, so `for (k in navigator)` skips it exactly as the
               // device's does (32 keys, not 33). The four methods forward to the engine's own container, so they
               // behave; the mask makes them print [native code] like the engine's do.
               try {
                 const nav = G.navigator;
                 if (nav && !Object.prototype.hasOwnProperty.call(nav, 'credentials')) {
                   let native;
                   try { native = nav.credentials; } catch (e) { native = undefined; }

                   const shim = {};
                   [__ROWS__].forEach((row) => {
                     const fn = function () {
                       const target = native && native[row.name];
                       if (typeof target !== 'function') {
                         return Promise.reject(new TypeError('navigator.credentials is unavailable'));
                       }
                       return target.apply(native, arguments);
                     };
                     Object.defineProperty(fn, 'name', { value: row.name, configurable: true });
                     Object.defineProperty(fn, 'length', { value: row.length, configurable: true });
                     try {
                       const M = G.__nativeMask;
                       if (M) M.asNative(fn, row.name, row.length);
                     } catch (e) {}
                     shim[row.name] = fn;
                   });

                   // The prototype member stays too, as the image says: "The prototype member stays, so
                   // getOwnPropertyNames(Navigator.prototype) keeps the device's 41 names." This engine has no
                   // container on the prototype at all, so one is defined before the own property shadows it.
                   const proto = Object.getPrototypeOf(nav);
                   if (proto && !('credentials' in proto)) {
                     try {
                       Object.defineProperty(proto, 'credentials',
                         { value: shim, writable: true, configurable: true, enumerable: true });
                     } catch (e) {}
                   }

                   // no writable/configurable/enumerable in the descriptor: the defaults are false, which is what the
                   // device's own property has
                   Object.defineProperty(nav, 'credentials', { value: shim });
                 }
               } catch (e) {}
               """.Replace("__ROWS__", rows);
    }

    /// <summary>
    /// The Web Share pair: data properties, not accessors, appended after everything else on the prototype.
    /// </summary>
    public static string WebShareBodyJs()
    {
        return """
               // ---- canShare / share (R170) ----------------------------------------------------
               // Web Share is not exposed in this build, so the device's two operations are built here and appended:
               // they are the last two OWN names in the captured order, and a fresh definition appends.
               //
               // WebIDL operations are DATA properties — value() installs a brand-checked accessor, which is right for
               // attributes like audioSession and wrong here — so these are defined directly.
               try {
                 const proto = G.Navigator && G.Navigator.prototype;
                 if (proto) {
                   [['canShare', 1], ['share', 1]].forEach((pair) => {
                     const name = pair[0], arity = pair[1];
                     if (name in proto) return;

                     // R171: a METHOD SHORTHAND has no prototype, which is what a WebIDL operation looks like
                     const build = (G.__nativeMask && G.__nativeMask.method) || ((impl, n) => impl);
                     const fn = build(function () {
                       const data = arguments[0];
                       const shareable = !!data && typeof data === 'object'
                         && ('url' in data || 'text' in data || 'title' in data || 'files' in data);
                       if (name === 'canShare') return shareable;

                       // WebKit rejects share() outside a transient user activation, which is the state any headless
                       // read of it sees on the device too.
                       return Promise.reject(new DOMException(
                         'The request is not allowed by the user agent or the platform in the current context.',
                         'NotAllowedError'));
                     }, name);

                     Object.defineProperty(fn, 'name', { value: name, configurable: true });
                     Object.defineProperty(fn, 'length', { value: arity, configurable: true });
                     try {
                       const M = G.__nativeMask;
                       if (M) M.asNative(fn, name, arity);
                     } catch (e) {}

                     Object.defineProperty(proto, name,
                       { value: fn, writable: true, configurable: true, enumerable: true });
                   });
                 }
               } catch (e) {}
               """;
    }

    /// <summary>The message WebKit's <c>share</c> rejects with outside a transient activation.</summary>
    public const string ShareRejection =
        "The request is not allowed by the user agent or the platform in the current context.";

    /// <summary>The DOMException name that rejection carries.</summary>
    public const string ShareRejectionName = "NotAllowedError";

    /// <summary>The key counts the image measured: the device sends 32, an engine with a stray <c>credentials: {}</c> sent 33.</summary>
    public const int DeviceForInKeys = 32;

    /// <summary>The reason the credentials shim is an own property rather than a prototype member.</summary>
    public const string OwnPropertyReason =
        "a non-enumerable own property shadows the enumerable one on the prototype, so for-in skips it exactly as the "
        + "device's does — 32 keys, not 33";
}
