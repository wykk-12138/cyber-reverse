"""Record R1051: the ninth item was answerable from code, and the scope is eleven not nine."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 第 9 项**由代码答了**；而范围是 **11 处**，不是 9（R1051）

**R1050 说第一步是答第 9 项（两个新行该不该进 `AntiBotVendors` 与 wall dispatch）。答了，而答案是**代码里写着的**。
然后把 9 处都改了 —— 红了 6 个，其中 **3 处是清单里没有的**。**

### ① 第 9 项的答案在 `AntiBotVendors` 自己的注释里

**`NamedButNotHandled` 那段写着 Riskified 为什么在那里：**

> 「Riskified 有三个 host 和四个 cookie，**而没有 handler**：`BuildRiskified` / `HandleRiskified` / `GetRiskified`
> 都缺席，**不像 `BuildForterSessionId` 或 `GetKasada`** 对 `All` 里的厂商那样。」

**→ 所以判据是**「有没有 handler 名字」**，而那是一个**可查的事实**，不是判断口味。**

| 厂商 | handler 名字 | 判定 |
|---|---|---|
| `BotDeflector` | `SubmitBotDeflectorChallenge` · `SolveBotDeflectorPow` · `SolveBotDeflectorIcons` | **三个 ⇒ 进 `All`** |
| `Vercel` | `VercelBotIdSolver` · `VercelChallengeHandler` | **两个 ⇒ 进 `All`** |

**→ 而 `State.Wired` 是**另一个问题**：它的注释是「Detect → solve → store all exist」——**复刻件侧**。
→ 复刻件没有这两个 solver ⇒ **`State.DetectedOnly`**（正是 R1025 给 queue-it 的读法：「recognised, with no solver here」）。
→ 而 wall dispatch 只派 `Wired` ⇒ **不动**。

**→ 所以第 9 项答完，而它把两处从「Wired」改成「DetectedOnly」，并把 `AntiBotVendors.All` 加了两个条目。**
**→ 两张表**不矛盾**：一张答「镜像能不能」，一张答「复刻件能不能」。**

### ② 而 9 处都改了，红了 6 个

| 红 | 性质 |
|---|---|
| `TheCookieTableHasFiveAndImpervaIsNotOne` | 清单第 8 项（「五」→ 六） |
| `FiveVendorsHaveCookiesAndPerimeterXIsOne` | 同上 |
| `AntiBotProtocolTests.FiveVendorsHaveCookieFamilies` | 同上 |
| **`AntiBotVendorTests.TheImageKnowsEightVendors`** | **第 10 处**：`All` 的数量被一个测试名钉着（8 → 10） |
| **`WallDispatchTests.OnlyWiredWallsAreDispatched`** | **第 11 处（真问题）**：它大概要求每行都要么 `Wired` 要么被明确登记「不派发」 |
| **`VendorWiringTests.TheGapsAreClassified`** | **第 11 处（真问题）**：新行的 `Gap` / `MarkerSource` 组合不在分类表里 |

**→ 所以第 9 项答对了两处（`Wired` → `DetectedOnly`），而没有消掉那两个红 ——
→ 说明它们的判据**不是**「是不是 Wired」，是别的东西，而那要读那两个测试的正文才知道。**

### ③ 三次尝试的轨迹，而那本身是结论

| 轮 | 估的范围 | 结果 |
|---|---|---|
| R1049 | **4 处** | 红 4（3 计数 + 1 真问题），回滚 |
| R1050 | **9 处** | 红 5（3 计数 + 2 真问题），回滚 |
| **R1051** | **9 处（含第 9 项）** | **红 6（3 计数 + 1 新计数 + 2 真问题），回滚** |

**→ 三次都在同一处回滚，而每次的清单都**更长**而不是更短。
→ 那说明：**这个仓的行数不是「一个数字」，而是被**若干测试名 + 若干分类表**共同钉着的，
→ 而它们无法靠「想一遍」列全。**
**→ 正确做法不是第四次尝试，是**先 grep 所有提到这批厂商或这个行数的测试**，一次看清全部钉子。**

### ④ 而这就是本轮的交付

**回滚后：`rows=7 · missing=7` · 套件 **2258 / 0 / 0** · 树绿（除生成的表）。**

| 项 | 状态 |
|---|---|
| 第 9 项（该不该进两张表） | **答了 —— handler 名字判据，两个都进 `All`，`State` 为 `DetectedOnly`** |
| 9 处改动 | 全部 applied 后又全部回滚 |
| 新增的第 10 处 | **`TheImageKnowsEightVendors`（`All` 从 8 → 10）** |
| 第 11 处（两个真问题） | `OnlyWiredWallsAreDispatched` · `TheGapsAreClassified` —— **要读正文才知道判据** |

### ⑤ 数字

| 度量 | R1050 | **R1051** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（回滚后）** |
| 函数数 | 174,293 | **174,293** |
| **第 9 项** | 「待答」 | **答了（handler 判据）** |
| **改了处数** | 5 | **7 patch / 9 处** |
| **transient 红** | 5 | **6（4 计数 + 2 真问题）** |
| **真实范围估计** | 9 | **11（其中 3 真问题）** |
| **`VendorWiring` 行数** | 7 | **7（回滚）** |
| **真厂商缺口** | 2 | **2（回滚）** |

### 教训

> **「列清单再改」在第三次失败了，而失败的方式一致：清单每次都少两处。
> → 因为钉子不在一个地方 —— 有的在**测试名里**（`ThreeOfSeven` · `FiveVendors` · `TheImageKnowsEight`），
> 有的在**分类表里**（`TheGapsAreClassified`），有的在**派发映射里**（`OnlyWiredWallsAreDispatched`）。**
> **→ 而它们只有一样东西是共同的：都在说「你改了一处，我还有意见」。
> → 所以下一次不是猜清单，是**让工具告诉我有几处** —— grep 出全部钉子，一次看完。**
"""

if "第 9 项**由代码答了**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1051 —— **第 9 项由代码答了；范围是 11 处不是 9；三次尝试后回滚**（套件 2258 绿）

### 第 9 项的答案在 `AntiBotVendors` 自己的注释里

**`NamedButNotHandled` 那段说 Riskified 在那里是因为 `Build/Handle/GetRiskified` **缺席**，
「不像 `BuildForterSessionId` 或 `GetKasada`」⇒ **判据是「有没有 handler 名字」**。

| 厂商 | handler | 判定 |
|---|---|---|
| `BotDeflector` | `SubmitBotDeflectorChallenge` · `SolveBotDeflectorPow` · `SolveBotDeflectorIcons` | **进 `All`** |
| `Vercel` | `VercelBotIdSolver` · `VercelChallengeHandler` | **进 `All`** |

**→ 而 `State.Wired` 是**复刻件侧**（Detect→solve→store 都要有）⇒ 复刻件无 solver ⇒ **`DetectedOnly`**。
→ wall dispatch 只派 `Wired` ⇒ 不动。**两张表不矛盾：一张答镜像，一张答复刻件。**

### 而 9 处全改后红了 6

| 红 | 性质 |
|---|---|
| 三处「五」 | 清单第 8 项 |
| **`TheImageKnowsEightVendors`** | **第 10 处**（`All` 8→10） |
| **`OnlyWiredWallsAreDispatched`** | **第 11 处（真问题）** |
| **`TheGapsAreClassified`** | **第 11 处（真问题）** |

**⇒ 答对了两处（`Wired`→`DetectedOnly`）而变化没消掉那两个红 ⇒ 它们的判据不是「是不是 Wired」，要读正文。**

### 三次尝试的轨迹

| 轮 | 估 | 红 |
|---|---|---|
| R1049 | 4 | 4（3 计数 + 1 真） |
| R1050 | 9 | 5（3 计数 + 2 真） |
| **R1051** | 9 | **6（4 计数 + 2 真）** |

**⇒ 每次清单都更长。钉子分散在**测试名**、**分类表**、**派发映射**三处，靠想列不全。**

### 数字

| 度量 | R1050 | **R1051** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **第 9 项** | 待答 | **答了** |
| **改了处数** | 5 | **7 patch / 9 处** |
| **transient 红** | 5 | **6（4 计数 + 2 真）** |
| **真实范围** | 9 | **11** |

**纪律**：下一次不是猜清单，是**grep 出全部钉子，一次看完**。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1051", NOTE)
append(RBLOCK, "R1051", "\n---\n\n## 475. **第 9 项由代码答了；真实范围 11 处；三次尝试后回滚**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1051: the ninth question was answerable from code, and the scope is eleven\n\n"
     "R1050 said the ninth item decided the other eight and had to be answered first. It did not need a judgement, it\n"
     "needed a reading: AntiBotVendors keeps Riskified in NamedButNotHandled because Build, Handle and Get are absent\n"
     " for it, unlike BuildForterSessionId and GetKasada. The test is whether a handler name exists.\n\n"
     "BotDeflector has three such names and Vercel has two, so both belong in All, which is the image-side list. State\n"
     " is a different question -- Wired means detect, solve and store all exist here, and neither has a solver in this\n"
     " workspace -- so both rows are DetectedOnly, R1025's reading of the same situation for queue-it. Wall dispatch\n"
     " only dispatches Wired rows, so it does not change. The two tables answer different questions and do not\n"
     " contradict each other.\n\n"
     "All nine changes went in, and six tests failed. Three are the cookie count spelled into test names, which was on\n"
     " the list. One is new: TheImageKnowsEightVendors pins the size of All, which goes from eight to ten. And two are\n"
     " the failures that survived from the previous attempt, unchanged by correcting Wired to DetectedOnly, which means\n"
     " their criterion is not what state a row has and can only be read from their bodies.\n\n"
     "So the scope is eleven, not nine, and three of them are real questions rather than counts. That is the third\n"
     " round reverted at this same place and each estimate was longer than the last: four, then nine, then eleven.\n\n"
     "The conclusion is not to guess a fourth list. The pins are scattered -- some in test names, some in a\n"
     " classification table, some in a dispatch map -- and nothing but reading them settles it. Next round greps every\n"
     " place that mentions these vendors or this row count, and reads all of it before touching a line.\n\n"
     "Figures: everything reverted, suite green at 2258, seven rows, two gaps, the ninth question answered, seven\n"
     " patches applied and undone, six transient failures of which two are real, and the scope estimate now at eleven.\n\n"
     "The lesson is that listing a change set by reasoning has failed three times running, and the fix is a query, not\n"
     " a better guess."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
