import io
p = r'D:\projects\cyber-reverse\replica\docs\XAML_BINDINGS.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## R235：剩余 67 个的完整清单（权威 backlog）

口径：**whole-source**（在 `src/` 任意位置都找不到这个名字）。`python tools\\bind_diff.py` 可随时重算。

### A. 噪音（12，不计入缺口）

| 类型 | 成员 |
|---|---|
| `Models.EditValue\\`1` | `HasMultiple_87 … HasMultiple_101`（泛型实例化产物） |

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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('backlog written')
