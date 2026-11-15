### `Solver` / `Sign in`：三个缺陷，其中一个是老熟人

### `Solver`：七个开关全部不落盘

窗口看起来完整：挑战队列、手动解算表单、七个 `Toggle`。

```csharp
private readonly SolverSettings _settings = new();   // ← 一个全新的对象
```

```csharp
void Toggle(string label, bool initial, Action<bool> setter)
{
    var cb = new CheckBox { Content = label, IsChecked = initial };
    cb.IsCheckedChanged += (_, _) =>
    {
        setter(cb.IsChecked ?? false);
        _services.Config.Save();          // solver toggles live in settings.json
    };
```

**`_settings` 是窗口自己的临时对象，从来没被写进 `Config.Solvers`。**

**`setter` 改的是 `_settings`，`Save()` 保存的是 `Config.Solvers`——两份不同的数据。**

**实测**：点 `Question sharing`（true → false），重启读 `solvers.json`：

```json
"questionSharing": true     ← 没变
```

**这是 R113 `Captcha Providers` 那个 bug 的完全重演。** 同一个形状：**改 A，保存 B，A 和 B 没有连线。**

**修**：让 `_settings` 指向配置里的那个对象。

```csharp
public static SolverSettings SettingsOf(AppServices services)
{
    var view = services.Config.Solvers.FirstOrDefault();
    if (view is null) { view = new SolverView(); services.Config.Solvers.Add(view); }
    if (view.Solvers.Count == 0)
        view.Solvers.Add(new Solver { Settings = new SolverSettings() });
    return view.Solvers[0].Settings;
}

public SolverWindow(AppServices services)
{
    _services = services;
    _settings = SettingsOf(services);    // ← 配置里的那个
```

**实测**：

```json
"questionSharing": false    ← 落盘了
```

### 顺带修的两处

**`Bus.Logged` 跨线程写 `_queue`**（和 R121 同一类）：

```csharp
// 之前
_services.Bus.Logged += (_, e) =>
{
    if (e.Source is "Captcha" or "Solver") _queue.Items.Add(e.Message);
};

// 之后
_services.Bus.Logged += (_, e) =>
{
    if (e.Source is not ("Captcha" or "Solver")) return;
    Avalonia.Threading.Dispatcher.UIThread.Post(() => _queue.Items.Add(e.Message));
};
```

**`SolveAsync` 没有 try/catch**：它由 `async void` 事件处理器调用，任何异常都会终止进程。加了。

### `Sign in`：catch 的消息被覆盖

```csharp
openBrowser.Click += (_, _) =>
{
    var url = _services.Auth.BuildOAuthUrl();
    try { Process.Start(new ProcessStartInfo(url) { UseShellExecute = true }); }
    catch (Exception ex) { _status.Text = $"cannot open browser: {ex.Message}"; }
    _status.Text = "browser opened — paste the authorization code below";   // ← 无条件覆盖
};
```

**浏览器打不开时，用户看到的是「browser opened」。**

这是 R103 那个 `_status.Text = "Starting all tasks."` 覆盖调试输出的同一形状——**状态栏是一个变量，后写的赢，而「成功消息」写在了 try 外面。**

**修**：成功消息搬进 try。

### 三个缺陷的分类

| 缺陷 | 类型 | 首次出现 |
|---|---|---|
| `_settings = new()` 不落盘 | **改 A 保存 B** | R113 `Captcha Providers` |
| `Bus.Logged` 跨线程 | **线程违规** | R121 `Monitor` |
| 状态消息覆盖 | **后写赢** | R103 `Tasks` |

**三个都是「已经见过并修过」的类型，在别的文件里原样重演。**

> **修一个 bug 不等于修掉一个 bug 类。** 除非有一个能在全库找到同类的检查，否则第 N 次出现时还是新 bug。

`ConfigureAwait` 那类有办法查（grep `.Async` 后面没有 `ConfigureAwait`）。**「改 A 保存 B」没有**——它需要知道哪些对象是被序列化的，而那是运行时的知识。

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
solvers.json     questionSharing 已恢复 true
```

---
