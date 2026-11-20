# 成员形状差异：84 条逐条处置

> 生成物：`python analysis/shape_gaps_report.py`。数据来自 `python tools/shape_audit.py --baseline` 的原始输出，
> 加上对 `replica/src/**/*.cs` 的**名字**搜索。
> 判据 a 要求把缺口结案（可做 / 结构差异 / 不可得）—— 这份文件就是那一步。

## 怎么读

- `evidence=` 是原版绑定描述符里记的访问器种类；`replica=` 是复刻件里同名成员的形状。
- **处置是机械判据**，只看源码文本，不含任何行为证据。它能被读者反驳，这正是它的用处。

## 汇总

| 处置 | 条数 |
|---|---|
| 需要选择模型 | 39 |
| Unknown（同名撞名，判据无判别力） | 22 |
| 结构差异，不补 | 17 |
| 计算属性（不加虚设 setter） | 4 |
| 真缺 | 1 |
| 可能改名，判据弱 | 1 |

## 逐条

### `AccountGrid.Delete`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Delete` 是通用名，源码里有 18 个类都叫它（如 `TaskKeyBinds.Delete`、`ProxyKeyBinds.Delete`、`BillingKeyBinds.Delete`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `AccountGrid.Edit`

- evidence: `Getter,Property,Setter`   replica: `prop-get`
- 处置：**计算属性（不加虚设 setter）**：`AccountGrid.Edit` 是由其它状态派生/投影的只读属性（`computed-expr`），为其增加空 setter 会制造不落地状态。

### `AccountGroupView.Delete`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Delete` 是通用名，源码里有 18 个类都叫它（如 `TaskKeyBinds.Delete`、`ProxyKeyBinds.Delete`、`BillingKeyBinds.Delete`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `AccountGroupView.Save`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Save` 是通用名，源码里有 11 个类都叫它（如 `ConfigurationStore.Save`、`SmartActionEditorWindow.Save`、`ProfileCreatorView.Save`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `ActionsModal.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `AnalyticsView.ChangeChart`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `AnalyticsView.OpenRelease`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `AycdInboxCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `BotTask.Task`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：静态反编译已确认原版 `BotTask.Task`（`0x14080CA20`）CLR 类型为 `TaskBase`（`0x144C963C8`，`StoreModuleBase` 的 69 个店铺子类的基类，承载 `Steps` 与 `Account`）；复刻件保持 `Cybersole.Core` 纯数据层（不反向引用 `Cybersole.Http` / `Cybersole.Stores`），`Steps` 与 `AccountId` 直接落在 `BotTask` 上，运行态由 `TaskEngine.TaskRuntime` 承载，不补跨层句柄属性。

### `CaptchaProviderCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `CaptchaProvidersView.Reorder`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CloudflareSolverCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `CreateGroupModal.Create`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Create` 是通用名，源码里有 3 个类都叫它（如 `AppServices.Create`、`ReleaseSitelistView.Create`、`TaskCreatorView.Create`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `CustomBrowser.Autofill`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**真缺**：全源码里没有 `Autofill` 这个名字。补它需要先知道它绑到什么。

### `CustomBrowser.Back`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CustomBrowser.Exit`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CustomBrowser.Forward`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CustomBrowser.Minimise`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CustomBrowser.Refresh`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CustomSizesView.Delete`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `CustomStoresView.Delete`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `DataView.ViewBackups`

- evidence: `Getter,Property,Setter`   replica: `prop-get`
- 处置：**计算属性（不加虚设 setter）**：`DataView.ViewBackups` 是由其它状态派生/投影的只读属性（`computed-expr`），为其增加空 setter 会制造不落地状态。

### `DesktopNotification.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `ExpressionView.Refresh`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Refresh` 是通用名，源码里有 15 个类都叫它（如 `BillingView.Refresh`、`SmartActionEditorWindow.Refresh`、`CreateGroupModal.Refresh`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `GoogleAccountEditView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `GoogleLogin.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `GroupSummary.Edit`

- evidence: `Getter,Property,Setter`   replica: `prop-get`
- 处置：**计算属性（不加虚设 setter）**：`GroupSummary.Edit` 是由其它状态派生/投影的只读属性（`computed-expr`），为其增加空 setter 会制造不落地状态。

### `HelpView.OpenUrl`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ImapCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `InputModal.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `KeyBindsView.Delete`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Delete` 是通用名，源码里有 18 个类都叫它（如 `TaskKeyBinds.Delete`、`ProxyKeyBinds.Delete`、`BillingKeyBinds.Delete`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `MainWindow.Navigate`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `MessageBoxDialog.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `NotificationsView.PlaySound`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`PlaySound` 是通用名，源码里有 2 个类都叫它（如 `NotificationService.PlaySound`、`PlatformSoundPlayer.PlaySound`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `NotificationsView.ResetSound`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `NotificationsView.Select`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Select` 是通用名，源码里有 4 个类都叫它（如 `ProfileAllocation.Select`、`LocalizationService.Select`、`MonitorWindow.Select`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `NotificationsView.SelectSound`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `PayPalAccountCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `PaymentView.SelectedProfiles`

- evidence: `Getter,Property,Setter`   replica: `prop-get`
- 处置：**计算属性（不加虚设 setter）**：`PaymentView.SelectedProfiles` 是由其它状态派生/投影的只读属性（`computed-body`），为其增加空 setter 会制造不落地状态。

### `ProfileView.CreateTest`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProfileView.MoveGroup`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProxyCreatorView.Add`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Add` 是通用名，源码里有 17 个类都叫它（如 `ObservableDictionary.Add`、`ProxyKeyBinds.Add`、`BillingKeyBinds.Add`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `ProxyGroupView.Delete`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProxyGroupView.Reset`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Reset` 是通用名，源码里有 4 个类都叫它（如 `RetailApiFamilies.Reset`、`ScheelsFrontastic.Reset`、`DataView.Reset`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `ProxyGroupView.Save`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Save` 是通用名，源码里有 11 个类都叫它（如 `ConfigurationStore.Save`、`SmartActionEditorWindow.Save`、`ProfileCreatorView.Save`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `ProxyView.AddProxies`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProxyView.ClearAll`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProxyView.ClearFailed`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**可能改名，判据弱**：`ClearFailed` 是个有识别度的名字，在 `ProxyGrid.ClearFailed` 上出现。**同名仍不等于同成员**，要确认得读那处的实现。记录为弱证据，不作为结案。

### `ProxyView.ClearOver`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`ClearOver` 是通用名，源码里有 1 个类都叫它（如 `ProxyGrid.ClearOver`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `ProxyView.CreateGroup`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProxyView.Delete`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Delete` 是通用名，源码里有 18 个类都叫它（如 `TaskKeyBinds.Delete`、`ProxyKeyBinds.Delete`、`BillingKeyBinds.Delete`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `ProxyView.MoveGroup`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `ProxyView.TestAll`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`TestAll` 是通用名，源码里有 1 个类都叫它（如 `ProxyKeyBinds.TestAll`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `PublishTemplateModal.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `SizeCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `SizeCreatorView.ToggleSizeSelected`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.AddAction`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.AddFilter`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.AddInput`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.Delete`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Delete` 是通用名，源码里有 18 个类都叫它（如 `TaskKeyBinds.Delete`、`ProxyKeyBinds.Delete`、`BillingKeyBinds.Delete`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `SmartActionsCreator.DeleteAction`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.DeleteFilter`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.DeleteInput`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.DeleteParam`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.Settings`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Settings` 是通用名，源码里有 5 个类都叫它（如 `Solver.Settings`、`AppPaths.Settings`、`ConfigurationStore.Settings`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `SmartActionsCreator.ToggleFilterBehaviour`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsCreator.UseTemplate`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SmartActionsView.Export`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Export` 是通用名，源码里有 1 个类都叫它（如 `ConfigurationStore.Export`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `SolverWindow.Add`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `SolverWindow.CloseSolver`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `StoreCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `StoreGroupModal.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

### `StoreGroupModal.RemoveStore`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `StoreGroupModal.Save`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Save` 是通用名，源码里有 11 个类都叫它（如 `ConfigurationStore.Save`、`SmartActionEditorWindow.Save`、`ProfileCreatorView.Save`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `TaskGroupView.Reset`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Reset` 是通用名，源码里有 3 个类都叫它（如 `RetailApiFamilies.Reset`、`ScheelsFrontastic.Reset`、`DataView.Reset`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `TaskView.CopyUrl`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `TaskView.Delete`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Delete` 是通用名，源码里有 18 个类都叫它（如 `TaskKeyBinds.Delete`、`ProxyKeyBinds.Delete`、`BillingKeyBinds.Delete`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `TaskView.Edit`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`Edit` 是通用名，源码里有 8 个类都叫它（如 `is.Edit`、`AccountGrid.Edit`、`CaptchaProvidersView.Edit`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `TaskView.MoveGroup`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `TaskView.SetQuery`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `TaskView.StartAll`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**Unknown（同名撞名，判据无判别力）**：`StartAll` 是通用名，源码里有 4 个类都叫它（如 `TaskKeyBinds.StartAll`、`TaskEngine.StartAll`、`MainViewModel.StartAll`）。「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。要结案只能读该类有没有这块功能，或等原版可观察。

### `UserView.OpenUrl`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `UtilitiesView.CreateStoreGroup`

- evidence: `Getter,Property,Setter`   replica: `method`
- 处置：**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。在没有原版可观察之前，加一个选择模型就是发明。

### `WebhookCreatorView.Close`

- evidence: `Getter,Property,Setter`   replica: `?`
- 处置：**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。

