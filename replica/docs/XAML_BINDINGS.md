# 原版的 XAML 绑定表：界面到底"碰"了哪些成员

## 这张表从哪来

`Cybersole.exe` 里 Avalonia 编译期 XAML 会为每个绑定生成一条描述符字符串：

```
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.CopyPassword!Getter
Cybersole.Ui.Views.Accounts.AccountGroupView,Cybersole.GroupName!Setter
Cybersole.Ui.Views.Browser.CustomBrowser,Cybersole.Back!Getter
```

左边是**类型全名**，右边是**它绑定的成员名**，`!Getter` / `!Setter` 表示绑定方向。
这些描述符在镜像 `0x0320b000` 起的一段里连续排布，抽出来得到：

```
174 个被 XAML 绑定的 Cybersole 类型
819 个去重成员名（1457 条 getter/setter 描述符）
```

存为 `docs/xaml_bindings.json`（约 20 KB）。

**和 locale 的区别**：locale 说界面**显示**什么（`Settings.General.QuicktaskSettings` → "Quicktask Settings"），
这张表说界面**碰**什么（`AccountGrid` → `CopyPassword`）。后者更接近行为。

## 怎么用

```
python tools\bind_diff.py              # 在整个 src/ 里找成员名 → "行为是否存在"
python tools\bind_diff.py --per-file   # 只在同名类所在文件里找 → "这个类是否暴露它"
```

两种口径给出的数字差很多，**引用时必须说清是哪种** —— 这是 R225 犯的错（见下）。

## 两种口径的数字（R225/R226）

| 口径 | 结论 |
|---|---|
| per-file（同名类文件内） | 108 个类型有对应类，167 个成员在该文件里没有 |
| whole-source（整个 src/） | **107 个成员在任何地方都没有**（50 个类型） |

差 60 个的原因：**复刻件把行为写在别处**。最典型的是 `ProxyView` 的
`CopyProxies / CloneProxies / DeleteProxies / TestProxies` —— 它们实现在 `ProxyGrid` 上
（`CopySelected / CloneProxy / DeleteSelected / TestProxy`），`ProxyView` 只有内联 lambda。

> **所以"成员名缺失"多数不是"能力缺失"，而是"名字不在那个类上"。**

## R226 修掉的

`ProxyView` 的六个名字现在真的存在，并且按钮改为调用它们（不是空壳）：

| 名字 | 行为 |
|---|---|
| `AddProxies(group)` | 调用注入的导入器 |
| `ClearAll(group)` | 清空该组的代理 |
| `CopyProxies()` | `_grid.CopySelected()` |
| `CloneProxies()` | 对每个选中项 `_grid.CloneProxy` |
| `DeleteProxies()` | `_grid.DeleteSelected()` |
| `TestProxies()` | 对每个选中项 `_grid.TestProxy` |

效果：whole-source 口径的缺口 **115 → 107**。

## 还剩下的真缺口（按类型）

| 类型 | 缺 | 性质 |
|---|---|---|
| `TaskView` | `CloneSelected, CopyUrl, EditAll, ForceStartSelected, OpenGroupPopup, OpenSolvers, OpenStaggerStart, OpenTaskCreator …` | 多数需要真实行为，不是改名 |
| `SmartActionsCreator` | `AddAction, AddFilter, AddInput, CloseOverlay, DeleteAction, DeleteFilter, DeleteInput, DeleteParam` | 编辑器的命令集，尚未成体系 |
| `UtilitiesView` | `CloneStoreGroup, CreateStoreGroup, DeleteStoreGroup, EditStoreGroup` | 行为已存在（内联），名字不在 |
| `TaskCreatorMainView` | `ProfileItems, ProfileGroupItems, SizeItems, ShowCartView` | 该视图在复刻件里是另一个名字 |
| `Models.EditValue\`1` | `HasMultiple_87 … HasMultiple_101` | **噪音**：泛型实例化产生的编号成员 |

`Models.EditValue\`1` 那 8 个是**编译器产物**，不是设计成员；统计时要排除。

## 纪律

1. 引用这张表时**写明口径**（per-file / whole-source）；
2. 加名字要**同时接到 UI 上**，不许为了消数字加空壳（`DeadButtonTests` 与 `UnreachedUiTypesTests` 会盯）；
3. 泛型编号成员（`HasMultiple_NN`）不计入缺口。

## R230：`SmartActionsCreator` 补了 8 个，剩 5 个**卡在模型上**

补上（都有模型支撑、按钮真的走它们）：

| 名字 | 实现 |
|---|---|
| `Save` | 原本就是 `private`，改成对外 |
| `IsEditing` | `existing is not null` |
| `SmartAction` | 正在编辑的动作 |
| `AddFilter(filter)` | 加筛选器 + 重画第 2 步（按钮改为调用它） |
| `DeleteFilter(index)` | 删除并同步 `SmartAction.Filters`（按钮改为调用它） |
| `Clone()` | 复制动作（含筛选器）写进文档并保存 |
| `Minimise()` / `Exit()` / `CloseOverlay()` | 宿主窗口操作 |

**卡在模型上的 5 个（需要先改模型，不是加个名字就行）**：

| 名字 | 缺什么 |
|---|---|
| `AddAction` / `DeleteAction` | 复刻件的 `SmartAction` 是**单个动作**（`Kind`/`Target`），原版有 `Actions` 集合与 `ActionParams`/`ActionConfig` 类型 |
| `AddInput` / `DeleteInput` / `DeleteParam` | 原版筛选器带 `Inputs`（`FilterInputEntry`），复刻件的 `SmartActionFilter` 只有 Field/Operator/Value |
| `ToggleFilterBehaviour` | 原版筛选器有 `Behaviour`（AND/OR），复刻件没有这个字段 |

这些**不是命名差异**，是**模型少了东西**。要做就得先扩模型（并补对应的序列化测试），
所以它们进的是"待扩展模型"清单，而不是"待加名字"清单。

## R231：`UtilitiesView` 五个绑定名落地（`StoreGroupModal` 因此从"不可达"变成可达）

| 名字 | 实现 |
|---|---|
| `StoreGroups` | `Config.Settings.StoreGroups` |
| `CreateStoreGroup(name)` | 建组（名字为空则 "Group N"），保存并刷新 |
| `CloneStoreGroup()` | 复制选中组（含 stores 列表） |
| `DeleteStoreGroup()` | 删除选中组 |
| `EditStoreGroup()` | 打开 `StoreGroupModal` —— **这个窗口此前从未被构造过**，于是它从"声明了没人用"的基线里掉了出去（36 → 35） |

三个按钮（New / Clone / Delete）改为调用这三个命令，行为只有一份。

> 这条值得单独记：**给一个命令补名字，顺手把一个"死窗口"救活了** —— 两条守卫各自响了一次。

## R233：`TaskCreatorMainView` 四个成员落地（缺口 76 → 70）

复刻件把它映射成 `TaskCreatorView`（`OriginalViewClassParityTests` 的 Renamed 表里三个原名都指向它）。

| 名字 | 实现 | 依据 |
|---|---|---|
| `SizeItems` | `SizePalette.Build(Settings.CustomSizes)` | 编辑器里已有的尺码梯 |
| `ProfileItems` | `Config.BillingGroups.SelectMany(g => g.Profiles)` | **profiles 挂在 Billing 组下**，不是独立文档 |
| `ProfileGroupItems` | `Config.BillingGroups` | Billing 页左栏就是 "PROFILE GROUPS" |
| `ShowCartView` | `_tabs.SelectedIndex == 1`（可写） | Setup / Cart / Advanced 三个标签 |

**一个容易走错的地方**：第一版我按 `Config.Profiles` / `Config.ProfileGroups` 写，编译直接报
"ConfigurationStore 未包含 Profiles" —— 因为**profile 根本没有独立文档**，它们属于 `BillingGroup`。
GUI 那边（Billing 页左栏叫 PROFILE GROUPS）本来就说清了这件事，是我先去猜了模型。

## R235：剩余 67 个的完整清单（权威 backlog）

口径：**whole-source**（在 `src/` 任意位置都找不到这个名字）。`python tools\bind_diff.py` 可随时重算。

### A. 噪音（12，不计入缺口）

| 类型 | 成员 |
|---|---|
| `Models.EditValue\`1` | `HasMultiple_87 … HasMultiple_101`（泛型实例化产物） |

### B. 只缺名字/入口（可直接补，行为多半在别处）

| 类型 | 缺 | 名字 |
|---|---|---|
| `Ui.Views.SmartActions.FilterRow` | 3 | `IsFirst, Passed, ValueText` |
| `Ui.Controls.ComboBoxEdit` | 2 | `ClearSelectionCommand, RemoveTokenCommand` |
| `Ui.Views.Accounts.AccountGrid` | 2 | `CopyAccounts, CopyPassword` |
| `Ui.Views.Settings.CaptchaProvidersView` | 2 | `DisabledProviders, EnabledProviders` |
| `Ui.Views.Settings.DataView` | 2 | `DataProviders, ViewBackups` |
| `Ui.Views.Settings.Modals.SizeCreatorView` | 2 | `SizeOptions, ToggleSizeSelected` |
| `Ui.Views.Settings.NotificationsView` | 2 | `ResetSound, SelectSound` |
| `Ui.Views.Settings.PaymentView` | 2 | `DetectedProfiles, SelectedProfiles` |
| 其余单成员 | 9 | `BrowserProfile.DisplayName`、`AycdInboxAccount.TaskCount`、`CreateModel.AccountSelectionMode`、`NotificationOptions.EnableSound`、`NotificationSound.SoundLocation`、`Solver.AIStatus`、`Status.Clickable`、`Store.ColorSupport`、`User.IsStaff` |

### C. 卡在模型（要先扩模型 + 序列化测试）

| 类型 | 缺 | 需要什么 |
|---|---|---|
| `SmartActionsCreator` | 5 | 多动作（`Actions` + `ActionParams/ActionConfig`）、筛选器 `Inputs`、`Behaviour` |
| `Attributes.Platform` | 3 | `InputType / QuantitySupport / QuantityAutoAdjustSupport` —— **每个平台的能力值缺证据**（成员名在池子里有，值没有） |
| `Models.CreateInputModel` | 4 | `MaxPrice, Minus, PriceCheckVisible, TogglePriceCheck` |

**结论：真正需要"设计决策"的只有 C 类 12 个；B 类 30 个是照名字接线；A 类 12 个是噪音。**

`python tools\bind_diff.py --buckets` 会直接给出这个分桶：

```
missing: 67     noise (HasMultiple_NN / Value_NN): 12     real gap: 55
```
