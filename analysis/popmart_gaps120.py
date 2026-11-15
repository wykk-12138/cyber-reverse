import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# Named steps in the 100-159 ordinal range — where Pop Mart lives.
hits = collections.OrderedDict()
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    for name, ordinal in re.findall(r"<([A-Za-z][A-Za-z0-9_]*)>d__(1[0-5]\d)", body):
        hits.setdefault(int(ordinal), set()).add(name)

print("ordinals found in 100..159:", len(hits))
for ordinal in sorted(hits):
    print("%4d  %s" % (ordinal, ", ".join(sorted(hits[ordinal]))))
