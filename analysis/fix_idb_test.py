import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\IDBEvidenceTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var rows = Doc().Split('\\n')
            .Where(l => l.StartsWith("| ", StringComparison.Ordinal) && l.Contains("`", StringComparison.Ordinal))
            .ToList();'''
new = '''        // Only the first table is the query log; the second one maps counts to code and has no
        // cursor column, so scanning the whole document would flag it.
        var doc = Doc();
        var cut = doc.IndexOf("## 数字与代码的对应", StringComparison.Ordinal);
        Assert.True(cut > 0, "the query table section is missing");

        var rows = doc[..cut].Split('\\n')
            .Where(l => l.StartsWith("| ", StringComparison.Ordinal) && l.Contains("`", StringComparison.Ordinal))
            .ToList();'''
if old not in t:
    raise SystemExit("scan anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("scan scoped to the query table")
