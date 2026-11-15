import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace("Assert.Equal(11, SurfaceOrder.Steps.Count);", "Assert.Equal(13, SurfaceOrder.Steps.Count);", 1)
t = t.replace('"window-names", "mask-pass",',
              '"window-names", "global-prune", "document-prune", "mask-pass",', 1)

old = """                    surfaceBody += WindowBaseline.BodyJs();"""
new = ("""                    surfaceBody += WindowBaseline.BodyJs();
                    surfaceBody += GlobalPrune.GlobalBodyJs();
                    surfaceBody += GlobalPrune.DocumentBodyJs();""")
t = t.replace(old, new, 1)

# the bridge must now really contain the two markers, which it does; the hand-written sample needs them too
io.open(p, "w", encoding="utf-8", newline="").write(t)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("Assert.Equal(14, names.Length);", "Assert.Equal(16, names.Length);", 1)
t2 = t2.replace('"Reseat", "WindowNames", "MaskTargets"',
                '"Reseat", "WindowNames", "GlobalPrune", "DocumentPrune", "MaskTargets"', 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("tests updated")
