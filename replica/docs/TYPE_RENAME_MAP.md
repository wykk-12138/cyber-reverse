# 类型改名候选图（生成文件，请勿手改）

> 由 `python tools/type_rename_map.py` 生成。用途：把 `bind_diff.py --type-presence` 列出的
> ABSENT 类型逐条变成**可审阅的候选**，再由人工在 `replica/docs/BINDING_BACKLOG.md` 里判
> RENAMED / UNIMPLEMENTED。**候选不是结论** —— 两个无关类可能共享成员名（`Name`/`Type` 尤其）。

| 项 | 值 |
|---|---|
| 绑定表类型 | 174 |
| 源码里存在的同名类型 | 119 |
| ABSENT（本次审阅对象） | 55 |
| 其中有 HIGH 候选 | 17 |
| 其中有 MEDIUM 候选 | 32 |
| 完全没有候选 | 3 |

## 逐条候选

### `Cybersole.Attributes.CreateInfo`  (2 members: Name, Properties)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `BotTask` | 2/2 |  |
| HIGH | `CaptchaProviderCreatorView` | 2/2 |  |
| HIGH | `ChromiumBridge` | 2/2 |  |

### `Cybersole.Attributes.Platform`  (5 members: InputType, MultiCart, Name, QuantityAutoAdjustSupport, QuantitySupport)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| LOW | `TaskCombinationBuilder` | 2/5 |  |
| LOW | `TaskCombinationRequest` | 2/5 |  |
| LOW | `TaskCreatorView` | 2/5 |  |

### `Cybersole.CloudflareSolvers.CloudflareSolver`  (9 members: ApiKey, Balance, BalanceSupported, Concurrency, Count, Id, IsFetchingBalance, Name, Type)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `CaptchaProvider` | 9/9 |  |
| MEDIUM | `CaptchaProviderConfig` | 8/9 |  |
| MEDIUM | `CaptchaProvidersView` | 8/9 |  |

### `Cybersole.Global.Settings`  (34 members: AutoOpen3DS, AutoOpen3DSLimit, BackupInterval, BetaUpdates, BrowserLimit, BrowserPath, BrowserProfileAssignment, BrowserWindowMode, Clock, Currency, Keybinds, Language, MaxBackups, MaxLogRetention, MaxLogSize, MonitorConcurrency, MonitorDelay, MonitorFilters, Notifications, PinGroups, ProfileGroupOrder, ProxyGroupOrder, QueuePresentation, QuickTaskProfiles, QuickTaskProxies, RetryDelay, ScrollbarColor, ScrollbarCornerRadius, ScrollbarWidth, ShopifyBrowserProxy, SmartActions, StartupPage, TaskGroupOrder, Timeout)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `GlobalSettings` | 33/34 |  |
| LOW | `GeneralSettingsView` | 12/34 |  |
| LOW | `SettingsShell` | 7/34 | 是 |

### `Cybersole.Helpers.BrowserProfile`  (1 members: DisplayName)

**无候选** —— 没有任何类持有这些成员名。按 UNIMPLEMENTED 处理前仍需读一遍绑定串上下文。

### `Cybersole.Helpers.ObservableDictionary`2`  (1 members: Count)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AccountGrid` | 1/1 |  |
| MEDIUM | `AccountImportWindow` | 1/1 |  |
| MEDIUM | `AccountMoveView` | 1/1 |  |

### `Cybersole.KeyInput.KeyGesture`  (2 members: Key, Modifiers)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `BillingKeyBinds` | 2/2 |  |
| HIGH | `KeyBind` | 2/2 |  |
| HIGH | `KeyBindMatcher` | 2/2 |  |

### `Cybersole.Models.Analytics`  (2 members: Spent, Success)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `AnalyticsView` | 2/2 | 是 |
| HIGH | `Checkout` | 2/2 |  |
| HIGH | `CheckoutStats` | 2/2 |  |

### `Cybersole.Models.AycdInboxAccount`  (5 members: ApiKey, Enabled, Error, Status, TaskCount)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `CaptchaProvidersView` | 3/5 |  |
| MEDIUM | `CloudflareSolversView` | 3/5 |  |
| MEDIUM | `ImapView` | 3/5 |  |

### `Cybersole.Models.Captcha`  (1 members: Proxy)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AdvancedView` | 1/1 |  |
| MEDIUM | `BouncyH2Client` | 1/1 |  |
| MEDIUM | `BouncyHttpClient` | 1/1 |  |

### `Cybersole.Models.Concurrency`  (3 members: Maximum, Mode, Ratio)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `ConcurrencySettings` | 3/3 |  |
| HIGH | `GeneralSettingsView` | 3/3 |  |
| MEDIUM | `ConcurrencyMode` | 2/3 |  |

### `Cybersole.Models.CreateInputModel`  (13 members: AutoQuantity, Color, Currency, Input, MaxPrice, MinPrice, Minus, Plus, PriceCheckVisible, Quantity, Sizes, Symbol, TogglePriceCheck)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `Product` | 7/13 |  |
| MEDIUM | `TaskCreatorView` | 7/13 |  |
| LOW | `TaskEditorWindow` | 4/13 |  |

### `Cybersole.Models.EditValue`1`  (14 members: HasMultiple, HasMultiple_101, HasMultiple_87, HasMultiple_88, HasMultiple_91, HasMultiple_93, HasMultiple_94, HasMultiple_95, HasMultiple_97, HasMultiple_98, HasMultiple_99, Value, Value_100, Value_92)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| LOW | `AnalyticsView` | 1/14 |  |
| LOW | `BouncyH2Client` | 1/14 |  |
| LOW | `BouncyHttpClient` | 1/14 |  |

### `Cybersole.Models.Notification`  (4 members: Message, Timestamp, Title, Type)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `MonitorEvent` | 3/4 |  |
| MEDIUM | `MonitorView` | 3/4 |  |
| MEDIUM | `AccountGrid` | 2/4 |  |

### `Cybersole.Models.NotificationSound`  (1 members: SoundLocation)

**无候选** —— 没有任何类持有这些成员名。按 UNIMPLEMENTED 处理前仍需读一遍绑定串上下文。

### `Cybersole.Models.ProfileItem`  (2 members: Description, Name)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `PublishTemplateModal` | 2/2 |  |
| HIGH | `StepAction` | 2/2 |  |
| HIGH | `StepActionRegistry` | 2/2 |  |

### `Cybersole.Models.RemoteData`  (1 members: Name)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `Account` | 1/1 |  |
| MEDIUM | `AccountGroup` | 1/1 |  |
| MEDIUM | `AccountGroupView` | 1/1 |  |

### `Cybersole.Models.Size`  (1 members: Value)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AnalyticsView` | 1/1 |  |
| MEDIUM | `BouncyH2Client` | 1/1 |  |
| MEDIUM | `BouncyHttpClient` | 1/1 |  |

### `Cybersole.Models.Store`  (6 members: ColorSupport, Currency, Elements, Info, Name, Url)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `CustomStore` | 3/6 |  |
| MEDIUM | `CustomStoresView` | 3/6 |  |
| MEDIUM | `StoreCreatorView` | 3/6 |  |

### `Cybersole.Models.User`  (6 members: Discord, Email, FirstName, Image, IsStaff, LastName)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `BillingView` | 3/6 |  |
| MEDIUM | `CheckoutFormBuilder` | 3/6 |  |
| MEDIUM | `CustomBrowserWindow` | 3/6 |  |

### `Cybersole.Models.ValueGroup`  (3 members: Name, Preview, Values)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `ActionsModal` | 2/3 |  |
| MEDIUM | `NetClient` | 2/3 |  |
| MEDIUM | `ProfileCsvEditorView` | 2/3 |  |

### `Cybersole.Providers.IDataProvider`  (1 members: Name)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `Account` | 1/1 |  |
| MEDIUM | `AccountGroup` | 1/1 |  |
| MEDIUM | `AccountGroupView` | 1/1 |  |

### `Cybersole.Services.ImapProvider`  (4 members: Host, MessageCount, Status, Username)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `ImapMailProvider` | 4/4 |  |
| HIGH | `ImapView` | 2/4 | 是 |
| MEDIUM | `Proxy` | 3/4 |  |

### `Cybersole.SmartActions.Action`  (5 members: Config, Description, Image, Name, Variables)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `PublishTemplateModal` | 3/5 |  |
| MEDIUM | `TaskView` | 3/5 |  |
| LOW | `BillingView` | 2/5 |  |

### `Cybersole.SmartActions.ActionConfig`  (2 members: Name, Required)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `SmartActionStep` | 2/2 |  |
| HIGH | `SmartActionStepConfig` | 2/2 |  |
| HIGH | `SmartActionsCreator` | 2/2 |  |

### `Cybersole.SmartActions.ActionParams`  (1 members: Action)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AccountGrid` | 1/1 |  |
| MEDIUM | `AccountGroupView` | 1/1 |  |
| MEDIUM | `AccountImportWindow` | 1/1 |  |

### `Cybersole.SmartActions.Filter`  (4 members: Behaviour, Inputs, Operator, Variable)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `SmartActionFilter` | 3/4 |  |
| MEDIUM | `SmartActionsCreator` | 3/4 |  |
| MEDIUM | `FilterRow` | 2/4 |  |

### `Cybersole.SmartActions.Operator`  (1 members: Name)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `Account` | 1/1 |  |
| MEDIUM | `AccountGroup` | 1/1 |  |
| MEDIUM | `AccountGroupView` | 1/1 |  |

### `Cybersole.SmartActions.RunHistory`  (4 members: Exception, Result, Timestamp, Trigger)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `SmartActionsCreator` | 3/4 |  |
| MEDIUM | `BouncyTls` | 2/4 |  |
| MEDIUM | `CasioModule` | 2/4 |  |

### `Cybersole.SmartActions.Template`  (5 members: Actions, Description, Filters, Title, Trigger)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `ActionsModal` | 4/5 |  |
| MEDIUM | `SmartActionsCreator` | 4/5 |  |
| MEDIUM | `SmartActionsView` | 4/5 |  |

### `Cybersole.SmartActions.Trigger`  (4 members: Description, Image, Name, Variables)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `BotTask` | 2/4 |  |
| MEDIUM | `Product` | 2/4 |  |
| MEDIUM | `PublishTemplateModal` | 2/4 |  |

### `Cybersole.SmartActions.Variable`  (1 members: Description)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `ExpressionExample` | 1/1 |  |
| MEDIUM | `ExpressionView` | 1/1 |  |
| MEDIUM | `PublishTemplateModal` | 1/1 |  |

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

### `Cybersole.Ui.Localization.LocalizeEnumExtension`  (1 members: Value)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AnalyticsView` | 1/1 |  |
| MEDIUM | `BouncyH2Client` | 1/1 |  |
| MEDIUM | `BouncyHttpClient` | 1/1 |  |

### `Cybersole.Ui.Localization.LocalizeFallbackExtension`  (1 members: Value)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AnalyticsView` | 1/1 |  |
| MEDIUM | `BouncyH2Client` | 1/1 |  |
| MEDIUM | `BouncyHttpClient` | 1/1 |  |

### `Cybersole.Ui.Localization.LocalizeFormatExtension`  (2 members: Value, Value2)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AnalyticsView` | 1/2 |  |
| MEDIUM | `BouncyH2Client` | 1/2 |  |
| MEDIUM | `BouncyHttpClient` | 1/2 |  |

### `Cybersole.Ui.Localization.LocalizeSwitchExtension`  (1 members: Condition)

**无候选** —— 没有任何类持有这些成员名。按 UNIMPLEMENTED 处理前仍需读一遍绑定串上下文。

### `Cybersole.Ui.Views.Accounts.AccountStoreEntry`  (2 members: IsSelected, Name)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `Account` | 1/2 |  |
| MEDIUM | `AccountGroup` | 1/2 |  |
| MEDIUM | `AccountGroupView` | 1/2 |  |

### `Cybersole.Ui.Views.Accounts.AccountStoreType`  (2 members: Stores, Type)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `CustomBrowser` | 2/2 |  |
| HIGH | `Drop` | 2/2 |  |
| HIGH | `ReleaseSitelistView` | 2/2 |  |

### `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView`  (2 members: Add, Close)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `AccountImportWindow` | 2/2 |  |
| HIGH | `AccountMoveView` | 2/2 |  |
| HIGH | `ActionsModal` | 2/2 |  |

### `Cybersole.Ui.Views.Analytics.Modals.CheckoutProperty`  (2 members: Key, Value)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `AnalyticsView` | 2/2 |  |
| HIGH | `BouncyH2Client` | 2/2 |  |
| HIGH | `ChromiumKasadaSolver` | 2/2 |  |

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

### `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView`  (1 members: Profile)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AdvancedView` | 1/1 |  |
| MEDIUM | `BaseCheckout` | 1/1 |  |
| MEDIUM | `BillingGroup` | 1/1 |  |

### `Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView`  (1 members: Profile)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AdvancedView` | 1/1 |  |
| MEDIUM | `BaseCheckout` | 1/1 |  |
| MEDIUM | `BillingGroup` | 1/1 |  |

### `Cybersole.Ui.Views.Settings.ErrorEntry`  (2 members: Key, Value)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `AnalyticsView` | 2/2 |  |
| HIGH | `BouncyH2Client` | 2/2 |  |
| HIGH | `ChromiumKasadaSolver` | 2/2 |  |

### `Cybersole.Ui.Views.Settings.KeyBindSection`  (2 members: Key, Shortcuts)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `KeyBindsView` | 2/2 |  |
| HIGH | `TaskKeyBinds` | 2/2 |  |
| MEDIUM | `AnalyticsView` | 1/2 |  |

### `Cybersole.Ui.Views.Settings.LocalizedOption`  (2 members: Text, Value)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `AnalyticsView` | 2/2 |  |
| HIGH | `BouncyHttpClient` | 2/2 |  |
| HIGH | `ChromiumBridge` | 2/2 |  |

### `Cybersole.Ui.Views.Settings.Modals.SizeOption`  (2 members: Selected, Title)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `SmartActionsView` | 2/2 |  |
| HIGH | `TaskView` | 2/2 |  |
| HIGH | `UtilitiesView` | 2/2 |  |

### `Cybersole.Ui.Views.Settings.SettingsView`  (19 members: AppearanceView, CaptchaProvidersView, CloudflareSolversView, CustomSizesView, CustomStoresView, DataView, GeneralSettingsView, GoogleAccountsView, HelpView, ImapView, KeyBindsView, LogOut, NotificationsView, PayPalAccountsView, PaymentView, Transition, Update, Version, WebhookView)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| HIGH | `SettingsShell` | 17/19 | 是 |
| LOW | `AnalyticsView` | 1/19 |  |
| LOW | `AntiBotVendors` | 1/19 |  |

### `Cybersole.Ui.Views.SmartActions.ActionConfigEntry`  (3 members: Config, Key, Parameters)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `CloudflareSolversView` | 2/3 |  |
| MEDIUM | `Ecdhe` | 2/3 |  |
| MEDIUM | `KeyBindsView` | 2/3 |  |

### `Cybersole.Ui.Views.SmartActions.TemplateGroup`  (2 members: Key, Templates)

| 级别 | 候选类 | 命中 | 同名干 |
|---|---|---|---|
| MEDIUM | `AnalyticsView` | 1/2 |  |
| MEDIUM | `AycdInboxClient` | 1/2 |  |
| MEDIUM | `BillingKeyBinds` | 1/2 |  |

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

