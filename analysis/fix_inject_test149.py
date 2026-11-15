import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceInjectionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("const applySurface = (W) => {};", bridge);'''

new = '''        // R149 renamed the wrapper's parameter from W to realm: WebAssemblySurface.BodyJs declares
        // `const W = G.WebAssembly`, and a `const` named like the enclosing parameter is a SyntaxError —
        // which the browser swallows, so the whole script silently did nothing.
        Assert.Contains("const applySurface = (realm) => {};", bridge);
        Assert.Contains("const applySurface = (realm) => {", bridge);
        Assert.DoesNotContain("const applySurface = (W)", bridge);'''

if old not in t:
    raise SystemExit("stub assert anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the string test follows the rename and records why")
