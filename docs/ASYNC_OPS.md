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
