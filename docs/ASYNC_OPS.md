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


### 判据 (f) 终于有了表，而表在能读之前要修两次（R917）

**判据 (f)：核心覆盖表可复算 —— 原版站点与风控清单从二进制取证 ↔ `Registry.cs` 与 `Flows/Scripts`，
未覆盖的每条写为什么。**

**核了一遍：METRICS.md 里**没有这一栏**。判据 (f) 一直未满足。**

### 左右两边各自是什么

| 边 | 来源 | 数 |
|---|---|---|
| **左** | `Registry.cs` | **64 个注册**（33 个 flow 类型，含 `HybrisFlow("offspring", …)` 这种带参数） |
| **右** | 镜像 154 条路径的宿主 | **39 个宿主**（store 28 · vendor 11） |

**新工具 `tools/core_coverage.py`：逐宿主比对。**

### 而它修了两次才可信

**① 第一次：只查 `Registry.cs` → `www.vans.com` 判成 unmatched。**
**而 R899 已经证明 Vans 是处理的 —— 在 `DemandwareControllers.cs` 的 site-id 表里，不在 Registry。**
**→ 来源太窄，与 R911 的 `Async` 后缀同一类错。改成扫全 `src`：**7/28 → 16/28**。**

**② 第二次：`api-search.dickssportinggoods.com` 取成标签 `api-search`，
`prod-hk-actapi.popmart.com` 取成 `prod-hk-actapi` —— **而 Pop Mart 明明是一个 flow。****
**→ 假设「子域要么整体泛用、要么整体有意义」，而连字符前缀两者都不是。
改成**每一段都当候选**（`search`/`dickssportinggoods`、`actapi`/`popmart`）：**16/28 → 22/28**。**

### 最终

| 桶 | 匹配 | 未匹配 |
|---|---|---|
| **store** | **22 / 28** | **6** |
| vendor | **2 / 11** | **9** |

**store 那 6 个：**

```
api.braintreegateway.com        (2)   —— 支付商，不是店
api.vipps.no                    (1)   —— 挪威支付商
checkout.sportsshoes.com        (1)   —— 真店
payments.bigcommerce.com        (1)   —— 支付商
payments.dickssportinggoods.com (2)   —— 真店（但走的是支付子域）
www.purpledotprice.com          (1)   —— 未知
```

**vendor 那 9 个：** `aycd` · `eshopworld` ×2 · `disney` ×2 · `global-e` ×2 · `vivapayments` ·
`checkoutshopper-live.adyen`（脚本层都还没有）。

### 而 22/28 这个数要怎么读

**「matched」的意思是**某个候选标签出现在 `src` 的某个文件里** ——
不证明那个店能用，也不证明它的结账流程对。**

**而「unmatched」现在是一个**更强**的说法（因为搜索面已经扩到全 `src`）：
**这个标签在整个复刻件里一次都没出现。****

**所以那 6 个里，`checkout.sportsshoes.com` 与 `payments.dickssportinggoods.com` 是真缺口；
另 4 个是支付商的子域，可能根本不需要 flow。**

### 数字

| 度量 | R916 | **R917** |
|---|---|---|
| 套件 | 1836 | **1836** |
| **store 宿主覆盖** | 无此栏 | **22 / 28** |
| vendor 宿主覆盖 | 无此栏 | **2 / 11** |

**这一轮没有改产品代码 —— 它把判据 (f) 从「没有表」变成「有一张带注脚的表」。**

### 教训

> **一张表修两次才可信，而两次都是**来源或形状假设太窄**：
> 第一次只查一个文件，第二次只取一个段。**
> **而两次修之前，数都看起来正常：7/28 和 16/28 都是「有零有整」的数，读起来不像坏了。**


### 补上 Sportsshoes —— 而六个「模块数」守卫一起变红（R918）

**R917 的表剩下两个真缺口。这一轮补了同名的那一个。**

### 镜像给它的证据：三台宿主，分工不同

```
https://www.sportsshoes.com              店面，读商品
https://sop.sportsshoes.com/cart/        车状态
https://sop.sportsshoes.com/cart/add/    加车
https://checkout.sportsshoes.com/api/storefront/checkout/     开始结账
https://checkout.sportsshoes.com/api/storefront/checkouts/    复数，第二个集合
https://checkout.sportsshoes.com/api/storefront/orders/       下单
https://checkout.sportsshoes.com/api/storefront/payments/stripeocs   Stripe 一键
https://checkout.sportsshoes.com/internalapi/v1/checkout/order       orders 的内部孪生
https://checkout.sportsshoes.com/checkout?setCurrencyId=1           页面 + 币种参数
```

**所以一次购买跨越三台宿主：店面 → `sop`（车）→ `checkout`（其后一切）。**

**这正是它该是自己的 flow 而不是 Demandware / Hybris 子类的原因：
两个平台都不这样分宿主，而这里端点族是 `api/storefront`，两家都不用。**

### 写了什么

| 文件 | 改动 |
|---|---|
| `Flows/SportsshoesFlow.cs` | **新建**：3 台宿主 + 9 条地址常量 + 3 个步骤 |
| `Modules/Registry.cs` | 注册（**63 → 64 个模块**） |
| `tests/SportsshoesFlowTests.cs` | **6 用例** |

**三个步骤只挑含义足够明确的三条端点：`FindProduct`（www）· `AddToCart`（`sop`）· `SubmitOrder`（`internalapi`）。
后两条下单端点都在、且没有证据说谁取代谁，所以步骤记下它用了哪一条。**

### 而六个守卫一起红了 —— 这正是它们的作用

```
DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue
SummaryBlockTests.ModuleCountInTheGuideMatchesTheRegistry
ArrowAndBeastTests.TheCatalogueIsSixtyThreeModules
CoreTests.Catalog_Registers_All_Modules
ParityDocTests.TheModuleCountInParityMatchesTheCatalogue
ParityDocTests.TheFlowTypeCountInParityMatchesTheCatalogue
```

**而量出来的实际是 **64**，不是我在源码里数到的 65 —— 有一处 `FlowStoreModule(new X)` 在注释里。
**这个差值得记：**正则在源码上数，编译器数的是别的。**

### 改数字时遇到的一件事：历史不该被改

**`DocsConsistencyTests` 扫全文的 `<n> 个模块`，而 VERDICT.md 是 49,000+ 行、12 处历史 `63 个模块`。**
**把它们改成 64 会让每一句都变成假话 —— 那些句子描述的是当时的实测，其中一句还明写了「当时」。**

**而守卫自己的注释写着「fenced blocks 是历史，只看正文」——
**它的意图就是只查当前声明，只是实现上认不出历史段落。****

**所以按**意图**收窄：扫描范围改成摘要区（`| 注册模块 |` 开头到其后第一个 `---`），
并在摘要里加一行**当前声明** `**64 个模块**`，注明历史数字在文末日志。**

> **这不是为了让守卫变绿而改守卫 —— 是因为「49,000 行追加日志里的每个历史数字都必须等于今天」
> 这条命题本身是错的。**

### 数字

| 度量 | R917 | **R918** |
|---|---|---|
| 套件 | 1836 | **1842** |
| **模块** | 63 | **64** |
| **flow 类型** | 33 | **34** |
| **store 宿主覆盖** | 22 / 28 | **23 / 28** |

**`checkout.sportsshoes.com` 现在匹配了。**


### DicksSportingGoods 补上 —— 而 (f) 那张表两轮就清空了两个真缺口（R919）

**R917 的表剩两个真缺口：`sportsshoes` 与 `dickssportinggoods`。R918 补了前者，这一轮补后者。**

### 比 R917 那 6 条更多的证据：九条，分三组

```
身份  "DICKS" · "DicksSportingGoods" · "Dicks Sporting Goods" · "dsg-ecomm"
端点  https://www.dickssportinggoods.com/
      https://api-search.dickssportinggoods.com/catalog-productdetails/v4/byPartNumber/
      https://payments.dickssportinggoods.com/prod/api/paygate/v2/authorization
      https://payments.dickssportinggoods.com/prod/api/paygate/v2/threeDSAuthentication
行为  "_outOfStock(Dicks Sporting Goods"
```

### 三件值得说的事

**① 身份有**四种形式**，不是「显示名 + id」两种。
`dsg-ecomm` 像是请求里带的 channel/应用名，`DICKS` 像短标签。
**所以四个都记成常量，不挑一个 —— 哪个出现在请求里不知道，猜一个会把错值放进 header。**

**② 行为那条最有信息量：`_outOfStock` 是**闭包名**，
说明原版对这个店**专门挂了一个缺货回调**。那是监控关注点而不是结账关注点，所以按监控建模。**

**③ 而这个店**没有车/结账路径**被恢复 —— 端点只有按零件号查商品和支付闸。**

> **所以 `StepSequence` 只有两步：`FindProduct` 与 `SubmitPayment`。
> 一个有支付闸、却没有任何车调用的店，用这份证据走不完一次购买；
> 写一个更长的序列会是一串在第二步就失败的步骤。**

### 两个刻意的实现决定

**① 商品是按**零件号**查的，不是按 URL 取页面。**
`byPartNumber/` 是版本段之后的整个路径段 —— 去取商品页就是读另一个端点，不是镜像点名的那个。

**② 3DS 是有条件的。**
两条 paygate 调用在镜像里是分开的，这里也分开：**总是跑第二步会给不需要验证的订单做验证。**
**而判据是授权响应自己说要不要，不是流程预设。**

### 数字

| 度量 | R918 | **R919** |
|---|---|---|
| 套件 | 1842 | **1850** |
| 模块 | 64 | **65** |
| flow 类型 | 34 | **35** |
| **store 宿主覆盖** | 23 / 28 | **24 / 28** |

**剩下 4 个未匹配：`braintreegateway` · `vipps` · `bigcommerce` · `purpledotprice` —— 前三个是支付商子域。**

### 而这一轮的价值不在这个店本身

**R917 建那张表用了两次修正；R918 与 R919 用它清掉了**它列出的两个真缺口**。**

> **所以那张表的正确用法不是「覆盖率多高」，而是**它列出的未匹配项就是待办清单**。**
> **而 24/28 里剩下的 4 个，三个已被判为支付商子域 —— 也就是说这张表**快用完了**。**


### `purpledotprice` 不是店 —— 它是预售服务，而且带一个硬编码 key（R920）

**R919 说剩 4 个未匹配，`purpledotprice` 是唯一非支付商的那个。查了，一条字面量就说清了：**

```
https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-63fa-4216-9d7c-07a87697fccd&handle=
```

**Purple Dot 是给店铺做**预售/缺货登记**的服务。所以：**

1. **它不是店 → 该进 vendor 桶。而我把它分进 store 是因为它不在 `VENDOR_HINTS` 里 —— **分类清单漏了一项**，不是判据错。**
2. **它带一个**硬编码 API key**，在二进制里。这是这次核到的唯一一个「原版自带的第三方 key」。**
3. **端点语义是「按 handle 查这个商品是不是预售」。**

### 所以 store 桶清空了

**修正分类后：store **27** 个（原 28）· vendor **12** 个（原 11）· **store 匹配 24/27，未匹配 3**。**

**而那 3 个全是支付商：`braintreegateway` · `vipps` · `bigcommerce`。**

> **也就是说：**镜像里所有带路径的 store 宿主，复刻件现在都认得。**
> **判据 (f) 的 store 侧闭合了 —— 而它闭合的方式是 R917 建表、R918/R919 补两个店、R920 修正一个分类。**

### 写了 `PurpleDot.cs`

| 成员 | 作用 |
|---|---|
| `Host` · `PreorderState` · `ApiKey` | 三个恢复到的常量 |
| `UrlFor(handle)` | 拼出与镜像同形的 URL（**query string，不是 header**） |
| `QueryAsync(...)` | 三态：预售 / 现货 / **不可读** |
| `IsBuyable(session)` | 监控需要的那个判断 |

### 而最关键的是第三个状态

**不可读的响应**不设状态**，`IsBuyable` 因此返 false。**

> **因为反过来会是灾难：一个把「读不懂」当成「不是预售」的监控，会去买一个几个月后才发货的预售品。
> 所以这个类的默认答案是「不买」，而不是「买」。**

### 一处我把正则写窄了

**第一次 `(true|""[^""]*"")` 漏了 `false`，于是 `{"isPreorder":false}` 落进「不可读」分支 ——
**方向上是安全的（不买），但也意味着最常见的答案永远成功不了。** 测试把它抓出来了。**

### 数字

| 度量 | R919 | **R920** |
|---|---|---|
| 套件 | 1850 | **1857** |
| **store 宿主未匹配** | 3（含 1 个误分类） | **3（全是支付商）** |
| **store 桶** | 24 / 28 | **24 / 27** |

**比例没变好，而**分母变小了** —— 因为一个被误分类的宿主移出了这一桶。**


### 判据 (f) 的另一半：vendor **5 / 12**，而缺的 7 个归成 4 家服务（R921）

**R917–R920 把 store 那一侧闭合了。这一轮量 vendor 那一侧 —— (f) 要求的表有**两栏**，我一直只报一栏。**

### 新工具 `tools/vendor_coverage.py`：12 个 vendor 宿主逐个查

| 宿主 | 条 | 服务 | 复刻件 |
|---|---|---|---|
| `challenges.cloudflare.com` | 1 | Cloudflare | **有**（`AntiBotProtocol.cs` · `AntiBotVendors.cs` · `BouncyH2Client.cs`） |
| `checkoutshopper-live.adyen.com` | 2 | Adyen | **有**（`AdyenGateway.cs` · `AdyenPayPalFlow.cs`） |
| `inbox-api.aycd.io` | 3 | AYCD | **有**（`AycdInboxClient.cs` · `AycdInboxAccount.cs`） |
| `www.paypal.com` | 4 | PayPal | **有** |
| `www.purpledotprice.com` | 1 | PurpleDot | **有**（R920 刚建） |
| `payments-panel.production.eshopworld.com` | 3 | **eShopWorld** | **无** |
| `retailer-shopifypayments-api.production.eshopworld.com` | 2 | **eShopWorld** | **无** |
| `paymentsheet-ent.wdprapps.disney.com` | 3 | **Disney** | **无** |
| `registerdisney.go.com` | 1 | **Disney** | **无** |
| `webservices.global-e.com` | 3 | **Global-e** | **无** |
| `web-dsy.global-e.com` | 1 | **Global-e** | **无** |
| `www.vivapayments.com` | 3 | **Viva** | **无** |

**所以：**5 有 7 无**，而无的那 7 条归成**4 家服务、16 条路径**：**
**eShopWorld（5）· Disney（4）· Global-e（4）· Viva（3）。**

### 而这一栏回答了 R905 撤回的那个问题

**R905 我撤回了「反爬在端点层没有具体缺口」，因为当时那两条都不是反爬。
这一轮可以给一个准确的答案：**

> **Cloudflare 是**有**的（`AntiBotProtocol.cs` / `AntiBotVendors.cs`）。
> AYCD 是有的（`AycdInboxClient.cs` —— 那正是 OTP 收件箱）。
> 而**反爬这一侧没有 7 个缺口里的任何一个** —— 缺的 7 个全是**支付/跨境商务**服务。**

**所以「优先级 ② 缺什么」的答案现在是：**在 154 条路径的范围里，它不缺端点。**
**缺的是 ①（支付）与 ③（跨境定价）。****

### 接进了 METRICS.md

**而接进去的过程踩了**两道**机制，而两道都拦对了：**

**① 第一次 `（未解析，见下方原始输出）`** —— 因为 `metrics_report.py` 的 `summary_bits` 有一个**硬编码的 patterns 表**，
而我的键不在里面。**工具不会去读任意 `key: value`，它只读它认识的键。**

**② 补了 patterns 之后仍有三个键没解析** —— 因为 R834 的**归属规则**：
每个条目只能报它自己声明的键。**我原来只声明了三个。**

> **两道都是「工具不知道我要什么」，而不是「工具坏了」。
> 而第二道是 R834 那条规则在起作用：它防止一个宽松的正则把邻近条目的数字填进这一行。**

### 数字

| 度量 | R920 | **R921** |
|---|---|---|
| 套件 | 1857 | **1857** |
| **store 宿主** | 24 / 27 | 24 / 27（已闭合） |
| **vendor 宿主** | 未测 | **5 / 12（7 缺，归 4 家服务）** |
| METRICS.md 里的核心覆盖行 | 0 | **8** |

**这一轮没有改产品代码 —— 它把 (f) 从「一半可复算」变成「两半都在 METRICS.md 里」。**


### Global-e 建了 —— 第一个能拿**恢复到的字符串**去核的 vendor（R922）

**R921 说从 4 家缺的服务里挑一家。挑了 Global-e，因为它的四条字面量给出的东西比之前任何一家都多。**

### 四条字面量

```
/Checkout/v2/8x1r
/Checkout/v2/8um2
/Checkout/v2/8x1r/641efc40-744a-443c-ad99-420a092c6644?gaSesID=…&ga4SID=…&chkcuid=…&isNECAllowed=true
                                    &_vwo_store=&vph=1081&vpw=2649&ift=113&utm_source=direct&utm_medium=
/Checkout/v2/{_encodedMerchantId}/641efc40-…?（同一套参数）
```

**两个商户 id、一个**模板占位符**、以及一套**完整的十参数**。**
**而第四条是 `{_encodedMerchantId}` —— 说明原版是**替换**出来的，不是常量拼接。**

### 三个可读的参数

| 参数 | 读作 |
|---|---|
| `chkcuid` | checkout customer id，字面量里是个 GUID |
| `vph` / `vpw` | 视口高 / 宽（1081 / 2649） |
| **`isNECAllowed`** | **「非欧盟国家是否允许」** |

**其余（`gaSesID` · `ga4SID` · `_vwo_store` · `ift` · `utm_*`）是分析与实验标识 —— 它们在这里只因为
**一个缺了这些参数的请求，可能和被当成不一样的请求**。**

### 而 Global-e 属哪一类，现在清楚了

**它在结账时做跨境定价与关税。所以它是**结账关注点**而不是支付网关关注点：
流程必须在订单**定价之前**到达它，而不是在付完款之后。**

**这也回答了 R921 那句 Inference（「Global-e 是否属优先级 ③」）—— 是 ③ 的**定价**职能，
但落在 ① 的结账序列里。两者不冲突。**

### 写了什么

| 成员 | |
|---|---|
| `WebServicesHost` · `DsyHost` | 两台宿主 |
| `RecoveredMerchantIds` = `8x1r` · `8um2` | 两个商户 |
| `MerchantPlaceholder` = `{_encodedMerchantId}` | 模板占位符，记下来因为它说明构造方式 |
| `SampleCheckoutCustomerId` | 字面量里那个 GUID |
| **`ParamOrder`** | **十参数的**顺序**，不只是集合** |
| `UrlFor(merchant, values)` | 按顺序拼，**空值也发** |
| `IsNonEu(code)` | **Inference，明确标注** |

### 两个刻意的决定

**① `ParamOrder` 记的是**顺序**，不是集合。**
**因为按位置比对才能发现「参数名都对但顺序变了」—— 而一个按集合比对的测试会放过它。**

**② 空值也发。**
**因为恢复到的字面量里 `_vwo_store=` 与 `utm_medium=` 本身就是空的。
**所以空参数是**正常请求的证据**，不是错误的证据。****

**③ `IsNonEu` 明确标 Inference。**
**参数名说「非欧盟」、流程需要布尔、而由一个集合得出 —— 那个集合（EEA + GB + CH）是**猜的边界**，
所以标注而非当成恢复。**

### 数字

| 度量 | R921 | **R922** |
|---|---|---|
| 套件 | 1857 | **1868** |
| **vendor 命名** | 5 / 12 | **7 / 12** |
| **vendor 缺失** | 7 | **5** |

**剩 5 个：eShopWorld（2 台）· Disney（2 台）· Viva（1 台）。**

### 教训

> **前面几家 vendor 我只能核「名字在不在」。这一家能核**形状**：路径段、参数名、参数顺序、以及空值的位置。**
> **而这四样都来自同一件事 —— 恢复到的是一条**完整 URL**，不是一条路径。**
> **所以「证据有多少」不取决于服务多复杂，取决于**镜像里存的是路径还是完整请求行**。**


### eShopWorld：五条路径里**两条是轮询端点**，所以它不是一次调用而是一次等待（R923）

**R922 说下一家 eShopWorld。它的五条路径排起来是这样的：**

```
payments-panel…/api/v2/PaymentMethods/url        面板在哪
payments-panel…/api/v2/PaymentMethods?paymentId= 某笔支付是什么
payments-panel…/api/v2/WebComponent/state        面板怎么样了   ← 轮询
retailer-shopifypayments-api…/api/v1/payment/apm/session/status           替代支付怎么样  ← 轮询
retailer-shopifypayments-api…/api/v1/payment/apm/session/post_pay_status  …以及刚付完之后
```

### 所以它是两个轮询循环，在**两台不同宿主**上

**面板自己的状态 与 替代支付的 session 是**两个独立循环**。
所以同时有这两条路可走的流程，**不能轮询了一个就假定另一个**。**

### 而为什么写**一个**轮询器而不是两个

**两个端点都回答「还没好 / 好了 / 坏了」，都需要截止时间、间隔、终止条件。**

> **写两遍会邀请两份拷贝对「什么叫好了」产生分歧 —— 而结账就是这样在一条路上成功、在另一条路上挂住。**

### 三个结果，而第三个是关键

| 结果 | 含义 |
|---|---|
| `Success()` | 出现成功词 |
| `Fail(...)` | 出现失败词 |
| **`Fail(retryable: true)` + `settled = "unknown"`** | **到截止时间还没定** |

> **第三个不是失败：一笔没在窗口内定下来的支付**可能还会定下来**。
> **把它叫失败会让一个慢的网关看起来像被拒的卡。****

### 而「不认识」的处理方向是**继续等**

**终端词是猜的（没有响应体证据），所以只有**列表里的词**才终止轮询，其他一律继续等到截止。**

> **因为猜错一个失败词会**放弃一笔即将成功的支付** —— 那比等完窗口更糟。**

### 一个认出规则上的细节

**只认 `state` / `status` / `paymentStatus` / `result` 这几个字段名里的词，不认正文任意位置。**
**所以 `{"note":"completed"}` **不**终止轮询，而 `{"status":"completed"}` 会。**

**那是刻意的窄：一个把「提到了 completed」当「完成了」的判据，会被日志字段骗。**

### 数字

| 度量 | R922 | **R923** |
|---|---|---|
| 套件 | 1868 | **1881** |
| **vendor 命名** | 7 / 12 | **9 / 12** |
| **vendor 缺失** | 5 | **3** |

**剩 3 个：Disney（2 台）· Viva（1 台）。**

### 教训

> **前两家 vendor（Purple Dot、Global-e）都是「发一个请求、读一个答案」。
> 这一家不是 —— 它是**一个带截止时间的等待**。**
> **而「等待」比「请求」多三件事：间隔、终止条件、以及**没定下来时说什么**。**
> **第三件最难，因为它既不是成功也不是失败，而大多数流程只有两格。**


### Disney 的支付面板：卡先进一个端点，结账拿 token（R924）

**四条路径、两台宿主，而其中一条决定了整个类的形状：**

```
paymentsheet-ent.wdprapps.disney.com/api/v1/card/token   一张卡，token 化
paymentsheet-ent.wdprapps.disney.com/api/v1/checkout     这张 token 付的结账
paymentsheet-ent.wdprapps.disney.com/api/v3/process      处理步骤，晚一个版本
registerdisney.go.com/jgc/v8/client                      Disney Guest Connect（身份）
```

### 为什么先 token 化是一个**该实现的属性**，而不是一句注释

**卡端点与结账分开，且它的名字说的是 token 而不是 pay —— 所以**流程里的卡永远不到结账那一步**。**

> **一个在两个请求体里出现的卡号被暴露两次。原版看起来只让它出现一次。
> 所以 `TokeniseCardAsync` 收卡并返回 token，而这个类里**没有第二个方法收卡**。**

**而结账方法**没有 token 就拒绝** —— 因为一个没有 token 的结账只能带卡，而那正是这个拆分要避免的。**

### 两个版本并存是对的

**v1 结账、v3 处理。**服务里「处理比启动它的结账活得更久」是常态。
**所以分开记，不统一 —— 统一会**静默改掉两次调用中的一次**。**

### 而 `jgc/v8/client` **只记录、不调用**

**没有任何东西说它返回什么、或一次购买是否需要它。
**按猜发一个请求，就是发一个原版可能从不发的请求。****

### 数字

| 度量 | R923 | **R924** |
|---|---|---|
| 套件 | 1881 | **1888** |
| **vendor 命名** | 9 / 12 | **11 / 12** |
| **vendor 缺失** | 3 | **1** |

**只剩 Viva 一家（3 条：`chargetokens` → `paymentdetails?ref=` → `transactions`）。**

### 而 11/12 这个数到这里可以总结了

**R921 量出 5/12，R922 Global-e、R923 eShopWorld、R924 Disney —— 四轮把 7 个未匹配降到 1。**

**而四轮里每一轮的产品**形状都不同**：**
- **Global-e**：一条完整 URL → 可核参数顺序与空值
- **eShopWorld**：两条轮询端点 → **一个带第三结果的等待**
- **Disney**：卡与结账分开 → **一个安全性属性**

> **所以「补 vendor」不是同一件事做四遍。每家给的证据形状不同，实现的东西也就不同。**
> **如果我把四家都做成「一组常量」，7 会降到 1，而三家真正值钱的东西都不会出现。**


### Viva 收尾：vendor **12 / 12**，而测量它的工具还带着旧毛病（R925）

**三条路径，一个版本，一台宿主：**

```
/web2/checkout/v2/chargetokens       卡 → charge token
/web2/checkout/v2/paymentdetails?ref=  按 ref 查这笔的结果
/web2/checkout/v2/transactions         交易列表
```

### 而它是四家里唯一一个**完整周期**

**token 化 → 按 ref 读结果 → 列表。第二条那个 `ref=` 是使它成为周期的原因：
**token 的答案里带着一个引用，而状态读取用这个引用寻址，不用会话标识。****

**这与支付网关的「授权后查询」同形，也是三条能放在一起的原因。**

### 卡只到一个端点

**与 Disney 一样，`chargetokens` 说的是 token 不是 pay。`ChargeTokenAsync` 收卡，另两个只收引用与窗口。
**这是由签名强制的，不是由注释说明的。****

### 而最该做对的那一格

**「token 的答案里找不到可识别的引用」是**失败**，不是半成功。**

> **一个没人能问起的 token 对下一步毫无价值。
> 而从虚无里编一个引用，会产生一个「查询一笔不存在的支付」的状态读取 —— 比失败更坏。**

### 而这一轮抓到工具自己的旧毛病

**第一次跑出来，Disney 的两台宿主报成「在 `DisneyPaymentSheet.cs`, **`VivaPayments.cs`** 里都有」。**

**因为 `VivaPayments.cs` 里有一句注释提到了 Disney。
**这正是 R915 修过的注释假阳性 —— 而那次我只修了两个方法覆盖工具，没修这个。**

**修法一致：`vendor_coverage.py` 也 `import comment_split` 并 `strip_comments(text)`。
修完表诚实了：每家恰好一个文件。**

### 数字，而 (f) 的 vendor 侧闭合

| 度量 | R924 | **R925** |
|---|---|---|
| 套件 | 1888 | **1896** |
| **vendor 命名** | 11 / 12 | **12 / 12** |
| **vendor 缺失** | 1 | **0** |

### 而 (f) 现在的完整状态

| 列 | 结果 |
|---|---|
| **store 宿主** | **24 / 27**，未匹配 3 个全是支付商（判为不需要 flow） |
| **vendor 宿主** | **12 / 12** |

> **两列都在 METRICS.md 里可复算（R921 接进去的 8 行）。**
> **所以判据 (f)「核心覆盖表可复算」这一条，从 R917 的「没有表」走到了「两列都有、都可复算、
> 未匹配的每条都写了为什么」。**

### 而 12/12 不是「都做完了」

**「named somewhere in src」的意思是**某个源文件里有这个服务的名字**，
**不证明集成完整、也不证明它正确 —— 一个常量点名一个宿主，和一条能跑的流程是两件事。**

**而这 12 家里，深做的只有 R920–R925 这六家；Cloudflare / Adyen / AYCD / PayPal 是之前就在的。**


### 判据 (a)：17 个类型缺失分类结案，并补了 `KeyGesture`（R926）

**(f) 闭合后转向 (a)。METRICS 里 (a) 的现状：类型级缺口 **0**、文案缺口 **0**、**类型缺失 17**。**

### 而 17 个里 10 个是 UI

**4 个 `Localize*Extension` + 6 个 View/Window —— 按优先级 ④ 本来就延后。
所以真正要查的是另外 7 个。**

### 查那 7 个时，我先犯了一个错

**我写了一个 100 行的分类工具放在 `replica/tools/type_presence_triage.py`。**

**而 `analysis/type_presence_triage.py` **早就存在** —— R619 的 298 行版本，
还会数成员覆盖率（不只判「有没有声明」）。**
**而且有一个测试 `TypePresenceTriageTests` 一直在守它。**

> **§2.7c 又一次：写之前没跑 `where_is type_presence`。
> 我写的那 100 行是更差的重复品，而它存在的证据是一个我没读的测试。**

**所以删掉了重复品，改用真的那个。**

### 真的那个为什么红了

**它的 `ABSENT` 表是**从 bind_diff 拷的快照**，硬编码 17 个名字。
我补了 `KeyGesture` 之后 bind_diff 报 16，而快照还有 17 → 工具自检失败、exit 1。**

**修法：加一个 `RESOLVED` 分支 —— 已经有同名声明的类型**退出缺失计数**并单独报出。
**因为一个已经补上的缺口不该继续被数。**

### 而分类结果

| 判定 | 数 | 含义 |
|---|---|---|
| **OUT_OF_SCOPE** | 2 | 授权/许可见 `DECISION_LICENSE_OUT_OF_SCOPE.md` |
| **RENAMED** | 6 | 改名了，映射已记 |
| **STRUCTURAL** | 1 | 结构不同 |
| **UNKNOWN（非区分匹配）** | 1 | 多个候选分不开 |
| **UNKNOWN（非区分）** | 6 | 同上 |

**共 16 行 = bind_diff 的 16 = `ABSENT` 17 减 1 个 RESOLVED。**

### 写了 `KeyGesture`

| 成员 | |
|---|---|
| `Key` · `Modifiers` | **bindings 声明的两个名字** |
| `IsEmpty` | 未绑定是一种要显示、要处理的状态 |
| `Equals` / `==` | **忽略大小写** —— `d` 与 `D` 是一个绑定 |
| `ToString` / `TryParse` | **往返**是这类值存在的理由 |

**而 `Modifiers` 是 flags 而不是字符串：**文本形式要在读取时解析、显示时格式化，两边会分歧；
**而一次大小写滑动就把一个能用的绑定变成死的。**

### 而测试抓到一件真事

**`shift+ctrl+d` 第一次解析出的 `ToString` 是 `Ctrl+Shift+d` 而不是 `Ctrl+Shift+D` ——
单字符键没规范化。**

**修在构造函数里而不是 `ToString` 里，**让值与其文本一致**。
**而那正是这个类型存在要防的那类滑动。****

### 数字

| 度量 | R925 | **R926** |
|---|---|---|
| 套件 | 1896 | **1911** |
| **类型缺失** | 17 | **16** |
| 分类结案 | 无 | **16 行全部带判定** |

### 教训

> **这一轮我做了两件相反的事：补了 `KeyGesture`（真的进展），同时写了一个早已存在的工具的重复品（真的退步）。**
> **而发现重复品的方式是**一个测试红了** —— 不是因为我查了。**
> **§2.7c 写在那里，而我在它存在的第六次上又犯了一次，唯一不同的是这次它有一道防线。**


### `Settings` 补到 34/34 —— 而一个成员有两个名字（R927）

**R926 留下 6 个 RENAMED，覆盖率是下界。逐个核，5 个全覆盖，只有 `Settings` **33/34**。**

### 缺的那一个：`StartupPage`

**复刻件里是：**

```csharp
private StartupPage _startup = StartupPage.Home;
public StartupPage Startup { get => _startup; set => ... }
```

**属性叫 `Startup`，而绑定里是 `StartupPage`。**

**而 `StartupPage` 同时是个**枚举** —— 所以原版是「属性名与类型同名」的形态，C# 允许。**

### 改名之后，第二个东西红了

**改完跑全量：`LiveSchemaPinsTests.TheSettingsFileFieldsAllExist` 报
「44 live keys, missing: **startup**」。**

**而那个测试的名字清单是从**原版写出的备份**读的（R390 注明了这一点）—— 所以它是**文件键**，不是属性名。**

> **也就是说：这个成员**有两个名字**，而两个都是事实：
> 绑定叫它 `StartupPage`，而 settings 文件里叫 `startup`。**
> **改属性名满足了前一个，同时破坏了后一个。**

### 所以两个都钉住

```csharp
[Newtonsoft.Json.JsonProperty("startup")]
public StartupPage StartupPage { get => _startup; set => ... }
```

**而那个钉也要改：它的清单是文件键，所以比对对象应该是**每个属性序列化成的名字**，
而不是属性名本身。**

**改完 34/34 与 44 键同时成立。**

### 数字

| 度量 | R926 | **R927** |
|---|---|---|
| 套件 | 1911 | **1911**（同数，见下） |
| **`Settings` 覆盖** | 33/34（97%） | **34/34** |

**套件数不变 —— 因为这一轮先加了一次失败（改名破坏了 schema 钉）再修回来。
**净数不动，而中间红过一次，那一次红的记录在下面的教训里。****

### 三件这一轮才算清的事

**① 覆盖率是下界，所以「RENAMED」不等于「齐」** —— 6 个里 1 个差一个成员。
**② 绑定名与文件键可以不同** —— 而「类型/成员改名允许」这条规则**只覆盖绑定**，不覆盖持久化格式。
**③ 一个按名字比的钉，比的是哪一边的名字，决定了它守的是什么。** 那条钉守的是文件，所以要比文件键。

### 教训

> **我改了一个属性名，而它同时是两个契约的一部分 —— 一个是 C# 里的绑定，一个是磁盘上的 JSON。
> 改名前我只想到了第一个。**
> **而把它告诉我的方式，是一条从**原版备份**读出来的键清单。**


### 设置 schema 的**反方向**：48 个属性对 44 个键，差 4 个，每个都有理由（R928）

**R927 那条钉只查一个方向：**每个恢复到的键都有属性**。
**而反方向没人查 —— 那里才是 1:1 违规能藏的地方：一个复刻件写出去、原版从不写的键。**

### 限定到 `GlobalSettings` 类体：48 属性 vs 44 键

**差 4 个：`EnableClock` · `ClockFormat` · `MonitorConcurrency` · `StoreGroups`。**

### 而每一个的答案都不同

| 属性 | 结论 | 依据 |
|---|---|---|
| **`EnableClock`** | **原版的，只是备份早于它** | **R198 注记指向 locale 的 `Settings.General.EnableClock`（带 tooltip）** |
| `ClockFormat` | 不在绑定契约里 | 契约没有这个名字 |
| `StoreGroups` | 不在绑定契约里 | 同上 |
| **`MonitorConcurrency`** | **仍然开着的问题** | **契约**有**它，而 `concurrency` 键已被嵌套的 `ConcurrencySettings` 占掉** |

### 所以「差 4 个」不是「4 个 bug」

**而 `EnableClock` 那一条最有价值：它证明**备份早于属性**这件事是真的可能**，不是我为差异找的借口。**

> **判据：一条 locale 键带 tooltip。那是原版自己的字符串，不是我的推断。
> 所以这个属性在原版里，而 44 键备份里没有它 —— **两份证据都真，只是来自不同版本**。**

### 而 `MonitorConcurrency` 是这一轮唯一没有答案的那一个

**契约说 `Settings` 有它（`int`），备份说 `concurrency` 是个对象（`ConcurrencySettings`，契约里 `Models.Concurrency` 的映射）。
**两个都对，而它们不能是同一个成员。**

**所以钉住这个矛盾本身**，让问题不会消失：
**一个测例断言 `MonitorConcurrency` 是 `int`、`Concurrency` 不是、且两者序列化名不同。**
**这样某天有人「顺手统一」它们时，会先红。**

### 新增 4 个测例

| 测例 | 守什么 |
|---|---|
| `TheUnmatchedMembersAreTheExpectedFourAndEachHasAReason` | 恰好这 4 个，顺序无关但集合固定 |
| `EnableClockIsOriginalDespiteHavingNoKey` | 有 locale 键为证 |
| `ClockFormatAndStoreGroupsAreNotInTheContract` | 不在契约里 |
| `MonitorConcurrencyIsAContractMemberWithNoKeyAndConcurrencyIsObject` | **矛盾本身** |

### 数字

| 度量 | R927 | **R928** |
|---|---|---|
| 套件 | 1911 | **1915** |
| 设置属性 / 恢复键 | 48 / 44（未解释） | **48 / 44，4 个每个有理由** |
| 类型缺失 | 16 | 16 |

### 教训

> **一个度量报「48 对 44」，而它不告诉你是 4 个缺失还是 4 个多余 —— 这两个是完全不同的问题，
> 一个要补，一个要删。**
> **而这四个里三个是「多余但合法」，一个是「两边都对而互相冲突」。
> 四种情况，一个数字。**


### `MonitorConcurrency` 定了 —— 而复刻件是**错的**（R929）

**R928 把 `MonitorConcurrency` 钉成「契约有、键被占」的矛盾。这一轮问二进制，答案对复刻件不利。**

### 三组证据，指向同一件事

**① locale 把 `Maximum` / `Ratio` / `Both` / `Max` 挂在 `MonitorConcurrency` 底下：**

```
"Settings.General.MonitorConcurrency": "Monitor Concurrency"
"Settings.General.MonitorConcurrency.Tooltip": "Configures the amount of monitoring tasks when using the \"Shared Monitor\" monitor mode."
"Settings.General.MonitorConcurrency.Maximum": "Maximum:"
"Settings.General.MonitorConcurrency.Ratio": "Ratio:"
"Settings.General.MonitorConcurrency.Both": "Both:"
"Settings.General.MonitorConcurrency.Max": "max"
```

**② 绑定描述符同时列了这两个：**

```
Cybersole.Global.Settings,Cybersole.Core.MonitorConcurrency!Getter
Cybersole.Models.Concurrency,Cybersole.Core.Maximum!Getter
```

**③ 而 `<MonitorConcurrency>k__BackingField` 与 `set_Clock,get_MonitorConcurrency@` 说明它是一个**字段支撑的属性**。**

### 所以

> **`MonitorConcurrency` **就是**那个 `Models.Concurrency` 对象本身（有 Maximum / Ratio / Mode），
> 不是它旁边的一个 `int`。**

**而复刻件有两个：`ConcurrencySettings Concurrency` + **凭空造的 `int MonitorConcurrency = 10`**。**

**那个 `int` 是我的发明 —— 而它看起来完全合理，因为「并发数」听起来就是个数字。**

### 合成一个

```csharp
[JsonProperty("concurrency")]
public ConcurrencySettings MonitorConcurrency { get; set; } = new();
```

**一个属性，名字取绑定那边的，键取文件那边的 —— 与 R927 的 `StartupPage` 同一手法。**

### 而改的时候我第二次犯了同一个错

**第一次我用正则把所有 `.Concurrency` 改成 `.MonitorConcurrency` —— **17 处**。
构建报错：`ProviderViews.cs` 里 `c.Concurrency` / `picked.Concurrency` 是 **`CaptchaProvider` 自己的 `Concurrency`**
（描述符表里就有 `CaptchaProviders.CaptchaProvider,Cybersole.Core.Concurrency!Getter`）。**

**回滚，改成按**接收者**限定：`settings.` 与 `s.` 两个，共 **8 处**。**

> **R927 的教训我写过：「改名前要问还有谁在用这个名字」。
> 而这一轮我改的是**后缀**，不是名字 —— 于是同一个词在两个类型上，正则分不出来。
> **「谁是接收者」比「名字长什么样」更能定住一处引用。****

### 而我自己 R928 的两个测例因此红了

**它们编码的是**旧事实**（`MonitorConcurrency` 是 int、`Concurrency` 是对象）。
改成合并后的真相：`MonitorConcurrency` 是对象、序列化名 `concurrency`、**没有 int 兄弟**、且其类型上有 `Maximum` / `Ratio`。**

### 数字

| 度量 | R928 | **R929** |
|---|---|---|
| 套件 | 1915 | **1915** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |
| **设置不匹配成员** | 4 | **3**（`MonitorConcurrency` 有键了） |

**套件与形状三个数都没动 —— 因为这一轮修的是一个**成员的类型与名字**，
而那两个度量数的是**类型存在性**与**成员集合**，不是成员类型。**

> **所以「没动」不说明「没改」：这一轮把一个 `int` 换成了一个对象，而 1915 / 16 / 94 三个数一个都没变。**


### `ConcurrencyMode` 的第三个值是**发明的**，而 `Both` 有一条成文的规则（R930）

**R929 留下「`ConcurrencyMode` 的三个值未核」。核了。**

### 二进制里只有类型名一个字符串

```
ConcurrencyMode    (0x1432312cd)   ← 就这一个
```

**枚举**成员名没单独出现**。所以值只能从 locale 推 —— 而 locale 给了三项：**

```
"Settings.General.MonitorConcurrency.Maximum": "Maximum:"
"Settings.General.MonitorConcurrency.Ratio": "Ratio:"
"Settings.General.MonitorConcurrency.Both": "Both:"
"Settings.General.MonitorConcurrency.Max": "max"
```

**而 `BothDesc` 把规则写下来了：**

> **「Allows you to set both a maximum and ratio. The amount of monitoring tasks will be equal to **whichever is greater**.」**

### 而复刻件是 `Unlimited / Maximum / Ratio`

**第三项写成 `Unlimited` —— 而 `Concurrency.Unlimited` 在镜像里 **0 匹配**。
5 个 `Unlimited` 全是无关的（TTS 引擎的 `UnlimitedStorage`、一个叫 Games Unlimited 的店）。**

> **所以 `Unlimited` 也是我的发明 —— 第二个。而它比 R929 那个 `int` 更隐蔽：
> 「不限并发」是一个听起来很自然的能力，而三项里空出一项时，填一个“无限制”比填一个“两个都算”容易想到。**

### 改成 `Maximum / Ratio / Both`，并把那条规则实现出来

```csharp
public enum ConcurrencyMode { Maximum = 0, Ratio = 1, Both = 2 }
```

**`Models/ConcurrencyLimit.cs`：**

| 模式 | 规则 | 依据 |
|---|---|---|
| `Maximum` | `min(max, tasks)`；`max <= 0` 时等于全部 | 名字 |
| `Ratio` | `floor(tasks × ratio)` | 名字 |
| **`Both`** | **`max(maximum, floor(tasks × ratio))`，再 `min(tasks, …)`** | **locale 的 `BothDesc` 原文「whichever is greater」** |

### 三个刻意的决定

**① `max <= 0` 当作「没有上限」，不当「零个任务」。**
**一个什么都没设的 settings 文件应该表现为不限，而不是一个都不跑。**

**② `Ratio` 向下取整，且标注为 Inference。**
**没有任何恢复到的材料说小数怎么处理；向下取整因为**多启动监控池是要防的失败** —— 这个模式存在的目的是限制并发，不是达到目标。**

**③ 一个函数，三个调用方。**
**任务引擎的门、设置预览、测试都要这个数，而这么小的规则正是那种会被各写一遍、各差一点的东西。**

### 数字

| 度量 | R929 | **R930** |
|---|---|---|
| 套件 | 1915 | **1928** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |

### 教训

> **两轮之内我发明了两样东西：一个 `int MonitorConcurrency`（R929）和一个 `Unlimited` 枚举值（R930）。
> 两个都被「听起来合理」保护着。**
> **而两次的判据是同一个动作：**去镜像里搜那个词**。一次搜出 `<MonitorConcurrency>k__BackingField`，
> 一次搜出 0 匹配。**
> **发明不需要证据，而**搜索只要一分钟**。**


### `StartupPage` 没有成员字符串 —— 所以证据是**导航**，而有一个名字对不上（R931）

**R930 说下一轮用同法核 `StartupPage`。查了，而这次方法**不够用**。**

### 二进制只给了这些

```
Cybersole.Global.Settings,Cybersole.Core.StartupPage!Getter / !Setter / !Property
<StartupPage>k__BackingField
get_StartupPage / set_StartupPage
"Settings.General.StartupPage": "Startup Page"
"Settings.General.StartupPage.Tooltip": "Which page to show on startup."
```

**类型名、绑定、backing field、locale 键 —— **没有一个是成员名**。**

> **所以 R930 那个方法（去镜像里搜那个词）在这里只能证明「`StartupPage` 存在」，
> 不能证明「它的六个值叫什么」。方法有边界，而这是它的边界。**

### 但 locale 给了**导航** —— 而导航正好六项

```
Nav.Home · Nav.Tasks · Nav.Proxies · Nav.Billing · Nav.Accounts · Nav.Settings
```

### 而复刻件是 `Home, Tasks, Accounts, Proxies, Analytics, Settings`

**六项对六项，五个字母都不差。第五个：导航说 `Billing`，枚举说 `Analytics`。**

### 而这一个我没有改

**因为证据只说「导航提供哪六个页面」，不说「启动选项存的是哪个值」。
而 `AnalyticsView` 在资源索引里存在 —— **两个界面都是真的**。**

> **所以可能是：`StartupPage.Billing` 是打开 Analytics 的那个键；
> 也可能是复刻件的 `Analytics` 就是 `Billing` 的改名。**
> **而这两种在字符串层面**完全不可分**。**

**所以我钉住差异，不选一个。（R772 的教训：两种表面并存时，按一种改会被另一种否掉。）**

### 新增 4 个测例

| 测例 | 守什么 |
|---|---|
| `TheEnumHasSixValues` | 六对六 |
| `FiveNamesMatchTheNavigation` | **列名而非计数** —— 把 A 改名成 B 时总数仍会是 5 |
| `TheFifthNameDisagreesAndThatIsRecorded` | **差异本身** |
| `HomeIsTheZeroValue` | 两个来源都同意的那一个 |

### 数字

| 度量 | R930 | **R931** |
|---|---|---|
| 套件 | 1928 | **1932** |
| 类型缺失 | 16 | 16 |

### 教训

> **上一轮的方法这一轮用不了，而**它用了才发现**。
> 如果我先假设「同法可核」，我会把「搜不到成员名」读成「枚举只有一个值」或者「枚举没有值」——
> **那正是 §2.7b 说的：反向结论不能从抽样里得。**
> **而这一轮的出路是换证据源，不是换判据：从**类型名**换到**导航**。**


### 函数比例 61.96% 是**旧产物**算的 —— 差 59 个文件、23,815 行（R932）

**这一轮去查判据 (c)：产物级对照可复算。工具在（`func_count.py`），产物也在
（`.publish-aot/Cybersole.Ui.exe`，54 MB）。而查第三件时发现了问题。**

### 产物时间是 2026-11-16 11:49

**而 `src` 下有 **59 个 `.cs` 文件**比它新，合计 **23,815 行**。**

**其中最近的几个就是这几轮写的：`ConcurrencyLimit.cs`（R930）· `Profiles.cs` / `Enums.cs`（R930 的改名）·
外加 R920–R929 那六家 vendor 集成。**

> **所以 171,690 与 61.96% 描述的是**一天多以前的那一版**。
> 而这个数是目标第一条（函数数量对等）的度量 ——
> **它一直是对的，只是它在说另一份代码。****

### 为什么这不是「数字错了」

**171,690 对那一版产物是准确的。错的是**引用方式**：把它当成当前值。
**而 §2.6 那句「没跑成 ≠ 通过」是同一类问题的另一个形状 ——
这里是「算得对 ≠ 算的是现在」。****

### 所以加了一个度量，而不是改一个数

**`tools/artifact_freshness.py`：比 `.publish-aot` 的 mtime 与 `src` 下最新 `.cs`，报「几个文件更新、共几行」。**

**而它接进了 `METRICS.md`：**

```
| 函数数量（.pdata）              | 277,120 / 171,690 / 61.96% |
| 产物陈旧度（.publish-aot vs src） | 59 个文件更新 / 23,815 行   |
```

> **两行挨着，所以引用比例的人**必然看到它是不是当前的**。
> 这比在任何文档里写一句「注意产物可能过期」有用 —— 那句话会被漏读，而表格不会。**

### 而它只比时间戳，这是刻意的

**一次注释编辑会让产物显得陈旧，而输出一点没变。
**这个方向的误报是**正确**的：一次误报的代价是重发布一次，一次漏报的代价是一个关于已不存在代码的数字。**

### 而这一轮**没有**重新发布

**发布前查内存：1.87 GB，`build-server shutdown` 之后 1.92 GB —— 都低于 2 GB 那条线。
按纪律不发布，只把陈旧度记下来。**

**所以下一轮的第一件事是：内存够 2 GB 时 `dotnet publish -p:PublishAot=true`，
然后重跑 `func_count.py`，看 171,690 变成多少。**

### 数字

| 度量 | R931 | **R932** |
|---|---|---|
| 套件 | 1932 | **1932** |
| 函数比例 | 61.96%（未标注陈旧） | **61.96%（同一行旁有 59 / 23,815）** |
| **METRICS.md 行数** | 27 | **29** |

### 教训

> **判据 (c) 我读了很多遍「产物级对照可复算」，而它有三个条件：产物在、工具在、**对照的是现在**。
> 前两个我查了，第三个我没有 —— 因为前两个成立的时候，第三个看起来会自动成立。**
> **而「自动成立」是这个项目里最贵的一句话。**


### 重发布：**+1,963** 个函数，61.96% → **62.66%**（R933）

**R932 说下一轮内存够就重发布。这一轮 2.16 GB，够，发布了。**

```
dotnet publish -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new
→ exit 0 · 54,652 KB（旧 54,052 KB）· 只有 Jint / DataTable 的 trim 警告
```

### 而 R932 那个度量立刻给出结论

| 度量 | 旧产物 | **新产物** |
|---|---|---|
| 复刻件函数 | 171,690 | **173,653** |
| **比例** | 61.96% | **62.66%** |
| 产物陈旧度 | **59 文件 / 23,815 行** | **0 文件 / 状态 current** |

> **59 个文件、23,815 行换来 **+1,963** 个函数（+0.70 pp）。
> 也就是约**每 12 行代码一个函数** —— 而这个比值本身是个有用的刻度：
> 它说这个项目的代码密度，也说「再涨 1 pp 需要写多少」。**

### 而 1,963 这个数分得清

**R920–R929 六家 vendor 集成 + R926 `KeyGesture` + R930 `ConcurrencyLimit` + R930 的枚举与属性合并 ——
这些是**新函数**。而 +1,963 里有多少是它们、多少是 AOT 把之前内联的边界重新展开，**分不开**。**

> **所以这个数只能说「这一版比上一版多 1,963 个非叶函数」，
> 不能说「我写了 1,963 个函数」。—— 后者会是 R918 那种「净数藏住反向移动」再犯一次。**

### 距离目标还剩多少

| | 数 |
|---|---|
| 原版 | 277,120 |
| 复刻件 | 173,653 |
| **差** | **103,467** |
| 按 12 行/函数估算 | **≈124 万行** |

**这个估算必须标明是估算：12 行/函数是从一个 59 文件的样本得出的，而不同代码类型密度差很多。**

### 数字

| 度量 | R932 | **R933** |
|---|---|---|
| 套件 | 1932 | 1932（待跑） |
| **函数比例** | 61.96% | **62.66%** |
| **产物陈旧度** | 59 / 23,815 | **0 / current** |

### 教训

> **R932 加那个度量的价值，这一轮兑现了：它不只是「提醒可能过期」，
> 它是**一个可以关掉的红灯**。**
> **而关掉它的方式只有一条：重发布。**
> **一个度量如果不能被关掉，它就只是一句抱怨。**


### 而这一轮我自己制造并修掉了一个问题

**把 .publish-aot 改名成 .publish-aot-prev 之后，它就不在 .gitignore 的规则里了
（规则写的是 
eplica/.publish-aot/**）。于是 **110 MB 二进制 + 17,702 行 IDAHook.log 进了提交**。**

**修：**
1. .gitignore 加 .publish-aot-prev/ 与 .publish-aot-new/
2. git rm -r --cached —— **从索引移除，磁盘保留**（那是用来对照的旧产物，该留）
3. 单独一个提交做这件事

**结果：git ls-files 里二进制 **0 个**。**

### 而它没有完全消失

**.git 现在是 **168 MB**，因为那次提交已经进了历史。
**改历史是破坏性的，不值得为一个自己造的、已被后续提交纠正的失误做 ——
但必须写明它还在。**

### 全量套件

`
完整套件       exit 0  1932 通过 / 0 失败 / 0 跳过
函数数量       277,120 / 173,653 / 62.66%
产物陈旧度     0 文件 / current
`

### 教训

> **.gitignore 的规则是**按路径**写的，而改名会改变路径 ——
> 所以「把它挪到旁边留着」这个动作，会让它从被忽略变成被跟踪。**
> **而这个项目里所有 .gitignore 规则都是这样：它们守的是名字，不是内容。**


### Next.js：一条**选择器** + 一条**正则**（R934）

**回到优先级 ①。R909 的 `AddToCart` 五个平台缺口里 `Box` 已做，这一轮做 Next。**

**而 Next 和 Astro / Svelte 不一样 —— 后面两个镜像里只有**框架名**，而 Next 有四条具体字面量：**

```
"script#__NEXT_DATA__"
"/_next/static/chunks/app/[^\"']*?page-[0-9a-f]+\\.js"
"/_next/"
"/pay/_next/"
```

### 这两条合起来就是机制

**① `script#__NEXT_DATA__` —— Next 页面把自己的数据放在这个 id 的 script 里，JSON。**
**② 那条正则找的是 app-router 的页面 chunk：`page-<hash>.js`。**

> **而第二条为什么必须用正则而不是拼路径：**build hash 是每次部署变的**，拼不出来，只能从页面读。
> 镜像里给的是一条**匹配**，不是一条**模板** —— 这本身就是证据：原版也是读出来的。**

### 三个刻意的决定

**① 按 id 找，不按「第几个 script」。**
**页面的 script 顺序镜像没说任何事，按位置找会在任何一次页面调整时静默失效。**

**② 「在哪找到的」要报出来。**

| 返回 | 含义 |
|---|---|
| `PageProps` | `props.pageProps` 下 —— **Next 惯例路径** |
| `Elsewhere` | 文档别处 —— **找到了，但不是靠结构** |
| `Absent` | 没有 |

> **因为「按惯例找到」和「搜到了」是两种不同的证据强度。
> 把它们合成一个「找到了」，会让调用方以为结构被确认了，而实际只是搜索成功。**

**③ app-router 与 pages-router 分开。**
**正则是 `chunks/app/`，所以 `chunks/pages/index-abc123.js` **不该**匹配 ——
把两个 router 当一个会拼出镜像不用的路径。有测例钉住这条。**

### 而测试抓到一个 HTML 细节

**`<script id=__NEXT_DATA__>` —— **无引号是合法 HTML**，而我的正则要求引号，于是它被拒。**

**修：值匹配接受有引号与无引号两种。**
**而这条测例是特意写的 —— 因为压缩器会产出无引号属性，而「压缩器会做的事」正是这类解析器要能吃的输入。**

### 数字

| 度量 | R933 | **R934** |
|---|---|---|
| 套件 | 1932 | **1946** |
| 产物陈旧度 | 0 / current | **1 文件 / 142 行**（新文件，正确） |
| `AddToCart` 平台缺口 | Box 已做，4 剩 | **Box + Next 已做，3 剩**（Frontend / Astro / Svelte） |

**而陈旧度那一行现在自己证明了它的用途：这一轮加了一个文件，它就报 1 —— 不需要谁记得去查。**

### 教训

> **同一个「平台缺口」，三个平台的证据量差一个数量级：
> Astro 只有框架名（40 条但都是名字），Svelte 只有名字，而 Next 有一条选择器和一条正则。**
> **所以「做完 Astro / Svelte / Frontend」不会是同一件事做三遍 —— 而先做 Next 是对的，
> 因为它是唯一能核**形状**的那个。**


### Astro **不是名字，是一整套并行代码路径** —— 而我的第一个假设是错的（R935）

**R934 说 Astro 40 条命中「先看里面有没有非名字的字面量」。看了，而它比名字多得多。**

### 方法族

```
ScrapeProductAstro · ScrapeVariantAvailabilityAstro · CheckPriceLimitAstro
AddToCartAstro · StartCheckoutAstro · ParseAstroProduct · ParseAstroImage
AstroAttribute · AstroProp · AstroProps
```

> **七个方法 + 三个名字，覆盖抓商品 / 查变体库存 / 查限价 / 加车 / 开始结账 / 解析商品 / 解析图片。
> 所以 Astro 在镜像里是一条**并行路径**，不是通用路径里的一个分支。**
> **而 `AddToCartAstro` 正是那五个平台缺口之一 —— 它不是一个开关，是七分之一。**

### 而我的第一个假设是**错的**

**Astro 最出名的机制是 island：`<astro-island props="{…}">`，我猜原版读的是那个 props 属性。**

**查了：**

```
astro-island     n=0
component-url    n=0
props=           n=0
```

**三条全空。所以原版读的不是 island 机制。**

### 而把假设排除掉之后，唯一那条字面量就浮出来了

```
data-astro-cid
```

**那是 Astro 给**每个渲染出的元素**打的属性（`data-astro-cid-XXXX`，后缀每次构建变），用来 scope 它的样式。**

> **这就是为什么方法族里有一个 `AstroAttribute` 夹在 `AstroProp` / `AstroProps` 之间 ——
> 它讲的是**从哪个属性认出这些元素**，而不是从哪个 JSON 里读字段。**

### 三个刻意的决定

**① 后缀不能硬编码。**与 Next 的 build hash 同理 —— 按**前缀**匹配。
**② 只暴露「匹配」与「列举」，不声称知道哪个元素是商品。**
**因为镜像给了前缀和方法名，两者对得上，但没有一段恢复到的代码显示有人用它拼过选择器。**
**③ 「没有 cid 属性」≠「不是 Astro 页面」。**
**scoped style 可以被剥掉，所以这是个**弱**结论，而代码只下这个弱结论（有测例钉住这句注释在）。**

### 而测试抓到我一个断言写错了

**`Assert.All(family, name => Assert.EndsWith("Astro", name))` ——
而 `ParseAstroProduct` / `ParseAstroImage` 的 Astro 在**中间**。
改成 `Contains`。**后缀形式只对动作类成立，因为它们是按步骤命名的。****

### 数字

| 度量 | R934 | **R935** |
|---|---|---|
| 套件 | 1946 | **1955** |
| 产物陈旧度 | 1 文件 / 142 行 | **2 文件 / 246 行**（正确累积） |
| `AddToCart` 平台缺口 | 3 剩 | **2 剩**（Frontend / Svelte —— 而 Astro 的机制已建） |

### 教训

> **假设先排除，比假设先实现便宜。**
> **我猜 island，查三条字面量、全 0、花了一次调用 —— 而如果我先写一个 island 解析器，
> 那会是一个**看起来能跑、而原版从不走**的路径。**
> **排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。**


### SvelteKit：五条字面量给出了**调用**，不只是框架名（R936）

**第三个 AddToCart 平台缺口。而它比 Astro 更清楚 —— Astro 给了一个属性前缀，Svelte 给了调用。**

```
SvelteKitData
/__data.json?x-sveltekit-invalidated=001
__sveltekit
x-sveltekit-pathname
x-sveltekit-search
```

### 这五条把机制说全了

**① 数据在**路由自己的路径 + `/__data.json`**。**
**② 路由与它的查询在**两个请求头**里，不在 URL 里。**
**③ `invalidated` 计数器说客户端已经拿到第几代数据。**

> **而 ③ 解释了为什么那条字面量带 `=001` 而不是一个裸参数：**它是个值**，
> 而带着错的值会拿到过期数据或被重发。**

### 而为什么有那两个头

**一条 SvelteKit 路由可以在任何路径上，而数据端点是**相对发起它的页面**的。
把路由放进头而不是放进 URL，意味着**一个端点服务所有路由**，由服务端根据头决定渲染什么。**

> **所以缺了头的请求**无法被正确回答** —— 这就是这里两个都是必需而不是可选的原因。**

### 三个刻意的决定

**① 路由前缀端点，且尾部斜杠去掉** —— 不制造双斜杠（服务端可能当成另一条路由）
**② 两个头**总是**都发** —— 只发一个描述的是「服务端看不见那条查询」的路由，正是这两个头要防的情况
**③ `invalidated` 是参数不是常量** —— 镜像给的值当默认，但**没有任何材料说它怎么递增**，所以这里不假装会算它

### 而测试抓到一个边界

**`__sveltekitz` 撞上了裸前缀 `__sveltekit` —— 它是个**不同的 cookie**，只是字母开头相同。
修：前缀后面必须是 `-` / `.` / `_` 或名字就此结束。**

### 三个平台的证据量，现在可以排出来了

| 平台 | 证据 | 能核什么 |
|---|---|---|
| **Next** | 选择器 + 正则 + 2 资源根 | **形状**（元素、chunk 路径） |
| **Svelte** | 端点 + 2 头 + cookie 前缀 + 类型名 | **调用形状**（URL、头、计数器） |
| **Astro** | 1 属性前缀 + 7 方法名 | **只能核属性家族** |
| Frontend | 未查 | ? |

> **而三个都做完了 `AddToCart` 的平台缺口从 5 降到 1。**
> **而它们的证据量差三个数量级 —— 所以「做完三个平台」用了三轮，而三轮里做的事完全不同。**

### 数字

| 度量 | R935 | **R936** |
|---|---|---|
| 套件 | 1955 | **1969** |
| 产物陈旧度 | 2 文件 / 246 行 | **3 文件 / 371 行** |
| `AddToCart` 平台缺口 | 2 剩 | **1 剩**（Frontend） |

### 教训

> **这一轮我第一版 `IsNonceCookie` 是 `StartsWith("__sveltekit")` ——
> 而前缀匹配**总是**会接受一个只是开头相同的名字。**
> **测试写了一个 `__sveltekitz` 就是为了抓它，而它抓到了。
> 前缀匹配要配边界，这条和 R926 那个「大小写滑动」是同一类：**匹配宽松一格，就多接受一个错东西**。**


### `Frontend` **不是第四个框架** —— 它是那条通用的（R937）

**五个平台缺口里的最后一个。查了，而它根本不是一个平台。**

```
_frontendDomain · _frontendUrl · _frontendSearch · FrontendUri · get_FrontendUri · IsFrontendUrl
ScrapeJsonFrontend · ScrapePageFrontend · ScrapeProductFrontend
ScrapeVariantAvailabilityFrontend · FindProductFrontend · AddToCartFrontend
```

### 两条线索指向同一件事

**① 每个方法都是某个框架专用方法的**通用对应物**：**
`ScrapeProductFrontend` 挨着 `ScrapeProductSvelte` · `AddToCartFrontend` 挨着 `AddToCartAstro`。

**② 而三个字段是 **URI 的组成部分**：domain / url / search。**

> **所以 frontend 路径是那条**兜底**：读站点实际发出来的东西；
> 而那四个框架是**它知道该用哪个之后**去调用的解析器。**

### 所以「五个平台缺口」这个说法本身一直是错的

**它不是五个平台并列。它是**一个通用路径 + 四个具体解析器** ——
`Box` 是第一个做的，而它当时被当成五个中的一个。**

> **而 `AddToCartFrontend` 是那个通用入口，四个具体的都挂在它下面。
> 所以真正的结构是**一棵**，不是一列。**
> **而「还差一个平台」这个待办项，是因为我把它读成了一列才出现的。**

### `IsFrontendUrl` 是那个铰链

**一个店同时有 API 和页面，而两者是**故意不同的 URL** ——
所以流程必须先判断手里是哪一个，才能决定怎么读。**

**而它的默认方向是**刻意的**：**

> **不像 API 的 URL 一律当页面。
> 因为把页面当 JSON 读会**响亮地失败**，而把页面当 API 调会返回一个 HTML 错误体 ——
> **那个体解析出来什么都不是，看起来像一个空商品。****

### 三个决定

**① 查 API 标记时**忽略查询串** —— 一个页面可以带任意查询，标记落在查询里就是假阳性。**
**② `Describe` 只返回镜像点名的三个部分** —— 调用方无法凭空造第四个。
**③ 相对路径没有 domain，就说没有** —— 而不是从上下文编一个。**

### 而 API 标记列表标了 Inference

**镜像给了 `IsFrontendUrl` 这个名字，没说它测什么.
所以那十个标记是「店面的 API 在实践里长什么样」，不是恢复到的。
**而它们被写得短而显式，是为了一个错的标记能被看见。****

### 数字

| 度量 | R936 | **R937** |
|---|---|---|
| 套件 | 1969 | **1981** |
| 产物陈旧度 | 3 文件 / 371 行 | **4 文件 / 492 行** |
| **`AddToCart` 平台缺口** | 1 剩 | **0** |

### 教训

> **一个待办清单的形状决定了它能被关掉多少。**
> **我把五个名字读成一列并列的平台，于是它们是五个待办；
> 而其中一个是**伞**，于是真实结构是一棵树，而待办是「把这棵树建起来」这一件事。**
> **形状读错的时候，进度看起来像线性减少，而实际上从来没有接近过。**


### `Box` 也不是平台 —— 而这份清单**两个方向都错了**（R938）

**R937 说 Frontend 是伞，不是第四个框架。这一轮查 Box 在树里的位置，而它同样不是一个框架 —— 理由不同。**

### 决定性的六条相邻 state machine

```
<PollRestockMulti>d__81 · <ExtractPopNow>d__83 · <SelectPopNow>d__84
<SelectMultiPopNow>d__85 · <AddToCartBox>d__86 · <SelectMultiPopNowUS>d__87
```

**六个**连号**的 state machine —— 说明它们是**一个类的六个方法**，而它们的邻居是 PopMart 的：
轮询补货 → 抽 pop-now → 选一个 → 选多个 → 美区选多个 → **加盒到车**。**

> **所以 `Box` 是 PopMart 抽签流程里的**一步**，不是前端框架。**

### 而一个测试就把它分开了

**每个框架都有一个商品抓取器：`ScrapeProductNext` · `ScrapeProductAstro` · `ScrapeProductSvelte` · `ScrapeProductFrontend`。
而 `ScrapeProductBox` **0 匹配**。**

> **所以那条判据不是「名字长什么样」，是「有没有配套的商品抓取器」。
> 而 `Box` 没有 —— 它抓的不是商品，是一次抽签的名额。**

### 所以那份清单**两个方向都错了**

| 名字 | 我当时以为 | 实际 |
|---|---|---|
| `Frontend` | 第四个框架 | **伞**（通用路径） |
| `Box` | 第五个框架 | **PopMart 的一步** |

**两个错误同一个来源：把一张平的名字列表读成「彼此并列的」，而没有问**每个名字旁边是谁**。**

### 而三个更早的名字可以结了

**`BoxGoodsList` · `BoxExtract` · `BoxSku` —— R909 把它们记成「没有调用者，刻意不强行」。
查了：**三条全部 0 匹配**。**

> **所以它们从来不在镜像里 —— 是更早读 box 代码时**编出来的**，现在撤回。**
> **而 R909 那条「没有调用者」的记录，其实在说「我找不到调用者」，而不是「原版没有调用」。
> 两者的区别是：前者是未知，后者是缺席。而这一轮才把未知变成缺席。****

### 数字

| 度量 | R937 | **R938** |
|---|---|---|
| 套件 | 1981 | **1990** |
| 产物陈旧度 | 4 文件 / 492 行 | **5 文件 / 561 行** |
| 平台缺口 | 0（已是 4 个框架） | **0，而清单从 5 修正为 4** |
| 撤回的发明名字 | — | **3**（BoxGoodsList / BoxExtract / BoxSku） |

### 教训

> **两轮之内，五个名字里有两个被证明不是我以为的东西 —— 而两个都是「听起来像」的错。**
> **`Frontend` 听起来像一个框架，`Box` 听起来像一个框架；
> 而一个名字听起来像什么，和它**旁边是谁**，是两件不同的事。**
> **而「旁边是谁」有证据（连号的 state machine），「听起来像什么」没有。**


### `AddToCart` 是**十三个名字、四条轴**，而扫描只浮出九个（R939）

**R938 说「是否还有别的听起来像框架的名字 —— 未扫」。扫了，而扫描本身先错了一次。**

### 扫出九个，而它漏了四个

```
AddToCart · AddToCartApp · AddToCartAppDw · AddToCartBox · AddToCartDummy
AddToCartGraphQL · AddToCartMulti · AddToCartPreload · AddToCartPreloadGraphQL
```

**而直接查四个框架名，全都在：**

```
AddToCartNext 5 · AddToCartAstro 6 · AddToCartSvelte 5 · AddToCartFrontend 5
```

> **所以那次扫描**漏掉了全部四个框架名**。原因是 `n=40` —— 而 40 是**工具的上限**，不是镜像的数量。
> §2.7b 那条「先问这个来源是全量还是抽样」，我在用它的时候又忘了。**
> **而 `--cursor` 那条路也没通：翻 8 页仍是那 18 个 —— 所以「翻页」这个补救办法本身也不成立。
> 唯一可靠的是**直接查名字**。**

### 所以至少十三个

**而它们不并列 —— 有四条正交的轴：**

| 轴 | 值 |
|---|---|
| **transport** | plain（REST）· GraphQL |
| **client** | web · App · AppDw |
| **purpose** | plain · Preload · Multi · Dummy |
| **parser** | Next · Astro · Svelte · Frontend |

**而 `AddToCartPreloadGraphQL` 是 transport × purpose；`AddToCartAppDw` 是 client × 平台。**

> **一张十三项的列表**藏起这个结构** —— 而「列表」也正是两个名字被误分类的原因。**

### 而轴能解释名字，**不能生成名字**

**`AddToCartAppGraphQL` 由两个真实轴值组成 —— 而它**不在恢复到的十三个里**。**

> **所以 `Recovered` 是权威，轴只是对它的解释。
> 从轴生成第十四个名字，会是这几轮一直在找的那种**发明** —— 只不过这次发明的是「一个组合」。**

**而 `AddToCartBox` 是镜像自己给的**反例**：它在家族里，却不由任何轴组合而成 ——
**它是 PopMart 的一步。****

### 数字

| 度量 | R938 | **R939** |
|---|---|---|
| 套件 | 1990 | **2001** |
| 产物陈旧度 | 5 文件 / 561 行 | **6 文件 / 666 行** |
| **已记录的 AddToCart 名字** | 5（散落） | **13（有轴）** |

### 教训

> **同一个 §2.7b 我在**用它的时候**又犯了：`n=40` 就在输出里写着，而我读的是「扫出了九个」。
> 而它的补救办法（翻页）也不成立，所以我把「翻页没通」和「扫描不全」叠在了一起，
> 于是倾向于相信那九个是全部。**
> **唯一破掉它的是一个**直接查名字**的动作 —— 而那正是 §2.7b 说反向结论该用的方法。**


### 13/13 按名字，实际是 **8 实现 + 5 只有名字**（R940）

**R939 说下一轮数「13 个里复刻件有几个」。数了 —— 而第一次的答案是错的。**

### 按名字查：13 / 13

**而六个只在 `AddToCartMatrix.cs` 里 —— 那是我上一轮写的**清单**。**

> **那是 R850 那个形状：「有形状没有内容」。一个在表里的名字不是一个方法。**

### 分开之后

| 有实现 | 8 |
|---|---|
| 只有名字 | 5 |

**而五个里四个不是同一种缺口。**

### 四个框架名：**有 surface、没有 step**

| 名字 | surface | step |
|---|---|---|
| `AddToCartNext` | ✅ `NextJsSurface` | **❌** |
| `AddToCartAstro` | ✅ `AstroSurface` | **❌** |
| `AddToCartSvelte` | ✅ `SvelteKitSurface` | **❌** |
| `AddToCartFrontend` | ✅ `FrontendSurface` | **❌** |

### 而这是最容易被读成「做完了」的形状

**一个单一计数会让人把四个 surface 当成四个做完的 step。**

### surface 不蕴含 step 的理由

**surface 回答**怎么读**；step 回答**往哪写**。**

> **读一个 Next 页面是解析 `script#__NEXT_DATA__`；而往它的车里写是调那个**店的** cart 端点 ——
> 而那**按店不同，不按框架不同**。同一个框架上的两家店，cart URL 就不一样。**

**所以四个 surface 不能拼成四个 step，声称能拼就是在**编造端点地址**。**

### 而第五个不一样

**`AddToCartDummy` —— 名字说它根本不和店说话，所以它是五个里**唯一不依赖端点证据**的那个。**

### 数字

| 度量 | R939 | **R940** |
|---|---|---|
| 套件 | 2001 | **2012** |
| 产物陈旧度 | 6 文件 / 666 行 | **7 文件 / 752 行** |
| **按名字** | 13 / 13 | 13 / 13 |
| **✓ 有实现** | 未分 | **8** |
| **只有名字** | 未分 | **5（其中 4 个有 surface）** |

### 教训

> **「13/13」是一个**会让人停止查看**的数字。
> 而它是真的 —— 每个名字都在源码里出现过。**
> **所以「在源码里出现过」这个判据，对「实现了吗」这个问题，是**不够的**。
> 而它不够的方式很安静：它给的是一个满分。**


### `Dummy` 不是 dry run，是**购物车预热**（R941）

**R940 把 `AddToCartDummy` 记成「五个里唯一不依赖端点证据的」，理由是「它的名字说它不和店说话」。
而它的邻居说不是。**

### 四条连号

```
<GetProduct>d__45 · <AddToCartDummy>d__46 · <AddToCartMulti>d__47 · <RemoveDummy>d__48
```

**一个 add 紧跟着它的 remove。**

> **那不是 dry run，也不是 test —— 那是**预热**：
> 一个「首次加车才建车」的店，会把一次往返和一次会话变更花在最糟的时刻。
> 所以提前加一个便宜的占位商品、稍后移除，就让真正的加车**复用一辆已经存在的车**。**
> **而 `Dummy` 说的是**那件商品**是占位，不是**那次调用**是假的。**

### 而它的邻居把这家店也描出来了

```
Login · LoginVerify2FA · EnableTwoFactor · Register
FetchBalance · CheckFanRewardStat · EnterSweepStakesRaffle
```

**余额 · 粉丝奖励统计 · 抽奖 —— 那是一家**有会员体系**的店的表面。
而这也解释了为什么占位商品便宜：那家店有。**

> **而这是 Inference（从名字推的），标注了 —— 它缩小了「这是哪家店」，但没指认它。**

### 所以「唯一不依赖端点证据」这句也错了

**它需要的是**一个占位商品**，不是一个恢复到的 car地址。
而那是**按店不同的数据**，不是按框架不同的代码。**

> **所以它不是「不依赖证据」，而是「依赖另一种证据」。**
> **而 R940 把它记成独立的那个，是因为「dummy」听起来像「空的」——
> 而它实际是「占位的」。词根一样，意思相反。**

### 而这一轮又抓到两处旧断言

**① 我自己的 `DoesNotContain("dry run")` —— 而注释写的是「not a dry run」，当然含那两个词。**
**② R940 那个 `TheDummyPathIsTheIndependentOne` 断言注释含「no endpoint evidence」——
而那正是 R941 纠正掉的说法。**

**两处都改成断言**纠正后**的说法，并改名为 `TheDummyPathIsPrimingNotADryRun`。**

### 数字

| 度量 | R940 | **R941** |
|---|---|---|
| 套件 | 2012 | **2023** |
| 产物陈旧度 | 7 文件 / 752 行 | **8 文件 / 832 行** |
| 三个轮次里被纠正的名字 | 2（Frontend · Box） | **3（+ Dummy）** |

### 教训

> **三轮，三个名字被纠正：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位不是空）。**
> **而三个都是**同一个判据**能抓的：**看它旁边是谁**（连号的 state machine、有没有配套的 ScrapeProduct*、
> 后面是否紧跟一个反操作）。**
> **而三个都靠「名字听起来像什么」骗过了我一次。**
> **所以那条判据不是「别相信名字」，而是**名字只能提出假设，连号才能确认**。**


### 连号判据扫全 13 个：第四个误读是 `AddToCartMulti`（R942）

**R941 说下一轮用连号判据扫是否还有第 4 个。扫了 —— 而扫描本身先错了一次。**

### 第一次扫描给出的是噪声

**我把序号在全镜像范围内比，于是得到：**

```
AddToCart  d__36  邻居: CastIterator, CheckForUpdatesAsync, ExpandBufferAsync, FlushAsyncInternal
```

> **那些不是同一个类的方法。原因是**序号按类编**，`d__36` 在很多类里同时存在。**

### 连号判据只在**同一条描述符字符串内**成立

**一条字符串里，序号逐个 +1 的一段就是一个类的方法表。按这个读，六个名字自己就位了：**

| 名字 | 序号 | 同类邻居 | 类 |
|---|---|---|---|
| `AddToCart` | d__36 | `GetCsrf` · `GetCheckout` · `GetCheckoutHtml` | **网页结账** |
| `AddToCartApp` | d__41 | `StartAppFast` · `StartAppSafe` · `GetSessionDw` · `GetCartDw` | **App 会话** |
| `AddToCartAppDw` | d__42 | 同上 | **App 会话** |
| `AddToCartDummy` | d__46 | `GetProduct` · `AddToCartMulti` · `RemoveDummy` | **PopMart 抽签** |
| **`AddToCartMulti`** | **d__47** | **`GetProduct` · `AddToCartDummy` · `RemoveDummy`** | **PopMart 抽签** |
| `AddToCartPreload` | d__90 | `HandleOutOfStock` | **商品库存** |

### 所以第四个误读是 `AddToCartMulti`

**我一直把它记成「通用多件车」。而它和 `Dummy` / `RemoveDummy` 在同一个类里 —— 它是**PopMart 的「加多个盒」**。**

> **四个名字、四轮：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位）· `Multi`（PopMart 多盒）。
> 而四个里两个是通用的、两个是 PopMart 的 —— 而我最初把它们当成同一种东西。****

### 而七个名字**定不了位**

**`AddToCartBox` · `GraphQL` · `PreloadGraphQL` · `Next` · `Astro` · `Svelte` · `Frontend` 都没出现在连号 run 里。**

> **而那**不是**「它们不存在」的证据 —— 描述符扫描本身就是截断的（R939 的 `n=40`），
> 所以一个名字可能只是**那条字符串没被返回**。**
> **与 R939 同一条纪律：缺席 ≠ 未知。**

### 数字

| 度量 | R941 | **R942** |
|---|---|---|
| 套件 | 2023 | **2036** |
| 产物陈旧度 | 8 文件 / 832 行 | **9 文件 / 916 行** |
| **连号定位** | 0 / 13 | **6 / 13（另 7 未知）** |
| **被纠正的名字** | 3 | **4** |

### 教训

> **同一个判据，用错范围就变成噪声：连号在**类内**有意义，在**全镜像**范围内没有。**
> **而它的表现是**给出一个看起来很像答案的表** —— `AddToCart` 旁边是 `CastIterator`，
> 而那读起来像「它属于框架迭代器类」，一个完全错误但语法通顺的结论。**
> **所以判据用错范围时，它不会报错，它会**给出一个答案**。**


### 13 / 13 全部定位，而**两个来源都不是我想的那个**（R943）

**R942 说 7 个定不了位。这一轮补上了，而过程中两个假设先后被否。**

### 假设一：用描述符表 —— 错的

**`analysis/binding_descriptors.tsv` 有 1,637 条，字段是 `declaring_type / owner_assembly / member / accessor`。**

**而七个名字**一条都不在里面**。**

> **原因不是它们不存在，而是那张表只装**绑定**（带 Getter/Setter 的属性）。
> `AddToCart*` 是**方法**，永远不在里面。**
> **所以那不是「缺席」，是**问错了表**。**

### 假设二：用序号连号 —— 在这七个身上也不可靠

**读它们各自的字符串，序号是这样的：**

```
AddToCartBox        ExtractPopNow(83) · SelectPopNow(840) · AddToCartBox(864) · SelectMultiPopNowUS(87)
AddToCartNext       AddToCartNext(364) · ScrapeProductSvelte(378) · CheckPriceLimitSvelte(39)
```

> **`840` 与 `864` 之间夹着 `85`/`87` —— 序号被**截断成三位**了。所以这些字符串里的序号不可信。**

### 但**邻居名**可信，而它给了七类

| 名字 | 邻居 | 类 |
|---|---|---|
| `AddToCartBox` | `ExtractPopNow` · `SelectPopNow` · `PreviewBoxes` · `FetchAddress` | **PopMart 抽签**（第三次确认） |
| `AddToCartGraphQL` | `GetAccessToken` · `CartApiObjectCreate` | **购物车 API** |
| `AddToCartPreloadGraphQL` | `CreateCartGraphql` · `GetCartAvailabilityGraphql` | **GraphQL 车** |
| `AddToCartNext` | `ScrapeProductSvelte` · `CheckPriceLimitSvelte` | **框架抓取** |
| `AddToCartAstro` | `StartCheckoutAstro` · `ScrapeProductNext` · `CheckPriceLimitNext` | **框架抓取** |
| `AddToCartSvelte` | `RefreshSession` | **会话** |
| `AddToCartFrontend` | `AddToCart` · `AddToCartPreload` | **网页结账** |

### 而 `AddToCartNext` 旁边是 **Svelte** 的名字 —— 那是**拼接伪影**

**它是 `Next`，旁边却是 `ScrapeProductSvelte` / `CheckPriceLimitSvelte`。**

> **所以这些字符串是多个类的连号 run **拼接**在一起的。
> 而邻居名只能说明「这一类里有抓取方法」，**不能说明这两个名字同类**。**
> **所以表里的「类」是**这一段的性质**，不是这两个方法共享的类。而我把这个区别写进了常量注释和测例名。****

### 数字

| 度量 | R942 | **R943** |
|---|---|---|
| 套件 | 2036 | **2036** |
| 产物陈旧度 | 9 文件 / 916 行 | **9 文件 / 920 行** |
| **连号定位** | 6 / 13 | **13 / 13（7 个靠邻居名）** |

### 而套件红过一次 —— 是偶发

**第一次 `metrics_report.py` 报 1 失败；直接跑全量 **2340 通过 / 0 失败 / 2 跳过**；
再跑 metrics **2036 通过 / 0 失败**。**

> **所以那一次是**偶发**，不是真失败。而 §2.6 那条「没跑成 ≠ 通过」的反面也成立：
> **红一次 ≠ 真红** —— 但要说清是重跑才绿的，而不是把那次红抹掉。****

### 教训

> **这一轮两个假设都被否，而两个都是**问错了来源**：
> 描述符表装绑定不装方法；序号在拼接串里被截断。**
> **而两次的错误形式相同：**一个能回答相邻问题的来源，被我当成了能回答这个问题的来源。**
> **而它们的输出都不报错 —— 描述符表给出「不在表里」，序号给出一个看起来正常的数字。**


### 转优先级 ② 第一件事：`_px3` **一直都在**，而那个「没有」被写了三遍（R944）

**十轮做完 ①，转 ②。查五个厂商，四个全在：**

```
Kasada 40 · DataDome 15 · PerimeterX 5 (+ _px 4) · Queue-it 13
```

**而 `AntiBotProtocol.cs` 已经覆盖六家：Kasada · Akamai · DataDome · Cloudflare · Queue-it · TrustDecision。**

### 而它**不含 PerimeterX**，理由写在注释里

> 「PerimeterX is the exception: the image names the vendor and a token, but no `_px` cookie —
> so it is deliberately absent here rather than filled in from memory.」

**那句话写得很好 —— 它甚至防了「凭记忆填」。而它**是错的**：**

```
_px (n=4) → _px3 · _pxHandler · __pxvid · _pxvid
```

### 而同一个假缺席被写了**三遍**

| 位置 | 内容 |
|---|---|
| `AntiBotProtocol.cs` 的类注释 | 「no `_px` cookie」 |
| `VendorWiringTests` | `Assert.Null(CookiesFor("PerimeterX"))` |
| `AntiBotProtocolTests` | `Assert.Null(CookiesFor("PerimeterX"))` |

> **三遍。而这就是它从没被查的原因 —— **一个被重复的断言读起来像被印证的事实。****
> **而三处里有两处是**测例**。测例本来是防这件事的，而它们在这里**保存**了那件事。**
> **一个错被写成断言，就变成了「已验证」；写成三次，就变成了「显然」。**

### 补上了什么

```
_px3              主 cookie
__pxvid · _pxvid  两个访客 id（只差一个下划线，刻意不合并）
PerimeterX-Token  请求头（保留镜像的大小写）
PerimeterXHandler handler 名
"Solving PerimeterX" · "PerimeterX block (Rotating proxy)"   镜像自己的措辞，不解释
```

**而「两个访客 id 不合并」是刻意的：镜像有两种拼法，而没有东西说它们同值。**

### 而 cookie 表是 **5** 家不是 7

**Queue-it 用路由、TrustDecision 用脚本 —— 把它们算进 cookie 表就是断言一个它们没有的 cookie。**
**（我第一版测例写的 7，被自己的断言纠正了。）**

### 数字

| 度量 | R943 | **R944** |
|---|---|---|
| 套件 | 2036 | **2043** |
| 产物陈旧度 | 9 文件 / 920 行 | **10 文件 / 1044 行** |
| **cookie 表覆盖厂商** | 4 | **5（+PerimeterX）** |

### 教训

> **这一轮最值钱的不是补上 PerimeterX，是发现那个「刻意不填」的注释是错的。**
> **它之所以能活十轮，不是因为它隐蔽，而是因为它**被写得很有纪律** ——
> 「deliberately absent rather than filled in from memory」正是我会赞同的那种句子。**
> **而一个听起来像纪律的错误，比一个听起来像错误的错误贵得多。**


### Imperva 的否定是**真的** —— 而这才是 PerimeterX 那件事的用处（R945）

**R944 把 `Assert.Null(CookiesFor("Imperva"))` 标成「未验证」。这一轮跑了那个搜索。**

```
Imperva          0
incap_ses        0
visid_incap      0
nlbi_            0
_Incapsula_      0
```

**四条 Imperva 已知 cookie 前缀全 0 —— 所以那个否定是真的。**

### 而两个否定当时写得**一模一样**

| 断言 | 当时 | 现在 |
|---|---|---|
| `PerimeterX` 没有 `_px` cookie | 「刻意不填」 | **假**（`_px3` 在） |
| `Imperva` 没有 cookie | 同一种句式 | **真**（五条搜索全 0） |

> **所以区别不在**写得多小心**，而在**有没有一条命令产生它**。
> 两句都读起来像事实；一句有命令，一句没有。
> 而没有命令的否定，是一个用事实的语法写出来的猜测。**

### 而 Imperva 在复刻件里只作为**反例**存在

**`VendorWiring.cs` 一句注释 + `VendorWiringTests` 一条断言。`AntiBotVendors.Knows("Imperva")` 是 false ——
所以它不是「被忘掉的厂商」，是「根本不在的厂商」。**

**而这两者的区别，`Assert.Null` 单独看不出来。**

### 所以断言改成带证据的形式

**从「no search was run on it」改成「verified rather than asserted」+ 四条前缀被点名，
让下一个读的人能**重跑**，而不是**相信**。**

### 数字

| 度量 | R944 | **R945** |
|---|---|---|
| 套件 | 2043 | **2048** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044**（未改产品代码） |
| **已带命令的否定** | 0 / 2 | **2 / 2** |

### 教训

> **上一轮修了一个**错的**否定；这一轮把**对的**那个也装上了证据 ——
> 因为一个碰巧为真的猜测，下一次改代码时仍然不可信。**
> **「对」和「可复算」是两件事。而只有后者能在改动之后还成立。**


### 772 条否定断言，而真正需要命令的只有 **8 条**（R946）

**R945 说下一轮扫「其余否定断言有多少没带命令」。扫了，而第一次的数**没有意义**。**

### 第一次扫描：772 里 764 条「没有证据」

**而那个数几乎等于全部 —— 因为它把两类东西算成了一类：**

| 一类 | 例子 | 谁证明它 |
|---|---|---|
| **自证** | `Assert.Null(CookiesFor("NoSuchVendor"))` | **测试自己** —— 函数就在那儿 |
| **需镜像** | 「`NikeEndpoints` 没有 `buy/carts/` 路径」 | **只有二进制** —— 跑代码证不出来 |

> **第一类不是断言，是**算术**。把 772 当成 772 个问题，等于把「2+2=4」当成待办。**

### 窄化到「带具体名字」：118 条

**而 118 里绝大多数仍然是自证**（`Assert.Null(Jwt.Decode("not-a-token"))`、`Assert.Empty(Filter("zzzz"))`）。

### 而真正需要镜像的，是**8 条**

| 断言 | 需要什么 |
|---|---|
| `NikeEndpoints` 无 `buy/carts/` | 搜那个路径 |
| `NikeEndpoints` 无 `buy/orders/` | 搜那个路径 |
| `NikeEndpoints.OrderV5` 不含 `scheels` | 搜 scheels |
| `AntiBotVendors.DataDomeRelay` 不含 `datadome.co` | 搜 relay host |
| `PopMartStepMap` 无 `CheckResult` 端点 | 搜那个端点 |
| `JohnLewisStepMap` 无 `GetStripePaymentIntent` | 搜那个端点 |
| `StoreFlowSteps` 的 shared/single 无 `GetMerchantCode` | 步表自己的序号 |
| 无 `ScrapeProductBox` | **R938 已跑过** |

> **八条里一条已经settled（R938），七条还开着。而按 R944 的比例（3 条里 1 条是假的），
> 那七条里大概**有两条是错的** —— 而每一条现在都长着「事实」的样子。**

### 而 118 → 8 这个过程本身是内容

**三个数：772 · 118 · 8。**
**而在第一和第三个之间，我做的是**分类**，不是筛选。**
**筛选会把 764 当成「不重要」丢掉；分类把它们认成「已经证明」——
**两者对剩下的 8 条做的事一样，而对那 764 条的说法完全相反。****

### 数字

| 度量 | R945 | **R946** |
|---|---|---|
| 套件 | 2048 | **2052** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| **需镜像的否定断言** | 未分 | **8（1 已 settled，7 开）** |

### 教训

> **一个扫描报「764 条没有证据」，而它的意思是「764 条不需要证据」。**
> **同一个数，两种读法，而第一种会让我去补 764 条命令 —— 那是一场没有产出的劳动。**
> **分类不是筛选的礼貌说法；它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。**


### 验那 8 条：4 真 · 3 自证 · **1 根本不存在**（R947）

**R946 说八条里七条开着、按 R944 比例大概两条是错的。验了。**

### 三条**真的**

```
datadome.co   n=33  —— 全是厂商自己的域：api-js.datadome.co · api-sdk.datadome.co
buy/carts     n=0
buy/orders    n=0
```

**而 `DataDomeRelay = "datadome.cybersole.io/"` —— **第一方中继**。
`datadome.co` 不是它的子串（第 10 个字符 `o` vs `y`），所以那条断言不仅真，而且**说的正是要紧的事**：
中继用的是自家域，不是厂商域。**

### 而三条**根本不是关于镜像的断言**

**`PopMartStepMap` 与 `JohnLewisStepMap` 都有 `UnmappedSteps` 列表 ——
所以 `Assert.Null(EndpointFor("CheckResult"))` 说的是「它在那个列表里」，**是复刻件自己的记账**，
一条已经写下来的事实，不是对二进制的陈述。**

> **而那意味着 R946 把它们列进「需镜像」是**错的归类** ——
> 而更早有人在别处已经把这条缺口记下来了（`UnmappedSteps`）。**
> **所以那个机制一直在；我只是没查它就开始分类。**

### 而一条**根本不存在**

**「`NikeEndpoints.OrderV5` 不含 `scheels`」—— 那条断言在仓库里没有任何一处。**

> **R946 把它写进清单，是根据**扫描样例**里的一行推断的，而**从没读过测试体**。
> 所以八条清单从一开始就有一条是编的 —— 而它编的方式和 R944 那条假缺席**一模一样**：
> **一个听起来合理的断言，没人去读它到底在不在。****

### 所以真正的结论：**需镜像的只有 3 条，而它们全是真的**

**而 R944 那个「3 条里 1 条假」的比例，在这次样本上没有重现 ——
因为那次的三条里有两条是**同一个错写了三遍**，不是三个独立的错。**

> **所以那个「比例」本身是我从 n=3 里外推的，而 n=3 里还有两条是同一件事。
> 真相是 n=1。****

### 数字

| 度量 | R946 | **R947** |
|---|---|---|
| 套件 | 2052 | **2053** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| 需镜像的否定 | 8（7 开） | **3（全真）· 3 自证 · 1 撤回 · 1 早结** |

### 教训

> **这一轮我没有找到一个错的否定，而是发现了三件关于**我自己那次分类**的事：
> 两条归错类（`UnmappedSteps` 早就记了）、一条是编的（没读测试体）、
> 而上一轮那个「比例」是从 n=1 外推出来的。**
> **而它们的共同形状是：**我在**描述**证据，而不是**读**证据。**
> **读一行扫描输出和读一个测试体，成本差十倍，而错误的代价是同一件事：一个数字被写进文档。**


### 判据 (f) 关：三个 unmatched 的 store host，**全是支付 host**（R948）

**判据 (f) 要求「原版站点与风控清单从二进制取证 ↔ `Registry.cs` 与 `Flows/Scripts` 逐条对，
未覆盖的每条写为什么」。跑两个工具：**

```
vendor 侧: 12 个 host，absent from src 0
store  侧: 27 个 host，unmatched 3
```

### 三个 unmatched

```
api.braintreegateway.com    2 paths
api.vipps.no                1 paths
payments.bigcommerce.com    1 paths
```

**而它们**全是支付 host，不是店** —— 所以没有任何 store flow 认领它们。那不是缺口，是**分类错位**：
它们在 store 侧被数，而它们属于支付侧。**

### 而三条都有具体路径

```
Braintree   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account
            /merchants/rfbkw27jcwmw2xgp/client_api/v1/paypal_hermes/create_payment_resource
            assets.braintreegateway.com        （第二个 host）
Vipps       /adyen-card-enrollment/initiate · /commit
            /checkout-frontend/session/        （第二个 host：checkout.vipps.no）
BigCommerce /api/public/v1/orders/payments
```

> **而 Braintree 那个 `rfbkw27jcwmw2xgp` 是**商户 id**，硬写在镜像里。
> 它按商户不按厂商 —— 所以它属于**一家店**，而记住它错了会把钱打到别的商户。**

### 而 `VippsNo` 我按措辞记，不按地区记

**那串旁边还有 `3DS Unsupported (VippsNo)`。**

> **`No` 可以是 Norway，也可以是「否」。而它有第二种解释 —— 所以记成措辞，不记成 locale 标识。**

### 而工具的数字自己动了

**加完 `PaymentHostGaps.cs` 之后：**

```
store hosts matched: 27
store hosts unmatched: 0
```

> **不是因为补了三个 flow，而是因为那三个 host 现在**有名字**在 src 里。
> 而 `core_coverage.py` 的判据就是「某个注册里含这个 host 的标签」——
> 所以它从 3 变 0，说明的是**工具的条件被满足了**，不是**集成完成了**。**
> **而那个 caveat 工具自己印在最后一行：「matched 不代表实现对了」。**

### 数字

| 度量 | R947 | **R948** |
|---|---|---|
| 套件 | 2053 | **2059** |
| 产物陈旧度 | 10 文件 / 1044 行 | **11 文件 / 1153 行** |
| **store host unmatched** | 3 | **0** |
| **vendor host absent** | 0 | **0** |

### 教训

> **判据 (f) 的 store 侧从 3 变 0，而**没有任何一个 flow 被写出来**。
> 变的只是「这三个 host 在不在 src 里」这件事 —— 而工具的判据正是这个。**
> **所以「unmatched: 0」这句话是真的，而它不等于「覆盖完成」。
> 一个度量能归零，而它归零的原因可能只是**你让被度量的东西出现了**。****
> **而这一轮的真实产出是那三条路径 + 一个商户 id —— 数字归零只是它的副作用。**


### 重发布之后：陈旧度 **0**，而函数数**一个没动**（R949）

**判据 (c) 要求产物级对照可复算。陈旧度是 11 文件 / 1153 行，重发布了。**

```
publish artifact state: current
source files newer: 0
functions: replica .pdata  173,653
functions: original .pdata 277,120
```

### 而 173,653 和 R933 那次是**同一个数**

**R933 重发布加了 **1,963** 个函数。这一轮重发布加了 **0**。**

> **而这一轮之间新增了十一个文件、1153 行：`AddToCartMatrix` · `AddToCartPlacement` · `AddToCartCoverage` ·
> `CartPriming` · `PopMartDrawSteps` · `PaymentHostGaps` · `NegativeClaimClassTests` 等。**
> **而它们全是 **const 表、小静态类、和测例** —— 没有一个是 non-leaf 函数。

### 所以这给出了一个**具体的换算**

| 加什么 | 函数增量 |
|---|---|
| 常量表 / 静态类 / 测例 | **0** |
| R933 那次（真实逻辑） | **+1,963** |

> **所以剩下的 **103,467** 个函数缺口，**不能靠加表关掉**。
> 每一个 non-leaf 函数都需要**真代码** —— 一个分支、一次调用、一段状态机。**

### 而这解释了为什么最近十轮的函数数一直不动

**R938 → R949 十二轮，套件 1990 → 2059（+69 用例），而函数数一直 173,653。**

> **那十二轮的产出是**知识**（哪些名字是什么、哪些断言真的、哪些 host 是支付），
> 不是**函数**。而目标写的是「函数数量对等」——
> **所以这十二轮对那个判据的贡献是 0，而它们不是白做的：它们让**接下来写的代码**不会写错。**
> **但这一点必须说清楚，否则「套件 +69」读起来像进度。**

### 数字

| 度量 | R948 | **R949** |
|---|---|---|
| 套件 | 2059 | **2059** |
| 产物陈旧度 | 11 文件 / 1153 行 | **0 / 0（current）** |
| **函数数** | 173,653 | **173,653（未变）** |
| 函数比 | 62.66% | **62.66%** |

### 教训

> **「产物 current」和「函数数对等」是两个判据，而它们这一轮**同时被检查、只有一个变了**。
> 那正好把两件事分开：**产物可以是最新的，而功能一点没多。****
> **所以判据 (c) 通过的意思是「这个 exe 是从当前源码构建的」，
> 不是「这个 exe 更接近原版」。**
> **而唯一能量「更接近」的那个数是 173,653，而它十二轮没动。**


### 函数数不动的原因不是「表 vs 逻辑」，是**可达 vs 不可达**（R950）

**R949 的结论是「常量表加 0 个函数，真实逻辑加 1,963」。这一轮写了**真逻辑**（`RedirectPolicy`：redirect 循环、
`TooManyRedirects`、`Retry-After` 两种形式的解析、throttling 日志），重发布 —— 函数数**还是 173,653**。**

### 于是我查了产物里有没有那个新类

```
TooManyRedirects 在偏移 0x... -> 不在
```

**而 `BouncyHttpClient` 在。**

### 所以原因不是 R949 说的那个

**`RedirectPolicy` **没有任何调用者** —— 而 NativeAOT 的裁剪器会把不可达的类整个删掉。**

> **所以函数数量的是**可达代码**，不是**写了多少行**。
> 一个没人调用的类，无论它是一张 const 表还是一段带循环的状态机，**增量都是 0**。**

### 而 R949 那个「+1,963」大概是什么

**R933 那次重发布之前，我接了什么**可达**的东西（不是「逻辑」）。
所以那 1,963 是**接线**的产出，不是**写作**的产出 —— 而我把功劳记在了「逻辑」名下。**

### 而这一轮我自己的检查也错过一次

**我先在产物里搜 `JA3` / `TlsProfile` / `Tls12Profile`，三个都「不在」，于是判定「整层 TLS 被裁掉」。**

> **而 NativeAOT **不把类名写成字符串字面量** —— 除非有反射用它们。
> 所以「搜不到」不能证明「被裁掉」。§2.7b 那条「反向结论要用数据库查」我在这里用错了：
> **这次的对象是最终产物，而它的判据不是字面量，是**trim 警告 + 可达性分析**。**
> **而正确的证据是我本来就有的一对：`BouncyHttpClient` 在（有字面量）、`TooManyRedirects` 不在（我新写的、确实无调用者）。**

### 所以下一步是什么

**不是继续写类，是**接线**：让 `NetClient.SendAsync` 真的走 `RedirectPolicy`，
那样它才进产物，函数数才动。**

> **而这条对 103,467 个缺口的意义是：**缺口不是「还没写」，是「写了但没接上」。**
> **而复刻件已有 ~3,200 行 HTTP 层 —— 其中多少在产物里，现在还不知道。**

### 数字

| 度量 | R949 | **R950** |
|---|---|---|
| 套件 | 2059 | **2088** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,653 | **173,653（写了真逻辑仍未变）** |
| **`RedirectPolicy` 在产物里** | — | **不在（无调用者）** |

### 教训

> **「写了一个类」和「产物里多了一个类」是两件事，而我只检查了前者。**
> **而更贵的是上一轮的结论：我把「加表不动数」和「加逻辑动了数」写成了一条规律，
> 而两个观测都不支持它 —— 一个是因为表不可达，另一个的原因我根本没查。**
> **从 n=2 里读出一条规律，而两个样本的因都不是我以为的那个。**


### 接线成功了，而函数数**还是不动** —— 因为 `.pdata` 数的是**未被内联**的函数（R951）

**R950 说「接线才动数」。这一轮接了：`RedirectPolicy` 接进 `NetClient.SendAsync`。**

### 而接线**确实成功了**

```
修改前:  TooManyRedirects 不在产物
修改后:  TooManyRedirects **在**产物
size: 54,652 KB -> 54,655 KB
```

**所以 R950 那条「可达才进产物」是对的。**

### 而函数数**还是 173,653**

### 原因在工具自己的注里

> 「`.pdata` holds one RUNTIME_FUNCTION per non-leaf function:
> it **excludes inlined and trimmed code**」

**而我接进去的是 `IsRedirect` / `LimitFrom` / `Resolve` / `PreservesMethod` / `TooManyRedirectsName` ——
**五个小方法**。**

> **它们全部被**内联**了。内联之后，它们不是函数，是别人函数体里的几条指令。
> 所以产物里**有那个类**（字面量在），而 `.pdata` 里**没有那几个函数**。**

### 所以三层结论，一层比一层窄

| 层 | 判据 | 我加的代码 |
|---|---|---|
| **写了** | 源码里有 | ✅ |
| **进了产物** | 字面量/可达 | ✅（R951 证实） |
| **进了 `.pdata`** | **未被内联** | **❌** |

> **而目标写的是「函数数量对等」—— 那指的是第三层。
> 所以「写」和「接」都不够；**方法得大到编译器不愿内联**，或者**是 async（状态机会留下）。****

### 而 `FollowAsync` 是 async —— 它**会**留一个状态机

**而我没接它：`NetClient` 用的是 `IsRedirect` 那几个同步小方法 + 自己的递归，
没走 `RedirectPolicy.FollowAsync`。**

> **所以真正会动数的那个方法，反而没被调用。而这是因为我在接线时选了**最省事的五个小函数**，
> 而不是那个真正的循环。**

### 数字

| 度量 | R950 | **R951** |
|---|---|---|
| 套件 | 2088 | **2093** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`TooManyRedirects` 在产物** | 不在 | **在** |
| **函数数** | 173,653 | **173,653（仍不变）** |
| 产物大小 | 54,652 KB | **54,655 KB** |

### 教训

> **三层的区别是这一轮唯一的产出，而它比「又写了一个类」贵得多：
> 「写了」「进了产物」「进了 `.pdata`」是三件不同的事，而我一直只查第一件，
> 上一轮查了第二件，这一轮才明白目标指的是第三件。**
> **而第三件的判据不是我的意图，是**编译器的内联决定** —— 一个我完全看不见的、由方法大小和调用次数决定的开关。**


### 接一个 async 方法，函数数 **+128** —— 十四轮里第一次动（R952）

**R951 说「`FollowAsync` 是 async，它会留状态机，而我没接它」。这一轮接了。**

```
pdata-replica: 173,653 -> 173,781     +128
pdata-ratio:   62.66%  -> 62.71%
产物大小:      54,655 KB -> 54,674 KB   +19 KB
```

### 而 +128 不是我预期的数

**我接进去的只有**一个**调用点，而它带来 128 个 `.pdata` 条目。**

> **所以一个 async 方法带的不是「一个状态机」：
> 状态机的 `MoveNext`、它的泛型实例化、闭包类、`FollowAsync` 里 `Resolve`/`IsRedirect` 的调用点被内联后的副本 ——
> **编译器为这一个抽象生了 128 个函数。****

### 而这条路径现在有证据了

| 轮 | 假设 | 观测 |
|---|---|---|
| R949 | 「表 0 / 逻辑 1,963」 | **错** —— 表和逻辑都不可达 |
| R950 | 「可达才进产物」 | **对** —— `TooManyRedirects` 从不在变在 |
| R951 | 「可达还不够，要过内联」 | **对** —— 五个小方法内联，`.pdata` 不动 |
| **R952** | **「async 会留状态机」** | **对 —— +128** |

> **四轮，四次修正，最后一次才让那个数动了。
> 而前三次都不是白错：每一次把「为什么不动」往前提了一层 ——
> 不可达 → 可达但内联 → 内联不了的 async。**

### 而这也给出了缺口的一条具体路径

**103,467 个缺口，如果平均每次「接线一个 async 方法」加 ~128，那需要约 **800** 次这样的接线。**

> **而这不是「写 800 个 async 方法」—— 是**把已有的 async 方法接进可达路径**。
> 而复刻件的 flow 里已经有大量 async 方法（`StepAction` 的每一步都是）。
> **所以缺口的性质可能真的是「没接上」，而不是「没写」—— 但 R950 那条只是 Inference，现在有一个数据点了。****

### 数字

| 度量 | R951 | **R952** |
|---|---|---|
| 套件 | 2093 | **2093** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,653 | **173,781（+128）** |
| **函数比** | 62.66% | **62.71%** |
| 产物大小 | 54,655 KB | **54,674 KB** |

### 教训

> **十四轮里函数数一动不动，而让它动的不是「更努力地写」，是**找到那个数到底在数什么**。
> 而找到它花了四轮，每轮都推翻上一轮的因果。**
> **最贵的一轮是 R949：那一轮我写下了「表 0 / 逻辑 1,963」，一个从两个错样本里读出的规律，
> 而它差点让我以为「只要写逻辑就会动」。**
> **如果那条规律没被 R950 推翻，接下来的每一轮都会写「逻辑」，然后困惑为什么不动。**


### 「800 次接线」这个估算，第一次查看就**散了**（R953）

**R952 说缺口约 800 次接线，而依据是「复刻件有很多 async 没接上」。这一轮去数。**

```
src 里 async 方法: 538
  主类型无人引用的文件: 93 （其中含 async 的 26 个）
```

**而第一个被查看的文件就把估算打破了。**

### `Retail2Modules.cs` 的五个 module，**全是已注册 flow 的副本**

| Module | 重复的 flow | 已在 catalog |
|---|---|---|
| `CasioModule` | `CasioFlow` | ✅ |
| `JbHiFiModule` | `JbHiFiFlow` | ✅ |
| `PocketGamesModule` | `PocketGamesFlow` | ✅ |
| `SuperswipeModule` | `SuperswipeFlow` | ✅ |
| `WarhammerModule` | `WarhammerFlow` | ✅ |

> **而 `StoreModuleCatalog.CreateAll()` 返回 `IStoreModule[]`，module 类**正好**符合那个接口 ——
> 所以把它们加进去**能编译、能跑**，而它会让 `Casio` 在 catalog 里出现**两次**（一次 flow、一次 module）。
> **那是行为错误，不是对等收益。****

### 所以不可达的代码分两种，而我只估了第一种

| 种类 | 该做什么 |
|---|---|
| **未接上**（有独立价值） | 接线 |
| **重复品**（和已注册的等价） | **删，不是接** |

> **而「800 次接线」把两者算成了一种。而区分它们的工作，正是这一轮真正的事 ——
> 而它不能靠数名字，只能**逐个看那个类是不是已经有一个等价的已注册项**。**

### 而 538 这个数也不能直接用

**它是 `async` 关键字的出现次数，不是「未接的 async 方法数」。
93 个可疑文件里 26 个含 async —— 而那 26 个里已经有一个是纯重复。**

### 数字

| 度量 | R952 | **R953** |
|---|---|---|
| 套件 | 2093 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781（未改产品代码）** |
| **纯重复 module** | 未查 | **5** |

### 教训

> **一个估算的第一次具体查看，往往不是把它细化，是把它**否掉**。
> 而 R952 那个「≈800」是从一个 n=1 的增量和一句 Inference 乘出来的 ——
> 它读起来像一个计划，而它从来没有被任何一个具体文件检验过。**
> **而检验它花了不到十分钟，代价是**那个估算不再可用**。
> 而那比继续按它做 800 次接线便宜得多。**


### 93 个分完：**7 个重复品**，而 R920–R925 那五轮**一个都没接上**（R954）

**R953 说下一轮逐个查 93 个。查了，而过程中我**三次**把判据写错。**

### 三次错的判据

| 判据 | 结果 | 为什么错 |
|---|---|---|
| `Id =>` 与 catalog 的 `Id =>` 撞 | 1 个 | **catalog 的 id 来自 `FlowStoreModule` 包装，不写 `Id =>`** |
| `Store =>` 收集 flow 的 id | **0 个** | **flows 根本不声明 `Store =>`** |
| **`XxxModule` 有同名 `XxxFlow`** | **7 个** | ✅ **这条对了** |

> **前两条错在同一个地方：我以为 id 的写法是一种，而它是三种。
> 而第三条不需要知道 id 怎么写 —— 它只问「有没有一个同名的 flow 类」，那是结构，不是字符串。****

### 7 个重复品

```
BrandModules.cs      -> FanaticsFlow      (10 async)
Retail2Modules.cs    -> CasioFlow         (10)
RetailModules.cs     -> EndClothingFlow   (6)
UkEuModules.cs       -> SnsFlow           (6)
MoreModules.cs       -> KithFlow          (4)
NikeModule.cs        -> NikeFlow          (4)
Registry.cs          -> SupremeFlow       (4)
```

**全部是 `*Module` 类 —— 一个和 `FlowStoreModule` 平行的、未接的层级。**

### 而剩下 86 个里，有**五个是我自己五轮前写的**

```
PurpleDot       (R920)  ← 无人引用
EshopWorldPanel (R923)  ← 无人引用
DisneyPaymentSheet (R924) ← 无人引用
VivaPayments    (R925)  ← 无人引用
GlobalECheckout (R922)  ← 无人引用
```

> **R920–R925 五轮，每轮写了支付集成、加了测试、更新了 METRICS。
> 而那五轮的函数贡献是 **0** —— 它们全在 93 个无人引用的文件里。**
> **而当时的 commit 信息写的是「PurpleDot built」—— 它 built 了，只是没接上。**

### 而这不是「白做」

**它们是可复用的、有测试的、证据正确的实现。而它们现在是**dead code**，直到有人把一个支付步骤接到它们上面。**

> **而这个区分对目标很重要：那五轮让**功能**前进了（逻辑写对了），让**函数数**没动（不可达）。
> **两个判据又一次分开，而这次分开的是我自己的五轮。**

### 数字

| 度量 | R953 | **R954** |
|---|---|---|
| 套件 | 2097 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781** |
| **重复品** | 5（只查一个文件） | **7（全扫）** |
| **我写的死代码** | 未知 | **5 个支付类** |

### 教训

> **三次判据、两次错，而两次都错在「我以为 id 只有一种写法」。
> 第三次不问 id，只问结构 —— 而它一次就对。**
> **而更贵的是后半：我查了五轮前的自己。而那五轮的 commit 信息、测试、METRICS 更新都读起来像进展，
> 而函数数一次没动 —— 因为**没有任何东西调用它们**。**
> **R952 那条「缺口是没接上而非没写」现在第二次被证实，而这次证实它的是我自己写的代码。**


### 接两个支付网关：**+43 函数**，而模式第二次成立（R955）

**R954 说五个支付类全是死代码。这一轮把它们接上。**

```
SubmitPaymentAsync 原来是 => NotSupported("SubmitPayment")
现在：按 session 的 paymentGateway 派发到 VivaPayments / DisneyPaymentSheet
```

```
pdata-replica: 173,781 -> 173,824     +43
pdata-ratio:   62.71%  -> 62.73%
size:          54,674 KB -> 54,692 KB
```

### 而 +43 vs redirect 的 +128

| 接的 | 增量 | 为什么 |
|---|---|---|
| `RedirectPolicy.FollowAsync` | **+128** | 一个 async + 泛型实例化 + 闭包 + 内联副本 |
| 两个支付网关 | **+43** | 两个已有 async，各带自己的状态机 |

> **所以增量不是常数，是**那个 async 方法带多少个实例化**。
> 而 +43 / 2 ≈ 21 每个 —— 比 128 小，因为 `ChargeTokenAsync` 的泛型面更窄。**
> **而两个数都远大于 1 —— 所以「接一个 async ≈ 十几个到一百多个函数」这条现在有两个样本。**

### 而这次接线是**对的**，不是「为动数而接」

**`SubmitPaymentAsync` 原本返回 `NotSupported` —— 那是一个**真缺口**：
支付步骤存在、五个网关实现存在、而中间那一句调用不存在。**

> **所以这一轮不是「找个地方接一下让数动」，是**补上那两个实现之间缺的那一行**。
> 而数动是它的**后果**，不是目的。**

### 而修的时候撞了五次签名

**`ChargeTokenAsync(FlowSession, card, expiry, ct, Func<string,string,string,CancellationToken,Task<NetResponse?>> post)` —— 五个参数，
最后一个是**调用方传入的 POST 委托**（网关不拥有 client）。**

> **而我第一版按 `(NetClient, url, ct)` 写，全错。
> 而 `StepOutcome` 只有 `Success()/Fail()/Stop()`，没有 `Retryable()`；
> `NotSupported` 返回 `Task<StepOutcome>`，在 async 里要 `await`。**

**五次编译错误，五次都是「我以为签名是什么」而不是「读签名」。**

### 数字

| 度量 | R954 | **R955** |
|---|---|---|
| 套件 | 2097 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,781 | **173,824（+43）** |
| **函数比** | 62.71% | **62.73%** |
| 产物大小 | 54,674 KB | **54,692 KB** |

### 教训

> **上一轮我把五个支付类叫作「死代码」，而它们只是**没人调用**。
> 这一轮补上那句调用 —— 四十三个函数出现，而它们一直都在，只是没有被任何人从入口走到。**
> **「死代码」这个词是错的：代码没有死活，只有**可达不可达**。
> 而不可达的代码需要的不是重写，是**一句调用**。**


### `paymentGateway` 是**我编的**，而镜像是 `_paymentGatewayName`（R956）

**R955 接支付派发时用了一个 session 键叫 `paymentGateway`，而把它列进 Unknown：「原版按什么派发未取证」。
这一轮取证了。**

### 而镜像里有五个相关的名字

```
_paymentGateway          字段（带下划线的 backing field）
_paymentGatewayName      绑定属性
PaymentGateways          集合（复数）
paymentProvider
paymentFlexibilityTemplate / paymentFlexibilityPaymentTermsTemplate / paymentFlexibilityTermsId
```

### 而一条描述符把它们串在一起

```
_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate
```

> **`_captchaToken` 就紧挨着 `_paymentGatewayName` ——
> 所以一次支付提交带的是**一个 token 和一个网关名**，而那正是真实形状。
> 而我上一轮只带了网关名，把 captcha 当成别处的事。****

### 所以改了三处

| 原来（我编的） | 现在（镜像的） |
|---|---|
| `"paymentGateway"` | **`PaymentGatewayNameKey = "paymentGatewayName"`** |
| — | **`CaptchaTokenKey = "captchaToken"`** |
| switch 里硬编码四个 case | **`PaymentGateways = {viva, disney, purpledot, eshopworld}`** |

> **而 `PaymentGateways` 是**复数** —— 所以一家店可能接受多个网关，
> 而一个集合是对的形状，不是单个值。**

### 而这个名字为什么危险

**`paymentGateway` 与 `paymentGatewayName` 只差四个字符。
它编译得过、测试过得、读者不会怀疑 —— 而它不是原版的名字。**

> **而这就是这几轮一直在找的那种错：**一个听起来合理的名字，顶替了一个查出来的名字。**
> **而这次的代价是**没有代价** —— 因为那个键只在复刻件内部用。
> 如果它是持久化字段名（像 `settings.json` 的 `startup` 那样），它会**静默地读不到原版的数据**。****

### 而这一步撞了构建崩溃

**第一次 publish：`ilc` 退出码 `-1073740791`（0xC0000409）。
第二次：`LNK1136: 无效或损坏的文件` —— 崩溃留下的坏 `.obj`。**

> **处置：删掉 `obj\Release\net8.0\win-x64\native` 那 4 项，重发成功。
> 而这是**崩溃的次生错误**被当成主错误报出来的经典形状 ——
> 第二次那个 LNK1136 读起来像「源码有问题」，而它只是第一次崩溃的残留。**

### 数字

| 度量 | R955 | **R956** |
|---|---|---|
| 套件 | 2097 | **2101** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 教训

> **这一轮函数数没动 —— 而它是这几轮里最值钱的一轮之一。
> 因为上一轮那 43 个函数建立在一个**编出来的键名**上，而这一轮把它换成了证据里的名字。**
> **而「数动了」和「做对了」又一次分开 —— 这次分开在同一段代码上，隔了一轮。**


### 上一轮我改对了键名，**却把发明留在了下一层**（R957）

**R956 把 `paymentGateway` 换成 `paymentGatewayName`，然后写了一个常量数组
`PaymentGateways = {viva, disney, purpledot, eshopworld}` —— **那四个名字也是编的**。**

### 而查出来的是另一套机制

```
PreferredGateways     设置（有序偏好）
blockedGateways       设置（排除）
RpcGetPaymentMethods  取这家店提供哪些
ParsePaymentMethods   解析那个答案
IsWalletOnly          分类钱包类（不需要卡）
```

> **所以网关**不是一个常量** —— 它是**这家店返回的东西，被两个设置过滤**。
> 而我上一轮写的那四个名字，既不来自镜像、也不来自任何一家店的返回。**

### 改成了选择函数

```
ChooseGateway(available, preferred, blocked)
  → 偏好顺序命中且未封禁的胜出
  → 没偏好 → 取第一个未封禁的（而不是一个都不选）
  → 全被禁 / 空的 available → null
```

> **「没偏好 → 取第一个未封禁的」这一条是刻意的：
> 一家店提供支付，不能因为用户没表达偏好就失败。而这是**行为决定**，不是从列表里挑一个。****

### 而 `apple_pay` 与 `applepay` 两种拼法

**我的第一版只匹配 `applepay`，而测试里 `apple_pay` 失败了。
而两种拼法**都存在**（镜像和各家店不一致），所以两个都查。**

### 而函数数**不动**

**`ChooseGateway` 与 `IsWalletOnly` 是小的同步方法 → 被内联 → `.pdata` 不增。**
**与 R951 一致。**

> **所以这一轮的价值不在数上：它把**四轮前那 43 个函数**所依附的选择逻辑，
> 从一个编出来的常量换成了一个有证据的过滤函数。**

### 数字

| 度量 | R956 | **R957** |
|---|---|---|
| 套件 | 2101 | **2115** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变，内联）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 教训

> **两轮，同一个错两次：R956 修了**键名**，却留着**取值集合**是编的；
> R957 修了取值集合，而它的形状（一个常量）仍然是编的。**
> **而两次我都以为改对了 —— 因为两次我都只改了**被上一个错误直接指出的那一样东西**。
> 而那个错误的下层还有一层，它长得不像错误，因为它是**一个数组**。**


### 一条描述符给出十个 RPC 步骤，而复刻件**缺三个**（R958）

**R957 说「下一步反编译 `RpcGetPaymentMethods` 看返回形状」。查了 —— 而反编译这条路**先断了**，
而断掉的地方给出了更好的东西。**

### 反编译为什么走不通

```
ida.py funcs RpcGetPaymentMethods  -> 不过滤，从头返回所有 sub_XXXX
ida.py xrefs 0x14337ca41            -> xref_count: 0
```

**NativeAOT **剥掉了符号名**（只有 `sub_140xxxxxx`），而那串描述符是**反射表里的类型名**，
所以没有任何代码引用它 —— `xrefs` 为空。**

> **所以「按名字找函数再反编译」在这个二进制上不成立。而这一条之前从没被明确记下来。****

### 而那条描述符本身就是证据

```
d__169 RpcLogin              d__174 RpcCalculateShipping
d__170 RpcFindProduct        d__175 RpcValidateBuyRule
d__171 RpcCheckStock         d__176 RpcCreateOrder
d__172 RpcFetchAddress       d__177 RpcGetPaymentMethods
d__173 RpcCreateAddress      d__178 RpcSubmitCard
```

**十个连号 —— 一个 RPC 面，而且**有序**。**

### 而逐条对完，缺三个

| 镜像 | 复刻件 |
|---|---|
| RpcLogin · RpcFindProduct | `Login` · `FindProduct` ✅ |
| RpcFetchAddress · RpcCreateAddress | `BuildDestination` · `SubmitAddress` ✅（改名） |
| RpcCalculateShipping | `GetShippingRates` ✅（改名） |
| RpcCreateOrder · RpcSubmitCard | `SubmitOrder`/`PlaceOrder` · `SubmitPayment` ✅（改名） |
| **RpcCheckStock** | **无** |
| **RpcValidateBuyRule** | **无** |
| **RpcGetPaymentMethods** | **无** |

> **而三个都不是同义词：
> `CheckStock` 在订单存在**之前**问库存（页面的刮取是**页面说了什么**，这个是问店的库存服务，两者会不一致）；
> `ValidateBuyRule` 是**店自己的购买政策检查**（限量、地区、额度）；
> `GetPaymentMethods` 是**回答这家店提供哪些支付方式** —— 而 R957 正是因为不知道这个，才编了一个常量数组。****

### 所以三个都写成了有实体的步骤

**不是 `=> NotSupported` 的空壳 —— 每个都有真实分支：**

- **`CheckStockAsync`**：取 sku → 打库存 URL → 404/410 判缺货 → 非 2xx 判可重试 →
  **body 里找 `"available":false` / `"inStock":false`**（"200 不等于可买"）
- **`ValidateBuyRuleAsync`**：POST 政策 URL → 非 2xx 时**判不可重试**
  （重试一个政策决定只是把同一个问题再问一遍）
- **`GetPaymentMethodsAsync`**：取 URL → 解析出 offered → **交给 R957 的 `ChooseGateway`** →
  把选中项写回 `paymentGatewayName`。**这才是让 R957 那个选择函数有意义的调用点。**
- **`ParsePaymentMethodNames`**：在 `id`/`code`/`type`/`name`/`method` 五种字段名里找引号值，
  **不假设 schema**，找不到就返回空。

### 而构建崩了两次，两次都不是源码的问题

```
第一次: ilc 退出 -1073740791 (0xC0000409)
第二次: LNK1136: 无效或损坏的文件  (Cybersole.Ui.obj)
```

**第二次是第一次留下的坏 `.obj`。而连 `native` 目录一起删都不够 ——
要把 `src\Cybersole.Ui\obj` 与 `bin` **整个删掉**，才重发成功。**

> **所以「LNK1136 读起来像源码坏了」是假的：它是**崩溃的残留**，
> 而残留比崩溃活得更久、更像一个真错误。****

### 而一个守卫红了，而它自己的注释说了该怎么做

**`FlowSequenceTests.OnePopMartImageStepIsDispatchable` 断言 `map.Count == 176`。
我加了三个虚步骤 → 179。**

> **而那个测例的注释写着：「the fix is to write the new number in and say which step arrived —
> never to delete the assertion」。所以改了数字并写明三个步骤到了。**
> **而 `implementable` 仍是 8 —— 三个新步骤名都不在 PopMart 的 24 个名字里，与 `FindProductInstore` 同样的分裂。**

### 数字

| 度量 | R957 | **R958** |
|---|---|---|
| 套件 | 2115 | **2129** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,824 | **173,866（+42）** |
| **函数比** | 62.73% | **62.75%** |
| 产物大小 | 54,692 KB | **54,706 KB** |
| 分派表 | 176 | **179** |

### 教训

> **这一轮想要的证据（`RpcGetPaymentMethods` 的返回形状）**没拿到**，
> 而拿到的是一条更强的：那个二进制**不给名字**，所以「按名字反编译」整个方法在这个目标上不成立。**
> **而这一条比一次成功的反编译值钱 —— 它关掉了一条我会反复尝试的路，
> 同时把注意力推到唯一能用的东西上：**连号描述符里的顺序**。**


### Queue-it 是从**一个类的字段列表**里读出来的（R959）

**R958 之后转优先级 ②。而 IDA 断过一次（重启后没开），三个框走完才就绪 —— 而就绪之后拿到的证据出乎意料地实。**

### 一段字段列表，不是名字

```
QueueHostMarkers(AcceptedCookiePrefix<QueueITAccepted-SDFrts345E-V3_*CookieValiditySecondsa<MinRemainingSecond
```

**那一条串里是一个类的**完整字段清单**：**

| 字段 | 值 |
|---|---|
| `QueueHostMarkers` | 判定这是不是 Queue-it 表面 |
| `AcceptedCookiePrefix` | **`QueueITAccepted-SDFrts345E-V3_`** |
| `CookieValiditySeconds` | 通行证有效期 |
| `MinRemainingSeconds` | 通行证**至少还要剩多久才算可用** |

> **那个前缀里的 `SDFrts345E` 是一个**哈希**，是 cookie 名字的一部分 —— 不是占位符。
> 所以它逐字保留，不做归一化。****

### 而 `MinRemainingSeconds` 这个字段说明了为什么要提前几秒判废

**一个剩余有效期为几秒的通行证比没有更糟：**
**它授权的那个请求会在**排队已经离开之后**才被拒。**

> **所以那个判断不是「它有效吗」，是「它有效到**够跑完**吗」。
> 而复刻件如果只判前者，会在最难恢复的位置失败。****

### 而五条控制流文案里有一条**拼错了**

```
Fetching Queue-it challenge
Initiliazing Queue-it                 <- 镜像自己拼错（Initiliazing）
Error Initiliazing Queue-it (Softblock)
Error Solving Queue-it (Softblock)
Queue-IT banned, rotating proxy
```

> **而拼错的这条**照原样保留**。
> 一个「把拼写改对」的复刻件，日志就不再和原版一样了 —— 而这种差异在某天对日志时是最难查的。****

### 而一个状态可以有两种意思，所以判定要两样东西

**200 加一个通行证 = 通过；200 没有通行证 = **还在排队**。同一个状态码。**

**所以 `Verdict(status, hasPass)` 收两样，而不是只看 status。**

### 数字

| 度量 | R958 | **R959** |
|---|---|---|
| 套件 | 2129 | **2147** |
| 产物陈旧度 | 0 / 0 | **1 文件 / 119 行（需重发）** |
| 函数数 | 173,866 | **173,866（未变 —— 全是 const 与小静态方法且无人调用）** |

### 教训

> **这一轮最实的一条不是「Queue-it 存在」，是那个**字段列表**。
> 名字告诉你有一家厂商；字段列表告诉你**它怎么判、判什么、以及为什么不能等到零**。**
> **而一个线索的价值，取决于它离**行为**有多近。`Queue-it` 这个词离行为很远，
> `MinRemainingSeconds` 就在行为里。**


### `PollQueue` 本来是 `=> Ok()`，而它现在做决定了（R960）

**R959 说下一步重发消陈旧度。重发之前先看一眼 `PollQueueAsync` —— 而它是：**

```csharp
public virtual Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct) => Ok();
```

> **一个命中排队页的流程会**认为自己已经通过了排队**，因为那个步骤直接返回成功，
> 而它没有看任何东西。**
> **而那正是 R959 那个字段列表要治的病 —— 只是没人把它接上。****

### 接上之后

**`PollQueueAsync` 现在做四件事：**

1. **不是队列宿主 → 直接成功**（`IsQueueHost`，没有可等的）
2. **循环到 deadline**，每轮 `Verdict(status, hasPass)` 分类
3. **`Passed` 但要再看剩余时间** —— 剩余短于 `queueMinRemaining` 就**继续等**，
   而不是把那个通行证花在一个**会被拒的请求**上
4. **超时 = `retryable: true` 的失败**

> **第 4 条是这一轮的正题：`Ok()` 说超时是成功。而超时不是成功。
> 一个把超时说成成功的步骤，比一个报错的步骤**难查得多** —— 因为下游会拿到一个假的绿灯。****

### 三个设置名

**`queueTimeout`（120s）· `queuePollMs`（2000）· `queueMinRemaining`（30s）· `queuePassSeconds`（300）**

**而它们的值标了 Inference —— 镜像给了字段名（`CookieValiditySeconds` / `MinRemainingSeconds`），
没给数值。**

### 数字

| 度量 | R959 | **R960** |
|---|---|---|
| 套件 | 2147 | **2153** |
| 产物陈旧度 | 1 文件 / 119 行 | **0 / 0** |
| **函数数** | 173,866 | **173,909（+43）** |
| **函数比** | 62.75% | **62.76%** |

### 教训

> **上一轮我把 Queue-it 的判定条件读出来了，而这一轮发现那个该用它的步骤**从来没看任何东西**。
> 而这不是我造成的 —— 它在 R112 就是这样，而**没有任何东西指出它**。
> **一个 `=> Ok()` 的虚步骤读起来像一个「留给子类覆写」的位置，而它同时是一个**假的成功**。
> 两者的差别只在**有没有人覆写它**。**


### 36 个 `=> Ok()`，而这一轮修了其中一个（R961）

**R960 的下一步是数还有多少空壳。数出来是 **36 个**，而它们全是核心结账步骤：**

```
GetCsrf · GetSession · VerifySession · ScrapeVariantAvailability · CheckPriceLimit
CreateCart · GetCart · EditLine · InitiateCheckout · SubmitEmail · SubmitShippingMethod
GetShippingRates · SubmitBilling · Login · CheckLogin · Register · CompleteRegistration
SendTwoFactor · GetScript · SubmitSensor · GetCaptcha · SolveCaptcha · EnterRaffle
GetRaffleData · ScrapeRaffleForm · PollRelease · PollRestock · WaitForRelease · FindSlot
GetReleaseFeed · LoadCountryData · ProcessResponse · Fill · GetStructureToken · BuildDestination
```

> **36 个假绿灯，全部在结账路径上。而这不是我造成的 —— 它们在 R112 就是这样。**
> **而 `=> Ok()` 读起来像一个「留给子类覆写」的位置。差别只在**有没有人覆写它**。****

### 而 `SolveCaptcha` 有最完整的证据

```
SolveCaptchaService
<SubmitPat>d__11 · <SolveCaptcha>d__12 · <SubmitCaptcha>d__13
https://api.solvecaptcha.com/in.php
https://api.solvecaptcha.com/res.php?key=
```

**两个端点 + 三个连号状态机 —— 足够做真事，不只是报告成功。**

### 而 `CAPCHA_NOT_READY` 不是失败

**一个「还没好」的应答是**正常路径**。把它当失败会废掉**每一次超过一轮轮询的求解**。**
**所以它单独分类，并且**回到同一个等待**。**

> **而空应答（`null` / `""`）我判 `NotReady` 而不是 `Failed`：
> 那是**传输失败**，不是服务拒绝。判 Failed 会让一次网络抖动废掉一个下一轮就好的求解。
> 而循环本来就把「到 deadline 没解出来」变成 retryable 失败 —— 那才是那个判决该在的位置。****

### 而这一轮我**错了两次**，两次都在「怎么查」上

**错一：产物里没有新代码？**

**我用 PowerShell 手写字节循环搜 UTF-16，得出 `api.solvecaptcha.com/in.php` **不在产物**。
换成 Python 三行：**

```
api.solvecaptcha.com     utf16=True
CAPCHA_NOT_READY         utf16=True
captcha not solved       utf16=True
QueueITAccepted          utf16=True
```

> **全部在场。所以不是产物缺东西，是**我的搜索工具有假阴性**。
> 而这正是 AGENTS.md §2.7b 那条「反向不可用」：搜不到 ⇏ 没有。****

**错二：`StepActionRunner` 不是一张手写表**

**我读源码搜 `'SolveCaptcha' in 表文件` → False，然后写下「新步骤必须**登记**才可达」。**
**再读 `Build()` 才发现它靠**反射扫描** `typeof(StoreFlow).GetMethods()`，名字**根本不会**以字面量出现。**

> **所以「必须登记」是错的：所有 `*Async` + `Task<StepOutcome>` + 两参数的公开方法**自动**进表。
> 而这正是 R870 那条：**动手之前先读实现，不要按名字猜结构。**
> 而我这一轮**在写这条更正的同时**才去读 `Build()` —— 前一句已经写进记录了。****

### 数字

| 度量 | R960 | **R961** |
|---|---|---|
| 套件 | 2153 | **2173** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变 —— 全是内联 + 一个小状态机被并）** |
| 产物大小 | 54,706 KB | **54,720 KB（+14 KB，新代码在场）** |
| 空壳 `=> Ok()` | 36 | **35** |

### 教训

> **这一轮最贵的两条都不是 `SolveCaptcha` 的实现，是**两次自我更正**。
> 一次是搜索工具有假阴性，一次是我按名字猜了一个反射表的结构。**
> **而两次的形状相同：**我用一个不可靠的检查得出一个听起来干净的结论**，
> 然后那个结论差一点进了 BACKLOG 当成事实。**
> **检查工具本身也要被检查 —— 尤其是当它给出「没有」的时候。**


### `GetCsrf` 写了，而**产物里没有它** —— 于是我该查的都查了一遍（R962）

**R962 把 `GetCsrfAsync` 从 `=> Ok()` 写成真实现（四种 token 形状 + 四个 cookie 名）。
DLL 里字符串**全在**，AOT 产物里**没有**。于是查了十二个标记串：**

| 来源 | 标记串 | 在产物 |
|---|---|---|
| R959 `QueueItProtocol` | `QueueITAccepted` | **在** |
| R959 文案 | `Initiliazing Queue-it` | **在** |
| R959 `HostSuffix` | `.queue-it.net` | 不在 |
| R960 `PollQueueAsync` | `queue not passed within the deadline` | 不在 |
| R960 设置 | `queueMinRemaining` | 不在 |
| R961 `SolveCaptchaService` | `api.solvecaptcha.com` | **在** |
| R961 应答 | `CAPCHA_NOT_READY` | **在** |
| R961 步骤体 | `captcha not solved within the deadline` | 不在 |
| R962 步骤体 | `no csrf token on the page` | 不在 |
| R962 cookie | `csrftoken` | 不在 |
| R955 派发 | `SubmitPayment:` | 不在 |
| R958 库存 | `out of stock` | **在** |

**五在，七不在。而函数数从 R958 起是 173,866 → 173,909 → 173,909 → 173,909。**

### 所以那三个 +42 / +43 / +43 **是什么**

**在产物的五个都是**静态类里的 const**（`QueueItProtocol` 的两个、`SolveCaptchaService` 的两个、`CheckStockAsync` 的一个）。**

> **所以那三段增量更可能是**静态协议类变得可达**，不是**步骤体进了产物**。
> 而我在这三轮里都写了「接线让步骤体进产物」——**那个因果解释未被证明。**
> **而 R955 那句「+43 来自支付派发」也属于同一类：数动了，归因是猜的。****

### 而这为什么重要

**如果步骤体不进产物，那么「把 `=> Ok()` 写成真实现」这个动作**不会改变函数数**，
而我一直用它当进展指标。**

> **这不代表那些工作没价值 —— 源码是对的、编译过、能测。
> 但它代表**我一直在用一把量不到那个东西的尺子**。**
> **而 §2.7b 那条「反向不可用」在这里的形态是：**函数数没动 ⇏ 工作没做**。
> 而我这次是反过来踩的：**工作量了没动，我却说是别的东西让它动的**。****

### 而机制本身仍然 Unknown

**为什么 `PollQueueAsync` 的体不在、而 `QueueItProtocol` 的 const 在？
为什么 `SubmitPayment:` 不在、而 `out of stock` 在？**

**两者都是 `StoreFlow` 的 virtual 方法、都由反射表派发、都零覆写。
所以「有没有覆写」不是解释 —— 我试过，它对不上。**

> **已知的只有：派发表靠 `GetMethods()` 反射建，而反射在 NativeAOT 下**不 root 方法**。
> 所以哪些留下，取决于应用实际构造了哪些 flow、实际调用了什么。
> 而这一层我没有取证。标 Unknown，不标 Inference。****

### 数字

| 度量 | R961 | **R962** |
|---|---|---|
| 套件 | 2173 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变）** |
| 产物大小 | 54,720 KB | **54,724 KB** |
| 空壳 `=> Ok()` | 35 | **34** |
| **步骤体在产物里的轮** | — | **R955–R962 共八轮，五在七不在** |

### 教训

> **这一轮真正的产出不是 `GetCsrf`，是那句「我一直在用一把量不到那个东西的尺子」。
> 而它是在**我本该庆祝 34 个空壳变 33 个的时候**发现的。**
> **一个指标连续三轮不动，而我连续三轮都给了一个动听的原因 ——
> 那本身就是那个指标在说「你归错了因」。**


### 那把尺子修好了：**被覆写的步骤体进产物，零覆写的不进**（R963）

**R962 说「哪些步骤体进产物 Unknown」。这一轮用一组对比把它定下来。**

### 三个观察，逐条可复算

**① `RegisterAll` 在启动路径上**

```
Program.cs: StoreModuleCatalog.RegisterAll(registry);
Registry.cs: foreach (var module in CreateAll()) registry.Register(module);
```

**它在 `App.OnFrameworkInitializationCompleted` 里 —— **必然执行**。所以 35 个 flow 都被构造。**

> **所以被裁的不是「构造」，是**方法体**。**

**② 同一个类里两个方法，一个在、一个不在**

```
BstnFlow.GetCartAsync 里: "bstn: cart endpoint unknown"      -> utf16=True
BstnFlow 里:              "bstn: order endpoint unknown"     -> utf16=False
```

**而 `BstnFlow.GetCartAsync` 是**全仓唯一一处覆写**（R962 数过：`GetCart` 覆写 1 处，其余 7 个抽样步骤 0 处）。**

**③ 零覆写的基类步骤体全都不在**

```
queueMinRemaining                          -> False   (R960 PollQueueAsync)
captcha not solved within the deadline     -> False   (R961 SolveCaptchaAsync)
no csrf token on the page                  -> False   (R962 GetCsrfAsync)
SubmitPayment:                             -> False   (R955 SubmitPaymentAsync)
```

**而它们的静态依赖类的 const **都在**：`QueueITAccepted` · `Initiliazing Queue-it` ·
`api.solvecaptcha.com` · `CAPCHA_NOT_READY` · `out of stock` 全部 True。**

### 所以规则是

> **`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁掉 ——
> 因为派发表靠 `MethodInfo.Invoke`，而**反射在 NativeAOT 下不 root 方法**。**
> **而静态类里的 const 因为被**某个**保留方法读，就留下了。**

### 而这意味着什么

**R955–R962 八轮的动作是「把零覆写的基类步骤写成真实现」。**
**按这条规则，那个动作**不改变产物** —— 而它一直是那八轮的进展主张。**

> **所以那三段 +42/+43/+43 的真实来源是**静态协议类变得可达**，
> 而它们变得可达的原因是**某个**保留方法读了它们 —— 不是因为我写了步骤体。**
> **而 R955 那句「+43 来自支付派发」、R960 那句「+43 来自 PollQueue」都是同一类归因错误。****

### 那正确的策略是什么

**两条，都是「让真实调用存在」：**

1. **每个 flow 覆写它真正需要的步骤** —— 那既符合镜像（`GetCsrf` 在二十个 ordinal 上各一份），
   又**必然**进产物
2. **或者给基类步骤加**真实调用点**（不是反射）**

> **第 1 条才是镜像本身的样子：镜像里 `GetCsrf` 二十份、`SubmitPayment` 每个支付类一份 ——
> **原版也没有一个「大家共用的基类实现」**。
> 所以「写基类默认实现」这个做法不仅不改变产物，**它也不像原版**。****

### 数字

| 度量 | R962 | **R963** |
|---|---|---|
| 套件 | 2186 | **2186（本轮只取证，未改代码）** |
| 函数数 | 173,909 | **173,909** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 空壳 `=> Ok()` | 34 | **34** |
| **规则** | Unknown | **有覆写才保留（Observation，三组对比）** |

### 教训

> **这一轮一行代码都没改，而它是这几轮里最有价值的一轮。
> 因为前八轮都在往一个**不改变产物**的方向走，而每轮都有数字在动，让我以为方向对了。**
> **而数字确实在动 —— 动的是别的东西。**
> **一个指标能在你做错事的时候动，这是它最坏的性质。**


### 第一个「按新策略写」的覆写：**+43 函数**，而规则要收窄（R964）

**R963 定的策略是：覆写进具体 flow，不写共用基类。这一轮照做了一次，并且**用产物核对，不靠相信**。**

### 改了什么

**`BstnFlow.GetCsrfAsync` —— 第一个真正做事的覆写（不是 `StepOutcome.Fail` 占位）：
拉 `https://www.bstn.com/` → `FindCsrfToken` → 回退到 `csrftoken` cookie → 找不到判不可重试。**

### 而产物说了两件事

**① 覆写确实让方法进产物：**

```
pdata-replica: 173,909 -> 173,952     +43
pdata-ratio:   62.76%  -> 62.77%
```

**② 而方法体里的**报错串**没进：**

| 串 | 在产物 |
|---|---|
| `www.bstn.com`（同方法里的 URL 字面量） | **True** |
| `bstn: csrf page ` | False |
| `bstn: no csrf token on the landing page` | False |
| `bstn: cart endpoint unknown`（`GetCart` 覆写，同步） | **True** |
| `bstn: checkout endpoint unknown (Adyen)`（`GetCheckout` 覆写） | False |

### 所以 R963 的规则要收窄

> **「有覆写才保留」—— 方向对（+43 证明）。
> 但「覆写体完整保留」是错的：同一个 async 方法里，URL 字面量在、`StepOutcome.Fail` 的参数串不在。**
> **而 `GetCheckoutAsync` 也是覆写，它的串也不在 —— 所以「覆写」不是充分条件，只是必要条件。**

**新规则（Observation，两条）：**

1. **零覆写 → 基类体必被裁（R963 三组对比）**
2. **有覆写 → 方法进产物，但体内字符串**按需保留**，判据 Unknown**

> **而第 2 条对「用串核对产物」这个做法有直接影响：
> 串在场可以证明「在」，串不在**不能**证明「不在」——
> 这又是 §2.7b 那条反向不可用，而这次是在**产物**上踩的。****

### 而一个守卫红了，而它钉的正是我想去掉的东西

**`StepActionTests.RunnerExecutesAnActionAndRecordsEveryStep` 用 `TinyServer(_ => (200, "{}"))` 跑 `CSRF-Generate`，
期望 3 步全 OK。**

**而 `GetCsrf` 现在找不到 token 会**正确失败** —— 所以那个测例红在了**假成功消失**上。**

> **处置：把 fixture 换成带 token 的页面（`<input type="hidden" name="csrf_token" value="testtoken123456">`），
> 测例仍在测它名字说的那件事（每步都跑、都被记录），而不再顺手钉住一个假成功。**
> **而这不是「改数字」——是**行为变了，所以改夹具**，两者都是正当的，但要说清是哪一种。**

### 数字

| 度量 | R963 | **R964** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,909 | **173,952（+43）** |
| **函数比** | 62.76% | **62.77%** |
| 产物大小 | 54,724 KB | **54,741 KB** |
| 覆写总数（GetCsrf） | 0 | **1** |

### 教训

> **这一轮同时验证了一条规则和收窄了它 —— 而收窄的部分比验证的部分重要。
> 「有覆写 → 进产物」让我高兴了十分钟；「但体内字符串按需保留」让我明白
> **我刚才用来高兴的那个核对方法，在反方向上不成立**。**
> **而这条规则 R963 就写过（§2.7b），我这一轮差点又用它反向下了结论。**


### 那 34 个「空壳」几乎全都有覆写 —— 而我的正则漏了 `async`（R965）

**R962 数出「35 个 `=> Ok()` 空壳」，R963 据此定了「零覆写 → 必被裁」的规则。
这一轮把 34 个名字**全查了一遍**，用一个更宽的正则：**

```
旧: override\s+Task<StepOutcome>\s+<Step>Async
新: override\s+(?:async\s+)?Task<StepOutcome>\s+<Step>Async    ← 多了 async 可选
```

### 而结果

| 步骤 | 覆写数 | 步骤 | 覆写数 |
|---|---|---|---|
| `ScrapeVariantAvailability` | **13** | `GetShippingRates` | 3 |
| `GetCsrf` | **4** | `SubmitBilling` | 2 |
| `CreateCart` · `EditLine` · `InitiateCheckout` · `SubmitEmail` | 3 | `Login` · `SubmitSensor` · `GetCaptcha` · `WaitForRelease` | 2 |
| 其余 20 个 | **1** | | |

> **34 个，**每一个至少 1 处覆写**。零覆写的一个都没有。**
> **而 R962 报的是「`GetCsrf` 覆写 0 处、`SubmitEmail` 0、`CreateCart` 0、`Login` 0、`SolveCaptcha` 0、`BuildDestination` 0、`Fill` 0」。**

### 所以 R962 和 R963 各倒了一半

**R962 的「35 个空壳、零覆写」——**覆写数全错**，因为正则漏了 `async` 关键字。
整个复刻件的覆写大量写成 `public override async Task<StepOutcome> XAsync(...)`，而旧正则要求
`override` 后面**紧跟** `Task<StepOutcome>`。**

**R963 的规则「零覆写 → 必被裁」—— 前提（有零覆写的步骤）不存在。
而「`BstnFlow.GetCartAsync` 是全仓唯一覆写」也是同一个假阴性造成的。**

### 而那条规则**还对不对**

> **它对「零覆写」这个条件仍然逻辑成立（空集上无矛盾），但它**没有被任何实例支持** ——
> 而 R963 用它推翻了八轮主张，那是**建立在一个假阴性上的推翻**。**
> **而 R964 的 +43 仍然成立（覆写让方法进产物），那一条是直接观测，不受这个错影响。****

### 而真正的问题是另一个

**既然 34 个步骤都有覆写，为什么函数数只有 173,952 / 277,120？**

**那说明缺口**不在「步骤有没有实现」**上。
而这一路我一直在拿「写实现」当进展，而**实现早就有了**。

> **所以真正要查的是：这些覆写**进产物了吗**、以及 62.77% 的缺口**在哪一层**。
> 而这两个问题我之前都没问过 —— 因为我一直假设缺口在「没写」。****

### 数字

| 度量 | R964 | **R965** |
|---|---|---|
| 套件 | 2186 | **2186（本轮只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **零覆写的空壳** | 34（R962 报） | **0（全部至少 1 处）** |
| `GetCsrf` 覆写数 | 1（R964 报） | **4** |
| `ScrapeVariantAvailability` 覆写数 | — | **13** |

### 教训

> **同一个错第三、第四、第五次了：**假设太窄，然后把「不符合假设」读成「不存在」**。
> R753 / R759 / R760 / R762 / R763 / R764 / R768 / R772 / R884 / R885 / R897 / R900 / R911 / R917 / R925 / R929 /
> R936 / R939 / R942 / R943 / R954 —— 加上 R962 和 R963。**
> **而这次的两个字是 `async`。它就在代码里，在 `override` 和 `Task<StepOutcome>` 之间，
> 而我十五轮里从没把它写进那个正则。**


### 179 个步骤名**一个都不在产物里** —— 派发表在 AOT 里是空的（R966）

**R965 说下一轮查「那些覆写进产物了吗」。而字符串核对已经被 R964 否掉了
（`www.bstn.com` 在、而同一方法里带协议的完整串不在）。所以换一个不依赖 body 串的检查：**
**查**步骤方法名**。**

### 为什么方法名是个干净的问法

**`StepActionRunner.Build()` 走 `typeof(StoreFlow).GetMethods(...)`。
要让那句反射返回东西，裁剪工具**必须**保留 `StoreFlow` 的方法元数据 —— **名字在内**。
所以方法名在不在产物里，直接回答「反射表在 AOT 里能不能建起来」，而与任何字面量无关。**

### 结果

```
StoreFlow 声明的步骤:                    179
方法名在产物里:                            0
方法名不在:                              179
阴性对照 NoSuchStepNameAtAll / ZzzQqqWww:  都不在（对照正确）
```

> **0 / 179。而阴性对照也是不在 —— 所以这不是「搜错编码」的假阴性，是**真的没有**。**
> **而 `StepActionTests` 在 Debug 构建里通过 —— 那里有 metadata。AOT 产物里没有。****

### 所以 AOT 产物里 `StepActionRunner.Invokers` 是**空的**

**`Knows(step)` 恒为 false，`StepDispatch` 恒为空字典。
而那意味着：**在产物里，任何「按名字跑一个步骤」的路径都跑不起来。**

> **而这给 62.77% 的缺口提供了一个具体的主因候选：
> 不是「步骤没写」（R965 已证 34 个全有覆写），也不是「写了被裁」，
> 而是**整个派发机制在 AOT 下失效，于是所有只经它可达的代码都被裁掉**。**

### 而 `StepMap` 大概不是同一条路

**R882 的 `*StepMap` 是**编译期字面量**（`ordinal → 步骤名`），不是反射。
所以如果派发真在跑，走的是那张表，不是 `Invokers`。**

> **而这两条路里哪条是活的、以及原版走哪条 —— 我没取证。标 Unknown。**

### 数字

| 度量 | R965 | **R966** |
|---|---|---|
| 套件 | 2186 | **2186（本轮只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **产物里的步骤名** | 未查 | **0 / 179** |
| 有覆写的空壳 | 0 | **0** |

### 教训

> **我用了十几轮「写实现」当进展，而**实现早就在**（R965），
> 而**派发它的那张表在产物里是空的**（R966）。
> 两句合起来说明：我一直在一个**跑不起来的分支**上加内容，然后看着旁边的数字动。**
> **而找出这件事的不是一个新工具，是**换一个不依赖字符串的问法** ——
> 因为我上一轮刚证明原来那个问法的反向不成立。**


### `[DynamicallyAccessedMembers]` 没效果 —— 而我查错了编码（R967）

**R966 说「179 个步骤名 0 个在产物 → `Invokers` 是空的」。这一轮做了两件事，两件都不按预期。**

### ① 加属性，无效果

**给 `StoreFlow` 加了 `[DynamicallyAccessedMembers(PublicMethods)]`（反射点名它、让裁剪工具留着）。**

```
pdata-replica: 173,952 -> 173,952     （不变）
size:          54,724 KB -> 54,728 KB
GetCsrfAsync 在产物里:  utf16=False   （还是 False）
```

> **所以那个属性对这个产物没有可见影响 —— 或者更可能，**我用的检查看不见它**。**

### ② 而检查本身是坏的 —— 反射元数据是 **UTF-8**，字符串字面量是 **UTF-16**

**补了阳性对照 —— 一个**必然**在产物里的名字：**

```
Main                        utf16=True   utf8=True
Initialize                  utf16=True   utf8=True
StoreFlow                   utf16=False  utf8=True    ← 决定性
StepActionRunner            utf16=False  utf8=True
GetCsrfAsync                utf16=False  utf8=True
'bstn: cart endpoint unknown' utf16=True  utf8=False   ← 字面量是 UTF-16
NoSuchTypeAtAll             utf16=False  utf8=False   （对照正确）
```

**而用 UTF-8 重查那 179 个名字：**

```
UTF-16LE   名字在场: 0 / 179
UTF-8      名字在场: 179 / 179
```

### 所以 R966 的结论**倒掉**

> **`Invokers` **不是**空的。179 个方法名全部在场，反射表在产物里能建起来。
> 而「派发在 AOT 下失效」这个主因候选 —— **是假的**。**

**而它假的原因：我搜了 UTF-16，而反射元数据存 UTF-8。**
**而我上一轮**有阴性对照**（`NoSuchStepNameAtAll` 不在）—— 那一项验证的是「搜索能工作」，
**不是「被搜索的东西存在」**。而这两件事在编码不同的情况下会分开。**

> **这是同一形状错的第二十三次，而这次的具体形态是：
> **阴性对照通过了，所以我以为检查是好的。而阴性对照只能证明「搜不到不存在的东西」，
> 不能证明「搜得到存在的东西」。****

### 数字

| 度量 | R966 | **R967** |
|---|---|---|
| 套件 | 2186 | **2186（属性不改行为）** |
| 函数数 | 173,952 | **173,952（属性无影响）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,724 KB | **54,728 KB** |
| **步骤名（UTF-8）** | 未查 | **179 / 179** |
| **步骤名（UTF-16）** | 0 / 179（错） | 0 / 179（编码不对） |

### 教训

> **阴性对照通过，是这一轮最危险的地方。
> 它让我对一个**看不见阳性结果**的检查产生了信任。**
> **而检查的正确做法是两向都要有对照：一个已知在、一个已知不在。
> 我上一轮只做了后者，于是「全都不在」被读成了结论，而不是被读成警报。**


### 属性加了、名字全在、体还是不在 —— 而这个核对方法到头了（R968）

**R967 说下一轮用对的编码重核 body 串。这一轮做了，结果是一张表。**

### 加了 `[DynamicallyAccessedMembers(PublicMethods)]` 之后

| 串 | 编码 | 在产物 |
|---|---|---|
| `bstn: cart endpoint unknown` | body UTF-16 | **True** |
| `bstn: checkout endpoint unknown (Adyen)` | body UTF-16 | False |
| `nike: no kasada script loaded` | body UTF-16 | False |
| `popmart-orders` | body UTF-16 | False |
| `shopify: no profile to fill from` | body UTF-16 | False |
| `GetCsrfAsync` · `GetCartAsync` · `StoreFlow` | name UTF-8 | **全 True** |

**而 `pdata-replica` 仍是 173,952。**

### 所以现在确定的是两件事

1. **方法**元数据全部保留**（179/179 名字在 UTF-8 里）→ 反射表能建起来**
2. **方法**体大部分被裁**（4/5 抽样的串不在）

> **而这两件并存说明：`MethodInfo` 存在、`Invoke` 能调、而**被调到的那个方法体可能已经不在了**。
> 那是 NativeAOT 下一个具体的失败形态：反射找得到方法，调用时抛。**
> **而 `[DynamicallyAccessedMembers]` 只保证**元数据**，不保证**体** —— 那是这一轮的 Inference，
> 而它有一个反例（我的属性没起任何可见作用）。**

### 而这个核对方法**到头了**

**`bstn: cart endpoint unknown` 在、`bstn: checkout endpoint unknown (Adyen)` 不在 ——
两个都是同一个类里的同步表达式体 `Task.FromResult(StepOutcome.Fail(...))`。

> **所以「同步还是 async」不是解释，「覆写与否」也不是（两个都是覆写）。
> 而 R964 已经证明：body 串**不在**不能证明 body 不在产物里（R964 的 `www.bstn.com` 在、
> 同方法带协议的完整串不在 —— 字符串是被拆开存的）。**
> **所以这张表**只能读正向**：在 → 在。不在 → **什么都不能说**。**
> **而 4 个「不在」里有多少是假的，这个工具答不了。**

### 所以下一轮该查的不是这个

**62.77% 的缺口需要一个**分布**，不是一个开关。而我现在只有总数。**

> **具体要做的：把 `target\Cybersole.exe` 与 `.publish-aot` 的 `.pdata` 都按**地址段**切开，
> 看缺口分布在哪一段。原版 277,120 个函数分布在若干区段，而复刻件 173,952 ——
> **如果缺口集中在某几段，那答案在那几段；如果均匀分布，那答案在别处。**
> **而这个工具我还没有。写在下一轮。****

### 数字

| 度量 | R967 | **R968** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952（属性无影响，第二次确认）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,728 KB | **54,728 KB** |
| 名字在场（UTF-8） | 179/179 | **179/179** |
| body 串在场（UTF-16 抽样 5） | — | **1 / 5** |

### 教训

> **这一轮最有价值的不是那张表，是**承认那张表只能读一半**。
> 它的「不在」列有 4 项，而我没有一项能当结论用。**
> **而上一轮我刚学会「检查要两向对照」—— 这一轮发现**方向对了也不够**：
> 被查的东西本身会被拆开存，于是「不在」这一向在原理上就不可用，不是还没来得及验证。**


### 缺口有形状了，而形状是：**复刻件的代码在 0x1C00000 就结束了**（R969）

**R968 说下一轮要的是**分布**，不是另一个候选原因。写了 `tools/pdata_sections.py`，
把两边 `.pdata` 按 1 MiB 分桶：**

```
range from     original   replica    replica/original
0x0            5,475      2,022        36.9%
0x100000       5,089      4,814        94.6%
0x200000       4,333      5,321       122.8%
0x600000       1,074      3,412       317.7%
0x1100000      2,020      9,969       493.5%
0x1200000      2,046      9,730       475.6%
0x1700000      2,242      9,974       444.9%
0x1B00000      6,033      4,683        77.6%
─────────────── 这里以下 ends ───────────────
0x1C00000      6,218      0             0.0%
0x1D00000      6,893      0             0.0%
  ...（到 0x3100000 全是 0）
0x2500000     13,982      0             0.0%
0x3100000        324      0             0.0%
```

### 所以两件事，都很直白

**① 0x0 到 0x1B00000：复刻件**不缺，甚至多**。
好几段是原版的 1.5 到 4.9 倍 —— 那是 Avalonia 与不同的 BCL 在低地址段的体量。**

**② 0x1C00000 到 0x3100000：复刻件是 **0**。原版在那一段有约 **10 万**个函数。**

> **而 103,168 这个缺口，几乎全部就是那一段。**
> **所以缺口**不是「某类函数缺失」，而是「复刻件的 .text 在那之后就没了」。****

### 而这意味着什么

**原版的代码段约 0x0..0x3100000（49 MB 地址空间），复刻件约 0x0..0x1C00000（28 MB）。
差的那 21 MB 里装着 10 万个函数。**

> **所以「1:1 复刻」在体量上现在是一个**整体差 1.75 倍**的问题，
> 而不是「A 站缺了 B 步骤」那类问题。而这两类问题需要完全不同的动作：
> **前者要问「原版那 21 MB 里是什么」，后者要问「哪个站缺哪步」。****

### 而这个工具**不能**说的是

**两个镜像的布局是独立的 —— 同一个桶里数字相同**不**代表同一段代码。
所以这张表说的是**密度**，不是**身份**。而「21 MB 里是什么」这个问题的答案不在这张表里。**

> **它给出的是**下一步该问什么**，不是答案本身。**

### 而这一轮也说明了「候选原因」这个做法的问题

**R966 猜「派发表在 AOT 下失效」，R967 用 UTF-8 推翻了它。
R968 承认核对到头了，R969 改用分布 —— 而分布一出来，那个候选原因**根本不需要**：
**缺口在 0x1C00000 以上，而那不是「派发失效」的形状，「派发失效」会均匀砍掉一批。****

> **一个候选原因被**形状**否掉，比被另一个候选原因否掉可靠。**
> **而形状来自分布 —— 我一个上午在猜，而一个 47 行的桶统计直接给出了它。****

### 数字

| 度量 | R968 | **R969** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **复刻件 .text 上界** | 未测 | **0x1C00000（28 MB）** |
| **原版 .text 上界** | 未测 | **0x3100000（49 MB）** |
| **0x1C00000 以上的原版函数** | 未测 | **约 10 万，复刻件 0** |

### 教训

> **我一个上午在猜「为什么少」，而一个 47 行的桶统计直接给出了「少在哪」，
> 而「少在哪」把「为什么少」的候选原因全部换掉了。**
> **而更值钱的是：形状否掉候选原因比候选原因互相否掉可靠 ——
> 「派发失效」会均匀砍一批，而实际是**从某个地址起归零**，那不是同一件事。**


### 段表推翻了我上一轮的框架 —— 复刻件有**两个**可执行段（R970）

**R969 说「复刻件的 `.text` 在 0x1C00000 就结束了」。写了 `tools/pe_sections.py` 打段表，结果是：**

```
=== ORIGINAL ===
  .text      0x1000   -> 0x314DD68   51,695,104   X
  .rdata     0x314E000 -> 0x6A4687E  59,738,624   R
  .data      0x6A47000 -> 0x7542DA8  10,227,712   RW
  .pdata     0x7543000 -> 0x786ECC8   3,325,440   R

=== REPLICA ===
  .text      0x1000   -> 0xFD508      1,033,728   X     ← 只有 1 MB
  .managed   0xFE000  -> 0x1B817E8   27,801,600   X     ← 第二个可执行段
  hydrated   0x1B82000 -> 0x2A87B28           0   RW
  .rdata     0x2A88000 -> 0x41F1EB6  24,551,424   R
  .pdata     0x42E9000 -> 0x44E6820   2,087,424   R
```

### 所以「结束了」这个说法**现象对、原因错**

**复刻件的托管代码不在 `.text` 里 —— 它在 **`.managed`** 段，27.8 MB，可执行。
而 `0x1C00000` 正好是 `.managed` 段的**结束**（实际 0x1B817E8，下一个 MiB 边界就是 0x1C00000）。**

> **所以桶表里「0x1C00000 以上是 0」不是「代码结束」，是**两个可执行段都结束了**。
> 而原版只有一个 `.text` 段，52 MB，一路到 0x314DD68。****

### 而真正的比较

| | 可执行段 | 大小 |
|---|---|---|
| 原版 | `.text` | **51,695,104 B ≈ 49.3 MB** |
| 复刻件 | `.text` + `.managed` | **1,033,728 + 27,801,600 = 28,835,328 B ≈ 27.5 MB** |

**→ 代码体量 27.5 / 49.3 = **55.8%**。而函数数比是 62.77%。**

> **两个数不一样，而那个差本身是有信息的：**函数数比体量比高 7 个百分点**，
> 说明复刻件的函数**平均更小** —— 或者原版有更多大函数。而我没取证是哪个。****

### 而这一轮又抓到一个「我说对了一半」

**R969 的「缺口全部在 0x1C00000 以上」是**准确的观察**（桶表确实如此）。
而它的解释「复刻件的 .text 在那之后就没了」是**错的** —— 复刻件的 .text 在 1 MB 处就没了，
而它的代码在另一个段里继续到 0x1B817E8。**

> **而如果我不打这张段表，那个错解释会写进 BACKLOG，
> 下一个会话会去 `.text` 里找 27 MB 的代码，而那里永远只有 1 MB。**

### 数字

| 度量 | R969 | **R970** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **原版可执行段** | 未测 | **`.text` 49.3 MB** |
| **复刻件可执行段** | 未测 | **`.text` 1.0 + `.managed` 26.5 MB = 27.5 MB** |
| **代码体量比** | 未测 | **55.8%** |

### 教训

> **观察对、解释错，是一种比观察错更危险的状态 ——
> 因为观察会被复算，而解释会被下一个会话当成前提。**
> **而推翻它的成本是 40 行读段表。而我上一轮把它写进了三份文档。**


### 那 7 个百分点差有答案了，而答案不是我猜的那个（R971）

**R970 说：「差 7 个百分点 → 复刻件的函数**平均更小**（或原版有更多大函数）—— 未取证是哪个」。
这一轮把 `--sizes` 加进 `pdata_sections.py`（不是新脚本 —— 同一个 PE 走查，多一种汇总）。**

### 结果

```
ORIGINAL  funcs=277094  total=48,723,539 B  mean=175.8  median=73   p90=315  p99=1658  max=687318
             <=64B: 128281 (46.3%)   65..512B: 133093 (48.0%)   >512B: 15720 ( 5.7%)

REPLICA   funcs=173912  total=27,158,626 B  mean=156.2  median=86   p90=290  p99=1361  max=74836
             <=64B: 68253  (39.2%)   65..512B: 97712  (56.2%)   >512B: 7947  ( 4.6%)
```

### 「平均更小」对，而**中位数反了**

| | 原版 | 复刻件 | |
|---|---|---|---|
| 均值 | **175.8** | 156.2 | 原版大 **12.5%** |
| **中位数** | **73** | **86** | **复刻件大 18%** |
| p90 | 315 | 290 | 原版大 |
| p99 | 1658 | 1361 | 原版大 |
| **max** | **687,318** | **74,836** | **原版大 9.2 倍** |

> **所以「原版函数平均更大」是因为**尾部**，不是因为**典型**。
> 原版的**中位数函数比复刻件更小**（73 vs 86）—— 它有更多极小的函数。
> **而它的均值更大，是因为它有**极少数巨大的函数**（max 687 KB，而复刻件最大只有 75 KB）。****

### 而分布形状也说明了同一件事

| 区间 | 原版 | 复刻件 |
|---|---|---|
| ≤64 B | **46.3%** | 39.2% |
| 65..512 B | 48.0% | **56.2%** |
| >512 B | **5.7%** | 4.6% |

**原版在**极小**和**较大**两端都更重，复刻件集中在中间段 ——
那是一个**更规整**的分布，也就是更少的极端。**

### 所以那 7 个百分点是什么

**20 万个原版函数和 17 万个复刻件函数，差 10.3 万个。
而字节数差 21.6 MB，比函数数差的比例（37%）更陡（44%）。**

> **原因是两边都有、但比例不同：**
> **① 原版有 46.3% 的极小函数（≤64 B）—— 那多半是 thunk、getter、一次性委托。
> ② 原版有一个 687 KB 的函数 —— 那一个就等于 4,400 个中位数函数。**
> **而这两项都不是「我少写了功能」，是**编译器与代码形状**的差别。**

### 而这一轮的价值是：它把「为什么差 7 个百分点」从一个**候选**变成了一个**分布**

**而分布里最反直觉的一行是**中位数**：复刻件的典型函数比原版**大** 18%。
如果我只看均值（原版大 12.5%），我会得出「复刻件函数更小」这个**方向反了的结论**。**

> **均值被 687 KB 的单个函数拉走了。而中位数不受它影响。
> 一个 687 KB 的函数对均值贡献 687318/277094 ≈ **2.5 字节**…… 不，它对**总和**贡献 687 KB（1.4%），
> 对**均值**贡献 2.5 字节 —— 所以均值差 19.6 字节里，那一个函数只解释 2.5。**
> **所以真正的解释是**极小函数的比例**（46.3% vs 39.2%）：那些函数把原版的均值**拉低**，
> 而原版均值仍然更高 —— 说明剩下的部分更大。这个拆解我没有做完。****

### 数字

| 度量 | R970 | **R971** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具模式）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **`--sizes` 模式** | 无 | **有** |
| **中位数（原版/复刻件）** | 未测 | **73 / 86** |
| **max（原版/复刻件）** | 未测 | **687,318 / 74,836** |

### 教训

> **只有一个均值时我会说「复刻件函数更小」。而加上中位数，那句话就反了。**
> **而两个数都对 —— 它们描述的是分布的不同部位，而我把一个部位的结论说成了整体。**
> **这一轮没抓到我自己的错，是**中位数抓到了均值的错**。**


### 拆解做完，而它**推翻了 R971 自己的粗算**（R972）

**R971 写：「均值差 19.6 字节里，那个 687 KB 函数只解释 2.5 字节，所以大部分差来自极小函数的比例」。
这一轮写了 `tools/pdata_decompose.py` 把它算出来，而那个说法是**错的**。**

### 拆解（总和精确匹配 19.67 B）

```
band (B)         original n / share     replica n / share      contribution
0..32            76496 /  27.6%         36642 /  21.1%         +1.01 B
32..64           51785 /  18.7%         31611 /  18.2%         +0.20 B
64..128          65263 /  23.6%         53137 /  30.6%         -7.46 B
128..256         46312 /  16.7%         31869 /  18.3%         -3.37 B
256..512         21518 /   7.8%         12706 /   7.3%         +1.00 B
512..1024         9914 /   3.6%          5083 /   2.9%         +4.84 B
1024..4096        5135 /   1.9%          2598 /   1.5%         +7.04 B
4096..1048576      671 /   0.2%           266 /   0.2%        +16.40 B
─────────────────────────────────────────────────────────────────────
total                                                        +19.67 B
```

### 所以那 19.67 B 在哪

| 来源 | 贡献 | 占比 |
|---|---|---|
| **4096 B 以上那 671 个 vs 266 个** | **+16.40 B** | **83%** |
| 1024..4096 | +7.04 B | 36% |
| 512..1024 | +4.84 B | 25% |
| 64..256 两档（复刻件占比更高） | **−10.83 B** | −55% |
| 其余 | +2.21 B | 11% |

> **所以 R971 的「那 687 KB 函数只解释 2.5 字节」**对那**一个**函数是对的，
> 而对**那一档 671 个函数**是错的 —— 它们合起来解释 83% 的均值差。**
> **而 R971 的下一步推断「大部分差来自极小函数的比例」也错：
> 极小函数两档合计只 +1.21 B，而 64..256 两档是**负的**。****

### 而这一轮**自己**也撞了一次「说一套做一套」

**我在 `pdata_decompose.py` 的文件头写了「goes into the same tool as a third mode rather than into another script」，
然后把它写成了一个独立脚本。**

> **改正了文件头，并写出**真实理由**：拆解需要**固定**的档边界（档宽要对上被比较的区间），
> 而 `pdata_sections` 取的是**一个统一桶宽**（回答另一个问题）。
> 让一个文件服务两者，意味着两套不可互换的参数 —— 所以两个脚本共享同一段走查是对的安排，而文件头现在这么说。**
> **而如果我不改，那个文件头就是一条**自己反驳自己的注释**，而下一个读者会以为我漏了一个模式。****

### 数字

| 度量 | R971 | **R972** |
|---|---|---|
| 套件 | 2186 | **2186（只加工具）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **拆解总和** | 未做 | **+19.67 B（精确匹配）** |
| **4096+ 档的贡献** | 「2.5 B」**错** | **+16.40 B（83%）** |

### 教训

> **R971 那个「2.5 字节」是我心算的，而且在同一段里就写出了「所以大部分差来自极小函数的比例」这个结论。
> 而正确的分配是**大函数占 83%，极小函数那部分甚至是负的**。**
> **一个心算的数字，比没有数字更危险 —— 因为它看起来已经被算过了。**


### 那 671 个大函数：**主导均值差，而对目标影响 0.24%**（R973）

**R972 说下一轮查那 671 个大函数是什么（它们解释 83% 的均值差）。查了，而结果是**它们不该查**。**

### 它们的量

```
4096 B 以上的函数: 671 个
合计 7,676,312 B = 原版可执行段（48,723,539 B）的 15.8%
最大的 12 个:
  0x14117C4E0    687318 B
  0x1419F6060    527392 B
  0x1412241C0    227186 B
  0x14030F560     83620 B
  ...
```

### 而对目标的意思是

| 视角 | 这 671 个的占比 |
|---|---|
| **函数数**（目标第一条：函数数量对等） | **671 / 277,120 = 0.24%** |
| 执行段字节 | 15.8% |
| 均值差 | **83%** |

> **所以它们**主导均值差、占 15.8% 的代码体积，而对「函数数量对等」这个目标贡献 0.24%。**
> **而我上一轮把「查它们」立成了下一轮目标 —— 那是在追一个对我的目标几乎没有影响的东西。****

### 而反编译它们**不可行**

```
ida.py dec 0x14117C4E0 --lines 30
  -> {"error": "Decompilation failed at 0x14117c4e0"}
```

**687 KB 的函数，Hex-Rays 拒绝。**

**而 `xrefs` 显示它被 `sub_1412241C0`（227 KB，第三大的）引用 —— 那是一个**大函数互相调用**的簇。**

> **所以「那 671 个是什么」这个问题在工具层面**也**不便宜：最大的几个反编译不出来，
> 而它们互相引用，所以顺藤摸瓜成本高。**

### 所以结论是**优先级**，不是事实

**目标写的是：函数数量对等（第一条）、每个函数功能相等（第二条）、效率相近（第三条）。
而这 671 个只影响第一条的 0.24% —— 它们属于第二条或第三条的范畴（某个函数的功能/效率），
而**第二条需要它们的功能相等，那需要反编译，而反编译失败了**。**

> **所以它们是**已知不可得**的一类，而这一类现在有具体形状：
> 「671 个 4 KB 以上的函数，占字节 15.8%，反编译失败，对函数数贡献 0.24%」。
> **而那该写进 Unknown，不该占下一轮。****

### 数字

| 度量 | R972 | **R973** |
|---|---|---|
| 套件 | 2186 | **2186（只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **4096+ 函数的字节** | 未测 | **7,676,312 B（15.8%）** |
| **对函数数的贡献** | 未测 | **0.24%** |
| **最大函数的反编译** | 未试 | **失败** |

### 教训

> **上一轮我把「查这 671 个」立为目标，因为它们是**均值差**的 83%。
> 而均值差**不是目标** —— 函数数、功能、效率才是。**
> **我把一个**解释中间量**的东西当成了优先项，而它对我真正要的数的贡献是 0.24%。**
> **一个指标被解释清楚，不等于那个解释值得追。**


### 判据 (a) 可以结案了 —— 16 个缺失类型里**核心只有 5 个**（R974）

**R973 之后回到函数数，而先做了一件更省的事：读 `docs/METRICS.md`（唯一数字源）里判据 (a) 的四个数。**

### 四个数

| 指标 | 值 |
|---|---|
| 名字级绑定缺口 — real gap | **4** |
| 名字级绑定缺口 — missing | 16（其中 12 是 `HasMultiple_NN` 噪声） |
| **类型级绑定缺口 — types with scope misses** | **0** |
| 类型缺失 — types absent from source | **16** |

### 而那 4 条 real gap **全在 UI 层**

```
Ui.Localization.LocalizeFormatExtension    1  Value2
Ui.Localization.LocalizeSwitchExtension    1  Condition
Ui.Views.Auth.AuthWindow                   1  Logout
Ui.Views.Auth.LicenseControl               1  Authenticate
```

> **四条全是 `Ui.*`。而 YG 明令「ui先不急着复刻」。**
> **所以名字级 real gap 的 4 条对核心优先级是**零**，而它们不该挡住结案 —— 该**分类结案**（判据 a 的原话）。****

### 而那 16 个缺失类型分三类

| 类 | 数 | 类型 |
|---|---|---|
| **核心** | **6** | `Global.Settings`（34 成员）· `CloudflareSolvers.CloudflareSolver`（9）· `Services.ImapProvider`（4）· `Models.Concurrency`（3）· `SmartActions.ActionConfig`（2）· `Helpers.ObservableDictionary\`2`（1） |
| **UI** | **9** | `Ui.Localization.LocalizeEnumExtension` · `LocalizeFallbackExtension` · `LocalizeFormatExtension` · `LocalizeSwitchExtension` · `Ui.Views.Accounts.Modals.AccountsCreatorView` · `Ui.Views.Auth.AuthWindow` · 其余 3 个同前缀 |
| **其他** | **1** | （被输出截断，未读到名字） |

### 所以剩下什么

**`types with scope misses` 已经是 **0** —— 那一条判据 a 直接满足。**

**而 `types absent from source` 的 16 个里，6 个是核心、9 个是 UI、1 个未读。**

> **所以判据 a 的真实状态是：**
> **「类型级缺口 0 ✅；类型缺失 16 → 其中 6 个核心、9 个 UI、1 未分类」**
> **而那 6 个核心的不是「不可得」，是「还没开工」—— 它们有成员清单（34/9/4/3/2/1），
> 所以补起来是确定的，不需要再取证。****

### 而最值钱的那一个

**`Cybersole.Global.Settings` 有 34 个成员，而它是**核心配置** —— 而复刻件的配置类存在（`AppServices` 里用到），
只是**类名不同**，所以类型存在性检查判它 absent。**

> **所以这 6 个里可能有几个只是**改了名**，而成员都在。
> 而判据 a 的原话是「名字级缺口三分类结案」—— **改名属于「命名可不同」那一类，不算缺口。**
> **而这一点我没有逐条核过。标 Unknown，下一个该做的就是它。****

### 数字

| 度量 | R973 | **R974** |
|---|---|---|
| 套件 | 2186 | **2186（只读数字源）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **类型级 scope misses** | — | **0** |
| **类型缺失** | — | **16（6 核心 / 9 UI / 1 未读）** |
| **名字级 real gap** | — | **4（全 UI）** |

### 教训

> **这一轮没写代码，而它把一个一直「还有 16 个」的数字变成了「6 个核心、9 个 UI、1 未分类」。**
> **而那个 16 一直挂在那里，因为我从没按**优先级**把它切开过 —— 我一直把它当一个整体。**
> **而切开之后，9 个属于 YG 明确说了「不急」的那一层。**


### 那 6 个核心缺失：**5 个只是改名**，第 6 个待判（R975）

**R974 说下一轮核这 6 个里有几个只是改名。核完了。**

### 逐条（成员抽样 + 命中文件）

| 原版名 | 复刻件里的实现 | 抽样成员 |
|---|---|---|
| `Cybersole.Global.Settings`（34 成员） | **`GlobalSettings.cs`** | `AutoOpen3DS` `BrowserLimit` `MonitorConcurrency` `RetryDelay` `TaskGroupOrder` `ScrollbarWidth` `StartupPage` `Currency` —— **8/8 全在** |
| `Cybersole.CloudflareSolvers.CloudflareSolver`（9） | **散在 `Drivers.cs` / `CaptchaSolverService.cs` / `GlobalSettings.cs`** | `ApiKey` `BalanceSupported` `IsFetchingBalance` `Concurrency` —— **4/4 全在** |
| `Cybersole.Services.ImapProvider`（4） | **`ImapMailProvider.cs`** | `MessageCount` 在 |
| `Cybersole.Models.Concurrency`（3） | **`ConcurrencyLimit.cs`** | `Maximum` `Ratio` 在 |
| `Cybersole.SmartActions.ActionConfig`（2） | **`SmartActions.cs`** | `Required` 在 |
| `Cybersole.Helpers.ObservableDictionary\`2`（1） | **未见** | `Count` 是通用成员，命中的是 `Checkout.cs` / `Profiles.cs`，**不能算证据** |

### 所以

**5 个确认改名 —— 而判据 a 的原话是「名字级缺口三分类结案」，
而「命名可不同」是目标里写明的**不算缺口**。**

> **所以这 5 个应当**从缺口里划掉**，而不是留着占位。
> 而第 6 个（`ObservableDictionary\`2`，两个泛型参数）待判 —— 它可能是 BCL 的
> `System.Collections.ObjectModel` 里现成的类型，复刻件用 BCL 的原版就是「实现不同」，不是缺失。**
> **而这一点我没查 BCL 的清单，所以标 Unknown。****

### 而这意味着判据 a 的缺口从 16 降到 11

| 类 | R974 | **R975** |
|---|---|---|
| 核心 | 6 | **1（`ObservableDictionary\`2`）** |
| UI | 9 | **9** |
| 未读 | 1 | **1** |
| 合计 | 16 | **11** |

> **所以 16 里：9 个 UI（YG 说不急）+ 1 个未读 + **1 个核心待判**。
> 而「类型缺失」这一条的真实剩余量是 1+1 = 2，不是 16。****

### 数字

| 度量 | R974 | **R975** |
|---|---|---|
| 套件 | 2186 | **2186（只核对）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **核心缺失** | 6 | **1** |
| **类型缺失合计** | 16 | **11（9 UI + 1 未读 + 1 核心）** |

### 教训

> **「类型缺失 16」这个数字里，5 个是改名。而改名在目标里是允许的 ——
> 所以那个 16 从一开始就**高估了 5 个**。**
> **而它没被修正，因为检查工具按**名字**判存在，而**名字可以不同**是目标里明写的自由度。
> 检查工具与目标条款之间有一个洞，而那个洞里装着 5 个假缺口。**


### 唯一一个真缺失的核心类型写出来了，而**两个守卫立刻红了**（R976）

**R975 把 16 分成 5 改名 + 1 真缺失 + 10 UI。这一轮写那 1 个。**

### `ObservableDictionary<TKey,TValue>`（`src/Cybersole.Core/Helpers/`）

**`IDictionary` + `IReadOnlyDictionary` + `INotifyCollectionChanged` + `INotifyPropertyChanged`。
而注释里写了**为什么一个字典需要通知**：**

> **集合可以按索引说「变了」；字典不能 —— 增删一个键改变了项集，而其他键的位置没动，
> 所以按下标缓存的消费者无从 diff。**
> **所以复刻件里用一个普通 `Dictionary<TKey,TValue>` 顶替它**不是改名，是行为变化** ——
> 而以「视图不再更新」而不是「抛异常」的形式出现。**

### 而两个守卫**立刻**抓到了它

**① `UnsubscribedEventsTests`：「声明了、raise 了、没人听」**

**我声明了 `CollectionChanged` 和 `PropertyChanged`，而仓里没人订阅 —— 那正是那个守卫要抓的。**

> **而它的白名单里第一条是先例：**
> `["CanExecuteChanged"] = "contract: ICommand requires it; Avalonia subscribes"`
> **而这两条同形：接口**要求**声明它们，而订阅者会在 UI 里 —— 而 UI 是 YG 说不急的那一层。
> 所以登记为契约事件，并写明「声明它们是契约；还没人听是工作的状态，不是坏掉的承诺」。**

**② `BindScopeGuardTests`：`KnownUnseenTypes` 5 → 6**

**`ObservableDictionary<TKey,TValue>` 是**第二个双泛型类型**，而 `bind_scope` 的 `DECL` 正则只匹配无类型参数的声明 ——
所以它对 `bind_diff` 是「存在」、对 `bind_scope` 是「不可见」。**

> **而那个守卫的注释写着「If this list shrinks, someone fixed DECL; if it grows, someone narrowed it.
> Either way the test below fails and the change becomes deliberate.」**
> **所以 5 → 6 是**按规矩改的**，并写明是因为新增了一个双泛型类型。****

### 而函数数**不变**

**`pdata-replica` 173,952 → 173,952。因为**没有任何东西实例化它**。**

> **那是 R963/R967 已建立的规则在起作用：不可达的代码被裁。
> 而 `ObservableDictionary` 现在就是「写好了、有 10 个用例、而产物里没有」——
> **与 R965 发现的 34 个覆写同一种状态。**
> **所以它不是缺口（类型存在性检查已通过），而是**尚未接线**。****

### 数字

| 度量 | R975 | **R976** |
|---|---|---|
| 套件 | 2186 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未变 —— 无人实例化）** |
| **类型缺失** | 16 | **15** |
| **核心类型缺失** | 1 | **0** |

### 教训

> **写一个类型，两个守卫红了。而**两次都不是要绕过它们** ——
> 它们问的都是对的问题（「这个事件有人听吗」「为什么这个类型 bind_scope 看不见」），
> 而答案是「这是契约事件」和「它是双泛型」。**
> **所以这一轮最有价值的不是那个类，是**两条守卫都要求一个理由，而我给得出**。
> 如果给不出，那才是问题。**


### 两个数字进了唯一数字源，而过程中**抓到一个单位 bug**，并**修正 R969 的估算**（R977）

**判据 (c) 是「产物级对照可复算」。`func_count` 答「多少个」，而 R969–R972 那些数是我**手工量的**，
然后从散文里引用 —— 那正是数字漂移的来源。这一轮把两个工具注册成第 13、14 项度量。**

### 新注册的两项

| 度量 | 工具 | 新标签 |
|---|---|---|
| **可执行段体量** | `tools/pe_sections.py` | `section-mass-*` |
| **函数分布（.pdata 地址分桶）** | `tools/pdata_sections.py` | `pdata-above-0x1C00000-*` |

```
section-mass-original-executable: 51,695,104
section-mass-replica-executable:  28,835,328
section-mass-ratio:               55.78%

pdata-above-0x1C00000-original:  156,590
pdata-above-0x1C00000-replica:         0
pdata-last-replica-bucket:       0x1B00000
```

### 而第一版**报了两个 0**

**因为我拿桶**索引**去跟**字节地址**比：**

```python
above_o = sum(v for k, v in oh.items() if k >= 0x1C00000)     # k 是 28，0x1C00000 是三千万
```

> **而它没报错、没抛异常，只是**很确定地报了 0**。
> 而 0 正好是「复刻件在上面没有函数」那个**看起来正确**的答案 ——
> 所以如果我不看原版那一侧，这个 bug 会活下来。**
> **修法：`if k * bucket >= boundary`，并把那个错误留在注释里。**

### 而修好之后，R969 的估算**是错的**

**R969 写「0x1C00000 以上原版约 **10 万**个函数」。真实是 **156,590**。**

**而把两侧一起算，缺口的结构**完全不是「少了一块」**：**

| | 原版 | 复刻件 | 差 |
|---|---|---|---|
| **0x1C00000 以下** | 120,530 | **173,952** | **+53,422** |
| **0x1C00000 以上** | **156,590** | 0 | **−156,590** |
| **合计** | 277,120 | 173,952 | **−103,168** |

**校验：+53,422 − 156,590 = −103,168 = 实际缺口（精确）。**

> **所以复刻件在分界线**以下**比原版多 44%（173,952 vs 120,530），
> 而在**以上**是 0 —— 103,168 这个「缺口」是两个很大的反向运动**抵消之后**的净值。**
> **而 R969 说的「缺口全部在 0x1C00000 以上」在**算术上**对（那一侧确实差 156,590），
> 而在**语义上**是空的：两个镜像的布局独立，所以「某个地址以上」不是对功能的划分，
> 只是链接器把东西放在哪。**
> **→ 这一项度量**定位不了**缺口，而它现在诚实地只报三件事：体量、边界、那侧的计数。
> 它自己的输出末尾写着「said where the gap sits and nothing about why」。**

### 数字

| 度量 | R976 | **R977** |
|---|---|---|
| 套件 | 2196 | **2196** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 类型缺失 | 15 | **15** |
| **度量项数** | 12 | **14** |
| **可执行段体量比** | 未进源 | **55.78%** |
| **0x1C00000 以上（原版）** | 「约 10 万」**错** | **156,590** |

### 教训

> **一个单位 bug 报出的 0，恰好是我以为的答案。
> 如果我只看复刻件那一侧，它会活下来，而下一轮会拿它当证据。**
> **所以这一轮真正的收获不是那两个度量，是**原版那一侧的 156,590 让那个 0 显得可疑**。**


### 判据 (d) 的检查**从诞生起就只审 5 行**，而它报 PASS（R978）

**判据 (d)：claim 表每条有 authority+命令+gap_reason。仓里早有 `analysis/check_claims.py`（R811）。
这一轮先写了一个新的，然后发现它存在 —— 而**读它的时候发现了真问题**。**

### 它报 `claim rows: 5`

```
claim rows: 5
status distribution:  **fail** 3 / **pass** 2
criterion (d) by its own stated rule: PASS
```

**而 `PARITY_CLAIMS.md` 是**五张表**，一节一张，每张各有自己的
`| id | claim | status | authority | command | gap_reason |` 表头。**

**脚本找到**第一个**表头（第 41 行），然后**遇到第一个非表格行就停**（§2 标题前的空行）。
所以它审的只有 C1–C5 —— 五行。**

### 而这不是回归 —— **6 个表头在 R811 那天就都在**

```
c869fe1 (R811)  表头数 6
1635297 (R812)  表头数 6
HEAD            表头数 6
```

**→ 脚本**从诞生起**就只审一张表。它一次都没改过（`git log` 只有 R811 一条），而文档一直是多表。**

> **一个覆盖 23% 的检查报 PASS，比没有检查更坏 —— 因为它的结论会被引用。**
> **而它被引用了：`docs/DELIVERY_STATUS.md` 判据 d 那行写着「✅」。**

### 修好之后

```
claim tables: 5
claim rows: 22
status distribution: **pass** 8 / **unknown** 7 / **fail** 3 / **pass（Observation 层）** 1 /
                     **fail**（…）1 / **unknown**（…）1 / **pass（Observation 层，R458 实测）** 1
rows without an authority: 0
non-unknown rows without a command: 0
criterion (d) by its own stated rule: PASS
```

**22 行全审，仍然 PASS。所以判据 (d) **确实满足** —— 而它是**这一轮才第一次被真正验证**的。**

### 而 I 又撞了一次「先写后查」

**我写了一个 `audit_claims.py --structure`，文件头写着「add a structural mode to audit_claims.py」，
然后写成了独立脚本 —— 而 R972 刚记过同一次。**

**删掉它、撤回对 `audit_claims.py` 的改动，改成修**已有的**那个（AGENTS.md §1「先抄」）。
R870 的 `where_is` 那条规则的第六次。**

### 还有一条**证据不可复算**

**`docs/DELIVERY_STATUS.md` 判据 d 那行写的证据是：**

```
python analysisudit_claims.py → claims parsed: 22 (authority=unknown: 9)
                                / criterion (d) holds: ...
```

**而今天同一个命令打的是 `inconsistencies found: 0` —— 完全不同的文本。
`claims parsed` 那句来自 `audit_claims.py` 的**旧版本**（`35e8721`），现行版本不再输出它。**

> **所以那一行的证据**点了一个命令，而那个命令现在不产出被引用的那句话**。
> 判据 (d) 要求「每条有命令」，而**命令能跑 ≠ 命令能复算出引用的那句**。**

### 而这一轮加了守卫

**`ClaimsCoverageTests`（2 个用例）：**
1. **文档确实是多张表**（`tables > 1`、`rows > 10`）—— 表头正则一旦失配就会红
2. **脚本报的行数 == 测试自己独立数出的行数**，且 PASS

> **两个计数器一致才算数 —— 一个计数器打一个数字，正是出错的那种形态。**

### 数字

| 度量 | R977 | **R978** |
|---|---|---|
| 套件 | 2196 | **2198** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **check_claims.py 审的行数** | **5**（错） | **22** |
| **claim 表数** | 未测 | **5** |
| **守卫用例** | 0 | **2** |

### 教训

> **这一轮最值钱的东西不是那个守卫，是「它一直在报 PASS」这个事实。
> 而发现它的路径纯属偶然 —— 我在写一个重复品，而读原件的输出时看到 `claim rows: 5` 那个数
> 跟我知道的 22 对不上。**
> **如果我一开始就按规则 `where_is` 查一次，我会看到同一行 `claim rows: 5`，
> **而很可能不觉得那有问题** —— 因为我要找的是「有没有这个检查」，不是「这个检查对不对」。
> 所以这一轮的运气在于：我多看了一眼一个我本来只打算复制的文件。**


### 变异套件**没有全 fired**，而 `HANDOFF.md` 的头部落后 152 轮（R979）

**判据 (e)：套件绿、**变异测试全 fired**、文档数字全来自 METRICS.md。这一轮把三句都实测了一遍。**

### ① 变异：36 条里 **33 fired / 1 装饰性 / 2 跳过**

```
running 36 of 36 mutations
guard fired                                 ×33
GUARD IS DECORATIVE — tests stayed green    round 606 -- the metric index points at a section that does not exist
SKIPPED — anchor not found                  round 164 -- PARITY.md's module count drifts
SKIPPED — anchor not found                  round 623 -- the copy audit's detail loop goes back to the old predicate
restored tree: GREEN   （2215 通过 / 0 失败 / 2 跳过）
```

> **所以「变异测试全 fired」**不满足** —— 一条守卫是装饰性的，两条的锚点在源码里已经找不到了。**
> **而「跳过」比「装饰性」更隐蔽：那条变异**根本没跑**，所以它既不会红也不会绿，
> 而套件照样绿。** 一个不跑的检查和一个通过的检查在日志里长得一样。**

### ② 三处具体的洞

| 变异 | 状态 | 意思 |
|---|---|---|
| round 606 — 度量索引指向不存在的节 | **装饰性** | 把 `METRIC_CLAIMS.md` 的索引改坏，守卫 `EverySectionTheMetricIndexReferencesExists` **没红** |
| round 164 — `PARITY.md` 的模块数漂移 | **跳过** | 锚点 `**62 个注册模块` 在文档里已不存在 |
| round 623 — copy audit 的 detail 循环回到旧判据 | **跳过** | 锚点那段循环在 `copy_audit_report.py` 里已不存在 |

**同一条 round 164 的**UI 数**变异仍然 fired —— 所以不是整条坏了，是**那一条锚点**坏了。**

### ③ `HANDOFF.md` 的头部停在 **R826** —— 落后 152 轮

**那是每轮**第一读**的块。而它当时写着：**

| 它写的 | 而 METRICS 现在是 |
|---|---|
| 套件 `1766 / 0` | 见 METRICS |
| 类型缺失 `17` | 见 METRICS |
| 形状 `78` | 见 METRICS |
| **(d) claim 表 PASS —— `check_claims.py`：5 行，2 pass / 3 fail** | **那个「5 行」正是 R978 修掉的缺陷** |

> **最坏的一行是最后那行：它把「只审 5 行」当成判据 (d) 满足的证据写在了交接里。
> 而 R978 发现的那个缺陷，其实**早就被记录在这份交接文档里** —— 只是记成了一个通过。**
> **一个活的块装死数字，比没有块更坏，因为它被第一读、被相信。**

**已刷新：头部改成指针 + 复算命令，历史 1,845 行原样保留。**

### ④ 顺带修掉两条「数字不是来自 METRICS」

**① `metrics_report.py` 的 `VERDICT_BY_FILE` 原来是 **cwd 相对路径**：**

```
从 replica/ 跑:    replica/docs/COPY_QUEUE.md 存在 = True
从仓库根跑:        docs/COPY_QUEUE.md 存在 = False   <- 回退判定静默失效
```

**那个回退是给一个会在解释器关闭时崩溃的脚本兜底的 —— 而它取决于你站在哪。改成锚到 `ROOT`。**

**② `DEVIATIONS.md` L50 硬编码「215 类型 / **1,637 条**」，而 `descriptor entries` 现在是 951。
改成指针。**

**修后只看活文档（`GOAL` / `SESSION_STATE` / `DEVIATIONS` / `HANDOFF` 头部）：硬编码命中 **0 / 0 / 0 / 0**。**

### ⑤ 新守卫

**`HandoffHeadPointerTests`（2 用例）：头部必须提到 `METRICS.md`；头部不得复述任何当前度量值
（同一行有指针除外）。**数字边界用 `(?<![0-9A-Za-z_,])` —— 否则 `R951` 会被读成 951。**

### 数字

| 度量 | R978 | **R979** |
|---|---|---|
| 套件 | 2198 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **变异 fired / 总** | 未测 | **33 / 36** |
| **装饰性** | 未测 | **1** |
| **跳过** | 未测 | **2** |
| **活文档硬编码** | DEVIATIONS 1 处 | **0** |

### 教训

> **「跳过」是这一轮最值钱的发现。一条变异没跑，它就不红不绿，而整套仍然绿。
> 所以「全 fired」这句话只有一个来源敢说：**分母也报了**的那个。**
> **而 R978 和 R979 是同一件事的两面：一个检查审 5 行、一条变异没跑 —— 两者都在报通过。**


### 三处里两处是**锚点过期**，第三处**根本不可能红**（R980）

**R979 量出 33 fired / 1 装饰性 / 2 跳过。这一轮把三处都查到底。**

### ① round 606：`§99` 现在**是真的标题**

**变异把 BLOCKERS.md 度量索引里的 `§25` 改成 `§99`，守卫要求每个 `§N` 都是真标题。**
**而 BLOCKERS.md 现在有 **403** 个 `## N.` 标题 —— `## 99.` 真的存在。**

```
文档标题号范围: 0..403，共 403 个
99 是标题? True
```

> **所以变异**不再改变任何东西** —— 而工具把它报成「GUARD IS DECORATIVE」，
> **那是把变异自己过期的前提算到守卫头上了**。**
> **修：`§99` → `§9999`（一个不可能成为标题的号）。**

### ② round 164：锚点里的数字自己会动

**`find: "**62 个注册模块"` —— 而 PARITY.md 现在是 `**65 个注册模块`。**
**同一份文件里，round 71 和 round 435 的注释都记着**同一次**教训（「锚点带上会变的数字」），
而这一条改过两次锚点还是又过期了。**

> **修：给 `mutation-check.py` 加**正则锚点**（`find_re` / `replace_re`），
> 这一条改成 `(\*\*)(\d+)( 个注册模块)` → `\g<1>9\g<2>\g<3>`。
> 什么数字都匹配，然后把前缀加一个 9 —— **文档数一定与 `CreateAll().Count` 不一致，而且永远不会过期。****

### ③ round 623：**不可能红**，因为文案缺口现在是 0

**变异把 detail 循环的判据换回旧的 `_present(v, text)`，守卫要求「明细行数 == 摘要的 missing 数」。**

**而 `copy_audit_report.py` 今天打的是：**

```
summary missing = 0
明细行（以 | ` 开头的表格行）= 0
```

> **缺口是 0，所以摘要 0、明细 0 —— 两边任何改动都还是 0 == 0。
> **这条守卫在缺口为 0 的时候**在原理上无法被触发**，无论怎么改都红不了。**
> **而它不是「装饰性」——「装饰性」的意思是守卫没用；这条的意思是**它的对象现在是空的**。
> 两者要采取的动作完全不同：前者改守卫，后者**要让守卫能自己造一个非空的情形**。**
> **已记 Unknown + 待办，不假装修好。**

### ④ 而这一轮的结果

```
running 36 of 36 mutations
fired        35
decorative    1   （round 623 —— 对象为空，见上）
skipped       0   （原 2）
restored tree: GREEN
```

| 度量 | R979 | **R980** |
|---|---|---|
| 变异 fired | 33 | **35** |
| 装饰性 | 1 | **1** |
| 跳过 | 2 | **0** |
| 套件 | 2200 | **2200** |

### 教训

> **「装饰性」这个标签会把两种完全不同的情形归成一类：
> 守卫没用，和守卫的对象是空的。**
> **而工具只有一个词，所以我差点把 623 也当成「守卫坏了」去改它 ——
> 那会把一条正确的守卫改坏，而它今天的沉默是对的。**


### 最后一条变异也能红了 —— **36 / 36 fired**（R981）

**R980 说 round 623 的守卫「对象为空」，要给它造一个非空情形。这一轮做了，而办法不是改守卫，是让**工具能指向别处**。**

### 缺口的形状

**守卫的不变式：`明细行数 == 摘要的 missing 数`。真实树今天两边都是 **0**，所以任何改动仍 0==0。**

**而两个判据在**一种形状**下会分开：**

| 判据 | 返回 True 的条件 |
|---|---|
| `_satisfied(key, value, text, code)`（新） | value 在源码里 **或** key 的名字出现在源码里 |
| `_present(value, text)`（旧） | **只有** value 在源码里 |

> **所以「键名在源码里、值不在」那一种 —— 新旧判据就分开。而真实树里没有这种键，因为缺口是 0。**

### 改法

**① `copy_audit_report.py` 加了 `--pool` / `--src` / `--out` 三个参数**（默认值就是原来的三个常量）。
**理由写在文件里：守卫要能指向一个人造的小样本，否则它只能永远指向真实树，而真实树上它无话可说。**

**② 守卫改成**跑两次**：**

```
[real tree]  摘要 0 / 明细 0   → 不变式成立（这是原本就在测的）
[fixture]    pool 里一行 "Accounts.Test.Key": "a value that appears nowhere at all"
             src 里一行 class Sample { const string K = "Accounts.Test.Key"; }
             → 键名在、值不在 → 宽判据算「在用」、窄判据算「缺」
             → 摘要 0 / 明细 0（正确代码）→ 成立
             → 摘要 0 / 明细 1（变异代码）→ **红**
```

### 而它真的红了 —— 手工验过

```
变异应用 1 处
[FAIL] Cybersole.Tests.CopyAuditConsistencyTests.DetailRowsMatchTheSummaryTotal
失败: 1
已还原
还原后：通过: 1
```

**然后是全量变异：**

```
running 36 of 36 mutations
fired        36      （原 33 → 35 → 36）
decorative    0      （原 1）
skipped       0      （原 2）
restored tree: GREEN
```

> **判据 (e) 的第二句「变异测试全 fired」**现在成立** —— 而它的成立方式不是把守卫改严，
> 是**给守卫一个能说话的对象**。**

### 而这一轮的方法也可以复用

**前三轮（R979/R980/R981）修的是同一个东西：一个检查沉默，有三种原因。**

| 原因 | 征兆 | 修法 |
|---|---|---|
| 它只审了一部分 | `claim rows: 5` | **扩范围**（R978） |
| 它的锚点/前提过期 | `SKIPPED` / `DECORATIVE` | **换锚点**（R980） |
| 它的对象是空的 | `DECORATIVE` 而代码没变 | **造对象**（R981） |

> **三种都报「通过」或「没通过」，而**修法完全不同**。而工具只给两个词。**

### 数字

| 度量 | R980 | **R981** |
|---|---|---|
| 变异 fired / 总 | 35 / 36 | **36 / 36** |
| 装饰性 | 1 | **0** |
| 跳过 | 0 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 教训

> **「守卫是装饰性的」和「守卫没有对象」在日志里是同一行。
> 而前者要改守卫，后者改了守卫就是把一条正确的守卫改坏。**
> **所以下一步永远是：先看代码有没有变。变了还绿 → 装饰性；没变 → 没有对象。**


### 变异数进了唯一数字源，而它自带**时间戳与陈旧度**（R982）

**判据 (e) 的第二句要「变异测试全 fired」。R981 让它成立了，而那个 `36 / 36` **只活在散文里** ——
正是 AGENTS.md §4 禁止的，也正是 R979 抓到的那个形状（交接里引了个 150 轮前的套件数）。**

### 而它不能塞进 `metrics_report.py`

**一次完整变异是 36 条 × 各跑一次过滤后的套件，约 12 分钟。而 `metrics_report.py` 是**每轮都跑**的命令。
把 12 分钟塞进去，它就不会被跑了。**

> **所以改成两个部分：`mutation-check.py` 写一份**带日期的结果**，`mutation_report.py` 读它。
> 与 `artifact_freshness.py` 对发布产物的处理同一个安排：数字带着它自己的时间戳，
> **而「陈旧」是被报出来的，不是被藏起来的。****

### 结果文件（真实跑出来的，不是写的）

```
{
  "ran_at": "2026-11-17T12:25:02+08:00",
  "total": 36,
  "fired": 36,
  "decorative": 0,
  "skipped": 0,
  "tree": "GREEN"
}
```

### 而 `METRICS.md` 多了五行

```
| 变异套件（上次运行） — mutation-fit: total | 36 |
| 变异套件（上次运行） — mutation-fit: fired | 36 |
| 变异套件（上次运行） — mutation-fit: decorative | 0 |
| 变异套件（上次运行） — mutation-fit: skipped | 0 |
| 变异套件（上次运行） — mutation-fit: staleness | 0 -- no exercised file is newer than the run |
```

### 而 stale 那个字段我改了两版才对

**第一版把 `docs/**` 也算进「被改动的输入」。后果：**任何文档编辑都会让 staleness 变成正数** ——
而一个每轮都响的告警没人看。**

> **变异改的是源码、跑的是测试。文档里的一段话两样都不是。改成只看 `src` / `tests` / `tools`。**

**第二版还把自己算了进去 —— 于是**改一次报告器就让报告失效**。
`mutation_report.py` 只读结果文件，改它不可能改变任何一条变异的裁决，所以按名字排除。**

**而两个方向都验过：**

```
排除自身后           staleness: 0
造一个源码文件       staleness: 0:03:26 -- dummy_probe.py changed after the run
删掉它              staleness: 0
```

### 而这个设计的诚实之处

**它做得到：报上次运行的数，并报源码从那之后动没动。
它做不到：保证今天重跑会给同样的数。** —— 那正是「重跑」的用途，而工具的输出自己写着这一句。

### 数字

| 度量 | R981 | **R982** |
|---|---|---|
| 度量项数 | 14 | **15** |
| 变异 fired / 总 | 36 / 36（只在散文里） | **36 / 36（在 METRICS 里，带时间戳）** |
| staleness | 未测 | **0** |
| 套件 | 2200 | **2200** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |

### 教训

> **一个「陈旧度」字段第一次写会错两次：一次因为把不相干的文件算进来（每轮都响），
> 一次因为把自己算进来（自我失效）。**
> **而两次的后果是同一种：告警响得太多，于是没人看 —— 而那时它和不存在是一样的。**


### `HandleBlock` 不是通用管线 —— 四个状态机串里只有一个类型带它（R983）

**回到核心。`HandleBlock` 是 HANDOFF 未结案项 #4，写着「与优先级 ② 直接相关」。这一轮把它定位到了具体形状。**

### ① 先确认它在两侧的状态

```
复刻件 where_is HandleBlock  ->  implementation 组 0 条（只有 docs 里出现过）
原版 ida.py str HandleBlock  ->  2 条命中
```

**两条命中里第一条就是决定性的：**

```
0x143454a52   "<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55"
0x143454ccf   "HandleBlockg"
```

**`<X>d__NN` 是 async 方法的状态机类型名。所以 `HandleBlock` 是**一个 async 方法**，
而它与 `SetRequest`（d__53）、`HandleResponse`（d__55）**编号相邻** —— 同一个类型里的三个相邻方法。**

### ② 而相邻不等于同管线 —— 有校准项

**把 `analysis/flows.txt`（UTF-16LE 的状态机名转储）里的四组串排出来：**

| 状态机串 | SetRequest | HandleBlock | HandleResponse |
|---|---|---|---|
| `<SetRequest>d__53 $ <HandleBlock>d__54 * <HandleResponse>d__55` | ✓ | **✓** | ✓ |
| `<Generate>d__26 " <SetRequest>d__27 * <HandleResponse>d__28` | ✓ | **✗** | ✓ |
| `* <HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48` | ✗ | ✗ | ✓ |
| `* <HandleResponse>d…`（截断，第 4 处） | ? | ✗ | ✓ |

**计数：`HandleResponse` 4 处 · `SetRequest` 2 处 · `HandleBlock` **1** 处。**

> **决定性：四个类型都有 `HandleResponse`，两个有 `SetRequest`，而只有一个有 `HandleBlock`。**
> **所以它不是请求/响应这一对的必然伴生 —— 第 2 组两兄弟都在、它不在，那是**校准项**。**
> **而 `analysis/flows.txt` 的老注释早就写着「相邻 ≠ 执行管线」，这一轮给出了它的**证据**。**

### ③ 顺序而**不是**位置

**在有它的那一组里，顺序是 `SetRequest` → `HandleBlock` → `HandleResponse`。**

> **Inference（中高）：`HandleBlock` 读的是**还没被正常解析的响应**，
> 所以它排在 `HandleResponse` 之前、`SetRequest` 之后。**
> **Observation 是三个方法的**相对编号**；「它读原始响应」是**推断**，没有代码支持 ——
> R827/R828 已确认它的字符串没有 xref，走 MethodTable 也没走通。**

### ④ 而复刻件那一侧的形状

**`where_is` 的结果说明兄弟都在、只缺这一个：**

| 名字 | 复刻件位置 |
|---|---|
| `SetRequest` | `src/Cybersole.Stores/Actions/StepAction.cs` |
| `HandleResponse` | `src/Cybersole.Http/BouncyHttpClient.cs`（3 处） |
| **`HandleBlock`** | **零** |
| `Blocked` | **30 处**，散在 `StoreFlow.cs`(11) · `HbxFlow.cs`(6) · 其余各 flow |

> **所以判断封锁的逻辑**已经在**，只是**分散在每个 flow 里**，而原版有一处集中的 `HandleBlock`。**
> **那不是「能力缺失」，是「形状不同」—— 而形状不同会不会导致行为不同，取决于那 30 处是否一致。
> 这一点我没有核过，标 Unknown。**

### ⑤ 这一轮**修正了** HANDOFF 里的一条判断

**HANDOFF 写「`HandleBlock` 与优先级 ② 直接相关」。而证据说的是更窄的一件事：
它是**某一个**类型的私有步骤，不是全局风控入口。**
**第 2 组两个兄弟都在而没有它 —— 如果它是通用管线，那一组也该有。**

### 数字

| 度量 | R982 | **R983** |
|---|---|---|
| 套件 | 2200 | **2200（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **变异 36/36** | 是 | **是**（未改代码，记录仍有效） |
| **`HandleBlock` 在原版的类型数** | 未测 | **1 / 4** |

### 教训

> **「相邻」这件事，我这一轮第一次给它配了**校准项** ——
> 第 2 组就是那个「两兄弟都在、它不在」的对照。**
> **没有那个对照，「`HandleBlock` 与 `SetRequest`/`HandleResponse` 相邻」会被读成
> 「它是这对兄弟的伴生」，而错的方向会一直带到实现里。**


### 那 30 处封锁判断**不一致**，而分歧有数字：23 处把「非成功」当「被封」（R984）

**R983 说下一轮核那 30 处是否彼此一致 —— 因为「形状不同会不会导致行为不同」全看这条。核完了。**

### ① 29 处，形状高度重复

```
19 处完全同一行： return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };
其余：Stores.Abstractions.cs 的枚举定义（Blocked = 4）
      StoreFlowRunner.cs:25/71   if (!anti.Ok) → Blocked
      StoreFlowRunner.cs:241/242 429 => Blocked · 401 => Blocked
      StoreFlowRunner.cs:300     private static CheckoutOutcome Blocked(...)
```

### ② 而它们前面那个 `if` **只有一个**

**把「Blocked 行」往上找到最近的 `if`：**

```
23 ×  if (!res.IsSuccess)
```

### ③ 而 `IsSuccess` 是「2xx 到 3xx」

```csharp
// src/Cybersole.Http/TlsProfile.cs
public bool IsSuccess => StatusCode is >= 200 and < 400;
```

> **所以 `!res.IsSuccess` 对 **404 和 500 都成立** —— 也就是说：**
> **「商品页没了」和「站方在拒绝我」在这 23 处是**同一件事**。**
> **而同一项目的 `StoreFlowRunner` 把它们分开：只有 `401` / `429` 判 Blocked，
> 反爬探测失败单独判。****

### ④ 所以 R983 的「形状不同」现在有了语义

| 位置 | 判据 | 404 的结果 |
|---|---|---|
| `StoreFlowRunner`（集中） | `401` / `429` / `!anti.Ok` | **不是 Blocked** |
| 23 个 module（分散） | `!res.IsSuccess` | **Blocked** |

> **两半**互相矛盾**，而且错的那一半是数量多的那一半。**
> **一个把「下架」报成「被封」的监控，比什么都不报更坏 ——
> 它会把真的 drop 藏在一个「我被封了」的故事后面。****

### ⑤ 这与 HANDOFF 未结案项 #2 是同一类缺陷

**#2 写的是「长度守卫把『响应体短/空』判成缺货」。**
**两条的形状一样：**用一个与目标现象无关的量，去决定那个现象。**
- 长度守卫：用 `body.Length` 决定「有没有货」
- 这 23 处：用 `!IsSuccess` 决定「有没有被封」

> **而两条都是「误报」方向 —— 误报缺货会错过 drop，误报封锁也会。
> 而这个项目已经记过一次「误报缺货 = 错过 drop，不可重来」。**

### ⑥ 这一轮**没有**改那 23 处，而理由要写清

**改它意味着逐站决定「404 对该站应该意味着什么」。而那需要镜像侧证据，这一轮没取到。**

> **所以加的是**守卫**，不是修复：**
> **`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）**
> 1. `IsSuccess` 的定义仍是 `>= 200 and < 400`（定义一改，下面的数就不再有意义）
> 2. 混淆点的数量**不得超过** 23（新增一处就红，并列出新的是哪一处）
> 3. 数量**必须等于** 23（减少了也要改常数并说明换成了什么 —— 防止常数变成过时的上界）

### 数字

| 度量 | R983 | **R984** |
|---|---|---|
| 套件 | 2200 | **2203** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是**（记录仍有效；新增代码未进变异集） |
| **`!IsSuccess`→Blocked 的点** | 未测 | **23** |

### 教训

> **「不一致」这个说法在没有数字的时候是软的。而一旦它变成「23 处对 3 处」，
> 就有了一个明确的、可以往下走的下一步。**
> **而这一轮真正的收获是：那 30 处的**共同点**不是一个共享的判据，
> 而是一行**复制了 23 遍的代码**。**


### 状态码分类在字符串层**不可得**，而我把复刻件的历史当成了原版证据（R985）

**R984 留了两条路：取镜像侧证据判「404 各站应是什么」，或把 401/403/429 收进分类器让 23 处改用。
这一轮走第一条，撞到墙；而撞墙的过程中发现自己上一轮读错了一处。**

### ① 状态码分类没有字符串可查

```
ida.py str 403  -> 40 条命中，全是噪声：GUID 片段 · "Build_403" · "10403" · "11403"
ida.py str 429  -> 40 条，第一条是 Metalama 的公钥串
ida.py str 401  -> 40 条，前两条是版本号与 Avalonia 公钥
```

> **原因很直白：状态码分类在代码里是**整数比较**，不产生字符串。
> 所以字符串路线**在原理上**看不见它 —— 不是「这次没找到」。**
> **而唯一带点信息的命中是 `0<SolveCptChallenge>d__39`（一个验证码挑战状态机），
> 那属于「挑战求解」，不属于「状态码分类」。**

**→ 要它必须走代码，而代码路线已经失败两次（R827/R828：字符串无 xref，MethodTable 未通）。**

### ② 而我在 R984 引用过一条「原版分类」

**R984 之后我打算用 `replica/docs/HISTORY.md:1488` 的「状态码分类（401/403 可重试 vs 422 不可）」当原版证据。
读上下文发现它不是。**

**那一节标题是「6.73 空桩填实（R12）」，正文第一句：「R12 审计给出的缺口是 88 个空桩。这一轮把其中 39 个填成真实实现」。**

> **所以那是**复刻件 R12 时自己的实现描述**，不是对原版的观察。**
> **拿它推「原版怎么分类」就是循环论证 —— 与 AGENTS.md §2.2 记的同一类错误
> （「复刻件写出的 settings.json 不能当实机证据」）。**
> **而这一条比那个更滑：它读起来像是在描述原版，因为整节都在讲「我们补齐了什么」。**

### ③ 而它顺手暴露了复刻件的**第三处**自相矛盾

**`StoreFlowRunner.cs:242` 写：**

```csharp
401 => new MonitorResult { Status = MonitorStatus.Blocked, Error = message },
```

**而同一个仓的 `HISTORY.md` 写 401 是可重试的。**

> **两处描述同一个状态码，一处判「终止（Blocked）」，一处判「可重试」。**
> **而 401 本来的意思是「凭据过期」—— 那正是 `RefreshSession` 存在的理由。
> 把它判成终止，等于把刷新会话这条路**提前关掉**。**

**→ 而这一点我**没有**改：改 401 的语义同样是行为变化，同样缺原版证据。**

### ④ 所以这一轮的实际结论是**路线封死**，不是「又找到一个缺陷」

**`HandleBlock` 与「状态码分类」现在共用同一个墙：**

| 要的东西 | 字符串层 | 代码层 |
|---|---|---|
| `HandleBlock` 的实现 | 名字在，但只给位置不给内容 | 无 xref · MethodTable 未通 |
| 状态码分类 | **原理上不可得**（整数比较无字符串） | 同上 |

> **所以这两条不该再各占一轮。它们是一个阻塞：**在原版里，名字能不能落到代码上**。**

### 数字

| 度量 | R984 | **R985** |
|---|---|---|
| 套件 | 2203 | **2203（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是** |
| **`!IsSuccess`→Blocked 的点** | 23 | **23（守卫钉着）** |
| **原版状态码分类的证据** | 未测 | **字符串层不可得** |

### 教训

> **「读起来像在描述原版」和「是在描述原版」是两件事，而我的判断靠的是语的语气。
> 那一节的语气全是第三人称客观陈述，而它描述的是**我们自己的**一次改动。**
> **更省事的判据是看标题和第一句说主语是谁 —— 「R12 把 39 个填成真实实现」，主语是我们。**


### 优先级 ① 有了每站的数：185 个覆写里 180 做实事，**只有 Bstn 一站的整条下单链断了**（R986）

**R985 说换一条不靠名字定位的核心工作。这一轮做的是优先级 ① 的真实状态：
每个站**能不能真下单** —— 而在这之前只有「每个步骤至少有 1 个覆写」这个**不同的**断言被量过。**

### ① 新工具，按**文件**数而不是按**步骤**数

**`hollow_audit.py` 回答的是「每个步骤跨所有站有几个覆写」。
而一个步骤在**别处**有覆写，说明不了**这个站的**覆写做了事。**

**`tools/flow_work_audit.py`：逐 flow 文件，把每个覆写体分类为「有实质工作」或「只返回一个结果」。**

### ② 而第一版分类器错得很有代表性

**第一版只把 `await` / `Http` / 会话访问算作工作，于是把这一行判成占位：**

```csharp
public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
    OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct);
```

**工作藏在辅助方法里。而那是 **R824 记过的同一件事**：「委派是**无接收者**调用，`\w+\.名字` 一定漏」。**

> **第一版：185 个覆写里 175 真、**10 占位**。
> 修好（把对本类方法的委派也算工作）：**180 真、5 占位**。
> 而那 5 个假占位里有 4 个是 `GetCheckout`，正是**下单链路上的关键一步** ——
> **如果我按第一版去「补」它们，我会写四份重复的实现，而它们本来就在。****

### ③ 修好之后的真实状态

| flow | 覆写 | 真 | 占位 |
|---|---|---|---|
| Magento | 33 | 33 | 0 |
| PopMart | 23 | 23 | 0 |
| Shopify | 18 | 17 | **1** |
| Footsites | 17 | 17 | 0 |
| Nike | 15 | 15 | 0 |
| Scheels | 12 | 12 | 0 |
| Farfetch / Hbx / Hybris | 10 each | 10 | 0 |
| **Bstn** | 9 | 5 | **4** |
| Demandware | 9 | 9 | 0 |
| Goat | 8 | 8 | 0 |
| 其余 5 个 | 1–5 | 全真 | 0 |
| **合计** | **185** | **180** | **5** |

**97.3% 的覆写做了超出「返回一个结果」的工作。**

### ④ 而那 5 个占位，两个类别

**Bstn 的 4 个 —— 整条下单链：**

```
AddToCart    Fail("bstn: cart endpoint unknown — /cart.js is 404 and the cart lives under /api/b…")
GetCart      Fail("bstn: cart endpoint unknown")
GetCheckout  Fail("bstn: checkout endpoint unknown (Adyen)")
SubmitOrder  Fail("bstn: order endpoint unknown")
```

**Shopify 的 1 个 —— `GetCsrf`，**有意**的空实现，注释写着 R823 的理由：
「不编造 fallback。GetHomeAsync 已经从页面提取 `authenticity_token`；若没有，在这里造一个 GUID
会把服务器从未签发的令牌放进会话，而每个带它的请求都会被判无效」。**

> **所以 10 个占位里，4 个是**我们不知道端点**，1 个是**有意不做**，5 个是我分类器的错。**
> **而「Bstn 能监控不能下单」现在有确切形状：找商品、读尺码、读库存四步都在，
> 从加购到提交订单四步全断，且断在「端点未知」上。****

### ⑤ 加的两条守卫

**`FlowWorkAuditTests`（2 用例）：**
1. `MostOverridesDoWork` —— 覆写总数 > 100（签名正则失配就会红），且占位数**不超过 5**
2. `AFlowWithPlaceholdersSaysWhy` —— 有 ≥2 个占位的 flow 必须出现 `endpoint unknown` 字样
   （**一个不说原因的占位，读起来像疏忽，而不是一条记下来的缺口**）

### 6 这一轮把「能不能下单」从**无测度**变成**一个数 + 一个具名缺口**

**而它同时说明：优先级 ① 的剩余不是「35 个站都要做」，是**一个站的四个端点**。
那是一个可完成的量，而不是一片模糊。**

### 数字

| 度量 | R985 | **R986** |
|---|---|---|
| 套件 | 2203 | **2205** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **flow 覆写总数** | 未测 | **185** |
| **有实质工作** | 未测 | **180（97.3%）** |
| **占位** | 未测 | **5（Bstn 4 + Shopify 1 有意）** |

### 教训

> **我的分类器第一版漏了「委派」，而那正是 R824 记过的形状 —— 只是那次是搜索，这次是分类。
> 同一条规则（「无接收者的调用看不见」）换了场景，我一次都没想起它。**
> **而代价如果不抽查：我会去「补」四个本来就在的方法。**


### `Bstn` **不在原版里** —— 而那四个占位不是原版的缺口，是**复刻件多出来的站没做完**（R987）

**R986 说「优先级 ① 的剩余 = 一个站的四个端点」。这一轮去取那三个端点，第一个动作就否掉了那个说法。**

### ① 原版里没有 `bstn`

```
ida.py str bstn      -> 0 命中
ida.py str api/bstn  -> 0 命中
ida.py str bstn.com  -> 0 命中
```

**`ida.py str` 查的是数据库本身，所以反向可用（§2.7b 的环）。
而 `core_coverage.py` 的 27 个 store host 里**也没有 bstn**：
`goat` `hbx` `popmart` `scheels` 都在，`bstn` 不在。**

> **三项一致：名字不在字符串池、不在 27 个 host 里、而它自己的占位写着 `endpoint unknown`。**
> **→ `BstnFlow` 是**复刻件自己加的站**，原版没有它。那四个占位不是「原版某站没做完」，
> 是「复刻件多了一个站，而那个站没做完」。****

### ② 而这条不能推广 —— 有三个校准项

**把 18 个站点 flow 名字逐个查原版：**

| flow | 命中 | 而平台在不在 |
|---|---|---|
| **Bstn** | **0** | **不在**（也不在 27 host 里） |
| **Hybris** | **0** | **在** —— `ecommerce-gateway.mollie.com … hypecommerce` |
| **PoqApp** | **0** | **在** —— `app.midtrans.com … poqapp` |
| Hbx | 调用失败，未判 | `hbx.com` 在 27 host 里 |
| 其余 14 个 | 2 – 40（40 是插件上限） | — |

> **所以「名字不在」只在 Bstn 上成立为「站不在」。
> `Hybris` 与 `PoqApp` 是**校准项**：名字缺失证明不了**平台**缺失 —— 原版卖 hybris 的店，
> 只是不叫这个名字。**
> **这正是 §2.7b 的那条：一个来源找不到 ⇏ 不存在。而这里的「第二个来源」
> 是 `core_coverage` 的 host 列表，它把 Hybris/PoqApp 的宿主都列了出来。**

### ③ 所以 R986 的归属错了，而数没错

| R986 说 | 实际 |
|---|---|
| 优先级 ① 剩余 = Bstn 四个端点 | **不是原版缺口** —— Bstn 不在原版 |
| 185 覆写 / 180 真 / 5 占位 | **对**（这一轮没有推翻） |
| 判据 (f) 27/27 matched / 0 unmatched | **对**，而它**从未把 Bstn 算进去** |

> **所以判据 (f) 的 store 覆盖仍是 **27/27、0 未覆盖**。
> 而 `BstnFlow` 的存在是一个**超出原版**的添加，它的 4 个占位说明那个添加没做完。**

### ④ 而处置有两种，这一轮不定

**① 删掉 `BstnFlow`** —— 若目标是「1:1」，原版没有的东西不该有。
**② 保留并标为「超出原版的添加」** —— 若多一个站是可接受的扩展。**

> **而这是 YG 该定的事，不是证据能定的。理由：两个方向都自洽，
> 而「1:1」这个词在这次对话里没有被明确到「不许有额外站」。**
> **所以记进 BLOCKERS，标为需要判断，而不是自己决定。**

### 数字

| 度量 | R986 | **R987** |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| flow 覆写 / 真 / 占位 | 185 / 180 / 5 | **185 / 180 / 5（未变）** |
| **判据 (f) store matched** | 27/27 | **27/27（Bstn 从未算入）** |
| **不在原版的站点 flow** | 未测 | **1（Bstn）** |

### 教训

> **R986 我把「复刻件的 35 个 flow」默认成了「原版那些站」。
> 而从没有人说过它们是同一批 —— `core_coverage` 的 27/27 与 35 个 flow 类型一直是两个数，
> 而我把它们读成了一个。**
> **而校验它只需一次 `ida.py str`。**


### 判据 (f) 的 store 分母虚高 12 —— `VENDOR_HINTS` 少了十二个支付网关（R988）

**R987 说下一轮核「35 个 flow vs 27 个 host 差 8」。
核的过程中发现 27 这个分母本身是错的：**十二个 host 不卖东西**。**

### ① 分类靠一份手写名单，而名单不完整

**`core_coverage.py` 把 host 分成 store 与 vendor 两桶，判据是 `VENDOR_HINTS` 里有没有这个标签。
而那份名单是从**风控厂商**加**三个大支付**写出来的：**

```python
"cloudflare", "kasada", "datadome", "perimeterx", "queue-it", "recaptcha", "hcaptcha",
"akamai", "aycd", "turnstile", "captcha", "paypal", "stripe", "adyen", "paynamics",
"eshopworld", "global-e", "vivapayments", "wdprapps", "disney", "purpledotprice", "purpledot"
```

> **名单之外的标签**默认**就是 store** —— 因为判据是「有没有被列进 vendor」。**
> **于是 `api.braintreegateway.com` · `api.sibspayments.com` · `api.vipps.no` ·
> `app.midtrans.com` · `degica.as1.gpayments.net` · `ecommerce-gateway.mollie.com` ·
> `flex.cybersource.com` · `payments.bigcommerce.com` · `retry.touchtechpayments.com` ·
> `threeds.airwallex.com` · `static-forms.klaviyo.com` · `www.ibm.com`
> —— **十二个支付/身份/表单网关 —— 全被算成了「店」。****

### ② 补上之后

```
改前: hosts with a path: 39  (store 27, vendor 12)
改后: hosts with a path: 39  (store 15, vendor 24)

store hosts matched:   15
store hosts unmatched:  0
```

**→ 判据 (f) 的 store 覆盖从「27/27」变成「15/15」，而 0 unmatched 不变。**

> **分母小了十二个，而分子一个没少 —— 所以**覆盖率没变，诚实度变了**。
> 而判据 (f) 要的是「原版**站点**清单」，不是「原版**主机**清单」。**
> **一个掺了支付网关的分母，会让「27/27」描述一件不是它名字所说的事。**

### ③ 一个我特意**没有**动的

**`authenticate.riotgames.com` 留在了 store 桶**，理由写进代码注释：
它是身份 host，但 registry 里**也有**一个 `riotgames` store flow ——
**把它移走会把这个配对藏起来，而不是修好一个标签。**

### ④ 而 METRICS 里那两个 vendor 数字**不是矛盾**

**改完后 `core_coverage` 报 vendor 桶 24，而 METRICS 的 vendor 度量报 12 —— 我去查了，不是同一件事：**

| 工具 | 分母 | 值 |
|---|---|---|
| `core_coverage.py` 的 vendor 桶 | 支付 + 风控 + 平台基础设施 host | **24** |
| `vendor_coverage.py`（METRICS 读的） | **风险厂商**（cloudflare / kasada / …） | **12** |

> **两个工具各自一致，而它们的「vendor」不是同一个概念 —— 这一点值得记，
> 但不构成缺陷。而**如果我没查就当成矛盾去改，会把一个正确的工具改坏**（R980 的同一课）。**

### ⑤ 一个仍然敞着的

**`core_coverage` 的 vendor 段只搜 `Scripts/`，所以 24 个里 20 个是 `unmatched`。
而 store 段搜整个 `src`。两段口径不同，输出里没写这一点。**

> **→ 记 Unknown：vendor 段的 unmatched 里有多少是「真的没实现」，多少是「实现不在 Scripts/ 里」。
> 这一轮没有分开，所以不能从 20 这个数读出任何关于覆盖率的结论。**

### 数字

| 度量 | R987 | **R988** |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **判据 (f) store 分母** | 27 | **15** |
| **store matched / unmatched** | 27 / 0 | **15 / 0** |
| **core_coverage vendor 桶** | 12 | **24** |

### 教训

> **「名单之外的默认是 store」是一条**默认规则**，而默认规则的错永远朝一个方向犯：
> 新东西被算进多数那一类，于是没人看得见。**
> **十二个支付网关在「27 个店」里待了很多轮，而它们每一个的输出行都写着 `matched` ——
> 一个错的分母会让每一行都看起来是对的。**


### 两列换成同一个分母后，vendor 的未覆盖从 **20** 降到 **6**，而 6 个全是支付网关（R989）

**R988 留了一个 Unknown：vendor 段只搜 `Scripts/`，store 段搜整个 `src`，所以 24 个里 20 个 `unmatched`
读不出任何覆盖率结论。这一轮把两段的分母统一，那个数变成可读的。**

### ① 缺陷：两列用两个分母

**`registry_ids()` 已经返回 `all_src`（整个 `src` 的文本），而 vendor 段另有一个 `scripts_text()`，只读 `Scripts/*.cs`。**

> **于是判据 (f) 那两列是**在不同分母下**量出来的：
> store 那列「源码里有没有这个名字」，vendor 那列「Scripts 目录里有没有这个名字」。
> 而 `kasada` / `datadome` / `perimeterx` 的实现本来就不全在 `Scripts/`。**

### ② 改法：共用 `all_src`

```python
# 改前
scr = scripts_text().lower()
# 改后
scr = all_src.lower()
```

### ③ 结果

```
vendor 24 个 host：matched 18 · unmatched 6
```

**而 6 个 unmatched 是：**

| host | 标签 |
|---|---|
| `app.midtrans.com` | midtrans |
| `degica.as1.gpayments.net` | gpayments |
| `ecommerce-gateway.mollie.com` | mollie |
| `flex.cybersource.com` | cybersource |
| `retry.touchtechpayments.com` | touchtech |
| `threeds.airwallex.com` | airwallex |

> **六个**全都是支付网关**，一个风控厂商都没有。**
> **→ 优先级 ②（风控对抗）的 vendor 覆盖是**完整的**：
> cloudflare · kasada · datadome · perimeterx · queue-it · aycd · turnstile/captcha · eshopworld ·
> wdprapps · disney · global-e · vivapayments · paypal · adyen · klaviyo · braintree · sibs · vipps —— 全 matched。**
> **→ 而那 6 个属于**下单链路**（优先级 ①），不是风控。**

**这是判据 (f) 第一次给出**可分类**的「未覆盖」：6 条，每一条都写着它是哪一类。**

### ④ 而统一分母顺手暴露一个假匹配

**改完后 `registerdisney.go.com` 匹配在标签 `go` 上 —— 而 `go` 出现在源码里几乎所有地方。**

**成因：分桶用**整串 host**（含 `disney` → 进 vendor 桶），匹配用**注册标签**（`go.com` 的标签是 `go`）。
两个步骤对「哪个 token 是这个 host 的名字」看法不同。**

**修：被 vendor 提示词打了桶的 host，用**那个提示词**当它的标识。改完 `registerdisney.go.com` 经 `disney` 匹配。**

> **而这条正是 R988 的 docstring 早就写着的风险：「a short label can match by accident」。
> 它真的发生了一次，而它发生的条件是**分桶与匹配用不同的 token** —— 那句话没说到这一层。**

### ⑤ 仍然诚实的部分

**`matched` 现在两列同义：「这个名字在源码里出现过」。
它不是「这个站能用」也不是「这个厂商接上了」—— 输出末尾的 NOTE 一直这么写着。**

### 数字

| 度量 | R988 | **R989** |
|---|---|---|
| 套件 | 2205 | **2205（未动测试）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| store matched / unmatched | 15 / 0 | **15 / 0** |
| **vendor unmatched（统一分母后）** | 20（口径不同，不可读） | **6（全是支付网关）** |
| **假匹配** | 1（`go`） | **0** |

### 教训

> **「两列数字放在一张表里」不等于「两列在回答同一个问题」。
> 而一个口径不同的分母，会让一列看起来只是「覆盖得差」，而不是「量错了」。**


### 那 6 条未覆盖分成两类，而其中一条藏着**伪造的支付令牌**（R990）

**R989 说下一轮核那 6 个支付网关是否真缺。核了，而答案不是「缺」或「不缺」——是**三种**。**

### ① 先确认真缺：它们不在源码里

```
where_is midtrans / gpayments / mollie / cybersource / touchtech / airwallex
  -> 各 2 个文件，而两个都是 docs\VERDICT.md 与 docs\BINDING_BACKLOG.md
```

**而 `core_coverage` 的 `all_src` 只走 `replica/src`。
→ 这 6 个在**源码**里确实一次都没出现，`unmatched` 是准确的。**

### ② 而它们各自的原版路径拿到了（来自二进制清单 `analysis/.coverage-paths.txt`）

| host | 路径 | 性质 |
|---|---|---|
| `app.midtrans.com` | `/snap/v1/transactions` · `/snap/v2/transactions` | 收单会话创建 |
| `degica.as1.gpayments.net` | `/api/v2/brw/info/result?transId=` | 结果查询 |
| `ecommerce-gateway.mollie.com` | `/api/v1/public/core/payments/poll` | 支付状态轮询 |
| `flex.cybersource.com` | `/flex/v2/tokens` | **令牌化** |
| `retry.touchtechpayments.com` | `/api/v1/:select` | 支付选择 |
| `threeds.airwallex.com` | `/api/v1/pa/gateway/hk/three-ds-method/redirect` | **3DS 重定向** |

### ③ 第一类：**泛化步骤覆盖了它，而指标在原理上看不见**

**3DS 在复刻件里是泛化的：**

```csharp
Solve3DSAsync         → c.Session.ThreeDsUrl = adyen.threeDSMethodUrl   // URL 来自 paymentData
Solve3DSRedirectAsync → GetAsync(c.Session.ThreeDsUrl) → 从 HTML 提取 transStatus
Handle3DSAsync        → 按 transStatus 判 Y / 其他
```

> **Airwallex 的 `three-ds-method/redirect` 被这条链覆盖 —— 而 URL 是**运行期**从 paymentData 读出来的，
> 所以 host 名永远不会写进源码。**
> **→ `matched` 测的是「host 名出现在源码里」，而**泛化步骤不写 host 名**。
> 这是覆盖率指标的结构性盲区，不是复刻件的缺陷。**

### ④ 第二类：**该调用的端点被一个伪造值代替了** —— 这是缺陷

```csharp
public virtual async Task<StepOutcome> GetPaymentTokenAsync(FlowContext c, CancellationToken ct)
{
    if (!string.IsNullOrEmpty(c.Session.PaymentToken)) return StepOutcome.Success();
    c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];   // ← 不调任何端点
    c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
    return StepOutcome.Success();
}
```

> **它不请求 `flex.cybersource.com/flex/v2/tokens`，而是**造一个随机 GUID 当支付令牌**。**
> **而 `ShopifyFlow.GetCsrf` 的注释明确写着 R823 的结论：
> 「不编造 fallback —— 服务器从未签发的令牌会让每个带它的请求被判无效」。**
> **`GetPaymentTokenAsync` 做的**正是那件被明令禁止的事**，而且它在**支付**路径上。**
> **→ 所以 Cybersource 那一条不是「名字没出现」，是「该调的端点被伪造值顶掉了」。**

**而 `HISTORY.md` 的 R12 表里还有一处同样的形状：「令牌 | `GetToken` | 16 字节 CSPRNG hex」。**

### ⑤ 第三类：真缺，且没有泛化路径

**`midtrans` / `gpayments` / `mollie` / `touchtech` —— 收单会话、结果查询、状态轮询、支付选择，
四者都是**host 专属**的端点，没有泛化步骤能覆盖它们。**

**→ 这四条是优先级 ① 的真缺口，而它们各自属于哪个 flow，尚未取证。**

### ⑥ 所以判据 (f) 的 6 条现在可以逐条写「为什么」

| # | 未覆盖 | 为什么 |
|---|---|---|
| 1 | `threeds.airwallex.com` | **泛化覆盖**（`Solve3DSRedirectAsync` 跟随运行期 URL）—— 指标盲区，非缺陷 |
| 2 | `flex.cybersource.com` | **被伪造令牌顶掉** —— `GetPaymentTokenAsync` 造 GUID 而不调用 |
| 3–6 | `midtrans` · `gpayments` · `mollie` · `touchtech` | **真缺**，host 专属端点，无泛化路径 |

### 数字

| 度量 | R989 | **R990** |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| vendor unmatched | 6 | **6（但分成了 1 盲区 / 1 伪造 / 4 真缺）** |
| **伪造的支付令牌** | 未测 | **1 处函数 + 1 处 `GetToken`** |

### 教训

> **「未覆盖」是一个**混合类别**：里面有「做不到」「没做」「做了但指标看不见」「做了个假的」。
> 而它们在这张表里长得一模一样 —— 都叫 `unmatched`。**
> **如果我只按这一个词去补，我会去写六个支付网关客户端，而其中一个的活儿已经干完了（只是指标看不见），
> 另一个的活儿是**先把自己伪造的那个值删掉**。**


### 伪造的支付令牌删了 —— 而**删掉它没让任何用例红**（R991）

**R990 发现 `GetPaymentTokenAsync` 造一个随机 GUID 当支付令牌。这一轮删了它，加了两条守卫，并验证守卫会红。**

### ① 先确认它从没被 override 过

```
GetPaymentToken 的 override: 0 处
```

**而真会拿到令牌的地方另有五处：**

| 位置 | 怎么拿的 |
|---|---|
| `FootsitesFlow.cs:353` | 从响应里提 `"id"` |
| `MagentoFlow.cs:806` | 从响应里提 `"token"` |
| `ShopifyFlow.cs:477` | 从响应里提 `"id"` |
| `StoreFlow.cs:1398 / 1474 / 1550` | 已有值 |
| `Payments/Gateways.cs` ×4 | 真网关端点签发的 nonce / token |

> **所以那个伪造**只是兜底** —— 方法开头就短路：`if (Session.PaymentToken 非空) return Success()`。
> 而它从没被走到，因为没有 flow 会「走到支付却没有令牌」……**
> **除非某个 flow 少写了一步。而那时它会**假装成功**。**

### ② 改法：兜底从「造值」改成「显式失败」

```csharp
// 改前
c.Session.PaymentToken = "tok_" + Guid.NewGuid().ToString("N")[..24];
c.Session.Vars["paymentToken"] = c.Session.PaymentToken!;
return StepOutcome.Success();

// 改后
return StepOutcome.Fail(
    $"{Name}: no payment token available -- no tokenising step ran for this flow, and this step will not invent one",
    retryable: true);
```

**理由直接引 R823：服务器未签发的令牌会让每个带它的请求被判无效。
伪造只是把失败**从这一步挪到某个下游调用**，而在那里它长得像「店方拒绝了我」。**

### ③ 而全量套件**没有一条用例因此变红**

```
改前 2222 通过 / 0 失败 / 2 跳过   （Speed!=Slow）
改后 完整套件 2207 通过 / 0 失败 / 0 跳过
```

**（2207 与 2222 的口径不同：`metrics_report.py` 按 R493 排除六个浏览器依赖类。）**

> **删掉一个伪造实现而套件全绿，读起来像「这个改动没有影响」。
> 实际含义是：**没有任何用例覆盖那条兜底路径** —— 它从没被执行过。
> 而「从没被执行」正是它活到现在的原因。**
> **→ 所以这一轮真正的产出不是删了那三行，是**加了两条守卫**。**

### ④ 两条守卫，而它们的方向相反

**`CredentialsAreObtainedNotInventedTests`（2 用例）：**

1. `NoCredentialIsMintedLocally` —— 扫整个 `src`，`\w*(PaymentToken|AuthToken|AccessToken|CsrfToken|SessionToken)\w*\s*=\s*[^;]*(Guid\.NewGuid|RandomNumberGenerator)`
   一处都不许有
2. `TheFallbackReportsRatherThanInvends` —— `GetPaymentTokenAsync` 必须**还在**、必须**仍短路于真令牌**、
   且必须含「will not invent one」字样

> **② 那条是防「用删除来修」：把一个**该报告缺失**的步骤删掉，会让缺口从「有诊断的失败」变成「不存在」。**

### ⑤ 而守卫**验过会红**

**手动把伪造放回 1 处 → `[FAIL] NoCredentialIsMintedLocally` → 还原 → 通过。**

```
临时把伪造放回 1 处
失败!  - 失败: 1，通过: 1
[xUnit.net] Cybersole.Tests.CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally [FAIL]
已还原
```

**（R981 立的规矩：一个没验过会红的守卫不是证据。）**

### ⑥ 仍然敞着的

**`GetToken`（`HISTORY.md` R12 表：「16 字节 CSPRNG hex」）是同形的第二处，而这一轮的守卫**没有**扫它 ——
因为它是「16 字节随机 hex」，与 `Guid.NewGuid` 不同形。那一条要单独取证：它签发的到底是什么令牌。**

### 数字

| 度量 | R990 | **R991** |
|---|---|---|
| 套件 | 2205 | **2207（+2 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 1 处 | **0** |
| **本地铸造的凭据（全 src）** | 未测 | **0** |

### 教训

> **一个从没被执行过的缺陷，删掉它不会让任何用例变红 ——
> 而那正是它活了这么久的原因。**
> **所以「删掉 + 全绿」不能当成验证；验证是**加一条会红的守卫，并亲眼看它红一次**。**


### `GetToken` 不是死代码，是**接线缺口** —— 而它的身体也不再伪造（R992）

**R991 说下一轮核 `GetToken`（16 字节 CSPRNG hex）是不是同形第二处。核完发现它更接近`HandleBlock`，
而不是`GetPaymentToken`。**

### ① 它是三合一的

```csharp
GetTokenAsync        → Vars["token"] = 16 字节随机 hex
CreateTokenAsync     → => GetTokenAsync
GetAuthTokenAsync    → => GetTokenAsync     // 注释：「Acquire an authorisation token specifically」
```

> **`GetAuthToken` 说它在「取授权令牌」，而它调的是造随机 hex。
> 授权令牌由服务器签发 —— 随机 hex 永远不是。**
> **这比 R991 那个更直接：那个至少叫「获取支付令牌」，这个明说「授权」。**

### ② 而它**完全没被接上**

```
Vars["token"] 的写入点: 1（就是它自己）；读取点: 0
GetTokenAsync / GetAuthTokenAsync / CreateTokenAsync 的调用点: 0（除两个别名互指）
出现在步骤序列里: 无（StoreFlowSteps.cs 无）
字符串形式引用 "GetToken" / "CreateToken" / "GetAuthToken": 0
```

> **所以它是**完全孤立**的：不执行、结果也没人读。
> 而「不执行」正是它活了这么久的原因 —— 与 R991 那条同一个机制，只是更彻底。**

### ③ 而它**不是**死代码该删 —— 三个名字都在原版里

```
recovered_method_names.txt:  CreateToken 行 453 · GetAuthToken 行 1269 · GetToken 行 1595
```

> **→ 形状在、**边**缺失。**
> **而 R955 已经定过这件事：「code is reachable or not, and unreachable code needs a **call**, not a rewrite」。**
> **→ 所以不删、不改名 —— 缺的是一个调用。**
> **→ 而那个调用点需要原版的证据，与 `HandleBlock` 是同一堵墙（名字定位不到代码）。**

### ④ 所以这一轮做的是**把身体改成不伪造**

```csharp
// 改前
var token = Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
c.Session.Vars["token"] = token;
return StepOutcome.Success();

// 改后
return StepOutcome.Fail(
    $"{Name}: no token source is known for this step -- it has never been wired into a flow, and this step will not "
    + "invent a credential", retryable: true);
```

> **理由：接线的人不该拿到一个会造值的身体。**
> **`GetAuthTokenAsync` 说它取授权令牌，而接上它的那一刻，一个随机 hex 就会变成「认证已完成」的信号。
> 那一刻的错误比现在贵得多 —— 因为那时它会**流进请求**。**
> **与 R991 同一条原则：不编造 fallback，缺少就以可诊断的方式缺。**

### ⑤ 而守卫**加宽了一格**，因为它原来漏掉了这个形状

**R991 的守卫匹配 `Token = …Guid.NewGuid`，即**左边是标识符**。
而这里是 `Vars["token"] = <随机字节>` —— **左边是索引器**，所以它漏过去了。**

**加宽后的模式同时匹配两种：**

```
\w*(PaymentToken|AuthToken|AccessToken|CsrfToken|SessionToken)\w*\s*=\s*[^;]*(Guid\.NewGuid|RandomNumberGenerator)
|
Vars\[\s*""[^""]*(token|nonce|secret|credential)[^""]*""\s*\]\s*=[^;]*(RandomNumberGenerator|Guid\.NewGuid)
```

> **这与 `flow_work_audit` 那个委派漏洞是同一课：我预期的形状不是它唯一的形状。**

**并新增第 3 条用例 `TheGenericTokenStepAlsoReports`：该方法必须还在、必须含「not invent a credential」、
且源码里不许再出现 `Vars["token"] = token`。**

### ⑥ 守卫验过会红

```
把 Vars["token"] = 随机 hex 放回 1 处
失败!  - 失败: 1，通过: 2，总计: 3
[FAIL] CredentialsAreObtainedNotInventedTests.NoCredentialIsMintedLocally
已还原
```

### 数字

| 度量 | R991 | **R992** |
|---|---|---|
| 套件 | 2207 | **2208（+1 用例）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 伪造的支付令牌 | 0 | **0** |
| **伪造的通用/授权令牌** | 1（`GetToken`） | **0** |
| 本地铸造的凭据（全 src，含会话变量） | 未覆盖索引器形状 | **0** |

### 教训

> **同一个「不执行所以没人反对」的机制，在 R991 那里是兜底从没被走到，
> 在这里是步骤从没被接上 —— 而后者更彻底：连「走到它」这件事都不存在。**
> **而两者的身体都是伪造的。所以「它不执行」不能当成「它没问题」的证据 ——
> 它只说明**现在**没问题，而接上线的那一刻问题才开始，且那时已经没人记得看过它。**


### 状态码分类在复刻件里有**两份**，而它们在 **409** 上给出相反结论（R993）

**R992 说下一轮核 `RefreshSessionAsync` / `HandleResponseAsync` 是否同形。核到一半发现更有价值的东西：
R985 说「状态码分类字符串层不可得」的那个分类，**复刻件里就有两份**。**

### ① 这两个**不像** `GetToken`

```csharp
RefreshSessionAsync   → 真 GET origin，写 Vars["lastStatus"]，按 IsSuccess 判
HandleResponseAsync   → 完整状态码表（下面）
```

**没有伪造，有实质内容。而 `Vars["lastStatus"]` 是**活的通道**：5 个写入者、4 个读取者，
`StoreFlowRunner.cs:293` 也在读它。**

### ② 而分类有两份，且**只有一份在执行路径上**

| 位置 | 在步骤序列 | 调用点 |
|---|---|---|
| `HandleResponseAsync`（`StoreFlow.cs:349`） | **无** | **0** |
| `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`） | **在用**（`LastStatus(ctx)` 读同一变量） | 有 |

**两份的表：**

| 码 | `HandleResponseAsync` | `ClassifyCheckoutFailure` |
|---|---|---|
| 200/201/204 · 3xx | Success | — |
| 400 | Fail 不可重试 | Error |
| 401 / 403 | Fail **可重试** | Error |
| 404 | Fail 不可重试 | Error |
| **409** | **Fail 可重试** | **Declined（终止）** |
| 422 | Fail 不可重试 | **Declined** |
| 429 | Fail 可重试 | Error |
| 5xx · 其它 | Fail 可重试 | Error |

### ③ 而冲突只有一个码，但是最要紧的那个

**`ClassifyCheckoutFailure` 的注释自己写着：**

> 「A 422 means the store understood the request and rejected it — retrying costs time and
> can burn the account. A 409 (sold out during checkout) is the same story.」

**而 `HandleResponseAsync` 把 409 判成**可重试**。**

> **409 = 结账途中售罄。判可重试会**重试一件已经卖掉的东西** ——
> 而那正是注释说「会烧账号」的那一类。**
> **→ 所以把它接上是**危险**的：接之前必须先把 409 对齐。**
> **这与 R992 的 `GetToken` 相反 —— 那个该接、这个不该直接接。**

### ④ 而这也更正了 R985

**R985 说「原版状态码分类在字符串层不可得」。那句仍然对（原版的看不到）。
但我当时没查**复刻件里有没有**，而答案是：有两份。**

> **而 `HISTORY.md` R12 那条「状态码分类（401/403 可重试 vs 422 不可）」描述的就是
> `HandleResponseAsync` —— 那条记录是对的，只是我一直没找到它在哪个文件。**
> **→ 我说「不可得」的时候，缺的不是原版证据，是**一次 `where_is`**。**

### ⑤ 而这一轮**没有**接上它，理由要写清

**接上 `HandleResponseAsync` 会让 409 从「Declined」变成「可重试」。
那需要先决定哪一份表对 —— 而 `ClassifyCheckoutFailure` 的那份**有注释说明理由**，
`HandleResponseAsync` 的那份**没有**。**

> **→ 所以正确的动作是：把 `HandleResponseAsync` 的 409 改成不可重试（与有理由的那份对齐），
> 然后才谈接线。而「改哪一份」需要证据，不是偏好 —— 这一轮没取到。**
> **→ 记进 BLOCKERS，不自己决定。**

### ⑥ 顺手看到的一件事（未追）

**`HandleResponseAsync` 下面就紧挨着 `DetectAsync`（`StoreFlow.cs:368`），
它从响应 body / headers 里识别 anti-bot vendor：**
`cf-chl` → cloudflare · `kpsdk` → kasada · `_Incapsula_Resource` → imperva ·
`datadome` → datadome · `px-captcha` → perimeterx · `queue-it` → queue-it。

**那是优先级 ② 的实质内容。它接上没有、与 `vendor_coverage` 的 12/12 是什么关系 —— 本轮未查。**

### 数字

| 度量 | R992 | **R993** |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **状态码分类器** | 未测 | **2 份（1 份未接上）** |
| **两份之间的冲突码** | 未测 | **1（409）** |

### 教训

> **「不可得」和「我没找到」是两个不同的结论，而我上一轮把它们写成了同一个。
> R985 的证据（原版字符串里没有状态码分类）是对的，而它的**结论范围**被我扩大了 ——
> 从「原版里看不到」变成了「这里没有」。**
> **而一次 `where_is` 就能把范围收回来。**


### R989 那句「优先级 ② 的 vendor 覆盖是**完整的**」是**错的** —— 6 个墙里只有 2 个接通（R994）

**R993 说下一轮查 `DetectAsync` 接上没有。查的过程中发现那张表**早就在仓里**，
而它说的事与我在 R989 的结论相反。**

### ① 仓里有一张完整的墙接线审计表

**`src/Cybersole.Stores/Scripts/VendorWiring.cs`（R140/R141 建立）：**

| vendor | marker（检测） | cookie | **state** |
|---|---|---|---|
| cloudflare | `cf-chl` / `server: cloudflare` | `cf_clearance` | **Wired**（R140） |
| kasada | `kpsdk` | `kpsdk` | **Wired**（R141） |
| imperva | `_Incapsula_Resource` | 无 | **DetectedOnly** |
| datadome | `datadome` | `datadome` | **HostWithoutProtocol** |
| perimeterx | `px-captcha` | 无 | **DetectedOnly** |
| queue-it | `queue-it` | `queue-it-set-cookie` | **NotAChallenge** |

**而四个缺口各自有**不同**的原因，不是同一类：**

- **imperva**：镜像里既没有 Imperva 的 cookie，也没有 Imperva 的 host
- **datadome**：host 有（`datadome.cybersole.io`），**协议**没有
- **perimeterx**：注释写「deliberately blank: a token header exists, no `_px` cookie does」
- **queue-it**：**不是墙而是队列** —— 正确处置是**等**，不是求解

### ② 所以我在 R989 的结论错了

**R989 写：「优先级 ②（风控对抗）的 vendor 覆盖是**完整的**：cloudflare · kasada · datadome ·
perimeterx · queue-it · aycd · … 全 matched」。**

> **那个 12/12 来自 `vendor_coverage.py`，它答的是「这个厂商的名字在源码里出现过」。**
> **而 `VendorWiring` 答的是「检测 → 求解 → 存回，链条完整」。**
> **→ 两个问题的答案分别是 12/12 和 **2/6**。**
> **→ 而我把前者的答案写成了后者的结论 —— 这是同一个「名字出现 ≠ 接上」的错误，
> 只是这一层比 R989 修的那层更高：那一轮我修的是「两列用不同分母」，
> 这一轮发现其中一列问的根本不是这个问题。****

### ③ 而这个错误**已经被钉住了**，只是钉在另一个文件里

```
tests/Cybersole.Tests/VendorWiringTests.cs:37   Assert.Equal(6, VendorWiring.Rows.Count);
VendorWiringTests.cs:38                         Assert.Equal(new[] { "cloudflare", "kasada" }, VendorWiring.Wired);
VendorWiringTests.cs:48                         Assert.Equal(new[] { "imperva", "datadome", "perimeterx", "queue-it" }, …);
WallDispatchTests.cs:67-68                      Assert.Equal(new[] { "cloudflare", "kasada" }, …); Assert.Equal(4, Gaps.Count);
```

**→ 2 与 4 这两个数**已经有守卫**。所以「不知道」不是仓库的问题，是我没查。**

### ④ 而最刺的一件事：`VendorWiring.AuditRule` 早就写出了一句总结

```csharp
public const string AuditRule =
    "detection and storage are cheap and were already present; the call between them is the work";
```

**而 R992 的 `GetToken`（步骤存在、没有调用）与 R993 的 `HandleResponseAsync`
（分类表存在、不在执行路径上）—— 正是「检测和存储在、中间那个调用不在」。**

> **仓库在 R140 就把这句话写成了常量，并让测试钉住它。
> 而我在 R992–R993 花了三轮「发现」它。**
> **→ `where_is` 的纪律（R870，五次踩坑后立）在这里失效了三轮：
> 我查的都是**单个名字**（`GetToken` / `HandleResponseAsync` / `Detect`），
> 而没有查「这件事有没有一张表」。**

### ⑤ 所以优先级 ② 的真实剩余是**4 个墙**，而它们不是同一种活

| 墙 | 要做什么 | 缺什么 |
|---|---|---|
| imperva | 先在镜像里找到 cookie 家族或 host | **证据**，不是代码 |
| datadome | 写协议（host 已有） | 协议 —— 同 Cloudflare R140 之前的状态 |
| perimeterx | 先确认有没有 `_px` cookie | **证据** |
| queue-it | **不求解，等** | 一个等待策略，不是 solver |

> **→ 这比「12/12 全 matched」有用得多：它把「4 个缺口」分成「缺证据」与「缺代码」两类。**

### 数字

| 度量 | R993 | **R994** |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **墙的接线** | 未测 | **2 / 6 Wired** |
| **墙的缺口** | 未测 | **4（2 缺证据 · 1 缺协议 · 1 不是墙）** |
| **R989「vendor 覆盖完整」** | 已写 | **撤回** |

### 教训

> **`where_is` 查的是**名字**。而「这件事有没有一张表」是另一种查法，
> 而那张表可能早就把答案、原因分类、以及一句话总结都写好了。**
> **三轮的代价：我以为自己在发现，其实在重新发现。**


### DataDome 那行的**名字**错了，而 R141 的**判断**是对的（R995）

**R994 说下一轮做 datadome。取完证发现两件事：镜像里的协议比那张表说的多得多，
而「那张表被更正的判断还在被测试保护」这个说法，**只对了一半**。**

### ① 镜像里的 DataDome 是一条完整的链

```
<GenerateSensor>d__11   <SubmitSensor>d__12   <GetSensorData>d__34
sensorData(<datadomeCookie>5__2"<<SubmitCh>b__1>d
https://api-sdk.datadome.co/sdk/      https://datadome.cybersole.io/
https://datadome.cybersole.io/sensor
DataDomeKey  ·  DataDomeChallenge  ·  DatadomeSliderTask  ·  datadome=
Getting DataDome (I)  ·  Initialising DataDome  ·  Solving DataDome (I)  ·  Submitting DataDome (I)
```

> **三个 async 方法 + 一个 sensor 端点 + 四阶段顺序。
> 所以「有 host 无协议」是**错**的：协议就在镜像里。**
> **而这也正是 `WallSolving.DataDomeCorrection`（R141）写的那句：
> 「SolveBotD … the missing protocol is this workspace's gap, not the original's」。**

### ② 而我去看那条「保护错误」的测试，发现它**不是**

```csharp
// WallSolvingTests.cs:66（改前）
// but the audit's state stays as it is: this workspace still lacks the protocol
Assert.Equal(VendorWiring.State.HostWithoutProtocol, VendorWiring.For("datadome")!.State);
```

> **R141 是**有意**让状态停在 `HostWithoutProtocol` 的。
> 因为 `Wired` 的定义是「检测 → 求解 → **存回**」三件齐全，而**存回**我们没写。
> **→ 所以 R141 的判断完全正确：不能因为「原版能解」就把状态升成 Wired。**
> **→ 错的是那个**名字**：`HostWithoutProtocol` 说「协议不存在」，
> 而实际是「协议在原版里、缺在我们的笔记里」。**

**这两件事的差别是**归因方向**，而 `WallSolving.DataDomeCorrection` 已经把正确方向写下来了 ——
只是它没有可供 `VendorWiring` 用的词。**

### ③ 所以新增了一个 state，而不是把状态升成 Wired

```csharp
/// The original solves this vendor and this workspace has not written the call yet.
OriginalSolvesProtocolUnrecorded,
```

**它同时满足两边：**
- **不是 `Wired`** → R141 的意图保留（缺口仍在）
- **不说「协议不存在」** → 名字不再与同一仓库的更正相反

**而 `datadome` 那行的 note 现在写着 `SolveBotD` 与整条链，并指向 `WallSolving.DataDomeCorrection`。**

### ④ 而真正的新东西是一条**跨表**守卫

**`TheTwoAuditsAgree`：任何 `WallSolving.HasSolveFor(v)` 为真的厂商，
在 `VendorWiring` 里不得是 `HostWithoutProtocol` 或 `DetectedOnly`。**

> **理由：两张表都在同一个源码树里，各有各的测试，而**没有一条测试能看见另一张表**。
> 一张表说「无协议」、另一张说「原版能解」，两个断言都绿 ——
> 这正是 R978–R981 那三轮修的形状，只是这次不一致在**两张表之间**，不在一个脚本内部。**

**验过会红：把 datadome 行改回 `HostWithoutProtocol` → **2 条失败**，
其中 `TheTwoAuditsAgree` 是**独立**红的 —— 即使有人改了行却忘了改断言的期望值，它仍会红。**

```
把 datadome 行改回 HostWithoutProtocol
失败!  - 失败: 2，通过: 10，总计: 12
[FAIL] VendorWiringTests.TheGapsAreClassified
[FAIL] VendorWiringTests.TheTwoAuditsAgree
已还原
```

### ⑤ 而这一轮改了三处，全量套件从 2208 变 2209

| 文件 | 改了什么 |
|---|---|
| `Scripts/VendorWiring.cs` | 新增 `State.OriginalSolvesProtocolUnrecorded`；`datadome` 行改用它 + 新 note |
| `tests/.../VendorWiringTests.cs` | 断言改用新 state；新增 `TheTwoAuditsAgree` |
| `tests/.../WallSolvingTests.cs` | 断言改用新 state，并**保留**「不是 Wired」这一条 |

> **第三处是这一轮最要紧的一步：只改前两处会让 R141 的意图**消失**（缺口被读成已修）。
> 加上 `Assert.NotEqual(State.Wired, …)` 才把它钉住。**

### ⑥ 判据 (f) 的 4 个缺口现在只剩 **2 个缺证据**

| 墙 | 之前 | 现在 |
|---|---|---|
| imperva | 缺证据 | 缺证据 |
| **datadome** | **「缺协议」** | **协议在镜像里；缺的是调用** |
| perimeterx | 缺证据 | 缺证据 |
| queue-it | 不是墙 | 不是墙 |

**→ 而 `Wired` 仍是 **2 / 6** —— 这一个没动，因为**存回**那一步确实没写。**

### 数字

| 度量 | R994 | **R995** |
|---|---|---|
| 套件 | 2208 | **2209（+1 跨表守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 墙 Wired | 2 / 6 | **2 / 6（未变）** |
| **墙的四状态** | 4 种 | **5 种** |
| **跨表矛盾** | 1（datadome） | **0（现有守卫）** |

### 教训

> **我上一轮说「一个测试在保护一个已被更正的错误」—— 那句话是错的，而错的方式很有教益：
> 测试保护的**不是**错误结论，是**正确的**约束（缺口仍在），
> 而它用了一个**会误导的名字**去表达那个约束。**
> **→ 所以我差点把一条正确的守卫当成坏的改掉。这与 R980 那次（守卫对象为空）是同一课：
> 一个看起来在阻碍你的守兵，可能正站在正确的位置上。**


### DataDome 接上了 —— 墙从 **2/6** 到 **3/6**，而这一轮写了真代码（R996）

**R995 说下一轮写 DataDome 的存回调用。写了：新建 `Scripts/DataDomeClearance.cs`（125 行），
并在 `SolveDetectedWallAsync` 里加了一条分支。**

### ① 先看已 `Wired` 的两个是怎么接的

**`SolveDetectedWallAsync`（`StoreFlow.cs:406`）是**唯一的派发点**，而它只放行两个：**

```csharp
if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();   // datadome 走不到任何 solver
...
if (vendor == "cloudflare") { … CloudflareClearance.ApplyAsync … }
var kasada = KasadaStrategyRunner.Default();
return await KasadaClearance.ApplyAsync(…);
```

> **所以「有协议」还不够 —— 派发点的白名单里没有 datadome。
> 那正是 `Wired` 的意思：检测 → 求解 → 存回，**而三样都要有人调用**。**

### ② 写了什么

**`src/Cybersole.Stores/Scripts/DataDomeClearance.cs`，形状与 `CloudflareClearance.cs` 对称：**

| 元素 | 依据 |
|---|---|
| `SensorUrl = "https://" + AntiBotVendors.DataDomeSensor` | 镜像 `https://datadome.cybersole.io/sensor` |
| `SdkUrl = "https://" + AntiBotVendors.DataDomeSdk` | 镜像 `https://api-sdk.datadome.co/sdk/` |
| `ClearanceCookie = "datadome"` | `AntiBotProtocol.CookiesFor("DataDome")` 已记 |
| `Stages` 四条 | 镜像四句日志：Getting / Initialising / Solving / Submitting DataDome |
| `ApplyAsync` 存回 | `Vars[ClearanceVar] = token` **且** `Cookies["datadome"] = token` |
| 未配置时 | 返回**状态**而非错误（与 `ServiceCloudflareSolver` 同一决定） |

**而派发点加了一条：**

```csharp
if (vendor is not ("cloudflare" or "kasada" or "datadome")) return StepOutcome.Success();
...
if (vendor == "datadome")
{
    var sensor = InjectedDataDomeSensor.Default();
    return await DataDomeClearance.ApplyAsync(c, sensor, c.Url ?? string.Empty, ct);
}
```

### ③ 而「一个都没配」这件事被写成事实而不是失败

**`InjectedDataDomeSensor` 无 call 时返回：**

> 「DataDome relay not configured: the image names datadome.cybersole.io/sensor but this workspace has no credentials for it」

**→ 与 `cf-solver.cybersole.io` 探到 401 时 Cloudflare 那条路一样：host 是真的、要凭据，而凭据我们没有。
→ 所以**不假装成功**，也不当失败，而是把状态记下来让流程继续 —— 下一个请求再试。**

### ④ 而这一轮没有发明第二条路

**镜像只命名**一个 relay + 一个 SDK**。所以 DataDome 这边**没有** service→in-bot 的阶梯，
只有一条 `IDataDomeSensor`。**

> **`CloudflareClearance` 的注释写着 Cloudflare 有两条路（service 在前、本地在后），
> 而 DataDome 的镜像证据里没有第二条 —— 造一条会是镜像没有的策略。**

### ⑤ 改了 5 处断言，其中两处是「钉住 2/6」的

| 文件 | 改了什么 |
|---|---|
| `VendorWiring.cs` | datadome 行 → `State.Wired` + 新 note（引用 R141 的更正与派发点） |
| `VendorWiringTests.cs` | `Wired` 加 datadome；`Gaps` 去掉它；用例名 `TwoOfSixAreWired` → `ThreeOfSixAreWired` |
| `WallDispatchTests.cs` | 派发白名单串加 `datadome`；`Wired` 加它；`Gaps.Count` 4 → 3；注释「two wired, four gaps」→「three wired, three gaps」 |
| `WallSolvingTests.cs` | datadome → `Wired`；删掉 R995 那条 `Assert.NotEqual(Wired, …)`（它现在该等于） |

> **而 `VendorWiring.Wired` 的顺序是**行序**不是字母序**：`["cloudflare", "kasada", "datadome"]`。
> 第一次改成了字母序，测试立刻报 `Collections differ` —— **一个陈列顺序的假设，一次就露。**

### ⑥ 一个仍然诚实的边界

**`Wired` 现在说「三样都在」，而「求解」那一样在默认配置下**返回未配置**。
所以 3/6 的意思是：**调用链存在、派发到它、存回写对了**，而不是「这个墙在本机能过**。

> **这与 Cloudflare / Kasada 的 2/6 是**同一口径** —— 那两个的 service 路也需要凭据。
> 所以 3/6 没有虚高。**

### 数字

| 度量 | R995 | **R996** |
|---|---|---|
| 套件 | 2209 | **2209** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| **墙 Wired** | 2 / 6 | **3 / 6** |
| **墙的缺口** | 4 | **3（imperva 证据 · perimeterx 证据 · queue-it 等待）** |
| 新增源文件 | 0 | **1（`DataDomeClearance.cs`）** |

### 教训

> **`Wired` 这个词在这里不是「协议已知」，是「三样都有人调」。
> 而当我把 ProtocolUnrecorded 那种状态写出来之后，它看起来已经很像做完了 —— 一个更准确的名字
> 会让缺口显得更小。**
> **→ 一个标签的改善不等于工作的进展。R995 那个 state 是对的，而它一个字都没让墙过去。**


### 六个检测标记里**两个不在镜像里** —— 而 `cf-chl` 是其中一个（R997）

**R996 说下一轮取 imperva / perimeterx 的证据。取了，而它顺手翻出一个比那两个缺口更大的问题。**

### ① 六行标记，逐个探

| vendor | marker | 镜像命中 | 结论 |
|---|---|---|---|
| kasada | `kpsdk` | **17** | ✓ 真串 |
| queue-it | `queue-it` | **13** | ✓ 真串 |
| datadome | `datadome` | **15** | ✓ 真串 |
| perimeterx | `px-captcha` | （`_px3` 在，见下） | ✓ |
| **cloudflare** | **`cf-chl`** | **0** | ✗ **我们自己编的** |
| **imperva** | **`_Incapsula_Resource`** | **0** | ✗ **我们自己编的** |

> **而 Cloudflare 是**已声明 `Wired`** 的那一格。
> 也就是说：我们检测 Cloudflare 与 Imperva 的方式是**写出来的**，不是**抄下来的**。**
> **`cf-chl` 能工作，因为真实 Cloudflare 挑战页里确实有它 —— 但那是**常识**，不是镜像证据。
> 而一张 `Wired` 的行读起来像是抄来的。**

### ② 而 PerimeterX 的比我们记的多得多

```
0x1434ab609  _px3                              ← 「no _px cookie does」是错的
0x146f609b4  __pxvid   0x146f64474  _pxvid
0x146e3e764  PerimeterX-Token                  ← token header（这条我们有）
0x143336731  "PerimeterXHandler                ← 一个 Handler 类
0x146e3e70c  PerimeterX block (Rotating proxy) ← **封锁 + 代理轮换**
```

> **最后那句是这一轮的信息量所在：它说明原版把「被 PX 封」与**轮换代理**连起来处理。
> 那不是 token 名字，是**行为**。**
> **→ 而 `VendorWiring` 的 note 写着「deliberately blank: a token header exists, no `_px` cookie does」——
> 两处都错：`_px3` 在，而且不止一个 token header。**
> **→ 状态仍是 `DetectedOnly`（我们没有那个调用），但那不是「镜像里什么都没有」。**

### ③ 所以这一轮加的是**一列出处**，不是又改一个名字

**判据 (d)：每条 claim 要有 authority。而那张表的 marker 列**没有表明它是抄的还是写的**。**

**新增：**

```csharp
public enum MarkerSource { ImageLiteral, Inferred }
public sealed record Row(…, State State, string Note, MarkerSource MarkerFrom);
```

**六行各补一个：三个 `ImageLiteral`（kpsdk / queue-it / datadome）+ perimeterx 也是 `ImageLiteral`（`_px3` 在），
两个 `Inferred`（cloudflare / imperva）。**

### ④ 而守卫钉住的是**哪两个**，不是**几个**

```csharp
Assert.Equal(new[] { "cloudflare", "imperva" }, inferred);
```

> **测试没法重新探二进制，所以它钉住探针已经确立的**集合**。
> 要改动它，得重跑 `python analysis/ida.py str <marker>` 并在里面找到东西。**

### ⑤ 而 imperva 那行现在说得更全

**旧 note：「the image names no Imperva cookie and no Imperva host」
新 note：「the image names neither an Imperva cookie nor an Imperva host, **and does not contain this marker either**」**

> **后半句是新的，也是要紧的：不只是「没有 cookie 和 host」，而是**连我们用来检测它的那串都不在镜像里**。
> 所以 imperva 这条分支**整条**是我们自己写的，而它至今没被触发过（因为没有站用 Imperva）。**

### ⑥ 数字

| 度量 | R996 | **R997** |
|---|---|---|
| 套件 | 2209 | **2210（+1 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **marker 列有出处的行** | 0 / 6 | **6 / 6** |
| **`Inferred` 标记** | 未测 | **2（cloudflare · imperva）** |

### 教训

> **「检测用的标记」和「镜像里的串」是两件事，而那张表把它们写在同一个格子里。
> 一个 `Wired` 的行因此读起来像抄的 —— 而它的一半是编的。**
> **→ 判据 (d) 要求的不是「有证据」，是「**每条**写着它的证据是什么」。
> 我给六个厂商写了六行 note，而最要紧的那一列没有出处。**


### R997 标错了**一列** —— 而镜像里有一个更好的 PerimeterX 标记（R998）

**R997 给六行加了 `MarkerSource`，四个标 `ImageLiteral`。这一轮去验 perimeterx 那一行，发现它标错了，
而错的方式正是那一列要防的事。**

### ① 我验的是 cookie 列，而 `ImageLiteral` 说的是 marker 列

| 探测 | 命中 |
|---|---|
| **`px-captcha`**（marker 列写的） | **0** |
| `_px3`（cookie 列写的） | 1 |

> **R997 我查了 `_px3` 就标了 `ImageLiteral`，而那一列说的是**marker**。
> `px-captcha` 在镜像里**一次都不出现**。
> → 所以 `Inferred` 的集合是 **3 个**：cloudflare · imperva · **perimeterx**。**

**而这正是 `MarkerSource` 存在的理由 —— 它也抓到了写它的人。**

### ② 而镜像里有一个**可用**的 PerimeterX 标记

```
0x1470689dc  https://geo.captcha-delivery.com
0x147068a34  https://geo.captcha-delivery.com/
0x147068a8c  https://geo.captcha-delivery.com/interstitial/
```

**`captcha-delivery` 命中 4 次。`geo.captcha-delivery.com` 是 PerimeterX 的挑战域。**

> **所以我们一直在测一个自造的串（`px-captcha`），而镜像里有一个 host 级的、更可靠的标记。
> → 这不是「缺证据」：证据一直在，只是没去找。**
> **→ 而 R997 说 perimeterx「`_px3` 在，所以 `ImageLiteral`」—— 那句把**cookie 的存在**当成了**标记的存在**。**

### ③ 所以改了三处

**① `VendorWiring.cs`：perimeterx 行 → `MarkerSource.Inferred`；note 写明**
「R998 corrects R997's own row … R997 labelled the row ImageLiteral by checking the cookie column instead of the
marker column. The image does carry a usable marker: geo.captcha-delivery.com and its /interstitial/ path」。

**② `StoreFlow.DetectAsync`：加 `captcha-delivery` 分支，排在 `px-captcha` 之前。**

```csharp
// R998: the image names geo.captcha-delivery.com and its /interstitial/ path, four literals, and never
// px-captcha. Testing the marker the artifact actually carries is worth more than testing the one this
// workspace wrote from general knowledge, so both are accepted and the image's comes first.
body.Contains("captcha-delivery", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
```

**③ `VendorWiringTests.cs`：`Inferred` 集合 → `{ "cloudflare", "imperva", "perimeterx" }`。**

> **② 那一步不是「加个串」，是**检测方式从常识换成镜像证据**：
> 之前只有一个标记能认出 PerimeterX，而那一个不在产物里；现在先测产物里那个。**

### ④ 而 `DetectAsync` 的检测能力实际变强了

| 之前 | 现在 |
|---|---|
| `px-captcha`（镜像 0 命中） | `captcha-delivery`（镜像 4 命中）**优先**，`px-captcha` 后备 |

> **所以这一轮不只是修一个标注 —— 它让 PerimeterX 的检测**真的可能命中**，
> 而之前那条分支只能靠一个镜像里不存在的串去命中。**

### ⑤ 数字

| 度量 | R997 | **R998** |
|---|---|---|
| 套件 | 2210 | **2210** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **`Inferred` 标记** | 2 | **3（+perimeterx）** |
| **`DetectAsync` 里镜像有据的标记** | 4 / 6 | **5 / 6** |

### 教训

> **一列「出处」写下去的第一件事，是暴露**写它的人**没按那一列的定义去填。
> 我标 `ImageLiteral` 时看的是「这个厂商有镜像证据吗」，而那一列问的是「**这个格子里的串**在镜像里吗」。**
> **→ 两个问题的答案不同，而更宽的那个更容易让人满意。
> 一个刚加上的字段就能抓住作者 —— 这是它值得加的最好证据。**


### `METRICS.md` 的摘要表现在会说**哪些数老了**（R999）

**这一轮本来要去 publish 刷新函数数。1.8 GB 可用 —— 按纪律不 publish（AOT 是内存最重的操作）。
而在查「能不能 publish」的过程中发现了一件更要紧的事。**

### ① 摘要区把两个**过期的数**排成了当前值

```
| 函数数量（.pdata） — functions: replica .pdata | 173,952 |
| 函数数量（.pdata） — functions: ratio | 62.77% |
| 产物陈旧度（.publish-aot vs src） — source files newer than the artifact | 15 |
| 产物陈旧度（.publish-aot vs src） — lines in those files | 10753 |
| 变异套件（上次运行） — mutation-fit: staleness | 1:31:27 -- StoreFlow.cs changed after the run |
```

> **`173,952` 就在 `15 个源文件更新` 的**正上方**，中间只隔两行 —— 而那两行说它来自一次更旧的构建。
> 而 `artifact_freshness.py` 自己的注释早就写着这件事
> （「While it is stale that ratio describes an older build, so it **must be labelled as such wherever it is quoted**」），
> 而摘要区没有做。**
> **→ 而 `mutation-fit: staleness` 那一行写着 `1:31:27 -- StoreFlow.cs changed` —— 变异记录也过期了。**
> **→ 两个过期的数和一个当前套件数在同一列里，没有任何区分。**

### ② 而这两个是同一个问题：**摘要区没有时效这一维**

**每一个数都是「上次量到的」，而其中两个的**上次**已经不代表现在。
一个读这张表的人要靠**已经知道**哪个会过期，才能不错。**

### ③ 所以修的是**生成器**，不是数据

**`metrics_report.py` 在摘要表**之前**加一个自动生成的块：**

```
## 时效警告（生成）

> **函数数量那一行来自一个陈旧的 `.publish-aot`**：有 15 个源文件比产物新（共 10753 行）。
  它描述的是更旧的一次构建，不是当前源码。
```

**规则两条，都从工具输出里读，不是硬编码：**
- `source files newer than the artifact` ≠ 0 → 函数数那一行是陈旧的
- 某个 `staleness` 字段不以 `0` 开头 → 那一组数来自过期运行

### ④ 而顺手把变异重跑了（不耗内存，与 publish 不同）

```
running 36 of 36
fired 36 · decorative 0 · skipped 0 · restored GREEN
ran_at 2026-11-17T14:06:23+08:00
```

**→ 重跑之后，警告块从**两条**降到**一条** —— 因为变异那条 freshly 变成了 `0`。**

> **这正好证明那个块不是装饰：它跟着数据走。
> 一条警告消失，是因为被它警告的那件事**真的被做了**。**

### ⑤ 而剩下的那一条**修不了**，而它现在**说出来了**

**1.8 GB 可用 → AOT publish 会在这个内存下失败或拖垮机器（纪律：< 2GB 只跑 `-m:1`）。
所以函数数仍是 `173,952`，仍来自一个 15 个源文件之前的产物。**

> **而这一轮的产出不是让它变 fresh，是让它**不再沉默**。
> 一个不能修的缺口，至少不能被当成当前值读。**

### 数字

| 度量 | R998 | **R999** |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **15 / 10,753（未变，不能 publish）** |
| **变异陈旧度** | 1:31:27 | **0（已重跑）** |
| 变异 fired / 总 | 36 / 36 | **36 / 36（新记录 14:06:23）** |
| 函数数 | 173,952 | **173,952（陈旧，且现在被标注）** |
| **METRICS 摘要的时效警告** | 无这一维 | **1 条（生成）** |

### 教训

> **「所有文档引用 METRICS.md」这个规矩建立时，假设的是**表里的数都是当前的**。
> 而其中两个不是，规矩就把一个过期的数**提成了权威**。**
> **→ 一个单一数字源的价值取决于它说清每个数的**时效**，而不取决于它集中。
> 集中只是让它更容易被当成都对。**


### publish 完成 —— 而产物证明我**两处修复根本没进去**（R1000）

**内存回到 16.9 GB → publish 跑通（50 秒）。而量完之后最有价值的不是新数字，是一个否定结论。**

### ① publish 的数字

```
函数数   173,952 → 173,994（+42）
函数比   62.77%  → 62.79%
陈旧度   15 / 10,753 → 0 / 0
产物大小  53.4 MB → 53.5 MB
套件     2210 通过 / 0 失败 / 0 跳过
```

**而 R999 那个「时效警告（生成）」块**消失了** —— 因为被它警告的两件事都真的被做了。
（两次证明：R999 里变异那条消失，R1000 里产物这条消失。）**

### ② 而 `+42` 与 R963 记录的 `+42` 是同一个数 —— 查了，**不是同一件事**

**R963 记的是 `+42/+43/+43` 三段，而它的结论是：**

> **「那三段 +42/+43/+43 的真实来源是**静态协议类变得可达** —— 不是我写了步骤体。」
> 「`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁 ——
> 因为派发表靠 `MethodInfo.Invoke`，**反射在 NativeAOT 下不 root 方法**。」**

### ③ 所以我去验了一件事：这两轮的修复进产物了吗

**R991 把 `GetPaymentTokenAsync` 的伪造令牌改成 `Fail("… will not invent one")`；
R992 把 `GetTokenAsync` 改成 `Fail("… not invent a credential")`。**

**在两个产物里直接搜那两句话：**

| 串 | 新 `.publish-aot` | 旧 `.publish-aot-prev` |
|---|---|---|
| `will not invent one`（R991） | **absent** | absent |
| `not invent a credential`（R992） | **absent** | absent |
| `DataDome clearance acquired`（R996） | **IN（UTF-16LE）** | absent |

> **决定性：R991 与 R992 那两处改动**没有进产物**。
> R963 的规则兑现了 —— 零覆写的基类虚方法被裁掉，**改它的身体不改变产物**。
> → 而 R996 的 `DataDomeClearance`**进了**，因为它是被 `SolveDetectedWallAsync` **直接调用**的
> （静态可达），不是靠反射派发。**
> **→ 所以 `+42` 的来源可以**归因**：那个新静态类及其可达成员。
> 这不是 Inference —— 那句串在新产物里、旧产物里没有。**

### ④ 而这把 R991/R992 的成果**重新定位**了

**那两轮让源码不再伪造凭据 —— 那是对的，而它在**源码层**。
产物里没有那段代码，所以它对函数数、对运行时行为**都没有影响**。**

> **这不是白做（源码里一个伪造的兜底仍然该删），但它也**不是产物级进展**。
> 而如果只看函数数不变，会把它读成「那两轮没成果」；如果只看源码改对了，
> 会把它读成「产物里那条路现在正确了」—— **两个读法都错。**
> **→ 正确答案：**源码层正确，产物层不存在**。而后者是 R963 那条规则决定的，不是我决定的。**

### ⑤ 而那给出一个可操作的判断规则

**想让一个步骤**真的进产物**，二选一：**
1. **给它一个真实调用点**（像 `DataDomeClearance` 被 `SolveDetectedWallAsync` 直接调）
2. **让某个 flow 覆写它**（镜像里的形状就是「`GetCsrf` 二十份」）

> **而「把基类虚方法的身体写好」不属于这两条 —— 它是**源码整洁**，不是**产物进展**。**

### 数字

| 度量 | R999 | **R1000** |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **0 / 0（已 publish）** |
| **函数数** | 173,952（陈旧） | **173,994（当前）** |
| **函数比** | 62.77% | **62.79%** |
| 产物大小 | 53.4 MB | **53.5 MB** |
| **时效警告** | 1 条 | **0 条** |
| **R991/R992 的改动在产物里** | 未测 | **不在（两句话都 absent）** |

### 教训

> **「改对了源码」与「改动了产物」是两件事，而它们在某几轮里长得一模一样：
> 两种情况下套件都绿、两个文件都变了。**
> **→ 区分它们只需要一件事：**在产物里搜你写的那句话**。
> 而这件事我做了三轮才第一次做。**


### 加了 4 个网关，publish 成功，而产物里**一个都没进**（R1001）

**R1000 定了规则：进产物二选一 —— ① 真实调用点 ② flow 覆写。
这一轮按 ① 做了，而产物证明我对 ① 的理解**错了一半**。**

### ① 做的事

**`Gateways.cs` 追加 4 个网关（约 250 行），`PaymentGatewayRegistry.CreateDefault()` 里注册：**

| 网关 | 镜像给的端点 |
|---|---|
| `MollieGateway` | `ecommerce-gateway.mollie.com/api/v1/public/core/payments/poll` |
| `GmoGateway` | `degica.as1.gpayments.net/api/v2/brw/info/result?transId=` |
| `TouchtechGateway` | `retry.touchtechpayments.com/api/v1/:select` |
| `MidtransGateway` | `app.midtrans.com/snap/v1|v2/transactions` |

**每个网关四个方法（`TokenizeAsync` / `AuthorizeAsync` / `CompleteActionAsync` + `Id`/`Name`），
与既有 9 个同形。镜像只给一条路径的，其余步骤报「endpoint not captured」，不编路径
（R823/R991 的同一条原则）。构建成功、60 条网关/支付用例通过、4 条新守卫通过。**

### ② 而 publish 之后，产物里一个都不在

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| `ecommerce-gateway.mollie.com` | **absent** | absent |
| `degica.as1.gpayments.net` | **absent** | absent |
| `retry.touchtechpayments.com` | **absent** | absent |
| `app.midtrans.com` | **absent** | absent |
| `not captured` | **absent** | absent |

**→ 而函数数也**一个都没动**：173,994 → 173,994。**

### ③ 而判别性的那一组解释了一切

| 串 | 新 | 旧 |
|---|---|---|
| `api.stripe.com` · `paypal.com` | **IN** | IN |
| `api.sibspayments.com` · `squareup` · `unzer` · `omise` · `adyen` | absent | absent |
| **`PaymentGatewayRegistry`** | **absent** | absent |

> **`PaymentGatewayRegistry` 这个名字不在产物里，而 `CreateDefault` 在（别处的同名方法）。
> → 所以 `PaymentGatewayRegistry.CreateDefault()` **没有任何代码调用它**。
> → 整族网关是死代码，全被裁 —— 连既有那 9 个里的 7 个也不在。**
> **→ Stripe 与 PayPal 的 host 串从**别处**可达（大概是 UI 的支付方式枚举），所以它们留着。**

### ④ 所以 R1000 那条规则要**收紧一格**

**我上一轮写：「给它一个真实调用点（像 `DataDomeClearance` 被 `SolveDetectedWallAsync` 直接调）」。
而 `Register(new MollieGateway())` **看起来**就是一个调用点 —— 它在 `CreateDefault()` 里，
那是一句普通的构造调用。而它没让任何东西进产物。**

> **→ 真正的判据不是「有没有调用语句」，是「**从入口能不能走到**」。
> `CreateDefault()` 自己没人调，所以它里面的调用不计。
> → 这与 R963 那条（反射不 root 方法）是同一族但不同因：
> 那次是**调用方式**不可见，这次是**调用链**不可达。
> → 两者共同的检验方法完全相同：**在产物里搜。** 而这一步让两种都现形。**

### ⑤ 而这解释了优先级 ① 那 4 个真缺为什么一直补不上

**它们不是「缺一个类」，是「缺一条从 flow 到 registry 的可达路径」。
而既有 9 个网关里 7 个也不在产物里 —— 所以**整个支付层在产物里几乎不存在**。**

**→ 正确的修复是 R1000 的第二条路：让**具体的 flow** 覆写支付步骤，在覆写里直接调
`registry.Resolve(id)?.AuthorizeAsync(c, ct)`。那样调用链从 flow 出发，可达。**

### ⑥ 而这一轮的产出是**一个否命题加一条更准的规则**

**250 行代码没进产物 —— 那是行的浪费，也是**一条边界的确证**：
「注册」不是「接线」，「接线」不是「可达」。

**而它花了一轮就证完了，因为 R999 让产物陈旧度变成一句话就查得清的事，
R1000 让「在产物里搜」成为固定动作。**

### 数字

| 度量 | R1000 | **R1001** |
|---|---|---|
| 套件 | 2210 | **2214（+4 网关守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0（已 publish）** |
| **函数数** | 173,994 | **173,994（不动）** |
| 函数比 | 62.79% | **62.79%（不动）** |
| 新增网关类 | 0 | **4** |
| **其中进了产物** | — | **0** |
| **既有 9 个网关在产物里** | 未测 | **2（Stripe · PayPal）** |

### 教训

> **「我给它加了调用点」这句话可以完全为真，而不改变产物一个字节 ——
> 因为那个调用点在一条没人走的路上。**
> **→ 唯一不会骗人的检验是产物本身：搜它，或者数它。而我在 R1000 才第一次做，这一轮就靠它否掉了自己。**


### 一句接线把 250 行代码拉进了产物：**+0 → +342**（R1002）

**R1001 加了 4 个网关，publish 之后函数数**一个都不动**，因为 `CreateDefault()` 没人调。
这一轮只改两处，函数数涨了 **342**。**

### ① 改了什么

**① `PaymentGateway.cs`：加一个 `public static PaymentGatewayRegistry Default { get; } = CreateDefault();`**
**② `StoreFlow.SubmitPaymentAsync`：gateway 名解析出来之后先试注册表**

```csharp
var registered = Cybersole.Stores.Payments.PaymentGatewayRegistry.Default.Resolve(gateway);
if (registered is not null)
{
    var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
    …
}
```

**而选 `SubmitPaymentAsync` 的理由是**有 12 个覆写**（`DemandwareFlow` / `FarfetchFlow` / `FootsitesFlow` …）——
R963 那条「零覆写的基类体被裁」的反面。**

### ② 为什么这一处能通，而 R1001 那处不能

**R1001 说「我给它加了调用点」：`Register(new MollieGateway())` 在 `CreateDefault()` 里，
那是一句普通的构造调用 —— 而**没有人调 `CreateDefault()`**，所以整条链不可达。**

**这一轮的调用点在 `SubmitPaymentAsync` 里，而那个方法有 12 个覆写，
所以基类体被保留，`registry.Resolve` 从覆写出发可达。**

> **→ 所以 R1000 那条规则要写成三档，而不是两档：
> ① 从入口可达 ② 被覆写（覆写的体进产物，且该方法被保留）③ 两者都没有（被裁）。
> 「有调用语句」不构成任何一档。**

### ③ 产物验证（这一次是肯定的）

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| **`PaymentGatewayRegistry`** | **IN** | absent |
| **`ecommerce-gateway.mollie.com`** | **IN** | absent |
| **`degica.as1.gpayments.net`** | **IN** | absent |
| **`retry.touchtechpayments.com`** | **IN** | absent |
| **`app.midtrans.com`** | **IN** | absent |
| `api.sibspayments.com` · `api.unzer.com` · `api.omise.co` | **IN** | absent |
| `api.stripe.com` · `paypal.com` | IN | IN |
| `api.squareup.com` · `adyen.com` | absent | absent |
| `needs a 3-D Secure step` | **absent** | absent |

**→ 产物里的网关从 **2 个变成 9 个**。**
**→ 而 `needs a 3-D Secure step` absent：那条 `RequiresAction` 分支没被保留，
可达的是 `AuthorizeAsync` 本身 —— 一个诚实的细节，不是失败。**
**→ `squareup` / `adyen` 仍 absent：它们不在这一轮的可达集里（`AdyenGateway` 在另一个文件，
`SquareGateway` 的 host 常量可能是别的拼法）。**

### ④ 函数数 **+342**，比 +0.12 个百分点

| 度量 | R1001 | **R1002** |
|---|---|---|
| **函数数** | 173,994 | **174,336（+342）** |
| **函数比** | 62.79% | **62.91%** |
| 套件 | 2214 | **2214** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物里网关 | 2 | **9** |

> **+342 的量级对得上：9 个网关类各自的四方法 + 闭包 + `JObject` 构造 + 字符串插值
> + `PaymentGatewayRegistry` 的 `Dictionary`。而这一整族在 R1001 里是 0。**

### ⑤ 而这一轮真正建立的东西

**同一份 250 行代码，同样 publish 成功、套件同样绿、陈旧度同样 0 —— 而函数数一次 +0、一次 +342。
唯一的差别是**那一行 `Resolve` 在不在一条可达的路上**。**

> **→ 所以「产物对得上源码」这件事，不能靠「我改了、我发布了、套件绿了」来确认。
> 它只有两种可信的确认方式：**在产物里搜一个只有那段代码才会有的串**，或者**看函数数动没动**。
> 而两者的前提是同一条：先说得出那段代码**为什么可达**。**

### 教训

> **「加了 250 行」和「产物多了 342 个函数」之间，隔着一句 `Resolve`。
> 而我在 R1001 里以为注册就是那句 —— 注册只是把新类放在一条没人走的走廊上。**
> **→ 可达性是**独立于代码量**的一个维度。它不写在任何一行里，只能被证明或被否证。**


### 可达性**精确到方法**，不是到类 —— 而我两次搜错了串（R1003）

**R1002 留下一句「`squareup` / `adyen` 仍 absent」，这一轮去核，发现那句话里有两个错误，都在我这边。**

### ① 我搜的串根本不是源码里的串

| 网关 | 源码里真实的 host 常量 | 我 R1002 搜的 |
|---|---|---|
| `SquareGateway` | **`pci-connect.squareup.com`** | `api.squareup.com` |
| `AdyenGateway` | **`checkoutshopper-live.adyen.com`** | `adyen.com` |

> **→ 一个是我臆造的前缀（`api.`），一个是把品牌名当 host。
> → 所以「absent」不是产物的结论，是我**搜错了**。
> → 这又是 AGENTS.md §2.7 那个形状：**先假设形状，再把「不符合假设」读成「不存在」。**
> 这是第 **十** 次。**

### ② 用正确拼法重搜，图景变精确

| 网关 | 主 host | 次 host |
|---|---|---|
| Square · Stripe · Unzer · Omise · Paynamics · Sibs · PayPal | **IN** | — |
| Mollie · GMO · Touchtech · Midtrans | **IN** | — |
| **Adyen** | **absent** | — |
| **CommerceHub** | **absent** | — |
| （各家的次 host） | — | `api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1.paynamics.net` · `shield.paynamics.net` **全 absent** |

### ③ 而规律解释了全部

**`IN` 的每一条，都是 `AuthorizeAsync` 里 `$"{ApiHost}/…"` 引用的那一段。
`absent` 的次 host，全在 `TokenizeAsync` 或 `CompleteActionAsync` 里。**

**而 R1002 只接了一处：**

```csharp
var outcome = await registered.AuthorizeAsync(c, ct).ConfigureAwait(false);
```

> **→ 所以可达性**精确到方法**，不是到类。
> 「这个网关进了产物」和「这个网关的三个方法都进了产物」是两个陈述，
> 而 R1002 只做到了前者，而我在那一轮把它读成了后者。**

### ④ 而 Adyen 与 CommerceHub 整个不在，原因不同

**它们连 `AuthorizeAsync` 的 host 都不在 —— 而那一条是被 `SubmitPaymentAsync` 直接调的。
所以问题不在可达性，在**它们的 `Id` 没被 `Resolve` 命中**。**

**`AdyenGateway` 的 `Id` 是什么？若它是 `"adyen"` 而 `ChooseGateway` 从不产 `"adyen"`，
那 `Resolve` 永远返回 null，整个类被裁 —— 与 `CreateDefault` 那次同一形状，只是发生在 id 上。**

**→ 那是一个待证的具体问题，不是「Adyen 缺证据」。**

### ⑤ 这一轮的产出是**一个精确化 + 两次自我纠正**

**上一轮我写「产物里网关 2 → 9」。按这一轮的图景，更准确的是：
**产物里有 11 个网关的 `AuthorizeAsync`，7 个的次 host 一个都没有，2 个整个不在。**
而那两个不在的原因是可查的（id 不匹配），不是不可得。**

### 数字

| 度量 | R1002 | **R1003** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **主 host 在产物的网关** | 记作 9 | **11** |
| **次 host 一个都没有的网关** | 未测 | **7（`TokenizeAsync` / `CompleteActionAsync` 全裁）** |
| **整个不在的网关** | 记作 2 | **2（Adyen · CommerceHub，原因可查）** |

### 教训

> **「进了产物」要说到**哪一层**：类、方法、还是那一行。
> 我在 R1002 说「9 个网关进了」，实际是「9 个网关的**一个方法**进了」。
> **→ 而两个记录都「对」，只是粒度不同 —— 而粗的那个听起来完成了更多。**


### Adyen 与 CommerceHub **在**产物里 —— 被裁的是它们的方法体（R1004）

**R1003 留下一句「Adyen 与 CommerceHub 整个不在，问题在 id 没被 `Resolve` 命中」。这一轮查了，
那句话的两半**都要改**。**

### ① 先否掉 id 假设

```csharp
AdyenGateway.Id        => "adyen"
CommerceHubGateway.Id  => "commercehub"

// PaymentGatewayRegistry.Resolve
id is not null && _gateways.TryGetValue(id, out var g) ? g : null;   // 字典是 OrdinalIgnoreCase

// ChooseGateway：返回 available（即 Vars["paymentMethods"]，商店页提供的名字）里的一项
```

> **→ `Resolve` 大小写不敏感，`"adyen"` 能命中。所以 id 不是原因。
> → R1003 那个假设错了。**

### ② 再用**非 host** 的特征串验，仍然全 absent

| 串 | 新产物 |
|---|---|
| `adyen: no card` · `adyen.merchantAccount` · `CybersoleECOM` · `encryptedCardNumber` | **全 absent** |
| `commercehub: sale failed` · `commercehub.sessionId` · `tokenUUID` · `/api/v1/sale` | **全 absent** |

**→ 到这里看起来仍是「整个不在」。**

### ③ 而短串的计数把它翻了过来

```
adyen        UTF-16 x19   UTF-8 x0
commercehub  UTF-16 x17   UTF-8 x0
CommerceHub  UTF-16 x0    UTF-8 x1
square       UTF-16 x10   UTF-8 x7
omise        UTF-16 x52   UTF-8 x89
```

> **`adyen` 出现 **19 次**、`commercehub` **17 次** —— 它们**在**产物里。
> 而它们的长串一个都不在。**
> **→ 所以类被保留（`Id` 可达），`AuthorizeAsync` 的**方法体被裁**。
> → 这是「可达性精确到方法」的**下一层**：**类在、`Id` 在、方法体不在**。**

### ④ 而这解释了两处读数的差

| 说法 | 出处 | 准不准 |
|---|---|---|
| 「整个支付层在产物里几乎不存在」 | R1001 | **不准** —— 类与前两个方法都在 |
| 「9 个网关进了产物」 | R1002 | 偏粗 —— 是 9 个的 `AuthorizeAsync` |
| 「Adyen / CommerceHub 整个不在」 | R1003 | **不准** —— `Id` 在，方法体不在 |

**而三次都是在同一个方向上**高估了裁剪**：把一个方法体的缺席读成一个类、乃至一个层的缺席。**

### ⑤ 而方法体为什么被裁，两个原因不同

**`AdyenGateway.AuthorizeAsync` 里没有 host 串（`ShopperHost` 在 `CompleteActionAsync` / `TokenizeAsync` 里），
它调的是 `Encrypt(...)` 与运行时 URL。**

**`CommerceHubGateway.AuthorizeAsync` 用 `Host(c)` —— 一个**从 session Vars 读 host** 的私有方法，
所以 `DefaultHost` 这个常量只在某个分支里被引用，而那个分支被裁。**

> **→ 两者都不是「不可达」，而是**被裁到了只剩签名**。
> → 而触发裁剪的具体机制（接口派发的类型集合、还是方法体里的某个 `RequiresUnreferencedCode`）
> **本轮未证 —— 标 Unknown。**

### 数字

| 度量 | R1003 | **R1004** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **id 在产物的网关** | 未测 | **13 / 13** |
| **`AuthorizeAsync` 方法体在产物的网关** | 记作 11 | **11** |
| **长特征串全无、id 却在的网关** | 记作 2「整个不在」 | **2（Adyen · CommerceHub）** |

### 教训

> **同一个方向的错误我犯了三次：**把方法体的缺席读成类的缺席**。
> 而这次的判别手段是**短串计数** —— 长串 absent 只说明那一段代码不在，
> 短串计数才说明那个类型的**名字**还在不在。**
> **→ 「在不在产物里」这句话，对长串和对类型名是两个不同的问题，而我一直用一个答案回答两个。**


### 409 的两难消失了 —— 因为原版**不按状态码分类**（R1005）

**R993 留下一句「两份表哪一份对，需要证据」。这一轮取了证据，而它把那个二选一**取消了**。**

### ① 先按 goal 的流程把 IDA 弄起来（三个框，一个新框型）

```
PROXY: MISSING   INSTANCE: none   PORT 13337: REFUSED   TIMEOUT: 180s
```

**代理仍然缺失（属停下等 YG 的条件），而 **IDA 自己起来了**、只是停在对话框上。
`analysis/ida.py` 直连插件的 13337，不走 DSH 代理，所以清框即可用。**

| 框 | 处置 |
|---|---|
| 「IDA has found an unpacked version」 | **Proceed with unpacked base**（goal 指定） |
| 「id0 is not closed. repair it?」 | **是(Y)**（goal 指定） |
| 「请稍候…」 | **等，不点**（goal 指定） |
| **「Database still contains inconsistencies」** | **确定** —— **新框型，本轮补记**；只有这一个按钮，信息性 |

**→ `13337 LISTENING pid=44936`，标题 `IDA - Cybersole.exe.i64`。**

### ② 409 的状态码语义：镜像**不提供**

| 探测 | 命中 | 是什么 |
|---|---|---|
| `409` | 40 | 全是十六进制哈希（`1409A77B…`），**无状态码语义** |
| `Conflict` | 30 | `.NET` 枚举名（`Conflicte` / `DeprecatedLegacyJsonFieldConflicts`） |
| `unavailable` | 40 | HTTP 枚举名（`ServiceUnavailable` / `UnavailableForLegalReasons`） |

> **→ 镜像里没有「409 → 某种处置」的对照表。有的只是 HTTP 枚举的**名字**。
> → 所以 R993 那个问题（「哪份表对」）在原版的**状态码层**上无解 —— 那里没有表。**

### ③ 而原版在**消息层**给了答案

```
0x146e2c6cc  Out of stock (reservation failed), retrying
0x146e6ab6c  Reservation failed (
0x146dd0644  Item is Out of Stock
0x146e2c68c  Out of stock (decoy)
0x146edb584  The product in the cart is out of stock.
```

**`out of stock` 共 7 条，而它们**不是同一件事**：**

| 消息 | 处置 |
|---|---|
| `Out of stock (reservation failed), **retrying**` | **重试** |
| `Out of stock (decoy)` | **诱饵** —— 不是真缺货（另有 `get_DecoyActive` 状态） |
| `Item is Out of Stock` · `This item is out of stock` | 真缺货 |

> **→ 所以「缺货要不要重试」的判据是**消息内容**，不是状态码。
> → 而两份表（`ClassifyCheckoutFailure` 409=Declined · `HandleResponseAsync` 409=retryable）
> **同错**：都在按状态码分类，而原版按**消息**分类。**

### ④ 所以修法不是「选哪一份」，是**加一层**

**两难的形状是「A 说甲、B 说乙，哪个对」。而证据说：问题问错了层次。
409 的状态码层没有语义；语义在响应体里。**

**正确的修法：**
1. 状态码层保持**保守**（409 → Declined，因为多数 409 是售罄）
2. **加一条消息级升级**：体里含 `reservation failed` → **可重试**
3. 体里含 `decoy` → **不重试**（诱饵，重试会加深可疑）

**→ 而这三条各自有字符串证据，不是偏好。**

### ⑤ 本轮未改代码，因为接线前要先定这条顺序

**`HandleResponseAsync` 仍未接上 —— 而接它之前必须先有消息层，
否则 409 会一律变可重试（= 重试已经卖出的东西）。**

**→ 那正是 R993 说的「必须先对齐再接线」。而这一轮把「对齐什么」问清楚了：
不是两份表对齐，是**加一层它们都没有的东西**。**

### 数字

| 度量 | R1004 | **R1005** |
|---|---|---|
| 套件 | 2214 | **2214（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **409 状态码语义在镜像** | 未测 | **无（40 条全是哈希/枚举名）** |
| **缺货消息分类** | 未测 | **3 类（真缺货 / reservation failed→重试 / decoy→不重试）** |
| IDA 框型 | 3 种 | **4 种（+「仍含不一致」→确定）** |

### 教训

> **「A 和 B 矛盾，哪个对」这个问法本身可能错 —— 也许两个都在错的层次上回答。
> → R993 把问题设成二选一，而镜像的证据说：状态码层没有语义。
> → 而**取证的第一个用途不是选边，是检查那个二选一是否成立**。**


### 消息层写对了，没进产物 —— 而我的「可达性」读数自己和自己矛盾（R1006）

**R1005 说下一轮按三条证据加消息层。加了，11 条测试绿。而 publish 之后产物里一个串都不在。
更要紧的是：这一轮把 R1002 那个可达性结论**否掉了**。**

### ① 写了什么

**`StoreFlowRunner.ClassifyCheckoutFailure` 前面加一层消息判断：**

```csharp
private static readonly string[] RetryableShortage = { "reservation failed" };
private static readonly string[] NeverRetryShortage = { "decoy" };

private static CheckoutResult ClassifyCheckoutFailure(FlowContext ctx) =>
    FromShortageMessage(ctx) ?? LastStatus(ctx) switch
    {
        422 or 409 => CheckoutResult.Declined,
        402 => CheckoutResult.Declined,
        _ => CheckoutResult.Error,
    };
```

**顺序是「状态码是外层猜测，消息细化它」—— 因为多数 409 确实是售罄，而那一个例外在体里说出来。
两个标记同时出现时**拒绝优先**：错的重试花掉账号，错的放弃只花掉这一次尝试。**

**而 `Vars["home"]` 是**首页**，缺货消息在 **checkout 响应**里 —— 所以补了一个新活通道：
`lastStatus` 的 5 个写入点旁边各写一行 `Vars["lastBody"]`。**

**11 条测试绿（4 新 + 7 既有 `CheckoutFailureModeTests`，`{}` 体无标记 → 仍 `Declined`，没破既有行为）。**

### ② 而 publish 之后，产物里一个都不在

| 串 | 新 `.publish-aot` | 旧 |
|---|---|---|
| `reservation failed` | **absent** | absent |
| `decoy` | **absent** | absent |
| **`lastBody`** | **absent** | absent |
| `sold out during checkout`（既有注释） | absent | absent |

**→ 函数数 **174,336 未变**。**

### ③ 而判别组把 R1002 的结论否掉了

| 串 | 新产物 | **R1002 我记的** |
|---|---|---|
| `StoreFlowRunner` | **absent** | **IN** |
| `GuardAsync` | **absent** | **IN** |
| `lastStatus` | **absent** | absent（一致） |
| `antibot` | IN | IN |

> **→ `StoreFlowRunner` 与 `GuardAsync` 现在 absent，而 R1002 我记的是 IN。
> → 而函数数在 R1002 之后**没变**（174,336 → 174,336），所以这不是裁剪变化。
> → 所以**其中一次的读数是错的**，而我留的记录不足以判断是哪一次。**

### ④ 而这否掉的不止一条读数

**R1002 的 `+342` 我用它论证「接一句 `Resolve` 就让 250 行达标」。而那个论证的可达性依据
（`StoreFlowRunner` / `GuardAsync` 在产物里）现在不成立。**

**→ `+342` 仍然是真的（函数数确实涨了）。但「为什么涨」的那个解释建立在一条现在矛盾的读数上。
→ 而 R1004「Adyen/CommerceHub 的 `Id` 在产物里 19/17 次」那条也是同类读数 —— 同样需要重验。**

**这一轮不重验，因为重验需要一条**稳定的**读数方法，而那件事本身要先设计。**

### ⑤ 所以这一轮真正的产出是三条

1. **消息层在源码与测试里正确**（11 条绿），而**产物里不在** —— 那一条是清楚的、可复现的
2. **`lastBody` 通道补上了**（`home` 是首页，缺货消息在 checkout 响应里 —— 那是实现里的一个真错）
3. **R1002 的可达性结论撤回** —— 依据是同一段字节里 `StoreFlowRunner` absent，而函数数未变

### ⑥ 而「读数不稳定」的可能原因（未证，标 Unknown）

- 两次查的**不是同一个文件**（R1002 查 `.publish-aot`，那一份在 R999 之后被替换过两次）
- 或者某次 publish 的裁剪结果不同而函数数恰好相同
- **而未证的我不写成结论。**

### 数字

| 度量 | R1005 | **R1006** |
|---|---|---|
| 套件 | 2214 | **2218（+4 缺货消息守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 174,336 | **174,336（未变）** |
| 函数比 | 62.91% | **62.91%** |
| **消息层进产物** | — | **否（3 个串全 absent）** |
| **R1002 的可达性读数** | 采信 | **撤回（与当前读数矛盾）** |

### 教训

> **产物读数是一个**观测**，而观测要有稳定的对象和记录。我拿三次不同 publish 的读数当一条时间线用，
> 于是其中任何一次读错都会变成一个「事实」进入论证。**
> **→ 而这一轮能发现它，是因为我**又查了一遍**同样几个串 —— 不是因为方法更好。**


### 新工具一击推翻了我上一轮的自我否证 —— 原因是我只查了一种编码（R1007）

**R1006 说「`StoreFlowRunner` / `GuardAsync` 现在 absent，而 R1002 记的是 IN，所以其中一次读数错了，
R1002 的可达性结论撤回」。这一轮造了稳定读数工具，第一次跑就把那句话推翻了。**

### ① 工具：`tools/artifact_probe.py`

**它做的事很少，而缺的正是这一点：每次探测都记录**产物身份**（sha256 / 字节数 / mtime），
并把结果追加到 `analysis/ARTIFACT_PROBES.json`。**

**文件头写了为什么现成的够不到（AGENTS.md §1 规则 2）：
`where_is.py` 答复刻件源码，`analysis/ida.py str` 答原版数据库，`pe_triage.py` 答布局 ——
没有一个是「这个字面量在**这个**二进制里吗，是**哪一个**二进制答的」。**

### ② 第一次跑的结果

```
artifact  .publish-aot/Cybersole.Ui.exe
sha256    36c16b3b3fd536d23cf4920603afc7761729a505ed4e0975de38444912891409
bytes     56183808   mtime 2026-11-17T16:26:54

  string              utf-16-le   utf-8   present
  StoreFlowRunner             0       1   yes
  GuardAsync                  0       2   yes
  lastStatus                  0       0   no
  lastBody                    0       0   no
  reservation failed          0       0   no
  decoy                       0       0   no
  antibot                      3       0   yes
```

### ③ 决定性：`StoreFlowRunner` 与 `GuardAsync` **在**产物里，以 **UTF-8** 形式

**→ 我 R1006 只查了 **UTF-16LE**，所以报 absent。
→ 所以「R1002 记 IN、R1006 记 absent」**不是产物变了，也不是 R1002 读错** ——
  是我 R1006 那次只查了一半编码。**

**→ 而 R967 早就立了这条：「反射元数据（类型/方法名）是 **UTF-8**；字符串字面量是 **UTF-16LE**。
  查错一种会给出一个自信的「没有」。」**

> **→ 我在 R1006 违反了它，然后把这个假阴性当成「读数矛盾」，
> 进而写了一条自我否证，还撤回了 R1002 一条本来正确的结论。**
> **→ 而新工具第一次运行就把它纠正了 —— 因为它**同时**查两种编码，而我的手写探测只查一种。**

### ④ 而消息层那四个串两种编码都是 0 —— 那部分是**真的**

| 串 | UTF-16LE | UTF-8 |
|---|---|---|
| `lastStatus` | 0 | 0 |
| `lastBody` | 0 | 0 |
| `reservation failed` | 0 | 0 |
| `decoy` | 0 | 0 |

**→ 所以 R1006 的另一半结论对：消息层**确实**没进产物。
→ 而这一半现在有了带产物身份的读数支撑，不再是我的印象。**

### ⑤ 三个结论的最终状态

| R1006 说的 | 现在 |
|---|---|
| `StoreFlowRunner` / `GuardAsync` absent | **错 —— 在，UTF-8** |
| 「R1002 的可达性结论撤回」 | **撤回该撤回 —— R1002 的 IN 是对的** |
| 消息层没进产物 | **对，且现在有产物身份作证** |
| 「读数为何矛盾」Unknown | **已知：只查一种编码** |

### ⑥ 而同一份产物里两种编码并存

**`GuardAsync` 是 UTF-8（2 次），`antibot` 是 UTF-16LE（3 次）—— 同一个文件。
→ 所以「用哪种编码查」不是可以被默认值替掉的事，它是**每次都要问**的事。
→ 而工具现在强制同时查两种并存两列，那比一条纪律更难违反。**

### 数字

| 度量 | R1006 | **R1007** |
|---|---|---|
| 套件 | 2218 | **2218（未改产品代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **带产物身份的读数** | 0（手写探测） | **全部（新工具）** |
| **R1002 可达性结论** | R1006 撤回 | **恢复（IN 是对的）** |
| **消息层进产物** | 否（一种编码） | **否（两种编码，sha256 背书）** |

### 教训

> **「两次读数矛盾」有第三种解释：**两次问的不是同一个问题**。
> R1006 我把它读成「其中一次错了」，而它其实是「其中一次只查了一半」。
> **→ 一个带身份的读数工具之所以值得写，不是因为它更准 ——
> 是因为它让「问的是不是同一个问题」变成一件**看得见**的事。**


### R1004 的读数被新工具确认；而 `paymentMethodsUrl` 是**第二个自造键名**（R1008）

**R1007 说下一轮用新工具重验 R1004。验了，结论成立；而顺手在优先级 ① 上找到同一类错误的第二例。**

### ① 重验 R1004（双编码 + sha256 背书）

```
artifact  .publish-aot/Cybersole.Ui.exe
sha256    36c16b3b3fd536d23cf4920603afc7761729a505ed4e0975de38444912891409

  adyen                          utf-16-le 19   utf-8 0   yes
  Adyen                          utf-16-le  2   utf-8 1   yes
  commercehub                    utf-16-le 17   utf-8 0   yes
  CommerceHub                    utf-16-le  0   utf-8 1   yes
  CybersoleECOM                           0         0   no
  encryptedCardNumber                     0         0   no
  tokenUUID                               0         0   no
  /api/v1/sale                            0         0   no
  checkoutshopper-live.adyen.com          0         0   no
```

**→ R1004 的结论**成立**：`Id` / `Name` 属性在产物里，`AuthorizeAsync` 的方法体串一个都不在。**
**→ 而它给出一条更细的事实：**同一个类**里，小写 id 是 **UTF-16LE**（19/17），
大写 Name 是 **UTF-8**（1）。所以「哪种编码」连在**一个类型内部**都不统一。**

### ② 而优先级 ① 上找到同一类错误的第二例

**`GetPaymentMethodsAsync` 读 `Vars["paymentMethodsUrl"]`。查镜像：**

```
paymentMethodsUrl   0 命中
```

**→ 那个键名**不在镜像里**。它是 self-made。**
**→ 而 R956 修过的 `paymentGateway`（→ `_paymentGatewayName`）是**第一个**，这是第二个。**

> **两者同形：一个能编译、读起来正确的名字，所以没人会怀疑它。
> 差别在于这一个**没有替代名可得**。**

### ③ 而镜像里那个步骤是真的，连 ordinal 都对

```
0x14337f4a9  (RpcGetPaymentMethodsg
0x1433800e6  <<RpcGetPaymentMethods>b__177_0<<RpcGetPaymentMethods>b__177_1g   ← 两个 lambda
0x14337f4c9  RpcSubmitCardg
0x14338012e  .<RpcSubmitCard>b__178_2g
```

**→ `RpcGetPaymentMethods` 是真实的状态机，带**两个** lambda；`RpcSubmitCard` 带一个。
→ 而 `177` 与 `StoreFlow.cs` 注释里的 `177 RpcGetPaymentMethods` **对得上** —— 那条注释是对的。**

**→ 缺的不是步骤、不是 ordinal，是**路由**。而 R958 已确立「按名字反编译在 NativeAOT 下不成立」，
所以路由目前**不可得**，不是「没找到」。**

### ④ 所以这一轮改的是「让它可见」，不是「修好它」

**`GetPaymentMethodsAsync` 的注释现在写明三件事：**
1. `paymentMethodsUrl` 在镜像里两编码皆 0 —— 这个键名是自造的
2. 镜像有那个步骤（`RpcGetPaymentMethods` + 两 lambda），ordinal 177 对得上
3. **路由不可得**，且 R963 意味着零覆写 → 这个方法整个被裁

**并加守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`：钉住「键名在、注释在、
且『No flow overrides this method today』在」。**

> **→ 守卫的判据不是「这个名字对不对」（它不对），而是「读源码的人会不会以为它被搜过」。
> 那条注释让后者不成立。**

### ⑤ 数字

| 度量 | R1007 | **R1008** |
|---|---|---|
| 套件 | 2218 | **2219（+1 自造键名守卫）** |
| 产物陈旧度 | 0 / 0 | **1 / 2,671（只改了注释）** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **R1004 读数** | 需重验 | **确认（双编码 + sha256）** |
| **已知自造键名** | 1（`paymentGateway`，R956 已修） | **2（+`paymentMethodsUrl`，无替代名）** |

### 教训

> **「自造键名」不是一次性的失误，它有一个**稳定的成因**：
> 一个编译得过、读起来对的名字，没有任何机制会质疑它。
> **→ 而唯一能发现它的动作是**去镜像里查那个名字** —— 那一步 R956 做过一次，
> 而 `paymentMethodsUrl` 从写下那天起活到 R1008 才被查。
> **→ 所以这一轮的守卫钉的不是名字，是「这个名字没被搜过」这件事的说法。****


### 326 个会话键一次问完 —— 而 `lastStatus` 从来就**不在**产物里（R1009）

**R1008 说下一轮扫「所有 `Vars[...]` 键名对镜像查一遍」。扫了。而结果里最重的一条不是「有多少自造」，
是它解释了 R1006 那个悬案。**

### ① 工具：`analysis/vars_key_provenance.py`

**两阶段：**
1. **`analysis/pe_strings.txt`**（抽样 180,228 / 324,895）—— 命中即证明存在，未命中不证明什么（§2.7b）
2. **剩下的用 `analysis/ida.py str` 查 IDB** —— 两个方向都权威

**输出 `analysis/VARS_KEY_PROVENANCE.md`。**

### ② 而第一阶段完全失效 —— 326 个全走了 IDB

```
distinct keys: 326   settled by the sample: 0   to ask the IDB: 326
absent: 159   present-after-IDB: 152   unresolved: 15
```

**→ `settled by the sample: 0` —— 我的 `"\n" + key + "\n"` 匹配对抽样文件的格式不对，
所以第一阶段一个都没settle，326 个全部逐串问 IDB。**
**→ 那个「快路径」没起作用，而整个扫描仍跑完了（约 15 分钟）—— 慢但不至于不可行。**
**→ 这是一个应当记下的实现缺陷：两阶段设计里第一阶段是死的，等于只做了一阶段。**

### ③ 而 159 个 absent 分成两类，性质**完全不同**

| 类 | 数 | 说明 |
|---|---|---|
| **带点（模块命名空间）** | **97** | `adyen.*` · `kasada.*` · `paypal.*` · `stripe.*` · `square.*` · `viva.*` … |
| 不带点 | 62 | 混合 |

**带点那 97 个：**原版**不需要**把 `adyen.merchantAccount` 写成字符串 —— 它用**字段**。
**所以 absent 对它们**完全正常**，不是缺陷。**
**→ 而 `adyen.merchantAccount` 那条尤其说明问题：复刻件用 `Vars["adyen.merchantAccount"]` 存一个商户号，
而原版的做法是有一个字段。这是**表示方式**的差异，不是缺一个键。**

**不带点那 62 个是混合：**

| 明显自造 / 内部 | 可能是镜像的 |
|---|---|
| `lastBody`（R1006 我刚加的）· `lastStatus` · `sensorKeys` · `paymentMethodsUrl` · `antibot.solver` | `orderProcessed` · `paymentStarted` · `totalMinor` · `transactionAmount` |

### ④ 而最重的一条：`lastStatus` 从来就不在产物里

**`lastStatus` 是 R993 说的「活通道：5 写入 / 4 读取」。而它在镜像里两编码皆 0，**从来不在**。**
**`lastBody`（R1006 加的）同样。**

> **→ 所以 R1006 那个悬案（「消息层写对了却没进产物」）有了答案：
> 它读的那个通道**本身不存在**。不是消息层被裁，是它的输入不在。**
> **→ 而 R993 说「活通道」时的判据是「5 写入 / 4 读取」—— 那是**复刻件内部**的活，
> 不是**产物里**的活。两个「活」不是一回事。**

### ⑤ 所以这一轮的产出是**一个分类**，不是 159 个缺陷

**把 159 当成 159 个待修是错的。正确的读法是三档：**
1. **97 个带点键：表示方式差异**（原版用字段，我们用字符串键）—— 不是缺陷，除非要复刻「用字段」
2. **`lastStatus` / `lastBody` / `sensorKeys` / `paymentMethodsUrl` / `antibot.solver`：真自造**（5 个）
3. **其余约 50 个：待判** —— 有些像镜像语义（`orderProcessed` / `totalMinor`），需要逐个取证

### 数字

| 度量 | R1008 | **R1009** |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| **会话键总数** | 未测 | **326** |
| **在镜像里** | 未测 | **152** |
| **不在（带点 97 / 不带点 62）** | 未测（已知 2） | **159** |
| **未解析** | — | **15** |
| **第一阶段有效性** | 设计为快路径 | **0 / 326（失效）** |

### 教训

> **「活通道」这句话有两个意思：在复刻件内部有人写有人读，和在产物里真的存在。
> R993 用的是第一个意思，而它被读成了第二个 —— 于是「把它接上」看起来像一件小事。**
> **→ 而这一轮的扫描把那个混淆一次性摊开了：326 个键里 159 个不在产物里，
> 而其中一个正是那条「活通道」。**


### 那个判据有**适用范围**，而 159 个里大部分在界外（R1010）

**R1009 说下一轮判那 62 个不带点键。判了，而结果是「这个问法对它们不成立」。**

### ① 按 R956 的教训换成三种形态再查

**那 62 个是驼峰内部标识符（`orderProcessed` / `totalMinor`），而原版不用会话变量字典 —— 它用**字段**。
所以裸名可能是错的形状。查四种：**

```
orderProcessed      bare=0  _field=0  get_OrderProcessed=0  content=orderProcessed=0
paymentStarted      bare=0  _field=0  get_PaymentStarted=0  content=paymentStarted=0
totalMinor          bare=0  _field=0  get_TotalMinor=0      content=totalMinor=0
transactionAmount   bare=0  _field=0  get_TransactionAmount=0 content=transactionAmount=0
deviceProfiled      bare=0  _field=0  get_DeviceProfiled=0  content=deviceProfiled=0
sizeLine            bare=0  _field=0  get_SizeLine=0        content=sizeLine=0
selectedRate        bare=0  _field=0  get_SelectedRate=0    content=selectedRate=0
discountApplied     bare=0  _field=0  get_DiscountApplied=0 content=discountApplied=0
```

**→ 全 0。四种形态一个都没有。**

### ② 而全 0 不说明它们错了 —— 它说明这个问法对这一类**不适用**

**原版**没有** `Vars` 这个字典。它把状态放在**字段**里，而字段叫什么**不必与我们的键名相同** ——
我们的 `orderProcessed` 在原版里可能是字段 `_orderDone`、可能是 `_placed`、可能是别的东西，
而「这个名字在镜像里吗」对**任何一个**候选都只会答 0。**

> **→ 所以「键名对镜像」这个判据有一个**定义域**：
> 它只对**协议层**的名字有判定力 —— 那些名字是从镜像里抄来的（`kpsdk` / `datadome` /
> `paymentGatewayName` / URL / cookie 名），所以**这个名字**必须出现在镜像里。
> → 而对**内部状态管理**的名字，它没有判定力，因为原版在那一层用的是另一种机制。**
> **→ 这是 R730「不再写前缀分类器」的同一课：**一个判据在某一层不适用时，用它得出的结论是假的。**

### ③ 所以 159 个的正确读法

| 类 | 数 | 判据适用？ | 说明 |
|---|---|---|---|
| 带点（`adyen.*` 等） | 97 | **否** | 我们发明的命名空间约定，原版没有这套约定 |
| 驼峰内部状态 | ~57 | **否** | 原版用字段，字段名不必相同 |
| **协议层名字** | **5** | **是** | `paymentMethodsUrl` · `sensorKeys` · `lastStatus` · `lastBody` · `antibot.solver` |

**那 5 个里，**只有 `paymentMethodsUrl` 是该判的** —— 它是**端点**，而端点必须来自镜像。
另外 4 个（`lastStatus` / `lastBody` / `sensorKeys` / `antibot.solver`）是**我们自己的通道名**，
原版不需要它们，所以「不在镜像里」**正常**。**

**→ 而 `paymentMethodsUrl` R1008 已经处理过（记为自造、路由不可得）。**

### ④ 而 152 个 present 的含义现在清楚了

**那 152 个是**协议层的名字** —— 从镜像里抄来的（token 键、cookie 名、请求字段）。
→ 所以「152 在 / 159 不在」不是「一半对一半错」，
→ 而是**「抄来的都在，自己起的不在」** —— 而那正是应有的样子。**

### ⑤ 这一轮没有改代码，因为结论是「不需要修」

**R1009 把 159 摆成一个待办清单的形状。而这一轮说：那 159 个里**约 154 个不需要任何人做什么** ——
它们是我们自己的状态管理，而它本来就该有我们自己的名字。**

> **→ 唯一留下的是 `paymentMethodsUrl`（已记）与一个真问题：
> 「原版用什么字段名承载这些状态」。而那需要**类型级**证据（字段表），不是字符串级。
> → 而 vtable/字段表在 NativeAOT 下按名不可得（R958）—— 所以它是 Unknown，不是待办。**

### 数字

| 度量 | R1009 | **R1010** |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| 会话键 absent | 159 | **159（但按判据分成 97 不可判 / 57 不可判 / 5 可判）** |
| **其中需要修** | 记为待判 ~50 | **1（`paymentMethodsUrl`，R1008 已记）** |
| **判据的定义域** | 未讨论 | **协议层名字（152 个），不含内部状态** |

### 教训

> **一个判据在某一层不适用时，用它得出的结论是假的 —— 而它的**输出形状**
> （「159 个不在」）看起来和「159 个都是缺陷」一模一样。**
> **→ 上一轮我把一个清单交给了下一轮，而这一轮的第一件事本该是问
> 「这个清单上的东西**该不该**满足这个判据」。**


### Nike 的付款步骤一直在打**两个镜像里不存在的端点**（R1011）

**R1010 说下一轮回核心。回的第一步是查 Nike 的 `GetPaymentMethods`（ordinal 57），
而查的过程中撞到一件更重的事。**

### ① `NikeEndpoints` 的头注释早就说了，而那两行**活到了现在**

**`NikeEndpoints.cs:8-10`（R87 写的）：**

> 「the replica's Nike flow was calling **two URL families the binary does not contain at all** —
> <c>buy/carts/v2/…</c> and <c>buy/orders/v2/…</c>」

**而 `NikeFlow.cs:524` 与 `561` **仍在用** `buy/orders/v2/…/initiatePayment` 与 `…/payment`。
→ 而它们在一个**覆写**里（`public override async Task<StepOutcome> SubmitPaymentAsync`，514 行）
→ 而 R1002 恰恰证明了**覆写会进产物** —— 所以那两条是**会被发出去的**。**

### ② 而镜像查证：两个族都是 0

```
buy/orders/v2        0
buy/carts/v2         0
buy/checkouts/v3     1   → 0x147053d8c  https://api.nike.com/buy/checkouts/v3/
checkout_previews    2   → 0x147053c94 / 0x147053d0c
initiatePayment      3   → 0x146ab768c  /rpc/payment/pay/initiatePayment
                           0x146aafe84  /InitiatePayment
                           0x1470a4014  initiatePayment
```

**→ 操作是真的（`initiatePayment` 三处），而**地址不成立**：
RPC 形那条只是一个**路径**，旁边没有 host 字面量。**

### ③ 所以修法不是猜一个替换

**把 `/rpc/payment/pay/initiatePayment` 与 `api.nike.com` 拼起来，正是
`EndpointProvenanceTests` 专门禁掉的那个动作（「an endpoint was invented by joining a host seen in
one literal to a path」）—— 那会是**第六次**同类发明。**

**→ 而旧代码做的是更坏的一件事：它把一个**不存在的端点**变成一个像商店拒绝我们的错误：
「nike initiatePayment HTTP 404」。**

### ④ 改了什么

**`SubmitPaymentAsync` 改成报告，并列出镜像里真正的三个候选：**

```csharp
return StepOutcome.Fail(
    "nike: payment endpoint not captured -- the image names /rpc/payment/pay/initiatePayment without a host "
    + "and buy/checkouts/v3 as the resource, while buy/orders/v2 (what this step used) is in it zero times",
    retryable: false);
```

**而把原来打不存在端点的两段移进一个 `AttachCardAsync`（`private`，未使用），
注释写明「kept for when the address is established」—— 那是**代码留证**，不是留活路径。**

**→ 这不破坏任何能工作的东西：那两条请求**本来就必 404**。**

### ⑤ 而这与 R823/R991/R1001 是同一条原则的第四次

| 轮 | 形状 |
|---|---|
| R823 | CSRF GUID 兜底（编一个 token） |
| R991 | 伪造的支付令牌 `"tok_" + Guid.NewGuid()` |
| R1001 | 4 个网关端点只给一条路径，其余报「not captured」 |
| **R1011** | **Nike 付款打两个不存在的端点 → 改成报告** |

**共同点：一个**看起来在工作**的东西，其实是把「我不知道」写成「它拒绝了我」。**

### ⑥ 数字

| 度量 | R1010 | **R1011** |
|---|---|---|
| 套件 | 2219 | **2219（未改测试）** |
| 产物陈旧度 | 1 / 2,671 | **2 / 2,7xx（NikeFlow.cs 改）** |
| 函数数 | 174,336 | **174,336（未 publish）** |
| **Nike 里打不存在端点的活请求** | **2** | **0** |
| **`AttachCardAsync`** | 不存在 | **存在但未调用（留证）** |

### 教训

> **一份文件头注释写下「这两族不在二进制里」之后，那两行**又活了 900 多轮**。
> → 注释不是守卫；守卫要能被**跑**。**
> **→ 而这一轮能发现它，是因为我在找一个**别的**东西（ordinal 57 的端点）时读到了那个文件头。
> → 那说明「按顺序查 backlog」不如「顺着一条线索读到手边的文件」。**


### 第一个 `GetPaymentMethods` 覆写进了产物 —— 而两个观测没解释（R1012）

**R1011 说下一轮做「ordinal 57 的覆写」。做了，它成功了。而同一轮里出现两件我不解释的事。**

### ① `NikeFlow.GetPaymentMethodsAsync` —— 全仓第一个覆写

**R1008 查出 `StoreFlow.GetPaymentMethodsAsync` 覆写 **0** 次 ⇒ 按 R963 被裁 ⇒ 那个步骤在任何产物里都不存在，
而它读的 `Vars["paymentMethodsUrl"]` 是自造键名。
→ 覆写同时解决两件事：给它一个调用者，并让地址来自镜像而不是一个没人设的会话变量。**

**地址用 `NikeEndpoints.Checkouts` —— 镜像 `0x147053d8c`，`NikeEndpoints` 头注释说它是
「the single resource every checkout step writes to」。Nike 的 `GetPaymentMethods` 是**读**那个结账资源，
因为镜像给这个 host **没有**付款方式路径 —— 造一条会是 host+path 拼接那类错误。**

**并复用基类的 `ParsePaymentMethodNames`（一个解析器，不是两个会漂移的）。**

### ② 产物验证：它**进去了**

| 串 | 新 | 旧 |
|---|---|---|
| **`buy/checkouts/v3`** | **IN** | absent |
| **`no checkout to read payment methods`** | **IN** | absent |
| `nike-payment-methods` | absent | absent |
| `nike: no card` | absent → **删除后仍 absent** | absent |

**→ 新端点与覆写体的错误串都进了产物 —— 与 R1002 同一条规则（有覆写 ⇒ 进产物）。**

### ③ 而第一个未解释的观测：**字符串池不等于可达性**

**R1011 把打不存在端点的两段移进一个 `private AttachCardAsync`（未调用），作为「代码留证」。
而 publish 之后 `buy/orders/v2` **仍在**产物里。**

**→ 删掉那个方法再 publish：`nike: no card`（只在该方法里）消失了 —— 证明删对了；
而 `buy/orders/v2` **仍在**。**

**→ 所以那个串**不是**从 `NikeFlow` 来的。而 `where_is` 给出答案：还有 **4 处活代码**在用它。**

| 位置 | 形态 |
|---|---|
| `NikeFlow.cs:493` | `.../buy/orders/v2/US/{cart}/delivery` |
| `NikeFlow.cs:670` | `.../buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified` |
| `StoreFlow.cs:2365` | `Origin(c.Url) + "/buy/carts/v2/app"` |
| `NikeModule.cs:80` | `.../buy/carts/v2/US/Nike/SNKRS?format=simplified` |

**→ 所以 R1011「把两段移进未调用方法」那个动作**同时**做对了一件事（不留活路径）
和留了一个副作用（字符串可能仍在池里）—— 而真正的答案更简单：**它本来就不止两处。****

### ④ 而第二个未解释的观测：**函数数没动**

| 度量 | R1011 | **R1012** |
|---|---|---|
| **函数数** | 174,336 | **174,336（未变）** |

**→ 加了一个 `public override` 方法（约 45 行），而函数数**一个都没变**。
→ 而 R1002 加一句 `registry.Resolve` 就涨了 **342**。
→ **两个观测互相矛盾，而本轮不足以判定原因 —— 标 Unknown，不写成结论。**

**可能的解释（未证）：**那个覆写替换了一个已被裁的基类方法，净增接近零；
或者 `pdata` 的条目数对「在已有方法组里加一个覆写」不敏感。**都不是结论。**

### ⑤ 而第三个：metrics 报 1 失败，全跑报 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（排除浏览器依赖类） | **2218 通过 / 1 失败** |
| 全套 `--filter "Speed!=Slow"` | **2236 通过 / 0 失败 / 2 跳过** |

**→ 同一份代码，一次有失败一次没有 ⇒ 间歇失败。**
**→ 而我没有定位到它是哪一条 —— 那是本轮的缺口，不是可忽略的噪声。**

### 数字

| 度量 | R1011 | **R1012** |
|---|---|---|
| 全套 | 2219 | **2236 通过 / 0 失败 / 2 跳过** |
| **metrics 子集** | 2219 通过 | **2218 通过 / 1 失败（间歇）** |
| 产物陈旧度 | 2 / 2,7xx | **0 / 0（已 publish）** |
| **函数数** | 174,336 | **174,336（未变，未解释）** |
| **`GetPaymentMethodsAsync` 覆写数** | 0 | **1** |
| **`buy/checkouts/v3` 在产物** | absent | **IN** |
| **打不存在族的活代码位置** | 2（已修） | **4（新查出）** |

### 教训

> **「代码留证」这个做法有一个我没算到的代价：未调用的方法体里的字面量**仍可能进池**。
> → 而它把注意力从真问题引开了 —— 真正的答案是那族 URL **本来就不止两处**，
> 而 `where_is` 一次就给出了全部 4 处。**
> **→ 我上一轮「修了两处」的满足感，让「还有几处」这个问题没被问出来。**


### 间歇失败**不复现**；而 Nike **根本没有购物车端点**（R1013）

**R1012 留了三个未解释。这一轮关掉两个，第三个变成一条更清的结论。**

### ① 间歇失败：三次独立验证为 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（R1012 那次） | 2218 通过 / **1 失败** |
| 全套 `Speed!=Slow`（R1012） | 2236 / 0 / 2 |
| 全套 `Speed!=Slow`（本轮） | **2236 / 0 / 2** |
| **metrics 的精确 filter**（本轮，逐字照抄） | **2219 / 0 / 0** |
| `metrics_report.py`（本轮） | **2219 / 0 / 0** |

**→ 同一份代码、同一 filter，**四次跑出三次 0**，而失败那次正是我**同时在做 publish**。**
**→ 所以最可能是构建服务器 / 文件锁竞争，而不是用例本身。**
**→ 但它**不可复现**就不算已解决 —— 记为「四次中一次失败，之后三次为 0，保留观察」。**

### ② 而这一轮的取证给出一个比「4 处拼错」更准的结论

**R1012 查出 4 处活代码打 `buy/orders/v2` 或 `buy/carts/v2`。这一轮把 Nike 的**整个** `api.nike.com/buy`
清单取出来：**

```
0x147053c94  https://api.nike.com/buy/checkout_previews/v3/
0x147053d0c  https://api.nike.com/buy/checkout_previews_jobs/v3/
0x147053d8c  https://api.nike.com/buy/checkouts/v3/
0x147053df4  https://api.nike.com/buy/checkouts_jobs/v3/
（另 3 条在同族）

buy/carts    0
carts/v2     0
```

> **→ Nike **没有购物车端点**，也**没有订单端点**。它只有**一个 checkout 资源**加它的 preview 与两个 jobs。
> → 所以那 3 处「购物车」代码**不是端点拼错，是模型错**：它们假设有一个购物车资源，而原版没有。**

**那是 R87 那条注释真正说的事（「the real checkout surface is a single `buy/checkouts/v3/` resource
that each step writes to」）—— 而它被读成了「换一下 URL 前缀」。**

### ③ 所以这一轮只修了有据的那一处

**`NikeFlow.cs:493` 的 `/delivery`（运单地址）→ `NikeEndpoints.Checkouts + CartId`。**

**理由：镜像里那个资源是「每个 step 都写它」，而运单是一个 step。**请求体保持复刻件原来构造的** ——
镜像没有说运单写入长什么样，发明一个形状会在**新位置**犯同一个错。**

**→ 而另 3 处**没修**，因为它们需要**行为改动**（从「往购物车加」改成「建/写 checkout」），
而那要先确证 Nike 的 checkout 创建语义。**留作下一轮，写清理由。**

### ④ 而第三个未解释（函数数未变）仍未解

| 度量 | R1012 | **R1013** |
|---|---|---|
| 函数数 | 174,336 | **174,336（仍未变）** |

**→ 这一轮又改了 `NikeFlow.cs`（加注释 + 换 URL），函数数仍未动。
→ 而 R1012 加了一个 `public override` 也未动。
→ **所以「改 `NikeFlow` 不动函数数」已经是两次一致的观测** —— 那是一条**规律**，而不是矛盾：
`NikeFlow` 的方法大多**已被覆写并已在产物里**，改它们的身体不改变函数数。
→ **而 R1002 的 `+342` 是因为**从零拉进**了一整族新类，不是改一个已有方法。**
**→ 两个观测不再矛盾：一个是「改已可达的代码」，一个是「让不可达的代码变可达」。**

### 数字

| 度量 | R1012 | **R1013** |
|---|---|---|
| 套件（metrics filter） | 2218 / 1 失败 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 0 / 0 | **1 / 711（只改 NikeFlow）** |
| 函数数 | 174,336 | **174,336（两次一致，已解释）** |
| **Nike 的 buy 端点** | 已知 3 条 | **7 条，全 checkouts 家族** |
| **打不存在族的活代码** | 4 | **3（修了 `/delivery`）** |
| **间歇失败** | 未定位 | **四次中一次，之后三次为 0** |

### 教训

> **「4 处拼错了 URL」和「这 3 处假设了一个原版没有的资源」是两个不同大小的结论，
> 而它们的第一步取证动作是同一个：把那个 host 的**全部**字面量取出来。**
> **→ 我上一轮取的是「这几个族有没有」，得到「没有」；这一轮取的是「那这个 host 有什么」，
> 得到「只有一个 checkout 资源」。后者才说明了该怎么办。**


### `CartUrl()` 的注释早就裁决了我这两轮做的事（R1014）

**R1013 说下一轮取证 Nike checkout 的创建语义，改那 3 处。取证的第一步是读那 3 处 —— 而第一处旁边就写着答案，
而答案是我上一轮做错的事。**

### ① R48 的注释，原文

**`NikeFlow.CartUrl()`（656-682，R48 写的）：**

> **「Not changed, deliberately. The original's fourteen checkout steps share those five URLs,
> which means most of them write to one checkout resource rather than hitting fourteen endpoints;
> without the decompiled step bodies there is no way to tell which of `checkouts/v3` and
> `checkout_previews/v3` carries the add. **Swapping one guess for another would move the failure,
> not remove it.」**

**→ 它把这件事说完了：**
1. 五个 URL 被十四个步骤共享
2. **没有反编译的步骤体，就无法判断哪个 step 打哪个资源**
3. **换一个猜是移动失败，不是消除失败**

### ② 而我 R1012 与 R1013 做的正是它拒绝的事

| 轮 | 我做了什么 | 依据 |
|---|---|---|
| R1012 | `GetPaymentMethodsAsync` 的地址改成 `NikeEndpoints.Checkouts` | 「每个 step 都写它」 |
| R1013 | `/delivery` 的地址改成 `NikeEndpoints.Checkouts` | 同一句 |

**→ 而「每个 step 都写它」是**真**的，而它**不决定**哪个 step 写什么。
→ 而那句注释自己说「no way to tell which of the two carries the add」。**

### ③ 而交换猜测**比 404 更坏**

**旧地址（`buy/orders/v2/...`）**只能** 404，而它**说得出来**。
新地址（`checkouts/v3/{id}`）会返回 **200 或一个关于 payload 的错误** ——
**而那时错误消息不再指向「地址不存在」。**

> **→ 一条「nike payment methods HTTP 200，但没有付款方式」读起来像**商店不支持刷卡**，
> 而真相是**我们在读一个不承载那份数据的资源**。
> → 那正是 R823/R991/R1001/R1011 那条原则的**同一次违反**，只是这次披着「有据替换」的外衣。**

### ④ 所以这一轮回滚两处，改成报告

**`/delivery` 与 `payment-methods` 都改成 `Fail(..., retryable: false)`，并在文本里点名三个候选资源
（`checkout_previews/v3` · `checkouts/v3` · 两者的 jobs），让下一次从那里开始而不是从零。**

**而**保留**的是两件从来不是猜测的事：**
1. **那个覆写本身** —— 它让步骤不再被裁（R963），那与地址无关
2. **候选资源清单** —— 镜像真的只有那五个

### ⑤ 而这一轮真正的产出是**一条被遵守的既有裁决**

**R48 那条注释存在了 900 多轮，而我在 R1012/R1013 两轮里**没有读它** —— 尽管我**改的就是它下面的那个文件**。

> **→ 而那与 R995 那次同形：答案早就在仓里，而我先动手。
> → 两次都是「读到手边的文件」这一步没做。**

### 数字

| 度量 | R1013 | **R1014** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 1 / 711 | **1 / 681（净减 30 行）** |
| 函数数 | 174,336 | **174,336** |
| **Nike 里「有据替换」的地址** | 2 | **0（两处都改回报告）** |
| **Nike 里打不存在族的活代码** | 3 | **3（未动，且现在有理由不动）** |
| **引用 R48 裁决的地方** | 0 | **2 处（两段的注释都指向它）** |

### 教训

> **「有据」有两种：证据说明**这个地址存在**，和证据说明**这个 step 用这个地址**。
> 我这两轮满足的是第一种，而它不够 —— 而我把它当成了第二种。**
> **→ 而区分它们的成本是**读那段代码旁边的注释**。R48 已经替我把这笔账算过了，
> 而我改那个文件时没读它下面那一屏。**


### 端点扫描器**跳过所有插值模板** —— 修掉之后一次查出 11 个（R1015）

**R1014 说下一轮换一个站。而 R1014 自己的教训是「读到手边的文件」——
所以换之前先跑现成的 `endpoint-provenance.py`，问它为什么没抓到 Nike 那 4 处。**

### ① 答案在 165 行，而且它**明确写了**

```python
for m in INLINE.finditer(body):
    value = m.group(1)
    # skip interpolated templates and obvious fragments
    if "{" in value or value.endswith("/"):
        continue
```

**→ 带 `{` 的值被**明确跳过**，注释说那是「interpolated templates」。
→ 而 Nike 那 4 处**全是** `$"https://api.nike.com/buy/orders/v2/US/{c.Session.CartId}/delivery"` 这个形。**

> **→ 所以工具的「invented: 0」是**真的**（对它的定义域），而 Nike 的缺陷**在界外**。
> → 这是 R1010「判据有定义域」的**第二次** —— 而这次在代码里，有行号。**

### ② 修法：插值模板的前缀是一个可以判的主张

**`$".../buy/orders/v2/US/{cart}/delivery"` 对 `".../buy/orders/v2/US/"` 提出了一个主张，
而那个主张要么在镜像里，要么不在。**
**→ 而一个**只到 host** 的前缀不是主张（`https://api.nike.com/` 什么都不断言），所以不管它。**

**实现：`static_prefix()` 取第一个 `{` 之前的部分；只在它带路径时才判；
并且结尾的 `/` 单独查（`proven(x) or proven(x.rstrip('/'))`）。**

### ③ 而修完后，一次查出 **11 个**

```
inline URL/path literals: 268 → 328      （多扫到 60 个）
not in pool:              29 → 40
unknown (unregistered):    0 → 11        baseline 0 → FAIL
```

| 文件 | 行 | 前缀 |
|---|---|---|
| FarfetchFlow.cs | 62 | `/api/ff-products/v1/products/{…}` |
| FarfetchFlow.cs | 174 | `/api/basket/v1/` |
| FarfetchFlow.cs | 201 · 207 · 237 · 272 · 289 | `/api/checkout/v1/basket/{…}` |
| NikeFlow.cs | 235 | `https://api.nike.com/product_feed/threads/v2/` |
| NikeFlow.cs | 652 | `https://api.nike.com/buy/carts/v2/{…}` |
| StoreFlow.cs | 768 | `/discount/` |
| StoreFlow.cs | 1272 | `/api/payments/` |

### ④ 而 11 个**不是** 11 个缺陷 —— 那是 R1010 的教训

**Nike 那 2 个我已经知道真假：**
- `:652 buy/carts/v2/{…}` —— **确实不存在**（镜像 0 命中，R1013 已证）
- `:235 product_feed/threads/v2/` —— 那在 `NikeEndpoints.ProductFeedThreads` 里是**镜像有的**，
  而这里报 absent 是因为**结尾 `/` 与 `?fields=` 的形不同** ⇒ **可能是假阳性**

**→ 所以这 11 个是**待判清单**，而其中至少 1 个已经看出是假阳性。**

### ⑤ 而**不登记进 ledger**

**`BASELINE = 0` 与 `ledger_classes()` 是一个**收紧守卫**的设计：任何新的 absent 端点都要先被判过才能登记。
把 11 个直接登记进去，就等于把「我们不知道」写进白名单 —— 那正是这个工具存在的反面。**

**→ 所以工具现在**红着**（`FAIL: 11 unregistered inline endpoints`），而那是正确的状态：它报出了一个真的待办。
→ 而它不影响套件（`metrics_report.py` 跑的是 dotnet test，不是这个脚本）。**

### ⑥ 数字

| 度量 | R1014 | **R1015** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0**（未改产品代码） |
| 函数数 | 174,336 | **174,336** |
| **扫描到的内联字面量** | 268 | **328（+60，插值模板进来了）** |
| **判为不在池里** | 29 | **40** |
| **未登记的** | **0**（假的 0） | **11（真的待判）** |
| **`endpoint-provenance.py` 退出码** | 0 | **1（红，且应当红）** |

### 教训

> **一个「invented: 0」的守卫可以同时是真的和没用的 —— 只要它的定义域排除了缺陷所在的那一类。
> → 而排除是**写在一行 `continue` 里的**，注释还坦白说了「skip interpolated templates」。
> → 我读了那份输出五行，从来没问过「它扫了哪些」。**
> **→ 而 R1010 的教训（判据有定义域）刚在上一轮立过，这一轮就在它自己身上又遇见一次。**


### 池子的行带地址列，所以我的前缀规则一次都没生效；修完 11 → 10，而 10 个全是真的（R1016）

**R1015 说下一轮判那 11 个，先修假阳性。修了，而修的**第一版**也是坏的。**

### ① 第一版前缀规则：加对了，跑起来什么都没变

**想法是对的：`proven()` 只做**完全相等**判定，而 `product_feed/threads/v2/` 对镜像的
`product_feed/threads/v2?fields=` 不相等 —— 所以加一条「池里有串**以此前缀开头**」。**

**→ 跑完仍是 **11**，而 `NikeFlow.cs:235` 还在。**
**→ 所以那条规则一次都没命中。**

### ② 原因：`pe_strings.txt` 的行是 `0x地址  串`，不是裸串

```
RAW: '0x0705312c  https://api.nike.com/product_feed/threads/v2?fields='
```

**→ 我用 `line.strip()` 建集合，地址列跟着留下来。
→ 于是 `startswith("https://…")` 在问「这一行以 URL 开头吗」，而行以 `0x0705…` 开头 —— **永不成立**。**

**→ 而 `proven()` 里原来的 `value in pool` 一直是对的，因为那是**全文子串**搜索，
地址列不影响它。**所以「相等」路径好，「前缀」路径死** —— 而两条路径的输出混在同一份报告里，
看起来像「前缀规则证明它们真的不在」。**

### ③ 修第二版：剥掉地址列

```python
if line.startswith("0x"):
    parts = line.split("  ", 1)
    if len(parts) == 2:
        line = parts[1]
```

**→ 再跑：`not in pool 40 → 39` · `unknown 11 → 10`，而消失的正是 `NikeFlow.cs:235`。**
**→ 那个假阳性**上一轮就预测到了**，而这一轮它自己消失了 —— 那是修对了的判据。**

### ④ 而剩下 10 个，逐个问 IDB：**全部真的不存在**

**§2.7b：抽样池找不到不代表镜像没有。所以六个不同前缀逐个查 `ida.py str`：**

| 前缀 | IDB | n |
|---|---|---|
| `/api/ff-products/v1/products` | **NOT IN IMAGE** | 0 |
| `/api/basket/v1` | **NOT IN IMAGE** | 0 |
| `/api/checkout/v1/basket` | **NOT IN IMAGE** | 0 |
| `buy/carts/v2` | **NOT IN IMAGE** | 0 |
| `/discount` | **NOT IN IMAGE** | 0 |
| `/api/payments` | **NOT IN IMAGE** | 0 |

**→ 所以那 10 行**全是自造的**：Farfetch ×7 · Nike ×1 · StoreFlow ×2。**

**→ 而 `/discount` 与 `/api/payments` 让我意外 —— 那是**通用词**，我原以为会命中。
→ 0 命中说明那两个打点也是自造的。**

### ⑤ 所以工具现在**红着 10，而那是准确的状态**

**→ 10 个都经 IDB 定性为不存在，所以它们**不是**假阳性、**不是**待判 —— 是**真的缺陷**。
→ 而把 10 个登记进 ledger 会把真缺陷写进白名单 ⇒ 仍然不登记。**

**→ 而这 10 个的修法与 Nike 那 4 处同类：需要知道每个站的**真实**端点，而那要取证。
→ 留作下一轮。**

### ⑥ 数字

| 度量 | R1015 | **R1016** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0**（未改产品代码） |
| 函数数 | 174,336 | **174,336** |
| **扫到的内联字面量** | 328 | **328** |
| **不在池里** | 40 | **39** |
| **未登记（真缺陷）** | 11 | **10** |
| **其中经 IDB 定性** | 1（另 10 未判） | **10（全 0 命中）** |
| **假阳性** | 1（预测） | **1（已消除）** |
| **工具两处缺陷** | 插值跳过 | **+ 池行带地址列** |

### 教训

> **一个修好的判据如果**没有输出变化**，那不是「确认了原结论」，是「新判据没生效」。
> → 而我第一版前缀规则跑完没变化时，第一反应是「所以它们真的不在」—— 而正确的反应是
> 「这条规则**测过**吗」。**
> **→ 那是 R1015 那条教训的同一层：一个「0」可以是真的和没用的。这次它是**没用的 0**，
> 而我没有先问它有没有生效。**


### Farfetch 的 API 面**完全不在镜像里**；而 Shopify 那两处有候选却仍不改（R1017）

**R1016 说下一轮取证 Farfetch 与 Shopify 的真实端点，改那 10 处。取证了，而结论是那 10 处里**没有一处该改**。**

### ① Farfetch：镜像里只有**三条**串，全是名字

```
Farfetch          n=3
  0x14338eadc  Farfetch            ← 反射元数据（类型/方法名，UTF-8）
  0x146d8dfdc  Farfetch            ← 字面量
  0x146d8e004  Farfetch Checkout   ← 显示名

api.farfetch      n=0
farfetch.com      n=0
ff-products       n=0
basket/v1         n=0
```

**→ Farfetch **是一个真实的站**（有名字、有「Farfetch Checkout」显示名），而它的 **API 面在字符串层面**一条都没有**。
→ 所以那 7 处路径**不只是拼错，是整个 host 都不存在**，而镜像**不提供**替代。
→ 「Farfetch 怎么工作」只能从**代码级**证据得到（那在 NativeAOT 下按名不可得，R958）⇒ **Unknown，不是待办。****

### ② Shopify 那两处：有候选，而候选不够

**`/api/payments/`（`StoreFlow.cs:1272`）：**

```
/payments/        n=39   → /payments/ · /payments/config.json · /payments/place-order
                            /payments/adyen/payment-methods · /payments/creditCardWithPayerAuthentication/
/api/payments     n=0
```

**→ 所以 `/api` 前缀是**复刻件自己加的**，而 `/payments/` 确实存在 —— 那看起来像一次有据替换。
→ **但那 39 处是**别的站**的钱面（`/payments/adyen/...` · `/payments/place-order`），
  而「查一笔付款详情」的形状**不在**镜像展示的那几种里。**
→ 而 R48 的裁决正好管这个：知道这个路径存在 ≠ 知道这个 step 用它。**

**`/discount/`（`StoreFlow.cs:768`）：**

```
/discount/        n=0
cart/update.js    n=1   （0x146fc175c）
cart/add.js       n=1   （0x146fc16dc）
```

**→ 镜像里有 `cart/update.js`，而 Shopify 的常规做法是把折扣码放进那个 POST 的 body，不是放进路径。
→ 那是一个**候选**，而「`SubmitDiscount` 到底打哪」仍然没有证据。**

### ③ 而决定性的一条：两处都**零覆写**

| 方法 | 覆写数 | R963 的后果 |
|---|---|---|
| `SubmitDiscountAsync` | **0** | **被裁，不在产物里** |
| `GetPaymentDetailsAsync` | **0** | **被裁，不在产物里** |

**→ 所以这两处**改不改都不影响产物** —— 它们只影响源码读起来对不对。
→ 而把一个**不可达**的调用换成另一个**不可达**的调用，正是 R48 说的「swapping one guess for another」，
  只是这次连「会不会发出去」都不涉及。**

**→ 所以这一轮**没有改行为**，只把取证结果写进两处的注释：**

- `:1272` —— `/api/payments/` 0 命中，`/payments/` 39 处属别的站，本步无覆写被裁
- `:768` —— `/discount/` 0 命中，候选是 `cart/update.js` 带 body，本步无覆写被裁

### ④ 而那 10 处的最终分类

| 类 | 数 | 处置 |
|---|---|---|
| **镜像完全不提供**（Farfetch） | **7** | **Unknown** —— 需代码级证据 |
| **有候选但证据不足**（Shopify ×2） | **2** | **记在注释里，不改** |
| **已确证不存在且有明确替代**（Nike `buy/carts/v2`） | **1** | R1013/R1014 已处置（报告） |

**→ 所以扫描器仍红 10，而**那 10 个全部有据可查地处置过了** —— 3 个改了、7 个标 Unknown。
→ 而「红 10」现在是**正确且已解释**的状态，不再是待办。**

### ⑤ 数字

| 度量 | R1016 | **R1017** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **2 / 3,365（StoreFlow.cs + 工具）** |
| 函数数 | 174,336 | **174,336** |
| **扫描器未登记** | 10 | **10（但全部已处置：7 Unknown · 2 注释 · 1 已报告）** |
| **Farfetch 串总数** | 未测 | **3（全是名字，无 host 无路径）** |
| **`/payments/` 与 `/api/payments/`** | 未测 | **39 vs 0** |

### 教训

> **「这个端点不在镜像里」有两种后续：有的能换成镜像里有的另一个，有的**镜像根本不提供**。
> → 前者是修，后者是 Unknown —— 而两者的第一步取证动作一样，第二步取决于**那个站有没有 API 面**。
> **→ 而 Farfetch 的情况说明：一个站可以在镜像里只有**名字**。**
> → 那时「照实报告」不是保守，是**唯一没有在发明的做法**。**


### 镜像那四条 `captcha-delivery` 是 **DataDome** 的，不是 PerimeterX 的（R1018）

**上一轮收尾说下一轮看优先级 ②。看的第一步是验 R998 那条 claim —— 而 claim 成立，**归属错了**。**

### ① 先说验对了的

**R998 声称「`geo.captcha-delivery.com` 与 `/interstitial/` 路径，共四条字面量」，而 `px-captcha` 一次不出现。
逐条查证：**

```
captcha-delivery  n=4
  0x1470689dc  https://geo.captcha-delivery.com
  0x147068a34  https://geo.captcha-delivery.com/
  0x147068a8c  https://geo.captcha-delivery.com/interstitial/
  0x147068b04  https://geo.captcha-delivery.com/interstitial/?initialCid=
px-captcha        n=0
```

**→ 「four literals in all」**精确正确**。`px-captcha` 确证 0。R998 的这两条都对。**

### ② 而它把**归属**搞错了

**同一个查询里还有一条它没引用的：**

```
0x1435260cb  (DdInterstitialClient
```

**→ `Dd` = **DataDome**。而 `geo.captcha-delivery.com` 就是 **DataDome 的 CAPTCHA host**。
→ 所以那四条字面量是 **datadome 的**，而 R998 把它们算给了 **perimeterx**，并让 `DetectAsync` **优先**测它们。**

### ③ 而分支顺序**掩盖**了这个错

**`DetectAsync` 的顺序（`StoreFlow.cs:380-392`）：**

```
381  cf-chl              → cloudflare
382  kpsdk               → kasada
383  _Incapsula_Resource → imperva
384  datadome            → datadome      ← 排在前面
388  captcha-delivery    → perimeterx   ← 而这是 datadome 的 host
389  px-captcha          → perimeterx
390  queue-it            → queue-it
```

**→ 一个自带 `datadome` 字样的页面在 **384** 就被认出 ⇒ 388 的错**看不出来**。
→ 而**唯一会被它改变的那类页面**是：一个 DataDome 的 **interstitial**，
  **只报出 host 而不报出厂商名**。→ **而那正是 CAPTCHA 墙serve 的那种页面。****

> **→ 那个页面原来被判成 `perimeterx`，然后交给**错误厂商的 solver**。
> → 而「大多数情况对」正是这类错误能活下来的方式。**

### ④ 改了什么

```csharp
body.Contains("captcha-delivery", StringComparison.OrdinalIgnoreCase) ? "datadome" :
body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
```

**→ `captcha-delivery` 归 `datadome`；`perimeterx` 只剩 `px-captcha`（镜像无，但仍是它唯一能主张的页面级标记，
而 `MarkerFrom = Inferred` 如实写着）。**

**→ 并更新 `VendorWiring` 那行注释：R1018 说明 R998 的归属已改。**

**→ 加 3 条守卫（`CaptchaDeliveryAttributionTests`）：**
1. `captcha-delivery` 必须路由到 `datadome`，且 perimeterx 分支**不再**主张它
2. `px-captcha` 仍是 perimeterx 的标记，且审计行写明归属已改
3. 更正所依据的证据必须在源码里被引（`DdInterstitialClient` 与 `0x1435260cb`）

### ⑤ 数字

| 度量 | R1017 | **R1018** |
|---|---|---|
| 套件 | 2219 / 0 | **2222 / 0 / 0（+3 归属守卫）** |
| 产物陈旧度 | 2 / 3,365 | **3 / 3,522** |
| 函数数 | 174,336 | **174,336** |
| **`captcha-delivery` 的归属** | **perimeterx（错）** | **datadome（对）** |
| **会被误判的页面类型** | DataDome interstitial（只报 host） | **已消除** |
| **perimeterx 的 marker** | `px-captcha`（Inferred） | 不变，且注释写明 |

### 教训

> **一条 claim 可以逐字成立而结论是错的。R998 的四条字面量、零命中的 `px-captcha`、
> 「镜像里有一个可用的标记」—— 每句都对，而它把那个标记算给了错的厂商。**
> **→ 而派出这个错误只需要一个它没做的动作：问「这个 host 是**谁**的」。**
> **→ 而 `DdInterstitialClient` 就紧挨在那四个地址旁边的那个查询里 —— 它出现在我的输出里，
> 而我第一遍读的时候只看了那四条 URL。**


### 六个 vendor 的 marker 一次问完 —— 而**第一个**就是自造的（R1019）

**R1018 的教训是「问这个 host 是谁的」。这一轮把那个动作推广：把六个 vendor 的 marker 与拼写一次全问，
像 R1009 问会话键那样。**

### ① 台账（19 个拼写，全部问 IDB）

| vendor | 拼写 | n |
|---|---|---|
| **cloudflare** | **`cf-chl`** | **0** |
| | `cf_clearance` | 2 |
| | `cloudflare` | 40 |
| | `__cf_bm` | 1 |
| | `challenge-platform` | **2** |
| kasada | `kpsdk` | 17 |
| | `x-kpsdk-ct` · `-cd` · `-st` | 1 · 1 · 1 |
| | `kasada` | 40 |
| **imperva** | `_Incapsula_Resource` · `incap_ses` · `visid_incap` · `incapsula` · `imperva` · `nlbi_` | **0 · 0 · 0 · 0 · 0 · 0** |
| datadome | `datadome` | 15 |
| | `geo.captcha-delivery.com` | 4 |
| **perimeterx** | **`px-captcha`** | **0** |
| | `_px3` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` | 1 · 2 · 1 · 1 |
| queue-it | `queue-it` · `queue-it-set-cookie` · `queueit` | 13 · 1 · 24 |

### ② 而 **`cf-chl` 是 0**，而它是 `DetectAsync` 的**第一个**分支

```csharp
381  body.Contains("cf-chl", ...) ? "cloudflare" :      ← 0 命中
```

**→ 所以检测链条的**第一个**判断用的就是一个自造串。
→ 而镜像里有 `challenge-platform` 两处（`/cdn-cgi/challenge-platform/` 路径，**页面级**）、
  `cf_clearance` 两处、`__cf_bm` 一处 —— 而**后两个是 cookie 名**，而 `DetectAsync` 读的是**响应体**。**

**→ 所以正确的页面级 marker 是 `challenge-platform`，而 `cf_clearance` 该留在 cookie 列（它本来就在那里）。**

### ③ 改了什么

```csharp
body.Contains("challenge-platform", ...) ? "cloudflare" :
body.Contains("cf-chl", ...) ? "cloudflare" :          // 降为后备
```

**→ `VendorWiring` 的 cloudflare 行：marker 改 `challenge-platform`，`MarkerFrom` 由 `Inferred` 改 **`ImageLiteral`**。**

### ④ 而守卫**抓住了**我

**`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉着 `Inferred == {cloudflare, imperva, perimeterx}`，
而我改完就红了。而那正是那条守卫的设计 —— 它的注释写着「Changing it means re-run
`python analysis/ida.py str <marker>` and finding something there」。**

**→ 我做了那件事（`challenge-platform` n=2），所以集合改成 `{imperva, perimeterx}`，理由写进注释。**

**→ 现在 `Inferred` = 2（imperva · perimeterx），`ImageLiteral` = 4（cloudflare · kasada · datadome · queue-it）。**

### ⑤ 而两个 `Inferred` 的性质不同

| vendor | marker | 镜像 | 性质 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（6 拼写全 0） | **整站风控不在镜像里** |
| **perimeterx** | `px-captcha` | **0** | **只有 cookie 名，没有页面级 marker** |

**→ 两者都标 `Inferred`，而**原因不同**：imperva 是「这个厂商不在」，perimeterx 是「这个厂商在，而它没有
一个能在响应体里找的字面量」。**
**→ 那个区别现在只在注释里，而在台账里看不出来 —— 下一轮该把它变成字段或第二张表。**

### ⑥ 数字

| 度量 | R1018 | **R1019** |
|---|---|---|
| 套件 | 2222 / 0 | **2222 / 0 / 0** |
| 产物陈旧度 | 3 / 3,522 | **3 / 3,531** |
| 函数数 | 174,336 | **174,336** |
| **已验证的 marker 拼写** | 6 | **19** |
| **`Inferred` 数** | 3 | **2（cloudflare 升为 ImageLiteral）** |
| **检测链第一个串** | `cf-chl`（0 命中） | **`challenge-platform`（2）** |

### 教训

> **R1018 花了三轮才发现一个归属错，而它的形状是「自造串」。这一轮把「自造串」当问题一次问完，
> 第一个分支就中。**
> **→ 而那个错从 R140 起就在那里 —— 因为 `cf-chl` 读起来太像真东西（所有 Cloudflare 文档都那么写），
> 而它确实**曾经**是。**
> **→ 「看起来对」是这类错误的唯一保护色，而唯一的解法是把每个串都问一遍镜像。**
