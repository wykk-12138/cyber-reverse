# 控件设计：`ComboBoxEdit` 家族（B 类第 1 件，R311 设计稿）

## 一、原版有什么（绑定表原文）

| 类型 | 绑定成员 |
|---|---|
| `Cybersole.Ui.Controls.ComboBoxEdit` | `ClearSelectionCommand`, `RemoveTokenCommand` |
| `Cybersole.Ui.Controls.ComboBoxToken` | `Text` |
| `Cybersole.Ui.Controls.ComboBoxGroupHeader` | `Name` |

三个类型在同一个命名空间，说明这是一个**控件族**：可编辑下拉 + token 项 + 分组标题。

## 二、从名字能推出什么（以及不能）

| 成员 | 能推出 | 不能推出 |
|---|---|---|
| `RemoveTokenCommand` | 下拉里选中的值以 **token** 形式展示，且**可逐个移除** | token 的视觉形态（圆角块？带叉？） |
| `ClearSelectionCommand` | 有"一键清空全部已选" | 清空是否保留分组 |
| `ComboBoxToken.Text` | token 只显示一个文本 | 是否带 tooltip / 图标 |
| `ComboBoxGroupHeader.Name` | 选项可以**分组**，组有标题 | 分组是否可折叠 |

**结论**：这是一个"多选 + token 展示 + 分组 + 可清空"的下拉。复刻件现在只有单选的 `UiKit.Combo`（48 处使用）。

## 三、复刻件现状

`UiKit.Combo(items, selected, onChanged, width)` → 单个 `ComboBox`，**单选**。
没有多选、没有 token、没有分组标题。

## 四、要做的东西（最小但可用）

```csharp
// src/Cybersole.Ui/Views/Controls/ComboBoxEdit.cs
public sealed class ComboBoxEdit : UserControl
{
    // 1) 选项可以带分组
    public sealed class Option { public string Text; public string? Group; }
    public sealed class ComboBoxToken { public string Text; }      // 绑定名对齐
    public sealed class ComboBoxGroupHeader { public string Name; } // 绑定名对齐

    public IReadOnlyList<Option> Options { get; set; }
    public IReadOnlyList<string> Selected { get; }                  // 已选 token 的文本

    public void RemoveToken(string text);   // ← RemoveTokenCommand 的语义
    public void ClearSelection();           // ← ClearSelectionCommand 的语义
}
```

**UI 形态**（不猜原版像素，只做等价交互）：
- 顶部一行：已选 token（每个带一个 × 按钮）+ "Clear" 按钮；
- 下面一个下拉：按 `Group` 分组，组标题用 `ComboBoxGroupHeader`；
- 选中/移除后触发 `Changed` 事件。

## 五、放哪儿用（先找真实用处，不造摆设）

原版绑这两个命令的页面未知（绑定表只给类型，不给页面）。
所以**先不接到任何页面**，只做控件 + 测试；等有页面证据（locale 键或 GUI 观察）再接。

> 这与 R265 的纪律一致：**没有使用处的控件不要硬接到界面上充数。**

## 六、验收标准

1. `RemoveToken("x")` 后 `Selected` 不含 `"x"`，且 `Changed` 触发一次；
2. `ClearSelection()` 后 `Selected` 为空；
3. 分组渲染顺序 = `Options` 顺序，组内顺序保持；
4. 空 `Options` 不崩、下拉为空；
5. 重复文本的 token 只移除第一个（可测）。

## 七、测试计划

`ComboBoxEditTests`（5 条，对应上面 5 条验收）—— 全部是纯逻辑，不需要开窗口。

## 八、完成后的账本动作

- 绑定缺口 **31 → 29**（`ClearSelectionCommand` + `RemoveTokenCommand` 两条关掉；`ComboBoxToken.Text` / `ComboBoxGroupHeader.Name` 随之有了宿主类型）；
- 运行 `python tools/backlog_report.py` 确认数字，再改 `MaxRealGap` 与账本标题（**先测后设**）。
