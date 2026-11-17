"""Record R983: HandleBlock's identity is narrowed by four state-machine runs, one of which is a control."""

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
### `HandleBlock` 不是通用管线 —— 四个状态机串里只有一个类型带它（R983）

**回到核心。`HandleBlock` 是 HANDOFF 未结案项 #4，写着「与优先级 ② 直接相关」。这一轮把它定位到了具体形状。**

### ① 先确认它在两侧的状态

```
复刻件 where_is HandleBlock  ->  implementation 组 0 条（只有 docs 里出现过）
原版 ida.py str HandleBlock  ->  2 条命中
```

**两条命中里第一条就是决定性的：**

```
0x143454a52   "<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55"
0x143454ccf   "HandleBlockg"
```

**`<X>d__NN` 是 async 方法的状态机类型名。所以 `HandleBlock` 是**一个 async 方法**，
而它与 `SetRequest`（d__53）、`HandleResponse`（d__55）**编号相邻** —— 同一个类型里的三个相邻方法。**

### ② 而相邻不等于同管线 —— 有校准项

**把 `analysis/flows.txt`（UTF-16LE 的状态机名转储）里的四组串排出来：**

| 状态机串 | SetRequest | HandleBlock | HandleResponse |
|---|---|---|---|
| `<SetRequest>d__53 $ <HandleBlock>d__54 * <HandleResponse>d__55` | ✓ | **✓** | ✓ |
| `<Generate>d__26 " <SetRequest>d__27 * <HandleResponse>d__28` | ✓ | **✗** | ✓ |
| `* <HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48` | ✗ | ✗ | ✓ |
| `* <HandleResponse>d…`（截断，第 4 处） | ? | ✗ | ✓ |

**计数：`HandleResponse` 4 处 · `SetRequest` 2 处 · `HandleBlock` **1** 处。**

> **决定性：四个类型都有 `HandleResponse`，两个有 `SetRequest`，而只有一个有 `HandleBlock`。**
> **所以它不是请求/响应这一对的必然伴生 —— 第 2 组两兄弟都在、它不在，那是**校准项**。**
> **而 `analysis/flows.txt` 的老注释早就写着「相邻 ≠ 执行管线」，这一轮给出了它的**证据**。**

### ③ 顺序而**不是**位置

**在有它的那一组里，顺序是 `SetRequest` → `HandleBlock` → `HandleResponse`。**

> **Inference（中高）：`HandleBlock` 读的是**还没被正常解析的响应**，
> 所以它排在 `HandleResponse` 之前、`SetRequest` 之后。**
> **Observation 是三个方法的**相对编号**；「它读原始响应」是**推断**，没有代码支持 ——
> R827/R828 已确认它的字符串没有 xref，走 MethodTable 也没走通。**

### ④ 而复刻件那一侧的形状

**`where_is` 的结果说明兄弟都在、只缺这一个：**

| 名字 | 复刻件位置 |
|---|---|
| `SetRequest` | `src/Cybersole.Stores/Actions/StepAction.cs` |
| `HandleResponse` | `src/Cybersole.Http/BouncyHttpClient.cs`（3 处） |
| **`HandleBlock`** | **零** |
| `Blocked` | **30 处**，散在 `StoreFlow.cs`(11) · `HbxFlow.cs`(6) · 其余各 flow |

> **所以判断封锁的逻辑**已经在**，只是**分散在每个 flow 里**，而原版有一处集中的 `HandleBlock`。**
> **那不是「能力缺失」，是「形状不同」—— 而形状不同会不会导致行为不同，取决于那 30 处是否一致。
> 这一点我没有核过，标 Unknown。**

### ⑤ 这一轮**修正了** HANDOFF 里的一条判断

**HANDOFF 写「`HandleBlock` 与优先级 ② 直接相关」。而证据说的是更窄的一件事：
它是**某一个**类型的私有步骤，不是全局风控入口。**
**第 2 组两个兄弟都在而没有它 —— 如果它是通用管线，那一组也该有。**

### 数字

| 度量 | R982 | **R983** |
|---|---|---|
| 套件 | 2200 | **2200（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **变异 36/36** | 是 | **是**（未改代码，记录仍有效） |
| **`HandleBlock` 在原版的类型数** | 未测 | **1 / 4** |

### 教训

> **「相邻」这件事，我这一轮第一次给它配了**校准项** ——
> 第 2 组就是那个「两兄弟都在、它不在」的对照。**
> **没有那个对照，「`HandleBlock` 与 `SetRequest`/`HandleResponse` 相邻」会被读成
> 「它是这对兄弟的伴生」，而错的方向会一直带到实现里。**
"""

if "`HandleBlock` 不是通用管线" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 983 轮：`HandleBlock` 不是通用管线 —— 四个状态机串里只有一个类型带它

### ① 两侧状态

**复刻件 `where_is HandleBlock` → implementation 组 **0** 条。
原版 `ida.py str HandleBlock` → 2 条，第一条决定性：**

```
0x143454a52  "<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55"
0x143454ccf  "HandleBlockg"
```

**`<X>d__NN` 是 async 状态机类型名 → `HandleBlock` 是**一个 async 方法**，
与 `SetRequest`(d__53)、`HandleResponse`(d__55) **编号相邻** → 同一类型里三个相邻方法。**

### ② 而相邻不等于同管线 —— 有校准项

| 状态机串 | SetRequest | HandleBlock | HandleResponse |
|---|---|---|---|
| `<SetRequest>d__53 $ <HandleBlock>d__54 * <HandleResponse>d__55` | ✓ | **✓** | ✓ |
| `<Generate>d__26 " <SetRequest>d__27 * <HandleResponse>d__28` | ✓ | **✗** | ✓ |
| `* <HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48` | ✗ | ✗ | ✓ |

**计数：`HandleResponse` 4 · `SetRequest` 2 · `HandleBlock` **1**。**

> **四个类型都有 HandleResponse，两个有 SetRequest，只有一个有 HandleBlock。
> 第 2 组两兄弟都在、它不在 —— 那是**校准项**，证明它不是这对兄弟的必然伴生。**
> **`flows.txt` 的老注释早写着「相邻 ≠ 执行管线」，这一轮给了它**证据**。**

### ③ 顺序而不是位置

**有它的那组顺序是 `SetRequest` → `HandleBlock` → `HandleResponse`。**

> **Inference（中高）：它读的是**还没被正常解析的响应**，所以排在 HandleResponse 之前。
> Observation 只是三个方法的相对编号；「读原始响应」是推断，无代码支持 ——
> R827/R828 已确认它的字符串没有 xref，走 MethodTable 也没走通。**

### ④ 复刻件那一侧

| 名字 | 位置 |
|---|---|
| `SetRequest` | `StepAction.cs` |
| `HandleResponse` | `BouncyHttpClient.cs`（3 处） |
| **`HandleBlock`** | **零** |
| `Blocked` | **30 处**，`StoreFlow.cs`(11) · `HbxFlow.cs`(6) · 其余各 flow |

> **封锁判断**已经在**，只是**分散在每个 flow 里**，而原版有一处集中的 `HandleBlock`。
> **那不是「能力缺失」，是「形状不同」—— 而形状不同会不会导致行为不同，取决于那 30 处是否一致。未核过，标 Unknown。**

### ⑤ 修正 HANDOFF 的一条判断

**HANDOFF：「`HandleBlock` 与优先级 ② 直接相关」。证据说的是更窄的事：
它是**某一个**类型的私有步骤，不是全局风控入口 —— 如果它是通用管线，第 2 组也该有。**

### 数字

| 度量 | R982 | **R983** |
|---|---|---|
| 套件 | 2200 | **2200（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是**（记录仍有效） |
| **`HandleBlock` 的原版类型数** | 未测 | **1 / 4** |

### 教训

> **「相邻」第一次配了**校准项**：第 2 组就是「两兄弟都在、它不在」的对照。
> 没有那个对照，「相邻」会被读成「伴生」，而错的方向会一直带到实现里。**
"""

BACKLOG_ADD = """

## 判据 (f)/优先级 ② — **`HandleBlock` 只在一个类型里（1/4）；复刻件零；封锁判断分散在 30 处**（R983）

### Observation

**原版 `ida.py str HandleBlock` → 2 条，第一条
`"<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55` → async 状态机，与两个兄弟编号相邻。**

**`analysis/flows.txt` 四组状态机串计数：`HandleResponse` 4 · `SetRequest` 2 · `HandleBlock` **1**。**

| 组 | SetRequest | HandleBlock | HandleResponse |
|---|---|---|---|
| d__53/54/55 | ✓ | **✓** | ✓ |
| d__26/27/28 | ✓ | **✗** | ✓ |
| Kasada d__46/47/48 | ✗ | ✗ | ✓ |

**→ 第 2 组是校准项：两兄弟都在、它不在 → 它不是这对兄弟的必然伴生。**

### 复刻件

| 名字 | 位置 |
|---|---|
| `SetRequest` | `StepAction.cs` |
| `HandleResponse` | `BouncyHttpClient.cs` |
| **`HandleBlock`** | **零** |
| `Blocked` | **30 处**（`StoreFlow.cs` 11 · `HbxFlow.cs` 6 · 其余各 flow） |

**→ 能力在，形状不同（分散 vs 集中）。**

### Inference（中高，未证）

**顺序 `SetRequest → HandleBlock → HandleResponse` 暗示它读**未解析的响应**。无代码支持。**

### 数字

**套件 2200（未改代码）· 陈旧度 0/0 · 函数数 173,952 · HandleBlock 原版类型数 1/4**

| 仍 Unknown | |
|---|---|
| `HandleBlock` 的实现与调用点 | 字符串无 xref；MethodTable 路线未通 |
| 30 处分判断是否彼此一致 | 未核 —— **这是「形状不同会不会导致行为不同」的关键** |

**纪律**：「相邻」要有校准项，否则会被读成「伴生」。
"""

BLOCKER = """

---

## 407. **`HandleBlock` 只在一个类型里（1/4）；复刻件零；封锁判断分散在 30 处**

> R983。**只取证，未改代码。** 套件 **2200（R982 的记录仍有效）**。

### 一、两侧状态

**复刻件 `where_is HandleBlock` → implementation 组 **0** 条。
原版 `ida.py str HandleBlock` → 2 条：**

```
0x143454a52   "<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55"
0x143454ccf   "HandleBlockg"
```

**`<X>d__NN` 是 async 状态机类型名 → `HandleBlock` 是一个 async 方法，
与 `SetRequest`(d__53)、`HandleResponse`(d__55) 编号相邻。**

### 二、而相邻不等于同管线 —— 有校准项

| 状态机串 | SetRequest | HandleBlock | HandleResponse |
|---|---|---|---|
| `<SetRequest>d__53 $ <HandleBlock>d__54 * <HandleResponse>d__55` | ✓ | **✓** | ✓ |
| `<Generate>d__26 " <SetRequest>d__27 * <HandleResponse>d__28` | ✓ | **✗** | ✓ |
| `* <HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48` | ✗ | ✗ | ✓ |
| `* <HandleResponse>d…`（第 4 处，截断） | ? | ✗ | ✓ |

**计数：`HandleResponse` 4 · `SetRequest` 2 · `HandleBlock` **1**。**

**→ 四个类型都有 `HandleResponse`，两个有 `SetRequest`，只有一个有 `HandleBlock`。
第 2 组两兄弟都在、它不在 —— **校准项**，证明它不是这对兄弟的必然伴生。**

**→ `analysis/flows.txt` 的老注释写着「相邻 ≠ 执行管线」，这一轮给出了证据。**

### 三、顺序（Inference 中高）

**有它的那组顺序是 `SetRequest` → `HandleBlock` → `HandleResponse`。**

**→ 推断它读的是**还没被正常解析的响应**。
**Observation 只是三个方法的相对编号；「读原始响应」是推断，无代码支持**
（R827/R828 已确认其字符串无 xref，MethodTable 路线未通）。**

### 四、复刻件那一侧

| 名字 | 位置 |
|---|---|
| `SetRequest` | `src/Cybersole.Stores/Actions/StepAction.cs` |
| `HandleResponse` | `src/Cybersole.Http/BouncyHttpClient.cs`（3 处） |
| **`HandleBlock`** | **零** |
| `Blocked` | **30 处**：`StoreFlow.cs` 11 · `HbxFlow.cs` 6 · 其余各 flow |

**→ 封锁判断的能力在，只是**分散**，而原版有一处集中的 `HandleBlock`。
→ 那不是「能力缺失」，是「形状不同」。而形状不同会不会导致行为不同，
取决于那 30 处是否彼此一致 —— **未核过，Unknown。****

### 五、修正 HANDOFF 的一条判断

**HANDOFF 写「`HandleBlock` 与优先级 ② 直接相关」。证据说的是更窄的事：
它是**某一个**类型的私有步骤，不是全局风控入口。
第 2 组两个兄弟都在而没有它 —— 如果它是通用管线，那一组也该有。**

### 六、数字

| 度量 | R982 | R983 |
|---|---|---|
| 套件 | 2200 | **2200（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是**（记录仍有效） |
| **`HandleBlock` 的原版类型数** | 未测 | **1 / 4** |

### 七、验证

```
cd D:\\projects\\cyber-reverse\\replica
python tools/where_is.py HandleBlock          -> implementation 组 0 条
cd ..
python analysis/ida.py str HandleBlock        -> 2 条，含 <SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55
python -c "读 analysis/flows.txt 按 utf-16-le 解码，数 HandleBlock/HandleResponse/SetRequest"
  -> 1 / 4 / 2
```

### 八、仍然 Unknown

- **`HandleBlock` 的实现与调用点**：**Unknown** —— 字符串无 xref；MethodTable 路线未通。
- **那 30 处分判断是否彼此一致**：**Unknown** —— **这是「形状不同会不会导致行为不同」的关键**，下一轮该核。

### 九、教训

**「相邻」这件事第一次配了校准项：第 2 组就是「两兄弟都在、它不在」的对照。**

**没有那个对照，「相邻」会被读成「伴生」，而错的方向会一直带到实现里。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R983", BLOCKER)
    ensure(RSTATUS, "R983", BLOCKER)
    ensure(RVERDICT, "第 983 轮", VERDICT)
    ensure(BACKLOG, "R983", BACKLOG_ADD)

    note = (
        "\n## R983 补充 — **`HandleBlock` 只在一个类型里（1/4）；复刻件零；封锁判断分散 30 处**（套件 2200）\n\n"
        "原版 `ida.py str HandleBlock` 第一条：`\"<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55`\n"
        "→ async 状态机，与两个兄弟编号相邻。\n\n"
        "而 `analysis/flows.txt`（按 utf-16-le 解码）四组计数：**HandleResponse 4 · SetRequest 2 · HandleBlock 1**。\n"
        "| 组 | SetRequest | HandleBlock |\n|---|---|---|\n"
        "| d__53/54/55 | ✓ | **✓** |\n| d__26/27/28 | ✓ | **✗** |\n| Kasada d__46/47/48 | ✗ | ✗ |\n\n"
        "→ **第 2 组是校准项：两兄弟都在、它不在 → 它不是这对兄弟的必然伴生。**\n\n"
        "复刻件：`SetRequest` 在 `StepAction.cs`、`HandleResponse` 在 `BouncyHttpClient.cs`、**`HandleBlock` 零**，\n"
        "而 `Blocked` 出现 **30 次**（`StoreFlow.cs` 11 · `HbxFlow.cs` 6 · 其余各 flow）。\n"
        "→ 能力在，**形状不同（分散 vs 集中）**。而形状不同会不会导致行为不同，取决于 30 处是否一致 —— **未核，Unknown**。\n\n"
        "→ 顺带修正 HANDOFF：「与优先级 ② 直接相关」应改为更窄的「某一个类型的私有步骤」。\n\n"
        "数字：套件 2200（未改代码）· 陈旧度 0/0 · 函数数 173,952 · HandleBlock 原版类型数 1/4。\n\n"
        "纪律：**「相邻」要有校准项，否则会被读成「伴生」。**\n\n"
        "下一轮：核那 30 处封锁判断是否彼此一致 —— 那是「形状不同会不会导致行为不同」的关键。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R983" not in h:
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
             for p, k in ((RBLOCK, "R983"), (RSTATUS, "R983"), (RVERDICT, "第 983 轮"), (BACKLOG, "R983")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R983: HandleBlock belongs to one type, not to the request pipeline\n\n"
         "Back to the core. HandleBlock was the fourth open item, recorded as directly relevant to the anti-bot priority, and\n"
         " this round narrowed it to a specific shape.\n\n"
         "On the replica side where_is finds no implementation anywhere. On the original side the name appears twice, and the\n"
         " first hit is the decisive one: a state-machine type name string reading SetRequest d__53, HandleBlock d__54,\n"
         " HandleResponse d__55. So HandleBlock is one async method, numbered adjacent to two siblings in the same type.\n\n"
         "Adjacency is not pipeline membership, and the calibration was already sitting in the dump. Decoding analysis/flows.txt\n"
         " as UTF-16 gives four such runs: HandleResponse appears in four types, SetRequest in two, and HandleBlock in one. The\n"
         " second run has both siblings and lacks HandleBlock, which is what turns \"adjacent\" into \"adjacent in one type\n"
         " only\". The file's own old comment said adjacency is not an execution order; this round gave that comment its\n"
         " evidence.\n\n"
         "The order in the one run that has it is SetRequest, then HandleBlock, then HandleResponse, which suggests it reads a\n"
         " response before normal parsing. That is inference and is marked as such: the string has no xrefs and the MethodTable\n"
         " route did not work in R827 and R828.\n\n"
         "On the replica side both siblings exist under other names, SetRequest in StepAction and HandleResponse in\n"
         " BouncyHttpClient, while Blocked appears thirty times scattered across the flows with none in a central handler. So\n"
         " the capability is present and the shape differs, and whether the shape difference changes behaviour depends on\n"
         " whether those thirty checks agree with each other. That has not been examined and stays Unknown.\n\n"
         "It also corrects the handoff: HandleBlock is one type's private step, not a global anti-bot entry point. Had it been\n"
         " universal plumbing, the second run would have had it too.\n\n"
         "Figures: suite 2200 unchanged, freshness zero, count 173,952, HandleBlock present in one of four request-lifecycle\n"
         " types.\n\n"
         "Unknown: HandleBlock's implementation and call sites, and whether the replica's thirty scattered block checks agree.\n\n"
         "The lesson is that adjacency needs a calibration case, and this round had one by luck of the dump being complete. The\n"
         " wrong reading -- that HandleBlock accompanies those siblings -- would have gone straight into an implementation.\n\n"
         "No product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()