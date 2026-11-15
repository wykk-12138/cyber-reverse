import io
pairs = [
 ("BackupMessage", "Successfully backed up all data.", "Data.Backup.Message"),
 ("BackupTitle", "Backup Success", "Data.Backup.Title"),
 ("ExportSuccessMessage", "Successfully exported data.", "Data.Export.Success.Message"),
 ("ImportFailMessage", "Failed to import data.", "Data.Import.Fail.Message"),
 ("ImportFailTitle", "Import Fail", "Data.Import.Fail.Title"),
 ("ImportSuccessMessage", "Successfully imported data.", "Data.Import.Success.Message"),
 ("ImportSuccessTitle", "Import Success", "Data.Import.Success.Title"),
 ("ImportUnsupportedTitle", "File Unsupported", "Data.Import.Unsupported.Title"),
 ("ImportUnsupportedJson", "This file type is unsupported. Please import a JSON file.", "Data.Import.UnsupportedJson"),
 ("ImportUnsupportedJsonCsv", "This file type is unsupported. Please import a JSON / CSV file.", "Data.Import.UnsupportedJsonCsv"),
 ("ResetMessage", "This will clear all data.", "Data.Reset.Message"),
 ("RestoreFailedTitle", "Restore Failed", "Data.Restore.Failed.Title"),
 ("RestoreSuccessMessage", "Successfully restored all data from backup.", "Data.Restore.Success.Message"),
 ("RestoreSuccessTitle", "Restored Successfully", "Data.Restore.Success.Title"),
]
lines = ['', "    // ------------------------------------------------ copy from the image's locale (R414)", '    //',
         "    // The Data.* strings that had no counterpart, verbatim (same table shape as the other pages). Export's failure",
         "    // pair was already here from R349; these are the rest of the family.",
         "    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)",
         '    {']
for name, value, key in pairs:
    esc = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
lines.append('    };')
lines.append('')
lines.append("    /// <summary>One of the image's data-page strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')
block = '\n'.join(lines)

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()
i = t.index('public sealed class DataView')
brace = t.index('{', i)
line_end = t.index('\n', brace) + 1
assert 'IReadOnlyDictionary<string, string> Copy' not in t[line_end:line_end + 4000]
t = t[:line_end] + block + t[line_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('14 data strings captured')
