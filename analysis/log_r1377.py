"""R1377 record, with the three errors this round had to fix in itself."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1377 轮：**65/65 全部落地**，以及本轮我犯的三个错

- **错一：覆盖率读错了三轮。** `operation_gap.py` 打两个数 ——「复刻件声明了多少操作名」与「镜像 65 个里带了几个」。
  我把前者当后者，于是「64/65、只剩一条」是假的：**真实 62/65，缺 3**。
  **工具已改**：现在固定打印 `carried: N of M image operations (absent K)`，比率不可能再被读错。
- **真正缺的三条**（地址从清单取，不从记忆取）：`SignInAsGuest`(453, `$medium`)、
  `addToCart`(232, `$sku/$qty/$type/$info`)、`buynow`(216, `query`)。
- **错二：族归错了。** 先把三条都塞进会话族 —— 但 `addToCart`/`buynow` 的词汇是 **Magento 的**
  （`quote_id`、`type: "Simple"`、`bundleOptions`、`isNormalBuyFlow`、返回 `cart_id`/`session_id`）
  → **移进 `MagentoCart`**，只留 `SignInAsGuest`。
- **错三：又是 `rfind('}')`。** 追加方法时用文件最后一个括号定位类尾 —— **方法落到类外**，
  `BuyNowDocument`/`AddToCartDocument`/`PostAsync` 三个"不存在"。**这是本项目第三次为同一行买单**
  （R1369 一次，本轮一次，加上早前一次）。**改成可复用助手 `analysis/insert_into_class.py`**（带括号配对、跳过字符串与注释）。
- **两个守卫也因此救了两件事**：`EveryDocumentConstantIsWhole`（我把 `buynow` 从文件里截断了）与
  `EveryDocumentConstantHasAProductionCaller`（常量不是功能 —— 现在有 `AddToCartAsync`/`BuyNowAsync`，
  由 `MagentoFlow.AddToCartAsync` 调用）。
- **一次过滤器的假红**：单独跑 `ShapeAuditGuardTests|BindScopeGuardTests` 两个"外部工具"类会失败其一，
  **跑全量 `Speed!=Slow` → 2860 通过 / 0 失败 / 2 跳过**。两个 external-tool 类在同一进程里共享状态，
  **这两个类必须整跑，不能拼过滤条件** —— 已写进注意事项。

### 五要素

- **改了什么**：`StoreSessionQueries`（+`SignInAsGuestDocument`）；`MagentoCart`（+`AddToCartDocument`/`BuyNowDocument`
  + `AddToCartAsync`/`BuyNowAsync`/`SendDocumentAsync`）；`MagentoFlow.AddToCartAsync` 加分支；
  `operation_gap.py` 增比率行；新增 `insert_into_class.py` 等 6 个脚本；重发布；METRICS 重生成。
- **验证命令与输出**：全量 `Speed!=Slow` → **2860/0/2**；`GeneratedDocumentTests|MagentoCartTests|StoreSessionQueries`
  → **62/62**；`operation_gap.py` → **`carried: 65 of 65 (absent 0)`**。
- **数字变化**：覆盖 **62 → 65/65（absent 0）**。
- **证据等级**：Observation —— 三条文档长度与声明集、Magento 词汇、两个守卫的断言、全量套件结果。
  **Correction ×3** —— 覆盖率读法、族归属、`rfind('}')`。
- **还剩什么**：浏览器侧结账面（需界面上下文）；`AddressInput` 构造点（名字已知）。
"""

POINTER = """
---

## 第 1377 轮（覆盖结案 65/65）

- **65/65，absent 0。** 最后三条按词表归位：`SignInAsGuest` → 会话族；`addToCart`/`buynow` → **`MagentoCart`**
  （`quote_id`/`Simple`/`isNormalBuyFlow` 是 Magento 词汇），并补上 `AddToCartAsync`/`BuyNowAsync` 真实调用者。
- **我连着三轮报错覆盖率**：`operation_gap.py` 打两个数，我读了错的那个。**工具已改为打印比率行。**
- **`rfind('}')` 第三次坑我** → 抽出可复用 `analysis/insert_into_class.py`（括号配对 + 跳过字符串/注释）。
- **过滤器注意**：`ShapeAuditGuardTests` 与 `BindScopeGuardTests` 是 external-tool 类，
  **单独拼过滤会假红**；以全量 `Speed!=Slow` 为准（本轮 2860/0/2）。
- 只剩浏览器侧结账面。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1377 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1377 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if '65 of 65' not in text:
    text += """
---

## 十六、GraphQL 操作覆盖结案（R1377）

**`carried: 65 of 65 image operations (absent 0)`** —— 以 `analysis/operation_gap.py` 的比率行为准
（此前三轮我误读了该工具的两个数字，已改工具）。

最后三条：`SignInAsGuest`(453) → 会话族；`addToCart`(232)、`buynow`(216) → **`MagentoCart`**，并有真实调用者。

**仍开放**：浏览器侧结账面；`AddressInput` 的构造点。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated')
