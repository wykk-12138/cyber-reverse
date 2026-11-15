import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MobileNavigatorTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("'maxTouchPoints'", js);
        Assert.Contains("value: 5", js);
        Assert.Contains("'standalone'", js);'''

new = '''        // the body passes the count through a placeholder, so the literal to look for is the call's argument
        Assert.Contains("put('maxTouchPoints', " + MobileNavigator.MaxTouchPoints + ")", js);
        Assert.Contains("put('standalone', false)", js);
        Assert.Contains("put('vendor', 'Apple Computer, Inc.')", js);

        // appVersion is derived from the agent, not hard-coded
        Assert.Contains("ua.slice(8)", js);'''

if old not in t:
    raise SystemExit("assert block anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("assertions match the body's shape")
