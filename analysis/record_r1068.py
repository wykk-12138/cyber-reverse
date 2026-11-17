"""Record R1068: sharding past the cap gives a type coverage of 89%, against a function ratio of 63%."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 分片绕开上限：类型覆盖 **89.3%**，而函数只有 **62.9%**（R1068）

**R1067 说 `ida.py str` 有 500 硬上限，所以「原版 0 个类型」是窗口的零。这一轮分片，而分片自己是**可验证的**。**

### ① 分片算法：让「完整」变成可判的

```
for letter in A..Z:
    q = ",Cybersole." + letter
    hits = probe(q, 500)
    if len(hits) >= 500:           ← 该片**饱和** ⇒ 不知道完整不完整
        split again on a second letter
    else:
        该片**不饱和** ⇒ **这一片是完整的**
```

**→ 关键：**不饱和的那一片可以判为完整**，因为返回数小于上限 ⇒ 没有东西被截掉。
→ 而饱和的片再细分（26 → 26×26）。**

**→ 26 次查询后没有片饱和（`pool_hits=26`），所以**一层就够** ——
→ 而那是**分片算法自己告诉我的**，不是我的估计。**

### ② 而结果

```
original types = **122**   namespaces = **31**
replica  types = **648**   namespaces = **53**
同名（simple name）= **109**
只在原版 = **13**      只在复刻件 = **534**
```

**→ 类型级同名覆盖 = 109 / 122 = **89.3%**。**

**→ 而「只在复刻件」的 534 个不是缺口**：goal 允许命名不同，
→ 而其中一部分是复刻件**自己加的**（648 个类型 vs 122 —— 复刻件的 UI 层用了更多小类）。**

### ③ 而那两个数字的对比是本轮最有用的东西

| 层 | 覆盖 | 算法 |
|---|---|---|
| **类型** | **109 / 122 = 89.3%** | 同名类型 / 原版类型 |
| **函数** | **174,258 / 277,094 = 62.9%** | `.pdata` ÷ 12 |
| **每类型函数密度** | 原版 **2,271** / 复刻件 **269** | 函数数 ÷ 类型数 |

**→ 类型几乎齐了（89%），而函数只有 63% ⇒ **差在每类型的密度，不在类型的存在。**
→ 而「原版每类型 2,271 个函数」听起来荒谬 —— 一个类型不该有 2,271 个方法。
→ **所以那个密度的读法是错的**：NativeAOT 的**函数不归属于类型**，`.pdata` 数的是**全部编译产物**，
→ 而 `Cybersole.` 那 122 个只是**有属性的类型**，不是全部类型。**

**→ 所以「每类型密度」这个派生量**没有意义**，我算它是错的。
→ 而正确的读法是：**类型层 89%，函数层 63%，两者差 26 个百分点，而原因未知** —— 那才是诚实的。**

### ④ 而 122 是**下界**，文档里已写

**`business_types.py` 的原版侧只算「有属性访问器的类型」⇒ 纯静态类、纯枚举、纯接口会漏。
→ 所以 122 是**下界**，而 109/122 是一个**下界的覆盖**，真实覆盖可能更高（若漏掉的类型复刻件也有）。**

### ⑤ 数字

| 度量 | R1067 | **R1068** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 比例 | 62.9% | **62.9%** |
| **原版业务类型** | 未知（窗口 500） | **122（下界，31 命名空间）** |
| **复刻件业务类型** | 648 | **648（53 命名空间）** |
| **同名** | — | **109** |
| **类型级覆盖** | — | **89.3%（下界）** |
| **只在原版** | — | **13** |
| **分片查询次数** | — | **26（一层即够，无片饱和）** |
| **「每类型密度」** | — | **算过，然后判为无意义** |

### 教训

> **分片的价值不只是绕开上限，是让「完整」变成**可判的**：
> 不饱和的片可以判为完整，而饱和的片自己举手要求细分。**
> **→ 而这一轮我也算了一个派生量（每类型 2,271 个函数）然后判它是错的 ——
> 因为 NativeAOT 的函数**不归属类型**。一个看起来能算的比率，算出来是荒谬值，
> 而荒谬值这次指向的是**我的分母不对**。**
> **→ 与 R1064 那次同族（每函数 6 字节），方向相反：那次是分子荒谬，这次是分母。**
"""

if "类型覆盖 **89.3%**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1068 —— **分片绕开上限：类型 89.3% vs 函数 62.9%**

### 分片让「完整」变成可判的

```
某片返回 < 500  ⇒ 不饱和 ⇒ **该片完整**
某片返回 ≥ 500  ⇒ 饱和 ⇒ 再细分
```

**26 次查询后没有片饱和 ⇒ 一层就够 —— 那是**算法自己说的**，不是我的估计。**

### 结果

```
original types = **122**（31 命名空间）    replica = **648**（53 命名空间）
同名 = **109**    只在原版 = **13**    只在复刻件 = **534**（命名不同，非缺口）
类型级覆盖 = 109/122 = **89.3%**
```

### 而对比是有用的

| 层 | 覆盖 |
|---|---|
| **类型** | **109 / 122 = 89.3%** |
| **函数** | **174,258 / 277,094 = 62.9%** |

**⇒ 类型几乎齐了，函数只有 63% ⇒ 差不在「类型存在」，而原因**未知**。**

### 而我算了一个派生量然后判它错

「原版每类型 2,271 个函数」—— 荒谬，因为 **NativeAOT 的函数不归属类型**：`.pdata` 数全部编译产物，
而 `Cybersole.` 那 122 个只是**有属性的类型**。⇒ **「每类型密度」这个派生量无意义，判为错。**

**⇒ 与 R1064「每函数 6 字节」同族：那次分子荒谬，这次**分母**荒谬。**

### 而 122 是下界

原版侧只算「有属性访问器的类型」⇒ 纯静态类/枚举/接口会漏 ⇒ 109/122 是**下界的覆盖**。

### 数字

| 度量 | R1067 | **R1068** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 原版业务类型 | 未知 | **122（下界）** |
| 复刻件业务类型 | 648 | **648** |
| 同名 | — | **109** |
| 类型级覆盖 | — | **89.3%（下界）** |
| 只在原版 | — | **13** |
| 分片查询 | — | **26，无片饱和** |

**纪律**：分片让「完整」可判；而荒谬的派生比率指向**分子或分母有一边不对**。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1068", NOTE)
append(RBLOCK, "R1068", "\n---\n\n## 492. **分片绕开上限：类型 89.3% vs 函数 62.9%**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1068: sharding past the cap gives type coverage of 89 per cent against 63 for functions\n\n"
     "R1067 established that a string query returns at most five hundred and that the zero on the original side was\n"
     " an artefact of that window. Sharding is the fix, and the useful part is that it verifies itself: a shard\n"
     " returning fewer than the cap cannot have been truncated, so it is complete, and a saturated one asks to be\n"
     " split again.\n\n"
     "Twenty-six queries, none saturated, so one level was enough -- and that is the algorithm reporting it rather than\n"
     " my estimate. The original has 122 types carrying properties across 31 namespaces; the replica has 648 across 53.\n"
     " 109 simple names appear on both sides, 13 only on the original, and 534 only in the replica, which is not a gap\n"
     " because the goal allows different names.\n\n"
     "Type coverage is therefore 109 of 122, 89.3 per cent, against a function ratio of 62.9 per cent. The types are\n"
     " nearly all present and the function count is not, so the difference is not whether types exist -- and why it is\n"
     " not is unknown rather than explained.\n\n"
     "I also computed a derived figure and then discarded it. Dividing functions by types gives 2,271 per type on the\n"
     " original, which is absurd for a type, and the reason is that NativeAOT functions do not belong to types: .pdata\n"
     " counts everything compiled, while the 122 are only the types that carry properties. A ratio whose value is\n"
     " absurd is pointing at one of its two sides, and this time it was the denominator.\n\n"
     "The 122 is a lower bound, since a type with no properties leaves no trace in this shape, so 89.3 per cent is a\n"
     " lower bound on coverage as well.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, 122 original types and 648\n"
     " replica ones, 109 shared names, 13 only original, 26 shard queries with none saturated, and one derived ratio\n"
     " computed and rejected.\n\n"
     "Unknown: the 26-point difference between type coverage and function ratio.\n\n"
     "The lesson is that sharding buys verifiability as well as reach, and that an absurd derived ratio points at\n"
     " whichever of its two sides is wrong."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
