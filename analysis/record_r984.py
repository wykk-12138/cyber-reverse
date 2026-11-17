"""Record R984: the scattered block checks do disagree, and the disagreement has a number."""

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
### 那 30 处封锁判断**不一致**，而分歧有数字：23 处把「非成功」当「被封」（R984）

**R983 说下一轮核那 30 处是否彼此一致 —— 因为「形状不同会不会导致行为不同」全看这条。核完了。**

### ① 29 处，形状高度重复

```
19 处完全同一行： return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };
其余：Stores.Abstractions.cs 的枚举定义（Blocked = 4）
      StoreFlowRunner.cs:25/71   if (!anti.Ok) → Blocked
      StoreFlowRunner.cs:241/242 429 => Blocked · 401 => Blocked
      StoreFlowRunner.cs:300     private static CheckoutOutcome Blocked(...)
```

### ② 而它们前面那个 `if` **只有一个**

**把「Blocked 行」往上找到最近的 `if`：**

```
23 ×  if (!res.IsSuccess)
```

### ③ 而 `IsSuccess` 是「2xx 到 3xx」

```csharp
// src/Cybersole.Http/TlsProfile.cs
public bool IsSuccess => StatusCode is >= 200 and < 400;
```

> **所以 `!res.IsSuccess` 对 **404 和 500 都成立** —— 也就是说：**
> **「商品页没了」和「站方在拒绝我」在这 23 处是**同一件事**。**
> **而同一项目的 `StoreFlowRunner` 把它们分开：只有 `401` / `429` 判 Blocked，
> 反爬探测失败单独判。****

### ④ 所以 R983 的「形状不同」现在有了语义

| 位置 | 判据 | 404 的结果 |
|---|---|---|
| `StoreFlowRunner`（集中） | `401` / `429` / `!anti.Ok` | **不是 Blocked** |
| 23 个 module（分散） | `!res.IsSuccess` | **Blocked** |

> **两半**互相矛盾**，而且错的那一半是数量多的那一半。**
> **一个把「下架」报成「被封」的监控，比什么都不报更坏 ——
> 它会把真的 drop 藏在一个「我被封了」的故事后面。****

### ⑤ 这与 HANDOFF 未结案项 #2 是同一类缺陷

**#2 写的是「长度守卫把『响应体短/空』判成缺货」。**
**两条的形状一样：**用一个与目标现象无关的量，去决定那个现象。**
- 长度守卫：用 `body.Length` 决定「有没有货」
- 这 23 处：用 `!IsSuccess` 决定「有没有被封」

> **而两条都是「误报」方向 —— 误报缺货会错过 drop，误报封锁也会。
> 而这个项目已经记过一次「误报缺货 = 错过 drop，不可重来」。**

### ⑥ 这一轮**没有**改那 23 处，而理由要写清

**改它意味着逐站决定「404 对该站应该意味着什么」。而那需要镜像侧证据，这一轮没取到。**

> **所以加的是**守卫**，不是修复：**
> **`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）**
> 1. `IsSuccess` 的定义仍是 `>= 200 and < 400`（定义一改，下面的数就不再有意义）
> 2. 混淆点的数量**不得超过** 23（新增一处就红，并列出新的是哪一处）
> 3. 数量**必须等于** 23（减少了也要改常数并说明换成了什么 —— 防止常数变成过时的上界）

### 数字

| 度量 | R983 | **R984** |
|---|---|---|
| 套件 | 2200 | **2203** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是**（记录仍有效；新增代码未进变异集） |
| **`!IsSuccess`→Blocked 的点** | 未测 | **23** |

### 教训

> **「不一致」这个说法在没有数字的时候是软的。而一旦它变成「23 处对 3 处」，
> 就有了一个明确的、可以往下走的下一步。**
> **而这一轮真正的收获是：那 30 处的**共同点**不是一个共享的判据，
> 而是一行**复制了 23 遍的代码**。**
"""

if "那 30 处封锁判断**不一致**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 984 轮：那 30 处封锁判断不一致，而分歧有数字 —— 23 处把「非成功」当「被封」

### ① 29 处，形状高度重复

```
19 处完全同一行：return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };
其余：枚举定义 · StoreFlowRunner 的 401/429/!anti.Ok · private static Blocked(...)
```

### ② 而它们前面那个 `if` 只有一个

```
23 ×  if (!res.IsSuccess)
```

### ③ 而 `IsSuccess` 是「2xx 到 3xx」

```csharp
public bool IsSuccess => StatusCode is >= 200 and < 400;   // TlsProfile.cs
```

> **所以 `!res.IsSuccess` 对 **404 和 500 都成立** ——
> 「商品页没了」和「站方在拒绝我」在这 23 处是**同一件事**。
> 而 `StoreFlowRunner` 把两者分开：只有 401 / 429 判 Blocked。**

### ④ 所以 R983 的「形状不同」现在有了语义

| 位置 | 判据 | 404 的结果 |
|---|---|---|
| `StoreFlowRunner`（集中） | `401` / `429` / `!anti.Ok` | **不是 Blocked** |
| 23 个 module（分散） | `!res.IsSuccess` | **Blocked** |

> **两半互相矛盾，而错的那一半是数量多的那一半。
> 一个把「下架」报成「被封」的监控，比什么都不报更坏 —— 它会把真的 drop 藏在一个「我被封了」的故事后面。**

### ⑤ 与 HANDOFF 未结案项 #2 是同一类缺陷

**#2：长度守卫用 `body.Length` 决定「有没有货」。这一条：用 `!IsSuccess` 决定「有没有被封」。
两条的形状一样 —— **用一个与目标现象无关的量，去决定那个现象**，而两条都是**误报**方向。**

### ⑥ 这一轮没改那 23 处，理由写清

**改它要逐站决定「404 对该站意味着什么」，而那需要镜像侧证据，这一轮没取到。**

**所以加的是**守卫**：`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）**
1. `IsSuccess` 的定义仍是 `>= 200 and < 400`
2. 混淆点**不得超过** 23（新增即红并列出新点）
3. 数量**必须等于** 23（减少了也要改常数并说明换成了什么）

### 数字

| 度量 | R983 | **R984** |
|---|---|---|
| 套件 | 2200 | **2203** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是**（记录仍有效） |
| **`!IsSuccess`→Blocked 的点** | 未测 | **23** |

### 教训

> **「不一致」在没有数字时是软的说法。变成「23 处对 3 处」之后，就有了明确的下一步。
> 而真正的收获是：那 30 处的**共同点**不是一个共享判据，而是一行**复制了 23 遍的代码**。**
"""

BACKLOG_ADD = """

## 判据 (f)/优先级 ② — **23 处 `!res.IsSuccess` → Blocked：把 404/500 当封锁**（R984，**+3 守卫**）

### 测量

**29 处 `Blocked`，其中 23 处的前置 `if` 是同一个：`if (!res.IsSuccess)`。
而 `IsSuccess => StatusCode is >= 200 and < 400` → **404 与 500 都是 Blocked**。**

**同一项目的 `StoreFlowRunner` 只把 `401` / `429` / `!anti.Ok` 判 Blocked → **两半矛盾，错的是数量多的那半**。**

### 为什么坏

**把「下架」报成「被封」，会把真的 drop 藏在一个「我被封了」的故事后面。
与 HANDOFF 未结案项 #2（长度守卫用 `body.Length` 判缺货）是同一类缺陷：用一个与目标现象无关的量去决定它。**

### 这一轮加的是守卫，不是修复

**`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）：`IsSuccess` 定义不变 · 混淆点 ≤ 23 · 混淆点 == 23。**

**没改那 23 处的理由：改它要逐站决定「404 对该站意味着什么」，需要镜像侧证据，未取到。**

### 数字

**套件 2203 · 陈旧度 0/0 · 函数数 173,952 · 混淆点 23**

| 仍 Unknown | |
|---|---|
| 404 / 500 在各站应判什么 | 需镜像侧证据 |
| 原版 `HandleBlock` 是否就是这一层 | 无 xref / MethodTable 未通 |

**纪律**：「不一致」要有数字才硬 —— 23 对 3。
"""

BLOCKER = """

---

## 408. **23 处 `!res.IsSuccess` → Blocked：把 404/500 当封锁；+3 守卫**

> R984。**加 3 个守卫，未改那 23 处。** 套件 **2203 通过 / 0 失败 / 0 跳过**。

### 一、测量

**29 处 `Blocked`。把「Blocked 行」往上找最近的 `if`，23 处是同一个条件：**

```
23 ×  if (!res.IsSuccess)
```

**而：**

```csharp
// src/Cybersole.Http/TlsProfile.cs
public bool IsSuccess => StatusCode is >= 200 and < 400;
```

**→ `!res.IsSuccess` 对 **404 和 500 都成立**。
→ 「商品页没了」与「站方在拒绝我」在这 23 处是**同一件事**。**

### 二、而集中的那一处把两者分开

| 位置 | 判据 | 404 的结果 |
|---|---|---|
| `StoreFlowRunner`（集中） | `401` / `429` / `!anti.Ok` | **不是 Blocked** |
| 23 个 module（分散） | `!res.IsSuccess` | **Blocked** |

**→ 两半互相矛盾，而错的那一半是数量多的那一半。
→ 一个把「下架」报成「被封」的监控，比什么都不报更坏 —— 它把真的 drop 藏在「我被封了」的故事后面。**

### 三、与未结案项 #2 同一类

**#2：长度守卫用 `body.Length` 决定「有没有货」。
本条：用 `!IsSuccess` 决定「有没有被封」。**

**两条的形状一样：**用一个与目标现象无关的量，去决定那个现象**，而两条都是**误报**方向。**

### 四、这一轮加守卫，不改那 23 处

**`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）：**

1. `TheSuccessTestIsStillWhatSuccessMeans` —— `IsSuccess` 仍是 `>= 200 and < 400`
   （**定义一改，下面的数就不再有意义**）
2. `NobodyNewTreatsAFailedResponseAsABlock` —— 混淆点**不得超过** 23，失败时列出新的是哪一处
3. `TheCountIsNotStaleInTheOtherDirection` —— 数量**必须等于** 23
   （**减少了也要改常数并说明换成了什么，防止常数变成过时的上界**）

**没改那 23 处的理由：改它意味着逐站决定「404 对该站应该意味着什么」，
而那需要镜像侧证据，这一轮没取到。**

### 五、数字

| 度量 | R983 | R984 |
|---|---|---|
| 套件 | 2200 | **2203** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是**（记录仍有效；新增代码未进变异集） |
| **`!IsSuccess`→Blocked 的点** | 未测 | **23** |

### 六、验证

```
cd replica
python - 扫 src 找 Blocked 行并上溯最近的 if -> 23 × if (!res.IsSuccess)
dotnet test --filter "FullyQualifiedName~BlockIsNotTheAbsenceOfSuccessTests" -m:1  -> 3 通过
python tools/metrics_report.py  -> 完整套件 exit 0  2203 通过 / 0 失败 / 0 跳过
```

### 七、仍然 Unknown

- **404 / 500 在各站应判什么**：**Unknown** —— 需镜像侧证据。
- **原版 `HandleBlock` 是否就是这一层**：**Unknown** —— 无 xref，MethodTable 路线未通。

### 八、教训

**「不一致」这个说法在没有数字的时候是软的。一旦变成「23 处对 3 处」，就有了明确的下一步。**

**而这一轮真正的收获是：那 30 处的**共同点**不是一个共享判据，
而是一行**复制了 23 遍的代码**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R984", BLOCKER)
    ensure(RSTATUS, "R984", BLOCKER)
    ensure(RVERDICT, "第 984 轮", VERDICT)
    ensure(BACKLOG, "R984", BACKLOG_ADD)

    note = (
        "\n## R984 补充 — **23 处 `!res.IsSuccess` → Blocked（404/500 都算封锁）；+3 守卫**（套件 2203）\n\n"
        "29 处 `Blocked`，把「Blocked 行」上溯最近的 `if`：**23 处都是 `if (!res.IsSuccess)`**。\n"
        "而 `IsSuccess => StatusCode is >= 200 and < 400` → **404 与 500 都是 Blocked**。\n\n"
        "→ 与集中的 `StoreFlowRunner`（只 `401`/`429`/`!anti.Ok` 判 Blocked）**矛盾，错的是数量多的那半**。\n"
        "→ 一个把「下架」报成「被封」的监控，比什么都不报更坏 —— 它把真的 drop 藏在「我被封了」的故事后面。\n"
        "→ 与 HANDOFF 未结案项 #2（长度守卫用 `body.Length` 判缺货）**同一类**：用与目标现象无关的量去决定它，都是误报方向。\n\n"
        "**这一轮加守卫不改那 23 处**：改它要逐站决定「404 对该站意味着什么」，需要镜像侧证据，未取到。\n"
        "`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）：`IsSuccess` 定义不变 · 混淆点 ≤ 23 · 混淆点 == 23。\n\n"
        "数字：套件 2203 · 陈旧度 0/0 · 函数数 173,952 · 混淆点 23。\n\n"
        "纪律：那 30 处的**共同点**不是一个共享判据，而是一行**复制了 23 遍的代码**。\n\n"
        "下一轮：取镜像侧证据判「404 各站应是什么」，或先把 401/403/429 收进一个 `IsBlocked` 分类器并让 23 处改用它。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R984" not in h:
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
             for p, k in ((RBLOCK, "R984"), (RSTATUS, "R984"), (RVERDICT, "第 984 轮"), (BACKLOG, "R984")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R984: the scattered block checks do disagree, and the disagreement is twenty-three against three\n\n"
         "R983 left one question: whether the replica's thirty-odd block checks agree with each other, since the shape\n"
         " difference only matters if it changes behaviour. Measured, it does.\n\n"
         "There are twenty-nine Blocked sites. Walking back from each to its nearest if gives twenty-three that share one\n"
         " condition: if (!res.IsSuccess). And IsSuccess is defined as a status between 200 and 400, so that condition is true\n"
         " for 404 and for 500 exactly as it is for a challenge page. The central runner in the same project treats only 401\n"
         " and 429 that way, and reports a failed anti-bot probe separately. So the two halves contradict each other, and the\n"
         " wrong half is the one with the numbers.\n\n"
         "A monitor that calls a delisting a block is worse than one that reports nothing, because it buries the drop that did\n"
         " happen inside a story about being blocked. This is also the same defect class as the open item about the length\n"
         " guard judging stock from body length: a quantity unrelated to the thing being decided, deciding it, and in the\n"
         " false-positive direction both times.\n\n"
         "This round adds a guard rather than a fix. Fixing means deciding, per site, what a 404 should mean there, and that\n"
         " needs original-side evidence not obtained here. The guard pins the number in three ways: that IsSuccess still means\n"
         " what it means, that no new site may conflate a failed response with a block, and that the constant may not become a\n"
         " stale upper bound when sites are removed.\n\n"
         "Figures: suite 2200 to 2203, freshness zero, count 173,952, twenty-three conflated sites.\n\n"
         "Unknown: what 404 and 500 should mean at each store, which needs original-side evidence; and whether the original's\n"
         " HandleBlock is this layer, whose string has no xrefs and whose MethodTable route did not work.\n\n"
         "The lesson is that \"inconsistent\" was soft until it had a number, and that the thirty sites' real common feature is\n"
         " not a shared predicate but one line copied twenty-three times.\n\n"
         "Three guard tests added; no behaviour changed; suite green at 2203."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()