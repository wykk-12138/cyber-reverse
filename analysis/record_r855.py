"""Record R855: the extra runs are task variants -- raffle covered, sweepstake and lottery absent."""

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
### 8 条之外的段：一部分是**任务变体**，不是别的站（R855）

**镜像里有这三组运行，而复刻件的覆盖差别极大：**

| 变体 | 镜像里的步骤 | 复刻件 |
|---|---|---|
| **raffle** | （已在 `RaffleFlow`，R835 查过 `r419.com` / `lndg.page` / `nodnod.digital`） | **`Raffle` 96 处 / 7 个文件** |
| **sweepstake** | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` | **`SweepStake` 0 处** |
| **lottery** | `FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · AddToCartMulti · AddToCartPreload` | **`Lottery` 0 处** |

**而 `TaskType` 在复刻件只出现 2 次（`ThirdPartyDrivers.cs`），没有对应的任务型枚举。**

### 所以 R854 那 20+ 段里的归属有两种

1. **站**（Nike / PopMart / JohnLewis / Demandware / CollectPlus / …）
2. **任务变体**（raffle / sweepstake / lottery / PayPal 信用卡）

**而变体这一层，复刻件只做了 raffle 一种。**

**这也解释了 `ProcessPaymentPaypalCreditCard` 那 11 步 —— 它可能不是某个站的流程，是「PayPal 信用卡」这个支付变体。**
"""

if "一部分是**任务变体**，不是别的站（R855" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: task-variant finding appended")

BLOCKER = """

---

## 279. 8 条之外的那些段，一部分是**任务变体**；复刻件只做了 raffle

> R855。未改产品代码。

### 一、一个猜测，两条证据

**R854 留下的问题：那 20+ 段各属哪个站。**

**我的怀疑：有些不是「别的站」，是「别的任务型」。**

**查复刻件：**

```
Raffle      96 处 / 7 个文件      ← 有
SweepStake   0 处                ← 无
Lottery      0 处                ← 无
TaskType     2 处（ThirdPartyDrivers.cs）
```

**而镜像里有这两段：**

```
GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle
FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · AddToCartMulti · AddToCartPreload
```

**所以：镜像至少有三种 raffle 族变体（raffle / sweepstake / lottery），复刻件只有第一种。**

### 二、这解释了 R854 里最长的那一段

**11 步的 `FindProduct · AddToCart · SubmitDiscount · GetCheckout · GetShippingRates ·
GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` ——**

**`ProcessPaymentPaypalCreditCard` 这个名字不是任何一个站的，是「PayPal 信用卡」这个支付变体。**

**所以 20+ 段的归属至少有两层：站与变体。而我前面一直只按站想。**

### 三、对判据 (f) 的意义

**(f) 要求「原版站点与风控清单从二进制取证 ↔ `Registry.cs` 与 `Flows/Scripts` 逐条对」。**

**这一轮说明那张表至少需要三列而不是两列：**

| 维度 | 复刻件状态 |
|---|---|
| **站** | Nike · PopMart · JohnLewis · Demandware ×2 · CollectPlus · structure-token ×2 · 另有 20+ 段的站未认 |
| **任务变体** | **raffle 有；sweepstake 无；lottery 无；PayPal 信用卡无** |
| **风控** | Kasada（`KasadaSolvers` / `KasadaClearance`）· Cloudflare（`CloudflareClearance`）· `HandleBlock` 未接 |

**「站 × 变体」这个矩阵，比单纯的站点清单更接近 (f) 要的东西。**

### 四、验证

```
grep SweepStake / Sweepstake / Lottery 全 src  -> 0
grep Raffle                               -> 96（7 文件）
grep TaskType                             -> 2（ThirdPartyDrivers.cs）
镜像: 0x1433712d6 GetSweepStakeCheckout … EnterSweepStakesRaffle
镜像: 0x1434b3109 … GetLotteryForm · SubmitLottery …
镜像: 0x143391b79 … ProcessPaymentPaypalCreditCard
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **sweepstake / lottery 是不是真的任务型**：**Inference（中）** ——
  名字里有 `Checkout` 与 `Raffle`，**但也可能只是某些站的结账变体。**
- **镜像的任务型枚举长什么样**：**Unknown** ——
  **`PopMartProductType` 是唯一见过的类型标记，通用任务型没找到。**
- **那 20+ 段里哪些是站、哪些是变体**：**Unknown** —— **这一轮只认了 3 段（sweepstake / lottery / PayPal）。**

### 六、教训

**R854 我写「那 20+ 段各属哪个站」，把归属当成了一个维度。**
**而 `ProcessPaymentPaypalCreditCard` 这个名字一看就不是站 —— 它是支付方式。**

**一个「段属于谁」的问题，被我默认成「属于哪个站」，是因为前面十几轮全在按站数。**
**而 (f) 要的其实是「站 × 变体 × 风控」的矩阵，不是一列站名。**
"""

VERDICT = """

---

## 第 855 轮：8 条之外的段，一部分是任务变体

### 一个猜测，两条证据

```
Raffle      96 处 / 7 文件   ← 有         SweepStake  0   ← 无         Lottery  0   ← 无
```

**而镜像里有：**
```
GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle
FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · …
```

**→ 镜像至少三种 raffle 族变体（raffle / sweepstake / lottery），复刻件只有第一种。**

### 这解释了 R854 里最长的那段

**11 步的 `… GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` ——
`ProcessPaymentPaypalCreditCard` 不是任何一个站，是「PayPal 信用卡」这个支付变体。**

**所以「段属于谁」至少有两层：站与变体。而我前面一直只按站想。**

### 对 (f) 的意义：那张表需要三列

| 维度 | 复刻件状态 |
|---|---|
| 站 | Nike · PopMart · JohnLewis · Demandware ×2 · CollectPlus · structure-token ×2 · **另 20+ 段未认** |
| **任务变体** | **raffle 有；sweepstake 无；lottery 无；PayPal 信用卡无** |
| 风控 | Kasada · Cloudflare · **`HandleBlock` 未接** |

> **「站 × 变体 × 风控」这个矩阵，比单纯的站点清单更接近 (f) 要的东西。**

### 仍然 Unknown

**sweepstake / lottery 是否真是任务型**（Inference 中，名字里有 `Checkout`/`Raffle`，也可能只是某些站的结账变体）·
**镜像的任务型枚举长什么样**（只见过 `PopMartProductType`）· **20+ 段里哪些是站哪些是变体**（本轮只认了 3 段）

### 教训

**一个「段属于谁」的问题，被我默认成「属于哪个站」，是因为前面十几轮全在按站数。**
**而 `ProcessPaymentPaypalCreditCard` 这个名字一看就不是站。**
"""

BACKLOG_ADD = """

## 判据 (f) — 站 × 变体 × 风控 三层（R855）

**复刻件覆盖差别：**

| 变体 | 镜像步骤 | 复刻件 |
|---|---|---|
| raffle | （`RaffleFlow`，R835 查过 r419/lndg/nodnod） | **96 处 / 7 文件** |
| **sweepstake** | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` | **0** |
| **lottery** | `… GetLotteryForm · SubmitLottery …` | **0** |
| **PayPal 信用卡** | `… GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` | 未查 |

**`TaskType` 在复刻件只 2 处（`ThirdPartyDrivers.cs`），无任务型枚举。**

### (f) 的表需要三列而非一列

| 维度 | 状态 |
|---|---|
| 站 | 8 条已记 + **20+ 段未认** |
| **任务变体** | raffle 有；sweepstake / lottery / PayPal 信用卡 无 |
| 风控 | Kasada · Cloudflare · **`HandleBlock` 未接** |

| 仍 Unknown | |
|---|---|
| sweepstake/lottery 是否真是任务型 | Inference 中 |
| 镜像的任务型枚举 | 只见过 `PopMartProductType` |
| 20+ 段哪些是站哪些是变体 | 本轮只认 3 段 |

**纪律**：**「段属于谁」被我默认成「属于哪个站」—— 因为前面十几轮全在按站数。而 `ProcessPaymentPaypalCreditCard` 一看就不是站。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R855", BLOCKER)
    ensure(RSTATUS, "R855", BLOCKER)
    ensure(RVERDICT, "第 855 轮", VERDICT)
    ensure(BACKLOG, "R855", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R855" not in h:
        h += ("\n## R855 补充 — 站 × 变体 × 风控\n\n"
              "**8 条之外的段一部分是任务变体**：raffle 有（96 处）· **sweepstake 0 · lottery 0**。\n"
              "**`ProcessPaymentPaypalCreditCard` 那 11 步不是站，是支付变体** —— 「段属于谁」至少两层。\n"
              "**→ 判据 (f) 的表需要三列：站 / 任务变体 / 风控**，而不是一列站名。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R855"), (RSTATUS, "R855"), (RVERDICT, "第 855 轮"), (BACKLOG, "R855")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R855: some runs outside the eight are task variants, and the replica has only raffle\n\n"
         "R854 left open which site each of the twenty-odd runs belongs to. The suspicion was that some belong to no"
         " site but to a task variant, and two probes support it. The replica mentions Raffle ninety-six times across"
         " seven files and mentions SweepStake and Lottery not at all. The image carries both: a four-step run with"
         " GetSweepStakeCheckout, GetSweepStakesShippingMethod, SubmitSweepStakesShipping and EnterSweepStakesRaffle,"
         " and a seven-step run containing GetLotteryForm and SubmitLottery.\n\n"
         "So the raffle family has three variants in the image and one in the replica, and TaskType appears twice in the"
         " whole replica with no task-type enumeration behind it.\n\n"
         "That also explains the longest of the unclaimed runs. Its last step is ProcessPaymentPaypalCreditCard, which is"
         " not a site at all but a payment variant -- so ownership has at least two layers, site and variant, and the"
         " previous rounds only ever asked about sites.\n\n"
         "For criterion (f) this changes the shape of the table it asks for. A single list of stores is not enough; what"
         " the evidence supports is a matrix of site by task variant by risk vendor. Against that, the replica covers"
         " eight recorded flow sequences plus raffle, with sweepstake, lottery and the PayPal card path absent, and"
         " HandleBlock still unwired from the Kasada sequence R854 found it in.\n\n"
         "Unknown: whether sweepstake and lottery are genuinely task types, since their names contain Checkout and Raffle"
         " and they could equally be checkout variants of particular stores, which would make them a site-layer matter"
         " rather than a variant layer one; what the image's task-type enumeration looks like, given that"
         " PopMartProductType is the only type marker seen and no general one was found; and which of the twenty-odd runs"
         " belong to sites versus variants, of which this round identified three.\n\n"
         "The lesson is about the shape of a question. I wrote 'which site does each run belong to' and never noticed the"
         " assumption inside it. One glance at ProcessPaymentPaypalCreditCard refutes it, and the reason I missed it is"
         " that a dozen consecutive rounds had been counting sites.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
