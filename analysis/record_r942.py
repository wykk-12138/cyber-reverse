"""Record R942: adjacency applied to all thirteen, and the fourth misfiling."""

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
### 连号判据扫全 13 个：第四个误读是 `AddToCartMulti`（R942）

**R941 说下一轮用连号判据扫是否还有第 4 个。扫了 —— 而扫描本身先错了一次。**

### 第一次扫描给出的是噪声

**我把序号在全镜像范围内比，于是得到：**

```
AddToCart  d__36  邻居: CastIterator, CheckForUpdatesAsync, ExpandBufferAsync, FlushAsyncInternal
```

> **那些不是同一个类的方法。原因是**序号按类编**，`d__36` 在很多类里同时存在。**

### 连号判据只在**同一条描述符字符串内**成立

**一条字符串里，序号逐个 +1 的一段就是一个类的方法表。按这个读，六个名字自己就位了：**

| 名字 | 序号 | 同类邻居 | 类 |
|---|---|---|---|
| `AddToCart` | d__36 | `GetCsrf` · `GetCheckout` · `GetCheckoutHtml` | **网页结账** |
| `AddToCartApp` | d__41 | `StartAppFast` · `StartAppSafe` · `GetSessionDw` · `GetCartDw` | **App 会话** |
| `AddToCartAppDw` | d__42 | 同上 | **App 会话** |
| `AddToCartDummy` | d__46 | `GetProduct` · `AddToCartMulti` · `RemoveDummy` | **PopMart 抽签** |
| **`AddToCartMulti`** | **d__47** | **`GetProduct` · `AddToCartDummy` · `RemoveDummy`** | **PopMart 抽签** |
| `AddToCartPreload` | d__90 | `HandleOutOfStock` | **商品库存** |

### 所以第四个误读是 `AddToCartMulti`

**我一直把它记成「通用多件车」。而它和 `Dummy` / `RemoveDummy` 在同一个类里 —— 它是**PopMart 的「加多个盒」**。**

> **四个名字、四轮：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位）· `Multi`（PopMart 多盒）。
> 而四个里两个是通用的、两个是 PopMart 的 —— 而我最初把它们当成同一种东西。****

### 而七个名字**定不了位**

**`AddToCartBox` · `GraphQL` · `PreloadGraphQL` · `Next` · `Astro` · `Svelte` · `Frontend` 都没出现在连号 run 里。**

> **而那**不是**「它们不存在」的证据 —— 描述符扫描本身就是截断的（R939 的 `n=40`），
> 所以一个名字可能只是**那条字符串没被返回**。**
> **与 R939 同一条纪律：缺席 ≠ 未知。**

### 数字

| 度量 | R941 | **R942** |
|---|---|---|
| 套件 | 2023 | **2036** |
| 产物陈旧度 | 8 文件 / 832 行 | **9 文件 / 916 行** |
| **连号定位** | 0 / 13 | **6 / 13（另 7 未知）** |
| **被纠正的名字** | 3 | **4** |

### 教训

> **同一个判据，用错范围就变成噪声：连号在**类内**有意义，在**全镜像**范围内没有。**
> **而它的表现是**给出一个看起来很像答案的表** —— `AddToCart` 旁边是 `CastIterator`，
> 而那读起来像「它属于框架迭代器类」，一个完全错误但语法通顺的结论。**
> **所以判据用错范围时，它不会报错，它会**给出一个答案**。**
"""

if "连号判据扫全 13 个" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R942 appended")

VERDICT = """

---

## 第 942 轮：连号判据扫全 13 个 —— 第四个误读是 `AddToCartMulti`

### 第一次扫描给出的是噪声

```
AddToCart  d__36  邻居: CastIterator, CheckForUpdatesAsync, ExpandBufferAsync
```

> **序号按类编，`d__36` 在很多类里同时存在。连号判据只在**同一条描述符字符串内**成立。**

### 按类内读，六个自己就位

| 名字 | 序号 | 邻居 | 类 |
|---|---|---|---|
| `AddToCart` | 36 | `GetCsrf`/`GetCheckout`/`GetCheckoutHtml` | 网页结账 |
| `AddToCartApp` | 41 | `StartAppFast`/`GetSessionDw`/`GetCartDw` | App 会话 |
| `AddToCartAppDw` | 42 | 同上 | App 会话 |
| `AddToCartDummy` | 46 | `GetProduct`/`Multi`/`RemoveDummy` | PopMart 抽签 |
| **`AddToCartMulti`** | **47** | **同 Dummy** | **PopMart 抽签** |
| `AddToCartPreload` | 90 | `HandleOutOfStock` | 商品库存 |

### 第四个误读

**`AddToCartMulti` 我一直记成「通用多件车」。它和 `Dummy`/`RemoveDummy` 同类 —— 是 **PopMart 的「加多个盒」**。**

> **四轮四个名字：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位）· `Multi`（PopMart 多盒）。
> 四个里两个通用、两个 PopMart —— 而我最初把四者当成同一种东西。**

### 七个定不了位

**`Box` · `GraphQL` · `PreloadGraphQL` · `Next` · `Astro` · `Svelte` · `Frontend` 未出现在连号 run 里。**

> **那不是「不存在」的证据 —— 描述符扫描本身截断。缺席 ≠ 未知（R939 同一纪律）。**

### 数字

| 度量 | R941 | **R942** |
|---|---|---|
| 套件 | 2023 | **2036** |
| 产物陈旧度 | 8 / 832 | **9 / 916** |
| 连号定位 | 0 / 13 | **6 / 13** |
| 被纠正的名字 | 3 | **4** |

### 教训

> **同一个判据，用错范围就变成噪声：连号在**类内**有意义，在**全镜像**范围内没有。
> 而它的表现是**给出一个看起来很像答案的表** —— 读起来像「它属于框架迭代器类」，
> 一个完全错误但语法通顺的结论。**
> **所以判据用错范围时不会报错，它会**给出一个答案**。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — 连号判据扫全 13：6 定位 / 7 未知；`Multi` 是第四个误读（R942，**+13 用例**）

### 判据的范围

**序号按类编 → 连号只在**同一条描述符字符串内**有意义。全镜像范围扫会给出 CastIterator 那种噪声。**

### 定位结果

| 名字 | 类 |
|---|---|
| `AddToCart` | 网页结账 |
| `AddToCartApp` / `AppDw` | App 会话 |
| `AddToCartDummy` / **`Multi`** | **PopMart 抽签** |
| `AddToCartPreload` | 商品库存 |

### 第四个误读

**`AddToCartMulti` 是 PopMart 的「加多个盒」，不是通用多件车。**

### `Scripts/AddToCartPlacement.cs`

**`Rows`(13，各带序号/类/邻居) · `FourthMisfiling` · `Placed`(6)/`Unplaced`(7) · `IsPlaced` · `ClassOf`**

### 数字

**套件 2023 → 2036 · 陈旧度 8/832 → 9/916 · 连号定位 0/13 → 6/13**

| 仍 Unknown | |
|---|---|
| 7 个未定位名字的类 | 描述符扫描截断 |
| `AddToCartPreload` 属哪个站 | 只知道商品库存类 |
| 是否还有第 5 个误读 | 只能对已定位的 6 个下结论 |

**纪律**：判据用错范围时不会报错，它会给出一个语法通顺的错答案。
"""

BLOCKER = """

---

## 366. 连号判据扫全 13：6 定位 / 7 未知；`Multi` 是第四个误读

> R942。**改产品代码 +13 用例。** 套件 **2036 通过 / 0 失败 / 0 跳过**。

### 一、第一次扫描是噪声

```
AddToCart d__36 邻居: CastIterator, CheckForUpdatesAsync, ExpandBufferAsync
```

**序号**按类编**，`d__36` 在很多类里同时存在 → 连号判据只在**同一条描述符字符串内**成立。**

### 二、按类内读

| 名字 | 序号 | 邻居 | 类 |
|---|---|---|---|
| `AddToCart` | 36 | `GetCsrf`/`GetCheckout`/`GetCheckoutHtml` | 网页结账 |
| `AddToCartApp`/`AppDw` | 41/42 | `StartAppFast`/`GetSessionDw`/`GetCartDw` | App 会话 |
| `AddToCartDummy`/**`Multi`** | 46/47 | `GetProduct`/`RemoveDummy` | **PopMart 抽签** |
| `AddToCartPreload` | 90 | `HandleOutOfStock` | 商品库存 |

### 三、第四个误读

**`AddToCartMulti` 记成「通用多件车」是错的 —— 它是 **PopMart 的「加多个盒」**。**

### 四、七个定不了位

**`Box`/`GraphQL`/`PreloadGraphQL`/`Next`/`Astro`/`Svelte`/`Frontend` 未出现在连号 run 里 ——
描述符扫描截断，所以缺席 ≠ 未知。**

### 五、数字

| 度量 | R941 | R942 |
|---|---|---|
| 套件 | 2023 | **2036** |
| 产物陈旧度 | 8 / 832 | **9 / 916** |
| **连号定位** | 0 / 13 | **6 / 13** |
| **被纠正的名字** | 3 | **4** |

### 六、验证

```
analysis/ida.py（类内连号解析）-> 6 个名字带类与邻居
test --filter AddToCartPlacementTests -> 13 通过
metrics_report.py             -> 2036 通过 / 0 失败
```

### 七、仍然 Unknown

- **7 个未定位名字的类**：**Unknown** —— 描述符扫描截断。
- **`AddToCartPreload` 属哪个站**：**Unknown** —— 只知道商品库存类。
- **是否还有第 5 个误读**：**Unknown** —— 只能对已定位的 6 个下结论。

### 八、教训

**同一个判据，用错范围就变成噪声：连号在类内有意义，在全镜像范围内没有。**

**而它的表现是给出一个看起来很像答案的表 —— `AddToCart` 旁边是 `CastIterator`，
读起来像「它属于框架迭代器类」，一个完全错误但语法通顺的结论。**

**所以判据用错范围时不会报错，它会**给出一个答案**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R942", BLOCKER)
    ensure(RSTATUS, "R942", BLOCKER)
    ensure(RVERDICT, "第 942 轮", VERDICT)
    ensure(BACKLOG, "R942", BACKLOG_ADD)

    note = (
        "\n## R942 补充 — 连号判据扫全 13：6 定位 / 7 未知；Multi 是第四个误读（+13 用例，套件 2036）\n\n"
        "第一次全镜像扫序号是噪声（序号按类编，d__36 在多类共存）→ 连号只在同一条描述符字符串内成立。\n\n"
        "定位 6 个：AddToCart=网页结账 · App/AppDw=App 会话 · Dummy/Multi=PopMart 抽签 · Preload=商品库存。\n"
        "→ 第四个误读：AddToCartMulti 是 PopMart 加多个盒，不是通用多件车。\n\n"
        "七个定不了位（Box/GraphQL/PreloadGraphQL/Next/Astro/Svelte/Frontend）—— 描述符扫描截断，缺席≠未知。\n\n"
        "数字：套件 2023 → 2036 · 陈旧度 8/832 → 9/916 · 连号定位 0/13 → 6/13 · 被纠正名字 3 → 4。\n\n"
        "纪律：判据用错范围时不会报错，它会给出一个语法通顺的错答案。\n\n"
        "下一轮：7 个未定位的类（需从别处取完整描述符）；或转优先级 ②（风控对抗）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R942" not in h:
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
             for p, k in ((RBLOCK, "R942"), (RSTATUS, "R942"), (RVERDICT, "第 942 轮"), (BACKLOG, "R942")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R942: adjacency applied to all thirteen, which found the fourth misfiling and a broken first scan\n\n"
         "After three corrections in three rounds the adjacency test was applied to the whole family. The first attempt\n"
         " compared ordinals across the image and produced nonsense -- AddToCart at d__36 beside CastIterator and\n"
         " FlushAsyncInternal -- because ordinals are numbered per class, so d__36 exists in many classes at once. The\n"
         " test only means something inside one concatenated descriptor string, where a run of ordinals increasing by one\n"
         " is one class's method list.\n\n"
         "Read that way six names place themselves. AddToCart sits among GetCsrf, GetCheckout and GetCheckoutHtml, a web\n"
         " checkout class. App and AppDw sit among StartAppFast, GetSessionDw and GetCartDw, an app-session class, so both\n"
         " are what their names say. Preload sits beside HandleOutOfStock. And Dummy and Multi share one class with\n"
         " GetProduct and RemoveDummy, which makes Multi PopMart's add-many-boxes rather than the generic multi-item cart\n"
         " its note claimed. That is the fourth misfiling in four rounds -- two general paths and two PopMart steps, all\n"
         " four originally taken for the same kind of thing.\n\n"
         "Seven names never appear in a consecutive run, including all four framework names and GraphQL, and that is not\n"
         " evidence of anything: the descriptor scan is itself truncated at forty matches, so a name can be missing from\n"
         " this table merely because its string was not returned. Absent is not unknown, which R939 already paid for.\n\n"
         "Figures: suite 2023 to 2036, freshness from eight files to nine and eight hundred and thirty-two lines to nine\n"
         " hundred and sixteen, six of thirteen placed and four names corrected.\n\n"
         "Unknown: the class of the seven unplaced names; which store Preload belongs to, of which only a stock-handling\n"
         " neighbour survives; and whether a fifth name is misfiled, since only the six placed ones can be judged.\n\n"
         "The lesson is that the same test outside its range becomes noise, and its noise looks like an answer -- AddToCart\n"
         " beside CastIterator reads as a plausible classification and is entirely wrong. A criterion used out of range\n"
         " does not fail; it answers.\n\n"
         "Product code changed; suite green at 2036."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()