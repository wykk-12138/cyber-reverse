# 模块级函数分布与 Cybersole.* 类型/方法普查报告（Gap #2）

> 生成时间：2026-11-20 22:02:25 +0800  |  生成脚本：`python analysis/module_function_census.py --write-doc`
> 全局动态套件/绑定指标唯一源：`docs/METRICS.md`（本文只陈述源码/PDB/二进制与 IDA 普查观测值）。

## 一、结论摘要（Observation / Inference / Unknown 严格分离）

- **Observation（复刻件 100% 归因）**：通过解析 `Cybersole.Ui.pdb`（MSF 7.0，233 模块 / 183,708 过程符号）并与 `Cybersole.Ui.exe` 的 `.pdata` 区间（187,794 有效函数区间 / 187,818 原始槽位）做精确 + 内嵌 funclet 匹配，**100.00%**（`outside=0`）`.pdata` 函数得到归属。其中 **86.48%**（162,411 个）为 `System.* / BCL`、Avalonia UI 栈与 NativeAOT CRT；**10.34%**（19,427 个）为第三方库（`Jint/Acornima`、`BouncyCastle`、`Newtonsoft.Json`、`MailKit/MimeKit`）；**仅 3.17%（5,956 个 `.pdata` 函数 / 1.52 MiB）为 `Cybersole.*` 自身业务代码**。
- **Observation（原版多信号归因与诚实未知量）**：对 `target/Cybersole.exe`（321,244 IDA 函数 / 277,094 有效 `.pdata` 区间 / 277,120 原始槽位），结合（1）可信原生 IDA 符号（过滤 `< 0x143025000` 的 9,496 个 tiny FLIRT/nullsub 误命）、（2）`chars_va - 12` 冻结 UTF-16 字符串（67,692 个对象头）与 C 字符串 `.text disp32` 扫描（204,638 命中 / 36,685 函数）、（3）937,233 条 IDA 调用图边的 1–2 跳保守纯模块传播，共归因 **62,836** 个函数（`Direct-Attributed` **10,937** + `Callgraph-Propagated` **51,899**），**`Unattributed` 258,408（80.44%）**如实保留为未知。
- **Observation（关键差距核对与死岛/补齐状态）**：
  1. **Mail/IMAP/AYCD 已接入运行链路（死岛已消除）**：`MailCodeService` + `ImapMailProvider` + `AycdInboxClient` 已接入 `AppServices.cs`、`TaskEngine.cs` 与设置校验动作，`Cybersole.Ui.pdb` 现包含 **2,394** 个 `.pdata` 函数（`MailKit` 1,263 + `MimeKit` 1,131；原版已观测 22 个归因函数）。
  2. **原版伴生运行时与三方依赖对照**：原版含独立 `Cybersole.Http.{Newtonsoft,Analytics,Debug}.dll`（复刻件已在 Phase 2 对位核心 `IBody`/`ClickHouseSink`/`HttpDebug`/`RootCertificateStore`），另有外部阻塞的三方栈 `DotNetBrowser`（653 归因函数）、`AngleSharp`（154）、`MSAL`（57）、`SignalR`（51）、`Velopack`（23）、`RabbitMQ.Client`（12）、`Metalama.Framework`（33）。
  3. **支付状态机与功能集边界**：Phase 2 已落地 `ContinueUnzerThreeDs`（`0x143383aa9`）、`CardinalInit`/`CardinalContinue`（`0x14338294f`）与 `CheckoutComGateway`（`0x1470530bc`）及 `CheckPriceLimitApp`/`FindProductCDN`/`CrowdTwist-Register`；而原版 21 个视觉推理 DTO（`0x14333c304`）、`ExecuteClipModelAsync`/`SolveImageInCloudAsync`/`ClickCellsAsync`（`0x1435f0000`）与反爬传感器封装（`GetSbsdHash`/`DdMobileTouchEvent`/`SensorPow`）归为 `Not In Function Set`。
- **Inference（结构解释）**：`Cybersole.Stores` 在原版仅靠字符串种子 + 零跨模块泄露 2 跳传播即已显影 **5,090** 个函数（4.41 MiB），是复刻件全部 `Cybersole.Stores`（3,403 个 `.pdata` 函数 / 829 KiB）的 **1.50 倍函数数 / 5.44 倍代码字节**，主因原版内含更多站内变体、3DS/支付状态机与浏览器/反爬交互代码；同时原版独有的 `DotNetBrowser` + `SignalR` + `MSAL` + `AngleSharp` + `RabbitMQ` + `MailKit` + .NET 10 BCL 体量共同构成了 `.pdata` 总数差值的主要部分。
- **Unknown**：原版 `Unattributed` 的 258,408 个函数缺少直接字符串引用、且经虚表/接口/跨模块调用隔断，无法在不猜测的情况下按单函数拆分到具体模块。

## 二、复刻件模块函数分布（`Cybersole.Ui.pdb` + `.pdata` 100% 实测）

- 产物：`D:\projects\cyber-reverse\replica\.publish-aot\Cybersole.Ui.exe`（61,192,704 B，修改时间 2026-11-20 19:02:56）
- PDB：`D:\projects\cyber-reverse\replica\.publish-aot\Cybersole.Ui.pdb`（297,078,784 B，233 模块，183,708 过程符号）
- `.pdata` 覆盖：187,794 有效函数区间（原始 187,818 槽含 42 字节对齐空槽），**0 个未归因区间**。

| 模块桶 | `.pdata` 合计 | 精确起始命中 | 内嵌 Funclet | 代码字节 | 占比 |
|---|---:|---:|---:|---:|---:|
| `System.* / BCL` | 123,617 | 115,134 | 8,483 | 15,055,273 | 65.83% |
| `Avalonia.*` | 33,473 | 30,485 | 2,988 | 5,865,115 | 17.82% |
| `Jint.*` | 8,463 | 7,908 | 555 | 2,743,321 | 4.51% |
| `Org.BouncyCastle.*` | 5,670 | 5,506 | 164 | 1,337,810 | 3.02% |
| `Cybersole.Stores` | 3,403 | 2,752 | 651 | 848,939 | 1.81% |
| `NativeAOT / CRT Runtime` | 1,895 | 1,085 | 810 | 702,435 | 1.01% |
| `Newtonsoft.Json.*` | 1,849 | 1,727 | 122 | 355,511 | 0.98% |
| `Cybersole.Ui` | 1,359 | 1,253 | 106 | 450,180 | 0.72% |
| `Microsoft.*` | 1,292 | 1,243 | 49 | 262,376 | 0.69% |
| `MailKit.*` | 1,263 | 1,049 | 214 | 389,442 | 0.67% |
| `MimeKit.*` | 1,131 | 1,003 | 128 | 830,981 | 0.60% |
| `Acornima.* (Jint)` | 1,051 | 1,032 | 19 | 274,113 | 0.56% |
| `Tmds.DBus (Avalonia)` | 922 | 800 | 122 | 175,058 | 0.49% |
| `SkiaSharp.*` | 860 | 829 | 31 | 86,827 | 0.46% |
| `Cybersole.Services` | 521 | 403 | 118 | 117,803 | 0.28% |
| `Cybersole.Http` | 479 | 368 | 111 | 135,142 | 0.26% |
| `HarfBuzzSharp.*` | 307 | 294 | 13 | 35,777 | 0.16% |
| `Cybersole.Core` | 194 | 179 | 15 | 45,402 | 0.10% |
| `MicroCom.Runtime (Avalonia)` | 45 | 38 | 7 | 6,028 | 0.02% |

### 复刻件源码与基线清单核对（`replica/src/` vs `replica/docs/baseline/`）

| 工程 | `.cs` 文件数 | 总行数 | 声明类型数 |
|---|---:|---:|---:|
| `Cybersole.Core` | 62 | 5,453 | 149 |
| `Cybersole.Http` | 26 | 5,655 | 66 |
| `Cybersole.Services` | 22 | 4,409 | 61 |
| `Cybersole.Stores` | 158 | 40,379 | 305 |
| `Cybersole.Ui` | 65 | 21,090 | 133 |

- **`recovered_accessors_by_type.txt`**：共 508 个类型键，其中 `Cybersole.*` **143** 个（精确命名空间匹配 85 + 同简名跨命名空间 44 + `type_classification.json` 分类 14 + 缺失 **0**）；其余 365 条包含带 NativeAOT 长度前缀噪声的 `xCybersole*`/`tAvalonia*` 及 `DotNetBrowser`/`Avalonia`/`System`。
- **`recovered_async_methods.txt`**：共 1,547 个去重 `<Method>d__N` 名（镜像共 2,587 次实现体）；按无注释源码词元对照，`replica/src/` 存在 **412** 个名字（对应 **1,324** 次原版实现，占高频业务词汇主体），缺席 **1,135** 个名字（1,263 次出现，主要为 BCL/第三方库内部及原版专有单次实现步骤）。

## 三、原版函数多信号归因分布（`target/Cybersole.exe`）

### 3.1 归因口径与 PDB 校准实验

1. **Signal 1（可信 IDA 符号）**：仅采信 `>= 0x143025000`（`main` 及 CRT/Win32 启动段）与 23 个 `Brotli*` 导出函数；显式剔除 `< 0x143025000` 托管代码区内的 **9,496** 个 `nullsub_*` 与 5–28 B IDA FLIRT 误匹配（实证样本：`0x14032aeb0` 被 IDA 标为 `__acrt_update_thread_multibyte_data_90`，实测加载 Avalonia 冻结串 `SystemControlDisabledBaseMediumLowBrush`）。
2. **Signal 2（字符串 Xref 归属）**：对 `idautils.Strings()` 中 67,692 个冻结 UTF-16 对象算头 `chars_va - 12`，连同 C/UTF-8 串在 `.text` 全字节滑动 `disp32` 扫描得 **204,638** 处指令引用（命中 **36,685** 个函数），按无歧义库/命名空间/URL/文案种子归因（`127` 个非 BCL 多模块冲突函数故意保留为未归因，不强行归类）。
3. **Signal 3（1–2 跳保守纯模块传播）**：在 IDA 937,233 条调用边上执行 2 轮传播：`System.* / BCL` 与 `NativeAOT / CRT` 在已归因邻居中唯一一致时传播；非 BCL 应用/三方模块仅当**全部邻居（caller ∪ callee）均已归因且同属该模块**时才传播。
   - **在有 PDB 真值的复刻件上校准（332,091 条 `E8` 边，模拟不均衡种子 8,015 个）**：传播 33,600 个函数，**总体准确率 93.5%**，`Cybersole.Stores` 精确率 **77.4%**（31 个），`Avalonia.*` 精确率 **96.6%**（175 个）。（对比实验表明：若对 `Cybersole.Stores` 放开向未归因 callee 传播，`Stores` 精确率会跌至 42.1%，因大量 BCL 泛型特化仅被上层业务调用。）

| 汇总档位 | IDA 函数数 | 占比 | 对应 `.pdata` 起始 | 代码字节 |
|---|---:|---:|---:|---:|
| **Direct-Attributed**（IDA 原生名 544 + 串 xref 10,393） | 10,937 | 3.40% | — | — |
| **Callgraph-Propagated**（Hop1 16,464 + Hop2 35,435） | 51,899 | 16.16% | — | — |
| **已归因小计** | **62,836** | **19.56%** | **55,276** | — |
| **Unattributed**（其中直接冲突跳过 127） | **258,408** | **80.44%** | **220,307** | 27,999,113 |
| **原版总计（IDA / `.pdata`）** | **321,244** | **100.00%** | **275,583（`.pdata` 有效 277,094 / 槽 277,120）** | — |

### 3.2 原版按模块桶明细

| 模块桶 | 总归因 | Direct | Propagated | `.pdata` 命中 | 字节数 | 中位地址 |
|---|---:|---:|---:|---:|---:|---|
| `System.* / BCL` | 49,435 | 3,012 | 46,423 | 42,686 | 12,163,658 | `0x1421036d0` |
| `Cybersole.Stores (Flows/Payments/AntiBot)` | 5,090 | 3,477 | 1,613 | 5,089 | 4,619,163 | `0x140dd66d0` |
| `NativeAOT / CRT Runtime` | 4,010 | 509 | 3,501 | 3,252 | 1,162,166 | `0x1428868ce` |
| `Avalonia.*` | 2,259 | 2,101 | 158 | 2,259 | 1,005,166 | `0x14033ada0` |
| `DotNetBrowser.*` | 653 | 633 | 20 | 652 | 259,590 | `0x1414ab9e0` |
| `Jint / Acornima` | 484 | 427 | 57 | 484 | 624,498 | `0x141753720` |
| `Cybersole.Ui` | 333 | 308 | 25 | 333 | 1,319,823 | `0x1406fbbd0` |
| `AngleSharp.*` | 154 | 154 | 0 | 154 | 49,207 | `0x1400ed9a0` |
| `Microsoft.Extensions.*` | 70 | 45 | 25 | 56 | 9,106 | `0x1425fc0e0` |
| `Microsoft.Identity.Client` | 57 | 36 | 21 | 50 | 16,911 | `0x1419a5220` |
| `Microsoft.AspNetCore.SignalR` | 51 | 34 | 17 | 51 | 26,274 | `0x14190158b` |
| `Cybersole.Http (Brotli native)` | 43 | 35 | 8 | 17 | 13,358 | `0x1430f2970` |
| `Metalama.*` | 33 | 30 | 3 | 33 | 2,204 | `0x141274500` |
| `Newtonsoft.Json.*` | 23 | 20 | 3 | 23 | 7,786 | `0x141adaf20` |
| `Velopack.*` | 23 | 17 | 6 | 21 | 22,510 | `0x1420120c0` |
| `MailKit / MimeKit` | 22 | 21 | 1 | 22 | 6,542 | `0x14189d4e0` |
| `Cybersole.Core` | 16 | 11 | 5 | 15 | 8,944 | `0x1426128a0` |
| `Org.BouncyCastle.*` | 16 | 15 | 1 | 16 | 4,978 | `0x140530690` |
| `SkiaSharp / HarfBuzzSharp` | 13 | 13 | 0 | 13 | 5,232 | `0x141b1c2b0` |
| `RabbitMQ.Client` | 12 | 12 | 0 | 12 | 2,986 | `0x141b08b20` |
| `Cybersole.Auth/Lic (R702 not-in-function-set)` | 10 | 8 | 2 | 10 | 2,322 | `0x140773371` |
| `Google.Protobuf.*` | 8 | 4 | 4 | 8 | 240 | `0x1415d8ca0` |
| `Cybersole.Http` | 8 | 6 | 2 | 7 | 6,197 | `0x141313990` |
| `Cybersole.Services` | 7 | 5 | 2 | 7 | 4,323 | `0x14101a970` |
| `OpenTelemetry / Analytics` | 6 | 4 | 2 | 6 | 986 | `0x141981e82` |
| `Unattributed` | 258,408 | 0 | 0 | 220,307 | 27,999,113 | — |

## 四、原版 `Cybersole.*` 子系统、DTO 与三方库逐项对照矩阵

原版 `.rdata` 元数据共观测 **75** 个程序集 `*.dll`、**714** 个 `Cybersole.*` 词元、**266** 个 `PropInit` JSON/序列化 DTO、**1549** 个 `<Method>d__N` 状态机名及 **98** 个 `avares://Cybersole/` 资产。

| 子系统 / 命名空间 / 家族 | 原版实证证据（地址 / 数量） | 复刻件对应 | 分类 | 缺口与判定依据 |
|---|---|---|---|---|
| **Cybersole.Stores.Flows (18 Flows / 369 Steps)** | 3,477 direct / 5,090 attributed funcs (`0x1408..0x1412`); 103 storefront async names (408 occ) | `Cybersole.Stores/` (40,379 LOC; 3,403 `.pdata` funcs, 829 KiB) | `Implemented (Core Verified Steps)` | 70/103 storefront async names present (375/408 occ); `CheckPriceLimitAppAsync` (`0x140d1c1a0`), `FindProductCdnAsync` (`0x140c986f0`), `CheckFanRewardState`/`SignUpFanRewards` (`0x140a0fc40`/`0x140a19360`), and Komoju/WebCVS convenience steps landed in `ShopifyFlow`/`FunkoFlow` (remaining: `Unknown` `ToppsVariant` serialized JSON keys & external-blocked Farfetch/per-store live capture). |
| **Cybersole.Stores.Payments (PayPal 3DS / Stripe / Adyen / Unzer / Checkout.com)** | 124 payment async names (195 occ); `0x143320000`, `0x14338294f` (`CardinalInit`), `0x143383aa9` (`ContinueUnzerThreeDs`), `0x1470530bc` (`api.checkout.com`) | `Cybersole.Stores/Payments/{PayPalThreeDs,StripeChallenge,CardinalThreeDs,CheckoutComGateway,Gateways}.cs` | `Implemented` | PayPal 3DS (9 stages), Stripe 6 endpoints + 8-builder static dispatch, `UnzerGateway` (`ContinueUnzerThreeDs`), `CardinalThreeDs` (Centinel/CardinalTrusted/DF/StepUp), and `CheckoutComGateway` (`api.checkout.com` 4 paths) landed (47/124 names, 118/195 occ); honest `Unknown` boundaries kept for Unzer prepare subpath/terminal set & ACS host field tables. |
| **Cybersole.Stores.Scripts (Kasada / Cloudflare / DataDome / PX / Akamai / Queue-it)** | Jint + Acornima (484 attributed funcs); `GenerateSensor`, `GetSbsdHash`, `DdMobileEvent`/`SensorRequest` (`0x14333fc96`), `SolverApiException` | `Cybersole.Stores/Scripts/*.cs` (`KasadaSolver`, `CloudflareStrategy`, `BrowserShim`, etc.) | `Partial / Compatibility Surfaces Only` | Passive vendor detection, Jint runtime shims, and compatibility surfaces implemented; sensor-forgery / anti-bot execution wrappers (`GetSbsdHash`/`GetSbsdScript`, `DdMobileTouchEvent`/`SensorPow`) and browser-hosted challenge wrappers are not part of the replica's function set. |
| **Cybersole.Stores AI / Vision & Automated Captcha Solving** | 21 Vision DTOs (`HintLabelsRequest`..`GANResult` @ `0x14333c304`), `ExecuteClipModelAsync`/`SolveImageInCloudAsync`/`ClickCellsAsync` @ `0x1435f0000`, `CallParallax` @ `0x14345c117` | `Cybersole.Services/Captcha/{CaptchaSolverService,Drivers}.cs`, `CaptchaSurface.cs` | `Not In Function Set` | User third-party API drivers (2Captcha/Parallax/Uncaptcha/HumanPresence) and detection (`CaptchaSurface`) implemented; automated CAPTCHA/anti-bot execution wrappers (`ExecuteClipModelAsync`, `ClickCellsAsync`, `MoveMouseAndClickWithoutTrajectoryAsync`) are not part of the replica's function set. |
| **Cybersole.Http (NetClient 0.10.0) + Brotli + Companion Packages** | `Cybersole.Http.dll`, `Cybersole.Http.{Newtonsoft,Analytics,Debug}.dll` (`0x14315a7c1..0x14316e350`), 51 attributed funcs (incl. Brotli) | `Cybersole.Http/` (479 `.pdata` funcs, 131 KiB; `BrotliDictionary.bin`) | `Implemented` | `SocketsHttpHandler` + `TlsProfile.Chrome150` + Brotli dict + `IBody`/`LegacyJsonBody`/`LegacyJarrayBody` + `ClickHouseSink` (`BoundedChannel`, `FlushOnceAsync`/`DrainLocalQueueAsync`) + `HttpDebug` (`CSHD\x01`) + `RootCertificateStore` landed. |
| **Cybersole.Services.Mail (ImapProvider / AYCD / MailKit + MimeKit)** | `MailKit.dll` + `MimeKit.dll` (22 attributed funcs @ `0x14188..0x1419e`), `WaitImapAsync` (`0x14336b99e`), `AycdCompletedTasks`/`AycdMailElement` (`0x14334cb55`) | `Cybersole.Services/Mail/{ImapMailProvider,AycdInboxClient}.cs` — **2,394 funcs in `Cybersole.Ui.pdb`** (`MailKit` 1,263 + `MimeKit` 1,131) | `Implemented` | `MailCodeService` (`Task.WhenAny`), `ImapMailProvider`, and `AycdInboxClient` wired into `AppServices.Mail` -> `TaskEngine` -> `CheckoutContext.WaitForMailCodeAsync` and Settings verification handlers (2,394 live `MailKit`/`MimeKit` funcs retained in NativeAOT PDB; MSAL Outlook OAuth refresh stays External Blocked). |
| **Cybersole.Services Cloud Sync / SignalR / RabbitMQ / MSAL / Velopack** | `SignalR` (51), `MSAL` (57), `Velopack` (23), `RabbitMQ` (12), 35 `*Dto` (`0x1433473dc`) + 21 `Remote*` (`0x1433611c7`) | `BackupScheduler.cs`, `ClockService.cs`, `SettingsShell.cs` (local Velopack cache check only) | `External Blocked` | Missing `SignalR` (`/connect/app`), `RabbitMQ.Client`, `Microsoft.Identity.Client` (MSAL OAuth2), cloud `*Dto`/`Remote*` sync, and real `Velopack` update feed (`cdn.cybersole.io/releases/` returns 404; `/connect/app` requires valid login). |
| **Cybersole.Core / Models / SmartActions / Providers (Metalama Observability)** | `Cybersole.Core.dll` + `Metalama.Framework` (33 funcs @ `0x141274`), `Cybersole.Providers.IDataProvider` (`0x143216abb`), `Cybersole.Global.Strings` (`0x143210e9f`) | `Cybersole.Core/` (5,453 LOC; 194 `.pdata` funcs; handwritten `ObservableObject` + `RelayCommand`) | `Implemented` | All 143 `Cybersole.*` accessor types accounted for (`85` FQN, `44` namespace-moved, `14` in `type_classification.json`, `0` missing); `IDataProvider` is an unimplemented interface contract; `CommunityToolkit.Mvvm` in `.csproj` is unused/trimmed. |
| **Cybersole.Ui (Avalonia Views / Controls / Localization)** | 333 attributed funcs (`0x14057..0x14088`), 98 `avares://Cybersole/` assets, `Avalonia` (2,259), `AvaloniaEdit` | `Cybersole.Ui/` (21,090 LOC; 1,359 `.pdata` funcs, `Avalonia 11.3.2`) | `Implemented` | Core UI views, controls, and localization helpers implemented (excluding `AvaloniaEdit` code editor and `TaskCreatorAdvancedView` merged into `TaskCreatorView`). |
| **Cybersole.Ui.Views.Auth & LicenseControl (R702)** | `AuthWindow`, `LicenseControl`, `Cybersole.Models.License`, 10 attributed funcs (`0x14076..0x14077`) | `Auth/` (`AuthService`, `LicenseService` read-only) | `Not In Function Set` | R702 classified it as user management, outside the replica's function set (`docs/DECISION_LICENSE_OUT_OF_SCOPE.md`). |
| **Cybersole.Web.BrowserHandlers & DotNetBrowser (Chromium 4.3.5.8591)** | 653 attributed funcs (`0x1413d..0x14153`), `IBrowserSessionView` (`0x143636deb`), `PaymentAutofill` (`0x14352da80`), 17 `Solver*` IPC DTOs (`0x143459376`), `AngleSharp` (154) | `CustomBrowser.cs` (Avalonia placeholder window without embedded Chromium engine) | `External Blocked` | Commercial `DotNetBrowser` + external Chromium runtime (`DOTNETBROWSER_CHROMIUM_DIR`) and `Cybersole.Web.BrowserHandlers` / `AngleSharp` HTML parser are absent in replica. |

## 五、Phase 2 核心收口状态与严格边界（遵循 R757 ①→②→③→④）

1. **① 站点流程与支付闭环（`Cybersole.Stores`，Waves 2B + 2C 已落地）**：已反编译落地 `ContinueUnzerThreeDs`（`0x143383aa9`）、`CardinalThreeDs`（`0x14338294f`）、`CheckoutComGateway`（`0x1470530bc`）、Shopify 便利店与 `CheckPriceLimitApp`/`FindProductCDN`（`0x140d1c1a0` / `0x140c986f0`）、Funko `CrowdTwist-Register`（`0x140a19360`）；仅余静态未解 `Unknown`（Unzer prepare 子路径/终态集、ACS 逐行表、Komoju 后缀、`ToppsVariant` 字段名）与需 live capture/凭据的外部阻塞分支。
2. **② 邮箱/OTP 服务接线（`Cybersole.Services.Mail`，Wave 2A 已落地）**：`MailCodeService` + `ImapMailProvider` + `AycdInboxClient` 已接入 `AppServices.cs` / `TaskEngine.cs` / `CheckoutContext.WaitForMailCodeAsync` 与设置页测试按钮，已确认 `MailKit`/`MimeKit` 进入 AOT PDB 产物（MSAL Outlook OAuth 保持 External Blocked）。
3. **③ 传输层与可观测性伴生包（`Cybersole.Http`，Wave 2D 已落地）**：`IBody`/`LegacyJsonBody`/`LegacyJarrayBody`、`ClickHouseSink`（`BoundedChannel` + `FlushOnceAsync`/`DrainLocalQueueAsync`）、`HttpDebug`（`CSHD\x01`）与 `RootCertificateStore` 均已落地并接入 `NetClient`/`HttpAnalytics`/`BouncyTls`。
4. **④ 外部阻塞与功能集边界**：`DotNetBrowser`（653 函数）与 `Cybersole.Web.BrowserHandlers`、`SignalR`/`/connect/app` 远端同步、`MSAL`/`Velopack`/`RabbitMQ` 保持 `External Blocked`；`AuthWindow`/`LicenseControl`（R702）与反爬/验证码执行封装（`ExecuteClipModelAsync`/`ClickCellsAsync`/`GetSbsdHash`/`DdMobileTouchEvent`/`SensorPow`）归为 `Not In Function Set`。
