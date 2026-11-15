import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## Demandware 双路不是「两条完整路径」（第 124 轮）

把 15 条双路步按「有没有端点」切开，得到三段 —— 而**切出来的形状本身就是结论**：

| 半边 | 步 | 端点 |
|---|---|---|
| **App 有端点** | `StartAppFast`、`StartAppSafe` | `/scapi/ShopperLogin/getAccessToken` |
| | `AddToCartApp` | `/scapi/ShopperBaskets/addItemToBasket` |
| **Dw 有端点** | `GetSessionDw`、`GetCartDw` | `Cart-Get` |
| | `AddToCartAppDw` | `Cart-AddProduct` |
| **App 无端点** | `ApplyDiscountApp`、`GetCheckoutApp`、`GetRatesApp`、`SubmitOrderApp` | **没有** |

### 关键事实：**SCAPI 族里没有下单端点**

镜像里的 SCAPI 只有六个 `ShopperBaskets` 调用（create / add / update ×4）和两个 `ShopperLogin` 调用。
**没有任何一个调用会创建订单。**

所以：

> **从 app 路开始的店，没法在 app 路上结束 —— 必须切回经典控制器去结账和下单。**

这正是「15 步里同时养着 App 和 Dw 两套词」所描述的形状。
也解释了那四个 `*App` 无名端点的步：它们是**店铺自己的端点**（app 调 storefront 代理），
所以 SCAPI 族里当然没有它们。

### 对 replica 的影响

`SubmitOrderAsync` 现在**只有经典路径** —— 这是对的，不是漏了。
要给 app 路接下单，就得发明 `/scapi/ShopperOrders/createOrder`，而镜像里没有这个东西。

`ScapiAppPathTests.ThereIsNoScapiOrdersEndpoint` 断言：
**SCAPI 族里任何一条都不含 "Order"**，而经典侧有 `PlaceOrder`。
'''

if "## Demandware 双路不是「两条完整路径」" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("dual-path split documented")
else:
    print("already present")
