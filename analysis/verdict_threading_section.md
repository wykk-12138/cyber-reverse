### `3DS` / `Monitor`：一个模态窗口的返回值，和一个跨线程的连锁反应

顶部工具栏的四个窗口（`Solver` / `Browser` / `Monitor` / `3DS`）这一轮查了两个。

### `3DS`：模态窗口返回 null

`ThreeDSWindow` 本身是完整的：

```csharp
private readonly TaskCompletionSource<string?> _tcs = new();
public Task<string?> Result => _tcs.Task;

private void CloseWithResult(string? code)
{
    if (!_tcs.Task.IsCompleted) _tcs.TrySetResult(code);
    base.Close();          // ← 无参
}
```

`MainWindow` 这样用它：

```csharp
var code = await win.ShowDialog<string?>(this);
if (!string.IsNullOrEmpty(code))
    _status.Text = $"3DS code captured ({code.Length} digits)";
```

**`ShowDialog<T>` 解析的是 `Close(object?)` 的参数。无参 `Close()` → `default(string?)` → `null`。**

**实测**：输入 `123456`，点 `Submit`，窗口关了，**状态栏没变**。

**修**：

```csharp
Close(code);   // 传给 ShowDialog 的返回值
```

**实测**：`3DS code captured (6 digits)` ✅

**`_tcs` 从没被 `await` 过**——两条通路只走了一条。`Result` 属性是给「非模态打开 + 外部 await」准备的，但当前没人用。

### `Monitor`：记录一条请求会炸掉发起请求的人

打开 `Monitor`，然后点 `License` → `Verify`：

```
failed: Call from invalid thread
```

**这不是 `License` 的错误。**

链条是这样的：

```
VerifyLicenseAsync
  → NetClient.GetAsync
      → HttpAnalytics.Record(...)
          → RequestRecorded?.Invoke(...)         ← 在池线程上
              → MonitorWindow 的订阅者
                  → _stream.Items.Insert(0, ...)  ← ListBox，UI 线程独占
                      → throw InvalidOperationException
          ← 异常从 Invoke 冒泡回 Record，再冒泡回 GetAsync
  ← catch (Exception ex) → _status.Text = "failed: " + ex.Message
```

**同一个 bug 在 `MainViewModel` 里还有三处**：

```csharp
_services.Bus.Logged    += (_, e) => AppendLog(e.ToString());          // ❌
_services.Bus.Checkout  += (_, e) => CheckoutLines.Insert(0, ...);     // ❌
_services.Bus.Notification += (_, message) => AppendLog(...);          // ❌

_services.Tasks.StateChanged += (_, rt) => Dispatcher.UIThread.Post(…); // ✅
_services.Notify.Shown       += (_, n)  => Dispatcher.UIThread.Post(…); // ✅
```

**同一个文件里，两处对了，三处错了。** 对的那两处是后来修的（R103 加了 `StateChanged` 的 Post）。

**修**：五个订阅者全部 `Dispatcher.UIThread.Post`。

`MonitorWindow` 里 `Matches(e)` 也读 `_filter.Text`，所以判断一起搬进 Post 内部。

### 修完实测

```
License: failed: the licence endpoint returned a sealed token that this build cannot open…
Monitor: requests=1  failures=0
         15:40:44.226 GET  200   961ms     206B http/1.1 license
         https://cybersole.io/api/apisecuretoken
```

**`License` 报出了它自己的真实错误，`Monitor` 记下了那条请求。**

### 一个「错误信息」的教训

**"Call from invalid thread" 是关于 `Monitor` 的，但它显示在 `License` 的对话框里。**

一个事件订阅者的线程违规，会让**任意一个**触发该事件的调用方报出一个和它无关的错误。

> **跨线程 bug 最难查的不是它在哪，而是它伪装成别处的故障。**

### 这一轮的四种缺陷

| 窗口 | 问题 | 类型 |
|---|---|---|
| `3DS` | `ShowDialog<T>` 返回 null | **API 误用**（用了但用错） |
| `Monitor` | 跨线程写 `ListBox` | **线程违规**（新类型） |
| `MainViewModel` | 三处跨线程写 `ObservableCollection` | 同上 |
| `License` | 被别人的线程违规污染 | **错误伪装** |

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
stray processes  0
settings.json    license 已清空
```

---
