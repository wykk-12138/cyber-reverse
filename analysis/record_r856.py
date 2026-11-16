"""Record R856: the task layer is five Start*Flow plus three *Task; sweepstake and lottery are not in it."""

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
### 任务层是 5 个 `Start*Flow` + 3 个 `*Task`；sweepstake / lottery **不在**其中（R856）

**镜像原文：**

```
0x14337bdc4  <StartSignupFlow>d__57 · <StartClearFlow>d__58 · <StartInStoreFlow>d__59 · <StartPopNowFlow>d__60 · <St…
0x14337cdcc  <FetchTasks>d__187 · <StartDailyCheckInTask>d__188 · <StartPopNowViewTask>d__189
```

**编号连续（57–60、187–189），是分派层的入口，不是流程内部的步骤。**

**而 `SweepStake` / `Lottery` 出现在流程序列内部：**

```
0x1433712d6  <GetSweepStakeCheckout>d__40 · <GetSweepStakesShippingMethod>d__41 · <SubmitSweepStakesShipping>d__42 …
0x1434b3109  <FindProductMulti>d__32 · <FindProductFlow>d__33 · <FindVariant>d__35 · <GetLotteryForm>d__36 · <Submit…
```

**序号 40–42、32–36 —— 是某条流程内的步骤。**

### 所以 R855 那个 Inference 有答案

| R855 的猜测 | 结论 |
|---|---|
| sweepstake / lottery 是任务型 | **不是** —— 任务型是那 5 + 3 个 |
| 它们是某些站的结账变体 | **更像这个** —— 它们是流程序列内的步骤，序号在 32–43 段 |

**所以 R855 说的「三层」是对的，但 sweepstake / lottery 属于**流程层**，不是任务层。**
**三层应写成：任务型（5 + 3）· 流程（站／变体）· 风控。**
"""

if "任务层是 5 个 `Start*Flow` + 3 个 `*Task`" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: task layer appended")

BLOCKER = """

---

## 280. 任务层是 **5 个 `Start*Flow` + 3 个 `*Task`**；sweepstake / lottery 不在其中

> R856。未改产品代码。**R855 的 Inference 得到答案。**

### 一、镜像里的任务分派层

```
0x14337bdc4  <StartSignupFlow>d__57 · <StartClearFlow>d__58 · <StartInStoreFlow>d__59 · <StartPopNowFlow>d__60 · <St…
0x14337cdcc  <FetchTasks>d__187 · <StartDailyCheckInTask>d__188 · <StartPopNowViewTask>d__189
```

**五个 `Start*Flow`（57–60，第五个应是 `StartNormalFlow` 61）+ 三个 `*Task`（187–189）。
编号连续 → 是分派层的入口方法，不是某条流程内部的步骤。**

### 二、而 sweepstake / lottery 是流程内的步骤

```
0x1433712d6  <GetSweepStakeCheckout>d__40 · <GetSweepStakesShippingMethod>d__41 · <SubmitSweepStakesShipping>d__42
0x1434b3109  <FindProductMulti>d__32 · <FindProductFlow>d__33 · <FindVariant>d__35 · <GetLotteryForm>d__36 · <SubmitLottery>d__37
```

**注意这两段的序号：40–42 与 32–37 —— 落在**流程序列的编号段里**（R852 已证流程各自从低位编号）。**

**所以它们是某条流程里的步骤，不是分派层入口。**

### 三、R855 的三层要改一处

| R855 写的 | 现在 |
|---|---|
| 站 · 任务变体 · 风控 | **任务型（5 + 3）· 流程（站／变体）· 风控** |

**sweepstake / lottery 归**流程层**，不归任务层。**

**而这一条对复刻件更有利：复刻件没有 sweepstake / lottery，但那缺的是**某条流程里的两个步骤**，
不是缺两种任务型。工作量完全不同。**

### 四、复刻件这一层的名字对照

**复刻件有 `NikeSteps.cs` / `PopMartEndpoints.cs` / `StoreFlowSteps.cs`，但**没有** `Start*Flow` 这种分派层
—— 它用 `Registry.cs` 的 63 个模块 + `FlowStoreModule(new XxxFlow(...))` 表达「有哪条流程」。

**所以镜像的「五个 Start*Flow」对应复刻件的什么，没查。**
**这是一个新的、具体的 Unknown，而且它比「20+ 段属哪个站」更容易答 —— 五个名字都拿到了。**

### 五、验证

```
ida.py str SweepStake  -> 25 matches（含 0x1433712d6 的 d__40/41/42 段）
ida.py str Lottery     -> 24 matches（含 0x1434b3109 的 d__32/33/35/36 段）
ida.py str PopNow      -> 29 matches（含 0x14337bdc4 的 d__57–60 段、0x14337cdcc 的 d__187–189 段）
grep SweepStake/Lottery 全 replica\src -> 0
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **五个 `Start*Flow` 的第五个是不是 `StartNormalFlow`**：**Inference（高）** —— 字符串被截断在 `<St`。
- **这五个与 `Registry.cs` 的 63 个模块是什么关系**：**Unknown，但这是最好答的一个** —— 五个名字都在手上。
- **`FetchTasks` / `StartDailyCheckInTask` / `StartPopNowViewTask` 三个 `*Task` 在复刻件里有没有**：
  **`StartDailyCheckInTask` R842 已判为改名实现（`CheckIn`）；另两个未查。**

### 七、教训

**R855 我把 sweepstake / lottery 猜成「任务变体」，理由是名字里有 `Checkout` 和 `Raffle`。
这一轮一查编号就否了它 —— 40–42 落在流程段，不落在分派段。**

**「猜一个东西属于哪层」最省的办法不是读名字，是看它的 ordinal 落在哪个编号段。
而 ordinal 分段的规则是 R852 自己刚建立的 —— 我建了工具，没用在自己的猜测上。**
"""

VERDICT = """

---

## 第 856 轮：任务层是 5 个 `Start*Flow` + 3 个 `*Task`；sweepstake / lottery 不在其中

### 镜像里的任务分派层

```
0x14337bdc4  <StartSignupFlow>d__57 · <StartClearFlow>d__58 · <StartInStoreFlow>d__59 · <StartPopNowFlow>d__60 …
0x14337cdcc  <FetchTasks>d__187 · <StartDailyCheckInTask>d__188 · <StartPopNowViewTask>d__189
```

**编号连续（57–60、187–189）→ 分派层入口。**

### 而 sweepstake / lottery 是流程内的步骤

```
0x1433712d6  GetSweepStakeCheckout d__40 · GetSweepStakesShippingMethod d__41 · SubmitSweepStakesShipping d__42
0x1434b3109  FindProductMulti d__32 · GetLotteryForm d__36 · SubmitLottery d__37
```

**序号 40–42 / 32–37 落在流程段（R852 已证流程各自从低位编号）→ 它们不是分派层入口。**

### R855 的三层要改一处

| R855 | 现在 |
|---|---|
| 站 · 任务变体 · 风控 | **任务型（5+3）· 流程（站／变体）· 风控** |

**这对复刻件更有利：它没有 sweepstake / lottery，缺的是**某条流程里的两个步骤**，不是两种任务型。工作量完全不同。**

### 一个新的、更好答的 Unknown

**复刻件用 `Registry.cs` 63 个模块 + `FlowStoreModule(new XxxFlow(...))` 表达「有哪条流程」，没有 `Start*Flow` 分派层。**

> **镜像那五个 `Start*Flow` 对应复刻件的什么 —— 五个名字都在手上，比「20+ 段属哪个站」好答得多。**

### 仍然 Unknown

**第五个是不是 `StartNormalFlow`**（字符串截断在 `<St`，Inference 高）· **五个 ↔ 63 个模块的关系**（**最好答的一个**）·
**`FetchTasks` / `StartPopNowViewTask` 在复刻件里有没有**（`StartDailyCheckInTask` R842 已判为 `CheckIn`）

### 教训

> **「猜一个东西属于哪层」最省的办法不是读名字，是看它的 ordinal 落在哪个编号段。**
> **而 ordinal 分段的规则是 R852 自己刚建立的 —— 我建了工具，没用在自己的猜测上。**
"""

BACKLOG_ADD = """

## 判据 (f) — 任务层 = 5 个 `Start*Flow` + 3 个 `*Task`（R856）

```
0x14337bdc4  StartSignupFlow d__57 · StartClearFlow d__58 · StartInStoreFlow d__59 · StartPopNowFlow d__60 · StartNormalFlow? d__61
0x14337cdcc  FetchTasks d__187 · StartDailyCheckInTask d__188 · StartPopNowViewTask d__189
```

**编号连续 → 分派层入口。**

**而 sweepstake / lottery 是流程内步骤**（`GetSweepStakeCheckout` d__40–42 · `GetLotteryForm` d__36 / `SubmitLottery` d__37）。
**→ 序号落在流程段 → R855 猜的「任务变体」不成立；它们属**流程层**。**

### 三层修正

**任务型（5+3）· 流程（站／变体）· 风控**

**→ 复刻件缺 sweepstake/lottery 是「某条流程里两个步骤」，不是「两种任务型」。**

### 新的最好答的 Unknown

**镜像 5 个 `Start*Flow` ↔ 复刻件 `Registry.cs` 63 个模块 —— 五个名字都在手上。**

| 仍 Unknown | |
|---|---|
| 第五个是不是 `StartNormalFlow` | Inference 高（截断在 `<St`） |
| **5 个 Start*Flow ↔ 63 模块** | **最好答的一个** |
| `FetchTasks` / `StartPopNowViewTask` 有无 | `StartDailyCheckInTask` 已判为 `CheckIn`（R842） |

**纪律**：**「猜属于哪层」看 ordinal 落在哪个编号段，比读名字准 —— 而 ordinal 分段的规则是 R852 自己立的，我没用在自己的猜测上。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R856", BLOCKER)
    ensure(RSTATUS, "R856", BLOCKER)
    ensure(RVERDICT, "第 856 轮", VERDICT)
    ensure(BACKLOG, "R856", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R856" not in h:
        h += ("\n## R856 补充 — 任务层 = 5 个 Start*Flow + 3 个 *Task\n\n"
              "`0x14337bdc4`: `StartSignupFlow`57 · `StartClearFlow`58 · `StartInStoreFlow`59 · `StartPopNowFlow`60 · `StartNormalFlow?`61\n"
              "`0x14337cdcc`: `FetchTasks`187 · `StartDailyCheckInTask`188 · `StartPopNowViewTask`189\n"
              "**编号连续 → 分派层入口。而 sweepstake/lottery 是流程内步骤（d__40–42 / d__36–37）→ R855 的「任务变体」不成立，属流程层。**\n"
              "**最好答的下一个 Unknown：5 个 `Start*Flow` ↔ `Registry.cs` 63 个模块。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R856"), (RSTATUS, "R856"), (RVERDICT, "第 856 轮"), (BACKLOG, "R856")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R856: the task layer is five Start flows and three tasks, and sweepstake is not in it\n\n"
         "R855 guessed that sweepstake and lottery were task variants, on the strength of names containing Checkout and"
         " Raffle. Checking ordinals refutes it. The image's dispatch layer sits at 0x14337bdc4, where StartSignupFlow is"
         " d__57, StartClearFlow 58, StartInStoreFlow 59 and StartPopNowFlow 60 in consecutive order, and at 0x14337cdcc"
         " where FetchTasks is 187, StartDailyCheckInTask 188 and StartPopNowViewTask 189. Consecutive numbering at those"
         " positions means entry points of a dispatcher rather than steps inside a flow.\n\n"
         "Sweepstake and lottery sit differently. GetSweepStakeCheckout is d__40 with GetSweepStakesShippingMethod 41 and"
         " SubmitSweepStakesShipping 42; GetLotteryForm is d__36 with SubmitLottery 37, inside a run whose earlier steps"
         " are FindProductMulti 32 and FindProductFlow 33. Those ordinals fall inside flow-sequence ranges, which R852"
         " established are numbered independently per flow.\n\n"
         "So R855's three layers stand but with one member moved. It is task type, which is five Start flows plus three"
         " tasks, then flow, which is where sites and their variants live, then risk vendor. Sweepstake and lottery belong"
         " to flow, not to task type.\n\n"
         "That is better news for the replica than R855 implied. It lacks sweepstake and lottery, but what is missing is"
         " two steps inside some flow rather than two whole task types, and those are very different amounts of work.\n\n"
         "It also produces a sharper unknown. The replica expresses which flows exist through Registry's sixty-three"
         " modules and FlowStoreModule(new XxxFlow(...)), with no Start-flow dispatch layer. What those five image"
         " entry points correspond to in the replica is unestablished, but every one of the five names is now in hand,"
         " which makes it a much easier question than which site twenty-odd runs belong to.\n\n"
         "Unknown: whether the fifth Start flow is StartNormalFlow, since the string truncates after Start; how the five"
         " map onto Registry's sixty-three modules; and whether FetchTasks and StartPopNowViewTask exist in the replica,"
         " since R842 already found StartDailyCheckInTask implemented under the name CheckIn.\n\n"
         "The lesson is small and annoying. The cheapest way to tell which layer something belongs to is not to read its"
         " name but to see which ordinal range it falls in -- and the ordinal-range rule is one I had established myself"
         " in R852 and then failed to apply to my own guess two rounds later.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
