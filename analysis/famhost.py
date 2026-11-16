import idautils
import re

fam_pat = re.compile(r"(/[A-Za-z][A-Za-z0-9_\-]*/v\d+/)")
host_pat = re.compile(r"//([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

# For each string that names a family, collect the hosts appearing in the SAME string. A literal like
# //checkout.johnlewis.com/bff/v2/orders carries both, so co-occurrence inside one literal is a stronger
# signal than proximity in the pool.
pairs = {}
for s in idautils.Strings():
    t = str(s)
    fams = set(m.group(1) for m in fam_pat.finditer(t))
    if not fams:
        continue
    hosts = set(m.group(1) for m in host_pat.finditer(t))
    if not hosts:
        continue
    for f in fams:
        for h in hosts:
            pairs.setdefault(f, {}).setdefault(h, 0)
            pairs[f][h] += 1

print("families with a co-located host " + str(len(pairs)))
for f in sorted(pairs):
    hs = sorted(pairs[f].items(), key=lambda kv: -kv[1])
    top = ",".join("%s(%d)" % (h, n) for h, n in hs[:3])
    print("H\t%s\t%s" % (f, top))
