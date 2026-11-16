using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The replay journal: patches recorded with a realm-independent path, so a child realm can be patched by resolving the
/// path there (R174).
///
/// <code>
/// const pathOf = (target) => {
///   if (target === G) return [];
///   for (let i = 0; i &lt; KNOWN.length; i++) {
///     const name = KNOWN[i];
///     let holder; try { holder = G[name]; } catch (e) { continue; }
///     if (!holder) continue;
///     if (holder === target) return [name];
///     try { if (holder.prototype === target) return [name, 'prototype']; } catch (e) { }
///     if (G.Intl) { for (…) { if (ctor === target) return ['Intl', INTL_NAMES[i]]; … } }
///   }
///   return null;
/// };
/// const record = (target, name) => {
///   const path = pathOf(target);
///   if (path) PATCHES.push({ path, key: name, from: target });
/// };
/// </code>
///
/// <para>
/// The reason is one sentence in the image: <i>an iframe gets its own constructors, so a same-origin child is otherwise
/// completely unspoofed — read iframe.contentWindow.navigator and the real Blink values come straight back.</i>
/// </para>
///
/// <para>
/// The replica already replays by re-running the whole body with a different realm, which works but patches whatever the
/// body happens to patch. A journal is different in two ways that matter: it records <b>which key on which object</b>
/// (so a member installed by one pass and masked by another is replayed once), and it can name objects the body cannot
/// reach generically — <c>Intl.DateTimeFormat.prototype</c>, which needs a three-step path.
/// </para>
/// </summary>
public static class PatchJournal
{
    /// <summary>One recorded patch: the path to the object, and the key on it.</summary>
    public sealed record Entry(string[] Path, string Key);

    /// <summary>
    /// The constructors a path can start with: the image's list, plus the two the key-order layer lives on (R187).
    /// <c>pathOf</c> only finds an object the list names, so an unlisted <c>Object.keys</c> is installed in the top
    /// realm and nowhere else.
    /// </summary>
    public static IReadOnlyList<string> Known =>
        AccessorBrandCheck.Known
            .Where(n => n != "Object" && n != "Reflect")
            .Concat(new[] { "Function" })
            .ToList();

    /// <summary>The Intl names, which need a three-step path.</summary>
    public static IReadOnlyList<string> IntlNames => AccessorBrandCheck.IntlNames;

    /// <summary>The patches this workspace installs on <c>Navigator.prototype</c>, and therefore records.</summary>
    public static IReadOnlyList<Entry> Entries =>
        new[]
            {
                AccessorBrandCheck.Guarded,
                NavigatorLocks.Installed,
                new[] { "audioSession" },
                ForwardingShims.WebShare.Select(p => p.Name),
            }
            .SelectMany(names => names)
            .Distinct(System.StringComparer.Ordinal)
            .Select(name => new Entry(new[] { "Navigator", "prototype" }, name))
            .Concat(new[]
            {
                // recorded but not installed here: the Intl constructors, whose paths are the reason the journal exists
                new Entry(new[] { "Intl", "DateTimeFormat", "prototype" }, "resolvedOptions"),
                new Entry(new[] { "Intl", "NumberFormat", "prototype" }, "resolvedOptions"),

                // R191: the key-order entry points are NOT journaled, deliberately. A copied wrapper closes over the
                // PARENT realm's CSSStyleDeclaration and G, so in a frame it matches nothing: measured, the child's
                // CSSStyleDeclaration.prototype came back with 12 own names instead of the 11 CSS_DECL answers, and a
                // window that is not the closure's G is never reordered. Each realm runs the body itself, so each gets
                // a wrapper wired to its own constructors.

                // R187, measured: without this a child frame answers `Function.prototype.toString.call(Object.keys)`
                // with the wrapper's own 20 lines, because the cloak lives in the parent's WeakMap and the child has
                // its own pristine `toString`. The patched one reads the shared map, so sharing it is the whole fix.
                new Entry(new[] { "Function", "prototype" }, "toString"),
            })
            .ToList();

    /// <summary>The journal, its recorder and its replayer.</summary>
    public static string BodyJs()
    {
        var known = string.Join(", ", Known.Select(n => "'" + n + "'"));
        var intl = string.Join(", ", IntlNames.Select(n => "'" + n + "'"));
        var entries = string.Join(", ",
            Entries.Select(e =>
                "{ path: [" + string.Join(", ", e.Path.Select(p => "'" + p + "'")) + "], key: '" + e.Key + "' }"));

        return """
               // ---- the replay journal (R174) ---------------------------------------------------
               // A same-origin iframe gets its own constructors, so a patch that lives only in the parent is missing
               // in the child: read iframe.contentWindow.navigator and the real Blink values come straight back.
               // Patches are therefore recorded with a realm-independent PATH and replayed by resolving it.
               try {
                 const KNOWN = [__KNOWN__];
                 const INTL_NAMES = [__INTL__];

                 const pathOf = (target) => {
                   if (target === G) return [];
                   for (let i = 0; i < KNOWN.length; i++) {
                     const name = KNOWN[i];
                     let holder;
                     try { holder = G[name]; } catch (e) { continue; }
                     if (!holder) continue;
                     if (holder === target) return [name];
                     try { if (holder.prototype === target) return [name, 'prototype']; } catch (e) {}

                     if (G.Intl) {
                       for (let j = 0; j < INTL_NAMES.length; j++) {
                         const ctor = G.Intl[INTL_NAMES[j]];
                         if (!ctor) continue;
                         if (ctor === target) return ['Intl', INTL_NAMES[j]];
                         if (ctor.prototype === target) return ['Intl', INTL_NAMES[j], 'prototype'];
                       }
                     }
                   }
                   return null;
                 };

                 const resolve = (realm, path) => {
                   let holder = realm;
                   for (let i = 0; i < path.length && holder; i++) {
                     try { holder = holder[path[i]]; } catch (e) { holder = null; }
                   }
                   return holder || null;
                 };

                 const PATCHES = [];
                 const record = (target, key) => {
                   const path = pathOf(target);
                   if (path) PATCHES.push({ path: path, key: key, from: target });
                   return path;
                 };

                 // Re-apply every recorded patch into another realm, descriptor and all: a value that arrives as a data
                 // property on the parent must not arrive as an accessor on the child.
                 const replay = (realm) => {
                   PATCHES.forEach((row) => {
                     try {
                       const target = resolve(realm, row.path);
                       if (!target) return;
                       const d = Object.getOwnPropertyDescriptor(row.from, row.key);
                       if (d) Object.defineProperty(target, row.key, d);
                     } catch (e) {}
                   });
                 };

                 G.__patchJournal = { known: KNOWN, intl: INTL_NAMES, patches: PATCHES, pathOf, resolve, record, replay };

                 // the journal this workspace fills, described once above
                 [__ENTRIES__].forEach((row) => {
                   try {
                     const target = resolve(G, row.path);
                     if (target) record(target, row.key);
                   } catch (e) {}
                 });

                 // and a same-origin child, patched the moment it appears
                 try {
                   const watched = new WeakSet();
                   const patchFrame = (frame) => {
                     try {
                       const child = frame && frame.contentWindow;
                       if (!child || watched.has(child)) return;
                       watched.add(child);
                       replay(child);
                     } catch (e) {}
                   };

                   const scan = (root) => {
                     try {
                       const frames = root.querySelectorAll ? root.querySelectorAll('iframe,frame') : [];
                       for (let i = 0; i < frames.length; i++) patchFrame(frames[i]);
                     } catch (e) {}
                   };

                   scan(G.document);
                   try {
                     new MutationObserver((records) => {
                       records.forEach((r) => {
                         (r.addedNodes || []).forEach && (r.addedNodes || []).forEach((node) => {
                           if (node && (node.tagName === 'IFRAME' || node.tagName === 'FRAME')) patchFrame(node);
                         });
                       });
                     }).observe(G.document, { childList: true, subtree: true });
                   } catch (e) {}
                 } catch (e) {}
               } catch (e) {}
               """
            .Replace("__KNOWN__", known)
            .Replace("__INTL__", intl)
            .Replace("__ENTRIES__", entries);
    }

    /// <summary>The rule the journal exists for.</summary>
    public const string Rule =
        "an iframe gets its own constructors, so a same-origin child is otherwise completely unspoofed — the patch has "
        + "to be recorded as a path and replayed by resolving it there";
}
