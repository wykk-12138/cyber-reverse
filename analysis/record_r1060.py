"""Record R1060: (e)'s second half is 36/36, with two differences left unexplained rather than guessed."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### (e) 的另一半：**36 个变异全部 fired**，staleness 0；而两个差异我没有猜（R1060）

**R1059 说 (e) 要「套件绿、变异测试全 fired」，而只算了前半。这一轮跑变异检查，后半也拿到的 —— 而它自带的警告让我必须先重跑。**

### ① 而工具自己要求重跑，那是对的

**第一次读报告拿到的是：**

```
mutation-fit-total: 36 · fired: 36 · decorative: 0 · skipped: 0 · tree: GREEN
mutation-fit-staleness: 7:52:15 -- behaviour_coverage.py changed after the run
"The counts above are from 2026-11-17T14:06:23+08:00 and the tree has moved since.
 They are a record of that run, not a statement about this one; re-run before quoting them as current."
```

**→ 那是**我**造成的陈旧：我在这轮之前改了 `behaviour_coverage.py`。
→ 而工具把这件事**写在输出里**并给出重跑命令 —— 所以「36/36」在那一刻是**历史**，不是现状。**
**→ 若我直接引用它，那就是**引一个过期数字当现状** —— 而那正是 METRICS 存在的理由。**

### ② 重跑后的数字（新鲜）

```
mutation-fit-total: 36
mutation-fit-fired: 36
mutation-fit-decorative: 0
mutation-fit-skipped: 0
mutation-fit-tree: GREEN
mutation-fit-staleness: 0 -- no exercised file is newer than the run
"Every mutation fired, none was decorative and none was skipped at the time of that run."
```

**→ 所以 (e) 的「变异测试全 fired」= **36 / 36 = 100%**，且无装饰性变异、无跳过、树 GREEN、**无陈旧**。
→ 而 36 个 guard 逐个打印了它模拟的回归（`round 135 -- the screen table stops agreeing with the geometry table`
· `round 290 -- a flow step loses its ordinal` · `round 623 -- the copy audit's detail loop goes back to the old
predicate` 等）—— **每一个都对应一条真实修过的缺陷。****

### ③ 而重跑恢复的树跑出 **2277** 个用例，而 METRICS 报 **2258** —— 差 19，而我**不猜**

```
mutation-check 的 restored tree:  2275 通过 / 0 失败 / 2 跳过 / 总计 2277
metrics_report.py 的完整套件:      2258 通过 / 0 失败 / 0 跳过 / 总计 2258
```

**→ 差 19，而 METRICS 的注释里写着它**默认排除浏览器依赖用例**（R493：`VoiceListTests` / `GlobalSurfaceTests` 等
要驱动真 Chrome，端点起不来时每个耗约 2 分钟，2026-11-14 连跑导致整机内存耗尽重启）。
→ **19 与「2 跳过」是否就是那批被排除的类，本表没有验证 ⇒ 标 Unknown。**

**→ 而我不把它写成「因为 R493 所以差 19」—— 那是一个**听起来对的**解释，而 R1044 教过我零值需要对照。**

### ④ 而 `mutation-check.py` 的 exit code 是 **1**，而它打印的一切都是 GREEN —— 那个 1 我没有解释

**→ 可能来源：**
- 「2 skipped」被它判为异常
- 某个 guard 的 round 记录过期
- 或者 restored tree 之外的另一项一致性检查

**→ 而**不猜**：记录成 Unknown，写清「输出全 GREEN 而 exit 1」这个矛盾本身。
→ 若下一轮要追，起点是 `analysis/MUTATION_RESULT.json` 与 `mutation-check.py` 的返回路径。**

### ⑤ 所以 (e) 现在的状态

| (e) 的子项 | 状态 |
|---|---|
| 套件绿 | **是 —— 2258 / 0 / 0** |
| **变异测试全 fired** | **是 —— 36 / 36，decorative 0，skipped 0，staleness 0** |
| 文档数字全来自 METRICS | **是**（本轮除外：36/2277 来自 mutation_report 与 mutation-check，而那是它们各自的权威） |
| **未解释** | **exit 1 · 2277 vs 2258 差 19** |

### ⑥ 数字

| 度量 | R1059 | **R1060** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 4 / 889 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| **变异总数** | 未测 | **36** |
| **fired** | 未测 | **36（100%）** |
| **decorative / skipped** | 未测 | **0 / 0** |
| **变异树** | 未测 | **GREEN** |
| **staleness** | — | **0（重跑后）** |
| **restored tree 用例** | — | **2277（2275 通过 / 2 跳过）** |
| **与 METRICS 的差** | — | **19 —— Unknown，不猜** |
| **`mutation-check` exit** | — | **1，而输出全 GREEN —— Unknown** |

### 教训

> **工具把「我的数字过期了」写在输出里，而那比任何纪律条文都有效 —— 它给出重跑命令，
> 而**引用过期数字**这件事因此变得显眼。**
> **→ 而这一轮的两个差异（19 与 exit 1）我都没有解释。那不是懒：
> 「因为 R493 所以差 19」听起来完全合理，而它是**推断**，而 R1044 教过我零值/差值需要对照。**
> **→ 所以正确的记录是「差 19，未验证」而不是「差 19，因为 R493」。**
"""

if "(e) 的另一半：**36 个变异全部 fired**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1060 —— **(e) 后半达成：36/36 变异 fired、staleness 0；两个差异标 Unknown 不猜**

### 而工具自己要求重跑 —— 那是对的

第一次读到的是**陈旧**的：
```
total 36 · fired 36 · decorative 0 · skipped 0 · tree GREEN
staleness 7:52:15 -- behaviour_coverage.py changed after the run
"They are a record of that run, not a statement about this one; re-run before quoting them as current."
```
**那是我造成的陈旧（我改了 `behaviour_coverage.py`）。直接引用就是引过期数字当现状。**

### 重跑后（新鲜）

```
mutation-fit-total: 36 · fired: 36 · decorative: 0 · skipped: 0
tree: GREEN · staleness: 0 -- no exercised file is newer than the run
"Every mutation fired, none was decorative and none was skipped at the time of that run."
```

**⇒ (e) 的「变异测试全 fired」= **36/36 = 100%**。而 36 个 guard 各对应一条真实修过的缺陷
（`round 290 -- a flow step loses its ordinal` · `round 623 -- the copy audit's detail loop goes back to the old predicate` …）。**

### 两个差异 —— 我不猜

```
mutation-check restored tree: 2275 通过 / 0 失败 / 2 跳过 / 总计 2277
metrics_report.py 完整套件:    2258 通过 / 0 失败 / 0 跳过 / 总计 2258      ← 差 19
```

**→ METRICS 注释说它**默认排除浏览器依赖用例**（R493）。而「19 与 2 跳过是否就是那批」**未验证 ⇒ Unknown**。
→ **不写成「因为 R493 所以差 19」—— 那是听起来对的推断，而 R1044 教过零值/差值需要对照。**

**而 `mutation-check.py` 的 exit code 是 **1**，而它打印的一切都是 GREEN ⇒ 那个矛盾**未解释**，标 Unknown。
起点：`analysis/MUTATION_RESULT.json` 与 `mutation-check.py` 的返回路径。**

### (e) 的状态

| 子项 | 状态 |
|---|---|
| 套件绿 | **是（2258 / 0 / 0）** |
| 变异测试全 fired | **是（36/36 · decorative 0 · skipped 0 · staleness 0）** |
| 文档数字来自 METRICS | **是**（36/2277 来自 mutation 工具，各有其权威） |
| 未解释 | **exit 1 · 差 19** |

### 数字

| 度量 | R1059 | **R1060** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 变异总数 / fired | 未测 | **36 / 36（100%）** |
| decorative / skipped | 未测 | **0 / 0** |
| staleness | — | **0** |
| restored tree 用例 | — | **2277** |
| 与 METRICS 差 | — | **19 —— Unknown** |

**纪律**：工具把「你的数字过期了」写在输出里，比任何纪律条文都有效。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1060", NOTE)
append(RBLOCK, "R1060", "\n---\n\n## 484. **(e) 后半：36/36 变异 fired；两个差异标 Unknown**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1060: every mutation fires, and two differences are left unexplained on purpose\n\n"
     "R1059 counted how much behaviour has assertions behind it and said criterion (e)'s other half -- mutation all\n"
     " fired -- was still open. The repository already had the toolchain, and the report answered immediately with a\n"
     " warning attached: the counts were from a run before I changed behaviour_coverage.py, and the tool said so in its\n"
     " own output with the command to re-run. Quoting them would have been quoting a historical number as current.\n\n"
     "After the re-run: thirty-six mutations, thirty-six fired, none decorative, none skipped, tree green, staleness\n"
     " zero. Each guard prints the regression it simulates and each one corresponds to a defect that was actually fixed\n"
     " -- a flow step losing its ordinal, a copy audit reverting to an old predicate, the screen table drifting from the\n"
     " geometry table. So criterion (e)'s second half is at one hundred per cent, and freshly so.\n\n"
     "Two differences are recorded as unknown rather than explained. The restored tree ran 2277 cases where \n"
     " metrics_report reports 2258, a gap of nineteen, and the METRICS header says it excludes browser-dependent tests\n"
     " by default. That makes nineteen sound explicable, and sounding explicable is exactly why it is not written down\n"
     " as explained: R1044 established that a difference needs a control before it can be read. Also, mutation-check\n"
     " exits with status one while everything it printed is green, and that contradiction is left standing with the two\n"
     " places to start investigating.\n\n"
     "Figures: suite green at 2258, freshness four files and 889 lines, count 174,293, thirty-six mutations all fired,\n"
     " zero decorative, zero skipped, zero staleness, and two open differences marked as such.\n\n"
     "Unknown: whether the nineteen are the excluded browser classes, and what returns one from mutation-check while the\n"
     " report says green.\n\n"
     "The lesson is that a tool which prints its own staleness is worth more than a rule telling people to re-run, and\n"
     " that a plausible explanation for a difference is not the same as a checked one."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
