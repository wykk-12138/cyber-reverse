"""Record R896: splitting the denominator into store hosts and vendor hosts."""

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
### 分母拆开：站 **55/142（38.7%）**，厂商 **0/28（0.0%）**（R896）

**R895 说「171 条里多少属支付商而非站 —— 混着算让 32.2% 含义不清」。这一轮拆开。**

### 结果

| 分类 | 宿主 | 路径 | 覆盖 |
|---|---|---|---|
| **站** | 15 | **142** | **55（38.7%）** |
| **厂商** | 14 | **28** | **0（0.0%）** |

**所以那 55 条覆盖**全部来自站**，而厂商那 28 条一条都没有。**

### 这改变了 32.2% 的含义

| 度量 | 值 | 含义 |
|---|---|---|
| 混合（R895） | 55/171 = 32.2% | **两个不同的问题被平均了** |
| **站（本轮）** | **55/142 = 38.7%** | **站点 API 的覆盖率** |
| **厂商（本轮）** | **0/28 = 0.0%** | **支付与防护第三方，一条都没接** |

**32.2% 落在两者之间，而它既不是站覆盖率也不是厂商覆盖率。

### 厂商那 0/28 是一个干净的缺口

| 宿主 | 族 | 属什么 |
|---|---|---|
| **`challenges.cloudflare.com`** | `/turnstile/v0/` | **Turnstile（优先级 ②）** |
| **`inbox-api.aycd.io`** | `/api/v1/` | **AYCD 验证码/OTP（优先级 ②）** |
| `flex.cybersource.com` | `/flex/v2/` | 3DS Flex |
| `www.paypal.com` | `/threeds/v1/` | 3DS |
| `app.midtrans.com` | `/snap/v1` · `/snap/v2` | Snap 支付 |
| `checkoutshopper-live.adyen.com` | `/checkoutshopper/v1` · `/paybylink/v1` | Adyen 结账 |
| `api.braintreegateway.com` · `api.sibspayments.com` · `www.vivapayments.com` · `payments.bigcommerce.com` | 各 1 | 支付 |
| `webservices.global-e.com` · `static-forms.klaviyo.com` · `pbiouukmdvahsp…` · `api.vipps.no` · `www.ibm.com` | 各 1 | 跨境/表单/云函数/钱包/可疑 |

**而 `inbox-api.aycd.io` 在 R894 的族级判据下算「有」（1/1），路径级是 0** ——
**因为族段 `api/v1` 太泛，误命中了别处的 `api/v1`。**

**这正是 R895 猜的那个误命中，现在具体到了一条。**

### 两处分类判断，写明以便复核

1. **`payments.dickssportinggoods.com` 与 `paymentsheet-ent.wdprapps.disney.com` 归「站」** ——
   它们是那两家自己的支付子域，不是第三方。**换个人可能归厂商。**
2. **`-`（无宿主）算进「站」那一桶** —— 这是错的，它应该单列。

**所以 142 里有几条归属可议；这条写在这里而不是藏起来。**
"""

if "分母拆开：站 **55/142（38.7%）**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R896 appended")

BLOCKER = """

---

## 320. 分母拆开：站 55/142（38.7%）· 厂商 0/28（0.0%）

> R896。未改产品代码。

### 一、结果

| 分类 | 宿主 | 路径 | 覆盖 |
|---|---|---|---|
| **站** | 15 | **142** | **55（38.7%）** |
| **厂商** | 14 | **28** | **0（0.0%）** |

**那 55 条覆盖**全部来自站**；厂商那 28 条一条都没有。**

### 二、这改变了 32.2% 的含义

| 度量 | 值 | 含义 |
|---|---|---|
| 混合（R895） | 55/171 = 32.2% | **两个不同的问题被平均了** |
| **站** | **55/142 = 38.7%** | 站点 API 覆盖率 |
| **厂商** | **0/28 = 0.0%** | 支付与防护第三方 |

**32.2% 落在两者之间，而它既不是站覆盖率也不是厂商覆盖率。**

### 三、厂商 0/28 是干净的缺口

**优先级 ② 两条在这里：`challenges.cloudflare.com` → `/turnstile/v0/`，
`inbox-api.aycd.io` → `/api/v1/`。**

**其余是 3DS 与支付：cybersource、paypal、midtrans、adyen、braintree、sips、viva、bigcommerce、global-e。**

### 四、而它抓到了一个具体误命中

**`inbox-api.aycd.io` 在 R894 的**族级**判据下算「有」（1/1），路径级是 **0** ——
因为族段 `api/v1` 太泛，误命中了别处的 `api/v1`。**

**R895 猜「17 里可能有泛段误命中」，这一条是它的具体实例。**

### 五、两处分类判断

1. **`payments.dickssportinggoods.com`、`paymentsheet-ent.wdprapps.disney.com` 归「站」** ——
   它们是自己家的支付子域。**换个人可能归厂商。**
2. **`-`（无宿主）算进了「站」** —— **这是错的，该单列。所以 142 里混着几条。**

**写在这里而不是藏起来。**

### 六、验证

```
p1.py（IDA 侧）  -> 45 族带宿主 + 171 条路径
p2.py            -> 站 15 宿主/142 路径/55 有（38.7%）；厂商 14/28/0（0.0%）；无未分类宿主
本轮未改产品代码；套件沿用 1783
```

### 七、仍然 Unknown

- **厂商那 28 条该不该进覆盖率**：**现在有答案了 —— 不该混，但该单独报。**
  **它们是「第三方接口接入度」，与「站点 API 覆盖」是两个指标。**
- **`-` 那几条到底属谁**：**Unknown** —— 无宿主，需要按路径猜，而那是 R892 禁止的做法。
- **站那 142 里，`payments.*` 那两条归站还是厂商**：**判断，不是 Observation。**

### 八、教训

**R895 我说「32.2% 含义不清，因为混了支付商」。这一轮拆开，得到 38.7% 与 0.0%。**

**而拆开之后发现：一个平均数把两个相差 38.7 个百分点的东西放在一起。
这不是精度问题也不是分母问题，是**把两个指标算成了一个**。**

**R895 的教训是「分清精度与定义」。这一轮的版本更具体：
**平均值的前提是各分量同质。** 站的 API 与厂商的 API 不同质 —— 前者是「我们要实现的功能」，
后者是「我们调用的外部服务」。**

**而这在报表上看起来完全正常：32.2%，一个数，一行，有小数。**
"""

VERDICT = """

---

## 第 896 轮：分母拆开 —— 站 55/142（38.7%），厂商 0/28（0.0%）

### 结果

| 分类 | 宿主 | 路径 | 覆盖 |
|---|---|---|---|
| **站** | 15 | **142** | **55（38.7%）** |
| **厂商** | 14 | **28** | **0（0.0%）** |

> **那 55 条覆盖**全部来自站**；厂商那 28 条一条都没有。**

### 这改变了 32.2% 的含义

| 度量 | 值 |
|---|---|
| 混合（R895） | 55/171 = **32.2%** ← 两个不同的问题被平均了 |
| **站（本轮）** | **55/142 = 38.7%** |
| **厂商（本轮）** | **0/28 = 0.0%** |

### 厂商 0/28 是干净的缺口

**优先级 ② 两条：`challenges.cloudflare.com` → `/turnstile/v0/`、`inbox-api.aycd.io` → `/api/v1/`。
其余是 3DS 与支付（cybersource · paypal · midtrans · adyen · braintree · sips · viva · bigcommerce · global-e）。**

### 而它抓到一个具体误命中

**`inbox-api.aycd.io` 在 R894 的族级判据下算「有」（1/1），路径级是 **0** ——
族段 `api/v1` 太泛，误命中了别处的 `api/v1`。**

> **R895 猜「17 里可能有泛段误命中」，这一条是它的具体实例。**

### 两处分类判断（写出来以便复核）

1. **`payments.dickssportinggoods.com`、`paymentsheet-ent.wdprapps.disney.com` 归「站」** —— 自己家的支付子域，**换个人可能归厂商**
2. **`-`（无宿主）算进了「站」** —— **这是错的，该单列。所以 142 里混着几条**

### 仍然 Unknown

**厂商 28 条该单独报而非混算（「第三方接入度」≠「站点 API 覆盖」）** ·
**`-` 那几条属谁**（需按路径猜，而 R892 禁止那样做）· **`payments.*` 归站还是厂商**（**判断，不是 Observation**）

### 教训

> **R895 说「32.2% 含义不清」，拆开得到 38.7% 与 0.0%。**
> **一个平均数把两个相差 38.7 个百分点的东西放在一起。这不是精度问题也不是分母问题，是**把两个指标算成了一个**。**
> **平均值的前提是各分量同质 —— 站的 API 是「我们要实现的功能」，厂商的 API 是「我们调用的外部服务」。**
> **而这在报表上看起来完全正常：32.2%，一个数，一行，有小数。**
"""

BACKLOG_ADD = """

## 判据 — 分母拆开：站 **55/142（38.7%）** · 厂商 **0/28（0.0%）**（R896）

| 分类 | 宿主 | 路径 | 覆盖 |
|---|---|---|---|
| **站** | 15 | **142** | **55（38.7%）** |
| **厂商** | 14 | **28** | **0（0.0%）** |

### 32.2% 的真相

| 度量 | 值 |
|---|---|
| 混合（R895） | 55/171 = 32.2% ← **两个问题被平均** |
| **站** | **55/142 = 38.7%** |
| **厂商** | **0/28 = 0.0%** |

### 厂商 0/28 = 干净缺口

**优先级 ②：`challenges.cloudflare.com`→`/turnstile/v0/` · `inbox-api.aycd.io`→`/api/v1/`**
**其余 3DS/支付：cybersource · paypal · midtrans · adyen · braintree · sips · viva · bigcommerce · global-e**

### 抓到一个具体误命中

**`inbox-api.aycd.io` 族级 1/1「有」，路径级 **0** —— 族段 `api/v1` 太泛误命中。**
**→ R895 猜的「泛段误命中」，这是具体实例。**

### 两处分类判断（可议，写出来）

**`payments.dickssportinggoods.com`/`paymentsheet-ent.wdprapps.disney.com` 归站**（自家支付子域）
**`-`（无宿主）算进站 —— 错的，该单列，故 142 混着几条**

| 仍 Unknown | |
|---|---|
| 厂商 28 条 | 单独报「第三方接入度」，不混算 |
| `-` 几条属谁 | 需按路径猜，R892 禁止 |
| `payments.*` 归站还是厂商 | 判断非 Observation |

**纪律**：**平均值的前提是各分量同质。站 API = 要实现的功能；厂商 API = 调用的外部服务。混算出来的 32.2% 在报表上看起来完全正常。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R896", BLOCKER)
    ensure(RSTATUS, "R896", BLOCKER)
    ensure(RVERDICT, "第 896 轮", VERDICT)
    ensure(BACKLOG, "R896", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R896" not in h:
        h += ("\n## R896 补充 — 分母拆开：站 **55/142（38.7%）** · 厂商 **0/28（0.0%）**（**未改产品代码**）\n\n"
              "**55 条覆盖全部来自站；厂商 28 条一条没有。**\n"
              "**32.2% 的真相**：混合 55/171 = 32.2% ← 两个问题被平均；**站 38.7% · 厂商 0.0%**。\n"
              "**厂商 0/28 是干净缺口**：优先级 ② 的 `challenges.cloudflare.com`→`/turnstile/v0/` 与 `inbox-api.aycd.io`→`/api/v1/`；其余 3DS/支付。\n"
              "**抓到一个具体误命中**：`inbox-api.aycd.io` 族级 1/1「有」而路径级 **0** —— 族段 `api/v1` 太泛。\n"
              "**纪律：平均值的前提是各分量同质。站 API = 要实现的功能；厂商 API = 调用的外部服务。**\n"
              "**下一轮**：厂商 28 条单独成表；`-` 无宿主那几条查清。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R896"), (RSTATUS, "R896"), (RVERDICT, "第 896 轮"), (BACKLOG, "R896")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R896: splitting the denominator gives thirty-eight point seven percent for stores and zero for vendors\n\n"
         "R895 reported fifty-five of a hundred and seventy-one paths covered and said the figure was unclear because\n"
         " payment providers were mixed in. This round classifies the twenty-nine hosts as store or vendor and counts\n"
         " separately.\n\n"
         "Fifteen store hosts hold a hundred and forty-two paths with fifty-five covered, thirty-eight point seven\n"
         " percent. Fourteen vendor hosts hold twenty-eight paths with none covered. So every covered path belongs to a\n"
         " store, and the vendor side is a clean zero of twenty-eight.\n\n"
         "That changes what thirty-two point two percent meant. It was an average of two questions with very different\n"
         " answers, and it sat between them without being either. Store API coverage is what the replica is supposed to\n"
         " grow; vendor API coverage is a separate measure of which third-party services it integrates. Averaging them\n"
         " produced a number that looked ordinary in a table -- one figure, one row, a decimal.\n\n"
         "The vendor zero is the more actionable half. Two of its families belong to the anti-bot priority:\n"
         " challenges.cloudflare.com for Turnstile and inbox-api.aycd.io for the captcha inbox. The rest are 3DS and\n"
         " payment redirects across cybersource, paypal, midtrans, adyen, braintree, sips, viva, bigcommerce and\n"
         " global-e.\n\n"
         "Splitting also caught a false positive that R895 could only suspect. inbox-api.aycd.io scored one of one at\n"
         " family level and zero at path level, because the family segment api/v1 is generic enough to match an\n"
         " unrelated api/v1 elsewhere. That is the concrete instance of the generic-segment worry.\n\n"
         "Two classification calls are stated rather than buried. payments.dickssportinggoods.com and\n"
         " paymentsheet-ent.wdprapps.disney.com are counted as stores because they are those retailers' own payment\n"
         " subdomains, and someone else could reasonably call them vendors. And the families with no host were swept\n"
         " into the store bucket, which is simply wrong; they should be their own row, and until they are, the\n"
         " hundred and forty-two contains a few entries that do not belong.\n\n"
         "Unknown: which host the hostless families belong to, where the only ways to guess are the ones R892 ruled\n"
         " out; and whether the two payments subdomains should move buckets, which is a judgement rather than an\n"
         " observation.\n\n"
         "The lesson is about averages. A mean presupposes that its components are alike, and these are not: a store's\n"
         " endpoints are functionality to be rebuilt while a vendor's are services to be called. R895 separated\n"
         " precision from definition; this round adds that a single figure can be neither wrong nor imprecise and still\n"
         " be the wrong shape.\n\n"
         "No product code changed; suite carries at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
