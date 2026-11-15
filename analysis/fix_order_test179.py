import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

# 1) ten steps now
t = t.replace('Assert.Equal(9, SurfaceOrder.Steps.Count);', 'Assert.Equal(10, SurfaceOrder.Steps.Count);', 1)
t = t.replace('''            "mask", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat", "mask-pass",''',
              '''            "mask", "parity", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat",
            "mask-pass",''', 1)

# 2) the deliberately-wrong sample carries the parity marker too
t = t.replace('''                    var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();''',
              '''                    var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs()
                        + MobileSurface.EngineBodyJs();''', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the order test knows ten steps")
