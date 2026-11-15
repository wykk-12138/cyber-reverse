"""Audit which model properties are actually consumed outside their own file."""
import io
import os
import re

ROOT = r"C:\Users\wykk\AppData\Local\Cybersole\replica"
TARGETS = [
    ("BotTask", r"src\Cybersole.Core\Models\Tasks.cs"),
    ("TaskGroup", r"src\Cybersole.Core\Models\Tasks.cs"),
    ("Account", r"src\Cybersole.Core\Models\Accounts.cs"),
    ("AccountGroup", r"src\Cybersole.Core\Models\Accounts.cs"),
    ("Profile", r"src\Cybersole.Core\Models\Profiles.cs"),
    ("Proxy", r"src\Cybersole.Core\Models\Proxies.cs"),
    ("ProxyGroup", r"src\Cybersole.Core\Models\Proxies.cs"),
]

# gather all .cs text once
texts = {}
for base, _, files in os.walk(ROOT):
    if "\\bin\\" in base or "\\obj\\" in base:
        continue
    for f in files:
        if f.endswith(".cs"):
            p = os.path.join(base, f)
            texts[p] = io.open(p, encoding="utf-8", errors="ignore").read()


def class_body(src, name):
    m = re.search(r"class\s+" + name + r"\b", src)
    if not m:
        return ""
    # brace matching
    start = src.find("{", m.end())
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i]
    return ""


for cls, rel in TARGETS:
    path = os.path.join(ROOT, rel)
    src = io.open(path, encoding="utf-8").read()
    body = class_body(src, cls)
    props = re.findall(r"public\s+[\w\?<>,\s\.\[\]]+\s+(\w+)\s*\{\s*get", body)

    others = "\n".join(v for k, v in texts.items() if os.path.normcase(k) != os.path.normcase(path))

    unused = []
    for prop in props:
        if len(re.findall(r"\.\s*" + re.escape(prop) + r"\b", others)) == 0:
            unused.append(prop)

    print(f"\n=== {cls} ({len(props)} props, {len(unused)} unused) ===")
    for u in unused:
        print("  -", u)
