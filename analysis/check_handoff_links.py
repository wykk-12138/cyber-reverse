"""Verify every document and section the handoff routes point at actually exists. (R701)

A reading guide whose pointers are broken is worse than no guide: the reader trusts it and finds nothing. This checks
paths and BLOCKERS section numbers, and reports anything missing.
"""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF_BLOCKERS.md")
PROMPT = os.path.join(ROOT, "docs", "HANDOFF_PROMPT.md")
BLOCKERS = os.path.join(ROOT, "docs", "BLOCKERS.md")


def sections():
    text = io.open(BLOCKERS, encoding="utf-8").read()
    nums = set()
    for line in text.splitlines():
        if line.startswith("## "):
            m = re.match(r"##\s+(\d+(?:\.\d+)?)", line)
            if m:
                nums.add(m.group(1))
    return nums


def main():
    have = sections()
    print("BLOCKERS sections: %d" % len(have))

    missing_paths, missing_sections = [], []

    for doc in (HANDOFF, PROMPT):
        text = io.open(doc, encoding="utf-8").read()
        label = os.path.basename(doc)

        # every `docs/...` or `analysis/...` or `replica/...` style path mentioned
        for m in re.finditer(r"`([A-Za-z0-9_\\/.-]+\.(?:md|py|txt|json))`", text):
            rel = m.group(1).replace("\\", "/")
            cands = [os.path.join(ROOT, rel), os.path.join(ROOT, "docs", rel),
                     os.path.join(ROOT, "analysis", rel), os.path.join(ROOT, "replica", rel)]
            if not any(os.path.exists(c) for c in cands):
                missing_paths.append((label, m.group(1)))

        # section refs like §118 or §43/§44
        for m in re.finditer(r"§\s*(\d+(?:\.\d+)?)", text):
            num = m.group(1)
            if num not in have:
                missing_sections.append((label, num))

    print()
    if missing_paths:
        print("MISSING PATHS (%d):" % len(missing_paths))
        for label, p in sorted(set(missing_paths)):
            print("  %-22s %s" % (label, p))
    else:
        print("all referenced files exist")

    print()
    uniq_secs = sorted(set(missing_sections), key=lambda x: x[1])
    if uniq_secs:
        print("MISSING SECTION NUMBERS (%d):" % len(uniq_secs))
        for label, n in uniq_secs:
            print("  %-22s §%s" % (label, n))
    else:
        print("all referenced BLOCKERS sections exist")

    return 0 if not missing_paths and not missing_sections else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
