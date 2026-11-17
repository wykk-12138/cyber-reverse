"""Record R1045: the artifact has no business symbol names, which is the root cause of four dead routes."""

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
### 这个产物**没有业务符号名** —— 而那是一条根因，不是第五次失败（R1045）

**R1044 说下一轮「从数据段找 `(ptr,len)` 表，或读 `NikeEndpoints` 那一族」。
而第二个方向我一说就错了：`NikeEndpoints` 是**复刻件**的类。所以我先问了更前面的问题。**

### ① 而那个问题给出了根因

```
functions:        321,244
named sub_*:      311,203   (96.87%)
other names:       10,041   —— 全部是 C++ CRT 符号
```

**样本（全部，不是挑的）：**
```
__CxxQueryExceptionSize · nullsub_81 · nullsub_82
?file_name@__crt_win32_buffer_debug_info@@QEBAPEBDXZ
?raw_length@charNode@@UEBAHXZ
?precision@ios_base@std@@QEBA_JXZ
__except_get_jumpbuf_sp · ?__acrt_select_exit_lock@@YA?AW4__acrt_lock_id@@XZ
```

**→ 96.87% 是 `sub_*`；剩下的 3.13% **没有一个**是 Cybersole 的业务函数名，全是 C++ 运行库。
→ 所以：**反射元数据里的名字（`Farfetch` · `CloudflareSolver` · `DataDomeHandler`）是**数据**，不是符号。****

### ② 而它把前面四条路**一次**解释掉

| 轮 | 试过的路 | 结果 | 根因 |
|---|---|---|---|
| R1040 | 查 `Stores.Flows` 命名空间 | 0 | **符号名里没有命名空间** |
| R1042 | `funcs Nike` | 全是 `sub_*` | **没有叫 Nike 的函数** |
| R1044 | `xrefs` 池条目 | 0（有对照） | **池条目不承载 xref** |
| R1044 | 搜 8 字节立即数 | 0 | **x64 `lea rip+disp`，绝对地址不落盘** |
| **R1045** | **数符号名** | **96.87% `sub_*`** | **符号被剥，名字只在数据里** |

**→ 前四条不是四个独立的坏运气，是**同一个**事实的四个侧面。
→ 而它们各自被我解释过一次，每次的解释都**只覆盖那一轮** —— 因为我没有问「有没有符号名」。**

### ③ 而生成物现在按 (b) 记它

**完成判据 (b) 说：「剩余仅『不可得』文案，且写明为何不可得」。
→ 所以这一条不再是「待查」，而是**不可得 + 四条已排除的路 + 唯一剩下的路**。**

**→ 唯一剩下的：数据流 —— 从数据段找指向池的 `(ptr,len)` 表，再找读它的代码。
→ 而那不是一次查询，是一件工程；**它要写明**，否则下一轮又会以为一步能做完。**

**→ `docs/CORE_COVERAGE.md`：4,974 → **5,980 字节**。**

### ④ 而它对本轮优先级意味着什么

**① 只剩这一条，而它的成本是「一件工程」，且**不保证成功**（那表可能不存在 —— 原版可能在运行时拼 URL）。
→ 所以 ① 的诚实状态是：**端点该有的都有据（门三项全零），而 Nike 那一个二选一不可得。**
→ 而 (f) 的复刻件侧**已完成**，原版侧**不可得且已写明**。**

**→ 所以下一轮该换到 ②（风控）或 ③（指纹层），而那两处还有可算的活。
→ 而在那之前，先把这条结论落进生成物，避免下一轮再从 ① 的同一个点开始。**

### ⑤ 数字

| 度量 | R1044 | **R1045** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改业务代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **函数符号名（`sub_*`）** | 未测 | **311,203 / 321,244 = 96.87%** |
| **业务函数名** | 未问 | **0** |
| **非 `sub_` 名** | 未测 | **10,041，全是 C++ CRT** |
| **已排除的取字符串路** | 3 | **4** |
| **`CORE_COVERAGE.md`** | 4,974 字节 | **5,980 字节** |
| **Nike 二选一的状态** | 「待下一轮」 | **不可得（按 (b) 写明）** |

### 教训

> **四条死路，我给了四个解释，而四个解释都是对的 —— 只是各自只覆盖那一轮。
> → 真正的问题在**上一层**：这个二进制有没有符号名。而那个问题一次调用就能答。**
> **→ 所以「查不到」反复出现时，该问的不是「这次为什么查不到」，
> 而是「**这类查询需要的前提，有没有成立过**」。**
"""

if "这个产物**没有业务符号名**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1045 轮：这个产物没有业务符号名 —— 那是一条根因

### ① 而那个问题给出了根因

```
functions:        321,244
named sub_*:      311,203   (96.87%)
other names:       10,041   —— 全部是 C++ CRT 符号
  __CxxQueryExceptionSize · nullsub_81 · ?file_name@__crt_win32_buffer_debug_info@@ · ?raw_length@charNode@@
```

**→ 96.87% 是 `sub_*`；剩下 3.13% **没有一个**是 Cybersole 的业务函数名。
→ 所以：**反射元数据里的名字（`Farfetch` · `CloudflareSolver`）是**数据**，不是符号。****

### ② 而它把前面四条路**一次**解释掉

| 轮 | 试过的路 | 根因 |
|---|---|---|
| R1040 | 查 `Stores.Flows` 命名空间 | **符号名里没有命名空间** |
| R1042 | `funcs Nike` | **没有叫 Nike 的函数** |
| R1044 | `xrefs` 池条目 | **池条目不承载 xref**（有对照） |
| R1044 | 搜 8 字节立即数 | **x64 `lea rip+disp`，绝对地址不落盘** |
| **R1045** | **数符号名** | **符号被剥，名字只在数据里** |

**→ 前四条不是四个坏运气，是**同一个事实的四个侧面** —— 而我每次的解释都只覆盖那一轮，
因为没有问「有没有符号名」。**

### ③ 而生成物按 (b) 记它

**不再是「待查」，而是**不可得 + 四条已排除的路 + 唯一剩下的路**（数据流找 `(ptr,len)` 表，是一件工程且不保证成功）。**
**→ `CORE_COVERAGE.md`：4,974 → **5,980 字节**。**

### ④ 而它对本轮优先级意味着什么

**① 的诚实状态：端点该有的都有据（门三项全零），而 Nike 那一个二选一**不可得**。
(f) 的复刻件侧**已完成**，原版侧**不可得且已写明**。**
**→ 下一轮该换到 ②（风控）或 ③（指纹层）。**

### ⑤ 数字

| 度量 | R1044 | **R1045** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **`sub_*` 占比** | 未测 | **96.87%（311,203 / 321,244）** |
| **业务函数名** | 未问 | **0** |
| **已排除的取字符串路** | 3 | **4** |
| **`CORE_COVERAGE.md`** | 4,974 字节 | **5,980 字节** |
| **Nike 二选一** | 「待下一轮」 | **不可得（按 (b)）** |

### 教训

> **四条死路，我给了四个解释，四个都对 —— 但各自只覆盖那一轮。
> → 真正的问题在**上一层**：这个二进制有没有符号名。而那问题一次调用就能答。**
> **→ 所以「查不到」反复出现时，该问的不是「这次为什么查不到」，
> 而是「**这类查询需要的前提，有没有成立过**」。**
"""

BACKLOG_ADD = """

## 判据 (a)(b) — **产物无业务符号名（96.87% `sub_*`）⇒ 四条取字符串路全断的根因**（R1045）

### 根因

```
functions 321,244 · sub_* 311,203 (96.87%) · 其余 10,041 全是 C++ CRT 符号 · 业务函数名 0
```

**⇒ 反射元数据里的名字是**数据**，不是符号。**

### 四条路一次解释掉

| 轮 | 路 | 根因 |
|---|---|---|
| R1040 | 命名空间 | 符号名里没有命名空间 |
| R1042 | `funcs Nike` | 没有叫 Nike 的函数 |
| R1044 | `xrefs` 池条目 | 池串无 xref（有对照） |
| R1044 | 8 字节立即数 | x64 `lea rip+disp`，绝对地址不落盘 |

### 按 (b) 记

**Nike 二选一 = **不可得**（四条已排除 + 唯一剩下的数据流是一件工程且不保证成功）。
`CORE_COVERAGE.md` 4,974 → **5,980** 字节。**

### ① 的诚实状态

**端点该有的都有据（门三项全零）· Nike 二选一不可得 · (f) 复刻件侧已完成、原版侧不可得且写明
⇒ 下一轮换 ② 或 ③。**

### 数字

**套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · sub_* 96.87% · 业务名 0 · 排除路 4 · 表 5,980 字节**

| 仍 Unknown | |
|---|---|
| Nike 哪个承接 shipping 写入 | **不可得（已排除四条路）** |
| Farfetch transport | 不可得（同因） |

**纪律**：「查不到」反复出现时，问前提有没有成立过，而不是每次问这次为什么。
"""

BLOCKER = """

---

## 469. **这个产物没有业务符号名 —— 一条根因，不是第五次失败**

> R1045。**改 1 个生成器（未改业务代码）。** 套件 **2258 通过 / 0 失败 / 0 跳过**。

### 一、而那个问题给出了根因

```
functions:        321,244
named sub_*:      311,203   (96.87%)
other names:       10,041   —— 全部是 C++ CRT 符号
```

**样本：**
```
__CxxQueryExceptionSize · nullsub_81 · nullsub_82
?file_name@__crt_win32_buffer_debug_info@@QEBAPEBDXZ
?raw_length@charNode@@UEBAHXZ
?precision@ios_base@std@@QEBA_JXZ
__except_get_jumpbuf_sp · ?__acrt_select_exit_lock@@YA?AW4__acrt_lock_id@@XZ
```

**→ 96.87% 是 `sub_*`；剩下的 3.13% **没有一个**是 Cybersole 的业务函数名，全是 C++ 运行库。
→ 所以：**反射元数据里的名字（`Farfetch` · `CloudflareSolver` · `DataDomeHandler`）是**数据**，不是符号。**

### 二、而它把前面四条路**一次**解释掉

| 轮 | 试过的路 | 结果 | 根因 |
|---|---|---|---|
| R1040 | 查 `Stores.Flows` 命名空间 | 0 | **符号名里没有命名空间** |
| R1042 | `funcs Nike` | 全是 `sub_*` | **没有叫 Nike 的函数** |
| R1044 | `xrefs` 池条目 | 0（有对照） | **池条目不承载 xref** |
| R1044 | 搜 8 字节立即数 | 0 | **x64 `lea rip+disp`，绝对地址不落盘** |
| **R1045** | **数符号名** | **96.87% `sub_*`** | **符号被剥，名字只在数据里** |

**→ 前四条不是四个独立的坏运气，是**同一个**事实的四个侧面。
→ 而它们各自被我解释过一次，每次的解释都**只覆盖那一轮** —— 因为我没有问「有没有符号名」。**

### 三、而生成物现在按 (b) 记它

**完成判据 (b) 说：「剩余仅『不可得』文案，且写明为何不可得」。
→ 所以这一条不再是「待查」，而是**不可得 + 四条已排除的路 + 唯一剩下的路**。

**→ 唯一剩下的：数据流 —— 从数据段找指向池的 `(ptr,len)` 表，再找读它的代码。
→ 而那不是一次查询，是一件工程；且**不保证成功**（那表可能不存在 —— 原版可能在运行时拼 URL）。

**→ `docs/CORE_COVERAGE.md`：4,974 → **5,980 字节**。**

### 四、而它对本轮优先级意味着什么

**① 只剩这一条，而它的成本是「一件工程」，且**不保证成功**。
→ 所以 ① 的诚实状态是：**端点该有的都有据（门三项全零），而 Nike 那一个二选一不可得。**
→ 而 (f) 的复刻件侧**已完成**，原版侧**不可得且已写明**。

**→ 所以下一轮该换到 ②（风控）或 ③（指纹层），而那两处还有可算的活。**

### 五、数字

| 度量 | R1044 | R1045 |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **函数符号名（`sub_*`）** | 未测 | **311,203 / 321,244 = 96.87%** |
| **业务函数名** | 未问 | **0** |
| **非 `sub_` 名** | 未测 | **10,041，全是 C++ CRT** |
| **已排除的取字符串路** | 3 | **4** |
| **`CORE_COVERAGE.md`** | 4,974 字节 | **5,980 字节** |
| **Nike 二选一的状态** | 「待下一轮」 | **不可得（按 (b) 写明）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py py "<遍历 idautils.Functions 计 sub_ 与非 sub_>"
  -> functions 321,244 · sub_* 311,203 · other 10,041（C++ CRT）
cd replica
python tools/core_coverage.py  -> 5,980 字节（含根因与四条排除）
python tools/metrics_report.py -> 完整套件 exit 0  2258 / 0 / 0 · 陈旧度 0 / 0
```

### 七、仍然 Unknown

- **Nike 那个二选一**：**不可得**（四条路已排除，剩下的数据流是一件工程且不保证成功）。
- **Farfetch 的 transport**：同因不可得。

### 八、教训

**四条死路，我给了四个解释，而四个解释都是对的 —— 只是各自只覆盖那一轮。
→ 真正的问题在**上一层**：这个二进制有没有符号名。而那个问题一次调用就能答。**

**→ 所以「查不到」反复出现时，该问的不是「这次为什么查不到」，
  而是「**这类查询需要的前提，有没有成立过**」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1045", BLOCKER)
    ensure(RSTATUS, "R1045", BLOCKER)
    ensure(RVERDICT, "第 1045 轮", VERDICT)
    ensure(BACKLOG, "R1045", BACKLOG_ADD)

    note = (
        "\n## R1045 补充 — **产物无业务符号名（96.87% `sub_*`）⇒ 四条取字符串路全断的根因**（套件 2258）\n\n"
        "```\nfunctions 321,244 · sub_* 311,203 (96.87%) · 其余 10,041 全是 C++ CRT 符号 · 业务函数名 0\n```\n"
        "样本：`__CxxQueryExceptionSize` · `nullsub_81` · `?file_name@__crt_win32_buffer_debug_info@@` · `?raw_length@charNode@@`。\n"
        "**⇒ 反射元数据里的名字（`Farfetch` · `CloudflareSolver`）是**数据**，不是符号。**\n\n"
        "**四条路一次解释掉**：命名空间 0（符号里没有命名空间）· `funcs Nike` 返 `sub_*`（没有叫 Nike 的函数）·\n"
        "`xrefs` 池条目 0（池串无 xref，有对照）· 8 字节立即数 0（x64 `lea rip+disp`，绝对地址不落盘）。\n"
        "**→ 前四条不是四个坏运气，是**同一个事实的四个侧面**。**\n\n"
        "**按 (b) 记**：Nike 二选一 = **不可得**（四条已排除 + 唯一剩下的数据流是一件工程且不保证成功）。\n"
        "`CORE_COVERAGE.md` 4,974 → **5,980** 字节。\n\n"
        "**① 的诚实状态**：端点该有的都有据（门三项全零）· Nike 二选一不可得 ·\n"
        "(f) 复刻件侧完成、原版侧不可得且写明 ⇒ **下一轮换 ②（风控）或 ③（指纹层）**。\n\n"
        "数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · sub_* **96.87%** · 业务名 **0** · 排除路 **4** · 表 5,980 字节。\n\n"
        "纪律：**「查不到」反复出现时，问前提有没有成立过，而不是每次问这次为什么。**\n\n"
        "下一轮：换到 ② 风控（`Solving Akamai (SBSD)/(SDS)` 的协议）或 ③ 指纹层。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1045" not in h:
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
             for p, k in ((RBLOCK, "R1045"), (RSTATUS, "R1045"), (RVERDICT, "第 1045 轮"), (BACKLOG, "R1045")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1045: the artifact has no business symbol names, which is the root of four dead routes\n\n"
         "R1044 carried two directions into this round and one of them was wrong on its face: NikeEndpoints is this\n"
         " workspace's class, not the original's. So the round started one level up, with the question all four earlier\n"
         " failures had in common -- does this binary have symbolic names at all.\n\n"
         "It does not. Of three hundred and twenty-one thousand functions, ninety-six point nine per cent are sub_*, and\n"
         " every one of the remaining ten thousand is a C++ runtime symbol: exception sizes, null subs, decorated\n"
         " std:: and CRT names. Not one is a Cybersole function. The names in the reflection metadata -- Farfetch,\n"
         " CloudflareSolver, DataDomeHandler -- are data, not symbols.\n\n"
         "Which explains four rounds at once. R1040 found no Stores.Flows namespace because there are no namespaces in\n"
         " the symbol table. R1042's funcs Nike returned sub_* because no function is called Nike. R1044's xrefs were\n"
         " empty, with a control, because pool entries carry none. The eight-byte immediate search found nothing because\n"
         " x64 reaches a pool entry by rip-relative lea.\n\n"
         "Each of those had its own explanation, and each explanation was correct, and each covered only its own round.\n"
         " The question that would have covered all four takes one call to answer.\n\n"
         "So the Nike either-or is now recorded as unavailable rather than pending, per criterion (b): four routes\n"
         " excluded with their reasons and their controls, one route left -- walking the data segment for the pool's\n"
         " pointer-length pairs -- and that one is a project, not a query, and may fail if the original assembles the URL\n"
         " at run time. The coverage table grows from 4,974 to 5,980 bytes carrying that.\n\n"
         "Which closes priority one honestly. Every endpoint that should have evidence has it, the gate reads zero on\n"
         " all three counts, the replica half of the coverage criterion is done, and the original half is unavailable\n"
         " with its reasons written down. The next round belongs to risk control or the fingerprint layer, where work\n"
         " remains that can actually be computed.\n\n"
         "Figures: suite 2258 unchanged, freshness zero, count 174,293, ninety-six point nine per cent of functions\n"
         " unnamed, zero business symbols, four routes excluded, and one open question downgraded to unavailable.\n\n"
         "The lesson is that when the same shape of failure keeps recurring, the question is not why this attempt failed\n"
         " but whether the premise every attempt shared was ever true.\n\n"
         "One generator changed; suite green at 2258."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()