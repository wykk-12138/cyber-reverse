# B 类 31 个缺口：逐类型决定（R309）

绑定表 `docs/xaml_bindings.json` 给出了每个类型的**完整命名空间**，这让"结构差异"从"说不清"变成"能决定"。
下面每个类型一行结论 + 依据。重算缺口：`python tools/backlog_report.py`。

## 结论分四种

- **抽控件**：原版确实有一个独立控件，复刻件里是内联构造 → 值得抽出来；
- **已有等价物**：功能在，只是名字/形状不同；
- **不可得**：值或上下文拿不到（见 R265 三源否证）；
- **纯内部状态**：没有独立控件，只是行/项的字段，记结构差异即可。

## 逐类型

| 类型（完整名） | 缺的成员 | 结论 | 依据 |
|---|---|---|---|
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvRow` | FullySelected, RowError, RowStatus | **抽控件** | 绑定表里是独立行控件（4 成员）；复刻件的 CSV 编辑是表单式，无行对象 |
| `Cybersole.Ui.Views.SmartActions.FilterRow` | IsFirst, Passed, ValueText | **抽控件** | 独立行控件（6 成员）；`IsFirst` 说明它知道自己在列表首位 |
| `Cybersole.Ui.Views.SmartActions.ActionRow` | IsFirst, Tooltip | **抽控件** | 同上（4 成员） |
| `Cybersole.Ui.Views.SmartActions.InputRow` | Matched | 抽控件（小） | 2 成员；`Matched` 是输入是否命中 |
| `Cybersole.Ui.Views.SmartActions.FilterInputEntry` | IsFirst | 抽控件（小） | 3 成员 |
| `Cybersole.Ui.Controls.ComboBoxEdit` | ClearSelectionCommand, RemoveTokenCommand | **抽控件** | 名字里的 `Token` 说明这是**可移除 token 的多选下拉**；同族还有 `ComboBoxToken`/`ComboBoxGroupHeader` |
| `Cybersole.Ui.Views.Accounts.AccountStoreEntry` | IsSelected | 已有等价物 | 复刻件的账户树节点承担同一角色 |
| `Cybersole.Ui.Views.Tasks.ElementCell` | ColumnSpan | 抽控件（小） | 元素网格的单元格；复刻件用列配置表达跨度 |
| `Cybersole.Ui.Localization.LocalizeSwitchExtension` | Condition | 已有等价物 | 复刻件用内联三元表达同一意图 |
| `Cybersole.Ui.Localization.LocalizeFormatExtension` | Value2 | 已有等价物 | 复刻件格式化用 `string.Format` 直调 |
| `Cybersole.Models.AycdInboxAccount` | TaskCount | 已有等价物 | 复刻件 `AycdInboxClient` 返回计数，未建模型 |
| `Cybersole.Models.NotificationSound` | SoundLocation | 已有等价物 | **`NotificationOptions.Path`**（`Profiles.cs:175`，每类一个），`SelectSound`/`ResetSound` 写它（R310 核实） |
| `Cybersole.Helpers.BrowserProfile` | DisplayName | 已有等价物 | 复刻件 `BrowserProfileAssignment` |
| `Cybersole.Models.User` | IsStaff | **不可得** | 需要账号角色信息，本地无来源 |
| `Cybersole.Attributes.Platform` | InputType, QuantitySupport, QuantityAutoAdjustSupport | **不可得** | 三源否证（R265）：池子只有名 / 下拉点不开 / locale 无 `Platform.*` |
| `Cybersole.Webhook.IWebhook` | ExtraFields | 抽结构（小） | locale 有 `Settings.Webhook.ExtraFields`，说明界面确有"额外字段" |
| `Cybersole.Ui.Views.Auth.AuthWindow` | Logout | 已有等价物 | 复刻件 `UserView.LogOut()`（R259）；原版是窗口级，形状不同 |
| `Cybersole.Ui.Views.Auth.LicenseControl` | Authenticate | 已有等价物 | 复刻件登录/许可在 `LoginControl` 里 |
| `Cybersole.Ui.Views.Accounts.AccountStoreType` | ColorSupport, Elements | 已有等价物 | 复刻件的商店契约是 `IStoreModule` |
| `Cybersole.Ui.Views.Settings.GeneralSettingsView` | Transition | **名不副实** | 见下 |
| `Cybersole.Ui.Views.SmartActions.FilterRow`（`Filter` 同名项） | Variable | 纯内部状态 | 复刻件筛选器是 `Field/Operator/Value` |

## 两个"名不副实"要单独说

1. **`Filter` 在绑定表里指向 `FilterRow`**（不是独立类型）—— 所以这一条其实是 `FilterRow` 的重复计数，
   不是新缺口。
2. **`SettingsView` 指向 `GeneralSettingsView`**，其 `Transition` 与 R261 记录过的
   `Settings.SettingsView.Transition` 是**同名不同类**，不是设置页过渡动画；**不可得**（无证据说明它控制什么）。

## 于是 31 的合理拆法

| 类 | 条数 | 动作 |
|---|---|---|
| 值得抽控件 | **8** | `ProfileCsvRow` / `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ComboBoxEdit` / `ElementCell` / `IWebhook.ExtraFields` |
| 已有等价物 | 12 | 保持记录，注释里指向等价物 |
| 不可得 | 3 | `Platform` ×3、`User.IsStaff`、`SettingsView.Transition` |
| 纯内部状态 / 重复计数 | 2 | `Filter.Variable`、`FilterRow` 重复 |

**下一轮起按"值得抽控件"那 8 条做，一次一个，每个都带绑定表依据。**


## R310：把"已有等价物"这一列也逐条核实了一遍

不能只写"已有等价物"就完事 —— 那和"结构差异"是同一句空话。逐条查了实现：

| 声称的等价物 | 实际存在 | 位置 |
|---|---|---|
| `AccountStoreEntry.IsSelected` → 账户树节点选中 | ✔ | 2 处命中（选中账户字段） |
| `LocalizeFormatExtension.Value2` → `string.Format` | ✔ | 2 处 |
| `AycdInboxAccount.TaskCount` → Aycd 计数 | ✔ | 4 处 |
| `NotificationSound.SoundLocation` → **`NotificationOptions.Path`** | ✔ | `Profiles.cs:175` + `SelectSound` 写它 |
| `BrowserProfile.DisplayName` → `BrowserProfileAssignment` | ✔ | 15 处 |
| `AuthWindow.Logout` → `UserView.LogOut()` | ✔ | 2 处（R259 加的） |
| `LicenseControl.Authenticate` → `LoginControl` | ✔ | 15 处 |
| `AccountStoreType` → `IStoreModule` | ✔ | 7 处 |

**两条"我一开始以为没有"的，其实是名字不同**：`SoundLocation` 在复刻件里叫 `Path`。
又一次印证 R295 那条：**"未命中"要复核查法。**

（`LocalizeSwitchExtension.Condition` 与 `Filter.Variable` 仍按"内联/内部状态"处理 ——
它们本来就不是可指认的成员。）
