# 事件接线表

上一轮（6.40）发现 `TaskEngine.CheckoutCompleted` 与 `EventBus.Checkout` 之间没有桥接，导致 Smart Actions / Analytics / 通知在真实运行时全部失效。这类“模块之间接不上”的缺陷单测抓不到，所以把全部事件与消费者列成契约，改动时必须对照。

## 事件清单

| 事件 | 触发方 | 消费方 | 状态 |
|---|---|---|---|
| `EventBus.Logged` | `EventBus.Log/Info/Warn/Error` | `MainViewModel`（Logs 页）、`SolverWindow` | ✅ |
| `EventBus.Notification` | `NotificationService`、模块告警 | `MainViewModel`（转日志 `[notify]`） | ✅ 本轮补 |
| `EventBus.Checkout` | `AppServices` 桥接 `TaskEngine.CheckoutCompleted` | `SmartActionEngine`、`CheckoutStats`、`MainViewModel`（结账流水） | ✅ 6.40 修复桥接 |
| `TaskEngine.CheckoutCompleted` | `TaskEngine.RunCoreAsync` | `AppServices` → `EventBus.RaiseCheckout` | ✅ 6.40 |
| `TaskEngine.StateChanged` | `TaskEngine.Raise` | `MainViewModel`（状态栏 + 刷新任务表） | ✅ 本轮补 |
| `NotificationService.Shown` | `PublishAsync` | `MainViewModel`（状态栏 `[Kind] Title`） | ✅ 本轮补 |
| `CheckoutStats.Changed` | 每次记录结账 | `MainWindow`（Analytics 摘要 + 柱状图） | ✅ |
| `HttpAnalytics.RequestRecorded` | `NetClient` 每次请求 | `MonitorWindow` | ✅ |
| `HttpAnalytics.ConnectionRecorded` | 连接建立/复用 | `MonitorWindow` | ✅ |
| `ClockService` 时间同步 | 定时器 | 无订阅（仅更新自身偏移） | ⚪ 设计如此 |

## 检查方法

改完与事件相关的代码后，跑：

```
D:\tools\dotnet8\dotnet.exe test tests\Cybersole.Tests\Cybersole.Tests.csproj
```

集成测试 `TaskEngineIntegrationTests` 会真起一个本地店铺、跑真实 `TaskEngine`，断言结账事件确实到达 `EventBus` —— 这是唯一能抓住“桥没接”的测试。

## 新增事件的规矩

1. 事件定义在 `EventBus` 或对应服务上；
2. **必须有至少一个生产消费方**，否则就是死代码；
3. 跨层传递（例如引擎 → 总线）要显式桥接，并在本表登记；
4. 集成测试里断言一次真实触发路径。

## 持久化路径

`ConfigurationStore.Save()` 一次写全部 8 个文档（settings / accounts / tasks / proxies / billing / solvers / analytics / smartActions），所以任何改内存的地方都必须在改完调一次。

| 修改点 | 是否落盘 |
|---|---|
| `TaskEditorWindow.Submit` | ✅ |
| `ProfileEditorWindow.Submit` | ✅ |
| `AccountImportWindow.Import` | ✅ |
| `SmartActionEditorWindow`（新增/删除/保存） | ✅ |
| `SolverWindow` 的 7 个开关 | ✅ 6.42 修复 |
| 设置页各项（点 Save 时） | ✅ `MainViewModel.SaveSettings` |
| 任务列表增删（`AddDemoTask` 等） | ✅ |
| `.cyb` 全量快照 | ✅ 6.42 接到启动/退出 |

检查方法：`Get-ChildItem -Recurse -Filter *.cs src | Select-String 'Config\.Save\(\)'`，新增编辑器时必须出现在列表里。
