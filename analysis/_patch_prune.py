import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\GlobalPrune.cs'
t = io.open(p, encoding='utf-8').read()

old_const = '''    /// <summary>The value a real Chrome-on-iOS can only ever report.</summary>'''
new_const = '''    /// <summary>
    /// Names Chromium puts BACK after a delete. Measured in R206: one suite run in about six ended with
    /// <c>extra[chrome]</c> — <c>'chrome' in window</c> true again, minutes after the prune had removed it. A single
    /// delete cannot win a race against a renderer that re-installs the object later, so the same deletion is
    /// re-asserted at the moments a renderer can do that.
    /// </summary>
    public static readonly IReadOnlyList<string> ReCreated = new[] { "chrome" };

    /// <summary>The value a real Chrome-on-iOS can only ever report.</summary>'''

old_body = '''                 G.__globalPrune = globalPrune;
                 globalPrune(G);
               } catch (e) {}'''
new_body = '''                 // R206: Chromium re-installs `chrome` after this runs. Re-assert the deletion of the names that come
                 // back, at every moment a renderer can put them there again -- the current task, DOMContentLoaded,
                 // load, one rAF and three short timers. Only the ReCreated list is touched, so this cannot delete
                 // anything this script added later in the load.
                 const reassert = (realm) => {
                   if (!realm) return;
                   [__RECREATED__].forEach((name) => { try { delete realm[name]; } catch (e) {} });
                 };
                 const scheduleReassert = (realm) => {
                   if (!realm) return;
                   reassert(realm);
                   try { realm.setTimeout(() => reassert(realm), 0); } catch (e) {}
                   try { realm.setTimeout(() => reassert(realm), 60); } catch (e) {}
                   try { realm.setTimeout(() => reassert(realm), 300); } catch (e) {}
                   try { if (realm.document && realm.document.addEventListener)
                     realm.document.addEventListener('DOMContentLoaded', () => reassert(realm), true); } catch (e) {}
                   try { if (realm.addEventListener)
                     realm.addEventListener('load', () => reassert(realm), true); } catch (e) {}
                   try { if (realm.requestAnimationFrame) realm.requestAnimationFrame(() => reassert(realm)); } catch (e) {}
                 };

                 G.__globalPrune = globalPrune;
                 G.__globalPruneReassert = scheduleReassert;
                 globalPrune(G);
                 scheduleReassert(G);
               } catch (e) {}'''

old_tail = '''               """.Replace("__DEVICE__", device).Replace("__KEEP__", keep);'''
new_tail = '''               """
            .Replace("__DEVICE__", device)
            .Replace("__KEEP__", keep)
            .Replace("__RECREATED__", string.Join(", ", ReCreated.Select(n => "'" + n + "'")));'''

old_keep_anchor = '''        var keep = string.Join(", ", Keep.Select(n => "'" + n + "'"));'''
new_keep_anchor = '''        var keep = string.Join(", ", Keep.Select(n => "'" + n + "'").Concat(new[] { "'__globalPruneReassert'" }));'''

for a, b in ((old_const, new_const), (old_body, new_body), (old_tail, new_tail), (old_keep_anchor, new_keep_anchor)):
    assert a in t, a[:60]
    t = t.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('patched GlobalPrune')
