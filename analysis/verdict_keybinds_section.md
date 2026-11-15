### `Keyboard Shortcuts`：26 个绑定，只有 1 个能工作

前面的页面查的是按钮。这一页要查的是**按键**，而按键不会在 UIA 树里留下痕迹——
只能按下去看会发生什么。

### 页面本身

```
Tasks      New task  Ctrl+G        Edit task  Ctrl+E      Clone  Ctrl+C
           Delete    Space         Start all  Z           Stop all  [
           Search    Ctrl+F
Proxies    Add  Ctrl+N   Test all  Ctrl+T   Copy  Ctrl+C
Billing    New profile  Ctrl+2   Clone  Ctrl+/   Delete  Space
```

三个按钮 `Enable shortcuts` / `Disable` / `Save` 都真的改 `s.Keybinds` 并保存。

**但 `Save` 没有可保存的东西**——这个页面所有值都是只读的 `TextBlock`。
「键盘快捷键」页不能改快捷键，`Save` 按钮就没有意义。

### 实测：按 F1 没反应

`settings.json` 里 `tasks.startAll = {"key": 90, "modifiers": 0}`。

**`90` 是什么？**

- Win32 虚拟键码 90 = `'Z'`
- **Avalonia `Key.F1` = 90**

按 F1 → 两个任务还是 `Idle`。
按 Z → **两个任务 `Idle` → `Monitoring`**。

**按 Z 启动了所有任务。**

### 两套编码混在一起

| 层 | 编码 | A | F1 | Delete | Right |
|---|---|---|---|---|---|
| `settings.json`（原版写的） | Avalonia `Key` | 44 | **90** | 32 | 25 |
| `KeyBindMatcher.VirtualKey` | Win32 VK | **65** | **112** | 32 | 39 |

`Matches` 比较 `bind.Key == virtualKey`，两套编码永远对不上。

**26 个绑定里只有两种能工作**：

1. **`Delete`（32）**——两个编码恰好相同
2. **`Z` 启动 `startAll`**——`'Z'` 的 Win32 值 90 恰好等于 `F1` 的 Avalonia 值 90

**第二种是纯粹的巧合，而且是有害的巧合**：用户按 Z 想输入文字，所有任务一起启动。

### 修：全部对齐到 Avalonia

`KeyBindMatcher` 重写：

```csharp
if (c is >= 'A' and <= 'Z') return 44 + (c - 'A');   // A = 44, Z = 69
if (c is >= '0' and <= '9') return 34 + (c - '0');   // D0 = 34, D9 = 43
…
if (upper[0] == 'F' && int.TryParse(upper[1..], out var fn) && fn is >= 1 and <= 24)
    return 90 + fn - 1;                               // F1 = 90, F24 = 113
```

**加了标点**——原版用 `[` 当 `stopAll`，而旧的 switch 里一个标点都没有：

```csharp
"[" => 147, "{" => 147,
"]" => 149, "}" => 149,
"." => 144, ">" => 144,
"-" => 143, "_" => 143,
…
```

**也认 Avalonia 自己的名字**（`OemOpenBrackets` / `OemCloseBrackets` / `OemPeriod` /
`OemMinus` / `OemPlus` / `OemComma` / `OemQuestion` / `OemPipe` / `OemQuotes` / `OemTilde` /
`OemSemicolon`），因为 `e.Key.ToString()` 返回的就是这些。

`Describe` 和 `Name` 同步改成 Avalonia 反查。

`GlobalSettings` 的默认值也重映射了 22 个数字——**默认值和 `settings.json` 现在一致**。

### 测试改成守不变式

旧的测试直接断言 Win32 值（`Assert.Equal(112, binds.StartAll.Key)`），
**它守着的是错的那套编码**。

新的测试守一个更强的东西——**每条默认绑定用「它自己的键名」喂回 `VirtualKey` 必须得到存储值**：

```csharp
Assert.Equal(binds.StartAll.Key, KeyBindMatcher.VirtualKey("F1"));
Assert.Equal(binds.New.Key, KeyBindMatcher.VirtualKey("G"));
Assert.Equal(binds.NextGroup.Key, KeyBindMatcher.VirtualKey("Right"));
```

**这正是旧表违反的不变式。**

还有一条专门钉住那个巧合：

```csharp
[Fact]
public void F1_And_Z_Are_Different_Keys()
{
    var startAll = new TaskKeyBinds().StartAll;

    Assert.True(KeyBindMatcher.Matches(startAll, KeyBindMatcher.VirtualKey("F1"), 0));
    Assert.False(KeyBindMatcher.Matches(startAll, KeyBindMatcher.VirtualKey("Z"), 0));
}
```

### 实测修复后

| 按键 | 结果 |
|---|---|
| `F1` | 两个任务 `Idle` → **`Monitoring`** ✅ |
| `F2` | `Monitoring` → **`Stopped`** ✅ |
| `Ctrl+G` | 打开 **`New task`** 窗口 ✅ |

`Ctrl+G` 还需要 `delivery_mode:"foreground"`——`hotkey` 走 `PostMessage` 时
`WM_KEYDOWN VK_CONTROL` **不更新 OS 级修饰键状态**，Avalonia 看不到 Ctrl 是按下的。
这是驱动层的限制，不是应用的 bug。

### `Save` 按钮仍然是空的

`KeyBindsView` 没有编辑控件，所以 `Save` 保存的是「什么都没改」。
**和 `Cloudflare Providers` 的「表单被忽略」不同——这里连表单都没有。**

改成把键位做成可编辑的输入框是一件独立的事（需要捕获按键、处理冲突、加 Reset），
不在这一轮。**但至少 `Save` 不再假装有东西可存**——`Enable shortcuts` / `Disable`
是真的写配置的，`Save` 现在也说明自己只是重写当前值。

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过   (+28，全是 KeyBindMatcherTests)
live contracts   PASS
store modules    PASS 61 registered
```

---
