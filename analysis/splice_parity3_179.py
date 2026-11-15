import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

out = []
inserted = False
for line in lines:
    stripped = line.strip()

    if stripped.startswith('new Step('):
        # renumber every existing step by one, highest first is unnecessary when rewriting in order
        pass

    out.append(line)

text = "\n".join(out)

# renumber from the bottom so no number collides
for n in range(9, 1, -1):
    text = text.replace(f"new Step({n}, \"", f"new Step({n + 1}, \"", 1)

anchor = '        new Step(3, "engine", "MobileSurface.EngineBodyJs()",'
if anchor not in text:
    raise SystemExit(f"engine anchor missing after renumber\n{text[:800]}")

text = text.replace(anchor,
    '        new Step(2, "parity", "EngineParity.BodyJs()",\n'
    '            "before every other patch: the error wrappers are what a brand check\'s ELIDE hook talks to"),\n\n'
    + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(text)
print("written")
