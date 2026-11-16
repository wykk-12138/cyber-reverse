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
