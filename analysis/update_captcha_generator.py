"""R1287: teach the captcha coverage generator what the engine evidence settles.

Two edits, both in the generator rather than in the generated file:
  * the replica table stops saying "completely missing" for markers whose recognition now exists (R1286) and whose
    execution cannot exist without a browser;
  * the boundary section loses the `Type` question, which 143ca6a9f answered, and gains the DotNetBrowser finding.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/captcha_coverage.py'
text = io.open(P, encoding='utf-8').read()

# 1. the replica marker table: name what is actually missing
old_row = '        add("| `%s` | %s | %s |" % (marker, where, "名字被引用" if hits else "**完全缺失**"))'
new_row = '\n'.join([
    '        add("| `%s` | %s | %s |" % (marker, where, "名字被引用"',
    '                                             if hits else "**无执行面**（识别面见 §七）"))',
])
if old_row not in text:
    raise SystemExit('row anchor missing')
text = text.replace(old_row, new_row)

# 2. the boundary section: the Type question is answered, and the engine is the real constraint
SECTION = """
    add("- **`Captcha.Type` 的取值已结案（R1286）**：`143ca6a9f` 的 checkpoint 页按它分支 —— `0` 是需要点击的复选框，`1` 是隐形 `execute()`。它与 provider 行的 `Type` 是两件事。")
    add("")
    add("## 七、为什么求解面是**结构性**缺的：原版自带 Chromium")
    add("")
    add("| 证据 | 内容 |")
    add("|---|---|")
    add("| `178267`–`178273` | `DotNetBrowser.Core, Version=4.3.5.8591` + 六平台 `DotNetBrowser.Chromium.*.xml` 清单 |")
    add("| `146a8b90c` | 原文：Native AOT 部署下 Chromium 二进制须手工预置 —— 设 `DOTNETBROWSER_CHROMIUM_DIR` 或 `EngineOptions.ChromiumDirectory` |")
    add("| `146b31fac` | 原文：AOT mode detected: Chromium binaries could not be found |")
    add("| `143dedc4e` 等 | Chromium 包清单 XML，`chrome.dll` 279–312 MB |")
    add("| `1470a1ef4` / `1470ad964` | `imgs.hcaptcha.com` / `js.hcaptcha.com`（页面侧脚本域） |")
    add("")
    add("**→ 原版在嵌入式 Chromium 里真跑 `grecaptcha.enterprise.execute()` 与 `turnstile.render()`**，所以")
    add("`HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 的**执行面**不是「还没写」，而是**需要一个浏览器引擎**。")
    add("复刻件当前没有；接入等于引入新依赖（DotNetBrowser 为商业授权，开源替代需另行裁决）——")
    add("因此这三条从待办移出，理由与所缺条件如上。")
    add("")
    add("**→ 而识别面不依赖引擎**：R1286 的 `CaptchaSurface` 用五个 loader 字面量认出四家挑战，已接进 `StoreFlow.DetectAsync` 写 `captcha.kind`。")
    add("")
"""
old_bounds = '    add("- **provider 的 `Type` 字段取值没有取证**：它区分什么（挑战类型还是服务商）要读 `CaptchaProvider` 的用法。")\n    add("")\n'
if old_bounds not in text:
    raise SystemExit('bounds anchor missing')
text = text.replace(old_bounds, SECTION.lstrip('\n'))

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('generator updated')
