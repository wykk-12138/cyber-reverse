# 进度与差距（Phase 2 收口更新 · 接续 R1300，2026-11-20）

> **动态度量唯一事实源**：`docs/METRICS.md`（在 `replica/` 下由 `python tools/metrics_report.py` 生成；本文活区不硬编码易漂移的全量数值）。
> **模块普查与差距依据**：`docs/MODULE_FUNCTION_CENSUS.md`、`docs/DESCRIPTOR_TRIAGE.md`、`docs/SHAPE_GAPS.md`、`docs/DATAFILES.md`。
> 判据 a–f 的逐条结构性证明在 `docs/GOAL_VERIFICATION.md`；本文回答：**Phase 1 + Phase 2 已结案面**、**诚实 Unknown 边界**、以及**仅剩外部阻塞 / 范围外项**。

---

## 一、一句话结论

1. **R1300 列出的 8 项本机可做差距已全部收口**（Phase 1：137 条描述符全量归类与本地化行为、模块级函数分布与类型/方法普查、核心成员形状、数据文件名对照、Stripe 构建器静态映射、HTTP/3 与超时核实、`OwnTls` 定位、`vendor_coverage.py` 全量复核，以及原归为外部阻塞的 `BotTask.Running`/`BotTask.Task` 静态定型）。
2. **`docs/MODULE_FUNCTION_CENSUS.md` 检出的四大类本机可做核心模块缺口已于 Phase 2（Waves 2A–2D）全部反编译落地并接通运行时**：
   - **Wave 2A**（`Cybersole.Services.Mail` + `AppServices` + `TaskEngine` + `Settings`）：并发 `Task.WhenAny` 调度 `ImapMailProvider` + `AycdInboxClient` 消除被 AOT 整块裁空的死岛；
   - **Wave 2B**（`Cybersole.Stores/Payments`）：`UnzerGateway`（`ContinueUnzerThreeDs`）、`CardinalThreeDs`（`CardinalInit`/`Continue`/`DeviceFingerprint`/`StepUp`）、`CheckoutComGateway`（`api.checkout.com` 四路径 + 接入默认网关表）及 `Komoju`/`WebCVS`/`ToysRUs_JP` 便利店结算；
   - **Wave 2C**（`Cybersole.Stores/Flows`）：Shopify `CheckPriceLimitAppAsync` 与 `FindProductCdnAsync`、Funko `CheckFanRewardState` / `SignUpFanRewards`（`CrowdTwist-Register`）；
   - **Wave 2D**（`Cybersole.Http` 伴生能力）：`IBody` / `LegacyJsonBody` / `LegacyJarrayBody`、`ClickHouseSink`（内存 `BoundedChannel` + `FlushOnceAsync` / `DrainLocalQueueAsync`）、`HttpDebug` CSHD v1 二进制捕获流与 `RootCertificateStore`。

---

## 二、已结案度量面与可复算入口

> 最新实测值以 `docs/METRICS.md` 及 `docs/MODULE_FUNCTION_CENSUS.md` 当次生成快照为准。

| 面 | 口径与来源 | 复算命令 |
|---|---|---|
| 站点流程 | 见 `docs/METRICS.md`（`CORE_COVERAGE.md`：`unknown placeholders 0`、`provenance exit 0`） | `python tools/core_coverage.py` |
| 支付挑战与网关 | PayPal 3DS 九阶段 + Stripe 6 端点与挑战 + 静态派发映射 + Unzer/Cardinal/Checkout.com 状态机 | `python tools/payment_challenges.py`、相关单测 |
| captcha（识别面） | 四家 loader 字面量实证并接入 `StoreFlow.DetectAsync` | `python tools/captcha_coverage.py` |
| 风控厂商 | `controls ok True`、IDA 字符串缓存完整后 13 项全部命中（含 `Solving POW challange` / `Solving checkpoint`） | `python tools/vendor_coverage.py` |
| 名字 / 类型绑定缺口 | 见 `docs/METRICS.md`（`bind_diff.py` / `bind_scope.py`，`real gap 0`、`scope misses 0`、`unclassified 0`） | `python tools/bind_scope.py`、`python tools/bind_diff.py --buckets`、`python tools/bind_diff.py --type-presence` |
| 文案 | 见 `docs/METRICS.md`（19 区无缺） | `python tools/copy_audit_report.py` |
| 数据文件名 | `original-on-disk not in replica 0`；内嵌资源与只读兜底已区分（`docs/DATAFILES.md`） | `python tools/datafiles_diff.py` |
| 传输层与伴生能力 | `NetClient` 默认路径对齐原版 + `TlsProfile.Chrome150` + `IBody` + `ClickHouseSink` + `HttpDebug` + `RootCertificateStore` | 见 `HttpCompanionTests` 与 `NetClientLoopbackProbeTests` |
| 模块级函数普查 | 复刻 PDB+`.pdata` 100% 归因 + 原版 321,244 函数多信号归因（见 `docs/MODULE_FUNCTION_CENSUS.md`） | `python analysis/module_function_census.py --write-doc` |
| 套件与变异 | 全量非慢速套件与 `mutation-check.py` 最新结果见 `docs/METRICS.md` | `python tools/metrics_report.py`、`python tools/mutation-check.py` |

---

## 三、核心模块逐项状态

图例：**✅ 已结案落地** · **⛔ 外部阻塞** · **🚫 范围外（禁止实现）**

### ① 站点与结账流程（`Cybersole.Stores/Flows`）

| 项 | 状态 | 结论与证据（含诚实 Unknown 边界） |
|---|---|---|
| 流程骨架、62 店映射与地址模型 | ✅ | override steps 占位零、provenance exit 0；`AddressModels` 纳入 `DemandwareFlow`（`AddressModelsTests`） |
| `CheckPriceLimitApp` / `FindProductCDN`（Wave 2C） | ✅ | 基于 `0x140d1c1a0`（App GraphQL `/api/2020-04/graphql.json`）与 `0x140c986f0`（`https://cdn.cybersole.io/variants/topps-{tok}.json`）实现于 `ShopifyFlow.cs` 并覆盖 `Phase2StoreStepsTests`。<br>**Unknown**：`ToppsVariant` 在二进制 `off_1449B8EB0` 的精确序列化字段名尚未静态确认，已在代码与本文如实标注 |
| `CheckFanRewardState` / `SignUpFanRewards`（Wave 2C） | ✅ | 基于 `0x140a0fc40` / `0x140a13670` / `0x140a19360` 在 `RetailFlows.cs`（`FunkoFlow`）落地 `.crowd-twist-points` / `[class*='points-value']` / `CrowdTwist-Register`，覆盖 `Phase2StoreStepsTests` |
| per-store 差异（23 条 0 命中 `inferred`） | ⛔ | R1266 证实 NativeAOT 部分字面量逐字节不可搜；静态归 `unknown`，待 live capture |
| Farfetch 7 条与 `connect/app` payload | ⛔ | `connect/app` 属服务端下发配置，需原版有效登录凭据与实机抓包（R1077 / R1294） |

### ② 支付与客户端校验层（`Cybersole.Stores/Payments` & Scripts）

| 项 | 状态 | 结论与证据（含诚实 Unknown 边界） |
|---|---|---|
| PayPal 3DS 九阶段 + Stripe 6 端点与派发 | ✅ | `PayPalThreeDs.cs`、`StripeChallenge.cs`、`Gateways.cs`（8 条静态 `AsyncTaskMethodBuilder.Start` 映射全数对齐 + `StripeSetupIntentTests`） |
| `UnzerGateway`（`ContinueUnzerThreeDs`，Wave 2B） | ✅ | 基于 `0x140960560` / `0x14095e0f0` 在 `Gateways.cs` / `CasioFlow` / `StoreFlow` 实现 prepare / set-payment / `api.unzer.com/v1/types/card` tokenize / order submit / `unzer/payment/redirect` 与 `#threeds-method-data` 3DS 状态机（`UnzerThreeDsTests`）。<br>**Unknown**：`0x14094c210` 精确 prepare 子路径、`qword_1472c65a0+8` 终态集合、`0x14094a870` 动作判定谓词未全解，已在代码显式保留边界 |
| `CardinalThreeDs`（`CardinalInit`/`Continue`/`DeviceFingerprint`/`StepUp`，Wave 2B） | ✅ | 基于 `0x14092df10` / `0x140939110` 实现 Centinel `1.35.0`、CardinalTrusted `2.1.0`、`geo.cardinalcommerce.com` 设备指纹采集与 `Cruise/StepUp` + `TermRedirection`，并接入 `StoreFlow`（`RunCardinalStepAsync`）、`DemandwareFlow`（含 `dfReferenceId`）、`WarhammerFlow` 与 `PaynamicsGateway`（`CardinalThreeDsTests`） |
| `CheckoutComGateway`（`api.checkout.com`，Wave 2B） | ✅ | 实现 Shopify Offsite、`sessions-interceptor`、NIKE-GS/ESW `authentication-devices.checkout.com` 与 Mollie 4 条路径并注册至 `PaymentGatewayRegistry.CreateDefault()`（`CheckoutComGatewayTests`、`UnmatchedGatewaysTests`）。<br>**Unknown**：`0x1408a34f0` 尾部分支中按发卡行 ACS 主机区分的表单字段表尚未逐家穷举 |
| 便利店结算（Shopify `ConvenienceStores`） | ✅ | 基于 `0x140cf7090` / `0x140d98f60` / `0x140dcecf0` 在 `ShopifyFlow.cs` 实现 Komoju + WebCVS（`shift_jis`）表单逻辑（原版独立名 `CompleteConvenienceStore` 不存在）。<br>**Unknown**：`komoju_api` `formUrl` 后缀表达式 `0x140d98f60` `[1..56]` 仍记为 Unknown |
| captcha 识别面（被动分类） | ✅ | 四家 loader 字面量 + `CaptchaSurface.Classify` 接入 `DetectAsync` |
| 反爬传感器伪造与验证码绕过执行面 | 🚫 | `GetSbsdHash` / `GetSbsdScript`、`DdMobileTouchEvent` / `SensorPow`、`ExecuteClipModelAsync` / `SolveImageInCloudAsync` / `ClickCellsAsync` / `MoveMouseAndClickWithoutTrajectoryAsync`、以及 `HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 绕过执行均属严格 **Out of Scope**，严禁复现 |

### ③ 传输层与可观测性伴生包（`Cybersole.Http`）

| 项 | 状态 | 结论与证据 |
|---|---|---|
| 默认路径 / HTTP/3 与 `OwnTls` 定位 | ✅ | `NetClient` 对齐 `SocketsHttpHandler`/`SslStream`（30s 连接 / 90s 空闲超时）、增加 `TlsProfile.Chrome150`；`IsProductionTransport` 与 `IsExperimentalTransport` 在 `NetClient.cs`/`BouncyTls.cs` 显式收口 |
| `IBody` 与 `LegacyJsonBody` / `LegacyJarrayBody`（Wave 2D） | ✅ | 基于 `0x1408be3f0` / `0x14130d9b0` 实现于 `Content/BodyContent.cs` 并接入 `RequestOptions.Body` 与 `NetClient.BuildRequest` / `PostBodyAsync` / `PostJsonAsync(JToken)` |
| `ClickHouseSink`（Wave 2D） | ✅ | 基于 IDA `0x14331...` 实证实现于 `ClickHouseSink.cs`（内存 `BoundedChannel(100_000)` + `FlushOnceAsync` / `DrainLocalQueueAsync` gzip `JSONEachRow` 对 `http_requests` 35 列与 `http_connections` 23 列；原版不写本地溢出文件，不涉及 `%APPDATA%\Cybersole`）并接入 `HttpAnalytics` |
| `HttpDebug` 与 `RootCertificateStore`（Wave 2D） | ✅ | 实现 CSHD v1 二进制帧协议（`CSHD\x01` + 5 帧类型、`CYBERSOLE_HTTP_DEBUG`）接入 `NetClient.SendAsync`，以及 `[uint32 BE len][DER bytes]` `RootCertificateStore` 接入 `BouncyTls`（`HttpCompanionTests`） |

### ④ 服务与业务模型 / 冻结 UI 面（`Cybersole.Services` & `Cybersole.Core` / `Ui`）

| 项 | 状态 | 结论与证据 |
|---|---|---|
| `Cybersole.Services.Mail` 接线（Wave 2A） | ✅ | 基于 `0x140f486c0` / `WaitImapAsync` (`0x140f40490`) / `AycdInboxService` (`0x140f27ea0..0x140f2bb70`) 对齐 `AycdInboxClient` 与 `ImapMailProvider`，构建 `MailCodeService`（`Task.WhenAny` 并发竞速）接入 `AppServices.Mail` → `TaskEngine` → `CheckoutContext.WaitForMailCodeAsync`，并接入 `ImapView` / `ImapCreatorView` / `AycdInboxCreatorView` 测试按钮（`.ConfigureAwait(true)`，0 新增 UI 类），覆盖 `MailServiceWiringTests` |
| `BotTask.Running` / `BotTask.Task` | ✅ | Phase 1 静态证毕：`BotTask.Running` 为 `bool` 联动 `TaskGroup.Running`；`BotTask.Task` 为 `TaskBase` (`0x144C963C8`) |
| `only in descriptors` / `shape mismatches` / `datafiles` | ✅ | `docs/DESCRIPTOR_TRIAGE.md`（137 条 0 未分类 + 本地化实现）、`docs/SHAPE_GAPS.md`（`--baseline` 对齐）、`docs/DATAFILES.md`（内嵌资源与只读兜底分离） |
| 云同步 / 嵌入式浏览器 / 登录授权 | ⛔ / 🚫 | `DotNetBrowser`（商业库）、`SignalR` `/connect/app`、`MSAL`（含 Outlook OAuth token 刷新链）、`RabbitMQ`、`Velopack` 远端更新归 **External Blocked**；`AuthWindow`/`LicenseControl` 维持 **R702 Out of Scope** |

---

## 四、本机差距 + Phase 2 核心队列核销总账

1. **R1300 本机可做 8 项**：**8/8 已结案**（`only-in-descriptors`、模块级函数普查、`shape mismatches`、`datafiles`、Stripe 派发、HTTP/3 与超时、`OwnTls`、`vendor_coverage.py`）。
2. **Phase 2 核心模块队列 Waves 2A–2D**：**4/4 已落地并通过验证**（Wave 2A 邮件/OTP 接线、Wave 2B Unzer/Cardinal/CheckoutCom 3DS 与便利店支付、Wave 2C Shopify/Topps CDN/Funko 奖励步骤、Wave 2D `Cybersole.Http` 伴生能力）。
3. **剩余未做项全部属外部阻塞或明确范围外**（按 GOAL 允许范围封存）：
   - **原版有效登录凭据**：Farfetch 7 条与 `/connect/app` payload、`SignalR`/`Remote*` 云端同步；
   - **live capture（真实请求/响应）**：23 条 0 命中 `inferred` 字面量，以及静态未解子分支（Unzer prepare 子路径/终态集、CheckoutCom 各发卡行 ACS 表单表、Komoju `formUrl` 后缀、`ToppsVariant` JSON 键名）；
   - **商业引擎 / 外部运行时**：`DotNetBrowser 4.3.5.8591` + Chromium、`MSAL` Outlook OAuth 交互流、`Velopack` CDN；
   - **严格范围外（禁止复现）**：R702 授权登录（`AuthWindow`/`LicenseControl`）、所有反爬传感器伪造与验证码绕过执行（`GetSbsdHash`、`DdMobileTouchEvent`/`SensorPow`、`ExecuteClipModelAsync`/`ClickCellsAsync`、`HCaptchaSpoof`/`RecaptchaEnterprise`/`TurnstileSiteKey` 绕过）。
