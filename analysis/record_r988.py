"""Record R988: the store denominator was padded with payment gateways."""

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
### 判据 (f) 的 store 分母虚高 12 —— `VENDOR_HINTS` 少了十二个支付网关（R988）

**R987 说下一轮核「35 个 flow vs 27 个 host 差 8」。
核的过程中发现 27 这个分母本身是错的：**十二个 host 不卖东西**。**

### ① 分类靠一份手写名单，而名单不完整

**`core_coverage.py` 把 host 分成 store 与 vendor 两桶，判据是 `VENDOR_HINTS` 里有没有这个标签。
而那份名单是从**风控厂商**加**三个大支付**写出来的：**

```python
"cloudflare", "kasada", "datadome", "perimeterx", "queue-it", "recaptcha", "hcaptcha",
"akamai", "aycd", "turnstile", "captcha", "paypal", "stripe", "adyen", "paynamics",
"eshopworld", "global-e", "vivapayments", "wdprapps", "disney", "purpledotprice", "purpledot"
```

> **名单之外的标签**默认**就是 store** —— 因为判据是「有没有被列进 vendor」。**
> **于是 `api.braintreegateway.com` · `api.sibspayments.com` · `api.vipps.no` ·
> `app.midtrans.com` · `degica.as1.gpayments.net` · `ecommerce-gateway.mollie.com` ·
> `flex.cybersource.com` · `payments.bigcommerce.com` · `retry.touchtechpayments.com` ·
> `threeds.airwallex.com` · `static-forms.klaviyo.com` · `www.ibm.com`
> —— **十二个支付/身份/表单网关 —— 全被算成了「店」。****

### ② 补上之后

```
改前: hosts with a path: 39  (store 27, vendor 12)
改后: hosts with a path: 39  (store 15, vendor 24)

store hosts matched:   15
store hosts unmatched:  0
```

**→ 判据 (f) 的 store 覆盖从「27/27」变成「15/15」，而 0 unmatched 不变。**

> **分母小了十二个，而分子一个没少 —— 所以**覆盖率没变，诚实度变了**。
> 而判据 (f) 要的是「原版**站点**清单」，不是「原版**主机**清单」。**
> **一个掺了支付网关的分母，会让「27/27」描述一件不是它名字所说的事。**

### ③ 一个我特意**没有**动的

**`authenticate.riotgames.com` 留在了 store 桶**，理由写进代码注释：
它是身份 host，但 registry 里**也有**一个 `riotgames` store flow ——
**把它移走会把这个配对藏起来，而不是修好一个标签。**

### ④ 而 METRICS 里那两个 vendor 数字**不是矛盾**

**改完后 `core_coverage` 报 vendor 桶 24，而 METRICS 的 vendor 度量报 12 —— 我去查了，不是同一件事：**

| 工具 | 分母 | 值 |
|---|---|---|
| `core_coverage.py` 的 vendor 桶 | 支付 + 风控 + 平台基础设施 host | **24** |
| `vendor_coverage.py`（METRICS 读的） | **风险厂商**（cloudflare / kasada / …） | **12** |

> **两个工具各自一致，而它们的「vendor」不是同一个概念 —— 这一点值得记，
> 但不构成缺陷。而**如果我没查就当成矛盾去改，会把一个正确的工具改坏**（R980 的同一课）。**

### ⑤ 一个仍然敞着的

**`core_coverage` 的 vendor 段只搜 `Scripts/`，所以 24 个里 20 个是 `unmatched`。
而 store 段搜整个 `src`。两段口径不同，输出里没写这一点。**

> **→ 记 Unknown：vendor 段的 unmatched 里有多少是「真的没实现」，多少是「实现不在 Scripts/ 里」。
> 这一轮没有分开，所以不能从 20 这个数读出任何关于覆盖率的结论。**

### 数字

| 度量 | R987 | **R988** |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **判据 (f) store 分母** | 27 | **15** |
| **store matched / unmatched** | 27 / 0 | **15 / 0** |
| **core_coverage vendor 桶** | 12 | **24** |

### 教训

> **「名单之外的默认是 store」是一条**默认规则**，而默认规则的错永远朝一个方向犯：
> 新东西被算进多数那一类，于是没人看得见。**
> **十二个支付网关在「27 个店」里待了很多轮，而它们每一个的输出行都写着 `matched` ——
> 一个错的分母会让每一行都看起来是对的。**
"""

if "判据 (f) 的 store 分母虚高 12" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 988 轮：判据 (f) 的 store 分母虚高 12 —— 十二个支付网关被算成「店」

### ① 分类靠一份手写名单，而名单不完整

**`core_coverage.py` 分 store / vendor 两桶，判据是标签在不在 `VENDOR_HINTS` 里。
而那份名单是从**风控厂商**加**三个大支付**写的（cloudflare … adyen … purpledot）。**

> **名单之外**默认就是 store** —— 因为判据是「有没有被列进 vendor」。
> 于是十二个支付/身份/表单网关全被算成「店」：
> braintreegateway · sibspayments · vipps · midtrans · gpayments · mollie ·
> cybersource · bigcommerce · touchtechpayments · airwallex · klaviyo · ibm。**

### ② 补上之后

```
改前: store 27, vendor 12
改后: store 15, vendor 24
store hosts matched: 15    store hosts unmatched: 0
```

> **分母小了十二，分子一个没少 —— 覆盖率没变，**诚实度变了**。
> 判据 (f) 要的是「原版**站点**清单」，不是「**主机**清单」。**

### ③ 特意没动的一个

**`authenticate.riotgames.com` 留在 store 桶** —— 它是身份 host，但 registry 里**也有** `riotgames` store flow。
**移走会藏起那个配对，而不是修好一个标签。**

### ④ 而 METRICS 里两个 vendor 数字不是矛盾

| 工具 | 分母 | 值 |
|---|---|---|
| `core_coverage.py` vendor 桶 | 支付 + 风控 + 基础设施 host | **24** |
| `vendor_coverage.py`（METRICS 读） | 风险厂商 | **12** |

> **两个工具各自一致，而「vendor」不是同一个概念。
> 如果没查就当成矛盾去改，会把一个正确的工具改坏（R980 同一课）。**

### ⑤ 仍然敞着的

**vendor 段只搜 `Scripts/`，store 段搜整个 `src` —— 两段口径不同，输出没写。
所以 24 个里 20 个 `unmatched` 不能读出任何覆盖率结论。记 Unknown。**

### 数字

| 度量 | R987 | **R988** |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **judge (f) store 分母** | 27 | **15** |
| **store matched / unmatched** | 27 / 0 | **15 / 0** |
| **core_coverage vendor 桶** | 12 | **24** |

### 教训

> **默认规则的错永远朝一个方向犯：新东西被算进多数那一类，于是没人看得见。
> 十二个支付网关在「27 个店」里待了很多轮，而它们每一行都写着 `matched` ——
> 一个错的分母会让每一行都看起来是对的。**
"""

BACKLOG_ADD = """

## 判据 (f) — **store 分母 27 → 15：十二个支付/身份/表单网关被算成店**（R988）

### 缺陷

**`core_coverage.py` 用 `VENDOR_HINTS` 手写名单分桶，**名单之外默认 store**。
名单只有风控厂商 + paypal/stripe/adyen/paynamics，于是十二个支付网关落进 store 桶：**
braintreegateway · sibspayments · vipps · midtrans · gpayments · mollie · cybersource ·
bigcommerce · touchtechpayments · airwallex · klaviyo · ibm

### 修

**`VENDOR_HINTS` 补上十二个标签（`riotgames` 特意不补 —— 它既是身份 host，registry 里也有 store flow）。**

### 结果

```
改前: store 27, vendor 12      改后: store 15, vendor 24
store hosts matched: 15        store hosts unmatched: 0
```

**→ 覆盖率不变（0 unmatched），分母变诚实。**

### 而 METRICS 两个 vendor 数不是矛盾

| 工具 | 分母 | 值 |
|---|---|---|
| `core_coverage.py` vendor 桶 | 支付+风控+基础设施 | 24 |
| `vendor_coverage.py` | 风险厂商 | 12 |

### 数字

**套件 2205 · 陈旧度 0/0 · 函数数 173,952 · store 分母 15 / matched 15 / unmatched 0**

| 仍 Unknown | |
|---|---|
| vendor 段 20 个 unmatched 里多少是真未实现 | 段口径不同（vendor 只搜 `Scripts/`），分不开 |

**纪律**：默认规则的错只朝一个方向犯 —— 新东西被算进多数那类。
"""

BLOCKER = """

---

## 412. **store 分母 27 → 15：十二个支付/身份/表单网关被算成「店」**

> R988。**改 `VENDOR_HINTS` 一处。** 套件 **2205 通过 / 0 失败 / 0 跳过**。

### 一、缺陷成因

**`core_coverage.py` 分 store / vendor 两桶，判据是 host 标签在不在手写的 `VENDOR_HINTS` 里。
名单只有风控厂商（cloudflare / kasada / datadome / perimeterx / queue-it / recaptcha / hcaptcha /
akamai / aycd / turnstile）加大支付三家（paypal / stripe / adyen）、eshopworld / global-e /
vivapayments / wdprapps / disney / purpledotprice。**

**→ **名单之外默认就是 store**。于是十二个落进去了：**

```
api.braintreegateway.com      api.sibspayments.com       api.vipps.no
app.midtrans.com              degica.as1.gpayments.net   ecommerce-gateway.mollie.com
flex.cybersource.com          payments.bigcommerce.com   retry.touchtechpayments.com
threeds.airwallex.com         static-forms.klaviyo.com   www.ibm.com
```

### 二、改了什么

**`VENDOR_HINTS` 补十二个标签：`braintree` `sibspayments` `vipps` `midtrans` `gpayments`
`mollie` `cybersource` `bigcommerce` `touchtech` `airwallex` `klaviyo` `ibm`。**

**`riotgames` 特意**没有**补：`authenticate.riotgames.com` 是身份 host，
但 registry 里**也有**一个 `riotgames` store flow —— **移走会把这个配对藏起来，而不是修好一个标签。**

### 三、结果

```
改前: hosts with a path: 39  (store 27, vendor 12)
改后: hosts with a path: 39  (store 15, vendor 24)

store hosts matched:   15
store hosts unmatched:  0
```

**→ 覆盖率不变（0 unmatched），分母变诚实。
→ 判据 (f) 要的是「原版**站点**清单」，不是「**主机**清单」。**

### 四、而 METRICS 里两个 vendor 数字不是矛盾

| 工具 | 分母 | 值 |
|---|---|---|
| `core_coverage.py` 的 vendor 桶 | 支付 + 风控 + 平台基础设施 host | **24** |
| `vendor_coverage.py`（METRICS 项目读它） | **风险厂商**（cloudflare / kasada / …） | **12** |

**→ 两个工具各自一致，「vendor」不是同一个概念。
→ 若没查就当成矛盾去改，会把一个正确的工具改坏 —— R980 的同一课。**

### 五、数字

| 度量 | R987 | R988 |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **判据 (f) store 分母** | 27 | **15** |
| **store matched / unmatched** | 27 / 0 | **15 / 0** |
| **core_coverage vendor 桶** | 12 | **24** |

### 六、验证

```
cd replica
python tools/core_coverage.py          -> hosts with a path: 39 (store 15, vendor 24)
                                          store hosts matched: 15 / unmatched: 0
python tools/metrics_report.py         -> 核心覆盖：store 宿主 exit 0 {store hosts 15, matched 15, unmatched 0}
                                          完整套件 exit 0  2205 通过 / 0 失败 / 0 跳过
```

### 七、仍然 Unknown

- **vendor 段 20 个 unmatched 里多少是真未实现**：**Unknown** —— store 段搜整个 `src`，
  vendor 段只搜 `Scripts/`，两段口径不同，输出里没写这一点，所以那个数读不出覆盖率。

### 八、教训

**「名单之外的默认是 store」是一条**默认规则**，而默认规则的错永远朝一个方向犯：
新东西被算进多数那一类，于是没人看得见。**

**十二个支付网关在「27 个店」里待了很多轮，而它们每一个输出行都写着 `matched` ——
一个错的分母会让每一行都看起来是对的。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R988", BLOCKER)
    ensure(RSTATUS, "R988", BLOCKER)
    ensure(RVERDICT, "第 988 轮", VERDICT)
    ensure(BACKLOG, "R988", BACKLOG_ADD)

    note = (
        "\n## R988 补充 — **store 分母 27 → 15：十二个支付网关被算成「店」**（套件 2205）\n\n"
        "`core_coverage.py` 用 `VENDOR_HINTS` 手写名单分 store/vendor，**名单之外默认 store**。\n"
        "而名单只有风控厂商 + paypal/stripe/adyen/paynamics，于是十二个落进 store 桶：\n"
        "braintreegateway · sibspayments · vipps · midtrans · gpayments · mollie · cybersource ·\n"
        "bigcommerce · touchtechpayments · airwallex · klaviyo · ibm。\n\n"
        "补齐之后：**store 27 → 15，vendor 12 → 24，store matched 15 / unmatched 0**。\n"
        "→ 覆盖率不变，**分母变诚实**。判据 (f) 要的是「原版站点清单」，不是「主机清单」。\n\n"
        "`riotgames` 特意没补：`authenticate.riotgames.com` 是身份 host，但 registry 里**也有** riotgames store flow，\n"
        "移走会藏起那个配对。\n\n"
        "**METRICS 的两个 vendor 数不是矛盾**：`core_coverage` 的 vendor 桶（支付+风控+基础设施）= 24，\n"
        "`vendor_coverage.py` 的风险厂商 = 12。两个工具各自一致，「vendor」不是同一概念 —— 没查就当成矛盾改，会改坏它。\n\n"
        "数字：套件 2205 · 陈旧度 0/0 · 函数数 173,952 · store 分母 15 / matched 15 / unmatched 0。\n\n"
        "纪律：**默认规则的错只朝一个方向犯 —— 新东西被算进多数那类，于是没人看得见。**\n\n"
        "下一轮：给「store 桶里不许出现支付标签」加一条守卫；并核 vendor 段口径（只搜 `Scripts/`）那个 Unknown。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R988" not in h:
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
             for p, k in ((RBLOCK, "R988"), (RSTATUS, "R988"), (RVERDICT, "第 988 轮"), (BACKLOG, "R988")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R988: the store denominator was padded with twelve payment gateways\n\n"
         "R987 left a gap to explain, thirty-five flow types against twenty-seven store hosts. Looking at that turned up\n"
         " something more basic: the twenty-seven was wrong.\n\n"
         "core_coverage splits hosts into store and vendor by testing each label against a hand-written list. That list was\n"
         " built from the risk vendors plus PayPal, Stripe, Adyen and Paynamics, and a label that is not on it is a store by\n"
         " default. So twelve payment, identity and form hosts counted as shops: Braintree, SIBs, Vipps, Midtrans, GMO,\n"
         " Mollie, Cybersource, BigCommerce, Touchtech, Airwallex, Klaviyo and IBM.\n\n"
         "Adding those twelve labels moves the split to fifteen stores and twenty-four vendor hosts, with store coverage\n"
         " still fifteen matched and none unmatched. The numerator did not change and the denominator got honest, which is\n"
         " what criterion (f) needs: it asks for the original's store list, not its host list.\n\n"
         "riotgames is deliberately not added. authenticate.riotgames.com is an identity host, but the registry also carries a\n"
         " riotgames store flow, so moving the host would hide that pairing rather than correct a label.\n\n"
         "Two vendor numbers now disagree on the surface and do not: core_coverage's vendor bucket counts payment, risk and\n"
         " infrastructure hosts together and reads twenty-four, while vendor_coverage counts the risk vendors only and reads\n"
         " twelve. They are consistent, and treating them as a contradiction would have broken a correct tool -- the same\n"
         " lesson as the round that nearly repaired a guard whose only problem was an empty subject.\n\n"
         "What stays open is that the store section searches all of src while the vendor section searches Scripts only, so\n"
         " the twenty unmatched vendor rows cannot be read as a coverage figure. That is recorded as unknown rather than\n"
         " papered over.\n\n"
         "Figures: suite 2205 unchanged, freshness zero, count 173,952, store hosts fifteen matched with none unmatched.\n\n"
         "Unknown: how many of the twenty unmatched vendor hosts are genuinely unimplemented, which needs the two sections\n"
         " to search the same tree.\n\n"
         "The lesson is that a default rule errs in one direction only: whatever is new lands in the majority bucket, and the\n"
         " wrong denominator makes every row underneath it look right.\n\n"
         "One hints list extended; suite green at 2205."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()