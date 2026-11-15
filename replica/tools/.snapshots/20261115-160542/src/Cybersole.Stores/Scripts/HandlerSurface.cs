using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The event-handler attributes, as accessor pairs — plus three one-line corrections from the same block (R196).
///
/// <para>
/// This is a correction of R193. That round filled in the not-function names as <c>{ value: null }</c> data slots, and
/// the target says exactly why that shape is wrong:
/// </para>
///
/// <code>
/// They are installed as ACCESSORS, not as data slots holding null. An event-handler IDL attribute on a [Global]
/// interface is an accessor pair on the global object in both engines, and hsw does not stop at `in`: it calls
/// getOwnPropertyDescriptor on ontouchstart / ontouchend / ontouchmove / ontouchcancel / ontouchforcechange and on the
/// handlers at the tail of the window list, then reads .value AND .get of each result and the getter's source.
/// A `{value: null, writable: true}` slot answers that with a shape no engine gives a handler.
/// </code>
///
/// <para>
/// And why the names have to exist at all — the gate that decides whether hsw spawns a worker:
/// </para>
///
/// <code>
/// aK_ = ('ontouchstart' in window);  lK = uS &amp;&amp; aK_ &amp;&amp; &lt;ua not Safari-shaped&gt;;  QW = nW || lK
/// With aK_ false the gate opens and we spawn a worker a real iPhone never spawns.
/// </code>
/// </summary>
public static class HandlerSurface
{
    /// <summary>The brand-check message, verbatim from the target's construction.</summary>
    public const string BrandMessage = "The Window.{0} {1} can only be used on instances of Window";

    /// <summary>The three corrections that share this block.</summary>
    public static readonly string[] Corrections =
    {
        "createEvent('TouchEvent') returns new TouchEvent('')",
        "webkitIndexedDB aliases indexedDB",
        "delete Performance.prototype.memory",
    };

    /// <summary>The layer.</summary>
    public static string BodyJs()
    {
        var touch = string.Join(", ", HandlerTable.Touch.Select(n => "'" + n + "'"));

        return """
               // ---- event-handler attributes (R196) ---------------------------------------------------
               // R193 filled the not-function names with `{ value: null }` slots. The target warns about exactly that
               // shape: hsw reads getOwnPropertyDescriptor on the touch handlers and on the tail of the window list,
               // then reads .value AND .get and the getter's source. An event-handler IDL attribute is an ACCESSOR
               // pair in both engines, and a data slot holding null is a shape no engine gives a handler.
               (() => {
               try {
                 const M = G.__nativeMask || {};
                 const asNative = M.asNative || ((fn) => fn);
                 const getterOf = M.getter || ((impl) => impl);
                 const setterOf = (impl, name) => (M.renamed || ((fn) => fn))(
                   Object.getOwnPropertyDescriptor({ set m(v) { impl.call(this, v); } }, 'm').set, name);

                 const HANDLERS = __HANDLERS__;

                 HANDLERS.forEach((name) => {
                   try {
                     if (name in G) return;
                     let handler = null;

                     // [Global] attributes accept a missing receiver and treat it as the global object.
                     const check = (self, kind) => {
                       if (self !== undefined && self !== null && self !== G) {
                         throw new TypeError('The Window.' + name + ' ' + kind
                           + ' can only be used on instances of Window');
                       }
                     };

                     const getter = getterOf(function () { check(this, 'getter'); return handler; }, 'get ' + name);
                     asNative(getter, 'get ' + name, 0);
                     const setter = setterOf(function (v) {
                       check(this, 'setter');
                       handler = (typeof v === 'function' || (v !== null && typeof v === 'object')) ? v : null;
                     }, 'set ' + name);
                     asNative(setter, 'set ' + name, 1);

                     Object.defineProperty(G, name,
                       { get: getter, set: setter, configurable: true, enumerable: true });
                   } catch (e) {}
                 });

                 // ---- createEvent ----------------------------------------------------------------
                 // WebKit still makes a TouchEvent this way; Blink removed it from the factory's list and throws
                 // NotSupportedError. The result is recorded as a boolean, so a page claiming iOS 26 was reporting that
                 // createEvent('TouchEvent') FAILED on it -- while 'ontouchstart' in window, five maxTouchPoints and a
                 // TouchEvent constructor all said the opposite in the same payload. Blink does keep the constructor,
                 // so the factory's result can be built directly: createEvent returns an uninitialised event, which
                 // `new TouchEvent('')` reproduces (type "", empty TouchLists, isTrusted false, not dispatched).
                 try {
                   if (G.Document && G.Document.prototype && typeof G.TouchEvent === 'function') {
                     const proto = G.Document.prototype;
                     const original = proto.createEvent;
                     const patched = { m() {
                       try {
                         if (arguments.length && String(arguments[0]).toLowerCase() === 'touchevent') {
                           return new G.TouchEvent('');
                         }
                       } catch (e) {}
                       return original.apply(this, arguments);
                     } }.m;
                     asNative(patched, 'createEvent', original.length);
                     Object.defineProperty(proto, 'createEvent',
                       { value: patched, writable: true, enumerable: false, configurable: true });
                   }
                 } catch (e) {}

                 // ---- prefixed aliases --------------------------------------------------------
                 try { if (!('webkitIndexedDB' in G) && G.indexedDB) {
                   Object.defineProperty(G, 'webkitIndexedDB',
                     { value: G.indexedDB, writable: true, enumerable: false, configurable: true });
                 } } catch (e) {}

                 // performance.memory is Blink-only -- WebKit has never shipped it -- and hsw probes
                 // `"memory" in performance` directly. It lives on Performance.prototype, so neither the window
                 // deletion pass nor the navigator prune reaches it.
                 try { if (G.Performance && G.Performance.prototype) delete G.Performance.prototype.memory; } catch (e) {}

                 G.__handlerSurface = { touch: [__TOUCH__], count: HANDLERS.length };
               } catch (e) {}
               })();
               """
            .Replace("__HANDLERS__", HandlerTable.HandlersJs)
            .Replace("__TOUCH__", touch);
    }

    /// <summary>The descriptor shape hsw reads.</summary>
    public const string Rule =
        "an event-handler IDL attribute is an accessor pair in both engines; a {value: null, writable: true} slot "
        + "answers the descriptor probes with a shape no engine gives a handler";

    /// <summary>The gate that depends on one of these names.</summary>
    public const string GateRule =
        "with aK_ false the gate opens and we spawn a worker a real iPhone never spawns";
}
