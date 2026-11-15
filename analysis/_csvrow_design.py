import io
p = r'D:\projects\cyber-reverse\replica\docs\CONTROL_DESIGN_ProfileCsvRow.md'
t = '''# 控件设计：`ProfileCsvRow`（B 类第 2 件，R313 设计稿）

## 一、原版有什么（绑定表原文）

```
Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView  -> Apply, Close, ColumnChoices, GroupName, ProfileCount
Cybersole.Ui.Views.Profiles.Modals.ProfileCsvRow         -> FullySelected, Number, RowError, RowStatus
```

`ProfileCsvRow` 在同一命名空间下，是编辑器里的**行**对象；四个成员正好说清一行要带什么：

| 成员 | 说明 |
|---|---|
| `Number` | 行号（第几行 CSV）—— 报错时能指到具体行 |
| `FullySelected` | 这一行是否**所有列都映射到了**（列映射完成度） |
| `RowStatus` | 行的状态文本（如 "OK" / "Missing address 2"） |
| `RowError` | 行的错误（为空表示没错误） |

## 二、复刻件现状

`ProfileCsvEditorView` 已有：`ColumnChoices`、`ProfileCount`、`Parse(csv)`、`Apply`、`Close`、`GroupName`（R256 加的 `Parse` + 3 条测试）。
**没有行对象** —— 解析结果只是 `string[]` 的列表，没有行号、没有逐行状态/错误。

## 三、要做的（最小但可用）

```csharp
// src/Cybersole.Ui/Views/Profiles/Modals/ProfileCsvRow.cs
public sealed class ProfileCsvRow
{
    public int Number { get; init; }                       // 1-based
    public IReadOnlyList<string> Cells { get; init; }
    public IReadOnlyDictionary<string, int> ColumnMap { get; init; }   // 列名 -> 单元格下标

    public bool FullySelected { get; }                     // 每一列都有映射 且 该单元格非空
    public string RowStatus { get; }                        // "Ready" / "3 of 5 columns mapped"
    public string RowError { get; }                         // 空 = 无错误；否则指出第一处问题
}
```

判定规则（**可测、可解释**）：

- `FullySelected` = `ColumnMap` 里每个列名都能取到非空单元格；
- `RowError` 优先级：空行 → "Row is empty"；列数不符 → "Expected N columns, found M"；缺必需列 → "Missing <col>"；
- 否则 `RowError` 为空，`RowStatus` = `"Ready (N columns)"`。

## 四、接到哪里（这次有真实用处）

`ProfileCsvEditorView.ProfileCount` 现在返回"能解析出几条"。
把它旁边加一个 `Rows` 属性（`IReadOnlyList<ProfileCsvRow>`），
**编辑器可以在状态区显示"3 行就绪 / 1 行有问题（第 2 行：Missing address 2）"** ——
这是 `ProfileCount` 之外的信息，且是原版 `RowError`/`RowStatus` 的用途。

**注意**：`ProfileCsvEditorView` 是**已被构造的**视图（它在 `ProfileView.OpenCsvEditor` 里），
所以 `ProfileCsvRow` 一旦被 `Rows` 返回就不再是"未构造类型" —— baseline 不需要动。

## 五、验收标准

1. `Rows` 的行数 = `Parse` 的结果条数；
2. 每行 `Number` 从 1 递增；
3. 全列映射且非空 → `FullySelected == true` 且 `RowError` 为空；
4. 缺列 → `FullySelected == false` 且 `RowError` 含缺失列名；
5. 空行被跳过，但仍占 `Number`（或明确不留行 —— 二选一并写进测试）。

## 六、测试计划

`ProfileCsvRowTests`（5 条对应上面；纯逻辑，不开窗口）+ 在 `ProfileCsvEditorView` 上加
`Rows` 的 1 条（给一段 2 行 CSV，断言行数/状态）。

## 七、完成后的账本动作

- 绑定缺口 **29 → 25**（`ProfileCsvRow` 的 4 个成员全部关掉）；
- ⚠ 注意：`Number` 当前**不在**缺口清单里（复刻件的 `Step` 之类没有它），实现后实际只关掉
  `FullySelected` / `RowError` / `RowStatus` 三条 → **预测 29 → 26**，落地后以 `backlog_report.py` 实测为准。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('design note written')
