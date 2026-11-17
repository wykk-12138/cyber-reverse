"""Record R1072: the cheap bridge does not exist, and why that was predictable."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 「名字旁边有代码指针」这个便宜路径**不存在** —— 而那是第四次同一个错（R1072）

**R1071 说下一步是把函数地址映射到方法名，而 `ReflectionMethod` 记录带 native 指针。
→ 于是我去字符串旁边找指针，想用最便宜的方式把两边接起来。**
**→ 三个锚点，一个指针都没有。**

### ① 而结果

```
sections: .text, .rdata, .data, .pdata, .rsrc, .reloc

CaptchaProvider.Priority!Getter    va=0x1432158bc   .text **0**   .rdata **0**   其他非小值 27
CaptchaProvider.Type!Getter        va=0x1432159dc   .text **0**   .rdata **0**   其他非小值 27
CaptchaProvider.Priority!Property  va=0x14363e0a0   .text **0**   .rdata **0**   其他非小值 27
```

**→ 而那 27 个「其他非小值」也不在 `.text`/`.rdata` 里 —— 它们是别的东西（长度、对齐填充、或池内偏移）。**

### ② 而这次**可以预判**

**→ 那些元数据字符串是**连续的 UTF-8 文本**（R1039 那条「池按字母序排」正是因为它们是池）。
→ 一个**池**里不会有逐条的指针 —— 指针在**另一张表**里，用偏移指回来。
→ **所以「名字旁边有代码指针」这个假设从结构上就不该成立。**
→ 而我还是先去试了最便宜的那条 —— **试没错，错的是我没在试之前说出「池不带指针」这个理由。****

**→ 而那是同一个错的**第四次**（R764 · R1047 · R1054 · 现在）：**
**→ 先假设形状，再把「不符假设」读成「不存在」。而这次的不存在是**真的**，
→ 但真值来自结构推理，我却是从一次零得到的 —— **两条路的结论一样，而只有一条能提前预判。****

### ③ 所以正确路径的规模要写清

| 路径 | 规模 | 可行性 |
|---|---|---|
| 名字旁找指针 | 3 个锚点 × 一次读 | **已证伪** |
| 解析 `MethodTable` / `ReflectionMethod` 结构表 | 需要先定结构布局 | **一个工程**（R1045 说过） |
| 用 `TypeManager` 的 `MethodTable` 映射（`ReadyToRun` 元数据） | 同上，且要理解 NativeAOT 的 vtable 槽 | 同上 |
| **从数据流反推类型**（R1071 说的） | 每函数一次推理 | 不规模 |

**→ 而那张表的意义是：三条真路径都要**先定结构布局**，而那是同一件事的三种说法。**

### ④ 而本轮**不是白跑**

**→ 它关掉了一条看起来最省的路，而那条路的诱惑是真实的 ——
→ 而若不试，" 名字旁边有没有指针" 会一直是一个悬念，而悬念会让人反复回来试。
→ **记下来之后，下一轮不必再想它。****

### ⑤ 数字

| 度量 | R1071 | **R1072** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| **锚点数** | — | **3** |
| **`.text` 指针命中** | — | **0 / 3** |
| **`.rdata` 指针命中** | — | **0 / 3** |
| **便宜路径** | 待试 | **证伪** |
| **真路径** | — | **三条，都要先定结构布局** |

### 教训

> **试最便宜的那条没错，错的是没在试之前把「它不该成立」的理由说出来。
> → 因为若先说得出理由，那次试就是**验证**而不是**试探**；而探测与验证的差别在于，后者事前可判。**
> **→ 与 R1064 那次同族：那一轮我以为框架差异解释得掉缺口，而基线给了 7,930；
> → 这一轮我以为池旁有指针，而结构上说池不带指针。**
> **→ 两次都是「我的假设没有先被检查」。**
"""

if "这个便宜路径**不存在**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1072 —— **「名字旁边有代码指针」不存在；那是第四次同一个错**

### 结果：三个锚点，零个指针

```
CaptchaProvider.Priority!Getter    .text **0**   .rdata **0**   其他非小值 27
CaptchaProvider.Type!Getter        .text **0**   .rdata **0**   其他非小值 27
CaptchaProvider.Priority!Property  .text **0**   .rdata **0**   其他非小值 27
```

**而那 27 个「其他非小值」也不在 `.text`/`.rdata` —— 是长度、对齐填充或池内偏移。**

### 而这次可以预判

**元数据字符串是**连续的 UTF-8 池**（R1039 的字母序正是池的性质）⇒ **池里不会有逐条指针**，
指针在另一张表里用偏移指回来。**所以这个假设从结构上就不该成立。**
**⇒ 试没错，错的是我没在试之前说出这个理由 —— 那样这次是**验证**，而不是**试探**。**

**⇒ 第四次同族（R764 · R1047 · R1054 · 现在）：先假设形状，再把不符读成不存在。
而这次的「不存在」是真的，但真值来自结构推理，我却从一次零得到。**

### 真路径的规模

| 路径 | 可行性 |
|---|---|
| 名字旁找指针 | **已证伪** |
| 解析 `MethodTable` / `ReflectionMethod` 结构表 | **一个工程（需先定布局）** |
| `TypeManager` 的 vtable 槽映射 | 同上 |
| 从数据流反推类型 | 不规模 |

**⇒ 三条真路径都是「先定结构布局」的三种说法。**

### 而本轮不是白跑

**它关掉了一条看起来最省的路。若不试，「名字旁边有没有指针」会一直是悬念，而悬念让人反复回来试。
记下来之后，下一轮不必再想它。**

### 数字

| 度量 | R1071 | **R1072** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 锚点 / `.text` 命中 | — | **3 / 0** |
| 便宜路径 | 待试 | **证伪** |
| 真路径 | — | **三条，都需先定结构** |

**纪律**：探测与验证的差别在于后者事前可判。假设先被检查，试才不是试探。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1072", NOTE)
append(RBLOCK, "R1072", "\n---\n\n## 496. **名字旁无代码指针；第四次同一个错**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1072: the cheap bridge does not exist, and the reason was predictable\n\n"
     "R1071 said the next step was mapping function addresses to method names, since a NativeAOT reflection method\n"
     " record carries a native pointer. So the cheapest possible version of that was tried: look for a code pointer in\n"
     " the bytes beside a metadata string, and three anchors returned none -- no eight-byte value in the window pointed\n"
     " into .text and none into .rdata either.\n\n"
     "That was predictable and I did not predict it. Those metadata strings are one continuous UTF-8 pool, and R1039\n"
     " established the alphabetical ordering that is the signature of a pool; a pool does not carry per-entry\n"
     " pointers. The pointers live in a separate table and refer back by offset. So the hypothesis could not have held\n"
     " structurally, and testing it turned a verification I could have reasoned into a probe I had to run.\n\n"
     "This is the fourth time the same shape has appeared -- R764, R1047, R1054 and now this: assume a shape, then read\n"
     " every mismatch as absence. The absence here is real, but it came from a zero rather than from the structural\n"
     " argument that would have given it in advance.\n\n"
     "The remaining paths all reduce to one thing. Parsing MethodTable or ReflectionMethod records, walking the\n"
     " TypeManager's vtable slots, and recovering types from data flow are three names for establishing the structure\n"
     " layout first. That is the scale of the work R1045 described as a project, and it is now the only way to join\n"
     " names to addresses.\n\n"
     "The round is not wasted. It closes the route that looked cheapest, and without closing it, whether a pointer sits\n"
     " beside a name would stay an open question that invites being tried again.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, three anchors, zero .text\n"
     " hits, zero .rdata hits, one cheap path refuted, three real paths all needing the same prerequisite.\n\n"
     "The lesson is that probing and verifying differ: a verification could have been predicted in advance, and this\n"
     " one could have been."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
