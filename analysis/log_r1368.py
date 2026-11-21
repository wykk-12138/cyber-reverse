"""R1368 record: CreditCard lands on a relative finalize path; two earlier conclusions corrected."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1368 轮：`CreditCard` 落地；**同时推翻 R1358 的一条错误结论**

- **先纠错**：R1358 说 `getShippingMethods` "没有独立操作名字符串" —— **错了**。
  它就在 **`0x14703FA94`**，`CreditCard` 在 **`0x146BA9704`**。
  **当时 `ida.py str --limit 8` 先返回八个 PascalCase 闭包名就停了** ——
  **一次被截断的搜索不是"不存在"的证据**。这条写进 VERDICT，也写进 ASYNC_TAIL 的告诫段落。
- **`CreditCard`(2867) 两个处理器**：
  - `sub_140AAE300`：**`api/checkout/v1/orders/` + 订单号 + `/finalize`**
    （`cardNumber`/`cardCvv`/`cardExpiryMonth`/`cardExpiryYear`/`cardName`、标签 `Submit order`）
    —— **相对路径，所以 origin 由调用方给，订单号是路径段而不是变量**；
  - `sub_140B29DA7`：**`https://www.nike.com/nl/checkout/confirmation?cid=`** + `Submit payment` + `SHIP`/`ASTLA`
    —— **Nike 变体**，归 Nike 自己那些步骤，**只记不并**。
- **`getShippingMethods`(531) 两个处理器**：一个只读 `carrier_code`/`carrier_title`/`method_code`/`method_title`
  （Magento 费率形状），另一个带 **`onepanini`/`Panini`** 与 `city`/`countryId`/`postcode` —— **又是 PANINI 族**。
- **落码**：`Flows/CheckoutCreditCard`（文档 + 路径前后缀 + 五个卡字段 + `UrlFor` + `SubmitAsync`），
  接进 `StoreFlow.SubmitCardAsync`（`checkout.origin` + `checkout.orderId` 触发，**卡字段全部取自会话**）。
- **产物**：`api/checkout/v1/orders/` UTF-16 命中 **1**；尺寸 61,993,984 → **61,997,568**。

### 五要素

- **改了什么**：新增 `Flows/CheckoutCreditCard.cs`、`tests/CheckoutCreditCardTests.cs`（3 条）；
  `StoreFlow.SubmitCardAsync` 加分支；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`CheckoutCreditCardTests` → **3/3**；`StoreFlow|Shortage` → **25/25**；
  `operation_gap.py` → 覆盖 **59/65**（缺 6）；`orphan_documents.py` → 0；产物 ASCII 命中 1；尺寸见上。
- **数字变化**：覆盖 58 → **59**；缺 7 → **6**；套件 +3；产物 +16,896 字节。
- **证据等级**：Observation —— 两个处理器各自的路径与字段、Nike 变体、`getShippingMethods` 的两个处理器、产物命中。
  Correction —— **R1358 的"无操作名字符串"是被截断的搜索造成的误判**。
- **还剩什么**：6 条 —— `getShippingMethods`(531)（两处理器都无主机）、`createMyPayment`(493)（Cybersource）、
  两方言、AO 三个体、Saucony 六步、`/cartApi/checkout`、`AddressInput`、浏览器侧结账面。
"""

POINTER = """
---

## 第 1368 轮

- **R1358 一条结论被推翻**：`getShippingMethods` **确有**独立操作名串（`0x14703FA94`），
  `CreditCard` 在 `0x146BA9704` —— 当时 `--limit 8` 被 PascalCase 闭包名占满，**把截断读成了不存在**。
- **`CreditCard`(2867) 落地**：相对路径 `api/checkout/v1/orders/<订单号>/finalize` + 五个卡字段
  → `Flows/CheckoutCreditCard`，接进 `SubmitCardAsync`。**另一处理器是 Nike NL 变体，只记不并。**
- `getShippingMethods` 两处理器：一个 Magento 费率字段，一个 **PANINI 族**。均无主机 → 仍需抓包。
- 覆盖 58 → **59/65**，缺 7 → **6**；产物 `api/checkout/v1/orders/` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1368 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1368 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if '被截断的搜索' not in text:
    text += """
---

## 八、一条方法论纠正（R1368）

R1358 曾把 `CreditCard` 与 `getShippingMethods` 判为"没有独立操作名字符串"。**两者都有**：

| 操作 | 独立串地址 | 两个处理器 |
|---|---|---|
| `CreditCard` | `0x146BA9704` | `api/checkout/v1/orders/<id>/finalize`（已落地）/ Nike NL 变体 |
| `getShippingMethods` | `0x14703FA94` | Magento 费率字段 / PANINI 族 |

**错因**：`ida.py str <名> --limit 8` 先返回八个 PascalCase 闭包名就截断了。

> **一次被截断的搜索不是"不存在"的证据。** 反向结论必须用不截断的检索，或换地址直查。

`getShippingMethods` 仍未落地：两个处理器**都没有主机**，需要抓包。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS got the correction section')
