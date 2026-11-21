"""R1345 record: the five-sender storefront family, and the Product query landed through a caller-supplied origin."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1345 轮：`Product`(10620) 落地，并且发现它是一组**五个发送方共用一个相对路径**的家族

- **追发送方**：`0x147127B44` → `0x140E1BBFC` → `sub_140E1BAB0`（1076 字节），操作名 `Product`、变量 `id`/`variationId`、
  路径 **`api/graphql`（相对路径）**。
  **那段内联常量骗了我一次**：`0x145E99C50` 读出来是 `api/grap` —— 不是主机，而是**逐字符拼路径**时的一截。
- **看邻居，发现整族**：
  ```
  0x140E1B1D0  Add to cart       AddItemToCart      id / input / productId
  0x140E1B700  —                 CreateInitialCart
  0x140E1BAB0  Find product      Product            id / variationId
  0x140E1BF40  Generate checkout CheckoutCart       id
  0x140E1C390  Get session       （只有 query/variables）
  ```
  **五个操作、一个相对路径、没有一个带主机** —— 与 `/cartApi/checkout` 同形：**主机在发送方之外**。
  其中三个名字（`AddItemToCart`/`CreateInitialCart`/`CheckoutCart`）本来就在 R1341 的缺席清单里。
- **落码**：`StorefrontApiProduct`（OperationName/Path/Document 10620/`DeclaredVariables` 四个/`SenderVariables` 两个/Envelope/FetchAsync）。
  **`origin` 是参数不是常量** —— 相对路径配一个编出来的主机，就是把真实请求发到真实服务器上去。
  文档声明四个变量（`id`/`isDraft`/`variationId`/`src`），**发送方只填两个**；另外两个是可选，
  **本类不替它们编值**（draft 与 src 覆盖会改变查询结果）。
- **接上调用者**：`ShopifyFlow.FindProductAsync` 第三分支（`storefrontapi.origin` 触发）。缺 origin 就照旧走门店查询。
- **产物**：`query Product(` UTF-16 命中 **1**、`storefrontapi` 命中 **3**；尺寸 61,676,032 → **61,714,944**。

### 五要素

- **改了什么**：新增 `Flows/StorefrontApiProduct.cs`、`tests/StorefrontApiProductTests.cs`（6 条）；
  `ShopifyFlow.cs`（第三分支）；新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StorefrontApiProductTests|ShopifyGraphQlTests` → **18/18**；
  `operation_gap.py` → 覆盖 **23/65**（缺 42）；`orphan_documents.py` → 0；`audit_document_constants.py` → **26 常量 / 0 问题**；
  产物两串 UTF-16 命中 1/3；尺寸 61,676,032 → 61,714,944。
- **数字变化**：覆盖 22 → **23**；缺 43 → **42**；套件 +6；产物 +38,912 字节。
- **证据等级**：Observation —— 五个发送方、操作名、变量、相对路径、内联常量的真实内容、产物命中。
  Unknown —— 这族属于**哪家店**（发送方都不带主机）。
- **还剩什么**：该族其余四个操作（发送方已定位）；42 个未覆盖操作；`approveMemberPayment` 两方言；
  浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1345 轮

- **`Product`(10620) 落地**，并且发现它属于**一组五发送方、共用相对路径 `api/graphql`、都不带主机**的家族
  （`AddItemToCart` / `CreateInitialCart` / `Product` / `CheckoutCart` / session）。
  **内联常量 `0x145E99C50` 读出来是 `api/grap`** —— 是逐字符拼路径的一截，不是主机（差点被它骗）。
- `StorefrontApiProduct`：**origin 是参数不是常量**（相对路径配编造的主机会打到真实服务器）；
  文档声明 4 个变量、发送方只填 2 个，**另两个不替它编值**。
- 接进 `ShopifyFlow.FindProductAsync` 第三分支（`storefrontapi.origin`）。
- 覆盖 22 → **23/65**，缺 43 → **42**；产物 `query Product(` 命中 1、`storefrontapi` 命中 3。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1345 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1345 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'StorefrontApiProduct' not in text:
    text = text.replace(
        "`Product`(10620)、",
        "**`Product`(10620) 已落地（R1345）：`StorefrontApiProduct`，与 `AddItemToCart`/`CreateInitialCart`/`CheckoutCart` "
        "同族，共用相对路径 `api/graphql`，**都不带主机**（origin 由调用方给）**、")
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
