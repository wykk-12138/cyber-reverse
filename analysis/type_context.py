"""Binding-descriptor neighbourhoods: which types share a compiled XAML block with each ABSENT type?

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
`BINDING_BACKLOG.md`'s B group (19 types whose only members are `Name`/`Type`/`Key`/`Value`) cannot be
classified from the source alone — a member name like `Name` carries no information. But the original's
compiled XAML leaves a much better clue: each binding-descriptor string is a *contiguous block* for one
XAML file/control template, so every type listed in the same string is bound in the same place. Reading a
type's **neighbours** therefore says which page/panel it belongs to.

`analysis/ida.py` can search one pattern and print the raw matches, but it neither batches nor extracts the
neighbour types; doing 51 searches by hand and reading 51 blobs is exactly the kind of step that produces
guesses. This script batches the search, extracts every `Cybersole.*` type mentioned alongside the target,
and writes one reviewable table.

What this yields: **Inference, medium confidence** — "bound in the same XAML block as X" is not the same as
"is the model of X's page", because one block can span a page and its modal. The output says which types
co-occur and at which address, so the reading can be checked.

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/type_context.py                 # every ABSENT type from analysis/type_presence.txt
    python analysis/type_context.py --type RemoteData
    python analysis/type_context.py --limit 5
"""

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANALYSIS = os.path.join(ROOT, "analysis")
PRESENCE = os.path.join(ANALYSIS, "type_presence.txt")
OUT = os.path.join(ANALYSIS, "type_context.md")

sys.path.insert(0, ANALYSIS)
import ida  # noqa: E402  - reuse the existing client: same endpoint, same protocol, no second implementation

TYPE_RE = re.compile(r"Cybersole\.[A-Za-z0-9_.]+")


def known_types():
    """The binding table's own type names.

    A descriptor block looks like `Cybersole.Models.RemoteData,Cybersole.Core.Name!Getter`, i.e.
    `<type>,<assembly>.<member>!<accessor>`. A naive `Cybersole\\.[\\w.]+` scan therefore harvests
    `Cybersole.Core.Name` — which is the *assembly plus member name*, not a type — and the first version of
    this tool reported those as neighbours. Restricting neighbours to names the binding table actually
    declares removes that whole class of noise.
    """
    binds = json.load(io.open(os.path.join(ROOT, "replica", "docs", "xaml_bindings.json"), encoding="utf-8"))
    return sorted(binds.keys(), key=len, reverse=True)


def neighbours_in(text, known, exclude):
    found = []
    for name in known:
        if name == exclude:
            continue
        if re.search(re.escape(name) + r"(?![A-Za-z0-9_])", text):
            found.append(name)
    return found


def absent_types():
    """Read the ABSENT list written by `replica/tools/bind_diff.py --type-presence`."""
    if not os.path.exists(PRESENCE):
        raise SystemExit("missing %s — run: cd replica; python tools/bind_diff.py --type-presence"
                         % PRESENCE)
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
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    targets = absent_types()
    if args.type:
        targets = [t for t in targets if args.type.lower() in t[0].lower()]
    if args.limit:
        targets = targets[:args.limit]

    ida.initialize()
    known = known_types()

    results = []
    for full, members in targets:
        pattern = re.escape(full)
        raw = ida.call("find_regex", {"pattern": pattern, "limit": 60})
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            results.append((full, members, [], "unparsable reply"))
            continue
        blocks = payload.get("matches") or []
        neighbours = {}
        for block in blocks:
            text = block.get("string") or ""
            for other in neighbours_in(text, known, full):
                neighbours[other] = neighbours.get(other, 0) + 1
        ranked = sorted(neighbours.items(), key=lambda kv: -kv[1])
        results.append((full, members, [block.get("addr") for block in blocks], ranked))

    lines = ["# 绑定描述符邻居（生成文件，请勿手改）", "",
             "> 由 `python analysis/type_context.py` 生成。目标：给 `bind_diff.py --type-presence` 列出的",
             "> ABSENT 类型找**同一个编译期 XAML 块里的邻居**，从而推断它属于哪个页面/面板。", "",
             "> **证据等级：Inference（中）** —— 同一个块里出现 ≠ 同一个页面的模型（一个块可以同时覆盖",
             "> 页面与其弹窗）。所以每行都给了地址，供回查原文。", ""]

    for full, members, blocks, ranked in results:
        lines.append("## `%s`  (%d members: %s)" % (full, len(members), ", ".join(members)))
        lines.append("")
        if not blocks:
            lines.append("**描述符串里没有出现** —— 该类型不是任何已编译 XAML 的绑定目标，")
            lines.append("（或字符串池已截断）。它的职责无法从绑定块推断，仍需反编译或 GUI 观察。")
            lines.append("")
            continue
        lines.append("出现于 %d 个描述符块：%s" % (len(blocks), "、".join("`%s`" % a for a in blocks)))
        lines.append("")
        if not ranked:
            lines.append("（块内没有其它 Cybersole 类型）")
            lines.append("")
            continue
        lines.append("| 邻居类型 | 同现次数 |")
        lines.append("|---|---|")
        for other, count in ranked[:12]:
            lines.append("| `%s` | %d |" % (other, count))
        lines.append("")

    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print("type context: %d targets" % len(results))
    for full, members, blocks, ranked in results:
        top = ranked[0][0] if ranked else "(no block)"
        print("  %-46s %d block(s)  top neighbour: %s" % (full.split("Cybersole.")[-1], len(blocks), top))
    print()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
