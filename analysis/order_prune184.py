import io

# the order contract and the guard grow two steps
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''        new Step(11, "mask-pass", "MaskTargets.ApplyJs()",'''
new1 = '''        new Step(11, "global-prune", "GlobalPrune.GlobalBodyJs()",
            "after every install: it deletes what the device's list does not carry, so it must run last of the adders"),

        new Step(12, "document-prune", "GlobalPrune.DocumentBodyJs()",
            "with the global prune: hCaptcha's first request reads document.featurePolicy"),

        new Step(13, "mask-pass", "MaskTargets.ApplyJs()",'''

if old1 not in t1:
    raise SystemExit("order anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# the guard covers both bodies
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t2 = io.open(p2, encoding="utf-8").read()
old2 = '        ("WindowNames", WindowBaseline.BodyJs()),'
new2 = ('        ("WindowNames", WindowBaseline.BodyJs()),\n'
        '        ("GlobalPrune", GlobalPrune.GlobalBodyJs()),\n'
        '        ("DocumentPrune", GlobalPrune.DocumentBodyJs()),')
if old2 not in t2:
    raise SystemExit("guard anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))
print("order and guard updated")
