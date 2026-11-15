"""Measure how much of the pool `copy_audit_report.py` actually checks (R543).

Its `AREAS` list is a hand-written whitelist of nineteen prefixes. Scanning the whole pool instead of that list
gave **222** absent values, so the question is: how much of the pool does the report never look at?

This prints:

    the whitelisted areas and their key counts
    the top-level areas present in the pool but NOT whitelisted, with their key counts
    how many of those non-whitelisted keys are absent from the source

Read-only. It does not change the report; it measures its coverage.
"""

import io
import os
import re

POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
SRC = r"D:\projects\cyber-reverse\replica\src"
REPORT = r"D:\projects\cyber-reverse\replica\tools\copy_audit_report.py"

PAT = re.compile(r'"([A-Z][\w.]*\.[\w.]+)":\s*"((?:[^"\\\n]|\\.){1,400})"')


def main():
    report = io.open(REPORT, encoding="utf-8").read()
    m = re.search(r"AREAS\s*=\s*\[(.*?)\]", report, re.S)
    areas = [a.strip().strip("'\"") for a in m.group(1).replace("\n", " ").split(",") if a.strip()]

    raw = io.open(POOL, encoding="utf-8", errors="replace").read()
    pairs = sorted(set(
        (mm.group(1), mm.group(2).replace('\\"', '"').replace('\\\\', '\\'))
        for mm in PAT.finditer(raw)))
    all_keys = [k for k, _v in pairs]

    parts = []
    for dirpath, _d, files in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in files:
            if fn.endswith(".cs"):
                parts.append(io.open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read())
    haystack = "\n".join(parts)

    by_area = {}
    for key, value in pairs:
        by_area.setdefault(key.split(".")[0], []).append((key, value))

    checked = [a for a in areas if a in by_area]
    unchecked = sorted(a for a in by_area if a not in areas)

    print("whitelisted areas: %d   (present in pool: %d)" % (len(areas), len(checked)))
    print("areas in the pool the report never looks at: %d" % len(unchecked))
    print()

    def absent(a):
        return sum(1 for _k, v in by_area[a] if v not in haystack)

    in_total = sum(len(by_area[a]) for a in checked)
    in_absent = sum(absent(a) for a in checked)
    out_total = sum(len(by_area[a]) for a in unchecked)
    out_absent = sum(absent(a) for a in unchecked)

    print("  %-28s %6s %8s" % ("area", "keys", "absent"))
    for a in sorted(checked, key=lambda x: -absent(x))[:10]:
        print("  %-28s %6d %8d   (whitelisted)" % (a, len(by_area[a]), absent(a)))
    print("  …")
    for a in sorted(unchecked, key=lambda x: -absent(x))[:18]:
        print("  %-28s %6d %8d" % (a, len(by_area[a]), absent(a)))
    print()
    print("whitelisted : %4d keys, %4d absent" % (in_total, in_absent))
    print("not checked : %4d keys, %4d absent" % (out_total, out_absent))
    print("whole pool  : %4d keys, %4d absent" % (in_total + out_total, in_absent + out_absent))


if __name__ == "__main__":
    main()
