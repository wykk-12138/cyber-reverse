"""Who owns each ABSENT type's members in the replica? (member-level, not type-level)

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
`type_rename_map.py` answers "which class looks most like this whole type" by averaging over all its
members. That is the wrong granularity for the B/C groups left in `BINDING_BACKLOG.md`: those types are
ABSENT, but a *single member* like `Proxy` or `Action` may well exist — it just lives on whatever class
took over the role. Averaging hides that: a 9-member type scores 8/9 and looks "present", while a
1-member type scores 0/1 and looks "missing", even when the one member is right there under another name.

So this asks the narrow question per member: **in which class bodies does this member name appear?**
The answer decides each row:
    - exactly one class  -> the role was RENAMED/MERGED into that class (structural difference)
    - many classes       -> the member name is generic (`Name`/`Type`/`Key`); carries no information
    - no class           -> the member genuinely does not exist anywhere (a real gap candidate)

Body extraction is the same brace-matching rule as `bind_scope.py`.

Reproduce:
    cd replica
    python tools/member_owner_map.py                 # every ABSENT type from ../analysis/type_presence.txt
    python tools/member_owner_map.py --type Captcha
    python tools/member_owner_map.py --max-owners 8
"""

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")
PRESENCE = os.path.abspath(os.path.join(ROOT, "..", "analysis", "type_presence.txt"))
OUT = os.path.abspath(os.path.join(ROOT, "..", "analysis", "member_owner_map.md"))

DECL = re.compile(r"\b(?:class|record|struct|enum|interface)\s+(\w+)\s*(?::\s*([^;{]+?))?\s*(?:where[^;{]*)?\{")


def strip_comments(text):
    """R442: the first version of this tool scanned raw bodies and reported `SettingsView.LogOut` as
    "single owner -> UserView" — but UserView only *mentions* LogOut in a doc comment; it has no such
    member. AGENTS.md's measuring rule is "削注释（注释里的名字不算实现）", the R249 lesson, and this is
    the second time in two rounds that prose got counted as code (the other was the R439 source guard).
    Same rule here, so the answer means the same thing as bind_diff/bind_scope."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?<!:)//[^\n]*", " ", text)


def bodies_by_name():
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
                            found.setdefault(match.group(1), []).append(strip_comments(text[start:index + 1]))
                            break
    return found


def absent_types():
    if not os.path.exists(PRESENCE):
        raise SystemExit("missing %s - run: cd replica; python tools/bind_diff.py --type-presence" % PRESENCE)
    raw = io.open(PRESENCE, "rb").read()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    rows = []
    for line in text.splitlines():
        m = re.match(r"\s+ABSENT\s+(\S+)\s+\(members: (.+)\)", line)
        if m:
            rows.append((m.group(1), [x.strip() for x in m.group(2).split(",")]))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--type", default=None, help="only types whose short name contains this")
    parser.add_argument("--max-owners", type=int, default=6)
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    targets = absent_types()
    if args.type:
        targets = [t for t in targets if args.type.lower() in t[0].lower()]

    bodies = bodies_by_name()
    names = sorted(bodies)

    lines = ["# 每个 ABSENT 成员的归属类（生成文件，请勿手改）", "",
             "> 由 `python tools/member_owner_map.py` 生成。**成员级**问题：这个成员名在哪些类的 body 里出现？",
             "> 用途：把 B/C 组里\"判不了\"的条目分成三类 —— 唯一归属（改名/合并）、归属过多（通用词，无信息）、",
             "> 零归属（真缺）。Body 提取规则与 `bind_scope.py` 相同。", ""]

    buckets = {"one": [], "many": [], "none": []}
    for full, members in targets:
        lines.append("## `%s`" % full)
        lines.append("")
        lines.append("| 成员 | 归属类 | 判读 |")
        lines.append("|---|---|---|")
        for member in members:
            needle = re.compile(r"\b" + re.escape(member) + r"\b")
            owners = [n for n in names if any(needle.search(b) for b in bodies[n])]
            if not owners:
                verdict = "**零归属 — 真缺候选**"
                buckets["none"].append((full, member))
            elif len(owners) == 1:
                verdict = "唯一归属 → 改名/合并"
                buckets["one"].append((full, member, owners[0]))
            else:
                verdict = "归属过多 → 通用词，无信息"
                buckets["many"].append((full, member))
            shown = "、".join("`%s`" % o for o in owners[:args.max_owners])
            if len(owners) > args.max_owners:
                shown += " …共 %d 个" % len(owners)
            lines.append("| `%s` | %s | %s |" % (member, shown or "（无）", verdict))
        lines.append("")

    lines += ["---", "",
              "## 汇总", "",
              "| 判读 | 条数 |", "|---|---|",
              "| 唯一归属（改名/合并） | %d |" % len(buckets["one"]),
              "| 归属过多（通用词） | %d |" % len(buckets["many"]),
              "| 零归属（真缺候选） | %d |" % len(buckets["none"]),
              ""]

    if buckets["one"]:
        lines += ["### 唯一归属的成员（可直接写进账本）", "", "| 类型 | 成员 | 归属类 |", "|---|---|---|"]
        for full, member, owner in buckets["one"]:
            lines.append("| `%s` | `%s` | `%s` |" % (full, member, owner))
        lines.append("")
    if buckets["none"]:
        lines += ["### 零归属的成员（真缺候选）", "", "| 类型 | 成员 |", "|---|---|"]
        for full, member in buckets["none"]:
            lines.append("| `%s` | `%s` |" % (full, member))
        lines.append("")

    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print("member owner map: %d absent types" % len(targets))
    print("  single owner (renamed/merged) : %d" % len(buckets["one"]))
    print("  too many owners (generic word): %d" % len(buckets["many"]))
    print("  no owner (real gap candidate) : %d" % len(buckets["none"]))
    print()
    for full, member, owner in buckets["one"]:
        print("  ONE   %-46s %-14s -> %s" % (full.split("Cybersole.")[-1], member, owner))
    print()
    for full, member in buckets["none"]:
        print("  NONE  %-46s %s" % (full.split("Cybersole.")[-1], member))
    print()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
