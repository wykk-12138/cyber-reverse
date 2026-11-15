"""Type rename map: for every ABSENT binding-table type, which replica class now plays that role?

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
`bind_diff.py --type-presence` answers one question — "is there a declaration with this name?" — and
`bind_scope.py` answers another — "is this member inside that type's body?". Neither can answer the
question R434 left open: **which class plays this role now**. AGENTS.md §0 explicitly allows the
replica to use different type names, so most of the 51 ABSENT types are renames, not gaps; deciding
that requires matching a *member set* against every class body, which no existing tool does.

Body extraction is copied from `bind_scope.py` (brace matching from the declaration's opening brace),
not re-invented: same rule, same answers.

How to read the output:
    HIGH    every member is present in that class's own body, and the member set is big enough to be
            distinctive (>= 2 members), OR the class name shares the type's stem.
    MEDIUM  at least half the members are present — a lead, not a conclusion.
    LOW     one or two hits; with common names like `Name`/`Type` this is usually coincidence.

A candidate is a **lead to verify by reading the class**, never a verdict: two unrelated classes can
share member names. The tool's job is to make the 51 rows reviewable; the classification itself
(RENAMED / UNIMPLEMENTED) belongs in `replica/docs/BINDING_BACKLOG.md`.

Reproduce:
    cd replica
    python tools/type_rename_map.py                 # summary + per-type candidates
    python tools/type_rename_map.py --min-members 2  # ignore single-member types (noisiest)
    python tools/type_rename_map.py --type Input
"""

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "docs", "TYPE_RENAME_MAP.md")

DECL = re.compile(r"\b(?:class|record|struct|enum|interface)\s+(\w+)\s*(?::\s*([^;{]+?))?\s*(?:where[^;{]*)?\{")


def bodies_by_name():
    """Every declaration's own body, keyed by short type name (same rule as bind_scope.py)."""
    found = {}
    for dirpath, _dirnames, filenames in os.walk(SRC):
        if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
            continue
        for filename in filenames:
            if not filename.endswith(".cs"):
                continue
            text = io.open(os.path.join(dirpath, filename), encoding="utf-8", errors="replace").read()
            for match in DECL.finditer(text):
                depth = 0
                start = match.end() - 1
                for index in range(start, len(text)):
                    if text[index] == "{":
                        depth += 1
                    elif text[index] == "}":
                        depth -= 1
                        if depth == 0:
                            found.setdefault(match.group(1), []).append(text[start:index + 1])
                            break
    return found


def stem(name):
    """Rough stem so `SettingsView` and `SettingsShell` both reduce to `settings`."""
    return re.sub(r"(view|model|modal|window|shell|entry|option|control|creator|provider)$", "", name.lower())


def score(body, members):
    hits = [m for m in members if re.search(r"\b" + re.escape(m) + r"\b", body)]
    return hits, (len(hits) / len(members)) if members else 0.0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-members", type=int, default=1, help="skip types with fewer members")
    parser.add_argument("--top", type=int, default=3, help="candidates shown per type")
    parser.add_argument("--type", default=None, help="only this type (substring)")
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    binds = json.load(io.open(BINDS, encoding="utf-8"))
    bodies = bodies_by_name()
    names = sorted(bodies)

    absent = []
    for full, members in sorted(binds.items()):
        short = full.split(".")[-1].split("`")[0]
        if short in bodies:
            continue                       # present by name: not this tool's business
        absent.append((full, short, sorted(members)))

    rows = []
    for full, short, members in absent:
        if len(members) < args.min_members:
            continue
        if args.type and args.type.lower() not in short.lower():
            continue
        scored = []
        for name in names:
            body = "\n".join(bodies[name])
            hits, ratio = score(body, members)
            if not hits:
                continue
            same_stem = stem(name) == stem(short) and len(stem(short)) >= 4
            level = "HIGH" if (ratio >= 1.0 and len(members) >= 2) or (same_stem and ratio >= 0.5) else \
                    "MEDIUM" if ratio >= 0.5 else "LOW"
            scored.append((level, name, len(hits), len(members), ratio, same_stem))
        scored.sort(key=lambda r: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r[0]], -r[4], -r[2]))
        rows.append((full, short, members, scored[:args.top]))

    high = [r for r in rows if r[3] and r[3][0][0] == "HIGH"]
    med = [r for r in rows if r[3] and r[3][0][0] == "MEDIUM"]
    none = [r for r in rows if not r[3]]

    lines = ["# 类型改名候选图（生成文件，请勿手改）", "",
             "> 由 `python tools/type_rename_map.py` 生成。用途：把 `bind_diff.py --type-presence` 列出的",
             "> ABSENT 类型逐条变成**可审阅的候选**，再由人工在 `replica/docs/BINDING_BACKLOG.md` 里判",
             "> RENAMED / UNIMPLEMENTED。**候选不是结论** —— 两个无关类可能共享成员名（`Name`/`Type` 尤其）。", ""]
    lines += ["| 项 | 值 |", "|---|---|",
              "| 绑定表类型 | %d |" % len(binds),
              "| 源码里存在的同名类型 | %d |" % (len(binds) - len(absent)),
              "| ABSENT（本次审阅对象） | %d |" % len(absent),
              "| 其中有 HIGH 候选 | %d |" % len(high),
              "| 其中有 MEDIUM 候选 | %d |" % len(med),
              "| 完全没有候选 | %d |" % len(none),
              "", "## 逐条候选", ""]

    for full, short, members, scored in rows:
        lines.append("### `%s`  (%d members: %s)" % (full, len(members), ", ".join(members)))
        lines.append("")
        if not scored:
            lines.append("**无候选** —— 没有任何类持有这些成员名。按 UNIMPLEMENTED 处理前仍需读一遍绑定串上下文。")
            lines.append("")
            continue
        lines.append("| 级别 | 候选类 | 命中 | 同名干 |")
        lines.append("|---|---|---|---|")
        for level, name, hits, total, ratio, same_stem in scored:
            lines.append("| %s | `%s` | %d/%d | %s |" % (level, name, hits, total, "是" if same_stem else ""))
        lines.append("")

    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print("type rename map: %d absent types reviewed" % len(rows))
    print("  HIGH candidate   : %d" % len(high))
    print("  MEDIUM candidate : %d" % len(med))
    print("  no candidate     : %d" % len(none))
    print()
    for full, short, members, scored in rows:
        top = scored[0] if scored else None
        if top:
            print("  %-46s %-6s -> %-28s %d/%d" % (short, top[0], top[1], top[2], top[3]))
        else:
            print("  %-46s %-6s -> (none) %d members" % (short, "NONE", len(members)))
    print()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
