import io
pairs = [
 ("AddRow", "Add Row", "ProfileCsv.AddRow"),
 ("AllColumns", "All columns", "ProfileCsv.AllColumns"),
 ("Apply", "Apply Changes", "ProfileCsv.Apply"),
 ("Clipboard", "clipboard", "ProfileCsv.Clipboard"),
 ("ConfirmDeleteFormat", "Apply and delete {0} profiles", "ProfileCsv.ConfirmDeleteFormat"),
 ("DeleteRows", "Delete Rows", "ProfileCsv.DeleteRows"),
 ("Duplicate", "Duplicate Rows", "ProfileCsv.Duplicate"),
 ("MenuClear", "Clear Cells", "ProfileCsv.Menu.Clear"),
 ("MenuCopy", "Copy", "ProfileCsv.Menu.Copy"),
 ("MenuFillDown", "Fill Down", "ProfileCsv.Menu.FillDown"),
 ("MenuPaste", "Paste", "ProfileCsv.Menu.Paste"),
 ("ErrorBoolean", "Use true or false", "ProfileCsv.Error.Boolean"),
 ("ErrorMonth", "Month must be between 1 and 12", "ProfileCsv.Error.Month"),
 ("ErrorNameRequired", "Profile name is required", "ProfileCsv.Error.NameRequired"),
 ("ErrorYear", "Year must be 2 or 4 digits", "ProfileCsv.Error.Year"),
 ("Export", "Export CSV", "ProfileCsv.Export"),
 ("Find", "Find", "ProfileCsv.Find"),
 ("Import", "Import CSV", "ProfileCsv.Import"),
 ("ModeGrid", "Grid", "ProfileCsv.Mode.Grid"),
 ("ModeText", "Raw CSV", "ProfileCsv.Mode.Text"),
 ("Regex", "Regex", "ProfileCsv.Regex"),
 ("ReplaceAll", "Replace All", "ProfileCsv.ReplaceAll"),
 ("ReplaceWith", "Replace with", "ProfileCsv.ReplaceWith"),
 ("StatusDiscardConfirm", "You have unsaved changes. Close again to discard them.", "ProfileCsv.Status.DiscardConfirm"),
 ("StatusExported", "Exported {0} rows to {1}", "ProfileCsv.Status.Exported"),
 ("StatusFixErrors", "Fix the highlighted cells before applying", "ProfileCsv.Status.FixErrors"),
 ("StatusIgnoredColumns", "Ignored unknown columns: {0}", "ProfileCsv.Status.IgnoredColumns"),
 ("StatusImported", "Merged {0} rows from {1}", "ProfileCsv.Status.Imported"),
 ("StatusNoHeader", "The CSV needs a header row with known column names", "ProfileCsv.Status.NoHeader"),
 ("StatusParseFailed", "Couldn't read the CSV: {0}", "ProfileCsv.Status.ParseFailed"),
 ("StatusRegexInvalid", "Invalid regular expression", "ProfileCsv.Status.RegexInvalid"),
 ("StatusReplaced", "Replaced {0} values", "ProfileCsv.Status.Replaced"),
 ("SummaryEdited", "{0} edited", "ProfileCsv.Summary.Edited"),
 ("SummaryErrors", "{0} errors", "ProfileCsv.Summary.Errors"),
 ("SummaryNew", "{0} new", "ProfileCsv.Summary.New"),
 ("SummaryNone", "No changes", "ProfileCsv.Summary.None"),
 ("SummaryRemoved", "{0} removed", "ProfileCsv.Summary.Removed"),
 ("Title", "CSV Editor", "ProfileCsv.Title"),
 ("Undo", "Undo", "ProfileCsv.Undo"),
]

lines = []
lines.append('\n    // ------------------------------------------------ copy from the image\'s locale (R410)')
lines.append('    //')
lines.append('    // The whole ProfileCsv.* family, verbatim from the string table. The editor had a handful of these strings as')
lines.append('    // literals scattered through the body; this table is the single place they live, with the key each one came from.')
lines.append('    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)')
lines.append('    {')
for name, value, key in pairs:
    esc = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
lines.append('    };')
lines.append('')
lines.append('    /// <summary>One of the image\'s CSV-editor strings, by the short name used in <see cref="Copy"/>.</summary>')
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')

block = '\n'.join(lines)

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>The columns the editor accepts (bound as <c>ColumnChoices</c>).</summary>'''
assert anchor in t and 'public static readonly IReadOnlyDictionary<string, string> Copy' not in t
t = t.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('39 ProfileCsv strings captured in one table')
