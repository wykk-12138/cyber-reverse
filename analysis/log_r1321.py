"""R1321 record: the billing mutation lands, and the 5407-character payment document is identified."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1321 轮：账单地址变更落地，并把那份 5407 字符的支付文档认了出来

- **这一批冻结文档全读出来了**（UTF-16，按对象头长度解）：
  | 地址 | 长度 | 内容 |
  |---|---|---|
  | `0x1470E4F94` | **323** | `mutation addBillingAddressToCart($cartId, $version, $address, $emailAddress)` → `updateMyCart(actions:[setBillingAddress, setCustomerEmail])` 返回 `id/version/isAbleToCheckout` |
  | `0x1470E9FA4` | **5407** | `mutation approveMemberPayment(...)` + `PaymentContingenciesFragment` + `ThreeDomainSecureFields` + `ThreeDSContingencyFragment` |
  | `0x14713DE4C` | **232** | `query addToCart($sku,$qty,$type,$info)`，`quote_id: "1"`（**另一家店**，Magento 1 形态） |
  | `0x14713E034` | **216** | `query buynow { buynow(item:{sku:"", qty:1, quote_id:"1", type:"Simple"}) }` |
- **落码（已接线，可达）**：`MagentoCart.AddBillingAddressDocument`（323 逐字节）+ `SetBillingAsync`，
  接进 `CasioFlow.SubmitBillingAsync`。**与加购文档的区别要记住**：加购用**字面替换令牌**，
  账单用 **GraphQL 变量**——两份填法不同，测试都钉住。
- **一个不肯编的数字**：账单变更声明 `$version: Long!`，而**加购的回复里没有 version**。
  所以这一版**从 `casio.cartVersion` 取，取不到就明说缺哪个变量**，而不是猜 0 或 1 ——
  猜出来的值会被店铺校验拒绝，而且会把"不知道"伪装成"知道"。测试里有一条专门断言**一个请求都不发**。
- **5100 字那份是什么，现在说得清了**：`approveMemberPayment` + `fundingOption`/`billingToken`/
  `autoReturnToMerchant`/`enablePaymentDataTransfer`/`contingencyContext`/`jwtSpecification` ——
  这是 **PayPal（Braintree 系）的支付编排 GraphQL**，不是 Magento。
  **R1312 那个死路里解出的 `jwtIssuer`/`jwtOrgUnitId`/`contingencyContext` 正是这份文档的字段** ——
  那轮找错了方向（我以为在找 Casio 的签名），其实它属于支付编排层。**这就是那条死路的答案。**
- **没有落它，是有意的**：它需要一个支付步骤去接；现在没有已证实的端点，硬塞一个类型会被 AOT 裁掉
  （R1310 的教训）。它先以**证据形式**留在 `analysis/.magento_cart_docs.json`，等有了端点再接。

### 五要素

- **改了什么**：`MagentoCart.cs`（账单文档 + `SetBillingAsync` + `MagentoBillingResult` + 布尔归一化）；
  `RetailFlows.cs`（`CasioFlow.SubmitBillingAsync`，新建、先查过 `where_is` 确认 Casio 没有此覆盖）；
  `MagentoCartTests.cs`（+3 条）；`read_magento_cart.py` 扩到五个文档；NativeAOT 重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter "MagentoCartTests|Casio"` → **45/45**；
  产物搜 `addBillingAddressToCart` **1**、`isAbleToCheckout` **1**、`updateMyCart` **1**；
  尺寸 61,314,560 → **61,328,896**；内嵌 `58b4eba3d5de (is HEAD)`。
- **数字变化**：套件 2635 → 见 METRICS 当前值（+3）；产物 +14,336 字节。
- **证据等级**：Observation —— 五份文档的地址与长度、字段名、产物三串命中。
  Inference —— 账单走 `updateMyCart` 就是 Casio 的结账面（文档是 Magento 通用 API，无字面量把它钉到这家店）。
  Unknown —— `$version` 的初值从哪来（需抓包）。
- **还剩什么**：`approveMemberPayment`（需端点）、`addToCart(query)`/`buynow`（另一家店）、
  AO 三个 checkout 体、Saucony 六步路径。
"""

POINTER = """
---

## 第 1321 轮

- 五份冻结文档全部解出：账单 323、支付编排 **5407**、`addToCart(query)` 232、`buynow` 216。
- 账单变更**已落地并接线**（`CasioFlow.SubmitBillingAsync`），加购用字面令牌、账单用 GraphQL 变量，两套填法都钉住。
- **不肯编 `$version`**：加购回复里没有 version，取不到就明说缺哪个变量，**一个请求都不发**。
- **5407 字那份是 PayPal/Braintree 支付编排**（`approveMemberPayment`/`fundingOption`/`contingencyContext`/`jwtSpecification`）——
  **R1312 那条死路解出的 `jwtIssuer`/`jwtOrgUnitId` 就是这份文档的字段**，答案在这里。
- 它**没有落地**：没有已证实的端点，硬塞会被 AOT 裁掉。等端点。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1321 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1321 \u8f6e')
