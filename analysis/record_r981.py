"""Record R981: the last mutation fires, so criterion (e)'s second clause holds."""

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
### 最后一条变异也能红了 —— **36 / 36 fired**（R981）

**R980 说 round 623 的守卫「对象为空」，要给它造一个非空情形。这一轮做了，而办法不是改守卫，是让**工具能指向别处**。**

### 缺口的形状

**守卫的不变式：`明细行数 == 摘要的 missing 数`。真实树今天两边都是 **0**，所以任何改动仍 0==0。**

**而两个判据在**一种形状**下会分开：**

| 判据 | 返回 True 的条件 |
|---|---|
| `_satisfied(key, value, text, code)`（新） | value 在源码里 **或** key 的名字出现在源码里 |
| `_present(value, text)`（旧） | **只有** value 在源码里 |

> **所以「键名在源码里、值不在」那一种 —— 新旧判据就分开。而真实树里没有这种键，因为缺口是 0。**

### 改法

**① `copy_audit_report.py` 加了 `--pool` / `--src` / `--out` 三个参数**（默认值就是原来的三个常量）。
**理由写在文件里：守卫要能指向一个人造的小样本，否则它只能永远指向真实树，而真实树上它无话可说。**

**② 守卫改成**跑两次**：**

```
[real tree]  摘要 0 / 明细 0   → 不变式成立（这是原本就在测的）
[fixture]    pool 里一行 "Accounts.Test.Key": "a value that appears nowhere at all"
             src 里一行 class Sample { const string K = "Accounts.Test.Key"; }
             → 键名在、值不在 → 宽判据算「在用」、窄判据算「缺」
             → 摘要 0 / 明细 0（正确代码）→ 成立
             → 摘要 0 / 明细 1（变异代码）→ **红**
```

### 而它真的红了 —— 手工验过

```
变异应用 1 处
[FAIL] Cybersole.Tests.CopyAuditConsistencyTests.DetailRowsMatchTheSummaryTotal
失败: 1
已还原
还原后：通过: 1
```

**然后是全量变异：**

```
running 36 of 36 mutations
fired        36      （原 33 → 35 → 36）
decorative    0      （原 1）
skipped       0      （原 2）
restored tree: GREEN
```

> **判据 (e) 的第二句「变异测试全 fired」**现在成立** —— 而它的成立方式不是把守卫改严，
> 是**给守卫一个能说话的对象**。**

### 而这一轮的方法也可以复用

**前三轮（R979/R980/R981）修的是同一个东西：一个检查沉默，有三种原因。**

| 原因 | 征兆 | 修法 |
|---|---|---|
| 它只审了一部分 | `claim rows: 5` | **扩范围**（R978） |
| 它的锚点/前提过期 | `SKIPPED` / `DECORATIVE` | **换锚点**（R980） |
| 它的对象是空的 | `DECORATIVE` 而代码没变 | **造对象**（R981） |

> **三种都报「通过」或「没通过」，而**修法完全不同**。而工具只给两个词。**

### 数字

| 度量 | R980 | **R981** |
|---|---|---|
| 变异 fired / 总 | 35 / 36 | **36 / 36** |
| 装饰性 | 1 | **0** |
| 跳过 | 0 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 教训

> **「守卫是装饰性的」和「守卫没有对象」在日志里是同一行。
> 而前者要改守卫，后者改了守卫就是把一条正确的守卫改坏。**
> **所以下一步永远是：先看代码有没有变。变了还绿 → 装饰性；没变 → 没有对象。**
"""

if "最后一条变异也能红了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 981 轮：最后一条变异也能红了 —— 36 / 36 fired

### 缺口的形状

**守卫不变式：`明细行数 == 摘要 missing 数`。真实树两边都是 **0** → 任何改动仍 0==0。**

**而两个判据在一种形状下分开：**

| 判据 | 返回 True 的条件 |
|---|---|
| `_satisfied(key, value, text, code)`（新） | value 在源码里 **或** key 的名字在源码里 |
| `_present(value, text)`（旧） | **只有** value 在源码里 |

> **「键名在、值不在」→ 新旧分开。真实树里没有这种键，因为缺口是 0。**

### 改法

**① `copy_audit_report.py` 加 `--pool` / `--src` / `--out`（默认值 = 原常量）**

**② 守卫跑两次：**

```
[real tree]  摘要 0 / 明细 0   → 成立
[fixture]    键名在源码、值不在 → 正确代码 0/0 成立；变异代码 0/1 → 红
```

### 手工验过它真的红

```
变异应用 1 处 → [FAIL] DetailRowsMatchTheSummaryTotal → 已还原 → 通过
```

### 而全量变异

```
running 36 of 36 mutations
fired 36 · decorative 0 · skipped 0 · restored GREEN
```

> **判据 (e) 第二句「变异测试全 fired」**现在成立** ——
> 成立方式不是把守卫改严，是**给守卫一个能说话的对象**。**

### 三轮修的是同一件东西：一个检查沉默有三种原因

| 原因 | 征兆 | 修法 |
|---|---|---|
| 只审了一部分 | `claim rows: 5` | **扩范围**（R978） |
| 锚点/前提过期 | `SKIPPED` / `DECORATIVE` | **换锚点**（R980） |
| 对象是空的 | `DECORATIVE` 而代码没变 | **造对象**（R981） |

> **三种都报「通过」或「没通过」，而修法完全不同。而工具只给两个词。**

### 数字

| 度量 | R980 | **R981** |
|---|---|---|
| 变异 fired / 总 | 35 / 36 | **36 / 36** |
| 装饰性 / 跳过 | 1 / 0 | **0 / 0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 教训

> **「守卫是装饰性的」和「守卫没有对象」在日志里是同一行。
> 前者要改守卫，后者改了就是把一条正确的守卫改坏。**
> **下一步永远是：先看代码有没有变。变了还绿 → 装饰性；没变 → 没有对象。**
"""

BACKLOG_ADD = """

## 判据 (e) — **变异 36 / 36 fired，0 装饰性，0 跳过**（R981，**+1 工具参数**）

### 改了什么

**① `copy_audit_report.py`：加 `--pool` / `--src` / `--out`（默认值 = 原常量）**
**② `CopyAuditConsistencyTests.DetailRowsMatchTheSummaryTotal`：跑两次 —— 真实树 + fixture**

**fixture 的形状是唯一让新旧判据分开的那一种：键名在源码里、值不在。**
**正确代码 → 摘要 0 / 明细 0；变异代码 → 摘要 0 / 明细 1 → 红（手工验过）。**

### 结果

```
running 36 of 36 mutations
fired 36 · decorative 0 · skipped 0 · restored GREEN
```

### 三轮的同一个东西：检查沉默有三种原因

| 原因 | 征兆 | 修法 |
|---|---|---|
| 只审了一部分 | `claim rows: 5` | 扩范围（R978） |
| 锚点/前提过期 | `SKIPPED` / `DECORATIVE` | 换锚点（R980） |
| 对象是空的 | `DECORATIVE` 而代码没变 | 造对象（R981） |

### 数字

**变异 36/36 · 套件 2200 · 陈旧度 0/0 · 函数数 173,952**

**纪律**：先看代码有没有变。变了还绿 → 守卫装饰性；没变 → 守卫没有对象。
"""

BLOCKER = """

---

## 405. **变异 36 / 36 fired，0 装饰性，0 跳过 → 判据 (e) 第二句成立**

> R981。**加工具参数 + 改写守卫为双跑。** 套件 **2200 通过 / 0 失败 / 0 跳过**。

### 一、缺口的形状

**守卫不变式：`明细行数 == 摘要 missing 数`。真实树两边都是 **0** → 任何改动仍 0==0 → 无法被触发。**

**两个判据在**一种**形状下分开：**

| 判据 | True 的条件 |
|---|---|
| `_satisfied(key, value, text, code)`（新） | value 在源码里 **或** key 的名字在源码里 |
| `_present(value, text)`（旧） | **只有** value 在源码里 |

**→「键名在、值不在」时分开。真实树里没有这种键，因为缺口是 0。**

### 二、改法

**① `copy_audit_report.py` 加 `--pool` / `--src` / `--out`（默认 = 原常量）。
理由写进文件：守卫要能指向人造小样本，否则只能指向真实树，而真实树上它无话可说。**

**② 守卫跑两次：**

```
[real tree]  摘要 0 / 明细 0  → 成立
[fixture]    pool: "Accounts.Test.Key": "a value that appears nowhere at all"
             src : class Sample { const string K = "Accounts.Test.Key"; }
             → 正确代码 0 / 0 成立；变异代码 0 / 1 → 红
```

### 三、手工验过它真的红

```
变异应用 1 处
[FAIL] Cybersole.Tests.CopyAuditConsistencyTests.DetailRowsMatchTheSummaryTotal
失败: 1
已还原 → 通过: 1
```

### 四、全量变异

```
running 36 of 36 mutations
fired        36      （33 → 35 → 36）
decorative    0      （原 1）
skipped       0      （原 2）
restored tree: GREEN
```

**→ 判据 (e) 第二句「变异测试全 fired」**现在成立**。
而成立方式不是把守卫改严，是**给守卫一个能说话的对象**。**

### 五、三轮修的是同一件东西

| 原因 | 征兆 | 修法 |
|---|---|---|
| 只审了一部分 | `claim rows: 5` | 扩范围（R978） |
| 锚点/前提过期 | `SKIPPED` / `DECORATIVE` | 换锚点（R980） |
| 对象是空的 | `DECORATIVE` 而代码没变 | 造对象（R981） |

### 六、数字

| 度量 | R980 | R981 |
|---|---|---|
| 变异 fired / 总 | 35 / 36 | **36 / 36** |
| 装饰性 | 1 | **0** |
| 跳过 | 0 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 七、验证

```
cd replica
python tools/mutation-check.py                    -> 36 of 36；fired 36 / decorative 0 / skipped 0；restored GREEN
dotnet test --filter "FullyQualifiedName~CopyAuditConsistencyTests" -m:1  -> 通过 1
python tools/metrics_report.py                    -> 完整套件 exit 0  2200 通过 / 0 失败 / 0 跳过
```

### 八、教训

**「守卫是装饰性的」和「守卫没有对象」在日志里是同一行。
而前者要改守卫，后者改了守卫就是把一条正确的守卫改坏。**

**所以下一步永远是：先看代码有没有变。变了还绿 → 装饰性；没变 → 没有对象。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R981", BLOCKER)
    ensure(RSTATUS, "R981", BLOCKER)
    ensure(RVERDICT, "第 981 轮", VERDICT)
    ensure(BACKLOG, "R981", BACKLOG_ADD)

    note = (
        "\n## R981 补充 — **变异 36 / 36 fired，0 装饰性，0 跳过 → 判据 (e) 第二句成立**（套件 2200）\n\n"
        "R980 说 round 623 的守卫「对象为空」。这一轮的办法不是改守卫，是**让工具能指向别处**：\n"
        "① `copy_audit_report.py` 加 `--pool` / `--src` / `--out`（默认 = 原常量）\n"
        "② 守卫跑两次 —— 真实树（摘要 0 / 明细 0）+ fixture（键名在源码、值不在 → 正确代码 0/0，变异代码 0/1 → 红）\n\n"
        "**手工验过它真的红**（应用变异 → `[FAIL] DetailRowsMatchTheSummaryTotal` → 还原 → 通过）。\n\n"
        "全量：**running 36 of 36 → fired 36 / decorative 0 / skipped 0 · restored GREEN**。\n\n"
        "→ 判据 (e) 第二句现在成立，而成立方式不是把守卫改严，是**给守卫一个能说话的对象**。\n\n"
        "三轮（R978/R979-980/R981）修的是同一件东西 —— 检查沉默有三种原因：\n"
        "| 原因 | 征兆 | 修法 |\n|---|---|---|\n"
        "| 只审了一部分 | `claim rows: 5` | 扩范围 |\n"
        "| 锚点/前提过期 | `SKIPPED` / `DECORATIVE` | 换锚点 |\n"
        "| 对象是空的 | `DECORATIVE` 而代码没变 | 造对象 |\n\n"
        "数字：变异 36/36 · 套件 2200 · 陈旧度 0/0 · 函数数 173,952。\n\n"
        "纪律：先看代码有没有变。变了还绿 → 装饰性；没变 → 没有对象。\n\n"
        "下一轮：把变异度量（fired / decorative / skipped）注册进 METRICS —— 判据 (e) 需要一个能复算的数。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R981" not in h:
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
             for p, k in ((RBLOCK, "R981"), (RSTATUS, "R981"), (RVERDICT, "第 981 轮"), (BACKLOG, "R981")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R981: the last mutation fires too, so the suite is fully exercised at 36 of 36\n\n"
         "R980 found that round 623's mutation could not fire because the copy gap is zero, making the guard's invariant\n"
         " 0 == 0 under any edit to either loop, and left open how to give it a case with content.\n\n"
         "The fix is not to tighten the guard. The two predicates in the tool disagree in exactly one shape: a key whose name\n"
         " appears in the source while its value does not, which the wide predicate counts as in use and the narrow one does\n"
         " not. No such key exists in the real tree today, because the gap is zero. So the tool gained --pool, --src and\n"
         "--out, and the guard now runs twice: once over the real tree, where the invariant must hold, and once over a\n"
         " two-line fixture built to that shape, where reverting the detail loop to the narrow predicate makes the summary\n"
         " say zero while the detail says one.\n\n"
         "That the mutation now fails the guard was verified by hand before trusting it: apply the edit, run the guard, see\n"
         " it fail, restore, see it pass. Then the whole mutation suite: 36 of 36, all fired, none decorative, none skipped.\n\n"
         "So criterion (e)'s second clause holds, and it holds because the guard was given something to say rather than\n"
         " because it was made stricter.\n\n"
         "Three rounds have now been the same problem in three costumes. A check can fall silent because it examines part of\n"
         " its subject, because its anchor or premise expired, or because its subject is empty. All three look like a verdict\n"
         " in the log and all three take a different repair, and the tool has two words for them.\n\n"
         "Figures: mutations 35 of 36 to 36 of 36, decorative one to zero, skipped zero, suite 2200, freshness zero.\n\n"
         "The lesson is that decorative and empty are the same line in the log. Decorative means the guard does not work;\n"
         " empty means it has nothing to work on, and changing the guard for the second case would break a correct guard.\n"
         " The question to ask first is whether the code changed at all.\n\n"
         "One tool parameter set added, one guard rewritten to run twice; suite green at 2200."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()