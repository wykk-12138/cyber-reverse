# 已知差异清单（复刻件 vs 原版 5.18.32）

这份文档只列**已知且被接受**的差异，每条都写清"为什么接受"。缺口数字与它不是一回事：
缺口是"还没做"（**当前值见 `docs/METRICS.md`**），这里是"决定不做或无法做"。

---

## 一、绑定形状：动作是方法，原件是 `ICommand` 属性

| 项 | 值 |
|---|---|
| 有访问器证据的成员 | 465（可写 327 / 只读 138） |
| 形状不一致 | **见 `docs/METRICS.md`**（`python tools/shape_audit.py`） |

**为什么接受**：复刻件没有任何 XAML 绑定，动作就是方法，行为等价。
**新规则**：新增动作成员写成 `ICommand` 属性（`docs/METHOD.md` §13）。

---

## 二、UI 结构：少两处、多两处

| 位置 | 差异 | 依据 |
|---|---|---|
| Group Settings | 原件 4 个 tab，复刻件曾多 `General`/`Manual` → **R353 已删** | locale `TaskGroup.Tab.*` 只有四个 |
| `Pinned` / `Order` | 已从该弹窗移除（`Pinned` 属 `TaskView.PinGroups`、`Order` 属 `Settings.TaskGroupOrder`） | 同上 |

---

## 三、文案与 URL

| 项 | 状态 |
|---|---|
| `UserView` 的 `TermsUrl` / `PrivacyUrl` | **inferred**：实机有按钮、没给链接目标 |
| GOAT 的 `/v1/buys` 等三条路径 | **inferred**：池子里查不到出处（该店只有 5 条 `web-api/` 路径有出处，且已全部用上） |
| 4 条 cookie / 4 条查询参数 | **inferred**：无镜像证据，逐行标注 |
| `Settings.Webhook.ExtraFields` 的界面位置 | 未知（属性是真的，5 个 locale 键为证） |

---

## 四、不可得（三源否证）

| 项 | 说明 |
|---|---|
| `Platform.InputType` / `QuantitySupport` / `QuantityAutoAdjustSupport` | **R465 推翻**：`Cybersole.Attributes.Platform` 在描述符表里 get=5 set=5，这三个（连同 `MultiCart`/`Name`）**全部 readwrite** —— 原判"池子只有名、下拉点不开、locale 无 `Platform.*`"三个来源都不覆盖描述符表 |
| `User.IsStaff` | **R465 推翻**：`Cybersole.Models.User` get=6 set=5，`IsStaff` 是 **readonly** 成员 —— 原判"需账号角色信息，本地无来源"只说明**行为**无据，不说明成员不存在 |
| `SettingsView.Transition` | **R463 订正**：原版绑定描述符表里 `Cybersole.Ui.Views.Settings.SettingsView` **19/19 命中，含 `Transition`** —— 它不是不可得，而是**复刻件未实现的一个真成员**。原判无证据说明它控制什么仍对行为成立（表只证明它被绑定），但对是否存在已不成立 |
| `AnalyticsView.OpenRelease` | 无 release 目录、无浏览器服务（**R465 未逐条核描述符表，仍记为待定**） |

> **R465 整节订正**：这一节原来的意思是"三个来源都查过，成员不存在或无据"。但原版把编译期绑定描述符
> 以可读串摊在字符串池里（`analysis/binding_descriptors.py`，215 类型 / 1,637 条），
> **是第四个来源，而且它比前三个都权威**：它是原版自己声明的绑定表。
>
> 用它核对的结果：`Platform` 那三个、`User.IsStaff`、`SettingsView.Transition`、`Store.ColorSupport/Elements`
> **全部在表里**，且多数可读写。所以它们不是"不可得"，是**复刻件未实现**。
>
> 这一节现在只剩一件事不可得：**拿不到"复刻件该怎么做"的依据（行为未知）** ——
> 而"原版有没有这个成员"已有确定答案：**有**。

---

## 五、故意留白（绑定表有名、行为未知）

`TaskView`：`CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle`
（R349 找到文案线索："Mass Link Change"、"Launch Quicktask"）

`CreateModel`：`Input` `Inputs` —— **类型不可推断**
`BotTask`：`Task` —— 类型不可推断，且与 `System.Threading.Tasks.Task` 同名
`SmartActionsView`：`Clock` `Export` · `GroupSummary`：`Clone` `Delete` `Edit` ·
`HistoryWindow`：`SmartAction` `View` · `GoogleAccountsView.Edit` · 两个自定义页的 `View`

---

## 六、类型级缺口

`python tools/bind_scope.py` —— 成员没长在该类型上。**当前缺口类型与成员逐个列在 `docs/METRICS.md`**
（本文件不复述数值）。剩余的几条大多是上面的"留白"项；`Profile.Card/Username`、`ProxyTester.Name`、
`SmartActionsView.Export` 三条已按 R433 裁决写成 Unknown 结案，见 `docs/PARITY_CLAIMS.md` §5。

---

## 七、怎么用这份文档

判断"是否 1:1"要分三层看：

1. **行为**：套件全绿（数字见 `docs/METRICS.md`）；8 条字面量流程可对账；错误目录逐字命中 → **这一层最实**；
2. **结构/文案**：七页实机核对，发现的四处差异已修 → **次之**；
3. **形状**（命令属性 vs 方法、tab 数、控件位置）→ **有意保留差异，见上文**。


---

## 八、复刻件比原版多写的四个设置项（R390）

原版自己写的备份（`Backups/Backup 14 Nov 08h01m.cyb`）里 `settings` 有 **44** 个键，复刻件的
`GlobalSettings` 有 48 个属性 —— 全部 44 个都在，另外 **4 个原版没有**：

| 属性 | locale 有吗 | 判断 |
|---|---|---|
| `EnableClock` / `ClockFormat` | `Settings.General.EnableClock` = "Enable clock" | 原版持久化的只有 `clock`（int，备份里是 0）。这两个可能是复刻件从 locale 反推出来的 |
| `MonitorConcurrency` | **有**（`Settings.General.MonitorConcurrency.Both` / `Maximum` / `MaximumDesc` / `Ratio` / `RatioDesc`，见 `SettingsShell.cs`） | **不是发明，已订正（R442）**：`Cybersole.Global.Settings` 的绑定成员列表里就有 `MonitorConcurrency`（`docs/xaml_bindings.json`），复刻件的 `GlobalSettings.MonitorConcurrency` 与之对应。原表把 locale 列写成"无"也错了。查法：`python tools\member_owner_map.py --type Settings` 给出唯一归属 |
| `StoreGroups` | 无 | 原版有 `customStores` / `customSizes`；复刻件的 `StoreGroupModal.Delete` 用的是这个集合 |

**为什么先不改**：删掉会连带去掉界面功能（时钟开关、分组管理），而"原版不持久化"不等于"原版没有"。
先把差异记下来，等 IDA 恢复后从反编译里定。

> **R442 订正**：上面三行用同一个标准重查了一遍 —— **"绑定表里有没有这个成员"**
> （`Cybersole.Global.Settings` 的成员列表：`... MonitorConcurrency, MonitorDelay, MonitorFilters, ...`）。
> - `MonitorConcurrency` **在**绑定表里 → 不是发明，已按上面那行订正；
> - `EnableClock` / `ClockFormat` **不在**绑定表里（表里只有 `Clock`）→ "复刻件从 locale 反推"的判断仍成立；
> - `StoreGroups` **不在**绑定表里 → 同样成立。
>
> 也就是说：四条里三条经得起查，一条被查翻了。**这就是把判断写成可复核条件而不是结论的价值。**

**现状**：这四个会被写进 `settings.json`。原版读到不认识的键通常忽略，所以不影响互通，但它们是**多余字节**。

---

## 九、已知口径：`bind_scope.py` 计入基类继承（LOOSE）

`python tools/bind_scope.py` 判"成员在不在该类型上"时，会**沿继承链合并基类 body**。
这是**正确口径**，理由两条：

1. XAML 绑定本来就沿继承链解析 —— 原版把 `Close` 绑在 `WebhookCreatorView` 上，实际由基类实现也完全成立；
2. `bind_scope.py` **自 R343 起**就是这么设计的（源码注释原文：`members inherited from a base are not missing`），
   不是后期放宽。

**因此下列 8 个类型是"纯靠基类通过"的，不计为缺口**（R433 用"不合并基类"的严格版实测得出）：

| 类型 | 靠基类满足的成员 |
|---|---|
| `AycdInboxCreatorView` | `Close` |
| `CaptchaProviderCreatorView` | `Close`, `Delete` |
| `Checkout` | `Profile`（继承自 `Profile` 的成员） |
| `CloudflareSolverCreatorView` | `Close`, `Delete` |
| `GoogleAccountEditView` | `Close` |
| `ImapCreatorView` | `Close` |
| `PayPalAccountCreatorView` | `Close` |
| `WebhookCreatorView` | `Close` |

严格版（own body only）会把这些报成缺口，得 12 个类型；**不要把 12 当缺口数**。
脚本输出末尾已加一行 `note: base-class inheritance is counted (by design since R343)`，
以后不必再问第二次。

---

## 十、死代码：27 个 src/ 侧零引用类型（R457）

用「声明的类型名在 src/ + 	ests/ 的其它位置是否出现过」扫描（排除泛型实参、排除声明行本身）：

- **测试类**约 80 个零引用是正常的（xunit 靠反射发现），不算。
- **src/ 侧真正零引用的有 27 个**，其中 **21 个是 store 模块类**：
  CasioModule、EndClothingModule、FanaticsModule、FootpatrolModule、FootsitesModule、
  HypeCommerceModule、JbHiFiModule、JdSportsModule、JohnLewisModule、KithModule、NotreModule、
  OffspringModule、PocketGamesModule、PopMartModule、RaffleModule、RiotGamesModule、SizeModule、
  SnsModule、SuperswipeModule、SupremeModule、WarhammerModule、YeezySupplyModule。

**它们不是功能缺失。** 注册表 CreateAll() 用的是 
ew FlowStoreModule(new XxxFlow())，
22 个模块**全部**都有对应的 XxxFlow 且都在注册表里（逐个核对过）。所以这 21 个类是
**Flow 架构取代模块类之后留下的旧实现**：行为由 Flow 承载，类本身没有任何调用点。

其余 6 个零引用：Ja3StreamExtensions、ProxyExtensions、TimeSpansExtensions、
Tls12FlightReader、WebTask 等扩展/辅助类。

**影响**：它们会被编译进产物（占一点体积与函数数），并且在阅读代码时制造「这里还有一条实现路径」
的错觉。**处置**：本轮不动它们（R352 删类导致过回滚，删之前要单独一轮 + 完整验证）；
先把清单记下来，需要瘦身时按这份清单处理。

**这不是「结构对等但行为不存在」的漏洞**，而是**同一能力存在两套实现、只有一套被接线**——
正好是纪律里那句「只能证明属性存在的成员，行为必须记 Unknown」的镜像：属性在，调用点不在。
