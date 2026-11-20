# 新会话的 goal（2026-11-20 Phase 1 + Phase 2 收口交接版，可直接粘贴）

> 用法：新会话里用 `/goal`（或 `create_goal`）创建下面「▣ goal 原文」这段；更细的执行细则放在下半节按需查阅，完整文件路由、当前进度与剩余四层问题见 `docs/HANDOFF_PROMPT_antigravity.md` 与 `docs/REMAINING_REPLICATION_ROADMAP.md`。

---

## ▣ goal 原文（建议）

```
把 Cybersole.exe 5.18.32（.NET 10 NativeAOT，无 IL）在 D:\projects\cyber-reverse\replica 里做成功能 1:1 复刻件：
函数数量对等、每个函数功能相等、效率相近；命名可不同，不要求字节级相同。根路径 D:\projects\cyber-reverse。

当前基线（2026-11-20，main 4da6712）：Phase 1（R1300 8/8 本地缺口）与 Phase 2（Waves 2A–2D：Mail-OTP 接线、Unzer/Cardinal/Checkout.com/便利店、Shopify-Topps/Funko、Cybersole.Http 伴生组件）已全部落地并重发布 NativeAOT 产物（state: current）。

最高优先级（YG R757 明令，不可倒置）：
① 各站 checkout flow（Cybersole.Stores\Flows）
→ ② 客户端挑战与校验层（支付 3DS/Stripe/Unzer/Cardinal/Checkout.com · 客户端检测，严禁实现任何反爬传感器伪造或验证码绕过执行）
→ ③ 请求与传输层（NetClient / Http2 / HTTP3 / TLS 指纹 / AngleSharp）
→ ④ 其余（含 UI 形状收口、MonitorView 命令语义），只在 ①–③ 核心项结案或卡外部条件时推进。
（注：AuthWindow/LicenseControl（R702）与一切反爬传感器伪造/自动化验证码绕过执行均属严格 OUT_OF_SCOPE，严禁实现。）

方法优先级（不可倒置）：先抄 seep-reverse-lab（D:\projects\seep-reverse-lab 的 MANUAL\Tool\skill），
再抄 rea（D:\projects\rea）与仓库 analysis\ 现成脚本，都不覆盖才自己写，且须在文件头注明"为什么现有不够用"。
反编译是主参照，GUI（CUA）只用于消歧与定位。
NativeAOT 反编译铁律：冻结字符串布局为 [MethodTable*:8][Length:4][UTF-16 chars]，ida.py str 返回 chars_va，
代码引用指向对象头 obj_va = chars_va - 12！必须对 chars_va - 12 查 xrefs_to 或跑 analysis\disp32_scan_any.py
→ analysis\site_to_func.py → IDA Hex-Rays 反编译 + analysis\names_at.py 解码 &off_146xxxxxx，严禁对 chars_va 直查得 0 就判不可得。

每轮固定循环，不允许空转或用静态台账充数：
① 从 docs\PROGRESS_AND_GAP.md 与 docs\REMAINING_REPLICATION_ROADMAP.md 按 ①→②→③ 取一条「本机可做」核心未结案项（禁止编造 External Blocked 项，禁止实现 Out of Scope 项；先跑 python tools\where_is.py 查现有实现）；
② 用 NativeAOT 四步反编译链（chars_va - 12 → 引用点 → 函数 → Hex-Rays + names_at.py）取得真实控制流与字段证据；
③ 落可执行运行时实现（先 python tools\snapshot.py；整块锚点替换，禁止按行号手术；严禁往 replica\src\ 新增 *Gaps/*Wiring/*Witness 等静态审计台账类）；
④ 用工具复算验证（相关 xunit 用例 + python tools\metrics_report.py，必要时全量；变更到运行时代码后重跑 mutation-check.py 与 NativeAOT 发布验证）；
⑤ 更新 docs\METRICS.md（生成，不手写）、docs\PROGRESS_AND_GAP.md 与 docs\HANDOFF.md，写清"改了什么 → 哪条命令验证 → 数字怎么变 → 还剩什么"。

证据纪律（违反即结论作废）：
Observation 只能来自工具引用的证据（含反编译 + names_at.py 解码常量）；推理标 Inference + 置信度 + 备择解释；
覆盖不全/能力不支持/证据冲突一律显式 Unknown，并写清缺哪类证据；结构对等 ≠ 行为对等；
复刻件自己写出的 settings/tasks/solvers/checkoutHistory 不得当实机证据；
%APPDATA%\Cybersole 与 %LOCALAPPDATA%\Cybersole 只读。
数字只有一个来源：docs\METRICS.md（由 python tools\metrics_report.py 生成），任何文档不得硬编码当前度量值。

完成判据（全部满足才算完成，逐条给证据）：
a) 类型级缺口 → 0、类型缺失 → 0（不可得写 Unknown + 缺什么；范围外引 R702 裁决）；名字级缺口全部三分类结案；
b) 剩余仅不可得文案且每条写明原因；
c) 产物级对照报告可复算（原版 target\Cybersole.exe ↔ 复刻件 .publish-aot 产物）；
d) claim 表每条都有 authority（tool-evidence / manual-from-command / unknown）+ 命令 + gap_reason；
e) 全量套件绿 + 变异测试全部 fired（条数以 python tools\mutation-check.py 输出的 running N of N 为准） + 全部文档数字来自 METRICS.md；
f) 核心覆盖可复算：站点流程、支付挑战、风控与 captcha 清单从二进制取证并对账，核心可执行逻辑逐项落地，真卡外部条件者写明原因。

内存纪律：available < 2 GB 只用 -m:1 跑相关用例；< 1 GB 停止构建并先腾内存。
只有两类事可以停下来等 YG：原版有效登录凭据/实机抓包/商业引擎拍板；宿主/MCP 环境需人工重启或点授权。其它一切自行解决。
```

---

## 建 goal 之前先确认的四件事（当前基线检查）

| # | 检查 | 命令 | 期望 |
|---|---|---|---|
| 1 | 工作区状态清楚 | `git status --short ; git log --oneline -5` | 清楚是否有并行会话未提交文件，绝不覆盖他人改动 |
| 2 | IDA 已就绪 | `python analysis\ida.py health` | `status: ok` 且 `hexrays_ready: true`（未就绪先跑 `ida-mcp-doctor.ps1` + CUA 清模态框） |
| 3 | 度量快照一键可刷且对照成立 | `cd replica; python tools\metrics_report.py --skip-tests` | 全部 `exit 0`，`vendor: controls ok` 为 `True`（未开 IDA 时守卫会 `exit 2` 拒写假零） |
| 4 | 核心取件队列明确 | 读 `docs\PROGRESS_AND_GAP.md` 与 `docs\REMAINING_REPLICATION_ROADMAP.md` | 从「一、本机静态深化」（店铺长尾 / 支付 `Unknown` 子分支 / 传输与 DOM / `C7c`）取件，严禁碰 Out of Scope 或编造 External Blocked |

四项都成立 → 启动新一轮或建 goal。

## 为什么这样设计（R434 立规背景 + 2026-11-18 路线纠偏）

| 阶段 | 解决了什么问题 | 怎么落地的 |
|---|---|---|
| R434 结构化改造 | 早期靠感觉评"60%"、每轮随机换话题、手抄数字漂移 | 固定五步循环 + Observation/Inference/Unknown 三级证据 + `docs/METRICS.md` 单一数字源 + a–f 判据 |
| R702 定位突破与范围裁决 | NativeAOT 字符串直查 xref 为 0、登录许可页耗时 | 解明冻结字符串头在 `chars_va - 12`，建成 `disp32_scan_any.py` → `site_to_func.py` → `names_at.py`；裁决 `AuthWindow`/`LicenseControl` 范围外不做 |
| R757 优先级扭转（YG 明令） | 过度消耗轮次在 UI 细节 | 明令先做各站自动下单与风控核心能力，UI 延后 |
| **2026-11-18 路线纠偏** | R1040–R1075 因压缩失忆丢了 `-12` 定位链、仍用 UI `BINDING_BACKLOG.md` 当循环入口、往 `replica/src/` 塞静态台账类凑指标 | ① 循环入口切回核心能力队列；② 恢复 `chars_va - 12` 反编译主航道；③ 立产品代码红线禁往 `src/` 写审计台账；④ 给 IDA 覆盖率生成器补 `controls ok` 非零退出守卫 |

---

## 每轮的执行细则（agent 按需查这一段）

### 开工前（只做一次）

1. 按 `docs\HANDOFF_PROMPT_antigravity.md` 的顺序表读路由文档。
2. 确认 IDA 在线（`python analysis\ida.py health` → `status: ok`）；若未起则跑 `ida-mcp-doctor.ps1` 并用 CUA 点掉模态框，直到「再读一次窗口没有对话框」。
3. 在 IDA 在线前提下跑 `python tools\metrics_report.py --skip-tests` 刷新基线。

### 每轮收尾模板

```
改了什么：
验证命令与输出：
数字变化：<度量> 旧 → 新
证据等级：Observation / Inference / Unknown 各是什么
还剩什么：
```

### 什么时候该写 Unknown 而不是硬写实现

- 先走完 `chars_va - 12` → `disp32_scan_any.py` → `site_to_func.py` → Hex-Rays + `names_at.py` 仍确认逻辑由服务端（如 `api.cybersole.io`）下发或需有效登录凭据才能观测 → 记 Unknown，写清缺哪类证据；
- **绝不允许**还没减 12 查对象头 xref 就草率标「无 xref 不可得」；
- 两个版本（5.18.32 / 5.18.35）行为不一致 → 记 Unknown，写明以 5.18.32 为准。

### 什么时候用只读读数器（不加载 skill）

| 需求 | 命令 |
|---|---|
| 新二进制/新版本先分诊（20 秒，纯只读） | `D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_triage.py <exe>` |
| 两版之间节/资源层面变了什么 | `D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_diff.py <A> <B>` |

`exe-reverse` 的 **skill 注册已停用**（`.dsh\skills-disabled\`）：它的框架是"打补丁让程序还能跑"，与本任务相反；脚本可用，框架不采用。

### 已知可用来交叉验证的输入

| 输入 | 用处 |
|---|---|
| `target\Cybersole.exe`（5.18.32，IDB 基于它） | **主参照** |
| `target-alt\Cybersole-5.18.35.exe` | 对照物：两版只差三个小版本，用版本对比反推结构变化 |
| `analysis\ida.py str` + `analysis\disp32_scan_any.py` + `analysis\names_at.py` | 全量字符串查询与 NativeAOT 字符串→函数→语义定位还原链 |
| `analysis\pe_strings.txt` + `docs\xaml_bindings.json` | 正向速查（注意 `pe_strings.txt` 是抽样，反向结论必须走 `ida.py str`） |
| `replica\docs\GUI_BASELINE.md` | 十次 GUI 实测，GUI 侧的唯一可信记录 |

---

## R757 优先级修正（YG 明令，全局生效）

> 「ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来」

**取件顺序固定为：**

1. **核心 —— 站点 checkout flow 的覆盖与行为**（`Cybersole.Stores.Flows`）
2. **核心 —— 客户端挑战与校验层**（支付 3DS/Stripe · Kasada · Cloudflare · DataDome · PerimeterX · Queue-it · 各类 captcha）
3. **核心 —— 请求与传输层**（`BouncyHttpClient` / `Http2` / `Tls12Client` / `BrowserIdentity` / `ChromiumStealth`）
4. 其余（含 UI 文案与布局、`BINDING_BACKLOG.md`）**降为收尾项**，只在核心无进展时做

**判据 a–f 与全量测试/变异测试纪律不变；`replica/src/` 只准写可执行产品代码，禁写静态审计台账类。**
