### `Navigator.prototype` 是 36 还是 71？——取决于页面站在哪个上下文

R139 的探测留下一个问题：`Object.getOwnPropertyNames(Navigator.prototype).length === 36`，
那个数对不对。

### 答案：36 是错的，71 才对——因为探测站在错的地方

R139 导航到 `data:text/html,…`。**`data:` URL 不是安全上下文。**

改成 `http://127.0.0.1:PORT/`（loopback 是安全上下文，和任何 `https://` 商城等同）之后：

| 项 | `data:` URL | `http://127.0.0.1` |
|---|---|---|
| `isSecureContext` | false | **true** |
| `Navigator.prototype` | 36 | **71** |
| `Document.prototype` | 246 | **250** |
| `window` own props | 988 | **1238** |
| `window` enumerable | 224 | **237** |

**35 个成员差了整整一半。**

### 那 35 个是什么

```
userAgentData  connection  bluetooth  usb  hid  serial  xr  deviceMemory
getBattery  mediaDevices  clipboard  gpu  locks  storage  wakeLock
presentation  scheduling  serviceWorker  credentials  keyboard  managed
virtualKeyboard  login  devicePosture  storageBuckets  canShare  share
clearAppBadge  setAppBadge  getUserMedia  requestMIDIAccess  requestMediaKeySystemAccess
getInstalledRelatedApps  registerProtocolHandler  unregisterProtocolHandler
```

**全部是「只在安全上下文暴露」的 API。** 它们不是缺失，是没解锁。

### 这解释了 R139 的十二个 `false`

R139 那张表里：

```
userAgentData    false     ← 安全上下文
bluetooth        false     ← 安全上下文
usb              false     ← 安全上下文
hid              false     ← 安全上下文
serial           false     ← 安全上下文
mediaDevices     false     ← 安全上下文
clipboard        false     ← 安全上下文
gpu              false     ← 安全上下文
locks            false     ← 安全上下文
storage          false     ← 安全上下文
wakeLock         false     ← 安全上下文
serviceWorker    false     ← 安全上下文
```

**十二个「缺失」，一个原因。**

### 修：测试自带一个 loopback 页

`InterfaceInventoryTests` 现在起一个 `HttpListener` 在 `127.0.0.1` 的随机端口上，
回一个最小 HTML，然后导航过去。

```csharp
private sealed class LocalPage : IDisposable
{
    public LocalPage()
    {
        var port = FreePort();
        Url = $"http://127.0.0.1:{port}/";
        _listener = new System.Net.HttpListener();
        _listener.Prefixes.Add(Url);
        _listener.Start();
        …
    }
}
```

**端口取 0 让系统分配，测完 `Stop()` + `Close()`。**

### 六条真断言

现在这个测试不只打印，它固定了 Windows Chrome 该有的样子：

| 断言 | 值 |
|---|---|
| `isSecureContext` 为 true | ✅ |
| **18 个 Blink 专有成员全 present** | `userAgentData` … `serviceWorker` 全 true |
| **2 个 WebKit 专有成员全 absent** | `standalone` / `audioSession` 全 false |
| `Navigator.prototype` ≥ 60 | **71** |
| UA token 是 `<major>.0.0.0` | `157.0.0.0` |
| `brands[].version` == UA 的 major | `157` == `157` |

**第二条和第三条是一对**：

- 如果哪天有人把原版的 `NAV_PRUNE`（删 Blink 专有成员）照搬到 replica 上，
  **第二条立刻红**——18 个成员会被删掉。
- 如果哪天有人为了「看起来像 Chrome」加上 `standalone`，
  **第三条立刻红**。

**那两个方向的错误，一个测试挡住了。**

### 一个 CDP 限制，如实记下

R138 修的是「UA 说 157，`userAgentData` 说 131」。修完之后这一轮去验证，发现：

```js
navigator.userAgentData.fullVersion             // undefined
navigator.userAgentData.getHighEntropyValues(['fullVersion'])
// → { brands: [...], mobile: false, platform: "Windows" }     ← 没有 fullVersion
```

**`fullVersion` 不在返回里，而且 `brands[].version` 是我设的 `157` 而不是
`fullVersionList` 里的 `157.0.8103.38`。**

**Chrome 157 的 headless 把 `fullVersionList` 的每一项都降级到 major。**

所以：

| 项 | 能否通过 CDP 控制 |
|---|---|
| `brands[].version` | **能**，且它是检测方拿去和 UA 比的那一个 |
| `getHighEntropyValues().fullVersion` | **不能**，这个 build 直接不返回 |

**R138 的修复仍然有效**——它保证 `brands` 和 UA 一致，那正是能被比对的部分。
**但「完整版本号」这一层，replica 和原版一样做不到。**

测试里写成：

```csharp
if (fullVersion == "(absent)")
    _out.WriteLine("CDP limitation: setUserAgentOverride.fullVersionList is downgraded to the major on this build");
else
    Assert.Equal(uaToken.Split('.')[0], fullVersion.Split('.')[0]);
```

**记下限制，而不是假装它不存在。** 哪天某个 build 开始返回它，这条会打印出来，
上面的注释就是需要改的地方。

### 验证

```
dotnet test --filter "Speed!=Slow"   643 通过 / 0 失败 / 2 跳过
live contracts                      PASS
store modules                       PASS 61 registered
build errors                        0
probe chrome left                   0
```

**输出**：

```
Navigator.prototype on a secure context: 71
UA token      157.0.0.0
brand version 157
fullVersion   (absent)
CDP limitation: setUserAgentOverride.fullVersionList is downgraded to the major on this build
```

---
