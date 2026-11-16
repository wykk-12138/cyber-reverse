"""Record R859: CreateInputModel's thirteen properties and no Type -- with its boundary stated."""

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
### `CreateInputModel` 的 13 个属性里**没有 `Type`**（R859）

**镜像里属性以 `声明类型,程序集.属性名!访问器` 的形式出现，可以逐条列出来。
`Cybersole.Models.CreateInputModel` 扫到 13 个：**

```
AutoQuantity · Color · Currency · Input · MaxPrice · MinPrice · Minus
Plus · PriceCheckVisible · Quantity · Sizes · Symbol · TogglePriceCheck
```

**没有 `Type`。**

### 边界：这是**创建表单的输入模型**，不一定是任务模型本身

**所以这一步能说：镜像的创建表单里没有「种类」这个输入项。**
**不能说：镜像的任务对象没有 Type。**

**而这也回答了一个相关问题 —— 五个 `Start*Flow` 的种类不是在创建表单里选的。**

### 顺带：复刻件的任务字段是混合物

| 字段 | 镜像里有？ |
|---|---|
| `MonitorMode` | **有**（`get_MonitorMode` @ `0x143300b4a`） |
| `PriceCheck` | **有**（`get_PriceCheck` @ `0x143303724`） |
| `MultiCart` | **有**（`get_MultiCart` / `set_MultiCart` @ `0x1432fd992`） |
| `NameTemplate` | **0 命中** —— 复刻件自己起的名字 |
| `CheckoutDelay` | **0 命中** —— 同上 |
| **`Type`** | **`CreateInputModel` 里没有；任务模型未查** |
"""

if "的 13 个属性里**没有 `Type`**（R859" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: CreateInputModel appended")

BLOCKER = """

---

## 283. `CreateInputModel` 的 13 个属性里没有 `Type`；而**种类也不是在创建表单里选的**

> R859。未改产品代码。

### 一、镜像里的属性可以逐条列

**镜像里属性以 `Cybersole.Models.CreateInputModel,Cybersole.Core.<属性名>!Getter` 的形式出现。
沿这个模式扫，`CreateInputModel` 得到 13 个属性：**

```
AutoQuantity · Color · Currency · Input · MaxPrice · MinPrice · Minus
Plus · PriceCheckVisible · Quantity · Sizes · Symbol · TogglePriceCheck
```

**没有 `Type`。**

### 二、边界要说清

**这是**创建表单的输入模型**，不一定是任务对象本身。**

| 能说 | 不能说 |
|---|---|
| 镜像的创建表单里没有「种类」这个输入项 | 镜像的任务对象没有 Type |

**所以 R858 那个「留还是删」还没答完 —— 但它推进了一步：
`Task.Type` 不是从 `CreateInputModel` 来的。**

### 三、一个附带结论，对 R857 有用

**五个 `Start*Flow` 的种类，**不是**在创建表单里选的。**

**那它在哪选？两种可能：**
1. **任务创建后按别的字段派发**（如 store 决定种类）
2. **种类是创建时的另一个入口**（不是这个表单）

**这解释了复刻件为什么没有种类层却也能跑：它的创建表单与镜像一样不含种类，
所以复刻件是从「没有种类输入」这个正确起点，走向了「也没有种类派发」这个错误终点。**

### 四、顺带：复刻件的任务字段是混合物

| 字段 | 镜像 |
|---|---|
| `MonitorMode` | **有**（`get_MonitorMode` @ `0x143300b4a`） |
| `PriceCheck` | **有**（`get_PriceCheck` @ `0x143303724`） |
| `MultiCart` | **有**（`get_MultiCart` / `set_MultiCart` @ `0x1432fd992`） |
| `NameTemplate` | **0** —— 复刻件自造 |
| `CheckoutDelay` | **0** —— 复刻件自造 |
| `Type` | `CreateInputModel` 无；任务对象未查 |

**所以那个模型的字段一半有出处、一半是自造。而自造的那两个（`NameTemplate` / `CheckoutDelay`）
是复刻件为了自己的批量创建功能加的，不是镜像的行为。**
**这在「功能 1:1」下是一个独立的小问题 —— 它们在复刻件里有实际用途，但**多出来的功能也是一种不相等**。**

### 五、验证

```
ida.py str CreateInputModel  -> 27 matches
  按 '<类型>,Cybersole.Core.<名>!Getter/Setter' 抽出 13 个属性；无 Type
ida.py str get_MonitorMode   -> 1（0x143300b4a）
ida.py str get_PriceCheck    -> 3
ida.py str NameTemplate      -> 0
ida.py str CheckoutDelay     -> 0
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **镜像的任务对象（不是创建表单）有没有 Type**：**Unknown** ——
  **要找任务对象的类型名。`Cybersole.Ui.Views.Tasks.Modals.TaskDetail…` 与 `TaskGroup…` 是线索。**
- **种类按什么派发**：**Unknown** ——
  **创建表单不含种类（本轮 Observation），所以派发依据是别的字段。**
- **复刻件那两个自造字段要不要留**：**Unknown** ——
  **它们支撑 `TaskCombinationBuilder` 的批量创建，而那个功能镜像里有没有没查。**

### 七、教训

**R858 我问「镜像有没有 Type」，问得太粗 —— `Type` 这个词在镜像里有 27 个变体（`get_TypeId` / `get_TypeOfT` …），
直接搜等于没搜。**

**这一轮换成「先找到字段的书写模式（`类型,程序集.名字!访问器`），再按模式抽表」，才得到 13 个属性这样一个可核对的答案。**

**找到一个领域里的**语法**，比搜一个词有用 —— 而 AGENTS.md §2.7 说的「先问有几种写法」，
说的就是这个，只是我这次才真的照做。**
"""

VERDICT = """

---

## 第 859 轮：`CreateInputModel` 的 13 个属性里没有 `Type`

### 镜像里的属性可以逐条列

**属性以 `Cybersole.Models.CreateInputModel,Cybersole.Core.<名>!Getter` 的形式出现。
按这个模式扫，得到 13 个属性：**

```
AutoQuantity · Color · Currency · Input · MaxPrice · MinPrice · Minus
Plus · PriceCheckVisible · Quantity · Sizes · Symbol · TogglePriceCheck
```

**没有 `Type`。**

### 边界

| 能说 | 不能说 |
|---|---|
| 镜像的创建表单里没有「种类」这个输入项 | 镜像的任务对象没有 Type |

### 一个附带结论，对 R857 有用

> **五个 `Start*Flow` 的种类，**不是**在创建表单里选的。**

**这解释了复刻件为什么没有种类层却也能跑：它的创建表单与镜像一样不含种类 ——
所以它是从「没有种类输入」这个**正确起点**，走向了「也没有种类派发」这个**错误终点**。**

### 顺带：复刻件的任务字段是混合物

| 字段 | 镜像 |
|---|---|
| `MonitorMode` · `PriceCheck` · `MultiCart` | **有**（`get_MonitorMode` @`0x143300b4a` 等） |
| `NameTemplate` · `CheckoutDelay` | **0 命中 —— 复刻件自造** |
| `Type` | `CreateInputModel` 无；任务对象未查 |

**那两个字自造字段支撑复刻件自己的批量创建 —— 而在「功能 1:1」下，**多出来的功能也是一种不相等**。**

### 仍然 Unknown

**镜像的任务对象有没有 Type**（线索：`TaskDetail…` / `TaskGroup…` 类型名）· **种类按什么派发**（创建表单不含种类，所以依据是别的字段）·
**复刻件那两个自造字段要不要留**（它们支撑 `TaskCombinationBuilder`，而那个功能镜像里有没有没查）

### 教训

> **R858 我问「镜像有没有 Type」，问得太粗 —— `Type` 在镜像里有 27 个变体（`get_TypeId` / `get_TypeOfT` …），直接搜等于没搜。**
> **这一轮换成「先找到字段的书写模式，再按模式抽表」，才得到 13 个属性这样一个可核对的答案。**
> **找到一个领域里的**语法**，比搜一个词有用 —— 这正是 §2.7 说的「先问有几种写法」。**
"""

BACKLOG_ADD = """

## 判据 (f) — `CreateInputModel` 13 属性无 Type（R859）

**按镜像的属性书写模式 `类型,程序集.名字!访问器` 抽表：**
`CreateInputModel` = `AutoQuantity` `Color` `Currency` `Input` `MaxPrice` `MinPrice` `Minus` `Plus`
`PriceCheckVisible` `Quantity` `Sizes` `Symbol` `TogglePriceCheck` —— **13 个，无 `Type`。**

**边界**：这是**创建表单输入模型**，不是任务对象本身。

### 附带结论（对 R857）

> **五个 `Start*Flow` 的种类不是在创建表单里选的。**

**→ 复刻件从「没有种类输入」（正确）走到「也没有种类派发」（错误）。**

### 复刻件任务字段是混合物

| 有出处 | `MonitorMode` · `PriceCheck` · `MultiCart` |
|---|---|
| **自造** | **`NameTemplate` · `CheckoutDelay`（0 命中）** |

**→ 「功能 1:1」下，多出来的功能也是一种不相等。**

| 仍 Unknown | |
|---|---|
| 镜像任务对象有无 Type | 线索 `TaskDetail…` / `TaskGroup…` |
| 种类按什么派发 | 创建表单不含种类，依据是别的字段 |
| 两个自造字段留不留 | 支撑 `TaskCombinationBuilder`；镜像有无此功能未查 |

**纪律**：**找一个领域的**语法**比搜一个词有用 —— `Type` 有 27 个变体，直接搜等于没搜。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R859", BLOCKER)
    ensure(RSTATUS, "R859", BLOCKER)
    ensure(RVERDICT, "第 859 轮", VERDICT)
    ensure(BACKLOG, "R859", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R859" not in h:
        h += ("\n## R859 补充 — CreateInputModel 13 属性无 Type\n\n"
              "**按镜像的属性书写模式 `类型,程序集.名字!访问器` 抽表，`CreateInputModel` 有 13 个属性，无 `Type`。**\n"
              "**边界：那是创建表单输入模型，不是任务对象。**\n"
              "**附带结论：五个 `Start*Flow` 的种类**不是在创建表单里选的** —— 复刻件从「没有种类输入」（正确）走到「没有种类派发」（错误）。**\n"
              "**复刻件任务字段一半有出处（`MonitorMode`/`PriceCheck`/`MultiCart`），一半自造（`NameTemplate`/`CheckoutDelay` 0 命中）。**\n"
              "**教训：找领域的**语法**比搜一个词有用 —— `Type` 有 27 个变体，直接搜等于没搜。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R859"), (RSTATUS, "R859"), (RVERDICT, "第 859 轮"), (BACKLOG, "R859")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R859: CreateInputModel has thirteen properties and Type is not one of them\n\n"
         "R858 asked whether the image has a Type field and asked it too coarsely, since Type appears in twenty-seven"
         " variant accessor names. This round finds the syntax instead. Properties appear in the image as"
         " declaring-type,assembly.property!accessor, so extracting along that pattern enumerates a model. For"
         " Cybersole.Models.CreateInputModel the table has thirteen entries: AutoQuantity, Color, Currency, Input,"
         " MaxPrice, MinPrice, Minus, Plus, PriceCheckVisible, Quantity, Sizes, Symbol and TogglePriceCheck. No Type.\n\n"
         "The boundary matters. CreateInputModel is the create form's input model, not the task object, so what this"
         " establishes is that the image's create form has no kind input. It does not establish that the task object"
         " lacks a Type.\n\n"
         "It does settle something adjacent that bears on R857: the five Start-flow kinds are not chosen in the create"
         " form. And that reframes the replica's problem. Its create form also has no kind input, matching the image, so"
         " it started from the right place and then failed to arrive at kind dispatch. The gap is at the dispatch end,\n"
         " not the input end.\n\n"
         "A side finding is worth recording for functional equivalence. The replica's task model mixes provenance:"
         " MonitorMode, PriceCheck and MultiCart come from the image and show up as get_MonitorMode at 0x143300b4a and"
         " get_PriceCheck at 0x143303724, while NameTemplate and CheckoutDelay match nothing at all and were invented to"
         " support the replica's own bulk creation. Under a one-to-one goal, added functionality is also a difference --"
         " less alarming than a missing one, but not equal.\n\n"
         "Unknown: whether the image's task object carries a Type, for which TaskDetail and TaskGroup type names are the"
         " leads; what the kind is dispatched on, given that the create form does not carry it; and whether the two"
         " invented fields should stay, which depends on whether the image has a comparable bulk-creation path, unchecked.\n\n"
         "The lesson is about syntax over vocabulary. Searching one word in a codebase that spells it twenty-seven ways"
         " produces nothing usable, while finding how the codebase writes properties at all produces a table that can be"
         " checked line by line. AGENTS.md section 2.7 already says to ask how many forms a thing takes first; this is"
         " the round where I actually did it.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
