"""Record R908: AddToCartBox implemented, and the five dead box endpoints it gives callers to."""

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
### `AddToCartBox` 实现了 —— 而它给 5 条死端点接上了调用者（R908）

**R907 说下一轮补 `AddToCartBox`。补了。**

### 先核了一遍「6 条 box 端点有没有调用者」

| 端点 | 之前 |
|---|---|
| `AddBoxListToCart` | **有 1 个**（PopMart 的 `AddToCart` 在用） |
| `BoxGoodsList` · `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` · `BoxExtract` | **全无** |

**所以 R907 那句「6 条端点没被调用」要修成「1 条有、5 条没有」。
而那一 条正是 `AddToCart` 用的 —— 它让整族**看起来**被覆盖了。**

### 实现了什么

**`AddToCartBoxAsync`（基类虚方法 + PopMart override），四步：**

1. `BoxSpuDetail?skuId=` —— 盒子属于哪个套装
2. `BoxSetPreview?skuId=` —— 套装里有什么（不揭示内容）
3. `BoxSetExtract` —— 从套装里抽一个
4. `AddBoxListToCart` —— 把抽到的条目加进车

**而 `AddToCartBox` 不在 PopMart 那 24 个名字里** —— 所以它像 `FindProductInstore` 一样：
**方法在、序列不列。** `implementable` 仍是 8，`map` 从 174 到 **175**。

### 调用者变化

| 端点 | 之前 | 之后 |
|---|---|---|
| `AddBoxListToCart` | 1 | **2** |
| `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` | 0 | **各 1** |
| `BoxGoodsList` · `BoxExtract` | 0 | **仍 0** |

**剩下两条仍无调用者，而它们各有一说：**
- **`BoxGoodsList`（`goodsListV2`）是列表端点** —— 属于「发现」而非「加车」，不该由这个方法用。
- **`BoxExtract`（`/box/extract`）与 `BoxSetExtract`（`/box_set/extract`）是两个变体** —— 我用了后者，前者不明。

### 异步覆盖

**310 → **311**（20.1%）—— 一个方法。这一族 15 个名字里现在 9 有 6 缺。**

### 而顺序与参数是 Inference

**镜像证明的是：有个方法叫 `AddToCartBox`，而 5 条端点在。**
**没证明的是：那四步的顺序、以及每一步的请求体。**

**所以方法里用的是最小 payload，而缺会话变量时**明确失败**（要 `boxSkuId`），不猜。**
"""

if "`AddToCartBox` 实现了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R908 appended")

VERDICT = """

---

## 第 908 轮：`AddToCartBox` 实现，给 5 条死端点接上调用者

### 先核「6 条 box 端点有没有调用者」

| 端点 | 之前 |
|---|---|
| `AddBoxListToCart` | **有 1 个**（`AddToCart` 在用） |
| `BoxGoodsList` · `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` · `BoxExtract` | **全无** |

> **所以 R907 那句「6 条没被调用」要修成「1 有 5 无」—— 而那一 条让整族**看起来**被覆盖了。**

### 实现了什么

**`AddToCartBoxAsync`（虚方法 + PopMart override），四步：**

1. `BoxSpuDetail?skuId=` —— 属于哪个套装
2. `BoxSetPreview?skuId=` —— 套装里有什么
3. `BoxSetExtract` —— 抽一个
4. `AddBoxListToCart` —— 加进车

**它不在 PopMart 那 24 个名字里 → 像 `FindProductInstore`：方法在、序列不列。
`implementable` 仍 8，`map` 174 → **175**。**

### 调用者变化

| 端点 | 之前 | 之后 |
|---|---|---|
| `AddBoxListToCart` | 1 | **2** |
| `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` | 0 | **各 1** |
| `BoxGoodsList` · `BoxExtract` | 0 | **仍 0** |

**剩下两条各有一说：`BoxGoodsList` 是列表端点（属「发现」非「加车」）；
`BoxExtract` 与 `BoxSetExtract` 是两个变体，我用了后者，前者不明。**

### 异步覆盖

**310 → 311（20.1%）—— 一个方法。这一族 15 个名字里现在 9 有 6 缺。**

### 而顺序与参数是 Inference

> **镜像证明：有个方法叫 `AddToCartBox`，5 条端点在。
> 没证明：那四步的顺序、每步的请求体。**
> **所以用最小 payload，缺会话变量时明确失败（要 `boxSkuId`），不猜。**

### 教训

> **这一族的教训是「一条有调用者」比「零条」更危险 —— 它让整族看起来被覆盖。
> 而我上一轮写「6 条端点没被调用」时，就是把 1 和 0 混着说的。**
"""

BACKLOG_ADD = """

## 优先级 ① — `AddToCartBox` 实现（R908，**改产品代码**）

### 6 条 box 端点的调用者（之前 → 之后）

| 端点 | 之前 | 之后 |
|---|---|---|
| `AddBoxListToCart` | 1 | **2** |
| `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` | 0 | **各 1** |
| `BoxGoodsList` · `BoxExtract` | 0 | **仍 0** |

### 四步链

**`BoxSpuDetail?skuId=` → `BoxSetPreview?skuId=` → `BoxSetExtract` → `AddBoxListToCart`**

### 数字

**`StoreFlow` 虚步骤 174 → **175**（`AddToCartBoxAsync`）· `implementable` 仍 **8**（不在 24 名里）·
异步覆盖 310 → **311（20.1%）** · 套件 **1805 通过**

| 仍 Unknown | |
|---|---|
| 四步顺序与请求体 | **Inference** |
| `BoxGoodsList` 的调用者 | 属「发现」步骤 |
| `BoxExtract` vs `BoxSetExtract` | 两变体，前者不明 |

**纪律**：**「1 条有调用者」比「零条」更危险 —— 它让整族看起来被覆盖。**
"""

BLOCKER = """

---

## 332. `AddToCartBox` 实现：5 条死端点接上了调用者；虚步骤 174 → 175

> R908。**改产品代码。** 套件 **1805 通过 / 0 失败 / 0 跳过**。

### 一、先核了一遍

| 端点 | 之前 |
|---|---|
| `AddBoxListToCart` | **1 个**（`AddToCart` 在用） |
| 其余 5 条 | **全无** |

**所以 R907 的「6 条没被调用」要修成「1 有 5 无」。而那一 条让整族看起来被覆盖。**

### 二、四步链

**`BoxSpuDetail?skuId=` → `BoxSetPreview?skuId=` → `BoxSetExtract` → `AddBoxListToCart`**

**`AddToCartBox` 不在 PopMart 的 24 名里 → 方法在、序列不列，同 `FindProductInstore`。**

### 三、数字

| 度量 | 之前 | 之后 |
|---|---|---|
| `StoreFlow` 虚步骤 | 174 | **175** |
| `implementable` | 8 | **8**（不变） |
| 异步覆盖 | 310（20.0%） | **311（20.1%）** |
| box 端点有调用者 | 1 / 6 | **4 / 6** |

### 四、剩下两条无调用者

- **`BoxGoodsList`（`goodsListV2`）**：列表端点 —— 属「发现」，不该由加车方法用。
- **`BoxExtract`（`/box/extract`）vs `BoxSetExtract`（`/box_set/extract`）**：两个变体，我用了后者。

### 五、验证

```
box 常量调用者计数           -> 之前 1/6，之后 4/6
StoreFlow 虚步骤             -> 175
test --filter FlowSequenceTests -> 7 通过
async_method_coverage.py     -> 311 / 1547 = 20.1%
metrics_report.py            -> 1805 通过 / 0 失败
```

### 六、仍然 Unknown

- **四步的顺序**：**Inference** —— 名字的自然读法，非观察。
- **每步的请求体**：**Unknown** —— 所以用最小 payload。
- **`BoxGoodsList` 与 `BoxExtract` 的调用者**：**Unknown**。

### 七、教训

**「1 条有调用者」比「零条」更危险 —— 它让整族看起来被覆盖。**

**而我上一轮写「6 条端点没被调用」时，就是把 1 和 0 混着说的。
这一轮核了一遍才发现是 1 有 5 无。**

**所以「这族被覆盖了」这句话要拆成「几条有调用者 / 共几条」。一个数不够。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R908", BLOCKER)
    ensure(RSTATUS, "R908", BLOCKER)
    ensure(RVERDICT, "第 908 轮", VERDICT)
    ensure(BACKLOG, "R908", BACKLOG_ADD)

    note = (
        "\n## R908 补充 — AddToCartBox 实现（改产品代码）\n\n"
        "先核了一遍 6 条 box 端点的调用者：之前 AddBoxListToCart 有 1 个（AddToCart 在用），其余 5 条全无。"
        "R907 的「6 条没被调用」要修成「1 有 5 无」—— 而那一条让整族看起来被覆盖。\n\n"
        "四步链：BoxSpuDetail?skuId= → BoxSetPreview?skuId= → BoxSetExtract → AddBoxListToCart。\n\n"
        "数字：StoreFlow 虚步骤 174 → 175 · implementable 仍 8（不在 24 名里）· 异步覆盖 310 → 311（20.1%）· "
        "box 端点有调用者 1/6 → 4/6 · 套件 1805 通过。\n\n"
        "剩下 BoxGoodsList（列表端点）与 BoxExtract（另一变体）仍无调用者。\n\n"
        "下一轮：BoxGoodsList 的调用者（属「发现」步骤，可能是 FindVariant 或 FindProduct 的一个分支）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R908" not in h:
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
             for p, k in ((RBLOCK, "R908"), (RSTATUS, "R908"), (RVERDICT, "第 908 轮"), (BACKLOG, "R908")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R908: AddToCartBox implemented, giving five dead box endpoints a caller\n\n"
         "R907 found AddToCartBox among the image's method names and noted that five of the six /shop/v1/box/ constants\n"
         " had no caller. This round checked that claim first and it needed amending: one of the six did have a caller,\n"
         " addBoxListToCart, reached from Pop Mart's ordinary AddToCart. That single caller is what made the family look\n"
         " covered when five sixths of it was dead.\n\n"
         "The method now walks the chain the names imply: the SPU detail to learn which set a box belongs to, the set\n"
         " preview to see what it holds, the set extract to take one out, and then the ordinary cart call to add the\n"
         " extracted line. Four of the six endpoints have callers afterwards; the goods list and the plain extract still\n"
         " do not, and each has a reason -- the goods list belongs to discovery rather than to adding, and the plain\n"
         " extract is a second variant beside the set extract that this method uses.\n\n"
         "AddToCartBox is not one of Pop Mart's twenty-four sequence names, so it behaves like FindProductInstore: the\n"
         " method exists and the sequence does not list it. The virtual count goes from 174 to 175 while implementable\n"
         " stays at eight.\n\n"
         "Async method coverage moves from 310 to 311, twenty point one percent. Within the AddToCart family, nine of\n"
         " fifteen names are now present and six are not.\n\n"
         "What is inference rather than observation is the order of the four calls and every request body. The image\n"
         " establishes that a method named AddToCartBox exists and that these endpoints exist; it does not establish the\n"
         " sequence or the payloads, so the method sends minimal bodies and fails explicitly when boxSkuId is missing\n"
         " rather than guessing one.\n\n"
         "Unknown: the four-step order, which is a reading of the names; each step's request body; and what calls the\n"
         " goods list and the plain extract.\n\n"
         "The lesson is that one caller out of six is more misleading than none, because a family with a live member\n"
         " reads as live. Saying a family is covered needs splitting into how many members are reached out of how many,\n"
         " and one number will not do.\n\n"
         "Product code changed; suite green at 1805."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
