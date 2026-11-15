import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = "var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();"
new = ("// R179: engine parity first among the patches — the error wrappers it installs are what the brand\n"
       "            // check's ELIDE hook talks to, and the stack format applies to everything constructed after.\n"
       "            var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();")

if old not in t:
    raise SystemExit("composition anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("parity spliced into the composition")
