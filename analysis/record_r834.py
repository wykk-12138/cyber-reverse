"""Record R834: ownership replaces detectability, and the mutation test had to be repaired twice before it fired."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 258. 每个度量声明自己拥有的正则键 —— **串味从「可检出」变成「不可能」**

> R834。改 `replica/tools/metrics_report.py`（共享工具），新增 `tools/mutation_ownership.py`。**全量已复跑。**

### 一、R833 留下的选择

R833 的补法是「加一条断言，要求每个 pattern 只在自己输出里出现」。**但那仍然只是检出。**

**改成声明所有权：`METRICS` 每条带上它允许填充的键，`summary_bits(out, owned)` 只提取这些。**
**于是松正则再也填不进别人的行 —— 不是被抓住，是做不到。**

```python
("函数数量（.pdata）", ["tools/func_count.py"],
 ["functions: original .pdata", "functions: replica .pdata", "functions: ratio"]),
```

**外加一条：没有任何度量拥有的 pattern 会在生成的文件里报 WARNING**（不是静默丢掉）。

### 二、改造踩了两次

| 尝试 | 错 | 后果 |
|---|---|---|
| ① | 用 `src.index("]", ...)` 找块尾 —— 找到的是**条目里 keys 列表的** `]` | 留下孤立的 `]),`，**语法错误** |
| ② | 改用按行切块，但变异测试里第一处锚点少了 `)` | **替换静默失败**，测试「通过」了却什么都没测 |

**① 靠 `git checkout -- replica/tools/metrics_report.py` 恢复**（快照目录结构不是我记的那样，git 更快）。
**② 靠给两处替换都加断言才发现** —— 只断言「变了」时，第一处成功就掩盖了第二处失败。

### 三、变异测试本身也修了两次

**第一次：读 stdout 找摘要表 —— 而 `--skip-tests` 不打印表，它写进 `METRICS.md`。**
**两个行列表都是空的，`any()` 在空列表上返回 False，于是「PASS」。**

**第二次：改读生成文件，但没断言第一处替换成功 —— 松键连自己的行都没进，测试报
「FAIL: the loose key did not even reach its own row, so the test is blind」。**

**第三次才真的响：**

```
| 函数数量（.pdata） — functions: LOOSE replica | 171,690 |     <- 进了自己的行
数据文件名对照 — 只有自己那两行                                <- 没串过去
PASS: the loose pattern filled the row that owns it and no other
```

**这三步本身就是这一轮的收获**：**一个测试要先证明自己能看见东西，它说的「通过」才有意义。**

### 四、验证

```
python tools\\mutation_ownership.py      exit 0，松键进自己的行 (171,690)、不进 datafiles
python tools\\metrics_report.py          九项全 exit 0，无 WARNING（无无主正则）
python tools\\metrics_report.py          1766 通过 / 0 失败
九项输出与 R833 完全一致（改造不改变任何数字）
```

### 五、仍然 Unknown

- **`copy:` 那条的聚合分支**：**Unknown** —— 它走 `label.startswith("copy:")` 的专门分支，
  **返回值是聚合而非最后一个匹配。改造没碰这段，边界也没验。**
- **`PATTERN_SOURCE` 在模块导入时读整个文件**：**代价可忽略（17 KB）**，
  **但如果将来把 pattern 表搬到别处，这条孤儿检查会静默失效。**
- **无主 pattern 的 WARNING 只在生成文件里出现**：**Unknown 有没有下游消费者会看它。**

### 六、教训

**「可检出」和「不可能」是两件事，而后者更省心：一条松正则现在无论多松都只污染自己的行。**

**而为了证明这一点，我写坏了两次工具、又修了两次测试。**
**第二次的失败形态最值得记：`any()` 在空列表上返回 False —— 一个空集合上的检查，永远说「干净」。**
"""

VERDICT = """

---

## 第 834 轮：串味从「可检出」变成「不可能」

### 改了什么

`METRICS` 每条带上它允许填充的正则键，`summary_bits(out, owned)` **只提取这些**。
外加：**没有任何度量拥有的 pattern 在生成文件里报 WARNING**，不静默丢掉。

```python
("函数数量（.pdata）", ["tools/func_count.py"],
 ["functions: original .pdata", "functions: replica .pdata", "functions: ratio"]),
```

### 变异测试（第三步才真的响）

```
| 函数数量（.pdata） — functions: LOOSE replica | 171,690 |     <- 进了自己的行
数据文件名对照 — 只有自己那两行                                <- 没串过去
PASS
```

### 改造与测试各失败两次

| 失败 | 原因 |
|---|---|
| 改造 ① 语法错误 | `src.index("]", ...)` 找到的是 keys 列表的 `]`，留下孤立 `]),` |
| 改造 ② 静默无效 | 变异测试第一处锚点少一个 `)`，只断言「变了」掩盖了第二处失败 |
| 测试 ① 假通过 | 读 stdout 找表，而 `--skip-tests` 写进 `METRICS.md`；**`any()` 在空列表上返回 False** |
| 测试 ② 抓到自己的盲点 | 松键连自己的行都没进 → 报「the test is blind」 |

> **一个测试要先证明自己能看见东西，它说的「通过」才有意义。**

### 验证

```
mutation_ownership.py exit 0 · metrics_report 九项 exit 0 无 WARNING · 1766 通过 / 0 失败
九项输出与 R833 完全一致 —— 改造不改变任何数字
```

### 仍然 Unknown

**`copy:` 聚合分支边界**（改造没碰、也没验）· **`PATTERN_SOURCE` 在导入时读整文件**（pattern 表若搬家，孤儿检查静默失效）· **无主 WARNING 有没有下游消费者**

### 教训

**「可检出」和「不可能」是两件事，后者更省心。**
**而 `any()` 在空集合上返回 False —— 一个空集合上的检查，永远说「干净」。**
"""

BACKLOG_ADD = """

## 判据 — 度量表的所有权改造（R834）

`METRICS` 每条带 owned keys，`summary_bits(out, owned)` 只提取这些；无主的 pattern 在生成文件里报 WARNING。

**效果**：**一条松正则无论多松，都只能污染它自己那一行 —— 从「可检出」变成「不可能」。**

### 变异测试（已响）

```
| 函数数量（.pdata） — functions: LOOSE replica | 171,690 |   ← 进了自己的行
数据文件名对照 — 没串过去
```

### 这一轮的四处失败（记形状）

| 失败 | 原因 |
|---|---|
| `src.index("]", ...)` 切块 | 找到的是 keys 列表的 `]` → 孤立 `]),` → 语法错误 |
| 替换静默失败 | 锚点少 `)`；**只断言「变了」掩盖了第二处失败** |
| 测试假通过 | 读 stdout 找表，实际写进 `METRICS.md`；**`any()` 在空列表上 False** |
| 测试盲点 | 松键连自己的行都没进 → 自带「the test is blind」提示 |

**纪律**：**每个要替换的锚点都断言；每个要读的位置都先证明能读到。**

| 仍 Unknown | |
|---|---|
| `copy:` 聚合分支边界 | 改造没碰、也没验 |
| `PATTERN_SOURCE` 导入时读整文件 | pattern 表若搬家，孤儿检查静默失效 |
| 无主 WARNING 有无下游消费者 | 未知 |

**九项输出与 R833 完全一致 —— 改造不改变任何数字，只改变可能性。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R834", BLOCKER)
    ensure(RSTATUS, "R834", BLOCKER)
    ensure(RVERDICT, "第 834 轮", VERDICT)
    ensure(BACKLOG, "R834", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    old = ("**待办：加断言要求每个 pattern 只在自家输出里出现** —— 让「短语够独特」这条前提可检验。")
    new = ("**已完成（R834）**：`METRICS` 每条声明 owned keys，`summary_bits(out, owned)` 只提取这些 ——\n"
           "**串味从「可检出」变成「不可能」**。变异测试 `tools/mutation_ownership.py` 已响"
           "（松键进自己的行、不进 datafiles）。")
    if old in h:
        h = h.replace(old, new, 1)
        print("  handoff updated")
    elif "R834" not in h:
        h += "\n## R834 补充\n\n度量表所有权改造：`summary_bits(out, owned)` 只提取自己拥有的键，串味结构上不可能。\n"
        print("  handoff appended")
    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R834"), (RSTATUS, "R834"), (RVERDICT, "第 834 轮"), (BACKLOG, "R834")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R834: ownership replaces detectability, so a loose pattern cannot reach another metric's row\n\n"
         "R833 confirmed the other eleven summary patterns were clean and noted that the premise -- the phrase is"
         " distinctive enough -- had no mechanical check. An assertion would catch the next loose pattern after the"
         " fact. Instead each METRICS entry now declares the keys its script may fill, and summary_bits extracts only"
         " those, so a pattern can be as loose as it likes without reaching a neighbour's line. A pattern no entry owns"
         " is reported as a warning in the generated file rather than silently never extracted.\n\n"
         "Getting there took two broken attempts and two blind tests, and those are the substance of the round.\n\n"
         "The first rewrite cut the METRICS block at the first closing bracket after the last entry, which belongs to"
         " that entry's key list rather than to the block, and left a stray bracket pair behind. git restored the file;"
         " the snapshot directory is not laid out the way I remembered and HEAD was faster.\n\n"
         "The second rewrite used a line-based block finder and asserted every anchor, then the mutation test failed"
         " to apply its first replacement because an anchor was missing a closing parenthesis -- and since I had only"
         " asserted that something changed, the second replacement's failure was invisible. Every replacement now"
         " asserts its own success.\n\n"
         "The mutation test itself was blind twice. The first version read stdout for the summary table, which"
         "--skip-tests does not print because it writes METRICS.md; both row lists came back empty and any() over an"
         " empty list is False, so it reported PASS without measuring anything. The second version read the generated"
         " file but could not see the loose key even in its own row, and said so: that is the check worth keeping,"
         " because a test that cannot see the thing it is testing reports cleanliness for the same reason it would"
         " report corruption.\n\n"
         "Now the loose key appears in the functions row as 171,690 and never in datafiles. Under the old design that"
         " same number would have landed in the datafiles row, which is exactly R832's bug.\n\n"
         "All nine metrics produce identical numbers to R833; the refactor changed what is possible, not what is"
         " measured. Suite 1766 pass / 0 fail.\n\n"
         "Unknown: the copy: branch's edges, since it aggregates rather than taking the last match and the refactor did"
         " not touch it; whether PATTERN_SOURCE reading the whole file at import stays correct if the pattern table"
         " moves, in which case the orphan check would quietly stop working; and whether anything downstream reads the"
         " orphan warning at all."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
