"""Static audit of mutation-check's anchors: no tests are run.

Every mutation locates its defect with a `find` string. When that string drifts — a comment gets reworded, a number in a
doc gets updated — the tool skips the mutation SILENTLY and still counts it in "24 guards". A guard that never runs is
worse than no guard, because it still appears in the report.

Run after any change to the files the mutations touch:
    <python> tools/mutation-audit.py
"""

import io, re, importlib.util, sys
spec = importlib.util.spec_from_file_location("mc", r"D:\projects\cyber-reverse\replica\tools\mutation-check.py")
mc = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mc)   # safe: main() only runs under __main__
except SystemExit:
    pass
print('mutations:', len(mc.MUTATIONS))
missing, ok = [], 0
for m in mc.MUTATIONS:
    try:
        text = io.open(m["file"], encoding="utf-8").read()
    except FileNotFoundError:
        missing.append((m["name"], "FILE MISSING"))
        continue
    if m["find"] in text:
        ok += 1
    else:
        missing.append((m["name"], "anchor not found"))
print('anchors present:', ok, '/', len(mc.MUTATIONS))
for n, why in missing:
    print('  DEAD:', n.replace('—','-'), '->', why)
