import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs'
t = io.open(p, encoding='utf-8').read()
old = '    public const string EmptyTitle = "Nothing to see here";'
new = '    public static readonly string EmptyTitle = Common.EmptyView.Headline;'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('SettingsModals folded')
