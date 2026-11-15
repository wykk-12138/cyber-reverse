import io
p = r'D:\projects\cyber-reverse\replica\docs\PARITY.md'
t = io.open(p, encoding='utf-8').read()
old = '**83 个 UI 类：26 个 `Window` 子类 + 57 个 `UserControl` 子类。**'
new = '**84 个 UI 类：26 个 `Window` 子类 + 58 个 `UserControl` 子类。**'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('PARITY.md 83/26/57 -> 84/26/58')
