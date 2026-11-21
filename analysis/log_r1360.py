"""R1360 record: Braintree's payments host, and the operation that needed no caller-supplied origin."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1360 轮：`TokenizeCreditCard` 直接写出 **Braintree 支付主机** —— 这一份不需要调用方补 origin

- **五份一窝先探两份**：
  - `TokenizeCreditCard` 的处理器 `sub_140B632B0` 带 **`https://payments.braintree-api.com/graphql`**，
    旁边是 `client`、`clientSdkMetadata`、`creditCard`、`cvv`、`expirationMonth`、`expirationYear`、
    `billingAddress`、`input` 与 **`dropin2`** —— **Braintree 支付 API + Drop-in v2 SDK 标记**。
    **这同时确认了 R1358 的 Braintree 判断，并给了这一份主机。**
  - `SignInAsGuest` 的处理器 `sub_140CFF770` 只有 `accessToken`/`authPayload`/`data` —— **继续留在无主机组**。
- **落码**：`Payments/BraintreeTokenizeCard`（Url / 505 字符文档 / `dropin2` / 八个字段名 / TokenizeAsync），
  接进 `StoreFlow.SubmitPaymentAsync`（`braintree.creditCard` 触发）。
  **卡号不写进源码**（与 R1348 的 storefront 令牌同一条规矩）。
- **一次差点犯的错**：第一版测试里让步骤真的发出去 —— 而端点是 **Braintree 的公网主机**。
  **和 R1352 那次 DNS 是同一类错误**，这次**在运行前就改掉了**：改成只验输入结构与信封。
- **另两处小伤**：`SubmitPaymentAsync` 是**带实现的 async 成员**，不能整体替换（第一次脚本报"未找到基类成员"）；
  插入后局部变量 `card` 与既有作用域冲突（`CS0136`），改名 `braintreeCard`。
- **产物**：`mutation TokenizeCreditCard` 与 `payments.braintree-api.com` **UTF-16 各命中 1**；
  尺寸 61,955,584 → **61,970,944**。（`dropin2` 两编码皆 0 —— 被内联进字符串拼接，按 §4.5 无结论。）

### 五要素

- **改了什么**：新增 `Payments/BraintreeTokenizeCard.cs`、`tests/BraintreeTokenizeCardTests.cs`（3 条）；
  `StoreFlow.SubmitPaymentAsync` 顶部加分支；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`BraintreeTokenizeCardTests|Shortage|BraintreeClientToken` → **12/12**；
  `StoreFlow|Payment` → **95/95**；`operation_gap.py` → 覆盖 **49/65**（缺 16）；`orphan_documents.py` → 0；
  产物两串各命中 1；尺寸见上。
- **数字变化**：覆盖 48 → **49**；缺 17 → **16**；套件 +3；产物 +15,360 字节。
- **证据等级**：Observation —— 处理器里的主机与八个字段名、`dropin2`、文档 505 字符、产物两串命中。
- **还剩什么**：16 个 —— `SignInAsGuest`(453)/`UpdateContactDetails`(244)/`UpdateCustomerForCart`(382)/
  `UpdateShippingAddress`(2386)（同窝，未探）；`CreditCard`(2867)/`getShippingMethods`(531)（无操作名串）；
  `addToCartByChannel`(2271)；`updateShipAddress`(140)/`updateMyPaymentWithActions`(401)；
  五份无主机（`createCartByStore`/`createMyPayment`/`initiateCheckout`/`maintainShippingGroups`/`saveAddress`）；
  两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；AO 三个体；Saucony 六步。
"""

POINTER = """
---

## 第 1360 轮

- **`TokenizeCreditCard`(505) 直接带主机**：`https://payments.braintree-api.com/graphql` + `dropin2`
  （Braintree Drop-in v2）→ 落成 `Payments/BraintreeTokenizeCard`，接进 `SubmitPaymentAsync`。
  **卡号不写进源码。**
- `SignInAsGuest` 处理器只有 `accessToken`/`authPayload` → 继续留在无主机组。
- **差点犯错**：第一版测试会让步骤真发到 Braintree 公网 —— 与 R1352 的 DNS 同类，**运行前改掉**。
- 覆盖 48 → **49/65**，缺 17 → **16**；产物 `mutation TokenizeCreditCard` 与主机串各 UTF-16 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1360 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1360 \u8f6e')
