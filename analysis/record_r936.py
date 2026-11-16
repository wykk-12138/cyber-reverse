"""Record R936: SvelteKit's mechanism from five literals, and the third AddToCart gap closes."""

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
### SvelteKit：五条字面量给出了**调用**，不只是框架名（R936）

**第三个 AddToCart 平台缺口。而它比 Astro 更清楚 —— Astro 给了一个属性前缀，Svelte 给了调用。**

```
SvelteKitData
/__data.json?x-sveltekit-invalidated=001
__sveltekit
x-sveltekit-pathname
x-sveltekit-search
```

### 这五条把机制说全了

**① 数据在**路由自己的路径 + `/__data.json`**。**
**② 路由与它的查询在**两个请求头**里，不在 URL 里。**
**③ `invalidated` 计数器说客户端已经拿到第几代数据。**

> **而 ③ 解释了为什么那条字面量带 `=001` 而不是一个裸参数：**它是个值**，
> 而带着错的值会拿到过期数据或被重发。**

### 而为什么有那两个头

**一条 SvelteKit 路由可以在任何路径上，而数据端点是**相对发起它的页面**的。
把路由放进头而不是放进 URL，意味着**一个端点服务所有路由**，由服务端根据头决定渲染什么。**

> **所以缺了头的请求**无法被正确回答** —— 这就是这里两个都是必需而不是可选的原因。**

### 三个刻意的决定

**① 路由前缀端点，且尾部斜杠去掉** —— 不制造双斜杠（服务端可能当成另一条路由）
**② 两个头**总是**都发** —— 只发一个描述的是「服务端看不见那条查询」的路由，正是这两个头要防的情况
**③ `invalidated` 是参数不是常量** —— 镜像给的值当默认，但**没有任何材料说它怎么递增**，所以这里不假装会算它

### 而测试抓到一个边界

**`__sveltekitz` 撞上了裸前缀 `__sveltekit` —— 它是个**不同的 cookie**，只是字母开头相同。
修：前缀后面必须是 `-` / `.` / `_` 或名字就此结束。**

### 三个平台的证据量，现在可以排出来了

| 平台 | 证据 | 能核什么 |
|---|---|---|
| **Next** | 选择器 + 正则 + 2 资源根 | **形状**（元素、chunk 路径） |
| **Svelte** | 端点 + 2 头 + cookie 前缀 + 类型名 | **调用形状**（URL、头、计数器） |
| **Astro** | 1 属性前缀 + 7 方法名 | **只能核属性家族** |
| Frontend | 未查 | ? |

> **而三个都做完了 `AddToCart` 的平台缺口从 5 降到 1。**
> **而它们的证据量差三个数量级 —— 所以「做完三个平台」用了三轮，而三轮里做的事完全不同。**

### 数字

| 度量 | R935 | **R936** |
|---|---|---|
| 套件 | 1955 | **1969** |
| 产物陈旧度 | 2 文件 / 246 行 | **3 文件 / 371 行** |
| `AddToCart` 平台缺口 | 2 剩 | **1 剩**（Frontend） |

### 教训

> **这一轮我第一版 `IsNonceCookie` 是 `StartsWith("__sveltekit")` ——
> 而前缀匹配**总是**会接受一个只是开头相同的名字。**
> **测试写了一个 `__sveltekitz` 就是为了抓它，而它抓到了。
> 前缀匹配要配边界，这条和 R926 那个「大小写滑动」是同一类：**匹配宽松一格，就多接受一个错东西**。**
"""

if "SvelteKit：五条字面量给出了**调用**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R936 appended")

VERDICT = """

---

## 第 936 轮：SvelteKit 的五条字面量给了**调用**，第三个平台缺口关闭

### 五条

```
SvelteKitData · /__data.json?x-sveltekit-invalidated=001
__sveltekit · x-sveltekit-pathname · x-sveltekit-search
```

### 机制

**① 数据在路由路径 + `/__data.json`**
**② 路由与查询在**两个头**里，不在 URL 里**
**③ `invalidated` 说客户端已有第几代数据**

> **③ 解释了为什么带 `=001` 而非裸参数：它是**一个值**，错的值会拿到过期数据。**

### 为什么有那两个头

**数据端点是**相对发起页面**的。把路由放进头，**一个端点服务所有路由**，服务端根据头决定渲染什么。**

> **所以缺了头的请求**无法被正确回答** —— 两个都是必需。**

### 三个决定

**① 尾部斜杠去掉（不制造双斜杠）· ② 两个头总是都发（只发一个 = 服务端看不见查询）·
③ `invalidated` 是参数不是常量（没有材料说它怎么递增）**

### 测试抓到一个边界

**`__sveltekitz` 撞上裸前缀 → 前缀后必须是 `-`/`.`/`_` 或结束。**

### 三个平台的证据量

| 平台 | 证据 | 能核什么 |
|---|---|---|
| **Next** | 选择器 + 正则 + 2 资源根 | **形状** |
| **Svelte** | 端点 + 2 头 + cookie 前缀 + 类型名 | **调用形状** |
| **Astro** | 1 属性前缀 + 7 方法名 | **只能核属性家族** |

> **三个做完，AddToCart 平台缺口 5 → 1。
> 而证据量差三个数量级 —— 三轮做的是三件完全不同的事。**

### 数字

| 度量 | R935 | **R936** |
|---|---|---|
| 套件 | 1955 | **1969** |
| 产物陈旧度 | 2 / 246 | **3 / 371** |
| AddToCart 平台缺口 | 2 剩 | **1 剩**（Frontend） |

### 教训

> **第一版 `IsNonceCookie` 是 `StartsWith("__sveltekit")` —— 前缀匹配**总是**接受只是开头相同的名字。
> 那个 `__sveltekitz` 测例就是为抓它写的，而它抓到了。**
> **前缀匹配要配边界 —— 与 R926 那个大小写滑动同类：**匹配宽松一格，就多接受一个错东西**。**
"""

BACKLOG_ADD = """

## 优先级 ① — SvelteKit surface（R936，**+14 用例**）

### 五条字面量

```
/__data.json?x-sveltekit-invalidated=001 · __sveltekit · x-sveltekit-pathname · x-sveltekit-search · SvelteKitData
```

### `Scripts/SvelteKitSurface.cs`

**`DataPath` · `DataEndpoint` · `InvalidatedParam` · `NonceCookiePrefix` · 两个头名 · `MethodFamily` ·
`DataUrl(route, invalidated)` · `DataHeaders(route, query)` · `IsNonceCookie` · `LooksLikeSvelteKit`**

### 三个决定

**尾部斜杠去掉 · 两个头总是都发 · `invalidated` 是参数不是常量（无递增证据）**

### 一个边界

**`IsNonceCookie` 前缀后必须是 `-`/`.`/`_` 或结束 —— `__sveltekitz` 不该匹配，测例抓到。**

### 数字

**套件 1955 → 1969 · 陈旧度 2/246 → 3/371 · AddToCart 平台缺口 2 → **1**（只剩 Frontend）**

| 仍 Unknown | |
|---|---|
| `invalidated` 如何递增 | 无材料 |
| 数据 JSON 的形状 | 无响应体 |
| Frontend 指什么 | 未查 |

**纪律**：前缀匹配要配边界 —— 匹配宽松一格，就多接受一个错东西。
"""

BLOCKER = """

---

## 360. SvelteKit：五条字面量给调用；第三个平台缺口关闭

> R936。**改产品代码 +14 用例。** 套件 **1969 通过 / 0 失败 / 0 跳过**。

### 一、五条字面量

```
SvelteKitData
/__data.json?x-sveltekit-invalidated=001
__sveltekit
x-sveltekit-pathname
x-sveltekit-search
```

### 二、机制

1. **数据在路由路径 + `/__data.json`。**
2. **路由与查询在两个头里，不在 URL 里。**
3. **`invalidated` 说第几代数据 —— 带错值会拿过期数据或被重发。**

**为什么有头：数据端点相对发起页面；把路由放进头 → 一个端点服务所有路由。
缺了头的请求无法被正确回答，所以两个都必需。**

### 三、三个决定

**尾部斜杠去掉（不制造双斜杠）· 两个头总是都发 · `invalidated` 是参数不是常量（无递增证据）**

### 四、测试抓到一个边界

**`IsNonceCookie` 第一版是裸 `StartsWith` → `__sveltekitz` 误匹配 →
修成前缀后必须 `-`/`.`/`_` 或结束。**

### 五、三平台证据量对比

| 平台 | 证据 | 能核什么 |
|---|---|---|
| Next | 选择器 + 正则 + 2 资源根 | 形状 |
| Svelte | 端点 + 2 头 + cookie 前缀 + 类型名 | 调用形状 |
| Astro | 1 属性前缀 + 7 方法名 | 属性家族 |

### 六、数字

| 度量 | R935 | R936 |
|---|---|---|
| 套件 | 1955 | **1969** |
| 产物陈旧度 | 2 / 246 | **3 / 371** |
| **AddToCart 平台缺口** | 2 剩 | **1 剩**（Frontend） |

### 七、验证

```
analysis/ida.py str "Svelte"                 -> 五条字面量 + 方法族
test --filter SvelteKitSurfaceTests          -> 14 通过
metrics_report.py                            -> 1969 通过 / 0 失败
```

### 八、仍然 Unknown

- **`invalidated` 如何递增**：**Unknown** —— 无材料。
- **数据 JSON 的形状**：**Unknown** —— 无响应体。
- **Frontend 指什么**：**Unknown** —— 未查。

### 九、教训

**前缀匹配**总是**会接受一个只是开头相同的名字。那个 `__sveltekitz` 测例就是为抓它写的，而它抓到了。**

**与 R926 那个大小写滑动同类：**匹配宽松一格，就多接受一个错东西。****
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R936", BLOCKER)
    ensure(RSTATUS, "R936", BLOCKER)
    ensure(RVERDICT, "第 936 轮", VERDICT)
    ensure(BACKLOG, "R936", BACKLOG_ADD)

    note = (
        "\n## R936 补充 — SvelteKit 五条字面量给调用（+14 用例，套件 1969）\n\n"
        "五条：/__data.json?x-sveltekit-invalidated=001 · __sveltekit · x-sveltekit-pathname · x-sveltekit-search · SvelteKitData。\n\n"
        "机制：数据在路由路径 + /__data.json；路由与查询在两个头里；invalidated 说第几代数据。\n"
        "为什么有头：端点相对发起页面 → 把路由放进头，一个端点服务所有路由；缺头无法被正确回答。\n\n"
        "三个决定：尾部斜杠去掉 · 两个头总是都发 · invalidated 是参数不是常量（无递增证据）。\n\n"
        "测试抓到：IsNonceCookie 裸 StartsWith → __sveltekitz 误匹配 → 前缀后必须有边界。\n\n"
        "三平台证据量：Next 形状 / Svelte 调用形状 / Astro 只能核属性家族 —— 差三个数量级。\n\n"
        "数字：套件 1955 → 1969 · 陈旧度 2/246 → 3/371 · AddToCart 平台缺口 2 → 1（只剩 Frontend）。\n\n"
        "纪律：前缀匹配要配边界 —— 匹配宽松一格，就多接受一个错东西。\n\n"
        "下一轮：Frontend（最后一个平台缺口），查它指什么。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R936" not in h:
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
             for p, k in ((RBLOCK, "R936"), (RSTATUS, "R936"), (RVERDICT, "第 936 轮"), (BACKLOG, "R936")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R936: SvelteKit, whose five literals give the calls and not just the framework's name\n\n"
         "The third AddToCart platform gap. Astro gave an attribute prefix and a method family; Svelte gives the calls:\n"
         " the data endpoint with its invalidated query, the nonce cookie prefix, two route headers, and a type name.\n\n"
         "Together they describe the mechanism. A SvelteKit page's data sits at the route's own path plus /__data.json;\n"
         " the route and its query travel in two headers rather than in the URL; and the invalidated counter says which\n"
         " generation of data the client already holds, which is why the literal carries a value rather than a bare\n"
         " parameter. The headers exist because the data endpoint is relative to the page that asked for it, so putting\n"
         " the route in headers lets one endpoint serve every route -- and a request omitting them cannot be answered\n"
         " correctly, which is why both are required here rather than optional.\n\n"
         "Three choices. A trailing slash is trimmed so the join cannot produce a double slash a server might read as a\n"
         " different route. Both headers are always emitted, since one alone describes a route whose query the server\n"
         " cannot see. And the invalidated counter is a parameter rather than a constant: the image's value is the\n"
         " default, and nothing recovered says how the counter advances, so no logic here pretends to compute it.\n\n"
         "A test caught a boundary. The first IsNonceCookie was a bare prefix test, which accepts __sveltekitz -- a\n"
         " different cookie that merely begins with the same letters. The prefix must now end at a separator or at the\n"
         " end of the name. That is the same fault as R926's case slip: a match one notch too loose accepts one wrong\n"
         " thing.\n\n"
         "The three platforms now rank by evidence rather than by difficulty. Next can be checked by shape, Svelte by the\n"
         " shape of a call, and Astro only by its attribute family -- three orders of magnitude apart, which is why three\n"
         " rounds did three quite different things.\n\n"
         "Figures: suite 1955 to 1969, freshness from two files to three and two hundred and forty-six lines to three\n"
         " hundred and seventy-one, and AddToCart platform gaps from two remaining to one.\n\n"
         "Unknown: how the invalidated counter advances; the data JSON's shape, since no response body survives; and what\n"
         " Frontend refers to, which is unchecked.\n\n"
         "Product code changed; suite green at 1969."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()