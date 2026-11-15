import io, os

root = r"C:\Users\wykk\AppData\Local\Cybersole\replica"
old, new = "5.18.30", "5.18.32"

skip = {"bin", "obj", ".git"}
exts = {".cs", ".md", ".ps1", ".py", ".json", ".axaml", ".csproj", ".txt", ".props"}

changed = []
total = 0
for base, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in skip]
    for name in files:
        if os.path.splitext(name)[1].lower() not in exts:
            continue
        p = os.path.join(base, name)
        try:
            t = io.open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if old not in t:
            continue
        n = t.count(old)
        io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new))
        changed.append((os.path.relpath(p, root), n))
        total += n

for rel, n in sorted(changed, key=lambda x: -x[1])[:12]:
    print("%4d  %s" % (n, rel))
print("files=%d occurrences=%d" % (len(changed), total))
