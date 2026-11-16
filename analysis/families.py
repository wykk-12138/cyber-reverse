import idautils
import re

# anchor on the API shape /segment/vN/ rather than on a word, then group. The earlier lesson was that a
# loose shape over the whole pool returns GUID and base64 fragments, so this one requires a leading slash,
# one segment, then v<digits>, then another slash.
pat = re.compile(r"(/[A-Za-z][A-Za-z0-9_\-]*/v\d+/[A-Za-z0-9_.\-/{}?=&%$:]*)")

fams = {}
for s in idautils.Strings():
    t = str(s)
    if "/v" not in t:
        continue
    for m in pat.finditer(t):
        p = m.group(1)
        # family = the first two segments
        seg = p.split("/")
        fam = "/" + seg[1] + "/" + seg[2] + "/"
        fams.setdefault(fam, set()).add(p)

print("families " + str(len(fams)) + " paths " + str(sum(len(v) for v in fams.values())))
for fam in sorted(fams):
    print("FAM\t%s\t%d" % (fam, len(fams[fam])))
    for p in sorted(fams[fam]):
        print("P\t%s\t%s" % (fam, p))
