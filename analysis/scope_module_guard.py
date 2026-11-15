import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DocsConsistencyTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // every "<n> 个模块 / "<n> modules" claim in the document
        var claims = Regex.Matches(doc, @"(\\d+)\\s*(?:个模块|modules)")'''

new = '''        // Fenced blocks are quoted output from past runs ("catalogue: 61 modules"), not claims
        // this document is making. R91 added a module and the guard went red on a log line from
        // three rounds earlier — the fix is to leave history alone and scan prose only.
        var prose = Regex.Replace(doc, "```.*?```", "\n", RegexOptions.Singleline);

        // every "<n> 个模块 / "<n> modules" claim in the document
        var claims = Regex.Matches(prose, @"(\\d+)\\s*(?:个模块|modules)")'''

if old not in t:
    raise SystemExit("claim-regex anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("guard now scans prose only")
