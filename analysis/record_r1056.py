"""Record R1056: the real type name found by reverse lookup, and one property actually added."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 反查名字 → 找到**一个真缺口** → 补上 → (a) 的类型级缺口真的成 0（R1056）

**R1055 留了一个 Unknown：`CloudflareSolverConfig` 在镜像里的真实类型名。这一轮反查到了，而它带来一个**真修复**。**

### ① 反查：用**成员名**找拥有者，不猜路径

**`IsFetchingBalance` 与 `BalanceSupported` 这两个名字很独特，而元数据形状里类型名就在成员名前面：**

```
IsFetchingBalance     n=10     BalanceSupported    n=8
CloudflareSolver      n=146  →  Cybersole.CloudflareSolvers.CloudflareSolver,Cybersole.Core.Name!Getter
```

**→ 真实名字是 **`Cybersole.CloudflareSolvers.CloudflareSolver`**，命名空间与 `Cybersole.CaptchaProviders` **完全同构**。
→ 而我上一轮猜的 `Cybersole.Core.CloudflareSolverConfig` 是错的 —— 错在**把命名空间猜成了 Core 而不是按功能分域**。**

### ② 而真名一用，那个「假零」变成了「1 个真缺口」

```
R1055（假名）：meta=0    orig=0  repl=8  missing=0   UNRESOLVED
R1056（真名）：meta=25   orig=9  repl=8  missing=1
```

**→ 同一个类型，换一个名字，从「没问题」变成「少一个属性」。
→ 而那正是上一轮那个 `resolved` 列的用处：它**拒绝**把 `orig=0` 读成零缺口，于是名字才被去查。**

**→ 若上一轮我把那个假零写成「已覆盖」，这一轮就不会去找名字，而那个缺口会一直待在那里。**

### ③ 而缺口是 `IsFetchingBalance` —— 而 R361 的注释自己说了这件事

**镜像 9 个属性：`ApiKey` · `Balance` · `BalanceSupported` · `Concurrency` · `Count` · `Id` ·
`IsFetchingBalance` · `Name` · `Type`**
**复刻件 8 个，缺 `IsFetchingBalance`。**

**→ 而 R361 的注释写着：「the binding table names three more fields on this record; **`CloudflareSolverConfig`
already had two of them, `CaptchaProvider` had none**」——
→ 所以当年给两个类各补字段，而 `IsFetchingBalance` **只到了 `CaptchaProvider`**。
→ 那句注释说「`CloudflareSolverConfig` 已有两个」，而实际**只补了两个，第三个漏了** ——
→ **一条记录自己写下的中间状态，和它当时的判断，差了一个字段。**

### ④ 而修的是一个属性，验证的是一个列

**加了 `IsFetchingBalance` 到 `CloudflareSolverConfig`，重算：**

```
CaptchaProvider          meta=24  orig=9  repl=11  missing=0  added=0
CloudflareSolverConfig   meta=25  orig=9  repl=9   missing=0  added=0
type-level gaps total: 0 (unresolved types: 0)
```

**→ 而这次的两个零**都是真的**：两个类型原版侧都有 9 个属性，复刻件侧都覆盖了。
→ **无未解类型** ⇒ 结论句不再需要「在查询成功的类型上」那个限定词 —— 因为**全部**都成功了。**

### ⑤ 而我又踩了一个 PowerShell 的坑

**用 `$t.Replace(old, new)` 时 `new` 里写了 `\\n` 当换行 —— 而单引号字符串里那是**字面反斜杠 n**。
→ 于是那行注释与元组被拼成一行，元组被注释掉，`TYPES` 少一个元素 ⇒ 输出只剩一行而我一开始没注意。**
**→ 修法：用 `edit` 工具，不用 PowerShell 做源码文本手术。那是我自己的纪律，而这一轮第一次破它。**

### ⑥ 数字

| 度量 | R1055 | **R1056** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 3 / 650 | **4 / 889（改了 GlobalSettings.cs）** |
| 函数数 | 174,293 | **174,293** |
| **`CloudflareSolverConfig` 原版侧** | 0（假零） | **9（真）** |
| **它的缺口** | 「0」（假） | **1 → 修后 0** |
| **未解类型** | 1 | **0** |
| **类型级缺口合计** | 「0」（有条件） | **0（无条件）** |
| **补的属性** | — | **1（`IsFetchingBalance`）** |

### 教训

> **上一轮那个 `resolved` 列在**下一轮**才显出价值：它拒绝把一个 `orig=0` 读成好消息，
> 于是这一轮才去查真名，而真名一用就露出一个真缺口。**
> **→ 所以「不把不知道写成零」的回报是滞后的 —— 它在当时只让表难看，而在下一轮让人找对地方。**
> **→ 而 R361 那条注释也值得记：它写道「已有两个」，而实际漏了第三个。
> → 一条注释记录的是**当时的判断**，而字段数是**后来可算的** —— 两者不一致时，可算的那个是对的。****
"""

if "反查名字 → 找到**一个真缺口**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1056 —— **反查名字 → 找到一个真缺口 → 补上 → (a) 类型级缺口真的成 0**

### 反查：用成员名找拥有者

```
IsFetchingBalance n=10 · BalanceSupported n=8 · CloudflareSolver n=146
→ Cybersole.CloudflareSolvers.CloudflareSolver,Cybersole.Core.Name!Getter
```

**真实名字 `Cybersole.CloudflareSolvers.CloudflareSolver`，与 `Cybersole.CaptchaProviders` **同构**。
我上一轮猜的 `Cybersole.Core.CloudflareSolverConfig` 错在把命名空间猜成 Core。**

### 而真名一用，假零变真缺口

```
R1055（假名）meta=0   orig=0  repl=8  missing=0  UNRESOLVED
R1056（真名）meta=25  orig=9  repl=8  missing=1
```

**⇒ 上一轮那列 `resolved` 的价值在**这一轮**才显出来：它拒绝把 `orig=0` 读成好消息，
于是才去查真名，而真名一用就露出缺口。**

### 缺口 = `IsFetchingBalance`，而 R361 的注释说的正是这件事

镜像 9 个属性，复刻件 8 个。R361 注释写「`CloudflareSolverConfig` **already had two** of them,
`CaptchaProvider` **had none**」—— 而 `IsFetchingBalance` 只到了 `CaptchaProvider`。
**⇒ 一条注释记的是**当时的判断**，字段数是**后来可算的**；不一致时可算的那个对。**

### 修后

```
CaptchaProvider  orig=9 repl=11 missing=0 · CloudflareSolverConfig orig=9 repl=9 missing=0
type-level gaps total: 0 (unresolved types: 0)
```

**两个零都是真的，且无未解类型 ⇒ 结论句不再需要限定词。**

### 而我又破了自己的纪律一次

`$t.Replace()` 里用 `\\n` 当换行 —— 单引号里是**字面反斜杠 n** ⇒ 元组被注释掉，`TYPES` 少一个元素。
**修法用 `edit` 工具。不用 PowerShell 做源码文本手术。**

### 数字

| 度量 | R1055 | **R1056** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 3 / 650 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| `CloudflareSolverConfig` 原版侧 | 0（假零） | **9（真）** |
| 其缺口 | 「0」（假） | **1 → 修后 0** |
| 未解类型 | 1 | **0** |
| 补的属性 | — | **1（`IsFetchingBalance`）** |

**纪律**：「不把不知道写成零」的回报是滞后的 —— 它当时只让表难看，下一轮让人找对地方。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1056", NOTE)
append(RBLOCK, "R1056", "\n---\n\n## 480. **反查名字 → 一个真缺口 → 补上 → (a) 类型级缺口成 0**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1056: the real type name found by reverse lookup, and one property actually added\n\n"
     "R1055 left the Cloudflare solver config as Unknown because Cybersole.Core.CloudflareSolverConfig returned no\n"
     " metadata. The query reverses: a distinctive property name appears in the same <type>,<asm>.<member>!Getter\n"
     " shape, and the type in front of it is the answer. IsFetchingBalance and BalanceSupported both pointed at\n"
     " Cybersole.CloudflareSolvers.CloudflareSolver, a namespace shaped exactly like Cybersole.CaptchaProviders. My\n"
     " guess had put it under Core, which was wrong about how the original groups things.\n\n"
     "With the real name the type went from zero original properties and nothing missing to nine original properties\n"
     " and one missing. The same type, a different name, a different answer -- and the resolved column added last round\n"
     " is what forced the search, because it refused to read an empty original side as good news. That column made the\n"
     " table look worse for a round and then pointed at the right place.\n\n"
     "The missing property is IsFetchingBalance. The image carries nine on this record and the replica had eight. R361's\n"
     " comment says the binding table names three more fields and that CloudflareSolverConfig already had two of them --\n"
     " but only two of the three reached this record, the third went to CaptchaProvider alone, and the comment recorded\n"
     " the judgement of the moment rather than the count.\n\n"
     "Adding it takes both types to nine original and nine replica with nothing missing and no unresolved types, so the\n"
     " conclusion no longer needs the qualifier it carried last round: every type in the table resolved.\n\n"
     "I also broke my own rule on the way. I patched the generator with a PowerShell string replace and wrote backslash-n\n"
     " inside single quotes, which is a literal backslash and an n, so the tuple became part of a comment and the list\n"
     " lost an entry. The edit tool does it properly and that is what the rule was for.\n\n"
     "Figures: suite green at 2258, freshness four files and 889 lines, count 174,293, two types at zero gaps, zero\n"
     " unresolved types, and one property added.\n\n"
     "The lesson is that refusing to write an unknown as a zero pays back late -- it costs a round of ugly numbers and\n"
     " then sends the next round to the right address."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
