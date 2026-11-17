# 交接提示词 · Antigravity 版（2026-11-18 路线纠偏版）

> **怎么用**：在 Antigravity 里选项目 `cyber-reverse`（工作区 `D:\projects\cyber-reverse`），新对话，
> 把下面 `---` 之间**整段**粘进去，然后让它自己跑（或每轮手动续）。
> 这份文件是**路由与作战纪律**，不是静态摘要 —— 数字与结论一律以工具与对应文档的当前输出为准。

---

## 你是谁、要干什么

你在接一个**已跑过千轮的逆向复刻项目**。任务：把 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT，
无 IL**）在 `D:\projects\cyber-reverse\replica\` 里做成**功能 1:1 复刻件**（复刻件用 .NET 8 + Avalonia，
框架不必跟随原版）：函数数量对等、每个函数功能相等、效率相近；**命名可以不同，不要求字节级相同**。

**最高优先级（YG 2026-11-16 / R757 明令，严禁倒置）**：
**① 各站结账流程（`Cybersole.Stores\Flows`）→ ② 客户端挑战与校验层（支付 3DS/Stripe · Kasada · Cloudflare · DataDome · PerimeterX · Queue-it · 各家 Captcha 驱动）→ ③ 请求与传输层（`Cybersole.Http`）→ ④ 其余（含 UI 绑定、文案与布局）彻底冻结在最后，只在 ①–③ 核心项全部结案或均卡外部凭据/裁决时才做。**

现在的位置：`replica` 能构建、全量测试套件绿、UI 绑定类指标大半已收口；**真正未完成的是核心可执行能力**（如 Nike `checkouts/v3` 真实请求体、PayPal 3DS / Stripe 支付挑战状态机、Kasada 进程内 Jint 主路与 `SolveAsync` 算法还原、6 类 Captcha 驱动对位），而不是 UI 绑定表或静态记账枚举。

## 开工前：按这个顺序读，别跳

数字与结论**全部以文件当前内容为准**，不要从本提示词推断动态数值。

| 顺序 | 读什么 | 它回答什么 | 别读哪部分 |
|---|---|---|---|
| 1 | `AGENTS.md`（仓库根） | 任务本体、方法论优先级、证据规则、NativeAOT `chars_va - 12` 铁律、产品代码红线。**Antigravity 会自动把它当规则加载** | — |
| 2 | `docs/GOAL.md` | goal 原文、每轮固定五步循环、完成判据 a–f、内存纪律 | 「为什么这样改」那节是早期历史讨论，可跳 |
| 3 | `docs/METRICS.md` | **唯一数字源**（生成物，带时间戳与逐条命令） | 里面的长输出块只有在你怀疑某个数时才细看 |
| 4 | `replica/docs/CORE_COVERAGE.md` · `replica/docs/PAYMENT_CHALLENGES.md` · `docs/KASADA/09-inventory.md` · `replica/docs/CAPTCHA_COVERAGE.md` | **每轮的核心取件源**：各站 Flow 占位步骤、支付挑战入口、Kasada 能力矩阵、Captcha 家族缺口 | 生成物头部直接看表，不要手改生成物 |
| 5 | `docs/BLOCKERS.md` | 近期轮次的实测记录、死路清单与踩坑过程 | 1.6 MB，**只读 `## R10xx` 标题 + 你关心的那一轮**（注：R1044/R1045「无 xref 不可得」与 R1071「反编译无语义」已被证伪纠偏，见下） |
| 6 | `docs/FORK_HANDOFF_session-02742978.md` | 上一长会话 769 轮交接：41 条 YG 原话、未结案背景与纪律沉淀 | 全文约 26 KB，注意阅读文内 **2026-11-18 纠偏注记** |

**按需再查**（不要一开始全读）：

| 需求 | 文档 |
|---|---|
| NativeAOT 冻结字符串定位原型报告 | `docs/BLOCKER_RESOLUTION_REPORT.md`（R702 验证 `chars_va - 12` → `disp32_scan_any.py` → 反编译全链路） |
| 登录/许可管理范围外裁决 | `docs/DECISION_LICENSE_OUT_OF_SCOPE.md`（R702 YG 裁决：`LicenseControl` / `AuthWindow` 属用户管理，**不做**） |
| Kasada 专题档案（01–10） | `docs/KASADA/`：`README.md` + `01-protocol.md` 至 `10-mobile.md`（含 Jint 主路、池化离屏浏览器、`HyperSolutionsSolver` 代理协议、`/tl` 回填与移动构型） |
| 厂商风控台账对账 | `replica/docs/VENDOR_COVERAGE.md` |
| 「1:1」claim 表与产物级对照 | `docs/PARITY_CLAIMS.md`、`docs/PARITY_PRODUCT.md` |
| 已接受差异与 GUI 实测基线 | `replica/docs/DEVIATIONS.md`、`replica/docs/GUI_BASELINE.md` |
| UI 绑定缺口账本（**优先级④才查**） | `replica/docs/BINDING_BACKLOG.md`（只读头部与目标节）· `docs/TYPE_PRESENCE_TRIAGE.md` |
| 更早历史（第 1–758 轮压缩摘要） | `docs/FORK_SUMMARIES_session-02742978.md`（用 grep 检索） |
| IDA 启动框清单与追加日志 | `docs/IDA_STARTUP_CHECKLIST.md` · `docs/HANDOFF.md` |

⚠ **`replica/docs/VERDICT.md` 此前停在「第 1048 轮」**，R1049–R1075 只写进了 `BLOCKERS.md` 与 `HANDOFF.md`，别把 `VERDICT.md` 旧尾部当最新状态。
⚠ 任何文档里硬编码的度量数字都只代表快照 —— 当前值只认 `docs/METRICS.md`。

## 第二件：先确认工作区与 IDA 就绪，再复算基线（顺序不可颠倒）

```powershell
cd D:\projects\cyber-reverse
git status --short ; git log --oneline -5          # 1) 先看工作区是否有并行会话未提交改动，严禁 git checkout -- .
python analysis\ida.py health                      # 2) 必须先确认 status: ok 且 hexrays_ready: true
cd replica ; python tools\metrics_report.py --skip-tests   # 3) IDA 就绪后再刷 docs\METRICS.md（约 20 秒）
```

- **为什么必须先看 IDA 再跑 `metrics_report.py`**：`vendor_coverage.py` / `payment_challenges.py` / `captcha_coverage.py` 依赖 `analysis/ida.py str` 探针。现已加上 `controls ok` 非零退出守卫（IDA 未就绪会 `exit 2` 拒绝覆盖生成物，并让 `metrics_report.py` 报非零退出），因此必须先确保 IDA 在线再刷新基线。
- 要引用「套件全绿 / 变异 fired」时跑实测：
  `python tools\metrics_report.py`（含完整套件）· `python tools\mutation-check.py`。
  **变异条数以 `running N of N` 的输出为准。**

## NativeAOT 反编译定位还原链（主航道 SOP —— 严禁再误判「无 xref 不可得」）

`.NET 10 NativeAOT` 剥离了业务函数符号名（96.87% 函数名为 `sub_*`），但**所有字符串字面量与反射元数据都原样保存在镜像里**。冻结 `System.String` 对象的内存布局为：

```
[ MethodTable* : 8 字节 ][ Length : 4 字节 ][ UTF-16 字符数据 … ]
  ↑ 对象头 obj_va = chars_va - 12 (-0x0C)      ↑ ida.py str / pe_strings 返回的 chars_va
```

`.text` 代码里的 `lea reg, [rip+disp32]` 指向的是对象头 **`obj_va = chars_va - 12`**，对 `chars_va` 直接调 `xrefs_to` 永远返回 `0`！遇到任何协议端点、状态文案或方法名，按以下**现成四步链**（均在 `analysis/` 下，禁止重复造脚本）直接定位并还原业务函数：

```powershell
# 1) 查字符串拿到 chars_va（确认 saturated: false），计算 obj_va = chars_va - 12
python analysis\ida.py str "checkouts/v3" --limit 50

# 2) 扫 .text 里的 rip+disp32 引用点（全字节滑窗，覆盖非 4 字节对齐指令，耗时 ~5 秒）
#    也可在 IDA 中直接查 xrefs_to(obj_va)
python analysis\disp32_scan_any.py 0x147053d80

# 3) 由代码引用点查 .pdata 精确函数边界
python analysis\site_to_func.py 0x140B26A5E

# 4) 用 IDA MCP 反编译该函数（拿控制流），并用 names_at.py 批量解码伪代码中的 &off_146xxxxxx / off_143xxxxxx
python analysis\names_at.py 0x146DA1778 0x146F2E098
```

**已验证样本（6 秒直达业务函数）**：
- Nike `checkouts/v3/`（`0x147053d8c - 12`）→ `sub_140B248A0`（8,935 B）
- Nike `checkout_previews/v3/`（`0x147053c94 - 12`）→ `sub_140B1DCC0`（4,617 B）
- PayPal 3DS（`0x146e93fb4 - 12`）→ `sub_141102970`（927 B）/ `sub_141105A80`（1,047 B）
- Stripe challenge（`0x146e9427c - 12`）→ `sub_140BE31F0`（1,017 B）
- HyperSolutions `/botid` & `/payload`（`-12`）→ `sub_14111CB10` / `sub_1411483E0`（已完整还原请求头契约，见 `docs/KASADA/04-remote-api-fallback.md` §2.6）

## 每轮固定循环（核心队列驱动，不许空转）

① **从下方「未结案核心队列 A」按 ①→②→③ 顺序取一条**（动手前先在 `replica\` 跑 `python tools\where_is.py <名字>` 读现有实现；**禁止拿 `BINDING_BACKLOG.md` 的 UI 项或写统计脚本充当核心轮次产出**）；
② **反编译取证**：走上面的 NativeAOT 四步链（`chars_va - 12` → 引用点 → 函数 → Hex-Rays + `names_at.py`），拿到真实控制流、请求字段与状态流转证据；
③ **落可执行实现**：先在 `replica\` 跑 `python tools\snapshot.py`；整块锚点替换，禁止按行号做手术；**只写运行时真实逻辑，严禁往 `replica/src/` 塞静态审计台账类**；
④ **验证复算**：跑相关 xunit 用例（`dotnet test --filter "..." -m:1`）+ `python tools\metrics_report.py`；
⑤ **更新记录**：`docs/METRICS.md`（生成，不手写）· `replica/docs/VERDICT.md` 新一轮 · `docs/BLOCKERS.md` + `docs/HANDOFF.md` 同步。

收尾必须写清这五行：

```
改了什么：
验证命令与输出：
数字变化：<度量> 旧 → 新
证据等级：Observation / Inference / Unknown 各是什么
还剩什么：
```

## 工具（本工作区已经配好，直接用）

MCP 服务器由工作区插件 `cyber-reverse-toolkit` 提供，工具名带前缀：

| 用途 | 服务器 | 工具名前缀 |
|---|---|---|
| 反编译 / xref（记着 `-12`）/ 字符串 / 函数清单 —— **主参照** | `ida` | `cyber-reverse-toolkit_ida_*` |
| 读窗口状态、点 IDA 模态框、GUI 消歧 —— **只做辅助** | `cua` | `cyber-reverse-toolkit_cua_*` |
| 第二意见（函数对比 / 版本对比） | `rea` | `cyber-reverse-toolkit_rea_*` |
| radare2 降级路线 + 知识库检索 | `seep` | `cyber-reverse-toolkit_seep_*` |

**IDA 就绪判据（唯一判据）**：工具调用返回真实数据，且**再读一次窗口没有对话框**。
报 `Did you run Edit -> Plugins -> MCP` = **IDA 没开或库没载入**，不是 MCP 坏了 —— 别重装、别改 JSON。端口 `13337`；报 ConnectionRefused = 端口漂移，重启该 MCP 服务器。

一键体检（含开 IDA + 点框 + 等就绪）：

```powershell
powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path "D:\projects\cyber-reverse\target\Cybersole.exe.i64"
```

输出 `VERDICT: ready` 才算可用；`HINT:` 开头那行就是下一步。

**开 IDA 的固定顺序**：打开**已有**的 `target\Cybersole.exe.i64` → 「加载现有(L)」→（若问）「Proceed with unpacked base」→（若问）「Repair」/「是(Y)」→「请稍候…」就等，别连点 →（若警告）「确定」→ 截图确认无对话框。
**这个库 1375 MB，永不重建** —— 重新分析要几小时，还会丢掉已有命名。

## 证据与产品代码纪律（违反即作废）

1. **Observation 只能来自工具引用到的证据**（含反编译控制流 + `names_at.py` 解码出的冻结对象常量）；推理标 `Inference` + 置信度 + 备择解释；覆盖不全 / 能力不支持 / 证据冲突一律显式 `Unknown` 并写清缺哪类证据。
2. **产品代码红线（Goodhart 防护）**：**严禁再往 `replica/src/` 新增任何静态逆向审计台账/缺口免责类**（如 `*Gaps`、`*Wiring`、`*Witness`、`*Coverage`、纯常量摸底表）以及仅锁死台账行数的钉子测试。分析结论与缺口台账一律归 `docs/` 或 `analysis/`；`replica/src/` **只准写可执行的运行时业务代码**（协议收发、状态机、数据模型、JS/TLS 执行）。
3. **少造轮子**：禁止用自编文本扫描器代替反编译读函数；确需新增辅助脚本前必须先确认 `seep-reverse-lab`、`rea` 与 `analysis/` 现成脚本均不覆盖，并在文件头写明原因（`AGENTS.md §1.2`）。
4. **结构对等 ≠ 行为对等**：只能证明属性存在的成员，行为记 `Unknown`，不许替它编实现。
5. **复刻件自己写出的** `settings.json` / `tasks.json` / `solvers.json` / `checkoutHistory.json` 不是实机证据（循环论证）。
6. **`%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` 只读**，永不写入。
7. **数字只有一个来源**：`docs/METRICS.md`（生成物）。任何文档不得硬编码度量当前值。
8. **判断文件编码只看字节**（`raw.decode('utf-8')`）；不要在任何文档或注释里复述乱码样本文本（`SourceEncodingTests` 会红）。
9. **写实现前先跑 `python tools\where_is.py <名字>`**（在 `replica\` 下跑），先读 implementation 组现有代码再动手。
10. **不要用 PowerShell 做源码文本手术**（易写 GBK、吞引号）；用编辑工具或 UTF-8 Python 脚本。

## 反复踩过的坑（别当新发现重演）

| 形状 | 代价与正道 |
|---|---|
| **对 `chars_va` 直接查 xref 得 0 就判「不可得」** | 忘了 NativeAOT 字符串对象头在 **`chars_va - 12`**（R1044/R1045 误判 Nike 路由不可得）。必须先减 12 再走 `xrefs_to` / `disp32_scan_any.py` |
| **只看裸伪代码 `v4..v54` 就判「反编译无语义」** | 伪代码里的 `&off_146xxxxxx` 就是冻结字符串对象头，喂给 `analysis/names_at.py` 即刻还原全部业务字段与文案（R702 已验证） |
| **往 `src/` 写记账枚举凑覆盖率** | R1049–R1052 花 4 轮改 12 处测试只为给静态表补两行，运行时能力零增长。缺口说明写进 `docs/`，`src/` 只写运行时代码 |
| **拿 UI 绑定账本 `BINDING_BACKLOG.md` 当主循环入口** | 导致连续 20+ 轮核心下单与挑战处理零产出。必须由下方核心队列驱动 |
| **抽样当全量** | `analysis/pe_strings.txt` 是抽样（180,228 行 vs IDB 324,895 条）。**反向结论必须用 `analysis/ida.py str`** |
| **把 `--limit` 当总数 / 零无对照** | `analysis/ida.py str` 需看 `saturated: false` 时的 `total`；任何负结论必须附已知非零对照（如 `kpsdk`） |
| **按符号计数判断「接线还是逻辑」** | 三次全给出无区分力结果（R714/R721/R730）。直接反编译读伪代码 |

## 未结案核心队列（按执行优先级排列）

**A. 明确可做的核心项（每轮从这里取件）**

1. **[优先级① · Checkout Flow] Nike 结账路由与请求体反编译落地**：
   - `CORE_COVERAGE.md` 已通过 `chars_va - 12` 定位出 `checkouts/v3/` → `sub_140B248A0`（8,935 B）与 `checkout_previews/v3/` → `sub_140B1DCC0`（4,617 B）。
   - 动作：反编译这两个函数并用 `names_at.py` 解出请求方法、URL 拼接、JSON 字段与调用顺序，替换 `NikeFlow.cs` 中的 `not captured` 占位；随后按同法核查 `FarfetchFlow.cs` 等含占位的 Flow。
2. **[优先级② · 支付挑战层] PayPal 3DS 与 Stripe Challenge 状态机实现**：
   - 详见 `replica/docs/PAYMENT_CHALLENGES.md`。入口已定位：PayPal 3DS 双路径状态机 `sub_141102970`（927 B）/ `sub_141105A80`（1,047 B，4 态 `Submit3DS → Process3DS → Waiting3DS → Complete3DS`，9 个可观察阶段含 `2.1`）；Stripe 挑战入口 `sub_140BE31F0`（1,017 B）及 `GetStripePaymentIntent` / `CreateStripePaymentMethod` / `SubmitOrderStripe` / `ProcessOrderStripe` / `ValidateStripeIntent` / `StripeFallbackHandler`。
   - 动作：反编译还原协议并在 `Cybersole.Stores/Payments` 落成真实可执行状态机与网关调用。
3. **[优先级② · 客户端校验层] Kasada 架构顺序与本地主路对齐**：
   - `docs/KASADA/`（`01`–`10`）已通过字符串元数据与 `chars_va - 12` 反编译考证清楚：原版默认高并发主路为进程内 **Jint 4.17.0**（`DoChallenge.GenerateJavascriptToken`），池化离屏浏览器（`_offscreenHost` / `_browserSemaphore`）与远端代理转发（`HyperSolutionsSolver`，协议已在 `04 §2.6` 完整解出）为辅路/可选路；各头回填、`/tl` 重载流程与移动构型亦已在 `08-cd.md`–`10-mobile.md` 核实（且已证伪 `Sha256Hex` 归属——它属 Akamai 而非 Kasada）。
   - 复刻件现状倒置：`NikeFlow.cs` 第 1 顺位调真浏览器，第 2 顺位 `KasadaSolver.cs` 还在盲探现代构型已不存在的 `KPSDK.ct()` 导出名。
   - 动作：按 `docs/KASADA/` 已落盘的反编译结论对齐 `replica` 侧的策略优先级、头提取与状态流转。
4. **[优先级② · Captcha 驱动层] 6 类支持家族与 `CaptchaProvider.Type` 分派对齐**：
   - 详见 `replica/docs/CAPTCHA_COVERAGE.md`：对位原版支持的 6 个家族（reCAPTCHA 含 Invisible/V3/Enterprise · hCaptcha 含 Invisible/Spoof · Turnstile · GeeTest 含 V4 与本地 HTML · Castle · TrustDevice；Arkose 与 MTCaptcha 已证实为 0）在 `CaptchaSolverService` / `ThirdPartyDrivers` 中的请求载荷与 `Type` 取值。
5. **[判据 e 维护] 变异套件陈旧度清零**：
   - 在 `replica\` 跑 `python tools\mutation-check.py`，刷新 `METRICS.md` 中的 `mutation-fit: staleness`。
6. **[优先级④ · 冻结至核心结案后] UI 收尾项**：
   - 名字级真缺口仅剩 **2 条** UI 本地化标记扩展（`LocalizeFormatExtension.Value2` · `LocalizeSwitchExtension.Condition`）—— **另外两条 `AuthWindow.Logout` 与 `LicenseControl.Authenticate` 已由 YG 在 R702 裁决 `OUT_OF_SCOPE`（用户登录/许可管理不做，见 `docs/DECISION_LICENSE_OUT_OF_SCOPE.md`），严禁重做**。
   - `docs/TYPE_PRESENCE_TRIAGE.md` 中剩余非核心 UI 视图项同样排在最后。

**B. 卡外部条件（未解锁前保持 Unknown，不编造实现）**

- PopMart 7 个抽签 POST body —— 需原版登录凭据抓包或找到对应请求构造函数；
- 原版完整服务端下发站点清单（`api.cybersole.io/connect/app`）—— 需原版登录凭据；
- `HyperSolutions` / Akamai 远端服务通道是否要在复刻件配置界面暴露用户 key —— 协议见 `docs/KASADA/04-remote-api-fallback.md` §2.6，产品策略待 YG 拍板；
- `BstnFlow` 处置策略 —— 待 YG 拍板。

**C. 判据口径上的真空（须如实向 YG 报告，不许自己圆）**

- **「效率相近」尚无自动化基准命令**（goal 第一句有要求，目前无统一压测/耗时度量脚本）。
- **「每个函数功能相等」在 R1059 被降级为覆盖率计数**（`METRICS.md` 中的函数比与类型覆盖比只是体量下界，不等于语义逐函数等价，核心模块仍须靠反编译逐流程对位）。

## 只有两类事可以停下来等 YG

1. 原版**有效登录/许可凭据**（仅影响必须经服务端下发或主界面实测才能获知的局部项）。
2. **MCP / 宿主环境需要人工点击授权或重启**。

其它一切（缺依赖、缺版本、工具报错、函数定位）**自行解决**。**不许把「卡住」当借口，也不许把 Unknown 写成完成，更不许用记账代码冒充业务实现。**

---

**最后一句**：这个仓库可能同时存在其它工作会话在提交文档（例如 `docs/KASADA/`）。每次开工与提交前先跑 `git status --short` 和 `git log --oneline -3`；**只暂存你自己改过的文件，绝不 `git checkout -- .` 或覆盖他人未提交的改动**。
