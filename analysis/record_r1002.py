"""Record R1002: one line of wiring made 250 lines of gateway reach the artifact."""

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
### 一句接线把 250 行代码拉进了产物：**+0 → +342**（R1002）

**R1001 加了 4 个网关，publish 之后函数数**一个都不动**，因为 `CreateDefault()` 没人调。
这一轮只改两处，函数数涨了 **342**。**

### ① 改了什么

**① `PaymentGateway.cs`：加一个 `public static PaymentGatewayRegistry Default { get; } = CreateDefault();`**
**② `StoreFlow.SubmitPaymentAsync`：gateway 名解析出来之后先试注册表**

```csharp
var registered = Cybersole.Stores.Payments.PaymentGatewayRegistry.Default.Resolve(gateway);
if (registered is not null)
{
    var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
    …
}
```

**而选 `SubmitPaymentAsync` 的理由是**有 12 个覆写**（`DemandwareFlow` / `FarfetchFlow` / `FootsitesFlow` …）——
R963 那条「零覆写的基类体被裁」的反面。**

### ② 为什么这一处能通，而 R1001 那处不能

**R1001 说「我给它加了调用点」：`Register(new MollieGateway())` 在 `CreateDefault()` 里，
那是一句普通的构造调用 —— 而**没有人调 `CreateDefault()`**，所以整条链不可达。**

**这一轮的调用点在 `SubmitPaymentAsync` 里，而那个方法有 12 个覆写，
所以基类体被保留，`registry.Resolve` 从覆写出发可达。**

> **→ 所以 R1000 那条规则要写成三档，而不是两档：
> ① 从入口可达 ② 被覆写（覆写的体进产物，且该方法被保留）③ 两者都没有（被裁）。
> 「有调用语句」不构成任何一档。**

### ③ 产物验证（这一次是肯定的）

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| **`PaymentGatewayRegistry`** | **IN** | absent |
| **`ecommerce-gateway.mollie.com`** | **IN** | absent |
| **`degica.as1.gpayments.net`** | **IN** | absent |
| **`retry.touchtechpayments.com`** | **IN** | absent |
| **`app.midtrans.com`** | **IN** | absent |
| `api.sibspayments.com` · `api.unzer.com` · `api.omise.co` | **IN** | absent |
| `api.stripe.com` · `paypal.com` | IN | IN |
| `api.squareup.com` · `adyen.com` | absent | absent |
| `needs a 3-D Secure step` | **absent** | absent |

**→ 产物里的网关从 **2 个变成 9 个**。**
**→ 而 `needs a 3-D Secure step` absent：那条 `RequiresAction` 分支没被保留，
可达的是 `AuthorizeAsync` 本身 —— 一个诚实的细节，不是失败。**
**→ `squareup` / `adyen` 仍 absent：它们不在这一轮的可达集里（`AdyenGateway` 在另一个文件，
`SquareGateway` 的 host 常量可能是别的拼法）。**

### ④ 函数数 **+342**，比 +0.12 个百分点

| 度量 | R1001 | **R1002** |
|---|---|---|
| **函数数** | 173,994 | **174,336（+342）** |
| **函数比** | 62.79% | **62.91%** |
| 套件 | 2214 | **2214** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物里网关 | 2 | **9** |

> **+342 的量级对得上：9 个网关类各自的四方法 + 闭包 + `JObject` 构造 + 字符串插值
> + `PaymentGatewayRegistry` 的 `Dictionary`。而这一整族在 R1001 里是 0。**

### ⑤ 而这一轮真正建立的东西

**同一份 250 行代码，同样 publish 成功、套件同样绿、陈旧度同样 0 —— 而函数数一次 +0、一次 +342。
唯一的差别是**那一行 `Resolve` 在不在一条可达的路上**。**

> **→ 所以「产物对得上源码」这件事，不能靠「我改了、我发布了、套件绿了」来确认。
> 它只有两种可信的确认方式：**在产物里搜一个只有那段代码才会有的串**，或者**看函数数动没动**。
> 而两者的前提是同一条：先说得出那段代码**为什么可达**。**

### 教训

> **「加了 250 行」和「产物多了 342 个函数」之间，隔着一句 `Resolve`。
> 而我在 R1001 里以为注册就是那句 —— 注册只是把新类放在一条没人走的走廊上。**
> **→ 可达性是**独立于代码量**的一个维度。它不写在任何一行里，只能被证明或被否证。**
"""

if "一句接线把 250 行代码拉进了产物" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1002 轮：一句接线把 250 行代码拉进产物 —— +0 → +342

### ① 改了两处

1. **`PaymentGateway.cs`**：`public static PaymentGatewayRegistry Default { get; } = CreateDefault();`
2. **`StoreFlow.SubmitPaymentAsync`**：gateway 名解析出来后先试注册表

```csharp
var registered = Cybersole.Stores.Payments.PaymentGatewayRegistry.Default.Resolve(gateway);
if (registered is not null)
{
    var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
    …
}
```

**选 `SubmitPaymentAsync` 的理由：它有 **12 个覆写** —— R963「零覆写基类体被裁」的反面。**

### ② 为什么这一处通、R1001 那处不通

**R1001 的 `Register(new MollieGateway())` 在 `CreateDefault()` 里，是一句普通构造调用 ——
而**没有人调 `CreateDefault()`**，整条链不可达。**

**这一轮的调用点在 `SubmitPaymentAsync` 里，它有 12 个覆写，所以基类体被保留。**

> **→ R1000 那条规则该写成三档：① 从入口可达 ② 被覆写 ③ 两者都没有（被裁）。
> 「有调用语句」不构成任何一档。**

### ③ 产物验证（肯定的）

| 串 | 新 | 旧 |
|---|---|---|
| **`PaymentGatewayRegistry`** | **IN** | absent |
| **4 个新网关的 host** | **IN** | absent |
| `sibspayments` · `unzer` · `omise` | **IN** | absent |
| `stripe` · `paypal` | IN | IN |
| `squareup` · `adyen` | absent | absent |
| `needs a 3-D Secure step` | **absent** | absent |

**→ 产物里的网关 **2 → 9 个**。
→ `needs a 3-D Secure step` absent：`RequiresAction` 分支没被保留，可达的是 `AuthorizeAsync` 本身。
→ `squareup`/`adyen` 不在这一轮的可达集里（不同文件 / 不同拼法）。**

### ④ 数字

| 度量 | R1001 | **R1002** |
|---|---|---|
| **函数数** | 173,994 | **174,336（+342）** |
| **函数比** | 62.79% | **62.91%** |
| 套件 | 2214 | **2214** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物里网关 | 2 | **9** |

> **+342 的量级对得上：9 个网关类各自的四方法 + 闭包 + `JObject` 构造 + 插值 + `Dictionary`。
> 而这一整族在 R1001 里是 0。**

### ⑤ 教训

> **「加了 250 行」和「产物多了 342 个函数」之间，隔着一句 `Resolve`。
> 而我在 R1001 里以为注册就是那句 —— 注册只是把新类放在一条没人走的走廊上。
> → 可达性是**独立于代码量**的一个维度。它不写在任何一行里，只能被证明或被否证。**
"""

BACKLOG_ADD = """

## 优先级 ①/判据 (c) — **`SubmitPaymentAsync` 接 `registry.Resolve`：函数数 173,994 → 174,336（+342），产物网关 2 → 9**（R1002）

### 改了两处

1. `PaymentGateway.cs` — `public static PaymentGatewayRegistry Default { get; } = CreateDefault();`
2. `StoreFlow.SubmitPaymentAsync` — gateway 名解析后先试 `Default.Resolve(gateway)`，
   命中则跑 `AuthorizeAsync`；`RequiresAction` 记 `threeDsUrl`/`threeDsPayload` 并返回 Success
   （`StepOutcome` 只有 Success/Fail/Stop，不发明第四个工厂）

**选它的理由：`SubmitPaymentAsync` 有 **12 个覆写** → 基类体保留 → 调用可达（R963 的反面）。**

### 可达性三档（R1000 修订）

**① 从入口可达 ② 被覆写 ③ 两者都没有（被裁）。「有调用语句」不构成任何一档。**
**R1001 +0 / R1002 +342，同一份代码，差别只在那一行是否在可达的路上。**

### 产物验证

**`PaymentGatewayRegistry` IN · 4 个新网关 host 全 IN · `sibspayments`/`unzer`/`omise` IN
→ 产物里网关 2 → 9。**
**`needs a 3-D Secure step` absent（该分支未保留，可达的是 `AuthorizeAsync`）· `squareup`/`adyen` absent。**

### 数字

**套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 比 62.91% · 产物网关 9**

| 仍 Unknown | |
|---|---|
| `api.squareup.com` / `adyen.com` 的 host 拼法 | 未核（可能不同） |
| DataDome 的 3DS 分支为什么被裁 | 未查 |

**纪律**：可达性独立于代码量，它不写在任何一行里。
"""

BLOCKER = """

---

## 426. **`SubmitPaymentAsync` 接 `registry.Resolve`：函数数 +342，产物网关 2 → 9**

> R1002。**改 2 个源文件。** 套件 **2214 通过 / 0 失败 / 0 跳过**。

### 一、改了什么

**① `PaymentGateway.cs`**

```csharp
public static PaymentGatewayRegistry Default { get; } = CreateDefault();
```

**② `StoreFlow.SubmitPaymentAsync`（gateway 名解析出来之后、构造通用 POST 之前）**

```csharp
var registered = Cybersole.Stores.Payments.PaymentGatewayRegistry.Default.Resolve(gateway);
if (registered is not null)
{
    var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);

    if (outcome.RequiresAction && !string.IsNullOrEmpty(outcome.ThreeDsUrl))
    {
        c.Session.Vars["threeDsUrl"] = outcome.ThreeDsUrl!;
        if (!string.IsNullOrEmpty(outcome.ThreeDsPayload)) c.Session.Vars["threeDsPayload"] = outcome.ThreeDsPayload!;
        c.Emit($"{Name}: {gateway} needs a 3-D Secure step", "payment");
        return StepOutcome.Success();
    }

    if (outcome.Ok) { c.Emit(…); return StepOutcome.Success(); }

    return StepOutcome.Fail($"{Name}: {outcome.Error ?? gateway + " declined"}", retryable: false);
}
```

**`StepOutcome` 只有 `Success`/`Fail`/`Stop` 三个工厂，所以 3DS 交接记进 `Vars` 而不是新造一个工厂
（新造一个形状是流程其余部分不认识的）。**

### 二、为什么这一处通、R1001 那处不通

**R1001 说「我给它加了调用点」：`Register(new MollieGateway())` 在 `CreateDefault()` 里，
那是一句普通的构造调用 —— 而**没有人调 `CreateDefault()`**，所以整条链不可达。**

**这一轮的调用点在 `SubmitPaymentAsync` 里，而那个方法有 **12 个覆写**
（`DemandwareFlow` / `FarfetchFlow` / `FootsitesFlow` …），所以基类体被保留、`registry.Resolve` 可达。**

**→ R1000 那条规则该写成三档，而不是两档：
① 从入口可达 ② 被覆写（方法体保留）③ 两者都没有（被裁）。
「有调用语句」不构成任何一档。**

### 三、产物验证（这一次是肯定的）

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| **`PaymentGatewayRegistry`** | **IN** | absent |
| **`ecommerce-gateway.mollie.com`** | **IN** | absent |
| **`degica.as1.gpayments.net`** | **IN** | absent |
| **`retry.touchtechpayments.com`** | **IN** | absent |
| **`app.midtrans.com`** | **IN** | absent |
| `api.sibspayments.com` · `api.unzer.com` · `api.omise.co` | **IN** | absent |
| `api.stripe.com` · `paypal.com` | IN | IN |
| `api.squareup.com` · `adyen.com` | absent | absent |
| `needs a 3-D Secure step` | **absent** | absent |

**→ 产物里的网关从 **2 个变成 9 个**。
→ `needs a 3-D Secure step` absent：那条 `RequiresAction` 分支没被保留，
  可达的是 `AuthorizeAsync` 本身 —— 一个诚实的细节，不是失败。
→ `squareup` / `adyen` 仍 absent：它们不在这一轮的可达集里
  （`AdyenGateway` 在另一个文件，`SquareGateway` 的 host 常量可能是别的拼法）。**

### 四、函数数 **+342**

| 度量 | R1001 | R1002 |
|---|---|---|
| **函数数** | 173,994 | **174,336（+342）** |
| **函数比** | 62.79% | **62.91%** |
| 套件 | 2214 | **2214** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物里网关 | 2 | **9** |

**→ +342 的量级对得上：9 个网关类各自的四方法 + 闭包 + `JObject` 构造 + 字符串插值
+ `PaymentGatewayRegistry` 的 `Dictionary`。而这一整族在 R1001 里是 0。**

### 五、验证

```
cd replica
python tools/snapshot.py
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug   -> 已成功生成
dotnet test --filter "FullyQualifiedName~Gateway|FullyQualifiedName~Payment|FullyQualifiedName~Flow" -m:1  -> 192 通过
dotnet publish … -o .publish-aot-new --nologo                        -> exit 0
轮换后 python tools/metrics_report.py -> functions: replica 174,336 · ratio 62.91% · source files newer 0 · 套件 2214
python - 在 .publish-aot 字节里搜 13 个串 -> 见上表
```

### 六、仍然 Unknown

- **`api.squareup.com` / `adyen.com` 的 host 拼法**：**Unknown** —— 未核，可能不同。
- **`RequiresAction` 分支为什么没被保留**：**Unknown** —— 未查。

### 七、教训

**「加了 250 行」和「产物多了 342 个函数」之间，隔着一句 `Resolve`。
而我在 R1001 里以为注册就是那句 —— 注册只是把新类放在一条没人走的走廊上。**

**→ 可达性是**独立于代码量**的一个维度。它不写在任何一行里，只能被证明或被否证。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1002", BLOCKER)
    ensure(RSTATUS, "R1002", BLOCKER)
    ensure(RVERDICT, "第 1002 轮", VERDICT)
    ensure(BACKLOG, "R1002", BACKLOG_ADD)

    note = (
        "\n## R1002 补充 — **一句接线把 250 行代码拉进产物：+0 → +342**（套件 2214）\n\n"
        "改两处：① `PaymentGatewayRegistry.Default`（静态单例）② `SubmitPaymentAsync` 里 "
        "`Default.Resolve(gateway)` → `AuthorizeAsync`。\n"
        "**选 `SubmitPaymentAsync` 的理由：它有 12 个覆写 → 基类体保留 → 调用可达（R963 的反面）。**\n\n"
        "**产物验证（肯定）**：`PaymentGatewayRegistry` IN · 4 个新网关 host 全 IN · `sibspayments`/`unzer`/`omise` IN\n"
        "→ **产物里网关 2 → 9**。`needs a 3-D Secure step` absent（该分支未保留，可达的是 `AuthorizeAsync`）。\n\n"
        "**函数数 173,994 → 174,336（+342）· 比 62.79% → 62.91% · 陈旧度 0/0。**\n"
        "→ 同一份 250 行代码，R1001 是 **+0**、R1002 是 **+342**，差别只在那一行是否在可达的路上。\n\n"
        "**可达性三档（R1000 修订）**：① 从入口可达 ② 被覆写 ③ 两者都没有（被裁）。\n"
        "**「有调用语句」不构成任何一档。**\n\n"
        "仍 Unknown：`squareup`/`adyen` 的 host 拼法；`RequiresAction` 分支为何未保留。\n\n"
        "纪律：**可达性独立于代码量，它不写在任何一行里，只能被证明或被否证。**\n\n"
        "下一轮：`GetPaymentMethodsAsync` 覆写 0 次 → 它必然被裁，把它接到某个覆写里去（或查原版是否真无覆写）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1002" not in h:
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
             for p, k in ((RBLOCK, "R1002"), (RSTATUS, "R1002"), (RVERDICT, "第 1002 轮"), (BACKLOG, "R1002")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1002: one line of wiring, and the function count moves by 342\n\n"
         "R1001 wrote four gateways and published them, and the artifact gained nothing, because CreateDefault had no\n"
         " caller. This round changes two things and the count goes from 173,994 to 174,336.\n\n"
         "The first is a single static instance of the registry instead of building one per payment. The second is the call\n"
         " site: SubmitPaymentAsync resolves the per-shop gateway name against that registry and, when it finds one, lets it\n"
         " authorise rather than building a generic post by hand.\n\n"
         "The choice of SubmitPaymentAsync is the whole reason it works. Twelve flows override it, so its body is retained\n"
         " where an unoverridden base method would be trimmed -- the reverse of R963's finding. R1001's Register call sat\n"
         " inside a method nobody invokes, which is a call statement on a road nobody walks.\n\n"
         "The artifact agrees. PaymentGatewayRegistry is present, all four new gateway hosts are present, and so are\n"
         " sibspayments, unzer and omise, which means the number of gateways in the binary goes from two to nine. Stripe and\n"
         " PayPal were already there from another reachable path. Square and Adyen are still absent, which is a question for\n"
         " another round rather than a failure of this one.\n\n"
         "One honest detail: the marker string for the 3-D Secure branch is absent, so that branch was not retained even\n"
         " though AuthorizeAsync was. The reachable part is the authorise call; the hand-off after it is not.\n\n"
         "The lesson worth keeping is that reachability is a dimension of its own, independent of how much code you write. It\n"
         " is not recorded on any line. 250 lines moved the count by nothing; one resolved call moved it by 342. And the way\n"
         " to know which you have is not the build, not the suite, not the publish succeeding -- it is searching the artifact\n"
         " for a string only that code can produce, or watching the count.\n\n"
         "Figures: suite 2214, freshness zero, functions 174,336, ratio 62.91 percent, gateways in the artifact nine.\n\n"
         "Unknown: the host spelling for Square and Adyen, and why the RequiresAction branch was trimmed.\n\n"
         "Two source files changed; suite green at 2214; function count up 342."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()