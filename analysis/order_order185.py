import io

# 1) the order contract gains the window-order step, the guard gains its body
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''        new Step(11, "global-prune", "GlobalPrune.GlobalBodyJs()",'''
new1 = '''        new Step(11, "window-order", "WindowOrder.BodyJs()",
            "before the prunes: it takes the baseline of every name this script installed, and the prunes delete some"),

        new Step(12, "global-prune", "GlobalPrune.GlobalBodyJs()",'''

if old1 not in t1:
    raise SystemExit("order anchor missing")
t1 = t1.replace(old1, new1, 1)
t1 = t1.replace('new Step(12, "document-prune"', 'new Step(13, "document-prune"', 1)
t1 = t1.replace('new Step(13, "mask-pass"', 'new Step(14, "mask-pass"', 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t2 = io.open(p2, encoding="utf-8").read()
old2 = '        ("GlobalPrune", GlobalPrune.GlobalBodyJs()),'
new2 = '        ("WindowOrder", WindowOrder.BodyJs()),\n        ("GlobalPrune", GlobalPrune.GlobalBodyJs()),'
if old2 not in t2:
    raise SystemExit("guard anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))
print("order and guard updated")
