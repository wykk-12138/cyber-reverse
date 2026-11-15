# PARITY_AUDIT — 函数数量对等审计

> 由 `analysis/parity_audit.py` 生成。原版数字来自 `docs/baseline/`（IDB 实测），
> replica 数字来自源码静态扫描（排除 `obj/`、`bin/`）。

## 一、业务步骤词汇的真实覆盖率

原版 289 个「出现 ≥2 次的 async 状态机名」混了两类东西，必须分开算：

| 类别 | 名字数 | 实现体数 | 是否该复刻 |
|---|---|---|---|
| 框架/BCL 内部（`ReadAsync`、`DisposeAsync`、`FlushAsync` …） | 121 | 457 | 否 —— replica 用真 BCL |
| **业务步骤**（`AddToCart`、`SubmitShipping`、`GetCsrf` …） | **168** | **872** | 是 |

### 业务词汇覆盖：**168 / 168 = 100.0%**（实现体 872 / 872 = 100.0%）

### 已覆盖的业务词汇（168，按实现次数）

- `Start` ×34
- `AddToCart` ×32
- `FindProduct` ×29
- `SubmitShipping` ×28
- `SubmitOrder` ×24
- `Login` ×22
- `SubmitPayment` ×22
- `GetCheckout` ×19
- `GetHome` ×18
- `HandleResponse` ×18
- `SubmitBilling` ×15
- `GetCsrf` ×14
- `ClearCart` ×12
- `GetProduct` ×12
- `SetRequest` ×12
- `AddToCartPreload` ×11
- `SubmitDiscount` ×11
- `GetShippingRates` ×10
- `SubmitEmail` ×10
- `EditLine` ×9
- `FindVariant` ×9
- `Register` ×9
- `SolveAsync` ×9
- `AccountLogin` ×8
- `AddToCartStoreFront` ×8
- `CompletePayment` ×8
- `GetSession` ×8
- `Process` ×8
- `RefreshSession` ×8
- `EnterRaffle` ×7
- `Generate` ×7
- `ScrapeJson` ×7
- `ScrapeProduct` ×7
- `AddToCartMulti` ×6
- `CheckPriceLimit` ×6
- `CreateCart` ×6
- `CreateCheckout` ×6
- `FindProductMulti` ×6
- `GetCart` ×6
- `GetPaymentToken` ×6
- `GetScript` ×6
- `GetShippingRate` ×6
- `PlaceOrder` ×6
- `ScrapeVariantAvailability` ×6
- `Solve` ×6
- `SubmitPayPal` ×6
- `SubmitSensor` ×6
- `ApplyDiscount` ×5
- `CompleteRegistration` ×5
- `FetchBalance` ×5
- `FillAsync` ×5
- `FindProductFlow` ×5
- `GetRaffleData` ×5
- `Login_EnsureTaskAlive` ×5
- `ProcessOrder` ×5
- `ProcessPayment` ×5
- `CreateTransaction` ×4
- `EmailLogin` ×4
- `ExecuteSave` ×4
- `GetPayPalToken` ×4
- `GetStructureToken` ×4
- `Load` ×4
- `Run` ×4
- `ScrapeRaffleForm` ×4
- `SendManualNotification` ×4
- `Submit` ×4
- `SubmitKlaviyoBulkEvents` ×4
- `SubmitKlaviyoEvent` ×4
- `SubmitKlaviyoProfile` ×4
- `SubmitRate` ×4
- `AddToCartApp` ×3
- `BuildDestination` ×3
- `CalculateTaxes` ×3
- `CreateBasket` ×3
- `CreateOrder` ×3
- `CreateStripePaymentMethod` ×3
- `FindProductApp` ×3
- `GenerateCheckout` ×3
- `GenerateSensor` ×3
- `GetCaptcha` ×3
- `GetPaymentPage` ×3
- `GetProductDetails` ×3
- `GetRaffle` ×3
- `GetRates` ×3
- `GetStripePaymentIntent` ×3
- `GetToken` ×3
- `ProcessResponseAsync` ×3
- `ScrapePreload` ×3
- `Solve3DS` ×3
- `StartPayPal` ×3
- `StartPayment` ×3
- `SubmitBillingAddress` ×3
- `SubmitKlaviyoSubscription` ×3
- `SubmitPassword` ×3
- `SubmitPaymentDetails` ×3
- `WaitForRelease` ×3
- `Authenticate` ×2
- `Authorize` ×2
- `CheckLogin` ×2
- `ConfirmSubscription` ×2
- `CreateGmoToken` ×2
- `CreatePayment` ×2
- `CreateToken` ×2
- `Execute` ×2
- `ExecuteFetchBalance` ×2
- `FindRegistration` ×2
- `FindSlot` ×2
- `GenerateSbsd` ×2
- `GenerateVariables` ×2
- `GetAccessToken` ×2
- `GetAuthToken` ×2
- `GetBasket` ×2
- `GetCheckoutCaptcha` ×2
- `GetKasada` ×2
- `GetMerchantCode` ×2
- `GetPayPalAccessToken` ×2
- `GetPayPalOrderId` ×2
- `GetPaymentDetails` ×2
- `GetPaymentUrl` ×2
- `GetRaffleProduct` ×2
- `GetReleaseFeed` ×2
- `GetSbsdData` ×2
- `GetSensorData` ×2
- `GetSessionApp` ×2
- `GetWorkTime` ×2
- `Handle3DS` ×2
- `HandleLogin` ×2
- `HandleOutOfStock` ×2
- `HandleRequiresAction` ×2
- `Import` ×2
- `Init` ×2
- `InitiateCheckout` ×2
- `LoadCountryData` ×2
- `LogBadRequest` ×2
- `LookupAddress` ×2
- `MoveMouse` ×2
- `Poll` ×2
- `PollCaptchaAsync` ×2
- `PollQueue` ×2
- `PollRelease` ×2
- `PollRestock` ×2
- `Process3DS` ×2
- `Remove` ×2
- `RemoveItem` ×2
- `RemoveLineItem` ×2
- `ResetPassword` ×2
- `ScrapeJsonFrontend` ×2
- `ScrapeProductAvailability` ×2
- `ScrapeProductPage` ×2
- `SetEmail` ×2
- `SignUp` ×2
- `Solve3DSRedirect` ×2
- `SolveCptChallenge` ×2
- `SolveRecaptcha` ×2
- `SubmitAddress` ×2
- `SubmitCaptcha` ×2
- `SubmitCard` ×2
- `SubmitCustomer` ×2
- `SubmitDelivery` ×2
- `SubmitDetailsCommerce` ×2
- `SubmitInfo` ×2
- `SubmitOrderApp` ×2
- `SubmitOrderStripe` ×2
- `SubmitShippingMethod` ×2
- `ThreeDS` ×2
- `Tokenize` ×2
- `UpdateCart` ×2
- `VerifySession` ×2

## 二、规模对照

| 指标 | 原版 | replica |
|---|---|---|
| 函数总数 | 320,933 | 948 |
| 有名字的函数 | 10,033 | 534 |
| 类 / 类型 | 153（绑定可见） | 343 |
| 视图类 | 96（含 10 个 Theme） | 67 |
| 属性 | — | 542 |
| 代码行 | — | 23,925 |

## 三、实现质量分档

「名字存在」不等于「功能相等」。把 `StoreFlow` 的 165 个步骤方法按实现分三档：

| 档位 | 数量 | 含义 |
|---|---|---|
| **真实实现** | **139** | 基类有独立逻辑（92）或具体 Flow override（47 个名字） |
| 转发别名 | 26 | 基类直接调另一个步骤（如 `AddToCartApp` → `AddToCart`） |
| 空实现 | 0 | 基类 `=> Ok()`，没有 Flow 覆盖 |

### 转发别名清单（26）

- `FindProductFlowAsync` → `FindProduct`
- `AddToCartStoreFrontAsync` → `AddToCart`
- `AddToCartMultiAsync` → `AddToCart`
- `GenerateCheckoutAsync` → `GetCheckout`
- `SubmitAddressAsync` → `SubmitShipping`
- `GetShippingRateAsync` → `GetShippingRates`
- `ApplyDiscountAsync` → `SubmitDiscount`
- `PlaceOrderAsync` → `SubmitOrder`
- `SubmitPaymentDetailsAsync` → `SubmitPayment`
- `AccountLoginAsync` → `Login`
- `EmailLoginAsync` → `Login`
- `SignUpAsync` → `Register`
- `GetKasadaAsync` → `SubmitSensor`
- `GetCheckoutCaptchaAsync` → `GetCaptcha`
- `GetRaffleAsync` → `GetRaffleData`
- `CreateCheckoutAsync` → `InitiateCheckout`
- `ExecuteFetchBalanceAsync` → `FetchBalance`
- `Login_EnsureTaskAliveAsync` → `VerifySession`
- `FindProductAppAsync` → `FindProduct`
- `GetSessionAppAsync` → `GetSession`
- `SubmitOrderAppAsync` → `SubmitOrder`
- `CreateTokenAsync` → `GetToken`
- `GetAuthTokenAsync` → `GetToken`
- `SolveCptChallengeAsync` → `GetCaptcha`
- `SolveRecaptchaAsync` → `GetCaptcha`
- `SubmitDeliveryAsync` → `SubmitShipping`

## 三、实现质量分档

「名字存在」不等于「功能相等」。把 `StoreFlow` 的 165 个步骤方法按实现分三档：

| 档位 | 数量 | 含义 |
|---|---|---|
| **真实实现** | **139** | 基类有独立逻辑（92）或具体 Flow override（47 个名字） |
| 转发别名 | 26 | 基类直接调另一个步骤（如 `AddToCartApp` → `AddToCart`） |
| 空实现 | 0 | 基类 `=> Ok()`，没有 Flow 覆盖 |

### 转发别名清单（26）

- `FindProductFlowAsync` → `FindProduct`
- `AddToCartStoreFrontAsync` → `AddToCart`
- `AddToCartMultiAsync` → `AddToCart`
- `GenerateCheckoutAsync` → `GetCheckout`
- `SubmitAddressAsync` → `SubmitShipping`
- `GetShippingRateAsync` → `GetShippingRates`
- `ApplyDiscountAsync` → `SubmitDiscount`
- `PlaceOrderAsync` → `SubmitOrder`
- `SubmitPaymentDetailsAsync` → `SubmitPayment`
- `AccountLoginAsync` → `Login`
- `EmailLoginAsync` → `Login`
- `SignUpAsync` → `Register`
- `GetKasadaAsync` → `SubmitSensor`
- `GetCheckoutCaptchaAsync` → `GetCaptcha`
- `GetRaffleAsync` → `GetRaffleData`
- `CreateCheckoutAsync` → `InitiateCheckout`
- `ExecuteFetchBalanceAsync` → `FetchBalance`
- `Login_EnsureTaskAliveAsync` → `VerifySession`
- `FindProductAppAsync` → `FindProduct`
- `GetSessionAppAsync` → `GetSession`
- `SubmitOrderAppAsync` → `SubmitOrder`
- `CreateTokenAsync` → `GetToken`
- `GetAuthTokenAsync` → `GetToken`
- `SolveCptChallengeAsync` → `GetCaptcha`
- `SolveRecaptchaAsync` → `GetCaptcha`
- `SubmitDeliveryAsync` → `SubmitShipping`
