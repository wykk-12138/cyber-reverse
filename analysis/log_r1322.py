"""R1322 record: 81 GraphQL operations in the image, and the payment/order documents landed."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1322 轮：镜像里有 **81** 个 GraphQL 操作/片段——不是四份，是一整套商务 API

- **换了问法就换了尺度**。前四轮都是"猜一个字段名再 grep"，每份文档都是意外。这轮直接列全量：
  以 `mutation` / `query` / `fragment` 开头的串，**81 条**（`analysis/graphql_documents.py`）。
  第一版筛子把 `{` 开头的也算进去，得 206 条 —— 其中大半是 locale JSON 和 RNG 模板的假阳性，
  已在脚本注释里写明为什么改成只认三种操作头。
- **清单里认得出的链路**（长度即规模）：
  `CreateInitialCart` 865 · `addLineItem` 3847 · `addToCartByChannel` 524/2421 · `CartLineItemSet` 1301 ·
  `addBillingAddressToCart` 333 · `addPaymentToCart` 236 · `SubmitOrder` 141 ·
  `addDiscountCode` 3811 · `UpdateShippingAddress` 2556 · `CurrencyConversion` **10996** ·
  `ResolveThreeDsContingency` **10846** 与 **10958**（两份）· `ThreeDsLookUpMutation` 877/905 ·
  `ThreeDsAuthenticateMutation` 837 · `TokenizeCreditCard` 505 · `AddCreditCard` 830 ·
  `OnboardGuestMutation` 3249 · `ApproveOnboardPaymentMutation` 4267 · `SignInAsGuest` 481 ·
  `UpdateContactDetails` 252 · `UpdateCustomerForCart` 406 · `cartApiObjectCreate` 5876。
  **这是一套完整的无头商务 API**（cartApi + 3DS + 引导开户 + 信用卡令牌化），不是某家店的私货。
- **落码**：`addPaymentToCart`（**236**，`0x1470E87CC`）与 `SubmitOrder`（**141**，`0x1470E1E7C`）逐字节进
  `MagentoCart`（`AddPaymentAsync` / `SubmitOrderAsync` / `MagentoOrderResult`），
  并把 `submitOrder(cartToken)` 接进 **`CasioFlow.SubmitOrderAsync` 的分支**——
  有 `casio.cartToken` 走 GraphQL，否则**保留原来 Unzer 那条路自己的拒绝**（测试两条都钉住）。
- **`$version` 的谜没解**：`CreateInitialCart` 返回 `id/estimatedTotal/products/customer`，**没有 version**；
  `addPaymentToCart` 和账单一样**要求** `$version` 并且**返回** version。
  所以 version 只能来自某次 `updateMyCart` 的回复——**第一次调用之前的那一个，仍然没有出处**。
  `cartToken` 同理：`submitOrder` 要它，而没有任何已解出的文档发放它。**两条都记成 Unknown，都不猜。**
- **本节最该记住的一件事**：我在 `CasioFlow` 里为订单**又写了一个 override**，撞 `CS0111` ——
  这个文件里 `SubmitOrderAsync` 有**六份**（六个不同 flow），我的 `where_is` 式检查用字符切片只看前 20000 字符，
  漏掉了后面那份。**这是连续第三轮同一个错**（R1320 加购、R1321 账单、R1322 订单）。
  教训不是"再小心一点"，而是：**检查重复必须按类体大括号配对切，不能按长度截**。

### 五要素

- **改了什么**：新增 `analysis/graphql_documents.py`；`MagentoCart.cs`（两份文档 + `AddPaymentAsync` +
  `SubmitOrderAsync` + `MagentoOrderResult` + 抽出的 `UpdateMyCartAsync`）；
  `RetailFlows.cs`（`CasioFlow.SubmitOrderAsync` 加 cartToken 分支）；`MagentoCartTests.cs`（+5 条）；
  重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter "MagentoCartTests|Casio"` → **51/51**；
  产物搜 `addPaymentToCart` **1**、`submitOrder(cartToken` **1**；
  尺寸 61,328,896 → **61,347,840**；内嵌 `5c0a9d492821 (is HEAD)`。
- **数字变化**：套件 2638 → 见 METRICS 当前值（+5）；产物 +18,944 字节；**新度量：GraphQL 操作 81 个**。
- **证据等级**：Observation —— 81 条清单、五份文档的地址与长度、产物两串命中。
  Unknown —— `$version` 初值、`cartToken` 来源（两者都要抓包）。
- **还剩什么**：3DS 那三份（10846/10958/877/905/837）是**第②优先级**的核心；
  `createCart`/`addLineItem` 链能补出完整的购物车流程；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1322 轮

- **镜像里有 81 个 GraphQL 操作/片段**（`analysis/graphql_documents.py`），是一整套无头商务 API：
  cartApi + 3DS + 引导开户 + 卡令牌化。之前四轮"猜字段名再 grep"只挖到四份，是尺度的错。
- 已落地 `addPaymentToCart`(236) 与 `SubmitOrder`(141)，`submitOrder(cartToken)` 接进 Casio 订单步的分支，
  **Unzer 原路径的拒绝原样保留**。
- `$version` 初值与 `cartToken` 来源**仍无出处**，两条都记 Unknown，不猜。
- **连续第三轮撞 `CS0111`**（加购/账单/订单）：`RetailFlows.cs` 里同名 override 有六份，
  按字符长度切片检查会漏。**检查重复必须按类体大括号配对切。**
"""

DOC_BODY = """# 镜像里的 GraphQL 文档（由 `python analysis/graphql_documents.py` 生成的口径）

> 数据源是 `analysis/ida_strings.txt`，那是**清单抽样**（见 AGENTS §2.7b），
> 所以这里的 **81 条是下界**，不能用来证明"镜像里没有某份文档"。

## 已按字节落地的

| 地址 | 长度 | 名称 | 落在 |
|---|---|---|---|
| `0x1470FD624` | 240 | `addProductsToCart`（字面令牌 `%CART_ID%`/`%QTY%`/`%SKU%`） | `MagentoCart.AddProductsDocument` |
| `0x1470FD4C4` | 32 | `createEmptyCart` | `MagentoCart.CreateEmptyCartDocument` |
| `0x14718FB74` | 61 | `customerCart` | `MagentoCart.CustomerCartDocument` |
| `0x1470E4F94` | 323 | `addBillingAddressToCart`（GraphQL 变量） | `MagentoCart.AddBillingAddressDocument` |
| `0x1470E87CC` | 236 | `addPaymentToCart` | `MagentoCart.AddPaymentDocument` |
| `0x1470E1E7C` | 141 | `SubmitOrder` | `MagentoCart.SubmitOrderDocument` |

## 认出但尚未落地的（按优先级）

| 地址 | 长度 | 名称 | 为什么还没做 |
|---|---|---|---|
| `0x1470E9FA4` | 5407 | `approveMemberPayment` | PayPal/Braintree 支付编排，缺端点 |
| `0x1470D7974` | 10846 | `ResolveThreeDsContingency` | 3DS 核心，需与 `PayPalThreeDs` 对齐后再落 |
| `0x1470DC9BC` | 10958 | `ResolveThreeDsContingency`（第二份） | 与上面差 112 字符，先要判定哪份在用 |
| `0x1470E261C`/`0x1470E2CCC` | 877/905 | `ThreeDsLookUpMutation` | 同上 |
| `0x1470E1FAC` | 837 | `ThreeDsAuthenticateMutation` | 同上 |
| `0x1470CF25C` | 865 | `CreateInitialCart` | 返回 id 但**不含 version** |
| `0x1470E6CDC` | 3847 | `addLineItem` | 需先定 cartApi 的那家店 |
| `0x1470E5234` | 3811 | `addDiscountCode` | 同上 |
| `0x1470D0FB4` | 10996 | `CurrencyConversion` | 同上 |
| `0x1470EF5FC` | 5876 | `cartApiObjectCreate` | 同上 |

## 两个已被文档证实"不在文档里"的量

- **`$version` 的初值**：`CreateInitialCart` 不返回它，`addBillingAddressToCart`/`addPaymentToCart` 要求它并返回它。
  首次调用前的值只能来自抓包。
- **`cartToken`**：`SubmitOrder` 要它，已解出的文档没有任何一份发放它。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1322 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1322 \u8f6e')
io.open(DOC, 'w', encoding='utf-8', newline='').write(DOC_BODY)
print('wrote %s' % DOC)
