# 绑定成员的形状（Property / Getter / Setter）

来源：字符串池里的编译期访问器名（`<Type>,Cybersole.<Member>!Property|Getter|Setter`）。
生成器：`python tools/bind_shape.py [过滤词]`。

**怎么读**：
**覆盖**：102 个类型在池子里有访问器证据。


- `Getter,Property,Setter` → 原件里是**可读写属性**（用户动作多半是 `ICommand` 属性）；
- `Getter,Property` → **只读属性**（数据）；
- `-` → 池子里没有该成员的访问器证据（可能是方法，或证据在别处）。

**用途**：新增成员时先看这里，按原件的形状写（动作写 `ICommand` 属性，数据写只读属性）。

## ComboBoxEdit

| 成员 | 形状 |
|---|---|
| `ClearSelectionCommand` | `Getter,Property,Setter` |
| `RemoveTokenCommand` | `Getter,Property,Setter` |

## ComboBoxGroupHeader

| 成员 | 形状 |
|---|---|
| `Name` | `Getter,Property` |

## ComboBoxToken

| 成员 | 形状 |
|---|---|
| `Text` | `Getter,Property` |

## LocalizeEnumExtension

| 成员 | 形状 |
|---|---|
| `Value` | `Getter,Property,Setter` |

## LocalizeFallbackExtension

| 成员 | 形状 |
|---|---|
| `Value` | `Getter,Property,Setter` |

## LocalizeFormatExtension

| 成员 | 形状 |
|---|---|
| `Value` | `Getter,Property,Setter` |
| `Value2` | `Getter,Property,Setter` |

## LocalizeSwitchExtension

| 成员 | 形状 |
|---|---|
| `Condition` | `Getter,Property,Setter` |

## AccountGrid

| 成员 | 形状 |
|---|---|
| `AccountGroup` | `Getter,Property` |
| `Accounts` | `Getter,Property` |
| `Add` | `Getter,Property,Setter` |
| `Clear` | `Getter,Property,Setter` |
| `CopyAccounts` | `Getter,Property,Setter` |
| `CopyPassword` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `DeleteSelected` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `MoveGroup` | `Getter,Property,Setter` |
| `OpenSettings` | `Getter,Property,Setter` |
| `Rows` | `Getter,Property` |

## AccountStoreEntry

| 成员 | 形状 |
|---|---|
| `IsSelected` | `Getter,Property,Setter` |
| `Name` | `Getter,Property,Setter` |

## AccountStoreType

| 成员 | 形状 |
|---|---|
| `Stores` | `Getter,Property,Setter` |
| `Type` | `Getter,Property,Setter` |

## AccountView

| 成员 | 形状 |
|---|---|
| `CreateGroup` | `Getter,Property,Setter` |

## GroupGrid

| 成员 | 形状 |
|---|---|
| `DeleteGroup` | `Getter,Property,Setter` |
| `Items` | `Getter,Property` |
| `Store` | `Getter,Property` |

## AccountGroupView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `GroupName` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |

## AccountsCreatorView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |

## CreateGroupModal

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Create` | `Getter,Property,Setter` |
| `Types` | `Getter,Property` |

## AnalyticsView

| 成员 | 形状 |
|---|---|
| `ChangeChart` | `Getter,Property,Setter` |
| `LoadAnalytics` | `Getter,Property,Setter` |
| `MoveNext` | `Getter,Property,Setter` |
| `MovePrevious` | `Getter,Property,Setter` |
| `OpenRelease` | `Getter,Property,Setter` |

## CheckoutList

| 成员 | 形状 |
|---|---|
| `Show` | `Getter,Property,Setter` |

## CheckoutProperty

| 成员 | 形状 |
|---|---|
| `Key` | `Getter,Property,Setter` |
| `Value` | `Getter,Property,Setter` |

## CheckoutView

| 成员 | 形状 |
|---|---|
| `Checkout` | `Getter,Property` |
| `Close` | `Getter,Property,Setter` |
| `Next` | `Getter,Property,Setter` |
| `OpenTracking` | `Getter,Property,Setter` |
| `Previous` | `Getter,Property,Setter` |
| `Properties` | `Getter,Property` |

## ReleaseSitelistView

| 成员 | 形状 |
|---|---|
| `Create` | `Getter,Property,Setter` |
| `Release` | `Getter,Property` |

## ReleaseView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Next` | `Getter,Property,Setter` |
| `Previous` | `Getter,Property,Setter` |
| `Release` | `Getter,Property` |
| `ShowGuide` | `Getter,Property,Setter` |
| `ShowSitelist` | `Getter,Property,Setter` |

## AuthWindow

| 成员 | 形状 |
|---|---|
| `Exit` | `Getter,Property,Setter` |
| `Logout` | `Getter,Property` |
| `Minimise` | `Getter,Property,Setter` |

## LicenseControl

| 成员 | 形状 |
|---|---|
| `Authenticate` | `Getter,Property` |
| `Dashboard` | `Getter,Property,Setter` |
| `Refresh` | `Getter,Property` |

## LoginControl

| 成员 | 形状 |
|---|---|
| `Cancel` | `Getter,Property,Setter` |
| `OpenBrowser` | `Getter,Property,Setter` |
| `SignIn` | `Getter,Property` |
| `SignUp` | `Getter,Property,Setter` |
| `UseCode` | `Getter,Property,Setter` |

## CustomBrowser

| 成员 | 形状 |
|---|---|
| `Autofill` | `Getter,Property,Setter` |
| `Back` | `Getter,Property,Setter` |
| `Exit` | `Getter,Property,Setter` |
| `Forward` | `Getter,Property,Setter` |
| `Minimise` | `Getter,Property,Setter` |
| `Refresh` | `Getter,Property,Setter` |
| `Status` | `Getter,Property` |
| `Type` | `Getter,Property` |

## GoogleLogin

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Save` | `Getter,Property` |

## SolverWindow

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `CloseSolver` | `Getter,Property,Setter` |
| `Dispose` | `Getter,Property` |
| `Minimise` | `Getter,Property,Setter` |
| `Panels` | `Getter,Property` |
| `Solvers` | `Getter,Property` |

## YoutubeWindow

| 成员 | 形状 |
|---|---|
| `Account` | `Getter,Property` |

## MainWindow

| 成员 | 形状 |
|---|---|
| `AccountView` | `Getter,Property` |
| `AnalyticsView` | `Getter,Property` |
| `BillingView` | `Getter,Property` |
| `Clock` | `Getter,Property` |
| `Exit` | `Getter,Property,Setter` |
| `Minimise` | `Getter,Property,Setter` |
| `Navigate` | `Getter,Property,Setter` |
| `OpenMonitor` | `Getter,Property,Setter` |
| `OpenNotifications` | `Getter,Property,Setter` |
| `OpenProfile` | `Getter,Property,Setter` |
| `ProxyView` | `Getter,Property` |
| `SettingsView` | `Getter,Property` |
| `TaskView` | `Getter,Property` |

## DesktopNotification

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |

## DropdownModal

| 成员 | 形状 |
|---|---|
| `ButtonText` | `Getter,Property` |
| `Placeholder` | `Getter,Property` |
| `Title` | `Getter,Property` |

## InputModal

| 成员 | 形状 |
|---|---|
| `ButtonText` | `Getter,Property` |
| `Close` | `Getter,Property,Setter` |
| `Placeholder` | `Getter,Property` |
| `Title` | `Getter,Property` |

## MessageBoxDialog

| 成员 | 形状 |
|---|---|
| `ActionText` | `Getter,Property,Setter` |
| `Cancel` | `Getter,Property,Setter` |
| `CancelText` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |
| `Confirm` | `Getter,Property,Setter` |
| `ShowAction` | `Getter,Property,Setter` |
| `ShowCancel` | `Getter,Property,Setter` |
| `TextAlignment` | `Getter,Property,Setter` |
| `Title` | `Getter,Property` |
| `Type` | `Getter,Property` |

## NotificationView

| 成员 | 形状 |
|---|---|
| `Clear` | `Getter,Property,Setter` |
| `Clock` | `Getter,Property` |
| `Delete` | `Getter,Property,Setter` |

## UserView

| 成员 | 形状 |
|---|---|
| `LogOut` | `Getter,Property,Setter` |
| `OpenUrl` | `Getter,Property,Setter` |

## MonitorView

| 成员 | 形状 |
|---|---|
| `LinkChange` | `Getter,Property,Setter` |
| `OpenFilter` | `Getter,Property,Setter` |
| `OpenUrl` | `Getter,Property,Setter` |
| `Quicktask` | `Getter,Property,Setter` |
| `View` | `Getter,Property` |

## MonitorWindow

| 成员 | 形状 |
|---|---|
| `Exit` | `Getter,Property,Setter` |
| `Minimise` | `Getter,Property,Setter` |
| `ShowMonitor` | `Getter,Property,Setter` |
| `ShowSmartActions` | `Getter,Property,Setter` |
| `ShowUtilities` | `Getter,Property,Setter` |

## ExpressionExample

| 成员 | 形状 |
|---|---|
| `Description` | `Getter,Property,Setter` |
| `Key` | `Getter,Property,Setter` |
| `Output` | `Getter,Property,Setter` |

## ExpressionView

| 成员 | 形状 |
|---|---|
| `Copy` | `Getter,Property,Setter` |
| `Expressions` | `Getter,Property` |
| `Refresh` | `Getter,Property,Setter` |

## ProfileAdvancedView

| 成员 | 形状 |
|---|---|
| `Profile` | `Getter,Property` |

## ProfileCreatorView

| 成员 | 形状 |
|---|---|
| `AdvancedView` | `Getter,Property` |
| `BillingView` | `Getter,Property` |
| `Close` | `Getter,Property,Setter` |
| `Count` | `Getter,Property` |
| `IsBulk` | `Getter,Property` |
| `IsCreating` | `Getter,Property` |
| `Names` | `Getter,Property` |
| `Navigate` | `Getter,Property,Setter` |
| `PaymentView` | `Getter,Property` |
| `Profile` | `Getter,Property` |
| `Save` | `Getter,Property,Setter` |
| `ShippingView` | `Getter,Property` |
| `Summary` | `Getter,Property` |

## ProfileCsvEditorView

| 成员 | 形状 |
|---|---|
| `Apply` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |
| `ColumnChoices` | `Getter,Property` |
| `GroupName` | `Getter,Property` |
| `ProfileCount` | `Getter,Property` |

## ProfileCsvRow

| 成员 | 形状 |
|---|---|
| `FullySelected` | `Getter,Property,Setter` |
| `Number` | `Getter,Property,Setter` |
| `RowError` | `Getter,Property,Setter` |
| `RowStatus` | `Getter,Property,Setter` |

## ProfileGroupView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `GroupName` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |

## ProfilePaymentView

| 成员 | 形状 |
|---|---|
| `Profile` | `Getter,Property` |

## ProfileView

| 成员 | 形状 |
|---|---|
| `Clear` | `Getter,Property,Setter` |
| `Clone` | `Getter,Property,Setter` |
| `CreateGroup` | `Getter,Property,Setter` |
| `CreateTest` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `DeleteSelected` | `Getter,Property,Setter` |
| `EditSelected` | `Getter,Property,Setter` |
| `Groups` | `Getter,Property` |
| `MoveGroup` | `Getter,Property,Setter` |
| `OpenCreator` | `Getter,Property,Setter` |
| `OpenCsvEditor` | `Getter,Property,Setter` |
| `OpenSettings` | `Getter,Property,Setter` |

## ProxyCreatorView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |

## ProxyGroupView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Draft` | `Getter,Property` |
| `Reset` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |
| `TimeSpans` | `Getter,Property` |

## ProxyView

| 成员 | 形状 |
|---|---|
| `AddProxies` | `Getter,Property,Setter` |
| `ClearAll` | `Getter,Property,Setter` |
| `ClearFailed` | `Getter,Property,Setter` |
| `ClearOver` | `Getter,Property,Setter` |
| `CloneProxies` | `Getter,Property,Setter` |
| `CopyProxies` | `Getter,Property,Setter` |
| `CreateGroup` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `DeleteProxies` | `Getter,Property,Setter` |
| `Groups` | `Getter,Property` |
| `MoveGroup` | `Getter,Property,Setter` |
| `OpenSettings` | `Getter,Property,Setter` |
| `ProxyTesters` | `Getter,Property` |
| `Test` | `Getter,Property,Setter` |
| `TestAll` | `Getter,Property,Setter` |
| `TestAllKeybind` | `Getter,Property,Setter` |
| `TestProxies` | `Getter,Property,Setter` |

## AppearanceView

| 成员 | 形状 |
|---|---|
| `ResetDefaults` | `Getter,Property,Setter` |

## CaptchaProvidersView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `DisabledProviders` | `Getter,Property` |
| `Edit` | `Getter,Property,Setter` |
| `EnabledProviders` | `Getter,Property` |
| `FetchBalance` | `Getter,Property,Setter` |
| `Reorder` | `Getter,Property,Setter` |

## CloudflareSolversView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `FetchBalance` | `Getter,Property,Setter` |

## CustomSizesView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Clear` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Rows` | `Getter,Property` |
| `View` | `Getter,Property` |

## CustomStoresView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Clear` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Rows` | `Getter,Property` |
| `View` | `Getter,Property` |

## DataView

| 成员 | 形状 |
|---|---|
| `Backup` | `Getter,Property` |
| `DataProviders` | `Getter,Property` |
| `Export` | `Getter,Property` |
| `Reset` | `Getter,Property,Setter` |
| `Restore` | `Getter,Property,Setter` |
| `ViewBackups` | `Getter,Property,Setter` |
| `ViewLogs` | `Getter,Property,Setter` |

## ErrorEntry

| 成员 | 形状 |
|---|---|
| `Key` | `Getter,Property,Setter` |
| `Value` | `Getter,Property,Setter` |

## GeneralSettingsView

| 成员 | 形状 |
|---|---|
| `ProfileItems` | `Getter,Property` |

## GoogleAccountsView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Clear` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `Rows` | `Getter,Property` |
| `YouTube` | `Getter,Property,Setter` |

## HelpView

| 成员 | 形状 |
|---|---|
| `OpenUrl` | `Getter,Property,Setter` |

## ImapView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Clear` | `Getter,Property,Setter` |
| `Configure` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `DisconnectAycd` | `Getter,Property,Setter` |
| `Rows` | `Getter,Property` |

## KeyBindSection

| 成员 | 形状 |
|---|---|
| `Key` | `Getter,Property,Setter` |
| `Shortcuts` | `Getter,Property,Setter` |

## KeyBindsView

| 成员 | 形状 |
|---|---|
| `Delete` | `Getter,Property,Setter` |

## LocalizedOption

| 成员 | 形状 |
|---|---|
| `Text` | `Getter,Property` |
| `Value` | `Getter,Property,Setter` |

## AycdInboxCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Save` | `Getter,Property` |

## CaptchaProviderCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Creating` | `Getter,Property` |
| `Delete` | `Getter,Property` |
| `Properties` | `Getter,Property` |
| `Save` | `Getter,Property` |

## CloudflareSolverCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Creating` | `Getter,Property` |
| `Delete` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |

## GoogleAccountEditView

| 成员 | 形状 |
|---|---|
| `Account` | `Getter,Property` |
| `AccountName` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |
| `EditMode` | `Getter,Property` |
| `Proxy` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |

## ImapCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Save` | `Getter,Property` |

## PayPalAccountCreatorView

| 成员 | 形状 |
|---|---|
| `AutoReopen` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |
| `EditMode` | `Getter,Property` |
| `InactivateAfter` | `Getter,Property,Setter` |
| `Model` | `Getter,Property` |
| `Password` | `Getter,Property,Setter` |
| `ProxyGroup` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |
| `UseLoginProxy` | `Getter,Property,Setter` |

## SizeCreatorView

| 成员 | 形状 |
|---|---|
| `Clear` | `Getter,Property` |
| `Close` | `Getter,Property,Setter` |
| `Save` | `Getter,Property` |
| `Search` | `Getter,Property` |
| `SizeOptions` | `Getter,Property` |
| `ToggleSizeSelected` | `Getter,Property,Setter` |

## SizeOption

| 成员 | 形状 |
|---|---|
| `Selected` | `Getter,Property,Setter` |
| `Title` | `Getter,Property,Setter` |

## StoreCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Save` | `Getter,Property` |

## WebhookCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |

## NotificationsView

| 成员 | 形状 |
|---|---|
| `PlaySound` | `Getter,Property,Setter` |
| `ResetSound` | `Getter,Property,Setter` |
| `Select` | `Getter,Property,Setter` |
| `SelectSound` | `Getter,Property,Setter` |
| `Types` | `Getter,Property` |

## PayPalAccountsView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Clear` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `Rows` | `Getter,Property` |
| `Toggle` | `Getter,Property,Setter` |

## PaymentView

| 成员 | 形状 |
|---|---|
| `Configure` | `Getter,Property,Setter` |
| `DetectedProfiles` | `Getter,Property` |
| `Refresh` | `Getter,Property,Setter` |
| `SelectedProfiles` | `Getter,Property,Setter` |

## SettingsView

| 成员 | 形状 |
|---|---|
| `AppearanceView` | `Getter,Property` |
| `CaptchaProvidersView` | `Getter,Property` |
| `CloudflareSolversView` | `Getter,Property` |
| `CustomSizesView` | `Getter,Property` |
| `CustomStoresView` | `Getter,Property` |
| `DataView` | `Getter,Property` |
| `GeneralSettingsView` | `Getter,Property` |
| `GoogleAccountsView` | `Getter,Property` |
| `HelpView` | `Getter,Property` |
| `ImapView` | `Getter,Property` |
| `KeyBindsView` | `Getter,Property` |
| `LogOut` | `Getter,Property` |
| `NotificationsView` | `Getter,Property` |
| `PayPalAccountsView` | `Getter,Property` |
| `PaymentView` | `Getter,Property` |
| `Transition` | `Getter,Property,Setter` |
| `Update` | `Getter,Property` |
| `Version` | `Getter,Property` |
| `WebhookView` | `Getter,Property` |

## WebhookView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Test` | `Getter,Property` |

## ActionConfigEntry

| 成员 | 形状 |
|---|---|
| `Config` | `Getter,Property,Setter` |
| `Key` | `Getter,Property,Setter` |
| `Parameters` | `Getter,Property,Setter` |

## ActionRow

| 成员 | 形状 |
|---|---|
| `Action` | `Getter,Property,Setter` |
| `IsFirst` | `Getter,Property,Setter` |
| `Result` | `Getter,Property,Setter` |
| `Tooltip` | `Getter,Property` |

## ActionsModal

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Close` | `Getter,Property,Setter` |

## FilterInputEntry

| 成员 | 形状 |
|---|---|
| `Filter` | `Getter,Property,Setter` |
| `Input` | `Getter,Property,Setter` |
| `IsFirst` | `Getter,Property,Setter` |

## FilterRow

| 成员 | 形状 |
|---|---|
| `Filter` | `Getter,Property,Setter` |
| `Inputs` | `Getter,Property,Setter` |
| `IsFirst` | `Getter,Property,Setter` |
| `Passed` | `Getter,Property` |
| `Title` | `Getter,Property` |
| `ValueText` | `Getter,Property,Setter` |

## HistoryWindow

| 成员 | 形状 |
|---|---|
| `Exit` | `Getter,Property,Setter` |
| `Filter` | `Getter,Property,Setter` |
| `Minimise` | `Getter,Property,Setter` |
| `ShowAll` | `Getter,Property,Setter` |
| `SmartAction` | `Getter,Property` |
| `View` | `Getter,Property` |

## InputRow

| 成员 | 形状 |
|---|---|
| `Matched` | `Getter,Property,Setter` |
| `Text` | `Getter,Property,Setter` |

## PublishTemplateModal

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Groups` | `Getter,Property` |

## SmartActionsCreator

| 成员 | 形状 |
|---|---|
| `AddAction` | `Getter,Property,Setter` |
| `AddFilter` | `Getter,Property,Setter` |
| `AddInput` | `Getter,Property,Setter` |
| `Clone` | `Getter,Property,Setter` |
| `CloseOverlay` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `DeleteAction` | `Getter,Property,Setter` |
| `DeleteFilter` | `Getter,Property,Setter` |
| `DeleteInput` | `Getter,Property,Setter` |
| `DeleteParam` | `Getter,Property,Setter` |
| `Exit` | `Getter,Property,Setter` |
| `IsEditing` | `Getter,Property` |
| `Minimise` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |
| `Settings` | `Getter,Property,Setter` |
| `SmartAction` | `Getter,Property` |
| `TimeSpans` | `Getter,Property` |
| `ToggleFilterBehaviour` | `Getter,Property,Setter` |
| `UseTemplate` | `Getter,Property,Setter` |

## SmartActionsView

| 成员 | 形状 |
|---|---|
| `Clock` | `Getter,Property` |
| `Clone` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `Export` | `Getter,Property,Setter` |
| `Filters` | `Getter,Property` |
| `OpenCreator` | `Getter,Property,Setter` |
| `View` | `Getter,Property` |
| `ViewLogs` | `Getter,Property,Setter` |

## TemplateGroup

| 成员 | 形状 |
|---|---|
| `Key` | `Getter,Property,Setter` |
| `Templates` | `Getter,Property,Setter` |

## ElementCell

| 成员 | 形状 |
|---|---|
| `Column` | `Getter,Property,Setter` |
| `ColumnSpan` | `Getter,Property,Setter` |
| `Content` | `Getter,Property,Setter` |
| `Name` | `Getter,Property,Setter` |

## GroupSummary

| 成员 | 形状 |
|---|---|
| `Clone` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `PinGroup` | `Getter,Property,Setter` |
| `StartAll` | `Getter,Property,Setter` |
| `StopAll` | `Getter,Property,Setter` |

## StaggerStartView

| 成员 | 形状 |
|---|---|
| `Cancel` | `Getter,Property,Setter` |
| `Start` | `Getter,Property,Setter` |
| `TotalTasks` | `Getter,Property` |

## TaskDetailsView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Task` | `Getter,Property` |

## TaskGroupListView

| 成员 | 形状 |
|---|---|
| `Groups` | `Getter,Property` |

## TaskGroupView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `CloudflareSolvers` | `Getter,Property` |
| `Delete` | `Getter,Property,Setter` |
| `Draft` | `Getter,Property` |
| `Link` | `Getter,Property,Setter` |
| `Reset` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |
| `TimeSpans` | `Getter,Property` |

## TaskCreatorCartView

| 成员 | 形状 |
|---|---|
| `Add` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `SizeItems` | `Getter,Property` |

## TaskCreatorMainView

| 成员 | 形状 |
|---|---|
| `ProfileGroupItems` | `Getter,Property` |
| `ProfileItems` | `Getter,Property` |
| `ShowCartView` | `Getter,Property,Setter` |
| `SizeItems` | `Getter,Property` |

## TaskCreatorView

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Create` | `Getter,Property,Setter` |

## TaskView

| 成员 | 形状 |
|---|---|
| `ClearAll` | `Getter,Property,Setter` |
| `CloneSelected` | `Getter,Property,Setter` |
| `CopyUrl` | `Getter,Property,Setter` |
| `CreateGroup` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `DeleteSelected` | `Getter,Property,Setter` |
| `Edit` | `Getter,Property,Setter` |
| `EditAll` | `Getter,Property,Setter` |
| `EditSelected` | `Getter,Property,Setter` |
| `ForceStartSelected` | `Getter,Property,Setter` |
| `LinkChange` | `Getter,Property,Setter` |
| `MoveGroup` | `Getter,Property,Setter` |
| `NextGroup` | `Getter,Property,Setter` |
| `OpenBrowser` | `Getter,Property,Setter` |
| `OpenGroupPopup` | `Getter,Property,Setter` |
| `OpenSettings` | `Getter,Property,Setter` |
| `OpenSolvers` | `Getter,Property,Setter` |
| `OpenStaggerStart` | `Getter,Property,Setter` |
| `OpenTaskCreator` | `Getter,Property,Setter` |
| `OpenTaskView` | `Getter,Property,Setter` |
| `PinGroups` | `Getter,Property,Setter` |
| `PreviousGroup` | `Getter,Property,Setter` |
| `Quicktask` | `Getter,Property,Setter` |
| `Search` | `Getter,Property,Setter` |
| `SetQuery` | `Getter,Property,Setter` |
| `StartAll` | `Getter,Property,Setter` |
| `StartSelected` | `Getter,Property,Setter` |
| `StopAll` | `Getter,Property,Setter` |
| `StopSelected` | `Getter,Property,Setter` |
| `Toggle` | `Getter,Property,Setter` |

## TimeSpanOption

| 成员 | 形状 |
|---|---|
| `Name` | `Getter,Property,Setter` |
| `Value` | `Getter,Property,Setter` |

## StoreGroupModal

| 成员 | 形状 |
|---|---|
| `Close` | `Getter,Property,Setter` |
| `Delete` | `Getter,Property,Setter` |
| `IsEditing` | `Getter,Property` |
| `RemoveStore` | `Getter,Property,Setter` |
| `Save` | `Getter,Property,Setter` |
| `Stores` | `Getter,Property` |
| `Title` | `Getter,Property` |

## UtilitiesView

| 成员 | 形状 |
|---|---|
| `CloneStoreGroup` | `Getter,Property,Setter` |
| `CreateStoreGroup` | `Getter,Property,Setter` |
| `DeleteStoreGroup` | `Getter,Property,Setter` |
| `EditStoreGroup` | `Getter,Property,Setter` |
| `StoreGroups` | `Getter,Property` |


---

## 系统差异：273 个"动作"成员，原件是属性、复刻件是方法（R368）

`python tools/shape_audit.py` 会列出所有"池子说有 Setter、而复刻件不是可写属性"的成员：

```
members with accessor evidence : 465
  settable                     : 327
  getter-only                  : 138
mismatches（可写证据 vs 复刻件写法）: 273 → 273（修 ComboBoxEdit 两条后 272）
```

### 这是什么差异

原件的 XAML 用 `Command="{Binding Xxx}"` 绑动作，所以**每个动作都是 `ICommand` 属性**；
复刻件用手写控件树，动作就是方法。**行为等价，形状不同。**

### 为什么不在这一轮全改

- 复刻件**没有任何 XAML 绑定**，形状差异不影响运行；
- 273 处全改成 `ICommand` 属性是纯形式重构，风险大于收益（R352 的教训还热着）。

### 规则（已写入 METHOD §13）

**新增"用户动作"成员时，写成 `ICommand` 属性**（与原件同形），存量不动。
