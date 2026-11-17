# 度量快照（生成文件，请勿手改）

> 本文件由 `python tools/metrics_report.py` 生成。
> **所有文档里的「当前值」都引用本文件，不再各自硬编码。**
> 要更新：重跑生成命令即可；手改本文件会在下一次生成时被覆盖。

| 项 | 值 |
|---|---|
| 生成时间 | 2026-11-17 20:41:21 +0800 |
| 工作目录 | `D:\projects\cyber-reverse\replica` |
| 生成命令 | `python tools/metrics_report.py` |
| 度量脚本结果 | 全部 exit 0 |
| 完整套件 | **2258 通过 / 0 失败 / 0 跳过 / 2258 总计** |

## 时效警告（生成）

> **函数数量那一行来自一个陈旧的 `.publish-aot`**：有 2 个源文件比产物新（共 401 行）。它描述的是更旧的一次构建，不是当前源码。
>
> **变异套件那一组数来自上一次运行，而它已经过期**：`6:34:51 -- VendorWiringTests.cs changed after the run`。

## 摘要素值

| 指标 | 值 |
|---|---|
| 名字级绑定缺口 — real gap | 4 |
| 名字级绑定缺口 — missing | 16 |
| 类型级绑定缺口 — types with scope misses | 0 |
| 类型缺失（type presence） — types absent from source | 15 |
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
| 函数数量（.pdata） — functions: replica .pdata | 174,293 |
| 函数数量（.pdata） — functions: ratio | 62.89% |
| 产物陈旧度（.publish-aot vs src） — source files newer than the artifact | 2 |
| 产物陈旧度（.publish-aot vs src） — lines in those files | 401 |
| 核心覆盖：store 宿主 | （未解析，见下方原始输出） |
| 核心覆盖：vendor 宿主 | （未解析，见下方原始输出） |
| 可执行段体量 — section-mass: original executable | 51695104 |
| 可执行段体量 — section-mass: replica executable | 28897792 |
| 可执行段体量 — section-mass: ratio | 55.90% |
| 函数分布（.pdata 地址分桶） — pdata: above boundary original | 156590 |
| 函数分布（.pdata 地址分桶） — pdata: above boundary replica | 0 |
| 函数分布（.pdata 地址分桶） — pdata: last replica bucket | 0x1B00000 |
| 变异套件（上次运行） — mutation-fit: total | 36 |
| 变异套件（上次运行） — mutation-fit: fired | 36 |
| 变异套件（上次运行） — mutation-fit: decorative | 0 |
| 变异套件（上次运行） — mutation-fit: skipped | 0 |
| 变异套件（上次运行） — mutation-fit: staleness | 6:34:51 -- VendorWiringTests.cs changed after the run |

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
type presence: 174 declared in bindings, 159 present in source, 15 absent
  ABSENT  Cybersole.CloudflareSolvers.CloudflareSolver (members: ApiKey, Balance, BalanceSupported, Concurrency, Count, Id, IsFetchingBalance, Name, Type)
  ABSENT  Cybersole.Global.Settings                  (members: AutoOpen3DS, AutoOpen3DSLimit, BackupInterval, BetaUpdates, BrowserLimit, BrowserPath, BrowserProfileAssignment, BrowserWindowMode, Clock, Currency, Keybinds, Language, MaxBackups, MaxLogRetention, MaxLogSize, MonitorConcurrency, MonitorDelay, MonitorFilters, Notifications, PinGroups, ProfileGroupOrder, ProxyGroupOrder, QueuePresentation, QuickTaskProfiles, QuickTaskProxies, RetryDelay, ScrollbarColor, ScrollbarCornerRadius, ScrollbarWidth, ShopifyBrowserProxy, SmartActions, StartupPage, TaskGroupOrder, Timeout)
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
  pdata-replica: 174,293
  pdata-ratio: 62.89%
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
publish artifact mtime: 2026-11-17 19:15:08
newest source: src\Cybersole.Stores\Scripts\VendorWiring.cs (2026-11-17 20:41:14)
source files newer than the artifact: 2
lines in those files: 401
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
  wrote docs/CORE_COVERAGE.md
  flows=18 steps=356 placeholders=14 provenance exit=0
```

### 核心覆盖：vendor 宿主

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/vendor_coverage.py
```

`exit 0`

```text
  wrote docs/VENDOR_COVERAGE.md
  controls ok=True  vendors named=13  wiring rows=7  missing=7
    missing: BotDeflector       n=2   0x146e93b9c
    missing: Vercel             n=2   0x146d8aa2c
    missing: Stripe challenge   n=1   0x146e9427c
    missing: PayPal 3DS         n=9   0x146e93fb4
    missing: captcha            n=1   0x146e94334
    missing: proof of work      n=1   0x146e93f74
    missing: checkpoint         n=1   0x146e94464
```

### 可执行段体量

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/pe_sections.py
```

`exit 0`

```text
=== ORIGINAL  image base 0x140000000  file 129243216 bytes ===
  name       rva start    rva end      raw size     flags
  ------------------------------------------------------------------
  .text      0x1000       0x314DD68    51695104     X
  .rdata     0x314E000    0x6A4687E    59738624     R
  .data      0x6A47000    0x7542DA8    10227712     RW
  .pdata     0x7543000    0x786ECC8    3325440      R
  .rsrc      0x786F000    0x78BA89C    309760       R
  .reloc     0x78BB000    0x7C7BC10    3935744      R

  section-mass-original-executable: 51695104
=== REPLICA  image base 0x140000000  file 56158720 bytes ===
  name       rva start    rva end      raw size     flags
  ------------------------------------------------------------------
  .text      0x1000       0xFDCB8      1035776      X
  .managed   0xFE000      0x1B903A8    27862016     X
  hydrated   0x1B91000    0x2AA0AF8    0            RW
  .rdata     0x2AA1000    0x42174D6    24602112     R
  .data      0x4218000    0x430EA18    223744       RW
  .pdata     0x430F000    0x450D858    2091520      R
  _RDATA     0x450E000    0x450E0F4    512          R
  .rsrc      0x450F000    0x455A7E7    309248       R
  .reloc     0x455B000    0x4562E84    32768        R

  section-mass-replica-executable: 28897792
  section-mass-ratio: 55.90%

  Executable sections summed by raw size. The ratio is a mass comparison and says nothing about what the
  code does: the replica links a different BCL and Avalonia, so part of the difference is not its own.
```

### 函数分布（.pdata 地址分桶）

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/pdata_sections.py
```

`exit 0`

```text
pdata bucket histogram (bucket = 0x100000 bytes)
  original: 277,120 functions, image base 0x140000000
  replica : 174,293 functions, image base 0x140000000

  range from     original   replica    replica/original
  ----------------------------------------------------
  0x0            5,475      2,017        36.8%
  0x100000       5,089      4,814        94.6%
  0x200000       4,333      5,321       122.8%
  0x300000       2,213      3,548       160.3%
  0x400000       5,791      5,925       102.3%
  0x500000       2,057      3,864       187.8%
  0x600000       1,074      3,457       321.9%
  0x700000       3,411      3,476       101.9%
  0x800000       4,076      2,517        61.8%
  0x900000       3,556      3,444        96.9%
  0xA00000       3,178      5,272       165.9%
  0xB00000       3,227      5,904       183.0%
  0xC00000       3,982      7,287       183.0%
  0xD00000       3,921      7,048       179.8%
  0xE00000       3,371      4,911       145.7%
  0xF00000       7,792      4,153        53.3%
  0x1000000      5,626      8,935       158.8%
  0x1100000      2,020      9,830       486.6%
  0x1200000      2,046      9,855       481.7%
  0x1300000      5,065      9,504       187.6%
  0x1400000      10,107     9,704        96.0%
  0x1500000      11,107     9,517        85.7%
  0x1600000      2,864      8,883       310.2%
  0x1700000      2,242      9,924       442.6%
  0x1800000      4,058      7,087       174.6%
  0x1900000      4,506      5,566       123.5%
  0x1A00000      2,310      7,324       317.1%
  0x1B00000      6,033      5,206        86.3%
  0x1C00000      6,218      0             0.0%
  0x1D00000      6,893      0             0.0%
  0x1E00000      5,418      0             0.0%
  0x1F00000      4,991      0             0.0%
  0x2000000      7,513      0             0.0%
  0x2100000      10,388     0             0.0%
  0x2200000      5,921      0             0.0%
  0x2300000      9,066      0             0.0%
  0x2400000      8,099      0             0.0%
  0x2500000      13,982     0             0.0%
  0x2600000      8,823      0             0.0%
  0x2700000      10,660     0             0.0%
  0x2800000      9,753      0             0.0%
  0x2900000      9,502      0             0.0%
  0x2A00000      6,140      0             0.0%
  0x2B00000      7,124      0             0.0%
  0x2C00000      6,490      0             0.0%
  0x2D00000      4,797      0             0.0%
  0x2E00000      7,319      0             0.0%
  0x2F00000      4,857      0             0.0%
  0x3000000      2,312      0             0.0%
  0x3100000      324        0             0.0%

  the five thinnest buckets with at least 500 original functions:
    0x1C00000        0.0%   original 6,218    replica 0
    0x1D00000        0.0%   original 6,893    replica 0
    0x1E00000        0.0%   original 5,418    replica 0
    0x1F00000        0.0%   original 4,991    replica 0
    0x2000000        0.0%   original 7,513    replica 0

  pdata-above-0x1C00000-original: 156590
  pdata-above-0x1C00000-replica: 0
  pdata-last-replica-bucket: 0x1B00000

  Buckets are compared by density, not by identity: the two images are laid out independently, so equal
  counts in a bucket do not mean the same code. This says where the gap sits and nothing about why.
```

### 变异套件（上次运行）

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/mutation_report.py
```

`exit 0`

```text
  mutation-fit-total: 36
  mutation-fit-fired: 36
  mutation-fit-decorative: 0
  mutation-fit-skipped: 0
  mutation-fit-tree: GREEN
  mutation-fit-staleness: 6:34:51 -- VendorWiringTests.cs changed after the run

  The counts above are from 2026-11-17T14:06:23+08:00 and the tree has moved since. They are a record of that run, not a
  statement about this one; re-run `python tools/mutation-check.py` before quoting them as current.
```

### 完整套件

```
cd D:\projects\cyber-reverse\replica
D:\tools\dotnet8\dotnet.exe test tests/Cybersole.Tests/Cybersole.Tests.csproj -c Debug --filter Speed!=Slow&FullyQualifiedName!~VoiceListTests&FullyQualifiedName!~GlobalSurfaceTests&FullyQualifiedName!~KeyOrderDispatchTests&FullyQualifiedName!~PatchJournalTests&FullyQualifiedName!~PruneWhitelistTests&FullyQualifiedName!~NetworkRecorderLiveTests&FullyQualifiedName!~ChromiumStealthTests -m:1
```

`exit 0` · 2258 通过 / 0 失败 / 0 跳过 / 2258 总计

```text
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorCensusTests.cs(36,9): warning xUnit2029: Do not use Assert.Empty to check if a value does not exist in a collection. Use Assert.DoesNotContain instead. (https://xunit.net/xunit.analyzers/rules/xUnit2029) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayloadCoverageTests.cs(34,9): warning xUnit2029: Do not use Assert.Empty to check if a value does not exist in a collection. Use Assert.DoesNotContain instead. (https://xunit.net/xunit.analyzers/rules/xUnit2029) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayloadCoverageTests.cs(35,9): warning xUnit2029: Do not use Assert.Empty to check if a value does not exist in a collection. Use Assert.DoesNotContain instead. (https://xunit.net/xunit.analyzers/rules/xUnit2029) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ObservableDictionaryTests.cs(77,9): warning xUnit2013: Do not use Assert.Equal() to check for collection size. Use Assert.Empty instead. (https://xunit.net/xunit.analyzers/rules/xUnit2013) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ObservableDictionaryTests.cs(109,9): warning xUnit2013: Do not use Assert.Equal() to check for collection size. Use Assert.Empty instead. (https://xunit.net/xunit.analyzers/rules/xUnit2013) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SizePaletteTests.cs(24,9): warning xUnit2031: Do not use a Where clause to filter before calling Assert.Single. Use the overload of Assert.Single that accepts a filtering function. (https://xunit.net/xunit.analyzers/rules/xUnit2031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SportsshoesFlowTests.cs(128,74): warning xUnit1031: Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await instead. (https://xunit.net/xunit.analyzers/rules/xUnit1031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StepActionTests.cs(293,89): warning xUnit1031: Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await instead. (https://xunit.net/xunit.analyzers/rules/xUnit1031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnmatchedGatewaysTests.cs(58,78): warning xUnit1031: Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await instead. (https://xunit.net/xunit.analyzers/rules/xUnit1031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
  Cybersole.Tests -> D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\bin\Debug\net8.0\Cybersole.Tests.dll
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\bin\Debug\net8.0\Cybersole.Tests.dll (.NETCoreApp,Version=v8.0)的测试运行
VSTest 版本 17.11.1 (x64)
正在启动测试执行，请稍候...
总共 1 个测试文件与指定模式相匹配。
已通过! - 失败:     0，通过:  2258，已跳过:     0，总计:  2258，持续时间: 2 m 15 s - Cybersole.Tests.dll (net8.0)
```

---

## 谁引用本文件

`AGENTS.md §4` · `docs/GOAL.md` 判据 a · `docs/HANDOFF.md` · `docs/COPY_QUEUE.md` 头部 ·
`replica/docs/SESSION_STATE.md` · `replica/docs/DEVIATIONS.md`。

`replica/docs/VERDICT.md` **不引用也不修改** —— 它是按轮次的历史记录。

