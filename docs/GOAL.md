# 新会话的 goal（可直接粘贴）

> 用法：新会话里让 agent 用 `create_goal` 创建下面「▣ goal 原文」这段；它每轮自动续跑。
> 更细的执行细则不塞进 goal（goal 会被反复读，必须短而硬），放在本文件下半节，agent 每轮按需查。

---

## ▣ goal 原文（建议）

```
把 Cybersole.exe 5.18.32（.NET 10 NativeAOT，无 IL）在 D:\projects\cyber-reverse\replica 里做成功能 1:1 复刻件：
函数数量对等、每个函数功能相等、效率相近；命名可不同，不要求字节级相同。根路径 D:\projects\cyber-reverse。

方法优先级（不可倒置）：先抄 seep-reverse-lab（D:\projects\seep-reverse-lab 的 MANUAL\Tool\skill），
再抄 rea（D:\projects\rea），都不覆盖才自己写，且须在文件头注明"为什么现有不够用"。
反编译是主参照，GUI（CUA）只用于消歧与定位。不常驻用不上的能力；缺依赖/缺版本由你侧装解决。

每轮固定循环，不允许"想起来就换目标"：
① 从 replica\docs\BINDING_BACKLOG.md 取一条未结案项（类型缺失/类型级缺口优先，其次名字级、再次截断文案）；
② 用 IDA（字符串 → xrefs → 函数 → Hex-Rays）或 rea investigate_feature 取得反编译证据；
③ 落实现（先 python tools\snapshot.py；整块锚点替换，禁止按行号手术）；
④ 用工具复算验证（python tools\metrics_report.py + 相关 xunit 用例，必要时全量）；
⑤ 更新 docs\METRICS.md（生成，不手写）与 VERDICT.md 新一轮，写清"改了什么 → 哪条命令验证 → 数字怎么变 → 还剩什么"。

证据纪律（违反即结论作废）：
Observation 只能来自工具引用的证据；推理标 Inference + 置信度 + 备择解释；
覆盖不全/能力不支持/证据冲突一律显式 Unknown，并写清缺哪类证据；
绝不把"证据不全导致的缺席"当成"行为不存在"或"行为等价"。
结构对等 ≠ 行为对等：只能证明属性存在的成员，行为必须记 Unknown。
复刻件自己写出的 settings/tasks/solvers/checkoutHistory 不得当实机证据。
%APPDATA%\Cybersole 与 %LOCALAPPDATA%\Cybersole 只读。

数字只有一个来源：docs\METRICS.md（由 python tools\metrics_report.py 生成）。
当前四项度量 = 名字级缺口 / 类型级缺口 / 类型缺失 / 成员形状差异；任何文档不得硬编码这些数字。

完成判据（全部满足才算完成，逐条给证据）：
a) 类型级缺口 → 0、类型缺失 → 0（每条若不可得则写 Unknown + 缺什么）；
   名字级缺口全部三分类结案（可做 / 结构差异 / 不可得）；
b) 剩余仅"字符串池中截断"的文案，且每条写明为何不可得；
c) 产物级对照报告可复算（原版 target\Cybersole.exe ↔ 复刻件 .publish-aot 产物）；
d) claim 表每条都有 authority（tool-evidence / manual-from-command / unknown）+ 命令 + gap_reason；
e) 全量套件绿 + 变异测试全部 fired（**条数以 `python tools\mutation-check.py` 输出的 `running N of N` 为准**，不在此写死） + 全部文档数字来自 METRICS.md。

内存纪律：available < 2 GB 只用 -m:1 跑相关用例；< 1 GB 停止构建并先腾内存。
只有两类事可以停下来等 YG：原版登录凭据；DSH 重启/开关 MCP 条目。其它一切自行解决。
```

---

## 建 goal 之前先确认的四件事（R434 之后的现状）

| # | 检查 | 命令 | 期望 |
|---|---|---|---|
| 1 | 四项度量能一键生成 | `cd replica; python tools\metrics_report.py --skip-tests` | 写出 `docs\METRICS.md`，含名字级/类型级/类型缺失/形状四项 |
| 2 | 类型缺失度量已存在 | 同上，看 `type presence` 段 | `Cybersole.Models.Input` 补完后 ABSENT 名单只剩有 Unknown 理由的 |
| 3 | 已裁决项都已落地 | `docs\R433_DECISIONS.md`、`docs\R434_DECISIONS.md` | 陈旧数字一次改齐、函数级对照走 IDA 双实例、claim 表带 authority |
| 4 | 当前待办只剩 backlog 一条有证据 | `replica\docs\BINDING_BACKLOG.md` | MonitorView 五条（其余已 Unknown 结案），之后就是判据 e |

四项都成立 → 在新会话里 `create_goal`，粘贴上面那段 goal。

## 为什么这样改（对照你上一版四点）

| 你的原版 | 问题 | 新版怎么处理 |
|---|---|---|
| 1. 配合 ida-pro mcp 反编译 + CUA 操作 cybersole 交叉验证 | 方向对，但没写"取哪条证据、什么时候才算完"，容易每轮换个话题 | 变成**每轮固定五步循环**，起点永远是 backlog 里的一条未结案项 |
| 2. 反编译为主、GUI 为辅 | 对，但没有"结论有效性"的规则 | 加进 rea 的四条证据纪律：Observation / Inference / Unknown / 不得以缺席当等价 |
| 3. 继续完成 1:1 复刻 | "1:1"没有可判定的边界，导致进度只能靠感觉（我之前自评 60% 就是拍脑袋） | 拆成 **a–e 五条完成判据**，每条都绑定一个可跑命令或一个工具产物 |
| 4. 注意内存 | 对，但没说多低算低 | 给阈值：< 2 GB 用 `-m:1`，< 1 GB 停止构建并先腾内存 |
| （新增） | 上一版没提"别自己造轮子" | 写进方法优先级 + "都不覆盖才自己写，且注明理由" |
| （新增） | 上一版没提"哪些事可以等你" | 明确**只有两类**（登录凭据、DSH 重启）——其余自行解决，避免把"卡住"当借口 |

---

## 每轮的执行细则（agent 每轮查这一段，不进 goal）

### 开工前（只做一次）

1. 读 `AGENTS.md`、`docs\REA-WORKFLOW.md`、`replica\docs\SESSION_STATE.md`、`replica\docs\METHOD.md`；
   `VERDICT.md` 只读尾部 300 行。
2. 打通三条链：`ida-mcp-doctor.ps1 -Path …` → `VERDICT: ready`；rea 用侧装 Node 起；CUA 只在需要消歧时用。
3. 复算基线：**唯一入口 `python tools\metrics_report.py`** → 生成 `docs\METRICS.md`（五个度量 + 完整套件，
   带时间戳与逐条命令）。**不要再分别手跑五个脚本再手抄数字**（R433 裁决 1）。

### 每轮收尾模板

```
改了什么：
验证命令与输出：
数字变化：<度量> 旧 → 新
证据等级：Observation / Inference / Unknown 各是什么
还剩什么：
```

### 什么时候该写 Unknown 而不是硬写实现

- 只有绑定名、没有行为线索（如 `ProxyTester.Name`）→ 记 Unknown，写"缺哪类证据能解"；
- 字符串池里被截断（`…when using the \`）→ 记 Unknown，注明"需 IDA 侧字符串或原版 UI 才能补全"；
- 两个版本（5.18.32 / 5.18.35）行为不一致 → 记 Unknown，写明以 5.18.32 为准。

### 什么时候用只读读数器（不加载 skill）

| 需求 | 命令 |
|---|---|
| 新二进制/新版本先分诊（20 秒，纯只读） | `python D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_triage.py <exe>` |
| 两版之间节/资源层面变了什么 | `python D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_diff.py <A> <B>` |

`exe-reverse` 的 **skill 注册已停用**（`.dsh\skills-disabled\`）：它的框架是"打补丁让程序还能跑"，与本任务相反；
脚本可用，框架不采用。

### 已知可用来交叉验证的两组输入

| 输入 | 用处 |
|---|---|
| `target\Cybersole.exe`（5.18.32，IDB 基于它） | 主参照 |
| `target-alt\Cybersole-5.18.35.exe` | 对照物：两版只差三个小版本，用 `compare_application_versions` 反推结构变化 |
| `analysis\pe_strings.txt` + `docs\xaml_bindings.json` | 名字/文案/绑定形状的"廉价真值" |
| `replica\docs\GUI_BASELINE.md` | 十次 GUI 实测，GUI 侧的唯一可信记录 |
