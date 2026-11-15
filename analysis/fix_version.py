import io, os

root = r"C:\Users\wykk\AppData\Local\Cybersole\replica"
skip_dirs = {"bin", "obj", ".git", "node_modules"}
exts = {".cs", ".md", ".ps1", ".py", ".json", ".axaml", ".csproj", ".sln"}

changed = []
total = 0
for base, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for name in files:
        if os.path.splitext(name)[1].lower() not in exts:
            continue
        p = os.path.join(base, name)
        try:
            t = io.open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if "5.18.28" not in t:
            continue
        n = t.count("5.18.28")
        t = t.replace("5.18.28", "5.18.30")
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        changed.append((os.path.relpath(p, root), n))
        total += n

for rel, n in sorted(changed, key=lambda x: -x[1]):
    print("%4d  %s" % (n, rel))
print("files=%d occurrences=%d" % (len(changed), total))
