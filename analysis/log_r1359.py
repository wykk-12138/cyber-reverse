"""R1359 record: four more operations, one family, origin from the caller."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1359 轮：B 块四份一次落地 —— **它们的处理器只写 `application/json` 与信封键，主机在更上层**

- **探四个操作名**：`getCustomerInformation` 的处理器 `sub_140E5B940` 只有
  `application/json` / `getCustomerInformation` / `operationName` / `query`；
  隔几百字节的 `updateMyPaymentWithActions`(`sub_140E5B570`) 也一样，**与 `getCart` 的状态机同块**。
  **主机在更上层** —— 与 R1345 的 `api/graphql` 族同形，所以答案也一样：**origin 由调用方给，没有就拒绝**。
- **四份文档与声明集（按实测，不按猜测）**：
  ```
  getCustomerInformation   197 字符   无变量
  getPaymentdMethods      3067 字符   无变量（保留镜像自己的错拼 "Paymentd"）
  item                      67 字符   无变量
  getCart                 3234 字符   $key / $locale
  ```
- **落码**：`Flows/StoreSessionQueries.cs`（四份文档 + `Declared` 表 + `DocumentFor` + `Envelope` + `SendAsync`，
  未声明变量在发送前挡掉）；接进 `StoreFlow.VerifySessionAsync`（`storeSession.origin` 触发，无则 `Ok()`）。
- **产物**：`query getCustomerInformation`、`query getPaymentdMethods`、`query getCart` **UTF-16 各命中 1**；
  尺寸 61,925,888 → **61,955,584**。

### 五要素

- **改了什么**：新增 `Flows/StoreSessionQueries.cs`、`tests/StoreSessionQueriesTests.cs`（6 条）；
  `StoreFlow.VerifySessionAsync` 加分支；新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StoreSessionQueriesTests` → **6/6**；`StoreFlow|Shortage` → **25/25**；
  `operation_gap.py` → 覆盖 **48/65**（缺 17）；`orphan_documents.py` → 0；产物三串各命中 1；尺寸见上。
- **数字变化**：覆盖 44 → **48**；缺 21 → **17**；套件 +6；产物 +29,696 字节。
- **证据等级**：Observation —— 两个处理器的字面量只有信封键、四份文档的长度与声明集、产物三串命中。
- **还剩什么**：17 个 —— `CreditCard`(2867)/`getShippingMethods`(531)（无操作名串）；
  `SignInAsGuest`(453)/`TokenizeCreditCard`(505)/`UpdateContactDetails`(244)/`UpdateCustomerForCart`(382)/
  `UpdateShippingAddress`(2386)；`addToCartByChannel`(2271)；`updateShipAddress`(140)/
  `updateMyPaymentWithActions`(401)；`cartCreate` 已做、`createCartByStore`(421)/`createMyPayment`(493)/
  `initiateCheckout`(251)/`maintainShippingGroups`(223)/`saveAddress`(296)（六份无主机）；
  两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；AO 三个体；Saucony 六步。
"""

POINTER = """
---

## 第 1359 轮

- B 块四份（`getCustomerInformation` 197 / `getPaymentdMethods` 3067 / `item` 67 / `getCart` 3234）一次落地：
  处理器**只有信封键没有主机** → `StoreSessionQueries`，**origin 由调用方给**，接进 `VerifySessionAsync`。
- **声明集按实测**：前三份**无变量**，`getCart` 是 `$key`/`$locale`；`getPaymentdMethods` 保留镜像的错拼。
- 覆盖 44 → **48/65**，缺 21 → **17**；产物三串各 UTF-16 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1359 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1359 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'StoreSessionQueries' not in text:
    text += """
## 无主机的会话族（R1359）

处理器 `sub_140E5B940` / `sub_140E5B570` 只有 `application/json` 与信封键，与 `getCart` 状态机同块，**主机在上层**。

| 操作 | 长度 | 声明集 |
|---|---|---|
| `getCustomerInformation` | 197 | 无 |
| `getPaymentdMethods` | 3067 | 无（保留镜像错拼） |
| `item` | 67 | 无 |
| `getCart` | 3234 | `$key`、`$locale` |

实现在 `Flows/StoreSessionQueries.cs`；origin 由调用方给。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
