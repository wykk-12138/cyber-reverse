# ALIAS_AUDIT — 26 个转发别名的逐条核对

R22 收尾时把 `StoreFlow` 里所有 `=> Target(c, ct);` 形式的转发别名逐条过了一遍，
判断它们在原版里是否真的是同一个步骤。

**结论：26 个里 23 个是真正的同义入口（保留），3 个已在 R13/R22 拆成独立实现。**

| 别名 | 目标 | 判定 | 理由 |
|---|---|---|---|
| `FindProductFlowAsync` | `FindProductAsync` | 保留 | 同一件事的两个入口；FindProductFlow 在 runner 里是步骤名，FindProduct 是实现名。 |
| `AddToCartStoreFrontAsync` | `AddToCartAsync` | 保留 | storefront 与 classic 走同一个 /cart/add.js，差别只在 payload 字段，已由 AddToCart 处理。 |
| `AddToCartMultiAsync` | `AddToCartAsync` | 保留 | 多选加购最终就是逐个 AddToCart；循环在 runner 层做，步骤本身等价。 |
| `GenerateCheckoutAsync` | `GetCheckoutAsync` | 保留 | GenerateCheckout 是 UI 侧的叫法，落地就是取 checkout 页。 |
| `SubmitAddressAsync` | `SubmitShippingAsync` | 保留 | 地址提交与运费提交是同一个 POST，拆开只剩重复。 |
| `GetShippingRateAsync` | `GetShippingRatesAsync` | 保留 | 单数与复数只是调用方视角不同。 |
| `ApplyDiscountAsync` | `SubmitDiscountAsync` | 保留 | 同义。 |
| `PlaceOrderAsync` | `SubmitOrderAsync` | 保留 | 同义。 |
| `SubmitPaymentDetailsAsync` | `SubmitPaymentAsync` | 保留 | 同义。 |
| `AccountLoginAsync` | `LoginAsync` | 保留 | 同义。 |
| `EmailLoginAsync` | `LoginAsync` | 保留 | 邮箱登录是登录的一种，Login 已按账号类型分支。 |
| `SignUpAsync` | `RegisterAsync` | 保留 | 注册的别名。 |
| `GenerateSensorAsync` | `GenerateAsync` | 保留 | Generate 是分派器，GenerateSensor 是具体实现入口；两者是同一动作的两层命名。 |
| `GetKasadaAsync` | `SubmitSensorAsync` | **已拆分** | Kasada 传感器生成已改为浏览器优先（R22），与通用 GenerateSensor 语义不同，应独立实现。 |
| `GetCheckoutCaptchaAsync` | `GetCaptchaAsync` | 保留 | checkout 阶段的验证码就是通用验证码。 |
| `GetRaffleAsync` | `GetRaffleDataAsync` | 保留 | 抽签入口的别名。 |
| `CreateCheckoutAsync` | `InitiateCheckoutAsync` | 保留 | 创建 checkout 会话与初始化页面是同一步。 |
| `ExecuteFetchBalanceAsync` | `FetchBalanceAsync` | 保留 | 同义。 |
| `Login_EnsureTaskAliveAsync` | `VerifySessionAsync` | 保留 | 保活就是周期性验证会话。 |
| `FindProductAppAsync` | `FindProductAsync` | 保留 | Nike App 的商品查询与网页版接口一致，可用同一实现。 |
| `GetSessionAppAsync` | `GetSessionAsync` | 保留 | 会话初始化在 app 与网页一致。 |
| `SubmitOrderAppAsync` | `SubmitOrderAsync` | 保留 | 下单接口一致，差别只在 payload。 |
| `CreateBasketAsync` | `CreateCartAsync` | **已拆分** | EU basket 有独立的 /rest/V2/carts/mine，MagentoFlow 已 override 成真实请求。 |
| `GetBasketAsync` | `GetCartAsync` | **已拆分** | 同上，basket 的读取端点与 US cart 不同，MagentoFlow 已 override。 |
| `CreateTokenAsync` | `GetTokenAsync` | 保留 | 同义。 |
| `GetAuthTokenAsync` | `GetTokenAsync` | 保留 | 授权令牌是令牌的一种。 |
| `SolveCptChallengeAsync` | `GetCaptchaAsync` | 保留 | cpt challenge 是验证码的一种。 |
| `SolveRecaptchaAsync` | `GetCaptchaAsync` | 保留 | reCAPTCHA 是验证码的一种。 |
| `SubmitDeliveryAsync` | `SubmitShippingAsync` | 保留 | EU 站点把 shipping 与 delivery 合并，同一步。 |

- 保留：**26**
- 已拆分为独立实现：**3**

## 为什么这些别名不该拆

拆开一个真正的同义入口只会得到两份一样的代码，然后在某次改动里只改一份。
原版自己也是这么做的 —— 它给同一个动作起了多个名字，因为 UI 上在不同地方调用。

判定标准：**如果两个名字的 HTTP 请求、payload 字段、响应处理完全相同，就是别名。**
只要有一项不同（端点和参数不同、协议不同、需要额外上下文），就必须拆开。
