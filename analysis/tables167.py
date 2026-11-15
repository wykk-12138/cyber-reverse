import io

# 1) MaskTargets: the two new getters
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MaskTargets.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '        new Target("G.Performance.prototype", "memory"),'
new1 = (
    '        new Target("G.Performance.prototype", "memory"),\n'
    '        new Target("Object.getPrototypeOf(G.navigator)", "standalone"),\n'
    '        new Target("Object.getPrototypeOf(G.navigator)", "locks"),'
)

if old1 not in t1:
    raise SystemExit("getters anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# 2) NativeArity: the two new arities
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeArity.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '            ["toString"] = 0,'
new2 = (
    '            ["toString"] = 0,\n\n'
    '            // LockManager.request(name, callback) and LockManager.query()\n'
    '            ["request"] = 2,\n'
    '            ["query"] = 0,'
)

if old2 not in t2:
    raise SystemExit("arity anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))

print("both tables extended")
