import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# put the period-start row inside the Limits form and drop the stray block
old_form = '''        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Total checkout limit", checkoutLimit),
            UiKit.Row("Checkout limit per profile", profileLimit),
            UiKit.Row("Reset limits after", resetAfter),
            UiKit.Caption("Counters roll over automatically once the reset window elapses.")));'''
new_form = '''        // R352: the period-start editor lives here, not on a tab of its own — the locale keeps its tooltip in this panel
        // ("Period starts when you first start a task") and TaskGroup.TimeSpan.Manual is one of the options above.
        var periodStart = UiKit.Text(_group.PeriodStart?.ToString("u"), watermark: "2026-01-01 00:00:00");
        periodStart.TextChanged += (_, _) =>
        {
            if (DateTime.TryParse(periodStart.Text, out var periodValue)) _group.PeriodStart = periodValue;
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Total checkout limit", checkoutLimit),
            UiKit.Row("Checkout limit per profile", profileLimit),
            UiKit.Row("Reset limits after", resetAfter),
            UiKit.Row("Period start", periodStart),
            UiKit.Caption("Counters roll over automatically once the reset window elapses.")));'''
assert old_form in t
t = t.replace(old_form, new_form, 1)

# remove the stray block that landed at class level
stray_start = t.index('        // R352: the period-start editor moved here from the old "Manual" tab')
stray_end = t.index('    private Control BuildCaptcha()')
t = t[:stray_start] + t[stray_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('limits form now carries period start; stray block removed')
