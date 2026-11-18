# 13 · 把浏览器路的代理流量压下来（实测 13.3 MB → 0.8 MB）

跑真实浏览器取 Kasada token 时，**页面加载本身就是账单**。这份记录是实测出来的，
包括哪些请求在吃流量、能压到多少、以及压完之后什么还成立。

---

## 1. 基线：一次取 token 花 13.3 MB

用 `ChromiumKasadaSolver` 打 `https://www.nike.com/`，按 CDP 的
`Network.loadingFinished.encodedDataLength` 统计真实过线字节：

```
roundtrips = 256
wire bytes = 13,328,651
requests dropped locally = 0
```

**13.3 MB / 256 个请求。**

> 注意：不能用 `content-length` 求和。chunked 响应没有这个头，
> 按它算会得到 21 MB —— 那是**重复计数**，不是真实流量。

## 2. 钱花在哪：五个视频文件占了 63%

按 URL 分组（这个能力现在是 `ChromiumKasadaSolver.WireBreakdown`）：

```
3,458,932  assets.nmp.nike.com/video/…video_2_000000001.cmfv
1,898,935  assets.nmp.nike.com/video/…video_3_000000001.cmfv
1,627,312  assets.nmp.nike.com/video/…video_3_000000001.cmfv
1,260,442  assets.nmp.nike.com/video/…video_4_000000001.cmfv
  385,716  …/{uuid}/{uuid}/            ← 传感器脚本，必须留
  210,337  www.nike.com/mtrx9k/…       ← GTM
  186,110  www.nike.com/               ← 页面本身
```

**5 个 `.cmfv` 合计约 8.4 MB。**

**第一次拦截没拦住它们** —— 我的列表里有 `*.mp4` / `*.webm`，
但 Nike 用的是私有扩展名 `.cmfv` / `.cmfa`。**按扩展名做黑名单会漏。**

**正确做法：按域名和路径拦**（`assets.nmp.nike.com/*`、`*/video/*`）。

## 3. 三档实测结果

同一台机器、同一个站点、每次都确认拿到了 token：

| 档 | 拦什么 | 流量 | 请求数 | 降幅 | token |
|---|---|---|---|---|---|
| 基线 | — | 13,328,651 | 256 | — | ✅ |
| 保守 | 图片/字体/媒体扩展名/分析域 | 2,625,745 | 185 | **−80%** | ✅ |
| 激进 | 再拦 GTM、`/static/*`、`_next/static`、`*.chunk.*.js`、CDN 探针 | **805,335** | 58 | **−94%** | ✅ |

**激进档在 Nike 上 0.8 MB 就出了 token**，和基线那个 token 是同一类东西（服务端签发）。

## 4. 可复用的拦截表

```csharp
var block = new[]
{
    // 图片 / 字体 / 媒体（含私有扩展名，Nike 用 .cmfv / .cmfa）
    "*.png","*.jpg","*.jpeg","*.webp","*.gif","*.svg","*.avif","*.ico",
    "*.woff","*.woff2","*.ttf","*.otf","*.eot",
    "*.mp4","*.webm","*.m3u8","*.ts","*.cmfv","*.cmfa","*.mpd",
    "*/video/*","*/video-player/*",
    // 第三方分析与上报
    "*.nr-data.net/*","*.cdndex.io/*","*.demdex.net/*","*.adobedtm.com/*",
    "*.facebook.net/*","*.google-analytics.com/*","*.doubleclick.net/*",
    "*.hotjar.com/*","*.segment.io/*","*.googletagmanager.com/*",
    // 标签管理器与静态分块（激进档，实测不影响 token）
    "*mtrx9k*","*/static/*","*_next/static/*","*.chunk.*.js",
    "*/cdn-cgi/*","*.cloudflareinsights.com/*",
    "*.bing.com/*","*.tiktok.com/*","*.pinterest.com/*","*.snapchat.com/*",
};

solver.BlockPatterns.AddRange(block);   // 在 LaunchAsync 之后、NavigateAsync 之前自动安装
```

**实现方式是 `Network.setBlockedURLs`**，不是 `Fetch` 拦截。
原因写在代码注释里：`Fetch` 要求逐请求回答 `Fetch.requestPaused`，
而这个类的事件循环持有发送闸门 —— 在里面回消息会死锁。`setBlockedURLs`
是浏览器自己丢，不需要回答，效果一样且没有这个风险。

## 5. Arcteryx 上同样有效

```
不拦截： wire bytes = 1,592,886 / 65 请求
拦截后： wire bytes = 1,302,494 / 72 请求（20 个本地丢弃）
```

Arc 的 checkout 页本来就比 Nike 首页轻（1.6 MB vs 13.3 MB），所以降幅只有 18%，
但 **token 照样拿到**（`Ok = True`）。

## 6. ⚠️ 压流量的代价：没有

**token 在每一档都拿到了。** 这一点必须说清楚，因为直觉上"拦资源会破坏指纹"——
**在这两个站点上没发生。**

但**这并不证明拦得越多越安全**。`_next/static/*` 和 `*.chunk.*.js` 是页面自己的应用代码，
我在这两个站点上拦了没出问题，**换站点可能就有问题**（某些站点的指纹采集依赖应用 JS）。
**保守档（−80%）是更安全的默认，激进档要按站点验。**

## 7. ⚠️ 这轮同时暴露了一个更深的问题：`cart.get` 仍然 429

拿到 Arc 的 token 之后，我按交接包的判据打了一次 `cart.get`：

```
不拦截基线：  cart.get bare=429(0b)  token=429(0b)
拦截激进档：  cart.get bare=429(0b)  token=429(0b)
```

**两档都 429，而且负对照也是 429。**

**⇒ 这不是拦截造成的**，是 `ChromiumKasadaSolver` 拿到的 token 本身过不了 `cart.get`。

浏览器 trace 显示页面**自己**发了一次 `cart.get`，用的 ct 和我们 probe 用的是同一个：

```
POST /tl          req ct=09cyTz2T…  ->  res ct=0EKj5hiZ…
req x-kpsdk-ct: 0EKj5hiZ…            ← 后续所有请求都用它，包括页面自己的 cart.get
```

**所以 ct 是对的，缺的是别的东西** —— 最可能是 cookie 和 CD。我的 probe 只带了
`x-kpsdk-ct / h / v`，没有 cookie，也没有签 CD。交接包 §1 说读接口不校验 CD，
但那是在**它自己那套完整请求头**下的结论。

**这件事本轮没有解决**，记在这里，不要被"流量降了 94%"这个结果盖过去。

## 8. 复现方式

```bash
# 基线
dotnet exec bin/Debug/net8.0/kasada-live.dll --browser

# 带拦截
KASADA_BLOCK="*.png,*.jpg,...,*/video/*" \
  dotnet exec bin/Debug/net8.0/kasada-live.dll --browser

# 顺带验收 token
KASADA_CART_URL="https://arcteryx.com/api/cart.get?input=…" \
  dotnet exec bin/Debug/net8.0/kasada-live.dll --browser https://arcteryx.com/us/en/checkout
```

`kasada-live` 现在会打印：请求数、CDP 真实过线字节、本地丢弃数、最大的 12 个响应、
以及（给了 `KASADA_CART_URL` 时）`cart.get` 带/不带 token 的两次状态。
