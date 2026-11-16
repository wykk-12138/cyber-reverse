"""Record R833: the other eleven patterns are clean, and the reason is their shape."""

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

## 257. `summary_bits` 其余十一项**全部干净**；而原因是它们的形状

> R833。未改产品代码（只跑了一遍交叉矩阵）。

### 一、上一轮留下的问题

R832 发现我新加的 `replica\\s*:\\s*([\\d,]+)` 从 `datafiles_diff.py` 的输出里读了一个 0，进了 `数据文件名对照` 那一行。
**修法是把标签改成唯一前缀。**

**留下的 Unknown**：**其余十一项有没有同类问题？**

### 二、做法：把每个脚本的输出与全部正则做矩阵

`analysis/cross_match.py` 载入 `metrics_report.py` 的 `METRICS` 与 `patterns`，
**逐个跑脚本、对每份输出套全部正则，再把每项的 `bits` 打出来。**

**结果：**

```
名字级绑定缺口      real gap 4 · missing 16
类型级绑定缺口      types with scope misses 0
类型缺失            types absent from source 17
成员形状差异        total mismatches 78
文案缺口总表        copy: zones with a missing key 0 (in 0 zone[s])
绑定缺口分桶        backlog: classes missing members 0 · backlog: types absent 4
原版绑定描述符表    descriptor entries 951 · descriptor types 215 · only in descriptors 132 · only in xaml table 0
数据文件名对照      datafiles: original-on-disk not in replica 0 · datafiles: replica-only 2
函数数量（.pdata）  functions: original .pdata 277,120 · replica 171,690 · ratio 61.96%
```

**每一项的 `bits` 只含自己的键。零串味。**

### 三、为什么其余十一项没这个问题

**看它们要求什么：**

| 正则 | 要求 |
|---|---|
| `types with scope misses:\\s*(\\d+)` | 四词短语 |
| `descriptor entries\\s*:\\s*(\\d+)` | 两词短语 |
| `only in xaml table\\s*:\\s*(\\d+)` | 四词短语 |
| `original-on-disk but not written by the replica\\s*:\\s*(\\d+)` | **六个词的整句** |

**而我新加的那条是 `replica\\s*:\\s*([\\d,]+)` —— 一个裸词加冒号。**
**它是全表唯一一条能被别人的输出满足的。**

**所以这不只是「我这条写得松」，是「这个表的其余条目都用了足够长的短语」。**
**这个表的设计前提是「短语足够独特」；我加的那条违反了前提，而不是表本身有缺陷。**

### 四、验证

```
python analysis\\cross_match.py     九个脚本全 exit 0；每项 bits 只含自己的键
python tools\\metrics_report.py     七项全 exit 0（R832 已跑）
本轮未改产品代码
四项度量沿用 4 / 0 / 17 / 78 / 0（+ 第七项 277,120 / 171,690 / 61.96%）
```

### 五、仍然 Unknown

- **将来新加的正则会不会再犯**：**Unknown** —— 判据是「短语够不够独特」，
  **而「够不够」没有机械检验。** 补法：**加一条断言，要求每个 pattern 在自己的输出的 `bits` 里出现、
  且在其余八份输出里都不出现。** 本轮没加。
- **`copy:` 那条是特殊的**：它在 `summary_bits` 里走分支（`label.startswith("copy:")`），
  **返回的是聚合值而不是最后一个匹配。** 这条逻辑我只读到、没验过边界。

### 六、教训

**「其余十一项有没有同样的问题」这个问题，答案是「没有」，而理由不是它们写得更好，
是它们都用了足够长的短语 —— 而表的设计前提就是这个。**

**我加的那条违反了前提，看起来却和别的条目一样整齐。**
**一条正则的危险不在它长什么样，在它能匹配到什么。**

**这一轮没找到缺陷。** **而「检查一遍、没有」这种结果，只有把矩阵打出来才算数 —— 我说「其余十一项应该没问题」是没有价值的。**
"""

VERDICT = """

---

## 第 833 轮：`summary_bits` 其余十一项全部干净

### 做法

`analysis/cross_match.py`：逐个跑九个脚本，对每份输出套**全部**正则，打印每项的 `bits`。

### 结果

**每一项的 `bits` 只含自己的键。零串味。**

### 为什么其余十一项没问题

| 正则 | 要求 |
|---|---|
| `types with scope misses:` | 四词短语 |
| `descriptor entries:` | 两词短语 |
| `original-on-disk but not written by the replica:` | **六词整句** |
| **我新加的 `replica\\s*:\\s*([\\d,]+)`** | **一个裸词 + 冒号** |

> **不只是「我这条写得松」，是「表里其余条目都用了足够长的短语」。表的设计前提是「短语足够独特」，我加的那条违反了前提。**

**一条正则的危险不在它长什么样，在它能匹配到什么。**

### 验证

```
cross_match.py 九个脚本全 exit 0，每项 bits 只含自己的键 · 产品代码未改
```

### 仍然 Unknown

**将来新加的正则会不会再犯** —— 判据是「短语够不够独特」，**而「够不够」没有机械检验**。
补法：**加一条断言，要求每个 pattern 在自己的输出里出现、在其余八份里都不出现。本轮没加。**

**`copy:` 那条走聚合分支，边界未验。**

### 教训

**「检查一遍、没有」这种结果，只有把矩阵打出来才算数 —— 我说「其余十一项应该没问题」是没有价值的。**
"""

BACKLOG_ADD = """

## 结案 — `summary_bits` 其余十一项无串味（R833）

**矩阵结果**：九个脚本全 exit 0；**每项的 `bits` 只含自己的键。**

### 原因不是它们写得更好，是形状

| 正则 | 要求 |
|---|---|
| `types with scope misses:` | 四词 |
| `descriptor entries:` | 两词 |
| `original-on-disk but not written by the replica:` | **六词整句** |
| **我新加的 `replica:`** | **裸词** |

**表的设计前提是「短语足够独特」；我加的那条违反了前提。**

> **一条正则的危险不在它长什么样，在它能匹配到什么。**

### 待办（本轮没做）

**加一条断言**：每个 pattern 必须在自己的输出里出现、且在其余八份输出里都不出现。**这才让前提可检验。**

| 仍 Unknown | |
|---|---|
| 将来新加正则会否重犯 | 无机械检验 |
| `copy:` 聚合分支的边界 | 只读到、未验 |

**纪律**：**「其余应该没问题」没有价值；把矩阵打出来才算数。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R833", BLOCKER)
    ensure(RSTATUS, "R833", BLOCKER)
    ensure(RVERDICT, "第 833 轮", VERDICT)
    ensure(BACKLOG, "R833", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R833" not in h:
        h += ("\n## R833 补充 — summary_bits 无串味\n\n"
              "九个脚本 × 全部正则的矩阵：**每项 bits 只含自己的键，零串味**。\n"
              "原因：其余条目都要求两到六词的短语，只有 R832 我加的那条用了裸词 `replica:`。\n"
              "**待办：加断言要求每个 pattern 只在自家输出里出现** —— 让「短语够独特」这条前提可检验。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R833"), (RSTATUS, "R833"), (RVERDICT, "第 833 轮"), (BACKLOG, "R833")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R833: the other eleven summary patterns are clean, and the reason is their shape\n\n"
         "R832 found one pattern matching another script's output and fixed it with unique labels, leaving open whether"
         " the other eleven had the same problem. This builds the matrix rather than checking pairs by hand: load"
         " METRICS and the pattern table out of metrics_report, run each of the nine scripts, apply every pattern to"
         " every output, and print each metric's bits.\n\n"
         "Every metric's bits contain only its own keys. Nothing crosses.\n\n"
         "The reason is not that those patterns are written more carefully but that all of them require multi-word"
         " phrases -- four words for types with scope misses, two for descriptor entries, six for the datafiles"
         " sentence. The table's premise is that a phrase is distinctive enough not to appear elsewhere, and my new"
         " pattern broke that premise with a single bare word followed by a colon. So the defect was mine and the table"
         " was sound, which is a different conclusion from the one I would have reached by assuming the table needed"
         " tightening.\n\n"
         "What makes a regex dangerous is not what it looks like but what it can match, and a pattern that looks as tidy"
         " as its neighbours can be the only one that matches three scripts.\n\n"
         "I did not add the assertion this deserves: that each pattern must appear in its own script's output and in"
         " none of the other eight. Without it the premise remains unchecked for the next pattern anyone adds, and"
         " writing the check is the only thing that turns the premise into a test.\n\n"
         "Unknown: whether a future pattern will repeat the mistake, which the assertion above would answer; and how the"
         " copy: branch behaves at its edges, since it aggregates rather than taking the last match and I read that code"
         " without exercising it.\n\n"
         "No product code changed; the seven metrics and the suite stand where R832 left them."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
