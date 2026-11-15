import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace("Assert.Equal(13, SurfaceOrder.Steps.Count);", "Assert.Equal(14, SurfaceOrder.Steps.Count);", 1)
t = t.replace('"window-names", "global-prune", "document-prune", "mask-pass",',
              '"window-names", "window-order", "global-prune", "document-prune", "mask-pass",', 1)
t = t.replace("""                    surfaceBody += WindowBaseline.BodyJs();""",
              """                    surfaceBody += WindowBaseline.BodyJs();
                    surfaceBody += WindowOrder.BodyJs();""", 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("Assert.Equal(16, names.Length);", "Assert.Equal(17, names.Length);", 1)
t2 = t2.replace('"WindowNames", "GlobalPrune"', '"WindowNames", "WindowOrder", "GlobalPrune"', 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("tests updated")
