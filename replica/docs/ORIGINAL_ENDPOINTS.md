# 原版端点表（从二进制提取）

**来源**：`C:\Users\wykk\AppData\Local\Cybersole\current\Cybersole.exe`（123 MB，NativeAOT 单文件），
IDA Pro 9.3sp2 载入后经 `ida_mcp` 的 `find_regex` 检索字符串缓存（**491,542 条**）。

**这一页不是猜的，也不是从文档抄的。** 每一行都是二进制里存在的字符串，地址可复查。

**局限**：`auto_analysis_ready` 仍是 `false`，所以**没有 xref**——这里能回答「原版调什么路径」，
不能回答「哪个函数调它」。字符串存在 ≠ 代码在用，但对 URL 而言二者高度一致。

---

## 1. Nike —— 28 个端点，Kasada 自主生成

### 账户（`accounts.nike.com`）

```
https://accounts.nike.com/authorize/v1
https://accounts.nike.com/authorize/v1?
https://accounts.nike.com/challenge/code/v1
https://accounts.nike.com/challenge/password/v1
https://accounts.nike.com/check/v1
https://accounts.nike.com/credential_lookup/v1
https://accounts.nike.com/token/v1
https://accounts.nike.com/verification_code/send/v1
https://accounts.nike.com/verify-unrecognized-device?
```

**OAuth client_id**：`4fd2d5e7db76e0f85a6bb56721bd51df`
**redirect_uri**：`https://www.nike.com/auth/login`，scope 含 `openid ni…`

### 购买（`api.nike.com`）

```
https://api.nike.com/buy/checkout_previews/v3/
https://api.nike.com/buy/checkout_previews_jobs/v3/
https://api.nike.com/buy/checkouts/v3/
https://api.nike.com/buy/checkouts_jobs/v3/
https://api.nike.com/buy/fulfillment_offerings_jobs/v2/
https://api.nike.com/buy/partner_cart_preorder/v2/
https://api.nike.com/buy/partner_cart_preorder_jobs/v2/
https://api.nike.com/deliver/available_gtins/v3
https://api.nike.com/product_feed/threads/v2?fields=
```

**注意 `_jobs` 的存在**：`checkout_previews_jobs` / `checkouts_jobs` / `fulfillment_offerings_jobs` /
`partner_cart_preorder_jobs`。**原版同时有同步和异步两条路**——异步提交后轮询 job 状态，
这是 Nike 在高峰期的推荐路径。replica 只有同步那条。

### 支付

```
https://api.nike.com/payment/3ds_authentications/v3
https://api.nike.com/payment/3ds_results/v3
https://api.nike.com/payment/deferred_payment_forms/v1
https://api.nike.com/payment/deferred_payment_forms/v1/jobs/
https://api.nike.com/payment/paypal_details/v2
https://api.nike.com/payment/paypal_mark/v2
https://api.nike.com/payment/preview/v3
https://api.nike.com/payment/preview/v3/jobs/
```

### 反爬（`dlpa.nike.com`）

```
https://dlpa.nike.com/6.js?namespace=
https://dlpa.nike.com/cc.js?sid=
https://dlpa.nike.com/cdn/cs/
https://dlpa.nike.com/et.js
https://dlpa.nike.com/s2?t=
```

### Kasada —— 这是自己实现的，不是接第三方

**类型表**（字符串里可读）：

```
IKasadaSolver          KasadaSolveResult      KasadaSolveRequest
KasadaCdSolver         KasadaHandler          KasadaMobileHandler
AkamaiGeneratorHyped   AkamaiGeneratorJevi    AkamaiPixel
```

**方法表**（`<Method>d__N` 是 C# async 状态机的编译产物，NativeAOT 保留了名字）：

```
<HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48  <GetMfc>d__49  <GetWorkTime>d__50
<Reset>b__44_0  <<GetKasada>b__48_0  <<GetKasada>b__48_1  <<GetKasada>b__48_2
```

**九个字段**：

```
_kasadaDt  _kasadaIm  _kasadaCt  _kasadaDv  _kasadaSt
_kasadaRst _kasadaFc  _kasadaH   _kasadaWorkTime
```

**指纹端点**：

```
/fp?x-kpsdk-v=
/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=
x-kpsdk-v=
```

**两个 UUID 是固定的站点标识**（Kasada 按客户分配），不是随机 nonce。

**结论**：用户最初问「nike 模块 cyber 做到了 kasada 直接生成，不确定是不是接了第三方」——
**不是第三方。** 原版有完整的 handler（取脚本 → 算 → 回填 → 处理响应 → 记工作时间）、
九个 sensor 字段、和 `/fp?x-kpsdk-v=` 端点。`KasadaCdSolver` 里的 `Cd` 是 Chrome DevTools
的缩写，说明它还保留了走浏览器算的一条路。

### 版本标记

```
Converse-Kasada-Version
Crocs-EU-Kasada-Version
Crocs-JP-Kasada-Version
Crocs-Kasada-Version
Scheels-Kasada-Version
```

**每个 Kasada 站点一个版本头**，说明 `get_KasadaVersion` 是按站点取的，不是全局常量。

---

## 2. Scheels —— 21 个 frontastic 端点

`scheels` 在 replica 里是 `Guarded`（Kasada 拦直连），**而原版有完整路径**：

### 购物车 / 结账

```
https://apihub.scheels.com/frontastic/action/cart/addToCart              ← 加购
https://apihub.scheels.com/frontastic/action/cart/checkout
https://apihub.scheels.com/frontastic/action/cart/clean
https://apihub.scheels.com/frontastic/action/cart/completeDetailsCheckout
https://apihub.scheels.com/frontastic/action/cart/completeSignifydStepUpCheckout
https://apihub.scheels.com/frontastic/action/cart/removeLineItem
https://apihub.scheels.com/frontastic/action/cart/sendSignifydStepUpCode
https://apihub.scheels.com/frontastic/action/cart/setAdyenCreditCard
https://apihub.scheels.com/frontastic/action/cart/updateCart
```

### 账户 / 商品 / 支付

```
https://apihub.scheels.com/frontastic/action/account/getAccount
https://apihub.scheels.com/frontastic/action/account/login
https://apihub.scheels.com/frontastic/action/account/register
https://apihub.scheels.com/frontastic/action/account/requestReset
https://apihub.scheels.com/frontastic/action/account/reset
https://apihub.scheels.com/frontastic/action/adyen/beginPayPal
https://apihub.scheels.com/frontastic/action/adyen/completePayPal
https://apihub.scheels.com/frontastic/action/product/getProduct
```

### 移动端 API

```
https://mobile-api.scheels.com/v5/auth/guest
https://mobile-api.scheels.com/v5/products/
```

### 伪装

```
UA:      Scheels/2.8.3.946 CFNetwork/1.0 Darwin/25.5.0 (iPhone iOS/26.5.2)
Header:  x-scheels-customerkey
Cookie:  scheels_ / scheels_com / scheels_registration
```

**`Signifyd` 两步**（`sendSignifydStepUpCode` + `completeSignifydStepUpCheckout`）说明 Scheels 有
设备指纹二次验证，和 Nike 的 3DS 是不同机制。

---

## 3. Warhammer —— GraphQL，不是 REST

replica 里 `warhammer` 是 `Live`，但三条 REST 路径全 403。**原版根本不走 REST**：

```
https://api.prod.warhammer.com/graphql                    ← 唯一业务端点
https://login.mywarhammer.com/oauth/token
https://login.mywarhammer.com/usernamepassword/challenge
https://login.mywarhammer.com/usernamepassword/login
https://www.warhammer.com/callback/login?redirect=/
```

**`warhammer-com-waf-auth`** 是它的 WAF 标识；`<AwaitDeviceProfiling>b__62_0` 说明登录后有
设备画像等待。

**「403 是 WAF 无差别拒绝，不携带路径信息」这个 R90 的结论，现在看来方向错了**：
不是 WAF 无差别，是**路径本身就不对**。

---

## 4. Fanatics

```
https://id.fanatics.com/api-internal/login/factor-request
```

**`api-internal`** —— 这个前缀是给自家前端用的，不是公开 API。
加上 `_abck` / `AkamaiHandler` / `AkamaiQueueHandler` / `AkamaiPixel`，
`fanatics` 的 403 是 Akamai Bot Manager + 内部登录端点两层。

---

## 5. Queue-it —— 完整 header 集合

```
QueueITAccepted-SDFrts345E-V3_        （cookie 名前缀）
x-queueit-challange-reason            （注意拼写 challange，不是 challenge）
x-queueit-challange-customerid
x-queueit-challange-eventid
x-queueit-challange-hash
x-queueit-challange-ruleid
x-queueit-challange-rulename
x-queueit-ajaxpageurl
x-queueit-ajaxpageurl-web
x-queueit-redirect
/challengeapi/queueitcaptcha/challenge/
```

**`challange` 这个拼写**：Queue-it 自己的 API 就是这么拼的（他们的历史 bug），
照着写才对。写成 `challenge` 服务端不认。

**`QueueITAccepted-SDFrts345E-V3_`** —— `SDFrts345E` 是固定后缀，跟版本号。

---

## 6. Hybris（offspring 等）

```
view/basket/add
view/basket/addPromotionalCode
view/component/basket/minibasketAjax
```

**`view/` 前缀**，不是 `/cart/`。replica 的 `offspring` 试的四个候选全 404，
因为都在猜 `/cart/add` 一类的形状。

---

## 7. Shopify —— 标准路径 + 一个意外的内部 GraphQL

```
cart/add.js
/cart.js
/checkouts/
checkouts/c/
/checkouts/internal/graphql
checkouts/internal/graphql/persisted?operationName=CheckoutExtensionSessionToken
checkouts/internal/graphql/persisted?operationName=PaypalDetails
checkouts/internal/graphql/persisted?operationName=PaypalToken
checkouts/internal/graphql/persisted?operationName=PollForReceipt
checkouts/internal/graphql/persisted?operationName=Proposal
checkouts/internal/graphql/persisted?operationName=SubmitForCompletion
```

**`checkouts/internal/graphql/persisted`** 是原版的深层路径——**persisted query**（operationName
而不是完整 query 文本），并且有 **`PollForReceipt`**（异步确认）。

`/cart/add` 之外还有 `/cart/addPromoCode`、`/cart/address`、`/checkout/cart/addcoupon/?couponCode=`。

**`form[action*='/cart/add'] input[name*='properties']`** —— 一条 **CSS 选择器**，
说明原版在 Shopify 上确实读 DOM（和 `bstn` 的视觉匹配不是一回事）。

---

## 8. Magento / Footlocker

```
/rest/V1
/rest/V1/ppcp/
https://api2.endclothing.com/rest/V1
FootlockerMagento / FootlockerMagentoHandler
```

---

## 9. Casio —— 有 recaptcha site key

```
https://www.casio.com
RecaptchaSiteKey: 6LfeU4ofAAAAAHTDXnfN1V9EroVWvwEPeqrXybdj
```

**`_adyenOrderId`** 说明走 Adyen。`casio` 在 replica 是 `Guarded`。

---

## 10. 三个「零命中」——负面证据

| pattern | 结果 | 含义 |
|---|---|---|
| `api/beast` | **0 条** | replica 的 `BstnFlow` 注释说 `/api/beast/geoIP` 200 已验证，**但原版二进制里没有这个字符串** |
| `casio\.com\|/us_en\|AEM` | **0 条**（除 site key 那条） | AEM 是实测推断，不是二进制里的 |
| `cybersole\.io` | **0 条** | 厂商域名运行时拼接，符合 R174–R178 的判断 |

**`api/beast` 这条最值得注意**：`BstnFlow` 基于一次 HTTP 探测把 `/api/beast/` 当作已验证，
而原版没有这个字面量。两种解释：

1. 原版用**视觉匹配**找商品（`match.cybersole.io`），根本不猜路径；
2. 路径确实存在，但由别的方式拼接。

**R153 的发现支持第一种**：`/locate` 做 tile-detect + siglip 图文匹配，**不解析 DOM**。

---

## 与 replica 的对照（需要改的）

| 站点 | replica 现状 | 原版实际 | 差 |
|---|---|---|---|
| `warhammer` | REST ×3 全 403 | **GraphQL** `api.prod.warhammer.com/graphql` | **路径类别错了** |
| `offspring` | `/cart/add` 类候选全 404 | `view/basket/add` | **前缀错了** |
| `scheels` | Guarded（Kasada 拦） | 21 个 frontastic 路径 + 移动 UA + `x-scheels-customerkey` | 有路径，缺 Kasada 会话 |
| `nike` | 有 Kasada 层 | 28 端点 + `_jobs` 异步 + `dlpa` | **缺异步和 dlpa** |
| `bstn` | `/api/beast/` | 二进制无此串 | 待定 |
| `fanatics` | Akamai 403 | `id.fanatics.com/api-internal/login/factor-request` | 端点已知，缺会话 |

---

**这一页的用法**：`PARITY.md` §3 的能力表说某模块「✅」或「❌」时，
判据应该是**这里有没有它的端点**，而不是「试了通不通」。
