import io

# 1) SurfaceInjectionTests + NativeMaskTests + PayloadCoverageTests assert the old composition head
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceInjectionTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
t1 = t1.replace("NativeMask.BodyJs() + MobileSurface.EngineBodyJs()",
                "NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs()")
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NativeMaskTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace('Assert.Contains("NativeMask.BodyJs() + MobileSurface.EngineBodyJs()", bridge);',
                'Assert.Contains("NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs()", bridge);')
io.open(p2, "w", encoding="utf-8", newline="").write(t2)

p3 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayloadCoverageTests.cs"
t3 = io.open(p3, encoding="utf-8").read()
t3 = t3.replace('Assert.Contains("NativeMask.BodyJs() + MobileSurface.EngineBodyJs()", bridge);',
                'Assert.Contains("NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs()", bridge);')
io.open(p3, "w", encoding="utf-8", newline="").write(t3)

# 2) the stack test now sees JSC's format, which is the point
p4 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StackElisionTests.cs"
t4 = io.open(p4, encoding="utf-8").read()
t4 = t4.replace('''        Assert.Contains("getter can only be used on instances of Navigator", stack!, System.StringComparison.Ordinal);
        Assert.DoesNotContain("(native)", stack, System.StringComparison.Ordinal);''',
'''        Assert.Contains("getter can only be used on instances of Navigator", stack!, System.StringComparison.Ordinal);
        Assert.DoesNotContain("(native)", stack, System.StringComparison.Ordinal);

        // R179 changed the FORMAT: JSC renders frames as `fn@url:line:col`, not `    at fn (url)`
        Assert.DoesNotContain("    at ", stack, System.StringComparison.Ordinal);''', 1)
io.open(p4, "w", encoding="utf-8", newline="").write(t4)
print("four tests follow R179")
