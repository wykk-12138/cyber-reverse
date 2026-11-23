# ADR · 嵌入式浏览器引擎选型（③-A 议程 · 网络栈已在 `full-QUIC/HTTP3/TLS` 支线落地，浏览器宿主待裁决）

> **这份文档的用途**：③-A 的浏览器宿主裁决单。R1384 将「商业 `DotNetBrowser` vs 开源 WebView2/CEF」与原版自定义 QUIC/HTTP3/TLS 指纹传输栈移出 `External Blocked`；**`full-QUIC/HTTP3/TLS` 支线现已按 IDA 实证完成纯 C# `Cybersole.Http 0.10.0` 全栈复刻**（`main` 保持在 `288a95e` 未改），本 ADR 目前唯一待裁决项为**嵌入式浏览器引擎选型**（第 3 节）。

---

## 1. 为什么现在要裁

经 IDA Pro 实证（`0x14316a46e`，PE 中无 Go 运行时、`msquic`、`quiche` 或 `boringssl` 导出），原版 `Cybersole.exe` 把两件事打包在一起：**浏览器宿主**（`DotNetBrowser` 653 函数 + `Cybersole.Web.BrowserHandlers`）与 **100% 纯 C# 自研 `Cybersole.Http 0.10.0` 传输栈**（借用 uTLS 命名风格的 `chrome_150` 等预设，内建 TLS 1.2/1.3、ML-KEM-768、QUIC v1/QPACK/HTTP/3、HTTP/2+HPACK 与 X.509 根证书校验）。复刻件在 `full-QUIC/HTTP3/TLS` 支线已通过 `TransportMode.PureNetClient` 完整补齐该纯 C# 传输栈；浏览器面目前仍走 Avalonia + 外部 Chrome 进程驱动。

以下三类驱动因素决定了浏览器引擎裁决仍需落定：

1. `Kasada` 浏览器求解（`ChromiumKasadaSolver`）、`CustomBrowser.Autofill`、②-A 里需要 JS 执行的分支（Cloudflare Turnstile / hCaptcha / Vercel challenge）各自接一次外部宿主；
2. 传输层的纯 C# 预设（`chrome_150` / `chrome_148_quic` 等 82 组 `ClientProfile`）已可在复刻件离线/回环对位，但浏览器宿主环境下的 JS/DOM/BOM 行为仍需统一托管方案；
3. `PublishAot` 下第三方浏览器库的 COM/Interop 面是发布风险，越晚裁越贵。

## 2. 候选与六维判据

| 候选 | 授权 | 指纹可编程度 | AOT 兼容 | 备注 |
|---|---|---|---|---|
| **`DotNetBrowser 4.3.5.8591` + 外部 Chromium** | 商业授权（原版同款） | 中（宿主级 API，深度指纹受库限制） | 待实测（COM/Interop） | 与原版结构最接近，行为对齐成本最低 |
| **WebView2** | 随 Windows/Edge 分发 | 低（Runtime 版本与指纹跟随系统 Edge） | 好 | 装机零成本，指纹不可控 |
| **CEF** | BSD，但需自带二进制 | 中高（可改 `onBeforeSendHeaders`、可注入） | 需自管进程与分发 | 体积与更新成本高 |
| **纯自研 `Cybersole.Http`（`PureNetClient`）+ 外部 Chrome / JS 引擎** | 自有 | 最高（已在 `full-QUIC/HTTP3/TLS` 支线实现 TLS/H2/H3 全字段控制） | 最好（已在 `PublishAot=true` 编译验证） | **传输层已解决**；无内置 JS 执行，浏览器分支仍需宿主 |

**判据（六维，逐项打分写在第 3 节表里）**：

1. TLS `ClientHello` 可编程度：cipher 顺序、extension 顺序与内容、`ALPN`、GREASE（纯 C# 传输栈已就绪，浏览器方案仅评宿主页头行为）；
2. HTTP/2 `SETTINGS` 帧顺序、`WINDOW_UPDATE`、伪头顺序（`chrome_150` 对齐度）；
3. QUIC/HTTP3 可编程度（`Initial` 包字段、transport parameters）；
4. `PublishAot=true` 下的可编译性与运行期依赖（COM、`DllImport`、动态加载）；
5. 授权与再分发（商业库的席位、离线激活、CI 可行性）；
6. 每任务一 profile 的内存与并发（N 个任务 = N 个 profile 时的实测上限）。

## 3. 裁决（浏览器引擎待填；纯 C# 网络栈已在支线落地）

| 维度 | 结论 | 证据 |
|---|---|---|
| 纯 C# QUIC/HTTP3/TLS 传输栈 | **已在 `full-QUIC/HTTP3/TLS` 支线落地** | `Cybersole.Http`（`TransportMode.PureNetClient`：`Crypto` + `MlKem768` + `X509` 121 根证书 + `Profiles` 82/68 预设 + `Tls` 1.2/1.3 + `Quic` v1 + `Http3`/QPACK + `ProtocolRacer`/`OriginPool`/`TlsClientCache`），全量套件与 `PublishAot` 绿 |
| 浏览器宿主采用候选 | _待裁决_ | — |
| 否决理由（其余浏览器候选） | _待填_ | — |
| 生效轮次 | _待填_ | — |

> 浏览器宿主裁决前先把第 2 节第 4–6 维的**实测数据**补齐（尤其 AOT COM/Interop 与并发内存曲线）；没有数据的裁决按 `Unknown` 记，不许拍脑袋。

## 4. 工程落位清单

1. **离线指纹基准与 Pure C# 预设**：已完成 —— `ProfileRegistry`（82 槽位 / 84 键 / 68 条 `ClientHelloSpec` / `ChromeQuicSpecs` `chrome_148_quic` / `chrome_150` 等）已落地；
2. **`Cybersole.Http/TlsProfile.cs` 扩展**：已完成 —— 新增 `TransportMode.PureNetClient = 4`，保留 `SChannel` 默认路径与 `OwnTls` 兼容性；
3. **纯 C# TLS 1.2/1.3 + H2/H1.1 + Dialers 对位**：已完成 —— `TlsHandshakeEngine` / `TlsStream` / `Http2Connection` / `Http1Connection` / `ProtocolRacer` / `OriginPool` / `TlsClientCache` 接入 `NetClient` 并通过本地真实回环与第三方 BouncyCastle TLS 1.3 互通测试；
4. **纯 C# QUIC v1 / QPACK / HTTP/3 真实握手栈**：已完成 —— `QuicConnection` / `QuicLossRecovery` / `Socks5UdpTransport` / `QpackCodec` / `Http3Connection` 通过 RFC 9000/9001/9002/9204/9114 回环全双工并发压测；
5. **浏览器引擎适配层（待裁决后实施）**：`Kasada` 浏览器求解、`CustomBrowser.Autofill` 与 ②-A 的 JS 执行分支统一走选定浏览器宿主。

## 5. 与 ②-A 的接口

②-A 的下列分支**依赖本 ADR 的第 4 步**（需要 JS 执行或浏览器环境）：

- Cloudflare Turnstile / 挑战页执行；
- hCaptcha（Stripe `captcha_vendor_name`）
- Vercel `request-challenge` 的进程内求解委托；
- BotDeflector 图标点选的坐标解析（需要渲染）。

在此之前，这些分支可以先实现**协议侧**（请求装配、令牌回写、状态机），把 JS 执行留成注入点并标 `Unknown`。
