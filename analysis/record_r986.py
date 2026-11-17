"""Record R986: per-flow work measured, one classifier bug caught, and only one store's order chain is broken."""

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
### 优先级 ① 有了每站的数：185 个覆写里 180 做实事，**只有 Bstn 一站的整条下单链断了**（R986）

**R985 说换一条不靠名字定位的核心工作。这一轮做的是优先级 ① 的真实状态：
每个站**能不能真下单** —— 而在这之前只有「每个步骤至少有 1 个覆写」这个**不同的**断言被量过。**

### ① 新工具，按**文件**数而不是按**步骤**数

**`hollow_audit.py` 回答的是「每个步骤跨所有站有几个覆写」。
而一个步骤在**别处**有覆写，说明不了**这个站的**覆写做了事。**

**`tools/flow_work_audit.py`：逐 flow 文件，把每个覆写体分类为「有实质工作」或「只返回一个结果」。**

### ② 而第一版分类器错得很有代表性

**第一版只把 `await` / `Http` / 会话访问算作工作，于是把这一行判成占位：**

```csharp
public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
    OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct);
```

**工作藏在辅助方法里。而那是 **R824 记过的同一件事**：「委派是**无接收者**调用，`\\w+\\.名字` 一定漏」。**

> **第一版：185 个覆写里 175 真、**10 占位**。
> 修好（把对本类方法的委派也算工作）：**180 真、5 占位**。
> 而那 5 个假占位里有 4 个是 `GetCheckout`，正是**下单链路上的关键一步** ——
> **如果我按第一版去「补」它们，我会写四份重复的实现，而它们本来就在。****

### ③ 修好之后的真实状态

| flow | 覆写 | 真 | 占位 |
|---|---|---|---|
| Magento | 33 | 33 | 0 |
| PopMart | 23 | 23 | 0 |
| Shopify | 18 | 17 | **1** |
| Footsites | 17 | 17 | 0 |
| Nike | 15 | 15 | 0 |
| Scheels | 12 | 12 | 0 |
| Farfetch / Hbx / Hybris | 10 each | 10 | 0 |
| **Bstn** | 9 | 5 | **4** |
| Demandware | 9 | 9 | 0 |
| Goat | 8 | 8 | 0 |
| 其余 5 个 | 1–5 | 全真 | 0 |
| **合计** | **185** | **180** | **5** |

**97.3% 的覆写做了超出「返回一个结果」的工作。**

### ④ 而那 5 个占位，两个类别

**Bstn 的 4 个 —— 整条下单链：**

```
AddToCart    Fail("bstn: cart endpoint unknown — /cart.js is 404 and the cart lives under /api/b…")
GetCart      Fail("bstn: cart endpoint unknown")
GetCheckout  Fail("bstn: checkout endpoint unknown (Adyen)")
SubmitOrder  Fail("bstn: order endpoint unknown")
```

**Shopify 的 1 个 —— `GetCsrf`，**有意**的空实现，注释写着 R823 的理由：
「不编造 fallback。GetHomeAsync 已经从页面提取 `authenticity_token`；若没有，在这里造一个 GUID
会把服务器从未签发的令牌放进会话，而每个带它的请求都会被判无效」。**

> **所以 10 个占位里，4 个是**我们不知道端点**，1 个是**有意不做**，5 个是我分类器的错。**
> **而「Bstn 能监控不能下单」现在有确切形状：找商品、读尺码、读库存四步都在，
> 从加购到提交订单四步全断，且断在「端点未知」上。****

### ⑤ 加的两条守卫

**`FlowWorkAuditTests`（2 用例）：**
1. `MostOverridesDoWork` —— 覆写总数 > 100（签名正则失配就会红），且占位数**不超过 5**
2. `AFlowWithPlaceholdersSaysWhy` —— 有 ≥2 个占位的 flow 必须出现 `endpoint unknown` 字样
   （**一个不说原因的占位，读起来像疏忽，而不是一条记下来的缺口**）

### 6 这一轮把「能不能下单」从**无测度**变成**一个数 + 一个具名缺口**

**而它同时说明：优先级 ① 的剩余不是「35 个站都要做」，是**一个站的四个端点**。
那是一个可完成的量，而不是一片模糊。**

### 数字

| 度量 | R985 | **R986** |
|---|---|---|
| 套件 | 2203 | **2205** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **flow 覆写总数** | 未测 | **185** |
| **有实质工作** | 未测 | **180（97.3%）** |
| **占位** | 未测 | **5（Bstn 4 + Shopify 1 有意）** |

### 教训

> **我的分类器第一版漏了「委派」，而那正是 R824 记过的形状 —— 只是那次是搜索，这次是分类。
> 同一条规则（「无接收者的调用看不见」）换了场景，我一次都没想起它。**
> **而代价如果不抽查：我会去「补」四个本来就在的方法。**
"""

if "优先级 ① 有了每站的数" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 986 轮：优先级 ① 有了每站的数 —— 185 覆写里 180 做实事，只有 Bstn 的下单链断

### ① 新工具按**文件**数，不按**步骤**数

**`hollow_audit.py` 答的是「每个步骤跨所有站有几个覆写」，
而一个步骤在别处有覆写，说明不了**这个站的**覆写做了事。**

**`tools/flow_work_audit.py`：逐 flow 文件分类每个覆写体。**

### ② 而第一版分类器错得很有代表性

**只把 `await`/`Http`/会话访问算作工作，于是把这一行判成占位：**

```csharp
public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
    OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct);
```

**工作藏在辅助方法里 —— **R824 记过的同一件事**：「委派是无接收者调用，`\\w+\\.名字` 一定漏」。**

> **第一版 175 真 / **10 占位**。修好 180 真 / **5 占位**。
> 而那 5 个假占位里 4 个是 `GetCheckout` —— 下单链路关键一步。
> **如果按第一版去「补」，我会写四份重复实现，而它们本来就在。****

### ③ 真实状态

| flow | 覆写 | 真 | 占位 |
|---|---|---|---|
| Magento | 33 | 33 | 0 |
| PopMart | 23 | 23 | 0 |
| Shopify | 18 | 17 | **1** |
| Footsites | 17 | 17 | 0 |
| Nike | 15 | 15 | 0 |
| Scheels | 12 | 12 | 0 |
| Farfetch / Hbx / Hybris | 各 10 | 10 | 0 |
| **Bstn** | 9 | 5 | **4** |
| Demandware | 9 | 9 | 0 |
| Goat | 8 | 8 | 0 |
| 其余 5 | 1–5 | 全真 | 0 |
| **合计** | **185** | **180** | **5** |

**97.3% 做了超出「返回一个结果」的工作。**

### ④ 那 5 个占位，两个类别

**Bstn 的 4 个 —— 整条下单链：`AddToCart` / `GetCart` / `GetCheckout` / `SubmitOrder`，
消息都是 `cart / checkout / order endpoint unknown`。**

**Shopify 的 1 个 —— `GetCsrf`，**有意**空实现，注释写着 R823 的理由：
不编造 fallback（服务器未签发的令牌会让每个带它的请求被判无效）。**

> **10 个占位里：4 个是我们不知道端点，1 个是有意不做，5 个是我分类器的错。
> 「Bstn 能监控不能下单」现在有确切形状：找商品/读尺码/读库存四步在，加购到提交订单四步全断。**

### ⑤ 两条守卫

**`FlowWorkAuditTests`：占位数 ≤ 5（且总数 > 100 防正则失配）；有 ≥2 占位的 flow 必须写明 `endpoint unknown`
（**不说原因的占位读起来像疏忽，而不是一条记下来的缺口**）。**

### ⑥ 把「能不能下单」从无测度变成**一个数 + 一个具名缺口**

> **优先级 ① 的剩余不是「35 个站都要做」，是**一个站的四个端点**。那是一个可完成的量。**

### 数字

| 度量 | R985 | **R986** |
|---|---|---|
| 套件 | 2203 | **2205** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **flow 覆写总数** | 未测 | **185** |
| **有实质工作** | 未测 | **180（97.3%）** |
| **占位** | 未测 | **5** |

### 教训

> **同一条规则（「无接收者的调用看不见」）换了场景，我一次都没想起它。
> 而代价如果不抽查：我会去「补」四个本来就在的方法。**
"""

BACKLOG_ADD = """

## 判据 (f)/优先级 ① — **185 覆写中 180 有实质工作；占位 5 个：Bstn 下单链 4 + Shopify 有意 1**（R986，**+1 工具 +2 守卫**）

### 新工具

**`tools/flow_work_audit.py` —— 按 **flow 文件**分类每个覆写体（`hollow_audit.py` 是按步骤跨站数）。**

### 分类器修正

**第一版只把 `await`/`Http`/会话访问算作工作 → 把 `=> OpenCheckoutAsync(...)` 判成占位（5 个假阳性）。
**R824 记过同一形状：「委派是无接收者调用」。** 修好：180 真 / 5 占位。**

### 真实状态

| flow | 覆写 | 真 | 占位 |
|---|---|---|---|
| Magento 33 · PopMart 23 · Shopify 18 · Footsites 17 · Nike 15 · Scheels 12 · Farfetch/Hbx/Hybris 各 10 · Demandware 9 · Goat 8 | | 全真 | 0（Shopify 除外 1） |
| **Bstn** | 9 | 5 | **4** |
| **合计** | **185** | **180（97.3%）** | **5** |

### 5 个占位

**Bstn：`AddToCart` / `GetCart` / `GetCheckout` / `SubmitOrder` —— 消息都是 `cart/checkout/order endpoint unknown`。**
**Shopify `GetCsrf`：有意空实现（R823：不编造 fallback）。**

**→ 优先级 ① 的剩余 = **一个站的四个端点**，不是「35 个站」。**

### 数字

**套件 2205 · 陈旧度 0/0 · 函数数 173,952 · 覆写 185 / 真 180 / 占位 5**

| 仍 Unknown | |
|---|---|
| Bstn 的 cart / checkout / order 端点 | 未取证（消息说的就是它） |

**纪律**：「无接收者的调用看不见」—— 搜索时是它，分类时还是它。
"""

BLOCKER = """

---

## 410. **185 覆写中 180 有实质工作；占位 5 个 = Bstn 下单链 4 + Shopify 有意 1**

> R986。**+1 工具 +2 守卫。** 套件 **2205 通过 / 0 失败 / 0 跳过**。

### 一、为什么需要新工具

**`hollow_audit.py` 回答「每个**步骤**跨所有站有几个覆写」。
而一个步骤在别处有覆写，说明不了**这个站的**覆写做了事。**

**`tools/flow_work_audit.py`：逐 flow **文件**，把每个覆写体分类为「有实质工作」或「只返回一个结果」。**

### 二、而第一版分类器错得很有代表性

**第一版只把 `await` / `Http` / 会话访问算作工作，于是把这一行判成占位：**

```csharp
public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
    OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct);
```

**→ 工作藏在辅助方法里。这是 **R824 记过的同一件事**：「委派是**无接收者**调用，`\\w+\\.名字` 一定漏」。
→ 第一版 175 真 / **10 占位**；修好（对本类方法的委派也算工作）**180 真 / 5 占位**。
→ 那 5 个假占位里 4 个是 `GetCheckout` —— **如果按第一版去「补」，会写四份重复实现，而它们本来就在。****

### 三、真实状态

| flow | 覆写 | 真 | 占位 |
|---|---|---|---|
| Magento | 33 | 33 | 0 |
| PopMart | 23 | 23 | 0 |
| Shopify | 18 | 17 | **1** |
| Footsites | 17 | 17 | 0 |
| Nike | 15 | 15 | 0 |
| Scheels | 12 | 12 | 0 |
| Farfetch / Hbx / Hybris | 各 10 | 10 | 0 |
| **Bstn** | 9 | 5 | **4** |
| Demandware | 9 | 9 | 0 |
| Goat | 8 | 8 | 0 |
| Sportsshoes 3 · Dicks 2 · NikeGs 1 | | 全真 | 0 |
| AdyenPayPal / Store | 0 | 0 | 0 |
| **合计** | **185** | **180（97.3%）** | **5** |

### 四、5 个占位，两个类别

**Bstn —— 整条下单链：**

```
AddToCart    Fail("bstn: cart endpoint unknown — /cart.js is 404 and the cart lives under /api/b…")
GetCart      Fail("bstn: cart endpoint unknown")
GetCheckout  Fail("bstn: checkout endpoint unknown (Adyen)")
SubmitOrder  Fail("bstn: order endpoint unknown")
```

**Shopify `GetCsrf` —— 有意空实现**，注释写着 R823 的理由：不编造 fallback
（服务器从未签发的令牌放进会话，会让每个带它的请求被判无效）。**

**→ 10 个占位里：4 个是我们不知道端点，1 个是有意不做，5 个是我分类器的错。
→ 「Bstn 能监控不能下单」有确切形状：找商品/读尺码/读库存四步在，加购到提交订单四步全断。
→ 优先级 ① 的剩余 = **一个站的四个端点**，不是「35 个站」。**

### 五、两条守卫（`FlowWorkAuditTests`）

1. `MostOverridesDoWork` —— 覆写总数 > 100（签名正则失配即红），占位数 **≤ 5**
2. `AFlowWithPlaceholdersSaysWhy` —— 有 ≥2 占位的 flow 必须出现 `endpoint unknown`
   （**不说原因的占位读起来像疏忽，而不是一条记下来的缺口**）

### 六、数字

| 度量 | R985 | R986 |
|---|---|---|
| 套件 | 2203 | **2205** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **flow 覆写总数** | 未测 | **185** |
| **有实质工作** | 未测 | **180（97.3%）** |
| **占位** | 未测 | **5** |

### 七、验证

```
cd replica
python tools/flow_work_audit.py  -> 185 / 180 / 5，97.3%
dotnet test --filter "FullyQualifiedName~FlowWorkAuditTests" -m:1  -> 2 通过
python tools/metrics_report.py   -> 完整套件 exit 0  2205 通过 / 0 失败 / 0 跳过
```

### 八、仍然 Unknown

- **Bstn 的 cart / checkout / order 端点**：**Unknown** —— 未取证，而占位的消息说的就是它。

### 九、教训

**同一条规则（「无接收者的调用看不见」）换了场景，我一次都没想起它 —— 那次是搜索，这次是分类。**

**而代价如果不抽查：我会去「补」四个本来就在的方法。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R986", BLOCKER)
    ensure(RSTATUS, "R986", BLOCKER)
    ensure(RVERDICT, "第 986 轮", VERDICT)
    ensure(BACKLOG, "R986", BACKLOG_ADD)

    note = (
        "\n## R986 补充 — **185 覆写中 180 有实质工作；占位 5 个 = Bstn 下单链 4 + Shopify 有意 1**（+1 工具 +2 守卫，套件 2205）\n\n"
        "新工具 `tools/flow_work_audit.py`：按 **flow 文件**分类每个覆写体（`hollow_audit.py` 是按步骤跨站数）。\n\n"
        "**分类器第一版错了**：只把 `await`/`Http`/会话访问算工作，把 `=> OpenCheckoutAsync(...)` 判成占位（5 个假阳性）。\n"
        "那正是 **R824 记过的形状：「委派是无接收者调用，`\\w+\\.名字` 一定漏」**。修好：**180 真 / 5 占位**。\n\n"
        "| flow | 覆写 | 真 | 占位 |\n|---|---|---|---|\n"
        "| Magento 33 · PopMart 23 · Footsites 17 · Nike 15 · Scheels 12 · Farfetch/Hbx/Hybris 各 10 · Demandware 9 · Goat 8 | | 全真 | 0 |\n"
        "| Shopify | 18 | 17 | **1** |\n| **Bstn** | 9 | 5 | **4** |\n| **合计** | **185** | **180（97.3%）** | **5** |\n\n"
        "**5 个占位 = Bstn 的 AddToCart/GetCart/GetCheckout/SubmitOrder（消息都是 `endpoint unknown`）+ Shopify 的 GetCsrf（R823 有意不编造）。**\n\n"
        "→ 优先级 ① 的剩余 = **一个站的四个端点**，不是「35 个站」。\n\n"
        "守卫 `FlowWorkAuditTests`（2 用例）：占位 ≤ 5；有 ≥2 占位的 flow 必须写明 `endpoint unknown`。\n\n"
        "数字：套件 2205 · 陈旧度 0/0 · 函数数 173,952 · 覆写 185/真 180/占位 5。\n\n"
        "纪律：**「无接收者的调用看不见」—— 搜索时是它，分类时还是它。**\n\n"
        "下一轮：取 Bstn 的三个端点（cart / checkout / order），把那一站的四个占位补成真实现。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R986" not in h:
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
             for p, k in ((RBLOCK, "R986"), (RSTATUS, "R986"), (RVERDICT, "第 986 轮"), (BACKLOG, "R986")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R986: per-flow work measured, and only one store's order chain is actually broken\n\n"
         "R985 left the core for a route that does not need names to reach code. This measures where priority one actually\n"
         " stands. The figure quoted for it until now was that every audited step has at least one override, which is a\n"
         " different claim: a step having an override somewhere says nothing about whether a given store's override does\n"
         " anything. hollow_audit answers per step across stores; the new flow_work_audit answers per file.\n\n"
         "The first classifier counted only an await, an HTTP call or session access as work, and so called\n"
         " `=> OpenCheckoutAsync(c, \"goat-checkout\", \"/checkout\", ct)` a placeholder. Five false positives, four of them\n"
         " GetCheckout -- the middle of the order chain. That is the shape R824 recorded about delegation: a call to a\n"
         " method of the same class has no receiver, so a pattern looking for something.Name sees nothing. Counting\n"
         " delegation as work brings 175 real and 10 placeholders down to 180 and 5.\n\n"
         "So of 185 overrides across 35 store flows, 180 do work. Four of the five remaining placeholders are Bstn's entire\n"
         " order chain -- add to cart, get cart, get checkout, submit order -- each returning a failure whose message says\n"
         " the endpoint is unknown. The fifth is Shopify's GetCsrf, deliberately empty with round 823's reasoning recorded:\n"
         " inventing a token the server never issued would make every request carrying it invalid.\n\n"
         "That turns the priority from an unmeasured area into one number and one named gap: four endpoints at one store.\n"
         " Had the classifier not been spot-checked, I would have written four duplicate implementations of methods that\n"
         " already exist.\n\n"
         "Two guards pin it: the placeholder count may not exceed five, and any flow with two or more placeholders must say\n"
         " the endpoint is unknown -- a placeholder that does not name what is missing reads as an oversight rather than a\n"
         " recorded gap.\n\n"
         "Figures: suite 2203 to 2205, freshness zero, count 173,952, overrides 185 with 180 doing work.\n\n"
         "Unknown: Bstn's cart, checkout and order endpoints, which is exactly what its placeholders say.\n\n"
         "The lesson is that the same rule -- a call with no receiver is invisible -- came back in a new costume, and I did\n"
         " not recognise it the second time.\n\n"
         "One tool and two guard tests added; suite green at 2205."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()