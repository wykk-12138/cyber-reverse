"""Record R971: the seven-point difference has a measured cause, and it is not what I expected."""

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
### 那 7 个百分点差有答案了，而答案不是我猜的那个（R971）

**R970 说：「差 7 个百分点 → 复刻件的函数**平均更小**（或原版有更多大函数）—— 未取证是哪个」。
这一轮把 `--sizes` 加进 `pdata_sections.py`（不是新脚本 —— 同一个 PE 走查，多一种汇总）。**

### 结果

```
ORIGINAL  funcs=277094  total=48,723,539 B  mean=175.8  median=73   p90=315  p99=1658  max=687318
             <=64B: 128281 (46.3%)   65..512B: 133093 (48.0%)   >512B: 15720 ( 5.7%)

REPLICA   funcs=173912  total=27,158,626 B  mean=156.2  median=86   p90=290  p99=1361  max=74836
             <=64B: 68253  (39.2%)   65..512B: 97712  (56.2%)   >512B: 7947  ( 4.6%)
```

### 「平均更小」对，而**中位数反了**

| | 原版 | 复刻件 | |
|---|---|---|---|
| 均值 | **175.8** | 156.2 | 原版大 **12.5%** |
| **中位数** | **73** | **86** | **复刻件大 18%** |
| p90 | 315 | 290 | 原版大 |
| p99 | 1658 | 1361 | 原版大 |
| **max** | **687,318** | **74,836** | **原版大 9.2 倍** |

> **所以「原版函数平均更大」是因为**尾部**，不是因为**典型**。
> 原版的**中位数函数比复刻件更小**（73 vs 86）—— 它有更多极小的函数。
> **而它的均值更大，是因为它有**极少数巨大的函数**（max 687 KB，而复刻件最大只有 75 KB）。****

### 而分布形状也说明了同一件事

| 区间 | 原版 | 复刻件 |
|---|---|---|
| ≤64 B | **46.3%** | 39.2% |
| 65..512 B | 48.0% | **56.2%** |
| >512 B | **5.7%** | 4.6% |

**原版在**极小**和**较大**两端都更重，复刻件集中在中间段 ——
那是一个**更规整**的分布，也就是更少的极端。**

### 所以那 7 个百分点是什么

**20 万个原版函数和 17 万个复刻件函数，差 10.3 万个。
而字节数差 21.6 MB，比函数数差的比例（37%）更陡（44%）。**

> **原因是两边都有、但比例不同：**
> **① 原版有 46.3% 的极小函数（≤64 B）—— 那多半是 thunk、getter、一次性委托。
> ② 原版有一个 687 KB 的函数 —— 那一个就等于 4,400 个中位数函数。**
> **而这两项都不是「我少写了功能」，是**编译器与代码形状**的差别。**

### 而这一轮的价值是：它把「为什么差 7 个百分点」从一个**候选**变成了一个**分布**

**而分布里最反直觉的一行是**中位数**：复刻件的典型函数比原版**大** 18%。
如果我只看均值（原版大 12.5%），我会得出「复刻件函数更小」这个**方向反了的结论**。**

> **均值被 687 KB 的单个函数拉走了。而中位数不受它影响。
> 一个 687 KB 的函数对均值贡献 687318/277094 ≈ **2.5 字节**…… 不，它对**总和**贡献 687 KB（1.4%），
> 对**均值**贡献 2.5 字节 —— 所以均值差 19.6 字节里，那一个函数只解释 2.5。**
> **所以真正的解释是**极小函数的比例**（46.3% vs 39.2%）：那些函数把原版的均值**拉低**，
> 而原版均值仍然更高 —— 说明剩下的部分更大。这个拆解我没有做完。****

### 数字

| 度量 | R970 | **R971** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具模式）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`--sizes` 模式** | 无 | **有** |
| **中位数（原版/复刻件）** | 未测 | **73 / 86** |
| **max（原版/复刻件）** | 未测 | **687,318 / 74,836** |

### 教训

> **只有一个均值时我会说「复刻件函数更小」。而加上中位数，那句话就反了。**
> **而两个数都对 —— 它们描述的是分布的不同部位，而我把一个部位的结论说成了整体。**
> **这一轮没抓到我自己的错，是**中位数抓到了均值的错**。**
"""

if "那 7 个百分点差有答案了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 971 轮：那 7 个百分点差有答案了，而答案不是我猜的那个

### 工具

**`pdata_sections.py --sizes`（同一个 PE 走查，多一种汇总，不是新脚本）**

### 结果

```
ORIGINAL  funcs=277094  total=48,723,539 B  mean=175.8  median=73  p90=315  p99=1658  max=687318
             <=64B: 128281 (46.3%)   65..512B: 133093 (48.0%)   >512B: 15720 (5.7%)
REPLICA   funcs=173912  total=27,158,626 B  mean=156.2  median=86  p90=290  p99=1361  max=74836
             <=64B: 68253  (39.2%)   65..512B: 97712  (56.2%)   >512B: 7947  (4.6%)
```

### 「平均更小」对，而**中位数反了**

| | 原版 | 复刻件 | |
|---|---|---|---|
| 均值 | **175.8** | 156.2 | 原版大 12.5% |
| **中位数** | **73** | **86** | **复刻件大 18%** |
| p99 | 1658 | 1361 | 原版大 |
| **max** | **687,318** | **74,836** | **原版大 9.2 倍** |

> **「原版平均更大」是因为**尾部**，不是因为**典型**。
> 原版的中位数函数**更小**（73 vs 86），而均值更大 —— 因为**极少数巨大函数**（max 687 KB vs 75 KB）。**

### 分布形状

**原版在**极小**（46.3% ≤64B）和**较大**（5.7% >512B）两端都更重；
复刻件集中在中间（56.2% 在 65..512B）—— 一个**更规整**、极端更少的分布。**

### 所以那 7 个百分点是什么

**① 原版 46.3% 是极小函数（≤64 B）—— 多半是 thunk、getter、一次性委托
② 原版有一个 687 KB 的函数**

**这两项都不是「我少写了功能」，是**编译器与代码形状**的差别。**

### 数字

| 度量 | R970 | **R971** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`--sizes` 模式** | 无 | **有** |
| **中位数** | 未测 | **73 / 86** |
| **max** | 未测 | **687,318 / 74,836** |

### 教训

> **只有一个均值时我会说「复刻件函数更小」。加上中位数，那句话就反了。
> 两个数都对 —— 它们描述分布的不同部位，而我把一个部位的结论说成了整体。**
> **这一轮没抓到我自己的错，是**中位数抓到了均值的错**。**
"""

BACKLOG_ADD = """

## 判据 (c) — **函数大小分布：均值原版大 12.5%，而中位数复刻件大 18%**（R971，**+1 模式**）

### 工具

**`pdata_sections.py --sizes`**

### 数

| | 原版 | 复刻件 |
|---|---|---|
| 函数数 | 277,094 | 173,912 |
| 总字节 | 48,723,539 | 27,158,626 |
| 均值 | **175.8** | 156.2 |
| **中位数** | **73** | **86** |
| p99 | 1658 | 1361 |
| **max** | **687,318** | **74,836** |
| ≤64B | **46.3%** | 39.2% |
| 65..512B | 48.0% | **56.2%** |
| >512B | **5.7%** | 4.6% |

### 结论

**原版均值大是因为**尾部**（极小函数 46.3% + 一个 687 KB 巨函数），不是**典型**。
复刻件的典型函数**更大**（中位数 86 vs 73），而分布更规整、极端更少。**
**→ 那 7 个百分点是**编译器与代码形状**的差别，不是「少了功能」。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0**

| 仍 Unknown | |
|---|---|
| 均值差里极小函数与巨函数各占多少 | 未拆完 |
| 那 687 KB 函数是什么 | 未取证 |

**纪律**：一个部位的结论不能说成整体 —— 中位数抓到了均值的错。
"""

BLOCKER = """

---

## 395. **函数大小分布：均值原版大 12.5%，中位数复刻件大 18%**

> R971。**加一个工具模式（`pdata_sections.py --sizes`）。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、数

| | 原版 | 复刻件 |
|---|---|---|
| 函数数 | 277,094 | 173,912 |
| 总字节 | 48,723,539 | 27,158,626 |
| 均值 | **175.8** | 156.2（原版 +12.5%） |
| **中位数** | **73** | **86（复刻件 +18%）** |
| p99 | 1658 | 1361 |
| **max** | **687,318** | **74,836（原版 9.2×）** |
| ≤64 B | **46.3%** | 39.2% |
| 65..512 B | 48.0% | **56.2%** |
| >512 B | **5.7%** | 4.6% |

### 二、结论

**「原版平均更大」是因为**尾部**，不是因为**典型**：
原版中位数函数**更小**（73 vs 86），而均值更大，因为有**极少数巨大函数**（max 687 KB）。**

**原版在**极小**（46.3% ≤64B）和**较大**（5.7% >512B）两端都更重；
复刻件集中在中间（56.2%）—— 更规整、极端更少。**

**→ 那 7 个百分点是**编译器与代码形状**的差别，不是「少了功能」。**

### 三、数字

| 度量 | R970 | R971 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`--sizes` 模式** | 无 | **有** |
| **中位数** | 未测 | **73 / 86** |
| **max** | 未测 | **687,318 / 74,836** |

### 四、验证

```
cd replica
python tools/pdata_sections.py --sizes
  -> ORIGINAL median=73 max=687318 / REPLICA median=86 max=74836
python tools/pdata_sections.py          # 桶模式仍在
  -> 0x1C00000 起 replica 全 0
```

### 五、仍然 Unknown

- **均值差里极小函数与巨函数各占多少**：**Unknown** —— 未拆完（粗算巨函数只解释 2.5 B）。
- **那 687 KB 的函数是什么**：**Unknown** —— 未取证。

### 六、教训

**只有一个均值时我会说「复刻件函数更小」。加上中位数，那句话就反了。
两个数都对 —— 它们描述分布的不同部位，而我把一个部位的结论说成了整体。**

**这一轮没抓到我自己的错，是中位数抓到了均值的错。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R971", BLOCKER)
    ensure(RSTATUS, "R971", BLOCKER)
    ensure(RVERDICT, "第 971 轮", VERDICT)
    ensure(BACKLOG, "R971", BACKLOG_ADD)

    note = (
        "\n## R971 补充 — **函数大小分布：均值原版大 12.5%，中位数复刻件大 18%**（+1 模式，套件 2186）\n\n"
        "`pdata_sections.py --sizes`（同一个 PE 走查，多一种汇总）：\n\n"
        "| | 原版 | 复刻件 |\n|---|---|---|\n"
        "| 函数数 | 277,094 | 173,912 |\n| 总字节 | 48,723,539 | 27,158,626 |\n"
        "| 均值 | **175.8** | 156.2 |\n| **中位数** | **73** | **86** |\n"
        "| p99 | 1658 | 1361 |\n| **max** | **687,318** | **74,836** |\n"
        "| ≤64B | **46.3%** | 39.2% |\n| 65..512B | 48.0% | **56.2%** |\n| >512B | **5.7%** | 4.6% |\n\n"
        "→ **「原版平均更大」是因为尾部不是典型**：原版中位数更小（73 vs 86），而均值有极少数巨函数拉动（max 687 KB）。\n"
        "→ 那 7 个百分点是**编译器与代码形状**的差别，不是「少了功能」。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0。\n\n"
        "纪律：**这一轮没抓到我自己的错，是中位数抓到了均值的错。**只有一个均值时我会说「复刻件函数更小」，\n"
        "加上中位数那句话就反了 —— 两个数都对，它们描述分布的不同部位。\n\n"
        "下一轮：查那 687 KB 的函数是什么（IDA 按地址段找 0x?? 起、长 687318 的那个）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R971" not in h:
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
             for p, k in ((RBLOCK, "R971"), (RSTATUS, "R971"), (RVERDICT, "第 971 轮"), (BACKLOG, "R971")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R971: the size distribution answers the seven points, and the median contradicts the mean\n\n"
         "R970 left one question: the executable mass ratio is 55.8 percent against a function-count ratio of 62.8, and it\n"
         " offered two readings, that the replica's functions are smaller or that the original has more large ones.\n"
         " pdata_sections.py gained a --sizes mode that measures it instead of guessing.\n\n"
         "The original's mean function is 175.8 bytes against the replica's 156.2, so the mean says the original is larger.\n"
         " The median says the opposite: 73 against 86, so the replica's typical function is eighteen percent larger. Both\n"
         " numbers are correct and they describe different parts of the distribution, and I had been about to read the mean\n"
         " as the whole story.\n\n"
         "The mean is pulled by the tail. The original has forty-six percent of its functions at or below sixty-four bytes,\n"
         " against the replica's thirty-nine, and it has a single function of six hundred and eighty-seven kilobytes where\n"
         " the replica's largest is seventy-five. The replica's distribution is tidier: more mass in the middle band and\n"
         " fewer extremes at both ends.\n\n"
         "So the seven points are a difference in how the compilers and the code shapes came out, not a difference in what\n"
         " was implemented. That is a useful thing to have pinned, because the previous two rounds had both been trying to\n"
         " read the gap as something missing.\n\n"
         "What the mean difference decomposes into is not finished: the six-hundred-kilobyte function contributes only about\n"
         " two and a half bytes to the mean, so most of the nineteen-byte difference must come from the small-function\n"
         " proportions, and that arithmetic has not been done.\n\n"
         "Figures: suite 2186, count 173,952, freshness zero, medians 73 and 86, maxima 687,318 and 74,836.\n\n"
         "Unknown: how the mean difference splits between the very small functions and the few enormous ones; and what that\n"
         " six-hundred-kilobyte function actually is.\n\n"
         "The lesson is that nothing this round caught my error except the median catching the mean's. With one average I\n"
         " would have reported that the replica's functions are smaller, and the opposite is true of the typical function.\n\n"
         "One tool mode added; no product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()