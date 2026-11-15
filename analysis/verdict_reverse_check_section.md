### 反向检查：有没有「控件改了但保存不读」的字段

R98 发现了「写的时候漏了」（`ExtraProducts` 加载时没回填）。这轮查反方向：
**某个输入框改了，`Save()` 不读它** —— 用户的修改静默消失。

### 方法

文本扫描，三个集合求差：

1. 所有能承载输入的字段（`TextBox` / `ComboBox` / `CheckBox` / `Slider` / …）
2. 所有「写回状态」的方法体（`Save*` / `Apply*` / `Submit*` / `Confirm*` / `Commit*` / `Persist*`）
3. 那些方法体里出现的 `xxx.Text` / `xxx.SelectedIndex` / `xxx.IsChecked` / `xxx.Value`

差集就是「声明了但没人读」的字段。

### 第一版扫描器全错

第一版只认 `Save*` / `Apply*` / `Persist*`，结果说：

```
Views\TaskEditorWindow.cs  —  13 input field(s), no Save/Apply method
Views\ProfileEditorWindow.cs — 15 input field(s), no Save/Apply method
```

**两个最重要的编辑器被判成「根本没有保存方法」。**

查源码：

```csharp
// TaskEditorWindow.cs:227
private void Submit(BotTask? existing)
```

**它叫 `Submit`，不叫 `Save`。** 名字集合补上 `Submit*` / `Confirm*` / `Commit*` 之后，
两个文件都从列表里消失了 —— 因为它们确实读了所有字段。

**这是「按命名约定推断」失败的经典案例**：约定是我想象的，代码不是。

### 第二版的结论

```
total fields never read by a Save/Apply method: 19
```

19 条里**没有一条是真的 bug**：

| 字段 | 为什么不是 bug |
|---|---|
| `TaskEditorWindow` 全部 13 个 | `Submit()` 全读 |
| `ProfileEditorWindow` 全部 15 个 | `Submit()` 全读 |
| `ProfileViews._list` / `_groups` / `_tasks` | 列表控件，不需要读回 |
| `SmartActionViews._rows` / `_search` / `_picker` | 同上 |
| `SmartActionEditorWindow._list` | 同上 |
| **`SignInWindow._authCode`** | **被 `ExchangeAsync()` 读，不在 `SubmitAsync()` 里** |

**最后一条是最后一个假阳性，也是最值得看的**：

```csharp
// SignInWindow.cs:100
private async Task ExchangeAsync()
{
    var code = _authCode.Text?.Trim();
    if (string.IsNullOrWhiteSpace(code))
    {
        _status.Text = "Paste the authorization code first.";
```

**两段式登录**：`SubmitAsync()` 拿邮箱密码换一个挑战，`ExchangeAsync()` 拿授权码换 token。
所以 `_authCode` 在两个方法之间流转，而扫描器只看一个方法体。

### 所以这一轮没有可修的东西

**这是好消息，不是白干**：

- R98 的 bug（`ExtraProducts` 不回填）是**真的**，已经修了
- 反方向的这一类**不存在**

**「查了一圈，没有」和「没查」是两种结论。** 前者让下一次可以跳过这项，
后者留下一个永远不确认的疑问。

### 扫描器留着当一个检查项

`analysis/find_unread_fields.py` 的价值不在现在，在将来：**每次给编辑器加字段时跑一遍**。

它会给假阳性（`ExchangeAsync` 那种），但**假阳性看一眼就排除，漏掉一个真 bug 要等用户报告**。

### 一个仍然存在的缺口

扫描只比较「字段名出现在方法体里」。它看不出：

```csharp
task.Sizes = _sizes.Text.Split(',');      // 读了
task.Sizes = new List<string>();          // 也"读了"（覆盖掉）
```

**语义层面的「读了但没用」需要人读代码。** 这轮只清掉了语法层面的那一类。

---
