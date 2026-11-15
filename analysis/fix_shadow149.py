import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# WebAssemblySurface.BodyJs declares `const W = G.WebAssembly`, so the wrapper's parameter cannot also be
# called W: `const W` inside a function whose parameter is W is a SyntaxError, and a SyntaxError in the
# injected source means the whole script silently does nothing.
old = '''            surfaceDef = "const applySurface = (W) => {\\n  const G = W;\\n" + body + "\\n          };";'''
new = '''            surfaceDef = "const applySurface = (realm) => {\\n  const G = realm;\\n" + body + "\\n          };";'''

if old not in t:
    raise SystemExit("wrapper anchor missing")
t = t.replace(old, new, 1)

old2 = '''            surfaceDef = "const applySurface = (W) => {};";'''
new2 = '''            surfaceDef = "const applySurface = (realm) => {};";'''

if old2 not in t:
    raise SystemExit("stub anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the wrapper parameter no longer shadows the body's WebAssembly binding")
