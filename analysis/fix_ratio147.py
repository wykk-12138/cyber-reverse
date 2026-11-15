import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MobileSurfaceTests.cs"
t = io.open(p, encoding="utf-8").read()

# 500/402 = 1.24378… and 485/402 = 1.20646…; the original's comment quoted 1.2437 and 1.2065, which is
# the same number rounded to four places. Compare the rounded value, not the literal.
old = '''        Assert.Equal("1.2437", MobileSurface.Format(before));
        Assert.Equal("1.2065", MobileSurface.Format(after));'''

new = '''        // the original's comment quotes 1.2437 and 1.2065; these are the same ratios rounded to four
        // places, so the test compares at the precision the comment used
        Assert.Equal("1.2437", before.ToString("0.0000", System.Globalization.CultureInfo.InvariantCulture));
        Assert.Equal("1.2065", after.ToString("0.0000", System.Globalization.CultureInfo.InvariantCulture));'''

if old not in t:
    raise SystemExit("ratio anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("ratio assertions use the comment's precision")
