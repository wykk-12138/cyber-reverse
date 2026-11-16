"""Record R861: BotTask.Task was already open since R364, and the loop closes there."""

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
### `BotTask.Task` 的类型：**R364 已经记为未定项**（R861）

**复刻件 `Tasks.cs` 里就写着：**

```
R364: the binding table names six more members on this model. Five have an inferable type; "Task"'
type could be an engine handle, an interface or a string id, and the name collides with System...,
so it stays named in docs/BINDING_BACKLOG.md.
```

**所以这不是新问题 —— 它从 R364 起就在 `BINDING_BACKLOG.md` 里。**

### 这四轮追的东西是同一批

| 轮 | 我在追 | 实际上 |
|---|---|---|
| R857 | 镜像顶层是「种类」还是「站」 | 是种类（5 个 `Start*Flow`） |
| R858 | `Task.Type` 是死字段 | 是，0 处写入 |
| R859 | 镜像有没有 `Type` | `CreateInputModel` 13 属性里没有 |
| R860 | `Type` 在哪个类型上 | 在 `BaseCheckout` 上，复刻件已有 |
| **R861** | **`BotTask.Task` 是什么类型** | **R364 已记为未定项** |

**而 `Task.Type` 与 `BotTask.Task` 是同一件事的两面：**
**`BotTask` 上有个成员叫 `Task`，类型未定；而 `Task.Type` 是复刻件多加的一个无人写的字段。**
**如果 `BotTask.Task` 的类里真有 `Type`，那复刻件那行就不是冗余，是**放错了位置**。**

**所以 `Task.Type` 删不删，取决于 `BotTask.Task` 的类型 —— 而那一条 R364 就没定。**
"""

if "R364 已经记为未定项**（R861" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R364 loop-closing appended")

BLOCKER = """

---

## 285. 追了四轮的东西回到 **R364 就记着的未定项**

> R861。未改产品代码。

### 一、答案在复刻件自己的注释里

`Cybersole.Core/Models/Tasks.cs`：

```
R364: the binding table names six more members on this model. Five have an inferable type; "Task"'s
type could be an engine handle, an interface or a string id, and the name collides with System...,
so it stays named in docs/BINDING_BACKLOG.md.
```

**所以 `BotTask.Task` 的类型从 R364 起就是**明写的未定项**，不是我这轮才发现的问题。**

### 二、而它和 `Task.Type` 是同一件事的两面

| 成员 | 状态 |
|---|---|
| `BotTask.Task` | **类型未定**（R364 记为 Unknown） |
| `Task.Type` | **复刻件多加的字段，0 处写入**（R858） |

**关键在于：**

> **如果 `BotTask.Task` 的类里真有 `Type`，那复刻件那行就不是「冗余」，是「放错了位置」。**

**所以 R858 的「留还是删」这个二选一又不够 —— 第三种可能是「挪」。**

**而选哪个取决于 `BotTask.Task` 的类型，也就是 R364 那条未定项。**

### 三、这四轮的形状

| 轮 | 我追的 | 结论 |
|---|---|---|
| R857 | 顶层是种类还是站 | 种类（5 个 `Start*Flow`） |
| R858 | `Task.Type` 是不是死字段 | 是，0 处写入 |
| R859 | 镜像有没有 `Type` | 创建表单 13 属性里没有 |
| R860 | `Type` 在哪个类型上 | `BaseCheckout`，复刻件已有 |
| **R861** | **`BotTask.Task` 是什么类型** | **R364 未定项** |

**四轮下来，每一轮都得到一个正确但更窄的结论，而链条的末端指向一个 R364 就记下的 Unknown。**

**这不是白走 —— R857–R860 的结论都是新的、可复算的（顶层维度、死字段、13 属性、模型 schema 齐备）。
但**这一轮该做的是先读自己的 backlog**，而不是再从镜像查一遍。**

### 四、R843 的规则我用错了地方

**R843 立的规则是「每批裁决前先 grep 仓里有没有同名分析文件」，我用它找 `*StepMap.cs`，很有效。**

**而 `BINDING_BACKLOG.md` 本身就是那个文件 —— 它记着所有未结案项。**
**这四轮我一直在从 METRICS/BLOCKERS/HANDOFF 读现状，但**没查 backlog 里「Task 的类型」这一条**。**
**规则该是：查一个成员之前，先在 backlog 里搜它的名字。**

### 五、验证

```
replica\\src\\Cybersole.Core\\Models\\Tasks.cs
  'R364: the binding table names six more members on this model …"Task"'s type could be an engine handle,
   an interface or a string id … so it stays named in docs/BINDING_BACKLOG.md.'
ida.py str Cybersole.Models. -> 7 个类型名（纯类型名搜索，比属性语法的 13 个更弱）
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`BotTask.Task` 的类型**：**Unknown，R364 起就是 —— 要证它得走类型元数据（MethodTable / 字段描述符），
  而那条路 R828 已记未通。**
- **`Task.Type` 是删是挪**：**Unknown** —— 取决于上一条。
- **那六个成员里另外五个是什么**：**Unknown** —— 注释只说「五个类型可推」，没列名字。

### 七、教训

**「先查 backlog」这条，是我这个会话里第五次学到同一类教训的形状：**

| 轮 | 本该先查的 |
|---|---|
| R843 | `StoreFlowSteps.cs` |
| R845 | `StoreFlow` 的 165 个虚步骤 |
| R846 | `ScapiAppPath.cs` |
| R847 | `JohnLewisStepMap.cs` / `DemandwareStepMap.cs` |
| **R861** | **`BINDING_BACKLOG.md` 里「Task 的类型」那一条** |

**前四次是「没读仓里的分析文件」，这次是「没读自己的待办清单」。**
**而 backlog 就是为我这种遗忘准备的 —— 我建了它，却在查一个它明确记着的成员时没打开它。**
"""

VERDICT = """

---

## 第 861 轮：追了四轮的东西回到 R364 就记着的未定项

### 答案在复刻件自己的注释里

`Tasks.cs`：
```
R364: the binding table names six more members on this model. Five have an inferable type; "Task"'s
type could be an engine handle, an interface or a string id … so it stays named in docs/BINDING_BACKLOG.md.
```

**`BotTask.Task` 的类型从 R364 起就是明写的未定项。**

### 而它和 `Task.Type` 是同一件事的两面

| 成员 | 状态 |
|---|---|
| `BotTask.Task` | **类型未定**（R364） |
| `Task.Type` | **复刻件多加，0 处写入**（R858） |

> **如果 `BotTask.Task` 的类里真有 `Type`，那复刻件那行不是「冗余」，是「放错了位置」。**
> **→ R858 的二选一又不够，第三种可能是「挪」。**

### 这四轮的形状

| 轮 | 追的 | 结论 |
|---|---|---|
| R857 | 顶层是种类还是站 | 种类（5 个 `Start*Flow`） |
| R858 | `Task.Type` 是不是死字段 | 是，0 处写入 |
| R859 | 镜像有没有 `Type` | 创建表单 13 属性里没有 |
| R860 | `Type` 在哪个类型上 | `BaseCheckout`，复刻件已有 |
| **R861** | **`BotTask.Task` 是什么类型** | **R364 未定项** |

**四轮每轮都得到正确但更窄的结论，链条末端指向一个 R364 就记下的 Unknown。**
**R857–R860 的结论都是新的、可复算的 —— 但**这一轮该做的是先读自己的 backlog**。**

### R843 的规则我用错了地方

**R843 立的是「裁决前先 grep 仓里有没有同名分析文件」，我用它找 `*StepMap.cs`，有效。**

> **而 `BINDING_BACKLOG.md` 本身就是那个文件 —— 它记着所有未结案项。**
> **规则该是：查一个成员之前，先在 backlog 里搜它的名字。**

### 仍然 Unknown

**`BotTask.Task` 的类型**（R364 起；要证得走 MethodTable，R828 已记未通）· **`Task.Type` 是删是挪**（取决于上一条）·
**那六个成员里另外五个是什么**（注释只说「五个可推」，没列名字）

### 教训

| 轮 | 本该先查的 |
|---|---|
| R843 | `StoreFlowSteps.cs` |
| R845 | `StoreFlow` 165 虚步骤 |
| R846 | `ScapiAppPath.cs` |
| R847 | `JohnLewisStepMap.cs` / `DemandwareStepMap.cs` |
| **R861** | **`BINDING_BACKLOG.md` 里「Task 的类型」那一条** |

**前四次是「没读仓里的分析文件」，这次是「没读自己的待办清单」。**
**而 backlog 就是为我这种遗忘准备的 —— 我建了它，却在查一个它明确记着的成员时没打开它。**
"""

BACKLOG_ADD = """

## 判据 (a)/(f) — `BotTask.Task` 类型是 R364 未定项（R861）

**`Tasks.cs` 注释：**
```
R364: the binding table names six more members on this model. Five have an inferable type; "Task"'s
type could be an engine handle, an interface or a string id … so it stays named in docs/BINDING_BACKLOG.md.
```

**→ 这是既有未定项，不是新问题。**

### 与 `Task.Type` 的关系

**若 `BotTask.Task` 的类里真有 `Type`，复刻件那行不是「冗余」，是「**放错了位置**」→ 第三种处理：「挪」。**

### 四轮链条

R857 顶层是种类 → R858 `Task.Type` 死字段 → R859 创建表单无 Type → R860 `Type` 在 `BaseCheckout` → **R861 回到 R364 未定项**

| 仍 Unknown | |
|---|---|
| `BotTask.Task` 的类型 | R364 起；需 MethodTable（R828 未通） |
| `Task.Type` 删还是挪 | 取决于上一条 |
| 那六个成员里另外五个 | 注释未列名字 |

**纪律（第五次同类教训）**：**查一个成员之前，先在 `BINDING_BACKLOG.md` 里搜它的名字。**
**前四次是没读仓里的分析文件，这次是没读自己的待办清单。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R861", BLOCKER)
    ensure(RSTATUS, "R861", BLOCKER)
    ensure(RVERDICT, "第 861 轮", VERDICT)
    ensure(BACKLOG, "R861", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R861" not in h:
        h += ("\n## R861 补充 — 回到 R364 未定项\n\n"
              "**`BotTask.Task` 的类型自 R364 起就记在 `BINDING_BACKLOG.md`** —— `Tasks.cs` 注释原话："
              "「type could be an engine handle, an interface or a string id」。\n"
              "**而它与 `Task.Type` 是一件事两面：若 `BotTask.Task` 的类里真有 Type，复刻件那行不是冗余，是**挪错了位置**。**\n"
              "**规则（第五次同类教训）：查一个成员之前，先在 `BINDING_BACKLOG.md` 里搜它的名字。** "
              "前四次是没读仓里的分析文件，这次是没读自己的待办清单。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R861"), (RSTATUS, "R861"), (RVERDICT, "第 861 轮"), (BACKLOG, "R861")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R861: four rounds of narrowing end at an unknown recorded back in R364\n\n"
         "Chasing BotTask.Task's type turned up the answer inside the replica's own source. Tasks.cs carries a comment"
         " from R364 recording that the binding table names six more members on this model, that five have inferable"
         " types, and that Task's type could be an engine handle, an interface or a string id, so it was left named in"
         " BINDING_BACKLOG.md. The question was answered before I asked it.\n\n"
         "That also changes what Task.Type is. R858 framed it as keep-or-delete, and R860 found the image's Type lives on"
         " BaseCheckout, which the replica already has. But if whatever class BotTask.Task resolves to carries a Type of"
         " its own, then the unwritten field in Tasks.cs is neither redundant nor correct -- it is in the wrong place,\n"
         " and the third option is to move it rather than keep or delete it. Which of the three is right depends on a"
         " type that R364 already marked unsettled.\n\n"
         "The four rounds did produce new, checkable results: the image's top layer is task kind rather than store,"
         " Task.Type has no writer, CreateInputModel has thirteen properties and no Type, and the model schema matches"
         " across BotTask, BaseCheckout, TaskGroup and WebTask. What they did not do was start from the backlog, and the"
         " end of the chain was sitting in it the whole time.\n\n"
         "This is the fifth member of a family of lessons. R843 should have started from StoreFlowSteps, R845 from"
         " StoreFlow's virtual steps, R846 from ScapiAppPath, R847 from the two step maps, and this round from"
         " BINDING_BACKLOG. The first four were failures to read analysis files the repository already held; this one is"
         " a failure to read my own open-items list. The rule that covers all five is short: before investigating a"
         " member, search the backlog for its name.\n\n"
         "Unknown: BotTask.Task's type, open since R364 and requiring the MethodTable route R828 recorded as unbuilt;"
         " whether Task.Type should be deleted or moved, which waits on that; and what the other five inferable members"
         " are, since the comment says five can be inferred without naming them.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
