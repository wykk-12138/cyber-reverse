import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

# R352 (retry, whole-method anchors only): four tabs, as the locale names them.
old = '''        var tabs = new TabControl { Height = 480 };
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "General", Content = BuildGeneral() },
            new TabItem { Header = "Delays", Content = BuildDelays() },
            new TabItem { Header = "Limits", Content = BuildLimits() },
            new TabItem { Header = "Captcha", Content = BuildCaptcha() },
            new TabItem { Header = "Notifications", Content = BuildNotifications() },
            new TabItem { Header = "Manual", Content = BuildManual() },
        };'''
new = '''        // R352: the locale names exactly four tabs — TaskGroup.Tab.{Delays,Limits,Captcha,Notifications} — with no
        // "General" and no "Manual". The old Manual tab misread TaskGroup.TimeSpan.Manual, which is one of the "Reset
        // limits after" options; PeriodStart belongs to the Limits tab (its tooltip lives there) and the group's
        // Pinned/Order are not part of this dialog at all (Pinned is TaskView.PinGroups, Order is
        // Settings.TaskGroupOrder), so those three controls are gone rather than relocated.
        var tabs = new TabControl { Height = 480 };
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "Delays", Content = BuildDelays() },
            new TabItem { Header = "Limits", Content = BuildLimits() },
            new TabItem { Header = "Captcha", Content = BuildCaptcha() },
            new TabItem { Header = "Notifications", Content = BuildNotifications() },
        };'''
assert old in t, 'tab block not found'
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('tabs reduced to four')
