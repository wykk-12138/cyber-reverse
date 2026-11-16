import io
import json
import os
import re
from collections import Counter

raw = io.open(r"D:/projects/cyber-reverse/analysis/.fp.txt", encoding="utf-8", errors="replace").read()
i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:])
res = (d.get("result") or "") + (d.get("stdout") or "")

paths = []
for l in res.splitlines():
    if not l.startswith("F\t"):
        continue
    _, host, p = l.split("\t")
    # a full URL matched from the two slashes: drop the host segment so the path is comparable
    if p.split("/")[1] == host:
        p = "/" + "/".join(p.split("/")[2:])
    paths.append((host, p))

print("paths after removing the host segment: %d" % len(paths))
seg = Counter(p.split("/")[1] for _h, p in paths)
print("first path segment distribution:")
for k, v in seg.most_common(20):
    print("  /%-30s %d" % (k, v))

api = [(h, p) for h, p in paths if p.startswith("/api/")]
print("")
print("paths under /api/: %d" % len(api))
for h, p in api[:8]:
    print("  %-34s %s" % (h[:34], p[:52]))

# now the coverage question: of all these, how many appear verbatim in the replica
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

hit = sum(1 for _h, p in paths if ('"' + p + '"') in rep_all)
print("")
print("verbatim in the replica: %d of %d" % (hit, len(paths)))
