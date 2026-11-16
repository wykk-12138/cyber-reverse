"""Record R937: Frontend was never a framework -- it is the generic path, and all five gaps close."""

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
### `Frontend` **不是第四个框架** —— 它是那条通用的（R937）

**五个平台缺口里的最后一个。查了，而它根本不是一个平台。**

```
_frontendDomain · _frontendUrl · _frontendSearch · FrontendUri · get_FrontendUri · IsFrontendUrl
ScrapeJsonFrontend · ScrapePageFrontend · ScrapeProductFrontend
ScrapeVariantAvailabilityFrontend · FindProductFrontend · AddToCartFrontend
```

### 两条线索指向同一件事

**① 每个方法都是某个框架专用方法的**通用对应物**：**
`ScrapeProductFrontend` 挨着 `ScrapeProductSvelte` · `AddToCartFrontend` 挨着 `AddToCartAstro`。

**② 而三个字段是 **URI 的组成部分**：domain / url / search。**

> **所以 frontend 路径是那条**兜底**：读站点实际发出来的东西；
> 而那四个框架是**它知道该用哪个之后**去调用的解析器。**

### 所以「五个平台缺口」这个说法本身一直是错的

**它不是五个平台并列。它是**一个通用路径 + 四个具体解析器** ——
`Box` 是第一个做的，而它当时被当成五个中的一个。**

> **而 `AddToCartFrontend` 是那个通用入口，四个具体的都挂在它下面。
> 所以真正的结构是**一棵**，不是一列。**
> **而「还差一个平台」这个待办项，是因为我把它读成了一列才出现的。**

### `IsFrontendUrl` 是那个铰链

**一个店同时有 API 和页面，而两者是**故意不同的 URL** ——
所以流程必须先判断手里是哪一个，才能决定怎么读。**

**而它的默认方向是**刻意的**：**

> **不像 API 的 URL 一律当页面。
> 因为把页面当 JSON 读会**响亮地失败**，而把页面当 API 调会返回一个 HTML 错误体 ——
> **那个体解析出来什么都不是，看起来像一个空商品。****

### 三个决定

**① 查 API 标记时**忽略查询串** —— 一个页面可以带任意查询，标记落在查询里就是假阳性。**
**② `Describe` 只返回镜像点名的三个部分** —— 调用方无法凭空造第四个。
**③ 相对路径没有 domain，就说没有** —— 而不是从上下文编一个。**

### 而 API 标记列表标了 Inference

**镜像给了 `IsFrontendUrl` 这个名字，没说它测什么.
所以那十个标记是「店面的 API 在实践里长什么样」，不是恢复到的。
**而它们被写得短而显式，是为了一个错的标记能被看见。****

### 数字

| 度量 | R936 | **R937** |
|---|---|---|
| 套件 | 1969 | **1981** |
| 产物陈旧度 | 3 文件 / 371 行 | **4 文件 / 492 行** |
| **`AddToCart` 平台缺口** | 1 剩 | **0** |

### 教训

> **一个待办清单的形状决定了它能被关掉多少。**
> **我把五个名字读成一列并列的平台，于是它们是五个待办；
> 而其中一个是**伞**，于是真实结构是一棵树，而待办是「把这棵树建起来」这一件事。**
> **形状读错的时候，进度看起来像线性减少，而实际上从来没有接近过。**
"""

if "`Frontend` **不是第四个框架**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R937 appended")

VERDICT = """

---

## 第 937 轮：`Frontend` 不是框架 —— 它是那条通用的，而五个缺口全关

### 字面量

```
_frontendDomain · _frontendUrl · _frontendSearch · FrontendUri · get_FrontendUri · IsFrontendUrl
ScrapeJsonFrontend · ScrapePageFrontend · ScrapeProductFrontend
ScrapeVariantAvailabilityFrontend · FindProductFrontend · AddToCartFrontend
```

### 两条线索

**① 每个方法都是框架专用方法的通用对应物** —— `ScrapeProductFrontend` 挨着 `ScrapeProductSvelte`
**② 三个字段是 **URI 组成部分**：domain / url / search**

> **所以 frontend 是**兜底路径**（读站点实际发出的东西），四个框架是它知道该用哪个之后调的解析器。**

### 而「五个平台缺口」这个说法一直是错的

**不是五个平台并列，是**一个通用路径 + 四个具体解析器**。
`Box` 是第一个做的，当时被当成五个中的一个。**

> **`AddToCartFrontend` 是通用入口，四个具体的挂在它下面。真实结构是**一棵树**，不是一列。**
> **「还差一个平台」这个待办项，是因为我把它读成一列才出现的。**

### `IsFrontendUrl` 是那个铰链

**一个店同时有 API 和页面，故意不同 URL → 流程必须先判断手里是哪一个。**

> **默认方向刻意：不像 API 的一律当页面。
> 把页面当 JSON 读会**响亮地失败**；把页面当 API 调会返回 HTML 错误体 ——
> **解析出来什么都不是，看起来像一个空商品。**

### 三个决定

**忽略查询串（页面可带任意查询，标记落在查询里是假阳性）· `Describe` 只返回三个部分 · 相对路径没有 domain 就说没有**

**而 API 标记列表标了 Inference —— 镜像给了名字没说测什么。**

### 数字

| 度量 | R936 | **R937** |
|---|---|---|
| 套件 | 1969 | **1981** |
| 产物陈旧度 | 3 / 371 | **4 / 492** |
| AddToCart 平台缺口 | 1 剩 | **0** |

### 教训

> **一个待办清单的形状决定了它能被关掉多少。
> 五个名字读成一列 → 五个待办；而其中一个是**伞** → 真实结构是一棵树，待办是「把这棵树建起来」一件事。**
> **形状读错时，进度看起来线性减少，而实际从没接近过。**
"""

BACKLOG_ADD = """

## 优先级 ① — Frontend 是通用路径，不是第四个框架（R937，**+12 用例，五缺口全关**）

### 结构读对之后

**一个通用路径 + 四个具体解析器（Box / Next / Astro / Svelte），`AddToCartFrontend` 是入口。**

### `Scripts/FrontendSurface.cs`

**`UriParts`(Domain/Url/Search) · `ApiPathMarkers`（Inference）· `MethodFamily`（6 个通用方法，3 个有具体对应）·
`LooksLikeApi` · `IsFrontendUrl` · `Describe`**

### 三个决定

**查标记时忽略查询串 · `Describe` 只返回三个部分 · 相对路径无 domain 就说没有**

### `IsFrontendUrl` 的默认方向

**不像 API 的一律当页面 —— 把页面当 JSON 读会响亮失败；当 API 调会返回 HTML 错误体，
解析出来像空商品。**

### 数字

**套件 1969 → 1981 · 陈旧度 3/371 → 4/492 · **AddToCart 平台缺口 1 → 0****

| 仍 Unknown | |
|---|---|
| 十个 API 标记是否与原版一致 | Inference |
| `Box` 在树里的位置 | 已做，但当时按"列"读的 |
| 其余四个通用方法的行为 | 只有名字 |

**纪律**：待办清单的形状决定它能被关掉多少。读成一列 → 五个待办；读成树 → 一件事。
"""

BLOCKER = """

---

## 361. `Frontend` 是通用路径；五缺口全关

> R937。**改产品代码 +12 用例。** 套件 **1981 通过 / 0 失败 / 0 跳过**。

### 一、字面量

```
_frontendDomain · _frontendUrl · _frontendSearch · FrontendUri · get_FrontendUri · IsFrontendUrl
ScrapeJsonFrontend · ScrapePageFrontend · ScrapeProductFrontend
ScrapeVariantAvailabilityFrontend · FindProductFrontend · AddToCartFrontend
```

### 二、两条线索

1. **每个方法都是框架专用方法的通用对应物**（`ScrapeProductFrontend` 挨着 `ScrapeProductSvelte`）。
2. **三个字段是 URI 组成部分**（domain / url / search）。

**→ frontend 是兜底路径；四个框架是它知道该用哪个之后调的解析器。**

### 三、「五个平台缺口」这个说法一直是错的

**不是五个平台并列，是一个通用路径 + 四个具体解析器。`Box` 当时被当成五个中的一个。**

**`AddToCartFrontend` 是入口，四个具体的挂在它下面 —— 结构是树，不是列。**

### 四、`IsFrontendUrl` 的默认方向

**不像 API 的一律当页面：把页面当 JSON 读会响亮失败；当 API 调会返回 HTML 错误体，
解析出来像空商品。**

### 五、三个决定

**忽略查询串 · `Describe` 只返回三个部分 · 相对路径无 domain 就说没有**

### 六、数字

| 度量 | R936 | R937 |
|---|---|---|
| 套件 | 1969 | **1981** |
| 产物陈旧度 | 3 / 371 | **4 / 492** |
| **AddToCart 平台缺口** | 1 剩 | **0** |

### 七、验证

```
analysis/ida.py str "Frontend"     -> 六字段 + 六个方法
test --filter FrontendSurfaceTests -> 12 通过
metrics_report.py                  -> 1981 通过 / 0 失败
```

### 八、仍然 Unknown

- **十个 API 标记是否与原版一致**：**Inference**。
- **`Box` 在树里的位置**：**Unknown** —— 已做，但当时按列读的。
- **其余四个通用方法的行为**：**Unknown** —— 只有名字。

### 九、教训

**一个待办清单的形状决定了它能被关掉多少。**

**五个名字读成一列 → 五个待办；而其中一个是**伞** → 真实结构是一棵树，待办是「把这棵树建起来」一件事。**

**形状读错的时候，进度看起来线性减少，而实际上从来没有接近过。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R937", BLOCKER)
    ensure(RSTATUS, "R937", BLOCKER)
    ensure(RVERDICT, "第 937 轮", VERDICT)
    ensure(BACKLOG, "R937", BACKLOG_ADD)

    note = (
        "\n## R937 补充 — Frontend 是通用路径；五缺口全关（+12 用例，套件 1981）\n\n"
        "Frontend 不是第四个框架：每个方法都是框架专用方法的通用对应物（ScrapeProductFrontend 挨着 "
        "ScrapeProductSvelte），三个字段是 URI 组成部分（domain/url/search）。\n"
        "→ 结构是**一个通用路径 + 四个具体解析器（Box/Next/Astro/Svelte）**，AddToCartFrontend 是入口。\n\n"
        "而「五个平台缺口」这个说法一直是错的 —— 我读成了一列，实际是一棵树。\n\n"
        "IsFrontendUrl 的默认方向刻意：不像 API 的一律当页面（把页面当 JSON 读会响亮失败；当 API 调返回 HTML "
        "错误体解析出来像空商品）。\n\n"
        "三个决定：忽略查询串 · Describe 只返回三个部分 · 相对路径无 domain 就说没有。API 标记标 Inference。\n\n"
        "数字：套件 1969 → 1981 · 陈旧度 3/371 → 4/492 · AddToCart 平台缺口 1 → 0。\n\n"
        "纪律：待办清单的形状决定它能被关掉多少。读成一列 → 五个待办；读成树 → 一件事。\n\n"
        "下一轮：Book 在树里的位置已做但按列读的；或转优先级 ②（风控对抗）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R937" not in h:
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
             for p, k in ((RBLOCK, "R937"), (RSTATUS, "R937"), (RVERDICT, "第 937 轮"), (BACKLOG, "R937")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R937: Frontend was never a fourth framework, and the shape of that list was wrong all along\n\n"
         "The last of the five AddToCart platform gaps. It is not a platform. Every method in the recovered family is a\n"
         " generic counterpart of a framework-specific one -- ScrapeProductFrontend beside ScrapeProductSvelte,\n"
         " AddToCartFrontend beside AddToCartAstro -- and the three fields are URI parts: domain, url and search. So the\n"
         " frontend path is the fallback that reads whatever the site served, and Box, Next, Astro and Svelte are parsers\n"
         " it calls once it knows which applies.\n\n"
         "Which means the phrase five platform gaps was wrong from the start. They were never five peers in a list; they\n"
         " are one generic path with four specific parsers hanging off it, and Box was the first of those parsers back\n"
         " when I was reading the names as a column. AddToCartFrontend is the entry point and the four sit beneath it, so\n"
         " the remaining item was not one more platform but the thing the other four hang from.\n\n"
         "IsFrontendUrl is the hinge. A store exposes an API and a page as deliberately different URLs, so a flow has to\n"
         " decide which it is holding before it decides how to read it, and the default direction is chosen rather than\n"
         " arbitrary: anything not recognisably an API is treated as a page, because reading a page as JSON fails loudly\n"
         " while calling a page as an API returns an HTML error body that parses to nothing and looks like an empty\n"
         " product.\n\n"
         "Three choices. API markers are matched with the query string stripped, since a page can carry any query and a\n"
         " marker inside one would be a false positive. Describe returns exactly the three parts the image names, so a\n"
         " caller cannot invent a fourth. And a relative path is reported as having no domain rather than being given one\n"
         " from context. The marker list itself is labelled inference, because the image names IsFrontendUrl and says\n"
         " nothing about what it tests.\n\n"
         "Figures: suite 1969 to 1981, freshness from three files to four and three hundred and seventy-one lines to\n"
         " four hundred and ninety-two, and the platform gaps from one to zero.\n\n"
         "Unknown: whether the ten API markers match the original's, which is inference; where Box sits in the tree, since\n"
         " it was built while reading the list as a column; and what the four remaining generic methods do, of which only\n"
         " the names survive.\n\n"
         "The lesson is that the shape of a to-do list decides how much of it can be closed. Read as a column, five names\n"
         " are five tasks; read as a tree, one of them is the umbrella and the task is to build the tree. While the shape\n"
         " was wrong the count fell one at a time and never got near done.\n\n"
         "Product code changed; suite green at 1981."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()