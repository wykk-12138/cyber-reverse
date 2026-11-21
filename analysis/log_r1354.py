"""R1354 record: shipping completes Highsnobiety, proven twice over."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1354 轮：`setShippingAddress`(4992) 补齐 Highsnobiety —— **签名和发送方各说一次，答案一致**

- **重新聚类剩下的 28 个**，得到 8 块。最高价值的一块是 `0x1470fa944`：
  `setShippingAddress`(4992) / `updateMyPaymentWithActions`(401) / `updateShipAddress`(140)。
- **两条独立证据指向同一结论**：
  1. **签名**：`$action: SetCartShippingAddress!` + `$locale` + `$preferredLocale`
     —— 与已落地的 `setBillingAddress`(4989)、`setCustomerEmail` **同形**；
  2. **发送方**：唯一引用点 `0x140B59CF7` 落在 `sub_140B59790` —— **R1339 扫主机时已标为 Highsnobiety 的 shipping 发送方**。
  **长度接近只是巧合的旁证，不是判据**（这是本轮特意写下来的一句）。
- **落码**：`HighsnobietyFlow.SubmitShippingAsync`（action 对象由调用方给，与 billing 同待遇）。
  **至此 Highsnobiety 七步齐全**：cart → email → product → billing → payment → shipping → order。
- **产物**：`mutation setShippingAddress` UTF-16 命中 **1**；尺寸 62,055,232 → **62,074,688**。

### 五要素

- **改了什么**：`RetailFlows.cs`（shipping 步 + 4992 字符常量）；`HighsnobietyFlowTests.cs`（+3 条，共 19）；
  新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`HighsnobietyFlowTests` → **19/19**；`operation_gap.py` → 覆盖 **38/65**（缺 27）；
  `orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 37 → **38**；缺 28 → **27**；套件 +3；产物 +19,456 字节。
- **证据等级**：Observation —— 文档 4992 字符与三个变量、引用点落在 R1339 已标注的 shipping 发送方内、产物命中。
- **还剩什么**：`updateShipAddress`(140)/`updateMyPaymentWithActions`(401)（同块，签名不同）；
  `CartLineItemSet`(1255)/`CreditCard`(2867)；`GetCart`(3520)/`GetCartCookie`(74)/`GetProductInventory`(490)；
  `SignInAsGuest`(453)/`TokenizeCreditCard`(505)/`UpdateContactDetails`(244)/`UpdateCustomerForCart`(382)/
  `UpdateShippingAddress`(2386)；`addToCartByChannel`(2271)；Unknown 六份（已登记）；B 块其余；
  `approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；
  AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1354 轮

- 重新聚类 28 个 → 8 块。`setShippingAddress`(4992) 落地：**签名**（action 对象 + 两个 locale）与**发送方**
  （`0x140B59CF7` → `sub_140B59790`，R1339 已标为 shipping）**两条独立证据一致**。
  **长度接近只是旁证，不是判据。**
- `HighsnobietyFlow.SubmitShippingAsync` 落地 → **该店七步齐全**（cart/email/product/billing/payment/shipping/order）。
- 覆盖 37 → **38/65**，缺 28 → **27**；产物 `mutation setShippingAddress` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1354 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1354 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'setShippingAddress' not in text:
    text += """
## Highsnobiety 的三个地址步（R1350 / R1354）

| 文档 | 长度 | 声明集 |
|---|---|---|
| `setCustomerEmail` | 4986（R1338） | action 对象 + 两个 locale |
| `setBillingAddress` | 4989 | `$action: SetCartBillingAddress!` + 两个 locale |
| `setShippingAddress` | 4992 | `$action: SetCartShippingAddress!` + 两个 locale |

三者同形；`setShippingAddress` 的引用点 `0x140B59CF7` 落在 R1339 已标为 shipping 的发送方 `sub_140B59790` 内。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
