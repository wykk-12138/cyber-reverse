"""Record R879: fourteen task kinds, and the unnamed sequence attributed by meaning."""

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
### 任务种类是 **14**，不是 5 —— 而它顺带给了那条无名序列一个**语义**归属（R879）

**基线文件 `replica/docs/baseline/recovered_async_methods.txt` 有 1547 个异步方法名。
从里面按后缀捞：**

```
Start*Flow  共 14 个
  StartAccountRegistrationFlow   StartClearFlow        StartDrawCheckFlow
  StartDrawEventFlow             StartDrawFlow         StartExhibitFlow
  StartInStoreFlow               StartNormalFlow       StartPopNowFlow
  StartRaffleFlow                StartReservationFlow  StartRpcFlow
  StartSignupFlow                StartTasksFlow

Start*Task  共 2 个
  StartDailyCheckInTask          StartPopNowViewTask
```

**R857 当时在 `0x14337bdc4` 一个代码区里看到 5 个（`StartSignupFlow` / `StartClearFlow` / `StartInStoreFlow` /
`StartPopNowFlow` / `StartNormalFlow`），据此说「顶层是任务种类 × 站」。**

**现在看：那 5 个是 14 个里的 5 个。**「任务种类 × 站」的判断是对的，而种类的数量错了三倍。**

### 顺带：那条无名序列（R878 撤回了 `DrawStores` 命名）有了语义归属

**它的 12 步：**

```
21 Start · 23 GetHome · 24 CheckVerification · 25 SubmitSaleRegistration
26 CheckLogin · 27 Register · 28 CompleteRegistration
30 GetCart · 31 ClearCart · 32 FindProduct · 33 AddToCart · 34 ReplaceProduct
```

**而 14 个任务种类里有一个叫 `StartAccountRegistrationFlow`。**

**`CheckVerification` / `SubmitSaleRegistration` / `Register` / `CompleteRegistration` ——
这四步与「账号注册流程」这个名字是**语义**对上的。**

**所以那条序列很可能是 `AccountRegistrationFlow` 的，而不是 `DrawStores` 的。**

**这是 Inference，而它与 R876 那次错的 Inference 有一个关键区别：**

| | R876（错） | R879（这条） |
|---|---|---|
| 依据 | **位置相邻** | **步骤名与流程名语义一致** |
| 可反驳点 | **字节间隔 22 > 11，直接推翻** | **没有直接推翻的证据** |
| 强度 | **零** | **弱，但非零** |

**R878 的教训是「能用算术回答就不该靠推断」。这一条不能用算术回答 ——
所以它停在 Inference，标注清楚，不写进 `StoreFlowSteps`。**

### `Start` ≠ `Init`

**R877 说「`Start` 与 `Init` 是否同一件事，这是 8/12 与 9/12 之间那一步」。**

**基线里 `Start` 和 `Init` **两个名字都存在**（`Start` 一条、`Init` 一条）。
所以它们不是同一件事的两种叫法，`Start` 是镜像里一个真实存在而复刻件没有的方法。**

**→ 8/12 就是 8/12，不是 9/12。**
"""

if "任务种类是 **14**，不是 5" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R879 appended")

BLOCKER = """

---

## 303. 任务种类 14 个（R857 说 5 个）；无名序列按**语义**归属；`Start` ≠ `Init`

> R879。未改产品代码。

### 一、14 个任务种类

**`replica/docs/baseline/recovered_async_methods.txt`（1547 个异步方法名）按后缀捞：**

```
Start*Flow (14)
  StartAccountRegistrationFlow  StartClearFlow        StartDrawCheckFlow
  StartDrawEventFlow            StartDrawFlow         StartExhibitFlow
  StartInStoreFlow              StartNormalFlow       StartPopNowFlow
  StartRaffleFlow               StartReservationFlow  StartRpcFlow
  StartSignupFlow               StartTasksFlow

Start*Task (2)
  StartDailyCheckInTask         StartPopNowViewTask
```

**R857 在 `0x14337bdc4` 一个代码区看到 5 个，据此说「顶层是任务种类 × 站」。
那 5 个是这 14 个里的 5 个 —— 判断对，数量错三倍。**

**这正是 §2.7b 那条「先问来源是全量还是抽样」：**
**R857 的来源是**一个代码区**，而基线是**全量方法名清单**。**

### 二、那条无名序列按语义归属

**序列（21–34）：`Start` · `GetHome` · `CheckVerification` · `SubmitSaleRegistration` ·
`CheckLogin` · `Register` · `CompleteRegistration` · `GetCart` · `ClearCart` · `FindProduct` ·
`AddToCart` · `ReplaceProduct`**

**14 个任务种类里有 `StartAccountRegistrationFlow`。四个步骤（`CheckVerification` /
`SubmitSaleRegistration` / `Register` / `CompleteRegistration`）与「账号注册」语义对上。**

**所以它很可能是 `AccountRegistrationFlow` 的。**

**这是 Inference，而与 R876 那个错的 Inference 的区别值得写下来：**

| | R876（错） | R879 |
|---|---|---|
| 依据 | 位置相邻 | **步骤名与流程名语义一致** |
| 能否被直接推翻 | **能：22 > 11** | 目前不能 |
| 强度 | 零 | **弱，但非零** |

**R878 说「能用算术回答就不该靠推断」。这条不能用算术回答 ——
所以它停在 Inference，**不写进 `StoreFlowSteps`**，因为那里放的是 Observation。**

### 三、`Start` ≠ `Init`，所以 8/12 不是 9/12

**基线里 `Start` 与 `Init` 两个名字都存在。它们不是同一件事的两种叫法。**

**`Start` 是镜像里真实存在、而 `StoreFlow` 没有的方法。**
**→ R877 说「这是 8/12 与 9/12 之间那一步」—— 那一步不存在，8/12 就是 8/12。**

### 四、这条对优先级 ① 的意义

**R857 的「任务种类 × 站」是复刻件 `Registry.cs` 与 `Flows/` 的理论骨架。**

**骨架若按 5 种任务建，就少了 9 种。**
**而复刻件目前的 `StepSequence` 只有 3 条（Nike / PopMart / JohnLewis），连 5 都没到。**

**所以：不是「差几条序列」，是「**任务种类这一层在复刻件里几乎没有对应物**」。**

### 五、验证

```
recovered_async_methods.txt -> 1547 pairs
Start*Flow  -> 14（列出全部）
Start*Task  ->  2（列出全部）
Start / Init 均在基线中 -> 两个不同方法
where_is Alias -> Profiles.cs 无 Alias 字段；访问器基线有 Aliases / AllowAlias / HasAllowAlias，无裸 Alias
```

### 六、仍然 Unknown

- **那 14 种任务在复刻件里对应什么**：**Unknown —— 这是优先级 ① 最大的结构缺口，本轮只把数量说准。**
  **`Registry.cs` 有 64 个模块，但模块是「站」，不是「任务种类」。**
- **无名序列是否真属 `AccountRegistrationFlow`**：**Inference（语义），未证。**
- **`Start` 这一步做什么**：**Unknown** —— 名字只说明它存在。

### 七、教训

**R857 从一个代码区数出 5，我从全量基线数出 14。**

**两次都是诚实的观察，而差别只在来源。§2.7b 那条规则我读过四次，这次是它第一次在**我自己前几轮的结论**上生效。**

**所以「先问来源是全量还是抽样」不只适用于新扫描 ——
它也适用于复核自己已经写下的数字。**

**而更值得记的是：R857 那个结论**看起来**是对的（「任务种类 × 站」这个骨架没错），
错的只是数量。一个方向正确的结论会让人不去复核它的数。**
"""

VERDICT = """

---

## 第 879 轮：任务种类 14 个（不是 5）；无名序列按语义归属；`Start` ≠ `Init`

### 14 个任务种类

**基线 `recovered_async_methods.txt`（1547 个异步方法名）按后缀捞：**

```
Start*Flow (14): StartAccountRegistrationFlow StartClearFlow StartDrawCheckFlow
  StartDrawEventFlow StartDrawFlow StartExhibitFlow StartInStoreFlow StartNormalFlow
  StartPopNowFlow StartRaffleFlow StartReservationFlow StartRpcFlow StartSignupFlow StartTasksFlow
Start*Task (2): StartDailyCheckInTask StartPopNowViewTask
```

**R857 在一个代码区看到 5 个 —— 判断（「顶层是任务种类 × 站」）对，数量错三倍。**

> **这是 §2.7b「先问来源是全量还是抽样」第一次在**我自己前几轮的结论**上生效。**

### 无名序列按语义归属

**序列里的 `CheckVerification` / `SubmitSaleRegistration` / `Register` / `CompleteRegistration`
与 `StartAccountRegistrationFlow` 这个名字**语义**对上 → 很可能是它的。**

| | R876（错） | R879 |
|---|---|---|
| 依据 | 位置相邻 | **步骤名 vs 流程名语义** |
| 能否被直接推翻 | **能：22 > 11** | 目前不能 |
| 强度 | 零 | **弱，但非零** |

**R878 说「能用算术回答就不该靠推断」；这条不能用算术回答 —— 所以它停在 Inference，**不写进 `StoreFlowSteps`**。**

### `Start` ≠ `Init`

**基线里两个名字都存在 → 不是同一件事 → R877「8/12 与 9/12 之间那一步」不存在，8/12 就是 8/12。**

### 对优先级 ① 的意义

**「任务种类 × 站」这个骨架若按 5 种建就少 9 种；而复刻件的 `StepSequence` 只有 3 条（Nike/PopMart/JohnLewis），连 5 都没到。**

> **所以不是「差几条序列」，是「**任务种类这一层在复刻件里几乎没有对应物**」。**
> **`Registry.cs` 的 64 个模块是「站」，不是「任务种类」。**

### 仍然 Unknown

**14 种任务在复刻件里对应什么**（**优先级 ① 最大的结构缺口，本轮只把数量说准**）·
**无名序列是否真属 `AccountRegistrationFlow`**（Inference）· **`Start` 做什么**

### 教训

> **R857 那个结论**看起来**是对的，错的只是数量 —— 一个方向正确的结论会让人不去复核它的数。**
"""

BACKLOG_ADD = """

## 优先级 ① — 任务种类 **14**（R857 说 5）；无名序列按语义归属（R879）

### 14 个 `Start*Flow` + 2 个 `Start*Task`

```
StartAccountRegistrationFlow StartClearFlow StartDrawCheckFlow StartDrawEventFlow
StartDrawFlow StartExhibitFlow StartInStoreFlow StartNormalFlow StartPopNowFlow
StartRaffleFlow StartReservationFlow StartRpcFlow StartSignupFlow StartTasksFlow
(+ StartDailyCheckInTask StartPopNowViewTask)
```

**来源：`replica/docs/baseline/recovered_async_methods.txt`（1547 个异步方法名，全量）。**
**R857 的来源是**一个代码区**（5 个）→ §2.7b「先问来源是全量还是抽样」第一次用在复核自己的旧结论上。**

### 无名序列（21–34）按语义归属

**`CheckVerification`/`SubmitSaleRegistration`/`Register`/`CompleteRegistration`
↔ `StartAccountRegistrationFlow` → **Inference（语义），非 Observation，不写进 `StoreFlowSteps`。****

| | R876（错） | R879 |
|---|---|---|
| 依据 | 位置相邻 | 步骤名 vs 流程名语义 |
| 可推翻 | **能（22>11）** | 目前不能 |
| 强度 | 零 | 弱但非零 |

### `Start` ≠ `Init`

**基线里两名都在 → R877 的「8/12→9/12」那一步不存在，8/12 就是 8/12。**

### 结构缺口

**「任务种类 × 站」骨架按 5 种建会少 9 种；而复刻件 `StepSequence` 只有 3 条（Nike/PopMart/JohnLewis）。**
**→ 不是「差几条序列」，是**任务种类这一层几乎没有对应物**（`Registry.cs` 64 个模块是「站」不是「任务种类」）。**

| 仍 Unknown | |
|---|---|
| **14 种任务在复刻件里对应什么** | **优先级 ① 最大结构缺口** |
| 无名序列是否真属 `AccountRegistrationFlow` | Inference |
| `Start` 做什么 | 未查 |

**纪律**：**方向正确的结论最容易免于复核 —— 复核时先问它的来源是全量还是抽样。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R879", BLOCKER)
    ensure(RSTATUS, "R879", BLOCKER)
    ensure(RVERDICT, "第 879 轮", VERDICT)
    ensure(BACKLOG, "R879", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R879" not in h:
        h += ("\n## R879 补充 — 任务种类 **14** 个（不是 5）\n\n"
              "**来源 `replica/docs/baseline/recovered_async_methods.txt`（1547 个异步方法名，全量）**："
              "`Start*Flow` 14 个 + `Start*Task` 2 个。**R857 的来源是一个代码区（5 个）→ 判断对，数量错三倍。**\n"
              "**14 个**：`AccountRegistration` `Clear` `DrawCheck` `DrawEvent` `Draw` `Exhibit` `InStore` `Normal` `PopNow` `Raffle` `Reservation` `Rpc` `Signup` `Tasks`。\n"
              "**无名序列（21–34）按语义归属 `StartAccountRegistrationFlow`**（`CheckVerification`/`SubmitSaleRegistration`/`Register`/`CompleteRegistration` 对上）—— **Inference，不写进 `StoreFlowSteps`。**\n"
              "**`Start` ≠ `Init`**（基线里两名都在）→ R877 的 9/12 不存在，**8/12 就是 8/12**。\n"
              "**结构缺口**：任务种类这一层在复刻件里几乎没有对应物（`Registry.cs` 64 个模块是「站」不是「任务种类」）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R879"), (RSTATUS, "R879"), (RVERDICT, "第 879 轮"), (BACKLOG, "R879")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R879: fourteen task kinds, not five, and the unnamed sequence attributed by meaning\n\n"
         "The baseline of 1547 recovered async method names settles two things R877 left open and corrects one of my\n"
         " own earlier numbers.\n\n"
         "There are fourteen Start-prefixed flow entries, and two task entries: AccountRegistration, Clear, DrawCheck,\n"
         " DrawEvent, Draw, Exhibit, InStore, Normal, PopNow, Raffle, Reservation, Rpc, Signup and Tasks, plus\n"
         " StartDailyCheckInTask and StartPopNowViewTask. R857 counted five of these from a single code region and\n"
         " concluded the top layer is task kind by store. The conclusion was right and the count was out by a factor of\n"
         " three. That is section 2.7b -- ask whether a source is complete or a sample -- applying to my own earlier\n"
         " conclusion for the first time rather than to a fresh scan.\n\n"
         "The unnamed sequence from R876 and R878 is plausibly the account registration flow. Its steps include\n"
         " CheckVerification, SubmitSaleRegistration, Register and CompleteRegistration, which match the name of\n"
         " StartAccountRegistrationFlow by meaning rather than by position. That is still inference, and the difference\n"
         " from R876's mistake is worth recording: R876 rested on adjacency and was refuted by arithmetic, since\n"
         " twenty-two bytes cannot fit in eleven, while this rests on the steps naming the thing the flow is called and\n"
         " nothing currently refutes it. Inference of the second kind stays out of StoreFlowSteps, where only\n"
         " observations belong.\n\n"
         "Start and Init are separate methods, both present in the baseline, so R877's step between eight of twelve and\n"
         " nine does not exist. Eight of twelve is the count.\n\n"
         "For priority one this is the largest structural gap named so far. If the replica organises by five task kinds\n"
         " it is missing nine; and in fact StepSequence exists on three flows only, Nike, Pop Mart and John Lewis. So\n"
         " the gap is not a few missing sequences but a missing layer: Registry's sixty-four modules are stores, not\n"
         " task kinds, and nothing in the replica corresponds to the task-kind axis at all.\n\n"
         "Unknown: what the fourteen task kinds correspond to in the replica, which this round only counts rather than\n"
         " maps; whether the unnamed sequence really belongs to AccountRegistrationFlow; and what Start does, since the\n"
         " name proves existence and nothing more.\n\n"
         "The lesson is that a conclusion pointing the right direction escapes re-checking. R857's骨架 was correct,\n"
         " and that correctness is exactly why the number beside it went unexamined for twenty-two rounds.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
