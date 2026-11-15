import io

edits = [
    (r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NativeMaskTests.cs",
     'Assert.Contains("var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();", bridge);',
     'Assert.Contains("var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();", bridge);'),
    (r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayloadCoverageTests.cs",
     'Assert.Contains("var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();", bridge);',
     'Assert.Contains("var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();", bridge);'),
    (r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceInjectionTests.cs",
     'Assert.Contains("var surfaceBody = NativeMask.BodyJs() + MobileSurface.EngineBodyJs();", bridge);',
     'Assert.Contains("var surfaceBody = NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();", bridge);'),
]

for path, old, new in edits:
    t = io.open(path, encoding="utf-8").read()
    if old in t:
        io.open(path, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
        print("patched", path.rsplit("\\", 1)[-1])
    else:
        print("anchor missing in", path.rsplit("\\", 1)[-1])
