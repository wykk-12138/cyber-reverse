"""Record R899: R898's constants were missing /api, and the ownership question is settled."""

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
### R898 的 Vans 常量少了 `/api` —— 而归属从 Inference 升为 Observation（R899）

**R898 留下的问题：那 6 条路径到底属不属 Vans。**

### 做法：搜「宿主与路径同处一条字面量」

**R898 的扫描模式是 `/(cart|products)/vN/` —— 它从 `/api` **之后**那一段开始匹配，
所以既看不到前面的宿主，也丢掉了前面的 `/api`。这两个后果是同一个原因。**

**改成搜 `vans.com.../(cart|products)/vN/`，一次得到 5 条完整 URL：**

```
https://www.vans.com/api/cart/v1/cartWithItem?locale=
https://www.vans.com/api/cart/v2/cart/
https://www.vans.com/api/cart/v2/checkout/order/
https://www.vans.com/api/cart/v2/checkout/order?locale=
https://www.vans.com/api/products/v2/products/
```

**（第 6 条 `.../api/cart/v1/cart/` 在 `0x14709bf5c`，同一族。）**

### 两个后果，一次修掉

| 项 | R898 | R899 |
|---|---|---|
| 路径前缀 | `/cart/v1/cart/` | **`/api/cart/v1/cart/`** |
| `OwnershipIsInference` | `true` | **`false`** |

**少了 `/api` 的常量指的是一个 Vans 服务器不会应答的路径。而归属现在是 Observation ——
宿主与路径在**同一条字面量**里，这正是 R893 用的判据。**

### 所以 R898 那两个「保守的判断」都是同一个扫描模式的副产品

**R898 说「这 6 条没有自带宿主，所以归属是 Inference」——听上去很谨慎。
而它谨慎地记录的是一个**我自己的匹配模式造成的假象**。**

**「证据不足」和「我的搜索看不到」是两件事，而 R898 把后者写成了前者。**

### 改了哪些

| 文件 | 改动 |
|---|---|
| `VansEndpoints.cs` | 5 个常量补齐 `/api` + 第 6 个 `CartV1` 单列 + `OwnershipIsInference = false` + 注释写明 R898 错在哪 |
| `VansEndpointTests.cs` | 7 用例；新增 `EveryPathCarriesTheApiPrefix` 与 `OwnershipIsNoLongerInference` |
"""

if "R898 的 Vans 常量少了 `/api`" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R899 appended")

VERDICT = """

---

## 第 899 轮：R898 的 Vans 常量少了 `/api` —— 归属从 Inference 升为 Observation

### 做法：搜「宿主与路径同处一条字面量」

**R898 的扫描模式 `/(cart|products)/vN/` 从 `/api` **之后**开始匹配 —— 既看不到宿主，也丢掉了 `/api`。
两个后果，同一个原因。**

**改成搜 `vans.com.../(cart|products)/vN/`，得到 5 条完整 URL：**

```
https://www.vans.com/api/cart/v1/cartWithItem?locale=
https://www.vans.com/api/cart/v2/cart/
https://www.vans.com/api/cart/v2/checkout/order/
https://www.vans.com/api/cart/v2/checkout/order?locale=
https://www.vans.com/api/products/v2/products/
```

### 两个后果，一次修掉

| 项 | R898 | R899 |
|---|---|---|
| 路径前缀 | `/cart/v1/cart/` | **`/api/cart/v1/cart/`** |
| `OwnershipIsInference` | `true` | **`false`** |

**少了 `/api` 的常量指的是一个 Vans 服务器不会应答的路径。**

### 而 R898 那两个「保守的判断」都是同一个扫描模式的副产品

> **R898 说「这 6 条没有自带宿主，所以归属是 Inference」—— 听起来很谨慎。
> 而它谨慎地记录的是一个**我自己的匹配模式造成的假象**。**
> **「证据不足」和「我的搜索看不到」是两件事，而 R898 把后者写成了前者。**

### 改了哪些

**`VansEndpoints.cs`**：5 常量补 `/api` + 第 6 个 `CartV1` 单列 + `OwnershipIsInference = false`
**`VansEndpointTests.cs`**：7 用例，新增 `EveryPathCarriesTheApiPrefix` 与 `OwnershipIsNoLongerInference`

**套件 1789 → 1790 通过 / 0 失败。**
"""

BACKLOG_ADD = """

## 优先级 ① — Vans 路径修正：补 `/api`，归属升为 Observation（R899）

### 根因：R898 的扫描模式从 `/api` 之后开始

**`/(cart|products)/vN/` → 看不到前面的宿主，也丢掉 `/api`。两个后果同一个原因。**

### 5 条完整 URL

```
https://www.vans.com/api/cart/v1/cartWithItem?locale=
https://www.vans.com/api/cart/v2/cart/
https://www.vans.com/api/cart/v2/checkout/order/
https://www.vans.com/api/cart/v2/checkout/order?locale=
https://www.vans.com/api/products/v2/products/
```

### 修正

| 项 | R898 | R899 |
|---|---|---|
| 前缀 | `/cart/v1/cart/` | **`/api/cart/v1/cart/`** |
| `OwnershipIsInference` | `true` | **`false`** |

**R898 的两个「保守判断」都是扫描模式的副产品 —— 「证据不足」≠「我的搜索看不到」。**

**7 用例（新增 `EveryPathCarriesTheApiPrefix` · `OwnershipIsNoLongerInference`）；套件 1790 通过。**

| 仍 Unknown | |
|---|---|
| 请求体/响应形状 | 故无步骤调用 |
| v1 与 v2 哪个当前用 | 镜像里都有 |
| `/api` 这层是否所有站相同 | 未查 |

**纪律**：**扫描模式决定了你能看见什么。看不到时先问「是不是我的模式截掉了它」，再写「证据不足」。**
"""

BLOCKER = """

---

## 323. R898 的 Vans 常量少了 `/api`；归属升为 Observation

> R899。**改产品代码 +1 用例。** 套件 **1790 通过 / 0 失败 / 0 跳过**。

### 一、根因

**R898 的扫描模式是 `/(cart|products)/vN/` —— 它从 `/api` **之后**那一段开始匹配。
所以既看不到前面的宿主，也丢掉了 `/api`。**

**两个后果，同一个原因：路径错了，而「没有宿主」这个观察也是假的。**

### 二、5 条完整 URL

```
https://www.vans.com/api/cart/v1/cartWithItem?locale=
https://www.vans.com/api/cart/v2/cart/
https://www.vans.com/api/cart/v2/checkout/order/
https://www.vans.com/api/cart/v2/checkout/order?locale=
https://www.vans.com/api/products/v2/products/
```

### 三、修正

| 项 | R898 | R899 |
|---|---|---|
| 前缀 | `/cart/v1/cart/` | **`/api/cart/v1/cart/`** |
| `OwnershipIsInference` | `true` | **`false`** |

**少了 `/api` 的常量指的是一个 Vans 服务器不会应答的路径。**

### 四、而 R898 的「谨慎」是假的

**R898 说「这 6 条没有自带宿主，所以归属是 Inference」。听起来很谨慎。**

**而它谨慎记录的是一个**我自己的匹配模式造成的假象**。
「证据不足」和「我的搜索看不到」是两件事，R898 把后者写成了前者。**

### 五、验证

```
搜 vans.com.../(cart|products)/vN/     -> 5 条完整 URL（宿主与路径同处一条字面量）
VansEndpoints.cs                       -> 5 常量补 /api + CartV1 单列 + OwnershipIsInference=false
test --filter VansEndpointTests        -> 7 通过 / 0 失败
python tools\\metrics_report.py          -> 1790 通过 / 0 失败（原 1789 + 1）
```

### 六、仍然 Unknown

- **请求体与响应形状**：**Unknown** —— 无步骤调用。
- **v1 与 v2 哪个是当前的**：**Unknown** —— 镜像里都有。
- **`/api` 这一层是不是所有站都这样**：**Unknown** ——
  **如果别的站的扫描也没看 `/api`，那 R892–R896 的覆盖数都可能低报。**

### 七、教训

**R895 我学了「上界/下界/精确」，R898 学了「Observation/Inference」。这一轮把两者连起来：
**一个 Inference 标注可能是扫描模式的假象，而不是证据的真实状态。**

**所以顺序该反过来：先问「我的模式能不能看见它」，再决定标 Observation 还是 Inference。
R898 反了 —— 它先标了 Inference，然后这个标注本身成了错误信息。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R899", BLOCKER)
    ensure(RSTATUS, "R899", BLOCKER)
    ensure(RVERDICT, "第 899 轮", VERDICT)
    ensure(BACKLOG, "R899", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R899" not in h:
        h += ("\n## R899 补充 — Vans 常量补 `/api`，归属升为 Observation（**改产品代码**，套件 1789→**1790**）\n\n"
              "**根因**：R898 的扫描模式 `/(cart|products)/vN/` 从 `/api` **之后**开始匹配 → **路径少了 `/api`，而「没有宿主」这个观察也是假的**。\n"
              "**5 条完整 URL**：`https://www.vans.com/api/cart/v1/cartWithItem?locale=` · `.../api/cart/v2/cart/` · "
              "`.../api/cart/v2/checkout/order/` · `.../api/cart/v2/checkout/order?locale=` · `.../api/products/v2/products/`。\n"
              "**修正**：前缀补 `/api`；**`OwnershipIsInference` `true` → `false`**（宿主与路径同处一条字面量）。\n"
              "**7 用例**（新增 `EveryPathCarriesTheApiPrefix` · `OwnershipIsNoLongerInference`）。\n"
              "**纪律：一个 Inference 标注可能是扫描模式的假象 —— 先问「我的模式能不能看见它」，再决定标注。**\n"
              "**下一轮**：查别的站的扫描是否也漏了 `/api` —— 若是，R892–R896 的覆盖数都低报。\n")
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
             for p, k in ((RBLOCK, "R899"), (RSTATUS, "R899"), (RVERDICT, "第 899 轮"), (BACKLOG, "R899")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R899: the Vans constants were missing their api prefix, and the ownership caveat was an artefact\n\n"
         "R898 recovered six Vans paths, recorded them without an /api prefix, and labelled their ownership as\n"
         " inference because none of the literals it examined carried a host. This round shows both of those were\n"
         " consequences of one scanning decision.\n\n"
         "The pattern was /(cart|products)/vN/, which begins matching at the segment after /api. So the prefix was\n"
         " never part of the match, and the host in front of it was never in view. Searching instead for vans.com\n"
         " followed by one of those path segments returns five complete URLs, each holding host and path in the same\n"
         " literal: the v1 cart with an item, the v2 cart, both spellings of the v2 order submission, and the product\n"
         " list, all under https://www.vans.com/api/.\n\n"
         "So the constants were naming paths no Vans server answers, and the inference label was recording an artefact\n"
         " rather than a state of the evidence. Because host and path share a literal, ownership is observed on the\n"
         " same criterion R893 used, so OwnershipIsInference flips from true to false. The flag is kept rather than\n"
         " deleted, and a test asserts the false direction, because the flip is the finding.\n\n"
         "Seven tests now pin the paths, two of them new: that every one carries the /api prefix, which catches a scan\n"
         " that starts too late, and that ownership is no longer inference.\n\n"
         "The episode's lesson is about the order of two questions. R898 asked what the evidence supported and\n"
         " answered inference; it never asked whether its pattern could see a host at all. Asking the second question\n"
         " first would have produced the observation immediately. A caveat that says the evidence is weak can itself be\n"
         " wrong, and when it is, it is worse than no caveat because it reads as diligence.\n\n"
         "Unknown: the request bodies and response shapes, which is why no step calls these; which cart version a given\n"
         " step uses, since the image holds both; and whether the scans behind R892 through R896 also stopped short of\n"
         " an /api layer, which if true means those coverage figures under-report the replica.\n\n"
         "Product code changed; suite green at 1790."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
