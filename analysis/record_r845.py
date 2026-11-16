"""Record R845: the 108 collapses to 35 real questions once the base class is checked."""

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
### 108 条的两刀切（R845，`analysis/partition_steps.py`）

```
108 条不同名
 ├── 49 条：StoreFlow 基类已声明 → 只是没重写，不是缺口
 └── 59 条：基类也没有
      ├── 24 条 PopMart（抽签/展览/预约 17 + GetOrders/GetInstoreOrders 等 7）
      └── 35 条：需要行为裁决
```

**`StoreFlow` 声明 165 个虚步骤；108 条里 49 条就在那 165 个里面。**

| 流程 | 基类有（无缺口） | 基类没有 |
|---|---|---|
| nike | 5（`Authorize` `CreateBasket` `SubmitCustomer` `SubmitShippingMethod` `SubmitBillingAddress`） | **9** |
| popmart | 0 | **24** |
| johnlewis | 5（`GetPaymentPage` `SubmitOrderStripe` `PlaceOrder` `HandleRequiresAction` `GetStripePaymentIntent`） | **8** |
| demandware-classic | 3（`InitiateCheckout` `CreateStripePaymentMethod` `CreateOrder`） | **5** |
| demandware-dual | 4（`GetRates` `FindProductApp` `AddToCartApp` `SubmitOrderApp`） | **9** |
| collectplus-app | 8（`GetProduct` `GetSessionApp` `GetBasket` `SubmitDiscount` `LookupAddress` `SubmitDelivery` `SubmitBilling` `StartPayment` `GetPaymentUrl`） | **4** |
| structure-token-multi | 12 | 0 |
| structure-token-single | 8 | 0 |

**注意 `structure-token-*` 那两行：基类全有 —— 也就是说那 4 个「同名」之外，剩下的基类都实现了。
R844 里我对这两行的映射（指向共用文件）导致的「不同名」全部落在基类一侧。**
"""

block = "\n## 108 条的两刀切（R845）\n" + TABLE
if "108 条的两刀切（R845" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write(block)
    print("  ASYNC_OPS.md: partition appended")
else:
    print("  ASYNC_OPS.md already has it")

BLOCKER = """

---

## 269. **108 条塌成 35 条**：先查基类，就少掉 49 条

> R845。`analysis/partition_steps.py` 常驻。`docs/ASYNC_OPS.md` 增分区表。未改产品代码。

### 一、R844 的三种原因，其中一种最便宜

R844 给 108 条不同名列了三种可能：**粒度合并 / 基类默认实现 / 真缺**。

**第二种最便宜，而且完全机械：`StoreFlow` 声明了 165 个虚步骤 —— 名字在上面的，基类已经实现了，只是该流程没重写。**

### 二、结果

```
108 条不同名
 ├── 49 条 StoreFlow 声明了 → 无缺口
 └── 59 条 基类也没有
      ├── 24 条 PopMart
      └── 35 条 真问题
```

**那 49 条里能看出复刻件的设计意图**：`Authorize` `CreateBasket` `SubmitCustomer` `SubmitShippingMethod`
`SubmitBillingAddress` `InitiateCheckout` `CreateOrder` `GetRates` `CalculateTaxes` `GetStructureToken`
`CreateTransaction` `SubmitPayPal` `ProcessPayment` …… **这些通用结账步骤在基类里，各站复用。**

**而 `structure-token-multi` / `structure-token-single` 两行基类全有（12 + 8 条）** ——
**说明 R844 里我对这两行的文件映射（指向共用文件）造成的「不同名」，全部落在基类一侧，不是缺口。**

### 三、剩下 59 条的形状

| 流程 | 条数 | 性质 |
|---|---|---|
| **popmart** | **24** | 抽签/展览/预约 17 步（R835–R838 已证没有）+ `GetOrders` `GetInstoreOrders` 等 7 步 |
| **nike** | **9** | `StartEcomSession` `GetAccessToken` `ValidateAddress` `SubmitShippingAddress` `GetShippingMethods` `BeginCheckout` `CheckInventory` `GetShopperIp` `GetPaymentMethods` |
| **demandware-dual** | **9** | `StartAppFast` `StartAppSafe` `GetSessionDw` `GetCartDw` `AddToCartAppDw` `SaveSessionDw` `ApplyDiscountApp` `GetCheckoutApp` `GetRatesApp` |
| **johnlewis** | **8** | `WebHandOver` `SessionHandover` `GuestCallback` `DeliveryPage` `CreateDelivery` `GetDeliveryMethods` `SubmitDeliveryMethod` `AuthenticatePayment` |
| **demandware-classic** | **5** | `GenerateCSRF` `SubmitConsignment` `SubmitShippingOption` `GetPaymentMethod` `ConfirmPayment` |
| **collectplus-app** | **4** | `CreateCheckoutApp` `GetDelivery` `GetCollectPlusLocations` `SubmitCollectPlus` |

**Nike 那 9 条 R843 已定性为粒度**（镜像 10 个可分别失败的结账阶段）。
**`demandware-dual` 那 9 条是「App 侧 / Dw 侧双路」**（R112 的注释就说这个流程两条路并存）。
**`johnlewis` 那 8 条是 Stripe 支付与交付回调链。**

**所以 59 条里，24（PopMart）+ 9（Nike）已有定性；剩 26 条要分别判。**

### 四、验证

```
python analysis\\partition_steps.py
  StoreFlow declares 165 virtual steps
  unmatched by name: 108
  ...StoreFlow declares the step: 49
  ...and StoreFlow does not:      59
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **26 条的真判**（59 − 24 − 9）：**Unknown** ——
  `demandware-dual` 9 · `johnlewis` 8 · `demandware-classic` 5 · `collectplus-app` 4。
- **49 条基类实现是否真的对每个站都适用**：**Unknown** ——
  **「基类有」证明方法存在，不证明它对这个站的行为正确。** 这是「功能相等」比「存在」更强的地方。
- **`popmart` 那 7 步**（`GetOrders` `GetInstoreOrders` 等）：**Unknown** —— 17 步已证没有，这 7 步未判。

### 六、教训

**R844 我造了个 16.9%，并写清它有三种解释。这一轮把其中一种查掉，108 变成 35。**

**而关键点是：这个数变小不是因为我放宽了标准，是因为我做了一个检查。**
**上一轮我说「一个错的总数比没有总数更坏」；这一轮是它的正面对照 ——
一个查清了构成的总数，比一个吓人的总数有用得多。**
"""

VERDICT = """

---

## 第 845 轮：108 条塌成 35 条 —— 先查基类，少掉 49 条

### 最便宜的那一刀

`StoreFlow` 声明 **165 个虚步骤**。名字在上面的，基类已实现，只是该流程没重写。

```
108 条不同名
 ├── 49 条 StoreFlow 声明了 → 无缺口
 └── 59 条 基类也没有
      ├── 24 条 PopMart
      └── 35 条 真问题
```

**那 49 条看得出设计意图**：`Authorize` `CreateBasket` `SubmitCustomer` `SubmitShippingMethod`
`InitiateCheckout` `CreateOrder` `GetRates` `CalculateTaxes` `GetStructureToken` `SubmitPayPal` `ProcessPayment` —— **通用结账步骤在基类，各站复用。**

**`structure-token-multi`/`single` 两行基类全有（12+8）** —— **R844 里那两行的「不同名」全部落在基类一侧，是我映射粗糙，不是缺口。**

### 59 条的形状

| 流程 | 条数 | 性质 |
|---|---|---|
| **popmart** | **24** | 抽签/展览/预约 17（已证没有）+ 7 未判 |
| **nike** | **9** | R843 已定性为**粒度** |
| **demandware-dual** | **9** | App 侧 / Dw 侧双路（R112 注释即此） |
| **johnlewis** | **8** | Stripe 支付 + 交付回调链 |
| **demandware-classic** | **5** | `GenerateCSRF` `SubmitConsignment` `SubmitShippingOption` `GetPaymentMethod` `ConfirmPayment` |
| **collectplus-app** | **4** | `CreateCheckoutApp` `GetDelivery` `GetCollectPlusLocations` `SubmitCollectPlus` |

**24 + 9 已有定性 → 剩 26 条要分别判。**

### 仍然 Unknown

**26 条的真判**（dual 9 · johnlewis 8 · classic 5 · collectplus 4）·
**49 条基类实现对每个站是否真的适用**（「基类有」证明方法存在，不证明对它这个站行为正确）·
**`popmart` 那 7 步**

### 教训

> **这个数变小不是因为我放宽了标准，是因为我做了一个检查。**
> **上一轮说「一个错的总数比没有总数更坏」；这一轮是正面对照 —— 一个查清了构成的总数，比一个吓人的总数有用得多。**
"""

BACKLOG_ADD = """

## 判据 (f) — 108 塌成 35（R845）

**工具**：`python analysis\\partition_steps.py`。

```
108 条不同名
 ├── 49 条 StoreFlow（165 虚步骤）已声明 → 无缺口，只是没重写
 └── 59 条 基类也没有
      ├── 24 PopMart（17 抽签/展览/预约已证没有 + 7 未判）
      └── 35 真问题
```

### 49 条基类侧体现的设计

`Authorize` `CreateBasket` `SubmitCustomer` `SubmitShippingMethod` `InitiateCheckout` `CreateOrder`
`GetRates` `CalculateTaxes` `GetStructureToken` `CreateTransaction` `SubmitPayPal` `ProcessPayment`
—— **通用结账步骤在基类，各站复用。**

**`structure-token-*` 两行基类全有（12+8）→ R844 里那两行「不同名」是映射粗糙，不是缺口。**

### 59 条的分布

| 流程 | 条数 | 状态 |
|---|---|---|
| popmart | 24 | 17 已证没有；7 未判 |
| nike | 9 | **R843 已定性：粒度** |
| demandware-dual | 9 | App/Dw 双路（R112 注释） |
| johnlewis | 8 | Stripe + 交付回调 |
| demandware-classic | 5 | 未判 |
| collectplus-app | 4 | 未判 |

**→ 剩 26 条要分别判。**

| 仍 Unknown | |
|---|---|
| 26 条真判 | dual 9 · johnlewis 8 · classic 5 · collectplus 4 |
| 49 条基类实现是否适用每站 | **「有」≠「对它这个站正确」** |
| popmart 7 步 | 未判 |

**纪律**：**数变小不是因为放宽标准，是因为做了一次检查。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R845", BLOCKER)
    ensure(RSTATUS, "R845", BLOCKER)
    ensure(RVERDICT, "第 845 轮", VERDICT)
    ensure(BACKLOG, "R845", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R845" not in h:
        h += ("\n## R845 补充 — 108 塌成 35\n\n"
              "`analysis/partition_steps.py`：`StoreFlow` 165 虚步骤里已含 108 条中的 **49 条**（无缺口，只是没重写）。\n"
              "剩 59 条：**24 PopMart（17 已证没有 + 7 未判）· 9 Nike（R843 已定性粒度）· 9 demandware-dual（App/Dw 双路）"
              "· 8 johnlewis（Stripe+交付回调）· 5 classic · 4 collectplus** → **剩 26 条要分别判**。\n"
              "**「基类有」证明方法存在，不证明对它这个站行为正确。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R845"), (RSTATUS, "R845"), (RVERDICT, "第 845 轮"), (BACKLOG, "R845")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R845: the 108 collapses to 35 once the base class is checked\n\n"
         "R844 listed three causes for the 108 image step names with no same-named override -- merged into a coarser"
         " step, already in the base class, or genuinely missing -- and did not separate them. The middle one is"
         " mechanical: StoreFlow declares 165 virtual steps, so a name found there is implemented by the base and merely"
         " not overridden by that flow.\n\n"
         "Forty-nine of the 108 sit in that base set. They show the design plainly: Authorize, CreateBasket,"
         " SubmitCustomer, SubmitShippingMethod, SubmitBillingAddress, InitiateCheckout, CreateOrder, GetRates,"
         " CalculateTaxes, GetStructureToken, CreateTransaction, SubmitPayPal and ProcessPayment are generic checkout"
         " stages the base provides for every store. Both structure-token flows turn out to have their entire remainder"
         " in the base, which means R844's mismatches on those two rows were my crude file mapping rather than gaps.\n\n"
         "Fifty-nine remain outside both. Twenty-four are PopMart, seventeen of which R835 through R838 already"
         " established are absent. Nine are Nike, which R843 established are granularity rather than absence. That leaves"
         " twenty-six needing a judgement: nine for demandware-dual, which R112's own note describes as keeping an app"
         " side and a web side alive at once; eight for John Lewis, which are a Stripe payment and delivery callback"
         " chain; five for Demandware classic; and four for CollectPlus.\n\n"
         "So the alarmingly large number from last round is now thirty-five, and then twenty-six. The number fell because"
         " a check was run and not because a standard was loosened, which is the counterpart to last round's warning"
         " about wrong totals: a total whose composition has been examined is worth far more than a frightening one.\n\n"
         "Unknown: the twenty-six, which this round only counted; whether the forty-nine base implementations actually"
         " suit each store, since a method existing does not establish that its behaviour is right for that site, and"
         " that gap is where every-function-behaves-the-same is stronger than mere presence; and the seven PopMart steps"
         " such as GetOrders and GetInstoreOrders that the earlier rounds did not cover.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
