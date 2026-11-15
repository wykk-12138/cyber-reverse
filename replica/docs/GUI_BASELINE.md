# GUI_BASELINE — 从运行中的 5.18.32 读到的真实界面

> 方法：Cua Driver 通过 UI Automation 读取已打开的 `Cybersole.exe`（pid 34996，
> window_id 920806）。每次读取都留了截图与 UIA 树。
>
> 这份文档的作用：**它是 replica 的唯一事实来源**。之前几轮的 UI 复现是照着 XAML
> 文件清单和字符串猜的，猜错了不少（见下面的「已纠正的猜错」）。

## 主窗口

**真实**：`Home / Tasks / Proxies / Billing / Accounts / Settings` —— **6 个 tab**

**replica 之前**：7 个（多了 `Analytics`、`Logs`）

> ⚠️ 待修：`MainWindow` 目前有 7 个 tab，需要改成 6 个并把 `Analytics` 挪到 **Home**。

### tab → 内容映射

| Tab | 真实内容 |
|---|---|
| **Home** | Analytics 仪表盘 |
| **Tasks** | 任务列表 |
| **Proxies** | 代理组管理 |
| **Billing** | 待读 |
| **Accounts** | 待读 |
| **Settings** | 设置页（见下） |

### ⚠️ 观察方法：点击后必须再读一次

像素点击之后立刻 `observe`，截到的往往是**上一个 tab 的内容**——Avalonia 的重绘晚一帧。
正确姿势：

```
1. run_steps  { click(x, y) }            ← 只点击，不 observe
2. get_window_state                       ← 单独再读一次，才是新内容
```

这个坑让我一度以为"点 Home 显示 Settings、点 Tasks 显示 Analytics"，
实际是每次都在看上一页。

### 标题栏右侧

真实有 5 个图标按钮（顺序）：某图标、通知铃、用户头像、最小化、关闭。
UIA 里表现为 `Button "Avalonia.Controls.Image"` ×3 + 系统按钮 ×2，没有可读标签。


## Accounts 页

```
ACCOUNT GROUPS
[🔍 Search stores]        id=StoreSearchBox

id=StoreList
  Nike                    + (空账号列表)
  Nike GS                 + (空)
  Shopify                 + (空)
  Footlocker (Asia)       + (空)
  Farfetch                + (空)
  Demandware (Funko)      + (空)
  Demandware              + (空)
  Magento                 + (空)
  Casio                   + (空)
  HBX                     + (空)
  Popmart                 + (空)
  Goat                    + (空)
  Scheels                 + (空)
  Warhammer               + (空)

[New Group +]

右侧：Nothing to see here / Add a group to get started
```

**列表不滚动**（滚动 15 tick 后截图哈希不变），所以这 14 项就是原版的完整平台清单。

### ⭐ 真正的三层结构：平台 → 区域站 → 组

点任意组的 `+` 会弹 **Create Group**：

```
Create Group
  Type    [Nike ▾]              ← 平台/底层技术（14 个之一）
  Store   [Select Store ▾]      ← 该平台下的具体店铺
  Name    [Group Name]
  [Add Group]
```

点各平台自己的 `+`，弹窗里 Type 会预选成那个平台。已读到的两组：

**`Type = Nike`（10 项）**

```
Nike US · Nike GB · Nike NL · Nike BE · Nike JP ·
Nike AT · Nike CZ · Nike DK · Nike FI · Nike FR
```

**`Type = Shopify`（可见 10 项，列表更长）**

```
Supreme EU · Supreme UK · Supreme US · Supreme JP · Supreme Asia ·
Buttercup Lynne Boutique · Converse CA · Converse JP · Dice Cup Cafe · END.
```

### ⭐⭐ 这改变了 `IStoreModule` 的粒度

原版的 **Type 是底层平台技术**（Shopify / Magento / Demandware / Nike 自建 …），
**Store 才是具体店铺**。同一技术下的不同品牌共用一个 Store 实现。

| 真实 | replica |
|---|---|
| `Shopify` 类型下的 `Supreme EU` / `Supreme UK` / … | `supreme` 是**独立 Flow 模块** |
| `Shopify` 类型下的 `Converse CA` / `Converse JP` | 无 |
| `Shopify` 类型下的 `END.` | ✅ 已改成 Shopify（原先是 Magento） |
| `Shopify` 类型下的 `Buttercup Lynne Boutique` / `Dice Cup Cafe` | 无（小众店） |

### Store 名单是服务器下发的，GUI 枚举不全

`Store` 输入框**可以过滤**（输入 `z` 得到 10 个 Z 开头的店）：

```
Zadoys · Zaibatsu · Zara Larsson US · Zatu Games · ZebraClub Berlin ·
zellerfeld · Zero Skateboards · zeropolis · Zeus.ph · Zulus Games
```

**但每个前缀最多显示 10 项，而且列表不可滚动。** 试过：

| 方式 | 结果 |
|---|---|
| UIA `scroll`（background） | 截图哈希不变 |
| UIA `scroll`（foreground，滚 popup） | 截图哈希不变 |
| `set_value` 拖 `PART_VerticalScrollBar` | 滚动条值变了，列表不动 |

**名单也不在二进制里** —— 在 `strings_all.tsv` 里搜 `Zadoys` / `Zaibatsu` /
`Buttercup Lynne` / `Dice Cup Cafe` 全部 0 命中。所以它是 `api.cybersole.io` 下发的远程配置。

**结论：Store 全量名单无法通过 GUI 读完，也不在静态分析范围内。**

这对目标的影响：

- **"复现所有网站模块"要按 Type（平台实现）算，不是按 Store（配置数据）算。**
  Store 名单是数据，几百个；平台实现是代码，14 个。
- 已确认的 Type：14 个（见上表）
- 已确认的 Store 样本：Nike 10 个区域站、Shopify 10 个已知品牌 + 26 个字母段各 10 个
  （量级在数百）



### ⭐ 原版支持的平台（14 个 Type）

| # | 平台 | replica 状态 |
|---|---|---|
| 1 | Nike | ✅ `nike`（但真实是 10 个区域站） |
| 2 | **Nike GS** | ❌ 缺 |
| 3 | Shopify | ✅ `shopify`（+26 个品牌配置） |
| 4 | Footlocker (Asia) | ⚠️ `footsites` 覆盖 Foot Locker，但 Asia 是单独 Type |
| 5 | **Farfetch** | ❌ 缺 |
| 6 | **Demandware (Funko)** | ✅ `funko`（GUI 第 2 轮补） |
| 7 | **Demandware** | ✅ `demandware`（GUI 第 2 轮补） |
| 8 | Magento | ✅ `magento`（+5 个品牌配置） |
| 9 | Casio | ✅ `casio` |
| 10 | **HBX** | ❌ 缺 |
| 11 | Popmart | ✅ `popmart` |
| 12 | **Goat** | ❌ 缺 |
| 13 | **Scheels** | ❌ 缺 |
| 14 | Warhammer | ✅ `warhammer` |

**平台实现：9 / 14。缺 5 个**：Nike GS、Farfetch、HBX、Goat、Scheels。


## Billing 页

```
PROFILE GROUPS              [Custom ▾]        [CSV Editor]  [🔍 Search profiles]
[🔍 Search groups]   id=GroupSearchBox
[Group 1       0]    id=ProfileGroupList
[New Group     +]

Group 1 ⚙   No Profiles Loaded

☐  Profile ⇅   Email ⇅   Card Holder ⇅   Card ⇅   Shipping ⇅    [Add Profile] [Clear Profiles]

                Nothing to see here
              Add some profiles to get started
```

- 左侧 `PROFILE GROUPS`（不是 "Billing Groups"），控件 id 与 Proxies 页**复用**：`GroupSearchBox` / `ProfileGroupList`
- 表头 **5 列**：`Profile` `Email` `Card Holder` `Card` `Shipping`
- 顶部按钮：`CSV Editor`
- 右侧按钮：`Add Profile`（绿）、`Clear Profiles`（红）

## 平台侧：Goat 抓到了，Scheels 还没

### 抓包工具

`tools/NetworkCapture` —— 独立控制台程序，绕过测试宿主（headed Chrome 在 `dotnet test`
里不会被回收，会挂）：

```powershell
dotnet run --project tools/NetworkCapture -- <url> [seconds] [--headless]
```

默认 headed，因为它存在的目的就是抓那些拦 headless 的站。

### Goat 的真实 API（实测）

```
GET /web-api/v1/countries
GET /web-api/v1/product_variants/buy_bar_data?productTemplateId=1729521&countryCode=US
GET /web-api/v1/product_variants/buy_bar_copies?productTemplateId=1729521
GET /web-api/v1/product_templates/recommended?productTemplateId=1729521&count=8
GET /web-api/v1/consumer-segment-access/get-user-segments/US
```

**三个容易做错的地方**：

| 项 | 错误的猜法 | 实际 |
|---|---|---|
| API 前缀 | `/api/` | **`/web-api/`** |
| 认证 | 无 | 每个请求带 **`X-CSRF-TOKEN`**（从 cookie 取） |
| 商品键 | URL slug | **数字 `productTemplateId`**（如 1729521） |

商品页把 `productTemplateId` 嵌在 HTML 里，URL 只有 slug——所以 `GoatFlow.GetHomeAsync`
要从页面正则挖出来。

另有 Cloudflare JSD 挑战（`/cdn-cgi/challenge-platform/`），headless 会被 403。

已落成 `GoatFlow`（7 步全实现，覆盖矩阵 71%——`SubmitShipping`/`SubmitPayment` 对
marketplace 不适用，购买即成交）。

### Scheels：还没抓

上一轮只确认了它**不是** Demandware（`/on/demandware.store/` 返回 404）、不是 Shopify、
不是 Magento——路径是自建的 `/c/{category}` + `/cp/{page}`，CMS 用 Amplience。

`NetworkRecorder` 对 scheels.com 在 headed 模式下拿到过 200，但还没跑完整的 API 抓取。


## Settings → Need Help? （页面标题 `Get Help`）

导航项叫 `Need Help?`，**页面标题是 `Get Help`**，副标题 `Take a look at common errors or contact support`。

```
[ Open help center ]
[🔍 Search errors]

（可滚动的错误词典，13 条）
```

### ⭐ 原版的完整错误词典（13 条）

**这就是 `Classify*Failure` 该输出的真实文案。**

| Tag | 标题 | 说明 |
|---|---|---|
| General | `Connection Error` | Target website unreachable or your proxies are currently not working. |
| General | `Not found` | Response code indicates that the server can't find the requested resource. |
| General | `Service Unavailable` | Response code indicates that the server is not ready to handle the request. |
| General | `Rate Limit` | …sent too many requests in a given amount of time ("rate limiting"). |
| General | `Forbidden` | …understood the request but refuses to authorize it. |
| General | `Task failed` | The task hit a unrecoverable error. Please make sure that it's configured properly and that all profile data is filled in and correct. |
| Shopify | `Error Submitting Shipping (Handle Error)` | This is caused by starting your Safe Preload tasks too early, which causes you to get requeued. |
| Shopify | `Error Submitting Order (Rate Limit)` | This means you were detected by antibot. This normally happens mainly if you are running Fast Mode on a site with antibot… |
| Shopify | `Payment Error` | This usually means that the item went out of stock on processing. |
| Shopify | `Connection Errors` | Your proxies are randomly disconnecting/having issues connecting to the site… |
| Shopify | `Tasks hanging on "Getting Shipping Rates"` | …does not ship to you and has region locked it to the state that their store is. |
| Shopify | `Invalid Credit Card Number/Billing` | …is invalid or Shopify is returning that from their end. It is not bot related. |
| Footsites | `Rate Limit / 429` | Status code used for a multitude of errors. Ranging from product blocks to IP / ASN blacklist. |

已落成 `src/Cybersole.Stores/Flows/ErrorCatalog.cs`：13 条逐字复制（**包括原文的
"a unrecoverable error" 这个语法错误**——这是产品表面的一部分，改了就 1:1 不上），
外加 `Classify(statusCode, stage, blocked)` 把 HTTP 状态 + 失败阶段映射到具体条目。

## Settings → Appearance

```
Appearance
Customize scrollbar appearance and sizing          [Reset Defaults]

Scrollbar
  ⓘ Scrollbar Width    [slider] [5] px
  ⓘ Corner Radius      [slider] [2] px
  ⓘ Scrollbar Color    [■] [#29293A]

PREVIEW
  Scroll to test the scrollbar appearance
  The scrollbar on the right reflects your current settings
  Adjust the width if the scrollbar is too small to grab
  Try different colors to match your preference
  Corner radius controls how rounded the scrollbar looks
  ... (可滚动的样例区)
```

**这一页只管滚动条**，三个字段：

| 标签 | 默认 | 控件 |
|---|---|---|
| `Scrollbar Width` | **5** | slider + 数字框 + `px` |
| `Corner Radius` | **2** | slider + 数字框 + `px` |
| `Scrollbar Color` | **`#29293A`** | 取色块 + 文本框 |

**replica 的问题**：`GlobalSettings` 里的默认值本来是对的（5 / `#29293A` / 2），
但 `AppearanceView.ResetDefaults()` 写的是 **0 / `#808080` / 4**——
点一下"Reset"就把正确值改成了错的。另外标签是 "Width / Colour / Corner radius"，
且没有 slider 和预览区。

已重写 `AppearanceView`：slider + 数字框联动、标签对齐、`Reset Defaults` 用真实默认值、
补上可滚动的 PREVIEW 区。

## Settings → Google Accounts

```
Google Accounts
Store Google accounts for easy access when using solvers

0 Accounts              [Clear Accounts] [Add Account]

☐  Name ⇅   Email ⇅

      Nothing to see here
  Add some Google accounts to get started
```

**表头 2 列**：`Name` / `Email`。

`Add Account` **不是表单**——它打开一个**内嵌的真实 Google 登录页**：

```
┌──────────────────────────────────────┐
│  G  Sign in                          │
│  Use your Google Account             │
│  [Email or phone]          Forgot email? │
│  Not your computer? Use Guest mode…  │
│  Create account            [Next]    │
└──────────────────────────────────────┘
[Name]              [Proxy]
[Save]
```

走完 OAuth 后，底部再填 `Name` 和 `Proxy` 保存。

> 这个弹窗的 UIA provider 会直接超时（`The UIA provider ... did not answer`），
> 只能靠截图判断结构。

**这对 replica 是个硬缺口**：`GoogleAccountEditView` 目前是手填 email / name / proxy。
真实版走 OAuth，意味着要复用 `ChromiumBridge` 打开登录页拿到会话，再存下代理配置。

**已实现** `src/Cybersole.Stores/Accounts/GoogleOAuthFlow.cs`：

```
BeginAsync()          LaunchAsync → ApplyStealthAsync → NavigateAsync(accounts.google.com/signin)
WaitForSignInAsync()  轮询 location.href 直到落在 myaccount.google.com
ReadIdentityAsync()   从 [data-email] 或正文正则取 email / 显示名
CompleteAsync()       上面两步的组合，返回 GoogleLinkResult
```

用的是 Nike Kasada 那条 `ChromiumBridge`（CDP），因为 Google 封的就是"跳过浏览器的脚本登录"。
`GoogleOAuthFlowTests` 锁住了 URL 判定、邮箱提取、以及失败时一定带 `Error`。

## Settings → PayPal Accounts

```
PayPal Accounts
Store PayPal accounts for easy access when creating tasks

0 Accounts              [Clear Accounts] [Add Account]

☐  Email ⇅   Status ⇅
```

**表头 2 列**：`Email` / `Status`。

`New PayPal Account` 弹窗 **6 个字段**：

| 字段 | 控件 | 默认 |
|---|---|---|
| Email | 文本 | — |
| Password | 文本 | — |
| Proxy Group | 下拉 | `None` |
| Max. inactive session duration | 下拉 | **`Permanent`** |
| Use login proxy | 开关 | **off** |
| Auto Reopen | 开关 | **on** |

replica 的模型字段大部分对上了（`ProxyGroup` / `UseLoginProxy` / `AutoReopen`），
但 `Max. inactive session duration` 之前是个**裸数字框**（`inactivateAfter`），
真实是带标签的下拉。已改成下拉并加 `PayPalAccount.MaxInactiveSessionDuration`。

`AutoReopen` 的默认值我们原来是 `false`，真实是 **on**——这条也一并记下。

## Settings → Data

```
Data
Import, export and backup data

[Select data ▾]                                 [Export] [Reset]

┌──────────────────────────────────────────────────────────┐
│  Drag and drop to import, or click to select file          │
└──────────────────────────────────────────────────────────┘

Backup                                          [Backup Now] [View Backups]
  ⓘ Restore from backup                                    [Restore]
  ⓘ Max backups                        [5]
  ⓘ Backup Interval                    [3 hours ▾]

Logs                                            [View Logs]
  ⓘ Max file size                      [50] mb
  ⓘ Maximum Retention Time             [1 day ▾]
```

**这一页的数值 replica 早就猜对了**：`MaxBackups = 5`、`BackupInterval = 3 hours`、
`MaxLogSize = 50 mb`、`MaxLogRetention = 1 day`，四个全中。

缺的是结构和交互：
- `Select data` 下拉（导出范围）+ `Export` / `Reset` 两个按钮
- **拖放/点击导入区**
- `Backup Interval` 是**带标签的下拉**（"3 hours"），replica 用的是裸分钟数字框
- `Maximum Retention Time` 同样是带标签的下拉（"1 day"），replica 用的是裸小时数字框
- `Backup Now` / `View Backups` / `View Logs` 三个入口

已重写 `DataView`：补上导入导出半页，两个时间字段改成带单位标签的下拉
（`30 minutes / 1 hour / 3 hours / 6 hours / 12 hours / 24 hours` 和
`1 day / 3 days / 1 week / 2 weeks / 1 month`），读写仍在 `TimeSpan` 上。

## Settings → Email Accounts

```
Email Accounts
Add imap email accounts to automatically login to certain sites

0 Accounts                   [Clear Accounts] [Add Accounts]

☐  Host ⇅   Email ⇅   Inbox Count ⇅

      Nothing to see here
  Add some accounts to get started
──────────────────────────────────────
● AYCD Inbox
  Not connected                                [Connect]
```

表头 **3 列**：`Host` / `Email` / `Inbox Count`。

`Add Imap Account` 弹窗 **3 个字段**：

```
Imap Provider   [Select or enter host ▾]
Email Address   [Enter email address]
Password        [Enter password]
[Save]
```

`Imap Provider` 可以下拉选，也可以直接输 host。预设 **6 个**：

```
imap.gmail.com · imap.mail.yahoo.com · imap.mail.me.com
imap.qq.com · imap.163.com · outlook.office365.com
```

（含 QQ 和 163 两个国内邮箱）

**AYCD Inbox 是底部一个独立面板**：彩色圆点 + 状态文字 + `Connect` 按钮，
不是散在表单里的几个字段。

**replica 之前**：5 个字段（Host / Port / Username / Password / TLS）、没有预设、
没有 `Inbox Count` 列，AYCD 摊成 4 个字段。已重写 `ImapView` 并给
`ImapAccount` 加了 `InboxCount`。

## Settings → Notifications

```
Notifications
Notifications and sounds

Enable Notifications                    [● on]

[Checkout] [Decline] [Captcha] [Smart Actions] [Other]

Allow Checkout Notifications            [● on]
  In-Bot Notifications                  [● on]
  Desktop Notifications                 [● on]

Sounds                                  [● on]
  [Default ▾]
  [Reset] [Play]
```

**五个分类是 tab，一次显示一个**——不是五块平铺。

每个分类下的固定四行 + 音效选择：

| 行 | 含义 |
|---|---|
| `Allow <Category> Notifications` | 该分类总开关 |
| `In-Bot Notifications` | 在 Cybersole 窗口内弹通知 |
| `Desktop Notifications` | 系统托盘通知 |
| `Sounds` | 声音开关 |
| `[Default ▾]` | 音效选择下拉 |
| `[Reset] [Play]` | 恢复默认音效 / 试听 |

**replica 之前**：5 个 `Section` 全部平铺，没有 tab 条；`In-Bot` 那行叫 "In-bot centre"；
没有音效下拉、没有 `Reset` / `Play` 按钮（只有全局的 Reset sound / Play sound）。

已重写 `NotificationsView`：五个 tab、每个 tab 四行 + 音效下拉 + Reset/Play。

`NotificationOptions` 的字段映射：`Enabled` → Allow、`Centre` → In-Bot、`Desktop`、
`Sound`、`Path`（音效名）。

## Settings → Webhooks

```
Webhooks
Receive real time notifications into your favorite services

[ New Webhook                            + ]

      Nothing to see here
  Add some webhooks to get started
```

`New Webhook` 不是一个弹窗按钮，而是列表里的一行（`DockPanel`，右边一个 `+`）。

点它 → **New Webhook** 弹窗：

```
New Webhook
  Name      [Personal server]
  Platform  [Select provider ▾]
  Webhook   [https://discord.com/api/webhooks]
  [Enter name]        ← 未填完时的确认按钮
```

**三个字段**：`Name` / `Platform` / `Webhook`（URL）。

placeholder 透露了两件事：
- Name 的示例是 `Personal server`
- Webhook URL 的示例是 `https://discord.com/api/webhooks`

**读不到的**：`Platform` 下拉的选项列表。这个 ComboBox 在 UIA 树里只暴露成
`Text "Platform"`，没有 ComboBox / ListItem 节点，点箭头和按 `Down` 都展不开
（`PART_List` 从没出现过）。`Provider`、`Platform` 这类下拉在别的页面是能读的
（Cloudflare 的 Provider 就读到了），唯独这里不行。

`CustomSizesView` / `CustomStoresView` 用的是同一个 `UiKit.Combo`，所以这大概率是
真实版这边用了不同的控件模板。

## Settings → Custom Sizes

```
Custom Sizes
Add custom Shopify size presets for easy access

0 Custom Sizes              [Clear Sizes] [Add Size(s)]

☐  Name ⇅

      Nothing to see here
  Add some size presets to get started
```

**表头只有一列 `Name`。** 按钮是 `Clear Sizes`（红）和 `Add Size(s)`（绿，注意括号）。

点 `Add Size(s)` → **Add Custom Sizes** 弹窗：

```
Add Custom Sizes
  Enter product URL
  [https://cybersole.io/]   [Clear]

  ┌──────────────────────────────┐
  │      Nothing to see here     │
  │   Search a valid product URL │
  └──────────────────────────────┘

  [Search]
```

**尺码不是手填的**——填商品 URL，点 `Search` 从商品页解析出尺码，再挑一个存成预设。
这解释了为什么列表只有 `Name` 一列（预设的"名字"就是那串尺码集合）。

已实现：`CustomSizesView` 现在走 `Enter product URL` → `Search` →
`/products/{handle}.js` → 读 `variants[].public_title` → `Add Selected` 存为预设。
`CustomPresetsTests` 锁住了 URL → handle 的提取规则（含带 locale 前缀和带 query 的形式）。

## Settings → Custom Stores

```
Custom Stores
Add custom Shopify store presets for easy access

0 Presets                      [Clear Presets] [Add Preset]

☐  Name ⇅   URL ⇅   Currency ⇅

      Nothing to see here
  Add some store presets to get started
```

点 `Add Preset` → **Add Custom Store** 弹窗：

```
Add Custom Store
  Enter store URL
  [https://cybersole.io/]
  [Add]
```

**只有 URL 一个字段。** Name 和 Currency 是添加后从店铺读回来的。

副标题 `Add custom Shopify store presets` 确认自定义店铺**只做 Shopify**——
和 replica 的 `Registry.RegisterCustom`（注册成 `ShopifyFlow` 别名）一致。

**replica 之前**：让用户填 Name + URL，没有 Currency 列，也没有 `0 Presets` 计数。
已改：`CustomStore` 加 `Currency`，`CustomStoresView` 只留 URL 输入，
Name 从 host 推导，计数/清空/删除按钮对齐真实版。

## Settings → Keyboard Shortcuts

标题 `Keyboard Shortcuts`，副标题 `Edit and disable keyboard shortcuts`。
顶部一个开关 `Enable Keyboard Shortcuts`（默认 on）。下面按页分组，每组两列。

### Tasks（12 项）

| 名称 | 键 | | 名称 | 键 |
|---|---|---|---|---|
| New Group | `Ctrl+G` | | Task Creator | `Ctrl+N` |
| Task Editor | `Ctrl+E` | | Start All | `F1` |
| Stop All | `F2` | | Delete Selected | `Delete` |
| Clone Selected | `Ctrl+C` | | Search | `Ctrl+F` |
| Quicktask | `Ctrl+Q` | | Link Change | `Ctrl+M` |
| Next Group | `Ctrl+Right` | | Previous Group | `Ctrl+Left` |

### Proxies（6 项）

| 名称 | 键 | | 名称 | 键 |
|---|---|---|---|---|
| New Group | `Ctrl+G` | | Add Proxies | `Ctrl+N` |
| Test All | `Ctrl+T` | | Copy Selected | `Ctrl+C` |
| Clone Selected | `Ctrl+D` | | Delete Selected | `Delete` |

### Billing（未见全，开头两项）

| 名称 | 键 |
|---|---|
| New Group | `Ctrl+G` |
| Add Profiles | `Ctrl+N` |

### ⭐ replica 之前 18 项全错

| 项 | 之前（Key,Mod） | 解码成 | 真实 |
|---|---|---|---|
| New Group | 50, 2 | `Ctrl+2` | `Ctrl+G` |
| Task Creator | 57, 2 | `Ctrl+9` | `Ctrl+N` |
| Task Editor | 48, 2 | `Ctrl+0` | `Ctrl+E` |
| Start All | 90, 0 | `Z` | `F1` |
| Stop All | 91, 0 | `0x5B` | `F2` |
| Delete Selected | 32, 0 | `Space` | `Delete` |
| Clone Selected | 46, 2 | `Ctrl+Delete` | `Ctrl+C` |
| Search | 49, 2 | `Ctrl+1` | `Ctrl+F` |
| Quicktask | 60, 2 | `Ctrl+F3` | `Ctrl+Q` |
| Link Change | 56, 2 | `Ctrl+8` | `Ctrl+M` |
| Next Group | 25, 2 | — | `Ctrl+Right` |
| Previous Group | 23, 2 | — | `Ctrl+Left` |
| Proxies 全部 6 项 | 50/57/63/46/47/32 | — | 71/78/84/67/68/46 |

已按真实值重写 `TaskKeyBinds` / `ProxyKeyBinds` 的默认值，并把测试从"断言旧的错值"
改成"断言从 GUI 读到的真值"。

## Settings → Cloudflare Providers

导航项 `Cloudflare Providers`，**页面标题 `3rd Party Cloudflare Providers`**，
副标题 `Add Cloudflare solving services, then pick one per task group`。

```
3rd Party Cloudflare Providers
Add Cloudflare solving services, then pick one per task group

[Add Provider]

      Nothing to see here
  Add a Cloudflare provider to get started
```

点 `Add Provider` → **Add Cloudflare Provider** 弹窗：

```
Add Cloudflare Provider
  Name         [uncaptcha.io]
  Provider     [uncaptcha.io ▾]        ← 只有 1 个选项
  API Key      [a6f979bf-...]
  Concurrency  [5]

  Pick this provider in a task group's Captcha tab to use it for that group's
  Cloudflare challenges.
  [Enter API Key]
```

**`Provider` 下拉只有一项：`uncaptcha.io`。**

**关键差异**：`replica` 之前把 Captcha 的 registry 直接搬来列所有 provider，
这错了两处：
1. 这是**独立的列表**，不是 captcha provider 的子集
2. 它只有**一个** provider

已重写 `CloudflareSolversView`：独立读 `settings.CloudflareSolvers`，
`Providers` 常量只有 `uncaptcha.io`，空状态和提示文案照抄真实版。

**"pick one per task group"** 这条说明 CF provider 是**按任务组绑定**的，不是全局开关。

已落成：

```csharp
StoreGroup.CloudflareProviderId   // 这个组用哪个 CF provider
StoreGroup.CaptchaProviderId      // 这个组用哪个 captcha provider（组内 Captcha tab）
MonitorContext.CloudflareProviderId / CaptchaProviderId / GroupId
```

三个都可空——为空时回落到全局默认（CF 用唯一的 `uncaptcha.io`，captcha 用优先级列表）。


## Settings → Payment

**不是支付网关配置**——是 3DS 和外部浏览器配置。

```
Payment
Configure advanced payment settings

3D Secure
  ⓘ Auto Open 3DS              [No ▾]

External Browser
  Browser Path                 [None]  [Configure]
  ⓘ Maximum Browser Tabs       [10]
  ⓘ Open Link As               [Tab ▾]

Browser Profiles
  Checkout Profiles    id=TokenList   [Browser default ▾]  [Refresh]
  ⓘ Profile Assignment         [Round robin ▾]
```

三个分组标题：`3D Secure` / `External Browser` / `Browser Profiles`。

**控件 id 是 `TokenList`** —— 说明这一块历史上是"token 列表"，改名成 checkout profiles 后 id 没变。

**replica 之前错得比较远**：

| 项 | 之前 | 真实 |
|---|---|---|
| `Auto Open 3DS` | Checkbox | **下拉 No/Yes** |
| 额外字段 | `Auto open limit`、`Shopify proxy` | **都没有** |
| `Browser Path` | `Executable` 文本框 | `Browser Path` + **Configure 按钮** |
| `Maximum Browser Tabs` | `Tab limit` | `Maximum Browser Tabs` |
| `Open Link As` | `Window mode` | `Open Link As`（Tab / Window） |
| `Checkout Profiles` | 双 ListBox（detected / selected） | **单个下拉** + Refresh |
| 分组标题 | 3-D Secure / Browser / Detected profiles | 3D Secure / External Browser / Browser Profiles |

已按真实布局重写 `PaymentView`。

## Settings → Captcha Providers

导航项叫 `Captcha Providers`，**页面标题是 `3rd Party Captcha Providers`**，
副标题 `Add and configure 3rd party captcha solving services`。右上角一个 `Add Source` 绿色按钮。

点 `Add Source` → **Add Captcha Provider** 弹窗：

```
Add Captcha Provider
  Name           [2Captcha]                                  ← placeholder
  Platform       [Select provider ▾]
  API Key        [a6f979bf-ab9e-4ea8-985f-b02d09bbcdfa]      ← placeholder
  Concurrency    [5]
  Captcha Types  [All Captchas ▾]
  Enabled        [● on]
  [Select platform]                                          ← 未选平台时的按钮
```

`Platform` 下拉的**完整 7 项**：

```
2Captcha · CapMonster · AntiCaptcha · AYCD · CapSolver · NextCaptcha · SolveCaptcha
```

**replica 之前只有 2Captcha**（另外 4 个 driver 是 HumanPresence / Uncaptcha / Parallax /
CfSolver，那是 Cybersole 自建服务，不在这个 3rd-party 列表里）。

已补 `src/Cybersole.Services/Captcha/ThirdPartyDrivers.cs`：

| Driver | 协议 | 端点 |
|---|---|---|
| `CapMonsterDriver` | JSON createTask/getTaskResult | `api.capmonster.cloud` |
| `AntiCaptchaDriver` | 同上 | `api.anti-captcha.com` |
| `CapSolverDriver` | 同上 | `api.capsolver.com` |
| `NextCaptchaDriver` | 同上 | `api.nextcaptcha.com` |
| `SolveCaptchaDriver` | 表单 in.php/res.php | `api.solvecaptcha.com` |
| `AycdCaptchaDriver` | — | 诚实报告：AYCD 是本地收件箱桥，不是打码服务 |

前者四个共用一个 `TaskApiDriver` 基类，只是 base URL 不同。

## Proxies 页


```
PROXY GROUPS                          [Custom ▾]
[🔍 Search groups]                    id=GroupSearchBox
[Group 1                        0]    id=ProxyGroupList
[New Group                    +]

Group 1 ⚙   No Proxies Loaded         ● 0 B download    ● 0 B upload

☐  IP ⇅   Port ⇅   Username ⇅   Status ⇅        [Add Proxies] [Clear All] [More]

                    Nothing to see here
                  Add some proxies to get started
```

- 左侧栏宽约 300px：标题 `PROXY GROUPS`、组类型下拉（`Custom`）、搜索框、组列表、`New Group`
- 右侧顶部：组名 + 齿轮、`No Proxies Loaded`、两个流量计数（下载/上传，各带彩色圆点）
- 表头 **4 列**：`IP` `Port` `Username` `Status`，全部可排序
- 三个按钮：`Add Proxies`（绿）、`Clear All`（红）、`More`

**replica 之前**：Proxies tab 直接塞了 `BillingView`，没有这层代理组结构。

## Tasks 页（任务列表）

```
[任务组下拉 "Group 1"] [...]  [🟢0] [🔴0] [🟣0] [🔵0]        [🔍 Search tasks]

☐  Site ⇅        Product ⇅        Profile ⇅        Proxies ⇅        Status ⇅        0 Tasks

                      (空状态)
                  Nothing to see here
                Add some tasks to get started

[Task Creator +]  [Clear Tasks 🗑]      [Start Tasks ▶]  [Stop Tasks ■]      [Edit Tasks ✏]  [Captcha Solver ▦]
```

**底部 6 个按钮**，左右各三个、中间两个：

| 位置 | 按钮 |
|---|---|
| 左 | `Task Creator` `Clear Tasks` |
| 中 | `Start Tasks` `Stop Tasks` |
| 右 | `Edit Tasks` `Captcha Solver` |

- 4 个状态计数按钮：绿（齿轮）、红（火焰）、紫（闪电）、蓝（刷新），各自带数字
- 组下拉的控件 id 是 `TaskGroupButton`，搜索框是 `FilterBox`
- 表头 5 列：`Site` `Product` `Profile` `Proxies` `Status`，全部可排序（⇅）
- 右上角显示 `0 Tasks`

## Home 页（Analytics 仪表盘）

```
[Checkouts | Spend]                          [Today | Week | Month | Year]        Checkout Feed

🛒 0 Checkouts
                    (空状态)
                Nothing to see here
        You haven't made any checkouts for this period
                                                        (右侧空状态)
                                                    Nothing to see here
                                              You haven't made any checkouts yet
Releases  ‹ 1/1 ›
[Supreme FW26 Week 13 Signups         Nov 10]
[Hot Wheels RLC Dodge Challenger SRT Demon 170   Nov 10]
[2026-27 Topps Hoops Basketball       Nov 10]
```

- 左上两个切换：`Checkouts` / `Spend`
- 右上四个时间粒度：`Today` / `Week` / `Month` / `Year`
- 中间大卡片：计数 + 图表/空状态
- 右侧独立栏：`Checkout Feed`
- 底部 `Releases` 轮播：`‹ 1/1 ›` + 卡片（封面图 + 标题 + 日期）

**这个页对应 replica 的 `AnalyticsView`**——真实版把它放在 Home，不是独立 tab。

## Settings 页


**顶部**：
```
Version 5.18.32
[ CHECK FOR UPDATES ]
```

**导航（14 个页面 + 1 个分组标题）**，注意**不是字母序**：

```
General
Appearance
Notifications
Webhooks
Email Accounts
Google Accounts
PayPal Accounts
Data
—— ADVANCED ——            ← 分组标题，不可点
Captcha Providers
Cloudflare Providers
Keyboard Shortcuts
Custom Stores
Custom Sizes
Payment
Need Help?
```

**底部**：
```
[ Log Out ]
```

---

## 已纠正的猜错

| 项 | replica 之前 | 真实 | 依据 |
|---|---|---|---|
| Settings 分区数 | 16 | **15**（14 页 + ADVANCED 标题不算页） | UIA 树 |
| `advanced` | 一个页面 `Advanced` | **ADVANCED 是分组标题**，不可点 | UIA 树无对应 RadioButton |
| 导航顺序 | 按 id 字母序 | **逻辑分组**：先账户类，再 ADVANCED 组 | UIA 树顺序 |
| `cloudflare-solvers` | 标题 "Cloudflare solvers" | **"Cloudflare Providers"** | UIA `Text` 节点 |
| `help` | "Need help" | **"Need Help?"** | 同上 |
| 大小写 | "Email accounts" / "Custom stores" / "Custom sizes" / "Captcha providers" / "PayPal accounts" / "Google accounts" / "Keyboard shortcuts" | **每个词首字母大写**：`Email Accounts` / `Custom Stores` / `Custom Sizes` / `Captcha Providers` / `PayPal Accounts` / `Google Accounts` / `Keyboard Shortcuts` | 同上 |
| 版本行 | 无 | **`Version 5.18.32` + `CHECK FOR UPDATES`** | UIA 树 |
| Log Out | 无 | **有**，在导航最底部 | UIA 树 |

已在 R1（GUI 轮）修复 `SettingsShell`，并把上述顺序/标题固化进
`tests/Cybersole.Tests/SettingsShellTests.cs`。

---

## 还没看的部分

以下从运行中的实例读，但**尚未**记录进本文档：

- `Home` 页
- `Proxies` 页
- `Billing` 页
- `Accounts` 页
- Settings 的 14 个页面各自的内容（字段、按钮、默认值）
- `Task Creator` 弹窗
- `Captcha Solver` 弹窗
- 任务组下拉、状态计数按钮的行为

## 怎么复现这份读取

```powershell
# 前提：Cybersole 正在运行
cua-driver call list_windows --pid 34996
cua-driver call get_window_state --pid 34996 --window_id <id>
```

或者在 DSH 里直接调 `mcp__cua__get_window_state`。
切换 tab 用像素点击（UIA 的 `Toggle` 只改选中态、不换视图）：

```
点击 (1014, 29)  → Settings
```


---

## R329：设置页导航栏 —— 实机复核（重启后第一次真正开 GUI）

原版 `D:\projects\cyber-reverse\target\Cybersole.exe`（5.18.32）以**保留会话**启动，直接进主界面，
点 Settings 后读到导航栏（从左到右、从上到下）：

```
Version 5.18.32    CHECK FOR UPDATES
────────────────────────────────────
General                 ← 选中态（高亮）
Appearance
Notifications
Webhooks
Email Accounts
Google Accounts
PayPal Accounts
Data
────────────
ADVANCED                ← 灰色、不可点的小标题（不是页面）
────────────
Captcha Providers
Cloudflare Providers
Keyboard Shortcuts
Custom Stores
Custom Sizes
Payment
────────────
Need Help?
Log Out                 ← 红色
```

### 这一次复核确认了四件事

1. **`ADVANCED` 确实是标题，不是页面** —— R300 那条守卫
   （`SettingsShellTests.AdvancedIsAGroupCaptionNotAPage`）写的是对的；
   R312 我加"第 16 个页面"被它拦下，也是对的。
2. **顺序与复刻件的 `Sections` 完全一致**（General → … → Payment → Need Help?）。
3. **底部有 `Log Out`** —— 复刻件 `SettingsShell` 已有（`Auth.SignOut()`），一致。
4. **General 页的行也一致**：Language / Default Monitor·Error·Timeout（2.500 ms、2.500 ms、10 sec）/
   Default Profiles·Proxies（None）/ ATC Browser Proxy·Queue Presentation（None、Time remaining）/
   Monitor Concurrency（Maximum + 3 max）/ Startup Page（Home）/ Currency（USD）。

### 结论

设置页这一整块**不需要改动** —— 它是"看起来像"之外的真对齐：结构、顺序、文案、控件值都对得上。


---

## R330：Payment 页 —— 用实机**结掉 R77 留下的悬案**

R77 记过一条 caveat：实机静止时只看到 "Auto Open 3DS"，看不到 "Max Open"，
所以怀疑它"只在 Auto Open 3DS 为 Yes 时才出现"，或者是个孤儿标签 —— 当时下拉点不开，问不下去。

这一轮把它问清楚了（在原版上操作，随后恢复原状）：

| 步骤 | 实机所见 |
|---|---|
| 初始 | `Auto Open 3DS [No]`，其下**没有** "Max Open" |
| 点开下拉 → Down → Enter | `Auto Open 3DS [Yes]`，其下**出现** `Max Open [5]` |
| 再切回 No | "Max Open" **消失** |

**结论：`Max Open` 是条件行，依赖 `Auto Open 3DS == Yes`。** 不是孤儿标签。

### 复刻件的改动（R330）

```csharp
var maxOpen = UiKit.Row("Max Open", auto3dsLimit);
maxOpen.IsVisible = s.AutoOpen3DS;
auto3ds.SelectionChanged += (_, _) => maxOpen.IsVisible = auto3ds.SelectedIndex == 1;
```

之前它一直显示（注释里还写着"藏起来会让这个值没有编辑器"）—— 那条理由在"条件是 Yes"成立后就失效了：
**值仍然有编辑器，只是编辑器跟着开关出现。**

### Payment 页其余控件（实机对照，全部一致）

`External Browser`：Browser Path + Configure / Maximum Browser Tabs `10` / Open Link As `Tab`
`Browser Profiles`：Checkout Profiles `Browser default` + Refresh / Profile Assignment `Round robin`

### 测试

`PaymentViewTests`（2 条）：`AutoOpen3DS=false` 时看不到 "Max Open"；`=true` 时看得到。
（走**逻辑树**，因为未挂载的控件没有视觉树；且判断可见性要连祖先一起看 —— 隐藏行仍持有自己的文本块。）


---

## R331：Tasks 页 —— 实机逐项对照，**没有差异**

实机（5.18.32，Settings → Tasks）读到的结构：

```
[🗂 Group 1 ⌄]  [...]    [🟢0][🔴0][🟣0][🔵0]              [🔍 Search tasks]     0 Tasks  ← 表头右侧
[☐]  Site⇅   Product⇅   Profile⇅   Proxies⇅   Status⇅                          0 Tasks
                            （空态）Nothing to see here / Add some tasks to get started
[Task Creator +]  [Clear Tasks 🗑]      [Start Tasks ▶] [Stop Tasks ■]      [Edit Tasks 🖊] [Captcha Solver ⧉]
```

与复刻件逐项对照（`TaskView.cs` / `TaskGrid.cs`）：

| 实机 | 复刻件 | 结论 |
|---|---|---|
| 分组下拉 `Group 1 ⌄` + 独立 `...` 按钮 | `_groups` ComboBox + `_groupMenuButton` | 一致 |
| 四色药丸 🟢🔴🟣🔵 = 0,0,0,0 | `Pill(Success,"#27AE60")`、`Pill(Failed,"#C0392B")`、`Pill(Declined,"#8E44AD")`、`Pill(Running,"#2980B9")` | 一致（顺序与颜色都对） |
| `Search tasks` | `_search`，占位文案相同 | 一致 |
| 列头 `Site / Product / Profile / Proxies / Status` 各带排序双箭头 | `HeaderButton("Site"/"Product"/"Profile"/"Proxies"/"Status")`，同序 | 一致 |
| 右下 `0 Tasks` | `CountCaption` = `"{0} Tasks"` | 一致 |
| 底部六键 3+3，Start/Stop 居中 | 文档里 R73 已记，代码同构 | 一致 |
| 空态两行 | `EmptyView` 的 headline + 第二行 | 一致 |

**Tasks 页无需改动。** 这一条与设置页一样，是"看出来的"而不是"读出来的"。

### 顺带纠正我自己的一次误判

我先在 `TaskGrid.cs` 里找四色药丸，没找到，差点记成"复刻件缺药丸"。
实际它在 `TaskView.cs:301-304` —— **`TaskGrid` 只画列表，工具条在 `TaskView`**。
又一次印证：**"未命中"先复核查法**（R295/R310 同一条）。


---

## R332：Proxies 页与 Accounts 页 —— 实机对照，并把商店清单**钉成测试**

### Proxies（零差异）

```
PROXY GROUPS   [Custom ⌄]
🔍 Search groups
Group 1                                                          0
[New Group +]

[📁] Group 1 [⚙]                      ● 0 B current download   ● 0 B current upload
No Proxies Loaded
[☐]  IP⇅  Port⇅  Username⇅  Status⇅        [Add Proxies] [Clear All] [More]
```

复刻件逐项有：`PROXY GROUPS`、`Custom`（六种排序之一，默认选中）、`Search groups`、
分组列表、`New Group`、`No Proxies Loaded`、两个流量计数（`current download` / `current upload`）、
`Add Proxies` / `Clear All` / `More`、列头 `IP/Port/Username/Status` 同序、空态两行。

### Accounts（零差异，且**顺序逐字相同**）

实机左栏 14 个平台，自上而下：

```
Nike · Nike GS · Shopify · Footlocker (Asia) · Farfetch · Demandware (Funko)
Demandware · Magento · Casio · HBX · Popmart · Goat · Scheels · Warhammer
```

复刻件 `StoreCatalog.Platforms` **逐字相同、顺序相同**（含 `Demandware (Funko)` 与 `Demandware` 并列、
`Footlocker (Asia)` 的括号、`Popmart` 的小写 m）。

其它：`ACCOUNT GROUPS` 标题、搜索框占位是 **"Search stores"**（注意不是 `Search groups`）、
`New Group +`、空态 `Add a group to get started` —— 全部一致。

### 新增守卫

`AccountStoreListTests`（2 条）：把 14 个名字与顺序**钉死**，并断言
`Nike/Nike GS`、`Demandware/Demandware (Funko)` 两对**保持互异**（这四行最容易在某次重构里被合并）。


---

## R333：Billing（Profiles）页实机对照 —— 零差异；三个列表页的列头**变成数据**

### Billing 实机结构

```
PROFILE GROUPS   [Custom ⌄]
🔍 Search groups
Group 1                                          0
[New Group +]

[📁] Group 1 [⚙]                        [CSV Editor]  🔍 Search profiles
No Profiles Loaded
[☐]  Profile⇅  Email⇅  Card Holder⇅  Card⇅  Shipping⇅   [Add Profile][Clear Profiles]
```

复刻件 `BillingView.Columns = { "Profile", "Email", "Card Holder", "Card", "Shipping" }` —— **同序同字**；
`CSV Editor` 按钮位置也对（在搜索框**左边**，同在表头右侧一格）。

### 把三页的列头变成"数据"而不是"五次调用"

之前三个网格都是逐行写 `HeaderButton("Site", …)`。现在改成：

```csharp
internal static readonly string[] Headers = { "Site", "Product", "Profile", "Proxies", "Status" };
private  static readonly TaskColumn[] HeaderColumns = { Site, Product, Profile, Proxies, Status };
for (var i = 0; i < Headers.Length; i++)
    grid.Children.Add(HeaderButton(Headers[i], HeaderColumns[i], i + 1));
```

Proxies 同样处理。**好处**：列头顺序成为可测试的数组，而不再埋在五次调用里。

### 新守卫

`ListPageColumnsTests`（3 条）：Tasks / Proxies / Billing 三页列头的文字与顺序，
与实机读数逐一相等（`TasksPageTests` 原本只钉了 Tasks，现在三页同置一处便于对照）。


---

## R334：Home 页 —— 实机空态与复刻件**有两处不同**（已改）

实机（无数据）与复刻件的差异：

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| Releases 分页 | **`0 / 0`** | `1 / 1`（`ReleasePages` 用了 `Math.Max(1, …)`） |
| Releases 空态 | `Nothing to see here` + **`There are no upcoming releases`** | 只有前一行，且**整段缺失** |

### 改了什么

1. `ReleasePages` 去掉 `Math.Max(1, …)` —— 没有数据就是 0 页；
2. 新增 `PagerCaption(page, pages)`：`pages <= 0` 时输出 `0 / 0`（否则 `page / pages`）；
3. 新增 `EmptyReleasesBody = "There are no upcoming releases"`，并在卡片为空时渲染两行空态。

### 为什么之前没发现

R73 那次读数**带着数据**（`Palace Skateboards Winter '26 Week 7 / Nov 13`），
分页自然是 `1 / 1`。**空态只有在"没有数据"的账号上才看得到** —— 而这次重启后正好是空库。

> 结论：**同一个小部件有两种状态，只测其中一种等于没测。**


---

## R335：Home 的 Spend 段 —— 又两处真差异（文案 + 金额格式）

实机点过 `Spend` 段：

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| 大数字 | **`$0`** | `0`（只有 `(int)Math.Round(spent)`，无货币符号） |
| 数字下的说明 | **`Money Spent`**（大写 S） | 一行代码写 `"Money spent"`，**紧接着另一行又覆盖成 `"Spend"`** |

### 改了什么

1. `SegmentCaption(index)` 成为唯一出处：`0 → "Checkouts"`，`1 → "Money Spent"`；
2. `SpendFigure(decimal)` → `"$" + 四舍五入`；**多位数格式标 `inferred`**（实机只给了空态的 `$0`）；
3. 两处旧赋值（117 行与 298 行）都改成调用这两个方法 —— 之前它们**互相矛盾**。

### 顺带确认

Spend 段的空态文案**与 Checkouts 段相同**：`Nothing to see here` / `You haven't made any checkouts for this period`
（没有改成 "spent"）—— 复刻件复用同一个 `EmptyPeriodBody`，一致。

### 测试

`TheSpendSegmentSaysMoneySpentAndPrintsADollarFigure`：
`SegmentCaption(0) == "Checkouts"`、`SegmentCaption(1) == "Money Spent"`、`SpendFigure(0m) == "$0"`。


---

## R336：通知面板（右上铃铛）—— 三处差异，其中两处是**我多加了东西**

实机点铃铛，面板（贴右侧的浮层，非独立窗口）：

```
0 Notifications                              [Clear]
        ┌ ✕ ┐
   Nothing to see here
   Your notifications will show up here
   （grid id = NotificationsGrid）
```

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| 标题 | **`0 Notifications`**（计数 + 词） | 只有 `Notifications`，且**多一行 `Clock`** |
| 按钮 | **只有 `Clear`**（右上） | `Clear` + **`Delete`** + `Close` |
| 空态 | `Nothing to see here` + **`Your notifications will show up here`** | `"(nothing yet)"` |

### 改了什么

1. 标题改为 `_caption` = `"{count} Notifications"`；
2. **删掉 `Clock` 行与 `Delete` 按钮** —— 实机面板的完整树里都没有（保留 `Close`：复刻件这个面板是独立窗口，需要关闭手段）；
3. 空态改成两行，第二行 = `EmptyBody = "Your notifications will show up here"`。

`_clock` 字段保留（`services.Clock` 仍在用），只是不再显示。

### 教训

前几轮我一直在"补缺失"，这一轮是**删多余**。两者同等重要，而"删"更难 ——
它需要先证明"实机的树里没有"，而这次恰好拿到了完整面板树。


---

## R337：头像面板（`• My License`）—— 复刻件原来是另一个窗口

实机点右上头像（**不记录账号名与邮箱**，只记结构）：

```
•  My License
      (avatar)
      <display name>
      <email>
   [ Dashboard ↗ ]
──────────────────────────────
Terms of Service  •  Privacy Policy            [ Log Out ]
```

复刻件原来是 `Account` 窗口：`Session` 卡片里 `Email / Subject / Role / Expires` 四行 + `Open dashboard` / `Sign in` / `Log out` 三个平按钮。

### 按实机重写

| 项 | 实机 | 复刻件现在 |
|---|---|---|
| 顶栏 | `•  My License` | 同（`\u2022  My License`） |
| 头像 | 圆形 | `Border` 圆角 32 + 字形占位 |
| 名字 / 邮箱 | 两行（名字大、邮箱小且淡） | 同（名字取邮箱 @ 前段，占位 `(signed out)`） |
| 主按钮 | `Dashboard ↗`，整行宽 | 同 |
| 页脚 | `Terms of Service • Privacy Policy` 左、红色 `Log Out` 右 | 同 |
| `Subject/Role/Expires` 三行 | **没有** | **删掉** |

### 两处诚实标注

1. `TermsUrl` / `PrivacyUrl` 两个地址**没有出处**（实机只给了按钮，没给链接目标）→ 标 `inferred: no image evidence (R337)`；
2. **`Sign in` 改成"无会话时才显示"** —— 实机是已登录态，面板上没有它；
   但 R213 的理由（没有会话时要有一条登录入口）仍然成立，所以留着、只隐藏。

### 教训

删掉 `Sign in` 后，`LoginControl` 立刻变成"声明但从未构造"，四条测试变红 —— 
**守卫逼我把"删"改成"条件显示"。** 这是守卫第二次挡住我的过度删减（第一次是 R300 的 `ADVANCED` 页面）。


---

## R338：Keyboard Shortcuts 页 —— 实机读到 18 条 chord，复刻件**全部一致**

实机（Settings → Keyboard Shortcuts）：

```
Keyboard Shortcuts — Edit and disable keyboard shortcuts
[Enable Keyboard Shortcuts]  ●

Tasks
  New Group      [Ctrl][G]  Task Creator   [Ctrl][N]
  Task Editor    [Ctrl][E]  Start All      [F1]
  Stop All       [F2]       Delete Selected[Delete]
  Clone Selected [Ctrl][C]  Search         [Ctrl][F]
  Quicktask      [Ctrl][Q]  Link Change    [Ctrl][M]
  Next Group     [Ctrl][→]  Previous Group [Ctrl][←]

Proxies
  New Group      [Ctrl][G]  Add Proxies    [Ctrl][N]
  Test All       [Ctrl][T]  Copy Selected  [Ctrl][C]
  Clone Selected [Ctrl][D]  Delete Selected[Delete]

Billing
  New Group      [Ctrl][G]  Add Profile    [Ctrl][N]
  …（下半截在折叠线以下）
```

每条 chord 右侧都有一个 `×`（清除该绑定），整页顶部是单个 `Enable Keyboard Shortcuts` 开关。

### 与复刻件对照

| 项 | 结论 |
|---|---|
| Tasks 12 条 chord | **全一致**（`Ctrl+G/N/E`、`F1`、`F2`、`Delete`、`Ctrl+C/F/Q/M`、`Ctrl+Right/Left`） |
| Proxies 6 条 | **全一致**（`Ctrl+G/N/T/C/D`、`Delete`） |
| 顺序与标签 | 一致（`KeyBindsView.TaskLabels` / `ProxyLabels`） |
| 顶部开关 | 一致（`Enable Keyboard Shortcuts`） |

### 新增守卫

`KeyBindChordTests`（3 条）：把 12 + 6 + 4 条 chord **用 `KeyBindMatcher.Describe` 的输出**钉住 ——
也就是说它测的是**界面上真正渲染的那个字符串**，而不是模型里的键码。

> Billing 后两条在实机折叠线以下，未本轮重读 → 测试注释里写明"这两条来自 R76 的抄录"，不冒充重测。


---

## R339：Webhooks 页 + 「New Webhook」弹窗 —— 实机读到，改了三处、记了三条

### 页面（空态）

```
Webhooks — Receive real time notifications into your favorite services
[ New Webhook                            + ]
                Nothing to see here
                Add some webhooks to get started
```

### 弹窗「New Webhook」

```
+  New Webhook                                    [×]
Name                          Platform
[Personal server      ]       [Select provider  ▾]
Webhook
[https://discord.com/api/webhooks              ]
[            Enter name                         ]
```

### 改了什么（复刻件 `WebhookCreatorView`）

| 项 | 实机 | 改前 | 现在 |
|---|---|---|---|
| 标题 | `New Webhook` | `New webhook` | `New Webhook` |
| Name 占位 | `Personal server` | `Checkout notifications` | `Personal server` |
| URL 占位 | `https://discord.com/api/webhooks` | `…/api/webhooks/…` | 实机原文 |
| Platform 占位 | `Select provider` | 直接列 `Discord/Custom` | 首项 `Select provider` |
| 布局 | Name 与 Platform **同一行**，URL 在 `Webhook` 标题下 | 三行竖排 | 同实机 |

### 记下来但**没改**的三条（证据不足）

1. **提交按钮**：实机空名时显示 `Enter name`（不是 `Save`）。想改成"名字空→`Enter name`、有名字→`Create`"，
   但那要重排 ctor，改到一半编译不过，**已回滚**，只记录；下轮用完整重写方式做。
2. **`Attach to group` / `Events` 两行**：实机在未选 Platform 时**看不到**，但可能在选完之后出现 —— 未验证，保留。
3. **`Extra Fields`**（R318 依照 locale key 加的）：这个弹窗里**没有**。可能属于某个具体 Platform 的展开项，
   也可能只存在于 locale 而没有界面 —— 未定，标注待查。

> 这一轮的教训：**"看到了差异"和"改得动"是两件事。** 记录也要算产出，硬改到编译不过不算。


---

## R340：Webhook 提交按钮是**三态机**（实机逐个走过）

在实机上把三个状态都走了一遍：

| 状态 | 按钮文字 | 是否可点 |
|---|---|---|
| Name 空 | **`Enter name`** | 否（灰） |
| Name 有值、URL 空 | **`Enter valid webhook`** | 否（灰） |
| Name 有值、URL 合法 | **`Save`** | **是（绿）** |

同时确认：**选定 `Discord` 之后没有多出任何字段** —— `Extra Fields` / `Events` / `Attach to group`
都没有出现（这直接质疑 R318 按 locale key 加的 `ExtraFields`：它在界面上没见过）。

### 复刻件改动

`WebhookCreatorView` 整类重写（含 R339 的布局）：`SubmitLabel(name, url)` / `IsWebhookUrl(url)` 两个纯函数 +
footer 按钮跟随两个输入框实时换字与启停。

### 一次自己造的乌龙

测试里我先写了 `("probe", "https://discord.com/api/webhooks", "Enter valid webhook")` —— 失败。
原因：那串 URL 在实机上是**占位水印**，不是值；输入框实际是空的。
**把水印当成值**，是我这一轮最典型的误读。

### 三次编辑失败的过程也要记

这一轮我在同一个 ctor 上改了三次都编译不过（索引错位、误伤到隔壁 `BrowserDriverCreatorView`、
把注释行并进了上一行）。最后**整类重写**才干净通过。

> 教训：**在别人（哪怕是自己）写的长文件里做索引级外科手术，代价远高于整段重写。**
> 下一次直接重写，不要省那几分钟。


---

## R350：Tasks → 「Group Settings」弹窗 —— 实机 4 个 tab，复刻件 6 个

实机（点 Tasks 页 `Group 1` 旁的齿轮）：

```
[📁] Group Settings                                   [×]
Group Name
[Group 1                                          ]
─────────────────────────────────────────────────
 Delays | Limits | Captcha | Notifications
 Monitor Delay [2500 ms]  🔗   Error Delay [2500 ms]
 Timeout [10 sec]
[ Delete ]                              [ Save ]
```

- `Delays` 的 tooltip：**"Group specific delays. If none are set, global delays will be used, you can adjust these in settings."**
- 🔗 按钮的 tooltip：**"When toggled, both monitor and retry delays will stay the same"**
- 底部两键：`Delete`（红）/ `Save`（绿）

复刻件 `TaskGroupView` 有 **6 个 tab**：`General / Delays / Limits / Captcha / Notifications / Manual`，
而 **`Group Name` 被放在 `General` tab 里**，实机是**放在 tab 之上**。

### 结论：这是结构性差异，本轮**只记录不改**

差异有三处：

1. 实机 **4** 个 tab，复刻件 **6** 个（多 `General` 与 `Manual`）；
2. `Group Name` 的位置不同（实机在 tab 上方）；
3. 复刻件 `General` 里还有 `Pinned` / `Order`，`Manual` 里是 `PeriodStart` —— **实机这三个控件还没找到家**。

**为什么不在这一轮改**：要先把实机的 `Limits` / `Captcha` / `Notifications` 三个 tab 也读一遍，
才能确定 `Pinned` / `Order` / `PeriodStart` 是"另有其处"还是"复刻件多造"。少读三个 tab 就重构，
就是又一次 R340 式的返工。


---

## R351：Group Settings —— 把「Group Name」搬到 tab 之上，页脚改成 Delete / Save

### 实机（R350 读数）

```
Group Settings                                  [×]
Group Name [Group 1]                  ← tab 之上、独立一行
 Delays | Limits | Captcha | Notifications
[ Delete ]                    [ Save ]     ← 底部两键，Delete 红
```

### 复刻件改了什么

1. 顶部加 `Group Settings` 标题 + **`Group Name` 独立行**（`groupName` 绑定 `_group.Name`）；
2. `General` tab 里**删掉 `Name` 那一行**（避免两个编辑器改同一个值），只留 `Pinned` / `Order`；
3. 页脚 `Save / Reset` → **`Delete` / `Save`**，并新增 `DeleteGroup()`（从 `Config.TaskGroups` 移除并保存，
   返回是否真的删到）。

### 还没改的（证据不足）

- `Delays` 的 🔗 联动、`Limits` / `Captcha` / `Notifications` 三个 tab 的内容（实机尚未逐个读完）；
- `Pinned` / `Order` / `Manual` tab 里的 `PeriodStart`：实机 4 个 tab 里没有它们的位置。

**tab 数仍是 6**，这是已知差异，等三个 tab 读完一次性收敛。


---

## R353：Group Settings 收敛到实机的 4 个 tab

| 项 | 实机 | 复刻件（改后） |
|---|---|---|
| tab | Delays / Limits / Captcha / Notifications | **同** |
| `Group Name` | tab 之上的独立行 | 同（R351） |
| 页脚 | `Delete` / `Save` | 同（R351） |
| `Period start` | 属 **Limits**（locale tooltip 在此） | 已移入 Limits |
| `Pinned` / `Order` / `Manual` | 不在本弹窗 | **已删**（`Pinned`→`TaskView.PinGroups`，`Order`→`Settings.TaskGroupOrder`） |


---

## R381：登录窗口（实机，640×780 左右）

重启后落在登录窗口，正好把这块界面量了：

```
[ ]  Window "Login"                                      -  X
                        🐢
            Welcome to Cybersole 5.0
        Sign in with your Cybersole account

            ☑ Remember Me

        [      Sign in with browser      ]      ← 全宽绿色

        Don't have an account?  Sign Up
```

**只有三样可交互的东西**：`Remember Me`、`Sign in with browser`、`Sign Up`。
**没有** "Use a code instead"，也没有许可证选择器。

### 复刻件因此改了两处

1. 首屏去掉 `Use a code instead`（它与实测不符）；
2. 把它挪到**等待态**（点过浏览器登录之后），与验证码输入框放在一起 —— 那里才是它的出口。

文案逐条核对（全部命中 locale）：`Auth.Welcome` / `Auth.Login.Subtitle` / `Auth.Login.Button` /
`Auth.Login.RememberMe` / `Auth.Login.NoAccount` / `Auth.Login.SignUp`。
