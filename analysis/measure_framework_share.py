"""Measure what the framework version contributes, directly.

R1064 said the ratio cannot be read as completeness because the artifacts inline different class libraries. R1065 built a
minimal .NET 8 AOT application and got 7,930 functions, which is thirteen times too small to explain a 102,827 gap, so
the framework explanation was retired rather than confirmed.

That left the framework's share undetermined. It can be measured rather than argued: the same source file, published
twice, once per target framework. The difference between the two counts is what the framework version contributes for
exactly the same application.

Reads .pdata from both artifacts and divides by twelve, the size of a RUNTIME_FUNCTION on x64.
"""

import os
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
TRIAGE = r"D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_triage.py"
PY = r"D:\projects\IDA-pro\python311\python.exe"

ARTIFACTS = [
    ("baseline net8.0", os.path.join(ROOT, "analysis", "baseline-aot", "out", "Baseline.exe")),
    ("baseline net10.0", os.path.join(ROOT, "analysis", "baseline-aot10", "out", "Baseline10.exe")),
    ("replica", os.path.join(ROOT, "replica", ".publish-aot", "Cybersole.Ui.exe")),
    ("original", os.path.join(ROOT, "target", "Cybersole.exe")),
]

PDATA = re.compile(r"\.pdata\s+0x[0-9a-fA-F]+\s+(\d+)\s+(\d+)")
ENTRY = re.compile(r"entry point : (0x[0-9a-fA-F]+)")
SIZE = re.compile(r"size\s+:\s+(\d+) bytes")


def probe(path):
    if not os.path.exists(path):
        return None
    p = subprocess.run([PY, TRIAGE, path], capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = (p.stdout or "") + (p.stderr or "")
    m = PDATA.search(txt)
    if not m:
        return None
    return {"pdata": int(m.group(1)), "functions": int(m.group(1)) // 12,
            "file": int(SIZE.search(txt).group(1)) if SIZE.search(txt) else None}


def main():
    rows = []
    for label, path in ARTIFACTS:
        d = probe(path)
        rows.append((label, d))
        if d is None:
            print("  %-18s MISSING or unreadable: %s" % (label, path))
        else:
            print("  %-18s .pdata=%-9d functions=%-7d file=%s MB"
                  % (label, d["pdata"], d["functions"],
                     "%.1f" % (d["file"] / 1048576.0) if d["file"] else "?"))

    by = {label: d for label, d in rows if d}
    print()
    if "baseline net8.0" in by and "baseline net10.0" in by:
        eight = by["baseline net8.0"]["functions"]
        ten = by["baseline net10.0"]["functions"]
        print("  same source, two frameworks:")
        print("    net8.0  %-7d" % eight)
        print("    net10.0 %-7d" % ten)
        print("    delta   %+d  (%.1f%% of the net8.0 count)"
              % (ten - eight, 100.0 * (ten - eight) / max(eight, 1)))
        print()
        gap = by["original"]["functions"] - by["replica"]["functions"]
        print("  what that means for the 62.89%% question:")
        print("    replica-vs-original gap             %d" % gap)
        print("    framework version contribution     %+d" % (ten - eight))
        print("    gap left after removing it          %d" % (gap - (ten - eight)))
        print()
        if abs(ten - eight) < gap / 4:
            print("  → the framework version explains less than a quarter of the gap; the rest is not framework")
        else:
            print("  → the framework version is a material part of the gap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
