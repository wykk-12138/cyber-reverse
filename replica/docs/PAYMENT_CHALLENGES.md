# 支付侧挑战（生成物 —— 不要手改）

由 `python tools/payment_challenges.py` 生成。 `VENDOR_COVERAGE.md` 把 7 个缺口分成厂商 / 支付挑战 / 通用挑战三类，其中**支付挑战归支付层**；而 `where_is` 显示这一层在本工作里**不存在**。

**→ 所以「归支付层」这句话是真的，同时也是一个没有被记下来的缺口。**

## 一、对照

| 对照串 | 命中 |
|---|---|
| `kpsdk` | **17** |

**→ 对照成立。**

## 二、PayPal 3DS 的阶段

**镜像里有 9 条分期文案：**

- `Solving PayPal 3DS (1)`
- `Solving PayPal 3DS (2)`
- `Solving PayPal 3DS (2.1)`
- `Solving PayPal 3DS (3)`
- `Solving PayPal 3DS (4)`
- `Solving PayPal 3DS (5)`
- `Solving PayPal 3DS (6)`
- `Solving PayPal 3DS (7)`
- `Solving PayPal 3DS (8)`

**→ 注意 `(2.1)`：那是阶段 2 之后的**子阶段**，所以**可观察阶段是 9 个而不是 8 个** —— R1048 把「9 条文案」读成「8 个阶段」，而多出来的那条正是 2.1。

## 三、3DS 状态机

镜像里有四个状态名：`Submit3DS` · `Process3DS` · `Waiting3DS` · `Complete3DS`。

**→ 那是一个 4 态机：提交 → 处理 → 等待 → 完成。** 而 PayPal 侧有两个 solver 体：`<SolvePayPal3DS>` 与 `<SolvePayPalHosted3DS>` —— **普通 3DS 与 Hosted 3DS 是两条路**，不是一条。

**→ R1078 反编译落地了阶段 1（两条路）**：目标是冻结字面量 **`https://www.paypal.com/graphql/`**（0x147097e78，send 步 `sub_14110D670` 以 `sub_1408B6310` 的 +24 槽 = **PUT** 发送）；头墙是 PayPal 自己的 web 客户端指纹 —— `x-app-name: checkoutuinodeweb_hermione`（0x146fc7338）、`x-paypal-internal-euat`、`paypal-client-metadata-id`、`sec-fetch-site/mode/dest = same-origin/cors/empty`、 `origin/referer = https://www.paypal.com`；Hosted 方言另带 `x-requested-with: fetch`、`x-locale: en_US`、 `x-country`、`priority: u=1, i` 且 x-app-name/referer 取自上下文。预算 30 秒（+236=30000），注册 white/StatusInfo 墙，状态分发 **200 → 成功续体，403 与 429 → 共享重试闭包**。状态文案按 ctx+144 布尔选 `Solving PayPal 3DS (1)` 或 `Proccesing 3D Secure`（原版拼写保留；R1081 更正：阶段 1 字面量带 `(1)` 后缀，此前文档速记把它丢了）。

**→ 九个阶段的构建器已全数解码（R1081/R1082）**：每阶段与阶段 1 **同一请求模板**（同头墙方言/同 30 秒预算/同 200→成功续体 + 403/429→共享重试分发），仅进度串、续体槽与载荷不同。标签对象与池清单逐一吻合：(1) `sub_141102970`/`sub_141105A80`（续体 a1[4]/a1[9]）；(2) `sub_141103410` + hosted 孪生 `sub_141107DA0`/`sub_141108170`（a1[7]，B 变体带 per-context origin/referer 覆写）；(2.1) `sub_141103800`（a1[8]）；(3) `sub_141103BF0`（全局闭包 qword_1472C7328+120）；(4) `sub_1411090C0`（a1+80）；(5) `sub_141109550`（a1+88）；(6) `sub_141109910`（a1[12]，origin/referer 按上下文拼接）；(7) `sub_14110A080`（a1+104）；(8) `sub_141106360`（a1[11]）。**阶段 4–8 走 hosted 方言**。

**→ R1083：载荷层也解了——graphql 操作是冻结字面量**（0x1470cc8cc..0x14712190c 的 threeDomainSecure 家族）：`ApproveOnboardPaymentMutation` · `CurrencyConversion` · `OnboardGuestMutation`（带 `is3DSecureRequired` 旗标）· `approveMemberPayment` ×2 · `PayWithQuery` · **`ResolveThreeDsContingency` ×2（解析操作：token/authId/referenceId/creditCardId/status/experiences 六变量）**。变体 B（0x1470dc9bc）由 **hosted solver `sub_141113680` 自己组装**——即 R1078 定位的 15,615 B / 11-case 状态机；变体 A（0x1470d7974）由普通 solver `sub_14110FDB0`（14,458 B）组装。九个可观察阶段 = 该机驱动 `ResolveThreeDsContingency` 的解析环。**剩余未知 = 每 case 的变量绑定**（哪个 case 设哪个 authId/referenceId/status）——两台 solver 的 case 体是下一探针。

**→ R1084：绑定源也定了位**——解析器变量从两路读入：**JSON 针**（冻结串 `"referenceId":"` 0x146a76254 ← 解析器 `sub_140940820`（335 B）/`sub_140D91B40`（308 B））与**挑战页 DOM**（选择器 `input[id='referenceId']` 0x1470a48dc ← `sub_14092F630`（557 B）——挑战页隐藏域，不只是响应 JSON）。响应键 `authId`（0x143446208）、`creditCardId`（0x146fd8f54）同为裸键字面量。剩余未知收窄为**每 case 用哪条源**——即两台 solver 的 switch case 体。

**→ R1085：hosted solver 的 case 体全链定型**（2,288 行伪代码已存 `analysis/_paypal_hosted_solver.c`，11 态机的状态槽 a1+88 逐级 0→8）。case 体常量解码出**第三组 3DS 操作名**：`GetThreeDsJwtQuery`（0x146DA0CF0）· `ThreeDsAuthenticateMutation`（0x146EEF8A0）· `ThreeDsLookUpMutation`（0x146EEF8F0）——加上 R1083 的 8 条，3DS graphql 面共 **11 个具名操作**。case 体还给出**挑战窗口**：尺寸 `_500_x_600`（0x146F5FF08）、页面 `https://www.paypal.com/checkoutweb/processThreedsConfirmation`（0x147097D08）、表单字段 **`JWT` + `MD`**（0x146DD3A08/0x146DF88D0，sub_14130CC50 表单编码）——银行挑战页的回帖字段。方言常量 `HERMES`（0x146DA8128）· `EXPRESS_CHECKOUT` · `PAYPAL` · `PRE_AUTH` · `en`。全链顺序：**JWT 查询 → 3DS 认证 → 挑战窗（processThreedsConfirmation 回帖 JWT/MD）→ 查找 → 解析**。

**→ R1086：四层全收口，机器可执行落地并接线**——`PayPalThreeDs` 现在是完整状态机：`GqlAsync`（持久化操作体 `{"operationName":N,"variables":{…}}`，PUT + 双方言头墙 + 200/403/429 分发）· `ReadContingency`（case 体针：status/redirectUrl/jwtSpecification/referenceId/paymentCard.id）· `RunAsync`（提交 → 读偶发 → JWT 查询 → 停在挑战窗 Waiting3DS，快照与续体字段入会话）· `ContinueAsync`（认证 → 查找 → `ResolveThreeDs-Contingency` 六变量解析，HERMES/EXPRESS_CHECKOUT 方言集）。**接线**：`PayPalGateway.CompleteActionAsync` 在 Waiting3DS 态驱动解析链——支付分发层到 3DS 机器的端到端执行链打通。同时 Nike 支付两步按反编译 `sub_140B35420` 落地（双 GET：`OrderV5/{order}/InitiatePayment?singleStep=true&deliveryCountryIso={country}` → eshopworld `PaymentMethods?paymentId=` → 令牌入会话 → checkout POST 的 paymentToken）。四态机名实相符：`StageIsDecoded` 对机器而非仅对标签表。

## 四、Stripe

| 名字 | 命中 | 首条地址 |
|---|---|---|
| `SubmitOrderStripe body` | **19** | `0x14337c40d` |
| `ProcessOrderStripe body` | **4** | `0x14337c6a2` |
| `GetStripePaymentIntent` | **6** | `0x14338389a` |
| `CreateStripePaymentMethod` | **13** | `0x14338377d` |
| `ValidateStripeIntent` | **1** | `0x143384be3` |
| `StripeFallbackHandler` | **1** | `0x143337a70` |
| `API version` | **2** | `0x143385e27` |

**→ 那是一条完整流程**：配置 → 支付意图 → 支付方法 → 提交 → 校验，外加一个 `StripeFallbackHandler` 与一个 API 版本常量（`2025-08-27.basil`）。

## 五、复刻件侧

| 标记 | 复刻件里出现在 | 性质 |
|---|---|---|
| `PayPal3DS` | `Gateways.cs` · `WallSolving.cs` | 名字被引用 |
| `PayPalThreeDs` | `StoreFlow.cs` · `StoreFlowRunner.cs` · `Gateways.cs` · `PayPalThreeDs.cs` | 名字被引用 |
| `StripeChallenge` | `Gateways.cs` · `StripeChallenge.cs` | 名字被引用 |
| `Submit3DS` | `PayPalThreeDs.cs` | 名字被引用 |
| `CreateStripePaymentMethod` | `DemandwareStepMap.cs` · `RetailFlows.cs` · `StoreFlow.cs` · `StoreFlowSteps.cs` | 名字被引用 |

**→ 「名字被引用」不等于「实现了」**：`PayPal3DS` 出现在 `WallSolving.cs`（风控侧），`CreateStripePaymentMethod` 出现在步骤映射表与 `RetailFlows`（flow 的步骤名）。两者都是**这个名字被提到**，不是支付挑战被执行 —— 与 R1042 那条「有文案不等于有 solver」同族。

**→ R1080：挑战确认步已解码落地**：`Solving Stripe challenge`（0x146e94270）唯一引用者 `sub_140BE31F0` 是**橙色墙** + hCaptcha 供词的确认机 —— 状态文案 `Submit billing`（0x146E9FFB8）、墙色 `orange`（0x1471099B0）、等待标签 `Waiting for captcha`（0x146F25E60）、失败文案 `Stripe challenge captcha failed` + UI 色 `#FB4961`（0x146E9F310/0x146A76FD0）；表单五字段：`challenge_response_token`（验证码令牌）、`challenge_response_ekey`=""（空串哨兵）、`client_secret`（ctx728）、`captcha_vendor_name`=`hcaptcha`（0x147045DF0）、`key`（ctx704，可发布密钥）→ **PUT `https://api.stripe.com`（0x147054DD8）+ ctx800 的逐单路径**（+24 槽）。已落地为 `Payments/StripeChallenge.cs` 并由 `StripeChallengeTests` 钉住。

**→ R1214–R1231：「六步流程」不再只是名字**。名字与序号来自状态机名表（`<CreateStripePaymentMethod>d__89` 一类，ASCII 长度前缀表，不是 UTF-16 冻结串），而六个步骤**承载的协议**已按 `chars_va - 12` 链解出并落地在 `Payments/Gateways.cs`：

| 表面 | 函数 | 已落地 |
| --- | --- | --- |
| payment_methods 表单 | `sub_140BDA320` | `StripeGateway.TokenizeAsync`（`Gateways.cs:504`），API 版本 `2025-01-27.acacia` |
| payment_methods 挑战面 | `sub_140959320` | 同一函数的 basil 面，`2025-08-27.basil` |
| setup_intent confirm | `sub_140BE0F80` | `SetupConfirmUrl` / `SetupConfirmForm`（`payment_method_data[*]` 族） |
| setup_intent retrieve | `sub_141145DB0` | `SetupIntentRetrieveUrl`（`&_stripe_account=` 即使为空也追加） |
| payment_intents retrieve（JL 变体） | `sub_1411458f0` | `is_stripe_sdk=true`、无版本片段（`MagentoFlow`） |
| payment_intents retrieve | `sub_140A40170` | `PaymentIntentRetrieveUrl`，`is_stripe_sdk=false` + `2025-09-30.clover` |
| payment_intents confirm（PayPal 钱包） | `sub_140B58D60` | `PayPalConfirmForm`，含 `mandate_data[*]` 两键与 `return_url` |

**→ 三条 Stripe API 版本在同一张串池里相邻**（`0x146ADFBE0` / `…C60` / `…C98`），测试断言三者互不相等，防止被「统一」。**三条不同的 UA 同理**（`20e04cd437` / `035decdc6c` / `d6356e1526`）。

**→ 仍旧 Unknown 的是「哪一步调用哪条表面」，不是协议本身**：四个构建器经 delegate/虚表间接派发到达，其 thunk 与存放槽（`0x147228EF8` / `0x1472279C8`）自身 `xrefs_to` 均为 **0** —— 静态 xref 走不通（R1219/R1222 两层实测）。剩余路径只有解析 NativeAOT 元数据表，或跑实机观察（需原版有效登录）。

## 六、边界

- **有方法名不等于有协议，但入口函数已可直接反编译**：`SubmitOrderStripe` 等名字只证明原版有这一步；在 NativeAOT 里取协议须按冻结字符串头 `obj_va = chars_va - 12` 查引用（`disp32_scan_any.py` → `site_to_func.py` → Hex-Rays + `names_at.py`）。已核实入口：`Solving PayPal 3DS`（`0x146e93fb4 - 12 = 0x146e93fa8`）→ `sub_141102970`（927 B）/ `sub_141105A80`（1,047 B）；`Solving Stripe challenge`（`0x146e9427c - 12 = 0x146e94270`）→ `sub_140BE31F0`（1,017 B）。
- **3DS 的真实分支取决于银行**：9 条分期是原版的**观察顺序**，不是所有卡都会走满。
- **这两个挑战不属于 `VendorWiring`**：那张表问的是「哪个站的风控在拦路」，而支付挑战是「付款这一步还要做什么」，两者不同类。
