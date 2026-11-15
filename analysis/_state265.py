import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
old = '| `SmartActionsCreator` | `UseTemplate` | 需要模板来源（`TemplateGroup` / `Template` 在复刻件里没有） |'
new = '''| `SmartActionsCreator` | `UseTemplate` | 需要模板来源（`TemplateGroup` / `Template` 在复刻件里没有） |'''
t = t.replace('| `Platform` | `InputType`, `QuantitySupport`, `QuantityAutoAdjustSupport` | **不可得**：值不在池子里、下拉点不开（R242） |',
              '| `Platform` | `InputType`, `QuantitySupport`, `QuantityAutoAdjustSupport` | **不可得（三个独立来源确认）**：池子只有成员名（R225）、下拉点不开（R242）、locale 里 `Platform.*` 零键（R265） |')
t = t.replace('| `ProfileCsvRow` / `FilterRow` / `ActionRow` | 3+3+2 | 行控件在复刻件里是内联构造 → **抽控件**或记结构差异 |',
              '| `ProfileCsvRow` / `FilterRow` / `ActionRow` | 3+3+2 | 行控件在复刻件里是内联构造；locale 里也没有对应文案键（R265）→ 属**纯内部状态**，建议记为结构差异 |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backlog doc updated with the third-source evidence')
