import io, re
# 1) BINDING_BACKLOG: 11 -> 10 types, and refresh the table (ProfileCreatorView cleared, MonitorView added)
p = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"
t = io.open(p, encoding='utf-8').read()
t = t.replace('## 类型级缺口（11 个类型，`python tools/bind_scope.py`）',
              '## 类型级缺口（10 个类型，`python tools/bind_scope.py`）')
t = t.replace('## 类型级缺口（11 个类型', '## 类型级缺口（10 个类型')
# rewrite the table rows to the current 10
old_start = t.find('| `TaskView` | `Toggle` |')
old_end = t.find('\n\n', t.find('| `ProxyTester` |'))
if old_start > 0 and old_end > old_start:
    new_table = '''| `TaskView` | `Toggle` | 唯一剩下的：无 locale 线索、无 GUI 证据 |
| `Profile` | `Card` `Username` | 数据属性；`Profiles.Column.Card` / `Common.Username` 是**列名**不是值 |
| `ProxyTester` | `Name` | 无对应概念 |
| `MonitorView` | `LinkChange` `OpenFilter` `OpenUrl` `Quicktask` `View` | R427 新发现：原版这个页面还有五个绑定（我的新类同名，被 `bind_scope` 归过来） |
| `CloudflareSolversView` | `Edit` | 页面只有 Add / Fetch balance，无编辑路径 |
| `DataView` | `ViewLogs` | 需要日志查看器（`AppPaths.LogsDir` 存在） |
| `GeneralSettingsView` | `ProfileItems` | 数据列表，位置未定 |
| `GoogleAccountsView` | `Edit` | 无编辑路径 |
| `ImapView` | `Configure` | AYCD 配置对话框，位置未定 |
| `SmartActionsView` | `Clock` `Export` | `Settings.General.EnableClock` 有线索，位置未定 |'''
    t = t[:old_start] + new_table + t[old_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('BINDING_BACKLOG updated')

# 2) RESUME: 11 -> 10, 1575 -> 1606
p2 = r"D:\projects\cyber-reverse\replica\docs\RESUME.md"
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('**11 个类型**', '**10 个类型**')
t2 = t2.replace('**1575 通过 / 0 失败 / 2 跳过**', '**1606 通过 / 0 失败 / 2 跳过**')
t2 = t2.replace('R405 时点', 'R426 时点')
t2 = t2.replace('确认 1575+（R426 时点为 1575', '确认 1606+（R426 时点为 1606')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('RESUME updated')

# 3) SESSION_STATE: the "12 个类型级缺口" line -> 10
p3 = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t3 = io.open(p3, encoding='utf-8').read()
t3 = t3.replace('4. 12 个类型级缺口里，`TaskView.Toggle` 等仍无定论的项。',
                '4. 10 个类型级缺口里，`TaskView.Toggle`、`MonitorView` 的五个绑定等仍无定论的项。')
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('SESSION_STATE updated')
