## 11. Nike —— 结账流程对等度（IDA 提取，第 48 轮）

### 原版的 14 步

`<Method>d__N` 是 C# async 状态机的编译产物；NativeAOT 保留了名字，所以方法表可以从
字符串缓存直接读出（`api_*` 那些是 `sub_140xxxxxx`，但名字在旁边）：

```
<Authorize>b__42_1        <GetAccessToken>b__43_1
<CreateBasket>d__46       <SubmitCustomer>d__48       <ValidateAddress>d__49
<SubmitShippingAddress>d__50   <GetShippingMethods>d__51   <SubmitShippingMethod>d__52
<SubmitBillingAddress>d__53    <BeginCheckout>d__54        <CheckInventory>d__55
<GetShopperIp>d__56       <GetPaymentMethods>d__57     <SubmitOrder>d__58
```

**14 步，两个字段承载状态**：`_checkoutId`、`_countryCode`。

### 只有 5 个 URL

```
POST https://api.nike.com/buy/checkout_previews/v3/
POST https://api.nike.com/buy/checkout_previews_jobs/v3/
POST https://api.nike.com/buy/checkouts/v3/
POST https://api.nike.com/buy/checkouts_jobs/v3/
GET  https://api.nike.com/deliver/available_gtins/v3
```

**14 步对 5 个 URL** —— 说明其中大部分是对**同一个 checkout 资源**的逐步写入
（`/buy/checkouts/v3/{checkoutId}/...`），不是 14 个独立端点。

`_checkoutId` 的存在支持这个读法：先创建一个 checkout，之后每一步往它上面追加。

### replica 现在是什么

`NikeFlow` 有 17 个 override，但**和那 14 步不是同一组**：

| 原版 | replica | 判定 |
|---|---|---|
| `<GetAccessToken>` | — | **缺** |
| `<SubmitCustomer>` | — | **缺** |
| `<ValidateAddress>` | — | **缺** |
| `<GetShippingMethods>` | — | **缺** |
| `<SubmitShippingMethod>` | — | **缺** |
| `<SubmitBillingAddress>` | — | **缺** |
| `<GetShopperIp>` | — | **缺** |
| `<GetPaymentMethods>` | — | **缺** |
| `<CreateBasket>` | `CreateCartAsync` | 名字不同，大致对应 |
| `<SubmitShippingAddress>` | `SubmitShippingAsync` | 部分（少了 method 那一步） |
| `<BeginCheckout>` | `GetCheckoutAsync` | 部分 |
| `<CheckInventory>` | `ScrapeVariantAvailabilityAsync` | 部分（replica 走 product_feed 不是 deliver/available_gtins） |
| `<SubmitOrder>` | `SubmitOrderAsync` | ✅ |
| `<Authorize>` | `GetSessionAsync` | 部分 |

**replica 多出来的**：`GetScript` / `GenerateSensor` / `SubmitSensor`（Kasada 三步，
原版在 `KasadaHandler` 里不在 flow 里）、`CheckPriceLimit`、`EditLine`、`GetCart`。

**所以「函数数量」接近（17 vs 14），「函数内容」不对等：缺 8 步，多 6 步。**
用户的三条标准里，第一条（数量）形式上接近，第二条（每步功能相等）**在这一层不成立**。

### 路径族也不对

| replica | 原版 |
|---|---|
| `api.nike.com/buy/carts/v2/{Marketplace}/Nike/SNKRS?format=simplified` | — |
| `api.nike.com/buy/orders/v2/US/{id}/delivery` | — |
| `api.nike.com/buy/orders/v2/US/{id}/initiatePayment` | — |
| `api.nike.com/buy/orders/v2/US/{id}/payment` | — |
| `api.nike.com/buy/orders/v2/US/{id}/submit` | — |
| — | `api.nike.com/buy/checkouts/v3/` |
| — | `api.nike.com/buy/checkout_previews/v3/` |
| — | `api.nike.com/deliver/available_gtins/v3` |

**`buy/orders/v2` 和 `buy/carts/v2` 在原版字符串表里一条都没有。** `snkrs` 也没有。

`buy/orders/v2` 是 Nike 真实存在过的 API（SNKRS 早期用它），所以 replica 不是凭空编的——
**但原版不走那条。** 这两件事可以同时为真，而「原版走哪条」才是 1:1 的判据。

### 要补齐需要什么

| 缺的 | 需要 |
|---|---|
| 8 步的 URL 形状 | `/buy/checkouts/v3/{id}/<step>` 的**段名**——得看反编译，字符串层只有基址 |
| 每步的 payload | 同上 |
| `GetShopperIp` 的来源 | 它要一个 shopper IP，可能来自代理出口——字符串层看不出来 |
| `_jobs` 的轮询间隔 | 控制流，需要 xref |

**这些都在 `auto_analysis_ready` 之后才能拿到**（现在 `false`，211,806 行没建完 xref）。

### 但字段名拿到了（第 49 轮）

字符串缓存里还有一整组私有字段。它们不是端点，是**每一步写进哪个变量**——
这比基址细一层，因为它说明每步产出什么：

| 步骤 | 私有字段 |
|---|---|
| `Authorize` / `GetAccessToken` | `_accessToken` `_refreshToken` `_accessTokenExpiry` `_identificationSignature` |
| `CreateBasket` | `_checkoutId` `_checkoutUrl` `_checkoutKey` `_checkoutQuery` |
| `SubmitShippingAddress` | `_shippingUuid` `_shippingUUID`（两个拼法都在，说明改过名） |
| `GetShippingMethods` | `_shippingRate` `_shippingPrice` `_shippingTotal` `_preloadRateSuffix` `_preloadShippingTotal` `_shippingChanged` |
| `SubmitShippingMethod` | `_shippingMethod` `_shippingCarrierCode` `_shippingMethodCode` `_urlSku` |
| `GetPaymentMethods` | `_paymentToken` `_paymentGateway` `_paymentGatewayName` `_paymentApprovalId` `_paymentFlexibilityTemplate` |
| `SubmitOrder` | `_orderToken` `_unverifiedPrice` `_paymentUri` `_paymentUrl` `_paymentId` |

**三件事由此确定**：

1. **`_identificationSignature` 存在** —— Nike 的请求要签名，不是裸 JSON。
   这是 8 步里最难补的一环：不知道签名算法，其余 7 步全白做。
2. **`_shippingCarrierCode` + `_shippingMethodCode` 是两个独立字段** ——
   `GetShippingMethods` 的响应里要各取一个，不是取一个 `id`。
3. **`_unverifiedPrice` 在 `SubmitOrder` 里** —— 提交前会再核一次价，
   价格变了就不提。replica 的 `CheckPriceLimitAsync` 是任务级别的价格上限，**不是这个**。

**还缺的只剩一样**：那 5 个 URL 后面接什么段名。字段名给了「写什么」，段名给不了「打到哪」。

### Nike 的请求头（第 50 轮）

```
nike-api-caller-id
x-nike-ux-id
x-nike-visitid
x-nike-visitorid
```

三个 caller id 值也在字符串里：

```
com.nike.commerce.checkout.web
com.nike.commerce.nikedotcom.web
com.nike.unite
```

**UA 片段**：`nike:com.nike.commerce.omega.ios:ios:26.8` —— `omega` 是 Nike 的 iOS 应用代号。

**`{0}oauth2/token`** —— token 路径是模板拼的，基址由 caller id 决定。

**replica 的 `NikeFlow` 一个都没设。** 它发裸 JSON 加 Kasada sensor。
sensor 证明「我是浏览器」，`nike-api-caller-id` 证明「我是哪个 Nike 客户端」——**两件事**。

### 支持的国家：**42 个**（第 89 轮更正；第 50 轮只读到 22 个）

字典序字符串池里有一段连续的 `Nike <CC>`：

```
Nike IT  Nike JP  Nike LU  Nike MX  Nike MY  Nike NL  Nike NO  Nike NZ
Nike PH  Nike PL  Nike PT  Nike RO  Nike SE  Nike SG  Nike SI  Nike SK
Nike TH  Nike TR  Nike TW  Nike US  Nike VN  Nike ZA
```

**replica 的 `Marketplace` 是 `const string Marketplace = "US";`** —— 一个国家写死。
原版有 22 个，并且 `_countryCode` 是一个**实例字段**（前面查到过），不是常量。

**还有两个移动端标识**：`NikeAndroidMobile`、`NikeIosMobile`，以及 `NikeGS`
（replica 里有一个独立的 `NikeGsFlow`，名字对得上）。

### 一条错误消息说明了 3DS 怎么做的

```
No 3D Secure session
No 3DS challenge found at
```

**`found at` 后面接一个地址** —— 原版会去某个 URL 找 3DS 挑战页，找不到就报这句。
这和 `RiotGamesFlow` 那类「等 3DS 窗口」不同：**它是主动去找那个页面**。

### 这一节为什么存在

`PARITY.md` §3 的能力表给 `nike` 打的是「✅ 加购」。**这一节说明那个 ✅ 只覆盖到
「有一个能跑的加购」，不覆盖「和原版同样的结账序列」。**

**两者不是同一件事。**

## 12. Nike endpoint 词汇表（第 87 轮，IDA 直接读出）

IDA 重新载入数据库后跑一次：

```
find_regex "api\.nike\.com"      →  20 条
```

**这 20 条就是二进制能调的全部 Nike base URL。** 已固化成
`Cybersole.Stores.Flows.NikeEndpoints`（19 个常量，产品流的 query 拼在字面量里），
并有 `NikeEndpointTests` 钉住——将来谁想「发明」第 21 个端点，测试会红。

| 家族 | URL |
|---|---|
| 结账预览 | `buy/checkout_previews/v3/` ＋ `_jobs/v3/` |
| 结账 | `buy/checkouts/v3/` ＋ `_jobs/v3/` |
| 运费报价 | `buy/fulfillment_offerings_jobs/v2/`（只有 jobs） |
| 预购购物车 | `buy/partner_cart_preorder/v2/` ＋ `_jobs/v2/` |
| 库存 | `deliver/available_gtins/v3` |
| 3DS | `payment/3ds_authentications/v3`、`payment/3ds_results/v3` |
| 延后付款 | `payment/deferred_payment_forms/v1` ＋ `/jobs/` |
| PayPal | `payment/paypal_details/v2`（＋jobs）、`payment/paypal_mark/v2`（＋jobs） |
| 支付预览 | `payment/preview/v3` ＋ `/jobs/` |
| 产品流 | `product_feed/threads/v2?fields=` |

### 对 replica 的直接结论

原版**没有** `buy/carts/v2/…`，也**没有** `buy/orders/v2/…` —— 而 replica 的 `NikeFlow`
正在用这两个家族：

| replica 现在 | 二进制里 |
|---|---|
| `buy/carts/v2/{CC}/Nike/SNKRS?format=simplified` | **不存在** |
| `buy/orders/v2/US/{id}/delivery` | **不存在** |
| `buy/orders/v2/US/{id}/initiatePayment` | **不存在** |
| `buy/orders/v2/US/{id}/payment` | **不存在** |
| `buy/orders/v2/US/{id}/submit` | **不存在** |

真正的形状是：**一个 `buy/checkouts/v3/{checkoutId}` 资源，14 步依次往它上面写**，
每一步的具体子路径由代码拼接（数据库里没有把它们作为独立字面量），
所以「哪一步写哪个子路径」**仍然没有证据**，`NIKE_PARITY.md` 第 11 节那张缺口表继续有效。

**这一步做的是把「不存在的东西」证实为不存在**，而不是把猜测换成另一个猜测。

## 13. 七个 Nike 标识（第 88 轮，IDA 读出）

```
find_regex "nike-[a-z-]+"   →  4 条；再把两个大写拼法手工确认
```

| 名字 | 地址 | 类型 |
|---|---|---|
| `NIKE-GS` | 0x146df584c | cookie |
| `NIKE-SESSION` | 0x146df5874 | cookie |
| `Nike-Kasada-Version` | 0x146dfbbd4 | header |
| `nike-api-caller-id` | 0x1470e4b84 | header |
| `x-nike-ux-id` | 0x14716b6d4 | header |
| `x-nike-visitid` | 0x14716b704 | header |
| `x-nike-visitorid` | 0x14716b73c | header |

**第 11 节写的「4 个 Nike header 未设置」其实是 7 个标识：4 个 header + 1 个 Kasada 版本 header
+ 2 个 cookie。而 replica 一个都没发。**

## 13b. 国家表是 42 个，不是 22 个（第 89 轮更正）

第 50 / 86 轮记的是 22 个市场，于是 `NikeFlow.Countries` 只有 22 项，`CountryFor("UK")` 还
因为「二进制没有 GB 市场」而回落到 US。第 89 轮直接查：

```
find_regex "Nike [A-Z]{2}$"   →  42 条（0x28 字节间隔，按字母序）
```

```
AT AU BE BG CA CH CZ DE DK ES FI FR GB GR GS HR HU IE IL IN IT JP
LU MX MY NL NO NZ PH PL PT RO SE SG SI SK TH TR TW US VN ZA
```

**`GB` 就在里面。** 之前那 22 个是这张表从 `IT` 开始的一段——**读到的是窗口，不是表**。

所以 R86 引入了一个真实的错：把 UK 的请求打到美国去。现在：
`Countries` 42 项、按字母序、`UK → GB`、`DE → DE`、`FR → FR`，只有表外的（`CN` 等）才回落到 US。

已固化为 `Cybersole.Stores.Flows.NikeHeaders`：

- 五个 header 名 → session var 键的映射（`nike.apiCallerId` / `nike.uxId` / `nike.visitId` /
  `nike.visitorId` / `nike.kasadaVersion`）
- `Apply(vars, headers)` 只在**真的观测到值**时才设置该 header，返回设置了几条

`NikeFlow.GetSessionAsync` 现在会把已知的那些塞进 `c.Session.Headers`。

### 为什么不用默认值

一个填了假值的 header 告诉 Kasada「这个客户端在说谎」，比「这个客户端没发这个 header」更糟。
**所以宁可少发，不发假。** `NikeHeaderTests.OnlyKnownValuesReachTheHeaders` 钉住这条。

## 14. 步数是 **16**，不是 14 —— 而且名字是编译器给的（第 111 轮）

R111 在重建后的 IDA 库里，字符串池中**一段相邻的字面量**就是整条 Nike 结账链，
带着编译器分配的 `d__N` 序号：

```
d__41 StartEcomSession      d__42 Authorize              d__43 GetAccessToken
d__44 FindVariant           d__46 CreateBasket            d__48 SubmitCustomer
d__49 ValidateAddress       d__50 SubmitShippingAddress   d__51 GetShippingMethods
d__52 SubmitShippingMethod  d__53 SubmitBillingAddress    d__54 BeginCheckout
d__55 CheckInventory        d__56 GetShopperIp            d__57 GetPaymentMethods
d__58 SubmitOrder
```

**16 步。** 文档从第 50 轮起一直写「14 步」，那是**读了一段就当全表**的又一次重犯。

序号跳过了 45 和 47 —— 那两个是编译器在两步之间插入的 `MoveNext` 辅助方法，
**不是步骤**。所以「有缺口」不代表「漏了步骤」。

### 手写清单会合并的那两对

| 手写时容易合并 | 镜像里 |
|---|---|
| `StartEcomSession` + `BeginCheckout` | **两步**（41 / 54） |
| `Authorize` + `GetAccessToken` | **两步**（42 / 43） |

**14 → 16 差的正好是这两对。** 这也解释了为什么之前那张表「看起来对、数起来少」。

已固化为 `Cybersole.Stores.Flows.NikeSteps`（16 条 + `Position()` + `IsStep()`），
`NikeStepTests` 五条钉住：16 条、序号升序、**只缺 45/47**、两对必须不同、位置 1-based。

### 与 persisted GraphQL 对上了

`BeginCheckout` / `SubmitOrder` / `GetPaymentMethods` 这三步，
正好对上第 13 节那 6 个 `persisted?operationName=`（`Proposal` / `SubmitForCompletion` /
`PollForReceipt` / `PaypalDetails` / `PaypalToken` / `CheckoutExtensionSessionToken`）。
**两条独立证据指向同一个形状：Nike 的结账后半段是持久化 GraphQL，不是 REST 子路径。**

## 15. 两个 POST 反编译落地 —— R1014 的悬案终局（第 1076 轮）

`chars_va - 12` 链把承载全部结账语义的两个函数直接定位出来，全部键名用
`names_at.py` 从冻结常量解出（可复算命令见 `docs/BLOCKERS.md` R1076）：

| 冻结串 | chars_va | 对象头 | `.text` 引用点 | 所属函数（.pdata） |
|---|---|---|---|---|
| `https://api.nike.com/buy/checkout_previews/v3/` | `0x147053c94` | `0x147053c88` | `0x140B1EDB1` | **`sub_140B1DCC0`**（4,617 B） |
| `https://api.nike.com/buy/checkouts/v3/` | `0x147053d8c` | `0x147053d80` | `0x140B26A5E` | **`sub_140B248A0`**（8,935 B） |

**第 12 节结尾那句「哪一步写哪个子路径仍然没有证据」就此作废：根本没有子路径。**
两个 POST 的 `request` 对象把一切内联 —— 配送块写在 preview POST 的
`items[].fulfillmentDetails.location.postalAddress` + `recipient` + `contactInfo`，
订单提交是 checkout POST 加 `paymentToken` 与 `totals`。R48 的「14 步对 5 URL =
逐步写入同一资源」读对了资源、读错了机制：**不是逐步 PATCH，是两个大 POST 加 jobs 调用。**

### preview POST（`sub_140B1DCC0`，两段状态机）

```
POST https://api.nike.com/buy/checkout_previews/v3/{市场}
{"request":{
  "country"        ← 收货地址的 country（B+64）
  "currency"       ← 任务枚举转字符串（sub_141CEDAC0，表未解）
  "locale"         ← ctx[23]
  "channel"        ← "NIKECOM"（0x146E11460）
  "items":[{ id(ctx19), skuId(ctx17), productId(ctx16),
             "offers":[], "itemCosts":{ priceInfo{8 个占位}, promotionDiscounts:[{code}] },
             "quantity"←购物车数量, "fulfillmentDetails":{ "type":"SHIP"(0x146E747F0),
               "getBy"←ctx32, "location":{ "id"←ctx27,
                 "postalAddress":{ country,address1,address2,postalCode,city,state },
                 "type":"address/shipping"(0x146F6EAB0) } },
             "valueAddedServices":[], "recipient":{firstName,lastName},
             "contactInfo":{phoneNumber,email} }]
  "promotionCodes":[discount_code]   ← 无码时 [null]（无条件发送 cell）
  "email"                            ← 最后一个键
}}
→ 之后必发一记 checkout_previews_jobs/v3/{同字段}（3 参 sub_1408B61E0，响应被丢弃）
```

priceInfo 占位与原版逐格对应：`price/fullPrice/subtotal/total/fullPriceTotal = null`，
`discount/valueAddedServices/taxTotal = 0`。

### checkout POST（`sub_140B248A0`，'Submit order' 0x146EA00F0）

同形再加：`email` **提到第一个键**、请求级 `paymentToken`←ctx29、`promotionCodes`
**有码才发**（`[]` 否则）、`items[0]` 多 `priceId`(ctx30)/`priceSnapshotId`(ctx31) 与
`taxes:[]`、以及完整 `totals` 块（null / 0 / `"NOT_CALCULATED"`(0x146E11E58) 逐位钉死在
`NikeBuyRequestTests`）。**JP 构型**（任务 channel == `'Nike JP'`(0x146E173E8)）：
recipient 加 `altFirstName`/`altLastName`（profile 的 `kana_first_name`/`kana_last_name`，
缺省空串哨兵 0x146A622F8），postalAddress 加 `address3` = address2。

**state 哨兵分支**：state ∈ {`ASTLA`(0x146B34B08), `CA`(0x146B655C8)}（先引用相等再逐值）
→ 发 `"{country}-{state}"`；否则原样发 state 字段。

### 落地与剩余

- `SubmitShippingAsync` = preview POST + jobs 跟进；`SubmitOrderAsync` = checkout POST。
  两者均为**可执行运行时实现**（`NikeFlow.BuildBuyRequest`/`BuildBuyItem`/`BuildTotals`），
  由 `NikeBuyRequestTests` 10 个用例钉住键序、字面量与占位形状。
- 证据等级：以上全部字段与控制流为 **Observation**；货币 ISO 表、locale 格式、
  jobs 跟进动词（GET，与 AYCD verify 共用 `+8` 槽）、ctx[26] 在两次调用之间被响应
  映射器改写为 job id 的读法、id/skuId 双 ctx 字段的 feeder、kana→JapaneseName 映射
  为 **Inference**（各自写入实现注释，可被后续反编译修正）。
- **剩余 Unknown**：`GetPaymentMethods`/`SubmitPayment` 的 initiatePayment 通道
  （`/rpc/payment/pay/initiatePayment` 无 host 配对，见 §12 与 PAYMENT_CHALLENGES.md）。
