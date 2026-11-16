import idautils
import re

# every absolute path-looking literal, any prefix, so the space is not narrowed by assumption
pat = re.compile(r"(/[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_.\-{}$]*)+)")

paths = set()
for s in idautils.Strings():
    t = str(s)
    if "/" not in t:
        continue
    for m in pat.finditer(t):
        p = m.group(1)
        if len(p) < 8 or p.count("/") < 2:
            continue
        paths.add(p)

print("count " + str(len(paths)))
for p in sorted(paths):
    print("PATH\t" + p)
