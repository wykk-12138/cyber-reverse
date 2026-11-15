import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        Reload();', '        LoadAnalytics();', 1)
# OpenRelease has no release catalogue to stand on — remove it rather than invent one
start = t.index('    /// <summary>\n    /// Opens a release\'s page (bound as <c>OpenRelease</c>)')
end = t.index('    public AnalyticsView(AppServices services)')
removed = t[start:end]
t = t[:start] + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ChangeChart uses LoadAnalytics; OpenRelease removed (%d chars) — no release catalogue exists' % len(removed))
