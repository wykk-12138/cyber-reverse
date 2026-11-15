import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public GoogleAccountsView(AppServices services)'''
add = '''    /// <summary>
    /// The YouTube channel/tab this view is pointed at (bound as <c>YouTube</c>, R366). The image exposes it as a
    /// get/set property and formats a window title as "YouTube - {0}"; what fills it is still unknown, so it is a plain
    /// string with no behaviour behind it.
    /// </summary>
    public string? YouTube { get; set; }

''' + anchor
assert anchor in t and 'public string? YouTube { get; set; }' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('GoogleAccountsView.YouTube added (string, property)')
