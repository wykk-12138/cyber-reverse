"""R1341 record: the sixty-five-operation inventory, a dialect pair, and the order step."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1341 轮：把"镜像里到底有多少 GraphQL 操作"这件事**数清楚**——65 个，复刻件有 18 个

- **先否掉一个会骗人的数法**：`ida.py str "mutation "` 只报 **7** 个操作，而复刻件自己就有 20 个 ——
  **它扫的不是文档池**（长串不在它所谓的"字符串"里）。用这个数做集合差，会得出一个自信而错误的清单。
  这正是 §2.7b 的坑：**抽样支撑不了集合差。**
- **改成走区域**：文档都在 `0x1470C0000..0x147150000`，按 4 字节步长找冻结串头（`MT=0x144DB6A40` + 长度），
  读出全部以 `mutation `/`query ` 开头的对象 —— **65 个操作**，逐个带地址与长度。
  **一个 64 KiB 的 `get_bytes` 会被省略号截断，必须 8 KiB 分块**（又一次）。
- **两个发现**：
  1. **`approveMemberPayment` 有两份**：`0x1470E9FA4` **5407** 字符（R1335 已落地）与 `0x1470EC9FC` **5620** 字符。
     又一对**方言**，和 3DS 那对同形。**哪份在哪用还没确定 —— 本轮只记录，不猜。**
  2. **复刻件覆盖 18/65，缺 47 个**，缺的总量约 10 万字符。清单按长度排序，最长的是
     `ProductDetails`(26206)、`PayWithQuery`(12561)、`Product`(10620)、`ShopProductSearch`(6537)。
- **落码**：缺的里面**发送方已经定位**的是 Highsnobiety 的 `fetchOrderConfirmation`（`0x14713E1FC`，4825 字符，
  发送方 `0x140B574F0`，变量 `stripePaymentIntentId`/`locale`/`preferredLocale`）——
  接成 `HighsnobietyFlow.SubmitOrderAsync`。覆盖数 **18 → 19**，缺 **47 → 46**。

### 五要素

- **改了什么**：`RetailFlows.cs`（`FetchOrderConfirmationDocument` + `SubmitOrderAsync` + 操作名常量）；
  `HighsnobietyFlowTests.cs`（+2 条，共 13）；新增 `analysis/document_region_scan.py`、`operation_inventory.py`、
  `operation_gap.py`、`add_order_step.py`、`add_order_tests.py`；重发布；METRICS 重生成。
- **验证命令与输出**：`HighsnobietyFlowTests` → **13/13**；`operation_gap.py` → 镜像 65 / 复刻 21 / 覆盖 19 / 缺 46；
  `orphan_documents.py` → 0；`audit_document_constants.py` → **22 常量 / 0 问题**；
  产物 `fetchOrderConfirmation` UTF-16 **2**、`stripePaymentIntentId` **4**；尺寸 61,526,016 → **61,544,960**。
- **数字变化**：覆盖 18 → **19**；缺 47 → **46**；套件 +2；产物 +18,944 字节。
- **证据等级**：Observation —— 65 个操作的地址与长度、两份 `approveMemberPayment` 的长度、49 个未覆盖名字。
  Unknown —— 两份方言的选用条件；46 个未覆盖操作各自的发送方。
- **还剩什么**：46 个未覆盖操作（清单已按长度排好，**逐轮取最大的那个**）；两份方言的选用条件；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1341 轮

- **`ida.py str` 只报 7 个操作，实际 65 个** —— 它扫的不是文档池，**抽样支撑不了集合差**。
  改为走区域 `0x1470C0000..0x147150000`（4 字节步长找冻结串头），**65 个操作**全列出来了
  （`analysis/.operations_in_image.json`）。64 KiB 的 `get_bytes` 会被省略号截断，**必须 8 KiB 分块**。
- **`approveMemberPayment` 有两份**：5407（R1335 已用）与 **5620**（`0x1470EC9FC`）。方言对，**选用条件未定**。
- **覆盖 18/65 → 19/65**：把 Highsnobiety 的 `fetchOrderConfirmation`(4825) 接成 `SubmitOrderAsync`。
  **缺 46 个**，按长度排序在 `operation_gap.py` 里，逐轮取最大。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1341 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1341 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'operation inventory' not in text:
    text += """
## 操作清单（R1341）：镜像 65 个，复刻件覆盖 19 个

**数法**：走区域 `0x1470C0000..0x147150000`，4 字节步长找冻结串头（`MT=0x144DB6A40` + 长度），
读出所有以 `mutation `/`query ` 开头的对象。结果存 `analysis/.operations_in_image.json`。
**不要用 `ida.py str "mutation "`** —— 它只报 7 个，长的文档不在它的"字符串"集合里。

**方言对**：`approveMemberPayment` 在 `0x1470E9FA4`（5407，R1335 已用）与 `0x1470EC9FC`（5620）各有一份，
**选用条件未定**。

**待取清单**（`python analysis/operation_gap.py` 输出全表，按长度降序）：
`ProductDetails`(26206)、`PayWithQuery`(12561)、`Product`(10620)、`ShopProductSearch`(6537)、
`cartApiObjectCreate`(5876)、`setShippingAddress`(4992)、`setBillingAddress`(4989)、`CheckoutCart`(4102)、
`GetCart`(3520)、`getCart`(3234)、`getPaymentdMethods`(3067)、`CreditCard`(2867)、`UpdateShippingAddress`(2386) …
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md got the inventory section')
