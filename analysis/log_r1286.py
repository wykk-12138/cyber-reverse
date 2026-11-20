"""Log R1286: the five challenge surfaces and the classifier on DetectAsync."""

import io

B = """
## R1286 —— 三种抗验证码挑战的**识别面**落地（镜像里嵌着完整求解页）

### 一、取证：镜像自带求解页，逐字给出各家的 loader

| 地址 | 内容 | 逐字关键行 |
|---|---|---|
| `143ca6a9f` | reCAPTCHA v2 checkpoint | `document.Solver.Captcha.Type === 0 → document.Solver.Recaptcha()`；`=== 1 → grecaptcha.execute()` |
| `143ca8507` | reCAPTCHA Enterprise | `https://www.google.com/recaptcha/enterprise.js?render=%sitekey%` + `grecaptcha.enterprise.execute(Sitekey, { action })` |
| `143cb2699` | Cloudflare Turnstile | `https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback` + `turnstile.render("#captcha", { sitekey, callback, 'before-interactive-callback' })` |
| `147153cf4` | hCaptcha（隐形） | 选择器 `script[src*='js.hcaptcha.com/1/api.js']` |
| `146ab71b4` | reCAPTCHA v2 anchor | `/recaptcha/api2/anchor` |

**共同点**：四家都通过同一个桥回传令牌 —— `document.Solver.Captcha.Solve(token)`。
**所以差别在 loader，不在回传路径**，这才是一个分类器能同时服务四家的原因。

### 二、顺带解决了 `CAPTCHA_COVERAGE.md` 的另一条 Unknown

该文档第 73 行写着「provider 的 `Type` 字段取值没有取证」。现在有了：
checkpoint 页按 `Captcha.Type` 分支 —— **`0` = 需要点击的复选框，`1` = 隐形 `execute()`**。
这与 R1285 的「`Type` 只读」是**两件不同的事**（一个是 provider 行的来源、一个是挑战种类的行为），别混。

### 三、改了什么（有真实调用点，不是又一张表）

- 新增 `Cybersole.Stores/Flows/CaptchaSurface.cs`：五个逐字字面量 + `Classify(body)` → `hcaptcha` /
  `turnstile` / `recaptcha-enterprise` / `recaptcha-v2` / `recaptcha-v3` / `none`，并把 `Type` 的 0/1 语义
  落成 `TypeInteractive` / `TypeInvisibleExecute` / `NeedsClick`。
- `StoreFlow.DetectAsync` 现在**除了墙厂商**，还写 `c.Session.Vars["captcha.kind"]`。
  两者刻意分开：**Cloudflare 边缘也能发 Turnstile，DataDome 前面也可能站着一个 Turnstile**。
- `CaptchaSurfaceTests` 9 条：五个字面量逐字、七组 `Classify` 判据、Enterprise 不被误判成 v3、`Type` 语义。

### 四、验证

`CaptchaSurface|Detect` **21/21**；全量 **2478 通过 / 0 失败 / 2 跳过 / 2480**。

### 五、缺口状态更新（从"完全缺失"到"识别有、求解无"）

`RecaptchaEnterprise` / `TurnstileSiteKey` / `HCaptchaSpoof` 三个标记：
**识别面已落地并有调用点**；**求解面**仍缺——它需要浏览器内执行（`grecaptcha.enterprise.execute` 等），
而复刻件没有 JS 引擎，属**结构性阻塞**，下一轮要么接宿主 WebView，要么把这条明确记为不可做。
"""

V = """
---

## 第 1286 轮：三种挑战识别面落地（镜像自带求解页）

- 证据：`143ca8507`（Enterprise loader）、`143cb2699`（Turnstile loader）、`147153cf4`（hCaptcha 选择器）、
  `146ab71b4`（v2 anchor）、`143ca6a9f`（`Captcha.Type` 0=点击 / 1=隐形 execute）。
- `CaptchaSurface.Classify` 接进 `DetectAsync`，写 `captcha.kind`；与墙厂商**分开**（一个页可同时是 CF 边缘 + Turnstile）。
- 新测 9 条；全量 **2478/0/2/2480**。
- 三标记从"完全缺失"→"识别有、求解无"（求解需 JS 引擎，结构性阻塞）。
"""

H = """
## R1286 —— 挑战识别面（Enterprise/Turnstile/hCaptcha/v2/v3）接进 DetectAsync；全量 2478/0/2/2480

Observation：
- 五个 loader 字面量逐字取自 `143ca6a9f`/`143ca8507`/`143cb2699`/`147153cf4`/`146ab71b4`。
- `Captcha.Type`：0=点击复选框、1=隐形 execute（`CAPTCHA_COVERAGE.md` 第 73 行的 Unknown 结案）。
- 四家共用回传桥 `document.Solver.Captcha.Solve(token)`。
- 全量 2478/0/2/2480。

改：`CaptchaSurface`（识别 + Type 语义）+ `DetectAsync` 写 `captcha.kind` + 9 条测试。
下轮：求解面要么接宿主 WebView（真执行 `execute()`），要么把三条标记明确记为结构性不可做。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
