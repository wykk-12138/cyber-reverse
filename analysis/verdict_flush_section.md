### `HttpAnalytics.Flush()`：一个空循环，而且它先删后判

读 `bucket_cybersole_ns.txt` 时发现了原版的程序集结构：

```
Cybersole.Core.dll
Cybersole.Http  +  .Newtonsoft  +  .Analytics  +  .Debug     ← 四个一起发
Cybersole.Tests / Cybersole.Cli
```

`Cybersole.Http` 是**公开发布的 NuGet 包**：

```
0.10.0.0  0.10.0+b3c7d7208d6ca2c3fbf0c83ed69c5b1a2c04b4d6
https://github.com/Cybersole/NetClient
```

它的两个子包的包描述写着它们该做什么：

> **Analytics** — every request (URL, status, timings, bytes, protocol, profile, proxy, tags) and every connection (opened, failed, closed) is written to **ClickHouse in batches**, enabled with `HttpAnalytics.Start(options)`.

> **Debug** — live request stream … to the Cybersole Proxy viewer, enabled with `HttpDebug.Enable()`.

### replica 的 `Flush()` 是这样的

```csharp
public void Flush()
{
    while (_requests.TryDequeue(out var req))
    {
        // Sink integration point: POST req as JSON to ClickHouse in batches.
        if (SinkUrl is null) break;
    }
}
```

**三层问题，每一层单独都够糟**：

1. **循环体是空的** —— 注释说「在这里 POST」，但那里没有 POST
2. **`TryDequeue` 在 `if (SinkUrl is null)` 之前执行** —— 即使没配 sink，**每调用一次就丢一个事件**
3. **`HttpAnalytics(autoFlush: true)` 每 10 秒调一次 `Flush`** —— 所以「丢一个」是「每 10 秒丢一个」

**实测**：`AppServices.cs:88` 是 `HttpDebug.Attach(analytics)`，而 `HttpAnalytics` 的 `autoFlush` 默认 `false`，所以目前不会自动丢。
**但只要有人把 `autoFlush` 打开，整个分析与调试缓冲区就会每 10 秒清空一次，而且没有任何报错。**

### 修

```csharp
public void Flush()
{
    if (SinkUrl is null) return;     // nothing to do, and nothing to lose

    var batch = new List<HttpRequestEvent>(Math.Min(BatchSize, 256));
    while (batch.Count < BatchSize && _requests.TryDequeue(out var req))
        batch.Add(req);

    if (batch.Count == 0) return;

    var body = new StringBuilder();
    foreach (var r in batch)
        body.Append(JsonConvert.SerializeObject(new { at = …, method = …, status = …,
            elapsed_ms = …, bytes = …, protocol = …, tag = …, profile = …, proxy = … },
            Formatting.None)).Append('\n');

    var target = SinkUrl;
    var payload = body.ToString();

    // fire and forget: analytics must never stall a request
    _ = Task.Run(async () =>
    {
        try
        {
            using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            using var content = new StringContent(payload, Encoding.UTF8, "application/x-ndjson");
            using var res = await http.PostAsync(target, content);
            if (!res.IsSuccessStatusCode)
                _failures.Enqueue($"… sink {target} rejected batch: HTTP {(int)res.StatusCode}");
        }
        catch (Exception ex)
        {
            _failures.Enqueue($"… sink {target} failed: {ex.Message}");
        }
    });
}
```

**格式是 ClickHouse 的 `JSONEachRow`**：一行一个紧凑对象，没有外层数组。
`application/x-ndjson` 是 ClickHouse HTTP 接口吃的类型。

### 三条测试

| 测试 | 挡什么 | 输出 |
|---|---|---|
| `Flush_WithNoSink_KeepsEveryEvent` | **原 bug**：没 sink 时丢数据 | `kept 5 of 5 after two flushes with no sink` |
| `BatchSize_CapsOneFlush` | 一次只发一批 | `BatchSize=3 left 4 of 7` |
| `Flush_WithSink_DoesNotBlockTheCaller` | 分析拖慢结账 | `Flush returned in 0 ms against a non-routable sink` |

**第一条是这次的核心**：它直接对着那个 `TryDequeue` 在 `SinkUrl` 之前的问题。
**如果 `Flush` 改回旧写法，这条测试立刻红。**

**第三条用 `10.255.255.1`（不可路由地址）**：同步发请求会挂几十秒，`Flush` 必须是即时的。

### 写测试时踩到自己的假设

第一版写了 `BatchSize = 3` 然后录 7 个，断言 `Snapshot.Count == 7`。
**失败了** —— 因为 `Record()` 里有 `if (_requests.Count >= BatchSize) Flush();`，
录到第 3 个和第 6 个时已经自动 flush 过两次了。

**改成「先按大 BatchSize 录，录完再调小」**——这样 `Record` 的自动 flush 不会干扰，
而 `Flush` 自己的批次上限仍然是可测的。

> **测试一个方法之前，要先确认它的邻居不会替它做事。**

### `Cybersole.Cli`：只有一个名字

字符串表里 `Cybersole.Cli` **出现一次**，就是程序集名本身。
没有命令、没有 `--flag`、没有 `Usage:`。

**证据等级 C。不补。** 一个只有名字的项目，补出来只能是我的想象。

### 验证

```
dotnet test      587 通过 / 0 失败 / 2 跳过   (+4)
live contracts   PASS
store modules    PASS 61 registered
build errors     0
```

---
