"""Record R923: eShopWorld's two polling loops and the shared poller."""

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
### eShopWorld：五条路径里**两条是轮询端点**，所以它不是一次调用而是一次等待（R923）

**R922 说下一家 eShopWorld。它的五条路径排起来是这样的：**

```
payments-panel…/api/v2/PaymentMethods/url        面板在哪
payments-panel…/api/v2/PaymentMethods?paymentId= 某笔支付是什么
payments-panel…/api/v2/WebComponent/state        面板怎么样了   ← 轮询
retailer-shopifypayments-api…/api/v1/payment/apm/session/status           替代支付怎么样  ← 轮询
retailer-shopifypayments-api…/api/v1/payment/apm/session/post_pay_status  …以及刚付完之后
```

### 所以它是两个轮询循环，在**两台不同宿主**上

**面板自己的状态 与 替代支付的 session 是**两个独立循环**。
所以同时有这两条路可走的流程，**不能轮询了一个就假定另一个**。**

### 而为什么写**一个**轮询器而不是两个

**两个端点都回答「还没好 / 好了 / 坏了」，都需要截止时间、间隔、终止条件。**

> **写两遍会邀请两份拷贝对「什么叫好了」产生分歧 —— 而结账就是这样在一条路上成功、在另一条路上挂住。**

### 三个结果，而第三个是关键

| 结果 | 含义 |
|---|---|
| `Success()` | 出现成功词 |
| `Fail(...)` | 出现失败词 |
| **`Fail(retryable: true)` + `settled = "unknown"`** | **到截止时间还没定** |

> **第三个不是失败：一笔没在窗口内定下来的支付**可能还会定下来**。
> **把它叫失败会让一个慢的网关看起来像被拒的卡。****

### 而「不认识」的处理方向是**继续等**

**终端词是猜的（没有响应体证据），所以只有**列表里的词**才终止轮询，其他一律继续等到截止。**

> **因为猜错一个失败词会**放弃一笔即将成功的支付** —— 那比等完窗口更糟。**

### 一个认出规则上的细节

**只认 `state` / `status` / `paymentStatus` / `result` 这几个字段名里的词，不认正文任意位置。**
**所以 `{"note":"completed"}` **不**终止轮询，而 `{"status":"completed"}` 会。**

**那是刻意的窄：一个把「提到了 completed」当「完成了」的判据，会被日志字段骗。**

### 数字

| 度量 | R922 | **R923** |
|---|---|---|
| 套件 | 1868 | **1881** |
| **vendor 命名** | 7 / 12 | **9 / 12** |
| **vendor 缺失** | 5 | **3** |

**剩 3 个：Disney（2 台）· Viva（1 台）。**

### 教训

> **前两家 vendor（Purple Dot、Global-e）都是「发一个请求、读一个答案」。
> 这一家不是 —— 它是**一个带截止时间的等待**。**
> **而「等待」比「请求」多三件事：间隔、终止条件、以及**没定下来时说什么**。**
> **第三件最难，因为它既不是成功也不是失败，而大多数流程只有两格。**
"""

if "eShopWorld：五条路径里**两条是轮询端点**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R923 appended")

VERDICT = """

---

## 第 923 轮：eShopWorld —— 五条路径里两条是轮询，所以它是一次等待

### 两台宿主、两个循环

**`payments-panel…/WebComponent/state` 与 `retailer-shopifypayments-api…/apm/session/status` 是两个独立循环。
所以同时有这两条路的流程**不能轮询了一个就假定另一个**。**

### 为什么写**一个**轮询器

**两个端点都回答「还没好 / 好了 / 坏了」，都需要截止时间、间隔、终止条件。**

> **写两遍会邀请两份拷贝对「什么叫好了」产生分歧 —— 而结账就是这样在一条路上成功、在另一条路上挂住。**

### 三个结果，第三个是关键

| 结果 | |
|---|---|
| `Success()` | 出现成功词 |
| `Fail(...)` | 出现失败词 |
| **`Fail(retryable: true)` + `settled = "unknown"`** | **到截止时间还没定** |

> **第三个不是失败：没在窗口内定下来的支付**可能还会定下来**。
> 把它叫失败会让一个慢的网关看起来像被拒的卡。**

### 而「不认识」的方向是**继续等**

**终端词是猜的（无响应体），所以只有列表里的词才终止，其他等到截止。
因为猜错一个失败词会**放弃一笔即将成功的支付**。**

### 一个认出规则上的细节

**只认 `state`/`status`/`paymentStatus`/`result` 字段里的词。
所以 `{"note":"completed"}` **不**终止轮询，`{"status":"completed"}` 会。**

> **一个把「提到了 completed」当「完成了」的判据，会被日志字段骗。**

### 数字

| 度量 | R922 | **R923** |
|---|---|---|
| 套件 | 1868 | **1881** |
| vendor 命名 | 7 / 12 | **9 / 12** |
| vendor 缺失 | 5 | **3** |

**剩 3 个：Disney（2 台）· Viva（1 台）。**

### 教训

> **前两家 vendor 都是「发一个请求、读一个答案」。这一家是**一个带截止时间的等待**。**
> **而「等待」比「请求」多三件事：间隔、终止条件、以及**没定下来时说什么**。
> 第三件最难，因为它既不是成功也不是失败，而大多数流程只有两格。**
"""

BACKLOG_ADD = """

## 优先级 ① — eShopWorld 面板 + 两个轮询（R923，**改产品代码 +13 用例**）

### 五条路径，两台宿主

```
payments-panel…/api/v2/{PaymentMethods/url, PaymentMethods?paymentId=, WebComponent/state}
retailer-shopifypayments-api…/api/v1/payment/apm/session/{status, post_pay_status}
```

### `Payments/EshopWorldPanel.cs`

**两台宿主 · 五条路径 · `Loop` 枚举（WebComponent / Apmp）· `StateUrl` · `MethodsUrlFor` ·
**`PollAsync`（共享轮询器）** · `StateWord` · `TerminalStates` / `SuccessWords`**

### 三个结果（第三个是关键）

**成功 / 失败 / **`settled = "unknown"` + retryable** —— 没定下来不是失败：慢网关不该看起来像被拒的卡。**

### 两个刻意的窄

**① 不认识的词**继续等**（猜错失败词会放弃即将成功的支付）。
② 只认 `state`/`status`/`paymentStatus`/`result` 字段内的词 → `{"note":"completed"}` 不终止。**

### 数字

**套件 1868 → 1881 · vendor 命名 7/12 → **9/12** · 缺失 5 → **3**（Disney×2 · Viva×1）**

| 仍 Unknown | |
|---|---|
| 真实状态词 | 无响应体，14 个词是猜的 |
| `post_pay_status` 与 `status` 的区别 | 只有路径名 |
| 面板返回什么 | 无响应体 |

**纪律**：**「等待」比「请求」多三件事 —— 间隔、终止条件、以及没定下来时说什么。第三件最难，因为大多数流程只有两格。**
"""

BLOCKER = """

---

## 347. eShopWorld：vendor 9/12；两个轮询循环共用一个轮询器

> R923。**改产品代码 +13 用例。** 套件 **1881 通过 / 0 失败 / 0 跳过**。

### 一、五条路径排起来是两台宿主、两个循环

```
payments-panel…/api/v2/PaymentMethods/url        面板在哪
payments-panel…/api/v2/PaymentMethods?paymentId= 某笔支付是什么
payments-panel…/api/v2/WebComponent/state        面板状态   ← 轮询
retailer-shopifypayments-api…/payment/apm/session/status          替代支付  ← 轮询
retailer-shopifypayments-api…/payment/apm/session/post_pay_status 刚付完
```

**面板状态与 APM session 是两个独立循环 → 同时有这两条路的流程不能轮询一个就假定另一个。**

### 二、为什么一个轮询器

**两个端点都回答「还没好/好了/坏了」，都需要截止时间、间隔、终止条件。
写两遍会邀请两份拷贝对「什么叫好了」产生分歧 —— 结账就是这样在一条路上成功、另一条路上挂住。**

### 三、三个结果，第三个是关键

| 结果 | |
|---|---|
| `Success()` | 成功词 |
| `Fail(...)` | 失败词 |
| **`settled = "unknown"` + retryable** | **到截止还没定** |

**没定下来不是失败：慢网关不该看起来像被拒的卡。**

### 四、两个刻意的窄

1. **不认识的词继续等** —— 猜错一个失败词会放弃一笔即将成功的支付。
2. **只认 `state`/`status`/`paymentStatus`/`result` 字段内的词** —— `{"note":"completed"}` 不终止。

### 五、数字

| 度量 | R922 | R923 |
|---|---|---|
| 套件 | 1868 | **1881** |
| **vendor 命名** | 7 / 12 | **9 / 12** |
| **vendor 缺失** | 5 | **3** |

**剩 3 个：Disney（2 台）· Viva（1 台）。**

### 六、验证

```
vendor_coverage.py                -> 两台 eshopworld 宿主均 yes（EshopWorldPanel.cs）；9 named / 3 absent
test --filter EshopWorldPanelTests -> 13 通过
metrics_report.py                 -> 1881 通过 / 0 失败
```

### 七、仍然 Unknown

- **真实状态词**：**Unknown** —— 无响应体，14 个词是猜的。
- **`post_pay_status` 与 `status` 的区别**：**Unknown** —— 只有路径名。
- **面板返回什么**：**Unknown**。

### 八、教训

**前两家 vendor 都是「发一个请求、读一个答案」。这一家是**一个带截止时间的等待**。**

**「等待」比「请求」多三件事：间隔、终止条件、以及**没定下来时说什么**。**

**第三件最难，因为它既不是成功也不是失败，而大多数流程只有两格 ——
所以这一轮新加的那一格（`unknown`）比两条路径本身更值钱。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R923", BLOCKER)
    ensure(RSTATUS, "R923", BLOCKER)
    ensure(RVERDICT, "第 923 轮", VERDICT)
    ensure(BACKLOG, "R923", BACKLOG_ADD)

    note = (
        "\n## R923 补充 — eShopWorld：两个轮询循环共用一个轮询器（改产品代码 +13 用例，套件 1868→1881）\n\n"
        "五条路径两台宿主：payments-panel（PaymentMethods/url · PaymentMethods?paymentId= · WebComponent/state）· "
        "retailer-shopifypayments-api（apm/session/status · post_pay_status）。\n\n"
        "两个轮询循环（WebComponent state 与 APM session）在**两台不同宿主**上 → 不能轮询一个就假定另一个。"
        "共用一个轮询器，因为写两遍会让两份拷贝对「什么叫好了」产生分歧。\n\n"
        "三结果：成功 / 失败 / **settled = unknown + retryable**（到截止还没定，不是失败）。\n\n"
        "两个刻意的窄：不认识的词继续等（猜错失败词会放弃即将成功的支付）· 只认 state/status/paymentStatus/result 字段内的词。\n\n"
        "数字：套件 1881 · vendor 命名 7/12 → 9/12 · 缺失 5 → 3（Disney×2 · Viva×1）。\n\n"
        "纪律：「等待」比「请求」多三件事 —— 间隔、终止条件、没定下来时说什么。第三件最难。\n\n"
        "下一轮：Disney（2 台，含 card/token + checkout + v3/process）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R923" not in h:
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
             for p, k in ((RBLOCK, "R923"), (RSTATUS, "R923"), (RVERDICT, "第 923 轮"), (BACKLOG, "R923")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R923: eShopWorld's two polling loops, and a third outcome most flows lack\n\n"
         "eShopWorld's five paths arrange into two hosts and two loops: the hosted panel's own state on one, and an\n"
         " alternative payment's session on the other. Two of the five are state endpoints, so this vendor is not a call\n"
         " but a wait -- and a flow that has both paths must not poll one and assume the other.\n\n"
         "The poller is written once for both loops. Both endpoints answer not-yet, done or failed, and both need a\n"
         " deadline, an interval and a terminal condition; two copies would invite a disagreement about what counts as\n"
         " done, which is how a checkout completes on one path and hangs on the other.\n\n"
         "The third outcome is the point. A poll that reaches its deadline without a terminal word reports unknown and\n"
         " stays retryable, because an unsettled payment may still settle and calling it failed would make a slow gateway\n"
         " look like a declined card. Most flows have two outcomes, and that missing third is where a wait differs from a\n"
         " request.\n\n"
         "Two narrowings are deliberate. A word outside the terminal list keeps waiting rather than failing, since a wrong\n"
         " guess at a failure word would abandon a payment about to succeed -- so an unknown answer waits out the clock.\n"
         " And recognition is limited to the state, status, paymentStatus and result fields, so {\"note\":\"completed\"}\n"
         " does not end a poll while {\"status\":\"completed\"} does; a criterion that treated any mention as completion\n"
         " would be fooled by a log field.\n\n"
         "Figures: suite 1868 to 1881, vendors named seven of twelve to nine, vendors absent five to three. Disney on two\n"
         " hosts and Viva on one remain.\n\n"
         "Unknown: the real state words, since no response body survives and all fourteen are guesses; how post_pay_status\n"
         " differs from status, of which only the path names survive; and what the panel returns.\n\n"
         "The lesson is about the shape of a wait. It needs an interval, a terminal condition, and an answer for what to\n"
         " say when neither terminal is reached -- and that third thing is the one most flows have no room for, which is\n"
         " why adding it was worth more than the two paths that prompted it.\n\n"
         "Product code changed; suite green at 1881."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()