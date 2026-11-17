"""Record R968: the attribute changed nothing measurable, and the body-string check has reached its limit."""

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
### 属性加了、名字全在、体还是不在 —— 而这个核对方法到头了（R968）

**R967 说下一轮用对的编码重核 body 串。这一轮做了，结果是一张表。**

### 加了 `[DynamicallyAccessedMembers(PublicMethods)]` 之后

| 串 | 编码 | 在产物 |
|---|---|---|
| `bstn: cart endpoint unknown` | body UTF-16 | **True** |
| `bstn: checkout endpoint unknown (Adyen)` | body UTF-16 | False |
| `nike: no kasada script loaded` | body UTF-16 | False |
| `popmart-orders` | body UTF-16 | False |
| `shopify: no profile to fill from` | body UTF-16 | False |
| `GetCsrfAsync` · `GetCartAsync` · `StoreFlow` | name UTF-8 | **全 True** |

**而 `pdata-replica` 仍是 173,952。**

### 所以现在确定的是两件事

1. **方法**元数据全部保留**（179/179 名字在 UTF-8 里）→ 反射表能建起来**
2. **方法**体大部分被裁**（4/5 抽样的串不在）

> **而这两件并存说明：`MethodInfo` 存在、`Invoke` 能调、而**被调到的那个方法体可能已经不在了**。
> 那是 NativeAOT 下一个具体的失败形态：反射找得到方法，调用时抛。**
> **而 `[DynamicallyAccessedMembers]` 只保证**元数据**，不保证**体** —— 那是这一轮的 Inference，
> 而它有一个反例（我的属性没起任何可见作用）。**

### 而这个核对方法**到头了**

**`bstn: cart endpoint unknown` 在、`bstn: checkout endpoint unknown (Adyen)` 不在 ——
两个都是同一个类里的同步表达式体 `Task.FromResult(StepOutcome.Fail(...))`。

> **所以「同步还是 async」不是解释，「覆写与否」也不是（两个都是覆写）。
> 而 R964 已经证明：body 串**不在**不能证明 body 不在产物里（R964 的 `www.bstn.com` 在、
> 同方法带协议的完整串不在 —— 字符串是被拆开存的）。**
> **所以这张表**只能读正向**：在 → 在。不在 → **什么都不能说**。**
> **而 4 个「不在」里有多少是假的，这个工具答不了。**

### 所以下一轮该查的不是这个

**62.77% 的缺口需要一个**分布**，不是一个开关。而我现在只有总数。**

> **具体要做的：把 `target\\Cybersole.exe` 与 `.publish-aot` 的 `.pdata` 都按**地址段**切开，
> 看缺口分布在哪一段。原版 277,120 个函数分布在若干区段，而复刻件 173,952 ——
> **如果缺口集中在某几段，那答案在那几段；如果均匀分布，那答案在别处。**
> **而这个工具我还没有。写在下一轮。****

### 数字

| 度量 | R967 | **R968** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952（属性无影响，第二次确认）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,728 KB | **54,728 KB** |
| 名字在场（UTF-8） | 179/179 | **179/179** |
| body 串在场（UTF-16 抽样 5） | — | **1 / 5** |

### 教训

> **这一轮最有价值的不是那张表，是**承认那张表只能读一半**。
> 它的「不在」列有 4 项，而我没有一项能当结论用。**
> **而上一轮我刚学会「检查要两向对照」—— 这一轮发现**方向对了也不够**：
> 被查的东西本身会被拆开存，于是「不在」这一向在原理上就不可用，不是还没来得及验证。**
"""

if "属性加了、名字全在、体还是不在" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 968 轮：属性加了、名字全在、体还是不在 —— 而核对方法到头了

### 加了 `[DynamicallyAccessedMembers(PublicMethods)]` 之后

| 串 | 编码 | 在产物 |
|---|---|---|
| `bstn: cart endpoint unknown` | body UTF-16 | **True** |
| `bstn: checkout endpoint unknown (Adyen)` | body UTF-16 | False |
| `nike: no kasada script loaded` | body UTF-16 | False |
| `popmart-orders` | body UTF-16 | False |
| `shopify: no profile to fill from` | body UTF-16 | False |
| `GetCsrfAsync` · `GetCartAsync` · `StoreFlow` | name UTF-8 | **全 True** |

**`pdata-replica` 仍 173,952 —— 属性第二次确认无影响。**

### 确定的两件事

1. **方法**元数据全部保留**（179/179 名字在 UTF-8）→ 反射表能建**
2. **方法**体大部分被裁**（4/5 抽样串不在）

> **两件并存说明：`MethodInfo` 存在、`Invoke` 能调、而**被调到的那个体可能已经不在了**。
> 那是 NativeAOT 下一个具体的失败形态：反射找得到方法，调用时抛。**

### 而这个核对方法**到头了**

**`bstn: cart endpoint unknown` 在、`bstn: checkout endpoint unknown (Adyen)` 不在 ——
两个都是同一个类里的同步表达式体 `Task.FromResult(StepOutcome.Fail(...))`。**

> **所以「同步 vs async」不是解释，「覆写与否」也不是（两个都是覆写）。
> 而 R964 已证 body 串**不在**不能证明 body 不在（字符串会被拆开存）。
> → **这张表只能读正向：在 → 在。不在 → 什么都不能说。**
> **4 个「不在」里有多少是假的，这个工具答不了。**

### 下一轮该查的不是这个

**62.77% 需要一个**分布**，不是一个开关。**

**具体：把两边 `.pdata` 按**地址段**切开，看缺口分布在哪些段。
集中在某几段 → 答案在那几段；均匀分布 → 答案在别处。这个工具还没有。**

### 数字

| 度量 | R967 | **R968** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952（第二次确认）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,728 KB | **54,728 KB** |
| 名字在场（UTF-8） | 179/179 | **179/179** |
| body 串在场（UTF-16 抽样 5） | — | **1 / 5** |

### 教训

> **最有价值的不是那张表，是承认它**只能读一半**。
> 上一轮刚学会「检查要两向对照」—— 这一轮发现方向对了也不够：
> 被查的东西本身会被拆开存，于是「不在」这一向在**原理上**就不可用，不是还没来得及验证。**
"""

BACKLOG_ADD = """

## 判据 (c) — 属性无影响第二次确认；body 串核对**原理上只能读一半**（R968）

### 观测

**`[DynamicallyAccessedMembers(PublicMethods)]` 后：`pdata-replica` 173,952 不变；
名字 179/179 在（UTF-8）；body 串抽样 5 个中 1 个在（UTF-16）。**

### 两条并存

**方法元数据在 → 反射表能建；方法体大部分被裁 → `Invoke` 能找到方法但体可能不在。**

### 核对方法的极限

**`bstn: cart endpoint unknown` 在、`bstn: checkout endpoint unknown (Adyen)` 不在 ——
同类、同形状、都是覆写。所以「同步/async」「覆写与否」都不是解释。**

**而 R964 已证字符串会被拆开存 → **「不在」这一向在原理上不可用**。**

### 下一轮的具体目标

**把两边 `.pdata` 按**地址段**切开，做出**缺口分布** —— 工具还没有，本轮立此目标。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 产物 54,728 KB · 名字 179/179 · body 1/5**

| 仍 Unknown | |
|---|---|
| body 串「不在」的真实比例 | 工具答不了 |
| 62.77% 缺口的分布 | 需新工具 |

**纪律**：方向对了也不够 —— 被查的东西本身会被拆开存。
"""

BLOCKER = """

---

## 392. 属性无影响（第二次确认）；body 串核对**原理上只能读一半**

> R968。**只取证。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、观测表

| 串 | 编码 | 在产物 |
|---|---|---|
| `bstn: cart endpoint unknown` | body UTF-16 | **True** |
| `bstn: checkout endpoint unknown (Adyen)` | body UTF-16 | False |
| `nike: no kasada script loaded` | body UTF-16 | False |
| `popmart-orders` | body UTF-16 | False |
| `shopify: no profile to fill from` | body UTF-16 | False |
| `GetCsrfAsync` · `GetCartAsync` · `StoreFlow` | name UTF-8 | **全 True** |

**`pdata-replica` 仍 173,952。**

### 二、两条并存

**方法元数据在（179/179）→ 反射表能建；方法体大部分被裁（4/5）→
`MethodInfo` 存在、`Invoke` 能调、而**被调到的体可能已经不在了**。**

### 三、核对方法的极限

**两个都是同一个类里的同步表达式体 `Task.FromResult(StepOutcome.Fail(...))`，
一个在、一个不在 → 「同步/async」不是解释、「覆写与否」也不是。**

**而 R964 已证字符串会被拆开存 → **「不在」这一向在原理上不可用**。**

**所以这张表只能读正向：在 → 在；不在 → 什么都不能说。**

### 四、下一轮的具体目标

**62.77% 需要一个**分布**：把两边 `.pdata` 按地址段切开，看缺口集中在哪些段。
**这个工具还没有，本轮立此目标。****

### 五、数字

| 度量 | R967 | R968 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,728 KB | **54,728 KB** |
| 名字 UTF-8 | 179/179 | **179/179** |
| body UTF-16 抽样 | — | **1 / 5** |

### 六、验证

```
python -c "..." 查 8 个串（5 body UTF-16 + 3 name UTF-8）
  -> 名字全 True；body 仅 'bstn: cart endpoint unknown' True
func_count.py -> 173,952
metrics_report.py -> 2186 通过 / 0 失败
```

### 七、仍然 Unknown

- **body 串「不在」的真实比例**：**Unknown** —— 工具在原理上答不了。
- **62.77% 缺口的分布**：**Unknown** —— 需新工具。

### 八、教训

**方向对了也不够 —— 被查的东西本身会被拆开存，于是「不在」这一向在原理上就不可用，
不是还没来得及验证。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R968", BLOCKER)
    ensure(RSTATUS, "R968", BLOCKER)
    ensure(RVERDICT, "第 968 轮", VERDICT)
    ensure(BACKLOG, "R968", BACKLOG_ADD)

    note = (
        "\n## R968 补充 — 属性无影响（第二次确认）；body 串核对**原理上只能读一半**（套件 2186）\n\n"
        "加属性后：`pdata-replica` 173,952 不变；名字 179/179 在（UTF-8）；\n"
        "body 串抽样 5 个：`bstn: cart endpoint unknown` **True**，其余 4 个 False。\n\n"
        "**两条并存**：方法元数据在 → 反射表能建；方法体大部分被裁 → `MethodInfo` 存在、`Invoke` 能调、\n"
        "而**被调到的体可能已经不在了**。\n\n"
        "**而核对方法到头了**：`bstn: cart endpoint unknown` 在、`bstn: checkout endpoint unknown (Adyen)` 不在 ——\n"
        "同类、同形状、都是覆写。而 R964 已证字符串会被拆开存 → **「不在」这一向在原理上不可用**。\n"
        "→ 这张表**只能读正向**：在 → 在；不在 → 什么都不能说。\n\n"
        "**下一轮具体目标**：把两边 `.pdata` 按**地址段**切开，做出**缺口分布**（工具还没有，本轮立此目标）。\n"
        "集中在某几段 → 答案在那几段；均匀分布 → 答案在别处。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 产物 54,728 KB · 名字 179/179 · body 1/5。\n\n"
        "纪律：方向对了也不够 —— 被查的东西本身会被拆开存。\n\n"
        "下一轮：写 `tools/pdata_sections.py`，把两边 .pdata 按地址段统计，给出缺口分布。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R968" not in h:
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
             for p, k in ((RBLOCK, "R968"), (RSTATUS, "R968"), (RVERDICT, "第 968 轮"), (BACKLOG, "R968")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R968: the attribute changed nothing again, and the body-string check can only be read one way\n\n"
         "R967 left a plan to recheck the override body strings now that the encodings are known: reflection metadata is\n"
         " UTF-8 and string literals are UTF-16. This round did that and produced a table.\n\n"
         "After DynamicallyAccessedMembers on StoreFlow, the count is still 173,952, all 179 step names are present as\n"
         " UTF-8, and of five sampled body strings only one is present: the cart endpoint message from BstnFlow survives,\n"
         " while the checkout endpoint message from the same class, the Nike Kasada message, the Pop Mart orders key and the\n"
         " Shopify profile message do not.\n\n"
         "Two facts now sit together. Method metadata is all there, so the reflection table builds. Method bodies are mostly\n"
         " gone, so Invoke can find a method whose body was removed. That is a specific failure shape under NativeAOT and it\n"
         " would explain a table that looks populated while dispatching to nothing.\n\n"
         "But the check has reached its limit, and that is the round's real content. The two Bstn strings are the same shape\n"
         " in the same class -- a synchronous expression body returning a Fail -- and one is present while the other is not.\n"
         " So neither async versus sync nor override versus base explains it. And R964 already showed that a retained\n"
         " method can keep some of its literals and drop others, which means absence cannot be read as evidence of absence\n"
         " at all. The table can only be read in the positive direction: present proves present, and absent says nothing.\n"
         " Four of the five rows are therefore unusable, not pending further verification.\n\n"
         "So the next question is not another switch but a distribution. Where the missing thirty-seven percent sits needs\n"
         " the two .pdata tables cut into address ranges and compared, because a gap concentrated in a few ranges points at\n"
         " those ranges while an even spread points somewhere else entirely. That tool does not exist yet and is set down\n"
         " here as the next target.\n\n"
         "Figures: suite 2186, count 173,952 for the second time, freshness zero, artifact 54,728 kilobytes, names 179 of\n"
         " 179, body strings 1 of 5.\n\n"
         "Unknown: the real proportion of absent body strings, which this tool cannot answer in principle; and the shape of\n"
         " the gap, which needs the new tool.\n\n"
         "The lesson is that getting the direction right was not enough. When the thing being searched for is itself stored\n"
         " split apart, the negative direction is unavailable in principle rather than merely unverified, and no amount of\n"
         " controls on that direction will make it usable.\n\n"
         "No product code changed; one document and the backlog updated."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()