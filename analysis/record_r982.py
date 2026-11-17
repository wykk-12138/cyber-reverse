"""Record R982: the mutation figure is now a metric with a timestamp beside it."""

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
### 变异数进了唯一数字源，而它自带**时间戳与陈旧度**（R982）

**判据 (e) 的第二句要「变异测试全 fired」。R981 让它成立了，而那个 `36 / 36` **只活在散文里** ——
正是 AGENTS.md §4 禁止的，也正是 R979 抓到的那个形状（交接里引了个 150 轮前的套件数）。**

### 而它不能塞进 `metrics_report.py`

**一次完整变异是 36 条 × 各跑一次过滤后的套件，约 12 分钟。而 `metrics_report.py` 是**每轮都跑**的命令。
把 12 分钟塞进去，它就不会被跑了。**

> **所以改成两个部分：`mutation-check.py` 写一份**带日期的结果**，`mutation_report.py` 读它。
> 与 `artifact_freshness.py` 对发布产物的处理同一个安排：数字带着它自己的时间戳，
> **而「陈旧」是被报出来的，不是被藏起来的。****

### 结果文件（真实跑出来的，不是写的）

```
{
  "ran_at": "2026-11-17T12:25:02+08:00",
  "total": 36,
  "fired": 36,
  "decorative": 0,
  "skipped": 0,
  "tree": "GREEN"
}
```

### 而 `METRICS.md` 多了五行

```
| 变异套件（上次运行） — mutation-fit: total | 36 |
| 变异套件（上次运行） — mutation-fit: fired | 36 |
| 变异套件（上次运行） — mutation-fit: decorative | 0 |
| 变异套件（上次运行） — mutation-fit: skipped | 0 |
| 变异套件（上次运行） — mutation-fit: staleness | 0 -- no exercised file is newer than the run |
```

### 而 stale 那个字段我改了两版才对

**第一版把 `docs/**` 也算进「被改动的输入」。后果：**任何文档编辑都会让 staleness 变成正数** ——
而一个每轮都响的告警没人看。**

> **变异改的是源码、跑的是测试。文档里的一段话两样都不是。改成只看 `src` / `tests` / `tools`。**

**第二版还把自己算了进去 —— 于是**改一次报告器就让报告失效**。
`mutation_report.py` 只读结果文件，改它不可能改变任何一条变异的裁决，所以按名字排除。**

**而两个方向都验过：**

```
排除自身后           staleness: 0
造一个源码文件       staleness: 0:03:26 -- dummy_probe.py changed after the run
删掉它              staleness: 0
```

### 而这个设计的诚实之处

**它做得到：报上次运行的数，并报源码从那之后动没动。
它做不到：保证今天重跑会给同样的数。** —— 那正是「重跑」的用途，而工具的输出自己写着这一句。

### 数字

| 度量 | R981 | **R982** |
|---|---|---|
| 度量项数 | 14 | **15** |
| 变异 fired / 总 | 36 / 36（只在散文里） | **36 / 36（在 METRICS 里，带时间戳）** |
| staleness | 未测 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 教训

> **一个「陈旧度」字段第一次写会错两次：一次因为把不相干的文件算进来（每轮都响），
> 一次因为把自己算进来（自我失效）。**
> **而两次的后果是同一种：告警响得太多，于是没人看 —— 而那时它和不存在是一样的。**
"""

if "变异数进了唯一数字源" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 982 轮：变异数进了唯一数字源，自带时间戳与陈旧度

### 为什么要拆成两半

**判据 (e) 第二句要「变异测试全 fired」。R981 让它成立了，而 `36 / 36` 只活在散文里 ——
正是 §4 禁止的，也正是 R979 抓到的形状。**

**但一次完整变异约 12 分钟，而 `metrics_report.py` 每轮都跑。塞进去它就不会被跑了。**

> **所以：`mutation-check.py` 写带日期的结果，`mutation_report.py` 读它。
> 与 `artifact_freshness.py` 同一个安排 —— 数字带时间戳，陈旧是被报出来的。**

### 结果文件（真实跑出来的）

```json
{"ran_at": "2026-11-17T12:25:02+08:00", "total": 36, "fired": 36,
 "decorative": 0, "skipped": 0, "tree": "GREEN"}
```

### METRICS.md 多了五行

```
mutation-fit: total 36 · fired 36 · decorative 0 · skipped 0
mutation-fit: staleness: 0 -- no exercised file is newer than the run
```

### 而 stale 字段我改了两版

**第一版把 `docs/**` 算进来 → **任何文档编辑都让 staleness 变正数** → 每轮都响的告警没人看。
改成只看 `src` / `tests` / `tools`。**

**第二版把自己算进去 → **改一次报告器就让报告失效** → 按名字排除自己（它只读，改它不可能改变任何裁决）。**

**两个方向都验过：**

```
排除自身后   staleness: 0
造一个源码   staleness: 0:03:26 -- dummy_probe.py changed after the run
删掉它      staleness: 0
```

### 这个设计的诚实边界

**做得到**：报上次运行的数，并报源码从那之后动没动。
**做不到**：保证今天重跑给同样的数 —— 那正是「重跑」的用途，工具输出自己写着这句。

### 数字

| 度量 | R981 | **R982** |
|---|---|---|
| 度量项数 | 14 | **15** |
| 变异 fired / 总 | 36 / 36（散文里） | **36 / 36（METRICS 里）** |
| staleness | 未测 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 教训

> **「陈旧度」字段第一次写会错两次：一次把不相干的算进来（每轮都响），一次把自己算进来（自我失效）。
> 而两次的后果是同一种：告警响得太多，于是没人看 —— 那时它和不存在是一样的。**
"""

BACKLOG_ADD = """

## 判据 (e) — **变异度量进 METRICS：36 total / 36 fired / 0 decorative / 0 skipped，staleness 0**（R982，**+1 度量 +1 工具**）

### 结构

**`mutation-check.py` 末尾写 `analysis/MUTATION_RESULT.json`（带 `ran_at`）→ `tools/mutation_report.py` 读它。
与 `artifact_freshness.py` 同一安排：数字带时间戳，陈旧被报出来而不是藏起来。**

### METRICS 五行

```
mutation-fit: total 36 · fired 36 · decorative 0 · skipped 0
mutation-fit: staleness: 0 -- no exercised file is newer than the run
```

### staleness 改了两版

**① 把 `docs/**` 算进来 → 任何文档编辑都让 staleness 变正 → 每轮都响 → 没人看。改成只看 `src`/`tests`/`tools`。**
**② 把自己算进来 → 改一次报告器就自我失效。按名字排除（它只读）。**

**两方向都验过：排除后 0；造一个源码文件 → `0:03:26`；删掉 → 0。**

### 数字

**度量项 15 · 变异 36/36 · staleness 0 · 套件 2200 · 产物陈旧度 0/0**

| 仍 Unknown | |
|---|---|
| 今天重跑会不会给同样的数 | 只有重跑能答（工具输出自己写着这句） |

**纪律**：一个每轮都响的告警，和不存在是一样的。
"""

BLOCKER = """

---

## 406. **变异度量进 METRICS（36/36/0/0，staleness 0）**

> R982。**+1 度量 +1 工具 + 结果文件。** 套件 **2200 通过 / 0 失败 / 0 跳过**。

### 一、为什么拆成两半

**判据 (e) 第二句要「变异测试全 fired」。R981 让它成立，而 `36 / 36` 只活在散文里 ——
正是 §4 禁止的，也正是 R979 抓到的形状。**

**但一次完整变异约 12 分钟，而 `metrics_report.py` 每轮都跑。塞进去它就不会被跑。
→ `mutation-check.py` 写带日期的结果，`mutation_report.py` 读它 —— 与 `artifact_freshness.py` 同一安排。**

### 二、结果文件（真实跑出来的）

```json
{"ran_at": "2026-11-17T12:25:02+08:00", "total": 36, "fired": 36,
 "decorative": 0, "skipped": 0, "tree": "GREEN"}
```

### 三、METRICS 五行

```
| 变异套件（上次运行） — mutation-fit: total | 36 |
| 变异套件（上次运行） — mutation-fit: fired | 36 |
| 变异套件（上次运行） — mutation-fit: decorative | 0 |
| 变异套件（上次运行） — mutation-fit: skipped | 0 |
| 变异套件（上次运行） — mutation-fit: staleness | 0 -- no exercised file is newer than the run |
```

### 四、staleness 字段改了两版

**① 把 `docs/**` 算进「被改动的输入」→ **任何文档编辑都让 staleness 变正数** → 每轮都响 → 没人看。
改成只看 `src` / `tests` / `tools`。**

**② 把自己（`mutation_report.py`）算进去 → **改一次报告器就让报告失效** → 按名字排除
（它只读结果文件，改它不可能改变任何一条变异的裁决）。**

**两个方向都验过：**

```
排除自身后        staleness: 0
造一个源码文件    staleness: 0:03:26 -- dummy_probe.py changed after the run
删掉它           staleness: 0
```

### 五、诚实边界

**做得到**：报上次运行的数，并报源码从那之后动没动。
**做不到**：保证今天重跑给同样的数。**那正是「重跑」的用途，而工具的输出自己写着这一句。**

### 六、数字

| 度量 | R981 | R982 |
|---|---|---|
| 度量项数 | 14 | **15** |
| 变异 fired / 总 | 36 / 36（散文里） | **36 / 36（METRICS 里）** |
| staleness | 未测 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 七、验证

```
cd replica
python tools/mutation-report  -> 见下
python tools/mutation_report.py
  -> mutation-fit-total: 36 / fired: 36 / decorative: 0 / skipped: 0 / staleness: 0
python tools/metrics_report.py
  -> 变异套件（上次运行） exit 0 {...}；完整套件 exit 0  2200 通过 / 0 失败 / 0 跳过
```

### 八、仍然 Unknown

- **今天重跑会不会给同样的数**：**只有重跑能答** —— 工具输出自己写着这句话。

### 九、教训

**一个「陈旧度」字段第一次写会错两次：一次把不相干的算进来（每轮都响），一次把自己算进来（自我失效）。**

**而两次的后果是同一种：告警响得太多，于是没人看 —— 那时它和不存在是一样的。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R982", BLOCKER)
    ensure(RSTATUS, "R982", BLOCKER)
    ensure(RVERDICT, "第 982 轮", VERDICT)
    ensure(BACKLOG, "R982", BACKLOG_ADD)

    note = (
        "\n## R982 补充 — **变异度量进 METRICS：36/36/0/0，staleness 0**（+1 度量 +1 工具，套件 2200）\n\n"
        "判据 (e) 第二句的 `36 / 36` 之前只活在散文里。一次完整变异约 12 分钟，塞进 `metrics_report.py` 会让它不被跑，\n"
        "所以拆成两半：`mutation-check.py` 写 `analysis/MUTATION_RESULT.json`（带 `ran_at`）→\n"
        "`tools/mutation_report.py` 读它。与 `artifact_freshness.py` 同一安排。\n\n"
        "METRICS 五行：`mutation-fit: total 36 / fired 36 / decorative 0 / skipped 0 / staleness 0`。\n\n"
        "**staleness 字段改了两版**：① 把 `docs/**` 算进来 → 任何文档编辑都让它变正 → 每轮都响 → 没人看；\n"
        "③ 把自己算进来 → 改一次报告器就自我失效 → 按名字排除。两方向都验过（排除后 0 / 造源码文件 → 0:03:26 / 删掉 → 0）。\n\n"
        "数字：度量项 15 · 变异 36/36 · staleness 0 · 套件 2200 · 产物陈旧度 0/0。\n\n"
        "纪律：**一个每轮都响的告警，和不存在是一样的。**\n\n"
        "下一轮：回到核心 —— 判据 (f) 的镜像→复刻件方向（`myshopify` 主机池 → 复刻差别名），或函数数那一刀按内容分。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R982" not in h:
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
             for p, k in ((RBLOCK, "R982"), (RSTATUS, "R982"), (RVERDICT, "第 982 轮"), (BACKLOG, "R982")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R982: the mutation figure becomes a metric with a timestamp beside it\n\n"
         "Criterion (e) says the mutation tests all fire. R981 made that true and the figure lived only in prose, which is\n"
         " what section 4 forbids and exactly the shape R979 caught when a handoff block quoted a suite total a hundred and\n"
         " fifty rounds old.\n\n"
         "A full mutation pass is thirty-six mutations each running a filtered suite, about twelve minutes, and\n"
         " metrics_report is the command run every round. Putting twelve minutes into it would stop it being run. So the pass\n"
         " now writes a dated record and a small reporter reads it, the same arrangement artifact_freshness uses for the\n"
         " publish artifact: the number carries its own timestamp and staleness is reported rather than hidden.\n\n"
         "The staleness field took two attempts to get right and both failures were the same failure. Counting docs/ made any\n"
         " document edit report the record as stale, and a warning that fires every round is one nobody reads. Counting this\n"
         " reporter itself made every improvement to it invalidate what it reports. Neither file changes what a mutation\n"
         " mutates or what a guard sees, so both are now excluded, and both directions were checked: zero with them out, three\n"
         " minutes twenty-six with a source file added, back to zero when it was removed.\n\n"
         "The design says what it can and cannot do. It reports the last run's counts and whether the tree has moved since. It\n"
         " does not promise a re-run today would agree, and the tool's own output says so.\n\n"
         "Figures: metrics fourteen to fifteen, mutations 36 of 36 fired with none decorative and none skipped, staleness zero,\n"
         " suite 2200, artifact freshness zero.\n\n"
         "Unknown: whether a re-run now would give the same counts, which only re-running answers.\n\n"
         "The lesson is that a staleness field goes wrong twice on first writing -- once by counting what does not matter, once\n"
         " by counting itself -- and both times the consequence is a warning loud enough to be ignored, which is the same as\n"
         " having none.\n\n"
         "One metric and one tool added, one result file written by a real run; suite green at 2200."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()