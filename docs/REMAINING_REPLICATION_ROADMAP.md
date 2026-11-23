# 完整复现剩余工作路线图（R1383 更新基线）

> **更新日期**：`2026-11-23` · **接续基线**：在 Phase 1 + Phase 2 与 R1382 审计纠偏之后，**R1383 已通过在线 IDA Pro（`target/Cybersole.exe.i64`）完成优先级 ①–③ 本地可达成静态逆向与运行态重实现（Batches 1–3）**，重发布 NativeAOT 产物为 `current`，并完成全量非浏览器套件与文档守卫验证；第 ④ 优先级 UI 绑定保持冻结。
> **唯一动态指标源**：`docs/METRICS.md`（由 `python replica/tools/metrics_report.py` 生成）
> **关联权威档案**：`docs/MODULE_FUNCTION_CENSUS.md` · `docs/ASYNC_TAIL.md` · `docs/C8_STRING_CLASSES.md` · `docs/VENDOR_WIRING.md` §十三 · `docs/PROGRESS_AND_GAP.md` · `docs/SHAPE_GAPS.md` · `docs/PARITY_CLAIMS.md`
> **口径说明**：本文中标注 `2026-11-20` 或 `R13xx` 的历史数值均为对应时点快照；实时动态数值一律以 `docs/METRICS.md`、`docs/MODULE_FUNCTION_CENSUS.md` 及 `docs/ASYNC_TAIL.md` 最新生成输出为准。

---

## 一、本机静态逆向与工程工作进展（Batches 1–3 已结案项与剩余技术边界）

### 1. `Cybersole.Stores` 站点流程与支付状态机（Batch 1 / 2 / 3C）

- **已补齐并接通的支付网关与 ACS 状态机**：
  1. **Batch 1**：落地 `StripeGateway`、`CommerceHubGateway`（含 `FunkoFlow`）、`GmoGateway`（含 `ToysRUsJpFlow`）、`KomojuGateway`（card/konbini 与 URL 解析）；
  2. **Batch 2（Checkout.com 28 家发卡行 ACS 处理器）**：依据 `0x1408a34f0` 在 `CheckoutComAcsHandlers.cs` 实现 19 个无头 ACS 簇与 `20_fallback` 共 28 家发卡行处理器，接入 `CheckoutComGateway` 并由 `CheckoutComAcsHandlersTests` 覆盖；
  3. **Batch 3C 站点消歧与核心流程重实现**：
     - **归属消歧**：确认 `0x14088A9E0` 属 **`JDGroup`/`FINL`**（Finish Line / JD Sports US，`GraphQlHashQueries` + Vantiv `eProtect`），`0x140E49000..0x140E63000` 为唯一 **`Warhammer`** CT 模块（Commercetools + `StoreSessionQueries` 18 步 + Cybersource Flex + Cardinal 3DS），两者分别接入 `JdSportsFlow` 与 `WarhammerFlow`（保留既有 `WarhammerGraphQlTests` pins）；
     - **`CasioFlow`**（`0x1409477E0`）：实现 Magento 前置 + 4 条非 PoW 支付路径（Stripe / Adyen / Unzer / Square）与 `casio.sku`（安全跳过 PoW `0x140949680` 与 Stripe Sensor `0x140959320`）；
     - **Panini / JohnLewis / Scheels / Shopify / 安全异步尾**：补齐 `MagentoFlow`（`onepanini` + PPCP + `Braintree*`）、`JohnLewisFlow`、`ScheelsFlow`（`StorefrontApiQueries`，保留 `/api/search` pin）、`ShopifyFlow`（`SignInAsGuest`/`customerAccessTokenCreate`/`ShopProductSearch`/`ProductDetails`/`product-drops`/`OnRunning`/`createCart`/`CreateCheckoutAsync`/`PaypalDetails`）及 `Nike`/`PopMart`/`Saucony`/`StoreFlow` 安全异步尾；
     - **GraphQL 覆盖核销**：`operation_gap.py`（R1383 修复注释/字面量/多返回与 1-hop `Envelope(` 解析）达到 **64 / 65** 生产调用（仅余 `cartCreate` 在原版亦为 0 调用死常量），无人写入 `Session.Vars` 旁路开关由 `51` 降至 **`14`**。
- **异步状态机尾项收口**（见最新生成的 `docs/ASYNC_TAIL.md` 与 `analysis/.payment_tail.json`）：
  - `docs/ASYNC_TAIL.md` 已按最新代码与产物重生成（payment 缺席名由 `66`/`63` 降至 **`56`**，store 缺席名降至 **`33`**）；`classify_payment_tail.py` 验证 **56 项中 0 可直接跟引用、56 项仅元数据**（受限于运行期/反爬/未实现外部网关）。
- **Unzer `apiKey` 与 Topps / `Saucony` 剩余边界**：
  - `Saucony` 已落地安全可控的公开流程步骤，剩余依赖实站接口响应或反爬传感的环节受安全/外部阻塞约束；`ToppsVariant` 键大小写按兼容读取处理。

### 2. 优先级 ② 反爬与风控面（严格只读被动审计）

- **已结案边界**：`docs/VENDOR_WIRING.md` §十三（R1383）完成 7 家未接线风控站点（Akamai / BotDeflector / Cloudflare / DataDome / PerimeterX / Queue-it / Vercel）与 Casio PoW/Stripe Sensor/ShopPay Gatekeeper 的**只读被动架构分型**；`vendor_coverage.py`（`controls ok=True`）守卫常态运行。
- **工程禁令**：`replica/src/` 中保持**零**主动反爬绕过、sensor 生成器、PoW 求解器或 CAPTCHA 求解代码。

### 3. 传输层与 HTML DOM 解析栈（Batch 3C Part 1）

- **HTML DOM 解析栈**：已引入 **`AngleSharp 1.4.0`**，以 `HtmlFormDom.cs` 替代支付与流程中的 HTML 正则解析，并通过 `PublishAot=true` 全量NativeAOT 链接验证。
- **HTTP 压缩与协议对齐**：已引入 **`ZstdSharp.Port 0.8.1`** 与 `Compression/ContentEncodingCodec.cs`（支持 gzip/deflate/br/zstd 与逆序多编码解码/出站编码），对齐 `NetClient` / `BouncyHttpClient` / `BouncyH2Client` / `RedirectPolicy` 的代理、请求头覆盖、`RequestOptions.Cookies` 注入回写与单层重定向环（`NetClientProtocolParityTests`）。
- **未追平传输基础设施**：原版 Go 移植 `chrome_150` 自定义 QUIC/HTTP3 指纹传输栈仍属独立重型基础设施边界，暂维持既有 `SocketsHttpHandler`+`SslStream` 与实验 `BouncyTls` 分层（不伪装 HTTP/3 自定义指纹）。

### 4. 行为等价与字符串分类验收（`C7c` & `C8`）

- **`C7c`**：`C7cBehavioralParityTests`（7 条确定性本地回环探针）与 `NetClientProtocolParityTests` 已落地并纳入默认 `metrics_report.py` 套件；全二进制任意函数伪代码等价因缺原版 PDB 仍诚实保留 `unknown`（见 `docs/PARITY_CLAIMS.md`）。
- **`C8`**：`analysis/c8_string_class_compare.py` 已补全 `Cybersole.Locales.en.json` 全量 58 项顶层前缀（1142/1142 覆盖）并移除框架/拼接 DLL/OCSP/CRL/NuGet 噪声，`docs/C8_STRING_CLASSES.md` 已按最新产物重生成（按 §4.5 保留 `unknown` 判据）。

### 5. UI 绑定形状（`docs/SHAPE_GAPS.md` — 优先级 ④ 冻结）

- 名字级与类型级绑定缺口归零；剩余成员形状差异（详见 `docs/METRICS.md` 与 `replica/docs/BINDING_BACKLOG.md`）与 `MonitorView` 3 条未定语义命令继续**冻结在优先级 ④**，待后续专门阶段或外部实机观察决策。
- 店铺表面结构差异（`docs/STOREFRONT_SURFACE.md`：原版 2669 裸域 vs 复刻 800 域）属范围决策而非局部缺漏。

---

## 二、必须先补齐外部条件才能推进的工作（`External Blocked`）

这部分逻辑或数据不存在于离线可执行文件本体中，或依赖受限外部设施，未获外部条件前**严禁猜测或编造实现**：

1. **需要原版有效登录账号 / 许可**
   - **服务端配置下发与线上站点目录**：捕获 `https://api.cybersole.io/connect/app` 的 `SignalR` 通道，解锁 `FarfetchFlow` 7 条服务端下发路由与完整线上站清单；
   - **云同步 / 队列 / 认证 / 更新基础设施**：`RabbitMQ.Client`、`MSAL`（含 Outlook OAuth2 交互令牌刷新）、`Velopack`（`cdn.cybersole.io/releases/`）；
   - **主界面实机观察与完整备份**：B 类 31 条 UI 本地动作（`docs/R508_LICENSE_GATE.md`）、`MonitorView` 3 条命令动作、含非空 `profiles` 的原版 `.cyb` 备份。
2. **需要真实站点流量抓包（Live Capture）**
   - 闭合 `Stores/Flows` 中 23 条 `inferred` 0 命中字面量，以及真实结账响应载荷对齐。
3. **需要决定嵌入式浏览器引擎方案**
   - 商业授权 **`DotNetBrowser 4.3.5.8591` + Chromium** vs 开源 WebView2/CEF 宿主与 `CustomBrowser.Autofill`。

---

## 三、不必盲目追平的“结构性非等价噪声”

后续验收不得把 `docs/METRICS.md` 里的 `.pdata` 函数总数比追到 `100%` 作为完成判据，原因如下：

1. **.NET 10 NativeAOT vs .NET 8 NativeAOT 运行时差异**：BCL、NativeAOT CRT、PE 节布局（`6` 节 vs `9` 节）与原版静态 Brotli 库 39 个导出天然不同。
2. **AOP 编译织入 vs 手写通知**：原版依赖 `Metalama.Framework`，复刻件采用手写 `ObservableObject` + `RelayCommand`。
3. **函数体量构成悬殊**：复刻件 `.pdata` 中绝大部分为 `System.*` / `Avalonia.*` / CRT（详见 `docs/MODULE_FUNCTION_CENSUS.md`），度量聚焦业务函数与协议行为等价。

---

## 四、后续推进条件路线

| 条件前提 | 推荐优先路线 | 说明 |
|---|---|---|
| **路线 A（当前本机无新凭据边界）** | 本机静态阶段已收口 | ①–③ 本机可达成核心流程、支付/ACS 状态机、DOM/HTTP 协议栈、只读风控分型及 `C7c`/`C8` 仪器已全部收口并过门禁 |
| **路线 B（获得原版有效许可 + 备份 + 抓包）** | 外部阻塞解锁路线 | 解锁 `FarfetchFlow` 7 路由、`/connect/app` SignalR 云同步、`MSAL`/B 类 31 条 UI 动作与 `23` 条 `inferred` 实机报文 |
| **路线 C（需完整内置浏览器或 UI 形状清零）** | 浏览器引擎拍板 / 优先级 ④ 解冻 | 先决策 `DotNetBrowser` vs WebView2/CEF，再按需解冻 `SHAPE_GAPS` 与 `BINDING_BACKLOG.md` |
