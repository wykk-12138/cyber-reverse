using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The key-order layer's entry points, installed where the target installs them (R186, corrected in R187).
///
/// <para>
/// R180 built a wide layer and left it unwired: wrapping the three entry points for <b>every</b> object made a mutated
/// run hang. R186 narrowed it to the window and to two entry points, and put it after the prunes — a guess about an
/// interaction. The target's own bytes settle both questions, at <c>0x03d1efd4</c>:
/// </para>
///
/// <code>
/// ['getOwnPropertyNames', 'keys'].forEach((name) => {
///   method(Object, name, function (original, args) {
///     return reorder(args[0], original.apply(this, args), name === 'keys');
///   });
/// });
/// method(Reflect, 'ownKeys', function (original, args) {
///   const keys = original.apply(this, args);
///   const strings = [], rest = [];
///   keys.forEach((k) => { (typeof k === 'string' ? strings : rest).push(k); });
///   if (!rest.length) return reorder(args[0], keys, false);
///   return reorder(args[0], strings, false).concat(rest);
/// });
/// </code>
///
/// <list type="number">
/// <item><b>Three entry points, not two.</b> <c>Reflect.ownKeys</c> is wrapped, and it splits the symbols off before
/// reordering and appends them back — because ordinary own-key order puts symbols last anyway, and the previous
/// "bail out if any symbol is present" guard made <c>getOwnPropertyNames</c> and <c>ownKeys</c> disagree about the same
/// object, which is a sharper tell than whatever the rule was hiding.</item>
/// <item><b>The window test is identity.</b> <c>reorder</c> answers the ordered list only for
/// <c>isWindow &amp;&amp; target === G</c> — "only the real global object, not something that merely looks like it".
/// The R186 slice accepted any object with <c>window === itself</c> and a <c>document</c>, which also matches a parent
/// frame reached through <c>contentWindow</c>.</item>
/// <item><b>Installed above the prunes.</b> <c>reorder</c> lands at <c>0x03d1efd4</c>, the prunes at
/// <c>0x03d208ca</c>/<c>0x03d272d4</c>/<c>0x03d27858</c>. They can live with that because they enumerate through the
/// captured <see cref="NativeRefs"/> reference; the replica now does the same.</item>
/// <item><b>The owner comes from the realm.</b> This body is replayed into a child realm with <c>G</c> pointing at the
/// child, so the constructors have to be read as <c>G.Object</c> / <c>G.Reflect</c>. Measured before the fix: the
/// parent's <c>Object.keys</c> came back as an uncloaked wrapper (20 lines of its own source) while the child held the
/// cloaked copy the journal had installed — one realm replay, two wrong answers.</item>
/// </list>
///
/// <para>
/// <b>Still narrower than the target, on purpose.</b> The target's <c>reorder</c> also carries the CSS
/// supported-property rule and the <c>ORDER</c> table (<see cref="KeyOrderTable"/>, measured but unwired); this slice
/// answers the window and passes every other object straight through.
/// </para>
/// </summary>
public static class WindowOrderWrap
{
    /// <summary>The three entry points the target patches, with the owner each one lives on.</summary>
    public static readonly (string Owner, string Name)[] EntryPoints =
    {
        ("Object", "getOwnPropertyNames"),
        ("Object", "keys"),
        ("Reflect", "ownKeys"),
    };

    /// <summary>
    /// The target's test, verbatim: only the real global. A <c>contentWindow</c> that carries <c>window</c> and
    /// <c>document</c> pointing at itself is not it.
    /// </summary>
    public const string IsWindowTest = "target === G";

    /// <summary>The three installs, in the target's order.</summary>
    public static string BodyJs()
    {
        var installs = string.Join("\n",
            EntryPoints.Select(p =>
                $"                 install('{p.Owner}', '{p.Name}', {(p.Name == "keys" ? "true" : "false")});"));

        return """
               // ---- window key order, narrowly (R186, corrected in R187) -------------------------
               // The three entry points the target patches, at 0x03d1efd4. Only the real global is reordered and
               // every other object passes through untouched: R180 measured that wrapping these for ALL objects
               // makes a mutated run hang, because the wrapper then sits underneath the code a mutation disables.
               try {
                 const CSS_DECL = __CSS__;
                 const INDEX = /^[0-9]+$/;
                 const ORDER = [
               __RULES__
                 ];

                 // ---- reorder: the target's own dispatch, 0x03d1e1bf -------------------------------
                 // Four answers in this order: the real global, a CSSStyleDeclaration PROTOTYPE (own-names only),
                 // a CSSStyleDeclaration INSTANCE (numeric indices alone), and the ORDER table. Anything that
                 // matches nothing keeps the engine's order.
                 const reorder = (target, names, enumerableOnly) => {
                   try {
                     if (target === G && G.__topList) {
                       // R192: the BASE is the device's recorded list (WINDOW_ENUM / WINDOW_ALL), not this realm's
                       // live enumeration — that is what the target passes at 0x03d1e274, and hsw reads the last 25
                       // names of Object.keys(window), so the order is the answer.
                       const recorded = G.__windowNames
                         ? (enumerableOnly ? G.__windowNames.enum : G.__windowNames.all) : null;
                       if (recorded && recorded.length) return G.__topList(recorded, names, enumerableOnly);
                       return G.__topList(names, names, enumerableOnly);
                     }

                     // hsw enumerates CSSStyleDeclaration.prototype, and "the supported-property list is one of the
                     // strongest engine tells there is". WebKit keeps its ~1500 accessors on CSSStyleProperties and
                     // leaves cssRules and getPropertyCSSValue on the declaration; Blink has no CSSStyleProperties.
                     // Gated on !enumerableOnly, exactly as the target gates it (0x03d1eb7b).
                     if (CSS_DECL && CSS_DECL.length && !enumerableOnly) {
                       if (typeof CSSStyleDeclaration !== 'undefined'
                           && target === CSSStyleDeclaration.prototype) {
                         return CSS_DECL.slice();
                       }
                     }

                     // The INSTANCE is the sharper one, and it is NOT gated: the call log records
                     // keys(CSSStyleDeclaration instance) twice per solve. Blink hangs ~1200 camelCase properties on
                     // the instance as own properties; WebKit leaves it "nothing but numeric indices". The loose
                     // attempt (filter to the device's vocabulary) still shipped 1505 names -- the right 881 plus 624
                     // duplicates in Blink's order -- and "no engine enumerates a property twice".
                     // CSS_PROTO is excluded explicitly: it is Object.create(CSSStyleDeclaration.prototype), so it
                     // answers true to instanceof exactly like an instance does. R189: read from the realm at CALL
                     // time — CSSStyleProperties is synthesized after this body installs, so a captured value would
                     // still be null when the first enumeration arrives.
                     if (typeof CSSStyleDeclaration !== 'undefined'
                         && target instanceof CSSStyleDeclaration
                         && target !== CSSStyleDeclaration.prototype && target !== G.__cssProto) {
                       return names.filter((n) => INDEX.test(n));
                     }

                     // The ORDER table, verbatim from the target: { match, names, drop }. A rule may also DROP names
                     // -- engine members the device does not have and that cannot be deleted (WebIDL constants are
                     // non-configurable). An empty `names` with a `drop` is a pure filter.
                     for (let i = 0; i < ORDER.length; i++) {
                       const rule = ORDER[i];
                       let hit = false;
                       try { hit = rule.match(target); } catch (e) { hit = false; }
                       if (!hit) continue;

                       const wanted = rule.names.filter((n) => names.indexOf(n) !== -1);
                       const extra = names.filter((n) => wanted.indexOf(n) === -1
                         && !(rule.drop && rule.drop.indexOf(n) !== -1));
                       return wanted.concat(extra);
                     }
                   } catch (e) {}
                   return names;
                 };

                 // The owner is resolved THROUGH THE REALM. A child realm replays this body with `G` pointing at the
                 // child while the closure's `Object` is still the parent's — measured, that left the parent holding
                 // an uncloaked wrapper and the child holding the cloaked copy.
                 const install = (host, name, enumerableOnly) => {
                   try {
                     const owner = G[host] || (host === 'Object' ? Object : Reflect);
                     const original = owner[name];
                     if (typeof original !== 'function') return;

                     const wrapped = {
                       wrap() {
                         const target = arguments[0];
                         const all = original.apply(this, arguments);
                         try {
                           if (enumerableOnly) return reorder(target, all, true);

                           // Reflect.ownKeys hands back symbols too, and ordinary own-key order puts them last
                           // anyway — so reorder the string half and append the rest, rather than bailing out.
                           const strings = [], rest = [];
                           all.forEach((k) => { (typeof k === 'string' ? strings : rest).push(k); });
                           if (!rest.length) return reorder(target, all, false);
                           return reorder(target, strings, false).concat(rest);
                         } catch (e) { return all; }
                       },
                     }.wrap;

                     try {
                       const M = G.__nativeMask;
                       if (M && M.asNative) M.asNative(wrapped, name, original.length);
                     } catch (e) {}

                     // The target installs through `method()`, which records the patch for realm replay. A child
                     // frame gets its own Object and Reflect, so the wrapper has to follow it there.
                     try {
                       if (G.__patchJournal && G.__patchJournal.record) G.__patchJournal.record(owner, name);
                     } catch (e) {}

                     Object.defineProperty(owner, name,
                       { value: wrapped, writable: true, configurable: true, enumerable: false });
                   } catch (e) {}
                 };

               __INSTALLS__
               } catch (e) {}
               """
            .Replace("__CSS__", KeyOrderRules.CssDeclarationJs)
            .Replace("__RULES__", KeyOrderRules.OrderRulesJs)
            .Replace("__INSTALLS__", installs);
    }

    /// <summary>Why the slice is this narrow.</summary>
    public const string Rule =
        "every other object passes through untouched: the wrapper must not sit underneath code a mutation can disable";

    /// <summary>Where the narrowing came from, in one sentence.</summary>
    public const string Correction =
        "three entry points, identity to the real global, installed above the prunes, the owner read through the realm "
        + "— all four read off 0x03d1efd4 and one measurement";
}
