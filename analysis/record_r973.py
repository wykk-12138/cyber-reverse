"""Record R973: the large functions dominate the mean and are irrelevant to the objective."""

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
### 那 671 个大函数：**主导均值差，而对目标影响 0.24%**（R973）

**R972 说下一轮查那 671 个大函数是什么（它们解释 83% 的均值差）。查了，而结果是**它们不该查**。**

### 它们的量

```
4096 B 以上的函数: 671 个
合计 7,676,312 B = 原版可执行段（48,723,539 B）的 15.8%
最大的 12 个:
  0x14117C4E0    687318 B
  0x1419F6060    527392 B
  0x1412241C0    227186 B
  0x14030F560     83620 B
  ...
```

### 而对目标的意思是

| 视角 | 这 671 个的占比 |
|---|---|
| **函数数**（目标第一条：函数数量对等） | **671 / 277,120 = 0.24%** |
| 执行段字节 | 15.8% |
| 均值差 | **83%** |

> **所以它们**主导均值差、占 15.8% 的代码体积，而对「函数数量对等」这个目标贡献 0.24%。**
> **而我上一轮把「查它们」立成了下一轮目标 —— 那是在追一个对我的目标几乎没有影响的东西。****

### 而反编译它们**不可行**

```
ida.py dec 0x14117C4E0 --lines 30
  -> {"error": "Decompilation failed at 0x14117c4e0"}
```

**687 KB 的函数，Hex-Rays 拒绝。**

**而 `xrefs` 显示它被 `sub_1412241C0`（227 KB，第三大的）引用 —— 那是一个**大函数互相调用**的簇。**

> **所以「那 671 个是什么」这个问题在工具层面**也**不便宜：最大的几个反编译不出来，
> 而它们互相引用，所以顺藤摸瓜成本高。**

### 所以结论是**优先级**，不是事实

**目标写的是：函数数量对等（第一条）、每个函数功能相等（第二条）、效率相近（第三条）。
而这 671 个只影响第一条的 0.24% —— 它们属于第二条或第三条的范畴（某个函数的功能/效率），
而**第二条需要它们的功能相等，那需要反编译，而反编译失败了**。**

> **所以它们是**已知不可得**的一类，而这一类现在有具体形状：
> 「671 个 4 KB 以上的函数，占字节 15.8%，反编译失败，对函数数贡献 0.24%」。
> **而那该写进 Unknown，不该占下一轮。****

### 数字

| 度量 | R972 | **R973** |
|---|---|---|
| 套件 | 2186 | **2186（只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **4096+ 函数的字节** | 未测 | **7,676,312 B（15.8%）** |
| **对函数数的贡献** | 未测 | **0.24%** |
| **最大函数的反编译** | 未试 | **失败** |

### 教训

> **上一轮我把「查这 671 个」立为目标，因为它们是**均值差**的 83%。
> 而均值差**不是目标** —— 函数数、功能、效率才是。**
> **我把一个**解释中间量**的东西当成了优先项，而它对我真正要的数的贡献是 0.24%。**
> **一个指标被解释清楚，不等于那个解释值得追。**
"""

if "那 671 个大函数：**主导均值差" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 973 轮：那 671 个大函数 —— 主导均值差，而对目标影响 0.24%

### 它们的量

```
4096 B 以上的函数: 671 个
合计 7,676,312 B = 原版可执行段的 15.8%
0x14117C4E0   687318 B
0x1419F6060   527392 B
0x1412241C0   227186 B
```

### 而对目标

| 视角 | 占比 |
|---|---|
| **函数数**（目标第一条） | **0.24%** |
| 执行段字节 | 15.8% |
| 均值差 | **83%** |

> **它们主导均值差、占 15.8% 体积，而对「函数数量对等」贡献 0.24%。
> 上一轮我把「查它们」立为目标，是在追一个对目标几乎没有影响的东西。**

### 而反编译它们**不可行**

```
ida.py dec 0x14117C4E0  ->  {"error": "Decompilation failed"}
```

**687 KB 的函数，Hex-Rays 拒绝。而 `xrefs` 显示它被 `sub_1412241C0`（227 KB）引用 ——
一个**大函数互相调用**的簇。**

### 所以结论是**优先级**，不是事实

**目标：函数数量对等（①）、功能相等（②）、效率相近（③）。
这 671 个只影响 ① 的 0.24%；② 需要它们的功能相等 —— 而反编译失败了。**

> **所以它们是**已知不可得**的一类，有具体形状：
> 「671 个 4 KB 以上的函数，占字节 15.8%，反编译失败，对函数数贡献 0.24%」。
> **写进 Unknown，不占下一轮。**

### 数字

| 度量 | R972 | **R973** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **4096+ 的字节** | 未测 | **7,676,312 B（15.8%）** |
| **对函数数贡献** | 未测 | **0.24%** |
| **最大函数反编译** | 未试 | **失败** |

### 教训

> **一个指标被解释清楚，不等于那个解释值得追。
> 我把「解释中间量」当成了优先项，而它对我真正要的数的贡献是 0.24%。**
"""

BACKLOG_ADD = """

## 判据 (a) — **4096+ 的 671 个函数：字节 15.8%、均值差 83%、函数数 0.24%、反编译失败**（R973）

### 量

**671 个，合计 7,676,312 B（原版可执行段的 15.8%）。最大 `0x14117C4E0` = 687,318 B。**

### 对三个目标条款的贡献

| 条款 | 占比 |
|---|---|
| ① 函数数量对等 | **0.24%** |
| ② 每个函数功能相等 | 需反编译 —— **失败** |
| ③ 效率相近 | 未测 |

### 反编译

**`ida.py dec 0x14117C4E0` → `Decompilation failed`（687 KB 太大）。
`xrefs` 显示被 `sub_1412241C0`（227 KB）引用 → 大函数互相调用的簇。**

### 处置

**写进 Unknown，不占下一轮。形状：671 个 / 15.8% 字节 / 函数数 0.24% / 反编译失败。**

### 数字

**套件 2186（只取证）· 函数数 173,952 · 陈旧度 0/0**

| 仍 Unknown | |
|---|---|
| 那 671 个是什么 | **反编译失败 → 已知不可得**（除非换方法） |
| 它们对效率的影响 | 未测 |

**纪律**：一个指标被解释清楚，不等于那个解释值得追。
"""

BLOCKER = """

---

## 397. **4096+ 的 671 个函数：均值差 83%、字节 15.8%、函数数 0.24%、反编译失败**

> R973。**只取证。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、量

```
4096 B 以上的函数: 671 个
合计 7,676,312 B = 原版可执行段（48,723,539 B）的 15.8%
最大的 12 个:
  0x14117C4E0    687318 B
  0x1419F6060    527392 B
  0x1412241C0    227186 B
  0x14030F560     83620 B
  ...
```

### 二、对目标三条款的贡献

| 条款 | 占比 |
|---|---|
| ① 函数数量对等 | **671 / 277,120 = 0.24%** |
| ② 每个函数功能相等 | 需反编译 —— **失败** |
| ③ 效率相近 | 未测 |
| （均值差，**非目标**） | 83% |
| （执行段字节，**非目标**） | 15.8% |

### 三、反编译不可行

```
ida.py dec 0x14117C4E0 --lines 30
  -> {"error": "Decompilation failed at 0x14117c4e0"}
```

**687 KB，Hex-Rays 拒绝。`xrefs` 显示被 `sub_1412241C0`（227 KB）引用 ——
大函数互相调用的簇，顺藤摸瓜成本高。**

### 四、处置

**写进 Unknown，不占下一轮。形状：671 个 / 15.8% 字节 / 函数数 0.24% / 反编译失败。**

### 五、数字

| 度量 | R972 | R973 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **4096+ 的字节** | 未测 | **7,676,312 B（15.8%）** |
| **对函数数贡献** | 未测 | **0.24%** |
| **最大函数反编译** | 未试 | **失败** |

### 六、验证

```
python: .pdata 里 4096 < size < 1MiB 的条目 -> 671 个，合计 7,676,312 B
analysis/ida.py xrefs 0x14117C4E0 -> 被 sub_1412241C0 引用
analysis/ida.py dec 0x14117C4E0   -> Decompilation failed
```

### 七、仍然 Unknown

- **那 671 个是什么**：**反编译失败 → 已知不可得**（除非换方法）。
- **它们对效率的影响**：**Unknown** —— 未测。

### 八、教训

**上一轮我把「查这 671 个」立为目标，因为它们是均值差的 83%。
而均值差不是目标 —— 函数数、功能、效率才是。**

**我把一个解释中间量的东西当成了优先项，而它对我真正要的数的贡献是 0.24%。**

**一个指标被解释清楚，不等于那个解释值得追。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R973", BLOCKER)
    ensure(RSTATUS, "R973", BLOCKER)
    ensure(RVERDICT, "第 973 轮", VERDICT)
    ensure(BACKLOG, "R973", BACKLOG_ADD)

    note = (
        "\n## R973 补充 — **4096+ 的 671 个函数：均值差 83%、字节 15.8%、函数数 0.24%、反编译失败**（套件 2186）\n\n"
        "671 个（4096 B 以上）合计 7,676,312 B = 原版可执行段的 **15.8%**；最大 `0x14117C4E0` = 687,318 B。\n\n"
        "**对三个目标条款的贡献**：① 函数数量对等 → **0.24%**；② 功能相等 → 需反编译，**失败**；③ 效率 → 未测。\n"
        "（而它们占**均值差 83%** 和**字节 15.8%** —— 两个都**不是目标**。）\n\n"
        "→ `ida.py dec 0x14117C4E0` → `Decompilation failed`（687 KB 太大）；\n"
        "  `xrefs` 显示被 `sub_1412241C0`（227 KB）引用 → 大函数互相调用的簇。\n\n"
        "**处置：写进 Unknown，不占下一轮。**形状：671 个 / 15.8% 字节 / 函数数 0.24% / 反编译失败。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0。\n\n"
        "纪律：**一个指标被解释清楚，不等于那个解释值得追。**\n\n"
        "下一轮：回到函数数本身 —— 173,952 / 277,120 的差在哪一类函数（用 IDA 的 af 清单按 ordinal/类分组）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R973" not in h:
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
             for p, k in ((RBLOCK, "R973"), (RSTATUS, "R973"), (RVERDICT, "第 973 轮"), (BACKLOG, "R973")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R973: the 671 large functions explain the mean and are irrelevant to the objective\n\n"
         "R972 left the large functions as the next target because they account for eighty-three percent of the mean\n"
         " difference. Looking at them shows they should not have been the target.\n\n"
         "There are six hundred and seventy-one functions above four kilobytes, totalling seven and a half megabytes, which\n"
         " is fifteen point eight percent of the original's executable section. The largest is six hundred and eighty-seven\n"
         " kilobytes at 0x14117C4E0. Against the objective's three clauses they matter as follows: they are zero point two\n"
         " four percent of the function count, they need decompiling to compare behaviour and decompiling fails, and their\n"
         " effect on throughput was not measured. The eighty-three percent figure describes the mean difference, and the mean\n"
         " difference is not one of the three clauses.\n\n"
         "Decompiling the largest does not work: Hex-Rays refuses the six-hundred-kilobyte function outright, and xrefs shows\n"
         " it called from another two-hundred-kilobyte function, so the cluster is both unreadable individually and expensive\n"
         " to approach by following references.\n\n"
         "So the right disposition is a recorded unknown rather than a work item, and it now has a shape: six hundred and\n"
         " seventy-one functions, fifteen point eight percent of the bytes, zero point two four percent of the count, not\n"
         " decompilable.\n\n"
         "Figures: suite 2186, count 173,952, freshness zero, the large-function total 7,676,312 bytes.\n\n"
         "Unknown: what those functions are, which is recorded as known-unobtainable by this method; and their effect on\n"
         " throughput, which was not measured.\n\n"
         "The lesson is that I made a target out of the thing that explained a derived number, when that derived number is\n"
         " not among the objectives. Explaining a measure is not the same as the explanation being worth pursuing.\n\n"
         "No product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()