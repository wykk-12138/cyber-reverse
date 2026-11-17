# 风控厂商覆盖表（生成物 —— 不要手改）

由 `python tools/vendor_coverage.py` 生成。完成判据 (f) 的风控一半：
**原版清单从二进制取证 ↔ `VendorWiring` 逐条对**。

## 一、对照是否成立

| 对照串 | 命中 |
|---|---|
| `kpsdk` | **17** |
| `datadome` | **15** |

**→ 对照成立，下方的零可读。**

## 二、原版在进度文案里点名的求解对象

**取证依据**：原版对用户显示 `Solving <X>` 形式的进度文案，那是**它自己写的**清单，而不是我们的分类。

| 厂商/挑战 | 命中 | 首条地址 |
|---|---|---|
| **Akamai** | **3** | `0x146e93ae4` |
| **BotDeflector** | **2** | `0x146e93b9c` |
| **Cloudflare** | **12** | `0x146d8a35c` |
| **DataDome** | **1** | `0x146e93f34` |
| **Kasada** | **17** | `0x146a86504` |
| **PerimeterX** | **1** | `0x146e9423c` |
| **Queue-it** | **1** | `0x146d0d1b4` |
| **Vercel** | **2** | `0x146d8aa2c` |
| **Stripe challenge** | **1** | `0x146e9427c` |
| **PayPal 3DS** | **9** | `0x146e93fb4` |
| **captcha** | **1** | `0x146e94334` |
| **proof of work** | **1** | `0x146e93f74` |
| **checkpoint** | **1** | `0x146e94464` |

**注意形状差异**（AGENTS §2.7）：Kasada 从不以 `Solving` 出现 —— 它只在 `x-kpsdk-*` 头里；
Queue-it 只在 `Error Solving Queue-it (Softblock)` 这一条错误文案里。
**所以「用同一个前缀扫全体」会漏掉两家**，这也是每个厂商单独一条查询的原因。

## 三、与 `VendorWiring` 的对账

`VendorWiring` 现有 **9** 行：

| Vendor | State | Solver | Relayed |
|---|---|---|---|
| `cloudflare` | `Wired` | `UserThirdParty` | True |
| `kasada` | `Wired` | `Unknown` | False |
| `akamai` | `DetectedOnly` | `Unknown` | False |
| `imperva` | `DetectedOnly` | `None` | False |
| `datadome` | `Wired` | `SelfHosted` | True |
| `perimeterx` | `DetectedOnly` | `Local` | False |
| `queue-it` | `DetectedOnly` | `Local` | False |
| `botdeflector` | `DetectedOnly` | `Local` | False |
| `vercel` | `DetectedOnly` | `Local` | False |

### 原版点名而台账里没有的（5）

| 缺的 | 命中 | 类别 | 处置 |
|---|---|---|---|
| **Stripe challenge** | 1 | payment | 支付侧挑战，不是站点风控。`VendorWiring` 是站点风控台账 ⇒ **不该进这张表**；它属于支付层（`AdyenGateway` 那一族），要在那里记。 |
| **PayPal 3DS** | 9 | payment | 九条分期文案（`(1)`…`(8)` 加无条件），是 3DS 流程的阶段，同样**不属于站点风控台账**。→ 归支付层。分期数本身是有用证据：3DS 有 8 个可观察阶段。 |
| **captcha** | 1 | challenge | 通用验证码挑战，不是某个厂商 ⇒ 台账形状不建模，且不该建模。 |
| **proof of work** | 1 | challenge | 通用 PoW 挑战，同上。注意镜像原文拼作 `challange` —— 保留拼写，不修正。 |
| **checkpoint** | 1 | challenge | 通用检查点，同上。 |

**→ 分成两类，而这是完成判据 (f) 要的「未覆盖的每条写为什么」：**

- **真厂商缺口 0 个**（无）：`VendorWiring` 应该补行。
- **不属于这张表的 5 个**（`Stripe challenge` · `PayPal 3DS` · `captcha` · `proof of work` · `checkpoint`）：它们不是站点风控厂商 —— 支付挑战归支付层，通用挑战类型是 `VendorWiring` 的形状不该建模的东西。

**→ 这些是 `VendorWiring` 的缺口**：原版对它们有进度文案，说明原版确实走到那一步，
而台账没有对应的行 ⇒ 按 (f)「未覆盖的每条写为什么」。

## 四、边界

- **有文案不等于有 solver**：文案说明原版走到那一步，而它交给第三方、自建还是内联，要另找证据（`VendorWiring.Solver` 那一列就是在记这件事）。
- **没有文案不等于没处理**：Kasada 与 Queue-it 都已经证明这一点（形状不同）。
- **对照只能证明「查得到」**：前缀查询 > 0 不等于该厂商在所有站上都启用。
