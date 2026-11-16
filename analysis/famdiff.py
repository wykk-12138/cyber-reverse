import io
import json
import os
import re

raw = io.open(r"D:/projects/cyber-reverse/analysis/.fam.txt", encoding="utf-8", errors="replace").read()
i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:])
res = (d.get("result") or "") + (d.get("stdout") or "")

img_fams = {}
for l in res.splitlines():
    if l.startswith("P\t"):
        _, fam, path = l.split("\t")
        img_fams.setdefault(fam, set()).add(path)

# every literal the replica strings together anywhere under src
rep_text = []
for dp, _dirs, fs in os.walk(r"D:/projects/cyber-reverse/replica/src"):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if not fn.endswith(".cs"):
            continue
        try:
            rep_text.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
        except OSError:
            pass
rep_all = "\n".join(rep_text)

covered, absent = [], []
for fam in sorted(img_fams):
    paths = img_fams[fam]
    hit = sum(1 for p in paths if ('"' + p + '"') in rep_all or p in rep_all)
    (covered if hit else absent).append((fam, hit, len(paths)))

print("image families: %d" % len(img_fams))
print("families the replica touches: %d" % len(covered))
print("families the replica has nothing from: %d" % len(absent))
print("")
print("=== absent families ===")
for fam, _h, n in absent:
    print("  %-34s %d paths" % (fam, n))
print("")
print("=== partially covered ===")
for fam, h, n in covered:
    if h < n:
        print("  %-34s %d/%d" % (fam, h, n))
