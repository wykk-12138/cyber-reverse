import io

p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
t1 = t1.replace("Assert.Equal(11, SurfaceOrder.Steps.Count);", "Assert.Equal(10, SurfaceOrder.Steps.Count);", 1)
t1 = t1.replace('"key-order", "mask-pass",', '"mask-pass",', 1)
t1 = t1.replace("""                    surfaceBody += KeyOrderTable.BodyJs();
                    surfaceBody += MaskTargets.ApplyJs();""",
                "                    surfaceBody += MaskTargets.ApplyJs();", 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsGuardTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("Assert.Equal(14, names.Length);", "Assert.Equal(13, names.Length);", 1)
t2 = t2.replace('"Reseat", "KeyOrder", "MaskTargets"', '"Reseat", "MaskTargets"', 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)

# the key-order runtime test must say what is true: the layer is built, not wired
p3 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyOrderTableTests.cs"
t3 = io.open(p3, encoding="utf-8").read()
t3 = t3.replace('''    /// <summary>Measured: the entry points are wrapped, symbols stay last, and a CSS instance answers indices.</summary>
    [Fact]
    public async Task TheEntryPointsAreWrapped()''',
'''    /// <summary>
    /// Built, not wired (R180). The layer is complete and its body is tested above; wiring it into the composition hung
    /// <c>mutation-check.py</c>, because the wrapped <c>Object.getOwnPropertyNames</c> sits underneath the replay code a
    /// mutation disables. This test records the gap rather than hiding it.
    /// </summary>
    [Fact]
    public void TheLayerIsBuiltButNotWired()
    {
        var bridge = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs"));

        Assert.Contains("// surfaceBody += KeyOrderTable.BodyJs();", bridge);
        Assert.Contains("deliberately NOT WIRED", bridge);
    }

    /// <summary>Measured on a bare page: symbols stay last, and a CSS instance owns numeric indices only.</summary>
    [Fact]
    public async Task TheEngineAlreadyPutsSymbolsLast()''', 1)
io.open(p3, "w", encoding="utf-8", newline="").write(t3)
print("three tests follow the honest state")
