import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorPlacementTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.language, navigator.languages.length,\\n" +
            "  navigator.languages.join('|'), Object.isFrozen(navigator.languages),\\n" +
            "  navigator.platform, navigator.vendor, navigator.productSub])");'''

new = '''        // one expression, no embedded newlines: a `\\n` inside a C# string becomes a real newline in the
        // JavaScript, and a newline inside a quoted literal is a SyntaxError — the same escaping trap R157 hit.
        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.language, navigator.languages.length, " +
            "navigator.languages.join('|'), Object.isFrozen(navigator.languages), " +
            "navigator.platform, navigator.vendor, navigator.productSub])");'''

if old not in t:
    raise SystemExit("probe anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the probe is one line")
