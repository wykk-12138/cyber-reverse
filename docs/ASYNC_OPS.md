# 镜像的具名 async 操作清单（生成物，R839）

**来源**：`python analysis/ida.py str <keyword> --limit 300`，从元数据里的 `<Name>d__N`（编译器给 async 方法
生成的状态机类型名）中提取，按 `Flow` / `Task` / `Pop` / `Cart` / `Checkout` / `Order` / `Session` / `Signup`
八个词各取一轮，合并去重。

**这不是全量**：只覆盖含这八个词的，且每个词受 `--limit 300` 限制。
`>d__` 全量在 `Strings()` 里是 1304 条，而插件的响应上限在 300 与 3000 之间 —— 所以**这是一个有偏的子集**。

**名字级 ≠ 功能级**：复刻件可能用别的名字实现了同一件事（goal 明确允许命名不同）。
所以「absent」是**待解释**，不是「缺失」。

| | 数 |
|---|---|
| 具名 async 操作 | **115** |
| 复刻件按名字命中 | **48** |
| 名字级未命中的 | **67** |

## 未命中的（每条要写为什么）

每一条终将得到三种裁决之一：**改名实现了** / **本就不需要（哪条证据）** / **真缺**。

- `AddToCart2` — 待判
- `AddToCartAstro` — 待判
- `AddToCartBox` — 待判
- `AddToCartDummy` — 待判
- `AddToCartFrontend` — 待判
- `AddToCartNext` — 待判
- `AddToCartSvelte` — 待判
- `CheckCart` — 待判
- `CheckPreOrderState` — 待判
- `CheckSession` — 待判
- `CompleteOrder` — 待判
- `CreateCustomCheckout` — 待判
- `CreateRaffleCheckout` — 待判
- `DetectByteOrderMarkAsync` — 待判
- `ExitSessionAsync` — 待判
- `FetchTasks` — 待判
- `FinalizeCheckout` — 待判
- `GetAppCartToken` — 待判
- `GetAtlasSessionToken` — 待判
- `GetCartCookie` — 待判
- `GetCartCsrf` — 待判
- `GetCartId` — 待判
- `GetCartItemId` — 待判
- `GetCartLines` — 待判
- `GetCartPage` — 待判
- `GetCartValue` — 待判
- `GetCartValueApp` — 待判
- `GetCheckoutHtml` — 待判
- `GetCheckoutPage` — 待判
- `GetPaymentSession` — 待判
- `GetRegisterSession` — 待判
- `GetSessionData` — 待判
- `GetSessionToken` — 待判
- `GetSweepStakeCheckout` — 待判
- `HandleOrderResult` — 待判
- `LoadCheckout` — 待判
- `LoadCheckoutPage` — 待判
- `LoadGuestSignup` — 待判
- `PreloadCheckout` — 待判
- `ProcessOrderCommerce` — 待判
- `ProcessOrderPaypalCreditCard` — 待判
- `ProcessOrderStripe` — 待判
- `RaffleOrder` — 待判
- `RequestSessionToken` — 待判
- `RestartSession` — 待判
- `RpcCreateOrder` — 待判
- `SetupProxySession` — 待判
- `SetupTask` — 待判
- `ShopAddToCart` — 待判
- `StartCheckout` — 待判
- `StartCheckoutAstro` — 待判
- `StartDailyCheckInTask` — 待判
- `StartInvoiceCheckout` — 待判
- `StartPopNowViewTask` — 待判
- `StartSignupFlow` — 待判
- `StartTasksFlow` — 待判
- `StepByteOrderMarkAsync` — 待判
- `SubmitAdyenOrder` — 待判
- `SubmitCheckoutPayment` — 待判
- `SubmitOrderCommerce` — 待判
- `SubmitSession` — 待判
- `SubmitStripeOrder` — 待判
- `SubmitUnzerOrder` — 待判
- `ValidateCheckout` — 待判
- `VerifyCart` — 待判
- `VerifyCheckout` — 待判
- `_TryReturnTask` — 待判

## 命中的

`AddToCart`、`AddToCartApp`、`AddToCartAppDw`、`AddToCartGraphQL`、`AddToCartMulti`、`AddToCartPreload`、`AddToCartPreloadGraphQL`、`AddToCartStoreFront`、`AdyenSession`、`AuditCartAdd`、`AuditCheckoutBehaviour`、`BeginCheckout`、`CanPlaceOrder`、`CartApiObjectCreate`、`ClearCart`、`CreateCart`、`CreateCartGraphql`、`CreateCheckout`、`CreateCheckoutApp`、`CreateOrder`、`GenerateCheckout`、`GetCart`、`GetCartAvailabilityGraphql`、`GetCartDataList`、`GetCartDw`、`GetCheckout`、`GetCheckoutApp`、`GetCheckoutCaptcha`、`GetInstoreOrders`、`GetOrders`、`GetPayPalOrderId`、`GetSession`、`GetSessionApp`、`GetSessionDw`、`InitiateCheckout`、`Login_EnsureTaskAlive`、`PlaceOrder`、`ProcessOrder`、`RefreshSession`、`SaveSessionDw`、`SessionAsync`、`SessionHandover`、`StartEcomSession`、`SubmitOrder`、`SubmitOrderApp`、`SubmitOrderStripe`、`UpdateCart`、`VerifySession`

## 裁决记录

| 名字 | 裁决 | 依据 |
|---|---|---|
| `AddToCartBox` | 改名实现 | `PopMartFlow.AddToCartAsync` POST `/shop/v1/box/boxCart/addBoxListToCart`（`PopMartEndpoints.AddBoxListToCart`，`PopMartEndpoints.cs` 命中 `boxCart` 两次） |
| `AddToCartFrontend` | 改名实现 | `Frontend` 在 `StoreFlow.cs` 出现一次 |
| `AddToCartSvelte` | 改名实现 | `Svelte` 在 `RetailFlows.cs` 出现一次 |
| `AddToCartNext` | **探针无效，未判** | 用 `Next` 当探针，命中几十个文件 —— 那个词在 `NextPoll` 之类里到处都是，**它证明不了任何事** |
| `AddToCartAstro` | 待判 | `Astro` 在复刻件 0 命中 |
| `AddToCart2` | 待判 | `AddToCart2` 在复刻件 0 命中 |
| `AddToCartDummy` | 待判 | `Dummy` 在复刻件 0 命中 |

**方法**：对每个未命中名，取它最有辨识度的那个词去 grep 复刻件。
**探针必须有辨识度** —— `Next` 那种词到处都是，用它当探针等于什么都没查。

### 第二批（R841）：支付 + 会话 + 结账面，24 条

| 名字 | 裁决 | 依据 |
|---|---|---|
| `SubmitStripeOrder` | 能力存在，命名未对上 | `Stripe` 命中 9 文件 —— 探针无辨识力，但 Stripe 处理显然在 |
| `ProcessOrderStripe` | 同上 | `Stripe` 9 文件 |
| `SubmitAdyenOrder` | 能力存在，命名未对上 | `Adyen` 命中 13 文件（含 `AdyenGateway.cs`） |
| `ProcessOrderPaypalCreditCard` | 改名实现 | `Paypal` -> `NikePersistedOperations.cs` ×10 |
| `SubmitUnzerOrder` | 改名实现 | `Unzer` -> `Gateways.cs` ×3 · `PaymentGateway.cs` ×1 · `CandidateSteps.cs` ×1 |
| `ProcessOrderCommerce` | 能力存在，命名未对上 | `Commerce` 命中 10 文件 |
| `SubmitCheckoutPayment` | 能力存在，命名未对上 | `SubmitPayment` 命中 19 文件 |
| `GetPaymentSession` | 待判 | `PaymentSession` 0 文件 |
| `GetSessionToken` | 改名实现 | `SessionToken` -> `NikePersistedOperations.cs` ×4 |
| `RequestSessionToken` | 改名实现 | 同上 |
| `GetSessionData` | 待判 | `SessionData` 0 文件 |
| `CheckSession` | 改名实现 | `VerifySession` -> `StoreFlow.cs` ×2 · `RetailFlows.cs` ×1 · `StepAction.cs` ×1 |
| `RestartSession` | 待判 | `RestartSession` 0 文件 |
| `SetupProxySession` | 待判 | `ProxySession` 0 文件 |
| `GetAtlasSessionToken` | 待判 | `Atlas` 0 文件 |
| `GetAppCartToken` | 改名实现 | `CartToken` -> `ShopifyHeaders.cs` ×2 |
| `CreateCheckout` | 改名实现 | -> `StoreFlow.cs` ×1 · `StoreFlowSteps.cs` ×2 |
| `CreateCustomCheckout` | 待判 | `CustomCheckout` 0 文件 |
| `CreateRaffleCheckout` | 改名实现 | `Raffle` -> `RetailFlows.cs` ×11 · `DemandwareFlow.cs` ×5 · `DemandwareRaffle.cs` ×1 |
| `FinalizeCheckout` | 待判 | `Finalize` 0 文件 |
| `GenerateCheckout` | 改名实现 | -> `StoreFlow.cs` ×1 |
| `LoadCheckoutPage` | 待判 | `GetCheckoutPage` 0 文件 |
| `ValidateCheckout` | 待判 | `ValidateCheckout` 0 文件 |
| `VerifyCheckout` | 待判 | `VerifyCart` 0 文件 |

**新分出一类裁决：「能力存在，命名未对上」。**
`Stripe` 命中 9 个文件、`Adyen` 13 个、`Commerce` 10 个、`SubmitPayment` 19 个 ——
**这些探针作为「名字对应」无效，但作为「能力存在」是强证据。**
**探针失败有两种读法，必须分开：词没辨识力（这一种）vs 能力真的没有（零命中且换词仍零）。**

### 第三批（R842）：其余 39 条

| 名字 | 裁决 | 依据 |
|---|---|---|
| `AddToCart2` | 待判 | `SecondAdd` 0 文件 |
| `AddToCartAstro` | 待判 | `Astro` 0 文件 |
| `AddToCartDummy` | 待判 | `Dummy` 0 文件 |
| `AddToCartNext` | 改名实现 | `__NEXT_DATA__` -> StoreFlow.cs x1 |
| `CheckCart` | 待判 | `VerifyCart` 0 文件 |
| `CheckPreOrderState` | 待判 | `PreOrder` 0 文件 |
| `CompleteOrder` | 待判 | `CompleteOrder` 0 文件 |
| `DetectByteOrderMarkAsync` | 改名实现 | `ByteOrderMark` -> NetClient.cs x1 |
| `FetchTasks` | 待判 | `FetchTasks` 0 文件 |
| `GetCartCookie` | 待判 | `cartCookie` 0 文件 |
| `GetCartCsrf` | 待判 | `CartCsrf` 0 文件 |
| `GetCartId` | 探针无辨识力 | `CartId` 11 文件（FarfetchFlow.cs, FlowContext.cs, FootsitesFlow.cs, GoatFlow.cs …）—— 探针无辨识力，**命中文件需人工判** |
| `GetCartItemId` | 待判 | `LineItemId` 0 文件 |
| `GetCartLines` | 改名实现 | `CartLines` -> ShopifyGraphQl.cs x1 |
| `GetCartPage` | 待判 | `CartPage` 0 文件 |
| `GetCartValue` | 待判 | `CartValue` 0 文件 |
| `GetCartValueApp` | 待判 | `CartValue` 0 文件 |
| `GetCheckoutHtml` | 待判 | `CheckoutHtml` 0 文件 |
| `GetCheckoutPage` | 待判 | `CheckoutPage` 0 文件 |
| `GetRegisterSession` | 探针无辨识力 | `Registration` 9 文件（StepAction.cs, AccountAndAuthFamilies.cs, DemandwareControllers.cs, DemandwareFlow.cs …）—— 探针无辨识力，**命中文件需人工判** |
| `GetSweepStakeCheckout` | 待判 | `SweepStake` 0 文件 |
| `HandleOrderResult` | 待判 | `OrderResult` 0 文件 |
| `LoadGuestSignup` | 待判 | `GuestSignup` 0 文件 |
| `Login_EnsureTaskAlive` | 改名实现 | `EnsureTaskAlive` -> StoreFlow.cs x1 |
| `PreloadCheckout` | 待判 | `PreloadCheckout` 0 文件 |
| `RaffleOrder` | 改名实现 | `Raffle` -> DemandwareFlow.cs x5, DemandwareRaffle.cs x1, RetailFlows.cs x11 |
| `RpcCreateOrder` | 改名实现 | `CreateOrder` -> DemandwareStepMap.cs x2, StoreApiFamilies.cs x3, StoreFlow.cs x1 |
| `SetupTask` | 待判 | `SetupTask` 0 文件 |
| `ShopAddToCart` | 待判 | `ShopAddToCart` 0 文件 |
| `StartCheckout` | 探针无辨识力 | `InitiateCheckout` 7 文件（DemandwareStepMap.cs, FootsitesFlow.cs, MagentoFlow.cs, ShopifyFlow.cs …）—— 探针无辨识力，**命中文件需人工判** |
| `StartCheckoutAstro` | 待判 | `StartCheckout` 0 文件 |
| `StartDailyCheckInTask` | 改名实现 | `CheckIn` -> NikeSteps.cs x2, PopMartEndpoints.cs x2, StoreFlowSteps.cs x1 |
| `StartInvoiceCheckout` | 待判 | `Invoice` 0 文件 |
| `StartPopNowViewTask` | 待判 | `PopNow` 0 文件 |
| `StartSignupFlow` | 改名实现 | `Signup` -> DemandwareControllers.cs x4, DemandwareFlow.cs x2, DemandwareRaffle.cs x1 |
| `StartTasksFlow` | 待判 | `StartTasks` 0 文件 |
| `StepByteOrderMarkAsync` | 改名实现 | `ByteOrderMark` -> NetClient.cs x1 |
| `VerifyCart` | 待判 | `VerifyCart` 0 文件 |
| `_TryReturnTask` | 待判 | `TryReturn` 0 文件 |

**合计**：{'待判': 27, '改名实现': 9, '探针无辨识力': 3}

**「探针无辨识力」不是裁决** —— 它只说这个词太常见。
**那些命中文件必须人工看：它们是关于这件事的（能力存在）还是无关的（词没用）。**


### 累计（R840–R842）

| 批次 | 条数 | 改名实现 | 能力存在 | 探针无辨识力 | 零命中待判 |
|---|---|---|---|---|---|
| R840 | 7 | 3 | 0 | 1 | 3 |
| R841 | 24 | 9 | 5 | 0 | 10 |
| R842 | 39 | 9 | 0 | 3 | 27 |
| **合计** | **70** | **21** | **5** | **4** | **40** |

**70/71 已过一轮探针（剩 `GetSessionData` 一条在 R841 已判「待判」，实际 71 条全覆盖）。**

### 现在这 40 条「零命中」意味着什么，以及不再意味着什么

**它已经不再意味着「缺失」。** 探针在本会话里已经错过很多次：

- **`AddToCartBox`** 零命中一次后，靠 `boxCart` 找到 —— **改名实现**
- **`AddToCartNext`** 用 `Next` 无效，用 `__NEXT_DATA__` 命中 —— **换词才看见**
- **`SubmitAdyenOrder`** 探针命中过多，**而命中的文件里就有 `AdyenGateway.cs`** —— **能力很全**

**所以「零命中」现在的准确含义是：用我试过的这些词，在复刻件源码里找不到它。
它可能是真缺，也可能用的是我没想到的词。**

### 要往下走，探针不是工具了

**这 40 条要判，需要的是调用图证据 —— 镜像里哪个流程调用它。**
**而调用图需要从「函数地址」走，不是从「名字字符串」走。**
**这正是 R828 记的：名字字符串没有 xref，代码地址才有。**

**所以下一阶段的工具不是 `str`，是「按地址找调用者」。**


### 教训（三轮累积）

**探针表的四种结果不是四种「程度」，是四种「不同的东西」：**

| 结果 | 含义 | 能不能当结论 |
|---|---|---|
| 1–5 文件命中 | 找到候选，**文件名字本身就是证据** | 能，但要读那个文件 |
| >5 文件命中 | **词没用**，或**能力很全** —— 须看命中文件是否关于这件事 | 不能，要先分辨 |
| 0 命中 | 用这些词找不到 | **不能**，词可能不对 |
| 换词后仍 0 命中 | 仍未找到 | **仍不能** —— 只能说「我没想到词」 |

**表格里没有一格能单独读成「缺失」。**
**这就是为什么判据 (f) 那句「未覆盖的每条写为什么」难 —— 「为什么」不能是「我搜过没搜到」。**

## 逐流程步骤对照（R844）

### 逐流程步骤对照（R844，`analysis/flow_step_gap.py`）

| 流程 | 镜像步数 | 同文件里的重写数 | **同名** | 不同名 |
|---|---|---|---|---|
| nike | 16 | 17 | **2** | 14 |
| popmart | 24 | 11 | **0** | 24 |
| johnlewis | 19 | 24 | **5** | 14 |
| demandware-classic | 12 | 10 | **3** | 9 |
| demandware-dual | 15 | 10 | **2** | 13 |
| collectplus-app | 17 | 23 | **2** | 15 |
| structure-token-multi | 15 | 23 | **4** | 11 |
| structure-token-single | 12 | 23 | **4** | 8 |
| **合计** | **130** | — | **22 (16.9%)** | **108** |

### 这个 22/130 是什么，不是什么

**是什么**：镜像这 8 个流程的 130 个步骤名，只有 22 个在复刻件的对应文件里有同名重写。

**不是什么**：

- **不是「覆盖 16.9%」。** `StoreFlow` 基类声明了 165 个步骤，**流程没重写不等于没实现** ——
  基类可能有默认实现，或该流程确实不需要那一步。
- **不是我映射准确。** `collectplus-app` / `structure-token-*` 我映射到
  `RetailFlows.cs` / `StoreFlow.cs` 这种共用文件，**里面 23 个重写不属于任何一个具体流程** ——
  所以那三行的「重写数」偏大而「同名数」偏小，**是我映射粗糙的结果。**
- **不是缺陷清单。** Nike 那 14 个不同名，R843 已查明是**粒度**：镜像 10 个可分别失败的结账阶段，
  复刻件 3 个粗步。

**它是什么**：**一张可以逐条追的清单。** 每一条不同名，最终要落在三种裁决之一：

1. **粒度合并** —— 复刻件的某个粗步做了它（Nike 那 10 条属此类）
2. **基类默认实现** —— 复刻件基类已有，只是没重写
3. **真缺**

## 108 条的两刀切（R845）

### 108 条的两刀切（R845，`analysis/partition_steps.py`）

```
108 条不同名
 ├── 49 条：StoreFlow 基类已声明 → 只是没重写，不是缺口
 └── 59 条：基类也没有
      ├── 24 条 PopMart（抽签/展览/预约 17 + GetOrders/GetInstoreOrders 等 7）
      └── 35 条：需要行为裁决
```

**`StoreFlow` 声明 165 个虚步骤；108 条里 49 条就在那 165 个里面。**

| 流程 | 基类有（无缺口） | 基类没有 |
|---|---|---|
| nike | 5（`Authorize` `CreateBasket` `SubmitCustomer` `SubmitShippingMethod` `SubmitBillingAddress`） | **9** |
| popmart | 0 | **24** |
| johnlewis | 5（`GetPaymentPage` `SubmitOrderStripe` `PlaceOrder` `HandleRequiresAction` `GetStripePaymentIntent`） | **8** |
| demandware-classic | 3（`InitiateCheckout` `CreateStripePaymentMethod` `CreateOrder`） | **5** |
| demandware-dual | 4（`GetRates` `FindProductApp` `AddToCartApp` `SubmitOrderApp`） | **9** |
| collectplus-app | 8（`GetProduct` `GetSessionApp` `GetBasket` `SubmitDiscount` `LookupAddress` `SubmitDelivery` `SubmitBilling` `StartPayment` `GetPaymentUrl`） | **4** |
| structure-token-multi | 12 | 0 |
| structure-token-single | 8 | 0 |

**注意 `structure-token-*` 那两行：基类全有 —— 也就是说那 4 个「同名」之外，剩下的基类都实现了。
R844 里我对这两行的映射（指向共用文件）导致的「不同名」全部落在基类一侧。**


### demandware-dual 9 条：R124 已答完（R846）

**`replica/src/Cybersole.Stores/Flows/ScapiAppPath.cs`（R124）已经把 15 步按「哪一侧有端点」分完：**

| 类别 | 步骤 | 端点 |
|---|---|---|
| app 侧有端点 | `StartAppFast` · `StartAppSafe` | `/scapi/ShopperLogin/getAccessToken` |
| app 侧有端点 | `AddToCartApp` | `/scapi/ShopperBaskets/addItemToBasket` |
| dw 侧有控制器 | `GetSessionDw` · `GetCartDw` | `demandware.store` Cart-Get |
| dw 侧有控制器 | `AddToCartAppDw` | `demandware.store` Cart-AddProduct |
| **app 侧无端点** | `ApplyDiscountApp` · `GetCheckoutApp` · `GetRatesApp` · `SubmitOrderApp` | **无 —— 必须回到站点自身** |

**结构性事实（`ScapiAppPath.NoOrdersEndpoint`）：**

> the SCAPI family has no orders endpoint: create/add/update baskets and two login calls only,
> so an app-path order must cross back to the classic controllers

**而 `DemandwareFlow` 里 SCAPI 那条路是真的写着**（`AddToCartViaScapiAsync` + `scapi.token`/`scapi.basketId`/`scapi.organizationId`）。

**所以这 9 条不需要新工作 —— 三条映射到已实现的端点，四条本来就没有端点。**


### johnlewis 8 与 demandware-classic 5：已有 StepMap 答完（R847）

**`JohnLewisStepMap.cs`（R118/R119）** —— 19 步对 12 个 BFF 端点：

| 我列的 8 条 | 映射到 |
|---|---|
| `WebHandOver` · `SessionHandover` | `v2/sessions/web/handover`（共用） |
| `GuestCallback` | `v4/callback/guest` |
| `DeliveryPage` | `v3/orderforms/deliveries` |
| `CreateDelivery` | `v4/orderforms/deliveries`（与 `SubmitShipping` 共用） |
| `GetDeliveryMethods` · `SubmitDeliveryMethod` | `v3/orderforms/deliveries/details`（共用） |
| `AuthenticatePayment` | `v2/orderforms/payments` |

**该文件还说明「为什么 19 步多于 12 端点」：BFF 端点是服务端的资源，步骤列表是客户端的阶段。**
**3 步没有端点的理由也写了**：`GetHome` 是页面加载；`HandleRequiresAction` / `GetStripePaymentIntent` 是 **Stripe 自己的主机**。

**`DemandwareStepMap.cs`（R117）** —— 经典 12 步对控制器，我列的 5 条：

| 我列的 5 条 | 结论 |
|---|---|
| `GenerateCSRF` | → `CSRF-Generate` |
| `SubmitConsignment` | → `CheckoutShippingServices-SubmitShipping` |
| `SubmitShippingOption` | → `CheckoutShippingServices-UpdateShippingMethod`（R117 新查出） |
| `ConfirmPayment` | → `CheckoutServices-PaymentAuthorization`（R117 新查出） |
| **`GetPaymentMethod`** | **有意未映射** —— 镜像里唯一的支付读是 `CheckoutServices-FetchOrderModel`，正被 `GetCheckout` 占着 |

**同一文件还有一条更硬的结论**：`CreateStripePaymentMethod` 无控制器，因为
**「there is no `Stripe-*` controller anywhere in the image」** —— 镜像的支付控制器全是 Adyen 的
（`AdyenUpgrade-Authorize` · `Adyen-Adyen3DS2` · `Adyen-PaymentsDetails` · `AdyenComponents-Payment*`）。

### 只剩 collectplus-app 4 条

`CreateCheckoutApp` `GetDelivery` `GetCollectPlusLocations` `SubmitCollectPlus` ——
**`Flows` 目录里没有任何 CollectPlus 专属文件**（`RetailApiFamilies.cs` / `ServiceHosts.cs` / `ScapiEndpoints.cs` 是通用件）。


### collectplus-app 4 条：端点族已定位，而流程本身已登记为「未证」（R848）

**`StoreApiFamilies.cs` 里有这个族的端点，只是名字不含 CollectPlus：**

```
/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores   <- GetCollectPlusLocations
/component/singlepagecheckout/cac/submit                                 <- SubmitCollectPlus
/component/singlepagecheckout/continueToPaymentDetails
/component/singlepagecheckout/setDeliveryCountry
/component/singlepagecheckout/setDeliveryMode
```

**而 `LambdaWitness.cs` 已经把 `collectplus-app` 登记在 `Unwitnessed` 里：**

> Flows with no ownership witness — their gaps stay unresolved.
> `"popmart", "demandware-classic", "demandware-dual", "collectplus-app", "structure-token-multi", "structure-token-single"`

**所以这 4 条的正确状态不是「Unknown」，是「端点族已知、归属未证、仓里已登记」。**

| 步骤 | 端点 | 状态 |
|---|---|---|
| `GetCollectPlusLocations` | `getClickAndCollectOrCollectPlusPoiStores` | **端点已定位** |
| `SubmitCollectPlus` | `cac/submit` | **端点已定位（族内）** |
| `CreateCheckoutApp` | `singlepagecheckout` 族 | **族内，未一一定位** |
| `GetDelivery` | 同上 | **族内，未一一定位** |

**而未证的原因是流程级：没有 ownership witness。**


### PopMart：端点层完整，缺的是驱动它的步骤（R849）

**R116 的 `PopMartStepMap.cs` 已把 24 步里 14 步对到 `/shop/v1/*` 端点；而 `PopMartEndpoints.cs` 有 39 个端点，
那 14 个配对用的常量全在：**

| 步骤 | 端点常量 | 路径 |
|---|---|---|
| `StartDrawFlow` · `FindDraw` | `DrawScratchDetail` | `/shop/v1/drawScratch/detail?uniqCode=` |
| `EnterDraw` | `DrawScratchDraw` | `/shop/v1/drawScratch/draw` |
| `ChooseGoods` | `DrawScratchChooseGoods` | `/shop/v1/drawScratch/chooseGoods` |
| `FindMegaDraw` · `EnterDrawEvent` | `MegaDrawHit` | `/shop/v1/drawScratch/megaDraw/hit` |
| `RedeemMemberPoints` | `PointsRedeemDraw` | `/shop/v1/redeem/points_redeem_draw` |
| `RedeemLuckPoints` | `LuckyPointsDraw` | `/shop/v1/redeem/lucky_points_redeem_draw` |
| `FindExhibit` | `StoreOfflineDrawInfo` | `/shop/v1/storeOfflineDraw/info?alias=` |
| `EnterExhibit` · `EnterReservation` | `StoreOfflineDrawJoin` | `/shop/v1/storeOfflineDraw/join` |
| `FindDates` | `StoreTicketDates` | `/shop/v1/store_ticket/dateList` |
| `FindTimeSlots` | `StoreTicketMainPage` | `/shop/v1/store_ticket/mainPage?uniqID=` |
| `GetOrders` | `OrderList` | `/shop/v1/order/list?...` |

**`PopMartFlow` 的 11 个重写里没有一个是上面这些步骤。**

### 修正 R835–R838

**那几轮说「复刻件没有抽签面」。按证据，准确说法是：**

> **端点层完整（39 个端点，含全部 14 个抽签/展览/预约端点）；映射表完整（R116）；
> 缺的只是 `PopMartFlow` 里那 14 个驱动步骤的方法。**

**「没有抽签面」在端点层是错的，只在步骤层成立。**


### PopMart 14 个抽签步骤：证据够写几个，不够写几个（R850）

**镜像里能查到的 draw 参数记号：**

```
_uniqCode       0x1433803a5      字段名
currentUniqCode 0x146fda6d4
storeUniqCode   0x1471647ac
&storeUniqCode=1 0x146a85e4c     查询串片段
Drawno          0x143902b40      属性名
```

| 步骤 | 端点 | 够不够写 |
|---|---|---|
| `StartDrawFlow` | `detail?uniqCode=` | **参数有证据**（`uniqCode` + `storeUniqCode`）→ 可写 |
| `FindDraw` | `detail?uniqCode=` | 同上 → 可写 |
| `EnterDraw` | `drawScratch/draw` | **请求体无证据** → 不可写 |
| `ChooseGoods` | `drawScratch/chooseGoods` | **请求体无证据** → 不可写 |
| `FindMegaDraw` · `EnterDrawEvent` | `megaDraw/hit` | 不可写 |
| `RedeemMemberPoints` · `RedeemLuckPoints` | `redeem/*` | 不可写 |
| `FindExhibit` · `EnterExhibit` | `storeOfflineDraw/*` | 不可写 |
| `FindDates` · `FindTimeSlots` | `store_ticket/*` | 不可写 |
| `EnterReservation` | `storeOfflineDraw/join` | 不可写 |
| `GetOrders` | `order/list` | 可写（与复刻件 `GetOrders` 同样式） |

**所以：3 个可写（`StartDrawFlow` `FindDraw` `GetOrders`），11 个只有端点没有形状。**

**而那 11 个不写的理由与 R823 删 CSRF 兜底是同一条：**
**一个能发请求但不知道发什么的方法，比一个不存在的步骤更坏 —— 它会让「14 步已实现」这句话看起来成立。**


### 结构性发现：**一条通用序列 vs 八条按流程的序列**（R851）

**复刻件：`StoreFlowRunner` 驱动一条通用 21 步序列，所有流程共用。**

```
GetHome · GetCsrf · GetSession · FindProduct · FindVariant · CreateCart · AddToCart
GetCart · EditLine · InitiateCheckout · GetCheckout · SubmitEmail · SubmitShipping
GetShippingRates · SubmitShippingMethod · SubmitBilling · SubmitDiscount · SubmitPayment
GetPaymentToken · SubmitOrder · ProcessOrder
```

**镜像：每个流程有自己的序列**（`StoreFlowSteps`，带该流程自己的 `d__N` 序号）：

| 流程 | 步数 | 与通用 21 步的关系 |
|---|---|---|
| Nike | 16 | 有 `ValidateAddress` `CheckInventory` `GetShopperIp` `GetPaymentMethods` —— 通用序列里没有位置 |
| PopMart | 24 | 抽签/展览/预约 17 步 —— **结账序列根本表达不了** |
| JohnLewis | 19 | 有 `WebHandOver` `GuestCallback` `AuthenticatePayment` —— 流程专属 |
| Demandware 经典 | 12 | 与通用接近，但少 `SubmitEmail` 多 `ConfirmPayment` |
| Demandware 双路 | 15 | 有 `StartAppFast` `GetCartDw` 等双路词汇 |
| CollectPlus | 17 | 有 `GetCollectPlusLocations` `SubmitCollectPlus` |
| structure-token ×2 | 15 / 12 | 有 `GetStructureToken` `CalculateTaxes` `ProcessTransaction` |

**这就是「14 个抽签步骤写不进 `PopMartFlow`」的真实原因：不是方法没写，是 runner 里没有它们的位置。**

**也是 Nike「10 个细步 vs 3 个粗步」的真实原因：通用序列没有 `ValidateAddress` 这一步，只能并进 `SubmitShipping`。**


### ordinal 是**按流程编号**的（R852）—— R851 从 Inference 升为 Observation

**130 个 ordinal，只有 63 个不同，67 个跨流程重复：**

| 流程 | 范围 |
|---|---|
| JohnLewis | 20 – 39 |
| DemandwareDual | 26 – 47 |
| StructureTokenMulti | 29 – 47 |
| DemandwareClassic | 32 – 43 |
| CollectPlusApp | 33 – 50 |
| StructureTokenSingle | 40 – 51 |
| Nike | 41 – 58 |
| PopMart | 104 – 153 |

**六个流程挤在 20–51 且大量重叠** —— 若是同一编号空间，`d__32` 只能是一个方法；
**而这里 `d__32` 在 DemandwareClassic 是 `AddToCart`、在 CollectPlusApp 是别的步骤。**

**所以每个流程自己从低位数起：各自一个类、各自一套序列。**

**结论：R851 说的「镜像八条按流程的序列」成立，而它上一轮只是 Inference（因为「ordinal 递增是否即运行顺序」没证）。
现在有证了 —— 不是「递增即顺序」，而是「编号空间按流程分开」，这足以支持「序列是每条流程自己的」。**


### 镜像原文里的两条 blob（R853）

**`<AddToCart>d__32` @ `0x1434acef3`：**

```
AddToCart(32) · InitiateCheckout(33) · GenerateCSRF(34) · GetCheckout(35) · SubmitBillingAddress(36) …
```

**逐字对上 `StoreFlowSteps.DemandwareClassic`（`AddToCart 32 · InitiateCheckout 33 · GenerateCSRF 34 · GetCheckout 35 · SubmitBillingAddress 36`）。**

**`<AddToCart>d__22` @ `0x14338114f`：**

```
GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23) …
```

### 第一件事：R852 从「转写来的观察」变成「镜像原文」

**同一个 `AddToCart`，在两条不同的 blob 里是 `d__32` 与 `d__22` —— 同一个名字，两个编号，
分别在两段相邻运行里。所以编号确实是按流程给的，不是全局的。**

**R852 的那条警告（「那个观察来自 `StoreFlowSteps` 的转写，不是镜像原文」）到此解除。**

### 第二件事：还有一条序列没被记录

**`GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23)` 不匹配已记录的 8 条：**

| 流程 | `GetHome` | `FindProductMulti` |
|---|---|---|
| CollectPlusApp | 33 | — |
| StructureTokenMulti | — | 29 |
| StructureTokenSingle | — | — |
| **这条未命名序列** | **19** | **20** |

**所以镜像里至少还有第九条流程序列，而 `StoreFlowSteps` 里没有它。**


### 真实序列数：1301 条 `d__` 串里有 **67 段**递增运行（R854）

**`StoreFlowSteps` 只记了 8 条。下面是其中明显是流程的，以及它们是否在 8 条里：**

| 地址 | 步数 | 序列开头 | 在 8 条里？ |
|---|---|---|---|
| `0x14336febd` | 12 | `StartAppFast · StartAppSafe · GetSessionDw · GetCartDw · FindProductApp · AddToCartApp · AddToCartAppDw · SaveSessionDw` | ✓ demandware-dual |
| `0x143391b79` | 11 | `FindProduct · AddToCart · SubmitDiscount · GetCheckout · GetShippingRates · GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` | **不在** |
| `0x14336eca7` | 8 | `GetCsrf · GetCheckout · GetCheckoutHtml · AddToCart · AddToCart2 · SubmitDiscount · SubmitShipping · SubmitOrder` | ✓ demandware-classic |
| `0x14338f6c5` | 8 | `GetHome · AddToCart · SubmitDiscount · GetCartValue · SubmitShipping · SubmitBilling · SubmitInfo · SendManualNotification` | **不在** |
| `0x14336f85f` | 7 | `FindProduct · AddToCart · GetCheckout · GetShippingRates · SubmitShipping · SubmitPayment · SubmitOrder` | ✓ 与 classic 同族 |
| `0x14339468a` | 7 | `FindProduct · GetProduct · CreateCart · AddToCart · SubmitPayment · SubmitOrder · ProcessOrder` | **不在** |
| `0x1434ab921` | 7 | `GetSession · RefreshToken · CreateCart · FindProduct · GenerateCheckout · SubmitEmail · SubmitShipping` | **不在** |
| `0x1434b3109` | 7 | `FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · AddToCartMulti · AddToCartPreload` | **不在** |
| `0x14337a56e` | 6 | `SubmitPayPal · ApplyPayPal · ProcessPayPal · Process3DS · SubmitOrder · ProcessOrder` | **不在** |
| `0x14337bdc4` | 6 | **`StartSignupFlow · StartClearFlow · StartInStoreFlow · StartPopNowFlow · StartNormalFlow · CheckLogin`** | **不在**（R838 那条） |
| `0x1433835c8` | 6 | `SetEmail · GetCheckoutPage · GetShippingRates · SubmitShipping · SetPayment · SubmitOrder` | **不在** |
| `0x14338b455` | 6 | `GetHome · WebHandOver · SessionHandover · GuestCallback · DeliveryPage · SubmitShipping` | ✓ johnlewis |
| `0x1433937ec` | 6 | `CreateCheckoutApp · GetBasket · AddToCart · SubmitDiscount · LookupAddress · GetDelivery` | ✓ collectplus-app |
| `0x1433712d6` | 4 | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` | **不在** |
| `0x14337c7e5` | 4 | `StartDrawCheckFlow · FindDraw · CheckDraw · EnterDraw` | ✓ popmart 片段 |
| `0x143386376` | 4 | `StartEcomSession · Authorize · GetAccessToken · FindVariant` | ✓ nike |
| **`0x14345abb1`** | **4** | **`HandleResponse · GetScript · GetKasada · GetWorkTime`** | **不在 —— 且这是 R827/R828 追不到的那个 `HandleResponse`** |
| `0x14344be8a` | 5 | `GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc` | **不在 —— 风控指纹组** |
| `0x14344998c` | 4 | `SubmitProps · SubmitProps2 · SubmitWpt · SubmitSensor` | **不在 —— 指纹组** |
| `0x14348bfc5` | 4 | `MoveMouseAsync · ReleaseMouseOnScreenAsync · PressMouseOnScreenAsync · PressKeyAsync` | **不在 —— 人机行为组** |

**另外一批是库代码，不是流程**：`ReadFrameHeaderAsync/ReadPayloadAsync/ReadRawAsync`（TLS 读）、
`AuthenticateAsync/ConnectAsync/DisconnectAsync`（gRPC）、`ProcessMessagesAsync/HandshakeAsync`（IPC）、
`StartAsync/StartReceiving/StartSending/StopAsync`（流）。

### 所以

**67 段里，明显是业务流程的至少 20 段；`StoreFlowSteps` 的 8 条是其中一部分。**

**R844 那个 16.9% 的分母（8 条 / 130 步）是抽样，不是总体。**


### 8 条之外的段：一部分是**任务变体**，不是别的站（R855）

**镜像里有这三组运行，而复刻件的覆盖差别极大：**

| 变体 | 镜像里的步骤 | 复刻件 |
|---|---|---|
| **raffle** | （已在 `RaffleFlow`，R835 查过 `r419.com` / `lndg.page` / `nodnod.digital`） | **`Raffle` 96 处 / 7 个文件** |
| **sweepstake** | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` | **`SweepStake` 0 处** |
| **lottery** | `FindProductMulti · FindProductFlow · FindVariant · GetLotteryForm · SubmitLottery · AddToCartMulti · AddToCartPreload` | **`Lottery` 0 处** |

**而 `TaskType` 在复刻件只出现 2 次（`ThirdPartyDrivers.cs`），没有对应的任务型枚举。**

### 所以 R854 那 20+ 段里的归属有两种

1. **站**（Nike / PopMart / JohnLewis / Demandware / CollectPlus / …）
2. **任务变体**（raffle / sweepstake / lottery / PayPal 信用卡）

**而变体这一层，复刻件只做了 raffle 一种。**

**这也解释了 `ProcessPaymentPaypalCreditCard` 那 11 步 —— 它可能不是某个站的流程，是「PayPal 信用卡」这个支付变体。**


### 任务层是 5 个 `Start*Flow` + 3 个 `*Task`；sweepstake / lottery **不在**其中（R856）

**镜像原文：**

```
0x14337bdc4  <StartSignupFlow>d__57 · <StartClearFlow>d__58 · <StartInStoreFlow>d__59 · <StartPopNowFlow>d__60 · <St…
0x14337cdcc  <FetchTasks>d__187 · <StartDailyCheckInTask>d__188 · <StartPopNowViewTask>d__189
```

**编号连续（57–60、187–189），是分派层的入口，不是流程内部的步骤。**

**而 `SweepStake` / `Lottery` 出现在流程序列内部：**

```
0x1433712d6  <GetSweepStakeCheckout>d__40 · <GetSweepStakesShippingMethod>d__41 · <SubmitSweepStakesShipping>d__42 …
0x1434b3109  <FindProductMulti>d__32 · <FindProductFlow>d__33 · <FindVariant>d__35 · <GetLotteryForm>d__36 · <Submit…
```

**序号 40–42、32–36 —— 是某条流程内的步骤。**

### 所以 R855 那个 Inference 有答案

| R855 的猜测 | 结论 |
|---|---|
| sweepstake / lottery 是任务型 | **不是** —— 任务型是那 5 + 3 个 |
| 它们是某些站的结账变体 | **更像这个** —— 它们是流程序列内的步骤，序号在 32–43 段 |

**所以 R855 说的「三层」是对的，但 sweepstake / lottery 属于**流程层**，不是任务层。**
**三层应写成：任务型（5 + 3）· 流程（站／变体）· 风控。**


### 镜像 = **任务种类 × 店**；复刻件 = **只有店**（R857）

**镜像顶层，五个入口（`0x14337bdc4`，d__57–60 + 第五个）：**

```
StartSignupFlow · StartClearFlow · StartInStoreFlow · StartPopNowFlow · StartNormalFlow
```

**这不是五个站，是五种**任务种类**：注册 · 清仓 · 到店 · PopNow 抽签 · 常规结账。**

**复刻件的顶层（`Modules/Registry.cs`，312 行）：**

```
64 个 FlowStoreModule · 33 个流程类 · 33 个 shop id
enter · offspring · bodega · concepts · packershoes · socialstatus · undefeated …
```

**`Registry.cs` 里没有「任务种类」这一层 —— 顶层直接是店。**

### 所以

| | 镜像 | 复刻件 |
|---|---|---|
| 顶层 | **任务种类（5 种）** | **店（64 个模块）** |
| 第二层 | 站／变体的流程序列 | 33 个流程类 |
| 第三层 | 风控 | 风控（Kasada / Cloudflare） |

**这解释了为什么「20+ 段运行」认不出归属 —— 它们里有的是**种类**下的通用序列，不对应任何站。**
**`StartPopNowFlow` 对应 Pop Mart 的抽签；`StartInStoreFlow` 对应到店；`StartSignupFlow` 对应注册。
它们是**跨站的**，所以按站去找必然错位。**


### 复刻件有 `Task.Type` 字段，而**没有任何地方写它**（R858）

**`Cybersole.Core/Models/Tasks.cs` 里有：**

```csharp
public bool MonitorMode { get; set; }
public string Type { get; set; } = string.Empty;
```

**而全 `replica\src` 里没有一处 `.Type =` 给它赋值**（搜到的 `.Type ==` 全是 `Tls12Client` 的 record 类型与 `JTokenType`）。

**`TaskCombinationRequest`（创建任务的输入）只有 `Store`，没有种类字段：**

```csharp
public required string Store { get; init; }
public string? Url { get; init; }
public bool MonitorMode { get; init; }
// … 没有 Kind / Mode / Type
```

### 所以

| | 镜像 | 复刻件 |
|---|---|---|
| 种类 | **顶层五个 `Start*Flow`，真的有分派** | **`Task.Type` 字段存在，无人写、无人按它分派** |

**死字段比缺字段更糟：它让「种类这一层」看起来存在。**


### `CreateInputModel` 的 13 个属性里**没有 `Type`**（R859）

**镜像里属性以 `声明类型,程序集.属性名!访问器` 的形式出现，可以逐条列出来。
`Cybersole.Models.CreateInputModel` 扫到 13 个：**

```
AutoQuantity · Color · Currency · Input · MaxPrice · MinPrice · Minus
Plus · PriceCheckVisible · Quantity · Sizes · Symbol · TogglePriceCheck
```

**没有 `Type`。**

### 边界：这是**创建表单的输入模型**，不一定是任务模型本身

**所以这一步能说：镜像的创建表单里没有「种类」这个输入项。**
**不能说：镜像的任务对象没有 Type。**

**而这也回答了一个相关问题 —— 五个 `Start*Flow` 的种类不是在创建表单里选的。**

### 顺带：复刻件的任务字段是混合物

| 字段 | 镜像里有？ |
|---|---|
| `MonitorMode` | **有**（`get_MonitorMode` @ `0x143300b4a`） |
| `PriceCheck` | **有**（`get_PriceCheck` @ `0x143303724`） |
| `MultiCart` | **有**（`get_MultiCart` / `set_MultiCart` @ `0x1432fd992`） |
| `NameTemplate` | **0 命中** —— 复刻件自己起的名字 |
| `CheckoutDelay` | **0 命中** —— 同上 |
| **`Type`** | **`CreateInputModel` 里没有；任务模型未查** |


### 模型层从镜像取全；四个模型复刻件**全部齐备**（R860）

**镜像的模型 schema（按 `类型,Cybersole.Core.属性!访问器` 语法抽取）：**

| 模型 | 属性数 | 属性 |
|---|---|---|
| `BotTask` | 14 | MonitorDelay · MonitorMode · Product · Products · Profile · Properties · ProxyGroup · RetryDelay · Running · StartTime · Status · Store · Task · Timeout |
| `BaseCheckout` | 8 | Image · Price · Product · Properties · Size · Store · Timestamp · **Type** |
| `TaskGroup` | 17 | CaptchaSource · CheckoutLimit · CloudflareSolverId · LinkedDelays · MonitorDelay · Name · NextReset · Pinned · ProfileLimit · RetryDelay · Running · Tasks · Timeout · TotalCheckouts · TotalDeclines · UsageExpiry · Webhooks |
| `WebTask` | 2 | Account · Steps |

**复刻件对照：14/14 · 8/8 · 17/17 · 2/2 —— 全部齐备。**

### 所以 R858 那个「留还是删」有答案了

**镜像的 `Type` 在 `BaseCheckout`（结账记录）上，而**不在** `BotTask` 上（14 个属性里没有 Type）。**

**而复刻件的 `BaseCheckout` 也有 `Type`（8/8）。**

**所以 `Tasks.cs` 里那个没人写的 `Type` 是**冗余声明** —— 正确的那份在 `BaseCheckout` 上，已经有了。**

### 两条对优先级 ② 有用的 Observation

- **`TaskGroup.CaptchaSource`** —— 验证码来源是**任务组**级配置
- **`TaskGroup.CloudflareSolverId`** —— Cloudflare solver 也是任务组级
- **`TaskGroup.ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines`** —— 配额与计数也在组级

**即：风控配置的挂载点是 `TaskGroup`，不是单任务。**


### `BotTask.Task` 的类型：**R364 已经记为未定项**（R861）

**复刻件 `Tasks.cs` 里就写着：**

```
R364: the binding table names six more members on this model. Five have an inferable type; "Task"'
type could be an engine handle, an interface or a string id, and the name collides with System...,
so it stays named in docs/BINDING_BACKLOG.md.
```

**所以这不是新问题 —— 它从 R364 起就在 `BINDING_BACKLOG.md` 里。**

### 这四轮追的东西是同一批

| 轮 | 我在追 | 实际上 |
|---|---|---|
| R857 | 镜像顶层是「种类」还是「站」 | 是种类（5 个 `Start*Flow`） |
| R858 | `Task.Type` 是死字段 | 是，0 处写入 |
| R859 | 镜像有没有 `Type` | `CreateInputModel` 13 属性里没有 |
| R860 | `Type` 在哪个类型上 | 在 `BaseCheckout` 上，复刻件已有 |
| **R861** | **`BotTask.Task` 是什么类型** | **R364 已记为未定项** |

**而 `Task.Type` 与 `BotTask.Task` 是同一件事的两面：**
**`BotTask` 上有个成员叫 `Task`，类型未定；而 `Task.Type` 是复刻件多加的一个无人写的字段。**
**如果 `BotTask.Task` 的类里真有 `Type`，那复刻件那行就不是冗余，是**放错了位置**。**

**所以 `Task.Type` 删不删，取决于 `BotTask.Task` 的类型 —— 而那一条 R364 就没定。**


### 读 backlog 读到一个 **R504 就记下、从没被抬走的天花板**（R862）

`replica/docs/BINDING_BACKLOG.md` 第 25–78 行，42 条「复刻件里既无方法也无属性」的成员分三类，
**其中 B 桶 31 条的性质不是「没做」，是「用现有工具拿不到行为证据」：**

| 想拿的东西 | 为什么拿不到 |
|---|---|
| 描述符 → 引用它的注册代码 | **描述符无 xref**（`0x14320c54d` → 0 · `0x1436389fc` → 0） |
| 属性 setter 做什么 | **编译期内联，没有独立函数体** |
| `ICommand` 的行为 | **藏在委托初始化点，该点靠类型信息定位，类型信息也无 xref** |

**R504 的原话：**

> 这与 `PARITY_CLAIMS.md` 的 C7c（每个函数功能相等）一直是 Unknown 是同一件事。
> 要么接受"结构对等、行为 Unknown"，要么换一条完全不同的证据路线（例如运行期差分）——
> **运行期路线需要登录凭据**，那是 goal 允许停下来等 YG 的两件事之一。

### 所以「每个函数功能相等」这条判据的实际状态

| 层 | 能到 | 靠什么 |
|---|---|---|
| 函数数量对等 | **61.96%**（R831，`.pdata` 计数） | 可复算 |
| 结构对等（成员/类型/形状） | **多数已清** | `bind_diff` / `bind_scope` / `shape_audit` |
| **每函数功能相等** | **Unknown** | **静态路线已断（R504）；运行期需凭据** |

**这三层不是同一种完成度。前两层可以靠静态分析推到接近 100%，第三层不行。**

### 这不是新发现，但它是 (f) 与 (a) 之间那个一直没被写清的边界

**判据 (a) 说「类型级缺口、类型缺失 → 0」。这一条**能**做到，因为它问的是存在性。**

**判据的正文另有「每个函数功能相等」。这一条**做不到**，而且不是努力不够 —— 是 NativeAOT
把 setter 内联、把描述符做成无 xref 的数据，静态工具在原理上够不到。**

**所以完成判据里混了两种东西：存在性（可达）与行为（不可达，除非运行期）。**


### R504 的天花板**只挡 UI**；核心的行为有另一条路（R863）

**42 条里点名的类，全部是 UI：**

```
AccountGrid · AccountGroupView · ActionsModal · CreateGroupModal · DesktopNotification
GoogleLogin · InputModal · MessageBoxDialog · PublishTemplateModal · StoreGroupModal
```

**成员是 `Add` · `Clear` · `Close` · `Delete` · `Edit` · `OpenUrl` · `Save` · `Start` · `StartAll` ——
都是 UI 上的按钮动作。**

### 所以

| 层 | R504 的天花板挡不挡 |
|---|---|
| **UI 成员行为** | **挡 —— 而 YG 2026-11-16 明令「ui先不急着复刻」** |
| **核心流程行为** | **不挡 —— 走的是另一条路（见下）** |

### 核心为什么不受影响

**R504 的断点有三条：描述符无 xref、setter 内联、`ICommand` 委托点无类型信息。
这三条都是**UI 属性**的问题 —— 一个按钮的 `Save` 属性做什么，没有独立函数体可读。**

**而核心步骤不是属性，是**方法发一个请求**。它的行为可以从三处证：**

1. **端点串**（`/shop/v1/drawScratch/draw` 这类，R849 已核 39 个全在）
2. **步骤序列与 ordinal**（R851–R856：哪几步、什么顺序、归哪一层）
3. **请求参数记号**（R850：`_uniqCode` / `storeUniqCode` / `Drawno`）

**所以核心的行为证据是「它发什么请求」，而 UI 的行为证据是「它改什么状态」。
前者在字符串池与 `.pdata` 里，后者被内联吃掉了。**

### 这对「每个函数功能相等」意味着

**这条判据在核心层**部分可达**（能证发什么请求），在 UI 层**不可达**（除非运行期差分）。**

**而 YG 的优先级已经把 UI 排在第 4 位。所以核心做到底时，
「功能相等」在核心层是有证据的；剩下的行为 Unknown 集中在被暂缓的 UI 层。**


### 两个阻塞被当成一个：R504 的与 C7c 的**理由不同**（R864）

**`docs/PARITY_CLAIMS.md` L58：**

```
| C7c | 任意两函数的伪代码等价 | unknown | unknown | — | 缺原版符号（PDB / 调试信息）。Ghidra 也不能提供…
```

**而 L56/L57：**

| claim | 状态 |
|---|---|
| C7a 绑定成员能否在原版定位到**绑定声明** | **pass**（51/51） |
| C7b 成员**形状**（getter/setter）两侧一致 | **fail**（条数见 METRICS） |
| **C7c 任意两函数的伪代码等价** | **unknown**，理由：**缺 PDB / 调试符号** |

### 关键：C7c 是**一条整体 claim**，不是逐成员

**它写的是「任意两函数」，所以它不区分核心与 UI —— R863 那个「天花板有没有触及核心」的问题，
在这条 claim 上**没有粒度**可答。**

### 而它的理由与 R504 不同

| 来源 | 断点 |
|---|---|
| **R504**（B 桶 31 条） | 描述符无 xref · setter 内联 · `ICommand` 委托点无类型信息 |
| **C7c** | **缺原版符号（PDB / 调试信息）** |

**两个理由指向不同的东西：**

- **R504 是结构性的** —— NativeAOT 把 setter 内联了，没有函数体可读
- **C7c 是工具性的** —— 没有符号表，两个二进制之间的函数**配对**做不了

**而「配对」这件事，`rea` 里有专门的工具：`match_native_functions`（按唯一符号 / 相同字节 / CFG 指纹配对）
与 `compare_functions`（对已配对的一对做逐面比较）。AGENTS.md §1 把这两个列为「第二意见」。**

**所以 C7c 未必是 dead end —— 它可能只是没试过第二套工具。**


### `rea` 的 native provider 一个都没配 —— C7c 那条路卡在配置（R865）

**`mcp__rea__binary_session`：**

| provider | 状态 | 缺什么 |
|---|---|---|
| ghidra | `not_configured` | `GHIDRA_INSTALL_DIR`（Ghidra 12.x） |
| hopper | `unsupported_host` | win32 不支持 |
| **ida** | **`not_configured`** | **`REA_IDA_MCP_CONFIG` 指到 IDA MCP 注册** |
| kuna | `not_configured` | `REA_KUNA_COMMAND` |

**而 `match_native_functions` 要的两侧 `list_procedures` Evidence，只能由 native provider 产出。**

**所以 R864 说的「没试过第二套工具」，落到实处的答案是：工具在，provider 不在。**

### 而缺的那个刚好是我已经有的

**`ida` 那个 provider 只缺 `REA_IDA_MCP_CONFIG` —— 一个指向 IDA MCP 注册的配置。
而本会话的 IDA MCP 一直是通的（`analysis/ida.py` 直连 13337，`str` / `py` / `xrefs` 都在用）。**

**所以配它不需要装东西，只需要：**

1. **写一个 IDA MCP 注册 JSON**（指向 13337）
2. **设 `REA_IDA_MCP_CONFIG` 为它的路径**
3. **重启 REA**

**第 3 步是硬门槛 —— 而「DSH 重启 / 开关 MCP 条目」是 goal 允许停下来等 YG 的两件事之一。**

### 所以 C7c 的完整状态

| 层 | 状态 |
|---|---|
| 工具存在（`match_native_functions` / `compare_functions`） | **是** |
| 工具需要的 provider | **未配（ida 只缺一个环境变量）** |
| 配它要不要停 | **要 —— 重启 REA 属于允许停等 YG 的条目** |
| 配了之后能不能配出足够多函数 | **Unknown**（两侧是不同 AOT 框架） |


### 「实现那几个步骤」有前置条件：**先做结构改动**（R866）

**核了三处：**

| 位置 | `GetOrders` / `StartDrawFlow` / `FindDraw` / `EnterDraw` / `GetInstoreOrders` |
|---|---|
| `StoreFlow` 的 165 个虚步骤 | **一个都没有** |
| `StoreFlowRunner` 的 21 步序列 | **一个都没有** |
| `PopMartFlow` 的 11 个重写 | **一个都没有** |

**所以实现它们要三步：加基类虚方法 · 在流程里重写 · **加进 runner**。**

**而第三步是问题：runner 的序列是通用的 —— 加一条进去，**所有流程都会调它**。**

### 两条路都通向坏结果

| 做法 | 结果 |
|---|---|
| **加进 runner** | **所有流程都调 `GetOrders`**，包括那些没有订单概念的 —— 假调用 |
| **不加进 runner** | **方法存在但没人调** —— 正是 R858 那个「死字段」的形态，只是换成方法 |

**所以这不是取舍，是**前置关系**：**

> **要写这些步骤，必须先让 runner 能按流程取序列（R851 的做法 1）。
> 否则写出来的每一条，要么污染别的流程，要么是死代码。**

### 这条对优先级 ① 的顺序意义

**R850 说「3 个可写，11 个只有端点没形状」。这一轮补上：**
**那 3 个也**不是现在能写的** —— 写它们要先有结构。**

**所以优先级 ① 的下一步不是「写 PopMart 的步骤」，是：**

1. **给 `StoreFlow` 加 `IReadOnlyList<Step>`（或等价物），每条流程返回自己的序列**
2. **runner 改成按流程取序列，而不是一条固定 21 步**
3. **然后才能加 `GetOrders` / `StartDrawFlow` / `FindDraw`，并且它们只在该流程里跑**

**这是一个可界定的改动，但它动的是 1897 行的 `StoreFlow` 与 294 行的 runner —— 不是一轮能顺手做完的。**


### 结构改造的精确范围：**四项，而第四项才是真活**（R867）

**核出来的现状：**

| 事实 | 证据 |
|---|---|
| `StoreFlow` **没有任何序列** | 唯一的 `IReadOnlyList` 是 `Domains`（L20） |
| 165 个步骤是**方法**，不是「名字 → 委托」的表 | `public virtual … (\w+)Async(FlowContext, CancellationToken)` |
| 序列数据**早就有** | `StoreFlowSteps.Flow` 记录：`(string Store, IReadOnlyList<Step> Steps, FlowSource Source)`，`Names` 是派生（L60） |
| 有 6 个文件在用 `StoreFlowSteps` | `CandidateSteps` · `DemandwareStepMap` · `JohnLewisStepMap` · `LambdaWitness` · `PopMartStepMap` · `ScapiAppPath` —— **全是为了分析，没有一处驱动执行** |

### 所以改造是这四项

| # | 改什么 | 大小 |
|---|---|---|
| 1 | `StoreFlow` 加 `public virtual IReadOnlyList<string> StepSequence => Array.Empty<string>();` | **一行，纯加性** |
| 2 | 8 个流程 override 它，返回对应的 `StoreFlowSteps.X.Names` | **8 处，机械** |
| 3 | `StoreFlowRunner` 在有 `StepSequence` 时按它跑，否则回落到现有 21 步 | **改一处分支，保持其余 25 个流程行为不变** |
| 4 | **一张「步骤名 → 委托」的表**（`StoreFlow` 的 165 个方法要被按名字调用） | **165 条，机械但量大 —— 这才是真活** |

**第 4 项是缺口：`storeflowsteps.All` 给的是**名字**，而 runner 要的是**能调的方法**。
现在两者之间没有任何桥。**

### 而第 4 项有一个便宜的写法

**不必手写 165 条。`StoreFlow` 可以把表建在基类里：**

```csharp
protected Dictionary<string, Func<FlowContext, CancellationToken, Task<StepOutcome>>> StepDispatch() => new()
{
    ["GetHome"] = GetHomeAsync, ["GetCsrf"] = GetCsrfAsync, /* … 165 条 … */
};
```

**而这张表可以用反射或源生成一次性生成，不必手抄。**
**——但反射在 AOT 下受限（这正是原版的技术约束），所以更可能是源生成或手写。**

**这一条本轮不查（要看复刻件是否已开 AOT / trimming），但它是第 4 项成本的关键。**

### 所以改造成本的正确说法

**「给 `StoreFlow` 加一个列表」是一行；
「让 runner 按名字调那 165 个方法」是一张 165 条的表 + 一个 AOT 下的实现选择。**

**R866 说「动的是 1897 行与 294 行」——现在更准：动的是 1897 行里的一张派发表，与 294 行里的一个分支。**


### 序列机制已建成，而它量出的第一个数是 **0 / 24**（R868）

**改了产品代码（R866 之后第一次）。三处：**

| 文件 | 改了什么 |
|---|---|
| `StoreFlow.cs` | `StepSequence` 虚属性（默认空）+ `StepDispatch` 派发表（反射，165 条）+ `RunStepNamedAsync` |
| `PopMartFlow.cs` | `override StepSequence => StoreFlowSteps.PopMart.Names` |
| `tests/.../FlowSequenceTests.cs` | 新建，7 个用例 |

**`StepSequence` 默认空 → 其余 25 个流程行为不变（有测试钉住）。**

### 派发表怎么建的：一个踩坑和一个更正

**第一版按**具体流程类型**绑定（`flowType.GetMethods()`），测试 3 失败：**

> `ArgumentException: Cannot bind to the target method because its signature is not compatible with that of the delegate type.`

**原因：`Func<StoreFlow, …>` 的第一参数是基类，而重写在 `PopMartFlow` 上声明 —— 运行时拒绝。**

**改法：按 `typeof(StoreFlow)` 的声明绑定（`DeclaredOnly`），**虚分派自然走到重写**。
**副作用是正向的：派发表对所有流程**是同一张**，`Lazy` 一次构建，不需要按类型缓存。**

### 机制量出的第一个数

```
map.Count      = 165
sequence.Count =  24
implementable  =   0
```

**Pop Mart 那 24 个镜像步骤名与 `StoreFlow` 的 165 个方法名**零交集**。**

**这个数和 R844 的「22/130」是同一件事的两种量法，而这一次是同一层里的比较：
镜像列出的步骤 ↔ 复刻件真能调的方法。R844 那个是跨层的（步骤名 vs 通用序列名），所以它需要三条免责声明；
这一个不需要。**

### 测试（7 个，全过）

| 用例 | 钉住什么 |
|---|---|
| `AFlowWithoutItsOwnSequenceReportsNone` | 不重写的流程序列为空 → 其余 25 个流程行为不变 |
| `PopMartDeclaresTheImagesTwentyFourSteps` | **断言 24 而非前缀** —— 删条目不能悄悄通过 |
| `PopMartSequenceFollowsTheImagesOrdinals` | `GetOrders`(104) 在 `EnterReservation`(153) 之前 |
| `DispatchReachesBothOverriddenAndInheritedSteps` | 重写（`GetHome`）与继承（`SubmitBillingAddress`/`Init`）都能派发 |
| `DispatchIsNotSilentlyEmpty` | `Count >= 150` —— 反射查询崩了会被抓住 |
| `NoPopMartImageStepIsDispatchableYet` | **`map=165` · `sequence=24` · `implementable=0`** |
| `TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint` | 表非空，所以上面的 0 意味着「两个名字集不相交」而不是「表坏了」 |

**最后两个是一对：一个量缺口，一个证明前一个的 0 不是因为表空。**


### R868 那张反射表是**重复品** —— 删掉，改用 `StepActionRunner`（R869）

**查 `StepOutcome` 的形状时撞见 `StepActionRunner`（`Actions/StepAction.cs` L195）——
它早就在做同一件事，而且做得更好：**

| | `StepActionRunner`（已有） | 我的 `StepDispatch`（R868 写的） |
|---|---|---|
| 取方法 | `typeof(StoreFlow).GetMethods()` | 同 |
| 调用方式 | **`MethodInfo.Invoke`** | `Delegate.CreateDelegate` ← **撞上 `ArgumentException`** |
| 名字查询 | `Knows(step)` | `TryGetValue` |
| 逐步计时 | **有**（`Stopwatch` + `TaskStepRecord`） | 无 |
| `ctx.Step()` / `ctx.Finish()` 记录 | **有** | 无 |
| 取消 / 异常处理 | **有** | 无 |

**所以 R868 那个 `ArgumentException` 本来不必撞 —— 现成的实现用 `Invoke`，绕开了它。**

### 改法

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | **删** `BuildDispatch` + `DispatchTable` + `RunStepNamedAsync`；`StepDispatch` 改为 `=> StepActionRunner.Invokers`；新增 `CanRunStep(step) => StepActionRunner.Knows(step)` |
| `StepAction.cs` | `Invokers` 由 `private` 改 **`internal`** |
| `NikeFlow.cs` / `MagentoFlow.cs`（内含 `JohnLewisFlow`） | 各加 `override StepSequence` |

**现在三个流程声明序列：Nike 16 · PopMart 24 · JohnLewis 19。**

### 而其余 5 个序列没有落点

| `StoreFlowSteps.X.Store` | 有对应流程类吗 |
|---|---|
| `nike` · `popmart` · `johnlewis` | **有** |
| **`demandware-classic` · `demandware-dual` · `collectplus-app` · `structure-token-multi` · `structure-token-single`** | **没有** |

**这正是 R855 说的「它们不是站，是变体」—— 现在是一个可核对的表。**

### runner 分支：写的时候就踩出一个假成功

**`RunCheckoutAsync` 在 Init + AntiBot 之后加分支：有 `StepSequence` 就走它。**

**第一版直接调 `StepActionRunner.RunAsync`。而 `PopMartFlow` 声明 24 步、可跑 0 步 →
`RunAsync` 的空步列表循环一次也不进 → 返回 `Ok = true` → **报「结账成功」而什么都没做**。**

**这就是本项目反复在删的那个形态。修法：`runnable.Count == 0` 直接 `Error`，
消息里写明「24 declared, 0 implemented」。**

**顺便：把 `sequenceDeclared` / `sequenceRunnable` 写进 session，让跳过的步数一直可见 ——
不然「跑了 24 步里的 9 步」和「跑完了」在结果上一样。**


### 把「写之前先查」做成一个命令：`tools/where_is.py`（R870）

**R869 的教训是「先查有没有现成的，要包括**实现**」。而教训写成人话会被忘 —— 五轮里忘了五次。
所以做成一个能跑的东西，并且写进 `AGENTS.md §2.7c`。**

```
python tools\where_is.py <名字>
```

**它按四类报出所有位置：**

| 组 | 判据（只看文件名与路径，不看内容） | 回答什么 |
|---|---|---|
| **implementation** | 兜底 | **定义行为的地方 —— 先读这一组** |
| analysis | 文件名含 `StepMap` / `Steps` / `Path` / `Controllers` / `ApiFamilies` / `Endpoints` / `Witness` / `Candidate` / `Parity` / `Claims` | 已经算过的分析 |
| test | 路径含 `tests/` | 已钉住的行为 |
| doc | `.md` / `.txt` / `.json` | 结论可能已写下 |

**分组只看名字，不看内容 —— 所以可复现、可解释，不需要模型判断。**

### 它自己第一次用就暴露了一个 bug

**第一版没排除 `tools/.snapshots/` —— 那是 `snapshot.py` 每次改动前留的全量副本。
结果 `StepActionRunner` 报「39 个文件」，其中 29 个是历史快照。**

**修掉之后：**

```
StepActionRunner --word  -> 7 files
    implementation (3): StoreFlow.cs(5) · StepAction.cs(1) · StoreFlowRunner.cs(1)
    test           (1): StepActionTests.cs(4)
    doc            (3): VERDICT.md · BINDING_BACKLOG.md · HISTORY.md
```

**`PopMart` 那条也是干净的：31 个文件，implementation 5（`PopMartFlow` 18 处）、
analysis 4（`PopMartStepMap` 18 处 · `LambdaWitness` · `PopMartEndpoints` · `StoreFlowSteps`）。**

**分析组正确分出来的意义：R835–R838 那四轮我该看的就是这一组。**

### 它有一条边界写在文件头

**它不查镜像。**问「原版怎么做」是 `analysis/ida.py str`，这个脚本只答「复刻件里有没有」。
**两者混用会产生假的「不存在」（§2.7b 已经踩过四次）。**


### `where_is` 第一次真用：它先逼出一个疑问，再把疑问解掉（R871）

**目标：R850 判为「可写」的 `GetOrders`。按 §2.7c 先跑：**

```
python tools\where_is.py GetOrders   -> 12 files
    implementation: （无）
    analysis:       CandidateSteps.cs · PopMartStepMap.cs · StoreFlowSteps.cs
    test:           FlowSequenceTests · PopMartStepMapTests · StoreFlowDigestTests
    doc:            VERDICT · BINDING_BACKLOG · ENDPOINT_FAMILIES · docs/baseline/*
```

**implementation 组空 → 确认没人实现，可以写。而 analysis 组里的 `CandidateSteps.cs` 逼出一个疑问。**

### 那个疑问

`CandidateSteps.cs` 写着：

```
104 GetAccessToken / CartApiObjectCreate / GetOrders        (three classes collide)
```

> **ordinals are per class, so a bare ordinal cannot say which class owns a name.**

**如果 104 上三个名字撞号，那「`GetOrders` 是 PopMart 的第 104 步」这个归属就不牢 —— 而整条 PopMart 序列都建立在它上面。**

### 核出来的答案：撞号是真的，但归属不模糊

```
GetAccessToken>d__104    @0x1433737e2  → 同段 CartApiObjectCreate>d__105 · AddToCartGraphQL>d__106
GetOrders>d__104         @0x14337c7e5  → 同段 GetInstoreOrders>d__105 · StartDrawFlow>d__115
```

**ordinal 104 出现两次，在**两条不同的 blob**里 —— 是两个不同类各自的第 104 个方法。**

**所以 `CandidateSteps` 那句警告说的是「裸 ordinal 扫描分不清名字来自哪条 blob」，
而不是「`GetOrders` 归属不明」。`GetOrders` 和 `104` 在**同一个字面量**里，归属是直接的。**

**这条值得记，因为下次再看到「N 个类撞号」时，第一反应不该是「归属不可知」，
而是「它们是同一个字面量还是不同字面量」。**

### 写出来的东西

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | 新增 `virtual GetOrdersAsync` —— **默认显式失败**（不是静默成功） |
| `PopMartFlow.cs` | `override GetOrdersAsync` → `GET Origin + PopMartEndpoints.OrderList`，存进 `Session.Vars["orders"]` |
| `FlowSequenceTests.cs` | `165 → 166`（map）、`0 → 1`（coverage），测试改名 |

**响应体整份存下来，不解析** —— 响应 schema 没有证据，解析就是编一个出来。

### 测试自己红了两次，两次都对

| 次 | 为什么红 | 处理 |
|---|---|---|
| 1 | `implementable` 从 0 变 1 | 按该测试注释里预先写的规则：改成新数字并说明加了什么 |
| 2 | `map.Count` 从 165 变 166（我加了基类虚方法） | 两个数一起钉住：`166` + `24` + `1` |

**第二个失败是个好信号：加一个虚方法会动 map，写一个步骤会动 coverage。
两个数一起断言，就能区分「加了虚方法但没人用」和「写了一步」。**


### R871 说 `GetInstoreOrders`「likely 可写」—— 查了，**不可写**（R872）

```
python tools\where_is.py GetInstoreOrders -> 9 files
    implementation: PopMartFlow.cs (1)   ← 我 R871 自己写的注释，不是实现
    analysis:       StoreFlowSteps.cs
```

**`PopMartEndpoints` 里与订单/门店相关的常量：**

```
BuyNow          /shop/v1/order/pre/v2/buyNow
OrderCounter    /shop/v1/order/pre/counter
CanPlaceOrder   /shop/v1/shop/can/place/order
OrderList       /shop/v1/order/list?currentPage=1&pageSize=20
OrderDetail     /shop/v1/order/v2/detailV2?orderNo=
StoreOfflineDrawInfo /join /joinResult       ← 抽签，不是订单
StoreTicketDates / StoreTicketMainPage
```

**没有一个是「店内订单」。所以写 `GetInstoreOrders` 就等于编一个 URL。**

**R871 那句「likely（同段、`PopMartEndpoints` 里可能有对应常量）」**两半都错了**：
同段是真的，常量没有。而「可能」这个词正是问题 —— 它把一个没查的事写成了倾向。**

### 而同一批查询暴露了更好的目标

**R116 已经配对、常量又都在的两步：**

| 步骤 | 端点 | 查询形状 |
|---|---|---|
| `FindExhibit` | `StoreOfflineDrawInfo` | `?alias=` |
| `EnterExhibit` | `StoreOfflineDrawJoin` | 无查询，POST |

**两步都写了。**

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | 新增 `virtual FindExhibitAsync` / `virtual EnterExhibitAsync`，均**默认显式失败** |
| `PopMartFlow.cs` | `FindExhibit` → `GET info?alias=`（alias 从 session 取，缺则失败）· `EnterExhibit` → `POST join`（体 = 上一步存的 exhibit，缺则失败） |

### 两个「缺就失败」是刻意的

**`FindExhibit` 缺 `alias` → 失败，不是发空 alias。**
**`EnterExhibit` 缺 exhibit 体 → 失败，不是发空 POST。**

**理由一致：返回 200 的空请求会被读成成功。这是本会话第七次遇到同一个形态，而这次是在写的时候就避开的。**

### 覆盖变化

```
map.Count     166 -> 168
implementable   1 ->   3
```


### 再写四个：`coverage 3 → 7`，而选哪四个是有判据的（R873）

**判据：R116 配了 14 步端点；其中**查询形状写在常量里**的才可写（GET + 参数名固定）。
其余是 POST，请求体无证据。**

| 步骤 | 端点 | 形状 | 写了吗 |
|---|---|---|---|
| `StartDrawFlow` | `DrawScratchDetail` | `?uniqCode=` | **写了** |
| `FindDraw` | `DrawScratchDetail` | `?uniqCode=` | **写了** |
| `FindDates` | `StoreTicketDates` | 无查询 | **写了** |
| `FindTimeSlots` | `StoreTicketMainPage` | `?uniqID=` | **写了** |
| `EnterDraw` | `DrawScratchDraw` | POST | **没写** —— 请求体无证据 |
| `ChooseGoods` | `DrawScratchChooseGoods` | POST | **没写** |
| `FindMegaDraw` · `EnterDrawEvent` | `MegaDrawHit` | POST | 没写 |
| `RedeemMemberPoints` | `PointsRedeemDraw` | POST | 没写 |
| `RedeemLuckPoints` | `LuckyPointsDraw` | POST | 没写 |
| `EnterExhibit` | `StoreOfflineDrawJoin` | POST | **R872 写了** —— 体 = 上一步响应 |
| `EnterReservation` | `StoreOfflineDrawJoin` | POST | 没写 |

**所以「写了几步」不是均匀推进，是**按证据形状分批**：**
**GET + 固定参数名的先写；POST 一律等请求体有证据。**

### 两个缺参数就失败的步骤

**`StartDrawFlow` / `FindDraw` 要 `uniqCode`，`FindTimeSlots` 要 `uniqID`，全部从 session 取，
而**这个复刻件里没有任何地方往 session 放它们**。所以这三个在当前代码里会明确失败。**

**这不是缺陷，是当前状态的可读表达：**缺什么，失败信息就写什么。
**如果它们发空参数，服务器可能返回 200，而那会被读成「跑通了」。**

### 而 `uniqCode` 这个名字不是猜的

**R850 在镜像里找到 `_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1` 四个记号。
所以参数名有出处，只是**谁来填**没建立。**

### 数字

```
map.Count      168 -> 172
implementable    3 ->   7
sequence.Count  24 不变
```

**测试四数一起钉（172 / 24 / 7 + 七条 `CanRunStep`，每条标着哪一轮加的）。**


### `uniqCode` 是**模型字段**，不是产生者 —— 而「谁填它」静态查不到（R874）

**镜像里带 `uniqCode` 的串只有 5 条，全列出来了：**

| 地址 | 串 | 性质 |
|---|---|---|
| `0x1433803a5` | `_uniqCode` | **属性后备字段**（下划线前缀） |
| `0x146fda6d4` | `currentUniqCode` | 属性名 |
| `0x1471647ac` | `storeUniqCode` | 属性名 |
| `0x146a85e4c` | `&storeUniqCode=1` | 查询串片段（拼在某个 URL 后） |
| `0x146ab82f4` | `/shop/v1/drawScratch/detail?uniqCode=` | 端点 |

**三条是字段名，一条是端点，一条是查询片段。**没有一条是「产生它的那一步」。**

### 所以答案不是「没找到」，是「这个名字层问不出来」

**「谁把值填进 `_uniqCode`」是 setter 的行为。而 R504 已证：**

> 属性 setter 做什么 —— **编译期内联，没有独立函数体**

**所以这条路和 R504 的 B 桶 31 条撞上的是同一堵墙。**

**区别在于：B 桶是 UI 属性，本轮是模型属性 —— 墙一样，作用域一样（都是属性写入）。**

### 这一条把 R873 那个 Unknown 从「未查」变成「查了，原因是 X」

| R873 写的 | 现在 |
|---|---|
| 「`uniqCode`/`uniqID` 从哪来 —— Unknown」 | **Unknown，原因：它是属性写入，静态拿不到；名字层只有字段名** |

**这比「未查」有用：下一轮不该再花时间在同一层搜名字，要搜就得换层（运行期，需凭据）。**

### 三条可走的路，代价不同

| 路 | 代价 | 能拿到什么 |
|---|---|---|
| 继续在字符串池搜别的名字 | 便宜，但**名字层已到顶** | 大概什么也拿不到 |
| 从 `&storeUniqCode=1` 反推它在哪个 URL 后面 | 中 | **可能拿到「哪个页面/接口会带它」** —— 这还没试 |
| 运行期观察 | **需登录凭据** | 真值 |

**第二条是唯一还没试的静态路，而它有具体形态：`&storeUniqCode=1` 后面一定跟着某个 URL 或路径串。**
**本轮没查 —— 那是下一轮第一件事。**


### `&storeUniqCode=1` 是**查询片段表里的一条**，不是某个 URL 的拼接（R875）

**R874 说「找到它拼在谁后面，就知道哪个页面带它」。查了那一段（`0x146a85000`–`0x146a8C000`）：

**`335` 条，按字母序排列，全是查询片段：**

```
&paypal_client_cfci=   &pid=        &pl=5        &plannedCartLines=   &pm=no
&provider=             &quantity=   &quantity=1  &redirect_uri=       &referer=
&response_type=code&…  &returnUrl=  &rt_api=     &scope=              &sessionToken=
&shipping_address[zip]=               &shop=      &sitekey=            &sku=
&storeId=              &storeKey=    &storeUniqCode=1   &successURL=   &tempSaveID=
```

**这是一张**查表**：代码要拼查询串时从这里取片段，不是每条都绑在某个特定 URL 上。**

**所以 R874 那条路走不通 —— 不是「没找到宿主」，是**没有宿主**。**

### 而它带来一个更重要的更正

**`&storeUniqCode=1` 的值**写死为 `1`**。它是一个**标志位**（「要带 store uniq code」），
而不是一个计算出来的编码。**

**R850 把它和 `_uniqCode` / `currentUniqCode` / `storeUniqCode` 归成「draw 参数记号」，四者并列。
现在看它们**不是同一类东西**：**

| 记号 | 性质 |
|---|---|
| `_uniqCode` | **属性后备字段** —— 值在运行时 |
| `currentUniqCode` · `storeUniqCode` | **属性名** —— 值在运行时 |
| **`&storeUniqCode=1`** | **固定标志位** —— 值恒为 1，无需来源 |

**所以「`uniqCode` 从哪来」这个问题，因为这条被排除而变窄了：它不是三个未知里最难的那个，
它是**两个运行时属性**的问题，而第三个根本不需要来源。**


### 顺着 `_uniqCode` 往上读，读到一整个模型和它自己的序列（R876）

**R875 说请求体键不在端点旁。下一处自然是模型字段旁 —— `_uniqCode` 在 `0x1433803a5`。**

**`0x143380300`–`0x143380900` 有 51 条串，分三段：**

**① 一个模型的后备字段表（3 字节对齐，紧凑排布）：**

```
_turnstileKey  _userCouponId  _mpUserCouponId  _setNo  _boxes
_drawid  _uniqCode  _hasDrawEntry  _winner  _drawLogId  _drawGoodsId
_luckAlias  _memberAlias  _eventId  _dates  _slots  _blockedSlots  _startTime
_uuidRegex  _rpcFingerprint  _rpcAddressId  _rpcFreightExpressId  _rpcFreightAmount
_rpcPayAmount  _rpcWarehouse  _rpcAdyenPayId  _rpcAdyenClientKey  _rpcPayPalPayId  _tasks
```

**② 四个枚举/属性名：`AppMode` · `TimeZone` · `DrawLocation` · `DrawIdentityType` · `IsRpc`**

**③ 一条带 ordinal 的步骤序列，前面就是它的归属名：**

```
0x143380392  DrawStores                      ← 模型名
0x143380569  <Start>d__21                     21
0x143380581  <GetHome>d__23                   23
0x14338059b  <CheckVerification>d__24         24
0x1433805d0  <SubmitSaleRegistration>d__25    25
0x14338060a  <CheckLogin>d__26                26
0x143380676  <Register>d__27                  27
0x143380753  <CompleteRegistration>d__28      28
0x143380833  <GetCart>d__30                   30
0x14338085d  <ClearCart>d__31                 31
0x1433808c3  <FindProduct>d__32               32
0x1433808e2  <AddToCart>d__33                 33
0x1433808ff  <ReplaceProduct>d__34            34
```

**这是第九条序列，而它有名字：`DrawStores` —— R869 说「5 条序列没有落点」，这一条现在有了。**

### 它回答了两个问题，但都不是完整的

**① 请求体键可能是字段名去掉下划线。**
`_drawid` → `drawId`? · `_drawGoodsId` → `drawGoodsId` · `_eventId` → `eventId` · `_memberAlias` → `memberAlias`

**这是 Inference，不是 Observation。**字段名叫 `_drawid` 而 JSON 键可能叫 `drawId`、`DrawId` 或别的。
**就像 R859 那条：属性语法是 `Cybersole.Models.<Type>,Cybersole.Core.<Prop>!Getter`，
名字能对上但大小写和形态要另外证。**

**② `DrawStores` 是一个独立流程，不是 PopMart 的别名。**
它的序列从 21 开始（PopMart 的从 104 开始），前几步是 `CheckVerification` / `SubmitSaleRegistration` /
`CheckLogin` / `Register` / `CompleteRegistration` —— **是注册/登录流程，不是抽签流程。**

**所以 `DrawStores` 这个名字有误导性：它带的序列是「门店/发售注册」，不是「抽签」。**

### 两条排除掉的路

| 探针 | 结果 |
|---|---|
| 12 个 `/shop/v1` 端点是否都在 `PopMartEndpoints` | **12/12 都在，39 个端点无缺口** |
| draw 端点附近有没有请求体键 | **没有 —— 那一段全是按字母序的路径表** |

**所以剩下的工作不是端点发现，而是「键名与形态」。**


### 覆盖最高的一条序列，**没有任何店类**（R877）

**`DrawStores` 的 12 步，与 `StoreFlow` 的 172 个虚方法按名字对：**

| 步骤 | 在 `StoreFlow` 里 |
|---|---|
| `GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart` | **有（8 个）** |
| `Start` | **没有裸名** —— 但有 `StartDrawFlow` / `StartPayment` / `StartPayPal`，与 `Init` |
| `CheckVerification` | **没有** —— 最近的是 `VerifySession` |
| `SubmitSaleRegistration` | **没有** |
| `ReplaceProduct` | **没有** |

**所以 8 / 12 精确对上。**

### 而这条顺序该倒过来读

| 序列 | 覆盖 |
|---|---|
| **`DrawStores`（无店类）** | **8 / 12** |
| PopMart（有类，写了 7 步） | 7 / 24 |
| Nike（有类，0 步） | 0 / 16 |

**覆盖最高的那条序列，是唯一一条**连流程类都没有**的。**

**原因不是它更完整，是它更普通：**`GetHome` / `GetCart` / `FindProduct` / `AddToCart` 是所有流程共用的步骤**，
而 `DrawStores` 只在这上面加了注册/登录。所以它「覆盖高」是因为它**大部分是通用步骤**。

**这条要小心读：8/12 不说明 `DrawStores` 已实现，只说明它的步骤名大多是通用的。**

### 两个近似，但我没算进去

| 镜像 | 最近 | 为什么不算 |
|---|---|---|
| `Start`（21） | `Init` | **首步同名是一件推断** —— 镜像里别的序列首步都叫 `Start`，而 `StoreFlow` 叫 `Init` |
| `CheckVerification` | `VerifySession` | **「验证会话」与「验证账号」不是一件事** |

**如果把这两个算成对上，就会得到 10/12 —— 而那个数字是编的。**

### 而它为什么没有店类

**`Registry.cs` / `RetailModules.cs` 里搜 `DrawStore` / `drawstore` / `draw-store`：无输出。**

**所以 `DrawStores` 不是一个站，是一个**流程概念** —— 与 R855 那五条变体同类。**

**而 R849 说「Pop Mart 的 14 个抽签端点全在」。现在看：**
**`DrawStores` 是「门店发售注册」，PopMart 是「抽签」—— 两个不同的东西被同一个端点族服务。**


### 撤回：第九条序列**没有名字**，`DrawStores` 是属性名（R878）

**R876 写「第九条序列有名字：`DrawStores`」。错的。**

### 为什么错：那是把最近的**大写字符串**当成了归属

**R876 看到的是这个排布：**

```
14338037b  _alias
143380382  _documentNumber
143380392  DrawStores          ← 我把它当成序列名
14338039d  _drawid
1433803a5  _uniqCode
...
143380569  <Start>d__21        ← 序列从这里开始
```

**算一下字节：`_alias` 到 `_documentNumber` 隔 7 字节，`_documentNumber` 到 `DrawStores` 隔 16 字节，
`DrawStores` 到 `_drawid` 隔 11 字节。**

**`DrawStores` 是 10 个字符，加 UTF-16 结束符是 22 字节 —— 塞不进 11 字节。
所以它们是**各自独立的字符串对象**，不是同一块连续字符数组。**

**而 NativeAOT 的字符串字面量表按**首次使用顺序**排布 ——
相邻只说明「编译器先排到它」，不说明任何归属关系。**

### 那 `DrawStores` 是什么

**它夹在 `_documentNumber` 与 `_drawid` 之间，没有下划线前缀。**
**这一整段是**模型的名字清单**：`_xxx` 是属性后备字段，`DrawStores` 是没有后备字段的公开属性名。**

**所以它是一个**属性**，与「这条步骤序列属于谁」无关。**

### 那第九条序列的归属

**未知。**

**它的 12 个步骤（21–34）在 `StoreFlow` 里对上 8 个（R877），这个数字不变 ——
但 R877 里那句「`DrawStores` 12 步」的归属前缀要删掉。**

**而且因为归属未知，「要不要为它建一个流程类」这个问题（R877 说最该判）**本身就不成立** ——
连它属于谁都不知道，谈不上建类。**

### 这是同一形态的第 N 次

| 轮 | 把什么当成了什么 | 实际 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点 |
| R875 | 四个 uniqCode 记号并列 | 两个字段 + 一个常量 |
| **R876 → R878** | **相邻的大写串 = 归属** | **独立字符串对象，按首用顺序排布** |

**R875 我给自己的规则是「每次并列问一句：需要来源吗」。
这次需要的规则更简单：**先看两个串之间隔多少字节。**


### 任务种类是 **14**，不是 5 —— 而它顺带给了那条无名序列一个**语义**归属（R879）

**基线文件 `replica/docs/baseline/recovered_async_methods.txt` 有 1547 个异步方法名。
从里面按后缀捞：**

```
Start*Flow  共 14 个
  StartAccountRegistrationFlow   StartClearFlow        StartDrawCheckFlow
  StartDrawEventFlow             StartDrawFlow         StartExhibitFlow
  StartInStoreFlow               StartNormalFlow       StartPopNowFlow
  StartRaffleFlow                StartReservationFlow  StartRpcFlow
  StartSignupFlow                StartTasksFlow

Start*Task  共 2 个
  StartDailyCheckInTask          StartPopNowViewTask
```

**R857 当时在 `0x14337bdc4` 一个代码区里看到 5 个（`StartSignupFlow` / `StartClearFlow` / `StartInStoreFlow` /
`StartPopNowFlow` / `StartNormalFlow`），据此说「顶层是任务种类 × 站」。**

**现在看：那 5 个是 14 个里的 5 个。**「任务种类 × 站」的判断是对的，而种类的数量错了三倍。**

### 顺带：那条无名序列（R878 撤回了 `DrawStores` 命名）有了语义归属

**它的 12 步：**

```
21 Start · 23 GetHome · 24 CheckVerification · 25 SubmitSaleRegistration
26 CheckLogin · 27 Register · 28 CompleteRegistration
30 GetCart · 31 ClearCart · 32 FindProduct · 33 AddToCart · 34 ReplaceProduct
```

**而 14 个任务种类里有一个叫 `StartAccountRegistrationFlow`。**

**`CheckVerification` / `SubmitSaleRegistration` / `Register` / `CompleteRegistration` ——
这四步与「账号注册流程」这个名字是**语义**对上的。**

**所以那条序列很可能是 `AccountRegistrationFlow` 的，而不是 `DrawStores` 的。**

**这是 Inference，而它与 R876 那次错的 Inference 有一个关键区别：**

| | R876（错） | R879（这条） |
|---|---|---|
| 依据 | **位置相邻** | **步骤名与流程名语义一致** |
| 可反驳点 | **字节间隔 22 > 11，直接推翻** | **没有直接推翻的证据** |
| 强度 | **零** | **弱，但非零** |

**R878 的教训是「能用算术回答就不该靠推断」。这一条不能用算术回答 ——
所以它停在 Inference，标注清楚，不写进 `StoreFlowSteps`。**

### `Start` ≠ `Init`

**R877 说「`Start` 与 `Init` 是否同一件事，这是 8/12 与 9/12 之间那一步」。**

**基线里 `Start` 和 `Init` **两个名字都存在**（`Start` 一条、`Init` 一条）。
所以它们不是同一件事的两种叫法，`Start` 是镜像里一个真实存在而复刻件没有的方法。**

**→ 8/12 就是 8/12，不是 9/12。**


### 任务种类这一层建起来了：**14 + 2**，6 个测试；而文档守卫又一次抓到我（R880）

**R879 说最大的结构缺口是「任务种类这一层在复刻件里几乎没有对应物」。这一轮把它建起来。**

### 新增 `TaskKinds.cs`

| 类型 | 内容 |
|---|---|
| `FlowKind` | **14 个**：Normal · Clear · Signup · AccountRegistration · PopNow · InStore · Draw · DrawCheck · DrawEvent · Exhibit · Raffle · Reservation · Rpc · Tasks |
| `TaskKind` | **2 个**：DailyCheckIn · PopNowView |
| `TaskKindCatalog` | 每个成员 ↔ 镜像名（`StartNormalFlow` …）· `Resolve(imageName)` 往返 |

**每个成员都有基线出处（`recovered_async_methods.txt` 的 `Start*Flow` / `Start*Task` 行）。
没有一个是为了对称而加的 —— 这是 R876/R878 那两轮的直接后果：那里的错，是把相邻当成归属。**

**而 `FlowKind` 与 `TaskKind` 分开，是因为镜像自己的名字就分开：
flow 跑一条结账形状的序列，task 按计划做一件事。合并就重犯 R877 那个
「`storeOfflineDraw` 与 `drawScratch` 看着像一家」的错误 —— 而它们服务不同的东西。**

### 6 个测试

| 用例 | 钉住什么 |
|---|---|
| `ThereAreFourteenFlowKinds` | **14，不是 5** |
| `ThereAreTwoTaskKinds` | 2，且与 flow 分开 |
| `EveryMemberHasAnImageNameAndResolvesBackToItself` | 每个成员都有出处名，且往返一致 |
| `TheImageNamesAreDistinct` | 16 个名字互不重复 |
| `AnUnclaimedNameResolvesToNothing` | **不认得的名字返回 null，不返回「最像的那个」** |
| `TheKindAxisIsNotYetWiredToAnyFlow` | **还没接进任何流程，断言这个缺席** |

**最后一条是刻意的：如果我只写前五条，这个目录看起来像个已完成的功能。
第六条说清它现在只是一张清单 —— 而这正是 R850 「空壳方法」那条教训的形态：
宁可报缺席，不报看起来完整。**

### 而文档守卫第四次抓到我

**`DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue` 红了。**

**我在 R879 写了「`Registry.cs` 的 **64** 个模块」，而目录实际是 **63**。**

**这个守卫的历史（VERDICT 里自己记着）：R457 · R464 · R813 · **现在**。**
**四次同一个模式：引用旧轮次的数字时顺手写成「N 个模块」。**

**修法不是改那个 64 —— 是承认这个句式本身就是陷阱。
守卫扫的是 `(\d+)\s*(?:个模块|modules)` 且 `n >= 20`，它分不清
「目录有 N 个模块」这个断言和「某一轮处理了 N 个模块」这个事实陈述。**

**所以正确做法是：**在 VERDICT 里不写「N 个模块」，写「模块」或直接引 `METRICS.md`。****

**这一轮我只把 64 改成 63（四处文档）。下次该改成不带数字的说法。**


### 给那个句式加天花板 —— 而它当场抓到我算错（R881）

**R880 说：真正该修的不是数字，是「N 个模块」这个句式。**

**做法不是削守卫，是加一条**只允许降、不允许升**的天花板测试：**

```
TheModuleCountPhraseDoesNotSpread
  ceiling = 16
  「N 个模块」(N>=20) 的处数 <= 16，超出就红，消息写着「改这句话，不要抬天花板」
```

**为什么不削守卫：`TheModuleCountInVerdictMatchesTheCatalogue` 抓的是「数字不对」，
而它分不清「目录有这么多个」（断言）与「某轮处理了这么多个」（事实）。
削它会一起削掉真断言；加天花板只针对**增长**。**

**为什么不改历史：那 16 句今天全都对。改对的东西会把证据改成叙述。**

### 而它第一次跑就红了 —— 因为我的天花板是错的

**我先用一段 python 数出 13，把 13 写成 ceiling。测试报 16。**

**查下来：**我的 python 脚本数错了**（围栏剥离里用了 `chr(10)` 与反引号模式，结果不可靠），
**同一个文件、同一个正则，C# 数出 16。**

**我又用一份写进文件的干净脚本复核：raw 16 · 剥围栏 16 —— 都是 16。**
**所以 13 是我的测量错误，16 是真值。**

**这件事本身就是这条测试的价值：一个从**手工计数**得来的天花板，是一个用我没核对过的工具断言出来的数字。**

### 三句话

| 我要的 | 拿到的 |
|---|---|
| 一个不增长的句式 | 一条 ceiling 测试 |
| ceiling 的初值 | **被自己的测试纠正：13 → 16** |
| 一个记录 | 一条「别用手工计数当基准」的实例 |


### 5 个 `Start*Flow` 与 Pop Mart 的抽签步骤**同一个字面量 blob**（R882）

**R880 说接 `FlowKind → StoreFlow` 需要「哪个站有哪个 `Start*Flow`」。把这把那一段完整读出来：**

```
14337b02a  Login_EnsureTaskAlive · CheckSession · Authorize · Authenticate · SubmitTwoFactor · GetToken
14337b55e  _cartId _itemId _visitorId _marketPlace _language _basePath _locationId _priceId
           _priceSnapshot _productPrice _shippingPrice _locationData _forter
           _paymentApprovalId _paymentUri _paypalToken _product _scope _state
           _twoFactorEnabled _redirectUrl _accountKasada
14337bda2  <Start>d__56
14337bdc4  <StartSignupFlow>d__57  <StartClearFlow>d__58  <StartInStoreFlow>d__59
           <StartPopNowFlow>d__60  <StartNormalFlow>d__61
14337be54  <SendTwoFactor>d__65    14337be6a  <Register>d__67
14337bf2d  <GetConfig>d__68  <GetSession>d__69   14337bf51  <Login>d__70  <Login_EnsureTaskAlive>d__71
14337bff7  <CanPlaceOrder>d__72  <FindProductMulti>d__73  <FindProduct>d__74
14337c042  <FindProductMultiInstore>d__75  <FindProductInstore>d__76  <ClearCart>d__77
```

**而 R871 认定的 `GetOrders>d__104` 在 `0x14337c7e5`，R849 的 `StartDrawFlow>d__115` 也在同一段。**

**所以同一个 blob 里有 ordinal 56 到 115+。**

### 这看起来像「这个类支持 5 种任务」，但不是

**一个字面量 blob 可以同时装**基类和派生类**的字面量 ——
NativeAOT 把方法名字面量集中放，不按类分块。**

**所以能说的只有：**

| 能说 | 不能说 |
|---|---|
| 5 个 `Start*Flow` 与 Pop Mart 的抽签步骤**在同一片字面量区** | **「Pop Mart 支持这 5 种任务」** |
| 这片区域有 ordinal 56–61 与 104–116+ | 「这是同一个类」 |
| 字段里有 `_accountKasada` 与 `_forter` | 「这个类属于哪个站」 |

**R878 的教训直接适用：位置相邻不是归属。而这次相邻的粒度是**blob**，比字符串更粗 —— 证据更弱，不是更强。**

### 而字段透露的东西仍然有用

| 字段 | 读法 |
|---|---|
| `_accountKasada` | **Kasada token 存在账号级**（不是请求级临时变量） |
| `_forter` | **Forter 风控 token 也在模型里** |
| `_marketPlace` · `_locationId` · `_locationData` · `_basePath` | **门店/市场模型** —— 与 `FindProductInstore` 一致 |
| `_paymentUri` · `_paypalToken` · `_paymentApprovalId` | 支付态 |

**`AntiBotVendors.cs` 把 Kasada 与 Forter 都列了，而 `GetKasada` 那一行的示例串是 `Nike-Kasada-Version`。
所以「Kasada 出现在这片的字段里」不指向唯一一个站。**

### 为什么没写映射表

**R880 说要建 `FlowKind × Store → StoreFlow`。这一轮查完，**证据不够**：

**要写「PopMart 支持 Normal/Clear/Signup/PopNow/InStore」，我需要「这 5 个 `Start*Flow` 的 ordinal
与 PopMart 的 ordinal 属于同一个类」的证据。而 blob 共享给不出这个。**

**所以映射表这一轮**不写**。写它就是拿 blob 相邻当归属，重犯 R876。**


### `!Getter` 形态给出一份**类型清单**，而它顺手解了悬了六十轮的 `Task.Type`（R883）

**R859 发现过 `<Type>,<Prop>!Getter` 这个形态。这一轮把它枚举完：**

```
2,587 个 (声明类型, 属性名, 访问器) 三元组
  508 个声明类型
存成 docs/baseline/recovered_accessors_by_type.txt（带出处与边界说明）
```

**分布：`Cybersole.Ui.Views.*` 60 个类型 · `Cybersole.Models.*` 22 个 · `Cybersole.SmartActions.*` ·
`Cybersole.Global.Settings`（21 属性）· **`Cybersole.Stores.*` 0 个**。**

### 它解了 `Task.Type`

**R364 起 `BotTask.Task` 的类型一直是 Unknown；R858 发现 `BotTask` 里还有**一个没人写的死字段 `Type`**。**

**现在：**

```
Cybersole.Models.Drop   2 props   Time, Type
```

**`Type` 不在 task 上，**在 `Drop` 上**。而 `Drop` 只有 `Time` 与 `Type` 两个属性 ——
这是一个「什么时候、哪种」的模型。**

**所以 R364 那个 Unknown 的答案不是「`Task.Type` 是什么类型」，
而是「**`Type` 属于另一个对象**」。**

**而 `Cybersole.Models.CreateModel` 8 个属性里**没有 `Type`**：**

```
AccountGroup · AccountSelectionMode · IsEditing · MonitorDelay · MonitorMode
ProxyGroup · RetryDelay · StartTime
```

**所以「任务创建模型」不带类型；类型挂在它关联的 `Drop` 上。**

### 它同时也说明 R504 那堵墙的**准确边界**

**`Cybersole.Stores.*` 在这个清单里是 **0**。**

**所以可见的类型都是运行时为了**绑定**需要物化的成员：Avalonia 控件、视图模型、Models。
**`Stores` 里的流程类不参与绑定，所以它们的属性不产生这种字面量。**

**→ R504 说的「类型信息拿不到」是对的，但边界比当时说的更准：
不是「全都拿不到」，是「**只有参与绑定的成员拿得到**」。**

**而这对 R882 那个 ordinal→类 的问题**没有帮助** —— 因为流程类正在拿不到的那一半里。**

### 顺带拿到的东西

| 类型 | 属性 |
|---|---|
| `Cybersole.Models.Store` | **只有 `Url`** —— 一个很窄的模型 |
| `Cybersole.Global.Settings` | 21 个，含 `BrowserLimit` `MonitorConcurrency` `QueuePresentation` `SmartActions` `TaskGroupOrder` |
| `Cybersole.Models.TaskGroup` | 9 个，含 `CaptchaSource` `CheckoutLimit` `CloudflareSolverId` `ProfileLimit` `TotalCheckouts` `TotalDeclines` `UsageExpiry` |
| `Cybersole.Models.BaseCheckout` | `Properties` · `Timestamp` |


### `where_is` 这一轮失败两次 —— 于是把它的默认改了（R884）

**目标：把 R883 解出来的 `Task.Type` 落地。**

**第一次失败：`where_is Drop` 用的是**子串**匹配 —— 55 个文件，实现组 15 个全是
`DropDown` / `ProxyDrop` 之类的假命中。而**真正的 `Drop` 类型在 `Checkout.cs:44`，不在那 15 个里**。**

**第二次失败：我写了新的 `Drop.cs` 和 `DropTests.cs`，编译报 CS0101「命名空间已包含 Drop 的定义」。**

**§2.7c 那条规则我执行的是一次 `where_is`，而它给的是假答案。**

### 所以修的默认，不是习惯

```
before:  默认子串，--word 才整词
after :  默认整词，--sub  才子串
```

**修后实测：**

| 调用 | 文件数 | 含 `Checkout.cs` 吗 |
|---|---|---|
| `where_is Drop`（默认，整词） | **16** | **是（实现组 3 个之一）** |
| `where_is Drop --sub` | 55 | 是，但混在假命中里 |

**R884 的理由写进了 `--sub` 的 help 文本：**
**「查 `Drop` 时子串形式返回十五个文件，全是 `DropDown` 和 `ProxyDrop` 命中，
而名字正好是 `Drop` 的类坐在 `Checkout.cs` 里、不在其中。」**

**这正是 R881 的原则：改数字撑到下一次，改机制才不重复。**

### 落到产品上的两件测量

| 类型 | 镜像（基线） | 复刻件 | 结论 |
|---|---|---|---|
| `Drop` | `Time` · `Type`（2） | `Time` · `Stores` · `Type`（3） | **`Stores` 在基线里没出现** |
| `CreateModel` | 8 个属性 | 20 个，**8 个全含** | **镜像有、复刻缺 = 0；复刻多 12 个** |

**而 `Stores` 的缺席是**弱证据** —— R883 的边界刚说过：清单只收「参与绑定」的成员。
所以「镜像的 `Drop` 没有 `Stores`」这句话不能说。**

**`CreateModel` 那条是判据 (a) 的正面证据：镜像的 8 个属性复刻件一个不缺。**


### 「形状 78」这个数字的证据源是**抽样池**（R885）

**目标：答 R884 的问题 —— `CreateModel` 那 12 个多余属性是 XAML 需要还是我编的。**

**按 §2.7c 先查，三次都是同一个答案：工具已经有了。`tools/shape_audit.py` 做的正是
「镜像的访问器形状 ↔ 复刻件声明」的对比，而 `docs/METRICS.md` 里那个「形状 78」就是它的输出。**

### 但它的证据源是抽样池

```
shape_audit.py:  POOL = analysis/pe_strings.txt     ← 抽样（180,228 行，§2.7b 四次踩坑）
实测:            evidence: string pool (102 types, sampled)
```

**而 R883 的基线（`idautils.Strings()` 全量）有 **211** 个类型。**

**池子里少一半，而且少掉的那个包含了 `Cybersole.Models.CreateModel` —— 所以
「形状 78」这个数从来没包含过 `CreateModel`。**

### 于是我给它加了 `--baseline`

```
shape_audit.py --baseline   -> evidence: baseline (211 types)
```

**但结果暴露了我自己那份基线的缺陷：**

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池 | 102 | **78** |
| R883 基线 | 211 | **0** |

**0 不是好消息 —— 是**基线把 `Getter`/`Setter` 的区分丢了**。**

**R883 的 `dump_accessors.py` 写成 `<类型> TAB <数量> TAB <属性列表>`，
**访问器种类（Getter/Setter/Property）在格式里就没了**。而 `want_set` 依赖 `'Setter' in kinds`，
所以基线模式下这个检查永不成立。**

**→ 一份丢了字段的数据比没有数据更危险：它让检查从「78 个不匹配」变成「0 个不匹配」，
而两句话在报表上看起来像「修好了」。**

### `CreateModel` 的答案：5 条，不是 12

**用基线跑 `--extra --type CreateModel`：**

```
CreateModel   AccountId          replica=prop+set
CreateModel   ProfileId          replica=prop+set
CreateModel   ProxyGroupId       replica=prop+set
CreateModel   TaskGroupId        replica=prop+set
CreateModel   UseSmartActions    replica=prop+set
total review rows: 5
```

**所以 12 个多余属性里有 **7 个在基线里有证据**，5 个没有。**

**而这 5 个的共同特征：四个是 `*Id`（外键）· 一个是 `UseSmartActions`。
`CreateModel` 在镜像里用 `ProxyGroup`（对象）而不用 `ProxyGroupId`（键）——
**这是一致的：镜像传对象，复刻件传 id。****


### 「形状」从 **78 变 94** —— 数字变差，而那是修正（R886）

**R885 暴露：`METRICS.md` 的「成员形状差异」读的是抽样池。这一轮把三处一起修了。**

| 文件 | 改动 |
|---|---|
| `analysis/dump_accessors_v2.py` | **新建**：每行 `(类型, 属性, 种类)`，**保留 Getter/Setter/Property** |
| `replica/docs/baseline/recovered_accessors_by_type.txt` | **重生成**：1,275 行 (类型,属性) / **508 类型** / Getter 950 · Setter 687 · Property 950 |
| `tools/shape_audit.py` | `--baseline` 读新格式（种类不再丢） |
| `tools/metrics_report.py` | 调 `shape_audit.py` **加 `--baseline`** |

### 数字变化

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池（原） | 102 | **78** |
| 全量基线（现） | 211 | **94** |

**94 比 78 差 —— 而它更对。**

**多出的 16 条是抽样池里根本没有的类型上的真实差异。
换句话说：这个指标过去一直在**少报**，而「78」在报表上看起来比「94」好。**

### 这是本轮唯一的产品影响

**`docs/METRICS.md` 现在写 `成员形状差异 — total mismatches | 94`（L23 与 L218 两处）。**

**而判据 (a)「类型级缺口 → 0」的距离因此**变远**了 16 条 —— 这是正确方向上的变远。**

### 三层错的顺序

1. **R883**：Dump 时把带字段的数据压成不带字段（引入缺陷，症状是安静返回 0）
2. **R885**：发现证据源是抽样，但只加开关、没改调用方
3. **R886**：重生成基线 + 改调用方 → 指标从 78 修正到 94

**每一层都是上一层没走完的那一步。**


### 94 条形状差异分解成 **3 类 × 63 个成员** —— 而最大的一块是 `Close`（R887）

**R886 把数字从 78 修到 94。这一轮把那 94 条分类，因为「94」本身不是可行动的信息。**

### 按复刻件现状分三类

| `replica=` | 条数 | 意思 |
|---|---|---|
| **`?`** | **44** | **成员在复刻件里根本不存在** |
| `method` | **34** | 复刻件有同名**方法**，而镜像是可写属性 |
| `prop-get` | **16** | 复刻件只有 getter，镜像有 Setter 证据 |

### 按成员名归族：94 条 = 63 个成员

| 成员 | 条数 | 分布 |
|---|---|---|
| **`Close`** | **15** | **全 `?`** |
| `Delete` | 8 | 5 `?` · 3 `method` |
| `Edit` | 3 | 2 `prop-get` · 1 `?` |
| `Save` | 3 | 全 `?` |
| `MoveGroup` | 3 | 全 `method` |
| `Reset` · `Running` · `Add` · `OpenUrl` | 各 2 | 混合 |
| 其余 55 个成员 | **各 1** | — |

**Top 6 个成员占 34 条（36%）。**

### 而这些名字说的是同一件事

**`Close` · `Delete` · `Save` · `Edit` · `Reset` · `Add` —— **全是视图上的动作成员**。**

**镜像把它们标成 `Getter,Property,Setter`，也就是**可写的 `ICommand` 属性**；
复刻件里它们要么不存在（`?`），要么是普通方法（`method`），要么是只读属性（`prop-get`）。**

**所以 94 条不是 94 个独立缺陷，是**一个结构故事**：
视图的动作成员在镜像里是可写 `ICommand` 属性。**

### 而 `?` 那 44 条里有两条值得单独看

```
BotTask    Running    evidence=Getter,Property,Setter    replica=?
BotTask    Task       evidence=Getter,Property,Setter    replica=?
```

**`BotTask.Task` 就是 R364 那个悬案！**

**而 R883 的结论是「`Type` 属于 `Drop`」。现在看：`BotTask` 缺的成员是 `Running` 和 `Task`，
两个都是 `Getter,Property,Setter` —— 也就是说它们在镜像里是**可写属性**。**

**所以 R364 那个问题的答案更完整了：`BotTask.Task` 在镜像里是**可写属性**，
而 R883 说的 `Drop.Type` 是另一件事（任务类型 vs 任务本身）。**


### 「形状 94」里 **77 条是 UI** —— 而这个指标一直在把我推向优先级 ④（R888）

**R887 把 94 条归了族，但没问**它们属于哪个优先级**。**

**按声明类型所在的 csproj 分组：**

| 项目 | 条数 |
|---|---|
| **`Cybersole.Ui`** | **77** |
| `Cybersole.Core` | 12 |
| `Cybersole.Services` | 5 |
| **`Cybersole.Stores`** | **0** |

**YG 的优先级是 ① checkout flow → ② 风控 → ③ 请求指纹层 → ④ **其余（含 UI）**。
所以这 94 条的 **82%** 落在被明令缓的那一档里，而优先级 ①（`Cybersole.Stores`）是**零缺口**。**

**也就是说：R881–R887 这几轮我在提高一个指标的分辨率，而它的主项不在目标上。**

### 改了什么

```
shape_audit.py     + 按项目分组输出
                   + core mismatches: 17        ← Stores + Services + Http + Core
metrics_report.py  + 取 core mismatches
                   + patterns 白名单加一条

METRICS.md L23  成员形状差异 — total mismatches |  94
METRICS.md L24  成员形状差异 — core mismatches  |  17
```

**现在「差多少」和「差在哪一档」是两个并列的数。**

### 而这个 17 本身也值得看

| 类型 | 项目 | 缺的成员 |
|---|---|---|
| `BotTask` | Core | **`Running` · `Task`** |
| `Checkout` | Core | `Profile` |
| `CreateModel` | Core | `Inputs` |
| `Notification` | Core | `Timestamp` · `Title` |
| `IWebhook` | Core | `Events` · `ExtraFields` · `Name` · `Url`（全是 `prop-get`） |

**`BotTask.Running` 与 `BotTask.Task` 是其中两个，而 `Task` 就是 R364 那个悬案。**

**所以核心那 17 条不是零散的 —— 最大的一族是 `BotTask`，而它是任务模型的中心。**

### 一处实现错，值得记

**第一版按 `_dp.split(os.sep)[1]` 取项目名，而 `ROOT` 是绝对路径，所以 `_parts[1]` 是 `projects`。
输出成了 `projects 94` 一行。改成「取 `src` 之后那一段」才对。**

**而一个只输出 `projects 94` 的分组表**看起来像在工作**（有分组、有数字），
**只是每一行都是同一个错名字 —— 与 R876 那次「相邻当归属」同族：形状对，内容错。**


### 抽签 POST 的请求体**静态不可得** —— 最后一条路也关上了（R889）

**R873 说 7 个抽签 POST 步骤缺请求体，R876 说字段名可能是候选键但那是 Inference。
这一轮把剩下的三条路都试完了。**

### 三条路，全部关闭

| 路 | 做法 | 结果 |
|---|---|---|
| **属性名** | 在 R883 基线里搜 `Drawid` `DrawGoodsId` `UniqCode` `EventId` `Slots` … 共 13 个 | **0 命中** —— draw 模型的属性从没被物化 |
| **函数名** | `ida.py funcs <名字>` | **`funcs` 不按名前过滤**，三个不同模式返回同样的前 50 个 `sub_` —— 镜像无符号名 |
| **字符串 xref** | `ida.py xrefs 0x14337c7e5` | **`xref_count: 0` —— 「No cross-references to this address」** |

**第三条是决定性的。`<GetOrders>d__104` / `<StartDrawFlow>d__115` 那条字面量**没有任何代码引用它** ——
它是死串，是编译期留下的名字表，而不是被代码指向的数据。**

**这正是 R504 那个结论（描述符无 xref）在**这个具体地址**上的确认。
而之前 R504 说的是「属性写入拿不到」，这一轮把范围扩到「这些状态机名字本身也没有 xref」。**

### 所以 PopMart 的抽签前沿到了静态天花板

**已写 7 步（R871–R873）· 缺 7 个 POST 的体 · 缺 `GetInstoreOrders` 的端点。**

**而这三样都要求**运行期观察** —— 那需要原版登录凭据。**

**按 goal 的纪律，这是「可停下等 YG」的两类事之一。**

### 而优先级 ① 还有别的未结项，不需要凭据

| 项 | 状态 |
|---|---|
| 抽签/展览/预约步骤的体 | **静态不可得，需凭据** |
| `GetInstoreOrders` 用哪个端点 | **常量里没有；可能还有别的名字没搜** |
| 5 条变体序列（demandware-* / collectplus / structure-token-*） | **无流程类；R879 说任务种类这一层才有 14 个名字** |
| 其余 7 个流程的 `StepSequence` | **只做了 3 个** |

**所以「静态天花板」不是「无事可做」，是「这一条路到头了，旁边还有四条」。**


### 端点覆盖补到 **41 / 41**，而且两个方向都钉住了（R890）

**R889 之后转走不需要凭据的那条路。做法不是继续搜 `GetInstoreOrders` 的名字，
而是把镜像里**全部** `/shop/v1/` 字面量枚举出来，与常量类做全量对比。**

### 结果

| | 条数 |
|---|---|
| 镜像 `/shop/v1/` 路径 | **41** |
| `PopMartEndpoints` 常量（改前） | 39 |
| **镜像有、复刻缺** | **2** |
| **复刻有、镜像没有** | **0** |

**缺的两个：**

```
/shop/v1/store_ticket/reserve
/shop/v1/store_ticket/sessionList
```

**多了零个 —— 也就是说 39 个常量每一个都有镜像出处。这个方向为 0 比缺 2 更重要：
它说明这个常量类没有一处是编的。**

### 而 `GetInstoreOrders` 的答案也出来了

**那 41 条里没有任何 `store/*order` 或 `instore` 路径。**

**所以 `GetInstoreOrders` 的端点**不在 `/shop/v1/` 下** —— 它不是这个族的。
要找到它得换前缀搜，而「换前缀」这件事本身是一条新的线索：`GetInstoreOrders` 可能与
`/shop/v1/storeOfflineDraw/*` 同族，也可能走一个完全不同的前缀。**

### 加了什么

| 文件 | 改动 |
|---|---|
| `PopMartEndpoints.cs` | **+2 常量**：`StoreTicketReserve` · `StoreTicketSessionList`，注释写明体未知故无步骤使用 |
| `PopMartEndpointCoverageTests.cs` | **新建 3 用例** |

**三个用例钉住两个方向：**

| 用例 | 钉住 |
|---|---|
| `TheImageHasFortyOneShopPaths` | 41 条，且互不重复 |
| `EveryImagePathAppearsInTheConstants` | **镜像有的，常量里必须有**（缺 = 调不到的端点） |
| `EveryConstantAppearsInTheImage` | **常量里有的，镜像里必须有**（多 = 我编的） |

**第三个是这两个里更要紧的：一个多出来的常量**看起来像覆盖**，而它是编的。**


### 找到**第二个端点族** `/store/v1/` —— 5 条，其中两条能写成步骤（R891）

**R890 说 `GetInstoreOrders` 的端点「不在 `/shop/v1/` 下」。这一轮用同一招但换了锚：**
**在全部字面量里搜含 `order` 的路径。**

### 第一次扫错，第二次对

**第一版正则 `(/[a-zA-Z0-9_\-]+(?:/[...]*)+)` 太松 —— 抓到 GUID、base64、`3ds` 碎片，70 条里没有一条含 `order`。**

**改成**以词为锚**：`/[A-Za-z0-9_.\-/{}?=&%]*order[...]*`，一次就找到了：**

```
146ab926c   /store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20
```

**而那个前缀不只一条。枚举 `/store/v1/`：**

| 路径 | 对应步骤 |
|---|---|
| `/store/v1/store/cart/add` | — |
| `/store/v1/store/cart/del` | — |
| `/store/v1/store/cart/listByStore?actionType=1&GID=` | — |
| **`/store/v1/store/order/listV3?currentPage=1&status=1&pageSize=20`** | **`GetInstoreOrders`（105）** |
| **`/store/v1/store/product/detail?storeId=`** | **`FindProductInstore`（76）** |

**所以这是**第二个端点族**，与 `/shop/v1/` 平行 —— 而 R871–R890 的全部工作都只在第一个族里。**

### 写了什么

| 文件 | 改动 |
|---|---|
| `PopMartEndpoints.cs` | **+5 常量**（新族一整块） |
| `StoreFlow.cs` | **+2 虚方法**：`GetInstoreOrdersAsync` · `FindProductInstoreAsync`，均默认显式失败 |
| `PopMartFlow.cs` | **+2 override**：GET，查询形状取自常量 |

### 而 `implementable` 只从 7 到 **8**，不是 9

**测试红了，报 `Expected: 9, Actual: 8`。**

**原因：`FindProductInstore` **不在 PopMart 那 24 个名字里**。**
**它是 ordinal 76，属于 R882 读到的那条更早的字面量段（56–77，含 5 个 `Start*Flow`），
而 PopMart 自己的段从 104 起。**

**所以：**已实现 ≠ 在序列里**。**
**测试现在两个都钉：`CanRunStep("FindProductInstore")` 为真，而 `StepSequence` 不含它。**


### 端点族覆盖表：**56 族，32 族完全没有** —— 而第一次报的是 40（R892）

**R891 说「还有没有第三个族，我只在 PopMart 的域里找过」。这一轮枚举全部 `/word/vN/` 形状，得到 56 个 API 族。**

### 而第一次的分级是错的

**第一版判据是「整条路径作为字面量出现」—— 于是报出 **40 族完全没有**。**

**抽查 `__bff__` 时发现它其实在：`JohnLewisBff.Base = ".../bff/"` + 相对路径 `"v2/orders"`。
**同一个端点，存法是「基址 + 相对路径」，而不是完整字面量。****

**改成分三级：**

| 级 | 判据 | 族数 |
|---|---|---|
| **exact** | 整条路径是字面量 | 3 |
| **relative** | 族名在源码里，或「去掉族前缀的尾部」是字面量 | 21 |
| **absent** | 族名在源码里根本不出现 | **32** |

**所以第一次多报了 8 个 —— 而错的形状是「存储形式不同被读成了不存在」，
与 R889 那次「工具读法错被读成对象缺席」同族。**

### 32 个完全没有的族（按路径数排）

| 族 | 路径数 |
|---|---|
| **`/customer/v1/`** | **10** |
| **`/Checkout/v2/`** · **`/bff/v4/`** | 各 **5** |
| **`/threeds/v1/`** · **`/bff/v3/`** · `/checkout/v2/` · `/cart/v2/` | 各 3–4 |
| `/activity/v1/` `/api/v7/` `/cart/v1/` `/client_api/v1/` `/commerce/v1/` `/marketing/v1/` `/paygate/v2/` `/product-core/v1/` `/legacy/v1/` … | 各 2 |
| **`/turnstile/v0/`** · **`/shield/v1/`** · `/flex/v2/` `/form/v1/` `/jgc/v8/` `/snap/v1/` `/snap/v2/` `/rest/v2/` `/public/v1/` … | 各 1 |

### 其中两条属于优先级 ②

| 族 | 为什么 |
|---|---|
| **`/turnstile/v0/`** | **Cloudflare Turnstile** —— R876 在模型字段里见过 `_turnstileKey` |
| **`/shield/v1/`** | 名字像防护服务；**内容未查** |

**所以「风控对抗」这一档在端点层也有一处具体缺口，而不只是方法名。**

### 这张表是判据 (f) 的形态

**goal 的 (f) 要求「核心覆盖表可复算：原版站点与风控清单 ↔ `Registry.cs` 与 `Flows/Scripts` 逐条对」。
这一轮给出的是**端点族**那一层的可复算表 —— 56 / 3 / 21 / 32。**

**而它还有一个前提没满足：那 56 个族是不是都属于 PopMart？**
**`/bff/*` 是 John Lewis 的，`/activity/v1/` 与 `/shop/v1/`、`/store/v1/` 属于 PopMart。
所以「56 个族」是**全镜像的**，不是某一个站的 —— 而按站分组还没做。**


### 族 ↔ 宿主：**45 族 / 28 宿主**，新文档 `docs/ENDPOINT_FAMILY_HOSTS.md`（R893）

**R892 的边界是「56 个族是全镜像的，按站分组还没做」。这一轮做了 —— 而分组的方法不是我起的名，
是**同现**。**

### 方法

**有些路径以完整 URL 出现（`//checkout.johnlewis.com/bff/v2/orders`），一条字面量里同时有宿主与族。
于是判据是：**族与宿主出现在同一条字面量里**。**

**这比「池内邻近」强 —— R876 那次错就是拿邻近当归属。同现是同一个字符串内部的关系。**

### 结果：45 / 56 族有同现宿主

| 宿主 | 族数 |
|---|---|
| **`api.nike.com`** | **11** |
| **`checkout.johnlewis.com`** | **4** |
| `www.vans.com` | 3 |
| `checkoutshopper-live.adyen.com` · `app.midtrans.com` | 各 2 |
| **`prod-hk-actapi.popmart.com`** | **1：`/activity/v1/`** |
| **`challenges.cloudflare.com`** | **1：`/turnstile/v0/`** |
| 其余 20 个宿主 | 各 1 |

### 优先级 ② 的三条落了地

| 宿主 | 族 | 读法 |
|---|---|---|
| **`challenges.cloudflare.com`** | **`/turnstile/v0/`** | **Cloudflare Turnstile 的端点** —— R876 见过 `_turnstileKey` 字段 |
| **`inbox-api.aycd.io`** | `/api/v1/` | **AYCD** 是验证码/OTP 收取服务；对应 `AycdInboxAccount` 模型 |
| `flex.cybersource.com` · `www.paypal.com` · `app.midtrans.com` | `/flex/v2/` · `/threeds/v1/` · `/snap/v1..v2/` | 3DS 与支付重定向 |

### 而它更正了 R835

**`prod-hk-actapi.popmart.com` 只带 `/activity/v1/` 一个族。**

**所以 PopMart 有**三个**路径空间、两个宿主：**

| 宿主 | 前缀 |
|---|---|
| `popmart.com`（`Origin(c.Url)` 拼出） | `/shop/v1/`（41）· `/store/v1/`（5） |
| **`prod-hk-actapi.popmart.com`** | **`/activity/v1/`（2）** |

**R835 当时搜 `activity/v1/exhibit_draw` 找 `StartDrawFlow` 没找到，判「PopMart 没有这个端点」。
现在看：抽签走 `/shop/v1/drawScratch/*`，而 `activity/v1` 是**另一个宿主的另一个空间**。
那次错的形状是「一个站只有一个 API 宿主」——而它有两个。**

### 四条边界，与表一起读

1. **45 / 56**：11 个族没有同现宿主，不在表里。
2. **同现证明「这个族在某宿主上」，不证明「只属于它」**：`/api/v1/` 在 aycd、goat、hbx 三个宿主上都出现。
3. **表里混了两类宿主**：站的 API（`api.nike.com`）与厂商的 API（`challenges.cloudflare.com`）。
4. **本表不说明复刻件有没有实现** —— 那是 R892 的 3 / 21 / 32 分级。


### 按宿主的覆盖：**17 / 45**，而分布比总数有用（R894）

**R893 给了族↔宿主表。这一轮加上「复刻件有没有」这一列。**

### 总数

| | |
|---|---|
| 有宿主的族 | **45** |
| 复刻件有 | **17** |
| 复刻件无 | **28** |

### 而按宿主看才有信息

| 宿主 | 有/共 | 读法 |
|---|---|---|
| **`api.nike.com`** | **11/11** | **Nike 全覆盖** |
| `checkout.johnlewis.com` | 1/4 | 只有 `bff/v2` |
| `checkoutshopper-live.adyen.com` | 1/2 | 缺 `paybylink/v1` |
| `id.asics.com` · `www.goat.com` · `www.nike.com` · `inbox-api.aycd.io` | 各 1/1 | 单族，齐 |
| **`www.vans.com`** | **0/3** | **`cart/v1` · `cart/v2` · `products/v2` 全缺** |
| **`challenges.cloudflare.com`** | **0/1** | **Turnstile 端点缺** |
| **`prod-hk-actapi.popmart.com`** | **0/1** | **`/activity/v1/` 缺** |
| 其余 18 个宿主 | 各 0/1 | 全是支付商或基础设施 |

### 三条具体结论

1. **Nike 的 11 个族全在复刻件里** —— 这是第一个能说「这个站端点层齐了」的站。
2. **Vans 的 3 个族一个没有** —— 而 R762 说复刻件有 62 个店模块。**所以 Vans 的模块在，端点不在。**
3. **`www.ibm.com` + `/dtd/v11/` 也在 0/1 里** —— 而 R893 就怀疑它是误收的字符串。

### 一个必须说的告诫

**「有」的判据是「族段（如 `api/v1`、`bff/v2`）在源码里出现」。**

**而 `api/v1`、`api/v2`、`bff/v2` 这种段太泛 —— 可能命中**不相关的代码**。**

**所以 17 这个数是**上界**，不是精确值。要精确得按宿主把每条路径都对一遍，
而那是 45 × 平均 2 条 = 约 100 次对比。这一轮没做。**

**这正是 R892 那个错的另一面：R892 因为判据太严高报缺口（40 vs 32），
这一轮因为判据太松可能低报缺口（17 可能是 14）。**


### 逐条算准：**55 / 171 条路径**（32.2%）—— 上界换成精确值（R895）

**R894 报 17/45 族，并说「17 是上界，族段太泛可能误命中」。这一轮按路径逐条对，把它算准。**

### 判据（两种存储形式都认）

| 形式 | 判据 |
|---|---|
| **whole** | 整条路径作为字面量出现 |
| **tail** | 去掉族前缀的尾部作为字面量出现（`Base + "v2/orders"`） |
| **missing** | 两者都不是 |

### 结果

| | |
|---|---|
| 有宿主的族下的路径 | **171** |
| **whole** | **47** |
| **tail** | **8** |
| **missing** | **116** |
| **合计有** | **55（32.2%）** |

### 两个分母，两个数

| 度量 | 值 |
|---|---|
| 族级（R894） | **17 / 45 = 37.8%** |
| **路径级（本轮）** | **55 / 171 = 32.2%** |

**两个数不同，而**不是**谁错了：族级问「这个族有没有被提到」，路径级问「这个族下的每条有没有」。

**一个族里提到 1 条，族级算「有」，路径级算 1/N。**

**所以：族级高估覆盖率。**17/45** 读起来像「三分之一的端点有了」，而按路径是 **32.2%**，
且那 17 个族里有 12 个只提到了一部分。**

### 而这修正了 R894 的一个说法

**R894 说「17 是上界」—— 那是把**族级**当路径级的判断。**

**按族级它其实不是上界：判据是「族段出现」，而族段出现确实意味着这个族有东西，族级 17 是准的。
问题在于**族级本身不是覆盖率**，因为它给「提到 1 条」和「提到全部」同样的分。**

**所以真正要修的不是松紧，是**分母**。**


### 分母拆开：站 **55/142（38.7%）**，厂商 **0/28（0.0%）**（R896）

**R895 说「171 条里多少属支付商而非站 —— 混着算让 32.2% 含义不清」。这一轮拆开。**

### 结果

| 分类 | 宿主 | 路径 | 覆盖 |
|---|---|---|---|
| **站** | 15 | **142** | **55（38.7%）** |
| **厂商** | 14 | **28** | **0（0.0%）** |

**所以那 55 条覆盖**全部来自站**，而厂商那 28 条一条都没有。**

### 这改变了 32.2% 的含义

| 度量 | 值 | 含义 |
|---|---|---|
| 混合（R895） | 55/171 = 32.2% | **两个不同的问题被平均了** |
| **站（本轮）** | **55/142 = 38.7%** | **站点 API 的覆盖率** |
| **厂商（本轮）** | **0/28 = 0.0%** | **支付与防护第三方，一条都没接** |

**32.2% 落在两者之间，而它既不是站覆盖率也不是厂商覆盖率。

### 厂商那 0/28 是一个干净的缺口

| 宿主 | 族 | 属什么 |
|---|---|---|
| **`challenges.cloudflare.com`** | `/turnstile/v0/` | **Turnstile（优先级 ②）** |
| **`inbox-api.aycd.io`** | `/api/v1/` | **AYCD 验证码/OTP（优先级 ②）** |
| `flex.cybersource.com` | `/flex/v2/` | 3DS Flex |
| `www.paypal.com` | `/threeds/v1/` | 3DS |
| `app.midtrans.com` | `/snap/v1` · `/snap/v2` | Snap 支付 |
| `checkoutshopper-live.adyen.com` | `/checkoutshopper/v1` · `/paybylink/v1` | Adyen 结账 |
| `api.braintreegateway.com` · `api.sibspayments.com` · `www.vivapayments.com` · `payments.bigcommerce.com` | 各 1 | 支付 |
| `webservices.global-e.com` · `static-forms.klaviyo.com` · `pbiouukmdvahsp…` · `api.vipps.no` · `www.ibm.com` | 各 1 | 跨境/表单/云函数/钱包/可疑 |

**而 `inbox-api.aycd.io` 在 R894 的族级判据下算「有」（1/1），路径级是 0** ——
**因为族段 `api/v1` 太泛，误命中了别处的 `api/v1`。**

**这正是 R895 猜的那个误命中，现在具体到了一条。**

### 两处分类判断，写明以便复核

1. **`payments.dickssportinggoods.com` 与 `paymentsheet-ent.wdprapps.disney.com` 归「站」** ——
   它们是那两家自己的支付子域，不是第三方。**换个人可能归厂商。**
2. **`-`（无宿主）算进「站」那一桶** —— 这是错的，它应该单列。

**所以 142 里有几条归属可议；这条写在这里而不是藏起来。**


### Vans 的 6 条路径取到了，而**归属是 Inference 不是 Observation**（R898）

**R897 留下的下一步：取 Vans 那 3 个族的精确路径。**

### 结果：6 条

```
/cart/v1/cart/
/cart/v1/cartWithItem?locale=
/cart/v2/cart/
/cart/v2/checkout/order/
/cart/v2/checkout/order?locale=
/products/v2/products/
```

### 而扫描结果里没有一条带宿主

**输出里 `HOST` 行一条都没有 —— 也就是说这 6 条字面量**没有一个自带 `www.vans.com`**。**

**所以归属是**族级**的：R893 的共现扫描证明 `/cart/v1/`、`/cart/v2/`、`/products/v2/` 三个**族**
与 `www.vans.com` 同处一条字面量，而这 6 条**具体路径**没有。**

**两者强度不同：**
- **族级归属 = Observation（共现）**
- **路径级归属 = Inference（同平台的别的站也可能用同样的路径）**

**所以 `VansEndpoints` 里写了一个 `OwnershipIsInference = true` 常量，把这条限制固化进类型而不是只写在注释里。**

### 加了什么

| 文件 | 内容 |
|---|---|
| `src\Cybersole.Stores\Flows\VansEndpoints.cs` | **新建**：6 常量 + `All` + `FamilyHost` + `OwnershipIsInference` |
| `tests\Cybersole.Tests\VansEndpointTests.cs` | **新建 6 用例** |

### 6 个用例里三个值得说

| 用例 | 钉住 |
|---|---|
| `BothCartVersionsArePresent` | **v1 与 v2 两个都留着** —— 镜像里都有，删任一个都是丢证据 |
| `TheOrderEndpointHasTwoSpellings` | 同一端点有 path 与 query 两种写法 |
| `TheProductsPathReallyRepeatsItsWord` | **`products/v2/products/` 的双词是镜像里的，不是我的笔误** |
| `OwnershipIsRecordedAsInferenceNotObservation` | **把「这是推断」钉成断言** —— 将来谁要按「观察到的归属」用这些路径，得先删掉这条 |

### 一个被换掉的测试

**第一版最后一个用例 `EveryPathAppearsVerbatimInTheSource` 读 `VansEndpoints.cs` 再查同一个文件里有没有这些字面量 —— 恒真，什么也没证明。**

**换成 `EveryPathStartsWithOneOfTheThreeFamilies`：每条路径必须以那三个族之一开头。
族段打错一个字仍会编译、仍看起来合理，所以这个检查有实际效力。**


### R898 的 Vans 常量少了 `/api` —— 而归属从 Inference 升为 Observation（R899）

**R898 留下的问题：那 6 条路径到底属不属 Vans。**

### 做法：搜「宿主与路径同处一条字面量」

**R898 的扫描模式是 `/(cart|products)/vN/` —— 它从 `/api` **之后**那一段开始匹配，
所以既看不到前面的宿主，也丢掉了前面的 `/api`。这两个后果是同一个原因。**

**改成搜 `vans.com.../(cart|products)/vN/`，一次得到 5 条完整 URL：**

```
https://www.vans.com/api/cart/v1/cartWithItem?locale=
https://www.vans.com/api/cart/v2/cart/
https://www.vans.com/api/cart/v2/checkout/order/
https://www.vans.com/api/cart/v2/checkout/order?locale=
https://www.vans.com/api/products/v2/products/
```

**（第 6 条 `.../api/cart/v1/cart/` 在 `0x14709bf5c`，同一族。）**

### 两个后果，一次修掉

| 项 | R898 | R899 |
|---|---|---|
| 路径前缀 | `/cart/v1/cart/` | **`/api/cart/v1/cart/`** |
| `OwnershipIsInference` | `true` | **`false`** |

**少了 `/api` 的常量指的是一个 Vans 服务器不会应答的路径。而归属现在是 Observation ——
宿主与路径在**同一条字面量**里，这正是 R893 用的判据。**

### 所以 R898 那两个「保守的判断」都是同一个扫描模式的副产品

**R898 说「这 6 条没有自带宿主，所以归属是 Inference」——听上去很谨慎。
而它谨慎地记录的是一个**我自己的匹配模式造成的假象**。**

**「证据不足」和「我的搜索看不到」是两件事，而 R898 把后者写成了前者。**

### 改了哪些

| 文件 | 改动 |
|---|---|
| `VansEndpoints.cs` | 5 个常量补齐 `/api` + 第 6 个 `CartV1` 单列 + `OwnershipIsInference = false` + 注释写明 R898 错在哪 |
| `VansEndpointTests.cs` | 7 用例；新增 `EveryPathCarriesTheApiPrefix` 与 `OwnershipIsNoLongerInference` |


### R892–R896 的覆盖数**低报最多 27 条** —— 前缀被扫描模式截掉了（R900）

**R899 留下的问题：`/api` 这层是不是别的站也有？**

### 答案：不止 `/api`，共 **27 / 154 条（17.5%）**在族前面还有前缀

**那 27 条正是 R893–R896 会截断的 —— 那些轮把「去掉前缀的路径」拿去与复刻件比，
所以即便复刻件有完整形式也会算成缺。**

| 前缀 | 路径数 |
|---|---|
| **`/api`** | **8** |
| `/payment` | 4 |
| `/payment-authentication` | 4 |
| `/web2` | 3 |
| `/merchants` | 2 |
| `/prod` | 2 |
| `/epayment` · `/forms` · `/data` · `/gs` 等 | 各 1 |

**样例（宿主 / 完整路径）：**

```
api.braintreegateway.com   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_me…
api.nike.com               /payment/deferred_payment_forms/v1/jobs
api.vipps.no               /epayment/internal/v1/card-page/Payments
payments.bigcommerce.com   /api/public/v1/orders/payments
payments.dickssporting…    /prod/api/paygate/v2/authorization
auth.casio-intl.com        /api/connect/v1/login
```

### 所以 R895 的 55/171 低报

**低报量最多 27 —— 而这 27 条里有多少是复刻件其实有的，还没算。
要算它得用完整路径重新对一遍。**

**而 Vans 那 6 条正是这 27 里的一部分 —— R899 修的只是它们，其余 21 条还没修。**

### 两个人口不同，不能直接比

| 扫描 | 路径数 | 代价 |
|---|---|---|
| R895（族内匹配） | 171 | **27 条被截断** |
| R900（全路径匹配） | 154 | **人口更小，因为去重方式不同** |

**所以 55/171 与 49/154 不是同一个度量在两个时点，而是两个不同的度量。
要一个可比的数，得先用**同一个**提取法跑一遍，而那还没做。**

### 一条要写完的教训

**同一个扫描模式在四轮里给出了四个数（40 族缺失、32 族缺失、17/45、55/171），
而它每一轮都在做同一件事：在 `/x/vN/` 这个地标处开始匹配。**

**地标匹配方便、好读、看起来对准了 API 的形状 —— 而它**默认前缀不存在**。
这个默认在 `/shop/v1/` 和 `/activity/v1/` 那些站上恰好成立，在 `/api/cart/v2/` 上不成立。**


### 一个正式工具，一个数 —— 而它推翻了 R896 的读法（R901）

**R900 承诺「用同一提取法重跑，得到可比的数」。这一轮不再写临时脚本，写成两个正式文件：**

| 文件 | 角色 |
|---|---|
| `analysis/coverage_extract.py` | 从镜像提取（完整路径，保留前缀） |
| `replica/tools/endpoint_coverage.py` | 与复刻件比对，按桶输出 |

**理由写在工具头部：R892–R900 同一个问题量了五次得到五个答案，因为每轮临时脚本各带一个假设。
**一个因为脚本换了而变化的数，不是测量。****

### 结果：三个桶，不是两个

| 桶 | 路径 | 覆盖 |
|---|---|---|
| **有宿主的站** | **55** | **3（5.5%）** |
| **厂商** | **32** | **0（0.0%）** |
| **无宿主** | **67** | **46（68.7%）** |
| 合计 | **154** | **49（31.8%）** |

### 而它推翻了 R896

**R896 报「站 55/142（38.7%）· 厂商 0/28」。**

**差别在于：R896 把**无宿主那 67 条算进了「站」桶**。这一轮把它们单列成第三桶。**

| 度量 | 值 | 桶的划分 |
|---|---|---|
| R896 | 站 55/142 = 38.7% | 两桶（无宿主并入站） |
| **R901** | 站 **3/55 = 5.5%** · 无宿主 **46/67 = 68.7%** | **三桶** |

**两个数都不算错，但它们回答不同的问题：
「复刻件实现了多少条站 API」——5.5%；「复刻件实现了多少条能定位到站的 API」——31.8%。**

### 而 5.5% 这个数很刺眼，它说明一件事

**当镜像**明确告诉我们某条路径属于哪个站**时，复刻件几乎一条都没有。**

**而无宿主那 67 条覆盖 68.7% —— 那些主要是 PopMart 的 `/shop/v1/` 路径（镜像里它们是相对路径，不带宿主）。**

**所以「覆盖 68.7%」和「覆盖 5.5%」描述的是同一批工作的两面：
**我做得多的是**没有宿主线索**的那部分，而**有宿主线索**的那部分几乎没动。**

### 一个我必须写下来的观察

**这五轮（R892–R900）我一直在改进度量，而**产品代码只动了两轮的常量**（R890 的 2 个、R898/R899 的 6 个）。**

**度量的价值是让下一步可判 —— 但它不能替代下一步。这一轮之后，「有宿主的站 API 只覆盖 3/55」是一个可执行的清单，
比前面任何一个数都更直接。**


### `/customer/v1/` 那 10 条补上了 —— 覆盖率**第一次真的动了**（R902）

**R901 说「下一轮第一件事：跑 `-v` 拿清单」。跑了，然后补了最多的一族。**

### 补了什么

**`/customer/v1/*` 10 条 —— 账户管理的完整四动词集与注册链路：**

| 路径 | 干什么 |
|---|---|
| `/customer/v1/address/add` · `del` · `list` · `update` | 地址增删查改 |
| `/customer/v1/customer/app` | 读当前客户 |
| `/customer/v1/customer/exist` | 注册前的存在性检查 |
| `/customer/v1/customer/guest/register` | 访客注册 |
| `/customer/v1/customer/login` · `register` | 登录 / 注册 |
| `/customer/v1/verification/send` | 发验证码 |

**而按 §2.7c 先查过：`/customer/v1` 字面量全库没有。
`ScapiEndpoints.cs` 里那个 customer 是 Salesforce Commerce API，另一回事。**

### 数字变化

| 度量 | R901 | **R902** |
|---|---|---|
| `hostless` 覆盖 | 46 / 67（68.7%） | **56 / 67（83.6%）** |
| 总缺失 | 105 | **95** |
| 套件 | 1790 | **1796** |

**所以这是 R892 以来第一次有**可测的产品进步**，而不是度量改进。**

### 而这一族比 Vans 那族更值得标注

**`OwnerIsUnknown = true`。它比 `VansEndpoints.OwnershipIsInference = false` 弱一档：**

| 类 | 归属状态 | 为什么 |
|---|---|---|
| `VansEndpoints` | **Observation** | 宿主与路径同处一条字面量 |
| **`CustomerApiEndpoints`** | **Unknown** | **没有任何一条字面量同时含这些路径与宿主** |

**所以这 10 条是「镜像里确实存在的端点，而属哪个站不知道」。
写常量是正当的（路径是观察），写步骤不是（体、响应、鉴权、调用者四样全缺）。**

### 6 个用例里两个值得说

| 用例 | 钉住 |
|---|---|
| `TheOwningStoreIsRecordedAsUnknown` | **把「归属未知」钉成断言** —— 将来谁找到共现证据，得改这个 flag 并说明 |
| `TheListIsOrderedForUseRatherThanAlphabetically` | **`All` 是按注册流程排的，不是字典序** —— 断言首项是 `CustomerExist` 且整体不等于排序结果 |


### 加了个「第三种状态」，浮出 **13 条假阴性**（R904）

**目标：取 `store` 那 52 条缺失清单。**

### 取出来一看，最大的可疑是 John Lewis

**清单里 `checkout.johnlewis.com` 占 11 条。而 `JohnLewisBff` 里它们是 `Base = ".../bff/"` + 相对路径
（`"v2/orders"`）—— **我的逐字匹配看不到。****

**所以这 11 条不是缺，是我的规则看不见。**

### 而 R894 已经因为这个吃过一次

**R894 的教训是「整条字面量」判据太严，高报出 40 族缺失。**

**这次同一个坑**在同一个工具里**又出现一次，因为我把它写成了「verbatim only」并自称那是诚实的默认。**

### 所以加了第三态，而没有放宽规则

| 状态 | 判据 | 含义 |
|---|---|---|
| **verbatim** | 整条路径是字面量 | 复刻件确实有这条 |
| **base-tail** | 去掉族前缀的尾部是字面量 | 复刻件知道这个端点，但它藏在某个 Base 后面 |
| **missing** | 两者都不是 | 真缺 |

**两者都不并入：算成 covered 会高报，算成 missing 会低报，而前面几轮轮流犯过这两种。**

### 数字

| 桶 | verbatim | base-tail | 合计 | 百分比（verbatim） |
|---|---|---|---|---|
| **store** | 3 | **8** | **11 / 55** | 5.5% |
| **vendor** | 0 | **5** | 5 / 32 | 0.0% |
| **hostless** | **67** | 0 | **67 / 67** | **100.0%** |
| **missing** | — | — | **71**（原 84） | — |

**13 条假阴性浮出来：store 8 条 + vendor 5 条。**

### 而 store 的真实覆盖是 11/55 = 20%，不是 5.5%

**verbatim 那 3 条我只敢报 5.5%；加上 base-tail 的 8 条是 20%。**

**而 20% 里有多少是「真的实现」还不确定 —— base-tail 匹配只证明「复刻件里有一段同样的字面量」，
不证明它挂在同一个 Base 下。所以这一列标注为「知道这个端点，形式我确认不了」。**


### `/shield/` 是 **Paynamics Shield**，不是反爬 —— R903 分错了类（R905）

**R903 把 `/shield/v1/verify_otp` 标成「优先级 ② 的第一个具体端点」，靠的是路径里那个词。**

**这一轮查了 20 条含 `shield` 的字面量：**

```
ShieldApiUrl   https://nodecde1.paynamics.net/possible
Invalid Paynamics Shield URL
Paynamics Shield error (
https://shield.paynamics.net
shield processor
shield.paynamics.net
<RunShield>d__18 · RunShield · shieldUri · <shieldQuery>5__4
```

**Paynamics 是菲律宾的支付网关。所以 `/shield/` 是**支付环节的 OTP**，与反爬无关。**

### 而这一族的「反爬」标签是我按词猜的

**`AntiBotRelated` 里我还放了 `submitThreeDS2Fingerprint` —— 那是 3DS 指纹，也不是反爬。**

**所以那个子集里现在两条都分错了。R903 那轮的标注是**按名字归类**，而 AGENTS.md §1 的 R730 裁决明写过：
「不要用符号计数/名字替代读代码」。**

### 查到的两件事，都补进产品

| 事实 | 复刻件状态 |
|---|---|
| 镜像有**两个** shield 宿主：`nodecde1.paynamics.net` 与 `shield.paynamics.net` | **只有一个**（`ShieldHost`） |
| `/shield/v1/verify_otp` | **没有** |

**所以这是**同一家支付商的两个宿主**，而设备画像走其中一个、OTP 校验走另一个。**

### 而镜像里有个方法 `RunShield`，复刻件没有

**`recovered_async_methods.txt` 里 `RunShield` 在（1 条）。复刻件 `where_is RunShield` 只有 docs。**

**所以这是一个**原版有、复刻件没有的步骤** —— 比缺一个常量大的缺口，而它现在被记下来了而不是被常量掩盖。**

### 加了什么

| 文件 | 改动 |
|---|---|
| `Payments/Gateways.cs` | +`PublicShieldHost` · +`ShieldVerifyOtp` · +`RecoveredShieldSurface` 公开访问器 |
| `tests/PaynamicsShieldTests.cs` | **新建 3 用例** |

**第三个用例 `TheRecoveredSurfaceIsNotYetCalled` 断言宿主在源码里只出现一次 ——
**将来谁把它接上，这条会红，而红的时候说明「这条常量变成调用了」，需要连同测试意图一起改。****


### 异步方法覆盖 **20.0%** —— 这才是函数对等的直尺度（R906）

**R905 发现 `RunShield` 存在。于是把它放大：镜像的 1,547 个异步方法名，复刻件里有没有。**

### 结果

| | |
|---|---|
| 镜像异步方法名 | **1,547** |
| 复刻件有 | **310（20.0%）** |
| 复刻件无 | **1,237** |

**新工具 `tools/async_method_coverage.py`，整词匹配、扫全 `src`。**

### 而 20% 与端点侧那个 100% 差得远

| 度量 | 值 | 量的是什么 |
|---|---|---|
| 端点覆盖（无宿主桶） | **100%** | URL 有没有被写下来 |
| **异步方法覆盖** | **20.0%** | **步骤有没有存在** |

**这两个不矛盾：一个 URL 写下常量算「有」，而**用它的方法**可能不存在。
R903 那 67 条 hostless 路径现在都有常量，而调用它们的方法多数还没有。**

**所以前几轮补常量是对的，但它补的是「路名」，不是「路」。**

### 而这是**上界**，不是缺口本身

**goal 允许改名。所以「名字不在」可能是：**
1. 功能真的没有
2. 功能在，但叫另一个名字

**这一条判别不了。要分辨得读每个缺失名字的语义 —— 那是 1,237 次判断。**

**所以这个数的正确读法是：**最多缺 1,237 个步骤**。**

### 而清单第一段就有一族很说明问题

```
AddToCart2 · AddToCartAstro · AddToCartBox · AddToCartDummy
AddToCartFrontend · AddToCartNext · AddToCartSvelte
```

**7 个 `AddToCart` 变体，按平台/框型/前端框架分。复刻件只有一个 `AddToCart`。**

**这是「一家店一个加车实现」的直接证据 —— 而不是一个可以参数化的通用步骤。**

### 前 80 个里的其他族

**`AcceptCallbacksAsync` · `AcceptLoopAsync`（服务端）· `AcquireAsync` · `AcquireLockAsync` · `AcquireUpdateLock`（并发）·
`AddAddress` · `AddPaymentMethod` · `AddPaymentToCart`（结账）· `AddImageAsync` · `AddHintImageAsync`（captcha 图）·
`Animate` · `AnimateViewportOffsetAsync`（UI）**

**所以 1,237 个缺失方法横跨服务端、并发、结账、captcha、UI —— 这就解释了为什么 20%。**


### `AddToCart` 族量准了：**8 / 15**，而缺的 7 个里 5 个是真缺口（R907）

**R906 说「1,237 是上界，因为可能只是改名」。这一轮挑一族把它变成确数。**

### 而族不是 8 个，是 **15** 个

**R906 只看到 7 个变体，实际 15 个，而且带出现次数（所以「同一件事被多少处调用」是可读的）：**

| 名字 | 镜像 | 复刻件 | 判读 |
|---|---|---|---|
| `AddToCart` | 32 | **35** | 主干，齐 |
| `AddToCartPreload` | 11 | 2 | 有，但复刻件里用得少 |
| `AddToCartStoreFront` | 8 | 2 | 有 |
| `AddToCartMulti` | 6 | 2 | 有 |
| `AddToCartApp` | 3 | **7** | 有，且复刻件里更多 |
| `AddToCartAppDw` | 1 | **4** | 有 |
| `AddToCartGraphQL` | 1 | **8** | 有，且复刻件里更多 |
| `AddToCartPreloadGraphQL` | 1 | **5** | 有 |
| `AddToCart2` | 1 | **0** | **缺** |
| `AddToCartDummy` | 1 | **0** | **缺 —— 但原版这个是测试桩** |
| `AddToCartBox` | 1 | **0** | **缺 —— 谜盒加车** |
| `AddToCartFrontend` | 1 | **0** | **缺** |
| `AddToCartAstro` | 1 | **0** | **缺 —— 无头前端框架** |
| `AddToCartNext` | 1 | **0** | **缺 —— 同上** |
| `AddToCartSvelte` | 1 | **0** | **缺 —— 同上** |

### 所以 7 个缺失要分三类

| 类 | 名字 | 判读 |
|---|---|---|
| **真缺口** | `AddToCartBox` · `AddToCartFrontend` · `AddToCartAstro` · `AddToCartNext` · `AddToCartSvelte` | **5 个** |
| **测试桩** | `AddToCartDummy` | **原版自己的测试桩，不该复刻** |
| **不明** | `AddToCart2` | 只有名字 |

**所以这一族真实缺口是 5，不是 7。**

### 而 `AddToCartBox` 是一条我漏掉的线索

**R890 我记过 PopMart 的 `/shop/v1/box/*` 那 6 条端点（`boxCart/addBoxListToCart`、`box_set/extract`、
`box_spu/detail` 等），当端点记下了，**但没注意到原版有一个专门的方法 `AddToCartBox` 在用它们。**

**所以那 6 条端点的调用者现在有了名字 —— 这比「有 6 条端点没被调用」精确。**

### 三个无头框架变体说明一件事

**`Astro` · `Next` · `Svelte` 是三个前端框架。它们各有一个加车方法，意味着原版对**用这些框架搭的无头店**
有专门的加车路径 —— 而不是走通用 API。**

**所以「一家店一个实现」还不够准；更准的说法是**一个前端栈一个实现**。**


### `AddToCartBox` 实现了 —— 而它给 5 条死端点接上了调用者（R908）

**R907 说下一轮补 `AddToCartBox`。补了。**

### 先核了一遍「6 条 box 端点有没有调用者」

| 端点 | 之前 |
|---|---|
| `AddBoxListToCart` | **有 1 个**（PopMart 的 `AddToCart` 在用） |
| `BoxGoodsList` · `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` · `BoxExtract` | **全无** |

**所以 R907 那句「6 条端点没被调用」要修成「1 条有、5 条没有」。
而那一 条正是 `AddToCart` 用的 —— 它让整族**看起来**被覆盖了。**

### 实现了什么

**`AddToCartBoxAsync`（基类虚方法 + PopMart override），四步：**

1. `BoxSpuDetail?skuId=` —— 盒子属于哪个套装
2. `BoxSetPreview?skuId=` —— 套装里有什么（不揭示内容）
3. `BoxSetExtract` —— 从套装里抽一个
4. `AddBoxListToCart` —— 把抽到的条目加进车

**而 `AddToCartBox` 不在 PopMart 那 24 个名字里** —— 所以它像 `FindProductInstore` 一样：
**方法在、序列不列。** `implementable` 仍是 8，`map` 从 174 到 **175**。

### 调用者变化

| 端点 | 之前 | 之后 |
|---|---|---|
| `AddBoxListToCart` | 1 | **2** |
| `BoxSpuDetail` · `BoxSetPreview` · `BoxSetExtract` | 0 | **各 1** |
| `BoxGoodsList` · `BoxExtract` | 0 | **仍 0** |

**剩下两条仍无调用者，而它们各有一说：**
- **`BoxGoodsList`（`goodsListV2`）是列表端点** —— 属于「发现」而非「加车」，不该由这个方法用。
- **`BoxExtract`（`/box/extract`）与 `BoxSetExtract`（`/box_set/extract`）是两个变体** —— 我用了后者，前者不明。

### 异步覆盖

**310 → **311**（20.1%）—— 一个方法。这一族 15 个名字里现在 9 有 6 缺。**

### 而顺序与参数是 Inference

**镜像证明的是：有个方法叫 `AddToCartBox`，而 5 条端点在。**
**没证明的是：那四步的顺序、以及每一步的请求体。**

**所以方法里用的是最小 payload，而缺会话变量时**明确失败**（要 `boxSkuId`），不猜。**


### 修自己上一轮留的缺陷：`AddToCartBox` 要的变量没人设（R909）

**R908 写了方法，但它要求会话里有个 `boxSkuId` —— 而**没有任何地方设它**。
所以那是一个**写了却调不到**的方法，与 R850 的「有形状无内容」同一层。**

### 改了什么

```
before:  必须 boxSkuId，否则失败
after :  boxSkuId 优先；没有就退到 c.Session.VariantId；两者都无才失败
```

**理由：普通运行里 `VariantId` 已经由 `FindSlot` 设过，所以这个方法现在**在一轮正常流程里可达**。
而显式 `boxSkuId` 仍能覆盖 —— 用于「盯一个盒子、加另一个」的情况。**

### 而 `BoxGoodsList` 与 `BoxExtract` 这一轮**刻意没接**

**查过三个发现步骤：**

| 步骤 | 现在取什么 |
|---|---|
| `FindProduct` | 商品页 `.json` |
| `FindVariant` | 读会话里的 `raw` |
| `FindSlot` | 从 `raw` 正则取 `skuId` |

**`BoxGoodsList`（`goodsListV2`）是列表端点，在这三个里没有自然位置。**

**硬接它会是 R850 的错：**一个看起来在用端点、而语义不明的步骤**。
所以这一轮**不接，并把它写成 Unknown 而不是做成一个假调用者**。**

### 数字

| 度量 | R908 | **R909** |
|---|---|---|
| 套件 | 1805 | **1808** |
| `StoreFlow` 虚步骤 | 175 | 175（不变） |
| box 端点有调用者 | 4 / 6 | 4 / 6（不变） |

**这一轮没有增加覆盖，只把一个不可达的方法变得可达。**

### 3 个用例

| 用例 | 钉住 |
|---|---|
| `TheBoxSkuFallsBackToTheFlowVariant` | 两个名字都被读，且是条件式回退而非两条分支 |
| `ItStillFailsWhenNeitherInputIsPresent` | **两者都无时明确失败** —— 空 sku 静默发送会「成功」而什么也没加 |
| `TheChainUsesFourEndpoints` | 四个端点都在方法体内；**窗口取到下一个 override，不取固定长度** |

**第三个用例第一次是红的，因为我用了固定 2400 字符窗口，第四个端点被截掉了 ——
**那是一次「测试写错而不是代码写错」的红**，而它说明固定长度窗口本身是个坏做法。**


### 让数据挑目标：最高杠杆的四个名字全在 HTTP 客户端上（R910）

**前面几轮的目标是「碰巧注意到的」。这一轮按镜像里的出现次数排序缺失名字。**

**新工具 `tools/absent_by_leverage.py`。排序后前四名：**

| 名字 | 镜像引用次数 |
|---|---|
| **`StartAsync`** | **19** |
| **`HandleResponse`** | **18** |
| **`StopAsync`** | **14** |
| `WriteToAsync` | 7 |
| `ScrapeProduct` · `ScrapeJson` · `GetOwnProperties` · `DisposeAsyncCore` | 各 7 |

### 而前四名里三个是 HTTP 客户端的生命周期

**查过：`BouncyHttpClient` 在，但 `StartAsync` / `StopAsync` / `HandleResponse` / `DisposeAsyncCore`
**全库一个都没有**。**

**而它的 `Dispose()` 是**空体** —— `public void Dispose() { }`，正是 R850 的「有形状无内容」，换了个名字。**

### 改了什么

| 改动 | 依据 |
|---|---|
| `ParseResponse` → **`HandleResponse`** | **同一概念，用镜像的名字** |
| `+ StartAsync` · `+ StopAsync` · `+ IsRunning` | 生命周期 |
| `+ DisposeAsyncCore` · `+ IAsyncDisposable` | 异步释放 |
| `Dispose()` 不再空 | `StopAsync` 里 `_analytics?.Flush()` |

**而 `StartAsync` 在 `StopAsync` 之后**拒绝启动**（抛 `NetException`）—— 不是因为镜像这么做，
是因为**允许复活已释放的客户端会让错误推到后面的 socket 失败上**。**

### 数字，而这一轮可以验算

| 度量 | R909 | **R910** |
|---|---|---|
| 套件 | 1808 | **1815** |
| 异步覆盖 | 311（20.1%） | **315（20.4%）** |
| **缺失名承载的出现次数** | **1523** | **1465** |

**58 的差，正好等于那四个名字的引用次数之和：19 + 18 + 14 + 7 = **58**。**

**这是这一串度量工作里第一次出现**事先可算的预测与实际相符**：
加哪些名字之前就知道会减去多少，而结果一分不差。**

### 而新的缺失榜首已经换人了

`WriteToAsync` 7 · `ScrapeProduct` 7 · `ScrapeJson` 7 · `GetOwnProperties` 7 · `WriteRawAsync` 6

**其中 `ScrapeProduct` / `ScrapeJson` 属优先级 ①（抓商品），`WriteToAsync` / `WriteRawAsync` 属 ③（IO）。**


### 覆盖率从 20.4% 修到 **24.0%** —— 因为我的匹配漏了 `Async` 后缀（R911）

**R910 排出的榜首是 `ScrapeProduct` 7 · `ScrapeJson` 7，我按那个去补 —— 结果编译报 CS0111「重复定义」。**

### 根因

**镜像的名字从状态机类型（`d__NN`）恢复，所以它们是 `ScrapeProduct`（**无 `Async`**）。
而 C# 方法是 `ScrapeProductAsync`。**

**我的判据是 `\bScrapeProduct\b` —— 而 `\b` 在 `t` 与 `A` 之间**不成立**，因为 `Async` 让标识符继续。
**所以 `ScrapeProductAsync` 不算命中 `ScrapeProduct`。****

### 影响范围

| 判据 | 命中 | 覆盖率 |
|---|---|---|
| 严格整词（旧） | 317 | 20.5% |
| **允许 `Async` 后缀（新）** | **371** | **24.0%** |

**54 个名字被误判为缺失。而 R906/R910 的所有排序都建立在这个误判上。**

### 而这一轮我先做坏了一次

**发现 CS0111 后我加了个删重复定义的动作，结果删掉 6,876 字符，**连 `GetHomeAsync` 一起删了** ——
虚步骤从 175 掉到 165，四个店编译失败（CS0115「没有找到适合的方法来重写」）。**

**而 `tools/.snapshot-backup` 不存在**（`snapshot.py` 写的是 `tools/.snapshots/`），所以我按错的路径找恢复源，找不到。**

**最后用 `git checkout -- src/Cybersole.Stores/Flows/StoreFlow.cs` 恢复 —— 175 恢复，编译干净。**

### 而第 462 轮那部分工作其实是对的

**`PopMartFlow` 在 HEAD 里**没有** `ScrapeProductAsync` / `ScrapeJsonAsync` 的 override。
所以我加的两个 override 是有效的、真实的。**

**这一轮保留了它们：`StoreFlow` 已有虚方法（所以不能重复声明），`PopMartFlow` 加 override（正确）。**

| 度量 | 改后 |
|---|---|
| `StoreFlow` 虚步骤 | **175** |
| 异步覆盖 | **371 / 1547 = 24.0%** |
| 缺失名承载出现次数 | **1303**（原 1523） |
| 套件 | **1815 通过 / 0 失败** |

### 新的缺失榜首（都真缺）

`WriteToAsync` 7 · `WriteRawAsync` 6 · `LoadAsync` 5 · `WriteStartNamespaceDeclarationAsync` 4 ·
`WriteAsyncInternal` 4 · `OverrideAsyncMethod` 4 · `OnLoadedAsync` 4 · `Enumerate` 4 · `DownloadAsync` 4

**`ScrapeProduct` 与 `ScrapeJson` 已从榜首消失 —— 因为它们现在真的在。**


### 恢复变成一条命令；并且我核清了两个套件数为什么不一致（R912）

**R911 的教训是「记错一个目录名就等于没有快照」。这一轮把那句话变成代码。**

### `snapshot.py` 加了两个模式

```
python tools/snapshot.py --list                     列出所有快照
python tools/snapshot.py --restore <stamp> [rel]    恢复一个文件或整份
```

**四种行为都实测过：**

| 情形 | 结果 |
|---|---|
| `--list` | 41 份 / 11,770 文件 / 109.5 MB，**并打印实际目录** |
| 恢复一个不存在的文件 | `not in that snapshot` + `restored 0`，**不写任何东西** |
| 恢复越界路径 `..\..\outside.cs` | 拒绝，`restored 0` |
| 恢复真实文件 | `restored 1`，而 `StoreFlow` 虚步骤仍是 **175** |

**而 `--list` 会打印那个真实路径 `tools/.snapshots` —— 这是刻意的：
R911 我不是不知道怎么恢复，是**记错了目录名**。所以让命令自己说路径。**

### 一处我该说清的：越界拒绝是被前一个检查挡住的

**`..\..\outside.cs` 报的是 `not in that snapshot`，不是我的路径守卫。
因为那个文件在快照里不存在，所以先被存在性检查拒绝了。**

**所以路径守卫（`dst.startswith(ROOT + sep)`）**只对「快照里存在、但会写到树外」的情形生效** ——
而快照里不会有那种路径。那行守卫**实际上不可达**。**

**留着它是对的还是多余的？我留着，因为快照的来源是 `os.walk(src)`，而如果将来有人改了快照内容，
守卫是唯一挡住写入树外的东西。但它现在不验证任何东西，这一点必须写出来。**

### 而两个套件数，我核过了

**`metrics_report.py` 报 1815；直接跑全量报 2113 通过 / 2 跳过。差 298。**

**原因（R493 的设计，不是新问题）：`metrics_report.py` 排除六个依赖真 Chrome 的类**
（`VoiceListTests` · `GlobalSurfaceTests` · `KeyOrderDispatchTests` · `PatchJournalTests` ·
`PruneWhitelistTests` · `NetworkRecorderLiveTests`），
**因为 2026-11-14 连着跑几轮全量把整机内存耗尽、系统重启。**

**所以两个数都对，各自对应一个范围：**
- **1815 = 不含浏览器类的套件**
- **2113 + 2 跳过 = 全部**

**而 `--skip-tests` 那次让 METRICS.md 写了「本次未运行 —— 这不等于通过」。**
**按 §2.6 那条（「没跑成」≠「通过」）这个写法本身是对的，但它让 METRICS.md 暂时不能引用。**
**这一轮末尾重跑了完整 metrics，METRICS.md L13 回到 `1815 通过 / 0 失败`。**


### `Submit` 族拆成四桶，而缺口位置被搬了家（R913）

**R912 之后回到优先级 ①。先按次数排结账相关缺失名，得到 244 个 —— 而**次数几乎都是 1**。**

**再看最高的三个：`SubmitShipping` 28 · `SubmitOrder` 24 · `SubmitPayment` 22 ——
**它们都在 `StoreFlow` 上。** 所以「244 个缺失」不说明结账有问题。**

### 所以拆成四桶

| 桶 | 名字 | 出现次数 | 复刻件有 |
|---|---|---|---|
| **base** | **50** | **183** | **26** |
| provider | 14 | 20 | 3 |
| platform | 9 | 11 | 2 |
| **challenge** | **20** | **26** | **3** |

**而缺口在最后两桶：**

**provider 缺：** `AdyenOrder` · `AdyenPayment` · `StripeOrder` · `UnzerOrder` · `KakaoPay` · `HpsPayment` ·
`ExternalPayment` · `WebComponent` · `SDK` · `Paypal` · `ThreeDSAuthentication`

**challenge 缺：** `RecaptchaChallenge` · `PowChallenge` · `POW` · `Challenges` · **`Fingerprint`** ·
**`ClientData`** · **`WebRtc`** · **`BrowserData`** · `Collect` · `CollectRedirect` · `CollectRedirectV2` ·
`Pat` · `Wpt` · `Render`

### 而 challenge 那桶里混了两件事

**`RecaptchaChallenge` / `PowChallenge` / `Challenges` 是**反爬挑战应答**（优先级 ②）。**

**而 `Fingerprint` / `ClientData` / `WebRtc` / `BrowserData` 是**指纹采集**（优先级 ③）——
**它们被放进同一桶只是因为名字里都带 challenge 类的词。**

**所以这一轮也把「优先级 ② 在端点层没有具体缺口」（R905 的撤回）修成了一句更准的话：
**反爬挑战应答有 3 个名字在、还有几个不在；而指纹采集那一组是优先级 ③ 的缺口，不是 ② 的。**

### 一处方法说明

**分桶按名字，而 AGENTS.md §1 的 R730 裁决说「不要用名字替代读代码」。**

**这里用名字**只为把候选分组给人挑**，不声称某个名字属于某一层。
**分错桶的代价是看一眼，不是错结论。**


### 第五个表面：WebRTC —— 而它不是「报告一个值」，是「不报告一个地址」（R914）

**R913 说补变体前要先知道每个变体差什么。从名字最清楚的一组开始：指纹四个。**

### 先查那四个

| 名字 | 复刻件 |
|---|---|
| `SubmitFingerprint` | 概念在（`BrowserIdentity` / `BrowserFingerprint`） |
| `SubmitClientData` | 概念在（`KasadaSolver.cs` 的 `ClientData`） |
| `SubmitBrowserData` | 概念在（`AppPaths.cs` 的 `BrowserData`） |
| **`SubmitWebRtc`** | **完全没有** |

**所以四个里三个只是名字不同，一个是真缺。**

### 而 `Scripts/` 里有 57 个文件，其中五个「表面」

`CanvasSurface` · `WebGlSurface` · `FontMediaSurface` · `MediaQuerySurface` · `VoiceTable` ——
**加上 `WebAssemblySurface` · `NavigatorCensus` · `WindowBaseline` 等。**

**它们都是「让浏览器报告一个和 persona 一致的值」。而 WebRTC 不同：**

> **它不报告值，它**打开通道**，而通道会用网络地址回答。
> 页面构造一个 offer、收集 ICE candidate，就能读到本机私有地址，并且在没有强制中继时读到公网地址。
> **挂代理时，那两个地址正是代理存在的理由。**

### 所以姿态是反的

| 其他表面 | WebRTC |
|---|---|
| 报告一个**必须与 persona 一致**的值 | **不报告 persona 没声称过的地址** |

**两类泄漏：`host` candidate（私有地址，或 Chromium 的 mDNS 名 —— 不指名地址但每台机器稳定，仍能关联会话）与
`srflx` candidate（问 STUN 服务器「我这个源地址看起来是什么」，挂代理时是代理地址，不挂时是真公网地址）。**

### 写了 `WebRtcSurface.cs`

**`Rule` · `CandidateLeaks` · `BodyJs()` · `RequiredFor(bool behindProxy)`，与其他 surface 同形。**

**而 `BodyJs()` 关的是**两半**：**

1. `onicecandidate` 事件里过滤掉 `srflx`/`host`
2. `localDescription` 的 getter 里把同样的 candidate 从 SDP 剥掉

> **只关第一半，直接读 `localDescription.sdp` 的页面仍然看得见。
> 两个同类 surface 的注释里都写过「两半都得对，不是一半」（`matchMedia` 的 `.media` 与 `.matches`）——
> 这里是同一句话的另一个实例。**

**而连接仍然可构造：`Wrapped.prototype = PC.prototype` 且 `Object.setPrototypeOf(Wrapped, PC)`。
**让 `RTCPeerConnection` 抛错会和泄漏一样容易被检出。****

### 6 个用例

`BothCandidateKindsAreNamed` · **`BothHalvesOfTheLeakAreClosed`** · `TheConnectionRemainsConstructible` ·
`ItDoesNothingWhenTheApiIsAbsent` · `TheGuardIsOnlyRequiredBehindAProxy` · `TheRuleStatesTheReasoningRatherThanAClaim`

### 数字，以及一个我必须说清的 +1

| 度量 | R913 | **R914** |
|---|---|---|
| 套件 | 1815 | **1821** |
| 异步覆盖 | 371（24.0%） | **372（24.0%）** |

**那个 +1 是 `SubmitWebRtc` 被算成「有了」—— 而它只出现在我写的**文档注释**里
（「The image names `<c>SubmitWebRtc</c>`」）。**

**所以 `async_method_coverage.py` 会把**文档里提到的名字**算作实现。这是一个已知的假阳性，
而它在**注释引用镜像名字**这种写法下必然出现 —— 而那种写法正是我一直在用的。**

**下一轮该修的是这个：扫描应排除注释，或至少分开统计「出现在代码里」与「只出现在注释里」。**


### 去掉注释再数：覆盖 **23.4%**，而 10 个名字只活在注释里（R915）

**R914 报了 372（24.0%），并说那个 +1 是我自己的注释。这一轮把整件事量清。**

### 三个数

| 判据 | 名字 | 占比 |
|---|---|---|
| **在代码里** | **362** | **23.4%** |
| **只在注释里** | **10** | **0.6%** |
| **两者都没有** | **1175** | **76.0%** |

**而「只在注释里」那 10 个，全部是我在文档注释里点过名、却从没实现的名字：**

```
CheckVerification · ExecuteConfigure · FindProductMultiInstore · GetThreeDsJwtQuery ·
MultipartScanEpilogueAsync · ParseMessageAsync · Purchase · RunShield ·
SubmitSaleRegistration · SubmitWebRtc
```

**这是一张「声称过但不存在」的清单 —— 而 R850 说的「有形状无内容」在这里换了个形态：
**有名字，没有形状，而且名字在文档里。****

### 去注释器为什么不能是正则

**`//` 剥到行尾的正则会撞上字符串里的 URL：**

```
var u = "https://example.test/a"; var after = 1;
                    ^^ 从这两个 / 开始剥，后面的真实代码全没了
```

**而剥掉代码比剥不掉注释**更坏** —— 它让存在的名字看起来不存在。
所以 `strip_comments` 是一个字符扫描器，跟踪四种字面量（普通串、verbatim 串、raw 串、字符字面量）。**

### 9 个用例，其中一个专门钉住这个

| 用例 | 钉什么 |
|---|---|
| **`AUrlInsideAStringDoesNotStartAComment`** | **字符串里的 URL 不开启注释，且其后的代码仍在** |
| `CodeSurvivesStripping` | **纯代码严格不变**（这是「剥多了」的守卫） |
| `AQuoteInsideABlockCommentDoesNotOpenAString` | 注释里的引号不开启字符串 |
| `VerbatimStringDoubledQuotesAreHandled` | `@""` 的转义不提前收尾 |
| `AnEscapedQuoteInAStringDoesNotEndIt` | `\"` 同理 |
| `ACharLiteralHoldingAQuoteIsNotAString` | `'"'` 不开启字符串 |
| `TheTreeSplitsCodeFromComments` | **三个数相加 = 1547** |

### 而测试自身踩了两次坑

**① 第一次全红，因为 `python -c` 的参数被按空格拆开** —— 脚本在第一个空格处变成语法错误。
**② 第二次 `TheTreeSplitsCodeFromComments` 红，因为我用 `Where(char.IsDigit)` 抓数字，
把行尾的百分比也抓进去了（`362  23.4%` → `362234`）。** 改成只取冒号后第一段数字。

### 数字与代价

| 度量 | R914 | **R915** |
|---|---|---|
| 套件 | 1821 | **1830** |
| **异步覆盖（去注释）** | 372（24.0%，含假阳性） | **362（23.4%）** |
| 缺失名承载出现次数 | 1303 | **1313** |

**而代价：那 9 个用例跑了 **1 分 16 秒**，因为每个 `Strip` 起一个 python 进程。
**套件从 4 分钟涨到 6 分钟。这是可接受但我该写在案的成本。****


### `RunShield` 实现了，而证据是**序号**而不是字面量（R916）

**R915 说从「只在注释里」那 10 个里挑真该实现的。挑了 `RunShield`，因为它的证据最多。**

### 查到的证据：一个序号序列

```
ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21 · TrimStrings 25
```

**而 `RunShield` 的局部变量是 `<data2>5__3` 与 `<shieldQuery>5__4`。**

**所以它**不是** R905 一开始判的那个孤立的 OTP 调用，而是**支付流程里的一个步骤**：
**打开安全页 → 导航 → 运行 shield → 处理结果**，而 `CardHolderName` 在后面。**

> **这个判断来自**序号相邻**与**局部变量名**，不来自任何字面量。
> 而 R905 我当时只看到 `/shield/v1/verify_otp` 一条路径，就把它归成「支付 OTP」——
> 方向对了，但**位置**搞错了：它在流程里，不在流程外。**

### 实现了什么

| 文件 | 改动 |
|---|---|
| `Flows/StoreFlow.cs` | `+ RunShieldAsync` 虚方法（**176** 个虚步骤） |
| `Payments/PaynamicsShield.cs` | **新建**：收 `FlowSession` + 一个 post 委托，不绑死 HTTP 客户端 |
| `tests/PaynamicsShieldStepTests.cs` | **6 用例** |

**而它调的正是 R905 恢复、却从没人用的那一对：`shield.paynamics.net` + `/shield/v1/verify_otp`。**

### 三个刻意的选择

**① 收 `FlowSession` 而不是 `FlowContext`。**
**它只读会话变量；收整个 context 会让每个测试都要造一个活 `NetClient`，
还会暗示它用了 context 里带的商品/卡/代理 —— 而它没用。**

**② 无 device token 时**明确失败且可重试**。**
**空 token 发出去会「成功」而什么都没挡。**

**③ 不认识的响应**仍然记录**。**
**答案的含义不明，丢掉就丢了唯一能被下一轮读的证据。**

### 数字

| 度量 | R915 | **R916** |
|---|---|---|
| 套件 | 1830 | **1836** |
| `StoreFlow` 虚步骤 | 175 | **176** |
| **异步覆盖（代码里）** | 362（23.4%） | **363（23.5%）** |
| **只在注释里** | **10** | **11** |

**而那个 11 要看仔细：`RunShield` **移出**了那一格（真实现了），
但 `OpenSecurePage` 与 `ProcessResult` **移入**了（我在新注释里点了它们）。**

> **所以这一轮在同一格上同时做了减法和加法 —— 净 +1，而净数掩盖了两件事都发生。**

### 一个测试红了，而它是**对的**

**`OnePopMartImageStepIsDispatchable` 报 `map.Count` 从 175 变 176。
它红得正确：我又加了一个不在 Pop Mart 24 个名字里的步骤。**

**这已经是连续第三次（`FindProductInstore` R891 · `AddToCartBox` R908 · `RunShield` R916）——
**三次都是「map 涨、coverage 不涨」。**

**所以那句话该写成结论而不是感慨：**镜像的步骤词汇比任何单个 flow 的序列都宽。**
**一个 flow 的序列是子集，而 map 是全集 —— 用 coverage 衡量 map 会说谎。****
