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
| **bstn 是否存在** | 原版 `bstn` / `BSTN` 都是 0 匹配 —— **复刻件多出来的模块** | **待裁决**（删=更忠实，牵动多处守卫） |
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
| `bstn` 删不删 | 待裁决 |
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
| bstn | **原版 0 字符串** | 待裁决 |

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
