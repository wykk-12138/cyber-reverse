"""Record R891: a second endpoint family, two steps, and the implemented-versus-sequenced distinction."""

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
### 找到**第二个端点族** `/store/v1/` —— 5 条，其中两条能写成步骤（R891）

**R890 说 `GetInstoreOrders` 的端点「不在 `/shop/v1/` 下」。这一轮用同一招但换了锚：**
**在全部字面量里搜含 `order` 的路径。**

### 第一次扫错，第二次对

**第一版正则 `(/[a-zA-Z0-9_\\-]+(?:/[...]*)+)` 太松 —— 抓到 GUID、base64、`3ds` 碎片，70 条里没有一条含 `order`。**

**改成**以词为锚**：`/[A-Za-z0-9_.\\-/{}?=&%]*order[...]*`，一次就找到了：**

```
146ab926c   /store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20
```

**而那个前缀不只一条。枚举 `/store/v1/`：**

| 路径 | 对应步骤 |
|---|---|
| `/store/v1/store/cart/add` | — |
| `/store/v1/store/cart/del` | — |
| `/store/v1/store/cart/listByStore?actionType=1&GID=` | — |
| **`/store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20`** | **`GetInstoreOrders`（105）** |
| **`/store/v1/store/product/detail?storeId=`** | **`FindProductInstore`（76）** |

**所以这是**第二个端点族**，与 `/shop/v1/` 平行 —— 而 R871–R890 的全部工作都只在第一个族里。**

### 写了什么

| 文件 | 改动 |
|---|---|
| `PopMartEndpoints.cs` | **+5 常量**（新族一整块） |
| `StoreFlow.cs` | **+2 虚方法**：`GetInstoreOrdersAsync` · `FindProductInstoreAsync`，均默认显式失败 |
| `PopMartFlow.cs` | **+2 override**：GET，查询形状取自常量 |

### 而 `implementable` 只从 7 到 **8**，不是 9

**测试红了，报 `Expected: 9, Actual: 8`。**

**原因：`FindProductInstore` **不在 PopMart 那 24 个名字里**。**
**它是 ordinal 76，属于 R882 读到的那条更早的字面量段（56–77，含 5 个 `Start*Flow`），
而 PopMart 自己的段从 104 起。**

**所以：**已实现 ≠ 在序列里**。**
**测试现在两个都钉：`CanRunStep("FindProductInstore")` 为真，而 `StepSequence` 不含它。**
"""

if "找到**第二个端点族** `/store/v1/`" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R891 appended")

BLOCKER = """

---

## 315. 第二个端点族 `/store/v1/`：5 条，写了 2 步，coverage **7 → 8**

> R891。**改产品代码。** 套件 **1783 通过 / 0 失败 / 0 跳过**。

### 一、R890 的「不在这一族」变成了「在那一族」

**R890 把 `GetInstoreOrders` 的端点缩小到「不在 `/shop/v1/` 下」。这一轮用同一招但换锚：
全部字面量里搜含 `order` 的路径，找到 `/store/v1/store/order/listV3?…`。**

**而那个前缀不只一条 —— 一整个族：**

| 路径 | 步骤 |
|---|---|
| `/store/v1/store/cart/add` · `cart/del` · `cart/listByStore?actionType=1&GID=` | — |
| **`/store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20`** | **`GetInstoreOrders`（105）** |
| **`/store/v1/store/product/detail?storeId=`** | **`FindProductInstore`（76）** |

**所以 R871–R890 的全部工作只在第一个族里；现在知道有第二个。**

### 二、而第一次扫是错的

**第一版正则 `(/[a-zA-Z0-9_\\-]+(?:/[...]*)+)` 太松 —— 70 条里全是 GUID、base64、`3ds` 碎片，
没有一条含 `order`。**

**「以形状为锚」失败了，「以词为锚」一次就对。
这与 R890 的教训是同一条的另一面：R890 说「枚举整个空间比搜名字强」，
而这一轮说**空间的边界要用词来划，不能用形状来猜**。**

### 三、`implementable` 只到 8，不是 9

**测试红了：`Expected: 9, Actual: 8`。**

**`FindProductInstore` **不在 PopMart 那 24 个名字里** —— 它是 ordinal 76，
属于 R882 那条更早的段（56–77），而 PopMart 自己的段从 104 起。**

> **所以「已实现」和「在序列里」是两件事。**
> **测试现在两个都钉：`CanRunStep("FindProductInstore")` 为真，而 `DoesNotContain` 它不在 `StepSequence`。**

**这个区分很重要：如果把「实现了几步」当成分母算覆盖率，那两个不同的分母会给出两个不同的数。**

### 四、验证

```
全字面量搜 order 形路径（以词为锚）   -> /store/v1/store/order/listV3?... @0x146ab926c
枚举 /store/v1/                        -> 5 条（列出全部）
+5 常量 · +2 虚方法 · +2 override       -> build 0 错误
StoreFlow 虚步骤                       -> 172 -> 174
/shop/v1 常量 41 · /store/v1 常量 5
test --filter FlowSequence|PopMartEndpoint -> 10 通过 / 0 失败
python tools\\metrics_report.py          -> 1783 通过 / 0 失败 / 0 跳过
```

### 五、仍然 Unknown

- **`/store/v1/` 那 3 条 cart 路径的步骤归属**：**Unknown** ——
  **端点有了，但没有 `StepSequence` 名字对得上。可能是 `AddToCart`/`GetCart` 的 in-store 变体。**
- **`storeId` 从哪来**：**Unknown** —— `FindProductInstore` 从 session 取，而没人放。
  **与 R872 的 `alias` 同形：步骤会明确失败而不是跑错。**
- **还有没有第三个族**：**Unknown** —— 现在知道 `/shop/v1/` 与 `/store/v1/`。
  **别的站可能有别的族，而我只在 PopMart 的域里找过。**

### 六、教训

**R890 我说「枚举整个空间比搜名字强」。这一轮补上一半：**
**空间的边界要用**词**来划，不能用**形状**来猜。**

**同一个动作（枚举全部再对比），锚错了两分钟全是垃圾，锚对了三十秒出答案。
而两次的差别只是一个正则。**

**而第二个收获是那个 8 不是 9 —— 一个测试失败逼出了一个我本来会写错的区分：
「实现了几步」和「序列里有几步」是两个数。**
"""

VERDICT = """

---

## 第 891 轮：第二个端点族 `/store/v1/` —— 5 条，写 2 步，coverage 7 → 8

### R890 的「不在这一族」变成了「在那一族」

**同一招换锚：全部字面量里搜含 `order` 的路径 → `0x146ab926c`：**

```
/store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20
```

**而那个前缀不只一条 —— 一整个族：**

| 路径 | 步骤 |
|---|---|
| `cart/add` · `cart/del` · `cart/listByStore?actionType=1&GID=` | — |
| **`order/listV3?currentPage=1&status=1&pageSize=20`** | **`GetInstoreOrders`（105）** |
| **`product/detail?storeId=`** | **`FindProductInstore`（76）** |

> **R871–R890 的全部工作只在第一个族里；现在知道有第二个。**

### 第一次扫是错的

**正则 `(/[a-zA-Z0-9_\\-]+(?:/[...]*)+)` 太松 → 70 条全是 GUID/base64/`3ds` 碎片，无一条含 `order`。**
**改成以**词**为锚，一次就对。**

> **R890 说「枚举整个空间比搜名字强」；这一轮补上一半：**空间的边界要用词来划，不能用形状来猜**。**

### `implementable` 只到 8，不是 9

**测试红了 `Expected: 9, Actual: 8` —— `FindProductInstore` **不在 PopMart 那 24 个名字里**（ordinal 76 属于 R882 那条更早的段 56–77，PopMart 从 104 起）。**

> **「已实现」和「在序列里」是两件事。测试现在两个都钉：`CanRunStep` 为真，`DoesNotContain` 它不在 `StepSequence`。**
> **这个区分要紧：两个不同的分母会给出两个不同的覆盖率。**

### 仍然 Unknown

**`/store/v1/` 3 条 cart 路径的步骤归属**（可能是 `AddToCart`/`GetCart` 的 in-store 变体）·
**`storeId` 从哪来**（从 session 取而没人放，同 R872 的 `alias` 形态）·
**还有没有第三个族**（**我只在 PopMart 的域里找过**）

### 教训

> **同一个动作（枚举全部再对比），锚错了两分钟全是垃圾，锚对了三十秒出答案 —— 差别只是一个正则。**
> **而第二个收获是那个 8 不是 9：一个测试失败逼出了一个我本来会写错的区分。**
"""

BACKLOG_ADD = """

## 优先级 ① — 第二个端点族 `/store/v1/`（R891，**改产品代码**）：coverage 7 → 8

### 找到 5 条（`/shop/v1/` 之外）

| 路径 | 步骤 |
|---|---|
| `cart/add` · `cart/del` · `cart/listByStore?actionType=1&GID=` | — |
| **`order/listV3?currentPage=1&status=1&pageSize=20`** | **`GetInstoreOrders`（105）** |
| **`product/detail?storeId=`** | **`FindProductInstore`（76）** |

**改动**：`PopMartEndpoints` **+5 常量** · `StoreFlow` **+2 虚方法**（默认失败） · `PopMartFlow` **+2 override**（GET）
**数字**：虚步骤 **172 → 174** · coverage **7 → 8** · `/shop/v1` 41 · `/store/v1` 5 · 套件 **1783 通过 / 0 失败**

### 两点要紧

**① 锚要用**词**不用**形状****
**松正则会抓到 GUID/base64/`3ds` 碎片（70 条无一条含 `order`）；以词为锚一次就对。**
**R890 说「枚举整个空间比搜名字强」；这条补：空间的边界要用词划。**

**② `implementable` 从 7 到 8 不是 9**
**`FindProductInstore` 已实现但**不在 PopMart 的 24 个名字里**（ordinal 76 属 R882 那条更早的段 56–77）。**
**测试两个都钉：`CanRunStep` 真 + `DoesNotContain` 不在 `StepSequence`。**
**→ 「实现了几步」与「序列里有几步」是两个分母。**

| 仍 Unknown | |
|---|---|
| `/store/v1/` 3 条 cart 路径的步骤归属 | 可能是 `AddToCart`/`GetCart` 的 in-store 变体 |
| `storeId` 从哪来 | 同 R872 的 `alias` 形态：会明确失败 |
| 有没有第三个族 | **只在 PopMart 域里找过** |

**纪律**：**空间的边界用词划，不用形状猜。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R891", BLOCKER)
    ensure(RSTATUS, "R891", BLOCKER)
    ensure(RVERDICT, "第 891 轮", VERDICT)
    ensure(BACKLOG, "R891", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R891" not in h:
        h += ("\n## R891 补充 — 第二个端点族 `/store/v1/`（**改产品代码**）：coverage 7 → 8\n\n"
              "**找到 5 条**：`cart/add` · `cart/del` · `cart/listByStore?actionType=1&GID=` · "
              "**`order/listV3?currentPage=1&status=1&pageSize=20`（`GetInstoreOrders` 105）** · **`product/detail?storeId=`（`FindProductInstore` 76）**。\n"
              "**改动**：`PopMartEndpoints` +5 常量 · `StoreFlow` +2 虚方法 · `PopMartFlow` +2 override。**虚步骤 172→174 · coverage 7→8 · 套件 1783 通过。**\n"
              "**两点要紧**：① **锚用词不用形状**（松正则抓 GUID/base64，70 条无一条含 `order`）；② **`implementable` 8 不是 9** —— "
              "`FindProductInstore` 已实现但**不在 PopMart 的 24 个名字里**（ordinal 76 属更早的段），**测试两个都钉**。\n"
              "**下一轮**：`/store/v1/` 那 3 条 cart 路径的步骤归属；有没有第三个族。\n")
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
             for p, k in ((RBLOCK, "R891"), (RSTATUS, "R891"), (RVERDICT, "第 891 轮"), (BACKLOG, "R891")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R891: a second endpoint family, two more steps, and implemented is not the same as sequenced\n\n"
         "R890 narrowed GetInstoreOrders' endpoint to 'not under /shop/v1/'. This round used the same method with a\n"
         " different anchor -- searching all literals for order-shaped paths -- and found it under /store/v1/, which\n"
         " turns out to hold five paths rather than one: cart add, cart delete, cart listByStore, order listV3 and\n"
         " product detail with a storeId.\n\n"
         "So there are two endpoint families and every round from R871 to R890 worked only inside the first. That is\n"
         " the incidental finding and it is larger than the two steps: five paths the replica did not represent at all.\n"
         " Two of them have fixed query shapes, so GetInstoreOrders at ordinal 105 and FindProductInstore at 76 are now\n"
         " written as GETs with no invented body, and three cart paths are recorded with no step because their callers\n"
         " are unidentified.\n\n"
         "The first scan of this round was wrong and its failure mode is worth keeping. A loose path pattern returned\n"
         " seventy matches that were GUIDs, base64 and 3ds fragments, none of them containing order. Anchoring on the\n"
         " word instead of the shape found the endpoint in one pass. R890 concluded that enumerating a space beats\n"
         " searching a name; this round adds that a space's boundary has to be drawn with words rather than guessed\n"
         " from shape.\n\n"
         "Coverage moved from seven to eight rather than nine, and the test caught it by failing with Expected 9,\n"
         " Actual 8. FindProductInstore is implemented but is not one of the twenty-four names in Pop Mart's sequence:\n"
         " it is ordinal 76, in the earlier literal run R882 read that holds the five Start-prefixed flows, while Pop\n"
         " Mart's own run begins at 104. The test now pins both facts, that the step can run and that the sequence does\n"
         " not name it, because implemented and sequenced are separate and two denominators would give two coverage\n"
         " figures.\n\n"
         "Unknown: which steps the three cart paths belong to, where they are plausibly the in-store variants of\n"
         " AddToCart and GetCart; where storeId comes from, since the step reads it from the session and nothing writes\n"
         " it, the same shape as alias in R872 where the step fails clearly instead of running wrongly; and whether a\n"
         " third family exists, since every search so far has been confined to Pop Mart's own domain.\n\n"
         "Product code changed; suite green at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
