import io, re, os

res = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\avalonia_resources.txt",
              encoding="utf-8", errors="replace").read()

# ClassToResourcePathIndex: <a:Key>Cybersole.Ui.Views.X</a:Key><a:Value>/Views/X.axaml</a:Value>
pairs = re.findall(r"<a:Key>(Cybersole\.Ui\.[^<]+)</a:Key><a:Value>([^<]+)</a:Value>", res)
views = [(k.rsplit(".", 1)[-1], v) for k, v in pairs]
print("original view classes:", len(views))

root = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src"
replica = set()
for base, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in {"bin", "obj"}]
    for name in files:
        if not name.endswith(".cs"):
            continue
        text = io.open(os.path.join(base, name), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"public\s+(?:sealed\s+|abstract\s+|static\s+)?class\s+(\w+)", text):
            replica.add(m.group(1))

print("replica classes:", len(replica))

missing = [(n, p) for n, p in views if n not in replica]
present = [(n, p) for n, p in views if n in replica]

print("\nMATCHED %d / %d" % (len(present), len(views)))
print("\nMISSING from the replica (%d):" % len(missing))
for n, p in missing:
    print("  %-38s %s" % (n, p))
