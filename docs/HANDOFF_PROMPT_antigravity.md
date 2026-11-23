# 交接提示词 · Antigravity 版（2026-11-23 R1383 静态逆向收口交接版）

> **怎么用**：在 Antigravity 里选项目 `cyber-reverse`（工作区 `D:\projects\cyber-reverse`），新建对话后把下面两条 `---` 之间的**整段**复制发送即可。
> 本提示词是**接手状态总览 + 三类边界清单 + 作战纪律**；实时动态数值一律以 `git log --oneline -5`、仓库现行工具与 `docs/METRICS.md` 为准，绝不从记忆或静态文档抄旧数字。

---

## 你是谁、当前进度与已闭环基线

你正在接手 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT，无 IL**）的功能 1:1 复刻工程（`D:\projects\cyber-reverse\replica\`，.NET 8 + Avalonia，允许内部命名不同、不要求字节级一致，追求核心业务函数与行为等价）。

**当前代码基线（`2026-11-23`，R1383 收口提交见 `git log --oneline -5`；开工前务必先跑 `git status --short`，切勿误覆盖工作区文件）**：
- **Phase 1 + Phase 2（Waves 2A–2D）+ R1382 审计纠偏 已完成**：137 条绑定描述符全归类与本地化 UI 接线、模块级 PDB/IDA 函数普查（`docs/MODULE_FUNCTION_CENSUS.md`）、`BotTask.Running`/`BotTask.Task` 静态定型、`AddressModels`、`MailCodeService`（IMAP + AYCD 并发竞速）、`UnzerGateway` / `CardinalThreeDs` / `CheckoutComGateway` / `Komoju` / `WebCVS`、`IBody` / `ClickHouseSink` / `HttpDebug` / `RootCertificateStore`，以及 R1382 对全仓门禁、GraphQL 文档、`.snapshots` 噪声的真实性纠偏。
- **R1383（IDA Pro 静态逆向与运行态重实现：Batches 1–3）已完成并全量验证**：
  - **Batch 1（支付网关扩展）**：`StripeGateway`、`CommerceHubGateway`（`FunkoFlow`）、`GmoGateway`（`ToysRUsJpFlow`）、`KomojuGateway` 与 `RequestOptions.Properties` / `OverrideHeaders`。
  - **Batch 2（Checkout.com 28 家发卡行 ACS 处理器）**：按 IDA `0x1408a34f0` 实现 19 个无头 ACS 簇与 `20_fallback`（`CheckoutComAcsHandlers.cs`）并接入 `CheckoutComGateway`。
  - **Batch 3C（协议/DOM + 站点归属消歧 + GraphQL/安全异步尾）**：
    - 引入 **`AngleSharp 1.4.0`**（`HtmlFormDom.cs` 替代支付与流程 HTML 正则）与 **`ZstdSharp.Port 0.8.1`**（`ContentEncodingCodec.cs` 逆序多编码解码/出站压缩），对齐 `NetClient` / `BouncyHttpClient` / `BouncyH2Client` / `RedirectPolicy`；
    - 通过 IDA 主工厂实证消除归属误判：确认 `0x14088A9E0` 属 **`JDGroup`/`FINL`**、`0x140E49000..0x140E63000` 为唯一 **`Warhammer`** CT 模块，分别接入 `JdSportsFlow` 与 `WarhammerFlow`（保留既有 `WarhammerGraphQlTests` pins）；
    - 补齐 `CasioFlow`（Magento 前置 + Stripe/Adyen/Unzer/Square 4 条非 PoW 网关）、Panini（`onepanini` 8 步 + PPCP + `BraintreeClientToken`/`BraintreeTokenizeCard`）、`JohnLewisFlow`、`ScheelsFlow`（保留 `/api/search` pin）、`ShopifyFlow` 缺失操作及 `Nike`/`PopMart`/`Saucony`/`StoreFlow` 安全异步尾（`operation_gap.py` 达成 64/65 生产调用，仅余原版 0 调用死常量 `cartCreate`；无人写 `Session.Vars` 旁路键降至 14）。
  - **优先级 ② 只读被动审计与 `C7c`/`C8` 验收仪器**：`docs/VENDOR_WIRING.md` §十三完成 7 家未接线风控与 PoW/Sensor 的只读被动架构分型；新增 `C7cBehavioralParityTests` 与 `NetClientProtocolParityTests` 本地回环行为探针；完成 `c8_string_class_compare.py` 去噪（覆盖 `Cybersole.Locales.en.json` 全量顶层前缀）。
- **验证基准**：`Cybersole.Ui` 全量 NativeAOT 已重新发布（`state: current`），`docs/METRICS.md` 全部 16 项指标与非浏览器全量 xUnit 套件全绿，`mutation_report` `staleness: 0`，`audit_parity_claims.py` `CRITERION (d): MET`，编码/文档守卫全绿。最新实时数字请始终以 `docs/METRICS.md` 为准。

## 开工前：按这个顺序读，别跳

| 顺序 | 读什么 | 它回答什么 |
|---|---|---|
| 1 | `AGENTS.md`（仓库根） | 任务本体、方法论优先级（先 `seep-reverse-lab` / `rea`）、证据规则、NativeAOT `chars_va - 12` 铁律、产品代码红线 |
| 2 | `docs/HANDOFF.md` | 当前状态快照、R1383 落账记录、完成判据 a–f 现状与机器纪律 |
| 3 | `docs/PROGRESS_AND_GAP.md` | Phase 1 + Phase 2 + R1383 逐项状态、安全跳过边界与 `External Blocked` 界限 |
| 4 | **`docs/REMAINING_REPLICATION_ROADMAP.md`** | **四层工作进度、剩余阻塞条件路线与结构性噪声说明** |
| 5 | `docs/METRICS.md` | **唯一动态数字源**（带时间戳与可复算命令；切勿手改或在他处硬编码当前值） |
| 6 | `docs/MODULE_FUNCTION_CENSUS.md` | 原版 IDA 多信号归因 vs 复刻 PDB+`.pdata` 100% 归因对比 |
| 7 | `docs/VENDOR_WIRING.md` §十三 | 7 家未接线风控站点的只读被动分型与安全禁区边界 |

**按需再查**：`docs/ASYNC_TAIL.md`（异步状态机尾项统计）· `docs/C8_STRING_CLASSES.md`（C8 字符串分类比对）· `docs/SHAPE_GAPS.md`（冻结在 ④ 的 UI 形状差异）· `docs/PARITY_CLAIMS.md`（C1–C15 / C-monitor-* Claim 表）· `replica/docs/CORE_COVERAGE.md` · `replica/docs/VENDOR_COVERAGE.md` · `docs/R508_LICENSE_GATE.md` · `docs/BLOCKERS.md`。

## 剩余问题与严格分流边界（严禁越界或编造）

### 边界 1 · 安全边界跳过项（严禁在 `replica/src/` 实现，仅保持只读被动审计）

- Casio `0x140949680`（PoW）、`0x140959320`（Stripe Sensor）、ShopPay Gatekeeper；
- Akamai（SBSD/SDS）、BotDeflector、Cloudflare、DataDome、PerimeterX、Queue-it、Vercel 的任何主动反爬绕过、PoW 求解器、sensor 生成器或 CAPTCHA 求解代码（仅在 `docs/VENDOR_WIRING.md` §十三保留只读被动分型与安全审计记录）。

### 边界 2 · 外部阻塞工作（`External Blocked`，未获条件前严禁猜测/编造）

1. **原版有效登录账号 / 许可**：抓包 `https://api.cybersole.io/connect/app`（SignalR）解锁 `FarfetchFlow` 7 条服务端下发路由与完整线上站清单；`RabbitMQ` / `MSAL`（Outlook OAuth2） / `Velopack`；主界面实机观察 B 类 31 条 UI 本地动作（`docs/R508_LICENSE_GATE.md`）；导入含非空 `profiles` 的原版 `.cyb` 备份以闭合 `Profile.Card` / `Username`。
2. **真实站点流量抓包（Live Capture）**：闭合 `Stores/Flows` 中 23 条 0 命中 `inferred` 字面量及运行期会话值（`x-paypal-internal-euat`、`paypal-client-metadata-id`、真站 `formUrl` 等）。
3. **嵌入式浏览器与自定义网络栈决策**：商业授权 `DotNetBrowser 4.3.5.8591` + 外部 Chromium vs 开源 WebView2/CEF 方案决策；以及是否投建原版 Go 移植 `chrome_150` 自定义 QUIC/HTTP3 指纹层。

### 边界 3 · 优先级 ④ 冻结项（待项目负责人拍板是否解冻）

- UI 绑定形状差异（`docs/SHAPE_GAPS.md`、`replica/docs/BINDING_BACKLOG.md`）与 `MonitorView` 3 条未定语义命令（`OpenUrl` / `LinkChange` / `Quicktask`）目前按 `AGENTS.md §2.5`（YG R757）保持冻结；如本轮接到用户明确指令解冻 ④（或已补齐外部凭据/抓包解锁路线 B/C），再行推进。

### 边界 4 · 不必盲目追平的“结构性非等价噪声”

- **.NET 10 NativeAOT vs .NET 8 NativeAOT** 造成的 BCL / CRT / PE 节布局 / Brotli 导出差异（`docs/GOAL_VERIFICATION.md` `C2/C3/C4`）；`Metalama.Framework` 编译期织入 vs 手写通知；复刻 `.pdata` 主体为 `System.*` / `Avalonia.*` / CRT，详见 `docs/MODULE_FUNCTION_CENSUS.md`。**严禁把 `.pdata` 总占比追到 100% 当目标**。

## 开工前自检：先确认工作区、Artifact 与 IDA 就绪

```powershell
cd D:\projects\cyber-reverse
git status --short ; git log --oneline -5
python analysis\ida.py health                               # 若使用 IDA，确认 status: ok 且 hexrays_ready: true
python analysis\operation_gap.py                            # 核对 carried: 65 of 65 / invoked 64/65
python analysis\orphan_documents.py                         # 期望: 0 orphans
cd replica ; python tools\artifact_freshness.py             # 期望: publish artifact state: current
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

## 每轮固定循环（先看新解锁条件，再按 ① → ② → ③ → ④ 推进）

1. **取件**：先确认用户本轮是否授予新凭据/抓包/引擎决策或显式指令解冻 ④（UI 形状）；动手前在 `replica\` 跑 `python tools\where_is.py <名字>` 读现有实现。
2. **反编译取证**：涉及原版逻辑时严格按 NativeAOT 四步链拿控制流、URL/头/JSON 字段与状态流转实证；反爬层仅做只读审计。
3. **落可执行代码**：先在 `replica\` 跑 `python tools\snapshot.py`；整块锚点替换，禁按行号手术；**严禁往 `replica/src/` 新增任何 `*Gaps` / `*Wiring` / `*Witness` / `*Coverage` 静态台账类**；未确认子分支显式标注 `Unknown` 并写明缺失证据。
4. **全面验证**：跑相关 xUnit 用例（加 `-m:1`，避免把网络 `Speed=Slow` 与真 Chrome 用例误混进本地快扫）；若改动运行代码，重跑 `python tools\mutation-check.py`、重发布 `.publish-aot`（先 `.publish-aot-new` 成功后再原子替换）、重跑 `python tools\metrics_report.py` 与 `python analysis\module_function_census.py --write-doc`。
5. **同步记录**：保持 `docs/METRICS.md` 为唯一数字源，同步更新 `docs/PROGRESS_AND_GAP.md`、`docs/REMAINING_REPLICATION_ROADMAP.md`、`docs/HANDOFF.md` 与 `replica/docs/SESSION_STATE.md`（注意 `HandoffHeadPointerTests` 严禁在 `# 历史` 之前写死 `METRICS.md` >100 数值）。

## 工程与安全硬红线（违反即作废）

1. `%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` 绝对只读，永不写入；复刻件自己写出的 JSON 不可当原版证据。
2. `SourceEncodingTests` 与 `scan_encoding_scope_r1301.py` 禁止在源码/文档/注释里写入任何乱码样本或 U+FFFD；不要用破坏编码的方式改源码文本。
3. `DocsConsistencyTests`、`DocumentNumbersAreSourcedTests`、`HandoffHeadPointerTests`、`ClaimsCoverageTests` 守卫文档与声明表一致性；`docs/PARITY_CLAIMS.md` 严格 6 列且单元格内严禁出现未独立成列的 `|`；改完文档务必重跑专项守卫与 `audit_parity_claims.py` / `check_claims.py` / `audit_claims.py`。
4. 内存纪律：`available < 2 GB` 构建/测试一律加 `-m:1`；`< 1 GB` 先停构建腾内存。
5. 禁 `git checkout -- .` 与 `git add -A`；不提交 IDA 日志（`Hook.log`/`IDAHook.log`）与 `__pycache__`。

---
