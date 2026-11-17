"""Record R1062: both differences close -- one retracted, one located."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 两个差异都闭合了 —— 一个是**撤销**，一个是**定位**（R1062）

**R1060 留了两个 Unknown。这一轮两个都结案，而结案方式不同：一个是我错了（撤销），一个是两个数各有定义（定位）。**

### ① `exit 1` —— **撤销**：那是我的管道

```
Start-Process python tools/mutation-check.py -PassThru -Wait
→ python ExitCode = 0
```

**→ 不经管道测得的退出码是 **0**。所以 R1060 那个「输出 GREEN 而 exit 1」**不存在** ——
→ 它是 `python … | Select-Object` 那条管道的退出码，被我读成了脚本的。**

**→ 而 R1061 的推理链是对的：脚本无 `sys.exit`、`main()` 无返回值 ⇒ 应当 0 ⇒ 实测 **0**。
→ 所以那个 Unknown **撤销**，而撤销的依据是一次**正确方式的测量**，不是一次更好的解释。**

### ② `2277` vs `2258` 的差 19 —— **定位**：两个数回答不同的集合

```
metrics_report.py 排除 **7** 个浏览器类：
  VoiceListTests · GlobalSurfaceTests · KeyOrderDispatchTests · PatchJournalTests
  PruneWhitelistTests · NetworkRecorderLiveTests · ChromiumStealthTests

mutation-check.py:612 跑 restored tree 用  "Speed!=Slow"   ← **完全不排除那些类**
```

**→ 所以 `2277 − 2258 = 19` 就是那 7 个类里 `Speed!=Slow` 的用例数。
→ 而两个数**都对**，它们回答不同的集合：**

| 数字 | 口径 | 用途 |
|---|---|---|
| **2258** | **默认套件**（排除 7 个浏览器依赖类，R493 为内存稳定性） | **(e)「套件绿」的唯一口径 —— METRICS 是唯一数字源** |
| **2277** | `Speed!=Slow`（不排除） | 变异检查的**恢复验证**口径 |

**→ 而 R1060 把 2277 与 2258 并排写成「差 19，Unknown」，那本身是一个**口径混用**：
→ 它们不是同一个集合的两个测量，是**两个集合各一个测量**。**

**→ 所以「差 19」这个说法本身要撤回 —— 不存在差，存在两个定义。**

### ③ 而 (e) 现在**两项都达成**

| (e) 的子项 | 状态 | 依据 |
|---|---|---|
| 套件绿 | **是** | `metrics_report.py` → 2258 通过 / 0 失败 / 0 跳过 |
| **变异测试全 fired** | **是** | 36 / 36 · decorative 0 · skipped 0 · staleness 0 · 树 GREEN |
| 文档数字全来自 METRICS | **是** | 变异那三个数来自 `mutation_report.py`，它自己的权威 |
| **退出码** | **0 —— 已实测** | `Start-Process … -Wait` → `ExitCode = 0` |

### ④ 数字

| 度量 | R1061 | **R1062** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 4 / 889 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| 变异 fired | 36 / 36 | **36 / 36** |
| **`mutation-check.py` 退出码** | 「归属未定」 | **0（实测，不经管道）** |
| **`exit 1` 那个 Unknown** | 存在 | **撤销 —— 是我的管道** |
| **「差 19」** | Unknown | **撤回 —— 是口径不同，不是差** |
| **2277 的来源** | 未知 | **`Speed!=Slow`，不排除 7 个浏览器类** |
| **(e) 的两项** | 一项半 | **两项都达成** |

### 教训

> **两个 Unknown 用两种方式结案，而两种都比「解释」强：
> 一个是**测对了所以消失了**（撤销），一个是**发现两个数字各有定义**（定位）。**
> **→ 而 R1060 的错在于把两个不同的**集合**并排相减 —— 那与「把 `orig=0` 读成零缺口」
> 和「把管道退出码读成脚本的」是同一族的第三、四种形态：
> **在数字的来源或定义不清时做算术。****
"""

if "两个差异都闭合了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1062 —— **两个差异闭合：`exit 1` 撤销（是我的管道）· 「差 19」撤回（是口径不同）**

### ① `exit 1` —— 撤销

```
Start-Process python tools/mutation-check.py -PassThru -Wait  →  python ExitCode = 0
```

**⇒ R1060 那个「GREEN 而 exit 1」**不存在** —— 那是 `python … | Select-Object` 管道的退出码。
⇒ R1061 的推理链对（无 `sys.exit`、`main()` 无返回 ⇒ 应 0），而实测 **0**。撤销依据是**正确方式的测量**。**

### ② 「差 19」—— 撤回：不存在差，是两个定义

```
metrics_report 排除 7 个浏览器类：VoiceListTests · GlobalSurfaceTests · KeyOrderDispatchTests
  PatchJournalTests · PruneWhitelistTests · NetworkRecorderLiveTests · ChromiumStealthTests
mutation-check:612 用 "Speed!=Slow" —— **完全不排除**
```

| 数字 | 口径 | 用途 |
|---|---|---|
| **2258** | **默认套件**（排除 7 类，R493 内存稳定） | **(e)「套件绿」唯一口径，METRICS 是唯一数字源** |
| **2277** | `Speed!=Slow`（不排除） | 变异恢复验证口径 |

**⇒ 它们不是同一集合的两个测量，是两个集合各一个测量 ⇒「差 19」这个说法撤回。**

### ③ (e) 两项都达成

| 子项 | 状态 |
|---|---|
| 套件绿 | **是（2258 / 0 / 0）** |
| 变异测试全 fired | **是（36/36 · decorative 0 · skipped 0 · staleness 0 · GREEN）** |
| 文档数字来自 METRICS | **是**（变异数来自 mutation_report，自有权威） |
| **退出码** | **0 —— 已实测** |

### 数字

| 度量 | R1061 | **R1062** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 变异 fired | 36 / 36 | **36 / 36** |
| 脚本退出码 | 归属未定 | **0（实测）** |
| `exit 1` 那个 Unknown | 存在 | **撤销** |
| 「差 19」 | Unknown | **撤回（口径不同）** |
| (e) 两项 | 一项半 | **两项达成** |

**纪律**：在数字的来源或定义不清时做算术 —— 那是假零、假缺口、假退出码、假差值这四种错共同的根。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1062", NOTE)
append(RBLOCK, "R1062", "\n---\n\n## 486. **两个差异闭合：exit 1 撤销、「差 19」撤回（口径不同）**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1062: both differences close, one retracted and one located\n\n"
     "R1060 left two unknowns. Both are closed this round, and by different means: one turned out to be my mistake and\n"
     " is retracted, the other turned out to be two numbers with different definitions rather than a difference.\n\n"
     "The exit code was zero. Run without a pipe, waiting on the process and reading its own code, mutation-check exits\n"
     " clean. So the contradiction I filed last round does not exist -- it was the pipeline's code that I read as the\n"
     " script's. R1061's reasoning held: no sys.exit, main returns nothing, therefore zero, and the measurement agrees.\n"
     " The retraction rests on measuring properly, not on explaining better.\n\n"
     "The nineteen is not a difference at all. metrics_report excludes seven browser-dependent classes for memory\n"
     " stability under R493, and mutation-check runs its restore verification with a Speed!=Slow filter that excludes\n"
     " nothing. So 2258 and 2277 are one measurement each of two different sets, and subtracting them was the error.\n"
     " Both numbers are right; 2258 is the default suite and the only figure criterion (e)'s green claim should cite,\n"
     " and 2277 is the mutation tool's restore check.\n\n"
     "Which leaves criterion (e) complete on both counts: the suite is green at 2258 passing, and all thirty-six\n"
     " mutations fire with none decorative, none skipped, zero staleness and a green tree, on a run that exits zero.\n\n"
     "Figures: suite green at 2258, freshness four files and 889 lines, count 174,293, thirty-six mutations all fired,\n"
     " exit code zero measured directly, one unknown retracted and one withdrawn.\n\n"
     "The lesson is that arithmetic before provenance or definition is the shared root of the false zero, the false\n"
     " gap, the false exit code and the false difference -- four shapes, one habit."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
