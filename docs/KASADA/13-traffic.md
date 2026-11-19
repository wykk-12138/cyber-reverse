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

---

## 9. 补上 CD 再测：卡在更前面一步

按交接包 §4 Step 4 走本地 CD 生成，先做离线自检（`kasada_cd.mjs`）：

```
$ node kasada_cd.mjs examples/cd-input.example.json
{"workTime":1700000000092,"id":"00000000000000000000000000000000",
 "answers":[30,3,8,60],"duration":0,"d":8,"st":1700000000000,"rst":1700000000008}
```

**与交接包 §5.C 给的期望输出逐字节一致。** 算法脚本本身是好的。

### 9.1 但四份输入里，三份拿不到

`generateCd({ ct, st, fc, time, id, runtimeSuffix })` 要有这些：

| 输入 | 状态 |
|---|---|
| `ct` | ✅ 拿得到（`/tl` 响应头） |
| `st` | ⚠️ `/tl` 响应头里**没有**（因为那一轮没解出来） |
| `fc` 里的 `cryptoChallenge` | ❌ **拿不到** |
| `runtimeSuffix` | ❌ **解不出来** |

**（1）`cryptoChallenge` 拿不到**

浏览器模式下抓到的 fc 和 curl 打 `/mfc` 拿到的一样：

```
eyJmZWF0dXJlRmxhZ3MiOnt9LCJkeW5hbWljQ29uZmlnIjp7ImZyb250ZW5k…   （截断）
→ {"featureFlags":{},"dynamicConfig":{"frontend":{"logLevel":40}}}
```

**没有 `cryptoChallenge`。** 交接包 §2 记的那份带
`{"difficulty":77,"subchallengeCount":4,"seedSuffix":"melt-u-bot"}` 的 fc，
在当前这套 headless + stealth 环境里**没出现过**。

**（2）`runtimeSuffix` 解不出来**

```
$ python kasada_re/decode-pool.py .tmp-arc-p.js .tmp-arc-pool --grep melt
container markers not found
```

当前的 `p.js`（158,330 字节）里那个池容器标记没了，脚本报 `container markers not found`。
交接包 §2 自己就写了"换版后必须重新解出，不能用旧值蒙" —— 而重解这条路现在是断的。

### 9.2 `/tl` 的正文是空的 —— 连浏览器也是

我加了 `ResponseBodyAsync`（`Network.getResponseBody`）去读 `/tl` 的正文，
因为交接包明确说"200 不等于成功，只有 15 字节 `{"reload":true}` 才算"。

```
Arc:   TlSolved = False   TlBody = []
Nike:  TlSolved = False   TlBody = []
```

**两个站点都是空正文。** 也印证了：

- 页面自己发的 `cart.get` 是 **429**（`reqbody=0b`）
- `/tl` 响应头里没有 `x-kpsdk-st`，请求里也没有 `x-kpsdk-cd`

**⇒ 这套 headless + stealth 环境下的浏览器，挑战根本没解出来。**

### 9.3 顺手修掉一个交接包点名的陷阱

交接包 §4 Step 0 写：

> **不要**在导航前/挑战期间发 CDP `Runtime.enable`（`Runtime.evaluate` 不需要它）。

复刻件的 `ChromiumBridge.LaunchAsync` **一直在发**（`ChromiumBridge.cs` 原来的 L176）。
已移除 —— `Runtime.evaluate` 确实不需要它。

**但移除之后 `/tl` 仍然是空正文**，所以这不是唯一原因，
（`--disable-blink-features=AutomationControlled` 本来就有）。
**这条改动是对的（文档明确要求），但它没解决问题，不能算修好了。**

### 9.4 这轮的实际结论

**流量那一半是成功的，CD 那一半没打通，而且卡点不在 CD 上。**

```
流量：13.3 MB → 805 KB（−94%），token 照样拿到   ✅
CD ：无法生成 —— 缺 cryptoChallenge、缺 runtimeSuffix、缺 st
     而这三样缺的根因是同一个：这一轮 /tl 没解出挑战
```

**"解出挑战"和"拿到 ct"是两件事。** 我们这边一直是后者：
token 有，但它是未解出回合发的，所以 `cart.get` 429。

**要把 CD 这条路走通，得先让 `/tl` 返回 `{"reload":true}`。** 那需要的不是 CD，
是让挑战本身跑通 —— 交接包说这只有真浏览器能做到，而"真浏览器"的具体条件
（不是 headless？特定的 stealth 组合？）本轮没有定位到。

### 9.5 我没验证的

- **没有在 headed（非 headless）模式下跑过** —— 这是最可能的下一个变量。
- **没有对比过官方/供应商产出的 bundle** —— 交接包 §5.D 的基线做法我没做。
- **没有尝试用旧的 `runtimeSuffix`**（`c7a30a96…`）硬算一份 CD ——
  文档说换版后会全错但字节合法，测了也说明不了问题。
- `cart.get` 的 429 可能还有别的成因（真实 cart id、登录态、地域），
  我只用了随机 32 hex 的 id。
