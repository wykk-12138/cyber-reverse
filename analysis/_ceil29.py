import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 29;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('当前 31 = 0 可做 + 31 结构（A 类清零）', '当前 29 = 0 可做 + 29 结构（A 类清零；R312 关掉 ComboBoxEdit 两条）')
t2 = t2.replace('| `ComboBoxEdit` | `ClearSelectionCommand`, `RemoveTokenCommand` | 用 `UiKit` 组合实现，无此控件 |',
                '| ~~`ComboBoxEdit`~~ | ~~`ClearSelectionCommand`, `RemoveTokenCommand`~~ | **R312 已实现**（`Views/Controls/ComboBoxEdit.cs`，5 条测试） |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ceiling 29 + backlog updated')
