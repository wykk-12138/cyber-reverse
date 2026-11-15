import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()

old = '''            try
            {
                services.Config.Export(picked.Path.LocalPath, kind);
                var size = new FileInfo(picked.Path.LocalPath).Length;
                status.Text = $"Exported {kind} ({size / 1024} KB).";
            }
            catch (Exception ex)
            {
                status.Text = "Export failed: " + ex.Message;
            }'''
new = '''            try
            {
                services.Config.Export(picked.Path.LocalPath, kind);
                var size = new FileInfo(picked.Path.LocalPath).Length;
                status.Text = $"{DataView.ExportSuccessTitle}: {kind} ({size / 1024} KB)";
            }
            catch (Exception ex)
            {
                // R349: the image carries a title and a message for this failure (Data.Export.Fail.Title / .Message),
                // so the status line leads with the title it prints there instead of a home-grown sentence.
                status.Text = $"{DataView.ExportFailTitle} — {DataView.ExportFailMessage} ({ex.Message})";
            }'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''    /// <summary>The data kinds this page can export/import (bound as <c>DataProviders</c>).</summary>'''
add = '''    // R349: the export toast copy, verbatim from the locale (Data.Export.*).
    public const string ExportSuccessTitle = "Export Success";
    public const string ExportFailTitle = "Export Fail";
    public const string ExportFailMessage = "Failed to export data.";

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('export copy from the locale')
