"""Record R1064: the 62.89% is a reliable count of the wrong thing."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### `62.89%` 是一个**可靠的、但测错了对象**的计数（R1064）

**上一轮把 (a)–(f) 逐条复核完，六条都达成。而目标本身不是那六条，是「函数数量对等」。
而 174,293 / 277,120 = 62.89% —— 那不叫对等，所以这一轮去查那 37% 是什么。**

### ① 第一个事实：两个产物的框架版本不同，而那是已知的

```
net10.0                                          n=1
IsAotCompatible  10.0.12+95017c711e6afc1085133d440e42b4bd78155701    ← **.NET 10.0.12**
System.Private.CoreLib                           n=5（含 "Large parts of the BCL won't work!"）
control kpsdk                                    17（对照成立）
```

**→ 原版是 **.NET 10.0.12** NativeAOT，复刻件是 **.NET 8** NativeAOT。
→ 而 AGENTS §0 明写「复刻件本身用 .NET 8 + Avalonia，**目标框架不必跟随原版**」。
→ **所以两个产物的 BCL（框架自带的那部分）本来就不同，而各自把它内联进 exe。****

### ② 而段结构给出两件事：函数数可靠，`.text` 大小不可比

| 段 | 原版 | 复刻件 | 比 |
|---|---|---|---|
| `.text` | **51,694,952** | **1,035,448** | **50×** |
| `.rdata` | 59,738,238 | 24,601,814 | 2.4× |
| `.data` | 11,517,352 | 1,010,200 | 11× |
| `.pdata` | **3,325,128** | **2,091,096** | 1.6× |

**→ `.pdata` 每条 12 字节：3,325,128 / 12 = **277,094** ≈ 277,120；2,091,096 / 12 = **174,258** ≈ 174,293。
→ 两个函数数**各自**与自己的 `.pdata` 对上 ⇒ **函数数这个量是可靠的。****

**→ 而 `.text` 差 50 倍是**不能读成「代码少 50 倍」**的：
→ 51,694,952 / 277,120 ≈ **每函数 186 字节**；1,035,448 / 174,293 ≈ **每函数 6 字节**。
→ **6 字节装不下一个函数** ⇒ 复刻件的大量代码**不在 `.text` 里**（它的 `.rdata` 24.6 MB、entropy 6.64）。
→ **两个 SDK 的段布局不同 ⇒ `.text` 大小不可比。****

### ③ 所以结论是：`62.89%` 可靠，而它测的不是「复刻完成度」

| 它能说的 | 它不能说的 |
|---|---|
| 两个产物各有多少个函数，且都可复算 | **差额里有多少是 BCL、多少是业务** |
| 复刻件函数**少于**原版 | **复刻件缺功能**（BCL 版本差就能造出这个差额） |

**→ 而「差额里有多少是 BCL」这个问题**不可解**，因为产物无符号：**
→ 96.87% 的函数是 `sub_*`，**没有名字能说「这个是 `System.Text.StringBuilder.Append`」**。
→ 所以「把 BCL 与业务分开」需要**另一个手段**，而本表没有它。**

### ④ 那缺什么是明确的

| 缺什么 | 为什么需要 | 缺了会怎样 |
|---|---|---|
| **把 BCL 函数与业务函数分开的手段** | 「函数数量对等」只应对业务函数 | 62.89% 会被读成「完成度 62.89%」，而那是**错读** |
| 可能的路径 | ① 用**同样的 .NET 8** 重编原版（无源码，不可行）② 比对两个 SDK 自带的 BCL 函数数基线 ③ 按**调用图可达性**分（业务函数被业务入口调用） | — |

**→ 而 ② 是**可算的**：编一个空的 .NET 8 NativeAOT，数它的函数数，那是一个 BCL 基线。
→ **→ 而那也是下一轮的第一步。****

### ⑤ 数字

| 度量 | R1063 | **R1064** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 / 277,120 | **同** |
| 比例 | 62.89% | **62.89%（可靠，但测的不是完成度）** |
| 原版框架 | 已知 .NET 10 | **.NET 10.0.12（带构建哈希）** |
| `.pdata` / 12 | 未验 | **277,094 / 174,258 —— 与函数数各自对上** |
| `.text` 每函数字节 | 未测 | **186 vs 6 ⇒ 不可比** |
| **「差额里多少是 BCL」** | 未问 | **不可解（无符号）—— 缺一个分离手段** |

### 教训

> **一个数字可以既可靠又答错问题。`62.89%` 是可靠的（两边的 `.pdata` 都对得上），
> 而它答的是「两个不同框架版本的 NativeAOT 函数总数比」，不是「复刻完成度」。**
> **→ 而这一轮真正的产出是**否定一个读法**，不是得到一个数字 ——
> 那与前几轮的「假零」「假缺口」不同：这次数字没错，错的是**它的解释**。**
> **→ 而 `.text` 那 50 倍差点让我写成「代码量少 50 倍」—— 是「每函数 6 字节」这个荒谬值拦住了我。
> → 荒谬的中间量是好东西：它比任何纪律都早地指出假设错了。**
"""

if "是一个**可靠的、但测错了对象**的计数" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1064 —— **`62.89%` 可靠，但测的不是完成度**

### 框架版本

```
IsAotCompatible  10.0.12+95017c711e6afc1085133d440e42b4bd78155701   ← 原版 .NET **10.0.12**
System.Private.CoreLib n=5 · control kpsdk 17
```

**原版 .NET 10.0.12 / 复刻件 .NET 8，而 AGENTS §0 明写「目标框架不必跟随原版」⇒ 两边 BCL 本来就不同。**

### 段结构：函数数可靠，`.text` 不可比

| 段 | 原版 | 复刻件 | 比 |
|---|---|---|---|
| `.text` | **51,694,952** | **1,035,448** | **50×** |
| `.rdata` | 59,738,238 | 24,601,814 | 2.4× |
| `.pdata` | **3,325,128** | **2,091,096** | 1.6× |

**`.pdata`/12 = 277,094 / 174,258 ⇒ 与两个函数数各自对上 ⇒ 函数数可靠。**
**而 `.text`/函数 = **186 vs 6 字节** —— 6 字节装不下函数 ⇒ 复刻件代码大量在 `.rdata` ⇒ **不可比**。**

### 结论：可靠但答错问题

| 能说 | 不能说 |
|---|---|
| 两产物各有多少函数，可复算 | 差额里多少是 BCL、多少是业务 |
| 复刻件函数**少于**原版 | **复刻件缺功能**（BCL 版本差就能造出差额） |

**⇒ 「差额多少是 BCL」不可解：96.87% 是 `sub_*`，没有名字能认出 `StringBuilder.Append`。**

### 而缺什么是明确的

**缺「把 BCL 与业务分开」的手段。** 可能路径：① 用 .NET 8 重编原版（无源码，不可行）
② **编一个空的 .NET 8 NativeAOT 数其函数数，得 BCL 基线（可算 —— 下一轮第一步）** ③ 按调用图可达性分。

### 数字

| 度量 | R1063 | **R1064** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 / 277,120 | **同** |
| 比例 | 62.89% | **62.89%（测的不是完成度）** |
| `.pdata`/12 | 未验 | **277,094 / 174,258** |
| `.text`/函数 | 未测 | **186 vs 6 ⇒ 不可比** |

**纪律**：荒谬的中间量是好东西 —— 「每函数 6 字节」比任何纪律都早地指出假设错了。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1064", NOTE)
append(RBLOCK, "R1064", "\n---\n\n## 488. **`62.89%` 可靠但测的不是完成度**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1064: the ratio is reliable and measures the wrong thing\n\n"
     "Six criteria were checked last round and all six hold. The objective is not those six, it is equal function\n"
     " counts, and 174,293 against 277,120 is 62.89 per cent -- not equal. So this round asked what the missing 37 per\n"
     " cent is.\n\n"
     "The first fact is that the two artifacts come from different frameworks. The original carries .NET 10.0.12 with\n"
     " its build hash in an IsAotCompatible string, and the replica is .NET 8 because AGENTS section zero says the\n"
     " target framework need not follow. Each SDK inlines its own class library, so part of the difference is two\n"
     " different BCLs rendered to native code, not two different amounts of Cybersole.\n\n"
     "The section table shows the count is trustworthy and one obvious comparison is not. .pdata divided by twelve\n"
     " gives 277,094 and 174,258, matching both function counts, so that quantity is solid. But .text differs by fifty\n"
     " times, and dividing it by the function count gives 186 bytes per function on the original against six on the\n"
     " replica. Six bytes cannot hold a function, so the replica's code is largely elsewhere -- its .rdata is 24\n"
     " megabytes at high entropy. Two SDKs lay out sections differently and .text sizes are not comparable. That absurd\n"
     " per-function figure is what stopped me writing that the replica has fifty times less code.\n\n"
     "So the ratio is reliable and answers the wrong question. It can say how many functions each artifact has and that\n"
     " the replica has fewer. It cannot say how much of the difference is BCL, and therefore cannot say the replica is\n"
     " missing behaviour. Splitting BCL from business code is not possible here: 96.87 per cent of functions are sub_, and\n"
     " no name identifies StringBuilder.Append.\n\n"
     "What is missing is therefore stated: a way to separate the two. Building the original against .NET 8 is not\n"
     " possible without sources. Compiling an empty .NET 8 NativeAOT application and counting its functions gives a BCL\n"
     " baseline in about a minute, and that is the next step. Reachability from business entry points is the other.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, .pdata divided by twelve\n"
     " matching both counts, and 186 against 6 bytes per function marking the comparison invalid.\n\n"
     "Unknown: how much of the 102,827 function difference is framework. A baseline build answers it for the framework\n"
     " side, not for what Cybersole itself does.\n\n"
     "The lesson is that a number can be reliable and still answer the wrong question -- and that an absurd intermediate\n"
     " value catches a wrong assumption sooner than any rule does."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
