"""Record R954: 7 duplicates, and five rounds of payment work that reached nothing."""

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
### 93 个分完：**7 个重复品**，而 R920–R925 那五轮**一个都没接上**（R954）

**R953 说下一轮逐个查 93 个。查了，而过程中我**三次**把判据写错。**

### 三次错的判据

| 判据 | 结果 | 为什么错 |
|---|---|---|
| `Id =>` 与 catalog 的 `Id =>` 撞 | 1 个 | **catalog 的 id 来自 `FlowStoreModule` 包装，不写 `Id =>`** |
| `Store =>` 收集 flow 的 id | **0 个** | **flows 根本不声明 `Store =>`** |
| **`XxxModule` 有同名 `XxxFlow`** | **7 个** | ✅ **这条对了** |

> **前两条错在同一个地方：我以为 id 的写法是一种，而它是三种。
> 而第三条不需要知道 id 怎么写 —— 它只问「有没有一个同名的 flow 类」，那是结构，不是字符串。****

### 7 个重复品

```
BrandModules.cs      -> FanaticsFlow      (10 async)
Retail2Modules.cs    -> CasioFlow         (10)
RetailModules.cs     -> EndClothingFlow   (6)
UkEuModules.cs       -> SnsFlow           (6)
MoreModules.cs       -> KithFlow          (4)
NikeModule.cs        -> NikeFlow          (4)
Registry.cs          -> SupremeFlow       (4)
```

**全部是 `*Module` 类 —— 一个和 `FlowStoreModule` 平行的、未接的层级。**

### 而剩下 86 个里，有**五个是我自己五轮前写的**

```
PurpleDot       (R920)  ← 无人引用
EshopWorldPanel (R923)  ← 无人引用
DisneyPaymentSheet (R924) ← 无人引用
VivaPayments    (R925)  ← 无人引用
GlobalECheckout (R922)  ← 无人引用
```

> **R920–R925 五轮，每轮写了支付集成、加了测试、更新了 METRICS。
> 而那五轮的函数贡献是 **0** —— 它们全在 93 个无人引用的文件里。**
> **而当时的 commit 信息写的是「PurpleDot built」—— 它 built 了，只是没接上。**

### 而这不是「白做」

**它们是可复用的、有测试的、证据正确的实现。而它们现在是**dead code**，直到有人把一个支付步骤接到它们上面。**

> **而这个区分对目标很重要：那五轮让**功能**前进了（逻辑写对了），让**函数数**没动（不可达）。
> **两个判据又一次分开，而这次分开的是我自己的五轮。**

### 数字

| 度量 | R953 | **R954** |
|---|---|---|
| 套件 | 2097 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781** |
| **重复品** | 5（只查一个文件） | **7（全扫）** |
| **我写的死代码** | 未知 | **5 个支付类** |

### 教训

> **三次判据、两次错，而两次都错在「我以为 id 只有一种写法」。
> 第三次不问 id，只问结构 —— 而它一次就对。**
> **而更贵的是后半：我查了五轮前的自己。而那五轮的 commit 信息、测试、METRICS 更新都读起来像进展，
> 而函数数一次没动 —— 因为**没有任何东西调用它们**。**
> **R952 那条「缺口是没接上而非没写」现在第二次被证实，而这次证实它的是我自己写的代码。**
"""

if "93 个分完：**7 个重复品**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 954 轮：93 个分完 —— 7 个重复品，而 R920–R925 那五轮一个都没接上

### 三次判据，两次错

| 判据 | 结果 | 为什么错 |
|---|---|---|
| `Id =>` 撞 catalog | 1 | catalog 的 id 来自 `FlowStoreModule` 包装 |
| `Store =>` 收集 | **0** | flows 根本不声明 `Store =>` |
| **`XxxModule` 有同名 `XxxFlow`** | **7** | ✅ **对了** |

> **前两条错在同一处：我以为 id 只有一种写法，而它是三种。
> 第三条不问 id，只问结构 —— 一次就对。**

### 7 个重复品，全是 `*Module`

**Fanatics · Casio · EndClothing · Sns · Kith · Nike · Supreme**（各对应一个已注册 flow）

### 而剩下 86 个里有**五个是我五轮前写的**

```
PurpleDot (R920) · GlobalECheckout (R922) · EshopWorldPanel (R923)
DisneyPaymentSheet (R924) · VivaPayments (R925)   ← 全部无人引用
```

> **那五轮的函数贡献是 **0**。而当时 commit 信息写的是「PurpleDot built」——
> 它 built 了，只是没接上。**

### 而这不是白做

**它们是可复用、有测试、证据正确的实现，而现在它们是 **dead code**，直到有人把一个支付步骤接上去。**

> **那五轮让**功能**前进了（逻辑写对），让**函数数**没动（不可达）。
> **两个判据又一次分开 —— 而这次分开的是我自己的五轮。**

### 数字

| 度量 | R953 | **R954** |
|---|---|---|
| 套件 | 2097 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781** |
| 重复品 | 5（只查一个文件） | **7（全扫）** |
| 我写的死代码 | 未知 | **5 个支付类** |

### 教训

> **三次判据两次错，而两次都错在「我以为 id 只有一种写法」。第三次只问结构，一次就对。**
> **而更贵的是后半：那五轮的 commit 信息、测试、METRICS 更新都读起来像进展，而函数数一次没动 ——
> 因为**没有任何东西调用它们**。**
"""

BACKLOG_ADD = """

## 判据 (c) — 93 个分完：7 重复品 + 5 个我写的死代码（R954，**未改产品代码**）

### 对的判据

**`XxxModule` 有同名 `XxxFlow` → 重复品。7 个：Fanatics/Casio/EndClothing/Sns/Kith/Nike/Supreme**

### 而 R920–R925 五个支付类全部无人引用

**`PurpleDot` · `GlobalECheckout` · `EshopWorldPanel` · `DisneyPaymentSheet` · `VivaPayments`**

**→ 那五轮函数贡献 0；功能前进了，函数数没动。**

### 三次判据（前两次错）

**`Id =>` 撞 catalog（1）· `Store =>` 收集（0）· 同名 flow（7 ✅）**

### 数字

**套件 2097（未变）· 陈旧度 0/0 · 函数数 173,781 · 重复品 7 · 死代码 5**

| 仍 Unknown | |
|---|---|
| 86 个里还有几个是重复品 | 只按 Module↔Flow 配过 |
| 五个支付类该由哪一步调用 | 需要一个支付步骤 |
| 接上一个支付类能加多少函数 | 未测 |

**纪律**：一个判据错在「我以为写法只有一种」时，换成问结构。
"""

BLOCKER = """

---

## 378. 93 个分完：7 重复品 + 5 个我写的死代码

> R954。**未改产品代码。** 套件 **2097 通过 / 0 失败 / 0 跳过**。

### 一、三次判据，两次错

| 判据 | 结果 | 错因 |
|---|---|---|
| `Id =>` 撞 catalog | 1 | catalog 的 id 来自 `FlowStoreModule` 包装 |
| `Store =>` 收集 | **0** | flows 不声明 `Store =>` |
| **`XxxModule` 有同名 `XxxFlow`** | **7** | ✅ |

**前两条错在「我以为 id 只有一种写法」。第三条只问结构，一次就对。**

### 二、7 个重复品，全是 `*Module`

**Fanatics · Casio · EndClothing · Sns · Kith · Nike · Supreme**

### 三、而剩下 86 个里有五个是我五轮前写的

```
PurpleDot (R920) · GlobalECheckout (R922) · EshopWorldPanel (R923)
DisneyPaymentSheet (R924) · VivaPayments (R925)
```

**全部无人引用 → 那五轮函数贡献 **0**。**

### 四、而这不是白做

**可复用、有测试、证据正确的实现 —— 现在是 dead code，直到有人把一个支付步骤接上去。**

### 五、数字

| 度量 | R953 | R954 |
|---|---|---|
| 套件 | 2097 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781** |
| **重复品** | 5 | **7** |
| **我写的死代码** | 未知 | **5** |

### 六、验证

```
grep 'class \w*Module' 全 src        -> 7 个有同名 Flow
grep 五个支付类名 全 src             -> 各自只在自己文件里
test --filter DuplicateModuleAuditTests -> 4 通过（R953）
metrics_report.py                    -> 2097 通过 / 0 失败
```

### 七、仍然 Unknown

- **86 个里还有几个是重复品**：**Unknown** —— 只按 Module↔Flow 配过。
- **五个支付类该由哪一步调用**：**Unknown** —— 需要一个支付步骤。
- **接上一个支付类能加多少函数**：**Unknown** —— 未测。

### 八、教训

**三次判据两次错，都错在「我以为 id 只有一种写法」。第三次只问结构，一次就对。**

**而更贵的是后半：那五轮的 commit 信息、测试、METRICS 更新都读起来像进展，而函数数一次没动 ——
因为没有任何东西调用它们。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R954", BLOCKER)
    ensure(RSTATUS, "R954", BLOCKER)
    ensure(RVERDICT, "第 954 轮", VERDICT)
    ensure(BACKLOG, "R954", BACKLOG_ADD)

    note = (
        "\n## R954 补充 — 93 个分完：7 重复品 + 5 个我写的死代码（未改产品代码，套件 2097）\n\n"
        "对的判据：`XxxModule` 有同名 `XxxFlow` → 重复品 7 个（Fanatics/Casio/EndClothing/Sns/Kith/Nike/Supreme）。\n"
        "前两次判据错在「我以为 id 只有一种写法」（Id => 撞 catalog 得 1；Store => 收集得 0）。\n\n"
        "而剩下 86 个里有五个是我 R920–R925 写的支付类，全部无人引用：\n"
        "PurpleDot · GlobalECheckout · EshopWorldPanel · DisneyPaymentSheet · VivaPayments\n"
        "→ 那五轮函数贡献 0；功能前进了，函数数没动。\n\n"
        "数字：套件 2097（未变）· 陈旧度 0/0 · 函数数 173,781 · 重复品 7 · 死代码 5。\n\n"
        "纪律：判据错在「我以为写法只有一种」时，换成问结构。\n\n"
        "下一轮：给一个支付步骤（StoreFlow 的虚步骤里）接上五个支付类之一，测函数增量。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R954" not in h:
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
             for p, k in ((RBLOCK, "R954"), (RSTATUS, "R954"), (RVERDICT, "第 954 轮"), (BACKLOG, "R954")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R954: seven duplicates, and five rounds of payment work that reached nothing\n\n"
         "R953 left ninety-three unreferenced files to classify. The classification took three attempts and the first two\n"
         " were wrong in the same way: I assumed there was one way for a store to declare its id. Matching Id => against\n"
         " the catalogue gave one hit, because the catalogue's ids come from FlowStoreModule wrappers rather than from\n"
         " declarations. Collecting Store => from the flows gave none, because flows do not declare it. The third attempt\n"
         " stopped asking about ids and asked about structure -- does a class named XxxModule have a sibling named\n"
         " XxxFlow -- and found seven at once.\n\n"
         "All seven are *Module classes forming a hierarchy parallel to FlowStoreModule: Fanatics, Casio, EndClothing, Sns,\n"
         " Kith, Nike and Supreme, each duplicating a store the catalogue already registers.\n\n"
         "The other eighty-six contain five classes I wrote myself between R920 and R925. PurpleDot, GlobalECheckout,\n"
         " EshopWorldPanel, DisneyPaymentSheet and VivaPayments are referenced by nothing outside their own files, so those\n"
         " five rounds contributed zero functions. Their commit messages said built, and they were built; nothing called\n"
         " them.\n\n"
         "That is not the same as wasted. The implementations are reusable, tested and correctly evidenced, and they are\n"
         " dead code until something calls them. But the distinction matters for the objective: those rounds advanced\n"
         " function and left the function count untouched, which is the second time the two criteria have separated -- and\n"
         " this time what separated them was my own work.\n\n"
         "Figures: suite unchanged at 2097, freshness zero, count 173,781, seven duplicates and five dead payment classes.\n\n"
         "Unknown: how many of the remaining eighty-six duplicate something, since only the Module-to-Flow pairing was\n"
         " checked; which step should call a payment class; and what one such wiring would add to the count.\n\n"
         "The lesson is that a criterion that fails because I assumed one spelling should be replaced by one that asks\n"
         " about structure. And the costlier half is the second: five rounds of commits, tests and metrics updates all read\n"
         " like progress while the number never moved, because nothing called the code.\n\n"
         "No product code changed; suite green at 2097."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()