"""Record R843: the per-flow step tables already existed, and Nike's granularity gap."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 267. **步骤表早就在仓里（R112）；而 Nike 的真实差距是粒度，不是缺失**

> R843。未改产品代码。**这一轮先承认一件事：R838–R842 在重新推导一份 `StoreFlowSteps.cs` 里已有的东西。**

### 一、我先做了什么，错在哪

**为了让「71 条未覆盖」有个清单，我从 R839 起从元数据里提 `<Name>d__N`，得到 115 个名字，
再用三轮探针判了 71 条。**

**而 `replica/src/Cybersole.Stores/Flows/StoreFlowSteps.cs` 里，从 R112 起就有更权威的东西：**

```csharp
/// Each flow's steps sit in one adjacent run in the string pool, with the compiler's d__N ordinals
/// attached — which makes the list authoritative rather than reconstructed.
```

**它给出 9 个流程、每条带 ordinal、按流程分组：**

| 流程 | 步数 | 例 |
|---|---|---|
| Nike | 16 | `StartEcomSession 41` … `SubmitOrder 58` |
| **Pop Mart** | **24** | `StartDrawFlow 115` · `FindMegaDraw 133` · `ChooseGoods 135` · `StartReservationFlow 149` … |
| John Lewis | 17 | `WebHandOver 23` · `GuestCallback 25` · `GetStripePaymentIntent 39` |
| Demandware 经典 | 12 | `InitiateCheckout 33` · `GenerateCSRF 34` · `SubmitConsignment 37` |
| Demandware 双路 | 15 | `StartAppFast 36` · `GetCartDw 39` · `AddToCartAppDw 42` |
| CollectPlus App | 16 | |
| StructureToken 多/单 | 14 / 14 | |

**我的 115 个名字是「按八个词搜出来的扁清单」；这份是「按流程分组、带序号、有出处」的表。**
**后者好得多，而我没读它。**

**R838 说「按词搜索给不出完整清单」—— 而正确答案不是「换个搜索方式」，是「先读仓里已有的清单」。**

### 二、Nike 的逐步骤对比（这才是判据 f 要的形态）

**`NikeFlow` 重写 17 个方法，而镜像 Nike 流程有 16 步；名字对得上的只有两个：**

```
OK  FindVariant            ordinal 44
OK  SubmitOrder            ordinal 58
--  StartEcomSession       41     --  SubmitShippingAddress  50     --  CheckInventory     55
--  Authorize              42     --  GetShippingMethods     51     --  GetShopperIp       56
--  GetAccessToken         43     --  SubmitShippingMethod   52     --  GetPaymentMethods  57
--  CreateBasket           46     --  SubmitBillingAddress   53
--  SubmitCustomer         48     --  BeginCheckout          54
--  ValidateAddress        49
```

**14 步没有同名重写。** 但原因不是「缺」：

**镜像把 Nike 的结账拆成细步 —— `SubmitCustomer` / `ValidateAddress` / `SubmitShippingAddress` /
`GetShippingMethods` / `SubmitShippingMethod` / `SubmitBillingAddress` / `BeginCheckout` /
`CheckInventory` / `GetShopperIp` / `GetPaymentMethods` 十步；
复刻件把它们压成 `SubmitShipping` / `SubmitPayment` / `GetCheckout` 三个。**

**所以 Nike 的差距是粒度，不是缺失**：**镜像有 10 个可分别失败的结账阶段，复刻件有 3 个。**
**这影响「每个函数功能相等」和「错误定位」：镜像某一步失败时能说清是哪一步，复刻件只能说到「提交配送」。**

### 三、Pop Mart 的 24 步（R838 的「抽签子系统」其实就在这里）

```
GetOrders 104 · GetInstoreOrders 105
StartDrawFlow 115 · StartDrawCheckFlow 116 · FindDraw 117 · CheckDraw 118 · EnterDraw 119 · CheckResult 120
StartDrawEventFlow 131 · FindDrawEvent 132 · FindMegaDraw 133 · EnterDrawEvent 134 · ChooseGoods 135
RedeemMemberPoints 136 · RedeemLuckPoints 137 · FetchAliases 138
StartExhibitFlow 139 · FindExhibit 141 · EnterExhibit 142
StartReservationFlow 149 · FetchDetails 150 · FindDates 151 · FindTimeSlots 152 · EnterReservation 153
```

**R838 从 `PopNow` 里读出 13 个名字，兴奋地称它「九方法子系统」—— 而这份表里 Pop Mart 的抽签/展览/预约
一共 17 步，分成四条独立的流（draw / draw-event / exhibit / reservation），`PopNow` 只是其中一条的一个词。**

**所以 R838 那个「子系统」判断既对又不全：对在「粗读复刻件没有」，不全在「把它当成一套」。**

### 四、验证

```
replica\\src\\Cybersole.Stores\\Flows\\StoreFlowSteps.cs   （R112 起就有，9 个流程、带 ordinal）
NikeFlow overrides 17 个；与镜像 16 步同名相交 2 个（FindVariant / SubmitOrder）
Pop Mart 镜像 24 步，其中抽签/展览/预约共 17 步
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **Nike 那 10 个细步在复刻件里分别对应到哪一行代码**：**Unknown** ——
  需要逐个读 `SubmitShipping` / `SubmitPayment` / `GetCheckout` 的实现，**看它们各自做了几件事。**
- **其余 8 个流程的同类对比**：**未做** —— 本轮只做了 Nike。
- **`StoreFlowSteps` 的 9 个流程与 `Registry.cs` 的 63 个模块怎么对应**：**Unknown** ——
  9 个有步骤表，63 个有模块，**中间的关系没建立。**

### 六、教训

**我在四轮里造了一份「名字清单」，而仓里躺着一份更好的 —— 按流程分组、带序号、注明出处的。**

**R838 的诊断是「按词搜索给不出完整清单」，我当时写下的结论是「换方法：遍历元数据或走类型图」。
正确的结论是更简单的一句：先读仓里已经有的。**

**因为「我不知道它已经存在」和「它不存在」在我脑子里长得一样。**
"""

VERDICT = """

---

## 第 843 轮：步骤表早就在仓里；Nike 的差距是粒度不是缺失

### 先承认：R838–R842 在重新推导已有之物

`replica/src/Cybersole.Stores/Flows/StoreFlowSteps.cs` **从 R112 起就有 9 个流程的步骤表，带 ordinal、按流程分组、注明出处**：

| 流程 | 步数 |
|---|---|
| Nike | 16 |
| **Pop Mart** | **24** |
| John Lewis | 17 |
| Demandware 经典 / 双路 | 12 / 15 |
| CollectPlus App | 16 |
| StructureToken 多 / 单 | 14 / 14 |

**我从元数据提的 115 个名字是「按八个词搜出的扁清单」。后者好得多，而我没读它。**

> **R838 的结论是「换方法」；正确的结论更简单：先读仓里已经有的。**
> **「我不知道它已经存在」和「它不存在」在我脑子里长得一样。**

### Nike 逐步骤对比（判据 f 要的形态）

**`NikeFlow` 17 个重写 ↔ 镜像 16 步，同名的只有两个（`FindVariant` 44 · `SubmitOrder` 58）。**

**14 步没有同名重写，但原因是粒度：**

> **镜像把 Nike 结账拆成 10 个可分别失败的阶段**（`SubmitCustomer`/`ValidateAddress`/`SubmitShippingAddress`/`GetShippingMethods`/`SubmitShippingMethod`/`SubmitBillingAddress`/`BeginCheckout`/`CheckInventory`/`GetShopperIp`/`GetPaymentMethods`），
> **复刻件压成 3 个**（`SubmitShipping`/`SubmitPayment`/`GetCheckout`）。
> **影响两件事：「每个函数功能相等」，以及错误定位 —— 镜像能说清哪一步失败，复刻件只能说到「提交配送」。**

### Pop Mart 的 24 步里，抽签/展览/预约共 17 步

`StartDrawFlow`/`FindDraw`/`EnterDraw`/`CheckResult` · `StartDrawEventFlow`/`FindMegaDraw`/`ChooseGoods`/`RedeemMemberPoints` · `StartExhibitFlow`/`EnterExhibit` · `StartReservationFlow`/`FindDates`/`FindTimeSlots`/`EnterReservation`

**R838 的 `PopNow` 只是其中一条流的一个词 —— 那轮「九方法子系统」既对（粗读没有）又不全（当成一套）。**

### 仍然 Unknown

**Nike 那 10 个细步分别对应复刻件哪一行**（要逐个读三个粗步的实现）· **其余 8 个流程的同类对比**（本轮只做 Nike）· **9 个有步骤表的流程 ↔ `Registry.cs` 63 个模块**（关系未建立）

### 验证

```
StoreFlowSteps.cs（R112 起）9 个流程带 ordinal
NikeFlow 17 重写 ∩ 镜像 16 步 = 2 · Pop Mart 24 步中抽签/展览/预约 17 步
产品代码未改 · 七项度量沿用
```
"""

BACKLOG_ADD = """

## 判据 (f) — 步骤表已在仓里（R843）；Nike 差距是粒度

**`StoreFlowSteps.cs`（R112 起）有 9 个流程的步骤表，带 ordinal、按流程分组、注明出处：**
Nike 16 · **Pop Mart 24** · John Lewis 17 · Demandware 经典 12 / 双路 15 · CollectPlus App 16 · StructureToken 多/单 14/14

> **R838–R842 从元数据提的 115 个名字是「按八个词搜的扁清单」。后者好得多，而我没读它。**
> **「我不知道它已经存在」和「它不存在」在我脑子里长得一样。**

### Nike：17 重写 ↔ 16 步，同名只有 2 个

**镜像 10 个细步**（`SubmitCustomer`/`ValidateAddress`/`SubmitShippingAddress`/`GetShippingMethods`/`SubmitShippingMethod`/`SubmitBillingAddress`/`BeginCheckout`/`CheckInventory`/`GetShopperIp`/`GetPaymentMethods`）
**↔ 复刻件 3 个粗步**（`SubmitShipping`/`SubmitPayment`/`GetCheckout`）。

**→ 差距是粒度，不是缺失。影响「功能相等」与错误定位。**

### Pop Mart 24 步：抽签/展览/预约共 17 步

`StartDrawFlow`…`CheckResult`（6）· `StartDrawEventFlow`…`RedeemMemberPoints`（7）· `StartExhibitFlow`…`EnterExhibit`（3）· `StartReservationFlow`…`EnterReservation`（5）
**R838 的 `PopNow` 只是其中一条流的一个词。**

| 仍 Unknown | |
|---|---|
| Nike 10 细步 ↔ 复刻件哪一行 | 要读三个粗步的实现 |
| 其余 8 个流程的对比 | 本轮只做 Nike |
| 9 步骤表流程 ↔ `Registry.cs` 63 模块 | 关系未建立 |
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R843", BLOCKER)
    ensure(RSTATUS, "R843", BLOCKER)
    ensure(RVERDICT, "第 843 轮", VERDICT)
    ensure(BACKLOG, "R843", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R843" not in h:
        h += ("\n## R843 补充 — 步骤表早已在仓里\n\n"
              "**`replica/src/Cybersole.Stores/Flows/StoreFlowSteps.cs`（R112 起）有 9 个流程的步骤表，带 ordinal。**\n"
              "R838–R842 从元数据提的 115 个名字是扁清单；**先读仓里已有的**。\n"
              "**Nike：镜像 16 步 ↔ NikeFlow 17 重写，同名仅 2 个。差距是粒度** —— "
              "镜像 10 个细步（`ValidateAddress`/`CheckInventory`/`GetShopperIp`…）vs 复刻件 3 个粗步。\n"
              "**Pop Mart 24 步，抽签/展览/预约共 17 步；`PopNow` 只是其中一条流的一个词。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R843"), (RSTATUS, "R843"), (RVERDICT, "第 843 轮"), (BACKLOG, "R843")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R843: the step tables were already in the repository, and Nike's gap is granularity\n\n"
         "For four rounds I built an inventory of the image's named operations, extracting d__N names from the metadata"
         " and probing seventy-one of them. StoreFlowSteps.cs has held a better answer since R112: nine flows, each step"
         " with its compiler ordinal, grouped by flow and citing where it came from, because the steps sit in adjacent"
         " runs in the string pool.\n\n"
         "My 115 names are a flat list keyed on eight search words. That is a worse instrument than a per-flow table"
         " with ordinals, and I did not read it. R838 concluded that word search cannot produce a complete inventory and"
         " that the fix was a different traversal. The simpler correct answer was to read what the repository already"
         " had, and the reason I missed it is that not knowing something exists looks the same as it not existing.\n\n"
         "Nike is the worked example of what criterion (f) should look like. NikeFlow overrides seventeen methods; the"
         " image's Nike flow has sixteen steps; two names intersect, FindVariant at ordinal 44 and SubmitOrder at 58."
         " The other fourteen are not missing but merged: the image separates SubmitCustomer, ValidateAddress,"
         " SubmitShippingAddress, GetShippingMethods, SubmitShippingMethod, SubmitBillingAddress, BeginCheckout,"
         " CheckInventory, GetShopperIp and GetPaymentMethods into ten stages that can fail independently, while the"
         " replica collapses them into SubmitShipping, SubmitPayment and GetCheckout.\n\n"
         "That distinction matters twice over. It is the real meaning of every function behaving the same -- ten stages"
         " against three is a different failure surface. And it changes what an error says: the image can name the stage"
         " that failed, the replica can only say that shipping submission failed.\n\n"
         "Pop Mart's twenty-four steps contain seventeen covering draws, events, exhibits and reservations, four distinct"
         " flows. R838's PopNow finding was right that the replica has none of it and wrong to call it one subsystem:"
         " PopNow is a word inside one of the four.\n\n"
         "Unknown: which lines inside the replica's three coarse steps carry the ten fine ones, needing each to be read;"
         " the same comparison for the other eight flows, since this round did only Nike; and how the nine flows with"
         " step tables map onto the sixty-three modules in Registry.cs, a relation that has not been built.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
