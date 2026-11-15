# 文案缺口三分类（自动生成：`python analysis/copy_triage.py`）

> 生成物，勿手改。汇总口径见 `docs/METRICS.md`（R433 裁决 1）。

| 堆 | 条数 | 含义 |
|---|---|---|
| 措辞不同 | 214 | 源码已有这句意思，字面不同（近似度 ≥ 0.55） |
| 真缺失 | 4 | 宿主类存在，但这句文案没写 |
| 无宿主 | 15 | 树里没有对应前缀的类 —— 整块功能未实现 |
| **合计** | **233** | 全池 1142 键中无字面匹配者 |

> **归属判定是启发式的**：`area` 前缀以子串形式在某个类名里出现即算"有宿主"。它会把 `Creator` 认到 `TaskCreatorView` 头上，也可能认错。**"真缺失"这一堆在动手前要逐条确认。**

## 措辞不同（214）

| 键 | 原文 | 源码里最接近的 | 近似度 | 文件 |
|---|---|---|---|---|
| `Advanced.MonitorMode` | Monitor Mode | Monitor mode | 1.00 | `TaskEditorWindow.cs` |
| `Cart.MinPrice` | Min Price | Min price | 1.00 | `SmartActionEditorWindow.cs` |
| `Creator.Cloudflare.AddTitle` | Add Cloudflare Provider | Add Cloudflare provider | 1.00 | `ProviderViews.cs` |
| `Creator.Google.EditTitle` | Edit Google Account | Edit Google account | 1.00 | `CaptchaViews.cs` |
| `Creator.Google.NewTitle` | New Google Account | New Google account | 1.00 | `SettingsModals.cs` |
| `Creator.Google.Title` | Edit Google Account | Edit Google account | 1.00 | `CaptchaViews.cs` |
| `Creator.PayPal.AutoReopen` | Auto Reopen | Auto reopen | 1.00 | `SettingsViews.cs` |
| `Creator.PayPal.EditTitle` | Edit PayPal Account | Edit PayPal account | 1.00 | `SettingsModals.cs` |
| `Creator.PayPal.NewTitle` | New PayPal Account | New PayPal account | 1.00 | `SettingsModals.cs` |
| `ProfileAddress.FirstName` | First Name | First name | 1.00 | `ProfileEditorWindow.cs` |
| `ProfileAddress.LastName` | Last Name | Last name | 1.00 | `ProfileEditorWindow.cs` |
| `ProfileCreator.ProfileName` | Profile Name | Profile name | 1.00 | `ProfileViews.cs` |
| `ProfileCreator.Title.New` | New Profile | New profile | 1.00 | `ProfileEditorWindow.cs` |
| `Proxies.Groups` | PROXY GROUPS | Proxy groups | 1.00 | `ProviderViews.cs` |
| `Settings.Imap.Status.Disconnected` | Disconnected | disconnected | 1.00 | `ImapMailProvider.cs` |
| `SmartActionSettings.RunInterval` | Run Interval | Run interval | 1.00 | `SmartActionViews.cs` |
| `SmartActionSettings.RunOnce` | Run Once | Run once | 1.00 | `SmartActionViews.cs` |
| `SmartActionsCreator.NewFilter` | New Filter | New filter | 1.00 | `SmartActionViews.cs` |
| `Solver.Settings.ImageChallenge` | Image Challenge | Image challenge | 1.00 | `SolverWindow.cs` |
| `Solver.Settings.MultiSelect` | Multi Select | Multi select | 1.00 | `SolverWindow.cs` |
| `Solver.Settings.QuestionSharing` | Question Sharing | Question sharing | 1.00 | `SolverWindow.cs` |
| `Solver.Settings.SquareChallenge` | Square Challenge | Square challenge | 1.00 | `SolverWindow.cs` |
| `TaskCreator.ScheduledStart` | Scheduled Start | Scheduled start | 1.00 | `TaskEditorWindow.cs` |
| `TaskDetails.MonitorMode` | Monitor Mode | Monitor mode | 1.00 | `TaskEditorWindow.cs` |
| `TaskDetails.PriceCheck` | Price Check | Price check | 1.00 | `TasksViews.cs` |
| `TaskDetails.StartTime` | Start Time | Start time | 1.00 | `TasksViews.cs` |
| `TaskGroups.Order.NewestPlaceholder` | NEWEST | Newest | 1.00 | `ProxyView.cs` |
| `Update.CheckForUpdates` | Check for updates | CHECK FOR UPDATES | 1.00 | `SettingsShell.cs` |
| `Utilities.StoreGroups.Delete.UsedMessageFormat` | This will permanently delete the store group "{0}".\nIt is used by {1} smart act | This will permanently delete the store group "{0}".
It is used by {0} smart acti | 0.99 | `UtilitiesViews.cs` |
| `Settings.Stores.DeleteConfirm.MessageFormat` | Are you sure you want to delete {0} presets?\nYou cannot undo this action. | Are you sure you want to delete {0} presets?\
You cannot undo this action. | 0.99 | `SettingsShell.cs` |
| `Settings.Sizes.DeleteConfirm.MessageFormat` | Are you sure you want to delete {0} sizes?\nYou cannot undo this action. | Are you sure you want to delete {0} sizes?\
You cannot undo this action. | 0.99 | `SettingsShell.cs` |
| `Accounts.Group.DeleteConfirm.MessageFormat` | Are you sure you want to delete the {0} account group?\nYou cannot undo this act | Are you sure you want to delete the {0} account group?
You cannot undo this acti | 0.98 | `AccountModals.cs` |
| `Accounts.DeleteConfirm.MessageFormat` | Are you sure you want to delete {0} accounts?\nYou cannot undo this action. | Are you sure you want to delete {0} accounts?
You cannot undo this action. | 0.98 | `AccountGrid.cs` |
| `Profiles.DeleteConfirm.MessageFormat` | Are you sure you want to delete {0} profiles?\nYou cannot undo this action. | Are you sure you want to delete {0} profiles?
You cannot undo this action. | 0.98 | `ProfileViews.cs` |
| `Proxies.DeleteConfirm.MessageFormat` | Are you sure you want to delete {0} proxies?\nYou cannot undo this action. | Are you sure you want to delete {0} proxies?
You cannot undo this action. | 0.98 | `ProxyView.cs` |
| `Tasks.DeleteConfirm.MessageFormat` | Are you sure you want to delete {0} tasks?\nYou cannot undo this action. | Are you sure you want to delete {0} tasks?
You cannot undo this action. | 0.98 | `TaskView.cs` |
| `TaskGroup.Tab.Delays.Tooltip` | Group specific delays.\n\nIf none are set, global delays will be used, you can a | Group specific delays.

If none are set, global delays will be used, you can adj | 0.97 | `TasksViews.cs` |
| `ProfilePayment.PhoneNumber` | Phone Number | phoneNumber | 0.96 | `NikeFlow.cs` |
| `ProxyCreator.ImportFormat` | Import ({0}) New Proxies | Import (0) New Proxies | 0.96 | `MainWindow.cs` |
| `Checkout.Tracking` | Tracking | /tracking | 0.94 | `NetworkRecorder.cs` |
| `Creator.Shipping.NamePlaceholder` | Shipping Rate Name | shippingRateName | 0.94 | `ShopifyFlow.cs` |
| `TemplateView.Title` | Templates | Template | 0.94 | `SettingsModals.cs` |
| `Common.Hour12` | 12 Hour | 12 hours | 0.93 | `Tasks.cs` |
| `Common.Hour24` | 24 Hour | 24 hours | 0.93 | `ProviderViews.cs` |
| `Common.Loading` | Loading | loading… | 0.93 | `CustomBrowserWindow.cs` |
| `ProfileAddress.ZipCode` | Zip Code | zipCode | 0.93 | `FootsitesFlow.cs` |
| `ProxyTester.Test.Placeholder` | Test on | Test On: | 0.93 | `MainViewModel.cs` |
| `Creator.Aycd.ModalTitle` | Connect AYCD Inbox | Disconnect AYCD Inbox | 0.92 | `SettingsShell.cs` |
| `SmartActionsCreator.NoActions` | No Actions | (no actions) | 0.91 | `SmartActionViews.cs` |
| `TaskGroups.Context.StopAll` | Stop All Tasks | Stopped all tasks | 0.90 | `MainViewModel.cs` |
| `Solver.Settings.AutoClick` | Auto-Click | Auto click | 0.90 | `SolverWindow.cs` |
| `Advanced.Section.MonitorDelays` | Monitor & Delays | Monitor delay | 0.90 | `TasksViews.cs` |
| `ProxyTester.Custom.Placeholder` | Enter site URL | Enter store URL | 0.90 | `ProviderViews.cs` |
| `Creator.Cloudflare.EditTitle` | Edit Cloudflare Provider | Add Cloudflare provider | 0.89 | `ProviderViews.cs` |
| `SmartActionsCreator.ActionOne` | 1 Action Saved | Action saved. | 0.89 | `SmartActionViews.cs` |
| `Solver.TestHCaptcha` | Test hCaptcha | text captcha | 0.88 | `CybersoleHosts.cs` |
| `Creator.Captcha.EditTitle` | Edit Captcha Provider | New captcha provider | 0.88 | `SettingsModals.cs` |
| `Creator.Shipping.SaveAs` | Save as | Save Task | 0.88 | `TasksViews.cs` |
| `ActionsModal.Title` | Select Action | Select an action. | 0.87 | `SmartActionViews.cs` |
| `Creator.Captcha.AddTitle` | Add Captcha Provider | Captcha Providers | 0.86 | `UiKit.cs` |
| `Creator.PayPal.Title` | Add PayPal Account | Edit PayPal account | 0.86 | `SettingsModals.cs` |
| `Common.Download` | Download | onload | 0.86 | `GlobalSurfaceTable.Generated.cs` |
| `ProxyTester.TestAll.Title` | Test All Proxies | Test Proxies | 0.86 | `ProxyGrid.cs` |
| `SmartActions.Result.Filtered` | Filtered | filter | 0.86 | `CssProperties.Generated.cs` |
| `SmartActionsCreator.SaveButton` | Save Smart Action | New smart action | 0.85 | `SmartActionViews.cs` |
| `Solver.TestReCaptcha` | Test ReCaptcha | text captcha | 0.85 | `CybersoleHosts.cs` |
| `TaskGroups.Context.StartAll` | Start All Tasks | Start Tasks | 0.85 | `TaskGrid.cs` |
| `ActionsModal.Empty` | No actions match your search | No stores matched your search | 0.84 | `AccountView.cs` |
| `Creator.Imap.ModalTitle` | Add Imap Account | no imap account | 0.84 | `ImapMailProvider.cs` |
| `Creator.Imap.Title` | Add Email Account | Email Accounts | 0.84 | `SettingsShell.cs` |
| `Creator.Shipping.Title` | Add Shipping Rate | Shipping rates | 0.84 | `SettingsModals.cs` |
| `TemplateView.FromTemplate` | Or from a template | From template | 0.84 | `SmartActionViews.cs` |
| `Common.Pause` | Pause | onpause | 0.83 | `GlobalSurfaceTable.Generated.cs` |
| `Creator.Google.SaveAccount` | Save Account | Move account | 0.83 | `AccountMoveView.cs` |
| `Creator.PayPal.SaveAccount` | Save Account | Move account | 0.83 | `AccountMoveView.cs` |
| `SmartActionSettings.Title` | Smart Action Settings | Action settings | 0.83 | `SmartActionViews.cs` |
| `Advanced.MultipleModes` | Multiple modes | Multiple stores | 0.83 | `TasksViews.cs` |
| `Solver.Settings.BoundingBox` | Bounding Box | Auto bounding box | 0.83 | `SolverWindow.cs` |
| `SmartActionsCreator.NoTrigger` | No Trigger | Trigger | 0.82 | `SmartActionEditorWindow.cs` |
| `SmartActionsCreator.Step1Trigger` | 1. Trigger | Trigger | 0.82 | `SmartActionEditorWindow.cs` |

## 真缺失（4）

| 键 | 原文 | 归属（启发式） |
|---|---|---|
| `Cart.Color.Placeholder` | Color (blank for random) | `Cart` |
| `Creator.Captcha.CaptchaTypesTooltip` | Which captchas to send to this service | `Creator` |
| `Creator.Cloudflare.Hint` | Pick this provider in a task group's Captcha tab to use it for that group's Cloudflare challenges. | `Creator` |
| `SmartActionsCreator.NeedAtLeastOneAction` | You must have at least one action | `SmartActionsCreator` |

## 无宿主（15）

| 键 | 原文 | 前缀 |
|---|---|---|
| `AccountSelectionMode.Description.MatchProfile` | Automatically assigns an account based on the task's profile email. The task will not proceed if no matching a | `AccountSelectionMode` |
| `AccountSelectionMode.Description.Random` | Automatically assigns a random account to each task at start, ensuring diverse task distribution. | `AccountSelectionMode` |
| `CaptchaSource.Description.All` | Route captchas to both in-bot and third party solvers. (Default) | `CaptchaSource` |
| `CaptchaSource.Description.Local` | Route captchas exclusively to your in-bot solvers. | `CaptchaSource` |
| `CaptchaSource.Description.Mobile` | Route captchas exclusively to the mobile app / api. | `CaptchaSource` |
| `CaptchaSource.Description.ThirdParty` | Route captchas exclusively to third party solvers. | `CaptchaSource` |
| `ExceedBehaviour.Description.Local` | Tasks will continue to run and revert to your local IP. | `ExceedBehaviour` |
| `ExceedBehaviour.Description.None` | Tasks will continue to run and use the proxy group. | `ExceedBehaviour` |
| `MonitorMode.Description.Monitor` | Tasks will wait for the in-bot monitor to detect a new product or restock and use the data provided by the mon | `MonitorMode` |
| `MonitorMode.Description.Shared` | Only a few tasks will monitor the selected store at the specified monitor delay. The products found will then  | `MonitorMode` |
| `MonitorMode.Description.Task` | Each task will constantly monitor the selected store at the specified monitor delay. This will ensure you have | `MonitorMode` |
| `ProfileAddress.CityPlaceholder` | New York City | `ProfileAddress` |
| `TimeAgo.OneDayAgo` | 1 day ago | `TimeAgo` |
| `Update.Latest.Message` | You are already on the latest version. | `Update` |
| `Update.Ready.Message` | A restart is required to install this update | `Update` |
