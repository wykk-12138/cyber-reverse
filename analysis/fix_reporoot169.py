import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PruneWhitelistTests.cs"
t = io.open(p, encoding="utf-8").read()

# add the RepoRoot helper before the final closing brace of the class
idx = t.rstrip().rfind("}")
helper = '''
    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
'''

t = t.rstrip()[:idx].rstrip() + "\n" + helper
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the helper is added")
