# 手动分叉交接 · 来源 session-02742978-75c8-40d5-85ab-e35cc8925210

> **这份文件是一次手工分叉的产物。** 来源会话的「分叉」按钮失败，所以在
> `session-6cc9c7bb…`（本会话）里直接读来源会话的存档，把上下文落成文件。
>
> - 来源存档：`C:\Users\wykk\.dsh\sessions\--D-projects-cyber-reverse--\session-02742978-75c8-40d5-85ab-e35cc8925210\session.v4.jsonl.zstd`
>   （135,546,657 字节压缩 → 57,106 行事件 / 552,980,148 字符 JSON / 769 轮 / 8,563 条 assistant 消息 / 7,837 次工具调用 / 33 次自动压缩）
> - 抽取脚本：`tools/session_peek.mjs`（结构探测）· `tools/session_project.mjs`（事件投影）· `tools/session_project2.mjs`（分层投影）
> - 摘要全档：`docs/FORK_SUMMARIES_session-02742978.md`（33 次压缩的全文，467,985 字符，覆盖第 1–758 轮）
> - 手写编年史：`docs/BLOCKERS.md`（R1047–R1074）· `docs/HANDOFF.md`（R1047–R1074）· `replica/docs/VERDICT.md`（到 R1048 为止）
> - 分叉时刻：2026-11-17 23:05 +0800（来源会话最后写入 23:02:26，goal 于 23:01:40 被 pause）

---

## 1. 来源会话是什么

| 项 | 值 |
|---|---|
| 会话 id | `session-02742978-75c8-40d5-85ab-e35cc8925210` |
| 工作目录 | `D:\projects\cyber-reverse`（与本会话相同） |
| 模型 | `deepseek-v4.1-flash`（provider `cpa`） |
| 起始 | 2026-11-14 18:17 +0800（第 1 轮：读 `docs/HANDOFF.md` 接手，YG 要求先复述目标与进度再开工） |
| 结束 | 2026-11-17 23:02（第 769 轮，goal 被 YG 暂停） |
| 用户输入 | 存档里 330 条非空 `user/message`，滤掉运行时注入（`Time sampled…` / `background job … finished` / `<system-reminder>` / `<goal_round>` / 自动 checkpoint）后是 **41 条真实 YG 输入**，散布在 769 轮里 —— 也就是说 **728 轮是 goal 自动续跑**。逐条见 §2.5 |
| goal | rev 31，最后一次操作是 **pause**（11-17 23:01:40），objective 1,820 字符（见 §2） |

**⇒ 结论：那边的「上下文」几乎全部沉淀在仓库文件里，不在对话里。** 对话只提供两样可迁移的东西：
① 每轮结尾的结论口径（`BLOCKERS.md` 已收）；② 中途踩坑的操作细节（见 §6）。

---

## 2. goal 原文（1,820 字符，逐字）

```
把 Cybersole.exe 5.18.32（.NET 10 NativeAOT，无 IL）在 D:\projects\cyber-reverse\replica 里做成功能 1:1 复刻件：
函数数量对等、每个函数功能相等、效率相近；命名可不同，不要求字节级相同。根路径 D:\projects\cyber-reverse。

核心优先（YG 2026-11-16 明令「ui先不急着复刻」）：
1 各站 checkout flow（Cybersole.Stores\Flows）→ 2 风控对抗（Kasada / Cloudflare / DataDome / PerimeterX /
Queue-it / 各家 captcha）→ 3 请求与指纹层（BouncyHttpClient / Http2 / Tls12Client / BrowserIdentity）→
4 其余（含 UI），只在核心无进展、或核心证据必须经 UI 才取得时做。

每轮：① 从 docs\METRICS.md（唯一数字源）、replica\docs\BINDING_BACKLOG.md、docs\BLOCKERS.md、
docs\HANDOFF.md 读现状（**不从本 prompt 推断现状**），取一条未结案项；② IDA 或 rea 取反编译证据；
③ 先 python tools\snapshot.py，整块锚点替换，禁按行号手术；④ python tools\metrics_report.py + 相关 xunit，
必要时全量；⑤ 更新 METRICS.md（生成）、replica\docs\VERDICT.md、BLOCKERS.md，
写清改了什么→哪条命令验证→数字怎么变→还剩什么。

方法与证据见 AGENTS.md §1/§2。要点：先抄 seep-reverse-lab 再抄 rea，都不覆盖才自写并在文件头注明理由；
反编译是主参照，CUA 只做消歧定位；Observation 只来自工具证据，推断标 Inference，覆盖不全标 Unknown；
子串计数只当地图不当判据；复刻件的 settings/tasks/solvers 不得当实机证据；
%APPDATA%\%LOCALAPPDATA%\Cybersole 只读。

IDA 每次打开（框不点掉，插件不起、13337 不监听）：后台跑
  powershell -File "D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1" -Path "<目标.i64>"
同时用 CUA 轮询：list_windows(app:"ida") → 读「请确认」类窗口 → 按条件点 → 再读，
**直到读不到对话框**（判据是"再读一次没有"，不是"点了 N 次"）。
条件：unpacked-version 警告 → **Proceed with unpacked base**；id0-not-closed → **是(Y)**；
「请稍候…」→ 等，不点；没见过的框 → 读正文再判，判完把这条补进本段。
就绪：doctor 输出 VERDICT: ready 且 mcp__ida__server_health status=ok（带 idb_path / hexrays_ready）。
报 PROXY: MISSING 或端口 REFUSED 且框已清 → 属停下等 YG。

完成判据：a) 类型级缺口、类型缺失 → 0，不可得写 Unknown+缺什么；名字级缺口三分类结案。
b) 剩余仅"字符串池截断"文案，且写明为何不可得。c) 产物级对照可复算（target\Cybersole.exe ↔ .publish-aot）。
d) claim 表每条有 authority+命令+gap_reason。e) 套件绿、变异测试全 fired、文档数字全来自 METRICS.md。
f) 核心覆盖表可复算：原版站点与风控清单从二进制取证 ↔ Registry.cs 与 Flows/Scripts 逐条对，
未覆盖的每条写为什么。

纪律：available<2GB 只用 -m:1；<1GB 停构建先腾内存。只有两类事可以停下等 YG：原版登录凭据；
DSH 重启 / 开关 MCP 条目（含 ida 代理没起）。
```

**注意 goal 第 1 句与 AGENTS §0 的口径差**：goal 说「效率相近」，AGENTS 说「命名可以不同，不要求字节级相同」——
两者不冲突，但**效率从未被度量过**（截至 R1074 没有一条命令测过效率）。这是判据外的一条真空。

---

## 2.5 YG 在来源会话里的 41 条真实输入

抽取方式：`user/message` 的 `data.content[]` 里 `type == "text"` 的块，滤掉运行时注入。下表**逐字保留**（长条截断处标 `…`），
原文可用 `tools/session_project2.mjs` 重抽。

### A. 任务与目标（改了方向的三条，字面最重要）

| 轮 | 原文 |
|---|---|
| 1 | `docs\HANDOFF.md   阅读提示词接手任务，但是接手后先不要开始执行，先回答我是否清楚任务目标已经当前进度，有不清楚的问我。` |
| **325** | **`ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来`** |
| 326 | `1.按照这个新目标，你生成一份goal目标提示词给我，我去修改  2.ida每次打开都要用cua读几次屏幕看看有没有框弹出来需要点的，每次最少两个框，这个也写进goal目标里，不然你老是忘记` |
| 327 | `放到goal里的长期loop推进的提示词怎么能写现状（现状（R757 盘过，别重复盘））？你搞清楚goal里推进的提示词应该写什么先，再给我重新生成一份` |
| 328 | `goal是每轮结束之后推进用的提示词，怎么会搞的这么长呢` |
| 273 | `把goal任务的轮次上限改成2000，刚刚报错了{goal "goal-e6ce3623-…" exhausted 256 goal rounds; increase maxGoalRounds before resuming}` |

**⇒ turn 325 是当前 goal 优先级的出处**（checkout flow → 风控 → 请求指纹 → 其余含 UI）。
**⇒ turn 327/328 是 goal 写法的出处**：goal 是**每轮推进用的提示词**，不写现状、不写轮次结论，只写「怎么干」。

### B. 裁决与否定权（YG 亲自定的）

| 轮 | 原文 |
|---|---|
| 3 | `裁决已写进 docs\R433_DECISIONS.md，按它执行。四个数我复核过：4 / 16 / 275 / 1607，你报的全对。你没有擅改数字、把待决项单列，这是对的，继续这么做。` + 五项裁决细节（陈旧数字改法、IDA 两侧对照不装 Ghidra、claim 双轨制…） |
| 4 | `选 A（结构对等 + 可观测行为 + 显式钩子），按 docs\R434_DECISIONS.md 执行。` + 四条约束 |
| 38 | `docs\R456_DECISIONS.md 查看这份文档` |
| 81 | `docs\R505_DECISIONS.md 查看裁决文档，需要去cybersole里创建account或task的话，你用cua mcp来操作` |
| 271 | `docs/BLOCKER_RESOLUTION_REPORT.md  看看这份报告，有没有什么启发` |
| 320 | `小版本更新都是个别网站的微调，不影响前端界面` |
| 273 | `好的，然后这里任务启动之后我会同步恢复goal目标任务` |

### C. 交接与文档纪律

| 轮 | 原文 |
|---|---|
| 2 | `以上问题落成文档，返回路径给我` |
| 36 | `总结一下现在的卡点` |
| 37 | `把卡点总结成文档，要包含卡点相关的上下文信息，我交给原会话agent判断` |
| 80 | `上一轮的问题总结成文档，返回给我路径` |
| **270** | **`把卡点和详细上下文信息（上下文信息通过指导agent读什么文档而不是塞到一份文档里）整理成文档，然后生成一份提示词，我让新会话agent来头脑风暴一下`** |
| 272 | `那你提的卡点现在算是解决了吗，可以继续推进目标了吗` |

**⇒ turn 270 是「上下文靠读文档、不靠塞文档」这条做法的出处** —— 本文件的结构也照它来：给路径与命令，不复制结论。

### D. 环境运维（几乎全是"内存爆了"）

| 轮 | 原文 |
|---|---|
| 67 | `又爆内存导致很多应用崩掉了，电脑重启了注意控制一下，ida-pro没开，需要你自己看一下，cybersole开了` |
| 254 | `又爆内存崩溃退出了，我重启电脑了，注意一下` |
| 259 | `“没有 git，没有版本控制——那 21 处改动无法从历史还原。”那你现在开始创建个git仓库，而且我看你没开ida-pro，你现在在干嘛` |
| 259 | `怎么老是忘记打开ida-pro要点好几个模态框呢，还有个卡着呢` |
| 319 | `内存快爆了，你保存一下进度，维护好文档，我重启电脑，顺便问下，cybersole我看一下没开，这几轮任务不需要开cybersole吗` |
| 320 | `重启了，cybersole也已经打开，之前登录授权过了，你要打开直接通过 C:\Users\wykk\AppData\Local\Cybersole\current\Cybersole.exe 即可` |
| 329 / 397 / 401 / 402 / 537 / 688 / 740 / 741 | `你先把ida-pro打开` / `保存一下任务进度，内存又爆了，要重启电脑` / `重新保存一下任务进度，刚刚忘了关goal` / `重启了` / `爆内存了重启电脑了，继续` / `继续` / `保存一下任务进度，内存爆了，要重启` / `继续，先把ida-pro拉起来` |

**⇒ 这条线说明：内存是这台机器的硬约束**（`available < 2GB` 只用 `-m:1`，`< 1GB` 停构建），
且**每次重启后 IDA 都要用 CUA 点掉对话框重新拉起** —— 这就是 goal 里那段 CUA 流程的由来。
**⇒ turn 259 是 git 仓库的由来**（此前 21 处改动无法从历史还原）。

### E. GUI 操作（CUA）

| 轮 | 原文 |
|---|---|
| 1 | `记得打开ida-pro时要用cua看看它有没有需要点击的框` |
| 81 | `怎么cybersole操作到一半就不操作了，store你要点下拉框啊` / `你要点右边的箭头啊` |
| 82 | `你决定，这个无所谓，全程你来操作` |


---

## 3. 当前状态（2026-11-17 23:0x，本会话已复算）

### 3.1 仓库

| 项 | 值 | 命令 |
|---|---|---|
| 分支 / HEAD | `main` / `e5aba08 R1074: the baseline never moved, and I read the limit as a count for the fifth time` | `git log --oneline -1` |
| 工作树 | **dirty**：`M analysis/ida.py`（R1075 未提交的改动，见 §4）· `D analysis/record_r1074.py`（临时记录脚本已删） | `git status --porcelain` |
| 本会话新增 | `tools/session_*.mjs`、本文件、`docs/FORK_SUMMARIES_session-02742978.md` | — |

### 3.2 度量（本会话 23:0x 重跑 `python tools/metrics_report.py --skip-tests`，全部 exit 0）

| 指标 | 值 |
|---|---|
| 名字级绑定缺口 | real gap **4** / missing **16** |
| 类型级绑定缺口 | **0**（153 个类型受检，2 个因泛型元数跳过） |
| 类型缺失（type presence） | **15** |
| 成员形状差异 | **94**（core 17） |
| 文案缺口 | **0**（649 键 / 20 区） |
| 绑定缺口分桶 | 类缺成员 **0** · 类型缺失 **4** |
| 原版绑定描述符表 | 951 条 / 215 类型 / only-in-descriptors 132 |
| 数据文件名对照 | 原版有而复刻件不写 **0** · 复刻件独有 **2**（`Cybersole.ProfileValidation.en.json`、`license.json`） |
| 函数数（.pdata 精确解析） | 原版 **277,120** / 复刻件 **174,293** / **62.89%** |
| 可执行段体量 | 51,695,104 / 28,897,792 / 55.90% |
| 产物陈旧度 | **0 / 0**（current） |
| 变异套件 | 36 总 / 36 fired / 0 decorative / 0 skipped，staleness 0:24:34（`business_types.py` 那轮之后动过） |
| 完整套件 | **2258 通过 / 0 失败 / 0 跳过**（来源会话 22:54 记录；本会话未重跑全量） |

### 3.3 环境

| 项 | 状态 |
|---|---|
| IDA | **未运行**（`Get-Process ida*` 空、13337 `REFUSED`、`python analysis/ida.py health` exit 1）→ 要取证得先按 goal 的 doctor + CUA 流程拉起 |
| IDB | `target\Cybersole.exe.i64`（**1375 MB**，三个月积累，**绝不可覆盖**） |
| 内存 | 来源会话最后一次记录 20.55 GB free；本会话未测 |

---

## 4. 进行中：R1075（未提交、未验证）

来源会话在 R1074 提交后立刻开了 R1075，**改完 `analysis/ida.py` 就停了**（23:01 被 pause）。

### 改的是什么

`analysis/ida.py` 的 `str` 子命令以前直接 `print(call('find_regex', ...))`，插件回来的 `n` 是
**返回条数**而不是命中总数。R1073 把 `--limit 4` 的结果读成「总共 4 条」，于是怀疑证据基线缩水，
又花一轮（R1074）推翻自己。所以 R1075 的处置是**把接口改成读不错的**，不是再写一遍提醒：

```python
raw = call('find_regex', {'pattern': rest[0], 'limit': limit})
obj = json.loads(raw)
hits = obj.get('matches') or []
obj['returned']  = len(hits)
obj['limit']     = limit
obj['saturated'] = len(hits) >= limit                     # 撞到上限 ⇒ 这个数不能当总数
obj['total']     = len(hits) if len(hits) < limit else 'at least %d (saturated -- raise --limit)' % len(hits)
obj['n']         = obj.get('n', len(hits))                # 保留旧键，向后兼容
```

### 它还没被验证

**要验的三条**（IDA 起来之后）：

1. `python analysis/ida.py str kpsdk --limit 4` → `saturated: true`、`total: "at least 4 …"`
2. `python analysis/ida.py str kpsdk --limit 500` → `saturated: false`、`total: 17`（17 是 R1044/R1053/R1073 三次一致的对照值）
3. `python analysis/ida.py str "Solving PayPal 3DS" --limit 600` → `total: 9`（R1053 的值）

三条都过 ⇒ 提交 + 写 R1075 记录（`BLOCKERS.md` / `HANDOFF.md`）。
任何一条不过 ⇒ 回滚这个 diff，先查 `find_regex` 到底返回什么键。

---

## 5. 最近 26 轮（R1049–R1074）一句话编年

| 轮 | 结论 |
|---|---|
| R1049 | `BotDeflector` / `Vercel` 的 Solver 都定了 `Local`（有据）；补行因 4 个守卫回滚 |
| R1050 | 补一行实际是九件事；五处改了、五处红、回滚；完整清单已固化 |
| R1051 | 第 9 项由代码答了；范围是 11 处不是 9；三次尝试后回滚 |
| R1052 | 12 个钉子一次改完；真厂商缺口归零（0）；套件 2257/1（红的是网络用例） |
| R1053 | 「归支付层」是没被记下来的缺口；两条支付挑战已量化（PayPal 3DS 9 条文案 / 4 态状态机 / 2 个 solver） |
| R1054 | 各家 captcha 第一次被枚举：6 家 + 2 家明确缺席；`UserThirdParty` 有了结构依据 |
| R1055 | (a) 的类型级缺口第一次被算出来：一个真的零旁边是一个假的零 |
| R1056 | 反查名字 → 找到一个真缺口 → 补上 → (a) 类型级缺口真的成 0 |
| R1057 | 两个命名空间是穷尽的；枚举纠正了一个 extras，又弄坏生成器一次 |
| R1058 | 「类型级缺口」不能用名字对 —— goal 早就写了「命名可不同」 |
| R1059 | 「每个函数功能相等」不可逐函数验证 ⇒ 换成可数的下界 |
| R1060 | (e) 后半达成：36/36 变异 fired、staleness 0；两个差异标 Unknown 不猜 |
| R1061 | 那个 exit 1 很可能是我的测量方式，不是脚本的矛盾 |
| R1062 | 两个差异闭合：`exit 1` 撤销（是我的管道）· 「差 19」撤回（是口径不同） |
| R1063 | 陈旧度 16/8,626 → 0/0；(c) 成立；路径校验第一次真的跑了 |
| R1064 | `62.89%` 可靠，但测的不是完成度（`.text`/函数 = 6 字节，荒谬的中间量） |
| R1065 | 自己编的 .NET 8 NativeAOT 基线否掉了我的安慰性解释（7,930 vs 102,827） |
| R1066 | 一次直接测量定了两轮假设，方向是反的（−621） |
| R1067 | 字符串探针上限 500 条 ⇒ 它的零是窗口的属性 |
| R1068 | 分片绕开上限：类型覆盖 89.3% vs 函数 62.9% |
| R1069 | 13 个疑似缺口全部排除（真缺口 0）；IDA 进程退出 |
| R1070 | IDA 重新拉起：3 个框，按规程点，`status: ok` |
| R1071 | 反编译通了；而它证明了反编译不足以给出语义 |
| R1072 | 「名字旁边有代码指针」不存在；那是第四次同一个错 |
| R1073 | 同一条查询：修复前 9 条、修复后 4 条；怀疑证据基线变了 |
| R1074 | R1073 的怀疑被推翻：基线没动（324,895 条字符串 / sha256 一致），是我把 `--limit` 当成总数 |

---

## 6. 未结案清单（从来源会话最后状态搬过来，按优先级）

### 6.1 明确可做

1. **R1075 收尾**（§4）：验证 → 提交 → 记录。
2. **支付层两个挑战**（R1053 取证完备、实现未做）：
   - PayPal 3DS：9 条文案（`(1) (2) (2.1) (3)…(8)`）+ 4 态状态机（`Submit3DS · Process3DS · Waiting3DS · Complete3DS`）+ 2 个 solver（`<SolvePayPal3DS>d__38`、`<SolvePayPalHosted3DS>d__39`）
   - Stripe challenge：`SubmitOrderStripe · ProcessOrderStripe · GetStripePaymentIntent · CreateStripePaymentMethod · SubmitStripeOrder · ValidateStripeIntent · SetStripePayment · StripeFallbackHandler`
   - 两者都不在复刻件里 ⇒ 属 (f) 「未覆盖的每条写为什么」里**已定位、可补**的两条。
3. **captcha 层**（R1054 枚举完，实现未做）：`Recaptcha`（含 Invisible/V3/Enterprise）· `HCaptcha`（含 Invisible/Spoof）· `Turnstile` · `Geetest`（含 V4 / 本地 html 自解）· `Castle` / `TrustDevice`；明确为零：funcaptcha/arkose、mtcaptcha。
4. **(a) 的 15 个 `ABSENT` 类型**要逐条分类 RENAMED / UNIMPLEMENTED —— 当前 `TYPE_PRESENCE_TRIAGE.md`（2,990 字节）已开工，未逐条结案。
5. **(b) 的 4 个 real gap**（`LocalizeFormatExtension.Value2` · `LocalizeSwitchExtension.Condition` · `AuthWindow.Logout` · `LicenseControl.Authenticate`）：属"类型不存在但成员有描述符"，要先定它们是不是原生实现。
   - **【2026-11-18 纠偏注记】**：其中 `AuthWindow.Logout` 与 `LicenseControl.Authenticate` 早在 R702 已由 YG 裁决 `OUT_OF_SCOPE`（登录与许可管理不做，见 `docs/DECISION_LICENSE_OUT_OF_SCOPE.md`）；剩余 2 条属 UI 标记扩展，冻结于优先级④。
6. **变异套件 staleness 0:24:34** —— `business_types.py` 在那次运行后被动过，要重跑 `python tools/mutation-check.py` 才能引用 36/36。

### 6.2 卡在外部条件

- **PopMart 7 个抽签 POST body** —— 需要原版登录凭据（YG 才有的两类事之一）
- **Kasada / Akamai 第三方 solver** —— 复刻件侧没有 solver 类；要不要做需 YG 定
- **`CloudflareSolver.Type` 的取值** —— 镜像里只有类型名，值域 Unknown
- **queue-it softblock 协议** —— 有文案（`Error Solving Queue-it (Softblock)`）无协议
- **`BstnFlow` 的处置** —— 需 YG 拍板（来源会话记了两轮未决）
- **DSH 的 ida MCP 代理**（`PROXY: MISSING`）—— 不阻塞 `analysis/ida.py` 直连，但属"要 YG 开关 MCP 条目"的那一类

### 6.3 判据口径上的真空

- **「效率相近」从未被度量**（goal 第 1 句），没有任何命令产出过效率数字。
- **「每个函数功能相等」** 在 R1059 被换成"可数的下界"（类型覆盖 89.3% vs 函数 62.9%，R1068），这是**判据的实质性降级**，需要 YG 知情。

---

## 7. 本会话复核出的两处口径不一致（来源会话留下的）

### 7.1 「函数数」在 BLOCKERS 里被换成了粗算值

`docs/BLOCKERS.md` 从 R1065 起的数字表（第 38244 / 38299 / 38350 / 38408 行）把函数数写成
**174,258 / 277,094**，而 `docs/METRICS.md`（唯一数字源）是 **174,293 / 277,120**。

来源：R1064 用 `.pdata` 段字节数 ÷ 12 反推得 **174,258 / 277,094**（`.pdata` = 2,091,096 / 3,325,128），
当时写的是「与两个函数数各自对上」——**是近似对上**（差 35 / 26，尾部对齐所致）。
后面几轮把粗算值直接当成了"函数数"。

**⇒ 处置：以 `func_count.py` 精确解析 RUNTIME_FUNCTION 的 277,120 / 174,293 / 62.89% 为准。**
这正是那边反复记的「计数掩盖口径」，换个地方又犯一次。

### 7.2 `VERDICT.md` 停在 R1048，R1049–R1074 没进去

`replica/docs/VERDICT.md`（62,632 行 / 2,459,648 字节）最后一节是「第 1048 轮」，最后修改 20:23。
R1049 之后的 26 轮只写进 `docs/BLOCKERS.md` 与 `docs/HANDOFF.md`（23:00 修改）。

**⇒ 别把 VERDICT 当"最新"读。** 它的 16 句上限规矩（来源会话记录）也仍有效。

### 7.3 **IDA 不可用时 `vendor_coverage.py` 报 `missing=0`，而 `missing=0` 看起来像"缺口归零"**（本会话实测）

本会话 23:12 在 IDA 未运行的情况下跑了一次 `python tools/metrics_report.py --skip-tests`，`vendor_coverage` 一节变成：

```
  controls ok=False  vendors named=0  wiring rows=9  missing=0      ← 本次
  controls ok=True   vendors named=13 wiring rows=9  missing=5      ← 22:54 的真实记录
```

成因（读 `replica/tools/vendor_coverage.py`）：它靠 `analysis/ida.py str <pattern> --limit N` 探针取厂商名，
探针失败时每条命中都是 0 ⇒ `control_ok = False`，但**它仍然照常印出 `missing=0` 并以 exit 0 结束**。

**⇒ 这是"看不见与不存在长得一样"的第 N 次复现，而且它污染的是 `docs/METRICS.md` 与
`replica/docs/VENDOR_COVERAGE.md` 两个生成物。** 本会话已 `git checkout` 回滚这两份文件，
没有让假零进仓库。

**⇒ 建议（下一轮一行）**：给 `vendor_coverage.py` 加拒绝发布守卫 —— `if not control_ok: return 2`，
理由与 R764 那次 `rows == 0` 的守卫完全同源（解析不出东西时不许发布"全部缺失/全部齐备"的结论）。
同一守卫也该加在 `metrics_report.py` 调它之后：任一 viz 脚本 exit != 0 时，METRICS 不写该节而写"未测"。
- **【2026-11-18 纠偏注记】**：`vendor_coverage.py`、`payment_challenges.py`、`captcha_coverage.py` 均已补上 `control_ok` 非零退出守卫（`exit 2`），且 `metrics_report.py` 的 `core` / `vendor` 摘要提取正则已修复对齐。

---

## 8. 纪律沉淀（来源会话 769 轮里新增的，本会话起继承）

1. **「写下来」不保证「不再犯」** —— 「抽样当全量」这个错写进文档后又犯了第 5 次（R816→R764→R1054→R1067→R1073/74）。
   对策不是再写一遍，而是**把接口改成读不错的**（`returned` / `saturated` / `total`）。
2. **一个零需要对照才能读**（R1044）：`datadome`/`queue-it` 的 0 是"没有"还是"探针不对"，只有加一个已知非零的对照才分得清。
3. **计数掩盖类别**（R1042 / R1048）：7 个缺口里有 2 个是真厂商、5 个根本不属于那张表。先说清 **kind**，数字才有意义。
4. **同一个形状的失败反复出现时，要问"每次尝试共享的那个前提，曾经成立过吗"**（R1045 / R1072）。
5. **反编译不足给出语义**（R1071）：IDA 能给你控制流，给不了"这个字符串是站名还是字段名"。
   - **【2026-11-18 纠偏注记】**：此条仅对裸看无符号伪代码成立。NativeAOT 冻结字符串对象头在 **`obj_va = chars_va - 12`**（R702 已验证），用 `disp32_scan_any.py` → `site_to_func.py` 定位函数后，把伪代码中的 `&off_146xxxxxx` 喂给 `analysis/names_at.py` 即可完整还原业务字符串与协议语义；最新接手规程以 `docs/HANDOFF_PROMPT_antigravity.md` 为准。
6. **荒谬的中间量是最好的报警器**（R1064）：「每函数 6 字节」比任何纪律都更早指出假设错了。
7. **工具的最小基线不是仓库的验收判据**（R1031）：证据不在就回滚，别为了让工具变绿而改产品口径。
8. **加一行到 `VendorWiring` 是 11 处联动改动** —— R468–R499 的连带清单在项目规模上的复现。
9. **`AntiBotVendors.All` 是镜像侧主张，`VendorWiring.State` 是复刻件侧主张** —— 两者可以合法地不一致。
10. **不要用 PowerShell 做源码文本手术**：`Set-Content` 不带 `-Encoding utf8` 会写成 GBK；
    heredoc 和引号会被吞。写临时 `.py`，跑，删。

---

## 9. 接手动作（本会话可直接执行，按序）

```powershell
# 0) 环境体检（IDA 未运行，先按 goal 的流程拉起；不想拉就先做不需要 IDA 的项）
Get-Process ida*                                  # 空 ⇒ 要拉
powershell -File "D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1" -Path "D:\projects\cyber-reverse\target\Cybersole.exe.i64"
#    同时 CUA 轮询 ida 窗口，条件见 §2 的 goal 原文；判据是"再读一次没有框"

# 1) R1075 验证（需要 IDA 就绪）
python analysis/ida.py str kpsdk --limit 4         # 期望 saturated: true
python analysis/ida.py str kpsdk --limit 500       # 期望 saturated: false, total: 17
python analysis/ida.py str "Solving PayPal 3DS" --limit 600   # 期望 total: 9

# 2) 不需要 IDA 就能做的
cd replica
python tools/mutation-check.py                     # 清掉 staleness 0:24:34
# 给 vendor_coverage.py 加 control_ok 拒绝发布守卫（§7.3，改脚本不需要 IDA，验证需要）
# 注意：IDA 未起时不要跑 metrics_report.py —— 它会把 vendor 一节写成假零并污染两份生成物（§7.3）
python tools/metrics_report.py                     # IDA 就绪后才跑；全量套件 1m28s

# 3) 之后按 §6.1 的 3 或 4 推进（支付层 / captcha 层 / 15 个 ABSENT 分类）
```

---

## 10. 一条提醒

来源会话是 **goal 驱动的自动续跑**（769 轮里 728 轮没有人类输入），它的"上下文"因此**高度依赖仓库文件的自洽**。
本会话若要接着跑，正确做法是：**先建 goal（objective 用 §2 的原文），再按 §9 的动作清单干**；
不要指望对话记忆能代替 `METRICS.md` / `BLOCKERS.md` —— 那边 33 次压缩证明了对话记忆是不可靠的载体。
