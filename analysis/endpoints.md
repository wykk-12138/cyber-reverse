# 原版字符串表里的端点

来源：`Cybersole.exe.i64` 的字符串缓存（491,542 条），`find_regex` 逐 pattern 检索。
IDA 的 `auto_analysis_ready` 仍是 false，所以没有 xref——**这里只有字符串，没有调用者**。

## nike-kasada  `(kasada|kpsdk|j-1\.2|x-kpsdk)` — 40 条

| 地址 | 字符串 |
|---|---|
| `0x14322a307` | `Kasada` |
| `0x1433125ba` | `IKasadaSolver` |
| `0x1433125f7` | `"KasadaSolveResult` |
| `0x1433127a0` | `$KasadaSolveRequest` |
| `0x143312cbe` | `KasadaCdSolver` |
| `0x1433250cc` | `KasadaHandler` |
| `0x1433256d6` | `&KasadaMobileHandler` |
| `0x1433613da` | `"get_KasadaVersiong` |
| `0x1433618f1` | `_kasada` |
| `0x14336190f` | `_kasadaMobile` |
| `0x143361925` | `KasadaVersion` |
| `0x14336c21d` | `_accountKasada` |
| `0x14343917e` | `get_KasadaCt` |
| `0x14343918b` | `set_KasadaCt` |
| `0x1434391d3` | `set_IpsUrl.<Script>k__BackingField2<BasePath>k__BackingField2<KasadaCt>k__BackingField*<Bmsz>k__BackingField6<CookieName>k__BackingField.<IpsUrl>k__BackingField` |
| `0x14343928d` | `KasadaCt` |
| `0x14344abf5` | `*<HandleResponse>d__46 <GetScript>d__47 <GetKasada>d__48` |
| `0x14344ac44` | `<GetMfc>d__49$<GetWorkTime>d__50"<<-ctor>b__43_0>d*<<GetKasada>b__48_2>d$<<GetMfc>b__49_1>d` |
| `0x14344aed3` | `GetKasada@` |
| `0x14344af6f` | `<Reset>b__44_0$<GetKasada>b__48_0$<GetKasada>b__48_1$<GetKasada>b__48_2g` |
| `0x14344b005` | `_kasadaDt` |
| `0x14344b00f` | `_kasadaIm` |
| `0x14344b019` | `_kasadaCt` |
| `0x14344b023` | `_kasadaDv` |
| `0x14344b02d` | `_kasadaSt` |
| `0x14344b037` | `_kasadaRst` |
| `0x14344b042` | `_kasadaFc` |
| `0x14344b04c` | `_kasadaH` |
| `0x14344b055` | `_kasadaWorkTime` |
| `0x14344b174` | `*<HandleResponse>d__32 <GetScript>d__33 <GetKasada>d__34$<GetWorkTime>d__35"<<-ctor>b__29_0>d*<<GetKasada>b__34_2>d` |
| `0x14344b393` | `<Reset>b__30_0$<GetKasada>b__34_0$<GetKasada>b__34_1$<GetKasada>b__34_2g` |
| `0x143482844` | `<kasada>5__2` |
| `0x146a6b3ac` | `&x-kpsdk-v=` |
| `0x146a9207c` | `/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=` |
| `0x146a99ca4` | `/fp?x-kpsdk-v=` |
| `0x146b83204` | `Converse-Kasada-Version` |
| `0x146b8e33c` | `Crocs-EU-Kasada-Version` |
| `0x146b8e4c4` | `Crocs-JP-Kasada-Version` |
| `0x146b8e614` | `Crocs-Kasada-Version` |
| `0x146d6e70c` | `Failed Kasada (Retry limit reached)` |

## nike-cart  `(nike\.com|/api/cart|/api/checkout|launch\.nike)` — 40 条

| 地址 | 字符串 |
|---|---|
| `0x143c92ff8` | `HungLan Artdesign - http://www.vietcomic.comVNI-Thufap2  Normalv2.0 Code VNI for WindowsVNI-Thufap2 Normal\u0002":true,"font-Vietnam":false,"font-Bwviet":false,` |
| `0x146f50f7c` | `accounts.nike.com` |
| `0x146f5880c` | `api.nike.com` |
| `0x146fb7b74` | `com.nike.commerce.checkout.web` |
| `0x146fb7bcc` | `com.nike.commerce.nikedotcom.web` |
| `0x147033a0c` | `https://accounts.nike.com` |
| `0x147033a54` | `https://accounts.nike.com/authorize/v1` |
| `0x147033abc` | `https://accounts.nike.com/authorize/v1?` |
| `0x147033b24` | `https://accounts.nike.com/challenge/code/v1` |
| `0x147033b94` | `https://accounts.nike.com/challenge/password/v1` |
| `0x147033c0c` | `https://accounts.nike.com/challenge?client_id=4fd2d5e7db76e0f85a6bb56721bd51df&redirect_uri=https://www.nike.com/auth/login&response_type=code&scope=openid%20ni` |
| `0x147033eec` | `https://accounts.nike.com/check/v1` |
| `0x147033f4c` | `https://accounts.nike.com/credential_lookup/v1` |
| `0x147033fc4` | `https://accounts.nike.com/token/v1` |
| `0x147034024` | `https://accounts.nike.com/verification_code/send/v1` |
| `0x1470340a4` | `https://accounts.nike.com/verify-unrecognized-device?` |
| `0x1470373d4` | `https://api.nike.com/buy/checkout_previews/v3/` |
| `0x14703744c` | `https://api.nike.com/buy/checkout_previews_jobs/v3/` |
| `0x1470374cc` | `https://api.nike.com/buy/checkouts/v3/` |
| `0x147037534` | `https://api.nike.com/buy/checkouts_jobs/v3/` |
| `0x1470375a4` | `https://api.nike.com/buy/fulfillment_offerings_jobs/v2/` |
| `0x14703762c` | `https://api.nike.com/buy/partner_cart_preorder/v2/` |
| `0x1470376ac` | `https://api.nike.com/buy/partner_cart_preorder_jobs/v2/` |
| `0x147037734` | `https://api.nike.com/deliver/available_gtins/v3` |
| `0x1470377ac` | `https://api.nike.com/payment/3ds_authentications/v3` |
| `0x14703782c` | `https://api.nike.com/payment/3ds_results/v3` |
| `0x14703789c` | `https://api.nike.com/payment/deferred_payment_forms/v1` |
| `0x147037924` | `https://api.nike.com/payment/deferred_payment_forms/v1/jobs/` |
| `0x1470379b4` | `https://api.nike.com/payment/paypal_details/v2` |
| `0x147037a2c` | `https://api.nike.com/payment/paypal_details/v2/jobs/` |
| `0x147037aac` | `https://api.nike.com/payment/paypal_mark/v2` |
| `0x147037b1c` | `https://api.nike.com/payment/paypal_mark/v2/jobs/` |
| `0x147037b94` | `https://api.nike.com/payment/preview/v3` |
| `0x147037bfc` | `https://api.nike.com/payment/preview/v3/jobs/` |
| `0x147037c6c` | `https://api.nike.com/product_feed/threads/v2?fields=` |
| `0x1470467bc` | `https://dlpa.nike.com/6.js?namespace=` |
| `0x14704681c` | `https://dlpa.nike.com/cc.js?sid=` |
| `0x147046874` | `https://dlpa.nike.com/cdn/cs/` |
| `0x1470468c4` | `https://dlpa.nike.com/et.js` |
| `0x147046914` | `https://dlpa.nike.com/s2?t=` |

## bstn  `api/beast` — 0 条

（无）

## shopify-cart  `(cart/add\.js|cart\.js|checkouts/)` — 17 条

| 地址 | 字符串 |
|---|---|
| `0x146a96fb4` | `/cart.js` |
| `0x146a97f9c` | `/checkouts/` |
| `0x146a97fcc` | `/checkouts/internal/graphql` |
| `0x146a9e3a4` | `/v1/checkouts/` |
| `0x146f58fe4` | `api/v1/checkouts/` |
| `0x146fa53ac` | `cart/add.js` |
| `0x146faab4c` | `checkouts/` |
| `0x146faab7c` | `checkouts/c/` |
| `0x146faabac` | `checkouts/internal/graphql/persisted?operationName=CheckoutExtensionSessionToken` |
| `0x146faac64` | `checkouts/internal/graphql/persisted?operationName=PaypalDetails` |
| `0x146faacfc` | `checkouts/internal/graphql/persisted?operationName=PaypalToken` |
| `0x146faad94` | `checkouts/internal/graphql/persisted?operationName=PollForReceipt` |
| `0x146faae2c` | `checkouts/internal/graphql/persisted?operationName=Proposal` |
| `0x146faaebc` | `checkouts/internal/graphql/persisted?operationName=SubmitForCompletion` |
| `0x1470374cc` | `https://api.nike.com/buy/checkouts/v3/` |
| `0x147041eec` | `https://checkout.sportsshoes.com/api/storefront/checkouts/` |
| `0x14704d574` | `https://gw.prod.api.mschf.xyz/checkouts/auth/guests` |

## hybris  `(basket/add|minibasket|hybris)` — 3 条

| 地址 | 字符串 |
|---|---|
| `0x147162a54` | `view/basket/add` |
| `0x147162a8c` | `view/basket/addPromotionalCode` |
| `0x147162ddc` | `view/component/basket/minibasketAjax` |

## magento  `(Magento|checkout/cart/add|rest/V1)` — 9 条

| 地址 | 字符串 |
|---|---|
| `0x14326bab1` | `"FootlockerMagento` |
| `0x143325cb0` | `0FootlockerMagentoHandler` |
| `0x143381c0a` | `Magento` |
| `0x146a97b6c` | `/checkout/cart/addcoupon/?couponCode=` |
| `0x146a9bd74` | `/rest/V1` |
| `0x146a9bd9c` | `/rest/V1/ppcp/` |
| `0x146d7832c` | `FootlockerMagento` |
| `0x146ddf964` | `Magento` |
| `0x147038f24` | `https://api2.endclothing.com/rest/V1` |

## casio  `(casio\.com|/us_en|AEM)` — 0 条

（无）

## fanatics  `(fanatics|akamai|_abck)` — 40 条

| 地址 | 字符串 |
|---|---|
| `0x14322640b` | `AkamaiPixel` |
| `0x143226db6` | `(AkamaiGeneratorHyped` |
| `0x143227470` | `&AkamaiGeneratorJevi` |
| `0x14322a071` | `Akamai` |
| `0x14330d102` | `GetAkamaiCookie@` |
| `0x14330d2de` | `s IAkamaiGenerator` |
| `0x143320fa3` | `AkamaiHandler` |
| `0x1433215d8` | `$AkamaiQueueHandler` |
| `0x143360319` | `_akamai_pid` |
| `0x14337ccb5` | `_homeAkamai` |
| `0x1433b5a23` | `C`/ AkamaiUserAgents` |
| `0x1433b5a3a` | `<,AkamaiMobileUserAgents` |
| `0x143438604` | `Domain0https://id.fanatics.com/"CloudflareRequest` |
| `0x143445422` | `_abckUseCount` |
| `0x14347d191` | `accountAkamai` |
| `0x146b2474c` | `Akamai` |
| `0x146b24774` | `Akamai API down (Contact Staff)` |
| `0x146b247cc` | `Akamai API down (Contact staff)` |
| `0x146b24824` | `Akamai Blocked (IP)` |
| `0x146b24864` | `Akamai Challenge block` |
| `0x146b248ac` | `Akamai Failed` |
| `0x146b248dc` | `Akamai Failed (Rotating)` |
| `0x146b24924` | `Akamai block` |
| `0x146b24954` | `Akamai block (Rotating...)` |
| `0x146b249a4` | `Akamai disabled` |
| `0x146b249dc` | `AkamaiGHost` |
| `0x146b24a0c` | `AkamaiQueueName` |
| `0x146b24a44` | `AkamaiReferer` |
| `0x146e7243c` | `SkipAkamai` |
| `0x146e77ebc` | `Solving Akamai (` |
| `0x146e77ef4` | `Solving Akamai (SBSD)` |
| `0x146e77f34` | `Solving Akamai (SDS)` |
| `0x146f44b4c` | `_abck` |
| `0x146f4781c` | `_fanaticsone` |
| `0x146f54524` | `akamai` |
| `0x146f5454c` | `akamaiMulticurrency` |
| `0x146f5458c` | `akamaiRequest` |
| `0x14704f90c` | `https://id.fanatics.com` |
| `0x14704f954` | `https://id.fanatics.com/` |
| `0x14704f99c` | `https://id.fanatics.com/api-internal/login/factor-request` |

## scheels  `(scheels)` — 33 条

| 地址 | 字符串 |
|---|---|
| `0x1433a70d7` | `Scheels	` |
| `0x146e579a4` | `SCHEELS` |
| `0x146e5e884` | `Scheels` |
| `0x146e5e8ac` | `Scheels-Kasada-Version` |
| `0x146e5e8f4` | `Scheels/2.8.3.946 CFNetwork/1.0 Darwin/25.5.0 (iPhone iOS/26.5.2)` |
| `0x146f59384` | `apihub.scheels.com` |
| `0x147038f84` | `https://apihub.scheels.com/frontastic/action/account/getAccount` |
| `0x14703901c` | `https://apihub.scheels.com/frontastic/action/account/login` |
| `0x1470390ac` | `https://apihub.scheels.com/frontastic/action/account/register` |
| `0x14703913c` | `https://apihub.scheels.com/frontastic/action/account/requestReset` |
| `0x1470391d4` | `https://apihub.scheels.com/frontastic/action/account/reset` |
| `0x147039264` | `https://apihub.scheels.com/frontastic/action/adyen/beginPayPal` |
| `0x1470392fc` | `https://apihub.scheels.com/frontastic/action/adyen/completePayPal` |
| `0x147039394` | `https://apihub.scheels.com/frontastic/action/cart/addToCart` |
| `0x147039424` | `https://apihub.scheels.com/frontastic/action/cart/checkout` |
| `0x1470394b4` | `https://apihub.scheels.com/frontastic/action/cart/clean` |
| `0x14703953c` | `https://apihub.scheels.com/frontastic/action/cart/completeDetailsCheckout` |
| `0x1470395e4` | `https://apihub.scheels.com/frontastic/action/cart/completeSignifydStepUpCheckout` |
| `0x14703969c` | `https://apihub.scheels.com/frontastic/action/cart/removeLineItem` |
| `0x147039734` | `https://apihub.scheels.com/frontastic/action/cart/sendSignifydStepUpCode` |
| `0x1470397dc` | `https://apihub.scheels.com/frontastic/action/cart/setAdyenCreditCard` |
| `0x14703987c` | `https://apihub.scheels.com/frontastic/action/cart/updateCart` |
| `0x14703990c` | `https://apihub.scheels.com/frontastic/action/product/getProduct` |
| `0x14705755c` | `https://mobile-api.scheels.com/v5/auth/guest` |
| `0x1470575cc` | `https://mobile-api.scheels.com/v5/products/` |
| `0x14707d21c` | `https://www.scheels.com/` |
| `0x14708b314` | `is-scheels` |
| `0x1470a7fbc` | `mobile-api.scheels.com` |
| `0x147135e54` | `scheels.com` |
| `0x147135e84` | `scheels_` |
| `0x147135eac` | `scheels_com` |
| `0x147135edc` | `scheels_registration` |
| `0x14716bde4` | `x-scheels-customerkey` |

## warhammer  `(warhammer)` — 17 条

| 地址 | 字符串 |
|---|---|
| `0x143328bed` | `&WarhammerWafHandler` |
| `0x1433a9802` | `WarHammer` |
| `0x14349f74a` | `&<SubmitCard>b__57_0:<AwaitDeviceProfiling>b__62_0,api.prod.warhammer.com` |
| `0x14349f79d` | `_loginHost:https://login.mywarhammer.com` |
| `0x14349fb25` | `Warhammer` |
| `0x146f0b2c4` | `Warhammer` |
| `0x146f5883c` | `api.prod.warhammer.com` |
| `0x1470381ac` | `https://api.prod.warhammer.com/graphql` |
| `0x147054d34` | `https://login.mywarhammer.com` |
| `0x147054d84` | `https://login.mywarhammer.com/login/callback` |
| `0x147054df4` | `https://login.mywarhammer.com/oauth/token` |
| `0x147054e5c` | `https://login.mywarhammer.com/usernamepassword/challenge` |
| `0x147054ee4` | `https://login.mywarhammer.com/usernamepassword/login` |
| `0x14707fb0c` | `https://www.warhammer.com/` |
| `0x14707fb5c` | `https://www.warhammer.com/callback/login?redirect=/` |
| `0x147165404` | `warhammer` |
| `0x14716542c` | `warhammer-com-waf-auth` |

## queue-it  `(queue-it|queueit)` — 37 条

| 地址 | 字符串 |
|---|---|
| `0x14322b470` | `QueueIt` |
| `0x14332782f` | `QueueItHandler` |
| `0x143381515` | `queueItHandler` |
| `0x143383190` | `_queueItHandler` |
| `0x14340e3bb` | `QueueItemD<GetDigestTokenForCredential>d__400<SendWithAuthAsync>d__174<SendWithNtAuthAsync>d__528<TrySetDigestAuthToken>d__152ChunkedEncodingReadStream` |
| `0x14344dc1e` | ` QueueHostMarkers(AcceptedCookiePrefix<QueueITAccepted-SDFrts345E-V3_*CookieValiditySecondsa	&MinRemainingSeconds(ShareIntervalSeconds` |
| `0x1436d5a01` | `2DequeueItemAndPostProcess@` |
| `0x146a8e8cc` | `.queue-it.net` |
| `0x146a977ec` | `/challengeapi/queueitcaptcha/challenge/` |
| `0x146a9bc2c` | `/queueit` |
| `0x146cf16cc` | `Error Initiliazing Queue-it (Softblock)` |
| `0x146cf1734` | `Error Solving Queue-it (Softblock)` |
| `0x146d72e7c` | `Fetching Queue-it challenge` |
| `0x146da115c` | `Initiliazing Queue-it` |
| `0x146e3c36c` | `Queue-IT banned, rotating proxy` |
| `0x146e3c3c4` | `Queue-it` |
| `0x146e3c3ec` | `QueueITAccepted` |
| `0x146e3c424` | `QueueITAccepted-SDFrts345E-V3_` |
| `0x146e3c47c` | `QueueItEventId` |
| `0x146e3c55c` | `QueueitEnqueueToken` |
| `0x146e47e24` | `Redirected into a Queue-it waiting room` |
| `0x146ef8ad4` | `Unsupported Queue-it BotDeflector page` |
| `0x146f12454` | `X-queueit-challange-reason` |
| `0x1470f0074` | `panini.queue-it.net` |
| `0x14712ab9c` | `queue-it` |
| `0x14712abc4` | `queue-it-set-cookie` |
| `0x14712ac04` | `queue-it.net` |
| `0x14712ad6c` | `queueittoken` |
| `0x14716ba04` | `x-queueit-ajaxpageurl` |
| `0x14716ba44` | `x-queueit-ajaxpageurl-web` |
| `0x14716ba8c` | `x-queueit-challange-customerid` |
| `0x14716bae4` | `x-queueit-challange-eventid` |
| `0x14716bb34` | `x-queueit-challange-hash` |
| `0x14716bb7c` | `x-queueit-challange-reason` |
| `0x14716bbcc` | `x-queueit-challange-ruleid` |
| `0x14716bc1c` | `x-queueit-challange-rulename` |
| `0x14716bc6c` | `x-queueit-redirect` |

## captcha-hosts  `(hcaptcha\.com|recaptcha|geetest|turnstile|funcaptcha)` — 40 条

| 地址 | 字符串 |
|---|---|
| `0x1432009e7` | `Cybersole.Models.SolverSettings,Cybersole.Core.ReCaptchaSegmentation!Getter` |
| `0x143200a33` | `Cybersole.Models.SolverSettings,Cybersole.Core.ReCaptchaSegmentation!Setter` |
| `0x143200a7f` | `Cybersole.Models.SolverSettings,Cybersole.Core.ReCaptchaMultiClassification!Getter` |
| `0x143200ad2` | `Cybersole.Models.SolverSettings,Cybersole.Core.ReCaptchaMultiClassification!SetterdCybersole.Models.Solver,Cybersole.Core.View!GetterjCybersole.Models.Solver,Cy` |
| `0x14321682d` | `get_Geetest` |
| `0x143216839` | `get_GeetestV4` |
| `0x143216861` | `get_Turnstile` |
| `0x1432168f3` | `0<Captcha>k__BackingFieldD<CaptchaEnterprise>k__BackingField8<EmptySolver>k__BackingField0<Geetest>k__BackingField4<GeetestV4>k__BackingField2<HCaptcha>k__Backi` |
| `0x143216aad` | `Geetest` |
| `0x143216ab9` | `GeetestV4` |
| `0x143216ae1` | `Turnstile` |
| `0x1432f56b2` | `Recaptcha` |
| `0x1432f56be` | `/$RecaptchaInvisible` |
| `0x1432f56d3` | `RecaptchaV3"HCaptchaInvisible&RecaptchaEnterprise&CloudflareTurnstile` |
| `0x1432f7330` | `"<Recaptcha>d__1150<Recaptcha_Source>d__116` |
| `0x1432f7373` | `"<Turnstile>d__1170<Turnstile_Source>d__118` |
| `0x1432f764f` | `"get_TestRecaptcha get_TestHcaptcha` |
| `0x1432f776d` | `ReloadChanged&ExecuteTestHcaptcha(ExecuteTestRecaptcha@` |
| `0x1432f792c` | ` Recaptcha_Sourceg` |
| `0x1432f7951` | ` Turnstile_Sourceg` |
| `0x1432f7a1c` | ` _reCaptchaSolver` |
| `0x1432f7b71` | `<<TestRecaptcha>k__BackingField:<TestHcaptcha>k__BackingField.<Reload>k__BackingField` |
| `0x1432f7e55` | `TestRecaptcha` |
| `0x1432f7fa4` | `set_AutoClick2get_ReCaptchaSegmentation2set_ReCaptchaSegmentation@get_ReCaptchaMultiClassification@set_ReCaptchaMultiClassification@<AutoBoundingBox>k__BackingF` |
| `0x1432f8178` | `+wo*ReCaptchaSegmentation` |
| `0x1432f8196` | `3xo8ReCaptchaMultiClassification` |
| `0x14332d46d` | `,UnpairedObjectPropInit:get_RecaptchaClassifyResponse@` |
| `0x14332d4ab` | `@Create_RecaptchaClassifyResponse@` |
| `0x14332d4d9` | `BRecaptchaClassifyResponsePropInit4get_RecaptchaSolveResponse@` |
| `0x14332d51f` | `:Create_RecaptchaSolveResponse@` |
| `0x14332d54a` | `<RecaptchaSolveResponsePropInit` |
| `0x14332db25` | `4_RecaptchaClassifyResponse` |
| `0x14332db45` | `._RecaptchaSolveResponse` |
| `0x14332de8f` | `3_y2RecaptchaClassifyResponse@` |
| `0x14332deb5` | ``y,RecaptchaSolveResponse@` |
| `0x143370e9a` | `_projectId"_turnstileEnabled` |
| `0x143370eb7` | `_turnstileKey` |
| `0x143375f4c` | `_adyenOrderId*https://www.casio.com RecaptchaSiteKeyP6LfeU4ofAAAAAHTDXnfN1V9EroVWvwEPeqrXybdj` |
| `0x143375fc5` | `"_recaptchaSiteKey` |
| `0x143386b4e` | `_recaptchaKey` |

## vendor-hosts  `cybersole\.io` — 0 条

（无）
