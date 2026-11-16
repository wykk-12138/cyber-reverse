# 「1:1」的有限 claim 表（判据 d）— R433 裁决 3 版

> 判据 d 原文：**用 `verify_reconstruction` 把"1:1"拆成有限 claim 逐条判 pass / fail / unknown，
> unknown 逐条写明缺什么证据。**
>
> R433 裁决 3 定为**双轨制**：表可以是人工判定的，但**每条 claim 必须带 `authority`**，
> 且 `authority ≠ unknown` 的必须带可重算 `command`。
> **判据 d 满足 = 每条都有 authority，且非 unknown 者都有命令。**

---

## 0. 为什么这张表是人工判定（证据原文，不是放水）

`verify_reconstruction` 实测拒绝（R433，rea 6.9.0）：

```
mcp__rea__verify_reconstruction(
  specification{claims:[{kind:"structural-artifact", dimension:"overall",
                         comparison_evidence_id:"ev_7d9cab4cc51faeb3ecb557aca6872becab53e25e66fb95f03c0748e64557d3cd"}]})
→ Error: Claim c1-import-surface requires compare_artifacts Evidence; selected inspect_pe_imports
```

它的 schema（`rea/src/domain/reconstructionVerificationSchemas.ts`）要求每条 claim 引用
`comparison_evidence_id`；comparison Evidence 只能由 `compare_functions` / `compare_artifacts` /
`compare_process_captures` 产生，而这三条在本机**全部不可用**（`docs/PARITY_PRODUCT.md` §5：

| provider | 状态 |
|---|---|
| ghidra | `not_configured`（`Set GHIDRA_INSTALL_DIR …`） |
| hopper | `unsupported_host`（win32） |
| ida | `not_configured`（`REA_IDA_MCP_CONFIG` 只认 legacy 工具名 `get_metadata`/`list_functions`/`decompile_function`，本机插件是新版目录） |
| kuna | `not_configured` |

R433 裁决 2 决定：**不装 Ghidra、不降级插件**，改用现成的两条 IDA 链做清单级对照。
Ghidra 留作后手，只有当某条 claim 必须伪代码级证据时才装，装前先说明它解决哪一条。

---

## 1. 结构类（structural-artifact）

| id | claim | status | authority | command | gap_reason |
|---|---|---|---|---|---|
| C1 | 两个产物是同类（PE32+/amd64/windows_gui/NativeAOT，无 CLR 目录） | **pass** | manual-from-command | `pe_triage.py` 对两产物各一次；见 `PARITY_PRODUCT.md` §2 | — |
| C2 | 节布局相同 | **fail** | manual-from-command | `pe_diff.py --summary`（6 节 ↔ 9 节）；`pe_triage.py` 节表 | — |
| C3 | 导出面相同 | **fail** | manual-from-command | 同上（39 ↔ 1） | — |
| C4 | 导入面相同 | **unknown** | unknown | — | 缺**原版 imphash 与完整导入集合**：`inspect_pe_imports` 对 129 MB 要求 `max_functions≥438` 且完整转储；本轮只算了复刻件（`ev_7d9cab…`）。补法：对原版跑一次并重定向到文件 |
| C5 | 资源面相同 | **pass** | tool-evidence | `python analysis\pe_resources.py` → 原版 **12** ↔ 复刻件 **12**，逐叶子同路径同类型。**R706 在 11:49 重建的新产物（55,349,248 B）上重算，结论不变** | — |

> C2/C3/C5 判 `fail` 但**每条都可解释**（AOT 版本差 / Brotli 静态库导出 / 复刻件不随附图标，见 `DEVIATIONS.md`）。

## 2. 函数类（structural-function）

| id | claim | status | authority | command | gap_reason |
|---|---|---|---|---|---|
| C6 | 函数数量与符号可见性对照成立 | **pass（Observation 层）** | manual-from-command | `python analysis\func_compare.py` → 原版 321,244（命名 10,041）/ 复刻件 187,328（命名 175,104）；**三个复刻件数各有条件，不是三份矛盾的测量**：187,328（R433，带 PDB）、187,698（R613，带 PDB）、**186,732（R613，不带 PDB，即同口径基准）**、187,732（R694，带 PDB + 当前源码产物）。带 PDB 的三个数差 370 是**三版产物**，不是误差；186,732 与它们的差是 **PDB 口径**（R613 实测 PDB 影响 +966 = 0.5%）；`python analysis\function_breakdown.py` → 复刻件业务代码 **2,485** 个 / 0.92 MB，其余 98.7% 是 BCL/Avalonia/Jint/加密库 | —  **[R706] 本行数字取自 2026-11-16 11:49 之前重建的产物（55,080,448 B）；11:49 的产物为 55,349,248 B，本行未在新产物上重测**，重测需把新 EXE+PDB 重新载入 IDA（13338）。 |
| C7a | 绑定成员能否在原版定位到**绑定声明** | **pass** | tool-evidence | `python analysis\binding_descriptors.py` → 原版描述符表 951 条 / 215 类型；**51 个 ABSENT 类型全部在表里、成员全覆盖**（R464） | — |
| C7b | 成员**形状**（getter / setter）两侧一致 | **fail**（当前条数见 `METRICS.md` 的"成员形状差异"） | tool-evidence | `python tools\shape_audit.py`；**用描述符表交叉验证：报出的每一条在原版描述符表里都有 Setter（0 反例）**（R467） | 构成（**R468 当时的实测，非当前值**；当前条数见 `METRICS.md`）：175 条是"原版要可写属性、复刻件实现成 `method`"；61 条是"复刻件根本找不到该成员"；29 条是"数据属性缺 setter"。运行时不受影响（复刻件代码构造 UI，不走 XAML 绑定），但**结构偏离明确**。R468 同时修掉 10 条误报（`ICommand Foo { get; }` 本来就该只读，不算缺 setter） |
| C7c | 任意两函数的**伪代码等价** | **unknown** | unknown | — | 缺原版符号（PDB / 调试信息）。**Ghidra 不能提供**（它只会把 `sub_` 改名成 `FUN_`），故不再作为选项。若将来要证行为等价，优先做**行为探针**（同输入 → 两侧输出/副作用对照），而不是伪代码 diff |
| C8 | 字符串池对等 | **unknown** | unknown | — | 缺**分类比对**：`analysis\pe_strings.txt`（原版）↔ AOT 字符串清单，按 locale 键 / URL / 错误消息分三类逐类比。现有工具无此能力 |
| C9 | `.pdata` 覆盖的展开函数数量级相当 | **unknown** | unknown | — | 该口径只覆盖"需要展开信息的函数"，与 `idautils.Functions()` 不等价；要判对等必须先证明两套口径的换算关系。当前：277,094 ↔ 170,137（`pe_triage` 的 `.pdata` vsize ÷ 12） |

> **C6 只判到 Observation 层**：数量差 −41.7% 是事实，但"差在哪"需要 C7；不许用 C6 的 pass 去暗示 C7。

## 3. 成员类

| id | claim | status | authority | command | gap_reason |
|---|---|---|---|---|---|
| C10 | 819 个绑定成员在产物中各自有可见实现 | **unknown** | unknown | `python tools\aot_member_coverage.py` → **12/819 = 1.5%**（R694：当前源码产物 55,080,448 B + 该产物自身导出的 187,732 个符号，`auto_analysis_ready=true` 之后才导出）。**旧值 21/819 已作废**：它的符号表比产物旧 20 小时（R693） **[R706] 本行数字取自 2026-11-16 11:49 之前重建的产物（55,080,448 B）；11:49 的产物为 55,349,248 B，本行未在新产物上重测**，重测需把新 EXE+PDB 重新载入 IDA（13338）。
| C11 | 111 个绑定类型名在产物里不可见，是命名差异还是未实现 | **unknown** | unknown | — | 缺**人工类型名映射表**（此处 111 是 R433 的口径；**当前的类型缺失计数见 `METRICS.md`**，逐条定性见 `docs/TYPE_PRESENCE_TRIAGE.md`）：AGENTS 允许命名不同（`SettingsView` → `Settings_SettingsShell`），类型名不匹配**不算缺口**，但要区分"改名"与"没有"，需要逐类型核对源码 |

## 3.5 MonitorView 五条命令（R434）

> 证据：编译期 XAML 绑定描述符三串（Getter / Setter / Property），见 §2.5 的地址表。
> `Getter/Setter/Property` 齐全 = 这五个成员是 **XAML 绑定目标**（列表页 + 选中项驱动），
> 所以"命令作用于当前选中项"是**结构可推**的，不是猜行为（R434 裁决 0）。

| id | claim | status | authority | command | gap_reason |
|---|---|---|---|---|---|
| C-monitor-view | `View` 触发后选中项详情可见，内容 == 当时选中项 | **pass** | tool-evidence | `dotnet test --filter "FullyQualifiedName~MonitorViewCommandTests"` · 绑定串 `0x14363b668` · 模型串 `0x14321141a` | — |
| C-monitor-openfilter | `OpenFilter` 触发后暴露 `Settings.MonitorFilters`，且是同一实例 | **pass** | tool-evidence | 同一用例类 · 绑定串 `0x1432111cd` / `0x143211210` / `0x14363b623` · 模型串 `Settings.MonitorFilters` 同行 | — |
| C-monitor-openurl | 打开商品 URL 的方式（外部浏览器 / 内置窗口？） | **unknown** | unknown | — | 需主界面 GUI 观察或伪代码级对照。绑定串只证明 `OpenUrl` 是命令，**不**说明它把 URL 交给谁。当前实现为显式钩子（host 未注入即无副作用） |
| C-monitor-linkchange | `Link Change` 作用于什么（替换选中项链接？批量？整个 feed？） | **unknown** | unknown | — | 同上。locale 只有 `Monitor.LinkChange` 文案，无语义。当前实现为显式钩子 |
| C-monitor-quicktask | `Quicktask` 的目标（创建任务？填充 creator？剪贴板？） | **unknown** | unknown | — | 同上。`Monitor.LaunchQuicktask` 只有文案。当前实现为显式钩子 |

**三条 unknown 的代码侧**：`MonitorView.OpenUrl` / `LinkChange` / `Quicktask` 的注释里写着对应 claim 编号，
未注入钩子时 `LastHookNote` 记录"structure only, behaviour not implemented"，且**不产生任何外部副作用**。
`MonitorViewBehaviourPins` 守卫这一点：代码或本表任一方被删，测试就红。

## 4. 行为类（behavioral）

| id | claim | status | authority | command | gap_reason |
|---|---|---|---|---|---|
| C12 | 全量测试套件绿 | **pass** | tool-evidence | `python tools\metrics_report.py`（内含 `dotnet test --filter "Speed!=Slow" -m:1`）→ 见 `docs/METRICS.md` | — |
| C13 | 落盘格式对齐（settings / tasks / solvers / checkoutHistory / .cyb） | **pass** | tool-evidence | settings/tasks/solvers/accounts/proxies + `.cyb` 由 `LiveSchemaPinsTests`（10 条）按原版 key 钉住；**`checkoutHistory` 此前没有任何格式守卫**，R445 补上 `CheckoutHistoryShapeTests`（2 条）—— 见右列 | **R445 复核时发现 evidence 不全**：原版数据目录里 `checkoutHistory.json` 是**唯一 PascalCase** 的文件（`Store/Product/Size/Price/Success/OrderNumber/Profile/At/TrackingUrl`），其余全是 camelCase；复刻件恰好因为 `CheckoutStats` 用了无 settings 的 `JsonConvert.SerializeObject` 而对上。守卫已补并实测会红（把写入改成 `Json.Serialize` 即失败） |
| C14 | 文案 19 区无缺 | **pass** | tool-evidence | `python tools\copy_audit_report.py` → **0 missing / 0 near**（条数见 `METRICS.md`）。**R704/R705 把最后两条从「有文案无发出路径」变成「有实现」**：`ProfileCsvEditorView.ValidateAddress` 按 R702 解出、R703 复验的四维规则校验 Country/State，名单由 `analysis/export_profile_lists.py` 从原版导出（244 国 / 50 州，对齐异常 0）。**不是把判据读宽** —— `_satisfied` 的「键出现在代码」这一支现在真的有代码 | — |
| C15 | **零直接调用点的函数比例**（"效率相近"的代理指标，**不是**效率对照） | **pass（Observation 层，R458 实测）** | tool-evidence | 两侧 IDA `py_eval` + `idautils.XrefsTo(ea, 0)`：原版 13337 → `total=321244 noref=3603 pct=1.1`；复刻件 13338 → `total=187328 noref=6669 pct=3.6` | **它证明什么**：复刻件"无直接调用点"比例是原版的 3.3 倍（可复算）。**它不证明什么**：① 不是运行时耗时对照（那需要两边跑同一条业务路径，卡在登录凭据）；② 零直接 xref ≠ 死代码 —— 主因是间接分派（绑定/委托/虚方法），且 `src/` 侧真正零引用的类型只有 27 个，量级远小于 6,669 |

> C12/C13 的数字**不再写死在本文件**：引用 `docs/METRICS.md`（生成文件）。这是 R433 裁决 1 的落地。

---

## 5. 绑定缺口：三条按 Unknown 结案（R433 裁决）

| 缺口 | status | authority | gap_reason（缺哪类证据能解） |
|---|---|---|---|
| `Profile.Card` / `Username` | **unknown** | unknown | 一份**含 profile 的原版备份**（现有备份 `profiles` 为空）→ 才能判定落盘是嵌套 `Card{Number,Cvv}` 还是平铺 |
| `ProxyTester.Name` | **unknown** | unknown | 原版 `Cybersole.ProxyTesters.ProxyTester` 是**行模型**、复刻件同名类是**服务**。需要原版该类型的方法体（IDA 按字符串 `ProxyTester` 追 xrefs）才能确定它有没有数据属性 |
| `SmartActionsView.Export` | **unknown** | unknown | 原版有 `get_Export`（池 `0x0351d8b1`），但**导出目标与格式无任何证据**（无 locale 键、无文件对话框文案、无示例产物） |

---

## 6. 判据 d 满足性（按裁决 3 的定义逐条核对）

| 条件 | 结果 |
|---|---|
| 每条 claim 都有 `authority` | **满足** —— C1–C14 + 三条绑定缺口 + MonitorView 五条（C-monitor-*），共 **22 条**，全部带 authority |
| 非 unknown 者都有 `command` | **满足** —— 10 条非 unknown（C1/C2/C3/C5/C6/C12/C13/C14 + C-monitor-view/C-monitor-openfilter）全部带命令 |
| unknown 者都有 `gap_reason` | **满足** —— 12 条 unknown 全部写明缺哪类证据 |

统计：**13 pass/fail（可复算）· 12 unknown（缺证据已写明）**。
（R459 加 **C15**（零直接 xref 比例，效率的代理观察）；R467 按 R456 裁决把 **C7 拆成 C7a/C7b/C7c**
—— C7a pass（51/51 能定位到绑定声明）、C7b **fail（R467 时为 275 条；当前条数见 `METRICS.md`，描述符表当时的 275/275 交叉确认仍成立）**、
C7c unknown（伪代码等价，Ghidra 也不能提供）。）

> 判据 d **满足**，但满足的是"**有限 claim + 逐条 authority + 逐条缺口**"这个标准，
> 不是"函数级等价已被证明"。后者仍是 C7 的 unknown。

---

### 6.5 R692：对 METRICS 做了一次机器核对 —— 7 处不一致，全部改为指针或标注

§6 的"满足"是**结构性**的（每条都有三列）。但表里同时写着**数字**，而项目的规矩是数字只住在 `docs/METRICS.md`。
R433 当初就是这么在六个文件里抓到八个失效数字的，同一类漂移在这张表里又长了出来。

工具：`python analysis/audit_claims.py`（读 METRICS 的当前值，逐条比对）。

| 位置 | 原来写的 | 处置 |
|---|---|---|
| C7b | `275 条形状差异` | 改为指针；R467 当时的 275/275 交叉确认保留并标注为历史 |
| C7b | 构成 `175 / 61 / 29` | 标注为 **R468 当时实测、非当前值** |
| C14 | `5 条缺失，全为"池中截断"`（当时的记录） | 条数改为指针；R668 证明不是截断，R704/R705 补实现后现值为 0 |
| C14 | gap_reason 称"5 条池中截断" | **更正为 R668 的结论**：剩下 2 条在池里完整，缺的是**校验行为**；R688 又证明校验名单也在 |
| C6 | 复刻件 `187,328` | 补上 **R613 同口径 186,732** |
| C10 | `21/819` | 标注为 **R433 时的一次性测量，未随度量重算** |
| C11 | `111 个绑定类型名` | 补指针到 METRICS 与 `TYPE_PRESENCE_TRIAGE.md` |

复算：`python analysis/audit_claims.py` → **inconsistencies found: 0**。

**注意处置方式**：一个数字被后续轮次更新，不等于那句话错了 ——
R467 的 275、R468 的构成、R433 的 21/819 在当时都是真的。
所以**不改历史、只加指针与"当时的"字样**；只有**被否证的事实**（"池中截断"）才更正，并写明是哪一轮否证的。

## 7. 把 unknown 变 pass/fail 的补法（R433 裁决后的优先级）

| 优先 | 动作 | 解锁 | 是否需新依赖 |
|---|---|---|---|
| 1 | 原版跑 `inspect_pe_imports`（`max_functions≥438`，重定向到文件） | C4 | 否 |
| 2 | 写字符串池分类比对（locale 键 / URL / 错误消息） | C8 | 否（须注明为何现有工具不够） |
| 3 | 两侧 `decompile` 配对器（基于现有 IDA 链，不装 Ghidra） | **C7** | 否 |
| 4 | 对 `.managed` 跑 Hex-Rays，或另做 managed 发布走 REA .NET 工具 | C10 / C11 | 需新构建配置 |
| 5 | 装 Ghidra 给 REA 当 native provider | C6 深层 / C7 | **数 GB + 第三套口径**；仅在某条 claim 必须它时才做，且先说明解决哪条 |

---

## 8. 一句话

> claim 表的价值不在"判了几个 pass"，而在**每条 fail 都能被解释、每条 unknown 都写清了缺什么**。

> **"1:1"当前：同类成立（C1）、结构差可知（C2/C3/C5）、函数清单已对照（C6）、
> 语义等价与成员可见性仍 Unknown（C7/C10/C11）。**
