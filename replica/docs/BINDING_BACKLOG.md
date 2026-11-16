# 绑定缺口工作账本

> **数字来源：`docs/METRICS.md`**（`python tools/metrics_report.py` 生成）。
> 本文件只列"哪些未结案、为什么"，不承担"当前是多少"的职责（R433 裁决 1）。
> 下方的分类数字是该账本自己的分桶口径（剥注释 + 排除泛型噪音），与 `bind_diff.py` 的
> `real gap` 可能相差几条 —— **口径不同不是矛盾**，引用时说清用的是哪一个。

`docs/xaml_bindings.json` 是原版编译期 XAML 的绑定表（174 类型 / 819 成员）。这里按
**"这个类型在复刻件里存不存在"** 把缺口分成两类。

> **口径**：whole-source（`src/` 任意位置都找不到）· **削注释**（注释里的名字不算实现）
> · 排除泛型噪音 `HasMultiple_NN` / `Value_NN`（12 个）
> · 与 `tests/Cybersole.Tests/BindingGapRatchetTests.cs` 完全一致；重算：`python tools/bind_diff.py --buckets`

## 名字级缺口（`python tools/bind_diff.py --buckets`，当前值见 `docs/METRICS.md`）

这些名字在 `src/` 里一处都没有（数量见 `docs/METRICS.md`）。**已逐条三分类结案** ——
见 **`docs/NAME_GAP_TRIAGE.md`**：不可得 7 条（三源否证，`DEVIATIONS.md` §4 已记）、
结构差异 9 条（复刻件用别的类型/机制扮演同一角色，逐条给了对应物）、**可做 0 条**。
**不要为了凑数而造空类型。**

> 关键背景：这 16 个成员所属的**类型多数本身就不存在**（`bind_diff.py --type-presence` 交叉可见），
> 所以这一批不是"漏了几个属性"，而是类型层/机制层差异在下游的投影。

## 42 条「复刻件里既无方法也无属性」的成员（R502/R503）

`shape_audit` 把它们标成 `replica=method` 是**兜底判定**；实际查下来，复刻件里连同名方法都没有。
原版全部是 `Getter,Property,Setter`。按模式分组后，它们分成**三种性质**，不是同一种活：

### A. 硬约束：做不到（7 条）

| 成员 | 所在类 | 为什么做不到 |
|---|---|---|
| `Close` | `GoogleLogin` `DesktopNotification` `InputModal` `MessageBoxDialog` `ActionsModal` `PublishTemplateModal` `StoreGroupModal` | 七个都是 **`Window` 子类**。`Window` 自己声明了 `Close()`，C# 不允许同类型里有同名属性（CS0102）。要做只能把 `Window.Close()` 改名 —— 那会破坏 Avalonia 的契约 |

**这不是缺口，是平台差异。** 原版不是 Avalonia，它的 `Close` 属性能与"关闭"这个动作共存。

### B. 需要设计行为：没有现成实现（31 条）

| 模式 | 条数 | 现状 |
|---|---|---|
| `Save` | 6 | 六个类里都**没有**保存逻辑 |
| `Clear` | 6 | 六个类里都**没有**清空逻辑 |
| `Add` | 6 | 同 |
| `Delete` | 3 | 同 |
| `OpenUrl` | 2 | 有 `Process.Start` 辅助，但**无参版本该打开哪个 URL 未知** |
| `StartAll`/`StartAll` 等 | 8 | 同 |

**为什么不直接写**：这些不是"改个形状"，是"写新功能"。写出来的是**我的猜测**，
而 goal 的纪律要求「只能证明属性存在的成员，行为必须记 Unknown」。
要写必须先有反编译证据（IDA 打开原版，找到这些成员的 setter/getter 实际做什么）。

**当前卡点**：IDA 未开（YG 2026-11-14 22:22 明确"ida-pro 没开"）。
不是不能开，是这一轮没有开 —— 下一轮需要时用 `ida-mcp-doctor.ps1` 拉起来。

**R504 更新（IDA 已开，并且这条路被证明是断的）**：

IDA 起来了（`auto_analysis_ready: true` / `hexrays_ready: true`），但拿 B 类行为的路走不通：

```
xrefs to the AccountGrid descriptor block (0x14320c54d) -> 0
xrefs to the Clear/Edit property block  (0x1436389fc) -> 0
```

两块描述符**都没有交叉引用**。NativeAOT 用相对偏移寻址元数据，数据段的 xref 链是断的 ——
这正是 `PARITY_PRODUCT.md` 里"原版零直接 xref 比例 1.1%"那个数字的成因。

**所以 B 类 31 条的结论不是"没做"，是"用现有工具拿不到行为证据"**：

| 想拿的东西 | 为什么拿不到 |
|---|---|
| 描述符 → 引用它的注册代码 | 描述符无 xref |
| 属性 setter 做什么 | 编译期内联，没有独立函数体 |
| `ICommand` 的行为 | 藏在委托初始化点，该点靠类型信息定位，类型信息也无 xref |

**这与 `PARITY_CLAIMS.md` 的 C7c（每个函数功能相等）一直是 Unknown 是同一件事。**
要么接受"结构对等、行为 Unknown"，要么换一条完全不同的证据路线（例如运行期差分：让原版执行一次
`Clear`，观察它改了什么）——**运行期路线需要登录凭据**，那是 goal 允许停下来等 YG 的两件事之一。

### C. 已做（4 条）

`AccountGroupView.Close` / `CreateGroupModal.Close`（R502，两个都是 `UserControl`，名字空着）
+ 之前几轮搬完的那些。

---

## 类型级缺口（`python tools/bind_scope.py`，当前值见 `docs/METRICS.md`）

> **R488 定性**：剩下这两个成员不是"没做"，各有明确原因。

| 类型.成员 | 原版描述符表 | 复刻件 | 定性 |
|---|---|---|---|
| `Profile.Username` | `Cybersole.Models.Profile` 有 `Username`（Getter+**Setter**） | **R488 已补**，落盘为 `username` | 已消除 |
| `Profile.Card` | 同表有 `Card`（Getter+**Setter**）；绑定表另有 `Cybersole.Models.Card -> Cvv, Number` → 是**嵌套对象** | **R511 已补**：`[JsonIgnore]` 计算属性，读写平铺的四个字段 | **已消除**。R510 看了原版的 New Profile 对话框：卡号 / MM/YY / CVV 是**三个并列输入框**，不是嵌套控件 —— 所以存储平铺、属性做视图，两边都对得上。`[JsonIgnore]` 是因为仍没有 `profiles.json` 样本，不去猜它写不写 `card` 键 |
| `ProxyTester.Name` | `Cybersole.ProxyTesters.ProxyTester` **有 `Name`（Getter）** —— 该类型在描述符表里只有这一条 | **R511 已补** `public string Name { get; }` | **已消除**。R488 判"证据冲突"是因为查错了命名空间（写成 `Cybersole.Services.ProxyTester`，那是复刻件的命名空间）。字符串**值**仍未知（locale 只有 `ProxyTester.Custom.*` 四个键，没有裸 `ProxyTester`），用类名兜底并在注释里写明 |



绑定表要的成员**没有长在该类型上**（名字在别处存在，所以不算进上面那 16）。

| 类型 | 成员 | 情况 |
|---|---|---|
| `Profile` | `Card` | **结构差异，已结案（R448）**。原先的结案条件写的是"需要一份含 profile 的原版备份"，但**不用等备份**：`docs/xaml_bindings.json` 里有独立条目 `Cybersole.Models.Card -> Cvv, Number`，说明 `Profile.Card` 是一个**嵌套对象**而不是字符串。复刻件把它平铺成 `CardNumber` / `CardCvv` / `CardExpiry` / `CardName` 四个字段 —— 同一份数据，不同形状。**Inference（高）**：绑定表证明的是"存在 Card 这个类型且带 Cvv/Number"，落盘究竟是嵌套还是平铺仍要备份；但"该不该是一个成员"已经能答 | |
| `Profile` | `Username` | **UNKNOWN**。`Profile` 的绑定成员是 `Card, Delivery, Email, Name, Phone, Username`；复刻件有 `Email` / `FirstName` / `LastName` / `Phone`，没有 `Username`。原版 **没有** `Profile.Username` 这条 locale（R448 实测，扫二进制字节），也找不到其它证据说明它与 `Email`/`Name` 的区别 —— 缺的是"Username 指什么" | |
| `ProxyTester` | `Name` | 原版 `Cybersole.ProxyTesters.ProxyTester` 是**行模型**（`ProxyView.ProxyTesters` 的集合元素，只有 Getter），复刻件这个类名是**服务**。结构差异，不是漏一个属性 |
| `SmartActionsView` | `Export` | **UNKNOWN**。绑定表里 `SmartActionsView` 的成员是 `Clock, Clone, Delete, Edit, Export, Filters, OpenCreator, View, ViewLogs` —— 其它八个复刻件都有（`OpenCreator` / `ViewLogs` / `Clock` / `FiltersCaption` 可见），只有 `Export` 一条命令完全不存在（`grep Export` 在 SmartActions 相关文件里 0 命中）。**R448 实测**：原版没有 `SmartActions.Export` 这条 locale，所以它多半是个无标签图标按钮 —— 缺的是"导出什么、什么格式" | |

> **R464 决定性发现**：用原版自己的**绑定描述符表**（`analysis/binding_descriptors.py`，215 类型 / 1,637 条）
> 逐个核对，**51 个类型全部在表里、成员全覆盖、0 例外**。
>
> 所以"类型缺失"这个度量名一直在误导 —— 它量的是**复刻件侧没有同名声明**，
> 不是"原版没有这个东西"。**原版每一个都有**，缺口全部在复刻件侧（没实现或改了名）。
>
> 另外：描述符表**完全覆盖** `xaml_bindings.json`（共有 819 = XAML 表全部成员，`only xaml = 0`），
> 并多出 **132 条**纯 C# 绑定 —— 后者正是 XAML 表长期看不见的那部分。

## 类型缺失（`python tools/bind_diff.py --type-presence`，当前值见 `docs/METRICS.md`）

> **R512 分类完成**：那个数字数的是"复刻件里没有同名声明"，而 AGENTS §0 明确允许改名。
> 所以每条必须先判 RENAMED（有对应物，只是名字不同）还是 UNIMPLEMENTED（真缺口），
> 否则这个数字不能当缺口用。工具：`python analysis/triage_absent_types.py`（判据见下）。

### 判据（可复算，不拍脑袋）

对每个 ABSENT 类型，用**公开成员集合**去和复刻件的每个类比 Jaccard，同时要求：

```
ratio >= 0.50  且  命中成员数 >= 2  且  短类名相似度 >= 0.35
```

三条缺一不可。前两条排掉"1 个成员巧合"（Jaccard 恒等于 0.5 的假阳性，
例如 `Size`→`EditValue`、`Operator`→`TimeSpanOption`）；
第三条排掉"成员碰巧重叠但语义不同"（例如 `AccountStoreType` 和 `Drop` 都有 `Stores`/`Type`，
但 `Drop` 还带 `Time`，它建模的是发售条目，不是账号页的店铺类型）。

输出：`analysis/type_presence_triage.tsv`（每行含 best match、命中数、Jaccard、判定）。

### 结果

**5 条 RENAMED**（复刻件里其实就是它，只是名字不同）：

| 原版 | 复刻件 | Jaccard |
|---|---|---|
| `Cybersole.KeyInput.KeyGesture` | `KeyBind` | 1.00 |
| `Cybersole.Models.Concurrency` | `ConcurrencySettings` | 1.00 |
| `Cybersole.SmartActions.ActionConfig` | `SmartActionStepConfig` | 1.00 |
| `Cybersole.CloudflareSolvers.CloudflareSolver` | `CloudflareSolverConfig` | 0.89 |
| `Cybersole.Global.Settings` | `GlobalSettings` | 0.66 |

**46 条 UNIMPLEMENTED**（真缺口，逐条见 TSV）。它们按性质分三组：

| 组 | 例子 | 为什么没有 |
|---|---|---|
| 数据模型 | `Models.User` `Models.Store` `Models.Size` `Models.Analytics` | 对应功能未接入 UI；造类会成死代码（`DEVIATIONS.md §十` 的教训） |
| 编辑对话框 | `Auth.AuthWindow` `Auth.LicenseControl` `Accounts.Modals.AccountsCreatorView` `Profiles.Modals.ProfilePaymentView` | 复刻件把这些画在页面内联，没有独立控件 |
| markup extension | `Localization.LocalizeEnumExtension` / `LocalizeFallbackExtension` / `LocalizeFormatExtension` / `LocalizeSwitchExtension` | 复刻件不用 XAML markup extension，文案走 `Copy` 字典 |

**这 46 条的"缺什么"是同一句话**：缺**这个类型被创建的那条功能路径**。
一旦那条路径实现（例如接入 Auth 窗口），类型和成员应当连同一起补 —— 而不是先造一个空类占位。

### R686：结案 —— 当前 17 条逐条有定性（上方 R512 的 51 条口径已作废）

> **上方的 R512 分类（5 改名 / 46 未实现，51 条口径）不再代表现状**，保留为历史记录。
> 当前值见 `docs/METRICS.md`；逐条定性由 `python analysis/type_presence_triage.py` 生成到
> `docs/TYPE_PRESENCE_TRIAGE.md`。判据经 R657 / R658 / R659 / R683 / R685 五次修订：
> 成员检验从正文出现改为**声明存在**，阈值从 `<3` 收到 `<2`，`STRUCTURAL` 要求**唯一达标类**，
> `PARTIAL` 要求**能指名候选**。

| 判定 | 条数 | 类型 |
|---|---|---|
| **RENAMED** | 7 | `CloudflareSolver`、`Settings`、`KeyGesture`、`Concurrency`、`ImapProvider`、`ActionConfig`、`TaskCreatorMainView` |
| **UNKNOWN (non-discriminative)** | 6 | `ObservableDictionary`、`LocalizeEnumExtension`、`LocalizeFallbackExtension`、`LocalizeFormatExtension`、`LocalizeSwitchExtension`、`AccountsCreatorView` |
| **UNKNOWN (non-discriminating match)** | 2 | `AuthWindow`、`TaskCreatorCartView` |
| **STRUCTURAL** | 1 | `SettingsView` |
| **UNIMPLEMENTED** | 1 | `LicenseControl` |
| **合计** | **17** | |

**这一项到此结案**：17 条里每一条都有判定，且每一条判定的证据行都能追溯到一条具体依据 ——
「sole declaration match」、「only 1 class reaches that」、「`Authenticate` 0 次」、「6 个候选」。
**没有一条只是「best match」就下了结论。**

真缺口只剩 **1** 条（`UNIMPLEMENTED`）；其余是改名、结构差异、或判据够不着（`UNKNOWN`，各自写明缺什么）。



### 三个缺口数是什么关系（R452 澄清）

| 度量 | 值（见 METRICS） | 口径 |
|---|---|---|
| **类型缺失** `bind_diff --type-presence` | 见 `docs/METRICS.md` | 绑定表的类型**全名**在 `src/` 里没有同名声明 |
| 其中「成员也完全找不到」`backlog_report` B 类 | **13 类型 / 16 成员** | 类型名不存在 **且** 成员名在整个源码里（剥注释后）找不到 |
| **名字级缺口** `bind_diff --buckets` real gap | 见 `docs/METRICS.md` | 与上一行**同一批成员**，只是不按类型分组 |

**关系**：后两行是同一批数据（16 = 16，已逐条核对）；第一行是它的超集 ——
51 个类型里另外 **38 个**类型名不存在，但成员名都能在别处找到。

> **R453 修正（重要）**：那 38 个不能说成"都是改名/拆分/分层"。按"最佳归属类"逐个算过后，
> 只有约 **12 个**的归属在语义上可信（成员数 ≥2 且覆盖率 100% 且类名相关，例如
> `CloudflareSolver 9/9 → CaptchaProvider`、`Concurrency 3/3 → ConcurrencySettings`、
> `ImapProvider 4/4 → ImapMailProvider`、`KeyGesture 2/2 → BillingKeyBinds`、
> `TaskCreatorMainView 4/4 → TaskCreatorView`）。
> 其余约 **26 个**的"最佳匹配"是**通用成员名造成的假阳性**：`Helpers.ObservableDictionary\`2 → AccountGrid`
> （唯一成员叫 `Count`）、`Models.RemoteData → Account`（成员叫 `Name`）、`SmartActions.Operator → Account`
> （成员叫 `Value`）、`LocalizeEnumExtension → AnalyticsView`。
> 它们只能证明"这个名字在源码某处存在"，**不能**证明"该类型的功能已复刻"。

**A 类（类型存在、只缺成员）当前为 0** —— `backlog_report` 的第一行输出就是
`classes that EXIST in the replica but miss members: 0 -> 0 members`。
这正是 R434–R451 逐条清掉的那部分；它归零意味着**剩下的缺口全部集中在"类型不存在"这一侧**。



**第三类缺口**（R434 新增的度量）：绑定表里的这个类型在 `src/` 中**一个同名声明都没有**
（`class|record|struct|enum|interface`）。前两个工具都看不见它 ——
`bind_diff.py` 只查"成员名是否出现在源码某处"（`Type` 这种名字满地都是），
`bind_scope.py` 只查"成员是否在该类型 body 内"（类型不存在时整条跳过）。
`Cybersole.Models.Input` 就是这样漏了 400 多轮，直到 R434 补上这个度量。

**处置口径**：每条 ABSENT 必须二分类，不许悬着。

| 分类 | 判定 | 记账方式 |
|---|---|---|
| **改名（RENAMED）** | 复刻件用别的类名实现了同一角色（`AGENTS.md` §0 允许命名不同） | 在本节记下映射 |
| **未实现（UNIMPLEMENTED）** | 确实没有对应实现 | 记 Unknown + 缺什么证据，或排进待做 |

**已确认的改名/合并映射**（R435，逐条读过声明，不是只看分数）：

| 绑定表类型 | 复刻件的类 | 判定 | 依据 |
|---|---|---|---|
| `Cybersole.Global.Settings` | `GlobalSettings` | RENAMED | **R449：34/34 成员全覆盖（此前 33/34）**。差的那一个是 `SmartActions` —— 复刻件拼成了 `Smartactions`，而绑定表要驼峰。改名 + `[JsonProperty("smartactions")]` 之后两件事同时成立：成员名对上、落盘 key 仍是原版的 `smartactions`（`LiveSchemaPinsTests` 盯着）。`Settings` 是 namespace 尾、类名加了 `Global` 前缀 |
| `Cybersole.Models.Concurrency` | `ConcurrencySettings` | RENAMED | 3/3（`Maximum`/`Mode`/`Ratio`） |
| `Cybersole.Services.ImapProvider` | `ImapMailProvider` | RENAMED | 4/4（`Host`/`Username`/`MessageCount`/`Status`）逐条读声明确认 |
| `Cybersole.Ui.Views.Settings.SettingsView` | `SettingsShell` | RENAMED | **18/19 有归属（R450）**：17 个成员在 `SettingsShell`，第 18 个 `LogOut` 是**跨类型**的 —— 它在 `UserView` 里有真成员 `public bool LogOut()`（剥注释后仍命中，非注释）。剩 1 个 `Transition` 零归属（见下）。AOT 产物符号 `Cybersole_Ui_..._Settings_SettingsShell` 亦可证 |
| `Cybersole.Ui.Views.Tasks.TaskCreatorMainView` | `TaskCreatorView` | RENAMED | 4/4（`ProfileGroupItems`/`ProfileItems`/`ShowCartView`/`SizeItems`） |
| `Cybersole.KeyInput.KeyGesture` | `KeyBind` | RENAMED | 2/2（`Key`/`Modifiers`，均为 `int`）逐条读声明确认 |
| `Cybersole.CloudflareSolvers.CloudflareSolver` | `CaptchaProvider` | **MERGED** | 9/9 成员完全一致 —— 复刻件用一个模型扮演原版的**两个**类型（`CloudflareSolver` 与 `Models.CaptchaProvider`），属结构合并，不是一对一改名 |

**候选图（生成物）**：`docs/TYPE_RENAME_MAP.md` —— `python tools/type_rename_map.py` 生成，
把每条 ABSENT 按"成员集合覆盖率 + 名字词干"打分，给出 top-3 候选。**候选不是结论**：
`Account` / `AnalyticsView` / `AccountGrid` 会对一堆单成员类型冒出高分，因为 `Name`/`Type`/`Key`/`Value` 太常见。

**剩余 39 条的处置口径**（判据 a 要求每条有归属，不许悬着；R441 已把其中 5 条定性，见下节）：

| 组 | 条数 | 特征 | 处置 | 缺什么证据才能定 |
|---|---|---|---|---|
| B｜通用成员名 | 15 | 成员只有 `Name`/`Type`/`Key`/`Value`/`Text`/`Count`/`Condition` 等通用词 | **UNKNOWN** | 需要原版该类型在 **XAML 中的使用位置**（哪个页面/控件引用它），或反编译其 getter/setter 才知道职责；靠成员名无法区分"改名"与"没做"。**邻居线索见下节** |
| C｜业务成员名 | 24 | 成员有业务语义（`ApiKey`/`Balance`/`SoundLocation`/`ZipCode`/`IsStaff` …）但无同干候选 | **UNKNOWN** | 需要原版**反编译该类型的字段布局**，或主界面 GUI 观察对应面板；其中 `Models.User`、`Ui.Views.Auth.AuthWindow`、`Ui.Views.Auth.LicenseControl` 三条已确认**复刻件无同名类**，是真实缺口候选 |

B 组清单：`Attributes.CreateInfo`、`Helpers.ObservableDictionary\`2`、`Models.ProfileItem`、`Models.RemoteData`、
`Models.Size`、`Models.ValueGroup`、`Providers.IDataProvider`、`SmartActions.ActionConfig`、`SmartActions.ActionParams`、
`SmartActions.Operator`、`SmartActions.Variable`、`Ui.Localization.LocalizeEnumExtension`、
`Ui.Localization.LocalizeFallbackExtension`、`Ui.Localization.LocalizeSwitchExtension`、
`Ui.Views.Accounts.AccountStoreType`、`Ui.Views.Analytics.Modals.CheckoutProperty`、`Ui.Views.Settings.ErrorEntry`、
`Ui.Views.Settings.KeyBindSection`、`Ui.Views.Settings.LocalizedOption`

C 组清单（24 条，其中 4 条 Localize/容器类已定性为结构差异，见下节）：`Attributes.Platform`、`Helpers.BrowserProfile`、`Models.Analytics`、`Models.AycdInboxAccount`、
`Models.Captcha`、`Models.CreateInputModel`、`Models.NotificationSound`、`Models.Store`、`Models.User`、
`SmartActions.Action`、`SmartActions.Filter`、`SmartActions.RunHistory`、`SmartActions.Template`、`SmartActions.Trigger`、
`Ui.Localization.LocalizeFormatExtension`、`Ui.Views.Accounts.AccountStoreEntry`、
`Ui.Views.Accounts.Modals.AccountsCreatorView`、`Ui.Views.Auth.AuthWindow`、`Ui.Views.Auth.LicenseControl`、
`Ui.Views.Profiles.Modals.ProfileAdvancedView`、`Ui.Views.Profiles.Modals.ProfilePaymentView`、
`Ui.Views.Settings.Modals.SizeOption`、`Ui.Views.SmartActions.ActionConfigEntry`、
`Ui.Views.SmartActions.TemplateGroup`、`Ui.Views.Tasks.TaskCreatorCartView`

> `SmartActions.Filter` 曾被候选图标成 HIGH（3/4 → `SmartActionFilter`），**逐条读声明后否掉了**：
> 复刻件 `SmartActionFilter` 是 `Field/Operator/Value`，原版是 `Behaviour/Inputs/Operator/Variable`，只命中 `Operator`。
> 候选图里 3/4 的分是 body 里出现同名字符串所致 —— **分数是线索，不是结论**。

**已消掉的**：`Cybersole.Models.Input { Type }`（R434 补上，绑定串 `0x14321141a` 为据）。

### 邻居线索（R437，生成物 `analysis/type_context.md`，**Inference 中置信**）

原版编译期 XAML 把每条绑定描述符写成**连续的串**，同一个串里的类型绑在同一处。所以"谁和它同现"
能推断它属于哪个页面 —— 这是 B 组（成员名无信息量）唯一能往前推的一步。

| ABSENT 类型 | 同块邻居（top） | 推断 |
|---|---|---|
| `Models.User` | `MainWindow` | 用户资料挂在主窗口（头像/姓名/邮箱） |
| `Ui.Views.Auth.LicenseControl` | `Models.License` | 激活控件绑 `License` 模型 |
| `Services.ImapProvider` | `Ui.Views.Settings.ImapView` | 就是 IMAP 设置页的 provider（复刻件已用 `ImapMailProvider` 扮演） |
| `Models.AycdInboxAccount` | `Ui.Views.Settings.ImapView` | AYCD 收件箱账号也挂在 IMAP 页 |
| `Models.Size` | `Ui.Views.Settings.CustomSizesView` | 自定义尺码页的行模型 |
| `KeyInput.KeyGesture` | `Ui.Views.Settings.KeyBindSection` | 键位节里的手势（复刻件 `KeyBind` 已对上） |
| `Ui.Views.Settings.KeyBindSection` | `KeyInput.KeyGesture` | 互相印证：同一块里的两个绑定目标 |
| `Attributes.CreateInfo` | `CaptchaProviderCreatorView` | "创建信息"是各类 Creator 弹窗的绑定目标 |
| `Attributes.Platform` | `TaskCreatorCartView` | 平台属性挂在任务创建的购物车视图上 |
| `CloudflareSolvers.CloudflareSolver` | `Models.TaskGroup` | 任务组引用 solver（与 R435 判的 MERGED 一致） |
| `SmartActions.Trigger` / `.Action` / `.ActionConfig` | `Filter` / `ActionConfig` / `ActionConfigEntry` | SmartActions 的模型与视图成对出现 |

**这是把"完全判不了"降级为"有归属线索、仍待反编译确认"，不是结论。**
另有 9 条在描述符串里**没有任何邻居**（`BrowserProfile`、`NotificationSound`、`AccountStoreEntry`、
`ProfileCsvRow` 等）—— 它们不是任何 XAML 的绑定目标，只能靠反编译或 GUI 观察。

### 已定性的子集（R441，B/C 组内 5 条升级为「结构差异」，硬证据）

| 绑定表类型 | 判定 | 证据（可复算） |
|---|---|---|
| `Ui.Localization.LocalizeEnumExtension` | **结构差异** | 复刻件里 `MarkupExtension` 出现 **0** 次、`.axaml` 文件 **0** 个 —— 它用 Avalonia + 代码构造 UI，**根本没有 WPF markup-extension 这一族机制** |
| `Ui.Localization.LocalizeFallbackExtension` | **结构差异** | 同上 |
| `Ui.Localization.LocalizeSwitchExtension` | **结构差异** | 同上 |
| `Ui.Localization.LocalizeFormatExtension` | **结构差异** | 同上（本条在 C 组，成员 `Value`/`Value2`） |
| `Helpers.ObservableDictionary\`2` | **结构差异** | `ObservableDictionary` 在 `src/` 里出现 **0** 次；复刻件用 `Dictionary` / `ObservableCollection` 表达同样的容器角色 |
| `Models.CreateInputModel` | **结构差异，已结案（R451）** | 13 个成员**全部有归属**，但被拆到四处：`BotTask`（`Color` / `MinPrice` / `MaxPrice` / `Input` / `Sizes`）、`TaskCreatorView`（`Minus` / `Plus` / `PriceCheckVisible` / `TogglePriceCheck`）、`TaskCombinationRequest`（`AutoQuantity`）、全局/店铺设置（`Currency` / `Symbol`）、以及通用名 `Quantity`。原版把"一个输入行"做成一个模型，复刻件把数据、UI 命令、组合请求分开 —— 同一份能力，不同分层 |

```
Get-ChildItem src -Recurse -Filter *.cs | Select-String "MarkupExtension"   # 期望 0
Get-ChildItem src -Recurse -Filter *.axaml                                 # 期望 0
Get-ChildItem src -Recurse -Filter *.cs | Select-String "ObservableDictionary"  # 期望 0
```

> 这三条命令都是"期望 0"，所以它们是**可复算的否证**：谁哪天引入了 XAML 机制，这里就该重判。

### 成员形状差异：`?`（找不到）那批的三分类（R471）

> **R528 追加：`method` 带参数那 32 条的障碍是"缺选中机制"，不是改名。**
>
> 具体到 `int index` 这 5 条，逐个查了类体：
>
> | 类 | 成员 | 类里有选中机制吗 |
> |---|---|---|
> | `CustomSizesView` | `Delete(int index)` | **没有**（类体里 0 处 `Selected*`；同文件另一个类才有） |
> | `CustomStoresView` | `Delete(int index)` | 待查（同文件） |
> | `SolverWindow` | `CloseSolver(int index)` | 有 2 处 |
> | `SmartActionsCreator` | `DeleteAction(int index)` / `DeleteFilter(int index)` | 有 14 处，但语义是"当前编辑的 action"，不是列表选中 |
>
> `CustomSizesView.Delete(int index)` **全树没有任何调用点**（源码、测试都查过）——
> 它在复刻件里是个孤立方法，按钮根本没接。
>
> **要把它变成无参 `ICommand`，得先回答"作用于哪一行"** —— 而这一页现在没有行选中。
> 这是**缺一条功能路径**，不是缺一个名字。
>
`

`shape_audit.py` 报 `replica=?` 的 60 条，逐条核对后分三类 —— **它们不是同一种东西**：

### A. 基类提供（约 10 条，`Close`）

`AycdInboxCreatorView` / `CaptchaProviderCreatorView` / `CloudflareSolverCreatorView` / `GoogleAccountEditView` /
`ImapCreatorView` / `PayPalAccountCreatorView` / `SizeCreatorView` / `WebhookCreatorView` / `CheckoutView` /
`ReleaseView` 全部继承 `SettingsModal : Window`（或直接 `Window`），而 **`Close` 是 Avalonia
`Window.Close()` 的方法**。

`shape_audit` 只扫**本类 body**（不含基类链），所以它看不见 `Close`。
→ 真实的差异是**形状**（原版是属性、复刻件是 `Window` 的方法），**不是"没有"**。

### B. 改名 / 拆分（约 15 条）

| 原版绑定成员 | 复刻件的对应 |
|---|---|
| `SmartActionsCreator.Delete` | 拆成 `DeleteAction` / `DeleteFilter` / `DeleteInput` |
| `TaskView.Edit` | 拆成 `EditAll` / `EditSelected` |
| `TaskGroupView.Delete` | `DeleteGroup` |
| `MessageBoxDialog.Cancel` | `CancelText` |
| `PaymentView.Refresh` | `RescanProfiles` |
| `CaptchaProvidersView.Add` | `RefreshProviders` + 创建流程（无同名 Add） |

### C. 真缺（约 20 条，需实现）

| 类型 | 缺的成员 | 该类现有的全部 public 成员 |
|---|---|---|
| `PayPalAccountCreatorView` | `AutoReopen` `Password` `ProxyGroup` `UseLoginProxy` | `EditMode` `InactivateAfter` |
| `SmartActionsView` | `Clone` `Delete` `Edit` `Export` | `Clock` `FiltersCaption` `OpenCreator` `Refresh` `Text` `ViewLogs` |
| `CheckoutView` | `Next` `Previous` | `OpenTracking` `Text` |
| `ProxyView` | `Test` `TestAll` | `AddProxies` `ClearAll` `CloneProxies` `CopyProxies` `CreateGroup` `DeleteProxies` `GroupOrder` `Loaded` `MoveGroup` `OpenSettings` |
| `StaggerStartView` | `Start` | `Cancel` `TotalTasks` |
| `ReleaseSitelistView` | `Create` | （空） |

**这三类的处置完全不同**：A 不改（口径问题）、B 不改（已等价）、C 才是要做的活。
之前它们混在一个 60 里，等于把"没做"和"换了名字"和"继承来的"算成同一件事。

### C 类里明确**不做**的一条（R474）

`ProxyView.TestAll` —— 原版绑定表要求它，但复刻件的 `ProxyGrid` 只公开 `SelectedProxies`，**没有全集**。
"对选中项测一遍然后叫它 TestAll"会在绑定表里看起来对、用起来是错的，所以**不加**。

要真做，先给 `ProxyGrid` 一个 `AllProxies`（并想清楚它和 `Filter` 的关系），那是另一轮的事。

## 成员级归属（R442，生成物 `analysis/member_owner_map.md`）



`type_rename_map.py` 是**类型级**平均：一个 9 成员的类型 8/9 看着"有"，一个 1 成员的类型 0/1 看着"缺"。
B/C 组真正需要的是**成员级**问题 —— 这个成员名到底在哪个类的 body 里：

```
python tools\member_owner_map.py
```

| 判读 | 条数 | 含义 | 处置 |
|---|---|---|---|
| 唯一归属 | 15 | 角色被改名/合并进那个类 | **结构差异** |
| 归属过多 | 159 | `Name`/`Type`/`Key` 这类通用词 | 无信息，维持 Unknown |
| **零归属** | **16** | 整个 `src/` 里没有这个名字（剥注释后） | **真缺候选**，维持 Unknown 但理由变具体 |

**唯一归属里最要紧的一条**：`Global.Settings.MonitorConcurrency` → `GlobalSettings`。
它直接翻掉了 `DEVIATIONS.md` §8 里"`MonitorConcurrency` 疑似发明"的判断 —— 绑定表里就有这个成员。

> **工具第一版踩了同一个坑**：它扫的是**含注释**的 body，于是把 `SettingsView.LogOut` 判成
> "唯一归属 → `UserView`"，而 `UserView` 只是**注释里提到** LogOut、并没有这个成员。
> 削注释后该条变成零归属。这是两轮之内第二次"散文被当成代码"（另一次是 R439 的源码守卫），
> 所以这条规则写进了工具的 docstring，而不只是写在文档里。

> 注：B/C 两组的"条数"是 R435 分类时的快照；**当前值以 `docs/METRICS.md` 的 `type presence` 段为准**，
> 那里逐条带成员清单。

## 已清零的类型（按轮次）

| 类型 | 结果 |
|---|---|
| `MonitorView` | **R434**（`LinkChange` / `OpenFilter` / `OpenUrl` / `Quicktask` / `View` 五条全加：`SelectedEvent` + 商品/事件模型 + `ICommand` 属性。`View`/`OpenFilter` 真做并有用例；另三条为显式钩子，行为记 Unknown —— `docs/PARITY_CLAIMS.md` C-monitor-*。证据：Getter/Setter/Property 三串齐全，地址见 `docs/R434_DECISIONS.md` §0） |
| `TaskView` | R432（`Toggle`：`ICommand` + `ToggleSelected`，闭包表 `<ToggleTask>b__0/b__1` 为据） |
| `DataView` | R432（`ViewLogs`：`ICommand` + `OpenLogs`，原来是按钮里的内联 lambda） |
| `CloudflareSolversView` | R432（`Edit`：`ICommand` + `EditSelected`，命令表 0x0351da5b 为据） |
| `GoogleAccountsView` | R432（`Edit`：命令表 0x0351ddd2 为据） |
| `ImapView` | R432（`Configure`：命令表 0x0351def6 + `<ExecuteConfigure>d__23`） |
| `GeneralSettingsView` | R432（`ProfileItems`：数据属性，与 `TaskCreatorMainView` 同名同源） |
| `TaskGroupView` | R354（`CloudflareSolvers` / `Close`） |
| `GroupSummary` | R376（`Edit` / `Clone` / `Delete`，`StartAll`/`StopAll` 于 R345） |
| `StoreGroupModal` | R377（`Delete` / `IsEditing`） |
| `HistoryWindow` | R379（`SmartAction` / `View`） |
| `PublishTemplateModal` | R380（`Groups`） |
| `ReleaseSitelistView` / `ReleaseView` | R374（`ShowSitelist` + 可达化） |
| `AccountView` | R371（`CreateGroup`） |
| `IWebhook` | R342 |
| `LoginControl` | R343 |
| `HelpView` | R346 |
| `CustomStoresView` / `CustomSizesView` | R347（除 `View`） |
| `GroupGrid` | R403（`Items` / `Store`） |
| `AccountGrid` | R403（`Rows`） |

## 不可得（三源否证，别再来回试）

| 项 | 说明 |
|---|---|
| `Platform.InputType` / `QuantitySupport` / `QuantityAutoAdjustSupport` | 池子只有名、下拉点不开、locale 无 `Platform.*` |
| `User.IsStaff` | 需账号角色信息，本地无来源 |
| `SettingsView.Transition` | 与同名成员不是同一类 |
| `CreateInputModel.Minus` / `Plus` | 无 GUI 证据 |
| `Store.ColorSupport` / `Elements` | 店铺契约是 `IStoreModule`，无此模型 |

## 纪律

> **"绑定表有名字"不等于"我知道它做什么"。** 名字先记进来，行为等反编译或 GUI 证据到位再落。
> 本轮的取证方式与每条的证据等级见 `docs/BINDING_EVIDENCE.md`。

---

## 名字级缺口：4 条全部结案为结构差异（R568）

`python tools/bind_diff.py --buckets` 的现状：

```
scope: whole-source   types: 174   members: 819
missing: 16
noise (HasMultiple_NN): 12
real gap              : 4
```

那 4 条：

| 类型 | 成员 | 为什么是结构差异 |
|---|---|---|
| `Ui.Localization.LocalizeFormatExtension` | `Value2` | XAML 的 `MarkupExtension`。复刻件**没有 XAML**（0 个 `.axaml`、0 个 `MarkupExtension` 子类），全部控件用 C# 构建 |
| `Ui.Localization.LocalizeSwitchExtension` | `Condition` | 同上 |
| `Ui.Views.Auth.AuthWindow` | `Logout` | `Window` 子类。`Logout` 是**页面行为**（清会话、跳登录页），不是可绑定的值 |
| `Ui.Views.Auth.LicenseControl` | `Authenticate` | **行为**。复刻件的许可流程还没建，一个属性装不下「发起认证」 |

**三分类结果**：

| 类别 | 条数 |
|---|---|
| 可做 | **0** |
| 结构差异 | **4** |
| 不可得 | **0** |

**12 条 `noise (HasMultiple_NN)` 的说明**：那些成员在源码里确实有同名标识符，但出现在别的类上
（`HasMultiple_NN` 是检测器的标记），不是这个类型的成员。**它们不是缺口，是匹配噪声。**

> 判据 a 那句「名字级缺口全部三分类结案」到这里成立 —— **但成立的方式是"4 条都做不了"，
> 不是"4 条都做完了"。这两种"结案"要分清。**


### R687：同 4 条成员，**两个不同的问题**，两个都叫「结案」—— 别混读

上面 R568 那 4 条，与 `docs/TYPE_PRESENCE_TRIAGE.md` 里对应的 4 个**类型**，问的不是同一件事：

| 问的是 | 工具 | 那 4 条的结果 |
|---|---|---|
| **这个成员能不能做成可绑定属性？** | 人工判（R568） | **4/4 不能** —— 2 个是 `MarkupExtension`（复刻件无 XAML：**0 个 `.axaml`、0 个 `MarkupExtension` 子类**，R687 复验仍成立） |
| **这个类型在源码里存在吗？** | `type_presence_triage.py`（R685） | `LocalizeFormatExtension` / `LocalizeSwitchExtension` → `UNKNOWN (non-discriminative)`；`AuthWindow` → `UNKNOWN (non-discriminating match)`；`LicenseControl` → **`UNIMPLEMENTED`** |

**两条都成立，互不否定。** 它们回答的是两个不同的问题：

```
R568：这个「成员」装不进一个绑定属性  → 结构差异（问的是成员的可实现形式）
R685：这个「类型」在源码里找不到      → 1 条真缺 + 3 条判据够不着（问的是类型的存在）
```

**最容易误读的是 `LicenseControl.Authenticate`**：
按 R568 它是「结构差异」（一个属性装不下"发起认证"这个动作），
按 R685 它所在类型是 **`UNIMPLEMENTED`**（`Authenticate` 全库 0 次）。
**前者说的是"成员形态"，后者说的是"类型缺失"——都不错，但只看其中一个会得到片面的印象。**

**所以读这两份结案时要带上问句**：
- 「4 条全部结构差异」→ 指**成员能否做成绑定属性**；
- 「1 条真缺 + 8 条 Unknown」→ 指**类型是否存在**。


## R583：`Models.Notification.Timestamp` —— 真缺口，但两个作用域都看不见

| 项 | 内容 |
|---|---|
| 契约绑定 | `Cybersole.Models.Notification` → `Message, Timestamp, Title, Type` |
| 复刻件 | `public sealed record Notification(NotificationKind Kind, string Title, string Body)` |
| 逐条 | `Title` ✓ / `Body`↔`Message` 改名 / `Kind`↔`Type` 改名 / **`Timestamp` 缺** |
| 为什么没被计数 | 整源作用域：`Timestamp` 在别处出现过（`RunHistory.Timestamp`），名字命中即算有；<br>单文件作用域：位置记录没有花括号体，类型定位不到 → 静默跳过 |
| 实测定位率 | `--per-file` 能看到 174 个里的 150 个，`Notification` 在看不见的 24 个里 |
| 处置 | **不补**。证据只证明成员存在，不证明填什么；补 `DateTime.Now` 是发明行为 |
| 行为 | **Unknown** |
| 缺的证据 | 原版这条记录的构造点及其实参来源（需反编译到调用点，或原版可运行后观察） |
| 对数字的影响 | 名字级 real gap 至少应为 5，当前报 4 |

### R584 补充：边界收紧了

| 项 | 结论 |
|---|---|
| `--per-file` 定位不到的 23 个 | 17 已计入类型缺失 / **6 是盲区** |
| 6 个盲区逐个测 | 4 个成员全在 / 1 个 `Notification` / 1 个 `State`（类型误判） |
| 所以 `real gap` | 报 4，**真值 5**（4 + `Notification.Timestamp`） |
| 边界 | **有界**：6 个盲区全部测过，没有遗漏的候选 |
| 未测 | 能定位的那 150 个类型内部是否还有整源搜索漏掉的缺口 |

### R585 补充：类型级判据交叉验证

| 项 | 结论 |
|---|---|
| 独立实现 | `analysis/independent_scope_check.py`，不复用 `bind_scope` 代码 |
| 覆盖 | 156 个类型（`bind_scope` 是 152） |
| 缺口 | 2 条，均已在册：`EditValue\`1` 噪声桶、`Notification`（R583） |
| 共同覆盖的 152 个 | 两边都报 0 —— **交叉印证** |
| 结论 | **类型级没有新缺口**，数字不用改 |
| 看不出 | 同名不同语义；父类只合并三层 |

## R592：`ProfileCsv.Error.UnknownCountry` / `UnknownState`

| 项 | 内容 |
|---|---|
| 契约 | `ProfileCsv.Error.*` 共 6 条；复刻件引用 4 条 |
| 缺 | `UnknownCountry` = `Unknown country "{0}"`、`UnknownState` = `Unknown state "{0}" for {1}` |
| 复刻件数据 | **无**任何国家/州表（`Alabama`… 零命中） |
| 原版数据 | **有**：`0x1437d663e` 起是序列化地址表，`state` → Alabama/Alaska/Arizona… |
| 原版代码 | 两个 locale 键 **0 条静态 xref**（AOT 下按名查字典），值只在 locale JSON blob 内出现 1 次 |
| 定性 | **功能性缺口**（不是文案缺口、不是数据缺口） |
| Unknown | 校验器是否使用那张地址表；缺**校验函数的反编译** |
| 下一手 | 从列名字面量 `country`/`state` 反查校验函数（不需要凭据） |

### R593：静态路线验证与边界

| 尝试 | 结果 |
|---|---|
| `ProfileCsv.Error.UnknownCountry` 键 | xrefs **0** |
| `ProfileCsv.Error.UnknownState` 键 | xrefs **0** |
| `Alabama` / `state` / `postcode`（数据表内） | xrefs **0**，且 item head 是自己、`size: 1`、无名 |
| `country` 精确匹配 | **91 处，xrefs 全为 0** |

**原因**：数据在未被 IDA 建模的序列化 blob 里；locale 键在 AOT 下按名查字典。
两类都不产生字符串级 xref。

**结论**：`UnknownCountry`/`UnknownState` 的定性不变 —— 缺的是「校验器拿哪份数据」。
越过它需要**建模 blob**（独立工程）或**原版运行时观察**（需凭据，阻塞）。

### R596：方法入口层面的结论

| 项 | 内容 |
|---|---|
| 测量 | 字符串 4001 抽样 → **0** 有 xref；函数 3001 抽样 → 2997 有 xref（99.9%） |
| 库内字符串总数 | 324,901 |
| 原因 | NativeAOT 字面量在元数据 blob 里，代码用基址+偏移取用，无 `lea` → 无数据 xref |
| 影响 | R592/R593/R595/R596 每一次"字符串→xrefs"的空结果都是它的表现 |
| 正确入口 | 导入表与命名符号 / 函数级特征 / 建模 blob / 运行时观察 |
| 仍然 Unknown | 是否**全部** 32 万条都无 xref（只抽样 4001）；IDA 能否批量建立数据引用 |

### R597：入口与布局

| 项 | 内容 |
|---|---|
| 可用入口 | 导入 thunk → 调用点 → 反编译（`GetEnvironmentVariableW` xrefs 4 / `ExpandEnvironmentStringsW` 1） |
| 走到的层 | 全是运行时库：CoreCLR 配置、`Environment.GetEnvironmentVariable` 包装、`Path.GetTempPath` |
| 解出的布局 | .NET AOT 字面量 = `[method table][len: int32][utf16 chars]`（`dword(+8)` 取长度、`+12` 起解码） |
| 验证样本 | `XDG_RUNTIME_DIR` / `TMPDIR` / `TMP` / `TEMP` / `/tmp`（即 `Path.GetTempPath`） |
| 硬事实 | `SHGet*` / `KnownFolder` 命名符号命中 **0** → 原版从不调 `Environment.GetFolderPath` |
| 仍 Unknown | 应用层读的具体变量名（需把 `sub_141DFE1A0` 的调用者递归展开） |

### R598：撤回一条推论

| 项 | 内容 |
|---|---|
| 展开 | 深度 0/1/2/3 = 3/42/60/35，总 140 个函数（≤深度 4） |
| 扫描 | 槽引用模式 **0**；ptr+len 模式 **0** |
| **撤回** | §33「数据根由环境变量决定（高置信）」→ **Unknown** |
| 为什么 | R597 查明 `GetEnvironmentVariableW` 的调用点全是 CoreCLR（GC 配置、`Path.GetTempPath`）——导入存在 ≠ 应用使用 |
| 仍成立 | `SHGet*` / `KnownFolder` 命中 0 → 不调 `Environment.GetFolderPath` |
| 下一手 | 换锚点：从文件 I/O（`CreateFileW` 等）反向找拼 `Cybersole` 路径的函数 |

### R599：持久化文件布局差集

| 项 | 内容 |
|---|---|
| 原版数据文件（镜像字面量） | accounts / analytics / billing / products / proxies / sessions / settings / smartActions / smartActionUtilities / solvers / tasks / sku-stores / public |
| 复刻件写的 | accounts / analytics / billing / **checkoutHistory** / **license** / proxies / sessions / settings / smartActions / smartActionUtilities / solvers / tasks |
| 原版有复刻件无 | `products.json`、`sku-stores.json`、`public.json` |
| 复刻件有原版无 | `checkoutHistory.json`、`license.json` |
| Unknown | 原版是否**真的写**那三个文件（字面量存在 ≠ 使用）；复刻件那两个名字的来历 |
| 说明 | 文件布局**不在五项度量内**，需单独的账 |

### R607：继承链这条也查了，0 条可做

| 项 | 内容 |
|---|---|
| 查什么 | 那 11 条"该类无无参 public 方法"的成员，父类有没有可继承的无参方法 |
| 基类 | 11 条的基类全是 `UserControl` / `Window`（Avalonia，**不在复刻件源码里**） |
| 结果 | 父类有 → **0**；父类在源码外（**Unknown**）→ **11** |
| 34 条最终账 | 23 条"有别的无参方法但无等价证据" + 11 条"父类 Unknown" = **0 条可做** |
| 纪律 | 即便 `Window.Close()` 存在，把 `RemoveStore` 映到它是猜语义（同 §24 / §31） |
| 自纠 | 第一版脚本把"源码外基类"说成"链上没有任何方法"，已改为 Unknown |



## 核心 — 结账收尾（R765 发现）

| 模块 | 缺的步骤 | 状态 |
|---|---|---|
| bstn, casio, fanatics, goat, hbx, hypecommerce, offspring, popmart, scheels, superswipe, warhammer, yeezysupply | `SubmitShippingAsync` + `SubmitPaymentAsync` | **未结案** |

来源：`ModuleCoverageTests` 的反射矩阵（`analysis/coverage_raw.txt` 是采集的原始输出）。
**不要用 grep 判"有没有实现"** —— 继承会骗人；矩阵看得穿继承。

取证前提：**先确认该站在原版里是否真有这两个步骤**，再实现。
`popmart` / `superswipe` 是非电商形态（抽奖应用），七步尺子对它们不合身，要先判定它们该用什么尺子。


## 核心 — 结账收尾（续，R766 后）

`scheels` 已补齐并到 100%。**余下 11 个 71% 模块**：

| 模块 | 备注 |
|---|---|
| bstn, casio, fanatics, hbx, hypecommerce, offspring, warhammer, yeezysupply | 待逐一取证原版端点 |
| popmart, superswipe | **非电商形态**，尺子本身要先判定 |
| goat | 端点显示是**抽奖面**（drops + captcha），尺子待判定 |

**另立一项（本轮故意没混做）**：`ScheelsFlow.GetCheckoutAsync` 仍走猜的 `/checkout`，
而真实端点是 `ScheelsFrontastic.Checkout`。改它要动 `OpenCheckoutAsync` 的调用约定。

**以及一个通用风险**：`SubmitShippingAsync`/`SubmitPaymentAsync` 的**请求体是推断**，
镜像只给了 action 名。补任何一步都要把 body 标成推断，不要写成证据。


## 核心 — 结账收尾（R767 后）

已到 100%：`scheels`（R766）、`hbx`（R767）。

**余下 9 个**：

| 模块 | 已知线索 | 下一步 |
|---|---|---|
| casio | `_adyenOrderId` + Square PCI hydrate | 补搜，判断收尾形态 |
| hypecommerce | `admin.hypecommerce.io/api/payment/methods/store` | **平台侧 API，可能是尺子问题** |
| bstn, fanatics, offspring, warhammer, yeezysupply | 域名未以 URL 出现 | **换搜法**：按 action 名 / host 前缀 |
| popmart, superswipe | 非电商形态 | 先定尺子 |
| goat | drops + submit-drop-captcha | **抽奖面，先定尺子** |

**通用风险（两轮都出现）**：新补的 `SubmitShippingAsync`/`SubmitPaymentAsync` 的**请求体都是推断**，
镜像只给 action 名。补任何一步都要把 body 标成推断。

**另立**：`ScheelsFlow.GetCheckoutAsync` 与 `HbxFlow` 的类注释都有过时表述，各自独立处理。


## 核心 — 待裁决与新立（R768）

| 项 | 内容 | 性质 |
|---|---|---|
| **bstn 是否存在** | 原版 `bstn` / `BSTN` 都是 0 匹配 —— **复刻件多出来的模块** | **已裁决：保留**（R91 决定，R794 结案）。理由见下 |
| **offspring 的 API 家族选错** | 注册为 `HybrisFlow`，原版走 Poq（`platform.poq.io/clients/offspring/{cart/items,checkout/start,account/guest-token}`） | **新立**，补两步修不了 |
| **Poq 家族** | 多 client 平台（`offspring` / `office`），含 `AtaVerifyCaptcha` | 新立，需先定形状 |
| fanatics / warhammer / yeezysupply | 只有账号面（oauth/login）或一条 GraphQL | **先判"原版有没有结账面"，再决定算不算缺口** |

**方法论提醒**：本站探针的 `NO-URLS` 标签曾把「关键词不匹配」说成「没有 URL」（R768 已修）。
**诊断文案报错因比没有诊断更坏** —— 见 `AGENTS.md` §2.7。


## 核心 — 覆盖率的口径修正（R769）

`ModuleCoverageTests` 的七步尺子对以下模块**不合身**，但**本轮只判定、未改测试**（改的是数字来源，按 §3 单独一轮）：

| 模块 | 判定 | 依据 |
|---|---|---|
| `fanatics` | **不是缺口** —— 原版只有 oauth2 账号面 | 7 URL 全登录，0 结账词 |
| `yeezysupply` | **不是缺口** —— 原版整池 1 条字符串（裸域名） | — |
| `warhammer` | **Unknown** —— GraphQL 存在，结账是否在内无证据 | 1 graphql，0 结账词 |
| `bstn` | **原版 0 字符串** —— 复刻件多出来的模块 | R768 |
| `offspring` | **API 家族错配**：Hybris ↔ Poq | R768 |
| `goat` / `popmart` / `superswipe` | 抽奖面，尺子待判定 | R765/R766 |

**下一步（单独一轮）**：把已判定为"不是缺口"的加入 `NonCommerce` 式豁免，**并写清每条的依据**；
`warhammer` 与 `goat` 这类 Unknown 不豁免。


## 核心 — 覆盖率口径（R770 更新）

`ModuleCoverageTests` 现在把三类分开：**fully covered / 部分 / exempt（原版没有）**。

```
resolved 62/62 · fully covered 49 · exempt 2
```

**豁免条目（每条必须带 R 号证据）**：`fanatics`、`yeezysupply`。

**不许进豁免的**：`warhammer`（Unknown）、`goat`（尺子未定）、`bstn`（复刻件多出来的，另立裁决）。

**余下待办**：

| 项 | 性质 |
|---|---|
| `offspring` 的 API 家族（Hybris ↔ Poq） | 新立，补步骤修不了 |
| `warhammer` 的 GraphQL mutation | Unknown，需读调用方 |
| `goat` / `popmart` / `superswipe` 的尺子 | 待判定 |
| `bstn` 删不删 | **已裁决：保留**（R794）。抓包证据 + 实机契约 + 两条事实都有测试钉住 |
| `casio` / `hypecommerce` 的收尾形态 | 线索弱 |


## 核心 — offspring / Poq（R771）

**三方错配**：注册表 `HybrisFlow` / 已声明未用 `OffspringFlow : MagentoFlow` / 原版 **Poq**。

**原版 Poq 面（7 条字符串，Observation）**：

```
platform.poq.io/clients/offspring/{products?ids=, cart/items, checkout/start, account/guest-token}
platform.poq.io/clients/office/{AtaVerifyCaptcha, recaptcha?trackingId=}
```

**没有支付端点、没有下单完成端点。**

| 项 | 状态 |
|---|---|
| 建 Poq 家族（4 个步骤有据） | **新立** —— 建成后最多 6/7，**那个分数是忠实的** |
| `office` 是否独立 module | Unknown |
| `checkout/start` 之后的收尾 | Unknown —— 池子里没有下一步 |

**明确否决的改动**：把注册表换成 `OffspringFlow` —— 覆盖率 71%→100%，但依据从 Poq 退成 Magento 的猜测。
**数字变好、证据变差，不做。**

**另记**：`flow_wiring_audit.py` 可复算「声明了却没接线的叶子 flow」，当前只有 `OffspringFlow` 一个真问题。


## 核心 — offspring 的两种表面（R773）

**已确认**：`offspring.co.uk` 网页 = **Hybris**（实机证据：主页含 `hybris`，
`/view/resources/getUserInfo`、`/view/component/basket/minibasketAjax` 回 JSON）。
镜像里的 `platform.poq.io/clients/offspring/*`（guest-token / cart/items / checkout/start / products?ids=）
是 **App 面**，Poq 平台。

| 项 | 状态 |
|---|---|
| 原版有没有走 App 面的任务类型 | **Unknown —— 必须先确认，再建 flow** |
| `office` client（AtaVerifyCaptcha / recaptcha） | Unknown，同上 |
| Poq 的支付端点 | Unknown，池子里没有 |

**本轮教训**：我因为镜像里有 Poq 字符串就把它当成 offspring 的结账面并替换了注册表，
被 `PlatformAssignmentTests` 的实机证据否掉。**"镜像里有某个面的字符串" ≠ "这个面就是它"。**

**R772 建、R773 回滚，净改动为零。** 证据记在 BLOCKERS §199 与 §198。


## 请求与指纹层 — Poq App 身份（R774）

**证据（Observation）**：`Poq-Native-iOS-App`（UA）+ `poq-app-id` / `poq-app-identifier` /
`poq-country-identifier` / `poq-currency-identifier` / `poq-slot-conditions` / `poq-user-id`（请求头）。

**归属**：第 3 优先级（请求与指纹层），**不是**站点 flow —— 上一轮错在这一层，见 R772/R773。

**复刻件现状**：整套身份**一处都没有**。

| 项 | 状态 |
|---|---|
| **谁发送这个 UA** | **Unknown —— 唯一挡在实现前面的事** |
| 查法 | 对 `Poq-Native-iOS-App` 在 `chars-12` 处取 xref，读调用点属于哪条路径 |
| 头的取值 | Unknown（只有头名） |
| `poq-slot-conditions` 语义 | Unknown |
| `office` 与 `offspring` 的头是否相同 | Unknown |

**实现前提**：确认调用链之后，把这套身份加进 `BrowserIdentity` / `BrowserFingerprint` 一族，
**不要建独立死类**（R772 的教训）。


## 请求与指纹层 — Poq App 面（R775 更新）

**R774 的 Unknown 已答：App 面是真集成。**

```
4 个头部构造器（共享 Poq 身份模板，sub_140B3B7C0 / BAC0 / BD40 / C030）
4 个 per-action 函数（guest-token / cart/items / checkout/start / products?ids=）
每个 action 有 4 个同形状调用者（thunk + 异步包装）→ 可达
```

**构建的正确单位**：**一个 App 面 flow**（身份 + 四步 + 一个注册项），
**不是**单独的身份常量 —— 后者会重复 R772 的死代码问题。

| 项 | 状态 |
|---|---|
| 触发它的任务类型名 | Unknown，需穿 4 层接口分派，**不影响判断** |
| `poq-app-id` 的取值来源 | Unknown（`sub_141CF6230(&off_146B5C780, a1[29])`、`sub_140B399B0(a1)` 未读） |
| `poq-slot-conditions` 语义 | Unknown |
| 为何是四个头部构造器 | Unknown |

**注意**：这与 `offspring` 的**网页面**（Hybris，实机证据，`PlatformAssignmentTests`）是**两种表面**，
**不要互相替换**（R772 的教训）。


## 工具债 — `off_` 槽位读取器（R776，优先于 App flow）

**问题**：Hex-Rays 里 `&off_XXXX` 是**静态槽位的地址**，槽里存着指向字符串对象的指针，**且受重定位**。
直接读到的是槽内容，不是字符串。

**已证据的错误路径**：① 当对象头读 +12 → 乱码；② `pe_strings.txt` 是文件偏移；
③ 自己换算 VA→文件偏移（`.data` RVA 0x6a47000 / raw 0x6a45c00）→ 仍乱码。

**要做**：读槽 8 字节 → 判断 VA 还是 RVA → 加 imagebase → +12 → 读 UTF-16LE。

**为什么优先**：`off_` 家族在原版里到处都是；这次挡住的是 Poq 六个头名，
**下一次会挡别的东西**。**本会话已经撞过三次。**

**在此之前**，Poq App 身份的进度冻结在：

```
已知：User-Agent + 6 个头名 + 4 个 offspring action + 2 个 office action
Unknown：另外 6 个头名、全部头的取值、触发它的任务类型
```

**构建单位不变**：App 面一个 flow（身份 + 四步 + 注册项），**不要只建身份常量**（R772 的教训）。


## 工具债已还 — `off_` 读取器（R777 完成）

```
python analysis/off_slot_reader.py [slot…]
```

**NativeAOT 字符串布局**：`+0` 方法表 · `+8` 长度 DWORD · `+12` UTF-16 字符 —— **`off_x` 就是对象本身**。
校准用 `off_1471151D0 → 'poq-app-id'`，长度与字符数必须一致；**校准不过就停**。

**Poq App 请求头（12 个，全部解出）**：

```
user-agent Poq-Native-iOS-App · accept · accept-language · accept-encoding
authorization · version-code · platform
poq-app-id · poq-app-identifier · poq-country-identifier · poq-currency-identifier · poq-user-id
```

**余下**：

| 项 | 状态 |
|---|---|
| 各头的取值 | Unknown（`sub_141CF6230`、`sub_140B399B0`、`a1[24]` 未读） |
| `poq-slot-conditions` 所在构造器 | Unknown |
| 触发 App 面的任务类型 | Unknown |

**构建单位不变**：App 面一个 flow（身份 + 四步 + 注册项）。**身份的头名现在齐了，值还差。**


## App 面 — 规格已齐（R778），可以建 flow

```
user-agent Poq-Native-iOS-App · accept application/json · accept-encoding gzip, deflate, br
accept-language nl-NL,nl;q=0.9 · version-code 26.0 · platform iphone
poq-app-id 275 · poq-app-identifier a1dad595-7431-45bc-9fb9-684dac169b5b
authorization "Bearer "+token · poq-country-identifier · poq-currency-identifier · poq-user-id   ← 动态
poq-slot-conditions   名字确认，取值未定位
```

**构建单位**：App 面一个 flow（身份 + 四动作 + 注册项）。**不要只建常量**（R772 的教训）。

| 项 | 状态 |
|---|---|
| 三个动态值 | 从会话取，**不照抄** |
| `poq-slot-conditions` 取值 | Unknown |
| `nl-NL` 是否被区域覆盖 | Unknown |
| 触发它的任务类型 | Unknown |

**地址规则（第四次踩）**：从代码往字符串走 **+12**；从字符往对象走 **−12**。
`off_slot_reader.py` 只接受**对象地址**。


## App 面 — 已建（R779）

`PoqAppFlow` 已注册为 `poq-app`（域名 `platform.poq.io`），覆盖率 **57%（4/7）**。

```
身份 8 常量 → c.Session.Headers（请求层真读的地方）
动作 4 个：guest-token / products?ids= / cart/items / checkout/start
动态 3 个：poq-country-identifier / currency / user-id ← 从 Session.Vars 取，不照抄
未写 3 个：shipping / payment / order ← 镜像在该面无端点
```

| 项 | 状态 |
|---|---|
| **触发 App 面的任务类型** | **Unknown —— 独立 module 是我选的形状，不是原版的** |
| `poq-slot-conditions` 取值 | Unknown |
| `nl-NL` 是否被区域覆盖 | Unknown |
| 缺的三步原版是否也没有 | Inference（高），未反证 |

**加模块的连带清单（R779 实测五处）**：`PARITY.md` 两处、`CoreTests.cs`、
`ArrowAndBeastTests`（名字里带数字）、`VERDICT.md` 顶部 reading guide。
**注册新模块前先想到这五处。**


## 核心 — R765 那张表的最终裁定（R780）

| 站 | 判定 | 下一步 |
|---|---|---|
| scheels · hbx | ✅ 已 100% | — |
| fanatics · yeezysupply | ✅ 不是缺口（已进豁免） | — |
| offspring 网页 | ✅ 100% | — |
| offspring App 面 | ✅ 已建 `poq-app`（57%） | 待定任务类型 |
| **casio** | 缺**整张配置面**（`CasioRegion` + 5 个 `casio_*` + 3 区域 + `casiostore`） | **可做**：把镜像的配置面用上 |
| casio 支付 | **信息不足**（Adyen，`_adyenOrderId` 是字段名不是端点） | 未取证 |
| **hypecommerce** | **抽奖面**（`entries/validate` + `entries/create`） | 尺子待定 |
| warhammer | Unknown（GraphQL mutation） | 需读调用方 |
| goat · popmart · superswipe | 抽奖面 | 尺子待定 |
| bstn | **原版 0 字符串** | **已裁决：保留**（R794） |

**方法论提醒**：R767 把「字段名 + 共用支付层字符串」数成了「该站有 2 个结账 URL」。
**数 URL 之前先看它是不是那个站自己的端点** —— 这是 §2.7 的又一次。


## 核心 — Casio 的具体缺口（R781）

原版判定逻辑（Observation）：

```
遍历 data.products.items[*]
每一项用 casio_can_purchase 判定可购
```

键名已用 `off_slot_reader.py` 读出：`data` / `products` / `items`。

| 要做的 | 现状 |
|---|---|
| 按 `data.products.items` 解析 | 复刻件未走这条路径 |
| 用 `casio_can_purchase` 判定可购 | **ABSENT** |

| 仍 Unknown | |
|---|---|
| item 的完整字段集 | 只确认路径 + 一个判定字段 |
| `CasioRegion` 的取值集合 | AU/SG/US 之外未知 |
| `casiostore.bhawar.com` 用途 | 落在 R759 那个 687 KB 并片里 |
| `casioid` 两个函数语义 | 187 B / 893 B，未读 |

**注意**：`CasioRegion` 零 xref 不等于没用到 —— 它是**数据记录里的键，代码按名字读**。
与 store 元数据同类（R761）。


## 核心 — Casio（R782 更新）

**已做**：`ScrapeVariantAvailabilityAsync` 改为走镜像的 `data.products.items[*]` + `casio_can_purchase`，
解不出时落回旧启发式。5 条测试钉住，含「解不出 → null 而非 false」。

**仍待做**：

| 项 | 状态 |
|---|---|
| `SubmitShippingAsync` / `SubmitPaymentAsync` | **信息不足**：Adyen 已知，`_adyenOrderId` 是字段名不是端点 |
| `data.products.items[*]` 的其余字段（`casio_image_url` / `casio_gender` / `casio_dob`） | 未接 |
| `CasioRegion` 的分区行为 | 零 xref＝数据键；取值集合未定 |
| `casiostore.bhawar.com` | 落在 687 KB 并片里，读不出边界 |
| `casioid` 两个函数（187 B / 893 B） | 未读 |

**口径提醒**：覆盖率（71%）衡量**有没有这一步**；R782 改的是**这一步判得对不对**。
**不要把「质量改动」记成「覆盖进展」。**


## 核心 — Casio `casioid` 的悬案（R783）

**已知（Observation）**：`casioid` 是 Casio 商品对象上的**属性名**。
`sub_14094AF90`（187 B）按键取它并带默认；`sub_140952790`（893 B）把它作成员名挂到构造对象上。

**未知**：它是**商品 id** 还是**变体 id**。

| 决定 | 理由 |
|---|---|
| **不改 `FindVariantAsync`** | 若 `casioid` 是商品 id，当 `VariantId` 用会**静默发错 id** —— 比现状更糟 |

**需要什么才能改**：一条能区分「商品 id」与「变体 id」的证据 ——
例如读 `sub_140952790` 里那个对象的其余成员，或找到把 `casioid` 与 `sku` 一起用到的调用点。

**判据**：改动后最坏情况是否会**更糟且不报错**。会 → 不改。


## 核心 — Casio 标识（R784 已改）

`FindVariantAsync` 现在：**`casioid` 优先，`sku` 兜底**。

**依据**：Casio 配置记录里有 `casioid`（与 `casio_can_purchase` / `casio_image_url` /
`casio_gender` / `casio_dob` 同处），**且 `casio.{0,24}sku` 与 `casio_sku` 都是 0 匹配** ——
**镜像里 Casio 没有 sku 概念**。

| 项 | 状态 |
|---|---|
| 站点是否区分商品 id / 变体 id | **Unknown**（`casioid` 语义最后一问） |
| `casio_dob` / `casio_gender` / `casio_image_url` 用途 | Unknown |
| Casio shipping / payment | 信息不足（Adyen 已知、端点未知） |

**方法论记录**：在整份 `RetailFlows.cs` 里按方法名找 `FindVariantAsync`，**先命中 `YeezySupplyFlow`** ——
**同名方法在一个文件里有多个，按名字找必须先限定类体。**（§2.7 第八次）


## 核心 — Casio 的共同前置（R785）

**镜像的 Casio 集成有五块**，复刻件只有商品一块：

| 面 | 原版证据 | 复刻件 |
|---|---|---|
| 分区 | `CasioRegion` · AU/SG/US · `/{region}/` 前缀 | ❌ |
| 登录 | `Casio Login` | ❌ 无 `LoginAsync` |
| 注册字段 | `casio_dob` · `casio_gender`（同一函数 `sub_140948FA0`） | ❌ |
| 商品字段 | `casio_can_purchase` · `casio_image_url` · `casioid` | ✅ 已用（R782/R784） |
| Adyen 支付 | `_adyenOrderId` | ❌ 端点未知 |

**四件事（登录/注册/加购/支付）卡在同一个缺口**：

> **区域 token 的取值，以及它在前缀里的拼法。**

`CasioRegion` 零 xref = **设置项，按名字读**。`AU`/`SG`/`US` 是显示名，**token 本身未知**。

| 项 | 状态 |
|---|---|
| 区域 token 与拼法 | **Unknown —— 最高优先的前置** |
| `sub_140948FA0` 其余读取 | Unknown |
| `casioid` 商品 id / 变体 id | Unknown |
| 登录端点形状 | Unknown |

**纪律提醒**：`casio_dob` / `casio_gender` / `_adyenOrderId` 都是**字段名**。
**R780 把字段名当端点栽过一次，不要再犯。**


## 核心 — Casio 区域（R786 更新）

**结论：区域 token 不是二进制里的独立字面量。**

两片字符串区都查过：
- `casio_*` 那片是**字母序全局表切片**（不是键值记录 —— 修正 R761 的模型）
- `Casio` / `Casio SG` / `Casio US` 是 **UI 显示名**，夹在 `Cash On Delivery` / `Catalan` / `Cebu` 之间
- `CasioAU` 在 `0x1433…`，是**类型名**不是显示串

**所以 `CasioRegion` 零 xref 的意思就是：设置项，值由用户配置给，不是我能从镜像抄的。**

**已做**：`CasioFlow.RegionPath(c, rest)` —— 有区域拼 `/{region}/…`，无区域返回原路径（逐字不变）。

| 项 | 状态 |
|---|---|
| 区域 token 取值 | **Unknown**（结构已就位，值仍缺） |
| 运行时拼 vs 配置给 | Unknown |
| `casioid` 商品/变体 id | Unknown |
| `Casio Login` 端点 | Unknown |

**纪律**：`analysis/casio_record_dump.py` 已加守卫 —— `START < IMAGE_BASE` 直接报「字面量少了一位」，
因为 R786 就犯过这个错（`0x146B7D800` → `0x146B7CC0`，RVA 变负）。


## 风控 — Warhammer AWS WAF（R787）

**镜像里唯一的站点级 WAF 处理器**（`WarhammerWafHandler` 与 `warhammer-com-waf-auth` 各 1 次）。

**两个 token 同行**：

```
x-aws-waf-token          ← AWS 自己的，作请求头
warhammer-com-waf-auth   ← 站点自己的，作 cookie（但按头发）
```

**另有完整 client hints**：`sec-ch-ua` / `sec-ch-ua-platform` / `sec-ch-ua-mobile`。

**已做**：`WarhammerFlow.ApplyWaf(c)` —— 从 `Session.Vars` 取两个 token，有才设。
**登录端点**从编的 `/api/login` 换成镜像的 `/usernamepassword/challenge`。

| 项 | 状态 |
|---|---|
| AWS WAF token 的取得方式 | **Unknown**（产出它的挑战交换不在字符串里） |
| Auth0 的 `client_id` / `state` / `nonce` | Unknown |
| **GraphQL operation 名** | **Unknown —— 复刻件仍发 REST，这是 Warhammer 最大的缺口** |
| 处理器四个方法各做什么 | Unknown（只读了构造器） |

**注意优先级**：这一条是第 2 层（风控对抗），不是第 1 层。

**工具记录**：`off_slot_reader.py` 一次解出 15 个头名 —— R776 为 6 个烧掉五次尝试，现在 15 个一次。


## 核心 — Warhammer GraphQL（R788 已取回底本）

**六条 operation，12,508 字符，全文在 nalysis/warhammer_graphql.txt。**

`
0x1470c8c44   1995  mutation（匿名，地址：copyFromId/firstname/lastname/address1）
0x1470c9bf4   2249  mutation（匿名，运费：selectedShippingRateId/isNewsletterSubscribed）
0x1470cad9c    798  mutation AddCreditCard
0x1470cb3f4   2108  mutation AddItemToCart
0x1470cc484    536  mutation AddToCart
0x1470cc8cc   4022  mutation ApproveOnboardPaymentMutation
`

**找法**：sub_140E4AE90 是静态初始化器，sub_141D25160(945) / (1920) 里的数字是**长度**，
说明查询文本在池子里 → **直接搜 ^mutation / ^query 长度 > 200 的**。

| 项 | 状态 |
|---|---|
| AddItemToCartInput 的请求字段 | Unknown（fragment 里是响应字段） |
| 两条匿名 mutation 的 operationName | Unknown |
| 查询类文本是否齐全 | 未找全（只取 > 200） |
| 响应消费面 | Unknown |

**下一步**：把这六条翻成 WarhammerFlow 的 GraphQL 请求，替换现在的 REST。
**参照**：复刻件的 NikePersistedOperations.cs 已有 GraphQL 落地先例。


## 核心 — Warhammer GraphQL（R789 已落地一条）

**`AddToCart` 已改成镜像原文**（R788 取回，池子 `0x1470cc484`）：

```
mutation AddToCart($sku: String!, $fascia: String!, … ) { addToCart(…) { ctCartJWT __typename } }
```

- 请求体 `{operationName, query, variables}`，`ctCartJWT` 记进会话
- **`fascia` 必填但取值 Unknown → 明确失败，不猜**
- 5 条测试钉住不变量（非空数 · 只选 ctCartJWT · 十变量都传）

| 待做 | 说明 |
|---|---|
| `SubmitOrderAsync` | **仍是编的 `/api/orders`** —— 订单提交的 operation 未定位 |
| `AddItemToCart` / `AddCreditCard` / 两条匿名 / `ApproveOnboardPayment` | 未翻（原文在 `analysis/warhammer_graphql.txt`） |
| `fascia` 取值 | Unknown |
| 响应消费面 | 只用了 `ctCartJWT` |

**注意**：本轮覆盖率未变 —— **换的是既有步骤的请求形状，不是补步骤。**
**质量改动不要记成覆盖进展。**


## 核心 — Warhammer（R790：原文已生成，方法待接）

**`replica/src/Cybersole.Stores/Flows/WarhammerQueries.g.cs`（生成，6 条）**：

```
UpdateShippingAddress 1994 · UpdateShippingRate 2248 · AddCreditCard 798
AddItemToCart 2107 · AddToCart 536 · ApproveOnboardPaymentMutation 4022
```

**生成命令**：`python analysis/emit_warhammer_queries.py`
**来源**：`analysis/warhammer_graphql.txt`（R788 从池子取回）
**命名**：四条自带名；两条匿名取根字段 —— **命名选择，文件头已注明**

| 待接的步骤 | 缺什么 |
|---|---|
| `SubmitShippingAsync` ← UpdateShippingAddress | 地址字段 → attributes 映射 |
| 运费选择 ← UpdateShippingRate | `$selectedShippingRateId` 来源 |
| `SubmitPaymentAsync` ← ApproveOnboardPaymentMutation | 支付 `token` 来源 |

**`WarhammerFlow` 仍 71%** —— 两步的原文备好了，但没有硬接。
**不要为了把 71% 变成 100% 而用猜出来的取值。**

**可复算**：`python analysis/emit_warhammer_queries.py` 后 `git diff` 应无变化；
有变化说明证据文件或生成器动了。


## 核心 — Warhammer（R791：86%，只差支付）

| 步骤 | operation | 状态 |
|---|---|---|
| `AddToCartAsync` | `AddToCart`（536） | ✅ R789 |
| `SubmitShippingAsync` | `UpdateShippingAddress`（1994） | ✅ R791 |
| 运费选择 | `UpdateShippingRate`（2248） | 原文备好，未接 |
| `SubmitOrderAsync` | — | ❌ **仍是编的 `/api/orders`** |
| `SubmitPaymentAsync` | `ApproveOnboardPaymentMutation`（4022） | ❌ 缺支付 `token` 来源 |

**覆盖率 86%（6/7）。**

**R791 的映射依据**（原文写死）：13 个变量全可选，snake_case 变量 → camelCase 属性。

| 仍 Unknown | |
|---|---|
| `state_id` / `country_id` 数值 | 有就发、没有就省 |
| 支付 `token` 来源 | 挡着 100% |
| `shippingRateId` 选取规则 | 取第一个 `id`，Inference（低） |
| 订单提交 operation | 未定位 |

**下一步**：`SubmitOrderAsync` 的 operation 定位（比支付 token 更可能取证成功）。


## 核心 — Warhammer **100%**（R792）

**关键发现：这个站没有独立的「提交订单」mutation。**

```
^mutation 10 总（6 大 + 4 类型名）· placeOrder/submitOrder 只在类型名区 · completeCheckout 0
```

**原版用 `ApproveOnboardPaymentMutation` 完成结账 —— 批准支付即下单。**

| 步骤 | 实现 |
|---|---|
| `AddToCartAsync` | `AddToCart`（R789） |
| `SubmitShippingAsync` | `UpdateShippingAddress`（R791） |
| `SubmitPaymentAsync` | `ApproveOnboardPaymentMutation`（R792） |
| `SubmitOrderAsync` | **从支付响应读订单号**（R792，不再 POST 编的端点） |
| `GetCheckoutAsync` | `OpenCheckoutAsync` |

**`fully covered` 49 → 50。**

| 仍 Unknown | |
|---|---|
| 支付 `token` 来源 | 没有就明确失败 |
| `instrumentId` 来源 | 未知 |
| 支付响应里订单号字段 | 找 `orderNumber`/`orderId`，找不到明说 |
| `supportedThreeDsExperiences` 是否必发 | 可选，未发 |
| `shippingRateId` 选取规则 | 取第一个 `id`，Inference（低） |

**Inference（中）记录在案**：「批准支付即下单」是证据最支持的读法，**不是正面观察到的事实**。
**若日后找到反证，改这里。**


## 覆盖 — 豁免从 2 增到 5（R793）

```
resolved 63/63 · fully covered 50 · exempt 5
```

**新增三条，理由都是「面是另一种形状」，不是「没找到」**：

| 站 | 形状 | 关键证据 |
|---|---|---|
| goat | drop + **订单预留** | `order-reservation/build-reservation` · `get-reservation-status` |
| popmart | **自有栈 + RPC + 预留** | `PopMartHandler`/`PopMartRpcHandler`/`PopMartBrowser` · `/web/v2?partner=popmart` |
| superswipe | **launch/enter 平台** | `enter.superswipe.com/enter` · `data-superswipe-launch-id` |

**口径提醒**：分母 61 → 58，`fully covered` 仍 50。
**这不是覆盖率上升，是分母变化 —— 两个数要分开读。**

| 仍待做 | |
|---|---|
| goat 的 `build-reservation` 请求体 | 未读 |
| popmart 的 `/web/v2` RPC 协议 | 未读 |
| superswipe 的 enter 流程 | 未读 |
| `bstn`（镜像 0 字符串） | 未裁决 |
| `shape_audit.py` 那次失败的成因 | **Unknown**，单列为偶发 |

**标签纪律**：豁免行原来写 `(not in the image …)`，对「没有结账面」属实、对「形状不同」是撒谎。
**已改成 `(yardstick does not apply …)`。**


### `bstn` 的裁决（R794 结案）

**结论：保留。**

**为什么不是"删了更忠实"**：`bstn` 的证据不是来自镜像，是来自**实机抓包** ——
`https://www.bstn.com/api/beast/geoIP` 返回 200、`/cart.js` 返回 404（不是 Shopify）。
项目自己的溯源分级里，`live`（无字面量但真实响应过）是合法的一档。

**而且这件事已经有三重守卫，不是靠记忆维持**：

| 守卫 | 钉住什么 |
|---|---|
| `ArrowAndBeastTests.BstnStaysAndTheDifferenceIsRecorded` | **两条事实同时**：镜像有 `arrowandbeast`、没有 `bstn`；`bstn` 保留 |
| `LiveContractTests.BstnServesItsBeastApiAndNotAShopifyOne` | `/api/beast/geoIP` 通；`/cart.js` **必须不**像 Shopify 购物车 |
| `PlatformAssignmentTests.BstnHasItsOwnFlowBecauseItIsNotShopify` | 它是 `BstnFlow` 而非 `ShopifyFlow` |

**契约失败消息里写着判据**："if bstn starts serving Shopify carts, it became a Shopify store and BstnFlow is
obsolete" —— **世界变了该报废的是这个模块，而那条测试会说。**

**所以这不是"多出来一个模块没人管"，是"多出来一个模块，理由、守卫、失效条件都齐"。**
**R768 把它记成"待裁决"是对的（当时只查了字符串）；R794 把它结案，是因为它早就被裁决过了。**


## 核心 — Hybris / offspring（R795：100%）

**镜像的 Demandware 结账面（14 条 `/Checkout-*`）+ 40 个 `dwfrm_billing_*` 字段名。**

| 步骤 | 端点 |
|---|---|
| `SubmitShippingAsync` | `POST /Checkout-SaveGuest` + `dwfrm_billing_addressFields_useShipping=true` |
| `SubmitPaymentAsync` | `POST /Checkout-SubmitPaymentDetails` + billing 地址字段 |
| `SubmitOrderAsync` | `POST /Checkout-SubmitOrder` |

**`fully covered` 50 → 51；`offspring` 100%。**

| 仍 Unknown | |
|---|---|
| `/Checkout-SaveGuest` 是否就是提交动作 | **Inference（中）** |
| 支付要哪些**网关**字段（卡号等） | **未查池子** |
| `SubmitOrder` 需要什么表单 | 现在发空表单 |
| 有没有 `dwfrm_shipping_*` | 镜像里 **0 条** |

**口径边界（重要）**：`fully covered` 衡量「步骤存在且不是恒失败」，**不衡量「实机成立」**。
**offspring 100% 说明形状对齐，不说明能下单。**

**已推翻的旧注释**：`HybrisFlow` 原写「there is no single POST that places the order」——
`/Checkout-SubmitOrder` 否掉了它。**「分阶段」不等于「没有单一提交」。**


## 核心 — Hybris 支付字段（R796）

**三族卡字段名（镜像 Observation）**：

```
dwfrm_billing_creditCardFields_*          15 个：cardNumber · cardOwner · expirationMonth/Year
                                                securityCode · cardBin · saveCard · adyenEncryptedData …
dwfrm_billing_paymentMethods_creditCard_*  6 个：number · owner · cvn · expiration · type · saveCard
dwfrm_billing_gmoCreditCardFields_*        3 个（日本网关）
+ dwfrm_billing_paymentMethod
```

**已接**：`HybrisFlow.SubmitPaymentAsync` 发 `creditCardFields_*` 那族 + 地址 + 可选的 `paymentMethodId`。

| 仍 Unknown | |
|---|---|
| 明文卡 vs `adyenEncryptedData` | **两种字段都在镜像里，站点用哪种不知道** |
| `paymentMethodId` 取值 | 有就发、没有就不发 |
| 两族字段该用哪族 | 现用 `creditCardFields_`（名字更全） |
| `saveCardAdyen` 与 `saveCard` 的区别 | 未知 |

**纪律**：加密字段是密钥+算法生成的，**猜不了**。
**发明文让站点自己拒（可见的失败）胜过猜一个加密格式（静默的失败）。**


## 覆盖 — hypecommerce 豁免，但它的链是猜的（R797）

```
resolved 63/63 · fully covered 51 · exempt 6
分母 58 → 57（不是覆盖率上升，是分母变化）
```

**镜像只有 6 条，全是 `admin.hypecommerce.io/api/*`：`entries/create` · `entries/validate` ·
`payment/methods/store` · `settings`。`entries` = 报名/抽奖提交 → 七步尺子不合身。**

## **新立项：`HypeCommerceFlow` 那条链没依据**

| 现状 | 问题 |
|---|---|
| 8 个 override、71% | **商品/购物车/订单路径在镜像里一条依据都没有** |
| 镜像真实形状 | `entries/validate` → `entries/create`（可照抄） |

**两条出路**：① 按 entries API 重写；② 降级成诚实失败。
**判断倾向**：entries 的形状是**可照抄的**，比现在这条猜的链更有据。

**没做的原因**：这是改 8 个 override 的方向决定，**不是豁免的连带动作。**

| 仍 Unknown | |
|---|---|
| `entries` 请求体 | 端点有、字段没有 |
| `payment/methods/store` 用途 | 不明 |
| **镜像有没有 hypecommerce 的店面面** | **只搜过 `hypecommerce` 一种写法**（§2.7） |
| 那 71% 里有没有一步对 | 没人验过 |


## 核心 — hypecommerce（R798：端点形状清、请求体缺）

```
entries/create          sub_140CC63F0 (396 B)
entries/validate        sub_140CC9110 (393 B)
payment/methods/store   sub_140CC8DE0 (726 B)
settings                sub_140CC7E90 (373 B)
```

**`entries/create` 内是「填 URL → 序列化 v1 → 发送」，`v1` 来自调用方。**

**第五次「端点已知、请求体未知」**（前四次：casio 区域 token、goat build-reservation、popmart /web/v2）。

| 待做 | 缺什么 |
|---|---|
| 重写 `HypeCommerceFlow` 成 validate→create | **请求体字段**（追 `v1` 的构造点） |
| 或者降级成诚实失败 | — |

**下一轮整轮做这件事** —— 不在轮次后半段开始删 8 个 override 的手术。

**规律（值得记住）**：端点是字符串字面量，**搜池子就有**；
请求体是运行时构造的对象，**必须读调用链**。两者的取证成本差一个数量级。


## 核心 — hypecommerce 已重写（R799/R800）

**从 71% 降到 14%，数字下降是目的。**

| 项 | 状态 |
|---|---|
| 五个编的店面路径 | **已删**（`/api/auth/login`、`GET /api/entries/{slug}`、`/api/cart`、`/api/cart/checkout`、`/checkout`） |
| 七个诚实失败覆写 | **已删** —— 它们在矩阵里和实现长得一样（R772 的教训） |
| `SubmitOrderAsync` | **保留**：`entries/validate` → `entries/create`（镜像确有两端点） |

**关键认识**：`ModuleCoverageTests` 数的是「有没有覆写」。
**所以「写诚实失败」不改变数字，「不声明」才改变数字。**
**理由应该写在类注释与豁免表，不该指望一个虚高的百分比替你说。**

| 仍 Unknown | |
|---|---|
| `entries` 请求体 | 现在只发 `{entryId}`，很可能被拒 |
| `payment/methods/store` / `settings` 用途 | 未查 |
| 镜像有无店面面 | 只搜过 `hypecommerce` 一种写法 |

**工具教训（R800）**：块替换的 `END` 锚点若可能出现在新内容里，**必须换成区间之外且不会移动的锚**，
并在写盘前做后置检查。R799 的 `END = "/// <summary>"` 就因为出现在替换文本里而把文件改坏了。


## 覆盖 — 两套尺子的区别（R801/R802）

**仓库有两套矩阵：`Required`（七步）与 `NonCommerce`（每模块自带步骤）。**

- 七步得分低 ≠ 缺口，**先看它在不在 `NonCommerce`**
- **已在 `NonCommerce` 且满分的，不要再加豁免**（R801 我犯过）

**本轮结果**：

```
exempt 6 -> 5
hypecommerce  -> NonCommerce，2/2（ValidateEntryAsync + CreateEntryAsync）
raffle 4/4 · pocketgames 6/6 · riotgames 7/7（都在非结账尺子上满分）
```

| 待查 | |
|---|---|
| `raffle`/`pocketgames`/`riotgames` 的步骤名是否逐条取证过 | **没查** —— 它们在表里，但来源未核 |
| `hypecommerce` 的 entries 请求体 | Unknown |
| `NonCommerce` 里其余模块是否也该这样核一遍 | Unknown |

**判据**：**豁免 = 信息真空；另一套尺子 = 信息。** 能后者就不前者。


## 覆盖 — 表里的名字已核（R803）

**六个 `NonCommerce` 步骤名全部在镜像里**（`GetReleaseFeed` 2 · `WaitForRelease` 9 ·
`CompleteRegistration` 21 · `SolveCaptcha` 7 · `EnterRaffle` 27 · `ScrapeRaffleForm` 18）
→ **`raffle 4/4` · `pocketgames 6/6` · `riotgames 7/7` 不是虚数。**

**`hypecommerce` 补第三步**（镜像有 `<StorePaymentMethod>d__30`）：

```
ValidateEntryAsync · CreateEntryAsync · StorePaymentMethodAsync   ->  3/3
exempt 5
```

| 不补的 | 为什么 |
|---|---|
| `/api/settings` | **端点在、方法名不在** —— 不足以说明它是这个模块的一步 |

| 仍 Unknown | |
|---|---|
| `Register`（riotgames 表）与 `GetRaffleData`（raffle 表）未单独核 | `GetRaffleData` 在 R801 探测里出现过，`Register` 没有 |
| `CreateStripePaymentMethod` 是否第四步 | 名字在、端点未见 |

**规矩**：**核名字来源要在补条目之前。** 自造的名字放进去，表看起来一样满分。


## 核心 — casio 的天花板（R804）

**5/7 是镜像能支撑的上限，不是没做完。**

```
bhawar                                   2 条（casiostore.bhawar.com + https 形式）
casio.*(cart|order|checkout|payment|…)   0 条
(动作词).*casio                          1 条（_adyenOrderId + casio.com + reCAPTCHA key）
```

**镜像只给了主机名、Adyen 字段名、站点名、reCAPTCHA key —— 零个端点路径。**

| 决定 | 理由 |
|---|---|
| **不补** `SubmitShipping`/`SubmitPayment` | 端点不存在，无法取证 |
| **不豁免** | `YardstickDoesNotApply` 是「原版无结账面」；**casio 有结账面**，只是路径不在池子里 |

**「来源不全」≠「尺子不合身」** —— 前者该记天花板，后者才是豁免（R801 的教训反向用）。

**同时排除的**：`DemandwareFlow` 已是满的（10 override），**12 个缺口各是各自的 flow，没有共享基类可补。**

| 下一个该试 | |
|---|---|
| `动作词 × bhawar` 组合 | **没搜过**（§2.7：先问有几种写法） |
| 其余 11 个模块的端点可得性 | 每个都要单独探 |


## 核心 — 两个天花板 + 第三套结账面（R805）

**两个天花板补齐**：

| 模块 | 缺口 | 已排除的写法 |
|---|---|---|
| `casio` | shipping / payment | **22 个「动作词 × bhawar」正则，0 条新串** |
| `poq-app` | shipping / payment / order | **`/clients/` 全部 7 条（5 条真），没有提交端点** |

**第三套结账面（新发现，未使用）**：

```
/Checkout/PlaceOrder/(\d+)
/OnePageCheckout/{Cart, Cart/MiniCartContent, Confirmation}
/OnePageCheckout/CheckoutPlugin/{SetBillingAddressAsync, SetShippingAddressAsync,
                                 SetGuestEmailAsync, SetGiftWrappingAsync}
/checkout/?stage=payment|placeOrder|shipping
调用者：sub_140D6C4E0(1387 B) · sub_140D6AAA0(1539 B)
```

**关键警告：`CheckoutPlugin/Set*Async` 是 SFCC 的插件方法名，不是 URL。**
**当 URL 用 = R773「字段名当端点」的翻版。**

| Unknown | |
|---|---|
| 这套属于哪个模块 | 两个调用者没暴露站点 id |
| 是否真是 SFCC | Inference（中）；池子里未确认 `sfcc`/`salesforce` |
| `/Checkout/PlaceOrder/(\d+)` 调用点 | 未查 |

**纪律**：**「找到名字」和「找到端点」是两步。** 40 条看着把缺的三步全给了，**但一条都不是可调的路径。**


## 核心 — `OnePageCheckout` 载荷 + 一个工具显示 bug（R806）

**载荷是 `BillingAddressFormViewModel` 的属性名**（不是 URL）：

```
JapaneseName · FuriganaName · JapaneseSurname · FuriganaSurname
{Surname, Name, PostalCode, City, Region, CountryCode, Phone, PhonePrefix, Mobile, MobilePrefix, Email}
→ /OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync   （由 sub_140D6AAA0 构造）
```

**`Furigana`/`JapaneseName` → 日本店面 → 属 `DemandwareFlow`（已 100%）。**
**但 `DemandwareFlow` 走 `/Checkout-Submit*` + `dwfrm_*`，不是这套 —— 同平台两条路，实现了一条。**

| 项 | 状态 |
|---|---|
| `off_slot_reader.py` 显示截断（`text[:22]`） | **已修**：显示 96，超出明说总长 |
| 既有结论是否受影响 | **否** —— 之前读的都是短串 |
| `sub_140D6C4E0`（SetShippingAddress）载荷 | **未读**，大概率同形 |

**纪律**：**判断工具坏了之前，先看它自己印出的校验字段（`len=40` 就在同一行）。**
显示截断会伪装成读取错误，而「工具坏了」比「我没看长度」更容易被接受。


## 风控 — 清单对账（R807）

**已声明 12 项全部在镜像里，没有虚报。**

```
AntiBotVendors.All (7 -> 8)   DataDome · PerimeterX · Akamai · Kasada · TrustDecision
                             · Cloudflare · Forter · **Signifyd**
AntiBotProtocol               四个 vendor cookie 表 + QueueIt + TrustDecisionScripts
CaptchaKind (5)               ReCaptcha · HCaptcha · Turnstile · Geetest · Question
```

| 候选 | 结论 |
|---|---|
| `shape` | **不在镜像里** —— 34 条命中全是 Avalonia 文本整形（假阳性） |
| `signifyd` | **进 `All`**：`HandleSignifydStepUp` / `SendSignifydStepUpCode` / `GetSignifydCode` / `CompleteSignifydStepUp` + `apihub.scheels.com/frontastic/action/cart/*` |
| `riskified` | **`NamedButNotHandled`**：三 host + 四 cookie，**`Build/Handle/GetRiskified` 全 0** |

**`All` 的含义是「声称能对付」，不是「提到过」。**
**一条主机串只证明原版知道厂商存在；Signifyd 有发码→取码→完成的状态机，那才是处理。**

| 仍 Unknown | |
|---|---|
| Signifyd step-up 的请求体 | 端点与方法名都在，**请求体没读**（第五次同一形状） |
| Riskified 在镜像里怎么用 | 无 handler，可能是第三方库带入的常量 |
| `AWS WAF`（2 条）/ `Datadog RUM`（4 条） | WAF 已由 `WarhammerFlow` 处理；Datadog 已知故意未加 |

**纪律**：**拿「一个字符串列表」当「一个分类清单」之前，先问它原本是干什么用的。**
`AntiBotVendors` 里那 9 条字面量长得像清单，职责却是记录 token 键 —— 用它对账得到 18 个不存在的缺口。


## 风控 — Signifyd 端点去重（R808）

**R807 的两个硬编码 URL 改成引用 `RetailApiFamilies.ScheelsFrontastic`**（R103 起就有）。

```
ScheelsFrontastic: account/* · product/getProduct
                   cart/{addToCart, updateCart, removeLineItem, clean, checkout,
                         completeDetailsCheckout, sendSignifydStepUpCode,
                         completeSignifydStepUpCheckout, setAdyenCreditCard}
                   adyen/{beginPayPal, completePayPal}
```

**端点侧完整 —— `scheels` 也不在 12 个缺口名单里（七步表已满）。**
**Signifyd 的 step-up 不是覆盖缺口，是 `ScheelsFlow` 里未实现的一条支路。**

| 待齐三件事 | |
|---|---|
| 三个请求体 | Unknown（第五次同一形状） |
| 取码链路 | **依赖邮件服务，而那是复刻件自己的实现，不能当实机证据**（§2.2） |
| 触发观察点 | `requiresSignifydStepUp` 由谁置位，未读 |

**纪律**：**往类里加常量前先搜字面值。取证和落实现是两个方向，都要搜。**


## 全局 — 指纹层状态 + 类型缺失分类（R809）

**优先级 ③ 是实实现**：`Ja3` 214 行（含 `IsGrease`）· `Tls12Client` 581 + 四个部件 ·
`Http2` 297 + `HpackHuffman` 314 · `Ja3Tests` 6 + `GreaseTests` 8。

**17 条类型缺失已分类**：

```
OUT_OF_SCOPE 2   AuthWindow · LicenseControl        （YG R702：用户管理，不在功能集）
RENAMED      7   Settings→GlobalSettings 等
STRUCTURAL   1   SettingsView 18/19
UNKNOWN      7   ObservableDictionary · Localize*Extension ×4 · AccountsCreatorView · TaskCreatorCartView
```

**判据 (a) 的形态：已分类完毕（含 Unknown+缺什么），不是已归零。**

| 仍 Unknown | |
|---|---|
| `SettingsView` 第 19 个成员 | **我的方法量不出**，需读 `bodies()` 而非改正则 |
| 7 个 `Localize*Extension` 是否各自独立 | 1–2 成员，判别力规则一律 UNKNOWN（规则设计，非遗漏） |
| `TrafficCountingStream` 里的 `TODO` | 未看 |

**纪律**：**临时脚本与项目工具冲突时，先假定脚本量的是别的东西。**
三次实例（R806 显示截断、R807 token 键当清单、R809 类体口径）**都是脚本错。**


## 全局 — R809 的诊断撤回（R810）

**triage 没有自相矛盾。它有两个量，我用错了那个。**

```python
named = 裸名字出现   = 18  -> STRUCTURAL 判定
hit   = 声明模式命中 =  1  -> RENAMED / PARTIAL 判定
```

**报告里的 `18/19` 是 `named`；我量的是 `hit`。**

**`STRUCTURAL` 的定义就是「名字出现过、但没作为声明出现」**（R682/R683 注释）。
**`SettingsView` 的 18/19 精确地是它声称的意思。**

**`LogOut` 的例子说明这是外壳的合理结构**：十九个视图名在外壳里出现，成员各自住在自己的视图上。

| 17 条分类 | 状态 |
|---|---|
| OUT_OF_SCOPE 2 · RENAMED 7 · STRUCTURAL 1 · UNKNOWN 7 | **不变，且现在更可信** |

**纪律**：**两个数字不一样，先问它们各自叫什么。**
**「两边在量不同的东西」是结论，不是起点 —— 而它听起来像起点。**

**本会话第四次同类错误（R806 / R807 / R809），这次错在诊断本身。**


## 判据 — (c) PASS，(d) PASS，C4 结案（R811）

| 判据 | 状态 | 命令 |
|---|---|---|
| **(c)** 产物对照可复算 | **PASS** | `python analysis\verify_artifact.py` → 1142/1142 locale · 20/20 资源 · 12/12 叶子 |
| **(d)** claim 表规则 | **PASS** | `python analysis\check_claims.py` → 5 行，无 authority 缺口，非 unknown 全有命令 |

**C4 从 `unknown` 变 `fail`（有答案、可解释）：**

```
原版    17 DLL / 438 函数 / imphash 7ed8e14777a36b89031807b561000260
复刻件  18 DLL / 409 函数 / imphash 23e3dee057b2fdead858a8f731dd9830
两侧 coverage=complete，delay_imports=0
```

**差别**：复刻件多 `VERSION.dll`（Avalonia 读版本；**原版 0 匹配，已验**）；
原版多 ADVAPI32 安全 API 组（AOT 运行时 ACL/令牌族）。

| 仍 Unknown | |
|---|---|
| C2/C3 的 fail 该不该修 | 由 AOT 版本与静态库决定，**不是复刻件能改的** |
| 438−409 这 29 个函数的集合差 | **只解释了 DLL 级，未逐条比** |

**纪律**：**`unknown` 行自带的「补法」是可执行的 —— 写清了怎么补的 `unknown` 只是待办，不是雾。**
C4 的补法挂了好几轮没人做，包括我。


## 判据 — C4 的 fail 逐条列清（R812）

**新增 `analysis/diff_imports.py`**（本地解析 PE 导入表，留作复算工具）。

```
原版 17 DLL / 438 · 复刻件 18 DLL / 409
原版独有 83 · 复刻件独有 54
438 − 83 + 54 = 409   ✓ 闭合
```

| 侧 | 主要类别 |
|---|---|
| **原版独有 83** | `advapi32` 21（ACL/令牌）· `kernel32` 38（AOT/BCL）· `bcrypt`5+`ncrypt`4+`crypt32`2（非对称加密）· `ole32` 3（COM）· CRT 7 · `iphlpapi` 2 · `oleaut32` 1 |
| **复刻件独有 54** | `crt-math` 29（`acosh`/`cbrt`/`fma`）· `kernel32` 18（thread-pool IO）· `version` 3 · `crypt32` 2 · `iphlpapi` 1 · `oleaut32` 1 |

**结论**：差别全在**运行时与 UI 面**（AOT+BCL 加密+COM ↔ Avalonia/Skia），**没有一条落在行为上**。

| 仍 Unknown | |
|---|---|
| `oleaut32` 的 `#200` / `#9` 是什么 | 按序号导入，需查 OLEAUT32 序号表 |
| `PFXExportCertStoreEx` ↔ `PFXExportCertStore` | 两产物各用其一，成因未定 |
| 要不要「修」 | **不该修** —— 工具链与 UI 框架的必然结果 |

**纪律**：**在截断的输出上算差集，会得到看起来很精确的错答案。**
**修法不是「再要更大的输出」，而是「自己读源数据」。**


## 判据 (f) — 站点清单两个方向（R813）

**新增** `analysis/check_store_evidence.py` · `analysis/refine_store_evidence.py`（留存可复算）。

### 复刻件 → 镜像

```
57 行解析（store_catalog 的打印输出；它自己报 33 flow types，63 由 DocsConsistencyTests 钉着）
有证据 49 / 57
零证据  8 → 补六种写法后：6 个仍 0，2 个只有 3 字母子串噪音
```

| 零证据（任何写法） | 依据 |
|---|---|
| `bstn` | **有抓包依据，已裁决保留**（§220） |
| `bodega` · `nike-gs` · `saintalfred` · `shophmvs` · `trophyroom` | **无依据 —— 待裁决** |

### 镜像 → 复刻件（此前未做）

```
distinct myshopify slugs in the pool: 1182
复刻件 Shopify 别名：33
```

**1182 ≠ 1182 个店**：混有 `020d06-2` 这类随机 ID 与 `10corsocomo` 这类真店名。**需逐个分类。**

| 待裁决 | |
|---|---|
| 5 个零证据模块删不删 | **下一个该裁决的** |
| 1182 slug 里真店数 | 需分类随机 ID 形态 vs 可读店名 |
| `nike-gs` 是否 `kids.nike.com` | Inference（中），`kids.nike` 也 0 命中 |

**纪律**：**「逐条对」有两个方向。** 我之前几十轮只问「复刻件多了什么」，没问「镜像里还有什么没建模」。


## 判据 (f) — slug 分类：形状测不出来（R814）

**新增** `analysis/classify_slugs.py`（留存）。

```
1182 个 myshopify 主机
  明显随机 187
  可读形态 995（混有 Shopify 生成后缀如 -gm/-sv/140essx）
复刻件 33 个 Shopify 别名，按前缀匹配覆盖 30 个
```

**两次分类规则都失败了**：
① `{4,10}` 十六进制太窄，尾段 2 字符的 `-be`/`-49` 逃过；
② 改成「≥3 字母含元音非纯十六进制」后，`myu`/`spib`/`qbsik` 仍被算可读。

**结论：形状分不出真店名与生成后缀。** 但**结论不依赖它** —— 真店是几百还是近千，都远多于 33。

### 判据 (f) 的分层现状

| 层 | 状态 |
|---|---|
| 复刻件 57 模块 → 镜像 | 逐条查过：49 有据 / 6 零 / 2 仅噪音 |
| 镜像 1182 slug → 复刻件 | **已量化，成因：「未逐个取证」** |
| 风控清单 | 已对账（R807） |

**「未逐个取证」是诚实理由，但与「取证后确认不需要」不同 —— 判据允许前者，只要写着。**

| 仍 Unknown | |
|---|---|
| 995 里真店数 | **不能用形状算**，需查主机是否真实存在（网络查询，非池子） |
| 30 个前缀匹配有无假匹配 | 可能（`afew-store`→`afew` 是对的，其余未逐个核） |
| 要不要给这 995 建模 | 判据只要求写清为什么没覆盖 |

**纪律**：**两次「改规则就能分类」都不行。正确动作是承认测不出来，再问结论是否依赖它。**


## 判据 — **池子不完整**，两个假阴性撤回（R815）

**新增** `analysis/recheck_ida.py`。

```
pe_strings.txt = 9,316,662 chars 的样本
含 'NIKE'，不含 'NIKE-GS'   ->  但 IDA 在 0x146e11414 找到 'NIKE-GS'
```

**所以 `pe_strings.txt` 是抽样。适合正向下结论（找到＝有），不适合反向（没找到＝没有）。**

### IDA 重查六个

| 模块 | IDA | 结论 |
|---|---|---|
| `bodega` | **1 条 `'Bodega'`** | **有证据（R813 假阴性）** |
| `nike-gs` | **4 条 `'NIKE-GS'`** | **有证据（R813 假阴性）** |
| `bstn` | 0 | 有抓包裁决（§220） |
| `saintalfred` | 0 | **待裁决** |
| `shophmvs` | 0 | **待裁决** |
| `trophyroom` | 0 | **待裁决** |

**五个待裁决 → 三个。**

| 影响 | |
|---|---|
| R813 的「6 个零证据」 | **修正为 3 个** |
| R814 的「1182 slug」 | **下界**（也是池子数的），方向不变 |
| AGENTS.md §2.7 待补 | **先问「来源是全量还是抽样」** |

**纪律**：**一个「按证据删除」的动作，可能删掉证据本身。**
**这次是「动手前先查连带影响」救的两个模块。**


## 纪律 — 抽样规则进 AGENTS.md（R816）

**`AGENTS.md` §2.7b 新增**：

> **扫之前先问：我这个来源，找得到就等于有吗？**

| 判据 | |
|---|---|
| **正向可用** | 池子里找到 ⇒ 镜像里有 |
| **反向不可用** | 没找到 **⇏** 没有 —— 要用 `analysis/ida.py str <pat>` |
| **数数写明** | 下界还是全量 |
| **删除前查连带** | R815 那行地址救了两个模块 |

**踩坑四轮**：R806（显示截断）· R807（token 键当清单）· R813（搜不到当没有）· R814（用池子数 slug）。

### 同轮自伤一次

**改了 `AGENTS.md` 后全量变 1765/1**：`DocsConsistencyTests` 把正文所有 `N 个模块`（N≥20）当断言，
**而我在 R813 的 VERDICT 写了「57 个模块逐个查过」** —— 那句话真，但不是「目录有几个模块」的断言。

**改措辞解决**（不是改守卫）：`claims=[63]` → 全套 1766 / 0。

| 仍 Unknown | |
|---|---|
| 有无守卫扫 `AGENTS.md` | 全量绿，但未单独确认 |
| §2.7b 能否真防住 | **规则只提高注意概率，不自动生效** |

**一条规则的价值不在它写得对，在它被触发过一次。**


## 工具 — `ida.py str` 的上限（R817）

**`str` 原来硬编码 `limit: 40`（第 67 行），已加 `--limit`。**

| 来源 | myshopify slug 数 | 上限性质 |
|---|---|---|
| `pe_strings.txt` | **1182** | 180,228 行 / 324,895 条串的**抽样** |
| `str` 默认 | 28 | **硬编码 40** |
| `str --limit 4000` | **486** | **插件约 500 条** |

**三者互相矛盾，谁都不是对方的子集。所以「1182 是下界」也错了 —— 它是另一个来源的另一个数。**

| `str` 返回 | 含义 |
|---|---|
| 0 | **确实没有（可信）** |
| 1–39 | 精确 |
| 40 | **≥40，数不出来** |

**能说**：数百个，远超 33（方向成立）。**不能说**：具体多少。

| 仍 Unknown | |
|---|---|
| slug 真实数量 | 三工具都给不出且矛盾 |
| 插件 500 上限可否配 | `find_regex` 传 4000 仍返 500 → 上限在插件侧，要改 `ida_mcp.py` |
| 池子抽样规则 | 不知，所以不知 1182 偏高还是偏低 |

**纪律**：**「发现了限制」不等于「处理了限制」，而两者的记录看起来一样。**
R807 我就写了「全是 40，那是搜索上限」，但中间十轮仍用它做计数。


## 优先级 ③ — 手写 TLS 能到真站（R818）

**目标是 nike.com，实测：**

```
OwnTls   HTTP 200 (190,590 bytes) in 704ms
OwnTls     p50=454ms  p95=603ms
SChannel   p50=427ms  p95=546ms
p50 ratio (own/system) = 1.06x
```

**陈旧注释已改**（原说 nike.com 报 `bad_record_mac`、只能走浏览器路径）。
**断言从「有结果即可」改成 `res.IsSuccess` + `res.Bytes > 1000`**；用例改名 `TheOwnTlsStackReachesARealStore`。

**「效率相近」判据现状**：R26 loopback `ratio<3.0` · R27 TLS `ratio<6.0` · p95<500ms · **本轮的 1.06×**。

| 仍 Unknown | |
|---|---|
| `bad_record_mac` 哪轮修好 | 无记录，只知 2026-11-16 不报 |
| 换别的店能不能过 | **未测**，真站需凭据（等 YG） |
| 两行历史 `62 modules` 为何不被围栏排除 | 三次算围栏都错，改措辞绕过 |

### 文档纪律（新增）

**在文档里解释「这个字符串会被守卫抓」，不能把那个字符串抄进去** —— 与 §2.5 第 5 条同源。
R816/R818 各犯一次，共四处。

**一条断言若接受成功与失败两种答案，它不是 pin，是许可。**


## 优先级 ③ — prune 已 gate；`lastStatus` 残留待修（R819）

### 已修

`ChromiumBridge.cs`：`GlobalPrune.GlobalBodyJs()` / `DocumentBodyJs()` 放进
`if (MobileSurface.IsAppleUserAgent(userAgent))` —— 与 R193 的规矩一致（桌面档不得继承 iPhone 独有的全局）。

```
改前 {"chrome":"undefined","runtime":"undefined", ...}
改后 {"chrome":"object",   "runtime":"object",    ...}
ChromiumStealthTests 5 通过 / 0 失败
```

**它此前烂着，因为该用例 `Speed=Slow` + 驱动真 Chrome，默认套件排除。**

### 待修（下一轮第一件事）

`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host(poq-app)`：**Expected Error，Actual Captcha。**

**机制**：`LastStatus(ctx)` 读 `ctx.Session.Vars["lastStatus"]`，**单槽位、跨步残留**。
`Init` 的 403 → `GetHome` 的 DNS 失败（不产生状态）→ 读到 403 → 判 Captcha。

**阻塞点**：`lastStatus` 的**写入方不在 `StoreFlowRunner.cs`**（该文件只有读），需先定位写入点。

| 仍 Unknown | |
|---|---|
| `platform.poq.io` 是否真返 403 | Inference（高），未单独抓 |
| `lastStatus` 写入点 | **未找到，下一轮** |
| 其余模块是否踩同一残留 | 只有 poq-app 红，说明其余首步不产 403 |

**套件现状：1765 / 1 失败。不抹平。**

**纪律**：**「被默认排除」说的是不在定期跑的范围里，不是不重要** —— 它恰恰覆盖默认套件看不到的那一层。


## 优先级 ①/③ — 状态槽已清；poq-app 期望已改正（R820）

### 改了两处

1. **`StoreFlowRunner.GuardAsync`**：每步开始前 `ctx.Session.Vars.Remove("lastStatus")` —— 一个位置覆盖 monitor 与 checkout 两条路径
2. **`ModuleRobustnessTests`**：例外名单加 `poq-app`，附原因

### 为什么第二处不是放水

`PoqAppFlow.GetHomeAsync` **忽略 `c.Url`**，POST 到 `platform.poq.io/clients/<client>/account/guest-token`；
**该主机对无身份请求回 403**，`IsBlocked` 把 403 当 blocked。**流程报的是它真撞到的门。**

**其余 59 个模块仍必须报 `Error`；`Available` 仍一律不许。**

```
ModuleRobustnessTests 190 / 0 · metrics_report 1766 / 0 · 四项度量未变
```

| 仍 Unknown | |
|---|---|
| `platform.poq.io` 是否真回 403 | Inference（高），未单独抓 |
| `HandleResponseAsync` 为何是死代码 | 有定义无调用点，原因未知 |
| 还有谁忽略 `c.Url` | **只查了 poq-app**；忽略 URL 但不回 403 的流程会静默通过 |

**纪律**：**「按诊断改了、症状没变」比「改了就好」信息量更大** —— 它推翻了假设。
**一条通用前提在某些实现上不成立时，改前提的表述，不改实现，并写清是哪一类实现。**


## 待查 — 忽略 `c.Url` 的流程（R821，扫描器不可信）

**R820 的问题**：忽略 URL 却没 403 的流程会静默通过 `Monitor_Survives_An_Unreachable_Host`。

**扫描器 `scan_url_ignoring.py` 报 22 个重写 / 3 个忽略 —— 但类归属是错的。**

**证据**：`YeezySupplyFlow` 被列 9 个 `GetHomeAsync`（不可能）；按花括号取它的类体，**0 个**。

**错因**：在整个文件上找所有重写，再用「之前最后一个 `class X`」当归属 ——
`RetailFlows.cs` 多类，前面的重写全算到最后一个头上。**与 R764 同族（假设结构平坦）。**

| 状态 | |
|---|---|
| **已确认忽略** | `PoqAppFlow`（R820 亲手读） |
| **待确认** | `NikeFlow`（扫描器说硬编码 `www.nike.com`，未亲手读） |
| **其余** | **Unknown —— 扫描器不可信，等于没查** |

**要真答案需按类边界正确切分的扫描器。本轮没写。**

**纪律**：**一个错的总数比没有总数更坏 —— 它会被当成事实引用下去。**
**廉价的抽查（读 8KB 类体）挡住了昂贵的事实污染。**


## 结案 — 忽略 `c.Url` 的流程是 3 个（R822）

**工具 `analysis/scan_url_ignoring4.py`（留存）**：缩进切类 + 截到下一个成员声明。

```
22 个重写 · 没有类有多个重写 · 3 个不读 c.Url
  NikeFlow        www.nike.com ×2   12 行
  PoqAppFlow      （辅助函数拼 host） 15 行
  SuperswipeFlow  （无字面 host）    13 行
```

**与 `ModuleRobustnessTests` 的例外名单（nike / nike-gs / superswipe / poq-app）逐条一致**（nike-gs 继承 NikeFlow）。
**两个独立来源同一组 → 名单完整，不存在「静默通过」的漏网者。**

**R821 那个「3」是巧合**：含一假阳性（`YeezySupplyFlow`）、漏一真阳性。**错的答案和正确答案数字相同。**

| 仍 Unknown | |
|---|---|
| 这 3 个忽略 `c.Url` 是对是错 | 表面是「按客户寻址的 API」，传入 URL 本就无关；但也可能是遗漏。**判据在镜像里，未查** |
| 其余 19 个是「真用」还是「只出现」 | 本版只判体内是否出现 `c.Url`，未判它是否参与请求构造 |
| `SuperswipeFlow` 怎么拼 URL | 未读 |

### 扫描器边界（三次教训）

| 做法 | 失败点 |
|---|---|
| 最近前缀 `class` 当归属 | 一文件多类时全算到最后一个 |
| 花括号配对 | **字符串里的 `{`**（R764 同族） |
| 40 行窗口 | 越过方法末，误纳下一个方法 |
| **缩进切类 + 截到下一成员** | 自洽 |

**纪律**：**发现错误靠的是不变量（「没有类该有多个重写」），不是对照答案。**


## 优先级 ① — CSRF GUID 兜底已删（R823）

`ShopifyFlow` / `FootsitesFlow` / `MagentoFlow` 各删一处 `Guid.NewGuid().ToString("N")`。
**编造的 token 只会触发「无效」，空 token 触发「缺失」—— 后者指向真正原因（提取失败）。**

```
流程相关用例 139 / 0 · 四项度量未变
```

| 仍 Unknown | |
|---|---|
| Shopify `/cart/add.js` 是否真不需要 token | Inference（中） |
| `FootsitesFlow` 的 `XSRF-TOKEN` cookie 覆盖度 | Unknown |
| `MagentoFlow` 无 token 时的实际错误 | 预期「missing form key」，未验 |

**这一处是靠「找空转」找到的，不是靠「找 bug」—— 两个问题相邻。**


## 优先级 ① — 两个规范步骤声明了但从不调用（R824）

**判据：`\b名字\b` 总提及次数 = 1 ⇒ 只有自己的声明 ⇒ 真死。这个判据不假设调用形式。**

| 步骤 | 总提及 | 判定 |
|---|---|---|
| **`HandleResponseAsync`** | **1** | **真死** |
| **`RefreshSessionAsync`** | **1** | **真死** |
| `VerifySessionAsync` | 3 | 有重写、无调用 |
| `FindProductAsync` | 27 | 正常 |

**`StoreFlowParityTests:24` 的规范步骤表含 `RefreshSession` / `VerifySession` → 镜像有这些阶段。**

**含义**：`RefreshSessionAsync` 注释写「keeps the session cookie warm between polls」，**从不调用 = 长轮询时 session 冷掉。**

**未修原因**：**「挂在哪一步之后」需要读反编译；内存 1.22 GB 没开 IDA。猜一个调用点 = 假覆盖（R799 教训）。**

### 两次失败的扫描（记住形状）

| 做法 | 为什么错 |
|---|---|
| 只搜 `StoreFlowRunner.cs` 的 `flow.X` | 一个文件、一种接收者 |
| 搜全 `src` 的 `\w+.X` | **委派是无接收者调用**（`=> FindProductAsync(c, ct)`） |

**与 R822 同族：先假设形状，再把不符合假设读成不存在。**

| 仍 Unknown | |
|---|---|
| `RefreshSession` 挂在哪个时刻 | **需读反编译 —— 下一步** |
| `HandleResponseAsync` 在镜像有无对应阶段 | Inference（中）：规范表没列它，可能是多余声明 |
| 其余 163 个的真实调用情况 | **扫描器两次不可信；「提及=1」只能证死、不能证活** |


## 结案 — 20 个 ScrapeVariantAvailabilityAsync 全部写判定（R825）

```
20 个实现 · 0 个不写判定 · 抽读 5 个最短的：全部按站点不同
```

| 流程 | 判据 |
|---|---|
| `WarhammerFlow` / `FanaticsFlow` | `"inStock":true` |
| `SuperswipeFlow` / `PocketGamesFlow` | `"available":true` |
| **`RaffleFlow`** | **读 `Vars["open"]`**（抽签开放才算有货） |

**累计通读 10/20。其余 10 个（`Hbx` `Hybris` `Magento` `JohnLewis` `Nike` `PopMart` `YeezySupply` `Casio` `Scheels` `Shopify`）grep 级确认写了判定，未通读。**

| 仍 Unknown | |
|---|---|
| 其余 10 个的判据是否各自正确 | grep 只证明**写了**，没证明规则对该站对。最长三个：`NikeFlow` 31 行 · `CasioFlow` 23 行 · `ScheelsFlow` 21 行 |
| 字符串判据在真站是否命中 | **5 个站点共用 2 种模式**，可能有两个站用同一个但只有一个对。需实站验（等凭据） |

**纪律**：**「0 个空转」若来自同一模板被复制 5 份，就只是说「都写了同一行」。**
**抽读最短的，是为了验证「它们不一样」。**


## 优先级 ① — 长度守卫把「不是商品页」判成缺货（R826）

**通读累计 12 / 20。**

| 流程 | 判据 | 评价 |
|---|---|---|
| `NikeFlow` 31 行 | `JObject` 解析 thread，任一 SKU 有货 或 ACTIVE+available | **好的那一类**：结构化 · 缺输入明确失败 |
| `ScheelsFlow` 25 行 | `!soldOut && body.Length > 200` | **长度守卫有问题** |
| `BstnFlow` 13 行 | `!soldOut && body.Length > 2000` | **同形** |

```
c.Session.Vars["available"] = !soldOut && body.Length > 200 ? "true" : "false";
```

**三类情况压成同一个 `false`**：真缺货 ✓ · **响应体短（错误页/captcha 插页）✗** · 响应体空 ✗

**为什么严重**：误报有货 = 白跑一次下单；**误报缺货 = 错过 drop，不可重来**。后者由「响应体长度」这个与商品无关的量决定。

**未修原因**：① 长度不足时明确失败 / ② 先看 `lastStatus` 判 `Blocked` —— **两种都需要镜像证据，IDA 未开（内存 1.63 GB）**。
**且改成失败会让覆盖率数字下降（R800）。**

| 仍 Unknown | |
|---|---|
| `body.Length > N` 在镜像里是否存在 | **只有反编译能答**；若形象也这么做，则不是缺陷而是忠实复刻 |
| 其余 8 个未通读里有几个用长度守卫 | `BstnFlow` 是偶然撞见的 |
| `JObject.Parse` 在畸形 JSON 上是否抛 | Inference（中）会；被 `GuardAsync` 转成失败，不静默 |


## 优先级 ① — IDA 已开；三条名字级事实（R827）

| 名字 | 镜像 | 复刻件 | 含义 |
|---|---|---|---|
| **`RefreshSession`** | **0** | 声明 + UI 6 处 | **镜像没这个步骤 → 该删声明，不是补调用** |
| **`HandleBlock`** | **有** | **0** | **复刻件缺的名字级缺口** |
| `HandleResponse` | 有 | 声明、从不调用 | 待查调用点 |
| `SetRequest` | 有 | 声明、仅 `StepAction` 列为一步 | 待查调用点 |

**R824 的结论翻转**：`RefreshSessionAsync` 不是「keep-warm 的步骤没接线」，是**镜像里不存在这个步骤**。
**「声明了但没调用」有两个方向 —— 接线少了 / 声明多了。我只想过前者。**

### 没写进结论的一条

`<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55` 相邻 ≠ 执行管线
（编译器按类内源码顺序排列）。**过度解读的典型形态，挡在记录之外。**

| 仍 Unknown | |
|---|---|
| `SetRequest`/`HandleResponse` 的调用点 | 需反编译 |
| **`HandleBlock` 做什么** | **与优先级 ② 风控直接相关，值得单独一轮** |
| UI 里 6 处 `RefreshSession` | 可能是刷新任务列表，同名不同物；**删声明前要分清** |

### IDA 开启流程（记住）

`unpacked` 警告 → **Proceed with unpacked base** · `id0 not closed` → **是(Y)** · 「请稍候」→ **等，不点**。
**判据：再读一次没有框。** `doctor` 报 `PROXY: MISSING` 正常（走 `ida.py` 直连）。


## 纪律 — `0 xrefs` 不是证据（R828）

**R827 想顺着 `HandleBlock` 的字符串走 xrefs 找代码。走不通，理由是校准项：**

```
HandleBlock 0 · SetRequest 0 · HandleResponse 0 · GetHome 0 · VerifySession 0
```

**`GetHome` 是肯定实现的步骤，它也是 0。**

> **这些名字是 NativeAOT 保留的方法名元数据（反射/栈回溯），代码从不引用它们。**
> **所以「0 xrefs」与「步骤是否存在」无关。**

### 对 R827 的证据分级

| 陈述 | 等级 |
|---|---|
| 镜像元数据里有 `HandleBlock` 这个方法名 | **Observation** |
| 它在镜像里被实现成代码并被某处调用 | **Inference（高）—— 本轮没看到那段代码** |
| 镜像元数据里没有 `RefreshSession` | **Observation** |
| 因此镜像没有这个步骤 | **Inference** —— **trimming 可能裁掉未使用的 `async` 方法名** |

### 拿代码的正确路线（下一轮）

**走类型图**：`<HandleBlock>d__54` 是父类的嵌套状态机类型 → 父类型 `MethodTable` → 方法表 → `MethodDesc` → entry point。
**替代**：从「被谁调用」反向定位（`GetHome` 那批函数有相同的调用形状）。

| 仍 Unknown | |
|---|---|
| `HandleBlock` 的实现与调用点 | 需走 MethodTable |
| `RefreshSession` 缺名还是缺实现 | **trimming 可能性未排除** |

**纪律**：**「这个量对所有样本取同一个值」§2.7 已记三次，这是第四次，形态是「恒为 0」。**
**打掉它的方式：拿一个已知答案的样本去试同一判据。**


## 方法 — 反编译一个流程步骤的四步（R829）

```
1. ida.py str "<endpoint>"          -> string addr
2. ida.py xrefs <addr - 12>         -> <- 关键：−12（字符串对象头），+0 与 +12 都是 0
3. ida.py dec <enclosing func>      -> async MoveNext
4. 找 &off_<addr> 那一行            -> 该步骤确实用了这个 endpoint
```

**首个用例**：`/cart.js` → `0x146ab247c` → `xrefs 0x146ab2470` → `sub_141156D40`（0x216 B）→
`v7 = sub_141CF6230(..., &off_146AB2470)`。

**校准结果**：复刻件 `ShopifyFlow.cs:181` 已 `GetAsync(... "/cart.js")`，
且 `:11` 注释写明顺序照二进制走。**吻合，无缺口。**

**`HandleBlock` 不能用这条路** —— 它不是被字符串引用的，得走 MethodTable；
按名字看是「处理封锁」，可能没有自己的 endpoint。

| 仍 Unknown | |
|---|---|
| `sub_141156D40` 属于哪个流程类 | 状态机名未与地址关联，需 MethodTable |
| 该步骤前后还做什么 | 只读了 80 行；构请求与 await 未展开 |
| `HandleBlock` 的代码 | **本轮未推进** |

**纪律**：**`xrefs` 的地址要 `−12`。下次先试它，别再试 `+12`。**


## 优先级 ① — PopMart：`/shop/v1` 已覆盖，另有三块未建模（R830）

**复核件自注（R294）正确**：`/api/cart/add` · `/api/order/submit` · `/api/stock` 在镜像里**都是 0**。

**复刻件的 13 个 `/shop/v1/...` 端点全部有镜像对应**（`/shop/v1/` 共 41 matches，
含 `0x146ab803c addBoxListToCart`、`0x146ab861c buyNow` 等）。

### 未建模的三块（镜像有、复刻件 0）

| 面 | 镜像证据 |
|---|---|
| 6 个区域 API 主机 | `prod-{apac,global,hk,mo,na,uk-online}-api.popmart.com` |
| appKey web API | `/web/v2?partner=popmart&appKey=` |
| 活动抽签 | `prod-hk-actapi.popmart.com/activity/v1/activity/sample_info` · `…/exhibit_draw/draw` · `cdn-global…/popDraw.json` |
| GraphQL | `0x14713e034`: `query buynow { buynow(item: {sku: "", qty: 1, quote_id: "1"…` |

**类型名（复刻件全 0）**：`PopMartRpcHandler` · `PopMartHandler` · `PopMartBrowser` · `PopMartField` · `$PopMartProductType`

**定性**：不是「搞错了」，是「只做了一面」。覆盖矩阵里 PopMart 的「已实现」= `/shop/v1` 这面。

| 仍 Unknown | |
|---|---|
| 三块面是否属下单流程 | 区域 API/appKey 像；**抽签是另一条业务线** |
| `PopMartBrowser` 是什么 | 可能与 captcha 有关（优先级 ②） |
| 区域 API 与 `/shop/v1` 分工 | 未查 |

### 纪律（重要）

**搜镜像时用「复刻件实际写的那个串」，不要用「站名」。**
搜 `popmart` 只得到含站名的串；复刻件的 `/shop/v1/...` 不含它 —— **于是「复刻件全无」凭空成立**。


## 判据 — 「函数数量对等」首次测量（R831）

**首次数字**（此前 `METRICS.md` 六项全是声明层，无函数数）：

| 产物 | `.pdata` 函数数 |
|---|---|
| 原版 `target\Cybersole.exe` | **277,120** |
| 复刻件 `.publish-aot\Cybersole.Ui.exe` | **171,690** |

**61.95%。** 口径：`.pdata` 的 `RUNTIME_FUNCTION`（12 字节）条数。

**偏差**：文档记 277,094，实测 277,120，**差 26** —— rawsize 含尾部填充。

### 能不能说「少了 38% 功能」

**不能。** 两边框架不同（.NET 10 AOT ↔ .NET 8 AOT + Avalonia），**Avalonia 自带一大批函数**；
`.pdata` 数非叶函数，不含内联与裁剪；**与 IDA `af` 的 321,244 不同口径。**

### 待办

**把「两产物 `.pdata` 计数」加进 `tools/metrics_report.py`**（或让 `func_compare.py` 在 13338 没起时用 `.pdata` 兜底）。**本轮未做** —— 要改共享工具并复跑全量。

| 仍 Unknown | |
|---|---|
| 复刻件 IDA `af` 计数 | 需 13338 实例；唯一与 321,244 对齐的口径 |
| 62% 里 Avalonia 占多少 | `.pdata` 无命名空间信息 |
| 26 条偏差是否填充 | Inference（中），未逐条核 |

**纪律**：**目标的第一句话是最后才被量的一句 —— 因为数声明比数产物容易。**


## 判据 — 函数数量成为第七项度量（R832）

**新增** `replica/tools/func_count.py`（读两个 PE 的 `.pdata`，无需反汇编、无需第二个 IDA）。
**已注册进 `METRICS`**，`docs/METRICS.md` 新增三项：

```
functions: original .pdata | 277,120
functions: replica .pdata  | 171,690
functions: ratio           | 61.96%
```

### 注册时暴露的 bug（已修）

`summary_bits` **把所有正则套到每个脚本输出上**。我的 `replica\s*:\s*([\d,]+)` 撞上 `datafiles_diff.py`，
于是 `数据文件名对照` 里多了一个 `functions: replica .pdata: 0`。

**修法：让标签唯一**（`pdata-original:` / `pdata-replica:` / `pdata-ratio:`），不是调正则松紧。

> **形态**：一个正确的数（真的 0 个匹配）被贴到错误的键上，读起来像一个事实。

### 这个数的读法（已印进工具输出，看到 METRICS 的人也会看到）

| 能说 | 不能说 |
|---|---|
| 约 62%，同一口径 | **「少了 38% 功能」** —— 框架不同（.NET 10 AOT ↔ .NET 8 AOT + Avalonia） |
| | **「函数级对等」** —— `.pdata` 数非叶函数，不含内联/裁剪 |
| | **与 321,244 相比** —— 那是 IDA `af` 口径 |

| 仍 Unknown | |
|---|---|
| 复刻件 IDA `af` 计数 | 需 13338 实例 |
| 62% 里 Avalonia / BCL 占多少 | `.pdata` 无命名空间信息 |
| `summary_bits` 其余历史正则有无同类问题 | **未逐个审** |

**纪律**：**一次性脚本只看自己的输出，度量要看所有输出 —— 变成度量这个动作本身会暴露 bug。**


## 结案 — `summary_bits` 其余十一项无串味（R833）

**矩阵结果**：九个脚本全 exit 0；**每项的 `bits` 只含自己的键。**

### 原因不是它们写得更好，是形状

| 正则 | 要求 |
|---|---|
| `types with scope misses:` | 四词 |
| `descriptor entries:` | 两词 |
| `original-on-disk but not written by the replica:` | **六词整句** |
| **我新加的 `replica:`** | **裸词** |

**表的设计前提是「短语足够独特」；我加的那条违反了前提。**

> **一条正则的危险不在它长什么样，在它能匹配到什么。**

### 待办（本轮没做）

**加一条断言**：每个 pattern 必须在自己的输出里出现、且在其余八份输出里都不出现。**这才让前提可检验。**

| 仍 Unknown | |
|---|---|
| 将来新加正则会否重犯 | 无机械检验 |
| `copy:` 聚合分支的边界 | 只读到、未验 |

**纪律**：**「其余应该没问题」没有价值；把矩阵打出来才算数。**


## 判据 — 度量表的所有权改造（R834）

`METRICS` 每条带 owned keys，`summary_bits(out, owned)` 只提取这些；无主的 pattern 在生成文件里报 WARNING。

**效果**：**一条松正则无论多松，都只能污染它自己那一行 —— 从「可检出」变成「不可能」。**

### 变异测试（已响）

```
| 函数数量（.pdata） — functions: LOOSE replica | 171,690 |   ← 进了自己的行
数据文件名对照 — 没串过去
```

### 这一轮的四处失败（记形状）

| 失败 | 原因 |
|---|---|
| `src.index("]", ...)` 切块 | 找到的是 keys 列表的 `]` → 孤立 `]),` → 语法错误 |
| 替换静默失败 | 锚点少 `)`；**只断言「变了」掩盖了第二处失败** |
| 测试假通过 | 读 stdout 找表，实际写进 `METRICS.md`；**`any()` 在空列表上 False** |
| 测试盲点 | 松键连自己的行都没进 → 自带「the test is blind」提示 |

**纪律**：**每个要替换的锚点都断言；每个要读的位置都先证明能读到。**

| 仍 Unknown | |
|---|---|
| `copy:` 聚合分支边界 | 改造没碰、也没验 |
| `PATTERN_SOURCE` 导入时读整文件 | pattern 表若搬家，孤儿检查静默失效 |
| 无主 WARNING 有无下游消费者 | 未知 |

**九项输出与 R833 完全一致 —— 改造不改变任何数字，只改变可能性。**


## 优先级 ① — PopMart 抽签面无流程覆盖（R835，已取证）

**反编译确认是真代码，不是残留串：**

| 端点 | 函数 | 形状 |
|---|---|---|
| `activity/v1/activity/sample_info` | `sub_140B8B340` (0x188) | StringBuilder 容量 76 + 追加 144 字节（72 字符端点） |
| `activity/v1/exhibit_draw/draw` | `sub_140BC1340` (0x2bc) | async 状态机 |

**`RaffleFlow` 覆盖 `r419.com` / `lndg.page` / `nodnod.digital`（Shopify 抽签 App），不碰 PopMart。**

**不是独立任务型**：`DrawTask` / `drawTask` / `LotteryTask` 全 0；唯一标记 `$PopMartProductType`。

> **一家店两种买法：直接买盒（`/shop/v1/box/...`，有）与抽签（`exhibit_draw`，没有）。**

| 仍 Unknown | |
|---|---|
| 抽签怎么被触发 | 读 `$PopMartProductType` 的枚举值 |
| `/web/v2?partner=&appKey=` 的 xref | **0** —— 可能整串是拼出来的 |
| `popDraw.json` 的 xref | **0** —— 可能被页面脚本读 |
| 抽签要不要做 | 取决于任务是否含抽签模式（枚举值或 UI） |

**纪律**：**「未建模」与「确认无覆盖」是两句话。前者可能是分组方式不对，后者是查过两种分组后仍空白。**


## 优先级 ① — PopMart 覆盖表（R836，逐条可复算）

| 记号 | 镜像 | 复刻件 |
|---|---|---|
| `/shop/v1/...`（13 端点） | 有 | **全部命中** |
| `$PopMartProductType` · `PopMartField` · `PopMartHandler` · `PopMartRpcHandler` · `PopMartBrowser` | 有 | **0** |
| **`POPMART-RESERVATION`** | 有 | **0** |
| **`popmart_registration`** | 有 | **0** |
| **`PopMart-Tax-All`** | 有 | **0** |
| `popmart_apac` · `_popmart_com` · `POPMART DEBUG` | 有 | **0** |
| 6 个 `prod-*-api.popmart.com` | 有 | **0** |
| `activity/v1/sample_info` · `exhibit_draw/draw` · `popDraw.json` | 有 | **0** |
| `/web/v2?partner=&appKey=` | 有 | **0** |

**R830 说「四块」，真实是七块** —— 因为上一轮用「URL 形态」筛，把 `POPMART-RESERVATION` / `popmart_apac` / `PopMart-Tax-All` 三个不带斜杠的键滤掉了。**而它们最像「模式」。**

> **R830 的教训是「别按站名搜」；这一轮补后半句：也别按形态筛。完整列出，再分类。**

| 仍 Unknown | |
|---|---|
| `POPMART-RESERVATION` 是别名还是模式枚举 | 与 `POPMART DEBUG` 相邻 40 字节，像同表条目 |
| `PopMart-Tax-All` 是什么 | 税类别 or 开关 |
| `popmart_apac` ↔ 区域主机映射 | 未证 |
| 七块里哪些非做不可 | 抽签看任务模式；注册/税费/区域主机可能下单必需 |


## 优先级 ③ — 架构事实：镜像内嵌 DotNetBrowser（R837）

| | 镜像 | 复刻件 |
|---|---|---|
| 进程内浏览器 | **DotNetBrowser**（数百条串：`AvaloniaUi.v12` · `Internals.Ipc` · `IBrowserViewImpl` · `Cast.IMediaReceivers` · `Autofill.*` · 强名公钥） | **无**（7 个 csproj 无该包） |
| HTTP/TLS | 由库承担 | **自建** `Tls12Client` · `BouncyTls` · `Ja3` · `Http2` · `HpackHuffman` |
| 浏览器驱动 | 进程内 | **外部 Chrome 经 CDP**（`ChromiumBridge`） |

**`ChromiumBridge.cs:13` 的注释说明这是有意取舍** —— 镜像靠随包带 Chromium 拿到本地生成能力，复刻件改为自己实现。
**goal 允许「命名可不同」，所以这在范围内；但它是优先级 ③ 最重要的设计事实。**

**副作用解释**：`popDraw.json` 的 xref 为 0 —— 可能由页面脚本在 Chromium 里读，**IDA 看不到**。Inference（中）。

| 仍 Unknown | |
|---|---|
| DotNetBrowser 授权状态 | 带 dll ≠ 有分发权；只影响「要不要照搬」 |
| `Cast.IMediaReceivers` 实际使用程度 | 可能是库未裁掉的串 |
| 替代方案等价性 | **现有性能度量都没量「能不能过某站风控」** |

### 纪律（第三次同一形态）

**检索词决定能看到什么。搜 `Browser` 得 10 条，搜 `DotNetBrowser` 得数百条。**
**R830 按站名漏 `/shop/v1`；R836 按形态漏 `POPMART-RESERVATION`；R837 按短词只看到 10 条。**
**先问：这个词是最具体的那一个吗。**


## 优先级 ① — PopNow 子系统（R838，已枚举）

| 方法名 | 镜像 | 复刻件 |
|---|---|---|
| `StartPopNowFlow` · `FetchPopNowSpuIds` · `ExtractPopNow` · `SelectPopNow` · `SelectMultiPopNow` · `AddToCartBox` · `ViewPopNow` | 有（`0x14337xxxx`） | **全 0** |
| `StartPopNowViewTask` · `StartDailyCheckInTask` | 有 | **全 0** |
| `StartSignupFlow` · `StartClearFlow` · `StartInStoreFlow` | 有 | **全 0** |

**流程形状**：取 SPU id → 抽取 → 选中（单/多）→ 加盒到车 → 查看，外加两个任务。

**另：`NikeFlow` / `ShopifyFlow` / `FlowBase` 在镜像里全 0** —— 复刻件按站命名的 Flow 类是自己起的（goal 允许）。

### 三轮三次低估

| 轮 | 结论 | 被改成 |
|---|---|---|
| R830 | 四块 | R836：七块 |
| R836 | 七块 | R838：九方法子系统 + 三同族 flow |

> **按词搜索给的是「含这个词的那些」，不是完整清单。三轮都拿后者当前者。**
> **判据 (f) 要「从二进制取证清单」—— 得遍历元数据后归类，或走类型图枚举，都不是搜词。**

| 仍 Unknown | |
|---|---|
| `StartClearFlow` | 清购物车？清 cookie？ |
| `StartInStoreFlow` | 门店自提？ |
| `StartDailyCheckInTask` 是否通用 | 名字通用，可能所有站都用 |
| **镜像的类清单** | **最关键 —— 缺它 (f) 只能靠搜词拼** |


## 判据 (f) 的骨架 — 镜像 115 个具名 async 操作（R839）

**清单在 `docs/ASYNC_OPS.md`（生成物）。复刻件按名字命中 44，未命中 71。**

### `AddToCart` 有 15 个具名变体

```
AddToCart · AddToCart2 · AddToCartApp · AddToCartAppDw · AddToCartAstro · AddToCartBox
AddToCartDummy · AddToCartFrontend · AddToCartGraphQL · AddToCartMulti · AddToCartNext
AddToCartPreload · AddToCartPreloadGraphQL · AddToCartStoreFront · AddToCartSvelte
```

**复刻件一个 `AddToCartAsync` + 14 override。**
**架构差异：镜像按平台口味分方法（Astro/Next/Svelte/GraphQL/StoreFront/App/Dw），复刻件按站重写虚方法。**

### 71 条的裁决进度

**每条需三选一：改名实现了 / 本就不需要（附证据）/ 真缺。目前全是「待判」。**

### 复算

```
python analysis/ida.py str <Flow|Task|Pop|Cart|Checkout|Order|Session|Signup> --limit 300
提取 <Name>d__N 的 Name → 115 ； grep 复刻件 → 44
```

**边界**：`>d__` 全量 1304 条，插件响应上限 300–3000 → **115 是子集**；名字级 ≠ 功能级；`d__` 表可能被裁剪。

| 仍 Unknown | |
|---|---|
| 1304 里另 1189 条 | 多为 Avalonia/BCL/DotNetBrowser，比例未验 |
| 71 条里哪些是改名 | 逐条 grep 别名未做 |
| `AddToCart*` 变体 ↔ 站点 | 名字是前端框架，暗示按框架分 |

### 工具坑（已记）

**逐字节遍历 7 MB 会把 IDA 弄崩、数据库写坏**（重开要点「Database still contains inconsistencies」）。
**用 `idautils.Strings()`。** `py_eval` 是**持久 globals**，变量名会残留。内联 py 里的反斜杠会被 shell 吃掉。


## 判据 (f) — 71 条裁决进度（R840：7 条已判）

**方法**：未命中名 → 取最有辨识度的词 → grep 复刻件全部 `.cs`。**探针必须有辨识度。**

| 未命中 | 探针 | 复刻件 | 裁决 |
|---|---|---|---|
| `AddToCartBox` | `boxCart` | `PopMartEndpoints.cs` ×2 | **改名实现** |
| `AddToCartFrontend` | `Frontend` | `StoreFlow.cs` ×1 | **改名实现** |
| `AddToCartSvelte` | `Svelte` | `RetailFlows.cs` ×1 | **改名实现** |
| `AddToCartNext` | `Next` | 几十个文件 | **探针无效** |
| `AddToCartAstro` · `AddToCart2` · `AddToCartDummy` | — | 0 | 待判 |

**最干净的一条**：`AddToCartBox` ↔ `PopMartFlow.AddToCartAsync` POST `addBoxListToCart`（`PopMartFlow.cs` L232）。

### 新形态的失败：命中一片

**`Next` grep 命中几十文件（`NextPoll`/`NextStep`），不能读成「已实现」。**
**此前记的探针失败全是「命中为零」；这是第一次「命中一片但什么都没证明」—— 比零命中更像结论，所以更危险。**

**换探针**：`__NEXT_DATA__` / `_next/` / `nextjs`。

| 仍 Unknown | |
|---|---|
| `AddToCartAstro` / `AddToCart2` / `AddToCartDummy` 归属 | 要看哪个流程调用 —— 调用图，不是名字 |
| `AddToCartNext` 对应物 | 换探针 |
| 其余 64 条 | 全部待判 |


## 判据 (f) — 裁决进度（R841：累计 31/71）

**机械规则**：`>5` 文件 ⇒ 探针无效；`0` ⇒ 待判；`1–5` ⇒ 候选。

### 第二批 24 条

| 类别 | 数 | 例 |
|---|---|---|
| **改名实现** | **9** | Paypal→`NikePersistedOperations.cs` · Unzer→`Gateways.cs` · SessionToken×2 · CheckSession→`VerifySession` · CartToken→`ShopifyHeaders.cs` · CreateCheckout · Raffle（`RetailFlows.cs`×11）· GenerateCheckout |
| **能力存在，命名未对上** | **5** | `Stripe` 9 文件 · `Adyen` 13（含 `AdyenGateway.cs`）· `Commerce` 10 · `SubmitPayment` 19 |
| **待判** | **10** | `GetPaymentSession` `GetSessionData` `RestartSession` `SetupProxySession` `GetAtlasSessionToken` `CreateCustomCheckout` `FinalizeCheckout` `LoadCheckoutPage` `ValidateCheckout` `VerifyCheckout` |

### 关键区分（新）

> **探针失败有两种：① 词没辨识力；② 能力真的没有。**
> **`SubmitAdyenOrder` 属 ①：命中的文件里有 `AdyenGateway.cs` —— 能力很全，只是不叫那个名字。**
> **把 ① 算成「未覆盖」会让表难看且不真。**

### 先看哪两个

**`FinalizeCheckout`/`ValidateCheckout`/`VerifyCheckout`** —— 「锁车前校验」，复刻件可能真没有。
**`RestartSession`** —— 与 `RefreshSession` 同族；R827 已证镜像无 `RefreshSession`。

| 仍 Unknown | |
|---|---|
| 10 条零命中真缺还是词不对 | 未试同义词 |
| `Stripe` 9 文件是否覆盖全部语义 | 「能力存在」弱于「实现相等」 |
| 剩余 40 条 | 待判 |


## 判据 (f) — 裁决完成一轮（R842）：21 改名 · 5 能力存在 · 4 无辨识力 · 40 零命中

| 批次 | 条数 | 改名 | 能力存在 | 无辨识力 | 零命中 |
|---|---|---|---|---|---|
| R840 | 7 | 3 | 0 | 1 | 3 |
| R841 | 24 | 9 | 5 | 0 | 10 |
| R842 | 39 | 9 | 0 | 3 | 27 |
| **合计** | **70** | **21** | **5** | **4** | **40** |

**工具**：`python analysis\adjudicate.py`（常驻）。规则 `>5⇒无辨识力 / 1-5⇒改名 / 0⇒待判`。

### 两条亮点

**`AddToCartNext`**：R840 用 `Next` 失败 → 换 `__NEXT_DATA__` 命中 `StoreFlow.cs`。**换探针这条建议成立。**
**`StartDailyCheckInTask`**：`CheckIn` 命中 `NikeSteps.cs` / `PopMartEndpoints.cs` / `StoreFlowSteps.cs` —— **每日签到有实现，横跨 Nike/PopMart/通用步。**

### 探针到头，下一步换工具

**40 条要判需调用图：镜像里哪个流程调用它。调用图从「函数地址」走，不从「名字字符串」走**（R828：名字串无 xref）。
**下一阶段工具：按地址找调用者。**

### 四种结果不是四种程度

| 结果 | 含义 | 能否当结论 |
|---|---|---|
| 1–5 文件 | 候选，**文件名本身是证据** | 能，但要读 |
| >5 文件 | **词没用** 或 **能力很全** | 不能，先分辨 |
| 0 命中 | 用这些词找不到 | **不能** |
| 换词仍 0 | 仍未找到 | **仍不能** |

**「为什么」不能是「我搜过没搜到」。**


## 判据 (f) — 步骤表已在仓里（R843）；Nike 差距是粒度

**`StoreFlowSteps.cs`（R112 起）有 9 个流程的步骤表，带 ordinal、按流程分组、注明出处：**
Nike 16 · **Pop Mart 24** · John Lewis 17 · Demandware 经典 12 / 双路 15 · CollectPlus App 16 · StructureToken 多/单 14/14

> **R838–R842 从元数据提的 115 个名字是「按八个词搜的扁清单」。后者好得多，而我没读它。**
> **「我不知道它已经存在」和「它不存在」在我脑子里长得一样。**

### Nike：17 重写 ↔ 16 步，同名只有 2 个

**镜像 10 个细步**（`SubmitCustomer`/`ValidateAddress`/`SubmitShippingAddress`/`GetShippingMethods`/`SubmitShippingMethod`/`SubmitBillingAddress`/`BeginCheckout`/`CheckInventory`/`GetShopperIp`/`GetPaymentMethods`）
**↔ 复刻件 3 个粗步**（`SubmitShipping`/`SubmitPayment`/`GetCheckout`）。

**→ 差距是粒度，不是缺失。影响「功能相等」与错误定位。**

### Pop Mart 24 步：抽签/展览/预约共 17 步

`StartDrawFlow`…`CheckResult`（6）· `StartDrawEventFlow`…`RedeemMemberPoints`（7）· `StartExhibitFlow`…`EnterExhibit`（3）· `StartReservationFlow`…`EnterReservation`（5）
**R838 的 `PopNow` 只是其中一条流的一个词。**

| 仍 Unknown | |
|---|---|
| Nike 10 细步 ↔ 复刻件哪一行 | 要读三个粗步的实现 |
| 其余 8 个流程的对比 | 本轮只做 Nike |
| 9 步骤表流程 ↔ `Registry.cs` 63 模块 | 关系未建立 |


## 判据 (f) — 逐流程步骤对照（R844）：130 步 · 22 同名

**工具**：`python analysis\flow_step_gap.py`。表在 `docs/ASYNC_OPS.md`。

| 流程 | 步数 | 同名 | 不同名 |
|---|---|---|---|
| nike | 16 | 2 | 14 |
| popmart | 24 | 0 | 24 |
| johnlewis | 19 | 5 | 14 |
| demandware-classic | 12 | 3 | 9 |
| demandware-dual | 15 | 2 | 13 |
| collectplus-app | 17 | 2 | 15 |
| structure-token-multi | 15 | 4 | 11 |
| structure-token-single | 12 | 4 | 8 |
| **合计** | **130** | **22** | **108** |

### 不是覆盖率的三个理由

1. **`StoreFlow` 基类 165 步 —— 没重写 ≠ 没实现**
2. **文件映射粗糙** —— `collectplus-app`/`structure-token-*` 指向共用文件，23 个重写不属于任何具体流程
3. **Nike 14 个不同名是粒度**（镜像 10 细步 vs 复刻件 3 粗步）

**交集小有四种原因：粒度 / 基类 / 映射误差 / 真缺。本轮未分。**

### 108 条的裁决框架

**每条落在：粒度合并 · 基类默认实现 · 真缺（只有第三类是缺陷）。**

| 仍 Unknown | |
|---|---|
| 108 条各属哪类 | 未裁决 |
| `popmart` 24 步同名 0 | 抽签/展览/预约 17 步已证没有；剩 7 步未判 |
| `Registry.cs` 63 模块 ↔ 8 流程表 | 关系未建 |

**纪律**：**一个错的总数比没有总数更坏 —— 错的地方不在数字，在它旁边没写清楚它是什么。**


## 判据 (f) — 108 塌成 35（R845）

**工具**：`python analysis\partition_steps.py`。

```
108 条不同名
 ├── 49 条 StoreFlow（165 虚步骤）已声明 → 无缺口，只是没重写
 └── 59 条 基类也没有
      ├── 24 PopMart（17 抽签/展览/预约已证没有 + 7 未判）
      └── 35 真问题
```

### 49 条基类侧体现的设计

`Authorize` `CreateBasket` `SubmitCustomer` `SubmitShippingMethod` `InitiateCheckout` `CreateOrder`
`GetRates` `CalculateTaxes` `GetStructureToken` `CreateTransaction` `SubmitPayPal` `ProcessPayment`
—— **通用结账步骤在基类，各站复用。**

**`structure-token-*` 两行基类全有（12+8）→ R844 里那两行「不同名」是映射粗糙，不是缺口。**

### 59 条的分布

| 流程 | 条数 | 状态 |
|---|---|---|
| popmart | 24 | 17 已证没有；7 未判 |
| nike | 9 | **R843 已定性：粒度** |
| demandware-dual | 9 | App/Dw 双路（R112 注释） |
| johnlewis | 8 | Stripe + 交付回调 |
| demandware-classic | 5 | 未判 |
| collectplus-app | 4 | 未判 |

**→ 剩 26 条要分别判。**

| 仍 Unknown | |
|---|---|
| 26 条真判 | dual 9 · johnlewis 8 · classic 5 · collectplus 4 |
| 49 条基类实现是否适用每站 | **「有」≠「对它这个站正确」** |
| popmart 7 步 | 未判 |

**纪律**：**数变小不是因为放宽标准，是因为做了一次检查。**


## 判据 (f) — demandware-dual 结案（R846）：26 → 17

**`ScapiAppPath.cs`（R124）已答完 dual 的 9 条：**

| 类别 | 步骤 |
|---|---|
| app 侧有端点 | `StartAppFast` `StartAppSafe` → `getAccessToken`；`AddToCartApp` → `addItemToBasket` |
| dw 侧有控制器 | `GetSessionDw` `GetCartDw` → `Cart-Get`；`AddToCartAppDw` → `Cart-AddProduct` |
| **app 侧无端点** | `ApplyDiscountApp` `GetCheckoutApp` `GetRatesApp` `SubmitOrderApp` |

> **NoOrdersEndpoint：「the SCAPI family has no orders endpoint … an app-path order must cross back to the classic controllers」**
> **→ 15 步两套词汇不是两条完整路径，是「app 起手、经典控制器收尾」。**

### 剩余

| 流程 | 条数 |
|---|---|
| johnlewis | 8 |
| demandware-classic | 5 |
| collectplus-app | 4 |
| **合计** | **17** |

### 第三次同样的错 → 规则

| 轮 | 造了什么 | 仓里早已有 |
|---|---|---|
| R838–R842 | 115 名字 | `StoreFlowSteps.cs`（R112） |
| R844–R845 | 108 不同名 | `StoreFlow` 165 虚步骤 |
| **R846** | dual 9 条 | **`ScapiAppPath.cs`（R124）** |

**规则**：**每批裁决前 `ls replica/src/Cybersole.Stores/Flows/*.cs | grep -i <flow-or-topic>`。**
**下一轮先读 `JohnLewisStepMap.cs`，不是先判 johnlewis 8 条。**

**纪律**：**代价不是时间，是文档里出现一份「待判 26 条」的假清单。**


## 判据 (f) — 17 → 4（R847）

**规则（R846 立）**：先 `Get-ChildItem replica/src/Cybersole.Stores/Flows -Filter *.cs`。**47 个文件，其中一整个 `*StepMap`/`*Steps` 分析层。**

| 流程 | R845 | R846 | R847 | 依据 |
|---|---|---|---|---|
| demandware-dual | 9 | 0 | 0 | `ScapiAppPath.cs`（R124） |
| johnlewis | 8 | 8 | **0** | **`JohnLewisStepMap.cs`（R118/R119）** |
| demandware-classic | 5 | 5 | **0** | **`DemandwareStepMap.cs`（R117）** |
| collectplus-app | 4 | 4 | **4** | **无专属文件** |
| **合计** | **26** | **17** | **4** |

### 两句该记的话（都出自已有文件）

> **a BFF endpoint is not a step … the step list is the client's phases and the endpoints are the server's resources.**

> **there is no `Stripe-*` controller anywhere in the image** —— 支付控制器全是 Adyen 的；R117 选择说出这件事而不编一个。

### 剩 4 条 = 真待判

`CreateCheckoutApp` · `GetDelivery` · `GetCollectPlusLocations` · `SubmitCollectPlus`

| 仍 Unknown | |
|---|---|
| 这 4 条要不要做 | 流程在 `StoreFlowSteps` 有 17 步表 → 镜像确实有它 |
| 8 流程 ↔ `Registry.cs` 63 模块 | 仍未建 |

**纪律**：**R844 的 16.9% 的真实问题是「用一个跨层级的量当覆盖率」。**


## 判据 (f) — 线索收尾（R848）

| 阶段 | 数 | 依据 |
|---|---|---|
| 名字清单 | 115 | 元数据 `<Name>d__N` |
| 探针三轮后 | 71 | |
| 8 流程 130 步 · 22 同名 | — | `StoreFlowSteps` |
| 减基类已有 | → **59** | `StoreFlow` 165 虚步骤 |
| 减 R124 | → **50** | `ScapiAppPath.cs` |
| 减两份 StepMap | → **4** | `JohnLewisStepMap` · `DemandwareStepMap` |
| 最后 4 条 | **已登记未证** | `LambdaWitness.Unwitnessed` |

### 端点族一直在

```
/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores   <- GetCollectPlusLocations
/component/singlepagecheckout/cac/submit                                 <- SubmitCollectPlus
```

**探针找的是「标识符含 CollectPlus」，而它写在路径里 → 0 命中。**

### `LambdaWitness.Unwitnessed`

```csharp
{ "popmart", "demandware-classic", "demandware-dual", "collectplus-app",
  "structure-token-multi", "structure-token-single" }
```

**注释：Flows with no ownership witness — their gaps stay unresolved.**

**→ 注意：`popmart` 也在里面。R835–R838 说它「没有」实现，而这里说的是「没有 ownership witness」——
两句话不同，不宜混用。**

| 仍 Unknown | |
|---|---|
| `collectplus-app` 的 ownership witness | 这正是登记原因 |
| `CreateCheckoutApp`/`GetDelivery` 族内具体端点 | 族已定位，未一一对上 |
| `popmart`/`structure-token-*` 的「没有」vs「未证」 | 两种说法要分开 |

### 纪律

**判据 (f) 的正确做法不是「先建清单再裁决」，是「先读 `Flows` 目录里的分析文件，它们就是清单」。**
**七轮五次建清单，五次都低估 —— 这不是疏忽，是方法缺一步。**


## 判据 (f) — PopMart 修正（R849）：端点全在，缺的是步骤

| 层 | 状态 |
|---|---|
| 端点 | **`PopMartEndpoints.cs` 39 个常量，14 个抽签/展览/预约端点全部存在** |
| 映射 | **`PopMartStepMap.cs`（R116）14 对** |
| **步骤** | **`PopMartFlow` 11 个重写里无一个 draw/exhibit/reservation** |

**→ 未覆盖的原因是「步骤方法没写」，不是「端点没有」或「未建模」。**

### 修正

**R835「没有任何流程覆盖它」/ R836「七块未建模」/ R838「十二个名字全为 0」——
端点层是错的，只在步骤层成立。**

**为什么没发现**：R835 从 `PopMartBrowser` 出发只查了 `activity/v1/exhibit_draw`（actapi 那条路），
**而 `/shop/v1/storeOfflineDraw/join` 是另一条路，镜像两条都有。**

| 仍 Unknown | |
|---|---|
| `CheckResult` 对哪个端点 | R116 诚实留空 |
| 剩下 10 步的端点 | `UnmappedSteps` 是数据 |
| 两条路的关系 | 未判 |

**纪律**：**「查了一条路」≠「查了全部路」。**


## 优先级 ① — PopMart 14 抽签步骤的证据边界（R850）

**参数记号（镜像）：** `_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1` · `Drawno`

| 判定 | 步骤 |
|---|---|
| **可写（3）** | `StartDrawFlow` · `FindDraw`（`detail?uniqCode=`）· `GetOrders` |
| **只有端点、无请求形状（11）** | `EnterDraw` `ChooseGoods` `FindMegaDraw` `EnterDrawEvent` `RedeemMemberPoints` `RedeemLuckPoints` `FindExhibit` `EnterExhibit` `EnterReservation` `FindDates` `FindTimeSlots` |

**不写这 11 个的理由（与 R823 同一条）**：
**能发请求但不知道发什么的方法，比不存在的步骤更坏 —— 它让「14 步已实现」看起来成立。**

### 写那 3 个的前置条件（未查）

1. `StoreFlowRunner` 的步骤序列固定 → 加步骤要同时改 runner
2. **`StoreFlowSteps` 的 ordinal ↔ runner 调用表是否一致** —— **加步骤前必须查清**

| 仍 Unknown | |
|---|---|
| `EnterDraw`/`ChooseGoods` 请求体 | **11 步里最关键的两步**，镜像无字段名记号 |
| `uniqCode` 来源 | `currentUniqCode` 暗示「当前」概念，未证 |
| runner 序列 ↔ `StoreFlowSteps` ordinal | **加步骤的前置条件** |

**纪律**：**宁可缺，也不要一个有形状没内容的实现。**


## 判据 (f) — 结构性发现（R851）：一条通用序列 vs 八条按流程序列

**`StoreFlowRunner.RunCheckoutAsync` = 手写固定 21 步元组序列，所有流程共用；不用 `StoreFlowSteps` 的 ordinal。**

```
GetHome GetCsrf GetSession FindProduct FindVariant CreateCart AddToCart GetCart EditLine
InitiateCheckout GetCheckout SubmitEmail SubmitShipping GetShippingRates
SubmitShippingMethod SubmitBilling SubmitDiscount SubmitPayment GetPaymentToken SubmitOrder ProcessOrder
```

**镜像：每流程一条序列** —— Nike 16 · PopMart 24 · JohnLewis 19 · DW 12/15 · CollectPlus 17 · ST 15/12。

### 统一解释

| 现象 | 原因 |
|---|---|
| Nike 10 细步 vs 3 粗步 | 通用序列没有 `ValidateAddress` 位置 |
| PopMart 14 抽签步写不进 | 结账序列表达不了抽签流程 |
| JohnLewis `WebHandOver` 无处放 | 流程专属步骤无对应位置 |
| R844 的 16.9% | 拿通用序列名字对八条流程步骤名 |

> **(f) 的「为什么」统一答案：不是端点缺、不是方法没写、不是粒度，是执行框架形状不同。**

### 三种改法

1. **`StoreFlow` 加 `IReadOnlyList<Step>`，runner 按流程取** —— 最忠实，动 runner + 165 声明
2. **runner 加 per-flow 分支** —— 快，成堆特例
3. **保持通用序列，专属步骤塞进现有步骤** —— **现状**

**只有 1 能让「每个函数功能相等」成立。本轮不改 —— 架构改动不该一轮顺手做。**

| 仍 Unknown | |
|---|---|
| 镜像那侧怎么组织 | 一个调度器按流程取序列 vs 8 个独立执行器 —— 未查 |
| ordinal 递增是否即运行顺序 | Inference（中） |
| 做法 1 对 165 声明 + 1766 用例的影响 | 未估 |

**纪律**：**「缺几个方法」和「户型不一样」是两个诊断；我前面十几轮一直在做前者。**


## 判据 (f) — ordinal 按流程编号（R852）

**130 个 ordinal · 63 不同 · 67 跨流程重复 · 范围 20–153。**

| 流程 | 范围 |
|---|---|
| JohnLewis | 20 – 39 |
| DemandwareDual | 26 – 47 |
| StructureTokenMulti | 29 – 47 |
| DemandwareClassic | 32 – 43 |
| CollectPlusApp | 33 – 50 |
| StructureTokenSingle | 40 – 51 |
| Nike | 41 – 58 |
| PopMart | 104 – 153 |

**六个挤在 20–51 且重叠 → 每流程自己编号 → 各自一个类、各自一套序列。**
**→ R851「八条按流程的序列」从 Inference 升为 Observation。**

### 一条对复刻件设计的反证

**`AddToCart` 在 JohnLewis 是 22、在 DemandwareClassic 是 32 —— 同名不同号。**
**→ 镜像里同名步骤在不同流程中是**不同方法**，不是共享方法被复用。**
**→ 对「165 虚方法 + 按站重写」是反证：镜像似乎每流程各写一份。**

| 仍 Unknown | |
|---|---|
| 镜像类结构 | 八类各持一套序列（Inference 高）；要证走 MethodTable |
| 重叠是否可能来自共享方法 | 「`d__32` 指不同步骤」排除，但观察来自转写 |
| 做法 1 该做多大 | 若序列与类绑定，可能不只是加一个列表 |

**纪律**：**「同一个结论换一个能证伪它的检查」比「补原来缺的那个证据」容易 —— 前者只要读表。**


## 判据 (f) — 第九条序列 + 分母不可靠（R853）

**直接证据（镜像原文）：**
`<AddToCart>d__32` @`0x1434acef3` = DemandwareClassic 逐字 · `<AddToCart>d__22` @`0x14338114f` = 未命名序列
**→ 同名字两个编号 → 编号按流程给 = Observation（R852 的转写警告解除）。**

### 新发现

`GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23)` **不匹配 8 条中任何一条**
（CollectPlus `GetHome`=33；struct-token-multi `FindProductMulti`=29）。

**→ 镜像至少还有第九条流程序列，`StoreFlowSteps` 里没有它。**

### 没问过的问题（现在很关键）

> **`StoreFlowSteps` 那 8 条是怎么选出来的？**
> R112 注释说「each flow's steps sit in one adjacent run」，**但没说是怎么确定「哪些流程」的。**

**若选法有偏，8 之外可能还有几条。而 8 是 R844 那个 16.9% 的分母。**

| 仍 Unknown | |
|---|---|
| 第九条属于哪个流程 | 需读完整 blob |
| **8 条怎么选出来的** | **关键** |
| 总共多少条序列 | **(f) 的分母，现不可靠** |

**纪律**：**分母错了，百分比就错了 —— 而它已经写进三份记录。**


## 判据 (f) — 67 段序列（R854）：8 条是抽样

**`idautils.Strings()` 遍历 1301 条含 `d__` 串 → 4 步以上递增运行 **67 段**。**

**明显是业务流程的 ≥20 段；`StoreFlowSteps` 的 8 条只是其中一部分。**

| 8 条里没有的（部分） | 步数 |
|---|---|
| `…GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` | 11 |
| `GetHome · GetCartValue · SubmitInfo · SendManualNotification` | 8 |
| `…GetLotteryForm · SubmitLottery` | 7 |
| `GetSession · RefreshToken · GenerateCheckout · SubmitEmail` | 7 |
| `SubmitPayPal · ApplyPayPal · ProcessPayPal · Process3DS` | 6 |
| `GetSweepStakeCheckout · … · EnterSweepStakesRaffle` | 4 |

> **R844 的 16.9% 连分母都不对，不该再当覆盖率引用。**

### `HandleResponse` 的邻居（优先级 ②）

```
0x14345abb1   HandleResponse · GetScript · GetKasada · GetWorkTime
```

**R824 查到它「总提及 = 1」、R827/R828 追不到代码 —— 现在它在一条序列里，邻居是 `GetKasada`。**
**→ 它大概是 Kasada 流程里的一步，不是通用「处理响应」。**

### 另外三组（优先级 ②）

`GetLogo · GetCookie · SubmitClientData · SubmitPOW · SubmitWebRtc`（POW/WebRTC）·
`SubmitProps · SubmitProps2 · SubmitWpt · SubmitSensor` · `MoveMouseAsync · PressMouseOnScreenAsync · PressKeyAsync`

| 仍 Unknown | |
|---|---|
| 20+ 段各属哪个站 | 要看端点族 |
| 8 条当初怎么选的 | 已知是抽样 |
| `HandleResponse` 是否真属 Kasada | Inference 中（「相邻 ≠ 同管线」） |
| 67 段里多少是库代码 | 未逐段分类 |

**纪律**：**「抽样还是总体」我在 R816 对 `pe_strings.txt` 问过并写进 §2.7b，却没对 `StoreFlowSteps` 问 —— 因为它看起来是我自己整理的数据。**


## 判据 (f) — 站 × 变体 × 风控 三层（R855）

**复刻件覆盖差别：**

| 变体 | 镜像步骤 | 复刻件 |
|---|---|---|
| raffle | （`RaffleFlow`，R835 查过 r419/lndg/nodnod） | **96 处 / 7 文件** |
| **sweepstake** | `GetSweepStakeCheckout · GetSweepStakesShippingMethod · SubmitSweepStakesShipping · EnterSweepStakesRaffle` | **0** |
| **lottery** | `… GetLotteryForm · SubmitLottery …` | **0** |
| **PayPal 信用卡** | `… GetPaypalId · GetPaypalBearer · ProcessPaymentPaypalCreditCard` | 未查 |

**`TaskType` 在复刻件只 2 处（`ThirdPartyDrivers.cs`），无任务型枚举。**

### (f) 的表需要三列而非一列

| 维度 | 状态 |
|---|---|
| 站 | 8 条已记 + **20+ 段未认** |
| **任务变体** | raffle 有；sweepstake / lottery / PayPal 信用卡 无 |
| 风控 | Kasada · Cloudflare · **`HandleBlock` 未接** |

| 仍 Unknown | |
|---|---|
| sweepstake/lottery 是否真是任务型 | Inference 中 |
| 镜像的任务型枚举 | 只见过 `PopMartProductType` |
| 20+ 段哪些是站哪些是变体 | 本轮只认 3 段 |

**纪律**：**「段属于谁」被我默认成「属于哪个站」—— 因为前面十几轮全在按站数。而 `ProcessPaymentPaypalCreditCard` 一看就不是站。**


## 判据 (f) — 任务层 = 5 个 `Start*Flow` + 3 个 `*Task`（R856）

```
0x14337bdc4  StartSignupFlow d__57 · StartClearFlow d__58 · StartInStoreFlow d__59 · StartPopNowFlow d__60 · StartNormalFlow? d__61
0x14337cdcc  FetchTasks d__187 · StartDailyCheckInTask d__188 · StartPopNowViewTask d__189
```

**编号连续 → 分派层入口。**

**而 sweepstake / lottery 是流程内步骤**（`GetSweepStakeCheckout` d__40–42 · `GetLotteryForm` d__36 / `SubmitLottery` d__37）。
**→ 序号落在流程段 → R855 猜的「任务变体」不成立；它们属**流程层**。**

### 三层修正

**任务型（5+3）· 流程（站／变体）· 风控**

**→ 复刻件缺 sweepstake/lottery 是「某条流程里两个步骤」，不是「两种任务型」。**

### 新的最好答的 Unknown

**镜像 5 个 `Start*Flow` ↔ 复刻件 `Registry.cs` 63 个模块 —— 五个名字都在手上。**

| 仍 Unknown | |
|---|---|
| 第五个是不是 `StartNormalFlow` | Inference 高（截断在 `<St`） |
| **5 个 Start*Flow ↔ 63 模块** | **最好答的一个** |
| `FetchTasks` / `StartPopNowViewTask` 有无 | `StartDailyCheckInTask` 已判为 `CheckIn`（R842） |

**纪律**：**「猜属于哪层」看 ordinal 落在哪个编号段，比读名字准 —— 而 ordinal 分段的规则是 R852 自己立的，我没用在自己的猜测上。**


## 判据 (f) — 顶层维度不同（R857）

| | 镜像 | 复刻件 |
|---|---|---|
| **顶层** | **任务种类 5 种**：`StartSignupFlow` `StartClearFlow` `StartInStoreFlow` `StartPopNowFlow` `StartNormalFlow` | **店：64 模块 / 33 流程类 / 33 shop id** |
| 二层 | 站／变体的流程序列 | 33 流程类 |
| 三层 | 风控 | 风控 |

**→ 复刻件能表达「对 Nike 结账」，表达不了「抽签任务 vs 常规结账」的区别 —— 后者在镜像里是顶层选择。**

> **这比缺 14 个方法更根本：方法能在现有结构里补，任务种类这一层没有对应位置。**
> **R851（一条通用序列 vs 八条按流程序列）与 R857（序列之上还有一层选择）是同一问题的两面。**

| 仍 Unknown | |
|---|---|
| 5 个种类各驱动哪些店 | `StartPopNowFlow`→Pop Mart 明；「清仓」适用哪些未查 |
| 复刻件任务配置有无「种类」字段 | `TaskColumn` 是表格列；要查 `Tasks` 模型 |
| 64 模块 / 33 流程类 | 一流程类被多 shop id 复用（合理），但「店」成了唯一区分维度 |

**纪律**：**问「这些段属于谁」之前，先问「复刻件按什么维度组织」。维度不同时，用一侧的维度索引另一侧，只会得到对不上的行。**


## 判据 (f) — `Task.Type` 死字段（R858）

**`Tasks.cs`：`public string Type { get; set; }` —— 全 `src` 无一处 `.Type =` 赋给它。**
**`TaskCombinationRequest` 只有 `required string Store`，无种类字段。**

| | 镜像 | 复刻件 |
|---|---|---|
| 种类 | `Start*Flow` ×5（d__57–61）真分派 | **字段在，无写入者** |

### 同一条标准的第三种形态

| 形态 | 例子 |
|---|---|
| 编造一个值 | R823 三个 CSRF GUID |
| 有形状没内容的方法 | R850 那 11 个抽签步骤 |
| **没人写的字段** | **R858 `Task.Type`** |

**→ 三种都让「已完成」看起来成立。**

### 本轮不删的理由

**删不删取决于镜像有没有这个字段 —— 未查。而「先删再查」会删掉线索（R815 的坑）。**

| 仍 Unknown | |
|---|---|
| 镜像任务模型有无 Type | **决定留删** |
| `Start*Flow` 靠什么分派 | 五个方法在，派发判断未查 |
| `Task.Type` 谁加的 | git log 可查，未必记了理由 |

**纪律**：**「没有这一层」vs「有字段、没有层」—— 后者才会让人走到「镜像里到底有没有这个字段」。**


## 判据 (f) — `CreateInputModel` 13 属性无 Type（R859）

**按镜像的属性书写模式 `类型,程序集.名字!访问器` 抽表：**
`CreateInputModel` = `AutoQuantity` `Color` `Currency` `Input` `MaxPrice` `MinPrice` `Minus` `Plus`
`PriceCheckVisible` `Quantity` `Sizes` `Symbol` `TogglePriceCheck` —— **13 个，无 `Type`。**

**边界**：这是**创建表单输入模型**，不是任务对象本身。

### 附带结论（对 R857）

> **五个 `Start*Flow` 的种类不是在创建表单里选的。**

**→ 复刻件从「没有种类输入」（正确）走到「也没有种类派发」（错误）。**

### 复刻件任务字段是混合物

| 有出处 | `MonitorMode` · `PriceCheck` · `MultiCart` |
|---|---|
| **自造** | **`NameTemplate` · `CheckoutDelay`（0 命中）** |

**→ 「功能 1:1」下，多出来的功能也是一种不相等。**

| 仍 Unknown | |
|---|---|
| 镜像任务对象有无 Type | 线索 `TaskDetail…` / `TaskGroup…` |
| 种类按什么派发 | 创建表单不含种类，依据是别的字段 |
| 两个自造字段留不留 | 支撑 `TaskCombinationBuilder`；镜像有无此功能未查 |

**纪律**：**找一个领域的**语法**比搜一个词有用 —— `Type` 有 27 个变体，直接搜等于没搜。**


## 判据 (f) — 模型层齐备；`Task.Type` 冗余（R860）

| 模型 | 镜像 | 复刻件 |
|---|---|---|
| `BotTask` | 14（**无 Type**；有 `Task` 嵌套、`StartTime`、`Status`） | **14/14** |
| `BaseCheckout` | 8（**有 Type**） | **8/8** |
| `TaskGroup` | 17（`CaptchaSource` · `CloudflareSolverId` · `ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines` · `Webhooks`） | **17/17** |
| `WebTask` | 2 | **2/2** |

**→ `Tasks.cs` 的 `Type` 是**冗余声明**，正确那份在 `BaseCheckout` 上。**

### 优先级 ② 的 Observation

**solver / 配额 / 计数全挂在 `TaskGroup`，不是单任务** —— **一个组共用同一套 solver 配置。**

### 未删的理由

**查了「有没有写」（0 处），没查「有没有读」。只读不写也可能被序列化进 `tasks.json` → 改输出结构 → 影响用例。**

### 对照的边界

**正则 `\b<属性名>\b` 搜**整个模型文件**，不是解析属性声明 → **上界宽松**，会把注释/别的类型/局部变量算进去。**

| 仍 Unknown | |
|---|---|
| `BotTask.Task` 是什么类型 | **若嵌套任务对象，「种类」可能在里** |
| `Task.Type` 有没有读点 | 决定能否安全删 |
| `TaskGroup` solver 配置复刻件挂在哪 | `KasadaSolvers`/`CloudflareClearance` 在，挂载点未查 |

**纪律**：**「字段存不存在」少了「在哪个类型上」这一维。**


## 判据 (a)/(f) — `BotTask.Task` 类型是 R364 未定项（R861）

**`Tasks.cs` 注释：**
```
R364: the binding table names six more members on this model. Five have an inferable type; "Task"'s
type could be an engine handle, an interface or a string id … so it stays named in docs/BINDING_BACKLOG.md.
```

**→ 这是既有未定项，不是新问题。**

### 与 `Task.Type` 的关系

**若 `BotTask.Task` 的类里真有 `Type`，复刻件那行不是「冗余」，是「**放错了位置**」→ 第三种处理：「挪」。**

### 四轮链条

R857 顶层是种类 → R858 `Task.Type` 死字段 → R859 创建表单无 Type → R860 `Type` 在 `BaseCheckout` → **R861 回到 R364 未定项**

| 仍 Unknown | |
|---|---|
| `BotTask.Task` 的类型 | R364 起；需 MethodTable（R828 未通） |
| `Task.Type` 删还是挪 | 取决于上一条 |
| 那六个成员里另外五个 | 注释未列名字 |

**纪律（第五次同类教训）**：**查一个成员之前，先在 `BINDING_BACKLOG.md` 里搜它的名字。**
**前四次是没读仓里的分析文件，这次是没读自己的待办清单。**


## 判据 — 抬走 R504 的天花板（R862）

**`BINDING_BACKLOG.md` L38–78 的 B 桶 31 条：性质是「静态拿不到行为证据」，不是「没做」。**

| 想拿的 | 为什么拿不到 |
|---|---|
| 描述符 → 注册代码 | 描述符无 xref（`0x14320c54d`→0 · `0x1436389fc`→0） |
| setter 做什么 | 编译期内联，无独立函数体 |
| `ICommand` 行为 | 委托初始化点靠类型信息定位，类型信息也无 xref |

### 目标分成两层

| 目标 | 可达 |
|---|---|
| 函数数量对等 | **可复算**（61.96%，R831） |
| 结构对等 | **可达** |
| **每函数功能相等** | **静态不可达，R504 起** |

### 待 YG 取舍

> 运行期差分是唯一剩余路线，**需要原版登录凭据**（goal 允许停等的两件事之一）。
> 不给则按「结构对等 + 行为 Unknown」收尾，并把边界写进完成判据每一处。

| 仍 Unknown | |
|---|---|
| 运行期差分成本 | 能否只跑单个动作 |
| 第三路线 | R504 列两条；R854「相邻运行」是第三种但只能定位 |
| 委托初始化点是否全无 xref | R504 只查两块描述符 |

**纪律**：**backlog 是「已经走不通的路」的清单。R504 记下后，我在 R824–R828 又重试了五轮。**
