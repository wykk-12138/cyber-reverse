import io
note = ('\n> **口径说明（R326）**：这里的"UI 类"只数 `Window` / `UserControl` 子类（当前 84 = 26 + 58）。\n'
        '> `UnreachedUiTypesTests` 与指南用的是**另一个分母** —— `Cybersole.Ui` 里所有 public class（当前 104，其中 31 个从未构造）。\n'
        '> 两个数字都对，**不要试图把它们对齐**：一个是"窗口/控件"，一个是"全部 UI 类型"。\n')
p = r'D:\projects\cyber-reverse\replica\docs\PARITY.md'
t = io.open(p, encoding='utf-8').read()
anchor = '**84 个 UI 类：26 个 `Window` 子类 + 58 个 `UserControl` 子类。**'
assert anchor in t
t = t.replace(anchor, anchor + note, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('PARITY.md: denominator note added')

p2 = r'D:\projects\cyber-reverse\replica\docs\RESUME.md'
t2 = io.open(p2, encoding='utf-8').read()
old = '| 不可达 UI 类 | **31**（104 个中） | `UnreachedUiTypesTests` |'
new = ('| 不可达 UI 类 | **31**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |\n'
       '| `PARITY.md` 的 UI 类 | **84**（26 Window + 58 UserControl，分母不同） | `ParityDocTests` |')
assert old in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
print('RESUME.md: second row for the other denominator')
