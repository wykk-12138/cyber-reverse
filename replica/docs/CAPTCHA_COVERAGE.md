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
| `HCaptchaSpoof` | **（无）** | **完全缺失** |
| `RecaptchaEnterprise` | **（无）** | **完全缺失** |
| `GeetestV4` | `Enums.cs` | 名字被引用 |
| `TurnstileSiteKey` | **（无）** | **完全缺失** |

**→ 与 `PAYMENT_CHALLENGES.md` 同一个判据：名字出现不等于实现。**

## 六、边界

- **有属性名不等于有协议**：`HCaptchaSpoof` 证明原版有那一步，不证明它发什么。
- **家族的变体数不等于组合数**：reCAPTCHA 的四个变体可以共享一条提交路径，也可以是四条。
- **provider 的 `Type` 字段取值没有取证**：它区分什么（挑战类型还是服务商）要读 `CaptchaProvider` 的用法。
