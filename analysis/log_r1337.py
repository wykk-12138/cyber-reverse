"""Write up R1337: what goes where, and the retraction it forced."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1337 轮：读三个发送方，把"发到哪"一次问清——并**撤回 R1334**

- **同一条链第四次用**（文档 → 单引用点 → 读发送方），这次一次查五份：

  | 文档 | 发送方读出的目标 |
  |---|---|
  | `SubmitOrder`(141) | `https://` + host + **`/graphql`**，`operationName`/`query`/`variables`/`cartToken` |
  | `addLineItem`(3847) | **`https://tm-api-eu.highsnobiety.com/`**，`sku`/`locale`/`country`/`action='Add to cart'` |
  | `addDiscountCode`(3811) | **同一个 Highsnobiety 主机**，`code`/`locale` |
  | `cartApiObjectCreate`(5876) | **Shopify Storefront**：`api/2025-04/graphql.json`、`gid://shopify/ProductVariant/`、`customerAccessToken`、`include*` 五个标志 |
  | `createEmptyCart`(32) | **没有任何 URL 字面量** —— 端点是调用方传的 |

- **结论一：R1320/R1321 的 `/graphql` 推断是对的**（`SubmitOrder` 的发送方亲自拼了 `/graphql`），存疑解除。
- **结论二：R1334 是错的，本轮撤回。** `/cartApi/checkout` 的发送方用的是 `cartType`/`lineItems`/`locationId`/`sourceSystem`
  取值 `Retail`/`Shopify` —— **Magento 购物车那五个变更没有任何一个发这些**。两族不是一回事。
  把 `CartApiEndpointFor` 挂在 `MagentoCart` 的六个入口上，等于**给不吃这条路径的文档换了一条路径**。
- **撤干净**：删掉 `CartApiPath`/`CartApiEndpointFor`/`ThemeApisHost`/`ResolveEndpoint` 四个成员、
  六处归一化、五条测试。**一条"对别的东西成立"的规则比没有规则更坏 —— 它看起来像证据**，
  而且第一次有人传裸主机时就会把端点导向错的地方。
- **结论三：Highsnobiety 是一家真实存在的店**（`tm-api-eu.highsnobiety.com`），复刻件里**没有**它。
  这两份文档（`addLineItem`/`addDiscountCode`）的归宿是那家店，不是泛指。

### 五要素

- **改了什么**：`MagentoCart.cs`（删 4 成员 + 6 处调用）；`MagentoCartTests.cs`（删 5 条）；
  `docs/GRAPHQL_DOCUMENTS.md`（逐条写上真实去向）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter MagentoCartTests` → **20/20**（由 25 减 5，删的就是 R1334 那五条）；
  `grep` 四处残留计数全 **0**；`disp32_scan_any` 五份文档各 **1 site**（`cartApiObjectCreate` 2）。
- **数字变化**：套件 2701 → 见 METRICS 当前值（−5）；产物重发布。
- **证据等级**：Observation —— 五个发送方的 URL/操作名/变量名；`/cartApi/checkout` 的变量名与取值。
  **本轮推翻的是我自己上一轮的 Inference。**
- **还剩什么**：Highsnobiety 这家店（两份文档的归宿）；`/cartApi/checkout` 究竟属于谁；
  `AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1337 轮

- **一次查清五份文档发到哪**：`SubmitOrder` → `<host>/graphql`（**R1320/R1321 推断正确，解除存疑**）；
  `addLineItem`/`addDiscountCode` → **`https://tm-api-eu.highsnobiety.com/`**（一家复刻件里还没有的店）；
  `cartApiObjectCreate` → **Shopify Storefront** `api/2025-04/graphql.json`；
  `createEmptyCart` → 无 URL 字面量，端点由调用方传。
- **撤回 R1334**：`/cartApi/checkout` 的变量是 `cartType`/`lineItems`/`locationId`/`sourceSystem`，
  **Magento 购物车变更没有一个发这些**。已删 4 成员 + 6 处调用 + 5 条测试。
  **一条"对别的东西成立"的规则比没有规则更坏 —— 它看起来像证据。**
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1337 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1337 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'tm-api-eu.highsnobiety.com' not in text:
    text += """
## 五份文档的真实去向（R1337，读发送方所得）

| 文档 | 发送方拼出的目标 | 关键变量 |
|---|---|---|
| `SubmitOrder`(141) | `https://` + host + `/graphql` | `cartToken`、`operationName`、`query`、`variables` |
| `addLineItem`(3847) | `https://tm-api-eu.highsnobiety.com/` | `sku`、`locale`、`country`、`action`（`Add to cart`） |
| `addDiscountCode`(3811) | `https://tm-api-eu.highsnobiety.com/` | `code`、`locale` |
| `cartApiObjectCreate`(5876) | Shopify Storefront `api/2025-04/graphql.json` | `gid://shopify/ProductVariant/`、`customerAccessToken`、`include*` |
| `createEmptyCart`(32) | 无 URL 字面量 —— 端点由调用方传 | — |

**`/cartApi/checkout` 不在这张表里。** 它的发送方用的是 `cartType`/`lineItems`/`locationId`/`sourceSystem`
（取值 `Retail`/`Shopify`），与上表任何一份都不重合 —— 所以 R1334 把那条路径挂到 `MagentoCart` 上是错的，已撤回。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md got the destination table')
