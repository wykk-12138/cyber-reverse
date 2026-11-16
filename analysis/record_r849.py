"""Record R849: PopMart's draw endpoints are all present; only the flow steps are missing."""

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
### PopMart：端点层完整，缺的是驱动它的步骤（R849）

**R116 的 `PopMartStepMap.cs` 已把 24 步里 14 步对到 `/shop/v1/*` 端点；而 `PopMartEndpoints.cs` 有 39 个端点，
那 14 个配对用的常量全在：**

| 步骤 | 端点常量 | 路径 |
|---|---|---|
| `StartDrawFlow` · `FindDraw` | `DrawScratchDetail` | `/shop/v1/drawScratch/detail?uniqCode=` |
| `EnterDraw` | `DrawScratchDraw` | `/shop/v1/drawScratch/draw` |
| `ChooseGoods` | `DrawScratchChooseGoods` | `/shop/v1/drawScratch/chooseGoods` |
| `FindMegaDraw` · `EnterDrawEvent` | `MegaDrawHit` | `/shop/v1/drawScratch/megaDraw/hit` |
| `RedeemMemberPoints` | `PointsRedeemDraw` | `/shop/v1/redeem/points_redeem_draw` |
| `RedeemLuckPoints` | `LuckyPointsDraw` | `/shop/v1/redeem/lucky_points_redeem_draw` |
| `FindExhibit` | `StoreOfflineDrawInfo` | `/shop/v1/storeOfflineDraw/info?alias=` |
| `EnterExhibit` · `EnterReservation` | `StoreOfflineDrawJoin` | `/shop/v1/storeOfflineDraw/join` |
| `FindDates` | `StoreTicketDates` | `/shop/v1/store_ticket/dateList` |
| `FindTimeSlots` | `StoreTicketMainPage` | `/shop/v1/store_ticket/mainPage?uniqID=` |
| `GetOrders` | `OrderList` | `/shop/v1/order/list?...` |

**`PopMartFlow` 的 11 个重写里没有一个是上面这些步骤。**

### 修正 R835–R838

**那几轮说「复刻件没有抽签面」。按证据，准确说法是：**

> **端点层完整（39 个端点，含全部 14 个抽签/展览/预约端点）；映射表完整（R116）；
> 缺的只是 `PopMartFlow` 里那 14 个驱动步骤的方法。**

**「没有抽签面」在端点层是错的，只在步骤层成立。**
"""

if "端点层完整，缺的是驱动它的步骤（R849" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: PopMart correction appended")

BLOCKER = """

---

## 273. **修正 R835–R838**：PopMart 的抽签端点**全在**，缺的只是驱动它的步骤

> R849。未改产品代码。**这轮推翻本会话自己六轮前的一个结论。**

### 一、`PopMartStepMap.cs`（R116）一直存在

**R835–R838 六轮里我没读过它。它把 24 步里 14 步对到了 `/shop/v1/*` 端点：**

```
EnterDraw        → DrawScratchDraw          /shop/v1/drawScratch/draw
ChooseGoods      → DrawScratchChooseGoods   /shop/v1/drawScratch/chooseGoods
FindMegaDraw     → MegaDrawHit              /shop/v1/drawScratch/megaDraw/hit
RedeemLuckPoints → LuckyPointsDraw          /shop/v1/redeem/lucky_points_redeem_draw
FindExhibit      → StoreOfflineDrawInfo     /shop/v1/storeOfflineDraw/info?alias=
EnterReservation → StoreOfflineDrawJoin     /shop/v1/storeOfflineDraw/join
FindDates        → StoreTicketDates         /shop/v1/store_ticket/dateList
...
```

### 二、而那些端点在复刻件里**全都在**

**`PopMartEndpoints.cs` 有 39 个端点常量（与 R116 记的「39 endpoints」一致），上面 14 个配对用的常量逐一核对，全部存在：**

```
DrawScratchDetail      YES  /shop/v1/drawScratch/detail?uniqCode=
DrawScratchDraw        YES  /shop/v1/drawScratch/draw
DrawScratchChooseGoods YES  /shop/v1/drawScratch/chooseGoods
MegaDrawHit            YES  /shop/v1/drawScratch/megaDraw/hit
PointsRedeemDraw       YES  /shop/v1/redeem/points_redeem_draw
LuckyPointsDraw        YES  /shop/v1/redeem/lucky_points_redeem_draw
StoreOfflineDrawInfo   YES  /shop/v1/storeOfflineDraw/info?alias=
StoreOfflineDrawJoin   YES  /shop/v1/storeOfflineDraw/join
StoreTicketDates       YES  /shop/v1/store_ticket/dateList
StoreTicketMainPage    YES  /shop/v1/store_ticket/mainPage?uniqID=
OrderList              YES  /shop/v1/order/list?currentPage=1&pageSize=20
```

### 三、所以要改的是结论，不是代码

**R835 写的是「PopMart 抽签面：没有任何流程覆盖它」。R836 写「七块未建模」。R838 写「九方法子系统，十二个名字全为 0」。**

**按现在的证据，准确的说法是：**

> **端点层完整（39 个端点，含全部抽签/展览/预约端点）。
> 映射表完整（R116 的 14 对）。
> 缺的只是 `PopMartFlow` 里那 14 个驱动步骤的方法 —— `PopMartFlow` 的 11 个重写里一个都不是。**

**「没有抽签面」在端点层是错的，只在步骤层成立。**

**这是好消息也是坏消息：坏在步骤确实没写；好在要写的时候不用去查端点 —— R116 已经对好了。**

### 四、为什么六轮都没发现

**R835 我从「`PopMartBrowser` 这个类型名」出发，搜 `activity/v1/exhibit_draw` —— 那确实是个真端点，也确实没被复刻件用。
于是我判「无覆盖」。**

**而 `exhibit_draw` 是 **actapi** 上的一条路；`/shop/v1/storeOfflineDraw/join` 是**另一条路** ——
镜像同时有两条，而我只顺着第一条查。**

**`PopMartStepMap` 里那句注释正好说明了这个：**

> Where the match is exact the pair is obvious: `EnterDraw` ↔ `DrawScratchDraw`, `ChooseGoods` ↔ `DrawScratchChooseGoods` …
> Where it is a guess the step is left unmapped: `CheckResult` could be `DrawScratchDetail` or a poll of the same call,
> and nothing in the image says which.

**所以 R116 已经做完了「哪条路对哪一步」的配对，并且诚实标注了哪些是猜的、哪些留空。**

### 五、这条修正对 (f) 的意义

**判据 (f) 要求「未覆盖的每条写为什么」。这一轮给出的「为什么」是：**

> **Pop Mart 的 24 步里 14 步的端点在复刻件里都有；未覆盖的原因不是缺端点，是 `PopMartFlow` 没写那 14 个步骤方法。**

**这比「未建模」精确得多，而且指出了工作量在哪。**

### 六、验证

```
replica\\src\\Cybersole.Stores\\Flows\\PopMartStepMap.cs   70 行，R116，14 对
replica\\src\\Cybersole.Stores\\Flows\\PopMartEndpoints.cs  39 个端点常量，14 个配对常量逐一核对全在
PopMartFlow.cs: 11 个重写，无一个 draw/exhibit/reservation 步骤
本轮未改产品代码
七项度量沿用
```

### 七、仍然 Unknown

- **`CheckResult` 对哪个端点**：**Unknown，且 R116 已诚实留空** —— 「可能是 `DrawScratchDetail` 或对同一调用的轮询，镜像里没说」。
- **剩下 10 步（24 − 14）的端点**：**Unknown** —— `UnmappedSteps` 是数据，不是遗漏。
- **`activity/v1/exhibit_draw` 那条路与 `/shop/v1/storeOfflineDraw/join` 的关系**：**Unknown** ——
  **镜像有两条路，R116 对的是后者，前者（我在 R835 查的）没有配对。**

### 八、教训

**我六轮前判「没有」，依据是「我查的那条路没有」。而镜像有两条路。**

**这次挡住我的东西和前面几次不同：不是「没读仓里的文件」，是「查了一条路就当成全部路」。**
**而 R116 的文件名摆在那里（`PopMartStepMap`），我六轮里没点开过。**
"""

VERDICT = """

---

## 第 849 轮：修正 R835–R838 —— PopMart 抽签端点全在，缺的只是驱动步骤

### `PopMartStepMap.cs`（R116）一直存在，六轮里没读

24 步里 14 步已对到 `/shop/v1/*`：`EnterDraw→DrawScratchDraw` · `ChooseGoods→DrawScratchChooseGoods` ·
`FindMegaDraw→MegaDrawHit` · `RedeemLuckPoints→LuckyPointsDraw` · `FindDates→StoreTicketDates` …

### 而那些端点在复刻件里全在

`PopMartEndpoints.cs` **39 个端点常量**，14 个配对常量**逐一核对全部存在**：

```
DrawScratchDetail YES · DrawScratchDraw YES · DrawScratchChooseGoods YES · MegaDrawHit YES
PointsRedeemDraw YES · LuckyPointsDraw YES · StoreOfflineDrawInfo YES · StoreOfflineDrawJoin YES
StoreTicketDates YES · StoreTicketMainPage YES · OrderList YES
```

### 所以要改的是结论

> **端点层完整 · 映射表完整（R116）· 缺的只是 `PopMartFlow` 里那 14 个驱动方法** ——
> **它的 11 个重写里一个都不是 draw/exhibit/reservation 步骤。**

**「没有抽签面」在端点层是错的，只在步骤层成立。**

### 为什么六轮没发现

**R835 我从 `PopMartBrowser` 出发，搜 `activity/v1/exhibit_draw` —— 那是 actapi 上的一条真路，也确实没被用。于是我判「无覆盖」。**
**而 `/shop/v1/storeOfflineDraw/join` 是**另一条路**。镜像同时有两条，我只顺着第一条查。**

**`PopMartStepMap` 的注释正是这件事的说明，而且标注了哪些配对是猜的（`CheckResult` 留空）。**

### 对 (f) 的意义

**(f) 要「未覆盖的每条写为什么」。这轮给出的「为什么」是：端点都有，`PopMartFlow` 没写那 14 个步骤方法。**
**比「未建模」精确得多，而且指出了工作量在哪。**

### 仍然 Unknown

**`CheckResult` 对哪个端点**（R116 已诚实留空）· **剩下 10 步的端点**（`UnmappedSteps` 是数据）·
**`exhibit_draw` 与 `/shop/v1/storeOfflineDraw/join` 两条路的关系**

### 教训

**我六轮前判「没有」，依据是「我查的那条路没有」。而镜像有两条路。**
**这次挡住我的不是「没读仓里的文件」，是「查了一条路就当成全部路」—— 而文件名 `PopMartStepMap` 摆在那里，六轮没点开。**
"""

BACKLOG_ADD = """

## 判据 (f) — PopMart 修正（R849）：端点全在，缺的是步骤

| 层 | 状态 |
|---|---|
| 端点 | **`PopMartEndpoints.cs` 39 个常量，14 个抽签/展览/预约端点全部存在** |
| 映射 | **`PopMartStepMap.cs`（R116）14 对** |
| **步骤** | **`PopMartFlow` 11 个重写里无一个 draw/exhibit/reservation** |

**→ 未覆盖的原因是「步骤方法没写」，不是「端点没有」或「未建模」。**

### 修正

**R835「没有任何流程覆盖它」/ R836「七块未建模」/ R838「十二个名字全为 0」——
端点层是错的，只在步骤层成立。**

**为什么没发现**：R835 从 `PopMartBrowser` 出发只查了 `activity/v1/exhibit_draw`（actapi 那条路），
**而 `/shop/v1/storeOfflineDraw/join` 是另一条路，镜像两条都有。**

| 仍 Unknown | |
|---|---|
| `CheckResult` 对哪个端点 | R116 诚实留空 |
| 剩下 10 步的端点 | `UnmappedSteps` 是数据 |
| 两条路的关系 | 未判 |

**纪律**：**「查了一条路」≠「查了全部路」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R849", BLOCKER)
    ensure(RSTATUS, "R849", BLOCKER)
    ensure(RVERDICT, "第 849 轮", VERDICT)
    ensure(BACKLOG, "R849", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R849" not in h:
        h += ("\n## R849 补充 — 修正 PopMart 结论\n\n"
              "**`PopMartEndpoints.cs` 有 39 个端点，14 个抽签/展览/预约端点全部存在；`PopMartStepMap.cs`（R116）已有 14 对映射。**\n"
              "**缺的只是 `PopMartFlow` 里那 14 个驱动步骤**（11 个重写里一个都不是）。\n"
              "**R835–R838 的「没有抽签面」在端点层是错的，只在步骤层成立。**\n"
              "为什么没发现：R835 只查了 `activity/v1/exhibit_draw`（actapi 那条路），**而 `/shop/v1/storeOfflineDraw/join` 是另一条路。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R849"), (RSTATUS, "R849"), (RVERDICT, "第 849 轮"), (BACKLOG, "R849")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R849: PopMart's draw endpoints are all present, so six rounds ago I named the wrong gap\n\n"
         "PopMartStepMap.cs, written in R116, pairs fourteen of Pop Mart's twenty-four steps against /shop/v1 endpoints:"
         " EnterDraw to DrawScratchDraw, ChooseGoods to DrawScratchChooseGoods, FindMegaDraw to MegaDrawHit,"
         " RedeemLuckPoints to LuckyPointsDraw, FindDates to StoreTicketDates, and so on. I never opened that file in the"
         " six rounds that followed.\n\n"
         "Checking the constants it names against PopMartEndpoints: all eleven are there, and the file holds thirty-nine"
         " endpoints in total, which matches R116's own count. So the replica has the entire draw, exhibit and"
         " reservation endpoint surface. What it lacks is the flow: PopMartFlow's eleven overrides contain no draw,"
         " exhibit or reservation step at all.\n\n"
         "That means R835, R836 and R838 named the wrong gap. R835 said no flow covers it, R836 said seven surfaces were"
         " unmodelled, R838 said twelve names came back zero. At the endpoint layer those are wrong; only at the step"
         " layer do they hold. The accurate statement is that the endpoints are complete, the pairing is complete, and"
         " the fourteen driver methods are unwritten -- which is both a better diagnosis and a cheaper one, since whoever"
         " writes them does not have to hunt for endpoints.\n\n"
         "The reason I missed it is different from the previous five misses. R835 started from the PopMartBrowser type"
         " name and searched for activity/v1/exhibit_draw, which is a real endpoint on the actapi host and genuinely"
         " unused by the replica, and concluded there was no coverage. But /shop/v1/storeOfflineDraw/join is a second"
         " path to the same business, and the image carries both. I followed one path and reported on all of them.\n\n"
         "R116's own comment shows what careful work looks like here: it says which pairs are obvious, and it leaves"
         " CheckResult unmapped because it could be DrawScratchDetail or a poll of the same call and nothing in the image"
         " decides.\n\n"
         "For criterion (f) the why is now specific: fourteen steps lack their driver methods, not their endpoints. The"
         " distinction between ONE path checked and ALL paths checked is what this round adds to the list of ways I have"
         " been wrong.\n\n"
         "Unknown: which endpoint CheckResult pairs with, left open by R116 on purpose; the endpoints for the other ten"
         " steps, recorded as UnmappedSteps rather than guessed; and how the actapi path relates to the shop path, since"
         " the replica models the second and the image carries both.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
