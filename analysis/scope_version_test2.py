import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\AppVersionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            var text = File.ReadAllText(path);
            if (text.Contains("5.18.28", StringComparison.Ordinal)) offenders.Add(path);'''
new = '''            // Code only: a comment or an XML-doc line may name the old number, because a
            // correction that cannot say what it corrected is a worse record than the mistake.
            var code = string.Join("\\n", File.ReadAllLines(path)
                .Where(line => !line.TrimStart().StartsWith("//", StringComparison.Ordinal)));

            if (code.Contains("5.18.28", StringComparison.Ordinal)) offenders.Add(path);'''
if old not in t:
    raise SystemExit("scan anchor missing")
t = t.replace(old, new, 1)

# The self-exclusion is no longer needed once comments are skipped.
t = t.replace('''            // This file names the old number on purpose, to say why it went.
            if (Path.GetFileName(path) == "AppVersionTests.cs") continue;

''', "")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("guard now skips comments instead of whole files")
