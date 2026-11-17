"""Record R969: the gap has a shape, and the shape is that the replica's code simply ends."""

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
### 缺口有形状了，而形状是：**复刻件的代码在 0x1C00000 就结束了**（R969）

**R968 说下一轮要的是**分布**，不是另一个候选原因。写了 `tools/pdata_sections.py`，
把两边 `.pdata` 按 1 MiB 分桶：**

```
range from     original   replica    replica/original
0x0            5,475      2,022        36.9%
0x100000       5,089      4,814        94.6%
0x200000       4,333      5,321       122.8%
0x600000       1,074      3,412       317.7%
0x1100000      2,020      9,969       493.5%
0x1200000      2,046      9,730       475.6%
0x1700000      2,242      9,974       444.9%
0x1B00000      6,033      4,683        77.6%
─────────────── 这里以下 ends ───────────────
0x1C00000      6,218      0             0.0%
0x1D00000      6,893      0             0.0%
  ...（到 0x3100000 全是 0）
0x2500000     13,982      0             0.0%
0x3100000        324      0             0.0%
```

### 所以两件事，都很直白

**① 0x0 到 0x1B00000：复刻件**不缺，甚至多**。
好几段是原版的 1.5 到 4.9 倍 —— 那是 Avalonia 与不同的 BCL 在低地址段的体量。**

**② 0x1C00000 到 0x3100000：复刻件是 **0**。原版在那一段有约 **10 万**个函数。**

> **而 103,168 这个缺口，几乎全部就是那一段。**
> **所以缺口**不是「某类函数缺失」，而是「复刻件的 .text 在那之后就没了」。****

### 而这意味着什么

**原版的代码段约 0x0..0x3100000（49 MB 地址空间），复刻件约 0x0..0x1C00000（28 MB）。
差的那 21 MB 里装着 10 万个函数。**

> **所以「1:1 复刻」在体量上现在是一个**整体差 1.75 倍**的问题，
> 而不是「A 站缺了 B 步骤」那类问题。而这两类问题需要完全不同的动作：
> **前者要问「原版那 21 MB 里是什么」，后者要问「哪个站缺哪步」。****

### 而这个工具**不能**说的是

**两个镜像的布局是独立的 —— 同一个桶里数字相同**不**代表同一段代码。
所以这张表说的是**密度**，不是**身份**。而「21 MB 里是什么」这个问题的答案不在这张表里。**

> **它给出的是**下一步该问什么**，不是答案本身。**

### 而这一轮也说明了「候选原因」这个做法的问题

**R966 猜「派发表在 AOT 下失效」，R967 用 UTF-8 推翻了它。
R968 承认核对到头了，R969 改用分布 —— 而分布一出来，那个候选原因**根本不需要**：
**缺口在 0x1C00000 以上，而那不是「派发失效」的形状，「派发失效」会均匀砍掉一批。****

> **一个候选原因被**形状**否掉，比被另一个候选原因否掉可靠。**
> **而形状来自分布 —— 我一个上午在猜，而一个 47 行的桶统计直接给出了它。****

### 数字

| 度量 | R968 | **R969** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **复刻件 .text 上界** | 未测 | **0x1C00000（28 MB）** |
| **原版 .text 上界** | 未测 | **0x3100000（49 MB）** |
| **0x1C00000 以上的原版函数** | 未测 | **约 10 万，复刻件 0** |

### 教训

> **我一个上午在猜「为什么少」，而一个 47 行的桶统计直接给出了「少在哪」，
> 而「少在哪」把「为什么少」的候选原因全部换掉了。**
> **而更值钱的是：形状否掉候选原因比候选原因互相否掉可靠 ——
> 「派发失效」会均匀砍一批，而实际是**从某个地址起归零**，那不是同一件事。**
"""

if "缺口有形状了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 969 轮：缺口有形状了 —— 复刻件的代码在 0x1C00000 就结束了

### 工具

**`tools/pdata_sections.py`（47 行逻辑，复用 `func_count.py` 的 PE 解析而非写第二个解析器）
把两边 `.pdata` 按 1 MiB 分桶。**

### 结果

```
0x0          5,475 → 2,022      36.9%
0x1100000    2,020 → 9,969     493.5%
0x1200000    2,046 → 9,730     475.6%
0x1700000    2,242 → 9,974     444.9%
──────────── 复刻件在这里结束 ────────────
0x1C00000    6,218 → 0           0.0%
0x2500000   13,982 → 0           0.0%
0x3100000      324 → 0           0.0%
```

### 两件事

**① 0x0..0x1B00000：复刻件**不缺，甚至多**（1.5 到 4.9 倍）—— Avalonia 与不同 BCL 的体量。**

**② 0x1C00000..0x3100000：复刻件 **0**，原版约 **10 万**个函数。**

> **103,168 这个缺口几乎全部就是那一段。
> 所以缺口**不是「某类函数缺失」**，是「复刻件的 .text 在那之后就没了」。**

### 这意味着什么

**原版代码段 0x0..0x3100000（49 MB），复刻件 0x0..0x1C00000（28 MB）。
差的 21 MB 装着 10 万个函数。**

> **「1:1 复刻」在体量上现在是一个**整体差 1.75 倍**的问题，
> 而不是「A 站缺 B 步骤」那类问题。两类问题需要完全不同的动作。**

### 工具不能说的

**两镜像布局独立 —— 同桶数字相同**不**代表同一段代码。这张表说的是**密度**，不是**身份**。
「21 MB 里是什么」不在这张表里。**

### 而这一轮也说明「候选原因」这个做法的问题

**R966 猜「派发失效」→ R967 用 UTF-8 推翻 → R968 承认核对到头 → R969 用分布。
而分布一出来，那个候选**根本不需要**：缺口在 0x1C00000 以上，
而「派发失效」会**均匀**砍一批 —— 不是**从某地址起归零**。**

> **一个候选原因被**形状**否掉，比被另一个候选否掉可靠。**

### 数字

| 度量 | R968 | **R969** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **复刻件 .text 上界** | 未测 | **0x1C00000（28 MB）** |
| **原版 .text 上界** | 未测 | **0x3100000（49 MB）** |
| **0x1C00000 以上** | 未测 | **原版约 10 万，复刻件 0** |

### 教训

> **我一个上午在猜「为什么少」，而 47 行桶统计直接给出了「少在哪」，
> 而「少在哪」把「为什么少」的候选原因全部换掉了。**
"""

BACKLOG_ADD = """

## 判据 (c) — **缺口分布：复刻件代码在 0x1C00000 结束**（R969，**+1 工具**）

### 工具

**`tools/pdata_sections.py --bucket 0x100000`（默认 1 MiB），复用 `func_count.py` 的 PE 解析**

### 分布

**0x0..0x1B00000：复刻件 1.5-4.9 倍于原版（不缺）**
**0x1C00000..0x3100000：复刻件 **0**，原版约 **10 万****

**复刻件 .text ≈ 28 MB；原版 ≈ 49 MB；差 21 MB 里装 10 万函数。**

### 结论

**缺口**不是「某类函数缺失**，是**整体体量差 1.75 倍**。**
**R966 的「派发失效」候选被**形状**否掉（那会均匀砍，不会从某地址起归零）。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0**

| 仍 Unknown | |
|---|---|
| 原版那 21 MB 里是什么 | 分布表答不了（布局独立，不是身份） |
| 哪些是 Avalonia/BCL 体量差、哪些是真缺口 | 需按名字而非地址对照 |

**纪律**：候选原因被形状否掉，比被另一个候选否掉可靠。
"""

BLOCKER = """

---

## 393. **缺口形状：复刻件代码在 0x1C00000 结束，原版到 0x3100000**

> R969。**新增一个工具，未改产品代码。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、工具

**`tools/pdata_sections.py`：把两边 `.pdata` 按 1 MiB 分桶（`--bucket` 可调）。
复用 `func_count.py` 的 PE 解析 —— 两个会互相矛盾的解析器比一个更该调试。**

### 二、分布

| 区间 | 原版 | 复刻件 | 比 |
|---|---|---|---|
| 0x0 | 5,475 | 2,022 | 36.9% |
| 0x1100000 | 2,020 | 9,969 | 493.5% |
| 0x1200000 | 2,046 | 9,730 | 475.6% |
| 0x1700000 | 2,242 | 9,974 | 444.9% |
| 0x1B00000 | 6,033 | 4,683 | 77.6% |
| **0x1C00000** | **6,218** | **0** | **0.0%** |
| 0x2500000 | 13,982 | 0 | 0.0% |
| 0x3100000 | 324 | 0 | 0.0% |

### 三、结论

**① 0x0..0x1B00000 复刻件不缺甚至更多（1.5-4.9 倍）—— Avalonia 与不同 BCL。**
**② 0x1C00000 以上复刻件是 0，原版约 10 万函数。**

**→ 103,168 的缺口几乎全部就是那一段。缺口**不是「某类函数缺失」，
是「复刻件的 .text 在那之后就没了」。****

**复刻件 .text ≈ 28 MB；原版 ≈ 49 MB；差 21 MB 里装 10 万函数 → 整体体量差 1.75 倍。**

### 四、R966 的候选被形状否掉

**「派发失效」会**均匀**砍一批；而实际是**从某地址起归零**。那不是同一件事。**

**→ 候选原因被**形状**否掉，比被另一个候选否掉可靠。**

### 五、工具不能说的

**两镜像布局独立 —— 同桶数字相同不代表同一段代码。这张表说的是**密度**，不是**身份**。
「21 MB 里是什么」不在这张表里。**

### 六、数字

| 度量 | R968 | R969 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **复刻件 .text 上界** | 未测 | **0x1C00000** |
| **原版 .text 上界** | 未测 | **0x3100000** |

### 七、验证

```
cd replica
python tools/pdata_sections.py
  -> 0x1C00000 起 replica 列全为 0
  -> 1C00000 以上原版合计约 10 万
```

### 八、仍然 Unknown

- **原版那 21 MB 里是什么**：**Unknown** —— 分布表答不了（布局独立，不是身份）。
- **哪些是 Avalonia/BCL 体量差、哪些是真缺口**：**Unknown** —— 需按名字而非地址对照。

### 九、教训

**我一个上午在猜「为什么少」，而 47 行桶统计直接给出了「少在哪」，
而「少在哪」把「为什么少」的候选原因全部换掉了。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R969", BLOCKER)
    ensure(RSTATUS, "R969", BLOCKER)
    ensure(RVERDICT, "第 969 轮", VERDICT)
    ensure(BACKLOG, "R969", BACKLOG_ADD)

    note = (
        "\n## R969 补充 — **缺口分布：复刻件代码在 0x1C00000 结束**（+1 工具，套件 2186）\n\n"
        "写了 `tools/pdata_sections.py`（复用 func_count.py 的 PE 解析），两边 .pdata 按 1 MiB 分桶：\n\n"
        "**0x0..0x1B00000：复刻件不缺甚至更多（1.5-4.9 倍）** —— Avalonia 与不同 BCL 的体量；\n"
        "**0x1C00000..0x3100000：复刻件 0，原版约 10 万函数。**\n\n"
        "→ 103,168 的缺口几乎全部就是那一段。**缺口不是「某类函数缺失」，是「复刻件的 .text 在那之后就没了」。**\n"
        "→ 复刻件 .text ≈ 28 MB，原版 ≈ 49 MB，差 21 MB 装 10 万函数 → **整体体量差 1.75 倍**。\n\n"
        "→ **R966 的「派发失效」候选被形状否掉**：那会均匀砍，不会从某地址起归零。\n"
        "   候选原因被**形状**否掉比被另一个候选否掉可靠。\n\n"
        "工具不能说的：两镜像布局独立，同桶数字不代表同一段代码 —— 说的是**密度**不是**身份**。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 复刻件 .text 上界 0x1C00000 · 原版 0x3100000。\n\n"
        "纪律：一个上午在猜「为什么少」，47 行桶统计直接给出「少在哪」，而它把候选原因全换了。\n\n"
        "下一轮：查原版 0x1C00000 以上的 10 万个函数**是什么**（用 IDA 按地址段采样函数名/字符串引用），\n"
        "判定那是 BCL/Avalonia 体量差还是真缺口。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R969" not in h:
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
             for p, k in ((RBLOCK, "R969"), (RSTATUS, "R969"), (RVERDICT, "第 969 轮"), (BACKLOG, "R969")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R969: the gap has a shape -- the replica's code simply ends at 0x1C00000\n\n"
         "R968 established that the body-string check can only be read in the positive direction and left the question of\n"
         " where the missing functions sit. This round added tools/pdata_sections.py, which buckets both .pdata tables by\n"
         " BeginAddress at one mebibyte and compares the histograms. It reuses func_count's PE parsing rather than adding a\n"
         " second parser, because two parsers that disagree are one more thing to debug than one.\n\n"
         "The answer is unusually clean. Below 0x1B00000 the replica is not short at all and is often larger, by factors\n"
         " between one and a half and nearly five, which is Avalonia and a different BCL taking their share. From 0x1C00000\n"
         " the replica is zero in every bucket, while the original carries roughly a hundred thousand functions up to\n"
         " 0x3100000. So the 103,168 gap is almost entirely that one span, and its shape is not a class of functions\n"
         " missing but the replica's text section ending.\n\n"
         "That reframes the objective as a whole. The replica's code occupies about twenty-eight megabytes of address space\n"
         " against the original's forty-nine, and the missing twenty-one hold a hundred thousand functions. The problem is a\n"
         " factor of 1.75 in overall mass, not a list of stores with missing steps, and those two need different work.\n\n"
         "It also disposes of the candidate cause from R966. Dispatch failing under NativeAOT would thin functions evenly\n"
         " across the image; what actually happened is a clean zero from one address upward. A candidate cause killed by a\n"
         " shape is more trustworthy than one killed by another candidate, and the shape took forty-seven lines of bucketing\n"
         " after a morning of guessing.\n\n"
         "What the tool cannot say is what lives in those twenty-one megabytes. The two images are laid out independently, so\n"
         " equal counts in a bucket do not mean the same code; the table reports density and not identity, and it points at\n"
         " the next question rather than answering it.\n\n"
         "Figures: suite 2186, count 173,952, freshness zero, replica text ending at 0x1C00000 against the original's\n"
         " 0x3100000.\n\n"
         "Unknown: what the original's upper twenty-one megabytes contains, which this table cannot show; and how much of the\n"
         " difference is Avalonia and BCL mass rather than a real gap, which needs comparison by name rather than address.\n\n"
         "The lesson is that a distribution answered in forty-seven lines what guessing had failed to answer all morning, and\n"
         " having the shape replaced every candidate explanation at once.\n\n"
         "One tool added; no product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()