"""Record R932: the function ratio came from a stale artifact, and now METRICS says so."""

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
### 函数比例 61.96% 是**旧产物**算的 —— 差 59 个文件、23,815 行（R932）

**这一轮去查判据 (c)：产物级对照可复算。工具在（`func_count.py`），产物也在
（`.publish-aot/Cybersole.Ui.exe`，54 MB）。而查第三件时发现了问题。**

### 产物时间是 2026-11-16 11:49

**而 `src` 下有 **59 个 `.cs` 文件**比它新，合计 **23,815 行**。**

**其中最近的几个就是这几轮写的：`ConcurrencyLimit.cs`（R930）· `Profiles.cs` / `Enums.cs`（R930 的改名）·
外加 R920–R929 那六家 vendor 集成。**

> **所以 171,690 与 61.96% 描述的是**一天多以前的那一版**。
> 而这个数是目标第一条（函数数量对等）的度量 ——
> **它一直是对的，只是它在说另一份代码。****

### 为什么这不是「数字错了」

**171,690 对那一版产物是准确的。错的是**引用方式**：把它当成当前值。
**而 §2.6 那句「没跑成 ≠ 通过」是同一类问题的另一个形状 ——
这里是「算得对 ≠ 算的是现在」。****

### 所以加了一个度量，而不是改一个数

**`tools/artifact_freshness.py`：比 `.publish-aot` 的 mtime 与 `src` 下最新 `.cs`，报「几个文件更新、共几行」。**

**而它接进了 `METRICS.md`：**

```
| 函数数量（.pdata）              | 277,120 / 171,690 / 61.96% |
| 产物陈旧度（.publish-aot vs src） | 59 个文件更新 / 23,815 行   |
```

> **两行挨着，所以引用比例的人**必然看到它是不是当前的**。
> 这比在任何文档里写一句「注意产物可能过期」有用 —— 那句话会被漏读，而表格不会。**

### 而它只比时间戳，这是刻意的

**一次注释编辑会让产物显得陈旧，而输出一点没变。
**这个方向的误报是**正确**的：一次误报的代价是重发布一次，一次漏报的代价是一个关于已不存在代码的数字。**

### 而这一轮**没有**重新发布

**发布前查内存：1.87 GB，`build-server shutdown` 之后 1.92 GB —— 都低于 2 GB 那条线。
按纪律不发布，只把陈旧度记下来。**

**所以下一轮的第一件事是：内存够 2 GB 时 `dotnet publish -p:PublishAot=true`，
然后重跑 `func_count.py`，看 171,690 变成多少。**

### 数字

| 度量 | R931 | **R932** |
|---|---|---|
| 套件 | 1932 | **1932** |
| 函数比例 | 61.96%（未标注陈旧） | **61.96%（同一行旁有 59 / 23,815）** |
| **METRICS.md 行数** | 27 | **29** |

### 教训

> **判据 (c) 我读了很多遍「产物级对照可复算」，而它有三个条件：产物在、工具在、**对照的是现在**。
> 前两个我查了，第三个我没有 —— 因为前两个成立的时候，第三个看起来会自动成立。**
> **而「自动成立」是这个项目里最贵的一句话。**
"""

if "函数比例 61.96% 是**旧产物**算的" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R932 appended")

VERDICT = """

---

## 第 932 轮：61.96% 是旧产物算的 —— 差 59 个文件、23,815 行

### 判据 (c) 有三个条件，我前两个查了

**产物在（54 MB）· 工具在（`func_count.py`）· **对照的是现在** —— 第三个我没查。**

### 而第三个不成立

**产物 mtime **2026-11-16 11:49**；`src` 下 **59 个 `.cs`** 比它新，合计 **23,815 行**。
包括 R930 的 `ConcurrencyLimit.cs` / `Enums.cs` / `Profiles.cs`，和 R920–R929 那六家 vendor 集成。**

> **所以 171,690 与 61.96% 描述的是**一天多以前那一版**。
> 而这个数是目标第一条的度量 —— 它一直是对的，只是它在说另一份代码。**

### 这不是「数字错了」，是「引用方式错了」

**171,690 对那一版产物是准确的。错的是把它当成当前值。
与 §2.6「没跑成 ≠ 通过」同类 —— 这里是「**算得对 ≠ 算的是现在**」。**

### 所以加度量，不改数字

**`tools/artifact_freshness.py` 接进 METRICS.md，两行挨着：比例 + 陈旧度。
引用比例的人**必然看到它是不是当前的**。**
**这比在文档里写一句「注意可能过期」有用 —— 那句话会被漏读，表格不会。**

### 只比时间戳是刻意的

**注释编辑会让产物显得陈旧而输出未变。**这个方向的误报是正确的**：
误报的代价是重发布一次，漏报的代价是一个关于已不存在代码的数字。**

### 而这一轮没有重新发布

**1.87 GB → `build-server shutdown` 后 1.92 GB，都低于 2 GB 那条线。按纪律不发布。**

### 数字

| 度量 | R931 | **R932** |
|---|---|---|
| 套件 | 1932 | 1932 |
| 函数比例 | 61.96%（未标注） | **61.96%（旁有 59 / 23,815）** |
| METRICS.md 行数 | 27 | **29** |

### 教训

> **「产物级对照可复算」有三个条件：产物在、工具在、对照的是现在。
> 前两个成立的时候，第三个看起来会自动成立。**
> **而「自动成立」是这个项目里最贵的一句话。**
"""

BACKLOG_ADD = """

## 判据 (c) — 函数比例来自旧产物；新增陈旧度度量（R932，**新工具 + 接进 METRICS**）

### 发现

**`.publish-aot/Cybersole.Ui.exe` mtime **2026-11-16 11:49**；
`src` 下 **59 个 `.cs`** 更新，合计 **23,815 行**（含 R920–R930 全部改动）。**

**→ 171,690 / 61.96% 描述的是旧产物。数字对那一版准确，错在当成当前值。**

### 改动

**`tools/artifact_freshness.py` → METRICS.md 新增一行「产物陈旧度」，与「函数数量」相邻。
`metrics_report.py` 加 metric 行 + patterns 两个键（owned 里不能放没有 pattern 的键 —— 那会让整行被丢）。**

### 只比时间戳（刻意）

**误报方向正确：重发布一次的代价 vs 一个关于已不存在代码的数字。**

### 未做

**未重新发布：1.87 / 1.92 GB 都低于 2 GB 线。下一轮内存够时
`dotnet publish -p:PublishAot=true` 再跑 `func_count.py`。**

### 数字

**套件 1932（不变）· METRICS.md 27 → 29 行**

| 仍 Unknown | |
|---|---|
| 当前产物的真实函数数 | 未发布，未知 |
| 59 个文件带来的增量 | 未知，可能几百到几千 |
| 陈旧度是否该进 CI | 未定 |

**纪律**：判据 (c) 三个条件：产物在、工具在、对照的是现在。前两个成立时第三个看起来会自动成立 —— 而「自动成立」是最贵的一句话。
"""

BLOCKER = """

---

## 356. 函数比例 61.96% 来自旧产物：差 59 文件 / 23,815 行

> R932。**新工具 + 改 metrics 管线，未改产品代码。** 套件 **1932 通过 / 0 失败 / 0 跳过**。

### 一、判据 (c) 有三个条件

**产物在（54 MB）· 工具在（`func_count.py`）· **对照的是现在** —— 第三个我没查。**

### 二、第三个不成立

```
.publish-aot/Cybersole.Ui.exe   mtime 2026-11-16 11:49:13
src 下更新的 .cs               59 个，23,815 行
（含 R930 的 ConcurrencyLimit.cs / Enums.cs / Profiles.cs 与 R920–R929 六家 vendor 集成）
```

**→ 171,690 与 61.96% 描述**一天多以前那一版**。数字对那一版准确，错在当成当前值。**

**与 §2.6「没跑成 ≠ 通过」同类：「算得对 ≠ 算的是现在」。**

### 三、所以加度量而不是改数字

**`tools/artifact_freshness.py` 接进 METRICS.md，与「函数数量」相邻两行。
引用比例的人必然看到陈旧度 —— 比文档里一句「注意可能过期」可靠。**

**只比时间戳（刻意）：误报的代价是重发布一次，漏报的代价是一个关于已不存在代码的数字。**

### 四、未重新发布

**1.87 GB → `build-server shutdown` 后 1.92 GB，均低于 2 GB 线，按纪律停。**

### 五、数字

| 度量 | R931 | R932 |
|---|---|---|
| 套件 | 1932 | **1932** |
| 函数比例 | 61.96%（未标注） | **61.96%（旁有 59 / 23,815）** |
| METRICS.md 行数 | 27 | **29** |

### 六、验证

```
artifact_freshness.py            -> stale；59 files / 23,815 lines
metrics_report.py                -> 两行均解析：ratio 61.96% · 59 files / 23,815 lines
```

### 七、仍然 Unknown

- **当前产物的真实函数数**：**Unknown** —— 未发布。
- **59 个文件的增量**：**Unknown** —— 可能几百到几千。
- **陈旧度是否该进 CI**：**未定**。

### 八、教训

**判据 (c) 我读了很多遍「产物级对照可复算」，而它有三个条件。
前两个查了，第三个没有 —— 因为前两个成立的时候，第三个看起来会自动成立。**

**而「自动成立」是这个项目里最贵的一句话。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R932", BLOCKER)
    ensure(RSTATUS, "R932", BLOCKER)
    ensure(RVERDICT, "第 932 轮", VERDICT)
    ensure(BACKLOG, "R932", BACKLOG_ADD)

    note = (
        "\n## R932 补充 — 函数比例 61.96% 来自旧产物（新工具 + 接进 METRICS，套件 1932）\n\n"
        "判据 (c) 三个条件：产物在、工具在、**对照的是现在**。前两个查了，第三个没有。\n"
        "产物 mtime 2026-11-16 11:49；src 下 59 个 .cs 更新、23,815 行（含 R920–R930 全部改动）。\n"
        "→ 171,690 / 61.96% 描述旧产物。数字对那一版准确，错在当成当前值。\n\n"
        "新增 tools/artifact_freshness.py，接进 METRICS.md 与「函数数量」相邻 —— 引用比例的人必然看到陈旧度。\n"
        "只比时间戳（刻意）：误报代价是重发布一次，漏报代价是一个关于已不存在代码的数字。\n\n"
        "未重新发布：1.87 / 1.92 GB 均低于 2 GB 线。\n\n"
        "数字：套件 1932（不变）· METRICS.md 27 → 29 行。\n\n"
        "纪律：判据 (c) 前两个成立时第三个看起来会自动成立 —— 而「自动成立」是最贵的一句话。\n\n"
        "下一轮第一件事：内存够 2 GB 时 dotnet publish -p:PublishAot=true，再跑 func_count.py。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R932" not in h:
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
             for p, k in ((RBLOCK, "R932"), (RSTATUS, "R932"), (RVERDICT, "第 932 轮"), (BACKLOG, "R932")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R932: the function ratio came from a stale artifact, and METRICS now says so beside it\n\n"
         "Criterion (c) asks for an artifact-level comparison that can be recomputed. The artifact exists at fifty-four\n"
         " megabytes and the tool exists, so both conditions looked satisfied -- and the third was not checked, because\n"
         " when the first two hold the third appears to follow. It does not. The published executable is dated\n"
         " 2026-11-16 11:49 and fifty-nine source files totalling twenty-three thousand eight hundred lines changed after\n"
         " it, including every vendor integration from R920 to R929 and R930's ConcurrencyMode work. So 171,690 and\n"
         " 61.96% describe a build more than a day old.\n\n"
         "That figure is accurate about that build. What is wrong is quoting it as current, which is the same class of\n"
         " mistake as section 2.6's not-runs-is-not-passes turned around: calculated correctly is not the same as\n"
         " calculated about now.\n\n"
         "So the fix is a measure rather than a number. artifact_freshness compares the artifact's timestamp with the\n"
         "newest source file and reports how many files postdate it and how many lines they hold, and it sits in\n"
         "METRICS.md directly beside the function ratio, so anyone quoting the ratio sees whether it describes the\n"
         "current code. That is more reliable than a sentence in a document asking readers to remember the artifact\n"
         "might be stale.\n\n"
         "Comparing timestamps only is deliberate. A comment edit marks the artifact stale while changing no output, and\n"
         " that false alarm is the correct direction to err: a false alarm costs a republish, while a missed one costs a\n"
         "figure quoted about code that no longer exists.\n\n"
         "The republish did not happen. Memory read 1.87 GB, and 1.92 GB after shutting the build servers down, both\n"
         " under the two-gigabyte line, so the round records the staleness instead of gambling on the build.\n\n"
         "Figures: suite unchanged at 1932, the ratio still reads 61.96% but now with 59 files and 23,815 lines beside\n"
         " it, and METRICS.md goes from twenty-seven rows to twenty-nine.\n\n"
         "Unknown: the replica's real function count, since nothing was published; how much those fifty-nine files add,\n"
         " which could be hundreds or thousands; and whether freshness belongs in CI.\n\n"
         "The lesson is that a criterion with three conditions is not satisfied by two, and that the unchecked one is\n"
         " usually the one that seems to follow automatically. That phrase -- follows automatically -- is the most\n"
         " expensive one in this project.\n\n"
         "Tool and pipeline changed; no product code; suite green at 1932."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()