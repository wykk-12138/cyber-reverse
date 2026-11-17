"""Record R1005: the 409 dilemma dissolves because the original classifies by message, not status code."""

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
### 409 的两难消失了 —— 因为原版**不按状态码分类**（R1005）

**R993 留下一句「两份表哪一份对，需要证据」。这一轮取了证据，而它把那个二选一**取消了**。**

### ① 先按 goal 的流程把 IDA 弄起来（三个框，一个新框型）

```
PROXY: MISSING   INSTANCE: none   PORT 13337: REFUSED   TIMEOUT: 180s
```

**代理仍然缺失（属停下等 YG 的条件），而 **IDA 自己起来了**、只是停在对话框上。
`analysis/ida.py` 直连插件的 13337，不走 DSH 代理，所以清框即可用。**

| 框 | 处置 |
|---|---|
| 「IDA has found an unpacked version」 | **Proceed with unpacked base**（goal 指定） |
| 「id0 is not closed. repair it?」 | **是(Y)**（goal 指定） |
| 「请稍候…」 | **等，不点**（goal 指定） |
| **「Database still contains inconsistencies」** | **确定** —— **新框型，本轮补记**；只有这一个按钮，信息性 |

**→ `13337 LISTENING pid=44936`，标题 `IDA - Cybersole.exe.i64`。**

### ② 409 的状态码语义：镜像**不提供**

| 探测 | 命中 | 是什么 |
|---|---|---|
| `409` | 40 | 全是十六进制哈希（`1409A77B…`），**无状态码语义** |
| `Conflict` | 30 | `.NET` 枚举名（`Conflicte` / `DeprecatedLegacyJsonFieldConflicts`） |
| `unavailable` | 40 | HTTP 枚举名（`ServiceUnavailable` / `UnavailableForLegalReasons`） |

> **→ 镜像里没有「409 → 某种处置」的对照表。有的只是 HTTP 枚举的**名字**。
> → 所以 R993 那个问题（「哪份表对」）在原版的**状态码层**上无解 —— 那里没有表。**

### ③ 而原版在**消息层**给了答案

```
0x146e2c6cc  Out of stock (reservation failed), retrying
0x146e6ab6c  Reservation failed (
0x146dd0644  Item is Out of Stock
0x146e2c68c  Out of stock (decoy)
0x146edb584  The product in the cart is out of stock.
```

**`out of stock` 共 7 条，而它们**不是同一件事**：**

| 消息 | 处置 |
|---|---|
| `Out of stock (reservation failed), **retrying**` | **重试** |
| `Out of stock (decoy)` | **诱饵** —— 不是真缺货（另有 `get_DecoyActive` 状态） |
| `Item is Out of Stock` · `This item is out of stock` | 真缺货 |

> **→ 所以「缺货要不要重试」的判据是**消息内容**，不是状态码。
> → 而两份表（`ClassifyCheckoutFailure` 409=Declined · `HandleResponseAsync` 409=retryable）
> **同错**：都在按状态码分类，而原版按**消息**分类。**

### ④ 所以修法不是「选哪一份」，是**加一层**

**两难的形状是「A 说甲、B 说乙，哪个对」。而证据说：问题问错了层次。
409 的状态码层没有语义；语义在响应体里。**

**正确的修法：**
1. 状态码层保持**保守**（409 → Declined，因为多数 409 是售罄）
2. **加一条消息级升级**：体里含 `reservation failed` → **可重试**
3. 体里含 `decoy` → **不重试**（诱饵，重试会加深可疑）

**→ 而这三条各自有字符串证据，不是偏好。**

### ⑤ 本轮未改代码，因为接线前要先定这条顺序

**`HandleResponseAsync` 仍未接上 —— 而接它之前必须先有消息层，
否则 409 会一律变可重试（= 重试已经卖出的东西）。**

**→ 那正是 R993 说的「必须先对齐再接线」。而这一轮把「对齐什么」问清楚了：
不是两份表对齐，是**加一层它们都没有的东西**。**

### 数字

| 度量 | R1004 | **R1005** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **409 状态码语义在镜像** | 未测 | **无（40 条全是哈希/枚举名）** |
| **缺货消息分类** | 未测 | **3 类（真缺货 / reservation failed→重试 / decoy→不重试）** |
| IDA 框型 | 3 种 | **4 种（+「仍含不一致」→确定）** |

### 教训

> **「A 和 B 矛盾，哪个对」这个问法本身可能错 —— 也许两个都在错的层次上回答。
> → R993 把问题设成二选一，而镜像的证据说：状态码层没有语义。
> → 而**取证的第一个用途不是选边，是检查那个二选一是否成立**。**
"""

if "409 的两难消失了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1005 轮：409 的两难消失了 —— 因为原版**不按状态码分类**

### ① 先把 IDA 弄起来（三个 goal 指定的框 + 一个新框型）

**doctor 报 `PROXY: MISSING` / `INSTANCE: none` / `PORT REFUSED` —— 而 IDA 其实起来了、停在对话框上。
`analysis/ida.py` 直连 13337，不走 DSH 代理，所以清框即可用。**

| 框 | 处置 |
|---|---|
| 「IDA has found an unpacked version」 | **Proceed with unpacked base** |
| 「id0 is not closed. repair it?」 | **是(Y)** |
| 「请稍候…」 | **等，不点** |
| **「Database still contains inconsistencies」** | **确定** —— **新框型，本轮补记** |

**→ `13337 LISTENING pid=44936`。**

### ② 409 的状态码语义：镜像**不提供**

| 探测 | 命中 | 是什么 |
|---|---|---|
| `409` | 40 | 全是十六进制哈希，**无状态码语义** |
| `Conflict` | 30 | `.NET` 枚举名 |
| `unavailable` | 40 | HTTP 枚举名（`ServiceUnavailable`） |

> **→ 没有「409 → 处置」的对照表。所以 R993 那个问题在原版的状态码层上**无解**。**

### ③ 而原版在**消息层**给了答案

| 消息 | 处置 |
|---|---|
| `Out of stock (reservation failed), **retrying**` | **重试** |
| `Out of stock (decoy)` | **诱饵**（另有 `get_DecoyActive` 状态） |
| `Item is Out of Stock` · `This item is out of stock` | 真缺货 |

> **→ 「缺货要不要重试」的判据是**消息内容**，不是状态码。
> → 两份表（409=Declined / 409=retryable）**同错**：都在按状态码分类。**
> **→ 而 `decoy` 那条更重要：诱饵**不能**重试 —— 重试会加深可疑。**

### ④ 修法不是选一份，是**加一层**

1. 状态码层保持**保守**（409 → Declined，多数 409 是售罄）
2. **消息级升级**：体含 `reservation failed` → **可重试**
3. 体含 `decoy` → **不重试**

**三条各有字符串证据，不是偏好。**

### ⑤ 本轮未改代码的理由

**接 `HandleResponseAsync` 之前必须先有消息层，否则 409 一律变可重试（= 重试已卖出的东西）。
R993 说「必须先对齐再接线」，这一轮把「对齐什么」问清楚了：
不是两份表对齐，是**加一层它们都没有的东西**。**

### 数字

| 度量 | R1004 | **R1005** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| **409 状态码语义在镜像** | 未测 | **无** |
| **缺货消息分类** | 未测 | **3 类** |
| **IDA 框型** | 3 | **4（+「仍含不一致」）** |

### 教训

> **「A 和 B 矛盾，哪个对」这个问法本身可能错 —— 也许两个都在错的层次上回答。
> → R993 把问题设成二选一，而镜像的证据说：状态码层没有语义。
> → **取证的第一个用途不是选边，是检查那个二选一是否成立。****
"""

BACKLOG_ADD = """

## 判据 (a)/优先级 ① — **409 两难取消：镜像无状态码语义；缺货按消息分 3 类（reservation failed→重试 · decoy→不重试）**（R1005）

### IDA 就绪（goal 流程）

**doctor 报 PROXY MISSING 但 IDA 起来了 ⇒ 清 3 个 goal 指定框 + **1 个新框型**
（「Database still contains inconsistencies」→ 确定）⇒ `13337 LISTENING`。
**`ida.py` 直连 13337，不依赖 DSH 代理。**

### 证据

| 探测 | 命中 | 是什么 |
|---|---|---|
| `409` | 40 | 全是哈希，无状态码语义 |
| `Conflict` | 30 | .NET 枚举名 |
| `unavailable` | 40 | HTTP 枚举名 |
| **`reservation failed`** | **2** | `Out of stock (reservation failed), retrying` · `Reservation failed (` |
| `decoy` | 10 | `get_DecoyActive` —— 诱饵是状态 |
| `out of stock` | 7 | 真缺货 ×3 + decoy + reservation failed |

### 裁决

**两份表**同错**：`ClassifyCheckoutFailure`（409=Declined）与 `HandleResponseAsync`（409=retryable）
都在按状态码分类，而原版按**消息**分类。**

**正确修法（未做）：① 状态码层保守（409→Declined）② 消息含 `reservation failed` → 可重试
③ 消息含 `decoy` → 不重试。**

### 数字

**套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 409 语义 无 · 缺货分类 3 · IDA 框型 4**

| 仍 Unknown | |
|---|---|
| `decoy` 的判定是否还有别的信号 | 未查 |

**纪律**：取证的第一个用途不是选边，是检查那个二选一是否成立。
"""

BLOCKER = """

---

## 429. **409 两难取消：镜像无状态码语义；缺货按消息分 3 类**

> R1005。**未改代码；IDA 就绪 + 取证。** 套件 **2214 通过 / 0 失败 / 0 跳过**。

### 一、先把 IDA 弄起来（goal 指定的框 + 一个新框型）

**doctor 报：**

```
PROXY: MISSING - DSH did not spawn [python -m ida_pro_mcp]
INSTANCE: none    PORT 13337: REFUSED    TIMEOUT: no listener after 180s
```

**而 `Get-Process` 显示 `ida pid=44936 mem=263 MB title=请确认` —— IDA 起来了，停在对话框上。
`analysis/ida.py` 直连插件的 13337，不上 DSH 代理，所以清框即可用。**

| 框 | 处置 |
|---|---|
| 「IDA has found an unpacked version」 | **Proceed with unpacked base**（goal 指定） |
| 「id0 is not closed. repair it?」 | **是(Y)**（goal 指定） |
| 「请稍候…」 | **等，不点**（goal 指定） |
| **「Database still contains inconsistencies」** | **确定** —— **新框型，本轮补记**；只有一个按钮，信息性 |

**→ 清完：`13337 LISTENING pid=44936`，`ida mem=1,889 MB`，标题 `IDA - Cybersole.exe.i64`。**

### 二、409 的状态码语义：镜像**不提供**

| 探测 | 命中 | 是什么 |
|---|---|---|
| `409` | 40 | 全是十六进制哈希（`1409A77B047C…`），**无状态码语义** |
| `Conflict` | 30 | `.NET` 枚举名（`Conflicte` / `DeprecatedLegacyJsonFieldConflicts`） |
| `unavailable` | 40 | HTTP 枚举名（`ServiceUnavailable` / `UnavailableForLegalReasons` / `ListenerUnavailable`） |

**→ 镜里没有「409 → 某种处置」的对照表。有的只是 HTTP 枚举的**名字**。
→ 所以 R993 那个问题（「两份表哪一份对」）在原版的**状态码层**上无解 —— 那里没有表。**

### 三、而原版在**消息层**给了答案

```
0x146e2c6cc  Out of stock (reservation failed), retrying
0x146e6ab6c  Reservation failed (
0x146dd0644  Item is Out of Stock
0x146e2c68c  Out of stock (decoy)
0x146edb584  The product in the cart is out of stock.
0x146eed0ac  This item is out of stock
```

**`out of stock` 共 7 条，而它们**不是同一件事**：**

| 消息 | 处置 |
|---|---|
| `Out of stock (reservation failed), **retrying**` | **重试** |
| `Out of stock (decoy)` | **诱饵** —— 不是真缺货（另有 `get_DecoyActive` 状态，10 条命中） |
| `Item is Out of Stock` · `This item is out of stock` · `The product in the cart is out of stock.` | 真缺货 |

**→ 「缺货要不要重试」的判据是**消息内容**，不是状态码。
→ 两份表**同错**：`ClassifyCheckoutFailure`（409=Declined）与 `HandleResponseAsync`（409=retryable）
  都在按状态码分类，而原版按**消息**分类。**

### 四、所以修法不是「选哪一份」，是**加一层**

**两难的形状是「A 说甲、B 说乙，哪个对」。而证据说：问题问错了层次。
409 的状态码层没有语义；语义在响应体里。**

**正确修法（本轮未做）：**

1. 状态码层保持**保守**（409 → Declined，因为多数 409 是售罄）
2. **加一条消息级升级**：体里含 `reservation failed` → **可重试**
3. 体里含 `decoy` → **不重试**（诱饵，重试会加深可疑）

**三条各自有字符串证据，不是偏好。**

### 五、本轮未改代码的理由

**`HandleResponseAsync` 仍未接上 —— 而接它之前必须先有消息层，
否则 409 会一律变可重试（= 重试已经卖出的东西）。
R993 说「必须先对齐再接线」；这一轮把「对齐什么」问清楚了：
**不是两份表对齐，是加一层它们都没有的东西。****

### 六、数字

| 度量 | R1004 | R1005 |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **409 状态码语义在镜像** | 未测 | **无（40 条全是哈希/枚举名）** |
| **缺货消息分类** | 未测 | **3 类** |
| **IDA 框型** | 3 种 | **4 种（+「仍含不一致」→确定）** |

### 七、验证

```
powershell -File "D:\\projects\\vm2api\\.dsh\\scripts\\ida-mcp-doctor.ps1" -Path "D:\\projects\\cyber-reverse\\target\\Cybersole.exe.i64"
  -> PROXY: MISSING / TIMEOUT（IDA 停在框上）
CUA: list_windows(app:"ida") -> 「请确认」-> Proceed with unpacked base
     -> 「请确认」-> 是(Y)
     -> 「请稍候…」-> 等 75s
     -> 「警告」-> 确定
Get-NetTCPConnection -LocalPort 13337 -> LISTENING pid=44936
python analysis/ida.py str "reservation failed" -> {"n":2}
python analysis/ida.py str "409"              -> {"n":40}（全哈希）
python analysis/ida.py str "out of stock"     -> {"n":7}
cd replica && python tools/metrics_report.py  -> 套件 2214 · 陈旧度 0/0 · 函数数 174,336
```

### 八、仍然 Unknown

- **`decoy` 的判定是否还有别的信号**：**Unknown** —— 未查（`get_DecoyActive` 是状态属性，
  但触发它的条件未取证）。
- **DSH 的 ida 代理**：仍 `MISSING` —— 属停下等 YG（不影响 `ida.py` 直连）。

### 九、教训

**「A 和 B 矛盾，哪个对」这个问法本身可能错 —— 也许两个都在错的层次上回答。**

**→ R993 把问题设成二选一，而镜像的证据说：状态码层没有语义。
→ 而**取证的第一个用途不是选边，是检查那个二选一是否成立**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1005", BLOCKER)
    ensure(RSTATUS, "R1005", BLOCKER)
    ensure(RVERDICT, "第 1005 轮", VERDICT)
    ensure(BACKLOG, "R1005", BACKLOG_ADD)

    note = (
        "\n## R1005 补充 — **409 两难取消：镜像无状态码语义；缺货按消息分 3 类**（套件 2214，未改代码）\n\n"
        "**IDA 就绪流程**：doctor 报 PROXY MISSING / PORT REFUSED，而 IDA 其实起来了停在框上 ——\n"
        "`ida.py` 直连 13337 不走 DSH 代理。清框：unpacked→**Proceed with unpacked base** ·\n"
        "id0→**是(Y)** · 「请稍候…」→**等** · **新框型「Database still contains inconsistencies」→ 确定**（本轮补记）。\n"
        "→ `13337 LISTENING pid=44936`。\n\n"
        "**409 的状态码语义在镜像里不存在**：`409` 40 条全是十六进制哈希；`Conflict` 30 条是 .NET 枚举名；\n"
        "`unavailable` 40 条是 HTTP 枚举名。**所以 R993 的「哪份表对」在状态码层无解。**\n\n"
        "**而原版在消息层给了答案**：`Out of stock (reservation failed), retrying` · `Out of stock (decoy)` ·\n"
        "`Item is Out of Stock`。**缺货分 3 类：reservation failed→重试 · decoy→不重试（另有 `get_DecoyActive`）· 真缺货。**\n\n"
        "**裁决**：两份表同错，都在按状态码分类。修法不是选一份，是**加一层消息判断**：\n"
        "① 状态码层保守（409→Declined）② 含 `reservation failed`→可重试 ③ 含 `decoy`→不重试。\n"
        "**接 `HandleResponseAsync` 之前必须先有这一层，否则 409 一律变可重试。**\n\n"
        "数字：套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 409 语义 无 · 缺货分类 3 · IDA 框型 4。\n\n"
        "纪律：**取证的第一个用途不是选边，是检查那个二选一是否成立。**\n\n"
        "下一轮：按三条证据加消息层（`reservation failed` / `decoy` / 真缺货），再接 `HandleResponseAsync`。\n"
        "**仍停下等 YG**：DSH 的 ida 代理 MISSING（不影响 ida.py，但 mcp__ida__* 不可用）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1005" not in h:
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
             for p, k in ((RBLOCK, "R1005"), (RSTATUS, "R1005"), (RVERDICT, "第 1005 轮"), (BACKLOG, "R1005")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1005: the 409 question dissolves, because the original classifies by message\n\n"
         "R993 left two status tables disagreeing about 409 and a note saying evidence was needed before wiring\n"
         " HandleResponseAsync. This round fetched the evidence, and it removes the choice rather than settling it.\n\n"
         "Getting there meant clearing three of the dialog boxes the goal names -- the unpacked-database warning, the\n"
         " unclosed id0 -- plus a fourth that was not on the list: an informational warning that the repaired database\n"
         " still contains inconsistencies, with a single acknowledge button. The doctor reports the proxy missing and the\n"
         " port refused, but IDA had started and was sitting on those boxes, and analysis/ida.py talks to the plugin on\n"
         " 13337 directly rather than through the DSH proxy, so clearing them was enough.\n\n"
         "The status-code layer holds nothing. Searching 409 returns forty hits, every one a hexadecimal hash. Conflict\n"
         " returns thirty .NET enum names. unavailable returns forty HTTP enum names. There is no table mapping a 409 to a\n"
         " disposition anywhere in the image, so asking which of the two tables is right has no answer at that layer.\n\n"
         "The message layer answers it instead. Out of stock appears seven times and the variants are not the same thing:\n"
         " reservation failed, retrying says to retry; decoy says the shortage is bait, and there is a get_DecoyActive\n"
         " property beside it; and the plain Item is Out of Stock means what it says. So whether a shortage is worth\n"
         " retrying depends on the body, not the code.\n\n"
         "That makes both tables wrong in the same way. ClassifyCheckoutFailure says 409 is a decline and\n"
         " HandleResponseAsync says it is retryable, and each is guessing from the status code when the original reads the\n"
         " message. The fix is not to pick one but to add a layer neither has: keep the status-code layer conservative,\n"
         " promote to retryable when the body says reservation failed, and refuse to retry when it says decoy, since\n"
         " retrying bait is how a session looks worse.\n\n"
         "No code changed, because wiring HandleResponseAsync before that layer exists would turn every 409 into a retry\n"
         " against something already sold. R993 said to align before wiring; this round found out what to align -- not the\n"
         " two tables to each other, but a layer they both lack.\n\n"
         "Figures: suite 2214 unchanged, freshness zero, count 174,336, no status-code semantics in the image, three\n"
         " message classes, four dialog types now known.\n\n"
         "Unknown: whether decoy has signals beyond the message, and the DSH ida proxy, which is still missing and still\n"
         " a stop-and-ask item rather than something to work around.\n\n"
         "The lesson is that \"A and B disagree, which is right\" can be the wrong question, because both may be answering\n"
         " at a level the artifact does not use. The first purpose of fetching evidence is to test whether the choice was\n"
         " real.\n\n"
         "No product code changed; one dilemma dissolved and one new dialog type recorded."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()