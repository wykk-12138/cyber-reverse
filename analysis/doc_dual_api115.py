import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 步 → 主机：Scheels 的双 API 对照（第 115 轮）

R114 找到 Scheels 的移动 API，R115 补上第三个端点 `/v5/Order/`，
于是**步列表和主机**第一次能对起来了 —— 但**只能对着名字对**：

| 移动端（`mobile-api.scheels.com`） | 步 |
|---|---|
| `v5/auth/guest` | `StartAppFast`、`StartAppSafe` |
| `v5/products/` | `FindProductApp`、`AddToCartApp` |
| `v5/Order/` | `SubmitOrderApp` |

| Web hub（`apihub.scheels.com/frontastic/action/`） | 步 |
|---|---|
| `account/login` | `Login` |
| `product/getProduct` | `GetProduct` |
| `cart/addToCart` | `AddToCart` |
| `cart/checkout` | `Checkout` |
| `cart/completeDetailsCheckout` | `CompleteDetailsCheckout` |
| `cart/sendSignifydStepUpCode` | `SignifydStepUpCode` |
| `cart/completeSignifydStepUpCheckout` | `CompleteSignifydStepUp` |

### 这张表是什么、不是什么

**是**：名字层的对应关系 —— `FindProductApp` 与 `products/` 说的是同一个名词，
`SubmitOrderApp` 与 `Order/` 也是。这是**当前唯一可用的桥**，把「步」和「主机」连起来。

**不是**：抓包。**没有任何一次请求被观察过。** 所以代码里写的是
`DualApi.Evidence = "name correlation … no request capture …"`，
测试断言这句话必须留在那儿 —— **一旦有人把它当成结论，这条断言会红。**

> 这是本会话第一次把两类证据（步表 / 主机表）接起来，
> 也是第一次**在接起来的同时声明「这条线是猜的」**。
'''

if "## 步 → 主机：Scheels 的双 API 对照" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("dual-api section appended")
else:
    print("already present")
