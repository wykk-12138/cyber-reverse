import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 32;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('当前 33 = 2 可做 + 31 结构', '当前 32 = 1 可做 + 31 结构')
t2 = t2.replace('| `SmartActionsCreator` | `UseTemplate` | 需要模板来源（`TemplateGroup` / `Template` 在复刻件里没有） |',
                '| `SmartActionsCreator` | ~~`UseTemplate`~~ | **R302 已实现**：模板只带元数据，用 `SourceActionId` 取源动作的 filters/steps |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ceiling 33 -> 32, backlog updated')
