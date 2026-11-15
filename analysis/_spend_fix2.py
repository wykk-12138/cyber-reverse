import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Avalonia;\n', 'using System.Globalization;\nusing Avalonia;\n', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using added at the top')
