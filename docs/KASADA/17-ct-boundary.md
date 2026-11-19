# 17 · CT 的产出边界

> 问题：一个 `ips.js` 能不能连出 5 个 CT，5 个之后才换 profile？
> 答案：**换的不是 profile，是浏览器进程。** 同一 profile 反复重启就能一直出新 CT，
> 而且从第二个起 `p.js` 全走缓存，每个 CT 约 **450 KB**。

---

## 1. 结论

| 设想 | 结果 |
|---|---|
| 一个会话、一份 `ips.js`、连出 5 个 CT | ❌ **一个都出不来**，挑战不再发生 |
| 同一浏览器实例内清身份 + 重导航 | ❌ `submission +0`，`ct`/`st` 逐字不变 |
| **同一 profile、每次新浏览器进程 + 清身份** | ✅ **每次都是新 CT，`p.js` 走缓存** |
| 共享缓存目录（`--disk-cache-dir`）跨 profile | ❌ 没生效，见 §5.1 |

**每 CT 的稳态成本 ≈ 450 KB**（冷启第一次 620 KB，之后固定 445–460 KB）。

---

## 2. 同一浏览器实例内出不来第二个 CT

每轮先清 cookie 与页面存储、再重新导航，连做 4 轮：

```
round 1: submission +0 ipsJsFiles +0  +5,585 bytes  ct=02uu1gAy7NGKM5aR...  st=1795101205548
round 2: submission +0 ipsJsFiles +0  +5,709 bytes  ct=02uu1gAy7NGKM5aR...  st=1795101205548
round 3: submission +0 ipsJsFiles +0  +5,688 bytes  ct=02uu1gAy7NGKM5aR...  st=1795101205548
round 4: submission +0 ipsJsFiles +0  +5,686 bytes  ct=02uu1gAy7NGKM5aR...  st=1795101205548

usable identities = 0/5   distinct ct = 1   ips.js downloads = 1
```

`submission +0` 与 `ipsJsFiles +0` 同时成立 ⇒ **第二轮挑战根本没发生**，不是脚本没复用。
`sensor` 的内存里还留着那一轮的结果，清掉磁盘上的身份不会清掉它。

---

## 3. 换进程就够了，profile 可以留着（决定性的一组）

同一个 profile 连跑两次（每次都是新浏览器进程、都清身份）：

```
cycle 1 (冷): bytes=619,066  ips=411,949  pjs=62,894   ct=02iNsOlfeplwaAa3...  cart 200
cycle 2 (热): bytes=441,359  ips=421,703  pjs=0        ct=02adhpSK5W44WxWy...  cart 200
```

再连跑三轮，确认可重复：

```
cycle 1: bytes=458,621  ips=438,022  pjs=0   ct=024hlrs5B2vRF7E6...  cart 200  secs=7
cycle 2: bytes=444,943  ips=425,614  pjs=0   ct=0261xTr4PmO6gmyQ...  cart 200  secs=9
cycle 3: bytes=460,531  ips=440,359  pjs=0   ct=021b6kTVq9oVZKBJ...  cart 200  secs=10
usable identities = 3/3   distinct ct = 3
```

- **每个 CT 都是新的**，每个 `cart.get` 都 200，每个返回不同 cart id；
- **`p.js` = 0**，第二个起完全走 profile 缓存；
- 每轮 445–460 KB，8–10 秒。

⇒ 机制：**进程重启把 sensor 的内存状态清掉了**，所以服务端认为这是一个没有身份的新来客，于是要求挑战；
而磁盘上的 profile 还在，`p.js` 和页面 HTML 直接从缓存拿。**两件事解耦了。**

---

## 4. `cart.get` 200 是真判据

同一条 URL，host 侧裸发、不带任何 `x-kpsdk-*`、不带 cookie：

```
裸请求                      status=429 size=0
带 UA/Origin/Referer 仍无 ct  status=429 size=0
```

没有身份就是 429。所以那些 200 确实是 CT 换来的。

---

## 5. 试过但没用的省法

### 5.1 共享缓存目录（没生效，且污染了当时的对照）

`--disk-cache-dir` 指到 profile 之外的公共目录：

```
cycle 1: pjs=64,427    cycle 2: pjs=64,436    cycle 3: pjs=64,036
```

`p.js` 一分没省。

> **注意**：这个开关还有个副作用 —— 它把缓存搬离了 profile 目录，所以**之后**用同一个 profile
> （不再带这个开关）时缓存是空的。本文档上一版据此写了"热 profile 仍每轮 64 KB"，
> 那个结论是被这个副作用污染的，已删除。§3 才是干净测法。

### 5.2 轮换 profile（不必要）

每轮一个独立 profile 也能出 CT（5/5，见上一版记录），但每个 profile 都是冷的，
`p.js` 和 HTML 都要重新付，所以是 625 KB/CT 而不是 450 KB。

**轮换 profile 是花钱买不需要的东西** —— 要的是新进程，不是新指纹。

---

## 6. 重算命令

```powershell
cd D:\projects\cyber-reverse
$env:DOTNET_ROOT='D:\tools\dotnet8'
$dll = 'analysis\kasada-live\bin\Release\net8.0\kasada-live.dll'

# 同一 profile，连跑 3 轮（第一轮冷，之后 p.js 为 0）
Remove-Item Env:\KASADA_SESSION,Env:\KASADA_ROTATE,Env:\KASADA_CACHE -ErrorAction SilentlyContinue
$env:KASADA_CYCLES  = '3'
$env:KASADA_PROFILE = (Join-Path (Get-Location) '.tmp-p2')
& D:\tools\dotnet8\dotnet.exe exec $dll --cycles

# 对照：同一浏览器实例内清身份重导航（出不来第二个 CT）
$env:KASADA_SESSION = '1'
& D:\tools\dotnet8\dotnet.exe exec $dll --cycles
```

看三处：`usable identities = N/N`、每轮的 `pjs=`、以及 `cart: status=200`。

---

## 7. 这些数字意味着什么

- **稳态 450 KB / CT**，其中 `ips.js` 约 420 KB。剩下那 30 KB 是 `/tl`、`/mfc`、`/fp` 与页面请求。
- `ips.js` 省不掉：它每轮由服务端按 `KP_UIDz` 现生成，`no-store`，见 16。
- `p.js` 与 HTML 能省，条件是**别换 profile**。
- **一个 CT 活得比想象久**：16 §7.4 与 17 §2 都测到同一 ct 连续多次 `cart.get` 全 200。
  所以实践中撞到的 429 更可能来自频率、并发或请求节奏，而不是 CT 老化。

---

## 8. 本轮改了什么

- `ChromiumBridge.LaunchAsync(..., cachePath)` → `--disk-cache-dir`（§5.1 无效，保留开关）。
- `ChromiumKasadaSolver.CachePath`；`FreshCookies` 现在**连页面存储一起清**。
- `analysis/kasada-live --cycles`
  - `KASADA_SESSION=1` 会话内多轮；`KASADA_ROTATE=1` 每轮独立 profile；默认同一 profile 连跑。
  - 每轮打印 `submission +N`、`ipsJsFiles +N`、`distinct`、`bytes/ips/pjs` 拆分。
  - `ipsJsFiles` 按 `KP_UIDz` 区分的 URL 计数，是判断"脚本有没有被复用"的关键量。

---

## 9. 本版修正了上一版的哪些结论

| 上一版 | 现在 |
|---|---|
| "要新 CT 只能换 profile" | **换进程即可，profile 留着更省** |
| "热 profile 仍每轮 64 KB `p.js`" | **热 profile `p.js` = 0**，上一版测的是被 `--disk-cache-dir` 污染过的 profile |
| "每 CT ≈ 625 KB" | **冷启 620 KB，稳态 ≈ 450 KB** |
| "共享缓存目录能让 5 个 profile 共用 p.js" | 没生效，且会破坏后续 profile 的缓存 |
