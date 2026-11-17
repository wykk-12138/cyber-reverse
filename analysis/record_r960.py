"""Record R960: PollQueue was a bare Ok and now makes the decision the protocol describes."""

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
### `PollQueue` 本来是 `=> Ok()`，而它现在做决定了（R960）

**R959 说下一步重发消陈旧度。重发之前先看一眼 `PollQueueAsync` —— 而它是：**

```csharp
public virtual Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct) => Ok();
```

> **一个命中排队页的流程会**认为自己已经通过了排队**，因为那个步骤直接返回成功，
> 而它没有看任何东西。**
> **而那正是 R959 那个字段列表要治的病 —— 只是没人把它接上。****

### 接上之后

**`PollQueueAsync` 现在做四件事：**

1. **不是队列宿主 → 直接成功**（`IsQueueHost`，没有可等的）
2. **循环到 deadline**，每轮 `Verdict(status, hasPass)` 分类
3. **`Passed` 但要再看剩余时间** —— 剩余短于 `queueMinRemaining` 就**继续等**，
   而不是把那个通行证花在一个**会被拒的请求**上
4. **超时 = `retryable: true` 的失败**

> **第 4 条是这一轮的正题：`Ok()` 说超时是成功。而超时不是成功。
> 一个把超时说成成功的步骤，比一个报错的步骤**难查得多** —— 因为下游会拿到一个假的绿灯。****

### 三个设置名

**`queueTimeout`（120s）· `queuePollMs`（2000）· `queueMinRemaining`（30s）· `queuePassSeconds`（300）**

**而它们的值标了 Inference —— 镜像给了字段名（`CookieValiditySeconds` / `MinRemainingSeconds`），
没给数值。**

### 数字

| 度量 | R959 | **R960** |
|---|---|---|
| 套件 | 2147 | **2153** |
| 产物陈旧度 | 1 文件 / 119 行 | **0 / 0** |
| **函数数** | 173,866 | **173,909（+43）** |
| **函数比** | 62.75% | **62.76%** |

### 教训

> **上一轮我把 Queue-it 的判定条件读出来了，而这一轮发现那个该用它的步骤**从来没看任何东西**。
> 而这不是我造成的 —— 它在 R112 就是这样，而**没有任何东西指出它**。
> **一个 `=> Ok()` 的虚步骤读起来像一个「留给子类覆写」的位置，而它同时是一个**假的成功**。
> 两者的差别只在**有没有人覆写它**。**
"""

if "`PollQueue` 本来是 `=> Ok()`" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 960 轮：`PollQueue` 本来是 `=> Ok()`，现在做决定了

### 发现

```csharp
public virtual Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct) => Ok();
```

**命中排队页的流程会**认为自己通过了排队** —— 那个步骤直接返回成功，没看任何东西。**

### 接上之后四件事

1. **不是队列宿主 → 直接成功**（没有可等的）
2. **循环到 deadline**，每轮 `Verdict(status, hasPass)` 分类
3. **`Passed` 但剩余时间短于 `queueMinRemaining` → 继续等**（不把通行证花在会被拒的请求上）
4. **超时 = `retryable: true` 的失败**

> **第 4 条是正题：`Ok()` 说超时是成功，而超时不是成功。
> 一个把超时说成成功的步骤比一个报错的步骤**难查得多** —— 下游会拿到一个假的绿灯。**

### 设置名

**`queueTimeout`(120s) · `queuePollMs`(2000) · `queueMinRemaining`(30s) · `queuePassSeconds`(300)**
**数值标 Inference —— 镜像给了字段名，没给数值。**

### 数字

| 度量 | R959 | **R960** |
|---|---|---|
| 套件 | 2147 | **2153** |
| 产物陈旧度 | 1 / 119 | **0 / 0** |
| **函数数** | 173,866 | **173,909（+43）** |
| **函数比** | 62.75% | **62.76%** |

### 教训

> **一个 `=> Ok()` 的虚步骤读起来像「留给子类覆写」的位置，而它同时是一个**假的成功**。
> 两者的差别只在**有没有人覆写它**。**
> **而它从 R112 就是这样，没有任何东西指出它 —— 因为它长得像设计，不像缺陷。**
"""

BACKLOG_ADD = """

## 优先级 ② — `PollQueueAsync` 从 `=> Ok()` 变成真判定（R960，**+6 用例**）

### 原来

**`=> Ok()` —— 命中排队页的流程认为自己通过了排队。**

### 现在

**`IsQueueHost` 前置 · 循环到 deadline · `Verdict` 分类 · 剩余时间不足则继续等 · **超时 = retryable 失败****

### 设置（值标 Inference，名为镜像字段名）

**`queueTimeout` · `queuePollMs` · `queueMinRemaining` · `queuePassSeconds`**

### 数字

**套件 2147 → 2153 · 陈旧度 1/119 → **0/0** · 函数数 173,866 → **173,909（+43）** · 比 62.76%**

| 仍 Unknown | |
|---|---|
| 四个设置的镜像真值 | 只有字段名 |
| 排队页的轮询语义（长轮询/短轮询） | 未取证 |
| `Softblock` 的处理差别 | 只有两条文案 |

**纪律**：`=> Ok()` 读起来像设计，不像缺陷 —— 差别只在有没有人覆写它。
"""

BLOCKER = """

---

## 384. `PollQueueAsync` 从 `=> Ok()` 变成真判定

> R960。**改产品代码 +6 用例。** 套件 **2153 通过 / 0 失败 / 0 跳过**。

### 一、发现

```csharp
public virtual Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct) => Ok();
```

**命中排队页的流程认为自己通过了排队 —— 没看任何东西。**

### 二、现在

1. **`IsQueueHost` 前置**（不是队列宿主直接成功）
2. **循环到 deadline**，每轮 `Verdict(status, hasPass)`
3. **`Passed` 但剩余短于 `queueMinRemaining` → 继续等**
4. **超时 = `retryable: true` 失败**

**第 4 条是正题：超时不是成功。**

### 三、设置

**`queueTimeout`(120s) · `queuePollMs`(2000) · `queueMinRemaining`(30s) · `queuePassSeconds`(300) —— 值标 Inference**

### 四、数字

| 度量 | R959 | R960 |
|---|---|---|
| 套件 | 2147 | **2153** |
| 产物陈旧度 | 1 / 119 | **0 / 0** |
| **函数数** | 173,866 | **173,909（+43）** |
| **函数比** | 62.75% | **62.76%** |

### 五、验证

```
grep 'PollQueueAsync.*=> Ok()' StoreFlow.cs -> 无
test --filter PollQueueWiringTests         -> 6 通过
func_count.py                              -> 173,909 (+43)
metrics_report.py                          -> 2153 通过 / 0 失败
```

### 六、仍然 Unknown

- **四个设置的镜像真值**：**Unknown** —— 只有字段名。
- **排队页的轮询语义**：**Unknown** —— 未取证。
- **`Softblock` 的处理差别**：**Unknown** —— 只有两条文案。

### 七、教训

**一个 `=> Ok()` 的虚步骤读起来像「留给子类覆写」的位置，而它同时是一个假的成功。**

**两者的差别只在有没有人覆写它。而它从 R112 就是这样，没有任何东西指出它 —— 因为它长得像设计。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R960", BLOCKER)
    ensure(RSTATUS, "R960", BLOCKER)
    ensure(RVERDICT, "第 960 轮", VERDICT)
    ensure(BACKLOG, "R960", BACKLOG_ADD)

    note = (
        "\n## R960 补充 — PollQueueAsync 从 `=> Ok()` 变成真判定（+6 用例，套件 2153）\n\n"
        "发现 PollQueueAsync 是 `=> Ok()` —— 命中排队页的流程认为自己通过了排队，没看任何东西。\n\n"
        "现在：IsQueueHost 前置 · 循环到 deadline · Verdict 分类 · 剩余时间不足则继续等 · **超时 = retryable 失败**。\n"
        "超时不是成功 —— 把超时说成成功的步骤比报错的步骤难查得多（下游拿到假绿灯）。\n\n"
        "设置：queueTimeout(120s) · queuePollMs(2000) · queueMinRemaining(30s) · queuePassSeconds(300) —— 值标 Inference。\n\n"
        "数字：套件 2147 → 2153 · 陈旧度 1/119 → **0/0** · 函数数 173,866 → **173,909（+43）** · 比 62.76%。\n\n"
        "纪律：`=> Ok()` 读起来像设计不像缺陷 —— 差别只在有没有人覆写它。\n\n"
        "下一轮：扫还有多少个 `=> Ok()` 的空壳虚步骤（它们的数量决定下一个批次）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R960" not in h:
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
             for p, k in ((RBLOCK, "R960"), (RSTATUS, "R960"), (RVERDICT, "第 960 轮"), (BACKLOG, "R960")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R960: PollQueue was a bare Ok and now makes the decision its protocol describes\n\n"
         "R959 left a plan to republish and clear the freshness row. Before that, PollQueueAsync turned out to be a bare\n"
         " Ok(), which means a flow that hit a waiting room believed it had passed one: the step returned success without\n"
         " looking at anything. The field list recovered last round existed to drive exactly this decision and nothing was\n"
         " connecting it.\n\n"
         "The step now does four things. A non-queue host returns success immediately, since there is nothing to wait for.\n"
         " Otherwise it polls to a deadline, classifying each response with QueueItProtocol.Verdict on the status and the\n"
         " presence of a pass together, because a 200 with a pass is through and a 200 without one is still queued. A pass\n"
         " whose remaining validity is under the margin keeps waiting rather than being spent on a request that will be\n"
         " refused after the queue has been left. And running out of time is a retryable failure.\n\n"
         "That last point is the round's substance: the Ok() said timeout was success, and a step that reports timeout as\n"
         " success is far harder to find than one that reports an error, because everything downstream receives a false\n"
         " green light.\n\n"
         "Four settings carry the values -- queueTimeout, queuePollMs, queueMinRemaining and queuePassSeconds -- and all\n"
         " four numbers are labelled inference, since the image gives the field names without the values.\n\n"
         "Figures: suite 2147 to 2153, freshness from one file and a hundred and nineteen lines to zero, count 173,866 to\n"
         " 173,909, ratio 62.75 to 62.76 percent.\n\n"
         "Unknown: the real values of the four settings; whether the waiting room expects long or short polling; and what\n"
         " Softblock does differently, of which only two message strings survive.\n\n"
         "The lesson is that a virtual step returning Ok reads like a place left for a subclass to override, and is also a\n"
         " false success. The difference between the two is only whether anything overrides it -- and this one had been\n"
         " that way since R112 with nothing pointing at it, because it looks like a design rather than a defect.\n\n"
         "Product code and a test class added; suite green at 2153."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()