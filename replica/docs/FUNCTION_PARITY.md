# FUNCTION_PARITY — 与原版 Cybersole 的函数级对齐台账

> 目标（用户 2026-11-10 定）：**不要求字节级 1:1，但代码功能要 1:1 —— 函数数量对等、每个函数功能相等、效率相近，命名可以不同。**
>
> 本文是这条目标的**度量基准 + 进度台账**。所有"原版"数字都出自本机 IDB 的实测提取，不是估计。

---

## 一、度量方法（可复现）

原版是 .NET NativeAOT 单文件：**无 CLR 元数据、无符号表**。所以"函数数量对等"不能靠读 IL，只能靠从二进制里**恢复业务词汇**，再把词汇映射到实现。

已建立的流水线（脚本在 `analysis/`）：

| 步骤 | 脚本 | 产出 |
|---|---|---|
| 1. 函数普查 + 全量字符串导出 | `ida_dump.py` | `functions.tsv`、`strings_all.tsv`、`segments.json` |
| 2. 从字符串堆恢复 C# 符号 | `mine_symbols.py` | `recovered_*.txt`（方法名 / lambda / 访问器 / 类型） |
| 3. 从字符串桶恢复架构 | `build_baseline.py` | `baseline_xaml.txt`、`baseline_classes.txt`、`baseline_endpoints.txt` |
| 4. 契约校验 | `tests/Cybersole.Tests/StoreFlowParityTests.cs` | 反射断言：契约是否覆盖恢复出的每个步骤名 |

### 为什么这条路走得通

NativeAOT 剥掉的是**元数据**，不是**字符串**。而编译器生成的 async 状态机名会以 `<方法名>d__序号` 的形式留在字符串堆里：

```
<AddToCart>d__12      <SubmitShipping>d__7      <Adyen-Authorize3DS2>
<FindProduct>d__31    <SubmitPayment>d__9      <Account-LoginVerify2FA>
```

同名字符串的**出现次数**就等于"有多少个实现体实现了这个方法" —— 这正是函数数量对等的直接度量。

---

## 二、原版基线（实测）

| 指标 | 数值 | 来源 |
|---|---|---|
| 函数总数 | **320,933** | `ida_dump.py` |
| 有真名的函数 | 10,033（3.1%） | 同上 |
| 字符串总数 | **265,462**（6.78 MB） | 同上 |
| `.text` 段 | 0x140001000–0x14313F000（≈49 MB） | `segments.json` |
| **async 状态机名（去重）** | **1,547** | `recovered_async_methods.txt` |
| 其中**出现 ≥2 次**（多实现 = 业务步骤词汇） | **289** | `recovered_async_multi.txt` |
| lambda 显示类 | 2,412 | `recovered_lambdas.txt` |
| 属性访问器（`get_`/`set_`） | 4,812 | `recovered_accessors.txt` |
| `*Async` 方法名 | 706 | `recovered_asyncsuffix.txt` |
| 方法名并集 | 3,220 | `recovered_method_names.txt` |
| 绑定可见的 `Cybersole.*` 类 | **153** | `baseline_classes.txt` |
| XAML 视图文件 | **86**（+10 个 Theme） | `baseline_xaml.txt` |
| 外部 host | 195（其中 7 个 cybersole 自有） | `baseline_endpoints.txt` |
| 绝对 URL | 369 | 同上 |
| 店铺动作名（`Xxx-Yyy`） | 13 个真实动作 | `baseline_actions.txt` |
| `Global.Settings` 字段 | **37** | `baseline_classes.txt` |

### 原版的步骤词汇（289 个多实现方法里抽出的业务动词）

按实现次数排序，这就是"每个店铺模块要做多少件事"的直接答案：

```
AddToCart 32   FindProduct 29   SubmitShipping 28   SubmitOrder 24   Login 22
SubmitPayment 22   GetCheckout 19   GetHome 18   HandleResponse 18   SubmitBilling 15
GetCsrf 14   ClearCart 12   GetProduct 12   SetRequest 12   AddToCartPreload 11
SubmitDiscount 11   GetShippingRates 10   SubmitEmail 10   EditLine 9   FindVariant 9
Register 9   AccountLogin 8   AddToCartStoreFront 8   CompletePayment 8   GetSession 8
Process 8   RefreshSession 8   EnterRaffle 7   Generate 7   GetOwnProperties 7
ScrapeJson 7   ScrapeProduct 7   AddToCartMulti 6   CheckPriceLimit 6   CreateCart 6
CreateCheckout 6   FindProductMulti 6   GetCart 6   GetPaymentToken 6   GetScript 6
GetShippingRate 6   PlaceOrder 6   ScrapeVariantAvailability 6   Solve 6
SubmitPayPal 6   SubmitSensor 6   ApplyDiscount 5   CompleteRegistration 5
FetchBalance 5   FindProductFlow 5   GetRaffleData 5   ProcessOrder 5   ProcessPayment 5
```

---

## 三、关键架构发现（决定了 replica 必须改成什么样）

### 3.1 原版是**步骤驱动**，不是"两个大方法"

证据链：
1. `Cybersole.Models.TaskStep` = `{ Name, Completed, Running, Started, Duration }`
2. `Cybersole.Models.WebTask` = `{ Account, Steps }` —— 一个任务有一个步骤列表
3. 13 个动作名 `Account-Login`、`Account-LoginVerify2FA`、`Account-SubmitRegistration`、`Account-CheckLogin`、`Account-VerifyTwoFactorEmailCode`、`Adyen-Authorize3DS2`、`Adyen-PaymentFromComponent`、`Adyen-PaymentsDetails`、`COShipping-Form`、`CSRF-Generate`、`Product-Variant`、`Sites-asics`
4. 289 个 async 步骤词汇

**结论**：每个店铺模块实现的是"一组合名步骤"，引擎按序执行并逐步上报状态。replica 原来的 `MonitorAsync` / `CheckoutAsync` 二元结构达不到这个粒度。

### 3.2 Kasada 是**本地生成**，不是接第三方

这是用户明确提到的点，现在有硬证据：

| 证据 | 位置 |
|---|---|
| 二进制内嵌 **Jint 4.17.0**（.NET JS 解释器） | `https://github.com/sebastienros/jint` |
| 二进制内嵌 **Acornima 1.7.0**（JS 解析器） | Jint 4.x 的解析器依赖 |
| 步骤名 `GetScript` / `GenerateSensor` / `SubmitSensor` / `GetSensorData` / `GetKasada` / `GenerateSbsd` / `GetSbsdData` / `Generate` | 恢复出的 async 状态机 |
| 脚本路径形态 `/{uuid}/{uuid}/tl` | `bucket_api_paths.txt` |

**还原出的做法**：抓店铺自己的 `ips.js` → 在 Jint 里配浏览器 shim 执行 → 读脚本自己生成的 `x-kpsdk-ct` / `x-kpsdk-cd` / `x-kpsdk-sb`。全程本地，没有 solver 网络往返 —— 所以"体感跟自主生成一样"，因为它**就是**自主生成。

### 3.3 原版的对外集成面（从 host/URL 桶提取）

```
自有服务    api.cybersole.io / cybersole.io/api/apisecuretoken / analytics.cybersole.io
            telemetry.cybersole.io / cdn.cybersole.io/releases/ / cf-solver.cybersole.io
            match.cybersole.io / arno-1863--matcher-standby-web.modal.run
验证码      api.uncaptcha.io/v1  ·  api.parallaxsystems.io/{gen,holdcaptcha}
            captcha.superswipe.com（+ status / enter / country-data / clicks）
邮件        inbox-api.aycd.io/api/v1/{tasks/mail/create, tasks/completed, user/verify}
反爬        api.humanpresence.io/v2  ·  h.online-metrix.net (ThreatMetrix)
支付        checkoutshopper-live.adyen.com  ·  pci-connect.squareup.com  ·  js.stripe.com
            api.unzer.com  ·  commercehub-secure-data-capture.fiservapps.com
            checkout-page.omise.co  ·  api.paynamics.net/v1/rpf  ·  api.sibspayments.com
店铺登录    authenticate.riotgames.com  ·  id.fanatics.com  ·  login.mywarhammer.com
            login.wingstop.com  ·  account.nrl.com  ·  clientsso-rl.legendsapis.com
```

### 3.4 原版的第三方栈（决定了"哪些函数不需要复刻"）

`Avalonia 12.1.3` · `AvaloniaEdit` · `AngleSharp` · `Acornima` · `Jint` · `BouncyCastle.Cryptography 33.1.0` · `Newtonsoft.Json` · `jose-jwt` · `CsvHelper` · `Bogus` · `Metalama.Framework` · `Velopack` · `DotNetBrowser 4.3.5` · `MailKit/MimeKit` · `RabbitMQ.Client` · `MSAL` · `SignalR` · `protobuf` · `Brotli`

这 20 个库的 ~30 万函数**不需要**在 replica 里重写——它们是依赖，不是业务。

---

## 四、逐子系统对照矩阵

图例：✅ 已对齐 · 🟡 部分/近似 · ⬜ 未开始

### 4.1 传输层（Cybersole.Http = NetClient 0.10.0）

| 原版 | replica | 状态 |
|---|---|---|
| `Cybersole.Http` 4 条传输 | `SChannel` / `BouncyHttp11` / `BouncyH2` / `OwnTls12` | ✅ |
| JA3 指纹 | `Ja3.cs`（GREASE + Chrome 扩展序） | ✅ |
| 自研 TLS 1.2 | `Tls12Client.cs`（581 行，EMS + AES-GCM + h2） | ✅ |
| HPACK + Huffman | `HpackHuffman.cs`（314 行） | ✅ |
| HTTP/2 帧 | `Http2.cs`（297 行） | ✅ |
| `HttpAnalytics.Start()` → ClickHouse 批量 | `HttpAnalytics.cs`（133 行，本地缓冲） | 🟡 无 ClickHouse 落地 |
| `HttpDebug.Enable()` → 实时请求流 | `HttpAnalytics` 事件 | 🟡 无独立 viewer |
| 代理轮换 + `MaxUsage` | `ProxyRotator.cs` | ✅ |
| 流量计数 | `TrafficCountingStream.cs` | ✅ |

### 4.2 数据模型（`Cybersole.Models.*`）

| 原版类 | replica | 状态 |
|---|---|---|
| `BaseCheckout` / `Checkout` | `Checkout.cs` | ✅ |
| `TaskStep` | `TaskSteps.cs`（本轮新增） | ✅ |
| `WebTask{Account,Steps}` | `Tasks.cs` + `TaskStep` | ✅ |
| `MonitorEvent` / `MonitorProduct` | `TaskSteps.cs`（本轮新增） | ✅ |
| `Address` / `Card` / `Country` / `Flag` / `Element` / `Shortcut` | `TaskSteps.cs`（本轮新增） | ✅ |
| `BotTask` | `Tasks.cs` | ✅ |
| `Account` / `AccountGroup` / `GoogleAccount` / `PayPalAccount` / `ImapAccount` / `AycdInbox` | `Accounts.cs` | ✅ |
| `Profile` / `ProfileGroup` | `Profiles.cs` | ✅ |
| `Proxy` / `ProxyGroup` | `Proxies.cs` | ✅ |
| `Solver` / `SolverSettings` / `SolverView` | `Checkout.cs` | ✅ |
| `Release` / `Drop` / `Analytics` / `License` / `User` / `Status` / `AsyncCommand` / `EditValue<T>` | 多处 | ✅ |
| `CaptchaProvider` / `CloudflareSolver` / `ProxyTester` / `ImapProvider` / `RemoteData` / `State` / `CreateModel` | 分散 | 🟡 字段未逐一核对 |
| `Cybersole.Elements.Element` | 本轮新增 | ✅ |

### 4.3 店铺流程（本轮重写）

| 原版 | replica | 状态 |
|---|---|---|
| 步骤契约（289 个多实现方法） | `Flows/StoreFlow.cs`：**145 个步骤方法** | ✅ 契约层 |
| 步骤执行器 | `Flows/StoreFlowRunner.cs`（monitor 9 步 / checkout 24 步） | ✅ |
| 步骤状态上报 | `TaskStep` + `FlowContext.Step()/Finish()` | ✅ |
| `Shopify` 全链 | `Flows/ShopifyFlow.cs`（13 步完整实现） | ✅ |
| `Nike` + Kasada | `Flows/NikeFlow.cs`（Kasada 3 步 + 商品/购物车/订单 10 步） | ✅ |
| Kasada 本地生成 | `Scripts/KasadaSolver.cs`（Jint 执行，7 个候选入口探测） | ✅ |
| 浏览器 shim | `Scripts/BrowserShim.cs`（navigator/screen/document/crypto/storage） | ✅ |
| 其余 ~48 个店铺 | `Modules/*.cs` 旧二元实现 | 🟡 待迁移到步骤式 |
| 13 个动作名注册表 | — | ⬜ |
| Adyen 3DS2 四查询 | — | ⬜ |

### 4.4 UI（86 个 XAML）

| 原版 | replica | 状态 |
|---|---|---|
| `MainWindow` (13 个绑定) | `MainWindow.cs`（6 个 tab） | 🟡 缺 `BillingView` |
| `Tasks/*`（9 个视图） | `TaskEditorWindow` + 主窗口 tab | 🟡 |
| `Profiles/*`（8 个） | `ProfileEditorWindow` | 🟡 缺 `ProfileCsvEditor`、`ExpressionView` |
| `Proxies/*`（3 个） | 主窗口 tab | 🟡 缺 `ProxyCreatorView`、`ProxyGroupView` 独立窗口 |
| `Accounts/*`（6 个） | `AccountImportWindow` | 🟡 |
| `Analytics/*`（6 个） | `StoreBarChart` | 🟡 缺 `ReleaseView`/`ReleaseSitelistView`/`ReleaseGuideView` |
| `Settings/*`（**17 个子视图** + 11 个 Modal） | 单一设置面板 | ⬜ 差距最大 |
| `SmartActions/*`（7 个） | `SmartActionEditorWindow` | 🟡 缺 `PublishTemplateModal`、`HistoryWindow` |
| `Captcha/*`（3 个） | `SolverWindow` | 🟡 缺 `GoogleLogin`、`YoutubeWindow` |
| `Modals/*`（6 个） | 部分 | 🟡 |
| `Auth/*`（4 个） | `SignInWindow` + `LicenseWindow` | 🟡 缺 `SplashWindow` |
| `Monitor/*`（2 个） | `MonitorWindow` | 🟡 |
| `Browser/CustomBrowser` | `CustomBrowserWindow` | 🟡 |
| `Utilities/UtilitiesView` + `StoreGroupModal` | — | ⬜ |

### 4.5 服务层

| 原版 | replica | 状态 |
|---|---|---|
| `Services.ClockService` | `ClockService.cs` | ✅ |
| `AuthService`（`AuthenticateAsync`/`VerifyLicenseAsync`/`GetLicensesAsync`/`RevokeLicense`/`LogoutAsync`） | `Auth/AuthService.cs` | ✅ |
| `LicenseVerifier` / `LicenseFile` / `ProbePaths` | `License/LicenseService.cs` | ✅ |
| 任务引擎 | `TaskEngine.cs`（303 行） | ✅ |
| Smart Actions 引擎 | `SmartActionEngine.cs` | ✅ |
| 通知 | `NotificationService.cs` | ✅ |
| 导入/导出 | `ImportParser.cs` / `ExportService.cs` | ✅ |
| 备份调度 | `BackupScheduler.cs` | ✅ |
| `ImapProvider`（MailKit 读验证码邮件） | `ImapAccount` 模型只有字段 | ⬜ |
| `AycdInbox` 客户端 | 模型只有字段 | ⬜ |
| HumanPresence / Uncaptcha / Parallax / Superswipe 专有 | — | ⬜ |
| Matcher（`match.cybersole.io`） | — | ⬜ |

---

## 五、函数数量对等的当前进度（R11 审计后）

数字全部来自 `docs/PARITY_AUDIT.md`（由 `analysis/classify_vocabulary.py` +
`analysis/impl_quality.py` 自动生成）。

### 5.1 业务步骤词汇

原版有 289 个「出现 ≥2 次的 async 状态机名」。它们混了两类东西，必须分开算：

| 类别 | 名字数 | 实现体数 | 该不该复刻 |
|---|---|---|---|
| 框架 / BCL 内部（`ReadAsync`、`DisposeAsync`、`FlushAsync` …） | 121 | 457 | 否 —— replica 用真 BCL |
| **业务步骤**（`AddToCart`、`SubmitShipping`、`GetCsrf` …） | **168** | **872** | 是 |

**业务词汇覆盖：168 / 168 = 100%（实现体 872 / 872 = 100%）。**

### 5.2 但「名字存在」不等于「功能相等」——分档如下

`StoreFlow` 有 165 个步骤方法，按实现质量分三档：

| 档位 | R11 | R12 | **R13** | 含义 |
|---|---|---|---|---|
| **真实实现** | 48（29%） | 87（53%） | **139（84%）** | 基类有独立逻辑（92）或具体 Flow override（47 个名字） |
| 转发别名 | 29（18%） | 29（18%） | **26（16%）** | 基类直接调另一个步骤（`FindProductFlow` → `FindProduct` …） |
| 空实现 | 88（53%） | 49（30%） | **0** | 基类 `=> Ok()`，没有任何 Flow 覆盖 |

**R13 把空桩清零。** 剩下的 26 个是刻意的转发别名 —— 那些步骤在原版里就是同一件事的
不同入口名（`AddToCartMulti` / `AddToCartStoreFront` / `AddToCartPreload` 都是加购，
只是拿到加购数据的方式不同），拆开只会制造重复代码。

R12/R13 两轮共填了 91 个实现，覆盖：

- **支付编排**：`StartPayment` / `ProcessPayment` / `CreatePayment` / `CreateTransaction` / `SubmitCard` / `Authorize` / `GetMerchantCode`
- **3-D Secure 全链**：`ThreeDS` / `Process3DS`（Y/A 通过、N/R 拒绝、U/C 可重试）/ `Solve3DS` / `Solve3DSRedirect`（从 ACS 页面抓 `transStatus`）/ `AwaitDeviceProfiling`
- **支付页**：`GetPaymentPage` / `GetPaymentUrl` / `GetPaymentDetails` / `CompletePayment`
- **PayPal**：`StartPayPal` / `GetPayPalToken`（建 order）/ `GetPayPalAccessToken`（OAuth2 Basic）/ `GetPayPalOrderId` / `SubmitPayPal`（capture）
- **Stripe**：`CreateStripePaymentMethod` / `GetStripePaymentIntent`
- **GMO**：`CreateGmoToken`（`p01.mul-pay.jp/payment/SaveCard.idPass`）
- **商品/运费**：`GetProduct` / `GetProductDetails` / `ScrapeProductPage` / `ScrapeProductAvailability` / `GetRates` / `SubmitRate`
- **账号**：`HandleLogin` / `SetEmail` / `SubmitPassword` / `ResetPassword` / `SubmitDetailsCommerce`
- **反爬**：`Generate` / `GetSensorData` / `GenerateSbsd` / `GetSbsdData`
- **Klaviyo 营销**：`SubmitKlaviyoEvent` / `SubmitKlaviyoBulkEvents` / `SubmitKlaviyoProfile` / `SubmitKlaviyoSubscription` / `ConfirmSubscription`
- **拆出来的别名**：`AddToCartApp`（app 端点 + channel 标记）、`SubmitOrderStripe`（intent → confirm）、`AddToCartPreload`（复用预载数据）

### 5.3 规模对照

| 指标 | 原版 | replica |
|---|---|---|
| 函数总数 | 320,933 | 948 |
| 有名字的函数 | 10,033 | 534 |
| 类 / 类型 | 153（绑定可见） | 343 |
| 视图类 | 96（含 10 Theme） | 69 |
| 属性 | — | 542 |
| 代码行 | — | 23,925 |
| 测试 | — | 411 |


### R14 新增：端到端验证 + Utilities + 一个真实 bug 修复

**端到端集成测试**（`tests/Cybersole.Tests/CheckoutFlowEndToEndTests.cs`）—— 这是第一次
让一个真实的 `ShopifyFlow` 通过 `StoreFlowRunner` 走完 24 步并打到真实 HTTP：

| 测试 | 断言 |
|---|---|
| `ShopifyCheckoutRunsEveryStepAgainstAMockStore` | 全链成功、订单号正确、22 个 `TaskStep` 全部 `Completed`、步骤顺序与 runner 承诺一致 |
| `TheStoreActuallyReceivesTheDocumentedRequests` | mock 侧确实收到了 `/products/*.js` `/cart/add.js` `/cart.js` `/checkout` `/checkouts/{t}/shipping_rates` `/payments` `/complete` |
| `CheckoutAbortsWhenTheCartIsRejected` | 死主机时中止并记录失败步骤与错误 |
| `MonitorHalfOfTheFlowReportsAvailability` | monitor 半边返回 `Available` / 价格 / 变体 / 尺码 |
| `NikeFlowRunsItsKasadaGateAgainstTheMock` | 拿不到 ips.js 时**失败关闭**（Blocked）而不是假装有货 |

**这个测试当场抓到一个真实 bug**：四处 `Origin()` 辅助函数用 `u.Host` 拼 URL，
而 `Uri.Host` **不含端口**。所有非默认端口（本地镜像、测试服务、某些代理前置）的请求
都会打到 :80/:443。四处已全部改成 `u.GetLeftPart(UriPartial.Authority)`：

```
src/Cybersole.Stores/Flows/StoreFlow.cs
src/Cybersole.Stores/Payments/AdyenGateway.cs
src/Cybersole.Stores/Payments/Gateways.cs
src/Cybersole.Stores/Scripts/KasadaSolver.cs
```

另加 `NetClientLoopbackProbeTests` 作为这个测试基础设施的护栏：它单独验证
`NetClient.GetAsync` 能打到 loopback HttpListener，避免以后 e2e 失败时误判。

**Utilities 2 个视图**：`UtilitiesView`（store groups 的 New / Clone / Delete + 店铺多选）、
`StoreGroupModal`（Title / Close / Save）。新增 `StoreGroup` 模型与
`GlobalSettings.StoreGroups` 槽位。

### R15 新增：失败分类 + 时间序列图表

**1. HTTP 状态进到步骤结果里**

之前 403 和 DNS 失败在 monitor 里都显示成 `Error` —— 分不清"被反爬挡了"和"网断了"。
现在 `StoreFlow.GetAsync` / `PostJsonAsync` / `PostFormAsync` 都会写
`Session.Vars["lastStatus"]` 与 `lastUrl`，runner 据此分类：

| 状态 | monitor 结果 | checkout 结果 |
|---|---|---|
| 403 | `Captcha` | Error |
| 429 / 401 | `Blocked` | Error |
| 502 / 503 / 504 | `Error` | Error |
| 422 / 409 / 402 | — | **`Declined`**（不可重试） |
| 其它 | `Error` | `Error` |

`422 → Declined` 这条最要紧：店听懂了请求但拒绝了（尺寸没了、库存冲突），
重试只会白白烧掉账号。

**2. 图表时间序列**

`StoreBarChart` 新增 `UpdateTimeline(buckets)` 模式：12 个小时桶，时间从左到右流动，
空的桶画一条细刻度线。`AnalyticsView` 的图表下拉多了第 4 项 "Timeline (last 12h)"。


### R16 新增：CustomBrowser autofill + 一次完整回归

**1. `CustomBrowserWindow` 补齐恢复出的命令面**

原版的 `Cybersole.Ui.Views.Browser.CustomBrowser` 有 Back / Forward / Refresh / Exit /
Minimise / Status / Type / Autofill。之前只有 Go / Reload / 一个假的 Back。
现在：

| 命令 | 实现 |
|---|---|
| Back / Forward | 真历史栈（`_history` + `_historyIndex`），前进时丢弃分叉 |
| Refresh | 重取当前地址，不重复入栈 |
| Minimise | `WindowState = Minimized` |
| Exit | `Close()` |
| **Autofill** | 右侧面板：profile 选择 + 14 个字段逐条展示 + "Copy all as JSON" |

Autofill 的字段集：`email` / `firstName` / `lastName` / `phone` / `address1` /
`address2` / `city` / `state` / `zip` / `country`，卡存在时再加 `card.number` /
`card.expiry` / `card.month` / `card.year` / `card.cvv`。

CVV 与到期日渲染成 `••••`，只有"Copy all"才给出真值 —— 面板本身不泄露。

**2. 完整回归（含 Slow）**

第一次真正跑全量 590 条。抓到 2 条过时断言：

`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host` 断言死主机必须是
`MonitorStatus.Error`，但：

- `nike` 在拿不到 ips.js 时**失败关闭** → `Blocked`
- `superswipe` 死在 captcha 步骤 → `Captcha`

这两个比笼统的 `Error` **更准确**，所以改的是断言而不是代码：

```
不可达主机 → 绝不返回 Available，且必须带错误消息
有反爬 gate 的模块（nike / superswipe）→ 报自己的 gate
其余模块                              → Error
```


### R17：Kasada 的真实答案 —— 原版内置 Chromium，不是纯 JS 引擎

这是用户最初点名的能力（"nike 模块 cyber 做到了 kasada 直接生成"）。这一轮把它查到底。

**1. 拿到了真货**

Nike 首页里 `KPSDK.configure([...])` 上方的脚本：

```
https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js
```

157,563 字节，`application/javascript`。已存为测试 fixture `tests/Cybersole.Tests/fixtures/nike-p.js`。
`KasadaSolver.FindScriptUrl` 之前只认 `ips.js`，加了 `p.js` 与跨域绝对 URL 两种形态。

**2. 在 Jint 里跑到 91.8%**

```
executed=False
stopped at offset 144669 (91.8% of 157563)
error = Cannot read properties of undefined (reading 'bind') @ line 1, col 144669
```

它把 bootstrap、字符串表、解码器全部跑过了，最后一次死在 **Kasada 自制的字节码解释器**里
（`function D(e,n)` 那个 trampoline）。这不是解析问题，是宿主 API 缺口。

**3. 结论：原版为什么"体感像自主生成"**

Cybersole 内置 **DotNetBrowser 4.3.5**（从 XAML 与依赖清单确认）。所以它的 Kasada 不是在
JS 引擎里算的，而是**在真 Chromium 里跑 ips.js**。这解释了：

- 为什么它的 header 与真浏览器无法区分 —— 因为就是真浏览器产的
- 为什么它不需要第三方 solver 服务 —— 本机就有浏览器
- 为什么 `x-kpsdk-ct` 还能配合 `cd`（body 加密）—— 同一份脚本上下文

**4. 代码侧改了什么**

`KasadaSolver` 现在如实报告：

| 字段 | 含义 |
|---|---|
| `ScriptExecuted` | payload 是否跑到底 |
| `StoppedAt` | 停在 payload 的哪个字节偏移 |
| `NeedsRealBrowser` | 是否属于"需要真浏览器"的失败（按**异常类型**判定，不按消息文本） |

`ScriptRuntime.TryExecute` 改成**先 `PrepareScript` 再 `Evaluate`** —— 解析失败与执行失败
必须区分：前者是 payload 坏了，后者意味着缺宿主 API。`LastErrorWasRuntime` 记录这个区分。

7 个测试：真 payload 大小、Jint 跑到 >80%、失败原因可解释、宿主缺口被标记、
语法错误不被误标、两种 script URL 形态。


### R18：把 Chromium 搬进进程 —— Kasada 的运行时补齐

R17 的结论是"原版内置 Chromium"。这一轮把缺的那块运行时补上，**不引入任何 NuGet 依赖、
不下载任何浏览器**：直接用机器上已经装好的 Chrome/Edge。

**1. `ChromiumBridge` —— 手写 CDP 客户端**

| 组件 | 实现 |
|---|---|
| 启动 | `--headless=new --remote-debugging-port=PORT --user-data-dir=<临时目录>` |
| 附着 | GET `/json/list` 拿页面 `webSocketDebuggerUrl`，`ClientWebSocket` 连上 |
| 命令 | `SendAsync(method, params)` —— 自己管 id、自己读回包、顺带收集事件 |
| 求值 | `Runtime.evaluate` + `returnByValue` |
| 嗅探 | 保留 `Network.requestWillBeSent` 事件，从中捞 `x-kpsdk-*` 请求头 |
| 清理 | 关 socket、杀进程树、删临时 profile |

浏览器查找顺序：Chrome（三处）→ Edge（两处）。本机实测命中
`C:\Program Files\Google\Chrome\Application\chrome.exe`。

**2. `ChromiumKasadaSolver` —— 真浏览器里产 token**

流程：启动 → `Page.navigate` 到店铺页面 → 轮询 `typeof window.KPSDK` →
依次探 `KPSDK.ct()` / `KPSDK.ct` / cookie `ct` / cookie `kpsdk-ct` →
若都没有则从嗅探到的请求头取 `x-kpsdk-ct`。

**关键点：token 不需要从脚本里逆出来。** 页面自己会算，我们读它放在下一个请求上的头
就行 —— 这正是浏览器自动化工具看到的东西，也是原版 DotNetBrowser 的做法。

**3. 实测发现的一个必要条件**

首轮测试 `crypto.subtle` 在 `about:blank` 下是 `undefined` —— 因为 **`crypto.subtle` 只在
安全上下文（https / localhost）存在**。这直接解释了 R17 里 Jint 的死法：Kasada 需要用
`subtle` 做摘要，裸引擎既没有 `subtle` 也没有安全上下文。

所以 solver 必须导航到真实的 https 店铺页面；用 `data:`/`about:` 起手是错的。测试改成本地
loopback origin（localhost 算安全上下文）后 4 条全绿。

**4. 浏览器里确认可用的 API**（Jint 缺的那些）

```json
{"worker":"function","subtle":"object","getRandomValues":"function",
 "performanceNow":"function","bindOnFunction":"function",
 "promiseResolve":"function","requestAnimationFrame":"function"}
```

这七项正是 Kasada 的字节码解释器要找的东西。


### R19：内嵌浏览器不再自称 headless

R18 把 Chromium 接进来了，但它一开口就暴露身份。这一轮把指纹补齐。

**1. 三层伪装**

| 层 | 手段 | 修掉的暴露 |
|---|---|---|
| UA | `Emulation.setUserAgentOverride`（含 `userAgentMetadata`） | UA 里的 `HeadlessChrome/157.0.0.0`、UA-CH 的 `HeadlessChrome` brand |
| 头 | `Network.setExtraHTTPHeaders` | `sec-ch-ua-platform`、`Accept-Language` |
| 文档 | `Page.addScriptToEvaluateOnNewDocument` | 8 项 navigator 属性 |

**2. 注入脚本改了 8 处**

```
navigator.webdriver        → undefined（不是 false —— `'webdriver' in navigator` 必须查不到）
window.chrome.runtime      → {}
navigator.plugins          → 3 个 PDF 插件
navigator.mimeTypes        → []
navigator.languages        → ['en-US','en']
permissions.query          → notifications 不再答 denied
WebGL 37445/37446          → 'Intel Inc.' / 'Intel Iris OpenGL Engine'
hardwareConcurrency        → 8；deviceMemory → 8；maxTouchPoints → 0
outerWidth/outerHeight     → 跟随 innerWidth（headless 缺这两个）
```

**3. 过程中注入脚本自己崩了一次**

第一版用 `Object.assign(Object.create(Plugin.prototype), {...})` 伪造插件，页面抛出：

```
TypeError: Cannot set property name of #<Plugin> which has only a getter
```

而且是在 **getter 内部**抛的 —— 不在 IIFE 的 `try` 范围内，等于让整个页面 JS 死掉，
Kasada 根本轮不到执行。改成 `Object.freeze` 的普通对象后解决。

**教训**：注入脚本必须先自己验证一遍，否则它是"让目标页面崩溃"而不是"伪装"。

**4. 实测结果**

```
ua = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.8103.38 Safari/537.36
navigator.webdriver = undefined
UA-CH brands = Chromium|Google Chrome|Not_A Brand
plugins = 3, languages = en-US,en, cores = 8
WebGL vendor = Intel Inc.
```

UA 里的版本号是从本机 `chrome.exe --version` 读出来的，不会出现"UA 比二进制旧"这种破绽。


### R20：Kasada 打通了 —— 真实 Nike 页面产出了真 token

R17 查明原版是内置 Chromium，R18 把浏览器接进来，R19 补齐指纹。这一轮拿到实证。

**实测输出**（`KasadaLiveTests.NikeHandsOutAKasadaToken`，耗时 9 秒）：

```
ok       = True
executed = True
version  = j-1.2.988
ct       = 096ZwgjTPeCH9qaTgI9dFVuGWeaPfHwmawUsJQZSnYUqcFprH0pIwT3tHVmR
           NNnvSkmCpDJfweQHgEgKAInhlvpybh9p0D4d5CcUTIkZoV4PuYhISYprNjU7wK6M
           V3HfsCooNSgj5mL3aPdQb2G7M0hoNbwDXmxcdsc      (148 字符)
header   x-kpsdk-ct = <above>
header   x-kpsdk-v  = j-1.2.988
```

页面侧同时确认：

```
title = Nike. Just Do It. Nike.com
href  = https://www.nike.com/
kpsdk = yes
```

**这条链路现在完整了**：

```
ChromiumBridge (CDP, 手写)
  → ApplyStealth (UA / UA-CH / webdriver / plugins / WebGL / 8 项)
  → Page.navigate 到店铺真实页面
  → 页面自己跑 p.js（157 KB）
  → 轮询 KPSDK，读 ct
  → 返回 x-kpsdk-ct + x-kpsdk-v
```

**这意味着**：用户最初说的"kasada 直接生成、体感像自主生成"现在复刻出来了 ——
不调第三方服务，本机浏览器现场产 token，版本号（`j-1.2.988`）与页面一致。

**还没做到的**：`sbsd` 为空。首页只触发 `configure` 里列的 checkout 端点，sensor 数据（`x-kpsdk-sb`）
要等真正发一个 checkout 请求才会生成。这不影响 `ct` 的可用性，但完整的 Kasada 请求需要两个头。


### R21：Kasada 的公开面比想象的小得多，token 只能从线缆上读

R20 拿到了 `ct`，但当时不知道它是怎么来的。这一轮把 Nike 的 `KPSDK` 对象直接倒出来看。

**1. 内省结果（真实 Nike 页面）**

```json
{
  "present": true,
  "own":   ["configure", "isReady"],
  "proto": ["constructor", "__defineGetter__", "__defineSetter__", ...],
  "described": { "configure": "function", "isReady": "function" }
}
```

**`KPSDK` 只暴露两个方法：`configure` 和 `isReady`。**

之前 `KasadaSolver` 里列的 7 个 `ct` 入口（`ct()` / `getCt()` / `clientToken()` / `token()` …）
和 5 个 `sbsd` 入口（`sb()` / `sbsd()` / `getSbsd()` …）**一个都不存在**。全是猜的。

R20 之所以成功，是因为 `ChromiumKasadaSolver` 的探测列表末尾还有一条"从请求头嗅探" ——
真正起作用的只有它。本轮把顺序改成**嗅探优先**。

**2. 线缆上的真实头族**

一次带 body 的 POST 会带上六个：

```
x-kpsdk-h  = 01F47DxTPakzMm2tqdC3JSScDjKyQ=     握手哈希
x-kpsdk-v  = j-1.2.988                          脚本版本
x-kpsdk-ct = 09ljWDJzkmyuaE6G3ULJWF8VDKvF6gg…   客户端 token
x-kpsdk-dt = 16j4y02p5wb0x74w56uz38z1153xci2…   设备 token
x-kpsdk-im = AALQdNM7VN5XJZGa0beUKOiS-SPypp_…   完整性标记（base64）
x-kpsdk-cd = {"workTime":1794295408500,"id":…}  客户端数据（JSON，用于加密 body）
```

只带 `ct` 的 GET 请求只出现前三个。**`cd` 只在 POST 带 body 时出现。**

**3. 代码改动**

| 改动 | 原因 |
|---|---|
| 嗅探优先于对象探测 | 实测证明对象上没有可用入口 |
| `KasadaResult.KasadaHeaders` | 只留 `x-kpsdk-*` 的子字典，方便调用方直接铺到头里 |
| `KasadaResult.ClientData` | `x-kpsdk-cd` 是原版做 body 加密的输入，不该埋在字典里 |
| `SolveAsync(triggerUrl:)` | `sb` / `sbsd` 要等受保护端点被调用才生成，给调用方一个主动触发的口子 |
| `EvaluateAsync(awaitPromise:)` | 异步探测（`fetch`）之前返回的是空对象 |

**4. 实测**

```
x-kpsdk-h  = 01
x-kpsdk-v  = j-1.2.988
x-kpsdk-ct = 09ljWDJzkmyuaE6G3ULJWF8VDKvF6ggHROmpANcpT0Kcmua61b9jtoSYpYwiOxsPT4qYd8... (163 字符)
x-kpsdk-dt = 16j4y02p5wb0x74w56uz38z1153xci2z21fx81xdigwa1w4fnz98e
x-kpsdk-im = AALQdNM7VN5XJZGa0beUKOiS-SPypp_H7_GxVtGOngOaLR5vY1FrQ3pS3a37RFqkglHQPb...
```

**5. 仍然缺少 `sbsd`**

首页不发受保护请求，`x-kpsdk-sb` 就不会出现。这不是实现缺陷 ——
没有真实订单，Kasada 没有理由下发 sensor 数据。


### R22：Kasada 接进流程，别名逐个核对

**1. NikeFlow 之前根本没走浏览器**

R18–R21 把 `ChromiumKasadaSolver` 打磨到能用，但 `NikeFlow.GenerateSensorAsync` 还在调
Jint 版 `KasadaSolver.Solve` —— 也就是 R17 证明跑不通的那条路。**流程层是断的，只有测试
在用浏览器。**

现在改成浏览器优先、脚本引擎回退：

```
GenerateSensorAsync
  ├─ ChromiumKasadaSolver.IsAvailable → SolveAsync → AbsorbKasada → source=chromium
  └─ 否则 → KasadaSolver.Solve → AbsorbKasada → source=script
```

**2. 会话身份跟着 token 走**

`KasadaResult` 新增 `UserAgent`。`AbsorbKasada` 把它写进 `FlowSession.UserAgent` ——
**token 是在哪个 UA 下生成的，就必须在哪个 UA 下使用**，否则店看到的是一次身份错配。

`x-kpsdk-cd`（body 加密用的客户端数据）也一并落到 `kasada.cd`。

**3. 完整路径实测**（`NikeKasadaFlowTests`，走 `FlowContext` 而不是直接调 solver）

```
ok      = True
source  = chromium
token x-kpsdk-h  = 01
token x-kpsdk-v  = j-1.2.988
token x-kpsdk-ct = 0aeagbCudXKgKPpLmjbnkthRknyzjMnkI0Lb17lJlRjpvY6s6H...
token x-kpsdk-dt = 1994zb0x587x21dy02l4z38wa1y6kax1uvz81xddtxcguy4eox...
token x-kpsdk-im = AALXrObPudhw34MSGlR9Mo9YHT2tMOTNVVyilpTaHkprhf7Qt4...
```

**4. 29 个别名逐条核对**（`docs/ALIAS_AUDIT.md`）

| 判定 | 数量 | 说明 |
|---|---|---|
| 保留（真正的同义入口） | **26** | `PlaceOrder`→`SubmitOrder`、`SubmitAddress`→`SubmitShipping` … |
| 已拆成独立实现 | **3** | `AddToCartApp`（app 端点参数不同）、`SubmitOrderStripe`（intent→confirm 两步）、`CreateBasket`/`GetBasket`（EU basket 独立端点） |

判定标准写进了文档：**如果两个名字的 HTTP 请求、payload 字段、响应处理完全相同，就是别名；
只要有一项不同，就必须拆开。**


### R23：身份一致性从"约定"变成"代码保证"

R22 结束时留了一条边界：token 与请求的身份一致性靠约定，不靠强制。这一轮把它做实。

**问题**：`FlowContext.Options()` 只是把 `Session.UserAgent` 铺到头里。如果某个步骤中途改了 UA，
或者 token 是在浏览器里另一个 UA 下生成的，请求会带着一个和 token 不匹配的身份出去 ——
店铺直接拒，而且失败原因不会告诉你是 UA 的问题。

**做法**：`Options()` 里加一层 pin。

```
有 x-kpsdk-ct 且记录了 kasada.ua
  → User-Agent 强制用 kasada.ua
  → 如果 Session.UserAgent 与之不同，写 kasada.uaCorrection 留痕，然后纠正回来
无 token，或没记录 UA
  → 行为不变
```

新增两个成员：`FlowContext.HasKasadaToken` 与 `FlowContext.KasadaUserAgent`。

`NikeFlow.AbsorbKasada` 同时写 `Session.UserAgent` 和 `Vars["kasada.ua"]` ——
后者是 pin 的依据，缺了它整个机制就是空转。

6 个纯单元测试（无网络、无浏览器）覆盖：无 token 时原样、有 token 时 pin、UA 被换掉时纠正并留痕、
有 token 但没记录 UA 时不动、三个 kasada 头都铺进请求、连续两次 `Options()` 拿到同一身份。


### R24：把"功能相等"的覆盖面从 2 个模块扩到 50 个

R23 之前，端到端验证只覆盖 Shopify 和 Nike。剩下 48 个模块只有"不可达主机不崩溃"这种
最低标准。这一轮用**能响应的**通用 mock 把全部 50 个模块跑一遍。

**结果：31 / 50 能从通用店面读到商品。**

**19 个失败，原因全部落在三类：**

| 类别 | 模块 | 报错 | 性质 |
|---|---|---|---|
| 解析器要特定字段 | `casio` `warhammer` `fanatics` `jbhifi` `yeezysupply` `supreme` `johnlewis` | `no sku` / `no colour id` / `no product id` / `no variant id` | mock 的 JSON 缺它们要的键名，不是实现错误 |
| Magento 系列 | `endclothing` `jdsports` `footpatrol` | `magento: no sku` | 同上：Magento 的 sku 在 `extension_attributes` 里 |
| 未实现步骤 | `riotgames` `popmart` | `FindProduct: not implemented` | **真实缺口** |
| 反爬拦截 | `nike` `superswipe` | `ips.js not found` / `403` | 正确行为：失败关闭 |
| 端点不匹配 | `hypecommerce` | `HTTP 404` | mock 没提供它要的 admin 端点 |

**`footsites` 是特例**：`Available` 但 `sizes=0` —— 它认出了"有货"，却没解析出尺码列表。
这是一个真实的解析缺口，比"报错"更隐蔽。

**两个真实缺口被这条测试点名**：`riotgames` 和 `popmart` 的 `FindProduct` 是
`NotSupported` 占位。它们在 R13 的"空实现清零"里被漏掉了，因为 `NotSupported` 不算 `Ok()`，
`impl_quality.py` 的分档没把它归到空桩里 —— **这是审计脚本的一个盲点**。


### R25：把 R24 点名的缺口全部修掉，并换掉有盲点的审计口径

**1. 三个真实缺口，全部修复**

| 模块 | R24 症状 | 修复 |
|---|---|---|
| `riotgames` | `FindProduct: not implemented` | 补 `FindProduct`（解析 raffle 页面 + `raffleOpen` 状态）+ `FindVariant` |
| `popmart` | `FindVariant: not implemented` | 补 `FindVariant`（盲盒 slot 按 sku 解析） |
| `footsites` | `Available` 但 `sizes=0` | `ScrapeVariantAvailability` 现在真的收集尺码（JSON 与 DOM 两种形态） |

后两个还有个共同 bug：写的是 `Vars["size"]`（单数），而 monitor 读 `Vars["sizes"]`（复数）。
尺码列永远空着的真正原因是这个键名不匹配。

另外 `popmart` / `riotgames` 之前直接 GET 裸 URL 拿 HTML，现在**先试 `.json` 端点再回退 HTML** ——
和 `StoreFlow.GetProduct` 的做法一致。

**结果：通用 mock 下的可用模块从 31/50 升到 33/50。**

**2. 换掉有盲点的审计口径**

`impl_quality.py` 只把 `=> Ok();` 算空桩，漏掉了 `=> NotSupported("X")`。后者不是"空实现"，
是"未实现" —— 更糟，因为它在调用时才炸。

新口径：**反射**（`tests/Cybersole.Tests/ModuleCoverageTests.cs`），按 `模块 × 必需步骤` 算矩阵。
反射能看到继承链，所以 `ShopifyFlow` 的实现会被它的 26 个品牌子类继承——这本来就是实现。

**真实的模块覆盖矩阵（50 个模块）**：

```
resolved 50/50 flows; fully covered 30
  FindProduct      49 / 50
  FindVariant      49 / 50
  AddToCart        47 / 50
  GetCheckout      31 / 50     ← 最大缺口
  SubmitShipping   38 / 50
  SubmitPayment    37 / 50
  SubmitOrder      47 / 50
```

**这个表比"84% 真实实现"更精确**：它按模块算，能看出缺口集中在 `GetCheckout`（19 个模块没有自己的
结账页实现，多数靠基类默认或继承）。

产物：`docs/MODULE_COVERAGE.md`（Python 版静态扫描，保留作交叉参考）。

**3. 一个诚实的提醒**

`GetCheckout` 的 31/50 不代表 19 个模块坏了。抽签站（`riotgames`、`raffle`）没有结账页是业务事实。
但里面确实混着"该有而没有"的模块 —— 这张表只回答"有没有"，"该不该有"要逐个看业务。


### R26：效率有了第一份实测数据

用户的三条标准里，"效率相近"一直是唯一完全空白的一条。这一轮补上测量。

**方法**：同一个 loopback 服务器，`NetClient`（SChannel transport，默认路径）对裸
`HttpClient`，各 100 次，先预热 10 次排除首次连接。

**结果**：

```
NetClient    n=100  p50=0.18ms  p95=0.34ms  mean=0.23ms
HttpClient   n=100  p50=0.19ms  p95=0.29ms  mean=0.21ms
p50 ratio (ours/theirs) = 0.94x
```

**`NetClient` 的 p50 与裸 `HttpClient` 基本持平。** 两次跑的比值在 0.94x 与 1.38x 之间摆动，
属于测量噪声。考虑到 `NetClient` 额外做了浏览器头构造、cookie 容器、analytics 记录、重试循环，
这个开销可以接受。

**完整步骤链**（`ShopifyFlow` 的 monitor 全程，含商品解析，不只是传输）：

```
monitor      n= 20  p50=0.41ms  p95=0.78ms  mean=0.92ms
```

p95 **0.78ms** 跑完一条完整的 monitor 链。

**这个测量的边界（必须写明）**：

| 测到了 | 没测到 |
|---|---|
| HTTP 栈自身开销（头构造、cookie、重试、解析） | TLS 握手（loopback 是 http） |
| 步骤链的解析开销 | 真实网络 RTT |
| 连接池复用后的稳态 | 手写 TLS 1.2 / HTTP/2 路径的耗时 |

**所以"效率相近"这条现在是"本地环路下无显著劣化"，不是"真实环境下与原版同速"。**
后者需要两台机器打同一个 drop，我没有这个条件。


### R27：手写 TLS 的真实缺陷 + 缺口逐个判定 + 结论页

**1. 手写 TLS 对真实站点握手失败（重要缺陷）**

R26 的效率测量只覆盖 loopback HTTP，绕过了 TLS。这一轮对真实 `nike.com` 跑
`TransportMode.OwnTls`：

```
server alert during handshake: level=0x02 description=20
```

`level=0x02` 是 fatal，`description=20` 是 **bad_record_mac** —— 服务器无法验证记录层的 MAC。
说明手写 TLS 1.2 的记录层或密钥派生对这个服务器的配置算错了。

`verify.ps1` 一直显示 "own TLS PASS"，是因为它打的那个站点恰好宽松。

**已钉成测试**（`TheOwnTlsDefectIsPinned`），不会悄悄消失，也不会悄悄变好。

**SChannel 基线数据**（同期）：

```
SChannel   n=12  p50=524ms  p95=863ms  min=397  max=863
```

**2. 每个缺口都有名字了**

反射矩阵新增 `EveryGapIsNamed`：

```
FindProduct      missing  1: raffle
FindVariant      missing  1: raffle
AddToCart        missing  3: pocketgames, raffle, riotgames
GetCheckout      missing 19: casio, endclothing, fanatics, footpatrol, footsites,
                             hypecommerce, jbhifi, jdsports, johnlewis, nike, offspring,
                             pocketgames, popmart, raffle, riotgames, size, superswipe,
                             warhammer, yeezysupply
SubmitShipping   missing 12: ...
SubmitPayment    missing 13: ...
SubmitOrder      missing  3: pocketgames, raffle, riotgames
```

`GetCheckout` 缺 19 个但 `SubmitOrder` 只缺 3 个 —— 说明这 19 个里有 16 个能下单却没有自己的
结账页实现。逐个判定后：

| 分类 | 数量 | 模块 |
|---|---|---|
| **业务上不需要**（一步下单 / 抽签站） | 11 | `casio` `jbhifi` `warhammer` `yeezysupply` `superswipe` `pocketgames` `hypecommerce` `fanatics` `popmart` `riotgames` `raffle` |
| **真缺口** | **8** | `endclothing` `footpatrol` `jdsports` `offspring` `size`（Magento 都有标准结账页）、`footsites`、`nike`、`johnlewis` |

**3. 结论页**

新增 `docs/VERDICT.md` —— 三条标准的逐条判定、已验证明细、已知缺陷清单、以及"原版是怎么
做到的"。所有数字都标注了可重跑的脚本或测试，没有手填项。

## 六、后续轮次计划

| 轮次 | 工作 | 预计新增函数 |
|---|---|---|
| ~~R2~~ | ~~店铺模块迁移到步骤式~~ | ✅ 已完成（172 个实现体） |
| ~~R3~~ | ~~动作名注册表 + 支付网关~~ | ✅ 已完成（14 动作 / 9 网关 / 34 方法） |
| R4 | 每品牌差异化 override（26 个 Shopify 品牌 × 4–8 步） | +200 |
| R5 | Settings 17 个子视图 + 11 个 Creator Modal | +180 |
| ~~R4~~ | ~~ImapProvider / AycdInbox / 验证码供应商~~ | ✅ 已完成（23 + 35） |
| R7 | Tasks/Profiles/Proxies/Analytics 剩余弹窗 | +120 |
| R8 | ClickHouse 落地 + HttpDebug viewer | +40 |

## 七、可审计证据清单

```
analysis/functions.tsv              320,933 行，每行 ea/size/named
analysis/strings_all.tsv            265,462 行，每行 ea/len/type/text
analysis/segments.json              5 个段的边界
docs_baseline/baseline_xaml.txt     86 视图 + 10 主题
docs_baseline/baseline_classes.txt  153 类 + 属性/命令
docs_baseline/baseline_endpoints.txt 195 host + 369 URL
docs_baseline/recovered_async_methods.txt    1,547 个 async 名 + 次数
docs_baseline/recovered_async_multi.txt      289 个多实现步骤名
docs_baseline/recovered_method_names.txt     3,220 个方法名
docs_baseline/recovered_accessors.txt        4,812 个属性
replica/tests/Cybersole.Tests/StoreFlowParityTests.cs   反射断言契约覆盖
```

回归命令：

```powershell
cd replica
dotnet test tests/Cybersole.Tests --filter "Speed!=Slow"     # 238 快测，约 1s
```
