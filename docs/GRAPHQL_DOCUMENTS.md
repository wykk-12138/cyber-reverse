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
| `0x1470E9FA4` | 5407 | `approveMemberPayment` | **R1335 已落地**：`PayPalPartnerApprove`，端点 `https://www.paypal.com/graphql/approveMemberPayment`（路径式）|
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

**R1334 补充**：拼接规则已读完 —— `https://` + `host 的 www 换成 themeapis`（无 `www.` 时加前缀）+ `/cartApi/checkout`，
已落成 `MagentoCart.CartApiEndpointFor` / `ThemeApisHost` / `ResolveEndpoint`，六个方法开头统一归一化。
**今天所有调用方传完整 URL，行为不变**；仍待定的是**哪家店**用这条路径。

## 五份文档的真实去向（R1337，读发送方所得）

| 文档 | 发送方拼出的目标 | 关键变量 |
|---|---|---|
| `SubmitOrder`(141) | `https://` + host + `/graphql` | `cartToken`、`operationName`、`query`、`variables` |
| `addLineItem`(3847) | `https://tm-api-eu.highsnobiety.com/` | `sku`、`locale`、`country`、`action`（`Add to cart`） |
| `addDiscountCode`(3811) | `https://tm-api-eu.highsnobiety.com/` | `code`、`locale` |
| `cartApiObjectCreate`(5876) | Shopify Storefront `api/2025-04/graphql.json` | `gid://shopify/ProductVariant/`、`customerAccessToken`、`include*` |
| `createEmptyCart`(32) | 无 URL 字面量 —— 端点由调用方传 | — |

**`/cartApi/checkout` 不在这张表里。** 它的发送方用的是 `cartType`/`lineItems`/`locationId`/`sourceSystem`
（取值 `Retail`/`Shopify`），与上表任何一份都不重合 —— 所以 R1334 把那条路径挂到 `MagentoCart` 上是错的，已撤回。

## Highsnobiety 的八个发送方（R1339）

主机 `https://tm-api-eu.highsnobiety.com/` 在 `.text` 里只有 **8 个引用点**，8 个函数即整店 API 面。
**注意**：这些引用指向**字符地址** `0x147089690`，不是对象头 `-12`；扫对象头得 0 site。

| 函数 | 标签 | 操作名 | 变量 |
|---|---|---|---|
| `0x140B56880` | Add to cart | `addLineItem` | `action`、`country`、`locale` |
| `0x140B56CC0` | Create payment | `createCheckoutPayment` | `storefront`、`action`?（`App`） |
| `0x140B57020` | Find product | `fetchProduct` | `slug`、`locale`、`preferredLocale`、`fallbackLocale`、`country` |
| `0x140B574F0` | Process order | `fetchOrderConfirmation` | `stripePaymentIntentId`、`locale`、`preferredLocale` |
| `0x140B57EB0` | Submit billing | 待读 | `action`、`additionalAddressInfo`、`address`、`city`、`country`、`firstName`、`lastName`、`phone` |
| `0x140B585B0` | — | `addDiscountCode` | `code`、`locale` |
| `0x140B58920` | Submit email | `setCustomerEmail` | `action`、`locale`、`preferredLocale` |
| `0x140B59790` | Submit shipping | 待读 | 同 billing |

`fetchProduct` = **5718** 字符（`0x1471407C4`），`setCustomerEmail` = **4986**（`0x1470F8234`），
`addLineItem` = **3435**（`0x1470E6CDC`），`addDiscountCode` = **3399**（`0x1470E5234`）。

## 操作清单（R1341）：镜像 65 个，复刻件覆盖 19 个

**数法**：走区域 `0x1470C0000..0x147150000`，4 字节步长找冻结串头（`MT=0x144DB6A40` + 长度），
读出所有以 `mutation `/`query ` 开头的对象。结果存 `analysis/.operations_in_image.json`。
**不要用 `ida.py str "mutation "`** —— 它只报 7 个，长的文档不在它的"字符串"集合里。

**方言对**：`approveMemberPayment` 在 `0x1470E9FA4`（5407，R1335 已用）与 `0x1470EC9FC`（5620）各有一份，
**选用条件未定**。

**待取清单**（`python analysis/operation_gap.py` 输出全表，按长度降序）：
**`ProductDetails`(26206) 已落地（R1342）：属于 `https://server.shop.app/graphql`，见 `ShopAppProduct`**、**`PayWithQuery`(12561) 与 `ShipToQuery`(2031) 已落地（R1343）：`PayPalCheckoutQueries`**、**`Product`(10620) 已落地（R1345）：`StorefrontApiProduct`，与 `AddItemToCart`/`CreateInitialCart`/`CheckoutCart` 同族，共用相对路径 `api/graphql`，**都不带主机**（origin 由调用方给）**、`ShopProductSearch`(6537)、
`cartApiObjectCreate`(5876)、`setShippingAddress`(4992)、`setBillingAddress`(4989)、`CheckoutCart`(4102)、
`GetCart`(3520)、`getCart`(3234)、`getPaymentdMethods`(3067)、`CreditCard`(2867)、`UpdateShippingAddress`(2386) …

## `api/graphql` 族（R1345–R1346）：五份文档，一个相对路径，无主机

| 操作 | 长度 | 地址 | 文档声明 | 发送方填 |
|---|---|---|---|---|
| `AddItemToCart` | 2108 | 0x1470CB3F4 | `$input` | `id`、`input`、`productId` |
| `CreateInitialCart` | 865 | 0x1470CF25C | 无 | 无 |
| `Product` | 10620 | 0x147127B44 | `id`、`isDraft`、`variationId`、`src` | `id`、`variationId` |
| `CheckoutCart` | 4102 | 0x14711CF9C | `$id` | `id` |
| `getSession` | 133 | 0x147146994 | 无 | 无 |

五个发送方（`0x140E1B1D0` / `0x140E1B700` / `0x140E1BAB0` / `0x140E1BF40` / `0x140E1C390`）**都不带主机**，
都拼相对路径 `api/graphql`。**origin 必须由调用方给** —— 相对路径配一个编出来的主机就是把真实请求发到真实服务器。
实现见 `Flows/StorefrontApiQueries.cs`。

## A 块 = Shopify Storefront（R1348）

发送方 `sub_140D1B380`（2258 字节）带 `api/2025-04/graphql.json`、`buyerIdentity`、`customerAccessToken`、
`gid://shopify/ProductVariant/` 与五个 `include*` 标志 —— 与复刻件 `ShopifyGraphQl.Endpoint` 拼的路径相同。

**该发送方里写死了一个 storefront 访问令牌**（`e927ea99…`）。**没有抄进源码**：令牌由调用方提供。

已落地：`cartApiObjectCreate`(5876) → `Flows/ShopifyCartCreate.cs`。
A 块其余 14 个操作（`createCart`、`setBillingAddress`、`removeLineItemFromCart` …）**同属这一族**，待接。

## A 块的三分（R1349）

| 文档 | 声明集 | 归属 |
|---|---|---|
| `cartApiObjectCreate`(5876) | `$input` + 六个 include + `country` + `metafieldsIdentifiers` | **Shopify Storefront** |
| `createCart`(1622) | `$lines`/`$buyerIdentity`/`$attributes`/`$country`/`$language` | **Shopify Storefront** |
| `removeLineItemFromCart`(1553) | `$cartId`/`$lineItemId`/`$version`/`$quantity`/`$locale` | **Shopify Storefront** |
| `setBillingAddress`(4989) | `$action: SetCartBillingAddress!`/`$locale`/`$preferredLocale` | **Highsnobiety 那一族** |
| `createCheckout`(720) | `$variantId`/`$location`/`$attributes`/`$recaptchaToken` | 未定（第三种签名） |

**地址聚类只是线索；变量签名才是证据。**

## product-drops（R1351）

`getProductDetails`(499 @0x1470F43C4) 的发送方 `sub_140C81880` 拼
`apps/product-drops?kind=mutation&operation=getProductDetails` —— **操作名在查询串里**（与 PayPal 合作方族同形），
文档是 **mutation**、`$handle: String`（**可空**）。实现在 `Flows/ShopifyProductDrops.cs`。

同批的 `saveAddress`、`maintainShippingGroups` **既无主机也无路径**，与 `getCart` 同处不可归属清单。

## storefront 的两个 API 版本（R1352）

| 操作 | 版本 | 地址 |
|---|---|---|
| `cartCreate`(91) | **2021-10** | 0x1470F23FC |
| `customerAccessTokenCreate`(250) | 2025-04 | 0x1470F41B4 |
| `cartApiObjectCreate` / `createCart` / `removeLineItemFromCart` | 2025-04 | — |

**版本随操作走，不随类走。**

另外：`checkoutAsGuest`(148) 的发送方直接写出 **`https://www.on.com/ko-kr/graphql`**（On Running 韩语店面），
`createCheckout`(720) 走 `apps/product-drops?kind=mutation&operation=createCheckout`。

## 按哈希投递的一族（R1357）

`sub_14088BB80`（`GetCartCookie` 名字的引用者）带：

```
x-graphql-hash          83c4b10c99a6f6c89abf7e84f83d5dc6360f8627eb2b70c7eb4b12590c6f1950
                        b613893783ae3da73f38b5f93a9a59ccbaa7f131a209cac92634a93d06f06866
x-graphql-query-name    x-header-id    Getting session    StatusInfo
```

| 操作 | 文档长度 | 地址 |
|---|---|---|
| `GetCartCookie` | 74 | 0x147120B5C |
| `GetProductInventory` | 490 | 0x147120C0C |
| `GetCart` | 3520 | 0x14711EFC4 |

**两个哈希与三个操作的配对未成立** —— 实现里哈希一律由调用方给。见 `Flows/GraphQlHashQueries.cs`。

## 无主机的会话族（R1359）

处理器 `sub_140E5B940` / `sub_140E5B570` 只有 `application/json` 与信封键，与 `getCart` 状态机同块，**主机在上层**。

| 操作 | 长度 | 声明集 |
|---|---|---|
| `getCustomerInformation` | 197 | 无 |
| `getPaymentdMethods` | 3067 | 无（保留镜像错拼） |
| `item` | 67 | 无 |
| `getCart` | 3234 | `$key`、`$locale` |

实现在 `Flows/StoreSessionQueries.cs`；origin 由调用方给。

## 一条操作、两种传输（R1361）

`UpdateShippingAddress` 的操作名有两个处理器：

| 处理器 | 路径 | 平台 |
|---|---|---|
| `sub_140E1DD80` | `api/graphql` | 已实现的相对路径族 |
| `sub_14098C830` | `/scapi/ShopperBaskets/updateShippingAddressForShipment` | **Salesforce Commerce API** |

只实现前者；SCAPI 那条**只记不实现**（复刻件没有其它商业平台面）。

## 归属靠处理器变量（R1362）

| 操作 | 长度 | 处理器特征 | 归入 |
|---|---|---|---|
| `UpdateCustomerForCart` | 382 | `api/graphql` + `basketId`/`email`/`input` | `StorefrontApiQueries`（第六份） |
| `addToCartByChannel` | 2271 | `key`/`locale`/`cartId`/`productId`/`quantity`，无主机 | `StoreSessionQueries` |

`addToCartByChannel` 文档声明 `$cartId`/`$locale`/`$productId`/`$quantity`/`$version` 五个，
发送方另提 `key`/`country`/`address` —— **以文档为准**。
