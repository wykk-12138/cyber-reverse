# 功能对照表 — Cybersole 5.18.32 vs 本复刻

证据来源：`analysis/Cybersole-RE-Report.md`（IDA Pro 反编译 + 字符串提取 + `%APPDATA%\Cybersole\settings.json` 实测）。

图例：✅ 已对齐 · 🟡 已实现但深度有限 · ⚪ 不复刻（属服务端/授权范畴）

## 1. 配置与存储

### 8 个文档

| 原版 | 复刻位置 | 状态 |
|---|---|---|
| `settings.json`（bearer/license/concurrency/keyBinds/notificationOptions/monitorFilters/webhooks/…） | `Core/Store/ConfigurationStore.cs` → `.Settings` | ✅ |
| `accounts.json`（分组 + 账号 + PayPal/Google/IMAP/AYCD） | → `.Accounts` | ✅ |
| `proxies.json`（分组 + 代理 + 测试状态） | → `.ProxyGroups` | ✅ |
| `tasks.json`（分组 + 任务 + 延迟/超时/账号绑定） | → `.TaskGroups` | ✅ |
| `billing.json`（Profile + 卡信息 + 并发策略） | → `.BillingGroups` | ✅ |
| `solvers.json` | → `.Solvers` | ✅ |
| `smartActions.json` | → `.SmartActions` | ✅ |
| `analytics.json`（`checkoutHistory.json`） | → `.Analytics` | ✅ |
| `.cyb` 备份（实测为明文 JSON 归档） | `ConfigurationStore.Backup()` | ✅ 含保留策略 |

### 写入是原子的

`AppPaths.cs:104`

```csharp
public void Save<T>(T value) where T : class
{
    var tmp = _path + ".tmp";
    File.WriteAllText(tmp, Json.Serialize(value));
    File.Move(tmp, _path);          // atomic on the same volume
}
```

**先写 `.tmp` 再 `Move`**，所以进程在写到一半被杀，磁盘上留下的仍然是**上一份完整的文件**，
不是半截 JSON。

**这是 R113 留下的东西**：那轮发现「保存后重启，改动全没了」，原因是 UI 编辑的是一个
一次性副本（见 R122 的 `SolverSettings` 缺陷），不是写文件的问题。**修 UI 的同时把写文件
也做成了原子的**——两个缺陷症状一样（改动消失），根因不同。

### 读取是容错的

```csharp
Settings = _settings.LoadOrDefault(() => new GlobalSettings());
TaskGroups = _tasks.LoadOrDefault(() => new List<TaskGroup>()) ?? new List<TaskGroup>();
```

**文件缺失、损坏、无法解析 → 返回默认值，不抛异常。** 调用方拿到的永远是一个可用对象。

`Load()` 还会补齐空的默认组：

```csharp
if (TaskGroups.Count == 0) TaskGroups.Add(new TaskGroup { Name = "Group 1" });
// 同样处理 ProxyGroups / BillingGroups
```

### 两个不是原子的地方

| 位置 | 情况 |
|---|---|
| `Backup()` | `File.WriteAllText(BackupsDir/Backup …cyb, …)` —— 直接写，没有 tmp+Move |
| `Save()` 整体 | 逐个文档 `_xxx.Save(...)`，8 次原子写但不是一个事务：写完 3 个崩掉，磁盘上是 3 新 5 旧 |

**这两条都留着。** 备份文件写坏了的代价是「少一份备份」，不是「数据丢了」；8 个文档之间
没有跨文件不变量，所以「3 新 5 旧」不会自相矛盾。

**写下来是因为它们是已知的不完美，不是没人注意到。**

### 这一节在 R163 之前

9 行，全是「哪个文件对应哪个类」。**原子写、容错读、默认组补齐、以及两处非原子——一个都没提。**

## 2. 传输与指纹

### 传输层

| 原版 | 复刻位置 | 状态 |
|---|---|---|
| SChannel 默认栈 | `TransportMode.SChannel` | ✅ TLS 1.2 + 1.3（BCL 提供） |
| 自定义 ClientHello（指纹伪装） | `TransportMode.BouncyH2` / `BouncyHttp11` | 🟡 cipher/SNI/GREASE 可控，扩展序被 BC 重排 |
| 完全自控的 ClientHello | `TransportMode.OwnTls` → `Tls12Client` | ✅ cipher 序 / 扩展序 / GREASE / SNI 全由字节数组决定 |
| **纯 C# QUIC/HTTP3/TLS 1.3 全栈** | `TransportMode.PureNetClient` → `TlsClientCache` / `ProtocolRacer` / `QuicConnection` / `Http3Connection` / `TlsStream` | ✅ 纯托管安全 C# 完整实现：`Cybersole.Http 0.10.0` TLS 1.2+1.3（含 ML-KEM-768、0xCA34、82 Profile / 68 ClientHelloSpec）、QUIC v1 + HTTP/3 + QPACK、HTTP/2 + HPACK 与 HTTP/1.1 |
| JA3 字符串生成 | `Cybersole.Http.Ja3.FromProfile` | ✅ |
| HTTP/2 + HPACK | `Http2.cs` + `Tls12Client.SendH2Async` | ✅ 含 Huffman 解码（`HpackHuffman.cs`） |
| HTTP/2 连接复用与 SETTINGS | `BouncyH2Client` / `Http2.cs` | ✅ |
| 代理轮换 | `ProxyRotator` + `TaskEngine` | ✅ |
| 代理测速 | `ProxyTester` + `TestProxiesAsync` | ✅ |
| 请求/连接分析（写 ClickHouse） | `HttpAnalytics.Flush` | ✅ 批量 `JSONEachRow`，失败不阻塞调用方 |

**TLS 1.3 与 QUIC/HTTP3 已在 `full-QUIC/HTTP3/TLS` 支线由 `TransportMode.PureNetClient` 完整补齐**：`OwnTls` 仍保留作为轻量 TLS 1.2 探针路径；新业务路径通过 `TransportMode.PureNetClient`（或直接 `TlsClientCache`）走纯 C# TLS 1.2/1.3、ML-KEM-768、QUIC v1/HTTP/3 与浏览器级 H2/H3 指纹。

### 压缩与内容

| 原版 | 复刻位置 | 状态 |
|---|---|---|
| Brotli（含 RFC 7932 预置字典） | `BrotliDictionary`（122,784 字节，内嵌资源） | 🟡 **字典字节完整，但 .NET 8 的 `BrotliStream` 不支持字典参数**，所以用它压出来的流读不了 |
| gzip / deflate | `BouncyHttpClient` | ✅ |

### 反检测（注入到真实 Chromium）

| 能力 | 复刻位置 | 状态 |
|---|---|---|
| UA 与 `userAgentData` 一致 | `ChromiumBridge.ApplyStealthAsync` | ✅ 两者都从 `ChromiumBridgeVersion()` 取；UA 用 `<major>.0.0.0`（UA Reduction 形式） |
| 完整版本号（`getHighEntropyValues().fullVersion`） | — | ❌ **CDP 限制**：Chrome 157 把 `setUserAgentOverride.fullVersionList` 降级到 major，且不返回该 hint |
| `webdriver` 缺失 | stealth 补丁 1 | ✅ |
| `window.chrome` / plugins / languages | 补丁 2–4 | ✅ |
| `permissions.query` 不返回 denied | 补丁 5 | ✅ |
| WebGL vendor 不是 SwiftShader | 补丁 6 | ✅ |
| `hardwareConcurrency` / `deviceMemory` / `maxTouchPoints` | 补丁 7 | ✅ |
| `outerWidth` / `outerHeight` | 补丁 8 | ✅ |
| `speechSynthesis.getVoices()` 非空 | 补丁 9 | ✅ 6 个 Windows Chrome 语音 |
| **同源 iframe 的 realm 重放** | 两条钩子（`createElement` + `contentWindow` getter）+ `WeakSet` | ✅ 13 个 `try` 块，每个补丁独立守卫 |
| 设备指纹表（29 张） | `Cybersole.Engine.hcaptcha-spoof.js`（606 KB，802 行注释） | ✅ 原版资产原样内嵌 |
| Kasada token | `KasadaSolver`（Jint）+ `ChromiumKasadaSolver`（真浏览器） | ✅ 两条路，`KasadaResult` 覆盖 8 个状态字段 |

**这一节在 R159 之前只有 7 行，全是传输层。** 反检测那 11 行是 R136–R138 才有的东西，
当时没有回来加。

## 3. 站点模块

**68 个注册模块，38 种不同的 flow 类型。** 数字取自 `CreateAll()` 的返回，
不是文件里 `new FlowStoreModule(` 的出现次数——后者是 62，多出的一个是
`RegisterShopifyHost()` 工厂里的模板。

| 类别 | 数量 | 说明 |
|---|---|---|
| `ShopifyFlow` | **29** | 1 个通用入口（无参，默认 `myshopify.com`）+ **28 个品牌别名** |
| `DemandwareFlow` | **2** | 同一引擎，两个品牌 |
| 其它 flow 类型 | **30** | 各 1 个，见下 |

**28 个 Shopify 品牌别名**

```
100thieves  10corsocomo  a-ma-maniere  afew  bodega  capsule  civilist
concepts  courtside  deadstock  extrabutter  lapstone  livestock  nakedcph
nrml  offthehook  overkill  packershoes  premiumgoods  saintalfred  shophmvs
sneakerpolitics  socialstatus  titan22  tresbien  trophyroom  undefeated  vooberlin
```

**30 种单一 flow**

```
Nike  NikeGs  Footsites  Supreme  EndClothing  JohnLewis  PopMart  YeezySupply
Hybris  Raffle  Casio  Warhammer  JbHiFi  Superswipe  PocketGames  Sns
Size  JdSports  Fanatics  RiotGames  HypeCommerce  Footpatrol  Notre  Bstn
Hbx  Funko  Farfetch  Goat  Scheels  Converse
```

**这一节在 R158 之前写的是「50 个模块 / 独立实现 13 个 / Shopify 别名 27 个」。**
50 是当时的真实数字；之后加了 11 个，表没回来改。

### 可达性（R256 实测，62 个域名逐个探）

**这一格在 R151 是 `Live 43 / Guarded 7`，R256 是 `Live 44 / Guarded 6`——105 轮里有一个模块跨过了那条线。**

| 状态 | 数量 | 成员 | 含义 |
|---|---|---|---|
| `Live` | 44 | 见下 | 2xx/3xx，模块有地方跑 |
| `Guarded` | 6 | `casio` `goat` `offspring` `pocketgames` `scheels` `yeezysupply` | 401/403/429，站点在但拒绝自动化 |
| `Wildcard` | 1 | `shopify` | `myshopify.com`——基域，根路径本就无站点 |
| `Missing` | 1 | `trophyroom` | `trophyroomstore.com`——域名在，站点没了 |
| `Reserved` | 1 | `demandware` | `demandware.example`——RFC 2606 保留，永不解析 |
| `Dead` | 8 | `bodega` `hypecommerce` `livestock` `nakedcph` `nike-gs` `offthehook` `premiumgoods` `shophmvs` | DNS 或 TLS 失败 |

**`Live` 的 44 个**：

```
100thieves 10corsocomo a-ma-maniere afew bstn capsule civilist concepts converse
courtside deadstock endclothing extrabutter fanatics farfetch footpatrol footsites
funko hbx jbhifi jdsports johnlewis kith lapstone nike notre nrml overkill
packershoes popmart raffle riotgames saintalfred size sneakerpolitics sns
socialstatus superswipe supreme titan22 tresbien undefeated vooberlin warhammer
```

**数字会漂，名字不会。** 两次测量之间变化的东西只有一个模块，但只写 `43` 和 `44`
看不出是哪一个——而写名字就能 `diff`。下一次跑 `ModuleReachabilityTests`（`Speed=Slow`）
会把当前分类打出来，拿它和上面两张格子比。

**真实的站点腐化只有 `Missing` 那 1 个，加上 `Dead` 里未核实的 6 个。**
`Wildcard` / `Reserved` / 部分 `Dead` 从注册那天起就注定是这个结果。

**`Dead` 要打折扣看**：这台机器跑 Mihomo，DNS 对每次 A 查询都回 `198.18.x.x` 假地址。
`bodega` 和 `offthehook` 已经用 DoH 确认有真实 A 记录，所以它们的 `Dead` 是「这次扫描到不了」，
不是「店铺没了」。其余 6 个未核实。

| 能力 | 状态 |
|---|---|
| 商品页可售/售罄判定（JSON-LD / 内联 JSON / HTML 关键词） | ✅ |
| 队列页识别（queue-it） | ✅ |
| 尺码提取 | ✅ |
| 加购（`/cart/add.js`、`/api/basket/add`、Magento 表单…） | ✅ |
| 结账表单字段（身份 + 账单 + 卡） | ✅ `CheckoutFormBuilder` |
| 多步支付 / 3DS 挑战处理 | 🟡 有 3DS 窗口与接口，未接真实发卡行流程 |
| **图片/元素定位**（`bstn` 商品卡、九宫格验证码） | ❌ 依赖视觉匹配服务，见 §7 |

## 4. 任务引擎

### 执行

| 原版 | 复刻位置 | 状态 |
|---|---|---|
| 监控循环 + 可变延迟 | `TaskEngine.RunCoreAsync` | ✅ R144 修过「`Flush` 先删后判」 |
| 并发上限（Settings → Concurrency） | `ConcurrencyGate` | ✅ 5 个单测 |
| 定时启动（`task.startTime`） | `TaskEngine` 等待逻辑 | ✅ |
| 监控过滤器（按站点族开关） | `MonitorFilterPolicy` | ✅ |
| 账号绑定 | `BotTask.AccountId` → `CheckoutContext.Account` | ✅ |
| Profile 绑定 | `BotTask.ProfileId` → `CheckoutContext.ProfileData` | ✅ |
| 代理组绑定 + 轮换 | `BotTask.ProxyGroupId` → `ProxyRotator` | ✅ |
| 任务组合（多商品 × 多 Profile × 多账号） | `TaskCombinationRequest` | ✅ |
| 任务分组 | `TaskGroup` + `GroupSummary` | ✅ R124 修过「后写赢」 |
| 抢购统计（成功率 / 花费 / 用时） | `CheckoutStats` | ✅ |
| 错误目录（按步骤归类失败原因） | `ErrorCatalog` + `StepStage` | ✅ **9 个步骤阶段** |
| 失败重试与退避 | `TaskEngine` 重试循环 | ✅ |

### 步骤动作（`StepActionRegistry`，14 个）

原版把结账拆成可组合的动作，复刻同名注册：

```
Account-Login                     Account-LoginVerify2FA
Account-SubmitRegistration        Account-VerifyTwoFactorEmailCode
Account-CheckLogin                Adyen-Authorize3DS2
Adyen-PaymentFromComponent        Adyen-PaymentsDetails
COShipping-Form                   CSRF-Generate
Product-Variant                   Sites-asics
Kasada-Sensor                     Queue-Pass
```

### 智能动作（`SmartActionEngine`）

| 维度 | 取值 | 数量 |
|---|---|---|
| 触发（`SmartTrigger`） | `CheckoutSuccess` / `Decline` / `Captcha` / `TaskFailed` / `TaskStarted` | **5** |
| 动作（`SmartActionKind`） | `Webhook` / `Notification` / `StopTask` | **3** |
| 过滤器（`SmartActionFilter`） | 站点 / 商品 / 价格 / 尺码 / 结果 | ✅ |
| 表达式（`ExpressionEngine`） | `{product}`, `{price}`, 比较与算术 | ✅ |
| 模板（`SmartActionUtilitiesDocument`） | 可发布/导入 | ✅ |

**这一节在 R161 之前只有 7 行**，全是执行层的绑定关系。步骤动作、智能动作、统计、
错误目录、任务组合——**一样都没有**。

### 被变异检查覆盖的部分

`PARALLEL` 的 17 条变异里有 5 条打的是这一层：

| 变异 | 守护 |
|---|---|
| `Flush` 先出队再检查 sink | `Flush_WithNoSink_KeepsEveryEvent` |
| catch 消息被下一行覆盖 | `NoStatusWriteImmediatelyFollowsItsOwnCatch` |
| 新写一个死按钮 | `NoNewStatusOnlyButtons` |
| 跨层 await 丢掉 `ConfigureAwait` | `UiAwaitsPinTheirContinuation` |
| 一次性 settings 对象 | `NoUiFieldHoldsAThrowawaySettingsObjectWhileSaving` |

## 5. UI

**85 个 UI 类：26 个 `Window` 子类 + 59 个 `UserControl` 子类。**
> **口径说明（R326）**：这里的"UI 类"只数 `Window` / `UserControl` 子类（当前 85 = 26 + 59）。
> `UnreachedUiTypesTests` 与指南用的是**另一个分母** —— `Cybersole.Ui` 里所有 public class（当前 104，其中 31 个从未构造）。
> 两个数字都对，**不要试图把它们对齐**：一个是"窗口/控件"，一个是"全部 UI 类型"。


这一节在 R162 之前列了 11 行。它不假——那 11 个都真的在——但它只覆盖了 **64 个里的 11 个**，
而且 R100–R124 那 24 轮修的 **45 个 UI 缺陷**一个都没记。

### 主结构

| 原版 | 复刻位置 | 状态 |
|---|---|---|
| 主窗口 6 页（Tasks/Accounts/Proxies/Analytics/Settings/Logs） | `MainWindow` + `SettingsShell` | ✅ |
| 左侧导航 + 状态栏 | `MainWindow`（`UiKit` 统一间距/圆角/字号） | ✅ |

### 独立窗口（24 个，择要）

| 窗口 | 用途 |
|---|---|
| `TaskEditorWindow` | 任务编辑器（含账号/Profile/代理组下拉） |
| `AccountImportWindow` | 账号导入（`ImportParser`） |
| `ProfileEditorWindow` | Profile 编辑 |
| `SolverWindow` | Captcha 求解面板 |
| `MonitorWindow` | 监控/调试 |
| `ThreeDSWindow` | 3DS 挑战 |
| `CustomBrowserWindow` | 浏览器（🟡 HTTP 抓取替代 DotNetBrowser，无 Chromium 渲染） |
| `SmartActionEditorWindow` | 智能动作编辑 |
| `ActionsModal` / `PublishTemplateModal` / `HistoryWindow` | 智能动作的弹窗、模板发布、历史 |
| `LicenseWindow` / `SignInWindow` / `GoogleLogin` | 授权与登录 |
| `MessageBoxDialog` / `InputModal` / `DropdownModal` / `StoreGroupModal` | 通用弹窗 |
| `DesktopNotification` / `NotificationView` | 桌面通知 |
| `StaggerStartView` / `UserView` / `YoutubeWindow` | 辅助 |

### 设置页（21 个 `UserControl`）

```
GeneralSettings  Appearance  Advanced  Data  KeyBinds  Help
Payment  Checkout  Profile  ProfileCreator  ProfileCsvEditor  ProfileGroup
CaptchaProviders  CloudflareSolvers  CustomSizes  CustomStores
Notifications  Webhook  Imap  GoogleAccounts  PayPalAccounts
```

### 任务页（9 个）

```
TaskCreator  TaskDetails  TaskGroupList  TaskGroup  Task
SmartActions  SmartActionsCreator  SmartActionSettings  Template
```

### 其它

| 项 | 复刻位置 | 状态 |
|---|---|---|
| Analytics 图表 | `AnalyticsView` + `StoreBarChart`（自绘）+ `ExportService`（CSV） | ✅ |
| 全局快捷键 | `KeyBindMatcher` + 按页作用域 | ✅ |
| 统一外观常量 | `UiKit`（间距/圆角/字号/状态栏工厂） | ✅ |
| **字体** | — | ❌ 见下 |

### 字体：原版用 Gotham，复刻用系统默认

原版从 `cdn.cybersole.io/fonts/` 加载 **Gotham 的 32 个变体**（16 个字重/斜体 × woff/woff2）：

```
Thin  XLight  Light  Book  Medium  Bold  Black  Ultra
（每一个都另有 Italic，各含 woff 与 woff2）
```

**实测这 32 个 URL 现在仍然全部 200**（`Head` 请求，无一例外）。

**复刻的 UI 没有任何 `FontFamily`**——除了 3 处 `Consolas,monospace`（账号导入、浏览器、
日志输出）。其余全部用 Avalonia 的默认字体（Windows 上是 Segoe UI）。

**为什么不补**：

**Gotham 是 Hoefler&Co 的商业字体。** 原版从自己的 CDN 提供它，说明它有分发许可；
复刻从同一个 CDN 下载再打包，是在用别人的许可做自己的分发。

**这一条和 §7 那些「厂商服务」不同**：那些是「服务端不在我这里」，
这一条是「素材的许可不在我这里」。**两者的处理方式相同——记录，不假装能补。**

**它不影响功能**：字号、字重、行高、布局都用 `UiKit` 的常量，换字体不会改变任何行为。
**差的只是字形。**

### R100–R124 那 45 个缺陷，现在有 5 道守卫

| 测试 | 防的是什么 | 在变异表里 |
|---|---|---|
| `StatusOverwriteTests` | **状态栏写成功，catch 里又写一次失败**（3 条断言） | ✅ 2 条变异 |
| `DeadButtonTests` | **按钮点了只写状态文字**（`Known` 列表 + 反向断言「列表不能烂」） | ✅ 1 条变异 |
| `SettingsShellTests` | 设置页签的注册与切换 | — |
| `SettingsModalTests` | 弹窗打开/关闭/焦点 | — |
| `UiContinuationTests` | **UI 层跨层 `await` 必须 pin continuation** | ✅ 1 条变异 |
| `AnalyticsAndModalTests` | 图表与弹窗的交互 | — |
| `KeyBindMatcherTests` | 快捷键匹配 | — |

**为什么「在变异表里」这一列重要**：`StatusOverwriteTests` 和 `DeadButtonTests` 都曾经是
装饰性的——测试绿，缺陷原样在。R143–R149 把它们变成真守卫的方式是**故意把缺陷改回去，
确认测试会红**。没进变异表的那几道，还没被这样验过。

## 6. 通知与自动化

| 子系统 | 复刻位置 | 行数 | 状态 |
|---|---|---|---|
| 通知分发（中心 + 桌面 + 声音 + webhook） | `NotificationService` | 81 | ✅ |
| Webhook（Discord 格式，按 `settings.webhooks` 逐条发） | `NotificationService.SendWebhookAsync` | — | ✅ |
| 邮件收码 — AYCD | `AycdInboxClient`（`inbox-api.aycd.io`） | 301 | ✅ |
| 邮件收码 — IMAP | `ImapMailProvider` | 273 | ✅ |
| 请求分析上报 | `HttpAnalytics.Flush`（ClickHouse `JSONEachRow`） | 193 | ✅ |
| Smart Actions（触发 → 过滤 → 动作） | `SmartActionEngine` | — | ✅ |
| CSV 导出 | `ExportService` | 54 | ✅ |

### `NotificationService`

```
in-app centre（.Shown 事件） + 桌面 toast + 声音 + webhook
选项来源：settings.notificationOptions
webhook 来源：settings.webhooks（逐条判断 .Enabled）
```

**`NotificationKind` → `NotificationOptions`** 是一个 `switch`，所以「哪些事件弹窗、哪些出声、
哪些发 webhook」是**每类事件独立配置**的，不是一个全局开关。

### 邮件收码：两条路

| 路由 | 协议 | 用途 |
|---|---|---|
| `AycdInboxClient` | HTTPS（`inbox-api.aycd.io/api/v1/tasks/{completed,mail/create}`） | AYCD 的托管收件箱 |
| `ImapMailProvider` | IMAP | 自有邮箱 |

**两条路产出同一个 `MailCodeResult`**（`Ok` / `Code` / `Subject` / `From` / `Received` / `Error` /
`Source`），所以调用方不需要知道走的是哪条。`Source` 字段就是为此存在的。

### `HttpAnalytics`

**不是「通知」，是「批量上报」**——它把每个请求的 `{Url, Method, Status, ElapsedMs, Bytes,
Protocol, Profile, Proxy, Tag}` 攒起来，`Flush()` 时以 `application/x-ndjson` 一次性 POST 到
`SinkUrl`。

**R127 修过一个缺陷**：`Flush()` 原来先出队再检查 sink，sink 为 null 时事件被扔掉。
现在是**检查在前**，且 `Flush_WithNoSink_KeepsEveryEvent` 守着它（变异表里有对应条目）。

### 这一节在 R163 之前只有 4 行

漏了 **AYCD 收码（301 行）**、**IMAP（273 行）**、**`HttpAnalytics`（193 行）**——
**三样加起来 767 行，一个字都没提。**

## 7. 不复刻的部分

**每一项都要写清「怎么验证这个理由还成立」**——一条不复刻的理由如果无法被检验，
它就会永远停在「当时是这么想的」。

| 项 | 原因 | 怎么验证这条理由还成立 |
|---|---|---|
| `api.cybersole.io` 授权/许可校验 | 属厂商服务端；复刻版用本地 `LicenseService` 模拟同一状态机 | `GET https://api.cybersole.io/health` → **200** |
| 遥测 / Analytics 上报（`telemetry/`、`cdn.cybersole.io`） | 同上，且无必要 | 根路径**有 HTTP 响应**（当前 404）——即「域名还在，只是没这个路由」 |
| Velopack 自动更新 | 与功能无关 | `FeedUrl` 指向 `https://cdn.cybersole.io/releases/`，**该路径下全部 404**（R178 测了 RELEASES / releases.win.json / releases.json / win/ / latest / index.json）——厂商已不再发布，但字体和图标路径仍 200 |
| DotNetBrowser 内嵌 Chromium | 体积/许可证问题，改用 HTTP 抓取 + 自写 TLS | 不依赖网络：`src/` 里没有对 `DotNetBrowser` 的程序集引用 |
| **视觉匹配子系统**（`match.cybersole.io`） | 见下 | `GET https://match.cybersole.io/health` → **200**，body 含 `"service":"match-edge"` |

**前三条的理由依赖厂商服务还在**，所以它们的验证只要求「有响应」，不要求「200」：

- **404 是好消息**——它证明 DNS 解析成功、TLS 握手成功、服务器回了话，只是这个路径没有东西
- **超时或 DNS 失败才是坏消息**——那说明域名没了，「属厂商服务端」这条理由就变成了
  「那个服务不存在了」，含义完全不同

**表上看不出这个区别，所以最后一列写明了要区分什么。** 这张表的三条网络检查在
`NonParityClaimsTests`（`Speed=Slow`）里，不放进快速测试。

### 视觉匹配：原版接了第三方模型

原版有一个独立服务，`match.cybersole.io`（备用节点在 Modal 上），只暴露 `POST /match`。
它的 `/health` 自报能力（证据等级 A，服务自己写的）：

```json
{ "ok": true, "service": "match-edge", "routes": ["POST /match"],
  "embed_endpoint_configured": true, "embed_key_configured": true, "coalescer_shards": 4 }
```

| 端点 | 方法 | 用途 | 成本 |
|---|---|---|---|
| `/match` | `clip-cosine-similarity (text → images)` | 文本类别 → 图片排序 | ~$0.00055 / 9 图 |
| `/detect` | `segmentation → clip-embed → cluster → singleton` | 找出没有配对的那个 | ~$0.0005 |
| `/oddone` | `cv-detect → vlm select over numbered crops` | 找出不同的那个 | $0.0005–$0.0016 |
| `/locate` | `tile-detect + siglip text-match` | 在图中找子图 | ~$0.0005 |

模型是 **`google/siglip2-base-patch16-256`**（Google 开源的图文匹配）+ **`claude-haiku-5-5`**
（Anthropic 的 VLM，用来在编号裁剪图上选一个）。

**这解释了 `bstn` 的产品卡为什么找不到 CSS 选择器**：原版不解析 DOM，它截图、切 tile、
用 SigLIP2 算「文本 → 图片」的余弦相似度排序。`Question.html`（只有一个 `<input>` 的那个
captcha 页）同理——输入什么由 `/oddone` 算出来。

**不复刻的理由**：

1. 需要跑模型（Python + PyTorch，约 400 MB），是另一个技术栈，不在这个 C# 仓库里
2. `/match` 裸调返回 400，`embed_key_configured: true` 说明要认证
3. 文档写明按调用计价（$0.00055 / 9 图）——**那是一笔订阅，不是一段代码**

**所以这一层的对等程度是「知道它存在、知道它怎么工作、知道为什么不在」，
不是「实现了」。** 涉及依赖它的模块（`bstn` 的商品定位、`Question` 类验证码）也一并
是这个状态。

### Cloudflare：客户端在，服务在厂商那边

**这一节在 R175 之前不存在。** 字符串表里有八个 Cloudflare 名字，看起来像一整块缺口：

```
CloudflareSolver      CloudflareResult         ICloudflareSlots
CloudflareJsdHandler  CloudflareClearanceCache CloudflareChallengeReplay
CloudflareBrowser     RemoteConcurrencyKey = "Cloudflare-Remote-Concurrency"
```

查下去分成两类：

| 二进制里的 | replica 里的 | 性质 |
|---|---|---|
| `CloudflareSolver` / `CloudflareResult` / `ICloudflareSlots` / `__FromCloudflareSolver` | **`CfSolverDriver`** | ✅ **客户端完整** |
| `CloudflareJsdHandler` / `JsdResult` / `IJsDialogs` | — | ❌ 依赖 DotNetBrowser（见上表） |

**`CfSolverDriver` 和原版是同一层**：

```csharp
public const string BaseUrl = "https://cf-solver.cybersole.io";
POST /solve  { token, sitekey, url, proxy, userAgent, action }
→ { token } 或 { cf_clearance }
```

**实测**：`GET https://cf-solver.cybersole.io/health` → `200 {"ok":true,"version":"2e5c5554dfbf"}`；
其余所有路径（`/`、`/solve`、`/docs`、`/openapi.json`）→ **401**。

**404 会说明「这个路径不存在」，401 说明「它存在，你没有 key」。** 和视觉匹配一样：
**服务是厂商的，客户端是自己的。**

**`IJsDialogs` 是个误认**：它看起来像 Cloudflare 的一部分，其实是 DotNetBrowser 的
JS 对话框接口（`InitializeDefaultJsDialogs` / `DeinitializeDefaultJsDialogs` 是它的方法）。
`CloudflareJsdHandler` 建在它上面，所以那个 handler 也不是独立能力，是内嵌浏览器的衍生品。

**所以「Cloudflare 支持」的对等程度是：能调，不能算。** 这和 §7 表里那条
「DotNetBrowser 内嵌 Chromium」是同一个缺口的下游。

## 8. 交付指标

数字取自仓库本身（`analysis/count_repo.py` 的同一套规则：排除 `obj/` `bin/`，
注释行不算代码）。

| 指标 | 数值 |
|---|---|
| 源文件 | **133 个 `.cs`**（`src/`）+ 115 个（`tests/`）= 248 |
| 代码行数 | **25,643**（不含注释与空行；含则为 33,142） |
| 注释行数 | 2,855（源）+ 1,457（测试） |
| 单元测试 | **643 个通过 / 0 失败 / 2 跳过** |
| 慢测试（`-Full`） | 895 个通过（含 61 域名的可达性扫描、浏览器探测） |
| 变异检查 | **17 条**，全部 `guard fired`；自检 **5/5** |
| 站点模块 | **62 个**注册 |
| 传输模式 | **5 种**：`SChannel` / `BouncyH2` / `OwnTls` / `BouncyHttp11` / `PureNetClient` |
| 内嵌资源 | **21 个**（`Core` 19：4 语言字典 + 14 引擎资产 + 1 份 CSV 校验名单；`Http` 2：Brotli 字典 + `RootCertificates.bin` 121 条根证书库） |

R704 加了第 20 个：`Data\ProfileValidation.en.json`（244 国 / 50 州）—— `ProfileCsvEditorView` 的 Country/State 校验要用它；规则由 R702 反编译解出、R703 复验。

### 分项目

| 项目 | 文件 | 行数 | 代码 | 注释 |
|---|---|---|---|---|
| `Cybersole.Core` | 22 | 2,601 | 1,931 | 312 |
| `Cybersole.Http` | 21 | 4,110 | 3,261 | 329 |
| `Cybersole.Services` | 21 | 3,388 | 2,575 | 297 |
| `Cybersole.Stores` | 40 | 13,853 | 10,347 | 1,346 |
| `Cybersole.Ui` | 29 | 9,190 | 7,529 | 571 |
| `Cybersole.Tests` | 115 | 13,525 | 10,014 | 1,457 |

**这张表在 R154 之前一直写着「88 个 `.cs` / 10,6xx 行 / 137 个测试 / 50 个模块」**——
那是它写下时的真实数字，之后 40 多轮没有回来改过。

**留着这句话是有意的**：一张对照表最容易烂的地方不是内容错，是**没人回去核对**。
数字改了不重要，**知道它为什么会旧**才重要。

**内嵌资源那一行在 R167 之前写的是「22 个（4 语言字典 + 14 引擎资产 + Brotli 字典 +
3 编译期）」**——4 + 14 + 1 = 19 是对的，**「3 编译期」是凑数凑上去的**，
项目里没有这样的东西。`EmbeddedResource` 在仓库里一共 19 条，`ParityDocTests` 现在数它。

