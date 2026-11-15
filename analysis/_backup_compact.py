import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\ConfigurationStore.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        var name = $"Backup {DateTime.Now:dd MMM HH\\\\hmm\\\\m}.cyb";
        File.WriteAllText(Path.Combine(AppPaths.BackupsDir, name), Json.Serialize(snapshot));'''
new = '''        var name = $"Backup {DateTime.Now:dd MMM HH\\\\hmm\\\\m}.cyb";

        // R388: a real 5.18.32 backup is written COMPACT (no newlines, no space after ':'): its first bytes are
        // {"proxies":[{"id":"66da0f96","name":"Group 1",… . Serialising with the indented default produced a file the
        // original would still read, but not one it would have written, so the writer now uses a compact clone.
        var compact = (JsonSerializerSettings)Json.Default;
        var settings = new JsonSerializerSettings
        {
            ContractResolver = compact.ContractResolver,
            Formatting = Newtonsoft.Json.Formatting.None,
            NullValueHandling = compact.NullValueHandling,
            DateTimeZoneHandling = compact.DateTimeZoneHandling,
            Converters = compact.Converters,
        };
        File.WriteAllText(Path.Combine(AppPaths.BackupsDir, name), Newtonsoft.Json.JsonConvert.SerializeObject(snapshot, settings));'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('backups now written compact, like the original')
