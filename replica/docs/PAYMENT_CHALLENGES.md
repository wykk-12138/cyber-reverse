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

**→ R1078 反编译落地了阶段 1（两条路）**：目标是冻结字面量 **`https://www.paypal.com/graphql/`**（0x147097e78，send 步 `sub_14110D670` 以 `sub_1408B6310` 的 +24 槽 = **PUT** 发送）；头墙是 PayPal 自己的 web 客户端指纹 —— `x-app-name: checkoutuinodeweb_hermione`（0x146fc7338）、`x-paypal-internal-euat`、`paypal-client-metadata-id`、`sec-fetch-site/mode/dest = same-origin/cors/empty`、 `origin/referer = https://www.paypal.com`；Hosted 方言另带 `x-requested-with: fetch`、`x-locale: en_US`、 `x-country`、`priority: u=1, i` 且 x-app-name/referer 取自上下文。预算 30 秒（+236=30000），注册 white/StatusInfo 墙，状态分发 **200 → 成功续体，403 与 429 → 共享重试闭包**。状态文案按 ctx+144 布尔选 `Solving PayPal 3DS` 或 `Proccesing 3D Secure`（原版拼写保留）。

**→ 九个阶段的函数地图（每条一记反编译即可结案）**：(1) `sub_141102970`/`sub_141105A80`（已落地）；(2) `sub_141103410` + `sub_141107DA0` + `sub_141108170`；(2.1) `sub_141103800`；(3) `sub_141103BF0`/`sub_141105EF0`；(4) `sub_1411090C0`；(5) `sub_141109550`；(6) `sub_141109910`/`sub_141109CF0`；(7) `sub_14110A080`；(8) `sub_141106360`。

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
| `PayPal3DS` | `PayPalThreeDs.cs` · `WallSolving.cs` | 名字被引用 |
| `PayPalThreeDs` | `PayPalThreeDs.cs` | 名字被引用 |
| `StripeChallenge` | `StripeChallenge.cs` | 名字被引用 |
| `Submit3DS` | `PayPalThreeDs.cs` | 名字被引用 |
| `CreateStripePaymentMethod` | `DemandwareStepMap.cs` · `RetailFlows.cs` · `StoreFlow.cs` · `StoreFlowSteps.cs` | 名字被引用 |

**→ 「名字被引用」不等于「实现了」**：`PayPal3DS` 出现在 `WallSolving.cs`（风控侧），`CreateStripePaymentMethod` 出现在步骤映射表与 `RetailFlows`（flow 的步骤名）。两者都是**这个名字被提到**，不是支付挑战被执行 —— 与 R1042 那条「有文案不等于有 solver」同族。

**→ R1080：挑战确认步已解码落地**：`Solving Stripe challenge`（0x146e94270）唯一引用者 `sub_140BE31F0` 是**橙色墙** + hCaptcha 供词的确认机 —— 状态文案 `Submit billing`（0x146E9FFB8）、墙色 `orange`（0x1471099B0）、等待标签 `Waiting for captcha`（0x146F25E60）、失败文案 `Stripe challenge captcha failed` + UI 色 `#FB4961`（0x146E9F310/0x146A76FD0）；表单五字段：`challenge_response_token`（验证码令牌）、`challenge_response_ekey`=""（空串哨兵）、`client_secret`（ctx728）、`captcha_vendor_name`=`hcaptcha`（0x147045DF0）、`key`（ctx704，可发布密钥）→ **PUT `https://api.stripe.com`（0x147054DD8）+ ctx800 的逐单路径**（+24 槽）。已落地为 `Payments/StripeChallenge.cs` 并由 `StripeChallengeTests` 钉住。

**→ 而「六步流程」的名字（`SubmitOrderStripe` 等六条）仍只是名字**：它们的方法体尚未按 `chars_va - 12` 链解码；挑战确认是六步中第一块落地的可执行协议。

**→ R1078/R1080 后复刻件侧分半**：PayPal 阶段 1 + Stripe 挑战确认均已落地（`PayPalThreeDs.cs` / `StripeChallenge.cs`，判据 e 变异各配可杀锚）；PayPal 阶段 2–8 与 Stripe 六步的其余步骤体已定位、每条一记反编译即可结案。

## 六、边界

- **有方法名不等于有协议，但入口函数已可直接反编译**：`SubmitOrderStripe` 等名字只证明原版有这一步；在 NativeAOT 里取协议须按冻结字符串头 `obj_va = chars_va - 12` 查引用（`disp32_scan_any.py` → `site_to_func.py` → Hex-Rays + `names_at.py`）。已核实入口：`Solving PayPal 3DS`（`0x146e93fb4 - 12 = 0x146e93fa8`）→ `sub_141102970`（927 B）/ `sub_141105A80`（1,047 B）；`Solving Stripe challenge`（`0x146e9427c - 12 = 0x146e94270`）→ `sub_140BE31F0`（1,017 B）。
- **3DS 的真实分支取决于银行**：9 条分期是原版的**观察顺序**，不是所有卡都会走满。
- **这两个挑战不属于 `VendorWiring`**：那张表问的是「哪个站的风控在拦路」，而支付挑战是「付款这一步还要做什么」，两者不同类。
