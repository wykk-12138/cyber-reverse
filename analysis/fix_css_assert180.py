import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyOrderTableTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        _out.WriteLine("css non-numeric = " + css);
        Assert.Equal("0", css);'''

new = '''        _out.WriteLine("css non-numeric:total = " + css);

        // Measured: no non-numeric name survives — the instance owns nothing but numeric indices, exactly as the
        // capture says a WebKit declaration does. The total is reported rather than asserted, because it depends on how
        // many inline properties the probe set.
        Assert.StartsWith("0:", css, System.StringComparison.Ordinal);'''

if old not in t:
    raise SystemExit("css assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion checks the filter, not the count")
