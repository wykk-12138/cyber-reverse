# 交付状态（objective 达成到哪一步）

> 本文回答一个问题：**这个复刻任务"做完了"是什么意思、现在到哪一步了。**

## 静态取证边界（R593）

判据 a / b 的**剩余部分**有一个共同的边界，写在最前面比埋在 §4 里有用：

| 还能靠静态推进？ | 内容 |
|---|---|
| ❌ | `ProfileCsv.Error.UnknownCountry` / `UnknownState` 的**规则**：需要知道校验器用哪份数据。 |
| ❌ | `Models.Notification.Timestamp` 的**填充来源**。 |
| ❌ | 那 34 条"需要选择模型"的成员各自的**参数从哪来**。 |
| ✅ | 以上三条的**存在性**已全部证清（原文、数据表位置、成员归属），缺的都只是"行为/取值"。 |

**为什么静态到此为止**（Observation）：

```
ProfileCsv.Error.UnknownCountry    xrefs 0
ProfileCsv.Error.UnknownState      xrefs 0
Alabama / state / postcode         xrefs 0（item head = 自己，size 1，无名）
country（精确匹配）                 91 处，xrefs 全为 0
```

镜像里的两类数据都不产生字符串级 xref：**序列化 blob**（代码引用 blob 起点）与**运行时字典**
（AOT 按名查，没有"读这个常量"的指令）。

要越过它只剩两条路，都不在单轮内：

1. **在 .i64 里把 blob 建模出来**（定义数据项与指针表）—— 独立工程；
2. **原版运行时观察** —— 需要登录凭据，属阻塞项。

**所以判据 a / b 现在的状态不是"没查"，是"查到了静态证据的尽头"。**

> 所有数值以 `docs/METRICS.md`（生成物）为准；本文引用的是 **2026-11-14 18:45 那次生成**的快照。
> 要最新值：`cd replica; python tools/metrics_report.py`。

---

## 0. 一句话结论

**交付判据 a–e 全部满足；objective 的三句话里，第一句未达成、第二句 unknown、第三句从未验证。**

这不是文字游戏。判据 a–e 是"交付物是否齐备"的标准，它们全绿只能说明
"该量的都量了、该记的都记了、该绿的都是绿的"；它**不等于**"功能 1:1 已达成"。

---

## 1. objective 三句话的逐条状态

objective 原文：「函数数量对等、**每个函数功能相等**、效率相近」。

| # | objective 的要求 | 状态 | 证据 / 原因 |
|---|---|---|---|
| 1 | **函数数量对等** | ❌ **未达成**（但差值已定位） | 原版 321,244 ↔ 复刻件 187,328（−41.7%）。`analysis/function_breakdown.py` 把复刻件拆开：**业务代码 `Cybersole_*` 只有 2,485 个函数 / 0.92 MB（1.3%）**，其余 98.7% 是 BCL/Avalonia/Jint/加密库。字节比例 0.50 与函数数比例 0.58 同量级 → 差异是**系统性（框架规模）**，不是某层整体缺失。原版侧**无法分解**（311,203 个 `sub_*`），所以"业务函数对等"仍不可判定 |
| 2 | **每个函数功能相等** | ⚠️ **unknown** | claim C7。三层障碍实测：① 原版 321,244 个函数全是 `sub_*`（无符号）；② locale 字符串**打包成整块 JSON**（`0x143c656aa` 一个块含数百条键值），块内偏移不能 xref 到引用它的函数；③ 复刻件 AOT 内联使 819 个绑定成员只有 21 个保留独立符号。**连"两侧各取一个可比函数"都过不去** |
| 3 | **效率相近** | ❌ **从未验证** | 两条**独立**限制，都不在我权限内：① **缺原版运行时入口**（登录凭据，进不了主界面）；② **跑原版就必然写 `%APPDATA%\Cybersole`**，而那是红线（只读）。唯一的规避线索是环境变量名 `CYBERSOLE_DATA`（字符串 `0x146b69f1c`），但在 IDA 里对它做 xrefs 得到 **0 个引用** —— 无法证明它能把数据根重定向到隔离目录，因此**不能据此启动原版**。`PerformanceTests` 只测复刻件自身，没有原版对照 |

> 第 3 条是我此前一直没提的一句。判据 a–e 里没有效率项，所以它从未被要求；但 objective 明写了它，
> 因此在这里单列，不藏。

---

## 2. 交付判据 a–e：逐条证据

| 判据 | 要求 | 现状 | 依据（今天重跑） |
|---|---|---|---|
| **a** | 类型级缺口 → 0、类型缺失 → 0（不可得则写 Unknown + 缺什么）；名字级三分类结案 | ⚠️ **三项成立、一项不成立** | **类型级：`python tools\bind_scope.py` → `types with scope misses: 0`** ✅<br>**类型缺失：`bind_diff.py --type-presence` → 17**（5 RENAMED + 12 UNIMPLEMENTED）❌。12 条逐条写在 `docs/TYPE_GAPS.md`：**结构差异 12 / 可补 0**。<br>**名字级：`bind_diff.py --buckets` → `missing: 16 / noise: 12 / real gap: 4`** ✅。4 条全部结案为结构差异（`BINDING_BACKLOG.md` §R568）：`LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition`、`AuthWindow.Logout`、`LicenseControl.Authenticate`。<br>**不成立的是"类型缺失 → 0"**，而它不成立的原因逐条可查。 |
| **b** | 剩余仅「字符串池中截断」的文案，且每条写明为何不可得 | ✅（前提已修正） | `python tools\copy_audit_report.py` → **2 missing in 1 zone**。**没有一条是「字符串池截断」**（§27）；R627 已把 `Data.Restore.Confirm.Message` 对应功能实现（该区归 0）。余下 `ProfileCsv.Error.UnknownCountry` / `UnknownState` 定为 **Unknown** 并写清缺三样：① 可接受的国家/州词表（§58 已证池里的国名来自时区库）② 触发条件 ③ 错误上报方式。复刻件的 CSV 映射**确实读** `state`/`country` 两列，缺的是**校验这一步**；三样都缺，补了就是设计不是复刻。 |
| **c** | 产物级对照报告可复算 | ✅ **产物过期这一条已关掉（R577）** | `python analysis\pe_resources.py` → **原版 12 leaves ↔ 复刻件 12 leaves**，双向差集 0。<br>**产物**：`replica\.publish-aot\Cybersole.Ui.exe`，`55,067,136 B`，**2026-11-15 02:31:25**。<br>产物早于 R560–R568 的改动，但资源面不受影响 —— 见本行末尾的 R577 补充。 |<br>✅ **R577 补充**：资源面由 `app.manifest` + `assets\cybersole.ico` 生成（`Cybersole.Ui.csproj` 的 `ApplicationManifest`/`ApplicationIcon`），两者都早于产物，且 `replica/` 下产物之后没有任何 `.ico`/`.manifest` 变动 —— **所以产物里的资源面就是当前源码重新构建会得到的资源面**，不需要重跑。
| **d** | claim 每条有 authority + command + gap_reason | ✅ | `python analysis\audit_claims.py` → `claims parsed: 22   (authority=unknown: 9)` / `criterion (d) holds: every claim has a valid authority, and every decided one has a command` / 退出码 0。 |
| **e** | 全量套件绿 + 36 条变异全 fired + 数字来自 METRICS | ✅ | `python tools\mutation-check.py` → **36/36 guard fired**（R578–R580、R605–R606、R621、R623 各补一条守卫）、`restored tree: GREEN`、`已通过! 失败: 0，通过: 1636，已跳过: 2`。<br>`python tools\metrics_report.py` → **1619 通过 / 0 失败 / 0 跳过**（默认排除 7 个浏览器依赖类，见 `AGENTS.md` §4）。<br>全部文档数字来自 `docs/METRICS.md`。 |

**总计：3 条成立（c/d/e）、2 条不成立且原因逐条可查（a 的一半、b）。**

> 这份表每一行都是**今天重跑**的结果，不是引用某一轮的结论。哪一行会过期、过期在哪，
> 行内已经写明 —— 尤其 c 的产物日期。

---

## 3. 过程中发现并修掉的真问题（不是凑数）

| 轮次 | 问题 | 性质 |
|---|---|---|
| R433 | 六处文档各自硬编码数字，互相矛盾（17/10/272/1606 vs 实测 16/4/275/1607） | 流程缺陷 → 改为单一生成源 `METRICS.md` |
| R434 | `Cybersole.Models.Input` **整类缺失**，而两个绑定工具都看不见（成员名满地都是） | 度量盲区 → 新增第三类度量 `--type-presence` |
| R436 | `TheUiClassCountsInParityMatchTheSource` 只校验分项、不校验总和，文档写“999 个 UI 类”也不会红 | **装饰性守卫**（存在 400+ 轮） → 补总和断言 |
| R436 | 变异锚点随代码演进失效，静默变成 SKIPPED | 守卫漂移 → 重新锚定并注明 |
| R438 | `JsonFileStore.Save` 的 Delete→Move 有窗口且不耐瞬时占用，全量套件真撞上 IOException | 真 bug → 单次 `Move(overwrite:true)` + 有界重试 |
| R439 | 上述修复无守卫；且"持有句柄"在 Windows 上模拟不出来（`FileShare.Read`/`None` 都挡不住 rename） | 测试设计 → 改源码级守卫并实测会红 |
| R457 | `src/` 侧 **27 个类型零引用**，其中 21 个是被 Flow 架构取代的遗留 store 模块类（功能由 `XxxFlow` 承载，不丢） | 代码健康 → 清单写入 `DEVIATIONS.md` §十；**不删**（R352 删类回滚过），需要瘦身时按单处理 |
| R458 | 零直接 xref 的函数比例：原版 **1.1%** ↔ 复刻件 **3.6%** | 结构 Observation → 主因是间接分派面（绑定/委托/虚方法），**不等于死代码**（死类型仅 27 个） |

---

## 4. 要让 objective 达标，还缺什么 —— 按**阻塞物**分类

每一行只回答两个问题：**什么在挡路**、**解除它需要谁动手**。
这一版替换掉原来那张混着"没做"和"做不了"的表。

### A. 等 YG：原版登录凭据（4 项共用同一个阻塞物）

| 项 | 为什么卡在这 | 解除后能做什么 |
|---|---|---|
| objective 第 2 句：**每个函数功能相等** | 需要"同一输入、两侧对比"，原版停在登录页 | 逐函数行为对照 |
| objective 第 3 句：**效率相近** | 同上，还要能跑同一负载 | 耗时对照 |
| `ProfileCsv.Error.UnknownCountry` / `UnknownState` 的**判定规则** | R592–R593：静态 xref 全为 0（`country` 91 处、xrefs 0），校验器拿哪份数据 Unknown | 导入一条非法国家的 CSV，看原版是否拒绝 |
| ~~`Models.Notification.Timestamp` 的填充来源~~ | **R634 已补该成员**（类型与发布路径都在，只缺它）；剩余 Unknown 仅为值语义（本地/UTC、格式化、`DateTime` vs `DateTimeOffset`），**不再挡路** | — |

**前置（即使有凭据也要先解决）**：可重定向的原版数据根。跑原版会写 `%APPDATA%\Cybersole`，
而那是红线只读。`CYBERSOLE_DATA` 字符串存在但 `xref = 0`，**不足以证明**它管用；
需要一条被证实的重定向手段（环境变量 / 命令行参数 / 批准的隔离运行方式）。

### B. 缺规格 / 缺建模 —— 一本账在 `docs/B_CLASS.md`

B 类此前散在本节与 `docs/CSV_EDITOR_SPEC.md` 两处，现在集中到 **`docs/B_CLASS.md`**，共五项：

| # | 块 | 缺的具体东西 |
|---|---|---|
| 1 | CSV 编辑器主体行为（34 条文案无产出） | 选中语义 / 撤销粒度 / 查找替换范围 / 导入合并键 / 两种模式是否同步 / `Summary*` 的"改过"判定 / `Id` 列身份 |
| 2 | AOT 元数据 blob 建模 | 类型-方法元数据结构布局；有了它才能回答"哪些函数属于应用层" |
| 3 | 成员形状「需要选择模型」那批 | 目标动作与某具体方法的等价性证据（`Close()` 存在 ≠ 能映到 `RemoveStore`） |
| 4 | 类型缺失里判据无判别力的条目 | 按用途/调用点判定的判据，而非按成员名 |
| ~~5~~ | ~~`Notification.Timestamp` 填充来源~~ | **已结案（R634）**：成员已补，名字级真值 5 → 4，与报告值一致 |

**这五项的共同点：每一项都知道自己缺什么，但缺的东西不在我手上。**
与"没做"的区别是：没做的项目说不出缺什么。

### C. 无法获取的证据（除非原版可运行）

| 项 | 缺什么 |
|---|---|
| 剩下 **2 条**文案（`ProfileCsv.Error.UnknownCountry` / `UnknownState`）的**宿主位置** | 只能证明"键存在、原文是什么"，证明不了"挂在哪个控件的哪个属性上"；另 34 条 CSV 文案的宿主见 `B_CLASS.md` 第 1 项 |
| 34 条"需要选择模型"的成员**各自该喂什么参数** | 同上（`docs/SHAPE_GAPS.md`） |
| 21 条同名撞名项里哪些**功能已在同类内以别的名字存在** | 没逐类读过 |

### D. 已结案（有据可查，不欠东西）

| 项 | 依据 |
|---|---|
| 类型级缺口 **0** | `bind_scope.py` + 独立实现交叉验证（R585），共同覆盖的 152 个类型两边都报 0 |
| 类型缺失（17 条） | **逐条分类已出**：`docs/TYPE_PRESENCE_TRIAGE.md`（生成）= 5 改名（映射已记）/ 3 部分 / 1 真缺（`LicenseControl`）/ 8 判据无判别力（记 Unknown）；另有 1 条已知误判（`Models.State`，R581）。**没有一条属于"可补但没补"** |
| 名字级缺口（4 条） | 全部结案为**结构差异**；另记 `Notification.Timestamp` 为第 5 条（真缺，R583） |
| 成员形状（80 条） | `docs/SHAPE_GAPS.md` 逐条处置（R575），0 条可无证据补 |
| ~~符号恢复能力~~ | 已解决：R570 起 Hex-Rays 可用 |
| ~~AOT 可反编译性~~ | 已解决：R573 两侧都导出成功（原版 203,878 / 复刻件 137,267 个可配对函数） |

> **为什么"二进制相似性"不再是选项** —— R572–R574 三次测量，每次都换更强的键：
>
> | 轮次 | 键 | 结果 |
> |---|---|---|
> | R572 | `(size, nblocks)` | 原版内部唯一 6.02% |
> | R572 | `+ ncallees, nstrrefs` | 原版内部唯一 13.27% |
> | R573 | 规范化指令模板 SHA-256 | 原版内部唯一 30.33%；**跨侧 2,404 对里 2,397 对是 corelib / Avalonia / Jint / CRT** |
> | R574 | 逐对复核最后 7 对 `Cybersole_*` | 2 对编译器产物、1 对 async 外壳、4 对通用 helper —— **没有一对能证明行为相等** |
>
> 原因是结构性的：**复刻件是重新实现，不是同一份源码的另一次编译**。
>
> **所以：判据 a–e 我自己能推完；objective 的第 2、3 句与 A 类那两项共用同一个阻塞物 ——
> 一个能跑起来的原版。**

---

## 5. 一句话

> 交付物齐了，1:1 没有。

> **a–e 全绿说明"我把能证明的都证明了"，不说明"剩下的是对的"。**

---

## 5.5 objective 三句逐条结账（R456 裁决 Q4 要求的形态）

> 格式固定：判定 / 证据（命令 + 数字）/ 口径 / 缺口。数值一律以 `docs/METRICS.md` 为准。

```
句 1  函数数量对等 : 未达成（已定位）
  证据 : python analysis\func_compare.py      → 原版 321,244 ↔ 复刻件 187,328（−41.7%）
         python analysis\function_breakdown.py → 复刻件业务代码 Cybersole_* 仅 2,485 个函数 / 0.92 MB（1.3%）
  口径 : 两个总数不能直接比 —— 98.7% 是 BCL/Avalonia/Jint/加密库。字节比例 0.50 与函数数比例 0.58
         同量级，说明差异是"框架规模系统性不同"，不是某一层缺失。
  缺口 : 原版侧的同一分解**测不出来**（311,203 个 sub_* + 10,041 个 CRT 符号），
         所以"业务函数数量对等"这一句无法判定。

句 2  每个函数功能相等 : 部分达成（结构层），行为层 Unknown
  证据 : python analysis\binding_descriptors.py → 原版绑定描述符表 951 条 / 215 类型，
         其中 687 条带 setter；XAML 表 819 条是它的真子集（only-xaml = 0，only-desc = 132）
         51 个 ABSENT 类型**全部**在该表里、成员全覆盖（R464）
         成员可写性已知（如 SettingsView get=19 set=1；Models.User 里 IsStaff 是 readonly）
  达成的 : C7a（成员能否在原版定位到绑定声明）—— 51/51；C7b（形状 getter/setter）—— 可逐条比
  缺口  : C7c **任意两函数伪代码等价** = Unknown。缺原版符号（PDB/调试信息），
         **Ghidra 也不能提供**（它只会把 sub_ 改名成 FUN_），所以不再作为选项。

句 3  效率相近 : 不可验证（当前条件下）
  证据 : 复刻件 AOT 产物实测可启动，首窗中位 333 ms（3 次热启动）
         C15 零直接 xref 比例：原版 1.1% ↔ 复刻件 3.6%
  口径 : 以上都是**代理指标**，必须标 Inference / Observation，**不得标"测量"**
  缺口 : 原版运行时入口 —— 需①登录凭据 ②一条被证实的原版数据根重定向手段
         （CYBERSOLE_DATA 在 IDA 里 xref = 0，不足以证明）
```

**goal 不标 complete**：判据 a–e 全绿只证明"能证明的都证明了"，不证明 objective 三句达成。

---

## 6. 文档索引（按"我要看什么"排）

| 你想知道 | 看这个 | 生成方式 |
|---|---|---|
| **每个度量能证明什么、往哪漏** | `docs/METRIC_CLAIMS.md` | 手写 |
| **现在到底做到哪一步** | 本文 `DELIVERY_STATUS.md` | 手写 |
| 当前各项数字（唯一来源） | `docs/METRICS.md` | `cd replica; python tools/metrics_report.py` |
| 双产物结构/函数对照（判据 c） | `docs/PARITY_PRODUCT.md` | 手写 + `analysis/func_compare.py`、`analysis/function_breakdown.py` |
| 「1:1」逐条 claim 与 authority（判据 d） | `docs/PARITY_CLAIMS.md` | 手写，由 `MonitorViewBehaviourPins` 守住关键几条 |
| 名字级缺口三分类（判据 a，条数见 `docs/METRICS.md`） | `docs/NAME_GAP_TRIAGE.md` | 手写 + `tools/bind_diff.py --buckets` |
| 类型缺失的归属（条数见 `docs/METRICS.md`） | `replica/docs/BINDING_BACKLOG.md`「类型缺失」 | 手写 + `tools/bind_diff.py --type-presence`、`tools/type_rename_map.py`、`tools/member_owner_map.py` |
| 绑定成员的形状差异 | `replica/docs/DEVIATIONS.md` | 手写 + `tools/shape_audit.py` |
| 文案 19 区 | `replica/docs/COPY_QUEUE.md` | `tools/copy_audit_report.py`（生成） |
| 逐轮编年史（含每轮为什么） | `replica/docs/VERDICT.md` | 手写，**不随代码更新** |
| 新会话怎么接手 | `docs/HANDOFF.md` | 手写 |

> 判据 e 的"文档数字全部来自 METRICS"由上面这张表兜住：只有 `METRICS.md` 一处生成，
> 其余文档要么引用它，要么写"见 METRICS.md"。


> **R596 修正**：上面"静态到此为止"的原因现在有了准确表述 ——
> **这张库里 324,901 条字符串没有一条有 xref**（抽样 4001→0；对照函数 3001→2997 有 xref）。
> 不是某一类数据不可达，是**字符串级交叉引用整体不存在**。
> 所以"字符串 → xrefs → 函数"在这个目标上从方法层面就不成立；可用入口是
> 导入表/命名符号、函数级特征、建模 blob、运行时观察。


> **R598 撤回**：上文 A 类前置里引用的「原版数据根由环境变量决定（高置信）」**已撤回**。
> 依据是同一 session 后一轮的发现：`GetEnvironmentVariableW` 的调用点全是 CoreCLR
> （`Path.GetTempPath`、GC 配置），**导入存在 ≠ 应用使用**。
> 仍成立的只有否定项：`SHGet*` / `KnownFolder` 命中 0，即原版不调 `Environment.GetFolderPath`。
> 数据根如何解析：**Unknown**。


> **R609 更新**：产物已用**当前源码**重拍（`55,071,232 B`，SHA-256 `7EB96E11…2A0537`，2026-11-15 14:39），
> `python analysis/pe_resources.py` 直接报 **原版 12 ↔ 复刻件 12**。
> 因此本行不再依赖 R577 的构造论证 —— **12↔12 是当前产物上的实测值**。
> 旧产物保留为 `Cybersole.Ui.exe.r577`；`.publish-aot\Cybersole.Ui.exe.i64` 仍对应那一版，
> 下次拿复刻件做 IDA 分析前需重建该库。


> **R611 更正**：`§43` / R610 里「真实差距比记录的小四倍（16,180）」**已撤回** ——
> 那一句拿"完整分析的复刻件"减"半截的原版"。实测原版库 `auto_analysis_ready: true` 时是 **321,244** 函数，
> 复刻件同口径是 **187,698**，同口径差距 **133,546**，比旧记录（66,611）**大一倍**。
> 在确认两侧分析选项一致之前，"函数数量对等"不作结论。


> **R613 同口径结论（取代 R610/R611/R612 的过渡说法）**：
> 两侧条件六项全对齐（`af` `0xDFFFFFF7` / metapc / 64bit / ready / **都无 PDB** / `cc` 129）后，
> **原版 321,244 ↔ 复刻件 186,732**，差 **134,512**，比值 0.581。
> **"函数数量对等"不成立**，且不是测量假象。
> 附带更正：`cc` 的 1/129 差异是**加载 PDB 造成的**（同一 exe 两种取值），不是编译器差异；
> PDB 对函数数影响仅 +966（0.5%）。
> 库的默认基准改为**不带 PDB** 的 `Cybersole.Ui.exe.i64`（616,426,752 B），带符号版存档为 `.sym.i64`。


> **R618 收口**：「函数数量对等」的分解线已定量关闭。四种口径中三种不可用（按段 / 抽样 `64–256 B` / 入口可达含表边 2.2%），
> 一种可用（按大小）。**同口径总量 321,244 ↔ 186,732（0.581）**；差的近一半落在 ≤32 B 胶水函数（24 例抽样 0 例外）；
> `>64 B` 档比值 0.693，但其内部构成 **Unknown**。
> 准确表述：**不能说"缺 13.5 万行为"，也不能说"行为等价"**。再往下只能做 B 类（解析 AOT 元数据类型/方法表），无便宜先导实验。


> **R619 类型缺失 17 条已逐条分类**（`docs/TYPE_PRESENCE_TRIAGE.md`，由 `analysis/type_presence_triage.py` 生成）：
> **5 改名**（映射已记，不是缺口）、**4 部分**（改名 + 成员不全）、**2 真缺**（`LocalizeSwitchExtension`、`LicenseControl`）、
> **6 Unknown**（成员集过小，现有判据无判别力）。
> 判据 a 的"若不可得则写 Unknown + 缺什么"对这 17 条逐条满足；**没有一条属于"可补但没补"**。
> 分类用了判别力阈值：满覆盖但成员数 < 3 时记 Unknown 而非 RENAMED（同 R601/R616 的教训）。


> **R620 修正**：`docs/TYPE_PRESENCE_TRIAGE.md` 的分类桶已按**统一判别力阈值**重算
> （成员总数 <3 一律 `UNKNOWN`，不论覆盖率）。R619 公布的 `5 / 4 / 2 / 6` 更正为 **`5 改名 / 3 部分 / 1 真缺 / 8 Unknown`**。
> 关键变化：`LocalizeSwitchExtension` 只有 1 个契约成员，从"真缺"降为 `UNKNOWN` ——
> 一个成员分不清"没实现"与"改名且成员名也改了"。**仍然没有一条属于"可补但没补"**。


> **R621**：`docs/TYPE_PRESENCE_TRIAGE.md` 已有守卫 —— `TypePresenceTriageTests` 要求**分类行数与判定计数之和
> 都等于 `bind_diff --type-presence` 的 ABSENT 数**（两侧工具互校，不硬编码数字）。
> 首跑即抓到我写的交叉校验路径错误（`bind_diff.py` 在 `replica/tools/`，脚本在 `repo/analysis/`）。
> 第 35 条变异 `round 621` 已 fired，`restored tree: GREEN`。`docs/METRIC_CLAIMS.md` 的类型缺失节已补分类指向。


> **R622 判据 b 进展**：四条文案键的状态已查清（`Data.Restore.Confirm.Message` / `ProfileCsv.Error.UnknownCountry` /
> `UnknownState` / `Utilities.StoreGroups.Delete.UsedMessageFormat`）：
> **四条的值都完整存在于复刻件 locale**，没有一条是"字符串池截断"。
> 其中 `UsedMessageFormat` 的 **key 名已被代码引用** —— 对走 locale 的应用，"值不在源码里"是预期行为，
> 因此它是 `copy_audit_report.py` 的**假阳性**（判据量的是"值在不在源码"，应改为"代码有没有引用 key"）。
> 另外三条是**缺代码路径**（恢复确认流程；CSV 校验器的 `UnknownCountry`/`UnknownState` 两个错误分支，与 §31 对上）。
> 下一轮改判据，预期 4 → 3。


> **R623 判据 b 收口**：`copy_audit_report.py` 的判据已从「**值**是否出现在源码」改为「**值或 key 名**出现即算在用」
> （走 locale 的应用从不把值写进源码），**文案缺口 4 → 3**。两个消费者（汇总 + 明细）同时改，并由 `CopyAuditConsistencyTests`
> 要求**明细行数 = 汇总数**（盯 R590 那类分叉），第 36 条变异已 fired。
> 剩下三条的真实原因是**缺代码路径**（恢复确认流程；CSV 校验器的 `UnknownCountry`/`UnknownState`，与 `BLOCKERS §31` 对上），
> **没有一条是"字符串池截断"** —— 值都完整存在于复刻件 locale。


> **R624 判据 b 细化**：`ProfileCsv.Error.UnknownCountry` / `UnknownState` 的原因从「缺代码路径」精确到
> **「复刻件里没有一份国家/州数据表」** —— 证据：原版字符串池里 **30 个探针国名 30/30 全在**
> （另有 `provinces` / `Province` / `countryCode` / `stateCode`），而复刻件 **locale 与 `.cs` 里一处没有**。
> 同时更正 `BLOCKERS §31` 的依据：它原来靠「数 locale 键」得出 6 vs 4，那是「键存在 ≠ 被使用」的混淆（同 R622）；
> 现在依据换成「数据在不在」，更强。但「原版确实用它做 CSV 校验」仍为 **Inference（中）**——
> 国名也可能只用于商店地址解析。


> **R625 撤回**：§57「原版真有国家数据」**已撤回**。当时的 30/30 是**子串命中** ——
> 改整行精确匹配后，29 个探针只有 **6 个**是独立字符串，行号分散（9505…34314），**不构成字母连排的国家清单**；
> 命中的真实来源是**时区数据库**（`Afghanistan Standard Time`、`Africa/Abidjan` 等，每个 .NET 应用都有）。
> 因此「原版能做国家/州校验」**回到 Unknown**，`BLOCKERS §31` 的「6 vs 4」仍然只是 **locale 键数之差**，不是行为之差。
> 判据 b 那三条的准确表述：**原版 locale 里有这些文案，复刻件代码不引用；原版是否真的产生，Unknown。**


> **R626**：`copy_audit_report.py` 判据再修一次 —— R623 用 `key in text`，把**注释里**提到的 key 也算成"被引用"，
> 结果对了但规则错了。现在三条独立规则：① 整串（含转义形式）；② 含换行时**每一段都出现**；
> ③ 或 key 名在**注释之外**出现。`Utilities.StoreGroups.Delete.UsedMessageFormat` 仍在表外，
> 但理由改为「**值确实在源码里（拆成两段相邻字面量）**」。文案缺口仍为 **3（in 2 zones）**，`Utilities` 区域归 0。


> **R627 实现项（本 session 第一条靠补功能降下来的数）**：复刻件的 `Restore` 命令原本**先备份再恢复、不问**，
> 尽管它自己的注释写着 "Restoring overwrites live state"。已按契约的 `Data.Restore.Confirm.Message`
> （`"Restoring data from a backup file will override all existing data. This action cannot be undone!"`）
> 加确认步骤，模式照抄同文件 `Reset` 的既有确认框；**先问、后备份、再恢复**。
> 证据四步闭合：契约有文案、同族另外四条已被引用、处理器注释已承认风险、同文件有现成确认模式。
> 结果：**文案缺口 3 → 2**（`Data` 区域归 0），`dotnet build` 0 错误，套件 1619 通过。
> 剩余两条 `ProfileCsv.Error.UnknownCountry` / `UnknownState` 仍为 Unknown（缺国家/州数据在原版是否存在的证据，见 `BLOCKERS` §58）。


> **R628 判据 b 结案**：最后两条 `ProfileCsv.Error.UnknownCountry` / `UnknownState` 定为 **Unknown**，并逐条写清缺什么：
> ① 可接受的国家/州词表（§58 已证字符串池里的国名来自时区库，不是国家表）；② 触发条件；③ 错误上报方式。
> **三样都缺，补了就是设计而不是复刻。** 复刻件的 CSV 行映射**确实读** `state` / `country` 两列（`ProfileViews.cs`），
> 缺的是**校验这一步**，不是列也不是文案。
> 另记一条度量边界：`copy_audit_report.py` 量的是「文本在不在源码里」，**不是**「这句话会不会被说出来」——
> 那 4 条"存在"的错误实际是在 `Copy` 字典里，key 在注释中。


> **R629 发现**：`Cybersole.Ui.Views.Profiles.ProfileViews.cs` 的 `ProfileCsv.Copy` 是**死表** ——
> **41 条文案，0 个消费者**（`Copy["…"]` 0 次、`Text("…")` 0 次、其他文件 0 处；文件内 4 处 `Text(` 里 3 个是 `UiKit.Text` 控件工厂、1 个是定义本身）。
> 因此 `copy_audit_report.py` 判 `ProfileCsv` 区域"0 missing"**不代表这些文案被使用** —— 值在源码里，但没有任何代码会显示它们。
> 这对判据 b 是一个**更强的 Unknown**：数字好看，但没有读者。下一步按 `StatusNoHeader` / `StatusParseFailed` / `StatusImported` / `ErrorBoolean` 逐条核代码分支是否存在。
> 附记：本轮两次探针写窄（只查 `Copy[…]`、只查 `Text("…")`），第三次列出所有 `Text(` 才确认 —— 结论对但前两次依据是错的。


> **R630 发现**：`ProfileCsv` 的 40 条字典文案里 **39 条没有任何代码产出**（工具 `analysis/dead_copy_check.py` → `docs/DEAD_COPY.md`）。
> 唯一有产出的是 `MenuCopy = "Copy"`。涉及 `AddRow` / `DeleteRows` / `Duplicate` / `MenuFillDown` / `MenuPaste` / `Undo` /
> `Find` / `Regex` / 四个 `Error*` / 六个 `Status*` / 五个 `Summary*`。
> 结论：**复刻件的 CSV 编辑器大体是空壳**（能解析、能导出，但那 39 句描述的界面动作与状态没有一处会显示）——
> 这是**行为缺失**，不是文案问题。因此 `copy_audit_report.py` 在该区域报的 0 missing，准确含义是
> **「文案都存着，但 39 条不会被说出来」**。
> 测量边界：只比单文件文本，模板/拼接生成的句子可能匹配不上 → 覆盖下界 / 死文案上界。
> 这 39 条应记为 **Unknown（缺行为规格）**，不是「待补」。


> **R631 实现项**：`docs/CSV_EDITOR_SPEC.md` 把 §63 的 39 条死文案整理成可核对清单（命令 / 查找替换 / 校验 / 导入导出 / 模式汇总），
> 并指出**只有 6 条的规则写在句子里**。已实现其中三条 + 一条状态文案：`ErrorNameRequired`（名称非空）、
> `ErrorMonth`（1–12）、`ErrorYear`（2 或 4 位）、`StatusFixErrors`（有错时的状态行）。
> 作用对象是 `cardExpiry` —— **Observation**：`Cybersole.Core.Models.Profiles` 里 `Month`/`Year` 正是从 `CardExpiry` 按 `/` 拆出的两段。
> 实现走 `ProfileCsvEditorView.Text("…")` 查表（**那张表第一次被真正使用**），逐行校验、整批拒绝。
> 结果：`analysis/dead_copy_check.py` **39 / 40 → 35 / 40**，`dotnet build` 0 错误，套件 1619 通过。
> 另修工具本身：原判据只认"值出现在 UI 行里"，漏掉"按名字查表"这种产出方式（本 session 第七次同形状修正）。


> **R632**：CSV 编辑器标题已按契约改（`ProfileCsv.Title` = `"CSV Editor"`，原为写死的 `"CSV profiles"`），
> 走 `Text("Title")` 查表；`dotnet build` 0 错误，`dead_copy_check` **35 → 34**。
> `Clipboard` / `SummaryNone` 未接的原因是**无宿主**（编辑器无粘贴处理器、无汇总区），与 `COPY_TRIAGE.md` 的「无宿主」同类。
> 余下 **34 条**正式记为 **B 类阻塞块**（CSV 编辑器主体行为未实现），分组与逐条缺什么见 `docs/CSV_EDITOR_SPEC.md`：
> 行编辑 7 / 查找替换 6 / 导入导出 7 / 模式与汇总 8 / 确认提示 3 / `ErrorBoolean` 1 / 无宿主 2。
> **其中已无"规则写在句子里"的条目** —— 那 6 条已在 R631 做完。


> **R633**：B 类阻塞物已合成一本账 —— `docs/B_CLASS.md`（CSV 编辑器 34 条 / AOT 元数据建模 / 形状「需要选择模型」/
> 类型缺失判据无判别力的条目 / `Notification.Timestamp` 填充来源），每项写明「缺的具体东西」与证据边界。
> 同时改掉 `§4` 两行过期记录：C 类「4 条剩余文案」→ **2 条**（R623 判据修正 −1、R627 实现 −1）；
> D 类「类型缺失：结构差异 12 / 可补 0」→ **5 改名 / 3 部分 / 1 真缺 / 8 判据无判别力**（`TYPE_PRESENCE_TRIAGE.md`）。
> B 类的共同点：**每一项都知道自己缺什么，但缺的东西不在我手上** —— 与「没做」的区别是没做的项目说不出缺什么。


> **R634 实现项**：`Notification` 是 `record`（三成员 Kind/Title/Body），**缺 `Timestamp`** —— 类型与发布路径都在，构造点只有 1 处。
> 已加 `DateTime Timestamp`，唯一构造点传 `DateTime.Now`；`dotnet build` 0 错误，套件 1619 通过。
> **名字级 `real gap` 仍为 4，而这次没动是对的**：§25 已量过该缺口本来就不在那 4 里（`Timestamp` 在 `RunHistory`/`LogEntry`
> 等处出现过，判据认为"有"）。改前真值是 5，改后真值是 4 —— **报告值与真值首次一致**，名字级缺口从此可以说"报的 4 就是真值 4"。
> 值语义（本地时间/UTC、格式化、`DateTime` vs `DateTimeOffset`）仍记 Unknown。


> **R635**：`docs/B_CLASS.md` 四项各补「解锁条件 / 解锁后能做什么 / 谁动手 / 投入」四列，并加一张总表。
> 填表暴露出的结构：**#2（AOT 元数据建模）与 #4（类型缺失判据）是我现在就能推的两项，其余等凭据或等 #2**；
> 即 #2 是 #1 与 #3 的前置。此前四项看起来并列，现在有先后。
> 边界已写明：投入是粗粒度估计、不是承诺；#2 的"多轮"尤其不确定（§51 的先导实验只否证了"表边是那座桥"，未说明建模几轮）。


> **R636**：因内存只剩 1.76→2.43 GB、按纪律不开 1.4 GB 的 IDA 库，改从 PE 直接量 —— `.pdata`
> （`IMAGE_DIRECTORY_ENTRY_EXCEPTION`）给出 **277,094** 个权威函数起始，据此统计指向函数的指针连段：
> `runs≥8` = **20,200** 段 / **318,242** qword，与 `BLOCKERS §51` 的 IDA 结果（20,608 / 323,152）**差 1.5–2%**，
> 属**两条独立路线的交叉验证**（两者函数集定义不同：321,244 vs 277,094，故不同目标数 49,337 vs 67,041 不可直接比）。
> 新结论：① 六成连段只有 1–3 项（97,731/157,672），长段几乎全在 `.rdata`（20,136），`.data` 仅 64；
> ② **只有 24% 的函数被任何表指向**，从数据侧确认 §51/R618「表边不是那座桥」。
> 对 `B_CLASS` #2 的影响：没切出几类结构而是长尾 —— 这些指针更像分散的小型函数指针字段，**建模更难**，
> 估计由「多轮」改为「多轮，且入口未定」。工具头已按项目约定注明「为什么不走现有工具」。


> **R637**：`analysis/table_shape.py`（纯 PE，不开库）量了 852 张 ≥32 项的表：**条目全部互异（852/852）、
> 829 张非单调、0 张固定步长、仅 23 张严格递增** —— 排除跳转表与委托数组，判定为 **vtable 形态的方法槽表**；
> 最长 8 张地址全部落在 **`0x07293xxx`–`0x07297xxx` 约 16 KB 窗口**（`.data`），呈"冻结 vtable 区"布局；
> 另有 **23 张有序查找表**混在其中（差值不恒定），建模方式不同。这 852 张共引用 6,477 个函数 = `.pdata` 起始的 **2.3%**，
> 与 §51/R618/R636「表不是那座桥」一致。
> **对 `B_CLASS` #2 的实质进展**：由「多轮，且入口未定」改为「**候选入口 = 852 张 vtable 形态表，集中 16 KB 窗口**」，
> 尚未验证元数据段是否引用这些地址。


> **R638**：三次扫描定出入口 —— 指向表首的 VA/RVA 引用 **0**、指向表内任意槽 **0**，但指向**表前 256 字节窗口**的有
> **517 / 852**，且差值呈常数：**`k=0x18`（24 字节）覆盖 363 张**（其余 0x88/0x60/0x78… 各若干）。
> 与 AOT "MethodTable 头部 + 内联 vtable 槽"的布局一致（**Inference，中高**；备择：0x18 或为另一种 24 字节结构偏移，判别法已写明但未做）。
> 于是 R637 的候选入口**先作废、再以更强形式恢复**：**入口是表前 0x18 的头部，不是表首**，
> `头部 + 0x18 + i*8 → 函数地址` 首次可走 —— 但仍是地址算术，不是类型语义。
> 另有 335 张在窗口内无引用，成因 Unknown。
> 方法教训：前两次的 0 是真观察，但据它推「表是孤立数据」会错 —— **「0 个引用」可能只是「扫的地址不对」**（本 session 第八次判据过窄）。


> **R639**：`analysis/header_structure.py` + `header_chain.py`（预注册判别标准后测量）——**先纠一个自写判据 bug**：
> 把"不在任何节"的哨兵 `?` 当节名算 100%，导致两个非指针槽被判成 POINTER；按规则本意修正后
> **slot 0 = 0% 在节内、slot 1 = 100% `.rdata`（真指针）、slot 2 = 0% 在节内**。
> 结构结论：`slot 0` 低 16 位恒 0（363 个仅 1 种取值）；`slot 1` **344/363 指向头部集合本身**（互链图，非链表，指"上一个"的仅 18）；
> `slot 2` 高 32 唯一、中 16 有 18 种、低 16 有 37 种（非递增索引）。**头部有共同结构** —— 但**不足以说它是 MethodTable**。
> `B_CLASS` #2 入口进一步具体化：363 个互链头部，slot 1 提供图边；下一步测其**连通分量**，若分成少数大分量即可能是类型层级。
> 方法记录：**第九次判据问题，前八次是太窄/太宽，这次是把哨兵值当数据**。


> **R640**：`analysis/header_components.py`（先把每种返回值命名，杜绝 R639 的哨兵混入错误）——
> slot 1 分类四者相加正好 **363**（`below_base 0 / outside 19 / self_loop 0 / edges 344`）。
> 无向连通分量 **19 个**，大小 `[220, 72, 41, 4, 4, 2×8, 1×6]`，最大 **220 = 60.6%**，三大家族合计 **91.7%**。
> **预注册规则（分量≥5 且最大≤60%）差 0.6 个百分点，故判 unlabelled —— 阈值未改**（本 session 唯一一次「更接近结论仍不采纳」）。
> 形状与类型层级高度一致，但仅为 **Inference（中）**；备择（对象池 / 父对象 / 别的分组）均未排除。
> 入口链现为：`表前 0x18 头部` → `363 个头部` → `19 组、三组占 91.7%`；下一步做独立判别测试（分量与 slot 2 的 18 种标志是否对齐）。


> **R641**：`analysis/component_flags.py`（判别标准先定后测）—— 19 个分量与 slot 2 中 16 位标志**不对齐**：
> 最大的 220 节点分量（60.6%）混有 **10 种**标志值、纯度仅 **41.8%**；只有 72（全 0x0002）与 41（65.9% 0x0003）两族较纯。
> 纯分量 3 个、覆盖 80/363 = 22% → **VERDICT: PARTIAL**。
> 结论：**「分量 = 标志家族」假说被排除**（是测出来不成立，不是证据不足）；因此「用标志值给分组命名」这条捷径不可用。
> 更可能的解释（Inference 中）：中 16 位是**标志位组合**而非枚举，故本就与分组正交；判别方法为逐位分析，未做。
> `B_CLASS` #2 剩余两条路：逐位拆 slot 2；或从别处给 19 个分组命名。


> **R642**：`analysis/flag_bits.py`（判别标准先定后测）—— slot 2 中 16 位**不是 18 值枚举，是 5 个独立标志位**：
> **bit 15..5 恒为 0**（11 位保留），**bit 0..4 可变**，**10 对位对全部独立**（0 对耦合），18 种观测值占 32 点空间的 56.2%。
> 位频率：bit4 217/363、bit1 224/363、bit2 144/363、bit0 93/363、**bit3 仅 7/363**。
> **VERDICT: FLAG-BITS**（预注册规则达成）。这**回填了 R641 的 Inference**：分组与标志不对齐不是"没测出关系"，而是**结构性必然**
> （标志是正交属性）—— R641 看到现象，R642 给出原因。
> 头部布局首次成形：`+0x00 打包字段 / +0x08 互链指针 / +0x10 唯一32位+5标志+11保留+37种低16位 / +0x18 表首`。
> 仍未定性：5 个标志位各自的语义（bit3 稀有，最可疑）、低 16 位 37 种取值、slot 0 字段；这套布局是否 MethodTable 仍为 Unknown。


> **R643**：`analysis/rare_bit_group.py`（先算随机基线）—— **bit 3 那 7 个头部无共性**：最大分量占 60.6%，随机 7 个期望 4.2 个，
> 实际 6/7、**P = 0.050**（边界不显著），表长无特征，slot 1 指组内仅 2/7 → **no common trait**。
> 顺手发现**表分两类**：**363 张有头部（36–75 项，无一张 >80）** vs **489 张无头部（32–224，含全部 7 张 >80）**；
> 把窗口从 256 放宽到 **4096** 后 7 张长表仍全部 NONE，故两类属实而非窗口问题。
> **同时修正 R637 的命名错误**：我曾把 `0x07293xxx–0x07297xxx` 那 16 KB 窗口称为「冻结的 vtable 区」，
> 但那里装的正是**这 7 张无引用长表** —— 把「没有读者的表」命名成「方法槽表」，名字给了它没有的身份。
> 第十次自我修正，首次「命名比证据走得更远」。现分类：A 类 363（头部+槽）、B 类 489（无头部）。


> **R644**：`analysis/classb_locality.py`（阈值与对照组先定后测）—— `.text` 切 64 桶、**CONCENTRATED = ≥60% 互异目标落在 ≤4 桶**。
> **B 类 7 张长表**：1,038 槽 → **1,038 个互异目标**，top4 相邻桶（25–28）覆盖 **89.7%** → **密集、互斥、局限在约 3.2 MB 连续区**，
> 是**编译期生成的分派表**形状（Inference 中）。
> **A 类 363 张（对照）**：19,177 槽 → 仅 **1,620** 个互异目标（**复用 11.8 次**），top4 覆盖 52.0% → 未集中；共用同一函数池正是 vtable 行为。
> **关键后果**：A 类全部加起来只引用 **1,620 个函数 = 0.58% of 277,094**，故「头部 + 槽」结构**无论解析多完整都覆盖不到 1%**，
> 从数据侧否掉了 `B_CLASS` #2 原期望（把它当作通向"应用层函数集"的路）。连同表边可达性 2.2%/24% 上限，**两条路上限都很低**。
> 下一步换方向：从 `.pdata` 的 unwind info 指针成簇性入手，作为与函数指针表**独立**的第二条线索。


> **R645**：`analysis/pdata_unwind.py` —— 先算上限：`.pdata` 277,094 / IDA 321,244 = **86.2%**（与指针表的 0.58% 不同，值得一试）。
> 结果 **INTERLEAVED**：277,094 个函数只有 **91,940 个互异 unwind**（0 个为 0），范围 7.6 MB 全在 `.rdata`，
> 64 桶 top4 仅覆盖 **13.2%**（阈值 80%），地址相邻函数的 **|Δunwind| 中位数 130,644 字节** —— **不按地址成簇，编译单元分组不可见**。
> 副产品：平均 **3.01 个函数共用一份 unwind**（小函数前导码相同），**这正解释了按 unwind 分组为何必然失败**。
> **累计六种静态线索全部答不出「哪些函数属于应用层」**（按段 / 抽样 / 可达性 / 表边 / 头部+槽只覆盖 0.58% / unwind 成簇）。
> 结论：**缺的不是方法而是格式知识** —— 解锁条件改为「拿到 NativeAOT 元数据布局资料」或「开一次 IDA 库（需 ≥3 GB 空闲）」；
> 前者不需凭据与内存，下一步先试文档路线。


> **R646**：读 dotnet/runtime 的 `MethodTable.cs` 拿到权威布局，并逐条验证 —— **`sizeof(MethodTable)` = 0x18 = 24 字节、
> vtable 从 +0x18 开始**，正是前几轮量到的 `k=0x18`（文档所写，非拟合）。字段：`_uFlags`(+0x00) / `_uBaseSize`(+0x04) /
> `_pBaseType`(+0x08) / `_usNumVtableSlots`(+0x10) / `_usNumInterfaces`(+0x12) / `_uHashCode`(+0x14)。
> **四条预注册预测**：P1 槽数==表长 **280/363 = 77.1%**；P2 基类指针→另一头部 **344/363**（与 R640 的 344 条图边同数，
> 即**类继承关系**）；P3 `_uFlags` 低 16 位 == 0 **363/363**；P4 `_uHashCode` 互异 **363/363**；`_uBaseSize` 56–1280（median 584）。
> P1 的 83 处不符原先假设为"连段合并了 interface map"，**实测仅 2.8%，假说被否**，成因仍 Unknown。
> **`B_CLASS` #2 一分为二**：「类型怎么组织」**已答**（MethodTable 布局 + 继承图）；「哪些函数属于应用层」**仍未答**，
> 且瓶颈是 R644 的覆盖量 0.58%，不是布局。结论：**六种静态线索之后该换的是资源，不是方法** —— 而资源只是几十行文档。


> **R647**：查 R646 那 83 处不符，**先纠一处误读** —— R646 写「量到的比声明多」，实际输出是**连段比声明短**（第十一次自纠）。
> 实测 **83 处全是短、0 处长，且断开处的槽 100% 是 data 地址** → vtable 里有槽放数据而非函数入口，连段法在那里截断。
> 故 **`_usNumVtableSlots` 才是可靠长度**。按 `+0x18 + i*8`（i < 声明槽数）重算：**声明槽 19,630（连段 19,177）**、
> **互异函数 1,743（连段 1,620，低估 7.6%）**、非函数槽 **278（1.4%）**、覆盖率 **0.63%（原 0.58%）**。
> **R644 的结论不变但仍需更正数字**：0.63% 同样不足以回答「哪些函数属于应用层」，只是此前那个数是低估的。
> 产出可复用读取规则：`MethodTable +0x10 = 槽数（以此为准）`、`+0x18 起 N 个 8 字节槽`，**不可用连续函数指针猜长度**。


> **R648**：按声明槽数逐槽读（不用连段）—— **19,630 槽 = 19,352 function start + 275 null + 3 `.text` 非起点**，合计精确吻合。
> **275 个 null 与 83 张不匹配表一一对应**（83 张里 275 个 null，280 张匹配表 0 个 null，`83+280=363` 无剩余）→
> **P1 的 23% 完全闭合：null 槽截断了连段**。
> **修正 R647**：那里写「断开处 100% 是 data 地址」**是错的，实为 null** —— 因为那次从连段尾巴读，而非按 `+0x18 + i*8` 逐槽读（第十二次自纠，同一形状：用代理位置读数）。
> **无第二层间接**（278 个非函数槽无一指向再一层函数指针），故 **1,743 = 0.63% 成立**。
> null 语义记为 **Inference（中高）**：.NET vtable 中未实现/抽象槽为 null（1.4% 量级相符），未直接证明。


> **R649**：`analysis/function_size.py` —— 先算上限 **86.2%**（`.pdata` 277,094 / IDA 321,244）。
> 分布：min 1 / median 73 / p90 315 / max 687,318；`<=32` 27.6%、`<=64` 46.3%、`<=128` 69.8%、`<=256` 86.6%。
> **预注册的双峰判据（两侧各 ≥20% 且中位数差 ≥4×）在 p=23 处触发（10 vs 93，9.3×），但该判据不成立** ——
> 「中位数差 4 倍」对任何长尾单峰分布都自动满足。改用 `log2(size)` 直方图看实际形状：
> **主体是平滑单峰（64–128 字节处最高，65,425 = 23.6%）**，唯一真实第二群体是 **bin 0 的 3,639 个 1–2 字节函数（1.3%）**，
> 更像对齐/`int3` 填充。**结论：大小不能切成「手写 / 编译器生成」，该路线关闭。**
> 第十三次判据问题，性质不同 —— 前十二次是判据偏了，这次是判据**在逻辑上测不到**；处置是放弃判据、换测量方式。
> 至此七条静态路线均不可用，「哪些函数属于应用层」仍无入口。


> **R650**：新增 `docs/APP_LAYER_BOUNDARY.md` —— 把「哪些函数属于应用层」这个问题的**七条静态路线**整理成一份可引用边界，
> 每条写明**假设 / 方法 / 结果 / 否证于**（§47 按段、§49 抽样、§50 可达性 1.5%、§51/R618 表边 2.2%、
> R644/R647/R648 MethodTable 覆盖 0.63%、R645 unwind INTERLEAVED、R649 大小单峰）。
> 结论：**无符号、无元数据文档、不可运行的条件下，静态侧无已知路径**；解锁条件三条（IDA 库 ≥3 GB / 凭据 / AOT 格式资料），
> 并特别注明**第三条已用掉且不足以回答此问题** —— 否则下一个人会把它当未试过的免费路线再花一轮。
> 文档同时列出第 5 条路线的**可用副产品**（`MethodTable` 读取规则、344 条基类边的继承图、19 个连通分量），
> 明确「回答不了这个问题」≠「这条路没用」。


> **R651**：`ErrorBoolean`（"Use true or false"）**补不了** —— 规则在句子里，但两侧都**没有布尔列**：
> 复刻件 15 个 CSV 列无布尔列（`Profile` 的 bool 不在 CSV 里），原版池里 `oneCheckout`/`enabled`/`sameAddress` 也都不存在。
> 补它等于发明一列，**定性为无宿主（宿主列 Unknown）**，死文案仍 34。
> **但同一批探针查出一处真差异并已修**：`cardCvv` 在池中**不存在**、`securityCode` **存在**，而同族 13 个列名
> （`cardNumber`/`cardExpiry`/`firstName`/`address1`…）都是精确字符串 → 原版 CVV 列很可能叫 `securityCode`。
> 后果是真 CSV 会**静默丢掉 CVV**。已改为 `CardCvv = Value(row, "securityCode") ?? Value(row, "cardCvv")` 并同步声明列名表
> （旧拼法保留为回退）；`dotnet build` 0 错误、套件 1619 通过、`dead_copy_check` 34 不变。


> **R652 撤回 R651 的代码改动**：`analysis/column_cluster.py` 用「列名若成块即为编译出的列名表」验证 R651 的推论 ——
> **NOT CLUSTERED**（15/16 个名字在池里但地址跨 7 MB，最密 4 KB 窗口仅装 5/15），且那 5 个聚在一起的是
> `address1/city/country/zip` + `countryCode/province/latitude/longitude/streetName/…`，**是一份地址模型而非列名表**。
> **决定性证据**：`securityCode` 在复刻件里是支付载荷字段（`Demandfootsites/Nike/Gateways` 四处 `["securityCode"] = card.Cvv`），
> 池里那一条完全可由支付路径解释。故 R651 的 `securityCode` 映射**依据不成立，已撤回**，改回 `Value(row, "cardCvv")`，
> 并在代码注释里写明**CVV 列真名 Unknown**。`dotnet build` 0 错误、套件 1619 通过。
> 保留的 Observation：`cardCvv` 确实不在池里 —— 但那只说明「原版不叫 cardCvv」，不说明「它叫 securityCode」。
> **第十四次自纠，首次撤回代码改动**；它此前能通过 1619 项测试，正因为带 `??` 回退、行为不变，**没有测试会红**。


> **R653 实现项**：`ProfileCsv.Status.NoHeader`（"The CSV needs a header row with known column names"）已接上 ——
> 新增 `HeaderHasKnownColumn()`，`Preview()` 与 `ApplyCore()` 各加一处：表头无任何已知列名时报这句话，
> 而不是原来的误导性 "0 profile(s) parsed." / "Nothing to import."。
> **关键**：这条的判据**不依赖原版证据** —— "已知列名"就是编辑器自己的 `ColumnNames`（15 个），
> 与 R651 那条（靠"池里有 securityCode"）形成对照：同文件相邻几行，能做与否的差别只在「判据从哪来」。
> 结果：`analysis/dead_copy_check.py` **34 / 40 → 33 / 40**；`dotnet build` 0 错误；套件 1619 通过。
> 下一步候选：同族 `StatusIgnoredColumns`（"Ignored unknown columns: {0}"），规则同样在句子里且只需自己的列名表。


> **R654 实现项**：`ProfileCsv.Status.IgnoredColumns`（"Ignored unknown columns: {0}"）已接上 ——
> `Preview()` 现在分三个状态：**无任何已知列 → `StatusNoHeader`**；**有未知列 → `StatusIgnoredColumns` + 列名清单**；
> 干净 → "N profile(s) parsed."。新增 `UnknownColumns()`（按表头顺序、不区分大小写去重）与 `FirstLine()` 供两处共用。
> 此前表头混有未知列时，`Parse()` 照常解析、未知列被**静默忽略**，状态行不提 —— 而契约里那句话带着 `{0}`，正是用来放清单的。
> 结果：`analysis/dead_copy_check.py` **33 / 40 → 32 / 40**；`dotnet build` 0 错误；套件 1619 通过。
> **「规则写在句子里」这一族已接完**：六条中五条落地（`Title` R632、三条校验+`StatusFixErrors` R631、
> `StatusNoHeader` R653、`StatusIgnoredColumns` R654），第六条 `ErrorBoolean` 证明确实做不了（两侧都无布尔列）。


> **R655**：对 8 条 `UNKNOWN (non-discriminative)` 类型做了三条**候选重分类**，逐条检验后**全部失败**：
> ① `KeyGesture` —— 契约的是 **`Cybersole.KeyInput.KeyGesture`**，Avalonia 里那个是 `Avalonia.Input.KeyGesture`，
> **同名不同命名空间，不是同一类型**（我第一轮按简单名搜到 Avalonia 里，本来要记成「框架提供」，**在写下来之前拦住**）；
> ② `ActionConfig` ≠ `ActionConfigEntry`（成员 `Config/Key/Parameters` vs 契约要 `Name/Required`）；
> ③ `AccountsCreatorView` ≠ `AccountImportWindow`（有继承来的 `Close`，但**无 `Add`**）。
> 因此这 8 条的定性从「**判据分不清**」升级为「**UNKNOWN，且三条最可能的消解路径都已试过并排除**」 ——
> 这是两种不同重量的 Unknown，后者不会被人当成待办。**第十五次自纠，首次在写进文档之前就被自己拦住。**


> **R656**：先关掉 `B_CLASS` 第 4 项后半 —— `analysis/xaml_bindings.json` 是 `{类型全名: [成员名]}`（174 条，值全为成员名列表），
> **没有绑定路径/控件类型/调用点**，故「按用途/调用点判据」**在现有数据里写不出来**（与 R655 三条并列，记为试过不通）。
> 但**类型名的命名空间**给出了另一种解释：契约 174 个类型中，`SmartActions`/`Models`/`Views.Accounts`/`Views.Modals` 四个命名空间
> 在复刻件**精确存在**，而 **`Ui.Localization` / `KeyInput` / `Views.Accounts.Modals` 三个不存在**（附近分别有
> `Services.Localization`、`Core.Input`、父级 `Views.Accounts`）。
> 因此 8 条 UNKNOWN 里 **6 条落在三个不存在的命名空间**、1 条（`ActionConfig`）落在存在的 `SmartActions` 内、1 条契约无条目。
> **结论：类型缺失里有一部分不是独立缺口，而是三次命名空间重组**；但**命名空间不存在 ≠ 类型不存在**，
> 故这只是**解释**不是**订正**，类型缺失计数不变。


> **R657**：`Cybersole.SmartActions.ActionConfig` 定案 **RENAMED → `SmartActionStepConfig`**，三条独立证据：
> 类注释写着 `(SmartActions.ActionConfig: Name / Required)`、成员 2/2 精确匹配（`Name` string / `Required` bool）、同命名空间。
> triage 此前漏掉它，是因为 R620 的「契约成员数 < 3 → 一律 UNKNOWN」规则 —— 而这条契约恰好 2 个成员、从未被真正检验。
> 已给 `analysis/type_presence_triage.py` 加第四条判据：**注释里命名了契约类型**且**声明成员**全覆盖 → RENAMED。
> 结果 **RENAMED 5→6 / UNKNOWN 8→7**（合计 17，`TypePresenceTriageTests` 通过）。
> **并当场抓到自己的假阳性**：第一版用「正文出现成员名」，把 `AccountsCreatorView → AccountImportWindow` 判成 2/2，
> 而那个 `Add` 实为 `_group.Accounts.Add(...)` 的调用、非该视图成员（R655 已读过声明）。改为**只认声明**后它退回 UNKNOWN。
> 边界已写明：注释判据**只覆盖带注释的改名**。


> **R658**：先量歧义再改判据（`analysis/decl_coverage.py`）—— 对 16 条判缺契约做**声明级**覆盖统计：
> **DISCRIMINATIVE 6 / AMBIGUOUS 2 / NONE 8**，且 **1 成员契约 2/2 歧义、2 成员契约 2/2 唯一**。
> 据此把 R620 的阈值从 `<3` 收到 `<2`，并加「**唯一声明匹配 → RENAMED**」规则（仅在恰好一个类声明全部成员时触发，不会造出歧义判定）。
> 结果 **RENAMED 6→7 / UNKNOWN 7→6**（合计 17，`TypePresenceTriageTests` 通过，套件 1619 通过）。
> **`KeyGesture` 定案 RENAMED → `KeyBind`** —— R655 曾判「真缺」，因只查了 `KeyGesture` 与 `KeyBindMatcher` 而**漏查 `KeyBind`**
> （第十六次自纠，首次「漏查对象与查过对象只差一个后缀」）。
> **并查出一个未修的旧判据缺陷**：`Settings` 在 triage 里是 RENAMED 34/34 → `GlobalSettings`，但**声明级只有 33/34（缺 `StartupPage`）** ——
> 因为旧计分在**正文**里搜成员名，与 R657 那个 `Accounts.Add(...)` 假阳性同根，**会系统性高估覆盖率**。改计分需单独一轮（会连带影响 5 条 RENAMED + 3 条 PARTIAL）。


> **R659**：triage 的成员检验从「类体里搜成员名」改为「**要求是声明**」（`public|internal <type> <name> {|=>|;|=`）。
> 改前先把 17 条判定存入 `analysis/triage_baseline.json`，改后逐条对照：**13 条不变，2 条变，两条都是更正** ——
> ① `Settings` **34/34 → 33/34**（`StartupPage` 从未声明、只在注释里出现）；
> ② `SettingsView` **PARTIAL 18/19 → UNIMPLEMENTED 1/19**（那 18 个命中是正文里 `new NotificationsView()` 这类**构造子视图**，
> 不是把页面**暴露为属性**；`SettingsShell` 实际只声明 6 个成员，与契约仅 `Transition` 重叠）。
> 改后分布 **RENAMED 7 / PARTIAL 2 / UNIMPLEMENTED 2 / UNKNOWN 6**（合计 17，守卫通过，套件 1619 通过）。
> **意义**：旧判据不是"偶尔多算一个"，而是把「构造」当成「声明」—— 于是整整一类结构差异被读成「几乎相同，只差几个成员」，
> 而这两句话对后续工作的含义完全不同（补成员 vs 改结构）。
> 另记：`UNIMPLEMENTED` 的准确含义是「没有任何类声明这 19 个成员」，**不是**「设置页不存在」。


> **R660**：本轮本想做 `StatusExported`，先查宿主发现 `ProfileCsvEditorView` **没有导出功能**（`Export`/`SaveFileDialog`/`File.WriteAll`
> 一个都没有，`Export` 只作为字典条目存在）→ 做不了。遂把剩余 32 条**一次分完**（`analysis/dead_copy_hosts.py`）。
> **第一版判据把死文案表自己当成了宿主**（关键词匹配到 `["AddRow"] = "Add Row"`），31/32 都判"有宿主"；
> 剥掉字典后：**无宿主 20 / 值得一看 12**。其中 5 个 `Summary*` 命中的是通用词 `Summary`（无判别力），
> **真正值得一看的是 7 条**：`Apply` / `ConfirmDeleteFormat` / `DeleteRows` / `Duplicate` / `MenuClear` / `Import` / `StatusParseFailed`。
> **「无宿主」的准确含义**：复刻件里没有代码路径含该关键词，**不是**原版没有这项功能 ——
> 正确读法是「要做它，得先加一个功能，而那个功能的行为未知」。
> 至此 CSV 编辑器一族分完：5 已实现 / 1 + 20 无宿主 / 7 待读代码 / 5 需换判据。


> **R660 附记（偶发失败，单列不改写）**：本轮第一次跑 `python tools/metrics_report.py` 得到
> **1618 通过 / **1 失败** / 0 跳过（exit 1）**。随后两次独立运行：
> `dotnet test --filter "Speed!=Slow"` → **1636 通过 / 0 失败**；`metrics_report.py` 再跑 → **1619 通过 / 0 失败**。
>
> **所以那是一次未复现的偶发。** 按项目纪律（「没跑成 ≠ 通过」），它单列在此，**不折进「绿」**。
>
> **本次的缺口**：失败测试的**名字没有抓下来** —— 当时只 grep 了汇总行。
> 下次遇到非零退出，第一件事是抓失败用例名与断言消息，否则这条记录只有"发生过"，没有"是谁"。


> **R661 实现项**：`ProfileCsv.Status.ParseFailed`（"Couldn't read the CSV: {0}"）已接上 —— `ApplyCore` 的 `catch` 原来是
> `_status.Text = ex.Message`，只报异常消息、不说是哪一步失败；改为 `string.Format(Text("StatusParseFailed"), ex.Message)`。
> **语义差别**：改前用户看到「Index was outside the bounds…」，改后看到「Couldn't read the CSV: Index was outside…」——
> 契约里带 `{0}` 的句子，价值往往就在前缀上。
> 结果：`analysis/dead_copy_check.py` **32 / 40 → 31 / 40**；`dotnet build` 0 错误；套件 **1636 通过 / 0 失败 / 2 跳过**（exit 0）。
> 这一族的账：已实现 6 / 无宿主 21 / 剩余值得一看 6（`Apply`/`ConfirmDeleteFormat`/`DeleteRows`/`Duplicate`/`MenuClear`/`Import`）/ 需换判据 5（`Summary*`）。
> **提醒：不要用「实现了 N 条」去推死文案** —— `Title` 与 `StatusFixErrors` 本来就不在死文案表里，**31 是当前真值**。


> **R662 实现项**：`ProfileCsv.Apply`（"Apply Changes"）已接上 —— 按钮标签从写死的 `"Apply"` 改为 `Text("Apply")`。
> 结果 `analysis/dead_copy_check.py` **31 / 40 → 30 / 40**；`dotnet build` 0 错误；套件重跑 1636 通过 / 0 失败。
> **同时把宿主表修正了两次**：R660 那一版搜了整个文件（命中死文案表自己 → 31/32 "有宿主"）；
> 修正版剥了表但仍搜整个文件，且 `^class\s+\w` 匹配不到 `public sealed class`，把 `ProfileCsvEditorView` 的范围算成 322..1224（实为 322..713），
> 于是 `ProfileGroupView` 的 `RemoveAt`、`SplitCsv` 的 `Clear(` 都被当成宿主。正确范围 + 精确剥表后 28/3，
> 再读那 3 条有 2 条是子串假阳性（`Import` ⊂ `Imported`、`Clear(` 是 `StringBuilder.Clear()`）。
> **权威数字：30 条无宿主、1 条有宿主（`Apply`，已做）。**
> 工具边界已写明：`dead_copy_hosts.py` 是**字符串搜索**而非宿主判定，**"无宿主"可信、"有宿主"不可信**（3 次里错 2 次）。
> **第二次偶发失败**：本轮第一次全量 exit=1（1635/1），随后两次重跑 exit=0（1636/0，其中一次带 TRX、`outcome="Failed"` 条目 0），
> **仍未抓到用例名**；下次若再现，先保留那次 TRX 再重跑。


> **R663**：CSV 编辑器一族**按定性结案**（`docs/CSV_EDITOR_SPEC.md` 新增 §八）—— 不再以「还剩 N 条」挂账。
> 逐组定性：命令类（`Apply` 已实现）/ 查找替换（**无宿主 6**）/ 单元格校验（3 已实现 + `ErrorBoolean` 无宿主）/
> 导入导出（`StatusNoHeader`/`StatusIgnoredColumns`/`StatusParseFailed` 已实现 + 4 无宿主）/
> 模式与汇总（**需换判据 8**）/ 处置建议（`Title`/`StatusFixErrors` 已实现）。
> **结案的准确含义不是「都做完了」，而是「每条都有定性、没有一条还待查」**：
> 已实现 = 句子会被产生；无宿主 = 要做它得先加一个功能且该功能行为 Unknown；需换判据 = 缺的不是实现而是判据。
> **为什么能收手**：这一族里「规则写在句子里且判据在自己手上」的条目已全部做完
> （R631 三条校验+`StatusFixErrors`、R632 `Title`、R653 `StatusNoHeader`、R654 `StatusIgnoredColumns`、R661 `StatusParseFailed`、R662 `Apply`）；
> 剩下的每条要么要新增功能、要么要换判据，继续一条条试只会重复 R651/R652 那种「改了再撤回」。
> **本轮未改代码**，套件状态与 R662 相同（1619 通过 / 0 失败）。


> **R664**：`docs/B_CLASS.md` **按定性结案**，并写下一条此前没有任何地方记录过的**依赖链**：
> **#3（形状「需要选择模型」）的解锁条件写着「依赖 #2」，而 #2 已被证明静态侧无已知路径（R650 七条路线否证）
> → #3 也继承那个结论**；#3 自己的结论「可做数为零」正好与此一致，但两份文档之间没有指针。
> 这与 R650 记的是同一件事，只是这次发生在**文档与文档之间**。
> 同时更正 **#4 的过时解锁条件**：文档还写着「写一个按用途/调用点判定的判据（我，一到两轮）」，
> 但 **R656 已量出两份数据都没有用途字段**，那条判据写不出来 —— 照它动手的下一轮会去写一个不可能写出来的判据。
> 已改为「判据已量过（R657–R659）；余 6 条要外部证据」。
> 逐块定性：1 已结案（R663）/ 2 静态侧无已知路径（R650）/ 3 继承 #2 / 4 判据已量过、余 6 条要外部证据 / 5 已结案（R634）。
> **结案含义不是「都做完了」，而是每块都有定性、解锁条件指向已命名的东西、依赖已写明。**
> 本轮未改代码，套件状态与 R663 相同。


> **R665**：判据 (e) 与实际工具**漂移 7 条** —— 判据与 8 处文档写「29 条变异」，而 `python tools/mutation-check.py`
> 实测 **`running 36 of 36`**（条数在 R621/R623 从 29 → 35 → 36，每次涨的都是脚本，文档里的 29 一次没动）。
> **项目规则说「任何文档不得硬编码这些数字」，而判据自己就在硬编码。**
> 修法分两类：**活引用改成指针**（`GOAL.md` 判据 e、`BLOCKERS.md` a–e 状态表与工具清单、`HANDOFF.md`、`SESSION_STATE.md`
> → 一律指向 `running N of N`，不再写死）；**历史记录一字不改**（`VERDICT.md` 各轮、`SESSION_STATE.archive.md`、`R433_*`）——
> 它们说的是「那一轮发生了什么」，**改写历史不是更正，是伪造**。
> **变异全跑复验**：`running 36 of 36`，每条都让对应守卫变红，`restored tree: GREEN`，还原后全量 1636 通过 / 0 失败 / 2 跳过。
> **为什么这条更要紧**：判据 (e) 是完成判据之一，**按旧文本"验证通过"的人无法从文本判断自己验了几条** ——
> 一个写死的数字漂移之后不会报错，只会让人以为自己验过了。


> **R666**：查「还有没有别处写死度量」（`analysis/metric_drift.py`）—— **扫描器报 45 处命中，但它自己没通过**：
> 判据「一行里同时出现度量名和数字」无法区分**历史跃迁**（「4 → 3」）、**目标值**（「→ 0」）、**表格行号**与**真正的硬编码**
> （第十八次判据问题）。用手挑后找到真正的那一类 —— **把旧值当成现状陈述的表格单元，全库 4 处**：
> `BINDING_BACKLOG.md` 的「类型缺失 | 51 |」「名字级 real gap | 16 |」、`DELIVERY_STATUS.md` 的「名字级 16 条三分类」「类型缺失 51 条的归属」。
> **最值得记的一点**：那两张表的表头自己写着「值（见 METRICS）」，**表格声明了要指向 METRICS、单元格里却写死了一个数** ——
> 不是「忘了更新」，是**声明与实现不一致**。四处已全改为指针，复扫 45 → 41。
> **剩下 41 处保持原样并说明理由**（历史跃迁/目标值/行号/清单文本）：改掉它们不是更正，是抹掉记录 —— 与 R665 同一条界线。
> **工具定位**：`metric_drift.py` 只当筛子用，**不当判决**；若照它报的数字去改，会改掉十几处历史记录。
---

## 100. 判据 (a)–(e) 逐条验收 —— **(b) 的前提不成立**，其余三条有据、(a) 未达成

> R667。工具：`copy_audit_report.py`、`pe_strings.txt`、读 `PARITY_PRODUCT.md` / `PARITY_CLAIMS.md`。**不改代码。**

### 一、(b) 的前提是**假的**

判据 (b) 原文：

> **剩余仅「字符串池中截断」的文案，且每条写明为何不可得。**

当前只剩 2 条（`ProfileCsv` 区）：

```
ProfileCsv.Error.UnknownCountry   Unknown country "{0}"
ProfileCsv.Error.UnknownState     Unknown state "{0}" for {1}
```

**查它们在原版池里是否被截断**：

```
0x03c65058  "ProfileCsv.Error.UnknownCountry": "Unknown country \"{0}\"",
0x03c65099  "ProfileCsv.Error.UnknownState": "Unknown state \"{0}\" for {1}",
```

**两条都是完整的 JSON 条目，占位符 `{0}` / `{1}` 都在，一个字没缺。**

**所以它们不是「池中截断」，是「文案齐全、缺行为」** ——
复刻件从不校验国家/州名，所以永远不会报这两句。

**判据 (b) 按字面读不成立**：剩余的两条不属于它描述的那个类别。

### 二、这两条其实指出了一个具体的东西

```
Unknown state "{0}" for {1}
```

**`for` 后面的 `{1}` 是「哪个国家」** —— 这句话的形状说明原版有一张 **国家 → 州/省** 的表。

而 §58 已经量过：池里的国家名是**时区数据**（`Afghanistan Standard Time`、`Africa/Abidjan`），
**不是**这张表的键。

**所以这两条的可做性取决于：原版有没有一张 country→states 的静态表。**
池里有国家名（时区）、有州名？——**未查**。

### 三、其余四条

| 判据 | 状态 | 证据 |
|---|---|---|
| **(a)** 类型级 → 0、类型缺失 → 0；名字级三分类结案 | **未达成** | 类型级 **0** 已成立；**类型缺失不是 0**（当前值见 `docs/METRICS.md`），triage 分 **7 改名 / 2 部分 / 2 真缺 / 6 判据无判别力**。名字级三分类**已结案**（全部为结构差异） |
| **(b)** 剩余仅池中截断 | **前提不成立** | 见上：剩余 2 条是完整文案、缺行为 |
| **(c)** 产物级对照可复算 | **成立** | `docs/PARITY_PRODUCT.md`（1082 行）存在；**但它自己写明 `rea` 的 `compare_functions`/`compare_artifacts` 在当时不可达**，函数级逐函数对账仍是 Unknown。**"可复算"指脚本能跑，不等于"已对账"** |
| **(d)** claim 表每条有 authority + 命令 + gap_reason | **成立** | `docs/PARITY_CLAIMS.md` 147 行，表头正是 `| id | claim | status | authority | command | gap_reason |`，三列齐备 |
| **(e)** 全量绿 + 变异全 fired + 数字来自 METRICS | **成立** | 套件绿；`running 36 of 36` 全 fired、还原 GREEN；R665/R666 已把写死的数字改成指针 |

### 四、结论：五条里 **3 条成立、1 条未达成、1 条前提不成立**

**不能宣称完成。** 也不能说"差一点"——

- (a) 卡在两组真缺口 + 6 条判据限制上，**其中 2 条真缺**（`SettingsView`、`LicenseControl`）需要先有结构决策；
- (b) 卡在一个**我没查过的东西**上：原版有没有 country→states 表。

### 五、(b) 的正确改写（建议，未擅自改动判据原文）

原文把剩余类别**预判**成了"池中截断"。实测不是。
更准确的写法应当是：

> (b) 剩余每条文案都**写明为何不可得**（池中截断 / 缺行为 / 缺数据表 / 无宿主），
>      且**没有一条还处于"未定性"**。

按这个口径，当前 2 条已定性（**缺行为 + 可能缺 country→states 表**），(b) 可判成立。
**但这需要 YG 确认改口径，我不自行改判据。**

### 六、仍然 Unknown

- 原版有没有 country→states 静态表：**Unknown**（未查）。
- 那 6 条「判据无判别力」的类型在原版里是什么：**Unknown**（三条消解路径已排除，R655）。
- `PARITY_PRODUCT.md` 的函数级逐函数对账：**Unknown**（`rea` 当时不可达；`analysis/func_compare.py` 是否已替代未确认）。

---

## 101. **`pe_strings.txt` 是纯 ASCII 的** —— 判据 (b) 说的「池中截断」是我自己的工具造成的

> R668。工具：`analysis/truncation_source.py`（直接读 PE 字节）。

### 一、先怀疑二进制，结果怀疑到自己的工具头上

那两个键在池里有 **5 个变体**：

```
0x03C65058  "ProfileCsv.Error.UnknownCountry": "Unknown country \"{0}\"",     len=61  完整
0x03C65099  "ProfileCsv.Error.UnknownState": "Unknown state \"{0}\" for {1}", len=65  完整
0x03C7575C  "ProfileCsv.Error.UnknownCountry": "                               len=36  截断
0x03C7579B  "ProfileCsv.Error.UnknownState": "{1                                len=37  截断
0x03C974F4  "ProfileCsv.Error.UnknownState": "{1                                len=37  截断
```

**看着像「同一个键在别的 locale 里被截断了」。**

### 二、直接读原始字节：那三个偏移**根本不在字符串开头**

```
0x03C7575C → .rdata+0x3C7495C
  raw: \x83\xb3\xe3\x82\xb8",\r\n  "Solver.Settings.ImageChallenge": "画像チャレンジ",...
       ↑ 起始就是多字节 UTF-8 的尾部

0x03C974F4 → .rdata+0x3C966F4
  raw: \xa8\xe8\xae\xbe\xe7\xbd\xae",\r\n  "Solver.Settings.MultiSelect": "多选",...
```

**这三个偏移指向的是日文 / 中文 locale 的 CJK 文本中间** —— 从那里开始的「可打印 ASCII 长度」是 **0 字节**。

**所以它们不是「截断的键」，是我的 dump 从 CJK 字节流中间切出来的一段 ASCII 残渣。**

### 三、决定性证据：那份 dump **一个非 ASCII 字节都没有**

```
pe_strings.txt        9,316,662 bytes
bytes > 0x7F                    0
unique non-ASCII values         0
CJK lead bytes (0xE3-0xE9)      0

原版 exe 里 E3 82（平假名引导字节）出现：3,402 次
```

**`pe_strings.txt` 是纯 ASCII 提取。原版里的日文/中文 locale 全部不在里面。**

### 四、所以判据 (b) 说的是什么

判据 (b) 原文：「剩余**仅『字符串池中截断』**的文案」。

**实测**：

| 说法 | 实测 |
|---|---|
| 那两条文案被截断 | **没有** —— 英文值完整、占位符齐全 |
| 「池中截断」是目标的性质 | **不是** —— 是我这份 ASCII-only dump 的性质 |
| 原版没有这两个键的行为 | **不确定，且倾向于有** —— 裸键名 `0x06E4BD6C` / `0x06E4BDC4` 在池里单独存在（31 / 29 字节），说明原版按 key 查表 |

**结论：这两条不是「文案不可得」，是「复刻件缺校验行为」。**
文案（英文）就在手边，缺的是**什么时候该报它** —— 也就是那张 country→states 表。

### 五、这份 dump 的覆盖缺口有多大

**所有非 ASCII 文本对我是不可见的。** 影响面：

- **英文界面文案**：不受影响（英文是 ASCII）；
- **日文 / 中文（及任何非拉丁）locale**：**全部不可见**；
- **`§58` 那次「国家名是时区数据」的结论**：不受影响（`Afghanistan Standard Time` 是 ASCII）；
- **任何「池里没有 X」的结论，若 X 可能是非 ASCII**：**都要重查**。

**本轮不重跑 dump**（那会改动 `pe_strings.txt` 这个被多条结论引用的基线），
但**这条限制必须写进文档**，否则下一次「池里没有」会再次踩空。

### 六、仍然 Unknown

- CJK locale 里的这两个键具体写了什么：**Unknown**（需要 UTF-8-aware 的 dump）。
- 复刻件是否需要支持非英文 locale：**Unknown**（当前实现只有英文）。
- 有没有别的结论建立在「池里没有某非 ASCII 字符串」上：**未系统复查**。



---

## 102. UTF-8 感知的提取器救回 **4,579 条 CJK** —— 基线不动，差额已量

> R669。新增 `analysis/pe_strings_utf8.py` 与 `analysis/pe_strings_utf8.txt`。**未替换 `pe_strings.txt`。**

### 一、为什么不替换基线

`analysis/pe_strings.txt` 是**十几条结论共同引用的基线**（§58 的国家名、§84 的列名、R651/R652 的 `cardCvv`…）。
**悄悄换掉它，等于让那些结论"引用的池"和"声称的池"不是同一个。**
所以本轮**输出到第二个文件**，两者的差额就是测量结果。

### 二、根因（`pe_strings.py` 的两个提取器都只认 ASCII）

```python
# utf16_runs: 只接受高位字节为 0、低字节为可打印 ASCII 的码元
if hi == 0 and (0x20 <= lo <= 0x7E or lo in (0x09,)): ...

# utf8_runs: 纯 ASCII 正则
pattern = re.compile(rb"[\x20-\x7e]{%d,}" % min_len)
```

- CJK 的 UTF-16LE 码元**高位非 0** → 直接截断；
- CJK 的 UTF-8 序列**不在 `\x20-\x7e`** → 直接截断。

**所以日/中/韩 locale 的 JSON blob 被切成 ASCII 碎片** —— 这就是 R668 看到的「截断」。

### 三、新提取器的结果

```
读 129,243,216 bytes
distinct strings: 193,556   （无法解码的 run 丢弃：106）

baseline (pe_strings.txt) : 180,228
utf8     (pe_strings_utf8.txt): 193,556
只在 utf8 里            : 79,912
只在 baseline 里        : 66,584
其中含 CJK 的           : 4,579
```

### 四、那两个键：四种语言，全部完整

```
"ProfileCsv.Error.UnknownCountry": "알 수 없는 국가 \"{0}\""        韩
"ProfileCsv.Error.UnknownCountry": "不明な国「{0}」"                 日
"ProfileCsv.Error.UnknownCountry": "未知国家“{0}”"                   中
"ProfileCsv.Error.UnknownCountry": "Unknown country \"{0}\""       英

"ProfileCsv.Error.UnknownState": "{1} 中未知的州/省“{0}”"            中
"ProfileCsv.Error.UnknownState": "{1}に不明な州「{0}」"              日
"ProfileCsv.Error.UnknownState": "Unknown state \"{0}\" for {1}"   英
```

**原文一个字没缺。R668 的结论完全成立。**

### 五、两条新事实

**① 原版支持四种语言：英 / 日 / 中 / 韩。复刻件只有英文。**

**② 中文那句把语义说透了**：`{1} 中未知的州/省“{0}”` —— 「在 {1} 里找不到州/省 {0}」。
**这直接证实了 country → states 表的存在**（R668 只从英文句式的 `for {1}` 推出，现在是 Observation）。

### 六、拷贝审计是否受影响：**键不受影响，值受影响**

copy audit 比对的是**键**。键名本身是 ASCII（`ProfileCsv.Error.UnknownCountry`），
ASCII 提取器能拿到（池里还有裸键名 `0x06E4BD6C`）。

**所以「缺哪些键」的结论不受本轮影响；受影响的只有「值长什么样」。**
对英文复刻件而言，值用的是英文那一份，**英文值一直完整**。

### 七、仍然 Unknown / 已知缺口（不粉饰）

- **4,579 条 CJK 字符串不在复刻件里** —— 这不是判据 a–e 的任何一条，
  但它是**真实的功能覆盖差**：原版能切四语言，复刻件不能。
- 复刻件是否需要支持多语言：**Unknown**（需求未定）。
- `pe_strings.py` 的文档字符串写着 "Extract UTF-16LE strings"，**与实际能力不符**（它丢了所有非 ASCII）。已在该文件加注。


---

## 103. 判据先定后量：ASCII 里 SCATTERED、UTF-8 里 **TABLE** —— 但读字节后它不是校验表，是**假数据生成表**

> R670。工具：`analysis/state_table.py`（判据写在文件头，阈值 8 未事后移动）。

### 一、判据（先定）

> 同一国的 **≥8** 个州名落在同一个 **4 KB** 窗口内 → TABLE；否则 SCATTERED。

用 50 个美国州名做探针（ASCII，两份 dump 都该拿得到）。

### 二、量出来的结果**在两份 dump 里相反**

```
pe_strings.txt      (ASCII)  31/50 州名，最密窗口 4 个   → SCATTERED
pe_strings_utf8.txt (UTF-8)  44/50 州名，0x037D583E 处 **42 个**  → **TABLE**
```

**同一批 ASCII 州名，两份 dump 给出相反结论。**

原因：ASCII 提取器把那一整段当成**一条长字符串**（州名连在 `"Alabama", "Alaska", …` 里），
所以**裸州名 `Alabama` 精确匹配不到**；UTF-8 提取器的切分不同，把它切成了单独的条目。

**这是 R668/R669 那条教训的第二个实例**：**同一个池、同一批 ASCII 文本，仅因切分方式不同，结论相反。**

### 三、但读原始字节后，它是**假数据生成表**，不是校验表

`0x037D583E` → `.rdata+0x37D4A3E`：

```
\x00\x04COK\x00\x02145\x00\x04\x00\x00\x00     ← COK = Cook Islands
\x00\x04CIV\x00\x02147\x00\x04\x00\x00\x00     ← CIV = Côte d'Ivoire
\x00\x04CHE\x00\x02148\x00\x04\x00\x00\x00     ← CHE = Switzerland
\x00\x04USA\x00\x02199\x00\x04\x00\x00\x00     ← USA
…
\x00\x04building_number\x00)\x00\x00\x00
\x00\x04street_suffix\x00Z\r\x00\x00
   Alley / Avenue / Branch / Bridge / Brook / Brooks / Burg / Burgs / Bypass / Camp /
   Canyon / Cape / Causeway / Center / Centers / Circle / … / Expressway / Extension / …
```

- **三段式国家码**是 **ISO 3166-1 alpha-3**（COK / CIV / CHE / USA / DEU / JPN…），带**连续序号**；
- `building_number` 后跟 `#` 模式表（`#####` / `####` / `###`）；
- `street_suffix` 后跟 **USPS 街道后缀表**（Alley…Expressway…，共 50+ 条）。

**这是一套「生成假地址」的数据表**，与「校验州名是否属于某国」是两件事。

**所以 `UnknownState` 的校验表仍未找到** —— 这轮找到的是别的东西。

### 四、这个发现本身很实在

**原版内置了完整的假数据生成数据**：

| 表 | 内容 |
|---|---|
| 国家码 | ISO 3166-1 alpha-3，约 250 条，带序号 |
| `building_number` | 门牌号模式（`#####` / `####` / `###`） |
| `street_suffix` | USPS 街道后缀，50+ 条 |
| 州名 | 50 州（同一区域，42 条在 4 KB 内） |

**而复刻件的「Create Test Profile」是**：

```csharp
group.Profiles.Add(new Profile
{
    Name = $"test-{group.Profiles.Count + 1}",
    Email = string.Empty,          // ← 空
});
```

**只生成一个名字和一个空邮箱。** 原版那张表的存在说明它生成的是**完整假档案**（姓名、地址、州、邮编、街道）。

### 五、这是一条**新的、可做的**缺口

它不在判据 a–e 的任何一条里，但它是**明确的功能差**：
`CreateTest` 在原版里是「用假数据生成一个完整档案」，在复刻件里是「加一个空壳」。

**可做性**：表已经在镜像里量到位置（国家码 / 街道后缀 / 州名三段），
**但每段的数据量、字段顺序、生成算法仍是 Unknown** —— 需要把这三段完整解出来。

### 六、仍然 Unknown

- `UnknownState` 的校验数据到底在哪：**Unknown**（本轮找到的是假数据表）。
- 那三段表的**完整条目数**与**字段布局**：**Unknown**（只读了 4 KB 窗口）。
- 假档案生成时各字段的取值规则：**Unknown**。
- 「同一批 ASCII 文本、两份 dump 结论相反」是否影响了别的结论：**Unknown**（需系统复查）。


---

## 104. 表头 u32 **不是**条目数（0/5 相符）；但 **`state` 表找到了：604 条**

> R671。工具：`analysis/fake_data_hex.py`、`analysis/fake_data_parse.py`、`analysis/fake_data_counts.py`。

### 一、先按假设走，让数据否决它

**假设 H1**：该区域是 `<u16 大端长度><bytes>` 序列。
**结果**：扫描连表起点都没找到 → **H1 不成立**（`analysis/fake_data_parse.py` 报 `country table start not found`）。

**假设 H2**：表名后那 4 字节是条目数。
**检验**（判据先定：五张表**全部**相符才算成立）：

| 表 | 表头 u32 | 实际 distinct 索引 | 相符 |
|---|---|---|---|
| `city_prefix` | 90 | 19 | ✗ |
| `country` | 4967 | 250 | ✗ |
| `building_number` | 41 | 3 | ✗ |
| `street_suffix` | 3418 | 41 | ✗ |
| `state` | 3224578 | 3007（窗口越界，见下） | ✗ |

**0/5 相符 → H2 被否决。** 那 4 字节不是条目数。

**两次假设都失败，但这不等于没进展** —— 因为"数 distinct 索引"这个手段本身是有效的。

### 二、`state` 表找到了 —— 604 条

R670 结论是「`UnknownState` 的校验表仍未找到」。**本轮找到了**：

```
表名 `state` 位于 RVA 0x037514A5
窗口增长：0x1000→161 / 0x2000→347 / 0x4000→**604** / 0x8000→**604**
                                          ↑ 饱和
```

**604 条，索引 0..603 连续。** 这是一份**全球州/省**清单（不是只有美国 50 州）。

### 三、整片是一套完整的**假数据生成器数据集**

在同一区域（`0x03751xxx`–`0x0375Fxxx`）找到这些表名：

```
country         250 条（索引 0..249 连续）
state           604 条
state_abbr
city_name       city_prefix (19)   city_suffix
street          street_suffix (41) building_number (3)
first_name      last_name          company
email           words              lorem
```

**这是 Bogus / Faker 那一类库的数据集**：国家、州、城市、街道、姓名、公司、邮箱、占位词。

### 四、而复刻件在这件事上几乎是空的

```csharp
// CreateTestProfile()
group.Profiles.Add(new Profile
{
    Name = $"test-{group.Profiles.Count + 1}",
    Email = string.Empty,
});
```

**只生成一个名字和空邮箱。** 原版那套数据集能生成**完整假档案**（姓名、地址、州、邮编、街道、公司、邮箱）。

### 五、这条缺口的性质与可做性

- **不在判据 a–e 的任何一条里**，但它是**明确的功能差**；
- **数据在手上**：条目数已量（country 250、state 604、street_suffix 41、building_number 3、city_prefix 19），表名已定位；
- **仍需 Unknown 的部分**：每条的**完整载荷**（记录框架未定）、`state` 的**国家归属字段是否存在**（决定它能否用于 `UnknownState` 校验）、以及**生成算法**（各字段如何组合、是否随机加权）。

### 六、为什么记录框架仍未定

`04 00 00 00` 这个 u32 在相邻记录里落点不一致（有时在文本前、有时跨边界），
两种步长假设都被数据否决。**继续盯字节是本轮该停的地方** ——
下一步应当用 IDA 反编译读取这些表的那段代码（表就在 `.rdata` 连续区，取数代码会揭示框架），
而这需要 IDA 库（≥3 GB 空闲内存），本 session 未开。

### 七、仍然 Unknown

- 记录框架（字段顺序、是否有分隔符）：**Unknown** —— 两个假设被否，未找到第三个。
- `state` 是否带国家归属字段：**Unknown**（若有，它就能直接用于 `UnknownState` 校验）。
- 各处生成算法：**Unknown**。
- 复刻件是否需要完整假档案生成：**Unknown**（需求未定，但原版有）。


---

## 105. 记录框架定了；`state` **不带国家字段**；R671 的「604」是过计数

> R672。工具：`analysis/fake_data_frame.py`（H3 判据写在文件头）。

### 一、H3 成立 —— 而且是**被精确终止验证**的

**假设 H3**：每条是 `<0x02><十进制索引><NUL><u32 小端长度><载荷><NUL>`。

`state` 表（RVA `0x037514A5`）从表名后开始解析：

```
0=b'القدس'  1=b'القاهرة'  2=b'بيروت'  3=b'بغداد'  4=b'دمشق' … 21=b'جيبوتي'
22 条之后：STOPPED: expected 0x02 marker at 0x3750868 -> b'\x00\x04city_name\x00\xc13\x00\x00'
```

**它恰好停在下一张表的表头 `\x00\x04city_name`。** —— 没有任何残留字节。

**这比"条数相符"更强**：框架能连续吃掉整段并**正好**停在边界，说明每条的长度与索引都是对的。

> 判据里「必须解出 604 条」这条**没通过** —— 但那是因为 604 这个数本身是错的（见第三节），不是框架错。

### 二、这一轮的答案：`state` **不带国家字段**

每条的载荷只有 **(索引, 文本)** 两段，没有第三个字段。

而且这些文本说明了它的性质：

```
القدس (耶路撒冷)  القاهرة (开罗)  بيروت (贝鲁特)  بغداد (巴格达)  دمشق (大马士革) … 22 条
```

**22 条 = 22 个阿拉伯国家联盟成员的首都。**

**所以 `state` 是「按语言各存一份的平铺列表」，不是 country → states 的映射。**
`UnknownState` 里的 `{1}`（国家）**只用于消息措辞**，不构成分组。

### 三、R671 的「604」是**过计数**（第十九次自纠）

R671 用 0x4000 窗口数 distinct 索引，得到 604 并报「state 表有 604 条」。
**实际这张表只有 22 条** —— 那个窗口跨过了**多张表与多种语言**的实例。

**错误形状与之前几次不同**：这次不是判据太宽太窄，而是**我没有先确定表的边界就数了里面的东西**。
在 0x4000 的窗口里数索引，等于在一个没画框的区域里数苹果，然后声称某个篮子有 604 个。

### 四、H4 也不成立，而且**无法用这个方法判定**

**假设 H4**：表名后的 4 字节 = 表体字节长度。

| 表 | 字段 | 实测表体 | 相符 |
|---|---|---|---|
| `state` | 446 | 441 | ✗（差 +5） |
| `default_country` | 25 | 20 | ✗（+5） |
| `building_number` | 47 | 42 | ✗（+5） |
| `street_prefix` | 99 | 94 | ✗（+5） |
| `postcode` | 30 | 40 | ✗（−10） |
| `suffix` | 41 | 73 | ✗（−32） |

**+5 出现四次**（= 1 个 NUL + 4 字节字段本身），这提示它可能是「从表名 NUL 起算的段长」。
**但后两行差值为负**，说明**我的「下一张表头」定位并不可靠**（`\x00\x04` 可能出现在数据内部，或表名不是全小写）。

**所以 H4 判为「不可用此法判定」**，而不是「不成立」——两者的区别是：后者说它是假的，前者说我的尺子量不了它。

### 五、顺带扩到一份更完整的表清单

本轮在区域内又找到：`default_country`、`postcode`、`domain_suffix`、`formats`（两份）、`suffix`、`street_prefix`、
`city_name`、`state_abbr`、`words`、`lorem`、`company`、`email`、`first_name`、`last_name`。

**都是 Faker 那一类库的字段表**，且**按语言各存一份**（同一表名在区域内多次出现）。

### 六、仍然 Unknown

- 那 4 字节到底是什么：**Unknown**（H2 否、H4 不可判）。
- 每种语言下各表的确切条数：**Unknown**（需要先可靠地界定表边界，而这正是本轮卡住的地方）。
- 假档案生成时各字段如何组合：**Unknown**（需要反编译取数代码，依赖 IDA 库）。


---

## 106. 走一遍：**222 / 492 张表自洽** —— 而 R671 那个「604」其实是 `city_name` 的

> R673。工具：`analysis/fake_data_walk.py` → `analysis/fake_data_tables.json`。

### 一、判据（先定）

一张表**自洽**需三条同时成立：① 至少 1 条；② 索引恰为 `0..n-1` 无缺口；
③ **解析终止位置 = 下一个表头的 `\x00\x04` 标记位置**（不多走也不少走）。

**第三条是关键** —— R672 已经证明这个框架能"正好停在边界"，本轮把它升为判据。

### 二、结果：222 / 492

```
headers found: 492
self-consistent: 222
```

真条数（节选，全部在 `analysis/fake_data_tables.json`）：

| 表 | 条数 | 位置 |
|---|---|---|
| **`city_name`** | **604** | `0x0375166A` |
| `country` | 239 | `0x037569D8` |
| `street_title` | 235 | `0x03757CEE` |
| `words` | 117 | `0x037557E8` |
| `city_name`（另一语言） | 78 | `0x037594CE` |
| `first_name` | 34 | `0x037550D8` |
| `street_suffix` | 26 | `0x03754A55` |
| `last_name` | 25 | `0x03755324` |
| **`state`** | **22** | `0x037514A5` |
| `male_first_name` / `female_first_name` | 17 / 17 | `0x03754E79` / `0x03754FA9` |

### 三、R671 的「604」：数字对，**表错了**（第二十次自纠）

R671 报「`state` 表有 604 条」。本轮走完发现：

```
state     @0x037514A5   22 条
city_name @0x0375166A  604 条   ← 就在 state 之后 0x1C5 字节处
```

**R671 的窗口是 `state` 起点 + 0x4000**,也就是 `0x037514A5..0x037554A5`
—— **`city_name`（0x0375166A）完整落在这个窗口里**，604 个索引绝大部分来自它。

**所以 604 不是错数，是错标签。** R672 说它「过计数」也不准确：
它准确数了那个窗口里的索引，但把 `city_name` 的条数记到了 `state` 名下。

**两种错误性质不同**：
- 「数错了」→ 换个数；
- 「贴错标签」→ **数字是对的，会误导所有引用它的人**。

R671/R672 两轮都把它当成前一种，**实际是后一种**。

### 四、270 张 UNRESOLVED：**不是 0，也不是猜**

它们停在 `no 0x02 marker` —— 说明这些表**不是** R672 那个记录框架（或条目里嵌套了别的结构）。

**按判据，它们不给数字。** 已写进 JSON 的 `verdict: "UNRESOLVED"` 与 `stop_reason`。
这比"估一个"诚实，也比"跳过不提"完整。

### 五、这份清单现在能干什么

`analysis/fake_data_tables.json` 里 222 条带**位置 + 条数 + 首条内容**，可以直接用于：

1. 复刻件的假档案生成器（`CreateTest`）**按表实现**，不必猜数据规模；
2. 判定"这张表在复刻件里有没有对应物"；
3. 后续若要完整导出数据，**从这些边界起逐条读**，边界已由判据给出。

### 六、仍然 Unknown

- 270 张 UNRESOLVED 的记录框架：**Unknown**（R672 的框架不适用，未找到替代）。
- 每张表的**完整载荷**（本轮只读了首条样本）：数据量已在 JSON 里，内容需要另一次导出。
- 那个 4 字节字段：**仍 Unknown**（H2 否、H4 不可判）。
- 假档案各字段的组合算法：**Unknown**（需反编译取数代码 / IDA 库）。


---

## 107. 结构是**三层**（分类 → 表 → 条目）；R673 的 222 是**我判据的缺陷**；修好后 **416 / 492**

> R674。工具：`analysis/fake_data_walk2.py` → `analysis/fake_data_tables_v2.json`。

### 一、读那张 UNRESOLVED 的表，看清了真实结构

`postcode @0x037510EA`：

```
postcode\0 \x1e\0\0\0
  \x02 0 \0 \x06\0\0\0 "#####" \0
  \x02 1 \0 \x05\0\0\0 "####"  \0
\x00 \x00\x03 internet \0 \x59\0\0\0        ← \x03 标记一个**分类**
  \x04 domain_suffix \0 \x45\0\0\0           ← \x04 标记一张**表**
    \x02 0 \0 \x06\0\0\0 "co.za" \0
```

**三层：分类（`\x00\x03`）→ 表（`\x04`）→ 条目（`\x02`）。**

### 二、所以 R673 的 270 个 UNRESOLVED 是**我判据的缺陷**（第二十一自纠）

R673 的第三条判据是「解析终止位置 = 下一个表头标记位置」——
**它假设布局是平的**：下一个兄弟一定是表。

**但分类会插在表之间。** `postcode` 的下一个东西是 `internet` 这个**分类**（`\x00\x03`），不是表，
所以「减 2」的算术必然对不上。

**修正判据**：条目以载荷的 NUL 收尾，所以"停下"本身就是干净的；
只要 ① ≥1 条 ② 索引 0..n-1 连续 ③ 停下的那个字节是**层标记或段终止符**（`0x00`/`0x02`/`0x03`/`0x04`）—— 就自洽。

**故意比 R673 弱**：它不再假设平铺，而平铺假设正是 R673 出错的地方。

### 三、重测结果

```
分类 87    表 492
self-consistent:  222  →  **416**
```

### 四、真实规模（`analysis/fake_data_tables_v2.json`）

| 分类 | 表 | 条数 |
|---|---|---|
| `address` | `street` | **8,311** |
| `name` | `first_name` | **3,007** |
| `name` | `last_name` | 1,688 |
| `address` | `street_root` | 1,031 |
| `name` | `male_last_name` / `female_last_name` | 999 / 999 |
| `lorem` | `supplemental` | 840 |
| `name` | `male_first_name` / `female_first_name` | 796 / 786 |
| `address` | `city_name` | 604 |
| `address` | `country` | 239 |
| `address` | `street_title` | 235 |
| `address` | `state` | 22 |

### 五、R671 那两个数**都是错标签**

```
R671 报「state 604」   → 实际 city_name 604，state 22
R671 报「state 3007」  → 实际 first_name 3007
```

**两个数都是真的，两个标签都错。** 而且 R672 把 604 说成「过计数」也不准确 —— 它没数错，是贴错了。

**这类错误的代价**：数字看起来可靠（它能对上某个真实集合），所以没人会去复核。
**如果我没有做"走一遍"这件事，`state = 604` 会被写进复刻件的假数据实现里。**

### 六、这份清单现在能干什么

`analysis/fake_data_tables_v2.json`：416 条带**分类 + 表名 + RVA + 条数 + 首条样本**。

可直接用于：
1. **按表实现假档案生成器**（规模已知，不必猜）；
2. 判定复刻件缺哪些表（现在知道原版有 8,311 条街道名、3,007 条名）；
3. 后续完整导出时从已证边界起逐条读。

### 七、仍然 Unknown

- 76 张仍 UNRESOLVED 的原因：**Unknown**（多为 `extensions` 一类短表，可能有第四种形状）。
- 87 个分类的完整层级归属（哪些表属于哪个分类的**权威**来源）：**Inference（中）** ——
  本轮按"表前面最近的一个分类"归属，这是位置推断，不是结构声明。
- 假档案各字段的组合算法：**Unknown**（需反编译 / IDA 库）。
- 那个 4 字节字段：**仍 Unknown**。


---

## 108. 那个 4 字节字段**定了**：`field = 表体长度 + 5`（421/421）；而走不动的表是**嵌套对象**

> R675。工具：`analysis/fake_data_field.py`。

### 一、三处线索合起来才对上

| 轮次 | 发现 |
|---|---|
| R671 | 「字段 = 条目数」→ **0/5 相符**，否 |
| R672 | 「字段 = 表体长度」→ 四次差 `+5`、两次为负，判「不可用此法判定」 |
| R675 | 76 张空表：`field == 5` 且**表体为 0 字节** |

**空表给出的 `5` 是钥匙**：`5 = 1（表名后的 NUL） + 4（字段自身） + 0（表体）`。

**所以规则是 `field = 表体长度 + 5`。** R672 那两次「为负」不是反例 —— 是它自己的下一个表头定位失败。

### 二、全表验证

```
tables checked      : 492
  field == body + 5 : 421
  mismatch          :  71
  zero-entry tables :  76
```

**71 个「不符」全部 `body_len == 0`** —— 即走不动的那些表。**在能测的 421 张里，421 张全部成立。**

**所以判据报的 `REJECTED` 是我判据把"测不了"算成了"不成立"。**
规则本身在可测范围内 **无一例外**。

### 三、`field - 5` 直接给出那些表的**确切表体长度**

这是本轮最实用的收获：走不动的表，现在能精确切片。

```
bban            body_len =  62
currency        body_len =  57
iban_formats    body_len = 10805
```

### 四、切片一读，第四层标记出现了

**`currency`（57 字节）**：

```
\x03 0 \0 \x06\0\0\0                    ← \x03 = 数组元素 0
   \x02 name   \0 \x09\0\0\0 "Ευρώ" \0
   \x02 code   \0 \x04\0\0\0 "EUR"  \0
   \x02 symbol \0 \x04\0\0\0 "€"    \0
```

**`iban_formats`（10,805 字节）**：

```
\x03 0 \0 \x98\0\0\0
   \x02 country \0 \x03\0\0\0 "AL" \0
   \x10 total   \0 \x1c\0\0\0            ← \x10 = 嵌套对象字段
      \x04 bban \0 \x43\0\0\0
         \x03 0 \0 \x1c\0\0\0
            \x02 type \0 \x02\0\0\0 "n" \0
            \x10 count \0 \x08\0\0\0 …
```

**所以标记有四种**：

| 标记 | 含义 |
|---|---|
| `\x02` | 命名字段（字符串/数值），`<name>\0<u32 len><value>\0` |
| `\x03` | 数组元素（按序号） |
| `\x04` | 命名的表 |
| `\x10` | **嵌套对象字段** |

**68 张 `bban` + `currency` + `iban_formats` 之所以"走不动"，是因为它们是嵌套对象，不是平铺列表。**
我的 walk 只处理了表层的 `\x02`，遇到 `\x03`/`\x10` 就停。

### 五、仍然 Unknown

- `\x03` / `\x10` 的**完整语义**（数组长度怎么算、嵌套对象的成员边界）：**Inference（中高）** ——
  从字节看形状清楚，但没有第二个独立样本验证。
- 嵌套表的**实际内容条数**：**Unknown**（本轮只读了前 120 字节）。
- 那 71 张里除 `bban`/`currency`/`iban_formats` 外还有没有别种形状：**Unknown**。

---

## 109. 假数据容器格式**完全解出**，6/6 精确消费 —— 且有三处语义验证

> R676。工具：`analysis/fake_data_nested.py`。判据先定：整段 body 被恰好消费（无残留、无越界）。

### 一、格式

```
table   := <name> NUL <u32 body_len + 5> <object>
object  := { value } NUL
value   := 0x02 <name>  NUL <u32 n> <n 字节，以 NUL 收尾>     -- 字符串字段
         | 0x10 <name>  NUL <u32 数值>                        -- **整数字段，载荷内联、其后无字节**
         | 0x03 <序号>  NUL <u32 n> <object>                  -- 数组元素，n = 内容 + 4
         | 0x04 <name>  NUL <u32 n> <object>                  -- 命名的表，n = 内容 + 4
```

**三条关键规则**：

1. **表头那个 u32 = 表体长度 + 5**（R675，421/421）；
2. **`0x03` / `0x04` 的长度字段把自身 4 字节也算进去**（所以 `n = 内容 + 4`）；
3. **`0x10` 是内联整数**：`<name> <u32 值>`，**后面没有载荷**。

### 二、结果：6 / 6 精确消费

| 表 | body | 节点数 | 结果 |
|---|---|---|---|
| `currency` | 57 | 4 | **EXACT** |
| `bban` | 62 | 6 | **EXACT** |
| `iban_formats` | 10,805 | **802** | **EXACT** |
| `street_title` | 6,093 | 235 | EXACT |
| `first_name` | 282 | 17 | EXACT |
| `city_name` | 13,244 | 604 | EXACT |

**没有一张有残留字节。** 判据 ACCEPTED。

### 三、三处**语义**验证（不是只自洽）

自洽只能证明"我的解析器吃得下"，不能证明"我理解对了"。这三处是外部知识核对：

| 位置 | 读到的值 | 外部事实 |
|---|---|---|
| `iban_formats` / `AL` | `total = 28` | **阿尔巴尼亚 IBAN 长度正好 28 字符** ✓ |
| `bban` 元素 0 / 1 | `count = 8` / `count = 16` | 账号位数的两种典型长度 ✓ |
| `currency` 元素 0 | `name=Ευρώ` / `code=EUR` / `symbol=€` | 三元组自洽 ✓ |

**所以 `0x10` 判为「内联整数」不是拟合出来的，是 28 这个值对上了 AL 的 IBAN 长度。**

### 四、这一条怎么找到的（三步都失败过）

```
R671  H2「字段=条目数」      → 0/5，否
R672  H4「字段=表体长度」    → 四次 +5、两次为负 → 判「不可用此法判定」
R675  空表 field==5          → 得出 +5 的常数含义 → 规则成立
R676  currency 声明54/消费50 → 差正好 4 → 0x03/0x04 的 n 含自身长度字段
R676  bban count 声明8/消费1 → 语义一查：count=8/16 是位数 → 0x10 是内联整数
```

**每一步都是"差一个具体的数"，而不是"再猜一次"。**

### 五、现在能做什么

`field - 5` 给出每张表的确切 body 长度，格式已解 ——
**整个假数据数据集现在可以完整导出**：87 个分类、492 张表、已证 416 张的条数。

`analysis/fake_data_tables_v2.json` 是清单，本轮的解析器是读取器。

### 六、仍然 Unknown

- 87 个分类的**权威层级归属**（本轮按"表前最近一个分类"推断）：**Inference（中）**。
- 76 张仍 UNRESOLVED 的表里，除已解的 `currency`/`bban`/`iban_formats` 外还有没有别的形状：**Unknown**。
- 假档案生成时各字段的**组合算法**：**Unknown**（需反编译取数代码）。
- 复刻件是否需要这套数据集：**Unknown**（需求未定，但原版有且规模很大）。


---

## 110. 导出判据**没达成** —— 而失败本身给出了三条事实

> R677。工具：`analysis/export_country.py`。

### 一、判据（上一轮就定下，未事后改动）

> `country` 表导出应得 **239** 条、每条是 **3 字母 ISO 码**、且含 R670 直接读到的
> `COK`/`CIV`/`CHE`/`USA`/`DEU`/`JPN`。

### 二、实测：**244 条、内容是国名**

```
country table: body 4962 bytes at file offset 0x37D1F0F
parsed entries: 244
bytes consumed: 4962 of 4962          ← 解析器本身没问题
first 8: ('str','0',b'Afghanistan'), ('str','1',b'Albania'), ('str','2',b'Algeria'), ...
```

**244 ≠ 239，且内容是 `Afghanistan`/`Albania`，不是 3 字母码。判据未达成。**

### 三、为什么选错表：我的"取最大 body"不是判据

我用「body 最大的 `country` 表」来挑目标 —— **那是个启发式，不是上一轮定的判据**。
上一轮判据要的是"239 条 + 3 字母码"，我在实现时把它换成了"最大的那张"。

**两者不等价，而我用后者替换前者时没有明说。**

### 四、枚举全部 `country\0` 表头，看清了真相

| RVA | body | 内容 |
|---|---|---|
| `0x037510C8` | 20 | `South Africa`（1 条，英） |
| `0x03754D70` | 20 | `فلسطين`（1 条，阿） |
| **`0x037569D8`** | **4655** | `Akrotiri və Dekeliya`… **239 条，阿塞拜疆语** |
| `0x03759AD6` | 19 | `Azərbaycan`（1 条） |
| `0x0375B0DF` | 3571 | `Afghánistán`/`Albánie`（捷克语） |
| `0x037A12DC` | 4774 | `Ägypten`（德语） |
| **`0x037D2D03`** | **4962** | `Afghanistan`/`Albania` **244 条，英语** |
| `0x037F66D0`… | **−2** | `AL\0\x10total…` ← **假阳性** |

**三条事实**：

1. **`country` 表存的是国名，不是 3 字母码。** 3 字母码确实存在于别处（R670 见过
   `\x02145\x00\x04\x00\x00\x00COK\x00` = 索引 145、值 `COK`），但**不在名叫 `country` 的表里**；
2. **239 是阿塞拜疆语那张的条数，英语那张是 244。** 我给判据写的 239 来自 R673 的走表结果，
   而那张是阿塞拜疆语 —— **我把一个语言实例的条数当成了普遍期望**；
3. **`body = −2` 的那些是假阳性**：`country` 在这里是 `iban_formats` 元素里的**字段名**，
   我的表头识别（`\x00\x04name\x00`）**分不出"表头"与"字段名"**。

### 五、这一轮的收获不是失败的，是三条事实

- 解析器**是对的**（4,962 字节精确消费、244 条齐全）；
- **判据写错了地方**：239 是语言实例的属性，不是这张表的属性；
- **表头识别有假阳性**：`name\0` 出现在两种语境里，我用同一条正则抓，必然混。

### 六、仍然 Unknown

- 3 字母国家码在哪张表里：**Unknown**（需要按内容而非表名去找）。
- 9 种语言各自的条数：**Unknown**（本轮只量到英 244、阿塞 239、捷 3571B、德 4774B）。
- 表头识别怎么区分「表」与「字段」：**Unknown** —— 本轮只确认了它分不出。


---

## 111. 按内容找：**唯一命中** `country_code_alpha_3`，250 条 100% 是码；并与 R670 双向对上

> R678。工具：`analysis/find_code_table.py`。

### 一、判据（先定）

> 条目 ≥ **200** 且 **≥90%** 的值是**恰好 3 个大写 ASCII 字母**。

### 二、唯一命中

```
=== ranked by 3-uppercase-letter ratio ===
  country_code_alpha_3 @0x037D4BC4  n=250  codes=250  100%  ['BGD','BEL','BFA','BGR']
  gender               @0x037F06DE  n=71   codes=2      3%
  country              @0x037569D8  n=239  codes=3      1%
  …
meeting the criterion: 1
```

**250 条，100%，表名就叫 `country_code_alpha_3`** —— 名字与内容完全一致。

**R677 的失败到此解释干净**：3 字母码从来不在 `country` 里，它在 `country_code_alpha_3` 里。

### 三、导出成功

```
table body 3140 bytes
entries: 250   indices 0..249
index 0   -> BGD
index 145 -> XKX
index 249 -> MOZ
contains USA/DEU/JPN/CHE/CIV: True
```

**3,140 字节，250 条，索引 0..249 连续。**

### 四、与 R670 的交叉验证：两个点都对上

R670 当时从原始字节读到的是这一串：

```
... 145 ... XKX ... 146 ... CIV ... 147 ... CHE ...  以及 ... 249 ... MOZ
```

**本轮导出**：`index 145 = XKX`、`index 249 = MOZ` —— **两点都一致**。

**而 R670 当时把这串写成「索引 145 = COK」，是它自己的配对错了**：
那条 dump 的格式是 `<索引><值>` 交替，`COK` 在 `145` **之前**，所以 `COK` 是 **144**，145 是 `XKX`。

**所以不是数据不一致，是我上一轮的转述把配对看串了一格。**

### 五、顺带得到的数据集全貌（按内容排序的输出里）

| 表 | 条数 | 位置 |
|---|---|---|
| `street` | **8,311** | 捷克语城市街道 |
| `city_name` | 604 / 602 / 78 | 三种语言 |
| `country` | 239 / 195 | 阿塞拜疆语 / 捷克语 |
| `country_code_alpha_3` | **250** | 唯一一份，无语言副本 |
| `time_zone` | 143 | `Pacific/Midway` 等 |
| `words` / `supplemental` | 117 / 121 | lorem |

**`country_code_alpha_3` 没有语言副本** —— 码本身不随语言变，这与 `country`（有 9 种语言）形成对照。

### 六、仍然 Unknown

- 250 条里 ISO 官方分配是 249 —— **多出的那一个**是哪个：**Unknown**（可能是 `XKX` 这个非官方码）。
- 9 种语言各自的完整条数：**Unknown**（本轮只量到若干）。
- 假档案生成时如何从这些表取字段：**Unknown**（需反编译取数代码）。


---

## 112. 250 条码：三项验过，**ISO 差集不可判定** —— 判据作废而不是判成功

> R679。工具：`analysis/country_codes.json`（导出清单）+ 外部核对。

### 一、判据（上一轮定下）

> 与 ISO 3166-1 官方 **249** 条对照，**差集应恰好一个元素**，并给出该元素。

### 二、能做到的验证（全部通过）

```
codes 250 / distinct 250 / duplicates: none
not matching [A-Z]{3}: none
non-standard probes present: ['XKX']
```

**250 条全部 `[A-Z]{3}`、无重复、索引 0..249 连续。**

### 三、`XKX` 是 **user-assigned**，不是官方分配

外部核对（[ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)）：
官方分配列表从 `ABW AFG AGO AIA ALA ALB AND …` 开始，而 `XKX`（科索沃）属于 **user-assigned** 一类，
不在官方分配清单内。

**这解释了 250 与 249 之间那一个差额中的至少一个。**

### 四、但**差集本身不可判定**

要算「差集恰好一个元素」，需要**完整的 249 条官方清单**。本轮拿不到：

- `web_fetch` 取 Wikipedia 页面 → **内容在 `AND` 之后被截断**（HTTP 200，但正文只到第 7 条）；
- `web_search` 返回的是摘要与若干链接，**没有完整清单**。

**所以我没有 249 条的可枚举集合，差集算不出来。**

### 五、因此判据**作废**，而不是判「通过」

三种可能的处理，我选第三种：

| 处理 | 为什么不选 |
|---|---|
| 报「差集恰好一个（`XKX`）」 | **没有算过差集**，只验证了一个已知反例 |
| 报「判据未达成」 | 也不准确 —— 它不是被否证，是**没法测** |
| **报「判据不可判定」并说明缺什么** | 这是唯一不撒谎的说法 |

**缺的东西很具体**：一份可枚举的 ISO 3166-1 alpha-3 官方清单（249 条）。

### 六、顺带一个未解的差

```
country（英语国名表）  244 条
country_code_alpha_3   250 条
差                     6
```

**为什么差 6，Unknown**。可能的原因：国名表缺若干属地、或码表含若干无独立国名的属地。
**未查**，也不猜。

### 七、仍然 Unknown

- 250 与 249 的完整差集：**Unknown**（缺官方清单）。
- 国名表 244 与码表 250 差 6 的原因：**Unknown**。
- 假档案生成时用哪张表取国家：**Unknown**（需反编译）。


---

## 113. ISO 差集 **PASS**：1 个多余（`XKX`）、0 个缺失 —— 解码链被外部权威验证

> R680。工具：`analysis/iso_diff.py`（ISO 侧用 `pycountry`，已侧装到用户目录）。

### 一、判据（R679 定，未改）

> 差集**恰好一个元素**，且反方向差集为空。

### 二、结果

```
ISO official      : 249
image (exported)  : 250

in image, not ISO : 1   ['XKX']
in ISO, not image : 0   -

criterion 'difference is exactly one element': PASS
  extra XKX -> (pycountry 里根本没有)
```

**250 = 249 条官方码 + `XKX`。而官方 249 条一条不缺。**

`XKX` 是**科索沃的 user-assigned 码** —— pycountry 的官方分配集合里根本没有它。

### 三、为什么这一步值得单独一轮

R679 判据**没法测**（网页截断、`web_search` 不给完整清单）。
这一轮把它变成**可测**，办法不是放宽判据，是**补上缺的那个集合**：`pip install --user pycountry`，
249 条，开头 `ABW AFG AGO AIA ALA ALB AND ARE` 与 Wikipedia 一致。

**判据没有改一个字，只是拿到了它引用的东西。**

### 四、这一条把整条解码链钉住了

从 R670 发现那片区域到现在，每一环都被独立检验过：

| 环 | 检验方式 | 结果 |
|---|---|---|
| 区域是假数据表 | 内容（国名/街道后缀/州名） | ✓ |
| 记录框架 `0x02/0x03/0x04/0x10` | **恰好消费** 6/6 张表 | ✓ |
| 表头字段 `= body + 5` | **421/421** 可测表 | ✓ |
| 读者 | 4,962 字节精确消费、244 条 | ✓ |
| 表识别（按内容而非名字） | **唯一命中** 100% 3 字母 | ✓ |
| **数据本身** | **ISO 249 条差集 PASS** | ✓ |

**最后一环是外部权威给出的同意** —— 不是自洽，不是"我的解析器吃得下"。
ISO 3166-1 alpha-3 是第三方定义的标准，250 条里有 249 条与它逐字相同。

### 五、这是本 session 里最强的一次外部验证

前面多数结论是**自洽型**（我的工具与我的另一份输出对齐）。
这一条是**外部型**：第三方标准说"应该是这 249 个"，我把从二进制里解出来的 250 个拿去比，
**只多一个、一个不少**。

**自洽能证明我没算错，外部验证能证明我理解对了。**

### 六、仍然 Unknown

- 国名表（英 244）与码表（250）差 6 的原因：**Unknown**（未查）。
- 假档案生成时如何组合这些表：**Unknown**（需反编译取数代码）。
- 复刻件是否要实现完整假档案：**Unknown**（需求未定，但数据现在**已可完整读取**）。

### 七、下一步（不是 Unknown，是决定）

数据集现在**可完整导出**：格式已解、边界已证、内容已被外部权威确认。
`CreateTest` 从"加一个空壳"变成"按真实数据生成完整假档案"所需的**全部材料都在手上** ——
缺的只剩一件事：**原版按什么规则组合这些字段**（姓名从 `first_name`+`last_name` 取？地址从
`street`+`city_name`+`state`+`postcode` 取？是否按国家联动？）。那是行为，不是数据。


---

## 114. 收成一份边界：`docs/FAKE_DATA_BOUNDARY.md` —— **数据全可得，行为全 Unknown**

> R681。新增 `docs/FAKE_DATA_BOUNDARY.md`。**不改代码。**

### 一、为什么单独成文

假数据这块查了 **十二轮**（R670–R680）。散在 `BLOCKERS` 十二节里，
下一个要动手的人得自己拼；拼不起来，就会像 R671/R672/R673 那样**把已经量过的东西再量一遍**。

R650 对「哪些函数属于应用层」做过同样的事，那份文档现在的效果是：
**读到它的人不会从第一条路线重新开始。**

### 二、文档把两半分开写

| 半边 | 状态 |
|---|---|
| **数据侧** | **已闭合**（位置、格式、表头字段、边界、清单、读取器、外部验证） |
| **行为侧** | **全部 Unknown**（五条，见下） |

**格式完整写在文档里**（四层标记 + `field = body + 5` + `n = 内容 + 4`），
**规模清单指向 `analysis/fake_data_tables_v2.json`**（416 条已证）。

### 三、最小行为证据清单 —— 这是文档的核心

实现假档案生成需要知道的五件事，**没有一件能从数据里读出来**：

| # | 需要知道的 | 状态 | 怎么才能知道 |
|---|---|---|---|
| 1 | 生成哪些字段 | **已够**（`Profile` 模型有 15 个字段） | 复刻件源码 |
| 2 | 每字段从哪张表取 | **Unknown** | 反编译 —— **最可能一次解开** |
| 3 | 是否按国家联动 | **Inference（中）**：中文文案 `{1} 中未知的州/省"{0}"` 说明校验时知道国家 | 反编译 / 运行期 |
| 4 | 顺序取还是随机取 | **Unknown** | 反编译 / 连点两次看结果 |
| 5 | 一次生成几条 | **Unknown** | 运行期 |

### 四、为什么这五条不能"从数据推"

**数据里没有"取法"这一层。** 格式解出的是 `(索引, 值)` 的**集合**；
取法是**代码里的循环与随机数**，它在 `.text` 里，不在 `.rdata` 里。

**这与 R650 是同一件事**：那里"函数属于哪一层"问不出，这里"字段怎么组合"读不出。
**两次都是：结构可得，行为不可得。**

### 五、解锁条件里有一条要特别写

> **AOT 元数据格式资料 → 无帮助。**

它给的是类型/方法结构，**不是函数体内的取数逻辑**。
R650 已经证明格式资料给不了"应用层划分"，这里同理 ——
**格式资料描述数据布局，不描述代码逻辑。**

**不把这条写下来，下一个人还会去翻文档，然后再花一轮。**

### 六、仍然 Unknown

- 第 2/3/4/5 条行为：**Unknown**（需 IDA 库或凭据）。
- 国名表 244 与码表 250 差 6 的原因：**Unknown**。
- 76 张 UNRESOLVED 表里是否还有第四种形状：**Unknown**（`currency`/`bban`/`iban_formats` 已解）。


---

## 115. `SettingsView` 其实 **19/19 都在** —— R659 判它 `UNIMPLEMENTED` 是错的；判定词表加了 `STRUCTURAL`

> R682。工具：读源码 + 改 `analysis/type_presence_triage.py`。

### 一、判据（先定）

> 契约的 19 个页面名，若 **≥15 个**在 `SettingsShell.cs` 里被构造或赋值（任意形式）→ **结构差异**；<15 才是真缺。

### 二、实测：**18 / 19 在 `SettingsShell.cs` 里**

```
names appearing anywhere in SettingsShell.cs : 18 / 19
  absent: ['LogOut']
```

而且不是"名字出现过"，是**真的被构造**：

```csharp
new SettingsSection("appearance", "Appearance", s => new AppearanceView(s)),
new SettingsSection("notifications", "Notifications", s => new NotificationsView(s)),
new SettingsSection("data", "Data", s => new DataView(s)),
new SettingsSection("payment", "Payment", s => new PaymentView(s)),
```

**复刻件用「区段列表 + 工厂 lambda」组织设置页** —— 与"19 个属性"等价，形状不同。

**第 19 个 `LogOut` 也在**，只是挂在另一个视图上：

```
Cybersole.Ui.Views.Modals.CommonModals.cs:432   public ICommand LogOut { get; }
Cybersole.Ui.Views.Modals.CommonModals.cs:385   /// User panel (Cybersole.Ui.Views.Modals.UserView) — LogOut / OpenUrl.
```

**所以 19/19 功能存在。判据不成立 → 结构差异，不是真缺。**

### 三、R659 错在哪（第二十二次自纠）

R659 把成员检验从"正文里出现"改成"要求是声明"—— **这一步是对的、更精确的**。
**但它同时沿用了一套只认一种存在形式的判定词表**：`IMPLEMENTED` / `UNIMPLEMENTED` / `PARTIAL` / `RENAMED`。

于是：**更精确的测量 + 装不下它的结论 = 一个错的结论。**
`SettingsView` 按声明算 1/19 → 判 `UNIMPLEMENTED`，而它其实 19/19。

**这与之前二十一次的形状不同**：前二十一次是判据偏了，这一次**判据是对的，结论词表不够宽**。

### 四、修法：词表加一个 `STRUCTURAL`

```python
# 若本会判 UNIMPLEMENTED，但契约成员名在源码里出现 ≥ 半数（只是没以声明形式落在同一个类型上）
→ STRUCTURAL
```

**测量一点没改**，只是让结论能表达它测到的东西。

### 五、结果

```
改前：RENAMED 7 / PARTIAL 2 / UNIMPLEMENTED 2 / UNKNOWN 6
改后：RENAMED 7 / STRUCTURAL 2 / PARTIAL 2 / UNKNOWN 6     （合计 17）
```

| 类型 | 旧判定 | 新判定 |
|---|---|---|
| `SettingsView` | UNIMPLEMENTED 1/19 | **STRUCTURAL 19/19** |
| `LicenseControl` | UNIMPLEMENTED 1/3 | **STRUCTURAL 2/3** |

守卫 `TypePresenceTriageTests` 通过；套件 1619 通过；`types absent from source` 仍 17（**这个词表改变定性，不改变计数**）。

### 六、`LicenseControl` 的 2/3 要标出来

3 个成员里 2 个名字出现过 —— **这是弱证据**，不像 `SettingsView` 的 19/19 那样干净。
判据取"≥半数"所以它进了 `STRUCTURAL`，**但证据行写的是 `2/3`，读者能自己判断。**

**我没有把它说成"已实现"。**

### 七、仍然 Unknown

- `LicenseControl` 的 2/3 是否真是等价实现：**Unknown**（需要逐个看那 2 个名字的用法）。
- 剩下 6 条 `UNKNOWN (non-discriminative)`：**Unknown**（三条消解路径已排除，R655）。
- 17 这个"类型缺失"计数是否该随词表变化：**不变** —— 它数的是"类型名是否存在于源码"，
  `STRUCTURAL` 是"成员名以别的形式存在"，两件事。


---

## 116. 判据第三版：**同一类体内共现** —— 两个案例第一次都对

> R683。改 `analysis/type_presence_triage.py`。

### 一、R682 的 `STRUCTURAL` 规则被打回

R682 的规则是「成员名在**全库**出现过 ≥ 半数 → STRUCTURAL」。拿 `LicenseControl` 一试就露底：

契约成员：`Authenticate` / `Dashboard` / `Refresh`（`Cybersole.Ui.Views.Auth.LicenseControl`）

| 成员 | 全库命中 | 实际是什么 |
|---|---|---|
| `Authenticate` | **0** | **不存在** |
| `Dashboard` | 5 | `LoginControl.cs` 里的**局部变量**、按钮文字 `"Dashboard ↗"` |
| `Refresh` | **165** | **通用方法名**，散在几十个无关类里 |

**「2/3」= 一个通用词 + 一句按钮文字。这不是等价实现。**

**一个通用标识符就能满足的规则，什么都没测到。**

### 二、修法：要求**在同一个类体内共现**

```
若本会判 UNIMPLEMENTED，但契约成员名在**某一个类体**里出现 ≥ 半数 → STRUCTURAL
```

**这比"全库出现过"强得多**：它要求这些名字**聚在一起**，而不是各自散落在别处。

### 三、两个案例第一次都对

```
改前（R682）：SettingsView STRUCTURAL 19/19   LicenseControl STRUCTURAL 2/3   ← 后者错
改后（R683）：SettingsView STRUCTURAL 18/19 co-occur in SettingsShell
              LicenseControl UNIMPLEMENTED                                   ← 两者都对
```

| 类型 | R659 声明级 | R682 全库出现 | **R683 同类共现** | 手查结论 |
|---|---|---|---|---|
| `SettingsView` | UNIMPLEMENTED ✗ | STRUCTURAL ✓ | **STRUCTURAL ✓** | 19/19 都在 ✓ |
| `LicenseControl` | UNIMPLEMENTED ✓ | STRUCTURAL ✗ | **UNIMPLEMENTED ✓** | `Authenticate` 不存在 ✓ |

**同一判据的第三版，第一次两个都对。** 区分它们的那一个性质是**「共现」**。

### 四、为什么前两版各错一个

- **R659（只认声明）**：把"构造"排除在外 → `SettingsView` 被误判（它 18 个页面是 `new AppearanceView(s)` 构造的）
- **R682（全库出现）**：把"通用词"放进来 → `LicenseControl` 被误判（`Refresh` 有 165 处无关命中）

**两版都在同一个位置上出错：用的不是"证据是否指向同一件事"，而是"某个字面量是否出现过"。**

差别只在**范围**（一个太严、一个太松），**方法没变**。
**R683 换了方法**：不问"出现过吗"，问"是否聚在同一处"。

### 五、结果与不变的东西

```
PARTIAL=2, RENAMED=7, STRUCTURAL=1, UNIMPLEMENTED=1, UNKNOWN=6   （合计 17）
守卫 TypePresenceTriageTests 通过；套件 1619 通过
types absent from source 仍 17
```

**计数一直没变**（17）。三轮改的都是**定性**，不是数量 ——
因为这三轮问的都是"这些类型到底算什么"，而不是"有几个类型不存在"。

### 六、`LicenseControl` 是现在唯一确认的真缺

`Authenticate` 在源码里 0 次出现，所以「许可认证」这个动作**在复刻件里不存在**。
（`AuthWindow` 仍是 `PARTIAL 2/3`，未动。）

### 七、仍然 Unknown

- `AuthWindow` 的 `PARTIAL 2/3` 是否等价：**Unknown**（本轮未查）。
- `LicenseControl.Authenticate` 在原版里做什么：**Unknown**（需反编译）。
- 剩下 6 条 `UNKNOWN (non-discriminative)`：**Unknown**。


---

## 117. 又一次 OOM 崩溃后：**不知道是哪条命令**，但补了两处可补的

> R684。新增 `analysis/pe_reader.py`；改 `replica/tools/metrics_report.py`。**未做分析工作。**

### 一、恢复状态（先查，不先假设）

```
free 16.55 GB / total 31.71 GB      无残留 dotnet/python/testhost 进程
BLOCKERS / VERDICT / DELIVERY_STATUS   全部到 R683
25 个快照在 replica/tools/.mutation-backup
```

**工作区完好，没有半写的文件。**

### 二、**我无法确定是哪条命令压垮的**

最后几轮跑的是：python 分析脚本 + `dotnet test`（两次）+ `metrics_report.py`。
**单次都不重**。而整个会话持续 2.5 小时、跑了四十多个脚本、几十次测试套件。

**说"我知道原因"会是编的。** 能确定的是**我这边有两处可改**，本轮把这两处改掉。

### 三、改动一：`analysis/pe_reader.py` —— 不再整读 129 MB

多个分析脚本都是 `open(EXE,'rb').read()`，一次 129,243,216 字节。
`pe_strings_utf8.py` 还在其之上构建 193,556 条字符串。

新模块用 **`mmap`**，按需触页；并提供 `free_gb()` 与 `check_memory()` 守卫。

**实测**：

```
free before full read  : 16.21 GB
free after  full read  : 16.11 GB     ← 整读要 0.10 GB（= 文件大小）
free after mmap reads  : 16.20 GB     ← mmap 几乎为 0
sections via mmap: 6    bytes at 0x037D4BC4: b'country_code_alpha_3\x00I\x0c\x00' ✓
```

**每次省 129 MB。** 这个量单独看不大 —— **所以我没有把它说成崩溃主因**，只说它是我能去掉的那部分累积。

### 四、改动二：`metrics_report.py` 加了内存守卫

它是**每轮都要跑**的那条命令，而全量套件每次都要构建并加载一个测试程序集。

```python
if not args.skip_tests:
    gb = _free_memory_gb()
    if gb < 1.0:  raise SystemExit("... free memory first ...")
    if gb < 2.0:  print("WARNING: below the 2 GB build floor; -m:1 only")
```

- **< 1.0 GB → 拒绝启动**（项目规则里的"停止"线）
- **< 2.0 GB → 警告**（"只用 -m:1"）
- **`--skip-tests` 豁免** —— 它什么都不构建

**给一台已经饿着的机器加负载，正是一轮变成一次重启的方式。**

### 五、验证

```
metrics_report.py --skip-tests  → 五项度量 exit 0，写 METRICS.md
metrics_report.py               → "free memory: 16.42 GB"  完整套件 exit 0  1619 通过 / 0 失败
```

守卫打印出来、全量仍绿。

### 六、这两处改动**没有触及任何结论**

`pe_reader` 读的是同一批字节；内存守卫不改变任何度量。
**没有一行结论因为这轮而变。** 前面 116 节的数字全部仍然有效。

### 七、仍然 Unknown

- 崩溃的确切触发命令：**Unknown**（无崩溃转储、无进程历史）。
- 是否还有别的累积源（例如 `mutation-check.py` 连跑 36 次套件）：**Unknown** ——
  它确实是最重的一条，但本轮没动它（改它要连带改测试里的条数守卫，需单独一轮）。
- 复刻件本身的行为缺口：**不变**（与内存无关）。


---

## 118. 17 条现在每条判定都有其证据支撑 —— 判据加了**唯一性**，`PARTIAL` 要求**能指名候选**

> R685。改 `analysis/type_presence_triage.py`（三次改动）。

### 一、`AuthWindow` 露出的问题

契约：`Exit` / `Logout` / `Minimise`（`Cybersole.Ui.Views.Auth.AuthWindow`）

| 成员 | 全库命中 | 实际 |
|---|---|---|
| **`Logout`** | **0** | **不存在** |
| `Exit` | 26 | **每个窗口都有的通用按钮** |
| `Minimise` | 29 | **同上** |

**而「2/3」在 8 个类里都成立** —— `MainWindow`、`MonitorWindow`、`HistoryWindow`、`CustomBrowserWindow`…
**8 个类都满足的判据，指不出任何一个。**

### 二、改动 ①：`STRUCTURAL` 加唯一性

达到半数阈值的类**不超过 2 个**才成立（1 个是个体，2 个容许基类/派生类）。

**验**：`SettingsView` **只有 1 个类**达标 → `STRUCTURAL` 站稳。

### 三、改动 ②：把候选类数写进证据行

```
AuthWindow          2/3  ; 6 class(es) reach this ratio
TaskCreatorCartView 2/3  ; 35 class(es) reach this ratio     ← 35！
SettingsView       18/19 ; only 1 class(es) reach that
```

**这一步改的是报告，不是判定** —— 让任意性可见，而不是藏在"best match"四个字后面。

### 四、改动 ③：`PARTIAL` 要求**能指名候选**

`PARTIAL` 的定义是「改名了但成员不全」——**那必须先能说出是哪个类**。
6 个或 35 个同分候选里挑一个，等于没挑。

```python
verdict = "PARTIAL" if _qualifying <= 2 else "UNKNOWN (non-discriminating match)"
```

**为什么不是 `UNIMPLEMENTED`**：没有证明"不存在"。
**为什么不是 `PARTIAL`**：没有指名任何候选。
**所以是 `UNKNOWN`** —— 证据不支持任何判定。

### 五、最终 17 条

| 判定 | 条数 | 说明 |
|---|---|---|
| `RENAMED` | **7** | 每一条都有**唯一声明匹配**或**注释指名** |
| `STRUCTURAL` | **1** | `SettingsView`，**只有 1 个类**达标 |
| `UNIMPLEMENTED` | **1** | `LicenseControl`（`Authenticate` 0 次） |
| `UNKNOWN (non-discriminative)` | 6 | 1 成员契约，词太泛 |
| `UNKNOWN (non-discriminating match)` | 2 | `AuthWindow`（6 候选）、`TaskCreatorCartView`（35 候选） |

**合计 17，与 `types absent from source` 一致。**

### 六、这一轮为什么值得单独记

改了三处判据，**计数一次没动**（17）。
三轮（R683/R685）改的都是**"这个数该怎么读"**，不是**"这个数是多少"**。

**现在每一条判定都能追溯到一条具体的证据**：
"sole declaration match"、"only 1 class reaches that"、"`Authenticate` 0 次"、"6 个候选"。
**没有一条只是"best match"就下了结论。**

### 七、仍然 Unknown

- `AuthWindow` / `TaskCreatorCartView` 到底有没有对应实现：**Unknown**（需要换个判据或反编译）。
- `LicenseControl.Authenticate` 在原版做什么：**Unknown**。
- 6 条 1 成员契约：**Unknown**（R655 已排除三条消解路径）。


---

## 119. `类型缺失` 这一项在账本里**结案**了 —— 结案表由工具生成，不是手抄

> R686。改 `replica/docs/BINDING_BACKLOG.md`（追加一节）。工具：`analysis/append_type_absence_closing.py`（一次性）。

### 一、发现的问题：账本描述的是一个**已经不存在的状态**

`BINDING_BACKLOG.md` 的「类型缺失」节里写的是 **R512 的分类**：

```
5 条 RENAMED + 46 条 UNIMPLEMENTED   （51 条口径）
```

**而当前度量是 17 条**，判定也由另一个工具（`type_presence_triage.py`）产出，
判据经 R657/R658/R659/R683/R685 **五次修订**。

**所以那一节描述的状态与现状无关了。**

### 二、处置：**不改历史，追加指针**

R665/R666 定过界线：**活引用要更正，历史记录保持它当时的样子**。
所以：

- **R512 那段一字未改**，只在上面加了一句「上方 R512 的 51 条口径已作废，保留为历史记录」；
- 追加一节 `R686：结案`，内含**当前 17 条的逐条定性表**。

### 三、表格是**生成**的，不是手抄的

脚本从 `docs/TYPE_PRESENCE_TRIAGE.md` 解析 17 行，按判定分组后写成 markdown。
**没有一个人工输入的数字** —— 这与「数字只有一个来源」的规则一致：
这里没有新增数据源，只是把已有生成物重新排版到该出现的地方。

### 四、追加内容

| 判定 | 条数 | 类型 |
|---|---|---|
| **RENAMED** | 7 | `CloudflareSolver`、`Settings`、`KeyGesture`、`Concurrency`、`ImapProvider`、`ActionConfig`、`TaskCreatorMainView` |
| **UNKNOWN (non-discriminative)** | 6 | 四个 `Localize*Extension`、`ObservableDictionary`、`AccountsCreatorView` |
| **UNKNOWN (non-discriminating match)** | 2 | `AuthWindow`、`TaskCreatorCartView` |
| **STRUCTURAL** | 1 | `SettingsView` |
| **UNIMPLEMENTED** | 1 | `LicenseControl` |
| **合计** | **17** | |

**真缺口只剩 1 条。**

### 五、验证

```
free memory 17.03 GB
类型缺失（type presence）  exit 0  types absent from source: 17      ← 与表里合计一致
绑定缺口分桶              exit 0  backlog: types absent: 4         ← 另一个口径，未受影响
完整套件                  exit 0  1619 通过 / 0 失败 / 0 跳过
```

**文档守卫全绿** —— 追加没有破坏 `backlog_report.py` 的解析。

### 六、这一项为什么可以结案

判据 a 的要求是「每条若不可得则写 Unknown + 缺什么」。现在：

- **7 条改名**：每条都有唯一声明匹配或注释指名；
- **1 条结构差异**：`SettingsView`，18/19 名字在**唯一一个**类里共现；
- **1 条真缺**：`LicenseControl`，`Authenticate` 全库 0 次；
- **8 条 Unknown**：各自写明是哪一种够不着（1 成员契约词太泛 / 6 或 35 个同分候选）。

**没有一条停在「待查」。** 这是结案的定义。

### 七、仍然 Unknown

- `LicenseControl.Authenticate` 在原版做什么：**Unknown**（需反编译）。
- 8 条 Unknown 里有没有实际已实现的：**Unknown**（需要比"名字共现"更强的判据，或反编译）。
- `backlog: types absent: 4` 与 `types absent from source: 17` 的口径差：**已知不同口径**（前者按类分桶，后者按类型计数），本轮未动。


---

## 120. 同 4 条成员、**两个不同的问题**，两个都叫「结案」—— 补一条区分说明

> R687。改 `replica/docs/BINDING_BACKLOG.md`（追加一节）。**不改判定、不改代码。**

### 一、先核对：R568 还准不准

`bind_diff --buckets` 当前输出：

```
missing: 16    noise (HasMultiple_NN): 12    real gap: 4

  Ui.Localization.LocalizeFormatExtension   1  Value2
  Ui.Localization.LocalizeSwitchExtension   1  Condition
  Ui.Views.Auth.AuthWindow                  1  Logout
  Ui.Views.Auth.LicenseControl              1  Authenticate
```

**与 R568 当时那 4 条是同一批。** R568 的两条支撑事实也复验过：

```
files scanned      : 304
.axaml / .xaml     : 0
MarkupExtension sub: 0
```

**「0 个 .axaml、0 个 MarkupExtension 子类」仍成立。**

### 二、但我一开始以为 R568 过时了 —— 那是错的

我本来准备像 R686 那样写「已作废」。**核对之后发现不能这么写**：

| 问的是 | 工具 | 那 4 条 |
|---|---|---|
| **成员能不能做成可绑定属性？** | 人工判（R568） | **4/4 不能** |
| **类型在源码里存在吗？** | `type_presence_triage.py`（R685） | 1 条真缺 + 3 条判据够不着 |

**两条都成立，回答的是不同问题。** 我把它们当成"同一件事的两种说法"，差点把一条正确的结论标成作废。

### 三、最容易误读的是 `LicenseControl.Authenticate`

- 按 **R568**：它是「结构差异」—— 一个属性装不下「发起认证」这个动作；
- 按 **R685**：它所在类型是 **`UNIMPLEMENTED`** —— `Authenticate` 全库 0 次。

**前者说"成员形态"，后者说"类型缺失"。都不错，但只看其中一个会得到片面的印象。**

### 四、处置：不改 R568，加一节区分

追加 `R687：同 4 条成员，两个不同的问题，两个都叫「结案」`，内含一张对照表与被误读风险的说明。

**为什么不是"改掉 R568"**：R568 没有错。
**为什么不是"什么都不做"**：两份文档都用了「结案」这个词，读者会把它们当成同一件事的两种说法。

### 五、验证

```
free memory 15.69 GB
名字级绑定缺口  exit 0  real gap: 4 / missing: 16     ← 未变
完整套件        exit 0  1619 通过 / 0 失败 / 0 跳过
```

### 六、判据 a 的后半因此成立吗

「名字级缺口全部三分类结案」——**按 R568 的口径已成立**（可做 0 / 结构差异 4 / 不可得 0），
且 R687 复验了它的支撑事实。

**但"成立"依赖问的是哪个问题**，所以现在两份结案并列存在并互相标注。

### 七、仍然 Unknown

- `LicenseControl.Authenticate` 在原版做什么：**Unknown**（需反编译）。
- `real gap` 的 4 条里有没有在原版也只是"不可绑定的行为"：**Inference（中）** ——
  R568 已按此判定，但那是从类型形态推的，没有反编译证据。


---

## 121. 判据 (b) 的验收记录 —— 那 2 条**不是截断**，而校验数据**其实是有的**

> R688。工具：`analysis/fake_data_tables_v2.json`（R674 生成，本轮只读它）。

### 一、判据 (b) 原文

> **剩余仅「字符串池中截断」的文案，且每条写明为何不可得。**

### 二、那 2 条是什么

```
ProfileCsv.Error.UnknownCountry   "Unknown country \"{0}\""
ProfileCsv.Error.UnknownState     "Unknown state \"{0}\" for {1}"
```

R668 已证：**不是池中截断** —— 两条在池里**完整存在**（`0x03C65058` / `0x03C65099`，占位符齐全），
而且**裸键名单独存在**（`0x06E4BD6C` / `0x06E4BDC4`），说明**原版确实按 key 查表**。

**所以 (b) 的前半（"仅池中截断"）不成立。**

### 三、我上一轮以为这两条"缺数据" —— 本轮发现数据是有的

R672 看到的 `state` 表是**阿拉伯语那一份**（22 条，阿盟首都），据此我写过"`state` 不带国家字段"。
**但 `state` 表是按语言各一份的。** 把全部 6 张走完：

| `state` 表 | 条数 | 首条 | 配对的 `state_abbr` |
|---|---|---|---|
| `@0x037514A5` | 22 | `القدس` | （无） |
| `@0x037A85FB` | 16 | `Baden-Württemberg` | **16 条**（`BW`…） |
| `@0x037BC3CA` | 9 | `Burgenland` | **9 条**（`Bgld.`…） |
| **`@0x037D662D`** | **50** | **`Alabama`** | **50 条**（`AL`…） |

**每张 `state` 都有一张条数相等的 `state_abbr` 配对（16↔16、9↔9、50↔50）。**
英语那份就是**美国 50 州 + 50 个缩写**。

同理 `country` 的英语那份有 **244** 条国名。

**所以校验所需的名单是齐的。**

### 四、那 (b) 现在的准确状态

| 问题 | 答案 |
|---|---|
| 是"池中截断"吗？ | **不是**（R668，两条完整） |
| 缺数据吗？ | **不缺**（本轮：50 州 + 50 缩写 + 244 国名） |
| 缺什么？ | **规则** —— 什么时候判、是否大小写敏感、是否接受缩写、是否按 locale 取表 |

**缺的是行为，不是数据，也不是文案。**

### 五、所以 (b) 按字面仍不成立，但性质变了

原文把剩余类别预判成"池中截断"，实测是"**数据齐、规则缺**"。
判据 (b) 的措辞需要一次明确处置 —— 这仍要 YG 点头（判据是考题，我不自己改）。

**但这一轮把处置所需的事实补齐了**：不是"不可得"，是"规则 Unknown"。

### 六、仍然 Unknown

- 校验的**触发时机**（导入时？编辑时？）：**Unknown**。
- **大小写**与**缩写是否被接受**：**Unknown**。
- 是否**按 locale 取对应那份名单**：**Inference（中高）** —— 名单按语言分份，这个结构暗示如此，但没有证据。
- 那 2 条文案在原版里由哪个函数发出：**Unknown**（需反编译）。


---

## 122. 判据 (b) 的三条处置写成待选清单 —— **我不选，摆事实给 YG**

> R689。新增 `docs/CRITERION_B_OPTIONS.md`。**不改判据、不改代码。**

### 一、为什么写成文档而不是直接选一条

判据是**考题**。R689 之前我在 (a) 的处置上已经改过三次判据（R683/R685），
但那三次都是**我自己工具的判据**，不是 GOAL 里的考题 (a)–(e)。

**(b) 是考题。** 改它的口径等于改考题 —— 那要 YG 点头。

### 二、文档把三条路径的代价并列写出

| 路径 | 改什么 | 代价 | 风险 |
|---|---|---|---|
| **A. 改口径** | 去掉「截断」这个预判 | **需 YG 点头** | **真的放宽** —— 以后任何"写明了原因"的缺口都算过 |
| **B. 实现校验** | `Validate()` 加两条规则 | 不需点头，但**规则是猜的** | 违反"结构对等 ≠ 行为对等"；四个维度全无证据 |
| **C. 保现状** | 什么都不改 | 零 | (b) 永远不成立 |
| **D. 拿规则**（前置条件） | 反编译 | 需 IDA 库或凭据 | **阻塞** |

### 三、我把"路径 A 是真放宽"这点写明白了

A 看起来像"措辞修正"，其实是**把判据的约束力去掉一半**：
原文要求剩余必须是"池中截断"这一特定原因，改成"写明原因"后，**任何有解释的缺口都算过**。

**这一点如果不写出来，A 会显得是最省事、最合理的选择。**

### 四、路径 B 的风险也写明白了

四个维度全无证据：何时校验、大小写、是否接受缩写、按国家还是按 locale。

**在四个维度都靠猜的情况下实现校验，会让 `ProfileCsv` 的测试变绿 —— 而绿的理由是错的。**

这比不做更危险。

### 五、我的建议：C + 等 D

理由已写进文档。**但明写了一句"这是 YG 的考题，我按他选的做"。**

### 六、仍然 Unknown

- 那 2 条文案的校验规则（四维）：**Unknown**（需反编译或运行期观察）。
- 原版是否**真的实现**了这两条校验：**Unknown** —— 也可能是残留文案。
- 若 YG 选 A，是否需要同步改其它文档对 (b) 的引用：**Unknown**（取决于改法）。


---

## 123. 判据 (c) 重算了一次；报告头部那句「函数级仍是 Unknown」**已被它自己的正文取代**

> R690。重跑 `analysis/pe_resources.py`；改 `docs/PARITY_PRODUCT.md`（加两处指针）。

### 一、重算结果

```
原版: 12 leaves (129243216 bytes)
复刻件: 12 leaves (55071232 bytes)
wrote analysis/pe_resources.md
```

**资源面 12 ↔ 12，与 R609 一致。** 命令可复算，输出落盘。

**但复刻件是 55,071,232 B，而 §1 表里写的是 54,979,584 B** —— 那是 R433 当时那版产物。
两个数都真，只是不同时点。已加一行提示，不改那张表（它记录的是 R433 的状态）。

### 二、发现：报告的**头部**说函数级 Unknown，而**正文**已经做完了

`PARITY_PRODUCT.md` 开头（R433 写的）写着：

> 未完成的部分：**rea 的 `compare_functions` / `compare_artifacts` 在本机不可达**，
> 所以函数级"逐函数对账"仍是 Unknown。

**而本文件后面 R609–R618 已经把这件事做了**：

| 节 | 内容 |
|---|---|
| R613 | 同口径函数数 **321,244 ↔ 186,732**，`cc` 差异是 PDB 造成的 |
| R614 | 那 134,512 的差**高度集中在极小函数**，>64 B 的只差 45,602 |
| R615 | ≤16 B 的函数逐个看过，都是**编译器胶水** |
| R617 | 可达性判据实测失败（两侧从入口可达都不足 2%） |
| R618 | 函数指针表存在但接进 BFS 也搭不起桥 —— 分解线定量关闭 |

**所以「函数级对账仍是 Unknown」不再成立**，成立的是「差异已量化并部分归因」。
未取代的只剩：`rea` 那两个工具始终没用上（R433 §5 的原因仍在）。

**已加指针。不改 R433 那段** —— 它记录的是当时的事实。

### 三、这一轮我自己弄坏了两次文本（同一个坑，第五次）

用 PowerShell here-string 写这段 Markdown 时，**反引号是 PowerShell 的转义符**：

| 破坏 | 表现 |
|---|---|
| ``rea`` | 变成 `ea`（吃掉首字母和两端引号） |
| `> **` 开头 | 被吃掉，行尾留孤立 `**` |
| 某行 `> ` 前缀 | 丢失，引用块断开 |

**AGENTS.md §2.5 规则 5 已经记过四次同类事故。这是第五次。**
修法：**所有含反引号的文本一律从文件写入，不经过 shell。**

### 四、还有一次「修一个不存在的 bug」（第二十三次自纠）

第二次修复后我写了个校验，报 `opens with '> **': False`，于是又改了一遍。
**实际文件是对的** —— 校验式子写成 `t2[i:]`，而 `i` 指向 `R`，所以永远看不到前面的 `> **`。

**看字节确认后：6 行引用块、`> **` 开头、`**` 结尾、`rea`/`compare_functions`/`cc` 全在。**

**这次错的不是结论，是检查本身。** 一个写错的校验会让人去"修"正确的东西 ——
**J 比漏检更危险，因为它留下改动痕迹。**

### 五、判据 (c) 现在的准确状态

| 要求 | 状态 |
|---|---|
| 报告存在 | ✓ `docs/PARITY_PRODUCT.md` |
| 命令可复算 | ✓ 本轮重跑 `pe_resources.py`，12↔12 一致 |
| 两侧产物都量过 | ✓ PE 结构、资源、函数数、字符串数 |
| 函数级对账 | ✓ **R609–R618 用 IDA 完成**（非 rea），差异已量化并部分归因 |
| `rea` 那两个工具 | **未使用** —— R433 §5 的原因仍在（不是缺口，是工具选择） |

**所以 (c) 成立**，且它的证据链现在从头部到正文是一致的（指针已加）。

### 六、仍然 Unknown

- 134,512 的差里剩余 45,602（>64 B 那一批）的逐函数归因：**Unknown**（R616 已证 12 例肉眼分类不足以归因）。
- PDB 之外的第二混淆项：**Unknown**（R612 只证明了 PDB 是一个来源）。


---

## 124. git 建起来了；IDA 开起来了；并用三次否定探测钉住了原版的**寻址形态**

> R691。新建 git 仓库（首提交 `35e8721`）；新增 `docs/IDA_STARTUP_CHECKLIST.md`、`analysis/run_idapy.py`；
> 在 IDA 里做了三次探测。

### 一、YG 提的两件事

1. **「没有版本控制，损坏不可逆」是对的** —— 本轮 `git init` 完成首提交：
   5,856 文件 / 90.3 MB；原版 exe、`.i64`、`.publish-aot`、超大派生 dump 全部忽略（`.gitignore` 已验证生效）。
2. **「你没开 IDA」也是对的** —— R684–R690 我在做判据对账，把反编译主线搁了。本轮打开了。

### 二、IDA 启动：**两个模态框**，不是一个

`ida-mcp-doctor.ps1` 报 `TIMEOUT: no listener after 180s`，看起来像 DSH 坏了。**实际是模态框**：

| # | 文本 | 点 |
|---|---|---|
| 1 | `Database ...i64 already exists. Overwrite?` | **加载现有(L)**（覆盖会丢已分析库） |
| 2 | `IDA has found an unpacked version ... did not close properly` | **Restore packed base**（上次崩溃留下的不一致文件） |

点完第二个后 **12 秒**端口起来，`ws` 涨到 1.9 GB。`ida.py health` → `status: ok`、`hexrays_ready: true`。

**清单已写进 `docs/IDA_STARTUP_CHECKLIST.md`。** 这是第五次在这上面浪费时间。

### 三、三次否定探测：原版的字符串/数据**没有直接引用**

想查「谁发出 `ProfileCsv.Error.UnknownState`」，按常规路径走，三次全部为空：

| 探测 | 对象 | 结果 |
|---|---|---|
| `xrefs` 裸键 `0x146e4d1c4` | `ProfileCsv.Error.UnknownState` | **0** |
| `xrefs` 表地址 `0x1437D4BC4` / `0x1437D662D` / `0x1437D2D03` | 国家码表 / 美国 50 州表 / 英语国名表 | **0 / 0 / 0** |
| `xrefs` locale 大 blob `0x143c656aa` 等三处 | 该 JSON 正文 | **0 / 0 / 0** |

**再加两次全区域扫描**：

| 扫描 | 范围 | 结果 |
|---|---|---|
| 按页探 `XrefsTo` | 区域 `0x143600000..0x143800000`，512 页 | **0 引用** |
| `bin_search` 找 8 字节指针（形如 `?? ?? ?? ?? 43 01 00 00`） | `.rdata` 58,336 KB + `.data` 11,248 KB | **0 指针** |

### 四、这说明了什么（Observation，不是推理）

**那片假数据集在 IDB 里与代码没有任何可见连接**：代码不引用它，数据里也没有指向它的指针。
字符串字面量同理。

**符合 NativeAOT 的寻址形态**：字面量与只读数据放在冻结堆，通过指针数组或相对偏移访问，
IDA 不把这种访问建模为「指针」或「xref」。

### 五、直接后果：**「字符串 → xref → 函数」这条路在原版上不通**

这条路的失效不是「证据不足」，是**工具在这个二进制形态上天然为空**。
R670–R688 那十二轮调查之所以一直只能谈数据、谈不到行为，根子在这里：
**不是我没找，是这个二进制不提供这条边。**

**所以 `CRITERION_B_OPTIONS.md` 里「路径 D：反编译拿规则」的前提要改**：
反编译本身可以做，但**先要能定位到函数**，而定位不能靠字符串引用。
可行替代：按 `.pdata` 函数清单逐个反编译并按内容特征筛（321,244 个函数，成本高但可分批）。

### 六、顺带纠正我自己的一处破坏

R690 我用一个全局替换把三份记录里**所有**「反斜杠 + 反引号」都删了反斜杠，
其中多数是**合法历史内容**（C# 泛型元数 `ObservableDictionary\`2` 之类）。21 处受影响，当时**没有 git**。

现在有了 git，但那次破坏已包含在首提交里（提交信息里写明了）。
**处置：不改历史，列为已知缺陷**；后续如需修复，用 git 做可回退的单独提交。

### 七、仍然 Unknown

- 假数据集的取用规则（四维）：**Unknown** —— 且现在知道**不能靠 xref 定位**。
- 函数级行为对等：**Unknown**（两侧 321,244 ↔ 186,732，R613–R618 的量化结论未变）。
- 那 21 处反引号破坏里有多少是真正的转义：**Unknown**（需要原始副本才能判定；没有）。


---

## 125. 判据 (d) 从「结构性满足」推进到「与度量一致」—— 7 处不一致，实核对为 0

> R692。工具：`analysis/audit_claims.py`；改 `docs/PARITY_CLAIMS.md`。

### 一、(d) 原来满足的是结构，不是内容

`PARITY_CLAIMS.md` §6 自审说 (d) 满足：22 条 claim 每条都有 `authority`，10 条非 unknown 都有 `command`，
12 条 unknown 都有 `gap_reason`。**这确实成立。**

**但表里同时写着数字**，而规则是数字只住在 `METRICS.md`。R433 当初就是这样在六个文件里抓到八个失效数字的。

### 二、机器核对：7 处

| 位置 | 原写 | 处置 |
|---|---|---|
| C7b | `275 条形状差异`（当前 **80**） | 改指针 + 标注历史 |
| C7b | 构成 `175/61/29` | 标注为 R468 当时值 |
| C14 | `5 条缺失`（当前 **2**） | 改指针 |
| C14 | "全为池中截断" | **更正**：R668 已否证（两条在池里完整） |
| C6 | 复刻件 `187,328` | 补 R613 同口径 **186,732** |
| C10 | `21/819` | 标注为一次性测量 |
| C11 | `111` | 补指针 |

复算 `python analysis/audit_claims.py` → **inconsistencies: 0**。

### 三、处置方式本身是这一轮的重点

**一个数字被后续轮次更新，不等于那句话当时错了。**
R467 的 275、R468 的构成、R433 的 21/819 —— 在当时都真。

所以：**不改历史、只加指针与「当时的」字样；只有被否证的事实才更正，并写明哪一轮否证的。**

**唯一被"更正"的是 C14 的「池中截断」** —— 那不是过期，是被 R668 证否。

### 四、审计脚本的第一版太粗（第二十四次自纠）

第一版规则是「文本里出现这个数字就报」，于是我把 7 处改完、加完标注后它**仍然报 4 处**。

**因为时代数字还在那里 —— 只是现在带着指针。** 问题在判据：它检查「数字在不在」，
而该检查的是「**同一行有没有指针或历史标注**」。

收紧后（`annotated()`：同行需含 `见 METRICS.md` / `当时的` / `R6xx` / `一次性` 之类）→ 0 处。

**第二十四次自纠，形状与前几次一致：判据测的是"存在"，该测的是"有没有交待"。**

### 五、仍然 Unknown

- C10 的 21/819 是否需要重算：**Unknown**（要重跑 `aot_member_coverage.py` 才有新值，本轮未跑）。
- C11 的 111 与当前类型缺失计数是否同一口径：**Unknown**（两者定义不同，未对齐）。
- C4 / C8 / C9 / C7c 等 unknown claim 的补法：**不变**（见本表 §7）。


---

## 126. 产物已用当前源码重建；而 **C10 的 21/819 是在一对双重过期的输入上算出来的**

> R693。重建 `.publish-aot`；起第二个 IDA 实例（复刻件，13338）在后台分析。

### 一、先查输入时效（判据先定）

> **C10 重算必须基于「当前源码构建的产物」+「从该产物导出的符号表」，任一过期结果即无效。**

查出来**两样都过期**：

| 输入 | 时间 | 说明 |
|---|---|---|
| `.publish-aot\Cybersole.Ui.exe` | **11-15 14:39** | 旧产物 |
| `analysis/replica_funcs.txt`（符号表） | **11-14 18:03** | **比产物还旧 20 小时** |
| 最新源码 `.cs` | **11-15 21:47** | 比产物新 |

**所以符号表比产物旧、产物比源码旧 —— 三层错位。**

### 二、结论：C10 的 21/819 不是对"当前产物"的测量

这比 R692 里写的「R433 时的一次性测量」更进一步 ——
**它不是"旧但当时有效"，而是"符号表与产物本身就对不上"**：
`replica_funcs.txt` 是 11-14 从当时的产物导出的，而 11-15 的产物已经变过。

**所以 C10 的 21/819 应记为：在一次已失效的输入组合上得到的数，不能代表任何一版产物。**

### 三、本轮做完的

**产物已重建**（当前源码，`mswin` Release + AOT）：

```
exit=0    artifact: 55,080,448 B  21:49:47
free: 14.57 GB -> 13.93 GB
```

**判据 (c) 的资源面在**新产物**上复算通过**：

```
原版: 12 leaves (129,243,216 bytes)
复刻件: 12 leaves (55,080,448 bytes)     ← 新产物
```

12 ↔ 12 与 R609 一致，且这次用的是当前源码的产物。

### 四、C10 的重算已启动，但需要第二次完整分析

`func_compare.py` 需要**两个活着的 IDA 实例**（原版 13337、复刻件 13338，带 PDB）。
第二个实例已启动：

```
启动 ida.exe .publish-aot\Cybersole.Ui.exe
模态框 1：Database ...i64 already exists -> **Overwrite**（旧库对应旧产物，按判据不能用 Load existing）
模态框 2：Load a new file（PE 加载器已选，Analysis 已启用）-> OK
状态：Please wait...  ws=718 MB（自动分析中）
```

**这一步是项目里最贵的一次分析**（55 MB AOT、约 18.7 万函数），本轮让它后台跑完。

### 五、仍然 Unknown

- C10 的**新值**：**Unknown**（等 13338 分析完 + 重导符号表 + 跑 coverage）。
- 新产物与旧产物的差异：**Unknown**（未做产物级 diff）。
- C6 里 187,328 与 186,732 两个数哪个对应哪版产物：**Unknown**。


---

## 127. C10 有了有效新值 **12/819 = 1.5%** —— 而中间有个"提前量的错"被我抓住了

> R694。工具：`analysis/ida_tool.py`、`analysis/wait_ready.py`、`analysis/func_compare.py`、
> `replica/tools/aot_member_coverage.py`。

### 一、第三个模态框：**Load PDB file**

第二个 IDA 实例（复刻件，13338）卡了 25 分钟，`ws` 停在 718 MB、**CPU 25 分钟只用了 9.6 秒**。
查窗口发现三个：`Load PDB file` / `Please wait...` / 主窗口。

**「Load PDB file」是我之前没记录的第三类模态框。** 它的选项是 `Load types` + `Load names`（都已勾选），
点 **Yes** —— **符号名正是 C10 的基础，绝不能点 No**。

点完 CPU 立刻从 9.6 s 涨到 60 s，分析真正开始。

### 二、然后我犯了一个更危险的错，并自己抓住了

点 Yes 后**一分钟**端口 13338 就起来了，我当即导出符号表：

```
exported 136989 rows
C10 -> members with a body : 9 (1.1%)
```

**同一份源码不该比旧记录的 187,328 少 27%。**

于是查 `server_health`：

```
13338: "auto_analysis_ready":false,  "strings_cache_ready":false,  strings_cache_size:0
13337: "auto_analysis_ready":true,   "strings_cache_ready":true,   strings_cache_size:324901
```

**端口开 ≠ 分析完。** 插件一加载就应答，而自动分析还在跑。
**所以 136,989 是一个中间值，C10 的 9/819 = 1.1% 无效。**

### 三、等就绪标志，不猜端口

写 `analysis/wait_ready.py`，轮询 `auto_analysis_ready`：

```
t+  0s  auto_analysis_ready=False  strings=0
t+320s  auto_analysis_ready=True   strings=0
READY after 320 s
```

**分析用了 320 秒。** 重新导出：

```
replica <- 13338  exported 187732 rows      ← 与旧记录 187,328 同量级
```

**C10 的新值**：

```
symbols in image : 187732
binding members  : 819
members with a body in the product : 12 (1.5%)
types with at least one member present : 10
```

**12 / 819 = 1.5%。** 旧值 21 / 819 = 2.6% 是在过期输入上算的，已降级；**这才是当前产物 + 其自身符号的有效值。**

**它比旧值更低**，这本身是信息：不是变差了，是旧值虚高。

### 四、两种错，代价不同

| 错 | 表现 | 后果 |
|---|---|---|
| **提前量** | 端口一起就导出 | 得到一个像样的数（9/819），**但它是中间态**，若不复核就会被写进表 |
| **过期** | 用昨天的符号表 | R693 已记：连"当时的有效测量"都算不上 |

**第一种更危险**：它不报错、不超时、数值合理 —— 只有"比旧值少 27%"这个反常才露出来。

**抓住它的不是工具，是那个反常。** 如果 136,989 恰好接近 187,328，我会直接写进表。

### 五、仍然 Unknown

- 12/819 里"缺席"的 807 条各自是被裁剪、被内联、还是只在元数据里：**Unknown**（需逐个看符号）。
- C10 的 coverage 数字与"行为是否存在"的关系：**Unknown**（coverage 是结构可见性，不是行为）。
- 新产物与 R577/R609 那两版产物的函数数差（187,732 vs 187,328）：**Unknown**（未做产物级 diff）。


---

## 128. C6 的三个数不是矛盾，是**三种测量条件**；而 R694 那个坑 **R433 早就写进文档了**

> R695。工具：`docs/PARITY_PRODUCT.md` 全文检索。

### 一、三个数各自的成立条件

| 数 | 条件 | 出处 |
|---|---|---|
| **187,328** | **带 PDB** | R433（第一次取到 **136,798**，重取后为 187,328） |
| **187,698** | **带 PDB** | R613 的表里那一列 |
| **186,732** | **不带 PDB**（同口径基准） | R613 重建库时 PDB 选 No |
| **187,732** | **带 PDB** + 当前源码产物（55,080,448 B） | R694 |

**R613 已经把条件列成表**：`auto_analysis_ready`、是否加载 PDB、`cc`、函数数、有符号名 —— 六项对齐。

**所以 186,732 与 187,698/187,732 不是矛盾的两份测量，是「不带 PDB」与「带 PDB」两种口径。**
带 PDB 的三个数（187,328 / 187,698 / 187,732）差 370，是**三版产物**，不是三次误差。

### 二、更难堪的发现：R694 那个坑，R433 已经写下来了

`PARITY_PRODUCT.md` §8 里原文写着：

> **踩过的坑（R433）**：第一次取复刻件函数数得 136,798，重取得 187,328。
> 原因是 **IDA 插件端口 open ≠ 自动分析完成** —— 端口在 PDB 加载阶段就监听了，函数还在持续识别。
> 判据是**窗口标题不再带 `Loading`** 且**连续两次取值相同**（187,328 两次一致）。

**而 R613 用的判据就是 `auto_analysis_ready: true`（t=240s）。**

**所以 R694 我不是发现了一个新陷阱，是重复了一个已经写在文档里的陷阱。**
而且我当时写的"抓住它的不是工具，是那个反常"—— **那句话说得太客气了**：
真正该抓住它的是那份文档，我只要在导出前读一眼 §8 就不会发生。

### 三、两次现象的对比（说明这个坑很稳定）

| | 第一次（错误） | 第二次（正确） | 倍数 |
|---|---|---|---|
| R433 | 136,798 | 187,328 | 0.730 |
| R694 | 136,989 | 187,732 | **0.730** |

**同一个比值，隔了 260 多轮。** 这说明它不是偶发，是**IDB 自动分析在 PDB 加载阶段的一个稳定中间态**。

**这个"稳定"反而危险**：任何人在那个窗口内取数，都会得到一个**看起来合理、且两次可能相同**的偏小数。

### 四、已做处置

`PARITY_CLAIMS.md` 的 C6 已补上三个数的条件；`docs/IDA_STARTUP_CHECKLIST.md` 已有「端口开 ≠ 分析完」一节
（R694 写的，判据是 `wait_ready.py`）。

**现在两份文档都说这件事**：一份在产物对照里（历史记录），一份在启动清单里（操作手册）。
**问题是它们互不引用。**

### 五、仍然 Unknown

- 187,328 / 187,698 / 187,732 三版产物之间除了函数数还有哪些差：**Unknown**（未做产物级 diff）。
- `.pdata` 口径 170,137 与 186,732 的换算关系：**Unknown**（C9 仍 unknown）。
- R433 那次 136,798 与 R694 的 136,989 差 191：**Unknown**（不同产物，比值相同）。


---

## 129. 把那条坑串成三处入口 —— 让下一次在**动手的地方**被拦住

> R696。改 `docs/PARITY_PRODUCT.md`、`docs/IDA_STARTUP_CHECKLIST.md`、`analysis/wait_ready.py`。

### 一、问题不在"没写下来"，在"写的地方不对"

R695 查明：这个坑 R433 就写进了 `PARITY_PRODUCT.md` §8，判据也给了；R613 还用过 `auto_analysis_ready`。
**而 R694 我照样踩了。**

原因很具体：`PARITY_PRODUCT.md` 是**产物对照报告**，读它的时候是"看结论"；
**取数的时候读的是代码和启动步骤**，不是那份报告。
**教训写在"总结"里，而犯错发生在"操作"里 —— 两者之间没有边。**

### 二、三处入口（各自不同的用途）

| 位置 | 用途 | 加了什么 |
|---|---|---|
| `docs/PARITY_PRODUCT.md` §8 | **历史记录**（R433 原文不动） | 下面加一条指向操作手册与工具的指引 |
| `docs/IDA_STARTUP_CHECKLIST.md` | **操作手册** | 指向历史记录，并说明旧判据已被取代 |
| `analysis/wait_ready.py` 文件头 | **就在取数的代码里** | 写明它取代的两个判据、以及为什么"两次一致"不够 |

**第三处是真正的修复**：判据现在住在**取数的那段代码里**，而不是只住在一份报告里。

### 三、`wait_ready.py` 文件头写下的关键理由（转述，不引原文以免混淆引号）

- 它取代 R433 的判据："窗口标题不再带 Loading" + "连续两次取值相同"；
- **后半不成立**，因为中间态是**稳定**的：R433 的错误/正确比值 `136,798/187,328 = 0.730`，
  R694 是 `136,989/187,732 = 0.730`，相隔 260 多轮仍一致。**两次取样可能都对，也可能都错。**
- R613 早已在用 `auto_analysis_ready` —— **好判据本来就存在，只是住在报告里，没住在取数的代码里。**

### 四、验证

```
wait_ready.py parses OK; docstring mentions R433: True, stable: True
完整套件  exit 0  1619 通过 / 0 失败 / 0 跳过
git       32b43f6（三处改动一次提交）
```

### 五、仍然 Unknown

- 这类"教训写在报告里、犯错发生在操作里"的缺口还有多少处：**Unknown** ——
  本轮只处理了这一条，没有系统清点其它坑是否都有操作入口。
- 是否还有第三种"稳定的中间态"（不只 IDA 分析）：**Unknown**。


---

## 130. 清点 123 条坑的「操作入口」：**25 条只停在报告里** —— 而"分析中途截断"这一族是其中之一

> R697。工具：`analysis/trap_entry_inventory.py`；改 `analysis/func_compare.py`。

### 一、判据（先定）

一条坑算「有操作入口」需其一：① 某脚本**文件头**（前 45 行，§1.2 要求在那里写理由）提到它的 `R` 编号；
② 某测试文件提到它；③ 操作手册里有对应步骤。否则算「只停在报告里」。

### 二、结果

```
traps (BLOCKERS.md sections carrying round ids): 123
have an operational entry point : 98
report only                     : 25
```

**这个 98 是上界、25 是下界** —— 匹配是宽松的（某 `R` 编号出现在任何测试文件里就算，不一定是为它写的测试）。
**所以「25 条只停在报告里」是可以确信的那一半。**

### 三、25 条里有一条正中要害

```
R610/611  §44. 两侧函数数都曾被"分析中途"截断 —— 差值两端必须同状态
R612      §45. "同口径"钉住了分析选项，但没钉住符号输入
```

**R694 踩的坑属于这一族，而这一族一个操作入口都没有。**

R433 踩过一次（写进 `PARITY_PRODUCT.md` §8）、R610/611 又记了一次（写进 `BLOCKERS.md` §44）、
R694 我第三次踩 —— **三次都写在报告里，三次都没有东西在动手时拦住。**

### 四、修法：把门放在**导出函数**里

`func_compare.py` 的 `export()` 本来就取了 `server_health`，**但拿回来就不看**。现在：

```python
ready = _ready(health)
if ready is not True:
    raise SystemExit(
        "%s: auto_analysis_ready is %r -- refusing to export.\n"
        "  Port-open is not readiness; functions are still being recognised.\n"
        "  Wait first:  python analysis/wait_ready.py <port> <timeout>\n"
        "  Background:  BLOCKERS 44/45 and 129, PARITY_PRODUCT section 8, IDA_STARTUP_CHECKLIST."
        % (label, ready))
```

`_ready()` 兼容四种回包形状（dict 直取、dict 嵌套一层、JSON 文本、缺键）。

**为什么放在这里**：这个坑从来没有在"报告"里被踩到 —— 它只在**运行导出命令**时被踩。
把门放在别处，等于再写一份报告。

### 五、验证到什么程度（不夸大）

```
_ready 单测（5 种回包）:
  dict ready -> True / dict not ready -> False / nested -> True / json text -> True / missing key -> None
```

**已验**：辅助函数对五种形状判断正确；`if ready is not True` 对 `False` 与 `None` 都会抛。
**未验**：**没有对真实「未就绪」实例跑过一次**（两个端口现在都就绪，13339 无监听 → 会先在连接处失败）。
**所以这只是「单测 + 代码审读」，不是「实测拦下」。**

### 六、仍然 Unknown

- 其余 23 条 report-only 的坑要不要同样加门：**Unknown**（逐条判断成本高，且多数是"结论"而不是"动作"）。
- 「98 条有入口」里有多少是**误计**（某 R 编号只是被顺带提到）：**Unknown**。
- 是否需要把这套清点接进 `metrics_report.py` 作为常驻度量：**Unknown**（会引入第五个度量，需 YG 同意）。


---

## 131. 清点结案：**真正没门的动作型只有 1 条**（R697 写的 2 条里有一条本来就有门）

> R698。新增 `docs/TRAP_ENTRY_CLOSURE.md`。

### 一、清点工具量的是「引用」，不是「覆盖」

三处假阴性暴露同一个结构缺陷：**一棵坑由"发现它的那一轮"编号，而修它的工具由"修它的那一轮"编号。**

| 段 | 坑的轮号 | 门在哪 | 门的轮号 | 为什么漏 |
|---|---|---|---|---|
| §37 | **R599** | `replica/tools/datafiles_diff.py`（已接进 `metrics_report.py`） | **R600** | **差一轮**，按编号匹配连不起来 |
| §54 | R621 | 该节自己写着「有守卫」 | — | 守卫测试没引用 `R621` |
| §118 | R655/683/685 | `type_presence_triage.py` + `TypePresenceTriageTests` | — | 同上 |

**所以 98 是上界、25 是下界，两者都不是真值。** 它量的是「有没有人写下那个编号」。

### 二、§37 不但有门，门还把它标 Unknown 的那点答了

`python tools/datafiles_diff.py`（R698 复跑）：

```
files on disk : 11          image literals: 23          replica references: 12
original-on-disk but not written by the replica : 0
literal-only (a string in the image, not a file) : 13   ... products.json, public.json, sku-stores.json ...
replica-referenced, found in neither source      : 1    license.json
```

**§37 当时判 Unknown 的正是**「原版是否真的写 `products.json` / `sku-stores.json` / `public.json`」。
**答案：它们是 literal-only —— 只是镜像里的字符串，磁盘上没有这些文件。**
而 **`original-on-disk but not written by the replica: 0`** —— 原版真正写的 11 个文件，复刻件全写。

**§37 说的"5 个不重合"，实际只剩 1 个真差异**（`license.json`）。

### 三、唯一真的没门的一条：§45

| 段 | 坑 | 现状 |
|---|---|---|
| **§45（R612）** | "同口径"钉住了分析选项，但**没钉住符号输入** | R697 的 `export()` 只查 `auto_analysis_ready`，**没记录 PDB 是否加载** |

**为什么这条算动作型**：每次建 IDA 库都要选 PDB 是/否，而 R613 实测这改变 `cc`（129 ↔ 1）
与函数数（186,732 ↔ 187,698）。**不记录它，186,732 与 187,698 这种差会被当成"产物变了"。**

### 四、结案账

```
25 条 report-only
  ├─ 假阴性   3 条  →  §37 / §54 / §118 本来就有门
  ├─ 待定     2 条  →  等 YG（判据 b 口径，同一主题）
  ├─ 结论型  19 条  →  不加门，正确
  └─ 动作型   1 条  →  §45 的门缺 PDB 维度 ← 唯一待办
```

**R697 写「动作型 2 条」是错的 —— 把已关门的 §37 算了进去。**

### 五、仍然 Unknown

- §45 的门加完后能否复现 186,732/187,698 的差：**Unknown**（未做）。
- 用**主题**（文件名/函数名/指标名）替代轮号匹配，能查出多少今天算错的：**Unknown**（改造未做）。
- `license.json` 在原版里是否以别的名字存在：**Unknown**（`datafiles_diff.py` 说两处源都没有）。


---

## 132. §45 的门装上了：导出文件第一行自带口径 —— 而它立刻证出两侧**符号条件不对称**

> R699。改 `analysis/func_compare.py`（`EXPORT_TEMPLATE` + `export()`）。

### 一、判据（R698 已定）

> 导出文件**第一行**必须能回答「这个数带不带符号」。

### 二、怎么判（Inference，不是 Observation）

`server_health` **没有任何字段**报告符号是否加载。所以用**非 `sub_` 名字占比**作代理：
R613 自己的两个基线是 **93%**（带符号）与 **2.1%**（不带），相差一个数量级。

```
ratio > 0.5  -> symbols=yes
ratio < 0.1  -> symbols=no
否则         -> symbols=unknown
```

**并且把头行里印出原始 `ratio`**，读者可以不同意这个判定。

### 三、实测结果

```
original: # exportspec symbols=no   named=10041   total=321244 ratio=0.0313
replica : # exportspec symbols=yes  named=175495  total=187732 ratio=0.9348
```

**它立刻证出一件比 §45 原话更重的事：两侧的符号条件相差一个数量级，而之前所有"函数数对照"都在这个不对称下做的。**

- 原版 IDB：**3.13%** 有名字（10,041 条，来自 PE 导出表 / CRT，**从未加载过 PDB**）
- 复刻件 IDB：**93.48%** 有名字（175,495 条，**加载了 PDB**）

**所以 `321,244 ↔ 187,732` 这个对照，是"符号贫乏的一侧"对"符号丰富的一侧"。**
R613 为了消掉这一维，专门重建了不带 PDB 的库（得 186,732）——**那个数才是同口径的**。

### 四、验证

| 检查 | 结果 |
|---|---|
| 两个导出文件第一行都有 `# exportspec symbols=` | ✓ |
| `export()` 会**回读文件**校验头行（不信 stdout） | ✓ 缺头即 `SystemExit` |
| 下游 `load_rows` 跳过它 | ✓ 无制表符 → `len(parts) < 3` → 跳过 |
| 下游 `aot_member_coverage.py` 结果不变 | ✓ **仍 12 / 819 = 1.5%** |

### 五、仍然 Unknown

- `ratio` 代理在中间区（0.1–0.5）会判 `unknown`，**实测两侧都在区间外**，但中间情形未遇过。
- 原版如果加载 PDB 后函数数会变多少：**Unknown**（R613 只做了复刻件那一侧）。
- 同口径的 `321,244 ↔ 186,732` 与带符号的 `321,244 ↔ 187,732` 该用哪个作为"函数数量对等"的口径：**Unknown** —— 需要 YG 或更多证据决定，我不自行选。
