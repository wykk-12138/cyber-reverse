namespace Cybersole.Stores.Scripts;

/// <summary>
/// The <c>CSSStyleProperties</c> synthesis and the proxy that hides Blink's declaration shape (R189).
///
/// <para>
/// Read off the target at <c>0x03d98/0x03d99…</c>, after the prunes — the global prune would otherwise delete
/// <c>window.CSSStyleProperties</c>, which is a WebKit-only name the device's list does not carry.
/// </para>
///
/// <para>
/// <b>Why it exists.</b> A Safari computed style is a <c>CSSStyleProperties</c>: 1468 camelCase accessors live on
/// <c>CSSStyleProperties.prototype</c>, and an instance owns nothing but numeric indices. Blink has no such interface,
/// so it hangs the same camelCase names on the declaration itself — 1230 own names where the device reports 480
/// indices — and <c>'appRegion' in getComputedStyle(el)</c> answers true where a real iPhone never had the property.
/// Filtering the enumeration (R188) fixes the channel hsw logs, and nothing else: descriptors, <c>in</c>, and
/// <c>hasOwnProperty</c> still told the truth about Blink.
/// </para>
///
/// <para>
/// <b>Why a proxy and not <c>delete</c>.</b> The target's measurement, kept because it is the reason for the shape:
/// "delete does NOT work on these: Blink exposes the camelCase CSS properties through an IDL named-property interceptor,
/// so getOwnPropertyNames reports them and getOwnPropertyDescriptor returns a descriptor, but removing one is a silent
/// no-op and it is back on the next read. Measured: after deleting, hasOwnProperty('appRegion') was still true."
/// A Proxy is legal here because every named own property is configurable and the declaration is extensible
/// (measured: 747 named own properties, 0 non-configurable, 0 non-enumerable), so no proxy invariant is violated.
/// </para>
/// </summary>
public static class CssStyleProperties
{
    /// <summary>The interface the target synthesizes, and the class string it must answer with.</summary>
    public const string InterfaceName = "CSSStyleProperties";

    /// <summary>
    /// The channel R188 could not fix: a name that only <c>in</c> and <c>hasOwnProperty</c> can see. Blink has it,
    /// WebKit has never shipped it.
    /// </summary>
    public const string BlinkOnlyProbe = "appRegion";

    /// <summary>The synthesis plus the proxy, one body.</summary>
    public static string BodyJs() => """
        // ---- CSSStyleProperties (R189) -----------------------------------------------------
        // A Safari computed style IS a CSSStyleProperties: 1468 accessors on the prototype, and an instance that
        // owns only numeric indices. Blink has no such interface -- it hangs the camelCase names on the declaration --
        // and R188 only fixed the ENUMERATION channel: `in`, hasOwnProperty and descriptor lookups still answered
        // honestly about Blink, which is a contradiction no engine can produce.
        (() => {
        try {
          if (typeof CSSStyleDeclaration === 'undefined') return;
          if (typeof G.CSSStyleProperties !== 'undefined') return;

          const CSS_PROPS = __PROPS__;
          if (!CSS_PROPS || !CSS_PROPS.length) return;
          const CSS_SET = new Set(CSS_PROPS);

          const M = G.__nativeMask || {};
          const asNative = M.asNative || ((fn) => fn);
          const renamed = M.renamed || ((fn) => fn);
          const getterOf = M.getter || ((impl, n) => renamed(
            Object.getOwnPropertyDescriptor({ get m() { return impl.call(this); } }, 'm').get, n));
          const setterOf = (impl, n) => renamed(
            Object.getOwnPropertyDescriptor({ set m(v) { impl.call(this, v); } }, 'm').set, n);
          const nativeOwnNames = G.__nativeOwnNames || Object.getOwnPropertyNames;

          // backgroundColor -> background-color, ApplePayButtonStyle -> -apple-pay-button-style
          const dashed = (name) => name
            .replace(/^[A-Z]/, (c) => '-' + c.toLowerCase())
            .replace(/[A-Z]/g, (c) => '-' + c.toLowerCase());

          const CSSStyleProperties = function CSSStyleProperties() {};
          asNative(CSSStyleProperties, 'CSSStyleProperties', 0);

          const proto = Object.create(CSSStyleDeclaration.prototype);

          // Defined in the captured order, `constructor` first, so getOwnPropertyNames comes back matching the
          // device without needing a reorder rule.
          Object.defineProperty(proto, 'constructor',
            { value: CSSStyleProperties, writable: true, enumerable: false, configurable: true });

          CSS_PROPS.forEach((name) => {
            if (name === 'constructor') return;
            const css = dashed(name);
            const getter = getterOf(function () { return this.getPropertyValue(css); }, 'get ' + name);
            asNative(getter, 'get ' + name, 0);
            const setter = setterOf(function (v) { this.setProperty(css, v); }, 'set ' + name);
            asNative(setter, 'set ' + name, 0);
            Object.defineProperty(proto, name,
              { get: getter, set: setter, enumerable: true, configurable: true });
          });

          CSSStyleProperties.prototype = proto;
          // reorder treats every `instanceof CSSStyleDeclaration` object as an instance unless it is one of the two
          // interface prototypes; this is the second one, and the wrap below is what makes it reachable.
          G.__cssProto = proto;

          // An interface prototype carries its own class string; without this one the prototype inherits
          // CSSStyleDeclaration's.
          Object.defineProperty(proto, Symbol.toStringTag,
            { value: 'CSSStyleProperties', writable: false, enumerable: false, configurable: true });
          Object.defineProperty(G, 'CSSStyleProperties',
            { value: CSSStyleProperties, writable: true, enumerable: false, configurable: true });

          // CSS_DECL (R188) makes getOwnPropertyNames(CSSStyleDeclaration.prototype) report the device's eleven names,
          // two of which -- cssRules and getPropertyCSSValue -- are WebKit-only and were never defined. The object
          // would then enumerate them while getOwnPropertyDescriptor returned undefined: a state no engine can
          // produce, and hsw already holds that exact list, so a descriptor lookup is the cheapest follow-up.
          try {
            const gpcv = { m() { return null; } }.m;
            asNative(gpcv, 'getPropertyCSSValue', 1);
            Object.defineProperty(CSSStyleDeclaration.prototype, 'getPropertyCSSValue',
              { value: gpcv, writable: true, enumerable: true, configurable: true });
          } catch (e) {}

          try {
            const cssRulesGetter = getterOf(function () { return null; }, 'get cssRules');
            asNative(cssRulesGetter, 'get cssRules', 0);
            Object.defineProperty(CSSStyleDeclaration.prototype, 'cssRules',
              { get: cssRulesGetter, enumerable: true, configurable: true });
          } catch (e) {}

          // Only OWN properties are filtered. In Blink the camelCase CSS properties are own properties of the
          // declaration; everything reached through the prototype chain -- getPropertyValue, setProperty, item,
          // cssText, length, constructor -- must pass through untouched, or the declaration stops working for the
          // page and for hCaptcha's own widget.
          const keep = (name) => typeof name !== 'string' || /^[0-9]+$/.test(name) || CSS_SET.has(name);
          const hidden = (t, p) => !keep(p) && Object.prototype.hasOwnProperty.call(t, p);
          const indexKey = (p) => typeof p === 'string' && /^[0-9]+$/.test(p);
          const BOUND = new WeakMap();

          // Which names must be bound to the real declaration. Measured in a child realm first: an identity check
          // against THIS realm's `Object.prototype` mis-fires there, because the child's `hasOwnProperty` is a
          // different function object — it fell through to the bind path, got bound to the RAW declaration, and
          // routed around the traps, so `cs.hasOwnProperty('appRegion')` answered true while `'appRegion' in cs`
          // answered false. Asking the interface prototype instead is realm-independent and is the exact set that
          // needs a brand-safe receiver.
          const needsBind = (p) => {
            try {
              return p !== 'constructor' && typeof p === 'string'
                && Object.prototype.hasOwnProperty.call(CSSStyleDeclaration.prototype, p);
            } catch (e) { return false; }
          };

          const wrap = (decl) => {
            if (!decl) return decl;
            // The prototype has to come from the DECLARATION's realm, not from the one that built this closure.
            // Measured: a same-origin child got the parent's proxy through the journal, so `getPrototypeOf(cs)` was
            // the parent's CSSStyleProperties.prototype and `cs instanceof w.CSSStyleDeclaration` answered false —
            // the one hard constraint (instanceof must keep working) breaking in the frame that matters.
            const protoFor = (t) => {
              try {
                const win = t && t.ownerDocument && t.ownerDocument.defaultView;
                const iface = win && win.CSSStyleProperties;
                if (iface && iface.prototype) return iface.prototype;
              } catch (e) {}
              return proto;
            };

            try {
              return new Proxy(decl, {
                getPrototypeOf(t) { return protoFor(t); },

                ownKeys(t) {
                  return nativeOwnNames(t).filter(indexKey).concat(Object.getOwnPropertySymbols(t));
                },

                has(t, p) { return hidden(t, p) ? false : Reflect.has(t, p); },

                getOwnPropertyDescriptor(t, p) {
                  if (hidden(t, p)) return undefined;
                  // A named own property is a Blink artifact: on WebKit it sits on the prototype, so hasOwnProperty
                  // must answer false for it, matching ownKeys above.
                  if (typeof p === 'string' && !indexKey(p)
                      && Object.prototype.hasOwnProperty.call(t, p)) return undefined;
                  return Reflect.getOwnPropertyDescriptor(t, p);
                },

                get(t, p) {
                  // On WebKit a computed style is a CSSStyleProperties, so its constructor must say so -- the
                  // target's own constructor is Blink's CSSStyleDeclaration. Read through the declaration's realm:
                  // a child frame's declaration has a constructor of its own, and `cs.constructor === w.CSSStyleProperties`
                  // is a question a detector can ask.
                  if (p === 'constructor') {
                    try {
                      const ctor = protoFor(t).constructor;
                      if (ctor) return ctor;
                    } catch (e) {}
                    return CSSStyleProperties;
                  }
                  // ...and so must its class string. Object.prototype.toString reads Symbol.toStringTag through this
                  // trap, and the target answered "CSSStyleDeclaration" -- two class names from one object needs no
                  // reference device to spot.
                  if (p === Symbol.toStringTag) return 'CSSStyleProperties';

                  const v = Reflect.get(t, p, t);
                  if (typeof v !== 'function') return v;

                  // Object.prototype's own builtins must NOT be bound: they are generic, they work with the proxy as
                  // the receiver, and binding them to the raw declaration routes them AROUND the traps. That made the
                  // same question give two answers -- decl.hasOwnProperty('appRegion') ran on the target and said true
                  // while Object.prototype.hasOwnProperty.call(decl, 'appRegion') went through
                  // getOwnPropertyDescriptor and said false.
                  if (!needsBind(p)) return v;

                  // Methods must be bound to the real declaration: CSSStyleDeclaration's methods carry a brand check
                  // and throw "Illegal invocation" when `this` is the proxy. But a bound function renames itself to
                  // "bound getPropertyValue" and its toString stops reading as native, so both are restored.
                  // `constructor` is handled above, because binding it made getComputedStyle(el).constructor.name
                  // report "bound CSSStyleDeclaration".
                  let bound = BOUND.get(v);
                  if (!bound) {
                    bound = v.bind(t);
                    asNative(bound, v.name, v.length);
                    BOUND.set(v, bound);
                  }
                  return bound;
                },
              });
            } catch (e) { return decl; }
          };

          const callWrap = (fn, self, args) => wrap(fn.apply(self, args));

          // Patched on the window, not on Document.prototype: the target installs `method(G, 'getComputedStyle')`.
          try {
            const original = G.getComputedStyle;
            if (typeof original === 'function') {
              const wrapped = { wrap() { return callWrap(original, this, arguments); } }.wrap;
              asNative(wrapped, 'getComputedStyle', original.length);
              // NOT recorded in the journal, deliberately: a copied wrapper carries THIS realm's CSSStyleProperties
              // prototype into the child, and then `cs instanceof w.CSSStyleDeclaration` answers false there. Each
              // realm runs this body itself, so each gets a proxy wired to its own prototype — measured both ways.
              Object.defineProperty(G, 'getComputedStyle',
                { value: wrapped, writable: true, enumerable: false, configurable: true });
            }
          } catch (e) {}
        } catch (e) {}
        })();
        """.Replace("__PROPS__", CssProperties.PropsJs);

    /// <summary>What the proxy is for, in the target's words.</summary>
    public const string Rule =
        "delete does NOT work on these: Blink exposes the camelCase CSS properties through an IDL named-property "
        + "interceptor, so removing one is a silent no-op and it is back on the next read";

    /// <summary>The contradiction the proxy removes.</summary>
    public const string Contradiction =
        "decl.hasOwnProperty('appRegion') ran on the target and said true while "
        + "Object.prototype.hasOwnProperty.call(decl, 'appRegion') went through getOwnPropertyDescriptor and said false";
}
