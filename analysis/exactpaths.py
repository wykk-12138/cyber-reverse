import idautils
import re

# every path under a family prefix, so the comparison can be per-path rather than per-family-segment.
fam_pat = re.compile(r"(/[A-Za-z][A-Za-z0-9_\-]*/v\d+/[A-Za-z0-9_.\-/{}?=&%$:]*)")
host_pat = re.compile(r"//([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

rows = {}
for s in idautils.Strings():
    t = str(s)
    ms = list(fam_pat.finditer(t))
    if not ms:
        continue
    hosts = [m.group(1) for m in host_pat.finditer(t)]
    host = hosts[0] if hosts else ""
    for m in ms:
        p = m.group(1)
        seg = p.split("/")
        fam = "/" + seg[1] + "/" + seg[2] + "/"
        rows.setdefault((fam, host), set()).add(p)

print("pairs " + str(len(rows)) + " paths " + str(sum(len(v) for v in rows.values())))
for (fam, host) in sorted(rows):
    for p in sorted(rows[(fam, host)]):
        print("P\t%s\t%s\t%s" % (fam, host or "-", p))
