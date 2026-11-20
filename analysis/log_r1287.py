"""Log R1287: the engine evidence that settles the three captcha markers."""

import io

B = """
## R1287 —— 三条 captcha 标记**结构性不可做**的判定（原版自带 Chromium）

### 一、判据：镜像用 DotNetBrowser 4.3.5.8591 跑 JS

| 证据 | 内容 |
|---|---|
| `178267`–`178273` | `DotNetBrowser.Core, Version=4.3.5.8591, PublicKeyToken=b0b5aaca9c95c84e` + 六平台 `DotNetBrowser.Chromium.{Chromium32,Chromium64,ChromiumWinArm,ChromiumLinux,ChromiumLinuxArm,ChromiumMac,ChromiumMacArm}.xml` |
| `146a8b90c` | 原文：*In Native AOT deployments, Chromium binaries must be pre-deployed manually. Set the `DOTNETBROWSER_CHROMIUM_DIR` environment variable or the `EngineOptions.ChromiumDirectory` property…* |
| `146b31fac` | 原文：*AOT mode detected: Chromium binaries could not be found in '* |
| `143dedc4e` / `143e0ef3b` / `143e30348` | Chromium 包清单 XML；`chrome.dll` **279,543,704 / 312,526,744 / 294,748,056** 字节，另有 `icudtl.dat`、`chrome_100_percent.pak`、`chrome.dll.sig` |
| `1470a1ef4` / `1470ad964` / `147100c44` | `imgs.hcaptcha.com` / `js.hcaptcha.com` / `newassets.hcaptcha.com`（页面侧脚本域） |

⇒ 原版**在嵌入式 Chromium 里真跑** R1286 那几行：`grecaptcha.enterprise.execute(...)`、`turnstile.render(...)`、
`document.Solver.Captcha.Solve(token)`。所以三家标记的**执行面**不是"还没写"，而是**需要一个浏览器引擎**。

### 二、判定（分类结案，不再占轮次）

| 标记 | 识别面 | 执行面 | 结论 |
|---|---|---|---|
| `HCaptchaSpoof` | ✅ R1286（`js.hcaptcha.com` 选择器） | ❌ | **需引擎**；`HCaptchaSpoof` 本身是某类型上的 bool 属性（backing-field 证据），其语义（如何 spoof）无协议证据 |
| `RecaptchaEnterprise` | ✅ R1286（`enterprise.js?render=`） | ❌ | **需引擎**：`grecaptcha.enterprise.execute` 必须在浏览器里跑 |
| `TurnstileSiteKey` | ✅ R1286（`turnstile/v0/api.js`） | ❌ | **需引擎**：`turnstile.render` 同上；实值 `0x4AAAAAACm-_-PQVKerNsuH` 已记录（`14339635d`） |

**所缺条件写清**：接同等引擎 = 引入新依赖（DotNetBrowser 商业授权；WebView2/CefSharp 需另行裁决）。

### 三、本轮改了什么

- `tools/captcha_coverage.py`（**生成器，不是生成物**）：§五的"完全缺失"改为"**无执行面**（识别面见 §七）"；
  §六的 `Type` 未知条目换成 **R1286 已结案**的表述；新增 **§七**，把上面五条证据与判定写进去。
- **生成物 `docs/CAPTCHA_COVERAGE.md` 本轮未重生成**：IDA 数据库刚修复，`strings_cache_ready: false`，
  `ida.py str` 在插件层抛异常（`zeromcp/jsonrpc.py:150 dispatch`）。生成器自带"对照组失败就拒绝覆盖"的保护
  （`kpsdk=0` → 拒绝写假零），所以我**没有绕过它**。下次 IDA 字符串缓存就绪后跑一次即可。

### 四、验证与诚实边界

- 生成器改动：`python analysis/update_captcha_generator.py` → `generator updated`。
- 生成物：**未更新**，原因如上（工具未就绪，不是我判断它不该更新）。
- IDA 侧本轮状态：三次重启（进程退出过一次）→ 三个模态框用 CUA 点掉 → `health = ok`、`hexrays_ready: true`、
  **`strings_cache_ready: false`** ← 这正是 `str` 查询失败的原因。

证据等级：Observation = 五类字符串与字节数、IDA 的健康字段原文；
Inference = 「三条执行面需引擎」；Unknown = `HCaptchaSpoof` 的具体行为（无协议证据）。
"""

V = """
---

## 第 1287 轮：三条 captcha 标记判为**结构性不可做**（原版用 DotNetBrowser + 外部 Chromium）

- 证据：`DotNetBrowser.Core 4.3.5.8591` + 六平台 Chromium 清单；`DOTNETBROWSER_CHROMIUM_DIR` AOT 约束原文；
  `chrome.dll` 279–312 MB 三份。
- 判定：`HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 识别面已有（R1286），**执行面需引擎**，
  从待办移出并写清所缺条件。
- 改的是**生成器**（`tools/captcha_coverage.py`，新增 §七）；生成物**未重生成**——IDA `strings_cache_ready: false`，
  `ida.py str` 抛异常，生成器拒绝覆盖（保护正确，未绕过）。
"""

H = """
## R1287 —— captcha 三条标记结构性判定完成；生成器已改、生成物待 IDA 缓存就绪后重生成

Observation：
- `DotNetBrowser.Core 4.3.5.8591`；`146a8b90c` 的 AOT 约束原文；`chrome.dll` 279/312/294 MB。
- IDA 本轮重启后 `health=ok`、`hexrays_ready=true`、**`strings_cache_ready: false`**（`ida.py str` 抛异常的真因）。

改：`tools/captcha_coverage.py` 新增 §七 + 措辞（"完全缺失"→"无执行面"）；生成物未重生成（工具未就绪，未绕过保护）。

下轮：IDA 缓存就绪后重生成文档；随后回优先级①——`Stores/Flows` 的 58 处 `inferred` 按站点批量核销。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
