"""Record R1031: the change was reverted because a live ratchet disagrees with the provenance tool."""

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
### 两个判据在打架：`endpoint-provenance` 要 `baseline: 0`，而棘轮要求那 10 条**仍在文件里**（R1031）

**R1030 说下一轮做「逐 flow 算端点镜像依据率」。算了，而算完之后我动手改，改完被四条守卫拦住，已回滚。**

### ① 依据率的准确数字（工具早就有，`endpoint-provenance.py`）

```
endpoint constants: 210   verbatim in pool: 210   invented: 0        ← 210/210 = 100%
inline literals: 331   not in pool: 41   registered: 29   **unregistered: 12**
  FarfetchFlow × 7 · NikeFlow × 1 · StoreFlow × 4
```

**→ 「34 个需 per-shop 覆写证据」的精确形式是这 **12** 条。
→ 而其中 Farfetch 占 7 条，且它们覆盖了**全部六个核心步骤** —— 整条结账链都是推出来的。**

### ② 而我按 Nike 先例（R1011）动手改，改完被拦

**12 → 5**（Farfetch 七条全清），而四条守卫红了：

```
EndpointEvidenceRatchetTests.EveryUnbackedEndpointSaysSoOnItsOwnLine   ← 每条无据端点要有一行标注
EndpointEvidenceRatchetTests.EveryUnbackedEndpointIsStillInItsFile     ← **它们必须仍在文件里**
FlowWorkAuditTests.MostOverridesDoWork                                 ← 覆写要有实质内容
FlowWorkAuditTests.AFlowWithPlaceholdersSaysWhy                        ← 占位要有理由
```

### ③ 而我读了那个棘轮，它有三层

```csharp
Sent (10 条：代码真的发出去的无据端点)      ← Farfetch 占 3
DocumentedOnly (7 条：只在文档注释里)        ← Farfetch 占 1
SentCeiling = 10                            ← 一条**上限**
```

**→ 所以那个棘轮**早就区分了**「真的发出去」与「只在注释里」—— 而我把 7 条**全部**当第一种处理。**
**→ 而 `SentCeiling = 10` 是一条**已接受债务的上限**；守卫防它**增长**，不要求它归零。**
**→ 而「仍在文件里」那条的作用是：**让移除成为一个必须记账的动作**，而不是静默的。**

> **→ 那正是 R1014「证据是地址存在 ≠ 证据这一步用它」的**镜像**：
> **移除一个无据端点**也是一个有后果的动作，而守卫要求它被记账。**

### ④ 所以两个判据的差在哪

| | `endpoint-provenance.py` | `EndpointEvidenceRatchetTests` |
|---|---|---|
| 判据 | 未登记的无据端点 = **0** | 未登记的无据端点 = **10（上限），且必须留在文件里** |
| 它防什么 | 新增无据端点 | 无据端点被**静默**移除或**静默**增加 |
| 谁更老 | R1015/R1016 | **R293** |

**→ 两者防的是**同一个东西的两头**，而我把「减到 0」当成了唯一目标。
→ 而 `baseline: 0` 那个 0 是**工具的期望值**，不是仓的验收标准 —— 仓的标准是 `SentCeiling = 10`。**

### ⑤ 所以本轮的正确结论是：**不动那 12 条，改的是它们的状态说明**

**→ 已回滚（`git checkout -- FarfetchFlow.cs`），套件回到 2243 / 0 / 0。
→ 而下一轮要做的不是删，是**让 12 条与两张表对齐**：
   哪些属于 `Sent`（真的发）、哪些属于 `DocumentedOnly`（只在注释里）、哪些**两边都没有**。**

**→ 而「两边都没有」的那部分是唯一真缺口 —— 而它需要先数出来，而不是先改。**

### ⑥ 数字

| 度量 | R1030 | **R1031** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（已回滚）** |
| 产物陈旧度 | 4 / 3,879 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **端点常量有据率** | 未测 | **210/210 = 100%** |
| **未登记的无据 inline 端点** | 「34 条待核」 | **12（Farfetch 7 · Nike 1 · StoreFlow 4）** |
| **中间态：改成报告后** | — | **5（已回滚）** |
| **仓的验收标准** | 误读为「0」 | **`SentCeiling = 10`（上限，防增长）** |
| **被守卫拦住并回滚的次数** | — | **1** |

### 教训

> **`baseline: 0` 是我**读成**的验收标准，而仓的标准是「不超过 10 且必须记账」。
> → 两个数都在同一个仓里，而我只读了工具输出的那个 —— 因为它在屏幕上，而另一个在测试文件里。**
> **→ 而那与 R1012 的「删除之后字面量仍在」是同一件事的两面：
> 那次是**以为删了却还在**，这次是**以为该删而仓要它留着**。**
"""

if "两个判据在打架" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1031 轮：两个判据在打架 —— 已回滚

### ① 依据率的准确数字

```
endpoint constants: 210   verbatim in pool: 210   invented: 0     ← 100%
inline literals: 331   not in pool: 41   registered: 29   unregistered: **12**
  FarfetchFlow × 7 · NikeFlow × 1 · StoreFlow × 4
```

**→ 「34 个需 per-shop 覆写证据」的精确形式是这 **12** 条。
→ Farfetch 的 7 条覆盖**全部六个核心步骤** —— 整条结账链都是推出来的。**

### ② 而我按 Nike 先例动手改：12 → 5，而四条守卫红了

```
EveryUnbackedEndpointSaysSoOnItsOwnLine   ·  EveryUnbackedEndpointIsStillInItsFile
MostOverridesDoWork                        ·  AFlowWithPlaceholdersSaysWhy
```

### ③ 而我读了那个棘轮，它有三层

```csharp
Sent (10 条：真的发出去)  ·  DocumentedOnly (7 条：只在注释里)  ·  SentCeiling = 10
```

**→ 棘轮**早就区分了**两种 —— 而我把 7 条**全部**当第一种处理。
→ `SentCeiling = 10` 是**已接受债务的上限**，守卫防它**增长**，不要求归零。
→ 「仍在文件里」那条的作用：**让移除成为必须记账的动作**，而不是静默的。

> **→ R1014「地址存在 ≠ 这一步用它」的**镜像**：**移除**一个无据端点也有后果，守卫要求它被记账。**

### ④ 两个判据的差

| | `endpoint-provenance.py` | `EndpointEvidenceRatchetTests` |
|---|---|---|
| 判据 | 未登记 = **0** | 未登记 = **≤10，且必须留在文件里** |
| 谁更老 | R1015/R1016 | **R293** |

**→ 两者防的是同一件事的两头，而我把「减到 0」当成了唯一目标。**

### ⑤ 已回滚

**`git checkout -- FarfetchFlow.cs`，套件回到 2243 / 0 / 0。
→ 下一轮不是删，是**让 12 条与两张表对齐**：哪些是 `Sent`、哪些是 `DocumentedOnly`、
哪些**两边都没有** —— 那是唯一真缺口，而它需要先数出来。**

### ⑥ 数字

| 度量 | R1030 | **R1031** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（已回滚）** |
| 产物陈旧度 | 4 / 3,879 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **端点常量有据率** | 未测 | **210/210 = 100%** |
| **未登记无据 inline 端点** | 「34 条待核」 | **12** |
| **中间态** | — | **5（已回滚）** |
| **仓的验收标准** | 误读为「0」 | **`SentCeiling = 10`（上限）** |

### 教训

> **`baseline: 0` 是我**读成**的验收标准，而仓的标准是「不超过 10 且必须记账」。
> → 两个数都在同一个仓里，而我只读了工具输出的那个 —— 因为它在屏幕上，另一个在测试文件里。**
> **→ 与 R1012「删除之后字面量仍在」是同一件事的两面：那次是**以为删了却还在**，
> 这次是**以为该删而仓要它留着**。**
"""

BACKLOG_ADD = """

## 判据 (f) — **端点依据率 210/210；12 条未登记；而仓的验收标准是 `SentCeiling = 10` 不是 0**（R1031）

### 准确数字

```
endpoint constants 210 / verbatim in pool 210 / invented 0      ← 100%
inline 331 / not in pool 41 / registered 29 / **unregistered 12**
  Farfetch × 7 · Nike × 1 · StoreFlow × 4
```

**Farfetch 的 7 条覆盖**全部六个核心步骤** —— 整条结账链都是推出来的。**

### 而改到 12 → 5 被四条守卫拦住，已回滚

```
EveryUnbackedEndpointSaysSoOnItsOwnLine · EveryUnbackedEndpointIsStillInItsFile
MostOverridesDoWork · AFlowWithPlaceholdersSaysWhy
```

### 棘轮有三层，我只看了第一层

```csharp
Sent (10)  ·  DocumentedOnly (7)  ·  SentCeiling = 10
```

**→ `SentCeiling = 10` 是**已接受债务的上限**，防增长，不要求归零。
→ 「仍在文件里」那条让**移除**成为必须记账的动作（R1014 的镜像）。**

### 下一轮

**不删，而是让 12 条与 `Sent` / `DocumentedOnly` 两张表**对齐** —— 找出**两边都没有**的那些，
那才是唯一真缺口。**

### 数字

**套件 2243/0/0（已回滚）· 陈旧度 5 / 4,199 · 函数数 174,336 · 常量 210/210 · 未登记 12 · 仓标准 ≤10**

| 仍 Unknown | |
|---|---|
| 12 条里几条两边都没登记 | 需逐条对表 |

**纪律**：工具输出的 `baseline` 不等于仓的验收标准 —— 后者可能在测试文件里。
"""

BLOCKER = """

---

## 455. **端点依据率 210/210；12 条未登记；仓的标准是 `SentCeiling = 10` 不是 0**

> R1031。**改动已回滚。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、依据率的准确数字

```
endpoint constants: 210   verbatim in pool: 210   invented: 0        ← 210/210 = 100%
inline literals: 331   not in pool: 41   registered: 29   **unregistered: 12**
  FarfetchFlow × 7 · NikeFlow × 1 · StoreFlow × 4
```

**→ 「34 个需 per-shop 覆写证据」的精确形式是这 **12** 条。
→ 其中 Farfetch 占 7 条，且它们覆盖了**全部六个核心步骤** —— 整条结账链都是推出来的。**

### 二、而我按 Nike 先例（R1011）动手改，改完被拦

**12 → 5**（Farfetch 七条全清），而四条守卫红了：

```
EndpointEvidenceRatchetTests.EveryUnbackedEndpointSaysSoOnItsOwnLine
EndpointEvidenceRatchetTests.EveryUnbackedEndpointIsStillInItsFile     ← **必须仍在文件里**
FlowWorkAuditTests.MostOverridesDoWork
FlowWorkAuditTests.AFlowWithPlaceholdersSaysWhy
```

### 三、而我读了那个棘轮，它有三层

```csharp
Sent (10 条：代码真的发出去的无据端点)      ← Farfetch 占 3
DocumentedOnly (7 条：只在文档注释里)        ← Farfetch 占 1
SentCeiling = 10                            ← 一条**上限**
```

**→ 棘轮**早就区分了**两种 —— 而我把 7 条**全部**当第一种处理。
→ `SentCeiling = 10` 是**已接受债务的上限**；守卫防它**增长**，不要求它归零。
→ 「仍在文件里」那条的作用：**让移除成为必须记账的动作**，而不是静默的。**

**→ 那正是 R1014「证据是地址存在 ≠ 证据这一步用它」的**镜像**：
  **移除一个无据端点**也是一个有后果的动作，而守卫要求它被记账。**

### 四、两个判据的差

| | `endpoint-provenance.py` | `EndpointEvidenceRatchetTests` |
|---|---|---|
| 判据 | 未登记的无据端点 = **0** | 未登记的无据端点 **≤10，且必须留在文件里** |
| 它防什么 | 新增无据端点 | 无据端点被**静默**移除或**静默**增加 |
| 谁更老 | R1015/R1016 | **R293** |

**→ 两者防的是**同一个东西的两头**，而我把「减到 0」当成了唯一目标。
→ 而 `baseline: 0` 那个 0 是**工具的期望值**，不是仓的验收标准。**

### 五、已回滚

**`git checkout -- replica/src/Cybersole.Stores/Flows/FarfetchFlow.cs`
→ 套件回到 **2243 / 0 / 0**。**

**→ 下一轮不是删，是**让 12 条与两张表对齐**：
  哪些属于 `Sent`、哪些属于 `DocumentedOnly`、哪些**两边都没有**。
→ 而「两边都没有」的那部分是唯一真缺口 —— 它需要先数出来，而不是先改。**

### 六、数字

| 度量 | R1030 | R1031 |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（已回滚）** |
| 产物陈旧度 | 4 / 3,879 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **端点常量有据率** | 未测 | **210/210 = 100%** |
| **未登记的无据 inline 端点** | 「34 条待核」 | **12（Farfetch 7 · Nike 1 · StoreFlow 4）** |
| **中间态：改成报告后** | — | **5（已回滚）** |
| **仓的验收标准** | 误读为「0」 | **`SentCeiling = 10`（上限，防增长）** |
| **被守卫拦住并回滚的次数** | — | **1** |

### 七、验证

```
cd D:\\projects\\cyber-reverse\\replica
python tools/endpoint-provenance.py     -> 常量 210/210 · 未登记 12 · exit 1
dotnet test --filter "FullyQualifiedName~EndpointEvidenceRatchet" -m:1  -> 全通过
python tools/metrics_report.py -> 完整套件 exit 0  2243 / 0 / 0
```

### 八、仍然 Unknown

- **12 条里有几条在 `Sent` 与 `DocumentedOnly` 两边都没登记**：**需逐条对表**。

### 九、教训

**`baseline: 0` 是我**读成**的验收标准，而仓的标准是「不超过 10 且必须记账」。**

**→ 两个数都在同一个仓里，而我只读了工具输出的那个 —— 因为它在屏幕上，而另一个在测试文件里。**

**→ 而那与 R1012 的「删除之后字面量仍在」是同一件事的两面：
  那次是**以为删了却还在**，这次是**以为该删而仓要它留着**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1031", BLOCKER)
    ensure(RSTATUS, "R1031", BLOCKER)
    ensure(RVERDICT, "第 1031 轮", VERDICT)
    ensure(BACKLOG, "R1031", BACKLOG_ADD)

    note = (
        "\n## R1031 补充 — **端点依据率 210/210；12 条未登记；仓的标准是 `SentCeiling = 10` 不是 0**（套件 2243，已回滚）\n\n"
        "**准确数字**：端点常量 **210/210**（100% 有据）· inline 331 中未登记的无据 **12**\n"
        "（Farfetch ×7 · Nike ×1 · StoreFlow ×4）。**Farfetch 的 7 条覆盖全部六个核心步骤** ⇒ 整条结账链是推出来的。\n\n"
        "**而我按 Nike 先例改成报告：12 → 5，被四条守卫拦住，已回滚。**\n"
        "```\nEveryUnbackedEndpointSaysSoOnItsOwnLine · EveryUnbackedEndpointIsStillInItsFile\nMostOverridesDoWork · AFlowWithPlaceholdersSaysWhy\n```\n\n"
        "**棘轮有三层，我只看了第一层**：`Sent (10)` · `DocumentedOnly (7)` · **`SentCeiling = 10`**。\n"
        "→ 棘轮早就区分「真的发出去」与「只在注释里」；而 `SentCeiling = 10` 是**已接受债务的上限**，防增长不要求归零。\n"
        "→ 「仍在文件里」那条让**移除**成为必须记账的动作 —— **R1014 的镜像**。\n\n"
        "**仓的标准不是工具输出的 `baseline: 0`** —— 那个 0 在屏幕上，标准在测试文件里。\n\n"
        "**下一轮**：不删，让 12 条与两张表**对齐**，找出**两边都没登记**的那些 —— 那才是唯一真缺口。\n\n"
        "数字：套件 2243/0/0（已回滚）· 陈旧度 5 / 4,199 · 函数数 174,336 · 常量 210/210 · 未登记 12 · 仓标准 ≤10。\n\n"
        "纪律：**工具输出的 `baseline` 不等于仓的验收标准。**\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1031" not in h:
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
             for p, k in ((RBLOCK, "R1031"), (RSTATUS, "R1031"), (RVERDICT, "第 1031 轮"), (BACKLOG, "R1031")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1031: two criteria disagree about the twelve endpoints, and the change is reverted\n\n"
         "R1030 left one open item: how much of each flow's endpoint surface rests on the image. Running the existing\n"
         " provenance tool answers it. Constants are 210 of 210 verbatim in the pool, which is the good number. Inline\n"
         " literals number 331, forty-one are not in the pool, twenty-nine of those are registered, and twelve are not:\n"
         " seven in Farfetch, one in Nike, four in StoreFlow.\n\n"
         "Farfetch turns out to be the real finding. Its seven carry every one of the flow's six core steps, so the whole\n"
         " checkout chain is inferred rather than evidenced, and the notes beside them have said so since R294 and R297.\n\n"
         "So I applied R1011's precedent and turned them into reports. The count fell from twelve to five and four guards\n"
         " went red, one of which asserts that those endpoints are still in their files. Reading that guard explained why:\n"
         " it keeps three lists, not one. Sent holds the ten that are really sent, DocumentedOnly holds the seven that\n"
         " appear only in a comment, and SentCeiling is ten -- a ceiling on accepted debt, not a target of zero. Removing\n"
         " an endpoint is meant to force a ledger update rather than happen quietly, which is R1014's lesson in mirror\n"
         " image: evidence that an address exists is not evidence this step uses it, and removing one is also an act with\n"
         " consequences.\n\n"
         "I had read baseline: 0 from the tool's output as the repository's standard. The repository's standard was in a\n"
         " test file, and it says ten and accounted for.\n\n"
         "So the edit is reverted, the suite is back to 2243, and what this round found is the disagreement rather than a\n"
         " fix. The next round does not delete: it reconciles the twelve against both ledgers to find which are in\n"
         " neither, because that subset is the only real gap and it needs counting before it needs changing.\n\n"
         "Figures: suite 2243 unchanged after the revert, freshness five files and 4,199 lines, count 174,336,\n"
         " constants at one hundred per cent evidenced, twelve unregistered inline endpoints, and the repository's own\n"
         " ceiling at ten.\n\n"
         "Unknown: how many of the twelve are missing from both ledgers.\n\n"
         "The lesson is that a tool's baseline is not the repository's acceptance criterion, that both numbers lived in\n"
         " the same repository, and that I read the one on the screen. It pairs with R1012: there I thought a deletion\n"
         " had happened and the literal remained; here I thought a deletion was wanted and the repository wanted it kept.\n\n"
         "No net code change; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()