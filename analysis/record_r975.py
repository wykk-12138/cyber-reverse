"""Record R975: five of the six core absences are renames, and the sixth is undecided."""

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
### 那 6 个核心缺失：**5 个只是改名**，第 6 个待判（R975）

**R974 说下一轮核这 6 个里有几个只是改名。核完了。**

### 逐条（成员抽样 + 命中文件）

| 原版名 | 复刻件里的实现 | 抽样成员 |
|---|---|---|
| `Cybersole.Global.Settings`（34 成员） | **`GlobalSettings.cs`** | `AutoOpen3DS` `BrowserLimit` `MonitorConcurrency` `RetryDelay` `TaskGroupOrder` `ScrollbarWidth` `StartupPage` `Currency` —— **8/8 全在** |
| `Cybersole.CloudflareSolvers.CloudflareSolver`（9） | **散在 `Drivers.cs` / `CaptchaSolverService.cs` / `GlobalSettings.cs`** | `ApiKey` `BalanceSupported` `IsFetchingBalance` `Concurrency` —— **4/4 全在** |
| `Cybersole.Services.ImapProvider`（4） | **`ImapMailProvider.cs`** | `MessageCount` 在 |
| `Cybersole.Models.Concurrency`（3） | **`ConcurrencyLimit.cs`** | `Maximum` `Ratio` 在 |
| `Cybersole.SmartActions.ActionConfig`（2） | **`SmartActions.cs`** | `Required` 在 |
| `Cybersole.Helpers.ObservableDictionary\\`2`（1） | **未见** | `Count` 是通用成员，命中的是 `Checkout.cs` / `Profiles.cs`，**不能算证据** |

### 所以

**5 个确认改名 —— 而判据 a 的原话是「名字级缺口三分类结案」，
而「命名可不同」是目标里写明的**不算缺口**。**

> **所以这 5 个应当**从缺口里划掉**，而不是留着占位。
> 而第 6 个（`ObservableDictionary\\`2`，两个泛型参数）待判 —— 它可能是 BCL 的
> `System.Collections.ObjectModel` 里现成的类型，复刻件用 BCL 的原版就是「实现不同」，不是缺失。**
> **而这一点我没查 BCL 的清单，所以标 Unknown。****

### 而这意味着判据 a 的缺口从 16 降到 11

| 类 | R974 | **R975** |
|---|---|---|
| 核心 | 6 | **1（`ObservableDictionary\\`2`）** |
| UI | 9 | **9** |
| 未读 | 1 | **1** |
| 合计 | 16 | **11** |

> **所以 16 里：9 个 UI（YG 说不急）+ 1 个未读 + **1 个核心待判**。
> 而「类型缺失」这一条的真实剩余量是 1+1 = 2，不是 16。****

### 数字

| 度量 | R974 | **R975** |
|---|---|---|
| 套件 | 2186 | **2186（只核对）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **核心缺失** | 6 | **1** |
| **类型缺失合计** | 16 | **11（9 UI + 1 未读 + 1 核心）** |

### 教训

> **「类型缺失 16」这个数字里，5 个是改名。而改名在目标里是允许的 ——
> 所以那个 16 从一开始就**高估了 5 个**。**
> **而它没被修正，因为检查工具按**名字**判存在，而**名字可以不同**是目标里明写的自由度。
> 检查工具与目标条款之间有一个洞，而那个洞里装着 5 个假缺口。**
"""

if "那 6 个核心缺失：**5 个只是改名**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 975 轮：那 6 个核心缺失 —— 5 个只是改名，第 6 个待判

### 逐条

| 原版名 | 复刻件 | 抽样成员 |
|---|---|---|
| `Global.Settings`（34） | **`GlobalSettings.cs`** | 8/8 全在（`AutoOpen3DS` `BrowserLimit` `MonitorConcurrency` `RetryDelay` `TaskGroupOrder` `ScrollbarWidth` `StartupPage` `Currency`） |
| `CloudflareSolvers.CloudflareSolver`（9） | 散在 `Drivers.cs` / `CaptchaSolverService.cs` | 4/4 全在 |
| `Services.ImapProvider`（4） | **`ImapMailProvider.cs`** | `MessageCount` 在 |
| `Models.Concurrency`（3） | **`ConcurrencyLimit.cs`** | `Maximum` `Ratio` 在 |
| `SmartActions.ActionConfig`（2） | **`SmartActions.cs`** | `Required` 在 |
| `Helpers.ObservableDictionary\\`2`（1） | **未见** | `Count` 通用，命中不算证据 |

### 所以 5 个确认改名

**判据 a 的原话：「名字级缺口三分类结案」—— 而「命名可不同」是目标里写明的**不算缺口**。**
**→ 这 5 个应从缺口里划掉。**

**第 6 个（`ObservableDictionary\\`2`，两泛型参数）待判 —— 可能是 BCL 现成类型，
若复刻件用 BCL 原版则是「实现不同」不是缺失。**未查 BCL 清单 → Unknown。****

### 而判据 a 的真实剩余量

| 类 | R974 | **R975** |
|---|---|---|
| 核心 | 6 | **1** |
| UI | 9 | **9** |
| 未读 | 1 | **1** |
| 合计 | 16 | **11** |

> **「类型缺失」的真实剩余量是 **1+1 = 2**（1 核心待判 + 1 未读），不是 16。**

### 数字

| 度量 | R974 | **R975** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **核心缺失** | 6 | **1** |
| **类型缺失合计** | 16 | **11** |

### 教训

> **「类型缺失 16」里 5 个是改名，而改名在目标里是允许的 —— 所以那个 16 从一开始就**高估了 5 个**。**
> **它没被修正，因为检查工具按**名字**判存在，而**名字可以不同**是目标里明写的自由度。
> 检查工具与目标条款之间有一个洞，而那个洞里装着 5 个假缺口。**
"""

BACKLOG_ADD = """

## 判据 (a) — **6 个核心缺失中 5 个只是改名；真实剩余 2**（R975）

### 核对结果

| 原版名 | 复刻件实现 | 抽样 |
|---|---|---|
| `Global.Settings`(34) | `GlobalSettings.cs` | 8/8 在 |
| `CloudflareSolvers.CloudflareSolver`(9) | `Drivers.cs`/`CaptchaSolverService.cs` | 4/4 在 |
| `Services.ImapProvider`(4) | `ImapMailProvider.cs` | 在 |
| `Models.Concurrency`(3) | `ConcurrencyLimit.cs` | 在 |
| `SmartActions.ActionConfig`(2) | `SmartActions.cs` | 在 |
| `Helpers.ObservableDictionary\\`2`(1) | **未见** | `Count` 通用，不算证据 |

### 结论

**5 个是改名 → 属于目标里写明的「命名可不同」→ **不算缺口，划掉**。**
**第 6 个待判（可能是 BCL 现成类型）→ Unknown。**

**→ 判据 a「类型缺失」真实剩余：1 核心待判 + 1 未读 = **2**（不是 16）。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 核心缺失 6 → 1 · 类型缺失 16 → 11（实剩 2）**

| 仍 Unknown | |
|---|---|
| `ObservableDictionary`2` 是否 BCL 现成 | 未查 BCL 清单 |
| 第 16 个缺失类型是什么 | 输出截断 |

**纪律**：检查工具按名字判存在，而名字可不同是目标里的自由度 —— 那个洞装着 5 个假缺口。
"""

BLOCKER = """

---

## 399. **6 个核心缺失中 5 个只是改名；判据 a 类型缺失真实剩余 2**

> R975。**只核对，未改代码。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、逐条核对

| 原版名 | 复刻件实现 | 抽样成员 |
|---|---|---|
| `Cybersole.Global.Settings`（34） | **`GlobalSettings.cs`** | `AutoOpen3DS` `BrowserLimit` `MonitorConcurrency` `RetryDelay` `TaskGroupOrder` `ScrollbarWidth` `StartupPage` `Currency` —— **8/8 全在** |
| `CloudflareSolvers.CloudflareSolver`（9） | 散在 `Drivers.cs` / `CaptchaSolverService.cs` / `GlobalSettings.cs` | `ApiKey` `BalanceSupported` `IsFetchingBalance` `Concurrency` —— **4/4 全在** |
| `Services.ImapProvider`（4） | **`ImapMailProvider.cs`** | `MessageCount` 在 |
| `Models.Concurrency`（3） | **`ConcurrencyLimit.cs`** | `Maximum` `Ratio` 在 |
| `SmartActions.ActionConfig`（2） | **`SmartActions.cs`** | `Required` 在 |
| `Helpers.ObservableDictionary\\`2`（1） | **未见** | `Count` 是通用成员，命中的是 `Checkout.cs`/`Profiles.cs`，**不算证据** |

### 二、结论

**5 个确认是改名。而判据 a 的原话是「名字级缺口三分类结案」，
而「命名可不同」是目标里写明的自由度 → **不算缺口，应从缺口里划掉**。**

**第 6 个（`ObservableDictionary\\`2`）待判 —— 可能是 BCL 现成类型，
若复刻件用 BCL 原版则是「实现不同」不是缺失。未查 BCL 清单 → Unknown。**

### 三、判据 a 的真实剩余量

| 类 | R974 | R975 |
|---|---|---|
| 核心 | 6 | **1** |
| UI | 9 | **9** |
| 未读 | 1 | **1** |
| 合计 | 16 | **11** |
| **真实剩余（非 UI、非改名）** | — | **2** |

### 四、数字

| 度量 | R974 | R975 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **核心缺失** | 6 | **1** |
| **类型缺失合计** | 16 | **11** |

### 五、验证

```
cd replica
python tools/where_is.py Settings            -> implementation 组有 GlobalSettings.cs
python tools/where_is.py ImapProvider        -> ImapMailProvider.cs
python tools/where_is.py Concurrency         -> ConcurrencyLimit.cs
python tools/where_is.py ActionConfig        -> SmartActions.cs
python tools/where_is.py ObservableDictionary-> 0 行
python -c "逐成员正则查 src" -> 8/8、4/4 全在
```

### 六、仍然 Unknown

- **`ObservableDictionary\\`2` 是否 BCL 现成类型**：**Unknown** —— 未查 BCL 清单。
- **第 16 个缺失类型是什么**：**Unknown** —— 输出截断。

### 七、教训

**「类型缺失 16」里 5 个是改名，而改名在目标里是允许的 —— 那个 16 从一开始就高估了 5 个。**

**它没被修正，因为检查工具按名字判存在，而名字可不同是目标里明写的自由度。**

**检查工具与目标条款之间有一个洞，而那个洞里装着 5 个假缺口。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R975", BLOCKER)
    ensure(RSTATUS, "R975", BLOCKER)
    ensure(RVERDICT, "第 975 轮", VERDICT)
    ensure(BACKLOG, "R975", BACKLOG_ADD)

    note = (
        "\n## R975 补充 — **6 个核心缺失中 5 个只是改名；判据 a 类型缺失真实剩余 2**（套件 2186）\n\n"
        "逐条核对：\n"
        "- `Global.Settings`(34) → **`GlobalSettings.cs`**，抽样 8/8 全在\n"
        "- `CloudflareSolvers.CloudflareSolver`(9) → 散在 `Drivers.cs`/`CaptchaSolverService.cs`，4/4 全在\n"
        "- `Services.ImapProvider`(4) → **`ImapMailProvider.cs`**\n"
        "- `Models.Concurrency`(3) → **`ConcurrencyLimit.cs`**\n"
        "- `SmartActions.ActionConfig`(2) → **`SmartActions.cs`**\n"
        "- `Helpers.ObservableDictionary`2`(1) → **未见**（`Count` 通用，不算证据）→ Unknown\n\n"
        "→ **5 个是改名 → 属目标里写明的「命名可不同」→ 不算缺口，划掉。**\n"
        "→ 判据 a「类型缺失」真实剩余：**1 核心待判 + 1 未读 = 2**（不是 16）。\n"
        "→ 9 个 UI（YG 说不急）+ 1 未读 + 1 核心待判 = 11 合计。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 核心缺失 6 → 1 · 类型缺失 16 → 11。\n\n"
        "纪律：**检查工具按名字判存在，而名字可不同是目标里的自由度 —— 那个洞装着 5 个假缺口。**\n\n"
        "下一轮：查 `ObservableDictionary`2` 是否 BCL 现成类型（查 .NET 8 BCL 清单）+ 补读第 16 个。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R975" not in h:
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
             for p, k in ((RBLOCK, "R975"), (RSTATUS, "R975"), (RVERDICT, "第 975 轮"), (BACKLOG, "R975")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R975: five of the six core absences are renames, so the sixteen was five too high\n\n"
         "R974 split the sixteen absent types into six core, nine UI and one unread, and left as Unknown how many of the\n"
         " six were only renamed. Checking each one answers it: five are renames.\n\n"
         "Global.Settings with thirty-four members is GlobalSettings.cs, and eight sampled members are all present.\n"
         " CloudflareSolver's members sit in Drivers.cs and CaptchaSolverService.cs rather than in a class of that name, and\n"
         " four sampled members are all there. ImapProvider is ImapMailProvider.cs. Models.Concurrency is ConcurrencyLimit.cs.\n"
         " SmartActions.ActionConfig is SmartActions.cs. Only Helpers.ObservableDictionary, which takes two type parameters,\n"
         " was not found, and the Count member it was checked by is too generic to count as evidence.\n\n"
         "Since the objective says naming may differ, and criterion (a) asks name-level gaps to close in three classes, a\n"
         " rename is not a gap. Those five come off the list rather than sitting on it as placeholders.\n\n"
         "That leaves criterion (a)'s type-absence item with two real remainders: one core type whose status is undecided and\n"
         " one whose name the output truncated. Nine of the eleven are UI, which was explicitly deferred.\n\n"
         "Figures: suite 2186, count 173,952, freshness zero, core absences six to one, total absences sixteen to eleven.\n\n"
         "Unknown: whether ObservableDictionary with two parameters is a BCL type the replica uses as-is, which needs the\n"
         " .NET 8 BCL listing checked; and what the sixteenth absent type is.\n\n"
         "The lesson is that the sixteen was five too high from the outset, because the check decides presence by name while\n"
         " the objective explicitly allows names to differ. A gap between a checker and the clause it serves can hold false\n"
         " gaps, and that one held five for a long time.\n\n"
         "No product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()