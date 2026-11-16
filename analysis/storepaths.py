import idautils

hits = {}
for s in idautils.Strings():
    t = str(s)
    if "/store/v1/" not in t:
        continue
    for chunk in t.split("/store/v1/")[1:]:
        body = "/store/v1/" + chunk
        for cut in (" ", "\t", '"', chr(0)):
            k = body.find(cut)
            if k > 0:
                body = body[:k]
        if len(body) > 10:
            hits.setdefault(body, s.ea)

print("count " + str(len(hits)))
for c in sorted(hits):
    print("S\t%x\t%s" % (hits[c], c))
