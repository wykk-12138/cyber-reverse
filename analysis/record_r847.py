"""Record R847: the rule collapses two more groups; only collectplus remains."""

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
### johnlewis 8 与 demandware-classic 5：已有 StepMap 答完（R847）

**`JohnLewisStepMap.cs`（R118/R119）** —— 19 步对 12 个 BFF 端点：

| 我列的 8 条 | 映射到 |
|---|---|
| `WebHandOver` · `SessionHandover` | `v2/sessions/web/handover`（共用） |
| `GuestCallback` | `v4/callback/guest` |
| `DeliveryPage` | `v3/orderforms/deliveries` |
| `CreateDelivery` | `v4/orderforms/deliveries`（与 `SubmitShipping` 共用） |
| `GetDeliveryMethods` · `SubmitDeliveryMethod` | `v3/orderforms/deliveries/details`（共用） |
| `AuthenticatePayment` | `v2/orderforms/payments` |

**该文件还说明「为什么 19 步多于 12 端点」：BFF 端点是服务端的资源，步骤列表是客户端的阶段。**
**3 步没有端点的理由也写了**：`GetHome` 是页面加载；`HandleRequiresAction` / `GetStripePaymentIntent` 是 **Stripe 自己的主机**。

**`DemandwareStepMap.cs`（R117）** —— 经典 12 步对控制器，我列的 5 条：

| 我列的 5 条 | 结论 |
|---|---|
| `GenerateCSRF` | → `CSRF-Generate` |
| `SubmitConsignment` | → `CheckoutShippingServices-SubmitShipping` |
| `SubmitShippingOption` | → `CheckoutShippingServices-UpdateShippingMethod`（R117 新查出） |
| `ConfirmPayment` | → `CheckoutServices-PaymentAuthorization`（R117 新查出） |
| **`GetPaymentMethod`** | **有意未映射** —— 镜像里唯一的支付读是 `CheckoutServices-FetchOrderModel`，正被 `GetCheckout` 占着 |

**同一文件还有一条更硬的结论**：`CreateStripePaymentMethod` 无控制器，因为
**「there is no `Stripe-*` controller anywhere in the image」** —— 镜像的支付控制器全是 Adyen 的
（`AdyenUpgrade-Authorize` · `Adyen-Adyen3DS2` · `Adyen-PaymentsDetails` · `AdyenComponents-Payment*`）。

### 只剩 collectplus-app 4 条

`CreateCheckoutApp` `GetDelivery` `GetCollectPlusLocations` `SubmitCollectPlus` ——
**`Flows` 目录里没有任何 CollectPlus 专属文件**（`RetailApiFamilies.cs` / `ServiceHosts.cs` / `ScapiEndpoints.cs` 是通用件）。
"""

if "已有 StepMap 答完（R847" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: johnlewis + demandware-classic closed")

BLOCKER = """

---

## 271. 规则一用就见效：**17 塌成 4**

> R847。未改产品代码。

### 一、先执行 R846 立的规则

```
Get-ChildItem replica\\src\\Cybersole.Stores\\Flows -Filter *.cs
```

**47 个文件。其中与本轮相关的是 `JohnLewisStepMap.cs`(93) 与 `DemandwareStepMap.cs`(82) ——
两个我都读了一遍。**

**`Flows` 目录里还有一整个 `*StepMap` / `*Steps` 家族**：`PopMartStepMap.cs` `NikeSteps.cs`
`ScapiEndpoints.cs` `CandidateSteps.cs` `GraphQlCartSteps.cs` `NikePersistedOperations.cs`
`DemandwareControllers.cs` `RetailApiFamilies.cs` `StoreApiFamilies.cs`。
**这是一套「按流程把步骤对到端点」的分析层，而我在 R838–R845 五轮里没碰过它。**

### 二、`johnlewis` 8 条：全部已映射

**`JohnLewisStepMap.cs`（R118/R119）** 把 19 步对到 12 个 BFF 端点。我列的 8 条：

| 步骤 | 端点 |
|---|---|
| `WebHandOver` · `SessionHandover` | `v2/sessions/web/handover`（共用） |
| `GuestCallback` | `v4/callback/guest` |
| `DeliveryPage` | `v3/orderforms/deliveries` |
| `CreateDelivery` | `v4/orderforms/deliveries`（与 `SubmitShipping` 共用） |
| `GetDeliveryMethods` · `SubmitDeliveryMethod` | `v3/orderforms/deliveries/details`（共用） |
| `AuthenticatePayment` | `v2/orderforms/payments` |

**而它给出了一个我没想过的解释：**

> **a BFF endpoint is not a step.** `v2/sessions/web/handover` serves `WebHandOver` and `SessionHandover` both,
> because **the step list is the client's phases and the endpoints are the server's resources.**

**这句话解释了「19 步 vs 12 端点」的全部张力 —— 也解释了我一直在数的「不同名」为什么不是缺口。**
**步骤是客户端阶段，端点是服务端资源，两者本来不是一一对应。**

**3 条无端点的理由也写了**：`GetHome` 是页面加载；`HandleRequiresAction` / `GetStripePaymentIntent`
是 **Stripe 自己的主机**（镜像里 John Lewis 直达 Stripe，而 Demandware 只有 Stripe 步骤没有 Stripe 控制器 ——
两份地图互为镜像）。

### 三、`demandware-classic` 5 条：4 已映射，1 有意未映射

| 步骤 | 结论 |
|---|---|
| `GenerateCSRF` | → `CSRF-Generate` |
| `SubmitConsignment` | → `CheckoutShippingServices-SubmitShipping` |
| `SubmitShippingOption` | → `UpdateShippingMethod`（**R117 新查出**） |
| `ConfirmPayment` | → `PaymentAuthorization`（**R117 新查出**） |
| `GetPaymentMethod` | **有意未映射** —— 唯一的支付读是 `FetchOrderModel`，正被 `GetCheckout` 占着 |

**同一文件的另一条硬结论：**

> **there is no `Stripe-*` controller anywhere in the image** —— 支付控制器全是 Adyen 的
> （`AdyenUpgrade-Authorize` · `Adyen-Adyen3DS2` · `Adyen-PaymentsDetails` · `AdyenComponents-Payment*`）

**所以 `CreateStripePaymentMethod` 这个步骤名在镜像里没有控制器支撑。**
**R117 的选择是「说出这件事而不是编一个控制器」—— 与本会话一直在用的标准一致。**

### 四、17 → 4

| 流程 | R845 | R846 | R847 |
|---|---|---|---|
| demandware-dual | 9 | 0 | 0 |
| johnlewis | 8 | 8 | **0** |
| demandware-classic | 5 | 5 | **0** |
| collectplus-app | 4 | 4 | **4** |
| **合计** | **26** | **17** | **4** |

### 五、仍然 Unknown

- **`collectplus-app` 4 条**（`CreateCheckoutApp` `GetDelivery` `GetCollectPlusLocations` `SubmitCollectPlus`）：
  **Unknown，且这次是真的** —— **`Flows` 目录里没有任何 CollectPlus 专属文件。**
- **那 4 条要不要做**：**Unknown** —— 取决于这个流程在镜像里是否被真正使用；
  **它在 `StoreFlowSteps` 里有一份 17 步的表，说明镜像确实有这个流程。**
- **`StoreFlowSteps` 的 8 个流程 ↔ `Registry.cs` 的 63 个模块**：**仍未建**（R843 起就记着）。

### 六、教训

**R846 立的规则（先 grep 同名分析文件）一次就用掉两个组，17 变 4。**

**而 `JohnLewisStepMap` 那句话值得单独记住：**

> **the step list is the client's phases and the endpoints are the server's resources.**

**我前面五轮一直在数的「步骤名对不对得上」，在这句话面前是个错问题 ——
步骤和端点不是同一层的东西，用名字对齐去量它，量出来的差异有一半是层级差。**

**所以 R844 那个 16.9% 的真实问题是：它在用一个跨层级的量当覆盖率。**
"""

VERDICT = """

---

## 第 847 轮：规则一用就见效 —— 17 塌成 4

### 先执行 R846 的规则

`Flows` 目录 47 个文件，其中 `JohnLewisStepMap.cs`(93) 与 `DemandwareStepMap.cs`(82) 直接答完了两批。
**目录里还有一整个 `*StepMap` / `*Steps` 家族**（`PopMartStepMap` `NikeSteps` `ScapiEndpoints` `CandidateSteps`
`GraphQlCartSteps` `DemandwareControllers` `RetailApiFamilies` `StoreApiFamilies`）—— **一套「步骤对端点」的分析层，
我在 R838–R845 五轮里没碰过。**

### johnlewis 8 条：全部已映射

`WebHandOver`/`SessionHandover` → `v2/sessions/web/handover` · `GuestCallback` → `v4/callback/guest` ·
`DeliveryPage` → `v3/orderforms/deliveries` · `CreateDelivery` → `v4/orderforms/deliveries` ·
`GetDeliveryMethods`/`SubmitDeliveryMethod` → `v3/orderforms/deliveries/details` · `AuthenticatePayment` → `v2/orderforms/payments`

**而它给出了一个我没想过的解释：**

> **a BFF endpoint is not a step … the step list is the client's phases and the endpoints are the server's resources.**

**这句话解释了「19 步 vs 12 端点」的全部张力 —— 也说明我一直在数的「不同名」有一半是层级差。**

### demandware-classic 5 条：4 已映射，1 有意未映射

`GenerateCSRF`→`CSRF-Generate` · `SubmitConsignment`→`SubmitShipping` · `SubmitShippingOption`→`UpdateShippingMethod` · `ConfirmPayment`→`PaymentAuthorization` · **`GetPaymentMethod` 有意未映射**（唯一的支付读是 `FetchOrderModel`，正被 `GetCheckout` 占着）

**同一文件另一条硬结论**：**there is no `Stripe-*` controller anywhere in the image** —— 支付控制器全是 Adyen 的。
**R117 的选择是「说出这件事而不是编一个控制器」。**

### 17 → 4

| 流程 | R845 | R846 | R847 |
|---|---|---|---|
| demandware-dual | 9 | 0 | 0 |
| johnlewis | 8 | 8 | **0** |
| demandware-classic | 5 | 5 | **0** |
| collectplus-app | 4 | 4 | **4** |
| **合计** | **26** | **17** | **4** |

### 仍然 Unknown

**`collectplus-app` 4 条 —— 这次是真的**（`Flows` 里无任何 CollectPlus 专属文件）·
**那 4 条要不要做**（流程在 `StoreFlowSteps` 有 17 步表，说明镜像确实有它）· **8 个流程 ↔ 63 个模块**（仍未建）

### 教训

> **`the step list is the client's phases and the endpoints are the server's resources.`**
> **我前面五轮一直在数的「步骤名对不对得上」，在这句话面前是个错问题 —— 用名字对齐去量它，量出来的差异有一半是层级差。**
> **所以 R844 那个 16.9% 的真实问题是：它在用一个跨层级的量当覆盖率。**
"""

BACKLOG_ADD = """

## 判据 (f) — 17 → 4（R847）

**规则（R846 立）**：先 `Get-ChildItem replica/src/Cybersole.Stores/Flows -Filter *.cs`。**47 个文件，其中一整个 `*StepMap`/`*Steps` 分析层。**

| 流程 | R845 | R846 | R847 | 依据 |
|---|---|---|---|---|
| demandware-dual | 9 | 0 | 0 | `ScapiAppPath.cs`（R124） |
| johnlewis | 8 | 8 | **0** | **`JohnLewisStepMap.cs`（R118/R119）** |
| demandware-classic | 5 | 5 | **0** | **`DemandwareStepMap.cs`（R117）** |
| collectplus-app | 4 | 4 | **4** | **无专属文件** |
| **合计** | **26** | **17** | **4** |

### 两句该记的话（都出自已有文件）

> **a BFF endpoint is not a step … the step list is the client's phases and the endpoints are the server's resources.**

> **there is no `Stripe-*` controller anywhere in the image** —— 支付控制器全是 Adyen 的；R117 选择说出这件事而不编一个。

### 剩 4 条 = 真待判

`CreateCheckoutApp` · `GetDelivery` · `GetCollectPlusLocations` · `SubmitCollectPlus`

| 仍 Unknown | |
|---|---|
| 这 4 条要不要做 | 流程在 `StoreFlowSteps` 有 17 步表 → 镜像确实有它 |
| 8 流程 ↔ `Registry.cs` 63 模块 | 仍未建 |

**纪律**：**R844 的 16.9% 的真实问题是「用一个跨层级的量当覆盖率」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R847", BLOCKER)
    ensure(RSTATUS, "R847", BLOCKER)
    ensure(RVERDICT, "第 847 轮", VERDICT)
    ensure(BACKLOG, "R847", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R847" not in h:
        h += ("\n## R847 补充 — 17 塌成 4\n\n"
              "**`JohnLewisStepMap.cs`（R118）答完 johnlewis 8 条 · `DemandwareStepMap.cs`（R117）答完 classic 5 条。**\n"
              "**只剩 `collectplus-app` 4 条**（`Flows` 里无任何 CollectPlus 专属文件）—— 这次是真待判。\n"
              "**关键引文**：「the step list is the client's phases and the endpoints are the server's resources」——\n"
              "**步骤与端点不是同一层，用名字对齐去量，量出来的差异有一半是层级差。R844 的 16.9% 就是跨层级量当覆盖率。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R847"), (RSTATUS, "R847"), (RVERDICT, "第 847 轮"), (BACKLOG, "R847")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R847: the rule collapses two more groups, seventeen down to four\n\n"
         "R846's rule was to list the flow's own directory before adjudicating anything, because three rounds in a row"
         " had rebuilt analyses the repository already held. Applied at once, it found forty-seven files and a whole"
         " family of step-map analyses I had not touched across five rounds: JohnLewisStepMap, DemandwareStepMap,"
         " PopMartStepMap, NikeSteps, ScapiEndpoints, CandidateSteps, GraphQlCartSteps.\n\n"
         "JohnLewisStepMap, from R118 and R119, pairs John Lewis's nineteen steps against twelve BFF endpoints and"
         " settles all eight names I had listed. More useful than the pairings is the sentence that explains the"
         " arithmetic: a BFF endpoint is not a step, because the step list is the client's phases while the endpoints are"
         " the server's resources. One endpoint serves WebHandOver and SessionHandover both; another serves SubmitShipping"
         " and CreateDelivery. That is the whole tension between nineteen steps and twelve endpoints, and it also means a"
         " large part of what I have been counting as unmatched names is a level difference rather than a gap.\n\n"
         "The map also records why three steps have no endpoint at all: GetHome is a page load, and"
         " HandleRequiresAction and GetStripePaymentIntent are calls to Stripe's own host. It notes the mirror image of"
         " R117's Demandware finding -- Demandware has Stripe steps but no Stripe controller, while John Lewis reaches"
         " Stripe directly, which is why no BFF endpoint names those steps.\n\n"
         "DemandwareStepMap, from R117, settles four of the five classic names against controllers and explains the"
         " fifth: GetPaymentMethod is deliberately unmapped because the only payment read in the image is"
         " FetchOrderModel, which GetCheckout already carries. The same file states that there is no Stripe controller"
         " anywhere in the image -- every payment controller is Adyen's -- so CreateStripePaymentMethod has no controller"
         " behind its name, and R117 chose to say so rather than invent one.\n\n"
         "Seventeen becomes four, and the four are CollectPlus's, for which the Flows directory holds no file of its own."
         " Those are genuinely open, and the question for them is whether the flow is used at all: StoreFlowSteps carries"
         " a seventeen-step table for it, which says the image does have the flow.\n\n"
         "The lesson from the map's own words is sharper than the tally. Five rounds of counting name matches were"
         " answering the wrong question, because steps and endpoints are not the same kind of thing. R844's 16.9 percent"
         " was a cross-level comparison presented as coverage.\n\n"
         "Unknown: whether CollectPlus's four steps need building, given the flow exists in the image's step table; and"
         " how the eight flows with step tables map onto the sixty-three modules in Registry.cs, which has been open since"
         " R843.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
