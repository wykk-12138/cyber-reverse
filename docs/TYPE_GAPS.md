# 类型缺失：未实现类型，逐条列出缺什么

> 生成物：`python analysis/type_gaps_report.py`。数据来自 `analysis/binding_descriptors.tsv`（原版绑定描述符表）与 `analysis/type_presence_triage.tsv`（R512 三分类）。
> 判据 a 要求「每条若不可得则写 Unknown + 缺什么」—— 这份文件就是那句「缺什么」。

## 怎么读

- **成员**：原版在那个类型上绑定的成员名，后跟访问器种类（`G` = Getter、`S` = Setter、`P` = Property）。
- **判断（启发式）**：从成员形状和类型名推的，**不是反编译证据**。
- **处置**：`结构差异` 表示复刻件换了实现方式或这本来就不是数据类；`可补` 表示应该补。

## 汇总

| 项 | 条数 |
|---|---|
| 总计 | 12 |
| **结构差异（不补）** | **12** |
| **可补** | **0** |

> **标成结构差异的条目，`bind_diff --type-presence` 的数字不会因此变化** —— 那个度量问的是「有没有同名类型」，不是「该不该有」。所以 `docs/METRICS.md` 仍是它自己的数。

## 逐条

### `Cybersole.Helpers.ObservableDictionary`2`

- 成员数（描述符表记的）：1；分类脚本命中：1 / Jaccard 0.50
- 与复刻件最接近的类：`TaskCombinationBuilder`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：collection wrapper
- 处置：**结构差异，不补**：Avalonia 的基础集合类型已经覆盖，复刻件不需要自己的包装。
- 成员：`Count`(G)

### `Cybersole.Services.ImapProvider`

- 成员数（描述符表记的）：4；分类脚本命中：4 / Jaccard 0.29
- 与复刻件最接近的类：`ImapMailProvider`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：small data model
- 处置：**结构差异，不补**：R512 已把它判为改名 → `ImapMailProvider`，那个类已经存在。再补一个同名类型只是为把数字减一。
- 成员：`Host`(G)、`MessageCount`(GS)、`Status`(GS)、`Username`(GS)

### `Cybersole.Ui.Localization.LocalizeEnumExtension`

- 成员数（描述符表记的）：1；分类脚本命中：1 / Jaccard 1.00
- 与复刻件最接近的类：`Size`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：markup extension / XAML helper
- 处置：**结构差异，不补**：这是 XAML 的 `MarkupExtension`。复刻件没有 XAML（0 个 `.axaml`、0 个 `MarkupExtension` 子类），全部控件用 C# 构建，没有可插的地方。
- 成员：`Value`(GS)

### `Cybersole.Ui.Localization.LocalizeFallbackExtension`

- 成员数（描述符表记的）：1；分类脚本命中：1 / Jaccard 1.00
- 与复刻件最接近的类：`Size`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：markup extension / XAML helper
- 处置：**结构差异，不补**：这是 XAML 的 `MarkupExtension`。复刻件没有 XAML（0 个 `.axaml`、0 个 `MarkupExtension` 子类），全部控件用 C# 构建，没有可插的地方。
- 成员：`Value`(GS)

### `Cybersole.Ui.Localization.LocalizeFormatExtension`

- 成员数（描述符表记的）：2；分类脚本命中：1 / Jaccard 0.50
- 与复刻件最接近的类：`Size`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：markup extension / XAML helper
- 处置：**结构差异，不补**：这是 XAML 的 `MarkupExtension`。复刻件没有 XAML（0 个 `.axaml`、0 个 `MarkupExtension` 子类），全部控件用 C# 构建，没有可插的地方。
- 成员：`Value`(GS)、`Value2`(GS)

### `Cybersole.Ui.Localization.LocalizeSwitchExtension`

- 成员数（描述符表记的）：1；分类脚本命中：0 / Jaccard 0.00
- 与复刻件最接近的类：``（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：markup extension / XAML helper
- 处置：**结构差异，不补**：这是 XAML 的 `MarkupExtension`。复刻件没有 XAML（0 个 `.axaml`、0 个 `MarkupExtension` 子类），全部控件用 C# 构建，没有可插的地方。
- 成员：`Condition`(GS)

### `Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView`

- 成员数（描述符表记的）：2；分类脚本命中：1 / Jaccard 0.33
- 与复刻件最接近的类：`ProxyCreatorView`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：small data model
- 处置：**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。
- 成员：`Add`(GS)、`Close`(GS)

### `Cybersole.Ui.Views.Auth.AuthWindow`

- 成员数（描述符表记的）：3；分类脚本命中：2 / Jaccard 0.25
- 与复刻件最接近的类：`MonitorWindow`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：small data model
- 处置：**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。
- 成员：`Exit`(GS)、`Logout`(G)、`Minimise`(GS)

### `Cybersole.Ui.Views.Auth.LicenseControl`

- 成员数（描述符表记的）：3；分类脚本命中：1 / Jaccard 0.25
- 与复刻件最接近的类：`BillingView`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：small data model
- 处置：**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。
- 成员：`Authenticate`(G)、`Dashboard`(GS)、`Refresh`(G)

### `Cybersole.Ui.Views.Settings.SettingsView`

- 成员数（描述符表记的）：19；分类脚本命中：1 / Jaccard 0.05
- 与复刻件最接近的类：`UserView`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：data model
- 处置：**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。
- 成员：`AppearanceView`(G)、`CaptchaProvidersView`(G)、`CloudflareSolversView`(G)、`CustomSizesView`(G)、`CustomStoresView`(G)、`DataView`(G)、`GeneralSettingsView`(G)、`GoogleAccountsView`(G)、`HelpView`(G)、`ImapView`(G)、`KeyBindsView`(G)、`LogOut`(G)、`NotificationsView`(G)、`PayPalAccountsView`(G)、`PaymentView`(G)、`Transition`(GS)、`Update`(G)、`Version`(G)、`WebhookView`(G)

### `Cybersole.Ui.Views.Tasks.TaskCreatorCartView`

- 成员数（描述符表记的）：3；分类脚本命中：2 / Jaccard 0.67
- 与复刻件最接近的类：`WebhookView`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：small data model
- 处置：**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。
- 成员：`Add`(GS)、`Delete`(GS)、`SizeItems`(G)

### `Cybersole.Ui.Views.Tasks.TaskCreatorMainView`

- 成员数（描述符表记的）：4；分类脚本命中：4 / Jaccard 0.29
- 与复刻件最接近的类：`TaskCreatorView`（**这是启发式匹配，不要当成同一类型**）
- 判断（启发式）：small data model
- 处置：**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。
- 成员：`ProfileGroupItems`(G)、`ProfileItems`(G)、`ShowCartView`(GS)、`SizeItems`(G)

