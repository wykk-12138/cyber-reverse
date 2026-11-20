"""Log R1295: the four skipped mutations, and the decorative one they uncovered."""

import io

B = """
## R1295 —— 判据 e) 的两个真缺口：**4 条 SKIP + 1 条装饰品守卫**，都已修

### 一、起因：我自己的改动让变异锚点失配

重跑 `mutation-check.py` 得到 `fired=55 / decorative=0 / skipped=4`，而 R1282 时是 `59/59/0`。
4 条 SKIP 全是**我前几轮的编辑**造成的：

| 变异 | 失配原因 |
|---|---|
| round 294 / 297 / 298 | R1290 给 41 行 `inferred: no image evidence` 追加了 R1266 后缀，锚点短语不再匹配 |
| round 1077 | R1294 把 Farfetch 的消息从 `endpoint unknown` 改成 `route unrecorded locally` |

**教训**：改文案就是在改变异锚点。改完必须重跑变异，否则"全部 fired"这条判据**悄悄失效**——
它报的是 SKIP 而不是红，很容易被当噪音略过。

### 二、修 SKIP 之后，暴露出**更严重的一条：装饰品守卫**

锚点修好后变成 `fired=58 / decorative=1 / skipped=0`。装饰品是 **round 1077**：
变异把消息缩短，测试**仍然绿**。

原因是我在 R1294 把断言写成了**文件级**：

```csharp
Assert.Contains("route unrecorded locally", source, ...)   // source = 整个文件
```

而 Farfetch 有 **7 条**消息，删掉一条，另外 6 条仍满足全部短语 ⇒ 守卫量的是文件，不是步骤。

**修法**：新增 `[Theory] EachStepCarriesTheReasonItself(step)`，**逐条**取步骤那一行并要求四个短语都在。

### 三、验证（单条手动，不靠全量）

`analysis/verify_1077_guard.py`：手动施加变异 → 只跑该守卫 → `finally` 还原。两次结果对照：

| 时机 | 结果 |
|---|---|
| 只有文件级断言时 | `VERDICT: STILL DECORATIVE (tests stayed green)` ← **证明第一次的"已修"是假的** |
| 加上逐条断言后 | `VERDICT: guard fired (tests went red)`，红的是 `EachStepCarriesTheReasonItself(step: "product")` |

### 四、最终数字

- 全量套件：**2485 通过 / 0 失败 / 2 跳过 / 2487**（+7 = 七条逐条守卫）
- 变异：**`total=59 fired=59 decorative=0 skipped=0`** ← 判据 e) 的变异部分达标
- 但同一份结果里 **`tree=RED`**，归因见下

### 五、`tree=RED` 的归因（不是我的改动）

`git status` 同时显示**并行会话**在动这些文件：`docs/CORE_COVERAGE.md`（13 行，生成物）、
`Hook.log`、`IDAHook.log`、`analysis/ARTIFACT_PROBES.json`，并删除了 `tools/read_nativeaot_string.py`。
变异末尾那次"restored tree"检查跑全量套件时，正好撞上这些并发写入。

**我的改动本身是绿的**：全量 2485/0/2，文档一致性 `DocsConsistency|ParityDoc|CoreCoverage` **21/21**。
本轮只暂存自己的三处（`mutation-check.py` / `FarfetchIsCoveredByTheOriginalTests.cs` / 记账脚本），
并行会话的文件一律不碰。

证据等级：Observation = 两轮 mutation 的 JSON 计数、两次 `verify_1077_guard.py` 的输出、21/21 与 2485/0/2 收据；
Inference = 「tree=RED 由并发写入造成」；**Unknown** = 并行会话那次 `core_coverage.py` 的结论（不属本轮）。
"""

V = """
---

## 第 1295 轮：判据 e) 收口——4 条 SKIP 修复，并揪出 1 条装饰品守卫

- 起因：R1290/R1294 改文案导致 4 个变异锚失配（`294`/`297`/`298`/`1077`）⇒ `skipped=4`。
- 修锚后暴露 round 1077 是**装饰品**：R1294 的断言写成**文件级**，删一条消息另外六条仍满足。
- 加 `[Theory] EachStepCarriesTheReasonItself` 逐条断言；手动单条验证从 `STILL DECORATIVE` 变为 `guard fired`。
- 最终：套件 **2485/0/2/2487**；变异 **59 fired / 0 decorative / 0 skipped**。
- 同一结果 `tree=RED`，归因并行会话（`CORE_COVERAGE.md` 等），我的改动全绿（文档测试 21/21）。
"""

H = """
## R1295 —— 判据 e)：4 SKIP + 1 装饰品全修；套件 2485/0/2/2487；变异 59/0/0

Observation：
- 两轮 mutation：`55/0/4` → 修锚 → `58/1/0` → 修守卫 → **`59/0/0`**。
- `verify_1077_guard.py` 两次对照：`STILL DECORATIVE` → `guard fired`（红在 `EachStepCarriesTheReasonItself(step:"product")`）。
- 套件 2485/0/2/2487（+7 逐条守卫）；`DocsConsistency|ParityDoc|CoreCoverage` 21/21。
- `tree=RED` 归因**并行会话**（改 `CORE_COVERAGE.md`/`Hook.log`/`IDAHook.log`，删 `read_nativeaot_string.py`）。

教训：**改文案=改变异锚**，改完必须重跑变异；`skipped` 不是红，最容易被忽略。
下轮：`metrics_report.py` 重跑刷新 METRICS（陈旧产物警告仍在），或处理并行会话结束后的 `tree` 复验。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
