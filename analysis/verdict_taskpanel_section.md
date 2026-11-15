### 第一次真的打开了「New Task」面板

之前 R20 只读过 `TaskEditorWindow` 的源码，没在真实 UI 里点开过。这轮用新窗口
（pid 57540 / window_id 2493528）点开 `Task Creator`，**读到了比源码更细的东西**。

### 原版面板的完整结构

它是 Tasks 页里的**内嵌面板**，不是独立窗口，有**三个 tab**：

**Setup**

```
Store            [Select store ▼]
Size             [Select sizes ▼]
Monitor Input    [Enter input]
Profiles         [Select profile ▼]
Proxies          [Select proxy group ▼]
Scheduled Start  [Set start time]
Quantity (per profile)  [1] [-] [+]
```

**Cart**

```
Monitor input  [1] [Enter input]        Quantity  [1] [-] [+]
Size           [Select sizes ▼]         [$]
               [Add Input                +]
```

Cart 支持**多行 input**（`Add Input` 加一行），所以一个任务可以监控多个商品。

**Advanced**

```
Monitor & Delays
  Monitor Mode   [Per Task ▼]
  Monitor  [1000] ms
  Retry    [1000] ms
  Timeout  [30]   sec
```

### 每个控件都有 id

UIA 树里读到了之前不知道的 id：

```
SetupRadioButton / CartRadioButton / AdvancedRadioButton
KeywordInput      （Monitor Input）
MinusButton / PlusButton
CreateButton
```

### 对照复刻版，发现三个缺口

| 原版 | 复刻版 |
|---|---|
| Scheduled Start | ❌ 缺 |
| Quantity (per profile) | ❌ 缺（**字段都没有**） |
| Monitor Mode | ❌ 缺（字段有，UI 没接） |

**`StartTime` 和 `MonitorMode` 在 `BotTask` 上早就有字段**（第 91、95 行），
只是 `TaskEditorWindow` 从来没渲染它们。**只有 `Quantity` 是连字段都不存在。**

### 补上了

**`BotTask`** 加一个字段：

```csharp
/// How many tasks to create per profile in the group.
/// The original labels this "Quantity (per profile)" and defaults it to 1.
public int Quantity { get; set; } = 1;
```

**`TaskEditorWindow`** 加三行 + 三个控件的读回：

```csharp
Row(11, "Scheduled start", _startTime);
Row(12, "Quantity (per profile)", _quantity);
Row(13, "Monitor mode", _monitorMode);
```

```csharp
task.Quantity = int.TryParse(_quantity.Text, out var qty) && qty > 0 ? qty : 1;
task.MonitorMode = _monitorMode.SelectedIndex == 1;

// blank means "start now"; unparseable is an error the user must fix rather than a silent
// fallback to now — a mistyped schedule that runs immediately is worse than one that refuses
task.StartTime = null;
if (!string.IsNullOrWhiteSpace(_startTime.Text))
{
    if (DateTime.TryParse(_startTime.Text, out var parsed)) ...
    else _error.Text = $"Scheduled start '{_startTime.Text}' is not a date — use yyyy-MM-dd HH:mm";
}
```

**`Monitor Mode` 的两选项**：原版是下拉（`Per Task` / …），模型里是 `bool`。
映射成 `Per Task` / `Per Site` 两选项，不发明第三种状态。

### 仍然没做的

| 项 | 为什么 |
|---|---|
| `Cart` tab 的多行 input | 需要 `BotTask` 支持一组 URL，不只是 `Product` 一个 |
| 三个 tab 的布局 | 当前是单页 Rows；改成 tab 是纯 UI 重构，不增加能力 |

**第一条是真缺口**（一个任务监控多商品），第二条只是排布。

### 验证

```
dotnet test (快速)   541 通过 / 0 失败 / 2 跳过
release build        成功
store modules        PASS 61 registered
verify.ps1           VERDICT: all checks passed
```

---
