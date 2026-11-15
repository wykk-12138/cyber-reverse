import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DemandwareDualPathTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var nulls = source.Split('\\n').Count(l => l.TrimStart().StartsWith("return null;", StringComparison.Ordinal));
        _out.WriteLine($"{nulls} `return null` exits in the helper");

        Assert.True(nulls >= 3, "every SCAPI failure path must return null");'''

new = '''        // most exits are inline guards (`if (x is null || !x.IsSuccess) return null;`), so count
        // occurrences of the statement rather than lines that begin with it
        var nulls = source.Split("return null;", StringSplitOptions.None).Length - 1;
        _out.WriteLine($"{nulls} `return null` exits in the helper");

        Assert.True(nulls >= 3, "every SCAPI failure path must return null");'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("count fixed")
