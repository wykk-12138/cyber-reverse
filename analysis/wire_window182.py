import io

# the two tests that count steps and bodies
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
t1 = t1.replace("Assert.Equal(10, SurfaceOrder.Steps.Count);", "Assert.Equal(11, SurfaceOrder.Steps.Count);", 1)
t1 = t1.replace('"key-order", "mask-pass",', '"window-names", "mask-pass",', 1)
t1 = t1.replace('''            "mask", "parity", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat",
            "mask-pass",''',
'''            "mask", "parity", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat",
            "window-names", "mask-pass",''', 1)
t1 = t1.replace('''                    surfaceBody += MaskTargets.ApplyJs();''',
'''                    surfaceBody += WindowBaseline.BodyJs();
                    surfaceBody += MaskTargets.ApplyJs();''', 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("Assert.Equal(13, names.Length);", "Assert.Equal(14, names.Length);", 1)
t2 = t2.replace('"Reseat", "MaskTargets"', '"Reseat", "WindowNames", "MaskTargets"', 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("counts updated")
