# 异步状态机长尾（由 `python analysis/async_tail.py --write-doc` 生成）

> 镜像的 NativeAOT 产物仍保留 `<名字>d__NN` 状态机串。三态判定：**declared**（复刻件有同名方法）、
> **mentioned**（源码里出现过这个名字但不是声明——通常是行为换名实现了、文档里点了名）、
> **absent**（源码里根本没出现，**只有这一类才算覆盖缺口**）。

| 项 | 值 |
|---|---|
| 镜像异步状态机名 | 801（出现 1291 次） |
| declared | 219 |
| mentioned | 97 |
| **absent** | **485** |

## 按家族（镜像 / absent）

| 家族 | 镜像 | absent |
|---|---|---|
| payment | 110 | 66 |
| store | 74 | 34 |
| other | 617 | 385 |

## payment 家族 · absent（真正的缺口）

| 名字 | 出现 |
|---|---|
| `ApproveMemberPayment` | 1 |
| `CacheTokenResponseAndCreateAuthenticationResultAsync` | 1 |
| `CheckInteractionChallenge` | 1 |
| `Complete3DSOrder` | 1 |
| `CompleteOrder` | 1 |
| `CreatePayPalToken` | 1 |
| `DetectByteOrderMarkAsync` | 1 |
| `DoChallengeAsync` | 1 |
| `ExistMoreChallenges` | 1 |
| `FilterTokensByEnvironmentAsync` | 1 |
| `FinalizeCheckout` | 1 |
| `FindAccessTokenAsync` | 1 |
| `FollowGmoRedirects` | 1 |
| `GenTokenAsync` | 1 |
| `GenerateJavascriptToken` | 1 |
| `GetAdyenPaymentStatus` | 1 |
| `GetAppCartToken` | 1 |
| `GetAtlasSessionToken` | 1 |
| `GetCardNonce` | 1 |
| `GetChallengeFrameRectAsync` | 1 |
| `GetChallengeRectanglesAsync` | 1 |
| `GetCustomerToken` | 1 |
| `GetDigestTokenForCredential` | 1 |
| `GetPayPalDetails` | 1 |
| `GetPayPalPaymentOptions` | 1 |
| `GetPayPalResult` | 1 |
| `GetStripeConfiguration` | 1 |
| `GetSweepStakeCheckout` | 1 |
| `HandleOrderResult` | 1 |
| `HandleUnzerRedirect` | 1 |
| `InitalizePayment` | 1 |
| `InitialisePayPal` | 1 |
| `InitializePayPal` | 1 |
| `PayerAuthenticate` | 1 |
| `ProcessDeferredPayment` | 1 |
| `ReadPaymentResponse` | 1 |
| `RefreshTokenAsync` | 1 |
| `RequestSessionToken` | 1 |
| `RequestToken` | 1 |
| `RpcCapturePayPal` | 1 |
| `RpcInitiatePayPal` | 1 |
| `RpcSolveThreeDS` | 1 |
| `RpcSubmitAdyenDetails` | 1 |
| `SendTokenRequestToBrokerAsync` | 1 |
| `SetAdyenPayment` | 1 |
| `SolveHintChallengeAsync` | 1 |
| `SolvePayPalHosted3DS` | 1 |
| `SquareCardNonce` | 1 |
| `SquareHydrate` | 1 |
| `StartInvoiceCheckout` | 1 |
| `SubmitAdyenOrder` | 1 |
| `SubmitBotDetectChallenge` | 1 |
| `SubmitChallenges` | 1 |
| `SubmitCheckoutPayment` | 1 |
| `SubmitOrderCommerce` | 1 |
| `SubmitPowChallenge` | 1 |
| `SubmitRecaptchaChallenge` | 1 |
| `SubmitThreeDSAuthentication` | 1 |
| `TokenizeDate` | 1 |
| `TokenizeText` | 1 |
| `UpdatePayment` | 1 |
| `ValidateCheckout` | 1 |
| `VerifyCheckout` | 1 |
| `VerifyStripeChallenge` | 1 |
| `WaitForUntouchedChallengeAsync` | 1 |
| `WalkUnzerReturn` | 1 |

## payment 家族 · mentioned（换名实现或只是文档点名）

| 名字 |
|---|
| `AuditCheckoutBehaviour` |
| `CanPlaceOrder` |
| `CardinalContinue` |
| `CardinalInit` |
| `CompletePayPalGuestPayment` |
| `ContinueUnzerThreeDs` |
| `GetOrder` |
| `GetPayment` |
| `GetUnzerCallback` |
| `RunCardinal` |
| `Solve3DSToken` |
| `SolvePayPal3DS` |
| `SubmitBotDeflectorChallenge` |

## store 家族 · absent

| 名字 | 出现 |
|---|---|
| `AddAddress` | 1 |
| `ClearActiveCart` | 1 |
| `FetchProductProperties` | 1 |
| `FilterBrokerAccountsByEnvAsync` | 1 |
| `FindAccountAsync` | 1 |
| `FindEarlyAccessProduct` | 1 |
| `FindHCaptchaInformationAsync` | 1 |
| `FindProductStoreFront` | 1 |
| `GetActiveCart` | 1 |
| `GetCartCsrf` | 1 |
| `GetCartId` | 1 |
| `GetCartItemId` | 1 |
| `GetHomepagePreloadVariant` | 1 |
| `GetLogin` | 1 |
| `GetProductHtml` | 1 |
| `GetProductZgwMobile` | 1 |
| `HandleCartUpdate` | 1 |
| `LoadProduct` | 1 |
| `ReplaceProduct` | 1 |
| `ReserveProduct` | 1 |
| `SaveAddress` | 1 |
| `ScrapeCaptchaKey` | 1 |
| `ScrapeProductData` | 1 |
| `ScrapeVariantAvailabilityStorefront` | 1 |
| `SearchProduct` | 1 |
| `SelectVariant` | 1 |
| `SendAsyncMultiProxy` | 1 |
| `SetCachedProductAsync` | 1 |
| `SetupProxySession` | 1 |
| `SolveBotCaptcha` | 1 |
| `StartShopApp` | 1 |
| `UpdateShippingMethodsList` | 1 |
| `VerifyCart` | 1 |
| `WaitCaptchaResultAsync` | 1 |

> `other` 家族 absent 385 个：`python analysis/async_tail.py --family other`。
