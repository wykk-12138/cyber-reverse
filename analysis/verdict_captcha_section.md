### `Captcha Providers`：四个死按钮 + 一个保存不落盘

`CaptchaProvidersView` 有 5 个按钮，只有 `Fetch balance` 是真的。

### 四个死按钮

```csharp
UiKit.Button("Up",   () => status.Text = "Priority raised."),
UiKit.Button("Down", () => status.Text = "Priority lowered."),
UiKit.Button("Add",  () => status.Text = "Provider added (set an API key to enable it)."),
UiKit.Button("Edit", () => status.Text = "Edit the selected provider."),
```

**`Up`/`Down` 最严重**：priority 决定解算器先用哪个 provider。声称改了而没改，
就是「两个 provider」和「一个 provider」的区别。

### 顺带发现：列表索引是错的

```csharp
_configs.AddRange(registry.Configs.Select(c => $"{c.Name} ({c.Type}) ..."));
enabled.ItemsSource = _configs.Where((_, i) => registry.Configs[i].Enabled).ToList();
```

**`_configs` 是格式化后的字符串，`Where` 的索引 `i` 是 `_configs` 的下标，
却拿去索引 `registry.Configs`** —— 只有当 enabled/disabled 的分布恰好对齐时才不出错。

**改成直接持有配置对象**：

```csharp
private readonly List<CaptchaProviderConfig> _enabled = new();
private readonly List<CaptchaProviderConfig> _disabled = new();
```

### 真的实现了 `Up` / `Down`

```csharp
void Move(int delta)
{
    var i = enabledList.SelectedIndex;
    if (i < 0 || i >= _enabled.Count) { status.Text = "Select an enabled provider first."; return; }

    var target = _enabled[i];
    var ordered = registry.Configs.Where(c => c.Enabled).OrderByDescending(c => c.Priority).ToList();
    var at = ordered.IndexOf(target);
    var swapWith = at + delta;
    if (swapWith < 0 || swapWith >= ordered.Count)
    {
        status.Text = delta < 0 ? "Already highest priority." : "Already lowest priority.";
        return;
    }

    // swap the two priorities rather than renumbering everything, so the numbers stay
    // meaningful to a user who set them by hand
    (ordered[at].Priority, ordered[swapWith].Priority) =
        (ordered[swapWith].Priority, ordered[at].Priority);
    …
}
```

**实测**：只有一个 enabled 时点 `Up` → `Already highest priority.`（正确）。

### 真的实现了 `Add`（同时也是 `Edit` 的保存）

表单是这个页面唯一的编辑器，所以 `Add` 兼作 Save：

```csharp
void AddProvider()
{
    var type = typeCombo.SelectedItem as string ?? registry.Drivers.FirstOrDefault()?.Type;
    var existing = registry.Configs.FirstOrDefault(c => c.Type.Equals(type, OrdinalIgnoreCase));

    if (existing is not null)
    {
        if (!string.IsNullOrWhiteSpace(name)) existing.Name = name;
        if (keyBox.Text is { Length: > 0 }) existing.ApiKey = keyBox.Text;
        if (int.TryParse(concurrency.Text, out var cc) && cc > 0) existing.Concurrency = cc;
        existing.Enabled = existing.ApiKey is { Length: > 0 };
        …
    }
    …
}
```

`Edit` 则把选中项填回表单：

```csharp
typeCombo.SelectedItem = picked.Type;
nameBox.Text = picked.Name;
concurrency.Text = picked.Concurrency.ToString();
keyBox.Focus();
```

### 但改完之后发现：**保存根本没落盘**

点 `Add`，UI 显示 provider 进了 Enabled 列表。**重启后消失了。**

查 `solvers.json`、`settings.json` —— **没有任何 provider 记录**。

原因：

```csharp
// CaptchaProviderRegistry —— 纯内存容器
private readonly List<CaptchaProviderConfig> _configs = new();
```

**它没有任何持久化方法。** 而 `GlobalSettings.CaptchaProviders` 才是写进 `settings.json` 的字段。

**视图调 `services.Config.Save()` 保存的是 settings 里已有的内容，和 registry 无关。**

### 第二层原因：持久化模型缺三个字段

```csharp
public sealed class CaptchaProvider
{
    public string Id / Name / Type / ApiKey; public double Balance;
    // 没有 Priority，没有 Enabled，没有 Concurrency
}
```

**即使想同步也没地方放。**

**修**：

```csharp
public int Priority { get; set; }
public bool Enabled { get; set; }
public int Concurrency { get; set; } = 10;
```

**加一个 `Sync()`**：

```csharp
void Sync()
{
    services.Config.Settings.CaptchaProviders = registry.Configs
        .Select(c => new CaptchaProvider
        {
            Name = c.Name, Type = c.Type, ApiKey = c.ApiKey,
            Balance = (double)(c.Balance ?? 0),
            Priority = c.Priority, Enabled = c.Enabled, Concurrency = c.Concurrency,
        })
        .ToList();
    services.Config.Save();
}
```

**然后 `AddProvider` / `Move` / `Fetch balance` 调 `Sync()` 而不是 `Config.Save()`。**

### 批量替换时踩了自己的坑

用 `replace('services.Config.Save();', 'Sync();')` 一次改了 16 处——**包括 `Sync()` 内部的
`Save()`**（会无限递归），**以及 `ProviderViews.cs` 里其它 5 个 view 的 `Save()`**
（那些 view 里没有 `Sync`）。

编译报了 6 个 `当前上下文中不存在名称"Sync"`。

**修**：按 `CaptchaProvidersView` 的行号范围（18–240）把范围外的 12 处改回去。

### 验证落盘

```json
captchaProviders: 11
  {'name': 'Persisted Solver', 'type': 'humanpresence', 'priority': 0,
   'enabled': True, 'concurrency': 10, 'apiKey': 'key-persist'}
  {'name': 'Uncaptcha', 'enabled': False, ...}
  {'name': 'Parallax Systems', ...}
  …
```

**11 个 driver 全部落盘，启用状态和 key 都在。**

### 验证

```
dotnet test      551 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
settings.json    11 provider rows persisted
```

---
