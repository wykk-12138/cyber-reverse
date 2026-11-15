import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            "  const d = Object.getOwnPropertyDescriptor(navigator, 'plugins');\\n" +'''

new = '''            "  const d = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(navigator), 'plugins');\\n" +'''

if old not in t:
    raise SystemExit("descriptor anchor missing")
t = t.replace(old, new, 1)

old2 = '''        // a native function's own toString is [native code], and so is the override's
        Assert.Contains("[native code]", masked, System.StringComparison.Ordinal);
        Assert.DoesNotContain("no-getter", masked, System.StringComparison.Ordinal);'''

new2 = '''        // R169: plugins is native now, so its getter is the browser's own — still [native code], just not ours.
        Assert.Contains("[native code]", masked, System.StringComparison.Ordinal);
        Assert.DoesNotContain("no-getter", masked, System.StringComparison.Ordinal);'''

if old2 not in t:
    raise SystemExit("assert anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old2, new2, 1))
print("the descriptor comes from the prototype")
