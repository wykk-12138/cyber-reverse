"""Record R989: one denominator for both columns, and the vendor column becomes readable."""

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
### 两列换成同一个分母后，vendor 的未覆盖从 **20** 降到 **6**，而 6 个全是支付网关（R989）

**R988 留了一个 Unknown：vendor 段只搜 `Scripts/`，store 段搜整个 `src`，所以 24 个里 20 个 `unmatched`
读不出任何覆盖率结论。这一轮把两段的分母统一，那个数变成可读的。**

### ① 缺陷：两列用两个分母

**`registry_ids()` 已经返回 `all_src`（整个 `src` 的文本），而 vendor 段另有一个 `scripts_text()`，只读 `Scripts/*.cs`。**

> **于是判据 (f) 那两列是**在不同分母下**量出来的：
> store 那列「源码里有没有这个名字」，vendor 那列「Scripts 目录里有没有这个名字」。
> 而 `kasada` / `datadome` / `perimeterx` 的实现本来就不全在 `Scripts/`。**

### ② 改法：共用 `all_src`

```python
# 改前
scr = scripts_text().lower()
# 改后
scr = all_src.lower()
```

### ③ 结果

```
vendor 24 个 host：matched 18 · unmatched 6
```

**而 6 个 unmatched 是：**

| host | 标签 |
|---|---|
| `app.midtrans.com` | midtrans |
| `degica.as1.gpayments.net` | gpayments |
| `ecommerce-gateway.mollie.com` | mollie |
| `flex.cybersource.com` | cybersource |
| `retry.touchtechpayments.com` | touchtech |
| `threeds.airwallex.com` | airwallex |

> **六个**全都是支付网关**，一个风控厂商都没有。**
> **→ 优先级 ②（风控对抗）的 vendor 覆盖是**完整的**：
> cloudflare · kasada · datadome · perimeterx · queue-it · aycd · turnstile/captcha · eshopworld ·
> wdprapps · disney · global-e · vivapayments · paypal · adyen · klaviyo · braintree · sibs · vipps —— 全 matched。**
> **→ 而那 6 个属于**下单链路**（优先级 ①），不是风控。**

**这是判据 (f) 第一次给出**可分类**的「未覆盖」：6 条，每一条都写着它是哪一类。**

### ④ 而统一分母顺手暴露一个假匹配

**改完后 `registerdisney.go.com` 匹配在标签 `go` 上 —— 而 `go` 出现在源码里几乎所有地方。**

**成因：分桶用**整串 host**（含 `disney` → 进 vendor 桶），匹配用**注册标签**（`go.com` 的标签是 `go`）。
两个步骤对「哪个 token 是这个 host 的名字」看法不同。**

**修：被 vendor 提示词打了桶的 host，用**那个提示词**当它的标识。改完 `registerdisney.go.com` 经 `disney` 匹配。**

> **而这条正是 R988 的 docstring 早就写着的风险：「a short label can match by accident」。
> 它真的发生了一次，而它发生的条件是**分桶与匹配用不同的 token** —— 那句话没说到这一层。**

### ⑤ 仍然诚实的部分

**`matched` 现在两列同义：「这个名字在源码里出现过」。
它不是「这个站能用」也不是「这个厂商接上了」—— 输出末尾的 NOTE 一直这么写着。**

### 数字

| 度量 | R988 | **R989** |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| store matched / unmatched | 15 / 0 | **15 / 0** |
| **vendor unmatched（统一分母后）** | 20（口径不同，不可读） | **6（全是支付网关）** |
| **假匹配** | 1（`go`） | **0** |

### 教训

> **「两列数字放在一张表里」不等于「两列在回答同一个问题」。
> 而一个口径不同的分母，会让一列看起来只是「覆盖得差」，而不是「量错了」。**
"""

if "两列换成同一个分母后" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 989 轮：两列同一个分母后，vendor 未覆盖从 20 降到 6，全是支付网关

### ① 缺陷：两列用两个分母

**`registry_ids()` 已返回 `all_src`（整个 `src`），而 vendor 段另有 `scripts_text()` 只读 `Scripts/*.cs`。**

> **判据 (f) 的两列因此在不同分母下量出来：store 问「源码里有没有」，vendor 问「Scripts 里有没有」。
> 而 kasada / datadome / perimeterx 的实现本来就不全在 `Scripts/`。**

### ② 改法：`scr = all_src.lower()`

### ③ 结果：vendor 24 → matched 18 / unmatched 6

| host | 标签 |
|---|---|
| `app.midtrans.com` | midtrans |
| `degica.as1.gpayments.net` | gpayments |
| `ecommerce-gateway.mollie.com` | mollie |
| `flex.cybersource.com` | cybersource |
| `retry.touchtechpayments.com` | touchtech |
| `threeds.airwallex.com` | airwallex |

> **六个全是支付网关，一个风控厂商都没有。
> → 优先级 ②（风控）的 vendor 覆盖**完整**：cloudflare · kasada · datadome · perimeterx · queue-it ·
> aycd · captcha · eshopworld · wdprapps · disney · global-e · vivapayments · paypal · adyen · klaviyo ·
> braintree · sibs · vipps 全 matched。
> → 那 6 个属于**下单链路**（优先级 ①）。**
> **这是判据 (f) 第一次给出**可分类**的「未覆盖」：6 条，每条都写着它属于哪一类。**

### ④ 统一分母顺手暴露一个假匹配

**`registerdisney.go.com` 匹配在标签 `go` 上 —— 而 `go` 几乎出现在源码各处。**

**成因：分桶用整串 host（含 `disney`），匹配用注册标签（`go.com` → `go`）。
两步对「哪个 token 是名字」看法不同。**

**修：被 vendor 提示词打桶的 host 用**那个提示词**当标识 → 现在经 `disney` 匹配，假匹配 0。**

> **这正是 R988 docstring 写的风险「a short label can match by accident」——
> 它真的发生了一次，而条件是**分桶与匹配用不同 token**，那句话没说到这一层。**

### ⑤ 仍然诚实的部分

**`matched` 两列同义：「这个名字在源码里出现过」。不是「这个站能用」。
输出末尾的 NOTE 一直这么写着。**

### 数字

| 度量 | R988 | **R989** |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| store matched / unmatched | 15 / 0 | **15 / 0** |
| **vendor unmatched** | 20（口径不同，不可读） | **6（全是支付网关）** |
| **假匹配** | 1（`go`） | **0** |

### 教训

> **「两列数字放在一张表里」不等于「两列在回答同一个问题」。
> 而一个口径不同的分母，会让一列看起来只是「覆盖得差」，而不是「量错了」。**
"""

BACKLOG_ADD = """

## 判据 (f) — **两列统一分母：vendor 未覆盖 20 → 6，全是支付网关；假匹配 1 → 0**（R989）

### 缺陷

**`registry_ids()` 已返回 `all_src`，而 vendor 段另有 `scripts_text()` 只读 `Scripts/*.cs`
→ 判据 (f) 两列在**不同分母**下量出来。**

### 修

**`scr = all_src.lower()`（共用同一份文本）。**

### 结果

```
vendor 24：matched 18 · unmatched 6
```

| 未覆盖 6 个 | 类别 |
|---|---|
| midtrans · gpayments · mollie · cybersource · touchtech · airwallex | **支付网关（优先级 ①）** |

**→ 风控厂商（优先级 ②）**全部 matched**：cloudflare · kasada · datadome · perimeterx · queue-it ·
aycd · captcha · eshopworld · wdprapps · disney · global-e · vivapayments · paypal · adyen · klaviyo ·
braintree · sibs · vipps。**

### 顺手修的假匹配

**`registerdisney.go.com` 匹配在标签 `go` 上（`go.com` 的注册标签）。
成因：分桶用整串 host、匹配用注册标签。改成「被 vendor 提示词打桶的 host 用那个提示词当标识」→ 经 `disney` 匹配。**

### 数字

**套件 2205（未动测试）· 陈旧度 0/0 · 函数数 173,952 · store 15/0 · vendor unmatched 6 · 假匹配 0**

| 仍 Unknown | |
|---|---|
| 那 6 个支付网关在复刻件里是否真缺 | `matched` 只说名字出现过，不说实现 |

**纪律**：两列放一张表 ≠ 两列在回答同一个问题。
"""

BLOCKER = """

---

## 413. **两列统一分母：vendor 未覆盖 20 → 6（全是支付网关）；假匹配 1 → 0**

> R989。**改 `core_coverage.py` 两处。** 套件 **2205 通过 / 0 失败 / 0 跳过**。

### 一、缺陷：判据 (f) 的两列用两个分母

**`registry_ids()` 已经返回 `all_src`（整个 `src` 的文本），
而 vendor 段另有一个 `scripts_text()`，只读 `Scripts/*.cs`。**

**→ store 那列问「源码里有没有这个名字」，vendor 那列问「Scripts 目录里有没有」。
→ 而 `kasada` / `datadome` / `perimeterx` 的实现本来就不全在 `Scripts/`。**

```python
# 改前
scr = scripts_text().lower()
# 改后
scr = all_src.lower()
```

### 二、结果

```
vendor 24 个 host：matched 18 · unmatched 6
```

| 未覆盖的 6 个 | 标签 | 类别 |
|---|---|---|
| `app.midtrans.com` | midtrans | 支付网关 |
| `degica.as1.gpayments.net` | gpayments | 支付网关 |
| `ecommerce-gateway.mollie.com` | mollie | 支付网关 |
| `flex.cybersource.com` | cybersource | 支付网关 |
| `retry.touchtechpayments.com` | touchtech | 支付网关 |
| `threeds.airwallex.com` | airwallex | 支付网关 |

**→ 六个**全是支付网关**，一个风控厂商都没有。
→ 优先级 ②（风控对抗）的 vendor 覆盖是**完整的**：
cloudflare · kasada · datadome · perimeterx · queue-it · aycd · captcha · eshopworld · wdprapps ·
disney · global-e · vivapayments · paypal · adyen · klaviyo · braintree · sibs · vipps —— 全 matched。
→ 那 6 个属于**下单链路**（优先级 ①），不是风控。**

**→ 这是判据 (f) 第一次给出**可分类**的「未覆盖」：6 条，每条都写着它属于哪一类。**

### 三、统一分母顺手暴露一个假匹配

**改完后 `registerdisney.go.com` 匹配在标签 `go` 上 —— 而 `go` 几乎出现在源码各处。**

**成因：分桶用**整串 host**（含 `disney` → 进 vendor 桶），
匹配用**注册标签**（`go.com` 的注册标签是 `go`）。**两步对「哪个 token 是名字」看法不同。**

**修：被 vendor 提示词打了桶的 host，用**那个提示词**当标识。**

```python
hint = next((v for v in VENDOR_HINTS if v in low), None)
(vendors if hint else stores).append((host, count, hint or label(host)))
```

**→ `registerdisney.go.com` 现在经 `disney` 匹配，假匹配 0。**

**→ 这正是 R988 docstring 写的风险「a short label can match by accident」。
它真的发生了一次，而条件是**分桶与匹配用不同 token** —— 那句话没说到这一层。**

### 四、仍然诚实的部分

**`matched` 现在两列同义：「这个名字在源码里出现过」。
不是「这个站能用」，也不是「这个厂商接上了」—— 输出末尾的 NOTE 一直这么写着。**

### 五、数字

| 度量 | R988 | R989 |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| store matched / unmatched | 15 / 0 | **15 / 0** |
| **vendor unmatched** | 20（口径不同，不可读） | **6（全是支付网关）** |
| **假匹配** | 1（`go`） | **0** |

### 六、验证

```
cd replica
python tools/core_coverage.py
  -> hosts with a path: 39 (store 15, vendor 24)
     store hosts matched: 15 / unmatched: 0
     vendor 段：matched 18 / unmatched 6（midtrans gpayments mollie cybersource touchtech airwallex）
     registerdisney.go.com -> matched … disney
python tools/metrics_report.py
  -> 核心覆盖：store 宿主 exit 0 {store hosts 15, matched 15, unmatched 0}
     完整套件 exit 0  2205 通过 / 0 失败 / 0 跳过
```

### 七、仍然 Unknown

- **那 6 个支付网关在复刻件里是否真缺**：**Unknown** —— `matched` 只说名字出现过，不说实现。

### 八、教训

**「两列数字放在一张表里」不等于「两列在回答同一个问题」。**

**而一个口径不同的分母，会让一列看起来只是「覆盖得差」，而不是「量错了」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R989", BLOCKER)
    ensure(RSTATUS, "R989", BLOCKER)
    ensure(RVERDICT, "第 989 轮", VERDICT)
    ensure(BACKLOG, "R989", BACKLOG_ADD)

    note = (
        "\n## R989 补充 — **两列统一分母：vendor 未覆盖 20 → 6（全是支付网关）；假匹配 1 → 0**（套件 2205）\n\n"
        "R988 留的 Unknown 解决了：vendor 段原用 `scripts_text()`（只读 `Scripts/`），而 store 段用整个 `src`。\n"
        "改成共用 `all_src` 之后，**vendor 24 → matched 18 / unmatched 6**：\n"
        "midtrans · gpayments · mollie · cybersource · touchtech · airwallex —— **六个全是支付网关，无一是风控厂商**。\n\n"
        "→ 优先级 ②（风控）vendor 覆盖**完整**：cloudflare · kasada · datadome · perimeterx · queue-it · aycd ·\n"
        "captcha · eshopworld · wdprapps · disney · global-e · vivapayments · paypal · adyen · klaviyo ·\n"
        "braintree · sibs · vipps 全 matched。那 6 个属于**下单链路**（优先级 ①）。\n\n"
        "**顺手修一个假匹配**：`registerdisney.go.com` 匹配在标签 `go` 上。\n"
        "成因：分桶用整串 host（含 `disney`）、匹配用注册标签（`go.com` → `go`）。\n"
        "改成「被 vendor 提示词打桶的 host 用那个提示词当标识」→ 经 `disney` 匹配，假匹配 0。\n\n"
        "数字：套件 2205（未动测试）· 陈旧度 0/0 · 函数数 173,952 · store 15/0 · vendor unmatched 6 · 假匹配 0。\n\n"
        "纪律：**两列放一张表 ≠ 两列在回答同一个问题。**\n\n"
        "下一轮：核那 6 个支付网关在复刻件里是否真缺（`matched` 只说名字出现过，不说实现）；或给 store 桶加防支付标签的守卫。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R989" not in h:
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
             for p, k in ((RBLOCK, "R989"), (RSTATUS, "R989"), (RVERDICT, "第 989 轮"), (BACKLOG, "R989")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R989: one denominator for both coverage columns, and the vendor column becomes readable\n\n"
         "R988 left the vendor section unreadable: twenty of twenty-four hosts unmatched. The cause was that the two\n"
         " columns of criterion (f)'s table were measured against different denominators. registry_ids already returns the\n"
         " text of all of src, but the vendor section called a separate scripts_text that walked only Scripts/, so a vendor\n"
         " whose implementation lives elsewhere could never match.\n\n"
         "Pointing both at the same text gives eighteen matched and six unmatched, and all six are payment gateways:\n"
         "Midtrans, GMO, Mollie, Cybersource, Touchtech and Airwallex. Not one risk vendor is among them. So the anti-bot\n"
         " column of priority two is complete -- Cloudflare, Kasada, DataDome, PerimeterX, Queue-it, AYCD, captcha handling,\n"
         " eShopWorld, wdprapps, Disney, Global-e, Viva, PayPal, Adyen, Klaviyo, Braintree, SIBs and Vipps all match -- and\n"
         " the six that do not belong to the checkout chain rather than to risk control. That is the first time criterion\n"
         "(f) has produced an uncovered list one can act on, because each of the six now carries its category.\n\n"
         "Unifying the denominator also exposed a false match. registerdisney.go.com was reporting as covered against the\n"
         " label go, which is the registrable label of go.com and appears throughout the source. The bucketing had used the\n"
         " whole host, where the vendor hint disney appears, while the match used the registrable label, so the two steps\n"
         " disagreed about which token names the host. A host put in the vendor bucket by a hint now carries that hint as its\n"
         " identity, and the false match is gone. The risk was written in R988's own docstring; what it did not say is that\n"
         " it fires when bucketing and matching use different tokens.\n\n"
         "What matched still means is unchanged and is stated in the output: the name appears somewhere in the source. Not\n"
         " that the store works, not that the vendor is wired.\n\n"
         "Figures: suite 2205 unchanged, freshness zero, count 173,952, store fifteen matched with none unmatched, vendor six\n"
         " unmatched against twenty before, false matches one to zero.\n\n"
         "Unknown: whether those six payment gateways are genuinely absent from the replica, since matched only speaks about\n"
         " names appearing.\n\n"
         "The lesson is that putting two numbers in one table does not make them answer the same question, and a mismatched\n"
         " denominator makes a column look badly covered rather than mismeasured.\n\n"
         "Two corrections in one tool; suite green at 2205."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()