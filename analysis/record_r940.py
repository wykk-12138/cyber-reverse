"""Record R940: thirteen of thirteen by name was really eight, and four of the five have a surface but no step."""

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
### 13/13 按名字，实际是 **8 实现 + 5 只有名字**（R940）

**R939 说下一轮数「13 个里复刻件有几个」。数了 —— 而第一次的答案是错的。**

### 按名字查：13 / 13

**而六个只在 `AddToCartMatrix.cs` 里 —— 那是我上一轮写的**清单**。**

> **那是 R850 那个形状：「有形状没有内容」。一个在表里的名字不是一个方法。**

### 分开之后

| 有实现 | 8 |
|---|---|
| 只有名字 | 5 |

**而五个里四个不是同一种缺口。**

### 四个框架名：**有 surface、没有 step**

| 名字 | surface | step |
|---|---|---|
| `AddToCartNext` | ✅ `NextJsSurface` | **❌** |
| `AddToCartAstro` | ✅ `AstroSurface` | **❌** |
| `AddToCartSvelte` | ✅ `SvelteKitSurface` | **❌** |
| `AddToCartFrontend` | ✅ `FrontendSurface` | **❌** |

### 而这是最容易被读成「做完了」的形状

**一个单一计数会让人把四个 surface 当成四个做完的 step。**

### surface 不蕴含 step 的理由

**surface 回答**怎么读**；step 回答**往哪写**。**

> **读一个 Next 页面是解析 `script#__NEXT_DATA__`；而往它的车里写是调那个**店的** cart 端点 ——
> 而那**按店不同，不按框架不同**。同一个框架上的两家店，cart URL 就不一样。**

**所以四个 surface 不能拼成四个 step，声称能拼就是在**编造端点地址**。**

### 而第五个不一样

**`AddToCartDummy` —— 名字说它根本不和店说话，所以它是五个里**唯一不依赖端点证据**的那个。**

### 数字

| 度量 | R939 | **R940** |
|---|---|---|
| 套件 | 2001 | **2012** |
| 产物陈旧度 | 6 文件 / 666 行 | **7 文件 / 752 行** |
| **按名字** | 13 / 13 | 13 / 13 |
| **✓ 有实现** | 未分 | **8** |
| **只有名字** | 未分 | **5（其中 4 个有 surface）** |

### 教训

> **「13/13」是一个**会让人停止查看**的数字。
> 而它是真的 —— 每个名字都在源码里出现过。**
> **所以「在源码里出现过」这个判据，对「实现了吗」这个问题，是**不够的**。
> 而它不够的方式很安静：它给的是一个满分。**
"""

if "13/13 按名字，实际是 **8 实现 + 5 只有名字**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R940 appended")

VERDICT = """

---

## 第 940 轮：13/13 按名字，实际是 8 实现 + 5 只有名字

### 按名字查是 13/13 —— 而六个只在我上一轮写的清单里

> **那是 R850：「有形状没有内容」。一个在表里的名字不是一个方法。**

### 分开之后：8 实现 + 5 只有名字

**而五个里四个不是同一种缺口：**

| 名字 | surface | step |
|---|---|---|
| `AddToCartNext` | ✅ `NextJsSurface` | **❌** |
| `AddToCartAstro` | ✅ `AstroSurface` | **❌** |
| `AddToCartSvelte` | ✅ `SvelteKitSurface` | **❌** |
| `AddToCartFrontend` | ✅ `FrontendSurface` | **❌** |

### 这是最容易被读成「做完了」的形状

**一个单一计数会让人把四个 surface 当成四个做完的 step。**

### surface 不蕴含 step

**surface 答**怎么读**，step 答**往哪写**。**

> **读 Next 页面是解析 `script#__NEXT_DATA__`；往车里写是调那个**店的** cart 端点 ——
> 而那**按店不同，不按框架不同**。同框架的两家店 cart URL 就不一样。**

**所以声称四个 surface 能拼成四个 step，就是在**编造端点地址**。**

### 而第五个不一样

**`AddToCartDummy` 名字说它不和店说话 —— 五个里**唯一不依赖端点证据**的。**

### 数字

| 度量 | R939 | **R940** |
|---|---|---|
| 套件 | 2001 | **2012** |
| 产物陈旧度 | 6 / 666 | **7 / 752** |
| 按名字 | 13 / 13 | 13 / 13 |
| **有实现** | 未分 | **8** |
| **只有名字** | 未分 | **5（4 个有 surface）** |

### 教训

> **「13/13」是一个**会让人停止查看**的数字，而它是真的 —— 每个名字都在源码里出现过。
> 所以「在源码里出现过」对「实现了吗」这个问题**不够**，
> 而它不够的方式很安静：**它给的是一个满分。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — AddToCart 三列计数：8 实现 / 5 只有名字 / 4 有 surface 无 step（R940，**+11 用例**）

### 按名字 13/13 是假满分

**六个只在 `AddToCartMatrix.cs`（上一轮的清单）里 → R850「有形状没有内容」。**

### 真实分布

**有实现 8 · 只有名字 5 —— 而 5 里 4 个（Next/Astro/Svelte/Frontend）**有 surface、无 step**。**

### 为什么 surface ≠ step

**surface 答怎么读；step 答往哪写。cart 端点**按店不同不按框架不同** → 拼不出 step，声称能拼是编造地址。**

### 第五个不同

**`AddToCartDummy` —— 不和店说话，唯一不依赖端点证据的缺口。**

### `Scripts/AddToCartCoverage.cs`

**`Rows`(13，各带 note) · `SurfaceWithoutStep`(4) · `IndependentGap` · `ImplementedCount`/`NamedOnlyCount` ·
`IsImplemented` · `HasSurfaceWithoutStep`**

### 数字

**套件 2001 → 2012 · 陈旧度 6/666 → 7/752**

| 仍 Unknown | |
|---|---|
| 四个框架的 cart 端点 | 按店不同，未恢复 |
| `AddToCartDummy` 的行为 | 只有名字 |
| 是否还有第 14 个名字 | R939 未扫完 |

**纪律**：「在源码里出现过」对「实现了吗」不够 —— 而它不够的方式很安静：给的是一个满分。
"""

BLOCKER = """

---

## 364. 13/13 是假满分：实际 8 实现 + 5 只有名字

> R940。**改产品代码 +11 用例。** 套件 **2012 通过 / 0 失败 / 0 跳过**。

### 一、按名字 13/13，而六个只在上一轮的清单里

**→ R850「有形状没有内容」。一个在表里的名字不是一个方法。**

### 二、真实分布

**有实现 **8** · 只有名字 **5**。而 5 里 **4 个有 surface、无 step**：**

| 名字 | surface | step |
|---|---|---|
| `AddToCartNext` | `NextJsSurface` | ❌ |
| `AddToCartAstro` | `AstroSurface` | ❌ |
| `AddToCartSvelte` | `SvelteKitSurface` | ❌ |
| `AddToCartFrontend` | `FrontendSurface` | ❌ |

**这是最容易被读成「做完了」的形状 —— 单一计数会把四个 surface 当成四个 step。**

### 三、surface ≠ step

**surface 答**怎么读**；step 答**往哪写**。cart 端点**按店不同，不按框架不同**。
声称四个 surface 能拼成四个 step，就是在**编造端点地址**。**

### 四、第五个不同

**`AddToCartDummy` —— 名字说它不和店说话，五个里**唯一不依赖端点证据**的。**

### 五、数字

| 度量 | R939 | R940 |
|---|---|---|
| 套件 | 2001 | **2012** |
| 产物陈旧度 | 6 / 666 | **7 / 752** |
| 按名字 | 13 / 13 | 13 / 13 |
| **有实现** | 未分 | **8** |
| **只有名字** | 未分 | **5（4 个有 surface）** |

### 六、验证

```
grep 13 个名字 vs src        -> 13/13
排除清单文件后重数           -> 8 实现 / 5 只有名字
test --filter AddToCartCoverageTests -> 11 通过
metrics_report.py            -> 2012 通过 / 0 失败
```

### 七、仍然 Unknown

- **四个框架的 cart 端点**：**Unknown** —— 按店不同，未恢复。
- **`AddToCartDummy` 的行为**：**Unknown** —— 只有名字。
- **是否还有第 14 个名字**：**Unknown** —— R939 未扫完。

### 八、教训

**「13/13」是一个**会让人停止查看**的数字，而它是真的 —— 每个名字都在源码里出现过。**

**所以「在源码里出现过」对「实现了吗」这个问题不够。而它不够的方式很安静：它给的是一个满分。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R940", BLOCKER)
    ensure(RSTATUS, "R940", BLOCKER)
    ensure(RVERDICT, "第 940 轮", VERDICT)
    ensure(BACKLOG, "R940", BACKLOG_ADD)

    note = (
        "\n## R940 补充 — 13/13 是假满分：8 实现 + 5 只有名字（+11 用例，套件 2012）\n\n"
        "按名字查 13/13，而六个只在 AddToCartMatrix.cs（上一轮的清单）里 → R850「有形状没有内容」。\n\n"
        "真实分布：8 实现 / 5 只有名字；5 里 4 个（Next/Astro/Svelte/Frontend）有 surface 无 step。\n"
        "surface 答怎么读、step 答往哪写；cart 端点按店不同不按框架不同 → 拼不出 step。\n"
        "AddToCartDummy 是五个里唯一不依赖端点证据的。\n\n"
        "数字：套件 2001 → 2012 · 陈旧度 6/666 → 7/752。\n\n"
        "纪律：「在源码里出现过」对「实现了吗」不够 —— 它不够的方式很安静：给的是一个满分。\n\n"
        "下一轮：AddToCartDummy（唯一不依赖端点证据的缺口）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R940" not in h:
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
             for p, k in ((RBLOCK, "R940"), (RSTATUS, "R940"), (RVERDICT, "第 940 轮"), (BACKLOG, "R940")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R940: thirteen of thirteen by name was really eight, and four of the five look finished\n\n"
         "Asked how many of the thirteen AddToCart names the replica held, a name search answered thirteen of thirteen.\n"
         " Six of those were occurrences in the list written the round before, which is R850's shape without content:\n"
         " a name in a table is not a method. Splitting the count gives eight implemented and five named only.\n\n"
         "The five are not one kind of gap. Four of them -- Next, Astro, Svelte and Frontend -- each have a surface, a\n"
         " class that knows how to read that page's data, and lack a step, the call that turns a read product into a cart\n"
         " line. That is the shape most likely to be read as finished, because a single count would take four surfaces for\n"
         " four completed steps.\n\n"
         "And the surfaces cannot compose into steps. A surface answers how to read; a step answers where to write.\n"
         " Reading a Next page means parsing script#__NEXT_DATA__, while writing to its cart means calling the store's cart\n"
         " endpoint, which varies per shop rather than per framework -- two shops on the same framework have different\n"
         " cart URLs. Claiming four surfaces make four steps would mean inventing endpoint addresses.\n\n"
         "The fifth is different again. AddToCartDummy's name says it does not talk to a shop at all, which makes it the\n"
         " one of the five whose absence does not wait on endpoint evidence.\n\n"
         "Figures: suite 2001 to 2012, freshness from six files to seven and six hundred and sixty-six lines to seven\n"
         " hundred and fifty-two, and the count split into eight and five.\n\n"
         "Unknown: the four frameworks' cart endpoints, which vary per shop and were not recovered; what AddToCartDummy\n"
         " does, of which only the name survives; and whether a fourteenth name exists, since R939's scan was incomplete.\n\n"
         "The lesson is that thirteen of thirteen is a number that stops a reader looking, and it was true -- every name\n"
         " did occur in the source. So occurring in the source is not enough to answer whether something is implemented,\n"
         " and the way it falls short is quiet, because it returns full marks.\n\n"
         "Product code changed; suite green at 2012."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()