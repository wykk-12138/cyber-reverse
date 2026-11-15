"""Count what PARITY.md section 8 claims, from the repository itself.

The table said "88 .cs files / 10,6xx lines / 137 tests / 50 modules", which was true when it was
written. Rounds 112-154 added a great deal. This prints the current numbers so the table can be
replaced with measured values rather than corrected by guesswork.
"""
import io
import os
import re

REPO = r"C:\Users\wykk\AppData\Local\Cybersole\replica"


def count(root, label):
    files = 0
    lines = 0
    blank = 0
    comment = 0
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("obj", "bin", "__pycache__")]
        for n in names:
            if not n.endswith(".cs"):
                continue
            path = os.path.join(dirpath, n)
            try:
                text = io.open(path, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            files += 1
            for line in text.split("\n"):
                lines += 1
                s = line.strip()
                if not s:
                    blank += 1
                elif s.startswith("//") or s.startswith("///") or s.startswith("*"):
                    comment += 1
    print(f"{label:24} {files:4} files  {lines:7} lines  "
          f"{lines - blank - comment:7} code  {comment:6} comment  {blank:5} blank")
    return files, lines


print("== source ==")
src_files, src_lines = count(os.path.join(REPO, "src"), "src/")
test_files, test_lines = count(os.path.join(REPO, "tests"), "tests/")
print()
print(f"{'total':24} {src_files + test_files:4} files  {src_lines + test_lines:7} lines")

print("\n== per project ==")
for project in sorted(os.listdir(os.path.join(REPO, "src"))):
    p = os.path.join(REPO, "src", project)
    if os.path.isdir(p):
        count(p, project)

print("\n== declared elsewhere ==")
# transport modes, from the enum
enum = os.path.join(REPO, "src", "Cybersole.Http", "NetClient.cs")
if os.path.exists(enum):
    text = io.open(enum, encoding="utf-8", errors="replace").read()
    m = re.search(r"enum TransportMode\s*\{([^}]*)\}", text)
    if m:
        modes = [x.strip() for x in m.group(1).split(",") if x.strip()]
        print(f"{'TransportMode':24} {len(modes)}: {', '.join(modes)}")

# modules, from the catalog
catalog = os.path.join(REPO, "src", "Cybersole.Stores", "Modules", "StoreModuleCatalog.cs")
if os.path.exists(catalog):
    text = io.open(catalog, encoding="utf-8", errors="replace").read()
    opens = len(re.findall(r"new FlowStoreModule\(", text))
    print(f"{'registered modules':24} {opens} FlowStoreModule entries")
