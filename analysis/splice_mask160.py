import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var surfaceBody = MobileSurface.EngineBodyJs();'''

new = '''        // The mask runs first: every patch after it can register itself as native (R160).
        var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();'''

if old not in t:
    raise SystemExit("surface body anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the mask is installed before anything it masks")
