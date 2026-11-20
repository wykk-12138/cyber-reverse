# 模块级函数分布与 Cybersole.* 类型/方法普查报告（Gap #2）

> 生成时间：2026-11-20 16:32:08 +0800  |  生成脚本：`python analysis/module_function_census.py --write-doc`
> 全局动态套件/绑定指标唯一源：`docs/METRICS.md`（本文只陈述源码/PDB/二进制与 IDA 普查观测值）。

## 一、结论摘要（Observation / Inference / Unknown 严格分离）

- **Observation（复刻件 100% 归因）**：通过解析 `Cybersole.Ui.pdb`（MSF 7.0，233 模块 / 175,955 过程符号）并与 `Cybersole.Ui.exe` 的 `.pdata` 区间（179,798 有效函数区间 / 179,840 原始槽位）做精确 + 内嵌 funclet 匹配，**100.00%**（`outside=0`）`.pdata` 函数得到归属。其中 **87.49%**（157,311 个）为 `System.* / BCL`、Avalonia UI 栈与 NativeAOT CRT；**9.47%**（17,032 个）为第三方库（`Jint/Acornima`、`BouncyCastle`、`Newtonsoft.Json`）；**仅 3.03%（5,455 个 `.pdata` 函数 / 1.36 MiB）为 `Cybersole.*` 自身业务代码**。
- **Observation（原版多信号归因与诚实未知量）**：对 `target/Cybersole.exe`（321,244 IDA 函数 / 277,094 有效 `.pdata` 区间 / 277,120 原始槽位），结合（1）可信原生 IDA 符号（过滤 `< 0x143025000` 的 9,496 个 tiny FLIRT/nullsub 误命）、（2）`chars_va - 12` 冻结 UTF-16 字符串（67,692 个对象头）与 C 字符串 `.text disp32` 扫描（204,638 命中 / 36,685 函数）、（3）937,233 条 IDA 调用图边的 1–2 跳保守纯模块传播，共归因 **62,836** 个函数（`Direct-Attributed` **10,937** + `Callgraph-Propagated` **51,899**），**`Unattributed` 258,408（80.44%）**如实保留为未知。
- **Observation（此前漏计的关键差距与死岛发现）**：
  1. **Mail/IMAP/AYCD 在复刻件产物中实际为 0**：`ImapMailProvider.cs` 与 `AycdInboxClient.cs` 虽在 `Cybersole.Services` 源码与单元测试中存在，但零被调于 `AppServices.cs`/`TaskEngine.cs`，NativeAOT 将 `MailKit`/`MimeKit` 100% 裁剪（`Cybersole.Ui.pdb` 中 0 个函数；原版已观测 22 个归因函数）。
  2. **原版多出 4 个独立 `Cybersole.*` 伴生包与多类三方运行时**：`Cybersole.Http.{Newtonsoft,Analytics,Debug}.dll`、`DotNetBrowser`（653 归因函数）、`AngleSharp`（154）、`MSAL`（57）、`SignalR`（51）、`Velopack`（23）、`RabbitMQ.Client`（12）、`Metalama.Framework`（33）。
  3. **AI/视觉验证码与 Unzer/Cardinal/Checkout.com**：原版含 21 个视觉推理 `PropInit` DTO（`0x14333c304`）、`ExecuteClipModelAsync`/`SolveImageInCloudAsync`（`0x1435f0000`，属验证码求解执行面 → `Out of Scope`），以及尚未闭环的 `ContinueUnzerThreeDs`（`0x143383aa9`）、`CardinalInit`（`0x14338294f`）、`api.checkout.com`、`ClickHouseSink`。
- **Inference（结构解释）**：`Cybersole.Stores` 在原版仅靠字符串种子 + 零跨模块泄露 2 跳传播即已显影 **5,090** 个函数（4.41 MiB），是复刻件全部 `Cybersole.Stores`（3,184 个 `.pdata` 函数 / 726 KiB）的 **1.60 倍函数数 / 6.22 倍代码字节**，主因原版内含更多站内变体、3DS/支付状态机与浏览器/反爬交互代码；同时原版独有的 `DotNetBrowser` + `SignalR` + `MSAL` + `AngleSharp` + `RabbitMQ` + `MailKit` + .NET 10 BCL 体量共同构成了 `.pdata` 总数差值的主要部分。
- **Unknown**：原版 `Unattributed` 的 258,408 个函数缺少直接字符串引用、且经虚表/接口/跨模块调用隔断，无法在不猜测的情况下按单函数拆分到具体模块。

## 二、复刻件模块函数分布（`Cybersole.Ui.pdb` + `.pdata` 100% 实测）

- 产物：`D:\projects\cyber-reverse\replica\.publish-aot\Cybersole.Ui.exe`（57,491,456 B，修改时间 2026-11-20 14:15:16）
- PDB：`D:\projects\cyber-reverse\replica\.publish-aot\Cybersole.Ui.pdb`（286,101,504 B，233 模块，175,955 过程符号）
- `.pdata` 覆盖：179,798 有效函数区间（原始 179,840 槽含 42 字节对齐空槽），**0 个未归因区间**。

| 模块桶 | `.pdata` 合计 | 精确起始命中 | 内嵌 Funclet | 代码字节 | 占比 |
|---|---:|---:|---:|---:|---:|
| `System.* / BCL` | 118,518 | 110,435 | 8,083 | 14,493,905 | 65.92% |
| `Avalonia.*` | 33,472 | 30,484 | 2,988 | 5,865,055 | 18.62% |
| `Jint.*` | 8,463 | 7,908 | 555 | 2,743,321 | 4.71% |
| `Org.BouncyCastle.*` | 5,670 | 5,506 | 164 | 1,337,783 | 3.15% |
| `Cybersole.Stores` | 3,184 | 2,590 | 594 | 743,018 | 1.77% |
| `NativeAOT / CRT Runtime` | 1,895 | 1,085 | 810 | 702,435 | 1.05% |
| `Newtonsoft.Json.*` | 1,848 | 1,726 | 122 | 355,449 | 1.03% |
| `Cybersole.Ui` | 1,339 | 1,237 | 102 | 445,427 | 0.74% |
| `Microsoft.*` | 1,292 | 1,243 | 49 | 262,376 | 0.72% |
| `Acornima.* (Jint)` | 1,051 | 1,032 | 19 | 274,113 | 0.58% |
| `Tmds.DBus (Avalonia)` | 922 | 800 | 122 | 175,069 | 0.51% |
| `SkiaSharp.*` | 860 | 829 | 31 | 86,824 | 0.48% |
| `Cybersole.Http` | 384 | 292 | 92 | 114,343 | 0.21% |
| `Cybersole.Services` | 354 | 281 | 73 | 81,202 | 0.20% |
| `HarfBuzzSharp.*` | 307 | 294 | 13 | 35,777 | 0.17% |
| `Cybersole.Core` | 194 | 179 | 15 | 45,402 | 0.11% |
| `MicroCom.Runtime (Avalonia)` | 45 | 38 | 7 | 6,028 | 0.03% |

### 复刻件源码与基线清单核对（`replica/src/` vs `replica/docs/baseline/`）

| 工程 | `.cs` 文件数 | 总行数 | 声明类型数 |
|---|---:|---:|---:|
| `Cybersole.Core` | 62 | 5,435 | 149 |
| `Cybersole.Http` | 22 | 4,476 | 51 |
| `Cybersole.Services` | 22 | 3,667 | 54 |
| `Cybersole.Stores` | 155 | 37,461 | 301 |
| `Cybersole.Ui` | 64 | 20,913 | 132 |

- **`recovered_accessors_by_type.txt`**：共 508 个类型键，其中 `Cybersole.*` **143** 个（精确命名空间匹配 85 + 同简名跨命名空间 44 + `type_classification.json` 分类 14 + 缺失 **0**）；其余 365 条包含带 NativeAOT 长度前缀噪声的 `xCybersole*`/`tAvalonia*` 及 `DotNetBrowser`/`Avalonia`/`System`。
- **`recovered_async_methods.txt`**：共 1,547 个去重 `<Method>d__N` 名（镜像共 2,587 次实现体）；按无注释源码词元对照，`replica/src/` 存在 **400** 个名字（对应 **1,312** 次原版实现，占高频业务词汇主体），缺席 **1,147** 个名字（1,275 次出现，主要为 BCL/第三方库内部及原版专有单次实现步骤）。

## 三、原版函数多信号归因分布（`target/Cybersole.exe`）

### 3.1 归因口径与 PDB 校准实验

1. **Signal 1（可信 IDA 符号）**：仅采信 `>= 0x143025000`（`main` 及 CRT/Win32 启动段）与 23 个 `Brotli*` 导出函数；显式剔除 `< 0x143025000` 托管代码区内的 **9,496** 个 `nullsub_*` 与 5–28 B IDA FLIRT 误匹配（实证样本：`0x14032aeb0` 被 IDA 标为 `__acrt_update_thread_multibyte_data_90`，实测加载 Avalonia 冻结串 `SystemControlDisabledBaseMediumLowBrush`）。
2. **Signal 2（字符串 Xref 归属）**：对 `idautils.Strings()` 中 67,692 个冻结 UTF-16 对象算头 `chars_va - 12`，连同 C/UTF-8 串在 `.text` 全字节滑动 `disp32` 扫描得 **204,638** 处指令引用（命中 **36,685** 个函数），按无歧义库/命名空间/URL/文案种子归因（`127` 个非 BCL 多模块冲突函数故意保留为未归因，不强行归类）。
3. **Signal 3（1–2 跳保守纯模块传播）**：在 IDA 937,233 条调用边上执行 2 轮传播：`System.* / BCL` 与 `NativeAOT / CRT` 在已归因邻居中唯一一致时传播；非 BCL 应用/三方模块仅当**全部邻居（caller ∪ callee）均已归因且同属该模块**时才传播。
   - **在有 PDB 真值的复刻件上校准（316,928 条 `E8` 边，模拟不均衡种子 7,753 个）**：传播 28,651 个函数，**总体准确率 93.3%**，`Cybersole.Stores` 精确率 **90.5%**（21 个），`Avalonia.*` 精确率 **97.1%**（210 个）。（对比实验表明：若对 `Cybersole.Stores` 放开向未归因 callee 传播，`Stores` 精确率会跌至 42.1%，因大量 BCL 泛型特化仅被上层业务调用。）

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
| `Velopack.*` | 23 | 17 | 6 | 21 | 22,510 | `0x1420120c0` |
| `Newtonsoft.Json.*` | 23 | 20 | 3 | 23 | 7,786 | `0x141adaf20` |
| `MailKit / MimeKit` | 22 | 21 | 1 | 22 | 6,542 | `0x14189d4e0` |
| `Cybersole.Core` | 16 | 11 | 5 | 15 | 8,944 | `0x1426128a0` |
| `Org.BouncyCastle.*` | 16 | 15 | 1 | 16 | 4,978 | `0x140530690` |
| `SkiaSharp / HarfBuzzSharp` | 13 | 13 | 0 | 13 | 5,232 | `0x141b1c2b0` |
| `RabbitMQ.Client` | 12 | 12 | 0 | 12 | 2,986 | `0x141b08b20` |
| `Cybersole.Auth/Lic (R702 Out-of-Scope)` | 10 | 8 | 2 | 10 | 2,322 | `0x140773371` |
| `Cybersole.Http` | 8 | 6 | 2 | 7 | 6,197 | `0x141313990` |
| `Google.Protobuf.*` | 8 | 4 | 4 | 8 | 240 | `0x1415d8ca0` |
| `Cybersole.Services` | 7 | 5 | 2 | 7 | 4,323 | `0x14101a970` |
| `OpenTelemetry / Analytics` | 6 | 4 | 2 | 6 | 986 | `0x141981e82` |
| `Unattributed` | 258,408 | 0 | 0 | 220,307 | 27,999,113 | — |

## 四、原版 `Cybersole.*` 子系统、DTO 与三方库逐项对照矩阵

原版 `.rdata` 元数据共观测 **75** 个程序集 `*.dll`、**714** 个 `Cybersole.*` 词元、**266** 个 `PropInit` JSON/序列化 DTO、**1549** 个 `<Method>d__N` 状态机名及 **98** 个 `avares://Cybersole/` 资产。

| 子系统 / 命名空间 / 家族 | 原版实证证据（地址 / 数量） | 复刻件对应 | 分类 | 缺口与判定依据 |
|---|---|---|---|---|
| **Cybersole.Stores.Flows (18 Flows / 369 Steps)** | 3,477 direct / 5,090 attributed funcs (`0x1408..0x1412`); 103 storefront async names (408 occ) | `Cybersole.Stores/` (37,461 LOC; 3,184 `.pdata` funcs, 725 KiB) | `Partial / Missing Core Logic` | 69/103 storefront async names present (374/408 occ); missing `CheckPriceLimitApp` @ `0x143373f5f`, `FindProductCDN` @ `0x1433a0f23`, `CheckFanRewardState`/`SignUpFanRewards` @ `0x14337...`, per-store App/GraphQL variants. |
| **Cybersole.Stores.Payments (PayPal 3DS / Stripe / Adyen / Unzer / Checkout.com)** | 124 payment async names (195 occ); `0x143320000`, `0x14338294f` (`CardinalInit`), `0x143383aa9` (`ContinueUnzerThreeDs`), `0x1470530bc` (`api.checkout.com`) | `Cybersole.Stores/Payments/{PayPalThreeDs,StripeChallenge,Gateways}.cs` | `Partial / Missing Core Logic` | PayPal 3DS (9 stages) & Stripe 6 endpoints + challenge implemented (44/124 names, 115/195 occ); `UnzerGateway.CompleteActionAsync` is stubbed (missing `ContinueUnzerThreeDs`/`CardinalInit`/`CompleteConvenienceStore` @ `0x1434a...` & `api.checkout.com` gateway). |
| **Cybersole.Stores.Scripts (Kasada / Cloudflare / DataDome / PX / Akamai / Queue-it)** | Jint + Acornima (484 attributed funcs); `GenerateSensor`, `GetSbsdHash`, `DdMobileEvent`/`SensorRequest` (`0x14333fc96`), `SolverApiException` | `Cybersole.Stores/Scripts/*.cs` (`KasadaSolver`, `CloudflareStrategy`, `BrowserShim`, etc.) | `Partial / Missing Core Logic` | Kasada Jint main path & detection surface implemented; missing `GetSbsdHash`/`GetSbsdScript`, `DdMobileTouchEvent`/`SensorPow` mobile/sensor DTOs (`0x14333fc96..0x14333ff2c`), and browser-hosted challenge execution. |
| **Cybersole.Stores AI / Vision & Automated Captcha Solving** | 21 Vision DTOs (`HintLabelsRequest`..`GANResult` @ `0x14333c304`), `ExecuteClipModelAsync`/`SolveImageInCloudAsync`/`ClickCellsAsync` @ `0x1435f0000`, `CallParallax` @ `0x14345c117` | `Cybersole.Services/Captcha/{CaptchaSolverService,Drivers}.cs`, `CaptchaSurface.cs` | `Out of Scope` | User third-party API drivers (2Captcha/Parallax/Uncaptcha/HumanPresence) and detection (`CaptchaSurface`) implemented; automated CAPTCHA/anti-bot bypass execution (`ExecuteClipModelAsync`, `ClickCellsAsync`, `MoveMouseAndClickWithoutTrajectoryAsync`) is out of scope. |
| **Cybersole.Http (NetClient 0.10.0) + Brotli + Companion Packages** | `Cybersole.Http.dll`, `Cybersole.Http.{Newtonsoft,Analytics,Debug}.dll` (`0x14315a7c1..0x14316e350`), 51 attributed funcs (incl. Brotli) | `Cybersole.Http/` (384 `.pdata` funcs, 111 KiB; `BrotliDictionary.bin`) | `Partial / Missing Core Logic` | Core `SocketsHttpHandler` + TLS + Brotli dict implemented; missing `Cybersole.Http.Newtonsoft` (`LegacyJsonBody`/`LegacyJarrayBody`), `ClickHouseSink` (`FlushOnceAsync`/`DrainLocalQueueAsync` @ `0x14331...`), `Cybersole.Http.Debug` proxy stream, `Cybersole.Http.Content.IBody`, `Cybersole.Http.X509.RootCertificates.bin`. |
| **Cybersole.Services.Mail (ImapProvider / AYCD / MailKit + MimeKit)** | `MailKit.dll` + `MimeKit.dll` (22 attributed funcs @ `0x14188..0x1419e`), `WaitImapAsync` (`0x14336b99e`), `AycdCompletedTasks`/`AycdMailElement` (`0x14334cb55`) | `Cybersole.Services/Mail/{ImapMailProvider,AycdInboxClient}.cs` — **0 funcs in `Cybersole.Ui.pdb`** | `Partial / Missing Core Logic` | Classes exist in `Cybersole.Services` & pass unit tests, but are **unwired zero-caller islands** (absent from `AppServices.cs` / `TaskEngine.cs`) so NativeAOT trims 100% of `MailKit`/`MimeKit` from `Cybersole.Ui.exe`. |
| **Cybersole.Services Cloud Sync / SignalR / RabbitMQ / MSAL / Velopack** | `SignalR` (51), `MSAL` (57), `Velopack` (23), `RabbitMQ` (12), 35 `*Dto` (`0x1433473dc`) + 21 `Remote*` (`0x1433611c7`) | `BackupScheduler.cs`, `ClockService.cs`, `SettingsShell.cs` (local Velopack cache check only) | `External Blocked` | Missing `SignalR` (`/connect/app`), `RabbitMQ.Client`, `Microsoft.Identity.Client` (MSAL OAuth2), cloud `*Dto`/`Remote*` sync, and real `Velopack` update feed (`cdn.cybersole.io/releases/` returns 404; `/connect/app` requires valid login). |
| **Cybersole.Core / Models / SmartActions / Providers (Metalama Observability)** | `Cybersole.Core.dll` + `Metalama.Framework` (33 funcs @ `0x141274`), `Cybersole.Providers.IDataProvider` (`0x143216abb`), `Cybersole.Global.Strings` (`0x143210e9f`) | `Cybersole.Core/` (5,435 LOC; 194 `.pdata` funcs; handwritten `ObservableObject` + `RelayCommand`) | `Implemented` | All 143 `Cybersole.*` accessor types accounted for (`85` FQN, `44` namespace-moved, `14` in `type_classification.json`, `0` missing); `IDataProvider` is an unimplemented interface contract; `CommunityToolkit.Mvvm` in `.csproj` is unused/trimmed. |
| **Cybersole.Ui (Avalonia Views / Controls / Localization)** | 333 attributed funcs (`0x14057..0x14088`), 98 `avares://Cybersole/` assets, `Avalonia` (2,259), `AvaloniaEdit` | `Cybersole.Ui/` (20,913 LOC; 1,339 `.pdata` funcs, `Avalonia 11.3.2`) | `Implemented` | Core UI views, controls, and localization helpers implemented (excluding `AvaloniaEdit` code editor and `TaskCreatorAdvancedView` merged into `TaskCreatorView`). |
| **Cybersole.Ui.Views.Auth & LicenseControl (R702)** | `AuthWindow`, `LicenseControl`, `Cybersole.Models.License`, 10 attributed funcs (`0x14076..0x14077`) | `Auth/` (`AuthService`, `LicenseService` read-only) | `Out of Scope` | Explicitly excluded by YG R702 ruling (`docs/DECISION_LICENSE_OUT_OF_SCOPE.md`). |
| **Cybersole.Web.BrowserHandlers & DotNetBrowser (Chromium 4.3.5.8591)** | 653 attributed funcs (`0x1413d..0x14153`), `IBrowserSessionView` (`0x143636deb`), `PaymentAutofill` (`0x14352da80`), 17 `Solver*` IPC DTOs (`0x143459376`), `AngleSharp` (154) | `CustomBrowser.cs` (Avalonia placeholder window without embedded Chromium engine) | `External Blocked` | Commercial `DotNetBrowser` + external Chromium runtime (`DOTNETBROWSER_CHROMIUM_DIR`) and `Cybersole.Web.BrowserHandlers` / `AngleSharp` HTML parser are absent in replica. |

## 五、Phase 2 核心补齐优先级建议（遵循 R757 ①→②→③→④）

1. **① 站点流程与支付闭环（`Cybersole.Stores`）**：优先反编译落地真实缺口中的可执行协议状态机——`ContinueUnzerThreeDs`（`0x143383aa9` 替代 `UnzerGateway.CompleteActionAsync` 空返回）、`CardinalInit`/`CardinalContinue`（`0x14338294f`）、`api.checkout.com`（`0x1470530bc`）与 `CheckPriceLimitApp`/`FindProductCDN`（`0x143373f5f` / `0x1433a0f23`）。
2. **② 接线已写但被 AOT 裁剪的服务岛（`Cybersole.Services.Mail`）**：将已有实现与单测的 `ImapMailProvider` + `AycdInboxClient` 接入 `AppServices.cs` 与 `TaskEngine.cs` 的验证码/邮箱验证等待流程（`WaitImapAsync` @ `0x14336b99e`），使 `MailKit`/`MimeKit` 真正进入 AOT 产物。
3. **③ 传输层与可观测性伴生包（`Cybersole.Http`）**：评估并补齐 `Cybersole.Http.Newtonsoft`（`LegacyJsonBody`）、`ClickHouseSink` 批量落盘及 `Cybersole.Http.Debug` 代理调试流，按需评估 `Cybersole.Http.X509.RootCertificates.bin`。
4. **④ 外部阻塞 / 范围外明确封存**：`DotNetBrowser`（653 函数）与 `Cybersole.Web.BrowserHandlers` 保持 `External Blocked`；`SignalR`/`connect/app` 远端同步与 `Remote*` schema 待有效凭据；`AuthWindow`/`LicenseControl`（R702）及 AI/CLIP 图像验证码自动求解执行面（`ExecuteClipModelAsync`/`ClickCellsAsync`）严格保持 `Out of Scope`。
