import io, re
R = r'D:\projects\cyber-reverse\replica'

# baseline: two more windows are constructed now
p = R + r'\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
for name in ('"HistoryWindow"', '"ReleaseGuideView"'):
    lines = t.splitlines(True)
    out = []
    for line in lines:
        if name in line:
            line = line.replace(name + ', ', '').replace(', ' + name, '').replace(name, '')
            if line.strip() in ('', ','):
                continue
        out.append(line)
    t = ''.join(out)
t = t.replace('        // R232: NotificationView / UserView are constructed by MainWindow.OpenNotifications / OpenProfile.',
              '        // R232: NotificationView / UserView are constructed by MainWindow.OpenNotifications / OpenProfile.\n'
              '        // R261: HistoryWindow by SmartActionsView.ViewLogs; ReleaseGuideView by ReleaseView.ShowGuide.')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('baseline trimmed')

# guide count
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 97 个，**31 个不可达**（32%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 97 个，**29 个不可达**（30%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide 97 / 29')

# ceiling from the measurement
p3 = R + r'\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t3 = io.open(p3, encoding='utf-8').read()
t3 = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 36;', t3)
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('ceiling set to the measured 36')
