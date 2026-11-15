### UA 说 157，`userAgentData` 说 131：一个自己拆自己台的会话

R137 在找 `NAV_PRUNE` 的实现，先读到的是它旁边的三份诊断记录。其中一份讲的是
hCaptcha 的 `spst` 字段；顺着它去核对 replica 的 UA 一致性，发现了一个更显眼的问题。

### 原版的三份诊断记录

**一、`spst`：在第一个请求上就输了**

```js
// hCaptcha's checksiteconfig -- the FIRST request of the whole flow, in plaintext, before a single
// sensor byte -- carries `spst=<0|1>`, computed as
//   !(document.hasPrivateToken === undefined || !document.featurePolicy ||
//     !document.featurePolicy.allowsFeature) &&
//   document.featurePolicy.allowsFeature("private-state-token-redemption")
// Private State Tokens and featurePolicy are Blink-only; WebKit has never shipped either, so a real
// Chrome-on-iOS can only ever answer 0. We answered 1. Verified against a device capture on the
// SAME sitekey AND the same api.js build (d865efcccaf8): device spst=0, bot spst=1 -- the only
// apples-to-apples comparison in the whole artifact set, and we were losing it on request one.
```

**「the only apples-to-apples comparison in the whole artifact set, and we were losing it on
request one」** —— 同一 sitekey、同一 `api.js` build（`d865efcccaf8`），一个 0 一个 1。
**在任何传感器字节之前，第一个明文请求就判定了。**

**对 replica 的启示是条件式的**：`spst` 的值取决于 UA 声称的平台——
iOS/WebKit 只能答 0，Windows/Blink 本来就答 1。
**replica 声称 Windows，答 1 是一致的。这个前提必须成立，否则整套 UA 都在撒谎。**

**二、`GLOBAL_PRUNE`：真正重要的那个 frame 在说实话**

```js
// Deleting only in this realm left `'chrome' in window` false at the top and TRUE inside an
// iframe -- and the challenge runs in an iframe, so the frame that matters was answering honestly.
```

**三、`NAV_PRUNE`：browserleaks 直接读 `navigator`**

```js
// Blink exposes a pile of interfaces WebKit has never shipped -- userAgentData, getBattery,
// connection, bluetooth, usb, hid, serial, xr, deviceMemory -- and browserleaks reads every one
// of them straight off navigator.
```

三条都是 iOS 专用的，**replica 一条都不需要**——它跑真的 Windows Chrome，
Blink 有的东西本来就该有。

**但第一条指向一个必须核对的前提。**

### 核对的代价

```
ChromiumBridge.cs:162     var version = "131.0.0.0";      ← 硬编码
```

而同一个文件里：

```csharp
public static string DefaultUserAgent()
{
    var chromeVersion = ChromiumBridgeVersion();   // ← 读真实版本
    return "… Chrome/{chromeVersion} Safari/537.36";
}
```

**这台机器装的是 Chrome 157.0.8103.38。**

所以同一个会话同时说：

| 位置 | 值 |
|---|---|
| `navigator.userAgent` | `Chrome/157.0.8103.38` |
| `navigator.userAgentData.brands` | `[{ brand: "Google Chrome", version: "131" }]` |
| `navigator.userAgentData.fullVersion` | `"131.0.0.0"` |

**UA 说 157，`userAgentData` 说 131。比对这两个字符串是一行代码，成本为零。**

**这个矛盾比 R136 修的 iframe 更容易被抓**：iframe 需要检测方主动去建一个 frame，
而这个只要读两个已存在的属性。

### 修：两处，一个来源

```csharp
var fullVersion = ChromiumBridgeVersion();          // 157.0.8103.38
var major = fullVersion.Split('.')[0];              // 157
```

`brands` 用 `major`，`fullVersionList` 和 `fullVersion` 用 `fullVersion`。

### 第二个问题：UA 里不该有构建号

原来 `DefaultUserAgent()` 把**完整版本**塞进 UA：

```
Chrome/157.0.8103.38
```

**真实的 Chrome 157 发的是**：

```
Chrome/157.0.0.0
```

**User-Agent Reduction** 把 UA 冻结成 `<major>.0.0.0`，完整构建号只在
`getHighEntropyValues()` 里出现。**在 UA 里写构建号，本身就是「这个 UA 是手写的」的信号。**

改成：

```csharp
var major = ChromiumBridgeVersion().Split('.')[0];
return "… Chrome/{major}.0.0.0 Safari/537.36";
```

**实测**：

```
UA: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
    Chrome/157.0.0.0 Safari/537.36
major: 157
```

### 第三个问题：硬编码兜底值

`ChromiumBridgeVersion()` 只有两个来源：`--version` 和硬编码 `"131.0.0.0"`。

**这台机器上 `--version` 是工作的**（输出 `Google Chrome 157.0.8103.38`），
但某些构建或受限配置下它不输出，那时 UA 会声称 **131**，而实际是 **157**——
**差 26 个大版本**。

加第二来源：

```csharp
var info = System.Diagnostics.FileVersionInfo.GetVersionInfo(path);
var candidate = info.ProductVersion ?? info.FileVersion;
```

**那是 Windows「属性 → 详细信息」里显示的值，`--version` 沉默时它仍然正确。**

三级顺序：`--version` → `FileVersionInfo` → `131.0.0.0`（最后兜底，注释写明「a stale
claim here is worse than no claim」）。

### 四条测试

| 测试 | 断言 | 输出 |
|---|---|---|
| `UserAgentUsesTheReducedForm` | 含 `Chrome/{major}.0.0.0`，不含 `Chrome/{chromeVersion}` | ✅ |
| `UserAgentDataComesFromTheSameReading` | 元数据块里**没有** `131.0.0.0` | ✅ |
| `VersionHasThreeSourcesInOrder` | `--version` → `FileVersionInfo` → 字面量 | `--version → FileVersionInfo → 131.0.0.0` |
| `TheRealInstalledVersionIsReadableOnThisMachine` | 实际读到的 major ≥ 100 | **`major: 157`** |

**第三条是这次的形状**：它不检查某一个值对不对，而检查**降级链存在**。
只测「值正确」的话，删掉第二来源仍然会通过——因为这台机器的 `--version` 好使。

**第四条是唯一一个真的去跑浏览器的**：它验证 `DefaultUserAgent()` 在这台机器上
能说出 157，而不是停在某个字面量。

### 验证

```
dotnet test      643 通过 / 0 失败 / 2 跳过   (+4)
live contracts   PASS
store modules    PASS 61 registered
build errors     0
```

---
