import io

# 1) MobileSurface.BodyJs must not declare G — the wrapper does, because both bodies share it.
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''        js += "  const G = W;\\n";
        js += "  const value = (target, name, v) => {\\n";'''
new1 = '''        // G is supplied by the caller's wrapper: both bodies share one realm reference, and declaring it
        // twice in the same function is a syntax error (R149 — the first run of the runtime test caught
        // exactly that, because the surface call is the last statement of apply and its throw was swallowed).
        js += "  const value = (target, name, v) => {\\n";'''

if old1 not in t1:
    raise SystemExit("mobile G anchor missing")
t1 = t1.replace(old1, new1, 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) the bridge's wrapper declares it
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''            surfaceDef = "const applySurface = (W) => {\\n" + body + "\\n          };";'''
new2 = '''            surfaceDef = "const applySurface = (W) => {\\n  const G = W;\\n" + body + "\\n          };";'''

if old2 not in t2:
    raise SystemExit("surface wrapper anchor missing")
t2 = t2.replace(old2, new2, 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("the wrapper supplies G once")
