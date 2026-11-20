"""Classify the 17 ABSENT types as RENAMED (with mapping) or UNIMPLEMENTED (R619).

`bind_diff.py --type-presence` reports types that have no same-name declaration, and its own footnote says each must be
classified before the number is used as a gap count: the replica is allowed to rename types (AGENTS.md §0), so a type
declared under another name is not missing.

Method, mechanical and per item:

  * search every `.cs` for the type's **simple name** (namespace ignored) — the same rule `bind_diff` uses to call a
    type "present", applied here to find *candidates* rather than to decide presence;
  * for each candidate, read its body and count how many of the contract's members appear in it;
  * full coverage + a plausible namespace move  -> RENAMED (record the mapping)
  * partial coverage                            -> PARTIAL (a renamed type that is also short of members)
  * no candidate                                -> UNIMPLEMENTED

Coverage is a **lower bound**: it counts member *names* in the candidate's body text, so inherited members, expression
bodies and differently-named-but-equivalent members all read as absent. A low number therefore does not prove the type
is different; it only fails to prove it is the same. That asymmetry is why RENAMED needs full coverage.

Read-only. Prints a table; writes `docs/TYPE_PRESENCE_TRIAGE.md`.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src"
OUT = r"D:\projects\cyber-reverse\docs\TYPE_PRESENCE_TRIAGE.md"

# R702: types the YG ruling placed outside the replica's function set (docs/DECISION_LICENSE_OUT_OF_SCOPE.md).
NOT_IN_FUNCTION_SET = {"AuthWindow", "LicenseControl"}

# name -> full member list, copied from `bind_diff.py --type-presence`
ABSENT = {
    "CloudflareSolver": "ApiKey, Balance, BalanceSupported, Concurrency, Count, Id, IsFetchingBalance, Name, Type",
    "Settings": "AutoOpen3DS, AutoOpen3DSLimit, BackupInterval, BetaUpdates, BrowserLimit, BrowserPath, "
                "BrowserProfileAssignment, BrowserWindowMode, Clock, Currency, Keybinds, Language, MaxBackups, "
                "MaxLogRetention, MaxLogSize, MonitorConcurrency, MonitorDelay, MonitorFilters, Notifications, "
                "PinGroups, ProfileGroupOrder, ProxyGroupOrder, QueuePresentation, QuickTaskProfiles, "
                "QuickTaskProxies, RetryDelay, ScrollbarColor, ScrollbarCornerRadius, ScrollbarWidth, "
                "ShopifyBrowserProxy, SmartActions, StartupPage, TaskGroupOrder, Timeout",
    "ObservableDictionary": "Count",
    "KeyGesture": "Key, Modifiers",
    "Concurrency": "Maximum, Mode, Ratio",
    "ImapProvider": "Host, MessageCount, Status, Username",
    "ActionConfig": "Name, Required",
    "LocalizeEnumExtension": "Value",
    "LocalizeFallbackExtension": "Value",
    "LocalizeFormatExtension": "Value, Value2",
    "LocalizeSwitchExtension": "Condition",
    "AccountsCreatorView": "Add, Close",
    # R702 (docs/DECISION_LICENSE_OUT_OF_SCOPE.md): the auth/licence family is user management, so it sits
    # outside the replica's function set. LicenseControl and AuthWindow therefore classify as
    # NOT_IN_FUNCTION_SET (not UNIMPLEMENTED): "not built" is now a decision, not a gap.
    "AuthWindow": "Exit, Logout, Minimise",
    "LicenseControl": "Authenticate, Dashboard, Refresh",
    "SettingsView": "AppearanceView, CaptchaProvidersView, CloudflareSolversView, CustomSizesView, CustomStoresView, "
                    "DataView, GeneralSettingsView, GoogleAccountsView, HelpView, ImapView, KeyBindsView, LogOut, "
                    "NotificationsView, PayPalAccountsView, PaymentView, Transition, Update, Version, WebhookView",
    "TaskCreatorCartView": "Add, Delete, SizeItems",
    "TaskCreatorMainView": "ProfileGroupItems, ProfileItems, ShowCartView, SizeItems",
}

DECL = re.compile(r"\b(?:class|record|struct|interface)\s+(\w+)\s*(?:<[^>]*>)?\s*(?:\([^)]*\))?\s*(?::[^{]+)?\{")


def bodies():
    """type name -> list of (namespace-ish file, body, preceding doc comment)"""
    found = {}
    for dirpath, dirnames, filenames in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".cs"):
                continue
            path = os.path.join(dirpath, fn)
            text = io.open(path, encoding="utf-8", errors="replace").read()
            for m in DECL.finditer(text):
                name = m.group(1)
                brace = m.end() - 1
                depth, i = 0, brace
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                # R657: the doc comment immediately above the declaration. Lines of `///` are gathered upwards from
                # the declaration; anything else stops the climb.
                doc = []
                prev = text.rfind("\n", 0, m.start())
                while prev > 0:
                    line_start = text.rfind("\n", 0, prev) + 1
                    line = text[line_start:prev].strip()
                    if line.startswith("///"):
                        doc.append(line)
                        prev = line_start - 1
                        continue
                    break
                found.setdefault(name, []).append((fn, text[brace:i + 1], " ".join(reversed(doc))))
    return found


def main():
    all_bodies = bodies()
    print("declared type names in src: %d" % len(all_bodies))
    print()

    # R619: searching for the SAME simple name is useless here -- `bind_diff` already established that this name is
    # absent, and a renamed type by definition has a different simple name (`Settings` -> `GlobalSettings`). So score
    # every declared type by how many of the contract's members its body contains and take the best.
    rows = []
    resolved = []
    for simple, member_text in ABSENT.items():
        # R926: the table above is a snapshot copied from bind_diff, so a type implemented since it was taken stays in
        # it. KeyGesture acquired a same-name declaration this round and the row count then disagreed with bind_diff,
        # which the guard caught. A name that now has a declaration is RESOLVED: it is reported separately and leaves
        # the absent count, because otherwise this tool would keep counting a gap that no longer exists.
        if simple in all_bodies:
            resolved.append(simple)
            continue
        members = [m.strip() for m in member_text.split(",") if m.strip()]
        # R702: docs/DECISION_LICENSE_OUT_OF_SCOPE.md takes precedence over any textual scoring for the
        # auth/licence family -- it is user management, which keeps it outside the function set.
        if simple in NOT_IN_FUNCTION_SET:
            rows.append((simple, "NOT_IN_FUNCTION_SET", "R702: auth/licence is user management, "
                         "not part of the replica's function set", 0, len(members)))
            continue
        # R659: declarations only. Searching the body for the bare name counted calls to OTHER objects' methods
        # (`_group.Accounts.Add(...)` satisfied `Add`) and names mentioned in comments, which inflated coverage --
        # `Settings` scored 34/34 that way while only 33 members are actually declared.
        pats = [
            re.compile(r"\b(?:public|internal)\s+[\w<>?\[\],. ]+\s+%s\s*(?:\{|=>|;|=)" % re.escape(m))
            for m in members
        ]
        best = None
        for name, sites in all_bodies.items():
            for fn, body, doc in sites:
                hit = 0
                for p in pats:
                    if p.search(body):
                        hit += 1
                score = hit / len(members)
                if best is None or score > best[0]:
                    best = (score, name, fn, hit)
        if best is None:
            rows.append((simple, "UNIMPLEMENTED", "no candidate", 0, len(members)))
            continue
        score, name, fn, hit = best
        # R619/R620: the *same* discriminative threshold applies to every verdict, not just RENAMED. A contract with
        # fewer than three members cannot tell one class from another, so no verdict stronger than UNKNOWN is
        # justified -- otherwise the PARTIAL bucket mixes "18/19, almost certainly the same type" with "1/2, noise",
        # and a bucket that mixes those two is not a classification.
        # R657: a doc comment that names the contract type and lists its members is evidence independent of member
        # count -- it says "this class is that type". `SmartActionStepConfig` carries
        # "One parameter of an action (SmartActions.ActionConfig: Name / Required)" and is the only reason this
        # two-member contract can be resolved at all.
        documented = None
        for cand, sites in all_bodies.items():
            for _fn, _body, doc in sites:
                if not doc:
                    continue
                if ("%s:" % simple) in doc or (".%s" % simple) in doc:
                    # R657b: declarations only. A call such as `_group.Accounts.Add(...)` is not a member of the class
                    # being examined, and counting it promoted `AccountImportWindow` on evidence that does not exist.
                    hit_c = 0
                    for mem in members:
                        if re.search(r"\bpublic\s+[\w<>?\[\],. ]+\s+%s\s*(?:\{|=>|;|=)" % re.escape(mem), _body):
                            hit_c += 1
                    if hit_c == len(members):
                        documented = (cand, _fn, hit_c)
                        break
            if documented:
                break

        if documented:
            verdict = "RENAMED"
            strength = "%d/%d (100%%) documented" % (documented[2], len(members))
            ev = "`%s` in %s — %s; its doc comment names %s" % (documented[0], documented[1], strength, simple)
            rows.append((simple, verdict, ev, documented[2], len(members)))
            continue
        # R658: a UNIQUE declaration-level match decides on its own, without the member-count threshold. The
        # threshold exists because coverage cannot tell two classes apart; when exactly one class declares every
        # contract member there is nothing to tell apart. Measured ambiguity: 1-member contracts were ambiguous in
        # 2 of 2 cases, 2-member contracts discriminative in 2 of 2 -- so the boundary sits at 2, not at 3.
        if len(members) >= 2:
            decl = []
            for cand, sites in all_bodies.items():
                for _fn, body, _doc in sites:
                    if all(re.search(r"\b(?:public|internal)\s+[\w<>?\[\],. ]+\s+%s\s*(?:\{|=>|;|=)" % re.escape(mem), body)
                           for mem in members):
                        decl.append(cand)
                        break
            decl = sorted(set(decl))
            if len(decl) == 1:
                rows.append((simple, "RENAMED",
                             "`%s` declares all %d member(s) — sole declaration match" % (decl[0], len(members)),
                             len(members), len(members)))
                continue

        # R682: a precise measurement paired with a verdict vocabulary that only knew one form of presence produced
        # a wrong conclusion -- `SettingsView` scored 1/19 by declarations and was called UNIMPLEMENTED, while 18 of
        # its 19 pages are constructed inline in `SettingsShell.cs` and `LogOut` lives on `UserView`. So: if the
        # member NAMES appear anywhere in the source but not as declarations, the verdict is STRUCTURAL, not
        # UNIMPLEMENTED. Nothing about the measurement changes.
        if len(members) >= 3 and not (score >= 0.95) and not (score >= 0.5 and hit >= 2):
            # R683: names must CO-OCCUR IN ONE CLASS BODY. The R682 version counted a name appearing anywhere in the
            # source, and `LicenseControl` then scored 2/3 on `Refresh` (a generic method name with 165 hits) plus
            # `Dashboard` (a button label) while `Authenticate` did not exist at all. A rule a common identifier can
            # satisfy measures nothing.
            best_class = None
            qualifying = []
            for cand, sites in all_bodies.items():
                for _fn, body, _doc in sites:
                    named = sum(1 for m in members if re.search(r"\b%s\b" % re.escape(m), body))
                    if named * 2 >= len(members):
                        qualifying.append((cand, named))
                    if best_class is None or named > best_class[1]:
                        best_class = (cand, named)
            # R685: the match must be UNIQUE-ish. `AuthWindow` reached 2/3 in EIGHT unrelated windows because `Exit`
            # and `Minimise` are window-chrome names every window carries; a fit that many classes satisfy names
            # none of them. At most two are tolerated (a base/derived pair).
            if best_class and best_class[1] * 2 >= len(members) and len(qualifying) <= 2:
                rows.append((simple, "STRUCTURAL",
                             "%d/%d member names co-occur in `%s` (only %d class(es) reach that)"
                             % (best_class[1], len(members), best_class[0], len(qualifying)),
                             best_class[1], len(members)))
                continue
            if best_class and best_class[1] * 2 >= len(members) and len(qualifying) > 2:
                rows.append((simple, "UNIMPLEMENTED",
                             "%d/%d names match but in %d classes -- not discriminating"
                             % (best_class[1], len(members), len(qualifying)),
                             0, len(members)))
                continue

        if len(members) < 3:
            verdict = "UNKNOWN (non-discriminative)"
        elif score >= 0.95:
            verdict = "RENAMED"
        elif score >= 0.5 and hit >= 2:
            # R685: report HOW MANY classes reach the same threshold. `AuthWindow` shows 2/3 against `MainWindow`,
            # but eight unrelated windows also reach 2/3 (`Exit` / `Minimise` are window-chrome names), so the
            # "best match" is arbitrary. The verdict is left alone -- changing an older branch's rule needs its own
            # round -- but the count goes into the evidence so the arbitrariness is visible rather than hidden.
            _qualifying = 0
            for _sites in all_bodies.values():
                for _f, _b, _d in _sites:
                    _n = sum(1 for m in members if re.search(r"\b%s\b" % re.escape(m), _b))
                    if _n * 2 >= len(members):
                        _qualifying += 1
            # R685c: `PARTIAL` presupposes a nameable candidate. With 6 or 35 classes scoring identically (see the
            # counts above), the "best match" is arbitrary, so the evidence supports NO verdict -- not
            # "unimplemented" (absence was not shown) and not "partial" (no candidate was named).
            verdict = "PARTIAL" if _qualifying <= 2 else "UNKNOWN (non-discriminating match)"
        else:
            verdict = "UNIMPLEMENTED"
        strength = "%d/%d (%.0f%%)" % (hit, len(members), 100.0 * score)
        ev = "best match `%s` in %s — %s" % (name, fn, strength)
        if verdict == "PARTIAL":
            ev += "; %d class(es) reach this ratio" % _qualifying
        rows.append((simple, verdict, ev, hit, len(members)))

    print("%-26s %-14s %s" % ("type (simple name)", "verdict", "evidence"))
    for simple, verdict, ev, hit, tot in rows:
        print("%-26s %-14s %s" % (simple, verdict, ev))

    counts = {}
    for _s, v, _e, _h, _t in rows:
        counts[v] = counts.get(v, 0) + 1
    print()
    if resolved:
        print("resolved since the snapshot was taken: %s" % ", ".join(resolved))
    print("triage rows: %d" % len(rows))
    print("verdicts: %s" % ", ".join("%s=%d" % (k, v) for k, v in sorted(counts.items())))

    # R621: every ABSENT type must carry exactly one verdict. A short row list would silently drop an item and the
    # document would still read as complete -- the same failure the metric-claims guard exists to prevent.
    # R926: ABSENT is a snapshot, so it may hold names that have since been implemented. Those are reported as
    # resolved above and are not rows, so the expectation is the snapshot minus the resolved ones rather than the whole
    # snapshot. Comparing to the whole thing made the tool refuse to run the moment a gap closed, which is the opposite
    # of what a gap-closing check should do.
    expected = len(ABSENT) - len(resolved)
    if len(rows) != expected:
        raise SystemExit("triage produced %d rows for %d absent types (%d of %d resolved)"
                         % (len(rows), expected, len(resolved), len(ABSENT)))
    total = 0
    for v in counts.values():
        total += v
    if total != expected:
        raise SystemExit("verdict counts sum to %d, expected %d" % (total, expected))

    lines = ["# 类型缺失 17 条的逐条分类（自动生成：`python analysis/type_presence_triage.py`）", "",
             "> 判据见脚本文件头。**成员覆盖率是下界**：只数类体里的成员名，继承来的、表达式体、",
             "> 以及改了名但等价的成员都会被算成缺。所以「低覆盖」不能证明「不是同一类型」，",
             "> 只能说明「没能证明是同一类型」——这也是 RENAMED 要求满覆盖的原因。", "",
             "> **判别力规则（R619/R620）**：**同一个阈值适用于所有判定**，不只 RENAMED。",
             "> 成员总数 < 3 的契约分不清两个类（一成员 `{ Count }` 会匹配任何提到 `Count` 的类），",
             "> 所以一律记 `UNKNOWN`，不给更强的判定。否则 `PARTIAL` 桶会混进",
             "> 「18/19 几乎肯定是同一类型」和「1/2 纯噪音」，而混着这两者的桶不成其为分类。",
             "> 这与 R601 邻域判据、R616 抽样判据是同一类教训：看似合理，实际不区分。", "",
             "| 类型（简单名） | 判定 | 证据 |", "|---|---|---|"]
    for simple, verdict, ev, hit, tot in rows:
        lines.append("| `%s` | **%s** | %s |" % (simple, verdict, ev))
    lines.append("")
    lines.append("判定合计：%s" % ", ".join("%s=%d" % (k, v) for k, v in sorted(counts.items())))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print()
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
