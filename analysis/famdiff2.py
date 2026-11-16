import io
import json
import os

raw = io.open(r"D:/projects/cyber-reverse/analysis/.fam.txt", encoding="utf-8", errors="replace").read()
i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:])
res = (d.get("result") or "") + (d.get("stdout") or "")

img_fams = {}
for l in res.splitlines():
    if l.startswith("P\t"):
        _, fam, path = l.split("\t")
        img_fams.setdefault(fam, set()).add(path)

rep = []
for dp, _dirs, fs in os.walk(r"D:/projects/cyber-reverse/replica/src"):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                rep.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
rep_all = "\n".join(rep)

# three grades of presence:
#   exact    -- the full path appears as a literal
#   relative -- the family's own segments appear without the leading family, which is how a class that
#               stores Base = ".../bff/" plus "v2/orders" represents the same endpoint
#   absent   -- the family name does not appear at all
exact = relative = absent = 0
rows = []
for fam in sorted(img_fams):
    paths = img_fams[fam]
    segs = fam.strip("/").split("/")
    e = sum(1 for p in paths if ('"' + p + '"') in rep_all)
    fam_seg = "/".join(segs)
    if e:
        exact += 1
        rows.append(("exact", fam, e, len(paths)))
        continue
    # relative form: look for the family name, or for a distinctive tail of one of its paths
    if fam_seg in rep_all or any(('"' + p[len(fam):] + '"') in rep_all for p in paths if len(p) > len(fam) + 4):
        relative += 1
        rows.append(("relative", fam, 0, len(paths)))
    else:
        absent += 1
        rows.append(("absent", fam, 0, len(paths)))

print("families: %d" % len(img_fams))
print("  exact    (full path as a literal): %d" % exact)
print("  relative (family stored with a Base prefix): %d" % relative)
print("  absent   (family name not in the source): %d" % absent)
print("")
print("=== absent ===")
for kind, fam, e, n in rows:
    if kind == "absent":
        print("  %-34s %d paths" % (fam, n))
print("")
print("=== relative (so my first pass was wrong about these) ===")
for kind, fam, e, n in rows:
    if kind == "relative":
        print("  %-34s %d paths" % (fam, n))
