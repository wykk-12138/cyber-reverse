# 交接提示词 · Antigravity 版（2026-11-20 Phase 1 + Phase 2 收口交接版）

> **怎么用**：在 Antigravity 里选项目 `cyber-reverse`（工作区 `D:\projects\cyber-reverse`），新建对话后把下面两条 `---` 之间的**整段**复制发送即可。
> 本提示词是**接手状态总览 + 剩余问题清单 + 作战纪律**；实时动态数值一律以仓库现行工具与 `docs/METRICS.md` 为准，绝不从记忆或静态文档抄旧数字。

---

## 你是谁、当前进度与已闭环基线

你正在接手 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT，无 IL**）的功能 1:1 复刻工程（`D:\projects\cyber-reverse\replica\`，.NET 8 + Avalonia，允许内部命名不同、不要求字节级一致，追求核心业务函数与行为等价）。

**当前代码基线（`2026-11-20`，收口提交 `4da6712`、交接归档 `8372d0c`；工作区另有未提交的文本清理改动，一律以 `git status --short` 为准）**：
- **Phase 1（R1300 本机可做 8/8 缺口 + 静态定型）已全部结案**：137 条绑定描述符全归类与本地化 4 方法接入 UI、模块级 PDB + IDA 函数普查建立（`docs/MODULE_FUNCTION_CENSUS.md`）、`BotTask.Running`（`bool`）/ `BotTask.Task`（`TaskBase`）静态定型、`SHAPE_GAPS.md` 基线对账、`DATAFILES.md` 内嵌资源与只读兜底分离、Stripe 8-builder 静态派发映射、HTTP/3 与超时 / `OwnTls` 定位、`AddressModels` 接入 `DemandwareFlow`、`vendor_coverage.py` 全量 13 项覆盖。
- **Phase 2（Waves 2A–2D 核心深化）已全部落地并重发布 NativeAOT 产物（`state: current`）**：
  - Wave 2A：`MailCodeService`（`Task.WhenAny` 并发竞速 IMAP + AYCD）接入 `AppServices.Mail` → `TaskEngine` → `CheckoutContext.WaitForMailCodeAsync` 及设置校验按键（`.ConfigureAwait(true)`），彻底消除了 NativeAOT 将 `MailKit`/`MimeKit` 整块裁空的死代码孤岛；
  - Wave 2B：`UnzerGateway`（`ContinueUnzerThreeDs` / `RunUnzerThreeDsAsync`）、`CardinalThreeDs`（Centinel/CardinalTrusted/设备指纹/`StepUp`）、`CheckoutComGateway`（`api.checkout.com` 四路径并接入默认网关表）与 Shopify 便利店 / SFCC `ToysRUs_JP` 落地；
  - Wave 2C：`ShopifyFlow`（`CheckPriceLimitAppAsync`、`FindProductCdnAsync`）与 `FunkoFlow`（`CheckFanRewardState` / `SignUpFanRewards` `CrowdTwist-Register`）落地；
  - Wave 2D：`Cybersole.Http` 伴生能力 `IBody` / `LegacyJsonBody` / `LegacyJarrayBody`、`ClickHouseSink`（纯内存 `BoundedChannel` + gzip `JSONEachRow`，零本地落盘）、`HttpDebug`（`CSHD\x01`）与 `RootCertificateStore` 落地。
- **验证基准**：NativeAOT 已重新发布为 `current`，`metrics_report.py` 全量套件、`mutation-check.py`（staleness: 0）、`vendor_coverage.py`、`audit_parity_claims.py`（`CRITERION (d): MET`）与专项守卫测试在 `4da6712` 上全部绿灯。最新数字请始终查阅 `docs/METRICS.md`。

## 开工前：按这个顺序读，别跳

| 顺序 | 读什么 | 它回答什么 |
|---|---|---|
| 1 | `AGENTS.md`（仓库根） | 任务本体、方法论优先级（先 `seep-reverse-lab` / `rea`）、证据规则、NativeAOT `chars_va - 12` 铁律、产品代码红线 |
| 2 | `docs/HANDOFF.md` | 当前状态快照、完成判据 a–f 现状与机器纪律 |
| 3 | `docs/PROGRESS_AND_GAP.md` | Phase 1 + Phase 2 逐项落账、已定位 `Unknown` 子分支与 `External Blocked` 界限 |
| 4 | **`docs/REMAINING_REPLICATION_ROADMAP.md`** | **完整复现剩余工作路线图（主取件单）** |
| 5 | `docs/METRICS.md` | **唯一动态数字源**（带时间戳与可复算命令；切勿手改或在他处硬编码当前值） |
| 6 | `docs/MODULE_FUNCTION_CENSUS.md` | 原版 321,244 函数多信号 IDA 归因 vs 复刻 PDB+`.pdata` 100% 归因、子系统对比 |

**按需再查**：`docs/SHAPE_GAPS.md`（84 条 UI 形状差异）· `docs/PARITY_CLAIMS.md`（C1–C15 / C-monitor-* Claim 表）· `replica/docs/CORE_COVERAGE.md` · `replica/docs/PAYMENT_CHALLENGES.md` · `docs/KASADA/` · `docs/R508_LICENSE_GATE.md` · `docs/BLOCKERS.md`（只读关心的 `## R1xxx` 节）。

## 完整复现剩余的三类关键问题（严格分流，严禁混淆）

### 问题 1 · 本机仍可继续推进的静态逆向与工程工作（优先取件区）

1. **`Cybersole.Stores` 站点流程与支付状态机长尾深化（最大核心业务缺口）**：
   - 原版多信号归因已见 **`5,090`** 个 `Cybersole.Stores` 函数（`4.41 MiB`）vs 复刻全部 **`3,403`** 个 `.pdata` 函数（`829 KiB`）；原版店铺异步名 `103` 个（`408` 次实现）、支付/3DS 异步名 `124` 个（`195` 次实现）——覆盖面分子与剩余长尾**只认** `docs/REMAINING_REPLICATION_ROADMAP.md` §1 与 `docs/MODULE_FUNCTION_CENSUS.md`，本文不复抄、以免双重漂移。
   - **优先消解 4 处已定位但尚未穷举的静态 `Unknown` 子分支**：
     - **Unzer**：`qword_1472c65a0+8` 终态集合、`0x14094a870` 动作判定谓词；（`0x14094c210` 已在 R1301 证定**不属于 Unzer**——它是 Magento Stripe 配置端点的请求配置委托，R1302 已落成 `StripeGateway.FetchConfigurationAsync`）；
     - **Checkout.com**：`0x1408a34f0` 的**分派层已读完**（R1303：28 个发卡行 ACS 主机名 / 18 个长度分支，已落成 `AcsHosts`），尚未读的是**每个主机处理器的方法体**（逐家挑战表单字段还在那里面）；
     - **Komoju**：`0x140d98f60` 的「`[1..56]` `formUrl` 后缀」**已撤回**（R1304：它只构建 konbini 请求体，URL 取自状态机上下文）；新已解并落码的是卡支付面（`KomojuGateway`：`https://komoju.com/gpayments_offsite/auth` + `https://degica.as1.gpayments.net/api/v2/brw/info/result?transId=` + 六个冻结 browser 字段）；**仍 Unknown**：konbini 请求体的目标 URL，与卡凭证请求体的目标 URL；
     - **Topps**：`off_1449B8EB0` 是 **JSON 类型句柄而非字符串表**，那个地址从来回答不了「键名」。R1305 从镜像仍保留的反射元数据里读出了类形（`ToppsCommerceProduct` 七个属性 + 4 个列表承载名），已落成 `ToppsCdn`；**仍 Unknown** 只剩序列化的大小写（读取器按大小写不敏感匹配绕开）。
2. **UI 绑定形状与交互语义收口（优先级④，核心项结案或阻塞后再做）**：
   - `docs/SHAPE_GAPS.md` 共 `84` 条（含 `core=1`）：`39` 条需要选择模型（如 `AnalyticsView.ChangeChart`、`CaptchaProvidersView.Reorder`）、`22` 条通用名撞名项（`Delete`/`Save`/`Create` 需逐类反编译确认）、`17` 条结构差异不补、`4` 条计算属性、`1` 条真缺 `CustomBrowser.Autofill`、`1` 条弱改名；
   - `MonitorView` 3 条未定语义命令（`OpenUrl`/`LinkChange`/`Quicktask`）、`ProxyTester.Name`、`SmartActionsView.Export`、`Cybersole.Providers.IDataProvider`、`AvaloniaEdit` 与 `TaskCreatorAdvancedView`。
3. **传输层（HTTP/3、生产级自定义 TLS 指纹）与 HTML DOM 解析对位**：
   - 复刻默认生产栈为 `SocketsHttpHandler` + `SslStream`（原版 BCL `Http3Support="false"`，无 `System.Net.Quic`/`msquic`），`BouncyTls` 标注为实验传输；原版店铺侧含 Go 移植自定义网络栈（ASICS 路径使用支持 HTTP/3 的 `chrome_150`）；原版另含 `AngleSharp`（`154` 函数）做 DOM 解析。
4. **行为等价与字符串分类验收升级**：
   - 闭合 `docs/PARITY_CLAIMS.md` 中长期 `unknown` 的 `C7c`（核心函数“同输入 → HTTP 请求报文/状态转移”级行为探针）与 `C8`（字符串池按 locale/URL/报错三分类全量对账脚本）。

### 问题 2 · 必须先补齐外部条件才能推进的工作（`External Blocked`，未解锁前严禁编造）

1. **原版有效登录账号 / 许可**：抓包 `https://api.cybersole.io/connect/app`（`SignalR` `51` 函数、`35 *Dto` + `21 Remote*`）才能解锁 `FarfetchFlow` 7 条服务端下发路由与完整线上站清单；`RabbitMQ` / `MSAL`（Outlook OAuth2） / `Velopack`（`cdn.cybersole.io/releases/` 404）；主界面观察 B 类 31 条 UI 本地动作（`docs/R508_LICENSE_GATE.md`）；导入含非空 `profiles` 的原版 `.cyb` 备份以闭合 `Profile.Card` / `Username`。
2. **真实站点流量抓包（Live Capture）**：闭合 `Stores/Flows` 中 23 条 `inferred` 0 命中字面量（R1266 已证 NativeAOT 部分串逐字节不可搜）及各支付网关真机响应校验。
3. **嵌入式浏览器引擎决策**：原版使用商业授权 `DotNetBrowser 4.3.5.8591` + 外部 Chromium（对应 `DotNetBrowser.*` `653` 函数与 `Cybersole.Web.BrowserHandlers`）；当前 `CustomBrowser` 为占位窗口，需先拍板商业授权还是开源 WebView2/CEF 重构。

### 问题 3 · 不必盲目追平的“结构性非等价噪声”

- **.NET 10 NativeAOT vs .NET 8 NativeAOT** 造成的 BCL / CRT / PE 节表（`6` vs `9`）/ Brotli 导出（`39` vs `1`）差异（`docs/GOAL_VERIFICATION.md` `C2/C3/C4`）；`Metalama.Framework` 编译期织入 vs 手写通知；复刻 `.pdata` 主体是运行时与框架（`System.*` `65.83%`、`Avalonia.*` `17.82%`、NativeAOT/CRT `1.01%`，见 `docs/MODULE_FUNCTION_CENSUS.md` 模块表），`Cybersole.*` 自研合计仅 `3.17%`。**严禁把 `.pdata` 总占比追到 100% 当目标**，应始终以 `Cybersole.*` 业务函数覆盖与行为等价为准。

## 开工前检查：先确认工作区与 IDA 就绪，再复算基线

```powershell
cd D:\projects\cyber-reverse
git status --short ; git log --oneline -5          # 1) 确认工作区状态（切勿 git checkout -- . 清掉未跟踪研究文件）
python analysis\ida.py health                      # 2) 必须确认 status: ok 且 hexrays_ready: true
cd replica ; python tools\metrics_report.py --skip-tests   # 3) IDA 就绪后再刷 docs/METRICS.md
```

- **IDA 未起或报错时**：后台跑 `powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path "D:\projects\cyber-reverse\target\Cybersole.exe.i64"`，配合 `cua` 轮询检查窗口并按条件点掉模态框（「加载现有(L)」「Proceed with unpacked base」「确定」），直到**再读一次没有对话框且 `health` 返回 `ok`**。**1375 MB IDB 永不重建。**

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
- `.publish-aot` 产物中短 ASCII 结尾 UTF-16 字符串最后一个 `0x00` 可能被 .NET 8 R2R 脱水 token 折叠（如 `api.unzer.com` 在 `0x2c589b7` 实测），搜不到字面量不代表代码被裁（验证可达性看 SHA-256 差分与 PDB，`AGENTS.md` §4.5）。

## 每轮固定循环（优先级 ① → ② → ③ → ④）

1. **取件**：从 `docs/REMAINING_REPLICATION_ROADMAP.md` 第一层「本机可做」队列选一项（禁止编造 External Blocked）；动手前先在 `replica\` 跑 `python tools\where_is.py <名字>` 读现有实现。
2. **反编译取证**：严格按 NativeAOT 四步链拿控制流、URL/头/JSON 字段与状态流转实证。
3. **落可执行代码**：先在 `replica\` 跑 `python tools\snapshot.py`；整块锚点替换，禁按行号手术；**严禁往 `replica/src/` 新增任何 `*Gaps` / `*Wiring` / `*Witness` / `*Coverage` 静态台账类**；未确认子分支显式标注 `Unknown` 并写明缺失证据。
4. **全面验证**：跑相关 xunit 用例（低内存 `-m:1`）；若改动影响运行时代码，重跑 `python tools\mutation-check.py`、`python tools\metrics_report.py`、必要时重发布 `.publish-aot` 并跑 `python analysis\module_function_census.py --write-doc`。
5. **同步记录**：保持 `docs/METRICS.md` 为唯一数字源，同步更新 `docs/PROGRESS_AND_GAP.md`、`docs/REMAINING_REPLICATION_ROADMAP.md` 与 `docs/HANDOFF.md`（注意 `HandoffHeadPointerTests` 严禁在 `# 历史` 之前写死 `METRICS.md` 数值）。

收尾必须写清五要素：
```
改了什么：
验证命令与输出：
数字变化：<度量> 旧 -> 新（均引 docs/METRICS.md）
证据等级：Observation / Inference / Unknown 各是什么
还剩什么：
```

## 工程与安全硬红线（违反即作废）

1. `%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` 绝对只读，永不写入；复刻件自己写出的 JSON 不可当原版证据。
2. `SourceEncodingTests` 禁止在源码/文档/注释里写入任何乱码样本或 U+FFFD；不要用 PowerShell 改源码文本，使用编辑器工具或 UTF-8 Python。
3. `DocsConsistencyTests`、`ParityDocTests`、`DocumentNumbersAreSourcedTests`、`HandoffHeadPointerTests`、`ClaimsCoverageTests` 守卫文档一致性，改完文档务必跑一轮专项测试。
4. 内存纪律：`available < 2 GB` 构建/测试一律加 `-m:1`；`< 1 GB` 先停构建腾内存。
5. 只有外部凭据/抓包/商业引擎拍板，或宿主 MCP 需人工授权/重启时停下来向用户确认；其余工程与逆向问题自行解决。

---
