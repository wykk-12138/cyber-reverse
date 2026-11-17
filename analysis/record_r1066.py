"""Record R1066: one direct measurement settles two rounds of hypothesis, against the hypothesis."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 一次直接测量，定了两轮假设 —— 而方向是**反的**（R1066）

**R1064 说 62.89% 不能读成完成度，因为两边 inline 了不同的 BCL。R1065 编了最小 .NET 8 基线得 7,930，说框架解释不了 102,827。
而两轮都停在「框架贡献未测定」上。这一轮**直接测**它。**

### ① 实验：同一份源码，两个目标框架

**`baseline-aot10/Baseline10.csproj` 用 `<Compile Include="..\\baseline-aot\\Program.cs" Link="Program.cs" />`
—— **按路径链接**而不是复制，所以两份构建**不可能漂移**：一个源文件，两个框架。
→ 而先侧装了 .NET 10 SDK（`D:\\tools\\dotnet10`，10.0.404，不覆盖系统运行时 —— AGENTS §1.4）。**

### ② 而结果

```
baseline net8.0    .pdata=95,160    functions=7,930    file=2.2 MB
baseline net10.0   .pdata=87,708    functions=7,309    file=2.3 MB
delta              **-621**  (-7.8%)
```

**→ .NET 10 的基线函数**比 .NET 8 **少** 621 个。**

**→ 所以「框架版本差异」不但解释不了缺口，**方向是反的**：
→ 若复刻件用 .NET 10，它会更**小**，缺口会更**大**。**

### ③ 而扣掉之后

```
replica-vs-original gap        102,836
框架版本贡献                    -621
扣掉后余下的缺口               103,457      ← **更大**
```

**→ 所以那 102,836 的差是**实质的**：应用代码量的差，不是框架幻觉。**

### ④ 而那把 62.89% 摆正了

| 量 | 值 |
|---|---|
| 复刻件函数 | 174,258 |
| 原版函数 | 277,094 |
| 比 | **62.9%** |
| 框架部分（两边，最小基线） | ~7,300–7,900，**几乎相等** |
| **⇒ 差几乎全部是应用侧** | **~103,000 个函数** |

**→ 所以「函数数量对等」还差 **约 10 万个函数**，而那是一个**真实的缺口**，
→ 不是框架版本、不是测量口径、不是命名差异。**

### ⑤ 而这一轮也说明了前两轮的形状

| 轮 | 做了什么 | 结论 |
|---|---|---|
| R1064 | 段结构 → 「62.89% 可靠但答错问题」 | 对，但停在「框架贡献未测定」 |
| R1065 | 最小 .NET 8 基线 7,930 → 「框架解释不了」 | 对，但仍是**推断** |
| **R1066** | **同源双框架，直接测差** | **−621 ⇒ 框架不是因素，方向相反** |

**→ 两轮推断，一次测量就替掉了。而测量的成本是：侧装一个 SDK + 编两个 2 MB 的程序。**

**→ 那与 R1044 那条「一个零需要对照」同族，但更高一层：
→ 这次需要的不是对照，是**一个能直接测出差值的实验设计** —— 而它的关键是**同源**（链接而非复制）。**

### ⑥ 数字

| 度量 | R1065 | **R1066** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 / 277,120 | **174,258 / 277,094（`.pdata`÷12）** |
| 比例 | 62.89% | **62.9%** |
| **.NET 8 基线** | 7,930 | **7,930** |
| **.NET 10 基线** | 未测 | **7,309** |
| **框架版本贡献** | 「未测定」 | **−621（方向相反）** |
| **扣框架后的缺口** | 「不可算」 | **103,457** |
| **框架是缺口的成因吗** | 未排除 | **排除，且方向相反** |
| **.NET 10 SDK** | 无 | **侧装 `D:\\tools\\dotnet10`（10.0.404）** |

### 教训

> **两轮推断（R1064、R1065）都被一次测量替掉了，而测量只花了「装一个 SDK + 编两个 2 MB 程序」。**
> **→ 而我上一轮已经在往「调用图可达性」的方向走了 —— 那是一条更贵、更绕的路，
> 而更便宜的那条（同源双框架）就在旁边。**
> **→ 所以「下一步做什么」本身也需要一次检查：**有没有一个直接测量能替掉我在推的东西？****
> **→ 而这次的关键设计只有一点：**链接源码而不是复制**。复制会漂移，链接不会 —— 而漂移会让 delta 失去意义。**
"""

if "一次直接测量，定了两轮假设" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1066 —— **一次直接测量定了两轮假设，方向是反的（−621）**

### 实验设计

`baseline-aot10/Baseline10.csproj` 用 `<Compile Include="..\\baseline-aot\\Program.cs" Link="Program.cs" />`
—— **按路径链接**而非复制 ⇒ 两份构建**不可能漂移**：一个源文件，两个框架。
先侧装 .NET 10 SDK（`D:\\tools\\dotnet10`，**10.0.404**，不覆盖系统 —— AGENTS §1.4）。

### 结果

```
baseline net8.0    7,930
baseline net10.0   7,309
delta              **-621**  (-7.8%)
```

**⇒ .NET 10 比 .NET 8 **少** 621 个函数 ⇒ 框架版本不但解释不了缺口，**方向相反**
（复刻件若用 .NET 10 会更小，缺口更大）。**

### 扣掉之后

```
gap                 102,836
框架贡献            -621
扣掉后              103,457     ← **更大**
```

**⇒ 那 102,836 是**实质的**：应用代码量的差。**

### 那 62.89% 摆正了

| 量 | 值 |
|---|---|
| 复刻件 / 原版 | 174,258 / 277,094 = **62.9%** |
| 框架（最小基线，两边几乎相等） | ~7,300–7,900 |
| **差几乎全部是应用侧** | **~103,000** |

**⇒ 「函数数量对等」还差约 **10 万个函数**，那是**真实缺口** —— 不是框架、不是口径、不是命名。**

### 前两轮的形状

| 轮 | 结论 | 性质 |
|---|---|---|
| R1064 | 62.89% 可靠但答错问题 | 对，停在「框架贡献未测」 |
| R1065 | 框架解释不了（7,930） | 对，但是**推断** |
| **R1066** | **直接测差 = −621** | **测量替掉两轮推断** |

### 数字

| 度量 | R1065 | **R1066** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 / 277,120 | **174,258 / 277,094** |
| .NET 8 / 10 基线 | 7,930 / 未测 | **7,930 / 7,309** |
| 框架贡献 | 「未测定」 | **−621（方向相反）** |
| 扣框架后缺口 | 「不可算」 | **103,457** |
| .NET 10 SDK | 无 | **侧装 10.0.404** |

**纪律**：「下一步做什么」本身也需要检查 —— 有没有一个直接测量能替掉我在推的东西？
而测量设计的关键是**同源**（链接而非复制），因为漂移会让 delta 失去意义。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1066", NOTE)
append(RBLOCK, "R1066", "\n---\n\n## 490. **一次直接测量定了两轮假设，方向相反（−621）**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1066: one direct measurement settles two rounds of hypothesis, against the hypothesis\n\n"
     "R1064 said the ratio cannot be read as completeness because the artifacts inline different class libraries.\n"
     "R1065 built a minimal .NET 8 AOT application, got 7,930 functions, and concluded the framework was far too small\n"
     " to explain a gap of 102,827. Both stopped short of measuring the framework's share, and I was about to go after\n"
     " reachability -- a more expensive route than the one standing next to it.\n\n"
     "The cheaper one is the same source published twice. Side-installing the .NET 10 SDK to D tools dotnet10, without\n"
     " touching the system runtime, and linking the same Program.cs by path rather than copying it, so the two builds\n"
     " cannot drift: one source, two frameworks, and the difference between the two counts is the framework version's\n"
     " contribution measured rather than argued.\n\n"
     "It is minus 621. .NET 10 produces fewer functions than .NET 8 for identical source, so the framework version does\n"
     " not explain any of the gap and points the wrong way -- a replica on .NET 10 would be smaller and the gap wider.\n"
     "Subtracting it makes the gap 103,457 rather than smaller.\n\n"
     "So the difference is application code. The replica carries 174,258 functions against 277,094, and the framework\n"
     " portion at the minimal baseline is nearly the same on both sides, which puts the shortfall at roughly a hundred\n"
     " thousand functions of real code. That is not a framework artefact, not a unit difference, and not naming.\n\n"
     "Two rounds of inference were replaced by one measurement costing an SDK install and two two-megabyte builds. The\n"
     " design detail that makes it valid is linking rather than copying: a copy would drift and the delta would stop\n"
     " meaning anything.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, 7,930 against 7,309 for identical source, a\n"
     " delta of minus 621, a gap of 102,836 that becomes 103,457, and a ratio unchanged at 62.9 per cent.\n\n"
     "Unknown: which functions those hundred thousand are, since the artifact has no symbols -- but their existence is\n"
     " now measured rather than suspected.\n\n"
     "The lesson is that choosing the next step deserves the same suspicion as a claim: there was a direct measurement\n"
     " available and I had started down a costlier path."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
