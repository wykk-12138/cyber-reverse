import idautils
import re

# anchored: a leading slash, at least one more segment, and the literal must contain the word we are
# hunting. Loose patterns over the whole pool produced GUID and base64 fragments, so the anchor is the
# word, not the shape.
words = ("order", "Order", "instore", "Instore", "inStore")

hits = []
for s in idautils.Strings():
    t = str(s)
    if "/" not in t:
        continue
    if not any(w in t for w in words):
        continue
    for chunk in re.findall(r"(/[A-Za-z0-9_.\-/{}?=&%]*order[A-Za-z0-9_.\-/{}?=&%]*"
                            r"|/[A-Za-z0-9_.\-/{}?=&%]*[Ii]n[Ss]tore[A-Za-z0-9_.\-/{}?=&%]*)", t):
        if len(chunk) > 6:
            hits.append((s.ea, chunk))

seen = {}
for ea, c in hits:
    seen.setdefault(c, ea)

print("count " + str(len(seen)))
for c in sorted(seen):
    print("P\t%x\t%s" % (seen[c], c))
