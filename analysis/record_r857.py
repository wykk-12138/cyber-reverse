"""Record R857: the image's top layer is task kind x store; the replica's is store only."""

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
### 镜像 = **任务种类 × 店**；复刻件 = **只有店**（R857）

**镜像顶层，五个入口（`0x14337bdc4`，d__57–60 + 第五个）：**

```
StartSignupFlow · StartClearFlow · StartInStoreFlow · StartPopNowFlow · StartNormalFlow
```

**这不是五个站，是五种**任务种类**：注册 · 清仓 · 到店 · PopNow 抽签 · 常规结账。**

**复刻件的顶层（`Modules/Registry.cs`，312 行）：**

```
64 个 FlowStoreModule · 33 个流程类 · 33 个 shop id
enter · offspring · bodega · concepts · packershoes · socialstatus · undefeated …
```

**`Registry.cs` 里没有「任务种类」这一层 —— 顶层直接是店。**

### 所以

| | 镜像 | 复刻件 |
|---|---|---|
| 顶层 | **任务种类（5 种）** | **店（64 个模块）** |
| 第二层 | 站／变体的流程序列 | 33 个流程类 |
| 第三层 | 风控 | 风控（Kasada / Cloudflare） |

**这解释了为什么「20+ 段运行」认不出归属 —— 它们里有的是**种类**下的通用序列，不对应任何站。**
**`StartPopNowFlow` 对应 Pop Mart 的抽签；`StartInStoreFlow` 对应到店；`StartSignupFlow` 对应注册。
它们是**跨站的**，所以按站去找必然错位。**
"""

if "镜像 = **任务种类 × 店**；复刻件 = **只有店**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: top-layer finding appended")

BLOCKER = """

---

## 281. 镜像顶层是**任务种类**，复刻件顶层是**店**

> R857。未改产品代码。**这解释了 R854/R855 为什么认不出那 20+ 段的归属。**

### 一、镜像的五个入口不是五个站

```
StartSignupFlow · StartClearFlow · StartInStoreFlow · StartPopNowFlow · StartNormalFlow
```

**五个名字里没有一个是店名。它们是五种任务种类：注册 · 清仓 · 到店 · PopNow 抽签 · 常规结账。**

### 二、复刻件的顶层只有店

`Modules/Registry.cs`（312 行）：

```
64 个 FlowStoreModule · 33 个流程类 · 33 个 shop id
enter · offspring · bodega · concepts · packershoes · socialstatus · undefeated · deadstock …
```

**没有「任务种类」这一层。`Registry` 问的是「有哪些店」，不是「有哪些种类的任务」。**

### 三、这解释了前面几轮的困难

**R854 我数出 67 段运行，然后问「那 20+ 段各属哪个站」——**
**而其中一部分属于**种类**，是跨站的，不对应任何站。所以按站去找必然错位。**

**R855 我把 sweepstake / lottery 猜成「任务变体」，R856 用 ordinal 否掉了它 ——
现在能说清它们为什么不像种类：种类是 `Start*Flow`（57–61），而在流程段（32–43）里的东西是**种类之下的流程步骤**。**

| | 镜像 | 复刻件 |
|---|---|---|
| 顶层 | **任务种类（5）** | **店（64 模块）** |
| 二层 | 站／变体的流程序列 | 33 个流程类 |
| 三层 | 风控 | 风控 |

### 四、这一条对「功能 1:1」意味着什么

**复刻件能表达「对 Nike 结账」，表达不了「执行一次抽签任务」和「执行一次常规结账」的区别 ——
因为后者在镜像里是顶层选择，在复刻件里不存在。**

**而这是一个**比缺 14 个方法更根本**的差距：
方法可以在现有结构里补，任务种类这一层没有对应的位置。**

**它和 R851 那个「一条通用序列 vs 八条按流程的序列」是同一个问题的两面：
R851 说流程序列的形状不同，这一轮说**序列之上还有一层选择**，而复刻件把那一层压成了「跑结账」。**

### 五、验证

```
ida.py str PopNow / SignupFlow / InStoreFlow -> 0x14337bdc4 与 0x14337cdcc（d__57–60、187–189）
replica\\src\\Cybersole.Stores\\Modules\\Registry.cs  312 行
  FlowStoreModule 64 · distinct flow classes 33 · shop id 字面量 33
grep 'Start.*Flow' replica\\src -> 无分派层
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **五个种类各自驱动哪些店**：**Unknown** ——
  `StartPopNowFlow` 显然指 Pop Mart，但 `StartClearFlow`「清仓」适用哪些店没查。
- **复刻件的任务配置里有没有「种类」这个字段**：**Unknown** ——
  `TaskColumn` 是表格列，不是任务种类。**这条要查 `Tasks` 模型。**
- **「64 个模块 / 33 个流程类」这个比例说明什么**：**Inference（中）** ——
  64 > 33 说明一个流程类被多个 shop id 复用（如多个 Shopify 店共用 `ShopifyFlow`），**这本身是复刻件的合理设计，
  但它把「店」当成了唯一的区分维度。**

### 七、教训

**R854 我问「那 20+ 段属哪个站」，问了三轮才发现顶层根本不是站。**

**而 R857 这一轮只做了一件事：读 `Registry.cs` 的前几行，看复刻件的顶层是什么。**
**这个检查本该在 R854 之前做 —— 在问「这些段属于谁」之前，先问「复刻件按什么维度组织」。**

**两个系统的顶层维度不同时，用一侧的维度去索引另一侧的条目，只会得到一堆对不上的行。**
"""

VERDICT = """

---

## 第 857 轮：镜像顶层是任务种类，复刻件顶层是店

### 镜像的五个入口不是五个站

```
StartSignupFlow · StartClearFlow · StartInStoreFlow · StartPopNowFlow · StartNormalFlow
```

**五种任务种类：注册 · 清仓 · 到店 · PopNow 抽签 · 常规结账。**

### 复刻件顶层只有店

`Registry.cs`（312 行）：**64 个 `FlowStoreModule` · 33 个流程类 · 33 个 shop id**（`enter` `offspring` `bodega` `concepts` …）
**没有「任务种类」这一层。**

### 这解释了前面几轮的困难

**R854 我数出 67 段运行，问「那 20+ 段各属哪个站」—— 而其中一部分属于**种类**，跨站，不对应任何站。按站去找必然错位。**

| | 镜像 | 复刻件 |
|---|---|---|
| 顶层 | **任务种类（5）** | **店（64 模块）** |
| 二层 | 站／变体的流程序列 | 33 个流程类 |
| 三层 | 风控 | 风控 |

### 对「功能 1:1」意味着什么

**复刻件能表达「对 Nike 结账」，表达不了「执行一次抽签任务」与「执行一次常规结账」的区别 ——
因为后者在镜像里是**顶层选择**，在复刻件里不存在。**

> **这比缺 14 个方法更根本：方法可以在现有结构里补，任务种类这一层没有对应的位置。**

**它和 R851 的「一条通用序列 vs 八条按流程的序列」是同一问题的两面 ——
R851 说序列形状不同，这一轮说**序列之上还有一层选择**，而复刻件把那一层压成了「跑结账」。**

### 仍然 Unknown

**五个种类各驱动哪些店**（`StartPopNowFlow` 显然指 Pop Mart，但「清仓」适用哪些没查）·
**复刻件的任务配置里有没有「种类」字段**（`TaskColumn` 是表格列，不是种类 —— 要查 `Tasks` 模型）·
**「64 模块 / 33 流程类」说明什么**（Inference 中：一流程类被多个 shop id 复用，**这本身合理，但它把「店」当成唯一区分维度**）

### 教训

> **在问「这些段属于谁」之前，先问「复刻件按什么维度组织」。**
> **两个系统的顶层维度不同时，用一侧的维度去索引另一侧的条目，只会得到一堆对不上的行。**
"""

BACKLOG_ADD = """

## 判据 (f) — 顶层维度不同（R857）

| | 镜像 | 复刻件 |
|---|---|---|
| **顶层** | **任务种类 5 种**：`StartSignupFlow` `StartClearFlow` `StartInStoreFlow` `StartPopNowFlow` `StartNormalFlow` | **店：64 模块 / 33 流程类 / 33 shop id** |
| 二层 | 站／变体的流程序列 | 33 流程类 |
| 三层 | 风控 | 风控 |

**→ 复刻件能表达「对 Nike 结账」，表达不了「抽签任务 vs 常规结账」的区别 —— 后者在镜像里是顶层选择。**

> **这比缺 14 个方法更根本：方法能在现有结构里补，任务种类这一层没有对应位置。**
> **R851（一条通用序列 vs 八条按流程序列）与 R857（序列之上还有一层选择）是同一问题的两面。**

| 仍 Unknown | |
|---|---|
| 5 个种类各驱动哪些店 | `StartPopNowFlow`→Pop Mart 明；「清仓」适用哪些未查 |
| 复刻件任务配置有无「种类」字段 | `TaskColumn` 是表格列；要查 `Tasks` 模型 |
| 64 模块 / 33 流程类 | 一流程类被多 shop id 复用（合理），但「店」成了唯一区分维度 |

**纪律**：**问「这些段属于谁」之前，先问「复刻件按什么维度组织」。维度不同时，用一侧的维度索引另一侧，只会得到对不上的行。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R857", BLOCKER)
    ensure(RSTATUS, "R857", BLOCKER)
    ensure(RVERDICT, "第 857 轮", VERDICT)
    ensure(BACKLOG, "R857", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R857" not in h:
        h += ("\n## R857 补充 — 顶层维度不同\n\n"
              "**镜像顶层 = 任务种类 5 种**（`StartSignupFlow` `StartClearFlow` `StartInStoreFlow` `StartPopNowFlow` `StartNormalFlow`）。\n"
              "**复刻件顶层 = 店**（`Registry.cs` 64 模块 / 33 流程类 / 33 shop id），**没有种类层**。\n"
              "**→ 复刻件能表达「对 Nike 结账」，表达不了「抽签任务 vs 常规结账」** —— 后者在镜像里是顶层选择。\n"
              "**这比缺 14 个方法更根本；与 R851（序列形状不同）是同一问题两面。**\n"
              "**规则：问「这些段属于谁」之前，先问「复刻件按什么维度组织」。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R857"), (RSTATUS, "R857"), (RVERDICT, "第 857 轮"), (BACKLOG, "R857")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R857: the image's top layer is task kind, the replica's is store\n\n"
         "R856 left five Start-flow entry points as the easiest open question -- what do they correspond to in the"
         " replica. Reading Registry.cs answers it. The replica has sixty-four FlowStoreModule entries over thirty-three"
         " flow classes and thirty-three shop ids like enter, offspring, bodega and concepts. Its top layer is the store.\n\n"
         "The image's top layer is not. StartSignupFlow, StartClearFlow, StartInStoreFlow, StartPopNowFlow and"
         " StartNormalFlow contain no store name among them. They are task kinds: signup, clearance, in-store, PopNow draw"
         " and ordinary checkout. So the shape is task kind times store, against the replica's store alone.\n\n"
         "That retroactively explains three rounds of difficulty. R854 counted sixty-seven runs and asked which site each"
         " belonged to, but some of them belong to a task kind and span stores, so indexing them by site could not line"
         " up. R855 guessed sweepstake and lottery were task variants and R856 refuted that by ordinal, and now the reason"
         " is visible: task kinds are the Start-flow entries numbered 57 to 61, whereas anything numbered in the thirties"
         " and forties is a flow step beneath a kind.\n\n"
         "For functional equivalence this is more fundamental than fourteen missing methods. Methods can be added inside"
         " the existing arrangement; a task-kind layer has nowhere to sit in it. The replica can express checking out at"
         " Nike and cannot express the difference between running a draw task and running an ordinary checkout, because"
         " in the image that difference is a top-level choice and in the replica it does not exist.\n\n"
         "It is also the other face of R851. There the finding was that flow sequences have a different shape; here it is"
         " that above the sequences sits a selection the replica has collapsed into 'run checkout'.\n\n"
         "Unknown: which stores each of the five kinds drives, since StartPopNowFlow obviously means Pop Mart while"
         " clearance's scope is unchecked; whether the replica's task configuration has a kind field at all, since"
         " TaskColumn is a grid column rather than a task kind and the Tasks model is where to look; and what the sixty-"
         " four-to-thirty-three ratio implies, which most likely means one flow class serving several shop ids -- a"
         " sensible arrangement that nonetheless makes the store the only axis of distinction.\n\n"
         "The lesson is an ordering of questions. Before asking which item an entry belongs to, ask along which dimension"
         " the other system is organised. When the two top dimensions differ, indexing one side's entries by the other"
         " side's dimension produces rows that cannot line up, and no amount of care in the indexing fixes it. Reading the"
         " first few lines of Registry.cs would have told me this before R854 rather than after R857.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
