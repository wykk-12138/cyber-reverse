"""Record R1065: my own baseline refutes the comfortable explanation."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 我自己编的基线**否掉了我的安慰性解释**（R1065）

**R1064 说 `62.89%` 不能读成完成度，因为两个产物inline 了两份不同的 BCL（原版 .NET 10.0.12、复刻件 .NET 8）。
那句话隐含一个安慰：**差的 37% 主要是框架**。
→ 这一轮编了个最小的 .NET 8 NativeAOT 去数它，而**结果否掉了那个安慰。****

### ① 基线：一个做真事但最小的 .NET 8 AOT 程序

```csharp
StringBuilder · LINQ · Dictionary · JsonSerializer · HttpClient · DateTimeOffset
```

**→ 刻意让它做点事而不是空 `Main`** —— 空的会被 trim 掉几乎全部框架，基线就**低估**了真应用的框架量。**

### ② 而结果：**7,930**

```
.pdata vsize = 95,160  →  ÷12 = **7,930** 个函数
baseline (.NET 8 最小 AOT)    7,930
replica                     174,293
original (.NET 10)          277,120
```

**→ 「最小 .NET 8 NativeAOT」只有 **7,930** 个函数。
→ 而两产物差 **102,827** —— **是基线的 13 倍。****

### ③ 所以那个安慰站不住了

| 上一轮隐含 | 而现在能说 |
|---|---|
| 「差 37% 主要是框架」 | **框架的固定成本只有 7,930 ⇒ 它解释不了 102,827** |
| — | **⇒ 那 102,827 主要是**应用侧 + 各自按需 trim 的 BCL**** |

**→ 而「各自按需 trim 了多少 BCL」仍然**不可算**（无符号），所以也不能反过来说「复刻件缺 102,827 个功能」。
→ 但**「差是框架造成的」这个读法被排除了** —— 而那是这一轮唯一能确定的事。**

### ④ 而那让 `62.89%` 的处境更难看，而不是更好

**→ 我原本希望基线给出一个「所以其实差不多」的答案。而它给出的是「7,930」。
→ 而 7,930 与 102,827 之比说明：**框架不是解释。****

**→ 那正是「用一个可算的量去检验一个想让它成立的解释」的结果 ——
→ 若我不编那个基线，我可以一直用「框架差异」把 62.89% 说得很体面。**

### ⑤ 缺什么，现在更清楚

| 缺什么 | 状态 |
|---|---|
| 复刻件的 174,293 里**多少是 BCL** | **不可算**（无符号 + trim 是编译期决定） |
| 原版的 277,120 里**多少是 BCL** | 同上 |
| **那 102,827 里多少是业务** | **不可算 —— 但已知**不是**框架的固定成本** |
| 可行的下一步 | 按**调用图可达性**分：从业务入口可达的 vs 只被库内部调用的 |

### ⑥ 数字

| 度量 | R1064 | **R1065** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 / 277,120 | **同** |
| 比例 | 62.89% | **62.89%** |
| **.NET 8 最小 AOT 基线** | 未测 | **7,930（`.pdata` 95,160 ÷ 12）** |
| **两产物差** | 102,827 | **102,827** |
| **差 / 基线** | 未算 | **13×** |
| **「差是框架造成的」** | 隐含成立 | **排除** |
| **基线程序位置** | — | **`analysis/baseline-aot/`（可重跑）** |

### 教训

> **我编这个基线，心里是想让它给出一个「所以其实差不多」的答案。而它给出 7,930。**
> **→ 而那正是「用一个可算的量去检验一个想让它成立的解释」的价值：
> 若不编它，我可以一直用「框架差异」把 62.89% 说得很体面。**
> **→ 与「荒谬的中间量拦住我」同族，方向相反：那次是一个怪数否掉假设，
> 这次是一个**正常但太小**的数否掉了一个想成立的说法。**
"""

if "我自己编的基线**否掉了我的安慰性解释**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1065 —— **我自己编的基线否掉了我的安慰性解释（7,930）**

### 编了什么

最小的 .NET 8 NativeAOT，**做一个真事**（`StringBuilder`·LINQ·`Dictionary`·`JsonSerializer`·`HttpClient`·`DateTimeOffset`）
而不是空 `Main`（空的会被 trim 光，基线会低估）。

### 结果

```
.pdata vsize = 95,160  ÷12 = **7,930**
baseline (.NET 8 最小)   7,930     replica 174,293     original 277,120     两产物差 **102,827**
```

### 所以安慰站不住了

| R1064 隐含 | 现在能说 |
|---|---|
| 「差 37% 主要是框架」 | **框架固定成本只有 7,930 ⇒ 解释不了 102,827（13 倍）** |
| — | **⇒ 那 102,827 主要是应用侧 + 各自按需 trim 的 BCL** |

**而「各自 trim 了多少 BCL」仍不可算（无符号）⇒ 也不能反过来说「复刻件缺 102,827 个功能」。
但**「差是框架造成的」被排除** —— 那是本轮唯一能确定的事。**

### 而它让 62.89% 更难堪，不是更好

**我原本希望基线给出「所以其实差不多」。它给出 7,930。
⇒ 若不编那个基线，我可以一直用「框架差异」把 62.89% 说得很体面。**

### 缺什么

| 缺什么 | 状态 |
|---|---|
| 复刻件 174,293 里多少是 BCL | **不可算**（无符号 + trim 是编译期决定） |
| 原版 277,120 里多少是 BCL | 同上 |
| 102,827 里多少是业务 | **不可算 —— 但已知**不是**框架固定成本** |
| 可行下一步 | 按**调用图可达性**：从业务入口可达的 vs 只被库内部调用的 |

### 数字

| 度量 | R1064 | **R1065** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 / 277,120 | **同** |
| **基线** | 未测 | **7,930** |
| 两产物差 | 102,827 | **102,827（13× 基线）** |
| 「差是框架」 | 隐含成立 | **排除** |

**纪律**：一个**正常但太小**的数，能否掉一个很想让它成立的说法。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1065", NOTE)
append(RBLOCK, "R1065", "\n---\n\n## 489. **自己编的基线否掉了安慰性解释（7,930 vs 102,827）**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1065: my own baseline refutes the comfortable explanation\n\n"
     "R1064 said the ratio cannot be read as completeness because the two artifacts inline two class libraries, the\n"
     " original built on .NET 10.0.12 and the replica on .NET 8. That carried a quiet comfort: most of the missing 37\n"
     " per cent is framework. This round built the smallest .NET 8 NativeAOT application that still does real work --\n"
     " StringBuilder, LINQ, a dictionary, JSON, an HttpClient, a timestamp -- and counted it.\n\n"
     "It is 7,930 functions. The gap between the two artifacts is 102,827, which is thirteen times the whole minimal\n"
     " framework. So the framework's fixed cost cannot account for the difference, and that explanation is gone.\n\n"
     "What remains is narrower and worse for the ratio. The 102,827 is mostly application code plus however much of the\n"
     " BCL each build trimmed in, and how much each trimmed is not computable here -- trimming is a compile-time\n"
     " decision and the artifact has no symbols. So this does not establish that 102,827 functions of behaviour are\n"
     " missing either. The one thing it does establish is that the difference is not the framework's fixed cost.\n\n"
     "I built the baseline hoping it would say the two are closer than they look. It said seven thousand nine hundred\n"
     " and thirty. Without it I could have kept describing 62.89 per cent as a framework artefact indefinitely, and the\n"
     " description would have been tidy and wrong.\n\n"
     "The next step is reachability: functions reachable from business entry points against functions only called from\n"
     " inside the library. That is the one split that does not need names.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, a baseline of 7,930 from a\n"
     " .pdata of 95,160 bytes, a gap of 102,827, and a ratio of thirteen to one that retires the framework explanation.\n\n"
     "Unknown: how much of either total is library rather than application, which both reachability and trimming\n"
     " decisions leave partly undetermined.\n\n"
     "The lesson is that a normal-looking number which happens to be small can refute a claim I wanted to be true, and\n"
     " that building the check before believing the comfort is the whole point of building it."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
