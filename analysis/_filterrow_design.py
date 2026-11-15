import io
p = r'D:\projects\cyber-reverse\replica\docs\CONTROL_DESIGN_FilterRow.md'
t = '''# 控件设计：SmartActions 的行家族（`FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry`，R316）

这四件在同一个命名空间，是**智能动作编辑器里的行**。一起设计，因为它们的成员互相咬合。

## 一、原版有什么（绑定表原文，全部 6+4+2+3 个成员）

| 类型 | 成员 |
|---|---|
| `SmartActions.FilterRow` | `Filter`, `Inputs`, `IsFirst`, `Passed`, `Title`, `ValueText` |
| `SmartActions.ActionRow` | `Action`, `IsFirst`, `Result`, `Tooltip` |
| `SmartActions.InputRow` | `Matched`, `Text` |
| `SmartActions.FilterInputEntry` | `Filter`, `Input`, `IsFirst` |

读得出的结构：

- **`FilterRow`** 持有一个 `Filter` 和它的 `Inputs`；`Passed` 是"这一条筛选是否通过"；
  `ValueText` 是值的显示文本；`IsFirst` 说明它知道自己是不是首行（首行没有分隔线/连接词）。
- **`ActionRow`** 持有一个 `Action`，`Result`（执行结果）与 `Tooltip`（结果说明）；同样有 `IsFirst`。
- **`InputRow`** 是 `{ Text }` + `Matched` —— 看起来是"输入提示/匹配列表的一行"。
- **`FilterInputEntry`** 是 `{ Filter, Input, IsFirst }` —— **筛选 × 输入**的配对项。

## 二、复刻件现状

`SmartActionsCreator` 里筛选是 `List<SmartActionFilter> _filters`，直接渲染成面板；
`SmartActionFilter` 已有 `Field/Operator/Value/Behaviour/Inputs`，`SmartActionFilterInput` 有 `Filter/Input`。
**没有行对象**：没有 `IsFirst`、没有 `Passed`、没有 `ValueText`、没有 `Result/Tooltip`。

## 三、要做的（数据 + 极薄渲染，不造像素）

```csharp
// src/Cybersole.Ui/Views/SmartActions/SmartActionRows.cs
public sealed class FilterRow
{
    public SmartActionFilter Filter { get; init; }
    public IReadOnlyList<FilterInputEntry> Inputs { get; init; }
    public bool IsFirst { get; init; }
    public string Title { get; }       // "Field Operator Value"，与 SmartActionFilter.ToString() 一致
    public string ValueText { get; }   // Filter.Value，空值显示 "(any)"
    public bool Passed { get; }        // 见判定规则
}

public sealed class FilterInputEntry
{
    public string Filter { get; init; }   // 所属筛选项名
    public string Input { get; init; }    // 该输入的当前值
    public bool IsFirst { get; init; }    // 是不是该筛选的第一条输入
}

public sealed class ActionRow
{
    public SmartActionStep Action { get; init; }
    public bool IsFirst { get; init; }
    public string Result { get; init; }   // 上次执行结果（默认空）
    public string Tooltip { get; init; }  // 结果说明（默认空）
}

public sealed class InputRow
{
    public string Text { get; init; }
    public bool Matched { get; init; }    // 是否命中当前输入
}
```

### `FilterRow.Passed` 的判定（可测）

`Filter.Passes(evt)` 已存在（`SmartActionFilter` 上），但它需要一个 `CheckoutEvent`。
行本身**不该持事件**，所以 `Passed` 是**由构造方传入**的判定结果：

```csharp
public FilterRow(SmartActionFilter filter, bool passed, bool isFirst, ...)
```

理由：行是渲染用的，判定属于引擎；把 `Passed` 传进来，行就永远可测且不依赖引擎运行。

## 四、接到哪里

`SmartActionsCreator` 已经有 `_filters`。新增：

```csharp
public IReadOnlyList<FilterRow> FilterRows { get; }     // 渲染用，IsFirst 由位置决定
public IReadOnlyList<ActionRow> ActionRows { get; }     // 同上，Result/Tooltip 默认空
```

`IsFirst` 由位置决定（`index == 0`）—— 这是可测的、也是成员名最直白的含义。

`InputRow` / `FilterInputEntry` 只做**类型 + 测试**，不接页面：目前没有证据说原版哪里显示"匹配列表"。

## 五、验收标准

1. `FilterRows.Count == _filters.Count`，且 `FilterRows[0].IsFirst == true`、其余 `false`；
2. `Title` 与 `Filter.ToString()` 相同；`Value` 为空时 `ValueText == "(any)"`；
3. `Passed` 原样传递（传 true 得 true）；
4. `Inputs` 与 `Filter.Inputs` 等长，`FilterInputEntry.IsFirst` 只在第一条为 true；
5. `ActionRows[0].IsFirst` 为 true，`Result`/`Tooltip` 默认空字符串；
6. `InputRow.Matched` 原样传递。

## 六、测试计划

`SmartActionRowTests`（6 条对应上面，纯逻辑）。**不开窗口。**

## 七、完成后的账本动作（预测 + 说明）

`FilterRow` 3 条（`IsFirst`/`Passed`/`ValueText`）+ `ActionRow` 2 条（`IsFirst`/`Tooltip`）
+ `InputRow` 1 条（`Matched`）+ `FilterInputEntry` 1 条（`IsFirst`）= **7 条**，
但 `FilterRow.Title`/`Inputs`、`ActionRow.Action`/`Result`、`InputRow.Text`、`FilterInputEntry.Filter`/`Input`
**本来就不在缺口清单里**，所以实测应为 **26 → 19**。

⚠ 落地后以 `python tools/backlog_report.py` 为准；如果数字不是 19，**先找差异再改 ceiling**。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('FilterRow design note written')
