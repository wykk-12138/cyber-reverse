r"""Extract the original's *binding descriptor table* out of its string pool, and diff it against XAML.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
Every existing binding tool (`bind_diff.py`, `bind_scope.py`, `type_rename_map.py`, `member_owner_map.py`)
takes `docs/xaml_bindings.json` as its notion of "what the original binds". That input only covers members
**XAML** touches, so pure-C# models (`Models.Flag`, `MonitorProduct`, `Input`, …) are invisible — and those
are exactly the types `BINDING_BACKLOG.md` records as "职责未定性".

R456 found that the original does not hide this: its compiled binding descriptors sit in the string pool as
readable blocks of

    <declaring type>,<assembly>.<member>!<Getter|Setter>

so *which type owns which member, and whether it has a setter* is stated by the binary itself. No
pseudocode, no symbol recovery, no third decompiler needed.

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/binding_descriptors.py
Outputs:
    analysis/binding_descriptors_raw.txt   every matching string block, verbatim
    analysis/binding_descriptors.tsv       declaring_type \t owner_assembly \t member \t accessor
    analysis/binding_descriptors.md        summary + symmetric difference against xaml_bindings.json
"""

import argparse
import collections
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANALYSIS = os.path.join(ROOT, "analysis")
BINDS = os.path.join(ROOT, "replica", "docs", "xaml_bindings.json")
RAW_OUT = os.path.join(ANALYSIS, "binding_descriptors_raw.txt")
TSV_OUT = os.path.join(ANALYSIS, "binding_descriptors.tsv")
MD_OUT = os.path.join(ANALYSIS, "binding_descriptors.md")

sys.path.insert(0, ANALYSIS)
import ida  # noqa: E402 - reuse the existing client (same endpoint, same protocol)

# Blocks are concatenations, sometimes with a one-character prefix (`t`, `d`, `P`) and no separator.
DESCRIPTOR = re.compile(
    rb"([A-Za-z_][\w.`]*\.[A-Za-z_][\w.`]*),([A-Za-z_][\w.`]*\.[A-Za-z_][\w.`]*)!(Getter|Setter)"
)

# The single-character prefix survives the regex above and lands inside the declaring type:
# `nCybersole.Models.User`, `PAvalonia.Size`, `zCybersole.SmartActions.Filter`. Left alone, every one of
# those types looks "absent from the table" when it is actually present — the first run of this tool
# reported 13 such false negatives. Strip the prefix only when what follows is a known root namespace, so a
# genuine one-letter namespace is not mangled.
ROOTS = {
    "Cybersole", "Avalonia", "System", "Microsoft", "Newtonsoft", "Jint", "BouncyCastle",
    "SkiaSharp", "HarfBuzzSharp", "Tmds", "Interop", "ABI", "Internal", "MicroCom",
}


def clean_type(name):
    parts = name.split(".")
    if parts and len(parts[0]) > 1 and parts[0][1:] in ROOTS:
        parts[0] = parts[0][1:]
    return ".".join(parts)

PAGE = 200          # the plugin rejects larger limits
MAX_PAGES = 80


def all_blocks(pattern):
    """Page through search hits.

    The plugin's paging parameter is `offset` (not the `cursor` the reply advertises — passing `cursor`
    is rejected with "unexpected parameters"). R456's brief assumed a cursor; measured otherwise.
    """
    ida.initialize()
    out = []
    offset = 0
    for _ in range(MAX_PAGES):
        args = {"pattern": pattern, "limit": PAGE}
        if offset:
            args["offset"] = offset
        res = ida.call("find_regex", args, timeout=900)
        try:
            payload = json.loads(res)
        except json.JSONDecodeError:
            print("  unparsable page for %s at offset %d: %s" % (pattern, offset, res[:120]))
            break
        matches = payload.get("matches") or []
        out.extend(matches)
        cursor = payload.get("cursor") or {}
        nxt = cursor.get("next")
        if cursor.get("done") or not matches or nxt is None or nxt <= offset:
            break
        offset = nxt
    print("  %s -> %d blocks" % (pattern, len(out)))
    return out


def parse(blocks):
    rows = []
    for block in blocks:
        text = (block.get("string") or "").encode("utf-8", "replace")
        for match in DESCRIPTOR.finditer(text):
            decl = clean_type(match.group(1).decode("utf-8", "replace"))
            owner = match.group(2).decode("utf-8", "replace")
            accessor = match.group(3).decode("utf-8", "replace")
            assembly, _, member = owner.rpartition(".")
            rows.append((decl, assembly, member, accessor, block.get("addr")))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--md-out", default=MD_OUT)
    args = parser.parse_args(argv)

    blocks = all_blocks("!Getter") + all_blocks("!Setter")
    unique_blocks = {}
    for block in blocks:
        unique_blocks[block.get("addr")] = block.get("string") or ""
    print("distinct blocks: %d" % len(unique_blocks))

    io.open(RAW_OUT, "w", encoding="utf-8").write(
        "\n".join("%s\t%s" % (addr, text.replace("\n", "\\n"))
                  for addr, text in sorted(unique_blocks.items())) + "\n")

    rows = parse([{"string": text, "addr": addr} for addr, text in unique_blocks.items()])
    triples = sorted({(decl, assembly, member, accessor) for decl, assembly, member, accessor, _ in rows})
    print("descriptors: %d raw, %d unique (declaring_type, assembly, member, accessor)" % (len(rows), len(triples)))

    io.open(TSV_OUT, "w", encoding="utf-8").write(
        "declaring_type\towner_assembly\tmember\taccessor\n"
        + "\n".join("\t".join(t) for t in triples) + "\n")

    # symmetric difference against the XAML-derived table
    binds = json.load(io.open(BINDS, encoding="utf-8"))
    xaml_pairs = {(typ, member) for typ, members in binds.items() for member in members}
    desc_pairs = {(decl, member) for decl, _a, member, _acc in triples}

    only_desc = sorted(desc_pairs - xaml_pairs)
    only_xaml = sorted(xaml_pairs - desc_pairs)
    shared = desc_pairs & xaml_pairs

    per_type = collections.Counter(decl for decl, _a, _m, _acc in triples)
    setters = {(decl, member) for decl, _a, member, acc in triples if acc == "Setter"}
    getters = {(decl, member) for decl, _a, member, acc in triples if acc == "Getter"}

    lines = ["# 原版绑定描述符表（生成文件，请勿手改）", "",
             "> 由 `python analysis/binding_descriptors.py` 生成。原版把编译期绑定描述符以可读串摊在字符串池里，",
             "> 形式是 `<声明类型>,<程序集>.<成员>!<Getter|Setter>`。**这是原版自己的说法**，不是推断。", "",
             "| 项 | 值 |", "|---|---|",
             "| 描述符块（去重） | %d |" % len(unique_blocks),
             "| 解析出的三元组（去重） | %d |" % len(triples),
             "| 涉及声明类型 | %d |" % len(per_type),
             "| Getter 条目 | %d |" % len(getters),
             "| Setter 条目 | %d |" % len(setters),
             "| 与 `xaml_bindings.json` 共有 | %d |" % len(shared),
             "| **仅描述符表有**（XAML 表看不见） | **%d** |" % len(only_desc),
             "| 仅 XAML 表有（需单独解释，**不等于不存在**） | %d |" % len(only_xaml),
             ""]

    lines += ["## 仅描述符表有的 (type, member)", "",
              "这些就是 `xaml_bindings.json` 看不到、但原版确实绑定的成员。", ""]
    for typ, member in only_desc[:200]:
        lines.append("- `%s` . `%s`%s" % (typ, member, "  *(有 setter)*" if (typ, member) in setters else ""))
    if len(only_desc) > 200:
        lines.append("- …共 %d 条" % len(only_desc))
    lines.append("")

    lines += ["## 按声明类型统计（前 40）", "", "| 类型 | 描述符条数 |", "|---|---|"]
    for typ, count in per_type.most_common(40):
        lines.append("| `%s` | %d |" % (typ, count))
    lines.append("")

    io.open(args.md_out, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print()
    print("distinct declaring types: %d" % len(per_type))
    print("getter entries: %d | setter entries: %d" % (len(getters), len(setters)))
    print("shared with xaml_bindings.json: %d" % len(shared))
    print("ONLY in descriptors (invisible to the XAML table): %d" % len(only_desc))
    print("only in xaml table: %d" % len(only_xaml))
    print()
    print("wrote %s" % TSV_OUT)
    print("wrote %s" % args.md_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
