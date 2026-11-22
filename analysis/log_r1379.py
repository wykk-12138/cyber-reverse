"""R1379 record: the browser surface was in the image, and the last open item closes."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1379 轮：**浏览器侧 PayPal 不在"需要抓包"那一栏** —— 它就在镜像里，一个函数写全了

- **我把它归错了两轮。** 一直写"需要界面上下文"。用 R1378 的新工具查三个头的引用：
  `x-paypal-internal-euat` 有 16 个站点，其中一个映射到 **`0x140F4C550`，38 个字面量** —— **整套都在里面**：
  ```
  x-app-name = checkoutuinodeweb_hermione     x-paypal-internal-euat      paypal-client-metadata-id
  accept / content-type / cookie / origin / referer / user-agent
  sec-ch-ua / sec-ch-ua-mobile / sec-ch-ua-platform / sec-fetch-dest / sec-fetch-mode / sec-fetch-site
  accept-language = en-GB          PayWithQuery / operationName / query / variables
  token / withSplitTender / expeirences(!)      https://www.paypal.com / mep/dashboard
  application/json / IFRAME / login / signin
  ```
- **能落地的**：`x-app-name` 的**值**、十五个请求头名、`en-GB`、`sec-fetch-*` 三个固定值、
  体里的 `PayWithQuery` + `token`/`withSplitTender`/**`expeirences`**（镜像自己的错拼，第四次）。
- **不能落地的**：`x-paypal-internal-euat` 与 `paypal-client-metadata-id` 的**值** —— 那是页面会话的，
  与 storefront 令牌同一条规矩：**由调用方给，缺了就拒绝并说明缺哪个**。
- **一次被裁掉**：第一版只加了类，产物尺寸**一字未变**、三个字面量 0 命中 —— **没有生产调用者，AOT 把它整个裁了**
  （R1370 的教训第二次应验）。接进 `StoreFlow.SubmitPayPalAsync` 后尺寸 +6,656，
  且新增消息串 `browser surface: no ` **UTF-16 命中 3** 作为正向证据。
- **产物**：三个头名本身 0 命中（§4.5：无结论），**以尺寸增长 + 消息串命中为准**；尺寸 62,085,632 → **62,092,288**。

### 五要素

- **改了什么**：新增 `Payments/PayPalBrowserSurface.cs`（常量 + `Headers` + `Body` + `CanSend` + `SendAsync`）、
  `tests/PayPalBrowserSurfaceTests.cs`（4 条）；`StoreFlow.SubmitPayPalAsync` 加分支；新增 3 个 analysis 脚本；
  重发布；METRICS 重生成。
- **验证命令与输出**：`PayPal*` → **91/91**；`orphan_documents.py` → 0；`operation_gap.py` → **65 of 65 (absent 0)**；
  产物 `browser surface: no ` UTF-16 命中 3；尺寸见上。
- **数字变化**：套件 +4；**OPEN_ITEMS 的最后一条关闭**。
- **证据等级**：Observation —— 38 个字面量清单、产物尺寸增长与消息串命中。
  **Correction** —— 「浏览器结账面需要界面上下文」是我的归类错误；只有两个**值**需要会话，形状全在镜像里。
- **还剩什么**：`OPEN_ITEMS` 里已无"静态可推进"项。
"""

POINTER = """
---

## 第 1379 轮（清单关闭）

- **浏览器侧 PayPal 不是外部依赖**：`0x140F4C550` 的 38 个字面量给出 `x-app-name = checkoutuinodeweb_hermione`、
  十五个头名、`en-GB`、`sec-fetch-*`、`PayWithQuery` + `token`/`withSplitTender`/`expeirences`、
  `https://www.paypal.com`。落成 `Payments/PayPalBrowserSurface`，接进 `SubmitPayPalAsync`。
- **只有两个值是会话的**（euat、client-metadata-id）→ 由调用方给，缺了拒绝并说明缺哪个。
- **又一次"只写类被裁"**：尺寸一字未变、字面量 0 命中；接线后 +6,656，消息串 `browser surface: no ` 命中 3。
- **OPEN_ITEMS 已无静态可推进项。**
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1379 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1379 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'PayPalBrowserSurface' not in text:
    text += """
---

## 十七、浏览器侧 PayPal 已结案（R1379）

它**不**需要抓包：`0x140F4C550` 的 38 个字面量给出完整形状 ——
`x-app-name = checkoutuinodeweb_hermione`、`x-paypal-internal-euat`、`paypal-client-metadata-id`、
浏览器头集、`en-GB`、`PayWithQuery` + `token`/`withSplitTender`/`expeirences`（镜像错拼）、`https://www.paypal.com`。

实现：`Payments/PayPalBrowserSurface`，接进 `StoreFlow.SubmitPayPalAsync`。
**只有两个值是页面会话的**（euat、client-metadata-id）→ 调用方给，缺则拒绝并说明。

**至此 OPEN_ITEMS 里已无"静态可推进"项。**
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: last static item closed')
