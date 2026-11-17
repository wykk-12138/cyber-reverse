"""Record R1004: the two absent gateways are present, with their method bodies trimmed."""

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
### Adyen 与 CommerceHub **在**产物里 —— 被裁的是它们的方法体（R1004）

**R1003 留下一句「Adyen 与 CommerceHub 整个不在，问题在 id 没被 `Resolve` 命中」。这一轮查了，
那句话的两半**都要改**。**

### ① 先否掉 id 假设

```csharp
AdyenGateway.Id        => "adyen"
CommerceHubGateway.Id  => "commercehub"

// PaymentGatewayRegistry.Resolve
id is not null && _gateways.TryGetValue(id, out var g) ? g : null;   // 字典是 OrdinalIgnoreCase

// ChooseGateway：返回 available（即 Vars["paymentMethods"]，商店页提供的名字）里的一项
```

> **→ `Resolve` 大小写不敏感，`"adyen"` 能命中。所以 id 不是原因。
> → R1003 那个假设错了。**

### ② 再用**非 host** 的特征串验，仍然全 absent

| 串 | 新产物 |
|---|---|
| `adyen: no card` · `adyen.merchantAccount` · `CybersoleECOM` · `encryptedCardNumber` | **全 absent** |
| `commercehub: sale failed` · `commercehub.sessionId` · `tokenUUID` · `/api/v1/sale` | **全 absent** |

**→ 到这里看起来仍是「整个不在」。**

### ③ 而短串的计数把它翻了过来

```
adyen        UTF-16 x19   UTF-8 x0
commercehub  UTF-16 x17   UTF-8 x0
CommerceHub  UTF-16 x0    UTF-8 x1
square       UTF-16 x10   UTF-8 x7
omise        UTF-16 x52   UTF-8 x89
```

> **`adyen` 出现 **19 次**、`commercehub` **17 次** —— 它们**在**产物里。
> 而它们的长串一个都不在。**
> **→ 所以类被保留（`Id` 可达），`AuthorizeAsync` 的**方法体被裁**。
> → 这是「可达性精确到方法」的**下一层**：**类在、`Id` 在、方法体不在**。**

### ④ 而这解释了两处读数的差

| 说法 | 出处 | 准不准 |
|---|---|---|
| 「整个支付层在产物里几乎不存在」 | R1001 | **不准** —— 类与前两个方法都在 |
| 「9 个网关进了产物」 | R1002 | 偏粗 —— 是 9 个的 `AuthorizeAsync` |
| 「Adyen / CommerceHub 整个不在」 | R1003 | **不准** —— `Id` 在，方法体不在 |

**而三次都是在同一个方向上**高估了裁剪**：把一个方法体的缺席读成一个类、乃至一个层的缺席。**

### ⑤ 而方法体为什么被裁，两个原因不同

**`AdyenGateway.AuthorizeAsync` 里没有 host 串（`ShopperHost` 在 `CompleteActionAsync` / `TokenizeAsync` 里），
它调的是 `Encrypt(...)` 与运行时 URL。**

**`CommerceHubGateway.AuthorizeAsync` 用 `Host(c)` —— 一个**从 session Vars 读 host** 的私有方法，
所以 `DefaultHost` 这个常量只在某个分支里被引用，而那个分支被裁。**

> **→ 两者都不是「不可达」，而是**被裁到了只剩签名**。
> → 而触发裁剪的具体机制（接口派发的类型集合、还是方法体里的某个 `RequiresUnreferencedCode`）
> **本轮未证 —— 标 Unknown。**

### 数字

| 度量 | R1003 | **R1004** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **id 在产物的网关** | 未测 | **13 / 13** |
| **`AuthorizeAsync` 方法体在产物的网关** | 记作 11 | **11** |
| **长特征串全无、id 却在的网关** | 记作 2「整个不在」 | **2（Adyen · CommerceHub）** |

### 教训

> **同一个方向的错误我犯了三次：**把方法体的缺席读成类的缺席**。
> 而这次的判别手段是**短串计数** —— 长串 absent 只说明那一段代码不在，
> 短串计数才说明那个类型的**名字**还在不在。**
> **→ 「在不在产物里」这句话，对长串和对类型名是两个不同的问题，而我一直用一个答案回答两个。**
"""

if "Adyen 与 CommerceHub **在**产物里" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1004 轮：Adyen 与 CommerceHub **在**产物里 —— 被裁的是方法体

### ① 先否掉 id 假设

**`AdyenGateway.Id = "adyen"` · `CommerceHubGateway.Id = "commercehub"` ·
`Resolve` 的字典是 `OrdinalIgnoreCase` · `ChooseGateway` 返回商店页提供名字中的一项。**

> **→ `"adyen"` 能命中。所以 id 不是原因，R1003 那个假设错了。**

### ② 用非 host 特征串验，仍全 absent

| 串 | 新产物 |
|---|---|
| `adyen: no card` · `adyen.merchantAccount` · `CybersoleECOM` · `encryptedCardNumber` | **全 absent** |
| `commercehub: sale failed` · `tokenUUID` · `/api/v1/sale` | **全 absent** |

### ③ 而短串计数把它翻了过来

```
adyen        UTF-16 x19     commercehub  UTF-16 x17
square       UTF-16 x10     omise        UTF-16 x52
```

> **`adyen` 出现 19 次、`commercehub` 17 次 —— 它们**在**产物里，而长串一个都不在。
> → 类被保留（`Id` 可达），`AuthorizeAsync` 的**方法体被裁**。
> → 「可达性精确到方法」的**下一层**：类在、`Id` 在、方法体不在。**

### ④ 三次读数都往同一方向高估了裁剪

| 说法 | 出处 | 准不准 |
|---|---|---|
| 「整个支付层几乎不存在」 | R1001 | **不准** |
| 「9 个网关进了产物」 | R1002 | 偏粗（是 9 个的 `AuthorizeAsync`） |
| 「Adyen / CommerceHub 整个不在」 | R1003 | **不准** |

**→ 三次都是把一个**方法体**的缺席读成一个**类**或一个**层**的缺席。**

### ⑤ 方法体被裁的两个原因不同

**Adyen**：`AuthorizeAsync` 里没有 host 串（`ShopperHost` 在别的两个方法里），它调 `Encrypt(...)` 与运行时 URL。
**CommerceHub**：用 `Host(c)` —— **从 session Vars 读 host** 的私有方法，所以 `DefaultHost` 常量只在被裁的分支里。

> **→ 两者都不是「不可达」，而是被裁到只剩签名。触发机制本轮未证 → Unknown。**

### 数字

| 度量 | R1003 | **R1004** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| **id 在产物的网关** | 未测 | **13 / 13** |
| **`AuthorizeAsync` 体在产物的网关** | 记作 11 | **11** |
| **长串全无、id 却在** | 记作 2「整个不在」 | **2（Adyen · CommerceHub）** |

### 教训

> **同一个方向的错误我犯了三次：把方法体的缺席读成类的缺席。
> 而这次的判别手段是**短串计数** —— 长串 absent 只说明那一段代码不在，
> 短串计数才说明那个类型的**名字**还在不在。**
> **→ 「在不在产物里」对长串和对类型名是两个问题，而我一直用一个答案回答两个。**
"""

BACKLOG_ADD = """

## 判据 (c) — **Adyen/CommerceHub 在产物里，被裁的是方法体；id 假设被否掉**（R1004）

### 否掉 R1003 的 id 假设

**`Id = "adyen"` / `"commercehub"` · `Resolve` 用 `OrdinalIgnoreCase` · `ChooseGateway` 返回商店提供的名字
→ `"adyen"` 能命中 → **不是 id 的问题**。**

### 非 host 特征串：全 absent

**`CybersoleECOM` · `encryptedCardNumber` · `tokenUUID` · `/api/v1/sale` · `commercehub.sessionId` → 全 absent。**

### 短串计数：把它们翻回来

**`adyen` UTF-16 **x19** · `commercehub` **x17** · `square` x10 · `omise` x52**
**→ 类与前两个方法在，`AuthorizeAsync` 的方法体被裁。**

### 三次读数都高估了裁剪

| 说法 | 出处 |
|---|---|
| 「整个支付层几乎不存在」 | R1001 ✗ |
| 「9 个网关进了产物」 | R1002 偏粗 |
| 「Adyen/CommerceHub 整个不在」 | R1003 ✗ |

**→ 都把**方法体**的缺席读成**类/层**的缺席。**

### 方法体被裁的两个原因

- **Adyen**：`AuthorizeAsync` 里无 host 串（`ShopperHost` 在 `CompleteActionAsync`/`TokenizeAsync`），调 `Encrypt(...)`
- **CommerceHub**：`Host(c)` **从 session Vars 读**，`DefaultHost` 常量只在被裁分支里

### 数字

**套件 2214 · 陈旧度 0/0 · 函数数 174,336 · id 在产物 13/13 · `AuthorizeAsync` 体在 11 · 长串全无 2**

| 仍 Unknown | |
|---|---|
| 触发「只留签名」裁剪的具体机制 | 未证 |
| `Host(c)` 从 Vars 读的 host 是否正确 | 需原版证据 |

**纪律**：「在不在产物里」对长串和对类型名是两个问题 —— 我一直用一个答案回答两个。
"""

BLOCKER = """

---

## 428. **Adyen/CommerceHub 在产物里，被裁的是方法体；R1003 的 id 假设被否掉**

> R1004。**未改代码，只取证。** 套件 **2214 通过 / 0 失败 / 0 跳过**。

### 一、先否掉 id 假设

```csharp
AdyenGateway.Id        => "adyen"
CommerceHubGateway.Id  => "commercehub"
// PaymentGatewayRegistry.Resolve: 字典 new(StringComparer.OrdinalIgnoreCase)
// ChooseGateway: 返回 available（Vars["paymentMethods"]，商店页提供的名字）里的一项
```

**→ `Resolve` 大小写不敏感，`"adyen"` 能命中 → **id 不是原因，R1003 那个假设错了。**

### 二、用非 host 的特征串验，仍然全 absent

| 串 | 新产物 |
|---|---|
| `adyen: no card` · `adyen.merchantAccount` · `CybersoleECOM` · `encryptedCardNumber` | **全 absent** |
| `commercehub: sale failed` · `commercehub.sessionId` · `tokenUUID` · `/api/v1/sale` | **全 absent** |

### 三、而短串的计数把它翻了过来

```
adyen        UTF-16 x19   UTF-8 x0
commercehub  UTF-16 x17   UTF-8 x0
CommerceHub  UTF-16 x0    UTF-8 x1
square       UTF-16 x10   UTF-8 x7
omise        UTF-16 x52   UTF-8 x89
paynamics    UTF-16 x7    UTF-8 x0
```

**→ `adyen` 出现 **19 次**、`commercehub` **17 次** —— 它们**在**产物里。
→ 而它们的长串一个都不在。
→ 所以类被保留（`Id` 可达），`AuthorizeAsync` 的**方法体被裁**。
→ 这是「可达性精确到方法」的**下一层**：**类在、`Id` 在、方法体不在。****

### 四、三次读数都往同一方向高估了裁剪

| 说法 | 出处 | 准不准 |
|---|---|---|
| 「整个支付层在产物里几乎不存在」 | R1001 | **不准** |
| 「9 个网关进了产物」 | R1002 | 偏粗（是 9 个的 `AuthorizeAsync`） |
| 「Adyen / CommerceHub 整个不在」 | R1003 | **不准** |

**→ 三次都是把一个**方法体**的缺席读成一个**类**或一个**层**的缺席。**

### 五、方法体被裁的两个原因不同

**`AdyenGateway.AuthorizeAsync`** 里没有 host 串 —— `ShopperHost`
（`checkoutshopper-live.adyen.com`）在 `CompleteActionAsync` / `TokenizeAsync` 里，
而 `AuthorizeAsync` 调的是 `Encrypt(...)` 与运行时构造的 URL。

**`CommerceHubGateway.AuthorizeAsync`** 用 `Host(c)`，而 `Host(c)` 是**从 session Vars 读 host** 的私有方法：

```csharp
var res = await GatewayHttp.PostAsync(c, $"{Host(c)}/api/v1/sale", body, "commercehub-sale", ct);
```

**所以 `DefaultHost`（`commercehub-secure-data-capture.fiservapps.com`）这个常量只在某个分支里被引用，
而那个分支被裁。两者都不是「不可达」，而是被裁到只剩签名。**

### 六、数字

| 度量 | R1003 | R1004 |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **id 在产物的网关** | 未测 | **13 / 13** |
| **`AuthorizeAsync` 体在产物的网关** | 记作 11 | **11** |
| **长特征串全无、id 却在的网关** | 记作 2「整个不在」 | **2（Adyen · CommerceHub）** |

### 七、验证

```
cd replica
python - 读 AdyenGateway.Id -> "adyen"；CommerceHubGateway.Id -> "commercehub"
python - 读 PaymentGatewayRegistry.Resolve -> 字典 StringComparer.OrdinalIgnoreCase
python - 读 ChooseGateway -> 返回 available 里的一项
python - 在 .publish-aot 搜 'CybersoleECOM' / 'encryptedCardNumber' / 'tokenUUID' / '/api/v1/sale' -> 全 absent
python - 计数 'adyen'.encode('utf-16-le') -> 19；'commercehub' -> 17
python tools/metrics_report.py -> 套件 2214 · 陈旧度 0/0 · 函数数 174,336
```

### 八、仍然 Unknown

- **触发「只留签名」裁剪的具体机制**：**Unknown** —— 是接口派发的类型集合、还是方法体里某个
  `RequiresUnreferencedCode`，本轮未证。
- **`CommerceHubGateway.Host(c)` 从 Vars 读的 host 是否正确**：**Unknown** —— 需原版证据。

### 九、教训

**同一个方向的错误我犯了三次：**把方法体的缺席读成类的缺席**。**

**而这次的判别手段是**短串计数** —— 长串 absent 只说明那一段代码不在，
短串计数才说明那个类型的**名字**还在不在。**

**→ 「在不在产物里」这句话，对长串和对类型名是两个不同的问题，
而我一直用一个答案回答两个。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1004", BLOCKER)
    ensure(RSTATUS, "R1004", BLOCKER)
    ensure(RVERDICT, "第 1004 轮", VERDICT)
    ensure(BACKLOG, "R1004", BACKLOG_ADD)

    note = (
        "\n## R1004 补充 — **Adyen/CommerceHub 在产物里，被裁的是方法体；R1003 的 id 假设被否掉**（套件 2214，未改代码）\n\n"
        "**否掉 id 假设**：`Id = \"adyen\"` / `\"commercehub\"` · `Resolve` 用 `OrdinalIgnoreCase` ·\n"
        "`ChooseGateway` 返回商店提供的名字 → `\"adyen\"` 能命中 → **不是 id 的问题**。\n\n"
        "**非 host 特征串全 absent**：`CybersoleECOM` · `encryptedCardNumber` · `tokenUUID` · `/api/v1/sale` · `commercehub.sessionId`。\n\n"
        "**而短串计数把它翻了过来**：`adyen` UTF-16 **x19** · `commercehub` **x17** · `square` x10 · `omise` x52\n"
        "→ **类与前两个方法在产物里，`AuthorizeAsync` 的方法体被裁。**\n"
        "→ 这是「可达性精确到方法」的**下一层**：类在、`Id` 在、方法体不在。\n\n"
        "**三次读数都往同一方向高估了裁剪**：「整个支付层几乎不存在」（R1001 ✗）· 「9 个网关进了」（R1002 偏粗）·\n"
        "「Adyen/CommerceHub 整个不在」（R1003 ✗）—— **都把**方法体**的缺席读成**类/层**的缺席。**\n\n"
        "**原因两个不同**：Adyen 的 `AuthorizeAsync` 里无 host 串（`ShopperHost` 在另两个方法）；\n"
        "CommerceHub 用 `Host(c)`（**从 session Vars 读**），`DefaultHost` 常量只在被裁分支里。\n\n"
        "数字：套件 2214 · 陈旧度 0/0 · 函数数 174,336 · id 在产物 13/13 · `AuthorizeAsync` 体在 11 · 长串全无 2。\n\n"
        "纪律：**「在不在产物里」对长串和对类型名是两个问题 —— 我一直用一个答案回答两个。**\n\n"
        "下一轮：查「只留签名」的触发机制 —— 或换到优先级 ① 的 flow 端点（那条路已有覆写证据）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1004" not in h:
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
             for p, k in ((RBLOCK, "R1004"), (RSTATUS, "R1004"), (RVERDICT, "第 1004 轮"), (BACKLOG, "R1004")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1004: Adyen and CommerceHub are in the artifact; what was trimmed is their method bodies\n\n"
         "R1003 closed by blaming an id mismatch for the two gateways whose hosts were missing. Both halves of that need\n"
         " correcting.\n\n"
         "The ids are fine. AdyenGateway reports \"adyen\", CommerceHubGateway reports \"commercehub\", the registry's\n"
         " dictionary compares case-insensitively, and ChooseGateway returns one of the names the shop offered. So Resolve\n"
         " would find them.\n\n"
         "Searching for non-host strings from those two classes -- CybersoleECOM, encryptedCardNumber, tokenUUID,\n"
         " /api/v1/sale -- returns nothing, which still looks like wholesale absence. Then counting the short names turns it\n"
         " around: adyen appears nineteen times in the artifact as UTF-16 and commercehub seventeen. The classes are there\n"
         " and so is the identifier; what is gone is the body of AuthorizeAsync.\n\n"
         "That makes three readings in a row that overestimated the trimming in the same direction. R1001 said the payment\n"
         " layer barely exists, R1002 said nine gateways arrived, R1003 said these two were entirely absent. Each time a\n"
         " missing method body was read as a missing class, and once as a missing layer.\n\n"
         "The two causes differ. Adyen's AuthorizeAsync carries no host string at all -- ShopperHost belongs to\n"
         " CompleteActionAsync and TokenizeAsync, and the authorise path builds its URL at runtime around an Encrypt call.\n"
         " CommerceHub builds its URL from Host(c), a private method that reads the host out of session variables, so the\n"
         " DefaultHost constant is referenced only inside a branch that was trimmed.\n\n"
         "Neither is unreachable, which is the interesting part. What mechanism leaves a type and its identifier present\n"
         " while removing a method body is not established, and I am marking it unknown rather than guessing.\n\n"
         "Figures: suite 2214 unchanged, freshness zero, count 174,336, ids present for thirteen of thirteen gateways,\n"
         " AuthorizeAsync bodies present for eleven, two with no long string at all but their id intact.\n\n"
         "The lesson is that whether something is in the artifact is two different questions depending on whether you ask\n"
         " it of a long string or of a type name, and I have been answering both with one answer.\n\n"
         "No product code changed; two claims corrected and one search discipline added."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()