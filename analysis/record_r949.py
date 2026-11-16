"""Record R949: republished, freshness zero, and 1153 lines of new code added no functions."""

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
### 重发布之后：陈旧度 **0**，而函数数**一个没动**（R949）

**判据 (c) 要求产物级对照可复算。陈旧度是 11 文件 / 1153 行，重发布了。**

```
publish artifact state: current
source files newer: 0
functions: replica .pdata  173,653
functions: original .pdata 277,120
```

### 而 173,653 和 R933 那次是**同一个数**

**R933 重发布加了 **1,963** 个函数。这一轮重发布加了 **0**。**

> **而这一轮之间新增了十一个文件、1153 行：`AddToCartMatrix` · `AddToCartPlacement` · `AddToCartCoverage` ·
> `CartPriming` · `PopMartDrawSteps` · `PaymentHostGaps` · `NegativeClaimClassTests` 等。**
> **而它们全是 **const 表、小静态类、和测例** —— 没有一个是 non-leaf 函数。

### 所以这给出了一个**具体的换算**

| 加什么 | 函数增量 |
|---|---|
| 常量表 / 静态类 / 测例 | **0** |
| R933 那次（真实逻辑） | **+1,963** |

> **所以剩下的 **103,467** 个函数缺口，**不能靠加表关掉**。
> 每一个 non-leaf 函数都需要**真代码** —— 一个分支、一次调用、一段状态机。**

### 而这解释了为什么最近十轮的函数数一直不动

**R938 → R949 十二轮，套件 1990 → 2059（+69 用例），而函数数一直 173,653。**

> **那十二轮的产出是**知识**（哪些名字是什么、哪些断言真的、哪些 host 是支付），
> 不是**函数**。而目标写的是「函数数量对等」——
> **所以这十二轮对那个判据的贡献是 0，而它们不是白做的：它们让**接下来写的代码**不会写错。**
> **但这一点必须说清楚，否则「套件 +69」读起来像进度。**

### 数字

| 度量 | R948 | **R949** |
|---|---|---|
| 套件 | 2059 | **2059** |
| 产物陈旧度 | 11 文件 / 1153 行 | **0 / 0（current）** |
| **函数数** | 173,653 | **173,653（未变）** |
| 函数比 | 62.66% | **62.66%** |

### 教训

> **「产物 current」和「函数数对等」是两个判据，而它们这一轮**同时被检查、只有一个变了**。
> 那正好把两件事分开：**产物可以是最新的，而功能一点没多。****
> **所以判据 (c) 通过的意思是「这个 exe 是从当前源码构建的」，
> 不是「这个 exe 更接近原版」。**
> **而唯一能量「更接近」的那个数是 173,653，而它十二轮没动。**
"""

if "重发布之后：陈旧度 **0**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 949 轮：重发布之后陈旧度 0，而函数数一个没动

### 重发布

```
publish artifact state: current
source files newer: 0
functions: replica .pdata  173,653
functions: original .pdata 277,120
```

### 而 173,653 和 R933 那次同一个数

**R933 重发布加了 **1,963** 个函数。这一轮加了 **0** ——
而中间新增了十一个文件、1153 行（`AddToCartMatrix` · `AddToCartPlacement` · `AddToCartCoverage` ·
`CartPriming` · `PopMartDrawSteps` · `PaymentHostGaps` 等）。**

> **它们全是 **const 表、小静态类、测例** —— 没有一个是 non-leaf 函数。**

### 所以有了一个具体换算

| 加什么 | 函数增量 |
|---|---|
| 常量表 / 静态类 / 测例 | **0** |
| R933 那次（真实逻辑） | **+1,963** |

> **剩下的 **103,467** 个缺口**不能靠加表关掉**。每个 non-leaf 函数都要真代码：
> 一个分支、一次调用、一段状态机。**

### 而这解释了十二轮函数数不动

**R938 → R949：套件 1990 → 2059（+69 用例），函数数一直 173,653。**

> **那十二轮的产出是**知识**，不是**函数**。而目标写的是「函数数量对等」——
> 所以这十二轮对那个判据的贡献是 0。而它们不是白做的：它们让**接下来写的代码**不写错。
> **但这一点必须说清楚，否则「套件 +69」读起来像进度。**

### 数字

| 度量 | R948 | **R949** |
|---|---|---|
| 套件 | 2059 | **2059** |
| 产物陈旧度 | 11 / 1153 | **0 / 0（current）** |
| 函数数 | 173,653 | **173,653（未变）** |
| 函数比 | 62.66% | **62.66%** |

### 教训

> **「产物 current」与「函数数对等」是两个判据，这一轮**同时被检查、只有一个变了**。
> 那正好把两件事分开：**产物可以是最新的，而功能一点没多。**
> **判据 (c) 通过的意思是「这个 exe 从当前源码构建」，不是「更接近原版」。**
> **唯一能量「更接近」的数是 173,653，而它十二轮没动。**
"""

BACKLOG_ADD = """

## 判据 (c) — 产物 current；而 1153 行新代码加了 0 个函数（R949，**重发布**）

### 重发布结果

**`.publish-aot\\Cybersole.Ui.exe` 54,652 KB · 陈旧度 11/1153 → 0/0 · 函数数 173,653 未变**

### 具体换算

| 加什么 | 函数增量 |
|---|---|
| const 表 / 静态类 / 测例 | **0** |
| 真实逻辑（R933） | **+1,963** |

**→ 剩余 103,467 缺口不能靠加表关掉。**

### 十二轮函数数不动的解释

**R938→R949 套件 +69 用例，函数数不变 —— 那十二轮产出的是**知识**，不是**函数**。**

### 数字

**套件 2059（未变）· 陈旧度 0/0 · 函数数 173,653 · 比 62.66%**

| 仍 Unknown | |
|---|---|
| 一个 non-leaf 函数的平均代码量 | R933 单样本 ≈ 12 行 C# |
| 哪些批次能一次加最多函数 | 未规划 |
| 表驱动模块是否该按模块折成函数 | 设计问题 |

**纪律**：判据 (c) 通过的意思是「exe 从当前源码构建」，不是「更接近原版」。
"""

BLOCKER = """

---

## 373. 重发布：陈旧度 0，函数数一个没动

> R949。**重发布，未改代码。** 套件 **2059 通过 / 0 失败 / 0 跳过**。

### 一、重发布结果

```
publish artifact state: current
source files newer: 0
functions: replica .pdata  173,653
functions: original .pdata 277,120
```

**`.publish-aot\\Cybersole.Ui.exe` = 54,652 KB**

### 二、而 173,653 与 R933 同一个数

**R933 加了 **1,963**；这一轮加 **0**。而中间新增十一文件、1153 行。**

**→ 那 1153 行全是 const 表 / 小静态类 / 测例，没有一个是 non-leaf 函数。**

### 三、具体换算

| 加什么 | 函数增量 |
|---|---|
| const 表 / 静态类 / 测例 | **0** |
| 真实逻辑（R933） | **+1,963** |

**→ 剩余 103,467 缺口不能靠加表关掉；每个 non-leaf 函数都要一个分支、一次调用、或一段状态机。**

### 四、十二轮函数数不动的解释

**R938→R949：套件 1990 → 2059（+69 用例），函数数 173,653 不变。**

**产出是知识不是函数 —— 对「函数数量对等」的贡献是 0，但让接下来写的代码不写错。**

### 五、数字

| 度量 | R948 | R949 |
|---|---|---|
| 套件 | 2059 | **2059** |
| 产物陈旧度 | 11 / 1153 | **0 / 0** |
| **函数数** | 173,653 | **173,653** |
| 函数比 | 62.66% | **62.66%** |

### 六、验证

```
dotnet publish -c Release -r win-x64 -p:PublishAot=true -o .publish-aot  -> exit 0, 54,652 KB
python tools/artifact_freshness.py   -> state: current, 0 files newer
python tools/metrics_report.py       -> 173,653 / 277,120 = 62.66%
```

### 七、仍然 Unknown

- **一个 non-leaf 函数的平均代码量**：**Inference** —— R933 单样本 ≈ 12 行 C#。
- **哪些批次能一次加最多函数**：**Unknown** —— 未规划。
- **表驱动模块是否该按模块折成函数**：**Unknown** —— 设计问题。

### 八、教训

**「产物 current」与「函数数对等」是两个判据，这一轮同时被检查、只有一个变了 ——
那正好把两件事分开：产物可以是最新的，而功能一点没多。**

**判据 (c) 通过的意思是「这个 exe 从当前源码构建」，不是「更接近原版」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R949", BLOCKER)
    ensure(RSTATUS, "R949", BLOCKER)
    ensure(RVERDICT, "第 949 轮", VERDICT)
    ensure(BACKLOG, "R949", BACKLOG_ADD)

    note = (
        "\n## R949 补充 — 重发布：陈旧度 0，函数数一个没动（套件 2059）\n\n"
        "重发布 .publish-aot\\Cybersole.Ui.exe 54,652 KB · 陈旧度 11/1153 → 0/0 (current) · 函数数 173,653 未变。\n\n"
        "而 173,653 与 R933 同一个数：R933 加了 1,963，这一轮加 0 —— 而中间新增十一文件 1153 行，"
        "全是 const 表/小静态类/测例，没有 non-leaf 函数。\n\n"
        "换算：const 表/静态类/测例 → 0 个函数；真实逻辑（R933）→ +1,963。"
        "→ 剩余 103,467 缺口不能靠加表关掉。\n\n"
        "解释十二轮函数数不动：R938→R949 套件 +69 用例，函数数不变 —— 产出是知识不是函数。\n\n"
        "数字：套件 2059（未变）· 陈旧度 0/0 · 函数数 173,653 · 比 62.66%。\n\n"
        "纪律：判据 (c) 通过的意思是「exe 从当前源码构建」，不是「更接近原版」。\n\n"
        "下一轮：写一批真正有 non-leaf 函数的代码（优先 ③ 请求与指纹层，或 ① 未做的 flow 逻辑）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R949" not in h:
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
             for p, k in ((RBLOCK, "R949"), (RSTATUS, "R949"), (RVERDICT, "第 949 轮"), (BACKLOG, "R949")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R949: republished, freshness zero, and 1153 lines of new code added no functions\n\n"
         "Criterion (c) asks for the artifact comparison to be recomputable, and the artifact was stale by eleven files\n"
         " and a thousand and one hundred and fifty-three lines. Republishing brought it current: zero files newer, and\n"
         " the executable is fifty-four megabytes built from the present source.\n\n"
         "The function count did not move. It is 173,653, the same figure R933 produced after its republish -- and R933's\n"
         " republish added 1,963 functions while this one added none, across eleven new files and well over a thousand\n"
         " lines. The difference is what those lines are: constant tables, small static classes and tests, none of which\n"
         " contains a non-leaf function.\n\n"
         "Which gives a concrete conversion for the remaining gap. Constant tables, static classes and tests add zero\n"
         " functions; real logic added 1,963. So the 103,467-function gap cannot be closed by adding tables, because a\n"
         " non-leaf function needs a branch, a call or a state machine, not a list.\n\n"
         "That also explains twelve rounds of an unmoving count. From R938 to here the suite went from 1990 tests to 2059\n"
         " while the count stayed exactly where it was, because those rounds produced knowledge rather than functions --\n"
         " what each name is, which assertions are true, which hosts are payment hosts. That work is not wasted, since it\n"
         " keeps the next code from being wrong, but its contribution to the function-count criterion is zero and saying\n"
         " so matters, because a suite rising by sixty-nine reads like progress.\n\n"
         "Figures: suite unchanged at 2059, freshness from eleven files to none, and the function count and ratio\n"
         " unchanged at 173,653 and 62.66 percent.\n\n"
         "Unknown: how much code one non-leaf function averages, inferred as about twelve C# lines from a single sample\n"
         " in R933; which batch of work adds the most functions at once, which was not planned; and whether table-driven\n"
         " modules should be folded into functions at all, which is a design question rather than a measurement.\n\n"
         "The lesson is that two criteria were checked in one round and only one of them changed, which separates them\n"
         " exactly: an artifact can be perfectly current while containing nothing more. Passing criterion (c) means the\n"
         " executable was built from this source, not that it is closer to the original, and the only number that measures\n"
         " closer sat still for twelve rounds.\n\n"
         "Republished; no code changed; suite green at 2059."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()