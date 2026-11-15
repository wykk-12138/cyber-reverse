import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 318/319 轮：最后两件落地 —— 缺口 **19 → 17**，B 类"值得抽"的清零

### 一、`IWebhook`（R318）

```csharp
// src/Cybersole.Core/Webhooks/IWebhook.cs
public interface IWebhook { Dictionary<string, string> ExtraFields { get; } }
```

`Webhook`（`Models/Tasks.cs`）实现它。依据：绑定表有 `IWebhook.ExtraFields`，locale 有
`Settings.Webhook.ExtraFields` —— 概念不是编的。

**一处妥协要记**：原版命名空间是 `Cybersole.Webhook`，但它和本程序集里的 `Webhook` **类名冲突**（`CS0118`），
所以落在 `Cybersole.Core.Webhooks`。**类型名 `IWebhook` 保持不变**（账本按类型名计）。

### 二、`ElementCell`（R319）

```csharp
// src/Cybersole.Ui/Views/Tasks/ElementCell.cs
ElementCell(Name, Content, Column, ColumnSpan)
```

接进 `TaskGrid` 的表头：原来每个子控件手写 `Grid.SetColumn(x, n)`，现在先描述成 `ElementCell` 再统一放置。
依据：绑定表 `ElementCell` 的四个成员（`Column`/`ColumnSpan`/`Content`/`Name`）。

### 三、账本

```
bind_diff：missing 29 → real gap **17**
ceiling 17；账本标题「当前 17 = 0 可做 + 17 结构」
```

### 四、验证（含全套）

```
完整套件   1474 通过 / 0 失败 / 2 跳过（24 s）
UI 类      104 声明 / 31 不可达
```

（`SummaryBlockTests` 又红了一次 —— UI 类 103 → 104，改指南后转绿。这是新 UI 类的必然连带。）

### 五、这一轮的一句话

> 缺口从 **33（R262）→ 17**，其中 A 类清零、B 类"值得抽控件"的 7 件全部落地。

> 剩下的 17 条全是**已有等价物 / 不可得 / 内部状态** —— 它们不是"还没做"，是"已判定不必做"。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 319 轮（`IWebhook` + `ElementCell` 落地，缺口 **19 → 17**；B 类"值得抽"的 7 件全清）。

---

## 缺口 17：全部是"已判定不必做"

| 类 | 条数 |
|---|---|
| 已有等价物（R310 逐条核实过） | 12 |
| 不可得（`Platform` 三值 / `User.IsStaff` / `SettingsView.Transition`） | 3 |
| 内部状态或重复计数（`Filter.Variable` 等） | 2 |

**7 件"值得抽控件"全部完成**：`ComboBoxEdit`(R312)、`ProfileCsvRow`(R314)、
`FilterRow`/`ActionRow`/`InputRow`/`FilterInputEntry`(R317)、`IWebhook`(R318)、`ElementCell`(R319)。

## 验证状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R319，全套）
缺口       17（real = ceiling = 账本标题）
UI 类      104 声明 / 31 不可达
mutation   29 条 / 锚点 29/29（R307 后未再全量跑）
Commit     43.5 GB / 可用 4.95 GB   ← 低于硬线
```

## 下一步（要重启后）

1. 全量 `mutation-check`（29 条，约 15 分钟）；
2. 之后缺口/结构层面已收敛 —— 可转向**功能深度**（六条流的助手方法判定、`docs/ENDPOINT_LEDGER.md` 里 10 条真实发送但无出处的端点）。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
