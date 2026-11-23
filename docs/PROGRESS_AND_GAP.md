# 进度与差距（`full-QUIC/HTTP3/TLS` 支线纯 C# 网络栈落地 · 2026-11-23）

> **R1383 更新（2026-11-23）**：接续 R1382 审计纠偏，已在 IDA Pro（`target/Cybersole.exe.i64`）辅助下完成优先级 ①–③ 本地可达成静态逆向与可执行代码重实现（Batches 1–3：支付网关/ACS 状态机、`JDGroup/FINL` 与 `Warhammer` CT 归属消歧、`Casio` 四网关、`Panini`/`Scheels`/`Shopify`/`JohnLewis`/`Saucony`/`Nike`/`PopMart` 安全业务链路与异步尾、`AngleSharp 1.4.0` DOM + `ZstdSharp.Port 0.8.1` + `Cybersole.Http` 协议对齐、风控架构分型、`C7c` 本地回环行为探针与 `C8` 分类去噪），全量 NativeAOT 产物已重发布（`state: current`），全部指标与非浏览器全量套件绿灯，第 ④ 优先级 UI 绑定保持冻结。
>
> **R1384 解冻与 `full-QUIC/HTTP3/TLS` 支线落地（2026-11-23）**：本文原先标 🔒 的「风控主动求解层」**整类解冻**，转为 **②-A 主战场**（施工图见 `docs/VENDOR_WIRING.md` §十四）。经 IDA 实证原版 `Cybersole.Http 0.10.0` 为 **100% 纯 C# 自研栈**（`0x14316a46e`，借用 uTLS `chrome_150` 等命名，PE 无 Go 运行时 / `msquic` / `quiche` / `boringssl`）；在独立支线 **`full-QUIC/HTTP3/TLS`**（`main` 锁定 `288a95e` 未改）已完成纯 C# Crypto / ML-KEM-768 / X.509+121 嵌入式根证书 / 82 组 `ClientProfile` 与 68 组 `ClientHelloSpec` / TLS 1.2+1.3（HRR / ALPS `0x44CD`&`0x4469` / RFC 8879 证书压缩 / KeyUpdate）/ QUIC v1（1-RTT KeyUpdate `"quic ku"` `HpKey` 不变性、Retry、`scidLen=0`）/ QPACK / HTTP/3 / HTTP/2+HPACK / HTTP/1.1 / Dialers / `ProtocolRacer` / `OriginPool` / `TlsClientCache` / `TransportMode.PureNetClient` 的完整复刻，并通过离线 Go 1.26.2 + `quic-go@v0.61.0`（7/7）及公网真实边缘与 `tls.peet.ws`/`tls.browserleaks.com`（16/16，`InsecureSkipVerify = false`）实测验证（详情见 `docs/LIVE_NETSTACK_INTEROP.md`）；③-A 仅剩**嵌入式浏览器引擎选型**（`docs/NETSTACK_ADR.md`）。
>
> **动态度量唯一事实源**：`docs/METRICS.md`（在 `replica/` 下由 `python tools/metrics_report.py` 生成；本文活区不硬编码易漂移的全量数值）。
> **模块普查与差距依据**：`docs/MODULE_FUNCTION_CENSUS.md` · `docs/ASYNC_TAIL.md` · `docs/C8_STRING_CLASSES.md` · `docs/VENDOR_WIRING.md` · `docs/DESCRIPTOR_TRIAGE.md` · `docs/SHAPE_GAPS.md` · `docs/DATAFILES.md`
> **剩余路线与新会话交接**：`docs/REMAINING_REPLICATION_ROADMAP.md` · `docs/HANDOFF.md` · `docs/HANDOFF_PROMPT_antigravity.md`
> 判据 a–f 的逐条结构性证明在 `docs/GOAL_VERIFICATION.md`、`docs/PARITY_CLAIMS.md`；本文回答：**本地已结案面**、**②-A 主动求解层议程与诚实 Unknown 边界**、以及**外部阻塞 / 范围外项**。

---

## 一、一句话结论

1. **R1300 列出的 8 项本机可做差距已全部收口**（Phase 1：137 条描述符全量归类与本地化行为、模块级函数分布与类型/方法普查、核心成员形状、数据文件名对照、Stripe 构建器静态映射、HTTP/3 与超时核实、`OwnTls` 定位、`vendor_coverage.py` 全量复核，`BotTask.Running`/`BotTask.Task` 静态定型）。
2. **Phase 2（Waves 2A–2D）与 R1383（Batches 1–3）本地核心模块缺口已反编译落地并接通运行时**：
   - **Wave 2A**（`Cybersole.Services.Mail` + `AppServices` + `TaskEngine` + `Settings`）：并发 `Task.WhenAny` 调度 `ImapMailProvider` + `AycdInboxClient` 消除死岛；
   - **Wave 2B + R1383 支付状态机**（`Cybersole.Stores/Payments`）：`StripeGateway`、`CommerceHubGateway`、`GmoGateway`、`KomojuGateway`（card/konbini 与 URL）、`UnzerGateway`（`ContinueUnzerThreeDs` + 非写死端）、`CardinalThreeDs`（`Init`/`Continue`/`DeviceFingerprint`/`StepUp`）、`BraintreeClientToken`/`BraintreeTokenizeCard` 与 **`CheckoutComGateway` + `CheckoutComAcsHandlers`**（按 `0x1408a34f0` 补齐 28 家发卡行 ACS 主机 / 19 无头簇与交互回退处理器，并用 `HtmlFormDom` 替代正则）；
   - **Wave 2C + R1383 站点流程**（`Cybersole.Stores/Flows`）：通过 IDA 主工厂实证消除归属误判（确认 `0x14088A9E0` 属 **`JDGroup`/`FINL`**，`0x140E49000..0x140E63000` 为唯一 **`Warhammer`** CT 模块）、落地 **`CasioFlow`** Magento 前置 + 4 条非 PoW 网关（Stripe/Adyen/Unzer/Square）、**Panini** 8 步流程与 PPCP/Braintree、**`JohnLewisFlow`**、**`ScheelsFlow`**（`StorefrontApiQueries`，保留 `/api/search`）、**`ShopifyFlow`**（`SignInAsGuest`/`customerAccessTokenCreate`/`ShopProductSearch`/`ProductDetails`/`product-drops`/`OnRunning`/`createCart`/`CreateCheckoutAsync`/`PaypalDetails`）及 `Nike`/`PopMart`/`Saucony`/`StoreFlow` 安全异步尾（GraphQL 65 项操作中已接线 64/65，唯一未接 `cartCreate` 为原版 0 调用死常量）；
   - **Wave 2D + R1383 传输与 DOM 栈**（`Cybersole.Http` & `Cybersole.Stores`）：`IBody`/`LegacyJsonBody`/`LegacyJarrayBody`、`ClickHouseSink`、`HttpDebug`、`RootCertificateStore`，新增 **`ZstdSharp.Port 0.8.1`**（`ContentEncodingCodec` 逆序多编码解压与出站编码）、**`AngleSharp 1.4.0`**（`HtmlFormDom`）并对齐 `NetClient` / `BouncyHttpClient` / `BouncyH2Client` / `RedirectPolicy`（代理、请求头覆盖、`RequestOptions.Cookies` 注入/回写、`AllowAutoRedirect=false` 单层重定向环）；
   - **风控架构分型与 `C7c`/`C8` 验收仪器**：`docs/VENDOR_WIRING.md` §十三完成 7 家站点风控与 Casio PoW/Stripe Sensor/ShopPay Gatekeeper 的架构分型（R1383 阶段只到分型，主动实现由 R1384 解冻后的 §十四 接管）；`C7cBehavioralParityTests` 与 `NetClientProtocolParityTests` 建立本地回环请求/状态探针；`analysis/operation_gap.py`（未写入旁路键 `51 → 14`）与 `analysis/c8_string_class_compare.py` 完成修复去噪（`Cybersole.Locales.en.json` 全覆盖）。

---

## 二、已结案度量面与可复算入口

> 最新实测值以 `docs/METRICS.md`、`docs/MODULE_FUNCTION_CENSUS.md`、`docs/ASYNC_TAIL.md` 与 `docs/C8_STRING_CLASSES.md` 当次生成快照为准。

| 面 | 口径与来源 | 复算命令 |
|---|---|---|
| 站点流程 | 见 `docs/METRICS.md` 与 `replica/docs/CORE_COVERAGE.md`（占位、`provenance exit` 与 `operation_gap` 以当次生成值为准） | `python replica/tools/core_coverage.py`、`python analysis/operation_gap.py`、`python replica/tools/endpoint-provenance.py` |
| 支付挑战与网关 | PayPal 3DS + Stripe + CommerceHub + GMO + Komoju + Unzer + Cardinal + Braintree + Checkout.com 28 家 ACS 处理器 | `python replica/tools/payment_challenges.py`、相关单测 |
| captcha / 风控面 | captcha 四家 loader 被动分类 + 架构分型（§十三）；**主动求解层见 ②-A / `VENDOR_WIRING.md` §十四** | `python replica/tools/captcha_coverage.py`、`python replica/tools/vendor_coverage.py` |
| 名字 / 类型绑定缺口 | 见 `docs/METRICS.md`（`real gap`、`types with scope misses`、`unclassified` 均以当次输出为准） | `python replica/tools/bind_scope.py`、`python replica/tools/bind_diff.py --buckets`、`python replica/tools/bind_diff.py --type-presence` |
| 文案与数据文件名 | `copy: zones with a missing key` 与 `datafiles` 见 `docs/METRICS.md`、`docs/DATAFILES.md` | `python replica/tools/copy_audit_report.py`、`python replica/tools/datafiles_diff.py` |
| 传输层与行为探针 | `ContentEncodingCodec`（gzip/deflate/br/zstd）、`HtmlFormDom`（AngleSharp）、`NetClient`/`Bouncy*` 对位 + `C7c` 本地回环探针 | `dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~C7cBehavioralParity" && dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~NetClientProtocolParity"` |
| 模块普查 / 字符串分类 | 复刻 PDB+`.pdata` 100% 归因、原版多信号归因及去噪 `C8` 五类串对照见各生成文档 | `python analysis/module_function_census.py --write-doc`、`python analysis/c8_string_class_compare.py --write-doc` |
| 套件、产物与变异 | 全量非浏览器套件、`PublishAot` 陈旧度与 `mutation-check` 最新结果见 `docs/METRICS.md` | `cd replica && python tools/metrics_report.py`、`python replica/tools/mutation-check.py` |

---

## 三、核心模块逐项状态

图例：**✅ 已结案落地** · **🚧 ②-A 主动求解层实现中** · **⛔ 外部阻塞**

### ① 站点与结账流程（`Cybersole.Stores/Flows`）

| 项 | 状态 | 结论与证据（含诚实 Unknown / 外部条件边界） |
|---|---|---|
| 流程骨架、62 店映射与地址模型 | ✅ | `StoreModuleCatalog.CreateAll()`（62 项）与 `AddressModels` 保持一致；`endpoint-provenance` `0 invented / 0 unknown` |
| Batch 1 & Batch 3C 核心店铺与 GraphQL 接线 | ✅ | 修正 `JDGroup/FINL` vs `Warhammer` CT 归属；落地 `CasioFlow`（Magento+4 网关）、`Panini`（`onepanini`）、`JohnLewis`、`Scheels`、`ShopifyFlow` 缺失操作与 `Nike`/`PopMart`/`Saucony`/`StoreFlow` 安全异步尾；`operation_gap` 达成 64/65 调用（仅余 0 调用死常量 `cartCreate`），`C7cBehavioralParityTests` 回环实证 |
| `CheckPriceLimitApp` / `FindProductCDN` / `Funko` 奖励 | ✅ | Wave 2C 已落地并由 `Phase2StoreStepsTests` 覆盖；`ToppsVariant` 键大小写仍如实标兼容读取 |
| per-store 差异（23 条 0 命中 `inferred`） | ⛔ | R1266 证实 NativeAOT 部分字面量逐字节不可搜；静态归 `unknown`，待 live capture |
| Farfetch 7 条与 `connect/app` payload | ⛔ | `connect/app` 属服务端下发配置，需原版有效登录凭据与实机抓包（R1077 / R1294） |

### ② 支付与客户端校验层（`Cybersole.Stores/Payments` & Scripts）

| 项 | 状态 | 结论与证据（含 ②-A 求解进度与 Unknown 边界） |
|---|---|---|
| PayPal 3DS / Stripe / Unzer / Cardinal / CommerceHub / GMO / Komoju / Braintree | ✅ | 主干状态机与网关均已落地，覆盖 `PayPal*`、`Stripe*`、`UnzerThreeDsTests`、`CardinalThreeDsTests`、`KomojuGatewayTests` 及 `C7cBehavioralParityTests` |
| `Checkout.com` 28 家发卡行 ACS 处理器 | ✅ | `CheckoutComAcsHandlers.cs`（19 个无头簇 + `20_fallback`）接入 `CheckoutComGateway` 并以 `HtmlFormDom` 解析表单（`CheckoutComAcsHandlersTests`） |
| captcha 识别面与 7 家风控架构分型 | ✅ / 🚧 | 四家 captcha loader 被动分类接入 `DetectAsync`；`docs/VENDOR_WIRING.md` §十三完成 7 家（Akamai / BotDeflector / Cloudflare / DataDome / PerimeterX / Queue-it / Vercel）与 Casio PoW/Stripe Sensor 的架构分型；**主动求解器、sensor 生成器与 CAPTCHA 绕过列 R1384 解冻的 ②-A 主战场**，施工图与验收口径见 §十四（每族「检测 → 求解 → 存回」三件齐全才算 `Wired`） |
| 未解运行期子分支（Komoju 真站表单体等） | ⛔ | 仅靠真实结账响应方能进一步确认的运行期细节保留 `unknown`/外部阻塞，不编造 |

### ③ 传输层、DOM 解析与验收仪器（`Cybersole.Http` & `analysis/`）

| 项 | 状态 | 结论与证据 |
|---|---|---|
| `NetClient` / `BouncyHttpClient` / `BouncyH2Client` / `RedirectPolicy` 对位 | ✅ | 合入 **`ZstdSharp.Port 0.8.1`**（`ContentEncodingCodec` 逆序解码/出站压缩）、`SChannel` 代理与头覆盖、`RequestOptions.Cookies` 注入回写及单层重定向环（`NetClientProtocolParityTests`） |
| HTML DOM 解析栈替换（`AngleSharp 1.4.0`） | ✅ | `HtmlFormDom.cs` 替代支付与流程 HTML 正则，AOT 原生发布已编入 `.publish-aot/Cybersole.Ui.exe` |
| `IBody` / `ClickHouseSink` / `HttpDebug` / `RootCertificateStore` | ✅ | Wave 2D 伴生能力全部在线并覆盖 `HttpCompanionTests` |
| 纯 C# QUIC/HTTP3/TLS 指纹传输栈 | ✅（支线完成） | 已在独立支线 `full-QUIC/HTTP3/TLS` 完成原版纯 C# `Cybersole.Http 0.10.0` 全栈复刻（IDA 实证 `0x14316a46e` 非 Go 移植）：`Crypto` + `MlKem768`、`X509` + 121 嵌入式 `RootCertificates.bin`、`Profiles`（82 槽/68 spec 含 `chrome_150`/`chrome_148_quic`）、TLS 1.2/1.3（HRR / ALPS `0x44CD`&`0x4469` / RFC 8879 / KeyUpdate）、QUIC v1（`Retry` / `"quic ku"` `HpKey` 不变性 / DNS IPv4 一致性）+ HTTP/3 + QPACK、HTTP/2（精确 `ConnectionFlow`）+ HPACK + HTTP/1.1、`Dialers`、`ProtocolRacer`、`OriginPool`、`TlsClientCache` 与 `TransportMode.PureNetClient`；通过 Go 1.26.2 + `quic-go@v0.61.0`（7/7）、公网边缘/指纹 Oracle（16/16，`InsecureSkipVerify = false`）及 `PublishAot` 实测（详见 `docs/LIVE_NETSTACK_INTEROP.md`）；浏览器宿主选型见 `docs/NETSTACK_ADR.md` |
| `C7c` 行为探针与 `C8` 串比对仪器 | ✅ | `docs/PARITY_CLAIMS.md` 已更新；`C8` 覆盖全量 `en.json` 前缀并去噪生成 `docs/C8_STRING_CLASSES.md`（保留 §4.5 `unknown` 诚实判据） |

### ④ 服务与业务模型 / 冻结 UI 面（`Cybersole.Services` & `Cybersole.Core` / `Ui`）

| 项 | 状态 | 结论与证据 |
|---|---|---|
| `Cybersole.Services.Mail` / `BotTask` / 描述符与数据文件 | ✅ | Wave 2A 与 Phase 1 收口完成；文案缺失与名字/类型绑定缺口保持零水平 |
| UI 成员形状（`SHAPE_GAPS`）与 `MonitorView` 3 命令 | ⏸️ | 依据 R757 优先级纪律继续**冻结在优先级 ④**，不提前解冻 |
| 云同步 / 嵌入式浏览器 | ⛔ / 🚧 | `SignalR` `/connect/app`、`MSAL`（Outlook OAuth）、`RabbitMQ`、`Velopack` 归 **External Blocked**（需原版凭据）；**浏览器引擎选型留作 ③-A 待裁决议程**（`DotNetBrowser 4.3.5.8591` / WebView2 / CEF 见 `docs/NETSTACK_ADR.md`；网络传输栈已在 `full-QUIC/HTTP3/TLS` 支线落地） |

---

## 四、本机核心议程与阻塞边界总账

1. **Phase 1 + Phase 2（Waves 2A–2D）+ R1383（Batches 1–3）**：优先级 ①–③ 本机可达成静态逆向与运行态重实现均已落地，NativeAOT 产物重编为 `current`，`mutation-fit` 全绿且 `staleness: 0`，全量非浏览器 xUnit 套件与 9 项 Python 静态守卫全部通过。
2. **②-A 主动求解层（R1384 解冻，本轮主战场）**：Casio `0x140949680`（PoW）、`0x140959320`（Stripe sensor）、ShopPay Gatekeeper 全链，以及 Akamai/Cloudflare/DataDome/PerimeterX/Queue-it/BotDeflector/Vercel 的主动求解器、sensor 生成器与 CAPTCHA 绕过逻辑，全部要在 `replica/src/` 落成可执行实现；施工图、令牌落点与验收口径见 `docs/VENDOR_WIRING.md` §十四，度量入口 `python replica/tools/vendor_coverage.py`。
3. **③-A 嵌入式浏览器引擎选型（网络栈已在支线完成）**：纯 C# `Cybersole.Http`（QUIC v1 / HTTP/3 / TLS 1.2+1.3 / 82 Profile）已在 `full-QUIC/HTTP3/TLS` 支线落地并通过 Go/`quic-go`、公网严格校验证书互操作（`docs/LIVE_NETSTACK_INTEROP.md`）与 NativeAOT 验证；③-A 仅剩 `DotNetBrowser 4.3.5.8591` vs WebView2 vs CEF 宿主选型裁决与适配（`docs/NETSTACK_ADR.md`）。
4. **剩余未做项属外部阻塞或高成本独立基础设施**：
   - **原版有效登录凭据**：Farfetch 7 条与 `/connect/app` payload、`SignalR`/`Remote*` 云同步、B 类 31 条 UI 本地动作与完整 `.cyb` 备份；
   - **Live Capture**：23 条 0 命中 `inferred` 字面量与真站实时响应对齐；
   - **外部运行时**：`MSAL`、`RabbitMQ`、`Velopack`（均需凭据/账号侧条件）；
   - **冻结面**：④ UI 成员形状（`replica/docs/BINDING_BACKLOG.md`）。
