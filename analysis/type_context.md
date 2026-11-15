# 绑定描述符邻居（生成文件，请勿手改）

> 由 `python analysis/type_context.py` 生成。目标：给 `bind_diff.py --type-presence` 列出的
> ABSENT 类型找**同一个编译期 XAML 块里的邻居**，从而推断它属于哪个页面/面板。

> **证据等级：Inference（中）** —— 同一个块里出现 ≠ 同一个页面的模型（一个块可以同时覆盖
> 页面与其弹窗）。所以每行都给了地址，供回查原文。

## `Cybersole.Attributes.CreateInfo`  (2 members: Name, Properties)

出现于 5 个描述符块：`0x143218a15`、`0x143218ae3`、`0x143218b24`、`0x14363fe4f`、`0x14363fee6`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 2 |

## `Cybersole.Attributes.Platform`  (5 members: InputType, MultiCart, Name, QuantityAutoAdjustSupport, QuantitySupport)

出现于 10 个描述符块：`0x1432212af`、`0x14322152c`、`0x14322157a`、`0x143221ddb`、`0x143221f8c`、`0x143221fd0`、`0x143645082`、`0x143645208`、`0x1436456cb`、`0x14364580f`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Tasks.TaskCreatorCartView` | 4 |
| `Cybersole.Models.CreateInputModel` | 2 |
| `Cybersole.Models.Store` | 2 |
| `Cybersole.Models.EditValue`1` | 2 |
| `Cybersole.Models.CreateModel` | 2 |

## `Cybersole.CloudflareSolvers.CloudflareSolver`  (9 members: ApiKey, Balance, BalanceSupported, Concurrency, Count, Id, IsFetchingBalance, Name, Type)

出现于 25 个描述符块：`0x143215f75`、`0x143215fbd`、`0x143216005`、`0x14321604d`、`0x143216097`、`0x1432160e1`、`0x14321612c`、`0x143216177`、`0x1432161c0`、`0x143216209`、`0x143216258`、`0x1432163d7`、`0x14321642b`、`0x143216480`、`0x143220a2d`、`0x143220a73`、`0x14363e4d8`、`0x14363e522`、`0x14363e56c`、`0x14363e5b8`、`0x14363e605`、`0x14363e650`、`0x14363e73d`、`0x14363e793`、`0x143644c1c`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.TaskGroup` | 2 |

## `Cybersole.Global.Settings`  (34 members: AutoOpen3DS, AutoOpen3DSLimit, BackupInterval, BetaUpdates, BrowserLimit, BrowserPath, BrowserProfileAssignment, BrowserWindowMode, Clock, Currency, Keybinds, Language, MaxBackups, MaxLogRetention, MaxLogSize, MonitorConcurrency, MonitorDelay, MonitorFilters, Notifications, PinGroups, ProfileGroupOrder, ProxyGroupOrder, QueuePresentation, QuickTaskProfiles, QuickTaskProxies, RetryDelay, ScrollbarColor, ScrollbarCornerRadius, ScrollbarWidth, ShopifyBrowserProxy, SmartActions, StartupPage, TaskGroupOrder, Timeout)

出现于 60 个描述符块：`0x14320d3fb`、`0x14320fe3f`、`0x143211210`、`0x1432139c0`、`0x143213a02`、`0x143214a73`、`0x1432154ea`、`0x1432155b2`、`0x1432155f8`、`0x143216c33`、`0x1432171b6`、`0x1432171f8`、`0x14321723a`、`0x14321727b`、`0x1432172bc`、`0x143217300`、`0x143217344`、`0x143217386`、`0x1432173c8`、`0x14321740b`、`0x1432176ea`、`0x1432184a7`、`0x143219e49`、`0x14321a4bc`、`0x14321a57d`、`0x14321a5be`、`0x14321a6ba`、`0x14321a777`、`0x14321a7b9`、`0x14321a99e`、`0x14321a9e7`、`0x14321e37d`、`0x14321f5d0`、`0x14363910b`、`0x14363a9a2`、`0x14363b668`、`0x14363ce1d`、`0x14363d7f7`、`0x14363de5c`、`0x14363de9d`、`0x14363dee5`、`0x14363ecc4`、`0x14363edc4`、`0x14363ee05`、`0x14363ee83`、`0x14363f006`、`0x14363f04a`、`0x14363f08d`、`0x14363f0d3`、`0x14363f117`、`0x14363f2d9`、`0x14363fae0`、`0x143640b16`、`0x143640eb1`、`0x143640f3a`、`0x143640fbb`、`0x14364103f`、`0x1436411a3`、`0x143643544`、`0x1436446d4`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.DataView` | 3 |
| `Cybersole.Ui.Localization.LocalizeEnumExtension` | 2 |
| `Cybersole.Models.Analytics` | 2 |
| `Cybersole.Ui.Views.Captcha.YoutubeWindow` | 2 |
| `Cybersole.Services.ClockService` | 2 |
| `Cybersole.Ui.Views.MainWindow` | 2 |
| `Cybersole.Ui.Views.Monitor.MonitorView` | 2 |
| `Cybersole.Models.Flag` | 2 |
| `Cybersole.Ui.Views.Proxies.ProxyView` | 2 |
| `Cybersole.Models.Concurrency` | 2 |
| `Cybersole.Ui.Views.Settings.LocalizedOption` | 2 |
| `Cybersole.Models.User` | 2 |

## `Cybersole.Helpers.BrowserProfile`  (1 members: DisplayName)

出现于 2 个描述符块：`0x14321a8d9`、`0x14364111b`

（块内没有其它 Cybersole 类型）

## `Cybersole.Helpers.ObservableDictionary`2`  (1 members: Count)

出现于 2 个描述符块：`0x14321dac6`、`0x143643059`

（块内没有其它 Cybersole 类型）

## `Cybersole.KeyInput.KeyGesture`  (2 members: Key, Modifiers)

出现于 2 个描述符块：`0x14321869c`、`0x14363fbe1`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.KeyBindSection` | 2 |
| `Cybersole.Models.Shortcut` | 2 |

## `Cybersole.Models.Analytics`  (2 members: Spent, Success)

出现于 2 个描述符块：`0x14320d3fb`、`0x14363910b`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Localization.LocalizeEnumExtension` | 2 |
| `Cybersole.Global.Settings` | 2 |

## `Cybersole.Models.AycdInboxAccount`  (5 members: ApiKey, Enabled, Error, Status, TaskCount)

出现于 7 个描述符块：`0x143217de9`、`0x143217f33`、`0x143217f75`、`0x14363f74e`、`0x14363f7cf`、`0x14363f813`、`0x14363f854`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.ImapView` | 1 |

## `Cybersole.Models.Captcha`  (1 members: Proxy)

出现于 2 个描述符块：`0x14320fb25`、`0x14363a7c2`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.SolverSettings` | 2 |
| `Cybersole.Models.GoogleAccount` | 2 |
| `Cybersole.Models.Solver` | 2 |

## `Cybersole.Models.Concurrency`  (3 members: Maximum, Mode, Ratio)

出现于 2 个描述符块：`0x14321740b`、`0x14363f117`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Global.Settings` | 2 |

## `Cybersole.Models.CreateInputModel`  (13 members: AutoQuantity, Color, Currency, Input, MaxPrice, MinPrice, Minus, Plus, PriceCheckVisible, Quantity, Sizes, Symbol, TogglePriceCheck)

出现于 26 个描述符块：`0x1432212af`、`0x1432214a2`、`0x1432214e7`、`0x143221640`、`0x143221681`、`0x143221932`、`0x1432219f0`、`0x143221a3a`、`0x143221a83`、`0x143221acc`、`0x143221b0d`、`0x143221b90`、`0x143221c11`、`0x143221c52`、`0x143221c93`、`0x143221cd4`、`0x143645082`、`0x1436451c1`、`0x143645296`、`0x14364541e`、`0x1436454a2`、`0x1436454ee`、`0x143645539`、`0x1436455c0`、`0x143645601`、`0x143645644`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.Store` | 4 |
| `Cybersole.Models.EditValue`1` | 3 |
| `Cybersole.Ui.Views.Tasks.TaskCreatorCartView` | 2 |
| `Cybersole.Attributes.Platform` | 2 |

## `Cybersole.Models.NotificationSound`  (1 members: SoundLocation)

出现于 2 个描述符块：`0x14321a398`、`0x143640e1c`

（块内没有其它 Cybersole 类型）

## `Cybersole.Models.ProfileItem`  (2 members: Description, Name)

出现于 4 个描述符块：`0x1432221ae`、`0x1432222f2`、`0x143645928`、`0x143645a37`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.CreateModel` | 4 |
| `Cybersole.Ui.Views.Tasks.TaskCreatorMainView` | 2 |
| `Cybersole.Models.EditValue`1` | 1 |

## `Cybersole.Models.RemoteData`  (1 members: Name)

出现于 2 个描述符块：`0x143213a84`、`0x14363cea3`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.ProfileGroup` | 2 |

## `Cybersole.Models.Size`  (1 members: Value)

出现于 2 个描述符块：`0x143216661`、`0x14363e8fa`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.CustomSizesView` | 2 |

## `Cybersole.Models.Store`  (6 members: ColorSupport, Currency, Elements, Info, Name, Url)

出现于 10 个描述符块：`0x14320d149`、`0x143216920`、`0x14321f5d0`、`0x1432212af`、`0x143221681`、`0x143638fa6`、`0x14363eacb`、`0x143643fcd`、`0x143645082`、`0x143645296`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.CreateInputModel` | 4 |
| `Cybersole.Ui.Views.Accounts.Modals.CreateGroupModal` | 2 |
| `Cybersole.Ui.Views.Settings.CustomStoresView` | 2 |
| `Cybersole.Ui.Views.Tasks.Modals.TaskDetailsView` | 2 |
| `Cybersole.Ui.Views.Tasks.TaskView` | 2 |
| `Cybersole.Elements.Element` | 2 |
| `Cybersole.Models.TaskStep` | 2 |
| `Cybersole.Models.BotTask` | 2 |
| `Cybersole.Models.Product` | 2 |
| `Cybersole.Models.Variant` | 2 |
| `Cybersole.Models.WebTask` | 2 |
| `Cybersole.Ui.Views.Tasks.TaskCreatorCartView` | 2 |

## `Cybersole.Models.User`  (6 members: Discord, Email, FirstName, Image, IsStaff, LastName)

出现于 8 个描述符块：`0x143210299`、`0x143210f62`、`0x1432176ea`、`0x143217bca`、`0x14363acb4`、`0x14363b4c0`、`0x14363f2d9`、`0x14363f5bf`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.MainWindow` | 2 |
| `Cybersole.Models.Notification` | 2 |
| `Cybersole.Ui.Views.Modals.NotificationView` | 2 |
| `Cybersole.Ui.Views.Modals.UserView` | 2 |
| `Cybersole.Ui.Views.Settings.LocalizedOption` | 2 |
| `Cybersole.Global.Settings` | 2 |
| `Cybersole.Ui.Views.Settings.GoogleAccountsView` | 2 |
| `Cybersole.Ui.Views.Settings.ErrorEntry` | 2 |
| `Cybersole.Ui.Views.Settings.HelpView` | 2 |

## `Cybersole.Models.ValueGroup`  (3 members: Name, Preview, Values)

出现于 6 个描述符块：`0x143223d7e`、`0x143223e46`、`0x143223fe4`、`0x143646900`、`0x143646981`、`0x143646a55`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Utilities.UtilitiesView` | 4 |

## `Cybersole.Providers.IDataProvider`  (1 members: Name)

出现于 2 个描述符块：`0x143216abb`、`0x14363ebc2`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.DataView` | 2 |

## `Cybersole.Services.ImapProvider`  (4 members: Host, MessageCount, Status, Username)

出现于 6 个描述符块：`0x1432181bf`、`0x143218464`、`0x1432184a7`、`0x14363f91f`、`0x14363fa9f`、`0x14363fae0`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.ImapView` | 4 |
| `Cybersole.Global.Settings` | 2 |
| `Cybersole.Ui.Views.Settings.KeyBindSection` | 1 |

## `Cybersole.SmartActions.Action`  (5 members: Config, Description, Image, Name, Variables)

出现于 11 个描述符块：`0x14321b98b`、`0x14321d90a`、`0x14321d94b`、`0x14321db55`、`0x14321dd47`、`0x14321dd8a`、`0x143641d1f`、`0x143641dda`、`0x143642f75`、`0x1436430ec`、`0x1436431c6`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.SmartActions.ActionConfig` | 5 |
| `Cybersole.SmartActions.ActionParams` | 3 |
| `Cybersole.Ui.Views.SmartActions.ActionsModal` | 2 |
| `Cybersole.Ui.Views.SmartActions.ActionConfigEntry` | 1 |

## `Cybersole.SmartActions.ActionConfig`  (2 members: Name, Required)

出现于 5 个描述符块：`0x14321db55`、`0x14321dd47`、`0x14321dd8a`、`0x1436430ec`、`0x1436431c6`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.SmartActions.ActionConfigEntry` | 1 |

## `Cybersole.SmartActions.ActionParams`  (1 members: Action)

出现于 3 个描述符块：`0x14321d90a`、`0x14321d94b`、`0x143642f75`

（块内没有其它 Cybersole 类型）

## `Cybersole.SmartActions.Filter`  (4 members: Behaviour, Inputs, Operator, Variable)

出现于 11 个描述符块：`0x14321c586`、`0x14321d1c0`、`0x14321d2e9`、`0x14321d475`、`0x14343ee4f`、`0x14343eeaf`、`0x14343ef90`、`0x143642419`、`0x143642b61`、`0x143642c52`、`0x143642cd2`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.SmartActions.SmartActionsCreator` | 3 |
| `Cybersole.Ui.Views.SmartActions.FilterRow` | 2 |
| `Cybersole.SmartActions.Operator` | 2 |
| `Cybersole.SmartActions.Trigger` | 2 |
| `Cybersole.SmartActions.Variable` | 2 |

## `Cybersole.SmartActions.Operator`  (1 members: Name)

出现于 2 个描述符块：`0x14321c586`、`0x143642419`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.SmartActions.FilterRow` | 2 |
| `Cybersole.SmartActions.Filter` | 2 |

## `Cybersole.SmartActions.RunHistory`  (4 members: Exception, Result, Timestamp, Trigger)

出现于 9 个描述符块：`0x14321c020`、`0x14321c0e9`、`0x14321c12b`、`0x14321c1f8`、`0x14321c23a`、`0x14364215e`、`0x14364219f`、`0x143642244`、`0x143642288`

（块内没有其它 Cybersole 类型）

## `Cybersole.SmartActions.Template`  (5 members: Actions, Description, Filters, Title, Trigger)

出现于 3 个描述符块：`0x14321eab2`、`0x14321eaf4`、`0x14364398c`

（块内没有其它 Cybersole 类型）

## `Cybersole.SmartActions.Trigger`  (4 members: Description, Image, Name, Variables)

出现于 7 个描述符块：`0x14321c2fc`、`0x14321c33d`、`0x14321d006`、`0x14321d2e9`、`0x1436422ca`、`0x143642a86`、`0x143642c52`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.SmartActions.Filter` | 2 |
| `Cybersole.Ui.Views.SmartActions.SmartActionsCreator` | 1 |

## `Cybersole.SmartActions.Variable`  (1 members: Description)

出现于 3 个描述符块：`0x14321d433`、`0x14321d475`、`0x143642cd2`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.SmartActions.Filter` | 2 |

## `Cybersole.Ui.Localization.LocalizeEnumExtension`  (1 members: Value)

出现于 3 个描述符块：`0x14320d3b4`、`0x14320d3fb`、`0x14363910b`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.Analytics` | 2 |
| `Cybersole.Global.Settings` | 2 |

## `Cybersole.Ui.Localization.LocalizeFallbackExtension`  (1 members: Value)

出现于 3 个描述符块：`0x14320eae3`、`0x14320eb2e`、`0x143639e4b`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.License` | 2 |

## `Cybersole.Ui.Localization.LocalizeFormatExtension`  (2 members: Value, Value2)

出现于 6 个描述符块：`0x14320c2d5`、`0x14320c31e`、`0x143212a80`、`0x143212aca`、`0x1436387a9`、`0x14363c4c7`

（块内没有其它 Cybersole 类型）

## `Cybersole.Ui.Localization.LocalizeSwitchExtension`  (1 members: Condition)

出现于 3 个描述符块：`0x14320c1fd`、`0x14320c24a`、`0x14363871a`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Accounts.AccountGrid` | 2 |

## `Cybersole.Ui.Views.Accounts.AccountStoreEntry`  (2 members: IsSelected, Name)

出现于 6 个描述符块：`0x14320ca2e`、`0x14320ca78`、`0x14320cac2`、`0x14320cb06`、`0x143638b9a`、`0x143638be6`

（块内没有其它 Cybersole 类型）

## `Cybersole.Ui.Views.Accounts.AccountStoreType`  (2 members: Stores, Type)

出现于 6 个描述符块：`0x14320c91e`、`0x14320c961`、`0x14320c9a4`、`0x14320c9e9`、`0x143638b0e`、`0x143638b53`

（块内没有其它 Cybersole 类型）

## `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView`  (2 members: Add, Close)

出现于 7 个描述符块：`0x14320cf7f`、`0x14320cfcd`、`0x14320d01b`、`0x14320d067`、`0x143638ebb`、`0x143638f0b`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView` | 1 |
| `Cybersole.Ui.Views.SmartActions.PublishTemplateModal` | 1 |

## `Cybersole.Ui.Views.Analytics.Modals.CheckoutProperty`  (2 members: Key, Value)

出现于 6 个描述符块：`0x14320e012`、`0x14320e05c`、`0x14320e0a6`、`0x14320e0f2`、`0x143639807`、`0x143639853`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.Checkout` | 2 |

## `Cybersole.Ui.Views.Auth.AuthWindow`  (3 members: Exit, Logout, Minimise)

出现于 3 个描述符块：`0x14320e884`、`0x143639c88`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseView` | 3 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView` | 1 |

## `Cybersole.Ui.Views.Auth.LicenseControl`  (3 members: Authenticate, Dashboard, Refresh)

出现于 8 个描述符块：`0x14320e9f9`、`0x14320ebae`、`0x14320ebf0`、`0x14320ec32`、`0x143639dd3`、`0x143639ecf`、`0x143639f13`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.License` | 2 |
| `Cybersole.Models.AsyncCommand` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |

## `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView`  (1 members: Profile)

出现于 3 个描述符块：`0x14321256a`、`0x14363c113`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.Profile` | 2 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView` | 1 |

## `Cybersole.Ui.Views.Profiles.Modals.ProfilePaymentView`  (1 members: Profile)

出现于 3 个描述符块：`0x14321354d`、`0x14363cba8`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.Profile` | 2 |
| `Cybersole.Models.Card` | 2 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |

## `Cybersole.Ui.Views.Settings.ErrorEntry`  (2 members: Key, Value)

出现于 2 个描述符块：`0x143217bca`、`0x14363f5bf`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.GoogleAccountsView` | 2 |
| `Cybersole.Ui.Views.Settings.HelpView` | 2 |
| `Cybersole.Models.User` | 2 |

## `Cybersole.Ui.Views.Settings.KeyBindSection`  (2 members: Key, Shortcuts)

出现于 5 个描述符块：`0x1432184a7`、`0x143218656`、`0x14321869c`、`0x14363fb9f`、`0x14363fbe1`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.KeyInput.KeyGesture` | 2 |
| `Cybersole.Models.Shortcut` | 2 |
| `Cybersole.Ui.Views.Settings.ImapView` | 1 |
| `Cybersole.Services.ImapProvider` | 1 |
| `Cybersole.Global.Settings` | 1 |

## `Cybersole.Ui.Views.Settings.LocalizedOption`  (2 members: Text, Value)

出现于 5 个描述符块：`0x143217665`、`0x1432176a7`、`0x1432176ea`、`0x14363f295`、`0x14363f2d9`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Global.Settings` | 2 |
| `Cybersole.Models.User` | 2 |

## `Cybersole.Ui.Views.Settings.Modals.SizeOption`  (2 members: Selected, Title)

出现于 6 个描述符块：`0x143219a72`、`0x143219aba`、`0x143219bb0`、`0x143219bf5`、`0x1436408f9`、`0x14364099c`

（块内没有其它 Cybersole 类型）

## `Cybersole.Ui.Views.Settings.SettingsView`  (19 members: AppearanceView, CaptchaProvidersView, CloudflareSolversView, CustomSizesView, CustomStoresView, DataView, GeneralSettingsView, GoogleAccountsView, HelpView, ImapView, KeyBindsView, LogOut, NotificationsView, PayPalAccountsView, PaymentView, Transition, Update, Version, WebhookView)

出现于 40 个描述符块：`0x14321aef6`、`0x14321af38`、`0x14321af79`、`0x14321afbe`、`0x14321b003`、`0x14321b051`、`0x14321b09a`、`0x14321b0e6`、`0x14321b12c`、`0x14321b16f`、`0x14321b1bc`、`0x14321b209`、`0x14321b24c`、`0x14321b29b`、`0x14321b2eb`、`0x14321b332`、`0x14321b37d`、`0x14321b3c7`、`0x14321b40d`、`0x14321b450`、`0x1436414ad`、`0x1436414f1`、`0x143641534`、`0x14364157b`、`0x1436415cb`、`0x143641616`、`0x143641664`、`0x1436416ac`、`0x1436416f1`、`0x143641740`、`0x14364178f`、`0x1436417d4`、`0x143641825`、`0x143641877`、`0x1436418c0`、`0x14364190d`、`0x143641959`、`0x1436419a1`、`0x1436419e6`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Ui.Views.Settings.WebhookView` | 3 |
| `Cybersole.Webhook.IWebhook` | 2 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |

## `Cybersole.Ui.Views.SmartActions.ActionConfigEntry`  (3 members: Config, Key, Parameters)

出现于 9 个描述符块：`0x14321db0b`、`0x14321db55`、`0x14321dc1d`、`0x14321dc6b`、`0x14321dcb9`、`0x14321dd00`、`0x1436430a0`、`0x14364312d`、`0x14364317d`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.SmartActions.ActionConfig` | 1 |

## `Cybersole.Ui.Views.SmartActions.TemplateGroup`  (2 members: Key, Templates)

出现于 6 个描述符块：`0x14321e99a`、`0x14321e9dd`、`0x14321ea20`、`0x14321ea69`、`0x1436438fc`、`0x143643941`

（块内没有其它 Cybersole 类型）

## `Cybersole.Ui.Views.Tasks.TaskCreatorCartView`  (3 members: Add, Delete, SizeItems)

出现于 9 个描述符块：`0x14322126a`、`0x1432212af`、`0x1432218a8`、`0x143221d99`、`0x143221ddb`、`0x143645082`、`0x1436453d4`、`0x1436456cb`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Attributes.Platform` | 4 |
| `Cybersole.Models.CreateInputModel` | 2 |
| `Cybersole.Models.Store` | 2 |
| `Cybersole.Models.CreateModel` | 2 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |

## `Cybersole.Ui.Views.Tasks.TaskCreatorMainView`  (4 members: ProfileGroupItems, ProfileItems, ShowCartView, SizeItems)

出现于 10 个描述符块：`0x143221f44`、`0x143222014`、`0x14322205f`、`0x1432221ae`、`0x1432223e9`、`0x1436457c5`、`0x143645855`、`0x143645928`、`0x143645ab5`、`0x143c5c282`

| 邻居类型 | 同现次数 |
|---|---|
| `Cybersole.Models.CreateModel` | 4 |
| `Cybersole.Models.ProfileItem` | 2 |
| `Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView` | 1 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView` | 1 |
| `Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView` | 1 |
| `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileAdvancedView` | 1 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 1 |

