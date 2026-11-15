import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorBrandCheckTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // a getter shorthand, not a plain function: no prototype, like a real accessor
        Assert.Contains("get x() {", js);'''

new = '''        // a getter shorthand, taken through its descriptor so reading it does not call it
        Assert.Contains("get x() {", js);
        Assert.Contains("Object.getOwnPropertyDescriptor({", js);
        Assert.Contains("}, 'x').get;", js);'''

if old not in t:
    raise SystemExit("test anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("test updated")
