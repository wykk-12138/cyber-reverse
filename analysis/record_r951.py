"""Record R951: wiring worked -- the class is in the artifact -- but .pdata counts non-inlined functions."""

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
### 接线成功了，而函数数**还是不动** —— 因为 `.pdata` 数的是**未被内联**的函数（R951）

**R950 说「接线才动数」。这一轮接了：`RedirectPolicy` 接进 `NetClient.SendAsync`。**

### 而接线**确实成功了**

```
修改前:  TooManyRedirects 不在产物
修改后:  TooManyRedirects **在**产物
size: 54,652 KB -> 54,655 KB
```

**所以 R950 那条「可达才进产物」是对的。**

### 而函数数**还是 173,653**

### 原因在工具自己的注里

> 「`.pdata` holds one RUNTIME_FUNCTION per non-leaf function:
> it **excludes inlined and trimmed code**」

**而我接进去的是 `IsRedirect` / `LimitFrom` / `Resolve` / `PreservesMethod` / `TooManyRedirectsName` ——
**五个小方法**。**

> **它们全部被**内联**了。内联之后，它们不是函数，是别人函数体里的几条指令。
> 所以产物里**有那个类**（字面量在），而 `.pdata` 里**没有那几个函数**。**

### 所以三层结论，一层比一层窄

| 层 | 判据 | 我加的代码 |
|---|---|---|
| **写了** | 源码里有 | ✅ |
| **进了产物** | 字面量/可达 | ✅（R951 证实） |
| **进了 `.pdata`** | **未被内联** | **❌** |

> **而目标写的是「函数数量对等」—— 那指的是第三层。
> 所以「写」和「接」都不够；**方法得大到编译器不愿内联**，或者**是 async（状态机会留下）。****

### 而 `FollowAsync` 是 async —— 它**会**留一个状态机

**而我没接它：`NetClient` 用的是 `IsRedirect` 那几个同步小方法 + 自己的递归，
没走 `RedirectPolicy.FollowAsync`。**

> **所以真正会动数的那个方法，反而没被调用。而这是因为我在接线时选了**最省事的五个小函数**，
> 而不是那个真正的循环。**

### 数字

| 度量 | R950 | **R951** |
|---|---|---|
| 套件 | 2088 | **2093** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`TooManyRedirects` 在产物** | 不在 | **在** |
| **函数数** | 173,653 | **173,653（仍不变）** |
| 产物大小 | 54,652 KB | **54,655 KB** |

### 教训

> **三层的区别是这一轮唯一的产出，而它比「又写了一个类」贵得多：
> 「写了」「进了产物」「进了 `.pdata`」是三件不同的事，而我一直只查第一件，
> 上一轮查了第二件，这一轮才明白目标指的是第三件。**
> **而第三件的判据不是我的意图，是**编译器的内联决定** —— 一个我完全看不见的、由方法大小和调用次数决定的开关。**
"""

if "接线成功了，而函数数**还是不动**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 951 轮：接线成功，而函数数还是不动 —— `.pdata` 数的是未被内联的函数

### 接线确实成功了

```
修改前  TooManyRedirects 不在产物
修改后  TooManyRedirects 在产物      size 54,652 -> 54,655 KB
```

**所以 R950 那条「可达才进产物」是对的。**

### 而函数数还是 173,653

### 原因在工具自己的注里

> 「`.pdata` holds one RUNTIME_FUNCTION per non-leaf function: it **excludes inlined and trimmed code**」

**而我接的是五个小方法（`IsRedirect`/`LimitFrom`/`Resolve`/`PreservesMethod`/`TooManyRedirectsName`）——
全部被**内联**。产物里有那个类，`.pdata` 里没有那几个函数。**

### 三层结论

| 层 | 判据 | 我加的 |
|---|---|---|
| 写了 | 源码里有 | ✅ |
| 进了产物 | 可达 | ✅（R951 证实） |
| **进了 `.pdata`** | **未被内联** | **❌** |

> **目标说的是第三层。所以「写」和「接」都不够：方法得大到编译器不愿内联，或者是 async。**

### 而 `FollowAsync` 是 async —— 它会留状态机，而我**没接它**

**`NetClient` 用的是那五个同步小方法 + 自己的递归，没走 `FollowAsync`。
所以真正会动数的那个方法反而没被调用 —— 因为接线时我选了最省事的五个小函数，而不是那个真正的循环。**

### 数字

| 度量 | R950 | **R951** |
|---|---|---|
| 套件 | 2088 | **2093** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| `TooManyRedirects` 在产物 | 不在 | **在** |
| 函数数 | 173,653 | **173,653** |
| 产物大小 | 54,652 KB | **54,655 KB** |

### 教训

> **「写了」「进了产物」「进了 `.pdata`」是三件不同的事，而我一直只查第一件。
> 第三件的判据不是我的意图，是**编译器的内联决定** —— 一个我看不见的、由方法大小和调用次数决定的开关。**
"""

BACKLOG_ADD = """

## 判据 (c)/③ — 接线成功；`TooManyRedirects` 进产物；而 `.pdata` 数非内联函数（R951，**+5 用例**）

### 接线

**`RedirectPolicy.{IsRedirect,LimitFrom,Resolve,PreservesMethod,TooManyRedirectsName}` 接进 `NetClient.SendAsync`；
`RequestOptions` 加 `int? MaxRedirects`；`FollowRedirects` 被尊重；用 `Clone()` 而非 `with`（class 不是 record）。**

### 三层的区别（本轮核心）

| 层 | 判据 | 结果 |
|---|---|---|
| 写了 | 源码有 | ✅ |
| 进产物 | 可达 | ✅ |
| 进 `.pdata` | 未被内联 | ❌ |

### 而 `FollowAsync`（async，会留状态机）**没被接** —— 接的是五个小方法

### 数字

**套件 2088 → 2093 · 陈旧度 0/0 · 函数数 173,653 未变 · 产物 54,652 → 54,655 KB**

| 仍 Unknown | |
|---|---|
| 内联阈值在哪 | 未测 |
| 已有 HTTP 层有多少方法被内联 | 未测 |
| 103,467 缺口的可行路径 | 需要「大方法 + 可达」 |

**纪律**：第三件的判据是编译器的内联决定，不是我的意图。
"""

BLOCKER = """

---

## 375. 接线成功；`.pdata` 数的是未被内联的函数

> R951。**改产品代码 +5 用例。** 套件 **2093 通过 / 0 失败 / 0 跳过**。

### 一、接线确实成功

```
修改前  TooManyRedirects 不在产物
修改后  TooManyRedirects 在产物
size 54,652 KB -> 54,655 KB
```

**R950 的「可达才进产物」被证实。**

### 二、而函数数还是 173,653

**工具自己的注：「`.pdata` holds one RUNTIME_FUNCTION per non-leaf function:
it **excludes inlined and trimmed code**」**

**我接的五个小方法全被内联 → 产物里有类，`.pdata` 里没有函数。**

### 三、三层

| 层 | 判据 | 结果 |
|---|---|---|
| 写了 | 源码有 | ✅ |
| 进产物 | 可达 | ✅ |
| **进 `.pdata`** | **未被内联** | **❌** |

**目标指的是第三层。**

### 四、而 `FollowAsync`（async，会留状态机）**没被接**

**接的是五个同步小方法 + 自己的递归。真正会动数的那个方法反而没被调用。**

### 五、改动清单

- **`NetClient.SendAsync` 加私有 hop 重载 + redirect 分支**
- **`RequestOptions` 加 `int? MaxRedirects`**
- **`FollowRedirects` 被尊重**
- **`options.Clone()` 而非 `with`（class 不是 record）+ `using System.Globalization;`**

### 六、数字

| 度量 | R950 | R951 |
|---|---|---|
| 套件 | 2088 | **2093** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`TooManyRedirects` 在产物** | 不在 | **在** |
| 函数数 | 173,653 | **173,653** |
| 产物大小 | 54,652 KB | **54,655 KB** |

### 七、验证

```
搜产物 TooManyRedirects  -> 在（R950 时不在）
func_count.py            -> 173,653 未变
test --filter RedirectWiringTests -> 5 通过
metrics_report.py        -> 2093 通过 / 0 失败
```

### 八、仍然 Unknown

- **内联阈值在哪**：**Unknown** —— 未测。
- **已有 HTTP 层有多少方法被内联**：**Unknown** —— 未测。
- **103,467 缺口的可行路径**：**Inference** —— 需要「大方法 + 可达」。

### 九、教训

**「写了」「进了产物」「进了 `.pdata`」是三件不同的事，而我一直只查第一件。**

**第三件的判据不是我的意图，是编译器的内联决定 —— 一个我看不见的、由方法大小和调用次数决定的开关。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R951", BLOCKER)
    ensure(RSTATUS, "R951", BLOCKER)
    ensure(RVERDICT, "第 951 轮", VERDICT)
    ensure(BACKLOG, "R951", BACKLOG_ADD)

    note = (
        "\n## R951 补充 — 接线成功；.pdata 数的是未被内联的函数（+5 用例，套件 2093）\n\n"
        "接线成功：TooManyRedirects 从「不在产物」变成「在产物」，size 54,652 → 54,655 KB。R950 的「可达才进产物」证实。\n\n"
        "而函数数还是 173,653 —— 工具注写着「.pdata excludes inlined and trimmed code」，"
        "我接的五个小方法全被内联。\n\n"
        "三层：写了（源码有）✅ · 进产物（可达）✅ · 进 .pdata（未被内联）❌ —— 目标指的是第三层。\n"
        "而 FollowAsync（async，会留状态机）反而没被接：接的是五个同步小方法 + 自己的递归。\n\n"
        "数字：套件 2088 → 2093 · 陈旧度 0/0 · 函数数 173,653 未变 · 产物 54,652 → 54,655 KB。\n\n"
        "纪律：第三件的判据是编译器的内联决定，不是我的意图。\n\n"
        "下一轮：把 FollowAsync 接进去（async 状态机会留 .pdata 条目）；或测内联阈值。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R951" not in h:
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
             for p, k in ((RBLOCK, "R951"), (RSTATUS, "R951"), (RVERDICT, "第 951 轮"), (BACKLOG, "R951")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R951: the wiring worked and the count still did not move, because .pdata excludes inlined code\n\n"
         "R950 said wiring is what moves the count, so this round wired RedirectPolicy into NetClient.SendAsync. The\n"
         " wiring did work: TooManyRedirects was absent from the artifact before and is present now, and its size grew by\n"
         " three kilobytes. So reachability is what gets code into the product.\n\n"
         "The function count is still 173,653, and the tool's own note explains why: .pdata holds one entry per non-leaf\n"
         " function and excludes inlined and trimmed code. What I wired were five small methods -- IsRedirect, LimitFrom,\n"
         " Resolve, PreservesMethod and the exception name -- which the compiler inlined into SendAsync. So the class is in\n"
         " the product and its functions are not in .pdata, because after inlining they are instructions inside someone\n"
         " else's body rather than functions of their own.\n\n"
         "That separates three things that had been one in my head: written in source, present in the artifact, and\n"
         " present in .pdata. The first two are now both verified and the third is the one the objective names, which\n"
         " means neither writing nor wiring is sufficient -- a method has to be large enough that the compiler declines to\n"
         " inline it, or async, since a state machine survives inlining.\n\n"
         "And FollowAsync is async, so it would have left an entry. I did not wire it: SendAsync uses the five small\n"
         " synchronous helpers plus its own recursion. The one method that would have moved the number is the one I\n"
         " bypassed, because when wiring I reached for the cheapest five calls rather than the real loop.\n\n"
         "Figures: suite 2088 to 2093, freshness zero, the artifact from 54,652 to 54,655 kilobytes, and the function\n"
         " count unchanged at 173,653.\n\n"
         "Unknown: where the inlining threshold sits, which was not measured; how much of the existing HTTP layer was\n"
         " inlined away; and what path the remaining gap can actually take, inferred as large reachable methods.\n\n"
         "The lesson is that the third criterion is decided by the compiler's inlining rather than by my intent -- a\n"
         " switch I cannot see, set by method size and call count.\n\n"
         "Product code changed; suite green at 2093."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()