"""Record R767: HBX closes a documented unknown, and eight stores are sorted by shape."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 194. `hbx` 71% → 100%：把一个**写在代码里的 Unknown 真的消掉了**；顺带把 8 个站按形态分了类

> R767。改 `HbxFlow.cs`（+2 步，`SubmitOrderAsync` 从失败桩改为真调用）；
> 新增 `analysis/store_checkout_probe.py`。

### 一、先分类，再动手

对余下 8 个站按域名取 URL 串，按「结账面 / 别的面」分：

| 站 | URL 数 | 结账面 | 别的面 | 判定 |
|---|---|---|---|---|
| **hbx** | 11 | **5** | 0 | **CHECKOUT** |
| casio | 8 | 2 | 0 | CHECKOUT（弱） |
| hypecommerce | 6 | 1 | 0 | 平台侧 API，非店铺结账 |
| bstn / fanatics / offspring / warhammer / yeezysupply | 0 | 0 | 0 | 域名未以 URL 形式出现，需换搜法 |

**所以先做 `hbx`**：它的证据最完整，是一套编号的两段式结账。

### 二、`HbxFlow` 原来写着一句诚实的失败

```csharp
/// <summary>The order endpoint has not been captured yet; the cart path is known, this is not.</summary>
public override Task<StepOutcome> SubmitOrderAsync(...) =>
    Task.FromResult(StepOutcome.Fail("hbx: order endpoint unknown — cart create and add are captured, checkout is not"));
```

**这句话当时是对的**：镜像里 HBX 只有商品面与 cart API。
**但它比我以为的长**（Observation）：

```
https://hbx.com/api/v1/carts
https://hbx.com/checkout?step=1
https://hbx.com/checkout?step=2
https://hbx.com/checkout/pay
```

**所以这一轮做的是「把一个记录在案的 Unknown 消掉」，而不是「猜一个端点」。**

### 三、改了什么

```
SubmitShippingAsync  → HTTP POST  /checkout?step=1
SubmitPaymentAsync   → HTTP POST  /checkout?step=2
SubmitOrderAsync     → HTTP POST  /checkout/pay      （原为失败桩）
```

**Observation**：那四个 URL，以及「结账是编号两步 + 一个独立的 pay 调用」。
**Inference（中）**：step=1 是地址、step=2 是支付方式，**以及三个请求体** —— 镜像只给了端点名，没给字段名。
**这个分工写进了方法注释，没有混在一起。**

### 四、验证

```
构建                已成功
ModuleCoverageTests hbx 71% → 100%（scheels 保持 100%）
完整套件            1751 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（未变）
71% 组              11 → 10
```

### 五、仍然 Unknown

- **三个请求体的字段名**：**Unknown** —— 与 R766 同一层薄。
- `casio` 的收尾步骤形态：**Unknown** —— 只有 `_adyenOrderId` 与 Square PCI hydrate 两条线索。
- `bstn` / `fanatics` / `offspring` / `warhammer` / `yeezysupply` 的端点：**Unknown** ——
  按域名取不到 URL，需要换成「按站点 action 名」或「按 host 前缀」的搜法。
- `HbxFlow` 的类注释仍写着「endpoint that is not known yet」：**已部分过时，未改** ——
  方法级注释现在是权威，但类注释迟早要跟着走。
"""

VERDICT = """

---

## 第 767 轮：把一个写在代码里的 Unknown 消掉

### 先分类再动手

对余下 8 个站按域名取 URL，分「结账面 / 别的面」：

**`hbx` 最完整（5 条结账 URL）**；`casio` 弱（2 条）；`hypecommerce` 是平台侧 API；
`bstn`/`fanatics`/`offspring`/`warhammer`/`yeezysupply` 的域名根本没以 URL 形式出现 —— **要换搜法。**

### `HbxFlow` 原来写着一句诚实的失败

> "The order endpoint has not been captured yet; the cart path is known, this is not."

**那句话当时是对的** —— 而镜像其实比它以为的长（Observation）：

```
hbx.com/api/v1/carts
hbx.com/checkout?step=1
hbx.com/checkout?step=2
hbx.com/checkout/pay
```

**所以这一轮做的是「消掉一个记录在案的 Unknown」，不是「猜一个端点」。**

### 改了什么

`SubmitShippingAsync` → `?step=1`；`SubmitPaymentAsync` → `?step=2`；`SubmitOrderAsync` → `/checkout/pay`（原为失败桩）。

**Observation**：URL 与「编号两步 + 独立 pay」。
**Inference（中）**：哪一步是地址、哪一步是支付，**以及三个请求体** —— 镜像只给端点名，没给字段名。

### 验证

```
构建绿 · hbx 71% → 100% · 套件 1751 / 0 · 度量未变 · 71% 组 11 → 10
```

### 仍然 Unknown

- 三个请求体的字段名（与 R766 同一层薄）
- `casio` 的收尾形态
- 另外 5 个站的端点：**按域名取不到，要换搜法**
- `HbxFlow` 类注释已部分过时（方法级注释现在是权威）
"""

BACKLOG_ADD = """

## 核心 — 结账收尾（R767 后）

已到 100%：`scheels`（R766）、`hbx`（R767）。

**余下 9 个**：

| 模块 | 已知线索 | 下一步 |
|---|---|---|
| casio | `_adyenOrderId` + Square PCI hydrate | 补搜，判断收尾形态 |
| hypecommerce | `admin.hypecommerce.io/api/payment/methods/store` | **平台侧 API，可能是尺子问题** |
| bstn, fanatics, offspring, warhammer, yeezysupply | 域名未以 URL 出现 | **换搜法**：按 action 名 / host 前缀 |
| popmart, superswipe | 非电商形态 | 先定尺子 |
| goat | drops + submit-drop-captcha | **抽奖面，先定尺子** |

**通用风险（两轮都出现）**：新补的 `SubmitShippingAsync`/`SubmitPaymentAsync` 的**请求体都是推断**，
镜像只给 action 名。补任何一步都要把 body 标成推断。

**另立**：`ScheelsFlow.GetCheckoutAsync` 与 `HbxFlow` 的类注释都有过时表述，各自独立处理。
"""


def main():
    for p, marker, text in ((P1, "R767", BLOCKER), (P3, "R767", BLOCKER), (P2, "第 767 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R767 后" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 余下 9 个（按线索分组）")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R767: HBX reaches 100% by closing a documented unknown, and eight stores sorted by shape\n\n"
         "Before touching anything, the remaining stores were sorted by what kind of surface the image names for\n"
         "each. hbx came out cleanest with five checkout URLs; casio weak with two; hypecommerce turned out to be a\n"
         "platform-side payment-methods API rather than a store checkout; and five stores -- bstn, fanatics,\n"
         "offspring, warhammer, yeezysupply -- have no URL at all under their domains, so they need a different\n"
         "search rather than a different conclusion.\n\n"
         "HbxFlow had been honest about its own gap. Its SubmitOrderAsync returned a failure whose message said the\n"
         "order endpoint had not been captured, with a doc comment to match. That was accurate when written, and the\n"
         "image is longer than the flow assumed: the cart API, then checkout?step=1, checkout?step=2, and\n"
         "checkout/pay. So this round removed a recorded unknown rather than guessing an endpoint.\n\n"
         "SubmitShippingAsync posts to step=1, SubmitPaymentAsync to step=2, and SubmitOrderAsync now calls\n"
         "checkout/pay instead of failing. What is observed is the four URLs and the fact that checkout is numbered\n"
         "in two steps with a separate pay call; what is inferred -- medium -- is which numbered step is the address\n"
         "and which the payment method, and all three request bodies, since the image names endpoints and not their\n"
         "fields. The split is written into the method comments.\n\n"
         "Suite 1751 pass / 0 fail, four metrics unchanged, hbx moves from 71% to 100% and the 71% group drops to\n"
         "ten. Left as its own item: HbxFlow's class comment still says a step will report a missing endpoint, which\n"
         "is now partly out of date even though the method-level doc is authoritative."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
