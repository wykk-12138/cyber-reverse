import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 364 轮：`BotTask` 五成员（类型级缺口 20 → 19）

| 成员 | 类型 / 说明 |
|---|---|
| `Products` | 派生（`AllProducts`），已有 `Product` + `ExtraProducts` 的合并视图 |
| `Profile` / `ProxyGroup` | 导航属性（此前只有 `ProfileId` / `ProxyGroupId`） |
| `Properties` | `Dictionary<string,string>` |
| `Status` | 单行状态文本 |

**故意留白**：`Task` —— 类型不可推断（可能是引擎句柄/接口/字符串 id），且名字与
`System.Threading.Tasks.Task` 冲突。已记进 backlog。

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 20 → 19
```

### 这一轮的一句话

> `Products` 我又是写成**派生**（`AllProducts` 已有合并逻辑），没有新造一个列表 ——
> 三份"产品列表"是这一程最常见的重复来源。

> **已经有合并逻辑的地方，只暴露它，不要再存一份。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| `CreateModel` | `Input` `Inputs` | **类型不可推断**（字符串？商品选项？列表？），只记名 |',
                '| `CreateModel` | `Input` `Inputs` | **类型不可推断**（字符串？商品选项？列表？），只记名 |\n| `BotTask` | `Task` | **类型不可推断**，且与 `System.Threading.Tasks.Task` 同名 |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('backlog updated')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 364 轮（`BotTask` 五成员；类型级缺口 19）。

---

## 类型级缺口：19（起点 52）

剩下主要是界面动作：`TaskView`(6) · `GroupSummary`(3) · `ProfileView`(3) · `ProfileCreatorView`(3) ·
`DataView.ViewLogs` · `SmartActionsView.Clock/Export` · `ReleaseView.ShowSitelist` · `ImapView.Configure` 等。

**留白清单**（类型不可推断）：`CreateModel.Input/Inputs`、`BotTask.Task`。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 19（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
