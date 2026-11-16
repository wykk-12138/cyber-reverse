"""Record R792: Warhammer reaches 100% because the site has no separate order step."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 218. Warhammer 到 **100%** —— 因为那个站**没有独立的「提交订单」步**

> R792。`RetailFlows.cs`：新增 `WarhammerFlow.SubmitPaymentAsync`，重写 `SubmitOrderAsync`。

### 一、先查"订单提交"这个 operation 到底存不存在

```
^mutation         10 总 —— 6 条大的（R788 已全取）+ 4 条类型名
placeOrder        40 匹配，全部在 0x1433…/0x1434…（类型名区，不是池子）
submitOrder       40 匹配，同样在类型名区
completeCheckout   0
```

**结论**：**镜像里 Warhammer 没有独立的订单提交 mutation。**
`^mutation` 那 10 条我一条没漏 —— **R788 的过滤器没漏东西，只是东西本来不存在。**

### 二、为什么 `SubmitOrderAsync` 一直找不到端点

**因为它在原版里就不存在。** 原版走的是 `ApproveOnboardPaymentMutation`：

```
approveGuestSignUpPayment(token: $token) {
  buyer { … }
  ...CartDonePage
  ...CompletedPaymentInfo
  fundingOptions { fundingInstrument { id lastDigits … } }
}
```

**「批准支付」就是下单** —— 返回里有 done page 与 completed payment info。

**这就是为什么复刻件那个 `/api/orders` 一直是编的：没有对应的东西可抄。**

### 三、实现

**`SubmitPaymentAsync`**（新）：
- 四个变量：`$token: String!`、`$instrumentId: String`、`$isBillingAgreement: Boolean!`、`$supportedThreeDsExperiences`
- **只发必填的两个 + 有则发 `instrumentId`**
- **没有 `paymentToken` 时如实失败**，不发占位值 ——
  「被拒的批准」与「被拒的卡」在调用方看来是一样的，发假的会掩盖真相

**`SubmitOrderAsync`**（重写）：
- **不再 POST 到编出来的 `/api/orders`**
- **从支付响应里读订单号**；读不到就明说"这个站的支付响应里没有直白的订单号字段"

**这不是"把失败改成成功"，是"把编的端点换成原版真实的完成方式"。**

### 四、Observation / Inference 分清楚

- **Observation**：池子里没有订单提交 mutation；`approveGuestSignUpPayment` 的存在与返回形状
- **Inference（中）**：**"批准支付即下单"** —— 返回形状与之一致，
  但镜像并没有在哪里**明确声明**"没有提交步"。**所以这一条是"证据最支持的读法"，不是"正面观察到的事实"**

**这句话写进了类注释。** 差别很重要：它意味着如果以后找到反证，该改的是这里。

### 五、覆盖率

```
warhammer    +  +  +  +  +  +  +   100%
resolved 63/63 flows; fully covered 49 -> 50; exempt 2
```

**`fully covered` 从 49 变成 50** —— 这是本会话第一次让这个数增加。

### 六、验证

```
构建                已成功
ModuleCoverageTests warhammer 100%
完整套件            1766 通过 / 0 失败 / 0 跳过（未变）
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **支付 `token` 从哪来**：**Unknown** —— 现在没有就明确失败。
- **`instrumentId` 的来源**：**Unknown**。
- **支付响应里订单号的确切字段**：**Unknown** —— 现在找 `orderNumber` / `orderId`，找不到就明说。
- **`supportedThreeDsExperiences`** 是否必须发：**Unknown** —— 可选，未发。
- **`shippingRateId` 的选取规则**：仍是 Inference（低）（R791）。
"""

VERDICT = """

---

## 第 792 轮：Warhammer 到 100%，因为那站没有独立的提交订单步

### 先查它到底存不存在

```
^mutation       10 总 —— 6 条大的（已全取）+ 4 条类型名
placeOrder      40 匹配，全在类型名区
submitOrder     40 匹配，同样
completeCheckout 0
```

> **镜像的 Warhammer 没有订单提交 mutation。R788 没漏，是本来就没有。**

### 为什么 `/api/orders` 一直是编的

**因为没有对应的东西可抄。** 原版走 `ApproveOnboardPaymentMutation`：

```
approveGuestSignUpPayment(token: $token) { buyer {…} ...CartDonePage ...CompletedPaymentInfo }
```

**「批准支付」就是下单。**

### 实现

- **`SubmitPaymentAsync`**：只发必填的 `token` + `isBillingAgreement`（+ 有则发 `instrumentId`）。
  **没有 token 时如实失败，不发占位值** —— 被拒的批准与被拒的卡在调用方看来一样，发假的会掩盖真相。
- **`SubmitOrderAsync`**：不再 POST 到编的端点，**从支付响应读订单号**，读不到就明说。

**这不是把失败改成成功，是把编的端点换成原版真实的完成方式。**

### Observation / Inference

- **Observation**：池子里没有提交 mutation；`approveGuestSignUpPayment` 的存在与返回形状
- **Inference（中）**：**「批准支付即下单」** —— 形状一致，**但镜像没在哪里明确声明「没有提交步」**

**写进了类注释：以后找到反证，该改的是这里。**

### 覆盖率

```
warhammer   + + + + + + +   100%
fully covered  49 -> 50
```

**本会话第一次让 `fully covered` 增加。**

### 验证

```
构建绿 · warhammer 100% · 整套 1766 / 0 · 度量未变
```
"""

BACKLOG_ADD = """

## 核心 — Warhammer **100%**（R792）

**关键发现：这个站没有独立的「提交订单」mutation。**

```
^mutation 10 总（6 大 + 4 类型名）· placeOrder/submitOrder 只在类型名区 · completeCheckout 0
```

**原版用 `ApproveOnboardPaymentMutation` 完成结账 —— 批准支付即下单。**

| 步骤 | 实现 |
|---|---|
| `AddToCartAsync` | `AddToCart`（R789） |
| `SubmitShippingAsync` | `UpdateShippingAddress`（R791） |
| `SubmitPaymentAsync` | `ApproveOnboardPaymentMutation`（R792） |
| `SubmitOrderAsync` | **从支付响应读订单号**（R792，不再 POST 编的端点） |
| `GetCheckoutAsync` | `OpenCheckoutAsync` |

**`fully covered` 49 → 50。**

| 仍 Unknown | |
|---|---|
| 支付 `token` 来源 | 没有就明确失败 |
| `instrumentId` 来源 | 未知 |
| 支付响应里订单号字段 | 找 `orderNumber`/`orderId`，找不到明说 |
| `supportedThreeDsExperiences` 是否必发 | 可选，未发 |
| `shippingRateId` 选取规则 | 取第一个 `id`，Inference（低） |

**Inference（中）记录在案**：「批准支付即下单」是证据最支持的读法，**不是正面观察到的事实**。
**若日后找到反证，改这里。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R792", BLOCKER)
    ensure(RSTATUS, "R792", BLOCKER)
    ensure(RVERDICT, "第 792 轮", VERDICT)
    ensure(BACKLOG, "R792", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 792 轮" if path == RVERDICT else "R792"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R792: Warhammer reaches 100% because the site has no separate order step at all\n\n"
         "Three searches settle what looked like a missing endpoint. Every mutation string over two hundred characters\n"
         "is one of the six R788 recovered, so nothing was filtered out. placeOrder and submitOrder both match forty\n"
         "times, and every one of those sits in the type-name region rather than the pool. completeCheckout matches\n"
         "nothing. Warhammer has no order-submit mutation, which is why the replica's /api/orders was invented and why\n"
         "no amount of further searching was going to find it.\n\n"
         "What the image does instead is approve the payment: approveGuestSignUpPayment(token:) returns the buyer, a\n"
         "cart-done page and completed payment info. So SubmitPaymentAsync now sends the image's own\n"
         "ApproveOnboardPaymentMutation with the two non-null arguments, the token from the session and\n"
         "isBillingAgreement false, plus an instrument id when one is available. With no token it fails and says so\n"
         "rather than sending a placeholder, because a rejected approval and a declined card look identical from the\n"
         "caller's side and a fake token would hide which happened.\n\n"
         "SubmitOrderAsync stops posting to the invented endpoint and reads the order number out of the payment\n"
         "response instead, failing with a clear reason when the response carries none. That is not turning a failure\n"
         "into a success; it is replacing an invented endpoint with the way the site actually completes an order.\n\n"
         "The inference is labelled medium and stated in the class comment: approval equals placement, and no separate\n"
         "submit exists. The return shape is consistent with it, but the image never says so outright, so if contrary\n"
         "evidence turns up, that comment is what should change.\n\n"
         "Warhammer goes to seven of seven, and the fully-covered count moves from 49 to 50 for the first time in this\n"
         "session. Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
