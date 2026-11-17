"""Record R978: the criterion (d) check audited 5 of 22 rows since the day it was written."""

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
### 判据 (d) 的检查**从诞生起就只审 5 行**，而它报 PASS（R978）

**判据 (d)：claim 表每条有 authority+命令+gap_reason。仓里早有 `analysis/check_claims.py`（R811）。
这一轮先写了一个新的，然后发现它存在 —— 而**读它的时候发现了真问题**。**

### 它报 `claim rows: 5`

```
claim rows: 5
status distribution:  **fail** 3 / **pass** 2
criterion (d) by its own stated rule: PASS
```

**而 `PARITY_CLAIMS.md` 是**五张表**，一节一张，每张各有自己的
`| id | claim | status | authority | command | gap_reason |` 表头。**

**脚本找到**第一个**表头（第 41 行），然后**遇到第一个非表格行就停**（§2 标题前的空行）。
所以它审的只有 C1–C5 —— 五行。**

### 而这不是回归 —— **6 个表头在 R811 那天就都在**

```
c869fe1 (R811)  表头数 6
1635297 (R812)  表头数 6
HEAD            表头数 6
```

**→ 脚本**从诞生起**就只审一张表。它一次都没改过（`git log` 只有 R811 一条），而文档一直是多表。**

> **一个覆盖 23% 的检查报 PASS，比没有检查更坏 —— 因为它的结论会被引用。**
> **而它被引用了：`docs/DELIVERY_STATUS.md` 判据 d 那行写着「✅」。**

### 修好之后

```
claim tables: 5
claim rows: 22
status distribution: **pass** 8 / **unknown** 7 / **fail** 3 / **pass（Observation 层）** 1 /
                     **fail**（…）1 / **unknown**（…）1 / **pass（Observation 层，R458 实测）** 1
rows without an authority: 0
non-unknown rows without a command: 0
criterion (d) by its own stated rule: PASS
```

**22 行全审，仍然 PASS。所以判据 (d) **确实满足** —— 而它是**这一轮才第一次被真正验证**的。**

### 而 I 又撞了一次「先写后查」

**我写了一个 `audit_claims.py --structure`，文件头写着「add a structural mode to audit_claims.py」，
然后写成了独立脚本 —— 而 R972 刚记过同一次。**

**删掉它、撤回对 `audit_claims.py` 的改动，改成修**已有的**那个（AGENTS.md §1「先抄」）。
R870 的 `where_is` 那条规则的第六次。**

### 还有一条**证据不可复算**

**`docs/DELIVERY_STATUS.md` 判据 d 那行写的证据是：**

```
python analysis\audit_claims.py → claims parsed: 22 (authority=unknown: 9)
                                / criterion (d) holds: ...
```

**而今天同一个命令打的是 `inconsistencies found: 0` —— 完全不同的文本。
`claims parsed` 那句来自 `audit_claims.py` 的**旧版本**（`35e8721`），现行版本不再输出它。**

> **所以那一行的证据**点了一个命令，而那个命令现在不产出被引用的那句话**。
> 判据 (d) 要求「每条有命令」，而**命令能跑 ≠ 命令能复算出引用的那句**。**

### 而这一轮加了守卫

**`ClaimsCoverageTests`（2 个用例）：**
1. **文档确实是多张表**（`tables > 1`、`rows > 10`）—— 表头正则一旦失配就会红
2. **脚本报的行数 == 测试自己独立数出的行数**，且 PASS

> **两个计数器一致才算数 —— 一个计数器打一个数字，正是出错的那种形态。**

### 数字

| 度量 | R977 | **R978** |
|---|---|---|
| 套件 | 2196 | **2198** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **check_claims.py 审的行数** | **5**（错） | **22** |
| **claim 表数** | 未测 | **5** |
| **守卫用例** | 0 | **2** |

### 教训

> **这一轮最值钱的东西不是那个守卫，是「它一直在报 PASS」这个事实。
> 而发现它的路径纯属偶然 —— 我在写一个重复品，而读原件的输出时看到 `claim rows: 5` 那个数
> 跟我知道的 22 对不上。**
> **如果我一开始就按规则 `where_is` 查一次，我会看到同一行 `claim rows: 5`，
> **而很可能不觉得那有问题** —— 因为我要找的是「有没有这个检查」，不是「这个检查对不对」。
> 所以这一轮的运气在于：我多看了一眼一个我本来只打算复制的文件。**
"""

if "判据 (d) 的检查**从诞生起就只审 5 行**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 978 轮：判据 (d) 的检查从诞生起就只审 5 行，而它报 PASS

### 发现

**`analysis/check_claims.py`（R811）报：**

```
claim rows: 5
status distribution:  **fail** 3 / **pass** 2
criterion (d) by its own stated rule: PASS
```

**而 `PARITY_CLAIMS.md` 是**五张表**，一节一张，每张各有自己的表头。
脚本找到**第一个**表头（第 41 行），**遇到第一个非表格行就停**（§2 标题前的空行）→ 只审 C1–C5。**

### 而不是回归 —— 6 个表头在 R811 那天就都在

```
c869fe1 (R811)  表头数 6
1635297 (R812)  表头数 6
HEAD            表头数 6
```

**→ 脚本从诞生起就只审一张表，一次都没改过（`git log` 只有 R811 一条）。**

> **覆盖 23% 的检查报 PASS，比没有检查更坏 —— 它的结论会被引用。
> 而它被引用了：`DELIVERY_STATUS.md` 判据 d 那行写着「✅」。**

### 修好之后

```
claim tables: 5
claim rows: 22
rows without an authority: 0
non-unknown rows without a command: 0
criterion (d) by its own stated rule: PASS
```

**22 行全审仍 PASS → 判据 (d) 确实满足，而它是**这一轮才第一次被真正验证**的。**

### 而我又撞了一次「先写后查」

**写了个 `audit_claims.py --structure`，文件头写着「add a structural mode」却做成独立脚本 —— R972 刚记过。
删掉、撤回改动，改成修**已有的**那个（§1「先抄」）。R870 那条规则的第六次。**

### 还有一条证据不可复算

**`DELIVERY_STATUS.md` 判据 d 那行的证据：`python analysis\\audit_claims.py → claims parsed: 22 …`
而今天同一命令打的是 `inconsistencies found: 0`。`claims parsed` 来自 `audit_claims.py` 的**旧版本**（`35e8721`）。**

> **命令能跑 ≠ 命令能复算出引用的那句。**

### 守卫

**`ClaimsCoverageTests`（2 用例）：① 文档确实是多张表；② 脚本报的行数 == 测试独立数出的行数，且 PASS。**
**两个计数器一致才算数。**

### 数字

| 度量 | R977 | **R978** |
|---|---|---|
| 套件 | 2196 | **2198** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **check_claims.py 审的行数** | **5**（错） | **22** |
| **claim 表数** | 未测 | **5** |
| **守卫用例** | 0 | **2** |

### 教训

> **发现它的路径纯属偶然：我在写一个重复品，而读原件输出时看到 `claim rows: 5` 跟我以为的 22 对不上。
> 如果我一开始就 `where_is` 查一次，我会看到同一行 `claim rows: 5`，**而很可能不觉得那有问题** ——
> 因为我要找的是「有没有这个检查」，不是「这个检查对不对」。**
> **所以运气在于：我多看了一眼一个本来只打算复制的文件。**
"""

BACKLOG_ADD = """

## 判据 (d) — **check_claims.py 审 5/22 行而报 PASS；已修为 22/22，+2 守卫**（R978）

### 缺陷

**`PARITY_CLAIMS.md` 是五张表（一节一张，各有表头）。`check_claims.py`（R811）
找到第一个表头后遇到第一个非表格行就停 → 只审 C1–C5 五行 → 报 PASS。**
**6 个表头在 R811 当天就都在 → **从诞生起**就只审一张表。**

### 修法

**`analysis/check_claims.py` 改为遍历文档里每一张表（`tables()` 生成器）。**

### 结果

```
claim tables: 5      claim rows: 22
rows without an authority: 0
non-unknown rows without a command: 0
criterion (d) by its own stated rule: PASS
```

**→ 判据 (d) 确实满足，而这是第一次被真正验证。**

### 新守卫

**`ClaimsCoverageTests`（2 用例）：文档多表（tables>1 / rows>10）+ 脚本行数 == 测试独立计数。**
**两个计数器一致才算数。**

### 另一条

**`DELIVERY_STATUS.md` 判据 d 那行引用的 `claims parsed: 22` 来自 `audit_claims.py` 的旧版本（`35e8721`），
现行版本打的是 `inconsistencies found: 0` → **证据点了一个命令，而它不再产出被引用的那句**。记 Unknown。**

### 数字

**套件 2198 · 陈旧度 0/0 · 函数数 173,952 · claim 行 5 → 22 · 守卫 2**

| 仍 Unknown | |
|---|---|
| `DELIVERY_STATUS.md` 那条证据的历史成因 | 未追（只知是旧版输出） |

**纪律**：覆盖 23% 的检查报 PASS，比没有检查更坏 —— 它的结论会被引用。
"""

BLOCKER = """

---

## 402. **判据 (d) 的检查从诞生起只审 5/22 行，而报 PASS；已修 +2 守卫**

> R978。**修已有工具（不是新造）+2 守卫。** 套件 **2198 通过 / 0 失败 / 0 跳过**。

### 一、缺陷

**`docs/PARITY_CLAIMS.md` 不是一张表 —— 是**五张**，一节一张，每张各有
`| id | claim | status | authority | command | gap_reason |` 表头。**

**`analysis/check_claims.py`（R811）找到**第一个**表头（第 41 行），
然后**遇到第一个非表格行就停**（§2 标题前的空行）→ 只审 C1–C5。**

```
claim rows: 5
status distribution:  **fail** 3 / **pass** 2
criterion (d) by its own stated rule: PASS
```

**而 6 个表头在 R811 当天就都在（`git show c869fe1` → 表头数 6）→ **不是回归，是从诞生起就这样**。
脚本一次都没改过（`git log --follow` 只有 R811 一条）。**

**→ 覆盖 23% 的检查报 PASS，比没有检查更坏 —— 它的结论会被引用，而 `DELIVERY_STATUS.md` 判据 d 写着「✅」。**

### 二、修法

**改成遍历文档里每一张表（`tables()` 生成器，按表头定位、按行边界收尾）。**

### 三、修好之后

```
claim tables: 5
claim rows: 22
status distribution: **pass** 8 / **unknown** 7 / **fail** 3 / （四种带限定的变体各 1）
rows without an authority: 0
non-unknown rows without a command: 0
criterion (d) by its own stated rule: PASS
```

**22 行全审仍 PASS → 判据 (d) **确实满足**，而这是**第一次被真正验证**。**

### 四、新守卫

**`ClaimsCoverageTests`（2 用例）：**
1. `TheDocumentIsMoreThanOneTable` —— `tables > 1` 且 `rows > 10`（表头正则失配就会红）
2. `TheScriptAuditsEveryTableNotJustTheFirst` —— 脚本报的行数 == 测试**独立**数出的行数，且 PASS

**→ 两个计数器一致才算数：一个计数器打一个数字，正是出错的那种形态。**

### 五、还有一条证据不可复算

**`DELIVERY_STATUS.md` 判据 d 那行引用的证据是
`python analysis\\audit_claims.py → claims parsed: 22 (authority=unknown: 9) / criterion (d) holds`。
今天同一命令打的是 `inconsistencies found: 0`。**
**`claims parsed` 那句来自 `audit_claims.py` 的**旧版本**（`35e8721`）。**

**→ 命令能跑 ≠ 命令能复算出被引用的那句。记 Unknown，成因未追。**

### 六、而我又撞了一次「先写后查」

**写了个 `audit_claims.py --structure`，文件头写着「add a structural mode to audit_claims.py」，
然后写成了独立脚本 —— **R972 刚记过同一次**。删掉、`git checkout` 撤回，改成修已有的那个（§1「先抄」）。
**R870 那条规则的第六次。****

### 七、数字

| 度量 | R977 | R978 |
|---|---|---|
| 套件 | 2196 | **2198** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **check_claims.py 审的行数** | **5**（错） | **22** |
| **claim 表数** | 未测 | **5** |
| **守卫用例** | 0 | **2** |

### 八、验证

```
cd D:\\projects\\cyber-reverse
python analysis/check_claims.py
  -> claim tables: 5 / claim rows: 22 / PASS
cd replica
dotnet test --filter "FullyQualifiedName~ClaimsCoverageTests" -m:1
  -> 2 通过
python tools/metrics_report.py
  -> 完整套件 exit 0  2198 通过 / 0 失败 / 0 跳过
```

### 九、仍然 Unknown

- **`DELIVERY_STATUS.md` 那条证据的历史成因**：**Unknown** —— 只知是旧版输出，未追何时失配。

### 十、教训

**发现它的路径纯属偶然：我在写一个重复品，而读原件输出时看到 `claim rows: 5` 跟我以为的 22 对不上。**

**如果我一开始就 `where_is` 查一次，我会看到同一行 `claim rows: 5`，而很可能不觉得那有问题 ——
因为我要找的是「有没有这个检查」，不是「这个检查对不对」。**

**所以运气在于：我多看了一眼一个本来只打算复制的文件。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R978", BLOCKER)
    ensure(RSTATUS, "R978", BLOCKER)
    ensure(RVERDICT, "第 978 轮", VERDICT)
    ensure(BACKLOG, "R978", BACKLOG_ADD)

    note = (
        "\n## R978 补充 — **判据 (d) 的检查从诞生起只审 5/22 行，而报 PASS；已修 +2 守卫**（套件 2198）\n\n"
        "`docs/PARITY_CLAIMS.md` 是**五张表**（一节一张，各有表头）。`analysis/check_claims.py`（R811）\n"
        "找到第一个表头后遇到第一个非表格行就停 → 只审 C1–C5 五行 → 报 PASS。\n"
        "**6 个表头在 R811 当天就都在 → 不是回归，是从诞生起就这样。**\n\n"
        "修法：改成遍历每一张表。修好之后 `claim rows: 22`，仍 PASS → **判据 (d) 确实满足，第一次被真正验证**。\n\n"
        "新守卫 `ClaimsCoverageTests`（2 用例）：文档多表 + 脚本行数 == 测试独立计数。\n\n"
        "另一条：`DELIVERY_STATUS.md` 判据 d 引用的 `claims parsed: 22` 来自 `audit_claims.py` 旧版本（`35e8721`），\n"
        "现行版本打 `inconsistencies found: 0` → **命令能跑 ≠ 命令能复算出被引用的那句**。记 Unknown。\n\n"
        "而我又撞了「先写后查」：写了 `audit_claims.py --structure` 却做成独立脚本（R972 同一次），已删除并改为修已有的。\n\n"
        "数字：套件 2198 · 陈旧度 0/0 · 函数数 173,952 · claim 行 5 → 22 · 守卫 2。\n\n"
        "纪律：覆盖 23% 的检查报 PASS，比没有检查更坏 —— 它的结论会被引用。\n\n"
        "下一轮：判据 (e) —— 套件绿、变异测试全 fired。先跑 mutation-check.py 看现状。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R978" not in h:
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
             for p, k in ((RBLOCK, "R978"), (RSTATUS, "R978"), (RVERDICT, "第 978 轮"), (BACKLOG, "R978")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R978: the criterion (d) check audited five of twenty-two rows and reported PASS\n\n"
         "Criterion (d) says every claim row carries authority, command and gap_reason, and check_claims.py has been the\n"
         " machine answer since R811. Reading it this round showed it printing 'claim rows: 5', which did not match the table\n"
         " I knew held far more.\n\n"
         "The document is not one table. It is five, one per section, each opening with its own header. The script found the\n"
         " first header at line 41 and stopped at the first non-table line, which is the blank before the next section's\n"
         " heading. So it audited C1 to C5 and reported PASS. Six headers existed on the day it was written, so this is not a\n"
         " regression: it has never covered more than a quarter of its subject, and it has never been changed since its single\n"
         " commit. A check covering twenty-three percent while printing PASS is worse than none, because its verdict gets\n"
         " quoted, and DELIVERY_STATUS.md does quote it as a tick.\n\n"
         "The fix walks every table. Twenty-two rows now, still zero without an authority and zero decided rows without a\n"
         " command, so criterion (d) genuinely holds -- and this round is the first time that has actually been verified\n"
         " rather than assumed.\n\n"
         "Two guard tests pin it: that the document really is more than one table, and that the script's row count equals an\n"
         " independent count taken in the test. Two counters agreeing is the property that was missing; one counter printing a\n"
         " number is exactly what went wrong.\n\n"
         "A second finding: DELIVERY_STATUS.md cites 'python analysis/audit_claims.py' producing 'claims parsed: 22'. That\n"
         " text came from an older revision of that script and the current one prints something else, so the cited evidence\n"
         " no longer reproduces from the cited command. Whether a command runs is not the same as whether it reproduces the\n"
         " sentence quoted.\n\n"
         "And I did the thing again: I wrote an audit_claims.py --structure whose own header said it belonged as a mode in that\n"
         " file, then wrote it as a separate script. R972 recorded the same mistake one round earlier. It was deleted and the\n"
         " existing tool fixed instead.\n\n"
         "Figures: suite 2196 to 2198, freshness zero, count 173,952, claim rows audited five to twenty-two, claim tables five,\n"
         " guard tests two.\n\n"
         "Unknown: why the DELIVERY_STATUS citation stopped reproducing, which was not traced.\n\n"
         "The lesson is that finding this was luck. Had I run where_is first I would have seen the same 'claim rows: 5' line\n"
         " and very likely not questioned it, because what I was looking for was whether the check existed, not whether it was\n"
         " right.\n\n"
         "One existing tool fixed, two tests added; docs/METRICS.md regenerated; suite green at 2198."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()