"""R1339 record: two more steps, and the eight-sender map that made them findable."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1339 轮：一家店的**全部 HTTP 面**用一个字符串的引用列表就能枚举出来——并据此补了两个步骤

- **方法升级**：`https://tm-api-eu.highsnobiety.com/`（`0x147089690`）在 `.text` 里**只有 8 个引用点**，
  而这 8 个函数就是这家店的**全部发送方**。一次 `disp32_scan_any` 就把整店的 API 面列全了：
  ```
  0x140B56880  Add to cart        addLineItem            action/country/locale
  0x140B56CC0  Create payment     createCheckoutPayment  storefront/App
  0x140B57020  Find product       fetchProduct           slug/locale/preferredLocale/fallbackLocale/country
  0x140B574F0  Process order      fetchOrderConfirmation stripePaymentIntentId/locale/preferredLocale
  0x140B57EB0  Submit billing     (操作名在下一轮读)      action/additionalAddressInfo/address/city/country/firstName/lastName/phone…
  0x140B585B0  —                  addDiscountCode        code/locale
  0x140B58920  Submit email       setCustomerEmail       action/locale/preferredLocale
  0x140B59790  Submit shipping    (下一轮)               action/additionalAddressInfo/address/…
  ```
- **一个地址学的反转**：扫 `chars_va - 12`（对象头）得 **0 site**，扫 **`chars_va`** 得 **8 site**。
  §2.7d 说代码通常持对象头；**这家店的发送方持有的是字符地址**。**两种都要试，才能说"没有引用"。**
- **`action` 之谜解开了**：`setCustomerEmail` 的文档签名是 `$action: SetCartCustomerEmail!`，
  `addLineItem` 是 `$action: AddCartLineItem!` —— **`action` 是"每个操作各自的输入对象"**，
  不是共享枚举。所以每步各有自己的会话键（`highsnobiety.action` / `highsnobiety.emailAction`）。
- **落码**：`FindProductAsync`（`fetchProduct`，5718 字符文档，五个变量全填）与
  `SubmitEmailAsync`（`setCustomerEmail`，4986 字符文档）。两份文档都用**显式 `\\r\\n` 转义**存，
  不再受编辑器换行归一化影响。**整个类由脚本整块重生成**，不做切片补丁 —— 上一轮切片把文件从 2066 行砍到 235 行的教训。
- **产物正向证据**：`query fetchProduct`、`mutation setCustomerEmail` 各命中 UTF-16 **1**，
  `fallbackLocale` **16**、`preferredLocale` **18**。尺寸 61,480,448 → **61,526,016**。

### 五要素

- **改了什么**：`RetailFlows.cs`（`HighsnobietyFlow` 整块重生成：4 份文档 + 5 个步骤）；
  `HighsnobietyFlowTests.cs`（+4 条，共 11）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`HighsnobietyFlowTests` → **11/11**；`orphan_documents.py` → 0；
  `audit_document_constants.py` → **21 常量 / 0 问题**；产物四串 UTF-16 命中；尺寸与哈希见上；
  mutation → 59 fired / 0 decorative / 0 skipped / GREEN / staleness 0；扫描 49,525 文件 0 命中。
- **数字变化**：套件 2703 → 见 METRICS 当前值（+4）；产物 +45,568 字节。
- **证据等级**：Observation —— 8 个引用点、每个函数的操作名与变量、两份新文档的字节与签名、产物命中。
  Unknown —— `AddCartLineItem` / `SetCartCustomerEmail` / 账单/配送的 `action` 对象字段名（故由调用方给 JSON）。
- **还剩什么**：Highsnobiety 的 payment/billing/shipping/order 四步（发送方已定位，操作名待读全）；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1339 轮

- **一家店的全部 HTTP 面 = 一个主机字符串的引用列表**：`0x147089690` 有 **8 个引用点**，8 个函数就是整店 API。
- **地址学反转**：扫 `chars_va - 12` 得 0 site，扫 **`chars_va`** 得 8 site —— **这两种都要试**才能说没有引用。
- **`action` 是"每操作各自的输入对象"**（`AddCartLineItem` / `SetCartCustomerEmail`），不是共享枚举 ——
  所以每步一个会话键。
- 新增 `FindProductAsync`（`fetchProduct` 5718）与 `SubmitEmailAsync`（`setCustomerEmail` 4986），
  文档用显式 `\\r\\n` 转义、**整块重生成不做切片补丁**。
- 下一步：payment/billing/shipping/order 四个发送方**已定位**，读全操作名即可补齐。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1339 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1339 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'Highsnobiety 的八个发送方' not in text:
    text += """
## Highsnobiety 的八个发送方（R1339）

主机 `https://tm-api-eu.highsnobiety.com/` 在 `.text` 里只有 **8 个引用点**，8 个函数即整店 API 面。
**注意**：这些引用指向**字符地址** `0x147089690`，不是对象头 `-12`；扫对象头得 0 site。

| 函数 | 标签 | 操作名 | 变量 |
|---|---|---|---|
| `0x140B56880` | Add to cart | `addLineItem` | `action`、`country`、`locale` |
| `0x140B56CC0` | Create payment | `createCheckoutPayment` | `storefront`、`action`?（`App`） |
| `0x140B57020` | Find product | `fetchProduct` | `slug`、`locale`、`preferredLocale`、`fallbackLocale`、`country` |
| `0x140B574F0` | Process order | `fetchOrderConfirmation` | `stripePaymentIntentId`、`locale`、`preferredLocale` |
| `0x140B57EB0` | Submit billing | 待读 | `action`、`additionalAddressInfo`、`address`、`city`、`country`、`firstName`、`lastName`、`phone` |
| `0x140B585B0` | — | `addDiscountCode` | `code`、`locale` |
| `0x140B58920` | Submit email | `setCustomerEmail` | `action`、`locale`、`preferredLocale` |
| `0x140B59790` | Submit shipping | 待读 | 同 billing |

`fetchProduct` = **5718** 字符（`0x1471407C4`），`setCustomerEmail` = **4986**（`0x1470F8234`），
`addLineItem` = **3435**（`0x1470E6CDC`），`addDiscountCode` = **3399**（`0x1470E5234`）。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md got the sender table')
