namespace Cybersole.Stores.Scripts;

/// <summary>
/// The device-only globals: the names the window list advertises and this engine never had (R193).
///
/// <para>
/// The target says why this layer exists, and it is the complement of the prune:
/// </para>
///
/// <code>
/// // Reproduced from the capture's globalTypes, not guessed. The window name list is answered from the device, so
/// // every name on it that this engine lacks was advertised with nothing behind it: listed by
/// // getOwnPropertyNames(window), `in` false, descriptor undefined. hsw asks for the `webkit` descriptor by name,
/// // and sweeps the tail of the list the same way.
/// </code>
///
/// <para>
/// R192 made that state reachable on purpose: the enumeration is now the device's 1062 names, so any name Blink lacks
/// is advertised without a backing property. Pass 1 builds the function-shaped names, pass 2 the booleans, the plain
/// values and the platform objects, and <c>webkit</c> gets a DATA property rather than an accessor — the target's
/// measurement is the reason: hsw keeps any window name whose value-or-getter is a native-looking function, so an
/// accessor-backed <c>webkit</c> would silently drop out of the suspicious-globals list, while the iPhone's
/// <c>webkit</c> is an OBJECT and is reported.
/// </para>
///
/// <para>
/// <b>One deliberate deviation.</b> The target's pass 2 writes its four kinds as sequential <c>if</c>s with no
/// <c>return</c> between them, so a row typed <c>"b"</c> or <c>"u"</c> falls through to the platform branch and is
/// overwritten with an object. In practice nothing reaches it (the twelve <c>_injected_*</c> names are installed by
/// <see cref="WindowBaseline"/> first, so <c>name in G</c> short-circuits), but <c>openDatabase</c> — typed
/// <c>"u"</c>, and absent from Blink — would end up an object where the device answers <c>typeof "undefined"</c>.
/// Each branch here returns, and the test measures the device's answer.
/// </para>
/// </summary>
public static class GlobalSurface
{
    /// <summary>The one name whose value-or-getter must not be a native-looking function.</summary>
    public const string InjectedDataProperty = "webkit";

    /// <summary>The one window method with an exact standard twin.</summary>
    public const string ForwardedMethod = "webkitCancelRequestAnimationFrame";

    /// <summary>The three passes, plus the WebKitNamespace member.</summary>
    public static string BodyJs()
    {
        var mainFrame = string.Join(", ", KeyOrderTable.MainFrameOnly.Select(n => "'" + n + "'"));

        return """
               // ---- device-only globals (R193) ----------------------------------------------------
               // The window list is the device's, so every name on it that this engine lacks has to EXIST, not just be
               // enumerable: "listed by getOwnPropertyNames(window), `in` false, descriptor undefined" is the tell.
               (() => {
               try {
                 const M = G.__nativeMask || {};
                 const asNative = M.asNative || ((fn) => fn);
                 const methodOf = M.method || ((impl, name) => impl);

                 const GLOBAL_KINDS = __KINDS__;
                 const GLOBAL_NOT_FN = new Set(__NOTFN__);
                 const INJECTED_GLOBALS = new Set(__INJECTED__);
                 const names = G.__windowNames || {};
                 const WINDOW_ALL = names.all || [];
                 const ENUMERABLE = new Set(names.enum || []);
                 const MAIN_FRAME_ONLY = new Set([__MAIN_FRAME__]);
                 const FRAMED = !!(G.__windowBaseline && G.__windowBaseline.framed);

                 const MADE = Object.create(null);

                 const value = (target, name, v, enumerable) => {
                   try {
                     Object.defineProperty(target, name,
                       { value: v, writable: true, enumerable: !!enumerable, configurable: true });
                   } catch (e) {}
                 };

                 const hiddenCtor = (name) => {
                   const Ctor = function () {};
                   try { Object.defineProperty(Ctor, 'name', { value: name, configurable: true }); } catch (e) {}
                   asNative(Ctor, name, 0);
                   return Ctor;
                 };

                 // Pass 1: functions. Interface objects first, so the instances in pass 2 can hang off their prototypes.
                 WINDOW_ALL.forEach((name) => {
                   try {
                     if (name in G || GLOBAL_NOT_FN.has(name)
                         || Object.prototype.hasOwnProperty.call(GLOBAL_KINDS, name)) return;

                     if (/^[A-Z]/.test(name)) {
                       const Ctor = function () { throw new TypeError('Illegal constructor'); };
                       Object.defineProperty(Ctor, 'name', { value: name, configurable: true });
                       Object.defineProperty(Ctor, 'length', { value: 0, configurable: true });
                       asNative(Ctor, name, 0);
                       Object.defineProperty(Ctor.prototype, Symbol.toStringTag,
                         { value: name, configurable: true });
                       Object.defineProperty(Ctor, 'prototype', { writable: false });
                       Object.defineProperty(G, name,
                         { value: Ctor, writable: true, enumerable: false, configurable: true });
                       MADE[name] = Ctor;
                       return;
                     }

                     // A window method the device has and this engine does not. The one with an exact standard twin
                     // forwards to it; the rest answer the way a call with no usable argument does.
                     const twin = name === '__TWIN__' ? G.cancelAnimationFrame : null;
                     const fn = methodOf(twin
                       ? function (id) { return twin.call(G, id); }
                       : function () { return null; }, name);
                     Object.defineProperty(fn, 'length', { value: twin ? 1 : 0, configurable: true });
                     Object.defineProperty(G, name,
                       { value: fn, writable: true, enumerable: ENUMERABLE.has(name), configurable: true });
                   } catch (e) {}
                 });

                 // Interface inheritance, for the two families whose parent is unambiguous from the name.
                 Object.keys(MADE).forEach((name) => {
                   try {
                     let parent = null;
                     if (name !== 'SVGPathSeg' && name !== 'SVGPathSegList' && name.indexOf('SVGPathSeg') === 0) {
                       parent = G.SVGPathSeg;
                     } else if (name === 'XMLHttpRequestProgressEvent') {
                       parent = G.ProgressEvent;
                     } else if (/Event$/.test(name)) {
                       parent = G.Event;
                     }
                     if (typeof parent !== 'function') return;
                     Object.setPrototypeOf(MADE[name], parent);
                     Object.setPrototypeOf(MADE[name].prototype, parent.prototype);
                   } catch (e) {}
                 });

                 // Pass 2: booleans, plain values and instances. Each branch returns — see the deviation note on
                 // this body: the target's four sequential ifs let a "b"/"u" row fall through to the platform branch.
                 Object.keys(GLOBAL_KINDS).forEach((name) => {
                   try {
                     if (name in G || (FRAMED && MAIN_FRAME_ONLY.has(name))) return;
                     const row = GLOBAL_KINDS[name];
                     if (row === undefined || row === null) return;

                     if (row === 'b') {
                       value(G, name, true, ENUMERABLE.has(name));
                       return;
                     }

                     if (row === 'u') {
                       // Callable on the device, but typeof says 'undefined'. Script cannot build such an object; an
                       // own property holding undefined answers the two things a page can ask of it -- `in` and
                       // typeof -- the way the device does.
                       value(G, name, undefined, ENUMERABLE.has(name));
                       return;
                     }

                     if (Object.prototype.hasOwnProperty.call(row, 'n')) {
                       value(G, name, row.n, ENUMERABLE.has(name));
                       return;
                     }

                     if (row.tag === 'Object') {
                       // A script object: plain, or an instance of a script class (minified name and all).
                       const inst = row.ctor && row.ctor !== 'Object'
                         ? Object.create(hiddenCtor(row.ctor).prototype) : {};
                       value(G, name, inst, ENUMERABLE.has(name));
                       return;
                     }

                     // A platform object. Its constructor is the device global of that name when there is one, and
                     // otherwise exists without ever being exposed -- so `x.constructor.name` answers while
                     // `window.PushManager` stays undefined, which is what the device does.
                     let Ctor = MADE[row.ctor];
                     if (!Ctor) {
                       Ctor = hiddenCtor(row.ctor);
                       Object.defineProperty(Ctor.prototype, Symbol.toStringTag,
                         { value: row.tag, configurable: true });
                     }

                     // INJECTED, not standard: WKWebView and Chrome-iOS set these on the window as plain own DATA
                     // properties. Every other name on this branch is a standard [Global] IDL attribute, which really
                     // is an accessor -- and an accessor-backed `webkit` hands hsw's sweep a native-looking getter,
                     // passes it, and drops out of the suspicious-globals list. The iPhone's `webkit` is an OBJECT,
                     // fails the sweep, and is reported.
                     if (INJECTED_GLOBALS.has(name)) {
                       Object.defineProperty(G, name, {
                         value: Object.create(Ctor.prototype),
                         writable: true,
                         enumerable: ENUMERABLE.has(name) || (name === 'webkit' && !FRAMED),
                         configurable: true,
                       });
                       return;
                     }

                     value(G, name, Object.create(Ctor.prototype), ENUMERABLE.has(name));
                   } catch (e) {}
                 });

                 // Pass 3 was here in R193: the not-function names the engine lacks were filled with
                 // `{ value: null, writable: true }`. R196 removed it — the target is explicit that an event-handler
                 // attribute is an ACCESSOR pair and that a null data slot "answers the descriptor probes with a shape
                 // no engine gives a handler". HandlerSurface installs the 131 accessor pairs instead.
                 // WebKitNamespace has exactly one member, and it is the reason the object exists.
                 try {
                   if (MADE.WebKitNamespace && MADE.UserMessageHandlersNamespace && G.webkit
                       && !('messageHandlers' in MADE.WebKitNamespace.prototype)) {
                     value(MADE.WebKitNamespace.prototype, 'messageHandlers',
                       Object.create(MADE.UserMessageHandlersNamespace.prototype));
                   }
                 } catch (e) {}
               } catch (e) {}
               })();
               """
            .Replace("__KINDS__", GlobalSurfaceTable.KindsJs)
            .Replace("__NOTFN__", GlobalSurfaceTable.NotFunctionJs)
            .Replace("__INJECTED__", GlobalSurfaceTable.InjectedGlobalsJs)
            .Replace("__MAIN_FRAME__", mainFrame)
            .Replace("__TWIN__", ForwardedMethod);
    }

    /// <summary>The tell this layer removes, in the target's words.</summary>
    public const string Rule =
        "every name on it that this engine lacks was advertised with nothing behind it: listed by "
        + "getOwnPropertyNames(window), `in` false, descriptor undefined";

    /// <summary>Why `webkit` is a data property.</summary>
    public const string WebkitRule =
        "an accessor-backed `webkit` hands the sweep a native-looking getter, passes it, and drops out of the "
        + "suspicious-globals list; the iPhone's `webkit` is an OBJECT and is reported";
}
