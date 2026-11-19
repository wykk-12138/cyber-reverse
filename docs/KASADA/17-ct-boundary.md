# 17 · CT 的产出边界：一个 ips.js 能不能出多个 CT

> 问题：一个会话里的那份 `ips.js`，能不能连出 5 个 CT，5 个之后才换 profile？
> 答案：**不能**。而且原因不在脚本，在于**挑战根本没有被要求**。
> 数字都可重算，命令在 §5。

---

## 1. 结论

| 设想 | 结果 |
|---|---|
| 一个会话、一个 `ips.js`、连出 5 个 CT | ❌ **一个都出不来**，挑战不再发生 |
| 5 个 profile 轮换、各出一个 CT | ✅ **5/5**，五个 CT 全不同、全部过 `cart.get` 200 |
| 共享缓存目录省掉 `p.js` | ❌ 没生效，`p.js` 仍每轮重下 |
| 热 profile 省掉 `p.js` | ❌ 清身份后仍重下 |

**每 CT 的实测成本 ≈ 625 KB。** 其中 `ips.js` ~420 KB、`p.js` ~64 KB，都省不掉。

---

## 2. 会话内出不来第二个 CT（决定性的一次）

同一浏览器、同一 profile，每轮先清 cookie 与页面存储、再重新导航，连做 4 轮：

```
round 1: new=False solved=False cart200=True submission +0 ipsJsFiles +0
          +  5,585 bytes   ct=02uu1gAy7NGKM5aR...  st=1795101205548   body=(none)
round 2: new=False solved=False cart200=True submission +0 ipsJsFiles +0
          +  5,709 bytes   ct=02uu1gAy7NGKM5aR...  st=1795101205548   body=(none)
round 3: new=False solved=False cart200=True submission +0 ipsJsFiles +0
          +  5,688 bytes   ct=02uu1gAy7NGKM5aR...  st=1795101205548   body=(none)
round 4: new=False solved=False cart200=True submission +0 ipsJsFiles +0
          +  5,686 bytes   ct=02uu1gAy7NGKM5aR...  st=1795101205548   body=(none)

ips.js downloads = 1   total 410,668 bytes
usable identities = 0/5   distinct ct = 1
```

三件事同时成立：

- **`submission +0`** —— 没有新的 `/tl`，挑战没被要求；
- **`ipsJsFiles +0`** —— 没有第二份 `ips.js`，因为压根没有第二轮；
- **`ct` 与 `st` 逐字相同** —— sensor 沿用了内存里那一轮的结果。

⇒ **身份不是"清掉就会重新挑战"的。挑战由服务端决定，服务端认为这个设备已经通过，就不再要求。**
在同一个会话里换身份没有意义 —— 换不掉的是设备指纹。

---

## 3. 要新 CT 只能换 profile（5/5 通过）

每轮一个独立 profile、独立身份：

```
cycle 1: ok=True tlSolved=True ct=02nXn3mBDVguNvZO... distinct=True st=1795101447495
          bytes=644,097  ips=435,439  pjs=64,267  dropped=39  secs=7
          cart: status=200 len=448 {"result":{"data":{"json":{"id":"irb6ykN4whJ0Iq6xjp3bklTxEaFhJ42R",...
cycle 2: ... ct=029ZUKFq3y7T1NAq...  bytes=626,701  ips=417,601  pjs=64,269  secs=9
          cart: status=200 ... "id":"xgC9WKWBgxihuN0C1WyxFHIBKZubWuME"
cycle 3: ... ct=01T5NiL1NgEK0UlX...  bytes=610,265  ips=401,640  pjs=64,270  secs=8
          cart: status=200 ... "id":"8fat1viSbkVyYRnBzBogMhse5YYtkQv1"
cycle 4: ... ct=022Y1TtcHABNelQV...  bytes=626,711  ips=418,449  pjs=64,269  secs=8
          cart: status=200 ... "id":"Pv3xMwFuaZ4tzjW462LLzkWMEXpQssPJ"
cycle 5: ... ct=024gFoT43RldA3rJ...  bytes=615,526  ips=406,544  pjs=64,428  secs=8
          cart: status=200 ... "id":"7eNw3aATpwck3wcZnhJuJgYI8VguiRaw"

usable identities = 5/5   distinct ct = 5
```

- **五个 CT 全不同**，五个 `cart.get` 全 200，**每次返回不同 cart id**；
- 每轮 8–9 秒，5 个 CT 约 3.05 MB；
- `ips.js` 每轮都取新的一份，因为换 profile 就是换会话，`KP_UIDz` 跟着变。

---

## 4. `cart.get` 200 是真判据（补证）

同一条 URL，从 host 侧裸发、不带任何 `x-kpsdk-*`、不带 cookie：

```
裸请求（无 cookie、无 x-kpsdk-*）        status=429 size=0
带 UA/Origin/Referer，仍无 ct             status=429 size=0
```

⇒ 没有身份就是 429。所以上面那些 200 确实是用 CT 换来的，不是公开可读。

---

## 5. 试过但没用的两条省法

### 5.1 共享缓存目录

`--disk-cache-dir` 指到 profile 目录之外的公共目录，想让 5 个 profile 共用一份 `p.js`：

```
cycle 1: bytes=621,796  ips=412,821  pjs=64,427
cycle 2: bytes=627,295  ips=418,292  pjs=64,436
cycle 3: bytes=646,717  ips=438,140  pjs=64,036
```

`p.js` 一分没省。**没有生效。**

### 5.2 热 profile

用已经跑过的 profile 再跑：

```
cycle 1: bytes=635,581  ips=427,719  pjs=63,878
cycle 2: bytes=648,879  ips=441,039  pjs=63,878
cycle 3: bytes=643,934  ips=436,050  pjs=64,038
```

仍然每轮 64 KB。**清身份会让 `p.js` 重新下载**，虽然它有 `max-age=600`。

（对照：同 profile **不清**身份时 `p.js` 确实是 0 字节，但那时挑战不发生、没有 CT，见 16 §4.1。）

---

## 6. 重算命令

```powershell
cd D:\projects\cyber-reverse
$env:DOTNET_ROOT='D:\tools\dotnet8'
$dll = 'analysis\kasada-live\bin\Release\net8.0\kasada-live.dll'

# 会话内多轮（结论：出不来第二个 CT）
Remove-Item Env:\KASADA_ROTATE -ErrorAction SilentlyContinue
$env:KASADA_SESSION = '1'
$env:KASADA_CYCLES  = '5'
$env:KASADA_PROFILE = (Join-Path (Get-Location) '.tmp-profile-s')
& D:\tools\dotnet8\dotnet.exe exec $dll --cycles

# 轮换 profile（结论：5/5 出五个不同 CT）
Remove-Item Env:\KASADA_SESSION -ErrorAction SilentlyContinue
$env:KASADA_ROTATE  = '1'
$env:KASADA_CYCLES  = '5'
$env:KASADA_PROFILE = (Join-Path (Get-Location) '.tmp-profile-r')
& D:\tools\dotnet8\dotnet.exe exec $dll --cycles
```

看三处：`usable identities = N/N`、每个 cycle 的 `distinct=`、以及 `cart: status=200`。

---

## 7. 这些数字意味着什么

- **拿 CT 的代价是每轮 625 KB，而且必须换设备指纹。** 这不是缓存问题，是 Kasada 的挑战频率由服务端掌握。
- **一个 CT 能在它的浏览器实例里活很久** —— §2 那 4 轮共 20 多秒内 4 次 `cart.get` 都 200；16 §7.4 也测到同一 ct 连打 3 次都 200。所以"CT 用几次就废"并不成立。
- 所以 **429 不是"CT 老了"**，更可能是频率、并发或行为模式触发的风控。要定位它，得从请求节奏上看，不是在 CT 上找原因。

---

## 8. 本轮改了什么

- `ChromiumBridge.LaunchAsync(..., cachePath)` → `--disk-cache-dir`（§5.1，没生效，但保留开关，日后可换实现）。
- `ChromiumKasadaSolver.CachePath`，以及 `FreshCookies` 现在**连页面存储一起清**（只清 cookie 不足以稳定触发挑战）。
- `analysis/kasada-live --cycles`
  - `KASADA_SESSION=1` 会话内多轮（清身份 + 重导航）；
  - `KASADA_ROTATE=1` 每轮独立 profile；
  - 每轮打印 `submission +N`、`ipsJsFiles +N`、`distinct`、字节拆分。
  - 这个 `ipsJsFiles` 计数是判断"脚本有没有被复用"的关键量：按 `KP_UIDz` 区分的 URL 数量。
