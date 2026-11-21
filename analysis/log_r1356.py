"""R1356 record: the PayPal order path, found by name and landed with its handler's three outcomes."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1356 轮：`placeOrderWithPaypal`(843) —— **名字指向处理器，处理器给出三种结局**

- **`CreditCard` 先试**：`ida.py str "CreditCard"` 只回元数据串（`CreditCard*CreditCardNetworkType`、`ICreditCards`、
  `DotNetBrowser.Autofill…`），**没有独立的操作名字符串** → 这一份暂缓，**没硬凑**。
- **`placeOrderWithPaypal` 成了**：`0x147113B8C` 的**两个引用点都在 `sub_140B5F250` 里**（与 Highsnobiety 其它发送方同块），
  该函数带：
  ```
  Error submitting order
  Payment Declined
  Your payment could not be processed
  StatusInfo
  PANINI
  ```
  **`PANINI` 是第二次出现**（第一次在 Shop app 加购处理器的 `onepanini` 键里）—— 说明它是本项目内部的标记词。
- **落码**：`HighsnobietyFlow.SubmitPayPalOrderAsync`（843 字符文档 + **三条消息常量** + 按回复映射），
  并在 `SubmitOrderAsync` 里加分支（`highsnobiety.paypalOrder` 触发）—— **该店因此有两条下单路径**。
- **一处工具链坑**：`SubmitOrderAsync` 在同一文件里出现 **7 次**（7 个流程各自重写），
  按裸锚点插入会撞错；改成**先定位 `class HighsnobietyFlow` 再取其后第一个**。记在脚本头。
- **产物**：`query placeOrderWithPaypal` UTF-16 命中 **1**；尺寸 62,088,000 → **62,095,168**。
  （`Payment Declined` 两编码皆 0 —— 常量被内联进 `Equals`，不独立存在，按 §4.5 无结论。）

### 五要素

- **改了什么**：`RetailFlows.cs`（PayPal 下单步 + 三条消息 + SubmitOrder 分支）；`HighsnobietyFlowTests.cs`（+3，共 22）；
  新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`HighsnobietyFlowTests` → **22/22**；`operation_gap.py` → 覆盖 **40/65**（缺 25）；
  `orphan_documents.py` → 0；`audit_document_constants.py` → **41 常量 / 0 问题**；产物命中 1；尺寸见上。
- **数字变化**：覆盖 39 → **40**；缺 26 → **25**；套件 +3；产物 +7,168 字节。
- **证据等级**：Observation —— 操作名两个引用点同在一个函数内、三条消息原文、文档 843 字符与两个变量、产物命中。
  Unknown —— `CreditCard` 的归属（没有独立操作名字符串可跟）。
- **还剩什么**：`CreditCard`(2867)/`GetCart`(3520)/`GetCartCookie`(74)/`GetProductInventory`(490)；
  `SignInAsGuest` 等五份；`addToCartByChannel`(2271)；`updateShipAddress`(140)/`updateMyPaymentWithActions`(401)；
  Unknown 六份（已登记）；B 块其余；`approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；
  `AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1356 轮

- `placeOrderWithPaypal`(843) 落地：操作名 `0x147113B8C` 的**两个引用点同在一个函数** `sub_140B5F250` 内，
  该函数带三条结局消息（`Error submitting order` / `Payment Declined` / `Your payment could not be processed`）
  与 `StatusInfo`、**`PANINI`**（第二次出现，内部标记词）。
- `HighsnobietyFlow.SubmitPayPalOrderAsync` + `SubmitOrderAsync` 分支 → **该店两条下单路径**。
- `CreditCard` 暂缓：**没有独立的操作名字符串**可跟（`ida.py str` 只回元数据）。
- 工具链坑：`SubmitOrderAsync` 同文件出现 **7 次**，锚点必须先在 `class HighsnobietyFlow` 之后定位。
- 覆盖 39 → **40/65**，缺 26 → **25**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1356 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1356 \u8f6e')
