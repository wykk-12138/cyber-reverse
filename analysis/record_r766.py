"""Record R766: Scheels reaches 100%, and the endpoints were never the missing part."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 193. Scheels 71% → 100%：**缺的从来不是端点**

> R766。改 `replica/src/Cybersole.Stores/Flows/ScheelsFlow.cs`（+2 步）。

### 一、先取证：原版 Scheels 到底有什么

`apihub.scheels.com` 的 17 个 action 全在（Observation）：

```
account/  getAccount login register requestReset reset
product/  getProduct
cart/     addToCart updateCart removeLineItem clean checkout completeDetailsCheckout
          sendSignifydStepUpCode completeSignifydStepUpCheckout setAdyenCreditCard
adyen/    beginPayPal completePayPal
```

**所以支付那一步原版确实有** —— 复刻件的缺失是真缺口，不是原版也没有。

**顺带一个判断上的纠正**：`goat` 的端点全是
`goat.com/api/v1/drops/get-user-drops`、`/submit-drop-captcha` —— **是抽奖面，不是结账面**，
**七步尺子对 `goat` 可能同样不合身**（与 `raffle` / `pocketgames` 一类）。**未取证，记 Unknown。**

### 二、而真正的发现是：端点早就声明好了，flow 一个都没用

`RetailApiFamilies.ScheelsFrontastic` 从 R103 起就把整个 action hub 声明成了常量，
**连两处 Signifyd 升级步骤都有**，而且注释里写着「订单在验证码送出并被接受前无法完成」。
**还有一条 `Chain` 直接给出购买顺序：**

```
Login, GetProduct, AddToCart, UpdateCart, Checkout, CompleteDetailsCheckout,
SignifydStepUpCode, CompleteSignifydStepUp, SetAdyenCreditCard
```

**而 `ScheelsFlow` 的结账两步用的是 `/checkout` 和 `/api/checkout/submit` —— 猜的路径。**

**所以"缺两步"其实是三层问题**：① 两步没实现；② 已实现的两步指向猜的 URL；③ 真实端点已declared 但无人调用。

### 三、改了什么

加了 `SubmitShippingAsync`（`cart/updateCart` → `cart/completeDetailsCheckout`）
与 `SubmitPaymentAsync`（`cart/setAdyenCreditCard`），URL 全部取自 `ScheelsFrontastic` 常量。

**Observation 与 Inference 分开写进了注释**：

- **Observation**：URL、名字、**顺序**（来自 `Chain`）
- **Inference（中）**：**请求体**。镜像给了 action 名，没给 JSON 字段名，
  所以 payload 由 flow 已有的数据拼出，**标为推断而非证据**。

**这是这一轮唯一需要小心的东西：URL 有据，body 没据。注释里写清了，后来人不要把它当既定事实。**

### 四、验证

```
构建                      已成功
ModuleCoverageTests       scheels 71% → 100%（反射矩阵认到了新步骤）
完整套件                  1751 通过 / 0 失败 / 0 跳过（未变）
四项度量                  4 / 0 / 17 / 78 / 0（未变）
```

**71% 组从 12 个降到 11 个**（`bstn` / `goat` 等仍在）。

### 五、仍然 Unknown

- **请求体的真实字段名**：**Unknown** —— 这是这一轮交付里最薄的一层。
- `goat` 该用哪把尺子：**Unknown** —— 端点显示是抽奖面。
- `GetCheckoutAsync` 仍走 `/checkout`（猜的）：**已知不一致，未改** ——
  改它要动 `OpenCheckoutAsync` 的调用约定，留作独立一项，避免和本轮混在一起。
- 其余 11 个 71% 模块缺的是不是同一对：**Inference（高）**，未逐一取证。
"""

VERDICT = """

---

## 第 766 轮：缺的从来不是端点

### 先取证

原版 `apihub.scheels.com` 的 17 个 action 全在，**包括支付**：
`cart/completeDetailsCheckout` · `cart/setAdyenCreditCard` · `cart/sendSignifydStepUpCode` ·
`cart/completeSignifydStepUpCheckout` · `adyen/beginPayPal` · `adyen/completePayPal`。

**所以复刻件缺的那两步是真缺口，不是原版也没有。**

**附带纠正**：`goat` 的端点全是 `drops/get-user-drops` / `submit-drop-captcha` ——
**抽奖面，不是结账面**，七步尺子对它可能不合身。

### 真正的发现：端点早声明好了，flow 一个都没用

`RetailApiFamilies.ScheelsFrontastic`（R103 起）把整个 action hub 声明成常量，
连两处 Signifyd 升级都有，**还有一条 `Chain` 直接给出购买顺序**。
**而 `ScheelsFlow` 用的是 `/checkout` 和 `/api/checkout/submit` —— 猜的。**

> **所以"缺两步"其实是：① 没实现；② 已实现的指向猜的 URL；③ 真端点已声明但无人调用。**

### 改了什么

`SubmitShippingAsync`（updateCart → completeDetailsCheckout）+
`SubmitPaymentAsync`（setAdyenCreditCard），URL 全取自常量。

**Observation 与 Inference 分开写：**

- **Observation**：URL、名字、顺序（来自 `Chain`）
- **Inference（中）**：**请求体** —— 镜像给了 action 名，没给 JSON 字段名

**这是本轮最薄的一层，注释里写清了，后来人不要当既定事实。**

### 验证

```
构建绿 · scheels 71% → 100% · 完整套件 1751 / 0 · 四项度量未变
71% 组：12 → 11
```

### 仍然 Unknown

- **请求体字段名**（最薄）
- `goat` 该用哪把尺子
- `GetCheckoutAsync` 仍走猜的 `/checkout` —— **已知不一致，故意没和本轮混在一起**
"""

BACKLOG_ADD = """

## 核心 — 结账收尾（续，R766 后）

`scheels` 已补齐并到 100%。**余下 11 个 71% 模块**：

| 模块 | 备注 |
|---|---|
| bstn, casio, fanatics, hbx, hypecommerce, offspring, warhammer, yeezysupply | 待逐一取证原版端点 |
| popmart, superswipe | **非电商形态**，尺子本身要先判定 |
| goat | 端点显示是**抽奖面**（drops + captcha），尺子待判定 |

**另立一项（本轮故意没混做）**：`ScheelsFlow.GetCheckoutAsync` 仍走猜的 `/checkout`，
而真实端点是 `ScheelsFrontastic.Checkout`。改它要动 `OpenCheckoutAsync` 的调用约定。

**以及一个通用风险**：`SubmitShippingAsync`/`SubmitPaymentAsync` 的**请求体是推断**，
镜像只给了 action 名。补任何一步都要把 body 标成推断，不要写成证据。
"""


def main():
    for p, marker, text in ((P1, "R766", BLOCKER), (P3, "R766", BLOCKER), (P2, "第 766 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R766 后" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 余下 11 个 + 两项新立")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R766: Scheels reaches 100% -- the endpoints were never what was missing\n\n"
         "Evidence first: the original's apihub.scheels.com carries seventeen actions, and they include the payment\n"
         "path -- completeDetailsCheckout, setAdyenCreditCard, both Signifyd step-up calls, and the Adyen PayPal\n"
         "pair. So the two steps ModuleCoverageTests reported missing are a real gap in the replica, not something\n"
         "the original lacks too.\n\n"
         "Correction found on the way: goat's endpoints are drops/get-user-drops and submit-drop-captcha, which is\n"
         "a raffle surface rather than a checkout, so the seven-step yardstick may not fit it any better than it fit\n"
         "the 29% group. Recorded as unknown, not acted on.\n\n"
         "The real finding is that the endpoints were declared all along. RetailApiFamilies.ScheelsFrontastic has\n"
         "held the whole Frontastic action hub since R103, Signifyd step-up included, with a Chain that lists the\n"
         "purchase order outright: Login, GetProduct, AddToCart, UpdateCart, Checkout, CompleteDetailsCheckout,\n"
         "SignifydStepUpCode, CompleteSignifydStepUp, SetAdyenCreditCard. ScheelsFlow called none of it, and its\n"
         "checkout steps pointed at /checkout and /api/checkout/submit, which nothing supports.\n\n"
         "So 'two missing steps' was three problems: the steps did not exist, the steps that did exist pointed at\n"
         "invented URLs, and the real endpoints sat declared and unused.\n\n"
         "Added SubmitShippingAsync as updateCart then completeDetailsCheckout, and SubmitPaymentAsync as\n"
         "setAdyenCreditCard, all URLs taken from the declared constants. The comments separate what is observed\n"
         "from what is inferred: the URLs, names and order are evidence, while the request bodies are not -- the\n"
         "image names the actions but not their JSON keys, so the payloads are marked inferred-medium. That is the\n"
         "thinnest layer in this delivery and it is labelled so nobody inherits it as settled.\n\n"
         "Suite 1751 pass / 0 fail, four metrics unchanged, scheels now scores 100% and the 71% group drops from\n"
         "twelve to eleven. GetCheckoutAsync still uses the invented path; that is left as its own item rather than\n"
         "bundled in, because changing it means touching OpenCheckoutAsync's contract."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
