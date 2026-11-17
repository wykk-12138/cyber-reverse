"""Record R992: GetToken is a wire-in gap, not dead code, and its body no longer fabricates."""

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
### `GetToken` 不是死代码，是**接线缺口** —— 而它的身体也不再伪造（R992）

**R991 说下一轮核 `GetToken`（16 字节 CSPRNG hex）是不是同形第二处。核完发现它更接近`HandleBlock`，
而不是`GetPaymentToken`。**

### ① 它是三合一的

```csharp
GetTokenAsync        → Vars["token"] = 16 字节随机 hex
CreateTokenAsync     → => GetTokenAsync
GetAuthTokenAsync    → => GetTokenAsync     // 注释：「Acquire an authorisation token specifically」
```

> **`GetAuthToken` 说它在「取授权令牌」，而它调的是造随机 hex。
> 授权令牌由服务器签发 —— 随机 hex 永远不是。**
> **这比 R991 那个更直接：那个至少叫「获取支付令牌」，这个明说「授权」。**

### ② 而它**完全没被接上**

```
Vars["token"] 的写入点: 1（就是它自己）；读取点: 0
GetTokenAsync / GetAuthTokenAsync / CreateTokenAsync 的调用点: 0（除两个别名互指）
出现在步骤序列里: 无（StoreFlowSteps.cs 无）
字符串形式引用 "GetToken" / "CreateToken" / "GetAuthToken": 0
```

> **所以它是**完全孤立**的：不执行、结果也没人读。
> 而「不执行」正是它活了这么久的原因 —— 与 R991 那条同一个机制，只是更彻底。**

### ③ 而它**不是**死代码该删 —— 三个名字都在原版里

```
recovered_method_names.txt:  CreateToken 行 453 · GetAuthToken 行 1269 · GetToken 行 1595
```

> **→ 形状在、**边**缺失。**
> **而 R955 已经定过这件事：「code is reachable or not, and unreachable code needs a **call**, not a rewrite」。**
> **→ 所以不删、不改名 —— 缺的是一个调用。**
> **→ 而那个调用点需要原版的证据，与 `HandleBlock` 是同一堵墙（名字定位不到代码）。**

### ④ 所以这一轮做的是**把身体改成不伪造**

```csharp
// 改前
var token = Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
c.Session.Vars["token"] = token;
return StepOutcome.Success();

// 改后
return StepOutcome.Fail(
    $"{Name}: no token source is known for this step -- it has never been wired into a flow, and this step will not "
    + "invent a credential", retryable: true);
```

> **理由：接线的人不该拿到一个会造值的身体。**
> **`GetAuthTokenAsync` 说它取授权令牌，而接上它的那一刻，一个随机 hex 就会变成「认证已完成」的信号。
> 那一刻的错误比现在贵得多 —— 因为那时它会**流进请求**。**
> **与 R991 同一条原则：不编造 fallback，缺少就以可诊断的方式缺。**

### ⑤ 而守卫**加宽了一格**，因为它原来漏掉了这个形状

**R991 的守卫匹配 `Token = …Guid.NewGuid`，即**左边是标识符**。
而这里是 `Vars["token"] = <随机字节>` —— **左边是索引器**，所以它漏过去了。**

**加宽后的模式同时匹配两种：**

```
\w*(PaymentToken|AuthToken|AccessToken|CsrfToken|SessionToken)\w*\s*=\s*[^;]*\b(Guid\.NewGuid|RandomNumberGenerator)\b
|
Vars\[\s*""[^""]*(token|nonce|secret|credential)[^""]*""\s*\]\s*=[^;]*\b(RandomNumberGenerator|Guid\.NewGuid)\b
```

> **这与 `flow_work_audit` 那个委派漏洞是同一课：我预期的形状不是它唯一的形状。**

**并新增第 3 条用例 `TheGenericTokenStepAlsoReports`：该方法必须还在、必须含「not invent a credential」、
且源码里不许再出现 `Vars["token"] = token`。**

### ⑥ 守卫验过会红

```
把 Vars["token"] = 随机 hex 放回 1 处
失败!  - 失败: 1，通过: 2，总计: 3
[FAIL] CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally
已还原
```

### 数字

| 度量 | R991 | **R992** |
|---|---|---|
| 套件 | 2207 | **2208（+1 用例）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 0 | **0** |
| **伪造的通用/授权令牌** | 1（`GetToken`） | **0** |
| 本地铸造的凭据（全 src，含会话变量） | 未覆盖索引器形状 | **0** |

### 教训

> **同一个「不执行所以没人反对」的机制，在 R991 那里是兜底从没被走到，
> 在这里是步骤从没被接上 —— 而后者更彻底：连「走到它」这件事都不存在。**
> **而两者的身体都是伪造的。所以「它不执行」不能当成「它没问题」的证据 ——
> 它只说明**现在**没问题，而接上线的那一刻问题才开始，且那时已经没人记得看过它。**
"""

if "`GetToken` 不是死代码" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 992 轮：`GetToken` 不是死代码，是接线缺口 —— 而它的身体也不再伪造

### ① 它是三合一的

```csharp
GetTokenAsync      → Vars["token"] = 16 字节随机 hex
CreateTokenAsync   → => GetTokenAsync
GetAuthTokenAsync  → => GetTokenAsync     // 注释：「Acquire an authorisation token specifically」
```

> **`GetAuthToken` 说它取授权令牌，而它调的是造随机 hex。授权令牌由服务器签发 —— 随机 hex 永远不是。
> 这比 R991 那个更直接：那个叫「获取支付令牌」，这个明说「授权」。**

### ② 而它完全没被接上

```
Vars["token"] 写入点 1（就是它自己）· 读取点 0
三个方法的调用点 0（除两个别名互指）
出现在步骤序列里：无（StoreFlowSteps.cs 无）
字符串引用 "GetToken" / "CreateToken" / "GetAuthToken"：0
```

> **完全孤立：不执行、结果没人读。「不执行」正是它活了这么久的原因。**

### ③ 而它**不是**死代码该删 —— 三个名字都在原版里

```
recovered_method_names.txt:  CreateToken 行 453 · GetAuthToken 行 1269 · GetToken 行 1595
```

> **→ 形状在、**边**缺失。R955 定过：「unreachable code needs a **call**, not a rewrite」。**
> **→ 不删、不改名 —— 缺的是一个调用。而调用点需要原版证据，与 `HandleBlock` 同一堵墙。**

### ④ 所以改的是身体

```csharp
return StepOutcome.Fail(
    $"{Name}: no token source is known for this step -- it has never been wired into a flow, and this step will not "
    + "invent a credential", retryable: true);
```

> **接线的人不该拿到一个会造值的身体。`GetAuthTokenAsync` 说它取授权令牌，
> 而接上它的那一刻，随机 hex 就会变成「认证已完成」的信号 —— 那时它会**流进请求**，错误贵得多。**
> **与 R991 同一条：不编造 fallback，缺少就以可诊断的方式缺。**

### ⑤ 而守卫加宽了一格

**R991 的守卫匹配 `Token = …`（左边是标识符），而这里是 `Vars["token"] = <随机字节>`（左边是**索引器**）→ 漏了。
加宽后两者都匹配。**

> **这与 `flow_work_audit` 那个委派漏洞是同一课：我预期的形状不是它唯一的形状。**

**新增第 3 条用例 `TheGenericTokenStepAlsoReports`。**

### ⑥ 守卫验过会红

```
把 Vars["token"] = 随机 hex 放回 1 处 → 失败: 1，通过: 2
[FAIL] NoCredentialIsMintedLocally → 已还原 → 3 通过
```

### 数字

| 度量 | R991 | **R992** |
|---|---|---|
| 套件 | 2207 | **2208（+1 用例）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的通用/授权令牌 | 1（`GetToken`） | **0** |
| 本地铸造凭据（含会话变量形状） | 未覆盖 | **0** |

### 教训

> **「它不执行」不能当成「它没问题」的证据 —— 它只说明**现在**没问题，
> 而接上线的那一刻问题才开始，且那时已经没人记得看过它。**
"""

BACKLOG_ADD = """

## 优先级 ①/③ — **`GetToken` = 接线缺口（三个名字都在原版）而非死代码；身体已改为报告；守卫加宽至索引器形状**（R992）

### 观察

```csharp
GetTokenAsync      → Vars["token"] = 16 字节随机 hex
CreateTokenAsync   → => GetTokenAsync
GetAuthTokenAsync  → => GetTokenAsync    // 「Acquire an authorisation token specifically」
```

**接线状态：`Vars["token"]` 写入 1 / 读取 0 · 三个方法调用 0 · 不在任何步骤序列 · 字符串引用 0。**

**原版：`recovered_method_names.txt` 有 CreateToken 行 453 · GetAuthToken 行 1269 · GetToken 行 1595
→ **形状在、边缺失**（R955：unreachable code needs a call, not a rewrite）。**

### 改了什么

**身体从「造 16 字节 hex」改成 `Fail($"{Name}: no token source is known … will not invent a credential")`。
理由：接线的人不该拿到会造值的身体；`GetAuthToken` 一旦接上，随机 hex 就变成「认证已完成」并流进请求。**

### 守卫加宽

**R991 的模式只匹配 `Token = <标识符>`；这里是 `Vars["token"] = <随机字节>`（索引器）→ 漏。
加宽后两种形状都匹配。新增 `TheGenericTokenStepAlsoReports`。验过会红（放回 1 处 → 1 失败 2 通过 → 还原 → 3 通过）。**

### 数字

**套件 2208（+1）· 陈旧度 0/0 · 函数数 173,952 · 伪造通用/授权令牌 0 · 本地铸造凭据 0**

| 仍 Unknown | |
|---|---|
| `GetToken` / `GetAuthToken` / `CreateToken` 在原版里被谁调用 | 名字定位不到代码，与 `HandleBlock` 同一堵墙 |

**纪律**：「它不执行」只说明现在没问题，不说明它没问题。
"""

BLOCKER = """

---

## 416. **`GetToken` = 接线缺口而非死代码；身体已改为报告；守卫加宽至索引器形状**

> R992。**改 `StoreFlow.GetTokenAsync` 一处 + 加宽守卫 + 加 1 用例。** 套件 **2208 通过 / 0 失败 / 0 跳过**。

### 一、它是三合一的

```csharp
GetTokenAsync        → Vars["token"] = 16 字节随机 hex
CreateTokenAsync     → => GetTokenAsync
GetAuthTokenAsync    → => GetTokenAsync     // 注释：「Acquire an authorisation token specifically」
```

**→ `GetAuthToken` 说它在「取授权令牌」，而它调的是造随机 hex。
→ 授权令牌由服务器签发 —— 随机 hex 永远不是。
→ 这比 R991 那个更直接：那个至少叫「获取支付令牌」，这个明说「授权」。**

### 二、而它完全没被接上

```
Vars["token"] 的写入点: 1（就是它自己）；读取点: 0
GetTokenAsync / GetAuthTokenAsync / CreateTokenAsync 的调用点: 0（除两个别名互指）
出现在步骤序列里: 无（StoreFlowSteps.cs 无）
字符串形式引用: 0
```

**→ 完全孤立：不执行、结果也没人读。
→ 「不执行」正是它活了这么久的原因 —— 与 R991 同一机制，只是更彻底。**

### 三、而它**不是**死代码该删

```
replica/docs/baseline/recovered_method_names.txt:
  CreateToken  行 453
  GetAuthToken 行 1269
  GetToken     行 1595
```

**→ 三个名字都在原版里 → 形状在、**边**缺失。
→ R955：「code is reachable or not, and unreachable code needs a **call**, not a rewrite」。
→ 所以不删、不改名 —— 缺的是一个调用；而调用点需要原版证据，与 `HandleBlock` 是同一堵墙。**

### 四、所以改的是身体

```csharp
// 改前
var token = Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
c.Session.Vars["token"] = token;
return StepOutcome.Success();

// 改后
return StepOutcome.Fail(
    $"{Name}: no token source is known for this step -- it has never been wired into a flow, and this step will not "
    + "invent a credential", retryable: true);
```

**→ 接线的人不该拿到一个会造值的身体。
→ `GetAuthTokenAsync` 说它取授权令牌，而接上它的那一刻，随机 hex 就会变成「认证已完成」的信号，
而那时它会**流进请求** —— 错误的代价比现在高得多。
→ 与 R991 同一条原则：不编造 fallback，缺少就以可诊断的方式缺。**

### 五、守卫加宽了一格（它原来漏掉了这个形状）

**R991 的模式：`\\w*(PaymentToken|…)\\w*\\s*=\\s*[^;]*\\b(Guid\\.NewGuid|RandomNumberGenerator)\\b`
—— 要求**左边是标识符**。

**这里是 `Vars["token"] = <随机字节>` —— 左边是**索引器**，所以漏过去了。加宽后两种形状都匹配：**

```
Vars\\[\\s*""[^""]*(token|nonce|secret|credential)[^""]*""\\s*\\]\\s*=[^;]*\\b(RandomNumberGenerator|Guid\\.NewGuid)\\b
```

**→ 这与 `flow_work_audit` 那个委派漏洞是同一课：**我预期的形状不是它唯一的形状**。**

**并新增第 3 条用例 `TheGenericTokenStepAlsoReports`：方法必须还在、必须含「not invent a credential」、
且源码里不许再出现 `Vars["token"] = token`。**

### 六、守卫验过会红

```
把 Vars["token"] = 随机 hex 放回 1 处
失败!  - 失败: 1，通过: 2，总计: 3
[xUnit.net] Cybersole.Tests.CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally [FAIL]
exit=1
已还原 → 3 通过
```

### 七、数字

| 度量 | R991 | R992 |
|---|---|---|
| 套件 | 2207 | **2208（+1 用例）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 0 | **0** |
| **伪造的通用/授权令牌** | 1（`GetToken`） | **0** |
| 本地铸造凭据（含会话变量形状） | 未覆盖索引器 | **0** |

### 八、验证

```
cd replica
python tools/snapshot.py                       -> 321 files
dotnet test --filter "FullyQualifiedName~CredentialsAreObtainedNotInvented" -m:1  -> 3 通过
  （把 Vars["token"] = 随机 hex 放回 1 处 -> 1 失败 2 通过 -> 还原 -> 3 通过）
python tools/metrics_report.py                 -> 完整套件 exit 0  2208 通过 / 0 失败 / 0 跳过
```

### 九、仍然 Unknown

- **`GetToken` / `GetAuthToken` / `CreateToken` 在原版里被谁调用**：**Unknown** ——
  名字定位不到代码，与 `HandleBlock` 同一堵墙（字符串无 xref，MethodTable 未通）。

### 十、教训

**同一个「不执行所以没人反对」的机制，在 R991 那里是兜底从没被走到，在这里是步骤从没被接上 ——
后者更彻底：连「走到它」这件事都不存在。**

**而两者的身体都是伪造的。所以「它不执行」不能当成「它没问题」的证据 ——
它只说明**现在**没问题，而接上线的那一刻问题才开始，且那时已经没人记得看过它。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R992", BLOCKER)
    ensure(RSTATUS, "R992", BLOCKER)
    ensure(RVERDICT, "第 992 轮", VERDICT)
    ensure(BACKLOG, "R992", BACKLOG_ADD)

    note = (
        "\n## R992 补充 — **`GetToken` = 接线缺口（三个名字都在原版）而非死代码；身体已改为报告；守卫加宽**（套件 2208）\n\n"
        "`GetTokenAsync` / `CreateTokenAsync` / `GetAuthTokenAsync` **共用一个造 16 字节随机 hex 的身体**，\n"
        "而 `GetAuthTokenAsync` 的注释写着「Acquire an authorisation token specifically」—— 授权令牌由服务器签发。\n\n"
        "接线状态：`Vars[\"token\"]` 写入 1 / **读取 0** · 三个方法**调用 0** · **不在任何步骤序列** · 字符串引用 0。\n"
        "而原版 `recovered_method_names.txt` 里三个名字都在（行 453 / 1269 / 1595）\n"
        "→ **形状在、边缺失**（R955：unreachable code needs a call, not a rewrite）→ **不是死代码该删**。\n\n"
        "所以改的是**身体**：`Fail($\"{Name}: no token source is known … will not invent a credential\")`。\n"
        "理由：接线的人不该拿到会造值的身体 —— 接上那一刻随机 hex 会变成「认证已完成」并流进请求。\n\n"
        "**守卫加宽**：R991 的模式只匹配 `Token = <标识符>`，而这里是 `Vars[\"token\"] = <随机字节>`（索引器）→ 漏。\n"
        "加宽后两种形状都匹配；新增 `TheGenericTokenStepAlsoReports`。**验过会红**（放回 1 处 → 1 失败 2 通过 → 还原 3 通过）。\n\n"
        "数字：套件 2208（+1）· 陈旧度 0/0 · 函数数 173,952 · 伪造通用/授权令牌 0 · 本地铸造凭据 0。\n\n"
        "纪律：**「它不执行」只说明现在没问题，不说明它没问题。**\n\n"
        "下一轮：核 `RefreshSessionAsync` / `HandleResponseAsync`（HANDOFF 记的另两个「真死步骤」）是否同形；\n"
        "或回到优先级 ② —— 风控 vendor 全 matched 之后，核「matched 不等于接上」。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R992" not in h:
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
             for p, k in ((RBLOCK, "R992"), (RSTATUS, "R992"), (RVERDICT, "第 992 轮"), (BACKLOG, "R992")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R992: GetToken is a wire-in gap rather than dead code, and its body stops fabricating\n\n"
         "R991 left the question of whether GetToken, described as sixteen random bytes of hex, repeated the payment-token\n"
         " defect. It does, and it is worse in one respect: three step names share that body, and one of them is\n"
         " GetAuthTokenAsync, whose comment says it acquires an authorisation token specifically. An authorisation token is\n"
         " issued by the server; random hex never is.\n\n"
         "But it is not dead code to delete. Nothing calls the three methods, none of their names appears in a step\n"
         " sequence, the variable they write is read nowhere, and no string reference to them exists anywhere -- so they\n"
         " never run. That is the same mechanism as R991 in a more complete form: there, a fallback was never reached; here,\n"
         " the step was never connected. And all three names sit in the original's recovered method list, at lines 453, 1269\n"
         " and 1595, so the shape is right and what is missing is an edge. Round 955 settled what to do about that: an\n"
         " unreachable function needs a call, not a rewrite.\n\n"
         "So the change is to the body. It now reports that no token source is known and that it will not invent a\n"
         " credential, on the same reasoning as the payment step. Whoever wires it up should not be handed something that\n"
         " makes a value up, because the moment GetAuthTokenAsync is connected, a random hex becomes a signal that\n"
         " authentication finished, and from there it reaches a request.\n\n"
         "The guard had a hole of the same shape as the classifier bug two rounds back. It matched a token-named identifier\n"
         " assigned a generated value, and this code assigns through an indexer, Vars with a string key, which the pattern\n"
         " never looked at. It now matches both forms, and a third test requires the method to remain, to keep saying it\n"
         " will not invent a credential, and to leave no assignment of the old shape behind. Restoring the fabrication for\n"
         " one line produced one failure against two passes; restoring the file produced three passes.\n\n"
         "Figures: suite 2207 to 2208, freshness zero, count 173,952, fabricated general and authorisation tokens one to\n"
         " zero, locally minted credentials across src including session-variable shapes zero.\n\n"
         "Unknown: who calls those three methods in the original, which needs the same access its name has not yet given --\n"
         " no string xrefs and no working MethodTable route, the wall HandleBlock already hit.\n\n"
         "The lesson is that never-running is not evidence of being fine. It says the defect is dormant, not absent, and\n"
         " when the edge is finally added nobody will remember having looked at it.\n\n"
         "One method's body corrected, one guard widened, one test added; suite green at 2208."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()