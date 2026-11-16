"""Record R892: the endpoint-family coverage table, and the first pass that over-reported by eight."""

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
### 端点族覆盖表：**56 族，32 族完全没有** —— 而第一次报的是 40（R892）

**R891 说「还有没有第三个族，我只在 PopMart 的域里找过」。这一轮枚举全部 `/word/vN/` 形状，得到 56 个 API 族。**

### 而第一次的分级是错的

**第一版判据是「整条路径作为字面量出现」—— 于是报出 **40 族完全没有**。**

**抽查 `__bff__` 时发现它其实在：`JohnLewisBff.Base = ".../bff/"` + 相对路径 `"v2/orders"`。
**同一个端点，存法是「基址 + 相对路径」，而不是完整字面量。****

**改成分三级：**

| 级 | 判据 | 族数 |
|---|---|---|
| **exact** | 整条路径是字面量 | 3 |
| **relative** | 族名在源码里，或「去掉族前缀的尾部」是字面量 | 21 |
| **absent** | 族名在源码里根本不出现 | **32** |

**所以第一次多报了 8 个 —— 而错的形状是「存储形式不同被读成了不存在」，
与 R889 那次「工具读法错被读成对象缺席」同族。**

### 32 个完全没有的族（按路径数排）

| 族 | 路径数 |
|---|---|
| **`/customer/v1/`** | **10** |
| **`/Checkout/v2/`** · **`/bff/v4/`** | 各 **5** |
| **`/threeds/v1/`** · **`/bff/v3/`** · `/checkout/v2/` · `/cart/v2/` | 各 3–4 |
| `/activity/v1/` `/api/v7/` `/cart/v1/` `/client_api/v1/` `/commerce/v1/` `/marketing/v1/` `/paygate/v2/` `/product-core/v1/` `/legacy/v1/` … | 各 2 |
| **`/turnstile/v0/`** · **`/shield/v1/`** · `/flex/v2/` `/form/v1/` `/jgc/v8/` `/snap/v1/` `/snap/v2/` `/rest/v2/` `/public/v1/` … | 各 1 |

### 其中两条属于优先级 ②

| 族 | 为什么 |
|---|---|
| **`/turnstile/v0/`** | **Cloudflare Turnstile** —— R876 在模型字段里见过 `_turnstileKey` |
| **`/shield/v1/`** | 名字像防护服务；**内容未查** |

**所以「风控对抗」这一档在端点层也有一处具体缺口，而不只是方法名。**

### 这张表是判据 (f) 的形态

**goal 的 (f) 要求「核心覆盖表可复算：原版站点与风控清单 ↔ `Registry.cs` 与 `Flows/Scripts` 逐条对」。
这一轮给出的是**端点族**那一层的可复算表 —— 56 / 3 / 21 / 32。**

**而它还有一个前提没满足：那 56 个族是不是都属于 PopMart？**
**`/bff/*` 是 John Lewis 的，`/activity/v1/` 与 `/shop/v1/`、`/store/v1/` 属于 PopMart。
所以「56 个族」是**全镜像的**，不是某一个站的 —— 而按站分组还没做。**
"""

if "端点族覆盖表：**56 族，32 族完全没有**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R892 appended")

BLOCKER = """

---

## 316. 端点族 **56 个，32 个完全没有** —— 而第一次报成 40

> R892。未改产品代码。

### 一、第一次分级错了，错在「存储形式」

**第一版判据：「整条路径作为字面量出现」。于是报 **40 族完全没有**。**

**抽查 `__bff__` 时发现：`JohnLewisBff.Base = ".../bff/"` + 相对路径 `"v2/orders"`。
**同一个端点，存法是「基址 + 相对路径」。****

**改成分三级：**

| 级 | 判据 | 族数 |
|---|---|---|
| **exact** | 整条路径是字面量 | 3 |
| **relative** | 族名出现，或去掉族前缀的尾部是字面量 | 21 |
| **absent** | 族名在源码里根本不出现 | **32** |

**第一次多报 8 个。错的形状是「存储形式不同被读成不存在」——
与 R889「工具读法错被读成对象缺席」同族，这是第三次了。**

### 二、32 个完全没有的族

| 族 | 路径数 |
|---|---|
| **`/customer/v1/`** | **10** |
| **`/Checkout/v2/`** · **`/bff/v4/`** | 各 5 |
| `/threeds/v1/` · `/bff/v3/` · `/checkout/v2/` · `/cart/v2/` | 各 3–4 |
| `/activity/v1/` `/api/v7/` `/cart/v1/` `/client_api/v1/` `/commerce/v1/` `/marketing/v1/` `/paygate/v2/` `/product-core/v1/` `/legacy/v1/` … | 各 2 |
| **`/turnstile/v0/`** · **`/shield/v1/`** `/flex/v2/` `/form/v1/` `/jgc/v8/` `/snap/v1/` `/snap/v2/` `/rest/v2/` `/public/v1/` … | 各 1 |

### 三、两条属于优先级 ②

| 族 | 为什么 |
|---|---|
| **`/turnstile/v0/`** | **Cloudflare Turnstile**；R876 在模型字段里见过 `_turnstileKey` |
| **`/shield/v1/`** | 名字像防护服务，内容未查 |

**所以「风控对抗」在端点层也有一处具体缺口，而不只是方法名层面。**

### 四、这张表的边界

**56 个族是**全镜像的**，不是某一个站的：`/bff/*` 是 John Lewis 的，
`/activity/v1/`、`/shop/v1/`、`/store/v1/` 属 PopMart。**

**所以「32 个完全没有」的意思是「复刻件源码里没有这些族的名字」，
而不是「PopMart 缺 32 族」。按站分组还没做 —— 那是这张表要成为判据 (f) 成品的前提。**

### 五、验证

```
idautils.Strings() / /segment/vN/ 形状   -> 56 族 / 全部路径
第一版判据（整条字面量）                  -> 40 族 absent
第二版判据（含 relative）                 -> 3 exact / 21 relative / 32 absent
__bff__ 抽查                             -> Base + "v2/orders" 形式，故第一版误判
本轮未改产品代码；套件沿用 1783
```

### 六、仍然 Unknown

- **那 32 族的顶层归属（哪个站）**：**Unknown** ——
  **`/customer/v1/` 那 10 条、`/jgc/v8/`、`/snap/v1/` 等，域名字面上看不出来。**
- **`/shield/v1/` 与 `/turnstile/v0/` 具体做什么**：**Unknown** —— 只有路径。
- **relative 那 21 族里，有多少是「基址对但路径缺」**：**Unknown** ——
  **我的判据只查族名或尾部，不查每一条都在。**

### 七、教训

**我这一轮的第一版判据是一个**关于存储形式的假设**，而错的方向是「高报缺口」。**

**这与前面几轮的错相反：R888 那个假 0（低报），这次是假 40（高报）。**
**两个方向都来自同一个东西 —— 判据里藏了一个我以为成立的前提。**

**而两次的发现方式不同：R888 是测试红了；这次是**抽查一个我预期应该缺席的族**。**
**「挑一个样本去推翻自己的判据」，比「相信判据的输出」便宜得多。**
"""

VERDICT = """

---

## 第 892 轮：端点族 56 个，32 个完全没有 —— 而第一次报成 40

### 第一次分级错了，错在「存储形式」

**第一版判据「整条路径作为字面量出现」→ 报 40 族完全没有。**

**抽查 `__bff__`：`JohnLewisBff.Base = ".../bff/"` + 相对路径 `"v2/orders"` ——
**同一端点，存法是「基址 + 相对路径」。****

| 级 | 判据 | 族数 |
|---|---|---|
| **exact** | 整条路径是字面量 | 3 |
| **relative** | 族名出现，或去掉族前缀的尾部是字面量 | 21 |
| **absent** | 族名根本不出现 | **32** |

**第一次多报 8 个。**

> **与 R889「工具读法错被读成对象缺席」同族 —— 这是第三次。
> 而方向相反：R888 是假 0（低报），这次是假 40（高报）。两个都来自判据里藏了一个我以为成立的前提。**

### 32 个完全没有的族

| 族 | 路径数 |
|---|---|
| **`/customer/v1/`** | **10** |
| **`/Checkout/v2/`** · **`/bff/v4/`** | 各 5 |
| `/threeds/v1/` · `/bff/v3/` · `/checkout/v2/` · `/cart/v2/` | 各 3–4 |
| `/activity/v1/` `/api/v7/` `/cart/v1/` `/client_api/v1/` `/commerce/v1/` `/marketing/v1/` `/paygate/v2/` `/product-core/v1/` `/legacy/v1/` … | 各 2 |
| **`/turnstile/v0/`** · **`/shield/v1/`** `/flex/v2/` `/form/v1/` `/jgc/v8/` `/snap/v1/` `/snap/v2/` `/rest/v2/` `/public/v1/` … | 各 1 |

### 两条属于优先级 ②

**`/turnstile/v0/`（Cloudflare Turnstile；R876 见过 `_turnstileKey`）· `/shield/v1/`（名字像防护，内容未查）**

> **所以「风控对抗」在端点层也有一处具体缺口，而不只是方法名层面。**

### 这张表的边界

**56 个族是**全镜像的**，不是单个站的：`/bff/*` 是 John Lewis 的，`/activity/v1/`、`/shop/v1/`、`/store/v1/` 属 PopMart。**
**→「32 个完全没有」= 「复刻件源码里没有这些族名」，**不是「PopMart 缺 32 族」**。按站分组未做。**

### 仍然 Unknown

**32 族的顶层归属**（`/customer/v1/` 10 条、`/jgc/v8/`、`/snap/v1/` 域名字面看不出）·
**`/shield/v1/` 与 `/turnstile/v0/` 具体做什么** ·
**relative 那 21 族里有多少是「基址对但路径缺」**

### 教训

> **两次判据的错方向相反（假 0 / 假 40），来源相同：判据里藏了一个我以为成立的前提。**
> **而两次的发现方式不同：R888 是测试红了；这次是**挑一个我预期应该缺席的族去推翻自己的判据**。**
> **「挑一个样本去推翻自己的判据」，比「相信判据的输出」便宜得多。**
"""

BACKLOG_ADD = """

## 判据 — 端点族 **56 个 / 32 个完全没有**（R892）

### 第一次报 40，多报 8 —— 错在存储形式

**`JohnLewisBff.Base = ".../bff/"` + 相对路径 `"v2/orders"` → 整条字面量判据找不到它。**

| 级 | 判据 | 族数 |
|---|---|---|
| exact | 整条路径是字面量 | 3 |
| relative | 族名出现，或去掉族前缀的尾部是字面量 | 21 |
| **absent** | **族名根本不出现** | **32** |

**→ 与 R889 同族（第三次）；方向与 R888 相反（假 0 vs 假 40），来源相同：判据里藏了一个以为成立的前提。**

### 32 个完全没有（按路径数）

**`/customer/v1/` 10** · **`/Checkout/v2/` · `/bff/v4/` 各 5** · `/threeds/v1/` `/bff/v3/` `/checkout/v2/` `/cart/v2/` 各 3–4 ·
`/activity/v1/` `/api/v7/` `/cart/v1/` `/client_api/v1/` `/commerce/v1/` `/marketing/v1/` `/paygate/v2/` `/product-core/v1/` `/legacy/v1/` 各 2 ·
**`/turnstile/v0/`** **`/shield/v1/`** `/flex/v2/` `/form/v1/` `/jgc/v8/` `/snap/v1/` `/snap/v2/` `/rest/v2/` `/public/v1/` 各 1

### 优先级 ② 的两条

**`/turnstile/v0/`（Cloudflare Turnstile，R876 的 `_turnstileKey`）· `/shield/v1/`（内容未查）**

### 边界

**56 族是**全镜像**的：`/bff/*` 属 John Lewis，`/activity/v1/` `/shop/v1/` `/store/v1/` 属 PopMart。
→「32 个完全没有」≠「PopMart 缺 32 族」。**按站分组未做 = 这张表成为判据 (f) 成品的前提。**

| 仍 Unknown | |
|---|---|
| 32 族的顶层归属 | 域名字面看不出 |
| `/shield/v1/` `/turnstile/v0/` 做什么 | 只有路径 |
| relative 21 族里多少「基址对路径缺」 | 判据只查族名/尾部 |

**纪律**：**挑一个预期应该缺席的样本去推翻自己的判据，比相信判据的输出便宜得多。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R892", BLOCKER)
    ensure(RSTATUS, "R892", BLOCKER)
    ensure(RVERDICT, "第 892 轮", VERDICT)
    ensure(BACKLOG, "R892", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R892" not in h:
        h += ("\n## R892 补充 — 端点族 **56 / 32 完全没有**（**未改产品代码**）\n\n"
              "**第一次报 40，多报 8**：`JohnLewisBff.Base = \".../bff/\"` + 相对路径 `\"v2/orders\"` → 整条字面量判据找不到。"
              "**改三级：exact 3 / relative 21 / absent 32。**\n"
              "**32 个完全没有**：`/customer/v1/` 10 · `/Checkout/v2/` `/bff/v4/` 各 5 · `/threeds/v1/` `/bff/v3/` `/checkout/v2/` `/cart/v2/` 各 3–4 · … · **`/turnstile/v0/`（Cloudflare Turnstile）** **`/shield/v1/`**。\n"
              "**优先级 ② 有两条具体缺口**：`/turnstile/v0/`（R876 的 `_turnstileKey`）与 `/shield/v1/`。\n"
              "**边界：56 族是全镜像的**，`/bff/*` 属 John Lewis → 「32 个没有」≠「PopMart 缺 32 族」。**按站分组未做。**\n"
              "**纪律：两次判据错方向相反（假 0 / 假 40），来源相同 —— 判据里藏了以为成立的前提。挑样本来推翻自己比相信输出便宜。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R892"), (RSTATUS, "R892"), (RVERDICT, "第 892 轮"), (BACKLOG, "R892")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R892: fifty-six endpoint families, thirty-two absent, and a first pass that over-reported by eight\n\n"
         "R891 asked whether a third endpoint family existed, having so far searched only inside Pop Mart's domain.\n"
         " Enumerating every /segment/vN/ shape in the image gives fifty-six API families.\n\n"
         "The first grading of them was wrong. It counted a family as present only when the whole path appeared as a\n"
         " literal, which reported forty families completely absent. Sampling the BFF family to check that claim showed\n"
         " it present as JohnLewisBff.Base plus relative paths like v2/orders -- the same endpoint, stored as a base and\n"
         " a tail. So the grading became three-way: three families present as whole literals, twenty-one present through\n"
         " a base prefix or a distinctive tail, and thirty-two where the family name does not appear in the source at\n"
         " all. The first pass over-reported absence by eight.\n\n"
         "That is the third round in a row where a real observation was read through a hidden assumption -- R889's\n"
         " JSON key, R888's absolute path segment, and now a storage convention -- and the direction of the error has\n"
         " reversed: R888 produced a false zero, a metric reporting success that was not there, while this one produced\n"
         " a false forty, a gap larger than reality. Both come from the same place.\n\n"
         "The thirty-two absent families are dominated by customer/v1 with ten paths, then Checkout/v2 and bff/v4 with\n"
         " five each, then threeds/v1, bff/v3, checkout/v2 and cart/v2 with three or four. Two belong to the anti-bot\n"
         " priority: turnstile/v0, which R876 saw a _turnstileKey field for, and shield/v1, whose contents are\n"
         " unchecked. So that priority has a concrete endpoint-level gap and not only a gap in method names.\n\n"
         "The table's boundary matters as much as its content. The fifty-six families span the whole image: bff is John\n"
         " Lewis's, activity/v1 and shop/v1 and store/v1 are Pop Mart's. So thirty-two absent means the replica's source\n"
         " never names those families, not that Pop Mart is missing thirty-two of them. Grouping by store is the work\n"
         " this table needs before it can serve criterion (f).\n\n"
         "Unknown: which store owns each of the thirty-two, since customer/v1, jgc/v8 and snap/v1 give nothing away in\n"
         " their names; what shield/v1 and turnstile/v0 do, of which only the paths are known; and how many of the\n"
         " twenty-one relative families are base-correct but path-incomplete, since the check looks at the family name\n"
         " and the tail rather than at every path.\n\n"
         "The lesson is about how to catch this kind of error. R888's false zero was caught by a test going red; this\n"
         " round's false forty was caught by deliberately sampling a family I expected to be absent, in order to\n"
         " refute my own criterion. That move is cheaper than trusting the output, and it should be routine.\n\n"
         "No product code changed; suite carries at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
