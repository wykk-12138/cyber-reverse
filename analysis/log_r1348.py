"""R1348 record: block A is the Shopify Storefront API, and the credential in the image stays out."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1348 轮：A 块认出来了——**Shopify Storefront API**；顺带发现镜像里写死了一个 **storefront 访问令牌**

- **一块一个发送方，就够定归属**：
  - **A 块** `sub_140D1B380`（2258 字节）：`api/2025-04/graphql.json`、`buyerIdentity`、`customerAccessToken`、
    `gid://shopify/ProductVariant/`、五个 `include*` —— **这就是 Shopify Storefront**，
    而复刻件的 `ShopifyGraphQl.Endpoint` **本来就拼这条路径**，所以 A 块 15 个操作该并入现有 storefront 机制，不需要另起一类。
  - **B 块** `sub_140E55F90`（960 字节）：**没有任何主机**，只有 `getCart`/`key`/`locale` —— 与 `api/graphql` 族同形，仍未定归属。
- **A 块最大那份落地**：`cartApiObjectCreate`（**5876** 字符，`$input` + 七个标志 + `metafieldsIdentifiers`）。
  发送方填 7 个，**`metafieldsIdentifiers` 声明但没填** → 留给调用方。
  新增 `ShopifyCartCreate`（Document/DeclaredVariables/SenderVariables/Envelope/CreateAsync），
  接进 `ShopifyFlow.AddToCartAsync`（`shopify.cartCreateHost` + token + input 三者齐全才走）。
- **一条不肯照抄的发现**：发送方里**写死了一个 Storefront 访问令牌** `e927ea99…`。
  **凭证抄进源码就是会泄漏的凭证** —— 所以令牌由调用方给，源码里没有它。
  产物核对：`mutation cartApiObjectCreate` **UTF-16 命中 1**；那串令牌 **两种编码都 0**。
- **产物**：尺寸 61,766,144 → **61,793,280**。

### 五要素

- **改了什么**：新增 `Flows/ShopifyCartCreate.cs`、`tests/ShopifyCartCreateTests.cs`（4 条）；
  `ShopifyFlow.cs`（AddToCart 分支）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopifyCartCreateTests|ShopifyGraphQlTests|StorefrontApi*` → **22/22**；
  `operation_gap.py` → 覆盖 **28/65**（缺 37）；`orphan_documents.py` → 0；`audit_document_constants.py` → **31 常量 / 0 问题**；
  产物命中 1，令牌两编码皆 0；尺寸见上。
- **数字变化**：覆盖 27 → **28**；缺 38 → **37**；套件 +4；产物 +27,136 字节。
- **证据等级**：Observation —— A/B 两个发送方的主机差异、文档 5876 字符与八个变量、产物命中与令牌缺席。
- **还剩什么**：A 块其余 14 个（现已知道并入 storefront）；B 块 7 个（无主机）；`approveMemberPayment` 两方言；
  浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1348 轮

- **A 块 = Shopify Storefront API**（`api/2025-04/graphql.json` + `buyerIdentity` + 五个 `include*`），
  复刻件已有 `ShopifyGraphQl.Endpoint` 拼同一路径 → 该并入现有机制。**B 块仍无主机。**
- A 块最大那份 `cartApiObjectCreate`(5876) 落地：`ShopifyCartCreate`，接进 `ShopifyFlow.AddToCartAsync`。
- **镜像里写死了一个 storefront 访问令牌 `e927ea99…`；没有抄进源码**（凭证抄进源码就是会泄漏的凭证）。
  产物核对：文档命中 1，令牌两编码皆 0。
- 覆盖 27 → **28/65**，缺 38 → **37**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1348 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1348 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'ShopifyCartCreate' not in text:
    text += """
## A 块 = Shopify Storefront（R1348）

发送方 `sub_140D1B380`（2258 字节）带 `api/2025-04/graphql.json`、`buyerIdentity`、`customerAccessToken`、
`gid://shopify/ProductVariant/` 与五个 `include*` 标志 —— 与复刻件 `ShopifyGraphQl.Endpoint` 拼的路径相同。

**该发送方里写死了一个 storefront 访问令牌**（`e927ea99…`）。**没有抄进源码**：令牌由调用方提供。

已落地：`cartApiObjectCreate`(5876) → `Flows/ShopifyCartCreate.cs`。
A 块其余 14 个操作（`createCart`、`setBillingAddress`、`removeLineItemFromCart` …）**同属这一族**，待接。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
