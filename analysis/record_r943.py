"""Record R943: all thirteen placed, the concatenation caveat, and the flaky suite run."""

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
### 13 / 13 全部定位，而**两个来源都不是我想的那个**（R943）

**R942 说 7 个定不了位。这一轮补上了，而过程中两个假设先后被否。**

### 假设一：用描述符表 —— 错的

**`analysis/binding_descriptors.tsv` 有 1,637 条，字段是 `declaring_type / owner_assembly / member / accessor`。**

**而七个名字**一条都不在里面**。**

> **原因不是它们不存在，而是那张表只装**绑定**（带 Getter/Setter 的属性）。
> `AddToCart*` 是**方法**，永远不在里面。**
> **所以那不是「缺席」，是**问错了表**。**

### 假设二：用序号连号 —— 在这七个身上也不可靠

**读它们各自的字符串，序号是这样的：**

```
AddToCartBox        ExtractPopNow(83) · SelectPopNow(840) · AddToCartBox(864) · SelectMultiPopNowUS(87)
AddToCartNext       AddToCartNext(364) · ScrapeProductSvelte(378) · CheckPriceLimitSvelte(39)
```

> **`840` 与 `864` 之间夹着 `85`/`87` —— 序号被**截断成三位**了。所以这些字符串里的序号不可信。**

### 但**邻居名**可信，而它给了七类

| 名字 | 邻居 | 类 |
|---|---|---|
| `AddToCartBox` | `ExtractPopNow` · `SelectPopNow` · `PreviewBoxes` · `FetchAddress` | **PopMart 抽签**（第三次确认） |
| `AddToCartGraphQL` | `GetAccessToken` · `CartApiObjectCreate` | **购物车 API** |
| `AddToCartPreloadGraphQL` | `CreateCartGraphql` · `GetCartAvailabilityGraphql` | **GraphQL 车** |
| `AddToCartNext` | `ScrapeProductSvelte` · `CheckPriceLimitSvelte` | **框架抓取** |
| `AddToCartAstro` | `StartCheckoutAstro` · `ScrapeProductNext` · `CheckPriceLimitNext` | **框架抓取** |
| `AddToCartSvelte` | `RefreshSession` | **会话** |
| `AddToCartFrontend` | `AddToCart` · `AddToCartPreload` | **网页结账** |

### 而 `AddToCartNext` 旁边是 **Svelte** 的名字 —— 那是**拼接伪影**

**它是 `Next`，旁边却是 `ScrapeProductSvelte` / `CheckPriceLimitSvelte`。**

> **所以这些字符串是多个类的连号 run **拼接**在一起的。
> 而邻居名只能说明「这一类里有抓取方法」，**不能说明这两个名字同类**。**
> **所以表里的「类」是**这一段的性质**，不是这两个方法共享的类。而我把这个区别写进了常量注释和测例名。****

### 数字

| 度量 | R942 | **R943** |
|---|---|---|
| 套件 | 2036 | **2036** |
| 产物陈旧度 | 9 文件 / 916 行 | **9 文件 / 920 行** |
| **连号定位** | 6 / 13 | **13 / 13（7 个靠邻居名）** |

### 而套件红过一次 —— 是偶发

**第一次 `metrics_report.py` 报 1 失败；直接跑全量 **2340 通过 / 0 失败 / 2 跳过**；
再跑 metrics **2036 通过 / 0 失败**。**

> **所以那一次是**偶发**，不是真失败。而 §2.6 那条「没跑成 ≠ 通过」的反面也成立：
> **红一次 ≠ 真红** —— 但要说清是重跑才绿的，而不是把那次红抹掉。****

### 教训

> **这一轮两个假设都被否，而两个都是**问错了来源**：
> 描述符表装绑定不装方法；序号在拼接串里被截断。**
> **而两次的错误形式相同：**一个能回答相邻问题的来源，被我当成了能回答这个问题的来源。**
> **而它们的输出都不报错 —— 描述符表给出「不在表里」，序号给出一个看起来正常的数字。**
"""

if "13 / 13 全部定位" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R943 appended")

VERDICT = """

---

## 第 943 轮：13/13 全部定位，而两个来源都不是我想的那个

### 假设一：描述符表 —— 错的

**`binding_descriptors.tsv` 1,637 条，七个名字**一条都不在**。
原因不是缺席 —— 那张表只装**绑定**（属性），`AddToCart*` 是**方法**。**

> **不是「缺席」，是**问错了表**。**

### 假设二：序号连号 —— 在这七个身上也不可靠

```
AddToCartBox   ExtractPopNow(83) · SelectPopNow(840) · AddToCartBox(864) · SelectMultiPopNowUS(87)
```

**`840` 与 `864` 之间夹着 `85`/`87` —— 序号被**截断成三位**。不可信。**

### 但邻居名可信，给了七类

| 名字 | 邻居 | 类 |
|---|---|---|
| `AddToCartBox` | `ExtractPopNow` · `PreviewBoxes` | PopMart 抽签（三次确认） |
| `AddToCartGraphQL` | `GetAccessToken` · `CartApiObjectCreate` | 购物车 API |
| `AddToCartPreloadGraphQL` | `CreateCartGraphql` | GraphQL 车 |
| `AddToCartNext` | `ScrapeProductSvelte` | 框架抓取 |
| `AddToCartAstro` | `StartCheckoutAstro` · `ScrapeProductNext` | 框架抓取 |
| `AddToCartSvelte` | `RefreshSession` | 会话 |
| `AddToCartFrontend` | `AddToCart` · `AddToCartPreload` | 网页结账 |

### 而 `Next` 旁边是 **Svelte** 的名字 —— 拼接伪影

> **这些字符串是多个类的连号 run **拼接**的。邻居名只能说明「这一段里有抓取方法」，
> 不能说明这两个名字同类。**所以表里的「类」是**这一段的性质**，不是共享的类** ——
> 这个区别写进了常量注释和测例名。**

### 数字

| 度量 | R942 | **R943** |
|---|---|---|
| 套件 | 2036 | **2036** |
| 产物陈旧度 | 9 / 916 | **9 / 920** |
| 连号定位 | 6 / 13 | **13 / 13** |

### 而套件红过一次 —— 偶发

**第一次 metrics 报 1 失败；直接全量 **2340 通过 / 0 失败 / 2 跳过**；再跑 metrics **2036 / 0**。**

> **§2.6 的反面也成立：红一次 ≠ 真红 —— 但要说清是重跑才绿的。**

### 教训

> **两个假设都被否，都是**问错了来源**：描述符表装绑定不装方法；序号在拼接串里被截断。
> 而错误形式相同：**一个能回答相邻问题的来源，被当成了能回答这个问题的来源。**
> 而它们都不报错 —— 描述符表给出「不在表里」，序号给出一个看起来正常的数字。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — 13/13 定位；两个来源被否；拼接伪影（R943，**改代码 + 改测例**）

### 被否的来源

1. **`binding_descriptors.tsv`（1637 条）只装绑定不装方法 → 七个一条都不在，那是问错表。**
2. **序号在拼接串里被截断成三位（840 与 864 之间夹 85/87）→ 不可信。**

### 可信的是邻居名 → 七类

**PopMart 抽签 · 购物车 API · GraphQL 车 · 框架抓取 ×2 · 会话 · 网页结账**

### 而 `AddToCartNext` 旁边是 Svelte 名 —— 拼接伪影

**字符串是多个类的 run 拼接的 → 邻居名说明「这一段有抓取方法」，不说明两个名字同类。
表里的「类」是**这一段的性质**。**

### 数字

**套件 2036（红一次后重跑绿）· 陈旧度 9/916 → 9/920 · 定位 6/13 → **13/13****

| 仍 Unknown | |
|---|---|
| 每个方法真正的所属类 | 序号不可信 |
| 框架抓取类的归属 | 拼接伪影掩盖 |
| 是否还有误读名字 | 已定位 13 个，只能对它们下结论 |

**纪律**：一个能回答**相邻**问题的来源，不能当成能回答**这个**问题的来源 —— 而它不会报错。
"""

BLOCKER = """

---

## 367. 13/13 定位；两个来源被否；拼接伪影

> R943。**改代码 + 改测例。** 套件 **2036 通过 / 0 失败 / 0 跳过**（红一次后重跑绿）。

### 一、假设一被否：描述符表只装绑定

**`binding_descriptors.tsv` 1,637 条，七个名字一条不在。原因：装属性不装方法 → **问错了表**。**

### 二、假设二被否：序号被截断

```
AddToCartBox  ExtractPopNow(83) · SelectPopNow(840) · AddToCartBox(864) · SelectMultiPopNowUS(87)
```

**840 与 864 之间夹 85/87 → 三位截断 → 序号不可信。**

### 三、可信的是邻居名

| 名字 | 邻居 | 类 |
|---|---|---|
| `AddToCartBox` | `ExtractPopNow` · `PreviewBoxes` | PopMart 抽签 |
| `AddToCartGraphQL` | `GetAccessToken` · `CartApiObjectCreate` | 购物车 API |
| `AddToCartPreloadGraphQL` | `CreateCartGraphql` | GraphQL 车 |
| `AddToCartNext` | `ScrapeProductSvelte` | 框架抓取 |
| `AddToCartAstro` | `StartCheckoutAstro` · `ScrapeProductNext` | 框架抓取 |
| `AddToCartSvelte` | `RefreshSession` | 会话 |
| `AddToCartFrontend` | `AddToCart` · `AddToCartPreload` | 网页结账 |

### 四、拼接伪影

**`AddToCartNext` 旁边是 Svelte 名 —— 字符串是多类 run 拼接的。
邻居名说明「这一段有抓取方法」，不说明两个名字同类。**

### 五、套件红过一次

**第一次 metrics 1 失败 → 直接全量 2340/0/2 → 再跑 metrics 2036/0。
**红一次 ≠ 真红，但要写清是重跑才绿的。****

### 六、数字

| 度量 | R942 | R943 |
|---|---|---|
| 套件 | 2036 | **2036** |
| 产物陈旧度 | 9 / 916 | **9 / 920** |
| **定位** | 6 / 13 | **13 / 13** |

### 七、验证

```
binding_descriptors.tsv 查 7 名 -> 0 命中（表装绑定）
各名字自身字符串          -> 邻居名七类齐全
test --filter AddToCartPlacementTests -> 13 通过
metrics_report.py         -> 2036 通过 / 0 失败
```

### 八、仍然 Unknown

- **每个方法真正的所属类**：**Unknown** —— 序号不可信。
- **框架抓取类的归属**：**Unknown** —— 拼接伪影掩盖。
- **是否还有误读名字**：**Unknown** —— 只能对已定位 13 个下结论。

### 九、教训

**两个假设都被否，都是**问错了来源**：描述符表装绑定不装方法；序号在拼接串里被截断。**

**错误形式相同：一个能回答**相邻**问题的来源，被当成了能回答**这个**问题的来源。**

**而它们都不报错 —— 描述符表给出「不在表里」，序号给出一个看起来正常的数字。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R943", BLOCKER)
    ensure(RSTATUS, "R943", BLOCKER)
    ensure(RVERDICT, "第 943 轮", VERDICT)
    ensure(BACKLOG, "R943", BACKLOG_ADD)

    note = (
        "\n## R943 补充 — 13/13 定位；两个来源被否；拼接伪影（套件 2036，红一次后重跑绿）\n\n"
        "假设一被否：binding_descriptors.tsv 只装绑定（属性）不装方法 → 七个查不到是问错表。\n"
        "假设二被否：序号在拼接串里被截断成三位（840 与 864 之间夹 85/87）→ 不可信。\n\n"
        "可信的是邻居名 → 七类：PopMart 抽签 / 购物车 API / GraphQL 车 / 框架抓取×2 / 会话 / 网页结账。\n"
        "而 AddToCartNext 旁边是 Svelte 名 = 拼接伪影 → 邻居名只说明「这一段有抓取方法」，不说明同类。\n\n"
        "套件：第一次 metrics 1 失败 → 直接全量 2340/0/2 → 再跑 metrics 2036/0 = 偶发。\n\n"
        "数字：定位 6/13 → 13/13 · 陈旧度 9/916 → 9/920。\n\n"
        "纪律：一个能回答「相邻」问题的来源，不能当成能回答「这个」问题的来源 —— 而它不会报错。\n\n"
        "下一轮：转优先级 ②（风控对抗）或 ③（请求与指纹层）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R943" not in h:
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
             for p, k in ((RBLOCK, "R943"), (RSTATUS, "R943"), (RVERDICT, "第 943 轮"), (BACKLOG, "R943")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R943: all thirteen placed, after two sources were ruled out for answering the wrong question\n\n"
         "R942 left seven names unplaced. Filling them in turned on two assumptions that both failed. The binding\n"
         " descriptor table has 1637 entries and none of the seven appears in it -- not because they are missing but\n"
         " because that table holds bindings, properties with accessors, while the AddToCart names are methods. That is\n"
         " asking the wrong table, not an absence.\n\n"
         "The second assumption was that consecutive ordinals would place them, and those strings have their ordinals\n"
         " truncated to three digits: AddToCartBox reads 864 while its neighbours read 840, 85 and 87. So the numbers in\n"
         " these particular strings cannot be trusted either.\n\n"
         "What is trustworthy is the neighbour names, and they give seven classes: PopMart draw for Box, cart API for\n"
         " GraphQL, GraphQL cart for PreloadGraphQL, framework scrape for Next and Astro, session for Svelte, and web\n"
         " checkout for Frontend. But AddToCartNext's neighbours are ScrapeProductSvelte and CheckPriceLimitSvelte, which\n"
         " says these strings concatenate several classes' runs together. A neighbour therefore tells you what the\n"
         " segment contains, not that the two names share a class, and that distinction is written into both the constant\n"
         " comment and the test's name.\n\n"
         "The suite went red once and then green: the first metrics run reported a failure, a direct full run gave 2340\n"
         " passed with two skipped, and metrics again gave 2036 with none. So it was flaky, which is the mirror of section\n"
         " 2.6 -- red once is not truly red, provided the round says the green came from a rerun rather than erasing the\n"
         " red.\n\n"
         "Figures: thirteen of thirteen placed, six by adjacency and seven by neighbour name; freshness nine files and\n"
         " nine hundred and twenty lines; suite 2036.\n\n"
         "Unknown: each method's real class, since the ordinals are unreliable; where the framework scrape classes sit,\n"
         " which the concatenation hides; and whether any name is still misfiled, since only the thirteen can be judged.\n\n"
         "The lesson is that both sources answered an adjacent question rather than this one -- a table of bindings for a\n"
         " question about methods, ordinals from concatenated strings for a question about class membership -- and neither\n"
         " reported an error. One said not in the table; the other gave numbers that look normal.\n\n"
         "Code and a test changed; suite green at 2036 after one flaky red."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()