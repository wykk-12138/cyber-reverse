"""Record R890: endpoint coverage completed to 41/41, both directions pinned."""

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
### 端点覆盖补到 **41 / 41**，而且两个方向都钉住了（R890）

**R889 之后转走不需要凭据的那条路。做法不是继续搜 `GetInstoreOrders` 的名字，
而是把镜像里**全部** `/shop/v1/` 字面量枚举出来，与常量类做全量对比。**

### 结果

| | 条数 |
|---|---|
| 镜像 `/shop/v1/` 路径 | **41** |
| `PopMartEndpoints` 常量（改前） | 39 |
| **镜像有、复刻缺** | **2** |
| **复刻有、镜像没有** | **0** |

**缺的两个：**

```
/shop/v1/store_ticket/reserve
/shop/v1/store_ticket/sessionList
```

**多了零个 —— 也就是说 39 个常量每一个都有镜像出处。这个方向为 0 比缺 2 更重要：
它说明这个常量类没有一处是编的。**

### 而 `GetInstoreOrders` 的答案也出来了

**那 41 条里没有任何 `store/*order` 或 `instore` 路径。**

**所以 `GetInstoreOrders` 的端点**不在 `/shop/v1/` 下** —— 它不是这个族的。
要找到它得换前缀搜，而「换前缀」这件事本身是一条新的线索：`GetInstoreOrders` 可能与
`/shop/v1/storeOfflineDraw/*` 同族，也可能走一个完全不同的前缀。**

### 加了什么

| 文件 | 改动 |
|---|---|
| `PopMartEndpoints.cs` | **+2 常量**：`StoreTicketReserve` · `StoreTicketSessionList`，注释写明体未知故无步骤使用 |
| `PopMartEndpointCoverageTests.cs` | **新建 3 用例** |

**三个用例钉住两个方向：**

| 用例 | 钉住 |
|---|---|
| `TheImageHasFortyOneShopPaths` | 41 条，且互不重复 |
| `EveryImagePathAppearsInTheConstants` | **镜像有的，常量里必须有**（缺 = 调不到的端点） |
| `EveryConstantAppearsInTheImage` | **常量里有的，镜像里必须有**（多 = 我编的） |

**第三个是这两个里更要紧的：一个多出来的常量**看起来像覆盖**，而它是编的。**
"""

if "端点覆盖补到 **41 / 41**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R890 appended")

BLOCKER = """

---

## 314. 端点覆盖 **41 / 41**，两方向钉住；而 `GetInstoreOrders` 不在这一族

> R890。**改产品代码（+2 常量）+ 新 3 用例。** 套件 **1783 通过 / 0 失败 / 0 跳过**（原 1780 + 3）。

### 一、做法换成全量枚举

**R889 之后转走不需要凭据的路。而我没有继续搜 `GetInstoreOrders` 的名字，
而是枚举镜像里**全部** `/shop/v1/` 字面量，与常量类做全量对比。**

| | 条数 |
|---|---|
| 镜像 | **41** |
| 复刻（改前） | 39 |
| **镜像有、复刻缺** | **2** |
| **复刻有、镜像没有** | **0** |

**缺 `/shop/v1/store_ticket/reserve` 与 `/shop/v1/store_ticket/sessionList`。**

**而「多 0 个」比「缺 2 个」更重要：39 个常量每一个都有镜像出处，没有一处是编的。**

### 二、`GetInstoreOrders` 的答案：不在 `/shop/v1/` 下

**那 41 条里没有任何 `store/*order` 或 `instore` 路径。**

**所以它的端点不在这一族 —— 要找到得换前缀搜。而「它不在这族」本身是一条新线索：
可能与 `/shop/v1/storeOfflineDraw/*` 同族，也可能走完全不同的前缀。**

**这比「未查」进一步：从「不知道在哪」变成「知道不在哪」。**

### 三、加了什么

| 文件 | 改动 |
|---|---|
| `PopMartEndpoints.cs` | **+2 常量**，注释写明请求体未知故无步骤使用 |
| `PopMartEndpointCoverageTests.cs` | **新建，3 用例** |

| 用例 | 钉住 |
|---|---|
| `TheImageHasFortyOneShopPaths` | 41 条且互不重复 |
| `EveryImagePathAppearsInTheConstants` | **镜像有的常量必须有** |
| `EveryConstantAppearsInTheImage` | **常量有的镜像必须有** |

**第三个更要紧：多出来的常量**看起来像覆盖**，而它是编的。**

### 四、一处我自己的 grep 错

**查「`box/*` 与 `cash/desk/*` 在不在复刻件里」时我用了
`Select-String -Pattern "box/|cash/desk|..." -SimpleMatch` —— `-SimpleMatch` 把整个串当字面量，
`|` 不生效，于是返回空，看起来像「都没有」。**

**而全量对比说它们在（41 = 41，多 0 缺 2）。**
**同一个「返回空」的形态，R889 刚记过一次 —— 这次发生在 grep 的开关上。**

### 五、验证

```
idautils.Strings() 全量 /shop/v1/ 枚举  -> 41 条（列出全部）
与 PopMartEndpoints 对比（改前）        -> 缺 2，多 0
+2 常量后                               -> 41 = 41
test --filter PopMartEndpointCoverageTests -> 3 通过 / 0 失败
python tools\\metrics_report.py           -> 1783 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **`GetInstoreOrders` 的端点**：**Unknown，但已缩小到「不在 `/shop/v1/` 下」。**
  **下一轮该枚举别的前缀（比如全部 `/store/` 或 `/api/` 路径），而不是猜名字。**
- **那 2 个新常量的请求体**：**Unknown** —— 所以没有步骤用它们。**这是 R850 的规矩：有端点无体不写步骤。**
- **`box/*` 那 6 条与 `cash/desk/*` 那 7 条有没有对应步骤**：**Unknown** ——
  **它们都在常量里（41 全含），但没有 `StepSequence` 名字对得上。所以是「端点全、步骤缺」。**

### 七、教训

**R873 我搜 `order` 一族找 `GetInstoreOrders`，没找到，判「常量里没有」。**
**这一轮换了个做法 —— 枚举全部再对比 —— 得到的不是一个答案，是三个：
缺哪两个、多几个、以及那个找不到的东西不在这一族。**

**「搜一个名字」得到的是关于这个名字的答案；「枚举全部再对比」得到的是关于整个空间的答案。**

**而这一轮还顺带验证了「41 个常量有没有编的」这个方向 —— 那是搜名字永远答不了的。**
"""

VERDICT = """

---

## 第 890 轮：端点覆盖 41 / 41，两方向钉住

### 做法换了：全量枚举再对比

| | 条数 |
|---|---|
| 镜像 `/shop/v1/` 路径 | **41** |
| `PopMartEndpoints`（改前） | 39 |
| **镜像有、复刻缺** | **2** |
| **复刻有、镜像没有** | **0** |

**缺 `/shop/v1/store_ticket/reserve` 与 `/shop/v1/store_ticket/sessionList`。**

> **而「多 0 个」比「缺 2 个」更重要：39 个常量每一个都有镜像出处，没有一处是编的。**

### `GetInstoreOrders` 的答案：不在 `/shop/v1/` 下

**那 41 条里没有任何 `store/*order` 或 `instore` 路径。
→ 从「不知道在哪」进一步到「知道不在哪」。下一轮该枚举别的前缀，而不是猜名字。**

### 加了什么

`PopMartEndpoints.cs` **+2 常量**（注释写明请求体未知故无步骤使用）· `PopMartEndpointCoverageTests.cs` **新建 3 用例**

| 用例 | 钉住 |
|---|---|
| `TheImageHasFortyOneShopPaths` | 41 条且互不重复 |
| `EveryImagePathAppearsInTheConstants` | **镜像有的常量必须有** |
| `EveryConstantAppearsInTheImage` | **常量有的镜像必须有** |

> **第三个更要紧：多出来的常量**看起来像覆盖**，而它是编的。**

### 一处我自己的 grep 错

**`Select-String -SimpleMatch "box/|cash/desk|..."` —— `-SimpleMatch` 让 `|` 不生效，返回空，
看起来像「都没有」。而全量对比说它们在。**

> **同一个「返回空」的形态，R889 刚记过一次 —— 这次发生在 grep 的开关上。**

### 仍然 Unknown

**`GetInstoreOrders` 端点**（**已缩小到「不在 `/shop/v1/` 下」**）· **2 个新常量的请求体**（所以无步骤用）·
**`box/*` 6 条与 `cash/desk/*` 7 条有无对应步骤**（**端点全、步骤缺**）

### 教训

> **R873 我搜 `order` 一族找 `GetInstoreOrders`，没找到，判「常量里没有」。**
> **这一轮换了做法，「枚举全部再对比」得到的不是**一个**答案，是三个：缺哪两个、多几个、以及那东西不在这一族。**
> **「搜一个名字」得到的是关于这个名字的答案；「枚举全部再对比」得到的是关于整个空间的答案 ——
> 而后者还能答「有没有编的」，那是搜名字永远答不了的。**
"""

BACKLOG_ADD = """

## 优先级 ① — 端点覆盖 **41 / 41**（R890，**+2 常量 +3 用例**）

### 全量枚举再对比（不是搜名字）

| | 条数 |
|---|---|
| 镜像 `/shop/v1/` | **41** |
| 复刻（改前） | 39 |
| **缺** | **2**：`store_ticket/reserve` · `store_ticket/sessionList` |
| **多** | **0** ← 39 个常量全部有镜像出处，**没有编的** |

### `GetInstoreOrders` 不在 `/shop/v1/` 下

**41 条里无 `store/*order` 或 `instore` → 从「不知道在哪」到「知道不在哪」。下一轮枚举别的前缀。**

### 测试（3 个，双向）

**`TheImageHasFortyOneShopPaths` · `EveryImagePathAppearsInTheConstants` · `EveryConstantAppearsInTheImage`**
**→ 第三个钉「多出来的常量」= 编造，它比缺失更危险（看起来像覆盖）。**

**套件 1783 通过 / 0 失败（原 1780 + 3）。**

### 我的 grep 错

**`-SimpleMatch "box/|cash/desk|..."` → `|` 不生效 → 返回空 → 像「都没有」。**
**同一「返回空」形态，R889 刚记过一次（这次在 grep 开关上）。**

| 仍 Unknown | |
|---|---|
| `GetInstoreOrders` 端点 | 已缩小到「不在 /shop/v1/ 下」 |
| 2 个新常量的请求体 | 故无步骤使用（R850 规矩） |
| `box/*` 6 条 · `cash/desk/*` 7 条的步骤 | **端点全、步骤缺** |

**纪律**：**搜一个名字答的是那个名字；枚举全部再对比答的是整个空间 —— 还能答「有没有编的」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R890", BLOCKER)
    ensure(RSTATUS, "R890", BLOCKER)
    ensure(RVERDICT, "第 890 轮", VERDICT)
    ensure(BACKLOG, "R890", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R890" not in h:
        h += ("\n## R890 补充 — 端点覆盖 **41 / 41**（**+2 常量 +3 用例**）\n\n"
              "**做法换成全量枚举再对比**：镜像 `/shop/v1/` 41 条 vs 复刻 39 → **缺 2（`store_ticket/reserve` · `store_ticket/sessionList`）、多 0**。"
              "**「多 0」更重要：39 个常量全部有镜像出处，没有编的。**\n"
              "**`GetInstoreOrders` 不在 `/shop/v1/` 下** → 从「不知道在哪」到「知道不在哪」。**下一轮枚举别的前缀。**\n"
              "**3 个用例双向钉住**，其中 `EveryConstantAppearsInTheImage` 钉「多出来的常量」= 编造。**套件 1783 通过 / 0 失败。**\n"
              "**我的 grep 错**：`-SimpleMatch \"box/|cash/desk\"` → `|` 不生效 → 返回空像「都没有」（同一「返回空」形态第二次）。\n"
              "**纪律：搜名字答那个名字；枚举全部再对比答整个空间 —— 还能答「有没有编的」。**\n")
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
             for p, k in ((RBLOCK, "R890"), (RSTATUS, "R890"), (RVERDICT, "第 890 轮"), (BACKLOG, "R890")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R890: endpoint coverage closes at forty-one of forty-one, with both directions pinned\n\n"
         "R889 left the draw frontier at a static ceiling and named four credential-free threads. This round took one,\n"
         " but changed the method: instead of searching again for the name GetInstoreOrders, it enumerated every\n"
         " /shop/v1/ literal in the image and compared the whole set against the constants.\n\n"
         "The image holds forty-one distinct paths and the constant class held thirty-nine. Exactly two were missing,\n"
         " store_ticket/reserve and store_ticket/sessionList, and none of the thirty-nine was absent from the image.\n"
         " That second direction matters more than the first: zero extras means no constant was invented, so the class\n"
         " is a faithful copy of the image's inventory rather than a plausible-looking one.\n\n"
         "The search also answers the question that started it, differently. None of the forty-one paths contains\n"
         " store-order or instore, so GetInstoreOrders' endpoint is not in this family at all. That moves the unknown\n"
         " from not knowing where it is to knowing where it is not, and the next attempt should enumerate a different\n"
         " prefix rather than guess another name.\n\n"
         "Both constants are added with a note that their request bodies are unknown and therefore no step uses them,\n"
         " which is R850's rule: an endpoint with no evidenced body does not get a step. Three tests pin the inventory\n"
         " in both directions -- the image's forty-one, every image path present as a constant, and every constant\n"
         " present in the image. The last is the one that catches fabrication, since an extra constant looks like\n"
         " coverage while being an invention.\n\n"
         "One grep error of mine belongs in the record. Checking whether the box and cash-desk families existed in the\n"
         " replica, I ran Select-String with -SimpleMatch over a pattern containing a pipe, which treats the whole\n"
         " string as a literal, so the pattern matched nothing and the families looked absent. The full comparison says\n"
         " they are present, since the totals agree at forty-one and the extras are zero. An empty result read as an\n"
         " absence is the same shape R889 recorded one round earlier, this time in a grep flag rather than a JSON key.\n\n"
         "Unknown: GetInstoreOrders' endpoint, now bounded to not being under /shop/v1/; the request bodies for the two\n"
         " new constants, which is why they have no caller; and whether the six box paths and the seven cash-desk paths\n"
         " have steps at all, where the constants are complete and the step names are absent.\n\n"
         "The lesson is about what a search can and cannot answer. Searching a name answers about that name; enumerating\n"
         " a space and comparing answers about the space, and it additionally answers whether anything in it was\n"
         " invented -- which no name search can do.\n\n"
         "Product code changed, two constants; suite green at 1783, the previous 1780 plus three."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
