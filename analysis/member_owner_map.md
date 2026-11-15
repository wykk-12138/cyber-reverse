# 每个 ABSENT 成员的归属类（生成文件，请勿手改）

> 由 `python tools/member_owner_map.py` 生成。**成员级**问题：这个成员名在哪些类的 body 里出现？
> 用途：把 B/C 组里"判不了"的条目分成三类 —— 唯一归属（改名/合并）、归属过多（通用词，无信息）、
> 零归属（真缺）。Body 提取规则与 `bind_scope.py` 相同。

## `Cybersole.Attributes.CreateInfo`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Properties` | `AccountGrid`、`BaseCheckout`、`BotTask`、`CaptchaProviderCreatorView`、`CheckoutView`、`LocalizationService` …共 9 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Attributes.Platform`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `InputType` | （无） | **零归属 — 真缺候选** |
| `MultiCart` | `TaskCombinationBuilder`、`TaskCombinationRequest`、`TaskCreatorView` | 归属过多 → 通用词，无信息 |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `QuantityAutoAdjustSupport` | （无） | **零归属 — 真缺候选** |
| `QuantitySupport` | （无） | **零归属 — 真缺候选** |

## `Cybersole.CloudflareSolvers.CloudflareSolver`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `ApiKey` | `AycdInbox`、`AycdInboxClient`、`AycdInboxCreatorView`、`CaptchaProvider`、`CaptchaProviderConfig`、`CaptchaProviderCreatorView` …共 21 个 | 归属过多 → 通用词，无信息 |
| `Balance` | `CaptchaProvider`、`CaptchaProviderConfig`、`CaptchaProvidersView`、`CloudflareSolverConfig`、`CloudflareSolversView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `BalanceSupported` | `AycdCaptchaDriver`、`CaptchaProvider`、`CaptchaProviderConfig`、`CaptchaProviderCreatorView`、`CaptchaProvidersView`、`CfSolverDriver` …共 14 个 | 归属过多 → 通用词，无信息 |
| `Concurrency` | `CaptchaProvider`、`CaptchaProviderConfig`、`CaptchaProviderCreatorView`、`CaptchaProvidersView`、`CaptchaSolverService`、`CloudflareSolverConfig` …共 11 个 | 归属过多 → 通用词，无信息 |
| `Count` | `AccountGrid`、`AccountImportWindow`、`AccountMoveView`、`AccountTable`、`AccountView`、`ActionsModal` …共 126 个 | 归属过多 → 通用词，无信息 |
| `Id` | `Account`、`AccountGroup`、`AccountImportWindow`、`AccountMoveView`、`AccountView`、`AdyenGateway` …共 113 个 | 归属过多 → 通用词，无信息 |
| `IsFetchingBalance` | `CaptchaProvider`、`CaptchaProviderConfig`、`CaptchaProvidersView`、`CaptchaSolverService` | 归属过多 → 通用词，无信息 |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Type` | `AccountGroup`、`AccountView`、`AntiCaptchaDriver`、`AycdCaptchaDriver`、`BaseCheckout`、`CapMonsterDriver` …共 45 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Global.Settings`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `AutoOpen3DS` | `GlobalSettings`、`MainWindow`、`PaymentView` | 归属过多 → 通用词，无信息 |
| `AutoOpen3DSLimit` | `GlobalSettings`、`MainWindow`、`PaymentView` | 归属过多 → 通用词，无信息 |
| `BackupInterval` | `AppServices`、`DataView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `BetaUpdates` | `AdvancedView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `BrowserLimit` | `GlobalSettings`、`PaymentView` | 归属过多 → 通用词，无信息 |
| `BrowserPath` | `GlobalSettings`、`PaymentView` | 归属过多 → 通用词，无信息 |
| `BrowserProfileAssignment` | `GlobalSettings`、`PaymentView` | 归属过多 → 通用词，无信息 |
| `BrowserWindowMode` | `GlobalSettings`、`PaymentView` | 归属过多 → 通用词，无信息 |
| `Clock` | `AppServices`、`ClockService`、`GeneralSettingsView`、`GlobalSettings`、`MainWindow`、`NotificationView` …共 7 个 | 归属过多 → 通用词，无信息 |
| `Currency` | `Checkout`、`CustomStore`、`CustomStoresView`、`GeneralSettingsView`、`GlobalSettings`、`StoreCreatorView` | 归属过多 → 通用词，无信息 |
| `Keybinds` | `GlobalSettings`、`KeyBindsView` | 归属过多 → 通用词，无信息 |
| `Language` | `App`、`BouncyHttpClient`、`BrowserShim`、`ChromiumBridge`、`GeneralSettingsView`、`GlobalSettings` …共 10 个 | 归属过多 → 通用词，无信息 |
| `MaxBackups` | `DataView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `MaxLogRetention` | `AppServices`、`DataView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `MaxLogSize` | `AppServices`、`DataView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `MonitorConcurrency` | `GlobalSettings` | 唯一归属 → 改名/合并 |
| `MonitorDelay` | `BotTask`、`CreateModel`、`GeneralSettingsView`、`GlobalSettings`、`GroupSummary`、`MainViewModel` …共 16 个 | 归属过多 → 通用词，无信息 |
| `MonitorFilters` | `GlobalSettings`、`MonitorFilterPolicy`、`MonitorView`、`TaskEngine` | 归属过多 → 通用词，无信息 |
| `Notifications` | `GlobalSettings`、`NotificationService`、`NotificationView`、`NotificationsView`、`SettingsShell`、`SmartAction` …共 9 个 | 归属过多 → 通用词，无信息 |
| `PinGroups` | `AdvancedView`、`GlobalSettings`、`TaskView` | 归属过多 → 通用词，无信息 |
| `ProfileGroupOrder` | `AdvancedView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `ProxyGroupOrder` | `AdvancedView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `QueuePresentation` | `GeneralSettingsView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `QuickTaskProfiles` | `GeneralSettingsView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `QuickTaskProxies` | `GeneralSettingsView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `RetryDelay` | `BotTask`、`CreateModel`、`GeneralSettingsView`、`GlobalSettings`、`GroupSummary`、`MainViewModel` …共 16 个 | 归属过多 → 通用词，无信息 |
| `ScrollbarColor` | `AppearanceView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `ScrollbarCornerRadius` | `AppearanceView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `ScrollbarWidth` | `AppearanceView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `ShopifyBrowserProxy` | `GeneralSettingsView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `SmartActions` | `AppPaths`、`AppServices`、`BackupDocument`、`HistoryWindow`、`MonitorWindow`、`PublishTemplateModal` …共 12 个 | 归属过多 → 通用词，无信息 |
| `StartupPage` | `GeneralSettingsView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `TaskGroupOrder` | `AdvancedView`、`GlobalSettings` | 归属过多 → 通用词，无信息 |
| `Timeout` | `AycdInboxClient`、`AycdInboxCreatorView`、`BotTask`、`CaptchaSolverService`、`ClockService`、`CreateModel` …共 32 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Helpers.BrowserProfile`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `DisplayName` | （无） | **零归属 — 真缺候选** |

## `Cybersole.Helpers.ObservableDictionary`2`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Count` | `AccountGrid`、`AccountImportWindow`、`AccountMoveView`、`AccountTable`、`AccountView`、`ActionsModal` …共 126 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.KeyInput.KeyGesture`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Key` | `AnalyticsView`、`AycdInboxClient`、`BillingKeyBinds`、`BouncyH2Client`、`CatalogValidator`、`CheckoutStats` …共 40 个 | 归属过多 → 通用词，无信息 |
| `Modifiers` | `BillingKeyBinds`、`KeyBind`、`KeyBindMatcher`、`KeyBindsView`、`MainWindow`、`ProxyKeyBinds` …共 7 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.Analytics`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Spent` | `AnalyticsView`、`Checkout`、`CheckoutStats`、`MainWindow` | 归属过多 → 通用词，无信息 |
| `Success` | `AdyenGateway`、`AnalyticsView`、`AycdInboxClient`、`BouncyHttpClient`、`BstnFlow`、`CasioFlow` …共 89 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.AycdInboxAccount`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `ApiKey` | `AycdInbox`、`AycdInboxClient`、`AycdInboxCreatorView`、`CaptchaProvider`、`CaptchaProviderConfig`、`CaptchaProviderCreatorView` …共 21 个 | 归属过多 → 通用词，无信息 |
| `Enabled` | `Account`、`ActionsModal`、`AycdInbox`、`AycdInboxCreatorView`、`BotTask`、`CaptchaProvider` …共 34 个 | 归属过多 → 通用词，无信息 |
| `Error` | `AccessorBrandCheck`、`AycdCaptchaDriver`、`AycdInboxClient`、`BouncyH2Client`、`BouncyHttpClient`、`CaptchaSolverService` …共 72 个 | 归属过多 → 通用词，无信息 |
| `Status` | `AdvancedView`、`AnalyticsView`、`AppearanceView`、`BillingView`、`BotTask`、`BouncyHttpClient` …共 101 个 | 归属过多 → 通用词，无信息 |
| `TaskCount` | （无） | **零归属 — 真缺候选** |

## `Cybersole.Models.Captcha`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Proxy` | `AdvancedView`、`BouncyH2Client`、`BouncyHttpClient`、`BouncyTls`、`CaptchaChallenge`、`CaptchaSolverService` …共 79 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.Concurrency`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Maximum` | `ConcurrencyMode`、`ConcurrencySettings`、`DataView`、`GeneralSettingsView`、`PaymentView`、`SettingsShell` …共 7 个 | 归属过多 → 通用词，无信息 |
| `Mode` | `ApiKasadaSolver`、`CaptchaProviderCreatorView`、`CloudflareSolverCreatorView`、`CloudflareStrategy`、`CloudflareStrategyRunner`、`ConcurrencySettings` …共 21 个 | 归属过多 → 通用词，无信息 |
| `Ratio` | `ConcurrencyMode`、`ConcurrencySettings`、`GeneralSettingsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.CreateInputModel`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `AutoQuantity` | `TaskCombinationRequest` | 唯一归属 → 改名/合并 |
| `Color` | `AccountGrid`、`AccountGroupView`、`AccountTable`、`AccountView`、`AppearanceView`、`CustomBrowser` …共 21 个 | 归属过多 → 通用词，无信息 |
| `Currency` | `Checkout`、`CustomStore`、`CustomStoresView`、`GeneralSettingsView`、`GlobalSettings`、`StoreCreatorView` | 归属过多 → 通用词，无信息 |
| `Input` | `BotTask`、`ComboBoxEdit`、`FilterInputEntry`、`FilterRow`、`KeyBindsView`、`MainWindow` …共 13 个 | 归属过多 → 通用词，无信息 |
| `MaxPrice` | `Product` | 唯一归属 → 改名/合并 |
| `MinPrice` | `Product`、`SmartAction`、`SmartActionEditorWindow`、`SmartActionEngine`、`SmartActionsCreator`、`SmartActionsView` | 归属过多 → 通用词，无信息 |
| `Minus` | `TaskCreatorView` | 唯一归属 → 改名/合并 |
| `Plus` | `TaskCreatorView` | 唯一归属 → 改名/合并 |
| `PriceCheckVisible` | `TaskCreatorView` | 唯一归属 → 改名/合并 |
| `Quantity` | `BotTask`、`CasioFlow`、`CreateModel`、`FanaticsFlow`、`FlowSession`、`FootsitesFlow` …共 16 个 | 归属过多 → 通用词，无信息 |
| `Sizes` | `BotTask`、`CasioModule`、`CustomSizesView`、`EndClothingModule`、`FanaticsModule`、`FarfetchFlow` …共 42 个 | 归属过多 → 通用词，无信息 |
| `Symbol` | `CssStyleProperties`、`GlobalSurface`、`KeyOrderTable`、`NavPrune`、`WindowNameTable` | 归属过多 → 通用词，无信息 |
| `TogglePriceCheck` | `TaskCreatorView` | 唯一归属 → 改名/合并 |

## `Cybersole.Models.NotificationSound`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `SoundLocation` | （无） | **零归属 — 真缺候选** |

## `Cybersole.Models.ProfileItem`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Description` | `ExpressionExample`、`ExpressionView`、`PublishTemplateModal`、`PublishedTemplate`、`StepAction`、`StepActionRegistry` | 归属过多 → 通用词，无信息 |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.RemoteData`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.Size`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.Store`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `ColorSupport` | （无） | **零归属 — 真缺候选** |
| `Currency` | `Checkout`、`CustomStore`、`CustomStoresView`、`GeneralSettingsView`、`GlobalSettings`、`StoreCreatorView` | 归属过多 → 通用词，无信息 |
| `Elements` | （无） | **零归属 — 真缺候选** |
| `Info` | `AppServices`、`AuthService`、`ClockService`、`EventBus`、`LogLevel`、`MainWindow` …共 15 个 | 归属过多 → 通用词，无信息 |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Url` | `AdyenGateway`、`BotTask`、`BouncyHttpClient`、`BstnFlow`、`CasioFlow`、`CasioModule` …共 89 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.User`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Discord` | `WebhookCreatorView` | 唯一归属 → 改名/合并 |
| `Email` | `Account`、`AccountColumn`、`AccountGrid`、`AccountImportWindow`、`AccountView`、`AuthService` …共 46 个 | 归属过多 → 通用词，无信息 |
| `FirstName` | `Address`、`BillingView`、`CheckoutFormBuilder`、`CustomBrowserWindow`、`FootsitesFlow`、`JohnLewisFlow` …共 14 个 | 归属过多 → 通用词，无信息 |
| `Image` | `BaseCheckout`、`BotTask`、`CanvasSurface`、`MonitorProduct`、`MonitorResult`、`Product` …共 12 个 | 归属过多 → 通用词，无信息 |
| `IsStaff` | （无） | **零归属 — 真缺候选** |
| `LastName` | `Address`、`BillingView`、`CheckoutFormBuilder`、`CustomBrowserWindow`、`FootsitesFlow`、`JohnLewisFlow` …共 14 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Models.ValueGroup`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Preview` | `ActionsModal`、`ProfileCsvEditorView` | 归属过多 → 通用词，无信息 |
| `Values` | `CaptchaProviderRegistry`、`JohnLewisStepMap`、`NetClient`、`OrderedExtensions`、`PaymentGatewayRegistry`、`PopMartStepMap` …共 9 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Providers.IDataProvider`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Services.ImapProvider`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Host` | `AccountAndAuthFamilies`、`BouncyH2Client`、`BouncyHttpClient`、`CasioModule`、`CommerceHubGateway`、`EndClothingModule` …共 44 个 | 归属过多 → 通用词，无信息 |
| `MessageCount` | `ImapMailProvider` | 唯一归属 → 改名/合并 |
| `Status` | `AdvancedView`、`AnalyticsView`、`AppearanceView`、`BillingView`、`BotTask`、`BouncyHttpClient` …共 101 个 | 归属过多 → 通用词，无信息 |
| `Username` | `ImapCreatorView`、`ImapMailProvider`、`Proxy`、`ProxyColumn`、`ProxyConnector`、`ProxyCreatorModel` …共 7 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.Action`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Config` | `AdvancedView`、`App`、`AppServices`、`AppearanceView`、`AycdInboxCreatorView`、`BillingView` …共 59 个 | 归属过多 → 通用词，无信息 |
| `Description` | `ExpressionExample`、`ExpressionView`、`PublishTemplateModal`、`PublishedTemplate`、`StepAction`、`StepActionRegistry` | 归属过多 → 通用词，无信息 |
| `Image` | `BaseCheckout`、`BotTask`、`CanvasSurface`、`MonitorProduct`、`MonitorResult`、`Product` …共 12 个 | 归属过多 → 通用词，无信息 |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Variables` | `SmartAction`、`SmartActionEngine` | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.ActionConfig`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Required` | `SmartActionStepConfig`、`SmartActionsCreator` | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.ActionParams`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Action` | `AccountGrid`、`AccountGroupView`、`AccountImportWindow`、`AccountMoveView`、`AccountView`、`ActionRow` …共 52 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.Filter`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Behaviour` | `MethodPatchTable`、`ProxyGroup`、`ProxyGroupView`、`ProxyRotator`、`SmartActionFilter`、`SmartActionSettingsView` …共 7 个 | 归属过多 → 通用词，无信息 |
| `Inputs` | `FilterRow`、`SessionPayloadBuilder`、`SessionTelemetry`、`SmartActionFilter`、`SmartActionsCreator` | 归属过多 → 通用词，无信息 |
| `Operator` | `SmartActionFilter`、`SmartActionsCreator`、`SmartActionsView` | 归属过多 → 通用词，无信息 |
| `Variable` | （无） | **零归属 — 真缺候选** |

## `Cybersole.SmartActions.Operator`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.RunHistory`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Exception` | `AccountImportWindow`、`AdyenGateway`、`AycdInboxClient`、`BouncyHttpClient`、`BouncyTls`、`CaptchaSolverService` …共 85 个 | 归属过多 → 通用词，无信息 |
| `Result` | `ActionRow`、`BouncyTls`、`CasioModule`、`CheckoutOutcome`、`EndClothingModule`、`ExpressionView` …共 30 个 | 归属过多 → 通用词，无信息 |
| `Timestamp` | `BaseCheckout`、`EventBus`、`MonitorEvent`、`MonitorView` | 归属过多 → 通用词，无信息 |
| `Trigger` | `ActionsModal`、`HistoryWindow`、`SmartAction`、`SmartActionEditorWindow`、`SmartActionEngine`、`SmartActionsCreator` …共 7 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.Template`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Actions` | `ActionsModal`、`AdvancedView`、`MonitorWindow`、`NotificationsView`、`SmartAction`、`SmartActionEditorWindow` …共 12 个 | 归属过多 → 通用词，无信息 |
| `Description` | `ExpressionExample`、`ExpressionView`、`PublishTemplateModal`、`PublishedTemplate`、`StepAction`、`StepActionRegistry` | 归属过多 → 通用词，无信息 |
| `Filters` | `ActionsModal`、`MonitorView`、`SmartAction`、`SmartActionsCreator`、`SmartActionsView` | 归属过多 → 通用词，无信息 |
| `Title` | `AccountGrid`、`AccountGroupView`、`AccountImportWindow`、`ActionsModal`、`AnalyticsView`、`CheckoutList` …共 59 个 | 归属过多 → 通用词，无信息 |
| `Trigger` | `ActionsModal`、`HistoryWindow`、`SmartAction`、`SmartActionEditorWindow`、`SmartActionEngine`、`SmartActionsCreator` …共 7 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.Trigger`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Description` | `ExpressionExample`、`ExpressionView`、`PublishTemplateModal`、`PublishedTemplate`、`StepAction`、`StepActionRegistry` | 归属过多 → 通用词，无信息 |
| `Image` | `BaseCheckout`、`BotTask`、`CanvasSurface`、`MonitorProduct`、`MonitorResult`、`Product` …共 12 个 | 归属过多 → 通用词，无信息 |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |
| `Variables` | `SmartAction`、`SmartActionEngine` | 归属过多 → 通用词，无信息 |

## `Cybersole.SmartActions.Variable`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Description` | `ExpressionExample`、`ExpressionView`、`PublishTemplateModal`、`PublishedTemplate`、`StepAction`、`StepActionRegistry` | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Localization.LocalizeEnumExtension`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Localization.LocalizeFallbackExtension`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Localization.LocalizeFormatExtension`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |
| `Value2` | （无） | **零归属 — 真缺候选** |

## `Cybersole.Ui.Localization.LocalizeSwitchExtension`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Condition` | （无） | **零归属 — 真缺候选** |

## `Cybersole.Ui.Views.Accounts.AccountStoreEntry`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `IsSelected` | （无） | **零归属 — 真缺候选** |
| `Name` | `Account`、`AccountGroup`、`AccountGroupView`、`AccountMoveView`、`AccountView`、`ActionsModal` …共 197 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Accounts.AccountStoreType`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Stores` | `AdvancedView`、`AppServices`、`CustomBrowser`、`Drop`、`GoogleAccountsView`、`HelpView` …共 19 个 | 归属过多 → 通用词，无信息 |
| `Type` | `AccountGroup`、`AccountView`、`AntiCaptchaDriver`、`AycdCaptchaDriver`、`BaseCheckout`、`CapMonsterDriver` …共 45 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Add` | `AccountGrid`、`AccountImportWindow`、`AccountMoveView`、`AccountTable`、`AccountView`、`ActionsModal` …共 126 个 | 归属过多 → 通用词，无信息 |
| `Close` | `AccountGroupView`、`AccountImportWindow`、`AccountMoveView`、`ActionsModal`、`App`、`BouncyHttpClient` …共 48 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Analytics.Modals.CheckoutProperty`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Key` | `AnalyticsView`、`AycdInboxClient`、`BillingKeyBinds`、`BouncyH2Client`、`CatalogValidator`、`CheckoutStats` …共 40 个 | 归属过多 → 通用词，无信息 |
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Auth.AuthWindow`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Exit` | `App`、`CustomBrowser`、`CustomBrowserWindow`、`HistoryWindow`、`MainWindow`、`MonitorWindow` …共 7 个 | 归属过多 → 通用词，无信息 |
| `Logout` | （无） | **零归属 — 真缺候选** |
| `Minimise` | `CustomBrowser`、`CustomBrowserWindow`、`HistoryWindow`、`MainWindow`、`MonitorWindow`、`SmartActionsCreator` …共 7 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Auth.LicenseControl`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Authenticate` | （无） | **零归属 — 真缺候选** |
| `Dashboard` | `LoginControl`、`UserView` | 归属过多 → 通用词，无信息 |
| `Refresh` | `BillingView`、`CaptchaProvidersView`、`CheckoutList`、`CloudflareSolversView`、`CreateGroupModal`、`CustomBrowser` …共 28 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Profile` | `AdvancedView`、`BaseCheckout`、`BillingGroup`、`BillingView`、`BotTask`、`BouncyHttpClient` …共 65 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Profile` | `AdvancedView`、`BaseCheckout`、`BillingGroup`、`BillingView`、`BotTask`、`BouncyHttpClient` …共 65 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Settings.ErrorEntry`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Key` | `AnalyticsView`、`AycdInboxClient`、`BillingKeyBinds`、`BouncyH2Client`、`CatalogValidator`、`CheckoutStats` …共 40 个 | 归属过多 → 通用词，无信息 |
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Settings.KeyBindSection`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Key` | `AnalyticsView`、`AycdInboxClient`、`BillingKeyBinds`、`BouncyH2Client`、`CatalogValidator`、`CheckoutStats` …共 40 个 | 归属过多 → 通用词，无信息 |
| `Shortcuts` | `KeyBindsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Settings.LocalizedOption`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Text` | `AccountGrid`、`AccountGroupView`、`AccountImportWindow`、`AccountTable`、`AccountView`、`AdvancedView` …共 123 个 | 归属过多 → 通用词，无信息 |
| `Value` | `AnalyticsView`、`BouncyH2Client`、`BouncyHttpClient`、`BrotliDictionary`、`BstnFlow`、`CasioFlow` …共 82 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Settings.Modals.SizeOption`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Selected` | `ComboBoxEdit`、`GoogleAccountsView`、`ImapView`、`KeyBindsView`、`ProfileView`、`SmartActionsView` …共 9 个 | 归属过多 → 通用词，无信息 |
| `Title` | `AccountGrid`、`AccountGroupView`、`AccountImportWindow`、`ActionsModal`、`AnalyticsView`、`CheckoutList` …共 59 个 | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Settings.SettingsView`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `AppearanceView` | `AppearanceView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `CaptchaProvidersView` | `CaptchaProvidersView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `CloudflareSolversView` | `CloudflareSolversView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `CustomSizesView` | `CustomSizesView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `CustomStoresView` | `CustomStoresView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `DataView` | `DataView`、`SettingsShell`、`WindowNameTable` | 归属过多 → 通用词，无信息 |
| `GeneralSettingsView` | `GeneralSettingsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `GoogleAccountsView` | `GoogleAccountsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `HelpView` | `HelpView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `ImapView` | `ImapView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `KeyBindsView` | `KeyBindsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `LogOut` | `UserView` | 唯一归属 → 改名/合并 |
| `NotificationsView` | `NotificationsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `PayPalAccountsView` | `PayPalAccountsView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `PaymentView` | `PaymentView`、`ProfileCreatorView`、`SettingsShell` | 归属过多 → 通用词，无信息 |
| `Transition` | （无） | **零归属 — 真缺候选** |
| `Update` | `AnalyticsView`、`MainWindow`、`SettingsShell`、`StoreBarChart` | 归属过多 → 通用词，无信息 |
| `Version` | `AntiBotVendors`、`AppVersion`、`ChromiumKasadaSolver`、`KasadaResult`、`KasadaSolver`、`KasadaStrategy` …共 12 个 | 归属过多 → 通用词，无信息 |
| `WebhookView` | `SettingsShell`、`WebhookView` | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.SmartActions.ActionConfigEntry`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Config` | `AdvancedView`、`App`、`AppServices`、`AppearanceView`、`AycdInboxCreatorView`、`BillingView` …共 59 个 | 归属过多 → 通用词，无信息 |
| `Key` | `AnalyticsView`、`AycdInboxClient`、`BillingKeyBinds`、`BouncyH2Client`、`CatalogValidator`、`CheckoutStats` …共 40 个 | 归属过多 → 通用词，无信息 |
| `Parameters` | `Ecdhe` | 唯一归属 → 改名/合并 |

## `Cybersole.Ui.Views.SmartActions.TemplateGroup`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Key` | `AnalyticsView`、`AycdInboxClient`、`BillingKeyBinds`、`BouncyH2Client`、`CatalogValidator`、`CheckoutStats` …共 40 个 | 归属过多 → 通用词，无信息 |
| `Templates` | `PublishTemplateModal`、`SmartActionsCreator`、`SmartActionsDocument` | 归属过多 → 通用词，无信息 |

## `Cybersole.Ui.Views.Tasks.TaskCreatorCartView`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `Add` | `AccountGrid`、`AccountImportWindow`、`AccountMoveView`、`AccountTable`、`AccountView`、`ActionsModal` …共 126 个 | 归属过多 → 通用词，无信息 |
| `Delete` | `AccountGrid`、`AccountGroupView`、`AccountView`、`BillingKeyBinds`、`ChromiumBridge`、`CustomSizesView` …共 34 个 | 归属过多 → 通用词，无信息 |
| `SizeItems` | `TaskCreatorView` | 唯一归属 → 改名/合并 |

## `Cybersole.Ui.Views.Tasks.TaskCreatorMainView`

| 成员 | 归属类 | 判读 |
|---|---|---|
| `ProfileGroupItems` | `TaskCreatorView` | 唯一归属 → 改名/合并 |
| `ProfileItems` | `GeneralSettingsView`、`TaskCreatorView` | 归属过多 → 通用词，无信息 |
| `ShowCartView` | `TaskCreatorView` | 唯一归属 → 改名/合并 |
| `SizeItems` | `TaskCreatorView` | 唯一归属 → 改名/合并 |

---

## 汇总

| 判读 | 条数 |
|---|---|
| 唯一归属（改名/合并） | 15 |
| 归属过多（通用词） | 159 |
| 零归属（真缺候选） | 16 |

### 唯一归属的成员（可直接写进账本）

| 类型 | 成员 | 归属类 |
|---|---|---|
| `Cybersole.Global.Settings` | `MonitorConcurrency` | `GlobalSettings` |
| `Cybersole.Models.CreateInputModel` | `AutoQuantity` | `TaskCombinationRequest` |
| `Cybersole.Models.CreateInputModel` | `MaxPrice` | `Product` |
| `Cybersole.Models.CreateInputModel` | `Minus` | `TaskCreatorView` |
| `Cybersole.Models.CreateInputModel` | `Plus` | `TaskCreatorView` |
| `Cybersole.Models.CreateInputModel` | `PriceCheckVisible` | `TaskCreatorView` |
| `Cybersole.Models.CreateInputModel` | `TogglePriceCheck` | `TaskCreatorView` |
| `Cybersole.Models.User` | `Discord` | `WebhookCreatorView` |
| `Cybersole.Services.ImapProvider` | `MessageCount` | `ImapMailProvider` |
| `Cybersole.Ui.Views.Settings.SettingsView` | `LogOut` | `UserView` |
| `Cybersole.Ui.Views.SmartActions.ActionConfigEntry` | `Parameters` | `Ecdhe` |
| `Cybersole.Ui.Views.Tasks.TaskCreatorCartView` | `SizeItems` | `TaskCreatorView` |
| `Cybersole.Ui.Views.Tasks.TaskCreatorMainView` | `ProfileGroupItems` | `TaskCreatorView` |
| `Cybersole.Ui.Views.Tasks.TaskCreatorMainView` | `ShowCartView` | `TaskCreatorView` |
| `Cybersole.Ui.Views.Tasks.TaskCreatorMainView` | `SizeItems` | `TaskCreatorView` |

### 零归属的成员（真缺候选）

| 类型 | 成员 |
|---|---|
| `Cybersole.Attributes.Platform` | `InputType` |
| `Cybersole.Attributes.Platform` | `QuantityAutoAdjustSupport` |
| `Cybersole.Attributes.Platform` | `QuantitySupport` |
| `Cybersole.Helpers.BrowserProfile` | `DisplayName` |
| `Cybersole.Models.AycdInboxAccount` | `TaskCount` |
| `Cybersole.Models.NotificationSound` | `SoundLocation` |
| `Cybersole.Models.Store` | `ColorSupport` |
| `Cybersole.Models.Store` | `Elements` |
| `Cybersole.Models.User` | `IsStaff` |
| `Cybersole.SmartActions.Filter` | `Variable` |
| `Cybersole.Ui.Localization.LocalizeFormatExtension` | `Value2` |
| `Cybersole.Ui.Localization.LocalizeSwitchExtension` | `Condition` |
| `Cybersole.Ui.Views.Accounts.AccountStoreEntry` | `IsSelected` |
| `Cybersole.Ui.Views.Auth.AuthWindow` | `Logout` |
| `Cybersole.Ui.Views.Auth.LicenseControl` | `Authenticate` |
| `Cybersole.Ui.Views.Settings.SettingsView` | `Transition` |

