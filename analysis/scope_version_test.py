import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\AppVersionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var offenders = new List<string>();
        foreach (var path in Directory.EnumerateFiles(root!, "*.cs", SearchOption.AllDirectories)
                     .Concat(Directory.EnumerateFiles(root!, "*.md", SearchOption.AllDirectories)))
        {'''
new = '''        // Source only. The docs are allowed to name the old number — a correction that cannot say
        // what it corrected is a worse record than the mistake.
        var offenders = new List<string>();
        foreach (var path in Directory.EnumerateFiles(root!, "*.cs", SearchOption.AllDirectories))
        {'''
if old not in t:
    raise SystemExit("scope anchor missing")
t = t.replace(old, new, 1)

# Wording: it is a scan of the code, not of the tree.
t = t.replace("""    /// The old number must not survive anywhere in the tree. R74 found 54 occurrences in 34 files;
    /// a partial fix is how a wrong version comes back.""",
              """    /// The old number must not survive in the code. R74 found 54 occurrences in 34 files — most of
    /// them User-Agent strings and settings defaults — and a partial fix is how a wrong version
    /// comes back.""")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("scoped the guard to source files")
