import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    public Func<string?> Clipboard { get; set; } = () =>
    {
        // the clipboard lives on a TopLevel, so a view without a window simply has nothing to read
        var top = TopLevel.GetTopLevel(this);
        return top is null ? null : top.Clipboard?.GetTextAsync().GetAwaiter().GetResult();
    };'''
new = '''    public Func<string?>? Clipboard { get; set; }

    /// <summary>Reads the clipboard through this view's window, or null when it has none.</summary>
    private string? ReadClipboard()
    {
        if (Clipboard is not null) return Clipboard();

        var top = TopLevel.GetTopLevel(this);
        return top?.Clipboard?.GetTextAsync().GetAwaiter().GetResult();
    }'''
assert old in t
t = t.replace(old, new, 1)
t = t.replace('var text = (Clipboard?.Invoke() ?? string.Empty).Trim();', 'var text = (ReadClipboard() ?? string.Empty).Trim();')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('clipboard seam fixed')
