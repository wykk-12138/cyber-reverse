import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EngineParityTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.DoesNotContain("prepareStackTrace =", js, System.StringComparison.Ordinal);
        Assert.Contains("prepareStackTrace", EngineParity.Rule + string.Join("", EngineParity.Messages.Keys));'''

new = '''        Assert.DoesNotContain("prepareStackTrace =", js, System.StringComparison.Ordinal);

        // and the trade-off is stated where the next reader will find it: in the class documentation
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "src", "Cybersole.Stores", "Scripts", "EngineParity.cs"));
        Assert.Contains("prepareStackTrace", source);'''

if old not in t:
    raise SystemExit("prepareStackTrace anchor missing")
t = t.replace(old, new, 1)

idx = t.rstrip().rfind("}")
t = t.rstrip()[:idx].rstrip() + '''

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
'''

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the assertion reads the source")
