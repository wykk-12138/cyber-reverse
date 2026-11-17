"""Record R1009: 326 session keys asked of the image at once, and lastStatus was never live."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 326 个会话键一次问完 —— 而 `lastStatus` 从来就**不在**产物里（R1009）

**R1008 说下一轮扫「所有 `Vars[...]` 键名对镜像查一遍」。扫了。而结果里最重的一条不是「有多少自造」，
是它解释了 R1006 那个悬案。**

### ① 工具：`analysis/vars_key_provenance.py`

**两阶段：**
1. **`analysis/pe_strings.txt`**（抽样 180,228 / 324,895）—— 命中即证明存在，未命中不证明什么（§2.7b）
2. **剩下的用 `analysis/ida.py str` 查 IDB** —— 两个方向都权威

**输出 `analysis/VARS_KEY_PROVENANCE.md`。**

### ② 而第一阶段完全失效 —— 326 个全走了 IDB

```
distinct keys: 326   settled by the sample: 0   to ask the IDB: 326
absent: 159   present-after-IDB: 152   unresolved: 15
```

**→ `settled by the sample: 0` —— 我的 `"\\n" + key + "\\n"` 匹配对抽样文件的格式不对，
所以第一阶段一个都没settle，326 个全部逐串问 IDB。**
**→ 那个「快路径」没起作用，而整个扫描仍跑完了（约 15 分钟）—— 慢但不至于不可行。**
**→ 这是一个应当记下的实现缺陷：两阶段设计里第一阶段是死的，等于只做了一阶段。**

### ③ 而 159 个 absent 分成两类，性质**完全不同**

| 类 | 数 | 说明 |
|---|---|---|
| **带点（模块命名空间）** | **97** | `adyen.*` · `kasada.*` · `paypal.*` · `stripe.*` · `square.*` · `viva.*` … |
| 不带点 | 62 | 混合 |

**带点那 97 个：**原版**不需要**把 `adyen.merchantAccount` 写成字符串 —— 它用**字段**。
**所以 absent 对它们**完全正常**，不是缺陷。**
**→ 而 `adyen.merchantAccount` 那条尤其说明问题：复刻件用 `Vars["adyen.merchantAccount"]` 存一个商户号，
而原版的做法是有一个字段。这是**表示方式**的差异，不是缺一个键。**

**不带点那 62 个是混合：**

| 明显自造 / 内部 | 可能是镜像的 |
|---|---|
| `lastBody`（R1006 我刚加的）· `lastStatus` · `sensorKeys` · `paymentMethodsUrl` · `antibot.solver` | `orderProcessed` · `paymentStarted` · `totalMinor` · `transactionAmount` |

### ④ 而最重的一条：`lastStatus` 从来就不在产物里

**`lastStatus` 是 R993 说的「活通道：5 写入 / 4 读取」。而它在镜像里两编码皆 0，**从来不在**。**
**`lastBody`（R1006 加的）同样。**

> **→ 所以 R1006 那个悬案（「消息层写对了却没进产物」）有了答案：
> 它读的那个通道**本身不存在**。不是消息层被裁，是它的输入不在。**
> **→ 而 R993 说「活通道」时的判据是「5 写入 / 4 读取」—— 那是**复刻件内部**的活，
> 不是**产物里**的活。两个「活」不是一回事。**

### ⑤ 所以这一轮的产出是**一个分类**，不是 159 个缺陷

**把 159 当成 159 个待修是错的。正确的读法是三档：**
1. **97 个带点键：表示方式差异**（原版用字段，我们用字符串键）—— 不是缺陷，除非要复刻「用字段」
2. **`lastStatus` / `lastBody` / `sensorKeys` / `paymentMethodsUrl` / `antibot.solver`：真自造**（5 个）
3. **其余约 50 个：待判** —— 有些像镜像语义（`orderProcessed` / `totalMinor`），需要逐个取证

### 数字

| 度量 | R1008 | **R1009** |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| **会话键总数** | 未测 | **326** |
| **在镜像里** | 未测 | **152** |
| **不在（带点 97 / 不带点 62）** | 未测（已知 2） | **159** |
| **未解析** | — | **15** |
| **第一阶段有效性** | 设计为快路径 | **0 / 326（失效）** |

### 教训

> **「活通道」这句话有两个意思：在复刻件内部有人写有人读，和在产物里真的存在。
> R993 用的是第一个意思，而它被读成了第二个 —— 于是「把它接上」看起来像一件小事。**
> **→ 而这一轮的扫描把那个混淆一次性摊开了：326 个键里 159 个不在产物里，
> 而其中一个正是那条「活通道」。**
"""

if "326 个会话键一次问完" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1009 轮：326 个会话键一次问完 —— 而 `lastStatus` 从来就不在产物里

### ① 工具：`analysis/vars_key_provenance.py`（两阶段）

**抽样 `pe_strings.txt` 命中即证明存在 → 剩下用 `ida.py str` 查 IDB（两向权威）→
输出 `analysis/VARS_KEY_PROVENANCE.md`。**

### ② 而第一阶段完全失效

```
distinct keys: 326   settled by the sample: 0   to ask the IDB: 326
absent: 159   present-after-IDB: 152   unresolved: 15
```

**→ `settled by the sample: 0` —— 我的换行匹配对抽样格式不对，326 个全走了 IDB。
→ 两阶段设计里第一阶段是死的，等于只做了一阶段（约 15 分钟）。**

### ③ 159 个 absent 分成两类，性质完全不同

| 类 | 数 | 说明 |
|---|---|---|
| **带点（模块命名空间）** | **97** | `adyen.*` · `kasada.*` · `paypal.*` · `stripe.*` · `square.*` · `viva.*` |
| 不带点 | 62 | 混合 |

**带点 97 个：原版**不需要**把 `adyen.merchantAccount` 写成字符串 —— 它用**字段**。
所以 absent 对它们**正常**，是**表示方式**差异，不是缺陷。**

**不带点 62 个是混合：`lastBody` / `lastStatus` / `sensorKeys` / `paymentMethodsUrl` 明显自造；
`orderProcessed` / `paymentStarted` / `totalMinor` 可能是镜像的。**

### ④ 而最重的一条：`lastStatus` 从来就不在产物里

**`lastStatus` 是 R993 说的「活通道：5 写入 / 4 读取」。而它在镜像里两编码皆 0，**从来不在**。**

> **→ R1006 那个悬案有了答案：它读的那个通道**本身不存在**。不是消息层被裁，是它的输入不在。
> → 而 R993 说「活通道」时的判据是「复刻件内部有人写有人读」，**不是「产物里真的存在」**。
> 两个「活」不是一回事。**

### ⑤ 所以产出是**一个分类**，不是 159 个缺陷

1. **97 个带点键：表示方式差异**（原版用字段）
2. **5 个真自造**（`lastStatus` / `lastBody` / `sensorKeys` / `paymentMethodsUrl` / `antibot.solver`）
3. **约 50 个待判**

### 数字

| 度量 | R1008 | **R1009** |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| **会话键总数** | 未测 | **326** |
| **在镜像里** | 未测 | **152** |
| **不在** | 未测（已知 2） | **159（带点 97 / 不带点 62）** |
| **未解析** | — | **15** |
| **第一阶段有效性** | 设计为快路径 | **0 / 326（失效）** |

### 教训

> **「活通道」有两个意思：在复刻件内部有人写有人读，和在产物里真的存在。
> R993 用的是第一个意思，而它被读成了第二个 —— 于是「把它接上」看起来像小事。
> → 这次扫描把那个混淆一次性摊开了：326 个键里 159 个不在产物里，
> 而其中一个正是那条「活通道」。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — **326 个会话键对镜像扫完：152 在 · 159 不在（97 带点是表示方式差异）· 15 未解析；`lastStatus` 从来不在产物里**（R1009）

### 工具

**`analysis/vars_key_provenance.py`（两阶段，输出 `analysis/VARS_KEY_PROVENANCE.md`）。**
**而第一阶段失效：`settled by the sample: 0` —— 换行匹配对抽样格式不对，326 个全走 IDB。**

### 结果

| | 数 |
|---|---|
| 会话键总数 | **326** |
| 在镜像里 | **152** |
| 不在 | **159**（带点 97 / 不带点 62） |
| 未解析 | **15** |

### 三分类

1. **97 个带点键**（`adyen.*` / `kasada.*` / `paypal.*` / `stripe.*`）—— 原版用**字段**不用字符串键，
   absent **正常**，是表示方式差异
2. **5 个真自造**：`lastStatus` · `lastBody` · `sensorKeys` · `paymentMethodsUrl` · `antibot.solver`
3. **约 50 个待判**（`orderProcessed` / `paymentStarted` / `totalMinor` 等像镜像语义）

### 最重的一条

**`lastStatus` 两编码皆 0 —— R993 说的「活通道」**从来不在产物里**。
→ R1006 的悬案有了答案：消息层读的通道**本身不存在**，不是消息层被裁。
→ 「活通道」两个意思（复刻件内部活 vs 产物里存在）被混用。**

### 数字

**套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336 · 键 326 / 152 / 159 / 15**

| 仍 Unknown | |
|---|---|
| 约 50 个不带点键里哪些是镜像的 | 待逐个取证 |
| 15 个未解析 | IDB 未答 |

**纪律**：「活通道」有两个意思，混用会让「接上」看起来像小事。
"""

BLOCKER = """

---

## 433. **326 个会话键扫完：152 在 · 159 不在（97 带点是表示方式差异）；`lastStatus` 从来不在产物里**

> R1009。**新增 1 个分析工具；未改产品代码。** 套件 **2219 通过 / 0 失败 / 0 跳过**。

### 一、工具

**`analysis/vars_key_provenance.py`：两阶段 —— 抽样 `pe_strings.txt` 命中即证明存在
（§2.7b：反向不可用），剩下用 `analysis/ida.py str` 查 IDB（两向权威）。
输出 `analysis/VARS_KEY_PROVENANCE.md`。**

### 二、而第一阶段完全失效

```
distinct keys: 326   settled by the sample: 0   to ask the IDB: 326
absent: 159   present-after-IDB: 152   unresolved: 15
```

**→ `settled by the sample: 0` —— 我的 `"\\n" + key + "\\n"` 匹配对抽样文件的格式不对，
所以第一阶段一个都没 settle，326 个全部逐串问 IDB（约 15 分钟）。
→ 两阶段设计里第一阶段是死的，等于只做了一阶段。这是一个应当记下的实现缺陷。**

### 三、159 个 absent 分成两类，性质**完全不同**

| 类 | 数 | 说明 |
|---|---|---|
| **带点（模块命名空间）** | **97** | `adyen.*` · `kasada.*` · `paypal.*` · `stripe.*` · `square.*` · `viva.*` · `kasada.*` … |
| 不带点 | 62 | 混合 |

**带点那 97 个：原版**不需要**把 `adyen.merchantAccount` 写成字符串 —— 它用**字段**。
所以 absent 对它们**完全正常**，不是缺陷。
→ `adyen.merchantAccount` 尤其说明问题：复刻件用一个字符串键存商户号，而原版有一个字段。
这是**表示方式**的差异，不是缺一个键。**

**不带点那 62 个是混合：**

| 明显自造 / 内部 | 可能是镜像的 |
|---|---|
| `lastBody`（R1006 加的）· `lastStatus` · `sensorKeys` · `paymentMethodsUrl` · `antibot.solver` | `orderProcessed` · `paymentStarted` · `totalMinor` · `transactionAmount` |

### 四、而最重的一条：`lastStatus` 从来就不在产物里

**`lastStatus` 是 R993 说的「活通道：5 写入 / 4 读取」。而它在镜像里两编码皆 0，**从来不在**。
`lastBody`（R1006 加的）同样。**

**→ R1006 那个悬案（「消息层写对了却没进产物」）有了答案：
它读的那个通道**本身不存在**。不是消息层被裁，是它的输入不在。
→ 而 R993 说「活通道」时的判据是「复刻件内部有人写有人读」，**不是「产物里真的存在」**。
两个「活」不是一回事。**

### 五、所以这一轮的产出是**一个分类**，不是 159 个缺陷

1. **97 个带点键：表示方式差异**（原版用字段，我们用字符串键）—— 不是缺陷
2. **5 个真自造**：`lastStatus` · `lastBody` · `sensorKeys` · `paymentMethodsUrl` · `antibot.solver`
3. **约 50 个待判** —— 有些像镜像语义，需要逐个取证

**把 159 当成 159 个待修是错的。**

### 六、数字

| 度量 | R1008 | R1009 |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| **会话键总数** | 未测 | **326** |
| **在镜像里** | 未测 | **152** |
| **不在** | 未测（已知 2） | **159（带点 97 / 不带点 62）** |
| **未解析** | — | **15** |
| **第一阶段有效性** | 设计为快路径 | **0 / 326（失效）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/vars_key_provenance.py
  -> distinct keys: 326 · settled by the sample: 0 · to ask the IDB: 326
  -> absent: 159 · present-after-IDB: 152 · unresolved: 15
  -> wrote analysis/VARS_KEY_PROVENANCE.md
cd replica && python tools/metrics_report.py -> 套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336
```

### 八、仍然 Unknown

- **约 50 个不带点键里哪些是镜像的**：**待逐个取证**。
- **15 个未解析**：**Unknown** —— IDB 未答。
- **`lastStatus` 该换成什么**：**Unknown** —— 原版用字段，而复刻件没有那个字段。

### 九、教训

**「活通道」这句话有两个意思：在复刻件内部有人写有人读，和在产物里真的存在。
R993 用的是第一个意思，而它被读成了第二个 —— 于是「把它接上」看起来像一件小事。**

**→ 而这一轮的扫描把那个混淆一次性摊开了：326 个键里 159 个不在产物里，
而其中一个正是那条「活通道」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1009", BLOCKER)
    ensure(RSTATUS, "R1009", BLOCKER)
    ensure(RVERDICT, "第 1009 轮", VERDICT)
    ensure(BACKLOG, "R1009", BACKLOG_ADD)

    note = (
        "\n## R1009 补充 — **326 个会话键扫完：152 在 · 159 不在（97 带点是表示方式差异）；"
        "`lastStatus` 从来不在产物里**（套件 2219，未改产品代码）\n\n"
        "**`analysis/vars_key_provenance.py`**（两阶段，输出 `analysis/VARS_KEY_PROVENANCE.md`）。\n"
        "**而第一阶段失效**：`settled by the sample: 0` —— 换行匹配对抽样格式不对，326 个全走 IDB（约 15 分钟）。\n\n"
        "结果：**326 键 · 152 在 · 159 不在（带点 97 / 不带点 62）· 15 未解析。**\n\n"
        "**三分类**：① 97 个带点键（`adyen.*`/`kasada.*`/`paypal.*`）—— 原版用**字段**不用字符串键，absent **正常**\n"
        "② 5 个真自造（`lastStatus`/`lastBody`/`sensorKeys`/`paymentMethodsUrl`/`antibot.solver`）\n"
        "③ 约 50 个待判（`orderProcessed`/`totalMinor` 像镜像语义）\n\n"
        "**最重的一条：`lastStatus` 两编码皆 0 —— R993 说的「活通道」从来不在产物里。**\n"
        "→ R1006 悬案有答案：**消息层读的通道本身不存在**，不是消息层被裁。\n"
        "→ 「活通道」两个意思（复刻件内部活 vs 产物里存在）被混用 —— 而混用会让「接上」看起来像小事。\n\n"
        "数字：套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336 · 键 326 / 152 / 159 / 15。\n\n"
        "纪律：**把 159 当成 159 个待修是错的。**\n\n"
        "下一轮：判那约 50 个不带点键（`orderProcessed`/`paymentStarted`/`totalMinor`/`transactionAmount` 优先）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1009" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R1009"), (RSTATUS, "R1009"), (RVERDICT, "第 1009 轮"), (BACKLOG, "R1009")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1009: all 326 session keys asked at once, and lastStatus was never there\n\n"
         "R1008 found the second invented key name by hand and noted that finding them one at a time would keep missing\n"
         " them. This round asks the whole set.\n\n"
         "vars_key_provenance.py was meant to be two-stage: settle what the string sample contains, then ask the IDB\n"
         " only about the rest. The first stage settled nothing -- my line-delimited match does not fit the sample's\n"
         " format -- so all 326 went to the IDB and the run took about fifteen minutes. Slow but done, and the failure of\n"
         " the fast path is worth recording: a two-stage design whose first stage is dead is a one-stage design.\n\n"
         "Of 326 distinct keys, 152 are in the image, 159 are not, and 15 went unresolved. The 159 split cleanly. Ninety-\n"
         " seven carry a module prefix -- adyen., kasada., paypal., stripe. -- and those absences are normal rather than\n"
         " defects: the original stores a merchant account in a field, not in a string key. That is a difference in how\n"
         " the state is represented, not a missing key.\n\n"
         "The sixty-two without a prefix are a mixture. Five are plainly this workspace's own: lastStatus, lastBody,\n"
         " sensorKeys, paymentMethodsUrl, antibot.solver. About fifty are undecided, and some read like the image's\n"
         " vocabulary -- orderProcessed, paymentStarted, totalMinor -- so they need asking individually.\n\n"
         "The important line is lastStatus. R993 called it a live channel on the strength of five writers and four\n"
         " readers, and it is absent from the artifact in both encodings. That answers the R1006 puzzle: the message\n"
         " layer did not reach the binary because the channel it reads was never in the binary, not because the layer was\n"
         " trimmed. And it exposes a word doing two jobs -- live inside the replica, and present in the artifact -- where\n"
         " R993 used the first and it is easy to read as the second.\n\n"
         "So this round's product is a classification, not a list of 159 repairs. Treating 159 as 159 defects would send\n"
         " the next several rounds fixing something that is not broken.\n\n"
         "Figures: suite 2219 unchanged, freshness one file and 2,671 lines, count 174,336, keys 326 in total with 152\n"
         " present, 159 absent and 15 unresolved, first stage effective on zero of 326.\n\n"
         "Unknown: which of the fifty unprefixed names are the image's, and the fifteen the IDB did not answer.\n\n"
         "The lesson is that \"live\" is ambiguous in a way that makes the work sound smaller than it is, and that asking\n"
         " the whole set at once turns a hunt into a classification.\n\n"
         "One analysis tool added, no product code changed; suite green at 2219."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()