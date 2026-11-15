import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 342 轮（`IWebhook` 补齐六成员；**发现缺口口径盲点**，新增 `tools/bind_scope.py`）。

---

## 两个缺口口径（都要看）

| 口径 | 工具 | 当前值 | 说明 |
|---|---|---|---|
| 名字级 | `tools/bind_diff.py` | **17** | 成员名在整个仓库里出现过即算满足 |
| **类型级** | `tools/bind_scope.py`（R342 新增） | **23 类** | 成员必须长在**该类型**上 |

`IWebhook` 缺 `Events/Type` 但名字级看不见 —— 因为 `TaskGroup` 等类型早就有这两个名字。

## 类型级缺口 top（已抽查为真）

| 类型 | 缺的成员 |
|---|---|
| `LoginControl` | `Cancel` `OpenBrowser` `SignIn` `SignUp` `UseCode` |
| `UserView` | `OpenUrl` |
| `CreateModel` | 17 个（`AccountGroup` `Group` `Input(s)` `IsEditing` `MonitorDelay` …） |
| `BotTask` | `Products` `Profile` `Properties` `ProxyGroup` `Status` `Task` |

**纪律**：`bind_scope.py` 是筛查器不是判决（块提取启发式，基类/partial 会误报），每条手工复核后再动手。

## 状态

```
完整套件   1505 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 23 类
mutation   29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
