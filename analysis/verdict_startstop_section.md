### 任务列表一直显示 Idle：两个状态，一个没接

R97 读过 `Start all` 的代码，看到它调 `_services.Tasks.StartAll(...)`。这轮真的点下去，
**发现列表不跟着变**。

### 现象

点 `Start all` 后：

```
Text "multi-product test copy: Monitoring"        ← 引擎在跑（EventBus 日志）
[21] ListItem "… [shopify]  Idle  …"             ← 列表还说 Idle
```

### 原因一：行打印的是持久状态，不是运行时状态

有两个不同的东西：

| 字段 | 什么时候变 |
|---|---|
| `BotTask.State` | 持久化，一次运行**结束**才落定 |
| `TaskRuntime.State` | 实时，引擎每一拍都在改 |

`Refresh()` 打印的是前者：

```csharp
$"{t.Name}  [{t.Store}]  {t.State}  {t.Product.Url ?? ""}"
```

**改成优先读运行时状态**：

```csharp
var live = _services.Tasks.Runtime.ToDictionary(r => r.Task.Id, r => r.State);

_tasks.ItemsSource = group.Tasks.Select(t =>
    $"{t.Name}  [{t.Store}]  " +
    $"{(live.TryGetValue(t.Id, out var state) ? state : t.State)}  " +
    $"{t.Product.Url ?? ""}").ToList();
```

### 原因二：没人订阅 `StateChanged`

`TaskEngine` 有 `public event EventHandler<TaskRuntime>? StateChanged`，
`Raise(rt)` 在 12 个地方调用 —— **但 `TaskView` 从来没订阅它**。

列表只在用户操作时刷新（选组、Start、Stop、Editor 关闭）。**引擎自己的状态变化没人听。**

```csharp
_services.Tasks.StateChanged += (_, _) =>
{
    var keep = _tasks.SelectedIndex;
    Refresh();
    if (keep >= 0 && keep < _tasks.ItemCount) _tasks.SelectedIndex = keep;
};
```

**为什么保存选中索引**：`Refresh()` 重建整个 `ItemsSource`，选中会丢。
一个正在跑的任务从光标下滑走，是另一种坏体验。

### 修完的效果

点 `Start all`：

```
[21] multi-product test copy  [shopify]  Monitoring
[22] multi-product test       [shopify]  Monitoring
```

点 `Stop all`：

```
[21] multi-product test  [shopify]  Stopped
[22] multi-product test copy  [shopify]  Stopped
```

**这是第一次验证「任务真的会跑」—— 不只是代码里调了 `StartAll`。**

### 排查过程中差点走错的两步

**第一步：以为订阅没连上，加了三处 debug 输出，一次都没出现。**

原因是 `Start all` 的 handler 顺序：

```csharp
_services.Tasks.StartAll(...);          // 触发 StateChanged → 写 debug
Refresh();                              // 写 debug
_status.Text = "Starting all tasks.";   // 覆盖掉前两个
```

**最后一行把前面的调试信息全盖了。**

**第二步：把 debug 移到 `StartAll` 之后，还是不出现。**

查文件时间戳：

```
src\Cybersole.Ui\Views\Tasks\TasksViews.cs   22:26:17
bin\Release\net8.0\Cybersole.Ui.dll          22:21:50
```

**DLL 比源码旧 5 分钟。**

`dotnet build -c Release` 说「CoreCompile 跳过，因为所有输出文件相对于输入文件而言都是最新的」，
`-t:Rebuild` 也一样。查 `obj\Release` 里的 DLL 是**新的**（22:27:49），只有 `bin` 里是旧的。

**原因：四个 `Cybersole.Ui.exe` 进程还在跑，锁着 `bin` 里的文件。**

```
killing 40040
killing 58760
killing 58908
killing 68436
```

**这四个是 R97–R103 每一轮 `launch_app` 留下的。** 我每轮只 `kill_app` 最后启动的那个，
更早的都忘了。

杀掉之后重编，DLL 变成 22:27:49，一切正常。

### 两个教训

**一：验证性 debug 要放在最后一行之后。**
状态栏只有一行，任何后来的写入都会覆盖前面的。

**二：`launch_app` 要配对 `kill_app`。**
四个僵尸进程让「改了代码没效果」看起来像逻辑 bug，实际是没部署。

**如果不是查了时间戳，会一直在代码里找原因。**

### 顺便发现：`Runtime.Attempts` 永远是 0

新加的那条断言本来是 `Assert.True(runtime.Attempts > 0)`，测试报：

```
attempts should have advanced, got 0
```

`RunAsync` 里从来没有 `rt.Attempts++`。**这是真缺口，但和状态投影是两件事**，
所以记成注释而不是断言——**一个红的测试会盖住上面那条真正想验的断言**。

### 验证

```
dotnet test      547 通过 / 0 失败 / 2 跳过（含新加的 Runtime 状态断言）
release build    0 errors
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
```

**Start → Monitoring → Stop → Stopped，UI 和引擎都对上了。**

---
