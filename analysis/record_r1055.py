"""Record R1055: criterion (a) computed, and one real zero beside one false one."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### (a) 的「类型级缺口」第一次被**算**出来；而一个真的零旁边是一个假的零（R1055）

**五轮都在取证与文档，而 (a)「类型级缺口 → 0」一直没被算过。这一轮把它变成算术。**

### ① 而判据是现成的：反射元数据的形状

**镜像里属性形如 `<命名空间>.<类型>,<程序集>.<成员>!Getter`。
→ 所以「原版某个类型有哪些属性」是一个**查询**，而「复刻件有哪些」是读源码的 `get` 访问器。
→ 两者相减就是 (a) 的缺口 —— **不需要判断，只需要算。****

### ② 而结果里有一个真的零和一个假的零

```
CaptchaProvider          meta=24  orig=9  repl=11  missing=0  added=0
CloudflareSolverConfig   meta=0   orig=0  repl=8   missing=0  added=7  UNRESOLVED
```

**→ 第一行是**真的**：镜像 9 个属性全在复刻件里（`Priority` · `Name` · `Type` · `ApiKey` · `Balance` ·
`Count` · `Concurrency` · `BalanceSupported` · `IsFetchingBalance`），复刻件另有 `Id`（本地主键）与
`Enabled`（用列表成员表达镜像的 `EnabledProviders` 集合）。**

**→ 第二行是**假的**：`orig=0` 说明原版侧查询为空，而 `missing=0` 是**空集减任何集合都是空**的必然结果。
→ 而 `Cybersole.Core.CloudflareSolverConfig` 那个类型名是**我猜的** —— 镜像里不叫这个。**

**→ 于是同一个 `0` 在同一张表里代表两件相反的事。而那是 R1044 那条「零值需要对照」的又一次：
那次的对照是横向的（拿已知存在的比），这次的对照是**纵向的**（原版侧有没有内容）。**

### ③ 而修法不是说「大概没问题」，是把两种零分开

**生成器现在对每个类型判 `resolved`（原版侧有没有属性）：
→ 未解的报 **Unknown + 缺什么**（这个类型在镜像里的真实名字），并且**不计入缺口，也不计为已覆盖**。
→ 所以结论那一行写的是「**在查询成功的类型上**，(a) 的缺口为 0」，而不是「缺口为 0」。**

**→ 而那句限定词是整份文档最关键的一句：它把「算过并且是零」与「没算过」分开了。**

### ④ 而那三个自加字段的理由要写进表里

**`Id` 是本地主键；`Enabled` 是「列表成员即启用」；而 `CloudflareSolverConfig` 的 7 个自加同理。
→ 若理由不写进表，下一轮会把它们当成**反向缺口**（「复刻件多了字段」）而去删 ——
→ 而 R815 那次「按证据删除，删掉了证据本身」正是这个形状。**

### ⑤ 数字

| 度量 | R1054 | **R1055** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 3 / 650 | **3 / 650** |
| 函数数 | 174,293 | **174,293** |
| **`CaptchaProvider` 元数据** | 24 | **24** |
| **`CaptchaProvider` 原版属性 / 复刻件属性** | 未知 | **9 / 11** |
| **`CaptchaProvider` 缺口** | 未算 | **0（真的）** |
| **`CloudflareSolverConfig` 原版侧** | 未算 | **0 ⇒ UNRESOLVED（假零已分隔）** |
| **类型级缺口合计** | 未算 | **0（仅查询成功的类型）** |
| **未解类型** | — | **1** |
| **`docs/TYPE_COVERAGE.md`** | 不存在 | **2,675 字节（生成）** |

### 教训

> **同一个 `0` 可以是「齐了」也可以是「没查到」，而它们在同一张表里长得一样。
> → 这一轮的修法不是把假的零改成「大概有」，是**加一列 `resolved`**，让两种零各有名字。**
> **→ 而那让结论句子必须带限定词 ——「在查询成功的类型上」—— 而那个限定词就是这一轮真正的产出。**
"""

if "(a) 的「类型级缺口」第一次被**算**出来" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1055 —— **(a) 的类型级缺口第一次被算出来；一个真的零旁边是一个假的零**

### 判据是现成的

镜像属性形如 `<ns>.<Type>,<asm>.<Member>!Getter` ⇒ 「原版某类型有哪些属性」是**查询**；
复刻件侧读源码 `get` 访问器 ⇒ **相减即缺口，不用判断。**

### 而结果里一个真零一个假零

```
CaptchaProvider          meta=24  orig=9  repl=11  missing=0  added=0
CloudflareSolverConfig   meta=0   orig=0  repl=8   missing=0  added=7  UNRESOLVED
```

**真零**：镜像 9 个属性全在复刻件（`Priority`·`Name`·`Type`·`ApiKey`·`Balance`·`Count`·`Concurrency`·
`BalanceSupported`·`IsFetchingBalance`），复刻件另有 `Id`（本地主键）与 `Enabled`（列表成员即启用）。

**假零**：`orig=0` ⇒ `missing=0` 是**空集减空集**的必然；而 `Cybersole.Core.CloudflareSolverConfig`
这个类型名是**我猜的**，镜像里不叫这个。

**⇒ 同一个 `0` 在同一张表里代表两件相反的事。R1044 那次的对照是横向的（拿已知存在的比），
这次的对照是**纵向的**（原版侧有没有内容）。**

### 修法：加一列 `resolved`，让两种零各有名字

未解的报 **Unknown + 缺什么**（真实类型名），且**不计入缺口、也不计为已覆盖**。
结论句因此必须写「**在查询成功的类型上**，缺口为 0」—— 那个限定词是真正的产出。

### 而自加字段的理由要写进表里

`Id`（本地主键）· `Enabled`（列表成员即启用）等。**不写理由，下一轮会把它们当反向缺口去删** ——
R815「按证据删除，删掉了证据本身」正是这个形状。

### 数字

| 度量 | R1054 | **R1055** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| `CaptchaProvider` 属性 | 未知 | **原版 9 / 复刻件 11** |
| `CaptchaProvider` 缺口 | 未算 | **0（真的）** |
| `CloudflareSolverConfig` 原版侧 | 未算 | **0 ⇒ UNRESOLVED** |
| 类型级缺口合计 | 未算 | **0（仅查询成功）** |
| 未解类型 | — | **1** |
| `TYPE_COVERAGE.md` | — | **2,675 字节** |

**纪律**：同一个 `0` 可以是「齐了」也可以是「没查到」；修法是给它们各自的名字，不是把它们都当成好消息。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1055", NOTE)
append(RBLOCK, "R1055", "\n---\n\n## 479. **(a) 类型级缺口第一次被算出来；一个真零一个假零**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1055: criterion (a) computed, and one real zero beside one false one\n\n"
     "Five rounds of evidence gathering and documents, and criterion (a)'s type-level gaps had never been counted. They\n"
     " can be: the image carries a property as <ns>.<Type>,<asm>.<Member>!Getter, so the original's property set for a\n"
     " type is a query, and the replica's is its source. Subtracting is arithmetic rather than judgement.\n\n"
     "The first run gave two zeros that mean opposite things. CaptchaProvider came out at nine original properties and\n"
     " eleven replica ones with nothing missing, and the two extras are local bookkeeping and a representation choice.\n"
     " That zero is real. CloudflareSolverConfig came out with zero original properties and therefore nothing missing,\n"
     " which is empty-set arithmetic and means the query found no metadata at all -- the type name was my guess and the\n"
     " image does not use it.\n\n"
     "So the same digit in one table stood for two opposite facts. R1044's control was lateral, comparing against\n"
     " something known to be non-zero; this one has to be longitudinal, asking whether the original side has content\n"
     " before its zero can be read.\n\n"
     "The fix is a resolved flag rather than a hedge. An unresolved type reports Unknown with what is missing -- its real\n"
     " name -- and counts neither as a gap nor as covered. That forces the conclusion sentence to say on types whose\n"
     " original side resolved, the gap is zero, and that qualifier is the actual product of the round.\n\n"
     "The reasons for the extra fields are in the table too. Id is a local key and Enabled expresses what the image says\n"
     " with an EnabledProviders collection. Without those reasons written down, a later round would read them as reverse\n"
     " gaps and delete them, which is R815's shape: deleting on evidence, and deleting the evidence with it.\n\n"
     "Figures: suite green at 2258, freshness three files and 650 lines, count 174,293, nine original properties against\n"
     " eleven replica ones with zero missing, one unresolved type, zero gaps across resolved types, and a sixth\n"
     " generated coverage document at 2,675 bytes.\n\n"
     "Unknown: the real name of the Cloudflare solver config type in the image, which the next round can search for by\n"
     " its members rather than by a guessed path.\n\n"
     "The lesson is that a zero can mean complete or unmeasured, and the cure is to give the two their own names rather\n"
     " than to treat both as good news."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
