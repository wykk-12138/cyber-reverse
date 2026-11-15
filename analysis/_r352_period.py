import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# PeriodStart moves into Limits: the locale puts its tooltip there.
anchor = '''    private Control BuildCaptcha()'''
add = '''        // R352: the period-start editor moved here from the old "Manual" tab — the locale keeps its tooltip in this
        // panel ("Period starts when you first start a task") and TaskGroup.TimeSpan.Manual is one of the options above.
        var periodStart = UiKit.Text(_group.PeriodStart?.ToString("u"), watermark: "2026-01-01 00:00:00");
        periodStart.TextChanged += (_, _) =>
        {
            if (DateTime.TryParse(periodStart.Text, out var value)) _group.PeriodStart = value;
        };

    private Control BuildCaptcha()'''
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('period-start block staged (needs wiring into the Limits form)')
