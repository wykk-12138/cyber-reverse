# 产物验证（生成文件，请勿手改）

> 由 `python analysis/verify_artifact.py` 生成。检查的是**发布出来的 AOT 产物**，
> 不是源码 —— AOT 重建后裁剪/重排/压缩都可能让资源与文案消失，而现有度量只看源码。

## 产物

| 项 | 值 |
|---|---|
| 路径 | `replica\.publish-aot\Cybersole.Ui.exe` |
| 字节 | 56399872 |

## locale 键存活

**1142/1142** 个 `en.json` 键出现在产物字节里

## 内嵌资源存活

**逻辑名 20/20 · 内容指纹 20/20**

| 资源 | 字节 | 逻辑名 | 内容指纹 |
|---|---|---|---|
| `Cybersole.Locales.en.json` | 63113 | yes | yes |
| `Cybersole.Locales.ja.json` | 72311 | yes | yes |
| `Cybersole.Locales.ko.json` | 67930 | yes | yes |
| `Cybersole.Locales.zh-Hans.json` | 61369 | yes | yes |
| `Cybersole.ProfileValidation.en.json` | 6214 | yes | yes |
| `Cybersole.Engine.Captcha.html` | 6757 | yes | yes |
| `Cybersole.Engine.CaptchaEnterprise.html` | 7894 | yes | yes |
| `Cybersole.Engine.EmptySolver.html` | 7777 | yes | yes |
| `Cybersole.Engine.Geetest.html` | 1826 | yes | yes |
| `Cybersole.Engine.GeetestV4.html` | 1138 | yes | yes |
| `Cybersole.Engine.HCaptcha.html` | 18453 | yes | yes |
| `Cybersole.Engine.Question.html` | 4201 | yes | yes |
| `Cybersole.Engine.Turnstile.html` | 1393 | yes | yes |
| `Cybersole.Engine.Ynap.html` | 8225 | yes | yes |
| `Cybersole.Engine.Popmart.html` | 3652 | yes | yes |
| `Cybersole.Engine.castle.js` | 328998 | yes | yes |
| `Cybersole.Engine.hcaptcha-spoof.js` | 606240 | yes | yes |
| `Cybersole.Engine.trustdevice.js` | 507 | yes | yes |
| `Cybersole.Engine.trustdevice-botd.js` | 1058 | yes | yes |
| `Cybersole.Http.Compression.BrotliDictionary.bin` | 122784 | yes | yes |

## 资源树叶数

| | 叶子 |
|---|---|
| 原版 | 12 |
| 复刻件 | 12 |

---

**结论**：全部通过

