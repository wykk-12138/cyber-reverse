"""Record R1044: the string pool carries no xrefs at all, so xrefs was never the instrument."""

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
### 字符串池**一条 xref 都没有** —— 而那对照出来的（R1044）

**R1043 说下一轮「搜引用那两条 URL 的 immediates」。搜了，两样都 0，而**对照**说明那不是查询失败。**

### ① 两种仪器，都是 0

| 检查 | 结果 |
|---|---|
| `xrefs_to 0x147053d8c`（`buy/checkouts/v3`） | **0** |
| `xrefs_to 0x147053c94`（`buy/checkout_previews/v3`） | **0** |
| 8 字节小端立即数 `bin_search`（`ida_bytes.bin_search`） | **0** |

**→ 第二种的 0 有原因：x64 用 `lea rip+disp32` 取址，绝对地址**从不落盘**。
→ 所以「搜立即数」这个办法**从原理上就不可能**成功 —— 而我上一轮把它写进了生成物。**

### ② 而对照给出更硬的答案

```
datadome          0x146ffe1fc   0 xrefs
queue-it          0x147147794   0 xrefs
```

**→ 两个**已知**池串也是 **0**。
→ 所以「池条目没有 xref」是**这个产物的通性**，不是那两条 Nike URL 的特别之处。
→ 而 `xrefs` 这整个仪器对 NativeAOT 的字符串池**无效** —— 不是「这两条查不到」。****

### ③ 而它解释了三次失败的查询

| 轮 | 查询 | 结果 | 当时的解读 |
|---|---|---|---|
| R1039 | `xrefs 0x146d8dfdc`（`Farfetch`） | 0 | 「NativeAOT 按 base+offset 引用」 |
| R1043 | `xrefs 0x147053d8c` | 0 | 「池条目无 xref」 |
| **R1044** | **对照：`datadome` · `queue-it`** | **0** | **「所有池条目都无 xref ⇒ 仪器无效」** |

**→ 前两次我给的解释都**接近**对，但都没有对照，所以那只是**推断**。
→ 而这一次有了对照，它变成**观察**：同一次调用里，已知的和待查的一样是 0。****

### ④ 所以正确的解法换了

**不是「搜引用」，而是：**
- 从**数据段**找指向池的 `(ptr, len)` 表（NativeAOT 的 frozen span 布局）
- 或反编译**已知**调用 Nike buy 面的函数，读它装配的字符串

**→ 而那比一次 `xrefs` 查询大得多 —— 而这一点要写明，否则下一轮会以为是个一步活。**

### ⑤ 而生成物被更正

**上一版我写的是「用 IDAPython 搜 immediates」，那**是错的**。
→ 现在那一节变成一张**不能解决**的检查表（五次查询 + 两个对照），以及**能解决**的两条路。
→ `docs/CORE_COVERAGE.md`：4,241 → **4,974 字节**。**

### ⑥ 数字

| 度量 | R1043 | **R1044** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改业务代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **那两条 URL 的 xref** | 未查 | **0 / 0** |
| **立即数搜索** | 建议用它 | **0（原理上不可能）** |
| **对照（已知池串）** | 无 | **`datadome` 0 · `queue-it` 0** |
| **池串是否有 xref** | 「这两条没有」 | **全部没有（通性）** |
| **`CORE_COVERAGE.md`** | 4,241 字节 | **4,974 字节** |
| **上一轮的错误建议** | 已写入 | **已更正** |

### 教训

> **零值需要对照才能读。** 而这一轮之前我做过三次「查不到」，每次都给了一个**听起来对**的解释。
> **→ 而那三个解释都是从一个零推出来的，没有一个是拿一个**已知非零**的东西比出来的。**
> **→ 而对照的成本是一次调用 —— 而它把「推断」变成「观察」，并且**否掉了我上一轮写下的方法**。**
"""

if "字符串池**一条 xref 都没有**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1044 轮：字符串池一条 xref 都没有 —— 而那是对照出来的

### ① 两种仪器，都是 0

| 检查 | 结果 |
|---|---|
| `xrefs_to 0x147053d8c`（`buy/checkouts/v3`） | **0** |
| `xrefs_to 0x147053c94` | **0** |
| 8 字节小端立即数 `bin_search` | **0** |

**→ 第二种的 0 有原因：x64 用 `lea rip+disp32`，绝对地址**从不落盘** ⇒「搜立即数」原理上不可能成功。
→ 而那正是我**上一轮写进生成物**的办法。**

### ② 而对照给出更硬的答案

```
datadome          0x146ffe1fc   0 xrefs
queue-it          0x147147794   0 xrefs
```

**→ 两个**已知**池串也是 0 ⇒「池条目没有 xref」是**通性**，不是那两条 URL 的特别之处。
→ `xrefs` 对 NativeAOT 字符串池**整个仪器无效**。**

### ③ 而它解释了三次失败的查询

| 轮 | 查询 | 解读 |
|---|---|---|
| R1039 | `xrefs` `Farfetch` | 「按 base+offset 引用」 |
| R1043 | `xrefs` `checkouts/v3` | 「池条目无 xref」 |
| **R1044** | **对照 `datadome`/`queue-it`** | **「所有池条目都无 xref」** |

**→ 前两次的解释都**接近**对，但没有对照 ⇒ 那只是推断；这次同一次调用里已知的也 0 ⇒ 观察。**

### ④ 所以解法换了

**不是「搜引用」，而是：从**数据段**找 `(ptr, len)` 表，或反编译**已知**调用 Nike buy 面的函数。
→ 而那比一次 `xrefs` 查询**大得多** —— 要写明，否则下一轮会以为是一步活。**

### ⑤ 而生成物被更正

**上一版「用 IDAPython 搜 immediates」**是错的**。现在那一节是**五条不能解决**的检查 + **两条能解决**的路。
→ `CORE_COVERAGE.md`：4,241 → **4,974 字节**。**

### ⑥ 数字

| 度量 | R1043 | **R1044** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **那两条 URL 的 xref** | 未查 | **0 / 0** |
| **立即数搜索** | 建议用它 | **0（原理上不可能）** |
| **对照（已知池串）** | 无 | **均 0** |
| **池串是否有 xref** | 「这两条没有」 | **全部没有** |
| **`CORE_COVERAGE.md`** | 4,241 字节 | **4,974 字节** |

### 教训

> **零值需要对照才能读。** 这轮之前我做过三次「查不到」，每次都给了一个**听起来对**的解释。
> **→ 而三个解释都是从零推出来的，没有一个是拿**已知非零**的东西比出来的。**
> **→ 对照的成本是一次调用 —— 它把推断变成观察，并**否掉了我上一轮写下的方法**。**
"""

BACKLOG_ADD = """

## 判据 (a)(f) — **字符串池无 xref（通性，有对照）；「搜 immediates」被否；生成物更正**（R1044）

### 两种仪器都 0，而对照说明原因

| 检查 | 结果 |
|---|---|
| `xrefs_to 0x147053d8c` / `0x147053c94` | **0 / 0** |
| 8 字节小端 `bin_search` | **0**（x64 `lea rip+disp` ⇒ 绝对地址不落盘） |
| **对照** `datadome` `0x146ffe1fc` | **0** |
| **对照** `queue-it` `0x147147794` | **0** |

**⇒ 「池条目无 xref」是**产物通性**；`xrefs` 对 NativeAOT 池字符串整个无效。**

### 三次查询的解释史

R1039「按 base+offset」→ R1043「池条目无 xref」→ **R1044「所有池条目都无 xref（有对照）」**。
**前两次是推断，第三次是观察。**

### 解法换了

**从**数据段**找 `(ptr,len)` 表，或反编译**已知**调用 Nike buy 面的函数 —— **比一次 `xrefs` 查询大得多**。**

### 更正

**上一轮写进生成物的「搜 immediates」已删；`CORE_COVERAGE.md` 4,241 → **4,974** 字节，
那一节现为「五条不能解决 + 两条能解决」。**

### 数字

**套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · xref 0/0 · 立即数 0 · 对照 0/0 · 表 4,974 字节**

| 仍 Unknown | |
|---|---|
| 哪个资源承接 shipping 写入 | **待读调用点，非 xref 可得** |
| Farfetch transport | 无线索 |

**纪律**：**零值需要对照才能读** —— 否则「查不到」会被一个听起来对的解释填满。
"""

BLOCKER = """

---

## 468. **字符串池一条 xref 都没有 —— 而那是对照出来的**

> R1044。**改 1 个生成器（未改业务代码）。** 套件 **2258 通过 / 0 失败 / 0 跳过**。

### 一、两种仪器，都是 0

| 检查 | 结果 |
|---|---|
| `xrefs_to 0x147053d8c`（`buy/checkouts/v3`） | **0** |
| `xrefs_to 0x147053c94`（`buy/checkout_previews/v3`） | **0** |
| 8 字节小端立即数 `ida_bytes.bin_search` | **0** |

**→ 第二种的 0 有原因：x64 用 `lea rip+disp32` 取址，绝对地址**从不落盘**。
→ 所以「搜立即数」这个办法**从原理上就不可能**成功 —— 而我上一轮把它写进了生成物。**

### 二、而对照给出更硬的答案

```
datadome          0x146ffe1fc   0 xrefs
queue-it          0x147147794   0 xrefs
```

**→ 两个**已知**池串也是 **0**。
→ 所以「池条目没有 xref」是**这个产物的通性**，不是那两条 Nike URL 的特别之处。
→ 而 `xrefs` 这整个仪器对 NativeAOT 的字符串池**无效** —— 不是「这两条查不到」。**

### 三、而它解释了三次失败的查询

| 轮 | 查询 | 结果 | 当时的解读 |
|---|---|---|---|
| R1039 | `xrefs 0x146d8dfdc`（`Farfetch`） | 0 | 「NativeAOT 按 base+offset 引用」 |
| R1043 | `xrefs 0x147053d8c` | 0 | 「池条目无 xref」 |
| **R1044** | **对照：`datadome` · `queue-it`** | **0** | **「所有池条目都无 xref ⇒ 仪器无效」** |

**→ 前两次我给的解释都**接近**对，但都没有对照，所以那只是**推断**。
→ 而这一次有了对照，它变成**观察**：同一次调用里，已知的和待查的一样是 0。**

### 四、所以正确的解法换了

**不是「搜引用」，而是：**
- 从**数据段**找指向池的 `(ptr, len)` 表（NativeAOT 的 frozen span 布局）
- 或反编译**已知**调用 Nike buy 面的函数，读它装配的字符串

**→ 而那比一次 `xrefs` 查询大得多 —— 而这一点要写明，否则下一轮会以为是个一步活。**

### 五、而生成物被更正

**上一版我写的是「用 IDAPython 搜 immediates」，那**是错的**。
→ 现在那一节变成一张**不能解决**的检查表（五次查询 + 两个对照），以及**能解决**的两条路。
→ `docs/CORE_COVERAGE.md`：4,241 → **4,974 字节**。**

### 六、数字

| 度量 | R1043 | R1044 |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改业务代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **那两条 URL 的 xref** | 未查 | **0 / 0** |
| **立即数搜索** | 建议用它 | **0（原理上不可能）** |
| **对照（已知池串）** | 无 | **`datadome` 0 · `queue-it` 0** |
| **池串是否有 xref** | 「这两条没有」 | **全部没有（通性）** |
| **`CORE_COVERAGE.md`** | 4,241 字节 | **4,974 字节** |
| **上一轮的错误建议** | 已写入 | **已更正** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py py "import idautils; print(sum(1 for _ in idautils.XrefsTo(0x146ffe1fc,0)))"  -> 0
python analysis/ida.py py "import idautils; print(sum(1 for _ in idautils.XrefsTo(0x147147794,0)))"  -> 0
cd replica
python tools/core_coverage.py  -> 4,974 字节（含五条不能解决 + 两条能解决）
python tools/metrics_report.py -> 完整套件 exit 0  2258 / 0 / 0 · 陈旧度 0 / 0
```

### 八、仍然 Unknown

- **哪个资源承接 shipping 写入**：**待读调用点，非 xref 可得**。
- **Farfetch 的 transport**：无线索。

### 九、教训

**零值需要对照才能读。** 而这一轮之前我做过三次「查不到」，每次都给了一个**听起来对**的解释。

**→ 而那三个解释都是从一个零推出来的，没有一个是拿一个**已知非零**的东西比出来的。**

**→ 而对照的成本是一次调用 —— 而它把「推断」变成「观察」，并且**否掉了我上一轮写下的方法**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1044", BLOCKER)
    ensure(RSTATUS, "R1044", BLOCKER)
    ensure(RVERDICT, "第 1044 轮", VERDICT)
    ensure(BACKLOG, "R1044", BACKLOG_ADD)

    note = (
        "\n## R1044 补充 — **字符串池无 xref（通性，有对照）；「搜 immediates」被否；生成物更正**（套件 2258）\n\n"
        "**两种仪器都 0**：`xrefs_to 0x147053d8c`/`0x147053c94` **0/0** · 8 字节小端 `bin_search` **0**\n"
        "（x64 `lea rip+disp` ⇒ 绝对地址不落盘）。\n\n"
        "**而对照给出答案**：`datadome 0x146ffe1fc` **0** · `queue-it 0x147147794` **0**\n"
        "⇒ **「池条目无 xref」是产物通性**，`xrefs` 对 NativeAOT 池字符串**整个无效**。\n\n"
        "**三次查询的解释史**：R1039「按 base+offset」→ R1043「池条目无 xref」→ **R1044「所有池条目都无 xref（有对照）」**。\n"
        "**前两次是推断，第三次是观察。**\n\n"
        "**解法换了**：从**数据段**找 `(ptr,len)` 表，或反编译**已知**调用 Nike buy 面的函数\n"
        "—— **比一次 `xrefs` 查询大得多**，要写明否则下一轮会以为是一步活。\n\n"
        "**更正**：上一轮写进生成物的「搜 immediates」已删；`CORE_COVERAGE.md` 4,241 → **4,974** 字节，\n"
        "那一节现为「五条不能解决 + 两条能解决」。\n\n"
        "数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · xref 0/0 · 立即数 0 · 对照 0/0 · 表 4,974 字节。\n\n"
        "纪律：**零值需要对照才能读** —— 否则「查不到」会被一个听起来对的解释填满。\n\n"
        "下一轮：从数据段找指向 `checkouts/v3` 的 `(ptr,len)` 表，或读 `NikeEndpoints` 那一族的装配点。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1044" not in h:
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
             for p, k in ((RBLOCK, "R1044"), (RSTATUS, "R1044"), (RVERDICT, "第 1044 轮"), (BACKLOG, "R1044")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1044: the string pool carries no xrefs at all, and a control is what showed it\n\n"
         "R1043 left one method to try: search the immediates that reference the two Nike buy URLs. Two instruments\n"
         " returned zero -- xrefs_to for both addresses, and an eight-byte little-endian binary search, which cannot\n"
         " work on x64 anyway because a pool entry is reached with a rip-relative lea and the absolute address is never\n"
         " stored.\n\n"
         "A control settles what those zeros mean. Two pool strings located in earlier rounds, datadome and queue-it,\n"
         " also return zero xrefs. So an empty xref list is a property of this artifact's string pool, not something\n"
         " particular about those two URLs, and xrefs is not an instrument for pool strings at all.\n\n"
         "That reinterprets three earlier queries. R1039 read a zero as base-plus-offset addressing; R1043 read the next\n"
         " zero as pool entries carrying no xrefs. Both explanations were close, and both were inferences, because\n"
         " neither compared against something known to be non-zero. This round does, in one call, and the same answer\n"
         " from a string that certainly is referenced turns an inference into an observation.\n\n"
         "It also retracts what I wrote last round. The generated table said to search immediates; that section now\n"
         " holds five checks that cannot settle the question and two approaches that could -- walking the data segment\n"
         " for the pool's pointer-length pairs, or decompiling a function already known to call Nike's buy surface. Both\n"
         " are larger than one xrefs query, and the document says so, because otherwise the next round would treat it as\n"
         " a single step.\n\n"
         "Figures: suite 2258 unchanged, freshness zero, count 174,293, two zero xref counts that a control explains,\n"
         " one method retracted, and the coverage table growing from 4,241 to 4,974 bytes with the checks that do not\n"
         " work written down beside the ones that might.\n\n"
         "Unknown: which resource takes the shipping write, and Farfetch's transport.\n\n"
         "The lesson is that a zero needs a control before it can be read, and that without one a zero gets filled with\n"
         " whatever explanation sounds right -- three times now, each one plausible, none of them observed.\n\n"
         "One generator changed; suite green at 2258."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()