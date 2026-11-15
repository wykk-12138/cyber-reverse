import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("{ get: guarded, configurable: true, enumerable: true }", js);
        Assert.Contains("'get ' + name", js);'''

new = '''        // R176 renamed the local: the getter is built by `install()` and installed by name
        Assert.Contains("{ get: getter, configurable: true, enumerable: true }", js);
        Assert.Contains("'get ' + name", js);'''

if old not in t:
    raise SystemExit("descriptor assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the descriptor assertion follows the rename")
