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
| `0x1470D7974` | **10262** | `ResolveThreeDsContingency`（无 provider 字段的方言） | **R1323 已落地**：`ResolveDocumentWithoutProviderFields` |
| `0x1470DC9BC` | **10370** | `ResolveThreeDsContingency`（带 provider 字段） | 早已在 `ResolveDocument`（R1149），R1323 确认逐字节一致 |
| `0x1470E261C`/`0x1470E2CCC` | **844/871** | `ThreeDsLookUpMutation` 方言对 | **R1324 已落地**：`LookUpDocumentWithoutProviderFields` / `LookUpDocument` |
| `0x1470E1FAC` | **813** | `ThreeDsAuthenticateMutation`（只有一份，不含 provider 字段） | 早已在 `AuthenticateDocument`，R1324 确认逐字节一致 |
| `0x1470CF25C` | 865 | `CreateInitialCart` | 返回 id 但**不含 version** |
| `0x1470E6CDC` | 3847 | `addLineItem` | 需先定 cartApi 的那家店 |
| `0x1470E5234` | 3811 | `addDiscountCode` | 同上 |
| `0x1470D0FB4` | 10996 | `CurrencyConversion` | 同上 |
| `0x1470EF5FC` | 5876 | `cartApiObjectCreate` | 同上 |

## 两个已被文档证实"不在文档里"的量

- **`$version` 的初值**：`CreateInitialCart` 不返回它，`addBillingAddressToCart`/`addPaymentToCart` 要求它并返回它。
  首次调用前的值只能来自抓包。
- **`cartToken`**：`SubmitOrder` 要它，已解出的文档没有任何一份发放它。

## 方言开关（R1325）

两份文档**各自冻结完整**，镜像在"选方法"而不是"选片段"：`sub_14110FDB0`(14458) 发不带
`authenticationProvider` 的那份，`sub_141113680`(15615) 发带的那份。两者的 MoveNext 桩
（`0x14258A4A0` / `0x14258A600`）**相距 0x160**，是同一个类的两个异步方法。

**镜像据什么条件选，仍未解。** 复刻件因此提供运行时可切：
`paypal3ds.providerFields`（缺省 `true` = 带 `authenticationProvider` 的那份），由
`PayPalThreeDs.ProviderFieldsRequested` 读取、`GqlAsync` 使用。一次抓包即可定案。

## 已解码、尚无归宿（R1326）

| 地址 | 长度 | 名称 | 状态 |
|---|---|---|---|
| `0x1470D611C` | 3104 | `OnboardGuestMutation` | **R1328 已落地**：`WarhammerQueries.OnboardGuestMutation`，接在审批之前 |
| `0x1470CC8CC` | 4040 | `ApproveOnboardPaymentMutation` | **已修复**：`WarhammerQueries` 里那份曾被截断标记污染 |
| `0x1470D0FB4` | 10406 | `CurrencyConversion` | 已解码，同上 |

`OnboardGuestMutation` 与 `CurrencyConversion` **故意没有落进 `src`**：没有调用点的类型会被 AOT 裁掉（R1310 的教训）。

## 这一族文档发到哪里（R1333）

`createCart` / `updateMyCart` / `addPaymentToCart` / `SubmitOrder` / `OnboardGuestMutation` /
`CurrencyConversion` / `approveMemberPayment` 属于**店铺侧的购物车 API**，不是 PayPal 的挑战流。

- 路径字面量：`/cartApi/checkout`（`0x146AB27FC`），**`.text` 里只有一个引用点**（`sub_140C32160`，1072 字节）。
- 拼法（反编译原样）：`"https://" + (主机标签 www|themeapis) + "/cartApi/checkout"`；
  另有 `https://themeapis.`（`0x14708885C`）与 `themeapis`（`0x14716CAE4`）。
- 同函数的字段名：`cartType`、`couponReferences`、`lineItems`、`locationId`、`sourceSystem`；取值 `Retail`、`Shopify`。

**因此**：`MagentoCart` 里那些方法接收的 `endpoint` 由调用方传入（当前是 `<origin> + /graphql`），
这条默认值**存疑**，需要用一次抓包或一个明确的店来定，不要凭形状改。
