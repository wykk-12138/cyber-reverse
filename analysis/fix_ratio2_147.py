import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MobileSurfaceTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // the original's comment quotes 1.2437 and 1.2065; these are the same ratios rounded to four
        // places, so the test compares at the precision the comment used
        Assert.Equal("1.2437", before.ToString("0.0000", System.Globalization.CultureInfo.InvariantCulture));
        Assert.Equal("1.2065", after.ToString("0.0000", System.Globalization.CultureInfo.InvariantCulture));'''

new = '''        // The comment quotes 1.2437 and 1.2065. 485/402 really is 1.2065, but 500/402 is 1.24378…,
        // which rounds to 1.2438 — so the original truncated there rather than rounded. Comparing at
        // three places keeps the test about the tell (the ratio moves) and not about the author's
        // rounding habit.
        Assert.Equal("1.244", before.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
        Assert.Equal("1.206", after.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
        Assert.True(before > after, "the ratio must fall when a scrollbar takes layout width");'''

if old not in t:
    raise SystemExit("ratio anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the rounding discrepancy is recorded instead of asserted")
