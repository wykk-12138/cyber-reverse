# 进度与差距（Phase 1 收口更新 · 接续 R1300，2026-11-20）

> **动态度量唯一事实源**：`docs/METRICS.md`（在 `replica/` 下由 `python tools/metrics_report.py` 生成；本文活区不硬编码易漂移的全量数值）。
> **模块普查与差距依据**：`docs/MODULE_FUNCTION_CENSUS.md`、`docs/DESCRIPTOR_TRIAGE.md`、`docs/SHAPE_GAPS.md`、`docs/DATAFILES.md`。
> 判据 a–f 的逐条结构性证明在 `docs/GOAL_VERIFICATION.md`；本文只回答：**Phase 1 已结案面**、**原版 vs 复刻件的模块差距真相**、以及 **Phase 2 核心模块复刻待办队列**。

---

## 一、一句话结论

1. **R1300 列出的 8 项本机可做差距已全部收口**（含第 1 项 137 条描述符归类与本地化行为、第 2 项模块级函数分布与类型/方法普查、以及原本归为外部阻塞的 `BotTask.Running`/`BotTask.Task` 静态定型）。
2. **`docs/MODULE_FUNCTION_CENSUS.md` 实证了剩余真正的核心业务缺口**：`.pdata` 比率不能直接当功能完成度（双方 BCL/三方库组成与内存布局不同），但原版 `Cybersole.Stores`、`Cybersole.Services.Mail`（当前在复刻件为被 AOT 整块裁掉的零调用死岛）、`Cybersole.Http` 伴生包存在明确可静态还原、可在本机工程化落地的运行时模块 → 列入 **Phase 2 核心复刻队列**（Waves 2A–2D）。

---

## 二、已结案度量面与可复算入口

> 最新实测值以 `docs/METRICS.md` 当次生成快照为准。

| 面 | 口径与来源 | 复算命令 |
|---|---|---|
| 站点流程 | 见 `docs/METRICS.md`（`CORE_COVERAGE.md`：`unknown placeholders 0`、`provenance exit 0`） | `python tools/core_coverage.py` |
| 支付挑战 | `PAYMENT_CHALLENGES.md`（PayPal 3DS 九阶段 + Stripe 六端点与挑战 + 静态派发映射） | `python tools/payment_challenges.py` |
| captcha（识别面） | 四家 loader 字面量实证并接入 `StoreFlow.DetectAsync` | `python tools/captcha_coverage.py` |
| 风控厂商 | `controls ok True`、IDA 字符串缓存完整后 13 项全部命中（含 `Solving POW challange` / `Solving checkpoint`） | `python tools/vendor_coverage.py` |
| 名字 / 类型绑定缺口 | 见 `docs/METRICS.md`（`bind_diff.py` / `bind_scope.py`，`real gap 0`、`scope misses 0`、`unclassified 0`） | `python tools/bind_scope.py`、`python tools/bind_diff.py --buckets`、`python tools/bind_diff.py --type-presence` |
| 文案 | 见 `docs/METRICS.md`（19 区无缺） | `python tools/copy_audit_report.py` |
| 数据文件名 | `original-on-disk not in replica 0`；内嵌资源与只读兜底已区分（`docs/DATAFILES.md`） | `python tools/datafiles_diff.py` |
| 传输层与 HTTP/3 | `NetClient` 默认路径对齐原版 `SocketsHttpHandler`/`SslStream`，并补齐 30s/90s 超时与 `TlsProfile.Chrome150` | 见下 §三 ③ 与 `replica/src/Cybersole.Http/NetClient.cs` |
| 套件与变异 | 全量非慢速套件与 `mutation-check.py` 最新结果见 `docs/METRICS.md` | `python tools/metrics_report.py`、`python tools/mutation-check.py` |

---

## 三、核心模块逐项状态

图例：**✅ Phase 1 已结案** · **🟡 列入 Phase 2 核心复刻** · **⛔ 外部阻塞** · **🚫 范围外（禁止实现）**

### ① 站点与结账流程（`Cybersole.Stores/Flows`）

| 项 | 状态 | 结论与下一步 |
|---|---|---|
| 已接入流程骨架与 62 店映射 | ✅ | 18 Flow / override steps、占位零、provenance exit 0；`AddressModels` 已纳入 `DemandwareFlow` |
| `CheckPriceLimitApp` / `FindProductCDN` / `CheckFanRewardState` / `SignUpFanRewards` | 🟡 | `docs/MODULE_FUNCTION_CENSUS.md` 在基线异步方法清单检出原版独有步骤（如 `0x143373f5f`、`0x1433a0f23`）；**Phase 2 Wave 2C** 用 IDA 反编译核对，仅在获知确切端点与载荷后落地 |
| per-store 差异（23 条 0 命中 `inferred`） | ⛔ | R1266 证实 NativeAOT 部分字面量逐字节不可搜；静态归 `unknown`，待 live capture |
| Farfetch 7 条与 `connect/app` payload | ⛔ | `connect/app` 属服务端下发配置，需原版有效登录凭据与实机抓包（R1077 / R1294） |

### ② 支付与客户端校验层（`Cybersole.Stores/Payments` & Scripts）

| 项 | 状态 | 结论与下一步 |
|---|---|---|
| PayPal 3DS 九阶段 + Stripe 六端点与挑战 | ✅ | `PayPalThreeDs.cs`、`StripeChallenge.cs`、`Gateways.cs`（含 SetupIntent/PaymentIntent 检索与确认路径） |
| Stripe 构建器派发关系（原 Gap #5） | ✅ | Phase 1 静态证毕：`0x147228EF8`/`0x1472279C8` 为 `AsyncStateMachineBox` 冻结 `ContextCallback` 字段而非派发表；通过 `AsyncTaskMethodBuilder.Start` 映射 8 个构建器至 Casio / John Lewis / Highsnobiety / PopMart / Above The Clouds / HBX / Sportsshoes / Shopify（已更新 `Gateways.cs`） |
| `UnzerGateway`（`ContinueUnzerThreeDs`） / `CardinalInit` / `api.checkout.com` | 🟡 | `docs/MODULE_FUNCTION_CENSUS.md` 实证 `UnzerGateway.CompleteActionAsync` 仍为占位桩，且缺少 `CardinalInit`/`CardinalContinue`（`0x14338294f`）与 `Checkout.com`（`0x1470530bc`）网关机；**Phase 2 Wave 2B** 重点反编译落地 |
| captcha 识别面（被动分类） | ✅ | 四家 loader 字面量 + `CaptchaSurface.Classify` 接入 `DetectAsync` |
| 反爬传感器伪造与验证码绕过执行面 | 🚫 | `GetSbsdHash` / `GetSbsdScript`、`DdMobileTouchEvent` / `SensorPow`、`ExecuteClipModelAsync` / `SolveImageInCloudAsync` / `ClickCellsAsync` / `MoveMouseAndClickWithoutTrajectoryAsync`、以及 `HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 绕过执行均属严格 **Out of Scope**，严禁复现 |

### ③ 传输层与可观测性伴生包（`Cybersole.Http`）

| 项 | 状态 | 结论与下一步 |
|---|---|---|
| 默认路径 / HTTP/3 与超时参数（原 Gap #6） | ✅ | Phase 1 IDA 静态实证：原版 BCL `SocketsHttpHandler.Http3Support` 编译期固定为 `"false"`（`0x144b19cb8`），`System.Net.Quic`/`msquic` 缺失；门店流量走自定义 Go 移植栈 `Cybersole.Http`（`0x144BDE5D0`），默认 `chrome_131` 关闭 H3，仅 ASICS 切用 `chrome_150` 开启 `ProtocolRacing`。复刻件 `NetClient` 已对齐连接 30s / 空闲 90s 超时并增加 `TlsProfile.Chrome150` |
| `OwnTls` 定位收口（原 Gap #7） | ✅ | 已在 `NetClient.cs` 与 `BouncyTls.cs` 显式区分 `IsProductionTransport` 与 `IsExperimentalTransport`（TLS 1.2 实验栈） |
| `Cybersole.Http.{Newtonsoft,Analytics,Debug}` 能力 | 🟡 | 原版含 `IBody`/`LegacyJsonBody`/`LegacyJarrayBody`、`ClickHouseSink`（`FlushOnceAsync`/`DrainLocalQueueAsync`）本地队列落盘重发、`Cybersole.Http.Debug` 调试捕获流及 `RootCertificates.bin`；**Phase 2 Wave 2D** 反编译对齐 |

### ④ 服务与业务模型 / 冻结 UI 面（`Cybersole.Services` & `Cybersole.Core` / `Ui`）

| 项 | 状态 | 结论与下一步 |
|---|---|---|
| `Cybersole.Services.Mail`（`ImapMailProvider` / `AycdInboxClient`） | 🟡 | Phase 1 PDB 普查发现致命死岛：类与单测虽在 `Cybersole.Services`，但 `AppServices` / `TaskEngine` / `StoreFlow` 无任何真实调用，`MailKit`/`MimeKit` 在 AOT 产物中 **0 函数被保留**；**Phase 2 Wave 2A** 对照 `WaitImapAsync`（`0x14336b99e`）接入主链与设置页验证动作 |
| `BotTask.Running` / `BotTask.Task`（原外部阻塞 #4） | ✅ | **Phase 1 已静态突破**：`BotTask.Running`（`0x14080E0F0`）确认为 `bool`（非 `int`）并联动 `TaskGroup.Running` 增减与 `PropertyChanged`，已落地并测试；`BotTask.Task`（`0x14080CA20`）确认为 `TaskBase`/`StoreModuleBase`（MT `0x144C963C8`，69 个子类），结构差异已在 `Tasks.cs` 与 `SHAPE_GAPS.md` 阐明 |
| `only in descriptors`（原本机 #1） | ✅ | `analysis/triage_only_in_descriptors.py` → `docs/DESCRIPTOR_TRIAGE.md` 全量归类（0 未分类），`Cybersole.Ui.Localization` 5 项扩展行为已在 `LocalizationService` / `LocalizeHelpers` 实现并接线 |
| `shape mismatches`（原本机 #3） | ✅（核心收口） | `SmartAction.Logs` 与 `BotTask.Running`（core 3 中可做 2 项）及 unambiguous `prop-get`/`Link` 均已修补；`analysis/shape_gaps_report.py --baseline` 对齐 `METRICS.md` 并更新 `docs/SHAPE_GAPS.md`；仅余 UI 需选择模型方法与 `BotTask.Task` 结构分层 |
| `datafiles: replica-only`（原本机 #4） | ✅ | `tools/datafiles_diff.py` 自动从 `*.csproj` 排除 `<EmbeddedResource>`（`Cybersole.ProfileValidation.en.json`），并区分只读兜底候选 `license.json`（R702）与 `written-by-replica-only: 0` |
| 云同步 / 嵌入式浏览器 / 登录授权 | ⛔ / 🚫 | `DotNetBrowser`（商业库）、`SignalR` `/connect/app`、`MSAL`、`RabbitMQ`、`Velopack` 远端更新归 **External Blocked**；`AuthWindow`/`LicenseControl` 维持 **R702 Out of Scope** |

---

## 四、Phase 1 差距清单核销总账

### 原 R1300「本机可做 8 项」→ 8/8 已结案

| # | 原待办 | Phase 1 结案状态 | 证据 / 产出 |
|---|---|---|---|
| 1 | 137 条 `only-in-descriptors` 逐条分类 | ✅ 已结案 | `analysis/triage_only_in_descriptors.py` → `docs/DESCRIPTOR_TRIAGE.md` + `LocalizationService`/`LocalizeHelpers` + 单测 |
| 2 | 函数分布按模块对照 | ✅ 已结案 | `analysis/module_function_census.py` → `docs/MODULE_FUNCTION_CENSUS.md`（复刻 100% PDB 归因 + 原版 321,244 函数多信号归因） |
| 3 | `shape mismatches`（core 优先） | ✅ 已结案 | `SmartAction.Logs`、`BotTask.Running` (`bool`)、`FilterRow`/`ProfileGroupView`/`TaskGroupView.Link` + `analysis/shape_gaps_report.py --baseline` |
| 4 | `datafiles: replica-only` | ✅ 已结案 | `replica/tools/datafiles_diff.py` 排除 csproj 内嵌资源并分离只读候选 → `docs/DATAFILES.md` |
| 5 | Stripe 四构建器派发关系 | ✅ 已结案 | `AsyncStateMachineBox` 静态定性与 `AsyncTaskMethodBuilder.Start` 全 8 条店铺级映射（`Gateways.cs`） |
| 6 | HTTP/3 是否真启用 | ✅ 已结案 | BCL `Http3Support="false"` 实证 + Go `Cybersole.Http` `chrome_131`/`chrome_150` ASICS H3 分支核实 + `NetClient`/`TlsProfile` 对齐 |
| 7 | `OwnTls` 定位写清 | ✅ 已结案 | `NetClient.cs` / `BouncyTls.cs` 显式标注并暴露生产/实验传输区分与退避计数测试 |
| 8 | `vendor named 11` 复核 | ✅ 已结案 | IDA 串缓存完备（324,901）下验证 `Solving POW challange` / `Solving checkpoint`，`vendor_coverage.py` 全量命中 |

### 剩余外部阻塞项（已从 5 项收窄为 4 项）

| # | 阻塞项 | 所缺外部条件 |
|---|---|---|
| 1 | Farfetch 7 条与 `connect/app` payload + 云端 `Remote*`/SignalR 同步 | 原版有效登录凭据 |
| 2 | 23 条 `inferred` 的 0 命中 | live capture（真实请求/响应） |
| 3 | 嵌入式浏览器与 `DotNetBrowser` / captcha 执行面 | 商业授权 `DotNetBrowser` 与外部 Chromium；且主动绕过属范围外 |
| 4 | `docs/PARITY_CLAIMS.md` 其余静态不可知 `unknown` | 逐条见 `PARITY_CLAIMS.md` 的 `gap_reason` 列（原 `BotTask.Running`/`BotTask.Task` 已移出至 Phase 1 ✅ 结案） |

---

## 五、Phase 2 核心模块复刻队列（按高确定性优先）

1. **Wave 2A — 邮箱/验证码服务接线（`Cybersole.Services.Mail` + `AppServices` + `TaskEngine` + `FlowContext`）**：基于 `WaitImapAsync`（`0x14336b99e`）与 `AycdInboxClient` 反编译结果，建立 `IMailCodeService`/`MailCodeService` 并接通运行时与设置校验动作，消除 `MailKit`/`MimeKit` 被 AOT 裁空问题。
2. **Wave 2B — 支付网关与 3DS 状态机补齐（`Cybersole.Stores/Payments`）**：反编译并落地 `UnzerGateway`（`ContinueUnzerThreeDs` @ `0x143383aa9`）、`CardinalThreeDs`（`CardinalInit` @ `0x14338294f`）及 `CheckoutComGateway`（`api.checkout.com` @ `0x1470530bc`）。
3. **Wave 2C — 商店流程剩余可证步骤（`Cybersole.Stores/Flows`）**：反编译 `CheckPriceLimitApp`（`0x143373f5f`）、`FindProductCDN`（`0x1433a0f23`）与 `CheckFanRewardState`/`SignUpFanRewards`，仅对获得精确端点与载荷证据的模块落地可执行实现。
4. **Wave 2D — `Cybersole.Http` 伴生能力（`Cybersole.Http`）**：反编译并对齐 `IBody`/`LegacyJsonBody`/`LegacyJarrayBody`、`HttpAnalytics` 本地队列溢出落盘与 `DrainLocalQueueAsync`、以及 `HttpDebug` 捕获流 / 证书集合。
5. **严格排除**：一切反爬传感器伪造/绕过（`GetSbsdHash`、`DdMobileTouchEvent`/`SensorPow`）与验证码自动求解执行（`ExecuteClipModelAsync`/`ClickCellsAsync`）及 R702 授权模块，绝不进入 Phase 2 实现清单。
