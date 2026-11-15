import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 363 轮：`CreateModel` 从 6 个成员补到 20 个（类型级缺口 21 → 20）

### 一、补的都是"数据"，不碰"行为"

| 补的 | 依据 |
|---|---|
| `Group` / `AccountGroup` / `Profile` / `Profiles` / `ProxyGroup` | 表单的选择项 |
| `Quantity` / `MonitorDelay` / `RetryDelay` / `Timeout` / `MonitorMode` / `StartTime` / `Store` | 与 `BotTask` 同名同型 |
| `Tasks`（列表） | 表单产出的任务 |
| `Total` | **派生**（`Tasks.Count`），不存 |
| `IsEditing` | 编辑态标志 |

### 二、故意没补的两个

`Input` / `Inputs`：**类型不可推断** —— 可能是字符串、也可能是商品选项对象或它们的列表。
按三档规则，这属于"行为未知"，只记名。

### 三、验证

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 21 → 20
```

### 四、这一轮的一句话

> 17 个成员里我补了 15 个、留了 2 个 —— **留的那两个，是唯一可能"补错"的两个。**

> **一次补齐 15 个只用了 20 行；判断哪 2 个不该补，用了更多思考。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| `PublishTemplateModal` | `Groups` | — |',
                '| `PublishTemplateModal` | `Groups` | — |\n| `CreateModel` | `Input` `Inputs` | **类型不可推断**（字符串？商品选项？列表？），只记名 |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('backlog updated')
