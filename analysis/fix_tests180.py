import io

# 1) JsGuardTests: thirteen -> fourteen bodies
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
t1 = t1.replace("Assert.Equal(13, names.Length);", "Assert.Equal(14, names.Length);", 1)
t1 = t1.replace('"Reseat", "MaskTargets", "WebAssembly wrapper"', '"Reseat", "KeyOrder", "MaskTargets", "WebAssembly wrapper"', 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) SurfaceOrderTests: eleven steps, and the wrong-order sample gains the key-order marker
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("Assert.Equal(10, SurfaceOrder.Steps.Count);", "Assert.Equal(11, SurfaceOrder.Steps.Count);", 1)
t2 = t2.replace('''            "mask", "parity", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat",
            "mask-pass",''',
'''            "mask", "parity", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat",
            "key-order", "mask-pass",''', 1)
t2 = t2.replace('''                    surfaceBody += MaskTargets.ApplyJs();''',
'''                    surfaceBody += KeyOrderTable.BodyJs();
                    surfaceBody += MaskTargets.ApplyJs();''', 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("two tests follow R180")
