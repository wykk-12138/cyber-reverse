# 18 · 浏览器取 CT 的流量方案（执行手册）

> 这份是**怎么做**，不是**怎么测**。测量记录在 13 / 16 / 17。
> 目标：在保证 CT 有效的前提下，把单次会话的过线流量压到最低。
> 所有数字来自 CDP 的 `Network.loadingFinished.encodedDataLength` —— 真正过线的字节。

---

## 1. 一页结论

| 阶段 | 过线字节 | 请求数 | 相对不拦截 |
|---|---|---|---|
| 不拦截，正常打开商品页 | 20,570,464 | 268 | 100% |
| **L1** 拦截 42 条 | 615,690 | 61 | 3.0% |
| **L2** 拦截 + 持久 profile | ~450,000 | ~55 | 2.2% |
| **L3** 会话内复用同一 CT | 每个业务请求 +1,330~1,487 | 1 | 0.007% |

**拿一个可用 CT 的稳态成本 ≈ 450 KB**（冷启第一次 620 KB）。
省下来的 20 MB 里，没有一个字节是挑战需要的。

---

## 2. 钱花在哪（一个 CT 的账）

### 2.1 不拦截时（商品页）

```
20,570,464 字节 / 268 请求
  ├─ 商品图、Next.js chunk、字体、视频、三方脚本  ≈ 19.4 MB
  ├─ ips.js（挑战程序本体）                         ≈ 0.42 MB
  └─ 真正参与挑战的请求（/mfc /fp /tl p.js HTML）   ≈ 0.21 MB
```

### 2.2 拦截后仍会下（这是硬成本）

| 资源 | 字节 | 能不能省 |
|---|---|---|
| `ips.js?KP_UIDz=…&x-kpsdk-im=…` | 401,640 – 441,039 | ❌ 服务端每轮现生成、`no-store` |
| `p.js` | 62,894 – 64,436 | ✅ 持久 profile 后 **0** |
| 产品页 HTML | 124,210 | ✅ 持久 profile 后 **4,236** |
| `/fp` | 5,229 | ❌ 挑战本身 |
| `/tl` | 4,727 | ❌ 挑战本身 |
| `/mfc` | 4,137 | ❌ 挑战本身 |
| `checkout-index-value.js` 等 | ~1,200 | ❌ |
| 其余（typekit css、bazaarvoice overrides 等） | ~2,400 | 部分可拦截 |

**`ips.js` 占稳态成本的 93%。** 它由服务端按 `KP_UIDz` 下发，明令 `no-cache, no-store, must-revalidate`，
每轮内容不同（数值常量随机化）。这是 Kasada 的吞吐成本，不是配置问题。

---

## 3. 三层手段

### L1 · 拦截：把页面家具挡在本地

**效果：20.57 MB → 0.64 MB（−97%）**

原理：用 CDP `Fetch` 域在请求级拦截，不匹配的请求**根本不出机器**，所以零代理流量。
不是"下了再丢"，是"没下"。

**默认 42 条（`ChromiumKasadaSolver.DefaultBlockPatterns`）**：

```
图片/字体/媒体   *.png *.jpg *.jpeg *.webp *.gif *.svg *.avif *.ico
                *.woff *.woff2 *.ttf *.otf *.eot
                *.mp4 *.webm *.m3u8 *.cmfv *.cmfa *.mpd
                */video/* */video-player/*
三方分析/信标     *.nr-data.net/* *.newrelic.com/* *.demdex.net/* *.adobedtm.com/*
                *.facebook.net/* *.google-analytics.com/* *.doubleclick.net/*
                *.hotjar.com/* *.segment.io/* *.googletagmanager.com/*
                *mtrx9k*  cdn.evgnet.com/*  *.evgnet.com/*
                *.bazaarvoice.com/* *.switchgrowth.com/* *.cloudflareinsights.com/*
同意管理 SDK     *.cookielaw.org/* *.onetrust.com/*      ← 首屏 139 KB，挑战一个字节都不读
静态包/边缘信标   */static/* *_next/static/* *.chunk.*.js */cdn-cgi/*
```

**为什么 `.cmfv` / `.cmfa` 要单独列**：按格式黑名单会漏掉厂商私有扩展名（Nike 的五个视频
就是 `.cmfv`，合计 8.4 MB，占那次总流量的 63%，见 13 §2）。

**用法**：

```csharp
var solver = new ChromiumKasadaSolver();   // ReduceTraffic 默认 true，42 条自动生效
// 只想加不想减：
solver.BlockPatterns.Add("*.example.com/*");
// 想完全放开（正常打开）：
solver.ReduceTraffic = false;
```

**关键约束**：这 42 条里**没有一条会挡掉挑战**。判定标准见 §5。
如果换站后挑战解不出，第一件事是把 `ReduceTraffic` 关掉重试，确认不是拦错了东西。

---

### L2 · 持久 profile：让 `p.js` 和页面走磁盘缓存

**效果：620 KB → ~450 KB（−28%）**

```csharp
solver.ProfilePath = @"D:\profiles\arc-01";   // 固定的 user-data-dir
solver.FreshCookies = true;                    // 但清掉身份
```

两个开关必须**一起**用：

| 只给 ProfilePath | 给 ProfilePath + FreshCookies |
|---|---|
| 5,501 字节，**没有 `/tl`、没有 CT** | ~450 KB，**新 CT，`cart.get` 200** |

为什么：持久 profile 里 cookie 还有效 → 服务端认为这设备已经通过 → **不要求挑战**。
便宜，但产出零。所以必须清身份。

**`FreshCookies = true` 会同时清 cookie 与 `local_storage`/`session_storage`。**
只清 cookie 不够 —— 实测出现过"同样清法有时触发有时不触发"，差别就在页面存储
（见 16 §4.2）。要稳定触发，两样一起清。

**身份要清、缓存要留** —— 这两件事在 Chrome 里是两个不同的存储：
`Network.clearBrowserCookies` + `Storage.clearDataForOrigin` 清前者，磁盘缓存不动。

---

### L3 · 会话内复用：把 450 KB 摊到 N 个业务请求

**效果：每多一个业务请求 +1,330~1,487 字节**

一个 CT 不需要"每个请求换一个"。实测同一个 ct：

```
round 1: +1,332 bytes  submission +0  ct=01XJe84J0n0f…  cart 200 → id tgdldIan…
round 2: +1,487 bytes  submission +0  ct=01XJe84J0n0f…  cart 200 → id sQRaMjbD…
round 3: +1,330 bytes  submission +0  ct=01XJe84J0n0f…  cart 200 → id yQyIM5Fo…
```

三次 200，每次返回**不同的 cart id**，`/tl` 轮次 +0，`ips.js` +0。

⇒ **单请求成本 = 450 KB ÷ N。** 会话越长越便宜。

**所以：不要为每个业务请求换 CT。** 换 CT 的代价是 450 KB，复用一个请求的代价是 1.4 KB。

---

## 4. 拿多个 CT（当确实需要时）

**只有一条路：重启浏览器进程。**

```csharp
// 每次都是新的 Solver 实例 = 新的浏览器进程 = 新的内存状态
for (var i = 0; i < n; i++)
{
    var s = new ChromiumKasadaSolver
    {
        ProfilePath  = profileDir,   // 同一个 profile，缓存留着
        FreshCookies = true,         // 身份清掉
    };
    var r = await s.SolveAsync(pageUrl, TimeSpan.FromSeconds(60));
    // r.Ct 是新的，r.Ok && s.TlSolved 才算有效
}
```

实测三连（同一 profile，三次新进程）：

```
cycle 1: bytes=458,621  ips=438,022  pjs=0  ct=024hlrs5B2vRF7E6…  cart 200
cycle 2: bytes=444,943  ips=425,614  pjs=0  ct=0261xTr4PmO6gmyQ…  cart 200
cycle 3: bytes=460,531  ips=440,359  pjs=0  ct=021b6kTVq9oVZKBJ…  cart 200
```

**注意**：在**同一个浏览器实例内**清身份再导航是**无效**的 —— sensor 内存里还揣着那一轮的结果，
`submission +0`、`ct`/`st` 逐字不变（17 §2）。必须重启进程。

---

## 5. 判据：怎么确认拿到的 CT 是真的

三层，缺一层就可能拿到"看起来能用、实际不可用"的 token。

### 第 1 层：`/tl` 正文必须是 `{"reload":true}`

```csharp
solver.TlSolved   // 由 /tl 响应体派生
solver.TlBody     // 正文原文
```

- `200` + **空正文** = 未解出的轮次，**不可用**
- 正文不是 `reload` 标记 = 不可用
- 只有 `{"reload":true}`（15 字节）才算解出

`ChromiumKasadaSolver.Ok` 已经要求 `TlSolved`，空正文会返回失败而不是带一个废 token 成功。

### 第 2 层：`cart.get` 200

**必须在这个会话里发**，不能在 host 侧另起连接：

```
GET /api/cart.get?input={"json":{"country":"us","language":"en","viewContext":"Cart"}}
```

四个必须对的细节（每一个错了都失败，且症状各不相同）：

| 错法 | 服务端原话 |
|---|---|
| 用 POST | `Unsupported POST-request to query procedure` → 405 |
| `input` 里塞裸对象 | `invalid_type: expected object, received undefined` → 400 |
| 缺 `{"json": …}` 信封 | 同上，input 整个塌成 undefined |
| `country` 写 `"US"` | `invalid_enum_value: received "US", options ["at","be",…]` → 400 |

**负对照（必须有）**：同一条 URL 从 host 侧裸发、不带 `x-kpsdk-*`、不带 cookie → **429**。
如果负对照也 200，说明这个接口公开可读，`cart.get` 就不构成判据。

### 第 3 层（未测）：写接口的 PoW 严格校验

`cart.add` 一类 mutation 才是真正严格的门。读取宽松、写入严格 —— 这层没测过，
不要拿前两层的结果推断它。

---

## 6. 五个"看起来更省"的坑

| 做法 | 现象 | 真相 |
|---|---|---|
| **手挂 `x-kpsdk-ct`** | 429 空 body | ct 与会话绑定，手工塞的组合不自洽 → 被 WAF 拒。**不挂反而能到应用层**（16 §4.1） |
| **不清身份只复用 profile** | 5.5 KB，没有 `/tl` | 服务端不要求挑战，**产出零** |
| **只清 cookie** | 有时触发有时不触发 | 身份也在页面存储里，要一起清 |
| **缓存 `ips.js`** | 5,497 字节，挑战失败 | 服务端每轮现生成、`no-store`；旧脚本算出的答案不认（16 §3.2） |
| **轮换 profile 拿新 CT** | 625 KB/CT | 能用但**贵 175 KB**：换进程就够了，profile 可以一直用（17 §5.2） |

另外两个已作废的想法：

- **`--disk-cache-dir` 跨 profile 共享缓存**：没生效（`p.js` 仍每轮 64 KB），
  而且会把缓存搬离 profile 目录，**污染后续用同一 profile 的测量**（17 §5.1）。
- **会话内清身份 + 重导航**：不产生新挑战，`ct`/`st` 逐字不变（17 §2）。

---

## 7. 和其他路线比

| 路线 | 每 CT 流量 | 代价 |
|---|---|---|
| 正常打开（不拦截） | 20.57 MB | 无 |
| **拦截 + 持久 profile（本方案）** | **~450 KB** | 需要维护一个 profile 目录 |
| 拦截 + 轮换 profile | ~625 KB | 每个 profile 冷缓存 |
| 本地执行 `p.js`（Jint） | **省不掉** | `ips.js` 仍要从服务端取，见下 |

**为什么本地执行省不了 `ips.js`**：`p.js`（65 KB）只是引导与协议框架，真正的挑战程序是
`ips.js`（未压缩 809,554 字节，`KPSDK.scriptStart=KPSDK.now()` 开头），由服务端按 `KP_UIDz`
现生成、每轮数值常量随机化。本地跑 `p.js` 照样会请求并执行它；想跳过只能复刻那 809 KB 的算法，
而它每轮都换，没有固定算法可复刻（16 §7.3）。

---

## 8. 完整配置清单

### 8.1 生产代码

```csharp
using var solver = new ChromiumKasadaSolver
{
    ProfilePath  = profileDir,        // 固定的 user-data-dir，跨轮复用
    FreshCookies = true,              // 每轮清身份（cookie + 页面存储）
    // ReduceTraffic = true,          // 默认就是 true，42 条拦截生效
    // KasadaHeadless = false,        // 默认有窗；headless 会加一堆自己的信号
    // KasadaStealth  = false,        // 默认不注入；参考实现什么都不注入
};

var r = await solver.SolveAsync(pageUrl, TimeSpan.FromSeconds(60));

if (!r.Ok || !solver.TlSolved)
    return;                        // 空正文/非 reload → 不要这个 token

var ct = r.Ct;                     // 可用
var st = solver.LastRoundtrips
            .LastOrDefault(x => x.Url.EndsWith("/tl"))
            ?.ResponseHeaders.GetValueOrDefault("x-kpsdk-st");
var receivedAt = solver.ReceivedAtMs;   // 浏览器 Date.now() 收到 /tl 的时刻
```

### 8.2 三个必须遵守的时序约束

1. **挑战期间不要探测页面。** 参考实现的 harvest 循环只做 `recv`，什么都不 evaluate。
   曾经每 250 ms `Runtime.evaluate` 一次，就是它让 `/tl` 回空正文。**我们的实现里没有这个循环。**
2. **`received_at_ms` 用浏览器的 `Date.now()`**，不是主机时钟。后者会把两台机器的时钟差
   当成时延注进 PoW 的 `workTime`。
3. **token 只能在它自己的会话里花。** cookies、client hints、TLS/HTTP2 指纹都在那个浏览器里，
   profile 一关就没了。要用就在 `AfterSolveAsync` 钩子里用，出了 `SolveAsync` 就来不及了。

### 8.3 分析工具（`analysis/kasada-live`）

```powershell
$env:DOTNET_ROOT = 'D:\tools\dotnet8'
$dll = 'analysis\kasada-live\bin\Release\net8.0\kasada-live.dll'

# 单轮 + 完整拆解
& D:\tools\dotnet8\dotnet.exe exec $dll --browser

# 连跑 N 轮（第一轮冷，之后 p.js = 0）
$env:KASADA_CYCLES  = '3'
$env:KASADA_PROFILE = (Join-Path (Get-Location) '.tmp-profile')
& D:\tools\dotnet8\dotnet.exe exec $dll --cycles
```

| 环境变量 | 作用 | 默认 |
|---|---|---|
| `KASADA_PAGE` | 目标页 | `https://arcteryx.com/us/en/shop/X000009417` |
| `KASADA_STORE` | 站点键 | `arcteryx` |
| `KASADA_PROFILE` | 持久 profile 目录 | 无（每轮临时） |
| `KASADA_FRESH` | `1` = 清身份 | — |
| `KASADA_CYCLES` | 连跑轮数 | 5 |
| `KASADA_ROTATE` | `1` = 每轮独立 profile | — |
| `KASADA_SESSION` | `1` = 同一浏览器内多轮（用于证明它无效） | — |
| `KASADA_CART_URL` | 判据接口 | `https://arcteryx.com/api/cart.get` |
| `KASADA_BLOCK` | 追加拦截（逗号分隔） | — |

### 8.4 看哪几行

```
wire bytes (CDP loadingFinished) = 445,460 across 55 requests   ← 总流量
requests dropped locally = 39                                   ← 本地挡掉多少
TlSolved = True   TlBody = [{"reload":true}]                    ← 判据第 1 层
G in-page GET {"json":...} : status=200 len=448                 ← 判据第 2 层
largest responses:                                              ← 钱花在哪
     438,022  .../ips.js?KP_UIDz=…
```

---

## 9. 边界与未验证

- **`ips.js` 的复用边界未知**：一份 `ips.js` 能支撑同一会话里多少次受保护请求、能撑多久。
  只知道 3 次以内不复取（17 §3）。
- **写接口那一层没测**：`cart.add` 一类 mutation 的严格性未验证，判据只到读取。
- **429 的成因未定**：已排除"CT 老化"（同一 ct 连打多次全 200），
  剩下频率、并发、请求节奏几个方向。要定位需要一份能复现 429 的节奏参数。
- **拦截表是按 Nike / Arcteryx 量的**，换站要重测。判定方法是把 `ReduceTraffic` 关掉跑一次，
  确认挑战在两种配置下都能解出；如果不能，先查是不是拦掉了挑战依赖的资源。
- **压缩率随页面变化**：Arc 的 checkout 页本身只有 1.59 MB，拦截只降 18%（13 §5）；
  商品页 20.57 MB，降 97%。**入口页选轻的，正常打开的成本本身就小一个数量级。**

---

## 10. 重算依据

| 文档 | 内容 |
|---|---|
| 13 | 首次测量的三档结果、Nike 五个视频占 63%、拦截表来源 |
| 15 | `cart.get` 200 的达成过程、三层请求错误、手工挂 ct 反而 429 |
| 16 | 435 KB vs 615 KB vs 20.57 MB、`ips.js` 身份、"80 KB" 撤回 |
| 17 | 会话内 vs 换进程的边界、5 个 CT 的实测、共享缓存无效 |

所有数字都能用 §8.3 的命令重跑。文档里不保留无法重算的数。
