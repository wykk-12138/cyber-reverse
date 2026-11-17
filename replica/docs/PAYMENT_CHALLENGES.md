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
| `PayPal3DS` | `WallSolving.cs` | 名字被引用 |
| `StripeChallenge` | **（无）** | **完全缺失** |
| `Submit3DS` | **（无）** | **完全缺失** |
| `CreateStripePaymentMethod` | `DemandwareStepMap.cs` · `RetailFlows.cs` · `StoreFlow.cs` · `StoreFlowSteps.cs` | 名字被引用 |

**→ 「名字被引用」不等于「实现了」**：`PayPal3DS` 出现在 `WallSolving.cs`（风控侧），`CreateStripePaymentMethod` 出现在步骤映射表与 `RetailFlows`（flow 的步骤名）。两者都是**这个名字被提到**，不是支付挑战被执行 —— 与 R1042 那条「有文案不等于有 solver」同族。

**→ 所以这两个缺口「为什么未覆盖」的答案是**：镜像把两条支付挑战写全了（9 条分期、4 态机、两个 PayPal solver、Stripe 六步），而本工作里**没有一处实现它们**：`StripeChallenge` 与 `Submit3DS` 连名字都没有，另两个只在别处被引用。

## 六、边界

- **有方法名不等于有协议**：`SubmitOrderStripe` 证明原版有这一步，不证明它发什么。要协议得反编译那几个体，而那是下一步。
- **3DS 的真实分支取决于银行**：9 条分期是原版的**观察顺序**，不是所有卡都会走满。
- **这两个挑战不属于 `VendorWiring`**：那张表问的是「哪个站的风控在拦路」，而支付挑战是「付款这一步还要做什么」，两者不同类。
