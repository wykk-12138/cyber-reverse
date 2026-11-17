"""Record R1067: the string probe is capped at 500, so a zero from it is a property of the window."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 字符串探针**上限 500 条**，所以它的零是**窗口的属性**（R1067）

**上一轮的结论是「应用侧缺 ~103,000 函数是真的」。本轮想把它定位到类型级，于是数原版有多少业务类型。
→ 而复刻件侧 648，原版侧 **0**。那是一个假结论，而追它的过程给出了一条更重要的边界。**

### ① 第一步就错在 pattern 上

```
Cybersole\\.            → 500 条，全是短串：Cybersole.dll · Cybersole.Core …
,Cybersole.Core\\.      → 4 条，形状终于出现：
     Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.AccountGroup!Getter
,Cybersole.Stores\\.    → **0**   ← 我假设的程序集名不存在
```

**→ 程序集名就是 **`Cybersole`**（无子命名空间），所以我假设的 `,Cybersole.Stores.` 是零。
→ 而那 500 条 `Cybersole.` 命中的**全是短串** —— 属性形状的在**窗口之外**。**

### ② 而第二步查出了一个硬上限

```
--limit 6     → n=6
--limit 5000  → n=**500**
```

**→ `n` 是**返回条数**，而 **5000 也只回 500** ⇒ **存在 500 的硬上限**，且它**不在 `ida.py` 里**
（`ida.py` 只把 limit 透传给 `find_regex`，没有 clamp）⇒ **在 IDA 插件侧。**

**→ 所以 `ida.py str` 的返回**永远最多 500 条 —— 它是**抽样**，不是全量。**

### ③ 而那让「原版 0 个类型」有了正确读法

**→ 不是我正则写错（正则对 `,Cybersole.AccountGroup!Getter` 是匹配的），
→ 而是**我的窗口里没有那种形状** —— 500 条短串占满了。**
**→ 那是 R816 那条「先问这个来源是全量还是抽样」的**第五次**，而这次我第一次拿到了**硬的**证据：
→ 同一条查询、limit 从 6 到 5000，返回数停在 500。前四次都是靠推理判断抽样，这次是测出来的。**

### ④ 而修法不是改 pattern，是**拒绝发布**

**`business_types.py` 现在在 `orig` 为空时 `return 2` 并打印：**

```
REFUSED: the original side returned no types, and the probe is capped at 500 strings.
A zero here means the sample missed, not that the image has no such types.
Shard the query by prefix before publishing anything from this tool.
```

**→ 与 R1051 给 `vendor_coverage.py` 加的那个 `rows == 0` 守卫同族。
→ 而这次的守卫多了一句「Shard the query by prefix」—— 因为它指明了下一步，而不只是拒绝。**

### ⑤ 而下一步是明确的：分片绕开上限

**26 个首字母 × 每片最多 500 条 ⇒ 上限 13,000 条，够覆盖 `,Cybersole.` 的真实规模。
→ 而那是下一轮的第一步，写清了。**

### ⑥ 数字

| 度量 | R1066 | **R1067** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 比例 | 62.9% | **62.9%** |
| 复刻件业务类型 | 未测 | **648 类型 / 53 命名空间** |
| **原版业务类型** | — | **未知 —— 窗口只给 500 条短串** |
| **`ida.py str` 上限** | 未测 | **500 硬上限（5000 也只回 500）** |
| **程序集名** | 假设 `Cybersole.Core`/`Stores` | **就是 `Cybersole`** |
| **`business_types.py` 的 0** | — | **拒绝发布（`return 2` + 指明分片）** |

### 教训

> **「抽样」这件事我推理过四次（R816），而这一次是**测**出来的：
> 同一条查询，limit 6 到 5000，返回数停在 500。**
> **→ 而它同时解释了为什么我的正则「看起来没错却得到零」：窗口被短串占满，
> 而那与正则无关、与镜像无关，只与窗口有关。**
> **→ 所以「零」的第三种来源：不是空集（R1055），不是错轴（R1058），是**窗口太窄**。
> → 而三种都长得一样，都需要一个东西来区分：这次的区分物是**limit 的扫描**。**
"""

if "字符串探针**上限 500 条**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1067 —— **字符串探针上限 500 条，所以它的零是窗口的属性**

### 第一步错在 pattern

```
Cybersole\\.            500 条，全是短串（Cybersole.dll · Cybersole.Core …）
,Cybersole.Core\\.      4 条，形状出现：…AccountGrid,Cybersole.AccountGroup!Getter
,Cybersole.Stores\\.    **0**   ← 我假设的程序集名不存在；真名就是 `Cybersole`
```

### 第二步查出硬上限

```
--limit 6 → n=6        --limit 5000 → n=**500**
```

**⇒ 500 是**硬上限**，不在 `ida.py`（它只透传）⇒ 在 IDA 插件侧。
⇒ `ida.py str` 返回**永远 ≤500 条 = 抽样**。**

### 而那让「原版 0 类型」有正确读法

**不是正则错（对 `,Cybersole.AccountGroup!Getter` 是匹配的），而是**窗口里没那种形状** —— 被短串占满。
⇒ R816「先问来源是全量还是抽样」的**第五次**，而这次是**测**出来的（前四次靠推理）。**

### 修法是拒绝发布

`business_types.py` 在 `orig` 空时 `return 2`，并打印：
```
REFUSED: … the probe is capped at 500 strings.
A zero here means the sample missed, not that the image has no such types.
Shard the query by prefix before publishing anything from this tool.
```

### 下一步：分片绕开上限

26 个首字母 × 500 = 13,000 条，够覆盖 `,Cybersole.` 的真实规模。

### 数字

| 度量 | R1066 | **R1067** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 复刻件业务类型 | 未测 | **648 / 53 命名空间** |
| 原版业务类型 | — | **未知（窗口只给 500 短串）** |
| `ida.py str` 上限 | 未测 | **500 硬上限** |
| 程序集名 | 假设 Core/Stores | **就是 `Cybersole`** |
| `business_types.py` 的 0 | — | **拒绝发布** |

**纪律**：「零」的第三种来源 —— 不是空集、不是错轴，是**窗口太窄**。区分物是 **limit 的扫描**。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1067", NOTE)
append(RBLOCK, "R1067", "\n---\n\n## 491. **字符串探针上限 500 条，零是窗口的属性**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1067: the string probe is capped at 500, and its zero belongs to the window\n\n"
     "R1066 measured the application-side shortfall and left open which types it consists of. Counting the original's\n"
     " business types looked like the way to locate it. The replica side came out at 648 types across 53 namespaces;\n"
     " the original side came out at zero, which was wrong.\n\n"
     "Two mistakes sat behind that zero. The first was a pattern that hit short strings: Cybersole dot matched five\n"
     " hundred entries but all of them were things like Cybersole.dll, so no attribute-shaped metadata was in the reply\n"
     " at all, and a namespace I guessed at, Cybersole.Stores, does not exist because the assembly is simply called\n"
     " Cybersole. Querying the comma form showed the real shape immediately.\n\n"
     "The second is the more useful one. Asking for six results gives six and asking for five thousand gives five\n"
     " hundred, so there is a hard cap at five hundred that is not in ida.py -- that script passes the limit straight\n"
     " through -- which puts it in the plugin. Every string query therefore returns a sample of at most five hundred,\n"
     " never the whole inventory.\n\n"
     "That reframes the zero. My regex does match the real shape; the window simply contained five hundred short\n"
     " strings and nothing else. This is the fifth time R816's warning about full-versus-sample has applied and the\n"
     " first time it was measured rather than reasoned: one query, two limits, one plateau.\n\n"
     "So the tool now refuses instead of publishing. When the original side comes back empty it exits with a message\n"
     " saying the probe is capped, that a zero here means the sample missed rather than the image being empty, and\n"
     " that the query should be sharded by prefix before anything is published. Same family as the rows-equal-zero\n"
     " guard on the vendor table, with the addition that this one names the next step.\n\n"
     "That next step is sharding: twenty-six first letters at five hundred each covers thirteen thousand strings,\n"
     " enough for the real size of the Cybersole prefix.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, 648 replica types across 53 namespaces,\n"
     " original types unknown, a cap of 500 that a request for 5000 does not raise, and one tool refusing to publish\n"
     " a zero it cannot distinguish from a miss.\n\n"
     "Unknown: the original's business type count, pending the sharded query.\n\n"
     "The lesson is that a zero has a third source -- neither an empty set nor a wrong axis, but a window too narrow --\n"
     " and that scanning the limit is what tells the three apart."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
