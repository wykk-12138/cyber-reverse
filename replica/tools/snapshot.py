import io, os, shutil, datetime

root = r"D:\projects\cyber-reverse\replica"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
dest = os.path.join(root, "tools", ".snapshots", stamp)
count = 0
for dirpath, dirnames, filenames in os.walk(os.path.join(root, "src")):
    if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
        continue
    for fn in filenames:
        if not fn.endswith(".cs"):
            continue
        src = os.path.join(dirpath, fn)
        rel = os.path.relpath(src, root)
        out = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy2(src, out)
        count += 1
print("snapshot", stamp, "->", count, "files")
