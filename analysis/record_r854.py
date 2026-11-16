"""Record R854: 67 runs, the eight were a sample, and HandleResponse sits next to GetKasada."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 真实序列数：1301 条 `d__` 串里有 **67 段**递增运行（R854）

**`StoreFlowSteps` 只记了 8 条。下面是其中明显是流程的，以及它们是否在 8 条里：**

| 地址 | 步数 | 序列开头 | 在 8 条里？ |
|---|---|---|---|
| `0x14336febd` | 12 | `StartAppFast · StartAppSafe · GetSessionDw · GetCartDw · FindProductApp · AddToCartApp · AddToCartAppDw · SaveSessionDw` | ✓ demandware-dual |
| `0x143391b79` | 11 | `FindProduct · AddToCart · SubmitDiscount · GetCheckout · GetShippingRates · GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` | **不在** |
| `0x14336eca7` | 8 | `GetCsrf · GetCheckout · GetCheckoutHtml · AddToCart · AddToCart2 · SubmitDiscount · SubmitShipping · SubmitOrder` | ✓ demandware-classic |
| `0x14338f6c5` | 8 | `GetHome · AddToCart · SubmitDiscount · GetCartValue · SubmitShipping · SubmitBilling · SubmitInfo · SendManualNotification` | **不在** |
| `0x14336f85f` | 7 | `FindProduct · AddToCart · GetCheckout · GetShippingRates · SubmitShipping · SubmitPayment · SubmitOrder` | ✓ 与 classic 同族 |
| `0x14339468a` | 7 | `FindProduct · GetProduct · CreateCart · AddToCart · SubmitPayment · SubmitOrder · ProcessOrder` | **不在** |
| `0x1434ab921` | 7 | `GetSession · RefreshToken · CreateCart · FindProduct · GenerateCheckout · SubmitEmail · SubmitShipping` | **不在** |
| `0x1434b3109` | 7 | `FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · AddToCartMulti · AddToCartPreload` | **不在** |
| `0x14337a56e` | 6 | `SubmitPayPal · ApplyPayPal · ProcessPayPal · Process3DS · SubmitOrder · ProcessOrder` | **不在** |
| `0x14337bdc4` | 6 | **`StartSignupFlow · StartClearFlow · StartInStoreFlow · StartPopNowFlow · StartNormalFlow · CheckLogin`** | **不在**（R838 那条） |
| `0x1433835c8` | 6 | `SetEmail · GetCheckoutPage · GetShippingRates · SubmitShipping · SetPayment · SubmitOrder` | **不在** |
| `0x14338b455` | 6 | `GetHome · WebHandOver · SessionHandover · GuestCallback · DeliveryPage · SubmitShipping` | ✓ johnlewis |
| `0x1433937ec` | 6 | `CreateCheckoutApp · GetBasket · AddToCart · SubmitDiscount · LookupAddress · GetDelivery` | ✓ collectplus-app |
| `0x1433712d6` | 4 | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` | **不在** |
| `0x14337c7e5` | 4 | `StartDrawCheckFlow · FindDraw · CheckDraw · EnterDraw` | ✓ popmart 片段 |
| `0x143386376` | 4 | `StartEcomSession · Authorize · GetAccessToken · FindVariant` | ✓ nike |
| **`0x14345abb1`** | **4** | **`HandleResponse · GetScript · GetKasada · GetWorkTime`** | **不在 —— 且这是 R827/R828 追不到的那个 `HandleResponse`** |
| `0x14344be8a` | 5 | `GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc` | **不在 —— 风控指纹组** |
| `0x14344998c` | 4 | `SubmitProps · SubmitProps2 · SubmitWpt · SubmitSensor` | **不在 —— 指纹组** |
| `0x14348bfc5` | 4 | `MoveMouseAsync · ReleaseMouseOnScreenAsync · PressMouseOnScreenAsync · PressKeyAsync` | **不在 —— 人机行为组** |

**另外一批是库代码，不是流程**：`ReadFrameHeaderAsync/ReadPayloadAsync/ReadRawAsync`（TLS 读）、
`AuthenticateAsync/ConnectAsync/DisconnectAsync`（gRPC）、`ProcessMessagesAsync/HandshakeAsync`（IPC）、
`StartAsync/StartReceiving/StartSending/StopAsync`（流）。

### 所以

**67 段里，明显是业务流程的至少 20 段；`StoreFlowSteps` 的 8 条是其中一部分。**

**R844 那个 16.9% 的分母（8 条 / 130 步）是抽样，不是总体。**
"""

if "真实序列数：1301 条 `d__` 串里有 **67 段**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: 67 runs appended")

BLOCKER = """

---

## 278. **67 段序列，`StoreFlowSteps` 的 8 条是抽样**；而 `HandleResponse` 的邻居是 `GetKasada`

> R854。未改产品代码。**这一条推翻了 R844 的分母。**

### 一、怎么数的

**镜像里每条流程序列是「多个 `d__N` 相邻、ordinal 递增」的一段串。
用 IDAPython 遍历全部 **1301** 条含 `d__` 的串（`idautils.Strings()`，不是 `str` —— 后者上限 500），
抽出「4 步以上、ordinal 递增且间隔 ≤3」的运行。**

**结果：67 段。**

### 二、8 条只是其中一部分

**明显是业务流程的至少 20 段。8 条里有的：`demandware-dual`(12) · `demandware-classic`(8) ·
`johnlewis`(6) · `collectplus-app`(6) · `popmart` 片段(4) · `nike`(4)。**

**8 条里没有的（部分）：**

| 步数 | 序列 |
|---|---|
| 11 | `FindProduct · AddToCart · SubmitDiscount · GetCheckout · GetShippingRates · GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` |
| 8 | `GetHome · AddToCart · SubmitDiscount · GetCartValue · SubmitShipping · SubmitBilling · SubmitInfo · SendManualNotification` |
| 7 | `FindProduct · GetProduct · CreateCart · AddToCart · SubmitPayment · SubmitOrder · ProcessOrder` |
| 7 | `GetSession · RefreshToken · CreateCart · FindProduct · GenerateCheckout · SubmitEmail · SubmitShipping` |
| 7 | `FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · AddToCartMulti · AddToCartPreload` |
| 6 | `SubmitPayPal · ApplyPayPal · ProcessPayPal · Process3DS · SubmitOrder · ProcessOrder` |
| 6 | `SetEmail · GetCheckoutPage · GetShippingRates · SubmitShipping · SetPayment · SubmitOrder` |
| 4 | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` |

**所以 R844 的 16.9% 是「8 条样本里的同名比」，不是「全镜像的覆盖率」。**
**这个数不该再被引用为覆盖率 —— 它连分母都不对。**

### 三、最重要的一条：`HandleResponse` 的邻居

```
0x14345abb1   HandleResponse · GetScript · GetKasada · GetWorkTime
```

**`HandleResponse` 是 R824 查到「总提及 = 1、真死」的那一步，R827/R828 追了几轮都到不了它的代码。**

**现在它在一条序列里，而邻居是 `GetKasada` —— 那是风控（优先级 ②）。**
**所以它大概不是通用的「处理响应」，是**Kasada 流程里的**一步。**

**这解释了为什么它在复刻件里孤立：复刻件有 `KasadaSolvers.cs` / `KasadaClearance.cs`，
但没有把 `HandleResponse` 接进任何序列。**

### 四、另外三组值得注意的

| 序列 | 性质 |
|---|---|
| `GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc` | **风控指纹组**（POW = proof of work，WebRTC） |
| `SubmitProps · SubmitProps2 · SubmitWpt · SubmitSensor` | **指纹组**（sensor / wpt） |
| `MoveMouseAsync · ReleaseMouseOnScreenAsync · PressMouseOnScreenAsync · PressKeyAsync` | **人机行为组** |

**这三组都不在 `StoreFlowSteps` 里（它不是流程表），但都是优先级 ② 的对象，而且都是 Observation。**

### 五、验证

```
idautils.Strings() 含 d__ 的串: 1301
4 步以上递增运行: 67
其中业务流程类: ≥20；库代码类: ReadFrameHeader/ConnectAsync/ProcessMessages/StartReceiving 等
0x14345abb1: HandleResponse · GetScript · GetKasada · GetWorkTime
0x14344be8a: GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **那 20+ 段流程各属哪个站**：**Unknown** —— 段落有了，归属没有。**要把段落对到站，得看每段的端点族。**
- **`StoreFlowSteps` 的 8 条当初怎么选的**：**仍是 Unknown**，但**现在知道它是抽样**。
- **`HandleResponse` 是否真属 Kasada 流程**：**Inference（中）** —— 邻居里有 `GetKasada`，
  **但「相邻」不等于「同一条管线」（R827 已记过这个坑）。**
- **67 段里有多少是库代码**：**Unknown** —— 我人工标了几组，**没逐段分类。**

### 七、教训

**R844 我用 8 条算出 16.9%，并在记录里写了三条「这不是覆盖率」的理由 ——
但那三条都是关于「解释」的（粒度、基类、映射），没有一条问「分母本身对不对」。**

**R853 发现了第 9 条，才逼出这个问题。**
**而这一轮一数：67 段。**

**「这个数是抽样还是总体」这个问题，我在 R816 就对 `pe_strings.txt` 问过一次，还写进了 AGENTS.md §2.7b。
而我没有对 `StoreFlowSteps` 问同一个问题 —— 因为它看起来是我自己整理的数据，不像外部来源。**
"""

VERDICT = """

---

## 第 854 轮：67 段序列，`StoreFlowSteps` 的 8 条是抽样

### 怎么数的

**用 `idautils.Strings()` 遍历全部 **1301** 条含 `d__` 的串（`str` 上限 500，不够），
抽「4 步以上、ordinal 递增且间隔 ≤3」的运行 → **67 段**。**

### 8 条只是其中一部分，明显是业务流程的至少 20 段

**8 条里没有的（部分）：**

| 步数 | 序列 |
|---|---|
| 11 | `…GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` |
| 8 | `GetHome · AddToCart · GetCartValue · SubmitInfo · SendManualNotification` |
| 7 | `…GetLotteryForm · SubmitLottery · AddToCartMulti` |
| 7 | `GetSession · RefreshToken · CreateCart · GenerateCheckout · SubmitEmail` |
| 6 | `SubmitPayPal · ApplyPayPal · ProcessPayPal · Process3DS` |
| 4 | `GetSweepStakeCheckout · SubmitSweepStakesShipping · EnterSweepStakesRaffle` |

> **R844 的 16.9% 是「8 条样本里的同名比」，不是覆盖率 —— 它连分母都不对，不该再被引用为覆盖率。**

### 最重要的一条：`HandleResponse` 的邻居

```
0x14345abb1   HandleResponse · GetScript · GetKasada · GetWorkTime
```

**`HandleResponse` 就是 R824 查到「总提及 = 1、真死」、R827/R828 追几轮到不了代码的那一步。**

**现在它在一条序列里，邻居是 `GetKasada` —— 风控（优先级 ②）。**
**所以它大概不是通用的「处理响应」，是**Kasada 流程里的一步** —— 这解释了它在复刻件里为何孤立。**

### 另外三组（都是优先级 ② 的 Observation）

| 序列 | 性质 |
|---|---|
| `GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc` | 风控指纹（POW / WebRTC） |
| `SubmitProps · SubmitProps2 · SubmitWpt · SubmitSensor` | 指纹（sensor / wpt） |
| `MoveMouseAsync · ReleaseMouseOnScreenAsync · PressMouseOnScreenAsync · PressKeyAsync` | 人机行为 |

### 仍然 Unknown

**那 20+ 段各属哪个站**（段落有了，归属没有 —— 要看每段端点族）· **8 条当初怎么选的**（仍是 Unknown，但已知是抽样）·
**`HandleResponse` 是否真属 Kasada**（Inference 中，「相邻 ≠ 同一管线」R827 已记过）· **67 段里多少是库代码**（未逐段分类）

### 教训

**R844 我给 16.9% 写了三条「这不是覆盖率」的理由，但那三条全是关于「解释」的，**没有一条问「分母本身对不对」**。**
**而「这个数是抽样还是总体」我在 R816 就对 `pe_strings.txt` 问过，还写进了 §2.7b —— 却没对 `StoreFlowSteps` 问，因为它看起来是我自己整理的数据。**
"""

BACKLOG_ADD = """

## 判据 (f) — 67 段序列（R854）：8 条是抽样

**`idautils.Strings()` 遍历 1301 条含 `d__` 串 → 4 步以上递增运行 **67 段**。**

**明显是业务流程的 ≥20 段；`StoreFlowSteps` 的 8 条只是其中一部分。**

| 8 条里没有的（部分） | 步数 |
|---|---|
| `…GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` | 11 |
| `GetHome · GetCartValue · SubmitInfo · SendManualNotification` | 8 |
| `…GetLotteryForm · SubmitLottery` | 7 |
| `GetSession · RefreshToken · GenerateCheckout · SubmitEmail` | 7 |
| `SubmitPayPal · ApplyPayPal · ProcessPayPal · Process3DS` | 6 |
| `GetSweepStakeCheckout · … · EnterSweepStakesRaffle` | 4 |

> **R844 的 16.9% 连分母都不对，不该再当覆盖率引用。**

### `HandleResponse` 的邻居（优先级 ②）

```
0x14345abb1   HandleResponse · GetScript · GetKasada · GetWorkTime
```

**R824 查到它「总提及 = 1」、R827/R828 追不到代码 —— 现在它在一条序列里，邻居是 `GetKasada`。**
**→ 它大概是 Kasada 流程里的一步，不是通用「处理响应」。**

### 另外三组（优先级 ②）

`GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc`（POW/WebRTC）·
`SubmitProps · SubmitProps2 · SubmitWpt · SubmitSensor` · `MoveMouseAsync · PressMouseOnScreenAsync · PressKeyAsync`

| 仍 Unknown | |
|---|---|
| 20+ 段各属哪个站 | 要看端点族 |
| 8 条当初怎么选的 | 已知是抽样 |
| `HandleResponse` 是否真属 Kasada | Inference 中（「相邻 ≠ 同管线」） |
| 67 段里多少是库代码 | 未逐段分类 |

**纪律**：**「抽样还是总体」我在 R816 对 `pe_strings.txt` 问过并写进 §2.7b，却没对 `StoreFlowSteps` 问 —— 因为它看起来是我自己整理的数据。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R854", BLOCKER)
    ensure(RSTATUS, "R854", BLOCKER)
    ensure(RVERDICT, "第 854 轮", VERDICT)
    ensure(BACKLOG, "R854", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R854" not in h:
        h += ("\n## R854 补充 — 67 段序列，8 条只是抽样\n\n"
              "**1301 条含 `d__` 串 → 4 步以上递增运行 67 段**（`idautils.Strings()`；`str` 上限 500 不够）。\n"
              "**`StoreFlowSteps` 的 8 条只是其中一部分，明显是业务流程的 ≥20 段。R844 的 16.9% 连分母都不对。**\n"
              "**`HandleResponse · GetScript · GetKasada · GetWorkTime` @`0x14345abb1`** —— "
              "R824 那个「真死」步骤，**邻居是 `GetKasada`，所以它大概是 Kasada 流程里的一步（优先级 ②）。**\n"
              "另三组指纹序列：`SubmitPOW`/`SubmitWebRtc` · `SubmitWpt`/`SubmitSensor` · 鼠标键盘行为组。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R854"), (RSTATUS, "R854"), (RVERDICT, "第 854 轮"), (BACKLOG, "R854")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R854: sixty-seven runs, so the eight flow tables were a sample and the 16.9 percent has no denominator\n\n"
         "R853 found a ninth sequence and asked how the eight had been selected. Counting settles it. Walking all 1301"
         " strings containing d__ through Strings() -- str caps at 500, which is why earlier attempts undercounted --"
         " and extracting runs of four or more ascending ordinals with gaps of at most three gives sixty-seven runs.\n\n"
         "At least twenty look like business flows, and the eight tables hold only some of them. Absent from the tables:"
         " an eleven-step PayPal credit-card path ending in ProcessPaymentPaypalCreditCard; an eight-step path with"
         " GetCartValue, SubmitInfo and SendManualNotification; a seven-step lottery path with GetLotteryForm and"
         " SubmitLottery; a seven-step path starting GetSession, RefreshToken, GenerateCheckout; a six-step PayPal three-"
         " DS path; a four-step sweepstake path. The rest are library code -- TLS frame readers, gRPC connect and"
         " authenticate, IPC handshake, stream start and stop.\n\n"
         "So R844's 16.9 percent was a same-name ratio inside an eight-flow sample, not a coverage figure. Its"
         " denominator was never the population, and the number should stop being cited as coverage at all.\n\n"
         "The most consequential row is a four-step run at 0x14345abb1: HandleResponse, GetScript, GetKasada, GetWorkTime."
         " HandleResponse is the step R824 found with a bare-name count of one and that R827 and R828 could not reach the"
         " code for. Here it sits inside a sequence whose neighbour is GetKasada, which puts it in the risk-control code"
         " that priority two is about rather than in generic response handling -- and that explains why it is isolated in"
         " the replica, which has Kasada solvers and clearance but never wired HandleResponse into anything.\n\n"
         "Three further runs belong to the same priority: GetLogo, GetCookie, SubmitClientData, SubmitPOW, SubmitWebRtc;"
         " SubmitProps, SubmitProps2, SubmitWpt, SubmitSensor; and the mouse and key behaviour group.\n\n"
         "Unknown: which site each of the twenty-odd flow runs belongs to, since the runs exist but their ownership needs"
         " the endpoint family of each; how the eight were originally chosen, still unknown though now known to be a"
         " sample; whether HandleResponse truly belongs to Kasada, which is inference from adjacency and R827 already"
         " recorded that adjacency is not a pipeline; and how many of the sixty-seven are library code, which I labelled"
         " by eye rather than classified.\n\n"
         "The lesson is about heredity. I wrote three reasons why 16.9 percent was not coverage, and all three were about"
         " interpreting the number; none asked whether its denominator was the population. I had asked exactly that"
         " question of pe_strings.txt in R816 and written the rule into AGENTS.md section 2.7b -- but not of"
         " StoreFlowSteps, because that table looked like data I had assembled myself rather than an external source.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
