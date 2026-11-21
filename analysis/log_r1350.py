"""R1350 record: the signature detector's limit, and the payment step it could not place."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1350 轮：签名聚类**只认得我写进去的族**——认不出的，要问"谁在发它"

- **把 A 块剩下的 11 份文档全解出来，按签名打分**：结果**全部 `none`**。
  原因很实在：这些短文档各有各的签名（`$handle`、`$email`、`$storeKey`/`$currency`/`$taxMode`、`$cartId`、
  `$address`/`$saveAddress`…），**没有一个落在我已知的三个族的词表里**。
  **所以这个检测器的能力边界是"已知族"，不是"任意族"。** 这条写进脚本头，别当成"它们不属于任何族"。
- **认不出的该问什么**：`createCheckoutPayment`（222 字符，`$storefront`/`$withoutShippingAddressSet`）
  唯一引用点 `0x140B56EA4` → 落在 `sub_140B56CC0`，**正是 R1339 扫 Highsnobiety 主机时列出的 "Create payment" 发送方**。
  同一个块、同一个主机、同一个操作 —— **归 Highsnobiety**。
- **落码**：`HighsnobietyFlow.SubmitPaymentAsync`（两个变量都由调用方给：`$storefront` 缺失就拒绝，
  `withoutShippingAddressSet` 由会话布尔决定）。
- **产物**：`mutation createCheckoutPayment` UTF-16 命中 **1**；尺寸 62,024,512 → **62,029,632**。

### 五要素

- **改了什么**：`RetailFlows.cs`（Highsnobiety 支付步）；`HighsnobietyFlowTests.cs`（+3 条，共 16）；
  新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`HighsnobietyFlowTests` → **16/16**；`operation_gap.py` → 覆盖 **32/65**（缺 33）；
  `orphan_documents.py` → 0；`audit_document_constants.py` → **35 常量 / 0 问题**；
  产物命中 1；尺寸 62,024,512 → 62,029,632。
- **数字变化**：覆盖 31 → **32**；缺 34 → **33**；套件 +3；产物 +5,120 字节。
- **证据等级**：Observation —— 11 份文档的声明集全部落空、`createCheckoutPayment` 的引用点落在 Highsnobiety 发送方内、产物命中。
- **还剩什么**：A 块 9 份（签名互异，需逐个找发送方）；B 块 7 个（无主机）；`approveMemberPayment` 两方言；
  浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1350 轮

- **签名聚类只认得写进词表的族**：A 块 11 份短文档全部 `none`（各有各的签名）。**这不是"不属于任何族"，是检测器的边界。**
- 认不出时的正确问法：**谁在发它**。`createCheckoutPayment`(222) 的引用点落在 `sub_140B56CC0` ——
  R1339 已列为 Highsnobiety 的 "Create payment" 发送方 → **归 Highsnobiety**，落成 `SubmitPaymentAsync`。
- 覆盖 31 → **32/65**，缺 34 → **33**；产物 `mutation createCheckoutPayment` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1350 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1350 \u8f6e')
