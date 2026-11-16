import io
import re

t = io.open(r"D:/projects/cyber-reverse/replica/docs/VERDICT.md", encoding="utf-8", errors="replace").read()
rx = r"(\d+)\s*(?:个模块|modules)"
FENCE = chr(96) * 3


def n(s):
    return sum(1 for m in re.finditer(rx, s) if int(m.group(1)) >= 20)


stripped = re.sub(FENCE + r".*?" + FENCE, "\n", t, flags=re.S)
print("raw                 : %d" % n(t))
print("fence-strip (re.S)  : %d" % n(stripped))

fence_lines = sum(1 for l in t.splitlines() if l.strip().startswith(FENCE))
print("fence lines         : %d" % fence_lines)
print("")

# Which matches disappear when the fence is stripped? Those are the 3.
seen = []
pos = 0
for m in re.finditer(rx, t):
    if int(m.group(1)) < 20:
        continue
    seen.append(m.start())

kept = []
for m in re.finditer(rx, stripped):
    if int(m.group(1)) < 20:
        continue
    kept.append(m.group(1))

print("raw matches: %d, stripped matches: %d" % (len(seen), len(kept)))
