import idautils

paths = set()
for s in idautils.Strings():
    t = str(s)
    if "/shop/v1/" in t:
        # a literal can hold several paths glued together; split on the prefix
        for chunk in t.split("/shop/v1/")[1:]:
            body = "/shop/v1/" + chunk
            # paths end at whitespace or a quote or a second prefix
            for cut in (" ", "\t", '"', chr(0)):
                k = body.find(cut)
                if k > 0:
                    body = body[:k]
            if len(body) > 9:
                paths.add(body)

print("count " + str(len(paths)))
for p in sorted(paths):
    print("PATH\t" + p)
