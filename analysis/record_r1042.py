"""Record R1042: the fourteen unknowns are not equally stuck, and a guard that silently did not run."""

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
### 那 14 个 Unknown **不是一样难**；而 Nike 的付款有**三条实名路由**（R1042）

**R1041 生成了表，说 14 个步骤报告端点未知。这一轮把它们的**消息**读了一遍 —— 而它们分成三组，
其中两组的消息**自带线索**。**

### ① 14 处不是同一种「不知道」

| flow | 数 | 消息里有什么 |
|---|---|---|
| **Farfetch** | 7 | 只说「原版有 Farfetch checkout，我们不知道 transport」—— **无线索** |
| **Bstn** | 4 | 第 1 条说「cart lives under `/api/beast`」· 第 3 条说「(Adyen)」—— **有线索** |
| **Nike** | 3 | 说「the image names `/rpc/payment/pay/initiatePayment`」—— **镜像里确实有名字** |

**→ 所以「14 个未知」这个计数掩盖了三种状态：彻底无线索（7）· 有候选（2）· 镜像里有名字（3）。**

### ② 而三条线索查下来的结果

```
/api/beast        n=0      ← Bstn 自己的消息说 cart 在那儿，而镜像里**零次**
adyen             n=167    ← 整套 Adyen 词汇：AdyenHandler · _adyenEU/UK/JP/AU · Adyen3DS · get_AdyenClientKey
rpc/payment/pay   n=3      ← **三条实名路由**
                             /rpc/payment/pay/initiatePayment
                             /rpc/payment/pay/submitAdyenDetails
                             /rpc/payment/pay/capturePayPalPaymentByChannelTransactionNo
buy/orders        n=0      ← 而 Nike 结账链的**上一步**：零次
```

**→ 两个结论：**
1. **Bstn 那条消息里的 `/api/beast` 是**它自己的**说法，镜像里 0 ⇒ 那条注释本身无据。
   → 而那是一条**待在注释里很久的假线索** —— 它把下一个人指向一个不存在的路径。**
2. **Nike 的付款不是「未取证」**：镜像里有三条实名路由，含 `submitAdyenDetails`。
   → 而 `NikeFlow.SubmitPaymentAsync` 的报告写着「the image names /rpc/payment/pay/initiatePayment」——
   **那句话是对的，而它仍然报告，因为**上一步**（`buy/orders/v2`）是 0。**

### ③ 而为什么不现在就把 Nike 的付款接上

**Nike 的结账链是 `SubmitShipping → GetPaymentMethods → SubmitPayment`。
→ 而 `buy/orders/v2`（shipping 那步）在镜像里 **0 次**，`buy/orders` 也 **0 次**。
→ 所以接上 `initiatePayment` 只是把失败点从「payment 未取证」挪到「shipping 未取证」——
→ **那正是 R48 的裁决：「换一个猜测只是移动失败，不是消除失败」。****

**→ 所以本轮**不动代码**：那三条路由被记下来，等 `buy/orders/v2` 有据时它们就是现成的。**

### ④ 而本轮还有一件**操作上的**事要记

**轮转三个 publish 目录时，我写的路径校验是：**

```powershell
if (Test-Path $p -and $p -notlike "$root\\.publish-aot*") { ... }
```

**→ PowerShell 需要 `(Test-Path $p) -and ...`，而那个写法**静默失败**（报 NamedParameterNotFound），
→ 于是**校验没跑，而删除与移动照旧执行了。**

**→ 结果是对的（三个路径都由 `(Get-Location)` 构造，本来就对），但那是**运气**，不是校验。
→ 而 AGENTS 那条「删除前先核实解析后的绝对路径」正是为此 —— 校验存在而没执行，比没有校验更坏，
因为它让人以为检查过了。**

**→ 而验证：`.publish-aot` 19:15（新）· `.publish-aot-prev` 18:55（旧）· 无 `-new` · exe 在。**

### ⑤ 数字

| 度量 | R1041 | **R1042** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| **产物陈旧度** | 1 / 217 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **报告 Unknown 的步骤** | 14 | **14（分成 7+4+3 三种状态）** |
| **`/api/beast` 在镜像里** | 未查 | **0 ⇒ Bstn 那条注释无据** |
| **`adyen` 词汇** | 未查 | **167 条** |
| **Nike 付款路由** | 「0 条」 | **3 条实名** |
| **Nike `buy/orders`** | 未查 | **0 ⇒ 上一步先断** |
| **路径校验是否执行** | — | **否（语法错，静默）** |

### 教训

> **「14 个未知」是一个**计数**，而计数把三种状态压成了一个大数字：
> 彻底无线索的 7 个、有候选的 2 个、镜像里有名字的 3 个。**
> **→ 而压平之后，那 3 个「其实有名字」的看起来和那 7 个一样无望。
> → 所以「未覆盖的每条写为什么」不只是写字 —— 它要求**每条都读一遍消息**，
> 因为消息里藏着下一轮能不能动手的全部信息。**
"""

if "那 14 个 Unknown **不是一样难**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1042 轮：那 14 个 Unknown 不是一样难；Nike 的付款有三条实名路由

### ① 14 处不是同一种「不知道」

| flow | 数 | 消息里有什么 |
|---|---|---|
| **Farfetch** | 7 | 只说「不知道 transport」—— **无线索** |
| **Bstn** | 4 | 第 1 条说「cart lives under `/api/beast`」· 第 3 条「(Adyen)」—— **有线索** |
| **Nike** | 3 | 说「the image names `/rpc/payment/pay/initiatePayment`」—— **镜像里确有名字** |

**→ 「14 个未知」这个计数把三种状态压成一个数字。**

### ② 三条线索的实际结果

```
/api/beast        n=0      ← Bstn 那条注释**无据**（它指向一个不存在的路径）
adyen             n=167    ← 整套词汇：AdyenHandler · _adyenEU/UK/JP/AU · Adyen3DS · get_AdyenClientKey
rpc/payment/pay   n=3      ← /initiatePayment · /submitAdyenDetails · /capturePayPalPaymentByChannelTransactionNo
buy/orders        n=0      ← Nike 结账链的**上一步**：零次
```

**→ Nike 的付款**不是**未取证 —— 而它仍报告，因为**上一步** `buy/orders/v2` 是 0。
→ 而接上 `initiatePayment` 只会把失败点挪到 shipping ⇒ **R48：「换一个猜测只是移动失败」。****

### ③ 所以本轮不动代码

**那三条路由记下来，等 `buy/orders/v2` 有据时它们就是现成的。**

### ④ 而一件**操作上的**事要记

```powershell
if (Test-Path $p -and $p -notlike "$root\\.publish-aot*") { ... }   ← 语法错，**静默失败**
```

**→ 校验没跑，删除与移动照旧执行。结果对（路径由 `(Get-Location)` 构造），但那是**运气**。
→ 而「校验存在但没执行」比没有校验更坏 —— 它让人以为检查过了。**
**→ 已验证：`.publish-aot` 19:15 · `.publish-aot-prev` 18:55 · 无 `-new` · exe 在。**

### ⑤ 数字

| 度量 | R1041 | **R1042** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| **产物陈旧度** | 1 / 217 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **Unknown 步骤** | 14 | **14（7+4+3 三种状态）** |
| **`/api/beast`** | 未查 | **0 ⇒ 注释无据** |
| **Nike 付款路由** | 「0」 | **3 条实名** |
| **路径校验执行** | — | **否（静默）** |

### 教训

> **「14 个未知」是**计数**，而计数把三种状态压成一个大数字：无线索 7 · 有候选 2 · 有名字 3。
> → 压平之后，那 3 个「其实有名字」的看起来和那 7 个一样无望。**
> **→ 「未覆盖的每条写为什么」不只是写字 —— 它要求**每条都读一遍消息**，
> 因为消息里藏着下一轮能不能动手的全部信息。**
"""

BACKLOG_ADD = """

## 判据 (f) — **14 个 Unknown 分三种状态；Nike 付款有 3 条实名路由；`/api/beast` 无据**（R1042）

### 三种状态

| flow | 数 | 消息 | 状态 |
|---|---|---|---|
| Farfetch | 7 | 只说不知道 transport | **无线索** |
| Bstn | 4 | `/api/beast` · `(Adyen)` | **有候选** |
| Nike | 3 | `the image names /rpc/payment/pay/initiatePayment` | **有名字** |

### 线索结果

```
/api/beast       0     ⇒ Bstn 那条注释**无据**（指向不存在的路径）
adyen            167   ⇒ AdyenHandler · _adyenEU/UK/JP/AU · Adyen3DS · get_AdyenClientKey
rpc/payment/pay  3     ⇒ /initiatePayment · /submitAdyenDetails · /capturePayPalPaymentByChannelTransactionNo
buy/orders       0     ⇒ Nike 结账链上一步先断
```

### 而接线被 R48 挡住

**接 `initiatePayment` 只把失败点挪到 shipping ⇒ 不动代码；记下三条路由备用。**

### 操作教训

**`if (Test-Path $p -and ...)` 语法错 ⇒ 校验静默没跑，而删除/移动照旧执行。
→ 结果对是因为路径由 `(Get-Location)` 构造，不是校验。**
**→ 「校验存在但没执行」比没有校验更坏。**

### 数字

**套件 2258/0/0 · 陈旧度 1/217 → **0/0** · 函数数 174,293 · Unknown 14（7+4+3）· Nike 付款路由 3 · `buy/orders` 0**

| 仍 Unknown | |
|---|---|
| `buy/orders/v2` 的真实路由 | 待取证（Nike 链的第一步） |
| Farfetch transport | 无线索 |

**纪律**：「未覆盖的每条写为什么」要求每条都读一遍消息 —— 消息里有能不能动手的全部信息。
"""

BLOCKER = """

---

## 466. **14 个 Unknown 不是一样难；Nike 付款有三条实名路由**

> R1042。**未改代码（publish + 取证）。** 套件 **2258 通过 / 0 失败 / 0 跳过**。
> **产物陈旧度 1 / 217 → 0 / 0。**

### 一、14 处不是同一种「不知道」

| flow | 数 | 消息里有什么 |
|---|---|---|
| **Farfetch** | 7 | 只说「原版有 Farfetch checkout，我们不知道 transport」—— **无线索** |
| **Bstn** | 4 | 第 1 条说「cart lives under `/api/beast`」· 第 3 条说「(Adyen)」—— **有线索** |
| **Nike** | 3 | 说「the image names `/rpc/payment/pay/initiatePayment`」—— **镜像里确实有名字** |

**→ 所以「14 个未知」这个计数掩盖了三种状态：彻底无线索（7）· 有候选（2）· 镜像里有名字（3）。**

### 二、而三条线索查下来的结果

```
/api/beast        n=0      ← Bstn 自己的消息说 cart 在那儿，而镜像里**零次**
adyen             n=167    ← 整套 Adyen 词汇：AdyenHandler · _adyenEU/UK/JP/AU · Adyen3DS · get_AdyenClientKey
rpc/payment/pay   n=3      ← **三条实名路由**
                             /rpc/payment/pay/initiatePayment
                             /rpc/payment/pay/submitAdyenDetails
                             /rpc/payment/pay/capturePayPalPaymentByChannelTransactionNo
buy/orders        n=0      ← 而 Nike 结账链的**上一步**：零次
```

**→ 两个结论：**
1. **Bstn 那条消息里的 `/api/beast` 是**它自己的**说法，镜像里 0 ⇒ 那条注释本身无据。
   → 而那是一条**待在注释里很久的假线索** —— 它把下一个人指向一个不存在的路径。**
2. **Nike 的付款不是「未取证」**：镜像里有三条实名路由，含 `submitAdyenDetails`。
   → 而 `NikeFlow.SubmitPaymentAsync` 的报告写着「the image names /rpc/payment/pay/initiatePayment」——
   **那句话是对的，而它仍然报告，因为**上一步**（`buy/orders/v2`）是 0。**

### 三、而为什么不现在就把 Nike 的付款接上

**Nike 的结账链是 `SubmitShipping → GetPaymentMethods → SubmitPayment`。
→ 而 `buy/orders/v2`（shipping 那步）在镜像里 **0 次**，`buy/orders` 也 **0 次**。
→ 所以接上 `initiatePayment` 只是把失败点从「payment 未取证」挪到「shipping 未取证」——
→ **那正是 R48 的裁决：「换一个猜测只是移动失败，不是消除失败」。**

**→ 所以本轮**不动代码**：那三条路由被记下来，等 `buy/orders/v2` 有据时它们就是现成的。**

### 四、而本轮还有一件**操作上的**事要记

**轮转三个 publish 目录时，我写的路径校验是：**

```powershell
if (Test-Path $p -and $p -notlike "$root\\.publish-aot*") { ... }
```

**→ PowerShell 需要 `(Test-Path $p) -and ...`，而那个写法**静默失败**（报 NamedParameterNotFound），
→ 于是**校验没跑，而删除与移动照旧执行了。**

**→ 结果是对的（三个路径都由 `(Get-Location)` 构造，本来就对），但那是**运气**，不是校验。
→ 而 AGENTS 那条「删除前先核实解析后的绝对路径」正是为此 —— 校验存在而没执行，比没有校验更坏，
  因为它让人以为检查过了。**

**→ 而验证：`.publish-aot` 19:15（新）· `.publish-aot-prev` 18:55（旧）· 无 `-new` · exe 在。**

### 五、数字

| 度量 | R1041 | R1042 |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| **产物陈旧度** | 1 / 217 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **报告 Unknown 的步骤** | 14 | **14（分成 7+4+3 三种状态）** |
| **`/api/beast` 在镜像里** | 未查 | **0 ⇒ Bstn 那条注释无据** |
| **`adyen` 词汇** | 未查 | **167 条** |
| **Nike 付款路由** | 「0 条」 | **3 条实名** |
| **Nike `buy/orders`** | 未查 | **0 ⇒ 上一步先断** |
| **路径校验是否执行** | — | **否（语法错，静默）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "/api/beast" --limit 600        -> {"n":0}
python analysis/ida.py str "adyen" --limit 600             -> {"n":167}
python analysis/ida.py str "rpc/payment/pay" --limit 600   -> {"n":3}
python analysis/ida.py str "buy/orders" --limit 600        -> {"n":0}
cd replica
Get-ChildItem -Directory -Filter ".publish-aot*"  -> .publish-aot 19:15 · .publish-aot-prev 18:55
python tools/metrics_report.py -> 完整套件 exit 0  2258 / 0 / 0 · 陈旧度 0 / 0
```

### 七、仍然 Unknown

- **`buy/orders/v2` 的真实路由**：待取证（Nike 链的第一步）。
- **Farfetch 的 transport**：无线索。

### 八、教训

**「14 个未知」是一个**计数**，而计数把三种状态压成了一个大数字：
  彻底无线索的 7 个、有候选的 2 个、镜像里有名字的 3 个。**

**→ 而压平之后，那 3 个「其实有名字」的看起来和那 7 个一样无望。**

**→ 所以「未覆盖的每条写为什么」不只是写字 —— 它要求**每条都读一遍消息**，
  因为消息里藏着下一轮能不能动手的全部信息。**

**→ 另一条：`if (Test-Path $p -and ...)` 语法错让校验静默失效而破坏性操作照旧执行。
  校验存在但没跑，比没有校验更坏 —— 它让人以为检查过了。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1042", BLOCKER)
    ensure(RSTATUS, "R1042", BLOCKER)
    ensure(RVERDICT, "第 1042 轮", VERDICT)
    ensure(BACKLOG, "R1042", BACKLOG_ADD)

    note = (
        "\n## R1042 补充 — **14 个 Unknown 分三种状态；Nike 付款有 3 条实名路由；`/api/beast` 无据**（套件 2258）\n\n"
        "**陈旧度 1/217 → 0/0**（publish + 轮转）。\n\n"
        "**三种状态**：Farfetch 7 处**无线索** · Bstn 4 处**有候选**（`/api/beast` · `(Adyen)`）·\n"
        "Nike 3 处**镜像里有名字**。\n\n"
        "**线索结果**：\n"
        "```\n/api/beast       0     ⇒ Bstn 那条注释**无据**（指向不存在的路径）\n"
        "adyen            167   ⇒ AdyenHandler · _adyenEU/UK/JP/AU · Adyen3DS · get_AdyenClientKey\n"
        "rpc/payment/pay  3     ⇒ /initiatePayment · /submitAdyenDetails · /capturePayPalPaymentByChannelTransactionNo\n"
        "buy/orders       0     ⇒ Nike 结账链上一步先断\n```\n\n"
        "**而接线被 R48 挡住**：接 `initiatePayment` 只把失败点挪到 shipping ⇒ 不动代码，三条路由记下备用。\n\n"
        "**操作教训**：`if (Test-Path $p -and ...)` 语法错 ⇒ 校验**静默没跑**，而删除/移动照旧执行。\n"
        "结果对是因为路径由 `(Get-Location)` 构造，不是校验。**「校验存在但没执行」比没有校验更坏。**\n\n"
        "数字：套件 2258/0/0 · 陈旧度 **0/0** · 函数数 174,293 · Unknown 14（7+4+3）· Nike 付款路由 **3** · `buy/orders` **0**。\n\n"
        "纪律：**「未覆盖的每条写为什么」要求每条都读一遍消息 —— 消息里有能不能动手的全部信息。**\n\n"
        "下一轮：`buy/orders/v2`（Nike 链第一步）的真实路由 —— 那是解开 3 个 Unknown 的钥匙。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1042" not in h:
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
             for p, k in ((RBLOCK, "R1042"), (RSTATUS, "R1042"), (RVERDICT, "第 1042 轮"), (BACKLOG, "R1042")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1042: the fourteen unknowns are not equally stuck, and a guard that silently did not run\n\n"
         "R1041's generated table reports fourteen steps with an unknown endpoint. Reading their messages rather than\n"
         " counting them separates three states.\n\n"
         "Farfetch's seven say only that the transport is unknown; there is no lead to follow. Bstn's four carry\n"
         " candidates, one naming a path and one naming Adyen. Nike's three say the image does carry a route name, and\n"
         " they are right -- /rpc/payment/pay has three of them, initiatePayment, submitAdyenDetails and\n"
         " capturePayPalPaymentByChannelTransactionNo. So three of the fourteen are blocked on something other than\n"
         " knowledge of the route.\n\n"
         "Following the leads also disposes of one. /api/beast returns zero, so Bstn's own note -- that the cart lives\n"
         " there -- is unbacked, and has been pointing readers at a path that does not exist. A false lead in a comment is\n"
         " worse than no lead, because it reads like progress.\n\n"
         "Nike's payment is not wired, and R48 gives the reason. Its chain runs shipping, then payment methods, then\n"
         " payment, and buy/orders is zero in every form tried. Wiring initiatePayment would move the failure from payment\n"
         " to shipping rather than remove it. The three routes are recorded instead, ready for whoever establishes the\n"
         " first step.\n\n"
         "The publish cleared freshness to zero. Rotating the three directories exposed something worth recording: my\n"
         " path check was written as a single Test-Path call with a boolean operator, which PowerShell rejects, so the\n"
         " check did not run while the delete and the two moves did. The outcome was correct because the paths were built\n"
         " from the current directory, which is luck rather than verification. A check that exists and does not execute\n"
         " is worse than no check, since it leaves the impression something was confirmed.\n\n"
         "Figures: suite 2258 unchanged, freshness zero for the first time since the last round of source edits, count\n"
         " 174,293, fourteen unknowns now sorted into seven without a lead, two with candidates and three with named\n"
         " routes, plus one comment shown to be unbacked.\n\n"
         "Unknown: the real route behind buy/orders/v2, which is the key to three of the fourteen.\n\n"
         "The lesson is that a count flattens states, and that the messages inside those fourteen steps held every piece\n"
         " of information about which of them could be acted on.\n\n"
         "No code changed; artifact republished; suite green at 2258."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()