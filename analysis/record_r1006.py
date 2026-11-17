"""Record R1006: the message layer is right and did not reach the artifact, and my reachability readings disagree with themselves."""

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
### 消息层写对了，没进产物 —— 而我的「可达性」读数自己和自己矛盾（R1006）

**R1005 说下一轮按三条证据加消息层。加了，11 条测试绿。而 publish 之后产物里一个串都不在。
更要紧的是：这一轮把 R1002 那个可达性结论**否掉了**。**

### ① 写了什么

**`StoreFlowRunner.ClassifyCheckoutFailure` 前面加一层消息判断：**

```csharp
private static readonly string[] RetryableShortage = { "reservation failed" };
private static readonly string[] NeverRetryShortage = { "decoy" };

private static CheckoutResult ClassifyCheckoutFailure(FlowContext ctx) =>
    FromShortageMessage(ctx) ?? LastStatus(ctx) switch
    {
        422 or 409 => CheckoutResult.Declined,
        402 => CheckoutResult.Declined,
        _ => CheckoutResult.Error,
    };
```

**顺序是「状态码是外层猜测，消息细化它」—— 因为多数 409 确实是售罄，而那一个例外在体里说出来。
两个标记同时出现时**拒绝优先**：错的重试花掉账号，错的放弃只花掉这一次尝试。**

**而 `Vars["home"]` 是**首页**，缺货消息在 **checkout 响应**里 —— 所以补了一个新活通道：
`lastStatus` 的 5 个写入点旁边各写一行 `Vars["lastBody"]`。**

**11 条测试绿（4 新 + 7 既有 `CheckoutFailureModeTests`，`{}` 体无标记 → 仍 `Declined`，没破既有行为）。**

### ② 而 publish 之后，产物里一个都不在

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| `reservation failed` | **absent** | absent |
| `decoy` | **absent** | absent |
| **`lastBody`** | **absent** | absent |
| `sold out during checkout`（既有注释） | absent | absent |

**→ 函数数 **174,336 未变**。**

### ③ 而判别组把 R1002 的结论否掉了

| 串 | 新产物 | **R1002 我记的** |
|---|---|---|
| `StoreFlowRunner` | **absent** | **IN** |
| `GuardAsync` | **absent** | **IN** |
| `lastStatus` | **absent** | absent（一致） |
| `antibot` | IN | IN |

> **→ `StoreFlowRunner` 与 `GuardAsync` 现在 absent，而 R1002 我记的是 IN。
> → 而函数数在 R1002 之后**没变**（174,336 → 174,336），所以这不是裁剪变化。
> → 所以**其中一次的读数是错的**，而我留的记录不足以判断是哪一次。**

### ④ 而这否掉的不止一条读数

**R1002 的 `+342` 我用它论证「接一句 `Resolve` 就让 250 行达标」。而那个论证的可达性依据
（`StoreFlowRunner` / `GuardAsync` 在产物里）现在不成立。**

**→ `+342` 仍然是真的（函数数确实涨了）。但「为什么涨」的那个解释建立在一条现在矛盾的读数上。
→ 而 R1004「Adyen/CommerceHub 的 `Id` 在产物里 19/17 次」那条也是同类读数 —— 同样需要重验。**

**这一轮不重验，因为重验需要一条**稳定的**读数方法，而那件事本身要先设计。**

### ⑤ 所以这一轮真正的产出是三条

1. **消息层在源码与测试里正确**（11 条绿），而**产物里不在** —— 那一条是清楚的、可复现的
2. **`lastBody` 通道补上了**（`home` 是首页，缺货消息在 checkout 响应里 —— 那是实现里的一个真错）
3. **R1002 的可达性结论撤回** —— 依据是同一段字节里 `StoreFlowRunner` absent，而函数数未变

### ⑥ 而「读数不稳定」的可能原因（未证，标 Unknown）

- 两次查的**不是同一个文件**（R1002 查 `.publish-aot`，那一份在 R999 之后被替换过两次）
- 或者某次 publish 的裁剪结果不同而函数数恰好相同
- **而未证的我不写成结论。**

### 数字

| 度量 | R1005 | **R1006** |
|---|---|---|
| 套件 | 2214 | **2218（+4 缺货消息守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 174,336 | **174,336（未变）** |
| 函数比 | 62.91% | **62.91%** |
| **消息层进产物** | — | **否（3 个串全 absent）** |
| **R1002 的可达性读数** | 采信 | **撤回（与当前读数矛盾）** |

### 教训

> **产物读数是一个**观测**，而观测要有稳定的对象和记录。我拿三次不同 publish 的读数当一条时间线用，
> 于是其中任何一次读错都会变成一个「事实」进入论证。**
> **→ 而这一轮能发现它，是因为我**又查了一遍**同样几个串 —— 不是因为方法更好。**
"""

if "消息层写对了，没进产物" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1006 轮：消息层写对了，没进产物 —— 而我的可达性读数自己和自己矛盾

### ① 写了什么

**`StoreFlowRunner.ClassifyCheckoutFailure` 加了一层消息判断：**

```csharp
private static readonly string[] RetryableShortage = { "reservation failed" };
private static readonly string[] NeverRetryShortage = { "decoy" };

private static CheckoutResult ClassifyCheckoutFailure(FlowContext ctx) =>
    FromShortageMessage(ctx) ?? LastStatus(ctx) switch { 422 or 409 => Declined, 402 => Declined, _ => Error };
```

**顺序：状态码是外层猜测，消息细化它。两个标记同时出现时**拒绝优先**
（错的重试花掉账号，错的放弃只花掉这一次尝试）。**

**并补了一个新活通道：`lastStatus` 的 5 个写入点旁各写 `Vars["lastBody"]`
（`home` 是**首页**，缺货消息在 **checkout 响应**里 —— 那是实现里的一个真错）。**

**11 条测试绿。**

### ② 而 publish 之后，产物里一个都不在

| 串 | 新 | 旧 |
|---|---|---|
| `reservation failed` · `decoy` · **`lastBody`** · `sold out during checkout` | **全 absent** | absent |

**函数数 **174,336 未变**。**

### ③ 判别组把 R1002 否掉了

| 串 | 新产物 | R1002 我记的 |
|---|---|---|
| `StoreFlowRunner` | **absent** | **IN** |
| `GuardAsync` | **absent** | **IN** |
| `antibot` | IN | IN |

> **而函数数在 R1002 之后**没变**（174,336 → 174,336），所以这不是裁剪变化。
> → 其中一次读数是错的，而我留的记录不足以判断是哪一次。**

### ④ 这否掉的不止一条读数

**R1002 的 `+342` 我用来论证「接一句 `Resolve` 就让 250 行达标」。而那个论证的可达性依据
（`StoreFlowRunner` / `GuardAsync` 在产物里）现在不成立。**

**→ `+342` 仍是真的（函数数确实涨了）。但「为什么涨」的解释建立在一条现在矛盾的读数上。
→ R1004「Adyen/CommerceHub 的 `Id` 在产物里 19/17 次」也是同类读数，同样需重验。**

### ⑤ 三条产出

1. **消息层源码与测试正确（11 绿），产物里不在** —— 清楚、可复现
2. **`lastBody` 通道补上**（`home` 是首页，消息在 checkout 响应里）
3. **R1002 的可达性结论撤回**

### ⑥ 读数不稳定的可能原因（未证，Unknown）

- 两次查的不是同一个文件（`.publish-aot` 在 R999 后被替换两次）
- 或某次 publish 裁剪不同而函数数恰好相同
- **未证的我不写成结论。**

### 数字

| 度量 | R1005 | **R1006** |
|---|---|---|
| 套件 | 2214 | **2218（+4）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 174,336 | **174,336（未变）** |
| **消息层进产物** | — | **否** |
| **R1002 的可达性读数** | 采信 | **撤回** |

### 教训

> **产物读数是一个**观测**，而观测要有稳定的对象和记录。我拿三次不同 publish 的读数当一条时间线用，
> 于是其中任何一次读错都会变成一个「事实」进入论证。
> → 这一轮能发现它，是因为我**又查了一遍**同样几个串 —— 不是因为方法更好。**
"""

BACKLOG_ADD = """

## 判据 (a)/①/(c) — **消息层实现正确（11 绿）但未进产物；`lastBody` 通道补上；R1002 可达性结论撤回**（R1006）

### 实现

**`ClassifyCheckoutFailure` 前加消息层：`reservation failed` → `Error`（可重试）· `decoy` → `Declined`（不重试）·
两者同时出现拒绝优先。状态码层保持保守。**
**`lastStatus` 的 5 个写入点旁各写 `Vars["lastBody"]`（`home` 是首页，消息在 checkout 响应里）。**
**11 条测试绿（4 新 + 7 既有）。**

### 产物验证（否定）

**`reservation failed` · `decoy` · `lastBody` · `sold out during checkout` 全 absent；函数数 174,336 未变。**

### 自我否证

| 串 | 新产物 | R1002 记录 |
|---|---|---|
| `StoreFlowRunner` | **absent** | **IN** |
| `GuardAsync` | **absent** | **IN** |
| `antibot` | IN | IN |

**→ 函数数在 R1002 之后未变 ⇒ 不是裁剪变化 ⇒ 其中一次读数错了。
→ R1002 的「+342 因为可达」解释与 R1004 的「Id 在产物里」读数都需要重验。
→ 需要一条**稳定的**产物读数方法先。**

### 数字

**套件 2218 · 陈旧度 0/0 · 函数数 174,336 · 消息层进产物 否 · R1002 可达性 撤回**

| 仍 Unknown | |
|---|---|
| 读数为何矛盾 | 未证（不同文件？裁剪巧合？） |
| 消息层怎样才能进产物 | 未证 |

**纪律**：产物读数是观测 —— 观测要有稳定的对象和记录。
"""

BLOCKER = """

---

## 430. **消息层实现正确但未进产物；`lastBody` 通道补上；R1002 可达性结论撤回**

> R1006。**改 2 个源 + 1 个测试文件。** 套件 **2218 通过 / 0 失败 / 0 跳过**。

### 一、实现

**`StoreFlowRunner.cs`：**

```csharp
private static readonly string[] RetryableShortage = { "reservation failed" };
private static readonly string[] NeverRetryShortage = { "decoy" };

private static CheckoutResult? FromShortageMessage(FlowContext ctx)
{
    var body = ctx.Session.Vars.TryGetValue("lastBody", out var b) && !string.IsNullOrEmpty(b)
        ? b
        : ctx.Session.Vars.TryGetValue("home", out var h) ? h : null;
    if (string.IsNullOrEmpty(body)) return null;

    foreach (var marker in NeverRetryShortage)
        if (body.Contains(marker, StringComparison.OrdinalIgnoreCase)) return CheckoutResult.Declined;

    foreach (var marker in RetryableShortage)
        if (body.Contains(marker, StringComparison.OrdinalIgnoreCase)) return CheckoutResult.Error;

    return null;
}

private static CheckoutResult ClassifyCheckoutFailure(FlowContext ctx) =>
    FromShortageMessage(ctx) ?? LastStatus(ctx) switch
    {
        422 or 409 => CheckoutResult.Declined,
        402 => CheckoutResult.Declined,
        _ => CheckoutResult.Error,
    };
```

**`StoreFlow.cs`：`lastStatus` 的 **5** 个写入点旁各写一行 `Vars["lastBody"] = res.Body ?? string.Empty;`
（`home` 是**首页**，而缺货消息在 **checkout 响应**里 —— 那是实现里的一个真错，本轮修掉）。**

**测试 `ShortageMessageTests.cs` 4 条 + 既有 `CheckoutFailureModeTests` 7 条 → **11 通过**。
（`{}` 体无标记 → 仍 `Declined`，既有行为未被破坏。）**

### 二、而 publish 之后，产物里一个都不在

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| `reservation failed` | **absent** | absent |
| `decoy` | **absent** | absent |
| **`lastBody`** | **absent** | absent |
| `sold out during checkout`（既有注释） | absent | absent |

**→ 函数数 **174,336 未变**。**

### 三、判别组把 R1002 的结论否掉了

| 串 | 新产物 | **R1002 我记的** |
|---|---|---|
| `StoreFlowRunner` | **absent** | **IN** |
| `GuardAsync` | **absent** | **IN** |
| `lastStatus` | **absent** | absent（一致） |
| `antibot` | IN | IN |

**→ `StoreFlowRunner` 与 `GuardAsync` 现在 absent，而 R1002 记的是 IN。
→ 而函数数在 R1002 之后**没变**（174,336 → 174,336），所以这不是裁剪变化。
→ 所以**其中一次的读数是错的**，而我留的记录不足以判断是哪一次。**

### 四、这否掉的不止一条读数

**R1002 的 `+342` 我用它论证「接一句 `Resolve` 就让 250 行达标」。而那个论证的可达性依据
（`StoreFlowRunner` / `GuardAsync` 在产物里）现在不成立。**

**→ `+342` 仍是真的（函数数确实涨了）。但「为什么涨」的解释建立在一条现在矛盾的读数上。
→ 而 R1004「Adyen/CommerceHub 的 `Id` 在产物里 19/17 次」那条也是同类读数 —— 同样需要重验。**

**这一轮不重验，因为重验需要一条**稳定的**读数方法，而那件事本身要先设计。**

### 五、数字

| 度量 | R1005 | R1006 |
|---|---|---|
| 套件 | 2214 | **2218（+4 缺货消息守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 174,336 | **174,336（未变）** |
| 函数比 | 62.91% | **62.91%** |
| **消息层进产物** | — | **否（3 个串全 absent）** |
| **R1002 的可达性读数** | 采信 | **撤回** |

### 六、验证

```
cd replica
python tools/snapshot.py
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug   -> 已成功生成
dotnet test --filter "FullyQualifiedName~ShortageMessageTests|FullyQualifiedName~CheckoutFailureModeTests" -m:1  -> 11 通过
dotnet publish … -o .publish-aot-new --nologo  -> exit 0
python - 在 .publish-aot 字节里搜 'reservation failed' / 'decoy' / 'lastBody' -> 全 absent
python - 搜 'StoreFlowRunner' / 'GuardAsync' -> absent（R1002 记的是 IN）
python tools/metrics_report.py -> 套件 2218 · 陈旧度 0/0 · 函数数 174,336
```

### 七、仍然 Unknown

- **产物读数为何前后矛盾**：**Unknown** —— 不同文件？裁剪巧合？未证。
- **消息层怎样才能进产物**：**Unknown** —— 未证。
- **R1004 的 `Id` 计数读数是否可靠**：**需重验**。

### 八、教训

**产物读数是一个**观测**，而观测要有稳定的对象和记录。
我拿三次不同 publish 的读数当一条时间线用，于是其中任何一次读错都会变成一个「事实」进入论证。**

**→ 而这一轮能发现它，是因为我**又查了一遍**同样几个串 —— 不是因为方法更好。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1006", BLOCKER)
    ensure(RSTATUS, "R1006", BLOCKER)
    ensure(RVERDICT, "第 1006 轮", VERDICT)
    ensure(BACKLOG, "R1006", BACKLOG_ADD)

    note = (
        "\n## R1006 补充 — **消息层实现正确（11 绿）但未进产物；`lastBody` 通道补上；R1002 可达性结论撤回**（套件 2218）\n\n"
        "`ClassifyCheckoutFailure` 加消息层：`reservation failed`→`Error`（可重试）· `decoy`→`Declined`（不重试）·\n"
        "两者同时出现**拒绝优先**；状态码层保持保守。**并补 `Vars[\"lastBody\"]`** —— `home` 是**首页**，\n"
        "缺货消息在 **checkout 响应**里（实现里的真错，本轮修掉）。**11 条测试绿。**\n\n"
        "**而 publish 后：`reservation failed` · `decoy` · `lastBody` 全 absent，函数数 174,336 未变。**\n\n"
        "**更重的是判别组把 R1002 否掉了**：`StoreFlowRunner` / `GuardAsync` 现在 **absent**，而 R1002 我记的是 **IN**。\n"
        "而函数数在 R1002 之后没变 ⇒ 不是裁剪变化 ⇒ **其中一次读数是错的**，而记录不足以判断是哪一次。\n"
        "→ **R1002「+342 因为可达」的解释撤回；R1004 的 `Id` 计数读数也需重验。**\n\n"
        "数字：套件 2218（+4）· 陈旧度 0/0 · 函数数 174,336（未变）· 消息层进产物 否 · R1002 可达性 撤回。\n\n"
        "纪律：**产物读数是观测 —— 观测要有稳定的对象和记录。**\n\n"
        "下一轮：先设计一条**稳定的**产物读数方法（同一文件 + 存快照 + 记录 sha256），再重验 R1002/R1004 两条结论。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1006" not in h:
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
             for p, k in ((RBLOCK, "R1006"), (RSTATUS, "R1006"), (RVERDICT, "第 1006 轮"), (BACKLOG, "R1006")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1006: the message layer is right and unreachable, and my own reachability readings disagree\n\n"
         "R1005 closed by saying the shortage disposition has to come from the body, since the artifact holds no\n"
         " status-code table. This round wrote that layer and it passes eleven tests.\n\n"
         "ClassifyCheckoutFailure now asks the body first and falls back to the code: reservation failed means another\n"
         " attempt is worth it, decoy means the shortage is bait and must not be retried, and when both markers appear\n"
         " the refusal wins, because a wrong retry costs an account while a wrongly abandoned attempt costs only that\n"
         " attempt. One real mistake surfaced while writing it -- the body channel I first reached for was Vars[\"home\"],\n"
         " which is the landing page, while a checkout shortage arrives on the checkout response -- so lastBody is now\n"
         " written beside each of the five places lastStatus is.\n\n"
         "Then the publish finished and none of it is in the binary. reservation failed, decoy and lastBody are all\n"
         " absent and the function count has not moved from 174,336.\n\n"
         "The comparison that matters is the control group. StoreFlowRunner and GuardAsync are absent now, and in R1002 I\n"
         " recorded both as present. The function count did not move between those rounds, so this is not a trimming\n"
         " change -- one of the two readings is simply wrong, and what I wrote down does not establish which.\n\n"
         "That retracts more than one line. The +342 from R1002 is real, since the count did move, but my explanation of\n"
         " it rested on those two strings being present, and R1004's count of adyen and commercehub by identifier is the\n"
         " same kind of reading and needs the same re-check.\n\n"
         "I am not re-checking this round, because re-checking needs a stable way to read the artifact first, and that is\n"
         " design work rather than another probe. What this round does establish is reproducible: the message layer is\n"
         " correct in source and in tests, and it is not in the artifact.\n\n"
         "Figures: suite 2214 to 2218, freshness zero, count unchanged at 174,336, message layer absent from the artifact,\n"
         " R1002's reachability reading withdrawn.\n\n"
         "Unknown: why the readings disagree, and what it would take for the message layer to reach the binary.\n\n"
         "The lesson is that an artifact reading is an observation, and an observation needs a stable subject and a\n"
         " record of it. I used readings from three different publishes as one timeline, so any single mistake became a\n"
         " fact that went on to carry an argument -- and the only reason it surfaced is that I looked at the same strings\n"
         " again.\n\n"
         "Two sources and one test file changed; suite green at 2218."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()