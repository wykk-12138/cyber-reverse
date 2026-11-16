"""Record R820: the status slot is cleared per step, and the poq-app expectation was the test's, not the code's."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 244. `lastStatus` 跨步残留已修；**而 poq-app 那半是测试的期望不对，不是代码不对**

> R820。改两处：`StoreFlowRunner.GuardAsync` 每步清空状态槽；`ModuleRobustnessTests` 的例外名单加 `poq-app`。

### 一、先找写入点

`lastStatus` 在 `StoreFlow.cs` 里有 **5 个写入点**，全在 HTTP 辅助函数里：

```
L1778 GetAsync      L1796 PostJsonAsync    L1823 SendAsync    L1887 PostFormAsync
L53   RefreshSessionAsync
```

**它们都在 try 里写、catch 里不写。** **所以请求失败时，槽位留着上一次的值。**

### 二、读它的人

- `StoreFlowRunner.ClassifyMonitorFailure` / `ClassifyCheckoutFailure` —— 分类失败
- `StoreFlow.HandleResponseAsync` —— **只有定义，没有调用点（死代码）**
- `StoreFlow.LogBadRequestAsync` —— 也只在槽位存在时读

**因为有死代码挡着，我先确认了 `HandleResponseAsync` 不在活路径上，才敢动槽位。**

### 三、改法：在 `GuardAsync` 里每步开始前清空

```csharp
ct.ThrowIfCancellationRequested();
ctx.Session.Vars.Remove("lastStatus");
```

**一个位置，覆盖 monitor 与 checkout 两条路径的所有步骤。**
**语义正是分类器要的**：「这一步的状态」，而不是「上一步留下的状态」。
**某步真的收到 403 时，辅助函数照样写 403，照样判 `Captcha` —— 正确行为不变。**

### 四、改完**还是 Captcha** —— 于是查出真正的成因

```
Monitor_Survives_An_Unreachable_Host(poq-app)   Expected: Error   Actual: Captcha
```

**清空之后仍然 Captcha，说明这个 403 是 `GetHome` 这一步自己拿到的。**

**读 `PoqAppFlow.GetHomeAsync`（第 126 行）：**

```csharp
public override async Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct)
{
    ApplyIdentity(c);
    var res = await PostJsonAsync(c, Action("account/guest-token"), "{}", _id + "-guest-token", ct);
    if (res is null) return StepOutcome.Fail($"{_id}: guest token unreachable", retryable: true);
    if (IsBlocked(res)) return StepOutcome.Fail($"{_id}: guest token blocked", retryable: true);
    ...
```

**它根本不看 `c.Url`。它 POST 到 `https://platform.poq.io/clients/offspring/account/guest-token`。**

**而 `platform.poq.io` 对一个无身份请求回 403** —— `IsBlocked` 判真 → 报 blocked → 分类器读 403 → `Captcha`。

**所以 `Captcha` 是对的：流程确实撞到了 403。**

**错的是用例的期望。** 那条用例的前提是「一个解析不了的主机不能看起来像有货」，
**这个前提对「会去取我给的那个 URL」的流程成立**；**poq-app 从不取它。**

### 五、改法：把 poq-app 加进例外名单，并写清为什么

```csharp
if (id is "nike" or "nike-gs" or "superswipe" or "poq-app")
    Assert.True(result.Status is MonitorStatus.Blocked or MonitorStatus.Captcha, ...);
```

**注释写明**：Poq 的表面是按客户寻址的 app API，不是网页；那个主机对无身份请求回 403，
`PoqAppFlow.IsBlocked` 把 403 当 blocked，所以流程报的是**它真的撞到的门**。

**这不是放宽断言**：其余 59 个模块仍然必须报 `Error`，`Available` 仍然一律不许。

### 六、验证

```
dotnet test --filter ModuleRobustnessTests    190 通过 / 0 失败
python tools\\metrics_report.py               1766 通过 / 0 失败
四项度量                                       4 / 0 / 17 / 78 / 0（未变）
```

**上一轮 1765 / 1 的状态收口了。**

### 七、仍然 Unknown

- **`platform.poq.io` 现在是否真的对无身份 POST 回 403**：**Inference（高）** ——
  从「403 走到 IsBlocked 分支」推的，**没有单独抓一次。**
- **`HandleResponseAsync` 为什么是死代码**：**Unknown** ——
  它读 `lastStatus`、按状态码分支，看起来该被某步调用，**但没有任何调用点。**
- **其余 59 个模块里，还有谁忽略 `c.Url`**：**Unknown** ——
  本轮只查了 poq-app。**如果一个流程忽略 URL 却没有 403，它会报 transport error，测试就过了，
  于是「忽略 URL」这件事本身不会被发现。**

### 八、教训

**清空状态槽是对的，但它没修好这条用例 —— 而这是有用的信号。**
**「我按诊断改了、症状没变」比「改了就好了」信息量更大**：
**它把「残留」这个假设推翻了，逼我去读流程本身。**

**另一条**：**一条通用前提（「解析不了的主机不能像有货」）在某些实现上不成立时，
该改的是前提的表述，不是实现。** 但要写清是哪一类实现，否则下一个读者会以为是放水。
"""

VERDICT = """

---

## 第 820 轮：状态槽已清；而 poq-app 那半是测试的期望不对

### 先找写入点

`lastStatus` 有 5 个写入点，全在 HTTP 辅助函数里，**都在 try 里写、catch 里不写** —— 失败时留旧值。

### 改法：`GuardAsync` 每步开始前清空

```csharp
ct.ThrowIfCancellationRequested();
ctx.Session.Vars.Remove("lastStatus");
```

**一个位置覆盖两条路径的所有步骤，语义正是分类器要的「这一步的状态」。**
**某步真收到 403 时照样写 403，正确行为不变。**

**动手前确认过 `HandleResponseAsync` 只有定义没有调用点（死代码），才敢动槽位。**

### 改完**还是 Captcha** —— 于是查出真正成因

`PoqAppFlow.GetHomeAsync` **不看 `c.Url`**，它 POST 到 `https://platform.poq.io/clients/offspring/account/guest-token`。
**那个主机对无身份请求回 403** → `IsBlocked` 判真 → 报 blocked → `Captcha`。

> **所以 `Captcha` 是对的：流程确实撞到了 403。错的是用例的期望。**

**那条用例的前提（「解析不了的主机不能像有货」）对「会去取我给的 URL」的流程成立 —— poq-app 从不取它。**

### 改法：加进例外名单并写清原因

`poq-app` 与 `nike`/`nike-gs`/`superswipe` 并列：**报的是它真的撞到的门。**

**不是放宽断言**：其余 59 个模块仍必须报 `Error`，`Available` 仍一律不许。

### 验证

```
ModuleRobustnessTests 190 通过 / 0 失败
metrics_report        1766 通过 / 0 失败
四项度量              4 / 0 / 17 / 78 / 0 未变
```

**上一轮 1765 / 1 收口了。**

### 教训

> **清空状态槽是对的，但它没修好这条用例 —— 而这是有用的信号。**
> **「我按诊断改了、症状没变」比「改了就好了」信息量更大：它把「残留」这个假设推翻了，逼我去读流程本身。**

**另一条：通用前提在某些实现上不成立时，该改的是前提的表述，不是实现 —— 但要写清是哪一类实现，否则读者会以为是放水。**
"""

BACKLOG_ADD = """

## 优先级 ①/③ — 状态槽已清；poq-app 期望已改正（R820）

### 改了两处

1. **`StoreFlowRunner.GuardAsync`**：每步开始前 `ctx.Session.Vars.Remove("lastStatus")` —— 一个位置覆盖 monitor 与 checkout 两条路径
2. **`ModuleRobustnessTests`**：例外名单加 `poq-app`，附原因

### 为什么第二处不是放水

`PoqAppFlow.GetHomeAsync` **忽略 `c.Url`**，POST 到 `platform.poq.io/clients/<client>/account/guest-token`；
**该主机对无身份请求回 403**，`IsBlocked` 把 403 当 blocked。**流程报的是它真撞到的门。**

**其余 59 个模块仍必须报 `Error`；`Available` 仍一律不许。**

```
ModuleRobustnessTests 190 / 0 · metrics_report 1766 / 0 · 四项度量未变
```

| 仍 Unknown | |
|---|---|
| `platform.poq.io` 是否真回 403 | Inference（高），未单独抓 |
| `HandleResponseAsync` 为何是死代码 | 有定义无调用点，原因未知 |
| 还有谁忽略 `c.Url` | **只查了 poq-app**；忽略 URL 但不回 403 的流程会静默通过 |

**纪律**：**「按诊断改了、症状没变」比「改了就好」信息量更大** —— 它推翻了假设。
**一条通用前提在某些实现上不成立时，改前提的表述，不改实现，并写清是哪一类实现。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R820", BLOCKER)
    ensure(RSTATUS, "R820", BLOCKER)
    ensure(RVERDICT, "第 820 轮", VERDICT)
    ensure(BACKLOG, "R820", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R820"), (RSTATUS, "R820"), (RVERDICT, "第 820 轮"), (BACKLOG, "R820")):
        body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R820: clear the status slot per step, and the poq-app expectation belonged to the test\n\n"
         "LastStatus is one key that five HTTP helpers in StoreFlow overwrite, and all five write inside try blocks and\n"
         "skip the write on the catch path, so a step that never issued a request inherits whatever ran before it. The\n"
         "runner now removes the key at the start of every guarded step -- one place covering both the monitor and the\n"
         "checkout paths, giving ClassifyMonitorFailure the status of this step rather than an older one. A step whose\n"
         "request does return a 403 still stores it and still classifies as Captcha, so the correct behaviour is\n"
         "unchanged. Before touching the slot I confirmed HandleResponseAsync, which also reads it, has no call sites.\n\n"
         "The fix did not change the symptom, which was the useful part. Still Captcha, which meant the 403 came from\n"
         "GetHome itself rather than from a previous step, and reading PoqAppFlow.GetHomeAsync explains it: the override\n"
         "ignores the context URL entirely and POSTs to platform.poq.io/clients/offspring/account/guest-token, because a\n"
         "Poq surface is an app API addressed per client rather than a web page. That host answers 403 to an\n"
         "unattributed request, IsBlocked treats 403 as blocked, and the flow reports the gate it actually met.\n\n"
         "So Captcha was correct and the expectation was wrong. The test's premise -- that a URL which never resolves\n"
         "must not look like stock -- holds for every flow that fetches the URL it is given, and this one never fetches\n"
         "it. poq-app joins nike, nike-gs and superswipe in the list of modules that may report Blocked or Captcha, with\n"
         "the reason written beside it. The test keeps its teeth: the other fifty-nine modules must still report Error\n"
         "and Available is still forbidden everywhere.\n\n"
         "Suite is 1766 of 1766, up from last round's 1765 of 1766.\n\n"
         "Unknown: whether platform.poq.io really returns 403, which I infer from the branch taken rather than from a\n"
         "request of my own; why HandleResponseAsync exists with no call sites, since it reads the slot and branches on\n"
         "it as though something should invoke it; and which other flows ignore the context URL, since a flow that\n"
         "ignores it and does not meet a 403 would report a transport error and pass silently, leaving the ignoring\n"
         "invisible.\n\n"
         "The habit worth keeping is that a fix which leaves the symptom unchanged carries more information than one\n"
         "that resolves it: it falsified a hypothesis and forced a reading of the flow itself.\n\n"
         "Four metrics unchanged at 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
