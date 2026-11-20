# captcha 覆盖（生成物 —— 不要手改）

由 `python tools/captcha_coverage.py` 生成。填补目标 ②的「各家 captcha」那一块 ——
前五家（Kasada · Cloudflare · DataDome · PerimeterX · Queue-it）在 `VendorWiring`，captcha 一直没枚举过。

## 一、对照

| 对照串 | 命中 |
|---|---|
| `kpsdk` | **17** |

**→ 对照成立，所以下面的零可读。**

## 二、原版支持的挑战家族

| 家族 | 命中 | 首条地址 | 变体（取自属性与任务名） |
|---|---|---|---|
| **reCAPTCHA** | **181** | `0x14320fa3a` | Recaptcha · RecaptchaInvisible · RecaptchaV3 · RecaptchaEnterprise |
| **hCaptcha** | **91** | `0x14322589a` | HCaptcha · HCaptchaInvisible · HCaptchaSpoof |
| **Cloudflare Turnstile** | **39** | `0x1432258b4` | Turnstile · CloudflareTurnstile · LoopTurnstile · turnstileToken |
| **GeeTest** | **15** | `0x143225880` | Geetest · GeetestV4 · GeeTestTask · GeeTestTaskProxyLess · Geetest.html · GeetestV4.html |
| **Castle** | **55** | `0x143159cbb` | get_Castle |
| **TrustDevice** | **16** | `0x1432258df` | TrustDeviceGen · TrustDeviceBotDOpen · static.trustdecision.com |

## 三、明确的零（有对照）

| 家族 | 命中 |
|---|---|
| Funcaptcha / ArkoseLabs | **0** |
| MTCaptcha | **0** |

**→ 所以「原版支持所有主流 captcha」是**错的**：Funcaptcha/Arkose 与 MTCaptcha 一次都不出现。**
→ 而这是**负结论**，它只有在对照成立时才有意义 —— 而对照是 `kpsdk 17`。**

## 四、而 provider **不是内建的**

`Cybersole.CaptchaProviders.CaptchaProvider` 的字段（命中 24 条元数据）：

- `Priority`
- `Name`
- `Type`
- `ApiKey`
- `Balance`
- `Count`
- `Concurrency`
- `BalanceSupported`
- `IsFetchingBalance`

**→ 那是一张**用户配置**的服务表**：每家有自己的 `ApiKey`、`Balance`、`Concurrency`、`Priority`，
而 `Settings.CaptchaProvidersView` 带 `EnabledProviders` / `Add` / `Reorder` —— 可启用、可排序。

**→ 所以原版的 captcha 走**用户第三方**（`VendorWiring.Solver.UserThirdParty`），
而那是这个值的**正面依据**：此前它只靠「没有本地 solver」这个缺席来支撑。**
**→ 而 `Geetest.html` / `GeetestV4.html` 说明 GeeTest 有一条**本地**路径**（页面内联脚本），
所以同一个家族可以两种方式都在 —— 与 R1025 的 queue-it「两种表面」同族。

## 五、复刻件侧

| 标记 | 出现在 | 性质 |
|---|---|---|
| `CaptchaProvider` | `Profiles.cs` · `GlobalSettings.cs` · `Stores.Abstractions.cs` · `CaptchaSolverService.cs` · `Drivers.cs` · `ThirdPartyDrivers.cs` · `ProviderViews.cs` · `SettingsShell.cs` · `SettingsModals.cs` | 名字被引用 |
| `HCaptchaSpoof` | **（无）** | **无执行面**（识别面见 §七） |
| `RecaptchaEnterprise` | **（无）** | **无执行面**（识别面见 §七） |
| `GeetestV4` | `Enums.cs` | 名字被引用 |
| `TurnstileSiteKey` | **（无）** | **无执行面**（识别面见 §七） |

**→ 与 `PAYMENT_CHALLENGES.md` 同一个判据：名字出现不等于实现。**

## 六、边界

- **有属性名不等于有协议**：`HCaptchaSpoof` 证明原版有那一步，不证明它发什么。
- **家族的变体数不等于组合数**：reCAPTCHA 的四个变体可以共享一条提交路径，也可以是四条。
- **`Captcha.Type` 的取值已结案（R1286）**：`143ca6a9f` 的 checkpoint 页按它分支 —— `0` 是需要点击的复选框，`1` 是隐形 `execute()`。它与 provider 行的 `Type` 是两件事。

## 七、为什么求解面是**结构性**缺的：原版自带 Chromium

| 证据 | 内容 |
|---|---|
| `178267`–`178273` | `DotNetBrowser.Core, Version=4.3.5.8591` + 六平台 `DotNetBrowser.Chromium.*.xml` 清单 |
| `146a8b90c` | 原文：Native AOT 部署下 Chromium 二进制须手工预置 —— 设 `DOTNETBROWSER_CHROMIUM_DIR` 或 `EngineOptions.ChromiumDirectory` |
| `146b31fac` | 原文：AOT mode detected: Chromium binaries could not be found |
| `143dedc4e` 等 | Chromium 包清单 XML，`chrome.dll` 279–312 MB |
| `1470a1ef4` / `1470ad964` | `imgs.hcaptcha.com` / `js.hcaptcha.com`（页面侧脚本域） |

**→ 原版在嵌入式 Chromium 里真跑 `grecaptcha.enterprise.execute()` 与 `turnstile.render()`**，所以
`HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 的**执行面**不是「还没写」，而是**需要一个浏览器引擎**。
复刻件当前没有；接入等于引入新依赖（DotNetBrowser 为商业授权，开源替代需另行裁决）——
因此这三条从待办移出，理由与所缺条件如上。

**→ 而识别面不依赖引擎**：R1286 的 `CaptchaSurface` 用五个 loader 字面量认出四家挑战，已接进 `StoreFlow.DetectAsync` 写 `captcha.kind`。
