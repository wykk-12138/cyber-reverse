"""Record R1017: Farfetch's API surface is not in the image at all, and the two Shopify sites stay put."""

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
### Farfetch 的 API 面**完全不在镜像里**；而 Shopify 那两处有候选却仍不改（R1017）

**R1016 说下一轮取证 Farfetch 与 Shopify 的真实端点，改那 10 处。取证了，而结论是那 10 处里**没有一处该改**。**

### ① Farfetch：镜像里只有**三条**串，全是名字

```
Farfetch          n=3
  0x14338eadc  Farfetch            ← 反射元数据（类型/方法名，UTF-8）
  0x146d8dfdc  Farfetch            ← 字面量
  0x146d8e004  Farfetch Checkout   ← 显示名

api.farfetch      n=0
farfetch.com      n=0
ff-products       n=0
basket/v1         n=0
```

**→ Farfetch **是一个真实的站**（有名字、有「Farfetch Checkout」显示名），而它的 **API 面在字符串层面**一条都没有**。
→ 所以那 7 处路径**不只是拼错，是整个 host 都不存在**，而镜像**不提供**替代。
→ 「Farfetch 怎么工作」只能从**代码级**证据得到（那在 NativeAOT 下按名不可得，R958）⇒ **Unknown，不是待办。****

### ② Shopify 那两处：有候选，而候选不够

**`/api/payments/`（`StoreFlow.cs:1272`）：**

```
/payments/        n=39   → /payments/ · /payments/config.json · /payments/place-order
                            /payments/adyen/payment-methods · /payments/creditCardWithPayerAuthentication/
/api/payments     n=0
```

**→ 所以 `/api` 前缀是**复刻件自己加的**，而 `/payments/` 确实存在 —— 那看起来像一次有据替换。
→ **但那 39 处是**别的站**的钱面（`/payments/adyen/...` · `/payments/place-order`），
  而「查一笔付款详情」的形状**不在**镜像展示的那几种里。**
→ 而 R48 的裁决正好管这个：知道这个路径存在 ≠ 知道这个 step 用它。**

**`/discount/`（`StoreFlow.cs:768`）：**

```
/discount/        n=0
cart/update.js    n=1   （0x146fc175c）
cart/add.js       n=1   （0x146fc16dc）
```

**→ 镜像里有 `cart/update.js`，而 Shopify 的常规做法是把折扣码放进那个 POST 的 body，不是放进路径。
→ 那是一个**候选**，而「`SubmitDiscount` 到底打哪」仍然没有证据。**

### ③ 而决定性的一条：两处都**零覆写**

| 方法 | 覆写数 | R963 的后果 |
|---|---|---|
| `SubmitDiscountAsync` | **0** | **被裁，不在产物里** |
| `GetPaymentDetailsAsync` | **0** | **被裁，不在产物里** |

**→ 所以这两处**改不改都不影响产物** —— 它们只影响源码读起来对不对。
→ 而把一个**不可达**的调用换成另一个**不可达**的调用，正是 R48 说的「swapping one guess for another」，
  只是这次连「会不会发出去」都不涉及。**

**→ 所以这一轮**没有改行为**，只把取证结果写进两处的注释：**

- `:1272` —— `/api/payments/` 0 命中，`/payments/` 39 处属别的站，本步无覆写被裁
- `:768` —— `/discount/` 0 命中，候选是 `cart/update.js` 带 body，本步无覆写被裁

### ④ 而那 10 处的最终分类

| 类 | 数 | 处置 |
|---|---|---|
| **镜像完全不提供**（Farfetch） | **7** | **Unknown** —— 需代码级证据 |
| **有候选但证据不足**（Shopify ×2） | **2** | **记在注释里，不改** |
| **已确证不存在且有明确替代**（Nike `buy/carts/v2`） | **1** | R1013/R1014 已处置（报告） |

**→ 所以扫描器仍红 10，而**那 10 个全部有据可查地处置过了** —— 3 个改了、7 个标 Unknown。
→ 而「红 10」现在是**正确且已解释**的状态，不再是待办。**

### ⑤ 数字

| 度量 | R1016 | **R1017** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **2 / 3,365（StoreFlow.cs + 工具）** |
| 函数数 | 174,336 | **174,336** |
| **扫描器未登记** | 10 | **10（但全部已处置：7 Unknown · 2 注释 · 1 已报告）** |
| **Farfetch 串总数** | 未测 | **3（全是名字，无 host 无路径）** |
| **`/payments/` 与 `/api/payments/`** | 未测 | **39 vs 0** |

### 教训

> **「这个端点不在镜像里」有两种后续：有的能换成镜像里有的另一个，有的**镜像根本不提供**。
> → 前者是修，后者是 Unknown —— 而两者的第一步取证动作一样，第二步取决于**那个站有没有 API 面**。
> **→ 而 Farfetch 的情况说明：一个站可以在镜像里只有**名字**。**
> → 那时「照实报告」不是保守，是**唯一没有在发明的做法**。**
"""

if "Farfetch 的 API 面**完全不在镜像里**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1017 轮：Farfetch 的 API 面完全不在镜像里；Shopify 那两处有候选却仍不改

### ① Farfetch：镜像里只有**三条**串，全是名字

```
Farfetch          n=3   0x14338eadc / 0x146d8dfdc / 0x146d8e004（Farfetch Checkout）
api.farfetch      n=0   farfetch.com n=0   ff-products n=0   basket/v1 n=0
```

**→ Farfetch **是一个真实的站**（有名字、有显示名），而它的 **API 面在字符串层面一条都没有**。
→ 那 7 处**不只是拼错，是整个 host 都不存在**，而镜像**不提供**替代。
→ 「Farfetch 怎么工作」只能从**代码级**证据得到（NativeAOT 下按名不可得，R958）⇒ **Unknown，不是待办。****

### ② Shopify 那两处：有候选，而候选不够

**`/api/payments/`（1272）**：`/payments/` **39 处**，`/api/payments` **0** ⇒ `/api` 是自加的。
**但那 39 处是**别的站**的钱面（`/payments/adyen/…` · `/payments/place-order`），
「查付款详情」的形状不在其中。→ R48 的裁决正管这个。**

**`/discount/`（768）**：0 命中；候选是 `cart/update.js`（0x146fc175c）+ body 带码。
→ 那是一个**候选**，而「`SubmitDiscount` 到底打哪」仍无证据。**

### ③ 而决定性的一条：两处都**零覆写**

| 方法 | 覆写 | R963 |
|---|---|---|
| `SubmitDiscountAsync` | **0** | **被裁，不在产物里** |
| `GetPaymentDetailsAsync` | **0** | **被裁，不在产物里** |

**→ 所以改不改都不影响产物。而把一个**不可达**的调用换成另一个不可达的调用，
正是 R48 说的「swapping one guess for another」。**

**→ 所以这一轮**没有改行为**，只把取证写进两处注释。**

### ④ 那 10 处的最终分类

| 类 | 数 | 处置 |
|---|---|---|
| **镜像完全不提供**（Farfetch） | **7** | **Unknown** —— 需代码级证据 |
| **有候选但证据不足**（Shopify ×2） | **2** | **记在注释里，不改** |
| **已确证不存在且有明确替代**（Nike） | **1** | 已报告（R1013/1014） |

**→ 扫描器仍红 10，而那 10 个**全部有据可查地处置过了** ⇒ 「红 10」现在是**正确且已解释**的状态。**

### ⑤ 数字

| 度量 | R1016 | **R1017** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **2 / 3,365** |
| 函数数 | 174,336 | **174,336** |
| **扫描器未登记** | 10 | **10（全部已处置）** |
| **Farfetch 串总数** | 未测 | **3（全是名字）** |
| **`/payments/` vs `/api/payments/`** | 未测 | **39 vs 0** |

### 教训

> **「这个端点不在镜像里」有两种后续：有的能换成镜像里有的另一个，有的**镜像根本不提供**。
> → 前者是修，后者是 Unknown —— 两者第一步取证一样，第二步取决于**那个站有没有 API 面**。
> → 而 Farfetch 说明：一个站可以在镜像里只有**名字**。那时「照实报告」不是保守，是**唯一没有在发明的做法**。**
"""

BACKLOG_ADD = """

## 优先级 ① — **Farfetch 的 API 面完全不在镜像里；Shopify 两处有候选却仍不改；10 处全部处置完毕**（R1017）

### Farfetch：镜像只有 3 条串，全是名字

**`Farfetch` · `Farfetch` · `Farfetch Checkout`（`0x14338eadc` · `0x146d8dfdc` · `0x146d8e004`）。
而 `api.farfetch` 0 · `farfetch.com` 0 · `ff-products` 0 · `basket/v1` 0。**

**→ 站是真的（有显示名），**API 面一条都没有** ⇒ 7 处路径不只是拼错，是整个 host 不存在。
→ 修法只能来自代码级证据（R958 说按名不可得）⇒ **Unknown，不是待办。****

### Shopify：有候选，候选不够

- **`/api/payments/`（1272）**：`/payments/` **39** · `/api/payments` **0** ⇒ `/api` 是自加的。
  **但那 39 处是别的站的钱面，「查付款详情」的形状不在其中 ⇒ R48 的裁决。**
- **`/discount/`（768）**：**0**；候选 `cart/update.js`（`0x146fc175c`）+ body 带码 ⇒ 仍是候选。

### 决定性：两处都零覆写 ⇒ 被裁 ⇒ 不在产物

**改不改都不影响产物；换一个不可达的调用 = R48 的「swapping one guess for another」。**
**→ 所以本轮不改行为，只把取证写进两处注释。**

### 10 处的最终分类

| 类 | 数 | 处置 |
|---|---|---|
| 镜像完全不提供（Farfetch） | 7 | **Unknown** |
| 有候选但证据不足（Shopify） | 2 | **注释，不改** |
| 已确证不存在（Nike） | 1 | 已报告 |

**→ 扫描器红 10 现在是**正确且已解释**的状态。**

### 数字

**套件 2219/0/0 · 陈旧度 2 / 3,365 · 函数数 174,336 · 未登记 10（全处置）· Farfetch 串 3 · `/payments/` 39 vs `/api/payments/` 0**

| 仍 Unknown | |
|---|---|
| Farfetch 怎么工作 | 需代码级证据（R958） |
| discount 打哪 | 候选 `cart/update.js`，无证据 |

**纪律**：一个站可以在镜像里只有名字；那时照实报告是唯一没有在发明的做法。
"""

BLOCKER = """

---

## 441. **Farfetch 的 API 面完全不在镜像里；Shopify 两处有候选却仍不改；10 处全部处置完毕**

> R1017。**改 1 个源文件（两处注释，行为未变）。** 套件 **2219 通过 / 0 失败 / 0 跳过**。

### 一、Farfetch：镜像里只有**三条**串，全是名字

```
Farfetch          n=3
  0x14338eadc  Farfetch            ← 反射元数据（类型/方法名，UTF-8）
  0x146d8dfdc  Farfetch            ← 字面量
  0x146d8e004  Farfetch Checkout   ← 显示名

api.farfetch      n=0
farfetch.com      n=0
ff-products       n=0
basket/v1         n=0
```

**→ Farfetch **是一个真实的站**（有名字、有「Farfetch Checkout」显示名），
而它的 **API 面在字符串层面一条都没有**。
→ 所以那 7 处路径**不只是拼错，是整个 host 都不存在**，而镜像**不提供**替代。
→ 「Farfetch 怎么工作」只能从**代码级**证据得到（那在 NativeAOT 下按名不可得，R958）
  ⇒ **Unknown，不是待办。****

### 二、Shopify 那两处：有候选，而候选不够

**`/api/payments/`（`StoreFlow.cs:1272`）：**

```
/payments/        n=39   → /payments/ · /payments/config.json · /payments/place-order
                            /payments/adyen/payment-methods · /payments/creditCardWithPayerAuthentication/
/api/payments     n=0
```

**→ 所以 `/api` 前缀是**复刻件自己加的**，而 `/payments/` 确实存在。
→ **但那 39 处是**别的站**的钱面，「查一笔付款详情」的形状**不在**镜像展示的那几种里。**
→ 而 R48 的裁决正好管这个：**知道这个路径存在 ≠ 知道这个 step 用它。**

**`/discount/`（`StoreFlow.cs:768`）：**

```
/discount/        n=0
cart/update.js    n=1   （0x146fc175c）
cart/add.js       n=1   （0x146fc16dc）
```

**→ 镜像里有 `cart/update.js`，而 Shopify 的常规做法是把折扣码放进那个 POST 的 body，不是路径。
→ 那是一个**候选**，而「`SubmitDiscount` 到底打哪」仍无证据。**

### 三、决定性：两处都**零覆写**

| 方法 | 覆写数 | R963 的后果 |
|---|---|---|
| `SubmitDiscountAsync` | **0** | **被裁，不在产物里** |
| `GetPaymentDetailsAsync` | **0** | **被裁，不在产物里** |

**→ 所以这两处**改不改都不影响产物** —— 它们只影响源码读起来对不对。
→ 而把一个**不可达**的调用换成另一个**不可达**的调用，正是 R48 说的「swapping one guess for another」。**

**→ 所以这一轮**没有改行为**，只把取证结果写进两处的注释：**

- `:1272` —— `/api/payments/` 0 命中，`/payments/` 39 处属别的站，本步无覆写被裁
- `:768` —— `/discount/` 0 命中，候选是 `cart/update.js` 带 body，本步无覆写被裁

### 四、那 10 处的最终分类

| 类 | 数 | 处置 |
|---|---|---|
| **镜像完全不提供**（Farfetch） | **7** | **Unknown** —— 需代码级证据 |
| **有候选但证据不足**（Shopify ×2） | **2** | **记在注释里，不改** |
| **已确证不存在且有明确替代**（Nike `buy/carts/v2`） | **1** | R1013/R1014 已处置（报告） |

**→ 所以扫描器仍红 10，而**那 10 个全部有据可查地处置过了**：
  3 个改了、7 个标 Unknown。
→ 而「红 10」现在是**正确且已解释**的状态，不再是待办。**

### 五、数字

| 度量 | R1016 | R1017 |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **2 / 3,365（StoreFlow.cs + 工具）** |
| 函数数 | 174,336 | **174,336** |
| **扫描器未登记** | 10 | **10（但全部已处置）** |
| **Farfetch 串总数** | 未测 | **3（全是名字，无 host 无路径）** |
| **`/payments/` 与 `/api/payments/`** | 未测 | **39 vs 0** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "Farfetch"        -> {"n":3}（全是名字）
python analysis/ida.py str "api.farfetch"    -> {"n":0}
python analysis/ida.py str "ff-products"     -> {"n":0}
python analysis/ida.py str "/payments/"      -> {"n":39}
python analysis/ida.py str "/api/payments"   -> {"n":0}
python analysis/ida.py str "cart/update"     -> {"n":2}（含 cart/update.js）
python analysis/ida.py str "/discount"       -> {"n":0}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
python tools/metrics_report.py                                      -> 完整套件 exit 0  2219 / 0 / 0
```

### 七、仍然 Unknown

- **Farfetch 怎么工作**：**Unknown** —— 需代码级证据，而 R958 说按名不可得。
- **discount 打哪**：**候选 `cart/update.js`，无证据。**

### 八、教训

**「这个端点不在镜像里」有两种后续：有的能换成镜像里有的另一个，有的**镜像根本不提供**。
前者是修，后者是 Unknown —— 而两者的第一步取证动作一样，第二步取决于**那个站有没有 API 面**。**

**→ 而 Farfetch 的情况说明：一个站可以在镜像里只有**名字**。
→ 那时「照实报告」不是保守，是**唯一没有在发明的做法**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1017", BLOCKER)
    ensure(RSTATUS, "R1017", BLOCKER)
    ensure(RVERDICT, "第 1017 轮", VERDICT)
    ensure(BACKLOG, "R1017", BACKLOG_ADD)

    note = (
        "\n## R1017 补充 — **Farfetch 的 API 面完全不在镜像里；Shopify 两处有候选却仍不改；10 处全部处置完毕**\n\n"
        "**Farfetch：镜像只有 3 条串，全是名字**（`Farfetch` · `Farfetch` · `Farfetch Checkout`）。\n"
        "而 `api.farfetch` **0** · `farfetch.com` **0** · `ff-products` **0** · `basket/v1` **0**。\n"
        "→ 站是真的（有显示名），**API 面一条都没有** ⇒ 7 处**不是拼错，是整个 host 不存在**。\n"
        "→ 只能从代码级证据得到（R958 说按名不可得）⇒ **Unknown，不是待办。**\n\n"
        "**Shopify 两处有候选，候选不够**：\n"
        "- `/api/payments/`（1272）：`/payments/` **39** 处而 `/api/payments` **0** ⇒ `/api` 是自加的，\n"
        "  但那 39 处是**别的站**的钱面，「查付款详情」的形状不在其中 ⇒ R48 裁决。\n"
        "- `/discount/`（768）：**0**；候选 `cart/update.js`（`0x146fc175c`）+ body 带码 ⇒ 仍是候选。\n\n"
        "**决定性：两处都零覆写 ⇒ 被裁 ⇒ 不在产物** ⇒ 改不改都不影响产物；\n"
        "换一个不可达的调用 = R48 的「swapping one guess for another」。**→ 本轮不改行为，只写注释。**\n\n"
        "**10 处全部处置完毕**：7 个 Unknown（Farfetch）· 2 个注释不改（Shopify）· 1 个已报告（Nike）。\n"
        "→ 扫描器**红 10 现在是正确且已解释**的状态，不再是待办。\n\n"
        "数字：套件 2219/0/0 · 陈旧度 2 / 3,365 · 函数数 174,336 · Farfetch 串 3 · `/payments/` 39 vs 0。\n\n"
        "纪律：**一个站可以在镜像里只有名字；那时照实报告是唯一没有在发明的做法。**\n\n"
        "下一轮：换到别的站（Farfetch 已封口为 Unknown）；或重新看优先级 ② 的风控面。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1017" not in h:
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
             for p, k in ((RBLOCK, "R1017"), (RSTATUS, "R1017"), (RVERDICT, "第 1017 轮"), (BACKLOG, "R1017")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1017: Farfetch's API surface is not in the image at all\n\n"
         "R1016 left ten names to judge. Judging them meant asking what the image holds for each host, and for Farfetch\n"
         " the answer is three strings: the name twice and the display name \"Farfetch Checkout\". There is no api.farfetch,\n"
         " no farfetch.com, no ff-products and no basket/v1. So those seven paths are not misspelled -- the host they\n"
         " would call does not exist in the artifact, and the image offers nothing to put in its place. A store can be\n"
         " present as a name and absent as an API, and when that is the case reporting is the only move that is not\n"
         " inventing.\n\n"
         "The two Shopify sites are a different shape and get a different answer. /payments/ appears thirty-nine times\n"
         " while /api/payments appears none, so the /api prefix is this workspace's addition. That looks like a\n"
         " substitution worth making until you read the thirty-nine: they are other stores' payment surfaces, place-order\n"
         " and config and the adyen method list, and a payment-details lookup is not among the shapes shown. Round 48\n"
         " already ruled on that gap -- knowing a path exists is not knowing this step uses it. The discount site is the\n"
         " same: /discount is absent, cart/update.js is present, and Shopify's convention puts the code in that POST's\n"
         " body rather than in the path, which makes it a candidate and not an answer.\n\n"
         "What settles both, though, is that neither method has an override. Under R963 both bodies are trimmed and\n"
         " neither reaches the artifact, so changing them would move nothing observable -- and swapping one unreachable\n"
         " call for another unreachable call is exactly what round 48 declined to do.\n\n"
         "So no behaviour changed. Both sites now carry the evidence in comments: which spelling is absent, what the\n"
         " image offers instead, and that the method is trimmed so the address cannot reach the wire. The ten names are\n"
         " now all disposed: seven unknown because the image does not supply them, two recorded rather than substituted,\n"
         " and one already reported. The scanner stays red at ten, and ten is now an explained count rather than a\n"
         " backlog.\n\n"
         "Figures: suite 2219 with no failures, freshness two files and 3,365 lines, count 174,336, three Farfetch strings\n"
         " of which none is a host, and the payments spelling at thirty-nine against zero.\n\n"
         "Unknown: how Farfetch's flow works, which needs code-level evidence NativeAOT does not give by name, and where\n"
         " the discount code is actually posted.\n\n"
         "The lesson is that \"this endpoint is not in the image\" has two follow-ups, one where something in the image\n"
         " can take its place and one where the image supplies nothing -- and telling them apart starts with the same\n"
         " question about whether that store has an API surface at all.\n\n"
         "One source file changed, both edits comments; suite green at 2219."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()