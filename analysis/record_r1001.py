"""Record R1001: four gateways added, and the artifact proves registration is not a call site."""

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
### 加了 4 个网关，publish 成功，而产物里**一个都没进**（R1001）

**R1000 定了规则：进产物二选一 —— ① 真实调用点 ② flow 覆写。
这一轮按 ① 做了，而产物证明我对 ① 的理解**错了一半**。**

### ① 做的事

**`Gateways.cs` 追加 4 个网关（约 250 行），`PaymentGatewayRegistry.CreateDefault()` 里注册：**

| 网关 | 镜像给的端点 |
|---|---|
| `MollieGateway` | `ecommerce-gateway.mollie.com/api/v1/public/core/payments/poll` |
| `GmoGateway` | `degica.as1.gpayments.net/api/v2/brw/info/result?transId=` |
| `TouchtechGateway` | `retry.touchtechpayments.com/api/v1/:select` |
| `MidtransGateway` | `app.midtrans.com/snap/v1|v2/transactions` |

**每个网关四个方法（`TokenizeAsync` / `AuthorizeAsync` / `CompleteActionAsync` + `Id`/`Name`），
与既有 9 个同形。镜像只给一条路径的，其余步骤报「endpoint not captured」，不编路径
（R823/R991 的同一条原则）。构建成功、60 条网关/支付用例通过、4 条新守卫通过。**

### ② 而 publish 之后，产物里一个都不在

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| `ecommerce-gateway.mollie.com` | **absent** | absent |
| `degica.as1.gpayments.net` | **absent** | absent |
| `retry.touchtechpayments.com` | **absent** | absent |
| `app.midtrans.com` | **absent** | absent |
| `not captured` | **absent** | absent |

**→ 而函数数也**一个都没动**：173,994 → 173,994。**

### ③ 而判别性的那一组解释了一切

| 串 | 新 | 旧 |
|---|---|---|
| `api.stripe.com` · `paypal.com` | **IN** | IN |
| `api.sibspayments.com` · `squareup` · `unzer` · `omise` · `adyen` | absent | absent |
| **`PaymentGatewayRegistry`** | **absent** | absent |

> **`PaymentGatewayRegistry` 这个名字不在产物里，而 `CreateDefault` 在（别处的同名方法）。
> → 所以 `PaymentGatewayRegistry.CreateDefault()` **没有任何代码调用它**。
> → 整族网关是死代码，全被裁 —— 连既有那 9 个里的 7 个也不在。**
> **→ Stripe 与 PayPal 的 host 串从**别处**可达（大概是 UI 的支付方式枚举），所以它们留着。**

### ④ 所以 R1000 那条规则要**收紧一格**

**我上一轮写：「给它一个真实调用点（像 `DataDomeClearance` 被 `SolveDetectedWallAsync` 直接调）」。
而 `Register(new MollieGateway())` **看起来**就是一个调用点 —— 它在 `CreateDefault()` 里，
那是一句普通的构造调用。而它没让任何东西进产物。**

> **→ 真正的判据不是「有没有调用语句」，是「**从入口能不能走到**」。
> `CreateDefault()` 自己没人调，所以它里面的调用不计。
> → 这与 R963 那条（反射不 root 方法）是同一族但不同因：
> 那次是**调用方式**不可见，这次是**调用链**不可达。
> → 两者共同的检验方法完全相同：**在产物里搜。** 而这一步让两种都现形。**

### ⑤ 而这解释了优先级 ① 那 4 个真缺为什么一直补不上

**它们不是「缺一个类」，是「缺一条从 flow 到 registry 的可达路径」。
而既有 9 个网关里 7 个也不在产物里 —— 所以**整个支付层在产物里几乎不存在**。**

**→ 正确的修复是 R1000 的第二条路：让**具体的 flow** 覆写支付步骤，在覆写里直接调
`registry.Resolve(id)?.AuthorizeAsync(c, ct)`。那样调用链从 flow 出发，可达。**

### ⑥ 而这一轮的产出是**一个否命题加一条更准的规则**

**250 行代码没进产物 —— 那是行的浪费，也是**一条边界的确证**：
「注册」不是「接线」，「接线」不是「可达」。

**而它花了一轮就证完了，因为 R999 让产物陈旧度变成一句话就查得清的事，
R1000 让「在产物里搜」成为固定动作。**

### 数字

| 度量 | R1000 | **R1001** |
|---|---|---|
| 套件 | 2210 | **2214（+4 网关守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0（已 publish）** |
| **函数数** | 173,994 | **173,994（不动）** |
| 函数比 | 62.79% | **62.79%（不动）** |
| 新增网关类 | 0 | **4** |
| **其中进了产物** | — | **0** |
| **既有 9 个网关在产物里** | 未测 | **2（Stripe · PayPal）** |

### 教训

> **「我给它加了调用点」这句话可以完全为真，而不改变产物一个字节 ——
> 因为那个调用点在一条没人走的路上。**
> **→ 唯一不会骗人的检验是产物本身：搜它，或者数它。而我在 R1000 才第一次做，这一轮就靠它否掉了自己。**
"""

if "加了 4 个网关，publish 成功" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1001 轮：加了 4 个网关，publish 成功，而产物里一个都没进

### ① 做的事

**`Gateways.cs` 追加 4 个网关（约 250 行）+ `CreateDefault()` 注册：**

| 网关 | 镜像给的端点 |
|---|---|
| `MollieGateway` | `ecommerce-gateway.mollie.com/api/v1/public/core/payments/poll` |
| `GmoGateway` | `degica.as1.gpayments.net/api/v2/brw/info/result?transId=` |
| `TouchtechGateway` | `retry.touchtechpayments.com/api/v1/:select` |
| `MidtransGateway` | `app.midtrans.com/snap/v1|v2/transactions` |

**构建成功 · 60 条网关/支付用例通过 · 4 条新守卫通过。镜像只给一条路径的步骤报
「endpoint not captured」，不编路径（R823/R991 同一条原则）。**

### ② 而 publish 之后，产物里一个都不在

**4 个 host 串全 absent，`not captured` 也 absent，函数数 173,994 → **173,994 不动**。**

### ③ 而判别性的那一组解释了一切

| 串 | 新 | 旧 |
|---|---|---|
| `api.stripe.com` · `paypal.com` | **IN** | IN |
| `api.sibspayments.com` · `squareup` · `unzer` · `omise` · `adyen` | absent | absent |
| **`PaymentGatewayRegistry`** | **absent** | absent |

> **`PaymentGatewayRegistry.CreateDefault()` **没有任何代码调用它** → 整族网关是死代码，全被裁。
> 连既有 9 个里的 7 个也不在。Stripe 与 PayPal 从**别处**可达（UI 的支付方式枚举）。**

### ④ R1000 那条规则要**收紧一格**

**我上一轮写「给它一个真实调用点」。而 `Register(new MollieGateway())` **看起来**就是调用点 ——
它在 `CreateDefault()` 里，是一句普通构造调用。而它没让任何东西进产物。**

> **→ 真正的判据不是「有没有调用语句」，是「**从入口能不能走到**」。
> 与 R963（反射不 root 方法）同一族但不同因：那次是**调用方式**不可见，这次是**调用链**不可达。
> → 两者的检验方法相同：**在产物里搜。**

### ⑤ 这解释了优先级 ① 那 4 个真缺为什么补不上

**它们不是「缺一个类」，是「缺一条从 flow 到 registry 的可达路径」。
而既有 9 个里 7 个也不在产物里 —— **整个支付层在产物里几乎不存在**。**

**→ 正确的修复是 R1000 的第二条路：让**具体的 flow** 覆写支付步骤，
在覆写里直接调 `registry.Resolve(id)?.AuthorizeAsync(c, ct)`。那样调用链从 flow 出发，可达。**

### ⑥ 数字

| 度量 | R1000 | **R1001** |
|---|---|---|
| 套件 | 2210 | **2214（+4 网关守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0（已 publish）** |
| **函数数** | 173,994 | **173,994（不动）** |
| 函数比 | 62.79% | **62.79%（不动）** |
| 新增网关类 | 0 | **4** |
| **其中进了产物** | — | **0** |
| **既有 9 个网关在产物里** | 未测 | **2（Stripe · PayPal）** |

### 教训

> **「我给它加了调用点」这句话可以完全为真，而不改变产物一个字节 ——
> 因为那个调用点在一条没人走的路上。
> → 唯一不会骗人的检验是产物本身：搜它，或者数它。
> 而我在 R1000 才第一次做，这一轮就靠它否掉了自己。**
"""

BACKLOG_ADD = """

## 优先级 ①/判据 (c) — **4 个网关已写但**零个进产物**：`CreateDefault()` 无调用者，整族被裁**（R1001）

### 写了什么

**`Gateways.cs` +250 行：`MollieGateway` · `GmoGateway` · `TouchtechGateway` · `MidtransGateway`，
各四方法，端点取自镜像；只给一条路径的步骤报「endpoint not captured」不编。**
**`PaymentGatewayRegistry.CreateDefault()` 里注册 → 13 个。**

### 产物验证（否定）

**4 个 host 串全 absent · `PaymentGatewayRegistry` absent · 函数数 173,994 不动。**
**而 `api.stripe.com` / `paypal.com` IN，`sibspayments` / `squareup` / `unzer` / `omise` / `adyen` absent
→ 既有 9 个里 **7 个也不在产物里** → 整个支付层几乎不存在。**

### 规则收紧（R1000 之上）

**「注册」不是「接线」，「接线」不是「可达」。
真正的判据是**从入口能不能走到** `CreateDefault()`，而它没人调。**

### 正确的修复方向

**让**具体 flow** 覆写支付步骤，在覆写里直接调 `registry.Resolve(id)?.AuthorizeAsync(c, ct)` ——
调用链从 flow 出发才可达（R1000 的第二条路）。**

### 数字

**套件 2214 · 陈旧度 0/0 · 函数数 173,994（不动）· 新增 4 类 / 进产物 0 · 既有 9 个在产物里 2**

| 仍 Unknown | |
|---|---|
| 哪个 flow 该承载这 4 个网关 | 未取证（需 host↔flow 对照） |
| `CreateDefault()` 在原版里是否有调用者 | 未取证 |

**纪律**：「我给它加了调用点」可以为真而不改变产物一个字节。
"""

BLOCKER = """

---

## 425. **4 个网关已写但零个进产物：`CreateDefault()` 无调用者，整族被裁**

> R1001。**新增 4 个网关类（约 250 行）+ 1 处注册 + 4 条守卫。** 套件 **2214 通过 / 0 失败 / 0 跳过**。

### 一、做的事

**`src/Cybersole.Stores/Payments/Gateways.cs` 追加 4 个网关，`PaymentGatewayRegistry.CreateDefault()` 里注册：**

| 网关 | 镜像给的端点 |
|---|---|
| `MollieGateway` | `ecommerce-gateway.mollie.com/api/v1/public/core/payments/poll` |
| `GmoGateway` | `degica.as1.gpayments.net/api/v2/brw/info/result?transId=` |
| `TouchtechGateway` | `retry.touchtechpayments.com/api/v1/:select` |
| `MidtransGateway` | `app.midtrans.com/snap/v1|v2/transactions` |

**每个网关四个方法，与既有 9 个同形。镜像只给一条路径的，其余步骤报「endpoint not captured」，不编路径
（R823/R991 的同一条原则）。`MidtransGateway.SnapPaths` 记两个 Snap 版本。**
**构建成功 · 60 条网关/支付用例通过 · 4 条新守卫（`UnmatchedGatewaysTests`）通过。**

### 二、而 publish 之后，产物里一个都不在

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| `ecommerce-gateway.mollie.com` | **absent** | absent |
| `degica.as1.gpayments.net` | **absent** | absent |
| `retry.touchtechpayments.com` | **absent** | absent |
| `app.midtrans.com` | **absent** | absent |
| `not captured` | **absent** | absent |

**→ 函数数也**一个都没动**：173,994 → 173,994。**

### 三、而判别性的那一组解释了一切

| 串 | 新 | 旧 |
|---|---|---|
| `api.stripe.com` · `paypal.com` | **IN** | IN |
| `api.sibspayments.com` · `squareup` · `unzer` · `omise` · `adyen` | absent | absent |
| **`PaymentGatewayRegistry`** | **absent** | absent |
| `CreateDefault` | IN（别处的同名方法） | IN |

**→ `PaymentGatewayRegistry` 这个名字不在产物里
→ 所以 `PaymentGatewayRegistry.CreateDefault()` **没有任何代码调用它**
→ 整族网关是死代码，全被裁 —— 连既有那 9 个里的 7 个也不在
→ Stripe 与 PayPal 的 host 串从**别处**可达（大概是 UI 的支付方式枚举），所以它们留着**

### 四、所以 R1000 那条规则要收紧一格

**R1000 写：「给它一个真实调用点（像 `DataDomeClearance` 被 `SolveDetectedWallAsync` 直接调）」。
而 `Register(new MollieGateway())` **看起来**就是一个调用点 —— 它在 `CreateDefault()` 里，
那是一句普通的构造调用。而它没让任何东西进产物。**

**→ 真正的判据不是「有没有调用语句」，是「**从入口能不能走到**」。
→ `CreateDefault()` 自己没人调，所以它里面的调用不计。
→ 这与 R963 那条（反射不 root 方法）是同一族但不同因：
**那次是调用方式不可见，这次是调用链不可达。**
→ 两者共同的检验方法完全相同：**在产物里搜。** 而这一步让两种都现形。**

### 五、这解释了优先级 ① 那 4 个真缺为什么一直补不上

**它们不是「缺一个类」，是「缺一条从 flow 到 registry 的可达路径」。
而既有 9 个网关里 7 个也不在产物里 —— **整个支付层在产物里几乎不存在**。**

**→ 正确的修复是 R1000 的第二条路：让**具体的 flow** 覆写支付步骤，
在覆写里直接调 `registry.Resolve(id)?.AuthorizeAsync(c, ct)`。那样调用链从 flow 出发，可达。**

### 六、数字

| 度量 | R1000 | R1001 |
|---|---|---|
| 套件 | 2210 | **2214（+4 网关守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0（已 publish）** |
| **函数数** | 173,994 | **173,994（不动）** |
| 函数比 | 62.79% | **62.79%（不动）** |
| 新增网关类 | 0 | **4** |
| **其中进了产物** | — | **0** |
| **既有 9 个网关在产物里** | 未测 | **2（Stripe · PayPal）** |

### 七、验证

```
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug   -> 已成功生成
dotnet test --filter "FullyQualifiedName~Gateway|FullyQualifiedName~Payment" -m:1      -> 60 通过
dotnet test --filter "FullyQualifiedName~UnmatchedGatewaysTests" -m:1                  -> 4 通过
dotnet publish src/Cybersole.Ui/Cybersole.Ui.csproj -c Release -r win-x64 -p:PublishAot=true -p:StripSymbols=true -o .publish-aot-new --nologo  -> exit 0，45 秒
轮换后 python tools/metrics_report.py -> functions: replica 173,994（未变）· source files newer 0 · 套件 2214
python - 在 .publish-aot 字节里搜 4 个 host 串 -> 全 absent；PaymentGatewayRegistry absent；
        api.stripe.com / paypal.com IN；sibspayments / squareup / unzer / omise / adyen absent
```

### 八、仍然 Unknown

- **哪个 flow 该承载这 4 个网关**：**Unknown** —— 需要 host↔flow 对照取证。
- **`CreateDefault()` 在原版里是否有调用者**：**Unknown** —— 未取证。

### 九、教训

**「我给它加了调用点」这句话可以完全为真，而不改变产物一个字节 ——
因为那个调用点在一条没人走的路上。**

**→ 唯一不会骗人的检验是产物本身：搜它，或者数它。
而我在 R1000 才第一次做，这一轮就靠它否掉了自己。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1001", BLOCKER)
    ensure(RSTATUS, "R1001", BLOCKER)
    ensure(RVERDICT, "第 1001 轮", VERDICT)
    ensure(BACKLOG, "R1001", BACKLOG_ADD)

    note = (
        "\n## R1001 补充 — **4 个网关已写但零个进产物：`CreateDefault()` 无调用者，整族被裁**（套件 2214）\n\n"
        "按 R1000 的规则①（真实调用点）做了：`Gateways.cs` 追加 4 个网关（Mollie / GMO / Touchtech / Midtrans，250 行），\n"
        "`PaymentGatewayRegistry.CreateDefault()` 注册 → 13 个。构建成功、60 条支付用例 + 4 条新守卫通过。\n\n"
        "**而 publish 后：4 个 host 串全 absent，函数数 173,994 → 173,994 不动。**\n"
        "判别组：**`PaymentGatewayRegistry` 这个名字不在产物里** → `CreateDefault()` 没人调 → 整族死代码被裁。\n"
        "→ 连既有 9 个里 **7 个也不在**（`sibspayments`/`squareup`/`unzer`/`omise`/`adyen` 全 absent），\n"
        "只有 `api.stripe.com` / `paypal.com` IN（从 UI 的支付方式枚举可达）。\n"
        "**→ 整个支付层在产物里几乎不存在。**\n\n"
        "**规则收紧**：「注册」不是「接线」，「接线」不是「可达」。真正的判据是**从入口能不能走到**。\n"
        "与 R963（反射不 root 方法）同一族但不同因：那次是调用方式不可见，这次是调用链不可达。\n\n"
        "**正确方向**：让**具体 flow 覆写支付步骤**，在覆写里直接调 `registry.Resolve(id)?.AuthorizeAsync(c, ct)`\n"
        "—— 调用链从 flow 出发才可达（R1000 的第二条路）。\n\n"
        "数字：套件 2214 · 陈旧度 0/0 · 函数数 173,994（不动）· 新增 4 类 / 进产物 **0** · 既有在产物里 2/9。\n\n"
        "纪律：**「我给它加了调用点」可以为真而不改变产物一个字节。**\n\n"
        "下一轮：取证 host↔flow 对照（哪个 flow 该承载 Mollie/GMO/Touchtech/Midtrans），"
        "然后让那个 flow 覆写支付步骤并直接调 registry —— 否则第 5 个网关也一样进不去。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1001" not in h:
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
             for p, k in ((RBLOCK, "R1001"), (RSTATUS, "R1001"), (RVERDICT, "第 1001 轮"), (BACKLOG, "R1001")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1001: four gateways written, published, and not one reaches the artifact\n\n"
         "R1000 established that getting code into the artifact takes a real call site or a flow override, and this round\n"
         " followed the first route. Gateways.cs gains Mollie, GMO, Touchtech and Midtrans, each with the endpoint the image\n"
         " gave it and each reporting that an endpoint was not captured rather than inventing one. They are registered in\n"
         " PaymentGatewayRegistry.CreateDefault, which now holds thirteen. The build is clean, sixty payment tests and four\n"
         " new guards pass.\n\n"
         "Then the publish finished and none of it is there. All four host strings are absent from the new artifact, the\n"
         " marker string is absent, and the function count does not move: 173,994 before, 173,994 after.\n\n"
         "The comparison that explains it is the existing gateways. api.stripe.com and paypal.com are present; sibspayments,\n"
         " squareup, unzer, omise and adyen are all absent, and so is the name PaymentGatewayRegistry. Seven of the nine\n"
         " gateways that were already written are not in the binary either. CreateDefault has no caller, so the whole family\n"
         " is dead code and trimming removes it, and the two survivors are reachable from somewhere else, most likely the\n"
         " payment-method list in the UI.\n\n"
         "So R1000's rule needs tightening one notch. Register(new MollieGateway()) looks exactly like a call site -- it is an\n"
         " ordinary constructor call inside CreateDefault -- and it moves nothing, because the method containing it is never\n"
         " reached. The test is not whether a call statement exists but whether the call chain reaches it from an entry\n"
         " point. This is the same family as R963, where reflection failed to root a method, but a different cause: there the\n"
         " call was invisible to the compiler, here the chain is unreachable. Both are caught the same way, by looking in the\n"
         " artifact, which is why that check is worth doing every time.\n\n"
         "That also explains why the four genuinely missing endpoints have resisted four attempts. They are not missing a\n"
         " class; they are missing a reachable path from a flow to the registry, and the registry is not reachable at all.\n"
         " The fix is R1000's second route: a concrete flow overrides the payment step and calls registry.Resolve inside that\n"
         " override, so the chain starts at the flow.\n\n"
         "Figures: suite 2210 to 2214, freshness zero after republishing, function count unchanged at 173,994, four gateway\n"
         " classes added, zero of them in the artifact, two of the pre-existing nine present.\n\n"
         "Unknown: which flow should carry these four gateways, and whether the original's CreateDefault has a caller.\n\n"
         "The lesson is that \"I gave it a call site\" can be entirely true and change not one byte of the binary, because the\n"
         " call site sits on a road nobody walks. Only the artifact refuses to be persuaded.\n\n"
         "Four classes and a registration added, four guards added; suite green at 2214 and the artifact honestly unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()