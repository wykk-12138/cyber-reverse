"""R1362 record: two more family members, each placed by its handler's variables."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1362 轮：两份各归各族 —— **靠处理器的变量判断，不靠地址**

- **`UpdateCustomerForCart`(382)** → 处理器 `sub_140E1D030` 带 **`api/graphql`** + `basketId`/`email`/`input`
  → 并入 **`StorefrontApiQueries`**（该族第六份）。
- **`addToCartByChannel`(2271)** → 处理器 `sub_140E53A10` 带 `cartId`/`key`/`locale`/`productId`/`quantity`/
  `country`/`address` 且**无主机** → 并入 **`StoreSessionQueries`**（`key`/`locale` 与 `getCart` 同签名，同 0x140E5xxxx 块）。
- **文档声明的变量 ≠ 发送方命名的字段**（又一次）：
  `addToCartByChannel` 文档只声明 `$cartId`/`$locale`/`$productId`/`$quantity`/`$version` 五个，
  而发送方还提到 `key`/`country`/`address` —— **以文档为准**，多出来的字段说明发送方在别处用它们。
- **一处脚本失误**：`StoreSessionQueries` 只有**一张** `Declared` 表（不是两张），我的插入逻辑按两张写，
  报"找到 1 次"。改成 **1 或 2 都支持**后通过。
- **产物**：`mutation UpdateCustomerForCart` 与 `mutation addToCartByChannel` **UTF-16 各命中 1**；
  尺寸 61,979,136 → **61,987,328**。

### 五要素

- **改了什么**：`StorefrontApiQueries.cs`（+1 文档/声明/分支）、`StoreSessionQueries.cs`（+1 文档/声明/分支）；
  两份测试各 +2（共 10 / 8）；新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StoreSessionQueriesTests|StorefrontApi*` → **18/18**；
  `operation_gap.py` → 覆盖 **52/65**（缺 13）；`orphan_documents.py` → 0；产物两串各命中 1；尺寸见上。
- **数字变化**：覆盖 50 → **52**；缺 15 → **13**；套件 +4；产物 +8,192 字节。
- **证据等级**：Observation —— 两个处理器的路径与字段集、两份文档的长度与声明集、产物两串命中。
- **还剩什么**：13 个 —— `UpdateContactDetails`(244)/`SignInAsGuest`(453)（同窝未探）；
  `updateShipAddress`(140)（0x14088 块，疑属哈希族）；`updateMyPaymentWithActions`(401)；
  `CreditCard`(2867)/`getShippingMethods`(531)（无操作名串）；
  五份无主机；两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；AO 三个体；Saucony 六步。
"""

POINTER = """
---

## 第 1362 轮

- `UpdateCustomerForCart`(382) → **`StorefrontApiQueries`**（处理器带 `api/graphql`）；
  `addToCartByChannel`(2271) → **`StoreSessionQueries`**（处理器带 `key`/`locale`、无主机）。
- **又一次"文档声明 ≠ 发送方字段"**：`addToCartByChannel` 文档五个变量，发送方多提 `key`/`country`/`address`
  —— **以文档为准**。
- 脚本失误一处：`StoreSessionQueries` 只有**一张** `Declared` 表，插入逻辑按两张写 → 改成 1/2 都支持。
- 覆盖 50 → **52/65**，缺 15 → **13**；产物两串各 UTF-16 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1362 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1362 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'addToCartByChannel' not in text:
    text += """
## 归属靠处理器变量（R1362）

| 操作 | 长度 | 处理器特征 | 归入 |
|---|---|---|---|
| `UpdateCustomerForCart` | 382 | `api/graphql` + `basketId`/`email`/`input` | `StorefrontApiQueries`（第六份） |
| `addToCartByChannel` | 2271 | `key`/`locale`/`cartId`/`productId`/`quantity`，无主机 | `StoreSessionQueries` |

`addToCartByChannel` 文档声明 `$cartId`/`$locale`/`$productId`/`$quantity`/`$version` 五个，
发送方另提 `key`/`country`/`address` —— **以文档为准**。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
