import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        ("Mask", NativeMask.BodyJs()),'''
new = '''        ("Mask", NativeMask.BodyJs()),
        ("Parity", EngineParity.BodyJs()),'''

if old not in t:
    raise SystemExit("bodies anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the guard covers the parity layer")
