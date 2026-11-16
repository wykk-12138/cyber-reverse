"""Record R907: the AddToCart family measured at 8 of 15, with the seven absences named and sorted."""

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
### `AddToCart` 族量准了：**8 / 15**，而缺的 7 个里 5 个是真缺口（R907）

**R906 说「1,237 是上界，因为可能只是改名」。这一轮挑一族把它变成确数。**

### 而族不是 8 个，是 **15** 个

**R906 只看到 7 个变体，实际 15 个，而且带出现次数（所以「同一件事被多少处调用」是可读的）：**

| 名字 | 镜像 | 复刻件 | 判读 |
|---|---|---|---|
| `AddToCart` | 32 | **35** | 主干，齐 |
| `AddToCartPreload` | 11 | 2 | 有，但复刻件里用得少 |
| `AddToCartStoreFront` | 8 | 2 | 有 |
| `AddToCartMulti` | 6 | 2 | 有 |
| `AddToCartApp` | 3 | **7** | 有，且复刻件里更多 |
| `AddToCartAppDw` | 1 | **4** | 有 |
| `AddToCartGraphQL` | 1 | **8** | 有，且复刻件里更多 |
| `AddToCartPreloadGraphQL` | 1 | **5** | 有 |
| `AddToCart2` | 1 | **0** | **缺** |
| `AddToCartDummy` | 1 | **0** | **缺 —— 但原版这个是测试桩** |
| `AddToCartBox` | 1 | **0** | **缺 —— 谜盒加车** |
| `AddToCartFrontend` | 1 | **0** | **缺** |
| `AddToCartAstro` | 1 | **0** | **缺 —— 无头前端框架** |
| `AddToCartNext` | 1 | **0** | **缺 —— 同上** |
| `AddToCartSvelte` | 1 | **0** | **缺 —— 同上** |

### 所以 7 个缺失要分三类

| 类 | 名字 | 判读 |
|---|---|---|
| **真缺口** | `AddToCartBox` · `AddToCartFrontend` · `AddToCartAstro` · `AddToCartNext` · `AddToCartSvelte` | **5 个** |
| **测试桩** | `AddToCartDummy` | **原版自己的测试桩，不该复刻** |
| **不明** | `AddToCart2` | 只有名字 |

**所以这一族真实缺口是 5，不是 7。**

### 而 `AddToCartBox` 是一条我漏掉的线索

**R890 我记过 PopMart 的 `/shop/v1/box/*` 那 6 条端点（`boxCart/addBoxListToCart`、`box_set/extract`、
`box_spu/detail` 等），当端点记下了，**但没注意到原版有一个专门的方法 `AddToCartBox` 在用它们。**

**所以那 6 条端点的调用者现在有了名字 —— 这比「有 6 条端点没被调用」精确。**

### 三个无头框架变体说明一件事

**`Astro` · `Next` · `Svelte` 是三个前端框架。它们各有一个加车方法，意味着原版对**用这些框架搭的无头店**
有专门的加车路径 —— 而不是走通用 API。**

**所以「一家店一个实现」还不够准；更准的说法是**一个前端栈一个实现**。**
"""

if "`AddToCart` 族量准了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R907 appended")

VERDICT = """

---

## 第 907 轮：`AddToCart` 族量准了 —— 8/15，缺的 7 个里 5 个是真缺口

### 而族是 15 个，不是 R906 说的 8 个

| 名字 | 镜像 | 复刻件 | 判读 |
|---|---|---|---|
| `AddToCart` | 32 | **35** | 主干，齐 |
| `AddToCartPreload` | 11 | 2 | 有 |
| `AddToCartStoreFront` | 8 | 2 | 有 |
| `AddToCartMulti` | 6 | 2 | 有 |
| `AddToCartApp` | 3 | **7** | 有，复刻件更多 |
| `AddToCartAppDw` | 1 | **4** | 有 |
| `AddToCartGraphQL` | 1 | **8** | 有，复刻件更多 |
| `AddToCartPreloadGraphQL` | 1 | **5** | 有 |
| `AddToCart2` | 1 | **0** | **缺** |
| `AddToCartDummy` | 1 | **0** | **缺 —— 原版是测试桩** |
| `AddToCartBox` | 1 | **0** | **缺 —— 谜盒加车** |
| `AddToCartFrontend` | 1 | **0** | **缺** |
| `AddToCartAstro` | 1 | **0** | **缺 —— 无头前端** |
| `AddToCartNext` | 1 | **0** | **缺 —— 同上** |
| `AddToCartSvelte` | 1 | **0** | **缺 —— 同上** |

### 7 个缺失分三类

| 类 | 名字 | 数 |
|---|---|---|
| **真缺口** | `Box` · `Frontend` · `Astro` · `Next` · `Svelte` | **5** |
| **测试桩** | `Dummy` | 1 |
| **不明** | `2` | 1 |

> **所以这一族真实缺口是 5，不是 7。**

### 而 `AddToCartBox` 是一条我漏掉的线索

**R890 我记过 PopMart 的 `/shop/v1/box/*` 那 6 条端点，当端点记下了，
**但没注意到原版有一个专门的方法 `AddToCartBox` 在用它们。**

> **所以那 6 条端点的调用者现在有了名字 —— 这比「有 6 条端点没被调用」精确。**

### 三个无头框架变体说明一件事

**`Astro` · `Next` · `Svelte` 各有一个加车方法 → 原版对**用这些框架搭的无头店**有专门路径。**

> **所以「一家店一个实现」还不够准；更准的说法是**一个前端栈一个实现**。**

### 教训

> **R906 说 1,237 是上界。这一轮把一族变成确数：15 个名字，8 有 7 缺，而 7 个里 1 个是测试桩、5 个是真缺口。**
> **所以上界到确数之间隔着的动作是：**把名字按语义分类**，而不是按存不存在分类。**
"""

BACKLOG_ADD = """

## 判据 — `AddToCart` 族 **8/15**，真缺口 5（R907，**新工具 `tools/addtocart_family.py`**）

### 15 个名字（R906 只看到 8 个）

**`AddToCart` 32 · `Preload` 11 · `StoreFront` 8 · `Multi` 6 · `App` 3 · 其余 10 个各 1**

### 复刻件 8 有 / 7 缺

| 有 | `AddToCart` 35 · `Preload` 2 · `StoreFront` 2 · `Multi` 2 · `App` 7 · `AppDw` 4 · `GraphQL` 8 · `PreloadGraphQL` 5 |
|---|---|
| **缺** | **`2` · `Dummy` · `Box` · `Frontend` · `Astro` · `Next` · `Svelte`** |

### 缺失分三类

| 类 | 名字 | 数 |
|---|---|---|
| **真缺口** | `Box` · `Frontend` · `Astro` · `Next` · `Svelte` | **5** |
| **测试桩**（原版自有，不该复刻） | `Dummy` | 1 |
| 不明 | `2` | 1 |

### 两条新线索

**① `AddToCartBox` 是 PopMart `/shop/v1/box/*` 那 6 条端点的调用者** —— R890 只当端点记了，漏了方法。
**② `Astro`/`Next`/`Svelte` 各一个方法 → 「一个前端栈一个实现」，比「一家店一个实现」更准。**

| 仍 Unknown | |
|---|---|
| `AddToCart2` 是什么 | 只有名字 |
| 5 个真缺口各差什么 | 需读实现 |
| `Dummy` 是否真该排除 | 判读，非观察 |

**纪律**：**上界到确数之间隔着的动作是「按语义分类」，而不是「按存不存在分类」。**
"""

BLOCKER = """

---

## 331. `AddToCart` 族 **8/15**：真缺口 5，一个测试桩，一个不明

> R907。**新增工具，未改产品代码。**

### 一、族是 15 个，不是 8 个

| 名字 | 镜像 | 复刻件 |
|---|---|---|
| `AddToCart` | 32 | **35** |
| `AddToCartPreload` | 11 | 2 |
| `AddToCartStoreFront` | 8 | 2 |
| `AddToCartMulti` | 6 | 2 |
| `AddToCartApp` | 3 | **7** |
| `AddToCartAppDw` | 1 | **4** |
| `AddToCartGraphQL` | 1 | **8** |
| `AddToCartPreloadGraphQL` | 1 | **5** |
| **`AddToCart2`** | 1 | **0** |
| **`AddToCartDummy`** | 1 | **0** |
| **`AddToCartBox`** | 1 | **0** |
| **`AddToCartFrontend`** | 1 | **0** |
| **`AddToCartAstro`** | 1 | **0** |
| **`AddToCartNext`** | 1 | **0** |
| **`AddToCartSvelte`** | 1 | **0** |

### 二、7 个缺失分三类

| 类 | 名字 | 数 |
|---|---|---|
| **真缺口** | `Box` · `Frontend` · `Astro` · `Next` · `Svelte` | **5** |
| **测试桩**（原版自有） | `Dummy` | 1 |
| 不明 | `2` | 1 |

**所以这一族的真实缺口是 5，不是 7。「缺 7 个」里有一个是原版自己的测试桩，不该复刻。**

### 三、两条新线索

1. **`AddToCartBox` 是 PopMart `/shop/v1/box/*` 那 6 条端点的调用者。**
   **R890 我只当端点记了，没注意到有个专门方法在用它们 —— 所以「6 条端点没被调用」现在有了名字。**
2. **`Astro` · `Next` · `Svelte` 各有一个加车方法 → 「一个前端栈一个实现」，比「一家店一个实现」更准。**

### 四、验证

```
recovered_async_methods.txt 里 ^AddToCart  -> 15 个名字，共 70 次出现
tools/addtocart_family.py                  -> 8 有 / 7 缺，逐个列出镜像次数与复刻件次数
本轮未改产品代码；套件沿用 1805
```

### 五、仍然 Unknown

- **`AddToCart2` 是什么**：**Unknown** —— 只有名字，没有别的证据。
- **5 个真缺口各差什么**：**Unknown** —— 需读各自实现。
- **`Dummy` 是否真该排除**：**判断，不是观察** ——
  **它在原版里是测试桩这一点是从名字推的，也可能是 `dummy` 支付方式（`AddToCartDummy` 可能指用假支付加车）。**

### 六、教训

**R906 说「1,237 是上界」。这一轮把一族变成确数：15 个名字，8 有 7 缺。**

**而上界到确数之间隔着的动作不是「查得更细」，是**按语义分类** ——
「存在/不存在」是两格，「存在/真缺口/测试桩/不明」是四格，而四格才对应「该不该补」。**

**如果我按两格报，`AddToCartDummy` 会进待补清单；按四格报，它出局。
一个字的差别决定它占不占一轮。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R907", BLOCKER)
    ensure(RSTATUS, "R907", BLOCKER)
    ensure(RVERDICT, "第 907 轮", VERDICT)
    ensure(BACKLOG, "R907", BACKLOG_ADD)

    note = (
        "\n## R907 补充 — AddToCart 族 8/15，真缺口 5（新工具 tools/addtocart_family.py）\n\n"
        "族是 15 个名字不是 8 个：AddToCart 32 · Preload 11 · StoreFront 8 · Multi 6 · App 3 · 其余 10 各 1。\n\n"
        "复刻件 8 有（AddToCart 35 · Preload 2 · StoreFront 2 · Multi 2 · App 7 · AppDw 4 · GraphQL 8 · PreloadGraphQL 5），"
        "7 缺（2/Dummy/Box/Frontend/Astro/Next/Svelte）。\n\n"
        "缺失分三类：真缺口 5（Box/Frontend/Astro/Next/Svelte）· 测试桩 1（Dummy）· 不明 1（2）。\n\n"
        "两条新线索：AddToCartBox 是 PopMart /shop/v1/box/* 那 6 条端点的调用者；Astro/Next/Svelte 各一个方法 → "
        "「一个前端栈一个实现」比「一家店一个实现」更准。\n\n"
        "下一轮：补 AddToCartBox（那 6 条端点已有常量，等方法）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R907" not in h:
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
             for p, k in ((RBLOCK, "R907"), (RSTATUS, "R907"), (RVERDICT, "第 907 轮"), (BACKLOG, "R907")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R907: the AddToCart family measures eight of fifteen, and five of the seven absences are real\n\n"
         "R906 put async method coverage at twenty percent and called it an upper bound, since renaming is allowed and an\n"
         " absent name can be a present feature. This round takes the family where that can be checked cheaply and\n"
         " converts the bound into a count.\n\n"
         "The family is fifteen names rather than the eight R906 listed, and the table carries occurrence counts, so it\n"
         " also shows how many call sites each has. Eight are present: AddToCart with thirty-five, then Preload,\n"
         " StoreFront, Multi, App, AppDw, GraphQL and PreloadGraphQL, three of which the replica uses more than the\n"
         " image does. Seven are absent: AddToCart2, Dummy, Box, Frontend, Astro, Next and Svelte.\n\n"
         "Those seven split three ways. Five are real gaps -- Box, Frontend and the three frontend-framework variants.\n"
         "One is the original's own test stub. One, AddToCart2, has nothing but a name. So the family's true gap is\n"
         " five rather than seven.\n\n"
         "Two leads came out of the table. AddToCartBox is the caller of the six /shop/v1/box/ endpoints recorded in\n"
         " R890, which were noted as endpoints with nothing calling them; now they have a name. And the Astro, Next and\n"
         " Svelte variants each exist separately, which means the original has a cart path per headless frontend stack\n"
         " rather than per store -- a sharper statement than one implementation per store.\n\n"
         "Unknown: what AddToCart2 is, of which only the name survives; what each of the five real gaps differs in,\n"
         " which needs reading each implementation; and whether Dummy really should be excluded, since the test-stub\n"
         " reading is inferred from the name and it could equally mean a dummy payment method.\n\n"
         "The lesson is about category count. Going from an upper bound to a count does not take a finer search, it\n"
         " takes more categories: present and absent is two, but present, real gap, test stub and unknown is four, and\n"
         " only four answers whether something needs building. Reported the coarse way, the test stub enters the\n"
         " worklist and costs a round.\n\n"
         "New tool; no product code changed; suite carries at 1805."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
