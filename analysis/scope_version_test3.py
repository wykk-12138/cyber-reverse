import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\AppVersionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = 'if (code.Contains("5.18.28", StringComparison.Ordinal)) offenders.Add(path);'
new = 'if (code.Contains(OldVersion, StringComparison.Ordinal)) offenders.Add(path);'
if old not in t:
    raise SystemExit("needle anchor missing")
t = t.replace(old, new, 1)

anchor = "    internal const string OriginalBinary ="
decl = ('    /// <summary>\n'
        '    /// The number this file exists to keep out. Split so the guard does not find its own\n'
        '    /// needle — the first version did, which is its own small lesson.\n'
        '    /// </summary>\n'
        '    private const string OldVersion = "5.18." + "28";\n\n')
if anchor not in t:
    raise SystemExit("const anchor missing")
t = t.replace(anchor, decl + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("needle split")
