"""Record R972: the decomposition contradicts R971's own rough arithmetic."""

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
### 拆解做完，而它**推翻了 R971 自己的粗算**（R972）

**R971 写：「均值差 19.6 字节里，那个 687 KB 函数只解释 2.5 字节，所以大部分差来自极小函数的比例」。
这一轮写了 `tools/pdata_decompose.py` 把它算出来，而那个说法是**错的**。**

### 拆解（总和精确匹配 19.67 B）

```
band (B)         original n / share     replica n / share      contribution
0..32            76496 /  27.6%         36642 /  21.1%         +1.01 B
32..64           51785 /  18.7%         31611 /  18.2%         +0.20 B
64..128          65263 /  23.6%         53137 /  30.6%         -7.46 B
128..256         46312 /  16.7%         31869 /  18.3%         -3.37 B
256..512         21518 /   7.8%         12706 /   7.3%         +1.00 B
512..1024         9914 /   3.6%          5083 /   2.9%         +4.84 B
1024..4096        5135 /   1.9%          2598 /   1.5%         +7.04 B
4096..1048576      671 /   0.2%           266 /   0.2%        +16.40 B
─────────────────────────────────────────────────────────────────────
total                                                        +19.67 B
```

### 所以那 19.67 B 在哪

| 来源 | 贡献 | 占比 |
|---|---|---|
| **4096 B 以上那 671 个 vs 266 个** | **+16.40 B** | **83%** |
| 1024..4096 | +7.04 B | 36% |
| 512..1024 | +4.84 B | 25% |
| 64..256 两档（复刻件占比更高） | **−10.83 B** | −55% |
| 其余 | +2.21 B | 11% |

> **所以 R971 的「那 687 KB 函数只解释 2.5 字节」**对那**一个**函数是对的，
> 而对**那一档 671 个函数**是错的 —— 它们合起来解释 83% 的均值差。**
> **而 R971 的下一步推断「大部分差来自极小函数的比例」也错：
> 极小函数两档合计只 +1.21 B，而 64..256 两档是**负的**。****

### 而这一轮**自己**也撞了一次「说一套做一套」

**我在 `pdata_decompose.py` 的文件头写了「goes into the same tool as a third mode rather than into another script」，
然后把它写成了一个独立脚本。**

> **改正了文件头，并写出**真实理由**：拆解需要**固定**的档边界（档宽要对上被比较的区间），
> 而 `pdata_sections` 取的是**一个统一桶宽**（回答另一个问题）。
> 让一个文件服务两者，意味着两套不可互换的参数 —— 所以两个脚本共享同一段走查是对的安排，而文件头现在这么说。**
> **而如果我不改，那个文件头就是一条**自己反驳自己的注释**，而下一个读者会以为我漏了一个模式。****

### 数字

| 度量 | R971 | **R972** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **拆解总和** | 未做 | **+19.67 B（精确匹配）** |
| **4096+ 档的贡献** | 「2.5 B」**错** | **+16.40 B（83%）** |

### 教训

> **R971 那个「2.5 字节」是我心算的，而且在同一段里就写出了「所以大部分差来自极小函数的比例」这个结论。
> 而正确的分配是**大函数占 83%，极小函数那部分甚至是负的**。**
> **一个心算的数字，比没有数字更危险 —— 因为它看起来已经被算过了。**
"""

if "拆解做完，而它**推翻了 R971 自己的粗算**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 972 轮：拆解做完，而它推翻了 R971 自己的粗算

### R971 说错了

**R971：「那 687 KB 函数只解释 2.5 字节，所以大部分差来自极小函数的比例」。
写了 `tools/pdata_decompose.py` 算出来 —— **那个说法是错的**。**

### 拆解（总和精确匹配 19.67 B）

```
0..32         27.6% → 21.1%    +1.01 B
32..64        18.7% → 18.2%    +0.20 B
64..128       23.6% → 30.6%    -7.46 B
128..256      16.7% → 18.3%    -3.37 B
256..512       7.8% →  7.3%    +1.00 B
512..1024      3.6% →  2.9%    +4.84 B
1024..4096     1.9% →  1.5%    +7.04 B
4096..1MB      0.2% →  0.2%   +16.40 B
──────────────────────────────────────
total                         +19.67 B
```

### 所以 19.67 B 在哪

| 来源 | 贡献 | 占比 |
|---|---|---|
| **4096 B 以上的 671 vs 266 个** | **+16.40 B** | **83%** |
| 1024..4096 | +7.04 B | 36% |
| 512..1024 | +4.84 B | 25% |
| **64..256 两档（复刻件占比更高）** | **−10.83 B** | −55% |

> **R971 的「687 KB 函数只解释 2.5 字节」对那**一个**函数对，
> 对**那一档 671 个**错 —— 它们合起来解释 83%。**
> **而「大部分差来自极小函数比例」也错：极小两档合计 +1.21 B，64..256 两档是**负的**。**

### 而这一轮自己也撞了一次「说一套做一套」

**文件头写「goes into the same tool as a third mode rather than into another script」，然后写成了独立脚本。**

> **改正了文件头并写出真实理由：拆解需要**固定**档边界，而 `pdata_sections` 取**统一桶宽**（回答另一个问题）。
> 两套不可互换的参数 → 两个脚本共享同一段走查是对的安排。**

### 数字

| 度量 | R971 | **R972** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **拆解总和** | 未做 | **+19.67 B（精确匹配）** |
| **4096+ 档贡献** | 「2.5 B」错 | **+16.40 B（83%）** |

### 教训

> **那个「2.5 字节」是我心算的，而同一段里就写出了「所以大部分差来自极小函数」这个结论。
> 正确的分配是大函数占 83%，极小那部分甚至是负的。**
> **一个心算的数字，比没有数字更危险 —— 因为它看起来已经被算过了。**
"""

BACKLOG_ADD = """

## 判据 (c) — **均值差拆解：4096 B 以上那档贡献 83%**（R972，**+1 工具**）

### 工具

**`tools/pdata_decompose.py`（固定档边界；与 `pdata_sections.py` 共享同一段 PE 走查）**

### 拆解（总和精确匹配 19.67 B）

| 档（B） | 原版占比 | 复刻件占比 | 贡献 |
|---|---|---|---|
| 0..32 | 27.6% | 21.1% | +1.01 B |
| 32..64 | 18.7% | 18.2% | +0.20 B |
| **64..128** | 23.6% | 30.6% | **−7.46 B** |
| **128..256** | 16.7% | 18.3% | **−3.37 B** |
| 256..512 | 7.8% | 7.3% | +1.00 B |
| 512..1024 | 3.6% | 2.9% | +4.84 B |
| **1024..4096** | 1.9% | 1.5% | **+7.04 B** |
| **4096..1MB** | 0.2%（671） | 0.2%（266） | **+16.40 B（83%）** |

### 更正 R971

**R971「687 KB 函数只解释 2.5 B，大部分差来自极小函数比例」→ **错**。
4096+ 那档 671 个函数合起来解释 **83%**；极小两档只 +1.21 B，64..256 是**负的**。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0**

| 仍 Unknown | |
|---|---|
| 那 671 个大函数是什么 | 未取证 |
| 复刻件在 64..256 占比更高是好事还是坏事 | 未判 |

**纪律**：心算的数字比没有数字更危险 —— 它看起来已经被算过了。
"""

BLOCKER = """

---

## 396. **均值差拆解：4096 B 以上那档贡献 83%；R971 的粗算错**

> R972。**新增工具（`tools/pdata_decompose.py`）。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、拆解（总和精确匹配 19.67 B）

| 档（B） | 原版占比 | 复刻件占比 | 贡献 |
|---|---|---|---|
| 0..32 | 27.6% | 21.1% | +1.01 B |
| 32..64 | 18.7% | 18.2% | +0.20 B |
| **64..128** | 23.6% | 30.6% | **−7.46 B** |
| **128..256** | 16.7% | 18.3% | **−3.37 B** |
| 256..512 | 7.8% | 7.3% | +1.00 B |
| 512..1024 | 3.6% | 2.9% | +4.84 B |
| **1024..4096** | 1.9% | 1.5% | **+7.04 B** |
| **4096..1MB** | 0.2%（671 个） | 0.2%（266 个） | **+16.40 B** |
| **total** | | | **+19.67 B** |

### 二、更正 R971

**R971 写「那个 687 KB 函数只解释 2.5 字节，所以大部分差来自极小函数的比例」—— **错**。**

**对那**一个**函数 2.5 B 是对的；对**那一档 671 个**是错的：它们合计贡献 **+16.40 B（83%）**。**

**而「大部分差来自极小函数」也错：0..64 两档合计只 **+1.21 B**，而 64..256 两档是 **−10.83 B**。**

### 三、而这一轮自己也撞了「说一套做一套」

**文件头写「goes into the same tool as a third mode rather than into another script」，然后写成了独立脚本。**

**改正文件头并写出真实理由：拆解需要**固定**档边界（档宽要对上被比较区间），
而 `pdata_sections` 取**一个统一桶宽**（回答另一个问题）。
两套不可互换的参数 → 两个脚本共享同一段走查是对的安排。**

### 四、数字

| 度量 | R971 | R972 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **拆解总和** | 未做 | **+19.67 B（精确匹配）** |
| **4096+ 档贡献** | 「2.5 B」错 | **+16.40 B（83%）** |

### 五、验证

```
cd replica
python tools/pdata_decompose.py
  -> total sum of contributions +19.67 B
  -> 4096..1048576 档 +16.40 B
  -> 64..128 档 -7.46 B，128..256 档 -3.37 B
```

### 六、仍然 Unknown

- **那 671 个大函数是什么**：**Unknown** —— 未取证。
- **复刻件在 64..256 占比更高是好事还是坏事**：**Unknown** —— 未判。

### 七、教训

**R971 那个「2.5 字节」是我心算的，而同一段里就写出了「所以大部分差来自极小函数」这个结论。**

**一个心算的数字，比没有数字更危险 —— 因为它看起来已经被算过了。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R972", BLOCKER)
    ensure(RSTATUS, "R972", BLOCKER)
    ensure(RVERDICT, "第 972 轮", VERDICT)
    ensure(BACKLOG, "R972", BACKLOG_ADD)

    note = (
        "\n## R972 补充 — **均值差拆解：4096 B 以上那档贡献 83%；R971 的粗算错**（+1 工具，套件 2186）\n\n"
        "`tools/pdata_decompose.py` 拆解 19.67 B 的均值差（总和精确匹配）：\n\n"
        "| 档（B） | 原版占比 | 复刻件占比 | 贡献 |\n|---|---|---|---|\n"
        "| 0..32 | 27.6% | 21.1% | +1.01 B |\n| 32..64 | 18.7% | 18.2% | +0.20 B |\n"
        "| **64..128** | 23.6% | 30.6% | **−7.46 B** |\n| **128..256** | 16.7% | 18.3% | **−3.37 B** |\n"
        "| 256..512 | 7.8% | 7.3% | +1.00 B |\n| 512..1024 | 3.6% | 2.9% | +4.84 B |\n"
        "| **1024..4096** | 1.9% | 1.5% | **+7.04 B** |\n"
        "| **4096..1MB** | 0.2%（671） | 0.2%（266） | **+16.40 B（83%）** |\n| total | | | **+19.67 B** |\n\n"
        "→ **R971「687 KB 函数只解释 2.5 B，大部分差来自极小函数比例」是错的**：\n"
        "   4096+ 那档 671 个合起来解释 **83%**；0..64 两档只 +1.21 B，而 64..256 是 **−10.83 B**。\n\n"
        "→ 而这一轮自己也撞了「说一套做一套」：文件头写「third mode rather than another script」然后写成了独立脚本。\n"
        "   已改正并写出真实理由（固定档边界 vs 统一桶宽，两套不可互换的参数）。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 拆解总和 +19.67 B。\n\n"
        "纪律：**心算的数字比没有数字更危险 —— 它看起来已经被算过了。**\n\n"
        "下一轮：查那 671 个大函数（原版 4096..1MB 档）是什么 —— 那占均值差 83%。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R972" not in h:
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
             for p, k in ((RBLOCK, "R972"), (RSTATUS, "R972"), (RVERDICT, "第 972 轮"), (BACKLOG, "R972")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R972: the decomposition contradicts my own rough arithmetic from last round\n\n"
         "R971 asserted that the six-hundred-kilobyte function accounted for only about two and a half bytes of the\n"
         " nineteen-byte mean difference, and concluded in the same paragraph that most of the difference therefore came\n"
         " from the proportion of very small functions. Adding tools/pdata_decompose.py to compute it shows both statements\n"
         " are wrong.\n\n"
         "The decomposition sums exactly to the mean difference, which is the property that makes it checkable. The band\n"
         " above four kilobytes holds six hundred and seventy-one functions in the original against two hundred and sixty-six\n"
         " in the replica, and contributes sixteen point four bytes, eighty-three percent of the total. The band from one to\n"
         " four kilobytes adds seven. And the two bands between sixty-four and two hundred and fifty-six bytes contribute\n"
         " minus ten point eight, because the replica puts more of its mass there and that pulls its mean down.\n\n"
         "So the single largest function was not the story; the band it sits in was. The small-function proportions were not\n"
         " the story either, and their contribution is not even positive in the middle bands.\n\n"
         "The round also caught itself doing what it warns about. The new script's header said the arithmetic belongs in the\n"
         " same tool as a third mode rather than in another script, and then the script was written as its own file. The\n"
         " header now states the real reason: a decomposition needs fixed band edges matched to the ranges being compared,\n"
         " while pdata_sections takes one uniform bucket width for a different question, so one file serving both would mean\n"
         " two sets of arguments that are not interchangeable. Two scripts sharing one section walk is the honest\n"
         " arrangement and the header says so.\n\n"
         "Figures: suite 2186, count 173,952, freshness zero, decomposition total plus nineteen point six seven bytes,\n"
         " matching the mean difference.\n\n"
         "Unknown: what those six hundred and seventy-one large functions in the original actually are; and whether the\n"
         " replica carrying more mass in the sixty-four to two hundred and fifty-six range is good or bad, which was not\n"
         " judged.\n\n"
         "The lesson is that a number I did in my head is more dangerous than no number, because it looks already computed.\n"
         " I wrote the wrong figure and drew the wrong conclusion from it inside one paragraph, and it survived a full round\n"
         " before the arithmetic was actually done.\n\n"
         "One tool added; a conclusion in three documents corrected."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()