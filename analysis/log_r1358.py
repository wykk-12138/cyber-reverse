"""R1358 record: Braintree under a PANINI-named module, and one more name that cannot be followed."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
UNATTR = 'docs/UNATTRIBUTED_OPERATIONS.md'

ROUND = """
---

## 第 1358 轮：`generateClientToken` 是 **Braintree**；`getShippingMethods` 没有操作名可跟

- **`generateClientToken`(188)**：操作名 `0x14703DADC` 有两个处理器 ——
  `sub_140B5EDB0` 带 `authorizationFingerprint`、`clientToken`、**`Error getting token`**、`StatusInfo`；
  `sub_140B61090` 带 **`onepanini`**。
  **`authorizationFingerprint` 是 Braintree 的字段，`clientToken` 是它的返回** ——
  所以这套支付栈底下是 **Braintree**，外层挂着一个以 PANINI 命名的模块
  （同一个标记已出现在 Shop app 加购处理器与 `placeOrderWithPaypal` 的 `PANINI` 里）。
- **落码**：`Payments/BraintreeClientToken`（188 字符文档 + 两个字段名 + `Error getting token` + FetchAsync），
  接进 `StoreFlow.GetSessionAsync`（`braintree.endpoint` 触发）。
  **失败用处理器自己的话**，不是原始错误。
- **`getShippingMethods` 跟不上**：字符串表里只有别处的闭包名（`GetShippingMethods` PascalCase），
  **没有独立的小写操作名字符串**。与 `CreditCard` 同组 —— **记下来，不硬凑**。
- **一处自伤**：写测试文件时手滑把末尾截断成 `TheReplyCarries(clientTokensit()`，
  编译前自己发现并整份重写 —— 这类错误**编译会报，但更该在写的时候就不发生**。
- **产物**：`query generateClientToken` UTF-16 命中 **1**；尺寸 61,917,184 → **61,925,888**。
  （`Error getting token` 两编码皆 0 —— 常量被内联，按 §4.5 无结论。）

### 五要素

- **改了什么**：新增 `Payments/BraintreeClientToken.cs`、`tests/BraintreeClientTokenTests.cs`（5 条）；
  `StoreFlow.GetSessionAsync` 加分支；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`BraintreeClientTokenTests` → **5/5**；`StoreFlow|ShopifyGraphQl` → **33/33**；
  `operation_gap.py` → 覆盖 **44/65**（缺 21）；`orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 43 → **44**；缺 22 → **21**；套件 +5；产物 +8,704 字节。
- **证据等级**：Observation —— 两个处理器的字面量、`authorizationFingerprint`/`clientToken` 的归属、
  文档 188 字符与 `$type`、产物命中。
  Unknown —— `getShippingMethods`/`CreditCard` 的归属（无独立操作名串）。
- **还剩什么**：21 个 —— `CreditCard`(2867)、`getShippingMethods`(531)（**均无操作名串**）、
  `getPaymentdMethods`(3067)/`getCustomerInformation`(197)/`item`(67)/`getCart`(3234)（B 块未探）、
  `SignInAsGuest` 等五份、`addToCartByChannel`(2271)、`updateShipAddress`(140)/`updateMyPaymentWithActions`(401)、
  Unknown 六份、两方言、浏览器侧结账面、`/cartApi/checkout` 归属、`AddressInput`、AO 三个体、Saucony 六步。
"""

POINTER = """
---

## 第 1358 轮

- **`generateClientToken`(188) 是 Braintree**：处理器带 `authorizationFingerprint`/`clientToken`/`Error getting token`；
  另一个处理带 `onepanini`（与 Shop app 加购、PayPal 下单的 `PANINI` 同源）。
  落成 `Payments/BraintreeClientToken`，接进 `StoreStep.GetSessionAsync`。
- **`getShippingMethods` 无独立操作名字符串**（只有别处的 PascalCase 闭包名）→ 与 `CreditCard` 同组，**不硬凑**。
- 覆盖 43 → **44/65**，缺 22 → **21**；产物 `query generateClientToken` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1358 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1358 \u8f6e')

text = io.open(UNATTR, encoding='utf-8').read()
if 'getShippingMethods' not in text:
    text += """
## 无独立操作名字符串的（R1358）

| 操作 | 长度 | 情况 |
|---|---|---|
| `CreditCard` | 2867 | `ida.py str "CreditCard"` 只回元数据（`CreditCard*CreditCardNetworkType`、`ICreditCards`） |
| `getShippingMethods` | 531 | 只回别处的 PascalCase 闭包名 |

**这两份不能靠"名字 → 处理器"定位**，需要别的入口（调用点或运行期）。
"""
    io.open(UNATTR, 'w', encoding='utf-8', newline='').write(text)
    print('UNATTRIBUTED_OPERATIONS.md updated')
