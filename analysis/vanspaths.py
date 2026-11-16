import idautils
import re

# exact paths under the three families Vans uses, plus the host each literal carries. The host filter is
# what makes these Vans's rather than another store's -- cart/v1 and products/v2 are generic names.
fam_pat = re.compile(r"(/(?:cart|products)/v\d+/[A-Za-z0-9_.\-/{}?=&%$:]*)")
host_pat = re.compile(r"//([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

rows = {}
for s in idautils.Strings():
    t = str(s)
    ms = list(fam_pat.finditer(t))
    if not ms:
        continue
    hosts = [m.group(1) for m in host_pat.finditer(t)]
    host = hosts[0] if hosts else "-"
    for m in ms:
        rows.setdefault(host, set()).add(m.group(1))

for host in sorted(rows):
    print("HOST\t" + host)
    for p in sorted(rows[host]):
        print("P\t%s\t%s" % (host, p))
