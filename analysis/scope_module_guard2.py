import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DocsConsistencyTests.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

# Find the line with the claims regex and insert the prose-only scoping right before it.
target = None
for i, line in enumerate(lines):
    if "var claims = Regex.Matches(doc," in line:
        target = i
        break
if target is None:
    raise SystemExit("claims line not found")

inject = [
    "        // Fenced blocks are quoted output from past runs (\"catalogue: 61 modules\"), not",
    "        // claims this document is making. R91 added a module and the guard went red on a log",
    "        // line from three rounds earlier — leave history alone, scan prose only.",
    '        var prose = Regex.Replace(doc, "```.*?```", "\\n", RegexOptions.Singleline);',
    "",
]
lines[target] = lines[target].replace("Regex.Matches(doc,", "Regex.Matches(prose,")
lines = lines[:target] + inject + lines[target:]

io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("injected prose scoping at line", target + 1)
