### `Keyboard Shortcuts` 后半程：26 个 `TextBlock` 换成 26 个捕获按钮

R116 修好了按键编码，但那一页**根本不能改键**：

```csharp
rows.Add(UiKit.Row(label, new TextBlock
{
    Text = Core.Input.KeyBindMatcher.Describe(bind),
    VerticalAlignment = VerticalAlignment.Center,
}));
```

**26 行全是只读显示。`Save` 按钮因此没有可存的东西。**

这不是假实现——**是结构缺失**。原版这一页每个键位都能点、能按、能改。

### 改成捕获按钮

```csharp
var capture = new Button
{
    Content = Cybersole.Core.Input.KeyBindMatcher.Describe(bind),
    MinWidth = 120,
};

capture.Click += (_, _) =>
{
    if (capturing?.Bind == bind) { EndCapture("Capture cancelled."); return; }

    EndCapture(null);
    capturing = (capture, bind, page, label);
    capture.Content = "Press a key…";
    capture.Focus();
    status.Text = $"Listening for {page} · {label}. Esc cancels.";
};
```

**`bind` 是 `Config.Settings.KeyBinds.Tasks.New` 这个对象本身**——改它的 `Key` 就是改配置，
不需要额外的映射表。

### 一个页面级 handler，不是每行一个

```csharp
AddHandler(KeyDownEvent, (_, e) =>
{
    if (capturing is not { } c) return;
    e.Handled = true;

    if (e.Key == Avalonia.Input.Key.Escape) { EndCapture("Capture cancelled."); return; }

    var code = KeyBindMatcher.VirtualKey(e.Key.ToString());
    if (code == 0) { status.Text = $"{e.Key} cannot be used as a shortcut."; return; }

    var mods = KeyBindMatcher.Modifiers(
        e.KeyModifiers.HasFlag(KeyModifiers.Alt),
        e.KeyModifiers.HasFlag(KeyModifiers.Control),
        e.KeyModifiers.HasFlag(KeyModifiers.Shift));
    …
}, RoutingStrategies.Tunnel);
```

**`Tunnel` 而不是 `Bubble`**：隧道阶段先于子控件，否则焦点所在的按钮会先把按键吃掉
（`Space` 会「按下」按钮，`Enter` 会激活它）。

### 冲突检测

```csharp
var clash = AllOnPage(s, c.Page)
    .FirstOrDefault(o => o.Bind != c.Bind
                         && o.Bind.Key == code
                         && o.Bind.Modifiers == mods);

if (clash.Bind is not null)
{
    status.Text = $"{KeyBindMatcher.Describe(clash.Bind)} is already {clash.Label} on this page.";
    return;
}
```

**同页冲突会导致其中一条永远不可达**——`MainWindow` 的 handler 是
`if / else if / else if` 顺序匹配，先声明的赢。

**跨页不检测**：`Ctrl+G` 在 Tasks 和 Proxies 都是「新建」，这是原版的设计，
因为两页的 handler 有 `TabIndex` 守卫。

### `Reset to defaults`

```csharp
var fresh = new Cybersole.Core.Settings.KeyBindSet();
Copy(fresh.Tasks, s.KeyBinds.Tasks);
Copy(fresh.Proxies, s.KeyBinds.Proxies);
Copy(fresh.Billing, s.KeyBinds.Billing);
```

**新建一个 `KeyBindSet` 就是默认值**，逐字段 `Copy` 回活动配置。
`Rebuild()` 遍历 `pairs` 重绘 26 个按钮的文字。

### 实测

| 步骤 | 结果 |
|---|---|
| 点 `F1` 按钮 | `Listening for Tasks · Start all. Esc cancels.` ✅ |
| 按 `F9` | 按钮文字变 **`F9`**，状态 `Tasks · Start all is now F9. Press Save to keep it.` ✅ |
| 点 `F2` 按钮再按 `F9` | **`F9 is already Start all on this page.`** ✅ 拒绝 |
| 点 `Save` | `Saved.` ✅ |
| 重启后读 `settings.json` | `startAll = {"key": 98}`（**F9**）✅ |
| 同一次保存里 `stopAll` | `{"key": 91}`（**F2**，没被冲突覆盖）✅ |

**`98 - 90 + 1 = 9`，`98` 就是 `F9`。** 键位真的改了、真的存了、冲突真的挡住了。

### 这一页的三种「假」都出现过

| 轮次 | 问题 | 类型 |
|---|---|---|
| R116 | 26 个绑定 25 个失效 | **编码不匹配**（读了却对不上） |
| R118 | `Save` 保存的是「什么都没改」 | **无对象可存** |
| R119 | 26 行只读 | **结构缺失**（根本没建） |

**同一个页面，三轮，三种完全不同的缺陷。** 前两轮修完它「能显示对的键位」「能存对的值」，
但它**仍然不能改键**——**因为改键这件事从来就没人写。**

> **「显示正确」和「可以修改」是两件独立的事，而前者会让人以为后者也在。**

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
settings.json    startAll 已恢复为 F1 (90)
```

---
