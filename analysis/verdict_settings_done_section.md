### `Settings` 收官：`Need Help?` + `CHECK FOR UPDATES` + `Log Out`

`Settings` 的 15 个 section 加两个独立按钮，这一轮查完最后三个，`Settings` 全覆盖。

### `Need Help?`：三个按钮，全是「会打开」

```csharp
UiKit.Button("Open community", () => status.Text = "Opening " + CommunityUrl),
UiKit.Button("Open center",    () => status.Text = "Opening " + DocsUrl),
UiKit.Button("Search errors",  () => status.Text = "Search the error index for the code you saw in the log."),
```

**没有一行调用 `Process.Start`。**

### 而且 `DocsUrl` 本身就是错的

```csharp
public const string DocsUrl = "https://cybersole.io/api/apisecuretoken";
```

**那是取 API token 的端点，不是文档。** 「Open center」即使真的打开，也会打开一个裸 JSON 响应。

**修**：`https://cybersole.io/docs`，三个按钮都真的 `Process.Start`。

`Search errors` 没有错误索引可搜——**它打开日志目录**，因为错误码实际写在那里。这不是"降级实现"，
是承认「索引不存在，但你要找的东西在这儿」。

### `CHECK FOR UPDATES`：`UpdateRequested` 没有订阅者

```csharp
check.Click += (_, _) => UpdateRequested?.Invoke(this, EventArgs.Empty);
```

```csharp
public event EventHandler? UpdateRequested;   // 全仓库唯一的引用就是上面这行
```

**声明了、invoke 了、没人听。** 这比 `Status("...")` 更隐蔽——**代码看起来在做事件驱动的事**。

**修**：按钮自己完成检查，`UpdateRequested` 保留（给未来的宿主用），但不是唯一动作。

### 检查什么

这个构建没有远程更新源。**能诚实报告的是本地 Velopack 布局的内容**：

```csharp
var cached = Directory.Exists(packages) ? Directory.GetDirectories(packages).Length : 0;

status.Text = cached > 0
    ? $"Version {AppVersion.Current} — {cached} package(s) in the local cache; no remote feed "
      + "is configured, so there is nothing to compare against."
    : $"Version {AppVersion.Current} — source build, no update feed to ask.";
```

**第一版写的是 `packaged → "is current"`**，实测输出了 `Version 5.18.28 is current.`

**但 `AppPaths.LocalRoot` 是 `%LOCALAPPDATA%\Cybersole`，而那里有原版装的 `packages` 目录**——
判断依据是别人的文件。**"is current" 是句假话。**

改成报数 + 说明「没有远程源可比较」。

**实测**：

```
Version 5.18.28 — 1 package(s) in the local cache; no remote feed is configured,
so there is nothing to compare against.
```

**这句话是真的：缓存里有 1 个包（原版的），但没有源能说它是不是最新。**

### `Log Out`：一半是真的

```csharp
logout.Click += (_, _) =>
{
    _services.Auth.SignOut();                      // ✅ 真的退出
    LogoutRequested?.Invoke(this, EventArgs.Empty); // ❌ 没人订阅
};
```

**`Auth.SignOut()` 真的执行**，`LogoutRequested` 和 `UpdateRequested` 一样是空壳。
**但用户看到的效果是对的**（会话清掉了），所以它不算死按钮。

### 顺手把版本号收进一个常量

`"5.18.28"` 原来散在 5 个地方（三处备份快照、设置页标题、rail 显示）。新增：

```csharp
public static class AppVersion
{
    public const string Current = "5.18.28";
    public static Version Parsed => Version.TryParse(Current, out var v) ? v : new Version(5, 18, 28);
}
```

`HelpView` 的 Diagnostics 现在也显示版本和数据目录。

### 实测

| 操作 | 结果 |
|---|---|
| `CHECK FOR UPDATES` | **`Version 5.18.28 — 1 package(s) in the local cache; no remote feed is configured…`** ✅ |
| `Need Help?` → `Open center` | **`Opened https://cybersole.io/docs`** ✅ |

### `Settings` 15 个 section 的最终状态

| section | 死按钮 | 其它缺陷 |
|---|---|---|
| `General` / `Appearance` | 0 | — |
| `Notifications` | 0 | 标签重复（R109 修） |
| `Webhooks` | 1（R109 修） | — |
| `Email Accounts` | 2（R110 修） | — |
| `Google Accounts` | 0 | — |
| `PayPal Accounts` | 0 | — |
| `Data` | **6**（R117 修） | — |
| `Captcha Providers` | **4**（R113 修） | 保存不落盘（R113 修） |
| `Cloudflare Providers` | 1（R115 修） | 表单被忽略（R115 修） |
| `Keyboard Shortcuts` | 0 | **26 个绑定 25 个失效**（R116 修） |
| `Custom Stores` | 0 | — |
| `Custom Sizes` | 1（R111 修） | — |
| `Payment` | 2（R111 修） | — |
| `Need Help?` | **3**（R118 修） | `DocsUrl` 指错（R118 修） |
| `CHECK FOR UPDATES` | **1**（R118 修） | 事件无订阅者 |
| `Log Out` | 0 | 事件无订阅者（不影响效果） |

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
stray processes  0
```

---
