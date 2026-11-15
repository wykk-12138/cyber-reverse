### 第 100 轮：把死按钮这一类清干净

R97 和 R99 各发现一批「按钮只写状态文本」。这轮不一个个找了，**扫整个 `Cybersole.Ui`**。

### 扫描结果

23 处，分布在三个 view：

| 文件 | 数量 | 例子 |
|---|---|---|
| `AnalyticsViews.cs` | 10 | `Previous` / `Next` / `Close` / `Show guide` / `Show site list` / `Open tracking` |
| `ProfileViews.cs` | 7 | `Open creator` / `Open CSV editor` / `Create group` / `Create test` / `Open settings` / `Close` ×2 |
| `SmartActionViews.cs` | 6 | `Edit` / `Publish` / `From scratch` / `From template` / `Blank` |

### 修了 7 个

| 按钮 | 修成 |
|---|---|
| `ProfileViews:Open creator` | 打开 `ProfileEditorWindow` |
| `ProfileViews:Create test` | 真的加一个 profile |
| `SmartActionViews:Edit` | 打开 `SmartActionEditorWindow` |
| `ProfileViews:Close` ×2 | `(TopLevel.GetTopLevel(this) as Window)?.Close()` |
| `TasksViews:Clone` | 深拷贝（R99） |
| `TasksViews:Create tasks` | 文案改成指向真的控件 |

### 剩下的 15 个都归了类

| 类 | 数量 | 理由 |
|---|---|---|
| 目标窗口不存在 | 2 | `Open CSV editor` / `Create group` |
| 静态页，没有下一页 | 7 | Analytics 的 `Previous`/`Next`/`Close`/`Show guide`/… |
| 行为诚实但标签夸大 | 1 | `Show` 是把选中项写进状态栏，不打开详情面板 |
| Settings 是 tab 不是窗口 | 1 | `Open settings` |
| 编辑器存在但没传 action | 4 | SmartActions 的 `Publish`/`From scratch`/… |

### 固化成测试

`DeadButtonTests` 两个断言：

```csharp
NoNewStatusOnlyButtonsAppear()   // 新出现的 status-only 按钮让构建失败
EveryKnownEntryStillExists()     // 白名单里过期的条目也让构建失败
```

输出：

```
status-only buttons: 15 (known: 15)
live: 15, known: 15
```

**第二个断言和第一个一样重要。** 只检查「没有新的」会让白名单慢慢腐烂——
条目指向的按钮改了名、删了、或者被真的实现了，列表里还留着，于是下一次真的新增一个时
它会藏在过期的噪声里。

### 写这个测试时踩的坑

第一次写的时候用了「取 label 之后的文本，找到第一个 `)`，截断」：

```csharp
var close = tail.IndexOf(')');
if (close > 60) continue;              // 认为是多行 handler
if (!statusOnly.IsMatch(tail[..(close + 1)])) continue;
```

**结果 `live: 0`。**

因为 `(), => Status(…)` 里的第一个 `)` 是**空参数列表的那个**，所以每个 fragment 都是 `', ()'`。

改用一条正则匹配整个结构：

```csharp
new Regex(@"UiKit\.Button\s*\(\s*""(?<label>[^""\\]*(?:\\.[^""\\]*)*)""\s*,"
        + @"\s*\(\s*\)\s*=>\s*(?<body>Status\(|_status\.Text\s*=|S\()")
```

**「截一段文本再判断」和「一次匹配完整结构」的区别，在这个例子里是 0 和 15。**

### 验证

```
dotnet test      547 通过 / 0 失败 / 2 跳过   (+2 DeadButtonTests)
release build    0 errors
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
```

---
