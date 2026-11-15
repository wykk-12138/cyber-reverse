import io
R = r'D:\projects\cyber-reverse\replica'
p = R + r'\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
out = []
for line in t.splitlines(True):
    s = line.strip()
    if s in ('"SmartActionsView",', '"UtilitiesView",'):
        continue
    if '"SmartActionsView"' in line or '"UtilitiesView"' in line:
        # remove just those names from a shared line
        line = line.replace('"SmartActionsView", ', '').replace(', "SmartActionsView"', '')
        line = line.replace('"UtilitiesView", ', '').replace(', "UtilitiesView"', '')
        if line.strip() in ('', ','):
            continue
    out.append(line)
io.open(p, 'w', encoding='utf-8', newline='').write(''.join(out))
print('baseline trimmed of SmartActionsView / UtilitiesView')

p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 97 个，**33 个不可达**（34%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 97 个，**31 个不可达**（32%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide 97 / 31')
