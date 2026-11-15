using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The two members from the thirteen that can be installed as plain values (R167).
///
/// <para>
/// R166 measured thirteen names a phone has and this engine lacks, and installed none of them. Two of them need no
/// simulation to be believable:
/// </para>
///
/// <list type="bullet">
/// <item><c>standalone</c> — a boolean, false in a browser tab. Safari-only, which is exactly why a phone claim needs
/// it and a Chromium build does not have it.</item>
/// <item><c>locks</c> — the Web Locks API: <c>request(name, callback)</c> and <c>query()</c>. Both are answerable
/// without a lock manager, because a page that calls them wants the callback to run, not a queue to inspect.</item>
/// </list>
///
/// <para>
/// Both go on <c>Navigator.prototype</c>, per R164's rule, and both are registered for masking per R160's — a member
/// that exists but prints its own source is worse than a member that is missing, because it answers two questions
/// wrongly instead of one.
/// </para>
/// </summary>
public static class NavigatorLocks
{
    /// <summary>The arity of <c>locks.request</c> per the specification.</summary>
    public const int RequestArity = 2;

    /// <summary>The arity of <c>locks.query</c>.</summary>
    public const int QueryArity = 0;

    /// <summary>The names this body installs.</summary>
    public static readonly IReadOnlyList<string> Installed = new[] { "standalone", "locks" };

    /// <summary>
    /// The statements: <c>standalone</c> on the prototype, and a <c>locks</c> whose <c>request</c> runs the callback and
    /// whose <c>query</c> answers an empty snapshot rather than throwing.
    /// </summary>
    public static string BodyJs()
    {
        return """
               // ---- the two plain values (R167) ------------------------------------------------
               try {
                 const N = G.navigator;
                 const P = N && Object.getPrototypeOf(N);
                 if (P) {
                   // standalone: Safari-only, so a phone claim needs it and Chromium has not got it
                   try {
                     Object.defineProperty(P, 'standalone',
                       { value: false, writable: true, configurable: true, enumerable: true });
                   } catch (e) {}

                   // locks: request(name, callback) resolves with the callback's result; query() answers a
                   // snapshot. An empty queue is the honest answer for a page that never held a lock.
                   try {
                     if (!('locks' in P)) {
                       const locks = {
                         request: function request(name, callback) {
                           const fn = (typeof callback === 'function') ? callback
                             : (typeof arguments[2] === 'function' ? arguments[2] : null);
                           if (!fn) return Promise.resolve(undefined);
                           try { return Promise.resolve(fn({ name: name, mode: 'exclusive' })); }
                           catch (e) { return Promise.reject(e); }
                         },
                         query: function query() {
                           return Promise.resolve({ held: [], pending: [], granted: [] });
                         },
                       };
                       Object.defineProperty(P, 'locks',
                         { value: locks, writable: true, configurable: true, enumerable: true });
                     }
                   } catch (e) {}
                 }
               } catch (e) {}
               """;
    }

    /// <summary>The rule: a member that exists and prints its source answers two questions wrongly.</summary>
    public const string Rule =
        "a member that exists but prints its own source is worse than a missing one: it answers both "
        + "\"does it exist\" and \"is it native\" wrongly";
}
