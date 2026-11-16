"""Record R858: Task.Type exists and nothing writes it, which is worse than absent."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 复刻件有 `Task.Type` 字段，而**没有任何地方写它**（R858）

**`Cybersole.Core/Models/Tasks.cs` 里有：**

```csharp
public bool MonitorMode { get; set; }
public string Type { get; set; } = string.Empty;
```

**而全 `replica\\src` 里没有一处 `.Type =` 给它赋值**（搜到的 `.Type ==` 全是 `Tls12Client` 的 record 类型与 `JTokenType`）。

**`TaskCombinationRequest`（创建任务的输入）只有 `Store`，没有种类字段：**

```csharp
public required string Store { get; init; }
public string? Url { get; init; }
public bool MonitorMode { get; init; }
// … 没有 Kind / Mode / Type
```

### 所以

| | 镜像 | 复刻件 |
|---|---|---|
| 种类 | **顶层五个 `Start*Flow`，真的有分派** | **`Task.Type` 字段存在，无人写、无人按它分派** |

**死字段比缺字段更糟：它让「种类这一层」看起来存在。**
"""

if "复刻件有 `Task.Type` 字段，而**没有任何地方写它**（R858" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: dead field appended")

BLOCKER = """

---

## 282. `Task.Type` 是个**死字段** —— 比缺字段更糟

> R858。未改产品代码。

### 一、字段在，写入者不在

`Cybersole.Core/Models/Tasks.cs`：

```csharp
public bool MonitorMode { get; set; }
public string Type { get; set; } = string.Empty;
```

**而全 `replica\\src` 没有一处 `.Type =` 给任务赋值。**
（搜到的 `.Type ==` 全是 `Tls12Client` 的 TLS record 类型判断与 `RetailFlows` 的 `JTokenType`。）

**创建路径也不带它：**

```csharp
public sealed class TaskCombinationRequest
{
    public required string Store { get; init; }     // ← 只有店
    public bool MonitorMode { get; init; }
    // … 没有 Kind / Mode / Type
}
```

### 二、所以 R857 的结论要收紧一层

| | 镜像 | 复刻件 |
|---|---|---|
| 种类 | 顶层五个 `Start*Flow`（d__57–61），真的有分派 | **字段存在，无写入者、无按它分派** |

**复刻件有那个**字段**，没有那一**层**。**

### 三、为什么死字段比缺字段更糟

**一个不存在的字段，任何人读代码都知道要新建。
一个存在但没人写的字段，读代码的人会以为「已经有了，只是还没接上」——
于是先去查「为什么 Type 是空的」，而不是「种类层要不要建」。**

**这与 R823 删掉编造 CSRF 兜底、R850 不写 11 个空壳方法是同一条标准的第三种形态：**

| 形态 | 例子 |
|---|---|
| 编造一个值 | R823 的三个 CSRF GUID |
| 写一个有形状没内容的方法 | R850 那 11 个抽签步骤 |
| **留一个没人写的字段** | **R858 的 `Task.Type`** |

**三种都会让「已完成」这句话看起来成立。**

### 四、这一轮不动代码，理由

**删掉 `Task.Type` 是一个动作，但**该不该删**取决于它是不是镜像里真有的字段 ——
如果是（比如镜像的任务模型真有 Type），那它该留着并且该被写；如果不是，它该删。**

**这条没查：镜像里任务模型有没有 Type。**
**而「先删再查」会让下一步失去线索 —— R815 记过这个坑（删掉一个模块可能删掉证据）。**

**所以本轮只记录状态，不删。**

### 五、验证

```
replica\\src\\Cybersole.Core\\Models\\Tasks.cs: public string Type
grep '\\.Type\\s*=' 全 src -> 0 处任务赋值（只有 TLS record 与 JToken 比较）
replica\\src\\Cybersole.Core\\Store\\TaskCombinationBuilder.cs: TaskCombinationRequest 只有 Store
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **镜像的任务模型有没有 Type 字段**：**Unknown** ——
  **这决定 `Task.Type` 该留该删。要查任务模型的字段名（可能在 `0x14337xxxx` 段）。**
- **镜像的 `Start*Flow` 是靠什么分派的**：**Unknown** ——
  五个方法存在，**但派发它们的判断（读任务哪个字段）没查。**
- **`Task.Type` 是谁加进来的、为什么**：**Unknown** ——
  **git log 能查，但那条记录未必说了理由。**

### 七、教训

**R857 我说「复刻件没有种类这一层」。这一轮查得更准：它有字段，没层。**

**两个说法差别很大，因为第一个说法会让人去找「层」在哪，第二个说法会让人去查「字段为什么空」。**

**而这两种后续动作里，只有第二种会走到「镜像里到底有没有这个字段」这个问题上。**
"""

VERDICT = """

---

## 第 858 轮：`Task.Type` 是个死字段 —— 比缺字段更糟

### 字段在，写入者不在

`Tasks.cs`：`public string Type { get; set; } = string.Empty;`
**而全 `replica\\src` 没有一处 `.Type =` 给任务赋值**（搜到的 `.Type ==` 全是 `Tls12Client` 的 record 类型与 `JTokenType`）。

**创建路径也不带它**：`TaskCombinationRequest` 只有 `required string Store`，没有 `Kind` / `Mode` / `Type`。

| | 镜像 | 复刻件 |
|---|---|---|
| 种类 | 顶层五个 `Start*Flow`（d__57–61），真的有分派 | **字段存在，无写入者、无按它分派** |

**→ 复刻件有那个**字段**，没有那一**层**。**

### 为什么死字段比缺字段更糟

> **一个不存在的字段，读代码的人都知道要新建。**
> **一个存在但没人写的字段，读的人会以为「已经有了，只是还没接上」—— 于是去查「为什么 Type 是空的」，而不是「种类层要不要建」。**

**这是同一条标准的第三种形态：**

| 形态 | 例子 |
|---|---|
| 编造一个值 | R823 的三个 CSRF GUID |
| 写一个有形状没内容的方法 | R850 那 11 个抽签步骤 |
| **留一个没人写的字段** | **R858 的 `Task.Type`** |

**三种都会让「已完成」这句话看起来成立。**

### 本轮不动代码，理由

**删不删取决于镜像里任务模型有没有 Type —— 这条没查。而「先删再查」会让下一步失去线索（R815 的坑：删掉一个模块可能删掉证据）。**

### 仍然 Unknown

**镜像任务模型有没有 Type 字段**（**决定留删**）· **镜像的 `Start*Flow` 靠什么分派**（五个方法在，派发判断没查）·
**`Task.Type` 是谁加的、为什么**（git log 能查，但未必记了理由）

### 教训

**「没有种类这一层」和「有字段、没有层」差别很大 —— 前者让人去找「层」，后者让人去查「字段为什么空」。**
**而只有第二种后续动作会走到「镜像里到底有没有这个字段」这个问题上。**
"""

BACKLOG_ADD = """

## 判据 (f) — `Task.Type` 死字段（R858）

**`Tasks.cs`：`public string Type { get; set; }` —— 全 `src` 无一处 `.Type =` 赋给它。**
**`TaskCombinationRequest` 只有 `required string Store`，无种类字段。**

| | 镜像 | 复刻件 |
|---|---|---|
| 种类 | `Start*Flow` ×5（d__57–61）真分派 | **字段在，无写入者** |

### 同一条标准的第三种形态

| 形态 | 例子 |
|---|---|
| 编造一个值 | R823 三个 CSRF GUID |
| 有形状没内容的方法 | R850 那 11 个抽签步骤 |
| **没人写的字段** | **R858 `Task.Type`** |

**→ 三种都让「已完成」看起来成立。**

### 本轮不删的理由

**删不删取决于镜像有没有这个字段 —— 未查。而「先删再查」会删掉线索（R815 的坑）。**

| 仍 Unknown | |
|---|---|
| 镜像任务模型有无 Type | **决定留删** |
| `Start*Flow` 靠什么分派 | 五个方法在，派发判断未查 |
| `Task.Type` 谁加的 | git log 可查，未必记了理由 |

**纪律**：**「没有这一层」vs「有字段、没有层」—— 后者才会让人走到「镜像里到底有没有这个字段」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R858", BLOCKER)
    ensure(RSTATUS, "R858", BLOCKER)
    ensure(RVERDICT, "第 858 轮", VERDICT)
    ensure(BACKLOG, "R858", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R858" not in h:
        h += ("\n## R858 补充 — `Task.Type` 是死字段\n\n"
              "**`Tasks.cs` 有 `public string Type`，全 `src` 无一处 `.Type =` 赋给它。** `TaskCombinationRequest` 只有 `Store`。\n"
              "**→ 复刻件有那个字段，没有那一层。死字段比缺字段更糟**：读代码的人会以为「已有，只是没接上」。\n"
              "**同一条标准的第三种形态**：编造值（R823 CSRF）· 有形状没内容的方法（R850 抽签 11 步）· 没人写的字段（本轮的 Type）。\n"
              "**本轮不删**：删不删取决于镜像有没有这个字段，未查；先删再查会删掉线索（R815）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R858"), (RSTATUS, "R858"), (RVERDICT, "第 858 轮"), (BACKLOG, "R858")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R858: Task.Type is a dead field, which is worse than a missing one\n\n"
         "R857 concluded the replica has no task-kind layer. Checking the model sharpens it: the field exists. Tasks.cs"
         " declares a public string Type, and nothing in the replica assigns it -- every .Type found in a sweep is a TLS"
         " record comparison or a JTokenType check. The creation path does not carry it either: TaskCombinationRequest"
         " has a required Store and a MonitorMode flag and no kind, mode or type at all.\n\n"
         "So the replica has the field and not the layer. That distinction matters more than it looks, because a field"
         " that does not exist sends the next reader to create one, while a field that exists and is never written sends"
         " them to ask why it is empty -- and only the second question leads on to asking whether the image has such a"
         " field at all.\n\n"
         "It is also the third form of a standard this session keeps applying. R823 removed three fabricated CSRF tokens;"
         " R850 declined to write eleven draw steps with invented request shapes; this round finds a declared field with"
         " no writer. Fabricating a value, shipping a method with a shape and no content, and leaving a field nobody"
         " writes all make the claim look done in the same way.\n\n"
         "Nothing was changed this round, and the reason is worth stating. Deleting Task.Type is one line, but whether it"
         " should go depends on whether the image's task model has such a field, which was not checked. Deleting first"
         " and asking afterwards would destroy the clue -- the lesson of R815, where a deletion about to be justified by"
         " evidence would have taken the evidence with it.\n\n"
         "Unknown: whether the image's task model carries a type field, which decides delete-or-keep; how the five"
         " Start-flow methods are dispatched, since the methods exist but the condition that selects among them was not"
         " traced; and who added Task.Type and why, which git log can show though it may not record a reason.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
