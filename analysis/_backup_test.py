import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheBackupFileUsesTheImagesKeyNames()
    {
        // a real 5.18.32 backup (Backups/Backup 14 Nov 08h01m.cyb) has exactly these nine top-level keys
        var live = new[]
        {
            "proxies", "billing", "accounts", "solvers", "settings", "tasks",
            "smartActions", "smartActionUtilities", "analytics",
        };

        var written = typeof(Cybersole.Core.Store.BackupDocument)
            .GetProperties()
            .Select(p => p.GetCustomAttributes(typeof(System.Text.Json.Serialization.JsonPropertyNameAttribute), false)
                .Cast<System.Text.Json.Serialization.JsonPropertyNameAttribute>()
                .Select(a => a.Name)
                .FirstOrDefault() ?? p.Name)
            .ToList();

        _out.WriteLine(string.Join(", ", written.OrderBy(x => x)));
        Assert.Equal(live.OrderBy(x => x), written.OrderBy(x => x));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backup-key test appended')
