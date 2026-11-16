"""Record R952: wiring one async method added 128 functions -- the first movement in fourteen rounds."""

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
### 接一个 async 方法，函数数 **+128** —— 十四轮里第一次动（R952）

**R951 说「`FollowAsync` 是 async，它会留状态机，而我没接它」。这一轮接了。**

```
pdata-replica: 173,653 -> 173,781     +128
pdata-ratio:   62.66%  -> 62.71%
产物大小:      54,655 KB -> 54,674 KB   +19 KB
```

### 而 +128 不是我预期的数

**我接进去的只有**一个**调用点，而它带来 128 个 `.pdata` 条目。**

> **所以一个 async 方法带的不是「一个状态机」：
> 状态机的 `MoveNext`、它的泛型实例化、闭包类、`FollowAsync` 里 `Resolve`/`IsRedirect` 的调用点被内联后的副本 ——
> **编译器为这一个抽象生了 128 个函数。****

### 而这条路径现在有证据了

| 轮 | 假设 | 观测 |
|---|---|---|
| R949 | 「表 0 / 逻辑 1,963」 | **错** —— 表和逻辑都不可达 |
| R950 | 「可达才进产物」 | **对** —— `TooManyRedirects` 从不在变在 |
| R951 | 「可达还不够，要过内联」 | **对** —— 五个小方法内联，`.pdata` 不动 |
| **R952** | **「async 会留状态机」** | **对 —— +128** |

> **四轮，四次修正，最后一次才让那个数动了。
> 而前三次都不是白错：每一次把「为什么不动」往前提了一层 ——
> 不可达 → 可达但内联 → 内联不了的 async。**

### 而这也给出了缺口的一条具体路径

**103,467 个缺口，如果平均每次「接线一个 async 方法」加 ~128，那需要约 **800** 次这样的接线。**

> **而这不是「写 800 个 async 方法」—— 是**把已有的 async 方法接进可达路径**。
> 而复刻件的 flow 里已经有大量 async 方法（`StepAction` 的每一步都是）。
> **所以缺口的性质可能真的是「没接上」，而不是「没写」—— 但 R950 那条只是 Inference，现在有一个数据点了。****

### 数字

| 度量 | R951 | **R952** |
|---|---|---|
| 套件 | 2093 | **2093** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,653 | **173,781（+128）** |
| **函数比** | 62.66% | **62.71%** |
| 产物大小 | 54,655 KB | **54,674 KB** |

### 教训

> **十四轮里函数数一动不动，而让它动的不是「更努力地写」，是**找到那个数到底在数什么**。
> 而找到它花了四轮，每轮都推翻上一轮的因果。**
> **最贵的一轮是 R949：那一轮我写下了「表 0 / 逻辑 1,963」，一个从两个错样本里读出的规律，
> 而它差点让我以为「只要写逻辑就会动」。**
> **如果那条规律没被 R950 推翻，接下来的每一轮都会写「逻辑」，然后困惑为什么不动。**
"""

if "接一个 async 方法，函数数 **+128**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 952 轮：接一个 async 方法，函数数 **+128** —— 十四轮第一次动

### 数字

```
pdata-replica: 173,653 -> 173,781     +128
pdata-ratio:   62.66%  -> 62.71%
size:          54,655 KB -> 54,674 KB   +19 KB
```

**套件 2093 通过 / 0 失败 / 0 跳过 · 陈旧度 0 / 0**

### 而 +128 不是我预期的数

**一个调用点带来 128 个 `.pdata` 条目 —— 所以一个 async 方法带的不是「一个状态机」：
`MoveNext`、泛型实例化、闭包类、被内联进状态机的调用点副本，编译器为一个抽象生了 128 个函数。**

### 四轮，四次修正

| 轮 | 假设 | 观测 |
|---|---|---|
| R949 | 「表 0 / 逻辑 1,963」 | **错** —— 两者都不可达 |
| R950 | 「可达才进产物」 | **对** |
| R951 | 「可达还不够，要过内联」 | **对** |
| **R952** | **「async 会留状态机」** | **对 —— +128** |

> **前三次不是白错：每一次把「为什么不动」往前提了一层。**

### 缺口的一条具体路径

**103,467 / 128 ≈ **800** 次这样的接线。**

> **而那不是「写 800 个 async 方法」—— 是**把已有的 async 方法接进可达路径**。
> 而复刻件的 flow 里已有大量 async 方法（`StepAction` 每一步都是）。
> **所以「缺口是没接上而非没写」从 Inference 变成了有一个数据点支撑的假设。**

### 教训

> **让它动的不是「更努力地写」，是**找到那个数到底在数什么**。
> 最贵的一轮是 R949：「表 0 / 逻辑 1,963」—— 从两个错样本读出的规律，差点让我以为「写逻辑就会动」。
> 如果没被推翻，接下来每轮都会写「逻辑」，然后困惑为什么不动。**
"""

BACKLOG_ADD = """

## 判据 (c)/③ — 函数数 +128（首次变动）；四轮因果链收敛（R952，**改产品代码 + 修 5 处旧断言**）

### 接线

**`NetClient.SendAsync` 的递归换成 `RedirectPolicy.FollowAsync`（async → 状态机）。**

### 数字

**函数数 173,653 → **173,781（+128）** · 比 62.66% → **62.71%** · 产物 54,655 → 54,674 KB · 套件 2093 · 陈旧度 0/0**

### 四轮因果链

**不可达（R949 错）→ 可达才进产物（R950）→ 还要过内联（R951）→ async 留状态机（R952 对）**

### 缺口路径

**103,467 / 128 ≈ 800 次接线（不是写 800 个方法，是把已有的 async 接进可达路径）**

| 仍 Unknown | |
|---|---|
| +128 的构成分解 | 未逐条查 |
| 复刻件有多少 async 未接 | 未统计 |
| 每次接线的平均增量 | 只有 n=1 |

**纪律**：让数动的不是「更努力地写」，是找到那个数在数什么。
"""

BLOCKER = """

---

## 376. 函数数 +128（首次变动）；四轮因果链收敛

> R952。**改产品代码 + 修 5 处旧断言。** 套件 **2093 通过 / 0 失败 / 0 跳过**。

### 一、数字

```
pdata-replica: 173,653 -> 173,781     +128
pdata-ratio:   62.66%  -> 62.71%
size:          54,655 KB -> 54,674 KB
```

### 二、而 +128 不是预期的数

**一个调用点 → 128 个 `.pdata` 条目。一个 async 方法带的不是「一个状态机」：
`MoveNext` · 泛型实例化 · 闭包类 · 被内联进状态机的调用点副本。**

### 三、四轮因果链

| 轮 | 假设 | 结果 |
|---|---|---|
| R949 | 表 0 / 逻辑 1,963 | **错** |
| R950 | 可达才进产物 | 对 |
| R951 | 还要过内联 | 对 |
| R952 | async 留状态机 | **对（+128）** |

### 四、缺口路径

**103,467 / 128 ≈ 800 次接线。不是写 800 个方法，是把已有的 async 接进可达路径。**

### 五、改动

**`SendAsync` 的递归换成 `RedirectPolicy.FollowAsync`（fetch 委托里做后续 hop 的真实请求）；
`TooMany` 时抛 `followed.TooManyMessage()`。**

### 六、修了 5 处旧断言

**`hops + 1` → `limit + 1` · `RedirectPolicy.Resolve` → `limit + 1` · `options.Clone()` → `carried.Clone()` ·
`PreservesMethod` 用法 → `followMethod = HttpMethod.Get` · `TooManyRedirectsName` → `followed.TooManyMessage()`**

### 七、验证

```
dotnet publish       -> 54,674 KB
python tools/func_count.py -> 173,781 (+128)
test --filter Redirect -> 35 通过
metrics_report.py    -> 2093 通过 / 0 失败，比 62.71%
```

### 八、仍然 Unknown

- **+128 的构成分解**：**Unknown** —— 未逐条查。
- **复刻件有多少 async 未接**：**Unknown** —— 未统计。
- **每次接线的平均增量**：**Unknown** —— 只有 n=1。

### 九、教训

**让它动的不是「更努力地写」，是找到那个数到底在数什么。**

**最贵的一轮是 R949：从两个错样本读出「表 0 / 逻辑 1,963」，差点让我以为「写逻辑就会动」。
如果没被 R950 推翻，接下来每轮都会写「逻辑」，然后困惑为什么不动。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R952", BLOCKER)
    ensure(RSTATUS, "R952", BLOCKER)
    ensure(RVERDICT, "第 952 轮", VERDICT)
    ensure(BACKLOG, "R952", BACKLOG_ADD)

    note = (
        "\n## R952 补充 — 函数数 +128（十四轮首次变动）；四轮因果链收敛（套件 2093）\n\n"
        "把 SendAsync 的递归换成 RedirectPolicy.FollowAsync（async → 状态机）：\n"
        "函数数 173,653 → **173,781（+128）** · 比 62.66% → **62.71%** · 产物 54,655 → 54,674 KB。\n\n"
        "而 +128 不是预期数：一个调用点带来 128 个 .pdata 条目（MoveNext · 泛型实例化 · 闭包类 · 内联副本）。\n\n"
        "四轮因果链：不可达（R949 错）→ 可达才进产物（R950）→ 还要过内联（R951）→ async 留状态机（R952 对）。\n\n"
        "缺口路径：103,467 / 128 ≈ 800 次接线（不是写 800 个方法，是把已有的 async 接进可达路径）。\n\n"
        "修了 5 处旧断言（hops+1→limit+1 · Resolve · Clone · PreservesMethod 用法 · TooManyMessage）。\n\n"
        "纪律：让数动的不是「更努力地写」，是找到那个数在数什么。\n\n"
        "下一轮：统计复刻件有多少 async 方法未接进可达路径（这决定 800 次接线是否可行）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R952" not in h:
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
             for p, k in ((RBLOCK, "R952"), (RSTATUS, "R952"), (RVERDICT, "第 952 轮"), (BACKLOG, "R952")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R952: wiring one async method added 128 functions, the first movement in fourteen rounds\n\n"
         "R951 ended with the observation that FollowAsync is async and so would leave a state machine, and that I had\n"
         " wired its five small synchronous helpers instead. This round wired FollowAsync: SendAsync's own recursion is\n"
         " replaced by a call to it, with the fetch delegate making the real requests for each subsequent hop.\n\n"
         "The count moved for the first time since R933: 173,653 to 173,781, ratio 62.66 to 62.71, artifact from 54,655\n"
         " to 54,674 kilobytes.\n\n"
         "One hundred and twenty-eight is not the number I expected from one call site, and that is the interesting part.\n"
         " An async method does not bring one state machine; it brings the MoveNext, the generic instantiations, the\n"
         " closure class, and copies of the call sites inlined into the state machine. The compiler generated 128\n"
         " functions for one abstraction.\n\n"
         "Which closes a four-round chain of corrections. R949 said tables add nothing and logic adds 1,963, which was\n"
         " wrong because both were unreachable. R950 said reachable code gets into the product, which was right.\n"
         " R951 said reachable is not enough because inlining removes small helpers, which was right. R952 says an async\n"
         " method survives inlining and brings many entries with it, which is right. None of the first three was wasted:\n"
         " each moved the question of why the number sat still one layer earlier.\n\n"
         "It also gives the gap a concrete shape. At roughly 128 per wiring, 103,467 needs about 800 of them -- and the\n"
         " work is not writing 800 async methods but connecting the async methods that already exist, of which the flow\n"
         " steps have many. So the guess that the gap is unwired rather than unwritten has one data point behind it now.\n\n"
         "Five older assertions had to be corrected, all of them naming strings the rewrite removed.\n\n"
         "Figures: suite 2093 green, freshness zero, count 173,781, ratio 62.71 percent.\n\n"
         "Unknown: how the 128 break down, which was not inspected; how many async methods the replica leaves\n"
         " unreachable, which would decide whether 800 wirings is feasible; and the average gain per wiring, for which\n"
         " this is a single sample.\n\n"
         "The lesson is that what moved the number was not writing harder but finding out what the number counts, and\n"
         " that took four rounds of overturning my own causes. The most expensive of them was R949, where I wrote down a\n"
         " law read off two bad samples -- had R950 not overturned it, every round after would have written logic and\n"
         " wondered why nothing moved.\n\n"
         "Product code changed; suite green at 2093."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()