"""Record R948: criterion (f) closes -- the three unmatched store hosts were payment hosts."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 判据 (f) 关：三个 unmatched 的 store host，**全是支付 host**（R948）

**判据 (f) 要求「原版站点与风控清单从二进制取证 ↔ `Registry.cs` 与 `Flows/Scripts` 逐条对，
未覆盖的每条写为什么」。跑两个工具：**

```
vendor 侧: 12 个 host，absent from src 0
store  侧: 27 个 host，unmatched 3
```

### 三个 unmatched

```
api.braintreegateway.com    2 paths
api.vipps.no                1 paths
payments.bigcommerce.com    1 paths
```

**而它们**全是支付 host，不是店** —— 所以没有任何 store flow 认领它们。那不是缺口，是**分类错位**：
它们在 store 侧被数，而它们属于支付侧。**

### 而三条都有具体路径

```
Braintree   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account
            /merchants/rfbkw27jcwmw2xgp/client_api/v1/paypal_hermes/create_payment_resource
            assets.braintreegateway.com        （第二个 host）
Vipps       /adyen-card-enrollment/initiate · /commit
            /checkout-frontend/session/        （第二个 host：checkout.vipps.no）
BigCommerce /api/public/v1/orders/payments
```

> **而 Braintree 那个 `rfbkw27jcwmw2xgp` 是**商户 id**，硬写在镜像里。
> 它按商户不按厂商 —— 所以它属于**一家店**，而记住它错了会把钱打到别的商户。**

### 而 `VippsNo` 我按措辞记，不按地区记

**那串旁边还有 `3DS Unsupported (VippsNo)`。**

> **`No` 可以是 Norway，也可以是「否」。而它有第二种解释 —— 所以记成措辞，不记成 locale 标识。**

### 而工具的数字自己动了

**加完 `PaymentHostGaps.cs` 之后：**

```
store hosts matched: 27
store hosts unmatched: 0
```

> **不是因为补了三个 flow，而是因为那三个 host 现在**有名字**在 src 里。
> 而 `core_coverage.py` 的判据就是「某个注册里含这个 host 的标签」——
> 所以它从 3 变 0，说明的是**工具的条件被满足了**，不是**集成完成了**。**
> **而那个 caveat 工具自己印在最后一行：「matched 不代表实现对了」。**

### 数字

| 度量 | R947 | **R948** |
|---|---|---|
| 套件 | 2053 | **2059** |
| 产物陈旧度 | 10 文件 / 1044 行 | **11 文件 / 1153 行** |
| **store host unmatched** | 3 | **0** |
| **vendor host absent** | 0 | **0** |

### 教训

> **判据 (f) 的 store 侧从 3 变 0，而**没有任何一个 flow 被写出来**。
> 变的只是「这三个 host 在不在 src 里」这件事 —— 而工具的判据正是这个。**
> **所以「unmatched: 0」这句话是真的，而它不等于「覆盖完成」。
> 一个度量能归零，而它归零的原因可能只是**你让被度量的东西出现了**。****
> **而这一轮的真实产出是那三条路径 + 一个商户 id —— 数字归零只是它的副作用。**
"""

if "判据 (f) 关：三个 unmatched" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 948 轮：判据 (f) 关 —— 三个 unmatched 的 store host 全是支付 host

### 跑两个工具

```
vendor 侧: 12 host, absent from src 0
store  侧: 27 host, unmatched 3
```

### 三个 unmatched 全是支付 host，不是店

```
api.braintreegateway.com · api.vipps.no · payments.bigcommerce.com
```

**所以没有任何 store flow 认领它们 —— 那不是缺口，是**分类错位**。**

### 三条都有具体路径

```
Braintree   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account
            .../paypal_hermes/create_payment_resource · assets.braintreegateway.com
Vipps       /adyen-card-enrollment/{initiate,commit} · /checkout-frontend/session/ · checkout.vipps.no
BigCommerce /api/public/v1/orders/payments
```

**而 `rfbkw27jcwmw2xgp` 是**商户 id**，按商户不按厂商 —— 记错会把钱打到别的商户。**

### `VippsNo` 按措辞记不按地区记

**旁边还有 `3DS Unsupported (VippsNo)`。`No` 可以是 Norway 也可以是「否」→ 记成措辞。**

### 而工具的数字自己动了

```
store hosts matched: 27 · unmatched: 0
```

> **不是补了三个 flow，而是那三个 host 现在**有名字**在 src 里 ——
> 而工具的判据正是「某个注册含这个 host 的标签」。
> 所以 3 → 0 说明**工具的条件被满足了**，不是**集成完成了**。
> 而那个 caveat 工具自己印着：「matched 不代表实现对了」。**

### 数字

| 度量 | R947 | **R948** |
|---|---|---|
| 套件 | 2053 | **2059** |
| 产物陈旧度 | 10 / 1044 | **11 / 1153** |
| store host unmatched | 3 | **0** |
| vendor host absent | 0 | **0** |

### 教训

> **判据 (f) 的 store 侧从 3 变 0，而**没有任何一个 flow 被写出来**。
> 变的只是「这三个 host 在不在 src 里」—— 而工具的判据正是这个。**
> **一个度量能归零，而它归零的原因可能只是**你让被度量的东西出现了**。**
> **真实产出是那三条路径 + 一个商户 id；数字归零只是副作用。**
"""

BACKLOG_ADD = """

## 判据 (f) — store host unmatched 3 → 0；三个都是支付 host（R948，**+6 用例**）

### 三个 host 与路径

**Braintree（含商户 id `rfbkw27jcwmw2xgp`，两条 client_api 路径 + 一个 asset host）·
Vipps（三条路径 + `checkout.vipps.no`）· BigCommerce（一条 `/api/public/v1/orders/payments`）**

### `Payments/PaymentHostGaps.cs`

**`Braintree.{MerchantId, Paths, AssetHost, ApiHost, UrlFor}` · `Vipps.{Paths, ApiHost, CheckoutHost, Messages, Urls}` ·
`BigCommerce.{PaymentsPath, Host, Url}` · `Hosts` · `IsPaymentHost`**

### 两条纪律

**① 商户 id 按商户不按厂商 —— 记错打错钱。**
**② `VippsNo` 按措辞不按地区 —— `No` 有两种解释。**

### 而数字归零的原因

**不是补了 flow，是那三个 host 现在在 src 里有名字 —— 工具的判据正是这个。**

### 数字

**套件 2053 → 2059 · 陈旧度 10/1044 → 11/1153 · store unmatched 3 → 0 · vendor absent 0**

| 仍 Unknown | |
|---|---|
| 三个 host 属哪家店 | 字符串里没店名 |
| `VippsNo` 是地区还是「否」 | 两种解释 |
| 集成是否真能用 | 只有 host 与路径 |

**纪律**：一个度量能归零，而它归零的原因可能只是你让被度量的东西出现了。
"""

BLOCKER = """

---

## 372. 判据 (f)：store host unmatched 3 → 0

> R948。**改产品代码 +6 用例。** 套件 **2059 通过 / 0 失败 / 0 跳过**。

### 一、两个工具

```
vendor 侧: 12 host, absent from src 0
store  侧: 27 host, unmatched 3
```

### 二、三个 unmatched 全是支付 host

```
api.braintreegateway.com (2) · api.vipps.no (1) · payments.bigcommerce.com (1)
```

**不是店 → 没有 store flow 认领它们 → 分类错位，不是缺口。**

### 三、三条路径

```
Braintree   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account
            .../paypal_hermes/create_payment_resource · assets.braintreegateway.com
Vipps       /adyen-card-enrollment/{initiate,commit} · /checkout-frontend/session/
BigCommerce /api/public/v1/orders/payments
```

**`rfbkw27jcwmw2xgp` 是商户 id，按商户不按厂商。**

### 四、`VippsNo` 按措辞记

**旁边有 `3DS Unsupported (VippsNo)`；`No` 可作 Norway 或「否」→ 记措辞。**

### 五、而数字归零的原因

**store hosts matched 27 / unmatched 0 —— 不是补了 flow，是那三个 host 现在有名字在 src 里。
工具的判据就是「某个注册含这个 host 的标签」，而它自己印着「matched 不代表实现对了」。**

### 六、数字

| 度量 | R947 | R948 |
|---|---|---|
| 套件 | 2053 | **2059** |
| 产物陈旧度 | 10 / 1044 | **11 / 1153** |
| **store unmatched** | 3 | **0** |
| vendor absent | 0 | **0** |

### 七、验证

```
python tools/core_coverage.py    -> store hosts unmatched: 0
python tools/vendor_coverage.py  -> vendors absent from src: 0
analysis/ida.py str braintreegateway -> 4（含商户 id）
test --filter PaymentHostGapTests    -> 6 通过
metrics_report.py                    -> 2059 通过 / 0 失败
```

### 八、仍然 Unknown

- **三个 host 属哪家店**：**Unknown** —— 字符串里没有店名。
- **`VippsNo` 是地区还是「否」**：**Unknown** —— 两种解释。
- **集成是否真能用**：**Unknown** —— 只有 host 与路径。

### 九、教训

**判据 (f) 的 store 侧从 3 变 0，而没有任何一个 flow 被写出来。**

**变的只是「这三个 host 在不在 src 里」—— 而工具的判据正是这个。**

**一个度量能归零，而它归零的原因可能只是你让被度量的东西出现了。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R948", BLOCKER)
    ensure(RSTATUS, "R948", BLOCKER)
    ensure(RVERDICT, "第 948 轮", VERDICT)
    ensure(BACKLOG, "R948", BACKLOG_ADD)

    note = (
        "\n## R948 补充 — 判据 (f)：store host unmatched 3 → 0；三个都是支付 host（+6 用例，套件 2059）\n\n"
        "vendor 侧 12 host absent 0；store 侧 27 host unmatched 3 = api.braintreegateway.com / api.vipps.no / "
        "payments.bigcommerce.com —— 全是支付 host 不是店。\n\n"
        "三条路径：Braintree（含商户 id rfbkw27jcwmw2xgp，两条 client_api + assets host）· "
        "Vipps（adyen-card-enrollment/{initiate,commit} + checkout-frontend/session + checkout.vipps.no）· "
        "BigCommerce（/api/public/v1/orders/payments）。\n\n"
        "VippsNo 按措辞记不按地区记（No 可作 Norway 或「否」）。\n\n"
        "而 store unmatched 3 → 0 不是补了 flow，是那三个 host 现在在 src 里有名字 —— 工具的判据正是这个。\n\n"
        "数字：套件 2053 → 2059 · 陈旧度 10/1044 → 11/1153 · store unmatched 3 → 0。\n\n"
        "纪律：一个度量能归零，而它归零的原因可能只是你让被度量的东西出现了。\n\n"
        "下一轮：判据 (c) 产物级对照（target\\Cybersole.exe ↔ .publish-aot）重算一次；或 ③ 请求与指纹层。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R948" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R948"), (RSTATUS, "R948"), (RVERDICT, "第 948 轮"), (BACKLOG, "R948")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R948: criterion (f) closes, and the three unmatched store hosts were payment hosts\n\n"
         "Criterion (f) asks for a coverage table the original's hosts can be checked against item by item. The vendor\n"
         " side is clean at twelve named and none absent; the store side reported twenty-seven hosts with three unmatched:\n"
         " api.braintreegateway.com, api.vipps.no and payments.bigcommerce.com.\n\n"
         "All three are payment hosts rather than shops, which is why no store flow claimed them -- a category mismatch\n"
         " rather than a missing integration. And all three carry concrete paths: Braintree has two client_api endpoints\n"
         " under a merchant id the image hard-codes, plus a separate asset host; Vipps has the Adyen card enrollment pair\n"
         " and a checkout frontend session path on a second host; BigCommerce has one endpoint for recording a payment\n"
         " against an order.\n\n"
         "Two details were recorded rather than smoothed over. The Braintree merchant id is per-merchant rather than\n"
         " per-vendor, so recording it wrong would route money to another merchant. And VippsNo sits beside\n"
         " 3DS Unsupported (VippsNo), where No can be Norway and can be the word, so it is kept as wording instead of\n"
         " being read as a locale.\n\n"
         "The coverage number then moved to zero without a single flow being written, because the tool's test is whether\n"
         " some registration contains the host's label, and the new file puts the labels there. So the zero says the tool's\n"
         " condition was met, not that anything is integrated -- the tool prints that caveat itself, and this round is a\n"
         " clean example of why it does.\n\n"
         "Figures: suite 2053 to 2059, freshness from ten files to eleven and a thousand and forty-four lines to a\n"
         " thousand one hundred and fifty-three, and store hosts unmatched from three to none.\n\n"
         "Unknown: which shop each of the three serves, since none of these strings names a store; whether VippsNo is a\n"
         " region or a denial; and whether any of it works, of which only hosts and paths survive.\n\n"
         "The lesson is that a metric can reach zero simply because the thing it measures was made to appear. The real\n"
         " output this round was three path sets and a merchant id, and the zero was a side effect.\n\n"
         "Product code changed; suite green at 2059."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()