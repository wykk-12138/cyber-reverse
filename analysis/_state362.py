import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 362 轮：`TaskGroup` 两个 + `NotificationOptions.Name`（类型级缺口 23 → 21）

| 类型 | 成员 | 说明 |
|---|---|---|
| `TaskGroup` | `Running` | 派生属性（`Tasks.Count(t => t.IsRunning)`），不存储 |
| `TaskGroup` | `CloudflareSolverId` | 名字仍留在 `CloudflareSolver`，这个存的是设置列表的 id |
| `NotificationOptions` | `Name` | 这组选项属于哪个分类（Checkout / Decline / Captcha / Smart Actions / Other） |

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 23 → 21（起点 52，已降 60%）
```

### 这一轮的一句话

> `Running` 我写成**派生**而不是字段 —— 因为它必须永远等于"本组正在跑的任务数"，
> 存成字段就一定会和 `Tasks` 不同步。

> **能算出来的，就不要存。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 362 轮（`TaskGroup.Running`（派生）/`CloudflareSolverId`、`NotificationOptions.Name`；类型级缺口 21）。

---

## 类型级缺口：21（起点 52，已降 60%）

剩下的多是"需要 UI 位置"或"行为未知"的：
`CreateModel`(17) · `BotTask`(6) · `TaskView`(6) · `GroupSummary`(3) · `ProfileView`(3) ·
`ProfileCreatorView`(3) · 以及零散的 `ViewLogs` / `Clock` / `Export` / `ShowSitelist` 等。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 21（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
