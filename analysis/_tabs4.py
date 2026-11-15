import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# 1) tabs: exactly the four the locale names, in its order
old_tabs = '''        var tabs = new TabControl { Height = 480 };
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "General", Content = BuildGeneral() },
            new TabItem { Header = "Delays", Content = BuildDelays() },
            new TabItem { Header = "Limits", Content = BuildLimits() },
            new TabItem { Header = "Captcha", Content = BuildCaptcha() },
            new TabItem { Header = "Notifications", Content = BuildNotifications() },
            new TabItem { Header = "Manual", Content = BuildManual() },
        };'''
new_tabs = '''        // R352: the locale names exactly four tabs — TaskGroup.Tab.{Delays,Limits,Captcha,Notifications} — and has no
        // "General" and no "Manual" tab. The old Manual tab was a misreading of TaskGroup.TimeSpan.Manual, one of the
        // "Reset limits after" options; PeriodStart belongs to Limits (TaskGroup.PeriodStart.Tooltip sits there), and
        // Pinned / Order have no place in this dialog at all (Pinned is TaskView.PinGroups, Order is the global
        // Settings.TaskGroupOrder).
        var tabs = new TabControl { Height = 480 };
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "Delays", Content = BuildDelays() },
            new TabItem { Header = "Limits", Content = BuildLimits() },
            new TabItem { Header = "Captcha", Content = BuildCaptcha() },
            new TabItem { Header = "Notifications", Content = BuildNotifications() },
        };'''
assert old_tabs in t
t = t.replace(old_tabs, new_tabs, 1)

# 2) fold the period-start editor into Limits and drop BuildGeneral / BuildManual
def cut(text, start_marker, end_marker):
    a = text.index(start_marker)
    b = text.index(end_marker, a)
    return text[:a] + text[b:]

anchor_limits_end = '''    private Control BuildCaptcha()'''
period_block = '''        // R352: the period-start editor moved here from the old "Manual" tab — the locale puts its tooltip in this
        // panel ("Period starts when you first start a task") and TaskGroup.TimeSpan.Manual is one of the options above.
        var periodStart = UiKit.Text(_group.PeriodStart?.ToString("u"), watermark: "2026-01-01 00:00:00");
        periodStart.TextChanged += (_, _) =>
        {
            if (DateTime.TryParse(periodStart.Text, out var value)) _group.PeriodStart = value;
        };

'''
t = t.replace(anchor_limits_end, period_block + anchor_limits_end, 1)
t = cut(t, '    private Control BuildGeneral()', '    private Control BuildDelays()')
t = cut(t, '    private Control BuildManual()', '    private Control BuildCaptcha()')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('tabs reduced to four; General/Manual removed; period start moved into Limits')
