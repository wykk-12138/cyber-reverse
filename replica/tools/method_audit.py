"""Report public methods that nothing outside their own file calls."""
import io
import os
import re

ROOT = r"C:\Users\wykk\AppData\Local\Cybersole\replica"

files = {}
for base, _, names in os.walk(ROOT):
    if "\\bin\\" in base or "\\obj\\" in base:
        continue
    for n in names:
        if n.endswith(".cs"):
            p = os.path.join(base, n)
            files[p] = io.open(p, encoding="utf-8", errors="ignore").read()

# only look at production code
prod = {p: t for p, t in files.items() if os.path.normcase(p).startswith(os.path.normcase(os.path.join(ROOT, "src")))}
alltext = "\n".join(files.values())

# public methods (skip overrides / interface impls are still useful to see, mark them)
pattern = re.compile(
    r"public\s+(?:static\s+|async\s+|sealed\s+|virtual\s+|override\s+)*"
    r"(?:[\w\?<>,\s\.\[\]\(\)]+?)\s+(\w+)\s*\(([^)]*)\)",
    re.MULTILINE,
)

report = []
for path, text in prod.items():
    for m in pattern.finditer(text):
        name = m.group(1)
        if name in ("if", "for", "while", "switch", "return", "new", "get", "set", "catch"):
            continue
        if name in ("Dispose", "GetHashCode", "ToString", "Equals", "GetEnumerator"):
            continue
        # count calls elsewhere (rough, ignores overload resolution)
        others = "\n".join(t for p2, t in files.items() if os.path.normcase(p2) != os.path.normcase(path))
        hits = len(re.findall(r"\b" + re.escape(name) + r"\s*(?:<[^>]*>)?\s*\(", others))
        if hits == 0:
            report.append((os.path.basename(path), name))

report.sort()
print(f"public methods with no external call site: {len(report)}")
for f, name in report:
    print(f"  {f}: {name}()")
