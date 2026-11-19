# 16 · 流量下限实测：用 `cart.get` 200 当尺子

> 判据换成严格的那一个：**同一会话里 `cart.get` 回复 200**（15 §3 已达成）。
> 数字全部来自 CDP 的 `Network.loadingFinished.encodedDataLength` —— 真正过线的字节。
> 命令在 §6，任何人都能重算。

---

## 1. 结论

**435 KB 是"走浏览器"这条路的物理下限。** 不是参数没调好，是挑战本身要下发这么多。

| 形态 | 过线字节 | 出 CT |
|---|---|---|
| 无屏蔽（对照） | 20,570,464 | ✅ |
| 默认屏蔽（42 条 pattern），每次新 profile | 615,690 | ✅ |
| **保留 profile + 清身份** | **435,529** | ✅ |
| 保留 profile，不清身份 | 5,501 | ❌ 服务端不要求挑战 |

从 20.57 MB 到 0.435 MB，**−97.9%**。

---

## 2. 那 435 KB 到底是什么（冷启，完整 URL）

```
     417,741  .../2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js?KP_UIDz=0zzrp5xYdyuJ2Wa…&x-kpsdk-v=j-1.2.998&x-kpsdk-im=AAJRspsL…
     124,210  https://arcteryx.com/us/en/shop/X000009417
      65,122  .../2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js
       5,229  .../2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-1.2.998
       4,727  .../2d206a39-8ed7-437e-a3be-862e0f06eea3/tl
       4,137  .../2d206a39-8ed7-437e-a3be-862e0f06eea3/mfc
       其余合计 ≈ 5,300
      ------------------------------------------------
     626,827  / 56 requests
```

**67% 是 `ips.js`。** 它带 `KP_UIDz` 和 `x-kpsdk-im` 两个每轮都变的参数 ——
内容是这一轮现生成的，**没有缓存的可能性**。

其余两块都能省：

| 资源 | 冷启 | 保留 profile 后 | 为什么 |
|---|---|---|---|
| 产品页 HTML | 124,210 | **4,236** | 普通可缓存资源 |
| `p.js` | 65,122 | **0** | `Cache-Control: public, max-age=600` |
| `ips.js` | 417,741 | 417,741 | `KP_UIDz` 每轮不同 |
| `fp`/`tl`/`mfc` | 14,093 | 14,093 | 挑战本身 |

124 + 65 = 189 KB 省掉，626 → 435。**剩下的就是挑战的固有成本。**

---

## 3. `ips.js` 省不掉的证据

`ips.js` 的 URL 里 `KP_UIDz` 是 sensor 现算的一串 base64，`x-kpsdk-im` 是完整性值。
两轮之间必变：

```
RUN 1: .../ips.js?KP_UIDz=0CwAs9aUvCzmTjOa5QXKj6YjNHuHB75bwhLdsBwfxaS65ox0AoEMOl9JvYjctslOcqqLd0WHRXv0ekfhnQ…
RUN 6: .../ips.js?KP_UIDz=0zzrp5xYdyuJ2WawlFdRha6e7j8Kv33zjF1Eb7Vaz6FXJPMph3RZK0OcdYfXnnDDGuzWPOgyincamTkJx7xU…
```

不同 URL ⇒ 缓存键不同 ⇒ 每次都取。这是 Kasada 的吞吐成本，不是我们没优化。

---

## 4. 两次"看起来更便宜"的运行，都是假的

### 4.1 保留 profile 且不清身份 → 5,501 字节，但没有 `/tl`

```
wire bytes = 5,501
TlSolved = False   TlBody = (null)
Error = the submission body was unreadable
```

cookie 里的身份还有效，服务端**根本不要求挑战**。便宜，产出零。

### 4.2 清了 cookie 却没触发挑战 → 5,497 字节

同一 profile、同一清法，有时触发有时不触发。差别在于身份不只存在 cookie 里 ——
页面存储里还剩东西时，清 cookie 不够。**要可靠地拿到挑战，cookie 与页面存储一起清。**

这两次说明同一件事：**字节数小不代表成功，必须和 `TlSolved` + `cart.get` 200 一起读。**

---

## 5. `cart.get` 200 确实是真判据

当尺子之前先确认它真的在用 token。`cart.get` 请求上实际挂的头：

```
req x-kpsdk-ct: 0EBEt65CU4b7FMgXRb5fF4wPlyy2FilxXXzRsdkxT69gQttsxXxEF4bmWGyD…
req x-kpsdk-dt: 1837z11lrxa3z4s7xb1x51jxc12jx74wdj4y2nx9smz37x6goz045f
req x-kpsdk-im: AAJsBXxr7Ua3c4q8OkH_g8TKovlfGO0ZAbSOVuSnJ9rxgRL-vh53o1RUuKyx…
req x-kpsdk-v : j-1.2.998
```

- **有 `x-kpsdk-ct`** ⇒ 读取携带身份；
- **没有 `x-kpsdk-cd`** ⇒ 与"读取不要 CD、写入才要 fresh CD"一致；
- 这些头**由 sensor 自己挂**（手工塞的那一臂是 429，见 15 §4.1）。

⇒ `cart.get` 200 成立即说明这一轮的 ct 是活的。

---

## 6. 重算命令

```powershell
cd D:\projects\cyber-reverse
$env:DOTNET_ROOT='D:\tools\dotnet8'
$dll = 'analysis\kasada-live\bin\Release\net8.0\kasada-live.dll'

# 形态一：每次新 profile（干净，最贵）
& D:\tools\dotnet8\dotnet.exe exec $dll --browser

# 形态二：保留 profile + 清身份（本轮最优，435 KB）
$env:KASADA_PROFILE = (Join-Path (Get-Location) '.tmp-profile')
$env:KASADA_FRESH   = '1'
& D:\tools\dotnet8\dotnet.exe exec $dll --browser

# 形态三：保留 profile + 不清身份（5.5 KB，但没有 CT）
Remove-Item Env:\KASADA_FRESH
& D:\tools\dotnet8\dotnet.exe exec $dll --browser
```

看四处：`wire bytes`、`TlSolved`、`/tl` 是否出现、`G in-page GET {"json":...}` 的 `status=`。

---

## 7. 再往下没有量级空间了（原 §7 的"80 KB"已撤回）

### 7.1 先纠正一条错结论

本文档上一版写过"本地执行 `p.js`、跳过 `ips.js` 下载，单次成本会掉到 80 KB"。**那是错的，撤回。**

错在两处叠加：一是把 417,741 读成了 `p.js`（95 字符截断，见 §8），二是假设 `ips.js` 可以不取。

### 7.2 `ips.js` 是什么（实测）

```
HTTP/1.1 200 OK
Content-Length: 809554
content-type: application/javascript; charset=utf-8
cache-control: no-cache, no-store, must-revalidate
```

788,720 字符、84 个 `function`、1 处 `new Function`，开头是

```js
KPSDK.scriptStart=KPSDK.now();"use strict";(function(){var S;var l=function(n,e,r){...
```

`KPSDK.scriptStart=KPSDK.now()` 说明它接着 `p.js` 建好的 `KPSDK` 对象继续执行；
大量数值常量（`-171615552+1333476568-516796168+…`）每轮随机化。

⇒ **`ips.js` 不是资源，是这一轮挑战程序的本体。** `p.js`（65 KB）是引导与协议框架，
真正的计算在这 809 KB 里，每轮现生成、明令不缓存。

### 7.3 所以"本地执行"省不掉它

用 Jint 本地跑 `p.js`，它执行到那一步照样会请求 `ips.js` 并把它跑掉。
唯一能"跳过"的办法是自己复刻那 809 KB 的算法 —— 而它的数值常量每轮都换，
**没有一份固定算法可供复刻**。

本地执行真正省的是**进程、并发、GUI**，不是流量；而且还要自己维护脚本副本，
失去浏览器缓存对 HTML 与 `p.js` 的托底。

### 7.4 真正的摊薄在这里

435 KB 换来的那一个 `x-kpsdk-ct`，实测连续打 3 次 `cart.get` 全部 200
（每次返回不同的 cart id），每轮只多约 1.3 KB，`/tl` 轮次 +0：

```
round 1: +  1,332 bytes, submission +0, ct 01XJe84J0n0f… -> status=200
round 2: +  1,487 bytes, submission +0, ct 01XJe84J0n0f… -> status=200
round 3: +  1,330 bytes, submission +0, ct 01XJe84J0n0f… -> status=200
```

⇒ **一个 `ips.js` 支撑一整段会话。单请求成本 = 435 KB ÷ N。**
要压"每次业务请求的流量"，靠的是复用这个会话，不是再去砍那 435 KB。

---

## 8. 本轮改了什么

- `ChromiumBridge`
  - `ClearCookiesAsync(origin, includeStorage)` —— 保留缓存、丢掉身份。
  - `CompletedTlCount()` —— 数已完成的 `/tl` 轮次，用来分辨"新 token"和"原来那个"。
- `ChromiumKasadaSolver`
  - `ProfilePath` —— 保留 profile，让 HTML 与 `p.js` 命中缓存（省 189 KB）。
  - `FreshCookies` —— 逼出新一轮挑战。
  - `AfterSolveAsync` / `AfterSolveError` —— token 只在它自己的会话里有意义，这是唯一能花掉它的窗口。
- `analysis/kasada-live`
  - **打印完整 URL**。原来截到 95 字符，而 sensor 目录下每个 URL 的前 95 字符完全一样，
    `ips.js`、`p.js`、`fp`、`mfc`、`tl` 全被读成同一个 —— 我因此把 417 KB 的 `ips.js`
    写成了 `p.js`，并据此推出"p.js 缓存是瓶颈"的错误结论。这是第三次栽在读取器截断上。
  - `KASADA_PAGE` / `KASADA_STORE` / `KASADA_PROFILE` / `KASADA_FRESH` / `KASADA_ROUNDS`。
  - 默认站点从 `nike.com` 改为 Arcteryx 产品页（见 15 §7）。

---

## 9. 待查

- `ips.js` 未压缩 809,554 字节，传输 417,741（brotli）。协商更优编码的空间极小，但没测过 `zstd`。
- **`ips.js` 的复用边界**：一个 `ips.js` 能支撑同一会话里多少次受保护请求、能撑多久。
  目前测到 3 次 `cart.get` 未触发新的 `/tl`，边界未探。
- 清身份需要清到哪一层才能**稳定**触发挑战（cookie 够不够、要不要 `local_storage`/`indexedDB` 一起清）。
  本轮出现过"同样清法有时触发有时不触发"，机制未定。
- 探测 `ips.js` 时 `Range: bytes=0-1023` 被忽略（回 `200` 而非 `206`，整份 809,554 字节返回），
  白花了 809 KB。要取头部得自己截流，不能靠 `Range`。
