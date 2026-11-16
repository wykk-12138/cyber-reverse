import io
import json
import os

raw = io.open(r"D:/projects/cyber-reverse/analysis/.ex.txt", encoding="utf-8", errors="replace").read()
i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:])
res = (d.get("result") or "") + (d.get("stdout") or "")

fam_host = {}
paths = {}
for l in res.splitlines():
    if not l.startswith("P\t"):
        continue
    _, fam, host, p = l.split("\t")
    fam_host[fam] = host
    paths.setdefault(fam, set()).add(p)

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


def present(p, fam):
    """Exact full path, or the tail after the family (a Base-prefixed constant plus a relative tail)."""
    if ('"' + p + '"') in rep_all:
        return "whole"
    tail = p[len(fam):]
    if len(tail) > 4 and ('"' + tail + '"') in rep_all:
        return "tail"
    return ""


exact = tail = missing = 0
rows = []
for fam in sorted(paths):
    for p in sorted(paths[fam]):
        how = present(p, fam)
        if how == "whole":
            exact += 1
        elif how == "tail":
            tail += 1
        else:
            missing += 1
        rows.append((fam_host.get(fam, "-"), fam, p, how or "missing"))

total = exact + tail + missing
print("paths under a family with a host: %d" % total)
print("  whole-path literal : %d" % exact)
print("  base + tail literal: %d" % tail)
print("  missing            : %d" % missing)
print("  covered            : %d  (%.1f%%)" % (exact + tail, 100.0 * (exact + tail) / total))
print("")
print("=== missing, by host ===")
cur = None
for host, fam, p, how in rows:
    if how != "missing":
        continue
    if host != cur:
        print("HOST " + host)
        cur = host
    print("  %-52s %s" % (p[:52], fam))
