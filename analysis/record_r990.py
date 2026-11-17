"""Record R990: the six uncovered payment hosts split two ways, and one of them hides a fabricated token."""

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
### 那 6 条未覆盖分成两类，而其中一条藏着**伪造的支付令牌**（R990）

**R989 说下一轮核那 6 个支付网关是否真缺。核了，而答案不是「缺」或「不缺」——是**三种**。**

### ① 先确认真缺：它们不在源码里

```
where_is midtrans / gpayments / mollie / cybersource / touchtech / airwallex
  -> 各 2 个文件，而两个都是 docs\\VERDICT.md 与 docs\\BINDING_BACKLOG.md
```

**而 `core_coverage` 的 `all_src` 只走 `replica/src`。
→ 这 6 个在**源码**里确实一次都没出现，`unmatched` 是准确的。**

### ② 而它们各自的原版路径拿到了（来自二进制清单 `analysis/.coverage-paths.txt`）

| host | 路径 | 性质 |
|---|---|---|
| `app.midtrans.com` | `/snap/v1/transactions` · `/snap/v2/transactions` | 收单会话创建 |
| `degica.as1.gpayments.net` | `/api/v2/brw/info/result?transId=` | 结果查询 |
| `ecommerce-gateway.mollie.com` | `/api/v1/public/core/payments/poll` | 支付状态轮询 |
| `flex.cybersource.com` | `/flex/v2/tokens` | **令牌化** |
| `retry.touchtechpayments.com` | `/api/v1/:select` | 支付选择 |
| `threeds.airwallex.com` | `/api/v1/pa/gateway/hk/three-ds-method/redirect` | **3DS 重定向** |

### ③ 第一类：**泛化步骤覆盖了它，而指标在原理上看不见**

**3DS 在复刻件里是泛化的：**

```csharp
Solve3DSAsync         → c.Session.ThreeDsUrl = adyen.threeDSMethodUrl   // URL 来自 paymentData
Solve3DSRedirectAsync → GetAsync(c.Session.ThreeDsUrl) → 从 HTML 提取 transStatus
Handle3DSAsync        → 按 transStatus 判 Y / 其他
```

> **Airwallex 的 `three-ds-method/redirect` 被这条链覆盖 —— 而 URL 是**运行期**从 paymentData 读出来的，
> 所以 host 名永远不会写进源码。**
> **→ `matched` 测的是「host 名出现在源码里」，而**泛化步骤不写 host 名**。
> 这是覆盖率指标的结构性盲区，不是复刻件的缺陷。**

### ④ 第二类：**该调用的端点被一个伪造值代替了** —— 这是缺陷

```csharp
public virtual async Task<StepOutcome> GetPaymentTokenAsync(FlowContext c, CancellationToken ct)
{
    if (!string.IsNullOrEmpty(c.Session.PaymentToken)) return StepOutcome.Success();
    c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];   // ← 不调任何端点
    c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
    return StepOutcome.Success();
}
```

> **它不请求 `flex.cybersource.com/flex/v2/tokens`，而是**造一个随机 GUID 当支付令牌**。**
> **而 `ShopifyFlow.GetCsrf` 的注释明确写着 R823 的结论：
> 「不编造 fallback —— 服务器从未签发的令牌会让每个带它的请求被判无效」。**
> **`GetPaymentTokenAsync` 做的**正是那件被明令禁止的事**，而且它在**支付**路径上。**
> **→ 所以 Cybersource 那一条不是「名字没出现」，是「该调的端点被伪造值顶掉了」。**

**而 `HISTORY.md` 的 R12 表里还有一处同样的形状：「令牌 | `GetToken` | 16 字节 CSPRNG hex」。**

### ⑤ 第三类：真缺，且没有泛化路径

**`midtrans` / `gpayments` / `mollie` / `touchtech` —— 收单会话、结果查询、状态轮询、支付选择，
四者都是**host 专属**的端点，没有泛化步骤能覆盖它们。**

**→ 这四条是优先级 ① 的真缺口，而它们各自属于哪个 flow，尚未取证。**

### ⑥ 所以判据 (f) 的 6 条现在可以逐条写「为什么」

| # | 未覆盖 | 为什么 |
|---|---|---|
| 1 | `threeds.airwallex.com` | **泛化覆盖**（`Solve3DSRedirectAsync` 跟随运行期 URL）—— 指标盲区，非缺陷 |
| 2 | `flex.cybersource.com` | **被伪造令牌顶掉** —— `GetPaymentTokenAsync` 造 GUID 而不调用 |
| 3–6 | `midtrans` · `gpayments` · `mollie` · `touchtech` | **真缺**，host 专属端点，无泛化路径 |

### 数字

| 度量 | R989 | **R990** |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| vendor unmatched | 6 | **6（但分成了 1 盲区 / 1 伪造 / 4 真缺）** |
| **伪造的支付令牌** | 未测 | **1 处函数 + 1 处 `GetToken`** |

### 教训

> **「未覆盖」是一个**混合类别**：里面有「做不到」「没做」「做了但指标看不见」「做了个假的」。
> 而它们在这张表里长得一模一样 —— 都叫 `unmatched`。**
> **如果我只按这一个词去补，我会去写六个支付网关客户端，而其中一个的活儿已经干完了（只是指标看不见），
> 另一个的活儿是**先把自己伪造的那个值删掉**。**
"""

if "那 6 条未覆盖分成两类" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 990 轮：6 条未覆盖分成三类，其中一条藏着伪造的支付令牌

### ① 先确认真不在源码里

```
where_is midtrans/gpayments/mollie/cybersource/touchtech/airwallex
  -> 各 2 个文件，两个都是 docs\\VERDICT.md 与 docs\\BINDING_BACKLOG.md
```

**`core_coverage` 的 `all_src` 只走 `replica/src` → 这 6 个在源码里确实没出现，`unmatched` 准确。**

### ② 原版路径（来自 `analysis/.coverage-paths.txt`）

| host | 路径 | 性质 |
|---|---|---|
| `app.midtrans.com` | `/snap/v1/transactions` · `/snap/v2/transactions` | 收单会话 |
| `degica.as1.gpayments.net` | `/api/v2/brw/info/result?transId=` | 结果查询 |
| `ecommerce-gateway.mollie.com` | `/api/v1/public/core/payments/poll` | 状态轮询 |
| `flex.cybersource.com` | `/flex/v2/tokens` | **令牌化** |
| `retry.touchtechpayments.com` | `/api/v1/:select` | 支付选择 |
| `threeds.airwallex.com` | `/api/v1/pa/gateway/hk/three-ds-method/redirect` | **3DS 重定向** |

### ③ 第一类：泛化覆盖，指标看不见

```csharp
Solve3DSAsync         → c.Session.ThreeDsUrl = adyen.threeDSMethodUrl
Solve3DSRedirectAsync → GetAsync(c.Session.ThreeDsUrl) → 提取 transStatus
Handle3DSAsync        → 按 transStatus 判 Y / 其他
```

> **Airwallex 的 3DS 重定向被这条链覆盖，而 URL 是**运行期**读的 → host 名永不写进源码。
> `matched` 测的是「名字出现在源码里」，而泛化步骤不写名字。**指标的结构性盲区，不是缺陷。****

### ④ 第二类：该调的端点被伪造值顶掉 —— 这是缺陷

```csharp
c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];   // 不调任何端点
```

> **它不请求 `flex.cybersource.com/flex/v2/tokens`，而是造一个随机 GUID 当令牌。
> 而 `ShopifyFlow.GetCsrf` 的注释明确写着 R823：「不编造 fallback ——
> 服务器从未签发的令牌会让每个带它的请求被判无效」。
> `GetPaymentTokenAsync` 做的正是被明令禁止的事，而且在**支付**路径上。**
> **`HISTORY.md` 的 R12 表里还有一处同形：「`GetToken` | 16 字节 CSPRNG hex」。**

### ⑤ 第三类：真缺，无泛化路径

**`midtrans` / `gpayments` / `mollie` / `touchtech` —— 收单会话、结果查询、状态轮询、支付选择，
都是 host 专属端点。这四条是优先级 ① 的真缺口，各自属于哪个 flow 尚未取证。**

### ⑥ 判据 (f) 的 6 条现在能逐条写「为什么」

| # | 未覆盖 | 为什么 |
|---|---|---|
| 1 | `threeds.airwallex.com` | **泛化覆盖**（运行期 URL）—— 指标盲区，非缺陷 |
| 2 | `flex.cybersource.com` | **被伪造令牌顶掉** |
| 3–6 | `midtrans` · `gpayments` · `mollie` · `touchtech` | **真缺**，host 专属 |

### 数字

| 度量 | R989 | **R990** |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| vendor unmatched | 6 | **6（1 盲区 / 1 伪造 / 4 真缺）** |
| **伪造的支付令牌** | 未测 | **1 处函数 + 1 处 `GetToken`** |

### 教训

> **「未覆盖」是**混合类别**：「做不到」「没做」「做了但指标看不见」「做了个假的」都叫 `unmatched`。
> 只按这一个词去补，会写六个支付网关客户端 —— 而其中一个的活儿已经干完（指标看不见），
> 另一个的活儿是**先把自己伪造的那个值删掉**。**
"""

BACKLOG_ADD = """

## 判据 (f)/优先级 ① — **6 条未覆盖分类：1 指标盲区 · 1 伪造令牌 · 4 真缺**（R990）

### 分类

| # | host | 为什么 | 性质 |
|---|---|---|---|
| 1 | `threeds.airwallex.com` | `Solve3DSRedirectAsync` 跟随运行期 URL，host 名不写进源码 | **指标盲区** |
| 2 | `flex.cybersource.com` | `GetPaymentTokenAsync` 造 GUID 而不调 `/flex/v2/tokens` | **伪造令牌（违反 R823）** |
| 3 | `app.midtrans.com` | `/snap/v1|v2/transactions` 收单会话 | 真缺 |
| 4 | `degica.as1.gpayments.net` | `/api/v2/brw/info/result` 结果查询 | 真缺 |
| 5 | `ecommerce-gateway.mollie.com` | `/payments/poll` 状态轮询 | 真缺 |
| 6 | `retry.touchtechpayments.com` | `/api/v1/:select` 支付选择 | 真缺 |

### 伪造令牌的确切形状

```csharp
// src/Cybersole.Stores/Flows/StoreFlow.cs:1151
c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];
```

**而 `ShopifyFlow.GetCsrf` 的注释写着 R823：「不编造 fallback —— 服务器从未签发的令牌会让每个带它的请求被判无效」。**
**同形第二处：`HISTORY.md` R12 表「`GetToken` | 16 字节 CSPRNG hex」。**

### 数字

**套件 2205（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 未覆盖 6 = 1 盲区 / 1 伪造 / 4 真缺**

| 仍 Unknown | |
|---|---|
| 4 条真缺各属于哪个 flow | 未取证 |
| `GetPaymentTokenAsync` 有无 override 真的调端点 | 未核（virtual，各 flow 可覆写） |

**纪律**：「未覆盖」是混合类别 —— 做不到 / 没做 / 指标看不见 / 做了个假的，四者同名。
"""

BLOCKER = """

---

## 414. **6 条未覆盖分类：1 指标盲区 · 1 伪造令牌 · 4 真缺**

> R990。**只取证，未改代码。** 套件 **2205（R989 的记录仍有效）**。

### 一、先确认真不在源码里

```
where_is midtrans / gpayments / mollie / cybersource / touchtech / airwallex
  -> 各 2 个文件，两个都是 docs\\VERDICT.md 与 docs\\BINDING_BACKLOG.md
```

**`core_coverage` 的 `all_src` 只走 `replica/src` → 这 6 个在**源码**里确实一次都没出现，
`unmatched` 是准确的。**

### 二、原版路径（`analysis/.coverage-paths.txt`，154 条路径的清单）

| host | 路径 | 性质 |
|---|---|---|
| `app.midtrans.com` | `/snap/v1/transactions` · `/snap/v2/transactions` | 收单会话创建 |
| `degica.as1.gpayments.net` | `/api/v2/brw/info/result?transId=` | 结果查询 |
| `ecommerce-gateway.mollie.com` | `/api/v1/public/core/payments/poll` | 支付状态轮询 |
| `flex.cybersource.com` | `/flex/v2/tokens` | **令牌化** |
| `retry.touchtechpayments.com` | `/api/v1/:select` | 支付选择 |
| `threeds.airwallex.com` | `/api/v1/pa/gateway/hk/three-ds-method/redirect` | **3DS 重定向** |

### 三、第一类：泛化覆盖，指标看不见

```csharp
Solve3DSAsync         → c.Session.ThreeDsUrl = adyen.threeDSMethodUrl
Solve3DSRedirectAsync → GetAsync(c.Session.ThreeDsUrl) → 从 HTML 提取 transStatus
Handle3DSAsync        → 按 transStatus 判 Y / 其他
```

**→ Airwallex 的 3DS 重定向被这条链覆盖，而 URL 是**运行期**从 paymentData 读的，
所以 host 名永远不会写进源码。
→ `matched` 测的是「host 名出现在源码里」，而**泛化步骤不写 host 名**。
→ **这是覆盖率指标的结构性盲区，不是复刻件的缺陷。****

### 四、第二类：该调用的端点被伪造值顶掉 —— 这是缺陷

```csharp
// src/Cybersole.Stores/Flows/StoreFlow.cs:1146-1154
public virtual async Task<StepOutcome> GetPaymentTokenAsync(FlowContext c, CancellationToken ct)
{
    if (!string.IsNullOrEmpty(c.Session.PaymentToken)) return StepOutcome.Success();
    c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];   // ← 不调任何端点
    c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
    return StepOutcome.Success();
}
```

**→ 它不请求 `flex.cybersource.com/flex/v2/tokens`，而是**造一个随机 GUID 当支付令牌**。
→ 而 `ShopifyFlow.GetCsrf` 的注释明确写着 R823 的结论：
「不编造 fallback —— 服务器从未签发的令牌会让每个带它的请求被判无效」。
→ **`GetPaymentTokenAsync` 做的**正是那件被明令禁止的事**，而且它在**支付**路径上。
→ `HISTORY.md` 的 R12 表里还有一处同形：「令牌 | `GetToken` | 16 字节 CSPRNG hex」。**

### 五、第三类：真缺，且无泛化路径

**`midtrans` · `gpayments` · `mollie` · `touchtech` —— 收单会话、结果查询、状态轮询、支付选择，
四者都是 host 专属端点，没有泛化步骤能覆盖。
→ 这四条是优先级 ① 的真缺口；各自属于哪个 flow，本轮未取证。**

### 六、判据 (f) 的 6 条现在能逐条写「为什么」

| # | 未覆盖 | 为什么 |
|---|---|---|
| 1 | `threeds.airwallex.com` | **泛化覆盖**（`Solve3DSRedirectAsync` 跟随运行期 URL）—— 指标盲区，非缺陷 |
| 2 | `flex.cybersource.com` | **被伪造令牌顶掉** —— `GetPaymentTokenAsync` 造 GUID 而不调用 |
| 3–6 | `midtrans` · `gpayments` · `mollie` · `touchtech` | **真缺**，host 专属端点，无泛化路径 |

### 七、数字

| 度量 | R989 | R990 |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| vendor unmatched | 6 | **6（1 盲区 / 1 伪造 / 4 真缺）** |
| **伪造的支付令牌** | 未测 | **1 处函数 + 1 处 `GetToken`** |

### 八、验证

```
cd replica
python tools/where_is.py mollie         -> 2 个文件，均 docs/
python - 读 analysis/.coverage-paths.txt 里六个 host 的路径
python - 读 src/Cybersole.Stores/Flows/StoreFlow.cs:1146 与 1572-1597
```

### 九、仍然 Unknown

- **4 条真缺各属于哪个 flow**：**Unknown** —— 未取证。
- **`GetPaymentTokenAsync` 有无 override 真的调端点**：**Unknown** —— 它是 `virtual`，各 flow 可覆写；本轮未逐个核。

### 十、教训

**「未覆盖」是一个**混合类别**：里面有「做不到」「没做」「做了但指标看不见」「做了个假的」。
而它们在这张表里长得一模一样 —— 都叫 `unmatched`。**

**只按这一个词去补，我会写六个支付网关客户端 —— 而其中一个的活儿已经干完了（只是指标看不见），
另一个的活儿是**先把自己伪造的那个值删掉**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R990", BLOCKER)
    ensure(RSTATUS, "R990", BLOCKER)
    ensure(RVERDICT, "第 990 轮", VERDICT)
    ensure(BACKLOG, "R990", BACKLOG_ADD)

    note = (
        "\n## R990 补充 — **6 条未覆盖分类：1 指标盲区 · 1 伪造令牌 · 4 真缺**（套件 2205，未改代码）\n\n"
        "核 R989 的 6 个支付网关：`where_is` 显示它们只在 `docs/VERDICT.md` 与 `docs/BINDING_BACKLOG.md`，\n"
        "而 `core_coverage` 的 `all_src` 只走 `replica/src` → `unmatched` 准确。\n\n"
        "**而六条分成三类：**\n"
        "1. `threeds.airwallex.com` —— **指标盲区**：`Solve3DSRedirectAsync` 跟随**运行期** URL（来自 paymentData），\n"
        "   host 名永不写进源码。泛化步骤覆盖率工具看不见。\n"
        "2. `flex.cybersource.com` —— **被伪造值顶掉**：`StoreFlow.cs:1151`\n"
        "   `c.Session.PaymentToken = \"tok_\" + Guid.NewGuid()...` **不调任何端点**。\n"
        "   而 `ShopifyFlow.GetCsrf` 的注释写着 R823：「不编造 fallback —— 服务器未签发的令牌会让每个带它的请求被判无效」。\n"
        "   同形第二处：`HISTORY.md` R12 表「`GetToken` | 16 字节 CSPRNG hex」。\n"
        "3. `midtrans` / `gpayments` / `mollie` / `touchtech` —— **真缺**（收单会话 / 结果查询 / 状态轮询 / 支付选择）。\n\n"
        "数字：套件 2205（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 未覆盖 6 = 1/1/4。\n\n"
        "纪律：**「未覆盖」是混合类别 —— 做不到 / 没做 / 指标看不见 / 做了个假的，四者同名。**\n\n"
        "下一轮：删掉 `GetPaymentTokenAsync` 的伪造令牌并让它调 `/flex/v2/tokens`（或写成显式 Fail + 原因），\n"
        "同时核有无 override 真的调了端点。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R990" not in h:
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
             for p, k in ((RBLOCK, "R990"), (RSTATUS, "R990"), (RVERDICT, "第 990 轮"), (BACKLOG, "R990")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R990: the six uncovered payment hosts are three different things, and one hides a fabricated token\n\n"
         "R989 left six vendor hosts unmatched and the instruction to find out whether the replica really lacks them.\n"
         " where_is shows each name in two files and both are docs, while the coverage tool searches only replica/src, so\n"
         " the unmatched verdict is accurate: none of the six appears anywhere in the source.\n\n"
         "Their original paths come from the 154-entry inventory the binary yielded, and they split three ways.\n\n"
         "Airwallex is not missing. Three-DS handling in the replica is generic: Solve3DSAsync takes the method URL from the\n"
         " payment data, Solve3DSRedirectAsync follows it and reads transStatus out of the returned form, and Handle3DSAsync\n"
         " classifies the result. The URL arrives at runtime, so the host name is never written down, and a coverage measure\n"
         " that looks for host names cannot see the handling at all. That is a blind spot of the measure, not a gap in the\n"
         " replica.\n\n"
         "Cybersource is worse than missing. GetPaymentTokenAsync does not call flex.cybersource.com/flex/v2/tokens; it\n"
         " assigns a fresh GUID prefixed with tok_ and returns success. That is precisely what the comment on Shopify's\n"
         " GetCsrf forbids, with round 823's reasoning attached: a token the server never issued makes every request\n"
         " carrying it invalid. The same shape appears a second time in the round 12 summary as GetToken generating sixteen\n"
         " random bytes. So there are two places where the replica invents a credential instead of obtaining one, and this\n"
         " one sits on the payment path.\n\n"
         "The remaining four -- Midtrans session creation, GMO result lookup, Mollie polling and Touchtech selection -- are\n"
         " genuinely absent and host-specific, with no generic step that could stand in.\n\n"
         "So criterion (f)'s six uncovered rows can now each say why: one invisible to the measure, one displaced by a\n"
         " fabricated value, four really missing. Had I repaired them by the label alone I would have written six payment\n"
         " clients, one of which already exists, and one of which needed a deletion before any client.\n\n"
         "Figures: suite 2205 unchanged, freshness zero, count 173,952, six uncovered split one blind spot, one fabricated,\n"
         " four absent.\n\n"
         "Unknown: which flows carry the four absent endpoints, and whether any flow overrides GetPaymentTokenAsync with a\n"
         " call that does reach the network.\n\n"
         "No product code changed this round; the defect is recorded with its exact location."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()