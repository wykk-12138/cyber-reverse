import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('''            _smartAction = value;
            Title = string.Format(LocaleLogsFormat, value?.Name ?? "All smart actions");
            Refresh();''',
'''            _smartAction = value;
            Title = string.Format(LocaleLogsFormat, value?.Name ?? "All smart actions");
            Render();''', 1)
t = t.replace('''            _view = value;
            Refresh();''',
'''            _view = value;
            Render();''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('uses Render() (the class has no Refresh)')
