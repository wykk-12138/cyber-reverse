import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\NIKE_PARITY.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 12. Nike endpoint 词汇表（第 87 轮，IDA 直接读出）

IDA 重新载入数据库后跑一次：

```
find_regex "api\\.nike\\.com"      →  20 条
```

**这 20 条就是二进制能调的全部 Nike base URL。** 已固化成
`Cybersole.Stores.Flows.NikeEndpoints`（19 个常量，产品流的 query 拼在字面量里），
并有 `NikeEndpointTests` 钉住——将来谁想「发明」第 21 个端点，测试会红。

| 家族 | URL |
|---|---|
| 结账预览 | `buy/checkout_previews/v3/` ＋ `_jobs/v3/` |
| 结账 | `buy/checkouts/v3/` ＋ `_jobs/v3/` |
| 运费报价 | `buy/fulfillment_offerings_jobs/v2/`（只有 jobs） |
| 预购购物车 | `buy/partner_cart_preorder/v2/` ＋ `_jobs/v2/` |
| 库存 | `deliver/available_gtins/v3` |
| 3DS | `payment/3ds_authentications/v3`、`payment/3ds_results/v3` |
| 延后付款 | `payment/deferred_payment_forms/v1` ＋ `/jobs/` |
| PayPal | `payment/paypal_details/v2`（＋jobs）、`payment/paypal_mark/v2`（＋jobs） |
| 支付预览 | `payment/preview/v3` ＋ `/jobs/` |
| 产品流 | `product_feed/threads/v2?fields=` |

### 对 replica 的直接结论

原版**没有** `buy/carts/v2/…`，也**没有** `buy/orders/v2/…` —— 而 replica 的 `NikeFlow`
正在用这两个家族：

| replica 现在 | 二进制里 |
|---|---|
| `buy/carts/v2/{CC}/Nike/SNKRS?format=simplified` | **不存在** |
| `buy/orders/v2/US/{id}/delivery` | **不存在** |
| `buy/orders/v2/US/{id}/initiatePayment` | **不存在** |
| `buy/orders/v2/US/{id}/payment` | **不存在** |
| `buy/orders/v2/US/{id}/submit` | **不存在** |

真正的形状是：**一个 `buy/checkouts/v3/{checkoutId}` 资源，14 步依次往它上面写**，
每一步的具体子路径由代码拼接（数据库里没有把它们作为独立字面量），
所以「哪一步写哪个子路径」**仍然没有证据**，`NIKE_PARITY.md` 第 11 节那张缺口表继续有效。

**这一步做的是把「不存在的东西」证实为不存在**，而不是把猜测换成另一个猜测。
'''

if "## 12. Nike endpoint" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("NIKE_PARITY section 12 appended")
else:
    print("already present")
