# 交接提示词 · Antigravity 版（2026-11-24 `full-QUIC/HTTP3/TLS` 支线态：纯 C# QUIC/HTTP3/TLS 已通过海外直连实测，余 ②-A + 浏览器引擎 ADR）

> **怎么用**：在 Antigravity 里选项目 `cyber-reverse`（工作区 `D:\projects\cyber-reverse`），新建对话后把下面两条 `---` 之间的**整段**复制发送即可。
> 本提示词是**接手状态总览 + 分流清单 + 作战纪律**；实时动态数值一律以 `git log --oneline -5`、仓库现行工具与 `docs/METRICS.md` 为准，绝不从记忆或静态文档抄旧数字。

> **R1384 解冻与 `full-QUIC/HTTP3/TLS` 支线记录（2026-11-24）**
>
> 1. 旧「边界 1 · 安全边界跳过项」**整块撤销**。以下项目自 R1384 起属于 **优先级 ②-A 主战场**，要落成 `replica/src/` 里可执行的运行时实现：Casio PoW（`0x140949680`）、Stripe Sensor（`0x140959320`）、ShopPay Gatekeeper 全链，以及 Akamai（SBSD/SDS）、BotDeflector、Cloudflare、DataDome、PerimeterX、Queue-it、Vercel 的**主动求解器 / sensor 生成器 / CAPTCHA 绕过**逻辑。
> 2. **网络栈已独立收口并通过海外与多代 KeyUpdate 实测，③-A 仅剩浏览器宿主选型**：经 IDA Pro 实证（`0x14316a46e`）原版 `Cybersole.Http 0.10.0` 为 **100% 纯 C# 自研**（借用 uTLS 命名如 `chrome_150`，非 Go 移植）；隔离支线 **`full-QUIC/HTTP3/TLS`**（`main` 锁定 `288a95e` 未改）已完成纯 C# TLS 1.2/1.3（含 HRR、ALPS `0x44CD`/`0x4469`、RFC 8879、`EarlyData` `0x002A` 原版对齐与 RFC 9001 §8.3 QUIC `EndOfEarlyData` 修复）、ML-KEM-768、X.509/121 根证书、82 组浏览器指纹、QUIC v1（含 Retry、KeyUpdate `"quic ku"` `HpKey` 不变性与写/读分离多代 `InitiateKeyUpdate`、DNS/IPv4 一致性）/QPACK（解码器流锁串行防溢出）/HTTP/3（3 条关键流优先）/HTTP/2/HTTP/1.1、`ProtocolRacer`/`OriginPool`/`TlsClientCache`/`TransportMode.PureNetClient` 全栈复刻，并已通过离线 Go 1.26.2 + `quic-go@v0.61.0`（8/8）、境内边缘与 `taobao.com`/`tmall.com` 多代主动 KeyUpdate（17/17）及美国东岸 IAD 海外直连公网 VPS 实测（`6f223b21` 8/8，现扩展为 11 项待 VPS 复跑，余 2 项待海外实跑公网边缘 `Unknown` 边界，见 `docs/LIVE_NETSTACK_INTEROP.md`）。③-A 当前待办仅余商业 `DotNetBrowser 4.3.5.8591` vs WebView2/CEF 选型与宿主适配（`docs/NETSTACK_ADR.md`）。
> 3. 仍然只按外部条件分流、不许编造的只剩两类：**原版有效凭据**与**真实站点抓包**（见「边界 I」）。

---

## 你是谁、当前进度与已闭环基线

你正在接手 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT，无 IL**）的功能 1:1 复刻工程（`D:\projects\cyber-reverse\replica\`，.NET 8 + Avalonia，允许内部命名不同、不要求字节级一致，追求核心业务函数与行为等价）。

**当前代码基线（`2026-11-24`，位于支线 `full-QUIC/HTTP3/TLS`，`main` 锁定 `288a95e` 未修改；开工前务必先跑 `git status --short` 与 `git log --oneline -5`）**：
- **Phase 1 + Phase 2（Waves 2A–2D）+ R1382 审计纠偏 + R1383 已完成**（继承自 `main`）：137 条描述符、模块级普查、`BotTask` 定型、`MailCodeService`、Batch 1–3C 支付与站点消歧、`AngleSharp 1.4.0`、`ZstdSharp.Port 0.8.1`、`C7c` 回环探针与 `C8` 去噪。
- **`full-QUIC/HTTP3/TLS` 支线纯 C# 网络栈已完成并全量验证**：按 IDA `0x14316a46e` 实证完整复刻原版 100% 纯 C# `Cybersole.Http 0.10.0`：`Crypto` + `MlKem768`、`X509`（`Asn1Reader` / `DerCertificate` / `CertificateVerifier` + 121 嵌入式 `RootCertificates.bin`）、`Profiles`（82 槽 / 84 键 / 68 `ClientHelloSpec` 含 `chrome_150` 与 `chrome_148_quic`）、纯 C# TLS 1.2/1.3（双 TCP/QUIC 状态机、HRR、ALPS `0x44CD`/`0x4469`、RFC 8879 Zlib/Brotli/Zstd、KeyUpdate、`EarlyData` `0x002A` 原版对齐与 RFC 9001 §8.3）、`QuicConnection` v1 + `QuicLossRecovery` + `Socks5UdpTransport`（含 Retry、1-RTT KeyUpdate `"quic ku"` `HpKey` 不变性与写/读分离多代 `InitiateKeyUpdate`、DNS IPv4 一致性）、`Http3Connection`（3 条关键单向流优先 + 解码器流锁串行防溢出）+ `QpackCodec`、`Http2Connection`（精确 `ConnectionFlow`）+ `HpackCodec` + `Http1Connection` + `Dialers`、`ProtocolRacer` / `OriginPool` / `TlsClientCache` 与 `TransportMode.PureNetClient` 接入 `NetClient`，并通过 Go 1.26.2 + `quic-go@v0.61.0`（8/8）、境内/Oracle（17/17 含 `taobao.com`/`tmall.com` 多代主动 KeyUpdate）及海外 IAD 直连公网 VPS（`6f223b21` 8/8，现扩展为 11 项待 VPS 复跑，`InsecureSkipVerify = false`）实测验证（余 2 项待海外实跑公网 `Unknown` 边界，见 `docs/LIVE_NETSTACK_INTEROP.md`）。
- **验证基准**：`Cybersole.Ui` 全量 NativeAOT 已在支线重新发布（`state: current`），`docs/METRICS.md` 全部指标、非浏览器全量 xUnit 套件与 `mutation-check`（`staleness: 0`）全绿，`audit_parity_claims.py` `CRITERION (d): MET`，编码/文档守卫全绿。最新实时数字请始终以 `docs/METRICS.md` 为准。

## 开工前：按这个顺序读，别跳

| 顺序 | 读什么 | 它回答什么 |
|---|---|---|
| 1 | `AGENTS.md`（仓库根） | 任务本体、方法论优先级（先 `seep-reverse-lab` / `rea`）、证据规则、NativeAOT `chars_va - 12` 铁律、产品代码红线 |
| 2 | `docs/HANDOFF.md` | 当前状态快照、R1383 落账记录、完成判据 a–f 现状与机器纪律 |
| 3 | `docs/PROGRESS_AND_GAP.md` | Phase 1 + Phase 2 + R1383 逐项状态、②-A 求解层议程与 `External Blocked` 界限 |
| 4 | **`docs/REMAINING_REPLICATION_ROADMAP.md`** | **四层工作进度、②-A/③-A 议程、剩余外部条件与结构性噪声说明** |
| 5 | `docs/METRICS.md` | **唯一动态数字源**（带时间戳与可复算命令；切勿手改或在他处硬编码当前值） |
| 6 | `docs/MODULE_FUNCTION_CENSUS.md` | 原版 IDA 多信号归因 vs 复刻 PDB+`.pdata` 100% 归因对比 |
| 7 | `docs/VENDOR_WIRING.md` §十三 · §十四 | §十三 = 7 家风控与 PoW/Sensor/Gatekeeper 的架构分型与地址实证；**§十四 = ②-A 主动求解层的实现目标、令牌落点与验收口径** |
| 8 | `docs/ENDPOINT_FAMILIES.md` · `replica/docs/VENDOR_COVERAGE.md` | 端点族与运行时"检测→求解→存回"接线现状（`missing` 逐族归零的度量入口） |

**按需再查**：`docs/ASYNC_TAIL.md`（异步状态机尾项统计）· `docs/C8_STRING_CLASSES.md`（C8 字符串分类比对）· `docs/SHAPE_GAPS.md`（冻结在 ④ 的 UI 形状差异）· `docs/PARITY_CLAIMS.md`（C1–C15 / C-monitor-* Claim 表）· `replica/docs/CORE_COVERAGE.md` · `docs/R508_LICENSE_GATE.md` · `docs/BLOCKERS.md`。

## 剩余工作与分流（②-A 已解冻；证据不许编造）

### 优先级 ②-A · 主动求解层（本轮主战场，允许并要求在 `replica/src/` 落地）

**范围**（八条主线，全部要出可执行实现 + 本地回环 pin 用例）：

| # | 目标 | IDA 锚点（先复核再引用） | 已知协议面 |
|---|---|---|---|
| 1 | **Casio PoW** | `0x140949680` | Magento 前置后的挑战入口；产出提交字段与 `casio.sku` 链路串联 |
| 2 | **Stripe Sensor** | `0x140959320` | `radar_options[hcaptcha_token]` 乘载槽、`challenge_response_ekey`、`client_secret`、`captcha_vendor_name` |
| 3 | **ShopPay Gatekeeper** | `/apps/gatekeeper/api/*` 族 | `bootstrap → interaction-challenge/create → render-token → gatekeeper-token → validate-gatekeeper-token → release-details` |
| 4 | **Akamai（SBSD/SDS）** | `0x1408C4180`（重试计数 + 代理轮转） | `_abck` / `bm_sz` / `bm_so` / `bm_lso` / `sbsd_o`；`akm.hypersolutions.co/v2/{sensor,sbsd,pixel}`、`forward.cybersole.io`、`new.jevi.dev/Solver/solve` |
| 5 | **BotDeflector** | 本地协议状态机 | `/icon/{get,verify}`、`/pow/{get,verify}`、`/verify-flow`；`challengeType` / `challengeToken` / `challengeFlowToken` / `botDeflectorJwtToken` / `botDeflectorVerifyEndpoint` |
| 6 | **Cloudflare** | `0x1408CDC20`、`0x1408CF700`、`0x1408EDA60` | `cf-solver.cybersole.io/v1/{warm,sessions/start}`、`cybersole-remote-solve-v1:` 前缀、`uncaptcha.io` 回退、`__cf_bm` / `cf_clearance` / `__cf_chl_tk` |
| 7 | **DataDome** | `0x1408ECEB0`（`(DD block)` 清 cookie） | `datadome.cybersole.io/sensor` + `x-api-key`、`cid` / `ddk` / `jsData` / `jsType` / `ch`、`geo.captcha-delivery.com` |
| 8 | **PerimeterX / Queue-it / Vercel** | `0x1408FACE0`、`0x1408FB420` / `0x14090A170` / `0x14091D990`、`0x14091D270` | PX：`api.parallaxsystems.io/{gen,holdcaptcha}` + 本地回环桥 + `403` & `appId`/`blockScript` + `PerimeterX-Token`；Q-it：`/spa-api/queue/*` + `452` + `queueittoken`；Vercel：`x-vercel-challenge-token`（版次 `2`）+ `_vcrcs` + `/.well-known/vercel/security/request-challenge` |

**实现规范（每族都照这个走，缺一条不算完成）**：

1. **证据先行**：先用 NativeAOT 四步链拿到「挑战入口函数 → 请求字段 → 应答字段 → 令牌落点」，地址与结论写进 `docs/VENDOR_WIRING.md` §十四；只写结论不写地址视为未完成。
2. **落位既有分派面**：`StoreFlow.SolveDetectedWallAsync`（检测 → 求解 → **存回**三件齐全才算 `Wired`）、`CloudflareStrategyRunner`、`InjectedDataDomeSensor`、`AntiBotTokens`；新类用 `*Solver` 命名放 `Cybersole.Stores/Scripts`，样板看现有 `ChromiumKasadaSolver`。动手前先 `python tools\where_is.py <名字>`。
3. **令牌落点契约**：每族写明 cookie 名 / 请求头名 / 表单字段名，并只走 `AntiBotTokens`、`RequestOptions.OverrideHeaders`、`Session.Vars` 三条既有通道——不许新造旁路键。
4. **验证口径**：每族至少三条本地回环用例（`HttpListener` / mock `HOST`）：挑战识别、求解提交、令牌回写；PoW 类必须有**已知答案向量**（challenge → nonce → score 的确定性断言）。真站流量只作离线回放样本，不当测试环境。
5. **占位符纪律**：端点写 `HOST` / `PATH` / `TOKEN` / `CHALLENGE` / `PATCH_BYTE` / `SERIAL`；真实值来自抓包时另立 Live Capture 清单，不混进代码常量。
6. **台账红线不变**：`replica/src/` 只写可执行运行时逻辑；覆盖率、缺口语义、逐族进度写进 `docs/`（`docs/VENDOR_WIRING.md` §十四 + `replica/docs/VENDOR_COVERAGE.md`）。
7. **完成判据**：`python replica/tools/vendor_coverage.py` 的 `missing` 逐族递减到 0 且 `controls ok=True`；每族有 pin 用例；`docs/METRICS.md` 与生成文档同步重算。

### 优先级 ③-A · 嵌入式浏览器引擎选型（纯 C# 网络栈已在 `full-QUIC/HTTP3/TLS` 支线交付）

1. **浏览器宿主裁决（`docs/NETSTACK_ADR.md`）**：商业 `DotNetBrowser 4.3.5.8591` + 外部 Chromium / WebView2 / CEF 三选一并给实测理由（判据：头与属性控制度、`PublishAot` 下的 COM/Interop 兼容、授权与再分发、每任务一 profile 的内存与并发）。
2. **纯 C# QUIC/HTTP3/TLS 指纹传输栈已落地**：`Cybersole.Http`（82 组 `ClientProfile` / `MlKem768` / 121 根证书 / TLS 1.2+1.3 含 HRR、ALPS `0x44CD`&`0x4469` 与 `EarlyData` `0x002A` 原版对齐 / QUIC v1 含 Retry、`"quic ku"` `HpKey` 不变性与写/读分离多代 `InitiateKeyUpdate` / QPACK 解码器流锁串行 / HTTP/3 关键流优先 / HTTP/2 精确 `ConnectionFlow` / HTTP/1.1 / `ProtocolRacer` / `OriginPool` / `TlsClientCache`）已通过 `TransportMode.PureNetClient` 交付并通过 NativeAOT、Go 1.26.2 + `quic-go@v0.61.0`（8/8）、境内/Oracle（17/17 含 `taobao.com`/`tmall.com` 多代主动 KeyUpdate）及海外 IAD 直连公网 VPS（`6f223b21` 8/8，`InsecureSkipVerify = false`，现扩展至 11 项待 VPS 复跑）实测，余 2 项待海外实跑公网边缘 `Unknown` 边界（实测档案见 `docs/LIVE_NETSTACK_INTEROP.md`）；特定结账站点真站对比抓包见「边界 I」。
3. 浏览器引擎路线落地后，`CustomBrowser.Autofill`、`Kasada` 浏览器求解与 ②-A 里需要 JS 执行的求解分支统一走该引擎适配层。

### 边界 I · 外部条件阻塞（未获条件前不许猜、不许编造）

1. **原版有效登录账号 / 许可**：抓包 `https://api.cybersole.io/connect/app`（SignalR）解锁 `FarfetchFlow` 7 条服务端下发路由与完整线上站清单；`RabbitMQ` / `MSAL`（Outlook OAuth2） / `Velopack`；主界面实机观察 B 类 31 条 UI 本地动作（`docs/R508_LICENSE_GATE.md`）；导入含非空 `profiles` 的原版 `.cyb` 备份以闭合 `Profile.Card` / `Username`。
2. **真实站点流量抓包（Live Capture）**：闭合 `Stores/Flows` 中 23 条 0 命中 `inferred` 字面量及运行期会话值（`x-paypal-internal-euat`、`paypal-client-metadata-id`、真站 `formUrl` 等）。

### 边界 II · 优先级 ④ 冻结项（待项目负责人拍板是否解冻）

- UI 绑定形状差异（`docs/SHAPE_GAPS.md`、`replica/docs/BINDING_BACKLOG.md`）与 `MonitorView` 3 条未定语义命令（`OpenUrl` / `LinkChange` / `Quicktask`）按 `AGENTS.md §2.5`（YG R757）保持冻结；接到明确解冻指令、或 ①–③（含 ②-A/③-A）结案后再动。

### 边界 III · 不必盲目追平的“结构性非等价噪声”

- **.NET 10 NativeAOT vs .NET 8 NativeAOT** 造成的 BCL / CRT / PE 节布局 / Brotli 导出差异（`docs/GOAL_VERIFICATION.md` `C2/C3/C4`）；`Metalama.Framework` 编译期织入 vs 手写通知；复刻 `.pdata` 主体为 `System.*` / `Avalonia.*` / CRT，详见 `docs/MODULE_FUNCTION_CENSUS.md`。**严禁把 `.pdata` 总占比追到 100% 当目标**。

## 开工前自检：先确认工作区、Artifact 与 IDA 就绪

```powershell
cd D:\projects\cyber-reverse
git status --short ; git log --oneline -5
python analysis\ida.py health                               # 若使用 IDA，确认 status: ok 且 hexrays_ready: true
python analysis\operation_gap.py                            # 核对 carried: 65 of 65 / invoked 64/65
python analysis\orphan_documents.py                         # 期望: 0 orphans
cd replica ; python tools\artifact_freshness.py             # 期望: publish artifact state: current
python tools\vendor_coverage.py                             # ②-A 的度量入口：controls ok=True + 逐族 missing
```

- **IDA 未起或报错时**：优先按 `docs/HANDOFF.md` 或后台跑 `powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path "D:\projects\cyber-reverse\target\Cybersole.exe.i64"`，配合 `cua` 点掉模态框（「加载现有(L)」「Proceed with unpacked base」「确定」），直到**再读一次没有对话框且 `health` 返回 `ok`**。**1375 MB IDB 永不重建。**

## NativeAOT 反编译定位还原链（严禁再犯「无 xref 不可得」）

`.NET 10 NativeAOT` 冻结 `System.String` 内存布局为 `[MethodTable*: 8B][Length: 4B][UTF-16 chars...]`，`ida.py str` 返回 `chars_va`，代码里的 `lea` 指向对象头 **`obj_va = chars_va - 12`（`-0x0C`）**！

```powershell
python analysis\ida.py str "<pattern>" --limit 50    # 1) 确认 saturated: false，拿到 chars_va，算 obj_va = chars_va - 12
python analysis\disp32_scan_any.py <obj_va>         # 2) 全字节滑窗扫描 .text 引用点（或直接 IDA xrefs_to(obj_va)）
python analysis\site_to_func.py <site_va>           # 3) 映射到 .pdata 精确业务函数边界
python analysis\names_at.py <off_146...>            # 4) IDA Hex-Rays 反编译函数后，批量解码伪代码中的冻结串与 MethodTable
```

**补充铁律**：
- `analysis/pe_strings.txt` 是抽样，反向结论必须走 `analysis/ida.py str`；
- `.publish-aot` 二进制中部分短字符串与字面量受 NativeAOT 折叠/表示差异影响，搜不到字面量不代表代码被裁（验证可达性看 SHA-256 差分与 PDB，`AGENTS.md` §4.5）。

## 每轮固定循环（先看新解锁条件，再按 ① → ②-A → ② → ③-A → ③ → ④ 推进）

1. **取件**：先确认用户本轮是否授予新凭据/抓包或显式指令解冻 ④；动手前在 `replica\` 跑 `python tools\where_is.py <名字>` 读现有实现。
2. **反编译取证**：涉及原版逻辑时严格按 NativeAOT 四步链拿控制流、URL/头/JSON 字段与状态流转实证；②-A 的每一条都要先有地址，再写代码。
3. **落可执行代码**：先在 `replica\` 跑 `python tools\snapshot.py`；整块锚点替换，禁按行号手术；**严禁往 `replica/src/` 新增任何 `*Gaps` / `*Wiring` / `*Witness` / `*Coverage` 静态台账类**；未确认子分支显式标注 `Unknown` 并写明缺失证据。
4. **全面验证**：跑相关 xUnit 用例（加 `-m:1`）；②-A 改动必须带本地回环 pin；若改动运行代码，重跑 `python tools\mutation-check.py`、重发布 `.publish-aot`（先 `.publish-aot-new` 成功后再原子替换）、重跑 `python tools\metrics_report.py` 与 `python analysis\module_function_census.py --write-doc`。
5. **同步记录**：保持 `docs/METRICS.md` 为唯一数字源，同步更新 `docs/PROGRESS_AND_GAP.md`、`docs/REMAINING_REPLICATION_ROADMAP.md`、`docs/VENDOR_WIRING.md` §十四、`docs/HANDOFF.md` 与 `replica/docs/SESSION_STATE.md`（注意 `HandoffHeadPointerTests` 严禁在 `# 历史` 之前写死 `METRICS.md` >100 数值）。

## 工程与安全硬红线（违反即作废）

1. `%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` 绝对只读，永不写入；复刻件自己写出的 JSON 不可当原版证据。
2. `SourceEncodingTests` 与 `scan_encoding_scope_r1301.py` 禁止在源码/文档/注释里写入任何乱码样本或 U+FFFD；不要用破坏编码的方式改源码文本。
3. `DocsConsistencyTests`、`DocumentNumbersAreSourcedTests`、`HandoffHeadPointerTests`、`ClaimsCoverageTests` 守卫文档与声明表一致性；`docs/PARITY_CLAIMS.md` 严格 6 列且单元格内严禁出现未独立成列的 `|`；改完文档务必重跑专项守卫与 `audit_parity_claims.py` / `check_claims.py` / `audit_claims.py`。
4. 内存纪律：`available < 2 GB` 构建/测试一律加 `-m:1`；`< 1 GB` 先停构建腾内存。
5. 禁 `git checkout -- .` 与 `git add -A`；不提交 IDA 日志（`Hook.log`/`IDAHook.log`）与 `__pycache__`。
6. **②-A 的证据纪律**：求解器的一切行为断言都必须能追到「地址 + 本地回环用例」；复刻件自己的输出、自己造的回放数据只算自证，不算原版证据；真站流量只作离线样本，不当测试环境。

---
