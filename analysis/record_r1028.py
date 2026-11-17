"""Record R1028: CloudflareSolver's eight properties, and why the How column is not being changed a third time."""

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
### `CloudflareSolver` 的八个属性；而**连续第三次改同一列**是我不改它的理由（R1028）

**R1027 说下一轮找 relay 的协议。找了，而找到的东西**又**推翻了那一列的判断 —— 所以这一轮不改它。**

### ① `/v1/warm` 之后什么都没有

```
cf-solver.cybersole.io/     n=1   → 只有 /v1/warm
v1/solve                    n=0
v1/result                   n=0
v1/task                     n=5   → 但属 aycd.io / uncaptcha.io（别的第三方）
```

**→ `cf-solver.cybersole.io` 只有**一个**路径：`/v1/warm`。
→ 没有 solve、没有 result。**所以它是一个**预热**端点，不是求解端点。**

### ② 而 `CloudflareSolver` 的八个属性说明求解者是谁

```
Cybersole.CloudflareSolvers.CloudflareSolver,   n=25
  Name (get/set) · Type (get)
  ApiKey (get/set)
  Balance (get/set) · BalanceSupported (get) · IsFetchingBalance (get/set)
  Count (get/set) · Concurrency (get/set)
```

**→ 每一个都在描述一个**用户配置的付费 solver**：**

| 属性 | 它意味着 |
|---|---|
| `ApiKey` | 用户填**自己的** key |
| `Balance` + `BalanceSupported` + `IsFetchingBalance` | **付费服务**才需要向用户显示余额 |
| `Type` | 有**多种** solver 可选 |
| `Count` · `Concurrency` · `Name` | 就是一个服务商条目 |

**→ 而 `DataDomeSolver` · `DatadomeSolver` · `Cybersole.Solvers.` 全部 **0 命中** —— datadome **没有**这个类。
→ 所以两家**走的路不一样**：cloudflare 是用户填 key 的第三方，datadome 是原版自建的中继。**

### ③ 而这意味着 `How` 要**第三次**改 —— 而我不改

**`How` 的历史：**

| 轮 | 值 | 理由 | 被什么推翻 |
|---|---|---|---|
| R1026 | `RemoteApi` / `Local` | 「有 `API down` 文案」 | R1027：cloudflare/datadome 走中继而无 outage |
| R1027 | `Relay` / `ThirdPartyApi` | 「有自建 host vs 有 outage」 | **R1028：cloudflare 两者都有** |
| R1028 | **不改** | — | — |

> **→ 连续第三次，同一个列。而那是一个信号：我在**用一条症状反推一个机制**，而每次都有第三种情形。
> → 而正确的反应不是第三次改值，是**先问清这个列在回答什么问题**。**

### ④ 而这个列的问题在于它想同时答两件事

**「谁在解」有两个独立维度：**

| 维度 | 取值 | 证据 |
|---|---|---|
| **求解者是谁** | 用户配的第三方 / 原版自建 / 本地实现 | `ApiKey`+`Balance` vs `*-solver.cybersole.io` vs 无 host |
| **是否经原版中转** | 是 / 否 | `cf-solver…/v1/warm` vs 直连 |

**→ cloudflare = 用户第三方 **+** 经原版预热 ⇒ 一个维度装不下。
→ datadome = 原版自建 + 直连。
→ kasada/akamai = 第三方（有 `API down`）+ 直连。
→ 所以那是**两个正交的轴**，而我一直想用一个枚举装。**

### ⑤ 所以本轮的交付是**诊断**，不是又一次改值

**→ 不改 `How`；把 `CloudflareSolver` 的八属性与 `ApiKey`/`Balance` 的含义记下来。
→ 下一轮把 `How` 换成**两个**列（或一个带两个字段的记录），而那时它才装得下三种情形。**

**→ 而 `How` 现在的 cloudflare = `Relay` 是**不完整**的 —— 它说了「经自建」而没说「求解者是用户第三方」。
→ 那个不完整现在写在这里，而不是留在代码里当结论。**

### ⑥ 数字

| 度量 | R1027 | **R1028** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（未改代码）** |
| 产物陈旧度 | 4 / 3,869 | **4 / 3,869** |
| 函数数 | 174,336 | **174,336** |
| **`cf-solver` 的路径数** | 未知 | **1（只有 `/v1/warm`）** |
| **`CloudflareSolver` 的属性数** | 未知 | **8** |
| **`DataDomeSolver` 类** | 未查 | **0 命中** |
| **`How` 的修正次数** | 2（R1026 · R1027） | **2 —— 第三次被诊断挡住** |

### 教训

> **连续两次改同一个列，而两次都被下一轮推翻 —— 那说明问题不在值上，在**列的定义**上。**
> **→ 而第三次我差点又改。拦住我的是数一下：**这个列我这轮是第几次动它。**
> **→ 三次动同一个地方，第一次是修，第二次是修错了，第三次该先问它该不该存在。**
"""

if "`CloudflareSolver` 的八个属性" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1028 轮：`CloudflareSolver` 的八个属性；而连续第三次改同一列是不改它的理由

### ① `/v1/warm` 之后什么都没有

```
cf-solver.cybersole.io/  n=1  → 只有 /v1/warm
v1/solve n=0 · v1/result n=0
v1/task  n=5 → 但属 aycd.io / uncaptcha.io
```

**→ `cf-solver.cybersole.io` 只有**一个**路径 ⇒ 它是**预热**端点，不是求解端点。**

### ② 而 `CloudflareSolver` 的八个属性说明求解者是谁

```
Name (get/set) · Type (get) · ApiKey (get/set)
Balance (get/set) · BalanceSupported (get) · IsFetchingBalance (get/set)
Count (get/set) · Concurrency (get/set)
```

**→ `ApiKey` = 用户填自己的 key；`Balance` + `BalanceSupported` + `IsFetchingBalance` = **付费服务**才需显示余额；
`Type` = 多种 solver 可选 ⇒ **那就是一个服务商条目。**
→ 而 `DataDomeSolver` · `DatadomeSolver` · `Cybersole.Solvers.` 全 **0 命中** ⇒ datadome **没有**这个类。**

### ③ 而这意味着 `How` 要**第三次**改 —— 而我不改

| 轮 | 值 | 理由 | 被什么推翻 |
|---|---|---|---|
| R1026 | `RemoteApi`/`Local` | 有 `API down` | R1027：cloudflare/datadome 走中继无 outage |
| R1027 | `Relay`/`ThirdPartyApi` | 自建 host vs outage | **R1028：cloudflare 两者都有** |
| **R1028** | **不改** | — | — |

**→ 连续第三次，同一个列 ⇒ 我在**用一条症状反推一个机制**，而每次都有第三种情形。**

### ④ 而这个列想同时答两件事（两个正交轴）

| 维度 | 取值 |
|---|---|
| **求解者是谁** | 用户第三方（`ApiKey`+`Balance`）/ 原版自建（`*-solver.cybersole.io`）/ 本地 |
| **是否经原版中转** | 是（`/v1/warm`）/ 否 |

**→ cloudflare = 用户第三方 **+** 经原版预热 ⇒ 一个维度装不下。**

### ⑤ 所以本轮交付是**诊断**，不是又一次改值

**不改 `How`；下一轮把它换成**两个**列（或带两个字段的记录），那时它才装得下三种情形。
→ `How` 现在的 cloudflare = `Relay` 是**不完整**的（说了「经自建」没说「求解者是用户第三方」），
而那个不完整现在写在这里，不是留在代码里当结论。**

### ⑥ 数字

| 度量 | R1027 | **R1028** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（未改代码）** |
| 产物陈旧度 | 4 / 3,869 | **4 / 3,869** |
| 函数数 | 174,336 | **174,336** |
| **`cf-solver` 路径数** | 未知 | **1** |
| **`CloudflareSolver` 属性数** | 未知 | **8** |
| **`DataDomeSolver` 类** | 未查 | **0 命中** |
| **`How` 修正次数** | 2 | **2 —— 第三次被诊断挡住** |

### 教训

> **连续两次改同一列、两次都被下一轮推翻 —— 那说明问题不在值上，在**列的定义**上。
> → 拦住第三次的不是判断力，是数一下：**这个列我这轮是第几次动它。**
> → 三次动同一个地方，第一次是修，第二次是修错了，第三次该先问它该不该存在。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`CloudflareSolver` 八属性：求解者是用户配的第三方；`How` 需要两个轴**（R1028）

### `cf-solver.cybersole.io` 只有一个路径

```
cf-solver.cybersole.io/  n=1 → /v1/warm
v1/solve 0 · v1/result 0
```

**→ 它是**预热**端点，不是求解端点。**

### `CloudflareSolver` 的八个属性

```
Name · Type · ApiKey · Balance · BalanceSupported · IsFetchingBalance · Count · Concurrency
```

**→ `ApiKey` 用户自己的 key · `Balance`/`BalanceSupported`/`IsFetchingBalance` 付费服务 · `Type` 多种 ⇒ 服务商条目。
→ 而 `DataDomeSolver`/`DatadomeSolver`/`Cybersole.Solvers.` **0 命中** ⇒ datadome 走自建中继，没有 solver 类。**

### 所以 `How` 装不下 —— 它需要两个正交轴

| 轴 | 取值 |
|---|---|
| 求解者 | 用户第三方 / 原版自建 / 本地 |
| 是否经原版中转 | 是 / 否 |

**cloudflare = 用户第三方 + 经预热 ⇒ 一个枚举装不下。**

### 本轮不改代码（诊断）

**`How` 已改两次（R1026 · R1027），两次都被下一轮推翻。第三次先问「这一列该不该存在」。**
**→ cloudflare = `Relay` 是**不完整**的，那个不完整写在这里而不是留在代码里当结论。**

### 数字

**套件 2243/0/0（未改代码）· 陈旧度 4 / 3,869 · 函数数 174,336 · cf-solver 路径 1 · 属性 8 · How 修正 2 次**

| 仍 Unknown | |
|---|---|
| `Type` 有哪些 solver 取值 | 未取证 |
| 预热之后真的求解打到哪 | 未取证 |

**纪律**：三次动同一个地方，第一次是修，第二次是修错了，第三次该先问它该不该存在。
"""

BLOCKER = """

---

## 452. **`CloudflareSolver` 八属性：求解者是用户配的第三方；`How` 需要两个轴**

> R1028。**未改代码 —— 本轮是诊断。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、`/v1/warm` 之后什么都没有

```
cf-solver.cybersole.io/     n=1   → 只有 /v1/warm
v1/solve                    n=0
v1/result                   n=0
v1/task                     n=5   → 但属 aycd.io / uncaptcha.io（别的第三方）
```

**→ `cf-solver.cybersole.io` 只有**一个**路径：`/v1/warm`。
→ 没有 solve、没有 result ⇒ **它是一个**预热**端点，不是求解端点。**

### 二、而 `CloudflareSolver` 的八个属性说明求解者是谁

```
Cybersole.CloudflareSolvers.CloudflareSolver,   n=25
  Name (get/set) · Type (get)
  ApiKey (get/set)
  Balance (get/set) · BalanceSupported (get) · IsFetchingBalance (get/set)
  Count (get/set) · Concurrency (get/set)
```

| 属性 | 它意味着 |
|---|---|
| `ApiKey` | 用户填**自己的** key |
| `Balance` + `BalanceSupported` + `IsFetchingBalance` | **付费服务**才需要向用户显示余额 |
| `Type` | 有**多种** solver 可选 |
| `Count` · `Concurrency` · `Name` | 就是一个服务商条目 |

**→ 而 `DataDomeSolver` · `DatadomeSolver` · `Cybersole.Solvers.` 全部 **0 命中** —— datadome **没有**这个类。
→ 所以两家**走的路不一样**：cloudflare 是用户填 key 的第三方，datadome 是原版自建的中继。**

### 三、而这意味着 `How` 要**第三次**改 —— 而我不改

| 轮 | 值 | 理由 | 被什么推翻 |
|---|---|---|---|
| R1026 | `RemoteApi` / `Local` | 「有 `API down` 文案」 | R1027：cloudflare/datadome 走中继而无 outage |
| R1027 | `Relay` / `ThirdPartyApi` | 「有自建 host vs 有 outage」 | **R1028：cloudflare 两者都有** |
| **R1028** | **不改** | — | — |

**→ 连续第三次，同一个列。而那是一个信号：我在**用一条症状反推一个机制**，而每次都有第三种情形。
→ 而正确的反应不是第三次改值，是**先问清这个列在回答什么问题**。**

### 四、而这个列的问题在于它想同时答两件事

| 维度 | 取值 | 证据 |
|---|---|---|
| **求解者是谁** | 用户配的第三方 / 原版自建 / 本地实现 | `ApiKey`+`Balance` vs `*-solver.cybersole.io` vs 无 host |
| **是否经原版中转** | 是 / 否 | `cf-solver…/v1/warm` vs 直连 |

**→ cloudflare = 用户第三方 **+** 经原版预热 ⇒ 一个维度装不下。
→ datadome = 原版自建 + 直连。
→ kasada/akamai = 第三方（有 `API down`）+ 直连。
→ 所以那是**两个正交的轴**，而我一直想用一个枚举装。**

### 五、所以本轮的交付是**诊断**，不是又一次改值

**→ 不改 `How`；把 `CloudflareSolver` 的八属性与 `ApiKey`/`Balance` 的含义记下来。
→ 下一轮把 `How` 换成**两个**列（或一个带两个字段的记录），而那时它才装得下三种情形。**

**→ 而 `How` 现在的 cloudflare = `Relay` 是**不完整**的 —— 它说了「经自建」而没说「求解者是用户第三方」。
→ 那个不完整现在写在这里，而不是留在代码里当结论。**

### 六、数字

| 度量 | R1027 | R1028 |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（未改代码）** |
| 产物陈旧度 | 4 / 3,869 | **4 / 3,869** |
| 函数数 | 174,336 | **174,336** |
| **`cf-solver` 的路径数** | 未知 | **1（只有 `/v1/warm`）** |
| **`CloudflareSolver` 的属性数** | 未知 | **8** |
| **`DataDomeSolver` 类** | 未查 | **0 命中** |
| **`How` 的修正次数** | 2 | **2 —— 第三次被诊断挡住** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "cf-solver\\.cybersole\\.io/"   -> {"n":1}（只有 /v1/warm）
python analysis/ida.py str "v1/solve"                     -> {"n":0}
python analysis/ida.py str "v1/result"                    -> {"n":0}
python analysis/ida.py str "Cybersole\\.CloudflareSolvers\\.CloudflareSolver,"  -> {"n":25}
python analysis/ida.py str "DataDomeSolver"               -> {"n":0}
python analysis/ida.py str "Cybersole\\.Solvers\\."         -> {"n":0}
cd replica && python tools/metrics_report.py -> 完整套件 exit 0  2243 / 0 / 0
```

### 八、仍然 Unknown

- **`Type` 有哪些 solver 取值**：**未取证**。
- **预热之后真的求解打到哪**：**未取证**。

### 九、教训

**连续两次改同一个列，而两次都被下一轮推翻 —— 那说明问题不在值上，在**列的定义**上。**

**→ 而第三次我差点又改。拦住我的是数一下：**这个列我这轮是第几次动它。**
**→ 三次动同一个地方，第一次是修，第二次是修错了，第三次该先问它该不该存在。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1028", BLOCKER)
    ensure(RSTATUS, "R1028", BLOCKER)
    ensure(RVERDICT, "第 1028 轮", VERDICT)
    ensure(BACKLOG, "R1028", BACKLOG_ADD)

    note = (
        "\n## R1028 补充 — **`CloudflareSolver` 八属性：求解者是用户配的第三方；`How` 需要两个轴**（套件 2243，未改代码）\n\n"
        "**`cf-solver.cybersole.io/` 只有 **1** 个路径：`/v1/warm`。`v1/solve` 0 · `v1/result` 0 ⇒ **预热端点，不是求解端点。**\n\n"
        "**`CloudflareSolver` 八个属性**：`Name` · `Type` · `ApiKey` · `Balance` · `BalanceSupported` ·\n"
        "`IsFetchingBalance` · `Count` · `Concurrency`。\n"
        "→ `ApiKey` = 用户自己的 key · `Balance`/`BalanceSupported`/`IsFetchingBalance` = **付费服务** · `Type` = 多种 ⇒ **服务商条目**。\n"
        "→ 而 `DataDomeSolver` / `DatadomeSolver` / `Cybersole.Solvers.` **全 0 命中** ⇒ datadome 走自建中继，无 solver 类。\n\n"
        "**所以 `How` 要第三次改 —— 而我不改。** 已改两次（R1026 · R1027），两次都被下一轮推翻。\n"
        "→ 问题不在值上，在**列的定义**上：它想同时装「求解者是谁」与「是否经原版中转」**两个正交轴**。\n"
        "→ cloudflare = 用户第三方 **+** 经原版预热 ⇒ 一个枚举装不下。\n\n"
        "**本轮是诊断**：不改 `How`，`cloudflare = Relay` 的**不完整**写在这里，不留在代码里当结论。\n"
        "**下一轮把 `How` 换成两个列/两个字段。**\n\n"
        "数字：套件 2243/0/0（未改代码）· 陈旧度 4 / 3,869 · 函数数 174,336 · cf-solver 路径 **1** · 属性 **8** · How 修正 **2** 次。\n\n"
        "纪律：**三次动同一个地方，第一次是修，第二次是修错了，第三次该先问它该不该存在。**\n\n"
        "下一轮：把 `How` 换成两个轴（求解者 + 是否中转）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1028" not in h:
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
             for p, k in ((RBLOCK, "R1028"), (RSTATUS, "R1028"), (RVERDICT, "第 1028 轮"), (BACKLOG, "R1028")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1028: CloudflareSolver has eight properties, and that is why How is not changing a third time\n\n"
         "R1027 sent this round after the relay protocol. Looking for it produced evidence that contradicts R1027's own\n"
         " classification, which makes this the second round running where the How column was wrong -- so this round\n"
         " diagnoses the column instead of editing it again.\n\n"
         "cf-solver.cybersole.io has exactly one path, /v1/warm. There is no v1/solve and no v1/result, so it warms\n"
         " something up rather than solving anything. What actually solves is named by a class: CloudflareSolver carries\n"
         " Name, Type, ApiKey, Balance, BalanceSupported, IsFetchingBalance, Count and Concurrency. An ApiKey the user\n"
         " supplies, a balance the app fetches and displays, and a choice of types are the shape of a paid solver the\n"
         " user subscribes to, not of something the original runs. DataDome has no equivalent class at all -- DataDomeSolver,\n"
         " DatadomeSolver and the Cybersole.Solvers namespace are all absent -- so those two vendors are arranged\n"
         " differently, which is what R1027 was trying to express and did not have the pieces for.\n\n"
         "The column cannot express it because it is answering two questions at once: who solves, and whether the\n"
         " original relays the traffic. Cloudflare is a user-configured third party that also gets warmed through the\n"
         " original's own host. One enum, two axes.\n\n"
         "So How stays as it is for now, with an acknowledged incompleteness recorded here -- cloudflare's Relay notes the\n"
         " relaying and not the solver -- rather than a third guess installed as a conclusion. The next round splits it.\n\n"
         "Figures: suite 2243 unchanged since no code changed, freshness four files and 3,869 lines, count 174,336,\n"
         " cf-solver at one path, CloudflareSolver at eight properties, DataDome's solver classes at zero, and How having\n"
         " been corrected twice.\n\n"
         "Unknown: what Type can be set to, and where the solving request actually goes after warming.\n\n"
         "The lesson is that two corrections to the same column in consecutive rounds, each overturned by the next,\n"
         " says the fault is in the column's definition rather than in any of its values -- and the thing that stopped a\n"
         " third attempt was counting how many times I had already been here, not judgement about this particular value.\n\n"
         "No code changed; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()