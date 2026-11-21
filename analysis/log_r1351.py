"""R1351 record: one of three senders names its endpoint, and two share the unattributed pile."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1351 轮：三个发送方，**只有一个说了自己往哪发**；另两个进入"无主机"那一堆

- **三份一起找发送方**（`getProductDetails` 499 / `saveAddress` 296 / `maintainShippingGroups` 223）：
  **三个都没有主机**。分开它们的是**路径**：
  ```
  getProductDetails    apps/product-drops?kind=mutation&operation=getProductDetails
  saveAddress          只有 envelope 键，无路径
  maintainShippingGroups  只有 envelope 键，无路径
  ```
  **`getProductDetails` 的操作名走在查询串里**（和 PayPal 合作方那族同形），所以它可归属、可落地；
  另两个**归入"不可归属"清单**（`.unattributed_operations.json`，与 `getCart` 同处），**不硬凑族**。
- **落码**：`ShopifyProductDrops`（Path 含查询串 / Document 499 / `DeclaredVariables=["handle"]` / FetchAsync），
  接进 `ShopifyFlow.FindProductAsync`（`productdrops.origin` 触发，handle 默认取 URL 解析值）。
- **又一次"先假设形状"**：测试里我写 `query getProductDetails($handle: String!)`，
  实际是 **`mutation getProductDetails($handle: String)`** —— **可空、且是 mutation**。已按实测改。
  另一条断言撞上 `TinyServer` **不保留查询串**，改成在常量上验查询串、在 `Path` 上验路径。
- **产物**：`mutation getProductDetails` UTF-16 命中 **1**、`product-drops` 命中 **7**；尺寸 62,029,632 → **62,038,528**。

### 五要素

- **改了什么**：新增 `Flows/ShopifyProductDrops.cs`、`tests/ShopifyProductDropsTests.cs`（6 条）；
  `ShopifyFlow.cs`（drops 分支）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopifyProductDropsTests|ShopifyGraphQlTests` → **18/18**；
  `operation_gap.py` → 覆盖 **33/65**（缺 32）；`orphan_documents.py` → 0；`audit_document_constants.py` → **36 常量 / 0 问题**；
  产物两串命中 1/7；尺寸见上。
- **数字变化**：覆盖 32 → **33**；缺 33 → **32**；套件 +6；产物 +8,896 字节。
- **证据等级**：Observation —— 三个发送方的主机/路径差异、文档 499 字符与真实首行（mutation、可空）、产物命中。
- **还剩什么**：不可归属 3 个（`saveAddress`/`maintainShippingGroups`/`getCart` 等）；A 块 7 份（`cartCreate` 91、
  `initiateCheckout` 251、`createMyPayment` 493、`customerAccessTokenCreate` 250、`createCartByStore` 421、
  `createCheckout` 720、`checkoutAsGuest` 148）；B 块其余；`approveMemberPayment` 两方言；浏览器侧结账面；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1351 轮

- 三个发送方一起查：`getProductDetails`(499) 的路径 **`apps/product-drops?kind=mutation&operation=getProductDetails`**
  → 可归属，落成 `ShopifyProductDrops` 并接进产品步；`saveAddress`/`maintainShippingGroups` **无主机无路径**
  → 进 `.unattributed_operations.json`（与 `getCart` 同堆），**不硬凑族**。
- **测试又栽在"假设形状"**：实际是 `mutation getProductDetails($handle: String)`（可空、mutation），
  不是 `query … String!`；另 `TinyServer` 不保留查询串，断言改到常量上。
- 覆盖 32 → **33/65**，缺 33 → **32**；产物 `mutation getProductDetails` 命中 1、`product-drops` 命中 7。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1351 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1351 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'ShopifyProductDrops' not in text:
    text += """
## product-drops（R1351）

`getProductDetails`(499 @0x1470F43C4) 的发送方 `sub_140C81880` 拼
`apps/product-drops?kind=mutation&operation=getProductDetails` —— **操作名在查询串里**（与 PayPal 合作方族同形），
文档是 **mutation**、`$handle: String`（**可空**）。实现在 `Flows/ShopifyProductDrops.cs`。

同批的 `saveAddress`、`maintainShippingGroups` **既无主机也无路径**，与 `getCart` 同处不可归属清单。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
