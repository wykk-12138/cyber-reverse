import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 26;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('当前 29 = 0 可做 + 29 结构（A 类清零；R312 关掉 ComboBoxEdit 两条）',
                '当前 26 = 0 可做 + 26 结构（A 类清零；R312 ComboBoxEdit、R314 ProfileCsvRow）')
t2 = t2.replace('| `ProfileCsvRow` / `FilterRow` / `ActionRow` | 3+3+2 | 行控件在复刻件里是内联构造；locale 里也没有对应文案键（R265）→ 属**纯内部状态**，建议记为结构差异 |',
                '| ~~`ProfileCsvRow`~~ / `FilterRow` / `ActionRow` | 0+3+2 | **R314 已实现 `ProfileCsvRow`**（`Views/Profiles/Modals/ProfileCsvRow.cs`，接在 `ProfileCsvEditorView.Rows`） |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ceiling 26 + backlog updated')
