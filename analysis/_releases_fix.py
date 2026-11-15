import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('        var cards = LoadReleases(byStore);\n        if (cards.Count == 0)',
              '        var cards = LoadReleases(byStore).ToList();\n        if (cards.Count == 0)')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('materialised the sequence before counting')
