import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceInjectionTests.cs"
t = io.open(p, encoding="utf-8").read()

old_start = t.find('    /// <summary>The bridge composes them rather than choosing one.</summary>')
if old_start < 0:
    raise SystemExit("compose test not found")

old = t[old_start:]

new = '''    /// <summary>The bridge composes them rather than choosing one.</summary>
    [Fact]
    public void AnAppleAgentGetsBothSurfaces()
    {
        var bridge = Source("src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs");

        // R156 changed the composition: the engine block is unconditional and the two gated bodies are
        // appended to the same buffer, so there is no empty stub to fall back to any more.
        Assert.Contains("var surfaceBody = MobileSurface.EngineBodyJs();", bridge);
        Assert.Contains("surfaceBody += WebAssemblySurface.BodyJs();", bridge);
        Assert.Contains("surfaceBody += MobileSurface.BodyJs();", bridge);

        _out.WriteLine("the engine block is always installed; the corrections only when the profile claims them");
    }
}
'''

t = t[:old_start] + new
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the composition test follows R156")
