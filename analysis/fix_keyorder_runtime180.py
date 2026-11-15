import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyOrderTableTests.cs"
t = io.open(p, encoding="utf-8").read()

# with the layer unwired, the entry points are the engine's own: assert what the ENGINE does, not what we install
t = t.replace('''        // the wrappers look native
        var sources = await bridge.EvaluateAsync(
            "JSON.stringify([Function.prototype.toString.call(Object.getOwnPropertyNames)," +
            "Function.prototype.toString.call(Reflect.ownKeys)].map((s) => s.split('\\\\n').length))");
        _out.WriteLine("sources = " + sources);
        Assert.Equal("[3,3]", sources);''',
'''        // unwired, the entry points are the engine's own — recorded so the baseline is not guessed at later
        var sources = await bridge.EvaluateAsync(
            "JSON.stringify([Function.prototype.toString.call(Object.getOwnPropertyNames)," +
            "Function.prototype.toString.call(Reflect.ownKeys)].map((s) => s.split('\\\\n').length))");
        _out.WriteLine("sources = " + sources);
        Assert.Equal("[1,1]", sources);''', 1)

t = t.replace('''        _out.WriteLine("css non-numeric:total = " + css);

        // Measured: no non-numeric name survives — the instance owns nothing but numeric indices, exactly as the
        // capture says a WebKit declaration does. The total is reported rather than asserted, because it depends on how
        // many inline properties the probe set.
        Assert.StartsWith("0:", css, System.StringComparison.Ordinal);''',
'''        _out.WriteLine("css non-numeric:total = " + css);

        // Unwired, this is BLINK's answer: the instance carries camelCase names, which is exactly the 1505-name shape the
        // capture describes. Recorded here so the gap is a number.
        var nonNumeric = int.Parse(css!.Split(':')[0]);
        Assert.True(nonNumeric > 0, "Blink's declaration instance carries non-numeric own properties");''', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the runtime test records Blink's baseline")
