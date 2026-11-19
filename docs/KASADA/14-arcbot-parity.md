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

---

## 13. 接着读完了实现，改了三处 —— 但 `/tl` 的 body 只有 200 字节

YG 指出我读一半就开干、而且不该急着关窗口。这两条都成立，下面是补上的部分。

### 13.1 他们等 `/tl` 完成，不是等第一个 token

```rust
const LISTEN_TIMEOUT:  Duration = Duration::from_secs(60);
const RECV_TIMEOUT:    Duration = Duration::from_secs(2);
const WORKER_DEADLINE: Duration = Duration::from_secs(80);
```

`await_first_tl` 阻塞到那条请求 `loadingFinished`，然后才读 body 判 `reload`。
**复刻件原来是"嗅到 `x-kpsdk-ct` 就 break"** —— 也就是挑战还没算完就把窗口关了。
已改成等 `FirstTlFinished()`（新增在 `ChromiumBridge` 上）。

### 13.2 他们只有一个 reader

`Cdp::recv` 是唯一读点，每条消息都过 `record`。复刻件的 `SendAsync` 是唯一读点，
**两次命令之间没人读 socket** —— `/tl` 的响应恰好落在那里就丢了，连带 body 和 `st`。

已改成：后台 `ReadLoopAsync` 独占 socket，命令回复按 id 交给等待者，通知全部进 `Events`；
`Events` 加了锁（读循环写、调用方读）。

### 13.3 bundle 里装的是什么

`rust/src/harvest/candidate.rs` 的 `build_kasada`：

```
x-kpsdk-ct, x-kpsdk-st, x-kpsdk-v,
user-agent, sec-ch-ua, sec-ch-ua-platform,
x-kpsdk-h（缺省 DEFAULT_KPSDK_H）, sec-ch-ua-mobile（可选）
```

**CD 用到的只有前两个 + `received_at_ms`**（§10），其余是业务请求头。

### 13.4 仍然卡住的地方：`/tl` 的请求体只有 200 字节

改完之后跑产品页 `https://arcteryx.com/us/en/shop/X000009417`：

```
POST …/tl -> status=0  body=200 字节
tl st = (absent)
TlBody = (null)
Ok = True, Ct = 0aEnKt0rZ1…
```

**`status=0` 表示那条 `responseReceived` 仍然没到；`body=200` 是关键** ——
arcbot 的记录里 `/tl` 的请求体是 **25,618 字节**，我们只有 200。

**⇒ payload 根本没进入计算阶段，发出去的是个空壳。**

这才是现在的真问题：不是读不到，是没东西可读。

**我这轮没解决它。** 下一步要查的是"为什么 payload 不算" ——
按 §12 的纪律，先对比同一页面在他们那边是否也算不出来，而不是继续调参数。

## 14. 这轮改了但没验证到收益

| 改动 | 状态 |
|---|---|
| 等 `/tl` 完成而非首个 token | 已改，`/tl` 仍未收到响应 |
| 单读者 + 事件加锁 | 已改，`/tl` 的 `responseReceived` 仍缺 |
| 删 `--enable-automation`、默认 headed、stealth 关 | 已改，token 仍能拿到 |

**三处改动都是按他们的实现照抄的，方向对，但都没能改变 `/tl` 的结果。**
说明还缺一个更前面的条件 —— 请求体只有 200 字节这件事指向 payload 没有真正运行计算。

---

## 15. 完整流程（`run_with_browser` + `run_worker` + `Cdp::harvest` 全读完了）

前面几轮我确实只读了一半就动手。这一节是把整条链一次性列出来，下一轮照这个抄，
不再在参数上试。

### 15.1 外层：`run_with_browser`（worker.rs L242–387）

```
1. effective_target_url(&options, request.target_origin)
2. prepare_proxy(proxy, target)  -> (proxy, bridge, chrome_proxy)
3. profile：给了就用，没给就新建临时目录（unix 下 chmod 0700）
4. deadline = started + WORKER_DEADLINE (80s)
5. run_worker(...) -> port
6. 【硬检查】若成功但 !bridge.target_seen()  -> ProxyRouteUnconfirmed（视为失败）
7. cleanup: 杀 chrome 子进程 -> 删临时 profile -> 记录 cleanup_complete
8. 组装 envelope 并写文件；判据是 run_worker 的结果
```

**第 6 条是我之前完全没做的：代理必须证明它确实把请求送到了目标，否则整轮算失败。**
envelope 里 `chrome.headed` 明确写 `true`。

### 15.2 内层：`run_worker`（worker.rs L553–653）

```
1. build_chrome_command(chrome_path, profile, requested_port=0, chrome_proxy)
     静态参数只有四个：
       --remote-allow-origins=*
       --no-first-run
       --no-default-browser-check
       --disable-blink-features=AutomationControlled
     加上 --user-data-dir / --remote-debugging-port / --proxy-server
     【没有任何 --headless，没有任何自动化开关】
2. spawn（unix 下 setpgid，把 Chrome 放进自己的进程组便于整组清理）
3. wait_for_debug_port(version_timeout=30s, version_poll=400ms)
4. list_tabs(port) -> 找 type == "page" -> webSocketDebuggerUrl
5. connect_with_stop(ws)
6. Cdp::new(socket, target_origin_or_target_url, receive_timeout=2s)
7. for method in ["Network.enable", "Page.enable"] { cdp.call(method) }
     【Runtime 域故意不开】
8. cdp.call("Page.navigate", { url: options.target_url })
9. cdp.harvest(stop, listen_deadline=min(now+60s, deadline), deadline, capture)
10. 无论成功失败：Page.stopLoading（限 2 秒）
11. capture.events = cdp.events（把事件留给外层判定）
```

### 15.3 核心：`Cdp::harvest`（worker.rs L686–737）

```
1. request_id = await_first_tl(listen_deadline)      ← 阻塞轮询 recv，直到该 requestId 的
                                                       loadingFinished 或 loadingFailed 出现
2. round = tl_round(events, request_id)
3. if round.loading_failed           -> TlBodyUnavailable
4. if round.status is None           -> TlPairingFailed
5. if status in {403, 429}           -> TlRateLimited
6. if status != 200                  -> ChallengeRefused
7. body = response_body(request_id)  ← Network.getResponseBody
8. if body.is_empty()                -> ChallengeRefused          【空正文 = 拒绝】
9. if !reload_true(body)             -> UnexpectedTlBody          【必须是 {"reload":true}】
10. 循环重取 tl_round，直到能从同一 requestId 的事件里凑出完整 candidate + received_at_ms
```

### 15.4 `Cdp::recv` —— 唯一读点（worker.rs L741–762）

```
socket.recv_timeout(timeout)
  -> 解析 JSON
  -> capture_event(message) 若是 network 事件则 record()
  -> 返回消息本身（给 call 匹配 id）
```

**`record` 同时负责：记下"第一个 `/tl` 请求"的 requestId，以及它的 loadingFinished 是否已到。**

### 15.5 bundle 从 `/tl` 的头里取（candidate.rs L374–416）

必需键（`SUCCESS_REQUIRED_KEYS`）+ 可选：

```
x-kpsdk-ct, x-kpsdk-st, x-kpsdk-v,
user-agent, sec-ch-ua, sec-ch-ua-platform,
x-kpsdk-h（缺则 DEFAULT_KPSDK_H）, sec-ch-ua-mobile（可选）
```

CD 另需 `received_at_ms`（本机收到那条 `/tl` 响应的时间），
`runtimeSuffix` 与 PoW 三参数用常量（§10）。

## 16. 复刻件现在缺的，按上面的清单逐条

| # | 他们的做法 | 复刻件现状 |
|---|---|---|
| 1 | 目标 URL 是商品页 | 现在能传，我最后用的就是 YG 给的 PDP |
| 2 | 走 `ProxyBridge`，且 `target_seen()` 为成功前置 | **完全没做**：直连，也没有路由确认 |
| 3 | 四个静态参数，无 headless、无自动化开关 | 已对齐 |
| 4 | 只开 `Network.enable` + `Page.enable` | 已对齐 |
| 5 | 导航后阻塞等第一个 `/tl` 的 finished | 已加 `FirstTlFinished()`，但 `/tl` 的请求体只有 200 字节 |
| 6 | 读 body，空则拒，非 `reload:true` 则拒 | 有 `TlBody`/`TlSolved`，但因 5 卡住读不到 |
| 7 | 从 `/tl` 头取 6 个必需键 | 取了，但同样依赖 5 |
| 8 | 单 reader | 已改 |
| 9 | 总预算 80s、等 `/tl` 60s、recv 2s | 复刻件是 60s 一把梭，没有分段 |

**最关键的两条缺口是 #2（代理 + 路由确认）和 #5 背后那个"请求体只有 200 字节"。**
前者完全没做；后者说明 payload 没进入计算 —— 而按他们 §13.1 的注释，通常就是
`navigator.webdriver !== false` 或 `Runtime.enable` 已经开过，这两处复刻件现在都对齐了，
**所以下一步应当先补代理，再复测**。

## 17. 下一轮做什么（照抄，不再试参数）

1. 给 `ChromiumKasadaSolver` 接代理：`--proxy-server=http://127.0.0.1:{bridgePort}`，
   并在导航后确认目标确实被访问过（等价 `target_seen()`），否则整轮判失败。
2. 补齐时间预算：总 80s、等 `/tl` 60s、每次 recv 2s、读 body 5s。
3. 复测产品页，看 `/tl` 的请求体是否从 200 字节涨到 KB 级、正文是否 15 字节 `{"reload":true}`。
4. 拿到 `ct` + `st` + `received_at_ms` 后签 CD，再打 `cart.get`。
