"""Record R1025: queue-it is not only a queue, and NotAChallenge loses its last user."""

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
### queue-it **不只是队列**；而 `NotAChallenge` 失去唯一使用者（R1025）

**R1024 说下一轮做 queue-it softblock（`Error Solving Queue-it (Softblock)` 与 `NotAChallenge` 矛盾）。做了，
而矛盾比那一句更深。**

### ① 八条证据说 queue-it 有挑战面

```
Fetching Queue-it challenge                0x146d8ea24   ← 它 serve 挑战
Error Solving Queue-it (Softblock)          0x146d0d1b4   ← 原版**尝试解**
Error Initiliazing Queue-it (Softblock)     0x146d0d14c   ← 且会初始化失败
Queue-IT banned, rotating proxy             0x146e57fb4   ← 也会换代理
Unsupported Queue-it BotDeflector page      0x146f1471c   ← BotDeflector 是它的反机器人产品
Redirected into a Queue-it waiting room     0x146e63a6c   ← 等待室是真的
/softblock                                  0x146ab8f6c
/challengeapi/queueitcaptcha/challenge/     0x146ab2cb4   ← **CAPTCHA 端点**
X-queueit-challange-{reason,customerid,eventid,hash,ruleid,rulename} + X-queueit-redirect   ← 7 个 header
QueueITAccepted · QueueITAccepted-SDFrts345E-V3_ · QueueitEnqueueToken · queueittoken
```

**→ 所以「队列不是墙，正确处置是等待」这句话**一半对**：等待**是**处置的一部分。
→ 而「等待是**全部**处置」**错了** —— 它还有 challenge · solver · BotDeflector · captcha。**

### ② 而这是一个**熟悉的形状**

| 轮 | 从 | 推出 | 实际 |
|---|---|---|---|
| R1018 | 「`captcha-delivery` 是挑战域」 | 「它属 perimeterx」 | 属 datadome |
| R1023 | 「只有换代理文案」 | 「原版不解 perimeterx」 | 有 `Solving PerimeterX` |
| **R1025** | 「我们看到的是等待室」 | **「它只是队列」** | **还有挑战面** |

**→ 三次都是**从「我看到的」推出「只有这些」**。**
**→ 而那正是 AGENTS §2.7b 那条「抽样不等于全量」的行为版：一个表面不等于全部表面。**

### ③ 改了什么

**`queue-it` 行：`State.NotAChallenge` → `DetectedOnly`，Note 列出八条证据并写明
「waiting is part of the handling rather than all of it」。**

**→ 而 `DetectedOnly` 与 R1024 给 akamai 的那个值是同一个 —— 而两行的理由不同：
akamai 是「镜像解它，我们没写」；queue-it 是「镜像解 softblock，我们只等待」。
→ 两者都是「镜像有而我们没有」，所以同一个 State 是对的。**

### ④ 而 `NotAChallenge` 现在**没有使用者**

**→ 保留枚举值（删掉会让分类法静默收缩），并加 4 条守卫其中之一专门钉「无使用者」。**

| 守卫 | 断言 |
|---|---|
| `TheRowIsNoLongerNotAChallenge` | `State == DetectedOnly` |
| `TheMarkerAndGapAreUnchanged` | marker/cookie/Gap 未被这次更正碰到 |
| `TheNoteNamesTheChallengeSurface` | Note 里点名五条证据（可查） |
| **`NoRowUsesNotAChallengeAnyMore`** | **无行使用该值** |

**→ 第 4 条是那个枚举值的**墓碑**：它记录「这个分类曾有一个用例，而现在没有」，而不是悄悄消失。**

### ⑤ 而两条旧守卫跟着动

| 守卫 | 旧断言 | 新断言 |
|---|---|---|
| `VendorsWithoutASolveStayWithoutOne` | `state == NotAChallenge` | **`state == DetectedOnly`**（`HasSolveFor("queue-it")` 仍 `false`） |
| `TheGapsAreClassified` | 同上 | 同上 |

**→ 而 `HasSolveFor("queue-it") == false` **不变** —— 复刻件确实没有 queue-it solver。
→ 变的只是**为什么**没有：不是「它不是墙」，而是「我们还没写」。**

### ⑥ 数字

| 度量 | R1024 | **R1025** |
|---|---|---|
| 套件 | 2233 / 0 | **2237 / 0 / 0（+4）** |
| 产物陈旧度 | 4 / 3,816 | **4 / 3,835** |
| 函数数 | 174,336 | **174,336** |
| **queue-it 的 State** | `NotAChallenge`（错） | **`DetectedOnly`** |
| **`NotAChallenge` 使用者** | 1 | **0（有墓碑守卫）** |
| **镜像给 queue-it 的挑战面证据** | 1 条（`Error Solving`） | **8 条** |

### 教训

> **三次，同一个形状：从「我看到的那个表面」推出「只有这个表面」。**
> **→ 而每次的反证据都在**同一个查询的输出里**（`DdInterstitialClient` · `Solving PerimeterX` ·
> `Fetching Queue-it challenge`）—— 我只读了它在回答的那个问题。**
> **→ 所以真正的纪律不是「别下结论」，是：**读一段输出时，把不回答我问题的那些行也读一遍**。**
"""

if "queue-it **不只是队列**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1025 轮：queue-it 不只是队列；而 `NotAChallenge` 失去唯一使用者

### ① 八条证据说 queue-it 有挑战面

```
Fetching Queue-it challenge                 它 serve 挑战
Error Solving Queue-it (Softblock)           原版尝试解
Error Initiliazing Queue-it (Softblock)      且会初始化失败
Queue-IT banned, rotating proxy              也会换代理
Unsupported Queue-it BotDeflector page       BotDeflector 是它的反机器人产品
Redirected into a Queue-it waiting room      等待室是真的
/softblock · /challengeapi/queueitcaptcha/challenge/    端点 + CAPTCHA
X-queueit-challange-{reason,customerid,eventid,hash,ruleid,rulename} + X-queueit-redirect
QueueITAccepted · QueueitEnqueueToken · queueittoken
```

**→ 「队列不是墙，正确处置是等待」一半对：等待**是**处置的一部分。
→ 「等待是**全部**处置」**错了**。**

### ② 而这是第三次同一个形状

| 轮 | 从 | 推出 | 实际 |
|---|---|---|---|
| R1018 | 「`captcha-delivery` 是挑战域」 | 「属 perimeterx」 | 属 datadome |
| R1023 | 「只有换代理文案」 | 「原版不解 perimeterx」 | 有 `Solving PerimeterX` |
| **R1025** | 「我们看到的是等待室」 | **「它只是队列」** | **还有挑战面** |

**→ 三次都是**从「我看到的」推出「只有这些」** —— 抽样不等于全量的**行为版**。**

### ③ 改了什么

**`queue-it`：`State.NotAChallenge` → `DetectedOnly`，Note 列八条证据并写明
「waiting is part of the handling rather than all of it」。**

**→ 与 akamai 同一个 State 而理由不同：akamai 是「镜像解它，我们没写」；
queue-it 是「镜像解 softblock，我们只等待」。两者都是「镜像有而我们没有」。**

### ④ 而 `NotAChallenge` 现在没有使用者

**保留枚举值（删掉会让分类法静默收缩），加 4 条守卫，其中一条专门钉「无使用者」——
那是那个值的**墓碑**。**

### ⑤ 而两条旧守卫跟着动

`VendorsWithoutASolveStayWithoutOne` 与 `TheGapsAreClassified` 的 `state == NotAChallenge` → `DetectedOnly`。
**→ `HasSolveFor("queue-it") == false` **不变** —— 变的只是**为什么**：
不是「它不是墙」，而是「我们还没写」。**

### ⑥ 数字

| 度量 | R1024 | **R1025** |
|---|---|---|
| 套件 | 2233 / 0 | **2237 / 0 / 0（+4）** |
| 产物陈旧度 | 4 / 3,816 | **4 / 3,835** |
| 函数数 | 174,336 | **174,336** |
| **queue-it State** | `NotAChallenge`（错） | **`DetectedOnly`** |
| **`NotAChallenge` 使用者** | 1 | **0** |
| **queue-it 挑战面证据** | 1 | **8** |

### 教训

> **三次，同一个形状：从「我看到的那个表面」推出「只有这个表面」。
> → 而每次的反证据都在**同一个查询的输出里**（`DdInterstitialClient` · `Solving PerimeterX` ·
> `Fetching Queue-it challenge`）—— 我只读了它在回答的那个问题。**
> **→ 所以真正的纪律不是「别下结论」，是：**读一段输出时，把不回答我问题的那些行也读一遍**。**
"""

BACKLOG_ADD = """

## 优先级 ② — **queue-it 不只是队列：`NotAChallenge` → `DetectedOnly`，八条证据**（R1025）

### 证据（八条，同一个查询里）

```
Fetching Queue-it challenge · Error Solving Queue-it (Softblock) ·
Error Initiliazing Queue-it (Softblock) · Queue-IT banned, rotating proxy ·
Unsupported Queue-it BotDeflector page · /softblock ·
/challengeapi/queueitcaptcha/challenge/ · X-queueit-challange-* ×7
```

**→ 「队列不是墙、处置是等待」一半对 —— 等待**是**一部分，「只是等待」错了。**

### 第三次同一个形状

| 轮 | 从 | 推出 | 实际 |
|---|---|---|---|
| R1018 | captcha-delivery 是挑战域 | 属 perimeterx | 属 datadome |
| R1023 | 只有换代理文案 | 原版不解 perimeterx | 有 `Solving PerimeterX` |
| R1025 | 我们看到等待室 | 它只是队列 | 还有挑战面 |

### 改了什么

**`State.NotAChallenge` → `DetectedOnly`；Note 列八条证据。4 条守卫，其中
`NoRowUsesNotAChallengeAnyMore` 是那个枚举值的**墓碑**。**

**两条旧守卫同步：`VendorsWithoutASolveStayWithoutOne` · `TheGapsAreClassified`。
`HasSolveFor("queue-it") == false` 不变 —— 变的是**为什么**。**

### 数字

**套件 2237（+4）· 陈旧度 4 / 3,835 · 函数数 174,336 · NotAChallenge 使用者 1 → 0 · 证据 1 → 8**

| 仍 Unknown | |
|---|---|
| queue-it softblock 求解协议 | 未取证 |
| `BotDeflector` 页是否另一套流程 | 未取证 |

**纪律**：读一段输出时，把不回答我问题的那些行也读一遍。
"""

BLOCKER = """

---

## 449. **queue-it 不只是队列；`NotAChallenge` 失去唯一使用者**

> R1025。**改 1 个源文件 + 1 个新测试 + 2 个旧测试。** 套件 **2237 通过 / 0 失败 / 0 跳过**。

### 一、八条证据说 queue-it 有挑战面

```
Fetching Queue-it challenge                0x146d8ea24   ← 它 serve 挑战
Error Solving Queue-it (Softblock)          0x146d0d1b4   ← 原版**尝试解**
Error Initiliazing Queue-it (Softblock)     0x146d0d14c   ← 且会初始化失败
Queue-IT banned, rotating proxy             0x146e57fb4   ← 也会换代理
Unsupported Queue-it BotDeflector page      0x146f1471c   ← BotDeflector 是它的反机器人产品
Redirected into a Queue-it waiting room     0x146e63a6c   ← 等待室是真的
/softblock                                  0x146ab8f6c
/challengeapi/queueitcaptcha/challenge/     0x146ab2cb4   ← **CAPTCHA 端点**
X-queueit-challange-{reason,customerid,eventid,hash,ruleid,rulename} + X-queueit-redirect
QueueITAccepted · QueueITAccepted-SDFrts345E-V3_ · QueueitEnqueueToken · queueittoken
```

**→ 所以「队列不是墙，正确处置是等待」这句话**一半对**：等待**是**处置的一部分。
→ 而「等待是**全部**处置」**错了** —— 它还有 challenge · solver · BotDeflector · captcha。**

### 二、而这是一个**熟悉的形状**（第三次）

| 轮 | 从 | 推出 | 实际 |
|---|---|---|---|
| R1018 | 「`captcha-delivery` 是挑战域」 | 「它属 perimeterx」 | 属 datadome |
| R1023 | 「只有换代理文案」 | 「原版不解 perimeterx」 | 有 `Solving PerimeterX` |
| **R1025** | 「我们看到的是等待室」 | **「它只是队列」** | **还有挑战面** |

**→ 三次都是**从「我看到的」推出「只有这些」**。
→ 而那正是 AGENTS §2.7b「抽样不等于全量」的**行为版**：一个表面不等于全部表面。**

### 三、改了什么

**`queue-it` 行：`State.NotAChallenge` → `DetectedOnly`，Note 列出八条证据并写明
  「waiting is part of the handling rather than all of it」。**

**→ 而 `DetectedOnly` 与 R1024 给 akamai 的那个值是同一个 —— 而两行的理由不同：
  akamai 是「镜像解它，我们没写」；queue-it 是「镜像解 softblock，我们只等待」。
→ 两者都是「镜像有而我们没有」，所以同一个 State 是对的。**

### 四、而 `NotAChallenge` 现在**没有使用者**

**→ 保留枚举值（删掉会让分类法静默收缩），并加 4 条守卫其中之一专门钉「无使用者」。**

| 守卫 | 断言 |
|---|---|
| `TheRowIsNoLongerNotAChallenge` | `State == DetectedOnly` |
| `TheMarkerAndGapAreUnchanged` | marker/cookie/Gap 未被这次更正碰到 |
| `TheNoteNamesTheChallengeSurface` | Note 里点名五条证据（可查） |
| **`NoRowUsesNotAChallengeAnyMore`** | **无行使用该值** |

**→ 第 4 条是那个枚举值的**墓碑**：它记录「这个分类曾有一个用例，而现在没有」，而不是悄悄消失。**

### 五、而两条旧守卫跟着动

| 守卫 | 旧断言 | 新断言 |
|---|---|---|
| `VendorsWithoutASolveStayWithoutOne` | `state == NotAChallenge` | **`state == DetectedOnly`** |
| `TheGapsAreClassified` | 同上 | 同上 |

**→ 而 `HasSolveFor("queue-it") == false` **不变** —— 复刻件确实没有 queue-it solver。
→ 变的只是**为什么**没有：不是「它不是墙」，而是「我们还没写」。**

### 六、数字

| 度量 | R1024 | R1025 |
|---|---|---|
| 套件 | 2233 / 0 | **2237 / 0 / 0（+4）** |
| 产物陈旧度 | 4 / 3,816 | **4 / 3,835** |
| 函数数 | 174,336 | **174,336** |
| **queue-it 的 State** | `NotAChallenge`（错） | **`DetectedOnly`** |
| **`NotAChallenge` 使用者** | 1 | **0（有墓碑守卫）** |
| **镜像给 queue-it 的挑战面证据** | 1 条 | **8 条** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "Softblock"            -> {"n":3}（/softblock · Initiliazing · Solving）
python analysis/ida.py str "Queue-it"             -> {"n":13}
python analysis/ida.py str "QueueIt"              -> {"n":24}
python analysis/ida.py str "queue-it-set-cookie"  -> {"n":1}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~QueueIt|~Vendor|~Wall" -m:1 -> 90 通过
python tools/metrics_report.py -> 完整套件 exit 0  2237 / 0 / 0
```

### 八、仍然 Unknown

- **queue-it softblock 的求解协议**：**未取证**。
- **`BotDeflector` 页是否另一套流程**：**未取证**。

### 九、教训

**三次，同一个形状：从「我看到的那个表面」推出「只有这个表面」。**

**→ 而每次的反证据都在**同一个查询的输出里**（`DdInterstitialClient` · `Solving PerimeterX` ·
  `Fetching Queue-it challenge`）—— 我只读了它在回答的那个问题。**

**→ 所以真正的纪律不是「别下结论」，是：**读一段输出时，把不回答我问题的那些行也读一遍**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1025", BLOCKER)
    ensure(RSTATUS, "R1025", BLOCKER)
    ensure(RVERDICT, "第 1025 轮", VERDICT)
    ensure(BACKLOG, "R1025", BACKLOG_ADD)

    note = (
        "\n## R1025 补充 — **queue-it 不只是队列：`NotAChallenge` → `DetectedOnly`，八条证据**（套件 2237）\n\n"
        "**八条证据（同一个查询里）**：`Fetching Queue-it challenge` · `Error Solving Queue-it (Softblock)` ·\n"
        "`Error Initiliazing Queue-it (Softblock)` · `Queue-IT banned, rotating proxy` ·\n"
        "`Unsupported Queue-it BotDeflector page` · `/softblock` · `/challengeapi/queueitcaptcha/challenge/` ·\n"
        "`X-queueit-challange-*` ×7。\n"
        "→ 「队列不是墙、处置是等待」**一半对** —— 等待**是**一部分，「只是等待」错了。\n\n"
        "**第三次同一个形状**：\n"
        "| 轮 | 从 | 推出 | 实际 |\n|---|---|---|---|\n"
        "| R1018 | captcha-delivery 是挑战域 | 属 perimeterx | 属 datadome |\n"
        "| R1023 | 只有换代理文案 | 原版不解 perimeterx | 有 `Solving PerimeterX` |\n"
        "| **R1025** | 我们看到等待室 | **它只是队列** | **还有挑战面** |\n"
        "→ 三次都是**从「我看到的」推出「只有这些」**。\n\n"
        "**改**：`State.NotAChallenge` → `DetectedOnly`（与 akamai 同值而理由不同：都是「镜像有而我们没有」）。\n"
        "**4 条守卫**，其中 `NoRowUsesNotAChallengeAnyMore` 是那个枚举值的**墓碑**。\n"
        "**两条旧守卫同步**；`HasSolveFor(\"queue-it\") == false` **不变** —— 变的是**为什么**。\n\n"
        "数字：套件 2237（+4）· 陈旧度 4 / 3,835 · 函数数 174,336 · NotAChallenge 使用者 1 → **0** · 证据 1 → **8**。\n\n"
        "纪律：**读一段输出时，把不回答我问题的那些行也读一遍。**\n\n"
        "下一轮：`BotDeflector` 页是否另一套流程；或 queue-it softblock 的求解协议。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1025" not in h:
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
             for p, k in ((RBLOCK, "R1025"), (RSTATUS, "R1025"), (RVERDICT, "第 1025 轮"), (BACKLOG, "R1025")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1025: queue-it is not only a queue, and NotAChallenge loses its last user\n\n"
         "R1024 closed on the contradiction between Error Solving Queue-it (Softblock) and a row that said a queue is\n"
         " not a challenge. The contradiction was the tip of it.\n\n"
         "Eight literals from one query describe a challenge surface: fetching the vendor's challenge, solving and\n"
         " initialising failures on its softblock, a BotDeflector page the original calls unsupported, a proxy rotation\n"
         " path, the /softblock endpoint, a queueitcaptcha challenge endpoint, and seven X-queueit-challange-* headers\n"
         " down to ruleid and rulename. The waiting room is real and is in that list too.\n\n"
         "So the old note was half right and wrong in its conclusion. Waiting is part of the handling; waiting being all\n"
         " of it does not follow, and the row said so as a state.\n\n"
         "This is the third round with the same shape. R1018 read a challenge host as PerimeterX's when it was\n"
         " DataDome's. R1023 read a proxy-rotation line as the whole of a response when a solving line sat beside it.\n"
         " And here the waiting room was read as the whole vendor. Each time the counter-evidence was in the output I\n"
         " was already reading; I only read the lines that answered my question.\n\n"
         "The state becomes DetectedOnly, which is the same value Akamai gets for a different reason -- the image solves\n"
         " both, and this workspace does neither. NotAChallenge keeps its declaration and loses its user, and a guard\n"
         " records that it is unused, which is the closest thing an enum value can have to a headstone.\n\n"
         "Two older guards moved with it. What has not changed is HasSolveFor(\"queue-it\") returning false: this\n"
         " workspace still has no queue-it solver. What changed is why -- not because the vendor poses no challenge, but\n"
         " because the work is not done.\n\n"
         "Figures: suite 2233 to 2237, freshness four files and 3,835 lines, count 174,336, queue-it's evidence up from\n"
         " one literal to eight, and NotAChallenge going from one user to none.\n\n"
         "Unknown: how a softblock is actually solved, and whether BotDeflector is a second flow.\n\n"
         "The lesson is that reading only the lines that answer your question is how a surface becomes the whole thing,\n"
         " and that the correction was sitting in the same output every time.\n\n"
         "One source file and three test files changed; suite green at 2237."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()