r"""Locale keys taken straight from the original binary's bytes, as a third opinion.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
Every existing locale metric -- `locale_coverage.py`, `locale_text_gap.py`, `copy_audit_report.py` -- reads
`analysis/pe_strings.txt`. That makes them **one path**: if the string dump is incomplete, all three agree
with each other and all three are wrong. R433 already learned this shape of mistake elsewhere (six documents
quoting numbers nobody regenerated).

This reads `target/Cybersole.exe` directly, decodes it as UTF-8, and pulls `"Area.Key": "value"` pairs out of
the raw bytes. It then reports three asymmetries that matter:

    in binary, not in the pool      -> the dump is incomplete; every locale metric inherits that blind spot
    in binary, not in the replica   -> a real copy gap (this is what claim C14 is about)
    in the replica, not in binary   -> the replica invented a key; the original never emits it

What this is NOT: a JSON parse. The locale payload is one big block; regex extraction survives truncation
and mis-nesting, which a strict parse would refuse. So "key exists" here means "this exact `"K": "` pair
appears in the bytes", not "the document is well formed".

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/locale_from_binary.py
    python analysis/locale_from_binary.py --area Monitor
"""

import argparse
import collections
import io
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINARY = os.path.join(ROOT, "target", "Cybersole.exe")
POOL = os.path.join(ROOT, "analysis", "pe_strings.txt")
REPLICA_LOCALES = os.path.join(ROOT, "replica", "src", "Cybersole.Core", "Locales")
OUT = os.path.join(ROOT, "analysis", "locale_from_binary.md")

# A locale key is `Area.Something(.Something)*`; require at least one dot and a capitalised head.
KEY = re.compile(rb'"([A-Z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)":\s*"')
# Keys whose head is one of these are the app's own copy families (matches docs/COPY_QUEUE.md areas).
AREAS = {
    "Auth", "Tasks", "Monitor", "Settings", "Proxies", "Profiles", "Accounts", "Analytics", "Billing",
    "Home", "Checkout", "SmartActions", "Captcha", "Release", "Data", "GroupModal", "TaskGroup",
    "TaskCreator", "HistoryWindow", "Cart", "Advanced", "ProfileCsv", "Error", "Utilities", "MonitorMode",
}


def keys_from_binary(families):
    raw = io.open(BINARY, "rb").read()
    found = collections.Counter()
    pattern = re.compile(rb'"((?:' + b"|".join(f.encode() for f in sorted(families, key=len, reverse=True))
                           + rb')\.[A-Za-z0-9_.-]+)":\s*"')
    for match in pattern.finditer(raw):
        found[match.group(1).decode("ascii", "replace")] += 1
    return found, len(raw)


def all_families_in_binary():
    """Every `"Xxx.Yyy": "` head in the bytes, so families the replica never implemented still show up."""
    raw = io.open(BINARY, "rb").read()
    heads = collections.Counter()
    for match in re.finditer(rb'"([A-Z][A-Za-z0-9_]*)\.[A-Za-z0-9_.-]+":\s*"', raw):
        heads[match.group(1).decode("ascii", "replace")] += 1
    return heads


def keys_from_pool(families):
    text = io.open(POOL, encoding="utf-8", errors="replace").read()
    found = set()
    for match in re.finditer(r'"([A-Z][\w.]*\.[\w.]+)":\s*"', text):
        name = match.group(1)
        if name.split(".")[0] in families:
            found.add(name)
    return found


def keys_from_replica():
    found = {}
    if not os.path.isdir(REPLICA_LOCALES):
        return found
    for filename in sorted(os.listdir(REPLICA_LOCALES)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(REPLICA_LOCALES, filename)
        try:
            data = json.load(io.open(path, encoding="utf-8"))
        except Exception as exc:                     # noqa: BLE001 - report, do not crash
            found[filename] = {"__parse_error__": str(exc)}
            continue
        found[filename] = data if isinstance(data, dict) else {}
    return found


def flatten(node, prefix=""):
    out = set()
    if isinstance(node, dict):
        for key, value in node.items():
            name = prefix + "." + key if prefix else key
            if isinstance(value, dict):
                out |= flatten(value, name)
            else:
                out.add(name)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--area", default=None, help="restrict to one key family")
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    replica_docs = keys_from_replica()

    # The family set comes from the replica, not a hand-written list: R446's first run used a 25-name
    # whitelist and reported 465 "invented" keys whose heads were Common / CaptchaSource / AccountsCreator —
    # all real families the list had simply missed. Deriving the set removes that whole class of noise.
    replica_union = set()
    for doc in replica_docs.values():
        replica_union |= flatten(doc)
    families = {k.split(".")[0] for k in replica_union} | AREAS

    if args.area:
        families = {args.area}

    binary, size = keys_from_binary(families)
    pool = keys_from_pool(families)

    if args.area:
        pref = args.area + "."
        binary = collections.Counter({k: v for k, v in binary.items() if k.startswith(pref)})
        pool = {k for k in pool if k.startswith(pref)}
        replica_docs = {f: {k: v for k, v in d.items() if k.startswith(pref)} for f, d in replica_docs.items()}
        replica_union = {k for k in replica_union if k.startswith(pref)}

    binary_keys = set(binary)
    per_file = {}
    for filename, doc in replica_docs.items():
        per_file[filename] = len(flatten(doc))

    only_binary = sorted(binary_keys - pool)
    missing_in_replica = sorted(binary_keys - replica_union)
    invented = sorted(replica_union - binary_keys)

    lines = ["# 从原版二进制字节直接取 locale 键（生成文件，请勿手改）", "",
             "> 由 `python analysis/locale_from_binary.py` 生成。**第三条路径**：现有三个文案工具都读",
             "> `analysis/pe_strings.txt`，如果那份转储不完整，它们会一起错。这里直接扫 `target/Cybersole.exe`。", "",
             "| 项 | 值 |", "|---|---|",
             "| 二进制大小 | %d bytes |" % size,
             "| 二进制里的 locale 键 | **%d** |" % len(binary_keys),
             "| `pe_strings.txt` 里的 locale 键 | %d |" % len(pool),
             "| 复刻件 4 个 locale 文件的键（并集） | %d |" % len(replica_union),
             ""]
    for filename, count in sorted(per_file.items()):
        lines.append("  - `%s`: %d 键" % (filename, count))
    lines += ["", "## 三种不对称", ""]
    lines += ["### 1. 二进制有、池里没有（池不完整 → 现有文案工具共同盲区）：%d" % len(only_binary), ""]
    for key in only_binary[:40]:
        lines.append("- `%s`" % key)
    if len(only_binary) > 40:
        lines.append("- …共 %d 条" % len(only_binary))
    lines += ["", "### 2. 二进制有、复刻件没有（真实文案缺口）：%d" % len(missing_in_replica), ""]
    for key in missing_in_replica[:40]:
        lines.append("- `%s`" % key)
    if len(missing_in_replica) > 40:
        lines.append("- …共 %d 条" % len(missing_in_replica))
    lines += ["", "### 3. 复刻件有、二进制没有（复刻件自己造的键）：%d" % len(invented), ""]
    for key in invented[:40]:
        lines.append("- `%s`" % key)
    if len(invented) > 40:
        lines.append("- …共 %d 条" % len(invented))
    lines.append("")

    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("binary : %d locale keys (%d bytes scanned)" % (len(binary_keys), size))
    print("pool   : %d keys" % len(pool))
    print("replica: %d keys (union of locale files)" % len(replica_union))
    print()
    print("in binary, not in pool     : %d" % len(only_binary))
    print("in binary, not in replica  : %d" % len(missing_in_replica))
    print("in replica, not in binary  : %d" % len(invented))
    print()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
