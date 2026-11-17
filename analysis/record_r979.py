"""Record R979: the mutation suite is not fully fired, and the handoff head was 152 rounds stale."""

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
### 变异套件**没有全 fired**，而 `HANDOFF.md` 的头部落后 152 轮（R979）

**判据 (e)：套件绿、**变异测试全 fired**、文档数字全来自 METRICS.md。这一轮把三句都实测了一遍。**

### ① 变异：36 条里 **33 fired / 1 装饰性 / 2 跳过**

```
running 36 of 36 mutations
guard fired                                 ×33
GUARD IS DECORATIVE — tests stayed green    round 606 -- the metric index points at a section that does not exist
SKIPPED — anchor not found                  round 164 -- PARITY.md's module count drifts
SKIPPED — anchor not found                  round 623 -- the copy audit's detail loop goes back to the old predicate
restored tree: GREEN   （2215 通过 / 0 失败 / 2 跳过）
```

> **所以「变异测试全 fired」**不满足** —— 一条守卫是装饰性的，两条的锚点在源码里已经找不到了。**
> **而「跳过」比「装饰性」更隐蔽：那条变异**根本没跑**，所以它既不会红也不会绿，
> 而套件照样绿。** 一个不跑的检查和一个通过的检查在日志里长得一样。**

### ② 三处具体的洞

| 变异 | 状态 | 意思 |
|---|---|---|
| round 606 — 度量索引指向不存在的节 | **装饰性** | 把 `METRIC_CLAIMS.md` 的索引改坏，守卫 `EverySectionTheMetricIndexReferencesExists` **没红** |
| round 164 — `PARITY.md` 的模块数漂移 | **跳过** | 锚点 `**62 个注册模块` 在文档里已不存在 |
| round 623 — copy audit 的 detail 循环回到旧判据 | **跳过** | 锚点那段循环在 `copy_audit_report.py` 里已不存在 |

**同一条 round 164 的**UI 数**变异仍然 fired —— 所以不是整条坏了，是**那一条锚点**坏了。**

### ③ `HANDOFF.md` 的头部停在 **R826** —— 落后 152 轮

**那是每轮**第一读**的块。而它当时写着：**

| 它写的 | 而 METRICS 现在是 |
|---|---|
| 套件 `1766 / 0` | 见 METRICS |
| 类型缺失 `17` | 见 METRICS |
| 形状 `78` | 见 METRICS |
| **(d) claim 表 PASS —— `check_claims.py`：5 行，2 pass / 3 fail** | **那个「5 行」正是 R978 修掉的缺陷** |

> **最坏的一行是最后那行：它把「只审 5 行」当成判据 (d) 满足的证据写在了交接里。
> 而 R978 发现的那个缺陷，其实**早就被记录在这份交接文档里** —— 只是记成了一个通过。**
> **一个活的块装死数字，比没有块更坏，因为它被第一读、被相信。**

**已刷新：头部改成指针 + 复算命令，历史 1,845 行原样保留。**

### ④ 顺带修掉两条「数字不是来自 METRICS」

**① `metrics_report.py` 的 `VERDICT_BY_FILE` 原来是 **cwd 相对路径**：**

```
从 replica/ 跑:    replica/docs/COPY_QUEUE.md 存在 = True
从仓库根跑:        docs/COPY_QUEUE.md 存在 = False   <- 回退判定静默失效
```

**那个回退是给一个会在解释器关闭时崩溃的脚本兜底的 —— 而它取决于你站在哪。改成锚到 `ROOT`。**

**② `DEVIATIONS.md` L50 硬编码「215 类型 / **1,637 条**」，而 `descriptor entries` 现在是 951。
改成指针。**

**修后只看活文档（`GOAL` / `SESSION_STATE` / `DEVIATIONS` / `HANDOFF` 头部）：硬编码命中 **0 / 0 / 0 / 0**。**

### ⑤ 新守卫

**`HandoffHeadPointerTests`（2 用例）：头部必须提到 `METRICS.md`；头部不得复述任何当前度量值
（同一行有指针除外）。**数字边界用 `(?<![0-9A-Za-z_,])` —— 否则 `R951` 会被读成 951。**

### 数字

| 度量 | R978 | **R979** |
|---|---|---|
| 套件 | 2198 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **变异 fired / 总** | 未测 | **33 / 36** |
| **装饰性** | 未测 | **1** |
| **跳过** | 未测 | **2** |
| **活文档硬编码** | DEVIATIONS 1 处 | **0** |

### 教训

> **「跳过」是这一轮最值钱的发现。一条变异没跑，它就不红不绿，而整套仍然绿。
> 所以「全 fired」这句话只有一个来源敢说：**分母也报了**的那个。**
> **而 R978 和 R979 是同一件事的两面：一个检查审 5 行、一条变异没跑 —— 两者都在报通过。**
"""

if "变异套件**没有全 fired**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 979 轮：变异套件没有全 fired；HANDOFF 头部落后 152 轮

### ① 变异：36 条里 **33 fired / 1 装饰性 / 2 跳过**

```
running 36 of 36 mutations
guard fired                                 ×33
GUARD IS DECORATIVE — tests stayed green    round 606 -- the metric index points at a section that does not exist
SKIPPED — anchor not found                  round 164 -- PARITY.md's module count drifts
SKIPPED — anchor not found                  round 623 -- the copy audit's detail loop goes back to the old predicate
restored tree: GREEN
```

> **判据 (e) 的「变异测试全 fired」**不满足**。
> 而「跳过」比「装饰性」更隐蔽：那条变异**根本没跑**，不红不绿，套件照样绿。**

### ② 三处具体的洞

| 变异 | 状态 |
|---|---|
| round 606 — 度量索引指向不存在的节 | **装饰性**（守卫没红） |
| round 164 — `PARITY.md` 模块数漂移 | **跳过**（锚点 `**62 个注册模块` 已不存在） |
| round 623 — copy audit detail 循环回旧判据 | **跳过**（锚点循环已不存在） |

**round 164 的**UI 数**变异仍然 fired → 不是整条坏，是**那条锚点**坏。**

### ③ `HANDOFF.md` 头部停在 **R826**，落后 152 轮

| 它当时写的 | 而现在是 |
|---|---|
| 套件 `1766 / 0` | 见 METRICS |
| 类型缺失 `17` · 形状 `78` | 见 METRICS |
| **(d) PASS —— `check_claims.py`：5 行，2 pass / 3 fail** | **那正是 R978 修掉的缺陷** |

> **最坏的是最后一行：它把「只审 5 行」当成判据 (d) 满足的证据写进了交接。
> R978 发现的缺陷**早就被记录在这份文档里** —— 只是记成了一个通过。**
> **一个活的块装死数字，比没有块更坏，因为它被第一读、被相信。**

**已刷新：指针 + 复算命令；历史 1,845 行原样保留。**

### ④ 顺带修掉两条「数字不是来自 METRICS」

**① `metrics_report.py` 的 `VERDICT_BY_FILE` 是 cwd 相对路径 → 从仓库根跑时静默失效。改成锚到 `ROOT`。**
**② `DEVIATIONS.md` L50 硬编码「1,637 条」，而 `descriptor entries` 现在是 951。改成指针。**

**修后活文档硬编码命中 **0 / 0 / 0 / 0**。**

### ⑤ 新守卫

**`HandoffHeadPointerTests`（2 用例）：头部必须提到 `METRICS.md`；不得复述当前度量值。
数字边界用 `(?<![0-9A-Za-z_,])` —— 否则 `R951` 会被读成 951。**

### 数字

| 度量 | R978 | **R979** |
|---|---|---|
| 套件 | 2198 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **变异 fired / 总** | 未测 | **33 / 36** |
| **装饰性 / 跳过** | 未测 | **1 / 2** |
| **活文档硬编码** | 1 | **0** |

### 教训

> **「跳过」是这一轮最值钱的发现。一条变异没跑，它就不红不绿，而整套仍然绿。
> 所以「全 fired」只有一个来源敢说：**分母也报了**的那个。**
> **R978 和 R979 是同一件事的两面：一个检查审 5 行、一条变异没跑 —— 两者都在报通过。**
"""

BACKLOG_ADD = """

## 判据 (e) — **变异 33/36（1 装饰性 + 2 跳过）；HANDOFF 头部已刷新；活文档硬编码 0**（R979）

### 变异实测

```
running 36 of 36 mutations
guard fired ×33
GUARD IS DECORATIVE    round 606 -- the metric index points at a section that does not exist
SKIPPED (anchor gone)  round 164 -- PARITY.md's module count drifts
SKIPPED (anchor gone)  round 623 -- the copy audit's detail loop goes back to the old predicate
restored tree: GREEN
```

**→ 「变异测试全 fired」**不满足**。三处：round 606 守卫装饰性；round 164 / 623 锚点已不存在。**

### HANDOFF 头部

**停在 R826（落后 152 轮），且把「`check_claims.py`：5 行」写成判据 (d) 满足的证据 ——
那个 5 行正是 R978 修掉的缺陷。已刷新为指针 + 复算命令；历史 1,845 行保留。**

### 两条数字来源

**① `metrics_report.py` `VERDICT_BY_FILE` 改成锚 `ROOT`（原 cwd 相对 → 从仓库根跑静默失效）**
**② `DEVIATIONS.md` 的「1,637 条」改成指针（现值 951）**

### 新守卫

**`HandoffHeadPointerTests`（2 用例）**

### 数字

**套件 2200 · 陈旧度 0/0 · 函数数 173,952 · 变异 33/36 · 活文档硬编码 0**

| 仍 Unknown / 待办 | |
|---|---|
| round 606 守卫为何不红 | 未查（下一轮） |
| round 164 / 623 的锚点该换成什么 | 未查 |

**纪律**：一条变异没跑就不红不绿，而整套仍然绿 ——「全 fired」只有报了分母的来源敢说。
"""

BLOCKER = """

---

## 403. **变异 33/36（1 装饰性 + 2 跳过）→ 判据 (e) 不满足；HANDOFF 头部已刷新**

> R979。**修两处路径/数字 + 刷新交接头部 + 2 守卫。** 套件 **2200 通过 / 0 失败 / 0 跳过**。

### 一、变异实测

```
running 36 of 36 mutations
guard fired                                 ×33
GUARD IS DECORATIVE  round 606 -- the metric index points at a section that does not exist
SKIPPED — anchor not found  round 164 -- PARITY.md's module count drifts
SKIPPED — anchor not found  round 623 -- the copy audit's detail loop goes back to the old predicate
restored tree: GREEN
```

**→ 判据 (e) 的「变异测试全 fired」**不满足**。**

**而「跳过」比「装饰性」更隐蔽：那条变异**根本没跑**，不红不绿，而套件照样绿。
一个不跑的检查和一个通过的检查在日志里长得一样。**

### 二、三处具体的洞

| 变异 | 状态 | 意思 |
|---|---|---|
| round 606 — 度量索引指向不存在的节 | **装饰性** | 守卫 `EverySectionTheMetricIndexReferencesExists` 没红 |
| round 164 — `PARITY.md` 模块数漂移 | **跳过** | 锚点 `**62 个注册模块` 已不存在 |
| round 623 — copy audit detail 循环回旧判据 | **跳过** | 锚点那段循环已不存在 |

**而 round 164 的**UI 数**变异仍然 fired → 不是整条坏，是**那条锚点**坏了。**

### 三、`HANDOFF.md` 头部停在 R826，落后 152 轮

| 它当时写的 | 而 METRICS 现在是 |
|---|---|
| 套件 `1766 / 0` | 见 `docs/METRICS.md` |
| 类型缺失 `17` · 形状 `78` | 见 `docs/METRICS.md` |
| **(d) PASS —— `check_claims.py`：5 行，2 pass / 3 fail** | **那正是 R978 修掉的缺陷** |

**→ 最坏的是最后一行：它把「只审 5 行」当成判据 (d) 满足的证据写在了交接里。
R978 发现的缺陷**早就被记录在这份文档里** —— 只是记成了一个通过。
一个活的块装死数字，比没有块更坏，因为它被第一读、被相信。**

**已刷新：头部改成指针 + 复算命令；历史 1,845 行原样保留。**

### 四、顺带修掉两条「数字不是来自 METRICS」

**① `metrics_report.py` 的 `VERDICT_BY_FILE` 是 **cwd 相对路径**：**

```
从 replica/ 跑:    replica/docs/COPY_QUEUE.md 存在 = True
从仓库根跑:        docs/COPY_QUEUE.md 存在 = False   <- 回退判定静默失效
```

**那个回退是给一个会在解释器关闭时崩溃的脚本兜底的 —— 而它取决于你站在哪。改成锚 `ROOT`。**

**② `DEVIATIONS.md` L50 硬编码「215 类型 / **1,637 条**」，而 `descriptor entries` 现在是 951。改成指针。**

**修后活文档（`GOAL` / `SESSION_STATE` / `DEVIATIONS` / `HANDOFF` 头部）硬编码命中 **0 / 0 / 0 / 0**。**

### 五、新守卫

**`HandoffHeadPointerTests`（2 用例）：头部必须提到 `METRICS.md`；不得复述任何当前度量值（同行有指针除外）。
数字边界用 `(?<![0-9A-Za-z_,])` —— 否则 `R951` 会被读成 951。**

### 六、数字

| 度量 | R978 | R979 |
|---|---|---|
| 套件 | 2198 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **变异 fired / 总** | 未测 | **33 / 36** |
| **装饰性** | 未测 | **1** |
| **跳过** | 未测 | **2** |
| **活文档硬编码** | 1 处 | **0** |

### 七、验证

```
cd replica
python tools/mutation-check.py          -> 36 of 36；33 fired / 1 decorative / 2 skipped；restored GREEN
  （完整日志 analysis/mutation-run.log）
dotnet test --filter "FullyQualifiedName~HandoffHeadPointerTests" -m:1  -> 2 通过
python tools/metrics_report.py          -> 完整套件 exit 0  2200 通过 / 0 失败 / 0 跳过
```

### 八、仍然 Unknown / 待办

- **round 606 的守卫为何不红**：**Unknown** —— 未查。下一轮。
- **round 164 / 623 的锚点该换成什么**：**Unknown** —— 未查。

### 九、教训

**「跳过」是这一轮最值钱的发现。一条变异没跑，它就不红不绿，而整套仍然绿。**

**所以「全 fired」这句话只有一个来源敢说：**分母也报了**的那个。**

**而 R978 和 R979 是同一件事的两面：一个检查审 5 行、一条变异没跑 —— 两者都在报通过。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R979", BLOCKER)
    ensure(RSTATUS, "R979", BLOCKER)
    ensure(RVERDICT, "第 979 轮", VERDICT)
    ensure(BACKLOG, "R979", BACKLOG_ADD)

    note = (
        "\n## R979 补充 — **变异 33/36（1 装饰性 + 2 跳过）→ 判据 (e) 不满足；HANDOFF 头部已刷新**（套件 2200）\n\n"
        "`python tools/mutation-check.py` 实测 36 条：**33 fired / 1 装饰性 / 2 跳过**，restored GREEN。\n"
        "- **装饰性**：round 606 — 度量索引指向不存在的节，守卫 `EverySectionTheMetricIndexReferencesExists` 没红\n"
        "- **跳过**：round 164 — `PARITY.md` 模块数，锚点 `**62 个注册模块` 已不存在\n"
        "- **跳过**：round 623 — copy audit detail 循环，锚点那段循环已不存在\n\n"
        "→ **「跳过」比「装饰性」更隐蔽：那条变异根本没跑，不红不绿，而套件照样绿。**\n\n"
        "而 `HANDOFF.md` 头部停在 **R826**（落后 152 轮），写着套件 1766、类型缺失 17、形状 78，\n"
        "**并且把「`check_claims.py`：5 行」写成判据 (d) 满足的证据 —— 那正是 R978 修掉的缺陷**。\n"
        "→ 已刷新为指针 + 复算命令；历史 1,845 行原样保留。\n\n"
        "顺带两条：\n"
        "① `metrics_report.py` 的 `VERDICT_BY_FILE` 从 cwd 相对改成锚 `ROOT`（从仓库根跑时回退静默失效）\n"
        "② `DEVIATIONS.md` 的「1,637 条」改成指针（`descriptor entries` 现值 951）\n"
        "→ 修后活文档硬编码命中 **0 / 0 / 0 / 0**。\n\n"
        "新守卫 `HandoffHeadPointerTests`（2 用例）。\n\n"
        "数字：套件 2200 · 陈旧度 0/0 · 函数数 173,952 · 变异 33/36 · 活文档硬编码 0。\n\n"
        "纪律：一条变异没跑就不红不绿，而整套仍然绿 ——「全 fired」只有报了分母的来源敢说。\n\n"
        "下一轮：查 round 606 的守卫为何不红，以及 164 / 623 的锚点该换成什么。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R979" not in h:
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
             for p, k in ((RBLOCK, "R979"), (RSTATUS, "R979"), (RVERDICT, "第 979 轮"), (BACKLOG, "R979")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R979: the mutation suite is not fully fired, and the handoff head was 152 rounds stale\n\n"
         "Criterion (e) has three clauses and this round measured all of them instead of assuming.\n\n"
         "The mutation run: 36 of 36, and of those 33 fired, one guard stayed green while the defect was back, and two\n"
         " mutations were skipped because their anchors no longer exist in the source. So the clause is not met. The\n"
         " skips are the more insidious half: a mutation that never runs is neither red nor green, and the suite goes green\n"
         " around it, so a check that did not run and a check that passed look identical in the log. The decorative one is\n"
         " round 606's metric-index guard; the skips are round 164's module-count anchor in PARITY.md and round 623's detail\n"
         " loop in the copy audit. Round 164's sibling UI-count mutation still fires, so the route is fine and one anchor is\n"
         " not.\n\n"
         "docs/HANDOFF.md opened with a where-we-are block dated R826, a hundred and fifty-two rounds behind, quoting a suite\n"
         " total and two metric figures that had moved, and citing as evidence for criterion (d) the check that turned out\n"
         " to cover five rows of twenty-two. That is the worst line in it: the defect R978 found was already written down in\n"
         " this document, recorded as a pass. A live block holding dead numbers is worse than no block because it is read\n"
         " first and believed. The block is now pointers and commands, and the 1845 lines of history below it are untouched.\n\n"
         "Two smaller number-source defects went with it. metrics_report has a verdict-by-file fallback for a script that\n"
         " crashes during interpreter shutdown, and its path was relative to whatever cwd the caller had, so it engaged from\n"
         " replica and silently did not from the repo root. DEVIATIONS.md hard-coded a descriptor count of 1,637 against a\n"
         " current 951. Both fixed, and the four live documents now carry no hard-coded metric value.\n\n"
         "A guard test pins the head: it must name the single source and must not restate a current metric value, with digit\n"
         " boundaries so that a round label like R951 is not read as 951.\n\n"
         "Figures: suite 2198 to 2200, freshness zero, count 173,952, mutations 33 of 36 with one decorative and two skipped,\n"
         " hard-coded metric values in live documents one to zero.\n\n"
         "Unknown: why round 606's guard does not fire, and what anchors rounds 164 and 623 should point at now.\n\n"
         "The lesson is that skipped is worse than decorative. Neither is a pass, and only the run that reports its own\n"
         " denominator can say the suite fired.\n\n"
         "Two path and number fixes, the handoff head refreshed, two guard tests; suite green at 2200."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()