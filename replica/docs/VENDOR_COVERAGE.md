# 风控厂商覆盖表（生成物 —— 不要手改）

由 `python tools/vendor_coverage.py` 生成。完成判据 (f) 的风控一半：
**原版清单从二进制取证 ↔ 复刻件运行时 `StoreFlow.SolveDetectedWallAsync` 真实求解接线核查**（R1382 修复了 R1296 删表后将 `missing` 强行置 0 的口径遮蔽）。

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

## 三、与复刻件运行时反爬分派（`StoreFlow.SolveDetectedWallAsync`）的对账

8 家站点风控中，运行时实际接通非空求解器：**1** 家；未接通或仅空回调占位：**7** 家：

| Vendor | State | Solver | Relayed |
|---|---|---|---|
| `Akamai` | `NotDispatched` | `None` | False |
| `BotDeflector` | `NotDispatched` | `None` | False |
| `Cloudflare` | `StubDefaultNull` | `CloudflareStrategyRunner.Default() (null callbacks)` | True |
| `DataDome` | `StubDefaultNull` | `InjectedDataDomeSensor.Default() (null callback)` | True |
| `Kasada` | `RuntimeWired` | `ChromiumKasadaSolver + HttpKasadaSolver` | False |
| `PerimeterX` | `NotDispatched` | `None` | False |
| `Queue-it` | `NotDispatched` | `None` | False |
| `Vercel` | `NotDispatched` | `None` | False |

### 原版点名而复刻件运行时未接通求解的站点风控（7）

| 缺的 | 命中 | 类别 | 处置 |
|---|---|---|---|
| **Akamai** | 3 | vendor | 运行时状态 `NotDispatched`（`None`）；原版有明确求解文案，复刻件运行时尚未接通可用求解器。 |
| **BotDeflector** | 2 | vendor | 运行时状态 `NotDispatched`（`None`）；原版有两条文案（`Solving BotDeflector icons` · `Solving BotDeflector proof of work`），所以它是**两种挑战**（图标点选 + PoW）。补行需要先定 `Solver`：镜像里没有第三方指向，但那不等于自建 —— R1029 的 `Relayed` 两轴就是为这种情形留的。 |
| **Cloudflare** | 12 | vendor | 运行时状态 `StubDefaultNull`（`CloudflareStrategyRunner.Default() (null callbacks)`）；原版有明确求解文案，复刻件运行时尚未接通可用求解器。 |
| **DataDome** | 1 | vendor | 运行时状态 `StubDefaultNull`（`InjectedDataDomeSensor.Default() (null callback)`）；原版有明确求解文案，复刻件运行时尚未接通可用求解器。 |
| **PerimeterX** | 1 | vendor | 运行时状态 `NotDispatched`（`None`）；原版有明确求解文案，复刻件运行时尚未接通可用求解器。 |
| **Queue-it** | 1 | vendor | 运行时状态 `NotDispatched`（`None`）；原版有明确求解文案，复刻件运行时尚未接通可用求解器。 |
| **Vercel** | 2 | vendor | 运行时状态 `NotDispatched`（`None`）；只有 `Solving Vercel` 一条，没有分期文案。补行的最小诚实形态是 `State.DetectedOnly` + `Solver.Unknown`，因为镜像只证明它被走到，不证明怎么解。 |

**→ 说明**：支付侧挑战（`Stripe challenge`、`PayPal 3DS`）归支付层单独核查；通用挑战名（`captcha`、`proof of work`、`checkpoint`）不按单厂商计缺口。

## 四、边界

- **有文案不等于有本地自建 solver**：文案说明原版走到那一步，而它交给第三方、自建还是内联，要按反编译证据核实。
- **没有文案不等于没处理**：Kasada 与 Queue-it 都已经证明这一点（形状不同）。
- **对照只能证明「查得到」**：前缀查询 > 0 不等于该厂商在所有站上都启用。
