import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 第四次同一个形状：发信人终于被调用，而**离线三件事同时成立**（第 155 轮）

`SessionTelemetry` 上一轮是独立类，没人调用。这一轮接进 `HttpAnalytics.Flush()`。

### 一、接口放哪：依赖方向决定位置

`Cybersole.Stores` 引用 `Cybersole.Http`，不是反过来。所以接口在 Http、实现在 Stores：

```csharp
public interface ISessionSink
{
    bool IsConfigured { get; }
    Task<bool> SendAsync(CancellationToken ct = default);
}
```

**好处不只是编译能过** —— `HttpAnalytics` 因此**不知道指纹是什么**，它只知道「有个东西可以收一份会话摘要」。

### 二、一个必须改的早退

```csharp
// 旧：只有请求侧有地址才继续
if (SinkUrl is null) return;
```

这会让「只配遥测、不配 ClickHouse」的部署**静默永不发送** —— 和 R127 那个「先 dequeue 再判空」是同一类缺陷。
现在早退的条件变成**两侧都没有**。

### 三、离线三件事同时成立

| 测试 | 断言 |
|---|---|
| 只配遥测 | `SinkUrl` 为 null 时**仍然发送**（fire-and-forget，测试轮询等它） |
| sink 未配置 | **一次都不调用**，也不排队 |
| 什么都没配 | 请求仍留在缓冲里、`Failures` 为空 —— **不构建、不排队、不发** |
| sink 抛异常 | 记进 `Failures`（`session sink failed: …`），**不冒到 flush 调用方** |
| 工厂缺失 | 拒绝并给理由 `no inputs factory`，传输零调用 |

### 四、为什么用「工厂」而不是「快照」

flush 是定时器驱动的，它不知道会话。如果挂上 sink 时就把 inputs 快照下来，发出去的会是**挂上那一刻**的会话，
而不是**发送那一刻**的。所以接口实现是：

```csharp
public Func<SessionPayloadBuilder.Inputs>? InputsFactory { get; set; }
```

### 五、这一轮的一句话

> 这是本会话第四次遇到同一个形状：**类写好了，没人调用。** 前三次我都是被测试逼着发现的。
>
> **这次我提前知道会这样，所以先写了「谁会调用它」再写它。差别不大，但方向对了。**
'''

if "## 第四次同一个形状" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("sink wiring documented")
else:
    print("already present")
