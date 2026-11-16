# 端点族 ↔ 宿主：从镜像取证（R893）

每一条都是 Observation：族与宿主在**同一个字面量**里同时出现（例如
`//checkout.johnlewis.com/bff/v2/orders`），不是靠池内邻近推断的。

复算命令（在 `D:\projects\cyber-reverse` 下）：

```
python analysis\ida.py py "exec(open(r'D:/projects/cyber-reverse/analysis/famhost.py').read(), {})"
```

范围：镜像中形如 `/<segment>/v<N>/` 的族，共 56 个；其中 **45 个与某个宿主同处一条字面量**。
另外 11 个族没有同现宿主（相对路径、或宿主来自配置），**未列**。

---

## 一、按宿主分组

| 宿主 | 族 |
|---|---|
| **`api.nike.com`** | **11 族**：`/checkout_previews/v3/` · `/checkout_previews_jobs/v3/` · `/checkouts/v3/` · `/checkouts_jobs/v3/` · `/deferred_payment_forms/v1/` · `/fulfillment_offerings_jobs/v2/` · `/partner_cart_preorder/v2/` · `/partner_cart_preorder_jobs/v2/` · `/paypal_details/v2/` · `/paypal_mark/v2/` · `/preview/v3/` |
| **`checkout.johnlewis.com`** | **4 族**：`/bff/v1/` · `/bff/v2/` · `/bff/v3/` · `/bff/v4/` |
| **`www.vans.com`** | 3 族：`/cart/v1/` · `/cart/v2/` · `/products/v2/` |
| `checkoutshopper-live.adyen.com` | 2 族：`/checkoutshopper/v1/` · `/paybylink/v1/` |
| `app.midtrans.com` | 2 族：`/snap/v1/` · `/snap/v2/` |
| **`prod-hk-actapi.popmart.com`** | 1 族：`/activity/v1/` |
| **`challenges.cloudflare.com`** | 1 族：**`/turnstile/v0/`** |
| `inbox-api.aycd.io` | 1 族：`/api/v1/` |
| `id.asics.com` | 1 族：`/api/v2/` |
| `paymentsheet-ent.wdprapps.disney.com` | 1 族：`/api/v3/` |
| `www.nike.com` | 1 族：`/api/v5/` |
| `static-forms.klaviyo.com` | 1 族：`/api/v7/` |
| `api-search.dickssportinggoods.com` | 1 族：`/catalog-productdetails/v4/` |
| `payments.dickssportinggoods.com` | 1 族：`/paygate/v2/` |
| `www.vivapayments.com` | 1 族：`/checkout/v2/` |
| `api.braintreegateway.com` | 1 族：`/client_api/v1/` |
| `auth.casio-intl.com` | 1 族：`/connect/v1/` |
| `flex.cybersource.com` | 1 族：`/flex/v2/` |
| `api.sibspayments.com` | 1 族：`/form/v1/` |
| `api.vipps.no` | 1 族：`/internal/v1/` |
| `checkout.sportsshoes.com` | 1 族：`/internalapi/v1/` |
| `registerdisney.go.com` | 1 族：`/jgc/v8/` |
| `payments.bigcommerce.com` | 1 族：`/public/v1/` |
| `www.paypal.com` | 1 族：`/threeds/v1/` |
| `www.goat.com` | 1 族：`/web-api/v1/` |
| `webservices.global-e.com` | 1 族：`/Checkout/v2/` |
| `pbiouukmdvahsphokqle.supabase.co` | 1 族：`/functions/v1/` |
| `www.ibm.com` | 1 族：`/dtd/v11/` |

---

## 二、这张表对优先级 ② 的三条

| 宿主 | 族 | 读法 |
|---|---|---|
| **`challenges.cloudflare.com`** | **`/turnstile/v0/`** | **Cloudflare Turnstile** —— R876 在模型字段里见过 `_turnstileKey`，此处是它的端点 |
| **`inbox-api.aycd.io`** | `/api/v1/` | **AYCD** 是验证码/OTP 收取服务；复刻件的 `AycdInboxAccount` 模型（R883 基线）对应它 |
| `flex.cybersource.com` · `www.paypal.com` · `app.midtrans.com` | `/flex/v2/` · `/threeds/v1/` · `/snap/v1..v2/` | **3DS 与支付重定向** —— 不是风控，但同属「结账后半段」 |

---

## 三、这张表对优先级 ① 的一条更正

**`prod-hk-actapi.popmart.com` 只带 `/activity/v1/` 一个族。**

**所以 PopMart 有**三个**路径空间，宿主不同：**

| 宿主或前缀 | 族 |
|---|---|
| `popmart.com`（由 `Origin(c.Url)` 拼） | `/shop/v1/`（41 条）· `/store/v1/`（5 条） |
| **`prod-hk-actapi.popmart.com`** | **`/activity/v1/`（2 条）** |

**这解释了 R835：当时搜 `activity/v1/exhibit_draw` 在 actapi 上找 `StartDrawFlow`，没找到 ——
因为抽签走 `/shop/v1/drawScratch/*`，而 `activity/v1` 是**另一个宿主的另一个空间**。**

---

## 四、边界（必须与表一起读）

1. **45 / 56**：11 个族没有同现宿主，**不在本表**。
2. **同现是证据，不是归属唯一性**：`/api/v1/` 出现在 `inbox-api.aycd.io`、`www.goat.com`、`hbx.com`
   三个宿主上（R883 的族清单里 `/api/v1/` 有 21 条路径）—— **一个族名可以属于多个站。**
3. **宿主 ≠ 站点模块**：`api.nike.com` 是 Nike，而 `challenges.cloudflare.com` 是**厂商**而非站。
   所以这张表混了两类：**站的 API** 与**厂商的 API**。
4. **本表不说明复刻件有没有实现**——那是 R892 的 3 / 21 / 32 分级。
