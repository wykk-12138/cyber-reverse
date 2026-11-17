"""Record R976: the one truly missing core type is written, and two guards had to be told why."""

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
### 唯一一个真缺失的核心类型写出来了，而**两个守卫立刻红了**（R976）

**R975 把 16 分成 5 改名 + 1 真缺失 + 10 UI。这一轮写那 1 个。**

### `ObservableDictionary<TKey,TValue>`（`src/Cybersole.Core/Helpers/`）

**`IDictionary` + `IReadOnlyDictionary` + `INotifyCollectionChanged` + `INotifyPropertyChanged`。
而注释里写了**为什么一个字典需要通知**：**

> **集合可以按索引说「变了」；字典不能 —— 增删一个键改变了项集，而其他键的位置没动，
> 所以按下标缓存的消费者无从 diff。**
> **所以复刻件里用一个普通 `Dictionary<TKey,TValue>` 顶替它**不是改名，是行为变化** ——
> 而以「视图不再更新」而不是「抛异常」的形式出现。**

### 而两个守卫**立刻**抓到了它

**① `UnsubscribedEventsTests`：「声明了、raise 了、没人听」**

**我声明了 `CollectionChanged` 和 `PropertyChanged`，而仓里没人订阅 —— 那正是那个守卫要抓的。**

> **而它的白名单里第一条是先例：**
> `["CanExecuteChanged"] = "contract: ICommand requires it; Avalonia subscribes"`
> **而这两条同形：接口**要求**声明它们，而订阅者会在 UI 里 —— 而 UI 是 YG 说不急的那一层。
> 所以登记为契约事件，并写明「声明它们是契约；还没人听是工作的状态，不是坏掉的承诺」。**

**② `BindScopeGuardTests`：`KnownUnseenTypes` 5 → 6**

**`ObservableDictionary<TKey,TValue>` 是**第二个双泛型类型**，而 `bind_scope` 的 `DECL` 正则只匹配无类型参数的声明 ——
所以它对 `bind_diff` 是「存在」、对 `bind_scope` 是「不可见」。**

> **而那个守卫的注释写着「If this list shrinks, someone fixed DECL; if it grows, someone narrowed it.
> Either way the test below fails and the change becomes deliberate.」**
> **所以 5 → 6 是**按规矩改的**，并写明是因为新增了一个双泛型类型。****

### 而函数数**不变**

**`pdata-replica` 173,952 → 173,952。因为**没有任何东西实例化它**。**

> **那是 R963/R967 已建立的规则在起作用：不可达的代码被裁。
> 而 `ObservableDictionary` 现在就是「写好了、有 10 个用例、而产物里没有」——
> **与 R965 发现的 34 个覆写同一种状态。**
> **所以它不是缺口（类型存在性检查已通过），而是**尚未接线**。****

### 数字

| 度量 | R975 | **R976** |
|---|---|---|
| 套件 | 2186 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未变 —— 无人实例化）** |
| **类型缺失** | 16 | **15** |
| **核心类型缺失** | 1 | **0** |

### 教训

> **写一个类型，两个守卫红了。而**两次都不是要绕过它们** ——
> 它们问的都是对的问题（「这个事件有人听吗」「为什么这个类型 bind_scope 看不见」），
> 而答案是「这是契约事件」和「它是双泛型」。**
> **所以这一轮最有价值的不是那个类，是**两条守卫都要求一个理由，而我给得出**。
> 如果给不出，那才是问题。**
"""

if "唯一一个真缺失的核心类型写出来了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 976 轮：唯一一个真缺失的核心类型写出来了，而两个守卫立刻红了

### `ObservableDictionary<TKey,TValue>`（`src/Cybersole.Core/Helpers/`）

**`IDictionary` + `IReadOnlyDictionary` + `INotifyCollectionChanged` + `INotifyPropertyChanged`。**

> **一个字典为什么需要通知：集合可以按索引说「变了」；字典不能 ——
> 增删一个键改变了项集，而其他键的位置没动，按下标缓存的消费者无从 diff。**
> **所以用普通 `Dictionary<TKey,TValue>` 顶替它不是改名，是行为变化 ——
> 以「视图不再更新」而不是「抛异常」的形式出现。**

### 两个守卫立刻抓到了它

**① `UnsubscribedEventsTests`：「声明了、raise 了、没人听」**

**我声明了两个事件而仓里没人订阅。而白名单里第一条是先例：
`["CanExecuteChanged"] = "contract: ICommand requires it; Avalonia subscribes"`。
这两条同形 —— 接口**要求**声明，订阅者在 UI 里（YG 说不急的那层）。
→ 登记为契约事件，并写明「声明是契约；还没人听是工作的状态，不是坏掉的承诺」。**

**② `BindScopeGuardTests`：`KnownUnseenTypes` 5 → 6**

**`ObservableDictionary<TKey,TValue>` 是第二个双泛型类型，而 `bind_scope` 的 `DECL` 正则只匹配无类型参数的声明
→ 对 `bind_diff` 存在、对 `bind_scope` 不可见。**
**而那个守卫的注释写着「if it grows, someone narrowed it … the change becomes deliberate」→ 5→6 是按规矩改的。**

### 而函数数不变

**173,952 → 173,952，因为**没有任何东西实例化它**（R963/R967 的规则在起作用）。
所以它不是缺口（类型存在性已通过），而是**尚未接线** —— 与 R965 发现的 34 个覆写同一种状态。**

### 数字

| 度量 | R975 | **R976** |
|---|---|---|
| 套件 | 2186 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（无人实例化）** |
| **类型缺失** | 16 | **15** |
| **核心类型缺失** | 1 | **0** |

### 教训

> **两个守卫红了，而两次都不是要绕过它们 —— 它们问的都是对的问题，
> 而答案是「这是契约事件」和「它是双泛型」。**
> **最有价值的不是那个类，是**两条守卫都要求一个理由，而我给得出**。如果给不出，那才是问题。**
"""

BACKLOG_ADD = """

## 判据 (a) — **核心类型缺失 1 → 0：写了 `ObservableDictionary<TKey,TValue>`**（R976，**+10 用例**）

### 改动

**`src/Cybersole.Core/Helpers/ObservableDictionary.cs`：
`IDictionary` + `IReadOnlyDictionary` + `INotifyCollectionChanged` + `INotifyPropertyChanged`。
替换已有键只发 `Item[]` 不发项集事件；移除携带旧对；`AddRange` 只对新增键通知；重复 `Add` 先抛后不通知。**

### 两个守卫红了，都按规矩处理

**① `UnsubscribedEventsTests` → 白名单登记两条契约事件（先例是 `CanExecuteChanged`）**
**② `BindScopeGuardTests` → `KnownUnseenTypes` 5 → 6（第二个双泛型类型，`DECL` 抓不到）**

### 而函数数不变

**无人实例化它 → 被裁（R963/R967 规则）。所以是**尚未接线**，不是缺口。**

### 数字

**套件 2186 → 2196 · 陈旧度 0/0 · 函数数 173,952（未变）· 类型缺失 16 → **15** · 核心类型缺失 1 → **0**

| 仍 Unknown | |
|---|---|
| 原版哪里用 `ObservableDictionary` | 未取证（需要能反编译的调用点） |
| 复刻件该在哪里实例化它 | 未定 |

**纪律**：守卫红了不是要绕过 —— 它要求一个理由，而理由给得出才是对的。
"""

BLOCKER = """

---

## 400. **核心类型缺失 1 → 0：写了 `ObservableDictionary<TKey,TValue>`**

> R976。**改产品代码 +10 用例。** 套件 **2196 通过 / 0 失败 / 0 跳过**。

### 一、改动

**`src/Cybersole.Core/Helpers/ObservableDictionary.cs`：
`IDictionary<TKey,TValue>` + `IReadOnlyDictionary<TKey,TValue>` + `INotifyCollectionChanged` + `INotifyPropertyChanged`。**

**行为要点：**
- **替换已有键 → 只发 `Item[]`，不发项集事件**（消费视图不该在每次编辑时重建）
- **移除 → 事件携带旧对**（移除后查不到）
- **重复 `Add` → 先抛 `ArgumentException`，不发通知**（没人该看到没发生的改变）
- **`AddRange` → 只对新增键通知，不覆盖已存在的**
- **`Clear` 空字典 → 不发通知**

### 二、两个守卫红了，都按规矩处理

**① `UnsubscribedEventsTests.NoEventIsDeclaredRaisedAndNeverListenedTo`**
**→ 白名单登记 `CollectionChanged` / `PropertyChanged`，理由同先例 `CanExecuteChanged`（契约事件，订阅者在 UI）**

**② `BindScopeGuardTests.ScopeMissesStayAtZeroAndTheExaminedSetReconciles`**
**→ `KnownUnseenTypes` 5 → 6（第二个双泛型类型，`bind_scope` 的 `DECL` 只匹配无类型参数的声明）**

### 三、而函数数不变

**`pdata-replica` 173,952 → 173,952 —— 无人实例化它，被裁。**
**所以它是**尚未接线**，不是缺口（R963/R967 的规则）。**

### 四、数字

| 度量 | R975 | R976 |
|---|---|---|
| 套件 | 2186 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **类型缺失** | 16 | **15** |
| **核心类型缺失** | 1 | **0** |

### 五、验证

```
dotnet build Cybersole.Core           -> 0 error
test --filter ObservableDictionaryTests -> 10 通过
test --filter UnsubscribedEventsTests|BindScopeGuardTests -> 3 通过
bind_diff.py --type-presence          -> 174 declared, 159 present, 15 absent
func_count.py                         -> 173,952（未变）
metrics_report.py                     -> 2196 通过 / 0 失败
```

### 六、仍然 Unknown

- **原版哪里用 `ObservableDictionary`**：**Unknown** —— 未取证（需要能反编译的调用点）。
- **复刻件该在哪里实例化它**：**Unknown** —— 未定。

### 七、教训

**写一个类型，两个守卫红了。而两次都不是要绕过它们 —— 它们问的都是对的问题
（「这个事件有人听吗」「为什么 bind_scope 看不见」），而答案是「契约事件」和「双泛型」。**

**最有价值的不是那个类，是两条守卫都要求一个理由，而我给得出。如果给不出，那才是问题。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R976", BLOCKER)
    ensure(RSTATUS, "R976", BLOCKER)
    ensure(RVERDICT, "第 976 轮", VERDICT)
    ensure(BACKLOG, "R976", BACKLOG_ADD)

    note = (
        "\n## R976 补充 — **核心类型缺失 1 → 0：写了 ObservableDictionary`2**（+10 用例，套件 2196）\n\n"
        "写了 `src/Cybersole.Core/Helpers/ObservableDictionary.cs`：IDictionary + IReadOnlyDictionary +\n"
        "INotifyCollectionChanged + INotifyPropertyChanged。替换已有键只发 Item[]；移除携带旧对；重复 Add 先抛后不通知；\n"
        "AddRange 只对新增键通知；Clear 空字典不发通知。\n\n"
        "**两个守卫立刻红了，都按规矩处理**：\n"
        "① `UnsubscribedEventsTests` → 白名单登记 CollectionChanged/PropertyChanged（先例是 CanExecuteChanged，契约事件）\n"
        "② `BindScopeGuardTests` → `KnownUnseenTypes` 5 → 6（第二个双泛型类型，DECL 只匹配无类型参数的声明）\n\n"
        "→ 函数数 173,952 **不变**：无人实例化它 → 被裁（R963/R967 规则）。所以是**尚未接线**，不是缺口。\n\n"
        "数字：套件 2186 → 2196 · 陈旧度 0/0 · 函数数 173,952 · 类型缺失 16 → **15** · 核心类型缺失 1 → **0**。\n\n"
        "纪律：守卫红了不是要绕过 —— 它要求一个理由，而理由给得出才是对的。\n\n"
        "下一轮：剩余 15 个类型缺失 = 10 UI + 5 改名（已核）。所以判据 a 的「类型缺失」实质已结案，\n"
        "下一步转回函数数（173,952 / 277,120）—— 用 rea 的 compare_functions 或 IDA 的类型清单对照。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R976" not in h:
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
             for p, k in ((RBLOCK, "R976"), (RSTATUS, "R976"), (RVERDICT, "第 976 轮"), (BACKLOG, "R976")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R976: the one genuinely missing core type is written, and two guards asked why\n\n"
         "R975 split the sixteen absent types into five renames, ten UI and one real absence. This round writes the one.\n\n"
         "ObservableDictionary takes two type parameters and implements IDictionary, IReadOnlyDictionary,\n"
         " INotifyCollectionChanged and INotifyPropertyChanged. The behaviour that matters is that replacing an existing key\n"
         " raises only the indexer notification and not the item-set one, so a consumer does not rebuild its view on every\n"
         " edit; that a removal carries the old pair, because it cannot be looked up afterwards; that a duplicate add throws\n"
         " before any notification, so nobody sees a change that did not happen; and that AddRange notifies only for keys that\n"
         " actually arrived.\n\n"
         "Two guards failed immediately and both were right to. UnsubscribedEventsTests reports an event that is declared and\n"
         " raised but never listened to, which is exactly what two new events look like before anything binds to them; they\n"
         " are registered as contract events on the same reasoning as ICommand's CanExecuteChanged, and the entry says that\n"
         " declaring them is the contract while having no listener yet is the state of the work. BindScopeGuardTests pins how\n"
         " many types are present to one tool and invisible to the other, and a second generic-arity type raises it from five\n"
         " to six, which is what that guard exists to make deliberate.\n\n"
         "The count did not move. The type is written, tested and present per bind_diff, but nothing instantiates it, so the\n"
         " trimmer drops it -- the same state as the thirty-four overrides R965 found. That makes it unwired rather than\n"
         " missing, and the type-absence criterion no longer counts it against us.\n\n"
         "Figures: suite 2186 to 2196, freshness zero, count 173,952, absent types sixteen to fifteen, core absent types one\n"
         " to zero.\n\n"
         "Unknown: where the original uses this type, which needs a call site that can be decompiled; and where the replica\n"
         " should instantiate it, which is undecided.\n\n"
         "The lesson is that two guards went red and neither needed circumventing. Both asked the right question -- does\n"
         " anything listen, and why is this type invisible to the other tool -- and both had an answer. What would have been a\n"
         " problem is having no answer.\n\n"
         "Product code and tests added; suite green at 2196."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()