import io
import json
import os

raw = io.open(r"D:/projects/cyber-reverse/analysis/.fh2.txt", encoding="utf-8", errors="replace").read()
i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:])
res = (d.get("result") or "") + (d.get("stdout") or "")

fam_host = {}
for l in res.splitlines():
    if not l.startswith("H\t"):
        continue
    _, fam, tail = l.split("\t")
    fam_host[fam] = tail.split("(")[0].split(",")[0]

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

rows = []
for fam, host in sorted(fam_host.items(), key=lambda kv: (kv[1], kv[0])):
    seg = fam.strip("/")
    # present if the family segment appears at all -- either as "bff/v2" inside a Base+tail, or as /bff/v2/
    present = (seg in rep_all) or ("/" + seg + "/" in rep_all)
    rows.append((host, fam, "yes" if present else "no"))

yes = sum(1 for _h, _f, p in rows if p == "yes")
print("families with a host: %d" % len(rows))
print("present in the replica: %d" % yes)
print("absent: %d" % (len(rows) - yes))
print("")
cur = None
for host, fam, p in rows:
    if host != cur:
        print("HOST " + host)
        cur = host
    print("  %-34s %s" % (fam, p))
