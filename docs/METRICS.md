# 度量快照（生成文件，请勿手改）

> 本文件由 `python tools/metrics_report.py` 生成。
> **所有文档里的「当前值」都引用本文件，不再各自硬编码。**
> 要更新：重跑生成命令即可；手改本文件会在下一次生成时被覆盖。

| 项 | 值 |
|---|---|
| 生成时间 | 2026-11-20 17:04:23 +0800 |
| 工作目录 | `D:\projects\cyber-reverse\replica` |
| 生成命令 | `python tools/metrics_report.py` |
| 度量脚本结果 | 全部 exit 0 |
| 完整套件 | **2486 通过 / 0 失败 / 0 跳过 / 2486 总计** |

## 时效警告（生成）

> **变异套件那一组数来自上一次运行，而它已经过期**：`350 -- src/Cybersole.Core/Models/SmartActions.cs (+349 more) differs from the run's manifest`。

## 摘要素值

| 指标 | 值 |
|---|---|
| 名字级绑定缺口 — real gap | 0 |
| 名字级绑定缺口 — missing | 14 |
| 类型级绑定缺口 — types with scope misses | 0 |
| 类型缺失（type presence） — types absent from source | 15 |
| 类型缺失（type presence） — classified | renamed 13, out of scope 2, unimplemented 0, unclassified 0 |
| 成员形状差异 — total mismatches | 84 |
| 成员形状差异 — core mismatches | 1 |
| 成员形状差异 — over-permissive total | 37 |
| 文案缺口总表 — copy: zones with a missing key | 0 (in 0 zone[s]) |
| 绑定缺口分桶 — backlog: classes missing members | 0 |
| 绑定缺口分桶 — backlog: types absent | 2 |
| 原版绑定描述符表 — descriptor entries | 951 |
| 原版绑定描述符表 — descriptor types | 215 |
| 原版绑定描述符表 — only in descriptors | 137 |
| 原版绑定描述符表 — only in xaml table | 0 |
| 数据文件名对照 — datafiles: original-on-disk not in replica | 0 |
| 数据文件名对照 — datafiles: replica-only | 1 |
| 函数数量（.pdata） — functions: original .pdata | 277,120 |
| 函数数量（.pdata） — functions: replica .pdata | 179,840 |
| 函数数量（.pdata） — functions: ratio | 64.90% |
| 产物陈旧度（.publish-aot vs src） — source files newer than the artifact | 30 |
| 产物陈旧度（.publish-aot vs src） — lines in those files | 20062 |
| 产物陈旧度（.publish-aot vs src） — of those, changed against HEAD | 0 |
| 核心覆盖：store 宿主 — core: flows | 18 |
| 核心覆盖：store 宿主 — core: override steps | 369 |
| 核心覆盖：store 宿主 — core: unknown placeholders | 0 |
| 核心覆盖：store 宿主 — core: provenance exit | 0 |
| 核心覆盖：vendor 宿主 — vendor: controls ok | True |
| 核心覆盖：vendor 宿主 — vendor: named in image | 13 |
| 核心覆盖：vendor 宿主 — vendor: wiring rows | 0 |
| 核心覆盖：vendor 宿主 — vendor: missing | 0 |
| 可执行段体量 — section-mass: original executable | 51695104 |
| 可执行段体量 — section-mass: replica executable | 29511680 |
| 可执行段体量 — section-mass: ratio | 57.09% |
| 函数分布（.pdata 地址分桶） — pdata: above boundary original | 156590 |
| 函数分布（.pdata 地址分桶） — pdata: above boundary replica | 1274 |
| 函数分布（.pdata 地址分桶） — pdata: last replica bucket | 0x1C00000 |
| 变异套件（上次运行） — mutation-fit: total | 59 |
| 变异套件（上次运行） — mutation-fit: fired | 59 |
| 变异套件（上次运行） — mutation-fit: decorative | 0 |
| 变异套件（上次运行） — mutation-fit: skipped | 0 |
| 变异套件（上次运行） — mutation-fit: staleness | 350 -- src/Cybersole.Core/Models/SmartActions.cs (+349 more) differs from the run's manifest |

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
  ABSENT  Cybersole.Ui.Localization.LocalizeEnumExtension renamed      Cybersole.Ui.Localization.LocalizeHelpers.Enum
  ABSENT  Cybersole.Ui.Localization.LocalizeFallbackExtension renamed      Cybersole.Ui.Localization.LocalizeHelpers.Fallback
  ABSENT  Cybersole.Ui.Localization.LocalizeFormatExtension renamed      Cybersole.Ui.Localization.LocalizeHelpers.Format
  ABSENT  Cybersole.Ui.Localization.LocalizeSwitchExtension renamed      Cybersole.Ui.Localization.LocalizeHelpers.Switch
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
  BotTask                    Task                   evidence=Getter,Property,Setter     replica=?
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
total mismatches: 84

over-permissive: member is read-only in the original but settable here
  CaptchaProvider            ApiKey                 evidence=Getter,Property            replica=prop+set
  CaptchaProvider            BalanceSupported       evidence=Getter,Property            replica=prop+set
  CaptchaProvider            Type                   evidence=Getter,Property            replica=prop+set
  Element                    PropName               evidence=Getter,Property            replica=prop+set
  BotTask                    Product                evidence=Getter,Property            replica=prop+set
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
  TaskStep                   Completed              evidence=Getter,Property            replica=prop+set
  TaskStep                   Duration               evidence=Getter,Property            replica=prop+set
  TaskStep                   Running                evidence=Getter,Property            replica=prop+set
  TaskStep                   Started                evidence=Getter,Property            replica=prop+set
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
  CaptchaProviderCreatorView Creating               evidence=Getter,Property            replica=prop+set
  CloudflareSolverCreatorView Creating               evidence=Getter,Property            replica=prop+set
  GoogleAccountEditView      EditMode               evidence=Getter,Property            replica=prop+set
  PayPalAccountCreatorView   EditMode               evidence=Getter,Property            replica=prop+set
  HistoryWindow              SmartAction            evidence=Getter,Property            replica=prop+set
  HistoryWindow              View                   evidence=Getter,Property            replica=prop+set
  SmartActionsCreator        IsEditing              evidence=Getter,Property            replica=prop+set
  IWebhook                   Type                   evidence=Getter,Property            replica=prop+set
over-permissive total: 37

by owning project (priority order: Stores > Services > Http > Core > Ui):
  Cybersole.Ui            83
  Cybersole.Core           1
core mismatches: 1
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
  embedded resources excluded (csproj): 6  Cybersole.Locales.en.json, Cybersole.Locales.ja.json, Cybersole.Locales.ko.json, Cybersole.Locales.zh-Hans.json, Cybersole.ProfileValidation.en.json, Fingerprint.template.json
  replica references: 12  accounts.json, analytics.json, billing.json, checkoutHistory.json, license.json, proxies.json, sessions.json, settings.json, smartActionUtilities.json, smartActions.json, solvers.json, tasks.json

original-on-disk but not written by the replica : 0  -
written-by-replica-only                          : 0  -
read-only fallback candidate (ProbePaths)        : 1  license.json
replica-referenced, found in neither source      : 1  (license.json [read-only fallback candidate])
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
  pdata-replica: 179,840
  pdata-ratio: 64.90%
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
publish artifact mtime: 2026-11-20 14:15:16
publish artifact size: 57491456 bytes
publish artifact sha256: fcff1bcda0a10638f9929544959a1f8dee9381ae987b98093db8c521139e19bf
newest source: src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs (2026-11-20 16:57:20)
source files newer than the artifact: 30
lines in those files: 20062
of those, changed against HEAD: 0
publish artifact state: current

  30 files are newer but unchanged against HEAD: mutation-check rewrites and restores its
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
  flows=18 steps=369 placeholders=0 provenance exit=0
```

### 核心覆盖：vendor 宿主

```
cd D:\projects\cyber-reverse\replica
C:\Python312\python.exe tools/vendor_coverage.py
```

`exit 0`

```text
  wrote docs/VENDOR_COVERAGE.md
  controls ok=True  vendors named=13  wiring rows=0  missing=0
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
=== REPLICA  image base 0x140000000  file 57491456 bytes ===
  name       rva start    rva end      raw size     flags
  ------------------------------------------------------------------
  .text      0x1000       0x103268     1057792      X
  .managed   0x104000     0x1C26B18    28453888     X
  hydrated   0x1C27000    0x2BA49C8    0            RW
  .rdata     0x2BA5000    0x43B9AF6    25250816     R
  .data      0x43BA000    0x44B5038    226816       RW
  .pdata     0x44B6000    0x46C4C08    2158080      R
  _RDATA     0x46C5000    0x46C50F4    512          R
  .rsrc      0x46C6000    0x47117E7    309248       R
  .reloc     0x4712000    0x471A020    33280        R

  section-mass-replica-executable: 29511680
  section-mass-ratio: 57.09%

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
  replica : 179,840 functions, image base 0x140000000

  range from     original   replica    replica/original
  ----------------------------------------------------
  0x0            5,475      1,937        35.4%
  0x100000       5,089      4,803        94.4%
  0x200000       4,333      5,228       120.7%
  0x300000       2,213      3,795       171.5%
  0x400000       5,791      5,737        99.1%
  0x500000       2,057      4,004       194.7%
  0x600000       1,074      4,199       391.0%
  0x700000       3,411      3,164        92.8%
  0x800000       4,076      3,113        76.4%
  0x900000       3,556      2,523        71.0%
  0xA00000       3,178      5,683       178.8%
  0xB00000       3,227      5,575       172.8%
  0xC00000       3,982      6,662       167.3%
  0xD00000       3,921      7,529       192.0%
  0xE00000       3,371      5,856       173.7%
  0xF00000       7,792      3,939        50.6%
  0x1000000      5,626      7,737       137.5%
  0x1100000      2,020      9,500       470.3%
  0x1200000      2,046      10,220      499.5%
  0x1300000      5,065      9,660       190.7%
  0x1400000      10,107     10,074       99.7%
  0x1500000      11,107     9,048        81.5%
  0x1600000      2,864      9,730       339.7%
  0x1700000      2,242      9,171       409.1%
  0x1800000      4,058      9,575       236.0%
  0x1900000      4,506      5,619       124.7%
  0x1A00000      2,310      5,793       250.8%
  0x1B00000      6,033      8,692       144.1%
  0x1C00000      6,218      1,274        20.5%
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
  pdata-above-0x1C00000-replica: 1274
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
  mutation-fit-tree: RED
  mutation-fit-staleness: 350 -- src/Cybersole.Core/Models/SmartActions.cs (+349 more) differs from the run's manifest

  The counts above are from 2026-11-20T15:18:54+08:00 and the tree has moved since. They are a record of that run, not a
  statement about this one; re-run `python tools/mutation-check.py` before quoting them as current.
```

### 完整套件

```
cd D:\projects\cyber-reverse\replica
D:\tools\dotnet8\dotnet.exe test tests/Cybersole.Tests/Cybersole.Tests.csproj -c Debug --filter Speed!=Slow&FullyQualifiedName!~VoiceListTests&FullyQualifiedName!~GlobalSurfaceTests&FullyQualifiedName!~KeyOrderDispatchTests&FullyQualifiedName!~PatchJournalTests&FullyQualifiedName!~PruneWhitelistTests&FullyQualifiedName!~NetworkRecorderLiveTests&FullyQualifiedName!~ChromiumStealthTests -m:1
```

`exit 0` · 2486 通过 / 0 失败 / 0 跳过 / 2486 总计

```text
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MethodPatchTableTests.cs(77,9): warning xUnit2029: Do not use Assert.Empty to check if a value does not exist in a collection. Use Assert.DoesNotContain instead. (https://xunit.net/xunit.analyzers/rules/xUnit2029) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ObservableDictionaryTests.cs(77,9): warning xUnit2013: Do not use Assert.Equal() to check for collection size. Use Assert.Empty instead. (https://xunit.net/xunit.analyzers/rules/xUnit2013) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PayPalChallengeNotificationUrlTests.cs(54,9): warning xUnit2000: The literal or constant value PayPalThreeDs.NotifyChallengeCompleteUrl should be passed as the 'expected' argument in the call to 'Assert.NotEqual(expected, actual)' in method 'TheTwoSiblingsDifferInMoreThanTheirMiddleWord' on type 'PayPalChallengeCallbackBaseTests'. Swap the parameter values. (https://xunit.net/xunit.analyzers/rules/xUnit2000) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ObservableDictionaryTests.cs(109,9): warning xUnit2013: Do not use Assert.Equal() to check for collection size. Use Assert.Empty instead. (https://xunit.net/xunit.analyzers/rules/xUnit2013) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnmatchedGatewaysTests.cs(58,78): warning xUnit1031: Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await instead. (https://xunit.net/xunit.analyzers/rules/xUnit1031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SizePaletteTests.cs(24,9): warning xUnit2031: Do not use a Where clause to filter before calling Assert.Single. Use the overload of Assert.Single that accepts a filtering function. (https://xunit.net/xunit.analyzers/rules/xUnit2031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StepActionTests.cs(293,89): warning xUnit1031: Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await instead. (https://xunit.net/xunit.analyzers/rules/xUnit1031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SportsshoesFlowTests.cs(128,74): warning xUnit1031: Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await instead. (https://xunit.net/xunit.analyzers/rules/xUnit1031) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StripeChallengeWiringTests.cs(78,9): warning xUnit2013: Do not use Assert.Equal() to check for collection size. Use Assert.Single instead. (https://xunit.net/xunit.analyzers/rules/xUnit2013) [D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Cybersole.Tests.csproj]
  Cybersole.Tests -> D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\bin\Debug\net8.0\Cybersole.Tests.dll
D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\bin\Debug\net8.0\Cybersole.Tests.dll (.NETCoreApp,Version=v8.0)的测试运行
VSTest 版本 17.11.1 (x64)
正在启动测试执行，请稍候...
总共 1 个测试文件与指定模式相匹配。
已通过! - 失败:     0，通过:  2486，已跳过:     0，总计:  2486，持续时间: 3 m 42 s - Cybersole.Tests.dll (net8.0)
```

---

## 谁引用本文件

`AGENTS.md §4` · `docs/GOAL.md` 判据 a · `docs/HANDOFF.md` · `docs/COPY_QUEUE.md` 头部 ·
`replica/docs/SESSION_STATE.md` · `replica/docs/DEVIATIONS.md`。

`replica/docs/VERDICT.md` **不引用也不修改** —— 它是按轮次的历史记录。

