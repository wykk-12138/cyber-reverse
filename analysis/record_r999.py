"""Record R999: the summary table now says which of its numbers have aged."""

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
### `METRICS.md` 的摘要表现在会说**哪些数老了**（R999）

**这一轮本来要去 publish 刷新函数数。1.8 GB 可用 —— 按纪律不 publish（AOT 是内存最重的操作）。
而在查「能不能 publish」的过程中发现了一件更要紧的事。**

### ① 摘要区把两个**过期的数**排成了当前值

```
| 函数数量（.pdata） — functions: replica .pdata | 173,952 |
| 函数数量（.pdata） — functions: ratio | 62.77% |
| 产物陈旧度（.publish-aot vs src） — source files newer than the artifact | 15 |
| 产物陈旧度（.publish-aot vs src） — lines in those files | 10753 |
| 变异套件（上次运行） — mutation-fit: staleness | 1:31:27 -- StoreFlow.cs changed after the run |
```

> **`173,952` 就在 `15 个源文件更新` 的**正上方**，中间只隔两行 —— 而那两行说它来自一次更旧的构建。
> 而 `artifact_freshness.py` 自己的注释早就写着这件事
> （「While it is stale that ratio describes an older build, so it **must be labelled as such wherever it is quoted**」），
> 而摘要区没有做。**
> **→ 而 `mutation-fit: staleness` 那一行写着 `1:31:27 -- StoreFlow.cs changed` —— 变异记录也过期了。**
> **→ 两个过期的数和一个当前套件数在同一列里，没有任何区分。**

### ② 而这两个是同一个问题：**摘要区没有时效这一维**

**每一个数都是「上次量到的」，而其中两个的**上次**已经不代表现在。
一个读这张表的人要靠**已经知道**哪个会过期，才能不错。**

### ③ 所以修的是**生成器**，不是数据

**`metrics_report.py` 在摘要表**之前**加一个自动生成的块：**

```
## 时效警告（生成）

> **函数数量那一行来自一个陈旧的 `.publish-aot`**：有 15 个源文件比产物新（共 10753 行）。
  它描述的是更旧的一次构建，不是当前源码。
```

**规则两条，都从工具输出里读，不是硬编码：**
- `source files newer than the artifact` ≠ 0 → 函数数那一行是陈旧的
- 某个 `staleness` 字段不以 `0` 开头 → 那一组数来自过期运行

### ④ 而顺手把变异重跑了（不耗内存，与 publish 不同）

```
running 36 of 36
fired 36 · decorative 0 · skipped 0 · restored GREEN
ran_at 2026-11-17T14:06:23+08:00
```

**→ 重跑之后，警告块从**两条**降到**一条** —— 因为变异那条 freshly 变成了 `0`。**

> **这正好证明那个块不是装饰：它跟着数据走。
> 一条警告消失，是因为被它警告的那件事**真的被做了**。**

### ⑤ 而剩下的那一条**修不了**，而它现在**说出来了**

**1.8 GB 可用 → AOT publish 会在这个内存下失败或拖垮机器（纪律：< 2GB 只跑 `-m:1`）。
所以函数数仍是 `173,952`，仍来自一个 15 个源文件之前的产物。**

> **而这一轮的产出不是让它变 fresh，是让它**不再沉默**。
> 一个不能修的缺口，至少不能被当成当前值读。**

### 数字

| 度量 | R998 | **R999** |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **15 / 10,753（未变，不能 publish）** |
| **变异陈旧度** | 1:31:27 | **0（已重跑）** |
| 变异 fired / 总 | 36 / 36 | **36 / 36（新记录 14:06:23）** |
| 函数数 | 173,952 | **173,952（陈旧，且现在被标注）** |
| **METRICS 摘要的时效警告** | 无这一维 | **1 条（生成）** |

### 教训

> **「所有文档引用 METRICS.md」这个规矩建立时，假设的是**表里的数都是当前的**。
> 而其中两个不是，规矩就把一个过期的数**提成了权威**。**
> **→ 一个单一数字源的价值取决于它说清每个数的**时效**，而不取决于它集中。
> 集中只是让它更容易被当成都对。**
"""

if "摘要表现在会说**哪些数老了**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 999 轮：`METRICS.md` 的摘要表现在会说哪些数老了

### ① 本来要去 publish，1.8 GB 挡住了 —— 而查到更要紧的事

**按纪律 < 2GB 不跑 AOT publish。而查的过程中发现：**

```
| 函数数量 — functions: replica .pdata | 173,952 |
| 函数数量 — functions: ratio | 62.77% |
| 产物陈旧度 — source files newer than the artifact | 15 |
| 产物陈旧度 — lines in those files | 10753 |
| 变异套件 — mutation-fit: staleness | 1:31:27 -- StoreFlow.cs changed after the run |
```

> **`173,952` 就在「15 个源文件更新」正上方，中间只隔两行。
> 而 `artifact_freshness.py` 的注释早写着
> 「must be labelled as such wherever it is quoted」—— 摘要区没做。
> 而变异记录也过期了 1.5 小时。**

### ② 这是同一个问题：摘要区没有**时效**这一维

**每个数都是「上次量到的」，而其中两个的「上次」不代表现在。
读表的人要靠**已经知道**哪个会过期，才能不错。**

### ③ 修生成器，不修数据

```
## 时效警告（生成）

> **函数数量那一行来自一个陈旧的 `.publish-aot`**：有 15 个源文件比产物新（共 10753 行）。
  它描述的是更旧的一次构建，不是当前源码。
```

**两条规则都从工具输出读，不硬编码：`source files newer` ≠ 0；某 `staleness` 不以 `0` 开头。**

### ④ 顺手重跑变异（不耗内存），警告从**两条降到一条**

```
running 36 of 36 · fired 36 · decorative 0 · skipped 0 · restored GREEN
ran_at 2026-11-17T14:06:23+08:00
```

> **一条警告消失，是因为被它警告的那件事**真的被做了** —— 那块不是装饰。**

### ⑤ 剩下那条**修不了**，但它现在**说出来了**

**1.8 GB 下 AOT publish 会失败或拖垮机器。所以函数数仍是 173,952，仍来自 15 个源文件之前的产物。
这一轮的产出不是让它变 fresh，是让它**不再沉默**。**

### 数字

| 度量 | R998 | **R999** |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **未变（不能 publish）** |
| **变异陈旧度** | 1:31:27 | **0（已重跑）** |
| 变异 fired / 总 | 36 / 36 | **36 / 36（新记录）** |
| 函数数 | 173,952 | **173,952（陈旧，且现在被标注）** |
| **摘要时效警告** | 无这一维 | **1 条（生成）** |

### 教训

> **「所有文档引用 METRICS.md」这个规矩建立时，假设表里的数都是当前的。
> 而其中两个不是，规矩就把一个过期的数**提成了权威**。
> → 单一数字源的价值取决于它说清每个数的**时效**，不取决于它集中。
> 集中只是让它更容易被当成都对。**
"""

BACKLOG_ADD = """

## 判据 (c)/(e) — **METRICS 摘要加「时效警告（生成）」：函数数来自陈旧产物、变异记录已重跑**（R999）

### 缺陷

**摘要表把 `173,952 / 62.77%` 排在 `15 个源文件更新` 的正上方而无标注；
`mutation-fit: staleness` 写着 `1:31:27`。两个过期的数与一个当前套件数同列。

`artifact_freshness.py` 自己的注释要求「must be labelled as such wherever it is quoted」，摘要区没做。**

### 修

**`metrics_report.py` 在摘要表前生成「时效警告」块，两条规则都从工具输出读：
`source files newer` ≠ 0 → 函数数陈旧；某 `staleness` 不以 `0` 开头 → 那组数过期。**

### 结果

**重跑变异后（36/36 fired · 0 decorative · 0 skipped · ran 14:06:23），警告从 2 条降到 1 条。
剩下那条是产物 —— 1.8 GB 下不能 publish，所以它**修不了，但不再沉默**。**

### 数字

**套件 2210 · 产物陈旧度 15 / 10,753（未变）· 变异陈旧度 0 · 变异 36/36 · 摘要警告 1 条**

| 仍 Unknown | |
|---|---|
| 今天的函数数是多少 | **Unknown** —— 需 publish，而内存不够 |

**纪律**：集中只让过期更容易被当成当前。
"""

BLOCKER = """

---

## 423. **METRICS 摘要加「时效警告（生成）」；变异已重跑（36/36）；产物仍陈旧且不能 publish**

> R999。**改 `metrics_report.py` 一处 + 重跑变异。** 套件 **2210 通过 / 0 失败 / 0 跳过**。

### 一、本来要去 publish，1.8 GB 挡住了

**`Get-CimInstance Win32_OperatingSystem` → FreePhysicalMemory 1.8 GB。
按纪律（< 2GB 只跑 `-m:1`）**不做 AOT publish**。查的过程中发现更要紧的事。**

### 二、摘要区把两个过期的数排成当前值

```
| 函数数量（.pdata） — functions: replica .pdata | 173,952 |
| 函数数量（.pdata） — functions: ratio | 62.77% |
| 产物陈旧度 — source files newer than the artifact | 15 |
| 产物陈旧度 — lines in those files | 10753 |
| 变异套件（上次运行） — mutation-fit: staleness | 1:31:27 -- StoreFlow.cs changed after the run |
```

**→ `173,952` 就在「15 个源文件更新」正上方，中间只隔两行。
→ 而 `artifact_freshness.py` 的注释早写着
「While it is stale that ratio describes an older build, so it **must be labelled as such wherever it is quoted**」——
摘要区没有做。
→ 而 `mutation-fit: staleness` 写着 `1:31:27 -- StoreFlow.cs changed` —— 变异记录也过期了。
→ **两个过期的数和一个当前套件数在同一列里，没有任何区分。****

### 三、所以修的是生成器

**`metrics_report.py` 在摘要表**之前**加一个自动生成的块，两条规则都从工具输出读：**

```
## 时效警告（生成）

> **函数数量那一行来自一个陈旧的 `.publish-aot`**：有 15 个源文件比产物新（共 10753 行）。
  它描述的是更旧的一次构建，不是当前源码。
```

- `source files newer than the artifact` ≠ 0 → 函数数那一行是陈旧的
- 某个 `staleness` 字段不以 `0` 开头 → 那一组数来自过期运行

### 四、而顺手把变异重跑了（不耗内存）

```
running 36 of 36
fired 36 · decorative 0 · skipped 0 · restored GREEN
ran_at 2026-11-17T14:06:23+08:00
```

**→ 重跑之后，警告块从**两条**降到**一条** —— 因为变异那条真的变成了 `0`。
→ **这证明那个块不是装饰：它跟着数据走。一条警告消失，是因为被它警告的那件事真的被做了。**

### 五、而剩下的那一条**修不了**

**1.8 GB 可用 → AOT publish 会在这个内存下失败或拖垮机器。
所以函数数仍是 `173,952`，仍来自一个 15 个源文件之前的产物。**

**→ 这一轮的产出不是让它变 fresh，是让它**不再沉默**。
→ 一个不能修的缺口，至少不能被当成当前值读。**

### 六、数字

| 度量 | R998 | R999 |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **15 / 10,753（未变，不能 publish）** |
| **变异陈旧度** | 1:31:27 | **0（已重跑）** |
| 变异 fired / 总 | 36 / 36 | **36 / 36（新记录 14:06:23）** |
| 函数数 | 173,952 | **173,952（陈旧，且现在被标注）** |
| **METRICS 摘要的时效警告** | 无这一维 | **1 条（生成）** |

### 七、验证

```
cd replica
python tools/mutation-check.py        -> 36 of 36；fired 36 / decorative 0 / skipped 0；GREEN；wrote MUTATION_RESULT.json
python tools/metrics_report.py        -> 完整套件 exit 0  2210 通过 / 0 失败 / 0 跳过
python - 读 ../docs/METRICS.md 找「## 时效警告（生成）」
  -> 一条：函数数量那一行来自一个陈旧的 .publish-aot（15 个源文件 / 10753 行）
```

### 八、仍然 Unknown

- **今天的函数数是多少**：**Unknown** —— 需要 publish，而当前内存不够（1.8 GB < 2 GB）。

### 九、教训

**「所有文档引用 METRICS.md」这个规矩建立时，假设的是**表里的数都是当前的**。
而其中两个不是，规矩就把一个过期的数**提成了权威**。**

**→ 一个单一数字源的价值取决于它说清每个数的**时效**，而不取决于它集中。
集中只是让它更容易被当成都对。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R999", BLOCKER)
    ensure(RSTATUS, "R999", BLOCKER)
    ensure(RVERDICT, "第 999 轮", VERDICT)
    ensure(BACKLOG, "R999", BACKLOG_ADD)

    note = (
        "\n## R999 补充 — **METRICS 摘要加「时效警告（生成）」；变异重跑 36/36；产物仍陈旧且不能 publish**（套件 2210）\n\n"
        "本来要去 publish 刷新函数数，**1.8 GB 可用 → 按纪律不做 AOT publish**。查的过程中发现更要紧的事：\n"
        "摘要表把 `173,952 / 62.77%` 排在 `15 个源文件更新` 的正上方而**无标注**，\n"
        "而 `mutation-fit: staleness` 写着 `1:31:27` —— **两个过期的数与一个当前套件数同列。**\n"
        "（`artifact_freshness.py` 自己的注释要求「must be labelled as such wherever it is quoted」，摘要区没做。）\n\n"
        "**修生成器**：`metrics_report.py` 在摘要表前生成「时效警告」块，规则从工具输出读（不硬编码）。\n"
        "**并重跑变异**（不耗内存）：**36/36 fired · 0 decorative · 0 skipped · GREEN · ran 14:06:23**。\n"
        "→ 警告从 **2 条降到 1 条** —— 一条消失是因为被警告的那件事**真的被做了**。\n\n"
        "剩下那条是产物：**修不了（内存不够），但它现在说出来了**。\n\n"
        "数字：套件 2210 · 产物陈旧度 **15 / 10,753（未变）** · 变异陈旧度 0 · 变异 36/36 · 摘要警告 1 条。\n\n"
        "纪律：**一个单一数字源的价值取决于它说清每个数的时效，不取决于它集中。**\n\n"
        "下一轮：内存回到 2 GB 以上时 publish 一次，让函数数变当前；或继续核心（imperva 标记 / 优先级 ① 的 4 个真缺端点）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R999" not in h:
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
             for p, k in ((RBLOCK, "R999"), (RSTATUS, "R999"), (RVERDICT, "第 999 轮"), (BACKLOG, "R999")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R999: the metrics summary now says which of its numbers have aged\n\n"
         "This round set out to publish, so the function count would describe the current tree. Free memory was 1.8 GB, and\n"
         " the discipline for that is no AOT build, so publishing did not happen. Looking into why turned up something more\n"
         " important than the figure.\n\n"
         "The summary table listed 173,952 functions and 62.77 percent directly above a line saying fifteen source files are\n"
         " newer than the artifact, with nothing to connect them. artifact_freshness.py's own comment requires that ratio be\n"
         " labelled as describing an older build wherever it is quoted, and the summary did not do it. The mutation counts\n"
         " carried a staleness line reading an hour and a half against StoreFlow.cs, so those were stale too. Two aged\n"
         " numbers sat in the same column as a current suite total with no way to tell them apart.\n\n"
         "The fix belongs in the generator, not the data. metrics_report now emits a warning block above the summary, derived\n"
         " from the tools' own output rather than hardcoded: a non-zero count of newer source files means the function row\n"
         " describes an older build, and a staleness field not starting at zero means that group's numbers came from an\n"
         " expired run.\n\n"
         "The mutations were rerun while that was being written, since a test pass costs time rather than memory: thirty-six\n"
         " of thirty-six fired, none decorative, none skipped, tree green, at 14:06. With that record fresh, the warning block\n"
         " dropped from two entries to one, which is the block doing its job -- an entry disappears because the thing it\n"
         " warned about was actually done.\n\n"
         "The one that remains cannot be fixed today. AOT publishing on 1.8 GB would fail or take the machine with it, so the\n"
         " function count stays at 173,952 from a build fifteen files old. What this round bought is not a fresh figure but a\n"
         " silent one made to speak: an unrepairable gap should at least not be readable as current.\n\n"
         "Figures: suite 2210, artifact freshness fifteen files and 10,753 lines unchanged, mutation staleness zero after the\n"
         " rerun, mutations 36 of 36, one generated warning.\n\n"
         "Unknown: what the function count is today, which needs a publish and therefore memory.\n\n"
         "The lesson is that the rule \"every document cites METRICS\" assumed every number in it was current. Two were not, so\n"
         " the rule promoted an old figure to authority. A single source of numbers is worth what it says about each number's\n"
         " age, not what it centralises; centralising only makes it easier to assume they are all fine.\n\n"
         "One generator changed, mutations rerun; suite green at 2210."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()