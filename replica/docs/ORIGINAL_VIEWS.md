# 原版有哪些 XAML 视图（87 个）

从 `Cybersole.exe` 里挖出来的 `AvaloniaResourceXamlInfo` 索引：**一个字符串字面量，一次给全。**

```
find_regex  pattern="ClassToResourcePathIndex"     → 索引标签本身（283 字符）
find_regex  pattern="ACCOUNTS SELECTED" limit=5    → 命中最长的那个 = 整个资源 blob（37,926 字符）
```

blob 里是两段东西挨在一起：先是 `<a:Key>类全名</a:Key><a:Value>/Views/…axaml</a:Value>` 的索引，
后面直接跟着**英文 locale 的 JSON**。所以「原版有哪些页面」和「原版有哪些文案」是一次拿到的。

> 复现脚本：`analysis\dump_blob.py`（输出 `analysis\original_views.txt`、
> `analysis\avalonia_resources.txt`、`analysis\embedded_locale.json`）

## 这张表和 replica 的关系

replica 现在有 84 个 UI 类，其中 41 个「声明了没人 new」。**这 87 个是原版的答案**：哪些是真的页面、
哪些是弹窗、哪些是 Grid 组件。对照之后「不可达」这个词才有意义——如果原版也没有，那就不是缺；
如果原版有，那 replica 的不可达类就是**还没接上**。

## 账户页（R70 点过的那一页）

| 类 | axaml |
|---|---|
| `Cybersole.Ui.Views.Accounts.AccountView` | `/Views/Accounts/AccountView.axaml` |
| `Cybersole.Ui.Views.Accounts.AccountGrid` | `/Views/Accounts/AccountGrid.axaml` |
| `Cybersole.Ui.Views.Accounts.GroupGrid` | `/Views/Accounts/GroupGrid.axaml` |
| `Cybersole.Ui.Views.Accounts.Modals.AccountGroupView` | `/Views/Accounts/Modals/AccountGroupView.axaml` |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | `/Views/Accounts/Modals/AccountsCreatorView.axaml` |
| `Cybersole.Ui.Views.Accounts.Modals.CreateGroupModal` | `/Views/Accounts/Modals/CreateGroupModal.axaml` |

**六个，不是一个。** R70 在 GUI 里看到的正是这六个：外层页（AccountView）、账户表（AccountGrid）、
左栏分组表（GroupGrid）、Group Settings 弹窗（AccountGroupView）、Add Accounts 弹窗
（AccountsCreatorView）、Create Group 弹窗（CreateGroupModal）。replica 现在只有两个
（`AccountView` + `AccountImportWindow`），剩下四个缺。

同样的结构在 Profiles / Proxies / Tasks 上重复：`Profiles.ProfileView` + 各 Modals，
`Proxies.ProxyView` + 各 Modals，`Tasks.TaskView` + `Tasks.Modals.*`。

## 完整清单

见 `analysis\original_views.txt`（`类全名<TAB>/路径`，87 行）。

## 完整清单（87）

| 类 | axaml |
|---|---|
| Cybersole.Ui.App | /App.axaml |
| Cybersole.Ui.Views.Accounts.AccountGrid | /Views/Accounts/AccountGrid.axaml |
| Cybersole.Ui.Views.Accounts.AccountView | /Views/Accounts/AccountView.axaml |
| Cybersole.Ui.Views.Accounts.GroupGrid | /Views/Accounts/GroupGrid.axaml |
| Cybersole.Ui.Views.Accounts.Modals.AccountGroupView | /Views/Accounts/Modals/AccountGroupView.axaml |
| Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView | /Views/Accounts/Modals/AccountsCreatorView.axaml |
| Cybersole.Ui.Views.Accounts.Modals.CreateGroupModal | /Views/Accounts/Modals/CreateGroupModal.axaml |
| Cybersole.Ui.Views.Analytics.AnalyticsView | /Views/Analytics/AnalyticsView.axaml |
| Cybersole.Ui.Views.Analytics.CheckoutList | /Views/Analytics/CheckoutList.axaml |
| Cybersole.Ui.Views.Analytics.Modals.CheckoutView | /Views/Analytics/Modals/CheckoutView.axaml |
| Cybersole.Ui.Views.Analytics.Modals.ReleaseGuideView | /Views/Analytics/Modals/ReleaseGuideView.axaml |
| Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView | /Views/Analytics/Modals/ReleaseSitelistView.axaml |
| Cybersole.Ui.Views.Analytics.Modals.ReleaseView | /Views/Analytics/Modals/ReleaseView.axaml |
| Cybersole.Ui.Views.Auth.AuthWindow | /Views/Auth/AuthWindow.axaml |
| Cybersole.Ui.Views.Auth.LicenseControl | /Views/Auth/LicenseControl.axaml |
| Cybersole.Ui.Views.Auth.LoginControl | /Views/Auth/LoginControl.axaml |
| Cybersole.Ui.Views.Auth.SplashWindow | /Views/Auth/SplashWindow.axaml |
| Cybersole.Ui.Views.Browser.CustomBrowser | /Views/Browser/CustomBrowser.axaml |
| Cybersole.Ui.Views.Captcha.GoogleLogin | /Views/Captcha/GoogleLogin.axaml |
| Cybersole.Ui.Views.Captcha.SolverWindow | /Views/Captcha/SolverWindow.axaml |
| Cybersole.Ui.Views.Captcha.YoutubeWindow | /Views/Captcha/YoutubeWindow.axaml |
| Cybersole.Ui.Views.EmptyView | /Views/EmptyView.axaml |
| Cybersole.Ui.Views.MainWindow | /Views/MainWindow.axaml |
| Cybersole.Ui.Views.Modals.DesktopNotification | /Views/Modals/DesktopNotification.axaml |
| Cybersole.Ui.Views.Modals.DropdownModal | /Views/Modals/DropdownModal.axaml |
| Cybersole.Ui.Views.Modals.InputModal | /Views/Modals/InputModal.axaml |
| Cybersole.Ui.Views.Modals.MessageBoxDialog | /Views/Modals/MessageBoxDialog.axaml |
| Cybersole.Ui.Views.Modals.NotificationView | /Views/Modals/NotificationView.axaml |
| Cybersole.Ui.Views.Modals.UserView | /Views/Modals/UserView.axaml |
| Cybersole.Ui.Views.Monitor.MonitorView | /Views/Monitor/MonitorView.axaml |
| Cybersole.Ui.Views.Monitor.MonitorWindow | /Views/Monitor/MonitorWindow.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ExpressionView | /Views/Profiles/Modals/ExpressionView.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ProfileAddressView | /Views/Profiles/Modals/ProfileAddressView.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView | /Views/Profiles/Modals/ProfileAdvancedView.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView | /Views/Profiles/Modals/ProfileCreatorView.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView | /Views/Profiles/Modals/ProfileCsvEditorView.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ProfileGroupView | /Views/Profiles/Modals/ProfileGroupView.axaml |
| Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView | /Views/Profiles/Modals/ProfilePaymentView.axaml |
| Cybersole.Ui.Views.Profiles.ProfileView | /Views/Profiles/ProfileView.axaml |
| Cybersole.Ui.Views.Proxies.Modals.ProxyCreatorView | /Views/Proxies/Modals/ProxyCreatorView.axaml |
| Cybersole.Ui.Views.Proxies.Modals.ProxyGroupView | /Views/Proxies/Modals/ProxyGroupView.axaml |
| Cybersole.Ui.Views.Proxies.ProxyView | /Views/Proxies/ProxyView.axaml |
| Cybersole.Ui.Views.Settings.AppearanceView | /Views/Settings/AppearanceView.axaml |
| Cybersole.Ui.Views.Settings.CaptchaProvidersView | /Views/Settings/CaptchaProvidersView.axaml |
| Cybersole.Ui.Views.Settings.CloudflareSolversView | /Views/Settings/CloudflareSolversView.axaml |
| Cybersole.Ui.Views.Settings.CustomSizesView | /Views/Settings/CustomSizesView.axaml |
| Cybersole.Ui.Views.Settings.CustomStoresView | /Views/Settings/CustomStoresView.axaml |
| Cybersole.Ui.Views.Settings.DataView | /Views/Settings/DataView.axaml |
| Cybersole.Ui.Views.Settings.GeneralSettingsView | /Views/Settings/GeneralSettingsView.axaml |
| Cybersole.Ui.Views.Settings.GoogleAccountsView | /Views/Settings/GoogleAccountsView.axaml |
| Cybersole.Ui.Views.Settings.HelpView | /Views/Settings/HelpView.axaml |
| Cybersole.Ui.Views.Settings.ImapView | /Views/Settings/ImapView.axaml |
| Cybersole.Ui.Views.Settings.KeyBindsView | /Views/Settings/KeyBindsView.axaml |
| Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView | /Views/Settings/Modals/AycdInboxCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView | /Views/Settings/Modals/CaptchaProviderCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView | /Views/Settings/Modals/CloudflareSolverCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView | /Views/Settings/Modals/GoogleAccountEditView.axaml |
| Cybersole.Ui.Views.Settings.Modals.ImapCreatorView | /Views/Settings/Modals/ImapCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView | /Views/Settings/Modals/PayPalAccountCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.ShippingRatesCreatorView | /Views/Settings/Modals/ShippingRatesCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.SizeCreatorView | /Views/Settings/Modals/SizeCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.StoreCreatorView | /Views/Settings/Modals/StoreCreatorView.axaml |
| Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView | /Views/Settings/Modals/WebhookCreatorView.axaml |
| Cybersole.Ui.Views.Settings.NotificationsView | /Views/Settings/NotificationsView.axaml |
| Cybersole.Ui.Views.Settings.PaymentView | /Views/Settings/PaymentView.axaml |
| Cybersole.Ui.Views.Settings.PayPalAccountsView | /Views/Settings/PayPalAccountsView.axaml |
| Cybersole.Ui.Views.Settings.SettingsView | /Views/Settings/SettingsView.axaml |
| Cybersole.Ui.Views.Settings.WebhookView | /Views/Settings/WebhookView.axaml |
| Cybersole.Ui.Views.SmartActions.ActionsModal | /Views/SmartActions/ActionsModal.axaml |
| Cybersole.Ui.Views.SmartActions.HistoryWindow | /Views/SmartActions/HistoryWindow.axaml |
| Cybersole.Ui.Views.SmartActions.PublishTemplateModal | /Views/SmartActions/PublishTemplateModal.axaml |
| Cybersole.Ui.Views.SmartActions.SmartActionsCreator | /Views/SmartActions/SmartActionsCreator.axaml |
| Cybersole.Ui.Views.SmartActions.SmartActionSettings | /Views/SmartActions/SmartActionSettings.axaml |
| Cybersole.Ui.Views.SmartActions.SmartActionsView | /Views/SmartActions/SmartActionsView.axaml |
| Cybersole.Ui.Views.SmartActions.TemplateView | /Views/SmartActions/TemplateView.axaml |
| Cybersole.Ui.Views.Tasks.Modals.GroupSummary | /Views/Tasks/Modals/GroupSummary.axaml |
| Cybersole.Ui.Views.Tasks.Modals.StaggerStartView | /Views/Tasks/Modals/StaggerStartView.axaml |
| Cybersole.Ui.Views.Tasks.Modals.TaskDetailsView | /Views/Tasks/Modals/TaskDetailsView.axaml |
| Cybersole.Ui.Views.Tasks.Modals.TaskGroupListView | /Views/Tasks/Modals/TaskGroupListView.axaml |
| Cybersole.Ui.Views.Tasks.Modals.TaskGroupView | /Views/Tasks/Modals/TaskGroupView.axaml |
| Cybersole.Ui.Views.Tasks.TaskCreatorAdvancedView | /Views/Tasks/TaskCreatorAdvancedView.axaml |
| Cybersole.Ui.Views.Tasks.TaskCreatorCartView | /Views/Tasks/TaskCreatorCartView.axaml |
| Cybersole.Ui.Views.Tasks.TaskCreatorMainView | /Views/Tasks/TaskCreatorMainView.axaml |
| Cybersole.Ui.Views.Tasks.TaskCreatorView | /Views/Tasks/TaskCreatorView.axaml |
| Cybersole.Ui.Views.Tasks.TaskView | /Views/Tasks/TaskView.axaml |
| Cybersole.Ui.Views.Utilities.StoreGroupModal | /Views/Utilities/StoreGroupModal.axaml |
| Cybersole.Ui.Views.Utilities.UtilitiesView | /Views/Utilities/UtilitiesView.axaml |
