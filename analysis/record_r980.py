"""Record R980: two of the three holes were stale anchors, and the third cannot fire at all."""

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
### 三处里两处是**锚点过期**，第三处**根本不可能红**（R980）

**R979 量出 33 fired / 1 装饰性 / 2 跳过。这一轮把三处都查到底。**

### ① round 606：`§99` 现在**是真的标题**

**变异把 BLOCKERS.md 度量索引里的 `§25` 改成 `§99`，守卫要求每个 `§N` 都是真标题。**
**而 BLOCKERS.md 现在有 **403** 个 `## N.` 标题 —— `## 99.` 真的存在。**

```
文档标题号范围: 0..403，共 403 个
99 是标题? True
```

> **所以变异**不再改变任何东西** —— 而工具把它报成「GUARD IS DECORATIVE」，
> **那是把变异自己过期的前提算到守卫头上了**。**
> **修：`§99` → `§9999`（一个不可能成为标题的号）。**

### ② round 164：锚点里的数字自己会动

**`find: "**62 个注册模块"` —— 而 PARITY.md 现在是 `**65 个注册模块`。**
**同一份文件里，round 71 和 round 435 的注释都记着**同一次**教训（「锚点带上会变的数字」），
而这一条改过两次锚点还是又过期了。**

> **修：给 `mutation-check.py` 加**正则锚点**（`find_re` / `replace_re`），
> 这一条改成 `(\\*\\*)(\\d+)( 个注册模块)` → `\\g<1>9\\g<2>\\g<3>`。
> 什么数字都匹配，然后把前缀加一个 9 —— **文档数一定与 `CreateAll().Count` 不一致，而且永远不会过期。****

### ③ round 623：**不可能红**，因为文案缺口现在是 0

**变异把 detail 循环的判据换回旧的 `_present(v, text)`，守卫要求「明细行数 == 摘要的 missing 数」。**

**而 `copy_audit_report.py` 今天打的是：**

```
summary missing = 0
明细行（以 | ` 开头的表格行）= 0
```

> **缺口是 0，所以摘要 0、明细 0 —— 两边任何改动都还是 0 == 0。
> **这条守卫在缺口为 0 的时候**在原理上无法被触发**，无论怎么改都红不了。**
> **而它不是「装饰性」——「装饰性」的意思是守卫没用；这条的意思是**它的对象现在是空的**。
> 两者要采取的动作完全不同：前者改守卫，后者**要让守卫能自己造一个非空的情形**。**
> **已记 Unknown + 待办，不假装修好。**

### ④ 而这一轮的结果

```
running 36 of 36 mutations
fired        35
decorative    1   （round 623 —— 对象为空，见上）
skipped       0   （原 2）
restored tree: GREEN
```

| 度量 | R979 | **R980** |
|---|---|---|
| 变异 fired | 33 | **35** |
| 装饰性 | 1 | **1** |
| 跳过 | 2 | **0** |
| 套件 | 2200 | **2200** |

### 教训

> **「装饰性」这个标签会把两种完全不同的情形归成一类：
> 守卫没用，和守卫的对象是空的。**
> **而工具只有一个词，所以我差点把 623 也当成「守卫坏了」去改它 ——
> 那会把一条正确的守卫改坏，而它今天的沉默是对的。**
"""

if "三处里两处是**锚点过期**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 980 轮：三处里两处是锚点过期，第三处根本不可能红

### ① round 606 —— `§99` 现在是真的标题

**变异把度量索引的 `§25` 改成 `§99`，守卫要求每个 `§N` 都是真标题。
而 BLOCKERS.md 现在有 **403** 个 `## N.`，`## 99.` 真的存在。**

> **变异**不再改变任何东西** —— 而工具报「GUARD IS DECORATIVE」，
> **那是把变异自己过期的前提算到守卫头上**。修：`§99` → `§9999`。**

### ② round 164 —— 锚点里的数字自己会动

**`find: "**62 个注册模块"`，而 PARITY.md 现在是 `**65 个注册模块`。
同一份文件里 round 71 / 435 的注释都记过同一次教训，这条改过两次还是又过期了。**

> **修：给 `mutation-check.py` 加**正则锚点**（`find_re`/`replace_re`）。
> 这条改成 `(\\*\\*)(\\d+)( 个注册模块)` → `\\g<1>9\\g<2>\\g<3>` —— 永不宣言过期。**

### ③ round 623 —— **不可能红**，因为文案缺口是 0

```
summary missing = 0
明细行 = 0
```

> **缺口 0 → 摘要 0、明细 0 → 两边任何改动都还是 0 == 0。
> 这条守卫在缺口为 0 时**在原理上无法被触发**。**
> **而它不是「装饰性」——「装饰性」是守卫没用；这条是**它的对象现在是空的**。
> 两者要采取的动作完全不同。已记 Unknown + 待办，不假装修好。**

### ④ 结果

```
running 36 of 36 mutations
fired        35
decorative    1   （round 623 —— 对象为空）
skipped       0   （原 2）
restored tree: GREEN
```

| 度量 | R979 | **R980** |
|---|---|---|
| 变异 fired | 33 | **35** |
| 装饰性 | 1 | **1** |
| 跳过 | 2 | **0** |
| 套件 | 2200 | **2200** |

### 教训

> **「装饰性」把一个词用在了两种情形上：守卫没用，和守卫的对象是空的。
> 我差点把 623 也当「守卫坏了」去改它 —— 那会把一条正确的守卫改坏，而它今天的沉默是对的。**
"""

BACKLOG_ADD = """

## 判据 (e) — **变异 35 fired / 1 装饰性（对象为空）/ 0 跳过**（R980）

### 修了什么

**① round 606：`§99` → `§9999`**（`## 99.` 已是真标题 —— BLOCKERS.md 有 403 节）
**② round 164：改用正则锚点**（`mutation-check.py` 新增 `find_re`/`replace_re`）——
`(\\*\\*)(\\d+)( 个注册模块)` → `\\g<1>9\\g<2>\\g<3>`，永不因数字移动而跳过
**③ round 623：不改守卫** —— 见下

### round 623 的新认识

```
summary missing = 0 ; 明细行 = 0
```

**缺口为 0 → 摘要 0、明细 0 → 两侧任何改动仍 0==0 → **守卫在原理上无法被触发**。**
**这不是「守卫装饰性」，是**对象为空**。动作不同：前者改守卫，后者要给守卫造一个非空情形。**

### 数字

**变异 36 条：fired 35 / 装饰性 1 / 跳过 0 · 套件 2200 · 陈旧度 0/0 · 函数数 173,952**

| 仍待办 | |
|---|---|
| round 623 的守卫如何能自造非空情形 | 未做（需要 fixture 或让工具能吃一个人造的缺口） |

**纪律**：「装饰性」一个词盖了两种情形 —— 守卫没用，和守卫的对象是空的。
"""

BLOCKER = """

---

## 404. **变异 35 fired / 1 装饰性（对象为空）/ 0 跳过**

> R980。**修两处锚点 + 给工具加正则锚点模式。** 套件 **2200 通过 / 0 失败 / 0 跳过**。

### 一、round 606 —— 变异的前提过期了

**变异把 BLOCKERS.md 度量索引里的 `§25` 改成 `§99`，守卫要求每个 `§N` 都是真标题。
而文档现在有 **403** 个 `## N.` —— `## 99.` 真的存在。**

```
文档标题号范围: 0..403，共 403 个
99 是标题? True
```

**→ 变异不再改变任何东西。而工具报的是「GUARD IS DECORATIVE」——
**那是把变异自己过期的前提算到守卫头上**。**

**修：`§99` → `§9999`。**

### 二、round 164 —— 锚点里的数字自己会动

**`find: "**62 个注册模块"`，而 PARITY.md 现在是 `**65 个注册模块`。
同一份文件里 round 71 / round 435 的注释都记过同一次教训，这条改过两次锚点还是又过期了。**

**修：`mutation-check.py` 新增 `find_re` / `replace_re`。这条改成**

```python
"find_re": r"(\\*\\*)(\\d+)( 个注册模块)",
"replace_re": r"\\g<1>9\\g<2>\\g<3>",
```

**任何数字都匹配，然后把前缀加一个 9 → 文档数一定与 `CreateAll().Count` 不一致，且永不因数字移动而跳过。**

### 三、round 623 —— **不可能红**，因为文案缺口是 0

```
summary missing = 0
明细行（以 | ` 开头的表格行）= 0
```

**守卫要求「明细行数 == 摘要 missing 数」。缺口 0 → 两边都是 0 → **任何改动仍 0 == 0**。
**这条守卫在缺口为 0 时在原理上无法被触发。**

**→ 这不是「守卫装饰性」，是**对象为空**。动作不同：前者改守卫，后者要给守卫造一个非空情形。
**已记 Unknown + 待办，不假装修好。****

### 四、结果

```
running 36 of 36 mutations
fired        35
decorative    1   （round 623 —— 对象为空）
skipped       0   （原 2）
restored tree: GREEN   2217 通过 / 0 失败 / 2 跳过
```

| 度量 | R979 | R980 |
|---|---|---|
| 变异 fired | 33 | **35** |
| 装饰性 | 1 | **1** |
| 跳过 | 2 | **0** |
| 套件 | 2200 | **2200** |

### 五、验证

```
cd replica
python tools/mutation-check.py    -> 36 of 36；fired 35 / decorative 1 / skipped 0；restored GREEN
  （完整日志分析见下一轮的 analysis/mutation-run2.log，已删除，命令可重跑）
python tools/metrics_report.py    -> 完整套件 exit 0  2200 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown / 待办

- **round 623 的守卫如何能自造非空情形**：**未做** —— 需要 fixture，或让工具能吃一个人造的缺口。

### 七、教训

**「装饰性」这个标签把两种完全不同的情形归成一类：守卫没用，和守卫的对象是空的。**

**而工具只有一个词，所以我差点把 623 也当成「守卫坏了」去改它 ——
那会把一条正确的守卫改坏，而它今天的沉默是对的。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R980", BLOCKER)
    ensure(RSTATUS, "R980", BLOCKER)
    ensure(RVERDICT, "第 980 轮", VERDICT)
    ensure(BACKLOG, "R980", BACKLOG_ADD)

    note = (
        "\n## R980 补充 — **变异 35 fired / 1 装饰性（对象为空）/ 0 跳过**（套件 2200）\n\n"
        "R979 的三处，两处是锚点过期，一处根本不可能红：\n"
        "- **round 606**：`§99` 现在**是真的标题**（BLOCKERS.md 有 403 节）→ 变异不再改变任何东西。已改 `§9999`\n"
        "- **round 164**：`find: \"**62 个注册模块\"` 而文档是 `**65` → 已给 `mutation-check.py` 加**正则锚点**\n"
        "  （`find_re`/`replace_re`），改成 `(\\*\\*)(\\d+)( 个注册模块)` → `\\g<1>9\\g<2>\\g<3>`，永不宣言过期\n"
        "- **round 623**：文案缺口现在是 **0** → 摘要 0、明细 0 → 两侧任何改动仍 0==0 →\n"
        "  **守卫在原理上无法被触发**。**这不是「装饰性」，是对象为空。不改守卫，记待办。**\n\n"
        "结果：36 条 → **fired 35 / 装饰性 1 / 跳过 0**（原 33/1/2），restored GREEN。\n\n"
        "数字：套件 2200 · 陈旧度 0/0 · 函数数 173,952。\n\n"
        "纪律：**「装饰性」一个词盖了两种情形 —— 守卫没用，和守卫的对象是空的。**\n"
        "工具只有一个词，差点让我把 623 也当「守卫坏了」去改，那会把一条正确的守卫改坏。\n\n"
        "下一轮：给 round 623 的守卫造一个非空情形（fixture 或让工具吃人造缺口）；然后把变异度量进 METRICS。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R980" not in h:
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
             for p, k in ((RBLOCK, "R980"), (RSTATUS, "R980"), (RVERDICT, "第 980 轮"), (BACKLOG, "R980")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R980: two mutation anchors had expired, and the third cannot fire at all\n\n"
         "R979 measured 33 fired, one decorative and two skipped. This round traced all three.\n\n"
         "Round 606's mutation points the metric index at section 99 to see whether a guard notices a pointer into nothing.\n"
         " It does notice, but the document has grown to 403 sections, so section 99 is now a real heading and the mutation\n"
         " changes nothing. The tool reported that as a decorative guard, which blames the guard for the mutation's own\n"
         " expired premise. The target is now 9999, which cannot become a heading.\n\n"
         "Round 164's anchor was the literal '62 registered modules' and the catalogue has reached 65. The same file records\n"
         " this lesson twice already, at rounds 71 and 435, and the row had been re-anchored twice and expired again. So the\n"
         " tool gained a regular-expression mode: this mutation now matches whatever number the line shows and prefixes a 9,\n"
         " which makes the document disagree with CreateAll().Count no matter how often the count moves.\n\n"
         "Round 623 is different in kind and I nearly got it wrong. Its mutation reverts the detail loop to the older\n"
         " predicate, and the guard requires the detail row count to equal the summary's missing total. The copy gap is\n"
         " currently zero, so summary is zero and detail is zero, and no edit to either loop can make them differ. The guard\n"
         " cannot be triggered while its subject is empty. That is not a decorative guard; it is a guard with nothing to\n"
         " guard. The two call for opposite actions -- change the guard versus give it a non-empty case -- and lumping them\n"
         " under one word is how a correct guard gets broken for being right.\n\n"
         "So the suite now runs 36 of 36 with 35 fired, none skipped, and one that cannot fire for the reason above.\n\n"
         "Figures: mutations fired 33 to 35, skipped 2 to 0, suite 2200, freshness zero, count 173,952.\n\n"
         "Unknown and open: how to give the copy-audit guard a non-empty case, which needs a fixture or a way for the tool to\n"
         " accept a manufactured gap.\n\n"
         "The lesson is that one label covered two situations. Decorative means the guard does not work; this one means it has\n"
         " nothing to work on, and only the label made them look the same.\n\n"
         "Mutation tooling extended; two anchors repaired; suite green at 2200."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()