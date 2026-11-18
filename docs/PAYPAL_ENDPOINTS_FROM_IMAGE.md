# PayPal 端点的真实清单（R1145，Observation）

镜像里 `paypal.com` 相关字面量共 **35 条**（`ida.py str "paypal\.com" --limit 40`，`saturated: false`）。
这张表是本轮从 IDB 直接取出的原始清单，供支付层后续取件比对；**不是**我们对流程的解释。

## 一、结账与订单（REST 风格，但 host 是 `www`）

| 地址 | 原文 |
|---|---|
| `0x14709910c` | `https://www.paypal.com/v2/checkout/orders` |
| `0x147099174` | `https://www.paypal.com/v2/checkout/orders/` |

**本轮据此修正**：复刻件原先用 `https://api.paypal.com/v2/checkout/orders`（`StoreFlow.cs` 两处：
`SubmitPayPalAsync` 的 capture、`GetPayPalTokenAsync` 的 create）。
**路径是对的，host 是编的。** 已改为镜像的 `www.paypal.com`。
`https://api.paypal.com/v1/oauth2/token`（`GetPayPalAccessTokenAsync`）**镜像里没有 oauth2 端点**，
仍留在 `EndpointLedgerTests` 的 `assembled` 一栏，**未改**——它需要一次判断，而不是一次改名。

## 二、网页 / GraphQL 流程

| 地址 | 原文 |
|---|---|
| `0x147097e84` | `https://www.paypal.com/graphql/` |
| `0x147097edc` | `https://www.paypal.com/graphql?ApproveOnboardPaymentMutation` |
| `0x147097f6c` | `https://www.paypal.com/graphql?GetThreeDsJwtQuery` |
| `0x147097fe4` | `https://www.paypal.com/graphql?OnboardGuestMutation` |
| `0x147098064` | `https://www.paypal.com/graphql?ResolveThreeDsContingency` |
| `0x1470980ec` | `https://www.paypal.com/graphql?ThreeDsAuthenticateMutation` |
| `0x14709817c` | `https://www.paypal.com/graphql?ThreeDsLookUpMutation` |

## 三、3DS 家族（`payment-authentication/threeds/v1/`）

| 地址 | 原文 |
|---|---|
| `0x14709854c` | `…/payment-authentication/threeds/v1/init-challenge` |
| `0x1470985f4` | `…/payment-authentication/threeds/v1/init-method` |
| `0x147098694` | `…/payment-authentication/threeds/v1/notify-challenge-cmpl/` |
| `0x14709874c` | `…/payment-authentication/threeds/v1/notify-method-cmpl` |

**这一条侧证解掉了旧疑点**：长期挂起的 `notify-challenge-cmpl` 一直缺的是**请求体键**，
而它的**完整 URL 形态**在此可见（带尾斜杠，`…/notify-challenge-cmpl/`）——旧记录里那个「parked」条目
应当以这个形态为准。

## 四、heliosnext / 页面

| 地址 | 原文 |
|---|---|
| `0x1470981fc` | `https://www.paypal.com/heliosnext/api/` |
| `0x147098264` | `…/heliosnext/api/processThreedsConfirmation` |
| `0x1470982fc` | `…/heliosnext/api/serverData` |
| `0x147098374` | `…/heliosnext/api/session` |
| `0x1470983e4` | `…/heliosnext/threeDS?action=verify&flow=3ds&cart_id=` |
| `0x147097cac` | `https://www.paypal.com/checkoutnow?token=` |
| `0x147097c44` | `https://www.paypal.com/checkoutnow/error` |
| `0x147097d14` | `https://www.paypal.com/checkoutweb/processThreedsConfirmation` |
| `0x147097da4` / `0x147097e0c` | `…/checkoutweb/signup` · `…/checkoutweb/signup/?token=` |
| `0x1470984ec` | `https://www.paypal.com/pay/checkout` |
| `0x1470987fc` | `https://www.paypal.com/signin` |
| `0x14709884c` / `0x1470988ac` / `0x147098914` | `…/smart/buttons` · `…/smart/card-field` · `…/smart/card-field?type=number&clientID=…` |
| `0x146a763a4` | `"url":"https://www.paypal.com/webapps/hermes?` |
| `0x14709848c` | `https://www.paypal.com/mep/dashboard` |
| `0x147097bb4` / `0x147097bfc` | `https://www.paypal.com` · `https://www.paypal.com/` |

## 五、这张表怎么重算

```
python analysis\ida.py str "paypal\.com" --limit 40
```

（`ida.py str` 连续调用约 25 次后传输会退化，见 R1144；单次调用不受影响。）
