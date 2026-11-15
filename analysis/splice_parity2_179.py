import io, re

# 1) composition: the actual line has 16-space indentation
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = "var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();"
new1 = ("// R179: engine parity first among the patches — the error wrappers it installs are what the\n"
        "                // brand check's ELIDE hook talks to, and the stack format applies to everything built after.\n"
        "                var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();")

if old1 not in t1:
    raise SystemExit("composition anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# 2) the order contract: insert parity as step 2 and renumber the rest by one
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
t2 = io.open(p2, encoding="utf-8").read()

# renumber existing steps 2..9 -> 3..10, highest first so no number is reused
for n in range(9, 1, -1):
    t2 = t2.replace(f"new Step({n}, ", f"new Step({n + 1}, ", 1)

t2 = t2.replace('        new Step(3, "engine", "MobileSurface.EngineBodyJs()",',
                '        new Step(2, "parity", "EngineParity.BodyJs()",\n'
                '            "before every other patch: the error wrappers are what a brand check\'s ELIDE hook talks to"),\n\n'
                '        new Step(3, "engine", "MobileSurface.EngineBodyJs()",', 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("both edits applied")
