import idautils
import re

# Full paths, captured from the start of the path rather than from the /segment/vN/ landmark. The R893-R896
# family scan matched at the landmark, which silently dropped any prefix in front of it -- /api was the one
# R899 found. This one keeps the whole thing.
full = re.compile(r"(/[A-Za-z][A-Za-z0-9_.\-]*(?:/[A-Za-z0-9_.\-{}?=&%$:]+)+)")
host = re.compile(r"//([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

# only paths that live under a family, so the comparison stays the same population as R895's
famly = re.compile(r"/[A-Za-z][A-Za-z0-9_\-]*/v\d+/")

rows = {}
for s in idautils.Strings():
    t = str(s)
    if not famly.search(t):
        continue
    hosts = [m.group(1) for m in host.finditer(t)]
    h = hosts[0] if hosts else "-"
    for m in full.finditer(t):
        p = m.group(1)
        if not famly.search(p):
            continue
        rows.setdefault(h, set()).add(p)

print("hosts " + str(len(rows)) + " paths " + str(sum(len(v) for v in rows.values())))
for h in sorted(rows):
    for p in sorted(rows[h]):
        print("F\t%s\t%s" % (h, p))
