# 03 · 方案二：真浏览器里跑 `ips.js`

> **一句话**：别管脚本怎么算，把页面加载起来，让它自己算，然后**从线上把结果捞出来**。
> token 不需要"逆"出来 —— 它一定会出现在脚本发出的下一个请求的请求头里。

---

## 1. 原版的做法（[Obs]）

| 证据 | 地址 | 说明 |
|---|---|---|
| `DotNetBrowser` | `0x14315a15d` | 商业 .NET Chromium 封装 |
| `DotNetBrowser.Core.dll` / `.AvaloniaUi.v12.dll` / `.Wpf` / `.WinForms` / `.Logging` | `0x14315a227` 一带 | 完整程序集族 |
| `DotNetBrowser.Core, PublicKey=0024…4DE6542CDB387F36…` | `0x1431684f1` | 强名公钥，可反查版本 |
| `ChromiumBinariesExtractor` | `0x1432bb1c5` | **自带浏览器二进制并解压** |
| `ChromiumPackage` / `ChromiumProfiles` / `ChromiumIndex` / `ChromiumFile` | `0x143257d07` 一带 | 版本管理与 profile 管理 |
| `EngineInitializationException` / `ChromiumBinariesMissingException` / `ConnectionClosedException` | `0x14329cc15` | 初始化失败面 |
| `.cybersole-chromium.xml` | `0x14336a99f` | **本机标记文件**：解压过就靠它认 |
| `get_ChromiumRoot` / `get_LegacyFolder` / `get_ChromiumDirectory` / `set_ChromiumDirectory` | `0x14336ae83` | 目录布局 |

`replica/docs/FUNCTION_PARITY.md` 记的版本是 **DotNetBrowser 4.3.5**。

**这套东西的定位**：它既给 UI 内嵌浏览器（登录、人工接管），也给"Jint 跑不动的站点"兜底。
所以产物里同时有 Jint 与 Chromium **不是矛盾** —— 是两条并存的路（02 §1 已给 Jint 的独立证据）。

---

## 2. 零依赖替代：手写 CDP 客户端

如果你的项目不想背一个商业组件，用**机器上已装的 Chrome/Edge** + CDP 能达到同样效果。骨架：

```csharp
// 1) 启动：headless=new + 独立 profile + 调试端口
var psi = new ProcessStartInfo(chromePath)
{
    Arguments = $"--headless=new --remote-debugging-port={port} " +
                $"--user-data-dir=\"{tempProfile}\" --no-first-run --disable-gpu",
    UseShellExecute = false,
};
var proc = Process.Start(psi)!;

// 2) 附着：拿 webSocketDebuggerUrl
var json = await http.GetStringAsync($"http://127.0.0.1:{port}/json/list");
var wsUrl = JsonDocument.Parse(json).RootElement[0].GetProperty("webSocketDebuggerUrl").GetString()!;
var ws = new ClientWebSocket();
await ws.ConnectAsync(new Uri(wsUrl), ct);

// 3) 导航到**真实 https 页面**（不是 about:blank，见 §3）
await Send("Page.navigate", new { url = pageUrl });
```

要点：

| 环节 | 关键点 |
|---|---|
| 启动 | `--headless=new`（旧 headless 指纹更差）；profile 用**临时目录**，用完删 |
| 附着 | `/json/list` → `webSocketDebuggerUrl` → `ClientWebSocket` |
| 求值 | `Runtime.evaluate` + `returnByValue: true` |
| **嗅探** | 保留 `Network.requestWillBeSent` 事件，从 `request.headers` 里捞 `x-kpsdk-*` |
| 清理 | 关 socket → 杀进程树 → 删 profile |

---

## 3. 嗅探法：token 从哪里来

这是整个方案的核心技巧，也是最容易做错的一步。

```csharp
// 打开 Network 域
await Send("Network.enable", new { });

// 脚本算出 token 后会带着它发请求；我们只需要听
foreach (var ev in events)
{
    if (ev.Method != "Network.requestWillBeSent") continue;
    var headers = ev.Params.GetProperty("request").GetProperty("headers");
    foreach (var name in new[] { "x-kpsdk-ct", "x-kpsdk-cd", "x-kpsdk-v", "x-kpsdk-st" })
        if (headers.TryGetProperty(name, out var v))
            captured[name] = v.GetString();
}
```

**为什么这条路对"现代构型"仍然有效**：现行 Nike 的 `KPSDK` 对象只暴露 `configure`/`isReady`，
`ct()` 之类的导出名已经不存在 —— 但脚本**必须**把 token 挂到请求上，否则站点自己就没法验签。
**所以导出名会消失，线上头部不会。**

> 这条经验可以推广：**当前端把能力藏起来时，从"它必须消费自己的产出"的那个边界上去观察。**

---

## 4. body 加密（`x-kpsdk-cd`）

`x-kpsdk-cd` 是 client data，用于把请求体加密。它**只在与产出它的那份脚本上下文一致时才对**。

所以：
- 你**不能**用 Jint 产一个 `ct`，再用浏览器产一个 `cd`；
- 也不能把 A 窗口的 `cd` 用到 B 窗口的 body 上。

**同一次会话内完成"生成 → 加密 → 发送"**，是这个方案比 Jint 更稳的地方：三者天然在同一上下文里。

---

## 5. 三个必须知道的坑

### 5.1 `about:blank` / `data:` 起手会失败

`crypto.subtle` 只在**安全上下文**（https、localhost、127.0.0.1）存在。
用 `about:blank` 起手，`subtle` 是 `undefined`，Kasada 立刻挂。
→ **必须先导航到真实的 https 页面**（或本地 loopback origin）。

### 5.2 headless 的 UA 会直接暴露

headless Chrome 的 UA 带 `HeadlessChrome/157.0.0.0`。真站点可能直接拒。
→ 覆盖 UA（`Network.setUserAgentOverride`）只是第一层；还有 `navigator.webdriver`、
`navigator.plugins.length`、WebGL vendor/renderer、字体列表等。
→ **原版能过是因为它用真实 Chromium 的完整指纹**（DotNetBrowser 是完整内核，不是精简壳）。

### 5.3 有站点会 403 掉"全新 headless 会话"

实测记录：`goat.com` 与 `scheels.com` 都 403 掉默认 headless 启动，换成**带头像目录的普通窗口**才过。
→ 所以 solver 要允许"有头 + 持久 profile"这个降级档。

---

## 6. 什么时候选这个方案

| 场景 | 选 |
|---|---|
| 站点只要 `x-kpsdk-ct`，Jint + shim 能跑完 | 02（内存低一个数量级） |
| 脚本用到 WebGL / Worker / WebRTC 等无法托管模拟的 API | **03** |
| 需要 `cd` 加密 body | **03** |
| 站点把 Kasada 与 TLS/HTTP2 指纹绑定 | **03**（但仍要自己的传输层，浏览器只负责算 token） |
| 只是探不到导出名 | 不是理由 —— 用 §3 的嗅探法 |

---

## 7. 复算

```powershell
python analysis\ida.py str DotNetBrowser --limit 60      # total >= 12
python analysis\ida.py str Chromium      --limit 60      # 含 Extractor / Profiles / Package
python analysis\ida.py str cybersole-chromium --limit 5  # .cybersole-chromium.xml
```
