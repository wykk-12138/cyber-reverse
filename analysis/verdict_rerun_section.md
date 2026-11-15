### 19 项探测重跑到安全上下文：三处变了，一处没变

R141 发现探测站在 `data:` URL 上，那 35 个 `navigator` 成员因此「缺失」。这一轮把 R139 的
**全部 19 项**重跑到 loopback 上。

### 对照

| 项 | R139（`data:`） | R142（`127.0.0.1`） | 判定 |
|---|---|---|---|
| `isSecureContext` | false | **true** | 上下文换了 |
| `navigator own props` | 36 | **71** | 35 个解锁 |
| `navigator has userAgentData` | absent | **present** | 上下文 |
| `document has browsingTopics` | absent | **present** | **上下文** |
| `document has featurePolicy` | present | present | 不变 |
| `uaData.brands` | absent | **present** | 上下文 |
| `uaData.fullVersion` | absent | **(null)** | **CDP 不暴露** |
| `webdriver` | undefined | undefined | 稳定 |
| `getVoices().length` | 6 | 6 | 稳定 |
| `ontouchstart in window` | False | False | 稳定 |
| `ontouchstart shape` | no descriptor | no descriptor | 稳定 |
| `plugins length` | 3 | 3 | 稳定 |
| `hardwareConcurrency` | 8 | 8 | 稳定 |
| `document own props` | location | location | 稳定 |
| `webdriver` in iframe | undefined | undefined | 稳定 |
| `voices` in iframe | 6 | 6 | 稳定 |
| `webkit in window` | False | False | 稳定 |
| `chrome in window` | True | True | 稳定 |

**三处变了，全部是「安全上下文门控」的 API。其余九项两次一致——那九项是真的。**

### 新的一处：`document.browsingTopics`

R141 的 `DOCUMENT_PRUNE` 列表里有它，R139 测出 `absent`，我当时判断「Chrome 157 已移除」。

**测在 `127.0.0.1` 上是 `present`。**

**所以它不是被移除，是被上下文门控。** 原版删它是因为 **WebKit 从来没有**，不是因为浏览器版本老。

**这是一个用错上下文就会得出的错误结论**——而且它听上去很合理（「新版移除了」）。

### 一处没变，而且不会变：`fullVersion`

```
uaData.fullVersion    (null)
```

`navigator.userAgentData.brands` 现在能读到：

```json
[{"brand":"Chromium","version":"157"},
 {"brand":"Google Chrome","version":"157"},
 {"brand":"Not_A Brand","version":"24"}]
```

**但 `fullVersion` 拿不到**——R141 已经用三种方式确认过：

```js
navigator.userAgentData.fullVersion                                    // undefined
navigator.userAgentData.getHighEntropyValues(['fullVersion']).then(…)  // 返回对象里没有这个键
Object.keys(navigator.userAgentData)                                   // 空
```

**Chrome 157 的 headless 把 `setUserAgentOverride.fullVersionList` 的每一项降级到 major，
并且不实现 `fullVersion` 这个 hint。**

所以断言写成：

```csharp
if (secure == "true")
{
    var brandVersion = Extract(brands, @"""version"":""(\d+)""");
    Assert.Equal(uaToken!.Split('.')[0], brandVersion);
    _out.WriteLine($"fullVersion from the default surface: {full} (CDP does not expose it)");
}
```

**`brands[].version` 能断言，`fullVersion` 只打印。** 前者是检测方拿去和 UA 比的那一个，
后者这个 build 根本不给——**对着一个测不到的东西写断言，只会让测试红在一个无法修的原因上，
而那个红会掩盖真正的回归。**

### `LocalPageServer` 提成一个共享类

两个 live 测试现在都用它：`tests/Cybersole.Tests/Support/LocalPageServer.cs`。

端口取 0 由系统分配，测完 `Stop()` + `Close()` + `Wait(1000)`。
**两个测试跑完，`cyb-chromium-` 的 Chrome 进程是 0 个**——`DisposeAsync` 里
`Kill(entireProcessTree: true)` 生效了。

### 验证

```
两个 live 测试            2 通过 / 0 失败（116 ms，Chrome 已预热）
dotnet test（快）         643 通过 / 0 失败 / 2 跳过
live contracts           PASS
store modules            PASS 61 registered
```

---
