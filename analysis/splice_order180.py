import io

# 1) composition: after the reseat, before the mask pass
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = "surfaceBody += MaskTargets.ApplyJs();"
new1 = ("// R180: the key-order layer wraps Object/Reflect, so it runs after every install and every reorder of\n"
        "                // the objects it walks.\n"
        "                surfaceBody += KeyOrderTable.BodyJs();\n\n"
        "                surfaceBody += MaskTargets.ApplyJs();")

if old1 not in t1:
    raise SystemExit("composition anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# 2) the order contract: eleven steps
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        new Step(10, "mask-pass", "MaskTargets.ApplyJs()",'''
new2 = '''        new Step(10, "key-order", "KeyOrderTable.BodyJs()",
            "after every install and reorder: it wraps Object and Reflect, so its rules must see final key sets"),

        new Step(11, "mask-pass", "MaskTargets.ApplyJs()",'''

if old2 not in t2:
    raise SystemExit("order anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))

# 3) the guard covers it
p3 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t3 = io.open(p3, encoding="utf-8").read()
old3 = '        ("MaskTargets", MaskTargets.ApplyJs()),'
new3 = '        ("KeyOrder", KeyOrderTable.BodyJs()),\n        ("MaskTargets", MaskTargets.ApplyJs()),'
if old3 not in t3:
    raise SystemExit("guard anchor missing")
io.open(p3, "w", encoding="utf-8", newline="").write(t3.replace(old3, new3, 1))
print("spliced, ordered, guarded")
