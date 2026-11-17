"""Record R1049: both vendors decided Local with hard evidence, and the row addition was reverted."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 两个厂商都**定了 `Local`**，而补行要改 4 个守卫 —— 本轮回滚（R1049）

**R1048 说下一轮给 `BotDeflector` 与 `Vercel` 各补一行，先定 `Solver`。定了，证据很硬；而补行的连带改动
比预想多，所以本轮**回滚**，把补行留成明确任务。**

### ① 取证：两个都是**原版自解**，不是交给第三方

```
BotDeflector   <SubmitBotDeflectorChallenge>d__38
               <SolveBotDeflectorPow>d__39
               <SolveBotDeflectorIcons>d__40
               _passed0_botDeflectorFingerprint
Vercel         VercelBotIdSolver
               x-vercel-challenge-token / -solution / -version
               SubmitPath /.well-known/vercel/security/request-challenge
               _vcrcs · SupportedVersion
```

**→ BotDeflector 有**三个状态机体**（提交 · 解 PoW · 解图标）+ 自己的指纹字段 ⇒ 自解自造身份。
→ Vercel 有**完整协议**（三个头 + 一条提交路径 + cookie + 版本常量）⇒ 自解。
→ **所以两个都是 `Solver.Local` / `Relayed false`，不是 `Unknown`。**

**→ 而那是 R1048 那句「无第三方指向不等于自建」的正面回答：这次**有**指向，指向**原版自己**。****

### ② 而我加了行，然后回滚

**加了两行后：`wiring rows=9 · missing=5`（真厂商缺口归零）。而套件红了 **4** 个：**

| 测试 | 为什么红 |
|---|---|
| `VendorWiringTests.ThreeOfSevenAreWired` | **名字里就写了「七分之三」** —— 行数增了两个 |
| `VendorSolvingModeTests.TheRestAreLocalOrNone` | 枚举所有行 |
| `VendorSolvingModeTests.TheTwoAxesAreIndependent` | 同上 |
| `VendorWiringTests.TheCookieColumnAgreesWithTheProtocolTable` | 新行的 cookie（`_vcrcs`）没在**协议表**里登记 |

**→ 按纪律判断：前三个是**形状**（枚举与计数），改数字 + 写原因即可；
→ 第 4 个是**真问题** —— `_vcrcs` 在镜像里有据，但在复刻件的协议表里没登记，而补登记是**另一件要证的事**，不该顺手做。**

**→ 而本轮预算不够改 4 个守卫 + 处理协议表，所以 `git checkout` 回滚，套件回 **2258 / 0 / 0**。**

### ③ 所以本轮的交货是**证据**，不是代码

| 项 | 状态 |
|---|---|
| `BotDeflector` 的 `Solver` | **`Local`（三个体 + 指纹字段）** |
| `Vercel` 的 `Solver` | **`Local`（三头 + 提交路径 + cookie + 版本）** |
| 两行是否加上 | **否 —— 回滚** |
| `VendorWiring` 行数 | **7（未变）** |
| 真厂商缺口 | **2（未变）** |

**→ 而那是一件要说清的事：**拿到证据**与**改进去**是两件事，而这一轮只完成了前一件。
→ 硬把代码塞进去再改 4 个守卫而不看清第 4 个，就是 R1031 那次回滚的形状。****

### ④ 下一轮的明确任务（四步，都已定位）

1. **`BotDeflector` 加行**：`Row("botdeflector", "BotDeflector", null, State.Wired, …, MarkerSource.ImageLiteral, Gap.None, Solver.Local, false)`
2. **`Vercel` 加行**：`Row("vercel", "x-vercel-challenge-token", "_vcrcs", State.Wired, …, ImageLiteral, None, Local, false)`
3. **改 3 个守卫的数字/枚举**：`ThreeOfSevenAreWired`（7→9、3→5）· `TheRestAreLocalOrNone` · `TheTwoAxesAreIndependent`
4. **第 4 个守卫要先定**：`_vcrcs` 该进协议表，还是该把那行的 cookie 列设 `null`（因为协议表没登记）——
   **那是一个真判断，不是数字调整。**

### ⑤ 数字

| 度量 | R1048 | **R1049** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（回滚后）** |
| 产物陈旧度 | 0 / 0 | **1 / 277**（文件已回滚但 mtime 更新） |
| 函数数 | 174,293 | **174,293** |
| **`BotDeflector` 的 Solver** | 未定 | **`Local`（有据）** |
| **`Vercel` 的 Solver** | 未定 | **`Local`（有据）** |
| **`VendorWiring` 行数** | 7 | **7（未变 —— 回滚）** |
| **真厂商缺口** | 2 | **2（未变）** |
| **加行时的红** | — | **4（3 形状 + 1 真问题）** |

### 教训

> **「先定 Solver」这一步完成了，而它揭示了下一步比预期大：补一行在这个仓里是**四件事**，不是一件。
> → 而那正是 R468–R499 那七条连带清单的同一个形状 —— **改一个东西，有 N 处要同步**。
> → 而这次我识别对了（3 形状 + 1 真问题），也**没有**硬塞进去。
> → 所以本轮的产出是「下一轮的任务变清楚了」，而不是「加了行」。**
"""

if "两个厂商都**定了 `Local`**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1049 —— **两个厂商都定了 `Local`（有据）；补行因 4 个守卫回滚，任务转下一轮**（套件 2258 绿）

### 取证（决定性）

```
BotDeflector  <SubmitBotDeflectorChallenge>d__38 · <SolveBotDeflectorPow>d__39 · <SolveBotDeflectorIcons>d__40
              _passed0_botDeflectorFingerprint
Vercel        VercelBotIdSolver · x-vercel-challenge-{token,solution,version}
              SubmitPath /.well-known/vercel/security/request-challenge · _vcrcs · SupportedVersion
```

**⇒ 两个都是原版**自解**（`Solver.Local` / `Relayed false`），不是 `Unknown`。**
→ 而那是 R1048「无第三方指向不等于自建」的正面回答：这次**有**指向，指向**原版自己**。

### 而补行回滚了

加两行后 `rows=9 · missing=5`（真缺口归零），但套件红 **4**：

| 测试 | 性质 |
|---|---|
| `ThreeOfSevenAreWired`（名字就写七分之三） | **形状**（7→9、3→5） |
| `TheRestAreLocalOrNone` | **形状**（枚举） |
| `TheTwoAxesAreIndependent` | **形状**（枚举） |
| `TheCookieColumnAgreesWithTheProtocolTable` | **真问题**：`_vcrcs` 没在协议表里登记 |

**→ 前三个改数字；第四个是**真判断**（`_vcrcs` 该进协议表，还是该行 cookie 设 `null`），不该顺手做。
→ 预算不够 ⇒ `git checkout` 回滚，套件回 **2258 / 0 / 0**。**

### 下一轮四步（都已定位）

1. `BotDeflector` 加行（marker `BotDeflector` · cookie `null` · `Wired` · `ImageLiteral` · `Gap.None` · `Local` · false）
2. `Vercel` 加行（marker `x-vercel-challenge-token` · cookie `_vcrcs` · 同上）
3. 改 3 个守卫的数字/枚举（`ThreeOfSevenAreWired` 7→9、3→5；另两个加两个名字）
4. **先定第 4 个**：`_vcrcs` 进协议表，或把该行 cookie 设 `null`

### 数字

| 度量 | R1048 | **R1049** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 0 / 0 | **1 / 277**（回滚但 mtime 更新） |
| 函数数 | 174,293 | **174,293** |
| **两个 Solver** | 未定 | **都是 `Local`（有据）** |
| **台账行数** | 7 | **7（回滚）** |
| **加行时的红** | — | **4（3 形状 + 1 真问题）** |

**纪律**：拿到证据与改进去是两件事。硬塞代码再改守卫而不看清第 4 个，就是 R1031 那次回滚的形状。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1049", NOTE)
append(RBLOCK, "R1049", "\n---\n\n## 473. **两个厂商都定了 Local（有据）；补行因 4 个守卫回滚**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1049: both vendors are solved locally, and adding their rows was reverted\n\n"
     "R1048 left two rows to add and one decision to make first: which Solver each gets. The decision is made and the\n"
     " evidence is hard, which is the round's real product.\n\n"
     "BotDeflector has three state-machine bodies -- submit, solve a proof of work, solve an icon grid -- plus a\n"
     " fingerprint field of its own. A vendor that submits, solves both challenge kinds and builds the identity it\n"
     " presents is solving locally. Vercel is a whole protocol in the image: token, solution and version headers, a\n"
     " submit path under .well-known, a _vcrcs cookie and a supported-version constant. Both are Local with relaying\n"
     " false, not Unknown, and that answers R1048's warning from the other side -- this time there is a pointer, and\n"
     " it points at the original itself.\n\n"
     "Adding the rows made the reconciliation read nine rows and five missing, with the genuine vendor gap at zero. It\n"
     " also turned four guards red. Three are shape: a test literally named ThreeOfSevenAreWired, and two that\n"
     " enumerate the rows. The fourth is not shape -- it checks that every cookie in the wiring table is also in the\n"
     " protocol table, and _vcrcs is evidenced in the image but never registered there.\n\n"
     "That fourth one is a real judgement, not a number to nudge: either the protocol table gains _vcrcs, or the\n"
     " wiring row claims a cookie it cannot back. Deciding that is its own piece of work, and doing it hastily while\n"
     " fixing three counts is how R1031 went wrong. So the change went back, the suite is green at 2258, and the four\n"
     " steps are written down with their locations.\n\n"
     "Figures: suite 2258 passing, freshness one file and 277 lines because the revert still touches the file's\n"
     " timestamp, count 174,293, two solvers now decided, seven rows unchanged and two genuine gaps unchanged.\n\n"
     "The lesson is that deciding Solver was the small half. Adding a row here is four changes, not one, and knowing\n"
     " that before writing is the difference between a partial round that reports cleanly and one that has to be\n"
     " undone."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
