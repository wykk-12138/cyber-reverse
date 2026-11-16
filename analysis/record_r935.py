"""Record R935: Astro is a parallel code path, not a name -- and the island guess was wrong."""

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
### Astro **不是名字，是一整套并行代码路径** —— 而我的第一个假设是错的（R935）

**R934 说 Astro 40 条命中「先看里面有没有非名字的字面量」。看了，而它比名字多得多。**

### 方法族

```
ScrapeProductAstro · ScrapeVariantAvailabilityAstro · CheckPriceLimitAstro
AddToCartAstro · StartCheckoutAstro · ParseAstroProduct · ParseAstroImage
AstroAttribute · AstroProp · AstroProps
```

> **七个方法 + 三个名字，覆盖抓商品 / 查变体库存 / 查限价 / 加车 / 开始结账 / 解析商品 / 解析图片。
> 所以 Astro 在镜像里是一条**并行路径**，不是通用路径里的一个分支。**
> **而 `AddToCartAstro` 正是那五个平台缺口之一 —— 它不是一个开关，是七分之一。**

### 而我的第一个假设是**错的**

**Astro 最出名的机制是 island：`<astro-island props="{…}">`，我猜原版读的是那个 props 属性。**

**查了：**

```
astro-island     n=0
component-url    n=0
props=           n=0
```

**三条全空。所以原版读的不是 island 机制。**

### 而把假设排除掉之后，唯一那条字面量就浮出来了

```
data-astro-cid
```

**那是 Astro 给**每个渲染出的元素**打的属性（`data-astro-cid-XXXX`，后缀每次构建变），用来 scope 它的样式。**

> **这就是为什么方法族里有一个 `AstroAttribute` 夹在 `AstroProp` / `AstroProps` 之间 ——
> 它讲的是**从哪个属性认出这些元素**，而不是从哪个 JSON 里读字段。**

### 三个刻意的决定

**① 后缀不能硬编码。**与 Next 的 build hash 同理 —— 按**前缀**匹配。
**② 只暴露「匹配」与「列举」，不声称知道哪个元素是商品。**
**因为镜像给了前缀和方法名，两者对得上，但没有一段恢复到的代码显示有人用它拼过选择器。**
**③ 「没有 cid 属性」≠「不是 Astro 页面」。**
**scoped style 可以被剥掉，所以这是个**弱**结论，而代码只下这个弱结论（有测例钉住这句注释在）。**

### 而测试抓到我一个断言写错了

**`Assert.All(family, name => Assert.EndsWith("Astro", name))` ——
而 `ParseAstroProduct` / `ParseAstroImage` 的 Astro 在**中间**。
改成 `Contains`。**后缀形式只对动作类成立，因为它们是按步骤命名的。****

### 数字

| 度量 | R934 | **R935** |
|---|---|---|
| 套件 | 1946 | **1955** |
| 产物陈旧度 | 1 文件 / 142 行 | **2 文件 / 246 行**（正确累积） |
| `AddToCart` 平台缺口 | 3 剩 | **2 剩**（Frontend / Svelte —— 而 Astro 的机制已建） |

### 教训

> **假设先排除，比假设先实现便宜。**
> **我猜 island，查三条字面量、全 0、花了一次调用 —— 而如果我先写一个 island 解析器，
> 那会是一个**看起来能跑、而原版从不走**的路径。**
> **排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。**
"""

if "Astro **不是名字，是一整套并行代码路径**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R935 appended")

VERDICT = """

---

## 第 935 轮：Astro 是一整套并行路径 —— 而我的第一个假设被三条 0 否掉了

### 方法族

```
ScrapeProductAstro · ScrapeVariantAvailabilityAstro · CheckPriceLimitAstro
AddToCartAstro · StartCheckoutAstro · ParseAstroProduct · ParseAstroImage
AstroAttribute · AstroProp · AstroProps
```

> **七个方法 + 三个名字。所以 Astro 在镜像里是一条**并行路径**，不是通用路径里的分支。
> 而 `AddToCartAstro` 是那五个缺口之一 —— 它不是开关，是七分之一。**

### 而我的第一个假设是错的

**我猜原版读 island 的 props 属性。查了：`astro-island` 0 · `component-url` 0 · `props=` 0。**

### 排除之后，唯一那条字面量浮出来了

```
data-astro-cid
```

**Astro 给每个渲染出的元素打的属性（后缀每次构建变），用来 scope 样式。**

> **这就是为什么方法族里有个 `AstroAttribute` 夹在 `AstroProp` / `AstroProps` 之间 ——
> 它讲的是**从哪个属性认出元素**，不是从哪个 JSON 读字段。**

### 三个决定

**① 后缀不能硬编码** —— 按前缀匹配（同 Next 的 build hash）
**② 只暴露匹配与列举，不声称知道哪个元素是商品** —— 没有恢复到的代码显示有人用它拼过选择器
**③ 「没有 cid 属性」≠「不是 Astro 页面」** —— scoped style 可被剥掉，代码只下这个弱结论

### 而测试抓到我一个断言写错

**`EndsWith("Astro")` —— 而 `ParseAstroProduct` 的 Astro 在中间。改成 `Contains`。
**后缀形式只对动作类成立，因为它们是按步骤命名的。****

### 数字

| 度量 | R934 | **R935** |
|---|---|---|
| 套件 | 1946 | **1955** |
| 产物陈旧度 | 1 / 142 | **2 / 246**（正确累积） |
| AddToCart 平台缺口 | 3 剩 | **2 剩**（Frontend / Svelte） |

### 教训

> **假设先排除，比假设先实现便宜。**
> **我猜 island，查三条字面量、全 0、花了一次调用 ——
> 而如果先写一个 island 解析器，那会是一个**看起来能跑、而原版从不走**的路径。
> 排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。**
"""

BACKLOG_ADD = """

## 优先级 ① — Astro 并行路径（R935，**+9 用例**）

### 方法族（七 + 三）

**`ScrapeProductAstro` · `ScrapeVariantAvailabilityAstro` · `CheckPriceLimitAstro` · `AddToCartAstro` ·
`StartCheckoutAstro` · `ParseAstroProduct` · `ParseAstroImage` · `AstroAttribute` · `AstroProp` · `AstroProps`**

### 机制

**`data-astro-cid` —— Astro 给每个元素打的 scoped-style 属性，后缀按构建变。**

**而 island 假设被否：`astro-island` 0 · `component-url` 0 · `props=` 0。**

### `Scripts/AstroSurface.cs`

**`CidPrefix` · `AttributePattern`（前缀锚定）· `MethodFamily` · `Attributes` · `LooksLikeAstro` · `TagsWith`**

### 三个决定

**前缀匹配（后缀不硬编码）· 不声称知道哪个元素是商品 · 「无 cid」≠「非 Astro」**

### 数字

**套件 1946 → 1955 · 陈旧度 1/142 → 2/246 · AddToCart 平台缺口 3 → **2**（Frontend / Svelte）**

| 仍 Unknown | |
|---|---|
| 哪个 cid 元素是商品 | 无恢复代码显示选择器 |
| `AstroProp` 读的是哪层 | 只有名字 |
| Svelte 的机制 | 未查 |

**纪律**：排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。
"""

BLOCKER = """

---

## 359. Astro 是并行路径；island 假设被三条 0 否掉

> R935。**改产品代码 +9 用例。** 套件 **1955 通过 / 0 失败 / 0 跳过**。

### 一、方法族说明它是并行路径

```
ScrapeProductAstro · ScrapeVariantAvailabilityAstro · CheckPriceLimitAstro · AddToCartAstro
StartCheckoutAstro · ParseAstroProduct · ParseAstroImage · AstroAttribute · AstroProp · AstroProps
```

**七个方法 + 三个名字 → 不是分支，是七分之一。**

### 二、我的 island 假设是错的

```
astro-island n=0 · component-url n=0 · props= n=0
```

### 三、排除之后浮出的唯一字面量

**`data-astro-cid`** —— Astro 给每个渲染元素打的属性（后缀按构建变）。

**→ 这就是 `AstroAttribute` 夹在 `AstroProp`/`AstroProps` 之间的原因。**

### 四、三个决定

1. **后缀不硬编码** —— 按前缀匹配。
2. **只暴露匹配与列举** —— 不声称知道哪个元素是商品（无恢复代码显示选择器）。
3. **「无 cid」≠「非 Astro」** —— scoped style 可被剥掉。

### 五、测试抓到一个断言错

**`EndsWith("Astro")` vs `ParseAstroProduct` 的 Astro 在中间 → 改 `Contains`。**

### 六、数字

| 度量 | R934 | R935 |
|---|---|---|
| 套件 | 1946 | **1955** |
| 产物陈旧度 | 1 / 142 | **2 / 246** |
| **AddToCart 平台缺口** | 3 剩 | **2 剩**（Frontend / Svelte） |

### 七、验证

```
analysis/ida.py str "Astro"          -> 7 个方法名 + 3 个名字
analysis/ida.py str "astro-island"   -> 0
analysis/ida.py str "data-astro-cid" -> 1
test --filter AstroSurfaceTests      -> 9 通过
metrics_report.py                    -> 1955 通过 / 0 失败
```

### 八、仍然 Unknown

- **哪个 cid 元素是商品**：**Unknown** —— 无恢复代码显示选择器。
- **`AstroProp` 读的是哪一层**：**Unknown** —— 只有名字。
- **Svelte 的机制**：**Unknown** —— 未查。

### 九、教训

**假设先排除，比假设先实现便宜。**

**我猜 island，三条 0，花一次调用。而如果先写 island 解析器，那会是一条**看起来能跑、而原版从不走**的路径。**

**排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R935", BLOCKER)
    ensure(RSTATUS, "R935", BLOCKER)
    ensure(RVERDICT, "第 935 轮", VERDICT)
    ensure(BACKLOG, "R935", BACKLOG_ADD)

    note = (
        "\n## R935 补充 — Astro 是并行路径；island 假设被三条 0 否掉（+9 用例，套件 1955）\n\n"
        "方法族七个：ScrapeProductAstro / ScrapeVariantAvailabilityAstro / CheckPriceLimitAstro / AddToCartAstro / "
        "StartCheckoutAstro / ParseAstroProduct / ParseAstroImage，外加 AstroAttribute / AstroProp / AstroProps。\n\n"
        "island 假设被否：astro-island 0 · component-url 0 · props= 0。\n"
        "唯一机制字面量：data-astro-cid（后缀按构建变）→ 前缀匹配。\n\n"
        "三个决定：后缀不硬编码 · 不声称知道哪个元素是商品 · 「无 cid」≠「非 Astro」。\n\n"
        "测试抓到：EndsWith(Astro) vs ParseAstroProduct 的 Astro 在中间 → 改 Contains。\n\n"
        "数字：套件 1946 → 1955 · 陈旧度 1/142 → 2/246 · AddToCart 平台缺口 3 → 2（Frontend / Svelte）。\n\n"
        "纪律：排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。\n\n"
        "下一轮：Svelte（22 条，同法筛非名字字面量）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R935" not in h:
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
             for p, k in ((RBLOCK, "R935"), (RSTATUS, "R935"), (RVERDICT, "第 935 轮"), (BACKLOG, "R935")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R935: Astro is a parallel code path, and the island guess was ruled out by three zeros\n\n"
         "Astro looked like the weakest of the remaining AddToCart gaps, since the image names only the framework. It\n"
         " names a great deal more: seven methods covering scrape, variant availability, price limit, add to cart, start\n"
         " checkout and two parsers, plus AstroAttribute, AstroProp and AstroProps. That makes Astro a parallel code\n"
         " path rather than a branch inside the generic one, and AddToCartAstro is one seventh of it rather than a flag.\n\n"
         "My first hypothesis was Astro's island mechanism -- elements carrying a props attribute -- and three searches\n"
         " returned zero each: astro-island, component-url, props=. Ruling it out cost one call and made the literal\n"
         " that does exist findable: data-astro-cid, the attribute Astro stamps on every element it renders to scope its\n"
         " styles, with a per-build suffix. That is why an Attribute name sits among the Prop names.\n\n"
         "Three choices follow. The suffix cannot be hard-coded, so matching is by prefix. The class exposes matching and\n"
         " listing but does not claim to know which element holds the product, because the prefix and the method names\n"
         " fit together while no recovered code shows a selector built from them. And no cid attribute is a weak negative:\n"
         " scoped styles can be stripped, so the code claims only that this page carries none, never that it is not\n"
         " Astro.\n\n"
         "A test caught an assertion of mine: EndsWith(Astro) fails on ParseAstroProduct and ParseAstroImage, where the\n"
         " word sits in the middle. Containment is the right test; the suffix form only holds for the actions, which are\n"
         " named after the steps they perform.\n\n"
         "Figures: suite 1946 to 1955, freshness from one file to two and a hundred and forty-two lines to two hundred\n"
         " and forty-six, and AddToCart platform gaps from three remaining to two -- Frontend and Svelte.\n\n"
         "Unknown: which cid element is the product, since no selector survives; what layer AstroProp reads; and Svelte's\n"
         " mechanism, which is unchecked.\n\n"
         "The lesson is that ruling a hypothesis out is cheaper than implementing one. Guessing island and finding three\n"
         " zeros cost a single query, while writing an island parser first would have produced a path that runs and that\n"
         " the original never takes.\n\n"
         "Product code changed; suite green at 1955."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()