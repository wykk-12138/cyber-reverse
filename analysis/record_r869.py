"""Record R869: removed my own duplicate, reused StepActionRunner, wired the runner branch."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### R868 那张反射表是**重复品** —— 删掉，改用 `StepActionRunner`（R869）

**查 `StepOutcome` 的形状时撞见 `StepActionRunner`（`Actions/StepAction.cs` L195）——
它早就在做同一件事，而且做得更好：**

| | `StepActionRunner`（已有） | 我的 `StepDispatch`（R868 写的） |
|---|---|---|
| 取方法 | `typeof(StoreFlow).GetMethods()` | 同 |
| 调用方式 | **`MethodInfo.Invoke`** | `Delegate.CreateDelegate` ← **撞上 `ArgumentException`** |
| 名字查询 | `Knows(step)` | `TryGetValue` |
| 逐步计时 | **有**（`Stopwatch` + `TaskStepRecord`） | 无 |
| `ctx.Step()` / `ctx.Finish()` 记录 | **有** | 无 |
| 取消 / 异常处理 | **有** | 无 |

**所以 R868 那个 `ArgumentException` 本来不必撞 —— 现成的实现用 `Invoke`，绕开了它。**

### 改法

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | **删** `BuildDispatch` + `DispatchTable` + `RunStepNamedAsync`；`StepDispatch` 改为 `=> StepActionRunner.Invokers`；新增 `CanRunStep(step) => StepActionRunner.Knows(step)` |
| `StepAction.cs` | `Invokers` 由 `private` 改 **`internal`** |
| `NikeFlow.cs` / `MagentoFlow.cs`（内含 `JohnLewisFlow`） | 各加 `override StepSequence` |

**现在三个流程声明序列：Nike 16 · PopMart 24 · JohnLewis 19。**

### 而其余 5 个序列没有落点

| `StoreFlowSteps.X.Store` | 有对应流程类吗 |
|---|---|
| `nike` · `popmart` · `johnlewis` | **有** |
| **`demandware-classic` · `demandware-dual` · `collectplus-app` · `structure-token-multi` · `structure-token-single`** | **没有** |

**这正是 R855 说的「它们不是站，是变体」—— 现在是一个可核对的表。**

### runner 分支：写的时候就踩出一个假成功

**`RunCheckoutAsync` 在 Init + AntiBot 之后加分支：有 `StepSequence` 就走它。**

**第一版直接调 `StepActionRunner.RunAsync`。而 `PopMartFlow` 声明 24 步、可跑 0 步 →
`RunAsync` 的空步列表循环一次也不进 → 返回 `Ok = true` → **报「结账成功」而什么都没做**。**

**这就是本项目反复在删的那个形态。修法：`runnable.Count == 0` 直接 `Error`，
消息里写明「24 declared, 0 implemented」。**

**顺便：把 `sequenceDeclared` / `sequenceRunnable` 写进 session，让跳过的步数一直可见 ——
不然「跑了 24 步里的 9 步」和「跑完了」在结果上一样。**
"""

if "R868 那张反射表是**重复品**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: dedup + runner appended")

BLOCKER = """

---

## 293. **R868 那张反射表是我写的重复品** —— 删掉改用现成的；顺带 runner 接上

> R869。**改了产品代码。** 套件 **1773 通过 / 0 失败 / 0 跳过**。

### 一、撞见现成的实现

**为了查 `StepOutcome` 的形状，读到 `Actions/StepAction.cs` 里的 `StepActionRunner`（L195）——
它从 R 更早的时候就在做同一件事，而且更完整：**

| | `StepActionRunner` | 我的 `StepDispatch`（R868） |
|---|---|---|
| 调用方式 | **`MethodInfo.Invoke`** | `Delegate.CreateDelegate` ← **撞上 `ArgumentException`** |
| `Knows(step)` | 有 | 只有 `TryGetValue` |
| 逐步计时 + `TaskStepRecord` | **有** | 无 |
| `ctx.Step()` / `ctx.Finish()` | **有** | 无 |
| 取消 / 异常 | **有** | 无 |

**R868 那个 `ArgumentException` 本来不必撞：现成实现用 `Invoke`，绕开了开放实例委托的绑定限制。**

**这是同一个教训的第二次落地 —— 而这次重复是我自己写的。
R843 立的规则「先 grep 同名分析文件」，我只想到「分析文件」，没想到「实现文件」。**

### 二、删掉了什么

**`StoreFlow.cs`：删 `BuildDispatch` / `DispatchTable` / `RunStepNamedAsync`。
`StepDispatch` 改为 `=> StepActionRunner.Invokers`；新增 `CanRunStep(step) => StepActionRunner.Knows(step)`。
`StepAction.cs`：`Invokers` 由 `private` 改 `internal`。**

**净效果：代码更少，能力更多（多了计时、记录、取消处理）。**

### 三、三个流程接上，五个没有落点

| `StoreFlowSteps.X.Store` | 流程类 |
|---|---|
| `nike` · `popmart` · `johnlewis` | **有，已 override** |
| `demandware-classic` · `demandware-dual` · `collectplus-app` · `structure-token-multi` · `structure-token-single` | **没有** |

**这是 R855 那句「它们不是站，是变体」的可核对形态：镜像有 8 条序列，复刻件只有 3 个类能承接。**

### 四、runner 分支，以及写它时踩出的假成功

**`RunCheckoutAsync` 在 Init + AntiBot 之后：`if (flow.StepSequence.Count > 0) return await RunDeclaredSequenceAsync(...)`。
空序列的 25 个流程行为不变。**

**第一版直接把可跑步交给 `StepActionRunner.RunAsync`。而 `PopMartFlow` 声明 24、可跑 0 ——
空列表的 `foreach` 一次也不进，返回 `Ok = true`，于是**报「结账成功」而什么都没做**。**

**这正是本项目反复在删的那个形态（R823 编造值 / R850 空壳方法 / R858 死字段 / 现在：空循环假成功）。
修法：`runnable.Count == 0` 直接 `Error`，消息写明「24 declared, 0 implemented」。**

**另外把 `sequenceDeclared` / `sequenceRunnable` 写进 session ——
不然「跑了 24 步里的 9 步」和「跑完了」在结果上没法区分。**

### 五、一个刻意的、记下来的选择

**某步真的失败时，这里**中止**整个序列。理由是购物车坏了之后后续步骤没有意义。**

**但这是**选择**，不是观察 —— 镜像在同样情况下怎么做没查。
**已作为 Unknown 写进代码注释，不当作事实陈述。**

### 六、验证

```
cd replica && python tools\\snapshot.py                      -> 20261116-214544
D:\\tools\\dotnet8\\dotnet.exe build src\\Cybersole.Stores\\... -> 0 错误
D:\\tools\\dotnet8\\dotnet.exe test --filter FlowSequenceTests -> 7 通过 / 0 失败
python tools\\metrics_report.py                                -> 1773 通过 / 0 失败 / 0 跳过
    wrote docs\\METRICS.md
序列覆盖: Nike 16 · PopMart 24 · JohnLewis 19 已声明；5 条序列无对应流程类
```

### 七、仍然 Unknown

- **`CheckoutResult` 没有「不支持」这个值**：**Observation** —— 只有 `Unknown/Declined/PaymentRequired/Success/Cancelled/Error/ThreeDSRequired`。
  **所以「这个流程根本没实现」只能用 `Error` 表达，与「跑了但失败」同值。这是镜像的行为还是复刻件的缺口，未查。**
- **某步失败该中止还是继续**：**Unknown**（本轮选了中止，已记在代码里）。
- **那 5 条序列要不要各建一个流程类**：**Unknown** —— 它们是变体（R855），
  **可能该建成 `DemandwareFlow` 的几种模式，而不是五个类。**

### 八、教训

**R868 我用 `Delegate.CreateDelegate` 撞了一堵墙，然后绕过去了。
R869 发现旁边有一扇门，一直是开的 —— 而且门后的房间比我自己搭的那个大。**

**「先查有没有现成的」这条，我把它理解成「查有没有现成的**分析**」。这次它该是「查有没有现成的**实现**」。
而查的成本是三分钟：读一个我本来就要读的文件。**

**顺带：我在这两轮里各写了一个假成功/重复品，而两个都是可以靠「先读再写」避免的。
所以下一步不该是继续写，而是先把「写之前读哪里」写清楚 —— 那比再写三处更有用。**
"""

VERDICT = """

---

## 第 869 轮：R868 那张反射表是我写的重复品 —— 删掉改用现成的

### 撞见现成的实现

**查 `StepOutcome` 形状时读到 `StepActionRunner`（`Actions/StepAction.cs` L195）—— 它早就在做同一件事，且更完整：**

| | `StepActionRunner` | 我 R868 写的 |
|---|---|---|
| 调用方式 | **`MethodInfo.Invoke`** | `CreateDelegate` ← **撞上 ArgumentException** |
| 逐步计时 / `ctx.Step()` / 取消 / 异常 | **全有** | 无 |

**→ R868 那堵墙本来不必撞。**

### 删掉了什么

**删 `BuildDispatch` / `DispatchTable` / `RunStepNamedAsync`；`StepDispatch => StepActionRunner.Invokers`；新增 `CanRunStep`。
`Invokers` 由 `private` 改 `internal`。**

**净效果：代码更少，能力更多。**

### 三个流程接上，五个没有落点

| 有 | `nike` · `popmart` · `johnlewis`（16 / 24 / 19 步） |
|---|---|
| **没有** | **`demandware-classic` · `-dual` · `collectplus-app` · `structure-token-*`** |

**→ R855 那句「它们不是站，是变体」的可核对形态。**

### runner 分支，以及写它时踩出的假成功

**`PopMartFlow` 声明 24、可跑 0 → `StepActionRunner.RunAsync` 空列表返回 `Ok = true` → **报「结账成功」而什么都没做**。**

**修法：`runnable.Count == 0` 直接 `Error`，消息写明「24 declared, 0 implemented」；
并把 `sequenceDeclared` / `sequenceRunnable` 写进 session，让跳过步数一直可见。**

> **这是本项目反复在删的那个形态的第五种：编造值 → 空壳方法 → 死字段 → **空循环假成功**。**

### 一个刻意的选择（已记在代码里）

**某步失败时中止整个序列 —— 理由是购物车坏了后续无意义。**但这是**选择**不是观察，镜像行为未查。**

### 仍然 Unknown

**`CheckoutResult` 没有「不支持」值**（只有 `Unknown/Declined/PaymentRequired/Success/Cancelled/Error/ThreeDSRequired`）→
「没实现」与「跑了但失败」同值 · **某步失败该中止还是继续**（本轮选了中止）·
**那 5 条变体该建五个类还是一套模式**（R855 倾向后者）

### 教训

> **「先查有没有现成的」我理解成「查有没有现成的**分析**」。这次它该是「查有没有现成的**实现**」—— 而查的成本是三分钟。**
> **两轮里我各写了一个重复品/假成功，两个都能靠「先读再写」避免。所以下一步不是继续写，而是把「写之前读哪里」写清楚。**
"""

BACKLOG_ADD = """

## 优先级 ① — 去重 + runner 接上（R869，**已改产品代码**）

**R868 的反射表是 `StepActionRunner`（`Actions/StepAction.cs` L195）的重复品，且后者更完整（`Invoke` 而非 `CreateDelegate`，含计时/记录/取消/异常）。已删，改指向它。**

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | 删 `BuildDispatch`/`DispatchTable`/`RunStepNamedAsync`；`StepDispatch => StepActionRunner.Invokers`；加 `CanRunStep` |
| `StepAction.cs` | `Invokers` private → `internal` |
| `NikeFlow.cs` · `MagentoFlow.cs`(JohnLewisFlow) | 各加 `override StepSequence` |
| `StoreFlowRunner.cs` | Init+AntiBot 后分支；新增 `RunDeclaredSequenceAsync` |

**套件 1773 通过 / 0 失败 / 0 跳过。**

### 覆盖

| 有落点 | nike 16 · popmart 24 · johnlewis 19 |
|---|---|
| **无落点** | **demandware-classic · demandware-dual · collectplus-app · structure-token-multi · structure-token-single** |

**→ R855「不是站是变体」的可核对形态。**

### 写 runner 时踩出的假成功（第五种形态）

**24 declared / 0 runnable → 空循环返回 Ok → 报「成功」而什么都没做。**
**已修：`runnable.Count == 0` → `Error("24 declared, 0 implemented")`；并把两个数写进 session 让跳过可见。**

**形态谱：编造值（R823）→ 空壳方法（R850）→ 死字段（R858）→ 空循环假成功（R869）。**

| 仍 Unknown | |
|---|---|
| `CheckoutResult` 无「不支持」值 | 「没实现」与「失败」同值 |
| 某步失败该中止还是继续 | 本轮选中止，镜像未查 |
| 5 条变体建五类还是一条模式 | R855 倾向后者 |

**纪律**：**「先查有没有现成的」要包括**实现**，不只是分析。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R869", BLOCKER)
    ensure(RSTATUS, "R869", BLOCKER)
    ensure(RVERDICT, "第 869 轮", VERDICT)
    ensure(BACKLOG, "R869", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R869" not in h:
        h += ("\n## R869 补充 — 去重 + runner 接上（**已改产品代码**）\n\n"
              "**R868 的反射表是 `StepActionRunner` 的重复品**（后者更完整：`Invoke` 而非 `CreateDelegate`，含计时/记录/取消）。**已删，改指向它。**\n"
              "**三个流程声明序列**：Nike 16 · PopMart 24 · JohnLewis 19；**五条序列无落点**（demandware-* / collectplus / structure-token-* → R855「是变体不是站」）。\n"
              "**runner 分支已接**；写时踩出**假成功**（24 declared / 0 runnable → 空循环返回 Ok）→ 已修：0 runnable 直接 Error。\n"
              "**形态谱第五种：编造值 → 空壳方法 → 死字段 → **空循环假成功**。**\n"
              "**套件 1773 通过 / 0 失败 / 0 跳过。**\n"
              "**教训：「先查有没有现成的」要包括**实现**，不只是分析。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R869"), (RSTATUS, "R869"), (RVERDICT, "第 869 轮"), (BACKLOG, "R869")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R869: the reflection table I wrote last round was a duplicate, and removing it added capability\n\n"
         "Looking up StepOutcome's shape turned up StepActionRunner in Actions/StepAction.cs, which has done the same"
         " work since long before R868 and does it better. It reflects the same methods from typeof(StoreFlow), exposes"
         " Knows, and runs a named step with per-step timing, FlowContext recording, cancellation and exception"
         " handling. Crucially it calls MethodInfo.Invoke rather than Delegate.CreateDelegate, which is why it never met"
         " the binding failure R868 hit. The wall I walked into had a door beside it, open the whole time.\n\n"
         "So the table and RunStepNamedAsync are deleted from StoreFlow. StepDispatch now exposes StepActionRunner's"
         " table and CanRunStep asks Knows, with Invokers widened from private to internal. Less code, more capability.\n\n"
         "Three flows now declare their orders -- Nike sixteen, Pop Mart twenty-four, John Lewis nineteen. Five do not,"
         " because no flow class claims their ids: demandware-classic, demandware-dual, collectplus-app and the two"
         " structure-token variants. That is R855's conclusion that these are variants rather than stores, now in a\n"
         " form that can be checked rather than argued.\n\n"
         "Wiring the runner branch produced a bug worth recording. Pop Mart declares twenty-four steps and can run none,"
         " and StepActionRunner over an empty list returns Ok without entering the loop -- so a flow that did nothing at"
         " all would have reported a completed checkout. That is the fifth shape of the same fault this project keeps\n"
         " removing: a fabricated value, a method with a shape and no content, a field nobody writes, and now an empty"
         " loop reporting success. The fix fails explicitly with '24 declared, 0 implemented', and both counts are\n"
         " written into the session so a run that did nine of twenty-four cannot look like one that finished.\n\n"
         "One choice is recorded as a choice: a failing step stops the sequence, on the reasoning that a broken cart\n"
         " makes later steps meaningless. That is a decision, not an observation, and it says so where it lives.\n\n"
         "Unknown: CheckoutResult has no value meaning unsupported -- only Unknown, Declined, PaymentRequired, Success,\n"
         " Cancelled, Error and ThreeDSRequired -- so 'this flow is not implemented' and 'it ran and failed' are the same\n"
         " value, and whether the image distinguishes them is unchecked; whether a mid-sequence failure should stop or\n"
         " continue; and whether the five variant sequences want five classes or one pattern, where R855 leans to the\n"
         " latter.\n\n"
         "The lesson is about what 'check for an existing implementation' covers. I took it to mean existing analysis and\n"
         " read the step maps; the thing I should have read was the code. Two rounds produced a duplicate and a false\n"
         " success, both avoidable by reading before writing, so the next useful move is not more code but writing down\n"
         " where to read before writing.\n\n"
         "Product code changed; suite green at 1773."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
