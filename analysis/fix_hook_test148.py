import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceInjectionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // the call sits inside apply, so every realm gets it — including a challenge frame
        var apply = bridge.IndexOf("const apply = (W) =>", System.StringComparison.Ordinal);
        var call = bridge.IndexOf("__SURFACE_CALL__", System.StringComparison.Ordinal);
        Assert.True(call > apply, "the surface call is inside apply");'''

new = '''        // the call sits inside apply, so every realm gets it — including a challenge frame.
        // Search from the script literal: the same placeholders also appear in the Replace calls above it,
        // which is exactly the kind of first-occurrence mistake this assertion would otherwise make.
        var script = bridge.IndexOf("private const string StealthScript", System.StringComparison.Ordinal);
        Assert.True(script > 0, "the script literal is present");

        var apply = bridge.IndexOf("const apply = (W) =>", script, System.StringComparison.Ordinal);
        var call = bridge.IndexOf("__SURFACE_CALL__", script, System.StringComparison.Ordinal);
        Assert.True(apply > script && call > apply, "the surface call is inside apply");'''

if old not in t:
    raise SystemExit("hook anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion searches inside the script literal")
