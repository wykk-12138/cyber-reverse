import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
old_start = t.index('    [Fact]\n    public void TheBackupFileUsesTheImagesKeyNames()')
old_end = t.index('\n}\n', old_start)
new = '''    [Fact]
    public void TheBackupFileUsesTheImagesKeyNames()
    {
        // R385: assert the file that would actually be written, not the attribute names — the project serialises with
        // Newtonsoft, so a System.Text.Json attribute here would have passed this test while writing different keys.
        var live = new[]
        {
            "proxies", "billing", "accounts", "solvers", "settings", "tasks",
            "smartActions", "smartActionUtilities", "analytics",
        };

        var json = Newtonsoft.Json.JsonConvert.SerializeObject(
            new Cybersole.Core.Store.BackupDocument(), Cybersole.Core.AppPaths.Json.Default);

        var written = Newtonsoft.Json.Linq.JObject.Parse(json).Properties().Select(p => p.Name).ToList();

        _out.WriteLine(string.Join(", ", written.OrderBy(x => x)));
        Assert.Equal(live.OrderBy(x => x), written.OrderBy(x => x));
    }
'''
t = t[:old_start] + new + t[old_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test now serialises and checks real keys')
