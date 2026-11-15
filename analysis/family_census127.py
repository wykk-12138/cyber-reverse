import io, re, collections

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# Endpoint-family census: how many distinct paths sit under each first path segment on a known host.
HOSTS = [
    "apihub.scheels.com", "mobile-api.scheels.com", "checkout.johnlewis.com",
    "api2.endclothing.com", "api.nike.com", "www.popmart.com", "popmart.com",
]

def census(host):
    pat = re.compile(re.escape(host) + r"(/[A-Za-z0-9_\-./{}$:?=&%]*)")
    paths = set()
    for m in pat.finditer(text):
        path = m.group(1)
        if len(path) > 2:
            paths.add(path)
    return paths

for host in HOSTS:
    paths = census(host)
    if not paths:
        print("== %s: no paths" % host)
        continue
    fam = collections.Counter()
    for path in paths:
        segs = [s for s in path.split("/") if s]
        key = "/".join(segs[:2]) if len(segs) >= 2 else (segs[0] if segs else "-")
        fam[key] += 1
    print("== %s  (%d distinct paths)" % (host, len(paths)))
    for key, n in sorted(fam.items(), key=lambda kv: (-kv[1], kv[0]))[:12]:
        print("   %-44s %d" % (key[:44], n))
    print()
