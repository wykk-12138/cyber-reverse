import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorPlacementTests.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

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

comment_one = "        // One expression, no embedded newlines: an escaped newline inside a C# string becomes a real"
comment_two = "        // newline in the JavaScript, and a newline inside a quoted literal is a SyntaxError."

replacement = [
    comment_one,
    comment_two,
    "        var probe = await bridge.EvaluateAsync(",
    '            "JSON.stringify([navigator.language, navigator.languages.length, " +',
    '            "navigator.languages.join(chr), Object.isFrozen(navigator.languages), " +',
    '            "navigator.platform, navigator.vendor, navigator.productSub])");',
]

# use a single-quoted separator built at runtime so the C# string stays simple
replacement[4] = '            "navigator.languages.join(\'" + "|" + "\'), Object.isFrozen(navigator.languages), " +'

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the probe is one clean expression")
