import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

sites = collections.Counter(re.findall(r"Sites-([A-Za-z0-9_]+)", text))
controllers = collections.Counter(re.findall(r"/([A-Z][A-Za-z]+-[A-Za-z]+)", text))

print("=== Demandware site ids (%d)" % len(sites))
for name, n in sites.most_common(30):
    print("  %-24s %d" % (name, n))

print("\n=== Demandware controllers (%d)" % len(controllers))
for name, n in controllers.most_common(40):
    print("  %-40s %d" % (name, n))
