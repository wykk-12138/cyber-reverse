import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ChromiumStealthTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Equal(3, root.GetProperty("plugins").GetInt32());'''

new = '''        // R156: five, not three — the image's own payload sample reports navigator.plugins.count = 5, all with
        // the same internal filename, so the earlier three was the replica's number rather than the device's.
        Assert.Equal(5, root.GetProperty("plugins").GetInt32());'''

if old not in t:
    raise SystemExit("plugins assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the stealth test follows the sample's count")
