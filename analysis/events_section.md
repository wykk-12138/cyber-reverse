### `CHECK FOR UPDATES` 不是死按钮——但它的两个事件从来没人在听

R178 发现 `cdn.cybersole.io/releases/` 全 404。R179 去看 replica 的更新入口。

### 按钮是真的

```csharp
var check = new Button { Content = "CHECK FOR UPDATES", … };

// Round 118: this only raised UpdateRequested, and nothing ever subscribed, so the button
// did nothing at all. Now it performs the check itself and reports a result either way.
check.Click += async (_, _) =>
{
    var packages = Path.Combine(AppPaths.LocalRoot, "packages");
    var cached = Directory.Exists(packages) ? Directory.GetDirectories(packages).Length : 0;
    status.Text = cached > 0 ? $"…{cached} package(s) in the local cache…" : $"…source build…";
};
```

**它读真实的本地 Velopack 目录并写状态栏。所以它不在 `DeadButtonTests` 的 `Known` 列表里——那是对的。**

**R178 之后那段措辞可以更准了**：注释说「this build 没有 remote feed」，但**原版的 feed 也 404 了**。改成：

```csharp
// There is no remote feed for either build.
// R178 measured it: the original's FeedUrl points at https://cdn.cybersole.io/releases/, and
// every Velopack path under it answers 404. … So this is not "the replica cannot check for
// updates while the original can". Neither can.
```

### 但那行 `UpdateRequested?.Invoke` 还在

```csharp
public event EventHandler? UpdateRequested;
public event EventHandler? LogoutRequested;
```

**全仓库 `+=` 数量：0。**

**R118 修的是「按钮什么都不做」——按钮现在做了。那两个事件是修复前的形状，被留在原地。**

### 写一个通用检查

`UnsubscribedEventsTests`：扫 `src/`，找「声明了、raise 了、但没有任何 `+=`」的事件。

第一次跑，**8 个**：

```
ClockService.Ticked              raise=1 subscribe=0
Primitives.CanExecuteChanged ×2  raise=1 subscribe=0
ConfigurationStore.Saved         raise=1 subscribe=0
AuthService.SignedIn             raise=1 subscribe=0
AuthService.SignedOut            raise=1 subscribe=0
SettingsShell.UpdateRequested    raise=1 subscribe=0
SettingsShell.LogoutRequested    raise=1 subscribe=0
```

**两类要分开**：

| 类别 | 处理 | 理由 |
|---|---|---|
| `CanExecuteChanged` | 白名单 | **`ICommand` 契约**，框架订阅，不是本仓库 |
| `Ticked` / `Saved` / `SignedIn` / `SignedOut` | 白名单 | **服务层扩展点**，主输出是属性（`ClockService.Current`），删了就没有通知途径 |
| `UpdateRequested` / `LogoutRequested` | **删掉** | UI 内部残留，按钮已经直接做事 |

**白名单带理由，不是带名字。**

### 顺带删掉一个装饰性测试

`SettingsShellTests.LogoutAndUpdateAreWired`：

```csharp
var fired = 0;
shell.LogoutRequested += (_, _) => fired++;
shell.UpdateRequested += (_, _) => fired++;

// both events must exist; firing them is the window's job, not the shell's
Assert.Equal(0, fired);
```

**它订阅、从不触发、断言计数器仍是 0——对任何实现都通过，包括事件什么都不做的实现。**

**而且那两行 `+=` 是全仓库仅有的订阅**，所以 `UnsubscribedEventsTests`（只扫 `src/`，这是对的）没报它们：
**从任何扫全树的检查看，这两个事件都「有人在听」。**

换成一条真能失败的：

```csharp
[Fact]
public void DisplayVersionMatchesTheAssemblyVersion()
{
    var info = typeof(SettingsShell).Assembly.GetName().Version;
    Assert.StartsWith($"{info!.Major}.{info.Minor}.{info.Build}", SettingsShell.DisplayVersion,
        StringComparison.Ordinal);
}
```

### 变异 21 → 22

```
round 179 -- an event is declared, raised, and never subscribed
    → 在 SettingsShell 里加 `public event EventHandler? ProbeEvent;` 和一个 raise
    → UnsubscribedEventsTests 报 red
```

### 这一轮的形状

```
R118   修了「按钮什么都不做」          → 按钮做事了
R118   留下了两个「按钮做过什么」的事件  → 没人听
R179   一个通用检查看见它们            → 删掉
```

> **修一个缺陷时最容易留下的，是它原来的形状。** 那个形状现在什么都不做，但它存在，
> 所以下一个读代码的人会为它留出预算。

**`DeadButtonTests` 管「按钮」，`UnsubscribedEventsTests` 管「事件」——同一条规则的两种形态。**

### 验证

```
raised-but-unsubscribed events: 0
dotnet test（快）      653 通过 / 0 失败 / 2 跳过
verify.ps1 -Full      PASS
  mutation guards       22 fired, 0 decorative, 0 did-not-compile, 0 skipped
```

---
