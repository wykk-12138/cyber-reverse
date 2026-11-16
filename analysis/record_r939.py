"""Record R939: the AddToCart family is a matrix of thirteen, and the scan found only nine of them."""

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
### `AddToCart` 是**十三个名字、四条轴**，而扫描只浮出九个（R939）

**R938 说「是否还有别的听起来像框架的名字 —— 未扫」。扫了，而扫描本身先错了一次。**

### 扫出九个，而它漏了四个

```
AddToCart · AddToCartApp · AddToCartAppDw · AddToCartBox · AddToCartDummy
AddToCartGraphQL · AddToCartMulti · AddToCartPreload · AddToCartPreloadGraphQL
```

**而直接查四个框架名，全都在：**

```
AddToCartNext 5 · AddToCartAstro 6 · AddToCartSvelte 5 · AddToCartFrontend 5
```

> **所以那次扫描**漏掉了全部四个框架名**。原因是 `n=40` —— 而 40 是**工具的上限**，不是镜像的数量。
> §2.7b 那条「先问这个来源是全量还是抽样」，我在用它的时候又忘了。**
> **而 `--cursor` 那条路也没通：翻 8 页仍是那 18 个 —— 所以「翻页」这个补救办法本身也不成立。
> 唯一可靠的是**直接查名字**。**

### 所以至少十三个

**而它们不并列 —— 有四条正交的轴：**

| 轴 | 值 |
|---|---|
| **transport** | plain（REST）· GraphQL |
| **client** | web · App · AppDw |
| **purpose** | plain · Preload · Multi · Dummy |
| **parser** | Next · Astro · Svelte · Frontend |

**而 `AddToCartPreloadGraphQL` 是 transport × purpose；`AddToCartAppDw` 是 client × 平台。**

> **一张十三项的列表**藏起这个结构** —— 而「列表」也正是两个名字被误分类的原因。**

### 而轴能解释名字，**不能生成名字**

**`AddToCartAppGraphQL` 由两个真实轴值组成 —— 而它**不在恢复到的十三个里**。**

> **所以 `Recovered` 是权威，轴只是对它的解释。
> 从轴生成第十四个名字，会是这几轮一直在找的那种**发明** —— 只不过这次发明的是「一个组合」。**

**而 `AddToCartBox` 是镜像自己给的**反例**：它在家族里，却不由任何轴组合而成 ——
**它是 PopMart 的一步。****

### 数字

| 度量 | R938 | **R939** |
|---|---|---|
| 套件 | 1990 | **2001** |
| 产物陈旧度 | 5 文件 / 561 行 | **6 文件 / 666 行** |
| **已记录的 AddToCart 名字** | 5（散落） | **13（有轴）** |

### 教训

> **同一个 §2.7b 我在**用它的时候**又犯了：`n=40` 就在输出里写着，而我读的是「扫出了九个」。
> 而它的补救办法（翻页）也不成立，所以我把「翻页没通」和「扫描不全」叠在了一起，
> 于是倾向于相信那九个是全部。**
> **唯一破掉它的是一个**直接查名字**的动作 —— 而那正是 §2.7b 说反向结论该用的方法。**
"""

if "`AddToCart` 是**十三个名字、四条轴**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R939 appended")

VERDICT = """

---

## 第 939 轮：`AddToCart` 是十三个名字、四条轴，而扫描只浮出九个

### 扫出九个，漏了四个

```
AddToCart · App · AppDw · Box · Dummy · GraphQL · Multi · Preload · PreloadGraphQL
```

**而直接查四个框架名，全在：`AddToCartNext` 5 · `AddToCartAstro` 6 · `AddToCartSvelte` 5 · `AddToCartFrontend` 5。**

> **`n=40` 是**工具上限**，不是镜像数量。§2.7b 我在用它的时候又忘了。
> 而 `--cursor` 翻 8 页仍是那 18 个 —— **补救办法本身也不成立。
> 唯一可靠的是直接查名字。**

### 四条正交的轴

| 轴 | 值 |
|---|---|
| transport | plain（REST）· GraphQL |
| client | web · App · AppDw |
| purpose | plain · Preload · Multi · Dummy |
| parser | Next · Astro · Svelte · Frontend |

**`AddToCartPreloadGraphQL` = transport × purpose；`AddToCartAppDw` = client × 平台。**

> **一张十三项列表藏起这个结构 —— 而「列表」也正是两个名字被误分类的原因。**

### 轴能解释，不能生成

**`AddToCartAppGraphQL` 由两个真实轴值组成 —— 而它**不在**恢复到的十三个里。**

> **所以 `Recovered` 是权威，轴只是解释。从轴生成第十四个名字是一种**发明**，
> 只不过发明的是「一个组合」。**

**而 `AddToCartBox` 是镜像自己给的反例 —— 在家族里，却不由轴组合而成。**

### 数字

| 度量 | R938 | **R939** |
|---|---|---|
| 套件 | 1990 | **2001** |
| 产物陈旧度 | 5 / 561 | **6 / 666** |
| AddToCart 名字 | 5（散落） | **13（有轴）** |

### 教训

> **`n=40` 就在输出里写着，而我读的是「扫出了九个」。
> 而补救办法（翻页）也不成立 → 「翻页没通」和「扫描不全」叠在一起，于是倾向于相信那九个是全部。**
> **唯一破掉它的是**直接查名字** —— 而那正是 §2.7b 说反向结论该用的方法。**
"""

BACKLOG_ADD = """

## 优先级 ① — AddToCart 矩阵：13 名字 / 4 轴（R939，**+11 用例**）

### 扫描只给了 9，而 40 是工具上限

**直接查四个框架名全在：Next 5 · Astro 6 · Svelte 5 · Frontend 5。`--cursor` 翻 8 页无效。**

### 13 个名字 + 4 条轴

**transport: plain/GraphQL · client: web/App/AppDw · purpose: plain/Preload/Multi/Dummy · parser: Next/Astro/Svelte/Frontend**

### `Scripts/AddToCartMatrix.cs`

**`Recovered`(13) · `Axes`(4) · `NotParsers`(Box) · `AxesOf` · `IsExplainedByAxes` · `ParserNames`(4)**

### 两条纪律

**① 轴能解释不能生成** —— `AddToCartAppGraphQL` 由真实轴值组成而不在恢复列表里。
**② `Box` 是镜像自己给的反例** —— 在家族里却不由轴组合。

### 数字

**套件 1990 → 2001 · 陈旧度 5/561 → 6/666 · AddToCart 名字 5 → 13**

| 仍 Unknown | |
|---|---|
| 是否还有第 14 个 | 扫描不全，需逐个直查 |
| `App` 与 `AppDw` 的差别 | AppDw ≈ Demandware |
| 13 个里复刻件有几个 | 未逐个数 |

**纪律**：`n=40` 是工具上限不是镜像数量；补救办法（翻页）也不成立时，唯一可靠的是直接查名字。
"""

BLOCKER = """

---

## 363. AddToCart 是 13 名字 / 4 轴；而扫描只给 9

> R939。**改产品代码 +11 用例。** 套件 **2001 通过 / 0 失败 / 0 跳过**。

### 一、扫描漏了全部四个框架名

```
扫出 9：AddToCart · App · AppDw · Box · Dummy · GraphQL · Multi · Preload · PreloadGraphQL
直查在：AddToCartNext 5 · AddToCartAstro 6 · AddToCartSvelte 5 · AddToCartFrontend 5
```

**`n=40` 是**工具上限**不是镜像数量；`--cursor` 翻 8 页仍是那 18 个 → 补救办法不成立。**

### 二、四条正交的轴

| 轴 | 值 |
|---|---|
| transport | plain · GraphQL |
| client | web · App · AppDw |
| purpose | plain · Preload · Multi · Dummy |
| parser | Next · Astro · Svelte · Frontend |

**`PreloadGraphQL` = transport × purpose；`AppDw` = client × 平台。**

### 三、轴能解释不能生成

**`AddToCartAppGraphQL` 由两个真实轴值组成，而**不在**恢复的 13 个里。
→ `Recovered` 是权威，从轴生成第 14 个名字是另一种发明。**

**`AddToCartBox` 是镜像自己给的反例：在家族里，不由轴组合成。**

### 四、数字

| 度量 | R938 | R939 |
|---|---|---|
| 套件 | 1990 | **2001** |
| 产物陈旧度 | 5 / 561 | **6 / 666** |
| **AddToCart 名字** | 5（散落） | **13（有轴）** |

### 五、验证

```
analysis/ida.py str "AddToCart"        -> n=40（工具上限），9 个去重名
analysis/ida.py str "AddToCartNext"    -> 5
test --filter AddToCartMatrixTests     -> 11 通过
metrics_report.py                      -> 2001 通过 / 0 失败
```

### 六、仍然 Unknown

- **是否还有第 14 个**：**Unknown** —— 扫描不全，需逐个直查。
- **`App` 与 `AppDw` 的差别**：**Inference** —— AppDw ≈ Demandware。
- **13 个里复刻件有几个**：**Unknown** —— 未逐个数。

### 七、教训

**`n=40` 就在输出里写着，而我读的是「扫出了九个」。**

**而补救办法（翻页）也不成立时，「翻页没通」和「扫描不全」叠在一起，于是倾向于相信那九个是全部。**

**唯一破掉它的是**直接查名字** —— 而那正是 §2.7b 说反向结论该用的方法。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R939", BLOCKER)
    ensure(RSTATUS, "R939", BLOCKER)
    ensure(RVERDICT, "第 939 轮", VERDICT)
    ensure(BACKLOG, "R939", BACKLOG_ADD)

    note = (
        "\n## R939 补充 — AddToCart 是 13 名字 / 4 轴；扫描只给 9（+11 用例，套件 2001）\n\n"
        "扫描 9 个（AddToCart/App/AppDw/Box/Dummy/GraphQL/Multi/Preload/PreloadGraphQL），"
        "而直查四个框架名全在（Next 5/Astro 6/Svelte 5/Frontend 5）→ n=40 是工具上限，--cursor 翻页无效。\n\n"
        "四条正交轴：transport(plain/GraphQL) · client(web/App/AppDw) · purpose(plain/Preload/Multi/Dummy) · "
        "parser(Next/Astro/Svelte/Frontend)。\n\n"
        "两条纪律：① 轴能解释不能生成（AddToCartAppGraphQL 由真实轴值组成而不在恢复列表）；"
        "② AddToCartBox 是镜像自己给的反例。\n\n"
        "数字：套件 1990 → 2001 · 陈旧度 5/561 → 6/666 · AddToCart 名字 5 → 13。\n\n"
        "纪律：n=40 是工具上限；补救办法不成立时唯一可靠的是直接查名字。\n\n"
        "下一轮：13 个里复刻件有几个（逐个对照）；或转优先级 ②。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R939" not in h:
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
             for p, k in ((RBLOCK, "R939"), (RSTATUS, "R939"), (RVERDICT, "第 939 轮"), (BACKLOG, "R939")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R939: the AddToCart family is thirteen names on four axes, and the scan found nine\n\n"
         "After two rounds finding that two of five names were misfiled, the question was whether more were. A scan gave\n"
         " nine: the plain method, App, AppDw, Box, Dummy, GraphQL, Multi, Preload and PreloadGraphQL. Direct queries then\n"
         " showed it had missed every framework-specific name -- AddToCartNext, Astro, Svelte and Frontend all exist -- so\n"
         " the family is at least thirteen. The scan's n was forty, which is the tool's ceiling rather than the image's\n"
         " count, and the paging fallback did not work either: eight pages returned the same eighteen. So the only\n"
         " reliable move was the one section 2.7b names for reverse conclusions, which is querying each name directly.\n\n"
         "The thirteen do not sit in a list. They sit on four independent axes: transport of plain or GraphQL, client of\n"
         " web, App or AppDw, purpose of plain, Preload, Multi or Dummy, and parser of Next, Astro, Svelte or Frontend.\n"
         " AddToCartPreloadGraphQL is transport times purpose and AddToCartAppDw is client times platform, so a flat list\n"
         " of thirteen hides the structure -- and a flat list is also how two names came to be misfiled.\n\n"
         "The axes explain the names but cannot generate them. AddToCartAppGraphQL combines two real axis values and is\n"
         " not among the recovered thirteen, so the list stays the authority and a fourteenth name derived from the axes\n"
         " would be an invention of the kind these rounds keep finding -- invented as a combination rather than as a\n"
         " word. And AddToCartBox is the image's own counter-example: in the family, explained by no axis, because it is a\n"
         " PopMart step.\n\n"
         "Figures: suite 1990 to 2001, freshness from five files to six and five hundred and sixty-one lines to six\n"
         " hundred and sixty-six, and the recorded family from five scattered names to thirteen with axes.\n\n"
         "Unknown: whether a fourteenth exists, since the scan is incomplete and each name would need its own query; how\n"
         " App differs from AppDw, inferred as Demandware; and how many of the thirteen the replica has, which was not\n"
         " counted one by one.\n\n"
         "The lesson is that n=40 was printed in the output and I read it as nine names. When the paging fallback also\n"
         " failed, incomplete-scan and broken-paging compounded into a reason to believe nine was all of them.\n\n"
         "Product code changed; suite green at 2001."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()