import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var surfaceDef = "const applySurface = (realm) => {\\n  const G = realm;\\n" + surfaceBody +
                         "\\n          };";'''

new = '''        // The masking pass goes last: a getter that has not been installed yet cannot be masked (R161).
        surfaceBody += MaskTargets.ApplyJs();

        var surfaceDef = "const applySurface = (realm) => {\\n  const G = realm;\\n" + surfaceBody +
                         "\\n          };";'''

if old not in t:
    raise SystemExit("surface def anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the masking pass runs last")
