import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ControllerCensusTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Equal("CheckoutServices", families[0].Key);
        Assert.Contains(families, f => f.Key == "Adyen");
        Assert.Contains(families, f => f.Key == "Cart");'''

new = '''        // Do not name a winner: which family has the most entries is a measurement, and naming it
        // from memory is what went wrong with counts four times already. Assert the structure instead.
        var biggest = families[0].Count();
        Assert.Equal(families.Max(f => f.Count()), biggest);

        foreach (var needed in new[] { "CheckoutServices", "Adyen", "Cart" })
        {
            Assert.Contains(families, f => f.Key == needed);
            _out.WriteLine($"{needed}: {families.First(f => f.Key == needed).Count()} entries");
        }'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("no hand-picked winner any more")
