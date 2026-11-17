# 交接提示词 · Antigravity 版

> **怎么用**：在 Antigravity 里选项目 `cyber-reverse`（工作区 `D:\projects\cyber-reverse`），新对话，
> 把下面 `---` 之间**整段**粘进去，然后让它自己跑（或每轮手动续）。
> 这份文件是**路由**，不是摘要 —— 它只告诉你「去读哪份文档的哪一节」，因为把上下文抄一遍
> 只会多一个必定过期的副本。

---

## 你是谁、要干什么

你在接一个**已跑了 769 轮的逆向复刻项目**。任务：把 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT，
无 IL**）在 `D:\projects\cyber-reverse\replica\` 里做成**功能 1:1 复刻件**（复刻件用 .NET 8 + Avalonia，
框架不必跟随原版）：函数数量对等、每个函数功能相等、效率相近；**命名可以不同，不要求字节级相同**。

优先级（YG 2026-11-16 明令，不可倒置）：
**① 各站 checkout flow（`Cybersole.Stores\Flows`）→ ② 风控对抗（Kasada / Cloudflare / DataDome /
PerimeterX / Queue-it / 各家 captcha）→ ③ 请求与指纹层 → ④ 其余（含 UI 文案与布局）只在核心无进展时做。**

现在的位置：`replica` 能构建、全量套件绿、四项绑定度量里有两项已经是 0；**卡的是核心能力**（支付挑战、
captcha、Kasada 这类厂商侧对抗），不是 UI。

## 开工前：按这个顺序读，别跳

数字与结论**全部以文件为准**，不要从我这段描述里推断现状（这段描述从写下的那一刻就在过期）。

| 顺序 | 读什么 | 它回答什么 | 别读哪部分 |
|---|---|---|---|
| 1 | `AGENTS.md`（仓库根） | 任务本体、方法论优先级、证据规则、度量纪律。**Antigravity 会自动把它当规则加载** | — |
| 2 | `docs/GOAL.md` | goal 原文、每轮五步循环、完成判据 a–e、内存纪律 | 「为什么这样改」那节是历史讨论，可跳 |
| 3 | `docs/METRICS.md` | **唯一数字源**（生成物，带时间戳与逐条命令） | 里面的长输出块只有在你怀疑某个数时才细看 |
| 4 | `replica/docs/BINDING_BACKLOG.md` | **每轮从这里取一条未结案项**；同时给出「哪些缺口是平台差异、哪些是缺行为证据」 | 10,000 行，**只读头部与你要取的那一节** |
| 5 | `docs/BLOCKERS.md` | 最近 26 轮（R1049–R1075）的结论、**死路清单**、反复踩的错 | 1.6 MB，**只读 `## R10xx` 标题 + 你关心的那一轮** |
| 6 | `docs/FORK_HANDOFF_session-02742978.md` | 上一会话 769 轮的交接：41 条 YG 原话、当前状态、未结案清单、**三处口径不一致** | 全文 25 KB，值得整读 |

**按需再查**（不要一开始就读）：

| 需求 | 文档 |
|---|---|
| 更早的来龙去脉（第 1–758 轮） | `docs/FORK_SUMMARIES_session-02742978.md`（33 次自动压缩摘要全文，485 KB，用 grep 找） |
| 「1:1」到底 claim 了什么、每条 authority | `docs/PARITY_CLAIMS.md`、`docs/PARITY_PRODUCT.md` |
| 已接受的差异 | `replica/docs/DEVIATIONS.md` |
| 核心覆盖：站点流程 / 厂商 / captcha / 支付 | `replica/docs/CORE_COVERAGE.md`、`VENDOR_COVERAGE.md`、`CAPTCHA_COVERAGE.md`、`PAYMENT_CHALLENGES.md` |
| Kasada（核心第②项，最新材料） | `docs/KASADA/`：`README.md` + `01-protocol` / `02-local-jint` / `03-browser` / `04-remote-api-fallback` / `05-states` / `06-evidence`（每条结论标了 Obs / Inf / Unk） |
| GUI 侧唯一可信记录 | `replica/docs/GUI_BASELINE.md`（十次实测） |
| IDA 启动要过哪些框 | `docs/IDA_STARTUP_CHECKLIST.md` |
| 每轮追加日志 | `docs/HANDOFF.md`（append-only，与 BLOCKERS 同格式） |

⚠ **`replica/docs/VERDICT.md` 停在「第 1048 轮」**，R1049 之后没写进去。**别把它当最新读。**
⚠ 任何文档里硬编码的度量数字都已过期 —— 数字只认 `docs/METRICS.md` 的**当前生成结果**。

## 第二件：先复算基线（三条命令）

```powershell
cd D:\projects\cyber-reverse
git log --oneline -5 ; git status --porcelain          # 现在 HEAD 在哪、工作区脏不脏
cd replica ; python tools\metrics_report.py --skip-tests   # 约 2 秒，重写 docs\METRICS.md
```

- IDA 不在时 `vendor_coverage.py` 会印 `missing=0` 并 **exit 0** —— 那是假零。
  只有 `controls ok=True` 的那次输出能引用；否则先让 IDA 就绪再跑。
- 要引用「套件全绿 / 变异 fired」就先跑真的：
  `python tools\metrics_report.py`（含完整套件）· `python tools\mutation-check.py`。
  **变异条数以 `running N of N` 的输出为准，任何文档里的 36 都是那一次的记录。**

## 每轮固定循环（不许临时换目标）

① 从 `replica/docs/BINDING_BACKLOG.md` 取**一条**未结案项（按上面的优先级挑，不是按谁好做挑）；
② 取证：IDA（字符串 → xrefs → 函数 → Hex-Rays）或 rea 的 `investigate_feature` / `compare_functions`；
③ 落实现：**先 `python tools\snapshot.py`**；**整块锚点替换，禁止按行号做手术**；
④ 复算：`python tools\metrics_report.py` + 相关 xunit 用例，必要时全量；
⑤ 更新：`docs/METRICS.md`（生成，不手写）· `replica/docs/VERDICT.md` 新一轮 · `docs/BLOCKERS.md` +
`docs/HANDOFF.md` 同一条记录。

收尾必须写这五行：

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
| 反编译 / xref / 字符串 / 函数清单 —— **主参照** | `ida` | `cyber-reverse-toolkit_ida_*` |
| 读窗口状态、点 IDA 模态框、GUI 消歧 —— **只做辅助** | `cua` | `cyber-reverse-toolkit_cua_*` |
| 第二意见（函数对比 / 版本对比） | `rea` | `cyber-reverse-toolkit_rea_*` |
| radare2 降级路线 + 知识库检索 | `seep` | `cyber-reverse-toolkit_seep_*` |

**IDA 就绪判据（唯一判据）**：工具调用返回真实数据，且**再读一次窗口没有对话框**。
报 `Did you run Edit -> Plugins -> MCP` = **IDA 没开或库没载入**，不是 MCP 坏了 —— 别重装、别改
JSON。端口 `13337`；报 ConnectionRefused = 端口漂移，重启这个 MCP 服务器。

一键体检（含开 IDA + 点框 + 等就绪）：

```powershell
powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path "D:\projects\cyber-reverse\target\Cybersole.exe.i64"
```

输出 `VERDICT: ready` 才算可用；`HINT:` 开头那行就是下一步。框的处理条件见 `docs/GOAL_NEXT.txt` 末段。

**开 IDA 的固定顺序**：打开**已有**的 `target\Cybersole.exe.i64` → 「加载现有(L)」→（若问）
「Proceed with unpacked base」→（若问）「Repair」/「是(Y)」→「请稍候…」就等，别连点 →
（若警告）「确定」→ 截图确认无对话框。
**这个库 1375 MB，永不重建** —— 重新分析要几小时，还会丢掉已有命名。

## 证据纪律（违反即结论作废）

1. **Observation 只能来自工具引用到的证据**；推理标 `Inference` + 置信度 + 备择解释；
   覆盖不全 / 能力不支持 / 证据冲突一律显式 `Unknown`，并写清**缺哪类证据**。
2. **结构对等 ≠ 行为对等**：只能证明属性存在的成员，行为记 `Unknown`，不许替它编实现。
3. **复刻件自己写出的** `settings.json` / `tasks.json` / `solvers.json` / `checkoutHistory.json`
   不是实机证据（循环论证）。
4. **`%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` 只读**，永不写入。
5. **数字只有一个来源**：`docs/METRICS.md`（生成物）。任何文档不得硬编码四项度量。
6. **判断文件编码只看字节**（`raw.decode('utf-8')`）；这个控制台会把 UTF-8 中文渲染成乱码，
   别据此判「文件坏了」。也**不要在文档里复述坏字符**（有测试会红）。
7. **动手写代码之前先跑 `python tools\where_is.py <名字>`**（在 `replica\` 下跑）—— 它按
   implementation / analysis / test / doc 四组报位置。这个项目**五次**把「没有」当成结论然后自己重写了一遍，而仓里早就有。
8. **不要用 PowerShell 做源码文本手术**（会写 GBK、吞引号）。要改就写临时 `.py`，跑，删。

## 反复踩过的坑（别当新发现）

| 形状 | 代价 |
|---|---|
| **抽样当全量** —— `analysis/pe_strings.txt` 是**抽样**（9.3 MB / 180,228 行），IDA 的清单是 324,895 条 | 犯过 5 次（R816→R764→R1054→R1067→R1073/74）。**反向结论必须用 `analysis/ida.py str`**（查数据库本身） |
| **一个零没有对照就读** | `datadome` / `queue-it` 的 0 是「没有」还是「探针不对」，只有加一个已知非零的对照才分得清 |
| **计数掩盖类别** | 「7 个缺口」里 2 个真厂商、5 个根本不属于那张表。**先说 kind，数字才有意义** |
| **以为反编译能给出语义** | IDA 给控制流，给不了「这个字符串是站名还是字段名」（R1071） |
| **荒谬的中间量没当回事** | 「每函数 6 字节」比任何纪律都更早指出假设错了（R1064） |
| **按符号计数判断「接线还是逻辑」** | 三次给出无区分力的结果（R714/R721/R730）。**读伪代码** |
| **以为加一行就完事** | 往 `VendorWiring` 加一行是 **11 处联动改动**（R1050/R1051 三次回滚） |
| **把 `--limit` 当总数** | 返 4 条不等于只有 4 条。`analysis/ida.py str` 现在报 `returned` / `saturated` / `total`：**`saturated: true` 时那个数不能当总数** |

## 当前状态快照（2026-11-18 00:05 生成；**会过期，以命令输出为准**）

| 项 | 值 |
|---|---|
| HEAD | 写这份时的提交叫 `R1075`；现查 `git log --oneline -1` |
| 函数数量（`.pdata`，精确解析） | 原版 **277,120** ↔ 复刻件 **174,293** = **62.89%** |
| 可执行段体量 | 51,695,104 ↔ 28,897,792 = 55.90%（**只比体量，不说代码在干什么**） |
| 名字级缺口 | real gap **4** / missing **16** |
| 类型级缺口 | **0** |
| 类型缺失（ABSENT） | **15**（需逐条分类 RENAMED / UNIMPLEMENTED，见 `docs/TYPE_PRESENCE_TRIAGE.md`） |
| 成员形状差异 | **94**（core 17，其余多在 UI 层） |
| 文案缺口 | **0**（649 键 / 20 区） |
| 完整套件 | **2258 通过 / 0 失败 / 0 跳过** |
| 变异套件 | 36/36 fired，但 **staleness 0:24:34**（`business_types.py` 在那次之后被改过）⇒ 引用前先重跑 |
| 厂商缺口 | 5 条已定位：Stripe challenge · PayPal 3DS · captcha · proof of work · checkpoint |
| `.pdata` 上界 | 原版有 156,590 个函数落到 `0x1C00000` 以上，复刻件 **0** |

## 未结案（按能不能做分）

**A. 明确可做**

1. **支付层两个挑战**（证据齐、实现缺）：PayPal 3DS（9 条文案 `(1)(2)(2.1)(3)…(8)` + 4 态状态机
   `Submit3DS · Process3DS · Waiting3DS · Complete3DS` + 2 个 solver）；Stripe challenge
   （`SubmitOrderStripe · ProcessOrderStripe · GetStripePaymentIntent · CreateStripePaymentMethod ·
   SubmitStripeOrder · ValidateStripeIntent · SetStripePayment · StripeFallbackHandler`）。
   详见 `replica/docs/PAYMENT_CHALLENGES.md`。
2. **captcha 层**（已枚举、未实现）：Recaptcha（Invisible/V3/Enterprise）· HCaptcha（Invisible/Spoof）·
   Turnstile · Geetest（V4 / 本地 html 自解）· Castle/TrustDevice；**明确为零**：funcaptcha/arkose、mtcaptcha。
   见 `replica/docs/CAPTCHA_COVERAGE.md`。
3. **15 个 ABSENT 类型**逐条分类 RENAMED / UNIMPLEMENTED。
4. **4 条名字级真缺口**（`LocalizeFormatExtension.Value2` · `LocalizeSwitchExtension.Condition` ·
   `AuthWindow.Logout` · `LicenseControl.Authenticate`）：先判定是不是原生实现。
5. **变异 staleness 清零**：`python tools\mutation-check.py`。
6. **Kasada**：`docs/KASADA/README.md` 里有四条路 + 一套状态机；复刻件侧有没有对应实现要先查
   `where_is.py kpsdk` / `VendorWiring`。

**B. 卡外部条件**

- PopMart 7 个抽签 POST body —— 需要**原版登录凭据**（YG 才有）
- Kasada / Akamai **第三方 solver** 要不要做 —— 需 YG 定（复刻件侧目前没有 solver 类）
- `CloudflareSolver.Type` 的取值 · queue-it softblock 协议 —— 只有文案，值/协议 Unknown
- `BstnFlow` 的处置 —— 需 YG 拍板

**C. 判据口径上的真空（要主动报给 YG，不许自己圆）**

- **「效率相近」从未被任何命令度量过**（goal 第一句）。
- **「每个函数功能相等」在 R1059 被实质降级**成「可数的下界」（类型覆盖 89.3% vs 函数 62.9%）。
  这是判据的降级，**不是完成度**。

## 只有两类事可以停下来等 YG

1. 原版**登录凭据**（拿不到就进不去主界面，那些局部行为只能记 Unknown）。
2. **MCP / 环境需要人动手**：DSH 重启、开关 MCP 条目；Antigravity 侧第一次用时若弹 MCP 授权，
   那是要人点一下的。

其它一切（缺依赖、缺版本、工具报错、脚本写不出来）**自己解决**：侧装、换路线、查 `BLOCKERS.md`。
**不许把「卡住」当借口，也不许为了让数字好看而把 Unknown 写成完成。**

---

**最后一句**：这个项目最贵的错误不是想不出办法，是**在同一条死路上换姿势**。
动手前先看 `docs/BLOCKERS.md` 的轮次标题和 `docs/FORK_HANDOFF_session-02742978.md` §8 的纪律沉淀。

⚠ **这个仓库可能正被另一处工作同时改**（写这份时 `docs/KASADA/` 的 01–06 是陆续落盘的，未提交）。
开工第一件事是 `git status`；**不要把别人未提交的内容覆盖掉**，也不要为了干净而 `git checkout -- .`。
