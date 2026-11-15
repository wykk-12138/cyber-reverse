import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## John Lewis：17 步 ↔ 12 端点（第 118 轮）—— 第一次「步比端点还多」

| 步 | 端点 |
|---|---|
| `WebHandOver`、`SessionHandover` | `bff/v2/sessions/web/handover` |
| `GuestCallback` | `bff/v4/callback/guest` |
| `DeliveryPage` | `bff/v3/orderforms/delivery-page` |
| `SubmitShipping`、`CreateDelivery` | `bff/v4/orderforms/deliveries` |
| `GetDeliveryMethods`、`SubmitDeliveryMethod` | `bff/v3/orderforms/deliveries/details` |
| `GetPaymentPage` | `bff/v2/orderforms/payment-page` |
| `SubmitOrderStripe`、`AuthenticatePayment` | `bff/v2/orderforms/payments` |
| `SubmitOrder`、`PlaceOrder` | `bff/v2/orders` |
| `SubmitBillingAddress` | `bff/v1/orderforms/payments/billing-address` |

**14 步 → 9 个不同端点。**

### 这个形状本身就是一条结论

**BFF 端点是「服务端的资源」，步是「客户端的阶段」。** 所以两个步共用一个端点是正常的，
不是错误 —— `handover` 同时服务 `WebHandOver` 和 `SessionHandover`，
`deliveries` 同时服务 `SubmitShipping` 和 `CreateDelivery`。**不要为了「一一对应」去拆端点。**

### 留空的 3 步：一个页面加载 + 两次 Stripe 调用

| 步 | 为什么留空 |
|---|---|
| `GetHome` | 页面加载，不是 BFF 资源 |
| `HandleRequiresAction` | **Stripe 的 3DS 回调**，打 Stripe 主机 |
| `GetStripePaymentIntent` | **Stripe 的 PaymentIntent**，同上 |

### 与 R117 正好互补

| 店 | Stripe 在哪 |
|---|---|
| **Demandware** | 有 `CreateStripePaymentMethod` 步，但**镜像里没有 `Stripe-*` 控制器**（支付控制器全是 Adyen） |
| **John Lewis** | 有 `HandleRequiresAction` / `GetStripePaymentIntent` 两个步，**直接打 Stripe 主机**，所以没有 BFF 端点对应它们 |

两条加起来说明：**「Stripe 步骤」在两个店里都存在，但只有其中一个把 Stripe 放在自己的控制器族里 —— 而那个是零。**

### 另一侧的 3 个端点没人点

`v4/orderforms/deliveries/`（尾斜杠变体）、`v4/orderforms/deliveries/delivery-address`、
`v3/orderforms/payments/`。第一个是同一资源的两条字面量，后两个留给「地址独立提交」和
「v3 支付」两条支路 —— **有端点没步，说明还有分支没被我看到。**
'''

if "## John Lewis：17 步 ↔ 12 端点" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("john lewis map documented")
else:
    print("already present")
