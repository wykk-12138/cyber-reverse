# 原版绑定描述符表（生成文件，请勿手改）

> 由 `python analysis/binding_descriptors.py` 生成。原版把编译期绑定描述符以可读串摊在字符串池里，
> 形式是 `<声明类型>,<程序集>.<成员>!<Getter|Setter>`。**这是原版自己的说法**，不是推断。

| 项 | 值 |
|---|---|
| 描述符块（去重） | 932 |
| 解析出的三元组（去重） | 1637 |
| 涉及声明类型 | 215 |
| Getter 条目 | 950 |
| Setter 条目 | 687 |
| 与 `xaml_bindings.json` 共有 | 819 |
| **仅描述符表有**（XAML 表看不见） | **132** |
| 仅 XAML 表有（需单独解释，**不等于不存在**） | 0 |

## 仅描述符表有的 (type, member)

这些就是 `xaml_bindings.json` 看不到、但原版确实绑定的成员。

- `Avalonia.Collections.AvaloniaList`1` . `Count`
- `Avalonia.Collections.AvaloniaList`1` . `Count_105`
- `Avalonia.Collections.AvaloniaList`1` . `Count_26`
- `Avalonia.Collections.AvaloniaList`1` . `Count_33`
- `Avalonia.Collections.AvaloniaList`1` . `Count_37`
- `Avalonia.Collections.AvaloniaList`1` . `Count_41`
- `Avalonia.Collections.AvaloniaList`1` . `Count_45`
- `Avalonia.Collections.AvaloniaList`1` . `Count_47`
- `Avalonia.Collections.AvaloniaList`1` . `Count_59`
- `Avalonia.Collections.AvaloniaList`1` . `Count_69`
- `Avalonia.Collections.AvaloniaList`1` . `Count_76`
- `Avalonia.Collections.AvaloniaList`1` . `Count_81`
- `Avalonia.Collections.AvaloniaList`1` . `Count_84`
- `Avalonia.Collections.DataGridCollectionView` . `Count`
- `Avalonia.Collections.DataGridCollectionViewGroup` . `Key`
- `Avalonia.Controls.CommandBar` . `OverflowItems`
- `Avalonia.Controls.CommandBar` . `VisiblePrimaryCommands`
- `Avalonia.Controls.Notifications.INotification` . `Message`
- `Avalonia.Controls.Notifications.INotification` . `Title`
- `Avalonia.Controls.ProgressBar` . `TemplateSettings`
- `Avalonia.Data.CompiledBinding` . `Converter`  *(有 setter)*
- `Avalonia.Data.CompiledBinding` . `ConverterParameter`  *(有 setter)*
- `Avalonia.Data.MultiBinding` . `Bindings`  *(有 setter)*
- `Avalonia.Data.MultiBinding` . `Converter`  *(有 setter)*
- `Avalonia.Data.TemplateBinding` . `Converter`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserItemViewModel` . `DisplayName`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserItemViewModel` . `IconKey`
- `Avalonia.Dialogs.Internal.ManagedFileChooserItemViewModel` . `Modified`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserItemViewModel` . `Size`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserItemViewModel` . `Type`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `FileName`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `Filters`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `Items`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `Location`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `QuickLinks`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `QuickLinksSelectedIndex`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `SelectedFilter`  *(有 setter)*
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `SelectedItems`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `SelectingFolder`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `SelectionMode`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `ShowFilters`
- `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` . `ShowHiddenFiles`  *(有 setter)*
- `Avalonia.Rect` . `Height`
- `Avalonia.Rect` . `Width`
- `Avalonia.Size` . `Height`
- `Avalonia.Size` . `Width`
- `Avalonia.Styling.ControlTheme` . `BasedOn`  *(有 setter)*
- `Avalonia.Styling.Setter` . `Value`  *(有 setter)*
- `Avalonia.Vector` . `Y`
- `AvaloniaEdit.CodeCompletion.ICompletionData` . `Content`
- `AvaloniaEdit.CodeCompletion.ICompletionData` . `Image`
- `AvaloniaEdit.CodeCompletion.IOverloadProvider` . `Count`
- `AvaloniaEdit.CodeCompletion.IOverloadProvider` . `CurrentContent`
- `AvaloniaEdit.CodeCompletion.IOverloadProvider` . `CurrentHeader`
- `AvaloniaEdit.CodeCompletion.IOverloadProvider` . `CurrentIndexText`
- `AvaloniaEdit.Search.SearchPanel` . `TextEditor`
- `DotNetBrowser.Autofill.Suggestion` . `AddressOrFullname`
- `DotNetBrowser.Autofill.Suggestion` . `CreditCardInfo`
- `DotNetBrowser.Autofill.Suggestion` . `HiddenPassword`
- `DotNetBrowser.AvaloniaUi.Autofill.SuggestionsPopup` . `AddressVisibility`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Autofill.SuggestionsPopup` . `CardVisibility`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Autofill.SuggestionsPopup` . `PasswordVisibility`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Autofill.SuggestionsPopup` . `Suggestions`
- `DotNetBrowser.AvaloniaUi.BrowserView` . `MenuItems`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.ContextMenu.MenuItemViewModel` . `Command`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.ContextMenu.MenuItemViewModel` . `Header`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.ContextMenu.MenuItemViewModel` . `IsEnabled`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.ContextMenu.MenuItemViewModel` . `MenuItems`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.ActionDialogViewModel` . `CancelActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.ActionDialogViewModel` . `DialogTitle`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.ActionDialogViewModel` . `Message`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.ActionDialogViewModel` . `OkActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `CancelActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `CancelVisibility`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `DialogTitle`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `Input`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `InputVisibility`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `Message`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` . `OkActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.SelectCertificateDialogViewModel` . `CancelActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.SelectCertificateDialogViewModel` . `DialogTitle`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.SelectCertificateDialogViewModel` . `Message`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.SelectCertificateDialogViewModel` . `OkActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.SelectCertificateDialogViewModel` . `SelectedCertificate`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.UserDataProfileDialogViewModel` . `CancelActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.UserDataProfileDialogViewModel` . `DialogTitle`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.UserDataProfileDialogViewModel` . `Info`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.UserDataProfileDialogViewModel` . `Message`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.UserDataProfileDialogViewModel` . `OkActionText`  *(有 setter)*
- `DotNetBrowser.AvaloniaUi.Dropdown.DropdownPopup` . `CustomPlacementCallback`
- `DotNetBrowser.AvaloniaUi.Dropdown.DropdownPopup` . `Items`  *(有 setter)*
- `DotNetBrowser.Browser.Widgets.Dropdown.DropdownItem` . `IsEnabled`
- `DotNetBrowser.Browser.Widgets.Dropdown.DropdownItem` . `IsSelectable`
- `DotNetBrowser.Browser.Widgets.Dropdown.DropdownItem` . `Label`
- `DotNetBrowser.Net.Certificates.Certificate` . `SubjectName`
- `F.Variant` . `Name`  *(有 setter)*
- `OverloadViewerBCollapseIfSingleOverloadConvertervAvaloniaEdit.Document.TextDocument` . `Text`
- `System.Array` . `Length`
- `System.Collections.Generic.Dictionary`2` . `Keys`
- `System.Collections.Generic.IReadOnlyCollection`1` . `Count`
- `System.Collections.Generic.IReadOnlyCollection`1` . `Count_53`
- `System.Collections.Generic.List`1` . `Count`
- `System.Collections.Generic.List`1` . `Count_107`
- `System.Collections.Generic.List`1` . `Count_29`
- `System.Collections.Generic.List`1` . `Count_67`
- `System.Collections.ObjectModel.Collection`1` . `Count`
- `System.Collections.ObjectModel.Collection`1` . `Count_103`
- `System.Collections.ObjectModel.Collection`1` . `Count_13`
- `System.Collections.ObjectModel.Collection`1` . `Count_16`
- `System.Collections.ObjectModel.Collection`1` . `Count_17`
- `System.Collections.ObjectModel.Collection`1` . `Count_24`
- `System.Collections.ObjectModel.Collection`1` . `Count_27`
- `System.Collections.ObjectModel.Collection`1` . `Count_34`
- `System.Collections.ObjectModel.Collection`1` . `Count_38`
- `System.Collections.ObjectModel.Collection`1` . `Count_40`
- `System.Collections.ObjectModel.Collection`1` . `Count_43`
- `System.Collections.ObjectModel.Collection`1` . `Count_50`
- `System.Collections.ObjectModel.Collection`1` . `Count_54`
- `System.Collections.ObjectModel.Collection`1` . `Count_63`
- `System.Collections.ObjectModel.Collection`1` . `Count_66`
- `System.Collections.ObjectModel.Collection`1` . `Count_70`
- `System.Collections.ObjectModel.Collection`1` . `Count_73`
- `System.Collections.ObjectModel.Collection`1` . `Count_74`
- `System.Collections.ObjectModel.Collection`1` . `Count_75`
- `System.Collections.ObjectModel.Collection`1` . `Count_78`
- `System.Collections.ObjectModel.Collection`1` . `Count_80`
- `System.Collections.ObjectModel.Collection`1` . `Count_90`
- `System.DateTime` . `Day`
- `System.Exception` . `Message`
- `System.Exception` . `Source`  *(有 setter)*
- `vAvaloniaEdit.Document.TextDocument` . `Text`  *(有 setter)*
- `xDotNetBrowser.Autofill.Suggestion` . `Value`

## 按声明类型统计（前 40）

| 类型 | 描述符条数 |
|---|---|
| `Cybersole.Global.Settings` | 68 |
| `Cybersole.Ui.Views.Tasks.TaskView` | 60 |
| `Cybersole.Ui.Views.SmartActions.SmartActionsCreator` | 35 |
| `Cybersole.Models.CreateModel` | 34 |
| `Cybersole.Models.TaskGroup` | 33 |
| `Cybersole.Ui.Views.Proxies.ProxyView` | 32 |
| `Cybersole.Models.EditValue`1` | 28 |
| `Cybersole.Models.BotTask` | 27 |
| `Cybersole.Models.CreateInputModel` | 24 |
| `Cybersole.SmartActions.SmartAction` | 24 |
| `Cybersole.Ui.Views.Profiles.ProfileView` | 23 |
| `System.Collections.ObjectModel.Collection`1` | 22 |
| `Cybersole.Ui.Views.Accounts.AccountGrid` | 21 |
| `Cybersole.Ui.Views.Settings.SettingsView` | 20 |
| `Cybersole.Models.Address` | 19 |
| `Cybersole.Ui.Views.MainWindow` | 19 |
| `Cybersole.Ui.Views.Modals.MessageBoxDialog` | 18 |
| `Avalonia.Dialogs.Internal.ManagedFileChooserViewModel` | 17 |
| `Cybersole.CloudflareSolvers.CloudflareSolver` | 16 |
| `Cybersole.Models.BaseCheckout` | 16 |
| `Cybersole.Models.Solver` | 16 |
| `Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView` | 16 |
| `Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView` | 16 |
| `Cybersole.CaptchaProviders.CaptchaProvider` | 15 |
| `Cybersole.Models.ProxyGroup` | 15 |
| `Cybersole.Ui.Views.SmartActions.SmartActionsView` | 15 |
| `Cybersole.Models.Product` | 14 |
| `Cybersole.Models.SolverSettings` | 14 |
| `Cybersole.Ui.Views.Browser.CustomBrowser` | 14 |
| `DotNetBrowser.AvaloniaUi.Dialogs.ViewModels.CustomizableDialogViewModel` | 14 |
| `Avalonia.Collections.AvaloniaList`1` | 13 |
| `Cybersole.Ui.Views.Tasks.Modals.TaskGroupView` | 13 |
| `Cybersole.Models.NotificationOptions` | 12 |
| `Cybersole.Models.Profile` | 12 |
| `Cybersole.Ui.Views.Tasks.Modals.GroupSummary` | 12 |
| `Cybersole.Models.Store` | 11 |
| `Cybersole.Models.User` | 11 |
| `Cybersole.Ui.Views.Analytics.Modals.ReleaseView` | 11 |
| `Cybersole.Ui.Views.Settings.DataView` | 11 |
| `Cybersole.Ui.Views.Settings.GoogleAccountsView` | 11 |

