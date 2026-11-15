import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = "        surfaceBody += GlobalPrune.GlobalBodyJs();"
new = ("        // R186: the narrow window-only key-order wrapper, after the function it calls and before the prune that\n"
       "        // would otherwise delete it.\n"
       "        surfaceBody += WindowOrderWrap.BodyJs();\n\n"
       "        surfaceBody += GlobalPrune.GlobalBodyJs();")

if old not in t:
    raise SystemExit("prune anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("wrapper spliced")
