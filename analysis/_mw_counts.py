import io
R = r'D:\projects\cyber-reverse\replica'
p = R + r'\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
for name in ('"NotificationView"', '"UserView"'):
    # remove the entry from whichever baseline line holds it
    lines = t.splitlines(True)
    for i, line in enumerate(lines):
        if name in line and 'R23' not in line:
            lines[i] = line.replace(name + ', ', '').replace(', ' + name, '').replace(name, '')
            break
    t = ''.join(lines)
t = t.replace('        // R231: StoreGroupModal is constructed by UtilitiesView.EditStoreGroup (the bound EditStoreGroup command).',
              '        // R231: StoreGroupModal is constructed by UtilitiesView.EditStoreGroup (the bound EditStoreGroup command).\n'
              '        // R232: NotificationView / UserView are constructed by MainWindow.OpenNotifications / OpenProfile.')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('baseline trimmed')

p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 97 个，**35 个不可达**（36%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 97 个，**33 个不可达**（34%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide 97 / 33')
