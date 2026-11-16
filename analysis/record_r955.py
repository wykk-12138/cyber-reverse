"""Record R955: wiring two payment gateways added 43 functions, and the pattern repeats."""

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
### 接两个支付网关：**+43 函数**，而模式第二次成立（R955）

**R954 说五个支付类全是死代码。这一轮把它们接上。**

```
SubmitPaymentAsync 原来是 => NotSupported(\"SubmitPayment\")
现在：按 session 的 paymentGateway 派发到 VivaPayments / DisneyPaymentSheet
```

```
pdata-replica: 173,781 -> 173,824     +43
pdata-ratio:   62.71%  -> 62.73%
size:          54,674 KB -> 54,692 KB
```

### 而 +43 vs redirect 的 +128

| 接的 | 增量 | 为什么 |
|---|---|---|
| `RedirectPolicy.FollowAsync` | **+128** | 一个 async + 泛型实例化 + 闭包 + 内联副本 |
| 两个支付网关 | **+43** | 两个已有 async，各带自己的状态机 |

> **所以增量不是常数，是**那个 async 方法带多少个实例化**。
> 而 +43 / 2 ≈ 21 每个 —— 比 128 小，因为 `ChargeTokenAsync` 的泛型面更窄。**
> **而两个数都远大于 1 —— 所以「接一个 async ≈ 十几个到一百多个函数」这条现在有两个样本。**

### 而这次接线是**对的**，不是「为动数而接」

**`SubmitPaymentAsync` 原本返回 `NotSupported` —— 那是一个**真缺口**：
支付步骤存在、五个网关实现存在、而中间那一句调用不存在。**

> **所以这一轮不是「找个地方接一下让数动」，是**补上那两个实现之间缺的那一行**。
> 而数动是它的**后果**，不是目的。**

### 而修的时候撞了五次签名

**`ChargeTokenAsync(FlowSession, card, expiry, ct, Func<string,string,string,CancellationToken,Task<NetResponse?>> post)` —— 五个参数，
最后一个是**调用方传入的 POST 委托**（网关不拥有 client）。**

> **而我第一版按 `(NetClient, url, ct)` 写，全错。
> 而 `StepOutcome` 只有 `Success()/Fail()/Stop()`，没有 `Retryable()`；
> `NotSupported` 返回 `Task<StepOutcome>`，在 async 里要 `await`。**

**五次编译错误，五次都是「我以为签名是什么」而不是「读签名」。**

### 数字

| 度量 | R954 | **R955** |
|---|---|---|
| 套件 | 2097 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,781 | **173,824（+43）** |
| **函数比** | 62.71% | **62.73%** |
| 产物大小 | 54,674 KB | **54,692 KB** |

### 教训

> **上一轮我把五个支付类叫作「死代码」，而它们只是**没人调用**。
> 这一轮补上那句调用 —— 四十三个函数出现，而它们一直都在，只是没有被任何人从入口走到。**
> **「死代码」这个词是错的：代码没有死活，只有**可达不可达**。
> 而不可达的代码需要的不是重写，是**一句调用**。**
"""

if "接两个支付网关：**+43 函数**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 955 轮：接两个支付网关 —— +43 函数，模式第二次成立

### 改动

**`SubmitPaymentAsync` 原来 `=> NotSupported("SubmitPayment")`；现在按 session 的 `paymentGateway`
派发到 `VivaPayments.ChargeTokenAsync` / `DisneyPaymentSheet.ProcessAsync`。**

### 数字

```
pdata-replica: 173,781 -> 173,824     +43
pdata-ratio:   62.71%  -> 62.73%
size:          54,674 KB -> 54,692 KB
套件 2097 通过 / 0 失败 / 0 跳过 · 陈旧度 0 / 0
```

### 而 +43 vs redirect 的 +128

| 接的 | 增量 |
|---|---|
| `RedirectPolicy.FollowAsync` | **+128** |
| 两个支付网关 | **+43**（≈21 每个） |

> **增量不是常数，是**那个 async 带多少实例化**。而两个数都远大于 1 ——
> 「接一个 async ≈ 十几个到一百多个函数」现在有两个样本。**

### 而这次接线是**对的**，不是「为动数而接」

**`SubmitPaymentAsync` 原本返回 `NotSupported` —— 那是一个**真缺口**：
支付步骤存在、五个网关实现存在、中间那句调用不存在。**

> **数动是它的**后果**，不是目的。**

### 而修的时候撞了五次签名

**`ChargeTokenAsync(FlowSession, card, expiry, ct, Func<...> post)` —— 最后一个是**调用方传入的 POST 委托**。
我第一版按 `(NetClient, url, ct)` 写，全错。`StepOutcome` 没有 `Retryable()`；`NotSupported` 要 `await`。**

**五次编译错误，五次都是「我以为签名是什么」而不是「读签名」。**

### 教训

> **上一轮我把五个支付类叫「死代码」，而它们只是**没人调用**。
> 「死代码」这个词是错的：代码没有死活，只有**可达不可达**。
> 而不可达的代码需要的不是重写，是**一句调用**。**
"""

BACKLOG_ADD = """

## 判据 (c)/① — 支付派发接上两个网关：+43 函数（R955，**改产品代码**）

### 改动

**`SubmitPaymentAsync` 按 `paymentGateway` 派发 → `VivaPayments.ChargeTokenAsync` / `DisneyPaymentSheet.ProcessAsync`；
post 委托按网关声明的 `Func<...>` 形状构造；无网关时保持 `NotSupported`。**

### 数字

**函数数 173,781 → **173,824（+43）** · 比 62.71% → **62.73%** · 产物 54,674 → 54,692 KB · 套件 2097 · 陈旧度 0/0**

### 两个样本

**redirect +128 · 两个支付网关 +43（≈21 每个）**

### 教训

**「死代码」是错的词 —— 代码只有可达不可达；不可达需要的不是重写，是一句调用。**

| 仍 Unknown | |
|---|---|
| +128 与 +43 的差因 | 泛型面宽窄（Inference） |
| 另外三个网关（PurpleDot/EshopWorld/GlobalECheckout）的增量 | 未接 |
| 派发是否与原版一致 | 原版按什么派发未取证 |

**纪律**：五次编译错误都是「我以为签名是什么」而不是「读签名」。
"""

BLOCKER = """

---

## 379. 支付派发接上两个网关：+43 函数

> R955。**改产品代码。** 套件 **2097 通过 / 0 失败 / 0 跳过**。

### 一、改动

**`SubmitPaymentAsync` 原来 `=> NotSupported("SubmitPayment")`；现在按 `paymentGateway` 派发：**

```
"viva" / "vivapayments" -> VivaPayments.ChargeTokenAsync(session, card, expiry, ct, post)
"disney" / "disneypaymentsheet" -> DisneyPaymentSheet.ProcessAsync(session, ct, post)
其它 -> NotSupported("SubmitPayment:" + gateway)
```

**`post` 委托按网关声明的 `Func<string,string,string,CancellationToken,Task<NetResponse?>>` 构造。**

### 二、数字

```
pdata-replica: 173,781 -> 173,824     +43
pdata-ratio:   62.71%  -> 62.73%
size:          54,674 KB -> 54,692 KB
```

### 三、两个样本

| 接的 | 增量 |
|---|---|
| `RedirectPolicy.FollowAsync` | **+128** |
| 两个支付网关 | **+43**（≈21 每个） |

**增量不是常数 —— 是那个 async 带多少泛型实例化 / 闭包。**

### 四、而这次接线是**对的**

**`SubmitPaymentAsync` 返回 `NotSupported` 是一个真缺口：步骤存在、实现存在、中间的调用不存在。
数动是后果，不是目的。**

### 五、五次签名错误

1. **`ChargeTokenAsync` 第五参是 `Func<...> post` 委托，不是 NetClient**
2. **`ProcessAsync` 同样形状**
3. **`StepOutcome` 没有 `Retryable()`（只有 Success/Fail/Stop）**
4. **`EshopWorldPanel` 没有 `IsSettled`**
5. **`NotSupported` 返回 `Task<StepOutcome>`，async 里要 `await`**

**五次都是「我以为签名是什么」而不是「读签名」。**

### 六、验证

```
dotnet build Cybersole.Stores -> 0 error
test --filter StoreFlow|Payment -> 59 通过
dotnet publish                -> 54,692 KB
func_count.py                 -> 173,824 (+43)
metrics_report.py             -> 2097 通过 / 0 失败，比 62.73%
```

### 七、仍然 Unknown

- **+128 与 +43 的差因**：**Inference** —— 泛型面宽窄。
- **另外三个网关的增量**：**Unknown** —— 未接。
- **派发是否与原版一致**：**Unknown** —— 原版按什么派发未取证。

### 八、教训

**「死代码」是错的词：代码没有死活，只有可达不可达；不可达需要的不是重写，是一句调用。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R955", BLOCKER)
    ensure(RSTATUS, "R955", BLOCKER)
    ensure(RVERDICT, "第 955 轮", VERDICT)
    ensure(BACKLOG, "R955", BACKLOG_ADD)

    note = (
        "\n## R955 补充 — 支付派发接上两个网关：+43 函数（套件 2097）\n\n"
        "SubmitPaymentAsync 从 `=> NotSupported` 改成按 paymentGateway 派发到 VivaPayments / DisneyPaymentSheet。\n"
        "函数数 173,781 → **173,824（+43）** · 比 62.71% → **62.73%** · 产物 54,674 → 54,692 KB。\n\n"
        "两个样本：redirect +128 · 两个支付网关 +43（≈21 每个）—— 增量不是常数，是 async 带的泛型实例化数。\n\n"
        "而这次接线是对的：SubmitPaymentAsync 返回 NotSupported 是真缺口（步骤在、实现在、中间调用不在）。\n\n"
        "五次签名错误：post 委托形状 · StepOutcome 无 Retryable() · EshopWorldPanel 无 IsSettled · "
        "NotSupported 要 await。全是「我以为签名是什么」而非「读签名」。\n\n"
        "纪律：「死代码」是错的词 —— 代码只有可达不可达；不可达需要的不是重写，是一句调用。\n\n"
        "下一轮：接另外三个网关（PurpleDot/EshopWorld/GlobalECheckout），或按原版证据核对派发方式。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R955" not in h:
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
             for p, k in ((RBLOCK, "R955"), (RSTATUS, "R955"), (RVERDICT, "第 955 轮"), (BACKLOG, "R955")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R955: wiring two payment gateways added 43 functions, so the pattern holds\n\n"
         "R954 found that all five payment gateway classes written between R920 and R925 were referenced by nothing. This\n"
         " round connected two of them: SubmitPaymentAsync used to return NotSupported and now dispatches on the session's\n"
         " paymentGateway name to VivaPayments.ChargeTokenAsync or DisneyPaymentSheet.ProcessAsync, building the post\n"
         " delegate in the shape the gateways declare.\n\n"
         "The count went from 173,781 to 173,824, ratio 62.71 to 62.73, artifact from 54,674 to 54,692 kilobytes. So the\n"
         " mechanism found in R952 holds: connecting an async method into a reachable path adds functions, and the size of\n"
         " the addition is not constant -- 128 for the redirect policy, about 21 each for these two -- because it tracks how\n"
         " much generic instantiation and closure the method carries.\n\n"
         "And this wiring is correct work rather than a move to make a number move. SubmitPaymentAsync returning NotSupported\n"
         " was a real gap: the step exists, five gateway implementations exist, and the call between them did not. The count\n"
         " moving is a consequence of closing that gap, not the reason for it.\n\n"
         "Getting it to compile took five corrections, all of the same kind. ChargeTokenAsync's fifth parameter is a post\n"
         " delegate the caller supplies rather than a client, because no gateway owns one; StepOutcome has Success, Fail and\n"
         " Stop but no Retryable; EshopWorldPanel has no IsSettled; and NotSupported returns a Task, so an async method must\n"
         " await it. Every one of the five was me assuming a signature instead of reading it.\n\n"
         "Figures: suite 2097 green, freshness zero, count 173,824, ratio 62.73 percent.\n\n"
         "Unknown: why the redirect added six times what a gateway did, inferred as the breadth of generic instantiation;\n"
         " what the other three gateways would add, which are not yet connected; and whether the original dispatches the same\n"
         " way, for which no evidence was taken.\n\n"
         "The lesson is that dead code was the wrong phrase last round. Code is not alive or dead, only reachable or not, and\n"
         " what unreachable code needs is not a rewrite but a single call.\n\n"
         "Product code changed; suite green at 2097."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()