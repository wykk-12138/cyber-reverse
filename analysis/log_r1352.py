"""R1352 record: four of the last seven placeable, and the storefront turns out to use two API versions."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1352 轮：A 块剩下七份一次扫完——**四份可归属，而且 Storefront 用了两个 API 版本**

- **七份一次扫**（脚本 `scan_block_a_paths.py`，每份走"引用点 → 函数 → 字面量"）：
  ```
  cartCreate                 api/2021-10/graphql.json                               host
  customerAccessTokenCreate  api/2025-04/graphql.json                               host
  createCheckout             apps/product-drops?kind=mutation&operation=createCheckout  path
  checkoutAsGuest            https://www.on.com/ko-kr/graphql                       host（On Running，ko-kr）
  createCartByStore          无主机无路径
  createMyPayment            无主机无路径
  initiateCheckout           无主机无路径
  ```
  **host 3 / path 1 / neither 3。**
- **两条实质发现**：
  1. **Storefront 不是只有一个版本** —— `cartCreate` 钉 **2021-10**，另两个钉 **2025-04**。
     所以**版本随操作走，不随类走**；`SendAsync` 改成未指定版本时按操作取默认（`cartCreate` → 2021-10）。
  2. **`checkoutAsGuest` 是本块第一个直接写出店铺主机的发送方**：`https://www.on.com/ko-kr/graphql`
     —— **On Running 的韩语店面**。只记事实，**没有把它塞进某个已有流程**（On Running 在复刻件里不是流程）。
- **落码**：`ShopifyStorefrontQueries` 增 `cartCreate`(91) 与 `customerAccessTokenCreate`(250)；
  `ShopifyProductDrops` 增 `createCheckout`(720) 与 `CreateCheckoutAsync`。
- **两处自我纠正**：
  - 写了个会**真发 DNS** 的测试（`shop.test` 跑了 22 秒后失败）→ 改成**只验拼出来的端点**，不发包。
  - 探针 `/api/2021-10/graphql.json` 命中 0 —— **那是运行时拼的，源码里没有这个字面量**（探针本身错了）。
    改查版本串：`2021-10` 与 `2025-04` **ascii 各命中 1、utf16 各 0**（§4.5：存储混合，缺席无信息量）。

### 五要素

- **改了什么**：`ShopifyStorefrontQueries.cs`（+2 操作、版本规则）、`ShopifyProductDrops.cs`（+checkout）；
  两份测试文件（共 10 + 8 条）；新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopifyStorefrontQueriesTests|ShopifyProductDropsTests` → **18/18**；
  `operation_gap.py` → 覆盖 **36/65**（缺 29）；`orphan_documents.py` → 0；`audit_document_constants.py` → **38 常量 / 0 问题**；
  产物 `mutation cartCreate` 1、`mutation customerAccessTokenCreate` 1、`mutation createCheckout` 2；
  版本串 ascii 各 1；尺寸 62,038,528 → **62,046,016**。
- **数字变化**：覆盖 33 → **36**；缺 32 → **29**；产物 +7,488 字节。
- **证据等级**：Observation —— 七个发送方的 host/path 分类、两个 API 版本、On Running 主机、文档四个长度、产物命中。
- **还剩什么**：不可归属 6 个（`createCartByStore`/`createMyPayment`/`initiateCheckout`/`saveAddress`/
  `maintainShippingGroups`/`getCart`）；**`checkoutAsGuest` 已定位但未落码**（On Running 非流程）；
  B 块其余；`approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；
  方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1352 轮

- A 块最后七份一次扫完：**host 3 / path 1 / neither 3**。落地 `cartCreate`(91)、`customerAccessTokenCreate`(250)、
  `createCheckout`(720)。
- **Storefront 不是单一版本**：`cartCreate` 钉 **2021-10**、其余 **2025-04** → **版本随操作走**，`SendAsync` 按操作取默认。
- **`checkoutAsGuest` 写出店铺主机 `https://www.on.com/ko-kr/graphql`**（On Running 韩语店面）——
  只记事实，**On Running 在复刻件里不是流程，所以未落码**。
- 自我纠正两处：测试曾真发 DNS（22 秒）；探针查"拼出来的端点"命中 0（源码里没有那个字面量，改查版本串）。
- 覆盖 33 → **36/65**，缺 32 → **29**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1352 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1352 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'storefront 的两个 API 版本' not in text:
    text += """
## storefront 的两个 API 版本（R1352）

| 操作 | 版本 | 地址 |
|---|---|---|
| `cartCreate`(91) | **2021-10** | 0x1470F23FC |
| `customerAccessTokenCreate`(250) | 2025-04 | 0x1470F41B4 |
| `cartApiObjectCreate` / `createCart` / `removeLineItemFromCart` | 2025-04 | — |

**版本随操作走，不随类走。**

另外：`checkoutAsGuest`(148) 的发送方直接写出 **`https://www.on.com/ko-kr/graphql`**（On Running 韩语店面），
`createCheckout`(720) 走 `apps/product-drops?kind=mutation&operation=createCheckout`。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
