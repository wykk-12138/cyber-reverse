# 端点族总表（截至 R104）

从 `Cybersole.exe` 5.18.32 的 UTF-16 字面量里 dump 出来的所有平台端点族。
每族的数量、形态、以及「它告诉了我们什么」都在这里。

取法：`python analysis/pe_strings.py current\Cybersole.exe pe_strings.txt 8`
（180,228 条去重字符串，不需要 IDA）。

| 族 | 数量 | 形态 | 证据轮次 | 常量 |
|---|---|---|---|---|
| Nike REST | 20 | `api.nike.com/buy/{checkouts,checkout_previews}/v3/` + `payment/*` | R87 | `NikeEndpoints` |
| Nike 标识 | 7 | 4 个 header + Kasada 版本 + 2 个 cookie | R88 | `NikeHeaders` |
| Nike 市场 | 42 | `Nike <CC>`，字母序 | R89 | `NikeFlow.Countries` |
| Nike persisted GraphQL | 6 | `checkouts/internal/graphql/persisted?operationName=` | R101 | `NikePersistedOperations` |
| Shopify REST | 2 | `cart/add.js`、`cart/update.js` | R96 | `ShopifyCartEndpointTests` |
| Shopify GraphQL | 2 文档 + 4 版本 | 354/346 字符逐字 + `api/{2020-04,2021-10,2024-10,2025-04}` | R97 | `ShopifyGraphQl` |
| Shopify 主机 | 1182 | `*.myshopify.com` | R96 | `docs/shopify_hosts.txt` |
| Demandware 经典 | 17 + 8 站点 | `/on/demandware.store/Sites-{site}-Site/{locale}/{ctrl}` | R94/R95 | `DemandwareControllers` |
| SFCC SCAPI | 9 | `/scapi/ShopperBaskets/*` + `/scapi/ShopperLogin/*` | R101 | `ScapiEndpoints` |
| Pop Mart | 39 | `/shop/v1/{box,order,shop/cash/desk,drawScratch,storeOfflineDraw,…}` | R100 | `PopMartEndpoints` |
| Demandware 抽签 | 6 | `/pages/raffle` + `panagora-raffle-data` 提取器 + `SaleRegistration-*` | R99 | `DemandwareRaffle` |
| 零售 RPC | 7 | `/rpc/ec/{buyRule,freight,order,spu,userAddress}/*` | R102 | `StoreApiFamilies.RpcEc` |
| 单页结账 | 7 | `/component/singlepagecheckout/*` | R102 | `StoreApiFamilies.SinglePageCheckout` |
| 发布闸门 | 8 | `/apps/gatekeeper/api/*`（token 交换链 + 遥测） | R102 | `StoreApiFamilies.Gatekeeper` |
| John Lewis BFF | 12 | 摊在 **v1/v2/v3/v4** 四个版本 | R103 | `RetailApiFamilies.JohnLewisBff` |
| Scheels Frontastic | 17 | `/frontastic/action/{account,adyen,cart,product}/*` | R103 | `RetailApiFamilies.ScheelsFrontastic` |
| better-auth | 11 | `/api/auth/{csrf,session,sign-in/email,…}` | R104 | `AccountAndAuthFamilies.BetterAuth` |
| Magento 账户 | 8 | `/account/login{,Post}/`，含 base64 referer 变体 | R104 | `AccountAndAuthFamilies.MagentoAccount` |
| On Running（韩国站） | 7 | Magento GraphQL router + `/ko-kr/checkout/*` | R104 | `AccountAndAuthFamilies.OnRunning` |

## 五条从族里读出来的结论

1. **Nike 的结账步骤不是 REST 子路径**，是 `operationName` 形式的持久化查询 ——
   这就是 R87/R88 找不到 `buy/orders/v2/{id}/shipping` 的原因（R101）。
2. **John Lewis 没有单一 base URL**：账单 v1、支付 v2、配送 v3、地址 v4。
   版本是数据，不是常量（R103）。
3. **Scheels 的风控是流程的一部分**：`sendSignifydStepUpCode` →
   `completeSignifydStepUpCheckout`，跳过它看起来像「一直被拒」（R103）。
4. **gatekeeper 是闸门不是购物车**：`render-token` → `gatekeeper-token` → `validate`，
   跳过它的后果是像封号的 403；`audit-events/*` 只是遥测，不能拿来 gate（R102）。
5. **SFCC 有两条路**：经典 `demandware.store` 控制器 与 SCAPI，原版两条都走（R101）。

## 唯一一条「解码得到」而不是「抄下来」的证据

Magento 的 `/account/login/referer/{base64}` 变体，镜像里有两条真实 payload：

```
aHR0cHM6Ly93d3cucGFuaW5pLml0L3NocF9pdGFfaXQvY3VzdG9tZXIvYWNjb3VudC9pbmRleC8  →  https://www.panini.it/shp_ita_it/customer/account/index/
aHR0cHM6Ly93d3cuZm9vdGxvY2tlci5waC8%2C                                      →  https://www.footlocker.ph/
```

`AccountAndAuthFamiliesTests.TheRefererPayloadsDecodeToRealHosts` 现场解码并断言 ——
**这是本会话唯一一条「字符串 → 含义」的证明，其余都只是「字符串存在」。**

## 每个店的步骤清单（第 111–112 轮，字符串池实证）

每个流程的步骤在池子里是**一段相邻字面量**，带编译器分配的 `d__N` 序号 ——
所以「这个店几步、先后顺序如何」不再靠猜。

| 店 / 流程 | 步数 | 关键步骤 | 对应端点族 |
|---|---|---|---|
| Nike | **16** | `StartEcomSession 41` … `SubmitOrder 58` | `NikeEndpoints`（R87）+ persisted GraphQL（R101） |
| Pop Mart | **24** | `StartDrawFlow 115`、`FindMegaDraw 133`、`RedeemLuckPoints 137`、`EnterReservation 153` | `/shop/v1/*`（R100） |
| John Lewis | **17** | `WebHandOver 23`、`GuestCallback 25`、`SubmitOrderStripe 32`、`GetStripePaymentIntent 39` | `bff/v1..v4`（R103） |
| Demandware 经典 | **12** | `InitiateCheckout 33`、`GenerateCSRF 34`、`SubmitConsignment 37`、`ConfirmPayment 43` | 经典控制器（R94） |
| Demandware 双路 | **15** | `StartAppFast 36`、`GetCartDw 39`、`AddToCartApp 41`、`AddToCartAppDw 42`、`SaveSessionDw 43` | SCAPI + 经典（R101 / R107） |

### 三段没有店名的流程（第 113 轮）

池子里这三段没有配店名，所以代码里也**不写品牌** —— 只记「凭什么认出它」：

| 流程 id | 步数 | 识别依据 |
|---|---|---|
| `collectplus-app` | 17 | `GetCollectPlusLocations` / `SubmitCollectPlus`（CollectPlus 是英国自提网络）+ `*App` 步 + 以 `GetPaymentUrl` 收尾 |
| `structure-token-multi` | 15 | `GetMerchantCode` → `GetStructureToken` → `CreateTransaction` → `ProcessPayment`，多规格（`FindProductMulti`）+ `CalculateTaxes` |
| `structure-token-single` | 12 | 同一引擎的单规格形状（`EditLine` 开头），`GetStructureToken` 在序号 40 |

「structure token」不是编的名字：镜像里还有 `PaymentData.UrlStructureTokenEncoded`、
`_structureToken`、`#UrlStructureTokenEncoded` —— 它是真实支付集成的一个字段。
**但具体是哪家支付商、哪个品牌，没有证据，所以不写。**

两条 structure-token 流程**共享 10 个步骤名**（`GetCheckout`、`GetMerchantCode`、
`GetShippingRate`、`SubmitShipping`、`GetStructureToken`、`CreateTransaction`、`SubmitPayment`、
`GetPayPalToken`、`SubmitPayPal`、`ProcessPayment`）—— 同一引擎、两个店面。
测试里的这个数字**是从两份列表算出来的**，不是手数的（我手数了两次都错：先 8、后 9）。

### 三条从步表里读出来的结论

1. **Pop Mart 有 24 步，比 Nike 还多** —— 它不是「结账流程」，是抽签/积分/预约平台：
   `EnterDraw`、`FindMegaDraw`、`RedeemMemberPoints`、`RedeemLuckPoints`、`EnterExhibit`、
   `EnterReservation`。这解释了为什么它的端点族有 39 条（R100）。
2. **Demandware 的两套步数是两件事**：经典 12 步（`SubmitConsignment` = Salesforce 的「配送」），
   和 15 步的**双路流程** —— `AddToCartApp` 与 `AddToCartAppDw`、`GetCartDw`、`SaveSessionDw`
   同时存在，说明原版在某些店上**两条路都养着**。这正是 R101 在端点里看到的 SCAPI/经典并存，
   也是 R107 接进 `DemandwareFlow` 的那个形状。
3. **John Lewis 的 Stripe 链是完整的**：`SubmitOrderStripe` → `AuthenticatePayment` →
   `HandleRequiresAction` → `GetStripePaymentIntent` —— 四个步骤才是一个 3DS 循环，
   少一个就卡在 `requires_action`。

已固化为 `Cybersole.Stores.Flows.StoreFlowSteps`（5 个流程 + `FlowFor()` + `AllStepNames()`），
`StoreFlowStepsTests` 六条钉住：五个步数、序号升序、Pop Mart 的抽签/积分/预约、
Demandware 双路的 App/Dw 成对、经典链里的 `SubmitConsignment`、按名字反查所属流程。

## 店铺底下的第三方服务（第 114 轮）

不是店铺、但原版真的在调的服务层：

| 服务 | 主机 / 端点 | 它是什么（依据） |
|---|---|---|
| **Scheels 移动 API** | `https://mobile-api.scheels.com/v5/auth/guest`、`/v5/products/` | 与 R103 的 Frontastic hub **是两个 API** |
| **END Clothing REST** | `https://api2.endclothing.com/rest/V1` | Magento REST（`ApiHost` 属性名就在旁边） |
| **AYCD 收件箱** | `inbox-api.aycd.io/api/v1/{user/verify, tasks/mail/create, tasks/completed?group=}` | 「验证 key → 建收信任务 → 轮询完成」三步 |
| **Parallax Systems** | `api.parallaxsystems.io/{gen, holdcaptcha}` | **验证码服务**：属性名就叫 `GenEndpoint` / `HoldCaptchaEndpoint` |
| **Google Maps** | `maps/api/geocode/json?address=`、`maps/api/js?libraries=places&key=` | 邮编 → 地址、地址自动补全 |

### 三条读出来的结论

1. **Scheels 有两个 API**：`apihub.scheels.com/frontastic/action/…`（Web hub，R103）
   和 `mobile-api.scheels.com/v5`（移动端）。**一个店有 web 与 app 两套 API**，
   和 R112 里 Demandware 那套 `App`/`Dw` 双路步表是同一种形状。
2. **Parallax 是「占位 + 求解」两段式**：`/holdcaptcha` 先把一个验证码槽位占住，再去 `/gen`。
   这就是为什么它的属性名是两个而不是一个 —— **占位和生成是两次调用**。
3. **AYCD 的三个端点正好是设置页那三个动作**：`user/verify`（填 key 后验证）、
   `tasks/mail/create`（建任务）、`tasks/completed?group=`（按组轮询）。
   GUI 那边的 IMAP 设置页是这三个端点的界面 —— **GUI 在这里只是给端点做注脚**。

> 注：本表的总数由五个分组分别计数后相加得出，**不是手写的总数**
> （手写总数在这一轮错了一次：写 14，实际 13）。

## 步 → 主机：Scheels 的双 API 对照（第 115 轮）

R114 找到 Scheels 的移动 API，R115 补上第三个端点 `/v5/Order/`，
于是**步列表和主机**第一次能对起来了 —— 但**只能对着名字对**：

| 移动端（`mobile-api.scheels.com`） | 步 |
|---|---|
| `v5/auth/guest` | `StartAppFast`、`StartAppSafe` |
| `v5/products/` | `FindProductApp`、`AddToCartApp` |
| `v5/Order/` | `SubmitOrderApp` |

| Web hub（`apihub.scheels.com/frontastic/action/`） | 步 |
|---|---|
| `account/login` | `Login` |
| `product/getProduct` | `GetProduct` |
| `cart/addToCart` | `AddToCart` |
| `cart/checkout` | `Checkout` |
| `cart/completeDetailsCheckout` | `CompleteDetailsCheckout` |
| `cart/sendSignifydStepUpCode` | `SignifydStepUpCode` |
| `cart/completeSignifydStepUpCheckout` | `CompleteSignifydStepUp` |

### 这张表是什么、不是什么

**是**：名字层的对应关系 —— `FindProductApp` 与 `products/` 说的是同一个名词，
`SubmitOrderApp` 与 `Order/` 也是。这是**当前唯一可用的桥**，把「步」和「主机」连起来。

**不是**：抓包。**没有任何一次请求被观察过。** 所以代码里写的是
`DualApi.Evidence = "name correlation … no request capture …"`，
测试断言这句话必须留在那儿 —— **一旦有人把它当成结论，这条断言会红。**

> 这是本会话第一次把两类证据（步表 / 主机表）接起来，
> 也是第一次**在接起来的同时声明「这条线是猜的」**。

## Pop Mart：24 步 ↔ 39 端点（第 116 轮）

本会话里**步数与端点数都最大的一对**。名字一致的地方连线，不一致的地方**留空并记下来**。

| 步 | 端点 |
|---|---|
| `GetOrders` | `/shop/v1/order/list` |
| `StartDrawFlow`、`FindDraw` | `/shop/v1/drawScratch/detail?uniqCode=` |
| `EnterDraw` | `/shop/v1/drawScratch/draw` |
| `ChooseGoods` | `/shop/v1/drawScratch/chooseGoods` |
| `FindMegaDraw`、`EnterDrawEvent` | `/shop/v1/drawScratch/megaDraw/hit` |
| `RedeemMemberPoints` | `/shop/v1/redeem/points_redeem_draw` |
| `RedeemLuckPoints` | `/shop/v1/redeem/lucky_points_redeem_draw` |
| `FindExhibit` | `/shop/v1/storeOfflineDraw/info?alias=` |
| `EnterExhibit`、`EnterReservation` | `/shop/v1/storeOfflineDraw/join` |
| `FindDates` | `/shop/v1/store_ticket/dateList` |
| `FindTimeSlots` | `/shop/v1/store_ticket/mainPage?uniqID=` |

**14 对。**

### 留空的 10 步（名字不settle）

```
CheckResult        StartDrawCheckFlow   StartDrawEventFlow   CheckDraw
FetchAliases       FetchDetails         StartExhibitFlow     StartReservationFlow
GetInstoreOrders   还有 1 个
```

`CheckResult` 可能是 `drawScratch/detail` 的轮询，也可能是另一个接口 —— **镜像里没有任何东西能定这个**，
所以留空。这 10 步现在是「待抓包确认」的清单，而不是一片空白。

### 另一侧：39 个端点里 25 个没有被任何步名点到

包括整个收银台族（`cash/desk/{adyen,alipayGlobal,paypal,stripe}`）、
`coupons/*`、`promotion/getList`、`freight/result`、`mission/*`。
这些是**结账后半段**用的 —— 而 Pop Mart 的 24 步全是「抽签/积分/预约」，
**结账那半段不在这个 flow 里**。这本身就是一条结论：**抽签流程和结账流程是两套。**

> 这张表和 R115 的 Scheels 表一样，写的是
> `name correlation … no request capture … unmapped steps and endpoints are recorded, not guessed`。
> 测试断言这句话必须留着。

## Demandware：12 步 ↔ 控制器（第 117 轮）—— 这一轮暴露的是**我的表不全**

| 步 | 控制器 |
|---|---|
| `AddToCart` | `Cart-AddProduct` |
| `InitiateCheckout` | `Checkout-Begin` |
| `GenerateCSRF` | `CSRF-Generate` |
| `GetCheckout` | `CheckoutServices-FetchOrderModel` |
| `SubmitBillingAddress` | **`CheckoutServices-SubmitBilling`**（R117 新发现） |
| `SubmitConsignment` | `CheckoutShippingServices-SubmitShipping` |
| `SubmitShippingOption` | **`CheckoutShippingServices-UpdateShippingMethod`**（R117 新发现） |
| `CreateOrder` | `CheckoutServices-PlaceOrder` |
| `SubmitPayment` | `CheckoutServices-SubmitPayment` |
| `ConfirmPayment` | **`CheckoutServices-PaymentAuthorization`**（R117 新发现） |

### 这一轮最重要的事：缺的三个不是二进制缺，是**我的表缺**

R94 我从字符串池的一个窗口里抄了 17 个控制器。拿 12 步去对，发现**三步没有对应的控制器**。
再往外搜，立刻找到 5 个新名字：

```
CheckoutServices-SubmitBilling          CheckoutShippingServices-UpdateShippingMethod
CheckoutServices-PaymentAuthorization   CheckoutServices-FetchOrderModel
CheckoutServices-SubmitCash             Adyen-Adyen3DS2 / Adyen-PaymentsDetails
```

**缺的是我抄的那一页，不是原版。**

> 这正是「步表当主参照」的价值：**它会在你的端点表不全的时候告诉你。**
> 反过来（只看端点表）永远不会发现缺口 —— 因为缺口看起来就是「没有这项」。

### 留空的 2 步

| 步 | 为什么留空 |
|---|---|
| `GetPaymentMethod` | 镜像里唯一的支付读取就是 `FetchOrderModel`，而它已经给了 `GetCheckout`；这一步是重读模型还是问别的，名字定不了 |
| `CreateStripePaymentMethod` | **镜像里没有任何 `Stripe-*` 控制器**。支付控制器全是 Adyen 的（`AdyenUpgrade-Authorize`、`Adyen-Adyen3DS2`、`Adyen-PaymentsDetails`、`AdyenComponents-Payment*`） |

第二条是一条独立结论：**这一步要么走通用提交带 Stripe 表单，要么原版自己这里就是缺口** ——
两种都比「我编一个 `Stripe-Components-Payment` 出来」诚实。

## John Lewis：17 步 ↔ 12 端点（第 118 轮）—— 第一次「步比端点还多」

| 步 | 端点 |
|---|---|
| `WebHandOver`、`SessionHandover` | `bff/v2/sessions/web/handover` |
| `GuestCallback` | `bff/v4/callback/guest` |
| `DeliveryPage` | `bff/v3/orderforms/delivery-page` |
| `SubmitShipping`、`CreateDelivery` | `bff/v4/orderforms/deliveries` |
| `GetDeliveryMethods`、`SubmitDeliveryMethod` | `bff/v3/orderforms/deliveries/details` |
| `GetPaymentPage` | `bff/v2/orderforms/payment-page` |
| `SubmitOrderStripe`、`AuthenticatePayment` | `bff/v2/orderforms/payments` |
| `SubmitOrder`、`PlaceOrder` | `bff/v2/orders` |
| `SubmitBillingAddress` | `bff/v1/orderforms/payments/billing-address` |

**14 步 → 9 个不同端点。**

### 这个形状本身就是一条结论

**BFF 端点是「服务端的资源」，步是「客户端的阶段」。** 所以两个步共用一个端点是正常的，
不是错误 —— `handover` 同时服务 `WebHandOver` 和 `SessionHandover`，
`deliveries` 同时服务 `SubmitShipping` 和 `CreateDelivery`。**不要为了「一一对应」去拆端点。**

### 留空的 3 步：一个页面加载 + 两次 Stripe 调用

| 步 | 为什么留空 |
|---|---|
| `GetHome` | 页面加载，不是 BFF 资源 |
| `HandleRequiresAction` | **Stripe 的 3DS 回调**，打 Stripe 主机 |
| `GetStripePaymentIntent` | **Stripe 的 PaymentIntent**，同上 |

### 与 R117 正好互补

| 店 | Stripe 在哪 |
|---|---|
| **Demandware** | 有 `CreateStripePaymentMethod` 步，但**镜像里没有 `Stripe-*` 控制器**（支付控制器全是 Adyen） |
| **John Lewis** | 有 `HandleRequiresAction` / `GetStripePaymentIntent` 两个步，**直接打 Stripe 主机**，所以没有 BFF 端点对应它们 |

两条加起来说明：**「Stripe 步骤」在两个店里都存在，但只有其中一个把 Stripe 放在自己的控制器族里 —— 而那个是零。**

### 另一侧的 3 个端点没人点

`v4/orderforms/deliveries/`（尾斜杠变体）、`v4/orderforms/deliveries/delivery-address`、
`v3/orderforms/payments/`。第一个是同一资源的两条字面量，后两个留给「地址独立提交」和
「v3 支付」两条支路 —— **有端点没步，说明还有分支没被我看到。**

## 修正：John Lewis 是 **19 步**，不是 17（第 119 轮）

R112 读到的 John Lewis 步表是 17 条，序号从 20 跳到 23 —— 我当时把那个缺口当成了编译器噪音。

**它不是。** 同一个类的**另一条字面量**（lambda 表）里写着：

```
<<FindProduct>g__Available|21_3      ← 方法 21 = FindProduct（内部还有个 local function）
<AddToCart>b__22_0                    ← 方法 22 = AddToCart
```

所以 **21 和 22 也是这个 flow 的步**：

| 序号 | 步 | R112 是否读到 |
|---|---|---|
| 20 | `GetHome` | 是 |
| **21** | **`FindProduct`** | **否** |
| **22** | **`AddToCart`** | **否** |
| 23 | `WebHandOver` | 是 |
| … | … | … |

**19 步。**

### 为什么这次能发现，上次不能

Nike 的 45/47 缺口真的是 `MoveNext` 助手（R111 已核实），所以「缺口=噪音」在 Nike 身上成立。
John Lewis 的 21/22 不是 —— **但只靠一条字面量分不出来**。

区别只在**第二条证据**：lambda 表把每个方法的序号和名字又列了一遍，
`21` 和 `22` 在那里有名字。

> **一条字面量的缺口，需要第二条字面量来判。**
> 我从 R112 到 R118 用了六轮，才第一次去看同一个类的 lambda 表。

### 对映射的影响

`FindProduct` / `AddToCart` 留空 —— **BFF 里根本没有购物车端点**，它从 handover 才开始。
所以 John Lewis 的留空步骤从 3 条变成 5 条：

```
GetHome   FindProduct   AddToCart   HandleRequiresAction   GetStripePaymentIntent
```

而「14 步 → 9 端点」不变：**新发现的两步没有端点，所以映射部分不受影响 —— 只有总数变了。**

## 序号扫描找到了名字，但不能证明归属（第 120 轮）

R119 学到：步表跳过某个序号时，去读**同一个类的 lambda 字面量**。
R120 试了更省事的办法 —— 扫全库的 `<Name>d__N`，按序号归堆。**它失败了，原因值得记下来：**

> **序号是「每个类各自编号」的。**

同一个序号 126 上同时挂着三个类的方法：

```
126  CompletePayPalGuestPayment   ← 支付类
126  Register                     ← 账户类
126  SubmitKlaviyoSubscription    ← 营销类
```

所以裸序号**说不出一个名字属于哪个类**。扫描结果只能是**候选**，不能并进 `StoreFlowSteps`。

### 九条候选（三个族）

| 序号 | 名字 | 同序号还有 |
|---|---|---|
| 106 | `AddToCartGraphQL` | `CartApiObjectCreate` |
| 107 | `AddToCartPreloadGraphQL` | `GetUnzerCallback` |
| 108 | `CreateCartGraphql` | `FetchTokensFromBrokerAsync` |
| 109 | `GetCartAvailabilityGraphql` | — |
| 125 | `CompletePayPalPayment` | — |
| 126 | `CompletePayPalGuestPayment` | `Register`、`SubmitKlaviyoSubscription` |
| 127 | `CompleteForwardPayment` | `WriteAttributeTextBlockAsync` |
| 128 | `AddToCartStoreFront` | — |
| 130 | `AddToCartPreload` | `WriteRawWithCharCheckingAsync` |

### 其中两族值得用「字面量法」再查一次

1. **GraphQL 购物车族（106–109）** 与 R101 那 6 个 `persisted?operationName=` 相互印证 ——
   这是 Nike 那条链的购物车半边，而 R96 已证明 replica 完全没有 GraphQL 购物车。
2. **PayPal / forward payment 族（125–127）** 与 R118 那条「某店直接打支付商主机」相互印证。

`CandidateStepTests.NoCandidateWasPromotedToAStep` 断言：
**候选与步表必须互不相交** —— 谁把候选当步用，测试就红。

> 这一轮的价值不在「找到了九个名字」，在**「证明了序号扫描不能用来证明归属」**。
> 否定一种方法，和找到一条证据一样有用 —— 只是它看起来不像进展。

## 归属如何证明：lambda 字面量，而不是 `d__` 连续段（第 121 轮）

R120 说「序号扫描证明不了归属」。这一轮找到了**能证明归属的证据**，顺便推翻了自己的一个默认假设。

### 证据一：`d__` 连续段 —— **不可靠**

```
1046:GetAccessToken   1050:CartApiObjectCreate   106:AddToCartGraphQL
```

1046 和 1050 属于**另一个大得多的类**，它的字符串只是**恰好排在这个类的字符串旁边**。

> **池里的相邻 = 文件里的相邻，不是「同一个类」。**

### 证据二：lambda 字面量 —— **可靠**

编译器把一个类的 lambda 生成成**一条字符串**，里面每个方法都带编号和名字：

```
:<CartApiObjectCreate>b__105_0  4<AddToCartGraphQL>b__106_0  B<AddToCartPreloadGraphQL>b__107_0
6<CreateCartGraphql>b__108_0   H<GetCartAvailabilityGraphql>b__109_0 … 6<RefreshEmailLogin>b__114_2
```

**连续 105 → 109，加 114，名字都在。** 这是这个类自己的方法表。

### 于是有一个 GraphQL 购物车类

| 序号 | 方法 |
|---|---|
| 105 | `CartApiObjectCreate` |
| 106 | `AddToCartGraphQL` |
| 107 | `AddToCartPreloadGraphQL` |
| 108 | `CreateCartGraphql` |
| 109 | `GetCartAvailabilityGraphql` |
| 114 | `RefreshEmailLogin`（同一个 lambda 字面量点名，属于这个类但不是购物车调用） |

四条 GraphQL 购物车调用 —— **正是 R96 证明 replica 完全缺失的那半边**。

### 十条回合绕出来的规则

> **lambda 字面量是归属证人；`d__` 连续段不是。**

R112 用连续段读步表（对），R119 用 lambda 表补跳空的步（对），R120 用裸序号扫描（错），
R121 才说清**为什么前两个对、第三个错**：

| 方法 | 能回答什么 |
|---|---|
| `d__` 连续段 | 一个类**大概**有哪些步（相邻但可能串类） |
| **lambda 字面量** | 一个类**确实**有哪些方法（一条串起，名字+序号成对） |
| 裸序号扫描 | 什么都证明不了（跨类编号冲突） |

## 那把尺子量了八个流程：**只有两个有证人**（第 122 轮）

R121 的规则是「lambda 字面量证明归属」。R122 把它量到所有流程上，结论是**这条规则很窄**：

| 流程 | 有归属证人？ | 证人范围 |
|---|---|---|
| John Lewis | **有** | 方法 20–39 |
| Nike | **有** | 方法 41–58 |
| Pop Mart / Demandware ×2 / CollectPlus / StructureToken ×2 | **无** | — |

**证人只在「序数和流程自己的序号对得上」时成立。** Pop Mart 的 lambda 字面量里
**没有任何一条**带 104–153 范围的序号 —— 所以它的 121–130 缺口**没有证人**，
R120 那九条候选**保持候选**。

### 为什么名字本身不算证据

扫描找到过这样的 lambda 表：

```
1:Authorize   2:SubmitShippingAddress     ← 看着像 Nike 的步，其实不是
```

Nike 的 `Authorize` 在**序号 42**。序号 1 的 `Authorize` 是**另一个类**的方法，只是同名。

> **名字会重名，序号不会跨类。** 所以「这个名字出现在一条 lambda 表里」什么都不证明；
> 只有「这条表的序号区间和那个流程重合」才证明。

### 扫描的副产品：Pop Mart 的**购物车类**

| 序号 | 方法 |
|---|---|
| 1 | `GetCartDataList` |
| 2 | `FetchCoupons` |
| 3 | `SubmitDiscount` |
| 4 | `ClearCart` |
| 5 | `FetchAddress` |
| 6 | `FetchAddress`（重载，保留两条） |

这六个名字与 Pop Mart 的 `/shop/v1/*` 端点族**逐一对应**（`cartDataList`、`couponsList`、
优惠券提交、地址拉取）。

**所以 Pop Mart 有两半：**

| 半 | 形态 | 规模 |
|---|---|---|
| 抽签 / 积分 / 预约 | 24 步的 flow | `EnterDraw`、`RedeemLuckPoints`、`EnterReservation` |
| **购买** | 6 方法的购物车类 | `GetCartDataList`、`FetchCoupons`、`SubmitDiscount`、`ClearCart`、`FetchAddress` |

这是 R116「抽签与结账是两套」的**第二个独立证据** —— 那次是从「25 个端点没人点」推的，
这次是从「有另一个类专门做这几件事」看到的。

## Pop Mart 的购买半边走通了（第 123 轮）

R122 找到那个 6 方法的购物车类之后，这一轮把能落的三个落进 `PopMartFlow`：

| 类方法 | 端点 | 状态 |
|---|---|---|
| `GetCartDataList` | `shoppingCartDataList` | **已实现** `GetCartAsync` |
| `FetchCoupons` | `coupons/list` | **已实现**（私有 helper，由购物车读取调用） |
| `SubmitDiscount` | `coupons/verify` | **已实现** `SubmitDiscountAsync` |
| `ClearCart` | —— | **不实现**：端点族里没有 |
| `FetchAddress` | —— | **不实现**：端点族里没有 |

### 为什么 `FetchCoupons` 是 helper 而不是 step

`StoreFlow` 的步骤词表里**没有** `FetchCoupons` 这个虚方法。为了把行为做出来而去**发明一个 step**，
等于往词表里塞一个二进制从没要求过的东西 —— 所以它是私有 helper，由购物车读取调用，
**行为存在，虚构的 step 不存在**。

### 一个行为上的变化

改动前：商品 → 加购 → 直接下单，**从不读自己刚建的购物车**，所以优惠券和地址根本无法影响订单。
改动后：`GetCart → FetchCoupons → SubmitDiscount → 下单`，顺序与购物车类一致
（测试断言 coupons 调用在 cart 之后）。

### 优惠券被拒不是失败

```csharp
c.Session.Vars["discount"] = "absent" | "applied" | "rejected";
return StepOutcome.Success();   // 三种都算走完了
```

一个用不上的券**不会让购物车不可下单** —— 这是 R99「没有这个功能 ≠ 这个功能失败了」的同一条原则。
测试断言 `SubmitDiscountAsync` 体内**没有** `StepOutcome.Fail`。

## Demandware 双路不是「两条完整路径」（第 124 轮）

把 15 条双路步按「有没有端点」切开，得到三段 —— 而**切出来的形状本身就是结论**：

| 半边 | 步 | 端点 |
|---|---|---|
| **App 有端点** | `StartAppFast`、`StartAppSafe` | `/scapi/ShopperLogin/getAccessToken` |
| | `AddToCartApp` | `/scapi/ShopperBaskets/addItemToBasket` |
| **Dw 有端点** | `GetSessionDw`、`GetCartDw` | `Cart-Get` |
| | `AddToCartAppDw` | `Cart-AddProduct` |
| **App 无端点** | `ApplyDiscountApp`、`GetCheckoutApp`、`GetRatesApp`、`SubmitOrderApp` | **没有** |

### 关键事实：**SCAPI 族里没有下单端点**

镜像里的 SCAPI 只有六个 `ShopperBaskets` 调用（create / add / update ×4）和两个 `ShopperLogin` 调用。
**没有任何一个调用会创建订单。**

所以：

> **从 app 路开始的店，没法在 app 路上结束 —— 必须切回经典控制器去结账和下单。**

这正是「15 步里同时养着 App 和 Dw 两套词」所描述的形状。
也解释了那四个 `*App` 无名端点的步：它们是**店铺自己的端点**（app 调 storefront 代理），
所以 SCAPI 族里当然没有它们。

### 对 replica 的影响

`SubmitOrderAsync` 现在**只有经典路径** —— 这是对的，不是漏了。
要给 app 路接下单，就得发明 `/scapi/ShopperOrders/createOrder`，而镜像里没有这个东西。

`ScapiAppPathTests.ThereIsNoScapiOrdersEndpoint` 断言：
**SCAPI 族里任何一条都不含 "Order"**，而经典侧有 `PlaceOrder`。

## 第六个流程：Adyen/PayPal 快捷结账（第 125 轮）

上一轮说「下一步去查那四个无端点 app 步」。这一轮问了更根本的问题：**SCAPI 族是不是我记全了？**

### 两个结果，来自同一个问题

**结果一（否定，确认 R124）**：`/scapi/` 一共 **9 条** —— 7 个 `ShopperBaskets`（create / add /
update ×5）+ 2 个 `ShopperLogin`。**没有下单，没有优惠券。** 所以那四个 app 步确实无端点。

**结果二（新发现）**：一条相邻字面量里藏着一个**全新的流程**：

| 序号 | 步 |
|---|---|
| 33 | `AdyenSession` |
| 34 | `SubmitPaymentPayPal` |
| 35 | `AdyenPayPalPatchOrder` |
| 36 | `GetPayPalAccessToken` |
| 37 | `AdyenSaveExpressShopperDetails` |
| 38 | `ShowConfirmationPaymentFromComponent` |

### 读法：又用上了 R119 的教训

字面量的第一个 token 是 `<PlaceOrder>d__32` —— **它属于前一条字符串的尾部**。
照字面读会得到「7 步 + 一组不能升序的序号」；去掉尾巴才是 **6 步，序号 33–38 完全连续**。

> `TailToken` 常量把这件事写在代码里，测试断言 `PlaceOrder` **不是**这个流程的步。

### 与 R124 正好相反的形状

| 路 | 能不能在一侧走完 |
|---|---|
| Demandware app 路 | **不能** —— 只到购物车，必须切回经典 |
| **Adyen/PayPal 快捷路** | **能** —— 六个步全在一侧，序号连续无缺口 |

### 顺带补进词表的两个控制器

```
Adyen-SaveExpressShopperDetails      ← 步骤 37 的落地端点
ShopperInfo-IP                        ← 风险检查读的 shopper IP 端点
```

`Adyen-SaveExpressShopperDetails` 这个控制器**在本会话的表里从来没出现过** ——
和 R117 的 `CheckoutServices-SubmitBilling` 是同一种遗漏：表是窗口读出来的，窗口外还有东西。

## 控制器族普查：又短了一截，而且池子会「粘」字（第 126 轮）

用「记全了吗」去查控制器族，得出两件事。

### 一、表又短了 —— 这次找到 5 个

```
Cart-UpdateProduct            Cart-ShowLayer
Adyen-PaymentFromComponent    Adyen-PayPalPatchOrder    Adyen-Authorize3DS2
```

这已经是**第三次**同型遗漏（R117 `CheckoutServices-SubmitBilling`、R125
`Adyen-SaveExpressShopperDetails`、R126 这五个）。

> **「表是窗口读出来的」不是运气问题，是方法问题。** 只要还是「读一段就记下来」，
> 就会继续短。这一轮之后控制器词表 **33 条**。

### 二、池子里的名字会带「粘连尾巴」

裸扫 `Prefix-Name` 得到 **94 个**「控制器」，但里面大量是粘连变体：

```
Cart-AddProduct      ←→  Cart-AddProducton
Cart-MiniCartShow    ←→  Cart-MiniCartSh92000052on
Cart-AP              ←→  Cart-APon / Cart-APs
Cart-EditProductLineItem ←→ Cart-EditProductLineIteon
```

原因：**池子里字符串和元数据交错存放**，一个真名字后面可能紧跟着别的字节，
拼出来就是「真名 + on」「真名 + 92000052」这种尾巴。

所以真实数量接近 33，不是 94。**过滤规则是「尾巴得像个方法名的词」—— 这是判断，不是测量**，
代码里标成判断（`TheTableKeepsNoMangledNames` 断言这些粘连变体**不在**词表里）。

### 三、顺手修的一个测试坏习惯

我原本写 `Assert.Equal("CheckoutServices", families[0].Key)` —— **凭记忆指定「最大的族」**。
实测 `CheckoutServices` 是 7 条，而它并不是最多的那个。

这已经是**第五次**在断言里手写数字/名字。改成结构化断言：

```csharp
var biggest = families[0].Count();
Assert.Equal(families.Max(f => f.Count()), biggest);   // 最大的确实是最大的
foreach (var needed in new[] { "CheckoutServices", "Adyen", "Cart" }) …
```

> **测试里不要写「我认为答案是多少」，要写「答案和它的来源一致」。**

## 更正：`/v5/Order/` 是 **Nike** 的，不是 Scheels 的（第 127 轮）

用「这个族记全了吗」做普查，第一条就抓到**我自己造出来的端点**。

### 事情经过

R115 我记了 Scheels 移动 API 的第三个端点：

```csharp
public const string Orders = Base + "/v5/Order/";     // ← 拼出来的
```

理由是「见过一个 `/v5/Order/` 路径」。R127 普查把全库 `v5/Order` 找了一遍，只有一条字面量：

```
https://www.nike.com/gs/checkout-api/api/v5/Order/
```

**是 Nike 的，而且是 Nike 的下单端点** —— 本会话从 R87 起一直问「Nike 的订单打到哪」，
答案就在这儿：不在 `api.nike.com`，而在 `www.nike.com/gs/checkout-api/api`（游客结账代理），
所以它从没出现在 `api.nike.com` 那 19 条里。

### 三处修正

| 位置 | 修正 |
|---|---|
| `ScheelsMobile` | 3 端点 → **2 端点**（`v5/auth/guest`、`v5/products/`） |
| `DualApi.AppSteps` | `SubmitOrderApp` 的映射**删除**（目标不存在了），该步回到未映射 |
| `NikeEndpoints` | **新增 `OrderV5`** —— Nike 的下单端点 |

### 这是第几次同类错误

「凭见过的片段拼一个端点出来」：

| 轮次 | 编出来的东西 | 真相 |
|---|---|---|
| R87 | Nike `buy/orders/v2` | 不存在 |
| R91 | BSTN `/api/beast` | 不存在 |
| R94 | Demandware `Checkout-Submit*` | 名字不对 |
| R96 | Shopify `cart/change.js` | 不存在 |
| R100 | Pop Mart `/api/*` | 不存在 |
| **R115→R127** | **Scheels `/v5/Order/`** | **是 Nike 的** |

六次。所以这一轮把规则又说了一遍，并且这次**写进断言**：

> **一个端点的「主机 + 路径」必须来自同一条字面量。** 跨字面量拼接 = 发明。
> `TheOrderPathBelongsToNikeNotScheels` 断言 `NikeEndpoints.OrderV5` 含 `nike.com` 且**不含**
> `scheels`，同时断言 Scheels 族里**没有任何一条**含 "Order"。

### 顺带：三份普查数据

| 主机 | 不同路径数 |
|---|---|
| `apihub.scheels.com` | **17**（全在 `frontastic/action/`） |
| `mobile-api.scheels.com` | **2** |
| `checkout.johnlewis.com` | **15**（12 是 `bff/*`，另 3 条是裸路径 `/callback/login/guest?email=`、`/delivery`、`/payment`） |
| `api.nike.com` | **19**（`payment/*`、`buy/*`、`deliver/*`） |
| `api2.endclothing.com` | **2** |

**John Lewis 那 15 条里，`/callback/login/guest?email=` 是表里没有的** —— 又一个「窗口外」。

## 溯源闸门：端点必须**逐字**出现在镜像里（第 128 轮）

上一条规则（「主机 + 路径必须来自同一条字面量」）这一轮变成了**机械检查**。

### 工具：`tools/endpoint-provenance.py` → 验证第 8 步

它做两件事：

1. 把 `src/Cybersole.Stores/Flows/*.cs` 里所有**端点常量**找出来；
2. 把 `Base + "/path/"` 这种**拼出来的**常量按嵌套类作用域**解引用成完整值**，
   然后逐字到 `analysis/pe_strings.txt` 里找。

```
endpoint constants: 159   verbatim in pool: 159   invented: 0   unresolved: 0
```

**159 / 159 逐字命中，0 编造。** 这条现在是 `verify-steps.ps1` 的第 8 步。

### 写这个工具时踩的两个坑（都是「我的检查器坏了」，不是端点坏了）

**坑一：把字典当列表迭代。** `for name, value in plain:` 对着 dict 跑，直接
`ValueError: too many values to unpack`。

**坑二（重要）：嵌套类共享常量名，扁平解析会串味。**

`RetailApiFamilies.cs` 里 `ScheelsFrontastic` 和 `JohnLewisBff` **各自**声明了一个 `Base`。
我把整个文件当一个作用域收集常量，字典 last-wins，于是 John Lewis 的路径被拼到了
Scheels 的主机上，报出 13 条假的「编造」。

修法：**先把嵌套类区间从外层文本里挖空**，再收集本层常量，解析时按「内层 → 外层」查。

```
修前：invented: 19      修后：invented: 0
```

> **检查器自己错了，比被检查的代码错了更危险** —— 它会让你去「修」本来正确的代码。
> 所以这一轮我改了两次工具，一次也没有动端点。

### 与 GUI 的关系

这一轮没用 GUI。它是纯字节侧的闸门 —— **GUI 无法回答「这个端点是不是我拼出来的」**，
因为界面上两个端点看起来都只是「一个设置项」。

## 常量干净不等于代码干净：**202 条内联字面量里 29 条不在镜像里**（第 129 轮）

第 128 轮的闸门只查 `public const string`，报「159/159 逐字命中」。这一轮把范围扩到
**方法体里的内联字面量**，结果立刻不一样：

```
endpoint constants:            160     verbatim in pool: 160    invented: 0
inline URL/path literals:      202     not in pool: 29
```

### 一、当场抓到一条：Nike 的下单

`NikeFlow.SubmitOrderAsync` 里写着

```csharp
$"https://api.nike.com/buy/orders/v2/US/{c.Session.CartId}/submit"   // ← R87 的发明，一直在代码里
```

**常量扫描看不见它**，因为它不是常量。R127 找到的 `NikeEndpoints.OrderV5` 才是镜像里那条。
现在改成 POST `OrderV5`，cartId 放 body（路径里没有位置放它）。

### 二、三类溯源，缺一不可

| 类 | 含义 | 例子 |
|---|---|---|
| `literal` | 逐字出现在镜像里 | `OrderV5`、`bff/v2/orders` |
| `live` | 镜像里没有，但**真实响应过** | BSTN `/api/beast`（R91 实测该前缀会应答） |
| `fixture` | **故意保留的不存在路径**，用测试禁止 | Pop Mart `/api/cart/add` 等三条（R100） |

「三者都不是」= 发明。台账写在 `docs/ENDPOINT_PROVENANCE.md`。

### 三、闸门改成「不许增长」而不是「必须为零」

剩下 **24 条待定**（Farfetch、Goat、HBX、Hybris、Magento、RetailFlows、Scheels、StoreFlow 等）。
一条条查清要好几轮，所以第 8 步的门槛是：

```
unknown (invented and unregistered): 24   baseline: 24     → PASS
超过 baseline → exit 1
```

**这是棘轮：只许往下走。** 每轮清掉几条就把 baseline 调低。

### 四、为什么不用「必须为零」

如果现在就把门槛设成 0，第 8 步永远是红的 —— **一条永远红的检查等于没有检查**
（这正是 R108 那轮「整轮跑不完」的教训）。棘轮能保证「不再变坏」，同时留下可见的清单。

### 五、这一轮的一句话

> 上一轮我以为闸门做完了，因为常量 159/159 干净。
> 这一轮把范围一扩，**29 条不在镜像里，其中一条正是我自己在 42 轮前编的 Nike 下单路径。**
>
> **「我检查过了」这句话，永远要跟着「我检查的是哪一部分」。**

## 每个 profile 一套指纹：镜像里的 `Fingerprint.template.json`（第 130 轮）

YG 指出原版有「不断生成新 Chrome profile」的机制，用来做出不同指纹，配合 Kasada token 与高并发。
**镜像里有完整的证据**，而且 replica 之前缺的正是这一半。

### 一、证据

一条元数据运行把 `Fingerprint` 类的字段列了出来：

```
<ColorDepth>k__BackingField            <DeviceMemory>k__BackingField
<HardwareConcurrency>k__BackingField   <PixelRatio>k__BackingField
<ScreenWidth>k__BackingField           <ScreenHeight>k__BackingField
<AvailableScreenWidth>k__BackingField  <AvailableScreenHeight>k__BackingField
```

旁边还有：

| 字面量 | 含义 |
|---|---|
| `Fingerprint.template.json` | **模板文件** —— 指纹不是随机的，是从模板填出来的 |
| `Fingerprint`（77 次） | 类/字段名 |
| `--profile-directory=`、`user-data-dir` | Chromium 开关 |
| `Profile 0` / `Profile 1` / `Profile 6` / `Profile 8` | **编号的 profile 目录** |
| `--window-size=363,684` | 一个实测窗口尺寸（偏窄，像真实小屏） |
| `set_ColorDepth` / `set_DeviceMemory` / `set_HardwareConcurrency` | 这些值是被**写进**浏览器的 |
| `x-kpsdk-v/-cd/-ct/-dt/-dv/-fc/-h/-im` | Kasada 的 8 个头 |

**结论：模板 → 每个 profile 一份指纹 → 每个 profile 一个 Chrome 身份 → 每个身份单独出 token。**

### 二、replica 之前的样子

```csharp
Object.defineProperty(N, 'hardwareConcurrency', { get: () => 8, configurable: true });
Object.defineProperty(N, 'deviceMemory', { get: () => 8, configurable: true });
```

**两个值所有 run 都一样**，而且六个 screen 字段**根本没设**。

> 指纹检查最先看的就是这个：**同一个安装里两个会话报告完全相同的硬件**，
> 比「没有伪装」更容易被识别 —— 因为真实用户不会这样。

### 三、这一轮做的

`BrowserFingerprint`（8 个字段，与镜像一致）：

- `ForProfile(key)` —— **按 profile key 确定性生成**：同一个 profile 永远同一套指纹
  （指纹在两次请求之间变化是比不伪装更大的破绽），不同 profile 拿到不同屏幕/硬件；
- `ToJavaScript()` —— 把 8 个字段全部注入（含 `screen.availWidth/availHeight`、`pixelDepth`、
  `devicePixelRatio`）；
- `ProfileDirectoryName(key)` —— `Profile 0..8`，与镜像的编号目录同形；
- `WindowSizeArgument()` —— 窗口尺寸跟着屏幕走，**不再固定 1280×900**（那和 1920×1080 的屏幕对不上）。

`ChromiumBridge` 现在：

```
var fingerprint = BrowserFingerprint.ForProfile(profile);
args: fingerprint.WindowSizeArgument(), fingerprint.ProfileDirectoryArgument(profile)
inject: StealthScript.Replace("__HC__", …).Replace("__DM__", …)
ApplyStealthAsync(…, BrowserFingerprint? fingerprint = null)   // 无 profile 时按 UA 派生
```

### 四、为什么「每个 profile 一套」比「每次随机」更强

| 做法 | 检测者看到 |
|---|---|
| 每次随机 | 同一账号两次请求硬件不同 → **明显异常** |
| 全部固定 | 所有账号硬件相同 → **农场特征** |
| **每 profile 一套、profile 内不变** | 像一群真实用户，各自一台机器 |

第三种才是原版的做法，也是 `Fingerprint.template.json` 存在的理由 —— 模板保证**多样性有边界**
（四个真实屏幕尺寸、四组硬件），不会随机出「1373 宽 / 1920 可用」这种自相矛盾的组合。

### 五、还没做的

- 模板文件本身没有从镜像里还原出来（只确认了文件名与字段集），现在是代码内置的四屏四档；
- `maxTouchPoints` 仍固定 0（桌面口径），镜像是否按 profile 变化未查证；
- 语音列表、WebGL vendor 这些已有伪装，但**没有跟随 profile 变化**。

## `%TEMP%\cyb-chromium-*` 是谁造的：不是原版（第 130 轮补充）

YG 在 `%TEMP%` 看到 **115 个 `cyb-chromium-<8位hex>`** 和 **14 个 `cyb-missing-<32位hex>`**，
问是不是反编译里看不懂的代码来自这里。查清了：**是 replica 自己造的，不是原版。**

| 目录 | 制造者 |
|---|---|
| `cyb-chromium-<8 hex>` | `ChromiumBridge.cs:56` —— `"cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]` |
| `cyb-missing-<32 hex>/h.json` | `CheckoutHistoryTests` 传入一个**不存在目录**下的 `h.json`，而 `CheckoutStats.Flush()` 在 `Dispose` 时**建目录并写入 `[]`** |

原版把浏览器 profile 放在**它自己的数据目录**里，不会用 `cyb-` 前缀。

### 但这条线索抓出了三个真问题

**① `CheckoutStats.Flush()` 有副作用**：空历史 + 文件不存在时仍然建目录、写 `[]`。
一次「打开设置页看一眼」也会落地一个目录；在只读安装上则变成被 `catch` 吞掉的异常。
现在：`_events.Count == 0 && !File.Exists(...)` 直接返回，测试断言**目录不存在**。

**② 1.8 GB 临时垃圾**：129 个目录，`tools/clean-temp.ps1` 已清掉（C: 可用空间随之大涨）。

**③ 一份被遗弃的「变异」**：`ChromiumBridge.cs` 里留着
`var fullVersion = "131.0.0.0";  // MUTATED` —— 那是 `mutation-check.py` 被中途杀掉时留下的。
它让 `UserAgentConsistencyTests` 一直红，而我差点把它当成新回归去查。
现在 `mutation-check.py` **每轮开始先自修复**：变异前把原文件存到 `tools/.mutation-backup/`，
下轮启动时发现文件里还有 `MUTATED` 就从备份还原。

> **一个被杀掉的检查，会留下它正在检查的那个错误。** 这比它自身的失败更难发现。

### 顺带修的一个资源问题

清理后全量重建暴露：`Cybersole.Core.csproj` 里 `Cybersole.Locales.ja.json` **缺
`WithCulture="false"`**，于是它被当成 `ja` 卫星程序集，主程序集只剩 3 个资源字典
（`LocaleDictionaryTests` 期望 4）。补上即绿 —— 正是该 csproj 注释里警告过的那个坑。

## 更正：指纹是**三层**，`Fingerprint.template.json` 属于 3DS 那层（第 131 轮）

R130 我把 `Fingerprint.template.json` 当成「浏览器指纹模板」。这一轮按资源全名查下去，**错了**。

### 资源全名

```
Cybersole.Core, Version=5.18.32.0, Culture=neutral, PublicKeyToken=null
  Cybersole.Helpers.Dlpa.Fingerprint.template.json
```

**命名空间是 `Dlpa`** —— 不是浏览器相关的命名空间。

### 它填的是一份 3-D Secure 设备画像

同一条字面量里的字段是支付方案的（EMVCo / 3DS2）口径：

```json
{"fingerprintAttempted":false,"fingerprintData":null,"challengeWindowSize":null,
 "threeDSCompInd":"Y","browserJavaEnabled":false,"browserJavascriptEnabled":true,
 "browserLanguage":"en-US","browserColorDepth":"24","browserScreenHeight":"1440",
 "browserScreenWidth":"5120","browserTZ":"-60","browserUserAgent":"…"}
```

注意 **`browserScreenWidth":"5120"`、`browserTZ":"-60"`** —— 值都是**字符串**，
而且 5120×1440 这种超宽屏正是「设备画像」要报的东西。

### 于是三层，不是一层

| 层 | 内容 | 谁在用 |
|---|---|---|
| **browser** | 8 字段（ColorDepth / DeviceMemory / HC / PixelRatio / Screen*） | 每个 Chrome profile（R130 已实现） |
| **payload** | `fingerprint-v1` 与 **`fingerprint-v1-sans-ua`** 两个变体 | 反爬脚本，按「UA 是否已在别处发送」二选一 |
| **dlpa** | 3DS 设备画像（`Fingerprint.template.json`） | **每一次支付** |

`fingerprint-v1-sans-ua` 这个名字本身就是一条结论：**同一个 payload 有「带 UA」和「不带 UA」两种发货方式**，
不是版本号，是调用方的选择。

### 对 R130 的影响

R130 的实现（`BrowserFingerprint`，每 profile 一套）仍然成立 —— 只是它属于**第一层**，
不是模板生成的。模板生成的第三层（3DS 画像）**还没实现**：支付时需要一份与浏览器层
**不矛盾**的画像（屏幕尺寸、色深、时区要和浏览器一致，否则同一笔支付自相矛盾）。

### 这一轮的一句话

> 「模板 → 指纹」这个理解很顺，顺到我根本没去读资源的全名。**读了一下全名，结论就变了。**
>
> **文件名和命名空间是零成本证据，而我总是先猜语义再去找证据。**

## 第三层落地：3DS 画像**从浏览器指纹派生**（第 132 轮）

`DlpaProfile` 不是「另建一套值」，而是**从 `BrowserFingerprint` 推导**：

```csharp
DlpaProfile.From(fingerprint, utcOffsetMinutes, userAgent, language)
```

| 字段 | 来源 |
|---|---|
| `browserColorDepth` | `fingerprint.ColorDepth` |
| `browserScreenWidth` / `Height` | `fingerprint.ScreenWidth` / `ScreenHeight` |
| `browserTZ` | **分钟数**（`60` = UTC+1，与实测样本 `-60` 同口径） |
| `browserLanguage` | `en-US` |
| `browserUserAgent` | 传入的 UA，`-sans-ua` 时**整条不出现** |
| `threeDSCompInd` / `fingerprintAttempted` | 常量 `Y` / `false` |
| `challengeWindowSize` | `null`，直到选定挑战窗口 |

### 为什么必须「派生」而不是「拼装」

支付画像与浏览器**不一致**会被方案的risk engine 拒，而拒的样子和「卡被拒」一模一样 ——
**排查时根本分不出来**。所以：

```csharp
public bool AgreesWith(BrowserFingerprint fingerprint)
```

测试 `AProfileCannotDisagree`：用 `with { BrowserScreenWidth = "5120" }` 造一个不一致的画像，
断言 `AgreesWith` 为 false —— **能造出来，但会被抓住**。

### 两层的边界，用测试钉住

`TheLayersDoNotBleed` 断言 DLPA 里**没有** `HardwareConcurrency` / `DeviceMemory` / `PixelRatio`
—— 那是浏览器层的字段，混进来就说明实现串层了。

### `-sans-ua` 只影响一个字段

`TheSansUaPayloadDropsOnlyTheUserAgent`：带 UA 版 12 个键，不带版 11 个，
**其余每个值逐一同值**。这保证了两个变体描述的是同一台设备，只是 UA 的发送位置不同。

## 三层从「有」到「用」：Adyen 的 `browserInfo` 不再写死（第 133 轮）

`AdyenGateway` 以前这样发支付：

```csharp
["colorDepth"] = 24, ["screenHeight"] = 1080, ["screenWidth"] = 1920, ["timeZoneOffset"] = 0,
```

**每个支付都发同一组值。** 而 3DS 风险引擎第一件事就是把这四个数和「做出这笔请求的浏览器」对比。

> 不一致就拒，而且**拒的样子和「卡被拒」一模一样** —— 所以它从来不会看起来像这一层的 bug。

### 现在

```csharp
["browserInfo"] = BrowserInfo(c),                     // 从 fingerprint 派生
["threeDS2RequestData"] = new JObject {
    ["threeDSCompInd"] = DlpaProfile.From(FingerprintFor(c), TimeZoneOffset(c)).ThreeDsCompInd,
},
```

- `FingerprintFor(c)` 先看会话里的 `browser.fingerprintKey`（浏览器桥写入），没有再按 UA 派生；
- `TimeZoneOffset(c)` 读 `browser.timezoneOffsetMinutes`；
- `BrowserInfo` 与 `DlpaProfile` **同源**，所以同一笔支付的两套描述不可能互相矛盾。

### 测试钉住的是「字面量不许回来」

`AdyenBrowserInfoTests` 断言源码里：

```
不存在  ["screenHeight"] = 1080
不存在  ["screenWidth"] = 1920
不存在  ["colorDepth"] = 24
不存在  ["timeZoneOffset"] = 0,
存在    ["screenHeight"] = fingerprint.ScreenHeight  …
```

**这个缺陷的形态就是「本该派生的地方写了个常量」**，所以测试直接盯这个形态，
而不是跑一次支付看结果 —— 因为结果永远长得像「被拒」，看不出是这里错。

### 这一轮的一句话

> 三层数据我做完了两层才想起来问：**它们接进真实请求了吗？**
>
> 答案是：没有。`browserInfo` 还写着 `1080/1920`，而我上一轮刚写完「画像必须与浏览器一致」。
> **写完规则不等于执行了规则 —— 中间隔着一次「去把它接上」。**

## 闭环：终于有东西**写**那三个会话键了（第 134 轮）

R133 教会网关**读** `browser.fingerprintKey` / `browser.timezoneOffsetMinutes`，
但工作区里**没有任何地方写它们** —— 读端存在、写端不存在，每次支付都退回按 UA 派生。

### `BrowserIdentity`：唯一写入者

```csharp
BrowserIdentity.Record(session, "task-9/profile-2", utcOffsetMinutes: 60);
// 写入三个键：
//   browser.fingerprintKey          = "task-9/profile-2"
//   browser.timezoneOffsetMinutes   = "60"
//   browser.fingerprintPayload      = "fingerprint-v1" | "fingerprint-v1-sans-ua"
```

三个键**一起写、一起读**，因为只有一个理由让它们分开：**它们只在同时正确时才有意义**。

### 为什么 key 必须是「同一条」

```csharp
var launcherFingerprint = BrowserFingerprint.ForProfile(profilePath);
BrowserIdentity.RecordProfile(session, profilePath, utcOffsetMinutes: -300);
var paymentFingerprint  = BrowserIdentity.Fingerprint(session);

Assert.Equal(launcherFingerprint, paymentFingerprint);   // LauncherAndPaymentAgree
```

**启动器用哪个 key 选屏幕，支付就必须用哪个 key 报屏幕。** 这条测试就是整条链存在的理由。

### 读端也收进同一个类

网关现在写的是 `BrowserIdentity.Fingerprint(c.Session)` / `.TimeZoneOffset(c.Session)`，
测试 `TheGatewayUsesTheSingleWriter` 断言网关里**不再出现** `"browser.fingerprintKey"` 这种字面量 ——
**一个键只有一种拼法**。

### 这一轮的一句话

> 上一轮我发现「规则没被执行」。这一轮发现更深一层：**读的人有了，写的人根本没有。**
>
> **一个只被读取的变量，不是配置，是悬念。**

## 三层的来源终于接上了：Kasada 求解器就是身份的出生地（第 135 轮）

整条链现在读得通了：

```
ChromiumBridge.LaunchAsync
   ├─ 建 profile 目录           →  ProfilePath
   └─ BrowserFingerprint.ForProfile(ProfilePath)
          ↓
ChromiumKasadaSolver.SolveAsync(…, FlowSession? session)
   ├─ ProfileKey = bridge.ProfilePath
   └─ BrowserIdentity.RecordProfile(session, bridge.ProfilePath, …, userAgentAlreadySent: true)
          ↓
AdyenGateway.BrowserInfo(c)
   └─ BrowserIdentity.Fingerprint(c.Session) → 同一个 key → 同一块屏幕
```

**在这之前，第一步对后两步是不可见的** —— token 求解所用的身份与支付所描述的身份
可以完全不同，而且**没有任何东西会报错**。

### 为什么 `userAgentAlreadySent: true`

求解器自己把 UA 发给页面（`ApplyStealthAsync` 会重写 UA 并注入），所以它记身份时选
`fingerprint-v1-sans-ua` —— **同一份 UA 不发两遍**，也不假设对方会去别处找。

### 测试的四条

| 测试 | 断言 |
|---|---|
| `TheSolverRecordsTheIdentity` | 记身份发生在 `NavigateAsync` **之前** |
| `TheBridgePublishesItsIdentity` | 桥暴露 `ProfilePath` / `Fingerprint` |
| `TheResultCarriesTheKey` | 无会话的调用方也能拿到 `ProfileKey` |
| `OneKeyOneFingerprintOneProfile` | 一个 key → 一个指纹 → 一份一致的 3DS 画像 |

### 这一轮的一句话

> 三层数据我做了四轮：先证明它们存在，再各自建类，再接线，再让写端存在。
> 这一轮才把「谁生成身份」和「谁使用身份」连成一条线。
>
> **数据模型正确，不等于数据流正确。**

## Kasada 是**四条路**，replica 只有一条（第 136 轮）

回到反编译主线，把原版的 Kasada 状态字符串全捞出来 —— 立刻发现我建的东西只覆盖了四分之一。

### 一、字符串就是证据

```
IKasadaSolver                       ← 一个接口，所以求解器是可插拔的
Getting Kasada ( / (1) / (2)        ← 「取」：向服务要
Getting Kasada (MFC)                ← 移动回退路上取
Failed getting Kasada               ← 「取」失败
Failed getting Kasada (Rotating)    ← 取失败 + 代理正在轮换
Failed solving Kasada               ← 「解」失败（跑页面）
Failed solving Kasada (TL)          ← 解失败于 TL 环节
Failed Kasada (Retry limit reached) ← 整条策略放弃
Kasada API down (Contact staff)     ← 服务不可达 —— 这是**运维问题**
Kasada-Fallback / Kasada-Mobile-Fallback   ← 两个**具名**回退
```

### 二、两处纠正

**① 「getting」和「solving」是两个动词。** 取 = 向远端服务要；解 = 跑页面。
`Kasada API down (Contact staff)` 只在一个**存在远端服务**的世界里讲得通 ——
而 replica 只有本地浏览器求解（`ChromiumKasadaSolver`）。

**② 回退是具名的**，所以调用方**知道**自己拿到的是哪一路。replica 之前没有这个概念。

### 三、四种模式

| 模式 | 动词 | 依据 |
|---|---|---|
| `Api` | getting | `Getting Kasada (…)`、`Kasada API down` |
| `Local` | solving | `Failed solving Kasada` |
| `Fallback` | falling back to | `Kasada-Fallback` |
| `MobileFallback` | falling back to | `Kasada-Mobile-Fallback`、`(MFC)` |

配 `IKasadaSolver` 接口（镜像里就声明了它）—— `ChromiumKasadaSolver` 只是**其中一种实现**。

### 四、版本头是**每店一个**，不是一个常量

```
Nike-Kasada-Version   Footsites-Kasada-Version   Scheels-Kasada-Version
Converse-Kasada-Version   Crocs-Kasada-Version (+ EU / JP)
```

七个。所以它是表，不是常量 —— 这也解释了为什么 Nike 那个常量在 `NikeHeaders` 里而不是全局。

### 五、8 个协议头

`x-kpsdk-ct / cd / dt / dv / fc / h / im / st` —— 比之前记的多出 **`st`**。

### 六、这一轮的一句话

> 我一直以为「Kasada 求解」就是一件事。字符串告诉我它是一条**策略**：
> 先取、再解、再回退，回退还有两条。
>
> **我把一条策略实现成了一个函数，然后以为这就是全部。**

## 四条路落成代码：`IKasadaSolver` + 三个实现 + 一个 runner（第 137 轮）

上一轮只是把字符串记成表。这一轮把它变成可执行的东西。

### 一、接口和四个实现

```csharp
public interface IKasadaSolver {
    KasadaStrategy.Mode Mode { get; }
    Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default);
}
```

| 实现 | 模式 | 它做什么 |
|---|---|---|
| `ApiKasadaSolver` | `Api` | 向服务要；**地址靠注入** |
| `LocalKasadaSolver` | `Local` | 包住现有的 `ChromiumKasadaSolver` —— 只加接口，不加逻辑 |
| `NamedFallbackSolver(Fallback)` | `Fallback` | 报告 `Kasada-Fallback` |
| `NamedFallbackSolver(MobileFallback)` | `MobileFallback` | 报告 `Kasada-Mobile-Fallback` |

`KasadaToken` 把 **token 与来源模式绑在一起** —— 调用方必须知道拿到的是哪一路，
因为回退 token 能用，但它和「解出来的」不是一回事。

### 二、`ApiKasadaSolver` 为什么不写地址

字符串证明**存在远端服务**（`Kasada API down (Contact staff)` 不可能是本地失败的消息），
但**没有给出地址**。所以：

```csharp
public ApiKasadaSolver(string? endpoint = null, Func<…>? call = null)
public bool IsConfigured => !string.IsNullOrEmpty(_endpoint) && _call is not null;
```

未配置时直接返回 `Kasada API down (Contact staff)` —— **用镜像自己的运维文案，而不是编一个主机名**。
这和 `endpoint-provenance.py` 是同一条规矩。

### 三、runner 的顺序与放弃

```
Api → Local → Fallback → MobileFallback
```

「取」在「解」前面：取便宜，而且镜像给尝试编了号（`Getting Kasada (1)`、`(2)`）——
**编号只有在先试、且会重试时才有意义**。回退放最后，因为回退 token 是没人想要的东西。

全空时返回镜像自己的放弃文案，并把**经过的每条状态串起来**：

```
Failed getting Kasada | Failed solving Kasada (TL) | Kasada-Fallback |
Kasada-Mobile-Fallback | Failed Kasada (Retry limit reached)
```

### 四、八条测试

覆盖：顺序、第一个可用即止（后面的路**不被调用**）、回退 token 自带名字、
全空放弃串、未配置 API 的运维文案、配置后能出 api token、回退不许冒充别的模式、四个实现覆盖四种模式。

### 五、这一轮的一句话

> 上一轮我说「我把一条策略实现成了一个函数」。这一轮把它拆回策略：
> **接口 + 四个实现 + 一个 runner，每段都能单独测。**
>
> **承认结构缺失，比补上结构难 —— 因为承认的时候，代码看起来是能跑的。**

## Cloudflare 是**同一条梯子**：服务 → in-bot（第 139 轮）

上一轮我说 `Cloudflare solver refused the token, solving in-bot` 与 Kasada 的 `Api → Local`
「是同一条策略的两个实例」。这一轮把它变成代码，验证这句话。

### 一、两个模式，一条梯子

| 模式 | 谁干活 | 地址 |
|---|---|---|
| `Service` | `cf-solver.cybersole.io` | **有**（十五个主机之一） |
| `InBot` | 已开着页面的浏览器 | 无（本地） |

```csharp
CloudflareStrategyRunner.Default(serviceCall, inBotSolve)
// 顺序：Service → InBot
```

**拒绝不是错误，是继续往下走的理由** —— 所以 runner 把 `RefusedMessage` 当**状态**返回，
而不是失败。

### 二、与 Kasada 对齐的地方

| 维度 | Kasada | Cloudflare |
|---|---|---|
| 服务路 | `Api`（地址**缺**，候选 `api.cybersole.io`） | `Service`（地址**有**） |
| 本地路 | `Local` | `InBot` |
| 额外路 | 两个具名回退 | 无 |
| 接口 | `IKasadaSolver` | `ICloudflareSolver` |
| 拒绝文案 | `Failed getting Kasada` | `Cloudflare solver refused the token, solving in-bot` |

`CloudflareAndKasadaHaveTheSameShape` 断言两者**服务在前、本地在后** —— 这就是那条原则。

### 三、协议是注入的，主机是记录的

服务的**协议**镜像里没有，所以 `ServiceCloudflareSolver` 的调用是注入的；
但它的**主机**有 —— `cf-solver.cybersole.io`，而且 `CybersoleHosts.WallFor` 能说出它解的是 Cloudflare。
**能和不能，分得清清楚楚。**

### 四、cookie 与注册表

- `cf_clearance` —— 与 `AntiBotProtocol.CookiesFor("Cloudflare")` 一致（测试对得上）；
- 设置页那六个名字（`CloudflareSolvers` / `CloudflareSolverId` / `CloudflareSolver.Default` /
  `CapSolver` / `CloseSolver` / `EmptySolver.html`）已入表。

### 五、这一轮的一句话

> 上一轮我把一句话当成**证据**。这一轮把它当成**规格**：照着它写出两个模式和一条顺序，
> 然后测试确认「服务在前、本地在后」。
>
> **一句话可以是证据，也可以是需求 —— 区别只在于你拿它来「相信」还是拿它来「实现」。**

## 中间那段补上了：检测 → 问策略 → 写回（第 140 轮）

`StoreFlow.DetectAsync` 早就把 vendor 记进 `antibot`，`AntiBotProtocol` 早就知道
Cloudflare 的 cookie 叫 `cf_clearance` —— **但中间没有人问策略要 token，也没有人把结果写回去。**

这和 R133/R134 在支付侧发现的缺口是**同一个形状**，值得把模式说出来：

> **检测在、存储在，中间的调用不在。**

### `CloudflareClearance.ApplyAsync`

```csharp
if (!IsCloudflare(c.Session)) return StepOutcome.Success();   // 别人家的墙不管
var (token, status) = await runner.GetAsync(pageUrl, ct);
c.Session.Vars["cloudflare.solverStatus"] = status;
if (token) { c.Session.Vars["cloudflare.clearance"] = token;
             c.Session.Cookies["cf_clearance"]      = token; }
else       { c.Emit(status, "antibot"); }        // 拒绝文案照原样发出，流程继续
```

**一次写两个地方**：会话变量（给本进程看）+ cookie（给下一次请求用）。

### 一条带状态码的实测

`SESSION_STATE` 里早有一行：

```
Cloudflare JSD  cf-solver.cybersole.io  401
```

这说明**这个主机是真的、可达的**，只是拒绝未认证的调用 —— 比 Kasada 那条路强：
Kasada 连主机都认不出来。所以这里把 401 写成常量并附一句人话：

```csharp
public const int ServiceStatusObserved = 401;
public const string ServiceStatusMeaning =
    "cf-solver.cybersole.io answers 401 to an unauthenticated call: the host is real and reachable, " +
    "the protocol needs credentials this workspace does not have";
```

**「有主机、没协议」比「什么都没有」更接近能实现** —— 而且这句话能让人接着往下查。

### 五条测试

清关成功（两处都写）、拒绝（只写状态不写 cookie）、别人家的墙不碰、
401 观测已记录、以及「检测与存储本来就是现成的」这条自证。

## 六道墙的普查：检测在、存储在，**调用**在两道（第 141 轮）

上一轮发现的缺陷（「检测在、存储在，中间的调用不在」）用同一把尺子扫一遍全部六个 vendor。

| vendor | 检测标记 | cookie | 调用已接？ |
|---|---|---|---|
| **cloudflare** | `cf-chl` / `server: cloudflare` | `cf_clearance` | **是**（R140） |
| **kasada** | `kpsdk` | `kpsdk` | **是**（R141） |
| imperva | `_Incapsula_Resource` | **无** | 否 |
| datadome | `datadome` | `datadome` | 否 |
| perimeterx | `px-captcha` | **无** | 否 |
| queue-it | `queue-it` | `queue-it-set-cookie` | 否 |

### 四个缺口不是同一种缺口

| vendor | 缺的是 | 要解开需要什么 |
|---|---|---|
| **datadome** | 协议（主机已知：`datadome.cybersole.io`） | 一次抓包 —— 与 R140 之前的 Cloudflare 同型 |
| **imperva** | 连 cookie 都没有 | 先找到它的 cookie 名 |
| **perimeterx** | 镜像里就是空的 | 保持空 —— **故意留白比猜一个 `_px` 更诚实** |
| **queue-it** | 不是挑战，是**排队** | **等待**，不是求解 |

> 最后一条最容易被写错：把 Queue-it 当验证码去「解」，会把一个排队问题变成一次失败。

### `KasadaClearance`：与 Cloudflare 的修法一模一样

```csharp
if (!IsKasada(c.Session)) return StepOutcome.Success();
var token = await runner.GetAsync(pageUrl, ct);
c.Session.Vars["kasada.status"] = token.Status;
c.Session.Vars["kasada.mode"]   = token.Mode.ToString();
if (!token.Usable) { c.Emit(token.Status, "antibot"); return StepOutcome.Success(); }
c.Session.Vars["kasada.token"] = token.Token;
c.Session.Cookies["kpsdk"]     = token.Token;   // 只有当镜像确实给了 cookie 名才写
```

**token 带着它的来路（`Mode`）一起存** —— 拿到回退 token 的调用方有权知道这一点。

### 一条从三轮里长出来的规则

```
detection and storage are cheap and were already present;
the call between them is the work
```

检测和存储是最便宜的部分，而且**它们早就在那儿**；真正的工作是中间那次调用。

## 最后一层：**调用终于有人调用了**（第 142 轮）

R140 接了 Cloudflare，R141 接了 Kasada —— 两处都是**没人调用的类**。
这是同一个缺陷再下一层：**调用存在，但没有调用者。**

`DetectAsync` 是唯一知道「哪道墙挡在前面」的地方，所以它也是唯一该分派的地方。

```csharp
c.Session.Vars["antibot"] = vendor;
c.Emit($"{Name}: anti-bot = {vendor}", "detect");
return await SolveDetectedWallAsync(c, ct);
```

### 分派只覆盖审计里「已接」的两个

```csharp
if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();
```

测试 `OnlyWiredWallsAreDispatched` 与 `VendorWiring.Wired` 对得上 ——
**分派范围 = 审计说已接的范围**，两处不许各说各的。

### 没有浏览器时记录**事实**，不是失败

```csharp
if (ChromiumBridge.FindBrowser() is null) {
    c.Session.Vars["antibot.solver"] = "unavailable";
    c.Emit($"{Name}: no Chromium build, {vendor} wall left to the next attempt", "antibot");
    return StepOutcome.Success();
}
c.Session.Vars["antibot.solver"] = "available";
```

因为：in-bot 跑不起来，而服务那半没配置 —— **跑了也只会每页打一行拒绝**。
所以记 `unavailable` 让流程继续。这条能在没有浏览器的机器上被测试，所以它被测试钉住了。

### 这一轮的一句话

> 同一个缺陷我修了四轮：存储 → 调用 → 调用者 → **调用者的触发条件**。
> 每一轮它都长得像「这次真的补完了」。
>
> **「接线」不是一个动作，是一串：写端、读端、调用、触发。任何一环缺失，功能都等于不存在。**

## 原版的解墙面：12 个方法，两处纠正（第 143 轮）

回到反编译主线：把原版所有「解墙」形状的方法名捞出来。

```
DetectAsync        ← 检测步，与 replica 的 DetectAsync 同名
SolveWafAsync      ← 通用解墙（一个墙一次调用）
RemoteSolve        ← 服务那条路，独立成一个方法
SolveBotD          ← DataDome 的 BotD 挑战
SolveCptChallenge  ← 插页式挑战
SolveRecaptcha     ← reCAPTCHA
SubmitCaptcha      ← 提交半，与取挑战分开
PollCaptchaAsync   ← **轮询**：至少有一条路是异步的
GetCheckoutCaptcha ← 结账时的验证码（Adyen 3DS captcha）
Solve3DS / Solve3DSRedirect / Solve3DSToken / SolvePayPal3DS
```

### 纠正一：**DataDome 原版是解的**

R141 的普查把 DataDome 记成「有主机、无协议」就停下了。但 `SolveBotD` 就是 DataDome 自己的挑战脚本，
原版有一个以它命名的方法 —— **原版解 DataDome**。

所以缺的是**本工作区对协议的了解**，不是原版的实现。和 R127 那次「缺的控制器在我的表里」是同一种措辞：

> **缺口在我的笔记里。**

`VendorWiring` 的状态**保持不变**（本工作区确实没接上），但理由改清楚了。

### 纠正二：至少有一条路是**轮询**的

`PollCaptchaAsync` 回答了本轮另一个问题：检测之后**不一定是原地 await**。
replica 的梯子是同步的 —— 对本地浏览器求解是对的，对「稍后才回答的服务」是不对的。

### 与 replica 已实现部分的对齐

| 原版 | replica |
|---|---|
| `DetectAsync` | `StoreFlow.DetectAsync` ✅ 同名 |
| `SolveWafAsync` | `CloudflareStrategyRunner` / `KasadaStrategyRunner` ✅ 通用形态 |
| `RemoteSolve` | `ApiKasadaSolver` / `ServiceCloudflareSolver` ✅ 服务路 |
| `SolveBotD` | ❌ 缺协议 |
| `PollCaptchaAsync` | ❌ 全是同步 await |

### 这一轮的一句话

> 我以为我在查「原版怎么做的」，结果查出来的是**「我上一轮说错了一句」**。
>
> **反编译最有用的时刻，不是它告诉我新东西，是它证明我旧的话不对。**

## 轮询那条路落成代码：`PollingSolver`（第 144 轮）

上一轮从 `PollCaptchaAsync` 得出「至少一条路是轮询的」。这一轮把它做成可以用的东西。

### 为什么需要它

| 路 | 什么时候有结果 |
|---|---|
| 本地浏览器求解 | 求解完就有 —— await 是对的 |
| **服务** | 接单，**稍后**才回答 —— await 分不清「拒绝」和「还没好」 |

replica 之前全是同步 await，所以**服务第二次才回答**和**服务拒绝**在代码里长得一模一样。

### `PollingSolver`：探针 + 间隔 + 上限

```csharp
new PollingSolver(probe, mode, interval: 1s, attempts: 20)
```

- **厂商无关** —— 探针由策略给，模式由策略定，它只负责「再看一次」；
- **有上限** —— 放弃时的状态串带次数与秒数：`Polled 20 time(s) and gave up after 20s`；
- **可取消** —— `ct` 一触发立刻退出，不烧预算。

### 六条测试（间隔用毫秒，秒级完成，不假时钟）

| 测试 | 断言 |
|---|---|
| `ATokenOnTheThirdLookIsFound` | 第三次答出，状态写 `Polled 3 time(s)` |
| `AProbeThatNeverAnswersGivesUpOnBudget` | 恰好探 5 次后放弃 |
| `CancellingStopsThePoll` | 取消后不再探（≤3 次） |
| `TheBudgetIsReadable` | `Attempts` / `Interval` / `GiveUpStatus` 可读 |
| `TheModeComesFromTheStrategy` | 模式来自策略，不来自装饰器 |
| `ThePollingFactIsRecorded` | 与 R143 的 `PollCaptchaAsync` 事实对得上 |

### 这一轮的一句话

> 上一轮我读到 `PollCaptchaAsync` 这个名字，说「至少一条路是轮询的」。这一轮补上那个「轮询」。
>
> **一个方法名可以是证据，但只有把它写成方法，它才变成能力。**

## 轮询接到两条服务路上了（第 145 轮）

R144 造了 `PollingSolver`，但它没接到任何地方。这一轮把两条服务路都改成可轮询。

### 一、两个工厂方法

```csharp
ApiKasadaSolver.Polling(probe, interval, attempts)
ServiceCloudflareSolver.Polling(probe, interval, attempts)
```

一次性的调用形式**保留**（`IsPolling == false`），因为**同步应答的服务仍然存在**。
两条路现在共享同一条判断：

```csharp
IsConfigured = _polling is not null || (endpoint && call);
```

### 二、为什么轮询形式**只收探针、不收地址**

```csharp
public static ApiKasadaSolver Polling(Func<CancellationToken, Task<string?>> probe, …)
```

**探针不是地址。** 所以 R137 那条规矩（没地址就不许编主机）在轮询形式下自动成立 ——
测试 `NoAddressStillMeansNoHost` 顺带断言源码里**不出现** `https://api.cybersole.io`。

### 三、空轮询要能掉到 in-bot

`AnEmptyPollFallsThroughToInBot`：服务路轮询 3 次全空 → 梯子继续 → in-bot 拿到 token →
状态仍是镜像那句 `Cloudflare solver refused the token, solving in-bot`。

**轮询没有改变梯子的顺序，只是让「服务那一路」有了等待的能力。**

### 四、五条测试

两条路都能轮询、迟到答案仍能出 token（状态带 `Polled 3 time(s)`）、
Cloudflare 那条按字符串接口返回、空轮询掉到 in-bot、无地址不许编主机。

### 五、这一轮的一句话

> R144 造了一个零件，R145 把它装上去。这两轮的差别，就是前面四轮反复踩的那件事：
> **零件存在 ≠ 零件在工作。**
>
> 不同的是，这次我**先造零件再接**，而不是先宣称接好了。

## 挖到原版的隐身脚本本体：**WebAssembly 指纹**（第 146 轮）

本来在查 `SolveWafAsync` 挂在哪。查着查着撞到一段**带注释的注入脚本源码**，就停在它上面。

### 原文（镜像里的字符串，逐字）

```
// The challenge frame fingerprints WebAssembly directly. Its payload carries
//   ws[0] = [WebAssembly, Module.prototype, Instance.prototype, Memory.prototype, Table.prototype]
//              .map((o) => Object.getOwnPropertyNames(o).length)
// which Blink answers [19,1,2,5,5] and both iPhones that passed answer [16,1,2,6,6]. The gap is
// two features pointing in opposite directions: Chrome ships JSPI (Suspending, promising,
// SuspendError) which Safari does not, and Safari ships WebAssembly type reflection
// (Memory.prototype.type, Table.prototype.type) which Chrome does not. Dropping three and adding
// two lands on the device's numbers exactly. Only the counts are transmitted, but a type() that
// threw when called would be a worse answer than one returning the shape the proposal describes.
```

### 三件值得学的事

1. **数字是测出来的**：Blink `[19,1,2,5,5]`，通过的 iPhone `[16,1,2,6,6]`；
2. **方向相反才是要点**：Chrome 有 JSPI（三个名字），Safari 有 type reflection（两个方法）——
   所以修法不是「藏掉 WebAssembly」，而是**「让计数符合它声称的那台设备」**；
3. **stub 要回答，不能抛**：`a type() that threw … would be a worse answer` ——
   **一个会抛的方法本身就是信号**。

### replica 之前的样子

注入脚本补了 navigator / screen / WebGL，**从没碰 WebAssembly**。
于是挑战帧问这一个问题时，看到的是「声称某台设备、却答 Blink 的数字」。

### 已落成 `WebAssemblySurface`

- `BlinkCounts` / `SafariCounts` / `JspiNames` / `TypeReflectionTargets` 全部来自上面那段原文；
- `ToJavaScript()` 按原文做法：删三个、加两个非枚举方法、`name in target` 就不重复加；
- `StubRule` 把「不许抛」写成常量，测试断言脚本里**没有 `throw`**。

### 顺手记一个自己的错

`CountsDifferByTheDelta` 我第一版写成 `blink - safari == 3 - 2` ——**方向反了**。
正确的关系是：第一个数 19→16 对应「删掉三个」，而 5→6 对应「加上两个」落在另外两个原型上。
测试先红了一次才发现。

### 这一轮的一句话

> 我在查一个方法挂在哪儿，结果捡到了**原版写给人看的注释**。
>
> **带解释的代码是最好的证据** —— 它不只告诉你做什么，还告诉你作者当时在权衡什么。

## 同一段注入脚本的其余部分：**iPhone 面的六条规则**（第 147 轮）

上一轮只读了 WebAssembly 那一块。把 `0x03d29000–0x03d2c800` 整段拉出来，151 条 —— 全是带注释的脚本。
每一条注释都在说「上一版被什么抓到了」。这些理由比数字值钱。

### 一、六条规则

| 规则 | 被抓的方式 |
|---|---|
| **TouchEvent 工厂要不抛** | Blink 的 `createEvent('TouchEvent')` 抛 `NotSupportedError`；于是页面「声称 iOS 26，却报触摸创建失败」，而 `'ontouchstart' in window`、`maxTouchPoints`、`TouchEvent` 构造器**在同一份 payload 里**说的相反 |
| **`performance.memory` 要删** | Blink 独有、WebKit 从未有过；hsw 直接探 `"memory" in performance`；它在 `Performance.prototype` 上，**窗口删除和 navigator 剪枝都碰不到** |
| **Screen 只能九个键** | Blink 多 `isExtended` / `onchange`（Multi-Screen Window Placement）；hCaptcha 整个 `for (var k in screen)` 抄走，**键的数量和位置都读**；十键的 screen 配 iPhone UA 自相矛盾 |
| **outer 与 inner 必须一起改** | 只改 outer 会造出 `innerWidth > outerWidth` 与 `innerWidth > screen.width` —— **真实浏览器造不出来** |
| **frame 里别改** | 设备数字是**顶层窗口**的；frame 里真实盒子才是诚实答案；但从未显示的 frame 布局是 0×0，**0×0 比「错但合理」更糟**，所以只有真有盒子时才保留原生值 |
| **`clientWidth` 要钉住** | hCaptcha 每次滚动推 `[scrollX, scrollY, clientWidth / min(innerWidth, clientWidth), now]`；innerWidth 假、clientWidth 真 → 比例 1.2437，滚动条占 15px 后变 1.2065 —— **iOS 滚动条是浮层，从不吃布局宽度，所以「会变的比例」是伪造不了的** |

### 二、两个可以拿去别处用的句子

> **「只改 outer 不改 inner，比两个都不改更糟。」**

> **「真正泄露的不是数字，是数字在本不该变的时候变了。」**

### 三、已落成 `MobileSurface`

`ScreenWidth 402` / `ScreenHeight 874` / `ChromeHeight 190` / `ViewportHeight 684` / `DevicePixelRatio 3`、
九键 `ScreenOrder`、`BlinkOnlyScreenMembers`、`Removed`（每条带探针）、`PinnedBoxes`、
`IsImpossibleGeometry`、`ZoomRatio`、`ScrollbarTell`、`FrameRule`。

### 四、一个诚实的差异

注释里写 `1.2437`，而 `500/402 = 1.24378…` **四舍五入是 1.2438** —— 原版是**截断**不是四舍五入。
测试改成比三位小数并附说明：**这一轮要钉的是「比例会变」这个事实，不是作者的取整习惯。**

### 五、这一轮的一句话

> 这些注释不是文档，是**战报** —— 每一条都记着「上一次被谁看穿了」。
>
> **能被读到的失败，比能被抄的成功更有信息量。**

## 两层表面接进注入链，并且**按声称的引擎开关**（第 148 轮）

R146 挖出 WebAssembly 面，R147 挖出 iPhone 面 —— 两个都只是**模型**，一个都没装上去。
这一轮把两段都缝进桥的 per-realm `apply`。

### 一、为什么必须进 `apply`

因为挑战帧是**读自己那个 realm** 的 WebAssembly 和 Screen，不会去问父窗口。
桥本来就有 per-realm 结构（`apply(W)` + `PATCHED` WeakSet + frame 重放），所以两个占位符：

```
__SURFACE_DEF__     ← 在 const apply 之前
__SURFACE_CALL__    ← 在 apply 末尾（每个 realm 都过）
```

### 二、闸门才是这轮的重点

```csharp
if (MobileSurface.IsAppleUserAgent(userAgent) || WebAssemblySurface.ShouldPatch(userAgent)) { … }
else surfaceDef = "const applySurface = (W) => {};";
```

理由两条，方向相反：

| 表面 | 为什么不能无条件装 |
|---|---|
| WebAssembly 计数 | 那些数字**是 Blink 的真实值**。一个声称 Chromium 的 profile **本来就诚实**，改了反而是新的谎 |
| iPhone 几何 | 这些数字描述 **402×874 的手机**。装在声称 363×684 桌面的 profile 上，等于「用一个不自洽换另一个不自洽」 |

> **补丁不是可以到处撒的谎，它只修正一处具体的不一致。**

### 三、几何只在顶层，钉箱处处生效

`MobileSurface.BodyJs()` 里：

```js
const isTop = (() => { try { return G === G.top; } catch (e) { return false; } })();
…
if (isTop) { innerWidth / innerHeight / outerWidth / outerHeight / devicePixelRatio }
// clientWidth / clientHeight 的 pin 在 if 之外 —— 挑战帧自己的比例也要为 1
```

这正是 R147 那条 frame 规则的代码形态。

### 四、五条测试

占位符在、调用在 `apply` **内部**（搜索从脚本字面量起算，避开 Replace 行里的同名占位符 ——
这个坑第一版就踩了）、闸门四例（iPhone / Chrome / Edge / 桌面 Safari）、
几何只在顶层而钉箱处处、两段都不 `throw` 且括号配平、非 Apple profile 装的是**空函数而不是错的函数**。

### 五、这一轮的一句话

> 两轮的证据到这一轮才第一次走到运行路径上。
>
> **模型正确、测试通过、但没接进去 —— 那叫笔记，不叫实现。**

## 真浏览器冒烟：两段 JS **根本没在跑**（第 149 轮）

前一轮用字符串断言证明「两段拼进了脚本」。这一轮启动真实 headless Chromium，把同一份脚本装进页面，
再把挑战帧会读的东西读回来 —— 结果四次红。

### 一、四次红，四个不同原因

| 症状 | 真实原因 |
|---|---|
| 全都没生效 | ① **`Page.addScriptToEvaluateOnNewDocument` 只对「下一个文档」生效** —— 在 `about:blank` 上求值量到的是打过补丁之前的浏览器 |
| 仍然全都没生效 | ② `about:blank` 根本不触发新文档脚本，得导航到真实文档 |
| 仍然全都没生效 | ③ **`applySurface(W)` 的形参叫 `W`，而 `WebAssemblySurface.BodyJs()` 里 `const W = G.WebAssembly`** —— 同作用域重名 = **SyntaxError**，浏览器把它吞掉，整份脚本静默不执行 |
| `outerHeight = 769` 而非 874 | ④ 桥以 **363×684** 启动窗口，而 profile 声称 874 —— 宿主窗口比声称的矮 |

诊断的关键一步是**看 `navigator.webdriver`**：补丁本该删掉它，结果它是 `boolean` ——
**说明整份脚本一行都没跑**，而不是「某段没跑」。这一步把猜测变成了结论。

### 二、三个教训，每个都可以复用

1. **「脚本装上了」不等于「脚本在跑」。** 要在**新文档**里、读**被补丁影响的属性**来验证，
   而不是断言字符串、也不是在旧文档上求值。
2. **SyntaxError 是最安静的失败。** 注入脚本外层套着 `try/catch`，一个重名 `const`
   会让整份脚本变成空操作，而没有任何报错传给调用方。
3. **几何的矛盾可能来自窗口尺寸，不是来自补丁。** 原版注释早就写了：
   > the host window must actually be this size or clicks land outside the viewport we claim —
   > one impossibility traded for another. See SolverWindow sizing.

### 三、这一轮的处理

- 三条原因都修好，`SurfaceRuntimeTests` 五条**真浏览器**断言全绿：
  WebAssembly 计数 `[16,1,2,6,6]`、JSPI 三名消失、两个 `type()` 返回 `{kind}`、
  `createEvent('TouchEvent')` 返回 `["object","",0,false]`、缩放比 `[402,402,684,684]`、
  子元素 `clientWidth` 仍是自己的 50、Chromium profile 下 JSPI **仍在**（闸门有效）。
- **第④条不修，钉住**：`outerHeight` 目前是宿主窗口高度，测试显式断言
  `parts[6] < MobileSurface.ScreenHeight` 并注明「窗口尺寸要跟随 profile」。
  **这是下一轮的具体任务，不是可以顺手抹掉的差异。**

### 四、这一轮的一句话

> 上一轮我写的是「模型正确、测试通过、但没接进去 —— 那叫笔记」。
> 这一轮发现：**接进去了，也可能是死的。**
>
> **能跑和看起来接好了，是两件完全不同的事；区分它们的唯一办法是真的跑一次。**

## 窗口尺寸跟随 profile，几何要**反复钉**（第 150 轮）

上一轮留下的第④条（`outerHeight` 报 769 而不是 874）这一轮解决，中间踩了两层。

### 一、第一层：启动尺寸

```csharp
public string WindowSizeArgument(string? userAgent) =>
    MobileSurface.IsAppleUserAgent(userAgent)
        ? $"--window-size={MobileSurface.ScreenWidth},{MobileSurface.ScreenHeight}"   // 402,874
        : WindowSizeArgument();                                                        // 桌面仍 363,684
```

`LaunchAsync(…, string? userAgent = null)` 把它透传 —— **声明什么尺寸，就用什么尺寸启动**。
这正是原版注释要求的：`the host window must actually be this size`。

### 二、第二层：赋值不够，getter 也会被覆盖

改成 `Object.defineProperty(G, name, { configurable: true, get: () => v })` 之后**仍然报 769**。
于是写了一个探针，量到三件事：

```
outerHeight: own = { kind: 'own', get: true, configurable: true }   proto = none
define attempt = ["ok", 874]        ← 当场生效
outerHeight now = 874
```

**结论**：属性的确可以覆盖，`defineProperty` 也成功 —— 但**浏览器在文档开始之后、窗口真正实现时又装了一遍自己的几何**，
把我们的 accessor 换掉了。769 是那一刻回来的。

### 三、修法：在浏览器「安顿几何」的那三个时刻重钉

```js
const pinAll = () => { pin('devicePixelRatio',3); pin('outerWidth',402);
                       pin('outerHeight',874); pin('innerWidth',402); pin('innerHeight',684); };
pinAll();
['DOMContentLoaded', 'load', 'resize'].forEach((ev) => G.addEventListener(ev, pinAll));
```

因为描述符是 `configurable: true`，每次重钉都替换掉浏览器刚装的那个。

### 四、结果

`SurfaceRuntimeTests` 的几何断言从「钉住差异」变成**等值断言**：

```
[402, 874, 3, 402, 684, 402, 874]
```

### 五、这一轮的一句话

> 昨天我写「这是下一轮的任务，不是可以顺手抹掉的差异」。今天抹掉了 —— 但**是量出原因之后抹的，不是假装它不存在**。
>
> **一个差值要么被解释，要么被消除；两者都不做的「先这样」会一直留在系统里。**

## 被漏掉的那半几何：`VisualViewport`（第 151 轮）

原版注释早就说过：

> innerWidth/innerHeight and visualViewport were the only geometry left unpatched, so they reported
> the real host window while outerWidth/outerHeight reported the device.

**replica 在修完前半句之后，正好又犯了后半句。** 这轮补上。

### 一、逐字取回的对象

```
const SCREEN = {"width":402,"height":874,"availWidth":402,"availHeight":874,
                "availLeft":0,"availTop":0,"colorDepth":24,"pixelDepth":24};
const SCREEN_ORDER = ["height","width","colorDepth","pixelDepth","availLeft","availTop",
                      "availHeight","availWidth","orientation"];
const VV = {offsetLeft:0, offsetTop:0, pageLeft:0, pageTop:0, width:VW, height:VH, scale:1};
```

### 二、两个新结论

**① `VisualViewport` 是七个字段**，值 `402 / 684 / scale 1 / offsets 0`，只装在顶层（它是窗口的视口，不是 frame 的）。
已进 `MobileSurface.VisualViewportFields` 与 `BodyJs()`；真浏览器测到 `[402,684,1,0,0]`。

**② `orientation` 在 `SCREEN_ORDER` 里，却不在 `SCREEN` 值对象里** —— 原版**不补**它的值。
实测这台机器报 `landscape-primary`、angle 0，而 profile 声称竖屏手机 —— **这是一处已知的不自洽**。

我不替它编一个值（那就成了「发明行为」），但也不让它沉默：运行时测试把 `orientation` 打印出来，
并断言它确实是「两个原生值之一」，同时在文档里记下这条矛盾。

> **留白要有名字。** 什么都不写的留白，和写着「这里已知不自洽」的留白，不是一回事。

### 三、四 + 一 条测试

`VisualViewportTests` 四条（七字段与顺序、orientation 只在形状里、视口只在顶层、
值与 `scale: 1` 且块内无 `throw`）；运行时测试新增视口与 orientation 两段测量。

### 四、这一轮的一句话

> 上一轮我以为「几何已经全对了」。原版那句注释里，我修的是 `innerWidth/innerHeight`，
> 而它同时点名了 `visualViewport` —— **同一句话里的两件事，我只做了一件，还以为句子读完了。**

## 捡到原版**自己的会话 payload 样本**（第 152 轮）

上一轮留下的 `orientation` 疑问，这一轮在池子里搜的时候撞到一份**完整样本** —— 原版发出去的
那份 JSON。这是本会话第一次拿到它的**遥测 schema**，而不是从类名推。

### 一、样本头（逐字）

```
{"sid":"9a10c34d-…","tid":"3bd808ffef1b18c5…",
 "_t":"ASaMBHzL7WoRfLL6ekqt4MuLNpqk5pjkxXylexg…",
 "cf_flags":"1006579","fresh-cookie":"true","cookie-_cc":"ASaMBHzL7WoRfLL6ekqt4MuL",
 "time-unix-epoch-ms":1778830875801,"time-local":"15-5-2026, 09:41:15",
 "time-string":"Fri May 15 2026 09:41:15 GMT+0200 (Midden-Europese zomertijd)",
 "time-tz-offset-minutes":-120,"time-tz-has-dst":"true","time-tz-dst-active":"true",
 "time-tz-std-offset":-120,"time-tz-fixed-locale-string":"6-3-2014, 07:58:39",
 "dom-local-tag":"ASaMBHzL7WoRfLL6ekqt4MuL","dom-session-tag":"ASaMBHzL7WoRfLL6ekqt4MuL", …}
```

### 二、四处值得命名的地方

| 键 | 说明 |
|---|---|
| `cookie-_cc` | 是 `_t` 的**前 24 个字符** —— cookie 是 token 的截断，**不是独立值** |
| `time-tz-*` 四件套 | 把夏令时写成**状态机**（offset / hasDst / dstActive / stdOffset），而不是一个数字 |
| `time-string` | 带浏览器自己的时区名 —— **`Midden-Europese zomertijd`（荷兰语）**。UA 怎么改都改不掉，因为它来自宿主机 |
| `time-tz-fixed-locale-string` | 把一个**固定瞬间**（2014-03-06 07:58:39）按宿主 locale 格式化 —— 交叉校验「声称的时区 vs 真实时区」最便宜的办法 |

> `-120` 是 JS `getTimezoneOffset()` 的语义（**落后 UTC 多少分钟**），CEST 是 +02:00，所以是 -120。
> 样本的 locale 名写着 `zomertijd`，两半互相作证。

### 三、顺带解决上一轮的疑问

同一份样本里有：

```
"window.screen.orientation.type":"landscape-primary","window.screen.orientation.angle":"0"
```

—— **原版自己报的就是 landscape**（Windows UA）。所以 R151 说的「已知不自洽」不是 replica 引入的，
**那就是原版的常态**。`orientation` 保持原生 = 1:1。

### 四、payload 的指纹部分

`navigator.userAgentData.brands`、connection 四件套（`effectiveType` / `rtt` / `saveData` / `downlink`）、
五个插件（**全部 `internal-pdf-viewer`** + 同一句 `Portable Document Format`）、
`canvas-print-100-999` 与 `-detailed-` 两个哈希、`canvas_spoofing: 0`、`js-errors` 数组、逐字体探测。

还有两个**不是 DOM 属性**的键：

```
"navigator.automationEnabled":false      ← 原版自己写的
"webdriver_detect":false                 ← 原版自己算的
```

**原版把「自己的判断」和「读到的值」放在同一个 namespace 里** —— 检测方无法从命名上区分它们。

### 五、已落成 `SessionPayload`

十六个头键（保序）、`CookieTagLength = 24`、`FixedLocaleDate`、`GetTimezoneOffsetMinutes`、
`IsDaylightActive`、`CookieTagFor`、`CfFlags`、`ComputedKeys`（四个「判断类」键）、
`PluginNames` + 单一 filename/desc、`DarkModeKey/Sample`、`ConnectionKeys`。七条测试。

### 六、这一轮的一句话

> 前一版我在**猜**它发什么；这一轮我看见了它发的东西。
>
> **一份真实样本，胜过十次「从类名推断字段名」。**

## 从 schema 到会发出去的 payload（第 153 轮）

上一轮记下样本，这一轮让它能被真正构建出来：`SessionPayloadBuilder.Build(Inputs)`。

### 一、三条「自洽规则」被写进代码

| 规则 | 代码形态 |
|---|---|
| `cookie-_cc` 是 `_t` 的前 24 字符 | `SessionPayload.CookieTagFor(token)`；`Inputs` **没有**这个字段，想传错都传不进来 |
| 时间四件套描述**同一个瞬间** | 都从 `Now` 派生 |
| 固定瞬间不是「现在」 | `time-tz-fixed-locale-string` 用 `SessionPayload.FixedLocaleDate` |

### 二、一个实测抓到的错

第一次跑测试：

```
Expected: "15-5-2026, 09:41:15"
Actual:   "15-5-2026, 07:41:15"
```

`1778830875801` 是 **07:41:15 UTC**，而样本写 **09:41:15** —— 差两小时，正好是 `getTimezoneOffset() == -120`。
所以 `time-local` 必须是**同一瞬间按声称时区偏移后**再格式化：

```csharp
["time-local"] = inputs.Now
    .ToOffset(TimeSpan.FromMinutes(-inputs.TimezoneOffsetMinutes))
    .ToString("d-M-yyyy, HH:mm:ss", CultureInfo.InvariantCulture),
```

**如果两个键各自取值，payload 就会自相矛盾地讲两个时间。** 这条是测试逼出来的，不是我先想到的。

### 三、固定格式与「可注入格式」

`FixedLocalePattern = "d-M-yyyy, HH:mm:ss"` —— 样本的 `6-3-2014, 07:58:39` 正是这个模式
（日不补零、月不补零、逗号、补零时钟）。**用的是模式而不是 culture 查表**：
样本那台机器的 culture 不保证这台机器装了，而模式本身就是证据。
调用方仍可传 `FixedLocaleString` 覆盖。

### 四、七条测试

键序 == `SessionPayload.HeadKeys`、cookie tag 三处同源且 `Inputs` 无可传字段、
时间四件套同瞬间且固定串≠当前串、布尔是字符串形态（关闭时给 `"false"` 而非缺键）、
固定模式复现样本、可注入格式、**构建器不读时钟**（同输入同字节、以 `{"sid":` 开头）。

### 五、这一轮的一句话

> 上一轮我说「一份真实样本胜过十次推断」。这一轮它立刻兑现了 —— 样本里的 `09:41:15`
> 直接指出我算错了时区偏移。
>
> **样本最值钱的地方，是它能反驳你；一份只会被赞成的资料，等于没有。**

## 有了发信人，而发信人**会挑地址**（第 154 轮）

R153 让 payload 能被构建，这一轮给它一个发送者。风险在于**发错地方**：一个主机没配或拼错的遥测器，
会把一份指纹发到某处然后报成功 —— 而且没人会注意到。

### 两道闸门

```csharp
public static readonly string[] AllowedHosts =
{
    "analytics.cybersole.io",
    "telemetry.cybersole.io",
};                      // R138 那十五个里的两个
```

1. **没地址就不发** —— 默认未配置，未配置给的是**理由**而不是静默成功；
2. **只发给记录过的两个主机** —— 其余按名字拒绝，连 `analytics.cybersole.io.evil.test` 这种
   后缀伪装也过不去；`api.cybersole.io` 也被拒（它不在允许表里）。

这与 `endpoint-provenance.py` 对店端点的规矩是同一条，只是这次用在 **Cybersole 自己的主机**上。

### 传输是注入的，所以能离线取证

```csharp
new SessionTelemetry(sinkUrl, post: (url, body, ct) => …)
```

测试因此能同时断言「发了什么」和「**没发**」：

| 测试 | 断言 |
|---|---|
| 无地址 | 传输**零调用**，`LastError` 含 `no sink configured` |
| 未知主机（四个候选含伪装后缀） | 传输**零调用**，理由含 `not one of the recorded hosts` |
| 两个允许主机 | 各发一次，body **逐字节等于** `SessionPayloadBuilder.Build(...)` |
| 传输返回 false | `transport refused the payload`，不抛 |
| 传输抛异常 | 记录消息，不抛 —— **遥测永远不在结账关键路径上** |
| 取消 | `cancelled` |

### 一条顺带的自检

两个允许主机**都不是 solver 主机**（`IsSolverHost` 为 false）—— 这份 payload 是遥测，不是解墙答案。

### 这一轮的一句话

> 上一轮我担心的是「算错」。这一轮担心的是「发错」——**算错会被测试抓住，发错不会**。
>
> **凡是会把数据送出边界的地方，边界本身必须是可枚举、可断言的常量。**

## 第四次同一个形状：发信人终于被调用，而**离线三件事同时成立**（第 155 轮）

`SessionTelemetry` 上一轮是独立类，没人调用。这一轮接进 `HttpAnalytics.Flush()`。

### 一、接口放哪：依赖方向决定位置

`Cybersole.Stores` 引用 `Cybersole.Http`，不是反过来。所以接口在 Http、实现在 Stores：

```csharp
public interface ISessionSink
{
    bool IsConfigured { get; }
    Task<bool> SendAsync(CancellationToken ct = default);
}
```

**好处不只是编译能过** —— `HttpAnalytics` 因此**不知道指纹是什么**，它只知道「有个东西可以收一份会话摘要」。

### 二、一个必须改的早退

```csharp
// 旧：只有请求侧有地址才继续
if (SinkUrl is null) return;
```

这会让「只配遥测、不配 ClickHouse」的部署**静默永不发送** —— 和 R127 那个「先 dequeue 再判空」是同一类缺陷。
现在早退的条件变成**两侧都没有**。

### 三、离线三件事同时成立

| 测试 | 断言 |
|---|---|
| 只配遥测 | `SinkUrl` 为 null 时**仍然发送**（fire-and-forget，测试轮询等它） |
| sink 未配置 | **一次都不调用**，也不排队 |
| 什么都没配 | 请求仍留在缓冲里、`Failures` 为空 —— **不构建、不排队、不发** |
| sink 抛异常 | 记进 `Failures`（`session sink failed: …`），**不冒到 flush 调用方** |
| 工厂缺失 | 拒绝并给理由 `no inputs factory`，传输零调用 |

### 四、为什么用「工厂」而不是「快照」

flush 是定时器驱动的，它不知道会话。如果挂上 sink 时就把 inputs 快照下来，发出去的会是**挂上那一刻**的会话，
而不是**发送那一刻**的。所以接口实现是：

```csharp
public Func<SessionPayloadBuilder.Inputs>? InputsFactory { get; set; }
```

### 五、这一轮的一句话

> 这是本会话第四次遇到同一个形状：**类写好了，没人调用。** 前三次我都是被测试逼着发现的。
>
> **这次我提前知道会这样，所以先写了「谁会调用它」再写它。差别不大，但方向对了。**

## 把样本变成待办：指纹部分三栏审计，并关掉两栏（第 156 轮）

R152 的样本读起来像一份清单。这一轮把它分成三栏，然后**能关的都关掉**。

### 一、三栏

| 栏 | 成员 |
|---|---|
| **已有**（9） | `userAgentData.brands/mobile/platform`、`userAgent`、`platform`、`language`、`hardwareConcurrency`、`deviceMemory`、`webdriver_detect` |
| **已装**（7，本轮） | `connection.{effectiveType,rtt,saveData,downlink}`、`plugins`、`automationEnabled`、`screen.darkMode.enabled` |
| **装不了**（5） | `canvas-print-100-999`、`canvas-print-detailed-100-999`、`canvas_spoofing`、`js-errors`、`font-*` |

第三栏是这一轮最想保住的东西：

> **canvas 哈希不是可以覆盖的属性，而是跑一遍 canvas 的结果。**

一份声称能「安装」它的隐身脚本，是在夸自己的射程。`canvas_spoofing` 与 `js-errors` 更是原版**自己的记账**，
和它们描述的那些读数塞在同一个 namespace 里。

### 二、两处实测纠正

**① 插件是 5 个，不是 3 个。** 样本 `navigator.plugins.count = 5`，五个名字共享
`internal-pdf-viewer`。replica 之前是 3 —— 连「数一下」都能被抓。
慢速测试 `ChromiumStealthTests` 里那条 `Assert.Equal(3, …)` 已改成 5，并注明依据是样本。

> **数字要从样本里抄，不要从上一版代码里抄。**

**② 顺序决定胜负。** 引擎块最初插在 `apply` 的**开头**，于是它设的 5 个插件被后面那段旧的 3 个覆盖 ——
实测读到 `[3, [...]]`。移到 `apply` **末尾**才对。

移动时还顺手犯了个错：把调用插在了 `apply` 的闭合 `};` **之后**，多出一个 `};` ——
整份脚本 SyntaxError、静默不执行、六个断言同时红。**这是同一个坑第二次踩**（R149 也踩过）。

### 三、真浏览器量到的结果

```
plugins     = [5,["PDF Viewer",…],["internal-pdf-viewer",…]]
connection  = ["4g",50,false,10]
flags       = [false,false]        // navigator.automationEnabled, screen.darkMode.enabled
```

六条真浏览器断言全绿。

### 四、这一轮的一句话

> 三栏里最容易被忽略的是**第三栏**：把「装不了」写下来，比把「还没装」写下来更难，
> 因为它要求承认射程有限。
>
> **一份诚实的清单，必须包含「做不到」那一栏。**

## 手机的**触觉面**与那道闸门（第 157 轮）

样本里还有两份东西：一份 `const NAV` 捕获，和一段讲清「为什么要补」的注释。

### 一、`const NAV`（逐字）

```
const NAV = {"standalone": false, "hardwareConcurrency": 4, "webdriver": false, "maxTouchPoints": 5,
             "cookieEnabled": true, "appCodeName": "Mozilla", "appName": "Netscape",
             "appVersion": "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15…"}
```

这台手机是 **iOS 27.0.1**、四核、**五个触点**。

### 二、闸门（原版注释，0x03d27ea7）

```
// hsw gates its whole worker path on one of them:
//   aK_ = ('ontouchstart' in window);  lK = uS && aK_ && <ua not Safari-shaped>;
//   QW = nW || lK
// With aK_ false the gate opens and we …
```

**`'ontouchstart' in window` 不是装饰** —— 一方墙的 worker 分支靠它和 UA 形状配对决定走哪条。
一个声称 iPhone、却答 `false` 的 profile，是在**回答一个对方用来选择的问题**。

### 三、replica 之前的样子

`MobileSurface` 装了屏幕、视口、Screen 形状，**却没装触点** —— `maxTouchPoints` 仍是宿主机的 10。
这和 R151 漏掉 `visualViewport` 是同一类：句子里的第二件事没做。

### 四、已落成 `MobileNavigator`

`MaxTouchPoints = 5`、`HardwareConcurrency = 4`、`IosVersion 27.0.1`、五个触觉处理器
（`ontouchstart/move/end/cancel/touchforcechange`）、`HswGate` / `HswConsequence` 两个常量。
只对 Apple UA 安装；真浏览器量到 `[true,5,true]`，而 Chrome profile 仍是 `false`。

### 五、`history.length` **谁都不改**

池子里 `pushState` / `replaceState` 出现 **0 次** —— 样本里的 `9` 是浏览器自己的数字。
所以「读它、但不写它」，并且测试断言三份 body 里都不出现这两个词。

### 六、又踩了同一个坑（第三次）

第一版 `BodyJs()` 用转义拼接，结果每个 `\n` 落成**字面反斜杠 + n**、跑到字符串外面 —— 一个 SyntaxError，
浏览器整份吞掉，`maxTouchPoints` 停在 10。改成 C# 原始字符串（`"""`）后立刻正确。

> **同一个错误（转义 / 括号）已经三次了。这不再是运气问题，是我该改用 raw string 作为默认写法。**

### 七、这一轮的一句话

> 「装了屏幕」不等于「装了手机」。**一台声称是手机的设备，得在每一个会被问到的地方都是手机。**

## 三次同一个死因，该造一把尺子了（第 158 轮）

| 轮 | 错在哪 | 后果 |
|---|---|---|
| R149 | `applySurface(W)` 形参与体内 `const W` 重名 | SyntaxError，浏览器吞掉，整份脚本不执行 |
| R156 | 调用被插到 `apply` 闭合 `};` **之后**，多一个 `};` | 同上 |
| R157 | 转义拼接，`\n` 落成字面反斜杠+n 跑到字符串外 | 同上 |

三次不同的错，同一个死因：**注入脚本的语法错误是不可见的**。

### 一、静态半边：`JsGuard`

对每一份生成的 body 检查四件事：

1. 没有字面 `\n` / `\t`（逃了两次的痕迹）；
2. **在字符串之外**统计 `{}` `()` `[]` 的净余额必须为 0；
3. 语句行数 ≥ 3 —— 「一整行长条」正是转义 bug 的形状；
4. 不能是空体 —— 空的 stub 在这份代码里从来等于「组合掉了」。

`AllBodies()` 覆盖五份：WebAssembly / Mobile / Engine / Touches / WebAssembly wrapper。
**新增一份 body 而忘了登记，`TheGuardCoversFiveBodies` 会红。**

### 二、动态半边：真 JS 解析器

```js
new Function('G', body)   // 编译，不执行
```

一条断言就能问出「这是不是一段程序」。并配**对照组**：

```
控制组：  try { … } catch (e) {}  ['a'].forEach(y);}      →  SyntaxError
```

对照组很重要 —— 没有它，这条测试只证明了「`new Function` 没抛」。

### 三、结果

- 五份 body 全部 `clean`（说明除 R157 那一处外，其余本来就是多行未转义的）；
- 五份 body 全部 `ok`（真解析器通过）；
- 组合后的 `applySurface`（Engine + WASM + Mobile + Touches）解析 `ok`，并且落地后
  `navigator.maxTouchPoints == 5`。

### 四、这一轮的一句话

> 同一个死因出现三次，说明**缺的不是小心，是一把尺子**。
>
> **每一次「我又犯了同样的错」的背后，都有一个本该存在的检查没被写下来。**

## 整份 `NAV` 取全：它是 **iOS 上的 Chrome**（第 159 轮）

上一轮只读了三行。把整条 `const NAV` 拉出来，长度是 16 个字段。

### 一、逐字（关键处）

```
"appVersion": "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15
               (KHTML, like Gecko) CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1",
"platform": "iPhone", "product": "Gecko", "productSub": "20030107",
"vendor": "Apple Computer, Inc.", "vendorSub": "",
"language": "nl-NL", "onLine": true, "pdfViewerEnabled": true
```

**`CriOS/156.0.8078.54`** —— 这是 **iOS 上的 Chrome**，但 iOS 只允许 WebKit，所以
`vendor` 仍是 `Apple Computer, Inc.`、`product` 仍是 `Gecko`。这台机器是**荷兰语（nl-NL）**。

### 二、`appVersion` 不是常量，是 UA 去掉 `Mozilla/`

```
userAgent   = "Mozilla/5.0 (iPhone; … Safari/604.1"
appVersion  = "5.0 (iPhone; … Safari/604.1"
```

一模一样，只差前缀。所以这一版改成**派生**而不是写死 —— 两个相邻属性如果说两套话，就是自相矛盾。

### 三、还有两份清单：`NAV_ORDER` 与 `NAV_KEYS`

```
NAV_ORDER = 49 项，按 for-in 走过的顺序
NAV_KEYS  = 51 项，含 __defineGetter__ / hasOwnProperty 等
```

**枚举顺序本身就是指纹** —— 一个 `for in navigator` 的检测器读的是顺序，不是集合。
已作为 `MobileNavigator.NavOrder` 记录（顺序原样保留）。

### 四、顺带发现：`CRED_SHIM`

```
const CRED_SHIM = [{"name": "get", "length": 1, "src": "function(e){if(!e?.publicKey)…"}]
```

—— 连 `navigator.credentials.get` 的 shim 都带着**长度**和一段**压缩后的源码**，
因为 `Function.prototype.toString` 会读源码。**shim 的伪装不止在行为上，还在它的文本上。**
这条留给后续轮次。

### 五、自己踩的坑：测量时机

`TheZoomRatioIsExactlyOne` 突然报 `Cannot read properties of null`。
诊断表达式一改就看清了：

```
ratio inputs = ["no-documentElement","loading"]
```

**导航在文档解析完成之前就返回了。** 之前在别的轮次恰好赶上了，这次没赶上 ——
所以测量前必须等 `document.readyState === 'complete'`。已加进测试工装。

### 六、这一轮的一句话

> 上一轮我以为 `NAV` 是三行。它其实是十六个字段 + 两份顺序清单 + 一个 shim。
>
> **「读完了」的感觉，通常只是「读到了我以为重要的那部分」。**

## 补丁是两件事：行为，以及它**自称是什么**（第 160 轮）

原版 `CRED_SHIM` 的每一项都带三样东西：

```
{"name": "get", "length": 1, "src": "function(e){if(!e?.publicKey){return O.get(e)}…"}
```

**为什么要记 `length` 和 `src`？** 因为它们**都会被读**：`fn.length` 是第二个，
`Function.prototype.toString` 是第三个。一个改了行为却答「`function () { … }`」的补丁，
**是在自报身份**。

### 一、replica 之前的样子

补了 `getVoices`、`createEvent`、十几个 getter —— **一个都没伪装 toString**。
任何一个检测器只要对那个 getter 调一次 `Function.prototype.toString.call(...)`，就看见源码。

### 二、`NativeMask`：注册表 + 一次覆盖

```js
const FAKES = new WeakMap();
const protoToString = Function.prototype.toString;
function toString() {
  const fake = FAKES.get(this);
  return fake !== undefined ? fake : protoToString.call(this);
}
asNative(toString, 'toString', 0);      // 连覆盖本身也要伪装
Object.defineProperty(Function.prototype, 'toString', { value: toString, … });
```

配 `asNative(fn, name, length)` 与 `maskGetter(target, prop)` 两个工具。
**安装顺序**：`NativeMask.BodyJs()` 在 `surfaceBody` 的最前面 —— 后面每一处补丁都能登记自己。

### 三、真浏览器量到

- 被补的 `navigator.plugins` getter：`toString` 答 `[native code]`；
- `Function.prototype.toString` 自身：也是 `[native code]`；
- `Element.prototype.clientWidth` 的 getter：同样；
- **页面的普通函数仍然打印源码**（`return x + 1`）——
  这条断言很重要：**伪装必须只盖住自己，不能把整个页面的 `toString` 变成静音**。

### 四、这一轮的一句话

> 上一轮我记下了 `CRED_SHIM` 带 `src`，还把它当「有趣的花边」。
> 这一轮才想明白：**它不是花边，它是规格 —— 说明 shim 的伪装有一半在文本上。**
>
> **证据里最不像证据的那一项，往往是你还没读懂的那一项。**

## 伪装终于有了调用者：22 行表 + 一趟最后的 pass（第 161 轮）

R160 把 `asNative` / `maskGetter` 造成了，**却一个都没登记** —— 这是本会话第五次「零件齐了没人调用」。
`MaskTargets` 就是调用者。

### 一、表是数据，不是代码

19 个 getter + 3 个函数，**每行带拥有者**：

```
G.navigator                plugins mimeTypes connection maxTouchPoints hardwareConcurrency
                           deviceMemory webdriver
G.Element.prototype        clientWidth clientHeight
G                          devicePixelRatio outerWidth outerHeight innerWidth innerHeight
G.Screen.prototype         width height darkMode
G.VisualViewport.prototype width
G.Performance.prototype    memory
G.speechSynthesis          getVoices
G.Document.prototype       createEvent
G.WebGLRenderingContext.prototype  getParameter
```

**为什么是数据**：测试可以逐行走。真浏览器里对每一行读描述符、问
`Function.prototype.toString`「你怎么说」——答源码的那一行就是自报身份的补丁。

### 二、pass 必须最后跑

```csharp
surfaceBody += MaskTargets.ApplyJs();     // 在 Engine/WASM/Mobile/Touches 之后
```

**尚未安装的 getter 无法被伪装** —— 所以顺序本身就是正确性。
`ThePassRunsLast` 断言它在 `MobileNavigator.BodyJs(userAgent)` 之后。

### 三、真浏览器逐行验证

22 行全部 `[native code]`（或 `absent`，因为某些平台上根本没有这个成员）。
断言是**逐行**的，不是抽样 —— 抽样会让第 20 行永远没人看。

### 四、这一轮的一句话

> 上一轮我说「补丁是两件事」。这一轮让那两件事**在同一处发生**：装补丁的 body 之后，
> 紧跟着一趟把这些名字全部登记为 native 的 pass。
>
> **机制和价值之间隔着的，通常只是一张表和一个调用点。**

## 三元组的另外两个：`length` 与 `name`（第 162 轮）

原版 shim 的条目是**三元组**：`{name, length, src}`。R161 只伪装了 `src`，
还把 `length` **从「刚被替换掉的那个函数」抄**——那是 shim 自己。

一个写成 `function () { … }` 的 shim，`length` 报 0，而平台的 `createEvent` 报 1。
**这是一条表达式就能读出来的差别。**

### 一、所以 arity 从**接口**来，不从实现来

```
getVoices   0     SpeechSynthesis.getVoices()
createEvent 1     Document.createEvent(type)
getParameter 1    WebGLRenderingContext.getParameter(pname)
toString    0     Function.prototype.toString()
```

`NativeArity.For(name)` 查表；表里没有就**抛**（构建期就炸，不是运行时静默）。
getter 的 `name` 是 `"get <prop>"`、`length` 是 0 —— 这一半之前碰巧是对的，**碰巧对不等于对**。

### 二、生成的 pass 现在写的是表里的数字

```js
M.asNative(owner.createEvent, 'createEvent', 1);   // 不再是 .length
```

测试断言 `DoesNotContain(".length)")` —— 旧形状必须消失。

### 三、真浏览器读回三元组

逐行读 `fn.name` / `fn.length`，并与 `NativeArity` 比对；另读一个 getter，
确认它是 `get plugins` / `0`。全部通过。

### 四、这一轮的一句话

> 三轮才把三元组读完：R160 读 `src`，R162 读 `name` 与 `length`。
> 每一轮我都以为「最重要的那个已经做了」。
>
> **一个被记录成三元的证据，通常三个都要做 —— 否则作者不会写成三元。**

## 剪枝：同一成员，一个 claim 装、另一个 claim 删（第 163 轮）

原版注入了 NAV 之后紧跟着一句注释：

```
// Actually removed, not hidden behind a trap. Blink exposes a pile of interfaces WebKit has
// never shipped -- userAgentData, getBattery, connection, bluetooth, usb, hid, serial, xr,
// deviceMemory -- and browserleaks reads every one of them straight off navigator.
NAV_PRUNE …
```

**这直接纠正了 R156**：那一轮我把 `connection` 无条件装给了**所有** profile。
对 Apple profile 这是反的 —— WebKit 从来没发布过它，它必须**不存在**。
而桌面样本确实读 `navigator.connection`。

> **同一个成员，一个 claim 装、另一个 claim 删。** 这就是本轮写进 `NavPrune.Rule` 的话。

### 一、`NavPrune`

九个名字：`userAgentData`、`getBattery`、`connection`、`bluetooth`、`usb`、`hid`、`serial`、`xr`、`deviceMemory`。

**删除而不是设陷阱** —— 因为「答否」和「不存在」不是一回事，`for in` 仍然会走到一个陷阱属性。
执行时对**实例和原型都删**；顺序在引擎块之后（否则删的是它刚装的那个）。

### 二、真浏览器两个 claim 各测一遍

```
phone   leaves = []
desktop keeps  = ["object","4g"]
```

`deviceMemory` 尤其有意思：它正是 replica 自己装的那个，现在对手机必须删掉。

### 三、`credentials` 四元组：**记录，但不实现**

```
get                  length 1
create               length 1
preventSilentAccess  length 0
store                length 1
```

原版的 `get` 里是 `he(e,true)`、`create` 里是 `ge(e)` —— 一个**虚拟认证器**，
用来过 3DS 的 WebAuthn 挑战。这一轮只把**形状**记下来，并把「没实现」写成明文：

```csharp
public const string CredentialsOpenItem =
    "the image's credentials.get/create are a working WebAuthn shim (virtual authenticator for 3-D Secure " +
    "challenges); this workspace records the shape and has not built the authenticator";
```

### 四、这一轮的一句话

> R156 我写「`connection` 是引擎成员，对所有 profile 都装」。R163 的注释告诉我：
> **它只对桌面成立，对手机是必须删的。**
>
> **「对所有 profile」这种说法，通常是「我只验证了一个 profile」的伪装。**

## 两条写在代码里的细节：装在**原型**上，`languages` 只有**一个**（第 164 轮）

原版这两行不是散文，是规格：

```js
Object.keys(NAV).forEach((key) => value(Navigator.prototype, key, NAV[key]));
value(Navigator.prototype, 'languages', Object.freeze([NAV.language]));
```

### 一、装在原型上

第一行说**位置**：属性装 `Navigator.prototype`，不是实例 —— 检测器可以读
`Object.getOwnPropertyNames(navigator)` 看它们是不是「自己的」。

### 二、`languages` 是一个元素

第二行说**数量**：一个语言，且冻结。手机报 `["nl-NL"]`，桌面才报 `["nl-NL","en-US"]`。

### 三、实测纠正：`defineProperty` 可能「接受但无效」

第一版只往原型上装，结果：

```
platform 仍是 Win32，languages 却是 1
```

同一个 `put` 里有的生效有的不生效 —— **`defineProperty` 不抛异常，不代表读回来是那个值**。
改成「原型、实例都试，**用读回值验证**」：

```js
const targets = [P, N];
for (…) { try { Object.defineProperty(target, name, {...}); if (N[name] === v) return; } catch (e) {} }
```

真浏览器最终读回：

```
["nl-NL",1,"nl-NL",true,"iPhone","Apple Computer, Inc.","20030107"]
```

### 四、守卫自己的 bug

`JsGuard` 忽然报 `braces: unbalanced: 2` —— 因为注释里那句
`browser's own accessor may answer…` 的**撇号**被当成字符串开头，把后面整段代码吞了。
改成**先跳过注释、再处理引号**。

> **一个会算错的守卫比没有守卫更坏 —— 它会让正确的代码变红。**

### 五、这一轮的一句话

> 两行代码，两个规格：**位置**和**数量**。我按字面实现位置，被浏览器的行为纠正；
> 按字面实现数量，一次就对了。
>
> **照着规格写，还要照着现实验。规格说「装上去」，现实说「装上去不等于读得到」。**

## 顺序重排：做到了 28/50，但**相对顺序 100%**（第 165 轮）

R159 只把 `NAV_ORDER` 记下来，没有执行。这一轮把 `reseat` 真跑起来。

### 一、机制（原版自己就在 Screen 上用）

```js
const d = Object.getOwnPropertyDescriptor(target, name);
if (!d || !d.configurable) return;      // 不可配置就搬不动
delete target[name];
Object.defineProperty(target, name, d); // 重加 = 移到末尾
```

按顺序依次执行，可配置的属性就会排在末尾、彼此保持给定次序。

### 二、实测（真浏览器）

```
before own = [maxTouchPoints, scheduling, userActivation, geolocation, ink, …]
after  own = [scheduling, ink, doNotTrack, webkit*, windowControlsOverlay, vibrate,
              constructor, standalone, hardwareConcurrency, …, javaEnabled]
recorded names present on the prototype: 28/50
relative order preserved: True
```

三条结论，都要照实写：

1. **不可配置的 Blink 名字永远在前面**（`scheduling`、`ink`、`webkitTemporaryStorage`…）—— 任何 reseat 都搬不动它们；
2. **50 个记录名里只有 28 个真的在 `Navigator.prototype` 上** —— 其余在 `Object.prototype` 或本引擎没有；
3. **在这 28 个之间，记录的相对顺序 100% 达成。**

所以断言写的是**测量到的事实**，不是理想：

```csharp
Assert.True(relativeOrder, "the recorded relative order is achieved among the properties that exist");
Assert.True(present.Count >= 20);
```

### 三、顺手纠一个数字

R159 的注解说 `NAV_ORDER` 是 **49** 项 —— **列表本身是 50 项**。测试里的常量改成从列表读。

> **数字要从数据里取，不要从描述数据的那句话里取。**

### 四、这一轮的一句话

> 「顺序重排」听起来是一个动作，实际是**一次谈判**：浏览器说哪些能搬、哪些不能，我们只能搬能搬的。
>
> **做不到 50/50 不是失败，假装做到了才是。**

## 五十个名字的户口普查：27 / 10 / 13（第 166 轮）

上一轮量出「28/50 在原型上」。这一轮问清另外二十二个在哪儿 —— 答案把整个问题切成两半。

```
在 Navigator.prototype    27   引擎有；只需值，不需存在
在 Object.prototype       10   toString / valueOf / hasOwnProperty / __defineGetter__ … 继承来的
完全不存在                13   手机有、本引擎没有
```

### 一、第三行是 `NavPrune` 的镜像

| 方向 | 名单 | 动作 |
|---|---|---|
| 引擎**有**、手机**没有** | `userAgentData` `connection` `bluetooth` `usb` `hid` `serial` `xr` `getBattery` `deviceMemory` | **删** |
| 手机**有**、引擎**没有** | `standalone` `locks` `credentials` `mediaDevices` `serviceWorker` `storage` `wakeLock` `share` `canShare` `requestMediaKeySystemAccess` `gpu` `clipboard` `audioSession` | **装** |

> **这是同一次测量的两个读法。**

### 二、十三个里这一轮只装两个

`standalone`（布尔）与 `locks`（页面会调方法的对象）—— 这两个是**普通值**，装上去不会引出更多问题。

其余十一个**逐个写下理由**，最重的是 `credentials`：

```
credentials   the image's shim is a working WebAuthn implementation (R163 open item)
serviceWorker a navigator.serviceWorker that never registers is itself a tell
gpu           WebGPU adapter surface is a fingerprint of its own
audioSession  Safari-only; a stub here would be a member Chrome never had either
```

**「先不装」和「忘了装」是两件事** —— 前者必须能说出为什么。

### 三、这一轮的一句话

> 一直以为「补上手机该有的成员」是一张清单。这一轮才发现它是**两张**：一张删、一张装，
> 而且两张来自同一次测量。
>
> **把一个负数说清楚，和把一个正数说清楚，价值一样。**

## 十三里装两个，并且**装的顺序**本身就是正确性（第 167 轮）

`standalone`（布尔）与 `locks`（Web Locks API）都能不靠模拟就说得通：调 `request` 的页面要的是**回调跑起来**，
不是真的排队。两者都装 `Navigator.prototype`（R164 的规矩），都进 `MaskTargets`（R160 的规矩）。

```
locks.request(name, callback)   length 2   回调执行，返回 Promise
locks.query()                   length 0   空快照 { held: [], pending: [], granted: [] }
```

### 一、实测

```
probe  = [false,"object","function",2,"function",0]
ran    = true:true      // Promise 已返回，回调已跑
masked = ["function get locks() { [native code] }", "function request() { [native code] }"]
```

### 二、装的位置错了，顺序就崩了

第一版把这两个**装在 reseat 之后**，于是它们落到原型属性列表的末尾 —— 实测：

```
recorded names present on the prototype: 29/50
relative order preserved: False
```

把安装移到 reseat **之前**，两条同时成立：29/50、相对顺序 True。

> **每一次「安装一个成员」都会在原型末尾追加一项。所以任何重排都必须排在所有安装之后。**

这条不是风格问题，是**顺序即正确性**——与 R161 里「mask 必须最后跑」是同一条规律。

### 三、这一轮的一句话

> 上一轮我说「先不装和忘了装是两件事」。这一轮装了，立刻撞到第二件事：
> **装的时机，和装不装一样重要。**
>
> **一个 pass 链条里，每一步的位置都是它语义的一部分。**

## 把「顺序即正确性」变成契约（第 168 轮）

三轮的学费：

| 轮 | 谁插错了位置 | 后果 |
|---|---|---|
| R161 | mask pass 想跑在前面 | 它要伪装的 getter 还没装 |
| R156 | 引擎块跑在旧 patch 之前 | 五个插件被三个覆盖 |
| R167 | `locks` 装在 reseat 之后 | 29/50，相对顺序 `False` |

所以这一轮把顺序**写下来，并且让它在源码里可检查**。

### 一、`SurfaceOrder`：九步，每步带「为什么不能动」

```
1 mask          first: every patch after it registers itself as native
2 engine        unconditional: true for every profile
3 webassembly   gated on an Apple claim
4 mobile        gated on an Apple claim
5 touches       after the mobile figures, same prototype
6 prune         after the engine block, deletes what it installed
7 locks         before the reseat, every install appends
8 reseat        after every install, orders what exists
9 mask-pass     last: an uninstalled getter cannot be masked
```

`SurfaceOrder.Check(bridgeSource)` 返回违规列表；`TheBridgeFollowsTheOrder` 用真实源码跑它。

### 二、两条反向断言：错的必须被抓

- **`AWrongOrderIsRejected`**：把 reseat 放到 locks 之前（R167 的真实错误），断言得到
  `reseat appears before locks`，并把原因一起带出来；
- **`AMissingBodyIsRejected`**：删掉 mask pass 那一行，断言 `mask-pass: marker not found` ——
  **少一步不能静默通过**。

### 三、这一轮的一句话

> 前三轮我每次都在运行时发现顺序错了，然后修好。这一轮改成**在编译后的第一秒就发现**。
>
> **一个错误被修好两次，说明缺的不是手，是尺子；被修好三次，说明缺的是把错误写进契约。**

## 又一段注释，三处纠正（第 169 轮）

`value(Navigator.prototype, 'languages', …)` 之后紧接的是 `NAV_PRUNE` 的**本体**，它把 R163 的三处判断都纠正了。

### 一、prune 是**白名单**，不是黑名单

```js
NAV_PRUNE = (realm) => {
  const proto = realm && realm.Navigator && realm.Navigator.prototype;
  if (!proto) return;
  nativeOwnNames(proto).forEach((key) => {
    if (!NAV_KEYS.has(key) && key !== 'constructor') { try { delete proto[key]; } catch (e) { } }
  });
```

R163 我写了九个名字去删。原版是**留下 51 个、其余全删**。

> 黑名单要在引擎每发布一个新接口时补一条；白名单**不会落后**。

我们的脚本还有几处把成员装在**实例**上（`deviceMemory` 等），所以 sweep 走**原型 + 实例**两遍 ——
这是同一规则的超集，实测逼出来的：不改的话 iPhone profile 仍然能读到 `navigator.deviceMemory`。

### 二、`audioSession`：`{}` + 一个 tag

```
// iOS exposes navigator.audioSession, which Blink has no equivalent for, so the prune above cannot restore it
// -- it was never there. hCaptcha serialises each navigator member with JSON.stringify, and on the device this
// one comes back as {} exactly like gpu and clipboard do, so a bare object with the right toStringTag reproduces
// what it reads.
const session = {};
Object.defineProperty(session, Symbol.toStringTag, { value: 'AudioSession', configurable: true });
Object.defineProperty(session, 'type', { value: 'auto', enumerable: false, configurable: true });
value(proto, 'audioSession', session);
```

**shim 不必模拟 API，它只需复现「读的人序列化出来的东西」。** 实测：

```
JSON.stringify(navigator.audioSession) → "{}"
Object.prototype.toString.call(…)      → "[object AudioSession]"
navigator.audioSession.type            → "auto"
```

### 三、`plugins` / `mimeTypes` 要**留原生**

```
// navigator.plugins / mimeTypes are left NATIVE. Blink's lists are the spec's five PDF viewers (filename
// "internal-pdf-viewer") and two PDF mime types, which is exactly what the iPhone reports: every device
// HAR -- iOS 26.6.1 (chrome-topps, tcg, topps-cp x2) and iOS 27.0.1 (shopify-cp-solve-28-10) -- sends
// topLevel.nv.plugins as five "internal-pdf-viewer", and the device collector reads lengths 5 / 2. An
// override here used to empty both, on the mistaken belief that WebKit's lists are empty, so every bot
// payload carried plugins: [] in plaintext.
```

R156 花了功夫「装五个插件」，**其实 Blink 本来就是五个**；而更早的 replica 装的是**三个**、`mimeTypes` 为空 ——
**比什么都不做更糟**。实测（原生，未打补丁）：`[5,2,"internal-pdf-viewer"]`。

### 四、这一轮的一句话

> 一段注释纠正了三处：机制（黑名单→白名单）、形状（`audioSession` 是 `{}`）、以及**「不要动」也是一种实现**。
>
> **最省力的修复，有时是删掉一段代码。**

## `credentials` 的答案不是虚拟认证器，是**转发**（第 170 轮）

原版那段注释比前面几段都长，一次说清三件事，而 replica 三件都错：

```
// Chrome for iOS does not expose WebKit's CredentialsContainer to the page. Its passkey script
// (components/webauthn/ios/resources/passkey_controller.ts, injected into every frame) caches the native one and
// then runs Object.defineProperty(navigator, 'credentials', {value: credentialsContainer})
// -- an OWN property of the navigator INSTANCE, non-enumerable, non-writable and non-configurable, holding a plain
// object of four script functions. Two things follow on the device and both were wrong here:
//   - for (k in navigator) SKIPS credentials, because a non-enumerable own property shadows the enumerable one on
//     the prototype. hCaptcha ships that loop verbatim as topLevel.nv: the device sends 32 keys, this engine sent
//     33 with `credentials: {}` after audioSession.
//   - the value is a plain Object whose methods print script source, not an [object CredentialsContainer] whose
//     methods print [native code].
// The prototype member stays, so getOwnPropertyNames(Navigator.prototype) keeps the device's 41 names.
```

### 一、原版**没有实现 WebAuthn**

它做的是：拿引擎自己的容器 → 四个方法各包一层转发 → 伪装源码。

```js
const fn = function () {
  const target = native && native[row.name];
  if (typeof target !== 'function') return Promise.reject(new TypeError('navigator.credentials is unavailable'));
  return target.apply(native, arguments);
};
```

**比虚拟认证器更小、也更忠实。** R163 把这件事写成「开放项」，这一轮可以关掉了 —— 关的方式是**换一个问题**。

### 二、三个可测的事实

实测（真浏览器）：

```
[true,false,false,false,-1,"function",1,"function get() { [native code] }"]
  ↑own ↑非枚举 ↑非可写 ↑非可配 ↑for-in 里没有 ↑是函数 ↑arity 1 ↑看起来原生
'credentials' in Navigator.prototype  →  true   （原型成员也在，影子关系成立）
```

- **非枚举自有属性** → `for (k in navigator)` **跳过**它 → 32 键而非 33；
- **arity 与 `[native code]`** → 三元组的另两项；
- **原型成员保留** → `getOwnPropertyNames(Navigator.prototype)` 仍是设备的那个数量。

### 三、`canShare` / `share`：数据属性，不是访问器

```
// WebIDL operations are DATA properties; value() installs a brand-checked accessor, which is right for attributes
// like audioSession and wrong here, so these are defined directly.
```

`canShare({title:'x'})` → `true`，`canShare({})` → `false`；
`share` 拒绝时用的正是 WebKit 那句：

```
The request is not allowed by the user agent or the platform in the current context.   (NotAllowedError)
```

### 四、这一轮的一句话

> R163 我写下「虚拟认证器未实现」，把它当成一块要补的空白。R170 的注释告诉我：
> **原版也没实现 —— 它转发了。**
>
> **一个「未实现」的开放项，有时是因为问题问错了，而不是因为活儿没干。**

## `prototype` 的有无，是一行语法的事（第 171 轮）

原版那三个 helper 里藏着最关键的一行：

```js
const renamed = (fn, name) => { try { fn.name via defineProperty } catch {} return fn; };
const noProtoMethod = (impl, name) => renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
const noProtoGetter  = (impl, name) => renamed(Object.getOwnPropertyDescriptor(
  { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');
```

**`({ m() {} }).m` 是方法简写** —— 它和普通函数表达式几乎一样，**唯独没有 `prototype`**。
而 WebIDL 操作正是这样。`delete fn.prototype` 也能做到，但简写是**根本不创建**。

### 一、为什么这件事重要

一个 `function () {}` 有 `prototype`，一个 WebIDL 操作没有。检测器一行就能分开：

```js
'prototype' in navigator.canShare   // 设备：false
'prototype' in navigator.canShare   // 未处理：true
```

### 二、实测

```
[["canShare","function",false,true,"canShare",1],
 ["share","function",false,true,"share",1]]
   ↑类型      ↑无 prototype ↑prototype 为 undefined ↑name ↑arity
```

而 `credentials` 的四个方法**故意保留** `prototype` —— 原版说「四个函数在设备上是普通函数表达式
（它们有 `.prototype`）」，实测 `'prototype' in navigator.credentials.get === true`。

> **同一个文件里，两种 shim 对 `prototype` 的要求相反。** 不是随手写的，是照设备抄的。

### 三、顺带记下：`toString` 的伪装原版做得更细

```js
const real = nativeToString.call(this);
const match = V8_NATIVE.exec(real);
return match ? match[1].replace(V8_ACCESS…) : …;
```

它不存一段假字符串，而是**读真实源码再用正则改写**（`V8_NATIVE` / `V8_ACCESS`）。
我这一版用的是「存一条 `[native code]` 文本」，行为上等价但更粗 —— 记为后续可细化项。

### 四、这一轮的一句话

> 我一直把「像原生」当成字符串问题。这一轮发现它也是**语法问题**：
> 一个函数有没有 `prototype`，取决于它是怎么写出来的。
>
> **伪装不只藏在值里，也藏在值被创建的方式里。**

## 伪装不是查表，是**改写**（第 172 轮）

原版 `toString` 的补丁只有六行，但两个正则把它们说清了：

```js
const V8_NATIVE   = /^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$/;
const V8_ACCESSOR = /^function (?:get|set) (?=[^\s(])/;

const real  = nativeToString.call(this);
const match = V8_NATIVE.exec(real);
return match ? match[1].replace(V8_ACCESSOR, 'function ') + ' {\n    [native code]\n}' : real;
```

### 一、两件事

1. **V8 把访问器的角色写进源码** —— `function get userAgent() { [native code] }` —— **设备不写**，
   所以 `V8_ACCESSOR` 把 `get `/`set ` 抹掉（`(?=[^\s(])` 让 `Map.prototype.get` 这种真名叫 get 的不受影响）；
2. **设备把原生的源码打印成三行**，V8 打印一行 —— 所以每一段匹配上的源码都被**重排**成
   `function x() {\n    [native code]\n}`。

**这解释了为什么「存一条假字符串」不够**：在我这版里，`Function.prototype.toString.call(Map)`
原本答 `function Map() { [native code] }` —— **一行，V8 形状**，而这台设备声称是 WebKit。

### 二、实测（真浏览器）

```
patched   = "function canShare() {\n    [native code]\n}"     ← 我们的补丁
untouched = "function Map() {\n    [native code]\n}"          ← 没碰过的原生，被重排
accessor  = "function userAgent() {\n    [native code]\n}"    ← get 角色被抹掉
user fn   = "function named(x) { return x + 1; }"              ← 页面的函数原样
```

### 三、这一轮踩的坑（同一个 TDZ 撞了两次）

`G.__nativeMask = { …, maskGetter, maskProps }` 写在了 `maskGetter` 定义**之前** ——
和原版注释里警告的完全是同一个错误（"it is declared further down in this same block, so it is in its temporal
dead zone at this point"）。整段 IIFE 抛出，`__nativeMask` 变 undefined，`canShare` 直接消失。

**而 `JsGuard` 当时并没有覆盖 `NativeMask`** —— 守卫只查了五份 body，新的七份没在内。
于是它既没报语法错，也没报顺序错。已扩到**十二份**，并让守卫学会两件事：

- **正则字面量里的括号不算代码**（`[^(]` 与 `\(\)` 曾让正确代码报「括号不平衡」）；
- **字符串里的 `\n` 是正常 JS**，只有出现在代码位置的转义才是 bug。

### 四、这一轮的一句话

> 原版用六个字符（`get `）和一次重排，把「像原生」从**值**做到了**格式**。
>
> **同一条事实，换个排版就可能是另一个证据。**

## 外来接收者要**抛异常**（第 173 轮）

原版一句话点破了数据属性和访问器的差别：

```
// A native accessor is bound to its interface and throws when handed a foreign receiver. A getter that just
// closes over a constant answers anyone, and that difference needs no reference device to see: pull the
// descriptor off Navigator.prototype, call .get on {}, and a real browser throws where a naive override
// returns the user agent.
```

replica 之前把那几个成员装成**数据属性** —— `.get.call({})` 直接答值。一行守卫就能对上：

```js
if (!(this instanceof G.Navigator)) throw new TypeError('Illegal invocation');
```

实测：

```
values  = ["iPhone","Apple Computer, Inc.","5.0 (iP","string"]
foreign = ["platform:TypeError","userAgent:TypeError"]
shape   = ["get platform", 0, false, "function platform() {\n    [native code]\n}"]
```

### 一、这一轮踩的两个坑（都值得记）

1. **`{ get x() { … } }.x` 会立刻调用 getter** —— `this` 是那个对象字面量，守卫当场抛出，
   整段 per-name 循环被吞掉，什么都没装上。原版用的是
   `Object.getOwnPropertyDescriptor({ get m(){…} }, 'm').get` —— **取描述符，不取值**。
2. **从原型上读值是错的**：`Navigator.prototype.platform` 在真浏览器里抛出
   `Illegal invocation`（原生访问器绑定接口）。值要从**实例**读 —— `G.navigator[name]`。

3. 顺带：`asNative` 存进 FAKES 的源码也要**抹掉访问器角色**，
   否则我们自己的访问器答 `function get userAgent() {…}`，而设备答 `function userAgent() {…}`。

### 二、另一半：补丁用**路径**记录，供子 realm 重放

```js
const record = (target, name) => {
  const path = pathOf(target);          // ['Navigator','prototype'] / ['Intl','DateTimeFormat','prototype']
  if (path) PATCHES.push({ path, key: name, from: target });
};
```

`KNOWN` 二十三个构造器 + `Intl` 九个名字，构成「一个对象在另一个 realm 里叫什么」的答案。

> **同源 iframe 有自己的构造函数。** 不按路径重放，`iframe.contentWindow.navigator` 会把真实 Blink 值原样交回来。

### 三、这一轮的一句话

> 「我装了这个值」和「我装了一个原生访问器」之间，差的是**一次 throw**。
>
> **检测器不需要参考设备，只需要一个空对象当接收者。**

## 同源 iframe 有自己的构造函数（第 174 轮）

原版一句话说清了为什么要按**路径**记录补丁：

```
// Every patch is recorded with a realm-independent path ("Navigator","prototype") so it can be replayed into a fresh
// realm. An iframe gets its own constructors, so a same-origin child is otherwise completely unspoofed -- read
// iframe.contentWindow.navigator and the real Blink values come straight back.
```

```js
const pathOf = (target) => {          // ['Navigator','prototype'] / ['Intl','DateTimeFormat','prototype']
  if (target === G) return [];
  for (const name of KNOWN) {
    const holder = G[name]; if (!holder) continue;
    if (holder === target) return [name];
    if (holder.prototype === target) return [name, 'prototype'];
    for (const intl of INTL_NAMES) { … return ['Intl', intl]; … }
  }
  return null;
};
const record = (target, key) => { const path = pathOf(target); if (path) PATCHES.push({ path, key, from: target }); };
```

### 一、为什么「重跑整段脚本」不够

replica 原来靠「换一个 realm 再跑一遍 body」—— 能覆盖，但不精确：它只能补 body 碰过的对象，
而 `Intl.DateTimeFormat.prototype` 这类**三步路径**根本不在 body 的可达范围内。

journal 记录的是**「哪个对象上的哪个键」**，重放时按路径在新 realm 里解析出来，再把
**描述符原样**拷过去 —— 父窗口是数据属性的，子窗口也必须还是数据属性。

### 二、实测（真浏览器）

```
child = ["iPhone","iPhone",5,5,"function",true]
          ↑父     ↑子    ↑父 ↑子  ↑子有 canShare ↑且 [native code]
```

### 三、这一轮抓到的真 bug：品牌校验**不能跨 realm**

第一版守卫写的是 `this instanceof G.Navigator` —— 对**子 frame 的 navigator 是 false**，
因为子 realm 有自己的构造函数。于是重放到子窗口的访问器**在子窗口自己身上抛出** `Illegal invocation`。

改成正则无关的判据：

```js
let tag; try { tag = Object.prototype.toString.call(this); } catch (e) { tag = ''; }
if (tag !== '[object Navigator]') throw new TypeError('Illegal invocation');
```

`{}` 仍然答 `[object Object]` → 抛；任何 realm 的 navigator 都答 `[object Navigator]` → 通过。

### 四、这一轮的一句话

> 我写了一个「只接受自己人」的守卫，结果它把另一个房间里的自己人也挡在门外。
>
> **身份判据如果绑在某个具体对象上，它就不是身份判据，是地址判据。**

## 品牌校验抛出的错误，堆栈里不能有**自己的帧**（第 175 轮）

```
// A native IDL brand check throws from inside the engine, so the error's stack has no JS frame for the check at
// all: in JSC the top frame is the accessor itself, rendered 'get userAgent@[native code]', and the next frame is
// the caller. Ours is built in JS, so the stack carried the override's own frame -- at this script's URL, with a
// line and column -- and the Error wrapper's frame on top of it. Both are pure artifacts of this file.
```

### 一、机制

```js
// Captured ONCE, here. Reading Error.captureStackTrace at throw time would call whatever the page has installed
// on it -- announcing every brand-check throw and handing the probe a live reference to the installed getter.
const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
```

抛错时：`nativeCapture(err, getter)` 把 getter **及其以上**的帧全部丢掉，然后**插一行假的原生帧**：

```
TypeError: Illegal invocation
    at get platform (native)
    at …调用者的帧…
```

实测正是如此 —— 第二行就是 `at get platform (native)`。

### 二、为什么「只读一次」很重要

若在抛错时读 `Error.captureStackTrace`，就是调用**页面装上去的那个**：每抛一次等于通知一次，
而且把装好的 getter 作为第二个参数**交到探针手里**。

> **在一个可被改写的内建上取值，等于把遥控器交给对方。**

### 三、这一轮的一句话

> 原版连**错误的形状**都照抄：不只「抛什么」，还有「抛的时候栈看起来像谁抛的」。
>
> **栈也是一份供词。**

## 校验抛什么话、用什么判据、留什么栈（第 176 轮）

上一轮我把「抛 `Illegal invocation`」当成对的。这一段注释推翻了它，并且把**三件事**一次说清：

```
// The message follows WebKit's wording rather than Blink's "Illegal invocation", since WebKit is the engine being
// presented.
throw new TypeError('The ' + label + '.' + name + ' getter can only be used on instances of ' + label);

// The brand is checked with Object.prototype.toString, NOT instanceof. Child realms are patched by copying this
// descriptor into them, so the closure below keeps the PARENT's constructor -- and instanceof is realm-scoped, so
// `this instanceof Navigator` is false for a perfectly good navigator inside an iframe.

// Armed with an EMPTY head on purpose. Eliding our own frames is measured and safe; the native frame a real engine
// would show here is not -- WebKit adds no JS frame for an IDL brand check at all, so caller-frames-only is the
// faithful answer and inventing 'get x@[native code]' would be a guess in the payload.
ELIDE = [getter, ''];
```

### 一、三处修正

| 项 | 上一轮（R173–R175） | 原版 |
|---|---|---|
| 文案 | `Illegal invocation`（Blink） | `The Navigator.platform getter can only be used on instances of Navigator`（WebKit） |
| 判据 | 硬编码 `'[object Navigator]'` | **安装时**捕获 `brand = Object.prototype.toString.call(target)`，再用它比对 |
| 栈 | 插入假帧 `at get platform (native)` | **只删自己的帧**，不造假帧 —— 「造假帧是猜测」 |

### 二、为什么「造假帧」是错的

我上一轮为了让栈「像原生」插了一行 `at get platform (native)`。原版的判断更严格：

> eliding our own frames is measured and safe; the native frame a real engine would show here is not.

**能删的删，不能确定的不要编。** 这条标准比「像」更高：宁可少一行，也不多一个猜的。

### 三、`label` 从哪来

```js
const label = (target && target.constructor && target.constructor.name) || '';
```

不是写死 `'Navigator'` —— 同一个 `value()` 也装到 `Screen`、`CanvasRenderingContext2D` 等对象上。

### 四、这一轮的一句话

> 同一个错误，原版写的是**三种正确**：正确的话、正确的判据、正确的栈。我三样都差一点。
>
> **「差不多像」和「就是它」之间的距离，正好是一个探针。**

## `enumerable !== false` —— 一个表达式，不是常量（第 177 轮）

`value()` 的收尾这一段以前没读过：

```js
Object.defineProperty(getter, 'name', { value: 'get ' + name, configurable: true });
Object.defineProperty(target, name, {
  get: getter,
  configurable: true,
  enumerable: enumerable !== false,
});
record(target, name);
```

replica 一直写死 `enumerable: true`。**对本工作区装的每个成员恰好都对，但作为形状是错的** ——
原版把它做成参数：默认 `true`，调用点说 `false` 就是 `false`。

### 一、为什么默认是 `true`

因为设备就是那样：`for (var k in navigator)` 数得出 32 个键，这几个成员都在里面。
实测（真浏览器）：

```
[["platform",true,true,true,false],["userAgent",true,true,true,false],
 ["vendor",true,true,true,false],["appVersion",true,true,true,false]]
   ↑accessor ↑enumerable ↑configurable ↑无 value 字段
for (k in navigator) 里有 platform  →  true
```

### 二、同一段里还有两个形状

**`method()`** —— 替换函数的**arity 取自原函数**，而且原函数作为**第一个参数**交给 builder：

```js
const replacement = noProtoMethod(function () { return build.call(this, original, arguments); });
Object.defineProperty(replacement, 'length', { value: original.length, configurable: true });
asNative(replacement, name);
target[name] = replacement;
```

**`reseat()`** —— R165 已实现，逐行核对**完全一致**：

```js
const listed = order.filter((k) => kept[k]);
const rest = own.filter((k) => kept[k] && order.indexOf(k) < 0);
const seq = listed.concat(rest);
seq.forEach((key) => { try { delete proto[key]; } catch (e) { } });
seq.forEach((key) => { try { Object.defineProperty(proto, key, kept[key]); } catch (e) { } });
```

> 「设备没列出的成员保持相对顺序、落在末尾；不可配置的成员不动」—— 我们两周前就是按这句写的。

### 三、这一轮的一句话

> 三个形状，一个是我抄错（`enumerable`），两个是我早就抄对（`method` 的 arity、`reseat` 的顺序）。
>
> **核对的价值不只在发现错，也在确认对 —— 后者让「对」从运气变成依据。**

## 三十四个打点，不是「导航器加几个补丁」（第 178 轮）

把池子里所有 `method(target, name, build)` 的调用点扫出来 —— **34 个不同位置**：

| 区域 | 数量 | 内容 |
|---|---|---|
| canvas | 6 | `measureText` `fillRect` `arc` `getImageData` `getContext` `toDataURL` |
| webgl | 4 | `getParameter` `getSupportedExtensions` `getContextAttributes` `getShaderPrecisionFormat` |
| audio | 2 | `AudioBuffer.getChannelData` `HTMLAudioElement.canPlayType` |
| date-intl | 10 | 5 个 `Date.prototype`、`DateProxy` 三件、`Date.parse`、`Intl.DateTimeFormat` |
| core | 3 | **`Function.prototype.bind`**、**`JSON.stringify`**、**`Reflect.ownKeys`** |
| other | 9 | `matchMedia` `Performance.now` `createEvent` `StorageManager.estimate` `getComputedStyle` `getVoices` 等 |

### 一、为什么这张表本身是结论

看到 `Function.prototype.bind`、`JSON.stringify`、`Reflect.ownKeys` 都在里面，就知道
**「注入的边界不在 navigator」**：它改写的是**读的方式**，不只是**被读的值**。

> `JSON.stringify` 在名单里，意味着「你把 navigator 序列化给我看」这条路已经被算进去了。

### 二、本工作区已实现 13 个，缺 21 个

```
canvas 6 / webgl 1 / date-intl 3 / core 0 / other 2   →  13
```

`TheGapIsANumber` 把差额算成数字并且逐条列名 —— **缺口是一个清单，不是一种感觉**。

### 三、一个自查出来的错

我第一版写「webgl 只有 2 个」（`getParameter` + `getSupportedExtensions`），实测 4 个；
五个区域相加只有 25，剩下的 **9** 个没有归属。断言「和必须等于 34」立刻把它抓出来，
于是 `ByArea()` 多了一个显式的 `other` 桶，把那九个名字打出来。

> **给分类加一条「必须加总」的断言，是为了让「我漏了一类」变成红色。**

### 四、这一轮的一句话

> 三十四个打点里，只有三个在 `navigator` 上。我过去两周一直在 `navigator` 里打转。
>
> **清单能纠正的不是记性，是视野。**

## V8 的话 vs JavaScriptCore 的话（第 179 轮）

「core 三个」我以为是引擎加固，读完发现是**引擎方言**。原版的 `MESSAGES` 表只有四行，每一行都是
Blink 的句子会暴露身份的地方：

```js
const MESSAGES = {
  "nullProp": "null is not an object (evaluating 'null.x')",
  "notFunction": "(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
  "badArrayLength": "Array length must be a positive integer of safe magnitude.",
  "jsonCircular": "JSON.stringify cannot serialize cyclic structures."
};
```

### 一、五处补丁

| 项 | V8 | 设备（JSC） |
|---|---|---|
| 栈格式 | `    at fn (url:line:col)` | `fn@url:line:col` |
| `stack` 描述符 | 自有 **accessor** | **可写数据属性** |
| `Error.stackTraceLimit` | 10 | 100 |
| `new Array(-1)` | 另一句话 | `Array length must be a positive integer of safe magnitude.` |
| `JSON.stringify` 循环 | 另一句话 | `JSON.stringify cannot serialize cyclic structures.` |

还有一行小到容易漏：**`Function.prototype.bind`** —— V8 给绑定函数起名 `function bound () {…}`，JSC 不起。

### 二、为什么不用 `Error.prepareStackTrace`

```
// Error.prepareStackTrace would also reformat, but assigning it makes `typeof Error.prepareStackTrace` report
// 'function' where the device says 'undefined', trading one tell for another. Wrapping construction avoids that.
```

**用「更明显的假」换「不明显的假」，是亏的。**

### 三、这一轮踩的两个坑

1. **方法简写不能当构造函数**：`{ [name](...args) {} }[name]` 没有 `[[Construct]]`，
   `new Error('x')` 直接答 `Error is not a constructor`。错误构造器**必须**是函数表达式；
   `Array` 同理。R171 我要的是「没有 prototype」，这里要的是「能 new」—— **形状服务于用途**。
2. **JSC 的 `stack` 只有帧，没有消息行**：`toJscStack` 把不匹配的行丢掉是**对的**，
   消息在 `e.message` 上。实测 `get platform@<anonymous>:633:21`。

### 四、这一轮的一句话

> 我一直以为「伪装」是让值看起来对，这一轮发现还要让**错误的措辞、栈的排版、报错的类名**看起来对。
>
> **身份不只在成功路径上泄露，也在失败路径上泄露。**

## 一个 `reorder`，三个入口，五类规则（第 180 轮）

原版同时改写 `Object.getOwnPropertyNames`、`Object.keys`、`Reflect.ownKeys`，三者都走同一个
`reorder(target, names, enumerableOnly)`。规则有五类：

| 类 | 内容 |
|---|---|
| 全局对象 | 数字索引在前、引擎自身列表居中、本脚本新增的名字在后；`MAIN_FRAME_ONLY`（`_injected_scroll_helper`、`_injected_navigation`）只从**非顶层帧**删除 |
| `CSSStyleDeclaration.prototype` | 用一张录制表回答 —— 「支持的属性列表是最强的引擎指纹之一，两个引擎连接口都不一致」 |
| `CSSStyleDeclaration` **实例** | 只报**数字索引** |
| `ORDER` 表 | `{ match, names, drop }`，`wanted.concat(extra)`；`drop` 用来摘掉设备没有、又删不掉的引擎成员（WebIDL 常量不可配置） |
| Symbol | `OrdinaryOwnPropertyKeys` 把 symbol 放最后，所以字符串部分重排后再把 symbol 接回去 |

### 一、最锋利的一条实测

先把实例过滤到「设备的词汇」，结果 **1505** 个名字 —— 正确的 881 后面跟着 624 个重复：

> a name list that repeats 624 entries is not a vocabulary difference an obscure device could explain; **no engine
> enumerates a property twice**.

原因是 Blink 把 ~1200 个驼峰属性挂在**实例**上，WebKit 挂在 `CSSStyleProperties.prototype` 上，实例只拥有数字索引。

### 二、symbol 那一半

早先的守卫「遇到带 symbol 的对象就跳过」—— 而**每个接口原型都带 `Symbol.toStringTag`**，
于是 `getOwnPropertyNames` 与 `Reflect.ownKeys` 对**同一个对象**给出不同答案：

> which is a sharper tell than whatever the rule was hiding.

### 三、这一轮的实际交付：**建好，但没接线**

`KeyOrderTable` 与它的测试都完成了。接进组合链后，`mutation-check.py` **挂住**：
一条被变异关掉的「重放路由」会因为被包裹的 `Object.getOwnPropertyNames` 而永远等下去。

所以这一轮把那一行**注释掉**，并在 `TheLayerIsBuiltButNotWired` 里断言这个状态：

```csharp
Assert.Contains("// surfaceBody += KeyOrderTable.BodyJs();", bridge);
Assert.Contains("deliberately NOT WIRED", bridge);
```

顺带记录 Blink 的基线（未接线时的真实取值）：

```
sources           = [3,3]        （cloak 之后原生源码都是三行）
css non-numeric   = 750:751      （实例带着 750 个驼峰名 + 1 个数字索引）
```

**这两个数就是接线后要改掉的差距。**

### 四、这一轮的一句话

> 我把「规则读懂了」当成「可以接线了」，实测告诉我还差一步：**被包裹的基础设施会改变别人的失败方式**。
>
> **一个会让工装挂起的正确实现，比一个没接线的正确实现更糟。**

## 窗口上那十一个 `_injected_*`（第 181 轮）

把原版那张顶层名字表数出来：**1290** 个名字。前二十个里就有这些：

```
_injected_programmatic_form_submission_handler   _injected_clipboard
_injected_setup_frame                            _injected_passkey_controller
_injected_autofill_form_features                 _injected_scroll_helper
_injected_navigation                             _injected_gcrweb
_injected_choose_file                            _injected_print
gcrweb                                           __gCrWeb
```

这是 **Chrome for iOS 自己的注入钩子**。我们的窗口一个都没有 —— 这是一个**设备级指纹**，
再多 navigator 上的修补也补不平：页面只要 `Object.keys(window)` 就能看出来。

### 一、为什么不能写成常量

```
// The TOP-LEVEL list cannot be a constant, because api.js hands the host page's globals to hsw:
//   function sr(){ return Object.keys(window).sort().join(",") }      // called from initChallenge
// goes into the create-challenge message as `wdata`, the frame stores it as window.__wdata, and
// the wasm reads it back (4 Reflect.get per solve; the proof grows with it).
```

所以答案是**实时**键表，且顺序要刻意安排。`WINDOW_BASELINE` 就是那个机制：

```
// Every own name the engine reported for this window once this script had finished installing --
// document-start, before any page script. Assigned on the LAST line of the file. Whatever the
// engine reports later that is not in here, the page put there.
```

### 二、帧与顶层不是同一张表

```js
const FRAMED = (() => { try { return isWindow && G.top !== G; } catch (e) { return true; } })();
const MAIN_FRAME_ONLY = new Set(['_injected_scroll_helper', '_injected_navigation']);
```

「a frame advertised two names its real counterpart lacks」—— 所以子帧要**少两个**名字，
而不是多两个。

### 三、`CSS_DECL` 只有十一个名字

```
["constructor","cssText","cssRules","length","parentRule","item",
 "getPropertyValue","getPropertyPriority","setProperty","removeProperty","getPropertyCSSValue"]
```

对比上一轮读到的「~1500 属性访问器在 `CSSStyleProperties` 上」—— **原型短、实例只有数字索引**，
两句合起来才是 WebKit 的形状。Blink 没有 `CSSStyleProperties`，它把驼峰属性挂实例、另外暴露 `cssFloat`。

### 四、这一轮的一句话

> 我一直在 `navigator` 上找差距，而最大的差距在 `Object.keys(window)` 里 —— **十一个别人有、我们没有的名字**。
>
> **指纹不只在被读的对象上，也在「有哪些对象」这件事上。**

## 把十一个名字放到窗口上（第 182 轮）

上一轮只是**读**到了那十二个名字，这一轮**装上去**，并且验证两件页面能验证的事。

### 一、装在链尾，且必须装在链尾

```csharp
surfaceBody += WindowBaseline.BodyJs();   // 十一个全局名 + 基线
surfaceBody += MaskTargets.ApplyJs();     // 最后
```

理由写在 `SurfaceOrder` 第 10 步：**它们是全局名，而它报告的基线是「本脚本装完之后」的自有名字表**
—— 早装一步，基线就会漏掉后面装的东西。

### 二、实测

```
probe = [6,"object",false,12]
          ↑六个抽样名都在  ↑__windowBaseline 是对象  ↑framed=false（顶层）  ↑12 个注入名
Object.keys(window) 里有 __gCrWeb 和 _injected_clipboard  →  true:true
```

子帧：

```
child = [false,false,true,true]
          ↑_injected_scroll_helper 不在  ↑_injected_navigation 不在  ↑__gCrWeb 在  ↑gcrweb 在
```

**两个名字被去掉、其余保留** —— 正是「a frame advertised two names its real counterpart lacks」的反面。

### 三、为什么这比 navigator 上的修补更有分量

`navigator` 上的每个值都可能被一个「更聪明的」检测器怀疑；而 `Object.keys(window)` 的长度和内容
是**结构性**的：要么有这个名字，要么没有。

> 我们之前所有的修补，都发生在**页面已经知道存在的对象内部**；这一轮第一次改变**对象清单本身**。

### 四、这一轮的一句话

> 抄一个值，只能骗过读这个值的检测；抄一个**名字**，骗过的是「这台设备上有什么」的检测。
>
> **后者的成本高一个数量级，收益也是。**

## 两张窗口名单，和一次自我纠错（第 183 轮）

原版有两张表，不是一张：

| 表 | 读法 | 数量 |
|---|---|---|
| `WINDOW_ALL` | `Object.getOwnPropertyNames(window)` | **1062** |
| `WINDOW_ENUM` | `Object.keys(window)` | **228** |

上一轮我写的是 **1290** —— 那是我的正则把数组外围的引号串也算进去了。
**名单是证据，数字是我对名单的猜测。**

### 一、两条表的关系解释了一句我之前读不懂的话

```
// a name reported from the enumerable pass lands BEFORE the script globals and one reported only from the
// own-names pass lands after them. The iPhone reported ["__gCrWeb","hsw","__wdata","webkit"], with `webkit`
// LAST, after two script-created globals.
```

对照两张表就明白了：

```
WINDOW_ALL  最后一 项  = "webkit"      （自有名，非枚举）
WINDOW_ALL  倒数第二   = "__gCrWeb"   （枚举）
WINDOW_ENUM 最后一项   = "__gCrWeb"
WINDOW_ENUM 里没有     "webkit"
```

于是「`webkit` 排在两个脚本全局之后」不是错乱，而是**它只出现在自有名那一遍**。

### 二、十二个注入名**全部可枚举**

上一轮的十二个名字在两张表里都在 —— 所以手机的 `Object.keys(window)` 里就有它们。
「子帧要少两个」是**原版自己加的规则**，不是设备的属性。

### 三、这一轮的交付

- `WindowNameTable.Generated.cs`（27 KB）：两张表**逐字**生成，头部写明来源与「不许手改」；
- `WindowNameTable`：`AllCount` / `EnumCount` / `OwnOnly`(834) / `Injected`(12) / `LastOwnOnly='webkit'` / `Correction`；
- `WindowBaseline.RecordedNameCount` 从 1290 改为 **1062**，并新增 `RecordedEnumCount = 228`。

### 四、这一轮的一句话

> 上一轮我「数出了」1290，这一轮老老实实把数组取出来是 1062。差的那部分是**我的工具的产物**，不是设备的。
>
> **先让工具报数，再让数字进文档 —— 顺序反了，就会把自己的 bug 写成别人的事实。**

## 两个一直缺的 prune：window 和 document（第 184 轮）

replica 一直有 `navigator` 的 prune，**从来没有 window 和 document 的**。原版两处都有。

### 一、`GLOBAL_PRUNE`：`chrome` 是被删掉的

```js
const KEEP = new Set(['hsw','Raven','_sharedLibs','webkit','__wdata','__hcLoggerInstalled',
  '__hcWorkerProbeInstalled','__hcWorker','__hcCollector','__hcLogCalls','__hcSweepDelay']);
GLOBAL_PRUNE = (realm) => {
  nativeOwnNames(realm).forEach((key) => {
    if (!DEVICE_GLOBALS.has(key) && !KEEP.has(key)) { try { delete realm[key]; } catch (e) { } }
  });
};
```

`DEVICE_GLOBALS` 就是上一轮那 **1062** 个名字的 Set。凡是设备没有、又不在 KEEP 里的，删。

**为什么它是函数而不是一次性循环**：

> A child realm arrives with a fresh global carrying the full Blink surface again. Deleting only in this realm left
> `'chrome' in window` false at the top and TRUE inside an iframe — **and the challenge runs in an iframe**, so the
> frame that matters was answering honestly.

### 二、`DOCUMENT_PRUNE`：第一个请求就输了

```
['featurePolicy','hasPrivateToken','hasRedemptionRecord','hasTrustToken',
 'browsingTopics','requestStorageAccessFor','prerendering','startViewTransition']
```

> hCaptcha's checksiteconfig — the FIRST request of the whole flow, in plaintext, before a single sensor byte —
> carries `spst`, computed as `!(document.hasPrivateToken === undefined || …) && featurePolicy.allowsFeature(…)`.
> Private State Tokens and featurePolicy are Blink-only; WebKit has never shipped either, so a real Chrome-on-iOS can
> only ever answer 0. **We answered 1.** Verified against a device capture on the SAME sitekey AND the same api.js
> build: device spst=0, bot spst=1 — the only apples-to-apples comparison in the whole artifact set, and we were
> losing it on request one.

### 三、实测

```
probe = [false,"undefined",false,false,true,"object"]
          ↑无 chrome  ↑typeof 是 undefined  ↑无 featurePolicy  ↑无 hasPrivateToken  ↑mask 还在
child = [false,false]
          ↑iframe 里也没有 chrome  ↑也没有 featurePolicy
```

### 四、这一轮的一句话

> 我们花了很多轮让 `navigator.platform` 看起来对，而 `'chrome' in window` 一直是 `true` ——
> **一行就能问倒的，往往不是最复杂的那一行。**
>
> **最响的谎话，通常是最短的那句。**

## 页面的全局名不该被删，该被**放到后面**（第 185 轮）

上一轮留下了这个问题：`GLOBAL_PRUNE` 删「设备没有的名字」，那页面自己加的 `window.foo` 怎么办？

答案在原版的 `topList` 里 —— **它不删，它排**：

```js
const topList = (all, names, enumerableOnly) => {
  const base = FRAMED ? all.filter((n) => !MAIN_FRAME_ONLY.has(n)) : all;
  if (!WINDOW_BASELINE) return base.slice();
  const known = new Set(base);
  const indices = [], defined = [];
  names.forEach((name) => {
    if (WINDOW_BASELINE.has(name) || known.has(name)) return;      // 已知 → 不动
    (/^(0|[1-9][0-9]*)$/.test(name) ? indices : defined).push(name); // 页面加的 → 分类
  });
  const out = indices.concat(base, defined);                        // 索引在前，基表居中，具名在后
  …
};
```

### 一、基线必须是**最后一句**

```
// MUST stay the last statement. The snapshot has to include everything installed above, or the slots this script
// added itself would later be reported as something the page defined.
if (isWindow) { try { WINDOW_BASELINE = new Set(nativeOwnNames(G)); } catch (e) { } }
```

早一句，脚本自己装的东西就会被当成「页面的」，于是**被排到最后**——顺序立刻变形。

### 二、`webkit` 的补丁只在一处

```js
if (enumerableOnly && !FRAMED && names.indexOf('webkit') !== -1 && out.indexOf('webkit') === -1) {
  const at = out.indexOf('Raven');
  out.splice(at === -1 ? out.length : at, 0, 'webkit');
}
```

`webkit` 在自有名表里、**不在**枚举表里，所以枚举那一遍要显式插到 `Raven` 之前。

### 三、实测

```
shape  = ["function"…]         __topList 在、__windowBaseline.names 有 1000+ 项
order  = ["Raven",true,true]   页面具名全局落在最后，且排在 Raven 之前
splice = [876,-1,true]         webkit 被插到 876 位（本次 all 里没有 Raven，于是追加）
```

### 四、顺手抓到自己踩的坑

第一次跑 `__topList` 是 `undefined` —— 因为 `GLOBAL_PRUNE` 把它删了（它不在 KEEP 里）。
**这正是 prune 该有的行为**，也说明 KEEP 必须覆盖自研内部名：`__topList`/`__globalPrune`/`__documentPrune` 已补进 KEEP。

### 五、这一轮的一句话

> 上一轮我以为答案是「谁该被删」，这一轮发现答案是「谁该被排在后面」。
>
> **很多时候「删掉」是最粗的修法；排序才是原版的做法 —— 它保留了信息，只改变读到的次序。**

## 只包一层窗口，别的都不碰（第 186 轮）

R180 把整个键序层建完却**没接线** —— 接上之后 `mutation-check.py` 挂住：一条被变异关掉的「重放路由」，
在包裹后的 `Object.getOwnPropertyNames` 之下永远等下去。

这一轮只接**最小的一片**：

```js
['getOwnPropertyNames', 'keys'].forEach((name) => {
  const original = Object[name];
  const wrapped = { wrap() {
    const target = arguments[0];
    const all = original.apply(this, arguments);
    if (!G.__topList) return all;
    const isWindow = target === G || (!!target && target.window === target && !!target.document);
    if (!isWindow) return all;                       // ← 别的对象原样放过
    return G.__topList(all, all, name === 'keys');
  } }.wrap;
  …
});
```

### 一、为什么只包窗口就够

api.js 真正调用的只有两处，而且都对着 `window`：

```js
function sr(){ return Object.keys(window).sort().join(",") }   // → wdata → wasm
```

页面里其他对象（数组、DTO、`document.body`）的行为**一个字节都不变** —— 这正是「不挂工装」的关键：
被变异关掉的那条重放路由走的是普通对象，`isWindow` 为 false，直接 `return all`。

### 二、实测

```
probe = [true,"b,a","b,a",3]
          ↑页面变量排在最后 ↑普通对象顺序不变 ↑Object.keys 也是 ↑源码三行（已伪装）
RealmReplayTests + SurfaceRuntimeTests + PatchJournalTests → 21 条全绿（重放路由未受影响）
```

### 三、这一轮的一句话

> 上一轮我学会了「排序比删除更接近原版」，这一轮学会了**「只包该包的那一个对象」**比「包住所有对象」更安全。
>
> **能力越大越要先问：这个能力真的需要覆盖那么大范围吗？**
