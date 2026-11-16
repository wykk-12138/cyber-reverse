import idautils
import os
import re

# Enumerate every accessor-shaped string: <DeclaringType>,<Property>!Getter|Setter|Property
pat = re.compile(r"([A-Za-z_][\w.<>`+\[\], ]*?),([A-Za-z_][\w.<>`]*?)!(Getter|Setter|Property)")

pairs = set()
types = {}
raw = 0
for s in idautils.Strings():
    t = str(s)
    if "!" not in t:
        continue
    for m in pat.finditer(t):
        raw += 1
        decl, prop, kind = m.group(1), m.group(2), m.group(3)
        # the leading length byte can be glued to the declaring type; strip any leading junk
        decl = decl.split()[0] if " " in decl else decl
        if not decl or not prop:
            continue
        pairs.add((decl, prop, kind))
        types.setdefault(decl, set()).add(prop)

print("raw matches %d distinct triples %d distinct types %d" % (raw, len(pairs), len(types)))

out = os.environ.get("OUT", r"D:/projects/cyber-reverse/analysis/accessors.txt")
with open(out, "w", encoding="utf-8") as f:
    for decl in sorted(types):
        props = sorted(types[decl])
        f.write("%s\t%d\t%s\n" % (decl, len(props), ",".join(props)))
print("wrote " + out)

# who lives under Cybersole.*
for prefix in ("Cybersole.Stores", "Cybersole.Models", "Cybersole.Core", "Cybersole.Http", "Cybersole.Services"):
    hits = sorted(d for d in types if d.startswith(prefix))
    print("%-22s %d types" % (prefix, len(hits)))
    for d in hits[:8]:
        print("    %-58s %d props" % (d[:58], len(types[d])))
