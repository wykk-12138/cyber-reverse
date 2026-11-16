"""Rank the witness candidates by whether the texts they load carry placeholders. (R734)

R733 recorded an observation that is explicitly experience rather than a criterion: the three candidates implemented
so far all choose between locale texts containing `{0}`/`{1}`, while the three rejected ones produce property
assignments, a dialog behind opaque predicates, or a slot-held label. A text with a placeholder means the function
substitutes something into it, which implies a computation worth probing; a bare label is a constant.

This orders the reading. It does not decide anything -- R730 stands, and each candidate still gets its pseudocode read.

**Criterion, fixed before measuring**: a candidate scores the number of DISTINCT locale values containing a placeholder
among the keys it loads. Candidates scoring zero go to the back.
"""

import io
import json
import os
import re
import sys

ROOT = r"D:\projects\cyber-reverse"
LOCALES = os.path.join(ROOT, "replica", "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
KEYS = os.path.join(ROOT, "analysis", "witness_candidate_keys.txt")
LEDGER = os.path.join(ROOT, "docs", "WITNESS_LEDGER.md")
OUT = os.path.join(ROOT, "analysis", "witness_ranking.tsv")

# already adjudicated in R729/R731/R732/R733; kept in the file for reference but not re-ranked
DONE = {
    "0x1410e2b60": "implemented R729",
    "0x140594500": "implemented R731",
    "0x140579e40": "implemented R732",
    "0x14125fc80": "unprobeable R733",
    "0x140601620": "unprobeable R733",
    "0x140654480": "unprobeable R733",
}


def main():
    values = json.load(io.open(LOCALES, encoding="utf-8"))
    rows = []
    for line in io.open(KEYS, encoding="utf-8"):
        if line.startswith("#"):
            continue
        parts = line.rstrip().split("\t")
        if len(parts) < 3:
            continue
        addr, _n, keys = parts[0], parts[1], parts[2]
        key_list = [k.strip() for k in keys.split(",") if k.strip()]
        placeholders = 0
        samples = []
        for k in key_list:
            v = values.get(k)
            if isinstance(v, str) and re.search(r"\{\d\}", v):
                placeholders += 1
                if len(samples) < 2:
                    samples.append(v[:44])
        rows.append((placeholders, addr, key_list, samples))

    rows.sort(key=lambda r: (-r[0], r[1]))
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# witness candidates ranked by how many placeholder texts they load (R734)\n")
        fh.write("placeholders\taddr\tstatus\tsample\n")
        for placeholders, addr, _ks, samples in rows:
            fh.write("%d\t%s\t%s\t%s\n" % (placeholders, addr, DONE.get(addr, "pending"),
                                           samples[0] if samples else ""))

    pending = [r for r in rows if r[0] > 0 and r[1] not in DONE]
    print("candidates read from the key file : %d" % len(rows))
    print("with at least one placeholder text: %d" % sum(1 for r in rows if r[0] > 0))
    print("  of those, still unread          : %d" % len(pending))
    print()
    print("next twelve to read:")
    for placeholders, addr, keys, samples in pending[:12]:
        print("  %-12s %d placeholder(s)  %s" % (addr, placeholders, (samples[0] if samples else "")[:52]))
        print("               keys: %s" % ", ".join(keys[:4]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
