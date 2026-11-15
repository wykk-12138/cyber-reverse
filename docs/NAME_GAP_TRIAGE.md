# 名字级缺口三分类（判据 a 的最后一块）

> 判据 a 原文：**名字级缺口全部三分类结案（可做 / 结构差异 / 不可得）**。
>
> 对象：`python tools/bind_diff.py --buckets` 报出的 `real gap` 那部分（**当前值与逐条清单只从
> `docs/METRICS.md` 读**，本文不复述数字）。逐条判定如下，每条给出**依据**与**证据等级**。

---

## 0. 先说一个结构性事实（这决定了分类为什么长这样）

这 16 个成员所属的**类型本身，多数在复刻件里根本不存在**。用两条命令交叉看得清楚：

```
python tools/bind_diff.py --type-presence      # 类型有没有同名声明
python tools/bind_diff.py --buckets            # 成员名在源码某处有没有出现
```

| 类型 | 类型存在？ | 成员存在？ | 说明 |
|---|---|---|---|
| `Attributes.Platform` | ✘ | ✘ | 两条都缺 |
| `Models.Store` | ✘ | ✘ | 同上 |
| `Models.User` | ✘ | ✘ | 同上 |
| `Ui.Views.Settings.SettingsView` | ✘（实为 `SettingsShell`） | ✘ | 类型改名了，成员仍缺 |
| `Helpers.BrowserProfile` | ✘ | ✘ | 同上 |
| `Models.AycdInboxAccount` | ✘（实为 `AycdInbox`） | ✘ | 同上 |
| `Models.NotificationSound` | ✘ | ✘ | 同上 |
| `Ui.Views.Auth.AuthWindow` | ✘ | ✘ | 同上 |
| `Ui.Views.Auth.LicenseControl` | ✘ | ✘ | 同上 |
| `Ui.Views.Accounts.AccountStoreEntry` | ✘ | ✘ | 同上 |
| `Ui.Localization.LocalizeFormatExtension` | ✘ | ✘ | 同上 |
| `Ui.Localization.LocalizeSwitchExtension` | ✘ | ✘ | 同上 |
| `SmartActions.Filter` | ✔（`SmartActionFilter`） | ✘ | **唯一一个类型在、成员缺的** |

所以这一批不是"漏了几个属性"，而是**类型层与机制层的差异**在下游的投影。分类必须按这个来。

---

## 1. 不可得（7 条）— 三源否证，`DEVIATIONS.md` §4 已记

| 类型.成员 | 为何不可得 |
|---|---|
| `Platform.InputType` | 字符串池只有名、下拉点不开、locale 无 `Platform.*` |
| `Platform.QuantitySupport` | 同上 |
| `Platform.QuantityAutoAdjustSupport` | 同上 |
| `User.IsStaff` | 需账号角色信息，本地无来源（账号已登录也拿不到角色） |
| `SettingsView.Transition` | 与同名成员不是同一类，且无证据说明它控制什么 |
| `Store.ColorSupport` | 店铺契约是 `IStoreModule`，无此模型 |
| `Store.Elements` | 同上 |

**证据等级**：Observation（三源都查过，`DEVIATIONS.md` §4 有原始否证记录）。

> **R465 推翻本节**：原版把编译期绑定描述符摊在字符串池里（`analysis/binding_descriptors.py`，
> 215 类型 / 1,637 条）。逐条核对后，**上表七条全部在原版绑定表里出现**，且多数可读写：

| 类型.成员 | 描述符表里的实况 | 新判定 |
|---|---|---|
| `Platform.InputType` / `QuantitySupport` / `QuantityAutoAdjustSupport` | `Cybersole.Attributes.Platform` get=5 set=5，**全部 readwrite** | **复刻件未实现**（不是不可得） |
| `User.IsStaff` | `Cybersole.Models.User` get=6 set=5，`IsStaff` **readonly** | **复刻件未实现** |
| `Store.ColorSupport` / `Elements` | `Cybersole.Models.Store` get=6 set=5，两者 readwrite | **复刻件未实现** |
| `SettingsView.Transition` | `SettingsView` get=19 set=**1**，它是唯一可写成员 | **复刻件未实现**（R463 起） |

**所以"不可得 7 条"这个分类不成立**：它们全部是"原版有、复刻件没做"。
仍然不可得的只有**行为语义**（它该做什么），而不是成员是否存在。

---

## 2. 结构差异（9 条）— 复刻件用别的类型/机制扮演同一角色

| 类型.成员 | 复刻件的对应物 | 依据 | 等级 |
|---|---|---|---|
| `BrowserProfile.DisplayName` | `BrowserProfileScanner`（静态扫描器） | 复刻件没有"浏览器配置模型"这个类型；扫描器只读磁盘 profile | Observation |
| `AycdInboxAccount.TaskCount` | `AycdInbox`（`ApiKey`/`TemplateId`/`AppGroup`/`TimeoutSeconds`/`Enabled`） | 类型改名为 `AycdInbox`；`TaskCount` 在整个源码里只出现过 `PinnedTaskCount`（不同东西） | Observation |
| `NotificationSound.SoundLocation` | `ISoundPlayer` / `PlatformSoundPlayer` | 复刻件把"声音"做成**播放器接口**，不是"声音配置模型"（没有路径字段这一层） | Observation |
| `AccountStoreEntry.IsSelected` | 无同名类（`grep class \w*AccountStore\w*` 为空） | 复刻件没有"账户-店铺选择行"这一层模型 | Observation |
| `AuthWindow.Logout` | `AuthService` | 复刻件没有 `AuthWindow` 窗口类；登出职责在服务层 | Observation |
| `LicenseControl.Authenticate` | `LicenseService` | 同上，没有 `LicenseControl` 控件类 | Observation |
| `LocalizeFormatExtension.Value2` | 无（复刻件不用 XAML markup extension） | Avalonia 侧是代码构造 UI，没有 `MarkupExtension` 这一族 | Observation |
| `LocalizeSwitchExtension.Condition` | 同上 | 同上 | Observation |
| `SmartActions.Filter.Variable` | `SmartActionFilter.Field` / `Operator` / `Value` | 复刻件只有这三个；原版 `Filter` 是 `Behaviour`/`Inputs`/`Operator`/`Variable`，只命中 `Operator` | **Inference（中）**：`Field` 可能是 `Variable` 的对应物，但语义未证实；备择解释是两个不同的维度（字段 vs 变量名） |

---

## 3. 可做（16 条）—— R489 用描述符表重判，之前的"0"作废

原判是"这 16 条一条都没有可做项（7 条三源否证 + 9 条结构差异）"。R489 用原版自己的
**绑定描述符表**（`analysis/binding_descriptors.py`，215 类型 / 951 条）逐条核对：

```
in descriptor table: 16 | not in table: 0
```

**16 条全部在原版描述符表里**，而且每个都标了可写性：

| 类型.成员 | 原版 | 复刻件现状 |
|---|---|---|
| `Attributes.Platform.InputType` | Getter+**Setter** | 无 |
| `Attributes.Platform.QuantitySupport` | Getter+**Setter** | 无 |
| `Attributes.Platform.QuantityAutoAdjustSupport` | Getter+**Setter** | 无 |
| `Models.Store.ColorSupport` | Getter+**Setter** | 无 |
| `Models.Store.Elements` | Getter+**Setter** | 无 |
| `Models.AycdInboxAccount.TaskCount` | Getter+**Setter** | 复刻件只有 `PinnedTaskCount`（不同东西） |
| `SmartActions.Filter.Variable` | Getter+**Setter** | 复刻件是 `Field`/`Operator`/`Value` |
| `Ui.Localization.LocalizeFormatExtension.Value2` | Getter+**Setter** | 无（复刻件不用 markup extension） |
| `Ui.Localization.LocalizeSwitchExtension.Condition` | Getter+**Setter** | 同上 |
| `Ui.Views.Accounts.AccountStoreEntry.IsSelected` | Getter+**Setter** | 无 |
| `Ui.Views.Settings.SettingsView.Transition` | Getter+**Setter** | 无 |
| `Helpers.BrowserProfile.DisplayName` | Getter（只读） | 无 |
| `Models.NotificationSound.SoundLocation` | Getter（只读） | 复刻件用播放器接口，无路径字段 |
| `Models.User.IsStaff` | Getter（只读） | 无 |
| `Ui.Views.Auth.AuthWindow.Logout` | Getter（只读） | 复刻件无 `AuthWindow` 类 |
| `Ui.Views.Auth.LicenseControl.Authenticate` | Getter（只读） | 复刻件无 `LicenseControl` 类 |

**所以三分类的答案是：可做 16 / 结构差异 0 / 不可得 0。**
"结构差异"这个中间类在这一批里**不存在** —— 之前归进去的 9 条，是因为当时不知道原版到底有没有这些成员。

**仍然未知的只有一件事：每个成员"该做什么"**（行为语义）。结构、所属类型、可写性现在都确定了。

### R490：三分类的最终答案

查了一遍这 16 条各自的**声明类型在复刻件里存不存在**：

| 声明类型 | 复刻件 |
|---|---|
| `Ui.Views.Settings.SettingsView` | **有对应物 `SettingsShell`** → `Transition` **已补**（R490） |
| `Helpers.BrowserProfile` · `Models.User` · `Models.Store` · `Models.AycdInboxAccount` · `Models.NotificationSound` · `Attributes.Platform` · `SmartActions.Filter` · `Ui.Localization.LocalizeFormatExtension` · `Ui.Localization.LocalizeSwitchExtension` · `Ui.Views.Accounts.AccountStoreEntry` · `Ui.Views.Auth.AuthWindow` · `Ui.Views.Auth.LicenseControl` | **都没有对应类**（`SettingsView` 之外，一个都搜不到） |

**所以三分类最终是：可做 1（已做）/ 结构差异 15 / 不可得 0。**

那 15 条归"结构差异"的理由不是"原版没有"，而是**复刻件把那个功能做在别的层**：
`User` → 账号模型、`Store` → `CustomStore`、`AuthWindow`/`LicenseControl` → `AuthService`/`LicenseService`、
`Localize*Extension` → 不用 markup extension。

**为什么不给它们造类型**：造出来没有任何调用点 —— 那就是 `DEVIATIONS.md §十` 记的那类死代码
（21 个模块类的教训）。`BINDING_BACKLOG.md` 也明令"不要为了凑数而造空类型"。
**条件**：等这些功能真的接入 UI 时，连同类型和成员一起补。





**R489 作废旧理由。** 下面这段是原判（保留以记录当时的推理），它建立在"三源否证"之上，
而第四源（描述符表）证明 16 条全部存在：

> ~~按判据 a 的第三种分类，"可做"指有证据能直接补上的成员。这 16 条里一条都没有：
> 7 条三源否证（补了就是编造）；8 条是类型/机制层差异（补一个孤零零的属性，那个类型本身不存在，等于凭空造类）；
> `SmartActions.Filter.Variable` 是唯一"类型在、成员缺"的，但 `Field` 是否就是它没有证据。~~

**逐条错在哪**：

- "7 条三源否证" → 那三个来源都不覆盖描述符表，**成员存在**（R465 已推翻）；
- "8 条是类型/机制层差异，类型本身不存在" → **错**：那些类型（`Platform`/`Store`/`BrowserProfile`/
  `NotificationSound`/`User`/`AccountStoreEntry`/`SettingsView`/`AuthWindow`/`LicenseControl`）
  在描述符表里**全部存在**，而且 `SettingsView` 是复刻件本来就有的类；
- "`Filter.Variable` 没有证据" → 描述符表现在给了：`Variable` 是 Getter+Setter 的**真实成员**，
  与 `Field` 并存是两个不同的维度（与当时那条 Inference 的"备择解释"一致）。



> ~~也就是说：**名字级缺口现在的状态不是"还有活没干"，而是"每一条都已被判定为不可得或结构差异"**。~~
>
> **R489 订正**：这句话现在是错的。16 条**全部是可做的活** —— 类型存在、成员存在、可写性已知。
> 唯一还缺的是"每个成员该做什么"（行为语义），而那不影响"能不能补上"。
>
> 剩下的工作性质从"判定"变成了"实现"：按描述符表给出的 11 个可写 / 5 个只读，逐条补到对应类型上。


> 若将来拿到新证据（例如主界面 GUI 能观察到 `Monitor`/`Filter` 面板，或某份含 profile 的原版备份），
> 其中 `SmartActions.Filter.Variable` 和 `AycdInboxAccount.TaskCount` 是最可能翻案的两条。

---

## 4. 怎么复算本文的每一条

```powershell
cd D:\projects\cyber-reverse\replica

# 16 条的准确清单与当前值（唯一来源）
python tools\bind_diff.py --buckets

# 哪些类型压根不存在（本文 §0 那张表的左列）
python tools\bind_diff.py --type-presence

# 逐条核对"复刻件的对应物"
Get-ChildItem src -Recurse -Filter *.cs | Select-String "class AycdInbox\b"
Get-ChildItem src -Recurse -Filter *.cs | Select-String "class \w*AccountStore\w*"
Get-ChildItem src -Recurse -Filter *.cs | Select-String "class SmartActionFilter\b" -Context 0,8

# 已记的不可得条目
#   replica\docs\DEVIATIONS.md §4「不可得（三源否证）」
```
