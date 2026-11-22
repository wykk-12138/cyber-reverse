"""R1373 record: /cartApi/checkout has a sender, and its host stops one label short."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1373 轮：`/cartApi/checkout` 的发送方找到了 —— **R1372 那条判据第一次派上用场**

- **按 R1372 的规矩查**（`disp32` 命中必须由函数字面量表确认）：路径只有一条精确串 `0x146AB27FC`，
  命中三个站点中**只有一个映射到真函数** `0x140C32160`，而它的字面量表**确实带着这条路径** ⇒ **真引用**。
- **那个函数的 11 个字面量**：
  ```
  /cartApi/checkout   CartType   CouponReferences   LineItems   LocationId
  Retail   Shopify    SourceSystem   https://   themeapis   www
  ```
  → 端点 = `https://` + `www` + `themeapis` + **<顶级域>** + `/cartApi/checkout`；
  体里有 `CartType`（两个值 `Retail`/`Shopify`）、`LineItems`、`LocationId`、`SourceSystem`、`CouponReferences`。
- **顶级域不在这 11 个字面量里** ⇒ **由调用方给**，**不替镜像写 `.com`**。
  `HostFor(tld)` / `UrlFor(tld)` 明确表达这一点；`Body(...)` 只接受那两个值，其它值抛 `ArgumentOutOfRangeException`。
- **接线进 `GetCartAsync`**（`themeapis.domain` 触发），确保不被裁。
- **产物**：`/cartApi/checkout` **ASCII 命中 1**、`themeapis` **UTF-16 命中 10 / ASCII 1**；
  尺寸 62,041,088 → **62,047,744**。

### 五要素

- **改了什么**：新增 `Flows/ThemeApisCheckout.cs`、`tests/ThemeApisCheckoutTests.cs`（3 条）；
  `StoreFlow.GetCartAsync` 加分支；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ThemeApisCheckoutTests` → **3/3**；`StoreFlow|ThemeApis` → **24/24**；
  `orphan_documents.py` → 0；产物命中见上；尺寸 +6,656 字节。
- **数字变化**：套件 +3；`/cartApi/checkout` 从"发送方未定位"变成**已实现**。
- **证据等级**：Observation —— 精确串地址、唯一真引用函数、11 个字面量清单、产物双编码命中。
- **还剩什么**：3 类 —— AO 三个体、Saucony 六步、浏览器侧结账面。
"""

POINTER = """
---

## 第 1373 轮

- **`/cartApi/checkout` 发送方 = `0x140C32160`**（字面量表确认，非 disp32 噪声）：11 个字面量给出
  `https://` + `www` + `themeapis` + <顶级域> + `/cartApi/checkout`，体字段 `CartType`/`LineItems`/`LocationId`/
  `SourceSystem`/`CouponReferences`，`CartType` 两值 `Retail`/`Shopify`。
- **顶级域不在镜像里** ⇒ 由调用方给，**不写 `.com`**。实现 `Flows/ThemeApisCheckout`，接进 `GetCartAsync`。
- 产物 `/cartApi/checkout` ASCII 命中 1、`themeapis` UTF-16 命中 10。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1373 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1373 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'ThemeApisCheckout' not in text:
    text += """
---

## 十三、`/cartApi/checkout` 已结案（R1373）

**发送方 `0x140C32160`**，字面量表确认（R1372 判据）。端点 `https://www.themeapis.<tld>/cartApi/checkout`，
**顶级域镜像未给 → 调用方给**。

体字段：`CartType`（`Retail`/`Shopify`）、`LineItems`、`LocationId`、`SourceSystem`、`CouponReferences`。
实现：`Flows/ThemeApisCheckout`，接进 `StoreFlow.GetCartAsync`。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: cartApi/checkout closed')
