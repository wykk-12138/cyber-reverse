import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 376 轮：`GroupSummary` 的 `Edit` / `Clone` / `Delete`（缺口 16 → 15）

| 成员 | 实现 |
|---|---|
| `Edit` | 只读布尔：这个摘要是不是在编辑某个组 |
| `Clone` | 复制组与其任务（名字加 " copy"，延迟/上限/Pinned 一并抄），写入配置并保存，返回新组 |
| `Delete` | 从配置移除并保存；第二次调用返回 false |

`Clone` 的两条测试把关键约束钉住：**组 id 必须是新的**、**任务数一致**、
**延迟等设置也被复制**（这类"复制了一半"的 bug 我见过）。

```
完整套件   1536 通过 / 0 失败 / 2 跳过
bind_scope 16 → 15
```

### 这一轮的一句话

> 复制功能最容易只抄一半 —— 所以测试里专门断言了"设置也抄了"。

> **复制操作的正确性，取决于你记不记得抄那些看不见的字段。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 376 轮（`GroupSummary.Edit/Clone/Delete`；类型级缺口 16 → 15）。

---

## 剩余 15 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.*` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit/FetchBalance` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`HistoryWindow.SmartAction/View` · `PublishTemplateModal.Groups` · `SmartActionsView.Clock/Export` ·
`TaskView.Toggle` · `StoreGroupModal.Delete/IsEditing`

## 状态

```
完整套件   1536 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 15（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
