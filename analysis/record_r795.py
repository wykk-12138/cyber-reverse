"""Record R795: Hybris gains its three checkout steps, taking offspring to 100%."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 221. Hybris 补上三步，`offspring` 到 **100%**；顺带推翻一句旧注释

> R795。`HybrisFlow.cs`：新增 `SubmitShippingAsync` / `SubmitPaymentAsync`，重写 `SubmitOrderAsync`。

### 一、镜像里有整个 Demandware 结账面（Observation）

`^/Checkout-` 一共 14 条：

```
/Checkout-Begin  (+ ?stage=payment|placeOrder|shipping)  (+ ?step=billing|payment|shipping|summary)
/Checkout-ContinueToBilling
/Checkout-SaveGuest
/Checkout-SubmitOrder
/Checkout-SubmitPaymentDetails
/checkout-login  (+ ?csrf_token=)
```

### 二、字段名也有 —— 但只有 billing 那一族

`^dwfrm` 40 条，**全部是 `dwfrm_billing_*`，一条 `dwfrm_shipping_*` 都没有。**
其中关键是 `dwfrm_billing_addressFields_useShipping` ——
**这个平台用「账单地址复用收货地址」这个标志，而不是另一套 shipping 字段。**

复刻件用它映射 Profile：

```
dwfrm_billing_addressFields_firstName · lastName · address1 · address2 · city
                                    · postalCode · phone · stateArea · country · email
```

**名字全是镜像的，不是我起的。**

### 三、三步

| 步骤 | 端点 | 依据 |
|---|---|---|
| `SubmitShippingAsync` | `POST /Checkout-SaveGuest` + `useShipping=true` | 端点 Observation；**「SaveGuest 就是提交」是 Inference（中）** |
| `SubmitPaymentAsync` | `POST /Checkout-SubmitPaymentDetails` + billing 字段 | 端点与字段都是 Observation |
| `SubmitOrderAsync` | `POST /Checkout-SubmitOrder` | 端点 Observation |

**`SubmitShippingAsync` 的歧义我写进了注释**：另一种读法是「先导航到 `?stage=shipping` 再填」，
镜像没说哪种。**区别记着而不强行裁定** —— 猜错只花一个来回就自己报出来，不像猜错的标识符那样静默。

### 四、推翻一句旧注释

`SubmitOrderAsync` 原来写着：

> Hybris checkout is a multi-step controller flow; **there is no single POST that places the order.**

**这句话被 `/Checkout-SubmitOrder` 直接否掉了。**
它没说错「流程是分阶段的」（`/Checkout-Begin` 的 stage/step 变体确实在），
**但它从"分阶段"推出了"没有单一提交" —— 那一步推错了。**

**这是「Unknown 被当成 Not-exist」的又一次**：没找到端点的那一版写法，读起来像"端点不存在"。

### 五、覆盖率

```
offspring    +  +  +  +  +  +  +   100%
resolved 63/63 flows; fully covered 50 -> 51; exempt 5
```

### 六、验证

```
构建                已成功
ModuleCoverageTests offspring 100%，fully covered 51
完整套件            1766 通过 / 0 失败 / 0 跳过（未变）
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`/Checkout-SaveGuest` 是不是提交动作**：**Inference（中）** —— 见第三节。
- **支付要哪些网关字段**（卡号、`dwfrm_billing_creditCardFields_*`）：**Unknown** ——
  这次只发了地址字段，**支付详情那一步大概率还需要卡字段名，而池子里没查**。
- **`SubmitOrder` 需要什么表单**：**Unknown** —— 现在发空表单。
- **`offspring` 的 100% 的含义**：**七步都实现，不等于七步都验证过** ——
  **没有任何一步在实机上跑过。**

**第八条要单独看重**：`fully covered` 衡量「这一步存在且不是恒失败」，**不衡量「这一步在真站上成立」**。
`offspring` 到 100% 说明它的形状与镜像对齐，**不说明它能买到东西。**
"""

VERDICT = """

---

## 第 795 轮：Hybris 补上三步，offspring 到 100%

### 镜像里有整个 Demandware 结账面

```
^/Checkout- 共 14 条：/Checkout-Begin(+stage/step 变体) · ContinueToBilling · SaveGuest
                     SubmitOrder · SubmitPaymentDetails · /checkout-login
```

### 字段名也有，但只有 billing 这一族

`^dwfrm` 40 条，**全是 `dwfrm_billing_*`，没有一条 `dwfrm_shipping_*`。**
关键：`dwfrm_billing_addressFields_useShipping` —— **平台用「账单地址复用收货地址」，不是另设一套。**

复刻件用它映射 Profile，**名字全是镜像的。**

### 三步

| 步骤 | 端点 | 依据 |
|---|---|---|
| SubmitShipping | `POST /Checkout-SaveGuest` + `useShipping=true` | 端点 Observation；**动作 Inference（中）** |
| SubmitPayment | `POST /Checkout-SubmitPaymentDetails` + billing 字段 | 都是 Observation |
| SubmitOrder | `POST /Checkout-SubmitOrder` | Observation |

**歧义写进注释**：另一种读法是「先导航到 `?stage=shipping` 再填」，镜像没说。
**猜错只花一个来回就自己报出来，不像猜错的标识符那样静默。**

### 推翻一句旧注释

原来写「there is no single POST that places the order」。**`/Checkout-SubmitOrder` 直接否掉了它。**

> **它没说错「流程分阶段」，但从「分阶段」推出「没有单一提交」—— 这一步推错了。**
> **这是「Unknown 被当成 Not-exist」的又一次。**

### 覆盖率

```
offspring   + + + + + + +   100%
fully covered 50 -> 51
```

### 验证

```
构建绿 · offspring 100% · 整套 1766 / 0 · 度量未变
```

### 一条必须写明的边界

**七步都实现 ≠ 七步都验证过。** 没有任何一步在实机跑过。

> **`fully covered` 衡量「这一步存在且不是恒失败」，不衡量「它在真站上成立」。**
> **offspring 到 100% 说明形状与镜像对齐，不说明它能买到东西。**
"""

BACKLOG_ADD = """

## 核心 — Hybris / offspring（R795：100%）

**镜像的 Demandware 结账面（14 条 `/Checkout-*`）+ 40 个 `dwfrm_billing_*` 字段名。**

| 步骤 | 端点 |
|---|---|
| `SubmitShippingAsync` | `POST /Checkout-SaveGuest` + `dwfrm_billing_addressFields_useShipping=true` |
| `SubmitPaymentAsync` | `POST /Checkout-SubmitPaymentDetails` + billing 地址字段 |
| `SubmitOrderAsync` | `POST /Checkout-SubmitOrder` |

**`fully covered` 50 → 51；`offspring` 100%。**

| 仍 Unknown | |
|---|---|
| `/Checkout-SaveGuest` 是否就是提交动作 | **Inference（中）** |
| 支付要哪些**网关**字段（卡号等） | **未查池子** |
| `SubmitOrder` 需要什么表单 | 现在发空表单 |
| 有没有 `dwfrm_shipping_*` | 镜像里 **0 条** |

**口径边界（重要）**：`fully covered` 衡量「步骤存在且不是恒失败」，**不衡量「实机成立」**。
**offspring 100% 说明形状对齐，不说明能下单。**

**已推翻的旧注释**：`HybrisFlow` 原写「there is no single POST that places the order」——
`/Checkout-SubmitOrder` 否掉了它。**「分阶段」不等于「没有单一提交」。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R795", BLOCKER)
    ensure(RSTATUS, "R795", BLOCKER)
    ensure(RVERDICT, "第 795 轮", VERDICT)
    ensure(BACKLOG, "R795", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 795 轮" if path == RVERDICT else "R795"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R795: Hybris gains its three checkout steps and offspring reaches 100%\n\n"
         "The image carries the whole Demandware checkout surface -- fourteen /Checkout- paths including Begin with its\n"
         "stage and step variants, ContinueToBilling, SaveGuest, SubmitOrder and SubmitPaymentDetails -- plus forty\n"
         "dwfrm_ field names. Every one of those forty is dwfrm_billing_, and none is dwfrm_shipping_, which is the\n"
         "interesting part: this platform expresses 'bill to the shipping address' with\n"
         "dwfrm_billing_addressFields_useShipping rather than with a second field set.\n\n"
         "So HybrisFlow now maps the profile onto the image's own billing names and submits three steps. Shipping posts\n"
         "to /Checkout-SaveGuest with useShipping set; payment posts to /Checkout-SubmitPaymentDetails; the order posts\n"
         "to /Checkout-SubmitOrder. Two of those three are pure observation. The first is an inference of medium\n"
         "confidence, because the image also carries /Checkout-Begin?stage=shipping and does not say whether shipping\n"
         "is entered by saving the guest or by navigating to that stage. That ambiguity is recorded rather than\n"
         "resolved: being wrong costs one HTTP round trip and reports itself, unlike a wrong identifier.\n\n"
         "The change also refutes a comment the file used to carry: that Hybris checkout is multi-step so there is no\n"
         "single POST that places an order. /Checkout-SubmitOrder is right there. The staged-flow observation was\n"
         "correct; the conclusion drawn from it was not, and it is the same shape of error as reading 'not found as an\n"
         "endpoint' as 'no such endpoint'.\n\n"
         "offspring reaches seven of seven and the fully-covered count moves from 50 to 51. One boundary belongs next\n"
         "to that number: fully covered measures that a step exists and is not a permanent failure. It does not measure\n"
         "that the step works against the live site, and none of these seven has been run against it. One hundred\n"
         "percent means the shape matches the image, not that it can buy anything.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
