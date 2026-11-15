import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyOrderTableTests.cs"
t = io.open(p, encoding="utf-8").read()

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
print("helper added")
