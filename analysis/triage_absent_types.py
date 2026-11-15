"""Classify the 51 ABSENT types as RENAMED (with the mapping) or UNIMPLEMENTED (R512).

Why this is not a hand-written table: `bind_diff --type-presence` compares **names**, and AGENTS.md §0 explicitly
allows renaming types. So every ABSENT entry has to be resolved against what the replica actually calls that thing,
or the 51 is meaningless as a gap count. The matching signal is the member set: for each absent type, find the
replica class whose public members overlap most, and report the Jaccard ratio. A ratio at or above the threshold is
a rename candidate (still needs a human yes); below it, the type is genuinely unimplemented.

Output is TSV so the same classification can be re-run and diffed.
"""

import difflib
import io
import json
import os
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
REPLICA = os.path.join(ROOT, "replica")
DESCRIPTORS = os.path.join(ROOT, "analysis", "binding_descriptors.tsv")
OUT = os.path.join(ROOT, "analysis", "type_presence_triage.tsv")

THRESHOLD = 0.5


def load_descriptors():
    by_type = {}
    for line in io.open(DESCRIPTORS, encoding="utf-8").read().splitlines()[1:]:
        if not line.strip():
            continue
        decl, asm, member, acc = line.split("\t")
        by_type.setdefault(decl, set()).add(member)
    return by_type


def scan_replica():
    """class name -> set of public member names, for every .cs under src/."""
    classes = {}
    for dirpath, dirnames, filenames in os.walk(os.path.join(REPLICA, "src")):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".cs"):
                continue
            text = io.open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"\bclass\s+(\w+)\b[^{]*\{", text):
                name = m.group(1)
                depth, start = 0, m.end() - 1
                body = ""
                for i in range(start, len(text)):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            body = text[start:i]
                            break
                members = set(re.findall(
                    r"\bpublic\s+(?:static\s+|readonly\s+|async\s+|override\s+|virtual\s+)*"
                    r"(?:[\w<>,\[\]\?\s\.]+?)\s+(\w+)\s*(?:\{|=>|\()", body))
                if members:
                    classes.setdefault(name, set()).update(members)
    return classes


def main():
    absent = []
    out = subprocess.run([sys.executable, os.path.join(REPLICA, "tools", "bind_diff.py"), "--type-presence"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPLICA).stdout
    for line in out.splitlines():
        m = re.match(r"\s+ABSENT\s+(\S+)\s+\(members: (.*)\)$", line)
        if m:
            absent.append((m.group(1), {x.strip() for x in m.group(2).split(",") if x.strip()}))

    classes = scan_replica()
    rows = []
    for full, members in absent:
        short = full.split(".")[-1]
        if short.endswith("`2"):
            short = short[:-2]
        best, best_ratio, best_hit, best_total = "", 0.0, 0, len(members)
        for cname, cmembers in classes.items():
            hit = len(members & cmembers)
            union = len(members | cmembers)
            ratio = hit / union if union else 0.0
            if ratio > best_ratio:
                best, best_ratio, best_hit, best_total = cname, ratio, hit, len(members)
        # A single shared member is not evidence of a rename: Jaccard is then 1/(1+1)=0.50 by construction,
        # which is why bare 0.50 matches came out as nonsense (`Size` -> `EditValue`, `Operator` -> `TimeSpanOption`).
        # Require at least two shared members as well as the ratio.
        #
        # Member overlap alone still lets a wrong class win: `AccountStoreType` matched `Drop` at 0.67 because both
        # have Stores/Type — but Drop also carries Time and models a release, not a store kind. So the names must
        # also resemble each other (difflib on the short names).
        name_ratio = difflib.SequenceMatcher(None, short.lower(), best.lower()).ratio()
        verdict = ("RENAMED"
                   if (best_ratio >= THRESHOLD and best_hit >= 2 and name_ratio >= 0.35)
                   else "UNIMPLEMENTED")
        rows.append((full, len(members), best, best_hit, "%.2f" % best_ratio, verdict))

    rows.sort(key=lambda r: (r[5], -float(r[4])))
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("absent_type\tmembers\tbest_replica_class\tmembers_hit\tjaccard\tverdict\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    renamed = [r for r in rows if r[5] == "RENAMED"]
    unimplemented = [r for r in rows if r[5] == "UNIMPLEMENTED"]
    print("wrote %s" % OUT)
    print("  RENAMED       %d" % len(renamed))
    print("  UNIMPLEMENTED %d" % len(unimplemented))
    print()
    for r in renamed:
        print("  RENAMED  %-56s -> %-26s %s" % (r[0], r[2], r[4]))


if __name__ == "__main__":
    main()
