### 用 CUA 操作复刻版自己，抓到三个死按钮

前几轮的工作模式是「用 CUA 读原版」。这轮反过来：**用 CUA 操作复刻版自己**。

### 启动

```
Cybersole.Ui.exe (Release)  →  pid 63904 / window_id 266508
标题：Cybersole 5.18.28 — functional replica
```

### 第一个发现：`New` 是死按钮

点 `New`，状态栏显示：

```
Open the task creator to add a task.
```

**没有窗口打开。**

### 第二个发现：`Creator` 也是死的

点 `Creator`，状态栏显示：

```
Task creator opened.
```

**说"打开了"，但什么都没打开。**

### 源码里三个按钮全是 `Status(...)`

```csharp
TasksViews.cs:594: UiKit.Button("New", () => Status("Open the task creator to add a task.")),
TasksViews.cs:595: UiKit.Button("Creator", () => Status("Task creator opened.")),
TasksViews.cs:596: UiKit.Button("Editor", () => Status("Select a task to edit.")),
```

**三个按钮只设置一行文字。`TaskEditorWindow` 从来没被这个 view 调用过。**

### 这是「假功能」的教科书案例

- 按钮存在 ✅
- 有文字标签 ✅
- 点击有反应 ✅（状态栏变了）
- **什么都不做** ❌

**截图上看不出来。** 只有真的点下去、然后检查"应该发生的事发生了没有"，才能发现。

**这和那九次平台误判是同一个模式**：发了请求、收到了响应、什么都没发生。

### 修了

```csharp
UiKit.Button("New", () => OpenEditor(null)),
UiKit.Button("Creator", () => OpenEditor(null)),
UiKit.Button("Editor", () =>
{
    var picked = SelectedTask();
    if (picked is null) Status("Select a task to edit.");
    else OpenEditor(picked);
}),
```

```csharp
private void OpenEditor(BotTask? existing)
{
    var owner = TopLevel.GetTopLevel(this) as Window;
    if (owner is null) { Status("No owner window — cannot open the editor."); return; }

    var editor = new TaskEditorWindow(_services, existing);
    editor.Closed += (_, _) => { _services.Config.Save(); Refresh(); };

    _ = editor.ShowDialog(owner);
    Status(existing is null ? "Task creator opened." : $"Editing {existing.Name}.");
}
```

顺带补了 `SelectedTask()`——`Editor` 需要知道列表里选中了哪个。

### 然后真的走了一遍完整流程

重新编译、重启，点 `Tasks` → `Creator`：

**窗口打开了，15 个字段全在**：

```
Name / Product URL / More products [+ Add product] / Store [Shopify ▼]
Sizes / Quick sizes [4][4.5][5]…[14] / Proxy group [Group 1 ▼]
Profile / Account / Monitor delay [2500] / Retry delay [2500] / Timeout [10]
Scheduled start / Quantity (per profile) [1] / Monitor mode [Per Task ▼]
Cancel / Create
```

### 点 `+ Add product`

树里多了一对：

```
[7] Button "×"        ← 删除这一行
[8] Edit              ← 新 URL 输入框
```

### 填数据、点 Create

```
[21] ListItem "multi-product test  [shopify]  Idle  https://example.com/p/primary"
   ↑ 注意末尾只显示主 URL
```

### 落盘验证

`%APPDATA%\Cybersole\tasks.json`：

```json
{
  "name": "multi-product test",
  "store": "shopify",
  "product": { "url": "https://example.com/p/primary", "sizes": ["9", "10"] },
  "monitorDelay": 2500, "retryDelay": 2500, "timeout": 10,
  "monitorMode": false,
  "quantity": 1,
  "extraProducts": [
    { "url": "https://example.com/p/extra-one", "sizes": ["9", "10"] }
  ]
}
```

**`extraProducts` 落盘了，`sizes` 正确继承（`["9", "10"]`）。**

**这是第一条被端到端验证过的 UI → 引擎 → 磁盘链路。**

### 顺带抓到一个间歇性失败

改完重跑测试，第一次 `失败 1，通过 544`，第二次 `失败 0，通过 545`。

**同一个命令，同样的代码，两次结果不同。**

这正是 R93 那轮怀疑过、但因为三次都稳定失败而没能证明的现象。**现在有了一个实例，但没有定位到是哪个测试。**

### 验证

```
dotnet test     第一次 544/545（1 个间歇性失败），第二次 545/545
store modules   PASS 61 registered
verify.ps1      VERDICT: all checks passed
tasks.json      extraProducts 已落盘，sizes 继承正确
```

---
