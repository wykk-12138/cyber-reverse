import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 365 轮：`ProfileView` 三个成员（类型级缺口 19 → 18）

| 成员 | 实现 |
|---|---|
| `Groups` | 组名列表（来自 `Config.BillingGroups`） |
| `DeleteSelected` | 从**当前组**移除所选 profile，保存，刷新 |
| `EditSelected` | 打开所选 profile 的编辑器（传 `Id`） |

### 三次编译失败，全是同一个根

1. `_services.Config.Profiles` —— **没有这个集合**（配置里是 `BillingGroups`，每组带 `Profiles`）；
2. `CurrentGroup()` —— 类里**已经有**一个同名方法；
3. `ShowGroup(group)` —— 不存在；类里叫 `Refresh()`。

三次都是"我以为这个类里有/没有某样东西"。§12 说"先读字段"，这一轮补一条：
**先读方法列表**（`grep 'public|private'`），不只看字段。

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 19 → 18
```
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §12.2 读类时也要读"已有哪些方法"（R365）

`ProfileView` 我写了 `CurrentGroup()` 与 `ShowGroup(group)` —— 前者**重名**、后者**不存在**（叫 `Refresh`）。
字段读对了，方法没读。

规则：加成员前 `grep -E 'public|private' <file>` 看一眼**字段和方法**两张表；
`grep 'Config\\.' <file>` 看一眼**配置里真实有哪些集合**（这一轮 `Config.Profiles` 就不存在）。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §12.2 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 365 轮（`ProfileView.Groups/DeleteSelected/EditSelected`；类型级缺口 18）。

---

## 类型级缺口：18（起点 52）

剩下的都是界面动作或类型不可推断：
`TaskView`(6) · `GroupSummary`(3) · `ProfileCreatorView`(3) · `DataView.ViewLogs` ·
`SmartActionsView.Clock/Export` · `ReleaseView.ShowSitelist` · `ImapView.Configure` · `PublishTemplateModal.Groups`

## 新纪律（`docs/METHOD.md` §12.2）

读类时**同时读字段与方法**；写 `Config.X` 之前先 `grep 'Config\\.'` 确认那个集合真的存在。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
