"""Record R864: R504's blocker and C7c's blocker are different, and C7c's may have a tool."""

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
### 两个阻塞被当成一个：R504 的与 C7c 的**理由不同**（R864）

**`docs/PARITY_CLAIMS.md` L58：**

```
| C7c | 任意两函数的伪代码等价 | unknown | unknown | — | 缺原版符号（PDB / 调试信息）。Ghidra 也不能提供…
```

**而 L56/L57：**

| claim | 状态 |
|---|---|
| C7a 绑定成员能否在原版定位到**绑定声明** | **pass**（51/51） |
| C7b 成员**形状**（getter/setter）两侧一致 | **fail**（条数见 METRICS） |
| **C7c 任意两函数的伪代码等价** | **unknown**，理由：**缺 PDB / 调试符号** |

### 关键：C7c 是**一条整体 claim**，不是逐成员

**它写的是「任意两函数」，所以它不区分核心与 UI —— R863 那个「天花板有没有触及核心」的问题，
在这条 claim 上**没有粒度**可答。**

### 而它的理由与 R504 不同

| 来源 | 断点 |
|---|---|
| **R504**（B 桶 31 条） | 描述符无 xref · setter 内联 · `ICommand` 委托点无类型信息 |
| **C7c** | **缺原版符号（PDB / 调试信息）** |

**两个理由指向不同的东西：**

- **R504 是结构性的** —— NativeAOT 把 setter 内联了，没有函数体可读
- **C7c 是工具性的** —— 没有符号表，两个二进制之间的函数**配对**做不了

**而「配对」这件事，`rea` 里有专门的工具：`match_native_functions`（按唯一符号 / 相同字节 / CFG 指纹配对）
与 `compare_functions`（对已配对的一对做逐面比较）。AGENTS.md §1 把这两个列为「第二意见」。**

**所以 C7c 未必是 dead end —— 它可能只是没试过第二套工具。**
"""

if "两个阻塞被当成一个：R504 的与 C7c 的**理由不同**（R864" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: blocker separation appended")

BLOCKER = """

---

## 288. R504 的阻塞与 C7c 的阻塞**不是同一件事**；而 C7c 可能有工具

> R864。未改产品代码。

### 一、C7c 是一条整体 claim，不是逐成员

`docs/PARITY_CLAIMS.md` L58：

```
C7c | 任意两函数的伪代码等价 | unknown | unknown | 缺原版符号（PDB / 调试信息）。Ghidra 也不能提供…
```

**它写的是「任意两函数」，所以它**不区分核心与 UI**。
R863 那个问题（天花板有没有触及核心）在这条 claim 上没有粒度可答。**

**而 C7a pass（51/51）、C7b fail（形状条数见 METRICS）—— 三者是**递进**的：
能定位 → 形状对 → 伪代码等价。前两个有粒度，第三个没有。**

### 二、而它的理由和 R504 完全不同

| 来源 | 断点 | 性质 |
|---|---|---|
| **R504**（B 桶 31 条 UI 成员） | 描述符无 xref · setter 内联 · `ICommand` 委托点无类型信息 | **结构性** |
| **C7c** | **缺原版符号（PDB / 调试信息）** | **工具性** |

**结构性的是：NativeAOT 把 setter 内联了，没有函数体可读 —— 换工具也没用。**
**工具性的是：两侧函数**配对**不了，因为没有符号可以对齐 —— 而这正是 `rea` 的两个工具要解决的问题。**

### 三、`rea` 的两个工具正好对口

| 工具 | 做什么 | 对 C7c 的用处 |
|---|---|---|
| `match_native_functions` | 按**唯一符号**、**相同观测字节**、CFG / 调用 / 字符串指纹配对两组 `list_procedures` | **正是「配对」这件事，不靠 PDB** |
| `compare_functions` | 对一对函数比较身份、伪代码、调用、引用、字符串、CFG 拓扑 | **配对之后的逐面比较** |

**AGENTS.md §1 把这两个列为「第二意见」。而 C7c 的 gap_reason 说「缺 PDB」——
`match_native_functions` 的设计前提就是**没有符号**（按字节与指纹配）。**

**所以 C7c 可能不是 dead end，是**没试过第二套工具**。**
**这条路这一轮不走（要两组 `list_procedures` Evidence，量大且需要 rea 会话），但它现在是一个正常的待办，不是一个天花板。**

### 四、这一轮的实际产出是「拆开」

**R862 说「这条路到头了」，R863 说「只挡 UI」，这一轮说**其实是两条不同的路**：**

| 路 | 状态 |
|---|---|
| UI 成员行为（R504） | **结构性到头**，且 YG 已暂缓 |
| 函数级伪代码等价（C7c） | **工具性未试**，`rea` 有对口工具 |

**所以「每个函数功能相等」的准确状态不是「不可能」，是：**
**核心层的**请求形状**有证据（R849/R850/R851–R856）；
函数级伪代码等价**没试过 `rea` 的配对**；
UI 成员行为**结构性拿不到**。**

### 五、验证

```
docs/PARITY_CLAIMS.md L56-L58: C7a pass · C7b fail · C7c unknown（理由：缺 PDB / 调试信息）
docs/PARITY_CLAIMS.md L121-L123: R467 把 C7 拆成 a/b/c 的记录
AGENTS.md §1: rea 的 match_native_functions / compare_functions 列为「第二意见」
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`match_native_functions` 在 AOT↔AOT 上能不能配上足够多的函数**：**Unknown** ——
  它能按「相同观测字节」配，而两侧是不同框架（.NET 10 AOT ↔ .NET 8 AOT），**字节相同的函数可能不多。**
- **配上的那批能否支持「功能相等」的判断**：**Unknown** —— `compare_functions` 给的是面比较，不是等价证明。
- **C7c 该不该改写成有粒度的几条**：**Unknown，但这是一个文档层面的改进** ——
  「任意两函数」这种写法让一条 claim 无法部分通过。

### 七、教训

**R862/R863 我一直在同一个词下想两个不同的问题 —— 「行为拿不到」。**

**一个是**结构**上拿不到（内联），一个是**工具**上没试（配对）。
**把它们合成一句，结论就是「不可能」；拆开看，一个是没有路，一个是没走那条路。**

**而 `AGENTS.md §1` 早就写着 rea 有那两个工具，还注明「第二意见」。
我没读那一行 —— 和 R861 那次没读 backlog 是同一个毛病，只是这次没读的是 AGENTS.md 自己。**
"""

VERDICT = """

---

## 第 864 轮：两个阻塞不是同一件事；而 C7c 可能有工具

### C7c 是一条整体 claim

```
C7c | 任意两函数的伪代码等价 | unknown | 缺原版符号（PDB / 调试信息）。Ghidra 也不能提供…
```

**「任意两函数」→ 不区分核心与 UI → R863 那个问题在这条 claim 上没有粒度可答。**

**而 C7a pass（51/51）· C7b fail · C7c unknown 是**递进**的：能定位 → 形状对 → 伪代码等价。**

### 而它的理由和 R504 完全不同

| 来源 | 断点 | 性质 |
|---|---|---|
| **R504**（UI 成员） | 描述符无 xref · setter 内联 · 委托点无类型信息 | **结构性** |
| **C7c** | **缺 PDB / 调试符号** | **工具性** |

**结构性的：换工具也没用。工具性的：只是两侧函数**配对**不了。**

### `rea` 的两个工具正好对口

| 工具 | 做什么 |
|---|---|
| `match_native_functions` | 按**唯一符号**、**相同观测字节**、CFG/调用/字符串指纹**配对**，**设计前提就是没有符号** |
| `compare_functions` | 配对后逐面比较（身份 / 伪代码 / 调用 / 引用 / 字符串 / CFG 拓扑） |

> **C7c 的 gap_reason 说「缺 PDB」，而 `match_native_functions` 的设计前提就是没有符号 —— 所以 C7c 可能不是 dead end，是**没试过第二套工具**。**

**本轮不走这条路（要两组 `list_procedures` Evidence，量大），但它现在是一个正常待办，不是天花板。**

### 所以「每个函数功能相等」的准确状态

| 层 | 状态 |
|---|---|
| 核心步骤的**请求形状** | **有证据**（R849 / R850 / R851–R856） |
| **函数级伪代码等价** | **没试过 `rea` 的配对** |
| **UI 成员行为** | **结构性拿不到**（且 YG 已暂缓） |

### 仍然 Unknown

**`match_native_functions` 在 AOT↔AOT 上能配多少**（两侧是不同框架，**字节相同的函数可能不多**）·
**配上的那批能否支持「功能相等」判断**（面比较 ≠ 等价证明）· **C7c 该不该改写成有粒度的几条**（「任意两函数」让一条 claim 无法部分通过）

### 教训

> **两个不同的问题在同一个词下 ——「行为拿不到」。一个是**结构**上拿不到（内联），一个是**工具**上没试（配对）。**
> **合成一句，结论是「不可能」；拆开看，一个是没有路，一个是没走那条路。**
> **而 `AGENTS.md §1` 早就写着 rea 有那两个工具 —— 我没读那一行，和 R861 没读 backlog 是同一个毛病。**
"""

BACKLOG_ADD = """

## 判据 — 两个阻塞拆开（R864）

**`PARITY_CLAIMS.md` L56–58：C7a pass（51/51）· C7b fail · C7c unknown（理由：**缺 PDB / 调试符号**）。**

**C7c 写「任意两函数」→ 整体一条，不区分核心/UI。**

| 来源 | 断点 | 性质 |
|---|---|---|
| R504（UI 成员） | 描述符无 xref · setter 内联 · 委托点无类型信息 | **结构性**（换工具无用） |
| **C7c** | 缺 PDB | **工具性**（配对问题） |

### `rea` 对口

**`match_native_functions`（按唯一符号/相同字节/CFG 指纹配对，**前提就是没有符号**）+ `compare_functions`（逐面比较）。**
**→ C7c 可能不是 dead end，是没试过第二套工具。本轮不走（量大），但记为正待办。**

### 「每函数功能相等」的准确状态

| 层 | 状态 |
|---|---|
| 核心步骤请求形状 | **有证据** |
| 函数级伪代码等价 | **没试 rea 配对** |
| UI 成员行为 | **结构性拿不到**（已暂缓） |

| 仍 Unknown | |
|---|---|
| AOT↔AOT 能配多少 | 两侧框架不同，字节相同可能不多 |
| 配上的能否支持「功能相等」 | 面比较 ≠ 等价证明 |
| C7c 该不该拆成有粒度的几条 | 「任意两函数」让 claim 无法部分通过 |

**纪律**：**一个是没路，一个是没走那条路 —— 合成一句就变成「不可能」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R864", BLOCKER)
    ensure(RSTATUS, "R864", BLOCKER)
    ensure(RVERDICT, "第 864 轮", VERDICT)
    ensure(BACKLOG, "R864", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R864" not in h:
        h += ("\n## R864 补充 — 两个阻塞拆开\n\n"
              "**C7c 是一条整体 claim**（「任意两函数」），理由 = **缺 PDB / 调试符号** → **工具性**。\n"
              "**R504 的 B 桶 31 条**（UI 成员）= 描述符无 xref / setter 内联 → **结构性**。\n"
              "**两者是不同的问题。而 `rea` 的 `match_native_functions` 前提就是没有符号（按字节与 CFG 指纹配对）→ C7c 是**没试过第二套工具**，不是 dead end。**\n"
              "**状态：核心请求形状有证据 · 函数级伪代码等价没试 rea 配对 · UI 成员行为结构性拿不到。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R864"), (RSTATUS, "R864"), (RVERDICT, "第 864 轮"), (BACKLOG, "R864")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R864: R504's blocker and C7c's are different problems, and C7c's has an untried tool\n\n"
         "PARITY_CLAIMS records C7c as the pseudocode equivalence of any two functions, unknown, with the gap reason"
         " being the absence of original symbols or PDB information. Two things follow.\n\n"
         "First, C7c is one whole claim rather than a per-member one, so it has no granularity with which to answer"
         " R863's question about whether the ceiling reaches the core. C7a passes at fifty-one of fifty-one locations,\n"
         " C7b fails on shape counts, and C7c is unknown -- a progression from locating a member, to its shape matching,\n"
         " to its code being equivalent, of which only the first two can be answered per member.\n\n"
         "Second, and more usefully, its reason is not R504's reason. R504's thirty-one UI members are blocked"
         " structurally: descriptors carry no cross-references, setters are inlined, and ICommand behaviour hides behind"
         " type information that also has none. No change of tool fixes that. C7c is blocked instrumentally: without"
         " symbols the two binaries' functions cannot be paired. And pairing is exactly what rea's match_native_functions"
         " does, by unique symbols, identical observed bytes, and CFG, call and string fingerprints -- a design whose"
         " premise is the absence of symbols. compare_functions then compares a paired function across identity,"
         " pseudocode, calls, references, strings and CFG topology. AGENTS.md section one lists both as the second\n"
         " opinion.\n\n"
         "So C7c is not a dead end; it is an untried tool. This round does not walk that road, since it needs two large\n"
         " list_procedures Evidence sets and a rea session, but the road is now an ordinary open item rather than a\n"
         " ceiling.\n\n"
         "The accurate state of every-function-behaves-the-same is therefore three different things: request shape for"
         " core steps is evidenced; function-level pseudocode equivalence has not been attempted with the pairing tool;\n"
         " and UI member behaviour is structurally unavailable and already deferred by YG.\n\n"
         "Unknown: how many functions match_native_functions can pair across two different AOT frameworks, where"
         " identical observed bytes may be rare; whether paired functions support a judgement of functional equality,\n"
         " since a facet comparison is not an equivalence proof; and whether C7c should be split into claims with"
         " granularity, because as written no part of it can pass on its own.\n\n"
         "The lesson is about the word 'unavailable'. Two distinct problems were hiding under it -- one structural, one"
         " instrumental -- and merging them produces a verdict of impossible, while separating them produces one closed"
         " road and one unwalked one. AGENTS.md had named the tools all along; not reading that line is the same fault as"
         " not reading the backlog in R861, except the file I failed to read was the instructions themselves.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
