import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("{ get: getter, configurable: true, enumerable: true }", js);'''

new = '''        // R177: `enumerable !== false`, not a constant
        Assert.Contains("enumerable: !MUST_HIDE.has(name)", js);'''

if old not in t:
    raise SystemExit("descriptor anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion follows R177")
