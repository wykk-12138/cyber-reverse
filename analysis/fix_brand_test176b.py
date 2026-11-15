import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // realm-independent: `instanceof G.Navigator` is false for a child frame's navigator (measured, R174)
        Assert.Contains("tag !== '[object Navigator]'", js);
        Assert.Contains("Object.prototype.toString.call(this)", js);'''

new = '''        // realm-independent, and captured from the TARGET rather than hard-coded (R176): `instanceof` is realm-scoped,
        // so `this instanceof Navigator` is false for a perfectly good navigator inside an iframe
        Assert.Contains("Object.prototype.toString.call(this) !== brand", js);
        Assert.Contains("brand = Object.prototype.toString.call(target)", js);'''

if old not in t:
    raise SystemExit("brand assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion follows the captured brand")
