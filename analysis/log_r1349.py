"""R1349 record: block A is a region, and the variable signature splits it three ways."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1349 轮：A 块**不是一个族**——变量签名把它劈成三份，其中一份根本不是 Shopify

- **上一轮把 A 块当成"一家人"，这轮读完五份文档就碎了**：
  ```
  cartApiObjectCreate      $input + 六个 include + country + metafieldsIdentifiers   Shopify Storefront
  createCart               $lines / $buyerIdentity / $attributes / $country / $language   Shopify Storefront
  removeLineItemFromCart   $cartId / $lineItemId / $version / $quantity / $locale    Shopify Storefront
  setBillingAddress        $action: SetCartBillingAddress! / $locale / $preferredLocale    Highsnobiety 那一族
  createCheckout           $variantId / $location / $attributes / $recaptchaToken    又是另一家
  ```
  **`setBillingAddress` 的签名和 Highsnobiety 的 `setCustomerEmail` 一模一样**（action 对象 + 两个 locale），
  而 `createCheckout` 带 recaptcha 令牌。**地址聚类只是把人带到块里，变量签名才是证据。**
- **落码**：`ShopifyStorefrontQueries`（三份 Storefront 文档 + `Declared`/`SenderFills` 两表 + `SendAsync`，
  未声明变量在发送前挡掉）；**`setBillingAddress` 归位到 `HighsnobietyFlow.SubmitBillingAsync`**（action 对象由调用方给）。
- **产物正向证据**：`mutation createCart`、`mutation removeLineItemFromCart`、`mutation setBillingAddress`
  **UTF-16 各命中 1**；尺寸 61,793,280 → **62,024,512**。

### 五要素

- **改了什么**：新增 `Flows/ShopifyStorefrontQueries.cs`、`tests/ShopifyStorefrontQueriesTests.cs`（6 条）；
  删除 `ShopifyCartCreate.cs` 与其测试；`ShopifyFlow.cs` 分支改指向；`RetailFlows.cs`（Highsnobiety 计费步）；
  新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopifyStorefrontQueriesTests|HighsnobietyFlowTests|ShopifyGraphQlTests` → **31/31**；
  `operation_gap.py` → 覆盖 **31/65**（缺 34）；`orphan_documents.py` → 0；`audit_document_constants.py` → **34 常量 / 0 问题**；
  产物三串各命中 1；尺寸见上。
- **数字变化**：覆盖 28 → **31**；缺 37 → **34**；套件 +2（净）；产物 +231,232 字节。
- **证据等级**：Observation —— 五份文档的声明集、两类签名的差异、产物三串命中。
  Unknown —— `createCheckout` 属于哪家（带 recaptcha，第三种签名）。
- **还剩什么**：A 块剩余（`getProductDetails`/`saveAddress`/… 归属待定）；B 块 7 个（无主机）；
  `approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；
  AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1349 轮

- **A 块不是一个族**：变量签名三分 —— Shopify Storefront（`cartApiObjectCreate`/`createCart`/`removeLineItemFromCart`）、
  **Highsnobiety 那一族（`setBillingAddress`，签名与 `setCustomerEmail` 同形）**、第三种（`createCheckout` 带 recaptcha）。
  **地址聚类只带路，变量签名才是证据。**
- `ShopifyStorefrontQueries`（3 份文档 + 两表 + `SendAsync`，未声明变量发送前挡掉）；
  `setBillingAddress` 归位到 `HighsnobietyFlow.SubmitBillingAsync`。
- 覆盖 28 → **31/65**，缺 37 → **34**；产物三串各 UTF-16 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1349 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1349 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'ShopifyStorefrontQueries' not in text:
    text += """
## A 块的三分（R1349）

| 文档 | 声明集 | 归属 |
|---|---|---|
| `cartApiObjectCreate`(5876) | `$input` + 六个 include + `country` + `metafieldsIdentifiers` | **Shopify Storefront** |
| `createCart`(1622) | `$lines`/`$buyerIdentity`/`$attributes`/`$country`/`$language` | **Shopify Storefront** |
| `removeLineItemFromCart`(1553) | `$cartId`/`$lineItemId`/`$version`/`$quantity`/`$locale` | **Shopify Storefront** |
| `setBillingAddress`(4989) | `$action: SetCartBillingAddress!`/`$locale`/`$preferredLocale` | **Highsnobiety 那一族** |
| `createCheckout`(720) | `$variantId`/`$location`/`$attributes`/`$recaptchaToken` | 未定（第三种签名） |

**地址聚类只是线索；变量签名才是证据。**
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
