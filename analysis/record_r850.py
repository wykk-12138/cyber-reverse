"""Record R850: what the image does and does not tell us about implementing the draw steps."""

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
### PopMart 14 个抽签步骤：证据够写几个，不够写几个（R850）

**镜像里能查到的 draw 参数记号：**

```
_uniqCode       0x1433803a5      字段名
currentUniqCode 0x146fda6d4
storeUniqCode   0x1471647ac
&storeUniqCode=1 0x146a85e4c     查询串片段
Drawno          0x143902b40      属性名
```

| 步骤 | 端点 | 够不够写 |
|---|---|---|
| `StartDrawFlow` | `detail?uniqCode=` | **参数有证据**（`uniqCode` + `storeUniqCode`）→ 可写 |
| `FindDraw` | `detail?uniqCode=` | 同上 → 可写 |
| `EnterDraw` | `drawScratch/draw` | **请求体无证据** → 不可写 |
| `ChooseGoods` | `drawScratch/chooseGoods` | **请求体无证据** → 不可写 |
| `FindMegaDraw` · `EnterDrawEvent` | `megaDraw/hit` | 不可写 |
| `RedeemMemberPoints` · `RedeemLuckPoints` | `redeem/*` | 不可写 |
| `FindExhibit` · `EnterExhibit` | `storeOfflineDraw/*` | 不可写 |
| `FindDates` · `FindTimeSlots` | `store_ticket/*` | 不可写 |
| `EnterReservation` | `storeOfflineDraw/join` | 不可写 |
| `GetOrders` | `order/list` | 可写（与复刻件 `GetOrders` 同样式） |

**所以：3 个可写（`StartDrawFlow` `FindDraw` `GetOrders`），11 个只有端点没有形状。**

**而那 11 个不写的理由与 R823 删 CSRF 兜底是同一条：**
**一个能发请求但不知道发什么的方法，比一个不存在的步骤更坏 —— 它会让「14 步已实现」这句话看起来成立。**
"""

if "证据够写几个，不够写几个（R850" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: evidence boundary appended")

BLOCKER = """

---

## 274. 那 14 个抽签步骤：**3 个可写，11 个只有端点没有形状**

> R850（第 400 轮）。未改产品代码。

### 一、可查到的参数证据

```
_uniqCode        0x1433803a5    字段名
currentUniqCode  0x146fda6d4
storeUniqCode    0x1471647ac
&storeUniqCode=1 0x146a85e4c    查询串片段
Drawno           0x143902b40    属性名
```

**所以 `detail?uniqCode=` 这条能写出真请求：`uniqCode` 从哪来、`storeUniqCode` 是查询参数，都有记号。**

### 二、逐步骤判定

| 步骤 | 端点 | 够不够写 |
|---|---|---|
| `StartDrawFlow` | `detail?uniqCode=` | **可写** |
| `FindDraw` | `detail?uniqCode=` | **可写** |
| `GetOrders` | `order/list` | **可写**（与复刻件同样式） |
| `EnterDraw` | `drawScratch/draw` | 请求体无证据 |
| `ChooseGoods` | `drawScratch/chooseGoods` | 请求体无证据 |
| `FindMegaDraw` `EnterDrawEvent` | `megaDraw/hit` | 无 |
| `RedeemMemberPoints` `RedeemLuckPoints` | `redeem/*` | 无 |
| `FindExhibit` `EnterExhibit` `EnterReservation` | `storeOfflineDraw/*` | 无 |
| `FindDates` `FindTimeSlots` | `store_ticket/*` | 无 |

**3 可写 · 11 不可写。**

### 三、为什么那 11 个不写

**与 R823 删掉 CSRF 兜底是同一条：**

> **一个能发请求但不知道发什么的方法，比一个不存在的步骤更坏 —— 它会让「14 步已实现」这句话看起来成立。**

**而写 3 个、留 11 个，也会让覆盖率看起来像 3/14 而不是 0/14 ——
所以我要在文档里写清「可写的是这 3 个，其余 11 个卡在响应形状」，而不是先写 3 个再去数。**

### 四、这一轮实际没改代码，理由

**写那 3 个还牵涉两步：**

1. **`StoreFlowRunner` 的步骤序列是固定的** —— 加步骤要同时改 runner，不只是加方法
2. **`PopMartFlow` 的 24 步在 `StoreFlowSteps` 里有序号，而 runner 的调用表未必按那个序号走**

**所以「加 3 个方法」不是 3 个方法的活，是「方法 + runner + 测试」的活，而且第 2 点要先查清。
本轮只做到「查清证据边界」，没有动代码。这是刻意的：把边界写清楚比先写一半更有用。**

### 五、验证

```
ida.py str drawScratch   -> 4 matches（四条端点）
ida.py str uniqCode      -> 5 matches（_uniqCode / currentUniqCode / storeUniqCode / &storeUniqCode=1 / detail?uniqCode=）
ida.py str Drawno        -> 1 match
PopMartEndpoints.cs: 39 个端点，14 个抽签/展览/预约端点全在（R849）
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`EnterDraw` / `ChooseGoods` 的请求体**：**Unknown** —— 镜像里没有对应的字段名记号。**这是 11 步里最关键的两步。**
- **`StartDrawFlow` 的 `uniqCode` 从哪来**：**Unknown** —— 可能是从商品页或 `detail` 的响应里取；
  **`currentUniqCode` 这个记号暗示有「当前」的概念，但没证。**
- **`StoreFlowRunner` 的步骤序列是否按 `StoreFlowSteps` 的序号**：**Unknown** —— **这是加步骤的前置条件。**

### 七、教训

**第 400 轮，而这一轮的产出是「3 个能写、11 个不能写、以及为什么」。**

**这个结论不好看，但它比「14 个都写了（其实就是都发了个 GET）」好。**
**而 R823 那次删 CSRF 兜底、和这一轮不写那 11 个，是同一条标准的两端：**
**宁可缺，也不要一个有形状没内容的实现。**
"""

VERDICT = """

---

## 第 850 轮（第 400 轮）：14 个抽签步骤，3 个可写、11 个只有端点没有形状

### 可查到的参数证据

```
_uniqCode · currentUniqCode · storeUniqCode · &storeUniqCode=1 · Drawno
```

**所以 `detail?uniqCode=` 能写出真请求。**

### 逐步骤判定：3 可写 · 11 不可写

| 可写 | `StartDrawFlow` · `FindDraw`（`detail?uniqCode=`）· `GetOrders`（`order/list`） |
|---|---|
| **不可写** | `EnterDraw` · `ChooseGoods` · `FindMegaDraw` · `EnterDrawEvent` · `RedeemMemberPoints` · `RedeemLuckPoints` · `FindExhibit` · `EnterExhibit` · `EnterReservation` · `FindDates` · `FindTimeSlots` |

### 为什么那 11 个不写

> **一个能发请求但不知道发什么的方法，比一个不存在的步骤更坏 —— 它会让「14 步已实现」这句话看起来成立。**

**与 R823 删 CSRF 兜底是同一条标准的两端：宁可缺，也不要一个有形状没内容的实现。**

### 而写那 3 个也不是 3 个方法的活

**① `StoreFlowRunner` 的步骤序列是固定的，加步骤要同时改 runner；**
**② `PopMartFlow` 的 24 步在 `StoreFlowSteps` 里有序号，而 runner 的调用表未必按那个序号走 —— 这条要先查清。**

**所以本轮只做到「查清证据边界」，没动代码。把边界写清楚比先写一半更有用。**

### 仍然 Unknown

**`EnterDraw`/`ChooseGoods` 的请求体**（11 步里最关键的两步，镜像无字段名记号）·
**`uniqCode` 从哪来**（`currentUniqCode` 暗示有「当前」概念，未证）·
**runner 步骤序列是否按 `StoreFlowSteps` 的序号**（加步骤的前置条件）

### 教训

**第 400 轮的产出是「3 个能写、11 个不能写、以及为什么」。这个结论不好看，但它比「14 个都写了（其实就是都发了个 GET）」好。**
"""

BACKLOG_ADD = """

## 优先级 ① — PopMart 14 抽签步骤的证据边界（R850）

**参数记号（镜像）：** `_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1` · `Drawno`

| 判定 | 步骤 |
|---|---|
| **可写（3）** | `StartDrawFlow` · `FindDraw`（`detail?uniqCode=`）· `GetOrders` |
| **只有端点、无请求形状（11）** | `EnterDraw` `ChooseGoods` `FindMegaDraw` `EnterDrawEvent` `RedeemMemberPoints` `RedeemLuckPoints` `FindExhibit` `EnterExhibit` `EnterReservation` `FindDates` `FindTimeSlots` |

**不写这 11 个的理由（与 R823 同一条）**：
**能发请求但不知道发什么的方法，比不存在的步骤更坏 —— 它让「14 步已实现」看起来成立。**

### 写那 3 个的前置条件（未查）

1. `StoreFlowRunner` 的步骤序列固定 → 加步骤要同时改 runner
2. **`StoreFlowSteps` 的 ordinal ↔ runner 调用表是否一致** —— **加步骤前必须查清**

| 仍 Unknown | |
|---|---|
| `EnterDraw`/`ChooseGoods` 请求体 | **11 步里最关键的两步**，镜像无字段名记号 |
| `uniqCode` 来源 | `currentUniqCode` 暗示「当前」概念，未证 |
| runner 序列 ↔ `StoreFlowSteps` ordinal | **加步骤的前置条件** |

**纪律**：**宁可缺，也不要一个有形状没内容的实现。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R850", BLOCKER)
    ensure(RSTATUS, "R850", BLOCKER)
    ensure(RVERDICT, "第 850 轮", VERDICT)
    ensure(BACKLOG, "R850", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R850" not in h:
        h += ("\n## R850 补充 — PopMart 14 步的证据边界\n\n"
              "**3 可写**：`StartDrawFlow` `FindDraw`（`detail?uniqCode=`，参数记号 `_uniqCode`/`storeUniqCode` 都在）· `GetOrders`。\n"
              "**11 只有端点、无请求形状**：`EnterDraw` `ChooseGoods` 等 —— **不写，理由与 R823 删 CSRF 兜底同一条**：\n"
              "**能发请求但不知道发什么的方法，比不存在的步骤更坏。**\n"
              "**写那 3 个的前置条件**：`StoreFlowRunner` 序列固定，且 **`StoreFlowSteps` 的 ordinal ↔ runner 调用表是否一致未查**。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R850"), (RSTATUS, "R850"), (RVERDICT, "第 850 轮"), (BACKLOG, "R850")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R850: three of the fourteen draw steps are writable and eleven have an endpoint but no shape\n\n"
         "R849 established that the replica holds every draw endpoint and that the fourteen driver methods are what is"
         " missing. The natural next move is to write them, so this round asked what the image actually says about the"
         " requests.\n\n"
         "It says more than nothing. The string pool carries _uniqCode, currentUniqCode, storeUniqCode, a query fragment"
         " &storeUniqCode=1, and Drawno. So detail?uniqCode= can be called for real: uniqCode has a field name and"
         " storeUniqCode is a query parameter, both evidenced. That makes StartDrawFlow and FindDraw writable, and"
         " GetOrders writable on the same pattern the replica already uses for order lists -- three of fourteen.\n\n"
         "The other eleven have an endpoint and nothing else. EnterDraw against drawScratch/draw, ChooseGoods against"
         " drawScratch/chooseGoods, the megaDraw hit, the two redeem calls, the exhibit and reservation paths and the"
         " two ticket reads: none of them has a request body the image names. Writing them would mean sending a request"
         " whose shape I invented, and that is worse than not writing them, because a method that issues a request makes"
         " 14 of 14 steps look implemented while eleven of them would be guesses. It is the same standard that removed"
         " the fabricated CSRF token in R823, from the other end: prefer missing to present-and-empty.\n\n"
         "Writing even the three is not three methods of work. The runner's step sequence is fixed, so adding steps"
         " changes it too; and whether the runner's call order matches the ordinals StoreFlowSteps records is not"
         " established, which has to be settled before inserting anything. So this round did not touch code. It mapped"
         " the evidence boundary instead, which is the more useful output: three writable, eleven blocked on request"
         " shape, and the two questions that gate the writable three.\n\n"
         "A milestone round producing a boundary rather than an implementation is the right shape. The unattractive"
         " answer -- three of fourteen, with reasons -- is worth more than fourteen methods that all fire a GET.\n\n"
         "Unknown: the request bodies for EnterDraw and ChooseGoods, the two that matter most among the eleven, since the"
         " image names no field for either; where uniqCode comes from, with currentUniqCode hinting at a notion of"
         " current without settling it; and whether the runner's sequence follows the recorded ordinals, which gates"
         " every step insertion.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
