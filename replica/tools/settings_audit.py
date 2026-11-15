"""Report which GlobalSettings properties are actually consumed anywhere else."""
import io
import os
import re

ROOT = r"C:\Users\wykk\AppData\Local\Cybersole\replica"
SETTINGS = os.path.join(ROOT, "src", "Cybersole.Core", "Settings", "GlobalSettings.cs")

src = io.open(SETTINGS, encoding="utf-8").read()
props = re.findall(r"public\s+[\w\?<>,\s\.\[\]]+\s+(\w+)\s*\{\s*get", src)

# collect all .cs text outside GlobalSettings.cs
texts = []
for base, _, files in os.walk(ROOT):
    if "\\bin\\" in base or "\\obj\\" in base:
        continue
    for f in files:
        if f.endswith(".cs"):
            p = os.path.join(base, f)
            if os.path.normcase(p) == os.path.normcase(SETTINGS):
                continue
            texts.append(io.open(p, encoding="utf-8", errors="ignore").read())

blob = "\n".join(texts)

unused = []
for prop in props:
    # usage as Settings.Xxx or .Xxx(
    hits = len(re.findall(r"[\.\s]" + re.escape(prop) + r"\b", blob))
    if hits == 0:
        unused.append(prop)

print(f"total properties: {len(props)}")
print(f"never referenced outside GlobalSettings.cs ({len(unused)}):")
for u in sorted(unused):
    print("  -", u)
