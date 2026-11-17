"""Record R977: two more metrics registered, a unit bug caught, and R969's estimate corrected."""

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
### 两个数字进了唯一数字源，而过程中**抓到一个单位 bug**，并**修正 R969 的估算**（R977）

**判据 (c) 是「产物级对照可复算」。`func_count` 答「多少个」，而 R969–R972 那些数是我**手工量的**，
然后从散文里引用 —— 那正是数字漂移的来源。这一轮把两个工具注册成第 13、14 项度量。**

### 新注册的两项

| 度量 | 工具 | 新标签 |
|---|---|---|
| **可执行段体量** | `tools/pe_sections.py` | `section-mass-*` |
| **函数分布（.pdata 地址分桶）** | `tools/pdata_sections.py` | `pdata-above-0x1C00000-*` |

```
section-mass-original-executable: 51,695,104
section-mass-replica-executable:  28,835,328
section-mass-ratio:               55.78%

pdata-above-0x1C00000-original:  156,590
pdata-above-0x1C00000-replica:         0
pdata-last-replica-bucket:       0x1B00000
```

### 而第一版**报了两个 0**

**因为我拿桶**索引**去跟**字节地址**比：**

```python
above_o = sum(v for k, v in oh.items() if k >= 0x1C00000)     # k 是 28，0x1C00000 是三千万
```

> **而它没报错、没抛异常，只是**很确定地报了 0**。
> 而 0 正好是「复刻件在上面没有函数」那个**看起来正确**的答案 ——
> 所以如果我不看原版那一侧，这个 bug 会活下来。**
> **修法：`if k * bucket >= boundary`，并把那个错误留在注释里。**

### 而修好之后，R969 的估算**是错的**

**R969 写「0x1C00000 以上原版约 **10 万**个函数」。真实是 **156,590**。**

**而把两侧一起算，缺口的结构**完全不是「少了一块」**：**

| | 原版 | 复刻件 | 差 |
|---|---|---|---|
| **0x1C00000 以下** | 120,530 | **173,952** | **+53,422** |
| **0x1C00000 以上** | **156,590** | 0 | **−156,590** |
| **合计** | 277,120 | 173,952 | **−103,168** |

**校验：+53,422 − 156,590 = −103,168 = 实际缺口（精确）。**

> **所以复刻件在分界线**以下**比原版多 44%（173,952 vs 120,530），
> 而在**以上**是 0 —— 103,168 这个「缺口」是两个很大的反向运动**抵消之后**的净值。**
> **而 R969 说的「缺口全部在 0x1C00000 以上」在**算术上**对（那一侧确实差 156,590），
> 而在**语义上**是空的：两个镜像的布局独立，所以「某个地址以上」不是对功能的划分，
> 只是链接器把东西放在哪。**
> **→ 这一项度量**定位不了**缺口，而它现在诚实地只报三件事：体量、边界、那侧的计数。
> 它自己的输出末尾写着「said where the gap sits and nothing about why」。**

### 数字

| 度量 | R976 | **R977** |
|---|---|---|
| 套件 | 2196 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 类型缺失 | 15 | **15** |
| **度量项数** | 12 | **14** |
| **可执行段体量比** | 未进源 | **55.78%** |
| **0x1C00000 以上（原版）** | 「约 10 万」**错** | **156,590** |

### 教训

> **一个单位 bug 报出的 0，恰好是我以为的答案。
> 如果我只看复刻件那一侧，它会活下来，而下一轮会拿它当证据。**
> **所以这一轮真正的收获不是那两个度量，是**原版那一侧的 156,590 让那个 0 显得可疑**。**
"""

if "两个数字进了唯一数字源" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 977 轮：两个数字进了唯一数字源，抓到一个单位 bug，并修正 R969 的估算

### 新注册两项度量（判据 c）

| 度量 | 工具 | 标签 |
|---|---|---|
| **可执行段体量** | `tools/pe_sections.py` | `section-mass-*` |
| **函数分布（地址分桶）** | `tools/pdata_sections.py` | `pdata-above-0x1C00000-*` |

```
section-mass-original-executable: 51,695,104
section-mass-replica-executable:  28,835,328
section-mass-ratio:               55.78%
pdata-above-0x1C00000-original:  156,590
pdata-above-0x1C00000-replica:         0
pdata-last-replica-bucket:       0x1B00000
```

### 第一版报了**两个 0** —— 单位 bug

```python
above_o = sum(v for k, v in oh.items() if k >= 0x1C00000)   # k 是桶索引 28，不是地址
```

> **它没报错、没抛异常，只是很确定地报了 0 —— 而 0 正好是「复刻件上面没有函数」那个看起来正确的答案。
> 如果我不看原版那一侧，这个 bug 会活下来。**
> **修法：`if k * bucket >= boundary`，错误留在注释里。**

### 而修好之后，R969 的估算是错的

**R969 说「0x1C00000 以上原版约 10 万」。真实 **156,590**。而两侧一起算，缺口**不是「少了一块」**：**

| | 原版 | 复刻件 | 差 |
|---|---|---|---|
| **0x1C00000 以下** | 120,530 | **173,952** | **+53,422** |
| **0x1C00000 以上** | **156,590** | 0 | **−156,590** |
| 合计 | 277,120 | 173,952 | **−103,168** |

**校验：+53,422 − 156,590 = −103,168（精确）。**

> **复刻件在分界线**以下**比原版多 44%，在**以上**是 0 —— 103,168 是两个很大的反向运动**抵消后**的净值。
> 而 R969 的「缺口全部在 0x1C00000 以上」算术上对、语义上空：两镜像布局独立，
> 「某地址以上」不是对功能的划分，只是链接器把东西放哪。
> → 这项度量**定位不了**缺口，它只诚实报体量、边界、那侧计数。**

### 数字

| 度量 | R976 | **R977** |
|---|---|---|
| 套件 | 2196 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 类型缺失 | 15 | **15** |
| **度量项数** | 12 | **14** |
| **体量比** | 未进源 | **55.78%** |
| **0x1C00000 以上（原版）** | 「约 10 万」错 | **156,590** |

### 教训

> **一个单位 bug 报出的 0，恰好是我以为的答案。而这次是**原版那一侧的 156,590** 让那个 0 显得可疑。**
"""

BACKLOG_ADD = """

## 判据 (c) — **度量项 12 → 14：可执行段体量 55.78% · 0x1C00000 以上原版 156,590 / 复刻件 0**（R977）

### 新增两项度量

**`可执行段体量`（`tools/pe_sections.py`）· `函数分布（.pdata 地址分桶）`（`tools/pdata_sections.py`）**

```
section-mass-ratio:              55.78%   (28,835,328 / 51,695,104)
pdata-above-0x1C00000-original: 156,590
pdata-above-0x1C00000-replica:        0
pdata-last-replica-bucket:      0x1B00000
```

### 抓到单位 bug

**第一版拿桶索引（28）跟字节地址（0x1C00000）比 → 两侧都报 0。没抛异常，只是很确定地错。
修法 `k * bucket >= boundary`，错误留在注释里。**

### 修正 R969

**「0x1C00000 以上约 10 万」→ **156,590**。而缺口是两个反向运动的净值：**

| | 原版 | 复刻件 | 差 |
|---|---|---|---|
| 0x1C00000 以下 | 120,530 | 173,952 | **+53,422** |
| 0x1C00000 以上 | 156,590 | 0 | **−156,590** |
| 合计 | 277,120 | 173,952 | **−103,168** |

**→ 复刻件在分界线以下比原版多 44%。而地址分桶**定位不了**缺口（布局独立）。**

### 数字

**套件 2196 · 产物陈旧度 0/0 · 函数数 173,952 · 类型缺失 15 · 度量项 14**

| 仍 Unknown | |
|---|---|
| 缺口在功能层面分布在哪 | 地址分桶答不了（布局独立） |

**纪律**：一个单位 bug 报出的 0 恰好是我以为的答案 —— 是原版那一侧的数让它可疑。
"""

BLOCKER = """

---

## 401. **度量项 12 → 14；抓到单位 bug；修正 R969 的「约 10 万」为 156,590**

> R977。**只改工具与度量注册，未改产品代码。** 套件 **2196 通过 / 0 失败 / 0 跳过**。

### 一、新增两项度量（判据 c）

| 度量 | 工具 | 标签 |
|---|---|---|
| **可执行段体量** | `tools/pe_sections.py` | `section-mass-original-executable` / `-replica-` / `-ratio` |
| **函数分布（.pdata 地址分桶）** | `tools/pdata_sections.py` | `pdata-above-0x1C00000-original` / `-replica` / `pdata-last-replica-bucket` |

```
section-mass-original-executable: 51,695,104
section-mass-replica-executable:  28,835,328
section-mass-ratio:               55.78%
pdata-above-0x1C00000-original:  156,590
pdata-above-0x1C00000-replica:         0
pdata-last-replica-bucket:       0x1B00000
```

### 二、抓到单位 bug

**第一版：`if k >= 0x1C00000` —— `k` 是桶**索引**（28），不是字节地址（三千万）。
它没抛异常，只是很确定地报了两个 0，而 0 正好是「复刻件上面没有函数」那个看起来正确的答案。**

**修法：`if k * bucket >= boundary`。错误留在注释里。**

### 三、修正 R969

**R969 的「0x1C00000 以上原版约 10 万」→ 真实 **156,590**。而两侧一起算，缺口不是「少了一块」：**

| | 原版 | 复刻件 | 差 |
|---|---|---|---|
| **0x1C00000 以下** | 120,530 | **173,952** | **+53,422** |
| **0x1C00000 以上** | **156,590** | 0 | **−156,590** |
| **合计** | 277,120 | 173,952 | **−103,168** |

**校验：+53,422 − 156,590 = −103,168（精确）。**

**→ 复刻件在分界线**以下**比原版多 44%；以上是 0。103,168 是两个大反向运动的净额。
→ 而地址分桶**定位不了**缺口：两镜像布局独立，「某地址以上」不是对功能的划分。**

### 四、数字

| 度量 | R976 | R977 |
|---|---|---|
| 套件 | 2196 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 类型缺失 | 15 | **15** |
| **度量项数** | 12 | **14** |
| **体量比** | 未进源 | **55.78%** |
| **0x1C00000 以上（原版）** | 「约 10 万」错 | **156,590** |

### 五、验证

```
cd replica
python tools/metrics_report.py --skip-tests
  -> 可执行段体量 exit 0 {'section-mass: original executable': '51695104', ...}
  -> 函数分布 exit 0 {'pdata: above boundary original': '156590', ...}
python tools/metrics_report.py
  -> 完整套件 exit 0  2196 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **缺口在功能层面分布在哪**：**Unknown** —— 地址分桶答不了（布局独立）。

### 七、教训

**一个单位 bug 报出的 0，恰好是我以为的答案。
如果我只看复刻件那一侧，它会活下来，而下一轮会拿它当证据。**

**这次是原版那一侧的 156,590 让那个 0 显得可疑。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R977", BLOCKER)
    ensure(RSTATUS, "R977", BLOCKER)
    ensure(RVERDICT, "第 977 轮", VERDICT)
    ensure(BACKLOG, "R977", BACKLOG_ADD)

    note = (
        "\n## R977 补充 — **度量项 12 → 14；抓到单位 bug；修正 R969 的「约 10 万」为 156,590**（套件 2196）\n\n"
        "判据 (c) 把两个工具注册成第 13、14 项度量（之前那些数是我手工量的、从散文里引用的）：\n"
        "- **可执行段体量**（`pe_sections.py`）：`section-mass-ratio: 55.78%`（28,835,328 / 51,695,104）\n"
        "- **函数分布**（`pdata_sections.py`）：`pdata-above-0x1C00000-original: 156,590` / `-replica: 0`\n\n"
        "**抓到单位 bug**：第一版 `if k >= 0x1C00000`，而 `k` 是桶**索引** 28，不是字节地址 → 两侧都报 0。\n"
        "它没抛异常，只是很确定地错了，而 0 正好是我以为的答案。修法 `k * bucket >= boundary`。\n\n"
        "**修正 R969**：「0x1C00000 以上约 10 万」→ 真实 **156,590**。而缺口是反向运动的净额：\n"
        "| | 原版 | 复刻件 | 差 |\n|---|---|---|---|\n"
        "| 0x1C00000 以下 | 120,530 | **173,952** | **+53,422** |\n"
        "| 0x1C00000 以上 | **156,590** | 0 | **−156,590** |\n"
        "| 合计 | 277,120 | 173,952 | **−103,168** |\n\n"
        "→ 复刻件在分界线**以下**比原版多 44%。103,168 是两个大反向运动抵消后的净值。\n"
        "→ 而地址分桶**定位不了**缺口（布局独立）。\n\n"
        "数字：套件 2196 · 陈旧度 0/0 · 函数数 173,952 · 类型缺失 15 · 度量项 14。\n\n"
        "纪律：一个单位 bug 报出的 0 恰好是我以为的答案 —— 是原版那一侧的 156,590 让那个 0 显得可疑。\n\n"
        "下一轮：转到判据 (d) —— claim 表每条要有 authority+命令+gap_reason。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R977" not in h:
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
             for p, k in ((RBLOCK, "R977"), (RSTATUS, "R977"), (RVERDICT, "第 977 轮"), (BACKLOG, "R977")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R977: two figures registered as metrics, a unit bug caught, and R969's estimate corrected\n\n"
         "Criterion (c) asks for an artifact comparison that can be recomputed. func_count answers how many; the figures\n"
         " from R969 through R972 answered how much and where, but they were measured by hand and then quoted from prose,\n"
         " which is exactly how a number drifts. Both tools existed, so this round registers them as the thirteenth and\n"
         " fourteenth metrics rather than adding capability.\n\n"
         "The executable mass ratio is 55.78 percent over 28,835,328 against 51,695,104 bytes. Above 0x1C00000 the original\n"
         " has 156,590 functions and the replica has none, and the replica's last populated bucket is 0x1B00000.\n\n"
         "The first version of that second figure reported zero in both images. The comparison was `k >= 0x1C00000` where k\n"
         " is a bucket index of 28 and 0x1C00000 is thirty million, so nothing matched. It raised no exception and reported a\n"
         " confident zero, and zero happens to be the answer I expected for the replica side -- had I not also printed the\n"
         " original side, the bug would have survived and the next round would have cited it. The fix multiplies by the bucket\n"
         " size first and the mistake is kept in a comment.\n\n"
         "Fixing it also overturns R969's estimate. I wrote that the original has roughly a hundred thousand functions above\n"
         " that boundary; it has 156,590. And reading both sides together shows the 103,168 gap is not a missing chunk but the\n"
         " net of two large opposite movements: below the boundary the replica has 173,952 against the original's 120,530, so\n"
         " it carries 53,422 more, while above it carries 156,590 fewer. Those two sum to exactly the gap.\n\n"
         "So R969's statement that the gap sits entirely above 0x1C00000 is arithmetically true of that span and semantically\n"
         " empty: the two images are laid out independently, so a boundary in one has no counterpart in the other and\n"
         " above-or-below is a fact about the linker, not about functionality. The metric now reports only mass, the boundary\n"
         " and that side's count, and its own output says it locates nothing.\n\n"
         "Figures: suite 2196, freshness zero, count 173,952, absent types 15, metrics twelve to fourteen, mass ratio 55.78\n"
         " percent, original above the boundary 156,590.\n\n"
         "Unknown: where the gap sits functionally, which address bucketing cannot answer for the reason above.\n\n"
         "The lesson is that a unit bug reported a zero that was exactly what I expected, and only the original-side figure\n"
         " made it look wrong.\n\n"
         "Tools and metric registration changed; docs/METRICS.md regenerated; suite green at 2196."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()