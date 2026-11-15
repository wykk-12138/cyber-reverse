import io
base = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings'
subs = [
    ('ProviderViews.cs', 'UiKit.Empty("Nothing to see here")', 'UiKit.Empty(EmptyView.Headline)'),
    ('ProviderViews.cs', 'public const string DialogEmptyTitle = "Nothing to see here";',
                          'public static readonly string DialogEmptyTitle = EmptyView.Headline;'),
    ('ProviderViews.cs', 'EmptyPane("Nothing to see here", "Add some size presets to get started")',
                          'EmptyPane(EmptyView.Headline, "Add some size presets to get started")'),
    ('SettingsViews.cs', 'new AccountTable(Columns, "Nothing to see here", EmptySubtitle)',
                          'new AccountTable(Columns, EmptyView.Headline, EmptySubtitle)'),
]
for name, old, new in subs:
    p = base + '\\' + name
    t = io.open(p, encoding='utf-8').read()
    n = t.count(old)
    if n == 0:
        print('MISS', name, old[:50]); continue
    t = t.replace(old, new)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('ok', name, 'replaced', n, '->', new[:60])

# ProviderViews:603 -- the remaining bare literal in a TextBlock; look at context
p = base + r'\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()
lines = t.splitlines()
print('--- 596..612 ---')
for i in range(595, 612):
    print(i+1, lines[i])
