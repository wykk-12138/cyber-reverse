import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## Demandware：12 步 ↔ 控制器（第 117 轮）—— 这一轮暴露的是**我的表不全**

| 步 | 控制器 |
|---|---|
| `AddToCart` | `Cart-AddProduct` |
| `InitiateCheckout` | `Checkout-Begin` |
| `GenerateCSRF` | `CSRF-Generate` |
| `GetCheckout` | `CheckoutServices-FetchOrderModel` |
| `SubmitBillingAddress` | **`CheckoutServices-SubmitBilling`**（R117 新发现） |
| `SubmitConsignment` | `CheckoutShippingServices-SubmitShipping` |
| `SubmitShippingOption` | **`CheckoutShippingServices-UpdateShippingMethod`**（R117 新发现） |
| `CreateOrder` | `CheckoutServices-PlaceOrder` |
| `SubmitPayment` | `CheckoutServices-SubmitPayment` |
| `ConfirmPayment` | **`CheckoutServices-PaymentAuthorization`**（R117 新发现） |

### 这一轮最重要的事：缺的三个不是二进制缺，是**我的表缺**

R94 我从字符串池的一个窗口里抄了 17 个控制器。拿 12 步去对，发现**三步没有对应的控制器**。
再往外搜，立刻找到 5 个新名字：

```
CheckoutServices-SubmitBilling          CheckoutShippingServices-UpdateShippingMethod
CheckoutServices-PaymentAuthorization   CheckoutServices-FetchOrderModel
CheckoutServices-SubmitCash             Adyen-Adyen3DS2 / Adyen-PaymentsDetails
```

**缺的是我抄的那一页，不是原版。**

> 这正是「步表当主参照」的价值：**它会在你的端点表不全的时候告诉你。**
> 反过来（只看端点表）永远不会发现缺口 —— 因为缺口看起来就是「没有这项」。

### 留空的 2 步

| 步 | 为什么留空 |
|---|---|
| `GetPaymentMethod` | 镜像里唯一的支付读取就是 `FetchOrderModel`，而它已经给了 `GetCheckout`；这一步是重读模型还是问别的，名字定不了 |
| `CreateStripePaymentMethod` | **镜像里没有任何 `Stripe-*` 控制器**。支付控制器全是 Adyen 的（`AdyenUpgrade-Authorize`、`Adyen-Adyen3DS2`、`Adyen-PaymentsDetails`、`AdyenComponents-Payment*`） |

第二条是一条独立结论：**这一步要么走通用提交带 Stripe 表单，要么原版自己这里就是缺口** ——
两种都比「我编一个 `Stripe-Components-Payment` 出来」诚实。
'''

if "## Demandware：12 步 ↔ 控制器" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("demandware map documented")
else:
    print("already present")
