import io, re
# LoginControl already has a Text(...) member; rename the table getter to CopyText there
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\LoginControl.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>One of the image's strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;'''
new = '''    /// <summary>One of the image's strings, by the short name used in <see cref="Copy"/> (CopyText: this class already
    /// has a Text member).</summary>
    public static string CopyText(string name) => Copy.TryGetValue(name, out var value) ? value : string.Empty;'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('LoginControl.Text -> CopyText')

# add the two leftovers
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\LoginControl.cs"
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('        ["LoginWaiting"]', '        ["BackToLogin"] = "Back to login",   // Auth.BackToLogin\n        ["LoginWaiting"]', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)

p3 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t3 = io.open(p3, encoding='utf-8').read()
t3 = t3.replace('        ["SearchPlaceholder"] = "Search history"', '        ["Clear"] = "Clear History",   // HistoryWindow.Clear\n        ["SearchPlaceholder"] = "Search history"', 1)
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('two leftovers added')
