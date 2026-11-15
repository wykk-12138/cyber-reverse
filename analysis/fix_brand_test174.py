import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("if (!(this instanceof G.Navigator))", js);'''

new = '''        // realm-independent: `instanceof G.Navigator` is false for a child frame's navigator (measured, R174)
        Assert.Contains("tag !== '[object Navigator]'", js);
        Assert.Contains("Object.prototype.toString.call(this)", js);'''

if old not in t:
    raise SystemExit("guard assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the guard assertion follows the realm-independent check")
