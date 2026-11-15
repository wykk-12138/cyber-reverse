import io

# 1) SurfaceInjectionTests: the composition string changed once more
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceInjectionTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''        Assert.Contains("var surfaceBody = MobileSurface.EngineBodyJs();", bridge);'''
new1 = '''        Assert.Contains("var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();", bridge);'''
if old1 not in t1:
    raise SystemExit("injection anchor missing")
t1 = t1.replace(old1, new1, 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) PayloadCoverageTests: same string, same reason
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayloadCoverageTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        Assert.Contains("var surfaceBody = MobileSurface.EngineBodyJs();", bridge);/*
'''
if old2 not in t2:
    old2 = '''        Assert.Contains("var surfaceBody = MobileSurface.EngineBodyJs();", bridge);'''
new2 = '''        Assert.Contains("var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();", bridge);'''
if old2 not in t2:
    raise SystemExit("coverage anchor missing")
t2 = t2.replace(old2, new2, 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)

print("two composition assertions follow R160")
