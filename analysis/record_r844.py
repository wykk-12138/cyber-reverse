"""Record R844: the eight-flow step table, its one real number, and why that number is not a coverage figure."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 逐流程步骤对照（R844，`analysis/flow_step_gap.py`）

| 流程 | 镜像步数 | 同文件里的重写数 | **同名** | 不同名 |
|---|---|---|---|---|
| nike | 16 | 17 | **2** | 14 |
| popmart | 24 | 11 | **0** | 24 |
| johnlewis | 19 | 24 | **5** | 14 |
| demandware-classic | 12 | 10 | **3** | 9 |
| demandware-dual | 15 | 10 | **2** | 13 |
| collectplus-app | 17 | 23 | **2** | 15 |
| structure-token-multi | 15 | 23 | **4** | 11 |
| structure-token-single | 12 | 23 | **4** | 8 |
| **合计** | **130** | — | **22 (16.9%)** | **108** |

### 这个 22/130 是什么，不是什么

**是什么**：镜像这 8 个流程的 130 个步骤名，只有 22 个在复刻件的对应文件里有同名重写。

**不是什么**：

- **不是「覆盖 16.9%」。** `StoreFlow` 基类声明了 165 个步骤，**流程没重写不等于没实现** ——
  基类可能有默认实现，或该流程确实不需要那一步。
- **不是我映射准确。** `collectplus-app` / `structure-token-*` 我映射到
  `RetailFlows.cs` / `StoreFlow.cs` 这种共用文件，**里面 23 个重写不属于任何一个具体流程** ——
  所以那三行的「重写数」偏大而「同名数」偏小，**是我映射粗糙的结果。**
- **不是缺陷清单。** Nike 那 14 个不同名，R843 已查明是**粒度**：镜像 10 个可分别失败的结账阶段，
  复刻件 3 个粗步。

**它是什么**：**一张可以逐条追的清单。** 每一条不同名，最终要落在三种裁决之一：

1. **粒度合并** —— 复刻件的某个粗步做了它（Nike 那 10 条属此类）
2. **基类默认实现** —— 复刻件基类已有，只是没重写
3. **真缺**
"""

block = "\n## 逐流程步骤对照（R844）\n" + TABLE
body = io.open(DOC, encoding="utf-8").read()
if "逐流程步骤对照（R844" not in body:
    io.open(DOC, "a", encoding="utf-8").write(block)
    print("  ASYNC_OPS.md: per-flow table appended")
else:
    print("  ASYNC_OPS.md already has the per-flow table")

BLOCKER = """

---

## 268. 8 个流程 130 步，22 个同名 —— 而这个数**不是覆盖率**

> R844。`analysis/flow_step_gap.py` 常驻。`docs/ASYNC_OPS.md` 增逐流程表。未改产品代码。

### 一、把 R843 的手工对比机械化了

`StoreFlowSteps.cs` 有 8 个流程的步骤表（`Nike` `PopMart` `JohnLewis` `DemandwareClassic` `DemandwareDual`
`CollectPlusApp` `StructureTokenMulti` `StructureTokenSingle`），带 ordinal。
脚本把每个流程的步骤名与该流程在复刻件里的重写做交集。

```
nike                    16 步 · 17 重写 · 同名 2
popmart                 24 步 · 11 重写 · 同名 0
johnlewis               19 步 · 24 重写 · 同名 5
demandware-classic      12 步 · 10 重写 · 同名 3
demandware-dual         15 步 · 10 重写 · 同名 2
collectplus-app         17 步 · 23 重写 · 同名 2
structure-token-multi   15 步 · 23 重写 · 同名 4
structure-token-single  12 步 · 23 重写 · 同名 4
合计                   130 步 · 同名 22 (16.9%)
```

### 二、这个数不是覆盖率，必须写清三条理由

**① `StoreFlow` 基类声明了 165 个步骤 —— 没重写不等于没实现。**
基类可能有默认实现；某流程也可能确实不需要那一步。

**② 我的文件映射粗糙。** `collectplus-app` / `structure-token-*` 我映射到
`RetailFlows.cs` / `StoreFlow.cs` 这种共用文件 —— **里面 23 个重写不属于任何一个具体流程。**
所以那三行「重写数」偏大、「同名数」偏小，**是映射误差不是事实。**

**③ Nike 那 14 个不同名已查明是粒度。** 镜像 10 个可分别失败的结账阶段，复刻件 3 个粗步（R843）。

**所以 22/130 只说明一件事：这 130 个名字与复刻件那 8 个流程的同名重写交集很小。
交集小可以来自粒度、来自基类、来自映射误差，也可以来自真缺 —— 四种原因，本轮没分开。**

### 三、它有用在哪

**它把「未覆盖的每条写为什么」变成了 108 条可逐条追的清单**，每条要落在三种裁决之一：

1. **粒度合并** —— 复刻件某个粗步做了它
2. **基类默认实现** —— 基类已有，只是没重写
3. **真缺**

**而第 3 类才是缺陷。**

### 四、验证

```
python analysis\\flow_step_gap.py
  8 个流程；130 步；同名 22；合计行给出百分比
docs\\ASYNC_OPS.md 增表
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **那 108 条里各属哪一类**：**Unknown** —— 本轮只给了清单，没做裁决。
- **`popmart` 24 步同名 0** 是最大的一块：**R835/R836/R838 已证抽签/展览/预约共 17 步复刻件没有，
  但剩下 7 步（`GetOrders` `GetInstoreOrders` 等）属哪一类未判。**
- **映射的正确做法**：**Unknown** ——
  `Registry.cs` 的 63 个模块与这 8 个流程表的关系未建立（R843 已记为 Unknown，本轮仍未建）。

### 六、教训

**我造出了一个看起来很吓人的数（16.9%），而它有三种非缺陷解释。**

**如果我在文档里只写「22/130」，下一轮的人会把它当覆盖率，然后去「修」那 108 条 ——
而其中大部分可能只是粒度不同。**
**这就是「一个错的总数比没有总数更坏」的具体形态；而错的地方不在数字，在它旁边没写清楚它是什么。**
"""

VERDICT = """

---

## 第 844 轮：8 个流程 130 步，22 个同名 —— 而这个数不是覆盖率

### 把 R843 的手工对比机械化了

| 流程 | 步数 | 同名 | 不同名 |
|---|---|---|---|
| nike | 16 | **2** | 14 |
| popmart | 24 | **0** | 24 |
| johnlewis | 19 | **5** | 14 |
| demandware-classic | 12 | **3** | 9 |
| demandware-dual | 15 | **2** | 13 |
| collectplus-app | 17 | **2** | 15 |
| structure-token-multi | 15 | **4** | 11 |
| structure-token-single | 12 | **4** | 8 |
| **合计** | **130** | **22 (16.9%)** | **108** |

### 为什么它不是覆盖率（三条理由）

1. **`StoreFlow` 基类声明 165 个步骤 —— 没重写 ≠ 没实现**
2. **我的文件映射粗糙**：`collectplus-app`/`structure-token-*` 映射到共用文件 `RetailFlows.cs`/`StoreFlow.cs`，
   **里面 23 个重写不属于任何一个具体流程** → 那三行「重写数」偏大、「同名数」偏小
3. **Nike 那 14 个已查明是粒度**（R843：镜像 10 个可分别失败的结账阶段 vs 复刻件 3 个粗步）

**交集小可以来自粒度、基类、映射误差，也可以来自真缺 —— 四种原因，本轮没分开。**

### 它有用在哪

**把「未覆盖的每条写为什么」变成 108 条可逐条追的清单**，每条落在：**粒度合并 / 基类默认 / 真缺**（只有第三类是缺陷）。

### 仍然 Unknown

**108 条各属哪一类**（只给清单未裁决）· **`popmart` 24 步同名 0 是最大一块**
（抽签/展览/预约 17 步已证没有，剩 7 步 `GetOrders`/`GetInstoreOrders` 等未判）·
**映射的正确做法**（`Registry.cs` 63 模块 ↔ 8 个流程表，关系未建）

### 教训

> **我造出一个看起来很吓人的数（16.9%），而它有三种非缺陷解释。**
> **如果只写「22/130」，下一轮的人会把它当覆盖率，去「修」那 108 条 —— 而大部分可能只是粒度不同。**
> **这就是「一个错的总数比没有总数更坏」的具体形态；错的地方不在数字，在它旁边没写清楚它是什么。**
"""

BACKLOG_ADD = """

## 判据 (f) — 逐流程步骤对照（R844）：130 步 · 22 同名

**工具**：`python analysis\\flow_step_gap.py`。表在 `docs/ASYNC_OPS.md`。

| 流程 | 步数 | 同名 | 不同名 |
|---|---|---|---|
| nike | 16 | 2 | 14 |
| popmart | 24 | 0 | 24 |
| johnlewis | 19 | 5 | 14 |
| demandware-classic | 12 | 3 | 9 |
| demandware-dual | 15 | 2 | 13 |
| collectplus-app | 17 | 2 | 15 |
| structure-token-multi | 15 | 4 | 11 |
| structure-token-single | 12 | 4 | 8 |
| **合计** | **130** | **22** | **108** |

### 不是覆盖率的三个理由

1. **`StoreFlow` 基类 165 步 —— 没重写 ≠ 没实现**
2. **文件映射粗糙** —— `collectplus-app`/`structure-token-*` 指向共用文件，23 个重写不属于任何具体流程
3. **Nike 14 个不同名是粒度**（镜像 10 细步 vs 复刻件 3 粗步）

**交集小有四种原因：粒度 / 基类 / 映射误差 / 真缺。本轮未分。**

### 108 条的裁决框架

**每条落在：粒度合并 · 基类默认实现 · 真缺（只有第三类是缺陷）。**

| 仍 Unknown | |
|---|---|
| 108 条各属哪类 | 未裁决 |
| `popmart` 24 步同名 0 | 抽签/展览/预约 17 步已证没有；剩 7 步未判 |
| `Registry.cs` 63 模块 ↔ 8 流程表 | 关系未建 |

**纪律**：**一个错的总数比没有总数更坏 —— 错的地方不在数字，在它旁边没写清楚它是什么。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R844", BLOCKER)
    ensure(RSTATUS, "R844", BLOCKER)
    ensure(RVERDICT, "第 844 轮", VERDICT)
    ensure(BACKLOG, "R844", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R844" not in h:
        h += ("\n## R844 补充 — 逐流程步骤对照\n\n"
              "`analysis/flow_step_gap.py`：8 个流程 130 步，与复刻件同名重写 **22（16.9%）**。\n"
              "**这不是覆盖率**：① `StoreFlow` 基类 165 步，没重写 ≠ 没实现；② 文件映射粗糙（共用文件里的重写不属于具体流程）；"
              "③ Nike 14 个不同名是**粒度**（镜像 10 细步 vs 复刻件 3 粗步）。\n"
              "**108 条裁决框架**：粒度合并 / 基类默认 / 真缺（只有第三种是缺陷）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R844"), (RSTATUS, "R844"), (RVERDICT, "第 844 轮"), (BACKLOG, "R844")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R844: eight flows, 130 steps, 22 name matches -- and why that is not a coverage figure\n\n"
         "R843 compared Nike by hand; this runs the same comparison for all eight flows that StoreFlowSteps carries, so"
         " the table exists once and mechanically. Nike 16 steps and 2 matches, PopMart 24 and 0, JohnLewis 19 and 5,"
         " demandware-classic 12 and 3, demandware-dual 15 and 2, collectplus-app 17 and 2, the two structure-token"
         " flows 15 and 12 with 4 each. One hundred and thirty steps, twenty-two name matches, 16.9 percent.\n\n"
         "That number must not be read as coverage, and the reasons are worth stating before anyone cites it. StoreFlow's"
         " base class declares 165 steps, so a flow that does not override one has not necessarily failed to implement"
         " it. My file mapping is crude: collectplus-app and the structure-token flows are mapped to shared files like"
         " RetailFlows and StoreFlow, where twenty-three overrides belong to no single flow, which inflates the override"
         " count on those rows and deflates the match count. And Nike's fourteen misses are already known to be"
         " granularity rather than absence, from R843: ten independently-failing checkout stages in the image against"
         " three coarse steps in the replica.\n\n"
         "So a small intersection has four possible causes -- granularity, base-class default, mapping error, genuine"
         " absence -- and this round did not separate them.\n\n"
         "What the table does give is 108 rows that can be chased one at a time, each landing on one of three verdicts:"
         " merged into a coarser step, already in the base class, or genuinely missing. Only the third is a defect.\n\n"
         "The risk is specific and worth naming. A figure like 16.9 percent looks alarming, and if the document only"
         " said 22 of 130 the next reader would treat it as coverage and set about fixing 108 items, most of which are"
         " probably differences of granularity. A wrong total is worse than no total, and here the wrongness is not in"
         " the arithmetic but in what the surrounding text fails to say about what the arithmetic measures.\n\n"
         "Unknown: which of the three categories each of the 108 falls into; the seven remaining PopMart steps such as"
         " GetOrders and GetInstoreOrders, since R835 through R838 established the seventeen draw, exhibit and"
         " reservation steps are absent; and how the sixty-three modules in Registry.cs relate to these eight flow"
         " tables, a relation still not built.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
