"""Record R887: the 94 shape gaps decompose into three kinds over 63 members."""

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
### 94 条形状差异分解成 **3 类 × 63 个成员** —— 而最大的一块是 `Close`（R887）

**R886 把数字从 78 修到 94。这一轮把那 94 条分类，因为「94」本身不是可行动的信息。**

### 按复刻件现状分三类

| `replica=` | 条数 | 意思 |
|---|---|---|
| **`?`** | **44** | **成员在复刻件里根本不存在** |
| `method` | **34** | 复刻件有同名**方法**，而镜像是可写属性 |
| `prop-get` | **16** | 复刻件只有 getter，镜像有 Setter 证据 |

### 按成员名归族：94 条 = 63 个成员

| 成员 | 条数 | 分布 |
|---|---|---|
| **`Close`** | **15** | **全 `?`** |
| `Delete` | 8 | 5 `?` · 3 `method` |
| `Edit` | 3 | 2 `prop-get` · 1 `?` |
| `Save` | 3 | 全 `?` |
| `MoveGroup` | 3 | 全 `method` |
| `Reset` · `Running` · `Add` · `OpenUrl` | 各 2 | 混合 |
| 其余 55 个成员 | **各 1** | — |

**Top 6 个成员占 34 条（36%）。**

### 而这些名字说的是同一件事

**`Close` · `Delete` · `Save` · `Edit` · `Reset` · `Add` —— **全是视图上的动作成员**。**

**镜像把它们标成 `Getter,Property,Setter`，也就是**可写的 `ICommand` 属性**；
复刻件里它们要么不存在（`?`），要么是普通方法（`method`），要么是只读属性（`prop-get`）。**

**所以 94 条不是 94 个独立缺陷，是**一个结构故事**：
视图的动作成员在镜像里是可写 `ICommand` 属性。**

### 而 `?` 那 44 条里有两条值得单独看

```
BotTask    Running    evidence=Getter,Property,Setter    replica=?
BotTask    Task       evidence=Getter,Property,Setter    replica=?
```

**`BotTask.Task` 就是 R364 那个悬案！**

**而 R883 的结论是「`Type` 属于 `Drop`」。现在看：`BotTask` 缺的成员是 `Running` 和 `Task`，
两个都是 `Getter,Property,Setter` —— 也就是说它们在镜像里是**可写属性**。**

**所以 R364 那个问题的答案更完整了：`BotTask.Task` 在镜像里是**可写属性**，
而 R883 说的 `Drop.Type` 是另一件事（任务类型 vs 任务本身）。**
"""

if "94 条形状差异分解成 **3 类 × 63 个成员**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R887 appended")

BLOCKER = """

---

## 311. 94 条形状差异 = 3 类 × 63 成员，最大一块是 `Close` × 15

> R887。未改产品代码。

### 一、三类

| `replica=` | 条数 | 意思 |
|---|---|---|
| **`?`** | **44** | 成员不存在 |
| `method` | **34** | 有同名方法，镜像是可写属性 |
| `prop-get` | **16** | 只有 getter |

### 二、按成员归族

| 成员 | 条数 |
|---|---|
| **`Close`** | **15（全 `?`）** |
| `Delete` | 8 |
| `Edit` · `Save` · `MoveGroup` | 各 3 |
| `Reset` · `Running` · `Add` · `OpenUrl` | 各 2 |
| 其余 55 | 各 1 |

**94 条 = 63 个成员。Top 6 占 34 条（36%）。**

### 三、这些名字是一个结构故事

**`Close` `Delete` `Save` `Edit` `Reset` `Add` 全是**视图上的动作成员**。
镜像标它们 `Getter,Property,Setter`，即**可写的 `ICommand` 属性**。**

**所以 94 条不是 94 个独立缺陷 —— 是同一件事在 63 个成员上的复现。**

**而这意味着修它是一次形态改造（动作成员从方法改成 `ICommand` 属性），不是 63 次补丁。
而那份改造清单 `AGENTS.md §3` 已经写好了（R468–R499 踩了七次的八项）。**

### 四、`BotTask` 那条给 R364 的答案更完整

```
BotTask    Running    evidence=Getter,Property,Setter    replica=?
BotTask    Task       evidence=Getter,Property,Setter    replica=?
```

**`BotTask.Task` 就是 R364 那个悬案。它是 `Getter,Property,Setter` —— **可写属性**。**

**R883 说的是 `Drop.Type`（任务类型挂在哪）；这一条说的是 `BotTask.Task`（任务本身）
在镜像里是可写属性。两件事，而之前我把它们混在一起想过。**

**所以 R364 的问题可以更准地重述：不是「`Task` 是什么类型」，而是
「`Task` 是 `BotTask` 上一个**可写属性**，而 `Type` 挂在 `Drop` 上」。**

### 五、验证

```
shape_audit.py --baseline | 按 replica= 统计 -> ? 44 · method 34 · prop-get 16
同输出按成员名归族                       -> 63 个成员；Close 15 · Delete 8 · Edit/Save/MoveGroup 3 …
BotTask 的 ? 行                           -> Running · Task，均 evidence=Getter,Property,Setter
本轮未改产品代码；套件沿用 1780
```

### 六、仍然 Unknown

- **`Close` × 15 该不该一次改**：**Unknown，而这是本轮之后最该判的。**
  **15 个视图各加一个 `ICommand Close` 是机械的，但 `AGENTS.md §3` 那八项连带清单意味着每次改动要动
  构造函数、类内调用点、方法组引用、测试断言 —— 15 次 × 8 项。可能的失败模式是改到一半。**
- **`method` 那 34 条是不是该全部改成属性**：**Unknown** ——
  **镜像是可写属性不代表复刻件必须一样；但 1:1 的目标要求形态一致。**
- **`prop-get` 那 16 条加 setter 会不会破坏什么**：**Unknown** ——
  **只读属性改成可写，绑定的双向行为会变。**

### 七、教训

**R886 把数字从 78 修到 94，而 94 本身不可行动。
这一轮把它拆成「3 类 × 63 成员，最大一块 15 条且有同一个名字」——
那一刻它从「一个数字」变成了「一件事」。**

**所以报数字和报结构不是同一件事。前者说差多少，后者说差在哪、是不是同一处。
而我前面几轮一直在报数字。**
"""

VERDICT = """

---

## 第 887 轮：94 条形状差异 = 3 类 × 63 成员，最大一块是 `Close` × 15

### 三类

| `replica=` | 条数 | 意思 |
|---|---|---|
| **`?`** | **44** | 成员不存在 |
| `method` | **34** | 有同名方法，镜像是可写属性 |
| `prop-get` | **16** | 只有 getter |

### 按成员归族：94 条 = 63 个成员

| 成员 | 条数 |
|---|---|
| **`Close`** | **15（全 `?`）** |
| `Delete` | 8 |
| `Edit` · `Save` · `MoveGroup` | 各 3 |
| `Reset` · `Running` · `Add` · `OpenUrl` | 各 2 |
| 其余 55 | 各 1 |

**Top 6 占 34 条（36%）。**

### 这些名字是**一个结构故事**

**`Close` `Delete` `Save` `Edit` `Reset` `Add` 全是视图上的动作成员。
镜像标它们 `Getter,Property,Setter` = **可写的 `ICommand` 属性**。**

> **所以 94 条不是 94 个独立缺陷，是同一件事在 63 个成员上的复现。**
> **修它是一次形态改造（动作成员 → `ICommand` 属性），不是 63 次补丁 —— 而 `AGENTS.md §3` 那八项连带清单就是为这件事写的。**

### `BotTask` 给 R364 的答案更完整

```
BotTask    Running    evidence=Getter,Property,Setter    replica=?
BotTask    Task       evidence=Getter,Property,Setter    replica=?
```

**`BotTask.Task` 是 `Getter,Property,Setter` —— **可写属性**。**

**R883 说的是 `Drop.Type`（类型挂在哪）；这一条说的是 `BotTask.Task`（任务本身是可写属性）。两件事。**

> **所以 R364 可以更准地重述：不是「`Task` 是什么类型」，而是「`Task` 是 `BotTask` 上一个可写属性，而 `Type` 挂在 `Drop` 上」。**

### 仍然 Unknown

**`Close` × 15 该不该一次改**（**最该判：15 × 8 项连带，可能的失败模式是改到一半**）·
**`method` 那 34 条是否全改属性** · **`prop-get` 那 16 条加 setter 会不会破坏双向绑定**

### 教训

> **R886 把数字从 78 修到 94，而 94 本身不可行动。**
> **这一轮拆成「3 类 × 63 成员，最大一块 15 条且同一个名字」—— 那一刻它从「一个数字」变成了「一件事」。**
> **报数字和报结构不是同一件事：前者说差多少，后者说差在哪、是不是同一处。**
"""

BACKLOG_ADD = """

## 判据 — 94 条形状差异 = **3 类 × 63 成员**（R887）

| `replica=` | 条数 |
|---|---|
| **`?`**（成员不存在） | **44** |
| `method`（有方法，镜像是可写属性） | **34** |
| `prop-get`（只有 getter） | **16** |

### 按成员归族：94 条 = 63 个成员

| 成员 | 条数 |
|---|---|
| **`Close`** | **15（全 `?`）** |
| `Delete` | 8 |
| `Edit` · `Save` · `MoveGroup` | 各 3 |
| `Reset` · `Running` · `Add` · `OpenUrl` | 各 2 |
| 其余 55 | 各 1 |

### 一个结构故事

**`Close`/`Delete`/`Save`/`Edit`/`Reset`/`Add` 全是视图动作成员；镜像是**可写 `ICommand` 属性**。**
**→ 94 条 = 同一件事在 63 个成员上的复现，修它是一次形态改造（`AGENTS.md §3` 八项连带清单就是为这件写的）。**

### `BotTask` 给 R364 更完整的答案

**`BotTask.Running` / `BotTask.Task` 均 `Getter,Property,Setter` → **可写属性**。
R883 的 `Drop.Type` 是「类型挂在哪」，这条是「任务本身是可写属性」——两件事。**
**→ R364 重述：`Task` 是 `BotTask` 上一个可写属性，而 `Type` 挂在 `Drop` 上。**

| 仍 Unknown | |
|---|---|
| **`Close`×15 该不该一次改** | **最该判：15×8 项连带，可能改到一半** |
| `method` 34 条是否全改属性 | 1:1 目标要求形态一致 |
| `prop-get` 16 条加 setter 会不会破坏双向绑定 | 未查 |

**纪律**：**报数字说差多少，报结构说差在哪 —— 94 不可行动，`Close × 15` 可以。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R887", BLOCKER)
    ensure(RSTATUS, "R887", BLOCKER)
    ensure(RVERDICT, "第 887 轮", VERDICT)
    ensure(BACKLOG, "R887", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R887" not in h:
        h += ("\n## R887 补充 — 94 条形状差异 = 3 类 × 63 成员（**未改产品代码**）\n\n"
              "**分类**：`?` 44（不存在）· `method` 34（有方法，镜像是可写属性）· `prop-get` 16（只有 getter）。\n"
              "**归族**：94 条 = 63 成员；**`Close` 15（全 `?`）** · `Delete` 8 · `Edit`/`Save`/`MoveGroup` 各 3 · 其余 55 各 1。\n"
              "**一个结构故事**：`Close`/`Delete`/`Save`/`Edit`/`Reset`/`Add` 全是视图动作成员，镜像是**可写 `ICommand` 属性** → **一次形态改造，不是 63 次补丁**（`AGENTS.md §3` 八项清单）。\n"
              "**`BotTask.Running`/`Task` 均 `Getter,Property,Setter` → 可写属性**；与 R883 的 `Drop.Type` 是两件事。**R364 重述：`Task` 是可写属性，`Type` 挂在 `Drop` 上。**\n"
              "**最该判：`Close`×15 要不要一次改**（15×8 项连带，可能改到一半）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R887"), (RSTATUS, "R887"), (RVERDICT, "第 887 轮"), (BACKLOG, "R887")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R887: the ninety-four shape gaps are three kinds over sixty-three members, and Close is a fifth of them\n\n"
         "R886 corrected the figure from seventy-eight to ninety-four. A count that size is not actionable, so this round\n"
         " classified it.\n\n"
         "By what the replica currently has: forty-four rows are members that do not exist at all, thirty-four exist as\n"
         " methods where the image has a settable property, and sixteen exist read-only where the image evidences a\n"
         " setter.\n\n"
         "By member name the ninety-four rows collapse to sixty-three members. Close accounts for fifteen, every one of\n"
         " them absent; Delete for eight; Edit, Save and MoveGroup for three each; Reset, Running, Add and OpenUrl for two\n"
         " each; and fifty-five members appear once. The top six names are a third of the total.\n\n"
         "Those names tell one story rather than sixty-three. Close, Delete, Save, Edit, Reset and Add are all action\n"
         " members on views, and the image marks each Getter,Property,Setter -- settable ICommand properties. The replica\n"
         " has them missing, or as plain methods, or as read-only properties. So this is a single shape difference\n"
         " repeated across sixty-three members, and the remedy is one conversion rather than sixty-three patches. The\n"
         " eight-item checklist in AGENTS.md section 3 exists for exactly that conversion, written after seven rounds of\n"
         " getting it wrong.\n\n"
         "BotTask appears twice in the absent list, as Running and as Task, both with Getter,Property,Setter. Task is the\n"
         " member whose type has been unknown since R364. So R883's finding about Drop.Type and this one are separate\n"
         " facts: Drop carries the kind of drop, while Task on BotTask is itself a settable property. R364's question is\n"
         " better put as which member carries what than as what type Task has.\n\n"
         "Unknown: whether the fifteen Close members should be converted in one pass, which is now the judgement to\n"
         " make, since each conversion touches the eight items in the checklist and fifteen of them in one round invites\n"
         " stopping halfway; whether the thirty-four method-shaped rows should all become properties, since matching the\n"
         " image's shape is what a 1:1 claim requires even where behaviour is unchanged; and whether adding setters to the\n"
         " sixteen read-only members would change two-way binding behaviour.\n\n"
         "The lesson is that reporting a number and reporting structure are different acts. Ninety-four says how much is\n"
         " wrong; three kinds over sixty-three members with a dominant name says where and whether it is one place. I\n"
         " have been reporting numbers for several rounds.\n\n"
         "No product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
