"""Record R851: one generic sequence against eight per-flow sequences -- the structural answer."""

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
### 结构性发现：**一条通用序列 vs 八条按流程的序列**（R851）

**复刻件：`StoreFlowRunner` 驱动一条通用 21 步序列，所有流程共用。**

```
GetHome · GetCsrf · GetSession · FindProduct · FindVariant · CreateCart · AddToCart
GetCart · EditLine · InitiateCheckout · GetCheckout · SubmitEmail · SubmitShipping
GetShippingRates · SubmitShippingMethod · SubmitBilling · SubmitDiscount · SubmitPayment
GetPaymentToken · SubmitOrder · ProcessOrder
```

**镜像：每个流程有自己的序列**（`StoreFlowSteps`，带该流程自己的 `d__N` 序号）：

| 流程 | 步数 | 与通用 21 步的关系 |
|---|---|---|
| Nike | 16 | 有 `ValidateAddress` `CheckInventory` `GetShopperIp` `GetPaymentMethods` —— 通用序列里没有位置 |
| PopMart | 24 | 抽签/展览/预约 17 步 —— **结账序列根本表达不了** |
| JohnLewis | 19 | 有 `WebHandOver` `GuestCallback` `AuthenticatePayment` —— 流程专属 |
| Demandware 经典 | 12 | 与通用接近，但少 `SubmitEmail` 多 `ConfirmPayment` |
| Demandware 双路 | 15 | 有 `StartAppFast` `GetCartDw` 等双路词汇 |
| CollectPlus | 17 | 有 `GetCollectPlusLocations` `SubmitCollectPlus` |
| structure-token ×2 | 15 / 12 | 有 `GetStructureToken` `CalculateTaxes` `ProcessTransaction` |

**这就是「14 个抽签步骤写不进 `PopMartFlow`」的真实原因：不是方法没写，是 runner 里没有它们的位置。**

**也是 Nike「10 个细步 vs 3 个粗步」的真实原因：通用序列没有 `ValidateAddress` 这一步，只能并进 `SubmitShipping`。**
"""

if "一条通用序列 vs 八条按流程的序列（R851" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: structural finding appended")

BLOCKER = """

---

## 275. **结构性发现**：复刻件一条通用 21 步序列，镜像八条按流程的序列

> R851。未改产品代码。**这一条解释了前面十几轮遇到的全部现象。**

### 一、R850 那个前置问题，答案比预期大

R850 问「`StoreFlowRunner` 的调用序与 `StoreFlowSteps` 的 ordinal 是否一致」。

**答案：不一致，而且不是顺序不一致 —— 是 runner 根本不用 ordinal。**

**`StoreFlowRunner.RunCheckoutAsync` 里是一条手写的固定元组序列，21 步，所有流程共用：**

```
 1 GetHome                 8 GetCart                15 SubmitShippingMethod
 2 GetCsrf                 9 EditLine               16 SubmitBilling
 3 GetSession             10 InitiateCheckout       17 SubmitDiscount
 4 FindProduct            11 GetCheckout            18 SubmitPayment
 5 FindVariant            12 SubmitEmail            19 GetPaymentToken
 6 CreateCart             13 SubmitShipping         20 SubmitOrder
 7 AddToCart              14 GetShippingRates       21 ProcessOrder
```

### 二、而镜像是每个流程一条序列

| 流程 | 步数 | 序列里有什么是通用序列没有的 |
|---|---|---|
| Nike | 16 | `ValidateAddress` · `CheckInventory` · `GetShopperIp` · `GetPaymentMethods` · `SubmitCustomer` |
| PopMart | 24 | 抽签/展览/预约 **17 步** |
| JohnLewis | 19 | `WebHandOver` · `SessionHandover` · `GuestCallback` · `AuthenticatePayment` |
| Demandware 经典 | 12 | `GenerateCSRF` · `SubmitConsignment` · `ConfirmPayment` |
| Demandware 双路 | 15 | `StartAppFast` · `StartAppSafe` · `GetCartDw` · `SaveSessionDw` |
| CollectPlus | 17 | `GetCollectPlusLocations` · `SubmitCollectPlus` |
| structure-token ×2 | 15 / 12 | `GetStructureToken` · `CalculateTaxes` · `CreateTransaction` · `ProcessPayment` |

**而镜像是「每个流程一条自己的序列」—— 那些 `d__N` 序号就是该流程内部的顺序，
不是一张全局表里的编号。**

### 三、这一条解释了前面所有现象

| 现象 | 真正的原因 |
|---|---|
| Nike 10 个细步 vs 复刻件 3 个粗步（R843） | **通用序列没有 `ValidateAddress` 的位置，只能并进 `SubmitShipping`** |
| PopMart 14 个抽签步骤写不进（R849/R850） | **结账序列根本表达不了抽签流程** |
| John Lewis 的 `WebHandOver` 等无处安放（R847） | **流程专属步骤在通用序列里没有对应位置** |
| R844 那个 16.9% | **在拿「通用序列的名字」对「八条流程的步骤名」** |

**所以判据 (f) 那条「未覆盖的每条写为什么」，现在有了统一的答案：**

> **不是因为端点缺、不是因为方法没写、不是因为粒度 —— 是因为复刻件用一条通用序列去覆盖八条不同的序列。**

**个体差异（少 14 个方法、少 10 个细步）都是这个结构差的表现。**

### 四、这意味着什么工作量

**要让 PopMart 的 24 步真的跑起来，`PopMartFlow` 里加 14 个方法不够 —— runner 得能按流程取序列。**

**三种做法，代价不同：**

1. **给 `StoreFlow` 加 `IReadOnlyList<Step>`，每个流程返回自己的序列，runner 按它跑** ——
   最忠实，但要改 runner 与全部 165 个声明的调用方式
2. **给 runner 加 per-flow 分支** —— 快，但会成为一堆特例
3. **保持通用序列，把流程专属步骤塞进现有步骤内部** —— 现状，也就是「Nike 10 步并成 3 步」

**现状是 3。而 1 是唯一能让「每个函数功能相等」成立的。**
**这一轮不改 —— 这是一次架构改动，不该在一轮里顺手做。**

### 五、验证

```
StoreFlowRunner.cs 294 行；RunCheckoutAsync 的固定元组序列 21 步
grep 'flow\.' 无命中 —— 用的是 ("Name", flow.XAsync) 元组
StoreFlowSteps.cs: 8 个流程，步数 16/24/19/12/15/17/15/12，各不相同
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **镜像里 runner 那侧是怎么做的**：**Unknown** ——
  如果镜像也是「一个调度器按流程取序列」，那做法 1 就是忠实复刻；
  **但也可能是每个流程自己驱动自己的序列（即 8 个独立执行器）。这两种在镜像里长得很不一样，没查。**
- **`StoreFlowSteps` 的 24 步是否就是运行顺序**：**Inference（中）** ——
  ordinal 递增通常意味着顺序，**但没有证据说镜像按 ordinal 跑。**
- **改成做法 1 后现有的 165 个声明与 1766 个用例会怎样**：**Unknown** —— 影响面没估。

### 七、教训

**我前面十几轮一直在数「哪个方法没有」，而真正的问题是「执行框架的形状不同」。**

**这就像在数一栋楼缺几个房间，而实际是户型不一样 —— 房间数对不上是结果，不是原因。**

**而发现它的路径很便宜：R850 问了一个前置问题（「runner 用 ordinal 吗」），
答案一读代码就有。那个前置问题我本该在 R849 之前就问。**
"""

VERDICT = """

---

## 第 851 轮：结构性发现 —— 一条通用序列 vs 八条按流程的序列

### R850 的前置问题，答案比预期大

**`StoreFlowRunner` 不用 ordinal。它是一条手写的固定元组序列，21 步，所有流程共用：**

```
GetHome · GetCsrf · GetSession · FindProduct · FindVariant · CreateCart · AddToCart
GetCart · EditLine · InitiateCheckout · GetCheckout · SubmitEmail · SubmitShipping
GetShippingRates · SubmitShippingMethod · SubmitBilling · SubmitDiscount · SubmitPayment
GetPaymentToken · SubmitOrder · ProcessOrder
```

**而镜像是每个流程一条自己的序列**（Nike 16 · PopMart 24 · JohnLewis 19 · Demandware 12/15 · CollectPlus 17 · structure-token 15/12）。
**那些 `d__N` 序号是该流程内部的顺序，不是一张全局表的编号。**

### 这一条解释了前面所有现象

| 现象 | 真正的原因 |
|---|---|
| Nike 10 细步 vs 3 粗步（R843） | **通用序列没有 `ValidateAddress` 的位置** |
| PopMart 14 抽签步骤写不进（R849/R850） | **结账序列根本表达不了抽签流程** |
| John Lewis 的 `WebHandOver` 无处安放（R847） | **流程专属步骤没有对应位置** |
| R844 的 16.9% | **拿「通用序列的名字」对「八条流程的步骤名」** |

> **判据 (f) 的「未覆盖的每条写为什么」，统一答案：**
> **不是端点缺、不是方法没写、不是粒度 —— 是复刻件用一条通用序列覆盖八条不同的序列。**

### 改起来有多大

1. **`StoreFlow` 加 `IReadOnlyList<Step>`，每流程返回自己的序列，runner 按它跑** —— 最忠实，要动 runner 与 165 个声明
2. **runner 加 per-flow 分支** —— 快，会成为一堆特例
3. **保持通用序列，专属步骤塞进现有步骤内部** —— **现状**

**现状是 3；只有 1 能让「每个函数功能相等」成立。本轮不改 —— 架构改动不该在一轮里顺手做。**

### 仍然 Unknown

**镜像那侧是怎么组织的**（也是一个调度器按流程取序列，还是 8 个独立执行器 —— 两者长得很不一样，未查）·
**24 步的 ordinal 递增是否就是运行顺序**（Inference 中）· **改成做法 1 对 165 个声明与 1766 个用例的影响**（未估）

### 教训

**前面十几轮一直在数「哪个方法没有」，而真正的问题是「执行框架的形状不同」。**
**像在数一栋楼缺几个房间，而实际是户型不一样 —— 房间数对不上是结果，不是原因。**

**发现它的路径很便宜：R850 问了一个前置问题，答案一读代码就有。那个前置问题本该在 R849 之前就问。**
"""

BACKLOG_ADD = """

## 判据 (f) — 结构性发现（R851）：一条通用序列 vs 八条按流程序列

**`StoreFlowRunner.RunCheckoutAsync` = 手写固定 21 步元组序列，所有流程共用；不用 `StoreFlowSteps` 的 ordinal。**

```
GetHome GetCsrf GetSession FindProduct FindVariant CreateCart AddToCart GetCart EditLine
InitiateCheckout GetCheckout SubmitEmail SubmitShipping GetShippingRates
SubmitShippingMethod SubmitBilling SubmitDiscount SubmitPayment GetPaymentToken SubmitOrder ProcessOrder
```

**镜像：每流程一条序列** —— Nike 16 · PopMart 24 · JohnLewis 19 · DW 12/15 · CollectPlus 17 · ST 15/12。

### 统一解释

| 现象 | 原因 |
|---|---|
| Nike 10 细步 vs 3 粗步 | 通用序列没有 `ValidateAddress` 位置 |
| PopMart 14 抽签步写不进 | 结账序列表达不了抽签流程 |
| JohnLewis `WebHandOver` 无处放 | 流程专属步骤无对应位置 |
| R844 的 16.9% | 拿通用序列名字对八条流程步骤名 |

> **(f) 的「为什么」统一答案：不是端点缺、不是方法没写、不是粒度，是执行框架形状不同。**

### 三种改法

1. **`StoreFlow` 加 `IReadOnlyList<Step>`，runner 按流程取** —— 最忠实，动 runner + 165 声明
2. **runner 加 per-flow 分支** —— 快，成堆特例
3. **保持通用序列，专属步骤塞进现有步骤** —— **现状**

**只有 1 能让「每个函数功能相等」成立。本轮不改 —— 架构改动不该一轮顺手做。**

| 仍 Unknown | |
|---|---|
| 镜像那侧怎么组织 | 一个调度器按流程取序列 vs 8 个独立执行器 —— 未查 |
| ordinal 递增是否即运行顺序 | Inference（中） |
| 做法 1 对 165 声明 + 1766 用例的影响 | 未估 |

**纪律**：**「缺几个方法」和「户型不一样」是两个诊断；我前面十几轮一直在做前者。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R851", BLOCKER)
    ensure(RSTATUS, "R851", BLOCKER)
    ensure(RVERDICT, "第 851 轮", VERDICT)
    ensure(BACKLOG, "R851", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R851" not in h:
        h += ("\n## R851 补充 — 结构性发现\n\n"
              "**`StoreFlowRunner` 是一条手写固定 21 步序列，所有流程共用；不用 `StoreFlowSteps` 的 ordinal。**\n"
              "**镜像每个流程一条自己的序列**（Nike 16 · PopMart 24 · JohnLewis 19 · DW 12/15 · CollectPlus 17 · ST 15/12）。\n"
              "**统一解释了 Nike 10 细步 vs 3 粗步、PopMart 14 抽签步写不进、JohnLewis 专属步骤无处放、R844 的 16.9%。**\n"
              "**(f) 的「为什么」：不是端点缺/方法没写/粒度，是**执行框架形状不同**。\n"
              "三种改法：① `StoreFlow` 加 `IReadOnlyList<Step>` 按流程取（最忠实）② runner 加 per-flow 分支 ③ 现状。**只有 ① 能让「功能相等」成立，本轮未改。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R851"), (RSTATUS, "R851"), (RVERDICT, "第 851 轮"), (BACKLOG, "R851")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R851: one generic sequence against eight per-flow sequences, which is the shape of the whole gap\n\n"
         "R850 asked whether the runner's call order matches the ordinals StoreFlowSteps records. The answer is larger"
         " than the question: the runner does not use ordinals at all. RunCheckoutAsync holds a hand-written tuple list"
         " of twenty-one steps, the same list for every flow -- GetHome, GetCsrf, GetSession, FindProduct, FindVariant,"
         " CreateCart, AddToCart, GetCart, EditLine, InitiateCheckout, GetCheckout, SubmitEmail, SubmitShipping,"
         " GetShippingRates, SubmitShippingMethod, SubmitBilling, SubmitDiscount, SubmitPayment, GetPaymentToken,"
         " SubmitOrder, ProcessOrder.\n\n"
         "The image instead gives each flow its own sequence, and the d__N ordinals are that flow's internal order rather"
         " than positions in one global table: Nike sixteen steps, Pop Mart twenty-four, John Lewis nineteen, Demandware"
         " twelve and fifteen, CollectPlus seventeen, the two structure-token flows fifteen and twelve.\n\n"
         "That single fact explains everything the previous rounds kept finding one at a time. Nike's ten fine checkout"
         " stages collapse into three coarse ones because the generic sequence has no slot for ValidateAddress or"
         " CheckInventory. Pop Mart's fourteen draw steps cannot be written because a checkout sequence has no way to"
         " express a draw at all. John Lewis's WebHandOver and GuestCallback have nowhere to sit. And R844's 16.9 percent"
         " was comparing one generic sequence's names against eight flows' step names.\n\n"
         "So criterion (f)'s demand that every uncovered item state why now has one answer instead of a hundred: not a"
         " missing endpoint, not an unwritten method, not granularity, but a different execution shape. The individual"
         " deficits are symptoms of it.\n\n"
         "Making Pop Mart's twenty-four steps actually run is therefore not fourteen methods. It needs the runner to"
         " take a sequence per flow, which means giving StoreFlow a step list and changing how 165 declarations are"
         " invoked. The cheap alternative, per-flow branches in the runner, becomes a pile of special cases; the current"
         " arrangement is the third option and is what exists. Only the first makes every function behave the same, and"
         " it is an architectural change that should not be slipped into a round that started by reading one file.\n\n"
         "Unknown: how the image organises this on its side, since a dispatcher that takes a per-flow sequence and eight"
         " independent executors look very different in disassembly and this round did not check; whether increasing"
         " ordinals are the run order, which is inference rather than observation; and what changing to a per-flow"
         " sequence does to the 165 declarations and the 1766 tests, which was not estimated.\n\n"
         "The lesson is about diagnosis rather than evidence. For a dozen rounds I counted which methods were missing,"
         " when the question was that the execution frame has a different shape -- like counting a building's missing"
         " rooms when the floor plan itself differs. The rooms not adding up is a consequence. And the discovery was"
         " cheap: R850 asked one prerequisite question, and reading the runner answered it. That question belonged before"
         " R849, not after it.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
