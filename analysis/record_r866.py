"""Record R866: implementing any of those steps requires the structural fix first."""

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
### 「实现那几个步骤」有前置条件：**先做结构改动**（R866）

**核了三处：**

| 位置 | `GetOrders` / `StartDrawFlow` / `FindDraw` / `EnterDraw` / `GetInstoreOrders` |
|---|---|
| `StoreFlow` 的 165 个虚步骤 | **一个都没有** |
| `StoreFlowRunner` 的 21 步序列 | **一个都没有** |
| `PopMartFlow` 的 11 个重写 | **一个都没有** |

**所以实现它们要三步：加基类虚方法 · 在流程里重写 · **加进 runner**。**

**而第三步是问题：runner 的序列是通用的 —— 加一条进去，**所有流程都会调它**。**

### 两条路都通向坏结果

| 做法 | 结果 |
|---|---|
| **加进 runner** | **所有流程都调 `GetOrders`**，包括那些没有订单概念的 —— 假调用 |
| **不加进 runner** | **方法存在但没人调** —— 正是 R858 那个「死字段」的形态，只是换成方法 |

**所以这不是取舍，是**前置关系**：**

> **要写这些步骤，必须先让 runner 能按流程取序列（R851 的做法 1）。
> 否则写出来的每一条，要么污染别的流程，要么是死代码。**

### 这条对优先级 ① 的顺序意义

**R850 说「3 个可写，11 个只有端点没形状」。这一轮补上：**
**那 3 个也**不是现在能写的** —— 写它们要先有结构。**

**所以优先级 ① 的下一步不是「写 PopMart 的步骤」，是：**

1. **给 `StoreFlow` 加 `IReadOnlyList<Step>`（或等价物），每条流程返回自己的序列**
2. **runner 改成按流程取序列，而不是一条固定 21 步**
3. **然后才能加 `GetOrders` / `StartDrawFlow` / `FindDraw`，并且它们只在该流程里跑**

**这是一个可界定的改动，但它动的是 1897 行的 `StoreFlow` 与 294 行的 runner —— 不是一轮能顺手做完的。**
"""

if "「实现那几个步骤」有前置条件：**先做结构改动**（R866" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: prerequisite appended")

BLOCKER = """

---

## 290. **前置关系**：不加结构就写不了那些步骤

> R866。未改产品代码。**这一轮本来想写代码，查出写不了。**

### 一、核了三处

| 位置 | `GetOrders` · `StartDrawFlow` · `FindDraw` · `EnterDraw` · `GetInstoreOrders` |
|---|---|
| `StoreFlow` 165 个虚步骤 | **0** |
| `StoreFlowRunner` 21 步序列 | **0** |
| `PopMartFlow` 11 个重写 | **0** |

**所以实现任何一条都要三步：基类虚方法 · 流程重写 · **进 runner**。**

### 二、而第三步让两条路都通向坏结果

| 做法 | 结果 |
|---|---|
| **进 runner** | runner 序列是通用的 —— **所有流程都会调 `GetOrders`**，包括没有订单概念的，这是假调用 |
| **不进 runner** | **方法在但没人调** —— R858 那个死字段的形态，只是换成方法 |

**所以这不是取舍，是**前置关系**：**

> **要写这些步骤，必须先让 runner 能按流程取序列。否则写出来的每一条，要么污染别的流程，要么是死代码。**

### 三、这修正了 R850 的判断

**R850 写「3 个可写（`StartDrawFlow` `FindDraw` `GetOrders`），11 个只有端点没形状」。**

**这一轮补上：那 3 个**现在也写不了** —— 写它们要先有结构。**

**R850 判的是「证据够不够」，这一轮判的是「位置有没有」。两条都过才算可写，而我只查了第一条。**

### 四、所以优先级 ① 的下一步是结构，不是步骤

1. **给 `StoreFlow` 加一个步骤列表（`IReadOnlyList<Step>` 或等价物），每条流程返回自己的序列**
2. **runner 改成按流程取序列，而不是一条固定 21 步**
3. **然后才能加 `GetOrders` / `StartDrawFlow` / `FindDraw`，且只在该流程里跑**

**这是可界定的改动，但动的是 1897 行的 `StoreFlow` 与 294 行的 runner —— 不是一轮能顺手做完的。**

**而它同时也解掉 R851 那个「一条通用序列 vs 八条按流程的序列」，
以及 R857 那个「顶层是店而不是任务种类」的一半（种类可以表达成序列的选择）。**

### 五、为什么不这轮就动

**因为改 `StoreFlow` 的形状会影响 165 个声明、33 个流程类、以及 1766 个用例。
这类改动必须先估影响面，而估影响面本身要先读 `StoreFlow` 的程序结构 —— 那是下一轮的事。**

**而「想清楚顺序」这一轮的产出，比「写三个方法然后把它们藏起来」有用。**

### 六、验证

```
replica\\src\\Cybersole.Stores\\Flows\\StoreFlow.cs        1897 行；virtual steps 165
   GetOrders / GetInstoreOrders / StartDrawFlow / FindDraw / EnterDraw -> 全 no
replica\\src\\Cybersole.Stores\\Flows\\StoreFlowRunner.cs   294 行；tuple steps 21；GetOrders 不在
replica\\src\\Cybersole.Stores\\Flows\\PopMartFlow.cs       344 行；11 个重写，无订单/抽签步骤
本轮未改产品代码
七项度量沿用
```

### 七、仍然 Unknown

- **`StoreFlow` 那 165 个虚步骤是怎么被组织成一个序列的**：**Unknown** ——
  **现在是 runner 手写列表；如果 `StoreFlow` 自己有一个有序列表，改造会小得多。**
- **33 个流程类里，有多少需要「非结账」序列**：**Unknown** ——
  **PopMart 需要，Nike 大概不需要，其余没查。**
- **1766 个用例里有多少会因为 runner 改动而红**：**Unknown** —— **这是改造前必须先估的。**

### 八、教训

**R850 我判「3 个可写」，判据是「证据够不够」。**
**这一轮一动手才发现还有第二个判据：「位置有没有」。**

**而这两个判据的差别，就是「能不能写对」和「能不能写」的差别 ——
只过第一个，写出来的东西是对的，但放不进系统里。**
"""

VERDICT = """

---

## 第 866 轮：前置关系 —— 不加结构就写不了那些步骤

### 本来想写代码，查出写不了

| 位置 | `GetOrders` · `StartDrawFlow` · `FindDraw` · `EnterDraw` · `GetInstoreOrders` |
|---|---|
| `StoreFlow` 165 个虚步骤 | **0** |
| `StoreFlowRunner` 21 步序列 | **0** |
| `PopMartFlow` 11 个重写 | **0** |

### 而第三步让两条路都通向坏结果

| 做法 | 结果 |
|---|---|
| **进 runner** | runner 是通用序列 —— **所有流程都会调 `GetOrders`**，包括没有订单概念的 |
| **不进 runner** | **方法在但没人调** —— R858 死字段的形态，换成方法 |

> **这不是取舍，是前置关系：要先让 runner 能按流程取序列。否则写出来的每一条，要么污染别的流程，要么是死代码。**

### 这修正了 R850

**R850 写「3 个可写」，判据是「证据够不够」。这一轮发现还有第二个判据：「位置有没有」。
**两条都过才算可写，而我只查了第一条。**

### 所以优先级 ① 的下一步是结构，不是步骤

1. **`StoreFlow` 加步骤列表，每条流程返回自己的序列**
2. **runner 按流程取序列，而不是固定 21 步**
3. **然后才能加 `GetOrders` / `StartDrawFlow` / `FindDraw`，且只在该流程里跑**

**它同时也解掉 R851（一条通用序列 vs 八条按流程）与 R857（顶层维度）的一半。**

### 为什么不这轮就动

**改 `StoreFlow` 的形状会影响 165 个声明、33 个流程类、1766 个用例。
这类改动必须先估影响面，而估影响面要先读 `StoreFlow` 的结构 —— 那是下一轮的事。**

> **「想清楚顺序」这一轮的产出，比「写三个方法然后把它们藏起来」有用。**

### 仍然 Unknown

**`StoreFlow` 那 165 个虚步骤是怎么组织成序列的**（现在是 runner 手写；**若 `StoreFlow` 自己有序列表，改造小得多**）·
**33 个流程类里有多少需要「非结账」序列**（PopMart 需要，Nike 大概不需要，其余没查）·
**1766 个用例里有多少会因 runner 改动而红**（**改造前必须先估**）

### 教训

**「能不能写对」和「能不能写」是两个判据。只过第一个，写出来的东西是对的，但放不进系统里。**
"""

BACKLOG_ADD = """

## 优先级 ① — 前置关系：不加结构写不了步骤（R866）

| 位置 | `GetOrders` / `StartDrawFlow` / `FindDraw` / `EnterDraw` | |
|---|---|---|
| `StoreFlow` 165 虚步骤 | **0** | |
| `StoreFlowRunner` 21 序列 | **0** | |
| `PopMartFlow` 11 重写 | **0** | |

**两步都通向坏结果：进 runner → 污染所有流程；不进 → 死代码（R858 形态）。**

> **前置关系：要先让 runner 按流程取序列。否则每条要么污染别人，要么是死代码。**

### 修正 R850

**R850 判「3 个可写」= 只查了「证据够不够」；漏了「位置有没有」。两条都过才算可写。**

### 下一步是三件事（不是一轮的量）

1. `StoreFlow` 加步骤列表，每流程返回自己的序列
2. runner 按流程取序列
3. 然后才能加 `GetOrders` / `StartDrawFlow` / `FindDraw`

**同时解掉 R851 与 R857 的一半。**

| 仍 Unknown | |
|---|---|
| `StoreFlow` 165 虚步骤如何组织成序列 | 若自带有序列表，改造小得多 |
| 33 流程类里多少需非结账序列 | PopMart 需；Nike 大概不需；其余未查 |
| **1766 用例多少会红** | **改造前必须先估** |

**纪律**：**「能不能写对」和「能不能写」是两个判据。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R866", BLOCKER)
    ensure(RSTATUS, "R866", BLOCKER)
    ensure(RVERDICT, "第 866 轮", VERDICT)
    ensure(BACKLOG, "R866", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R866" not in h:
        h += ("\n## R866 补充 — 前置关系\n\n"
              "**`GetOrders` / 抽签几步：`StoreFlow` 165 虚步骤里 0 · runner 21 序列里 0 · PopMartFlow 11 重写里 0。**\n"
              "**进 runner → 污染所有流程；不进 → 死代码（R858 形态）。→ **前置关系：先让 runner 按流程取序列**。**\n"
              "**修正 R850：它判「3 个可写」只查了「证据够不够」，漏了「位置有没有」。**\n"
              "**下一步三件事：`StoreFlow` 加步骤列表 · runner 按流程取 · 再加步骤。** 影响 165 声明 / 33 流程类 / 1766 用例，**须先估影响面**。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R866"), (RSTATUS, "R866"), (RVERDICT, "第 866 轮"), (BACKLOG, "R866")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R866: none of those steps can be written without the structural change first\n\n"
         "This round set out to write code, having spent a dozen rounds on evidence. It found the code cannot be"
         " written yet. GetOrders, StartDrawFlow, FindDraw, EnterDraw and GetInstoreOrders are absent from all three"
         " places they would need to be: StoreFlow's 165 virtual steps, the runner's twenty-one-entry tuple sequence, and"
         " PopMartFlow's eleven overrides.\n\n"
         "Implementing any of them therefore takes three moves -- a base virtual, a flow override, and an entry in the"
         " runner -- and the third move is where both routes go wrong. Adding to the runner puts the call in the single"
         " generic sequence, so every flow would invoke an order fetch whether or not it has an order concept. Not adding"
         " leaves the method present and uncalled, which is the dead-field shape of R858 wearing a method's clothes.\n\n"
         "So this is a prerequisite rather than a trade-off. Before any of these steps can exist, the runner has to take"
         " a sequence per flow. Written before that, each step either leaks into flows it does not belong to or is never"
         " reached.\n\n"
         "It also corrects R850, which judged three of the fourteen writable. That judgement asked whether the evidence"
         " sufficed and never asked whether there was anywhere to put the result. Both questions have to pass; I only"
         " asked the first.\n\n"
         "The next move for priority one is therefore structural: give StoreFlow a step list that each flow returns, turn"
         " the runner into something that takes it, and only then add GetOrders, StartDrawFlow and FindDraw so they run"
         " where they belong. That same change answers half of R851's generic-against-per-flow finding and half of R857's"
         " top-dimension finding, since a task kind can be expressed as a choice of sequence.\n\n"
         "It was not done this round because the change touches 165 declarations, 33 flow classes and 1766 tests, and"
         " estimating that blast radius means reading StoreFlow's structure first, which is the next round's work. Working"
         " out the order was the useful output; three methods hidden away would not have been.\n\n"
         "Unknown: how StoreFlow's 165 virtual steps are organised into a sequence today, since the runner holds a"
         " hand-written list and a flow-owned ordered list would make the change much smaller; how many of the 33 flow"
         " classes need a non-checkout sequence, where Pop Mart clearly does and Nike probably does not while the rest are"
         " unchecked; and how many of the 1766 tests would go red under a runner change, which must be estimated before\n"
         " touching it.\n\n"
         "The lesson is that being able to write something correctly and being able to write it are two different tests."
         " Passing only the first produces code that is right in itself and fits nowhere.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
