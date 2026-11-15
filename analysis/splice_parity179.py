import io

# 1) splice the parity layer right after the mask, before the engine block
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''                var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();'''

new1 = '''                // R179: engine parity first among the patches — the error wrappers it installs are what the brand
                // check's ELIDE hook talks to, and the stack format applies to everything constructed afterwards.
                var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();'''

if old1 not in t1:
    raise SystemExit("composition anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# 2) the order contract grows a step
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        new Step(2, "engine", "MobileSurface.EngineBodyJs()",'''
new2 = '''        new Step(2, "parity", "EngineParity.BodyJs()",
            "before every other patch: the error wrappers are what a brand check's ELIDE hook talks to"),

        new Step(3, "engine", "MobileSurface.EngineBodyJs()",'''

if old2 not in t2:
    raise SystemExit("order anchor missing")
t2 = t2.replace(old2, new2, 1)

# renumber the rest
for old_n, new_n in [(3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)]:
    t2 = t2.replace(f'new Step({old_n}, "', f'new Step({new_n}, "', 1) if old_n != new_n else t2

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("parity is step two")
