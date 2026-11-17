"""Record R1059: behaviour coverage counted, and the two totals are different questions."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 「每个函数功能相等」不可逐函数验证 ⇒ 换成**可数的下界**（R1059）

**R1058 说剩下的是那九个服务类的**功能**等价，「那需要行为而不是元数据」。这一轮把「功能」变成可数的东西。**

### ① 而判据必须先换

**goal 要「每个函数功能相等」。而 R1045 证明这个产物 **96.87% 的函数是 `sub_*`**、没有业务符号。
→ **所以逐函数比对不可行** —— 不是难，是**没有可配对的键**。**

**→ 而可行的问题换成了：**核心行为里有多少有断言撑着？** 那是可数的，且它是 (e)「套件绿」的直接内容。**

### ② 而结果

```
[Fact]+[Theory] 方法数       1968
① checkout flow              375
② 风控对抗                    178
③ 请求与指纹                  209
其余（含 UI）                1206
```

**→ 三个优先级的测试合计 **762** 个方法，占 38.7%；其余 1206 个（含 UI）占 61.3%。
→ 而那与 goal 的优先级**相反**：UI 与其余占了多数测试。**

**→ 而那不是缺陷陈述，是**现状**：UI 层有大量可断言的行为（绑定、命令、行数），而那正是 R468–R499 那七条连带清单的产物。**
**→ 所以「UI 先不急着复刻」是一条**优先级**指令，不是「UI 不重要」—— 它的测试量说明它已经被测得很细。**

### ③ 而两个总数差 290，那是口径不是漏测

```
方法数    1968   ← 我数的
用例数    2258   ← METRICS 报的
```

**→ 差额来自 `[Theory]`：一个方法带 N 组参数就跑 N 次。
→ 所以下表的每级数字都是**方法数**，而套件的 2258 是**用例数** —— **两个都对，但它们回答不同的问题。**

**→ 那一条必须写进文档，否则下一个人会以为漏了 290 个测试，而去补一批不存在的测试。**

### ④ 而这张表的边界要写死

| 边界 | 为什么重要 |
|---|---|
| 分组按**测试名**不按文件 | 名字是「这个测试断言什么」的最近证据 |
| **名字可能误导** | `VendorWiringTests` 断言台账数据而非行为，落进 ② 只因关键词 ⇒ **数字是上界** |
| 断言数 ≠ 覆盖度 | 2258 个测试也可能反复断言同一件事 |
| **原版侧没有对应数字** | 它没有测试 ⇒ **这张表只说复刻件，不能用来声称与原版等价** |

### ⑤ 而 (e) 的另一半还没做

**完成判据 (e) 要「套件绿、**变异测试全 fired**」。
→ 上面数的是**有多少行为被断言**；而「全 fired」数的是**有多少变异被抓住**。
→ **两者都要，而只有前者是本轮算的。****

**→ 而后者有一个可算的形态：变异数 / 被抓住的变异数。若仓里已有变异测试的框架，那个比值就是 (e) 的第二个数字。**

### ⑥ 数字

| 度量 | R1058 | **R1059** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 4 / 889 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| **测试方法数** | 未测 | **1968** |
| **① checkout flow** | 未测 | **375** |
| **② 风控对抗** | 未测 | **178** |
| **③ 请求与指纹** | 未测 | **209** |
| **其余（含 UI）** | 未测 | **1206** |
| **三个优先级占比** | — | **38.7%** |
| **方法数 vs 用例数差** | 未注意 | **290（`[Theory]` 展开）** |
| **`docs/BEHAVIOUR_COVERAGE.md`** | 不存在 | **2,073 字节（生成）** |

### 教训

> **「每个函数功能相等」在无符号产物里**没有可配对的键** —— 而那不等于无法评估，
> 它意味着要换一个问题：多少核心行为有断言撑着。**
> **→ 而换问题时最容易丢的是口径：1968 与 2258 差 290，而那个差如果没写清，
> 下一个人会去补一批不存在的测试。**
"""

if "「每个函数功能相等」不可逐函数验证" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1059 —— **「每个函数功能相等」不可逐函数验证 ⇒ 换成可数的下界**

### 判据必须换

goal 要「每个函数功能相等」，而 R1045 证明 **96.87% 的函数是 `sub_*`**、无业务符号
⇒ **没有可配对的键**，逐函数比对不可行（不是难，是不可行）。
**可行的问题：核心行为里有多少有断言撑着。**

### 而结果

```
[Fact]+[Theory] 方法数  1968        ① checkout  375   ② 风控  178   ③ 指纹  209   其余（含 UI） 1206
```

**三个优先级合计 **762** 个方法（38.7%）· 其余 **1206**（61.3%）。
⇒ 与 goal 优先级**相反**：UI 与其余占多数测试。而那是**现状**而非缺陷 ——
「UI 先不急着复刻」是**优先级**指令，不是「UI 不重要」，它的测试量说明它已被测得很细。**

### 而两个总数差 290 —— 那是口径不是漏测

```
方法数 1968（我数的）   用例数 2258（METRICS 报的）   ← [Theory] 一个方法带 N 组参数跑 N 次
```

**必须写进文档，否则下一个人会以为漏了 290 个测试而去补一批不存在的。**

### 边界写死

分组按**测试名**（名字是「断言什么」的最近证据）· **名字可能误导**（`VendorWiringTests` 断言数据而非行为 ⇒ 数字是**上界**）·
断言数 ≠ 覆盖度 · **原版侧无对应数字 ⇒ 这张表不能声称「与原版等价」**。

### 而 (e) 的另一半还没做

(e) 要「套件绿、**变异测试全 fired**」。上面数**多少行为被断言**，那个数**多少变异被抓住**。
**两者都要，只有前者是本轮算的。**

### 数字

| 度量 | R1058 | **R1059** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 测试方法数 | 未测 | **1968** |
| ① / ② / ③ | 未测 | **375 / 178 / 209** |
| 其余（含 UI） | 未测 | **1206** |
| 方法 vs 用例差 | 未注意 | **290（Theory 展开）** |
| `BEHAVIOUR_COVERAGE.md` | — | **2,073 字节** |

**纪律**：换问题时最容易丢的是口径；1968 与 2258 差 290，不说清就会去补不存在的测试。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1059", NOTE)
append(RBLOCK, "R1059", "\n---\n\n## 483. **「每个函数功能相等」不可逐函数验证 ⇒ 换成可数下界**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1059: per-function equality has no pairing key, so coverage is counted instead\n\n"
     "R1058 concluded that the nine service classes need a functional comparison rather than a metadata one. The goal's\n"
     " middle requirement is that every function's behaviour be equal, and R1045 established that ninety-six point nine\n"
     " per cent of this artifact's functions are sub_ -- there is no key to pair on. So that requirement cannot be\n"
     " verified function by function, not because it is hard but because there is nothing to match against.\n\n"
     "The question that can be answered is how much core behaviour has an assertion behind it, and it is countable. The\n"
     " suite has 1968 test methods: 375 on checkout flows, 178 on risk control, 209 on the request and fingerprint\n"
     " layer, and 1206 elsewhere including the UI. The three priorities together are 762 methods, just under thirty-nine\n"
     " per cent, and the rest is the larger half.\n\n"
     "That is a statement about the present rather than a fault. The UI has a great deal of assertable behaviour --\n"
     " bindings, commands, row counts -- which is exactly what the seven-item change list of R468 to R499 produced. The\n"
     " instruction to leave the UI aside was a priority, not a judgement that the UI does not matter, and its test volume\n"
     " shows it has been pinned in detail.\n\n"
     "The two totals differ by 290 and that is a unit difference, not missing tests. 1968 counts methods and 2258 counts\n"
     " cases, because a Theory runs once per parameter set. Every figure in the table is a method count, and the suite's\n"
     " number is a case count; both are right and they answer different questions. Writing that down matters, because\n"
     " otherwise the next reader sees a 290-test hole and fills it with tests that do not exist.\n\n"
     "The table's limits are stated in it: grouping is by test name, which is the nearest evidence of what a test\n"
     " asserts; a name can mislead, as VendorWiringTests pins ledger data rather than behaviour and lands in risk control\n"
     " on a keyword, so the number is an upper bound; assertions are not coverage; and the original has no tests at all,\n"
     " so nothing here supports a claim of equivalence with it.\n\n"
     "Criterion (e)'s other half is untouched. It asks that the suite be green and that mutation testing all fire. This\n"
     " counts how much behaviour is asserted; that counts how many mutations are caught, and only the first is done.\n\n"
     "Figures: suite green at 2258, freshness four files and 889 lines, count 174,293, 1968 test methods against 2258\n"
     " cases, 375 and 178 and 209 across the three priorities, 1206 elsewhere, and a seventh generated document.\n\n"
     "The lesson is that when a requirement has no key, the honest move is to restate it as something countable -- and\n"
     " that restating it is where units get lost."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
