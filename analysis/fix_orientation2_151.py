import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains(orientation!, o => o is "portrait-primary" or "landscape-primary");'''

new = '''        Assert.True(orientation!.Contains("portrait-primary", System.StringComparison.Ordinal)
                    || orientation!.Contains("landscape-primary", System.StringComparison.Ordinal),
            "orientation is one of the two native values: " + orientation);'''

if old not in t:
    raise SystemExit("orientation assert anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion is a string check")
