"""Record R919: Dicks Sporting Goods, and the payoff of the coverage table criterion (f) produced."""

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
### DicksSportingGoods 补上 —— 而 (f) 那张表两轮就清空了两个真缺口（R919）

**R917 的表剩两个真缺口：`sportsshoes` 与 `dickssportinggoods`。R918 补了前者，这一轮补后者。**

### 比 R917 那 6 条更多的证据：九条，分三组

```
身份  "DICKS" · "DicksSportingGoods" · "Dicks Sporting Goods" · "dsg-ecomm"
端点  https://www.dickssportinggoods.com/
      https://api-search.dickssportinggoods.com/catalog-productdetails/v4/byPartNumber/
      https://payments.dickssportinggoods.com/prod/api/paygate/v2/authorization
      https://payments.dickssportinggoods.com/prod/api/paygate/v2/threeDSAuthentication
行为  "_outOfStock(Dicks Sporting Goods"
```

### 三件值得说的事

**① 身份有**四种形式**，不是「显示名 + id」两种。
`dsg-ecomm` 像是请求里带的 channel/应用名，`DICKS` 像短标签。
**所以四个都记成常量，不挑一个 —— 哪个出现在请求里不知道，猜一个会把错值放进 header。**

**② 行为那条最有信息量：`_outOfStock` 是**闭包名**，
说明原版对这个店**专门挂了一个缺货回调**。那是监控关注点而不是结账关注点，所以按监控建模。**

**③ 而这个店**没有车/结账路径**被恢复 —— 端点只有按零件号查商品和支付闸。**

> **所以 `StepSequence` 只有两步：`FindProduct` 与 `SubmitPayment`。
> 一个有支付闸、却没有任何车调用的店，用这份证据走不完一次购买；
> 写一个更长的序列会是一串在第二步就失败的步骤。**

### 两个刻意的实现决定

**① 商品是按**零件号**查的，不是按 URL 取页面。**
`byPartNumber/` 是版本段之后的整个路径段 —— 去取商品页就是读另一个端点，不是镜像点名的那个。

**② 3DS 是有条件的。**
两条 paygate 调用在镜像里是分开的，这里也分开：**总是跑第二步会给不需要验证的订单做验证。**
**而判据是授权响应自己说要不要，不是流程预设。**

### 数字

| 度量 | R918 | **R919** |
|---|---|---|
| 套件 | 1842 | **1850** |
| 模块 | 64 | **65** |
| flow 类型 | 34 | **35** |
| **store 宿主覆盖** | 23 / 28 | **24 / 28** |

**剩下 4 个未匹配：`braintreegateway` · `vipps` · `bigcommerce` · `purpledotprice` —— 前三个是支付商子域。**

### 而这一轮的价值不在这个店本身

**R917 建那张表用了两次修正；R918 与 R919 用它清掉了**它列出的两个真缺口**。**

> **所以那张表的正确用法不是「覆盖率多高」，而是**它列出的未匹配项就是待办清单**。**
> **而 24/28 里剩下的 4 个，三个已被判为支付商子域 —— 也就是说这张表**快用完了**。**
"""

if "DicksSportingGoods 补上" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R919 appended")

VERDICT = """

---

## 第 919 轮：DicksSportingGoods 补上 —— (f) 那张表两轮清空了两个真缺口

### 九条证据，分三组

```
身份  "DICKS" · "DicksSportingGoods" · "Dicks Sporting Goods" · "dsg-ecomm"
端点  www.dickssportinggoods.com/
      api-search.dickssportinggoods.com/catalog-productdetails/v4/byPartNumber/
      payments.dickssportinggoods.com/prod/api/paygate/v2/{authorization, threeDSAuthentication}
行为  "_outOfStock(Dicks Sporting Goods"
```

### 三件值得说的事

**① 身份有**四种形式**。`dsg-ecomm` 像请求里的 channel 名，`DICKS` 像短标签。
**四个都记成常量，不挑一个 —— 哪个出现在请求里不知道，猜一个会把错值放进 header。**

**② `_outOfStock` 是**闭包名** → 原版对这个店**专门挂了一个缺货回调**。按监控建模，不按结账。**

**③ 这个店**没有车/结账路径**被恢复 —— 只有按零件号查商品和支付闸。**

> **所以序列只有两步。一个有支付闸、却没有任何车调用的店，用这份证据走不完一次购买；
> 写更长的序列会是一串在第二步就失败的步骤。**

### 两个实现决定

**① 商品按**零件号**查**（`byPartNumber/` 是版本段后的整段），不是取商品页 —— 取页面就是读另一个端点。
**② 3DS 有条件**：两条 paygate 调用分开，判据是授权响应自己说要不要，不是流程预设。

### 数字

| 度量 | R918 | **R919** |
|---|---|---|
| 套件 | 1842 | **1850** |
| 模块 | 64 | **65** |
| flow 类型 | 34 | **35** |
| store 宿主覆盖 | 23 / 28 | **24 / 28** |

**剩 4 个未匹配：`braintreegateway` · `vipps` · `bigcommerce` · `purpledotprice` —— 前三个是支付商子域。**

### 而这一轮的价值不在这个店本身

> **R917 建那张表用了两次修正；R918 与 R919 用它清掉了它列出的两个真缺口。**
> **所以那张表的正确用法不是「覆盖率多高」，而是**它列出的未匹配项就是待办清单**。
> 而 24/28 剩下的 4 个里三个已被判为支付商子域 —— **这张表快用完了**。**

### 教训

> **一个度量工具最大的价值不是它报的数，是它报出来的**清单**。
> 7/28 那个数当时是错的，而它列出的 21 个名字里有 2 个是真的 —— 修正判据之后，那 2 个还在。**
"""

BACKLOG_ADD = """

## 优先级 ① — DicksSportingGoods 补上（R919，**改产品代码 +8 用例**）

### 九条证据

**身份 4 种：`DICKS` · `DicksSportingGoods` · `Dicks Sporting Goods` · `dsg-ecomm`**
**端点 4 条：www / api-search`byPartNumber` / paygate`authorization` / paygate`threeDSAuthentication`**
**行为 1 条：`_outOfStock`（闭包名 → 缺货回调）**

### 改动

**`Flows/DicksSportingGoodsFlow.cs` 新建（4 身份常量 + 3 宿主 + 4 地址 + 2 步骤）· `Registry.cs` 注册 · 8 用例**

### 两个实现决定

**按零件号查商品（不取页面）· 3DS 有条件（判据来自授权响应，不是流程预设）**

### 序列只有两步的理由

**没有车/结账路径被恢复 → 用这份证据走不完一次购买；更长的序列会在第二步失败。**

### 数字

**套件 1842 → 1850 · 模块 64 → 65 · flow 类型 34 → 35 · store 宿主 23/28 → **24/28****

| 仍 Unknown | |
|---|---|
| 四种身份里哪种进请求 | 猜一个会把错值放进 header |
| 车的端点在哪个宿主 | 未恢复 |
| `purpledotprice` 是什么 | 只剩它一个非支付商未匹配 |

**纪律**：**度量工具最大的价值不是它报的数，是它报出来的清单。**
"""

BLOCKER = """

---

## 343. DicksSportingGoods 补上：24/28；(f) 的表两轮清空两个真缺口

> R919。**改产品代码 +8 用例。** 套件 **1850 通过 / 0 失败 / 0 跳过**。

### 一、九条证据，分三组

```
身份  "DICKS" · "DicksSportingGoods" · "Dicks Sporting Goods" · "dsg-ecomm"
端点  www.dickssportinggoods.com/
      api-search.dickssportinggoods.com/catalog-productdetails/v4/byPartNumber/
      payments.dickssportinggoods.com/prod/api/paygate/v2/authorization
      payments.dickssportinggoods.com/prod/api/paygate/v2/threeDSAuthentication
行为  "_outOfStock(Dicks Sporting Goods"
```

### 二、三件事

1. **身份四种形式**，四个都记成常量 —— **哪个进请求不知道，猜一个会把错值放进 header。**
2. **`_outOfStock` 是闭包名** → 原版对这个店**专门挂了缺货回调** → 按监控建模。
3. **没有车/结账路径被恢复** → 序列只有两步（`FindProduct` · `SubmitPayment`）。

### 三、两个实现决定

- **按零件号查商品**（`byPartNumber/` 是版本段后的整段），不取商品页 —— 那是另一个端点。
- **3DS 有条件**，判据来自**授权响应**而不是流程预设：总是跑第二步会给不需要验证的订单做验证。

### 四、数字

| 度量 | R918 | R919 |
|---|---|---|
| 套件 | 1842 | **1850** |
| 模块 | 64 | **65** |
| flow 类型 | 34 | **35** |
| **store 宿主覆盖** | 23 / 28 | **24 / 28** |

**剩 4 个：`braintreegateway` · `vipps` · `bigcommerce`（支付商子域）· `purpledotprice`（未知）。**

### 五、验证

```
core_coverage.py                     -> store 24/28；两台 DSG 宿主均 matched
test --filter DicksSportingGoodsFlowTests -> 8 通过
metrics_report.py                    -> 1850 通过 / 0 失败
```

### 六、仍然 Unknown

- **四种身份里哪种进请求**：**Unknown** —— 这正是四个都留着的原因。
- **车的端点在哪个宿主**：**Unknown** —— 未恢复，也是序列只有两步的原因。
- **`purpledotprice` 是什么**：**Unknown** —— 4 个未匹配里唯一非支付商。

### 七、教训

**R917 建那张表用了两次修正；R918 与 R919 用它清掉了它列出的两个真缺口。**

**所以那张表的正确用法不是「覆盖率多高」，而是**它列出的未匹配项就是待办清单**。**

**而 7/28 那个数是错的，它列出的 21 个名字里有 2 个是真的 —— 修正判据之后，那 2 个还在。
错的数里可以有对的清单，这是两件事。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R919", BLOCKER)
    ensure(RSTATUS, "R919", BLOCKER)
    ensure(RVERDICT, "第 919 轮", VERDICT)
    ensure(BACKLOG, "R919", BACKLOG_ADD)

    note = (
        "\n## R919 补充 — DicksSportingGoods 补上（改产品代码 +8 用例，套件 1842→1850）\n\n"
        "九条证据：身份 4 种（DICKS / DicksSportingGoods / Dicks Sporting Goods / dsg-ecomm）· "
        "端点 4 条（www / api-search byPartNumber / paygate authorization / threeDSAuthentication）· "
        "行为 1 条（_outOfStock 闭包名 → 缺货回调）。\n\n"
        "改动：DicksSportingGoodsFlow.cs 新建（4 身份 + 3 宿主 + 4 地址 + 2 步骤）· Registry.cs 注册 · 8 用例。\n"
        "序列只有两步：没有车/结账路径被恢复，更长序列会在第二步失败。\n\n"
        "3DS 有条件（判据来自授权响应）；商品按零件号查不取页面。\n\n"
        "数字：套件 1850 · 模块 64→65 · flow 类型 34→35 · store 宿主 23/28 → 24/28。\n"
        "剩 4 个：braintreegateway · vipps · bigcommerce（支付商子域）· purpledotprice（未知）。\n\n"
        "(f) 那张表两轮清空两个真缺口 —— 它的价值不在覆盖率，在于未匹配项就是待办清单。\n\n"
        "下一轮：purpledotprice 是什么（唯一非支付商未匹配）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R919" not in h:
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
             for p, k in ((RBLOCK, "R919"), (RSTATUS, "R919"), (RVERDICT, "第 919 轮"), (BACKLOG, "R919")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R919: Dicks Sporting Goods added, and the coverage table's other genuine gap closes\n\n"
         "R917's table listed two genuine gaps. R918 closed one and this round closes the other. The evidence is richer\n"
         " than the six literals first seen: nine, in three groups. Four identity forms -- DICKS, DicksSportingGoods,\n"
         " Dicks Sporting Goods and dsg-ecomm -- then four endpoints across three hosts, then one behaviour literal.\n\n"
         "All four identities are recorded as constants rather than one being chosen, because which of them appears in a\n"
         " request is unknown and guessing would put a wrong value in a header. dsg-ecomm reads like a channel name and\n"
         " DICKS like a short tag, and neither is established.\n\n"
         "The behaviour literal is the informative one: _outOfStock is a closure name, so the original attaches an\n"
         " out-of-stock callback to this store specifically. That is a monitoring concern rather than a checkout one and\n"
         " is modelled as one.\n\n"
         "The endpoints are a product search by part number and a paygate, with no basket or checkout path recovered at\n"
         " all -- which is why the sequence is two steps. A store with a paygate but no cart call cannot be taken through\n"
         " a purchase from this evidence, and a longer sequence would be steps that fail at the second one. The product\n"
         " lookup reads by part number because that is the endpoint the image names; fetching the page instead would be a\n"
         " different endpoint. And 3-D Secure is conditional on the authorisation's own answer, since always running the\n"
         " second call would authenticate orders that needed no authentication.\n\n"
         "Figures: suite 1842 to 1850, modules 64 to 65, flow types 34 to 35, store host coverage 23 of 28 to 24.\n\n"
         "What this round is worth is not the store. R917 needed two corrections to build the table; R918 and R919 used it\n"
         " to close the two genuine gaps it named. So the table's value is not its percentage but its list -- and of the\n"
         " four hosts still unmatched, three are payment subdomains already judged not to need a flow, which means the\n"
         " table is nearly spent.\n\n"
         "Unknown: which identity form appears in a request; where this store's cart endpoint lives, which is why the\n"
         " sequence stops at two; and what purpledotprice is, the only unmatched host that is not a payment provider.\n\n"
         "The lesson is that a wrong number can carry a right list. Seven of twenty-eight was wrong when it was\n"
         " printed, and two of the twenty-one names it listed were real; after the criterion was corrected, both were\n"
         " still there.\n\n"
         "Product code changed; suite green at 1850."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()