"""Record R934: Next.js surface from a selector and a regex, closing the second AddToCart gap."""

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
### Next.js：一条**选择器** + 一条**正则**（R934）

**回到优先级 ①。R909 的 `AddToCart` 五个平台缺口里 `Box` 已做，这一轮做 Next。**

**而 Next 和 Astro / Svelte 不一样 —— 后面两个镜像里只有**框架名**，而 Next 有四条具体字面量：**

```
"script#__NEXT_DATA__"
"/_next/static/chunks/app/[^\\"']*?page-[0-9a-f]+\\\\.js"
"/_next/"
"/pay/_next/"
```

### 这两条合起来就是机制

**① `script#__NEXT_DATA__` —— Next 页面把自己的数据放在这个 id 的 script 里，JSON。**
**② 那条正则找的是 app-router 的页面 chunk：`page-<hash>.js`。**

> **而第二条为什么必须用正则而不是拼路径：**build hash 是每次部署变的**，拼不出来，只能从页面读。
> 镜像里给的是一条**匹配**，不是一条**模板** —— 这本身就是证据：原版也是读出来的。**

### 三个刻意的决定

**① 按 id 找，不按「第几个 script」。**
**页面的 script 顺序镜像没说任何事，按位置找会在任何一次页面调整时静默失效。**

**② 「在哪找到的」要报出来。**

| 返回 | 含义 |
|---|---|
| `PageProps` | `props.pageProps` 下 —— **Next 惯例路径** |
| `Elsewhere` | 文档别处 —— **找到了，但不是靠结构** |
| `Absent` | 没有 |

> **因为「按惯例找到」和「搜到了」是两种不同的证据强度。
> 把它们合成一个「找到了」，会让调用方以为结构被确认了，而实际只是搜索成功。**

**③ app-router 与 pages-router 分开。**
**正则是 `chunks/app/`，所以 `chunks/pages/index-abc123.js` **不该**匹配 ——
把两个 router 当一个会拼出镜像不用的路径。有测例钉住这条。**

### 而测试抓到一个 HTML 细节

**`<script id=__NEXT_DATA__>` —— **无引号是合法 HTML**，而我的正则要求引号，于是它被拒。**

**修：值匹配接受有引号与无引号两种。**
**而这条测例是特意写的 —— 因为压缩器会产出无引号属性，而「压缩器会做的事」正是这类解析器要能吃的输入。**

### 数字

| 度量 | R933 | **R934** |
|---|---|---|
| 套件 | 1932 | **1946** |
| 产物陈旧度 | 0 / current | **1 文件 / 142 行**（新文件，正确） |
| `AddToCart` 平台缺口 | Box 已做，4 剩 | **Box + Next 已做，3 剩**（Frontend / Astro / Svelte） |

**而陈旧度那一行现在自己证明了它的用途：这一轮加了一个文件，它就报 1 —— 不需要谁记得去查。**

### 教训

> **同一个「平台缺口」，三个平台的证据量差一个数量级：
> Astro 只有框架名（40 条但都是名字），Svelte 只有名字，而 Next 有一条选择器和一条正则。**
> **所以「做完 Astro / Svelte / Frontend」不会是同一件事做三遍 —— 而先做 Next 是对的，
> 因为它是唯一能核**形状**的那个。**
"""

if "Next.js：一条**选择器** + 一条**正则**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R934 appended")

VERDICT = """

---

## 第 934 轮：Next.js —— 一条选择器 + 一条正则

### 四条第字面量

```
"script#__NEXT_DATA__"
"/_next/static/chunks/app/[^\\"']*?page-[0-9a-f]+\\\\.js"
"/_next/"  ·  "/pay/_next/"
```

### 这两条合起来就是机制

**① 数据在那个 id 的 script 里（JSON）。**
**② 那条正则找 app-router 的页面 chunk。**

> **为什么必须用正则：**build hash 每次部署都变**，拼不出来，只能从页面读。
> 镜像给的是一条**匹配**而不是**模板** —— 这本身就是证据：原版也是读出来的。**

### 三个决定

**① 按 id 找，不按「第几个 script」** —— 顺序镜像没说任何事
**② 「在哪找到的」要报出来：`PageProps`（惯例路径）/ `Elsewhere`（搜索成功）/ `Absent`**
> **「按惯例找到」与「搜到了」是两种证据强度；合成一个「找到了」会让调用方以为结构被确认了。**
**③ app-router 与 pages-router 分开** —— `chunks/pages/…` **不该**匹配，有测例钉住

### 测试抓到一个 HTML 细节

**`<script id=__NEXT_DATA__>` 无引号是合法 HTML，而正则需要引号 → 修成两种都接受。
压缩器会产出无引号属性，而那正是这类解析器要能吃的输入。**

### 数字

| 度量 | R933 | **R934** |
|---|---|---|
| 套件 | 1932 | **1946** |
| 产物陈旧度 | 0 / current | **1 文件 / 142 行**（新文件，正确） |
| AddToCart 平台缺口 | 4 剩 | **3 剩**（Frontend / Astro / Svelte） |

**陈旧度那一行现在自己证明了用途：加一个文件它就报 1，不需要谁记得去查。**

### 教训

> **同一个「平台缺口」，三个平台的证据量差一个数量级：
> Astro 与 Svelte 只有框架名，而 Next 有一条选择器和一条正则。**
> **所以先做 Next 是对的 —— 它是唯一能核**形状**的那个。**
"""

BACKLOG_ADD = """

## 优先级 ① — Next.js surface（R934，**+14 用例**）

### 四条字面量

```
script#__NEXT_DATA__                                       选择器
/_next/static/chunks/app/[^"']*?page-[0-9a-f]+\\.js         正则
/_next/  ·  /pay/_next/                                    资源根
```

### `Scripts/NextJsSurface.cs`

**`DataSelector` · `PageChunkPattern` · `AssetRoot` · `PayAssetRoot` · `ExtractDataJson` · `FindProperty` · `PageChunks`**

### 三个决定

**按 id 找（不按位置）· `Found.{PageProps,Elsewhere,Absent}` 报证据强度 · app-router 与 pages-router 分开**

### 一个 HTML 细节被测试抓到

**无引号 `id=__NEXT_DATA__` 是合法 HTML 而正则需要引号 → 两种都接受（压缩器会产出无引号的）。**

### 数字

**套件 1932 → 1946 · 产物陈旧度 0 → 1 文件 / 142 行（正确）· AddToCart 平台缺口 4 → **3**（Frontend / Astro / Svelte）**

| 仍 Unknown | |
|---|---|
| `props.pageProps` 的真实字段名 | 只有惯例 |
| `/_next/` 与 `/pay/_next/` 的区别 | 后者是支付页 |
| Astro / Svelte / Frontend 的机制 | 只有框架名 |

**纪律**：同一个「平台缺口」，证据量可以差一个数量级 —— 先做能核形状的那个。
"""

BLOCKER = """

---

## 358. Next.js surface：第二条 AddToCart 平台缺口关闭

> R934。**改产品代码 +14 用例。** 套件 **1946 通过 / 0 失败 / 0 跳过**。

### 一、四条字面量

```
"script#__NEXT_DATA__"                                     a CSS selector
"/_next/static/chunks/app/[^\\"']*?page-[0-9a-f]+\\\\.js"    a regex
"/_next/"                                                  asset root
"/pay/_next/"                                              a payment page's asset root
```

### 二、机制

**① 数据在 `script#__NEXT_DATA__` 里（JSON）。**
**② 正则找 app-router 页面 chunk。**

**为什么用正则而非模板：build hash 每次部署都变。镜像给的是**匹配**不是**模板** —— 这本身说明原版也是读出来的。**

### 三、三个决定

1. **按 id 找，不按「第几个 script」** —— 顺序镜像没说任何事。
2. **`Found.{PageProps, Elsewhere, Absent}`** —— 「按惯例找到」与「搜到了」是两种证据强度，
   合成一个会让调用方以为结构被确认了。
3. **app-router 与 pages-router 分开** —— `chunks/pages/index-abc123.js` 不该匹配，有测例钉住。

### 四、一个 HTML 细节被测试抓到

**`<script id=__NEXT_DATA__>` 无引号是合法 HTML，而正则要求引号 → 修成两种都接受。
压缩器会产出无引号属性 —— 而那正是这类解析器要能吃的输入。**

### 五、数字

| 度量 | R933 | R934 |
|---|---|---|
| 套件 | 1932 | **1946** |
| 产物陈旧度 | 0 / current | **1 文件 / 142 行**（新文件，正确） |
| **AddToCart 平台缺口** | 4 剩 | **3 剩**（Frontend / Astro / Svelte） |

### 六、验证

```
test --filter NextJsSurfaceTests -> 14 通过
metrics_report.py                -> 1946 通过 / 0 失败；陈旧度 1 文件 / 142 行
```

### 七、仍然 Unknown

- **`props.pageProps` 的真实字段名**：**Unknown** —— 只有惯例。
- **`/_next/` 与 `/pay/_next/` 的区别**：**Inference** —— 后者是支付页的资源根。
- **Astro / Svelte / Frontend 的机制**：**Unknown** —— 镜像里只有框架名。

### 八、教训

**同一个「平台缺口」，三个平台的证据量差一个数量级：Astro 与 Svelte 只有框架名，Next 有选择器加正则。**

**所以先做 Next 是对的 —— 它是唯一能核**形状**的那一个。
而陈旧度那一行现在自己证明了用途：加一个文件它就报 1，不需要谁记得去查。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R934", BLOCKER)
    ensure(RSTATUS, "R934", BLOCKER)
    ensure(RVERDICT, "第 934 轮", VERDICT)
    ensure(BACKLOG, "R934", BACKLOG_ADD)

    note = (
        "\n## R934 补充 — Next.js surface（改产品代码 +14 用例，套件 1946）\n\n"
        "四条字面量：script#__NEXT_DATA__（选择器）· /_next/static/chunks/app/[^\"']*?page-[0-9a-f]+\\.js（正则）· "
        "/_next/ · /pay/_next/。\n\n"
        "机制：数据在那个 id 的 script 里（JSON）；正则找 app-router chunk（build hash 每次部署变，只能读不能拼）。\n\n"
        "三个决定：按 id 找不按位置 · Found.{PageProps,Elsewhere,Absent} 报证据强度 · app-router 与 pages-router 分开。\n\n"
        "测试抓到：无引号 id=__NEXT_DATA__ 是合法 HTML 而正则需要引号 → 两种都接受（压缩器会产无引号的）。\n\n"
        "数字：套件 1932 → 1946 · 陈旧度 0 → 1 文件 / 142 行（正确）· AddToCart 平台缺口 4 → 3（Frontend/Astro/Svelte）。\n\n"
        "纪律：同一「平台缺口」证据量可差一个数量级 —— 先做能核形状的那个。\n\n"
        "下一轮：Astro（40 条命中，先看里面有没有非名字的字面量）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R934" not in h:
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
             for p, k in ((RBLOCK, "R934"), (RSTATUS, "R934"), (RVERDICT, "第 934 轮"), (BACKLOG, "R934")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R934: Next.js, the second AddToCart platform gap, from a selector and a regex\n\n"
         "Back to the checkout priority, where AddToCart had five platform gaps and Box closed one. Next is the second,\n"
         " and unlike Astro and Svelte -- which the image names only as words -- it comes with four specific literals: the\n"
         " selector script#__NEXT_DATA__, the page-chunk regex, and two asset roots.\n\n"
         "Those two say the mechanism outright. A Next page exposes its own data as JSON in the script carrying that id,\n"
         " and the regex finds the app-router chunk rendering the current route. The second has to be a match rather than\n"
         " a template because the build hash changes with every deployment -- and the image giving a pattern instead of a\n"
         " path is itself evidence that the original reads it out of the page too.\n\n"
         "Three choices. The element is matched by id rather than by position, since the image says nothing about script\n"
         " order and a positional lookup would fail silently on any page change. The property lookup reports where it\n"
         " found the value, because props.pageProps is a convention rather than something recovered, and collapsing\n"
         " found-by-convention with found-by-search would tell a caller its structure was confirmed when only a search\n"
         " had succeeded. And app-router is kept apart from pages-router: the literal names chunks/app, so a\n"
         " chunks/pages file must not match, and treating the two routers as one would build a path the image does not\n"
         " use.\n\n"
         "A test caught an HTML detail: <script id=__NEXT_DATA__> without quotes is valid HTML and the first regex\n"
         " rejected it. Both forms are accepted now, because a minifier produces unquoted attributes and that is exactly\n"
         " the input a parser of this kind has to eat.\n\n"
         "Figures: suite 1932 to 1946, AddToCart platform gaps from four remaining to three, and artifact freshness\n"
         " reads one file and a hundred and forty-two lines -- the new file, correctly. That row earned its place this\n"
         " round by reporting the change without anyone remembering to ask.\n\n"
         "Unknown: the real field names under props.pageProps, of which only the convention is known; the difference\n"
         " between /_next/ and /pay/_next/, inferred as a payment page's root; and the mechanism for Astro, Svelte and\n"
         " Frontend, where the image carries only framework names.\n\n"
         "The lesson is that gaps of the same kind can differ by an order of magnitude in evidence, so doing Next first\n"
         " was right -- it is the only one of the four that can be checked by shape rather than by name.\n\n"
         "Product code changed; suite green at 1946."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()