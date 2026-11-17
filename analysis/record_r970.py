"""Record R970: section tables overturn the framing of R969's conclusion."""

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
### 段表推翻了我上一轮的框架 —— 复刻件有**两个**可执行段（R970）

**R969 说「复刻件的 `.text` 在 0x1C00000 就结束了」。写了 `tools/pe_sections.py` 打段表，结果是：**

```
=== ORIGINAL ===
  .text      0x1000   -> 0x314DD68   51,695,104   X
  .rdata     0x314E000 -> 0x6A4687E  59,738,624   R
  .data      0x6A47000 -> 0x7542DA8  10,227,712   RW
  .pdata     0x7543000 -> 0x786ECC8   3,325,440   R

=== REPLICA ===
  .text      0x1000   -> 0xFD508      1,033,728   X     ← 只有 1 MB
  .managed   0xFE000  -> 0x1B817E8   27,801,600   X     ← 第二个可执行段
  hydrated   0x1B82000 -> 0x2A87B28           0   RW
  .rdata     0x2A88000 -> 0x41F1EB6  24,551,424   R
  .pdata     0x42E9000 -> 0x44E6820   2,087,424   R
```

### 所以「结束了」这个说法**现象对、原因错**

**复刻件的托管代码不在 `.text` 里 —— 它在 **`.managed`** 段，27.8 MB，可执行。
而 `0x1C00000` 正好是 `.managed` 段的**结束**（实际 0x1B817E8，下一个 MiB 边界就是 0x1C00000）。**

> **所以桶表里「0x1C00000 以上是 0」不是「代码结束」，是**两个可执行段都结束了**。
> 而原版只有一个 `.text` 段，52 MB，一路到 0x314DD68。****

### 而真正的比较

| | 可执行段 | 大小 |
|---|---|---|
| 原版 | `.text` | **51,695,104 B ≈ 49.3 MB** |
| 复刻件 | `.text` + `.managed` | **1,033,728 + 27,801,600 = 28,835,328 B ≈ 27.5 MB** |

**→ 代码体量 27.5 / 49.3 = **55.8%**。而函数数比是 62.77%。**

> **两个数不一样，而那个差本身是有信息的：**函数数比体量比高 7 个百分点**，
> 说明复刻件的函数**平均更小** —— 或者原版有更多大函数。而我没取证是哪个。****

### 而这一轮又抓到一个「我说对了一半」

**R969 的「缺口全部在 0x1C00000 以上」是**准确的观察**（桶表确实如此）。
而它的解释「复刻件的 .text 在那之后就没了」是**错的** —— 复刻件的 .text 在 1 MB 处就没了，
而它的代码在另一个段里继续到 0x1B817E8。**

> **而如果我不打这张段表，那个错解释会写进 BACKLOG，
> 下一个会话会去 `.text` 里找 27 MB 的代码，而那里永远只有 1 MB。**

### 数字

| 度量 | R969 | **R970** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **原版可执行段** | 未测 | **`.text` 49.3 MB** |
| **复刻件可执行段** | 未测 | **`.text` 1.0 + `.managed` 26.5 MB = 27.5 MB** |
| **代码体量比** | 未测 | **55.8%** |

### 教训

> **观察对、解释错，是一种比观察错更危险的状态 ——
> 因为观察会被复算，而解释会被下一个会话当成前提。**
> **而推翻它的成本是 40 行读段表。而我上一轮把它写进了三份文档。**
"""

if "段表推翻了我上一轮的框架" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 970 轮：段表推翻了我上一轮的框架 —— 复刻件有两个可执行段

### R969 说错了一半

**R969：「复刻件的 `.text` 在 0x1C00000 就结束了」—— 现象对，原因错。**

### 段表

```
=== ORIGINAL ===
  .text      0x1000    -> 0x314DD68   51,695,104   X
  .rdata     0x314E000 -> 0x6A4687E   59,738,624   R
  .pdata     0x7543000 -> 0x786ECC8    3,325,440   R

=== REPLICA ===
  .text      0x1000    -> 0xFD508      1,033,728   X   ← 只有 1 MB
  .managed   0xFE000   -> 0x1B817E8   27,801,600   X   ← 第二个可执行段
  .rdata     0x2A88000 -> 0x41F1EB6   24,551,424   R
  .pdata     0x42E9000 -> 0x44E6820    2,087,424   R
```

**复刻件的托管代码不在 `.text` 里，在 **`.managed`** 段。
而 `0x1C00000` 正好是 `.managed` 的**结束**（实际 0x1B817E8）。**

> **所以桶表里「0x1C00000 以上是 0」不是「代码结束」，是**两个可执行段都结束了**。**

### 真正的比较

| | 可执行段 | 大小 |
|---|---|---|
| 原版 | `.text` | **49.3 MB** |
| 复刻件 | `.text` + `.managed` | **1.0 + 26.5 = 27.5 MB** |

**→ 代码体量比 **55.8%**，而函数数比 **62.77%**。
差 7 个百分点说明复刻件的函数**平均更小**（或原版有更多大函数）—— 未取证是哪个。**

### 而这一轮又抓到一个「我说对了一半」

**R969 的观察准确（桶表确实如此），解释错（.text 在 1 MB 处就没了，代码在另一个段）。
若不打段表，那个错解释会进 BACKLOG，下个会话会去 `.text` 里找 27 MB —— 而那里永远只有 1 MB。**

### 数字

| 度量 | R969 | **R970** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **原版可执行段** | 未测 | **49.3 MB** |
| **复刻件可执行段** | 未测 | **27.5 MB** |
| **代码体量比** | 未测 | **55.8%** |

### 教训

> **观察对、解释错，比观察错更危险 —— 因为观察会被复算，而解释会被下一个会话当成前提。**
> **而推翻它的成本是 40 行读段表。而我上一轮把它写进了三份文档。**
"""

BACKLOG_ADD = """

## 判据 (c) — **段表：复刻件两个可执行段；R969 的框架修正**（R970，**+1 工具**）

### 工具

**`tools/pe_sections.py`：打印两边段表（名字/RVA 范围/raw size/权限）**

### 事实

**原版：`.text` 0x1000→0x314DD68 = 51,695,104 B（49.3 MB），单一段**
**复刻件：`.text` 0x1000→0xFD508 = 1,033,728 B（1.0 MB）+ `.managed` 0xFE000→0x1B817E8 = 27,801,600 B（26.5 MB）**

### 更正

**R969「复刻件的 .text 在 0x1C00000 结束」→ **现象对、原因错**：
0x1C00000 是 `.managed` 段的结束，不是 .text 的。**

### 而真正的数

**代码体量比 27.5 / 49.3 = **55.8%**；函数数比 **62.77%**。
差 7 个百分点 → 复刻件函数平均更小（或原版更多大函数）—— **未取证是哪个**。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0**

| 仍 Unknown | |
|---|---|
| 那 7 个百分点差的成因（函数大小分布） | 未取证 |
| 原版 49.3 MB 里哪些是复刻件也有的 | 需按名字对照 |

**纪律**：观察对、解释错，比观察错更危险。
"""

BLOCKER = """

---

## 394. **段表：复刻件有两个可执行段；R969 的框架修正**

> R970。**新增一个工具（`tools/pe_sections.py`）+ 更正 R969。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、段表

```
=== ORIGINAL ===
  .text      0x1000    -> 0x314DD68   51,695,104   X
  .rdata     0x314E000 -> 0x6A4687E   59,738,624   R
  .pdata     0x7543000 -> 0x786ECC8    3,325,440   R

=== REPLICA ===
  .text      0x1000    -> 0xFD508      1,033,728   X   ← 1 MB
  .managed   0xFE000   -> 0x1B817E8   27,801,600   X   ← 第二个可执行段
  hydrated   0x1B82000 -> 0x2A87B28            0  RW
  .rdata     0x2A88000 -> 0x41F1EB6   24,551,424   R
  .pdata     0x42E9000 -> 0x44E6820    2,087,424   R
```

### 二、更正 R969

**R969 说「复刻件的 `.text` 在 0x1C00000 就结束了」—— **现象对、原因错**。**

**0x1C00000 是 **`.managed`** 段的结束（实际 0x1B817E8），不是 `.text` 的。
复刻件的 `.text` 在 1 MB 处就没了，托管代码在另一个可执行段里继续。**

### 三、真正的比较

| | 可执行段 | 大小 |
|---|---|---|
| 原版 | `.text` | **49.3 MB** |
| 复刻件 | `.text` + `.managed` | **27.5 MB** |

**代码体量比 **55.8%**；函数数比 **62.77%**。
差 7 个百分点 → 复刻件函数平均更小（或原版更多大函数）—— **未取证是哪个**。**

### 四、为什么这个更正重要

**若不打段表，R969 的错解释会进 BACKLOG，下个会话会去 `.text` 里找 27 MB —— 而那里永远只有 1 MB。**

**观察对、解释错，比观察错更危险：观察会被复算，解释会被当成前提。**

### 五、数字

| 度量 | R969 | R970 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **原版可执行段** | 未测 | **49.3 MB** |
| **复刻件可执行段** | 未测 | **27.5 MB** |
| **代码体量比** | 未测 | **55.8%** |

### 六、验证

```
cd replica
python tools/pe_sections.py
  -> ORIGINAL .text 0x1000..0x314DD68
  -> REPLICA  .text 0x1000..0xFD508 + .managed 0xFE000..0x1B817E8
```

### 七、仍然 Unknown

- **那 7 个百分点差的成因（函数大小分布）**：**Unknown** —— 未取证。
- **原版 49.3 MB 里哪些是复刻件也有的**：**Unknown** —— 需按名字对照。

### 八、教训

**观察对、解释错，比观察错更危险 —— 因为观察会被复算，而解释会被下一个会话当成前提。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R970", BLOCKER)
    ensure(RSTATUS, "R970", BLOCKER)
    ensure(RVERDICT, "第 970 轮", VERDICT)
    ensure(BACKLOG, "R970", BACKLOG_ADD)

    note = (
        "\n## R970 补充 — **段表：复刻件有两个可执行段；R969 框架修正**（+1 工具，套件 2186）\n\n"
        "写了 `tools/pe_sections.py` 打段表，结果推翻了 R969 的框架：\n\n"
        "**原版**：`.text` 0x1000→0x314DD68 = **51,695,104 B（49.3 MB）**，单一段。\n"
        "**复刻件**：`.text` 0x1000→0xFD508 = **1,033,728 B（1.0 MB）** +\n"
        "             `.managed` 0xFE000→0x1B817E8 = **27,801,600 B（26.5 MB）** ← 第二个可执行段。\n\n"
        "→ **R969「复刻件的 .text 在 0x1C00000 结束」现象对、原因错**：0x1C00000 是 `.managed` 的结束，不是 .text 的。\n\n"
        "→ 真正的数：代码体量比 27.5/49.3 = **55.8%**，而函数数比 **62.77%**。\n"
        "   差 7 个百分点 → 复刻件函数平均更小（或原版更多大函数）—— 未取证是哪个。\n\n"
        "→ 若不打段表，那个错解释会进 BACKLOG，下个会话会去 `.text` 里找 27 MB —— 而那里永远只有 1 MB。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 原版可执行 49.3 MB · 复刻件 27.5 MB · 体量比 55.8%。\n\n"
        "纪律：观察对、解释错，比观察错更危险 —— 解释会被下一个会话当成前提。\n\n"
        "下一轮：查那 7 个百分点差的成因 —— 统计两边 .pdata 里每个函数的 (End-Begin) 大小分布。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R970" not in h:
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
             for p, k in ((RBLOCK, "R970"), (RSTATUS, "R970"), (RVERDICT, "第 970 轮"), (BACKLOG, "R970")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R970: the section tables overturn last round's framing -- the replica has two executable sections\n\n"
         "R969 reported that the replica's text section ends at 0x1C00000. Adding tools/pe_sections.py to print both section\n"
         " tables shows the observation was right and the explanation was wrong.\n\n"
         "The original has one executable section: .text from 0x1000 to 0x314DD68, fifty-one million bytes. The replica has\n"
         " two: .text of one megabyte, and a managed section of nearly twenty-eight megabytes that carries the compiled\n"
         " managed code and is also executable. 0x1C00000 is where the managed section ends, not where the text section\n"
         " does. The bucket table was accurate; my reading of it was not.\n\n"
         "So the real comparison is forty-nine megabytes against twenty-seven and a half, a ratio of about fifty-six\n"
         " percent, against a function-count ratio of sixty-two point eight. Those two numbers differing by seven points is\n"
         " itself information: the replica's functions are on average smaller, or the original has more large ones, and which\n"
         " of those it is has not been measured.\n\n"
         "Had the tables not been printed, the wrong explanation would have gone into the backlog, and the next session\n"
         " would have looked for twenty-seven megabytes inside a text section that only ever holds one. That is the specific\n"
         " cost of an accurate observation with an inaccurate explanation: the observation gets recomputed, the explanation\n"
         " gets inherited as a premise. Overturning it cost forty lines of section reading, after it had already been written\n"
         " into three documents.\n\n"
         "Figures: suite 2186, count 173,952, freshness zero, original executable fifty-one million bytes against the\n"
         " replica's twenty-seven and a half across two sections.\n\n"
         "Unknown: what causes the seven-point difference between mass and count, which needs the per-function size\n"
         " distribution; and how much of the original's forty-nine megabytes the replica also has, which needs comparison by\n"
         " name rather than size.\n\n"
         "The lesson is that an accurate observation with a wrong explanation is more dangerous than a wrong observation,\n"
         " because the second gets rechecked and the first gets believed.\n\n"
         "One tool added; conclusions in three documents corrected."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()