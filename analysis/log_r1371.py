"""R1371 record: Cybersource's request shape implemented, its host left with the caller."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1371 轮：`createMyPayment` 的**请求形状**全部可得 —— 缺的只是主机，而主机本就不该由镜像给

- **两个处理器**（`name_then_handler.py createMyPayment`）：
  - `sub_140E55A00`（请求侧）：把 `customFields` 用 **`isv_payment_data`/`isv_store`/`isv_screenHeight`/
    `isv_screenWidth`/`isv_customerIpAddress`** 拼出来，`centAmount`/`currencyCode` 在旁边，
    并命名 **`cybersource`** 与 **`creditCardWithPayerAuthentication`**，拒绝语 **`No capture context`**；
  - `sub_140E51E20`（应答侧）：从 `data` 里读 **`isv_tokenCaptureContextSignature`**，错误语
    **`Error processing payment`**。
- **两个都没有主机** —— 所以端点是商家的、由调用方给；**能实现的是请求本身**，这正是这一轮做的：
  文档 + 五个自定义字段名 + 两条拒绝语 + 应答键 + `BuildCustomFields`（**空值丢弃**：
  供应商对"存在但为空"与"不存在"的读法不同）。
- **接线进 `StoreFlow.GetPaymentTokenAsync`** —— R1370 的教训：**不接线会被 AOT 裁掉**。
- **产物**：`mutation createMyPayment` UTF-16 命中 **1**、`createMyPayment` 命中 **2**；
  尺寸 62,028,800 → **62,037,504**。（`isv_payment_data`/`No capture context`/`creditCardWithPayerAuthentication`
  两编码皆 0 —— 按 §4.5 无结论，且**尺寸增长证明代码确实在里面**。）

### 五要素

- **改了什么**：新增 `Payments/CybersourcePayment.cs`、`tests/CybersourcePaymentTests.cs`（3 条）；
  `StoreFlow.GetPaymentTokenAsync` 加分支；新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`CybersourcePaymentTests` → **3/3**；`StoreFlow|Payment` → **99/99**；
  `operation_gap.py` → 覆盖 **61/65**（缺 4）；`orphan_documents.py` → 0；产物命中见上。
- **数字变化**：覆盖 60 → **61**；缺 5 → **4**；套件 +3；产物 +8,704 字节。
- **证据等级**：Observation —— 两处理器的字段词表与两条拒绝语、应答键、文档 493 字符、产物命中、尺寸增长。
- **还剩什么**：4 条 —— `AddressInput` 形状、AO 三个体、Saucony 六步、`/cartApi/checkout` 发送方、
  浏览器侧结账面（均需外部证据）。
"""

POINTER = """
---

## 第 1371 轮

- **`createMyPayment`(493) 落地**：处理器给出完整请求形状（五个 `isv_*` 自定义字段、`cybersource`、
  `creditCardWithPayerAuthentication`、`No capture context`、`Error processing payment`、
  `isv_tokenCaptureContextSignature`）→ `Payments/CybersourcePayment`，接进 `GetPaymentTokenAsync`。
- **主机仍由调用方给** —— 两个处理器都没命名主机，端点属商家自己。
- 覆盖 60 → **61/65**，缺 5 → **4**；产物 `mutation createMyPayment` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1371 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1371 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'CybersourcePayment' not in text:
    text += """
---

## 十一、`createMyPayment` 已结案（R1371）

不是"缺主机所以做不了"：**请求形状完全可得**，缺的只是商家端点（本就不该由镜像给）。

| 要素 | 值 |
|---|---|
| 自定义字段 | `isv_payment_data`、`isv_store`、`isv_screenHeight`、`isv_screenWidth`、`isv_customerIpAddress` |
| 供应商/方法 | `cybersource`、`creditCardWithPayerAuthentication` |
| 拒绝语 | `No capture context`、`Error processing payment` |
| 应答键 | `isv_tokenCaptureContextSignature` |

实现：`Payments/CybersourcePayment`，接进 `StoreFlow.GetPaymentTokenAsync`；端点由调用方给。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: createMyPayment closed')
