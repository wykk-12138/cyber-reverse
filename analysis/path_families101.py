import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# Path-like literals: start with /, at least two segments, no spaces.
paths = re.findall(r"/[a-zA-Z0-9][a-zA-Z0-9_\-/\.{}$:?=&%]*", text)

# Group by the first two segments.
prefix = collections.Counter()
examples = collections.defaultdict(list)

for path in paths:
    parts = [s for s in path.split("/") if s]
    if len(parts) < 2:
        continue
    key = "/" + parts[0] + "/" + parts[1]
    prefix[key] += 1
    if len(examples[key]) < 3 and path not in examples[key]:
        examples[key].append(path)

print("distinct path literals:", len(paths))
print("distinct prefixes:", len(prefix))
print()
for key, n in prefix.most_common(45):
    print("%4d  %-32s %s" % (n, key, "  ".join(e[:44] for e in examples[key])))
