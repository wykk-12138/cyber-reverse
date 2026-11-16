"""Record R878: retract R876's naming of the ninth sequence."""

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
### 撤回：第九条序列**没有名字**，`DrawStores` 是属性名（R878）

**R876 写「第九条序列有名字：`DrawStores`」。错的。**

### 为什么错：那是把最近的**大写字符串**当成了归属

**R876 看到的是这个排布：**

```
14338037b  _alias
143380382  _documentNumber
143380392  DrawStores          ← 我把它当成序列名
14338039d  _drawid
1433803a5  _uniqCode
...
143380569  <Start>d__21        ← 序列从这里开始
```

**算一下字节：`_alias` 到 `_documentNumber` 隔 7 字节，`_documentNumber` 到 `DrawStores` 隔 16 字节，
`DrawStores` 到 `_drawid` 隔 11 字节。**

**`DrawStores` 是 10 个字符，加 UTF-16 结束符是 22 字节 —— 塞不进 11 字节。
所以它们是**各自独立的字符串对象**，不是同一块连续字符数组。**

**而 NativeAOT 的字符串字面量表按**首次使用顺序**排布 ——
相邻只说明「编译器先排到它」，不说明任何归属关系。**

### 那 `DrawStores` 是什么

**它夹在 `_documentNumber` 与 `_drawid` 之间，没有下划线前缀。**
**这一整段是**模型的名字清单**：`_xxx` 是属性后备字段，`DrawStores` 是没有后备字段的公开属性名。**

**所以它是一个**属性**，与「这条步骤序列属于谁」无关。**

### 那第九条序列的归属

**未知。**

**它的 12 个步骤（21–34）在 `StoreFlow` 里对上 8 个（R877），这个数字不变 ——
但 R877 里那句「`DrawStores` 12 步」的归属前缀要删掉。**

**而且因为归属未知，「要不要为它建一个流程类」这个问题（R877 说最该判）**本身就不成立** ——
连它属于谁都不知道，谈不上建类。**

### 这是同一形态的第 N 次

| 轮 | 把什么当成了什么 | 实际 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点 |
| R875 | 四个 uniqCode 记号并列 | 两个字段 + 一个常量 |
| **R876 → R878** | **相邻的大写串 = 归属** | **独立字符串对象，按首用顺序排布** |

**R875 我给自己的规则是「每次并列问一句：需要来源吗」。
这次需要的规则更简单：**先看两个串之间隔多少字节。**
"""

if "撤回：第九条序列**没有名字**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R878 appended")

BLOCKER = """

---

## 302. 撤回 R876：第九条序列没有名字

> R878。未改产品代码。

### 一、错在哪

**R876 写「第九条序列有名字：`DrawStores`」。**

**我看到的是这个排布：**

```
14338037b  _alias
143380382  _documentNumber
143380392  DrawStores      ← 我当成序列名
14338039d  _drawid
1433803a5  _uniqCode
143380569  <Start>d__21    ← 序列实际从这里开始
```

**字节间隔：`_alias`→`_documentNumber` 7 字节 · →`DrawStores` 16 字节 · →`_drawid` 11 字节。**

**`DrawStores` 10 字符 + UTF-16 结束符 = 22 字节，**塞不进 11 字节**。
所以它们是各自独立的字符串对象，不是同一块连续字符数组。**

**而 NativeAOT 的字符串字面量表按**首次使用顺序**排布 ——
相邻只说明编译器先排到它，不说明任何归属。**

### 二、`DrawStores` 到底是什么

**它夹在 `_documentNumber` 与 `_drawid` 之间，没有下划线前缀。**

**这一整段是模型的名字清单：`_xxx` 是属性后备字段，`DrawStores` 是没有后备字段的公开属性名。**

**所以它是**属性**，与序列归属无关。**

### 三、连带撤掉的是什么

**R877 说「最该判的一条：`DrawStores` 要不要建流程类」。**

**这条问题**不成立** —— 归属都不知道，谈不上建类。**

**而 R877 的 8/12 数字**不变**（那是拿 12 个步骤名直接对 `StoreFlow` 算的），
只是不该带那个归属前缀。**

**这是本轮唯一实质的更正：一个数字对，而它旁边那句名字是错的。**

### 四、同一形态第 N 次

| 轮 | 把什么当成了什么 | 实际 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点 |
| R875 | 四个 uniqCode 记号并列 | 两个字段 + 一个常量 |
| **R876 → R878** | **相邻的大写串 = 归属** | **独立对象，按首用顺序排布** |

**R875 我给自己立的规则是「每次并列问：需要来源吗」。
这次需要的更简单：**先算两个串之间隔多少字节。** **

**一个能算的检查，胜过一条要靠记性的规则。**

### 五、验证

```
0x143380392 DrawStores 与 0x14338039d _drawid 相隔 11 字节
"DrawStores" 长 10 字符 → UTF-16 需 22 字节（含结束符）
→ 不可能同属一块连续数组 → 独立字符串对象
→ 排布顺序 = 字面量首次使用顺序，与语义归属无关
本轮未改产品代码
```

### 六、仍然 Unknown

- **第九条序列（21–34）属于谁**：**Unknown —— 而这现在是明确的一句话，不是「`DrawStores`」。**
- **`DrawStores` 这个属性是什么**：**Unknown** —— 名字像「抽签店列表」，
  **但它与 `_drawid`/`_uniqCode` 同属一个模型，可能是「这个上下文涉及的店」。**
- **字面量表的排布顺序是否真是首用顺序**：**Inference** ——
  **这条我没证，只是它比「按字母序」更符合观察到的乱序。**

### 七、教训

**我上一轮把「邻近」读成「归属」，这一轮算出它不可能邻近。**

**而两次用的是同一个动作：看那一段有什么。区别是这次我算了字节。**

**所以「看周围」这个动作本身不够 —— 要问「它们真的是同一个东西吗」，
而那个问题有时候能用算术回答（22 > 11），有时候不能。**

**能用算术回答的时候，就不该靠推断。**
"""

VERDICT = """

---

## 第 878 轮：撤回 —— 第九条序列没有名字

### 错在哪

**R876 写「第九条序列有名字：`DrawStores`」。那是把最近的**大写字符串**当成了归属。**

```
14338037b  _alias
143380382  _documentNumber
143380392  DrawStores      ← 我当成序列名
14338039d  _drawid
143380569  <Start>d__21    ← 序列实际从这里开始
```

**字节间隔：7 · 16 · **11**。而 `DrawStores` 10 字符 + UTF-16 结束符 = **22 字节**，塞不进 11 字节。**

> **所以它们是各自独立的字符串对象。而 NativeAOT 字面量表按**首次使用顺序**排布 ——
> 相邻只说明编译器先排到它，不说明任何归属。**

### `DrawStores` 到底是什么

**夹在 `_documentNumber` 与 `_drawid` 之间，没有下划线前缀 → 是**没有后备字段的公开属性名**，
这一整段是模型的名字清单。它与序列归属无关。**

### 连带撤掉什么

**R877 说「最该判的一条：`DrawStores` 要不要建流程类」—— 这条问题**不成立**，归属都不知道，谈不上建类。**

**而 8/12 那个数字**不变**（拿 12 个步骤名直接对 `StoreFlow` 算的），只是不该带那个归属前缀。**

> **一个数字对，而它旁边那句名字是错的。**

### 同一形态第 N 次

| 轮 | 把什么当成了什么 | 实际 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点 |
| R875 | 四个 uniqCode 记号并列 | 两个字段 + 一个常量 |
| **R876 → R878** | **相邻的大写串 = 归属** | **独立对象，按首用顺序排布** |

### 仍然 Unknown

**第九条序列（21–34）属于谁**（**现在是明确的一句话，不是「`DrawStores`」**）·
**`DrawStores` 这个属性是什么**（像「抽签店列表」，但同属那个结账上下文模型）·
**字面量表是否真按首用顺序**（**Inference，我没证**）

### 教训

> **上一轮我把「邻近」读成「归属」，这一轮算出它不可能邻近。**
> **两次用的是同一个动作：看那一段有什么。区别是这次我算了字节。**
> **所以「看周围」本身不够 —— 要问「它们真的是同一个东西吗」，而那个问题有时候能用算术回答（22 > 11）。**
> **能用算术回答的时候，就不该靠推断。**
"""

BACKLOG_ADD = """

## 撤回 — 第九条序列没有名字（R878）

**R876 写「第九条序列有名字：`DrawStores`」→ **错的**。**

```
143380392  DrawStores   与   14338039d  _drawid   相隔 11 字节
"DrawStores" 10 字符 + UTF-16 结束符 = 22 字节  →  塞不进 11 字节
```

**→ 独立字符串对象；NativeAOT 字面量表按**首次使用顺序**排布 → 相邻 ≠ 归属。**

### `DrawStores` 是属性名

**夹在 `_documentNumber` 与 `_drawid` 之间、无下划线前缀 → 无后备字段的公开属性名。**

### 连带撤掉

**R877「`DrawStores` 要不要建流程类」→ **问题不成立**（归属未知）。**
**8/12 数字**不变**，只是不该带归属前缀。**

| 仍 Unknown | |
|---|---|
| 第九条序列（21–34）属于谁 | **明确的一句话：Unknown，不是 `DrawStores`** |
| `DrawStores` 属性是什么 | 像「抽签店列表」，同属结账上下文模型 |
| 字面量表是否按首用顺序 | **Inference，未证** |

**纪律**：**「看周围」不够 —— 要问「它们真的是同一个东西吗」；能用算术回答（22 > 11）时就不该靠推断。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R878", BLOCKER)
    ensure(RSTATUS, "R878", BLOCKER)
    ensure(RVERDICT, "第 878 轮", VERDICT)
    ensure(BACKLOG, "R878", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R878" not in h:
        h += ("\n## R878 补充 — **撤回 R876**：第九条序列没有名字\n\n"
              "**`DrawStores`@`0x143380392` 与 `_drawid`@`0x14338039d` 相隔 **11 字节**，而 `DrawStores` 10 字符 + UTF-16 结束符 = **22 字节** → 塞不进 → **独立字符串对象**。"
              "**NativeAOT 字面量表按首用顺序排布 → 相邻 ≠ 归属。**\n"
              "**`DrawStores` 是**属性名**（夹在 `_documentNumber` 与 `_drawid` 之间，无下划线前缀）。**\n"
              "**连带撤掉 R877「`DrawStores` 要不要建流程类」——问题不成立（归属未知）。8/12 数字不变，只是不该带归属前缀。**\n"
              "**纪律：「看周围」不够 —— 要问「它们真的是同一个东西吗」；**能用算术回答（22 > 11）时就不该靠推断。****\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R878"), (RSTATUS, "R878"), (RVERDICT, "第 878 轮"), (BACKLOG, "R878")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R878: retracting R876 -- the ninth sequence has no name, and arithmetic says so\n\n"
         "R876 named the ninth sequence DrawStores. That was wrong, and the way it was wrong is checkable rather than\n"
         " a matter of judgement. DrawStores sits at 0x143380392 and the next string, _drawid, at 0x14338039d. Eleven\n"
         " bytes apart. DrawStores is ten characters, which is twenty-two bytes in UTF-16 including the terminator, so\n"
         " it cannot fit in eleven. They are separate string objects, and NativeAOT orders its literal table by first\n"
         " use, which means adjacency records the compiler's ordering and nothing about ownership.\n\n"
         "What DrawStores actually is shows in its position: it sits between _documentNumber and _drawid without an\n"
         " underscore, in a run that is a model's name list where _-prefixed entries are backing fields. It is a public\n"
         " property with no backing field stored beside it. It has nothing to say about which flow owns the steps.\n\n"
         "So the sequence 21 through 34 is unattributed. R877's count of eight steps matching StoreFlow stands, because\n"
         " that number comes from comparing twelve step names against the class and never depended on the attribution.\n"
         " What does not stand is R877's conclusion that the most pressing judgement was whether DrawStores should become\n"
         " a flow class -- that question presupposes a name the evidence does not give.\n\n"
         "One number was right and the sentence beside it was wrong, which is the specific hazard of writing an\n"
         " attribution next to a measurement. The measurement can be recomputed and the attribution cannot, so the\n"
         " attribution is where doubt should sit.\n\n"
         "This is the fourth round in this shape. R830 and R836 read site names against URL shapes as one thing; R863\n"
         " read 'behaviour unavailable' and 'UI' as one breakage; R875 read four uniqCode markers as one kind, when two\n"
         " are fields and one is a constant; R876 read adjacency as ownership.\n\n"
         "The rule I gave myself at R875 was to ask, whenever listing things together, whether each needs a source.\n"
         " The rule this round needs is simpler and mechanical: measure the gap between the two strings. Where a question\n"
         " can be settled by arithmetic, it should not be settled by inference.\n\n"
         "Unknown: which flow owns steps 21 through 34, now stated plainly as unknown rather than as a name; what the\n"
         " DrawStores property holds, where the name suggests a list of draw stores and it shares a model with _drawid\n"
         " and _uniqCode, so plausibly the stores this checkout context concerns; and whether the literal table really\n"
         " is ordered by first use, which is inference and unproven though it explains the observed disorder better\n"
         " than alphabetical order would.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
