import io
# 1) PARITY.md: 58 UserControl -> 59, total 84 -> 85
p = r"D:\projects\cyber-reverse\replica\docs\PARITY.md"
t = io.open(p, encoding='utf-8').read()
t = t.replace('**84 个 UI 类：26 个 `Window` 子类 + 58 个 `UserControl` 子类。**',
              '**85 个 UI 类：26 个 `Window` 子类 + 59 个 `UserControl` 子类。**', 1)
t = t.replace('这里的"UI 类"只数 `Window` / `UserControl` 子类（当前 84 = 26 + 58）',
              '这里的"UI 类"只数 `Window` / `UserControl` 子类（当前 85 = 26 + 59）', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('PARITY.md 58 -> 59, 84 -> 85')

# 2) guide: 104 -> 105 classes, 28 -> 29 unreachable
for gp in ('docs/SESSION_STATE.md', 'docs/VERDICT.md', 'docs/RESUME.md'):
    path = r"D:\projects\cyber-reverse\replica\\" + gp.replace('/', '\\')
    g = io.open(path, encoding='utf-8').read()
    g = g.replace('104 声明 / 28 不可达', '105 声明 / 29 不可达')
    g = g.replace('104 声明 / 29 不可达', '105 声明 / 29 不可达')
    g = g.replace('**104 个，**28 个不可达', '**105 个，**29 个不可达')
    g = g.replace('104 个，**28 个不可达**', '105 个，**29 个不可达**')
    g = g.replace('| 不可达 UI 类 | **28**（104 个中', '| 不可达 UI 类 | **29**（105 个中')
    io.open(path, 'w', encoding='utf-8', newline='').write(g)
print('docs numbers bumped')

# 3) the unreachable baseline gains MonitorView
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t2 = io.open(p2, encoding='utf-8').read()
old = '"TaskCreatorView", "GroupSummary",'
new = '"TaskCreatorView", "GroupSummary", "MonitorView",'
assert old in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
print('MonitorView added to the unreachable baseline')
