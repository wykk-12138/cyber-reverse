import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorPlacementTests.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

# lines 93..95 (1-based) are the broken three-line expression; replace with one clean line
start = None
for i, line in enumerate(lines):
    if "var probe = await bridge.EvaluateAsync(" in line:
        start = i
        break

if start is None:
    raise SystemExit("probe start not found")

end = start
while ");" not in lines[end]:
    end += 1

replacement = [
    '        // One expression, no embedded newlines: a `\\n` inside a C# string becomes a real newline in the',
    '        // JavaScript, and a newline inside a quoted literal is a SyntaxError — R157\\'s escaping trap again.',
    '        var probe = await bridge.EvaluateAsync(',
    '            "JSON.stringify([navigator.language, navigator.languages.length, " +',
    '            "navigator.languages.join(\'|\'), Object.isFrozen(navigator.languages), " +',
    '            "navigator.platform, navigator.vendor, navigator.productSub])");',
]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the probe is one clean expression")
