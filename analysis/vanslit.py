import idautils

# The site-id table in the replica came from somewhere in the image. Find every literal that holds the bare
# token "vans" and print it whole, so the association is read off one string rather than inferred from
# proximity. A literal holding both the site id and a host would be the co-occurrence R898 could not find.
seen = set()
for s in idautils.Strings():
    t = str(s)
    if "vans" not in t.lower():
        continue
    if len(t) > 1200:
        # a very long literal is a table; keep the part around the hit so the output stays readable
        i = t.lower().find("vans")
        lo = max(0, i - 300)
        hi = min(len(t), i + 300)
        body = t[lo:hi]
        tag = "WRAP"
    else:
        body = t
        tag = "FULL"
    if body in seen:
        continue
    seen.add(body)
    print("L\t%x\t%d\t%s\t%s" % (s.ea, len(t), tag, body.replace("\t", " ").replace("\n", "\\n")))
