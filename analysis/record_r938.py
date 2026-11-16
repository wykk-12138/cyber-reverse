"""Record R938: Box is a PopMart step, so the five platform gaps were four -- and three names are withdrawn."""

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
### `Box` 也不是平台 —— 而这份清单**两个方向都错了**（R938）

**R937 说 Frontend 是伞，不是第四个框架。这一轮查 Box 在树里的位置，而它同样不是一个框架 —— 理由不同。**

### 决定性的六条相邻 state machine

```
<PollRestockMulti>d__81 · <ExtractPopNow>d__83 · <SelectPopNow>d__84
<SelectMultiPopNow>d__85 · <AddToCartBox>d__86 · <SelectMultiPopNowUS>d__87
```

**六个**连号**的 state machine —— 说明它们是**一个类的六个方法**，而它们的邻居是 PopMart 的：
轮询补货 → 抽 pop-now → 选一个 → 选多个 → 美区选多个 → **加盒到车**。**

> **所以 `Box` 是 PopMart 抽签流程里的**一步**，不是前端框架。**

### 而一个测试就把它分开了

**每个框架都有一个商品抓取器：`ScrapeProductNext` · `ScrapeProductAstro` · `ScrapeProductSvelte` · `ScrapeProductFrontend`。
而 `ScrapeProductBox` **0 匹配**。**

> **所以那条判据不是「名字长什么样」，是「有没有配套的商品抓取器」。
> 而 `Box` 没有 —— 它抓的不是商品，是一次抽签的名额。**

### 所以那份清单**两个方向都错了**

| 名字 | 我当时以为 | 实际 |
|---|---|---|
| `Frontend` | 第四个框架 | **伞**（通用路径） |
| `Box` | 第五个框架 | **PopMart 的一步** |

**两个错误同一个来源：把一张平的名字列表读成「彼此并列的」，而没有问**每个名字旁边是谁**。**

### 而三个更早的名字可以结了

**`BoxGoodsList` · `BoxExtract` · `BoxSku` —— R909 把它们记成「没有调用者，刻意不强行」。
查了：**三条全部 0 匹配**。**

> **所以它们从来不在镜像里 —— 是更早读 box 代码时**编出来的**，现在撤回。**
> **而 R909 那条「没有调用者」的记录，其实在说「我找不到调用者」，而不是「原版没有调用」。
> 两者的区别是：前者是未知，后者是缺席。而这一轮才把未知变成缺席。****

### 数字

| 度量 | R937 | **R938** |
|---|---|---|
| 套件 | 1981 | **1990** |
| 产物陈旧度 | 4 文件 / 492 行 | **5 文件 / 561 行** |
| 平台缺口 | 0（已是 4 个框架） | **0，而清单从 5 修正为 4** |
| 撤回的发明名字 | — | **3**（BoxGoodsList / BoxExtract / BoxSku） |

### 教训

> **两轮之内，五个名字里有两个被证明不是我以为的东西 —— 而两个都是「听起来像」的错。**
> **`Frontend` 听起来像一个框架，`Box` 听起来像一个框架；
> 而一个名字听起来像什么，和它**旁边是谁**，是两件不同的事。**
> **而「旁边是谁」有证据（连号的 state machine），「听起来像什么」没有。**
"""

if "`Box` 也不是平台" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R938 appended")

VERDICT = """

---

## 第 938 轮：`Box` 也不是平台 —— 这份清单两个方向都错了

### 六条相邻 state machine

```
<PollRestockMulti>d__81 · <ExtractPopNow>d__83 · <SelectPopNow>d__84
<SelectMultiPopNow>d__85 · <AddToCartBox>d__86 · <SelectMultiPopNowUS>d__87
```

**六个**连号** —— 一个类的六个方法，而邻居是 PopMart 的：轮询补货 → 抽 pop-now → 选一个 → 选多个 →
美区选多个 → **加盒到车**。**

> **所以 `Box` 是 PopMart 抽签流程里的**一步**，不是框架。**

### 一个测试就分开了

**每个框架都有商品抓取器（`ScrapeProduct{Next,Astro,Svelte,Frontend}`），而 `ScrapeProductBox` **0 匹配**。**

> **判据不是「名字长什么样」，是「有没有配套的商品抓取器」。**

### 所以清单两个方向都错了

| 名字 | 以为 | 实际 |
|---|---|---|
| `Frontend` | 第四个框架 | **伞** |
| `Box` | 第五个框架 | **PopMart 的一步** |

**同一个来源：把平的名字列表读成并列，而没问**每个名字旁边是谁**。**

### 而三个更早的名字可以结了

**`BoxGoodsList` · `BoxExtract` · `BoxSku` —— 三条全部 **0 匹配**。
所以它们从来不在镜像里，是更早读 box 代码时**编出来的**，现在撤回。**

> **而 R909 那条「没有调用者」其实在说「我找不到调用者」，不是「原版没有调用」——
> 前者是未知，后者是缺席。这一轮才把未知变成缺席。**

### 数字

| 度量 | R937 | **R938** |
|---|---|---|
| 套件 | 1981 | **1990** |
| 产物陈旧度 | 4 / 492 | **5 / 561** |
| 平台缺口 | 0 | **0，清单从 5 修正为 4** |
| 撤回的发明名字 | — | **3** |

### 教训

> **两轮之内五个名字里两个不是我以为的东西 —— 都是「听起来像」的错。
> 一个名字听起来像什么，和它**旁边是谁**，是两件不同的事。
> 而「旁边是谁」有证据（连号 state machine），「听起来像什么」没有。**
"""

BACKLOG_ADD = """

## 判据 (a)/优先级 ① — `Box` 是 PopMart 的一步；三名字撤回（R938，**+9 用例**）

### 决定性的连号

```
d__81 PollRestockMulti · d__83 ExtractPopNow · d__84 SelectPopNow
d__85 SelectMultiPopNow · d__86 AddToCartBox · d__87 SelectMultiPopNowUS
```

**一个类的六个方法 → `Box` 是抽签一步。**

### 分开两类的那条判据

**每个框架都有 `ScrapeProduct*`；`ScrapeProductBox` **0 匹配**。**

### 清单修正

| 名字 | 以为 | 实际 |
|---|---|---|
| `Frontend` | 框架 | 伞 |
| `Box` | 框架 | PopMart 一步 |

**框架数 **4**：Next / Astro / Svelte / Frontend。**

### 撤回三个发明

**`BoxGoodsList` · `BoxExtract` · `BoxSku` → 全 0 匹配 → 从来不在镜像里。**
**R909 的「无调用者」= 「我找不到」，不是「原版没有」—— 这一轮把未知变缺席。**

### `Scripts/PopMartDrawSteps.cs`

**`DrawSteps`(6) · `WithdrawnNames`(3) · `Frameworks`(4) · `FrameworkCount` · `IsDrawStep`**

### 数字

**套件 1981 → 1990 · 陈旧度 4/492 → 5/561**

| 仍 Unknown | |
|---|---|
| `SelectMultiPopNowUS` 的美区差异 | 只有名字 |
| 另外两个 draw 步骤的行为 | 只有名字 |
| 是否还有别的「听起来像框架」的名字 | 未扫 |

**纪律**：一个名字听起来像什么，和它旁边是谁，是两件不同的事。后者有证据，前者没有。
"""

BLOCKER = """

---

## 362. `Box` 是 PopMart 的一步；清单从 5 修正为 4；三名字撤回

> R938。**改产品代码 +9 用例。** 套件 **1990 通过 / 0 失败 / 0 跳过**。

### 一、六条连号 state machine

```
<PollRestockMulti>d__81 · <ExtractPopNow>d__83 · <SelectPopNow>d__84
<SelectMultiPopNow>d__85 · <AddToCartBox>d__86 · <SelectMultiPopNowUS>d__87
```

**连号 = 一个类的六个方法；邻居是 PopMart 的抽签流程 → `Box` 是其中一步，不是框架。**

### 二、分开两类的那条判据

**每个框架都有 `ScrapeProduct*`（Next/Astro/Svelte/Frontend 四个全有）；`ScrapeProductBox` **0 匹配**。**

### 三、清单修正（两个方向都错）

| 名字 | 以为 | 实际 |
|---|---|---|
| `Frontend` | 第四个框架 | **伞**（通用路径） |
| `Box` | 第五个框架 | **PopMart 的一步** |

**同一个来源：把平的名字列表读成并列，没问「旁边是谁」。**

### 四、撤回三个发明

**`BoxGoodsList` · `BoxExtract` · `BoxSku` → 全 **0 匹配**，从来不在镜像里。**

**R909 记的「无调用者」实际是「我找不到调用者」—— 未知；而 0 匹配才是缺席。**

### 五、数字

| 度量 | R937 | R938 |
|---|---|---|
| 套件 | 1981 | **1990** |
| 产物陈旧度 | 4 / 492 | **5 / 561** |
| **框架数** | 5（名义） | **4** |
| **撤回名字** | — | **3** |

### 六、验证

```
analysis/ida.py str "AddToCartBox"     -> 6 命中，全在 d__8x 连号里
analysis/ida.py str "ScrapeProductBox" -> 0
analysis/ida.py str "BoxGoodsList"/"BoxExtract"/"BoxSku" -> 各 0
test --filter PopMartDrawStepsTests    -> 9 通过
metrics_report.py                      -> 1990 通过 / 0 失败
```

### 七、仍然 Unknown

- **`SelectMultiPopNowUS` 的美区差异**：**Unknown** —— 只有名字。
- **另外两个 draw 步骤的行为**：**Unknown** —— 只有名字。
- **是否还有别的「听起来像框架」的名字**：**Unknown** —— 未扫。

### 八、教训

**两轮之内，五个名字里两个不是我以为的东西。两个都是「听起来像」的错。**

**`Frontend` 听起来像框架，`Box` 听起来像框架；而「听起来像什么」和「旁边是谁」是两件不同的事。**

**后者有证据（连号 state machine），前者没有。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R938", BLOCKER)
    ensure(RSTATUS, "R938", BLOCKER)
    ensure(RVERDICT, "第 938 轮", VERDICT)
    ensure(BACKLOG, "R938", BACKLOG_ADD)

    note = (
        "\n## R938 补充 — Box 是 PopMart 的一步；清单 5 修正为 4；三名字撤回（+9 用例，套件 1990）\n\n"
        "六条连号 state machine（d__81 PollRestockMulti · d__83 ExtractPopNow · d__84 SelectPopNow · "
        "d__85 SelectMultiPopNow · d__86 AddToCartBox · d__87 SelectMultiPopNowUS）→ Box 是抽签一步。\n\n"
        "判据：每个框架都有 ScrapeProduct*；ScrapeProductBox 0 匹配。\n\n"
        "清单两个方向都错：Frontend 是伞、Box 是 PopMart 一步 → 框架数 4（Next/Astro/Svelte/Frontend）。\n\n"
        "撤回三个发明名字：BoxGoodsList / BoxExtract / BoxSku → 全 0 匹配。\n"
        "R909 的「无调用者」= 我找不到（未知），0 匹配才是缺席。\n\n"
        "数字：套件 1981 → 1990 · 陈旧度 4/492 → 5/561。\n\n"
        "纪律：一个名字听起来像什么，和它旁边是谁，是两件不同的事。后者有证据，前者没有。\n\n"
        "下一轮：扫是否还有别的「听起来像框架」的名字；或转优先级 ②（风控对抗）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R938" not in h:
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
             for p, k in ((RBLOCK, "R938"), (RSTATUS, "R938"), (RVERDICT, "第 938 轮"), (BACKLOG, "R938")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R938: Box is a PopMart step, so the list of five was wrong in both directions\n\n"
         "R937 found Frontend was an umbrella rather than a fourth framework. This round checked where Box sits, and it\n"
         " is not a framework either, for a different reason: six consecutive state-machine numbers place AddToCartBox\n"
         " among PollRestockMulti, ExtractPopNow, SelectPopNow, SelectMultiPopNow and SelectMultiPopNowUS. One class's\n"
         " methods, and a PopMart draw sequence -- restock polling, extract a pop-now, select one, select many, the US\n"
         " variant, then add a box to the cart.\n\n"
         "The test that separates the two kinds is a product scraper. Every framework has one -- ScrapeProductNext,\n"
         " ScrapeProductAstro, ScrapeProductSvelte and ScrapeProductFrontend all exist -- and a search for\n"
         " ScrapeProductBox returns nothing. So the criterion is not what a name looks like but whether it has a scraper\n"
         " beside it, and Box does not, because what it grabs is a slot in a draw rather than a product.\n\n"
         "Which means the list of five was wrong in two directions at once: one member was an umbrella and another was a\n"
         " shop-specific step. Both mistakes came from reading a flat list of names and assuming they were peers, and\n"
         " both were only detectable by asking what surrounds each name.\n\n"
         "Three older names are also settled. BoxGoodsList, BoxExtract and BoxSku had been carried since R909 as having no\n"
         " callers, and all three return zero matches -- they were never in the image, having been invented during an\n"
         " earlier reading of the box code. R909's note that these had no callers was really saying I could not find any,\n"
         " which is an unknown; zero matches is absence, and it took a separate search to tell the two apart.\n\n"
         "Figures: suite 1981 to 1990, freshness from four files to five and four hundred and ninety-two lines to five\n"
         " hundred and sixty-one, and the framework count corrected from a nominal five to four.\n\n"
         "Unknown: how the US variant of SelectMultiPopNow differs; what the other two draw steps do, of which only names\n"
         " survive; and whether other names in the tree also only look like frameworks.\n\n"
         "The lesson is that two of five names in two rounds were not what they seemed, and both were plausible-sounding\n"
         " mistakes. What a name sounds like and who stands beside it are different questions, and only the second has\n"
         " evidence.\n\n"
         "Product code changed; suite green at 1990."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()