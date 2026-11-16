import idautils
import re

fam_pat = re.compile(r"(/[A-Za-z][A-Za-z0-9_\-]*/v\d+/)")
host_pat = re.compile(r"//([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

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

print("families " + str(len(pairs)))
for f in sorted(pairs):
    hs = sorted(pairs[f].items(), key=lambda kv: -kv[1])
    print("H\t%s\t%s" % (f, hs[0][0]))
