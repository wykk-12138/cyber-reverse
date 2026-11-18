# 类型改名候选图（生成文件，请勿手改）

> 由 `python tools/type_rename_map.py` 生成。用途：把 `bind_diff.py --type-presence` 列出的
> ABSENT 类型逐条变成**可审阅的候选**，再由人工在 `replica/docs/BINDING_BACKLOG.md` 里判
> RENAMED / UNIMPLEMENTED。**候选不是结论** —— 两个无关类可能共享成员名（`Name`/`Type` 尤其）。

| 项 | 值 |
|---|---|
| 绑定表类型 | 174 |
| 源码里存在的同名类型 | 154 |
| ABSENT（本次审阅对象） | 20 |
| 其中有 HIGH 候选 | 9 |
| 其中有 MEDIUM 候选 | 5 |
| 完全没有候选 | 0 |

## 逐条候选

### `Cybersole.CloudflareSolvers.CloudflareSolver`  (9 members: ApiKey, Balance, BalanceSupported, Concurrency, Count, Id, IsFetchingBalance, Name, Type)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `CaptchaProvider` | 9/9 |  |
| HIGH | `CloudflareSolverConfig` | 9/9 |  |
| MEDIUM | `CaptchaProviderConfig` | 8/9 |  |

### `Cybersole.Global.Settings`  (34 members: AutoOpen3DS, AutoOpen3DSLimit, BackupInterval, BetaUpdates, BrowserLimit, BrowserPath, BrowserProfileAssignment, BrowserWindowMode, Clock, Currency, Keybinds, Language, MaxBackups, MaxLogRetention, MaxLogSize, MonitorConcurrency, MonitorDelay, MonitorFilters, Notifications, PinGroups, ProfileGroupOrder, ProxyGroupOrder, QueuePresentation, QuickTaskProfiles, QuickTaskProxies, RetryDelay, ScrollbarColor, ScrollbarCornerRadius, ScrollbarWidth, ShopifyBrowserProxy, SmartActions, StartupPage, TaskGroupOrder, Timeout)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `GlobalSettings` | 34/34 |  |
| LOW | `GeneralSettingsView` | 12/34 |  |
| LOW | `SettingsShell` | 9/34 | 是 |

### `Cybersole.Helpers.ObservableDictionary`2`  (1 members: Count)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AccountGrid` | 1/1 |  |
| MEDIUM | `AccountImportWindow` | 1/1 |  |
| MEDIUM | `AccountMoveView` | 1/1 |  |

### `Cybersole.Models.Concurrency`  (3 members: Maximum, Mode, Ratio)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `ConcurrencySettings` | 3/3 |  |
| HIGH | `GeneralSettingsView` | 3/3 |  |
| MEDIUM | `ConcurrencyLimit` | 2/3 |  |

### `Cybersole.Models.EditValue`1`  (14 members: HasMultiple, HasMultiple_101, HasMultiple_87, HasMultiple_88, HasMultiple_91, HasMultiple_93, HasMultiple_94, HasMultiple_95, HasMultiple_97, HasMultiple_98, HasMultiple_99, Value, Value_100, Value_92)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| LOW | `AnalyticsView` | 1/14 |  |
| LOW | `AstroSurface` | 1/14 |  |
| LOW | `BouncyH2Client` | 1/14 |  |

### `Cybersole.Models.Notification`  (4 members: Message, Timestamp, Title, Type)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `NotificationService` | 4/4 |  |
| MEDIUM | `MonitorEvent` | 3/4 |  |
| MEDIUM | `MonitorView` | 3/4 |  |

### `Cybersole.Services.ImapProvider`  (4 members: Host, MessageCount, Status, Username)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `ImapMailProvider` | 4/4 |  |
| HIGH | `ImapView` | 2/4 | 是 |
| MEDIUM | `Proxy` | 3/4 |  |

### `Cybersole.SmartActions.ActionConfig`  (2 members: Name, Required)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `SmartActionStep` | 2/2 |  |
| HIGH | `SmartActionStepConfig` | 2/2 |  |
| HIGH | `SmartActionsCreator` | 2/2 |  |

### `Cybersole.Ui.Controls.ComboBoxGroupHeader`  (1 members: Name)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `Account` | 1/1 |  |
| MEDIUM | `AccountGroup` | 1/1 |  |
| MEDIUM | `AccountGroupView` | 1/1 |  |

### `Cybersole.Ui.Controls.ComboBoxToken`  (1 members: Text)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AccountGrid` | 1/1 |  |
| MEDIUM | `AccountGroupView` | 1/1 |  |
| MEDIUM | `AccountImportWindow` | 1/1 |  |

### `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView`  (2 members: Add, Close)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `AccountImportWindow` | 2/2 |  |
| HIGH | `AccountMoveView` | 2/2 |  |
| HIGH | `ActionsModal` | 2/2 |  |

### `Cybersole.Ui.Views.Auth.AuthWindow`  (3 members: Exit, Logout, Minimise)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `CustomBrowser` | 2/3 |  |
| MEDIUM | `CustomBrowserWindow` | 2/3 |  |
| MEDIUM | `HistoryWindow` | 2/3 |  |

### `Cybersole.Ui.Views.Auth.LicenseControl`  (3 members: Authenticate, Dashboard, Refresh)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| LOW | `BillingView` | 1/3 |  |
| LOW | `CaptchaProvidersView` | 1/3 |  |
| LOW | `CheckoutList` | 1/3 |  |

### `Cybersole.Ui.Views.Settings.SettingsView`  (19 members: AppearanceView, CaptchaProvidersView, CloudflareSolversView, CustomSizesView, CustomStoresView, DataView, GeneralSettingsView, GoogleAccountsView, HelpView, ImapView, KeyBindsView, LogOut, NotificationsView, PayPalAccountsView, PaymentView, Transition, Update, Version, WebhookView)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `SettingsShell` | 18/19 | 是 |
| LOW | `AnalyticsView` | 1/19 |  |
| LOW | `AntiBotVendors` | 1/19 |  |

### `Cybersole.Ui.Views.Tasks.TaskCreatorCartView`  (3 members: Add, Delete, SizeItems)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AccountGrid` | 2/3 |  |
| MEDIUM | `AccountView` | 2/3 |  |
| MEDIUM | `BillingKeyBinds` | 2/3 |  |

### `Cybersole.Ui.Views.Tasks.TaskCreatorMainView`  (4 members: ProfileGroupItems, ProfileItems, ShowCartView, SizeItems)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `TaskCreatorView` | 4/4 |  |
| LOW | `GeneralSettingsView` | 1/4 |  |

