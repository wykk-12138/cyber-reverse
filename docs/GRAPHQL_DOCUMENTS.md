# 镜像里的 GraphQL 文档（由 `python analysis/graphql_documents.py` 生成的口径）

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
