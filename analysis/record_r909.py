"""Record R909: the boxSkuId fallback, and the caller that was deliberately not forced."""

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
### 修自己上一轮留的缺陷：`AddToCartBox` 要的变量没人设（R909）

**R908 写了方法，但它要求会话里有个 `boxSkuId` —— 而**没有任何地方设它**。
所以那是一个**写了却调不到**的方法，与 R850 的「有形状无内容」同一层。**

### 改了什么

```
before:  必须 boxSkuId，否则失败
after :  boxSkuId 优先；没有就退到 c.Session.VariantId；两者都无才失败
```

**理由：普通运行里 `VariantId` 已经由 `FindSlot` 设过，所以这个方法现在**在一轮正常流程里可达**。
而显式 `boxSkuId` 仍能覆盖 —— 用于「盯一个盒子、加另一个」的情况。**

### 而 `BoxGoodsList` 与 `BoxExtract` 这一轮**刻意没接**

**查过三个发现步骤：**

| 步骤 | 现在取什么 |
|---|---|
| `FindProduct` | 商品页 `.json` |
| `FindVariant` | 读会话里的 `raw` |
| `FindSlot` | 从 `raw` 正则取 `skuId` |

**`BoxGoodsList`（`goodsListV2`）是列表端点，在这三个里没有自然位置。**

**硬接它会是 R850 的错：**一个看起来在用端点、而语义不明的步骤**。
所以这一轮**不接，并把它写成 Unknown 而不是做成一个假调用者**。**

### 数字

| 度量 | R908 | **R909** |
|---|---|---|
| 套件 | 1805 | **1808** |
| `StoreFlow` 虚步骤 | 175 | 175（不变） |
| box 端点有调用者 | 4 / 6 | 4 / 6（不变） |

**这一轮没有增加覆盖，只把一个不可达的方法变得可达。**

### 3 个用例

| 用例 | 钉住 |
|---|---|
| `TheBoxSkuFallsBackToTheFlowVariant` | 两个名字都被读，且是条件式回退而非两条分支 |
| `ItStillFailsWhenNeitherInputIsPresent` | **两者都无时明确失败** —— 空 sku 静默发送会「成功」而什么也没加 |
| `TheChainUsesFourEndpoints` | 四个端点都在方法体内；**窗口取到下一个 override，不取固定长度** |

**第三个用例第一次是红的，因为我用了固定 2400 字符窗口，第四个端点被截掉了 ——
**那是一次「测试写错而不是代码写错」的红**，而它说明固定长度窗口本身是个坏做法。**
"""

if "修自己上一轮留的缺陷：`AddToCartBox` 要的变量没人设" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R909 appended")

VERDICT = """

---

## 第 909 轮：修 `AddToCartBox` 的不可达输入，并刻意不接那两条端点

### 修了什么

**R908 写了方法，但它要求会话里有个 `boxSkuId` —— 而**没有任何地方设它**。
所以那是一个写了却调不到的方法，与 R850 的「有形状无内容」同一层。**

```
before:  必须 boxSkuId，否则失败
after :  boxSkuId 优先；没有就退到 VariantId；两者都无才失败
```

> **`VariantId` 已由 `FindSlot` 设过，所以这个方法现在在一轮正常流程里可达。
> 而显式 `boxSkuId` 仍能覆盖 —— 用于「盯一个盒子、加另一个」。**

### 而 `BoxGoodsList` 与 `BoxExtract` 刻意没接

| 步骤 | 现在取什么 |
|---|---|
| `FindProduct` | 商品页 `.json` |
| `FindVariant` | 读会话 `raw` |
| `FindSlot` | 从 `raw` 正则取 `skuId` |

**`BoxGoodsList`（`goodsListV2`）是列表端点，在这三个里没有自然位置。**

> **硬接它会是 R850 的错：一个看起来在用端点、而语义不明的步骤。
> 所以这一轮不接，把它写成 Unknown 而不是做成一个假调用者。**

### 数字

| 度量 | R908 | **R909** |
|---|---|---|
| 套件 | 1805 | **1808** |
| box 端点有调用者 | 4 / 6 | 4 / 6 |

**这一轮没有增加覆盖，只把一个不可达的方法变得可达。**

### 一次「测试写错」的红

**`TheChainUsesFourEndpoints` 第一次红，因为我用了固定 2400 字符窗口，第四个端点被截掉了。**

> **那是一次**测试写错而不是代码写错**的红 —— 而它说明固定长度窗口本身是个坏做法。
> 改成取到下一个 `override` 为止。窗口要是跟着代码走，不是跟着一个数字走。**

### 教训

> **R908 那轮我报的是「4/6 有调用者」。而其中一条新接上的端点所属的方法**根本调不到**。
> 所以「有调用者」要问第二句：**那个调用者跑得到吗？****
"""

BACKLOG_ADD = """

## 优先级 ① — `AddToCartBox` 输入修正（R909，**改产品代码 +3 用例**）

### 修

```
before:  必须 boxSkuId（无人设）→ 方法不可达
after :  boxSkuId → 回退 c.Session.VariantId → 都无才失败
```

**`VariantId` 由 `FindSlot` 设过 → 普通流程可达；显式 `boxSkuId` 仍可覆盖。**

### 而 `BoxGoodsList` / `BoxExtract` 刻意不接

**`FindProduct` 取商品页 json · `FindVariant` 读 `raw` · `FindSlot` 正则取 skuId —— `goodsListV2` 在这三个里无自然位置。**
**→ 硬接 = R850 的「有形状无内容」，故留 Unknown。**

### 数字

**套件 1805 → 1808 · 虚步骤 175（不变）· box 调用者 4/6（不变）**
**这一轮不增覆盖，只把不可达变可达。**

### 一次测试写错的红

**`TheChainUsesFourEndpoints` 用固定 2400 字符窗口 → 第四个端点被截 → 红。改成取到下一个 `override`。**

| 仍 Unknown | |
|---|---|
| `BoxGoodsList` 的调用者 | 列表端点，发现侧无自然位置 |
| `BoxExtract` vs `BoxSetExtract` | 两变体 |
| 5 个 AddToCart 真缺口 | 各自实现未读 |

**纪律**：**「有调用者」要问第二句 —— 那个调用者跑得到吗？**
"""

BLOCKER = """

---

## 333. `AddToCartBox` 输入修正：不可达变可达；两条端点刻意不接

> R909。**改产品代码 +3 用例。** 套件 **1808 通过 / 0 失败 / 0 跳过**。

### 一、修的是我自己上一轮留的缺陷

**R908 写了方法，但它要求 `boxSkuId` —— **没有任何地方设它**。所以写了却调不到，与 R850 同层。**

```
before:  必须 boxSkuId，否则失败
after :  boxSkuId 优先 → 回退 c.Session.VariantId → 都无才失败
```

**`VariantId` 由 `FindSlot` 设过 → 普通流程可达；显式 `boxSkuId` 仍可覆盖。**

### 二、两条端点刻意不接

| 步骤 | 取什么 |
|---|---|
| `FindProduct` | 商品页 `.json` |
| `FindVariant` | 读 `raw` |
| `FindSlot` | 正则取 `skuId` |

**`BoxGoodsList`（`goodsListV2`）在这三个里无自然位置。硬接 = R850 的「有形状无内容」。**

### 三、数字

| 度量 | R908 | R909 |
|---|---|---|
| 套件 | 1805 | **1808** |
| 虚步骤 | 175 | 175 |
| box 调用者 | 4 / 6 | 4 / 6 |

**不增覆盖，只把不可达变可达。**

### 四、一次「测试写错」的红

**`TheChainUsesFourEndpoints` 第一次红 —— 固定 2400 字符窗口把第四个端点截掉了。**

**那是**测试写错而不是代码写错**。改成取到下一个 `override`：窗口跟着代码走，不跟着数字走。**

### 五、验证

```
test --filter AddToCartBoxInputTests -> 3 通过
box 常量调用者                       -> 4 / 6（不变）
async_method_coverage.py             -> 311 / 1547（不变）
metrics_report.py                    -> 1808 通过 / 0 失败
```

### 六、仍然 Unknown

- **`BoxGoodsList` 的调用者**：**Unknown** —— 列表端点，发现侧三个步骤都无自然位置。
- **`BoxExtract` 与 `BoxSetExtract`**：**Unknown** —— 两变体，我用了后者。
- **`AddToCart` 那 5 个真缺口**：**各自实现未读。**

### 七、教训

**R908 我报「4/6 有调用者」。而其中一条新接上的端点所属的方法**根本调不到**。**

**所以「有调用者」要问第二句：**那个调用者跑得到吗？**

**这一轮两个数字（4/6、175）都没动，而可达性变了 —— 所以数字不动不等于没有改进，
也不等于改进被记下来了。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R909", BLOCKER)
    ensure(RSTATUS, "R909", BLOCKER)
    ensure(RVERDICT, "第 909 轮", VERDICT)
    ensure(BACKLOG, "R909", BACKLOG_ADD)

    note = (
        "\n## R909 补充 — AddToCartBox 输入修正（改产品代码 +3 用例，套件 1805→1808）\n\n"
        "修的是 R908 自己留的缺陷：方法要求 boxSkuId 而无人设 → 写了却调不到（R850 同层）。\n"
        "改成 boxSkuId 优先 → 回退 VariantId → 都无才失败。VariantId 由 FindSlot 设过，故普通流程可达。\n\n"
        "BoxGoodsList 与 BoxExtract 刻意不接：FindProduct 取 json、FindVariant 读 raw、FindSlot 正则取 skuId，"
        "goodsListV2 在这三个里无自然位置；硬接 = 有形状无内容。\n\n"
        "数字：套件 1808 · 虚步骤 175（不变）· box 调用者 4/6（不变）—— 不增覆盖，只把不可达变可达。\n\n"
        "一次测试写错的红：固定 2400 字符窗口截掉第四个端点 → 改成取到下一个 override。\n\n"
        "纪律：「有调用者」要问第二句 —— 那个调用者跑得到吗？\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R909" not in h:
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
             for p, k in ((RBLOCK, "R909"), (RSTATUS, "R909"), (RVERDICT, "第 909 轮"), (BACKLOG, "R909")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R909: AddToCartBox becomes reachable, and two endpoints are deliberately left unwired\n\n"
         "R908 wrote the method and required a session variable nothing set, which made a written method uncallable in\n"
         " an ordinary run -- R850's shape without content, one layer up. The fix gives it a fallback to the flow's own\n"
         " variant, which FindSlot already sets, while an explicit boxSkuId still overrides for the case of watching one\n"
         " box and adding another.\n\n"
         "The goods list and the plain extract remain uncalled, and that is a decision rather than an omission. The\n"
         " three discovery steps were read first: FindProduct fetches the product page's json, FindVariant reads the raw\n"
         " body from the session, and FindSlot pulls a skuId out of it with a regex. A listing endpoint has no natural\n"
         " place among those, and wiring one anyway would produce a step that appears to use an endpoint whose meaning\n"
         " is unknown -- exactly what R850 warns about. So it stays Unknown instead of acquiring a fake caller.\n\n"
         "The suite goes from 1805 to 1808 while the virtual count stays at 175 and the box caller count stays at four\n"
         " of six. Nothing gained coverage this round; what changed is reachability, which no figure here records.\n\n"
         "One test failure belongs in the record because it was the test's fault. The chain test used a fixed 2400\n"
         " character window measured from the method signature, which cut the fourth endpoint off and failed for a\n"
         " reason that had nothing to do with the code. It now runs to the next override, so the window follows the code\n"
         " rather than a number.\n\n"
         "Unknown: what calls the goods list, since the discovery side has no natural place for it; how the plain\n"
         " extract differs from the set extract; and what each of the five real AddToCart gaps implements.\n\n"
         "The lesson is a second question behind the first. Saying a family has four of six callers says nothing about\n"
         " whether those four callers can run, and one of the four was behind a method that could not.\n\n"
         "Product code changed; suite green at 1808."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
