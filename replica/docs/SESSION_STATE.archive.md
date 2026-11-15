# 交接状态

> 这份文件是给「压缩上下文之后的我」看的。它只说四件事：**现在在哪、怎么验证、还剩什么、别踩哪些坑。**
> 细节在 `VERDICT.md`（历史）和 `PARITY.md`（能力表），这里不重复。

最后更新：第 401 轮（AYCD 的 `Connect` / `Disconnect` 标签补上并接线；套件 1575）。

---

## 近似错误队列：三分类

| 类别 | 例子 | 处置 |
|---|---|---|
| 真缺陷 | `Disconnect` 缺席（只有状态词 `disconnected`） | ✅ 已补（R401） |
| 拼接字符串造成的假阳性 | `" Custom Size"` vs `1 Custom Size` | 忽略 |
| 位置未定 | `Add Size` vs `Add Size(s)` | 先确认按钮再改 |

## 状态

```
完整套件   1575 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

最后更新：第 400 轮（`EmptyView.Body(key)` + Cloudflare 页改用自己的空状态文案；套件 1575）。

---

## `EmptyView` 现在支持"每页一句话"

```csharp
EmptyView.Body("cloudflare")   // "Add a Cloudflare provider to get started"
EmptyView.For("cloudflare")    // 完整控件
```

词典键：checkouts / feed / tasks / accounts / proxies / profiles / **cloudflare** / **smartActions**

## 状态

```
完整套件   1575 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
文案       4 区清零；Settings 21 条近似错误待核对（1 条已解决：Cloudflare 空状态）
```

最后更新：第 399 轮（Cloudflare 页空状态：想改但被 `EmptyView` 结构挡住，已留档在代码注释里）。

---

## 待做：`EmptyView` 需要"每页副标题"

- 现状：`UiKit.Empty(EmptyView.Headline)` 单行；守卫 `EmptyViewTests.EveryPageUsesTheSharedControl` 强制使用它
- 需要：`EmptyView` 支持每页副标题（如 `EmptyView.For(key)` 带 subtitle）
- 受益页：Cloudflare（`Add a Cloudflare provider to get started`）等

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
文案       4 区清零；Settings 21 条近似错误待核对；Cloudflare 空状态待结构改动
```

最后更新：第 398 轮（新增"近似错误"检测工具；21 条候选，**一处未改**，全部留待位置确认）。

---

## 近似错误队列（`python tools/locale_near_miss.py Settings`）

21 条 locale 与复刻件"几乎相同但不相等"的文案。**未修改**，因为：

- 有些位置已被**实测**固定（`Add Size(s)` 就是实测的 Chrome）；
- 有些 locale 键属于别的页面（`Settings.Data.ViewLogs` vs Smart Actions 页的按钮）。

**处置原则**：先确认这句文案在哪个界面、那个界面是否实测过；两者都有据才改。

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
文案       4 区清零；Settings 区 21 条近似错误待核对
```

最后更新：第 397 轮（Accounts 左栏底部改为"组数"；发现两个空状态被我混淆并回滚）。

---

## 两个空状态（别再混）

| 键 | 原文 | 用在哪 |
|---|---|---|
| `Accounts.Empty.NoStores.Subtitle` | `No stores matched your search` | 左栏店铺搜索 |
| `Accounts.Empty.NoResults.Subtitle` | `There are no accounts matching your search` | 账户列表搜索 |

守卫 `TheAccountsRailIsATwoLevelTreeSoItDoesNotUseTheGrid` 会盯着第一条的字面量。

## 已接线 / 待接线

| 区域 | 状态 |
|---|---|
| TaskGroup | ✅ 标签已接（R396） |
| Accounts | 部分（组数已接；空状态待接第二条） |
| Proxies / Tasks / Profiles | 常量已加，控件未接 |

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
```

最后更新：第 396 轮（TaskGroup 文案清零，并把 delayer/limits/captcha/notifications 的标签真的接上）。

---

## 文案清零的五个区域

| 区域 | 条数 | 轮次 | 是否接到界面 |
|---|---|---|---|
| Accounts | 10 | R392 | 常量（待接线） |
| Proxies | 6 | R393 | 常量（待接线） |
| Tasks | 10 | R394 | 常量（待接线） |
| Profiles | 13 | R395 | 常量（待接线） |
| **TaskGroup** | **10** | **R396** | **已接线** |

**下一步**：把前四个页面的常量替换到实际控件上（照 R396 的做法：先断言原行内容，再按行改）。

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

最后更新：第 395 轮（Profiles 页文案 13 → 0；四个页面合计 39 条原文补齐）。

---

## 文案缺口：四个区域清零

| 区域 | 条数 | 轮次 |
|---|---|---|
| Accounts | 10 | R392 |
| Proxies | 6 | R393 |
| Tasks | 10 | R394 |
| Profiles | 13 | R395 |

命令：`python tools/locale_text_gap.py <Area>`

**下一批**：TaskGroup 20 / SmartActions 20 / Data 19 / TaskCreator 33 / Settings 240。

## 状态

```
完整套件   1572 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

最后更新：第 394 轮（Tasks 页文案 10 → 0；三个页面文案已清零；套件 1565）。

---

## 文案缺口：已清零的三个区域

| 区域 | 结果 |
|---|---|
| Accounts | 0（R392，10 条） |
| Proxies | 0（R393，6 条） |
| Tasks | 0（R394，10 条） |

命令：`python tools/locale_text_gap.py <Area>`

**下一批**：Profiles 26 / TaskGroup 20 / SmartActions 20 / Data 19 / TaskCreator 33 / Settings 240。

## 状态

```
完整套件   1565 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

最后更新：第 393 轮（Proxies 页文案 6 → 0；套件 1559）。

---

## 文案缺口进度（`python tools/locale_text_gap.py <Area>`）

| 区域 | 缺 | 状态 |
|---|---|---|
| Accounts | 10 | ✅ 已补（R392） |
| Proxies | 6 | ✅ 已补（R393） |
| Tasks | 10 | 待补 |
| Profiles / Settings / TaskCreator / SmartActions / TaskGroup / Data / … | 未清点 | 待补 |

## 状态

```
完整套件   1559 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

最后更新：第 392 轮（新增文案缺口工具；Accounts 页补回十条原文；套件 1554）。

---

## 现在有四条度量线

| 度量 | 工具 | 现状 |
|---|---|---|
| 名字级绑定缺口 | `tools/bind_diff.py` | 17 |
| 类型级绑定缺口 | `tools/bind_scope.py` | 12 |
| 成员形状差异（已接受） | `tools/shape_audit.py` | 272 |
| **文案缺口** | **`tools/locale_text_gap.py` / `locale_coverage.py`** | **582 键中引用 99（17%）** |

文案缺口是新的一层：按键统计 17%，但**按原文匹配**能直接列出"这句界面文字复刻件里没有"。

## 状态

```
完整套件   1554 通过 / 0 失败 / 2 跳过
缺口       17 / 12 /（文案未全面清点）
```

最后更新：第 391 轮（原版备份的嵌套对象钉住：`AycdInbox` 5 字段、`Solver` 4 持久化字段）。

---

## 绑定 ≠ 持久化（两个方向都已确认）

| 成员 | 绑定表 | 原版备份 |
|---|---|---|
| `Solver.Name` / `View` / `Reload` | ✅ | ❌ |
| `TaskGroup.UsagePeriod` / `ProxyGroup.UsagePeriod` | ❌ | ✅ |

**判断"该不该有"时，先问是哪一层在说话。**

## 状态

```
完整套件   1547 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
LiveSchemaPinsTests  6 个用例
```

最后更新：第 390 轮（设置字段钉子换成原版备份的 44 键；四个多余设置项记入 DEVIATIONS）。

---

## 待 IDA 恢复后确认的四项

`EnableClock` · `ClockFormat` · `MonitorConcurrency` · `StoreGroups`
—— 原版备份里没有，复刻件会写出去。**没删**（删了会砍功能），记在 `docs/DEVIATIONS.md` 第八节。

## 状态

```
完整套件   1546 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
证据       字符串池/locale/绑定表 + 原版备份（紧凑 camelCase）可信
```

最后更新：第 389 轮（从原版备份补出 `TaskGroup.UsagePeriod` / `ProxyGroup.UsagePeriod`）。

---

## 原版备份给出的结构（可信）

```
tasks[]    16 字段（含 usagePeriod 与 usageExpiry 两个）
proxies[]   8 字段（含 usagePeriod 与 usageExpiry 两个）
solvers[]  left / top / width / height / solvers
settings   44 键（含 bearer / license / quickTaskProxies / shopifyBrowserProxy / browserPath）
```

**R54 的"代理组没有独立 usagePeriod"被推翻**：绑定表只说 XAML 绑了什么，持久化层两个都写。

## 状态

```
完整套件   1546 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

最后更新：第 388 轮（格式指纹判定文件作者；备份改为紧凑写出；证据重新分类）。

---

## 证据来源判定（用格式指纹）

| 证据 | 判定 | 结论 |
|---|---|---|
| `settings/tasks/solvers/accounts/billing/proxies/analytics/smartActions.json` | **复刻件自己写的** | 不能用作"实机"证据 |
| `checkoutHistory.json` | 与复刻件同风格 | 不能用作证据 |
| `Backups\*.cyb`（13 Nov，紧凑 camelCase） | **原版写的** | `.cyb` 九键结论**成立** |
| 字符串池 / locale / 绑定表 | 从 exe 读的 | **始终可信** |

## 状态

```
完整套件   1545 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
观察       HomePageParityTests 曾偶发 1 次失败，重跑通过
```

最后更新：第 387 轮（**发现复刻件一直在写原版数据目录**；已隔离并复核证据可信度）。

---

## 数据目录已隔离

```
复刻件   %APPDATA%\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\Cybersole             （只读证据，永不写入）
留存     analysis/apdata-preserved-20261114-095358/   （16 个文件）
守卫     TheReplicaNeverWritesIntoTheOriginalsDataDirectory
```

## 证据可信度（重要）

| 证据 | 状态 |
|---|---|
| 字符串池 / locale / 绑定表 | ✅ 可信 |
| `settings.json` 43 键、`tasks.json`、`solvers.json` | ❌ **撤回**（可能是复刻件写的） |
| `checkoutHistory.json`、`.cyb` 备份 | ⚠️ 待复核 |

`LiveSchemaPinsTests` 保留（回归价值），但注释里的"来自实机"按待复核处理。

## 状态

```
完整套件   1545 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

最后更新：第 386 轮（`smartActionUtilities` 键名 `utilities` → `groups`；小文件格式全部钉住）。

---

## 文件格式对齐情况（六项全部已钉）

| 实机文件 | 复刻件类型 | 测试 |
|---|---|---|
| `settings.json` | `GlobalSettings` | `TheSettingsFileFieldsAllExist` |
| `tasks.json` | `TaskGroup` | `TheTaskGroupFileFieldsAllExist` |
| `solvers.json` | `Solver`/`SolverSettings` | `TheSolverFileFieldsAllExist` |
| `accounts.json` / `analytics.json` / `smartActions.json` / `smartActionUtilities.json` | 各自 Document | `TheSmallerDocumentsAlsoUseTheImagesKeyNames` |
| `billing.json` / `proxies.json` | `BillingGroup`/`ProxyGroup` | `TheGroupFilesCarryAtLeastTheImagesFields` |
| `Backups\*.cyb` | `BackupDocument` | `TheBackupFileUsesTheImagesKeyNames` |

## 状态

```
完整套件   1544 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

最后更新：第 385 轮（**R384 的修复没生效**：属性用错序列化器；已改 Newtonsoft 并让测试真的序列化）。

---

## 序列化器（务必记住）

```
项目用 Newtonsoft.Json
AppPaths/Store.Json.Default = CamelCaseNamingStrategy + StringEnum(camelCase) + TimeSpanJsonConverter
Formatting.Indented, NullValueHandling.Ignore, DateTimeZoneHandling.Utc
```

**`System.Text.Json` 的属性在这个项目里是死的。** 要改键名只能 `[Newtonsoft.Json.JsonProperty]`。

## 状态

```
完整套件   1542 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
文件格式   settings / tasks / solvers / checkoutHistory / .cyb 五项已对齐并钉住
```

最后更新：第 384 轮（备份文件键名与实机对齐：`BackupDocument` 九个 `[JsonPropertyName]`）。

---

## 文件格式已对齐（这一轮最重要）

实机 `.cyb` 顶层键 = `proxies, billing, accounts, solvers, settings, tasks, smartActions, smartActionUtilities, analytics`。
复刻件原来用 PascalCase 且少一个、多两个 → **两边备份互不兼容**，已修并用测试钉住。

## 已核对的实机文件格式

| 文件 | 复刻件对应 | 状态 |
|---|---|---|
| `settings.json` | `GlobalSettings` | 43 键全中 |
| `tasks.json` | `TaskGroup` | 10 键全中 |
| `solvers.json` | `Solver` + `SolverSettings` | 4 + 7 全中 |
| `checkoutHistory.json` | `CheckoutEvent` | 9 键全中 |
| `Backups\*.cyb` | `BackupDocument` | **R384 修好并钉住** |

## 状态

```
完整套件   1542 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

最后更新：第 383 轮（`LiveSchemaPinsTests`：把实机 JSON 的 43+10+4+7 个字段名钉进测试）。

---

## 现在的"最硬约束"三件套

| 约束 | 内容 |
|---|---|
| `LiveSchemaPinsTests` | 实机落盘的字段名（settings / taskGroup / solver / solverSettings） |
| `bind_scope.py` | 类型级绑定缺口 12 |
| `bind_diff.py` | 名字级缺口 17 |

**改名字会同时被第一和第三条抓到。**

## 状态

```
完整套件   1541 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 382 轮（发现实机落盘 JSON，新增 `tools/live_schema_diff.py`；设置/任务组字段全对上）。

---

## 新的最硬证据源：`%APPDATA%\Cybersole\*.json`

```
python tools/live_schema_diff.py
```

| 文件 | 类 | 结果 |
|---|---|---|
| `settings.json` | `GlobalSettings` | live 43 / replica 48，**缺 0** |
| `tasks.json` | `TaskGroup` | live 10 / replica 25，**缺 0** |
| `billing.json` / `accounts.json` / `proxies.json` / `smartActions.json` | — | 顶层结构已记录 |

**这是程序自己写的字段名** —— 比 locale 和 GUI 都硬。

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 381 轮（重启实机 → 量登录窗口；首屏去掉 `Use a code instead`）。

---

## 实机状态

原版进程在跑，停在 **Login** 窗口（登录态已失效）。GUI 无法进入主界面，因为需要用户账号登录。

**登录窗口已核对完毕**（第十个实机界面）：三样可交互控件，文案逐条命中 locale。

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 380 轮（`PublishTemplateModal.Groups`；类型级缺口 13 → 12）。

---

## 剩余 12 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.Items/Store` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`SmartActionsView.Clock/Export` · `TaskView.Toggle`

**共同点**：都需要"界面位置"或"真实数据/服务"才能定，光看名字定不了。

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级，起点 52）
UI 类      104 声明 / 28 不可达
```

最后更新：第 379 轮（`HistoryWindow.SmartAction/View`；类型级缺口 14 → 13）。

---

## 剩余 13 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.*` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`PublishTemplateModal.Groups` · `SmartActionsView.Clock/Export` · `TaskView.Toggle`

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 13（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 378 轮（`CloudflareSolversView.FetchBalance` 提取；套件 1538 通过）。

---

## 提取成员的收益（这一轮的例子）

`FetchBalance()` 把按钮里的整段逻辑变成可调用成员，于是**两条"不该发请求"的早退分支**第一次有了测试：

```
没有 provider      → "No Cloudflare provider configured."
有 provider 无 key → "cf: no API key, so no balance to ask for."
```

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 14（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 377 轮（`StoreGroupModal.Delete/IsEditing`；类型级缺口 15 → 14）。

---

## 配置集合的真实路径（血泪版）

| 想写的 | 真实的 |
|---|---|
| `Config.TaskGroups` | ✅ |
| `Config.BillingGroups` | ✅ |
| `Config.Profiles` | ❌ 不存在（在 `BillingGroups[i].Profiles`） |
| `Config.StoreGroups` | ❌ 不存在（是 `Config.Settings.StoreGroups`） |

写之前先 `grep 'List<' src/Cybersole.Core/Settings/GlobalSettings.cs`。

## 状态

```
完整套件   1536 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 14（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 376 轮（`GroupSummary.Edit/Clone/Delete`；类型级缺口 16 → 15）。

---

## 剩余 15 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.*` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit/FetchBalance` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`HistoryWindow.SmartAction/View` · `PublishTemplateModal.Groups` · `SmartActionsView.Clock/Export` ·
`TaskView.Toggle` · `StoreGroupModal.Delete/IsEditing`

## 状态

```
完整套件   1536 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 15（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 375 轮（`AnalyticsView.OpenRelease`；不可达 UI 类 29 → 28；新增 `tools/wire_candidates.py`）。

---

## 新工具：`tools/wire_candidates.py`

列出"没有任何地方构造的 UI 类"与"绑定表里 `Show*`/`Open*` 成员"的名字匹配 —— **接线的候选队列**。

本轮据此补了 `AnalyticsView.OpenRelease`（`ReleaseView` 因此可达）。

## 剩余 16 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.*` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit/FetchBalance` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`HistoryWindow.SmartAction/View` · `PublishTemplateModal.Groups` · `SmartActionsView.Clock/Export` ·
`GroupSummary.Clone/Delete/Edit` · `TaskView.Toggle` · `StoreGroupModal.Delete/IsEditing`

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 16（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 374 轮（`ReleaseView.ShowSitelist`；缺口 16，不可达 UI 类 29）。

---

## 连着两轮都是"把已有视图接上"

| 轮 | 成员 | 接上的既有视图 |
|---|---|---|
| R373 | `TaskView.CreateGroup` | `TaskGroupView` |
| R374 | `ReleaseView.ShowSitelist` | `ReleaseSitelistView` |

**不可达 UI 类 31 → 29。** 剩下的 29 个多半是原版也没有的弹窗，或需要真数据才有意义。

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 16（类型级）
UI 类      104 声明 / 28 不可达
```

最后更新：第 373 轮（`TaskView.CreateGroup` / `MoveGroup`；`TaskGroupView` 变为可达，不可达 UI 类 31 → 30）。

---

## `TaskView` 只剩 1 个无定论

`Toggle`（`CreateGroup` / `MoveGroup` / `LinkChange` / `Quicktask` / `PinGroups` 都已落地）

## 可达性指标会动

`TaskGroupView` 因为 `CreateGroup()` 构造它，从"不可达基线"里删除 →
指南数字 31 → 30（三份文档同步）。**这类红是改善，不是回归。**

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 17（类型级）
UI 类      104 声明 / 30 不可达
```

最后更新：第 372 轮（`TaskView.LinkChange` / `Quicktask`：读剪贴板 + 原件失败文案；缺口 5 → 3）。

---

## `TaskView` 剩余 3 个无定论

`CreateGroup` · `MoveGroup` · `Toggle`

## 这一轮学到的（第 N 次同一个病）

`BotTask` 没有 `Url`、`TaskEngine` 没有 `Add`、属性初始化器里不能写 `this` ——
**先读模型字段与引擎方法，再写调用**（`docs/METHOD.md` §12.2 的延伸）。

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 17（类型级）
```

最后更新：第 371 轮（`AccountView.CreateGroup` 提取；**IDA MCP 当前不可用**，已记录恢复条件）。

---

## 工具状态（影响下轮路线）

```
ida MCP  PROXY MISSING / INSTANCE none / PORT 13337 REFUSED
恢复      重启 DSH 或重开 IDA 并载入库（两者都会中断会话）→ 需要用户在方便时决定
```

在恢复之前：**只做池子/代码内的推进**，需要反编译才能定的项继续留白。

## 新纪律

**在类里插方法，锚点必须是方法声明，不能是方法体里的一行**（R371 因此把成员插进了 ctor）。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 17（类型级）
```

最后更新：第 370 轮（`TaskView.PinGroups`；否证了"绑定表漏成员"的怀疑）。

---

## 已否证（不必再查）

- 池子的访问器证据**没有**给出绑定表之外的类型或成员（102 vs 174，差集为空）；
  它唯一多给的是**形状**（`docs/BINDING_SHAPES.md`）。

## `TaskView` 剩 5 个无定论成员

`CreateGroup` · `LinkChange` · `MoveGroup` · `Quicktask` · `Toggle`
（`PinGroups` 已按"可读写属性 + `TaskGroup.Pinned`"实现）

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

最后更新：第 369 轮（新增 `docs/DEVIATIONS.md` 差异账本；关掉原版进程把 available 从 2.87 GB 拉回 3.69 GB）。

---

## 差异账本（`docs/DEVIATIONS.md`）

七节：绑定形状(272) · UI 结构 · 文案/URL(inferred) · 不可得(三源否证) · 故意留白 · 类型级缺口(18) · 怎么读。

**判断 1:1 分三层**：行为（最实）→ 结构/文案（次之）→ 形状（有意保留差异）。

## 内存纪律（这轮再次触发）

`available < 4 GB` 时：不做变异测试（29 轮编译）、不跑完整套件，只跑文档守卫（57 个）。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过（上一轮跑过）
缺口       17（名字级）/ 18（类型级）
原版进程   已关闭（需要 GUI 核对时再启动）
```

最后更新：第 368 轮（新增 `tools/shape_audit.py`；量化出 273 处形状差异，**决定不改**并记录理由）。

---

## 一个已知且被接受的差异

```
有访问器证据的成员 465（可写 327 / 只读 138）
形状不一致       273 → 272   （"池子说可写，复刻件是方法"）
```

原因：原件用 XAML `Command=` 绑动作（动作=属性），复刻件手写控件树（动作=方法）。
**行为等价，形状不同**。存量不改；新增动作成员按 §13 写成 `ICommand` 属性。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

最后更新：第 367 轮（新增 `tools/bind_shape.py` 与 `docs/BINDING_SHAPES.md`：102 个类型的成员形状）。

---

## 新账本：成员形状

```
python tools/bind_shape.py [过滤词]
docs/BINDING_SHAPES.md        ← 102 个类型 × 每个绑定成员的 Property/Getter/Setter
```

| 形状 | 含义 | 写法 |
|---|---|---|
| `Getter,Property,Setter` | 可读写属性 | 用户动作 → `ICommand` 属性；数据 → 可写属性 |
| `Getter,Property` | 只读属性 | 数据 |
| — | 无访问器证据 | 可能是方法 |

**已应用**：`AccountGroupView.GroupName` 改为可写（证据有 `Setter`）。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

最后更新：第 366 轮（`GoogleAccountsView.YouTube`；发现绑定成员可能是**命令属性**）。

---

## 新认识：绑定成员的"形状"（`docs/METHOD.md` §13）

池子里出现 `get_Add` / `get_Clear` / `get_Edit` / `get_Delete` → 原件的这些成员是 **`ICommand` 属性**。
复刻件写成方法，行为等价，但 XAML 的 `Command=` 只能绑属性。

**今后新增"用户动作"类成员，优先写成 `ICommand` 属性。**

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

最后更新：第 365 轮（`ProfileView.Groups/DeleteSelected/EditSelected`；类型级缺口 18）。

---

## 类型级缺口：18（起点 52）

剩下的都是界面动作或类型不可推断：
`TaskView`(6) · `GroupSummary`(3) · `ProfileCreatorView`(3) · `DataView.ViewLogs` ·
`SmartActionsView.Clock/Export` · `ReleaseView.ShowSitelist` · `ImapView.Configure` · `PublishTemplateModal.Groups`

## 新纪律（`docs/METHOD.md` §12.2）

读类时**同时读字段与方法**；写 `Config.X` 之前先 `grep 'Config\.'` 确认那个集合真的存在。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

最后更新：第 364 轮（`BotTask` 五成员；类型级缺口 19）。

---

## 类型级缺口：19（起点 52）

剩下主要是界面动作：`TaskView`(6) · `GroupSummary`(3) · `ProfileView`(3) · `ProfileCreatorView`(3) ·
`DataView.ViewLogs` · `SmartActionsView.Clock/Export` · `ReleaseView.ShowSitelist` · `ImapView.Configure` 等。

**留白清单**（类型不可推断）：`CreateModel.Input/Inputs`、`BotTask.Task`。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 19（类型级）
```

最后更新：第 362 轮（`TaskGroup.Running`（派生）/`CloudflareSolverId`、`NotificationOptions.Name`；类型级缺口 21）。

---

## 类型级缺口：21（起点 52，已降 60%）

剩下的多是"需要 UI 位置"或"行为未知"的：
`CreateModel`(17) · `BotTask`(6) · `TaskView`(6) · `GroupSummary`(3) · `ProfileView`(3) ·
`ProfileCreatorView`(3) · 以及零散的 `ViewLogs` / `Clock` / `Export` / `ShowSitelist` 等。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 21（类型级）
```

最后更新：第 361 轮（`Solver` 四成员 + `CaptchaProvider` 三字段；类型级缺口 25 → 23）。

---

## 模型层两个"同类记录"现在对等了

| 字段 | `CloudflareSolverConfig` | `CaptchaProvider` |
|---|---|---|
| `Count` | 原有 | **R361 补** |
| `BalanceSupported` | 原有 | **R361 补** |
| `IsFetchingBalance` | — | **R361 补** |

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 23（类型级，起点 52）
```

最后更新：第 360 轮（`WebTask.Steps` / `Product.Color` / `SmartAction.Logs`；类型级缺口 25）。

---

## 经验：模型层成员最省力

`WebTask.Steps`、`Product.Color`、`SmartAction.Logs` 三个都只加数据，不涉及 UI 定位，
编译一次通过。**先把这一层做完，剩下的都是界面问题。**

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 25（类型级，起点 52）
```

最后更新：第 359 轮（`SolverWindow.Minimise` / `Dispose`；类型级缺口 28）。

---

## 一条新补的纪律（`docs/METHOD.md` §12.1）

**加成员前连基类一起读**：`Window` 没有 `Dispose`，写 `new` + `base.Dispose()` 直接编译失败。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 28（类型级，起点 52）
```

最后更新：第 358 轮（`ProfileGroupView.GroupName` / `AccountGroupView.GroupName` / `TaskGroupListView.Groups`；缺口 29）。

---

## 类型级缺口的处理节奏（已稳定）

1. 先 `python tools/snapshot.py`；
2. `grep 'class X' -Context 0,20` 读字段与构造；
3. 按真实形状加**一个**成员；
4. `dotnet build` → 通过再加下一个。

R358 用这套流程补了三个成员，**零编译错误**。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 29（类型级，起点 52）
```

最后更新：第 357 轮（`MessageBoxDialog.Type` = `MessageBoxType`；`ProfileCsvEditorView.GroupName`；缺口 32）。

---

## 测试上的硬限制（记住）

**`Window` 在没有 Avalonia 平台时无法构造**：`new MessageBoxDialog(...)` 会抛
`Unable to locate 'Avalonia.Platform.IWindowingPlatform'`。
→ 涉及 `Window` 的绑定成员，测试只能用**反射**断言，不能构造实例。

`UserControl`（如 `TaskDetailsView`、`ProfileCsvEditorView`）可以构造，`Close()` 无宿主时返回 false。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 32（类型级）
```

最后更新：第 356 轮（`Close` 家族再扩 4 个类型 + `ProxyGroupView.Delete`；类型级缺口 34）。

---

## `Close` / `Cancel` 家族覆盖

`TaskCreatorView` · `TaskDetailsView` · `TaskGroupView` · `ProxyCreatorView` · `ProxyGroupView` ·
`ProfileGroupView` · `StaggerStartView(Cancel)` · `HelpView.OpenUrl` · `UserView.OpenUrl`

约定：**无宿主窗口 → 返回 false**（可断言，不抛）。

## 新纪律（`docs/METHOD.md` §12）

写方法前先 `grep 'class X' -Context 0,30` 看字段与构造；类没有所需依赖就把依赖作为参数传入。
**一次只加一个成员，加完立刻编译。**

## 状态

```
完整套件   1523 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 34（类型级）
```

最后更新：第 355 轮（`Close`/`OpenUrl` 家族补五处；类型级缺口 40 → 37）。

---

## `Close` / `OpenUrl` 的约定（今后照此写）

```csharp
public bool Close()   // 无宿主窗口 → false
public static bool OpenUrl(string url)   // 无法启动浏览器 → false
```

两处都**返回 bool**，让"无宿主/无浏览器"可断言。

已覆盖：`UserView.OpenUrl`、`TaskGroupView.Close`、`TaskDetailsView.Close`、`TaskCreatorView.Close`、`HelpView.OpenUrl`。

## 状态

```
完整套件   1521 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 37（类型级）
```

最后更新：第 354 轮（`TaskGroupView` 绑定成员清零：`CloudflareSolvers` 成属性、`Close` 补上；类型级缺口 40）。

---

## 类型级缺口：40（起点 52）

| 已清零的类型 | 轮次 |
|---|---|
| `IWebhook` | R342 |
| `LoginControl` | R343 |
| `HelpView` | R346 |
| `CustomStoresView` / `CustomSizesView`（除 `View`） | R347 |
| **`TaskGroupView`** | **R354** |

## 一条守卫的处置（值得记住）

`TheTaskGroupDropdownStillReadsTheCaptchaRegistry` 因结构变化变红 ——
**行为没变，所以改守卫**，并把它拆成三条断言（组合框读属性 / 属性读注册表 / 字段仍被写回）。

## 状态

```
完整套件   1518 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 40（类型级）
```

最后更新：第 353 轮（先建 `tools/snapshot.py` 快照，再把 Group Settings 收敛到实机的 4 个 tab）。

---

## 安全网

```
python tools/snapshot.py   →  tools/.snapshots/<时间戳>/   （245 个 .cs）
```

**改结构前先跑它。** 上一轮靠 `.mutation-backup/` 救回四个类，这一轮起有自己的快照。

## Group Settings 现在与实机一致

| 项 | 状态 |
|---|---|
| 4 个 tab（Delays/Limits/Captcha/Notifications） | ✅ |
| `Group Name` 在 tab 之上 | ✅ |
| 页脚 `Delete` / `Save` | ✅ |
| `Period start` 在 Limits | ✅ |
| `Pinned` / `Order` / `Manual` 移除 | ✅ |

剩 `TaskGroupView.CloudflareSolvers`（Captcha tab 的求解器列表）待补。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 41（类型级）
```

最后更新：第 352 轮（**切坏文件 → 从 `tools/.mutation-backup/` 恢复**；R345/R351 重做完毕，1515 绿）。

---

## 事故与恢复（务必记住）

| 项 | 内容 |
|---|---|
| 事故 | 用"行号切文件"删两个方法，切掉 `TaskDetailsView` / `GroupSummary` / `TaskGroupListView` / `TaskGroupView.Save+Reset` |
| 现场 | 无 git、无还原点 |
| 恢复 | `replica/tools/.mutation-backup/TasksViews.cs`（07:57 快照）复制回来 → 编译 0 错误 |
| 重做 | R345（`GroupSummary.StartAll/StopAll`）、R351（名字在 tab 之上 / `Delete`+`Save` 页脚 / `DeleteGroup`） |
| 结果 | 完整套件 **1515 通过 / 0 失败 / 2 跳过** |
| 未完成 | R352 的 4 tab（正是切坏文件的那一步） |

## 新规矩（`docs/METHOD.md` §11）

1. 改结构**整段替换**，不用行号；
2. 一次只切一处，**切完立刻编译**；
3. **不要清空 `tools/.mutation-backup/`** —— 它是唯一保险；
4. 非切不可时，先手工复制一份 `*.cs.bak`。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 41（类型级）
```

最后更新：第 351 轮（Group Settings：`Group Name` 移到 tab 之上、页脚改 `Delete/Save`）。

---

## Group Settings 现状（`TaskGroupView`）

| 项 | 实机 | 复刻件 |
|---|---|---|
| `Group Name` | tab 之上的独立行 | **已同（R351）** |
| 页脚 | `Delete`(红) / `Save` | **已同（R351）** |
| tab 数 | 4（Delays/Limits/Captcha/Notifications） | 仍是 6（多 `General` / `Manual`） |
| `Pinned`/`Order`/`PeriodStart` | 未找到位置 | 仍在 `General` / `Manual` |

**下轮**：把实机 `Limits` / `Captcha` / `Notifications` 三个 tab 的内容读全，再一次性收敛 tab 数。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41
```

最后更新：第 350 轮（实机 Group Settings：4 tab vs 复刻件 6 tab，**只记录待改**）。

---

## 待改：Group Settings 弹窗（证据已录，下轮动手）

| 项 | 实机 | 复刻件 |
|---|---|---|
| tab 数 | **4**（Delays / Limits / Captcha / Notifications） | 6（多 `General` / `Manual`） |
| `Group Name` | **tab 之上的独立字段** | 在 `General` tab 里 |
| `Pinned` / `Order` / `PeriodStart` | 未见 | 在 `General` / `Manual` 里 |

**下轮第一步**：把实机 `Limits` / `Captcha` / `Notifications` 三个 tab 的内容读完，再一次性重构。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41
```

最后更新：第 349 轮（导出提示改为 locale 原文；留白项挖到文案线索："Mass Link Change" 等）。

---

## 留白项的文案线索（下次不用再找）

| 名字 | 线索 |
|---|---|
| `TaskView.LinkChange` | `Monitor.LinkChange`="Link Change"、字面量 **"Mass Link Change"** → 批量改链接 |
| `TaskView.Quicktask` | `Monitor.LaunchQuicktask`="Launch Quicktask" |
| `SmartActionsView.Clock` | `Settings.General.EnableClock`="Enable clock" + `.Tooltip` → 受设置控制的时钟显示 |
| `DataView.Export` | `Data.Export.Fail.Title`="Export Fail" / `.Message`="Failed to export data." |

## 本轮落地

`DataView.ExportSuccessTitle` / `ExportFailTitle` / `ExportFailMessage` 三个常量 + 失败行改用 locale 原文；
`DataExportCopyTests` 钉住。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41
```

最后更新：第 348 轮（`HistoryWindow.Exit/Minimise` + `SmartActionsView.OpenCreator`；成员数在降，类型数仍 41）。

---

## 计量提醒（`docs/METHOD.md` §10.2）

`bind_scope.py` 数的是**类型**：两个类型各少 2 个成员时，总数**不动**。
看进展要同时看**类型数**与**成员数**。

## 已修的绑定名（累计）

`IWebhook` 六成员 · `LoginControl` 五操作 · `TaskView.ClearAll/OpenSettings` ·
`GroupSummary.StartAll/StopAll` · `HelpView.OpenUrl` · 两个自定义页 `Rows/Delete` ·
`HistoryWindow.Exit/Minimise` · `SmartActionsView.OpenCreator`

## 留白（行为未知，只记名）

`TaskView` 六个 · `SmartActionsView.Clock/Export` · `GroupSummary` 三个 ·
`HistoryWindow.SmartAction/View` · `PublishTemplateModal.Groups` · 两个自定义页的 `View`

## 状态

```
完整套件   1514 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41（类型口径）
```

最后更新：第 347 轮（`CustomStoresView` / `CustomSizesView` 补 `Rows` / `Delete`；`View` 留白；类型级缺口 41）。

---

## 类型级缺口修到 41（起点 52）

| 类型 | 轮次 | 修了什么 |
|---|---|---|
| `IWebhook` | R342 | 六成员补齐 |
| `LoginControl` | R343 | 五个操作提为成员 |
| `TaskView` | R344 | `ClearAll` / `OpenSettings` |
| `GroupSummary` | R345 | `StartAll` / `StopAll` |
| `HelpView` | R346 | `OpenUrl` |
| `CustomStoresView` / `CustomSizesView` | R347 | `Rows` / `Delete` |

**留白清单**（行为未知，只记名）：两个自定义页的 `View`、`TaskView` 六个、`SmartActionsView` 三个、
`GroupSummary` 三个、`HistoryWindow` 四个、`PublishTemplateModal` 一个。

## 状态

```
完整套件        1513 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      41（筛查器口径）
mutation        29 / 29 fired
```

最后更新：第 346 轮（`HelpView.OpenUrl` 提为成员并删除旧本地函数；类型级缺口 44 → 43）。

---

## 类型级缺口：已修三个类型（R343–R346）

| 类型 | 修了什么 |
|---|---|
| `LoginControl` | `Cancel` / `OpenBrowser` / `SignUp` / `UseCode` / `SignInAsync` |
| `TaskView` | `ClearAll` / `OpenSettings` |
| `GroupSummary` | `StartAll` / `StopAll` |
| `HelpView` | `OpenUrl`（并删掉被取代的本地函数） |

剩余 43 条筛查器命中里，真缺口与框架误报混在一起；每条按三档处理：
**提名字 / 照名实现 / 只记名**。

## 状态

```
完整套件        1511 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      43（筛查器口径）
mutation        29 / 29 fired
```

最后更新：第 345 轮（`GroupSummary` 补 `StartAll`/`StopAll`；`Clone`/`Delete`/`Edit` 按规则留白）。

---

## 三档处理的第二次应用

| 成员 | 判定 | 结果 |
|---|---|---|
| `GroupSummary.StartAll` / `StopAll` | 语义无歧义 | **已实现**（返回计数，可测） |
| `GroupSummary.Clone` / `Delete` / `Edit` | 语义未定 | **留白**，记在 `docs/BINDING_BACKLOG.md` |

## 两次编译失败的原因（同一老毛病）

`StopAll` 实际签名是 `StopAll(IEnumerable<string> ids)`；`BotTask.IsRunning` 是**只读计算属性**。
都是"没先读那一行"（R259 / R302 / R325 同源）。

## 状态

```
完整套件        1509 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      44（筛查器口径）
mutation        29 / 29 fired
```

最后更新：第 344 轮（`TaskView` 补 `ClearAll`/`OpenSettings`；六个未知行为**记名不猜**）。

---

## 类型级缺口的处理原则（R344 定下）

| 情况 | 做法 |
|---|---|
| 行为已存在、只是名字不同 | **提成绑定名**（R343 `LoginControl`、R344 `TaskView.ClearAll`） |
| 行为清楚、尚未落到该类型 | 照绑定名实现（如 `OpenSettings` 导航） |
| **行为未知** | **只记名**，写进 `docs/BINDING_BACKLOG.md`，不编实现 |

当前"记名未落"的：`TaskView` 六个（`CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle`）、
`SmartActionsView` 三个、`GroupSummary` 五个、`HistoryWindow` 四个、`PublishTemplateModal` 一个。

## 状态

```
完整套件        1507 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      44（筛查器口径，含框架成员误报）
mutation        29 / 29 fired
```

最后更新：第 343 轮（`LoginControl` 五个绑定操作成为成员；`bind_scope.py` 修好块提取）。

---

## 这一轮两件事

1. **`LoginControl`**：`Cancel` / `OpenBrowser` / `SignUp` / `UseCode` / `SignInAsync` 从匿名回调变成成员，
   按钮改为调用（同一手法见 R239）。`bind_scope.py` 里该类型已干净。
2. **`bind_scope.py` 修好**：花括号配对 + 基类上溯；数字 52 → 44，且不再抖动。

## 工具现在的定位

**筛查器，不是判决书**：44 个"类型级缺成员"里仍有框架成员误报（`Close` 等）。
每条要手工复核；本轮抽的 `LoginControl` 五条全为真。

## 状态

```
完整套件        1506 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      44（筛查器口径，含误报）
mutation        29 / 29 fired
```

最后更新：第 342 轮（`IWebhook` 补齐六成员；**发现缺口口径盲点**，新增 `tools/bind_scope.py`）。

---

## 两个缺口口径（都要看）

| 口径 | 工具 | 当前值 | 说明 |
|---|---|---|---|
| 名字级 | `tools/bind_diff.py` | **17** | 成员名在整个仓库里出现过即算满足 |
| **类型级** | `tools/bind_scope.py`（R342 新增） | **23 类** | 成员必须长在**该类型**上 |

`IWebhook` 缺 `Events/Type` 但名字级看不见 —— 因为 `TaskGroup` 等类型早就有这两个名字。

## 类型级缺口 top（已抽查为真）

| 类型 | 缺的成员 |
|---|---|
| `LoginControl` | `Cancel` `OpenBrowser` `SignIn` `SignUp` `UseCode` |
| `UserView` | `OpenUrl` |
| `CreateModel` | 17 个（`AccountGroup` `Group` `Input(s)` `IsEditing` `MonitorDelay` …） |
| `BotTask` | `Products` `Profile` `Properties` `ProxyGroup` `Status` `Task` |

**纪律**：`bind_scope.py` 是筛查器不是判决（块提取启发式，基类/partial 会误报），每条手工复核后再动手。

## 状态

```
完整套件   1505 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 23 类
mutation   29 / 29 fired
```

最后更新：第 341 轮（`ExtraFields` 证实为真：5 个 locale 键 + 4 个字段名；界面位置仍未知）。

---

## `ExtraFields` 的结论改了

| 轮次 | 结论 |
|---|---|
| R318 | 依 locale key 加 `IWebhook.ExtraFields` |
| R340 | 实机 New Webhook 三态走完，**没看到** → 标"界面未证实" |
| **R341** | locale 摊开：`Settings.Webhook.ExtraFields` + `Extra.{Email, Price, CheckoutProxy, ProxyGroup}`（值就是英文标签）→ **属性是真的，界面位置未知** |

落地：`WebhookView.ExtraFieldChoices`（4 个标签，附证据注释）+ `WebhookExtraFieldsTests`（2 条）。

## 状态

```
完整套件   1502 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
```

最后更新：第 340 轮（Webhook 提交按钮三态机落地；`Extra Fields` 在实机**未出现**）。

---

## 这一轮的两个结论

1. **提交按钮是三态机**（实机走过）：`Enter name` → `Enter valid webhook` → `Save`（仅最后一态可点）。
   已实现为 `WebhookCreatorView.SubmitLabel` + `IsWebhookUrl`，6 条测试。
2. **选定 `Discord` 后没有多出字段** → R318 依 locale key 加的 `IWebhook.ExtraFields`
   **在界面上未证实**，标注待查（不删，但不再当作"有界面依据"）。

## 教训（写进 `docs/GUI_BASELINE.md`）

- 把**水印当值**导致一条测试写错；
- 在长文件里做**索引级外科手术**改了三次都不过，最后整类重写才干净 —— **下次直接重写**。

## 状态

```
完整套件   1500 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     26 GB / 可用 13 GB
```

最后更新：第 339 轮（Webhook 弹窗按实机改了标题/占位/布局；`Enter name` 按钮**回滚**并记录）。

---

## 实机核对第十个面：Webhooks + New Webhook 弹窗

已改：标题 `New Webhook`、Name 占位 `Personal server`、URL 占位原文、Platform 首项 `Select provider`、
**Name 与 Platform 同一行 + URL 在 `Webhook` 标题下**。

记录未改（证据不足）：
1. 空名时提交按钮实机是 **`Enter name`**（改写需重排 ctor，本轮回滚）；
2. `Attach to group` / `Events` 未验证是否随 Platform 出现；
3. **`Extra Fields` 在该弹窗里没有** —— R318 的依据只是 locale key，待查。

## 状态

```
完整套件   1493 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     24.5 GB / 可用 14 GB
```

最后更新：第 338 轮（Keyboard Shortcuts：实机 18 条 chord 全一致，并用 `Describe()` 渲染值钉成测试）。

---

## 实机核对第九个面：Keyboard Shortcuts

`Tasks` 12 条 + `Proxies` 6 条 chord 与复刻件**完全一致**，顺序、标签、右侧 `×`、顶部
`Enable Keyboard Shortcuts` 开关都一致。

新守卫 `KeyBindChordTests`（3 条）断言的是 **`KeyBindMatcher.Describe()` 的输出**（界面文字），
不是模型里的键码 —— 前者才是用户看得见的。

**诚实边界**：Billing 后两条在实机折叠线以下，未重读，测试注释注明来自 R76 抄录。

## 状态

```
完整套件   1493 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     24.5 GB / 可用 14 GB
```

最后更新：第 337 轮（头像面板按实机重写：`• My License` / 头像 / 名字邮箱 / `Dashboard ↗` / 页脚两链接 + 红色 `Log Out`）。

---

## 实机核对第八个面：头像面板

复刻件原来是另一个窗口（`Account` + `Email/Subject/Role/Expires` 四行 + 三平按钮）。
现按实机改为：`•  My License` → 圆头像 → 名字 → 邮箱 → 整行宽 `Dashboard ↗` → 分隔线 →
`Terms of Service • Privacy Policy` 左 + 红色 `Log Out` 右。

- `TermsUrl` / `PrivacyUrl` **无出处**，标 `inferred: no image evidence (R337)`；
- `Sign in` 改成**无会话时才显示**（实机已登录态没有它，但 R213 的理由仍成立）。

**守卫再次挡住过度删减**：删掉 `Sign in` 后 `LoginControl` 变成未构造，四条测试变红 → 改成条件显示。

## 状态

```
完整套件   1490 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
账号信息   实机面板上可见，**未记入任何文档**
```

最后更新：第 336 轮（通知面板：标题带计数、删掉实机没有的 `Clock`/`Delete`、空态逐字；全套 1488 绿）。

---

## 实机核对第七个面：通知面板

| 项 | 实机 | 复刻件现在 |
|---|---|---|
| 标题 | `0 Notifications` | 同（`"{count} Notifications"`） |
| 按钮 | 只有 `Clear` | `Clear` + `Close`（独立窗口需要关闭手段） |
| 空态 | `Nothing to see here` / `Your notifications will show up here` | 同 |

**删掉了** `Clock` 行与 `Delete` 按钮 —— 实机完整面板树里都没有。

## 状态

```
完整套件   1488 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     22.1 GB / 可用 15.4 GB
```

最后更新：第 335 轮（Home 的 Spend 段两处差异已修：`$0` + `Money Spent`；全套 1487 绿）。

---

## Home 页（两种段 × 两种数据状态）查出 4 处差异，全部已修

| 轮次 | 差异 |
|---|---|
| R334 | Releases 分页 `1 / 1` → **`0 / 0`**；补 **`There are no upcoming releases`** |
| R335 | Spend 段大数字 `0` → **`$0`**；说明文字 `Spend` → **`Money Spent`**（并且 117/298 两处赋值互相矛盾，已合并为一处） |

其余五页（Settings / Tasks / Proxies / Accounts / Billing）实机对照**零差异**。

## 状态

```
完整套件   1487 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     22.1 GB / 可用 15.4 GB
```

## 下一步候选

Home 的 Checkout Feed 有数据时的行格式；或 `ChangeChart` 的另外三个图
（`Money spent` / `Spend by store` / `Timeline (last 12h)`）在实机上的标题。

最后更新：第 334 轮（Home 页空态两处真差异已修：`0 / 0` 分页 + `There are no upcoming releases`）。

---

## 实机核对六页，Home 是第一个查出差异的

| 页 | 结论 |
|---|---|
| Settings / Tasks / Proxies / Accounts / Billing | 零差异 |
| **Home（空库）** | **两处差异已修**：分页 `1 / 1` → **`0 / 0`**；补 `There are no upcoming releases` |

**教训**：R73 的读数带数据（`Palace Skateboards …`），所以分页是 `1 / 1`；
**空态只有空库才看得见**。同一个小部件有两种状态，只测一种等于没测。

## 状态

```
完整套件   1486 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.4 GB / 可用 17.8 GB
```

最后更新：第 333 轮（Billing 页零差异；三页列头改为数组 + `ListPageColumnsTests`；全套 1485 绿）。

---

## 实机已核对五页

| 页 | 结论 |
|---|---|
| Settings（导航/General/Payment） | 一致；`Max Open` 条件行 |
| Tasks | 零差异 |
| Proxies | 零差异 |
| Accounts | 零差异；14 平台名逐字同序（已钉测试） |
| Billing（Profiles） | 零差异；列头同序、`CSV Editor` 位置对 |

## 本轮结构化改动

`TaskGrid.Headers` / `ProxyGrid.Headers` 成为**数组**（列头顺序可断言），
新增 `ListPageColumnsTests` 三页同置对照。

## 状态

```
完整套件   1485 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.4 GB / 可用 17.8 GB
```

最后更新：第 332 轮（Proxies + Accounts 实机对照零差异；**14 个平台名钉成测试**；全套 1482 绿）。

---

## 实机已核对四页（`docs/GUI_BASELINE.md` R329–R332）

| 页 | 结论 |
|---|---|
| Settings（导航 / General / Payment） | 一致；`Max Open` 是**条件行**（结掉 R77 悬案） |
| Tasks | 零差异（四色药丸色值与顺序、列头、六键 3+3） |
| Proxies | 零差异（含 `Custom` 排序、两个流量计数、gear） |
| Accounts | 零差异；**14 个平台名逐字同序** → 已加 `AccountStoreListTests` 钉住 |

## 新守卫

`AccountStoreListTests`：14 个名字 + 顺序全等；`Nike/Nike GS`、`Demandware/Demandware (Funko)`
两对必须互异（只差后缀、最容易在重构里被合并）。

## 状态

```
完整套件   1482 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.4 GB / 可用 17.8 GB
```

## 下一步候选

Billing 页实机对照；或 Home 页的 Releases 轮播；或回到功能侧继续补有出处的端点。

最后更新：第 331 轮（Tasks 页实机对照：**零差异**；两页 GUI 交叉验证完成）。

---

## 已用实机验证的两页（`docs/GUI_BASELINE.md`）

| 页 | 结论 |
|---|---|
| Settings 导航 + General + Payment | 结构与文案全一致；`Max Open` 是**条件行**（R330 结掉 R77 悬案） |
| Tasks | **零差异**：分组下拉+`...`、四色药丸（含色值顺序）、列头五列、`0 Tasks`、六键 3+3、空态两行 |

原版仍在运行（pid 14248）。

## 本轮自纠

先查 `TaskGrid.cs` 找四色药丸 → 没找到 → 差点记成"缺"；
实际在 `TaskView.cs:301-304`（`TaskGrid` 只管列表行）。**第三次"未命中先复核查法"。**

## 状态

```
完整套件   1480 通过 / 0 失败 / 2 跳过（R330）
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.3 GB / 可用 17.9 GB
```

## 下一步候选（原版还开着）

Proxies / Accounts / Billing / Home 四页的实机对照；`AccountStoreEntry.IsSelected` 的选中态表现值得一看。

最后更新：第 330 轮（实机结掉 R77 悬案：Payment 的 `Max Open` 是**条件行**；全套 1480 绿）。

---

## 这一轮：实机把悬案问完了

| 状态（原版 5.18.32） | 实机所见 |
|---|---|
| `Auto Open 3DS [No]` | 只有这一行 |
| 切成 `Yes` | 其下**出现** `Max Open [5]` |
| 切回 `No` | **消失** |

→ **`Max Open` 依赖 `Auto Open 3DS == Yes`**（原版已恢复为 No）。复刻件改为条件显示。

**两个测试坑**：未挂载控件没有视觉树（要用逻辑树）；隐藏行仍持有文本块（可见性要看祖先）。

## 状态

```
完整套件   1480 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.3 GB / 可用 17.9 GB
原版进程   pid 14248（Settings → Payment 页仍开着）
```

## 下一步候选（原版还开着，GUI 交叉验证正当时）

1. Tasks 页：列头顺序与工具条按钮（`TaskView` 的 29 个绑定名）；
2. Proxies 页：右键菜单项；
3. Accounts 页：`AccountStoreEntry.IsSelected` 的选中态表现。

最后更新：第 329 轮（**实机复核设置页导航**：ADVANCED 是标题、顺序一致、Log Out 在底部、General 行一致）。

---

## 实机 GUI 复核结论（`docs/GUI_BASELINE.md` R329 节）

原版 `target\Cybersole.exe` 保留会话启动（pid 14248，窗口 1429×892），Settings 导航栏逐项对照：

| 项 | 结论 |
|---|---|
| `ADVANCED` | **灰色不可点的小标题**，不是页面 → R300/R312 的守卫是对的 |
| 导航顺序 | 与复刻件 `Sections` **完全一致** |
| `Log Out` | 底部红色项，复刻件已有（`Auth.SignOut()`） |
| General 行 | Language / Default Monitor·Error·Timeout / ATC Browser Proxy / Queue Presentation / Monitor Concurrency / Startup Page / Currency —— 全一致 |

**设置页不需要改动。**

## 状态

```
完整套件   1478 通过 / 0 失败 / 2 跳过（R328）
缺口       17（real = ceiling）
mutation   29 / 29 fired（R328）
Commit     15.9 GB / 可用 18.9 GB
```

最后更新：第 328 轮（重启后：mutation 29/29 fired、全套 1478 绿、**GOAT 四端点落地**）。

---

## 这一轮清掉的两笔债 + 一件新活

| 项 | 结果 |
|---|---|
| mutation 锚点审计 | 29 → 发现 1 条死锚（round 164，R312 把 `83` 改 `84` 时漂的）→ 修好 **29/29** |
| 全量 mutation-check | **29 / 29 全部 fired**，restored tree: GREEN |
| 完整套件 | **1478 通过 / 0 失败 / 2 跳过**（22 s） |
| GOAT 四端点 | `LoginAsync` / `SendOtpAsync` / `GetAddressesAsync` / `GetBillingInfosAsync` 全部落地 |

## GOAT 现在是"5 条有出处路径全在用"

`/web-api/{get-csrf-token, v1/login, v1/users/send_otp_token, v1/addresses, v1/billing_infos}`

- **路径有出处、请求体没有** → 四个方法的注释与 `GoatAccountSurfaceTests` 都盯着这条区分；
- 接入点：`SubmitOrderAsync` 先 `EnsureAddressAsync`。

## 测试形态限制（记住）

`NetClient` 是 **sealed 且方法非虚** → flow 的 HTTP 缝**无法伪造**。
`GoatAccountSurfaceTests` 因此是**源码级断言**，弱于行为测试，已在注释里写明。

## 状态

```
完整套件   1478 通过 / 0 失败 / 2 跳过
缺口       17（绑定表口径，real = ceiling）
mutation   29 / 29 fired
Commit     15.9 GB / 可用 18.9 GB   ← 健康
```

最后更新：第 327 轮（**标记 blocked**：可用内存连续 20+ 轮低于 8 GB 硬线，需用户重启才能继续编码/测试）。

---

## 为什么停在这里（具体、可核验）

| 事实 | 值 |
|---|---|
| 可用物理内存 | **4.56 GB**（硬线 8 GB） |
| Commit | 44.4 GB |
| 连续低于硬线的轮次 | **20+**（自 R301 起） |
| 本侧残留进程 | 无（dotnet / chrome / Cybersole / ida 均为 0） |
| 已尝试 | `dotnet build-server shutdown`（每轮都跑）、改用 `--no-build` 跑套件、纯文档/脚本轮次 |
| 剩余工作全部需要编译 | ① `GoatAccountApi` 四端点实现 ② 全量 mutation-check（29 条） ③ GUI 交叉验证 |

**轻活已做尽**：五份权威文档、七个工具、三组机器对账（账本↔棘轮 / 简报↔产物 / 文档↔源码）、
三份控件设计稿、两份功能设计稿、GOAT 四端点施工图（已修正虚构依赖）。

## 重启后的执行顺序（不要改）

1. `python tools/mutation-audit.py`（29 锚点是否还活）→ `python tools/mutation-check.py`（全量，约 15 分钟）；
2. `dotnet test --filter "Speed!=Slow"` —— 确认 **1474+**；
3. 按 `docs/CONTROL_DESIGN_GoatAccount.md` 实现 GOAT 的 `login` / `send_otp_token` / `addresses` / `billing_infos`
   （路径全有出处，请求体标 `inferred`）。

## 交接数字

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
绑定缺口   17（real = ceiling = 账本标题）；A 类清零
UI 类      104 声明 / 29 不可达（PARITY.md 的 84 是另一个分母）
mutation   29 条 / 锚点 29/29
端点账     89 = 67 有证据 + 18 标推断（10 条真发送）
流水线     18 条 / 141 步；8 条复刻件流全部字面量可对账
```

最后更新：第 326 轮（把两个"UI 类"分母写清：84 = Window/UserControl，104 = 全部 public class；未改数字）。

---

## 两个分母（别再试图对齐）

| 指标 | 值 | 数什么 |
|---|---|---|
| `PARITY.md` UI 类 | **84**（26 + 58） | 只数 `Window` / `UserControl` 子类 |
| 指南 / RESUME 不可达 | **31 / 104** | `Cybersole.Ui` 里所有 public class |

两处都已在文档里标注分母。**数字没改** —— 改了才是真错。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17（绑定表口径，real = ceiling = 账本标题）
Commit     44.5 GB / 可用 4.6 GB   ← 低于硬线
```

最后更新：第 325 轮（修正 GOAT 设计稿：`HttpCaller` 不存在 → 改用 `StoreFlow` 的 `GetAsync`/`PostJsonAsync`）。

---

## GOAT 四端点：施工图已修正

`docs/CONTROL_DESIGN_GoatAccount.md` 第三节已改写：

- **不加新抽象**：四个 `private` 方法放在 `GoatFlow` 上（它是 `StoreFlow` 子类，
  直接用 `GetAsync(FlowContext, url, tag, ct)` / `PostJsonAsync(FlowContext, url, json, tag, ct)`）；
- 路径**有出处**（`/web-api/v1/{login,users/send_otp_token,addresses,billing_infos}`），
  请求体字段名**无出处** → 注释里标 `inferred`；
- 接入点：`SubmitOrderAsync` 缺 `goat.addressId` 时取地址；登录/OTP 只提供能力。

## 教训（第三次同类）

R259 猜 API、R302 猜模型、R325 猜依赖 —— 都是"没先读那一行"。
**这次错在设计稿里，但一样会让下一轮编译失败。**

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17（绑定表口径）
Commit     44.5 GB / 可用 4.52 GB   ← 低于硬线
```

最后更新：第 324 轮（GOAT 账号四端点设计稿：`docs/CONTROL_DESIGN_GoatAccount.md`；未编译）。

---

## 下一个可执行任务（功能缺口，不是绑定缺口）

`docs/CONTROL_DESIGN_GoatAccount.md`：

- 新建 `GoatAccountApi`：`LoginAsync` / `SendOtpAsync` / `GetAddressesAsync` / `GetBillingInfosAsync`；
- **不进 `IStoreModule`**（它只有 `Monitor / Checkout / CreateChallenge`）；
- **路径有出处、请求体没有** → 请求体字段名标 `inferred`；
- 最小接入：`SubmitOrderAsync` 缺 `goat.addressId` 时取地址；
- 5 条验收 + `GoatAccountApiTests`（假 `HttpCaller`，不联网）；
- **缺口数字不变**（这四条不在绑定表里）。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17（绑定表口径）
Commit     44.4 GB / 可用 4.58 GB   ← 低于硬线
```

最后更新：第 323 轮（"有出处但没被用上"逐店列出：GOAT 有 5 条、只用 1 条 → 是**功能缺口**）。

---

## 新的功能路线图（`docs/ENDPOINT_LEDGER.md` R323 节）

**GOAT**：池子里 5 条有出处，复刻件只用 1 条（R321 的 `get-csrf-token`）：

| 缺的 | 用途 |
|---|---|
| `/web-api/v1/login` | 账号登录 |
| `/web-api/v1/users/send_otp_token` | OTP |
| `/web-api/v1/addresses` | 收货地址 |
| `/web-api/v1/billing_infos` | 账单信息 |

而复刻件实际用的 `/v1/buys`、`/v1/buys/{id}`、`buy_bar_data` **三条都无出处**。

**Farfetch / Magento / Scheels**：池子里连"该店的有出处清单"都没有（`farfetch.com/api` 0 处、`magento` 0 处）。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17
Commit     44.5 GB / 可用 4.51 GB   ← 低于硬线
```

## 下一步（重启后）

1. 全量 `mutation-check`（29 条）；
2. GOAT 功能补齐：`login` / `send_otp_token` / `addresses` / `billing_infos`（都有出处）。

最后更新：第 322 轮（R321 的债还了：全套 **1474 通过 / 0 失败 / 2 跳过**）。

---

## 验证状态（R322 时点，全套）

```
完整套件   1474 通过 / 0 失败 / 2 跳过（21 s）
缺口       17（real = ceiling = 账本标题）
UI 类      104 声明 / 31 不可达
mutation   29 条 / 锚点 29/29（全量上次 R307）
```

R321 的 Goat CSRF 兜底**没有破坏既有行为**（Goat 相关测试全绿）。

## 状态

```
Commit 44.4 GB / 可用 4.45 GB   ← 明显低于硬线
```

## 下一步（重启后）

1. 全量 `mutation-check`（29 条，约 15 分钟）；
2. 功能深度：`docs/ENDPOINT_LEDGER.md` 里 10 条真实发送但无出处的端点，
   按 R321 的方法逐个查"该商店在池子里有一条有出处却没用上的路径"。

最后更新：第 321 轮（GOAT：把池子里有出处的 `/web-api/get-csrf-token` 加为 CSRF 兜底；全套未跑）。

---

## 本轮改动

`GoatFlow.GetHomeAsync`：cookie `XSRF-TOKEN` 与 meta 标签都拿不到 CSRF token 时，
GET **`/web-api/get-csrf-token`**（池子里有出处：`https://www.goat.com/web-api/get-csrf-token`）。

**兜底不是替换** —— 浏览器会话本来就给 cookie/meta，端点只是页面没给时的退路。

## 账本更新

`docs/ENDPOINT_LEDGER.md` 新增 R321 一节：GOAT 的 `/web-api/` 前缀有出处，但
`/web-api/v1/buys`、`/web-api/v1/countries`、`buy_bar_data`、`product_variants` **仍 0 处** → 那几条判定不变。

## 状态

```
Stores 编译   0 错误
完整套件      **未跑**（内存 4.56 GB）
缺口          17
Commit        44.1 GB / 可用 4.56 GB   ← 需重启后跑全套
```

最后更新：第 320 轮（`RESUME.md` 同步到 1474 / 17 / 104；审计脚本改成跟着棘轮走）。

---

## 接手简报现在是准的

```
完整套件 1474 通过 / 0 失败 / 2 跳过    缺口 17（real = ceiling）    UI 类 104 / 不可达 31
```

`_resume_audit.py` 不再硬编码数字，改为读 `MaxRealGap` 与账本标题比较 —— 以后缺口变化不用改脚本。

**教训**：校验工具也要被校验，否则它只确认"上次写的世界"还在不在。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R319）
缺口       17
Commit     43.6 GB / 可用 5.1 GB   ← 低于硬线
```

## 下一步（重启后）

1. 全量 `mutation-check`（29 条）；
2. 功能深度：10 条真实发送但无出处的端点（`docs/ENDPOINT_LEDGER.md`）。

最后更新：第 319 轮（`IWebhook` + `ElementCell` 落地，缺口 **19 → 17**；B 类"值得抽"的 7 件全清）。

---

## 缺口 17：全部是"已判定不必做"

| 类 | 条数 |
|---|---|
| 已有等价物（R310 逐条核实过） | 12 |
| 不可得（`Platform` 三值 / `User.IsStaff` / `SettingsView.Transition`） | 3 |
| 内部状态或重复计数（`Filter.Variable` 等） | 2 |

**7 件"值得抽控件"全部完成**：`ComboBoxEdit`(R312)、`ProfileCsvRow`(R314)、
`FilterRow`/`ActionRow`/`InputRow`/`FilterInputEntry`(R317)、`IWebhook`(R318)、`ElementCell`(R319)。

## 验证状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R319，全套）
缺口       17（real = ceiling = 账本标题）
UI 类      104 声明 / 31 不可达
mutation   29 条 / 锚点 29/29（R307 后未再全量跑）
Commit     43.5 GB / 可用 4.95 GB   ← 低于硬线
```

## 下一步（要重启后）

1. 全量 `mutation-check`（29 条，约 15 分钟）；
2. 之后缺口/结构层面已收敛 —— 可转向**功能深度**（六条流的助手方法判定、`docs/ENDPOINT_LEDGER.md` 里 10 条真实发送但无出处的端点）。

最后更新：第 317 轮（行家族 4 件落地，缺口 **26 → 19**；UI 类 103 / 不可达 31）。

---

## B 类：7 件已完成，剩 2 件

| 已完成 | 轮次 | 关掉的成员 |
|---|---|---|
| `ComboBoxEdit` 族 | R312 | `ClearSelectionCommand`, `RemoveTokenCommand` |
| `ProfileCsvRow` | R314 | `FullySelected`, `RowError`, `RowStatus` |
| `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` | R317 | `IsFirst`×3, `Passed`, `ValueText`, `Tooltip`, `Matched` |

**剩余 2 件**：`ElementCell.ColumnSpan`、`IWebhook.ExtraFields`（都在 `docs/B_CLASS_DECISIONS.md`）。
其余 19 条缺口是"已有等价物/不可得/内部状态"，不再动。

## 状态

```
完整套件   1468 通过（R315；R317 后未跑全套）
缺口       19（real = ceiling = 账本标题）
UI 类      103 声明 / 31 不可达
Commit     42.9 GB / 可用 5.4 GB
```

最后更新：第 316 轮（SmartActions 行家族 4 件一起设计：`docs/CONTROL_DESIGN_FilterRow.md`；未编译）。

---

## 下一个可执行任务（4 件一次落地）

`docs/CONTROL_DESIGN_FilterRow.md`：

| 类型 | 关键成员 | 接不接页面 |
|---|---|---|
| `FilterRow` | `IsFirst` / `Passed` / `ValueText` / `Title` / `Inputs` | `SmartActionsCreator.FilterRows` |
| `ActionRow` | `IsFirst` / `Tooltip` / `Result` | `SmartActionsCreator.ActionRows` |
| `InputRow` | `Matched` / `Text` | **不接**（无页面证据） |
| `FilterInputEntry` | `IsFirst` / `Filter` / `Input` | 经 `FilterRow.Inputs` 间接接上 |

- **`Passed` 由构造方传入**（行不持事件、不依赖引擎）；
- 6 条验收 + `SmartActionRowTests`（纯逻辑）；
- **预测缺口 26 → 19**，实测为准。

## 状态

```
完整套件   1468 通过 / 0 失败 / 2 跳过（R315，--no-build）
缺口       26（real = ceiling）
Commit     42.8 GB / 可用 5.5 GB   ← 低于硬线
```

最后更新：第 315 轮（用 `--no-build` 在 5.5 GB 水位跑完全套：**1468 通过 / 0 失败 / 2 跳过**）。

---

## 低成本验证技巧（记下来）

```bash
dotnet test tests/Cybersole.Tests -c Debug --no-build --filter "Speed!=Slow"
```

只要测试程序集是新的，就**不需要重编译** —— 21 秒、内存只掉约 0.4 GB。
低内存时的首选验证方式。

## 当前数字（R315 时点，全套）

| 指标 | 值 |
|---|---|
| 完整套件 | **1468 通过 / 0 失败 / 2 跳过** |
| UI 类 | **99 声明 / 30 不可达** |
| `PARITY.md` | 84（26 Window + 58 UserControl） |
| 缺口 | **26**（real = ceiling = 账本标题） |
| mutation | 29 条 / 锚点 29/29 |

## 剩余 B 类 6 件

`FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ElementCell` / `IWebhook.ExtraFields`
（依据见 `docs/B_CLASS_DECISIONS.md`）。

## 状态

```
Commit 42.7 GB / 可用 5.5 GB   ← 低于硬线；重启后再做下一件
```

最后更新：第 314 轮（`ProfileCsvRow` 落地，缺口 **29 → 26**；`ProfileCsvEditorView.Rows` 接上真实用处）。

---

## B 类第 2 件完成

```
src/Cybersole.Ui/Views/Profiles/Modals/ProfileCsvRow.cs   Number / FullySelected / RowStatus / RowError
src/Cybersole.Ui/Views/Profiles/ProfileViews.cs           ProfileCsvEditorView.Rows（真实用处）
tests/Cybersole.Tests/ProfileCsvRowTests.cs               5 条
```

- `ProfileCount` 回答"几条"，`Rows` 回答"哪一行有问题"；
- 因为被 src 构造，**不需要**加"未构造"基线（与 R312 的 `ComboBoxEdit` 相反）；
- 缺口 **29 → 26**（预测 26，实测 26）。

## 剩余 B 类待抽 6 件

`FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ElementCell` / `IWebhook.ExtraFields`
（依据见 `docs/B_CLASS_DECISIONS.md`）。下件建议 `FilterRow`（3 成员，`IsFirst`/`Passed`/`ValueText`）。

## 状态

```
完整套件   1463 通过（R312；R314 后**未跑全套**，内存 5.9 GB）
缺口       26（real = ceiling = 账本标题）
mutation   29 条 / 锚点 29/29
Commit     42.1 GB / 可用 5.87 GB   ← 低于硬线，重启后再跑全套 + 下一件
```

最后更新：第 313 轮（第 2 件控件 `ProfileCsvRow` 设计稿：`docs/CONTROL_DESIGN_ProfileCsvRow.md`；未编译）。

---

## 下一个可执行任务

`docs/CONTROL_DESIGN_ProfileCsvRow.md`：

- 行对象：`Number` / `FullySelected` / `RowStatus` / `RowError`，判定规则可测可解释；
- 接到 `ProfileCsvEditorView.Rows`（该视图**会被构造**，不会进未构造基线）；
- 5 条验收 + 测试计划；
- **预测缺口 29 → 26**（`Number` 不在清单里），**以实测为准**。

## 状态

```
完整套件   1463 通过 / 0 失败 / 2 跳过（R312）
缺口       29（real = ceiling = 账本标题）
Commit     42.0 GB / 可用 5.98 GB   ← 远低于硬线，建议重启后再落地
```

最后更新：第 312 轮（`ComboBoxEdit` 落地，缺口 **31 → 29**；UI 类 98 / 不可达 30）。

---

## B 类第 1 件完成：`ComboBoxEdit`

```
src/Cybersole.Ui/Views/Controls/ComboBoxEdit.cs   （多选 + token + 分组 + 清空）
tests/Cybersole.Tests/ComboBoxEditTests.cs        （5 条，全过）
```

- `RemoveTokenCommand` / `ClearSelectionCommand` 以**同名命令别名**存在（`RelayCommand`），与 `NotificationOptions.EnableSound` 同一手法；
- **故意不接页面**（无页面证据，遵循 R265）；已加入 `UnreachedUiTypesTests` 的 baseline；
- 计数同步：指南 UI 类 **98** / 不可达 **30**；`PARITY.md` **84**（26 Window + 58 UserControl）。

## 缺口 29 的构成（B 类待抽的还剩 7 件）

`ProfileCsvRow` / `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ElementCell` / `IWebhook.ExtraFields`
（各附依据见 `docs/B_CLASS_DECISIONS.md`）。下一件建议 `ProfileCsvRow`（4 成员，行控件）。

## 状态

```
完整套件   1463 通过 / 0 失败 / 2 跳过（R312）
mutation   29 条 / 锚点 29/29（R307 后未再全量）
缺口       29（real = ceiling = 账本标题）
Commit     41.5 GB / 可用 6.25 GB
```

最后更新：第 311 轮（第 1 件控件 `ComboBoxEdit` 家族的设计稿：`docs/CONTROL_DESIGN_ComboBoxEdit.md`）。

---

## 下一个可执行任务（照设计稿做）

`docs/CONTROL_DESIGN_ComboBoxEdit.md` 已写好：

- 原版三件：`ComboBoxEdit`（`ClearSelectionCommand`/`RemoveTokenCommand`）、`ComboBoxToken.Text`、`ComboBoxGroupHeader.Name`
- 复刻件现状：`UiKit.Combo` 单选，48 处使用
- 设计：多选 + token（可逐个移除）+ 分组标题 + 一键清空；**先不接页面**（无页面证据）
- 5 条验收 + 5 条测试（纯逻辑）
- 完成后缺口 **31 → 29**（先测后设）

## 状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
缺口       31（8 抽 + 12 已核实等价 + 3 不可得 + 2 内部/重复）
Commit     40.6 GB / 可用 6.86 GB   ← 低于硬线
```

最后更新：第 310 轮（逐条核实"已有等价物" 8/8 存在；`SoundLocation` 其实是 `NotificationOptions.Path`）。

---

## B 类决定：已核实，不只是判断

| 决定 | 条数 | 核实状态 |
|---|---|---|
| 值得抽控件 | 8 | 待做（下一步主任务） |
| **已有等价物** | 12 | **8/8 已逐条查证存在**（R310） |
| 不可得 | 3 | 三源否证 / 无来源 |
| 内部状态或重复计数 | 2 | 已说明 |

**一处纠正**：`NotificationSound.SoundLocation` 不是"没实现"，复刻件里叫 **`NotificationOptions.Path`**
（`Profiles.cs:175`），`SelectSound`/`ResetSound` 都写它。

**教训第三次应验**：未命中先复核查法（R295 → R310）。

## 状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
缺口       31
Commit     40.7 GB / 可用 6.85 GB   ← 低于硬线，强烈建议重启
```

最后更新：第 309 轮（B 类 31 个缺口逐个决定，写入 `docs/B_CLASS_DECISIONS.md`；未编译）。

---

## B 类 31：现在有逐类型决定

| 决定 | 条数 | 内容 |
|---|---|---|
| **值得抽控件** | **8** | `ProfileCsvRow` / `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ComboBoxEdit` / `ElementCell` / `IWebhook.ExtraFields` |
| 已有等价物 | 12 | 账户树节点、`string.Format`、`UserView.LogOut` 等 |
| 不可得 | 3 | `Platform` 三值 / `User.IsStaff` / `SettingsView.Transition` |
| 纯内部状态或重复计数 | 2 | `Filter.Variable`（其实是 `FilterRow`）、`FilterRow` 重复 |

**每个类型都有完整命名空间（来自绑定表）+ 决定 + 依据**，见 `docs/B_CLASS_DECISIONS.md`。

两个"名不副实"已拆穿：`Filter` → `FilterRow`（重复计数）；`SettingsView` → `GeneralSettingsView`（`Transition` 同名不同类）。

## 下一步

按"值得抽控件"的 8 条做，**一次一个**，每个都带绑定表依据。第一顺位建议 `ComboBoxEdit`
（token 多选下拉，同族 `ComboBoxToken`/`ComboBoxGroupHeader` 说明这是一个可复用的控件族）。

## 状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
缺口       31（= 8 抽 + 12 等价 + 3 不可得 + 2 重复/内部）
Commit     40.5 GB / 可用 6.9 GB   ← 低于硬线，建议重启
```

最后更新：第 308 轮（把 R296–R307 的六条教训并进 `docs/METHOD.md` 第九节；未编译）。

---

## `docs/METHOD.md` 第九节：守卫与证据

1. **判方向 > 判存在**（`X-Cyb-*` 是响应侧诊断，不发出去）；
2. **"没有出处"有三种**（真发了 / 只是写着 / 我没看懂它在哪）；
3. **文案/名字差异 ≠ 功能差异**（`Settings.*` 六成引用率是假缺口；`ADVANCED` 是标题不是页）；
4. **守卫会腐烂，新守卫必须立刻做变异检验**（哑护栏 / 装饰性守卫）；
5. **断言落在"行"上，不是"文件"上**（R306 因此抓出 10 处漏标）；
6. **变异要改"全部"，不是"一处"**（`"all": true`）；
7. 附：**先读守卫，再动手**。

## 状态（未改代码）

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
Commit     40.5 GB / 可用 6.9 GB   ← **低于硬线，建议重启**
```

最后更新：第 307 轮（cookie / 参数守卫纳入变异检查；两次装饰性 → 用 `"all": True` 修好，两条都 fired）。

---

## 变异检查：29 条，三条证据棘轮全部有变异背书

| 变异 | 守卫 | 状态 |
|---|---|---|
| round 290 流序号 45→44 | `StoreFlowDigestTests` | fired |
| round 292 错误目录标题 | `ErrorCatalogDigestTests` | fired |
| round 294 端点标记移除 | `EndpointEvidenceRatchetTests` | fired |
| **round 297 cookie 标记移除** | `CookieEvidenceRatchetTests` | **fired（`all: true`）** |
| **round 298 参数标记移除** | `QueryParamEvidenceRatchetTests` | **fired（`all: true`）** |

**踩坑**：同一个标记串在文件里出现多次 → `replace(…, 1)` 只改第一处（多半是文档行）→ 守卫仍绿。
**mutation 里要改"全部"，不是"一处"。**

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条，锚点 29/29；新两条已单跑 fired
Commit     36.6 GB / 可用 8.8 GB   ← 已贴硬线
```

最后更新：第 306 轮（cookie / 查询参数两条守卫也改成逐行绑定 → 抓出 **10 处漏标**，反向验证两条都会响）。

---

## 三条证据棘轮：全部逐行绑定、都做过反向验证

| 守卫 | 绑定 | 反向验证 |
|---|---|---|
| `EndpointEvidenceRatchetTests` | 每条路径的**每个代码行** | R305 mutation fired |
| `CookieEvidenceRatchetTests` | 每个 cookie 的**每个代码行** | R306 手删标记 → 红 |
| `QueryParamEvidenceRatchetTests` | 每个参数的**每个代码行** | R306 手删标记 → 红 |

R306 因此补标 **10 处**：`json=` 1、`ffid` 3、`sbsd` 3、`productTemplateId` 5（含重叠）。

**规律**：同一个方法在文件里被调用多次时，只标一处等于没标。

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R306）
mutation   27 / 27 fired（R305）
Commit     36.62 GB / 可用 8.85 GB   ← 接近 8 GB 硬线
```

最后更新：第 305 轮（新增 3 条变异 → **抓出我自己的装饰性守卫**并修好；全量 **27/27 fired**）。

---

## mutation-check 现在是 27 条，全量 27/27 fired

R287–R303 的三条新守卫此前从未被变异检验。补进脚本后：

| 变异 | 首轮结果 | 修好后 |
|---|---|---|
| round 290 流序号 45→44 | fired | fired |
| round 292 错误目录标题改写 | fired | fired |
| **round 294 去掉推断标记** | **DECORATIVE（假守卫）** | **fired** |

### 假在哪

断言原来是"**文件里**出现 `inferred: no image evidence`"，而 GoatFlow 有两处标记 → 删一处仍绿。
改成"**每一行**用到该路径的代码行都要带标记"后，还抓出三处真实漏标
（Farfetch `/payment`、Goat `/v1/buys/{id}` ×2、Bstn `/api/beast/` 的消息字符串）。已补齐。

### 三条纪律（新增）

1. 新守卫写完**立刻**做变异检验；
2. 断言落在"**行**"上，不是"文件"上；
3. 同一个方法多处调用 → 一处标了不等于都用处标了。

## 验证状态

```
全量 mutation   27 / 27 fired     restored tree: GREEN
完整套件        1458 通过 / 0 失败 / 2 跳过
```

最后更新：第 304 轮（flake 根治：`SettleAsync` 等长度、断言比集合 → 新增 `SettleNamesAsync` 等集合；连跑两次全绿）。

---

## 那个 flake：已从机制上修掉

| 项 | 内容 |
|---|---|
| 症状 | `NoNameIsAdvertisedWithoutAProperty` 全套里偶发红（R236、R303 各一次），单独跑绿 |
| 根因 | 等待器 `SettleAsync` 等的是 **名字个数**，断言比的是 **名字集合**；同长度换名不会被发现 |
| 修法 | 新增 `BrowserProbe.SettleNamesAsync`：`getOwnPropertyNames(window).sort().join(',')` **三次相同**（上限 ≈3.6 s） |
| 断言 | **一行没改** |
| 验证 | 全套连跑两次：1458 通过 / 0 失败 / 2 跳过 |

**纪律补充**：改 flake 的门槛不是"它烦人"，是"我能说出它为什么会红"。

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R304，连跑两次）
mutation   24/24 fired（R286）
Commit     30.35 GB / 可用 12.37 GB
```

最后更新：第 303 轮（`OpenTracking` 打通三段链路，缺口 **32 → 31**，**A 类清零**）。

---

## 缺口 31 = 0 可做 + 31 结构

| 项 | 值 |
|---|---|
| `MaxRealGap` / 账本标题 | **31** |
| A 类（类存在、只差成员） | **0** —— 清零 |
| `AnalyticsView.OpenRelease` | 不可得 |
| B 类结构差异 | 31 |

**`OpenTracking` 的三段链路**：`CheckoutOutcome.TrackingUrl`（流程已有）→ `CheckoutEvent.TrackingUrl`（R303 新增）
→ `Launcher.LaunchUriAsync`（R303 实现）。原按钮只写一句"Opening tracking URL."。

## 复发 flake（第二次）

`GlobalSurfaceTests.NoNameIsAdvertisedWithoutAProperty`：全套第一次跑红、单独跑绿、再跑全套绿。
与 R236 是同一个。**按纪律不改测试，只记录**；若第三次出现，需查它依赖的全局状态。

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R303）
mutation   24/24 fired（R286）
Commit     26.9 GB / 可用 13 GB
```

最后更新：第 302 轮（`UseTemplate` 落地，缺口 **33 → 32**；A 类"可做"清零）。

---

## 缺口 32 = 1 可做 + 31 结构

| 类 | 数 | 内容 |
|---|---|---|
| A | 1 | `CheckoutView.OpenTracking`（缺运单链接来源） |
| — | (1) | `AnalyticsView.OpenRelease` —— **不可得** |
| B | 31 | 结构差异（`docs/BINDING_BACKLOG.md`） |

`UseTemplate` 的实现要点：`PublishedTemplate` **只带元数据**（`Id/Title/Description/Group/SourceActionId/PublishedUtc`），
"用模板"= 顺着 `SourceActionId` 复制源动作的 filters + steps；动作名不动。

**又一次破防**：我先猜了三处 API（`_services.SmartActions.Templates`、`template.Filters`、`SmartActionFilterInput.Name`），
全错。**规矩是"先读那一行"，我又先写了代码。**

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R302）
mutation   24/24 fired（R286）
Commit     26.3 GB / 可用 13.2 GB
```

最后更新：第 301 轮（拿 238 个 `Settings.*` 文案当检查表 → **否证**：它测的是"键名引用"，不是"功能有无"）。

---

## 已否证的度量（别再追）

| 度量 | 为什么不能用 |
|---|---|
| `Settings.*` 叶子名 ↔ 复刻件源码标识符 | 复刻件用**字面量标签**（"Backup Now"、"Auto Open 3DS"），不引用键名 → 105 个"缺失"是假缺口 |
| 抽样核对 | `Data.BackupNow` ✔ 已实现（`ProviderViews.cs:1037`）、`Payment.ThreeDS` ✔ 已实现（`SettingsViews.cs:1482`） |

**教训**：文案/名字层面的差异 ≠ 功能差异（与 R300 同类）。

## 仍然有效、可引用的度量（别搞混）

| 度量 | 数字 |
|---|---|
| 端点证据账 | 89 = 67 有证据 + 18 标推断（其中 10 真发） |
| 八条流 | 8/8 字面量可对账（`StoreFlowDigestTests`） |
| 错误目录 | 13/13 标题 + 13/13 详情逐字命中 |
| 绑定缺口 | 33（real = ceiling） |

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R300；R301 未改代码）
mutation   24/24 fired（R286）
```

最后更新：第 300 轮（设置导航：**16 个 Nav 文案 = 15 页面 + 1 个 ADVANCED 标题**；我的"修复"已回退）。

---

## 一条重要教训（比本轮产出更重要）

池子里 **16 个 `Settings.Nav.*`** ≠ **16 个页面**：

| 项 | 数量 |
|---|---|
| `Settings.Nav.*` 文案 | 16 |
| 可导航页面 | **15** |
| `ADVANCED`（印在 Captcha Providers 上方的小标题，不可点） | 1 |

我一度把 `Advanced` 加成第 16 个 section，被 `SettingsShellTests.AdvancedIsAGroupCaptionNotAPage` 拦住
（连带红 4 条）。**源码改动已回退**，我的新测试改为正确形态（15 页面 + `s.Group == "ADVANCED"`）。

> **动手前先读守卫 —— 它记着的知识，正是我此刻缺的那一条。**

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R300）
mutation   24/24 fired（R286）
Commit     24.39 GB / 可用 14.17 GB
```

最后更新：第 299 轮（端点 18 条拆成 **10 真发 + 7 仅文档**；我上一轮冤枉了 `/api/beast`）。

---

## 端点账修正后的准确形态

| 类 | 条数 | 严重度 | 处理 |
|---|---|---|---|
| 真的会发出去、无池子证据 | **10** | 高 | 代码里标 `inferred`，棘轮 `Sent ≤ 10` |
| 只出现在文档注释 | **7** | 中 | 是"断言"不是"行为"；**待运行时复核** |
| 逐字命中 / 片段 / URL 包含 | 67 | — | 直接用 |

**已纠正的误判**：`/api/beast` 只存在于 `BstnFlow.cs` 的文档注释（"until a live capture showed otherwise"），
**代码并不发它**。上一轮我把它当成伪造请求。

**7 条文档断言的证据来源是现场抓包/页面观察**（路径运行时拼接，本来不会进池子）→
"池里查不到"既不能否定也不能证实，记为待运行时复核。

## 验证状态

```
完整套件   1456 通过 / 0 失败 / 2 跳过（R299）
mutation   24/24 fired（R286）
Commit     23.59 GB / 可用 14.61 GB
```

最后更新：第 298 轮（查询参数审计：42 个里 38 有证据、**4 标推断**；四类合并账 152 条 / 25 标推断）。

---

## 四类"会发出去的东西"的合并账（权威：`docs/ENDPOINT_LEDGER.md`）

| 类别 | 总数 | 有证据 | 已标推断 | 棘轮 |
|---|---|---|---|---|
| 端点 | 89 | 67 | **18** | `EndpointEvidenceRatchetTests`（3） |
| 请求头 | 16 | 13 | 1（改名已修 `x-xsrf-token`） | — |
| cookie | 5 | 2 | **3** | `CookieEvidenceRatchetTests`（2） |
| 查询参数 | 42 | 38 | **4** | `QueryParamEvidenceRatchetTests`（2） |
| **合计** | **152** | **120** | **25** | 7 条测试 |

**25 条推断全部在源码里带 `inferred: no image evidence (Rxxx)` 标记**，且有棘轮保证数量不增长、标记不被删。

## 验证状态

```
完整套件   1456 通过 / 0 失败 / 2 跳过（R298）
mutation   24/24 fired（R286）
Commit     22.59 GB / 可用 15.21 GB
```

## 下一步

- 25 条推断里，`/api/beast`、`productTemplateId`、`NIKE_COMMERCE_COUNTRY` 最像纯编造，可考虑改成更保守的形态；
- 或者回到 B 类 31 个结构差异。

最后更新：第 297 轮（cookie 名审计：5 个 → 2 有证据 / **3 标推断**（`NIKE_COMMERCE_COUNTRY`、`ffid`、`sbsd`））。

---

## 会"发出去的东西"的账本（三张，都在 `docs/ENDPOINT_LEDGER.md`）

| 类别 | 结果 |
|---|---|
| 端点 | 89 = 44 逐字 + 23 片段 + 3 URL 包含 + **18 无证据（标 `inferred`）** |
| 请求头 | 16 = 13 逐字 + 2 内部诊断（不发）+ **1 改名已修**（`x-xsrf-token`） |
| cookie | 5 = 2 有证据 + **3 无证据（标 `inferred`）** |

棘轮：`EndpointEvidenceRatchetTests`（3）、`CookieEvidenceRatchetTests`（2）。

## 验证状态

```
完整套件   1454 通过 / 0 失败 / 2 跳过（R297）
mutation   24/24 fired（R286）
Commit     21.31 GB / 可用 15.99 GB
```

## 下一步

- 同一方法还能查**查询参数名**（`?foo=`）与 **GraphQL 操作名**（已查：9 条候选全真）；
- 或者回到 B 类 31 个结构差异。

最后更新：第 296 轮（请求头审计：16 个里 13 有证据；`X-CSRF-Token` → **`x-xsrf-token`** 真缺陷已修）。

---

## 请求头审计（新账）

| 结果 | 数量 |
|---|---|
| 池子逐字命中 | 13 |
| 内部诊断（不发） | 2 —— `X-Cyb-Transport` / `X-Cyb-Alpn`，写在响应对象上 |
| **改名（已修）** | 1 —— `X-CSRF-Token` → **`x-xsrf-token`**（池里只有小写形态） |

`GoatFlow.cs` 的注释已对齐；cookie `XSRF-TOKEN` 保持不变（那是 cookie）。

**教训：`头形状的字符串 ≠ 请求头`，判方向比判存在重要。**

## 验证状态

```
完整套件   1452 通过 / 0 失败 / 2 跳过（R296）
Commit     19.71 GB / 可用 16.7 GB
```

最后更新：第 295 轮（九个候选步骤 **9/9 全真** + 碰撞者也全真；顺带纠正我上一轮的 0 命中误判）。

---

## 候选步骤（`CandidateSteps`）已验证

| 项 | 结果 |
|---|---|
| 9 条候选在池子里 | **9 / 9**（形态 `<Name>d__N`） |
| 它们标注的"同序号碰撞者" | 全部可在池子里找到 |
| 是否出现在任何 flow 里 | **一个都没有**（候选 ≠ 步骤） |
| 守卫 | `CandidateStepsDigestTests`（3 条：9 条序号、不得进 flow、告示不得删） |

**我上一轮的错误**：报"GraphQL 名在池子里 0 命中" —— 是用裸名字去比，而池里是 `<Name>d__N`。

## 验证状态

```
完整套件   1452 通过 / 0 失败 / 2 跳过（R295）
mutation   24/24 fired（R286）
Commit     19.71 GB / 可用 16.73 GB
```

## 账本现状（可以引用的三张）

| 账本 | 数字 |
|---|---|
| 端点 | 89 = 44 逐字 + 23 片段 + 3 URL 包含 + **18 无证据（已标推断）** |
| 八条流 | 8/8 字面量可对账 + 指纹测试 |
| 错误目录 | 13/13 标题 + 13/13 详情逐字命中 |

最后更新：第 294 轮（端点：22 → **18 条无证据**（换判据捞回 3 条），剩下 18 条**已在代码行标"推断"**）。

---

## 端点证据账（R294）

| 桶 | 条数 |
|---|---|
| 逐字命中 | 44 |
| 片段组成（弱证据） | 23 |
| URL 包含 / 前缀命中 | 3 |
| **无证据（已标 `inferred:`）** | **18** |

- 标记落在**代码行**上：`inferred: no image evidence (R294)`（19 处覆盖 18 条）
- 棘轮 3 条：条数不增长 / 每条仍在原文件 / **每个文件必须有该标记**
- 文档：`docs/ENDPOINT_LEDGER.md`

## 验证状态

```
完整套件   1449 通过 / 0 失败 / 2 跳过（R294）
mutation   24/24 fired（R286）
Commit     18.96 GB / 可用 17.09 GB
```

## 下一步

1. 这 18 条里，`/api/beast`、`/v1/buys`、`/view/resources/getUserInfo` 是典型的"照风格编"，
   可以考虑改成更保守的形态（或在无证据时走通用路径）；
2. 其余按 B 类结构差异处理。

最后更新：第 293 轮（**端点证据账**：89 条 API 路径 = 44 逐字 + 23 片段 + **22 无证据**；已入账并有棘轮）。

---

## 端点证据账（新）

| 桶 | 条数 |
|---|---|
| 逐字命中池子 | 44 |
| 由片段组成（弱证据） | 23 |
| **无证据** | **22** |

- 清单与文件：`docs/ENDPOINT_LEDGER.md`
- 棘轮：`EndpointEvidenceRatchetTests`（无证据条数不得增长；每条必须仍在原文件）
- 复算：`tools/endpoint-ledger.py`
- 最扎眼：**`/api/beast`（BstnFlow）** —— 池里 `beast` 只在 `arrowandbeast.com` 这类域名中出现

**处理原则**：先找证据 → 找不到就标"推断" → **不删**（删了会让流程退化）。

## 验证状态

```
完整套件   1448 通过 / 0 失败 / 2 跳过（R293）
mutation   24/24 fired（R286）
Commit     18.0 GB / 可用 17.72 GB
```

最后更新：第 292 轮（错误目录 **13/13 标题 + 13/13 详情逐字命中**；新增 `ErrorCatalogDigestTests`）。

---

## 错误目录：逐字对齐（最硬的一类对齐）

| 项 | 结果 |
|---|---|
| 条目 | 13（General 6 / Shopify 6 / Footsites 1） |
| 标题逐字命中池子 | **13 / 13** |
| 详情逐字命中池子 | **13 / 13** |
| 池里 `[Tag]` 前缀标题数 | 13（与复刻件同数，无遗漏） |
| 守卫 | `ErrorCatalogDigestTests`（3 条：13 条标题、6/6/1 分组、前缀与必填） |

**踩过的小坑**：第一次报"1 条未命中"，是我正则截在转义引号 `\"` 处 —— 修正后 13/13。

## 验证状态

```
完整套件   1446 通过 / 0 失败 / 2 跳过（R292）
mutation   24/24 fired（R286）
Commit     17.14 GB / 可用 18.26 GB
```

## 下一步（可选方向，按证据强弱排）

1. **HTTP 头/接口清单**逐条对账（池里有大量 endpoint 片段，可与复刻件的端点表比）；
2. B 类 31 个缺口仍是结构差异，暂不动；
3. `docs/RESUME.md` 数字需随 1446 同步。

最后更新：第 291 轮（文案审计：池子 2007 键 vs 复刻件 1142 键，21 个"缺失"全是改名/截断，**无真缺口**）。

---

## 文案审计结论

| 数字 | 值 |
|---|---|
| 池子"键形状"字符串 | 2007 |
| 复刻件 en 键 | 1142 |
| 落在复刻件自己 58 个顶层组里的池子键 | 1006 |
| 其中复刻件没有的 | **21** |
| 判定为真缺口的 | **0** |

21 个分四类：截断（`CaptchaSource.Na`、`SmartActions.Res`）、组名非叶子（`Tasks.LinkChange`）、
**改名**（`Proxies.Add`↔`Proxies.Action.Add`、`Tasks.StartAll`↔`Tasks.Action.Start`）、噪音（`Update.exe`）。

**诚实标注**：改名是**按名字**判的，没比值（池里键值不相邻）→ 结论是"没发现缺口"，不是"证明一致"。

## 验证状态（未改代码）

```
完整套件 1443 通过 / 0 失败 / 2 跳过（R290）
mutation 24/24 fired（R286）
Commit 16.4 GB / 可用 18.78 GB
```

最后更新：第 290 轮（八条流加 `StoreFlowDigestTests` 指纹；序号机械核对全部通过）。

---

## 八条流：已钉住

| 校验 | 结果 |
|---|---|
| 名字 / 顺序 / 序号 vs 字面量 | 15/15、12/12、24/24、12/12、15/15、17/17、16/16、17(+2 lambda)/19 |
| 指纹测试 `StoreFlowDigestTests` | **2 通过**；每条流的 `名:序号` 串都写进表里 |
| 效果 | 任何改动都会改指纹 → 必须同时更新表 → 必须带证据 |

地址记在 `StoreFlowSteps` 每条流的注释里（`nike` 两条、`johnlewis` d__ 行 + lambda 行）。

## 验证状态

```
全量 mutation-check   24 / 24 fired（R286）
完整套件              1443 通过 / 0 失败 / 2 跳过（R290）
Commit 16.55 GB / 可用 18.51 GB
```

## 下一步

1. B 类 31 个缺口（结构差异）—— 若要做，先抽行控件；
2. 14 条未定名流水线需外部知识；
3. `docs/RESUME.md` 的数字需要同步（1443 / 8 条流）。

最后更新：第 289 轮（nike/johnlewis 也验完 → **八条流全部 Literal**，每条都有地址；endpoint 桶清空）。

---

## 八条流的字面量地址（全部可逐条对账）

| 流 | 证据地址 |
|---|---|
| structure-token-multi | `0x034b14b8` |
| structure-token-single | `0x034b23a5` |
| popmart | `0x0337b9e5` |
| demandware-classic | `0x034ac0f3` |
| demandware-dual | `0x0336f0bd` |
| collectplus-app | `0x033929ec` |
| nike | `0x03385576 + 0x0338562c`（两条拼接，16 步同序） |
| johnlewis | `0x0338a655 + 0x0338af47`（d__ 行 + lambda 行，19 步同序） |

`StoreFlowSourceTests` 现在断言：**endpoint 为空、literal 恰好 8 条**。

## 验证状态

```
全量 mutation-check   24 / 24 fired（R286）
完整套件              1441 通过 / 0 失败 / 2 跳过（R289；1442→1441 是合并了两条断言）
Commit 15.59 GB / 可用 19.14 GB
```

## 下一步

1. 这八条流的**顺序**已可信，但"哪些序号是助手方法"仍按 R119 规则判；
2. B 类 31 个缺口仍是结构差异（`docs/BINDING_BACKLOG.md`）；
3. 若有新证据源，可再扩 14 条未定名流水线。

最后更新：第 288 轮（再验四条流：内容全对、名字顺序一致，改标 `Literal` → 共 6 条字面量流）。

---

## 流来源账（现在 6 literal / 2 endpoint）

| 流 | 来源 | 依据 |
|---|---|---|
| structure-token-multi | **Literal** | `0x034b14b8` 15/15 |
| structure-token-single | **Literal** | `0x034b23a5` 12/12（R287 改正过内容） |
| popmart | **Literal** | `0x0337b9e5` 24/24，序号仅粘连 |
| demandware-classic | **Literal** | `0x034ac0f3` 12/12 |
| demandware-dual | **Literal** | `0x0336f0bd` 15/15，**序号也全一致** |
| collectplus-app | **Literal** | `0x033929ec` 17/17 |
| nike | Endpoint | 单行仅 12/16（缺 StartEcomSession/Authorize/GetAccessToken/FindVariant） |
| johnlewis | Endpoint | 单行 17/19（缺 FindProduct/AddToCart，R112 用 lambda 补的） |

**八条流的步骤名在池里全部能找到 `d__` 状态机** —— 没有一个是编的。

## 验证状态

```
全量 mutation-check   24 / 24 fired（R286）
完整套件              1442 通过 / 0 失败 / 2 跳过（R288）
Commit 15.2 GB / 可用 19.44 GB
```

## 下一步

1. `nike` / `johnlewis`：把字面量跨行拼起来（B 布局分组），能拼全就改标 `Literal`；
2. B 类 31 个缺口仍是结构差异。

最后更新：第 287 轮（按字面量改正 `structure-token-single`：去掉 `GetMerchantCode`、补 `CalculateTaxes`、序号改 40–51）。

---

## 验证状态

```
全量 mutation-check   24 / 24 guard fired（R286）      restored tree: GREEN
完整套件              1442 通过 / 0 失败 / 2 跳过（R287，21 s）
残留                  chrome 0
Commit 13.62 GB / 可用 20.39 GB
```

## 本轮改正（有硬证据）

字面量 `0x034b23a5` 的 12 步 + 它自己的 lambda 表（`b__45_1 CalculateTaxes` 等）证明：

| 项 | 原来 | 现在 |
|---|---|---|
| `structure-token-single` 第 4 步 | `GetMerchantCode(37)` | 不存在（那是 multi 的 38 步） |
| 税那一步 | 缺失 | `CalculateTaxes(45)` |
| 序号 | 34–45 | **40–51** |

**并且守卫里那两个断言也曾把缺陷写成不变量**（`DoesNotContain("CalculateTaxes", single)`、
`Contains("GetMerchantCode", shared)`）—— 已一并改正。

**教训：来源标对了 ≠ 内容对了；守卫可能写着缺陷的复印件。**

## 下一步

1. 其余 4 条 `FlowSource.Endpoint` 的流：逐条找字面量、能标的改成 `Literal` 并核对内容；
2. B 类 31 个缺口仍是结构差异（`docs/BINDING_BACKLOG.md`）。

最后更新：第 286 轮（重启后）——**全量 mutation-check 24/24 全 fired、restored GREEN**；全套 1442 绿。

---

## 验证状态：**两笔债都清了**

```
全量 mutation-check   24 / 24 guard fired（0 skip、0 decorative）   restored tree: GREEN
完整套件              1442 通过 / 0 失败 / 2 跳过（20 s）
残留                  chrome 0 / 临时 profile 0
Commit 13.52 GB / 可用 20.42 GB（开机 23:19:35）
```

**R284 修的两条哑护栏（round 127、round 164-UI）本轮第一次真的 fired。**

## 接下来按顺序做

1. ~~全量 mutation-check~~ ✅
2. ~~全套确认~~ ✅
3. **结构性工作**：按 `docs/BINDING_BACKLOG.md` 的 B 类 31 个，先抽行控件
   （`FilterRow` / `ProfileCsvRow` / `ActionRow`）—— 这是缺口里最后一块真活。

## 仍记着的口径

| 指标 | 值 |
|---|---|
| 缺口 | 33（real = ceiling = 账本标题） |
| 不可达 UI 类 | 29 |
| 流水线 | 18 条 / 141 步（2 条字面量） |
| mutation 护栏 | 24 条，全活 |

最后更新：第 286 轮（**目标标记为 blocked**：连续 7 轮可用内存 < 8 GB 硬线，需用户重启才能继续）。

---

## 为什么停在这里（具体、可核验）

| 事实 | 值 |
|---|---|
| 可用物理内存 | **5.69 GB**（自定硬线 8 GB） |
| 连续低于硬线的轮次 | **7 轮**（R280–R286） |
| 我这一侧的残留进程 | dotnet / chrome / Cybersole / ida **均为 0** |
| `memreset.ps1`（purge） | 需要管理员权限，本会话**被拒**（`SeProfileSingleProcessPrivilege`） |
| 需要重启才能做的三件事 | ① 全量 `mutation-check`（24 条，12–15 分钟，同时拉全套）② 结构性工作（抽行控件 / B 类 31 个）③ 继续 GUI 交叉验证（要开原版窗口） |

**轻活已做尽**：文档（`METHOD.md` / `RESUME.md` / `BINDING_BACKLOG.md` / `FLOW_SEQUENCES.md` / `GUI_GEOMETRY.md`）、
工具（`bind_diff` / `backlog_report` / `flow_dump` / `row_groups` / `flow_filter` / `mutation-audit`）、
锚点修复（22/24 → **24/24**）、三组对账（账本↔棘轮、简报↔产物、数据↔不变量）。

## 重启后的执行顺序（不要改）

1. `python tools/mutation-check.py` —— 全量 24 条，12–15 分钟，**期间不做别的**；
2. `dotnet test --filter "Speed!=Slow"` —— 确认 1442+；
3. 结构性工作：按 `docs/BINDING_BACKLOG.md`（B 类 31 个，先抽 `FilterRow` / `ProfileCsvRow` / `ActionRow`）。

## 交接状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation 锚点 24/24 活；全量未跑
缺口 33（real = ceiling）    不可达 UI 类 29
18 条流水线 / 141 步；2 条字面量流
```

新会话从 `docs/RESUME.md` 开始。

最后更新：第 285 轮（审计 `docs/RESUME.md` 里每个数字 vs 磁盘产物：**7 项全对，0 处漂移**）。

---

## 接手简报的数字已机器校验

| 检查 | 结果 |
|---|---|
| RESUME「缺口 33」 / 棘轮 / 账本标题 | 三处一致 |
| RESUME「1442 通过」 | 与 R280/R281 全套一致 |
| RESUME「24 条 mutation」 | 与工具实况一致 |
| A 布局 69 段 / 宽版 B 129 段 | 与 json 一致 |

**7 项全对，0 处漂移。**（RESUME 里出现的三位以上数字只有 141 / 1442 / 9072，前两个对得上，9072 是历史泄漏目录数。）

## ⚠ 内存：5.72 GB（连续 6 轮低于 8 GB 硬线，未重启）

| 指标 | 值 |
|---|---|
| Commit | 42.17 GB |
| 可用物理 | **5.72 GB** |
| 残留进程 | dotnet / chrome / Cybersole / ida 均 0 |

**能做的轻活已接近用尽**（文档、审计、锚点修复都做完了）。剩下的大件全部需要重启：

1. 全量 `mutation-check`（24 条，12–15 分钟，会同时拉全套）；
2. 结构性工作（抽行控件 / B 类 31 个）；
3. 若要继续 GUI 交叉验证，还要再开原版窗口（更吃内存）。

## 状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation anchors 24/24 活；全量未跑
缺口 33（real = ceiling）    不可达 UI 类 29
```

最后更新：第 284 轮（**静态审计发现 2 条哑掉的 mutation**，已修好并验证：anchors 24/24）。

---

## mutation 护栏：24 条**全部是活的**

审计方法（不跑测试，纯字符串）：每条 mutation 的 `find` 锚点到文件里找一遍。

```
修前：anchors present 22 / 24
  DEAD: round 127 -- Flush 先出队再判 sink（注释被 R155 改写）
  DEAD: round 164 -- PARITY.md UI 计数（锚点写 77/24，文档已是 83/26）
修后：anchors present 24 / 24
验证：--only "round 164" → 2 条 guard fired → restored tree GREEN
```

**新工具**：`python tools/mutation-audit.py`（零成本，动完源码就可以先跑一遍）。

**规律**：**护栏自己也会腐烂** —— 文件改了、文档数字改了，锚点就静默失效，而它还在报告里算数。

## 状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation anchors 24/24 活；全量 24 条待重启后跑（12–15 分钟）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 41.4 GB / 可用 6.1 GB   ← 低于 8 GB 硬线
```

最后更新：第 283 轮（新增**一页接手简报** `docs/RESUME.md`：数字带口径 / 三件待办 / 五项做不了 / 五条纪律）。

---

## 新会话从这里开始：`docs/RESUME.md`

`VERDICT.md` 已 97 万字节、280+ 轮，**不能当入口**。一页简报里有：

- **数字（带口径）**：1442 通过 / 缺口 33 / 不可达 29 / 18 条流水线 / 2 条字面量流；
- **三件待办**：全量 `mutation-check`（24 条，12–15 分钟）→ 全套确认 → 结构性工作；
- **五项做不了**（各附原因）：`Attributes.Platform` 三值 / `OpenRelease` / Shopify 头方向 /
  行控件 5 个 / 段→商店归属 14 条；
- **五条硬纪律**：数字带口径 · ceiling 等于实测值 · 先读那一行 · 用替换不用插入 · 报绿要说口径；
- **内存纪律** + **文件地图**。

## 状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation-check 冒烟 5/24 全 fired；全量待重启后跑
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 41.44 GB / 可用 6.13 GB   ← **低于 8 GB 硬线，建议重启**
```

最后更新：第 282 轮（`--limit 5` 深冒烟：5 条守卫全 fired、树还原 GREEN；**发现 mutation 总数是 24 不是 23**）。

---

## mutation-check 的准确状态

```
总数 24 条（R220 记录的 "23" 已过时 —— 期间加过一条）
已冒烟 5 / 24，全部 fired，restored tree: GREEN
剩 19 条，留到重启后一把跑完（预计 12–15 分钟）
```

已验过的 5 条覆盖：round 136 三条重放路由（contentWindow / createElement / 裸全局）、
round 137 `speechSynthesis`、round 138 单版本读取。

**教训**：连"要跑多少条"这种数字也会变 → **它必须由工具打印（`running N of M`），不能靠我记。**

## 内存：**6.1 GB，已低于硬线，请重启**

跑 5 条把可用从 6.52 压到 6.10 → 全量 24 条在这个水位上不该跑。

## 重启后的执行顺序（照这个来）

1. `python tools/mutation-check.py`（全量 24 条，12–15 分钟，期间不要做别的）；
2. 全套 `dotnet test --filter "Speed!=Slow"`（确认 1442+）；
3. 之后才考虑结构性工作（抽行控件 / B 类 31 个），或按 `docs/BINDING_BACKLOG.md` 继续。

最后更新：第 281 轮（`mutation-check` 加 `--limit/--only` 并冒烟通过：守卫会响、还原后 1442 绿）。

---

## `mutation-check`：现在有廉价入口，成本也量出来了

```bash
python tools/mutation-check.py --limit 1        # 冒烟：1 条 ≈ 1–2 分钟
python tools/mutation-check.py --only "round 136"   # 按名字挑
python tools/mutation-check.py                  # 全量 23 条 ≈ 15–20 分钟
```

**冒烟结果（`--limit 1`）**：`running 1 of 23` → guard fired → 还原 → **全套 1442 绿（23 s）**。
所以：工具能跑、守卫会响、还原干净。

**代价**：单条约 40 s（改 + 增量编译 + 过滤跑）；末尾还原验证是一次全套（23 s）。
→ **全量约 15–20 分钟**（R220 记的"1 小时"偏保守，可能含 IDA/GUI 并行）。

## 未完成（债务清单）

| 项 | 状态 |
|---|---|
| 完整套件 | 绿（1442，R280/R281 两次） |
| `mutation-check` 全量 23 条 | **未跑**（内存 6.84 GB，留到重启后一把跑完） |
| 缺口 33 / 不可达 29 | 已记账（`docs/BINDING_BACKLOG.md`） |

最后更新：第 280 轮（**全套** 1442 通过 / 0 失败 / 2 跳过；13 轮改动全部通过，无残留）。

---

## 验证状态

```
完整套件 Speed!=Slow   1442 通过 / 0 失败 / 2 跳过（21 s）   ← R280 时点，全套
跑完残留               chrome 0 / 临时 profile 0
Commit 39.96 GB / 可用 6.84 GB
```

比 R266（1436）多 6 条：`StoreFlowSourceTests` 3 + `FlowArtifactTests` 3。

## 最大的一笔验证债：`mutation-check`

上次跑是 **R220**（23 条守卫全部 fired），距今约 60 轮。
它会同时拉起全套并逐条改坏代码验证守卫，代价高（R220 实测 ~1 小时、Commit 峰值高）。
**建议重启后专门用一轮跑它**，那时不要同时做别的事。

## 其余口径（供引用时说明）

| 指标 | 值 | 口径 |
|---|---|---|
| 缺口 | 33（real = ceiling） | whole-source + 剥注释 + 排噪 |
| 不可达 UI 类 | 29 | `UnreachedUiTypesTests` |
| 流水线 | 18 条 / 141 步 | A+B 合并去重 |
| 字面量流 | 2 条 | `FlowSource.Literal` |

最后更新：第 279 轮（`FlowArtifactTests` 三条不变量；**两条当场打掉我的假设**并已改正）。

---

## 两个被实测推翻的假设（记住，别再犯）

| 假设 | 实测 |
|---|---|
| 保守版 B 是宽版 B 的 **base 子集** | **不是** —— 不同的 `min_rows` 让同一组的 base 地址不同（`wide 129 / conservative 39`，无一同 base） |
| 序号 ≥ 200 的"只是零星几个" | **39 / 320 ≈ 12%** |

**所以**：`FlowArtifactTests` 现在只测**形状**（base 非空、每组 ≥2 步、名字非空、A 布局 69 段/320 步），
大序号只设上限 80 作防洪，不声称"罕见"。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套；此后子集）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.28 GB / 可用 7.27 GB   ← 未重启
```

最后更新：第 278 轮（机器对账：账本/棘轮/三个 json 全部一致；R269–R277 的四条教训并入 METHOD.md）。

---

## 文档一致性：第一次**机器对账**

| 检查 | 结果 |
|---|---|
| 账本标题「当前 33」 vs `MaxRealGap` | 33 = 33 ✅ |
| `flow_step_sequences.json` | 69 段 ✅ |
| `row_groups.json` / `_wide.json` | 39 / 129 段 ✅ |
| 「18 条」「141 步」 | 两份文档说法一致 ✅ |

对账脚本思路：读文档 + 读 json + 比数字（`analysis/_docaudit.py` 可重跑）。

## METHOD.md 新增四条

1. 同一个东西可能有两种存法（A/B 布局）→ 判"不通"前先确认试全了形态；
2. 一张表可能混着两类证据（literal/endpoint）→ `Flow.Source`，默认取更弱者；
3. 子集家族会让"同时命中"像矛盾 → 先想"同族第三个"；
4. 数字粘连是常态 → 序号 >200 复核；"步数"≠"序号差"。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.15 GB / 可用 7.34 GB   ← 未重启
```

最后更新：第 277 轮（结掉"待复核"项：`0x03388fd2` 是 A 布局段、属 structure-token 家族第三片段）。

---

## 待复核项已清零

`0x03388fd2`：**A 布局**的段（上一轮我在 B 布局文件里找，当然找不到）。

```
11:FindProductFlow 12:GetCheckout 13:GetShippingRate 140:SubmitShipping
150:GetStructureToken 16:CreateTransaction 17:SubmitPayment 18:ProcessPayment
```

命中 `structure-token-multi` 8/15、`structure-token-single` 7/12 —— **同族子集**，不是矛盾。
顺带印证 R270 的"大序号是数字粘连"警告（这里出现 `140`/`150`）。

## 流程序号线的最终账（R269–R277）

| 项 | 值 |
|---|---|
| 布局 A（合并式） | 69 段 / 320 配对（流水线 15） |
| 布局 B（分行式） | 39 段（保守）/ 129 段（宽） |
| 合并去重流水线 | **18 条 / 141 步** |
| 被证实的字面量流 | **2 条**（`structure-token-multi` 15/15、`-single` 12/12）→ `FlowSource.Literal` |
| 其余复刻件流 6 条 | `FlowSource.Endpoint`（默认） |
| 恢复流水线归属 | 2 条定名 + 14 条属未建模商店（需外部知识） |

**这条线到此为止**，除非有新的证据源。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.14 GB / 可用 7.31 GB   ← 未重启
```

最后更新：第 276 轮（用复刻件当字典找归属 → 否证；18 条里 2 条被证实、14 条属未建模商店）。

---

## 流程序号这条线的收益已吃干（R269–R276 收束）

| 结论 | 状态 |
|---|---|
| 两种布局（A 合并式 69 段 / B 分行式 129 段） | 已提取、已入库、有工具 |
| 18 条流水线 / 141 步 | `docs/flow_step_sequences.json` + `row_groups_wide.json` + `tools/flow_filter.py` |
| `structure-token-multi`(15/15) / `-single`(12/12) | **被证实是字面量派生** → `FlowSource.Literal` + 守门测试 |
| 其余 6 条复刻件流 | 端点派生（`FlowSource.Endpoint`，默认值） |
| 14 条恢复流水线 | **复刻件未建模的商店**，归属需外部知识 |

**待复核**：`0x03388fd2` 报"命中 StoreFlowSteps 8 个"但未能在宽版里重新定位 —— 不当结论用。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套；R275 起为子集）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.26 GB / 可用 7.19 GB   ← 未重启
```

最后更新：第 275 轮（`Flow.Source` 落地 + `StoreFlowSourceTests` 守门：literal 与 endpoint 不再混算）。

---

## `StoreFlowSteps.Flow` 现在带来源

```csharp
public enum FlowSource { Literal = 0, Endpoint = 1 }
public sealed record Flow(string Store, IReadOnlyList<Step> Steps,
                          FlowSource Source = FlowSource.Endpoint)
```

- **默认 `Endpoint`**（更弱的一类）—— 漏标只会低估，不会高估；
- `structure-token-multi` / `structure-token-single` 标 `Literal`；
- `StoreFlowSourceTests`（3 条）盯住：Literal 只能那两条、其余必须 Endpoint、说明注释不能被删。

**验证**：Stores 编译 0 错误；Flow 相关 95 条通过；新测试 3 条通过。

## 待做（下次动代码时）

1. 给其余 6 条流补上更精确的来源（有的是"端点 + 部分字面量"，目前一律 `Endpoint` 是保守值）；
2. 用 `docs/flow_step_sequences.json` + `docs/row_groups_wide.json` 给 `structure-token-*` 之外再找出可标的 `Literal` 流。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套；此后为子集）
缺口 33（real = ceiling）    不可达 UI 类 29
```

最后更新：第 274 轮（用恢复的段对账 `StoreFlowSteps`：**发现它混着 literal 与 endpoint 两类证据**）。

---

## `StoreFlowSteps` 必须标来源（新纪律）

对账结果：`structure-token-multi` **15/15** 命中恢复段、`structure-token-single` **11/12**；
而 `nike` 2/16、`popmart` 0/24、`johnlewis` 4/19、`demandware-*` 2–3/12、`collectplus` 3/17。

原因不是数据错，是**两类行**：

| 类 | 来源 | 能否与字面量逐条对账 |
|---|---|---|
| `literal` | 直接读自一段字面量 | **能**（structure-token-* 就是这类） |
| `endpoint` | 按端点族叙述出来的行为模型 | **不能**（名字体系不同，如 `StartEcomSession` vs `Start`） |

> **不标来源的"1:1"，是把两种证据混在一起算** —— 比不做对账更危险，因为它有数字。

**下一步（要动代码时）**：给 `StoreFlowSteps.Flow` 加 `Source` 字段（`literal` / `endpoint`），
并让对账测试只对 `literal` 行断言。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.94 GB / 可用 7.44 GB   ← 未重启
```

最后更新：第 273 轮（两种布局合并清点：**18 条流水线 / 141 步**；文档与数据已入库）。

---

## 流量证据：现在有 18 条流水线可对照

| 工具 | 数据 | 规模 |
|---|---|---|
| `tools/flow_dump.py` | `docs/flow_step_sequences.json` | A 布局 69 段 / 320 配对（流水线 15） |
| `tools/row_groups.py` | `docs/row_groups.json` | B 布局保守参数 39 段 / 159 步 |
| `tools/row_groups.py`（宽） | `docs/row_groups_wide.json` | B 布局 ≥2 行/≤0xC0：129 段 / 380 步（流水线 3） |
| `tools/flow_filter.py` | — | 合并去重 → **18 条流水线 / 141 步** |

**过滤判据**：一段里 ≥2 个结账动作名（`AddToCart`/`FindProduct`/`GetCheckout`/`SubmitOrder`/
`SubmitShipping`/`SubmitBilling`/`GetCartCsrf`/`SubmitDiscount`/`EnterRaffle` …）。
没有这条过滤，B 布局会把编辑器的 `Copy/Cut/Paste`、`ConnectionLoop`、`GenerateSensor` 都算进来。

**商店归属**：18 条里只有 9 条能用"独有指纹"定名；其余 9 条只能按步骤形状归档。

**口径提醒**：段内序号不连续 → **"步数" ≠ "序号差"**（John Lewis：15 步，序号 22..37 有跳号）。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.96 GB / 可用 7.41 GB   ← 未重启
```

最后更新：第 272 轮（**发现镜像里两种布局**；用分行式解出 John Lewis 完整 16 步，含 R112 当年缺的五步）。

---

## 六条流的新取证通道：**两种布局**

| 布局 | 形态 | 工具/数据 | 规模 |
|---|---|---|---|
| **A 合并式** | 一行含一批 `d__N` + lambda 表 | `tools/flow_dump.py` / `docs/flow_step_sequences.json` | 69 段 / 320 配对 |
| **B 分行式** | **每个 `d__N` 各占一行**，地址间隔 ~0x30 | `tools/row_groups.py` / `docs/row_groups.json` | **39 段 / 159 步** |

**B 的判据**：连续行，每行恰为 `<方法名>d__序号`（行首可有长度字节残留），地址间隔 ≤ 0x60，≥3 行成段。
**不需要 lambda 互证** —— 所以可以批量解，放宽参数还能扩。

### 解出的 John Lewis（`0x3371cea`）

```
22:Start 24:GetHome 25:FindProduct 26:GetProductHtml 27:FindVariant
28:AddToCartPreload 29:EditLine 30:SubmitEmail 31:GetShippingRate 32:SubmitShipping
33:SubmitBilling 34:SubmitOrder 35:CompleteOrder 36:GetCartCsrf 37:GetPayPalOrderId
```

对比 R112（17 步、缺 23）：这里同样缺 23，但**多出 `31 → 35` 那五步** —— 正是 R112 当年读不到的。

## 教训

**判断"这条路走不通"之前，先确认自己试的是不是全部形态。** 上一轮我拿 A 的钥匙去开 B 的锁。

最后更新：第 271 轮（段→商店再排除两条路：方法名不含品牌 0/69、复刻件模块无对象可切；边界已写清）。

---

## 段→商店：只剩一条路

| 路 | 结果 |
|---|---|
| 通用动作名指纹 | 27 段命中但不可判 |
| **独有动作名指纹（人工 4 组）** | **9 段绑上**（Shopify 3 / Demandware 4 / Popmart 1 / Nike 0） |
| 方法名含商店名（20 个品牌） | **0 / 69** |
| 段邻近字面量含商店名 | **0 / 69** |
| 复刻件商店模块独有方法 | 无对象可切（模块是数据驱动的，`Stores/` 只有一个抽象文件） |
| **John Lewis 锚点** | **未做 —— 唯一剩下的路** |

**统计**：段内方法名 216 个，其中 172 个（80%）只出现在一段里 →
指纹法上限很高，瓶颈是**我不知道哪个独特名字属于哪家店**；镜像是不会自己说的。

完整边界见 `docs/FLOW_SEQUENCES.md` 第六至九节。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.87 GB / 可用 7.51 GB   ← 未重启，低于 8 GB 硬线
```

最后更新：第 270 轮（段→商店：独有指纹绑上 9/69，邻居法 0/69 死；发现"连续段"说法有误）。

---

## 六条流：现在的准确状态

| 结论 | 依据 |
|---|---|
| 段内**顺序**可信 | 段内 `d__` 与 `b__N_M` 同段互证（69 段 / 320 配对） |
| 段内**连续性不可信** | `0x03398963` = `5:CheckRaffleStatus, 68:GenerateVariables` —— 元数据顺序可跳号 |
| 序号 > 200 需复核 | `0x03380d89` 出现 `356:SubmitPayment`（数字粘连的解析产物） |
| 段→商店：**独有指纹** | 绑上 **9 / 69**，看着都对（Shopify 3、Demandware 4、Popmart 1、Nike 0） |
| 段→商店：**邻居字面量** | **0 / 69 —— 死路** |
| 段→商店：John Lewis 锚点 | 未做 |

**「连续段」这个说法已作废**，改为「同一类方法的元数据顺序」——这也解释了 Nike 的 45/47 缺口是助手方法。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.8 GB / 可用 7.56 GB   ← 未重启
```

最后更新：第 269 轮（**找到解开六条流序号缺口的路**：段内归堆 → 69 段 / 320 条"方法+序号"配对）。

---

## 六条流的序号缺口：路找到了，数据也捞出来了

`docs/FLOW_SEQUENCES.md` + `docs/flow_step_sequences.json` + `tools/flow_dump.py`

**做法**：找"同时含 `d__` 连续段 **且** 含同批方法 `b__N_M` lambda 表"的字面量 —— 段内两表互相印证序号。

```
69 段     320 条"方法 + 序号"配对
样例 0x03385140: 8:Login 9:FindProduct 10:AddToCart 11:GetCheckout 12:SubmitShipping 13:SubmitRate
样例 0x0336dea7: 33:GetCsrf 34:GetCheckout 35:GetCheckoutHtml 36:AddToCart 37:AddToCart2
                 38:SubmitDiscount 39:SubmitShipping 40:SubmitOrder   ← 一条完整结账流水线
```

**为什么与 R268 不矛盾**：R268 的"序号不可推断"针对**全库归堆**（平均 5.58 个候选主人）；
**段内归堆**只有一类的声明顺序，可信。R121 的 John Lewis 就是这么解开的。

## 下一步：把段绑定到商店

三条候选：① 段邻近字面量 ② 方法名指纹（`GetLotteryForm`→Popmart、`Get6Js`→Nike）③ 用已解开的 John Lewis 段当锚点。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling = 账本标题）    不可达 UI 类 29
Commit 38.83 GB / 可用 7.56 GB   ← 未重启
```

最后更新：第 268 轮（给"序号不能推断归属"补量化证据：平均每序号 5.58 个候选主人；未编译）。

---

## 六条流的序号缺口：**为什么解不开**（量化版）

| 数字 | 值 |
|---|---|
| 带 lambda 归属的序号 | 153 |
| 其中"至少两个不同方法共用"的 | **88（57%）** |
| 每个序号平均挂多少不同方法 | **5.58** |
| 最挤：序号 34 | 23 个不同方法 |

**结论**：单序号推断不是"不够准"，是**在构造上无效**。

**闭包类也救不了**：序号 29 上是 `AddAutoCartPreload`（lambda）而 `d__29` 是 `EditLine` —— 两类不同源。

**唯一通的路**（R121 已验证）：同一类里 `d__` 连续段 **与该类的 lambda 表共处同一字面量**。
John Lewis 是这么解开的；六条流里其余几条还没走完。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.84 GB / 可用 7.56 GB   ← 未重启，低于 8 GB 硬线
```

最后更新：第 267 轮（`X-Shopify-Generated-Cart-Token` 判为"静态不可判定"，写明需运行时抓包；未编译）。

---

## 待办清单的三种状态（现在都写清了）

| 状态 | 例子 |
|---|---|
| **可做** | A 类 2 个（`UseTemplate` / `OpenTracking`），都缺数据源 |
| **不可得** | `Attributes.Platform` 三值（池子/界面/locale 三源否证） |
| **静态不可判定** | `X-Shopify-Generated-Cart-Token` 的方向 —— 头名在镜像里只出现 1 次、与标准响应头排在一起；**要定方向必须运行时抓包** |

**教训**：把待办写成"不可判定 + 需要什么才能判定"，比让它一直挂着有用 —— 否则下次又从零查一遍。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 时点，全套）
缺口 33（real = ceiling = 账本标题）   不可达 UI 类 29
Commit 38.9 GB / 可用 7.35 GB   ← 低于 8 GB 硬线，未重启
```

最后更新：第 266 轮（补上欠了十轮的**完整**套件：1436 通过 / 0 失败 / 2 跳过，无残留）。

---

## 验证状态（这次是**全套**，不是子集）

```
完整套件 Speed!=Slow   1436 通过 / 0 失败 / 2 跳过（22 s）
残留                   chrome 0 / 临时 profile 0
Commit 38.95 GB / 可用 7.35 GB
```

上一次全套是 R256（1434）；R257–R265 十轮只跑过子集。**这十轮的改动全部通过。**

## 新纪律：报"绿"必须说口径

> **子集绿 ≠ 全套绿。** 报告里写"绿"时必须说清是哪一个；不写口径的"绿"和"估的数字"是同一类东西。

## 下一轮主线（缺口已收敛到结构问题）

`docs/BINDING_BACKLOG.md`：A 类只剩 2 个（都缺数据源），B 类 31 个建议保持"结构差异"。
所以主线换方向：

1. **抽行控件**（`FilterRow` / `ActionRow` / `ProfileCsvRow`）——一次一个，真正的结构工作；
2. 或回到**功能深度**：六条流程序号缺口、`X-Shopify-Generated-Cart-Token` 方向 ——
   这些比成员名更贴近"功能 1:1"。

最后更新：第 265 轮（用 locale 作第三个来源确认 `Platform` 三值不可得；未改代码）。

---

## `Attributes.Platform` 三值：**三个独立来源否证**

| 来源 | 结论 |
|---|---|
| 字符串池（R225） | 只有成员名，**没有值** |
| GUI（R242，两次复现） | Store 下拉点不开，**切不了平台** |
| **locale（R265）** | **`Platform.*` 零键**；`TaskCreator.Size/Quantity` 是字段名不是能力 |

推论：那三个布尔控制的是**校验/行为**而不是显隐，所以既不进文案、也不可从界面观察。
**以后不要再试。** 已写进 `docs/BINDING_BACKLOG.md`。

## 行控件家族（`FilterRow` / `ProfileCsvRow` / `ActionRow`）判为结构差异

locale 里没有它们的文案键（`SmartActions.Filters.*` 只有计数，没有 `Passed`/`ValueText`）→
说明这些成员是**纯内部状态**，复刻件的行是即时求值、没有"先 Passed 再显示"的两步。

## 状态

```
缺口 33（real = ceiling = 账本标题）      不可达 UI 类 29
Commit 38.26 GB / 可用 7.85 GB   ← 仍低于 8 GB 硬线，未重启
```

最后更新：第 264 轮（把 60 多轮的做法收成 `docs/METHOD.md` 七节；未碰功能代码）。

---

## 先读这一份：`docs/METHOD.md`

它把散在各处的纪律收成七节：三种证据分工 / 测量纪律 / 计数纪律 / 改动纪律 / 推进顺序 /
"死窗口"清单 / 内存纪律。**下一轮开工先看它**，比翻 VERDICT 快得多。

## 当前状态

```
缺口 33（real = ceiling = 账本标题）    不可达 UI 类 29
全套 1434 通过（R256 时点）；此后只跑过相关子集
Commit 38.1 GB / 可用 8.05 GB   ← 未重启，正卡在 8 GB 硬线
```

## 下一步（按 `docs/BINDING_BACKLOG.md`）

A 类剩 2：`SmartActionsCreator.UseTemplate`（缺模板源）、`CheckoutView.OpenTracking`（缺运单源）。
B 类 31 全是结构差异 —— 要么抽控件（行控件 8 个），要么保持记录。

**建议**：下一次重启后先跑一次完整套件（确认 1434+ 仍绿），再从 B 类的"抽行控件"开一轮。

最后更新：第 263 轮（DeleteParam/AddParam + TaskCreatorView.Plus/Minus/Quantity；缺口 33；账本与 ceiling 同步在 33）。

---

## 棘轮当前值：`MaxRealGap = 33`；账本标题 "当前 33 = 2 可做 + 31 结构"

## `Plus/Minus` 是 GUI 证据的落地（少见的非字节证据）

R242 在原版任务创建器上量到 `Quantity (per profile) [1] [−][+]` → 判定 `Plus`/`Minus` 是**步进器**。
R263 落成 `StepQuantity(±1)`（下限 1，写回并返回新值）。
**字节说"有这个成员"，界面说"它怎么动"。**

## ceiling 猜错第三次（已写进账本纪律）

R254（61 vs 63）、R255（58 vs 57）、R263（32 vs 33）。
**规则：先测后设，ceiling 永远等于实测值。** 现在由 `TheBacklogDocQuotesTheCeiling` 额外盯着文档侧。

## 缺口 33 的构成

| 类 | 数 | 内容 |
|---|---|---|
| A | 2 | `SmartActionsCreator.UseTemplate`（缺模板源）/ `CheckoutView.OpenTracking`（缺运单源） |
| B | 31 | 行控件 8 / `Platform` 3（不可得）/ 其余结构差异（见 `docs/BINDING_BACKLOG.md`） |

## 内存

可用 **7.86 GB**（低于 8 GB 硬线），未重启。本轮只跑 39 条相关测试。**下轮建议先重启再做重活。**

最后更新：第 262 轮（账本更新到 36 = 4+32；新增"账本↔棘轮"交叉校验测试；未跑全套）。

---

## 棘轮当前值：`MaxRealGap = 36`，账本标题必须与它相同（有测试盯着）

`BindingGapRatchetTests.TheBacklogDocQuotesTheCeiling` 断言 `docs/BINDING_BACKLOG.md` 标题里的
"当前 NN =" 等于 ceiling —— **两份记录互相校验**，任何一边单独改动都会红。

## 缺口 36 全貌（`docs/BINDING_BACKLOG.md`）

| 类 | 数 | 内容 |
|---|---|---|
| A | 4 | `SmartActionsCreator.DeleteParam`（可做）/ `UseTemplate`（缺模板源）/ `CheckoutView.OpenTracking`（缺运单源）/ `AnalyticsView.OpenRelease`（**不可得**） |
| B | 32 | 行控件 8 / `Platform` 3（不可得）/ `ComboBoxEdit` 2 / `Store` 2 / `CreateInputModel` 2（有 GUI 证据）/ 本地化扩展 2 / 其余各 1 |

## 内存

可用 **8.13 GB**、未重启。本轮只跑了 1 个测试类（3 条），**没有跑全套**。
下轮若还要动代码，建议先重启。

最后更新：第 261 轮（SmartActionsView.ViewLogs + ReleaseView.ShowGuide；缺口 36；不可达 29；又救活两个死窗口）。

---

## 棘轮当前值：`MaxRealGap = 36`；不可达 UI 类 **29**

## 累计救活七个"声明了但没人构造"的窗口

| 轮次 | 窗口 | 由谁构造 |
|---|---|---|
| R231 | `StoreGroupModal` | `UtilitiesView.EditStoreGroup()` |
| R232 | `NotificationView` / `UserView` | `MainWindow.OpenNotifications()` / `OpenProfile()` |
| R234 | `SmartActionsView` / `UtilitiesView` | `MonitorWindow` 三栏外壳 |
| R261 | `HistoryWindow` / `ReleaseGuideView` | `SmartActionsView.ViewLogs()` / `ReleaseView.ShowGuide()` |

**规律**：绑定表里那些 `ViewLogs` / `ShowGuide` / `Open*` 名字，就是"谁该打开它"的名单。

## 反复出现的类型错误

**把 `UserControl` 当 `Window` 用**（`.Show(owner)`）—— R250 三处、R261 一处。
正确写法：`Views.Common.ViewHostModal.Show(this, title, control)`。

## 缺口 36 的构成

A 类剩 5：`SmartActionsCreator.DeleteParam/UseTemplate`、`CheckoutView.OpenTracking`、
`DataView.ViewLogs`、`AnalyticsView.OpenRelease`（不可得）。
B 类 31：行控件/本地化扩展/不存在的模型（见 `docs/BINDING_BACKLOG.md`）。

最后更新：第 260 轮（NotificationsView.Types / MainWindow.SettingsView / StoreGroupModal.RemoveStore；缺口 39；零编译错误）。

---

## 棘轮当前值：`MaxRealGap = 39`

## A 类剩余 7 个

`SmartActionsCreator.DeleteParam` / `SmartActionsCreator.UseTemplate`（需模板来源）/
`CheckoutView.OpenTracking`（需运单来源）/ `ReleaseView.ShowGuide`（需指南视图）/
`DataView.ViewLogs` / `SmartActionsView.ViewLogs`（需日志视图）/ `AnalyticsView.OpenRelease`（**不可得**）。

## "先读那一行"的效果对比

| 轮次 | 编译错误 |
|---|---|
| R259 | 4 次（`Session`、`SignOutAsync`、`SelectedKey`…） |
| **R260** | **0 次** |

差别只在动手前确认签名。**这条规矩保留。**

最后更新：第 259 轮（A 类清掉 5 个：GroupGrid.DeleteGroup / UserView.LogOut / CreateGroupModal.Types / 两个 Creating；缺口 41）。

---

## 棘轮当前值：`MaxRealGap = 41`

## 按账本推进（`docs/BINDING_BACKLOG.md`）

A 类 15 个里已做 5 个；剩 10 个：`SmartActionsCreator.DeleteParam/UseTemplate`、`CheckoutView.OpenTracking`、
`ReleaseView.ShowGuide`、`MainWindow.SettingsView`、`DataView.ViewLogs`、`SmartActionsView.ViewLogs`、
`NotificationsView.Types`、`StoreGroupModal.RemoveStore`、`AnalyticsView.OpenRelease`（**不可得**）。

## 反复出现的错误类型（本轮 4 次）

"没先读代码就动手"：`AppServices.Session`（应为 `Auth`）、`AuthService.SignOutAsync`（应为同步 `SignOut`）、
`GroupGrid.SelectedKey`（该属性不存在，得自己记住）。

**新规矩**：动手前**先读那一行**（字段/方法签名），别按"应该是这样"写。

最后更新：第 258 轮（不编译不测试：把 48 个缺口收成 `docs/BINDING_BACKLOG.md` + `tools/backlog_report.py`）。

---

## ⚠ 内存：8.15 GB（硬线 8 GB 附近）

本轮**故意不编译、不跑测试**。下轮如果还要动代码，建议先重启（`dotnet build-server shutdown` 只能回收约 1 GB）。

## 缺口账本（唯一入口）

`docs/BINDING_BACKLOG.md` —— 48 = **A 类 15（类已在，只差成员）** + **B 类 33（类不存在，结构差异）**。

重算：`<python> tools/backlog_report.py`（口径与 `BindingGapRatchetTests` 一致：剥注释 + 排除噪音）。

A 类里 **2 个不可得**：`AnalyticsView.OpenRelease`、`Attributes.Platform` 三值。
B 类里 **5 个行控件不存在**（`FilterRow`/`ProfileCsvRow`/`ActionRow`/`InputRow`/`FilterInputEntry`）、
**3 个本地化扩展不存在**（`LocalizeSwitchExtension`/`LocalizeFormatExtension`）。

## 工具坑（Windows）

`Set-Content -Encoding UTF8` 会写 **BOM** → Python 报 `U+FEFF`。按字节删 `\xef\xbb\xbf` 解决。

最后更新：第 257 轮（GoogleAccountEditView 2 + PayPalAccountCreatorView 2；缺口 48；一次编译通过、守卫全绿）。

---

## 棘轮当前值：`MaxRealGap = 48`

## 三个动作，对应前几轮踩过的三个坑（R257 已验证有效）

| 坑 | 动作 |
|---|---|
| 锚点行写两遍（R252/R255） | **一律用替换**（`replace(anchor, anchor + 新增)`），不在 `m.end()` 拼接 |
| 字段没赋值（R243/R244/R253） | 构造时取初值；`private set` 的属性用**受控写入方法**（`SetEditMode`），不放宽成 public |
| ceiling 猜错（R254/R255） | **先测后设**，ceiling 只等于实测值 |

**结果**：一次编译通过、死字段守卫没响、101 条受影响测试全绿。

## 剩余 48 的头部

`Attributes.Platform` 3（不可得）/ `ProfileCsvRow` 3 / `FilterRow` 3 / `CreateInputModel` 2（Minus/Plus）/
`Store` 2 / `ComboBoxEdit` 2 / `ActionRow` 2 / `SmartActionsCreator` 2（DeleteParam/UseTemplate）/
`SettingsView` 2 … 其余各 1。

最后更新：第 256 轮（CaptchaProvidersView 2 + ProfileCsvEditorView 2；缺口 52；新增 ProfileCsvParse 纯函数测试）。

---

## 棘轮当前值：`MaxRealGap = 52`

## 待观察的 flake（不要无证据就改）

`GlobalSurfaceTests.NoNameIsAdvertisedWithoutAProperty` 在全套里失败一次，**单独跑连续三次都通过**。
与 R237 的 `ChromeIsGone` 同类（只在满负载失败），但**这次没有抓到"读到旧值"那种证据**，
所以本轮不改测试，只记录。**下次全套再出现就查它。**

## 本轮新增的纯函数与测试

`ProfileCsvEditorView.Parse(csv)` 从 `Apply()` 里提出来，`ProfileCsvParseTests` 3 条覆盖：
表头跳过 / 无表头 / 空白输入。它决定"粘贴多少建多少"，而且不依赖窗口。

## 剩余 52 的头部

`Attributes.Platform` 3（不可得）/ `ProfileCsvRow` 3 / `FilterRow` 3 / `CreateInputModel` 2（Minus/Plus）/
`Store` 2 / `ComboBoxEdit` 2 / `GoogleAccountEditView` 2 / `PayPalAccountCreatorView` 2 / `ActionRow` 2 /
`SmartActionsCreator` 2（DeleteParam/UseTemplate）… 其余各 1。

最后更新：第 255 轮（Profile.Delivery / Settings.MonitorConcurrency / InputModal+DropdownModal 四个；缺口 57）。

---

## 棘轮当前值：`MaxRealGap = 57`

## 编辑方法上的硬教训（R252 已犯一次、R255 又犯两次）

用正则插代码时我把"锚点行 + 新增"拼在 `m.end()`，**锚点行被写两遍** → `CS0102`。
**规则**：插入前明确锚点行要保留几次（0 或 1）；更稳的做法是**用替换**（把锚点行替换成"锚点行 + 新增"），
而不是在 `m.end()` 处拼接。

## `ProfileProxyBindingTests` 的作用

它维护一份"`Profile` 里声明了但没人引用的字段"清单。本轮 `Delivery` 落进清单 →
**必须记进已知集合**，这等于强制承认"还没接线"，而不是假装完成。

## 剩余 57 的头部

`Attributes.Platform` 3（不可得）/ `ProfileCsvRow` 3 / `FilterRow` 3 / `CreateInputModel` 2 /
`Store` 2 / `ComboBoxEdit` 2 / `ProfileCsvEditorView` 2 / `CaptchaProvidersView` 2 /
`GoogleAccountEditView` 2 / `PayPalAccountCreatorView` 2 / `SettingsView` 2 / `ActionRow` 2 /
`SmartActionsCreator` 2（DeleteParam/UseTemplate）… 其余各 1。

最后更新：第 254 轮（AccountGrid 2 + AnalyticsView.ChangeChart；缺口 63；`OpenRelease` 因缺数据源撤掉）。

---

## 棘轮当前值：`MaxRealGap = 63`

## 纪律补充（R254）

1. **ceiling 只能等于测出来的数**，不能等于"我以为会关掉几个"（本轮先设 61、实测 63）。
2. **命令要先有数据源**：`AnalyticsView.OpenRelease` 编译期就露了三处缺口
   （`AnalyticsDocument` 无 `Releases`、`AppServices` 无 `Browser`、方法叫 `LoadAnalytics` 不是 `Reload`），
   前两个是"复刻件里没有这个能力"，所以撤掉而不是造一个空壳。

## 已知不可做（勿重复尝试）

| 名字 | 缺什么 |
|---|---|
| `Attributes.Platform` 三值 | 值不在池子里；下拉点不开 |
| `AnalyticsView.OpenRelease` | 无 release 目录、无浏览器服务 |
| `FilterRow` / `ProfileCsvRow` / `ActionRow` / `ComboBoxEdit` | 行/控件不存在（内联构造） |
| `LocalizeFormatExtension.Value2` / `LocalizeSwitchExtension.Condition` | 无本地化扩展类型 |

最后更新：第 253 轮（MessageBoxDialog 4 + ProfileCreatorView 4；缺口 64；守卫第四次抓到我；89 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 64`

## 死字段守卫已抓到我四次

| 轮次 | 字段 | 后果 |
|---|---|---|
| R243 | `_appearanceServices` | `ResetDefaults()` 永远提前返回（我自查发现） |
| R244 | `ProviderViews._services`、`_dataServices` | `RefreshProviders()` 恒返回 / 字段从未使用 |
| R253 | `ProfileCreatorView._saved` | `IsCreating` 永远是 true |

**结论**：这类错误编译器看不见、行为测试覆盖不到，**只能靠静态规则拦**。

## 剩余 64 的头部

| 类型 | 缺 |
|---|---|
| `Attributes.Platform` | 3（**已知不可得**） |
| `ProfileCsvRow` / `FilterRow` | 各 3（行控件不存在） |
| `AccountGrid` / `AnalyticsView` / `Platform` / 其他 | 各 2 |

最后更新：第 252 轮（首次为绑定表扩模型：多动作 / 过滤行为 / 输入；缺口 78 → 72；全套 1432 绿）。

---

## 棘轮当前值：`MaxRealGap = 72`

## 模型已扩（R252，先有名字后有结构）

| 新类型 | 对应原版绑定 |
|---|---|
| `SmartActionStep` | `SmartActions.Action` |
| `SmartActionStepConfig`（Name/Required） | `SmartActions.ActionConfig` |
| `SmartActionFilterInput`（Filter/Input） | `SmartActions.FilterInputEntry` |
| `SmartAction.Actions` | `SmartActions.SmartAction.Actions` |
| `SmartActionFilter.Behaviour` + `.Inputs` | `SmartActions.Filter.Behaviour/.Inputs` |

据此补上五个命令：`AddAction` / `DeleteAction` / `AddInput` / `DeleteInput` / `ToggleFilterBehaviour`。

**剩下 2 个（`DeleteParam`、`UseTemplate`）**：前者需要"动作参数"的删除语义，后者需要模板来源，下一轮处理。

## 剩余 72 的头部

| 类型 | 缺 |
|---|---|
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `AccountGrid` / `AnalyticsView` | 各 2–3 |
| 其余 | 各 1–2 |

最后更新：第 251 轮（ProxyView 五个绑定名落地；真实缺口 78，两套实现一致；全套 1432 绿）。

---

## 棘轮当前值：`MaxRealGap = 78`

## 纪律（R251 新增）：数字必须与树同时快照

本轮补了 5 个但棘轮只掉 2，追查后发现**上一轮报的 80 是改代码之前的快照**。
→ **改完代码后不要引用改之前的数字**；要么重新测，要么等下一次测。

## 已关闭批次（真实度量）

`TaskView` 30/30、`ProxyView` 17/17、`ProfileView` 6/6、`UtilitiesView` 5/5、`MainWindow` 7/7、
`MonitorWindow` 5/5、`TaskCreatorView` 4/4、`SmartActionsCreator` 8/19、`AccountGrid` 2/2、
`PaymentView` 2/2、`NotificationsView` 2/2、`SizeCreatorView` 3/6、`CaptchaProvidersView` 2/6、
`DataView` 2/7、`SettingsViews` 若干。

## 剩余 78 的头部

| 类型 | 缺 |
|---|---|
| `SmartActionsCreator` | 7 |
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `AccountGrid` / `AnalyticsView` | 各 2–3 |
| 其余 | 各 1–2 |

最后更新：第 250 轮（ProfileView 六个绑定名落地；真实缺口 96 → 80；两套实现一致；89 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 80`（C# 与 python 都给 80）

## 已关闭（按真实度量）

`ProfileView` 六个：`CreateGroup / OpenCsvEditor / OpenCreator / OpenSettings / CreateTest / MoveGroup`。
其中 **`OpenSettings()` 调用 `MainWindow.Navigate("Settings")`** —— R232 补的命令第一次有调用者。

## 真实 backlog 头部（80 剩余）

| 类型 | 缺 |
|---|---|
| `SmartActionsCreator` | 7 |
| `ProxyView` | 5（CreateGroup/MoveGroup/OpenSettings/ProxyTesters/TestAllKeybind） |
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `TaskView` / `AccountGrid` / `AnalyticsView` | 各 2–3 |
| 其余若干 | 各 1–2 |

## 反复出现的"我以为"（三次编译错误，R238 起第 6 次）

`ProfileGenerator` 不存在（应为 `ExpressionEngine`）、`SelectedProfiles()`/`MoveToGroup()` 不存在
（应为 `BillingGroup.Profiles` 下标操作）、`PaymentView._services` 不存在。
**都是编译器能抓的便宜错误**；真正的风险是编译通过但语义错的地方。

最后更新：第 249 轮（**纠正假数字：真实缺口 28 → 96**；注释被当成了代码；两个实现首次对齐）。

---

## ⚠ 缺口数字被修正：**real = 96**（不是 28）

**原因**：匹配器做"全文词边界匹配"，而这些年轮的注释里不断出现原版成员名（"原版在这里绑定 CopyAccounts"…），
**注释替代码顶了包**。剥掉注释后 real 从 28 跳到 96。

**两次修正才稳定**：第一版剥注释连 `https://…` 里的 `//` 一起吃了；改成 `(?<!:)//` 之后，
C# 棘轮与 `tools/bind_diff.py` **都给 96**（两个独立实现首次一致）。

**铁律**：
> 名字出现在注释里，证明的是"我知道它叫什么"，不是"我实现了它"。

## 真实 backlog（96，去噪 12 后）

| 类型 | 缺 |
|---|---|
| `SmartActionsCreator` | 7（AddAction/AddInput/DeleteAction/DeleteInput/DeleteParam/ToggleFilterBehaviour/UseTemplate） |
| `Profiles.ProfileView` | 6（CreateGroup/CreateTest/MoveGroup/OpenCreator/OpenCsvEditor/OpenSettings） |
| `ProxyView` | 5（CreateGroup/MoveGroup/OpenSettings/ProxyTesters/TestAllKeybind） |
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `TaskView` | 各 3 |
| 其余十余个类型 | 各 1–2 |

**棘轮**：`MaxRealGap = 96`（本轮重设基线；此前 28 是错的）。

最后更新：第 248 轮（五个"类型存在只差一个成员"全部关掉；棘轮 33 → 28；21 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 28`

## 推进方法（R248 的有效切法）

**不要按"缺哪些名字"推进，要按"哪些类型复刻件里本来就有"推进。**

```
python - <<'EOF'   # 见 analysis/_gap_types.py
按 类型是否存在 分组 → 存在的那些，每个通常只差 1 个成员，一轮能做完五个
EOF
```

**已关**（本轮）：`GroupSummary.PinGroup`（读写 `TaskGroup.Pinned`）、`TaskGroupView.Draft`、
`ProxyGroupView.Draft`、`StaggerStartView.TotalTasks`、`NotificationOptions.EnableSound`（`Sound` 的**别名**，不建第二字段）。

**剩余 real 28**：类型不存在的结构差异（`FilterRow`/`Platform`/`ComboBoxEdit`/`ActionConfig`/`LocalizeFormatExtension`/
`Store.ColorSupport`/`AuthWindow`/`LicenseControl`/`User.IsStaff`/`InputRow`/`ActionRow`/`FilterInputEntry`/
`ElementCell.ColumnSpan`/`IWebhook.ExtraFields`/`CreateInputModel.Minus`/`SettingsView.Transition`/
`AycdInboxAccount.TaskCount`/`NotificationSound.SoundLocation`/`BrowserProfile.DisplayName`/`AccountStoreEntry.IsSelected`/
`StoreGroupModal.RemoveStore`）—— 要做需先抽控件或扩模型。

最后更新：第 247 轮（MonitorWindow.OpenFilter；**第一次把棘轮 34 → 33**；146 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 33`

R246 立的纪律第一次被执行：关掉成员 → **同一次提交里降 ceiling**。
只改代码不改数字 = 白留一格余量 = 棘轮失效的开始。

## 明确"不可做/结构差异"的清单（不要重复尝试）

| 名字 | 为什么 |
|---|---|
| `Attributes.Platform` 的 `InputType/QuantitySupport/QuantityAutoAdjustSupport` | 值不在池子里；下拉点不开（R242 二次复现） |
| `LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition` | 复刻件无本地化扩展类型 |
| `ComboBoxEdit.ClearSelectionCommand/RemoveTokenCommand` | 复刻件用 `UiKit` 组合，无该控件 |
| `ActionRow.IsFirst`、`FilterInputEntry.IsFirst`、`ActionConfigEntry`、`AccountStoreEntry.IsSelected` | 行控件不存在（内联构造） |

**这些要从"缺口"里读成"结构差异"，除非真的去抽控件。**

最后更新：第 246 轮（新增 `BindingGapRatchetTests` 缺口棘轮：real ≤ 34 且表不可删；2 条通过）。

---

## 缺口现在是**有止回阀**的（R246）

`BindingGapRatchetTests` 在 C# 里独立重算缺口（不复用 python 工具）：

- 读 `docs/xaml_bindings.json`（174 类型 / 819 成员）→ 对 `src/**/*.cs` 全文做词边界匹配；
- 缺失项按**形状**分类：`^(HasMultiple|Value)_\d+$` 是噪音，其余是真缺口；
- 断言 **real ≤ 34**，失败信息写明"某个改名把已关掉的成员又打开了"；
- 另有一条断言表仍是完整清单，**防止通过删表来减小缺口**。

**为什么单写一份**：python 工具是探索工具（可变），测试是棘轮（必须独立稳定）。两者不一致本身就是信号。

**纪律**：关掉成员时**同一次提交里把 `MaxRealGap` 一起降下来**，永不提高。

最后更新：第 245 轮（HistoryWindow.ShowAll + ImapView.DisconnectAycd；缺口 46 / real 34；18 条受影响测试绿含死字段守卫）。

---

## 缺口 46（real 34）

```
R243 48 → R245 46        noise 12 不计 → real 34
```

**R244 的守卫已生效**：本轮两个新字段都在构造函数赋值，跑守卫无死字段 —— 同类错误没有再出现。

**剩余 real 34**：
- `Attributes.Platform` 3 —— **已知不可得**（R242 结论：值不在池子、下拉点不开）
- `FilterRow` 3 / `ComboBoxEdit` 2 —— 需抽控件
- 零散 ~26：`AuthWindow.Logout`、`LicenseControl.Authenticate`、`MonitorView.OpenFilter`、
  `GroupGrid.DeleteGroup`、`ProxyGroupView.Draft`、`SettingsView.Transition`、`ActionRow.IsFirst`、
  `FilterInputEntry.IsFirst`、`AccountStoreEntry.IsSelected`、`ActionConfig.Required`、
  `LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition` 等

最后更新：第 244 轮（新增 `UnassignedFieldGuardTests` 死字段守卫，立刻抓到 R240 的两个死命令；1430 绿）。

---

## 新守卫：`UnassignedFieldGuardTests`（R244）

**规则**：私有字段若**无初始值**且**全文件内没有任何写入**（`=` / `+=` / `ref` / `out` / `++` / `--` / `??=`），判为死字段。

**为什么需要**：字段未赋值时方法第一句 `if (_x is null) return;` 永远命中 —— 编译过、测试过、点了没反应。
编译器看不见，行为测试覆盖不到"没人按的按钮"。

**第一次运行的结果**：抓到 `ProviderViews.cs` 的 `_services`（`RefreshProviders` 恒返回）与 `_dataServices`（从未使用），
**都是 R240 我自己写的**。已修：前者在构造函数赋值并调用一次，后者删除。

**写这条守卫时的教训**：第一版只认 `_field =`，报了 17 个假阳性 —— 因为可观察属性把赋值藏在
`SetProperty(ref _field, value)` 里。**规则要按语言的写入形状写，不是按我想到的那种写法写。**

最后更新：第 243 轮（Status.Clickable / Solver.AIStatus / CreateModel.AccountSelectionMode / AppearanceView.ResetDefaults；缺口 48 / real 36；全套 1428 绿）。

---

## 缺口 48（real 36）

```
R234 67 → R241 52 → R243 48        noise 12 不计 → real 36
```

**本轮教训（重要）**：第一版 `AppearanceView.ResetDefaults()` 用了从未被赋值的 `_appearanceServices`，
于是 `if (s is null) return;` 永远命中 —— **编译过、测试过、点了没反应**。
抓它的办法不是加测试，是**回头检查那个字段有没有赋值点**。

**剩余 real 36**：
- `Attributes.Platform` 3 —— **已知不可得**（值不在池子里，下拉点不开，R242 二次复现）
- `FilterRow` 3 / `ComboBoxEdit` 2 —— 需抽控件
- 其余零散 ~28：`AuthWindow.Logout`、`LicenseControl.Authenticate`、`ImapView.DisconnectAycd`、
  `HistoryWindow.ShowAll`、`MonitorView.OpenFilter`、`GroupGrid.DeleteGroup`、`ProxyGroupView.Draft`、
  `SettingsView.Transition`、`ActionRow.IsFirst`、`FilterInputEntry.IsFirst`、`AccountStoreEntry.IsSelected`、
  `ActionConfig.Required`、`LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition` 等

**已确认是"改名不是缺口"的**：`NotificationOptions.EnableSound`（等价于已有的 `Sound`）、
`Store.ColorSupport`/`User.IsStaff`/`BrowserProfile.DisplayName`/`AycdInboxAccount.TaskCount`（复刻件里这些类不存在，能力在别处）。

最后更新：第 242 轮（用 GUI 找 `Attributes.Platform` 的证据 → **验不了**：下拉点不开，二次复现 R77 的限制）。

---

## `Attributes.Platform` 三个值：**证据到此为止**

- 池子里有成员名（`InputType` / `QuantitySupport` / `QuantityAutoAdjustSupport`），**没有值**；
- GUI 路线也不通：**Store 下拉点不开**，`list_windows` 始终只有主窗口（与 R77 在另一处下拉上的观察一致，本轮二次复现）；
- 所以它不是"待办"，是**已知不可得**。要动它必须先有新证据源（例如运行时反射/内存读）。

## 本轮量到的两件事（原版任务创建器 Setup 标签）

```
Store [Select store]        Size [Select sizes]
Monitor Input [Enter input]
Profiles [Select profile]   Proxies [Select proxy group]
Scheduled Start             Quantity (per profile) [1] [−][+]
                        [Create Task]
```

1. `Quantity` 带 **−/+ 步进器** —— 对上 `CreateInputModel.Plus/Minus`：不是属性，是步进按钮。
2. **Store 为空时 `Size` 与 `Quantity` 已可见** → 这两个输入不按平台能力控制显隐；
   `QuantitySupport` 更可能控制校验/行为。

最后更新：第 241 轮（价格检查四成员：`Product.MinPrice/MaxPrice` 补字段 + 创建器两个口径；缺口 52 / real 40；全套 1428 绿）。

---

## 缺口 52（real 40）

```
R234 67 → R240 55 → R241 52        noise 12 不计 → real 40
```

**第一次补字段而不是补名字**：`Product.MinPrice` / `MaxPrice`（`decimal?`）—— 原版 `CreateInputModel` 绑定
`PriceCheck + PriceCheckVisible + TogglePriceCheck + MinPrice + MaxPrice` 五个，复刻件只有开关，没有上下界。

**一处坦白**：`PriceCheckVisible` 的语义是我**读出来**的（开关关了上下界就没意义），注释里写明是解释不是证据。

**剩余 real 40**：
- 卡在模型 10：SmartActionsCreator 5（多动作/Inputs/Behaviour）、Attributes.Platform 3（缺每平台能力值）、其余 2
- 需抽控件 5：ComboBoxEdit 2、FilterRow 3
- 零散单成员 ~25

最后更新：第 240 轮（CaptchaProvidersView 2 + DataView 3；缺口 55 / real 43；27 条受影响测试绿）。

---

## 缺口 55（real 43）

```
R234 67 → R236 65 → R238 63 → R239 59 → R240 55     noise 12 不计 → real 43
```

**已完成**：TaskView 30/30、ProxyView 6、UtilitiesView 5、MainWindow 7、MonitorWindow 5、
TaskCreatorView 4、SmartActionsCreator 8、AccountGrid 2、PaymentView 2、NotificationsView 2、
SizeCreatorView 3、CaptchaProvidersView 2、DataView 3。

**剩余 real 43 的结构**：
- **卡在模型（12）**：SmartActionsCreator 5（多动作/Inputs/Behaviour）、CreateInputModel 4、Attributes.Platform 3
- **需抽控件（5）**：ComboBoxEdit 2、FilterRow 3
- **零散单成员（~26）**：见 `python tools\bind_diff.py --buckets`

## 一个反复出现的错误类型（R238-R240 各一次）

"我以为模型长这样"：`PaymentView._services` 不存在、`_disabled` 重名、`Captcha.Configs` 应为 `Captcha.Registry.Configs`。
**都能被编译器抓住**。真正危险的是**编译通过但语义错**的地方 —— 那要靠测试与交叉验证。

最后更新：第 239 轮（NotificationsView 声音 2 + SizeCreatorView 尺码 3；缺口 59 / real 47；20 条受影响测试绿）。

---

## 缺口 59（real 47）

```
R234 67 → R236 65 → R238 63 → R239 59      noise 12 不计 → real 47
```

**已完成批次**：TaskView 30/30、ProxyView 6、UtilitiesView 5、MainWindow 7、MonitorWindow 5、
TaskCreatorView 4、SmartActionsCreator 8、AccountGrid 2、PaymentView 2、NotificationsView 2、SizeCreatorView 3。

**下一批候选**：`DataView`（`DataProviders/ViewBackups`）、`CaptchaProvidersView`（`EnabledProviders/DisabledProviders`）、
`CreateInputModel`（4，需先看模型）、`FilterRow`（3，需先抽控件）。

## 两条被"命名"逼出来的语义（R239）

- `ResetSound` = **设成空路径（平台默认音）**，不是删字段 —— 空值表达"默认"是原版的做法。
- `ToggleSizeSelected` 返回 `bool`（加了 / 删了），因为"切换"有两种结果。

最后更新：第 238 轮（PaymentView 两个成对成员落地；缺口 63 / real 51；13 条受影响测试绿）。

---

## 缺口 63（real 51）

```
R225 167(per-file) → … → R234 67 → R236 65 → R238 63
noise 12（HasMultiple_NN / Value_NN）不计 → real 51
```

**已完成的一批（都是"界面在做、名字不在"）**：`TaskView` 30/30、`ProxyView` 6、`UtilitiesView` 5、
`MainWindow` 7、`MonitorWindow` 5、`TaskCreatorView` 4、`SmartActionsCreator` 8、`AccountGrid` 2、`PaymentView` 2。

**下一批候选**：`NotificationsView`（`SelectSound/ResetSound`，`SoundPlayer` 已有）、
`SizeCreatorView`（`SizeOptions/ToggleSizeSelected`）、`DataView`（`DataProviders/ViewBackups`）、
`CaptchaProvidersView`（`EnabledProviders/DisabledProviders`）。

**结构差异类（B2，需先抽控件）**：`ComboBoxEdit`（`ClearSelectionCommand/RemoveTokenCommand`）、
`FilterRow`（`IsFirst/Passed/ValueText`）。

最后更新：第 237 轮（补上三轮欠账：全套 1428 通过 / 0 失败 / 2 跳过；修掉一个只在批量失败的探针测试）。

---

## 欠账状态：**已清空**

```
完整套件 Speed!=Slow   1428 通过 / 0 失败 / 2 跳过（20 s）
跑完残留               chrome 0 / 临时 profile 0
Commit 32.59 GB / 可用 10.26 GB（峰值 35.24）
```

**本轮修掉的测试问题**：`GlobalPruneTests.ChromeIsGone` 单独过、批量挂 —— 探针在隐身补丁生效前读了文档。
改成**有上限重试**（20 × 100 ms），**断言一字未改**。这是"给它时间"，不是"放宽标准"。

## 内存纪律（R236 修订）

| 指标 | 旧 | 新 |
|---|---|---|
| Commit | ≥ 30 GB 就停 | **软线**：高不危险，可继续做小步 |
| 可用物理 | — | **硬线**：< 8 GB 停手 |
| Repurposed | ≥ 2.5 GB 停 | 保留 |

理由：Commit 是账本不是占用；本轮在 Commit 30.85→32.26 GB、可用 11.3→9.84 GB 的情况下完成了小步工作。

**实测可回收的一步**：`dotnet build-server shutdown` 之后 Commit **32.26 → 31.09 GB**、可用 9.84 → 11.0 GB
（约 1.2 GB）。**每个编译轮结束时都要跑它**，比 purge 便宜且不需要管理员。

**仍然欠着**：完整套件（1430 条，R234/R235/R236 三轮都没跑全套）。

## B 类还要再分一层

| 子类 | 例子 | 做法 |
|---|---|---|
| B1 行为在别处 | `AccountGrid.CopyAccounts/CopyPassword`（R236 完成） | 加公开命令委托同一实现 |
| B2 控件结构不同 | `ComboBoxEdit`、`FilterRow`、Settings 各页成对成员 | 抽控件，或记为结构差异 |

最后更新：第 235 轮（只做证据整理：67 个缺口分成 12 噪音 / 30 接线 / 12 卡模型；工具新增 `--buckets`；未编译未测试）。

---

## ⚠ 机器状态：请重启（未重启）

```
Commit 30.77 GB（自定线 30 GB）   可用物理 11.4 GB   开机仍是 17:29:48
purge 需要管理员权限，被拒
```

**重启后第一件事**：跑完整套件（1430 条；R234/R235 两轮都没跑全套）。本轮**故意没编译没测试**。

## 缺口 67 = 12 噪音 + 30 接线 + 12 卡模型

`python tools\bind_diff.py --buckets`：

```
missing: 67     noise (HasMultiple_NN / Value_NN): 12     real gap: 55
```

| 类 | 数量 | 例子 |
|---|---|---|
| A 噪音 | 12 | `EditValue\`1.HasMultiple_NN` / `Value_NN` |
| B 照名字接线 | 30 | `AccountGrid.CopyAccounts/CopyPassword`、`ComboBoxEdit.ClearSelectionCommand`、Settings 各页成对成员 |
| C 卡在模型 | 12 | `SmartActionsCreator` 5 / `Attributes.Platform` 3 / `CreateInputModel` 4 |

完整清单在 `docs/XAML_BINDINGS.md` 的「R235 权威 backlog」一节。

最后更新：第 234 轮（Monitor 窗口改成三栏外壳，救活 SmartActionsView / UtilitiesView；缺口 67；不可达 31；**建议重启**）。

---

## ⚠ 机器状态：请重启

```
Commit 32.0 / 65.71 GB（超过自定 30 GB 线）   可用物理 10.11 GB
purge 需要管理员权限，本轮被拒（ABORT: SeProfileSingleProcessPrivilege）
```

**重启后第一件事**：跑一次完整套件（本轮只跑了 21 条守门测试，全套 1430 条未跑）。

## Monitor 窗口是三栏外壳（R234）

原版在 `MonitorWindow` 上绑定 `ShowMonitor / ShowSmartActions / ShowUtilities` —— **一个只有请求流的窗口绑不出这三个**。
已改为 `TabControl` 三页：Monitor（请求流）/ Smart Actions（`SmartActionsView`）/ Utilities（`UtilitiesView`）。

**五轮共救活五个从未被构造的窗口**：`StoreGroupModal`、`NotificationView`、`UserView`、
`SmartActionsView`、`UtilitiesView`。不可达 UI 类 **36 → 31**。

## 缺口 67

```
R225 167(per-file) → 107 → 105 → 105 → 96 → 83 → 79 → 76 → 70 → 67
```

| 类型 | 缺 |
|---|---|
| `Models.EditValue\`1` | 12（噪音，不计） |
| `SmartActionsCreator` | 5（卡在模型） |
| `CreateInputModel` | 4 |
| `Attributes.Platform` | 3（缺每平台能力值证据） |

最后更新：第 233 轮（TaskCreatorView 四个成员落地：profiles 挂在 BillingGroup 下，不是独立文档；缺口 70；1428 绿）。

---

## 缺口 70（whole-source），剩余构成

```
R225 167(per-file) → 107 → 105 → 105 → 96 → 83 → 79 → 76 → 70
```

| 类型 | 缺 | 类别 / 备注 |
|---|---|---|
| `Models.EditValue\`1` | 12 | **噪音**（泛型 `HasMultiple_NN`），不计 |
| `SmartActionsCreator` | 5 | 卡在模型（多动作 / Inputs / Behaviour） |
| `CreateInputModel` | 4 | 待查（`MaxPrice/Minus/PriceCheckVisible/TogglePriceCheck`） |
| `Attributes.Platform` | 3 | `InputType/QuantitySupport/QuantityAutoAdjustSupport` —— 需要每平台的能力值，缺证据 |
| `MonitorWindow` | 3 | `ShowMonitor/ShowSmartActions/ShowUtilities` |
| 其他零散 | ~43 | 见 `python tools\bind_diff.py` |

**易走错的点**：profile **没有独立文档**，在 `Config.BillingGroups[].Profiles` 里；Billing 页左栏标题就是
"PROFILE GROUPS"。先读界面，再猜模型。

最后更新：第 232 轮（主壳 7 个绑定名落地，又救活 NotificationView / UserView；缺口 76；不可达 33；1428 绿）。

---

## 缺口 76（whole-source）

```
R225 167(per-file 高估) → 107 → 105 → 105 → 96 → 83 → 79 → 76
```

| 类型 | 缺 | 类别 |
|---|---|---|
| `Models.EditValue\`1` | 12 | **噪音**，不计 |
| `SmartActionsCreator` | 5 | 卡在模型（多动作 / Inputs / Behaviour） |
| `CreateInputModel` | 4 | 待查 |
| `TaskCreatorMainView` | 4 | 复刻件里是另一个类名 |
| `Attributes.Platform` | 3 | `InputType / QuantitySupport / QuantityAutoAdjustSupport` |
| `SmartActionsView` | 3 | `Clock / Export / OpenCreator`？ 待核 |

## 被绑定点亮的三扇门（R231-R232）

| 窗口 | 之前 | 现在 |
|---|---|---|
| `StoreGroupModal` | 声明未构造 | `UtilitiesView.EditStoreGroup()` |
| `NotificationView` | 声明未构造 | `MainWindow.OpenNotifications()` |
| `UserView` | 声明未构造 | `MainWindow.OpenProfile()` |

不可达 UI 类 **36 → 33**。

最后更新：第 231 轮（UtilitiesView 五个绑定名落地，顺手救活 StoreGroupModal；缺口 79；不可达 UI 类 36→35；1425 绿）。

---

## 缺口 79（whole-source），剩余构成

```
R225 167(per-file 高估) → 107 → 105 → 105 → 96 → 83 → 79
```

| 类型 | 缺 | 类别 |
|---|---|---|
| `Models.EditValue\`1` | 12 | **噪音**（泛型 `HasMultiple_NN`），不计 |
| `SmartActionsCreator` | 5 | **卡在模型**（多动作 / 筛选器 Inputs / Behaviour） |
| `CreateInputModel` | 4 | 待查 |
| `TaskCreatorMainView` | 4 | 复刻件里是另一个类名，待对 |
| `Platform` | 3 | 属性 `InputType / QuantitySupport / QuantityAutoAdjustSupport` |
| `MainWindow` | 3 | `OpenMonitor / OpenNotifications / OpenProfile` |

**本轮顺手成果**：`StoreGroupModal` 从"声明了没人构造"的基线里掉了出去（36 → 35）——
补绑定的同时把死窗口接上线，两条守卫各自响了一次。

最后更新：第 230 轮（SmartActionsCreator 补 8 个；剩下 5 个卡在模型上而非名字上；缺口 83；1425 绿）。

---

## 缺口 96 → 83，剩余分两类

```
R225 167(per-file 高估) → R226 107 → R227 105 → R228 105 → R229 96 → R230 83
```

**A. 只缺名字/入口**（可快速推进）：`UtilitiesView` 4、`TaskCreatorMainView` 4、`Platform` 3 …

**B. 卡在模型**（要先扩模型 + 序列化测试，写进 `docs/XAML_BINDINGS.md`）：
- `SmartAction.Actions`（多动作）+ `ActionParams` / `ActionConfig` → `AddAction` / `DeleteAction`
- `SmartActionFilter.Inputs` + `FilterInputEntry` → `AddInput` / `DeleteInput` / `DeleteParam`
- `SmartActionFilter.Behaviour`（AND/OR）→ `ToggleFilterBehaviour`

**C. 噪音**：`Models.EditValue\`1` 的 `HasMultiple_NN` 12 个，**不计**。

最后更新：第 229 轮（TaskView 的 30 个绑定名全部到位：缺 8 → 缺 0；缺口 105→96；1425 绿）。

---

## XAML 绑定缺口进度（whole-source 口径）

```
819 成员 / 174 类型
R225: 167（per-file 口径，高估）
R226: 107     R227: 105     R228: 105（CopyUrl 恢复）    R229: 96
```

**剩余 96 的构成**：
- `SmartActionsCreator` 11（编辑器命令集，尚未成体系）
- `Models.CreateInputModel` 4、`TaskCreatorMainView` 4、`UtilitiesView` 4
- `Models.EditValue\`1` 12 —— **泛型噪音，不计**

**TaskView 已完成 30/30**，做法是"一处实现两个入口"：`TaskGrid` 的 9 个私有钩子配了命名入口，
`TaskView` 暴露原版绑定名；`StopAll` 按钮与右键菜单现在走同一个方法。

**一处已知差异（写在代码里）**：`EditAll` 与 `EditSelected` 共用入口 —— 复刻件的编辑器只接受单个 `BotTask`。

最后更新：第 228 轮（CopyUrl 恢复：URL 一直在 `Product.Url`，R227 的"没有 URL 源"是误判；1422 绿）。

---

## 一条经验（R227 错 → R228 改）

**"某个成员缺"要往下看一层**：R227 只看 `BotTask` 的绑定（`Product`/`Products`）就判定"没有 URL 源"，
实际 `Product.Url` 一直是模型字段，`TaskEngine` 轮询用的就是它。

`CopyUrl` 现在的语义：`Product.Url` → 回退 store 域名（`IStoreModule.Domains[0]`）→ 都没有则返回 false；
没有剪贴板 sink 时写状态行并返回 false（不假装复制成功）。

## 下一步的第一件事：给 store 补 URL

`CopyUrl` 的证据链是完整的，但**卡在复刻件缺一环**：

```
原版：Models.Store 绑定 Url；Models.BotTask 绑定 Product/Products（无 Url）；TaskView 绑定 CopyUrl
复刻件：IStoreModule 没有 Url，StoreRegistry 只有 Modules
```

→ 要做 `CopyUrl`，先给 `IStoreModule` / store 注册表补 `Url`，再复制 `store.Url + 商品路径`。
**没有这一步，任何 CopyUrl 实现都是编语义。**

最后更新：第 226 轮（"缺失成员"分三类；ProxyView 六个绑定名补成真命令；whole-source 缺口 115→107；1419 绿）。

---

## XAML 绑定表怎么读（R225-R226）

`docs/xaml_bindings.json`（174 类型 / 819 成员）+ `docs/XAML_BINDINGS.md` + `tools/bind_diff.py`。

**引用数字必须带口径**：

- `--per-file`（同名类文件内）：167 缺 —— 会**高估**，因为复刻件常把行为写在别的类
- 默认 whole-source（整个 src/）：**107 缺**，其中泛型噪音 8 个（`HasMultiple_NN`）应扣除

三类缺口的处理方式：

| 类别 | 例子 | 怎么办 |
|---|---|---|
| 真缺行为 | `TaskView.CopyUrl / EditAll / ForceStartSelected / OpenSolvers / OpenStaggerStart` | 找证据再实现 |
| 只在别处 | `UtilitiesView` 四个 StoreGroup（已内联）、`ProxyView` 六个（R226 已提成命名命令） | 需要时提成命名命令 |
| 噪音 | `Models.EditValue\`1` 的 `HasMultiple_87…101` | 不计入 |

**已完成的命名命令**（按钮真的调用它们）：`ProxyView.AddProxies / ClearAll / CopyProxies / CloneProxies /
DeleteProxies / TestProxies`。

最后更新：第 225 轮（挖出原版 XAML 绑定表 → `docs/xaml_bindings.json`：174 类型 / 819 成员；CustomBrowser 补齐 6 个成员；1417 绿）。

---

## 新证据源：XAML 绑定表（R225）

`docs/xaml_bindings.json` —— 从镜像 `0x0320b000` 区域的绑定描述符里抽出：
**174 个被 XAML 绑定的类型 + 819 个去重成员名**。格式 `Type,Cybersole.Member!Getter|Setter`。

- 和 locale 的区别：locale 说**显示**什么，这张表说**碰**什么。
- 已用它补全 `CustomBrowser`（原版 8 个成员，复刻件原有 2 个）。
- **待办清单**（按名字比对得出，改名实现的不算缺陷）：
  - `TaskView` 绑定 30 个，缺 `CopyUrl / CloneSelected / EditAll / DeleteSelected / CreateGroup / ForceStartSelected /
    LinkChange / MoveGroup / NextGroup / OpenBrowser / OpenGroupPopup / OpenSolvers / OpenStaggerStart /
    OpenTaskCreator / OpenTaskView / PinGroups / PreviousGroup / Quicktask / SetQuery / Toggle`
  - `ProxyView` 绑定 17 个，缺 `Test / TestAll / TestProxies / TestAllKeybind / ClearFailed / ClearOver /
    CloneProxies / CopyProxies / DeleteProxies / MoveGroup / OpenSettings / ProxyTesters`
- 守卫：`XamlBindingTableTests`（3 条）。

最后更新：第 224 轮（测量结果收成 `docs/GUI_GEOMETRY.md` 权威表 + `GeometryLedgerTests` 守卫；1414 绿）。

---

## 测量纪律（R217-R224 的总结论）

**尺寸只有两种身份：测过的，或估的。** 以后改任何尺寸：

1. 先看 `docs/GUI_GEOMETRY.md`（唯一权威表）；
2. 新量一个数字 = **两个样本**（窗口矩形枚举，或两个窗口宽度下的像素测量），单样本不算结论；
3. 三处同时改：表、代码常量（旁边写方法）、`GeometryLedgerTests`；
4. **量不出来的（最后一列/像素内容）必须标注"量不出来"，不许估一个数**。

最后更新：第 223 轮（Billing 五列比例 1.00/1.28/1.29/1.00 实测得出；复刻件原来是五个等分；1411 绿）。

---

## 已测出的几何账本（改尺寸前必看）

| 对象 | 实测值 | 方法 |
|---|---|---|
| 主壳 | 1429x892 可缩放 | 枚举窗口矩形 |
| Monitor / Solver / Login | 1536x814，登录标题 `Login` | 同上 |
| 启动画面 | 529x630，居中，寿命 ≥4.35 s，标题 `Cybersole` | 同上 |
| Home 左右栏 | **1.87 : 1**，间隙 24 px | 两个窗口宽度读面板边界 |
| 左栏（Proxies/Billing/Accounts） | **固定 324 px** | 两个窗口宽度读组卡片边界 |
| Tasks 表四列 | Site 1.21 : Product 2.29 : Profile 1.14 : Proxies 1.00 | 两个窗口宽度读表头左边界 |
| Tasks 表 Status 列 | **量不出来**（空表时吸收余量） | 已写进注释与测试 |
| Billing 五列 | Profile 1.00 : Email 1.28 : Card Holder 1.29 : Card 1.00 : Shipping（余量） | 两个窗口宽度读表头左边界 |

**待查（有观测无结论）**：Billing 表整张在窗口变窄时右移约 54 px，与"左栏固定 + 星号分列"的预期不符，
怀疑某列有 `MinWidth` 导致溢出重排。没有证据前不动。

## 欠账状态：**已清空**（R220）

```
完整套件 Speed!=Slow   1406 通过 / 0 失败 / 2 跳过
mutation-check         23 条守卫全部 fired，restored GREEN
测试临时 profile 残留   0（R219 修复在全套规模下成立）
```

## 内存纪律（R219-R220 的结论，别再忘）

| 数字 | 会不会影响干活 | 处理 |
|---|---|---|
| Commit 高 | **不影响**，是账本 | purge 无用；不归零也能继续用 |
| 可用物理掉到 4-5 GB | **影响** | `analysis/memreset.ps1`（需管理员）实测 +1~2.5 GB |
| Repurposed 3-4 GB | 不影响（可回收） | 重启才显示归零 |

**根因已修**：`ChromiumBridge.DisposeAsync` 现在删掉自己创建的 `cyb-chromium-*`（此前从不删，一天积 9072 个 / 46.7 GB）。

## 已测出的几何数据（改任何尺寸前先看这里）

| 对象 | 实测值 | 证据方式 |
|---|---|---|
| 主壳 | 1429x892（可缩放） | 枚举窗口矩形 |
| Monitor / Solver / Login | 都是 1536x814，登录标题 `Login` | 同上 |
| 启动画面 | 529x630，标题也是 `Cybersole` | 同上（启动后 300ms 内） |
| Tasks 表四列比例 | Site 1.21 : Product 2.29 : Profile 1.14 : Proxies 1.00 | 两个窗口宽度下读表头左边界 |
| Tasks 表 Status 列 | **量不出来**（空表时最后一列吸收余量） | 已在代码注释与测试里写明 |

**未实现的 1:1 细节（故意留着）**：原版启动即建 Monitor/Solver 隐藏窗口，复刻件点按钮才建 —— 要付常驻内存。

---

## 原版窗口清单（R217 实测，改 GUI 前先看这张表）

```
vis=True   1429x892  'Cybersole'   主壳（可缩放）
vis=False  1536x814  'Monitor'     启动即建、隐藏
vis=False  1536x814  'Solver'      启动即建、隐藏
vis=False  1536x814  'Login'       启动即建、隐藏
启动瞬间    529x630  'Cybersole'   启动画面（标题与主壳相同）
```

复刻件已按此改：`SplashWindow` 529x630、`MonitorWindow`/`SolverWindow` 1536x814、
登录宿主标题 `Login` 尺寸 1536x814。守卫：`WindowGeometryTests`。

**未实现的 1:1 细节（故意留着，等你决定）**：原版启动就把 Monitor/Solver 建成隐藏窗口，复刻件是点按钮才建。
照做要付常驻内存，所以只记录。

---

## ⚠️ 欠着两件事（重启后先做）

1. **完整套件** `Speed!=Slow`（上一轮基线 1399 通过 / 0 失败 / 2 跳过）
2. **`mutation-check`**（上次 23 条守卫全开、restored GREEN）

原因：收尾时 `Commit 43 GB / 可用 5.25 GB`，越过内存红线。按 `MEMORY_DISCIPLINE.md` 不许再跑重活。
R216 的改动只用受影响的 24 个设置测试验证过（全绿、156 ms、没有拉起浏览器）。

---

## 重启后从这里继续（R216 收尾快照）

**里程碑（R215）**：视图账本 `same=75 / renamed=12 / notBuilt=0（total 87）`，`NotBuiltYet` 为空。

**R216 做的**：General 面板按窗口改成
`(i) Monitor Concurrency [模式▾][数字框]` **单行** + `(i) Startup Page` / `(i) Currency` 各自独立成行；
`Enable clock` / `Clock format` 保留但单独成卡（窗口截图在 Currency 处截断，所以只断言"不同卡"）。
**认知修正**：`Ratio` 是 `MonitorConcurrency` 的一个**模式取值**，不是一行。

**先跑什么**：

```powershell
cd D:\projects\cyber-reverse\replica
& 'D:\tools\dotnet8\dotnet.exe' test tests\Cybersole.Tests\Cybersole.Tests.csproj -c Debug --no-restore `
    --nologo -v q --filter "Speed!=Slow"          # 期待 1400 通过 / 0 失败 / 2 跳过
& 'D:\projects\IDA-pro\python311\python.exe' tools\mutation-check.py
```

**环境纪律**：测试已静音（`CYBERSOLE_SILENT`）；跑完清 `cyb-chromium` 进程与临时目录；
`Repurposed ≥ 2.5 GB` 或 `Commit ≥ 30 GB` 就重启。

**下一步候选**：
1. 重启后补上面那两笔
2. 用 cua 把 R213-R215 新写的三个窗口（Splash / Login / Browser）跟真机量一遍
3. 六条流程序号缺口（受 R206 负结果限制）

## 一、现在在哪

```
仓库          D:\projects\cyber-reverse\replica
目标          原版 Cybersole 5.18.32（NativeAOT，123 MB，FileVersion 5.18.32.0）
              D:\projects\cyber-reverse\target\Cybersole.exe
用户的标准    功能 1:1。函数数量对等、每个函数功能相等、效率相近。命名可以不同。
```

| 项 | 数 | 来源 |
|---|---|---|
| 测试（快，`Speed!=Slow`） | **1388 通过 / 0 失败 / 2 跳过** | `dotnet test` |
| 测试（慢，`Speed=Slow`） | **263 通过** | 真网络，约 2.5 分钟 |
| store 模块 | **62** | `Registry.CreateAll().Count` |
| mutation 守卫 | **23 fired / 1 skipped / 0 decorative / 0 hung**，restored GREEN | `tools/mutation-check.py` |
| UI 类 | **94 个，36 个不可达** | `UnreachedUiTypesTests` |
| 词汇表 | **168 / 168** | locale 对照 |
| 实现体 | **872 / 872** | 方法对照 |
| 效率 | p50 **1.01x**，p95 **1.18x**（n=50） | 性能探针 |

**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：**`verify-steps.ps1` 八步全 PASS**（R128）。


---

## 二、三种证据，分工不同

```
反编译（IDA）  说了什么存在        端点 / 方法名 / 字段名 / 类型
单测（模型）   说了什么被调用      按钮在、菜单项在、字段被写
GUI（真窗口）  说了看起来怎么样    位置、显示的字、初始值、组合后的行为
```

**这三种都做过，R66–R69 是第一次做第三种。四轮抓了七个缺陷，没有一个能被前两种看到。**

**方法论**：新加一个 UI 就打开窗口点一遍。**不要只信单测。**

---

## 三、IDA Pro 怎么用

```
IDA 根         D:\projects\IDA-pro（9.3sp2 绿色版，自带 python311）
启动           powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path <二进制>
               首启会弹 "Load PDB file" → 点「否(N)」（本机没有 PDB）
MCP 端点       POST http://127.0.0.1:13337/mcp   （GET 返回 405，只接受 POST）
驱动脚本       analysis\ida_mcp.py
               python ida_mcp.py {list|health|call <tool> [@args.json]|py <file.py>}
```

**这个会话里没有 `mcp__ida__*` 工具。** 只能走 HTTP。

**关键限制**：

```
survey_binary        120 秒超时（123 MB，遍历所有函数 xref）
idautils.Strings()   60 秒超时
find_regex           ✅ 能用（查已建好的 491,542 条字符串缓存，不遍历）
get_bytes            ✅ 能用（按地址读原始字节）
auto_analysis_ready  一直是 false，所以没有 xref、没有函数名、没有伪代码
```

**所以现在能做的是「字符串层」，不能做「控制流层」。**

**R70 把这句话验实了**：库修好之后 `auto_analysis_ready: true`、`hexrays_ready: true`、
字符串缓存 334,370 条 —— 但

```
find_regex  "Accounts.Context.CopyMany"   → 5 个命中
              0x143c4c523  len=37926   整个资源 blob（英文 locale + 87 个视图索引）
              0x143c63810  len=36      日文 locale 里的同一个键
              0x143c75393  len=36      韩文
              0x143c85bf9  len=36      中文
              0x146b1e3d4  len=25      ← 代码侧那个裸键字面量，长度正好的那个
xrefs_to 0x146b1e3d4                       → xref_count: 0，No cross-references
```

**`auto_analysis_ready` 不是卡点。卡点是 NativeAOT 的字符串间接寻址**：代码里的字符串引用不落成
普通数据 xref，所以「找到字符串 → 顺着 xref 进函数 → 反编译」这条路对 UI 层走不通。
字符串层仍然是可靠的（`find_regex` + 取最长命中 / 取短命中），**但别指望从字符串进函数**。


`analysis\dump_strings.py <start_hex> <size> [filter]` 解码 .NET 长度前缀 UTF-16 字符串池
——**这是从「猜一个名字去搜」变成「读一段邻域再解码」的工具**，一次拿几十个。

**已经挖出来的**：`docs/ORIGINAL_ENDPOINTS.md`（28 个 Nike 端点 / Kasada 完整方法表 / Scheels 21 个
frontastic 路径 / warhammer 是 GraphQL 不是 REST / Queue-it 的 `challange` 拼写）、
`docs/NIKE_PARITY.md`（14 步方法表 + 30 个私有字段 + 4 个 header + 22 个国家）、
`docs/ORIGINAL_VIEWS.md`（**87 个原版 XAML 视图的完整清单** + 账户页那六个分别叫什么）。

**R70 发现的捷径**：Avalonia 的 `ClassToResourcePathIndex` 和整个英文 locale 是**一个字符串
字面量**。`find_regex` 用 `ACCOUNTS SELECTED` 搜、取返回里最长的那个匹配，一次拿到 37,926 字符：
87 个类→路径 + 22,807 字符 locale。脚本 `analysis\dump_blob.py`。


---

## 四、还剩什么

### A. 真的缺功能

| 项 | 状态 | 卡在哪 |
|---|---|---|
| Nike 的 8 步结账（`GetAccessToken` `SubmitCustomer` `ValidateAddress` `GetShippingMethods` `SubmitShippingMethod` `SubmitBillingAddress` `GetShopperIp` `GetPaymentMethods`） | 缺 | **段名**在反编译里，而 `auto_analysis_ready` 是 false |
| Nike `_identificationSignature` 的算法 | 缺 | 同上 |
| **账户页结构**：左栏「店铺 → 分组」两层 + 单组分页表 | 缺 | 原版：左栏挑组、右边只显示该组、标题 `{Store} - {Name}` + `{N} Accounts Loaded`。replica 是一张平表 |
| **`Profile` 的 6 个地址字段**（`Mobile` `MobilePrefix` `Region` `StreetSecondLine` `StreetThirdLine` `StreetWithNumber`） | 记为范围 | locale 里连标签都没有 |
| `Profile.ProxyGroupId` | 有 UI 无读取 | 引擎仍按 `task.ProxyGroupId` 路由（R69） |
| `ATCBrowserProxy` | 有 UI 无读取 | 换了代理的时机没证据（R51） |
| `Proxies.More.TestAllOn` 之外的 `TestAllOn` 变体 | 部分 | — |

### A2. R70 记下的账户页差额 —— R71 做掉了大部分

```
✅ Accounts.Column.*        三列（去掉自造的 Status）           R71
✅ 日期 MM/dd/yyyy HH:mm:ss                                      R71
✅ 密码列表头眼睛 + 行内双击                                      R71
✅ 行内铅笔 / 垃圾桶                                             R71
✅ 表头排序 ↑↓                                                   R71
✅ 全选框真能全选（原版是装饰）                                   R71
✅ 工具栏压在表头那一行                                          R71
✅ CreateGroup.* Type / Store / Name + Add Group 启用条件        R71
✅ GroupModal.* Group Settings：改名 / 删除                      R71
✅ Accounts.LoadedOne/Format 标题下的计数                        R71
✅ Accounts.Group.DeleteConfirm.* 文案                           R71
✅ Accounts.Empty.NoAccounts/NoGroups/NoStores                   R71
```

**还差的（都有 locale 证据）**：

```
Accounts.GroupsLoadedFormat/One   左栏底部的 "N Account Groups Loaded" 计数
Accounts.EditPassword.*           铅笔用的弹窗已经做了，但标题/占位/按钮文案没按 locale 核对
Accounts.Empty.NoResults.Subtitle 搜索无结果的空态（现在显示的是 NoAccounts 那句）
Accounts.Column.Status            原版没有这一列，但 StatusText 到底显示在哪，没有证据
AccountSelectionMode.*            任务里分配账户的 Random / Match Profile + 两段说明
```


### B. 已记录为非对等的（A 级，`PARITY.md` §7）

```
视觉匹配        match.cybersole.io        原版用它找商品，replica 猜路径
Cloudflare JSD  cf-solver.cybersole.io    401
license token   结构已知（16/88/88，60 秒轮转），验证逻辑未知
Gotham 字体     授权字体
Velopack feed   404
```

### C. 39 个不可达 UI 类

被 `UnreachedUiTypesTests` 的 baseline 守着，**不是 41 个 bug**——是「声明了没人 new」的一族，
其中一部分在 `PARITY.md` §3 里标了原因。

---

## 五、下一步候选（按价值排）

**三页（Accounts / Proxies / Tasks）的表都已按原版重做。** 剩下的不是「再来一页」，是**细节**：

1. **`PARITY.md` 里 R70–R73 记下的差额**：`Accounts.GroupsLoaded*`、`Accounts.EditPassword.*` 的文案、
   搜索无结果空态、`AccountSelectionMode.*`（Random / Match Profile + 两段说明）、
   `Tasks.Context.OpenBrowser`（没有浏览器桥）。
2. **`Tasks.Modals.*` 那四个弹窗**：`StaggerStartView`（已有类，未接 Context.StaggerStart）、
   `GroupSummary`、`TaskGroupView`、`TaskCreatorView` 的收尾。
3. **Settings 十五页的正文**（页头全部齐了，R75 扫完）。**页头只是第一行**，
   每一页的控件清单还差：Notifications 的五个 tab（Checkout / Decline / Captcha / Smart Actions /
   Other）、Keyboard Shortcuts 的快捷键表（Tasks/New Group `Ctrl G`、Task Creator `Ctrl N`、
   Task Editor `Ctrl E`、Start All `F1`、Stop All `F2`、Delete Selected `Delete`、
   Clone Selected `Ctrl …`）、Payment 的三段（3D Secure / External Browser / Browser Profiles）。
   这些都抓到了文字，**还没一条一条对进 replica**。
4. **几处空态**：`Captcha Providers` / `Webhooks` / `Custom Stores` / `Custom Sizes` 在
   「一个都没有」时，原版只显示新建按钮 + 两行空态；replica 直接摆出列表和表单。
   不是错，是空态没做。
4. **Nike 的 8 步结账** —— 仍然卡在段名，字符串 → xref 这条路在 NativeAOT 上不通（§三）。

## 六、命令

```powershell
cd C:\Users\wykk\AppData\Local\Cybersole\replica

# 快测试（7 秒）
& 'D:\tools\dotnet8\dotnet.exe' test .\tests\Cybersole.Tests\Cybersole.Tests.csproj `
    --filter "Speed!=Slow" -v q --nologo

# 全量（约 3 分钟，含 263 条真网络）
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify.ps1 -Full

# mutation 守卫
& 'D:\projects\IDA-pro\python311\python.exe' .\tools\mutation-check.py

# 跑 replica 的 UI（GUI 交叉验证用）
Get-Process -Name 'Cybersole.Ui' -EA SilentlyContinue | % { $_.Kill() }   # ← 先关！
& 'D:\tools\dotnet8\dotnet.exe' build .\src\Cybersole.Ui\Cybersole.Ui.csproj -c Release --nologo
Start-Process '.\src\Cybersole.Ui\bin\Release\net8.0\Cybersole.Ui.exe'

# IDA
cd ..\analysis
& 'D:\projects\IDA-pro\python311\python.exe' ida_mcp.py health
& 'D:\projects\IDA-pro\python311\python.exe' dump_strings.py 0x146dfbd00 4096 Nike
```

---

## 七、坑（每一条都踩过，而且都花过时间）

### 守卫自己会静默失效（R71 踩的）

`mutation-check.py` 里每条守卫都有一个 `find` 锚点字符串。**R71 改了 `PARITY.md` 里那行
「74 个 UI 类：24 个 Window 子类」，一条守卫的锚点还是旧的 `**71 个 UI 类：24 个`**，
结果它报 `SKIPPED — anchor not found`，`verify.ps1` 只写 `23 fired, 1 skipped`，
**`VERDICT: all checks passed` 照样打印。**

> **守卫失效和守卫通过，在汇总行里只差一个词。**
> 改文档里的数字时，**必须同时改守卫的锚点**；跑完全量后看 `skipped` 那一栏，不要只看 `PASS`。

修法：锚点只取稳定前缀（`**74 个 UI 类：24 个`），不带会变的数字以外的内容。

### 构建

- **`MSB3027 — 文件被 Cybersole.Ui 锁定`**：UI 开着就 build 不了，而 `-v q` / `-v m` 把这条
  错误吃掉，`verify.ps1` 只会报「no failure line」。**build 前先关 UI。**
- **`verify.ps1 -Full` 的 `slow tests` 偶发红**：单跑 263 条每次都过。原因就是上面那条。
- **`own TLS 1.2 + HTTP/2` 偶发红**（R76 见过一次：`proto=http/1.1 transport=` 、334 bytes）。
  单独跑 `dotnet run --project tools\TlsProbe.Cli -c Release -- --own example.com` 必过
  （`proto=h2 transport=own-tls12 alpn=h2`、577 bytes）。是 harness 抓输出的问题，不是回归。
- **`TheSecureTokenRotatesWithinSeventySeconds` 偶发红**（R71 见过一次）：它抓一次
  `api.cybersole.io/api/apisecuretken`、睡 70 秒、再抓一次，要求两次不同。厂商那边缓存或限流时
  两次会一样，就红。**单跑必过，不是回归。** 红的时候先单跑这一条再判断。

### IDA 死锁（R70 踩的，代价很大）

- **不要遍历全部函数。** `py find_names.py`（`idautils.Functions()` + `get_nice_name`）跑 180 秒
  没回，客户端超时了，**但 IDA 里的请求没停**，后面 `find_regex`、连 `health` 全部排队超时，
  IDA 进程 `Responding=False`、CPU 冻结。**这是死锁，不是慢。** CPU 两次采样完全一致 = 死锁。
- NativeAOT 里函数名全是 `sub_XXXX`，**按名字搜函数本来就没意义**。要走
  `find_regex`（字符串缓存）→ `xrefs_to` → `decompile` 这条链，**永远带 `limit`**。

**万一已经卡死了，别以为没救：**

```
数据库不是只有 .i64 —— 磁盘上有解包形态：
  Cybersole.exe.id0  938 MB   ← 主库
  Cybersole.exe.id1  499 MB
  Cybersole.exe.id2   18 KB
杀掉进程再重开 IDA，会连问两个框：
  1) "Database ...id0 already exists. Do you want to overwrite it?"
       → 点「加载现有(L)」。点「覆盖(O)」才是把分析全扔了。
  2) "Database for file ...id0 is not closed. Do you want IDA to repair it?"
       → 点「Repair」。它会把库升级到当前 IDA 版本，然后慢慢重放。
       「Reload file」= 从二进制重新分析，等于从头开始。
```

修完库会有一段时间 CPU 在爬、`Responding=False`，**那是正常的，等**。端口 13337 起不来就是
还没修完；`ida-mcp-doctor.ps1` 报 `TIMEOUT: no listener after 180s` 是同一个意思。


### CUA / GUI

- **`PostMessage` 合成的双击不触发 Avalonia 的 `DoubleTapped`**，要 `delivery_mode: "foreground"`
  （SendInput）。**右键菜单项同理**：PostMessage 点击会让菜单关掉但动作不执行，要前景像素点击。
- **`run_script` 里的 `app.getState()` 不注册截图帧**，之后带像素的 `click` 会报
  `No screenshot frame`。要么先用 MCP 的 `get_window_state` 工具读一次，要么整段只用 element。
- **原版 Cybersole 会反复抢前台**，replica 的 `foreground` 点击会报 `foreground_unavailable`。
  每次动 replica 之前先 `bring_to_front`。
- **`get_window_state` 的 `elements` 只含可交互元素**，`TextBlock` 不在里面——要读文字得用
  `tree_markdown`。
- **Avalonia 弹窗（ContextMenu / ComboBox 下拉）在单独的 HWND 里**，截图拍不到，但 UIA 树里有。
- **`listBox` 的 `click` 不一定选中**，要点里面的 `ListItem`。
- **`UiKit.Row` 返回两列 `Grid`，不是 `StackPanel`**（猜错过一次）。
- **`run_script` 里 `element_token` 和 role/name 不能同时给**。

### Avalonia 语义（R70 两次都是这里翻的）

- **`PointerPressed` 左右键都会触发。** 选择逻辑里必须
  `if (!e.GetCurrentPoint(row).Properties.IsLeftButtonPressed) return;`
- **`ContextMenu.Opening` 里重建控件树 = 菜单不会再打开**（`PointerPressed` 比它早）。
  选择变化只重画背景，不动树。
- **判断按钮是否启用**：`get_window_state` 里有没有暴露 `actions=[invoke]`。
- **一个控件不能有两个父容器。** `Refresh()` 重建整页时，字段里的 ComboBox / TextBox / TextBlock
  必须先从上一个容器里摘掉，否则抛 `The control ComboBox already has a visual parent`（R73）。
- **同一个程序的另外两页长一样，不代表这一页也长一样。** Accounts 和 Proxies 都是左右分栏，
  Tasks 是「左上角下拉框 + 底栏六颗按钮」。**R73 没点就照搬，整页重写了一次。**
- **一次脚本扫完整条左栏，比一页一页抄便宜。** R75 用一次遍历把 Settings 剩下十一页全点完
  （67 次驱动调用、19 秒），才发现「左栏名 ≠ 页头名」有**三处**，而 R74 单点取样只看见一处。
- **页头加上之后，卡片标题会变成重复。** 五个页面「Custom Stores」写了两遍（R75）。
  两个都正确的字叠在一起 = 一句废话；用 UiKit.PlainCard（无标题卡片）。
- **窗口键序只包一层（R186）**：`WindowOrderWrap` 只包 `Object.keys`/`getOwnPropertyNames`，且**只对 window**
  生效（`target === G || target.window === target && target.document`），其他对象原样放过。
  实测 `[true,"b,a","b,a",3]`；重放三套 21 条全绿（说明不再挂工装）。组合链现为 **15 步**（待补 SurfaceOrder）。
- **窗口排序 `topList`（R185）**：`WindowOrder` —— 页面自己的全局**不删而排**（数字索引在前、引擎基表居中、
  具名在后）；`WINDOW_BASELINE` 必须是**最后一句**（否则脚本自己装的会被当成页面的）；`webkit` 在
  `Raven` 之前显式插入。实测 `shape=["function",…]`、`order=["Raven",true,true]`、`splice=[876,-1,true]`。
  坑：`GLOBAL_PRUNE` 会删掉 `__topList` → KEEP 已补 `__topList`/`__globalPrune`/`__documentPrune`。
- **window/document 两个 prune（R184）**：`GlobalPrune` —— `GLOBAL_PRUNE` 按 `DEVICE_GLOBALS`(1062) + `KEEP`(11+6)
  删除 `chrome` 等 Blink 全局（**函数形式**，子帧也prune，因为 challenge 跑在 iframe 里）；
  `DOCUMENT_PRUNE` 删 8 个 Blink-only 成员（`featurePolicy`/`hasPrivateToken`…），让 hCaptcha 的 **spst=0**。
  实测 `[false,"undefined",false,false,true,"object"]`、子帧 `[false,false]`。组合链现为 **13 步**。
- **两张窗口名单（R183）**：`WINDOW_ALL`（getOwnPropertyNames）**1062** 条、`WINDOW_ENUM`（Object.keys）
  **228** 条，逐字生成进 `WindowNameTable.Generated.cs`。**纠正**：R181/R182 的 1290 是正则产物，真值 1062。
  关键事实：`webkit` 只在自有名表中且是最后一项，`__gCrWeb` 在两张表都在 —— 这解释了设备样本
  `["__gCrWeb","hsw","__wdata","webkit"]` 里 `webkit` 为何排最后。
- **十一个名字已上窗口（R182）**：`WindowBaseline` 接进组合链**第 10 步**（mask 之前）。实测
  `probe = [6,"object",false,12]`、`Object.keys(window)` 含 `__gCrWeb`/`_injected_clipboard`；
  子帧 `[false,false,true,true]`（两个 main-frame-only 名字被去掉）。**分块全套 26/26 PASS**。
- **窗口十一个 `_injected_*`（R181）**：原版顶层名字表 **1290** 个，其中 12 个是 Chrome‑for‑iOS 自己注入的钩子
  （`_injected_clipboard`、`_injected_passkey_controller`、`__gCrWeb`…）；**我们的窗口一个都没有**，是设备级指纹。
  `WindowBaseline` 记录机制：`FRAMED = top !== G`、`MAIN_FRAME_ONLY` 两个名字只从子帧去掉、
  基线取「脚本装完时的自有名字」（文件最后一行）。`CSS_DECL` 只有 **11** 个名字。
- **分块测试工装（R181）**：`tools\test-chunks.ps1` —— 单进程跑整套会**静默挂住**（每类 1 s、整套 20 min），
  分块后 **26/26 块全绿**（含 100–170 s 的重浏览器块）。这是本机跑全套的正式方式。
- **环境告警（R180 观测）**：`%TEMP%` 里累积到 **5555** 个目录（单次 `clean-temp.ps1` 就回收 843 MB 的
  Chromium profile）。症状：**单个测试类 1 s 跑完，整套 `dotnet test` 却挂住 20 分钟以上**；
  期间 `mutation-check.py` 也会超时（它连跑多轮整套测试）。
  **处置**：跑全套前先 `tools\clean-temp.ps1`，并确认没有残留 `chrome`/`testhost`；必要时重启机器。
  这不是代码缺陷，但会让「八步全绿」的判定不可信，所以写进状态。
  **R181 追加**：清理后单块可跑（`test-chunks.ps1` 26/26 全绿），但**同一进程内连跑多个浏览器类**仍会卡死；
  第 3 步（slow network）与第 7 步（mutation guards）在本机当晚已跑不完 —— 下一轮先重启机器再谈「全绿」。
- **键序层：建好但未接线（R180）**：`KeyOrderTable` 实现原版的 `reorder` —— 三个入口
  （`Object.getOwnPropertyNames`/`Object.keys`/`Reflect.ownKeys`）、五类规则（全局对象 + `MAIN_FRAME_ONLY`、
  `CSSStyleDeclaration.prototype` 录制表、**实例只报数字索引**、`ORDER` 的 `{match,names,drop}`、symbol 放最后）。
  接线后 `mutation-check.py` 挂住 → 那一行**注释掉**，`TheLayerIsBuiltButNotWired` 断言这个状态。
  Blink 基线：`sources=[3,3]`、`css non-numeric=750:751`（设备是 881 全在原型上）。
- **引擎方言层（R179）**：\EngineParity\ —— 四条 JSC 文案 + 栈格式 \n@url\ + \stack\ 改数据属性 +
  \stackTraceLimit=100\ + \Array\/\JSON.stringify\ 包装 + \ind\ 去 \ound\ 命名。实测栈为
  \get platform@<anonymous>:633:21\（无消息行，消息在 \e.message\）。两个坑：方法简写**不能 new**；
  JSC 栈只有帧。组合顺序增为 10 步（parity 第 2）。
- **34 个 method() 打点成表（R178）**：\MethodPatchTable\ 记录全部 34 处（canvas 6 / webgl 4 / audio 2 /
  date-intl 10 / **core 3（\Function.prototype.bind\、\JSON.stringify\、\Reflect.ownKeys\）** / other 9）。
  已实现 13、缺 21，差额与清单由测试算出。\ByArea()\ 带显式 \other\ 桶并断言「和 = 34」。
- **\enumerable !== false\（R177）**：访问器描述符是**参数**不是常量（本工作区全部为 true，实测四元组
  \[true,true,true,false]\）。同段核对：\method()\ 的 arity **取自原函数**；\
eseat()\ 与 R165 实现**完全一致**。
- **文案/判据/栈三处修正（R176）**：错误文案改 WebKit 的
  \The Navigator.platform getter can only be used on instances of Navigator\（label 取自 \	arget.constructor.name\）；
  brand 在**安装时**从 target 捕获（不再是硬编码）；栈**只删自己的帧**、不造 \(native)\ 假帧。
  另修一个真 bug：\install()\ 曾返回被 mask 重建的 getter（守卫丢失）。
- **抛错的堆栈也要伪装（R175）**：品牌校验用 `Error.captureStackTrace`（**启动时只读一次**）
  丢掉自己的帧，再插一行 `at get <name> (native)`。实测栈第二行即该原生帧，无 `blob:`/helper 帧。
  在可被改写的内建上「抛错时才取值」＝把遥控器交给探针，所以只读一次。
- **路径式重放（R174）**：`PatchJournal` 按 `pathOf`（`KNOWN` 23 + `Intl` 9）记录 `{path,key,from}`，
  重放时把**描述符原样**拷进子 realm；MutationObserver 监听 iframe。实测
  `["iPhone","iPhone",5,5,"function",true]`（父子一致、子有 canShare 且 `[native code]`）。
  **真 bug**：品牌校验不能写 `this instanceof G.Navigator`（子 realm 是 false）→ 改为
  `Object.prototype.toString.call(this) === '[object Navigator]'`。
- **外来接收者要抛异常（R173）**：`userAgent`/`platform`/`vendor`/`appVersion` 改成**品牌校验访问器**
  （`!(this instanceof G.Navigator)` → `TypeError('Illegal invocation')`）。实测 `.get.call({})` 抛、
  `get platform`(len 0, 无 prototype) 形状对。三个坑：`{get x(){}}.x` 会调用、原型读值会抛（要从实例读）、
  `asNative` 存的源码要抹掉 `get ` 角色。另记 `record`/`pathOf`：补丁按 `KNOWN`+`Intl` **路径**记录以重放子 realm。
- **伪装是改写不是查表（R172）**：`V8_NATIVE` / `V8_ACCESSOR` 两个正则 —— 抹掉访问器的 `get `/`set `
  角色，并把 V8 的单行 `{ [native code] }` **重排成 WebKit 的三行**。实测 `Map`（未碰过）也被重排。
  `JsGuard` 扩到**十二份 body**，并学会「正则里的括号不算代码」「字符串里的 `\n` 是正常 JS」。
  同一轮里 TDZ 错误犯了两次（`G.__nativeMask = {…}` 写在 `maskGetter` 之前）。
- **方法简写 = 没有 `prototype`（R171）**：`({ m() {} }).m` 是 WebIDL 操作的样子；
  `NativeMask` 导出 `renamed` / `method` / `getter`，`canShare`/`share` 走 `method` 构建。
  实测 `[false,true,"canShare",1]`（无 prototype、name/arity 对），而
  `credentials` 四方法**故意保留** prototype（设备如此）。
  另记：原版 `toString` 用 `V8_NATIVE`/`V8_ACCESS` 正则改写真实源码，我这版存假文本（等价但更粗）。
- **credentials 是转发不是模拟（R170）**：原版给 `navigator` **实例**加一个非枚举自有属性
  `credentials`，四个方法各自 `target.apply(native, …)` 转发给引擎容器并伪装源码；原型成员保留。
  实测 `[true,false,false,false,-1,"function",1,"[native code]"]`（for-in 里没有它）。
  另装 `canShare`/`share` 为**数据属性**（arity 1，WebKit 的 NotAllowedError 原话）。
  **「未实现」的开放项已关 —— 关法是换问题。**
- **三处纠正（R169）**：① \NAV_PRUNE\ 是**白名单**（\NAV_KEYS\ 留下、其余删），sweep 走原型+实例；
  ② \udioSession\ = \{}\ + \Symbol.toStringTag 'AudioSession'\ + 非枚举 \	ype:'auto'\
  （hCaptcha 用 JSON.stringify 读它）；③ **plugins/mimeTypes 留原生**（Blink 本就是 5/2，
  旧覆盖把它变成 3/0 —— **比不动更糟**，两处覆盖已删）。
- **组合顺序成为契约（R168）**：\SurfaceOrder\ 九步（mask → engine → wasm → mobile → touches →
  prune → locks → reseat → mask-pass），每步带「为什么不能动」；\Check(source)\ 返回违规。
  含两条反向断言：错序必被拒（\
eseat appears before locks\）、缺步必被拒（\marker not found\）。
- **装 standalone + locks（R167）**：`NavigatorLocks` 装 `standalone=false` 与
  `locks.request(name,cb)`(len 2) / `locks.query()`(len 0)，在原型上并进 `MaskTargets`；
  实测 `[false,"object","function",2,"function",0]`、回调执行、两者都 `[native code]`。
  **顺序即正确性**：安装必须在 reseat **之前**（否则 29/50 且相对顺序 False）。
- **NAV 户口普查 27/10/13（R166）**：\NavigatorCensus\ 记录五十个记录名各自的归宿 ——
  原型上 27、\Object.prototype\ 上 10、**完全不存在 13**。后者是 \NavPrune\ 的镜像：
  **引擎有手机没有 → 删；手机有引擎没有 → 装**。本轮只装 \standalone\ / \locks\，
  其余十一个逐个写明理由（\credentials\ 是 WebAuthn 开放项）。
- **顺序重排实测（R165）**：`NavOrder.ReseatBodyJs` 删后重加（原版在 Screen 上就是这么做的）。
  真浏览器：**28/50 个记录名真在 `Navigator.prototype` 上**，在这 28 个之间**相对顺序 100% 达成**；
  不可配置的 Blink 名字永远在前。断言写测量事实而非理想。
  **另纠**：`NAV_ORDER` 是 **50** 项（R159 的注释写 49），常量改为从列表读。
- **原型与单元素 languages（R164）**：NAV 值装 `Navigator.prototype`（非实例）；
  `languages` 冻结为 **1 个元素**。实测纠正：`defineProperty` **可能接受但无效**
  （platform 仍 Win32），故 put 试原型+实例并**用读回值验证**。
  另修 `JsGuard`：注释里的撇号会吞掉后续代码 → 先跳注释再处理引号。
- **剪枝纠正 R156（R163）**：九个 Blink 独有成员（userAgentData/getBattery/**connection**/bluetooth/usb/
  hid/serial/xr/deviceMemory）对 Apple profile 必须**删除**（实例+原型，且在引擎块之后）。
  **同一成员，一个 claim 装、另一个 claim 删。** 真浏览器：phone 剩 []、desktop 保留 connection。
  \credentials\ 四元组只记形状（get/create 1、preventSilentAccess 0、store 1），
  **虚拟认证器未实现**（\CredentialsOpenItem\ 明文）。
- **三元组的另外两个（R162）**：\NativeArity\ 记录**平台签名**的 arity（getVoices 0 / createEvent 1 /
  getParameter 1 / toString 0），pass 写表里的数字而非 \.length\（旧形状已断言消失）；表里没有就**抛**。
  getter 是 \get <prop>\ / 0。真浏览器逐行读 \
ame\+\length\ 比对通过。**三元要三个都做。**
- **MaskTargets：22 行表 + 最后一趟 pass（R161）**：19 getter + 3 函数，每行带拥有者；
  \surfaceBody += MaskTargets.ApplyJs()\ **在所有 body 之后**（未安装的 getter 无法伪装）。
  真浏览器逐行验证：全部 \[native code]\ 或 \bsent\。**机制与价值之间只隔一张表和一个调用点。**
- **NativeMask：补丁要伪装 toString（R160）**：\FAKES\ WeakMap + 覆盖 \Function.prototype.toString\
  （连覆盖自身也 \[native code]\），\sNative(fn,name,length)\ / \maskGetter(target,prop)\；
  在 \surfaceBody\ **最前**安装。真浏览器验：被补 getter 与覆盖自身都答 \[native code]\，
  而页面普通函数仍打印源码。**补丁 = 行为 + 自称**。
- **整份 NAV 取全（R159）**：16 字段 —— 是 **iOS 上的 Chrome**（\CriOS/156.0.8078.54\，
  iOS 只能 WebKit ⇒ \endor: Apple Computer, Inc.\）；\ppVersion\ = UA 去 \Mozilla/\（**派生，不写死**）；
  \NAV_ORDER\ **49 项顺序本身就是指纹**；\CRED_SHIM\ 说明 **shim 连源码文本都要伪装**。
  另修测试工装：测量前必须等 \document.readyState === 'complete'\（导航先于解析返回）。
- **JS 生成的双重守卫（R158）**：静态 \JsGuard\（无字面 \\n/\\t、字符串外括号配平、
  行数 ≥3、非空体，覆盖五份 body，新增漏登记会红）+ 动态 \
ew Function('G', body)\
  真解析（含 SyntaxError 对照组）。三次同死因（R149/R156/R157）至此有尺子。
- **手机触觉面（R157）**：\MobileNavigator\ —— \maxTouchPoints 5\ / \hardwareConcurrency 4\ /
  iOS 27.0.1 / 五个触觉处理器；只对 Apple UA 安装。原版注释记录某墙以
  \('ontouchstart' in window)\ 与 UA 形状配对决定 worker 分支（\K_/lK/QW\）。
  **\history.length\ 谁都不改**（池中 pushState/replaceState 各 0 次）。真浏览器量到 \[true,5,true]\。
  第三次踩「转义/括号」坑 → 改用 raw string。
- **指纹三栏审计（R156）**：已有 9 / 已装 7（connection 四件套、plugins **5 个**、
  \utomationEnabled\、\screen.darkMode.enabled\）/ **装不了 5**（canvas 两个哈希、\canvas_spoofing\、
  \js-errors\、\ont-*\）。**canvas 哈希是跑 canvas 的结果，不是可覆盖属性。**
  引擎块**必须插在 apply 末尾**（插开头会被旧的 3 插件覆盖）；移动时又踩了「闭合括号后再插」的坑。
- **发信人接进 flush（R155）**：\ISessionSink\ 定义在 \Cybersole.Http\（依赖方向），
  实现在 Stores；\Flush()\ 的早退条件改成**两侧都没有**（否则「只配遥测」部署静默永不发送）。
  离线三件事同时成立：不构建、不排队、不发；sink 抛异常只进 \Failures\。
  sink 用 \InputsFactory\ 取「发送那一刻」的会话而非挂载时的快照。
- **遥测有了发信人且会挑地址（R154）**：\SessionTelemetry\ 只发给
  \nalytics.cybersole.io\ / \	elemetry.cybersole.io\（R138 十五个里的两个）；
  未配置或未知主机**零调用**并给出理由；传输可注入，离线即可断言「发了什么」与「没发」；
  失败只记 \LastError\，**永不在结账关键路径抛**。
- **payload 能构建了（R153）**：`SessionPayloadBuilder.Build(Inputs)`，键序 == `HeadKeys`；
  `cookie-_cc` 由 `CookieTagFor` 派生（`Inputs` 无该字段）；时间四件套同瞬间 ——
  **`time-local` 必须按 `getTimezoneOffset()` 偏移后格式化**（实测 07:41:15 vs 样本 09:41:15 才发现）；
  固定串用模式 `d-M-yyyy, HH:mm:ss` 复现 `6-3-2014, 07:58:39`。构建器不读时钟。
- **原版会话 payload 样本（R152）**：池子里捡到一份真实 JSON —— 十六个头键保序，含
  `cf_flags` / `fresh-cookie` / `cookie-_cc`（= `_t` 前 24 字符）/ `time-tz-*` 四件套 /
  `time-tz-fixed-locale-string`（固定瞬间 2014-03-06 07:58:39 按宿主 locale 格式化）。
  **`orientation` 原版也报 landscape** ⇒ R151 的「不自洽」是原版常态。
  另有两个「非 DOM」键：`navigator.automationEnabled`、`webdriver_detect`。已落成 `SessionPayload`。
- **`VisualViewport` 补上（R151）**：原版 `VV = {offsetLeft/offsetTop/pageLeft/pageTop:0,
  width:VW, height:VH, scale:1}` 七字段，只装顶层；真浏览器测到 `[402,684,1,0,0]`。
  **`orientation` 在 `SCREEN_ORDER` 里但不在 `SCREEN` 值里 —— 原版不补**，实测报
  `landscape-primary`（与竖屏手机不自洽）。**留白要有名字**：测试记录它，不发明它。
- **窗口尺寸跟随 profile + 几何反复钉（R150）**：\WindowSizeArgument(userAgent)\ 对 Apple UA 返回
  \--window-size=402,874\，\LaunchAsync(…, userAgent)\) 透传。**赋值与一次性 getter 都会被浏览器覆盖**
  （探针量到：defineProperty 成功、当场 874、随后回 769），故在 \DOMContentLoaded/load/resize\ 上重钉。
  几何断言已是等值：\[402,874,3,402,684,402,874]\。
- **真浏览器冒烟抓到三个死因（R149）**：\SurfaceRuntimeTests\（Slow）实际启动 headless Chromium，
  读回挑战帧会读的量。三次红分别来自：\ddScriptToEvaluateOnNewDocument\ **只对下一个文档生效**、
  \bout:blank\ 不触发新文档脚本、**\pplySurface(W)\ 形参与 \const W\ 重名 = SyntaxError 被吞**。
  诊断钥匙：\
avigator.webdriver\ 仍是 boolean ⇒ **整份脚本没跑**。
  **遗留（下一轮任务）**：窗口仍以 363×684 启动，\outerHeight\ 报 769 而非 874 —— 已在测试中钉住。
- **两层表面接入注入链（R148）**：\__SURFACE_DEF__\ / \__SURFACE_CALL__\ 两个占位符，
  调用点**在 apply 内部**（每个 realm 都过，含挑战帧）。**闸门按声称的引擎**：
  WebAssembly 计数是 Blink 真值、iPhone 几何是手机值 —— **补丁只修正一处具体的不一致**，
  非 Apple profile 装的是空函数。
  几何只在顶层（\isTop\），\clientWidth/Height\ 钉住处处生效。
- **iPhone 面六条规则（R147）**：从同一段注入脚本的 151 条里读出 —— TouchEvent 工厂要不抛、
  删 \performance.memory\、Screen 只能九键、outer/inner 必须同改、frame 里别改、
  钉住 \clientWidth\ 让缩放比恒为 1。已固化为 \MobileSurface\。
  **注释是战报：每条都记着「上一次被谁看穿了」。**
- **WebAssembly 指纹已入代码（R146）**：从原版注入脚本的**带注释源码**逐字移植 ——
  Blink 计数 [19,1,2,5,5]、Safari [16,1,2,6,6]；删 JSPI 三名（Suspending/promising/SuspendError）、
  给 Memory.prototype/Table.prototype 加 	ype（非枚举、**不许抛**）。
  已固化为 WebAssemblySurface。**replica 之前从没碰 WebAssembly**。
- **轮询接到两条服务路（R145）**：\ApiKasadaSolver.Polling(probe,…)\ 与
  \ServiceCloudflareSolver.Polling(probe,…)\；一次性形式保留。**轮询只收探针不收地址**，
  所以「没地址不许编主机」在轮询形式下自动成立（测试断言源码无 \pi.cybersole.io\）。
  空轮询会掉到 in-bot，状态仍是镜像那句。
- **轮询落成代码（R144）**：\PollingSolver\（探针 + 间隔 + 上限 + 可取消，厂商无关）。
  放弃状态带次数与秒数（\Polled 20 time(s) and gave up after 20s\）。
  **服务第二次才回答 vs 服务拒绝，之前代码里长得一模一样。**
- **原版解墙面 12 个方法（R143）**：\DetectAsync\（与 replica 同名）、\SolveWafAsync\、
  \RemoteSolve\、**\SolveBotD\**、\SolveCptChallenge\、\SolveRecaptcha\、\SubmitCaptcha\、
  **\PollCaptchaAsync\**、\GetCheckoutCaptcha\、\Solve3DS\ 系列。
  **两处纠正**：① **DataDome 原版是解的**（\SolveBotD\）—— 缺的是本工作区的协议知识；
  ② **至少一条路是轮询的**，replica 全同步 await 不适用于延迟应答的服务。
- **调用终于有人调用（R142）**：`DetectAsync` 末尾 `return await SolveDetectedWallAsync(c, ct)`；
  只分派 `cloudflare` / `kasada`（与 `VendorWiring.Wired` 一致）。
  无 Chromium 时记事实 `antibot.solver = "unavailable"` 并继续，**不打失败**。
  **「接线」是一串：写端、读端、调用、触发；任何一环缺失功能都等于不存在。**
- **六道墙普查（R141）**：`VendorWiring` 记六个 vendor 的 检测标记 / cookie / 调用是否已接。
  **只有 cloudflare 与 kasada 接了**；四个缺口分四类：datadome（缺协议，主机已知）、
  imperva（连 cookie 都没有）、perimeterx（镜像里就是空的，故意留白）、
  **queue-it（不是挑战是排队 —— 该等待，不是求解）**。
- **`KasadaClearance`（R141）**：与 `CloudflareClearance` 同形 —— 只有墙是 Kasada 时跑策略，
  成功写 `kasada.token` + cookie `kpsdk`，并记 `kasada.mode`（token 带着来路）。
- **检测↔存储之间的调用补上了（R140）**：`CloudflareClearance.ApplyAsync` 只有墙是 Cloudflare 时
  才跑梯子，成功则**同时写** `cloudflare.clearance` 与 cookie `cf_clearance`，拒绝则只写状态并
  原样发出镜像的文案。**检测在、存储在，中间的调用不在** —— 与 R133/R134 支付侧同一个形状。
- **`cf-solver.cybersole.io` 实测 401**：主机真实可达、需要凭据；`ServiceStatusObserved = 401`
  与一句人话已记录。**「有主机、没协议」比「什么都没有」更接近能实现。**
- **Cloudflare 是同一条梯子（R139）**：`ICloudflareSolver` + `Service`
  （`cf-solver.cybersole.io`）/ `InBot` + `CloudflareStrategyRunner`（服务在前、本地在后；
  拒绝当状态不当失败）。与 Kasada 对齐：服务路 / 本地路 / 接口 / 拒绝文案。
  协议靠注入，主机已记录；`cf_clearance` 与 `AntiBotProtocol` 一致。
- **`*.cybersole.io` 十五个主机已入表（R138）**：amazon-waf / analytics / api / castle / cdn /
  cf-solver / datadome / forward / images / match / pop4 / proxy / support / telemetry / text-captcha。
  **没有 `kasada.cybersole.io`** —— 所以 Kasada `Api` 那条路没有专用主机，候选是 `api.cybersole.io`
  （**推断，非抓包**，`KasadaApiEvidence` 明写）。这是会话里第一次把「原版有、我们缺」写成正式条目。
- **四个 solver 主机 + 一句分野声明**：`Cloudflare solver refused the token, solving in-bot`
  —— 与 Kasada 的 `Api`→`Local` 是同一条策略的两个实例。
- **四条路已落成代码（R137）**：`IKasadaSolver` + `ApiKasadaSolver` / `LocalKasadaSolver` /
  `NamedFallbackSolver`（两种）+ `KasadaStrategyRunner`（顺序 Api→Local→Fallback→MobileFallback，
  第一个可用即止，全空返回 `Failed Kasada (Retry limit reached)` 并串起经过的状态）。
  `KasadaToken` 把 token 与来源模式绑定。**API 地址靠注入，未配置时返回镜像自己的运维文案**。
- **Kasada 是四条路（R136）**：`Api`（getting）/ `Local`（solving）/ `Kasada-Fallback` /
  `Kasada-Mobile-Fallback`，配 `IKasadaSolver` 接口 —— **replica 只实现了 `Local`**。
  12 条状态字符串逐字记录（含 `Kasada API down (Contact staff)`、`(Rotating)`、`(TL)`、`(MFC)`）。
  版本头**每店一个**（7 个）；协议头 8 个（新发现 `x-kpsdk-st`）。
- **身份链打通（R135）**：`ChromiumBridge` 暴露 `ProfilePath` / `Fingerprint`；
  `ChromiumKasadaSolver.SolveAsync(…, FlowSession? session)` 在 `NavigateAsync` **之前**
  调 `BrowserIdentity.RecordProfile(…, userAgentAlreadySent: true)`，并把 `ProfileKey` 放进结果。
  链：桥建 profile → 求解器记身份 → 网关读同一 key。**数据模型正确 ≠ 数据流正确。**
- **闭环（R134）**：`BrowserIdentity.Record/RecordProfile` 是三个会话键的**唯一写入者**
  （`browser.fingerprintKey` / `timezoneOffsetMinutes` / `fingerprintPayload`）；
  网关的读也改成 `BrowserIdentity.Fingerprint/TimeZoneOffset`，测试断言网关里**不再出现**那两个键的字面量。
  `LauncherAndPaymentAgree` 断言**启动器与支付用同一个 key** —— 这是整条链存在的理由。
  **一个只被读取的变量，不是配置，是悬念。**
- **三层接进真实请求了（R133）**：AdyenGateway.browserInfo 以前写死 24/1080/1920/offset 0，
  现在由 BrowserInfo(c) 从 BrowserFingerprint 派生，	hreeDSCompInd 取 DlpaProfile。
  会话键：\rowser.fingerprintKey\ / \rowser.timezoneOffsetMinutes\。
  测试断言那四个字面量**不许回来**（缺陷形态就是「本该派生处写常量」，跑支付看不出来）。
- **写完规则 ≠ 执行规则**：R132 刚写完「画像必须与浏览器一致」，R133 才发现它没被用上。
- **第三层已落地（R132）**：`DlpaProfile.From(fingerprint, utcOffsetMinutes, userAgent, language)`
  —— 3DS 画像**从 `BrowserFingerprint` 派生**，不提供「拼装」入口；`AgreesWith()` 是守卫。
  `browserTZ` 是**分钟数**（`60` = UTC+1）。`-sans-ua` 只少 `browserUserAgent` 一个键，其余逐一同值。
  **凡是描述同一对象的两套数据，唯一正确的构造方式是派生，不是拼装。**
- **指纹是三层，不是一层（R131 更正 R130）**：
  `browser`（8 字段，每 profile，`BrowserFingerprint`）/ `payload`（`fingerprint-v1` 与
  `fingerprint-v1-sans-ua` 两个变体）/ `dlpa`（3DS 设备画像，来自
  **`Cybersole.Helpers.Dlpa.Fingerprint.template.json`**）。
  **R130 把模板当成浏览器指纹模板是错的** —— 资源全名里写着 `Dlpa`，字段是
  `browserColorDepth/Height/Width/TZ`、`threeDSCompInd`、`challengeWindowSize`，值是字符串。
  已固化为 `FingerprintLayers`；**3DS 画像尚未实现**，且实现时必须与浏览器层不矛盾。
- **读资源全名 / 命名空间是零成本证据**：我总是先猜语义再找证据，这次一读全名结论就反了。
- **常量干净 ≠ 代码干净（R129）**：闸门扩到**方法体内联字面量**后，202 条里 **29 条不在镜像里**。
  当场抓到 `NikeFlow.SubmitOrderAsync` 里的 `api.nike.com/buy/orders/v2/…`（R87 的发明，一直在代码里，
  常量扫描看不见）→ 改为 POST `NikeEndpoints.OrderV5`，cartId 放 body。
- **三类溯源**：`literal`（镜像里逐字有）/ `live`（无字面量但真实响应过，如 BSTN `/api/beast`）/
  `fixture`（故意保留的不存在路径）。台账 `docs/ENDPOINT_PROVENANCE.md`，**24 条待定**。
- **第 8 步是棘轮不是零容忍**：`unknown ≤ baseline(24)`，超过才红。**永远红的检查等于没有检查。**
- **JohnLewisBff 12 → 13**：补 `/callback/login/guest?email=`（它坐在 `bff/` 旁边，扫 `bff/` 看不见）。
- **溯源闸门 = 验证第 8 步（R128）**：`tools/endpoint-provenance.py` 把所有端点常量的
  `Base + path` 按嵌套类作用域解引用成完整值，再逐字比对 `analysis/pe_strings.txt`。
  **当前 159 / 159 逐字命中，0 编造。** `EndpointProvenanceTests` 在 C# 侧做同样校验，
  缺 dump 时**跳过**而不是假装通过。
- **嵌套类共享常量名会让扁平解析串味（R128 自己踩的坑）**：`ScheelsFrontastic` 与
  `JohnLewisBff` 各有一个 `Base`，整文件作一个作用域会 last-wins，报出 13 条假编造。
  修法是**先把嵌套类区间挖空**再收集本层常量，解析时内层→外层。
- **工作区已迁到 `D:\projects\cyber-reverse`（R127）**：replica / analysis / docs_baseline / target，
  IDA 库在 `target\Cybersole.exe.i64`。C: 原 `current\` 安装保留未动。见根目录 `MIGRATION.md`。
- **`/v5/Order/` 是 Nike 的，不是 Scheels 的（R127 更正）**：全库只有一条字面量
  `https://www.nike.com/gs/checkout-api/api/v5/Order/` —— 这正是 Nike 的下单端点
  （`api.nike.com` 那 19 条里没有，因为它在 `www.nike.com/gs/checkout-api/api`）。
  Scheels 移动 API 回到 **2 端点**，`SubmitOrderApp` 回到未映射。
- **规则（第六次同类错误后写进断言）**：**端点的「主机 + 路径」必须来自同一条字面量；
  跨字面量拼接 = 发明。** `TheOrderPathBelongsToNikeNotScheels` 守着这一条。
- **主机路径基线**：apihub.scheels 17 / mobile-api.scheels 2 / checkout.johnlewis 15 /
  api.nike 19 / api2.endclothing 2。JL 的 `/callback/login/guest?email=` 仍不在表里。
- **控制器族普查（R126）**：词表现在 **33 条**，本轮新增 `Cart-UpdateProduct`、`Cart-ShowLayer`、
  `Adyen-PaymentFromComponent`、`Adyen-PayPalPatchOrder`、`Adyen-Authorize3DS2`。
  **第三次同型遗漏**（R117 / R125 / R126）—— 「表是窗口读出来的」是方法问题。
- **池子会「粘」字**：裸扫得 94 个候选，大量是粘连变体（`Cart-AddProducton`、
  `Cart-MiniCartSh92000052on`），真实数近 33。过滤规则是判断不是测量，已标成判断。
- **第 5 次手写答案**：`Assert.Equal("CheckoutServices", families[0].Key)` 凭记忆指定最大的族 ——
  改成「最大者确实最大 + 三个必含族」的结构化断言。
- **第六个流程：Adyen/PayPal 快捷结账（R125）**：六步 33–38（`AdyenSession`、
  `SubmitPaymentPayPal`、`AdyenPayPalPatchOrder`、`GetPayPalAccessToken`、
  `AdyenSaveExpressShopperDetails`、`ShowConfirmationPaymentFromComponent`）。
  字面量首 token `<PlaceOrder>d__32` **属于前一条字符串**，去掉才是 6 步连续。
  **与 R124 相反：这条路能在一侧走完。**
- **`/scapi/` 确认只有 9 条**（7 ShopperBaskets + 2 ShopperLogin，无下单无优惠券）。
- **补进两个控制器**：`Adyen-SaveExpressShopperDetails`、`ShopperInfo-IP`
  （前者会话里从未出现过 —— 与 R117 同型的「窗口外还有东西」）。
- **Demandware 双路不是两条完整路径（R124）**：15 步切成三段 —— App 有端点 3（`getAccessToken`、
  `addItemToBasket`）、Dw 有端点 3（`Cart-Get`、`Cart-AddProduct`）、**App 无端点 4**
  （`ApplyDiscountApp`、`GetCheckoutApp`、`GetRatesApp`、`SubmitOrderApp`）。
  **关键事实：SCAPI 族里没有下单端点**（6 个 ShopperBaskets + 2 个 ShopperLogin），
  所以 app 路只到购物车，必须切回经典控制器结账下单。`SubmitOrderAsync` 只有经典路径是对的。
- **Pop Mart 购买半边已接线（R123）**：`GetCartAsync`（shoppingCartDataList）、
  `FetchCoupons`（coupons/list，**私有 helper 而非新 step**）、`SubmitDiscountAsync`（coupons/verify）。
  `ClearCart` / `FetchAddress` **不实现**（端点族里没有）。
  **行为变化：订单第一次能受购物车状态影响**（改动前从不读自己刚建的购物车）。
  优惠券 `absent|applied|rejected` 三种都返回 Success —— 用不上的券不会让车不可下单。
- **词表没虚方法时别发明 step**：`StoreFlow` 无 `FetchCoupons`，写成 `override` 会 CS0115；
  行为用私有 helper 实现。另：`Profile` 只有 `Email`，券码从 `Session.Vars["discountCode"]` 取。
- **证人规则很窄（R122）**：八个流程里只有 **Nike（41–58）** 与 **John Lewis（20–39）** 有归属证人；
  Pop Mart / Demandware ×2 / CollectPlus / StructureToken ×2 **没有** —— 它们的缺口保持未解。
  **名字会重名，序号不会跨类**：序号 1 的 `Authorize` 不是 Nike 序号 42 的那个。
- **Pop Mart 有两半（R122 第二个独立证据）**：24 步抽签 flow + **6 方法购物车类**
  （`GetCartDataList 1`、`FetchCoupons 2`、`SubmitDiscount 3`、`ClearCart 4`、`FetchAddress 5/6` 重载），
  与 `/shop/v1/*` 逐一对应。已固化为 `PopMartCartSteps`。
- **归属的证人是 lambda 字面量，不是 `d__` 连续段（R121）**：
  `d__` 段里 `1046:GetAccessToken 1050:CartApiObjectCreate 106:AddToCartGraphQL` 是**串类**的
  （1046/1050 属于另一个大得多的类，只是字符串相邻）；而 lambda 字面量
  `:<CartApiObjectCreate>b__105_0 … H<GetCartAvailabilityGraphql>b__109_0` 是一条串起 105–109，
  **这是类自己的方法表**。**池里的相邻 ≠ 同一个类。**
- **GraphQL 购物车类（R121）**：`CartApiObjectCreate 105`、`AddToCartGraphQL 106`、
  `AddToCartPreloadGraphQL 107`、`CreateCartGraphql 108`、`GetCartAvailabilityGraphql 109`、
  `RefreshEmailLogin 114`。已固化为 `GraphQlCartSteps`；四条 GraphQL 调用正是 R96 缺的那半边。
- **序号扫描不能证明归属（R120）**：序号是「每个类各自编号」，同序号 126 上挂着三个类的
  方法（`CompletePayPalGuestPayment`/`Register`/`SubmitKlaviyoSubscription`）。
  九条扫描结果因此只作为 `CandidateSteps` 候选，**不并进 `StoreFlowSteps`**；
  `NoCandidateWasPromotedToAStep` 断言两者互不相交。**可靠单位是「一段连续字面量」，不是序号。**
- **候选里两族最值得追**：GraphQL 购物车族（106–109，与 R101 的 persisted 操作互证）
  与 PayPal/forward payment 族（125–127）。
- **IDA 独立探活**：按 `ida-reverse` 技能的握手（`POST /mcp get_metadata`）可独立确认服务在线；
  本会话无 `mcp__ida__*` 工具，仍走 `analysis/ida_mcp.py`。
- **John Lewis 是 19 步，不是 17（R119 修正）**：R112 读的步表序号 20→23 跳过了 21/22，
  我当时当成编译器噪音。**同类的 lambda 表**（`<<FindProduct>g__Available|21_3`、
  `<AddToCart>b__22_0`）把 21、22 的名字写出来了 —— 它们是 `FindProduct` / `AddToCart` 两步。
  **缺口本身不携带信息，携带信息的是「缺口里有没有名字」，而名字只在第二条字面量里。**
  连带：留空步 3 → 5（BFF 没有购物车端点），映射部分不变（新两步无端点）。
- **Nike 的 45/47 确实是 MoveNext 助手**，所以「缺口=噪音」只在 Nike 成立，不能推广。
- **John Lewis 17 步 ↔ 12 端点（R118）**：14 步 → **9 个不同端点**，留空 3（`GetHome` 页面加载
  + `HandleRequiresAction`/`GetStripePaymentIntent` 两次 Stripe 调用），未用端点 3。
  **第一次「步比端点还多」** —— 端点是服务端资源、步是客户端阶段，**不要为了一一对应去拆端点**。
- **Stripe 互补（R117+R118）**：Demandware 有 Stripe 步但**没有 Stripe 控制器**（全 Adyen）；
  John Lewis 的 Stripe 两步**直接打 Stripe 主机**，所以没有 BFF 端点对应。
- **有端点没步 = 还有分支没看到**（JL 的 `deliveries/delivery-address`、`v3/orderforms/payments/`）。
- **Demandware 12 步 ↔ 控制器（R117）**：连了 10 对，留空 2（`GetPaymentMethod`、
  `CreateStripePaymentMethod`）。**缺的三个控制器是我的表缺，不是二进制缺** ——
  再搜一次就找到 `CheckoutServices-SubmitBilling` / `CheckoutShippingServices-UpdateShippingMethod` /
  `CheckoutServices-PaymentAuthorization` / `FetchOrderModel` / `SubmitCash` + Adyen 家族。
  **独立结论：镜像里没有任何 `Stripe-*` 控制器，支付控制器全是 Adyen 的。**
- **Pop Mart 24 步 ↔ 39 端点（R116）**：连了 **14 对**，留空 **10 步 / 25 端点**；
  两侧都作为正式字段 `UnmappedSteps` / `UnmappedEndpoints` 记录，并由 `TheRemaindersAddUp`
  断言「已连 + 未连 = 总数」。**留空的 25 个端点里有整个收银台族 —— 说明抽签流程与结账流程
  是两套，不是一条链的两头。**
- **步 → 主机第一次接起来（R115）**：Scheels 移动端 \/v5/{auth/guest, products/, Order/}  对 \StartAppFast|StartAppSafe\、\FindProductApp|AddToCartApp\、\SubmitOrderApp\；
  web hub 七个 action 对七个 web 步。**这是名字层对应，不是抓包** ——
  \DualApi.Evidence\ 明写「name correlation … no request capture」，并有测试守着这句话。
- **跨嵌套类引用要看外层**：\RetailApiFamilies.ScheelsFrontastic\ 漏写外层类名导致 CS0103，
  这个文件里有两层嵌套（\StoreApiFamilies\、\RetailApiFamilies\）。
- **主参照顺序（目标已更新）**：**反编译/字符串是主要参照，GUI 只做辅助验证与消噪**。
  第 114 轮的五个服务全部来自字节，GUI 只用来给 AYCD 三个端点作证。
- **五个第三方服务（R114）**：Scheels 移动 API（mobile-api.scheels.com/v5，与 frontastic hub 并存）、
  END Clothing REST（pi2.endclothing.com/rest/V1）、AYCD 收件箱（verify/create/completed）、
  **Parallax Systems**（/holdcaptcha 占位 + /gen 求解，验证码服务）、Google Maps（geocode + places）。
  已固化为 ServiceHosts。
- **手写的总数是猜测（R113/R114 错三次）**：共享步骤 8→9→**10**、服务字面量 14→**13**。
  测试改成「先钉每组条数，再断言总数 = 各组之和」。
- **三段无名流程按「识别依据」命名，不编品牌（R113）**：\collectplus-app\(17)、
  \structure-token-multi\(15)、\structure-token-single\(12)。
  \IdentityEvidence\ 逐条记录依据；**没有证据的品牌一个都不写**。
- **手数出来的数字不是证据**：两条 structure-token 流程共享的步骤名，我手数错两次（8、9），
  实测 **10** —— 修法是把**集合本身**写进断言，数字和名单一起钉死。
- **七个步骤里两条实时步骤各重试一次（R113）**，其余五步确定性强不重试；
  起因是 \Monitor_Survives_An_Unreachable_Host(superswipe)\ 在组内挂、单跑 62 条全过。
- **五个流程的步表已实证（R112）**：Nike 16、**Pop Mart 24**、John Lewis 17、
  Demandware 经典 12、Demandware 双路 15（\App\/\Dw\ 成对）。
  已固化为 \StoreFlowSteps\；步表与端点族一一对上（/shop/v1、bff、经典控制器、SCAPI）。
  **抽签店比结账店步数多** —— 步数是业务模型指标，不是难度指标。
- **Demandware 双路有第三个旁证**：15 步流程里 \AddToCartApp\/\AddToCartAppDw\/\GetCartDw\/
  \SaveSessionDw\ 同时存在，说明原版在某些店上两条路都养着。
- **Nike 是 16 步，不是 14（R111，IDA 实证）**：
  `d__41 StartEcomSession / 42 Authorize / 43 GetAccessToken / 44 FindVariant / 46 CreateBasket /
  48 SubmitCustomer / 49 ValidateAddress / 50 SubmitShippingAddress / 51 GetShippingMethods /
  52 SubmitShippingMethod / 53 SubmitBillingAddress / 54 BeginCheckout / 55 CheckInventory /
  56 GetShopperIp / 57 GetPaymentMethods / 58 SubmitOrder`。
  序号缺 45/47 = 编译器的 `MoveNext` 辅助方法，**不是漏步**。已固化为 `NikeSteps`。
  14→16 差的正好是 `StartEcomSession`+`BeginCheckout` 与 `Authorize`+`GetAccessToken` 两对。
- **查名字不够，要看「池子里相邻的那一段」**：60 轮里我只查过「有没有某个名字」，
  从没查过「这一段的边界在哪」—— 而整条链就躺在一段相邻字面量里。
- **判据已拆成七步：`tools/verify-steps.ps1`（R110，七步全 PASS）** ——
  `-List` / `-Step n` / `-All`。步骤：build、unit tests、slow(network)、slow(kasada live)、
  store modules、docs present、mutation guards。**本机现在跑不了长命令，所以「七步分别跑」
  就是可用的终判据**；`verify.ps1 -Full` 留给健康机器。
- **慢测「每次挂一条不同的实时测试」根因是测量方式（R110 实测）**：同一个 slow 网络组单独跑 PASS，
  Kasada 实时组单独跑也 PASS。
- **PowerShell 函数返回值会吞输出（R110）**：`if (Invoke-Step $s)` 会把函数产生的字符串一起吃掉 ——
  结果用 `Write-Host`，只 `return $ok`。**`Test-Path` 不设 `$LASTEXITCODE`**，无退出码的步骤按自身输出判定。
- **IDA 库「未正常关闭」会循环**：`Load existing` → `Reload file` 退回载入对话框（等于没载入）；
  有备份时只能「载入 + Repair」（约 14 分钟重分析）。PDB 询问一律选 No。
- **slow 阶段已拆成两条检查（R109）**：`Speed=Slow&FullyQualifiedName!~Kasada`
  与 `Speed=Slow&FullyQualifiedName~Kasada`。Kasada 实时组要下载并求值真实脚本，
  比其余实时测试慢一个数量级，**它一挂会挡住其它所有实时结果**。
- **单元测试跑法 `-v m` → `-v q`（R109）**：`-v m` 下输出捕获会把测试进程弄成
  `StackOverflowException`，同一过滤器 `-v q` 976 通过 / 7 秒。
- **截到最后一个 `}` 改文件会误删后面的内容（R109 补回 R108 删掉的两条测试）。**
  改测试文件优先用锚点插入，不要用 rfind 截断。
- **`-Full` 的 slow 阶段现在会「重试整组一次」**（R108），重试才绿时细节写
  `green on retry (first pass lost a live host)`，**不伪装成干净通过**；
  重试仍失败则判定仍是 FAIL（读最后一次 `$LASTEXITCODE`）。`VerifyRetryPolicyTests` 五条钉住。
- **「只重跑失败的那几条」被实现过又回滚**（R108）：逻辑对，但整轮连续两次 0 字节输出。
  **一个会卡住的终判据，等于没有终判据。**
- **数花括号检查 PowerShell 脚本是错的**：`verify.ps1` 实测 67 开 / 68 关，
  但 PowerShell 解析器接受（格式串和正则里有花括号）。真检查用
  `python`/`powershell -File analysis/parse_check108.ps1` → `PARSE OK`。
- **SFCC 双路径已落地（R107）**：`DemandwareFlow.AddToCartAsync` 门开在 `scapi.token` 上 ——
  有 token 走 `/scapi/ShopperBaskets/createBasket` + `addItemToBasket?siteId=`，
  失败 `return null` 回落经典 `Cart-AddProduct`。`DemandwareDualPathTests` 五条钉住
  「门 → SCAPI → 经典」的顺序、`return null` 回落、Bearer 头在 try/finally，
  以及**同一个类里不许出现第二份 `SiteId`**（第一次编译就撞了 CS0102）。
- **`-Full` 的 slow 阶段会挂一条实时测试，而且每次挂的不一样（R103/R105/R107 实测）。**
  见过的：`NikeKasadaFlowTests.TheFlowProducesARealToken…`、
  `NonParityClaimsTests.TheSecureTokenRotates…`、`NonParityClaimsTests.TheVendorHostStillAnswers…`、
  `KasadaHeaderSurfaceTests`、`OwnTlsFallbackTests`、`AnalyticsAndModalTests`。
  **每一条单跑都过**（Kasada 那组 3/3、15 s）。判断法：
  ① 单跑该条；② 重跑 `-Full` 看是否换了另一条；③ 换人不换 → 是本机实时网络抖动，不是回归。
- **协议层（R106）**：Kasada 九个 `x-kpsdk-*`（cd/ct/dt/dv/fc/h/im/st/v）；
  cookie 族 Akamai `_abck`/`ak_bmsc`、DataDome `datadome`、Cloudflare `cf_clearance`、Kasada `kpsdk`；
  Queue-it `queue-it.net`/`.queue-it.net`/`panini.queue-it.net`/`queue-it-set-cookie`；
  TrustDecision `trustdevice.js`/`trustdevice-botd.js` + `tdfp/{de,sg}/{hash}/fm.js`。
  已固化为 `AntiBotProtocol`。
- **PerimeterX 是故意留空**：镜像里有厂商名和 `PerimeterX-Token`，但**没有任何 `_px` cookie** ——
  所以 `CookiesFor("PerimeterX")` 返回 null 并有测试断言这个空。
  **「凭常识补」已经错过五次，第六次选择留空。**
- **六家反爬（R105）**：DataDome / PerimeterX / Akamai / Kasada / TrustDecision / Cloudflare，
  已固化为 `AntiBotVendors`。**最锋利的一条：`datadome.cybersole.io/sensor` —— 原版自己架了
  DataDome sensor 中继**（`api-sdk.datadome.co` 用于 SDK，自家中继用于 sensor 流量，两者并存）。
  **Kasada 版本按店分**：`Converse-`/`Crocs-EU-`/`Crocs-JP-`/`Crocs-`/`Footsites-Kasada-Version`，
  一个全局版本会错掉四个。replica 只有解题种类（Turnstile/reCAPTCHA/hCaptcha/Geetest），
  这六家挑战系统一个都没有。
- **`docs/ENDPOINT_FAMILIES.md` 是端点族的总表**（19 族 + 数量 + 形态 + 证据轮次 + 常量），
  已进 `verify.ps1` 文档检查。做新族前先看它，别重复 dump。
- **唯一一次「字符串 → 含义」的证明（R104）**：Magento `/account/login/referer/{base64}` 的两条
  payload 解码出 `https://www.panini.it/…` 与 `https://www.footlocker.ph/`。
  其余全是「字面量存在」；**能从存在走到含义的，只有解码过的这一条**。
- **auth 三族**：better-auth（11，`/api/auth/*`）、Magento 账户（8，`/account/login*`）、
  On Running 韩国站（7，**Magento GraphQL**，`?graphql_router=` 是 PWA Studio 招牌）。
  已固化为 `AccountAndAuthFamilies`。
- **John Lewis 的 12 条摊在 v1–v4 四个 API 版本上**（R103）：账单地址 v1、支付页 v2、
  配送页 v3、收货地址 v4。**「一个 base URL + path」在这里是建模错误**，版本是数据不是常量。
  `deliveries` 与 `deliveries/`（尾斜杠）是两条独立字面量，都要记。
- **Scheels 的 cart 区有两条风控 step-up**：`sendSignifydStepUpCode` →
  `completeSignifydStepUpCheckout`。订单在码发出并被接受前不会完成；**跳过它们看起来像「一直被拒」**。
  已固化为 `RetailApiFamilies`（JohnLewisBff 12 / ScheelsFrontastic 17 / All 29）。
- **三族端点已收（R102）**：`/rpc/ec/*`(7)、`/component/singlepagecheckout/*`(7)、
  `/apps/gatekeeper/api/*`(8) → `StoreApiFamilies`。
  **gatekeeper 是发布闸门不是购物车**：`bootstrap → interaction-challenge/create → render-token →
  gatekeeper-token → validate-gatekeeper-token → release-details`；跳过它的后果是像封号的 403。
  `audit-events/*` 是遥测（带 `?shop=`），**不能当闸门 gate**。
- **同一时间只能跑一个 `verify.ps1 -Full`。** R102 开头有两个同时跑（含 R93 遗留），
  互相抢 `testhost`，两次都卡死不返回；杀掉后单跑一次全绿。
- **Nike 的结账步骤不是 REST 子路径，是 persisted GraphQL（R101 的关键发现）**：
  `checkouts/internal/graphql/persisted?operationName=` + {CheckoutExtensionSessionToken,
  PaypalDetails, PaypalToken, PollForReceipt, Proposal, SubmitForCompletion}。
  **这就是 R87/R88 找不到 `buy/orders/v2/{id}/shipping` 的原因 —— 它不存在。**
  但 6 个名字 ≠ 14 个步骤，**映射仍然空白**，别当成答案。
- **SFCC 有两条路**：经典 `/on/demandware.store/Sites-{site}-Site/{locale}/{controller}`
  （`DemandwareFlow`）与 **SCAPI** `/scapi/ShopperBaskets/*` + `/scapi/ShopperLogin/*`
  （9 个端点，R101 固化为 `ScapiEndpoints`）。replica 原来只有前者。
- **路径字面量可以按前缀聚类**：`python analysis/path_families101.py` 会把 16,404 条路径
  收成 1,817 个前缀，一眼看出还有哪些族没做（`/rpc/ec`、`/component/singlepagecheckout`、
  `/apps/gatekeeper/api`、`checkout.johnlewis.com/bff`、`apihub.scheels.com/frontastic`）。
- **Pop Mart 是一整套 `/shop/v1/*`（39 个端点）**（R100）：`box_set/preview` → `box_set/extract` →
  `boxCart/addBoxListToCart` → `order/pre/v2/buyNow`，再加四家收银台
  `cash/desk/{adyen,alipayGlobal,paypal,stripe}/pay`。已固化为 `PopMartEndpoints`；
  replica 原来的 `/api/stock`、`/api/cart/add`、`/api/order/submit` **三个都不存在**。
- **「看起来合理、实际属于另一个家族」在本会话犯了五次**：Nike `buy/orders/v2`（R87）、
  BSTN `/api/beast`（R91）、Demandware `Checkout-Submit*`（R94）、Shopify `cart/change.js`（R96）、
  Pop Mart `/api/*`（R100）。**同一个错误五次 = 方法问题**：顺序必须是
  **先 dump 字符串、再写代码**，不是先写再找证据背书。
- **抽签链路（R99）**：镜像有 `/pages/raffle`、`<script id="panagora-raffle-data"[^>]*>(.*?)</script>`
  （逐字提取器）、`.raffle-data[data-id]`、`/api/raffle-sig`、`SaleRegistration-Config` /
  `-SignupSubmit`、`Cart-CartDrawBody`、`Already Entered Draw`。
  已落成 `DemandwareRaffle` + `DemandwareFlow.EnterRaffleAsync`。
  **关键分支：页面没有抽签数据 → `raffle=absent` 且返回成功** ——
  「没有这个功能」不等于「这个功能失败了」，否则不办抽签的店连普通结账都会挂。
- **`StepOutcome` 是 struct**：`StepOutcome?` 是 `Nullable<T>`，`return graph!` 报 CS0266，
  必须 `return graph.Value`。**`!` 只对引用类型的可空标注说话。**
- **GraphQL 已接进 `ShopifyFlow.GetCartAsync`，门开在 token 上**：有
  `shopify.storefrontToken` + `shopify.cartId` 才发请求，否则回落 `/cart.js`；
  请求失败返回 null 让调用方回落，**不把「这家店没给 token」报成结账失败**。
- **照抄也会被自己的洁癖改坏（R97）**：Shopify 的购物车查询片段在镜像里**以 `"` 开头**、
  **花括号 12 开 13 关**（它是片段，开头 `)` 关掉了 `cart(…)`，文档收尾的 `}` 在、开头的 `{` 不在）。
  写测试断言「配平」会逼着人把忠实抄本改错 —— 要显式记账，不要整齐。
- **Shopify GraphQL 链路已落代码但未接通**：`ShopifyGraphQl` 有 354/346 字符的两份逐字文档、
  四个 API 版本、`checkoutUrl` 深度解析；**没有 storefront token 就不会真调用**，这条线是 inert 的。
- **PDB 这条路断了（R96）**：`Temp\ida\Cybersole.pdb\…\Cybersole.$$$` 是 0 字节占位；
  更新包 `Cybersole-5.18.32-win-x64-full.nupkg`（57 MB / 11 条目）**不含任何 .pdb**。
  `sub_*` 换不了真名，别再找。
- **Shopify 只有两个购物车端点：`cart/add.js`、`cart/update.js`。**
  `cart/change.js`、`cart/clear.js` 在镜像里**不存在**（Shopify 文档里有，但这个二进制不调）。
  R96 已把 `ShopifyFlow` / `StoreFlow` 三处改掉，`ShopifyCartEndpointTests` 禁止它们回来。
- **镜像里有 1,182 个 `*.myshopify.com` 主机**，已逐字导出 `docs/shopify_hosts.txt`
  （进了 `verify.ps1` 文档检查 + `ShopifyHostListTests` 钉住数量/唯一/字母序/形态）。
- **换工具不如换问题（R96）**：「谁引用了这条字符串」问不出来；「这个平台用了哪几个端点」
  一次 `pe_strings` dump 就全有，而且立刻查出四个假货。
- **「字符串存在性」查得到，「谁引用了它」查不到 —— 这是死路，别再试。**
  R95 在新建的 5.18.32 库上确认三条全空：`xrefs_to <字符串地址>` = 0；
  `find type=immediate/imm/refs/ref/data` = 0；`insn_query` 找 `lea` 引用 = 扫 20 万条 0 命中
  （要整数操作数，且默认只扫 20 万条，全 `.text` 是 200 万级）。
  NativeAOT 用偏移表 + RIP 相对寻址，IDA 看不到这层关系。**要拿引用关系只能靠 PDB 或动态调试。**
- **`insn_query` 真实 schema**：`{queries:[{mnem/op0/op1/op2/op_any(整数)/func/segment/start/end/count}]}`，
  **必须带 scope**（`segment` 或 `start`+`end` 或 `func`），否则报 `Scope required`。
- **数据库运行中无法备份**：IDA 独占 `.id0/.id1`，`Copy-Item` 报「正由另一进程使用」。
  备份只能在 IDA 里打包或关闭后复制。
- **端口通了不等于能查。** R94 重载后 `/mcp` 在 IDA **刚开始加载**时就应答（`server_health: ok`），
  但 `find_regex` 要建全库字符串缓存，会死在
  `ida_mcp.sync.IDASyncError: Tool timed out after 60.00s`。
  判据是 **`auto_analysis_ready == true`**，不是端口。
  用 `python analysis/ida_wait.py [分钟]` 轮询，打印 READY 再查。
- **不用 IDA 也能取证：`python analysis/pe_strings.py <exe> <out> 8`。**
  直接从 PE 抽 UTF-16LE 字面量（129 MB → 180,228 条 → 9.3 MB 文本），不需要分析完成。
  R94 用它拿到 Demandware 全族：8 个 `Sites-*` 站点 id + 17 个真控制器名。
  **分析库是加速器，不是数据源** —— 丢了库不等于丢了内容。
- **Demandware 的四个假控制器（R94 已修）**：`Checkout-Submit` / `Checkout-SubmitShipping` /
  `Checkout-SubmitPayment` / `Cart-Show` 在镜像里都不存在，真名是
  `CheckoutServices-PlaceOrder` / `CheckoutShippingServices-SubmitShipping` /
  `CheckoutServices-SubmitPayment` / `Cart-Get`。已固化为 `DemandwareControllers`。
- **目标带 PDB 提示**：`C:\actions-runner\_work\Cybersole\Cybersole\...\net10.0\win-x64\native\Cybersole.pdb`
  —— 目标是 **.NET 10** + GitHub Actions 构建。**拿到那份 PDB 就能让 `sub_*` 变真名。**
- **IDA 数据库现在是「无」——R93 崩了一次，Repair 把 `.id0/.id1/.id2`（约 1.6 GB）删了。**
  反编译这一路归零，重建要重新自动分析 123 MB 的 NativeAOT（小时级）。
  **没有事实损失**：`NikeEndpoints` / `NikeHeaders` / `NikeFlow.Countries` / `IDB_EVIDENCE.md` /
  `NIKE_PARITY.md` / `original_view_classes.txt` 就是全部证据，二进制打不开也一样在。
- **大查询会杀死取证工具。** R93 用 `find_regex "Mozilla/5\.0" limit=400`（每条几 KB）把 IDA 插件带崩。
  以后一律 `limit ≤ 60` + 窄模式，**取完立刻备份 `.i64`**。
- **目标会自动升版。** R93 打开时 `FileVersion` 已是 **5.18.32**（原 5.18.30），
  `AppVersionTests.VersionMatchesTheOriginalBinary` 自己响了 —— 那正是 R74 加它的理由。
  已全仓 42 文件 82 处改成 5.18.32。**「1:1」永远带一个定语：对哪个版本。**
- **店铺名以「类型名 + `0x1b 0x08` 后缀」存放**，带 `$` 锚点的正则会漏掉它们；
  `^[A-Z]\w+(Handler|Tester)$` 只能确认某个店存在，**不足以枚举全部店铺**（53 条里绝大多数是框架类名）。
- **同一个店的身份也写在 User-Agent 里。** `OFFSPRING/3 … poq.ios/21.1.6 poq-webview` ⇒
  OffSpring 是 **Poq** 移动 App，不是 Magento —— replica 的 `offspring → MagentoFlow` 没有依据。
- **空结果不是「没有信息」。** R91 查 `bstn` 得到 0 条，但那 3 条命中里有
  `ARROW & BEAST` / `arrowandbeast.com` / `arrowbeast.myshopify.com` ——
  **原版有这个店而 replica 没有**，同时 replica 的 `BstnFlow` 在二进制里毫无踪影。
  补上 `arrowandbeast`（Shopify 别名），`BstnFlow` 保留（有抓包证据），两条事实都进测试。
- **「1 skipped」是最容易被忽略的绿。** 加一个模块后 `mutation-check` 的 round-164 锚点漂了，
  `verify.ps1` 只报 `23 fired, 1 skipped` —— **skipped 既不是红也不是通过**。改锚点后回到 24/0/0。
- **`-Full` 下 Analytics/Chart 一组 UI 测试会偶发红，而同样命令单跑必过。** R91 连撞三次
  （CheckoutStatsPeriodTests / AnalyticsAndModalTests / ChartTimelineTests，每次不同一条），
  清 `testhost` 后重跑 `-Full` 全绿。**是本机运行期噪音，不是回归**；判断方法永远是
  单跑该条 + 清进程重跑整轮。
- **跑测试前先清 `testhost`。** 上一次后台 `verify.ps1` 残留的 testhost 会让 18 条无关 UI 测试一起红；
  `Get-Process testhost | Kill` 后重跑即恢复。**不是代码问题，是环境残留。**
- **每取一条二进制事实，记下「这条是全的吗」。** `docs/IDB_EVIDENCE.md` 是这张账：
  事实 / 模式 / 命中 / `cursor.done` / 轮次，外加「代码常量 ↔ 数量 ↔ 哪条查询」和
  「已知取不到、别再试」。R90 复查六条全部 `done: true`（20 / 7 / 42 / 1 / 2 / 1）。
  `IDBEvidenceTests` 让文档和常量不许各自漂移；这份文档也在 `verify.ps1` 的检查清单里。
- **字符串池是字母序、跨店铺共享的。** `dump_strings.py` 的窗口摘录只能证明
  「这个字面量存在」，**不能证明「它属于 Nike」** —— `checkoutshopper-live.adyen.com`、
  `chi21120` 就和 Nike 的键挨着。
- **分页工具默认给你「一页」。** R86 用 `find_regex "Nike [A-Z]{2}"`（limit 40）只取到
  从 `IT` 开始的一段，写下「22 个市场」；R89 读掉 `cursor.done` 才看到 **42 个**（`AT`…`ZA`，
  字母序，0x28 字节间隔）。**凡是能分页的地方，「读到的」和「全部」永远是两件事。**
  后果不是「少几项」：`CountryFor("UK")` 因为「二进制没有 GB 市场」回落到 US，
  **把英国用户送去美国结账**，而且还有一条测试把错误钉住了。
- **测试保证「代码和信念一致」，不保证「信念和原版一致」。** 那条
  `Assert.Equal("US", CountryFor("UK"))` 在错误事实上完全正确地运行。
- **Nike 14 步的子路径：当前证据不可达，别再试。** R88 三条路都走到头：
  ① 20 个 URL 是连续存放的一张表，邻域没有 `/shipping_address` 之类碎片；
  ② `find_regex "(shipping_address|/shipping|…)"` 命中的全是别的店；
  ③ **修复后的 IDA 库里函数名全是 `sub_140xxxxxx`**（`func_query name_regex` 返回空），
  `NIKE_PARITY` 里那 14 个名字来自**字符串**里的 `d__N` 状态机名，不是符号。
  → 除非拿到运行期抓包，这一层没有更多可挖的。
- **Nike 的标识是 7 个不是 4 个。** `find_regex "nike-[a-z-]+"` + 两个大写拼法：
  4 个 header（`nike-api-caller-id` / `x-nike-ux-id` / `x-nike-visitid` / `x-nike-visitorid`）
  ＋ `Nike-Kasada-Version` ＋ 2 个 cookie（`NIKE-SESSION` / `NIKE-GS`）。
  已固化为 `NikeHeaders`，`GetSessionAsync` 按 session var **只发已知值**（不编默认值）。
- **IDA 关掉之后的重开流程（R87 实测）**：`ida-mcp-doctor.ps1 -Path Cybersole.exe`
  → 弹「数据库已存在」→ 点 **加载现有(L)** → 再弹「not closed, repair?」→ 点 **Repair**
  → 「请稍候…」约 2 分钟（1 GB 的 `.id0`）。doctor 自己会在 180 s 超时退出，**没关系**：
  IDA 活着就行，之后直接用 `python analysis/ida_mcp.py health / call …`。
  修复完成后 `auto_analysis_ready` / `strings_cache_ready` 会先是 false，`find_regex` 仍可用。
- **`find_regex "api\.nike\.com"` = 20 条，这就是 Nike 端点的全集。** 已固化为
  `Cybersole.Stores.Flows.NikeEndpoints`。**replica 用的 `buy/carts/v2/…` 与 `buy/orders/v2/…`
  在二进制里根本不存在**；真实形状是单个 `buy/checkouts/v3/{checkoutId}` 资源，14 步往它上面写，
  但每步的子路径是拼接的、没有字面量，**因此仍无证据**。见 `NIKE_PARITY.md` 第 12 节。
- **常量装不下「每个任务不一样」的东西。** Nike 的 `const string Marketplace = "US"` 让
  22 个市场变成一个：无论 profile 写哪国都只能在美国结账。改成实例字段 `CountryCode` 后，
  **静态方法 `CartUrl()` 立刻编译失败** —— 编译器比人先发现「常量没了，静态也就没了」。
- **映射错了比没有映射更糟。** `NikeFlow.CountryFor` 只认二进制的 22 个市场，`UK`/`DE`/`CN`
  一律回落 US，**不凭空发明市场**——否则请求会打到一个 API 从没被问过的地方去。
- **画在屏幕上的控件 = 对用户的承诺。** R84 我给 `AccountTable` 的表头画了 `⇅`，而它不排序 ——
  **上一轮修别人的死按钮，这一轮自己造了一个**。R85 把表头改成 `Button` + `SortBy()`：
  同列再点反向、换列升序、箭头 `↑/↓/⇅` 跟着变，`Ordered()` 是纯函数供测试打。
- **测试绑在实现形状上是好事。** 表头从 `TextBlock` 改成 `Button` 后，R84 的两条断言当场抛
  `First()` —— 不是脆弱，是**它正确地指出这是行为变化，不是重构**。
- **拼字符串的界面永远长不出第二列。** R84 前三个账户页的数据是
  `$"{a.Host}    {a.User}    {a.InboxCount}"` —— PayPal 那行甚至把
  `running=… refreshed=…` 印在界面上。改成 `string[]` 由 `AccountTable` 按列切格，
  **数据不再为了显示而成型**。
- **`IsVisible` 在容器上，不在文字上 —— 这件事撞了两次。** R79 空态一次、R84 表头一次。
  断言「某块不见了」一律走祖先链找 `IsVisible=false`。
- **`Window` 子类不能在无头测试里构造。** `new StoreCreatorView(...)` 抛
  `Unable to locate 'Avalonia.Platform.IWindowingPlatform'`。要测这类弹窗，**读源码断言形状**
  （标题常量 / 字段行 / 按钮文案 / 没有 Save-Close），或另建一个 headless 平台。
- **「本来就有」不等于「本来就对」。** R82 说「让手搭弹窗改用已有类」，R83 一看：
  已有的 `StoreCreatorView` 是 Name+URL+Save/Close，`SizeCreatorView` 是 33 个硬编码尺码勾选表
  —— 两个都是自己想的，和原版对不上。**正确动作反过来：把证据搬进旧类，删掉手搭那份。**
  为了「消除重复」而把一个错的实现变成唯一实现，比两份都错更糟。
- **原版会掉回登录页。** R82 打开时窗口已关、进程已无；重启后停在 `Cybersole.exe … "Login"`。
  **没有凭据就没有 Settings**，GUI 这一路证据当场失效。所以：**能落成文字快照 + 断言的
  东西要尽早落**（R74–R81 抄下的字符串，现在就是「原版再打不开也还在」的东西）。
- **视图类普查是免费的函数数量口径。** 二进制 Avalonia 资源清单的
  `ClassToResourcePathIndex` 有 **87 条**（类名 + .axaml）。快照存 `docs/original_view_classes.txt`；
  实测 **69 同名 / 12 改名合并 / 6 真没有**（`SplashWindow`、`LoginControl`、`CustomBrowser`、
  `EmptyView`、`GroupGrid`、`ProxyCreatorView`）。守卫在 `OriginalViewClassParityTests`，
  欠账清单只准变短。
- **同一个对话框可能有两份实现。** 资源清单里有 `Settings/Modals/StoreCreatorView.axaml` 与
  `SizeCreatorView.axaml`，而 replica 的 `SettingsModals.cs` 早就有 `StoreCreatorView` ——
  R79/R80 在 `CustomStoresView`/`CustomSizesView` 里手搭的同名弹窗是**第二份**。
  下一轮先让手搭的那两个改为使用已有类。
- **`scroll` 对这一层 Avalonia 窗口无效**（后台上报 `Background delivery is not available … mouse_scroll`）。
  必须给**列表内的像素坐标 + foreground**：`app.scroll([900,700], "down", 4, {delivery_mode:"foreground"})`，
  否则滚轮事件被丢掉，列表一动不动而你以为是「到底了」（R81 一开始就因此少收了 3 条）。
- **整份数据做完不等于功能做完。** R81 发现 `ErrorCatalog` 里躺着 13 条逐字抄来的错误说明，
  而 `HelpView` 的注释写着「没有错误索引可搜」—— **一份没人渲染的目录，和一份没写过的目录，
  在屏幕上完全一样。**
- **`ChartTimelineTests.AnalyticsViewOffersFourCharts` 偶发红**（R81 的 `-Full` 见过一次，单跑必过，
  重跑 `-Full` 全绿）。属于共享 UI 状态的偶发，不是回归。
- **同一个 Settings 页面对了之后，隔壁那页通常是同一份模板换一列。** R79 把 Custom Stores
  改成「表 + 弹窗」，R80 发现 Custom Sizes 是同一个形状（单列 + `Add Size(s)` 带括号），
  先找模板再补差异，比从零开始便宜得多。
- **「不知道」的代价有时只是多点一下。** R79 留着 Custom Sizes 不动的原因是「没点过那个弹窗」；
  R80 点开了，四个字串一目了然。**能点就点，别把它留成悬念。**
- **「不在屏幕上」≠「不在逻辑树里」。** Avalonia 用 `IsVisible=false` 让控件消失，它仍然是子节点。
  断言「空态消失」必须走祖先链找 `IsVisible=false`（R79 一条断言写错三次），
  而且 `IsVisible` 标在**包着它的容器**上，不在文字本身。
- **能干活不等于一样。** R79 把 replica 自己那套「表单摊在页面上」的 Custom Stores 删了，
  换成原版的「表 + 弹窗」。功能没变、形状变了——这才是 1:1 的标准。
- **界面上的每个控件都要能指出「另一端接着谁」。** R78 查出 Notifications 页的 Sounds 开关、
  声音文件、以及页面级的 `settings.notifications` **全都没有读者**：`NotificationService`
  只弹窗、记日志、发 webhook，从不播放。现在有 `ISoundPlayer`（winmm `PlaySound`，无 NuGet）、
  `NotificationService.PlaySound`，`PublishAsync` 按 `Notifications → Enabled → Sound → Path` 逐层判。
- **开关（ToggleSwitch）不是复选框（CheckBox）。** 原版这一页每行都是右侧绿色开关；
  用 `UiKit.Check` 是不同控件、不同位置。`UiKit.Switch(caption, value, onChanged)` 是对的形状，
  而且文字是 `TextBlock`，测试能扫到。
- **原版的下拉框在 UIA 里没有 peer。** `role:combobox` 查不到，像素点击的正确姿势是
  「截图坐标 ÷ (窗口宽/截图宽)」——驱动会把传入值再乘一次缩放（R77 实测 1.1288）。
  即便如此，点中之后**弹层不会出现、也没有新 HWND**。所以「下拉框里有哪些选项」
  这一层证据目前取不到，不要写成「大概是……」。
- **`Enum.GetNames<T>()` 不能直接当界面文案。** R77 屏幕上出现 `RoundRobin`，原版是
  `Round robin`。给枚举字段的页面一律走显式显示名表。
- **`t.find(x)` 回答的是「x 第一次在哪」，不是「我要的那个 x 在哪」。** R76 的改写脚本用
  `find('Content = UiKit.Scroll(UiKit.Form(')` 定位，命中的是 `GeneralSettingsView` 的那一行，
  于是从那里到目标注释之间的 **600 行被替换掉**：AppearanceView、NotificationsView、
  KeyBindsView 整个没了，本仓库没有 git、没有备份目录。
  **补得回来是因为 R74/R75 一轮一轮抄过那三页的文字——那是唯一的备份。**
  重写脚本时用「两段唯一锚点 + assert 都在同一函数内」，或者先 grep 出全部出现位置。
- **只写状态行、什么都不打开的按钮/菜单项 = 一定有一个是错的。** R74 的版本号：AppVersion.Current 写 5.18.28，
  SettingsShell.DisplayVersion 写 5.18.32（从 GUI 抄的），二进制是 5.18.32。
  集中成常量不会校验它。**现在有守卫直接读 FileVersionInfo 比对。**
- **页头是 shell 的装饰，不是每页自己画的**，而且左栏名和页头名可以不一样
  （Captcha Providers vs 3rd Party Captcha Providers）。**那不是 bug，别统一。**
- **只写状态行、什么都不打开的按钮/菜单项，会被 `DeadButtonTests` 拦下**（R73 的
  `Open In Browser`）。没有实现就不要注册，并记进 `PARITY.md`。
- **`ColumnDefinitions` 里写 `Auto` 的那一列，在表头和数据行里算出来不一样宽**（R72）。
  表头那一列装着工具栏，数据行那一列是空的，于是左边所有星号列在两个 Grid 里分到的宽度不同，
  **表头和数据错位**。判据：表头和数据行必须用同一份固定像素的模板。
  连带的第二个坑：固定宽度给小了，按钮上的字被裁成 `Clear Accou...`。


### 编码

- **`Get-Content` 把 UTF-8 读成 ANSI**（中文变乱码）。用 Python `io.open(..., encoding='utf-8')`。
- **PowerShell 5.1 的 here-string 会吃 `\$` 和中文**。复杂脚本写成 `.py` 文件再跑。
- **`.ps1` 必须带 BOM**（否则 5.1 把 `失败` 解码成乱码，正则永远匹配不到）。

### 子串匹配（四次）

```
R64  new ProfileGroupView(   命中  new ProfileGroup
R65  "Move accounts to"      找不到 "Move To…"（label 和 locale 文本不同）
R67  注释里的旧写法          被当成代码
R67  注释里的示例            被自己的测试数进去
```

**用词边界 / 结构化比对，不要 `Contains`。判断「这个字段有没有被引用」时尤其危险。**

### 手写列表（三次，三个受害者）

```
R63  ProfileViews.Clone      13/37 字段   → 丢 4 个卡字段，结账跑不了
R63  BillingView.Clone       24/37 字段   → 和上面互相不一致
R65  TasksViews.CloneTask    有 StartTime → 克隆的任务看起来已经在跑
```

**`MemberwiseClone` 不是更聪明的写法，是不用再维护的写法。**
**但换成自动版本时，先问当初为什么不一致**（R68 就是没问，丢了一个后缀）。

---

## 八、孤儿这个词，现在有七种形态

```
R180  事件：声明了、raise 了、没人订阅
R185  类型：声明了、编译过、没人 new        ← ProfileGroup（R64）
R198  标签：有 label、没字段                ← 8 个，R51 解决 1 个
R409  字段：有字段、没人读                  ← ShopifyBrowserProxy / Profile.ProxyGroupId（R69）
R411  两半：label 在 A、字段在 B，互不相识   ← ATCBrowserProxy / ShopifyBrowserProxy
R55   列表：有集合、只 Add、没 ItemsSource   ← AccountLines（我自己造的）
R56   同上，第二次                          ← ProxyLines（我自己造的，一个 round 后）
R70   双份状态：两份同类状态并存，动作只读其中一份
        ← 原版账户表的行复选框 vs 行选择集。三行打勾、右键一行，
          菜单写「1 ACCOUNTS SELECTED」、也只复制一行。复选框是装饰
R71   悬空控件：造了、接了事件、暴露了属性、属性值全对，**没进任何容器**
        ← CreateGroupModal 的 Add Group。对话框只有 Close，单测全绿
```

**第八种比前七种更阴**：前七种能靠「有没有人读」找出来，第八种两个字段**都有人读**——
只是一个读在画面上、一个读在动作里。**只有点下去才会发现它们不是同一个东西。**

**第九种（R71）比第八种更阴**：它连「有没有人读」都通过了——属性被读、逻辑被断言、
`IsEnabled` 被检查。**唯一没发生的事是「它没被画出来」。**
判据只有一条：**问它有没有 parent。**

**修完一处，检查刚才那处有没有变成孤儿。**

