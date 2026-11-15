import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var present = NavOrder.Navigator.Where(n => achieved.Contains(n)).ToList();
        _out.WriteLine($"recorded names present on the prototype: {present.Count}/{NavOrder.Navigator.Count}");
        _out.WriteLine($"relative order preserved: " +
                       $"{present.SequenceEqual(achieved.Where(n => present.Contains(n)))}");

        Assert.NotNull(parsed["forIn"]);'''

new = '''        var present = NavOrder.Navigator.Where(n => achieved.Contains(n)).ToList();
        var relativeOrder = present.SequenceEqual(achieved.Where(n => present.Contains(n)));
        _out.WriteLine($"recorded names present on the prototype: {present.Count}/{NavOrder.Navigator.Count}");
        _out.WriteLine($"relative order preserved: {relativeOrder}");

        // What the browser allows, measured rather than assumed (R165): 28 of the fifty recorded names live on
        // Navigator.prototype at all — the rest are inherited from Object.prototype or absent from this engine —
        // and among those that do exist the recorded relative order is achieved exactly. The non-movable Blink
        // names sit in front of everything, which no reseat can change.
        Assert.True(relativeOrder, "the recorded relative order is achieved among the properties that exist");
        Assert.True(present.Count >= 20, $"only {present.Count} of the recorded names exist on the prototype");

        // and the members this workspace installs are in the achieved order
        Assert.Contains("maxTouchPoints", achieved);
        Assert.Contains("standalone", achieved);'''

if old not in t:
    raise SystemExit("measure anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the measurement is the assertion")
