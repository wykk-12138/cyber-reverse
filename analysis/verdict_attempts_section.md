### `Attempts` 不是 bug，是我读错了它的含义

R103 加了一条断言 `Assert.True(runtime.Attempts > 0)`，测试报：

```
attempts should have advanced, got 0
```

**我把它记成「引擎不计数」的缺口。** 这轮查源码，发现它一直在计数：

```csharp
// TaskEngine.cs:291
else
{
    rt.Attempts++;
    await Task.Delay(monitorDelay, ct).ConfigureAwait(false);
}
```

**在 `else` 分支** —— 也就是「没有库存」的那条路。

而集成测试的 mock 服务端第一拍就返回 `available: true`，走的是 `if (monitor.InStock)` →
直接进结账，**从来不到 `else`**。

### 所以 `Attempts` 的实际语义

| 名字暗示 | 实际含义 |
|---|---|
| 「尝试结账几次」 | **「轮询了几次，每次都发现没货」** |

**名字错了，行为没错。**

### 处理方式：改文档而不是改代码

**为什么不改名**：`TaskRuntime` 只在内存里，没有序列化、没有跨进程约定，改名成本低——
但**收益也是零**。真正需要修的是「读它的人会猜错」。

**所以加了一段 summary**：

```csharp
/// Monitor polls that came back out of stock.
///
/// Not "checkout attempts" despite the name: the in-stock branch raises state and hands off to
/// checkout without touching this, and the checkout path either returns (success) or backs off
/// on retryDelay. Only the idle poll loop increments it.
///
/// Round 103 added an assertion that this advances after a real checkout and it did not —
/// that was the test guessing the wrong semantic, not the engine missing a count.
public int Attempts { get; set; }
```

**并且把测试拆成两条，各钉一半语义**：

```csharp
// 有货：mock 第一拍就有库存，所以必须还是 0
Assert.Equal(0, runtime.Attempts);

// 无货：每拍加一
Assert.True(runtime.Attempts >= 3, $"expected several sold-out polls, got {runtime.Attempts}");
```

第二条需要 mock 支持无货，所以 `StartStoreServer` 加了个参数：

```csharp
private static (HttpListener Listener, int Port) StartStoreServer(bool inStock = true)
```

```csharp
var body = path.Contains("cart")
    ? "{\"orderNumber\":\"TEST-123\"}"
    : $"{{\"available\":{(inStock ? "true" : "false")},…}}";
```

新测试：

```csharp
[Fact]
public async Task SoldOutPollsAdvanceTheAttemptsCounter()
{
    var (listener, port) = StartStoreServer(inStock: false);
    …
    engine.Start(task);
    await Task.Delay(900);        // MonitorDelay = 40ms，约 6 拍

    Assert.True(runtime.Attempts >= 3, $"expected several sold-out polls, got {runtime.Attempts}");
    Assert.Equal(TaskState.Monitoring, runtime.State);
}
```

**跑了 903 ms，`>= 3` 通过。**

### 这是一次「测试写错了」而不是「代码写错了」

R103 的记录里写着：

> `RunAsync` 里从来没有 `rt.Attempts++`。**真缺口。**

**那句是错的。** 我只 grep 了 `Attempts` 出现的行，看到 `TaskEngine.cs:291: rt.Attempts++;`
却没看它在哪个分支里 —— **有那行，但没在那条路上**。

**这轮的教训和 R102 的同源**：

> **「字段名出现了」和「字段在这个场景下被赋值」是两件事。**
>
> R102 是扫描器把 `_authCode` 判成未读（实际在另一个方法里读）；
> R104 是我把 `rt.Attempts++` 判成不存在（实际在另一个分支里）。

**两次都是「按名字找，按字面判断，没看控制流」。**

### 验证

```
dotnet test      548 通过 / 0 失败 / 2 跳过   (+1 SoldOutPollsAdvanceTheAttemptsCounter)
release build    0 errors
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
```

---
