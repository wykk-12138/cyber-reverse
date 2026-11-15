import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

pairs = [
    ('var surfaceDef = "const applySurface = (W) => {};";',
     'var surfaceDef = "const applySurface = (realm) => {};";'),
    ('surfaceDef = "const applySurface = (W) => {\\n  const G = W;\\n" + body + "\\n          };";',
     'surfaceDef = "const applySurface = (realm) => {\\n  const G = realm;\\n" + body + "\\n          };";'),
]

for old, new in pairs:
    if old not in t:
        raise SystemExit("anchor missing: " + old[:50])
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("both the stub and the real wrapper use `realm`")
