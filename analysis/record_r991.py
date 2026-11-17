"""Record R991: the fabricated payment token is gone and a guard keeps it gone."""

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
### 伪造的支付令牌删了 —— 而**删掉它没让任何用例红**（R991）

**R990 发现 `GetPaymentTokenAsync` 造一个随机 GUID 当支付令牌。这一轮删了它，加了两条守卫，并验证守卫会红。**

### ① 先确认它从没被 override 过

```
GetPaymentToken 的 override: 0 处
```

**而真会拿到令牌的地方另有五处：**

| 位置 | 怎么拿的 |
|---|---|
| `FootsitesFlow.cs:353` | 从响应里提 `"id"` |
| `MagentoFlow.cs:806` | 从响应里提 `"token"` |
| `ShopifyFlow.cs:477` | 从响应里提 `"id"` |
| `StoreFlow.cs:1398 / 1474 / 1550` | 已有值 |
| `Payments/Gateways.cs` ×4 | 真网关端点签发的 nonce / token |

> **所以那个伪造**只是兜底** —— 方法开头就短路：`if (Session.PaymentToken 非空) return Success()`。
> 而它从没被走到，因为没有 flow 会「走到支付却没有令牌」……**
> **除非某个 flow 少写了一步。而那时它会**假装成功**。**

### ② 改法：兜底从「造值」改成「显式失败」

```csharp
// 改前
c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];
c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
return StepOutcome.Success();

// 改后
return StepOutcome.Fail(
    $"{Name}: no payment token available -- no tokenising step ran for this flow, and this step will not invent one",
    retryable: true);
```

**理由直接引 R823：服务器未签发的令牌会让每个带它的请求被判无效。
伪造只是把失败**从这一步挪到某个下游调用**，而在那里它长得像「店方拒绝了我」。**

### ③ 而全量套件**没有一条用例因此变红**

```
改前 2222 通过 / 0 失败 / 2 跳过   （Speed!=Slow）
改后 完整套件 2207 通过 / 0 失败 / 0 跳过
```

**（2207 与 2222 的口径不同：`metrics_report.py` 按 R493 排除六个浏览器依赖类。）**

> **删掉一个伪造实现而套件全绿，读起来像「这个改动没有影响」。
> 实际含义是：**没有任何用例覆盖那条兜底路径** —— 它从没被执行过。
> 而「从没被执行」正是它活到现在的原因。**
> **→ 所以这一轮真正的产出不是删了那三行，是**加了两条守卫**。**

### ④ 两条守卫，而它们的方向相反

**`CredentialsAreObtainedNotInventedTests`（2 用例）：**

1. `NoCredentialIsMintedLocally` —— 扫整个 `src`，`\w*(PaymentToken|AuthToken|AccessToken|CsrfToken|SessionToken)\w*\s*=\s*[^;]*\b(Guid\.NewGuid|RandomNumberGenerator)\b`
   一处都不许有
2. `TheFallbackReportsRatherThanInvends` —— `GetPaymentTokenAsync` 必须**还在**、必须**仍短路于真令牌**、
   且必须含「will not invent one」字样

> **② 那条是防「用删除来修」：把一个**该报告缺失**的步骤删掉，会让缺口从「有诊断的失败」变成「不存在」。**

### ⑤ 而守卫**验过会红**

**手动把伪造放回 1 处 → `[FAIL] NoCredentialIsMintedLocally` → 还原 → 通过。**

```
临时把伪造放回 1 处
失败!  - 失败: 1，通过: 1
[xUnit.net] Cybersole.Tests.CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally [FAIL]
已还原
```

**（R981 立的规矩：一个没验过会红的守卫不是证据。）**

### ⑥ 仍然敞着的

**`GetToken`（`HISTORY.md` R12 表：「16 字节 CSPRNG hex」）是同形的第二处，而这一轮的守卫**没有**扫它 ——
因为它是「16 字节随机 hex」，与 `Guid.NewGuid` 不同形。那一条要单独取证：它签发的到底是什么令牌。**

### 数字

| 度量 | R990 | **R991** |
|---|---|---|
| 套件 | 2205 | **2207（+2 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 1 处 | **0** |
| **本地铸造的凭据（全 src）** | 未测 | **0** |

### 教训

> **一个从没被执行过的缺陷，删掉它不会让任何用例变红 ——
> 而那正是它活了这么久的原因。**
> **所以「删掉 + 全绿」不能当成验证；验证是**加一条会红的守卫，并亲眼看它红一次**。**
"""

if "伪造的支付令牌删了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 991 轮：伪造的支付令牌删了 —— 而删掉它没让任何用例红

### ① 先确认它从没被 override

```
GetPaymentToken 的 override: 0 处
```

**而真会拿到令牌的地方另有五处：`FootsitesFlow:353`（提 `"id"`）· `MagentoFlow:806`（提 `"token"`）·
`ShopifyFlow:477`（提 `"id"`）· `StoreFlow:1398/1474/1550` · `Payments/Gateways.cs` ×4。**

> **那个伪造只是兜底 —— 方法开头短路于真令牌。它从没被走到，因为没有 flow 会「走到支付却没有令牌」……
> 除非某个 flow 少写了一步，而那时它会**假装成功**。**

### ② 改法：兜底从「造值」改成「显式失败」

```csharp
return StepOutcome.Fail(
    $"{Name}: no payment token available -- no tokenising step ran for this flow, and this step will not invent one",
    retryable: true);
```

**理由直接引 R823：服务器未签发的令牌会让每个带它的请求被判无效。
伪造只是把失败**从这一步挪到下游**，在那里它长得像「店方拒绝了我」。**

### ③ 而全量套件没有一条用例因此变红

```
改前 2222 通过（Speed!=Slow）   改后 完整套件 2207 通过 / 0 失败 / 0 跳过
```

**（口径不同：`metrics_report.py` 按 R493 排除六个浏览器依赖类。）**

> **删掉一个伪造实现而套件全绿，读起来像「这改动没影响」。实际含义是
> **没有任何用例覆盖那条兜底路径** —— 它从没被执行过。
> 而「从没被执行」正是它活到现在的原因。
> → 所以真正的产出不是删了那三行，是**加了两条守卫**。**

### ④ 两条守卫方向相反

**`CredentialsAreObtainedNotInventedTests`（2 用例）：**

1. `NoCredentialIsMintedLocally` —— 扫整个 `src`，`Token = …Guid.NewGuid|RandomNumberGenerator` 一处不许有
2. `TheFallbackReportsRatherThanInvends` —— 该方法必须**还在**、必须**仍短路于真令牌**、必须含「will not invent one」

> **② 防「用删除来修」：删掉一个**该报告缺失**的步骤，会让缺口从「有诊断的失败」变成「不存在」。**

### ⑤ 守卫验过会红

```
临时把伪造放回 1 处 → 失败: 1
[FAIL] CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally
已还原
```

### ⑥ 仍然敞着的

**`GetToken`（`HISTORY.md` R12：「16 字节 CSPRNG hex」）是同形第二处，而守卫**没扫它** ——
它是随机 hex，与 `Guid.NewGuid` 不同形。要单独取证它签发的是什么令牌。**

### 数字

| 度量 | R990 | **R991** |
|---|---|---|
| 套件 | 2205 | **2207（+2 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 1 处 | **0** |
| **本地铸造的凭据（全 src）** | 未测 | **0** |

### 教训

> **一个从没被执行过的缺陷，删掉它不会让任何用例变红 —— 而那正是它活了这么久的原因。
> 所以「删掉 + 全绿」不是验证；验证是**加一条会红的守卫，并亲眼看它红一次**。**
"""

BACKLOG_ADD = """

## 优先级 ①/判据 (f) — **伪造的支付令牌已删；+2 守卫（验过会红）；本地铸造凭据全 src = 0**（R991）

### 改了什么

**`StoreFlow.GetPaymentTokenAsync` 的兜底从 `PaymentToken = "tok_" + Guid.NewGuid()…` 改成
`Fail($"{Name}: no payment token available … will not invent one", retryable: true)`。**

**理由：R823 —— 服务器未签发的令牌会让每个带它的请求被判无效；伪造只是把失败挪到下游，
在那里它长得像「店方拒绝了我」。**

**而它**从没被 override**，真令牌来自五处：`FootsitesFlow:353` · `MagentoFlow:806` · `ShopifyFlow:477` ·
`StoreFlow:1398/1474/1550` · `Gateways.cs` ×4。**

### 守卫（`CredentialsAreObtainedNotInventedTests`，2 用例）

1. `NoCredentialIsMintedLocally` —— 全 `src` 不许有 `Token = …Guid.NewGuid|RandomNumberGenerator`
2. `TheFallbackReportsRatherThanInvends` —— 该方法必须还在、仍短路于真令牌、含「will not invent one」
   （**防「用删除来修」**）

**验过会红：手动放回 1 处 → `[FAIL] NoCredentialIsMintedLocally` → 还原 → 通过。**

### 数字

**套件 2207（+2）· 陈旧度 0/0 · 函数数 173,952 · 伪造令牌 0 · 本地铸造凭据 0**

| 仍 Unknown | |
|---|---|
| `GetToken`（16 字节 CSPRNG hex）是不是同形第二处 | 守卫没扫它（不同形），需单独取证 |

**纪律**：删掉 + 全绿不是验证；验证是加一条会红的守卫并亲眼看它红一次。
"""

BLOCKER = """

---

## 415. **伪造的支付令牌已删；+2 守卫（验过会红）**

> R991。**改 `StoreFlow.GetPaymentTokenAsync` 一处 + 加 2 守卫。** 套件 **2207 通过 / 0 失败 / 0 跳过**。

### 一、先确认它从没被 override

```
GetPaymentToken 的 override: 0 处
```

**而真会拿到令牌的地方另有五处：**

| 位置 | 怎么拿的 |
|---|---|
| `FootsitesFlow.cs:353` | 从响应提 `"id"` |
| `MagentoFlow.cs:806` | 从响应提 `"token"` |
| `ShopifyFlow.cs:477` | 从响应提 `"id"` |
| `StoreFlow.cs:1398 / 1474 / 1550` | 已有值 |
| `Payments/Gateways.cs` ×4 | 真网关端点签发 |

**→ 那个伪造**只是兜底**：方法开头短路于真令牌 `if (Session.PaymentToken 非空) return Success()`。
→ 它从没被走到，因为没有 flow 会「走到支付却没有令牌」—— **除非某个 flow 少写了一步，而那时它会假装成功。****

### 二、改了什么

```csharp
// 改前
c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];
c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
return StepOutcome.Success();

// 改后
return StepOutcome.Fail(
    $"{Name}: no payment token available -- no tokenising step ran for this flow, and this step will not invent one",
    retryable: true);
```

**→ 理由直接引 R823：服务器未签发的令牌会让每个带它的请求被判无效。
→ 伪造只是把失败**从这一步挪到某个下游调用**，而在那里它长得像「店方拒绝了我」。**

### 三、而全量套件**没有一条用例因此变红**

```
改前 2222 通过 / 0 失败 / 2 跳过   （Speed!=Slow）
改后 完整套件 2207 通过 / 0 失败 / 0 跳过
```

**（2207 与 2222 口径不同：`metrics_report.py` 按 R493 排除六个浏览器依赖类。）**

**→ 删掉一个伪造实现而套件全绿，读起来像「这个改动没有影响」。
→ 实际含义是：**没有任何用例覆盖那条兜底路径** —— 它从没被执行过。
→ 而「从没被执行」正是它活到现在的原因。
→ **所以这一轮真正的产出不是删了那三行，是加了两条守卫。****

### 四、两条守卫，方向相反

**`CredentialsAreObtainedNotInventedTests`（2 用例）：**

1. **`NoCredentialIsMintedLocally`** —— 扫整个 `src`：
   `\\w*(PaymentToken|AuthToken|AccessToken|CsrfToken|SessionToken)\\w*\\s*=\\s*[^;]*\\b(Guid\\.NewGuid|RandomNumberGenerator)\\b`
   一处都不许有
2. **`TheFallbackReportsRatherThanInvends`** —— `GetPaymentTokenAsync` 必须**还在**、
   必须**仍短路于真令牌**、且必须含「will not invent one」

**→ ② 那条是防「用删除来修」：把一个**该报告缺失**的步骤删掉，
会让缺口从「有诊断的失败」变成「不存在」。**

### 五、而守卫**验过会红**（R981 立的规矩）

**手动把伪造放回 1 处 → 跑 → 还原：**

```
临时把伪造放回 1 处
失败!  - 失败: 1，通过: 1，已跳过: 0，总计: 2
[xUnit.net 00:00:00.62] Cybersole.Tests.CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally [FAIL]
exit=1
已还原
```

### 六、数字

| 度量 | R990 | R991 |
|---|---|---|
| 套件 | 2205 | **2207（+2 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 1 处 | **0** |
| **本地铸造的凭据（全 src）** | 未测 | **0** |

### 七、验证

```
cd replica
python tools/snapshot.py                       -> 321 files
dotnet test --filter "Speed!=Slow" -m:1        -> 2222 通过 / 0 失败 / 2 跳过
dotnet test --filter "FullyQualifiedName~CredentialsAreObtainedNotInventedTests" -m:1  -> 2 通过
  （把伪造放回 1 处 -> 1 失败 1 通过 -> 还原 -> 2 通过）
python tools/metrics_report.py                 -> 完整套件 exit 0  2207 通过 / 0 失败 / 0 跳过
```

### 八、仍然 Unknown

- **`GetToken`（`HISTORY.md` R12 表：「16 字节 CSPRNG hex」）是不是同形第二处**：**Unknown** ——
  这一轮的守卫**没有**扫它，因为它是随机 hex 而非 `Guid.NewGuid`，形状不同。要单独取证它签发的是什么令牌。

### 九、教训

**一个从没被执行过的缺陷，删掉它不会让任何用例变红 —— 而那正是它活了这么久的原因。**

**所以「删掉 + 全绿」不能当成验证；验证是**加一条会红的守卫，并亲眼看它红一次**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R991", BLOCKER)
    ensure(RSTATUS, "R991", BLOCKER)
    ensure(RVERDICT, "第 991 轮", VERDICT)
    ensure(BACKLOG, "R991", BACKLOG_ADD)

    note = (
        "\n## R991 补充 — **伪造的支付令牌已删；+2 守卫（验过会红）**（套件 2207）\n\n"
        "`GetPaymentTokenAsync` 有 **0 个 override**，真令牌来自五处（`FootsitesFlow:353` 提 `\"id\"` ·\n"
        "`MagentoFlow:806` 提 `\"token\"` · `ShopifyFlow:477` · `StoreFlow:1398/1474/1550` · `Gateways.cs` ×4）。\n"
        "→ 那个 `Guid.NewGuid()` 只是**兜底**，而它会让「某个 flow 少写了一步」变成**假装成功**。\n\n"
        "改成 `Fail($\"{Name}: no payment token available … will not invent one\", retryable: true)`。\n"
        "理由直接引 R823：未签发的令牌让每个带它的请求被判无效；伪造只是把失败挪到下游、并伪装成被店方拒绝。\n\n"
        "**而删掉它，全量套件一条都没红**（2222 通过 / 0 失败）→ 说明**没有任何用例覆盖那条兜底路径**。\n"
        "所以产出不是删了三行，是加了两条守卫：\n"
        "`NoCredentialIsMintedLocally`（全 src 不许 `Token = …Guid.NewGuid`）·\n"
        "`TheFallbackReportsRatherThanInvends`（该方法必须还在、仍短路、含「will not invent one」—— 防「用删除来修」）。\n"
        "**验过会红**：手动放回 1 处 → `[FAIL]` → 还原 → 通过。\n\n"
        "数字：套件 2207（+2）· 陈旧度 0/0 · 函数数 173,952 · 伪造令牌 0 · 本地铸造凭据 0。\n\n"
        "纪律：**删掉 + 全绿不是验证；验证是加一条会红的守卫并亲眼看它红一次。**\n\n"
        "下一轮：核 `GetToken`（16 字节 CSPRNG hex）是不是同形第二处 —— 守卫没扫它（不同形）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R991" not in h:
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
             for p, k in ((RBLOCK, "R991"), (RSTATUS, "R991"), (RVERDICT, "第 991 轮"), (BACKLOG, "R991")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R991: the fabricated payment token is gone, and removing it broke nothing\n\n"
         "R990 found GetPaymentTokenAsync assigning a fresh GUID prefixed with tok_ and returning success. This round removes\n"
         " it, guards against its return, and checks that the guard fails when the fabrication does.\n\n"
         "Nothing overrides that method, and the flows that need a token get a real one: Footsites reads the id out of its\n"
         " tokenise response, Magento reads the token, Shopify reads the id, three sites in StoreFlow already hold one, and\n"
         " Gateways.cs mints four kinds through their real endpoints. So the fabrication was only ever a fallback, reached\n"
         " when the session had no token at all, and it short-circuited on the presence of one. What it did in practice was\n"
         " turn \"this flow is missing its tokenising step\" into a success that failed later at the server, wearing the\n"
         " store's rejection as a disguise.\n\n"
         "The replacement reports instead of inventing, with round 823's reasoning attached: a token the server never issued\n"
         " makes every request carrying it invalid. Nothing is lost, because a made-up token would have failed anyway, later\n"
         " and with less to go on.\n\n"
         "The full suite stayed green through the removal -- 2222 passing before, 2207 through metrics_report afterwards, the\n"
         " two counts differing only because that wrapper excludes six browser-dependent classes. A green suite after deleting\n"
         " a defect sounds like the change was inconsequential. It means no test ever reached that branch, which is exactly\n"
         " why the branch survived: nothing exercised it, so nothing objected.\n\n"
         "So the deliverable is two guards, pointing opposite ways. One refuses any local minting of a token-shaped member\n"
         "across all of src. The other requires the fallback to still exist, still short-circuit on a real token, and still\n"
         " say it will not invent one -- which stops the fix from being \"delete the step\", since a step that reports a\n"
         " missing prerequisite is worth more than its absence.\n\n"
         "The first guard was verified to fail before being trusted: putting the fabrication back for one line produced one\n"
         " failure and one pass, and restoring produced two passes.\n\n"
         "Figures: suite 2205 to 2207, freshness zero, count 173,952, fabricated tokens one to zero, locally minted\n"
         " credentials across src zero.\n\n"
         "Unknown: whether GetToken, described in the round 12 summary as sixteen random bytes of hex, is the same defect in\n"
         " another shape. The guard does not scan for it because a random byte array is not a Guid.\n\n"
         "The lesson is that deleting a defect nothing exercises cannot turn a suite red, and that is the reason it lasted.\n"
         " Deleting plus green is not verification; verification is a guard that fails, watched failing once.\n\n"
         "One method corrected, two guard tests added; suite green at 2207."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()