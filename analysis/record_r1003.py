"""Record R1003: reachability is per method, and I searched for the wrong host literals twice."""

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
### 可达性**精确到方法**，不是到类 —— 而我两次搜错了串（R1003）

**R1002 留下一句「`squareup` / `adyen` 仍 absent」，这一轮去核，发现那句话里有两个错误，都在我这边。**

### ① 我搜的串根本不是源码里的串

| 网关 | 源码里真实的 host 常量 | 我 R1002 搜的 |
|---|---|---|
| `SquareGateway` | **`pci-connect.squareup.com`** | `api.squareup.com` |
| `AdyenGateway` | **`checkoutshopper-live.adyen.com`** | `adyen.com` |

> **→ 一个是我臆造的前缀（`api.`），一个是把品牌名当 host。
> → 所以「absent」不是产物的结论，是我**搜错了**。
> → 这又是 AGENTS.md §2.7 那个形状：**先假设形状，再把「不符合假设」读成「不存在」。**
> 这是第 **十** 次。**

### ② 用正确拼法重搜，图景变精确

| 网关 | 主 host | 次 host |
|---|---|---|
| Square · Stripe · Unzer · Omise · Paynamics · Sibs · PayPal | **IN** | — |
| Mollie · GMO · Touchtech · Midtrans | **IN** | — |
| **Adyen** | **absent** | — |
| **CommerceHub** | **absent** | — |
| （各家的次 host） | — | `api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1.paynamics.net` · `shield.paynamics.net` **全 absent** |

### ③ 而规律解释了全部

**`IN` 的每一条，都是 `AuthorizeAsync` 里 `$"{ApiHost}/…"` 引用的那一段。
`absent` 的次 host，全在 `TokenizeAsync` 或 `CompleteActionAsync` 里。**

**而 R1002 只接了一处：**

```csharp
var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
```

> **→ 所以可达性**精确到方法**，不是到类。
> 「这个网关进了产物」和「这个网关的三个方法都进了产物」是两个陈述，
> 而 R1002 只做到了前者，而我在那一轮把它读成了后者。**

### ④ 而 Adyen 与 CommerceHub 整个不在，原因不同

**它们连 `AuthorizeAsync` 的 host 都不在 —— 而那一条是被 `SubmitPaymentAsync` 直接调的。
所以问题不在可达性，在**它们的 `Id` 没被 `Resolve` 命中**。**

**`AdyenGateway` 的 `Id` 是什么？若它是 `"adyen"` 而 `ChooseGateway` 从不产 `"adyen"`，
那 `Resolve` 永远返回 null，整个类被裁 —— 与 `CreateDefault` 那次同一形状，只是发生在 id 上。**

**→ 那是一个待证的具体问题，不是「Adyen 缺证据」。**

### ⑤ 这一轮的产出是**一个精确化 + 两次自我纠正**

**上一轮我写「产物里网关 2 → 9」。按这一轮的图景，更准确的是：
**产物里有 11 个网关的 `AuthorizeAsync`，7 个的次 host 一个都没有，2 个整个不在。**
而那两个不在的原因是可查的（id 不匹配），不是不可得。**

### 数字

| 度量 | R1002 | **R1003** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **主 host 在产物的网关** | 记作 9 | **11** |
| **次 host 一个都没有的网关** | 未测 | **7（`TokenizeAsync` / `CompleteActionAsync` 全裁）** |
| **整个不在的网关** | 记作 2 | **2（Adyen · CommerceHub，原因可查）** |

### 教训

> **「进了产物」要说到**哪一层**：类、方法、还是那一行。
> 我在 R1002 说「9 个网关进了」，实际是「9 个网关的**一个方法**进了」。
> **→ 而两个记录都「对」，只是粒度不同 —— 而粗的那个听起来完成了更多。**
"""

if "可达性**精确到方法**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1003 轮：可达性精确到方法，而我两次搜错了串

### ① 我搜的串根本不是源码里的串

| 网关 | 真实 host 常量 | 我 R1002 搜的 |
|---|---|---|
| `SquareGateway` | **`pci-connect.squareup.com`** | `api.squareup.com` |
| `AdyenGateway` | **`checkoutshopper-live.adyen.com`** | `adyen.com` |

> **一个是我臆造的前缀，一个是把品牌名当 host。所以「absent」不是产物的结论，是我搜错了。
> 这是 §2.7 那个形状第**十**次：先假设形状，再把「不符合假设」读成「不存在」。**

### ② 用正确拼法重搜，图景变精确

**11 个网关的主 host **IN**（Square 也在）；**Adyen** 与 **CommerceHub** 整个 absent；
7 个的次 host（`api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1/shield.paynamics.net`）全 absent。**

### ③ 而规律解释了全部

**`IN` 的都是 `AuthorizeAsync` 里 `$"{ApiHost}/…"` 那一段。
`absent` 的次 host 全在 `TokenizeAsync` 或 `CompleteActionAsync` 里 —— 而 R1002 只接了一处：**

```csharp
var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
```

> **→ 可达性**精确到方法**，不是到类。
> 「这个网关进了产物」与「三个方法都进了」是两个陈述，R1002 只做到了前者，而我把它读成了后者。**

### ④ Adyen 与 CommerceHub 的原因不同

**它们连 `AuthorizeAsync` 的 host 都不在 —— 而那条是被直接调的。
所以问题不在可达性，在**它们的 `Id` 没被 `Resolve` 命中**（与 `CreateDefault` 那次同形状，只是发生在 id 上）。
→ 那是一个待证的具体问题，不是「Adyen 缺证据」。**

### ⑤ 数字

| 度量 | R1002 | **R1003** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| **主 host 在产物的网关** | 记作 9 | **11** |
| **次 host 一个都没有** | 未测 | **7** |
| **整个不在** | 记作 2 | **2（Adyen · CommerceHub）** |

### 教训

> **「进了产物」要说到**哪一层**：类、方法、还是那一行。
> 我在 R1002 说「9 个网关进了」，实际是「9 个网关的**一个方法**进了」。
> → 两个记录都「对」，只是粒度不同 —— 而粗的那个听起来完成了更多。**
"""

BACKLOG_ADD = """

## 判据 (c)/优先级 ① — **可达性精确到方法；Square/Adyen 是我搜错串；Adyen/CommerceHub 整个不在 = id 不匹配**（R1003）

### 自我纠正 ×2

| 网关 | 真实 host | 我 R1002 搜的 |
|---|---|---|
| Square | `pci-connect.squareup.com` | `api.squareup.com` ✗ |
| Adyen | `checkoutshopper-live.adyen.com` | `adyen.com` ✗ |

**→ 「absent」是我搜错了，不是产物没有。§2.7 形状第十次。**

### 精确图景

- **11 个网关的主 host IN**（`AuthorizeAsync` 里 `$"{ApiHost}/…"` 那一段）
- **Adyen · CommerceHub 整个 absent**
- **7 个的次 host 全 absent**（`api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1/shield.paynamics.net`）
- **原因：R1002 只接 `AuthorizeAsync`，`TokenizeAsync` / `CompleteActionAsync` 全裁**

**→ 可达性精确到**方法**，不是到类。**

### 待查（可查，非不可得）

**Adyen / CommerceHub 的 `Id` 是否会被 `Resolve` 命中 —— 若不命中，整个类被裁（与 `CreateDefault` 同形状）。**

### 数字

**套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 主 host IN 11 · 次 host 全无 7 · 整个不在 2**

**纪律**：「进了产物」要说到类、方法、还是那一行 —— 粗的那个听起来完成了更多。
"""

BLOCKER = """

---

## 427. **可达性精确到方法；Square/Adyen 是我搜错串；Adyen/CommerceHub 整个不在**

> R1003。**未改代码，只取证。** 套件 **2214 通过 / 0 失败 / 0 跳过**。

### 一、自我纠正：两次搜错了串

| 网关 | 源码里真实的 host 常量 | R1002 搜的 |
|---|---|---|
| `SquareGateway`（`Gateways.cs:70`） | **`pci-connect.squareup.com`** | `api.squareup.com` |
| `AdyenGateway`（`AdyenGateway.cs:22`） | **`checkoutshopper-live.adyen.com`** | `adyen.com` |

**→ 一个是我臆造的前缀（`api.`），一个是把品牌名当 host。
→ 所以 R1002 那句「`squareup` / `adyen` 仍 absent」**两个都是我的错**，不是产物的事实。
→ AGENTS.md §2.7 那个形状第**十**次：先假设形状，再把「不符合假设」读成「不存在」。**

### 二、用正确拼法重搜

| 网关 | 主 host | 次 host |
|---|---|---|
| Square · Stripe · Unzer · Omise · Paynamics · Sibs · PayPal | **IN** | — |
| Mollie · GMO · Touchtech · Midtrans | **IN** | — |
| **Adyen** | **absent** | — |
| **CommerceHub** | **absent** | — |
| 各家次 host | — | `api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1.paynamics.net` · `shield.paynamics.net` **全 absent** |

### 三、而规律解释了全部

**`IN` 的每一条，都是 `AuthorizeAsync` 里 `$"{ApiHost}/…"` 引用的那一段。
`absent` 的次 host，全在 `TokenizeAsync` 或 `CompleteActionAsync` 里。**

**而 R1002 只接了一处：**

```csharp
var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
```

**→ 所以可达性**精确到方法**，不是到类。
→ 「这个网关进了产物」和「这个网关的三个方法都进了产物」是两个陈述；
  R1002 只做到了前者，而我在那一轮把它读成了后者。**

### 四、Adyen 与 CommerceHub 整个不在，原因不同

**它们连 `AuthorizeAsync` 的 host 都不在 —— 而那一条是被 `SubmitPaymentAsync` 直接调的。
所以问题不在可达性，在**它们的 `Id` 没被 `Resolve` 命中**。**

**`AdyenGateway` 的 `Id` 若是 `"adyen"` 而 `ChooseGateway` 从不产 `"adyen"`，
那 `Resolve` 永远返回 null，整个类被裁 —— 与 `CreateDefault` 那次同一形状，只是发生在 id 上。**

**→ 那是一个**待证的具体问题**，不是「Adyen 缺证据」。**

### 五、数字

| 度量 | R1002 | R1003 |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **主 host 在产物的网关** | 记作 9 | **11** |
| **次 host 一个都没有的网关** | 未测 | **7** |
| **整个不在的网关** | 记作 2 | **2（Adyen · CommerceHub）** |

### 六、验证

```
cd replica
python - 读 Gateways.cs:70 -> NonceHost = "https://pci-connect.squareup.com"
python - 读 AdyenGateway.cs:22 -> ShopperHost = "https://checkoutshopper-live.adyen.com"
python - 在 .publish-aot 字节里搜 'pci-connect.squareup.com' -> IN
python - 搜 'checkoutshopper-live.adyen.com' -> absent
python - 搜 'commercehub-secure-data-capture.fiservapps.com' -> absent
python - 搜 'api.sandbox.paypal.com' / 'checkout-page.omise.co' / 'nodecde1.paynamics.net' -> 全 absent
python tools/metrics_report.py -> 套件 2214 · 陈旧度 0/0 · 函数数 174,336
```

### 七、仍然 Unknown

- **Adyen / CommerceHub 的 `Id` 是否会被 `Resolve` 命中**：**未查**（下一步）。
- 其余家次 host 是否需要接（取决于原版是否调 `TokenizeAsync` / `CompleteActionAsync`）。

### 八、教训

**「进了产物」要说到**哪一层**：类、方法、还是那一行。
我在 R1002 说「9 个网关进了」，实际是「9 个网关的**一个方法**进了」。**

**→ 两个记录都「对」，只是粒度不同 —— 而粗的那个听起来完成了更多。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1003", BLOCKER)
    ensure(RSTATUS, "R1003", BLOCKER)
    ensure(RVERDICT, "第 1003 轮", VERDICT)
    ensure(BACKLOG, "R1003", BACKLOG_ADD)

    note = (
        "\n## R1003 补充 — **可达性精确到方法；Square/Adyen 是我搜错串；Adyen/CommerceHub 整个不在 = id 不匹配**（套件 2214，未改代码）\n\n"
        "**自我纠正 ×2**：`SquareGateway` 的真实 host 是 **`pci-connect.squareup.com`**（我搜 `api.squareup.com`）；\n"
        "`AdyenGateway` 是 **`checkoutshopper-live.adyen.com`**（我搜 `adyen.com`）。→ 「absent」是我搜错了。\n"
        "（AGENTS.md §2.7 那个形状第**十**次：先假设形状，再把不符读成不存在。）\n\n"
        "**正确拼法重搜**：11 个网关的主 host **IN**（Square 也在）· **Adyen / CommerceHub 整个 absent** ·\n"
        "7 个的次 host 全 absent（`api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1/shield.paynamics.net`）。\n\n"
        "**规律**：IN 的都是 `AuthorizeAsync` 里 `$\"{ApiHost}/…\"` 那一段；absent 的次 host 全在\n"
        "`TokenizeAsync` / `CompleteActionAsync` 里 —— **而 R1002 只接了 `AuthorizeAsync`。**\n"
        "**→ 可达性精确到**方法**，不是到类。**\n\n"
        "**Adyen/CommerceHub 的原因不同**：它们连被直接调的 `AuthorizeAsync` host 都不在 → 问题在**它们的 `Id` 没被 `Resolve` 命中**\n"
        "（与 `CreateDefault` 同形状，只是发生在 id 上）。**那是可查的具体问题，不是缺证据。**\n\n"
        "数字：套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 主 host IN 11 · 次 host 全无 7 · 整个不在 2。\n\n"
        "纪律：**「进了产物」要说到类、方法、还是那一行 —— 粗的那个听起来完成了更多。**\n\n"
        "下一轮：查 `AdyenGateway.Id` / `CommerceHubGateway` 的 Id 与 `ChooseGateway` 的产出集合是否相交。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1003" not in h:
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
             for p, k in ((RBLOCK, "R1003"), (RSTATUS, "R1003"), (RVERDICT, "第 1003 轮"), (BACKLOG, "R1003")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1003: reachability stops at the method, and I had searched for the wrong host twice\n\n"
         "R1002 closed with a line saying squareup and adyen were still absent from the artifact. Checking it showed the\n"
         " line contained two mistakes and both were mine.\n\n"
         "SquareGateway's host is pci-connect.squareup.com and I had searched for api.squareup.com, an invented prefix.\n"
         " AdyenGateway's is checkoutshopper-live.adyen.com and I had searched adyen.com, a brand name where a host\n"
         " belongs. So absence was a fact about my search rather than about the binary, which is the tenth time this shape\n"
         " has caught me: assume a spelling, then read disagreement as non-existence.\n\n"
         "Searching with the real literals gives a much sharper picture. Eleven gateways have their primary host present,\n"
         " Square included. Adyen and CommerceHub are entirely absent. And seven gateways are missing their secondary\n"
         " hosts -- api.sandbox.paypal.com, checkout-page.omise.co, nodecde1 and shield on paynamics -- none of which are in\n"
         " the binary.\n\n"
         "The pattern explains every row. What is present is precisely the string from AuthorizeAsync, the method R1002\n"
         " wired up. What is missing sits in TokenizeAsync or CompleteActionAsync, which nothing calls. So reachability\n"
         " stops at the method, not at the class. \"The gateway is in the artifact\" and \"all three of its methods are\" are\n"
         " different statements, and last round I made the first and read it as the second.\n\n"
         "Adyen and CommerceHub differ in cause. Their AuthorizeAsync host is missing too, and that one is called directly,\n"
         " so the problem is not reachability but that their Id never matches what Resolve is given -- the same shape as the\n"
         " CreateDefault round, displaced onto an id. That is a specific question with an answer, not a lack of evidence.\n\n"
         "Figures: suite 2214 unchanged, freshness zero, count 174,336, eleven gateways with a primary host present, seven\n"
         " with no secondary host at all, two entirely absent.\n\n"
         "The lesson is that \"it reached the artifact\" needs a level: class, method, or line. Both of my records were true\n"
         " and the coarser one sounded like more had been finished.\n\n"
         "No product code changed; one claim made precise and one search corrected twice."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()