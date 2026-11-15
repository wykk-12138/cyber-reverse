import io
p = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"
doc = '''# 绑定缺口工作账本（当前 17 = 0 可做 + 17 结构）

`docs/xaml_bindings.json` 是原版编译期 XAML 的绑定表（174 类型 / 819 成员）。这里按
**"这个类型在复刻件里存不存在"** 把缺口分成两类。

> **口径**：whole-source（`src/` 任意位置都找不到）· **削注释**（注释里的名字不算实现）
> · 排除泛型噪音 `HasMultiple_NN` / `Value_NN`（12 个）
> · 与 `tests/Cybersole.Tests/BindingGapRatchetTests.cs` 完全一致；重算：`python tools/backlog_report.py`

## 名字级缺口（17，`python tools/bind_diff.py`）

这 17 个名字在 `src/` 里一处都没有。它们大多是**结构性的**——绑定的是原版自己的辅助类型或
XAML 扩展，复刻件用别的方式实现了同样的行为。**不要为了凑数而造空类型。**

## 类型级缺口（11 个类型，`python tools/bind_scope.py`）

绑定表要的成员**没有长在该类型上**（名字在别处存在，所以不算进上面那 17）。

| 类型 | 成员 | 情况 |
|---|---|---|
| `TaskView` | `Toggle` | 唯一剩下的：无 locale 线索、无 GUI 证据 |
| `AccountGrid` | `AccountGroup` `Edit` | `AccountGroup` 疑为数据属性；`Edit` 无编辑路径 |
| `ProfileCreatorView` | `AdvancedView` `Navigate` `PaymentView` | 三步向导的分区，需 GUI 位置 |
| `CloudflareSolversView` | `Edit` | 无编辑路径（页面只有 Add / Fetch balance） |
| `DataView` | `ViewLogs` | 需要日志查看器（`AppPaths.LogsDir` 存在） |
| `GeneralSettingsView` | `ProfileItems` | 数据列表，位置未定 |
| `GoogleAccountsView` | `Edit` | 无编辑路径 |
| `ImapView` | `Configure` | AYCD 配置对话框，位置未定 |
| `SmartActionsView` | `Clock` `Export` | `Settings.General.EnableClock` 有线索，位置未定 |
| `Profile` | `Card` `Username` | 数据属性；`Card` 疑为 `Last4` 的格式化，`Username` 归属不明 |
| `ProxyTester` | `Name` | 无对应概念 |

## 已清零的类型（按轮次）

| 类型 | 结果 |
|---|---|
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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(doc)
print('BINDING_BACKLOG rewritten in UTF-8, bytes:', len(doc))
