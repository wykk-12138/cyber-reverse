# 度量快照（生成文件，请勿手改）

> 本文件由 `python tools/metrics_report.py` 生成。
> **所有文档里的「当前值」都引用本文件，不再各自硬编码。**
> 要更新：重跑生成命令即可；手改本文件会在下一次生成时被覆盖。

| 项 | 值 |
|---|---|
| 生成时间 | 2026-11-17 04:53:06 +0800 |
| 工作目录 | `D:\projects\cyber-reverse\replica` |
| 生成命令 | `python tools/metrics_report.py` |
| 度量脚本结果 | 全部 exit 0 |
| 完整套件 | **1955 通过 / 0 失败 / 0 跳过 / 1955 总计** |

## 摘要素值

| 指标 | 值 |
|---|---|
| 名字级绑定缺口 — real gap | 4 |
| 名字级绑定缺口 — missing | 16 |
| 类型级绑定缺口 — types with scope misses | 0 |
| 类型缺失（type presence） — types absent from source | 16 |
| 成员形状差异 — total mismatches | 94 |
| 成员形状差异 — core mismatches | 17 |
| 文案缺口总表 — copy: zones with a missing key | 0 (in 0 zone[s]) |
| 绑定缺口分桶 — backlog: classes missing members | 0 |
| 绑定缺口分桶 — backlog: types absent | 4 |
| 原版绑定描述符表 — descriptor entries | 951 |
| 原版绑定描述符表 — descriptor types | 215 |
| 原版绑定描述符表 — only in descriptors | 132 |
| 原版绑定描述符表 — only in xaml table | 0 |
| 数据文件名对照 — datafiles: original-on-disk not in replica | 0 |
| 数据文件名对照 — datafiles: replica-only | 2 |
| 函数数量（.pdata） — functions: original .pdata | 277,120 |
| 函数数量（.pdata） — functions: replica .pdata | 173,653 |
| 函数数量（.pdata） — functions: ratio | 62.66% |
| 产物陈旧度（.publish-aot vs src） — source files newer than the artifact | 2 |
| 产物陈旧度（.publish-aot vs src） — lines in those files | 246 |
| 核心覆盖：store 宿主 — hosts with a path | 39 |
| 核心覆盖：store 宿主 — store hosts | 27 |
| 核心覆盖：store 宿主 — store hosts matched | 24 |
| 核心覆盖：store 宿主 — store hosts unmatched | 3 |
| 核心覆盖：store 宿主 — vendor hosts | 12 |
| 核心覆盖：vendor 宿主 — vendor hosts carrying a path | 12 |
| 核心覆盖：vendor 宿主 — vendors named somewhere in src | 12 |
| 核心覆盖：vendor 宿主 — vendors absent from src | 0 |

## 逐条命令与原始输出

### 名字级绑定缺口

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/bind_diff.py --buckets
```

`exit 0`

```text
scope: whole-source   types: 174   members: 819
missing: 16

noise (HasMultiple_NN): 12
real gap              : 4

  Ui.Localization.LocalizeFormatExtension             1  Value2
  Ui.Localization.LocalizeSwitchExtension             1  Condition
  Ui.Views.Auth.AuthWindow                            1  Logout
  Ui.Views.Auth.LicenseControl                        1  Authenticate
```

### 类型级绑定缺口

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/bind_scope.py
```

`exit 0`

```text
type-scoped check: types present, members missing on THAT type
types with scope misses: 0
types examined: 153
types skipped for generic arity: 2
note: base-class inheritance is counted (by design since R343)
```

### 类型缺失（type presence）

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/bind_diff.py --type-presence
```

`exit 0`

```text
type presence: 174 declared in bindings, 158 present in source, 16 absent
  ABSENT  Cybersole.CloudflareSolvers.CloudflareSolver (members: ApiKey, Balance, BalanceSupported, Concurrency, Count, Id, IsFetchingBalance, Name, Type)
  ABSENT  Cybersole.Global.Settings                  (members: AutoOpen3DS, AutoOpen3DSLimit, BackupInterval, BetaUpdates, BrowserLimit, BrowserPath, BrowserProfileAssignment, BrowserWindowMode, Clock, Currency, Keybinds, Language, MaxBackups, MaxLogRetention, MaxLogSize, MonitorConcurrency, MonitorDelay, MonitorFilters, Notifications, PinGroups, ProfileGroupOrder, ProxyGroupOrder, QueuePresentation, QuickTaskProfiles, QuickTaskProxies, RetryDelay, ScrollbarColor, ScrollbarCornerRadius, ScrollbarWidth, ShopifyBrowserProxy, SmartActions, StartupPage, TaskGroupOrder, Timeout)
  ABSENT  Cybersole.Helpers.ObservableDictionary`2   (members: Count)
  ABSENT  Cybersole.Models.Concurrency               (members: Maximum, Mode, Ratio)
  ABSENT  Cybersole.Services.ImapProvider            (members: Host, MessageCount, Status, Username)
  ABSENT  Cybersole.SmartActions.ActionConfig        (members: Name, Required)
  ABSENT  Cybersole.Ui.Localization.LocalizeEnumExtension (members: Value)
  ABSENT  Cybersole.Ui.Localization.LocalizeFallbackExtension (members: Value)
  ABSENT  Cybersole.Ui.Localization.LocalizeFormatExtension (members: Value, Value2)
  ABSENT  Cybersole.Ui.Localization.LocalizeSwitchExtension (members: Condition)
  ABSENT  Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView (members: Add, Close)
  ABSENT  Cybersole.Ui.Views.Auth.AuthWindow         (members: Exit, Logout, Minimise)
  ABSENT  Cybersole.Ui.Views.Auth.LicenseControl     (members: Authenticate, Dashboard, Refresh)
  ABSENT  Cybersole.Ui.Views.Settings.SettingsView   (members: AppearanceView, CaptchaProvidersView, CloudflareSolversView, CustomSizesView, CustomStoresView, DataView, GeneralSettingsView, GoogleAccountsView, HelpView, ImapView, KeyBindsView, LogOut, NotificationsView, PayPalAccountsView, PaymentView, Transition, Update, Version, WebhookView)
  ABSENT  Cybersole.Ui.Views.Tasks.TaskCreatorCartView (members: Add, Delete, SizeItems)
  ABSENT  Cybersole.Ui.Views.Tasks.TaskCreatorMainView (members: ProfileGroupItems, ProfileItems, ShowCartView, SizeItems)

note: ABSENT = no same-name declaration anywhere in src/. The replica is allowed to rename
      types (AGENTS.md §0), so each ABSENT must be classified as RENAMED (record the mapping)
      or UNIMPLEMENTED (a real gap) before the number is used as a gap count.
```

### 成员形状差异

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/shape_audit.py --baseline
```

`exit 0`

```text
evidence: baseline (211 types, kinds kept)
mismatches: member has Setter evidence but the replica is not a settable property
  BotTask                    Products               evidence=Getter,Property,Setter     replica=prop-get
  BotTask                    Running                evidence=Getter,Property,Setter     replica=?
  BotTask                    Task                   evidence=Getter,Property,Setter     replica=?
  Checkout                   Profile                evidence=Getter,Property,Setter     replica=?
  CreateModel                Inputs                 evidence=Getter,Property,Setter     replica=?
  Notification               Message                evidence=Getter,Property,Setter     replica=prop-get
  Notification               Timestamp              evidence=Getter,Property,Setter     replica=?
  Notification               Title                  evidence=Getter,Property,Setter     replica=?
  Notification               Type                   evidence=Getter,Property,Setter     replica=prop-get
  TaskGroup                  Running                evidence=Getter,Property,Setter     replica=prop-get
  ClockService               Current                evidence=Getter,Property,Setter     replica=prop-get
  AccountGrid                Edit                   evidence=Getter,Property,Setter     replica=prop-get
  AccountGroupView           Delete                 evidence=Getter,Property,Setter     replica=?
  AccountGroupView           Save                   evidence=Getter,Property,Setter     replica=?
  CreateGroupModal           Create                 evidence=Getter,Property,Setter     replica=?
  AnalyticsView              ChangeChart            evidence=Getter,Property,Setter     replica=method
  AnalyticsView              OpenRelease            evidence=Getter,Property,Setter     replica=method
  GoogleLogin                Close                  evidence=Getter,Property,Setter     replica=?
  SolverWindow               Add                    evidence=Getter,Property,Setter     replica=method
  SolverWindow               CloseSolver            evidence=Getter,Property,Setter     replica=method
  MainWindow                 Navigate               evidence=Getter,Property,Setter     replica=method
  DesktopNotification        Close                  evidence=Getter,Property,Setter     replica=?
  InputModal                 Close                  evidence=Getter,Property,Setter     replica=?
  MessageBoxDialog           Close                  evidence=Getter,Property,Setter     replica=?
  UserView                   OpenUrl                evidence=Getter,Property,Setter     replica=method
  ExpressionExample          Output                 evidence=Getter,Property,Setter     replica=prop-get
  ExpressionView             Refresh                evidence=Getter,Property,Setter     replica=?
  ProfileGroupView           GroupName              evidence=Getter,Property,Setter     replica=prop-get
  ProfileView                CreateTest             evidence=Getter,Property,Setter     replica=method
  ProfileView                MoveGroup              evidence=Getter,Property,Setter     replica=method
  ProxyCreatorView           Add                    evidence=Getter,Property,Setter     replica=?
  ProxyGroupView             Delete                 evidence=Getter,Property,Setter     replica=method
  ProxyGroupView             Reset                  evidence=Getter,Property,Setter     replica=?
  ProxyGroupView             Save                   evidence=Getter,Property,Setter     replica=?
  ProxyView                  AddProxies             evidence=Getter,Property,Setter     replica=method
  ProxyView                  ClearAll               evidence=Getter,Property,Setter     replica=method
  ProxyView                  ClearFailed            evidence=Getter,Property,Setter     replica=?
  ProxyView                  ClearOver              evidence=Getter,Property,Setter     replica=?
  ProxyView                  CreateGroup            evidence=Getter,Property,Setter     replica=method
  ProxyView                  Delete                 evidence=Getter,Property,Setter     replica=?
  ProxyView                  MoveGroup              evidence=Getter,Property,Setter     replica=method
  ProxyView                  TestAll                evidence=Getter,Property,Setter     replica=?
  CaptchaProvidersView       Reorder                evidence=Getter,Property,Setter     replica=method
  CustomSizesView            Delete                 evidence=Getter,Property,Setter     replica=method
  CustomStoresView           Delete                 evidence=Getter,Property,Setter     replica=method
  DataView                   ViewBackups            evidence=Getter,Property,Setter     replica=prop-get
  HelpView                   OpenUrl                evidence=Getter,Property,Setter     replica=method
  KeyBindsView               Delete                 evidence=Getter,Property,Setter     replica=?
  AycdInboxCreatorView       Close                  evidence=Getter,Property,Setter     replica=?
  CaptchaProviderCreatorView Close                  evidence=Getter,Property,Setter     replica=?
  CloudflareSolverCreatorView Close                  evidence=Getter,Property,Setter     replica=?
  GoogleAccountEditView      Close                  evidence=Getter,Property,Setter     replica=?
  ImapCreatorView            Close                  evidence=Getter,Property,Setter     replica=?
  PayPalAccountCreatorView   Close                  evidence=Getter,Property,Setter     replica=?
  SizeCreatorView            Close                  evidence=Getter,Property,Setter     replica=?
  SizeCreatorView            ToggleSizeSelected     evidence=Getter,Property,Setter     replica=method
  WebhookCreatorView         Close                  evidence=Getter,Property,Setter     replica=?
  NotificationsView          PlaySound              evidence=Getter,Property,Setter     replica=?
  NotificationsView          ResetSound             evidence=Getter,Property,Setter     replica=method
  NotificationsView          Select                 evidence=Getter,Property,Setter     replica=?
  NotificationsView          SelectSound            evidence=Getter,Property,Setter     replica=method
  PaymentView                SelectedProfiles       evidence=Getter,Property,Setter     replica=prop-get
  ActionsModal               Close                  evidence=Getter,Property,Setter     replica=?
  PublishTemplateModal       Close                  evidence=Getter,Property,Setter     replica=?
  SmartActionsCreator        AddAction              evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        AddFilter              evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        AddInput               evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        Delete                 evidence=Getter,Property,Setter     replica=?
  SmartActionsCreator        DeleteAction           evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        DeleteFilter           evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        DeleteInput            evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        DeleteParam            evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        Settings               evidence=Getter,Property,Setter     replica=?
  SmartActionsCreator        ToggleFilterBehaviour  evidence=Getter,Property,Setter     replica=method
  SmartActionsCreator        UseTemplate            evidence=Getter,Property,Setter     replica=method
  SmartActionsView           Export                 evidence=Getter,Property,Setter     replica=?
  GroupSummary               Edit                   evidence=Getter,Property,Setter     replica=prop-get
  TaskGroupView              Link                   evidence=Getter,Property,Setter     replica=?
  TaskGroupView              Reset                  evidence=Getter,Property,Setter     replica=?
  TaskView                   CopyUrl                evidence=Getter,Property,Setter     replica=method
  TaskView                   Delete                 evidence=Getter,Property,Setter     replica=?
  TaskView                   Edit                   evidence=Getter,Property,Setter     replica=?
  TaskView                   MoveGroup              evidence=Getter,Property,Setter     replica=method
  TaskView                   SetQuery               evidence=Getter,Property,Setter     replica=method
  TaskView                   StartAll               evidence=Getter,Property,Setter     replica=?
  StoreGroupModal            Close                  evidence=Getter,Property,Setter     replica=?
  StoreGroupModal            RemoveStore            evidence=Getter,Property,Setter     replica=method
  StoreGroupModal            Save                   evidence=Getter,Property,Setter     replica=?
  UtilitiesView              CreateStoreGroup       evidence=Getter,Property,Setter     replica=method
  IWebhook                   Enabled                evidence=Getter,Property,Setter     replica=prop-get
  IWebhook                   Events                 evidence=Getter,Property,Setter     replica=prop-get
  IWebhook                   ExtraFields            evidence=Getter,Property,Setter     replica=prop-get
  IWebhook                   Name                   evidence=Getter,Property,Setter     replica=prop-get
  IWebhook                   Url                    evidence=Getter,Property,Setter     replica=prop-get
total mismatches: 94

by owning project (priority order: Stores > Services > Http > Core > Ui):
  Cybersole.Ui            77
  Cybersole.Core          12
  Cybersole.Services       5
core mismatches: 17
```

### 文案缺口总表

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/copy_audit_report.py
```

`exit 0`

```text
wrote COPY_QUEUE.md
   Accounts        36    0 missing    0 near
   Proxies         33    0 missing    0 near
   Tasks           40    0 missing    0 near
   Profiles        27    0 missing    0 near
   Analytics       12    0 missing    0 near
   Auth            27    0 missing    0 near
   Billing          0    0 missing    0 near
   Checkout         6    0 missing    0 near
   Data            20    0 missing    0 near
   HistoryWindow   17    0 missing    0 near
   Monitor         15    0 missing    0 near
   ProfileCsv      43    0 missing    0 near
   Release          4    0 missing    0 near
   Settings       255    0 missing    0 near
   SmartActions    22    0 missing    0 near
   TaskCreator     37    0 missing    0 near
   TaskGroup       30    0 missing    0 near
   Utilities       23    0 missing    0 near
   GroupModal       2    0 missing    0 near
   ---- summary ---- 0 zone(s) | 649 key(s) | 0 missing | 0 near
   detail rows: 0  (must equal the TOTAL missing count)
```

### 绑定缺口分桶

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/backlog_report.py
```

`exit 0`

```text
classes that EXIST in the replica but miss members: 0 -> 0 members

types that DO NOT exist (structural): 4 -> 4 members
  LocalizeSwitchExtension          Condition
  LocalizeFormatExtension          Value2
  AuthWindow                       Logout
  LicenseControl                   Authenticate
```

### 原版绑定描述符表

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/descriptor_report.py
```

`exit 0`

```text
descriptor entries      : 951
descriptor types        : 215
entries with a setter   : 687
xaml table entries      : 819
shared                  : 819
only in descriptors     : 132
only in xaml table      : 0
```

### 数据文件名对照

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/datafiles_diff.py
```

`exit 0`

```text
data directory : C:\Users\wykk\AppData\Roaming\Cybersole
  files on disk : 11  accounts.json, analytics.json, billing.json, checkoutHistory.json, proxies.json, sessions.json, settings.json, smartActionUtilities.json, smartActions.json, solvers.json, tasks.json
  image literals: 23
  replica references: 13  Cybersole.ProfileValidation.en.json, accounts.json, analytics.json, billing.json, checkoutHistory.json, license.json, proxies.json, sessions.json, settings.json, smartActionUtilities.json, smartActions.json, solvers.json, tasks.json

original-on-disk but not written by the replica : 0  -
replica-referenced, found in neither source      : 2  Cybersole.ProfileValidation.en.json, license.json
literal-only (a string in the image, not a file) : 13  CreateToken.json, __data.json, config.json, graphql.json, meta.json, popDraw.json, products.json, prop.json, public.json, shipping_rates.json, sku-stores.json, system.text.json.serialization.json, wpt.json

wrote D:\projects\cyber-reverse\docs\DATAFILES.md
```

### 函数数量（.pdata）

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/func_count.py
```

`exit 0`

```text
function count (non-leaf, from .pdata):
  pdata-original: 277,120
  pdata-replica: 173,653
  pdata-ratio: 62.66%
  .pdata holds one RUNTIME_FUNCTION per non-leaf function: it excludes inlined and trimmed code, so this
  compares function mass between the two images and does not establish function-level equality.
```

### 产物陈旧度（.publish-aot vs src）

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/artifact_freshness.py
```

`exit 0`

```text
publish artifact: .publish-aot\Cybersole.Ui.exe
publish artifact mtime: 2026-11-17 04:40:00
newest source: src\Cybersole.Stores\Scripts\AstroSurface.cs (2026-11-17 04:51:37)
source files newer than the artifact: 2
lines in those files: 246
publish artifact state: stale

  The function ratio in METRICS.md comes from this artifact. While it is stale that ratio describes an
  older build, so it must be labelled as such wherever it is quoted rather than presented as current.
```

### 核心覆盖：store 宿主

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/core_coverage.py
```

`exit 0`

```text
hosts with a path: 39  (store 27, vendor 12)
registry identifiers: 82   flow types: 35

store hosts
  matched api-search.dickssportinggoods.com         1 paths  dickssportinggoods
  unmatched api.braintreegateway.com                  2 paths  
  matched api.nike.com                              4 paths  nikegs, nike
  matched api.sibspayments.com                      1 paths  in src
  matched api.tobe-official.jp                      1 paths  in src
  unmatched api.vipps.no                              1 paths  
  matched app.midtrans.com                          2 paths  poqapp
  matched auth.casio-intl.com                       1 paths  casio, casio
  matched authenticate.riotgames.com                1 paths  riotgames
  matched checkout.johnlewis.com                   11 paths  johnlewis
  matched checkout.sportsshoes.com                  1 paths  sportsshoes
  matched degica.as1.gpayments.net                  1 paths  in src
  matched ecommerce-gateway.mollie.com              1 paths  hypecommerce
  matched flex.cybersource.com                      1 paths  in src
  matched forms.shopifyapps.com                     2 paths  shopify
  matched hbx.com                                   1 paths  hbx
  matched id.asics.com                              3 paths  in src
  unmatched payments.bigcommerce.com                  1 paths  
  matched payments.dickssportinggoods.com           2 paths  dickssportinggoods
  matched prod-hk-actapi.popmart.com                2 paths  popmart
  matched retry.touchtechpayments.com               1 paths  in src
  matched static-forms.klaviyo.com                  1 paths  in src
  matched threeds.airwallex.com                     1 paths  in src
  matched www.goat.com                              9 paths  goat
  matched www.ibm.com                               1 paths  in src
  matched www.nike.com                              1 paths  nikegs, nike
  matched www.vans.com                              6 paths  in src

vendor hosts
  matched challenges.cloudflare.com                 1 paths  cloudflare
  matched checkoutshopper-live.adyen.com            2 paths  adyen
  unmatched inbox-api.aycd.io                         3 paths  aycd
  unmatched payments-panel.production.eshopworld.com  3 paths  eshopworld
  unmatched paymentsheet-ent.wdprapps.disney.com      3 paths  disney
  matched registerdisney.go.com                     1 paths  go
  unmatched retailer-shopifypayments-api.production.eshopworld.com  2 paths  eshopworld
  unmatched web-dsy.global-e.com                      1 paths  global-e
  unmatched webservices.global-e.com                  3 paths  global-e
  matched www.paypal.com                            4 paths  paypal
  unmatched www.purpledotprice.com                    1 paths  purpledotprice
  unmatched www.vivapayments.com                      3 paths  vivapayments

hosts with a path: 39
store hosts: 27
store hosts matched: 24
store hosts unmatched: 3
vendor hosts: 12
NOTE: matched means a registration contains the host's label; unmatched means none does. Neither proves
      the store works or is absent -- a store can be registered under a label sharing no letters with its
      domain, and a short label can match by accident.
```

### 核心覆盖：vendor 宿主

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/vendor_coverage.py
```

`exit 0`

```text
vendor hosts carrying a path: 12

host                                                        pt  service      named in
challenges.cloudflare.com                                    1  Cloudflare   yes  AntiBotProtocol.cs, AntiBotVendors.cs, CloudflareClearance.cs
checkoutshopper-live.adyen.com                               2  Adyen        yes  AdyenGateway.cs, AdyenPayPalFlow.cs, BstnFlow.cs
inbox-api.aycd.io                                            3  AYCD         yes  Accounts.cs, AycdInboxAccount.cs, AycdInboxClient.cs
payments-panel.production.eshopworld.com                     3  eShopWorld   yes  EshopWorldPanel.cs
paymentsheet-ent.wdprapps.disney.com                         3  Disney       yes  DisneyPaymentSheet.cs
registerdisney.go.com                                        1  Disney       yes  DisneyPaymentSheet.cs
retailer-shopifypayments-api.production.eshopworld.com       2  eShopWorld   yes  EshopWorldPanel.cs
web-dsy.global-e.com                                         1  Global-e     yes  GlobalECheckout.cs
webservices.global-e.com                                     3  Global-e     yes  GlobalECheckout.cs
www.paypal.com                                               4  PayPal       yes  Accounts.cs, AdyenPayPalFlow.cs, CandidateSteps.cs
www.purpledotprice.com                                       1  PurpleDot    yes  PurpleDot.cs
www.vivapayments.com                                         3  Viva         yes  VivaPayments.cs

vendor hosts carrying a path: 12
vendors named somewhere in src: 12
vendors absent from src: 0
NOTE: 'yes' means some source file contains the service's name. It does not mean the integration is complete
      or correct -- a constant naming a host and a working flow are different things.
```

### 完整套件

```
cd D:\projects\cyber-reverse\replica
D:\tools\dotnet8\dotnet.exe test tests/Cybersole.Tests/Cybersole.Tests.csproj -c Debug --filter Speed!=Slow&FullyQualifiedName!~VoiceListTests&FullyQualifiedName!~GlobalSurfaceTests&FullyQualifiedName!~KeyOrderDispatchTests&FullyQualifiedName!~PatchJournalTests&FullyQualifiedName!~PruneWhitelistTests&FullyQualifiedName!~NetworkRecorderLiveTests&FullyQualifiedName!~ChromiumStealthTests -m:1
```

`exit 0` · 1955 通过 / 0 失败 / 0 跳过 / 1955 总计

```text
  正在确定要还原的项目…
D:\projects\cyber-reverse\replica\src\Cybersole.Services\Cybersole.Services.csproj : warning NU1902: 包 "MailKit" 4.8.0 具有已知的 中 严重性漏洞，https://github.com/advisories/GHSA-9j88-vvj5-vhgr [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
  所有项目均是最新的，无法还原。
  Cybersole.Core -> D:\projects\cyber-reverse\replica\src\Cybersole.Core\bin\Debug\net8.0\Cybersole.Core.dll
  Cybersole.Http -> D:\projects\cyber-reverse\replica\src\Cybersole.Http\bin\Debug\net8.0\Cybersole.Http.dll
D:\projects\cyber-reverse\replica\src\Cybersole.Services\Cybersole.Services.csproj : warning NU1902: 包 "MailKit" 4.8.0 具有已知的 中 严重性漏洞，https://github.com/advisories/GHSA-9j88-vvj5-vhgr
  Cybersole.Services -> D:\projects\cyber-reverse\replica\src\Cybersole.Services\bin\Debug\net8.0\Cybersole.Services.dll
  Cybersole.Stores -> D:\projects\cyber-reverse\replica\src\Cybersole.Stores\bin\Debug\net8.0\Cybersole.Stores.dll
  Cybersole.Ui -> D:\projects\cyber-reverse\replica\src\Cybersole.Ui\bin\Debug\net8.0\Cybersole.Ui.dll
  Cybersole.Tests -> D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\bin\Debug\net8.0\Cybersole.Tests.dll
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\bin\Debug\net8.0\Cybersole.Tests.dll (.NETCoreApp,Version=v8.0)的测试运行
VSTest 版本 17.11.1 (x64)
正在启动测试执行，请稍候...
总共 1 个测试文件与指定模式相匹配。
已通过! - 失败:     0，通过:  1955，已跳过:     0，总计:  1955，持续时间: 1 m 18 s - Cybersole.Tests.dll (net8.0)
```

---

## 谁引用本文件

`AGENTS.md §4` · `docs/GOAL.md` 判据 a · `docs/HANDOFF.md` · `docs/COPY_QUEUE.md` 头部 ·
`replica/docs/SESSION_STATE.md` · `replica/docs/DEVIATIONS.md`。

`replica/docs/VERDICT.md` **不引用也不修改** —— 它是按轮次的历史记录。

