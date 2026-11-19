# 度量快照（生成文件，请勿手改）

> 本文件由 `python tools/metrics_report.py` 生成。
> **所有文档里的「当前值」都引用本文件，不再各自硬编码。**
> 要更新：重跑生成命令即可；手改本文件会在下一次生成时被覆盖。

| 项 | 值 |
|---|---|
| 生成时间 | 2026-11-20 01:43:01 +0800 |
| 工作目录 | `D:\projects\cyber-reverse\replica` |
| 生成命令 | `python tools/metrics_report.py --skip-tests` |
| 度量脚本结果 | 全部 exit 0 |
| 完整套件 | 本次跳过（`--skip-tests`） |

## 时效警告（生成）

> **函数数量那一行来自一个陈旧的 `.publish-aot`**：有 23 个源文件比产物新（共 15240 行）。它描述的是更旧的一次构建，不是当前源码。
>
> **变异套件那一组数来自上一次运行，而它已经过期**：`3 -- tests/Cybersole.Tests/DocumentNumbersAreSourcedTests.cs (+2 more) differs from the run's manifest`。

## 摘要素值

| 指标 | 值 |
|---|---|
| 名字级绑定缺口 — real gap | 0 |
| 名字级绑定缺口 — missing | 14 |
| 类型级绑定缺口 — types with scope misses | 0 |
| 类型缺失（type presence） — types absent from source | 15 |
| 类型缺失（type presence） — classified | renamed 13, out of scope 2, unimplemented 0, unclassified 0 |
| 成员形状差异 — total mismatches | 88 |
| 成员形状差异 — core mismatches | 3 |
| 成员形状差异 — over-permissive total | 45 |
| 文案缺口总表 — copy: zones with a missing key | 0 (in 0 zone[s]) |
| 绑定缺口分桶 — backlog: classes missing members | 0 |
| 绑定缺口分桶 — backlog: types absent | 2 |
| 原版绑定描述符表 — descriptor entries | 951 |
| 原版绑定描述符表 — descriptor types | 215 |
| 原版绑定描述符表 — only in descriptors | 137 |
| 原版绑定描述符表 — only in xaml table | 0 |
| 数据文件名对照 — datafiles: original-on-disk not in replica | 0 |
| 数据文件名对照 — datafiles: replica-only | 2 |
| 函数数量（.pdata） — functions: original .pdata | 277,120 |
| 函数数量（.pdata） — functions: replica .pdata | 179,456 |
| 函数数量（.pdata） — functions: ratio | 64.76% |
| 产物陈旧度（.publish-aot vs src） — source files newer than the artifact | 23 |
| 产物陈旧度（.publish-aot vs src） — lines in those files | 15240 |
| 产物陈旧度（.publish-aot vs src） — of those, changed against HEAD | 0 |
| 核心覆盖：store 宿主 — core: flows | 18 |
| 核心覆盖：store 宿主 — core: override steps | 369 |
| 核心覆盖：store 宿主 — core: unknown placeholders | 11 |
| 核心覆盖：store 宿主 — core: provenance exit | 0 |
| 核心覆盖：vendor 宿主 — vendor: controls ok | True |
| 核心覆盖：vendor 宿主 — vendor: named in image | 13 |
| 核心覆盖：vendor 宿主 — vendor: wiring rows | 9 |
| 核心覆盖：vendor 宿主 — vendor: missing | 5 |
| 可执行段体量 — section-mass: original executable | 51695104 |
| 可执行段体量 — section-mass: replica executable | 29445120 |
| 可执行段体量 — section-mass: ratio | 56.96% |
| 函数分布（.pdata 地址分桶） — pdata: above boundary original | 156590 |
| 函数分布（.pdata 地址分桶） — pdata: above boundary replica | 604 |
| 函数分布（.pdata 地址分桶） — pdata: last replica bucket | 0x1C00000 |
| 变异套件（上次运行） — mutation-fit: total | 59 |
| 变异套件（上次运行） — mutation-fit: fired | 59 |
| 变异套件（上次运行） — mutation-fit: decorative | 0 |
| 变异套件（上次运行） — mutation-fit: skipped | 0 |
| 变异套件（上次运行） — mutation-fit: staleness | 3 -- tests/Cybersole.Tests/DocumentNumbersAreSourcedTests.cs (+2 more) differs from the run's manifest |

## 逐条命令与原始输出

### 名字级绑定缺口

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/bind_diff.py --buckets
```

`exit 0`

```text
scope: whole-source   types: 174   members: 814
missing: 14

noise (HasMultiple_NN): 12
out of scope (R702)   : 2
real gap              : 0
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
types examined: 154
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
  ABSENT  Cybersole.CloudflareSolvers.CloudflareSolver renamed      Cybersole.Stores.Scripts.CloudflareStrategy
  ABSENT  Cybersole.Global.Settings                  renamed      Cybersole.Core.Settings.GlobalSettings
  ABSENT  Cybersole.Models.Concurrency               renamed      Cybersole.Core.Settings.GlobalSettings (concurrency members)
  ABSENT  Cybersole.Services.ImapProvider            renamed      Cybersole.Services.Mail.ImapMailProvider
  ABSENT  Cybersole.SmartActions.ActionConfig        renamed      Cybersole.Core.Models.SmartAction (config members)
  ABSENT  Cybersole.Ui.Localization.LocalizeEnumExtension renamed      Cybersole.Ui.Localization.LocalizationService helpers
  ABSENT  Cybersole.Ui.Localization.LocalizeFallbackExtension renamed      Cybersole.Ui.Localization.LocalizationService helpers
  ABSENT  Cybersole.Ui.Localization.LocalizeFormatExtension renamed      Cybersole.Ui.Localization.LocalizationService helpers
  ABSENT  Cybersole.Ui.Localization.LocalizeSwitchExtension renamed      Cybersole.Ui.Localization.LocalizationService helpers
  ABSENT  Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView renamed      AccountCreatorView
  ABSENT  Cybersole.Ui.Views.Auth.AuthWindow         out_of_scope 
  ABSENT  Cybersole.Ui.Views.Auth.LicenseControl     out_of_scope 
  ABSENT  Cybersole.Ui.Views.Settings.SettingsView   renamed      SettingsShell
  ABSENT  Cybersole.Ui.Views.Tasks.TaskCreatorCartView renamed      cart view inside TaskCreatorView
  ABSENT  Cybersole.Ui.Views.Tasks.TaskCreatorMainView renamed      TaskCreatorView

classified: renamed 13, out of scope 2, unimplemented 0, unclassified 0

note: ABSENT = no same-name declaration anywhere in src/. The replica is allowed to rename
      types (AGENTS.md §0), so each ABSENT must be classified in tools/type_classification.json
      as RENAMED (with the counterpart), OUT_OF_SCOPE (with the ruling) or UNIMPLEMENTED.
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
  BotTask                    Running                evidence=Getter,Property,Setter     replica=?
  BotTask                    Task                   evidence=Getter,Property,Setter     replica=?
  CreateModel                Inputs                 evidence=Getter,Property,Setter     replica=?
  AccountGrid                Delete                 evidence=Getter,Property,Setter     replica=?
  AccountGrid                Edit                   evidence=Getter,Property,Setter     replica=prop-get
  AccountGroupView           Delete                 evidence=Getter,Property,Setter     replica=?
  AccountGroupView           Save                   evidence=Getter,Property,Setter     replica=?
  CreateGroupModal           Create                 evidence=Getter,Property,Setter     replica=?
  AnalyticsView              ChangeChart            evidence=Getter,Property,Setter     replica=method
  AnalyticsView              OpenRelease            evidence=Getter,Property,Setter     replica=method
  CustomBrowser              Autofill               evidence=Getter,Property,Setter     replica=?
  CustomBrowser              Back                   evidence=Getter,Property,Setter     replica=method
  CustomBrowser              Exit                   evidence=Getter,Property,Setter     replica=method
  CustomBrowser              Forward                evidence=Getter,Property,Setter     replica=method
  CustomBrowser              Minimise               evidence=Getter,Property,Setter     replica=method
  CustomBrowser              Refresh                evidence=Getter,Property,Setter     replica=method
  GoogleLogin                Close                  evidence=Getter,Property,Setter     replica=?
  SolverWindow               Add                    evidence=Getter,Property,Setter     replica=method
  SolverWindow               CloseSolver            evidence=Getter,Property,Setter     replica=method
  MainWindow                 Navigate               evidence=Getter,Property,Setter     replica=method
  DesktopNotification        Close                  evidence=Getter,Property,Setter     replica=?
  InputModal                 Close                  evidence=Getter,Property,Setter     replica=?
  MessageBoxDialog           Close                  evidence=Getter,Property,Setter     replica=?
  UserView                   OpenUrl                evidence=Getter,Property,Setter     replica=method
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
  StoreCreatorView           Close                  evidence=Getter,Property,Setter     replica=?
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
total mismatches: 88

over-permissive: member is read-only in the original but settable here
  CaptchaProvider            ApiKey                 evidence=Getter,Property            replica=prop+set
  CaptchaProvider            BalanceSupported       evidence=Getter,Property            replica=prop+set
  CaptchaProvider            Type                   evidence=Getter,Property            replica=prop+set
  Element                    PropName               evidence=Getter,Property            replica=prop+set
  BotTask                    Product                evidence=Getter,Property            replica=prop+set
  CreateInputModel           PriceCheckVisible      evidence=Getter,Property            replica=prop+set
  CreateInputModel           Symbol                 evidence=Getter,Property            replica=prop+set
  Input                      Type                   evidence=Getter,Property            replica=prop+set
  License                    Last4                  evidence=Getter,Property            replica=prop+set
  MonitorProduct             AvailableVariants      evidence=Getter,Property            replica=prop+set
  Proxy                      Host                   evidence=Getter,Property            replica=prop+set
  Proxy                      Port                   evidence=Getter,Property            replica=prop+set
  Proxy                      Username               evidence=Getter,Property            replica=prop+set
  Shortcut                   Name                   evidence=Getter,Property            replica=prop+set
  Solver                     Reload                 evidence=Getter,Property            replica=prop+set
  Solver                     View                   evidence=Getter,Property            replica=prop+set
  Status                     Clickable              evidence=Getter,Property            replica=prop+set
  Store                      Info                   evidence=Getter,Property            replica=prop+set
  TaskStep                   Completed              evidence=Getter,Property            replica=prop+set
  TaskStep                   Duration               evidence=Getter,Property            replica=prop+set
  TaskStep                   Running                evidence=Getter,Property            replica=prop+set
  TaskStep                   Started                evidence=Getter,Property            replica=prop+set
  User                       IsStaff                evidence=Getter,Property            replica=prop+set
  ValueGroup                 Preview                evidence=Getter,Property            replica=prop+set
  GroupGrid                  Items                  evidence=Getter,Property            replica=prop+set
  GroupGrid                  Store                  evidence=Getter,Property            replica=prop+set
  CustomBrowser              Type                   evidence=Getter,Property            replica=prop+set
  DropdownModal              ButtonText             evidence=Getter,Property            replica=prop+set
  DropdownModal              Placeholder            evidence=Getter,Property            replica=prop+set
  InputModal                 ButtonText             evidence=Getter,Property            replica=prop+set
  InputModal                 Placeholder            evidence=Getter,Property            replica=prop+set
  MessageBoxDialog           Type                   evidence=Getter,Property            replica=prop+set
  ProfileCreatorView         IsBulk                 evidence=Getter,Property            replica=prop+set
  ProfileCreatorView         ShippingView           evidence=Getter,Property            replica=prop+set
  LocalizedOption            Text                   evidence=Getter,Property            replica=prop+set
  CaptchaProviderCreatorView Creating               evidence=Getter,Property            replica=prop+set
  CloudflareSolverCreatorView Creating               evidence=Getter,Property            replica=prop+set
  GoogleAccountEditView      EditMode               evidence=Getter,Property            replica=prop+set
  PayPalAccountCreatorView   EditMode               evidence=Getter,Property            replica=prop+set
  FilterRow                  Passed                 evidence=Getter,Property            replica=prop+set
  FilterRow                  Title                  evidence=Getter,Property            replica=prop+set
  HistoryWindow              SmartAction            evidence=Getter,Property            replica=prop+set
  HistoryWindow              View                   evidence=Getter,Property            replica=prop+set
  SmartActionsCreator        IsEditing              evidence=Getter,Property            replica=prop+set
  IWebhook                   Type                   evidence=Getter,Property            replica=prop+set
over-permissive total: 45

by owning project (priority order: Stores > Services > Http > Core > Ui):
  Cybersole.Ui            85
  Cybersole.Core           3
core mismatches: 3
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

types that DO NOT exist (structural): 2 -> 2 members
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
xaml table entries      : 814
shared                  : 814
only in descriptors     : 137
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
  pdata-replica: 179,456
  pdata-ratio: 64.76%
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
publish artifact mtime: 2026-11-19 11:09:47
newest source: src\Cybersole.Stores\Payments\PayPalThreeDs.cs (2026-11-20 01:27:58)
source files newer than the artifact: 23
lines in those files: 15240
of those, changed against HEAD: 0
publish artifact state: current

  23 files are newer but unchanged against HEAD: mutation-check rewrites and restores its
  targets, which updates mtime without changing a byte. Nothing to rebuild.
```

### 核心覆盖：store 宿主

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/core_coverage.py
```

`exit 0`

```text
  wrote docs/CORE_COVERAGE.md
  flows=18 steps=369 placeholders=11 provenance exit=0
```

### 核心覆盖：vendor 宿主

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/vendor_coverage.py
```

`exit 0`

```text
  wrote docs/VENDOR_COVERAGE.md
  controls ok=True  vendors named=13  wiring rows=9  missing=5
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
=== REPLICA  image base 0x140000000  file 57375744 bytes ===
  name       rva start    rva end      raw size     flags
  ------------------------------------------------------------------
  .text      0x1000       0x102C28     1056256      X
  .managed   0x103000     0x1C15D88    28388864     X
  hydrated   0x1C16000    0x2B8CF90    0            RW
  .rdata     0x2B8D000    0x43970C6    25207296     R
  .data      0x4398000    0x4492C68    226304       RW
  .pdata     0x4493000    0x46A0C00    2153472      R
  _RDATA     0x46A1000    0x46A10F4    512          R
  .rsrc      0x46A2000    0x46ED7E7    309248       R
  .reloc     0x46EE000    0x46F5FD8    32768        R

  section-mass-replica-executable: 29445120
  section-mass-ratio: 56.96%

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
  replica : 179,456 functions, image base 0x140000000

  range from     original   replica    replica/original
  ----------------------------------------------------
  0x0            5,475      1,895        34.6%
  0x100000       5,089      4,810        94.5%
  0x200000       4,333      5,258       121.3%
  0x300000       2,213      3,758       169.8%
  0x400000       5,791      5,768        99.6%
  0x500000       2,057      3,981       193.5%
  0x600000       1,074      4,217       392.6%
  0x700000       3,411      3,209        94.1%
  0x800000       4,076      2,977        73.0%
  0x900000       3,556      2,615        73.5%
  0xA00000       3,178      5,609       176.5%
  0xB00000       3,227      5,814       180.2%
  0xC00000       3,982      6,469       162.5%
  0xD00000       3,921      7,772       198.2%
  0xE00000       3,371      5,568       165.2%
  0xF00000       7,792      3,945        50.6%
  0x1000000      5,626      8,037       142.9%
  0x1100000      2,020      9,535       472.0%
  0x1200000      2,046      10,273      502.1%
  0x1300000      5,065      9,565       188.8%
  0x1400000      10,107     10,064       99.6%
  0x1500000      11,107     9,169        82.6%
  0x1600000      2,864      9,578       334.4%
  0x1700000      2,242      9,335       416.4%
  0x1800000      4,058      9,199       226.7%
  0x1900000      4,506      5,738       127.3%
  0x1A00000      2,310      5,769       249.7%
  0x1B00000      6,033      8,925       147.9%
  0x1C00000      6,218      604           9.7%
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
    0x1D00000        0.0%   original 6,893    replica 0
    0x1E00000        0.0%   original 5,418    replica 0
    0x1F00000        0.0%   original 4,991    replica 0
    0x2000000        0.0%   original 7,513    replica 0
    0x2100000        0.0%   original 10,388   replica 0

  pdata-above-0x1C00000-original: 156590
  pdata-above-0x1C00000-replica: 604
  pdata-last-replica-bucket: 0x1C00000

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
  mutation-fit-total: 59
  mutation-fit-fired: 59
  mutation-fit-decorative: 0
  mutation-fit-skipped: 0
  mutation-fit-tree: GREEN
  mutation-fit-staleness: 3 -- tests/Cybersole.Tests/DocumentNumbersAreSourcedTests.cs (+2 more) differs from the run's manifest

  The counts above are from 2026-11-20T01:32:25+08:00 and the tree has moved since. They are a record of that run, not a
  statement about this one; re-run `python tools/mutation-check.py` before quoting them as current.
```

### 完整套件

本次未运行（`--skip-tests`）。**这不等于通过**：判据 e 需要它。

---

## 谁引用本文件

`AGENTS.md §4` · `docs/GOAL.md` 判据 a · `docs/HANDOFF.md` · `docs/COPY_QUEUE.md` 头部 ·
`replica/docs/SESSION_STATE.md` · `replica/docs/DEVIATIONS.md`。

`replica/docs/VERDICT.md` **不引用也不修改** —— 它是按轮次的历史记录。

