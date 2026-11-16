"""Record R888: the shape metric was dominated by deferred work, so it now reports the core figure too."""

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
### 「形状 94」里 **77 条是 UI** —— 而这个指标一直在把我推向优先级 ④（R888）

**R887 把 94 条归了族，但没问**它们属于哪个优先级**。**

**按声明类型所在的 csproj 分组：**

| 项目 | 条数 |
|---|---|
| **`Cybersole.Ui`** | **77** |
| `Cybersole.Core` | 12 |
| `Cybersole.Services` | 5 |
| **`Cybersole.Stores`** | **0** |

**YG 的优先级是 ① checkout flow → ② 风控 → ③ 请求指纹层 → ④ **其余（含 UI）**。
所以这 94 条的 **82%** 落在被明令缓的那一档里，而优先级 ①（`Cybersole.Stores`）是**零缺口**。**

**也就是说：R881–R887 这几轮我在提高一个指标的分辨率，而它的主项不在目标上。**

### 改了什么

```
shape_audit.py     + 按项目分组输出
                   + core mismatches: 17        ← Stores + Services + Http + Core
metrics_report.py  + 取 core mismatches
                   + patterns 白名单加一条

METRICS.md L23  成员形状差异 — total mismatches |  94
METRICS.md L24  成员形状差异 — core mismatches  |  17
```

**现在「差多少」和「差在哪一档」是两个并列的数。**

### 而这个 17 本身也值得看

| 类型 | 项目 | 缺的成员 |
|---|---|---|
| `BotTask` | Core | **`Running` · `Task`** |
| `Checkout` | Core | `Profile` |
| `CreateModel` | Core | `Inputs` |
| `Notification` | Core | `Timestamp` · `Title` |
| `IWebhook` | Core | `Events` · `ExtraFields` · `Name` · `Url`（全是 `prop-get`） |

**`BotTask.Running` 与 `BotTask.Task` 是其中两个，而 `Task` 就是 R364 那个悬案。**

**所以核心那 17 条不是零散的 —— 最大的一族是 `BotTask`，而它是任务模型的中心。**

### 一处实现错，值得记

**第一版按 `_dp.split(os.sep)[1]` 取项目名，而 `ROOT` 是绝对路径，所以 `_parts[1]` 是 `projects`。
输出成了 `projects 94` 一行。改成「取 `src` 之后那一段」才对。**

**而一个只输出 `projects 94` 的分组表**看起来像在工作**（有分组、有数字），
**只是每一行都是同一个错名字 —— 与 R876 那次「相邻当归属」同族：形状对，内容错。**
"""

if "「形状 94」里 **77 条是 UI**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R888 appended")

BLOCKER = """

---

## 312. 「形状 94」里 77 条是 UI；核心项目 **17** 条

> R888。**改工具链两处 + METRICS 增一行。** 套件 **1780 通过 / 0 失败 / 0 跳过**。

### 一、按优先级分组的 94 条

| 项目 | 条数 | 优先级 |
|---|---|---|
| **`Cybersole.Ui`** | **77** | **④（YG 明令缓）** |
| `Cybersole.Core` | 12 | ④ 但偏底 |
| `Cybersole.Services` | 5 | ② 相邻 |
| **`Cybersole.Stores`** | **0** | **① 零缺口** |

**YG 的次序是 ① checkout flow → ② 风控 → ③ 请求指纹 → ④ 其余（含 UI）。
所以 94 条的 82% 在被缓的那一档，而 ① 是零缺口。**

**→ R881–R887 这几轮我在提高一个指标的分辨率，而它的主项不在目标上。**

### 二、改了什么

```
shape_audit.py     + 按项目分组
                   + core mismatches: 17
metrics_report.py  + 取 core mismatches（patterns 白名单加一条）
METRICS.md L23    总 94
METRICS.md L24    核心 17
```

**「差多少」与「差在哪一档」现在是两个并列的数。**

### 三、核心那 17 条

| 类型 | 缺的成员 |
|---|---|
| **`BotTask`** | **`Running` · `Task`** |
| `Checkout` | `Profile` |
| `CreateModel` | `Inputs` |
| `Notification` | `Timestamp` · `Title` |
| `IWebhook` | `Events` · `ExtraFields` · `Name` · `Url` |

**最大一族是 `BotTask`，而它是任务模型的中心 —— 而 `Task` 就是 R364 那个悬案。**

### 四、一处实现错

**第一版用 `_dp.split(os.sep)[1]` 取项目名，而 `ROOT` 是绝对路径 → `_parts[1]` 是 `projects`，
输出成了 `projects 94` 一行。**

**而它**看起来像在工作** —— 有分组、有数字，只是每行同一个错名字。
**与 R876「相邻当归属」同族：形状对，内容错。****

**修法是取 `src` 之后那一段。**

### 五、验证

```
shape_audit.py --baseline -> total 94 · by owning project: Ui 77 / Core 12 / Services 5 · core mismatches 17
metrics_report.py         -> {'total mismatches': '94', 'core mismatches': '17'}
docs/METRICS.md L23/L24   -> 94 / 17
完整套件                   -> 1780 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **核心那 17 条该不该现在做**：**Unknown，而这是本轮之后最该判的。**
  **它们是 Core/Services 里的属性形状差异，不是 Stores 的 —— 所以仍然不在优先级 ① 的正中心。**
- **`BotTask.Running` 与 `BotTask.Task` 是什么类型**：**Unknown** ——
  **证据只说它们是 `Getter,Property,Setter`（可写属性），类型本身没有。**
- **`Cybersole.Http` 在分组里没出现**：**Observation** —— 说明那 94 条里没有一条命中 Http 的类型，
  **而优先级 ③ 正是请求层。**

### 七、教训

**R887 我说「报数字说差多少，报结构说差在哪」。这一轮发现还缺第三个轴：**差在哪一档**。**

**而那个轴最要紧 —— 因为 YG 给过次序，而我的指标把 82% 的注意力指向了被缓的那一档。**

**一个指标不需要错才会误导；它只需要**没有按目标分解**。**
"""

VERDICT = """

---

## 第 888 轮：「形状 94」里 77 条是 UI —— 指标一直把我推向优先级 ④

### 按优先级分组

| 项目 | 条数 | 优先级 |
|---|---|---|
| **`Cybersole.Ui`** | **77** | **④（YG 明令缓）** |
| `Cybersole.Core` | 12 | ④ 但偏底 |
| `Cybersole.Services` | 5 | ② 相邻 |
| **`Cybersole.Stores`** | **0** | **① 零缺口** |

> **94 条的 82% 在被缓的那一档，而 ① 是零缺口。
> → R881–R887 这几轮我在提高一个指标的分辨率，而它的主项不在目标上。**

### 改了什么

```
shape_audit.py     + 按项目分组 + core mismatches: 17
metrics_report.py  + 取 core mismatches（patterns 白名单加一条）
METRICS.md L23     总 94
METRICS.md L24     核心 17
```

### 核心那 17 条

| 类型 | 缺的成员 |
|---|---|
| **`BotTask`** | **`Running` · `Task`** |
| `Checkout` | `Profile` |
| `CreateModel` | `Inputs` |
| `Notification` | `Timestamp` · `Title` |
| `IWebhook` | `Events` · `ExtraFields` · `Name` · `Url` |

**最大一族是 `BotTask`，而它是任务模型的中心 —— `Task` 就是 R364 那个悬案。**

### 一处实现错

**第一版用绝对路径的 `_parts[1]` 取项目名 → 输出 `projects 94` 一行。**

> **而它**看起来像在工作** —— 有分组、有数字，只是每行同一个错名字。与 R876「相邻当归属」同族：形状对，内容错。**

### 仍然 Unknown

**核心那 17 条该不该现在做**（**最该判：它们不是 Stores 的，仍不在 ① 正中心**）·
**`BotTask.Running`/`Task` 是什么类型**（只说可写属性）·
**`Cybersole.Http` 没出现**（**说明 94 条没一条命中请求层 —— 而 ③ 正是请求层**）

### 教训

> **R887 说「报数字说差多少，报结构说差在哪」。这一轮发现还缺第三个轴：**差在哪一档**。**
> **而那个轴最要紧 —— 因为 YG 给过次序，而我的指标把 82% 的注意力指向了被缓的那一档。**
> **一个指标不需要错才会误导；它只需要**没有按目标分解**。**
"""

BACKLOG_ADD = """

## 判据 — 「形状 94」里 77 条是 UI；核心 **17**（R888，**改工具链两处**）

### 按优先级分组

| 项目 | 条数 | 优先级 |
|---|---|---|
| **`Cybersole.Ui`** | **77** | **④（缓）** |
| `Cybersole.Core` | 12 | ④ 偏底 |
| `Cybersole.Services` | 5 | ② 相邻 |
| **`Cybersole.Stores`** | **0** | **① 零缺口** |

**→ 94 的 82% 在被缓的那一档。R881–R887 在提高一个主项不在目标上的指标的分辨率。**

### 改动

`shape_audit.py` 加按项目分组 + `core mismatches: 17`；`metrics_report.py` 加 pattern；
**`METRICS.md` L23 总 94 / L24 核心 17。**

### 核心 17 条

**`BotTask`（`Running` · `Task`）· `Checkout`（`Profile`）· `CreateModel`（`Inputs`）·
`Notification`（`Timestamp` · `Title`）· `IWebhook`（`Events` · `ExtraFields` · `Name` · `Url`）**

**最大一族 `BotTask` = 任务模型中心；`Task` 即 R364 悬案。**

### 实现错一处

**绝对路径下 `_parts[1]` = `projects` → 输出 `projects 94`。**看起来像在工作**（有分组有数字），只是每行同一错名。**

| 仍 Unknown | |
|---|---|
| **核心 17 条该不该现在做** | **最该判：不是 Stores 的，仍不在 ① 正中心** |
| `BotTask.Running`/`Task` 的类型 | 只知是可写属性 |
| `Cybersole.Http` 未出现 | **94 条没一条命中请求层，而 ③ 正是请求层** |

**纪律**：**指标不需要错才会误导 —— 只需要**没有按目标分解**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R888", BLOCKER)
    ensure(RSTATUS, "R888", BLOCKER)
    ensure(RVERDICT, "第 888 轮", VERDICT)
    ensure(BACKLOG, "R888", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R888" not in h:
        h += ("\n## R888 补充 — 「形状 94」里 **77 条是 UI**；核心 **17**（**改工具链两处**）\n\n"
              "**按项目分组**：`Ui` 77（**优先级 ④，YG 明令缓**）· `Core` 12 · `Services` 5 · **`Stores` 0（① 零缺口）**。"
              "**→ 94 的 82% 在被缓的那一档；R881–R887 在提高一个主项不在目标上的指标的分辨率。**\n"
              "**改动**：`shape_audit.py` 加按项目分组 + `core mismatches: 17`；`metrics_report.py` 加 pattern；**METRICS L23 总 94 / L24 核心 17**。\n"
              "**核心 17 条**：`BotTask`(`Running`·`Task`) · `Checkout`(`Profile`) · `CreateModel`(`Inputs`) · `Notification`(`Timestamp`·`Title`) · `IWebhook`(4 个)。**最大一族 `BotTask` = 任务模型中心。**\n"
              "**`Cybersole.Http` 未出现 → 94 条没一条命中请求层，而 ③ 正是请求层。**\n"
              "**纪律：指标不需要错才会误导 —— 只需要没有按目标分解。**\n")
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
             for p, k in ((RBLOCK, "R888"), (RSTATUS, "R888"), (RVERDICT, "第 888 轮"), (BACKLOG, "R888")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R888: seventy-seven of the ninety-four shape gaps are UI, so the metric now reports the core figure\n\n"
         "R887 classified the gaps by kind and by member name but never asked which priority band they fall in. Grouped\n"
         " by the project that declares each type, seventy-seven belong to Cybersole.Ui, twelve to Core, five to\n"
         " Services, and none to Stores.\n\n"
         "The ordering in force is checkout flows first, then anti-bot, then the request and fingerprint layer, then\n"
         " everything else including the UI. So eighty-two percent of this metric sits in the band that was explicitly\n"
         " deferred, and priority one carries none of it. Rounds R881 through R887 went into sharpening a figure whose\n"
         " dominant term is out of scope -- correcting its source, restoring a dropped field, and decomposing it by\n"
         " member, all of which improved a number pointed the wrong way.\n\n"
         "So the audit now splits its rows by owning project and prints a core figure alongside the total, and the\n"
         " metrics runner picks both up: ninety-four overall, seventeen across Stores, Services, Http and Core.\n"
         " Two numbers side by side, one saying how much is wrong and the other saying how much of it matters.\n\n"
         "The seventeen are worth reading rather than counting. BotTask contributes Running and Task, and Task is the\n"
         " member whose type has been unknown since R364; Checkout contributes Profile; CreateModel contributes Inputs;\n"
         " Notification contributes Timestamp and Title; and IWebhook contributes Events, ExtraFields, Name and Url.\n"
         " The largest family is BotTask, which is the centre of the task model.\n\n"
         "One implementation error is worth recording because of its shape. The first version took the project name as\n"
         " the second path segment, and since ROOT is absolute that segment is 'projects', so the table printed a\n"
         " single row reading 'projects 94'. It looked like it worked -- there was a heading, there were counts -- and\n"
         " every row carried the same wrong name. That is the same family as R876 reading adjacency as ownership:\n"
         " correct shape, wrong content.\n\n"
         "Unknown: whether the core seventeen should be done now, which is the judgement to make, since they sit in\n"
         " Core and Services rather than Stores and so are still off the centre of priority one; what types BotTask's\n"
         " Running and Task have, where the evidence establishes only that they are settable properties; and why\n"
         " Cybersole.Http appears nowhere in the ninety-four, which suggests no gap touches the request layer -- the\n"
         " very thing priority three is about.\n\n"
         "The lesson is that a metric needs a third axis beyond magnitude and structure: which band. R887 said a number\n"
         " says how much while structure says where; this round adds that without the band, a correct metric can still\n"
         " aim attention at deferred work. It does not have to be wrong to mislead -- only undecomposed against the\n"
         " goal.\n\n"
         "Tool chain changed; no product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
