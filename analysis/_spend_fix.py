import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('public static string SpendFigure(double amount) => "$" + Math.Round(amount).ToString("0");',
              'public static string SpendFigure(decimal amount) => "$" + Math.Round(amount).ToString("0", CultureInfo.InvariantCulture);')
if 'using System.Globalization;' not in t:
    t = t.replace('using System.Linq;', 'using System.Globalization;\nusing System.Linq;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('decimal signature')
