"""Record R883: the accessor shape yields a type inventory, and it resolves the Task.Type question."""

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
### `!Getter` 形态给出一份**类型清单**，而它顺手解了悬了六十轮的 `Task.Type`（R883）

**R859 发现过 `<Type>,<Prop>!Getter` 这个形态。这一轮把它枚举完：**

```
2,587 个 (声明类型, 属性名, 访问器) 三元组
  508 个声明类型
存成 docs/baseline/recovered_accessors_by_type.txt（带出处与边界说明）
```

**分布：`Cybersole.Ui.Views.*` 60 个类型 · `Cybersole.Models.*` 22 个 · `Cybersole.SmartActions.*` ·
`Cybersole.Global.Settings`（21 属性）· **`Cybersole.Stores.*` 0 个**。**

### 它解了 `Task.Type`

**R364 起 `BotTask.Task` 的类型一直是 Unknown；R858 发现 `BotTask` 里还有**一个没人写的死字段 `Type`**。**

**现在：**

```
Cybersole.Models.Drop   2 props   Time, Type
```

**`Type` 不在 task 上，**在 `Drop` 上**。而 `Drop` 只有 `Time` 与 `Type` 两个属性 ——
这是一个「什么时候、哪种」的模型。**

**所以 R364 那个 Unknown 的答案不是「`Task.Type` 是什么类型」，
而是「**`Type` 属于另一个对象**」。**

**而 `Cybersole.Models.CreateModel` 8 个属性里**没有 `Type`**：**

```
AccountGroup · AccountSelectionMode · IsEditing · MonitorDelay · MonitorMode
ProxyGroup · RetryDelay · StartTime
```

**所以「任务创建模型」不带类型；类型挂在它关联的 `Drop` 上。**

### 它同时也说明 R504 那堵墙的**准确边界**

**`Cybersole.Stores.*` 在这个清单里是 **0**。**

**所以可见的类型都是运行时为了**绑定**需要物化的成员：Avalonia 控件、视图模型、Models。
**`Stores` 里的流程类不参与绑定，所以它们的属性不产生这种字面量。**

**→ R504 说的「类型信息拿不到」是对的，但边界比当时说的更准：
不是「全都拿不到」，是「**只有参与绑定的成员拿得到**」。**

**而这对 R882 那个 ordinal→类 的问题**没有帮助** —— 因为流程类正在拿不到的那一半里。**

### 顺带拿到的东西

| 类型 | 属性 |
|---|---|
| `Cybersole.Models.Store` | **只有 `Url`** —— 一个很窄的模型 |
| `Cybersole.Global.Settings` | 21 个，含 `BrowserLimit` `MonitorConcurrency` `QueuePresentation` `SmartActions` `TaskGroupOrder` |
| `Cybersole.Models.TaskGroup` | 9 个，含 `CaptchaSource` `CheckoutLimit` `CloudflareSolverId` `ProfileLimit` `TotalCheckouts` `TotalDeclines` `UsageExpiry` |
| `Cybersole.Models.BaseCheckout` | `Properties` · `Timestamp` |
"""

if "`!Getter` 形态给出一份**类型清单**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R883 appended")

BLOCKER = """

---

## 307. `!Getter` 枚举出 508 个类型；而它把 `Task.Type` 这个悬案解了

> R883。**新增基线文件，不改产品代码。**

### 一、枚举结果

```
2,587 个 (声明类型, 属性名, 访问器) 三元组 · 508 个声明类型
-> replica/docs/baseline/recovered_accessors_by_type.txt（带出处与边界说明）
```

**分布：`Cybersole.Ui.Views.*` 60 · `Cybersole.Models.*` 22 · `Cybersole.SmartActions.*` ·
`Cybersole.Global.Settings` 21 属性 · **`Cybersole.Stores.*` 0**。**

### 二、`Task.Type` 悬案解了

**R364 起 `BotTask.Task` 的类型是 Unknown；R858 还发现 `BotTask` 里有个没人写的死字段 `Type`。**

```
Cybersole.Models.Drop   2 props   Time, Type
```

**`Type` 不在 task 上，在 `Drop` 上。而 `Drop` **只有** `Time` 与 `Type`。**

**所以那个 Unknown 的答案不是「`Task.Type` 是什么类型」，而是**「`Type` 属于另一个对象」**。**

**而 `CreateModel` 的 8 个属性里**没有 `Type`**：
`AccountGroup` · `AccountSelectionMode` · `IsEditing` · `MonitorDelay` · `MonitorMode` ·
`ProxyGroup` · `RetryDelay` · `StartTime`。**

**→ 任务创建模型不带类型；类型挂在关联的 `Drop` 上。**

**这是六十轮的 Unknown 变成「换个对象找」的一句话。**

### 三、R504 那堵墙的边界现在准确了

**`Cybersole.Stores.*` 在这个清单里是 **0**。**

**可见类型全是运行时为了**绑定**要物化的成员：Avalonia 控件、视图模型、Models。
**`Stores` 里的流程类不参与绑定，所以不产生这种字面量。** **

**所以 R504 是对的，但边界比当时更准：不是「全都拿不到」，
是「**只有参与绑定的成员拿得到**」。**

**而这对 R882 的 ordinal→类 问题**没有帮助** —— 流程类正在拿不到的那一半里。**

### 四、顺带拿到的模型

| 类型 | 属性 |
|---|---|
| `Cybersole.Models.Store` | **只有 `Url`** |
| `Cybersole.Global.Settings` | 21：`BrowserLimit` `MonitorConcurrency` `QueuePresentation` `SmartActions` `TaskGroupOrder` `BackupInterval` … |
| `Cybersole.Models.TaskGroup` | 9：`CaptchaSource` `CheckoutLimit` `CloudflareSolverId` `LinkedDelays` `ProfileLimit` `TotalCheckouts` `TotalDeclines` `UsageExpiry` `MonitorDelay` |
| `Cybersole.Models.BaseCheckout` | `Properties` · `Timestamp` |

**`TaskGroup` 那 9 个属性对复刻件直接有用：`CaptchaSource` / `CloudflareSolverId` 是优先级 ② 的，
`CheckoutLimit` / `ProfileLimit` 是调度层的。**

### 五、验证

```
idautils.Strings() 全量 + 正则 ([A-Za-z_][\w.<>`+\[\], ]*?),([A-Za-z_][\w.<>`]*?)!(Getter|Setter|Property)
  -> 2587 raw / 2587 distinct triples / 508 types
写入 replica/docs/baseline/recovered_accessors_by_type.txt（含 11 行出处与边界说明头）
Cybersole.Stores.*  -> 0 types
Cybersole.Models.Drop -> Time, Type
本轮未改产品代码；套件沿用 1780
```

### 六、仍然 Unknown

- **`Drop` 与 task 的关联方式**：**Unknown** ——
  **`Drop` 有 `Time`/`Type`，`CreateModel` 有 `StartTime`，两者怎么连起来没有证据。**
- **`Drop.Type` 的实际取值**：**Unknown** ——
  **名字只说是「类型」，而 14 个 `FlowKind` 是否就是它的取值，未证。**
- **流程类为什么不在这个清单里**：**Inference** ——
  **「不参与绑定所以不物化」是我从「Stores 为 0」反推的，而反推不是观察。**

### 七、教训

**这个形态 R859 就发现了，我当时只用一个类型（`AccountStoreType`）验证了一下，然后走了。
六十轮后才回来把它枚举完。**

**代价是这六十轮里 `Task.Type` 一直是 Unknown、R504 的边界一直说得太宽。**

**所以「发现一个形态」和「把它枚举完」是两件事，而我只做了前一件。
一条正则、一次全量扫，成本十分钟 —— 而我把它留了六十轮。**
"""

VERDICT = """

---

## 第 883 轮：`!Getter` 枚举出 508 个类型，而它把 `Task.Type` 悬案解了

### 枚举

```
2,587 个 (声明类型, 属性, 访问器) 三元组 · 508 个声明类型
-> replica/docs/baseline/recovered_accessors_by_type.txt（含出处与边界说明）
```

**`Cybersole.Ui.Views.*` 60 · `Cybersole.Models.*` 22 · **`Cybersole.Stores.*` 0**。**

### `Task.Type` 悬案解了

**R364 起 `BotTask.Task` 的类型是 Unknown；R858 发现还有个没人写的死字段 `Type`。**

```
Cybersole.Models.Drop   2 props   Time, Type
```

**`Type` 不在 task 上，在 `Drop` 上；而 `Drop` 只有这两个属性。**

> **那个 Unknown 的答案不是「`Task.Type` 是什么类型」，而是「**`Type` 属于另一个对象**」。**
> **而 `CreateModel` 的 8 个属性里没有 `Type` → 任务创建模型不带类型，类型挂在关联的 `Drop` 上。**

### R504 那堵墙的边界现在准确了

**`Cybersole.Stores.*` 是 0。可见类型全是运行时为**绑定**要物化的成员。**

> **R504 是对的，但边界更准：不是「全都拿不到」，是「**只有参与绑定的成员拿得到**」。**
> **而这对 R882 的 ordinal→类 问题没有帮助 —— 流程类正在拿不到的那一半里。**

### 顺带拿到的模型

**`Store` 只有 `Url`** · **`Global.Settings` 21 个**（`BrowserLimit` `MonitorConcurrency` `QueuePresentation` `SmartActions` `TaskGroupOrder`…）·
**`TaskGroup` 9 个**（`CaptchaSource` `CheckoutLimit` `CloudflareSolverId` `ProfileLimit` `TotalCheckouts` `TotalDeclines` `UsageExpiry`…）
**→ `CaptchaSource`/`CloudflareSolverId` 直接属于优先级 ②，`CheckoutLimit`/`ProfileLimit` 属于调度层。**

### 仍然 Unknown

**`Drop` 与 task 的关联方式** · **`Drop.Type` 的取值是否就是 14 个 `FlowKind`** ·
**流程类为何不在此清单**（Inference：「不参与绑定所以不物化」是反推，不是观察）

### 教训

> **这个形态 R859 就发现了，我当时只用一个类型验证了一下就走了。六十轮后才回来枚举完。**
> **代价是这六十轮里 `Task.Type` 一直是 Unknown、R504 的边界一直说得太宽。**
> **「发现一个形态」和「把它枚举完」是两件事，而我只做了前一件 —— 一条正则、一次全量扫，成本十分钟，我留了六十轮。**
"""

BACKLOG_ADD = """

## 判据 — `!Getter` 枚举：508 个类型（R883）

**新增基线 `replica/docs/baseline/recovered_accessors_by_type.txt`**：`2,587` 三元组 / `508` 类型，带出处与边界说明头。

**分布**：`Cybersole.Ui.Views.*` 60 · `Cybersole.Models.*` 22 · **`Cybersole.Stores.*` 0**

### `Task.Type` 悬案解了（R364 → R883）

```
Cybersole.Models.Drop   2 props   Time, Type
Cybersole.Models.CreateModel 8 props  AccountGroup … StartTime（无 Type）
```

**→ `Type` 属于 `Drop`，不属于 task。那个 Unknown 的答案是「换个对象找」。**

### R504 边界更正

**`Stores` 为 0 → R504 不是「全都拿不到」，是「**只有参与绑定的成员拿得到**」。
→ 对 R882 的 ordinal→类 无帮助（流程类在拿不到的那一半）。**

### 顺带

**`Store` 只有 `Url`** · **`Global.Settings` 21** · **`TaskGroup` 9**（`CaptchaSource`/`CloudflareSolverId` 属优先级 ②，`CheckoutLimit`/`ProfileLimit` 属调度层）

| 仍 Unknown | |
|---|---|
| `Drop` 与 task 怎么关联 | `CreateModel.StartTime` vs `Drop.Time` 未连 |
| `Drop.Type` 取值是否 = 14 个 `FlowKind` | 未证 |
| 流程类为何不在清单 | Inference（反推） |

**纪律**：**发现一个形态 ≠ 把它枚举完。R859 到 R883 隔了六十轮，成本十分钟。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R883", BLOCKER)
    ensure(RSTATUS, "R883", BLOCKER)
    ensure(RVERDICT, "第 883 轮", VERDICT)
    ensure(BACKLOG, "R883", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R883" not in h:
        h += ("\n## R883 补充 — `!Getter` 枚举：508 个类型（**新增基线文件，未改产品代码**）\n\n"
              "**`replica/docs/baseline/recovered_accessors_by_type.txt`**：2,587 三元组 / 508 类型，带出处与边界头。"
              "分布 `Ui.Views` 60 · `Models` 22 · **`Stores` 0**。\n"
              "**`Task.Type` 悬案解了**：`Cybersole.Models.Drop { Time, Type }` —— **`Type` 属于 `Drop` 不属于 task**；`CreateModel` 8 属性无 `Type`。\n"
              "**R504 边界更正**：不是「全都拿不到」，是「**只有参与绑定的成员拿得到**」（`Stores` 为 0 即证）。"
              "**对 R882 的 ordinal→类 无帮助。**\n"
              "**顺带**：`Store` 只有 `Url`；`Global.Settings` 21；**`TaskGroup` 9（含 `CaptchaSource`/`CloudflareSolverId` → 优先级 ②）**。\n"
              "**纪律：发现一个形态 ≠ 把它枚举完（R859 → R883 隔六十轮，成本十分钟）。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R883"), (RSTATUS, "R883"), (RVERDICT, "第 883 轮"), (BACKLOG, "R883")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R883: enumerating the accessor shape yields 508 types and settles where Task.Type lives\n\n"
         "R859 found that properties appear as <DeclaringType>,<Property>!Getter, verified it on one type and moved on.\n"
         " Sixty rounds later the shape has been enumerated: 2587 distinct triples over 508 declaring types, written to\n"
         " replica/docs/baseline/recovered_accessors_by_type.txt with a header stating provenance and limits.\n\n"
         "It settles a question open since R364. BotTask.Task has had an unknown type that whole time, and R858 found a\n"
         " dead Type field on BotTask that nothing writes. The accessor inventory shows Drop with exactly two\n"
         " properties, Time and Type, and shows CreateModel's eight properties containing no Type at all. So the answer\n"
         " to that unknown is not what type Task.Type has but that Type belongs to a different object -- the drop a task\n"
         " is created for carries the time and the type, and the creation model carries neither.\n\n"
         "It also sharpens R504's ceiling. Cybersole.Stores appears zero times in the inventory, because the visible\n"
         " members are those the runtime had to materialise for binding: Avalonia controls, view models and Models. Flow\n"
         " classes take part in no binding and therefore produce no such literal. So R504's conclusion holds, with a\n"
         " narrower boundary than I gave it: not that type information is unavailable, but that only binding members\n"
         " are available. Which is also why this does not help R882 -- flow classes sit in the unavailable half.\n\n"
         "Useful by-products: Store has a single property, Url; Global.Settings has twenty-one including BrowserLimit,\n"
         " MonitorConcurrency, QueuePresentation, SmartActions and TaskGroupOrder; and TaskGroup has nine including\n"
         " CaptchaSource and CloudflareSolverId, which belong to the anti-bot priority, and CheckoutLimit and\n"
         " ProfileLimit, which belong to scheduling.\n\n"
         "Unknown: how a Drop attaches to a task, since Drop has Time and CreateModel has StartTime and nothing connects\n"
         " them; whether Drop.Type's values are the fourteen FlowKinds; and why flow classes are absent from the\n"
         " inventory, where 'they take part in no binding' is my inference from their absence rather than an\n"
         " observation.\n\n"
         "The lesson is the gap between finding a shape and enumerating it. R859 found this one, checked a single type\n"
         " and left; the cost of finishing was one regex and one full scan, ten minutes, and it stayed unspent for sixty\n"
         " rounds during which Task.Type was unknown and R504's ceiling was stated too widely.\n\n"
         "New baseline file; no product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
