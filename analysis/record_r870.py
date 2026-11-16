"""Record R870: the rule from R869 became a script and a doctrine section."""

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
### 把「写之前先查」做成一个命令：`tools/where_is.py`（R870）

**R869 的教训是「先查有没有现成的，要包括**实现**」。而教训写成人话会被忘 —— 五轮里忘了五次。
所以做成一个能跑的东西，并且写进 `AGENTS.md §2.7c`。**

```
python tools\\where_is.py <名字>
```

**它按四类报出所有位置：**

| 组 | 判据（只看文件名与路径，不看内容） | 回答什么 |
|---|---|---|
| **implementation** | 兜底 | **定义行为的地方 —— 先读这一组** |
| analysis | 文件名含 `StepMap` / `Steps` / `Path` / `Controllers` / `ApiFamilies` / `Endpoints` / `Witness` / `Candidate` / `Parity` / `Claims` | 已经算过的分析 |
| test | 路径含 `tests/` | 已钉住的行为 |
| doc | `.md` / `.txt` / `.json` | 结论可能已写下 |

**分组只看名字，不看内容 —— 所以可复现、可解释，不需要模型判断。**

### 它自己第一次用就暴露了一个 bug

**第一版没排除 `tools/.snapshots/` —— 那是 `snapshot.py` 每次改动前留的全量副本。
结果 `StepActionRunner` 报「39 个文件」，其中 29 个是历史快照。**

**修掉之后：**

```
StepActionRunner --word  -> 7 files
    implementation (3): StoreFlow.cs(5) · StepAction.cs(1) · StoreFlowRunner.cs(1)
    test           (1): StepActionTests.cs(4)
    doc            (3): VERDICT.md · BINDING_BACKLOG.md · HISTORY.md
```

**`PopMart` 那条也是干净的：31 个文件，implementation 5（`PopMartFlow` 18 处）、
analysis 4（`PopMartStepMap` 18 处 · `LambdaWitness` · `PopMartEndpoints` · `StoreFlowSteps`）。**

**分析组正确分出来的意义：R835–R838 那四轮我该看的就是这一组。**

### 它有一条边界写在文件头

**它不查镜像。**问「原版怎么做」是 `analysis/ida.py str`，这个脚本只答「复刻件里有没有」。
**两者混用会产生假的「不存在」（§2.7b 已经踩过四次）。**
"""

if "把「写之前先查」做成一个命令：`tools/where_is.py`（R870" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: where_is appended")

BLOCKER = """

---

## 294. 教训做成了命令：`tools/where_is.py` + `AGENTS.md §2.7c`

> R870。未改 C#，新增一个 Python 工具与一节操典。

### 一、为什么做成脚本而不是一段话

**「写之前先查有没有现成的」这句话，我在 R843 / R845 / R846 / R848 / R869 各写了一遍，五次各忘一次。
第六遍写成话还是会忘 —— 所以写成能跑的东西。**

```
python tools\\where_is.py <名字>
```

**按四类分组：**

| 组 | 回答 |
|---|---|
| **implementation** | **定义行为的地方 —— 先读这组** |
| analysis | `*StepMap` / `*Steps` / `*Path` / `*Controllers` / `*Endpoints` / `*Witness` 这类「已经算过」的 |
| test | 已钉住的行为 |
| doc | 结论可能已写下 |

**分组只看文件名与路径，不看内容。**这是刻意的：**可复现、可解释、不需要模型判断** ——
与 §2 那条「结论要能被第三方重算」一致。

### 二、它第一次用就抓到自己的 bug

**第一版没排除 `tools/.snapshots/`（`snapshot.py` 每次改动前留的全量副本）。
`StepActionRunner` 报 39 个文件，其中 29 个是历史快照。**

**修掉之后：**

```
StepActionRunner --word -> 7 files
    implementation: StoreFlow.cs · StepAction.cs · StoreFlowRunner.cs
    test:           StepActionTests.cs
    doc:            VERDICT.md · BINDING_BACKLOG.md · HISTORY.md

PopMart -> 31 files
    implementation: PopMartFlow.cs(18) · MonitorFilterPolicy.cs(2) · Profiles.cs · Registry.cs · RetailModules.cs
    analysis:       PopMartStepMap.cs(18) · LambdaWitness.cs(2) · PopMartEndpoints.cs(2) · StoreFlowSteps.cs(2)
```

**`PopMart` 那条正好说明它有用：如果我 R835 就跑过这一行，analysis 组会直接把 `PopMartStepMap` 推到我面前 ——
而那正是 R849 才发现我六轮都没读的文件。**

### 三、写进操典，因为工具不会被记住，操典会

**`AGENTS.md §2.7c`，五次踩坑的表放在规则前面：**

| 轮 | 我造了什么 | 仓里早已有 |
|---|---|---|
| R843 | 115 个名字的清单 | `StoreFlowSteps.cs` |
| R845 | 「108 条不同名」 | `StoreFlow` 165 虚步骤 |
| R846 | dual 9 条待判 | `ScapiAppPath.cs` |
| R848 | collectplus 4 条待办 | `LambdaWitness.Unwitnessed` |
| **R868→R869** | **一张反射派发表** | **`StepActionRunner`** |

**配套两条也写进去了：**

- **「先查有没有现成的」要包括**实现**，不只是分析。** 前四次我都只想到分析文件。
- **一个名字在 implementation 组里出现，就先去读那个文件再决定写不写。**
  查的成本三分钟；重复品和假成功的成本是两轮。

### 四、它不做什么（边界写在文件头）

**不查镜像。**问「原版怎么做」是 `analysis/ida.py str`；这个脚本只答「复刻件里有没有」。
**两者混用会产生假的「不存在」—— §2.7b 已踩四次。**

**也不判「该不该有」。**它只报位置，判断留给人。

### 五、验证

```
python tools\\where_is.py StepDispatch      -> 5 files（impl 2 / test 1 / doc 2）
python tools\\where_is.py StepActionRunner --word -> 7 files（impl 3 / test 1 / doc 3）
python tools\\where_is.py PopMart           -> 31 files（impl 5 / analysis 4 / …）
AGENTS.md §2.7c 已写入（工具段落 + 五次踩坑表 + 两条配套）
本轮未改 C# 代码
套件沿用 1773 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **`where_is` 的分组判据靠文件名**：**这是它的弱点** ——
  一个叫 `Foo.cs` 但内容是分析的文件会被归到 implementation。
  **R870 没处理这个；出现误判时按「把文件改名」处理，不要给脚本加启发式。**
- **它没有测试**：**Unknown 是否值得加** ——
  **它是个只读脚本，输出靠人读；加 xunit 去 shell 一个 Python 进程，成本可能高于收益。**
- **`AGENTS.md §2.7c` 会不会被读到**：**这是它真正的风险** ——
  **规则文件写了不等于读了，R861 就是没读 `BINDING_BACKLOG.md` 而白走四轮。**

### 七、教训

**一个教训被重复写五遍，说明「写下来」不是修复手段。**

**真正起作用的是两件：**
**① 它有一个命令，成本三分钟，不需要我记得；**
**② 它有一个编号（§2.7c），能被我或下一个会话当成检查项引用。**

**而这两件都不是新的洞察 —— 是这个仓库已经在用的做法（§2.7 与 §2.7b 都是这样）。
我只是终于把同一条办法用在自己身上。**
"""

VERDICT = """

---

## 第 870 轮：教训做成了命令

### 为什么做成脚本

**「写之前先查有没有现成的」我在 R843/R845/R846/R848/R869 各写了一遍，五次各忘一次。第六遍写成话还是会忘。**

```
python tools\\where_is.py <名字>
```

| 组 | 回答 |
|---|---|
| **implementation** | **定义行为的地方 —— 先读这组** |
| analysis | `*StepMap` / `*Steps` / `*Path` / `*Controllers` / `*Endpoints` / `*Witness` |
| test | 已钉住的行为 |
| doc | 结论可能已写下 |

**分组只看文件名与路径，不看内容 —— 可复现、可解释、不需要模型判断。**

### 它第一次用就抓到自己的 bug

**没排除 `tools/.snapshots/`（`snapshot.py` 的全量副本）→ `StepActionRunner` 报 39 个文件，29 个是历史快照。**

**修后：`StepActionRunner` 7 files（impl 3 / test 1 / doc 3）；`PopMart` 31 files，
analysis 组里有 `PopMartStepMap.cs`(18) —— **那正是 R849 才发现我六轮没读的文件。**
如果我 R835 跑过这一行，它会直接推到我面前。**

### 写进操典

**`AGENTS.md §2.7c`，五次踩坑表在规则前面：**

| 轮 | 我造了什么 | 仓里早已有 |
|---|---|---|
| R843 | 115 个名字 | `StoreFlowSteps.cs` |
| R845 | 「108 条不同名」 | `StoreFlow` 165 虚步骤 |
| R846 | dual 9 条 | `ScapiAppPath.cs` |
| R848 | collectplus 4 条 | `LambdaWitness.Unwitnessed` |
| **R868→R869** | **反射派发表** | **`StepActionRunner`** |

**两条配套：「先查有没有现成的」要包括**实现**；implementation 组有命中就先读再写。**

### 边界写在文件头

**不查镜像**（那是 `analysis/ida.py str`）· **不判「该不该有」**，只报位置。

### 仍然 Unknown

**分组靠文件名**（叫 `Foo.cs` 的分析文件会误归 implementation —— **出现误判就改名，不要给脚本加启发式**）·
**它没有测试**（只读脚本，输出靠人读）·
**§2.7c 会不会被读到** —— **这是真正的风险：规则写了不等于读了，R861 就是没读 backlog 而白走四轮**

### 教训

> **一个教训被重复写五遍，说明「写下来」不是修复手段。**
> **起作用的是两件：① 它有一个三分钟成本的命令，不需要我记得；② 它有一个编号，能当检查项引用。**
> **而这两件都不是新洞察 —— 这个仓库的 §2.7 与 §2.7b 一直是这样用的。我只是终于把同一条办法用在自己身上。**
"""

BACKLOG_ADD = """

## 方法 — `tools/where_is.py` + `AGENTS.md §2.7c`（R870）

**「写之前先查有没有现成的」被写成命令（五次遗忘之后）：**

```
python tools\\where_is.py <名字>     # 按 implementation / analysis / test / doc 四组报位置
python tools\\where_is.py StepDispatch --kind impl
python tools\\where_is.py Sequence --all
```

**分组只看文件名与路径，不看内容 → 可复现、可解释。**
**它第一次用就抓到自己没排除 `tools/.snapshots/`（`StepActionRunner` 报 39 个文件，29 个是历史快照），已修。**

### 实测

| 名字 | 结果 |
|---|---|
| `StepActionRunner --word` | 7 files（impl 3 / test 1 / doc 3） |
| `PopMart` | 31 files（impl 5 / **analysis 4，含 `PopMartStepMap.cs`(18)**） |

**`PopMart` 那条说明它有用：R835 若跑过，`PopMartStepMap` 会直接出现 —— 而那是我 R849 才发现六轮没读的文件。**

### 边界

**不查镜像**（`analysis/ida.py str`）· **不判该不该有**，只报位置。

| 仍 Unknown | |
|---|---|
| 分组靠文件名 | 误判就改名，不加启发式 |
| 无测试 | 只读脚本，输出靠人读 |
| **§2.7c 会被读到吗** | **真风险：R861 就是没读 backlog 白走四轮** |

**纪律**：**教训写五遍没用；有用的是一个三分钟成本的命令 + 一个可引用的编号。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R870", BLOCKER)
    ensure(RSTATUS, "R870", BLOCKER)
    ensure(RVERDICT, "第 870 轮", VERDICT)
    ensure(BACKLOG, "R870", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R870" not in h:
        h += ("\n## R870 补充 — 教训做成命令\n\n"
              "**`python tools\\where_is.py <名字>`**：按 **implementation / analysis / test / doc** 四组报位置，只看文件名与路径。\n"
              "**它第一次用就抓到自己没排除 `tools/.snapshots/`**（`StepActionRunner` 报 39 个文件，29 个是快照），已修 → 7 files。\n"
              "**`PopMart` → 31 files，analysis 组含 `PopMartStepMap.cs`(18)** —— **R835 若跑过就会直接看到，而那是 R849 才发现六轮没读的文件。**\n"
              "**已写进 `AGENTS.md §2.7c`**（五次踩坑表 + 两条配套：要包括**实现**；implementation 组有命中就先读再写）。\n"
              "**边界：不查镜像（那是 `analysis/ida.py str`），不判该不该有。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R870"), (RSTATUS, "R870"), (RVERDICT, "第 870 轮"), (BACKLOG, "R870")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R870: the lesson became a command, because writing it down five times was not a fix\n\n"
         "Across R843, R845, R846, R848 and R869 I wrote the same lesson five times: check whether it already exists"
         " before building it. Each time I then forgot again, and R869's cost was highest, because the reflection table"
         " I wrote met a binding failure that the existing StepActionRunner never meets.\n\n"
         "So the lesson is now tools/where_is.py. Given a name it reports every place it appears, grouped four ways by"
         " file name and path rather than by content: implementation, which is where behaviour is defined and what to"
         " read first; analysis, which catches StepMap, Steps, Path, Controllers, Endpoints and Witness files that have"
         " already worked something out; test, which pins what is guaranteed; and doc, which may already state the"
         " conclusion. Judging by file name keeps it reproducible and explainable, matching the rule that a third party"
         " can recompute any claim.\n\n"
         "The tool caught its own bug on first use. It did not exclude tools/.snapshots, the full copies snapshot.py"
         " takes before each mutation, so StepActionRunner appeared to live in thirty-nine files of which twenty-nine"
         " were history. After the fix it reports seven: three implementation, one test, three doc.\n\n"
         "The PopMart run is the argument for the tool. It reports thirty-one files with an analysis group containing"
         " PopMartStepMap.cs at eighteen occurrences -- the very file whose absence from my reading R849 discovered six"
         " rounds too late. Had I run this one line at R835, it would have been handed to me.\n\n"
         "The rule also went into AGENTS.md as section 2.7c, with the five-round table ahead of it and two companions:"
         " that checking for what exists must include implementations and not just analyses, which is what I got wrong"
         " the first four times, and that a name appearing in the implementation group means reading that file before"
         " deciding to write.\n\n"
         "Its boundaries are in the file header. It does not look at the image -- that is analysis/ida.py str -- because"
         " mixing the two produces false absences, which section 2.7b already documents four times. And it does not"
         " judge whether something ought to exist; it reports where things are and leaves the judgement.\n\n"
         "Unknown: the grouping depends on file names, so an analysis living in a generically named file would be"
         " grouped as implementation, and the answer there is to rename the file rather than add heuristics to the"
         " script; the tool has no test, on the grounds that a read-only reporter whose output a person reads may not"
         " repay an xunit wrapping a Python process; and the real risk is whether section 2.7c gets read at all, since"
         " R861 was four rounds wasted by not reading BINDING_BACKLOG.\n\n"
         "The lesson behind the lesson is that a lesson repeated five times is evidence that writing it down is not a"
         " fix. What works is a command that costs three minutes and does not depend on my memory, plus a section"
         " number that a later session can cite as a check. Neither is a new insight -- sections 2.7 and 2.7b have"
         " worked this way all along. I merely applied the repository's own method to myself.\n\n"
         "No C# changed; suite carries at 1773."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
