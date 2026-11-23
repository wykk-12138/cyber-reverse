# 会话状态（2026-11-23 `full-QUIC/HTTP3/TLS` 支线交接态）

本文件只保留**当前工作态索引与环境基线**。历史逐轮叙述归 `docs/VERDICT.md`、`docs/HANDOFF.md`（与 git 历史），实时度量唯一事实源归 **`docs/METRICS.md`**。

## 当前状态（2026-11-23 支线 `full-QUIC/HTTP3/TLS`，`main` 锁定 `288a95e` 未修改）

**单一事实源：`docs/METRICS.md`**（`python tools/metrics_report.py` 生成，带时间戳与逐条命令）。
本文件**不再硬编码动态度量数值** —— 数字只认 `docs/METRICS.md` 当次生成输出。

| 项 | 看哪里 |
|---|---|
| **最新收口总账（Phase 1/2 + R1383）** | **`docs/PROGRESS_AND_GAP.md`** |
| **完整复现工作路线图与分流边界（②-A 已解冻）** | **`docs/REMAINING_REPLICATION_ROADMAP.md`** |
| **新会话交接导航与复制即用提示词** | **`docs/HANDOFF.md`** · **`docs/HANDOFF_PROMPT_antigravity.md`** |
| **全量度量、套件通过数与变异新鲜度** | **`docs/METRICS.md`** |
| **纯 C# QUIC/HTTP3/TLS 第三方与公网互操作实测档案** | **`docs/LIVE_NETSTACK_INTEROP.md`** |
| **原版 ↔ 复刻件模块级 PDB/IDA 函数普查** | **`docs/MODULE_FUNCTION_CENSUS.md`** |
| **异步状态机尾项 / 字符串分类 / 风控分型与 ②-A 求解施工图** | **`docs/ASYNC_TAIL.md`** · **`docs/C8_STRING_CLASSES.md`** · **`docs/VENDOR_WIRING.md` §十三 · §十四** |
| **产物级对照与「1:1」Claim 表** | `docs/PARITY_PRODUCT.md` · `docs/PARITY_CLAIMS.md` |
| **已接受差异与 UI 形状台账（冻结在 ④）** | `docs/DEVIATIONS.md` · `docs/SHAPE_GAPS.md` · `docs/BINDING_BACKLOG.md` |

- **已闭环状态（R1383 + `full-QUIC/HTTP3/TLS` 支线）**：在 Phase 1–2 与 R1382–R1383（支付网关/28 家 ACS/站点流程/GraphQL/`AngleSharp`/`ZstdSharp.Port`/`C7c`/`C8`）基础上，`full-QUIC/HTTP3/TLS` 支线已按 IDA 实证（`0x14316a46e`）完成原版 100% 纯 C# `Cybersole.Http 0.10.0` 全栈复刻：`Crypto` + `MlKem768`、`X509` + 121 嵌入式根证书 `RootCertificates.bin`、`Profiles`（82 槽 / 68 spec 含 `chrome_150`）、纯 C# TLS 1.2/1.3（HRR / ALPS `0x44CD`&`0x4469` / RFC 8879 / KeyUpdate）、`QuicConnection` v1（`Retry`/1-RTT KeyUpdate `HpKey` 不变性/DNS IPv4 一致性）+ `Http3Connection`/QPACK、`Http2Connection`（精确 `ConnectionFlow`）+ `Http1Connection`、`Dialers`、`ProtocolRacer`、`OriginPool`、`TlsClientCache` 与 `TransportMode.PureNetClient`，并通过离线 Go 1.26.2 + `quic-go@v0.61.0`（7/7）及公网真实边缘/指纹 Oracle（16/16，`InsecureSkipVerify = false`）实测验证（详情见 `docs/LIVE_NETSTACK_INTEROP.md`）；全量 NativeAOT 产物已重发布（`state: current`），全部指标、非浏览器测试套件与变异门禁绿灯（`CRITERION (d): MET`、变异 `staleness: 0`）。

- **R1384 解冻与支线分工（2026-11-23）**：风控主动求解层（Casio PoW / Stripe Sensor / ShopPay Gatekeeper / 7 家反爬求解器 · sensor 生成器 · CAPTCHA 绕过）转为 **②-A 主战场**；纯 C# QUIC/HTTP3/TLS 网络栈已在 `full-QUIC/HTTP3/TLS` 支线实现，③-A 当前仅剩**嵌入式浏览器引擎选型**（`DotNetBrowser 4.3.5.8591` vs WebView2/CEF，见 `docs/NETSTACK_ADR.md`），均不再计入 `External Blocked`。**后续会话不得据此重新冻结这两项。**

## 参照物（两个版本，别混）

| 版本 | 路径 | 用途 |
|---|---|---|
| **5.18.32** | `target/Cybersole.exe`（`target/Cybersole.exe.i64` 基于它） | **任务主目标** |
| 5.18.35 | `target-alt/Cybersole-5.18.35.exe` | 版本差分对照输入（REA `compare_application_versions` / `pe_diff.py`） |

## 数据目录（重要）

```
复刻件   %APPDATA%\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\Cybersole             （OriginalDataRoot，只读证据，永不写入）
原版安装 %LOCALAPPDATA%\Cybersole        （LocalRoot，只读）
```

守卫：`EverythingTheReplicaWritesStaysUnderItsOwnDataRoot` —— 复刻件一切可写路径必须落在自身 `DataRoot` 下，绝不写入原版目录。

## 证据可信度

| 证据 | 状态 |
|---|---|
| IDA 数据库（`analysis/ida.py str` / Hex-Rays / `names_at.py` / `.pdata`） | ✅ 全量权威（须对冻结字符串算 `chars_va - 12`） |
| 字符串池抽样（`analysis/pe_strings.txt`） | 🟡 正向可用，反向**不可**当全量否定证据 |
| 原版 `.cyb` 备份（紧凑 camelCase）与 `docs/GUI_BASELINE.md` | ✅ 可信实证 |
| `settings.json` / `tasks.json` / `solvers.json` 等复刻件输出 | ❌ 不可作为原版“实机”证据（防止循环论证） |

## 工具（`replica/tools/` 与 `analysis/`）

| 工具 | 作用 |
|---|---|
| `replica/tools/metrics_report.py` | 一键生成 `docs/METRICS.md` 并跑非慢速全量测试 |
| `replica/tools/mutation-check.py` / `mutation_report.py` | 变异测试校验与新鲜度报告 |
| `replica/tools/where_is.py` | 动手前先查 `replica/src/` 现有实现 |
| `replica/tools/snapshot.py` | 修改源码前创建恢复快照 |
| `replica/tools/vendor_coverage.py` / `core_coverage.py` | 风控与站点流程覆盖核对 |
| `replica/tools/bind_diff.py` / `bind_scope.py` / `copy_audit_report.py` / `datafiles_diff.py` | 绑定、文案与数据文件名对照 |
| `analysis/module_function_census.py` | 复刻件 PDB + 原版 IDA 模块级函数普查（生成 `docs/MODULE_FUNCTION_CENSUS.md`） |
| `analysis/disp32_scan_any.py` / `site_to_func.py` / `names_at.py` | NativeAOT 冻结字符串定位与字面量解码链 |

## 下一步推进路线

①–③ 本机可达成静态逆向与运行态重实现已在 R1383 收口。**R1384 解冻（YG 指令）**后，剩余工作分五类：

1. **②-A 主动求解层（主战场，要在 `replica/src/` 落成可执行实现）**：Casio PoW（`0x140949680`）、Stripe Sensor（`0x140959320`）、ShopPay Gatekeeper 六步链，以及 Akamai / BotDeflector / Cloudflare / DataDome / PerimeterX / Queue-it / Vercel 的主动求解器、sensor 生成器与 CAPTCHA 绕过。施工图与验收口径：`docs/VENDOR_WIRING.md` §十四；度量：`python tools/vendor_coverage.py`。
2. **③-A 嵌入式浏览器引擎选型（网络栈已在 `full-QUIC/HTTP3/TLS` 支线交付）**：`docs/NETSTACK_ADR.md` 裁决 `DotNetBrowser 4.3.5.8591` / WebView2 / CEF 宿主方案并落适配层；原版纯 C# `Cybersole.Http 0.10.0` QUIC/HTTP3/TLS 指纹全栈已由 `TransportMode.PureNetClient` 实现并通过 Go 1.26.2 + `quic-go@v0.61.0` 及公网严格 TLS/QUIC/HTTP/3 互操作实测（`docs/LIVE_NETSTACK_INTEROP.md`）。
3. **外部阻塞**：原版有效登录凭据（`/connect/app` SignalR、`Farfetch` 7 路由、`MSAL`/`RabbitMQ`/`Velopack`、B 类 UI 本地动作、含非空 `profiles` 的 `.cyb` 备份）与真实站点抓包（`inferred` 字面量、真站响应）。
4. **优先级 ④ UI 形状冻结**：`docs/SHAPE_GAPS.md`、`docs/BINDING_BACKLOG.md`。
5. **结构性非等价噪声**：`docs/REMAINING_REPLICATION_ROADMAP.md` §三。

详见 **`docs/REMAINING_REPLICATION_ROADMAP.md`** 与 **`docs/HANDOFF_PROMPT_antigravity.md`**。
