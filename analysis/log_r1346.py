"""R1346 record: the whole api/graphql family in one class, and the rule it enforces."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1346 轮：`api/graphql` 那一族的**五个操作一次做完**——并且发现"发送方填的变量"与"文档声明的变量"不是同一组

- **一次取四份**：`AddItemToCart`(2108)、`CreateInitialCart`(865)、`CheckoutCart`(4102)、`getSession`(133)，
  加上 R1345 的 `Product`(10620) —— 五份文档、一个相对路径、一个类（`StorefrontApiQueries`）。
  `StorefrontApiProduct` **已并入并删除**（一个族一个类，五个类就是五处要维护同一条 origin 规则）。
- **关键发现：两组变量不一致**：

  | 操作 | 文档声明 | 发送方填 |
  |---|---|---|
  | AddItemToCart | `$input` | `id`、`input`、`productId` |
  | CreateInitialCart | 无 | 无 |
  | Product | `id`、`isDraft`、`variationId`、`src` | `id`、`variationId` |
  | CheckoutCart | `$id` | `id` |
  | getSession | 无 | 无 |

  **文档赢**：文档没声明的变量**不能传**（服务端会拒），文档声明而发送方没填的是**可选**。
  于是类里**同时公开两组**，并在发送前**挡掉未声明的变量** —— 不等服务端返回一个没人预期的 GraphQL 错误。
- **一条测试按新规则重写**：原来"缺 id 就拒"的用例**前提已经不成立**（通用 `SendAsync` 不该替每个操作校验 id），
  换成**"传了未声明的变量就拒"** —— 那是这个族真正强制的规则。
- **产物正向证据**：五份文档首行在产物里 **UTF-16 各命中 1**；尺寸 61,714,944 → **61,739,520**。

### 五要素

- **改了什么**：新增 `Flows/StorefrontApiQueries.cs`（五份文档 + 声明/填充两组表 + `SendAsync`）；
  删除 `StorefrontApiProduct.cs`；`ShopifyFlow.cs` 分支改指向族；`StorefrontApiProductTests.cs` 迁移并重写（6 条）；
  新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StorefrontApi*` → **6/6**；`ShopifyGraphQlTests` → **12/12**；
  `operation_gap.py` → 覆盖 **26/65**（缺 39）；`orphan_documents.py` → 0；`audit_document_constants.py` → **29 常量 / 0 问题**；
  产物五串各命中 1；尺寸 61,714,944 → 61,739,520。
- **数字变化**：覆盖 23 → **26**；缺 42 → **39**；产物 +24,576 字节。
- **证据等级**：Observation —— 五份文档的字节与声明集、五组发送方变量、产物命中。
  Unknown —— 这族属于哪家店（发送方都不带主机）。
- **还剩什么**：39 个未覆盖操作；`approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；
  `AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1346 轮

- **`api/graphql` 族五个操作一次做完**（AddItemToCart 2108 / CreateInitialCart 865 / Product 10620 /
  CheckoutCart 4102 / getSession 133），一个类 `StorefrontApiQueries`；`StorefrontApiProduct` 已并入删除。
- **两组变量不一致**：文档声明的 ≠ 发送方填的（见 R1346 表）。**文档赢** —— 未声明的变量**发送前就挡掉**，
  声明了而没填的是可选。类里同时公开 `Declared` 与 `SenderFills`。
- 覆盖 23 → **26/65**，缺 42 → **39**；产物五份文档首行 UTF-16 各命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1346 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1346 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'StorefrontApiQueries' not in text:
    text += """
## `api/graphql` 族（R1345–R1346）：五份文档，一个相对路径，无主机

| 操作 | 长度 | 地址 | 文档声明 | 发送方填 |
|---|---|---|---|---|
| `AddItemToCart` | 2108 | 0x1470CB3F4 | `$input` | `id`、`input`、`productId` |
| `CreateInitialCart` | 865 | 0x1470CF25C | 无 | 无 |
| `Product` | 10620 | 0x147127B44 | `id`、`isDraft`、`variationId`、`src` | `id`、`variationId` |
| `CheckoutCart` | 4102 | 0x14711CF9C | `$id` | `id` |
| `getSession` | 133 | 0x147146994 | 无 | 无 |

五个发送方（`0x140E1B1D0` / `0x140E1B700` / `0x140E1BAB0` / `0x140E1BF40` / `0x140E1C390`）**都不带主机**，
都拼相对路径 `api/graphql`。**origin 必须由调用方给** —— 相对路径配一个编出来的主机就是把真实请求发到真实服务器。
实现见 `Flows/StorefrontApiQueries.cs`。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md got the family table')
