# 14 · 对照 arcbot 的本地采集实现：我们缺什么

读了 `D:\projects\arcbot`（YG 的 Rust 主线）的本地采集路径，把它和复刻件的
`ChromiumKasadaSolver` 逐项对照。**这份记录只讲 browser 取 ct 这一条链，不碰其余模块。**

来源文件（都是只读）：

- `rust/src/harvest/worker.rs` —— 本地采集 worker
- `rust/src/harvest/protocol.rs` / `cdp.rs` / `proxy_bridge.rs`
- `docs/ct-source.md` §"`/fp` 与 `/tl` 的接受条件"

---

## 1. 他们只有四个静态参数，我们加了两个

`rust/src/harvest/worker.rs` 原文：

```rust
const CHROME_STATIC_ARGS: [&str; 4] = [
    "--remote-allow-origins=*",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-blink-features=AutomationControlled",
];
```

而且注释写得很硬：

> `--disable-blink-features=AutomationControlled` is load-bearing: opening a DevTools port otherwise
> makes Chrome advertise `navigator.webdriver === true`, and the Kasada challenge then refuses to
> solve (HTTP 200 with `x-kpsdk-cr: true` and an empty body). … **No automation-enabling switch may be
> added here.**

**复刻件的 `ChromiumBridge` 原来有两处与这条直接冲突：**

| 我们的写法 | 问题 |
|---|---|
| `if (!headed) args.Add("--enable-automation");` | **正是上面禁止的那个开关**，而且 headless 时才加 —— 最不该加的时候加 |
| `--exclude-switches=enable-automation` | 与上一行自相矛盾，且不起作用 |

**已删除。** 现在两种模式下都不加任何自动化开关。

## 2. 他们只开两个 CDP 域

```rust
/// The Runtime domain is deliberately absent. Kasada detects a debugger that has
/// enabled it and then refuses to solve the challenge…
const CDP_SETUP_METHODS: [&str; 2] = ["Network.enable", "Page.enable"];
```

**复刻件原来开三个**（`Page` / `Runtime` / `Network`），`Runtime.enable` 上一轮已移除
（`13-traffic.md` §9.3），这一轮对照确认了那处改动的依据就是这段注释。

## 3. 他们跑带窗口的浏览器，我们默认 headless

`CHROME_STATIC_ARGS` 里没有任何 `--headless`，`process/harvest.rs` 走的是正常窗口 +
本地 `ProxyBridge`。

**复刻件原来 `LaunchAsync(headed: false)` 是默认值。** 已改成默认 headed
（`ChromiumKasadaSolver.KasadaHeadless` 可切回）。

## 4. 他们不注入任何 stealth 脚本

在整个 `rust/src/harvest/` 里搜 `addScriptToEvaluateOnNewDocument` / `Page.addScript`，
**一处都没有**。他们靠的是"不做奇怪的事"，不是"把 `navigator` 改得像真的"。

**复刻件的 `ApplyStealthAsync` 会重写一整套浏览器表面。** 每一处重写都是一处
与真浏览器的差异，也就都是可检测点。已改成默认不调用
（`ChromiumKasadaSolver.KasadaStealth` 可开回）。

## 5. 他们必走代理，我们直连

`worker.rs` L514 / L539：

```rust
let bridge = super::proxy_bridge::ProxyBridge::start(bridge_spec, target, stop.clone())…
"--proxy-server={}://{}:{}",
```

**每个采集会话都经由本机 ProxyBridge 走真实代理。** 复刻件这边直连 ——
机房出口本身就是一类信号。

**这一条我没有改**，因为复刻件的浏览器路目前不接受代理参数，
而且这需要先确认出口到底有多大影响。

## 6. YG 的流程纠正：**必须先进首页，不能直接进 checkout**

此前我一直直接打 `https://arcteryx.com/us/en/checkout`。**这是错的。**
改成 `https://arcteryx.com/` 之后：

```
Ok      = True
Ct      = 0aEH2Vgwl83PaudqYRs1Sl27on4tJxMaY6wJcDF9l9mzH6hW33kkdB5tXgVXzPDxPBPPaVTGSmzOqqgyDsg8KSyJZK1BS2uJG7QF
wire bytes = 3,168,788 / 93 请求
```

**直接进 checkout 除了流程不自然，还可能是那一页本身就需要购物车状态。**

## 7. 仍然没解决的：`/tl` 正文读不到

```
TlSolved = False   TlBody = (null)
cart.get bare=429(0b) token=429(0b)
```

**注意 `TlBody` 是 `null` 而不是 `""`** —— 这是"读不到"，不是"空正文"。
`ResponseBodyAsync` 用 `Network.getResponseBody` 在轮询循环里读，返回 null 说明
要么 requestId 匹配错（比如匹配到了预检请求），要么 CDP 已经丢弃了响应体。

**在读到它之前，无法判断那一轮到底解出没有。** 这也是与 §13 里
"空正文"说法的一个修正：Arc 上我看到的 `[]` 来自旧代码路径，当前是 `null`。

## 8. 这轮改了什么

| 文件 | 改动 |
|---|---|
| `ChromiumBridge.cs` | 删 `--enable-automation` 与 `--exclude-switches=enable-automation` |
| `ChromiumKasadaSolver.cs` | 默认 headed（`KasadaHeadless` 可切）；stealth 默认关闭（`KasadaStealth` 可开） |

**测试**：本轮改动后 Kasada/Chromium 套件仍全绿（见提交信息）。

## 9. 我没有验证的

- **改完这四项之后 `/tl` 是否真的返回 `{"reload":true}`** —— 读不到正文，所以不知道。
- **代理**：没给浏览器路接代理，也没做有无代理的对照。
- **他们 `--remote-allow-origins=*`** 我们没加；不确定是否必要。
- **他们的 `proxy_bridge` 处理 SOCKS5h 与认证 HTTP 代理的细节**没读。

---

## 10. CD 只需要三个值 —— 我之前说"输入拿不到"是错的

`rust/src/provider/local_cd.rs` 把 CD 做成了产品代码，`sign_bundle(bundle, runtime_suffix)` 的输入是：

```rust
let ct  = bundle.get("x-kpsdk-ct");        // 字符串
let st  = bundle_number(bundle, "x-kpsdk-st");       // 数字
let rst = bundle_number(bundle, "received_at_ms");   // 数字
```

**只有这三个。** 我是因为以为要从 fc / p.js 里取参数才卡住的：

```rust
/// Deployment suffix verified for the current Arc p.js version.
pub const DEFAULT_RUNTIME_SUFFIX: &str =
    "c7a30a9618c37908599dc69b67703a2b09eaf9c9b88973c5fb521f36eb0e4bd0";

const DIFFICULTY: f64 = 77.0;
const SUBCHALLENGE_COUNT: usize = 4;
const SEED_SUFFIX: &str = "melt-u-bot";
```

**`runtimeSuffix` 是常量，PoW 的三个参数也是常量**（`fc` 用 `ordinary::DEFAULT_FC`，它编码的正是
`{"difficulty":77,"subchallengeCount":4,"seedSuffix":"melt-u-bot"}`）。

**⇒ 不需要解 p.js 取 runtimeSuffix，也不需要服务端下发 `cryptoChallenge`。**
§13 §9.1 里"三份输入拿不到"的结论，作废。

真正需要的只有 **`ct` + `st` + 本机收到 st 的时刻**，这三个浏览器都能给。

---

## 11. 我一直在瞎试，真正的缺陷在事件采集

`worker.rs` 的核心循环长这样：

```rust
fn recv(&mut self, stop, timeout) -> Result<Option<InputValue>, WorkerError> {
    let Some(raw) = self.socket.recv_timeout(timeout)? else { return Ok(None) };
    ...
    if let Some(event) = capture_event(&message) {
        self.record(event);          // ← 每一条消息都过这里，事件不会漏
    }
}
```

而 `await_first_tl` 是**主动阻塞等**第一个 `/tl` 请求出现并完成：

```rust
loop {
    if let Some(request_id) = self.first_tl.as_ref().filter(|_| self.first_tl_finished) {
        return Ok(request_id.clone());
    }
    let _ = self.recv(stop, ...)?;
}
```

**复刻件的 `ChromiumBridge` 不是这个结构。** 它只有 `SendAsync` 一个读点 ——
**只有当有人发命令时才会从 socket 读消息**。`EvaluateAsync` 的轮询会顺带读到一些事件，
但 `/tl` 的 `responseReceived` 恰好发生在那两次轮询之间时，就**没人读、事件被丢**。

所以我的 trace 里 `/tl` 显示成：

```
** POST …/tl -> 0 (200…
```

**`Status = 0` 不是"服务端返回 0"，是这条 `responseReceived` 根本没进 `Events`。**
连带后果：

- `TlBody` 读不到（`ResponseBodyAsync` 要靠 requestId 找，找不到 → null）
- `x-kpsdk-st` 看不到（它就在那条丢失的响应的头里）
- CD 算不出来（缺 st）

**这才是这台机器上真正少的东西 —— 不是参数，是读循环。**

**我前面几轮调 `--enable-automation`、headless/headed、stealth、拦截表，都是在参数上试，
而数据在采集阶段就漏掉了。** 这一点 YG 说"不要瞎试"是对的：
应该先把这个读循环照抄过来，再谈参数。

## 12. 下一轮该做的（照抄，不试）

1. `ChromiumBridge` 增加一个**常驻读循环**：一个后台任务持续 `socket.ReceiveAsync`，
   把每条消息按 `requestId` 索引进 `Events`；`SendAsync` 只负责发命令并按 id 等回复。
2. `await_first_tl` 等价物：阻塞等第一个 `/tl` 的 `requestWillBeSent` + `loadingFinished`，
   拿到 requestId 后立刻 `Network.getResponseBody` 读正文，判 `reload`。
3. 拿到 `st` 和本机接收时刻，用 `DEFAULT_RUNTIME_SUFFIX` + `DEFAULT_FC` 那组常量签 CD。
4. 用 `ct` + CD 打 `cart.get`。

**在这四步做完之前，不再动任何 Chrome 参数。**
